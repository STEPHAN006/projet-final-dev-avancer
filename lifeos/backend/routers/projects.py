"""FastAPI Projects Endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from lifeos.services.data_service import ds
from lifeos.backend.schemas import ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/")
def get_projects(status: Optional[str] = None, q: Optional[str] = None):
    return ds.projects.list_projects(status=status, search_query=q)

@router.get("/{project_id}")
def get_project(project_id: int):
    p = ds.projects.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p

@router.get("/{project_id}/tasks")
def get_project_tasks(project_id: int):
    return ds.tasks.list_tasks(project_id=project_id)

@router.post("/", status_code=201)
def create_project(project: ProjectCreate):
    return ds.projects.create_project(
        title=project.title,
        description=project.description,
        category=project.category,
        color=project.color,
        deadline=project.deadline
    )

@router.patch("/{project_id}")
def update_project(project_id: int, updates: ProjectUpdate):
    p = ds.projects.update_project(project_id, **updates.model_dump(exclude_unset=True))
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p

@router.delete("/{project_id}")
def delete_project(project_id: int):
    ok = ds.projects.delete_project(project_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True}
