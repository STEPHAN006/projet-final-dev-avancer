"""Habits tracking and streaks service."""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from lifeos.core.database import get_connection
from lifeos.core.events import bus

class HabitService:
    def list_habits_with_logs(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM habits ORDER BY id ASC")
        habits = [dict(r) for r in cur.fetchall()]

        # Generate last 7 days dates (oldest to newest: -6, -5, ..., 0)
        today = date.today()
        recent_dates = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]

        for h in habits:
            cur.execute("""
                SELECT date, status FROM habit_logs
                WHERE habit_id = ? AND date >= ?
            """, (h["id"], recent_dates[0]))
            logs_map = {r["date"]: bool(r["status"]) for r in cur.fetchall()}

            h["days"] = [{"date": d, "done": logs_map.get(d, False)} for d in recent_dates]
            h["today_done"] = logs_map.get(today.isoformat(), False)

        conn.close()
        return habits

    def toggle_habit_for_date(self, habit_id: int, target_date: Optional[str] = None) -> bool:
        conn = get_connection()
        cur = conn.cursor()
        d_str = target_date or date.today().isoformat()

        cur.execute("SELECT status FROM habit_logs WHERE habit_id = ? AND date = ?", (habit_id, d_str))
        row = cur.fetchone()
        if row:
            new_status = 0 if row["status"] == 1 else 1
            cur.execute("UPDATE habit_logs SET status = ? WHERE habit_id = ? AND date = ?", (new_status, habit_id, d_str))
            done = bool(new_status)
        else:
            cur.execute("INSERT INTO habit_logs (habit_id, date, status, notes) VALUES (?, ?, 1, '')", (habit_id, d_str))
            done = True

        # Update streak
        self._recalculate_streak(conn, habit_id)

        conn.commit()
        conn.close()

        bus.emit("habits_updated")
        bus.emit("streaks_updated")
        bus.emit("stats_updated")
        return done

    def _recalculate_streak(self, conn, habit_id: int):
        cur = conn.cursor()
        today = date.today()
        # Count consecutive days backwards
        streak = 0
        check_day = today
        while True:
            cur.execute("SELECT status FROM habit_logs WHERE habit_id = ? AND date = ? AND status = 1", (habit_id, check_day.isoformat()))
            if cur.fetchone():
                streak += 1
                check_day -= timedelta(days=1)
            else:
                # If today wasn't done yet, check if yesterday was done to not immediately break
                if check_day == today:
                    check_day -= timedelta(days=1)
                    continue
                break

        cur.execute("SELECT streak_best FROM habits WHERE id = ?", (habit_id,))
        r = cur.fetchone()
        best = max(streak, r["streak_best"] if r else 0)

        cur.execute("UPDATE habits SET streak_current = ?, streak_best = ? WHERE id = ?", (streak, best, habit_id))

    def create_habit(
        self,
        name: str,
        description: str = "",
        frequency: str = "daily",
        target_per_week: int = 7,
        color: str = "#C6A76B",
        icon: str = "star"
    ) -> Dict[str, Any]:
        conn = get_connection()
        cur = conn.cursor()
        now_str = datetime.now().isoformat()
        cur.execute("""
            INSERT INTO habits (name, description, frequency, target_per_week, color, icon, streak_current, streak_best, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?)
        """, (name, description, frequency, target_per_week, color, icon, now_str))
        hid = cur.lastrowid
        conn.commit()
        conn.close()

        bus.emit("habits_updated")
        return {"id": hid, "name": name}

    def delete_habit(self, habit_id: int) -> bool:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        count = cur.rowcount
        conn.commit()
        conn.close()
        if count > 0:
            bus.emit("habits_updated")
            bus.emit("streaks_updated")
            return True
        return False
