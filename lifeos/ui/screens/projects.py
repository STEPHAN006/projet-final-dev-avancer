"""Projects Portfolio Screen for LifeOS (Shadcn / React Native style)."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDIconButton
from lifeos.ui.theme import theme
from lifeos.ui.components.card import AtelierCard
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton, AtelierBadge
from lifeos.ui.components.progress import AtelierProgressBar
from lifeos.ui.components.navigation import AtelierTopBar, AtelierBottomNav
from lifeos.ui.components.dialogs import AddProjectDialog
from lifeos.services.data_service import ds
from lifeos.core.events import bus

class ProjectsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_category = "all"

        with self.canvas.before:
            self._bg_col = Color(rgba=theme.bg_canvas)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar
        self.top_bar = AtelierTopBar(
            title="Projets",
            subtitle="PORTFOLIO & LIVRABLES",
            right_icon="plus",
            right_action=self._open_add_dialog
        )
        self.root_box.add_widget(self.top_bar)

        # Category Filter Tabs
        filter_box = BoxLayout(spacing=6, padding=[16, 10, 16, 6], size_hint_y=None, height=48)
        self.filter_buttons = {}
        cats = [
            ("all", "Tous"),
            ("Dev", "Dev & Code"),
            ("Académique", "Études"),
            ("Santé", "Santé"),
        ]
        for key, label in cats:
            btn = AtelierButton(
                text=label,
                font_size="11sp",
                size_hint_x=1.0
            ) if key == self.selected_category else AtelierGhostButton(
                text=label,
                font_size="11sp",
                size_hint_x=1.0
            )
            btn.bind(on_release=lambda inst, k=key: self._set_cat(k))
            self.filter_buttons[key] = btn
            filter_box.add_widget(btn)

        self.filter_box = filter_box
        self.root_box.add_widget(filter_box)

        # Projects ScrollView
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.projects_box = BoxLayout(
            orientation="vertical",
            spacing=12,
            padding=[16, 8, 16, 20],
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
        bus.subscribe("theme_changed", self._on_theme)

        self.refresh_projects()

    def _on_theme(self, *args, **kwargs):
        self._bg_col.rgba = theme.bg_canvas
        self._update_tabs_ui()
        self.refresh_projects()

    def _update_tabs_ui(self):
        self.filter_box.clear_widgets()
        cats = [
            ("all", "Tous"),
            ("Dev", "Dev & Code"),
            ("Académique", "Études"),
            ("Santé", "Santé"),
        ]
        for key, label in cats:
            btn = AtelierButton(text=label, font_size="11sp", size_hint_x=1.0) if key == self.selected_category else AtelierGhostButton(text=label, font_size="11sp", size_hint_x=1.0)
            btn.bind(on_release=lambda inst, k=key: self._set_cat(k))
            self.filter_box.add_widget(btn)

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

        if self.selected_category != "all":
            projects = [p for p in projects if p.get("category") == self.selected_category]

        if not projects:
            self.projects_box.add_widget(Label(
                text="Aucun projet dans cette catégorie.",
                font_size="13sp",
                color=theme.text_muted,
                size_hint_y=None,
                height=100
            ))
            return

        for p in projects:
            card = AtelierCard(
                orientation="vertical",
                spacing=8,
                padding=[16, 14, 16, 14],
                size_hint_y=None,
                height=110
            )

            # Top Header Row: Category badge & Title
            row_top = BoxLayout(size_hint_y=None, height=24)
            cat_badge = AtelierBadge(text=p.get("category", "Dev"))
            row_top.add_widget(cat_badge)

            lbl_title = Label(
                text=p["title"],
                font_size="14sp",
                bold=True,
                color=theme.text_primary,
                halign="left"
            )
            lbl_title.bind(size=lbl_title.setter("text_size"))
            row_top.add_widget(lbl_title)
            card.add_widget(row_top)

            # Description
            lbl_desc = Label(
                text=p.get("description", ""),
                font_size="11sp",
                color=theme.text_secondary,
                halign="left",
                size_hint_y=None,
                height=20
            )
            lbl_desc.bind(size=lbl_desc.setter("text_size"))
            card.add_widget(lbl_desc)

            # Progress Bar
            prog_val = p.get("calculated_progress", 0)
            pbar = AtelierProgressBar(value=prog_val, bar_height=5)
            card.add_widget(pbar)

            # Footer meta (tasks count & % progress) without broken emojis
            ftr = BoxLayout(size_hint_y=None, height=22)
            lbl_tasks = Label(
                text=f"{p.get('completed_tasks', 0)}/{p.get('total_tasks', 0)} tâches validées",
                font_size="11sp",
                color=theme.text_secondary,
                halign="left"
            )
            lbl_tasks.bind(size=lbl_tasks.setter("text_size"))

            lbl_pct = Label(
                text=f"{prog_val}%",
                font_size="12sp",
                bold=True,
                color=theme.primary,
                halign="right"
            )
            lbl_pct.bind(size=lbl_pct.setter("text_size"))

            ftr.add_widget(lbl_tasks)
            ftr.add_widget(lbl_pct)
            card.add_widget(ftr)

            card.bind(on_touch_down=lambda inst, touch, pid=p["id"]: self._on_project_click(inst, touch, pid))
            self.projects_box.add_widget(card)

    def _on_project_click(self, instance, touch, project_id):
        if instance.collide_point(*touch.pos):
            if self.manager and "project_details" in self.manager.screen_names:
                scr = self.manager.get_screen("project_details")
                scr.load_project(project_id)
                self.manager.current = "project_details"

    def _set_cat(self, cat):
        self.selected_category = cat
        self._update_tabs_ui()
        self.refresh_projects()
