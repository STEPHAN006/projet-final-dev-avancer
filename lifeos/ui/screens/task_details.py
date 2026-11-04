"""Task Details Screen for LifeOS."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDIconButton
from lifeos.ui.theme import (
    BG_CANVAS, BG_CARD, BG_CARD_HOVER, BORDER_COLOR,
    GOLD, CHAMPAGNE, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ERROR, SUCCESS
)
from lifeos.ui.components.card import AtelierCard
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton, AtelierBadge
from lifeos.ui.components.checkbox import AtelierCheckbox
from lifeos.ui.components.navigation import AtelierTopBar
from lifeos.services.data_service import ds

class TaskDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_id = None
        self.task_data = None

        with self.canvas.before:
            Color(rgba=BG_CANVAS)
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
            spacing=16,
            padding=[16, 16, 16, 24],
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)
        self.root_box.add_widget(self.scroll)

        self.add_widget(self.root_box)

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
        if not self.task_data:
            self.content.add_widget(Label(text="Tâche introuvable.", color=TEXT_MUTED))
            return

        t = self.task_data

        # 1. Main Info Card (Title, Status, Priority, Project)
        card_main = AtelierCard(
            orientation="vertical",
            spacing=12,
            padding=[16, 16, 16, 16],
            size_hint_y=None,
            height=270
        )

        lbl_sec = Label(
            text="INFORMATIONS GÉNÉRALES",
            font_size="10sp",
            bold=True,
            color=GOLD,
            halign="left",
            size_hint_y=None,
            height=16
        )
        lbl_sec.bind(size=lbl_sec.setter("text_size"))
        card_main.add_widget(lbl_sec)

        # Title Input
        self.in_title = TextInput(
            text=t.get("title", ""),
            multiline=False,
            background_color=BG_CARD_HOVER,
            foreground_color=TEXT_PRIMARY,
            cursor_color=GOLD,
            padding=[12, 10, 12, 10],
            size_hint_y=None,
            height=42
        )
        card_main.add_widget(self.in_title)

        # Description Input
        self.in_desc = TextInput(
            text=t.get("description", ""),
            multiline=True,
            background_color=BG_CARD_HOVER,
            foreground_color=TEXT_PRIMARY,
            cursor_color=GOLD,
            padding=[12, 8, 12, 8],
            size_hint_y=None,
            height=64
        )
        card_main.add_widget(self.in_desc)

        # Priority & Project Row
        row_p = BoxLayout(spacing=10, size_hint_y=None, height=42)
        self.sp_priority = Spinner(
            text=t.get("priority", "MEDIUM"),
            values=("URGENT", "HIGH", "MEDIUM", "LOW"),
            background_color=BG_CARD_HOVER,
            color=GOLD,
            size_hint_x=0.5
        )
        self.in_est_min = TextInput(
            text=str(t.get("estimated_minutes", 30)),
            hint_text="Est. min",
            input_filter="int",
            multiline=False,
            background_color=BG_CARD_HOVER,
            foreground_color=TEXT_PRIMARY,
            size_hint_x=0.5
        )
        row_p.add_widget(self.sp_priority)
        row_p.add_widget(self.in_est_min)
        card_main.add_widget(row_p)

        # Time Spent Row
        lbl_time_spent = Label(
            text=f"Temps réel passé : [b]{t.get('actual_minutes', 0)} min[/b]  ·  Statut : [b]{'Terminée ✓' if t.get('is_completed') else 'En cours'}[/b]",
            markup=True,
            font_size="12sp",
            color=TEXT_SECONDARY,
            halign="left",
            size_hint_y=None,
            height=20
        )
        lbl_time_spent.bind(size=lbl_time_spent.setter("text_size"))
        card_main.add_widget(lbl_time_spent)

        self.content.add_widget(card_main)

        # 2. Pomodoro Focus Quick Launch Card
        focus_card = AtelierCard(
            orientation="horizontal",
            spacing=14,
            padding=[16, 14, 16, 14],
            size_hint_y=None,
            height=70
        )
        col_f = BoxLayout(orientation="vertical", spacing=2)
        lbl_f_title = Label(
            text="SESSION FOCUS POMODORO",
            font_size="10sp",
            bold=True,
            color=GOLD,
            halign="left"
        )
        lbl_f_title.bind(size=lbl_f_title.setter("text_size"))
        lbl_f_sub = Label(
            text="Lancer 25 min de deep work lié à cette tâche",
            font_size="12sp",
            color=TEXT_PRIMARY,
            halign="left"
        )
        lbl_f_sub.bind(size=lbl_f_sub.setter("text_size"))
        col_f.add_widget(lbl_f_title)
        col_f.add_widget(lbl_f_sub)
        focus_card.add_widget(col_f)

        btn_launch_f = AtelierButton(
            text="Lancer ⏱",
            font_size="12sp",
            size_hint=(None, None),
            size=(90, 40)
        )
        btn_launch_f.bind(on_release=self._launch_focus_for_task)
        focus_card.add_widget(btn_launch_f)
        self.content.add_widget(focus_card)

        # 3. Subtasks Section Card
        self.subtasks_card = AtelierCard(
            orientation="vertical",
            spacing=10,
            padding=[16, 16, 16, 16],
            size_hint_y=None
        )
        lbl_sub_sec = Label(
            text="SOUS-TÂCHES & JALONS",
            font_size="10sp",
            bold=True,
            color=GOLD,
            halign="left",
            size_hint_y=None,
            height=16
        )
        lbl_sub_sec.bind(size=lbl_sub_sec.setter("text_size"))
        self.subtasks_card.add_widget(lbl_sub_sec)

        subtasks = t.get("subtasks", [])
        self.subtask_items = list(subtasks)
        self.subtask_rows_container = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        self.subtask_rows_container.bind(minimum_height=self.subtask_rows_container.setter("height"))
        self._refresh_subtask_rows()
        self.subtasks_card.add_widget(self.subtask_rows_container)

        # Add subtask input row
        row_add = BoxLayout(spacing=8, size_hint_y=None, height=40)
        self.in_new_sub = TextInput(
            hint_text="Ajouter une étape...",
            multiline=False,
            background_color=BG_CARD_HOVER,
            foreground_color=TEXT_PRIMARY,
            padding=[10, 8, 10, 8]
        )
        btn_add_sub = AtelierGhostButton(
            text="+",
            font_size="18sp",
            size_hint=(None, None),
            size=(40, 40)
        )
        btn_add_sub.bind(on_release=self._add_subtask)
        row_add.add_widget(self.in_new_sub)
        row_add.add_widget(btn_add_sub)
        self.subtasks_card.add_widget(row_add)

        # dynamic height
        self.subtasks_card.height = max(160, 80 + len(self.subtask_items) * 44 + 50)
        self.content.add_widget(self.subtasks_card)

        # 4. Action Buttons (Save / Toggle Completion)
        row_actions = BoxLayout(spacing=12, size_hint_y=None, height=48)

        btn_toggle = AtelierGhostButton(
            text="Décocher" if t.get("is_completed") else "Marquer Terminée ✓",
            text_color=SUCCESS if not t.get("is_completed") else TEXT_SECONDARY
        )
        btn_toggle.bind(on_release=self._toggle_completion)

        btn_save = AtelierButton(text="Enregistrer")
        btn_save.bind(on_release=self._save_changes)

        row_actions.add_widget(btn_toggle)
        row_actions.add_widget(btn_save)
        self.content.add_widget(row_actions)

    def _refresh_subtask_rows(self):
        self.subtask_rows_container.clear_widgets()
        for idx, sub in enumerate(self.subtask_items):
            row = BoxLayout(spacing=10, size_hint_y=None, height=36)
            cb = AtelierCheckbox(active=bool(sub.get("done")))
            cb.bind(on_release=lambda _, i=idx: self._toggle_subtask(i))
            row.add_widget(cb)

            txt = f"[s]{sub.get('text', '')}[/s]" if sub.get("done") else sub.get("text", "")
            lbl = Label(
                text=txt,
                markup=True,
                font_size="13sp",
                color=TEXT_MUTED if sub.get("done") else TEXT_PRIMARY,
                halign="left"
            )
            lbl.bind(size=lbl.setter("text_size"))
            row.add_widget(lbl)

            btn_del = MDIconButton(
                icon="close",
                theme_icon_color="Custom",
                icon_color=TEXT_MUTED,
                size_hint=(None, None),
                size=(32, 32)
            )
            btn_del.bind(on_release=lambda _, i=idx: self._del_subtask(i))
            row.add_widget(btn_del)
            self.subtask_rows_container.add_widget(row)

    def _toggle_subtask(self, idx):
        if 0 <= idx < len(self.subtask_items):
            self.subtask_items[idx]["done"] = not self.subtask_items[idx].get("done")
            self._save_subtasks()
            self._refresh_subtask_rows()

    def _del_subtask(self, idx):
        if 0 <= idx < len(self.subtask_items):
            self.subtask_items.pop(idx)
            self._save_subtasks()
            self._refresh_subtask_rows()
            self.subtasks_card.height = max(160, 80 + len(self.subtask_items) * 44 + 50)

    def _add_subtask(self, *args):
        txt = self.in_new_sub.text.strip()
        if txt:
            self.subtask_items.append({"text": txt, "done": False})
            self.in_new_sub.text = ""
            self._save_subtasks()
            self._refresh_subtask_rows()
            self.subtasks_card.height = max(160, 80 + len(self.subtask_items) * 44 + 50)

    def _save_subtasks(self):
        if self.task_id:
            ds.tasks.update_task(self.task_id, subtasks=self.subtask_items)

    def _save_changes(self, *args):
        if not self.task_id:
            return
        title = self.in_title.text.strip()
        desc = self.in_desc.text.strip()
        priority = self.sp_priority.text
        try:
            est_min = int(self.in_est_min.text.strip() or 30)
        except ValueError:
            est_min = 30

        ds.tasks.update_task(
            self.task_id,
            title=title,
            description=desc,
            priority=priority,
            estimated_minutes=est_min,
            subtasks=self.subtask_items
        )
        self._go_back()

    def _toggle_completion(self, *args):
        if self.task_id:
            ds.tasks.toggle_task(self.task_id)
            self.load_task(self.task_id)

    def _delete_current_task(self):
        if self.task_id:
            ds.tasks.delete_task(self.task_id)
            self._go_back()

    def _launch_focus_for_task(self, *args):
        if self.manager and "focus" in self.manager.screen_names and self.task_data:
            focus_screen = self.manager.get_screen("focus")
            focus_screen.setup_focus_session(
                task_id=self.task_id,
                title=self.task_data.get("title", "Focus Session")
            )
            self.manager.current = "focus"
