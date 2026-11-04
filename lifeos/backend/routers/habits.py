"""FastAPI Habits Endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from lifeos.services.data_service import ds
from lifeos.backend.schemas import HabitCreate, HabitToggle

router = APIRouter(prefix="/habits", tags=["Habits"])

@router.get("/")
def get_habits():
    return ds.habits.list_habits_with_logs()

@router.post("/", status_code=201)
def create_habit(habit: HabitCreate):
    return ds.habits.create_habit(
        name=habit.name,
        description=habit.description,
        frequency=habit.frequency,
        target_per_week=habit.target_per_week,
        color=habit.color,
        icon=habit.icon
    )

@router.post("/{habit_id}/toggle")
def toggle_habit(habit_id: int, body: Optional[HabitToggle] = None):
    d = body.date if body else None
    done = ds.habits.toggle_habit_for_date(habit_id, target_date=d)
    return {"habit_id": habit_id, "done": done}

@router.delete("/{habit_id}")
def delete_habit(habit_id: int):
    ok = ds.habits.delete_habit(habit_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"success": True}
