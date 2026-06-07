from pathlib import Path


def extract_txt(file_path: str) -> list[tuple[int, str]]:
    text = Path(file_path).read_text(encoding="utf-8", errors="replace").strip()
    return [(1, text)] if text else []
