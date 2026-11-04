"""LifeOS Application Class and Window Manager."""

import sys
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivymd.app import MDApp
from lifeos.core.config import COLOR_CANVAS
from lifeos.core.database import init_db
from lifeos.backend.server import start_background_server
from lifeos.ui.screens import (
    SplashScreen, DashboardScreen, TasksScreen, TaskDetailsScreen,
    ProjectsScreen, ProjectDetailsScreen, CalendarScreen, StudyScreen,
    HabitsScreen, StreaksScreen, GoalsScreen, FocusScreen,
    StatisticsScreen, SettingsScreen, ModulesScreen
)

class LifeOSApp(MDApp):
    def __init__(self, run_api=True, **kwargs):
        super().__init__(**kwargs)
        self.run_api = run_api

    def build(self):
        # Database init
        init_db()

        # Start FastAPI local background server if requested
        if self.run_api:
            try:
                start_background_server()
            except Exception as e:
                print(f"[LifeOS] Notice: FastAPI server couldn't start ({e}), running offline direct engine.")

        # Window styling
        self.title = "LifeOS — Atelier Executive System"
        Window.clearcolor = COLOR_CANVAS

        # If running on Linux/Desktop, set sleek phone dimensions for optimal preview
        if not hasattr(sys, "getandroidapilevel"):
            Window.size = (412, 860)

        # KivyMD Theme
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"

        # Screen Manager
        sm = ScreenManager(transition=FadeTransition(duration=0.12))
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(TasksScreen(name="tasks"))
        sm.add_widget(TaskDetailsScreen(name="task_details"))
        sm.add_widget(ProjectsScreen(name="projects"))
        sm.add_widget(ProjectDetailsScreen(name="project_details"))
        sm.add_widget(CalendarScreen(name="calendar"))
        sm.add_widget(StudyScreen(name="study"))
        sm.add_widget(HabitsScreen(name="habits"))
        sm.add_widget(StreaksScreen(name="streaks"))
        sm.add_widget(GoalsScreen(name="goals"))
        sm.add_widget(FocusScreen(name="focus"))
        sm.add_widget(StatisticsScreen(name="statistics"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(ModulesScreen(name="modules"))

        sm.current = "splash"
        return sm
