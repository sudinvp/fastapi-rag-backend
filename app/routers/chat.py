from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Chunk, Document, User
from app.schemas import ChatRequest, ChatResponse, RetrievedChunk
from app.services.embeddings import cosine_similarity, embed_query
from app.services.llm import generate_answer, stream_answer

router = APIRouter(prefix="/chat", tags=["chat"])


async def _retrieve_relevant_chunks(
    db: AsyncSession, current_user: User, query: str, document_id: str | None
) -> list[tuple[Chunk, float]]:
    stmt = select(Chunk).join(Document).where(Document.owner_id == current_user.id)
    if document_id:
        stmt = stmt.where(Chunk.document_id == document_id)

    result = await db.execute(stmt)
    all_chunks = result.scalars().all()
    if not all_chunks:
        return []

    query_vector = embed_query(query)
    scored = [(chunk, cosine_similarity(query_vector, chunk.embedding)) for chunk in all_chunks]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[: settings.top_k_results]


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    top_chunks = await _retrieve_relevant_chunks(db, current_user, payload.query, payload.document_id)
    context_texts = [chunk.text for chunk, _ in top_chunks]

    answer = await generate_answer(payload.query, context_texts)

    sources = [
        RetrievedChunk(document_id=chunk.document_id, chunk_index=chunk.chunk_index, text=chunk.text, score=score)
        for chunk, score in top_chunks
    ]
    return ChatResponse(answer=answer, sources=sources)


@router.post("/stream")
async def chat_stream(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Streams the LLM's answer token-by-token as plain text chunks."""
    top_chunks = await _retrieve_relevant_chunks(db, current_user, payload.query, payload.document_id)
    context_texts = [chunk.text for chunk, _ in top_chunks]

    return StreamingResponse(stream_answer(payload.query, context_texts), media_type="text/plain")
