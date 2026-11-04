"""Calendar and events service."""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
from lifeos.core.database import get_connection
from lifeos.core.events import bus

class CalendarService:
    def list_events(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        query = "SELECT * FROM calendar_events WHERE 1=1"
        params = []
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        query += " ORDER BY date ASC, start_time ASC"
        cur.execute(query, params)
        events = [dict(r) for r in cur.fetchall()]
        conn.close()
        return events

    def get_events_for_date(self, target_date: str) -> List[Dict[str, Any]]:
        return self.list_events(start_date=target_date, end_date=target_date)

    def create_event(
        self,
        title: str,
        date_str: str,
        start_time: str,
        end_time: str,
        description: str = "",
        event_type: str = "task",
        location: str = "",
        color: str = "#C6A76B",
        is_all_day: bool = False
    ) -> Dict[str, Any]:
        conn = get_connection()
        cur = conn.cursor()
        now_str = datetime.now().isoformat()
        cur.execute("""
            INSERT INTO calendar_events (title, description, date, start_time, end_time, event_type, location, color, is_all_day, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, description, date_str, start_time, end_time, event_type, location, color, 1 if is_all_day else 0, now_str))
        event_id = cur.lastrowid
        conn.commit()
        conn.close()

        bus.emit("calendar_updated")
        return self.get_event(event_id)

    def get_event(self, event_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM calendar_events WHERE id = ?", (event_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def delete_event(self, event_id: int) -> bool:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
        count = cur.rowcount
        conn.commit()
        conn.close()
        if count > 0:
            bus.emit("calendar_updated")
            return True
        return False
