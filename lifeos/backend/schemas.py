"""Pydantic schemas for the FastAPI backend."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Tasks ---
class TaskSubtask(BaseModel):
    text: str
    done: bool = False

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = ""
    project_id: Optional[int] = None
    priority: str = "MEDIUM"
    due_date: Optional[str] = None
    estimated_minutes: int = 30
    tags: List[str] = []
    subtasks: List[TaskSubtask] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    estimated_minutes: Optional[int] = None
    actual_minutes: Optional[int] = None
    is_completed: Optional[int] = None
    tags: Optional[List[str]] = None
    subtasks: Optional[List[TaskSubtask]] = None

# --- Projects ---
class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = ""
    category: str = "Dev"
    color: str = "#C6A76B"
    deadline: Optional[str] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    progress: Optional[int] = None
    status: Optional[str] = None
    deadline: Optional[str] = None

# --- Calendar ---
class EventCreate(BaseModel):
    title: str = Field(..., min_length=1)
    date: str
    start_time: str
    end_time: str
    description: str = ""
    event_type: str = "task"
    location: str = ""
    color: str = "#C6A76B"
    is_all_day: bool = False

# --- Study ---
class CourseCreate(BaseModel):
    code: str
    name: str
    professor: str = ""
    semester: str = "S1"
    color: str = "#DFBA7B"
    target_grade: float = 16.0
    current_grade: float = 14.0

class ExamCreate(BaseModel):
    course_id: int
    title: str
    date: str
    weight: float = 1.0
    room: str = ""

class StudySessionCreate(BaseModel):
    course_id: int
    title: str
    duration_minutes: int = 45
    notes: str = ""

# --- Habits & Streaks ---
class HabitCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    frequency: str = "daily"
    target_per_week: int = 7
    color: str = "#C6A76B"
    icon: str = "star"

class HabitToggle(BaseModel):
    date: Optional[str] = None

# --- Goals ---
class Milestone(BaseModel):
    text: str
    done: bool = False

class GoalCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = ""
    category: str = "Dev"
    target_date: Optional[str] = None
    milestones: List[Milestone] = []

# --- Focus ---
class FocusSessionCreate(BaseModel):
    title: str = "Session Focus"
    duration_minutes: int = 25
    mode: str = "pomodoro"
    task_id: Optional[int] = None
    course_id: Optional[int] = None

# --- Settings ---
class SettingUpdate(BaseModel):
    key: str
    value: str
