"""FastAPI Settings & Backup Endpoints."""

from fastapi import APIRouter
from lifeos.services.data_service import ds
from lifeos.backend.schemas import SettingUpdate

router = APIRouter(prefix="/settings", tags=["Settings & Backup"])

@router.get("/")
def get_settings():
    return ds.settings.get_all_settings()

@router.post("/")
def update_setting(payload: SettingUpdate):
    ds.settings.set_setting(payload.key, payload.value)
    return {"key": payload.key, "value": payload.value}

@router.get("/export")
def export_backup():
    return ds.settings.export_full_backup()

@router.post("/reset")
def reset_to_seed():
    ds.settings.reset_to_seed()
    return {"success": True, "message": "Database reset to clean seeds"}
