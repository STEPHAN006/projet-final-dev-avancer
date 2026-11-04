"""Shadcn / React Native Style Dialogs and Form Inputs for LifeOS."""

from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle, Line
from lifeos.ui.theme import theme
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton
from lifeos.services.data_service import ds
from lifeos.core.events import bus

class ShadcnInput(TextInput):
    """Shadcn Style Text Input: clean 1px border, smooth rounded-8, focus border."""
    def __init__(self, **kwargs):
        kwargs.setdefault("background_color", [0, 0, 0, 0])
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("foreground_color", theme.text_primary)
        kwargs.setdefault("cursor_color", theme.primary)
        kwargs.setdefault("hint_text_color", theme.text_muted)
        kwargs.setdefault("multiline", False)
        kwargs.setdefault("padding", [12, 10, 12, 10])
        kwargs.setdefault("font_size", "14sp")
        super().__init__(**kwargs)

        self.bind(pos=self._update_canvas, size=self._update_canvas, focus=self._on_focus)
        with self.canvas.before:
            self._bg_col = Color(rgba=theme.bg_input)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            self._border_col = Color(rgba=theme.border)
            self._border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1.0)

        bus.subscribe("theme_changed", self._on_theme)

    def _on_theme(self, *args, **kwargs):
        self.foreground_color = theme.text_primary
        self.cursor_color = theme.primary
        self.hint_text_color = theme.text_muted
        self._bg_col.rgba = theme.bg_input
        self._border_col.rgba = theme.border
        self._update_canvas()

    def _on_focus(self, instance, is_focused):
        if is_focused:
            self._border_col.rgba = theme.border_focus
            self._border_line.width = 1.4
        else:
            self._border_col.rgba = theme.border
            self._border_line.width = 1.0

    def _update_canvas(self, *args):
        if hasattr(self, "_bg_rect"):
            self._bg_rect.pos = self.pos
            self._bg_rect.size = self.size
            self._border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, 8)


class ShadcnSelect(Spinner):
    """Shadcn Style Dropdown Select: clean border, rounded-8, subtle caret."""
    def __init__(self, **kwargs):
        kwargs.setdefault("background_color", [0, 0, 0, 0])
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("color", theme.text_primary)
        kwargs.setdefault("font_size", "13sp")
        super().__init__(**kwargs)

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        with self.canvas.before:
            self._bg_col = Color(rgba=theme.bg_input)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            self._border_col = Color(rgba=theme.border)
            self._border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1.0)

        bus.subscribe("theme_changed", self._on_theme)

    def _on_theme(self, *args, **kwargs):
        self.color = theme.text_primary
        self._bg_col.rgba = theme.bg_input
        self._border_col.rgba = theme.border

    def _update_canvas(self, *args):
        if hasattr(self, "_bg_rect"):
            self._bg_rect.pos = self.pos
            self._bg_rect.size = self.size
            self._border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, 8)


# Alias for backwards compatibility
StyledInput = ShadcnInput


