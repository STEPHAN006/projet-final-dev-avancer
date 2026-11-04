"""Study Hub service for academic tracking."""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
from lifeos.core.database import get_connection
from lifeos.core.events import bus

class StudyService:
    def list_courses(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.*,
                (SELECT COUNT(*) FROM study_exams e WHERE e.course_id = c.id) as exams_count,
                (SELECT COUNT(*) FROM study_sessions s WHERE s.course_id = c.id) as sessions_count
            FROM study_courses c
            ORDER BY c.code ASC
        """)
        courses = [dict(r) for r in cur.fetchall()]
        conn.close()
        return courses

    def get_course(self, course_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM study_courses WHERE id = ?", (course_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def create_course(
        self,
        code: str,
        name: str,
        professor: str = "",
        semester: str = "S1",
        color: str = "#DFBA7B",
        target_grade: float = 16.0,
        current_grade: float = 14.0
    ) -> Dict[str, Any]:
        conn = get_connection()
        cur = conn.cursor()
        now_str = datetime.now().isoformat()
        cur.execute("""
            INSERT INTO study_courses (code, name, professor, semester, color, target_grade, current_grade, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (code, name, professor, semester, color, target_grade, current_grade, now_str))
        cid = cur.lastrowid
        conn.commit()
        conn.close()

        bus.emit("study_updated")
        return self.get_course(cid)

    def list_upcoming_exams(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        today_str = date.today().isoformat()
        cur.execute("""
            SELECT e.*, c.code as course_code, c.name as course_name, c.color as course_color
            FROM study_exams e
            JOIN study_courses c ON e.course_id = c.id
            WHERE e.date >= ?
            ORDER BY e.date ASC
        """, (today_str,))
        exams = [dict(r) for r in cur.fetchall()]
        conn.close()
        return exams

    def create_exam(self, course_id: int, title: str, date_str: str, weight: float = 1.0, room: str = "") -> Dict[str, Any]:
        conn = get_connection()
        cur = conn.cursor()
        now_str = datetime.now().isoformat()
        cur.execute("""
            INSERT INTO study_exams (course_id, title, date, weight, room, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (course_id, title, date_str, weight, room, now_str))
        eid = cur.lastrowid
        conn.commit()
        conn.close()

        bus.emit("study_updated")
        return {"id": eid, "course_id": course_id, "title": title, "date": date_str}

    def log_study_session(self, course_id: int, title: str, duration_minutes: int, notes: str = "") -> Dict[str, Any]:
        conn = get_connection()
        cur = conn.cursor()
        now_str = datetime.now().isoformat()
        today_str = date.today().isoformat()
        cur.execute("""
            INSERT INTO study_sessions (course_id, title, date, duration_minutes, notes, completed, created_at)
            VALUES (?, ?, ?, ?, ?, 1, ?)
        """, (course_id, title, today_str, duration_minutes, notes, now_str))
        sid = cur.lastrowid
        conn.commit()
        conn.close()

        bus.emit("study_updated")
        bus.emit("stats_updated")
        return {"id": sid, "course_id": course_id, "duration": duration_minutes}
