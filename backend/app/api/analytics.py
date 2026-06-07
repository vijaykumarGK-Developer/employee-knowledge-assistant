from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.services.analytics_service import (
    get_overview_stats,
    get_popular_questions,
    get_unanswered_questions,
    get_user_activity,
)
from app.schemas.analytics import (
    OverviewStats,
    PopularQuestion,
    UnansweredQuestion,
    UserActivity,
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview", response_model=OverviewStats)
def overview(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> OverviewStats:
    return OverviewStats(**get_overview_stats(db))


@router.get("/popular-questions", response_model=list[PopularQuestion])
def popular_questions(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[PopularQuestion]:
    return [PopularQuestion(**q) for q in get_popular_questions(db, limit)]


@router.get("/unanswered", response_model=list[UnansweredQuestion])
def unanswered(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[UnansweredQuestion]:
    return [UnansweredQuestion(**q) for q in get_unanswered_questions(db)]


@router.get("/user-activity", response_model=list[UserActivity])
def user_activity(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[UserActivity]:
    return [UserActivity(**a) for a in get_user_activity(db, days)]
