"""Settings, backup and export service."""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from lifeos.core.database import get_connection, init_db
from lifeos.core.events import bus

class SettingsService:
    def get_all_settings(self) -> Dict[str, str]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT key, value FROM settings")
        rows = cur.fetchall()
        conn.close()
        return {r["key"]: r["value"] for r in rows}

    def get_setting(self, key: str, default: str = "") -> str:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cur.fetchone()
        conn.close()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()
        bus.emit("settings_updated", key=key, value=value)

    def export_full_backup(self) -> Dict[str, Any]:
        """Export all user data as a clean portable JSON structure."""
        conn = get_connection()
        cur = conn.cursor()
        backup = {
            "version": "1.0.0",
            "exported_at": datetime.now().isoformat(),
            "tables": {}
        }
        for table in [
            "settings", "projects", "tasks", "calendar_events",
            "study_courses", "study_exams", "study_sessions",
            "habits", "habit_logs", "streaks", "goals", "focus_sessions"
        ]:
            cur.execute(f"SELECT * FROM {table}")
            backup["tables"][table] = [dict(r) for r in cur.fetchall()]
        conn.close()
        return backup

    def reset_to_seed(self):
        """Reset the database to clean fresh seed data."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS tasks;")
        cur.execute("DROP TABLE IF EXISTS projects;")
        cur.execute("DROP TABLE IF EXISTS calendar_events;")
        cur.execute("DROP TABLE IF EXISTS study_exams;")
        cur.execute("DROP TABLE IF EXISTS study_sessions;")
        cur.execute("DROP TABLE IF EXISTS study_courses;")
        cur.execute("DROP TABLE IF EXISTS habit_logs;")
        cur.execute("DROP TABLE IF EXISTS habits;")
        cur.execute("DROP TABLE IF EXISTS streaks;")
        cur.execute("DROP TABLE IF EXISTS goals;")
        cur.execute("DROP TABLE IF EXISTS focus_sessions;")
        cur.execute("DROP TABLE IF EXISTS settings;")
        conn.commit()
        conn.close()
        init_db()
        bus.emit("tasks_updated")
        bus.emit("projects_updated")
        bus.emit("habits_updated")
        bus.emit("streaks_updated")
        bus.emit("goals_updated")
        bus.emit("stats_updated")
        bus.emit("settings_updated")
