"""Test suite for FastAPI backend endpoints."""

from fastapi.testclient import TestClient
from lifeos.backend.app import app

client = TestClient(app)

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"

def test_tasks_endpoints():
    res = client.get("/api/tasks/")
    assert res.status_code == 200
    tasks = res.json()
    assert isinstance(tasks, list)
    assert len(tasks) > 0

    # Create task
    payload = {
        "title": "API Test Task",
        "description": "Created via FastAPI",
        "priority": "HIGH",
        "estimated_minutes": 25,
        "tags": ["Test"],
        "subtasks": [{"text": "Step 1", "done": False}]
    }
    c_res = client.post("/api/tasks/", json=payload)
    assert c_res.status_code == 201
    created = c_res.json()
    task_id = created["id"]
    assert created["title"] == "API Test Task"

    # Toggle task
    t_res = client.post(f"/api/tasks/{task_id}/toggle")
    assert t_res.status_code == 200
    assert t_res.json()["is_completed"] == 1

    # Delete task
    d_res = client.delete(f"/api/tasks/{task_id}")
    assert d_res.status_code == 200
    assert d_res.json()["success"] is True

def test_dashboard_and_stats():
    res = client.get("/api/stats/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "daily_progress_pct" in data
    assert "current_streak_days" in data

    rep_res = client.get("/api/stats/report?days=7")
    assert rep_res.status_code == 200
    assert len(rep_res.json()["focus_labels"]) == 7

def test_projects_endpoints():
    res = client.get("/api/projects/")
    assert res.status_code == 200
    projects = res.json()
    assert len(projects) >= 4

def test_habits_and_streaks():
    h_res = client.get("/api/habits/")
    assert h_res.status_code == 200
    habits = h_res.json()
    assert len(habits) >= 5

    s_res = client.get("/api/streaks/")
    assert s_res.status_code == 200
    streaks = s_res.json()
    assert "daily_habits" in streaks

def test_goals():
    res = client.get("/api/goals/")
    assert res.status_code == 200
    assert len(res.json()) >= 4

def test_settings_and_export():
    s_res = client.get("/api/settings/")
    assert s_res.status_code == 200
    assert "theme" in s_res.json()

    exp_res = client.get("/api/settings/export")
    assert exp_res.status_code == 200
    assert "tables" in exp_res.json()
