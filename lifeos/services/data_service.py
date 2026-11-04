"""Unified Offline-First Data Service for LifeOS.
Singleton providing instant zero-latency access to all modules.
"""

from lifeos.services.task_service import TaskService
from lifeos.services.project_service import ProjectService
from lifeos.services.calendar_service import CalendarService
from lifeos.services.study_service import StudyService
from lifeos.services.habit_service import HabitService
from lifeos.services.streak_service import StreakService
from lifeos.services.goal_service import GoalService
from lifeos.services.focus_service import FocusService
from lifeos.services.stats_service import StatsService
from lifeos.services.settings_service import SettingsService

class DataService:
    def __init__(self):
        self.tasks = TaskService()
        self.projects = ProjectService()
        self.calendar = CalendarService()
        self.study = StudyService()
        self.habits = HabitService()
        self.streaks = StreakService()
        self.goals = GoalService()
        self.focus = FocusService()
        self.stats = StatsService()
        self.settings = SettingsService()

ds = DataService()