class AddTaskDialog(ModalView):
    def __init__(self, on_task_created=None, initial_project_id=None, **kwargs):
        super().__init__(**kwargs)
        self.on_task_created = on_task_created
        self.size_hint = (0.9, None)
        self.height = 420
        self.auto_dismiss = True
        self.background_color = [0, 0, 0, 0.55]

        # Container
        box = BoxLayout(orientation="vertical", spacing=12, padding=18)
        with box.canvas.before:
            self._b_col = Color(rgba=theme.bg_surface)
            self._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[14])
            self._l_col = Color(rgba=theme.border)
            self._line = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, 14), width=1.0)
        box.bind(pos=lambda *_: self._update(box), size=lambda *_: self._update(box))

        # Title
        box.add_widget(Label(
            text="Nouvelle Tâche",
            font_size="17sp",
            bold=True,
            color=theme.text_primary,
            size_hint_y=None,
            height=26
        ))

        # Input Title
        self.in_title = ShadcnInput(hint_text="Intitulé de la tâche...", size_hint_y=None, height=42)
        box.add_widget(self.in_title)

        # Input Description
        self.in_desc = ShadcnInput(hint_text="Description ou notes rapides...", size_hint_y=None, height=42)
        box.add_widget(self.in_desc)

        # Priority & Time Row
        row = BoxLayout(spacing=10, size_hint_y=None, height=42)
        self.sp_priority = ShadcnSelect(
            text="URGENT",
            values=("URGENT", "HIGH", "MEDIUM", "LOW"),
            size_hint_x=0.5
        )
        self.in_time = ShadcnInput(
            hint_text="Durée (min, ex: 30)",
            text="30",
            input_filter="int",
            size_hint_x=0.5
        )
        row.add_widget(self.sp_priority)
        row.add_widget(self.in_time)
        box.add_widget(row)

        # Project selection spinner
        projects = ds.projects.list_projects()
        self.project_map = {f"{p['title']}": p["id"] for p in projects}
        self.project_map["Aucun projet"] = None
        proj_values = list(self.project_map.keys())

        default_proj_text = "Aucun projet"
        if initial_project_id:
            for title, pid in self.project_map.items():
                if pid == initial_project_id:
                    default_proj_text = title
                    break

        self.sp_project = ShadcnSelect(
            text=default_proj_text,
            values=proj_values,
            size_hint_y=None,
            height=42
        )
        box.add_widget(self.sp_project)

        # Action Buttons
        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=44)
        btn_cancel = AtelierGhostButton(text="Annuler", size_hint_x=0.45)
        btn_cancel.bind(on_release=lambda x: self.dismiss())
        btn_submit = AtelierButton(text="Créer la tâche", size_hint_x=0.55)
        btn_submit.bind(on_release=self._submit)

        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_submit)
        box.add_widget(btn_box)

        self.add_widget(box)

    def _update(self, box):
        self._rect.pos = box.pos
        self._rect.size = box.size
        self._line.rounded_rectangle = (box.x, box.y, box.width, box.height, 14)

    def _submit(self, *args):
        title = self.in_title.text.strip()
        if not title:
            return
        desc = self.in_desc.text.strip()
        priority = self.sp_priority.text
        proj_id = self.project_map.get(self.sp_project.text)
        try:
            mins = int(self.in_time.text.strip() or 30)
        except ValueError:
            mins = 30

        task = ds.tasks.create_task(
            title=title,
            description=desc,
            priority=priority,
            project_id=proj_id,
            estimated_minutes=mins
        )
        if self.on_task_created:
            self.on_task_created(task)
        self.dismiss()


class AddProjectDialog(ModalView):
    def __init__(self, on_project_created=None, **kwargs):
        super().__init__(**kwargs)
        self.on_project_created = on_project_created
        self.size_hint = (0.9, None)
        self.height = 370
        self.auto_dismiss = True
        self.background_color = [0, 0, 0, 0.55]

        box = BoxLayout(orientation="vertical", spacing=12, padding=18)
        with box.canvas.before:
            self._b_col = Color(rgba=theme.bg_surface)
            self._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[14])
            self._l_col = Color(rgba=theme.border)
            self._line = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, 14), width=1.0)
        box.bind(pos=lambda *_: self._update(box), size=lambda *_: self._update(box))

        box.add_widget(Label(
            text="Nouveau Projet",
            font_size="17sp",
            bold=True,
            color=theme.text_primary,
            size_hint_y=None,
            height=26
        ))

        self.in_title = ShadcnInput(hint_text="Titre du projet...", size_hint_y=None, height=42)
        box.add_widget(self.in_title)

        self.in_desc = ShadcnInput(hint_text="Objectif ou description...", size_hint_y=None, height=42)
        box.add_widget(self.in_desc)

        row = BoxLayout(spacing=10, size_hint_y=None, height=42)
        self.sp_category = ShadcnSelect(
            text="Dev",
            values=("Dev", "Académique", "Santé", "Personnel"),
            size_hint_x=0.5
        )
        self.sp_color = ShadcnSelect(
            text="Bleu",
            values=("Bleu", "Indigo", "Vert", "Ambre"),
            size_hint_x=0.5
        )
        row.add_widget(self.sp_category)
        row.add_widget(self.sp_color)
        box.add_widget(row)

        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=44)
        btn_cancel = AtelierGhostButton(text="Annuler", size_hint_x=0.45)
        btn_cancel.bind(on_release=lambda x: self.dismiss())
        btn_submit = AtelierButton(text="Créer le projet", size_hint_x=0.55)
        btn_submit.bind(on_release=self._submit)

        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_submit)
        box.add_widget(btn_box)

        self.add_widget(box)

    def _update(self, box):
        self._rect.pos = box.pos
        self._rect.size = box.size
        self._line.rounded_rectangle = (box.x, box.y, box.width, box.height, 14)

    def _submit(self, *args):
        title = self.in_title.text.strip()
        if not title:
            return
        desc = self.in_desc.text.strip()
        cat = self.sp_category.text
        color_map = {"Bleu": "#2563EB", "Indigo": "#6366F1", "Vert": "#10B981", "Ambre": "#F59E0B"}
        color = color_map.get(self.sp_color.text, "#2563EB")

        p = ds.projects.create_project(title=title, description=desc, category=cat, color=color)
        if self.on_project_created:
            self.on_project_created(p)
        self.dismiss()


