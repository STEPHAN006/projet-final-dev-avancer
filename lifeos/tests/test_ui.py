"""Unit tests for LifeOS UI Screens and Components."""

import pytest
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from lifeos.core.database import init_db
from lifeos.ui.screens import (
    SplashScreen, DashboardScreen, TasksScreen, TaskDetailsScreen,
    ProjectsScreen, ProjectDetailsScreen, CalendarScreen, StudyScreen,
    HabitsScreen, StreaksScreen, GoalsScreen, FocusScreen,
    StatisticsScreen, SettingsScreen, ModulesScreen
)

class DummyMDApp(MDApp):
    def build(self):
        return None

@pytest.fixture(scope="session", autouse=True)
def init_test_app():
    app = DummyMDApp()
    app.theme_cls.theme_style = "Dark"
    app.theme_cls.primary_palette = "Amber"
    yield app

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_screen_instantiation():
    sm = ScreenManager()

    splash = SplashScreen(name="splash")
    dash = DashboardScreen(name="dashboard")
    tasks = TasksScreen(name="tasks")
    t_details = TaskDetailsScreen(name="task_details")
    projects = ProjectsScreen(name="projects")
    p_details = ProjectDetailsScreen(name="project_details")
    cal = CalendarScreen(name="calendar")
    study = StudyScreen(name="study")
    habits = HabitsScreen(name="habits")
    streaks = StreaksScreen(name="streaks")
    goals = GoalsScreen(name="goals")
    focus = FocusScreen(name="focus")
    stats = StatisticsScreen(name="statistics")
    settings = SettingsScreen(name="settings")
    modules = ModulesScreen(name="modules")

    screens = [
        splash, dash, tasks, t_details, projects, p_details,
        cal, study, habits, streaks, goals, focus,
        stats, settings, modules
    ]

    for s in screens:
        sm.add_widget(s)

    assert len(sm.screen_names) == 15
    assert "dashboard" in sm.screen_names
    assert "study" in sm.screen_names
    assert "streaks" in sm.screen_names
    assert "focus" in sm.screen_names
    assert "statistics" in sm.screen_names

def test_task_details_loading():
    screen = TaskDetailsScreen(name="task_details")
    # Load first seeded task (id=1)
    screen.load_task(1)
    assert screen.task_id == 1
    assert screen.task_data is not None
    assert len(screen.content.children) > 0

def test_project_details_loading():
    screen = ProjectDetailsScreen(name="project_details")
    # Load first seeded project (id=1)
    screen.load_project(1)
    assert screen.project_id == 1
    assert screen.project_data is not None

def test_study_screen_refresh():
    screen = StudyScreen(name="study")
    screen.refresh_data()
    assert len(screen.content.children) >= 4

def test_habits_screen_refresh():
    screen = HabitsScreen(name="habits")
    screen.refresh_habits()
    assert len(screen.content.children) >= 3

def test_streaks_screen_refresh():
    screen = StreaksScreen(name="streaks")
    screen.refresh_data()
    assert len(screen.content.children) >= 3

def test_goals_screen_refresh():
    screen = GoalsScreen(name="goals")
    screen.refresh_goals()
    assert len(screen.content.children) >= 3

def test_focus_timer_modes():
    screen = FocusScreen(name="focus")
    assert screen.mode == "pomodoro"
    assert screen.preset_seconds == 25 * 60

    screen._set_mode("short_break")
    assert screen.mode == "short_break"
    assert screen.preset_seconds == 5 * 60

    screen._set_mode("stopwatch")
    assert screen.mode == "stopwatch"
    assert screen.preset_seconds == 0

def test_statistics_screen_refresh():
    screen = StatisticsScreen(name="statistics")
    screen.refresh_stats()
    assert len(screen.content.children) >= 4

def test_settings_screen_refresh():
    screen = SettingsScreen(name="settings")
    screen.refresh_settings()
    assert len(screen.content.children) >= 5

def test_theme_toggle_and_colors():
    from lifeos.ui.theme import theme

    theme.set_mode("light")
    assert theme.is_light is True
    assert theme.bg_canvas != theme.bg_surface or theme.bg_canvas is not None

    bg_u, fg_u = theme.badge_colors("URGENT")
    assert bg_u is not None and fg_u is not None

    theme.toggle()
    assert theme.is_light is False

    theme.set_mode("light")
    assert theme.is_light is True
