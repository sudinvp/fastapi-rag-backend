from google import genai
from google.genai import types
from tenacity import retry, retry_if_not_exception_type, stop_after_attempt, wait_exponential

from app.config import settings

_client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

RAG_SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using ONLY the provided "
    "context. If the context doesn't contain the answer, say you don't know "
    "instead of guessing. Keep answers concise and cite which part of the "
    "context you used when relevant."
)


def _build_prompt(query: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(no relevant context found)"
    return f"Context:\n{context}\n\nQuestion: {query}"


class LLMConfigError(RuntimeError):
    """Raised when no LLM provider is configured (e.g. missing API key)."""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_not_exception_type(genai.errors.ClientError),
)
async def generate_answer(query: str, context_chunks: list[str]) -> str:
    if _client is None:
        preview = context_chunks[0][:300] if context_chunks else "No relevant context was found."
        return (
            "[GEMINI_API_KEY not set - returning retrieved context instead of an "
            f"LLM-generated answer]\n\n{preview}"
        )

    response = await _client.aio.models.generate_content(
        model="gemini-flash-latest",  # <-- Changed from settings.llm_model
        contents=_build_prompt(query, context_chunks),
        config=types.GenerateContentConfig(system_instruction=RAG_SYSTEM_PROMPT, max_output_tokens=1024),
    )
    return response.text or ""


async def stream_answer(query: str, context_chunks: list[str]):
    """Async generator yielding response text tokens as they arrive."""
    if _client is None:
        yield "[GEMINI_API_KEY not set] " + (context_chunks[0][:300] if context_chunks else "No context found.")
        return

    stream = await _client.aio.models.generate_content_stream(
        model="gemini-flash-latest",  # <-- Changed from settings.llm_model
        contents=_build_prompt(query, context_chunks),
        config=types.GenerateContentConfig(system_instruction=RAG_SYSTEM_PROMPT, max_output_tokens=1024),
    )
    async for chunk in stream:
        if chunk.text:
            yield chunk.text