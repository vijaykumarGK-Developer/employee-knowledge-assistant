from pathlib import Path

from app.services.extractors.pdf_extractor import extract_pdf
from app.services.extractors.docx_extractor import extract_docx
from app.services.extractors.txt_extractor import extract_txt
from app.services.extractors.csv_extractor import extract_csv


def extract_text(file_path: str, file_type: str | None = None) -> list[tuple[int, str]]:
    path = Path(file_path)
    ext = file_type or path.suffix.lstrip(".").lower()
    extractors = {
        "pdf": extract_pdf,
        "docx": extract_docx,
        "txt": extract_txt,
        "csv": extract_csv,
    }
    extractor = extractors.get(ext)
    if not extractor:
        raise ValueError(f"Unsupported file type: {ext}")
    return extractor(file_path)
