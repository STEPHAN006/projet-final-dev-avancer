"""Project Details Screen for LifeOS (Shadcn / React Native style)."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from lifeos.ui.theme import theme
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
            self._bg_col = Color(rgba=theme.bg_canvas)
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
            spacing=14,
            padding=[16, 14, 16, 24],
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)
        self.root_box.add_widget(self.scroll)

        self.add_widget(self.root_box)

        bus.subscribe("tasks_updated", lambda *_: self.refresh())
        bus.subscribe("theme_changed", self._on_theme)

    def _on_theme(self, *args, **kwargs):
        self._bg_col.rgba = theme.bg_canvas
        self.refresh()

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
        if not self.project_data:
            return

        self.content.clear_widgets()
        p = self.project_data

        # 1. Main Info Card
        card_info = AtelierCard(
            orientation="vertical",
            spacing=8,
            padding=[16, 14, 16, 14],
            size_hint_y=None,
            height=130
        )
        row_cat = BoxLayout(size_hint_y=None, height=24)
        cat_badge = AtelierBadge(text=p.get("category", "Dev"))
        row_cat.add_widget(cat_badge)
        card_info.add_widget(row_cat)

        lbl_title = Label(
            text=p["title"],
            font_size="17sp",
            bold=True,
            color=theme.text_primary,
            halign="left",
            size_hint_y=None,
            height=26
        )
        lbl_title.bind(size=lbl_title.setter("text_size"))
        card_info.add_widget(lbl_title)

        lbl_desc = Label(
            text=p.get("description") or "Aucune description",
            font_size="12sp",
            color=theme.text_secondary,
            halign="left",
            size_hint_y=None,
            height=20
        )
        lbl_desc.bind(size=lbl_desc.setter("text_size"))
        card_info.add_widget(lbl_desc)

        # Progress bar
        prog_row = BoxLayout(spacing=10, size_hint_y=None, height=18)
        prog_bar = AtelierProgressBar(value=p.get("calculated_progress", 0), size_hint_x=0.8, pos_hint={"center_y": 0.5})
        lbl_pct = Label(text=f"{p.get('calculated_progress', 0)}%", font_size="11sp", bold=True, color=theme.primary, size_hint_x=0.2)
        prog_row.add_widget(prog_bar)
        prog_row.add_widget(lbl_pct)
        card_info.add_widget(prog_row)

        self.content.add_widget(card_info)

        # 2. Tasks header & Add button
        row_tasks_head = BoxLayout(size_hint_y=None, height=28)
        lbl_th = Label(
            text=f"TÂCHES LIÉES ({len(p.get('tasks', []))})",
            font_size="11sp",
            bold=True,
            color=theme.text_secondary,
            halign="left"
        )
        lbl_th.bind(size=lbl_th.setter("text_size"))
        row_tasks_head.add_widget(lbl_th)

        btn_add_t = AtelierGhostButton(
            text="+ Tâche",
            font_size="11sp",
            size_hint=(None, 1),
            width=76
        )
        btn_add_t.bind(on_release=self._open_add_task_dialog)
        row_tasks_head.add_widget(btn_add_t)
        self.content.add_widget(row_tasks_head)

        # 3. Tasks list
        tasks = p.get("tasks", [])
        if not tasks:
            self.content.add_widget(Label(
                text="Aucune tâche dans ce projet.",
                font_size="13sp",
                color=theme.text_muted,
                size_hint_y=None,
                height=60
            ))
        else:
            for t in tasks:
                t_card = AtelierCard(
                    orientation="horizontal",
                    spacing=12,
                    padding=[12, 10, 12, 10],
                    size_hint_y=None,
                    height=56
                )
                cb = AtelierCheckbox(active=bool(t["is_completed"]))
                cb.bind(on_release=lambda _, tid=t["id"]: ds.tasks.toggle_task(tid))
                t_card.add_widget(cb)

                txt = f"[s]{t['title']}[/s]" if t["is_completed"] else t["title"]
                lbl = Label(
                    text=txt,
                    markup=True,
                    font_size="13sp",
                    bold=True,
                    color=theme.text_muted if t["is_completed"] else theme.text_primary,
                    halign="left"
                )
                lbl.bind(size=lbl.setter("text_size"))
                t_card.add_widget(lbl)

                badge = AtelierBadge(text=t.get("priority", "MEDIUM"))
                t_card.add_widget(badge)

                self.content.add_widget(t_card)

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
