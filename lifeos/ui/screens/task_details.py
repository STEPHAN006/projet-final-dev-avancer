"""Task Details Screen for LifeOS (Shadcn / React Native style)."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDIconButton
from lifeos.ui.theme import theme
from lifeos.ui.components.card import AtelierCard
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton, AtelierBadge
from lifeos.ui.components.checkbox import AtelierCheckbox
from lifeos.ui.components.navigation import AtelierTopBar
from lifeos.ui.components.dialogs import ShadcnInput, ShadcnSelect
from lifeos.services.data_service import ds
from lifeos.core.events import bus

class TaskDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_id = None
        self.task_data = None

        with self.canvas.before:
            self._bg_col = Color(rgba=theme.bg_canvas)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar with Back action
        self.top_bar = AtelierTopBar(
            title="Détails de la Tâche",
            subtitle="Spécifications & Focus",
            on_back=self._go_back,
            right_icon="delete-outline",
            right_action=self._delete_current_task
        )
        self.root_box.add_widget(self.top_bar)

        # Scrollable Form
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

        bus.subscribe("tasks_updated", self._on_tasks_updated)
        bus.subscribe("theme_changed", self._on_theme)

    def _on_theme(self, *args, **kwargs):
        self._bg_col.rgba = theme.bg_canvas
        if self.task_id:
            self._render_details()

    def _on_tasks_updated(self, *args, **kwargs):
        if self.task_id:
            self.task_data = ds.tasks.get_task(self.task_id)
            if self.task_data:
                self._render_details()

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _go_back(self):
        if self.manager:
            self.manager.current = "tasks"

    def load_task(self, task_id: int):
        self.task_id = task_id
        self.task_data = ds.tasks.get_task(task_id)
        self._render_details()

    def _render_details(self):
        self.content.clear_widgets()
        t = self.task_data
        if not t:
            self.content.add_widget(Label(text="Tâche introuvable.", color=theme.text_muted))
            return

        # 1. Main Info Card
        card_main = AtelierCard(
            orientation="vertical",
            spacing=10,
            padding=[16, 14, 16, 14],
            size_hint_y=None,
            height=160
        )

        row_priority = BoxLayout(size_hint_y=None, height=26)
        badge = AtelierBadge(text=t.get("priority", "MEDIUM"))
        row_priority.add_widget(badge)

        proj_name = t.get("project_title") or "Aucun projet"
        lbl_proj = Label(
            text=f"Projet: {proj_name}",
            font_size="11sp",
            color=theme.primary,
            halign="left"
        )
        lbl_proj.bind(size=lbl_proj.setter("text_size"))
        row_priority.add_widget(lbl_proj)
        card_main.add_widget(row_priority)

        # Title Input
        self.in_title = ShadcnInput(
            text=t["title"],
            font_size="15sp",
            size_hint_y=None,
            height=42
        )
        card_main.add_widget(self.in_title)

        # Description Input
        self.in_desc = ShadcnInput(
            text=t.get("description") or "",
            hint_text="Description de la tâche...",
            size_hint_y=None,
            height=42
        )
        card_main.add_widget(self.in_desc)
        self.content.add_widget(card_main)

        # 2. Time & Metrics Card
        card_time = AtelierCard(
            orientation="vertical",
            spacing=10,
            padding=[16, 14, 16, 14],
            size_hint_y=None,
            height=126
        )

        lbl_t_head = Label(
            text="ESTIMATION & SUIVI TEMPOREL",
            font_size="10sp",
            bold=True,
            color=theme.text_secondary,
            halign="left",
            size_hint_y=None,
            height=16
        )
        lbl_t_head.bind(size=lbl_t_head.setter("text_size"))
        card_time.add_widget(lbl_t_head)

        row_est = BoxLayout(spacing=10, size_hint_y=None, height=42)
        lbl_est_label = Label(text="Durée estimée (min) :", font_size="12sp", color=theme.text_primary, size_hint_x=0.5, halign="left")
        lbl_est_label.bind(size=lbl_est_label.setter("text_size"))
        self.in_est = ShadcnInput(
            text=str(t.get("estimated_minutes", 30)),
            input_filter="int",
            size_hint_x=0.5
        )
        row_est.add_widget(lbl_est_label)
        row_est.add_widget(self.in_est)
        card_time.add_widget(row_est)

        st_label = "Terminée" if t.get("is_completed") else "En cours"
        lbl_actual = Label(
            text=f"Temps réel passé : [b]{t.get('actual_minutes', 0)} min[/b]  ·  Statut : [b]{st_label}[/b]",
            markup=True,
            font_size="12sp",
            color=theme.text_secondary,
            halign="left",
            size_hint_y=None,
            height=20
        )
        lbl_actual.bind(size=lbl_actual.setter("text_size"))
        card_time.add_widget(lbl_actual)

        self.content.add_widget(card_time)

        # 3. Focus launcher
        card_focus = AtelierCard(
            orientation="horizontal",
            spacing=10,
            padding=[14, 10, 14, 10],
            size_hint_y=None,
            height=54
        )
        lbl_f = Label(
            text="Lancer une session Pomodoro sur cette tâche",
            font_size="12sp",
            color=theme.text_primary,
            halign="left"
        )
        lbl_f.bind(size=lbl_f.setter("text_size"))
        card_focus.add_widget(lbl_f)

        btn_go_focus = AtelierButton(
            text="Lancer Focus",
            font_size="11sp",
            size_hint=(None, None),
            size=(96, 34),
            pos_hint={"center_y": 0.5}
        )
        btn_go_focus.bind(on_release=lambda _: self._start_focus_for_task())
        card_focus.add_widget(btn_go_focus)
        self.content.add_widget(card_focus)

        # 4. Subtasks Section
        subtasks = t.get("subtasks", [])
        card_sub = AtelierCard(
            orientation="vertical",
            spacing=8,
            padding=[16, 14, 16, 14],
            size_hint_y=None
        )
        lbl_sub_head = Label(
            text="SOUS-TÂCHES & JALONS",
            font_size="10sp",
            bold=True,
            color=theme.text_secondary,
            halign="left",
            size_hint_y=None,
            height=16
        )
        lbl_sub_head.bind(size=lbl_sub_head.setter("text_size"))
        card_sub.add_widget(lbl_sub_head)

        for idx, s in enumerate(subtasks):
            s_row = BoxLayout(spacing=10, size_hint_y=None, height=28)
            cb = AtelierCheckbox(active=bool(s.get("done")), size_box=18)
            cb.bind(on_release=lambda _, i=idx: self._toggle_subtask(i))
            s_row.add_widget(cb)

            txt = f"[s]{s['text']}[/s]" if s.get("done") else s["text"]
            lbl_st = Label(
                text=txt,
                markup=True,
                font_size="12sp",
                color=theme.text_muted if s.get("done") else theme.text_primary,
                halign="left"
            )
            lbl_st.bind(size=lbl_st.setter("text_size"))
            s_row.add_widget(lbl_st)
            card_sub.add_widget(s_row)

        # Add subtask row
        row_add_s = BoxLayout(spacing=8, size_hint_y=None, height=38)
        self.in_new_sub = ShadcnInput(hint_text="Ajouter une sous-tâche...", size_hint_x=0.75)
        btn_add_s = AtelierGhostButton(text="+", font_size="16sp", size_hint_x=0.25)
        btn_add_s.bind(on_release=self._add_subtask)
        row_add_s.add_widget(self.in_new_sub)
        row_add_s.add_widget(btn_add_s)
        card_sub.add_widget(row_add_s)

        card_sub.height = 70 + len(subtasks) * 32
        self.content.add_widget(card_sub)

        # 5. Bottom Action Buttons
        btn_row = BoxLayout(spacing=10, size_hint_y=None, height=44)
        btn_save = AtelierButton(text="Sauvegarder", size_hint_x=0.5)
        btn_save.bind(on_release=self._save_changes)

        toggle_label = "Décocher" if t.get("is_completed") else "Marquer Terminée"
        btn_toggle = AtelierGhostButton(text=toggle_label, size_hint_x=0.5)
        btn_toggle.bind(on_release=self._toggle_completion)

        btn_row.add_widget(btn_save)
        btn_row.add_widget(btn_toggle)
        self.content.add_widget(btn_row)

    def _save_changes(self, *args):
        try:
            mins = int(self.in_est.text.strip() or 30)
        except ValueError:
            mins = 30
        ds.tasks.update_task(
            self.task_id,
            title=self.in_title.text.strip() or self.task_data["title"],
            description=self.in_desc.text.strip(),
            estimated_minutes=mins
        )

    def _toggle_completion(self, *args):
        ds.tasks.toggle_task(self.task_id)

    def _delete_current_task(self):
        if self.task_id:
            ds.tasks.delete_task(self.task_id)
            self._go_back()

    def _toggle_subtask(self, idx):
        subtasks = list(self.task_data.get("subtasks", []))
        if 0 <= idx < len(subtasks):
            subtasks[idx]["done"] = not subtasks[idx].get("done", False)
            ds.tasks.update_task(self.task_id, subtasks=subtasks)

    def _add_subtask(self, *args):
        text = self.in_new_sub.text.strip()
        if not text:
            return
        subtasks = list(self.task_data.get("subtasks", []))
        subtasks.append({"text": text, "done": False})
        ds.tasks.update_task(self.task_id, subtasks=subtasks)
        self.in_new_sub.text = ""

    def _start_focus_for_task(self):
        if self.manager and "focus" in self.manager.screen_names:
            self.manager.current = "focus"
