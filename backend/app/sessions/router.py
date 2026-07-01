"""Session routes: CSV upload + processing, history listing, single-session fetch."""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from app.dependencies import get_current_user
from app.ml.preprocessing import CSVValidationError
from app.sessions import service as sessions_service
from app.sessions.schemas import SessionResult, SessionSummary
from app.users.schemas import UserPublic

router = APIRouter()


@router.post("/upload", response_model=SessionResult, status_code=status.HTTP_201_CREATED)
async def upload_session(
    file: UploadFile = File(...),
    current_user: UserPublic = Depends(get_current_user),
) -> SessionResult:
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Only .csv files are accepted"
        )
    raw = await file.read()

    # ML inference is CPU-bound — run it off the event loop.
    try:
        analytics = await run_in_threadpool(
            sessions_service.analyze_csv, raw, current_user.weight_kg
        )
    except CSVValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return await sessions_service.save_session(current_user, file.filename, analytics)


@router.get("", response_model=list[SessionSummary])
async def list_sessions(
    current_user: UserPublic = Depends(get_current_user),
) -> list[SessionSummary]:
    return await sessions_service.list_sessions(current_user.id)


@router.get("/{session_id}", response_model=SessionResult)
async def get_session(
    session_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> SessionResult:
    session = await sessions_service.get_session(current_user.id, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session