class AddHabitDialog(ModalView):
    def __init__(self, on_habit_created=None, **kwargs):
        super().__init__(**kwargs)
        self.on_habit_created = on_habit_created
        self.size_hint = (0.9, None)
        self.height = 320
        self.auto_dismiss = True
        self.background_color = [0, 0, 0, 0.55]

        box = BoxLayout(orientation="vertical", spacing=12, padding=18)
        with box.canvas.before:
            self._b_col = Color(rgba=theme.bg_surface)
            self._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[14])
            self._l_col = Color(rgba=theme.border)
            self._line = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, 14), width=1.0)
        box.bind(pos=lambda *_: self._update(box), size=lambda *_: self._update(box))

        box.add_widget(Label(
            text="Nouvelle Habitude",
            font_size="17sp",
            bold=True,
            color=theme.text_primary,
            size_hint_y=None,
            height=26
        ))

        self.in_name = ShadcnInput(hint_text="Ex: Méditation (15 min)...", size_hint_y=None, height=42)
        box.add_widget(self.in_name)

        self.in_desc = ShadcnInput(hint_text="Raison ou notes...", size_hint_y=None, height=42)
        box.add_widget(self.in_desc)

        row = BoxLayout(spacing=10, size_hint_y=None, height=42)
        self.sp_freq = ShadcnSelect(
            text="Quotidien (7j/7)",
            values=("Quotidien (7j/7)", "5 jours / semaine", "3 jours / semaine"),
            size_hint_x=1.0
        )
        row.add_widget(self.sp_freq)
        box.add_widget(row)

        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=44)
        btn_cancel = AtelierGhostButton(text="Annuler", size_hint_x=0.45)
        btn_cancel.bind(on_release=lambda x: self.dismiss())
        btn_submit = AtelierButton(text="Ajouter l'habitude", size_hint_x=0.55)
        btn_submit.bind(on_release=self._submit)

        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_submit)
        box.add_widget(btn_box)

        self.add_widget(box)

    def _update(self, box):
        self._rect.pos = box.pos
        self._rect.size = box.size
        self._line.rounded_rectangle = (box.x, box.y, box.width, box.height, 14)

    def _submit(self, *args):
        name = self.in_name.text.strip()
        if not name:
            return
        desc = self.in_desc.text.strip()
        h = ds.habits.create_habit(name=name, description=desc)
        if self.on_habit_created:
            self.on_habit_created(h)
        self.dismiss()


