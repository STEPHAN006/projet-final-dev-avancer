"""Goals and milestones tracking service."""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from lifeos.core.database import get_connection
from lifeos.core.events import bus

class GoalService:
    def list_goals(self, category: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        query = "SELECT * FROM goals WHERE 1=1"
        params = []
        if category and category != "Tous":
            query += " AND category = ?"
            params.append(category)
        if status and status != "all":
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY id ASC"
        cur.execute(query, params)
        rows = cur.fetchall()
        goals = []
        for r in rows:
            g = dict(r)
            try:
                g["milestones"] = json.loads(g.get("milestones_json") or "[]")
            except Exception:
                g["milestones"] = []
            goals.append(g)
        conn.close()
        return goals

    def get_goal(self, goal_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        g = dict(row)
        try:
            g["milestones"] = json.loads(g.get("milestones_json") or "[]")
        except Exception:
            g["milestones"] = []
        return g

    def create_goal(
        self,
        title: str,
        description: str = "",
        category: str = "Dev",
        target_date: Optional[str] = None,
        milestones: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        conn = get_connection()
        cur = conn.cursor()
        now_str = datetime.now().isoformat()
        ms = milestones or []
        ms_json = json.dumps(ms)

        # compute initial progress
        done_count = sum(1 for m in ms if m.get("done"))
        progress = int((done_count / len(ms) * 100)) if ms else 0

        cur.execute("""
            INSERT INTO goals (title, description, category, target_date, progress, status, milestones_json, created_at)
            VALUES (?, ?, ?, ?, ?, 'active', ?, ?)
        """, (title, description, category, target_date, progress, ms_json, now_str))
        gid = cur.lastrowid
        conn.commit()
        conn.close()

        bus.emit("goals_updated")
        bus.emit("stats_updated")
        return self.get_goal(gid)

    def toggle_milestone(self, goal_id: int, milestone_index: int) -> Optional[Dict[str, Any]]:
        goal = self.get_goal(goal_id)
        if not goal:
            return None
        ms = goal.get("milestones", [])
        if 0 <= milestone_index < len(ms):
            ms[milestone_index]["done"] = not ms[milestone_index].get("done", False)

        done_count = sum(1 for m in ms if m.get("done"))
        new_progress = int((done_count / len(ms) * 100)) if ms else goal["progress"]
        status = "completed" if (ms and done_count == len(ms)) else "active"

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE goals
            SET milestones_json = ?, progress = ?, status = ?
            WHERE id = ?
        """, (json.dumps(ms), new_progress, status, goal_id))
        conn.commit()
        conn.close()

        bus.emit("goals_updated")
        bus.emit("stats_updated")
        return self.get_goal(goal_id)

    def delete_goal(self, goal_id: int) -> bool:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        count = cur.rowcount
        conn.commit()
        conn.close()
        if count > 0:
            bus.emit("goals_updated")
            bus.emit("stats_updated")
            return True
        return False
