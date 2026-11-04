"""FastAPI Task Endpoints."""

from typing import Optional, List
from fastapi import APIRouter, HTTPException
from lifeos.services.data_service import ds
from lifeos.backend.schemas import TaskCreate, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/")
def get_tasks(
    status: Optional[str] = None, # all, today, urgent, completed, pending
    project_id: Optional[int] = None,
    q: Optional[str] = None
):
    return ds.tasks.list_tasks(filter_status=status, project_id=project_id, search_query=q)

@router.get("/{task_id}")
def get_task(task_id: int):
    t = ds.tasks.get_task(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t

@router.post("/", status_code=201)
def create_task(task: TaskCreate):
    return ds.tasks.create_task(
        title=task.title,
        description=task.description,
        project_id=task.project_id,
        priority=task.priority,
        due_date=task.due_date,
        estimated_minutes=task.estimated_minutes,
        tags=task.tags,
        subtasks=[s.model_dump() for s in task.subtasks]
    )

@router.post("/{task_id}/toggle")
def toggle_task(task_id: int):
    t = ds.tasks.toggle_task(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t

@router.patch("/{task_id}")
def update_task(task_id: int, updates: TaskUpdate):
    data = updates.model_dump(exclude_unset=True)
    if "subtasks" in data and data["subtasks"] is not None:
        data["subtasks"] = [s if isinstance(s, dict) else s.model_dump() for s in data["subtasks"]]
    t = ds.tasks.update_task(task_id, **data)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t

@router.delete("/{task_id}")
def delete_task(task_id: int):
    ok = ds.tasks.delete_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}
