"""FastAPI Goals Endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from lifeos.services.data_service import ds
from lifeos.backend.schemas import GoalCreate

router = APIRouter(prefix="/goals", tags=["Goals"])

@router.get("/")
def get_goals(category: Optional[str] = None, status: Optional[str] = None):
    return ds.goals.list_goals(category=category, status=status)

@router.get("/{goal_id}")
def get_goal(goal_id: int):
    g = ds.goals.get_goal(goal_id)
    if not g:
        raise HTTPException(status_code=404, detail="Goal not found")
    return g

@router.post("/", status_code=201)
def create_goal(goal: GoalCreate):
    return ds.goals.create_goal(
        title=goal.title,
        description=goal.description,
        category=goal.category,
        target_date=goal.target_date,
        milestones=[m.model_dump() for m in goal.milestones]
    )

@router.post("/{goal_id}/milestone/{index}/toggle")
def toggle_milestone(goal_id: int, index: int):
    g = ds.goals.toggle_milestone(goal_id, index)
    if not g:
        raise HTTPException(status_code=404, detail="Goal or milestone not found")
    return g

@router.delete("/{goal_id}")
def delete_goal(goal_id: int):
    ok = ds.goals.delete_goal(goal_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"success": True}
