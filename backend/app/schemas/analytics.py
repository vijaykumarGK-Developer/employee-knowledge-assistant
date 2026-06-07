from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_users: int
    total_documents: int
    questions_today: int
    unanswered_count: int
    unanswered_percentage: float


class PopularQuestion(BaseModel):
    question: str
    count: int


class UnansweredQuestion(BaseModel):
    content: str
    created_at: str


class UserActivity(BaseModel):
    date: str
    active_users: int
