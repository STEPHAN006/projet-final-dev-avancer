"""FastAPI Study Hub Endpoints."""

from fastapi import APIRouter, HTTPException
from lifeos.services.data_service import ds
from lifeos.backend.schemas import CourseCreate, ExamCreate, StudySessionCreate

router = APIRouter(prefix="/study", tags=["Study Hub"])

@router.get("/courses")
def get_courses():
    return ds.study.list_courses()

@router.post("/courses", status_code=201)
def create_course(course: CourseCreate):
    return ds.study.create_course(
        code=course.code,
        name=course.name,
        professor=course.professor,
        semester=course.semester,
        color=course.color,
        target_grade=course.target_grade,
        current_grade=course.current_grade
    )

@router.get("/exams")
def get_upcoming_exams():
    return ds.study.list_upcoming_exams()

@router.post("/exams", status_code=201)
def create_exam(exam: ExamCreate):
    return ds.study.create_exam(
        course_id=exam.course_id,
        title=exam.title,
        date_str=exam.date,
        weight=exam.weight,
        room=exam.room
    )

@router.post("/sessions", status_code=201)
def log_session(session: StudySessionCreate):
    return ds.study.log_study_session(
        course_id=session.course_id,
        title=session.title,
        duration_minutes=session.duration_minutes,
        notes=session.notes
    )
