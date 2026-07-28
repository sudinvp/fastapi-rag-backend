from app.services.chunking import chunk_text


def test_chunk_text_empty_string_returns_empty_list():
    assert chunk_text("") == []


def test_chunk_text_short_text_returns_single_chunk():
    text = "hello world this is short"
    chunks = chunk_text(text, chunk_size=10, overlap=2)
    assert chunks == [text]


def test_chunk_text_respects_chunk_size_and_overlap():
    words = [f"word{i}" for i in range(25)]
    text = " ".join(words)

    chunks = chunk_text(text, chunk_size=10, overlap=3)

    # Every chunk should have at most `chunk_size` words
    for chunk in chunks:
        assert len(chunk.split()) <= 10

    # Consecutive chunks should overlap by the configured amount
    first_words = chunks[0].split()
    second_words = chunks[1].split()
    overlap_words = first_words[-3:]
    assert second_words[:3] == overlap_words


def test_chunk_text_covers_all_words():
    words = [f"w{i}" for i in range(37)]
    text = " ".join(words)
    chunks = chunk_text(text, chunk_size=10, overlap=2)

    reconstructed = set()
    for chunk in chunks:
        reconstructed.update(chunk.split())

    assert reconstructed == set(words)
