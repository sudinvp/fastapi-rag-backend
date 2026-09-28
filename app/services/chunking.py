from app.config import settings


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    """
    Splits text into overlapping word-based chunks.

    Word-based (not char-based) chunking keeps chunks semantically coherent
    and roughly token-proportional, which matters for embedding quality.
    Overlap preserves context across chunk boundaries so an answer that spans
    two chunks isn't lost at the split point.
    """
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap  # step forward, keeping `overlap` words of context only

    return chunks
