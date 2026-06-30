"""Session routes: CSV upload + processing, history listing, single-session fetch."""
from fastapi import APIRouter

router = APIRouter()

# TODO: POST /upload      -> accept CSV, run ML pipeline, persist + return results
# TODO: GET  /            -> list current user's sessions (paginated, by date)
# TODO: GET  /{session_id} -> fetch one session with analytics + exercise logs
