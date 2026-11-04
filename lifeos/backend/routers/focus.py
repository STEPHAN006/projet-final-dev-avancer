"""FastAPI Focus & Pomodoro Endpoints."""

from fastapi import APIRouter
from lifeos.services.data_service import ds
from lifeos.backend.schemas import FocusSessionCreate

router = APIRouter(prefix="/focus", tags=["Focus & Pomodoro"])

@router.get("/today")
def get_today_focus():
    return ds.focus.get_today_focus_stats()

@router.post("/sessions", status_code=201)
def log_session(session: FocusSessionCreate):
    return ds.focus.log_session(
        title=session.title,
        duration_minutes=session.duration_minutes,
        mode=session.mode,
        task_id=session.task_id,
        course_id=session.course_id
    )
