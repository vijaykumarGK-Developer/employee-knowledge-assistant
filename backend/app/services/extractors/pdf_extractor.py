import fitz


def extract_pdf(file_path: str) -> list[tuple[int, str]]:
    pages: list[tuple[int, str]] = []
    with fitz.open(file_path) as doc:
        for page_num in range(len(doc)):
            text = doc[page_num].get_text()
            if text.strip():
                pages.append((page_num + 1, text.strip()))
    return pages
