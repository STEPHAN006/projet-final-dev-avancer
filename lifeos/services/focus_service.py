"""Focus and Pomodoro service."""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
from lifeos.core.database import get_connection
from lifeos.core.events import bus

class FocusService:
    def log_session(
        self,
        title: str,
        duration_minutes: int,
        mode: str = "pomodoro",
        task_id: Optional[int] = None,
        course_id: Optional[int] = None
    ) -> Dict[str, Any]:
        conn = get_connection()
        cur = conn.cursor()
        now_str = datetime.now().isoformat()

        cur.execute("""
            INSERT INTO focus_sessions (title, task_id, course_id, duration_minutes, mode, completed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, task_id, course_id, duration_minutes, mode, now_str))
        sid = cur.lastrowid

        # If linked to a task, increment the task actual_minutes
        if task_id:
            cur.execute("""
                UPDATE tasks
                SET actual_minutes = actual_minutes + ?
                WHERE id = ?
            """, (duration_minutes, task_id))

        conn.commit()
        conn.close()

        bus.emit("focus_updated")
        bus.emit("stats_updated")
        bus.emit("tasks_updated")
        return {"id": sid, "title": title, "duration": duration_minutes}

    def get_today_focus_stats(self) -> Dict[str, Any]:
        conn = get_connection()
        cur = conn.cursor()
        today_str = date.today().isoformat()

        cur.execute("""
            SELECT COUNT(*) as session_count, COALESCE(SUM(duration_minutes), 0) as total_minutes
            FROM focus_sessions
            WHERE completed_at LIKE ?
        """, (f"{today_str}%",))
        row = cur.fetchone()

        cur.execute("""
            SELECT * FROM focus_sessions
            ORDER BY id DESC LIMIT 5
        """)
        recent = [dict(r) for r in cur.fetchall()]
        conn.close()

        total_min = row["total_minutes"] if row else 0
        count = row["session_count"] if row else 0

        hours = total_min // 60
        mins = total_min % 60
        time_formatted = f"{hours}h {mins:02d}m" if hours > 0 else f"{mins}m"

        return {
            "session_count": count,
            "total_minutes": total_min,
            "formatted_time": time_formatted,
            "recent_sessions": recent
        }
