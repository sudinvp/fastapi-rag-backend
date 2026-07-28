from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, get_db
from app.dependencies import get_current_user
from app.models import Chunk, Document, User
from app.schemas import DocumentIngestRequest, DocumentResponse
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts

router = APIRouter(prefix="/documents", tags=["documents"])


async def _process_ingestion(document_id: str, content: str):
    """
    Runs as a background task: chunk the text, embed each chunk, persist.
    Kept out of the request/response cycle so large documents don't block
    the client past the initial 202-style response.
    """
    pieces = chunk_text(content)
    if not pieces:
        return
    vectors = embed_texts(pieces)

    async with AsyncSessionLocal() as session:
        for idx, (piece, vector) in enumerate(zip(pieces, vectors)):
            session.add(Chunk(document_id=document_id, chunk_index=idx, text=piece, embedding=vector))
        await session.commit()


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(
    payload: DocumentIngestRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = Document(owner_id=current_user.id, title=payload.title, content=payload.content)
    db.add(document)
    await db.commit()
    await db.refresh(document)

    # Ingestion (chunk + embed) happens asynchronously in the background so
    # the endpoint returns immediately even for large documents.
    background_tasks.add_task(_process_ingestion, document.id, payload.content)

    expected_chunk_count = len(chunk_text(payload.content))
    return DocumentResponse(
        id=document.id,
        title=document.title,
        chunk_count=expected_chunk_count,
        created_at=document.created_at,
    )


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Document).where(Document.owner_id == current_user.id))
    documents = result.scalars().all()

    responses = []
    for doc in documents:
        count_result = await db.execute(select(Chunk).where(Chunk.document_id == doc.id))
        chunk_count = len(count_result.scalars().all())
        responses.append(
            DocumentResponse(id=doc.id, title=doc.title, chunk_count=chunk_count, created_at=doc.created_at)
        )
    return responses


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.owner_id == current_user.id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    await db.delete(document)
    await db.commit()
