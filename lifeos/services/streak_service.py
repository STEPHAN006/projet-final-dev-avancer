"""Streaks and Daily Checklist Protocol service."""

from datetime import datetime, date
from typing import Dict, List, Any
from lifeos.core.database import get_connection
from lifeos.core.events import bus
from lifeos.services.habit_service import HabitService

class StreakService:
    def __init__(self):
        self.habit_service = HabitService()

    def get_streaks_overview(self) -> Dict[str, Any]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM streaks ORDER BY current_streak DESC")
        streaks = [dict(r) for r in cur.fetchall()]
        conn.close()

        habits = self.habit_service.list_habits_with_logs()
        total_habits = len(habits)
        done_today = sum(1 for h in habits if h.get("today_done"))

        completion_pct = int((done_today / total_habits * 100)) if total_habits > 0 else 0

        # Calculate highest streak
        max_streak = max([s["current_streak"] for s in streaks] + [h["streak_current"] for h in habits] + [0])

        return {
            "streaks": streaks,
            "daily_habits": habits,
            "total_today": total_habits,
            "completed_today": done_today,
            "completion_pct": completion_pct,
            "main_streak_days": max_streak
        }

    def toggle_daily_item(self, habit_id: int) -> bool:
        return self.habit_service.toggle_habit_for_date(habit_id)
