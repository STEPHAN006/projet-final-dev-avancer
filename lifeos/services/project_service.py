"""Project management service."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from lifeos.core.database import get_connection
from lifeos.core.events import bus

class ProjectService:
    def list_projects(self, status: Optional[str] = None, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT p.*,
                (SELECT COUNT(*) FROM tasks t WHERE t.project_id = p.id) as total_tasks,
                (SELECT COUNT(*) FROM tasks t WHERE t.project_id = p.id AND t.is_completed = 1) as completed_tasks
            FROM projects p
            WHERE 1=1
        """
        params = []
        if status:
            query += " AND p.status = ?"
            params.append(status)
        if search_query:
            query += " AND (p.title LIKE ? OR p.description LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        query += " ORDER BY p.id DESC"
        cur.execute(query, params)
        rows = cur.fetchall()
        projects = []
        for r in rows:
            p = dict(r)
            # Recompute dynamic progress if tasks exist
            if p["total_tasks"] > 0:
                p["calculated_progress"] = int((p["completed_tasks"] / p["total_tasks"]) * 100)
            else:
                p["calculated_progress"] = p["progress"]
            projects.append(p)
        conn.close()
        return projects

    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.*,
                (SELECT COUNT(*) FROM tasks t WHERE t.project_id = p.id) as total_tasks,
                (SELECT COUNT(*) FROM tasks t WHERE t.project_id = p.id AND t.is_completed = 1) as completed_tasks
            FROM projects p
            WHERE p.id = ?
        """, (project_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        p = dict(row)
        if p["total_tasks"] > 0:
            p["calculated_progress"] = int((p["completed_tasks"] / p["total_tasks"]) * 100)
        else:
            p["calculated_progress"] = p["progress"]
        return p

    def create_project(
        self,
        title: str,
        description: str = "",
        category: str = "Dev",
        color: str = "#C6A76B",
        deadline: Optional[str] = None
    ) -> Dict[str, Any]:
        conn = get_connection()
        cur = conn.cursor()
        now_str = datetime.now().isoformat()
        cur.execute("""
            INSERT INTO projects (title, description, category, color, progress, status, deadline, created_at)
            VALUES (?, ?, ?, ?, 0, 'active', ?, ?)
        """, (title, description, category, color, deadline, now_str))
        pid = cur.lastrowid
        conn.commit()
        conn.close()

        bus.emit("projects_updated")
        bus.emit("stats_updated")
        return self.get_project(pid)

    def update_project(self, project_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        fields = []
        params = []
        for k, v in kwargs.items():
            if k in ("title", "description", "category", "color", "progress", "status", "deadline"):
                fields.append(f"{k} = ?")
                params.append(v)
        if not fields:
            conn.close()
            return self.get_project(project_id)

        params.append(project_id)
        cur.execute(f"UPDATE projects SET {', '.join(fields)} WHERE id = ?", params)
        conn.commit()
        conn.close()

        bus.emit("projects_updated")
        bus.emit("stats_updated")
        return self.get_project(project_id)

    def delete_project(self, project_id: int) -> bool:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        count = cur.rowcount
        conn.commit()
        conn.close()
        if count > 0:
            bus.emit("projects_updated")
            bus.emit("tasks_updated")
            bus.emit("stats_updated")
            return True
        return False