class AddGoalDialog(ModalView):
    def __init__(self, on_goal_created=None, **kwargs):
        super().__init__(**kwargs)
        self.on_goal_created = on_goal_created
        self.size_hint = (0.9, None)
        self.height = 420
        self.auto_dismiss = True
        self.background_color = [0, 0, 0, 0.55]

        box = BoxLayout(orientation="vertical", spacing=12, padding=18)
        with box.canvas.before:
            self._b_col = Color(rgba=theme.bg_surface)
            self._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[14])
            self._l_col = Color(rgba=theme.border)
            self._line = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, 14), width=1.0)
        box.bind(pos=lambda *_: self._update(box), size=lambda *_: self._update(box))

        box.add_widget(Label(
            text="Nouvel Objectif Stratégique",
            font_size="17sp",
            bold=True,
            color=theme.text_primary,
            size_hint_y=None,
            height=26
        ))

        self.in_title = ShadcnInput(hint_text="Intitulé de l'objectif...", size_hint_y=None, height=42)
        box.add_widget(self.in_title)

        self.in_desc = ShadcnInput(hint_text="Description ou raison capitale...", size_hint_y=None, height=42)
        box.add_widget(self.in_desc)

        row = BoxLayout(spacing=10, size_hint_y=None, height=42)
        self.sp_category = ShadcnSelect(
            text="Dev & Pro",
            values=("Dev & Pro", "Académique", "Santé", "Personnel"),
            size_hint_x=0.5
        )
        self.in_date = ShadcnInput(
            hint_text="Échéance (ex: 2024-06-30)",
            text="2024-06-30",
            size_hint_x=0.5
        )
        row.add_widget(self.sp_category)
        row.add_widget(self.in_date)
        box.add_widget(row)

        self.in_milestones = ShadcnInput(
            hint_text="Jalons (séparés par virgule, ex: Prototype, Test, Release)",
            size_hint_y=None,
            height=42
        )
        box.add_widget(self.in_milestones)

        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=44)
        btn_cancel = AtelierGhostButton(text="Annuler", size_hint_x=0.45)
        btn_cancel.bind(on_release=lambda x: self.dismiss())
        btn_submit = AtelierButton(text="Créer l'objectif", size_hint_x=0.55)
        btn_submit.bind(on_release=self._submit)

        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_submit)
        box.add_widget(btn_box)

        self.add_widget(box)

    def _update(self, box):
        self._rect.pos = box.pos
        self._rect.size = box.size
        self._line.rounded_rectangle = (box.x, box.y, box.width, box.height, 14)

    def _submit(self, *args):
        title = self.in_title.text.strip()
        if not title:
            return
        desc = self.in_desc.text.strip()
        cat = self.sp_category.text
        target_date = self.in_date.text.strip()
        raw_ms = self.in_milestones.text.split(",")
        milestones = [{"title": m.strip(), "done": False} for m in raw_ms if m.strip()]
        if not milestones:
            milestones = [{"title": "Première étape", "done": False}]

        g = ds.goals.create_goal(
            title=title,
            description=desc,
            category=cat,
            target_date=target_date,
            milestones=milestones
        )
        if self.on_goal_created:
            self.on_goal_created(g)
        self.dismiss()


class AddCourseDialog(ModalView):
    def __init__(self, on_course_created=None, **kwargs):
        super().__init__(**kwargs)
        self.on_course_created = on_course_created
        self.size_hint = (0.9, None)
        self.height = 360
        self.auto_dismiss = True
        self.background_color = [0, 0, 0, 0.55]

        box = BoxLayout(orientation="vertical", spacing=12, padding=18)
        with box.canvas.before:
            self._b_col = Color(rgba=theme.bg_surface)
            self._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[14])
            self._l_col = Color(rgba=theme.border)
            self._line = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, 14), width=1.0)
        box.bind(pos=lambda *_: self._update(box), size=lambda *_: self._update(box))

        box.add_widget(Label(
            text="Nouvelle Matière Universitaire",
            font_size="17sp",
            bold=True,
            color=theme.text_primary,
            size_hint_y=None,
            height=26
        ))

        self.in_code = ShadcnInput(hint_text="Code UE (ex: UE 105)...", size_hint_y=None, height=42)
        box.add_widget(self.in_code)

        self.in_name = ShadcnInput(hint_text="Intitulé (ex: Sécurité & Cryptographie)...", size_hint_y=None, height=42)
        box.add_widget(self.in_name)

        row = BoxLayout(spacing=10, size_hint_y=None, height=42)
        self.in_prof = ShadcnInput(hint_text="Professeur (optionnel)", size_hint_x=0.6)
        self.in_target = ShadcnInput(hint_text="Note cible (ex: 16)", text="16", input_filter="float", size_hint_x=0.4)
        row.add_widget(self.in_prof)
        row.add_widget(self.in_target)
        box.add_widget(row)

        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=44)
        btn_cancel = AtelierGhostButton(text="Annuler", size_hint_x=0.45)
        btn_cancel.bind(on_release=lambda x: self.dismiss())
        btn_submit = AtelierButton(text="Ajouter le cours", size_hint_x=0.55)
        btn_submit.bind(on_release=self._submit)

        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_submit)
        box.add_widget(btn_box)

        self.add_widget(box)

    def _update(self, box):
        self._rect.pos = box.pos
        self._rect.size = box.size
        self._line.rounded_rectangle = (box.x, box.y, box.width, box.height, 14)

    def _submit(self, *args):
        code = self.in_code.text.strip()
        name = self.in_name.text.strip()
        if not code or not name:
            return
        prof = self.in_prof.text.strip()
        try:
            target = float(self.in_target.text.strip() or 16.0)
        except ValueError:
            target = 16.0

        c = ds.study.create_course(code=code, name=name, professor=prof, target_grade=target)
        if self.on_course_created:
            self.on_course_created(c)
        self.dismiss()


