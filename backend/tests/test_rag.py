from unittest.mock import patch, MagicMock

from app.services.extractors import extract_text
from app.services.chunker import chunk_document


def test_txt_extraction(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("Hello world. This is a test document. " * 20)
    pages = extract_text(str(f), "txt")
    assert len(pages) == 1
    assert len(pages[0][1]) > 0
    assert pages[0][0] == 1


def test_chunking():
    pages = [(1, "This is a sample document with enough text to create multiple chunks. " * 30)]
    chunks = chunk_document(pages, "doc-1")
    assert len(chunks) > 1
    assert chunks[0]["doc_id"] == "doc-1"
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["page_num"] == 1
    assert len(chunks[0]["text"]) > 0


def test_chunk_metadata():
    pages = [(1, "Page one text. " * 10), (2, "Page two text. " * 10)]
    chunks = chunk_document(pages, "doc-2")
    page_nums = {c["page_num"] for c in chunks}
    assert 1 in page_nums
    assert 2 in page_nums


@patch("app.services.embeddings.SentenceTransformer")
def test_embeddings_service(mock_model):
    mock_instance = MagicMock()
    mock_instance.encode.return_value = [[0.1] * 384]
    mock_model.return_value = mock_instance

    from app.services.embeddings import generate_embeddings
    result = generate_embeddings(["test text"])
    assert len(result) == 1
    assert len(result[0]) == 384


def test_rag_pipeline():
    from app.services.rag_pipeline import answer_question
    result = answer_question("What is the policy?", department="hr")
    assert "answer" in result
