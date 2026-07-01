"""Analytics routes: aggregate stats across a user's session history."""
from fastapi import APIRouter, Depends

from app.analytics import service as analytics_service
from app.analytics.schemas import UserAnalyticsSummary
from app.dependencies import get_current_user
from app.users.schemas import UserPublic

router = APIRouter()


@router.get("/summary", response_model=UserAnalyticsSummary)
async def summary(
    current_user: UserPublic = Depends(get_current_user),
) -> UserAnalyticsSummary:
    return await analytics_service.build_user_summary(current_user.id)
