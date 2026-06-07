from langchain_text_splitters import RecursiveCharacterTextSplitter


CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function=len,
)


def chunk_document(
    pages: list[tuple[int, str]], doc_id: str
) -> list[dict]:
    chunks: list[dict] = []
    chunk_index = 0
    for page_num, text in pages:
        if not text.strip():
            continue
        texts = splitter.split_text(text)
        for t in texts:
            chunks.append({
                "text": t,
                "page_num": page_num,
                "doc_id": doc_id,
                "chunk_index": chunk_index,
            })
            chunk_index += 1
    return chunks
