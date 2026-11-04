"""FastAPI Analytics Endpoints."""

from fastapi import APIRouter
from lifeos.services.data_service import ds

router = APIRouter(prefix="/stats", tags=["Analytics & Stats"])

@router.get("/dashboard")
def get_dashboard_summary():
    return ds.stats.get_dashboard_summary()

@router.get("/report")
def get_report(days: int = 7):
    return ds.stats.get_analytics_report(days=days)
