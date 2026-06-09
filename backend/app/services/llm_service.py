def generate_answer(question: str, context_chunks: list[dict]) -> str:
    if not context_chunks:
        return "I couldn't find any relevant information to answer your question."

    grouped: dict[str, list[str]] = {}
    for c in context_chunks:
        title = c.get("doc_title", "Document")
        if title not in grouped:
            grouped[title] = []
        grouped[title].append(c["text"])

    parts: list[str] = []
    for title, texts in grouped.items():
        seen = set()
        unique = []
        for t in texts:
            t_clean = t.strip()
            if t_clean and t_clean not in seen:
                seen.add(t_clean)
                unique.append(t_clean)
        if unique:
            content = "\n".join(f"  - {u}" for u in unique[:3])
            parts.append(f"From {title}:\n{content}")

    answer = "\n\n".join(parts) if parts else "No relevant information found."
    return answer
