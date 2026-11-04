"""Project Details Screen for LifeOS."""

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
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton, AtelierBadge
from lifeos.ui.components.checkbox import AtelierCheckbox
from lifeos.ui.components.progress import AtelierProgressBar
from lifeos.ui.components.navigation import AtelierTopBar
from lifeos.ui.components.dialogs import AddTaskDialog
from lifeos.services.data_service import ds
from lifeos.core.events import bus

class ProjectDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_id = None
        self.project_data = None

        with self.canvas.before:
            Color(rgba=BG_CANVAS)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar
        self.top_bar = AtelierTopBar(
            title="Détails du Projet",
            subtitle="Chantier & Tâches",
            on_back=self._go_back,
            right_icon="delete-outline",
            right_action=self._delete_current_project
        )
        self.root_box.add_widget(self.top_bar)

        # Scroll
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(
            orientation="vertical",
            spacing=16,
            padding=[16, 16, 16, 24],
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)
        self.root_box.add_widget(self.scroll)

        self.add_widget(self.root_box)

        bus.subscribe("tasks_updated", lambda *_: self.refresh())

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _go_back(self):
        if self.manager:
            self.manager.current = "projects"

    def load_project(self, project_id: int):
        self.project_id = project_id
        self.refresh()

    def refresh(self):
        if not self.project_id:
            return
        self.project_data = ds.projects.get_project(self.project_id)
        self._render()

    def _render(self):
        self.content.clear_widgets()
        if not self.project_data:
            self.content.add_widget(Label(text="Projet introuvable.", color=TEXT_MUTED))
            return

        p = self.project_data
        self.top_bar.title = p["title"]
        self.top_bar.subtitle = p.get("category", "Projet").upper()

        # 1. Summary Card
        card_sum = AtelierCard(
            orientation="vertical",
            spacing=10,
            padding=[16, 16, 16, 16],
            size_hint_y=None,
            height=130
        )
        lbl_desc = Label(
            text=p.get("description", "") or "Aucune description renseignée.",
            font_size="13sp",
            color=TEXT_PRIMARY,
            halign="left",
            size_hint_y=None,
            height=36
        )
        lbl_desc.bind(size=lbl_desc.setter("text_size"))
        card_sum.add_widget(lbl_desc)

        prog = p.get("calculated_progress", 0)
        pbar = AtelierProgressBar(value=prog, bar_height=6)
        card_sum.add_widget(pbar)

        row_meta = BoxLayout(size_hint_y=None, height=22)
        lbl_tasks_meta = Label(
            text=f"Progression : {prog}% ({p.get('completed_tasks', 0)}/{p.get('total_tasks', 0)} terminées)",
            font_size="12sp",
            color=GOLD,
            halign="left"
        )
        lbl_tasks_meta.bind(size=lbl_tasks_meta.setter("text_size"))
        row_meta.add_widget(lbl_tasks_meta)
        card_sum.add_widget(row_meta)
        self.content.add_widget(card_sum)

        # 2. Add Task Button
        btn_add_task = AtelierButton(
            text="+ Ajouter une tâche à ce projet",
            font_size="13sp",
            size_hint_y=None,
            height=44
        )
        btn_add_task.bind(on_release=self._open_add_task_dialog)
        self.content.add_widget(btn_add_task)

        # 3. Tasks list (Pending & Completed)
        tasks = ds.tasks.list_tasks(project_id=self.project_id)
        pending = [t for t in tasks if not t.get("is_completed")]
        completed = [t for t in tasks if t.get("is_completed")]

        # --- Section À FAIRE ---
        lbl_sec_todo = Label(
            text=f"À FAIRE ({len(pending)})",
            font_size="12sp",
            bold=True,
            color=GOLD,
            halign="left",
            size_hint_y=None,
            height=26
        )
        lbl_sec_todo.bind(size=lbl_sec_todo.setter("text_size"))
        self.content.add_widget(lbl_sec_todo)

        if not pending:
            self.content.add_widget(Label(
                text="Toutes les tâches de ce projet sont terminées !",
                font_size="12sp",
                color=TEXT_MUTED,
                size_hint_y=None,
                height=30
            ))
        else:
            for t in pending:
                self.content.add_widget(self._build_task_row(t))

        # --- Section TERMINÉES ---
        if completed:
            lbl_sec_done = Label(
                text=f"TERMINÉES ({len(completed)})",
                font_size="12sp",
                bold=True,
                color=TEXT_SECONDARY,
                halign="left",
                size_hint_y=None,
                height=26
            )
            lbl_sec_done.bind(size=lbl_sec_done.setter("text_size"))
            self.content.add_widget(lbl_sec_done)

            for t in completed:
                self.content.add_widget(self._build_task_row(t))

    def _build_task_row(self, t):
        card = AtelierCard(
            orientation="horizontal",
            spacing=12,
            padding=[12, 10, 12, 10],
            size_hint_y=None,
            height=62
        )
        cb = AtelierCheckbox(active=bool(t["is_completed"]))
        cb.bind(on_release=lambda _, tid=t["id"]: ds.tasks.toggle_task(tid))
        card.add_widget(cb)

        txt = f"[s]{t['title']}[/s]" if t["is_completed"] else t["title"]
        lbl = Label(
            text=txt,
            markup=True,
            font_size="13sp",
            bold=True,
            color=TEXT_MUTED if t["is_completed"] else TEXT_PRIMARY,
            halign="left"
        )
        lbl.bind(size=lbl.setter("text_size"))
        card.add_widget(lbl)

        badge = AtelierBadge(text=t.get("priority", "MEDIUM"))
        card.add_widget(badge)

        card.bind(on_touch_down=lambda inst, touch, tid=t["id"]: self._on_task_tap(inst, touch, tid))
        return card

    def _on_task_tap(self, instance, touch, task_id):
        if instance.collide_point(*touch.pos) and touch.x > instance.x + 40:
            if self.manager and "task_details" in self.manager.screen_names:
                scr = self.manager.get_screen("task_details")
                scr.load_task(task_id)
                self.manager.current = "task_details"

    def _open_add_task_dialog(self, *args):
        dialog = AddTaskDialog(
            initial_project_id=self.project_id,
            on_task_created=lambda _: self.refresh()
        )
        dialog.open()

    def _delete_current_project(self):
        if self.project_id:
            ds.projects.delete_project(self.project_id)
            self._go_back()
