"""Task management service."""

import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from lifeos.core.database import get_connection
from lifeos.core.events import bus

class TaskService:
    def list_tasks(
        self,
        filter_status: Optional[str] = None, # "all", "today", "urgent", "completed", "pending"
        project_id: Optional[int] = None,
        search_query: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        conn = get_connection()
        query = """
            SELECT t.*, p.title as project_title, p.color as project_color
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE 1=1
        """
        params = []

        q = search_query or search

        if project_id is not None:
            query += " AND t.project_id = ?"
            params.append(project_id)

        if filter_status == "today":
            today_str = date.today().isoformat()
            query += " AND (t.due_date = ? OR t.due_date IS NULL)"
            params.append(today_str)
        elif filter_status == "urgent":
            query += " AND t.priority = 'URGENT' AND t.is_completed = 0"
        elif filter_status == "completed":
            query += " AND t.is_completed = 1"
        elif filter_status == "pending":
            query += " AND t.is_completed = 0"

        if q:
            query += " AND (t.title LIKE ? OR t.description LIKE ?)"
            params.extend([f"%{q}%", f"%{q}%"])

        # Order by completed asc, priority rank, due_date
        query += """
            ORDER BY t.is_completed ASC,
            CASE t.priority
                WHEN 'URGENT' THEN 1
                WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3
                WHEN 'LOW' THEN 4
                ELSE 5
            END,
            t.due_date ASC, t.id DESC
        """

        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        tasks = []
        for r in rows:
            t = dict(r)
            try:
                t["tags"] = json.loads(t.get("tags") or "[]")
            except Exception:
                t["tags"] = []
            try:
                t["subtasks"] = json.loads(t.get("subtasks_json") or "[]")
            except Exception:
                t["subtasks"] = []
            tasks.append(t)
        conn.close()
        return tasks

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT t.*, p.title as project_title, p.color as project_color
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            WHERE t.id = ?
        """, (task_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        t = dict(row)
        try:
            t["tags"] = json.loads(t.get("tags") or "[]")
        except Exception:
            t["tags"] = []
        try:
            t["subtasks"] = json.loads(t.get("subtasks_json") or "[]")
        except Exception:
            t["subtasks"] = []
        return t

    def create_task(
        self,
        title: str,
        description: str = "",
        project_id: Optional[int] = None,
        priority: str = "MEDIUM",
        due_date: Optional[str] = None,
        estimated_minutes: int = 30,
        tags: Optional[List[str]] = None,
        subtasks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        conn = get_connection()
        cur = conn.cursor()
        now_str = datetime.now().isoformat()
        tags_json = json.dumps(tags or [])
        subtasks_json = json.dumps(subtasks or [])

        cur.execute("""
            INSERT INTO tasks (title, description, project_id, priority, due_date, estimated_minutes, actual_minutes, is_completed, completed_at, tags, subtasks_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 0, 0, NULL, ?, ?, ?)
        """, (title, description, project_id, priority, due_date, estimated_minutes, tags_json, subtasks_json, now_str))
        task_id = cur.lastrowid
        conn.commit()
        conn.close()

        bus.emit("tasks_updated")
        bus.emit("stats_updated")
        return self.get_task(task_id)

    def toggle_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT is_completed FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return None

        new_status = 0 if row["is_completed"] else 1
        completed_at = datetime.now().isoformat() if new_status == 1 else None

        cur.execute("""
            UPDATE tasks SET is_completed = ?, completed_at = ? WHERE id = ?
        """, (new_status, completed_at, task_id))
        conn.commit()
        conn.close()

        bus.emit("tasks_updated")
        bus.emit("stats_updated")
        return self.get_task(task_id)

    def update_task(self, task_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()

        fields = []
        params = []
        for k, v in kwargs.items():
            if k == "subtasks":
                fields.append("subtasks_json = ?")
                params.append(json.dumps(v))
            elif k == "tags":
                fields.append("tags = ?")
                params.append(json.dumps(v))
            elif k in ("title", "description", "project_id", "priority", "due_date", "estimated_minutes", "actual_minutes", "is_completed", "completed_at"):
                fields.append(f"{k} = ?")
                params.append(v)

        if not fields:
            conn.close()
            return self.get_task(task_id)

        params.append(task_id)
        cur.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?", params)
        conn.commit()
        conn.close()

        bus.emit("tasks_updated")
        bus.emit("stats_updated")
        return self.get_task(task_id)

    def delete_task(self, task_id: int) -> bool:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        rows_affected = cur.rowcount
        conn.commit()
        conn.close()

        if rows_affected > 0:
            bus.emit("tasks_updated")
            bus.emit("stats_updated")
            return True
        return False
