"""FastAPI Streaks & Checklist Endpoints."""

from fastapi import APIRouter
from lifeos.services.data_service import ds

router = APIRouter(prefix="/streaks", tags=["Streaks & Checklist"])

@router.get("/")
def get_streaks():
    return ds.streaks.get_streaks_overview()

@router.post("/{habit_id}/check")
def check_item(habit_id: int):
    done = ds.streaks.toggle_daily_item(habit_id)
    return {"habit_id": habit_id, "done": done}
