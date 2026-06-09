import re

from app.services.embeddings import generate_embeddings
from app.services.vector_store import search_similar
from app.services.llm_service import generate_answer

OFF_TOPIC_KEYWORDS = [
    "weather", "sports", "movie", "recipe", "cook", "joke", "jokes", "funny",
    "game", "play", "music", "song", "celebrity", "news today", "politics",
    "stock market", "crypto", "bitcoin", "horoscope", "astrology",
]

DEPT_KEYWORDS = {
    "hr": ["hr", "human resource", "leave", "hiring", "probation", "benefit", "salary", "payroll"],
    "engineering": ["engineering", "engineer", "developer", "tech", "code", "deploy", "api", "backend", "frontend"],
    "finance": ["finance", "financial", "expense", "budget", "reimbursement", "vendor", "travel", "invoice"],
}


def _is_off_topic(question: str) -> bool:
    q = question.lower().strip()
    if any(re.search(rf"\b{kw}\b", q) for kw in OFF_TOPIC_KEYWORDS):
        return True
    return False


def _detect_department(question: str) -> str | None:
    q = question.lower()
    for dept, keywords in DEPT_KEYWORDS.items():
        if any(kw in q for kw in keywords):
            return dept
    return None


def answer_question(
    question: str,
    department: str | None = None,
    chat_history: list[dict] | None = None,
) -> dict:
    if not question.strip():
        return {"answer": "Please ask a valid question."}

    if _is_off_topic(question):
        return {"answer": "I'm here to help with company-related questions. Could you please ask about our policies, documents, or processes?"}

    dept_filter = _detect_department(question) or department

    question_embeddings = generate_embeddings([question])
    query_embedding = question_embeddings[0]

    results = search_similar(query_embedding, department_filter=dept_filter, top_k=3)

    if not results:
        return {"answer": "I couldn't find any relevant information in the company documents to answer your question."}

    best = results[0]
    if best.get("score", 0) > 1.5:
        return {"answer": "I couldn't find any relevant information in the company documents to answer your question."}

    answer = generate_answer(question, results)

    return {"answer": answer}
