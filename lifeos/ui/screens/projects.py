"""Projects Overview Screen for LifeOS."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from lifeos.ui.theme import (
    BG_CANVAS, BG_CARD, BG_CARD_HOVER, BORDER_COLOR,
    GOLD, CHAMPAGNE, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED
)
from lifeos.ui.components.card import AtelierCard
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton
from lifeos.ui.components.progress import AtelierProgressBar
from lifeos.ui.components.navigation import AtelierTopBar, AtelierBottomNav
from lifeos.ui.components.dialogs import AddProjectDialog
from lifeos.services.data_service import ds
from lifeos.core.events import bus

class ProjectsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(rgba=BG_CANVAS)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar
        self.top_bar = AtelierTopBar(
            title="Projets",
            subtitle="Vision & Chantiers",
            right_icon="plus",
            right_action=self._open_add_dialog
        )
        self.root_box.add_widget(self.top_bar)

        # Projects ScrollView
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.projects_box = BoxLayout(
            orientation="vertical",
            spacing=14,
            padding=[16, 16, 16, 20],
            size_hint_y=None
        )
        self.projects_box.bind(minimum_height=self.projects_box.setter("height"))
        self.scroll.add_widget(self.projects_box)
        self.root_box.add_widget(self.scroll)

        # Bottom Nav
        self.bottom_nav = AtelierBottomNav(
            current_tab="projects",
            nav_callback=self._handle_navigation
        )
        self.root_box.add_widget(self.bottom_nav)

        self.add_widget(self.root_box)

        bus.subscribe("projects_updated", lambda *_: self.refresh_projects())
        bus.subscribe("tasks_updated", lambda *_: self.refresh_projects())

        self.refresh_projects()

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_pre_enter(self):
        self.bottom_nav.set_tab("projects")
        self.refresh_projects()

    def _handle_navigation(self, route):
        if self.manager and route != "projects":
            self.manager.current = route

    def _open_add_dialog(self):
        dialog = AddProjectDialog(on_project_created=lambda _: self.refresh_projects())
        dialog.open()

    def refresh_projects(self):
        self.projects_box.clear_widgets()
        projects = ds.projects.list_projects()

        if not projects:
            self.projects_box.add_widget(Label(
                text="Aucun projet actif. Créez-en un avec le bouton '+'.",
                color=TEXT_MUTED,
                size_hint_y=None,
                height=100
            ))
            return

        for p in projects:
            card = AtelierCard(
                orientation="vertical",
                spacing=10,
                padding=[16, 14, 16, 14],
                size_hint_y=None,
                height=138
            )

            # Header row: Title + Category pill
            hdr = BoxLayout(spacing=8, size_hint_y=None, height=24)
            lbl_title = Label(
                text=p["title"],
                font_size="15sp",
                bold=True,
                color=TEXT_PRIMARY,
                halign="left"
            )
            lbl_title.bind(size=lbl_title.setter("text_size"))

            lbl_cat = Label(
                text=p.get("category", "Dev").upper(),
                font_size="10sp",
                bold=True,
                color=GOLD,
                halign="right",
                size_hint_x=0.3
            )
            lbl_cat.bind(size=lbl_cat.setter("text_size"))

            hdr.add_widget(lbl_title)
            hdr.add_widget(lbl_cat)
            card.add_widget(hdr)

            # Description
            lbl_desc = Label(
                text=p.get("description", "") or "Aucune description",
                font_size="12sp",
                color=TEXT_SECONDARY,
                halign="left",
                size_hint_y=None,
                height=22
            )
            lbl_desc.bind(size=lbl_desc.setter("text_size"))
            card.add_widget(lbl_desc)

            # Progress Bar
            prog_val = p.get("calculated_progress", 0)
            pbar = AtelierProgressBar(value=prog_val, bar_height=5)
            card.add_widget(pbar)

            # Footer meta (tasks count & % progress)
            ftr = BoxLayout(size_hint_y=None, height=22)
            lbl_tasks = Label(
                text=f"✓ {p.get('completed_tasks', 0)}/{p.get('total_tasks', 0)} tâches",
                font_size="11sp",
                color=TEXT_SECONDARY,
                halign="left"
            )
            lbl_tasks.bind(size=lbl_tasks.setter("text_size"))

            lbl_pct = Label(
                text=f"{prog_val}%",
                font_size="12sp",
                bold=True,
                color=GOLD,
                halign="right"
            )
            lbl_pct.bind(size=lbl_pct.setter("text_size"))

            ftr.add_widget(lbl_tasks)
            ftr.add_widget(lbl_pct)
            card.add_widget(ftr)

            # Click handler to open project details
            card.bind(on_touch_down=lambda inst, touch, pid=p["id"]: self._on_project_click(inst, touch, pid))
            self.projects_box.add_widget(card)

    def _on_project_click(self, instance, touch, project_id):
        if instance.collide_point(*touch.pos):
            if self.manager and "project_details" in self.manager.screen_names:
                scr = self.manager.get_screen("project_details")
                scr.load_project(project_id)
                self.manager.current = "project_details"