class AddExamDialog(ModalView):
    def __init__(self, courses, on_exam_created=None, **kwargs):
        super().__init__(**kwargs)
        self.courses = courses
        self.on_exam_created = on_exam_created
        self.size_hint = (0.9, None)
        self.height = 360
        self.auto_dismiss = True
        self.background_color = [0, 0, 0, 0.55]

        box = BoxLayout(orientation="vertical", spacing=12, padding=18)
        with box.canvas.before:
            self._b_col = Color(rgba=theme.bg_surface)
            self._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[14])
            self._l_col = Color(rgba=theme.border)
            self._line = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, 14), width=1.0)
        box.bind(pos=lambda *_: self._update(box), size=lambda *_: self._update(box))

        box.add_widget(Label(
            text="Ajouter un Examen",
            font_size="17sp",
            bold=True,
            color=theme.text_primary,
            size_hint_y=None,
            height=26
        ))

        self.course_map = {f"{c['code']} - {c['name']}": c["id"] for c in courses}
        c_values = list(self.course_map.keys()) if self.course_map else ["Aucun cours"]
        self.sp_course = ShadcnSelect(
            text=c_values[0],
            values=c_values,
            size_hint_y=None,
            height=42
        )
        box.add_widget(self.sp_course)

        self.in_title = ShadcnInput(hint_text="Titre (ex: Examen Final - Coeff 3)...", size_hint_y=None, height=42)
        box.add_widget(self.in_title)

        row = BoxLayout(spacing=10, size_hint_y=None, height=42)
        self.in_date = ShadcnInput(hint_text="Date (YYYY-MM-DD)", text="2024-01-20", size_hint_x=0.5)
        self.in_room = ShadcnInput(hint_text="Salle / Amphi", text="Amphi Turing", size_hint_x=0.5)
        row.add_widget(self.in_date)
        row.add_widget(self.in_room)
        box.add_widget(row)

        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=44)
        btn_cancel = AtelierGhostButton(text="Annuler", size_hint_x=0.45)
        btn_cancel.bind(on_release=lambda x: self.dismiss())
        btn_submit = AtelierButton(text="Enregistrer", size_hint_x=0.55)
        btn_submit.bind(on_release=self._submit)

        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_submit)
        box.add_widget(btn_box)

        self.add_widget(box)

    def _update(self, box):
        self._rect.pos = box.pos
        self._rect.size = box.size
        self._line.rounded_rectangle = (box.x, box.y, box.width, box.height, 14)

    def _submit(self, *args):
        title = self.in_title.text.strip()
        cid = self.course_map.get(self.sp_course.text)
        if not title or not cid:
            return
        d_str = self.in_date.text.strip()
        room = self.in_room.text.strip()
        ex = ds.study.create_exam(course_id=cid, title=title, date_str=d_str, room=room)
        if self.on_exam_created:
            self.on_exam_created(ex)
        self.dismiss()
