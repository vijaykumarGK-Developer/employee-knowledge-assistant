import pandas as pd


def extract_csv(file_path: str) -> list[tuple[int, str]]:
    df = pd.read_csv(file_path)
    lines = []
    for _, row in df.iterrows():
        line = " | ".join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
        if line:
            lines.append(line)
    full_text = "\n".join(lines)
    return [(1, full_text)] if full_text else []
