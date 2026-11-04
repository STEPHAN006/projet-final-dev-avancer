"""Unit tests for LifeOS Data Services."""

import os
import pytest
from lifeos.core.database import init_db
from lifeos.services.data_service import ds

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()

def test_task_service_crud():
    # 1. List initial seeded tasks
    tasks = ds.tasks.list_tasks()
    assert len(tasks) >= 5

    # 2. Create task
    new_task = ds.tasks.create_task(
        title="Test Writing Kivy App",
        description="Verify unit tests pass",
        priority="HIGH",
        estimated_minutes=40
    )
    assert new_task["id"] is not None
    assert new_task["title"] == "Test Writing Kivy App"
    assert new_task["is_completed"] == 0

    # 3. Toggle task completion
    toggled = ds.tasks.toggle_task(new_task["id"])
    assert toggled["is_completed"] == 1

    # 4. Update task
    updated = ds.tasks.update_task(new_task["id"], title="Updated Task Title")
    assert updated["title"] == "Updated Task Title"

    # 5. Delete task
    deleted = ds.tasks.delete_task(new_task["id"])
    assert deleted is True

def test_project_service():
    projects = ds.projects.list_projects()
    assert len(projects) >= 4

    p = ds.projects.create_project(
        title="Nouveau Projet Test",
        category="Dev",
        color="#C6A76B"
    )
    assert p["id"] is not None
    assert p["title"] == "Nouveau Projet Test"
    assert p["status"] == "active"

    # Clean up
    assert ds.projects.delete_project(p["id"]) is True

def test_habits_and_streaks():
    overview = ds.streaks.get_streaks_overview()
    assert "daily_habits" in overview
    assert "main_streak_days" in overview
    assert overview["total_today"] >= 5

    # Toggle habit
    first_habit = overview["daily_habits"][0]
    res = ds.habits.toggle_habit_for_date(first_habit["id"])
    assert isinstance(res, bool)

def test_goals_milestones():
    goals = ds.goals.list_goals()
    assert len(goals) >= 4

    g = goals[0]
    initial_progress = g["progress"]
    # Toggle first milestone
    updated_g = ds.goals.toggle_milestone(g["id"], 0)
    assert updated_g is not None

def test_focus_and_stats():
    # Log a focus session
    res = ds.focus.log_session(
        title="Test Deep Work",
        duration_minutes=25,
        mode="pomodoro"
    )
    assert res["id"] is not None
    assert res["duration"] == 25

    # Summary
    summary = ds.stats.get_dashboard_summary()
    assert summary["focus_minutes_today"] >= 25
    assert "daily_progress_pct" in summary
    assert "current_streak_days" in summary

    # Analytics report
    report = ds.stats.get_analytics_report(days=7)
    assert len(report["focus_labels"]) == 7
    assert len(report["focus_hours"]) == 7
