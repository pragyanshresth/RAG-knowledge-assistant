from backend.services.chunking import chunk_text


def test_overlap_and_size():
    text = " ".join(f"w{i}" for i in range(500))
    chunks = chunk_text(text, 200, 40)
    assert len(chunks) > 1 and all(len(c) <= 200 for c in chunks)
    assert chunks[0].split()[-1] in chunks[1].split()  # tail of chunk 0 repeats in chunk 1


def test_empty():
    assert chunk_text("   ") == []
