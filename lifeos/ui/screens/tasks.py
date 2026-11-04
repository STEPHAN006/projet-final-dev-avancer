"""Tasks Management Screen for LifeOS (Shadcn / React Native style)."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDIcon
from lifeos.ui.theme import theme
from lifeos.ui.components.card import AtelierCard
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton, AtelierBadge
from lifeos.ui.components.checkbox import AtelierCheckbox
from lifeos.ui.components.navigation import AtelierTopBar, AtelierBottomNav
from lifeos.ui.components.dialogs import AddTaskDialog, ShadcnInput
from lifeos.services.data_service import ds
from lifeos.core.events import bus

class TasksScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_filter = "all" # all, today, urgent, pending, completed
        self.search_query = ""

        with self.canvas.before:
            self._bg_col = Color(rgba=theme.bg_canvas)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar
        self.top_bar = AtelierTopBar(
            title="Tâches",
            subtitle="Priorités & Actions",
            right_icon="plus",
            right_action=self._open_add_dialog
        )
        self.root_box.add_widget(self.top_bar)

        # Search Bar & Filter Tabs
        header_ctrls = BoxLayout(orientation="vertical", spacing=8, padding=[16, 10, 16, 6], size_hint_y=None, height=92)

        # Shadcn search input
        self.search_input = ShadcnInput(
            hint_text="Rechercher une tâche...",
            size_hint_y=None,
            height=40
        )
        self.search_input.bind(text=self._on_search)
        header_ctrls.add_widget(self.search_input)

        # Filter tabs
        self.tabs_scroll = ScrollView(size_hint=(1, None), height=34, do_scroll_y=False)
        self.tabs_box = BoxLayout(spacing=6, size_hint_x=None, padding=[2, 0, 2, 0])
        self.tabs_box.bind(minimum_width=self.tabs_box.setter("width"))

        self.filter_buttons = {}
        filters = [
            ("all", "Toutes"),
            ("today", "Aujourd'hui"),
            ("urgent", "Urgentes"),
            ("pending", "En cours"),
            ("completed", "Terminées"),
        ]

        for key, label in filters:
            btn = AtelierButton(
                text=label,
                font_size="11sp",
                size_hint=(None, None),
                size=(88, 32)
            ) if key == self.current_filter else AtelierGhostButton(
                text=label,
                font_size="11sp",
                size_hint=(None, None),
                size=(88, 32)
            )
            btn.bind(on_release=lambda inst, k=key: self._set_filter(k))
            self.filter_buttons[key] = btn
            self.tabs_box.add_widget(btn)

        self.tabs_scroll.add_widget(self.tabs_box)
        header_ctrls.add_widget(self.tabs_scroll)
        self.root_box.add_widget(header_ctrls)

        # Tasks List ScrollView
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.tasks_container = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=[16, 8, 16, 20],
            size_hint_y=None
        )
        self.tasks_container.bind(minimum_height=self.tasks_container.setter("height"))
        self.scroll.add_widget(self.tasks_container)
        self.root_box.add_widget(self.scroll)

        # Bottom Nav
        self.bottom_nav = AtelierBottomNav(
            current_tab="tasks",
            nav_callback=self._handle_navigation
        )
        self.root_box.add_widget(self.bottom_nav)

        self.add_widget(self.root_box)

        bus.subscribe("tasks_updated", lambda *_: self.refresh_tasks())
        bus.subscribe("theme_changed", self._on_theme)

        self.refresh_tasks()

    def _on_theme(self, *args, **kwargs):
        self._bg_col.rgba = theme.bg_canvas
        self._update_tabs_ui()
        self.refresh_tasks()

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_pre_enter(self):
        self.bottom_nav.set_tab("tasks")
        self.refresh_tasks()

    def _handle_navigation(self, route):
        if self.manager and route != "tasks":
            self.manager.current = route

    def _open_add_dialog(self):
        dialog = AddTaskDialog(on_task_created=lambda _: self.refresh_tasks())
        dialog.open()

    def _on_search(self, instance, val):
        self.search_query = val.strip()
        self.refresh_tasks()

    def _set_filter(self, key):
        self.current_filter = key
        self._update_tabs_ui()
        self.refresh_tasks()

    def _update_tabs_ui(self):
        self.tabs_box.clear_widgets()
        filters = [
            ("all", "Toutes"),
            ("today", "Aujourd'hui"),
            ("urgent", "Urgentes"),
            ("pending", "En cours"),
            ("completed", "Terminées"),
        ]
        for key, label in filters:
            if key == self.current_filter:
                btn = AtelierButton(text=label, font_size="11sp", size_hint=(None, None), size=(88, 32))
            else:
                btn = AtelierGhostButton(text=label, font_size="11sp", size_hint=(None, None), size=(88, 32))
            btn.bind(on_release=lambda inst, k=key: self._set_filter(k))
            self.tabs_box.add_widget(btn)

    def refresh_tasks(self):
        self.tasks_container.clear_widgets()

        tasks = ds.tasks.list_tasks(
            filter_status=self.current_filter,
            search=self.search_query
        )

        if not tasks:
            empty_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None, height=140)
            lbl_empty = Label(
                text="Aucune tâche dans cette section.",
                font_size="13sp",
                color=theme.text_muted,
                halign="center"
            )
            empty_box.add_widget(lbl_empty)
            self.tasks_container.add_widget(empty_box)
            return

        for t in tasks:
            card = AtelierCard(
                orientation="horizontal",
                spacing=12,
                padding=[14, 12, 14, 12],
                size_hint_y=None,
                height=72
            )

            # Checkbox
            cb = AtelierCheckbox(active=bool(t["is_completed"]))
            cb.bind(on_release=lambda inst, tid=t["id"]: ds.tasks.toggle_task(tid))
            card.add_widget(cb)

            # Details
            col = BoxLayout(orientation="vertical", spacing=2)
            title_text = f"[s]{t['title']}[/s]" if t["is_completed"] else t["title"]
            lbl_title = Label(
                text=title_text,
                markup=True,
                font_size="13sp",
                bold=True,
                color=theme.text_muted if t["is_completed"] else theme.text_primary,
                halign="left",
                size_hint_y=None,
                height=22
            )
            lbl_title.bind(size=lbl_title.setter("text_size"))

            # Meta Row without broken emojis
            meta = BoxLayout(spacing=10, size_hint_y=None, height=18)
            proj = t.get("project_title") or "Général"
            lbl_proj = Label(
                text=f"Projet: {proj}",
                font_size="11sp",
                color=theme.primary,
                halign="left"
            )
            lbl_proj.bind(size=lbl_proj.setter("text_size"))

            subtasks = t.get("subtasks", [])
            sub_text = ""
            if subtasks:
                done_sub = sum(1 for s in subtasks if s.get("done"))
                sub_text = f" · {done_sub}/{len(subtasks)} sous-tâches"

            lbl_time = Label(
                text=f"{t.get('estimated_minutes', 30)} min{sub_text}",
                font_size="11sp",
                color=theme.text_secondary,
                halign="left"
            )
            lbl_time.bind(size=lbl_time.setter("text_size"))

            meta.add_widget(lbl_proj)
            meta.add_widget(lbl_time)

            col.add_widget(lbl_title)
            col.add_widget(meta)
            card.add_widget(col)

            # Priority Badge
            badge = AtelierBadge(text=t.get("priority", "MEDIUM"))
            card.add_widget(badge)

            # Tap card to view details
            card.bind(on_touch_down=lambda inst, touch, tid=t["id"]: self._on_card_tap(inst, touch, tid))

            self.tasks_container.add_widget(card)

    def _on_card_tap(self, instance, touch, task_id):
        if instance.collide_point(*touch.pos):
            if touch.x > instance.x + 40:
                self._open_task_details(task_id)

    def _open_task_details(self, task_id):
        if self.manager and "task_details" in self.manager.screen_names:
            detail_screen = self.manager.get_screen("task_details")
            detail_screen.load_task(task_id)
            self.manager.current = "task_details"
