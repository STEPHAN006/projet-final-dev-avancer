"""FastAPI Calendar Endpoints."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from lifeos.services.data_service import ds
from lifeos.backend.schemas import EventCreate

router = APIRouter(prefix="/calendar", tags=["Calendar"])

@router.get("/events")
def get_events(start_date: Optional[str] = None, end_date: Optional[str] = None):
    return ds.calendar.list_events(start_date=start_date, end_date=end_date)

@router.get("/day/{target_date}")
def get_events_for_day(target_date: str):
    return ds.calendar.get_events_for_date(target_date)

@router.post("/events", status_code=201)
def create_event(event: EventCreate):
    return ds.calendar.create_event(
        title=event.title,
        date_str=event.date,
        start_time=event.start_time,
        end_time=event.end_time,
        description=event.description,
        event_type=event.event_type,
        location=event.location,
        color=event.color,
        is_all_day=event.is_all_day
    )

@router.delete("/events/{event_id}")
def delete_event(event_id: int):
    ok = ds.calendar.delete_event(event_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"success": True}
