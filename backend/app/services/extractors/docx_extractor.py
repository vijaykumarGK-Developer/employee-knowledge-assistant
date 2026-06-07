from docx import Document


def extract_docx(file_path: str) -> list[tuple[int, str]]:
    doc = Document(file_path)
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [(1, full_text)] if full_text.strip() else []
