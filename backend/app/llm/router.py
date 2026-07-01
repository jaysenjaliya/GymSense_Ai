"""LLM routes: "Analyze My Workout" — AI recommendations from session + history."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.analytics import service as analytics_service
from app.dependencies import get_current_user
from app.llm import service as llm_service
from app.llm.schemas import AnalyzeRequest, WorkoutAnalysisResponse
from app.sessions import service as sessions_service
from app.users.schemas import UserPublic

router = APIRouter()


@router.post("/analyze", response_model=WorkoutAnalysisResponse)
async def analyze(
    payload: AnalyzeRequest,
    current_user: UserPublic = Depends(get_current_user),
) -> WorkoutAnalysisResponse:
    session = await sessions_service.get_session(current_user.id, payload.session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    history = await analytics_service.build_user_summary(current_user.id)
    profile = current_user.model_dump(mode="json", include={
        "name", "age", "gender", "height_cm", "weight_kg", "fitness_goal",
    })

    try:
        return await llm_service.analyze_workout(
            profile=profile,
            current_session=session.model_dump(mode="json"),
            history=history.model_dump(mode="json"),
        )
    except llm_service.LLMError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI analysis failed: {exc}",
        )
