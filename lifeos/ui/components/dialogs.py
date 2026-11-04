"""Dialogs and Modals for creating entities in LifeOS."""

from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle, Line
from lifeos.ui.theme import (
    BG_CARD, BORDER_COLOR, GOLD, TEXT_PRIMARY,
    TEXT_SECONDARY, BG_CARD_HOVER, CHAMPAGNE
)
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton
from lifeos.services.data_service import ds

class StyledInput(TextInput):
    def __init__(self, **kwargs):
        kwargs.setdefault("background_color", BG_CARD_HOVER)
        kwargs.setdefault("foreground_color", TEXT_PRIMARY)
        kwargs.setdefault("cursor_color", GOLD)
        kwargs.setdefault("multiline", False)
        kwargs.setdefault("padding", [12, 10, 12, 10])
        super().__init__(**kwargs)

class AddTaskDialog(ModalView):
    def __init__(self, on_task_created=None, initial_project_id=None, **kwargs):
        super().__init__(**kwargs)
        self.on_task_created = on_task_created
        self.size_hint = (0.9, None)
        self.height = 430
        self.auto_dismiss = True
        self.background_color = [0, 0, 0, 0.7]

        # Container
        box = BoxLayout(orientation="vertical", spacing=12, padding=16)
        with box.canvas.before:
            Color(rgba=BG_CARD)
            self._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[16])
            Color(rgba=BORDER_COLOR)
            self._line = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, 16), width=1.2)
        box.bind(pos=lambda *_: self._update(box), size=lambda *_: self._update(box))

        # Title
        box.add_widget(Label(
            text="Nouvelle Tâche",
            font_size="18sp",
            bold=True,
            color=TEXT_PRIMARY,
            size_hint_y=None,
            height=28
        ))

        # Input Title
        self.in_title = StyledInput(hint_text="Intitulé de la tâche...", size_hint_y=None, height=42)
        box.add_widget(self.in_title)

        # Input Description
        self.in_desc = StyledInput(hint_text="Description ou notes rapides...", size_hint_y=None, height=42)
        box.add_widget(self.in_desc)

        # Priority & Time Row
        row = BoxLayout(spacing=10, size_hint_y=None, height=42)
        self.sp_priority = Spinner(
            text="URGENT",
            values=("URGENT", "HIGH", "MEDIUM", "LOW"),
            background_color=BG_CARD_HOVER,
            color=GOLD,
            size_hint_x=0.5
        )
        self.in_time = StyledInput(
            hint_text="Durée (min, ex: 45)",
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

        self.sp_project = Spinner(
            text=default_proj_text,
            values=proj_values,
            background_color=BG_CARD_HOVER,
            color=TEXT_PRIMARY,
            size_hint_y=None,
            height=42
        )
        box.add_widget(self.sp_project)

        # Action Buttons
        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=44)
        btn_cancel = AtelierGhostButton(text="Annuler")
        btn_cancel.bind(on_release=lambda x: self.dismiss())
        btn_submit = AtelierButton(text="Créer la tâche")
        btn_submit.bind(on_release=self._submit)

        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_submit)
        box.add_widget(btn_box)

        self.add_widget(box)

    def _update(self, box):
        self._rect.pos = box.pos
        self._rect.size = box.size
        self._line.rounded_rectangle = (box.x, box.y, box.width, box.height, 16)

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
            project_id=proj_id,
            priority=priority,
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
        self.height = 360
        self.auto_dismiss = True

        box = BoxLayout(orientation="vertical", spacing=12, padding=16)
        with box.canvas.before:
            Color(rgba=BG_CARD)
            self._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[16])
            Color(rgba=BORDER_COLOR)
            self._line = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, 16), width=1.2)
        box.bind(pos=lambda *_: self._update(box), size=lambda *_: self._update(box))

        box.add_widget(Label(
            text="Nouveau Projet",
            font_size="18sp",
            bold=True,
            color=TEXT_PRIMARY,
            size_hint_y=None,
            height=28
        ))

        self.in_title = StyledInput(hint_text="Titre du projet...", size_hint_y=None, height=42)
        box.add_widget(self.in_title)

        self.in_desc = StyledInput(hint_text="Objectif ou description...", size_hint_y=None, height=42)
        box.add_widget(self.in_desc)

        row = BoxLayout(spacing=10, size_hint_y=None, height=42)
        self.sp_category = Spinner(
            text="Dev",
            values=("Dev", "Académique", "Santé", "Personnel"),
            background_color=BG_CARD_HOVER,
            color=GOLD,
            size_hint_x=0.5
        )
        self.sp_color = Spinner(
            text="Or",
            values=("Or", "Champagne", "Vert", "Ambre"),
            background_color=BG_CARD_HOVER,
            color=TEXT_PRIMARY,
            size_hint_x=0.5
        )
        row.add_widget(self.sp_category)
        row.add_widget(self.sp_color)
        box.add_widget(row)

        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=44)
        btn_cancel = AtelierGhostButton(text="Annuler")
        btn_cancel.bind(on_release=lambda x: self.dismiss())
        btn_submit = AtelierButton(text="Créer le projet")
        btn_submit.bind(on_release=self._submit)

        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_submit)
        box.add_widget(btn_box)

        self.add_widget(box)

    def _update(self, box):
        self._rect.pos = box.pos
        self._rect.size = box.size
        self._line.rounded_rectangle = (box.x, box.y, box.width, box.height, 16)

    def _submit(self, *args):
        title = self.in_title.text.strip()
        if not title:
            return
        desc = self.in_desc.text.strip()
        cat = self.sp_category.text
        color_map = {"Or": "#C6A76B", "Champagne": "#DFBA7B", "Vert": "#7DD9A3", "Ambre": "#E5A93B"}
        color = color_map.get(self.sp_color.text, "#C6A76B")

        p = ds.projects.create_project(title=title, description=desc, category=cat, color=color)
        if self.on_project_created:
            self.on_project_created(p)
        self.dismiss()


class AddHabitDialog(ModalView):
    def __init__(self, on_habit_created=None, **kwargs):
        super().__init__(**kwargs)
        self.on_habit_created = on_habit_created
        self.size_hint = (0.9, None)
        self.height = 340
        self.auto_dismiss = True

        box = BoxLayout(orientation="vertical", spacing=12, padding=16)
        with box.canvas.before:
            Color(rgba=BG_CARD)
            self._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[16])
            Color(rgba=BORDER_COLOR)
            self._line = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, 16), width=1.2)
        box.bind(pos=lambda *_: self._update(box), size=lambda *_: self._update(box))

        box.add_widget(Label(
            text="Nouvelle Habitude",
            font_size="18sp",
            bold=True,
            color=TEXT_PRIMARY,
            size_hint_y=None,
            height=28
        ))

        self.in_name = StyledInput(hint_text="Ex: Méditation (15 min)...", size_hint_y=None, height=42)
        box.add_widget(self.in_name)

        self.in_desc = StyledInput(hint_text="Pourquoi ce rituel est capital...", size_hint_y=None, height=42)
        box.add_widget(self.in_desc)

        row = BoxLayout(spacing=10, size_hint_y=None, height=42)
        self.sp_freq = Spinner(
            text="Quotidien (7j/7)",
            values=("Quotidien (7j/7)", "5 jours / semaine", "3 jours / semaine"),
            background_color=BG_CARD_HOVER,
            color=GOLD,
            size_hint_x=1.0
        )
        row.add_widget(self.sp_freq)
        box.add_widget(row)

        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=44)
        btn_cancel = AtelierGhostButton(text="Annuler")
        btn_cancel.bind(on_release=lambda x: self.dismiss())
        btn_submit = AtelierButton(text="Ajouter l'habitude")
        btn_submit.bind(on_release=self._submit)

        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_submit)
        box.add_widget(btn_box)

        self.add_widget(box)

    def _update(self, box):
        self._rect.pos = box.pos
        self._rect.size = box.size
        self._line.rounded_rectangle = (box.x, box.y, box.width, box.height, 16)

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

        box = BoxLayout(orientation="vertical", spacing=10, padding=16)
        with box.canvas.before:
            Color(rgba=BG_CARD)
            self._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[16])
            Color(rgba=BORDER_COLOR)
            self._line = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, 16), width=1.2)
        box.bind(pos=lambda *_: self._update(box), size=lambda *_: self._update(box))

        box.add_widget(Label(
            text="Nouvel Objectif Stratégique",
            font_size="17sp",
            bold=True,
            color=TEXT_PRIMARY,
            size_hint_y=None,
            height=28
        ))

        self.in_title = StyledInput(hint_text="Intitulé de l'objectif...", size_hint_y=None, height=42)
        box.add_widget(self.in_title)

        self.in_desc = StyledInput(hint_text="Description ou raison capitale...", size_hint_y=None, height=42)
        box.add_widget(self.in_desc)

        row = BoxLayout(spacing=10, size_hint_y=None, height=42)
        self.sp_category = Spinner(
            text="Dev & Pro",
            values=("Dev & Pro", "Académique", "Santé", "Personnel"),
            background_color=BG_CARD_HOVER,
            color=GOLD,
            size_hint_x=0.5
        )
        self.in_date = StyledInput(
            hint_text="Échéance (ex: 2024-06-30)",
            text="2024-06-30",
            size_hint_x=0.5
        )
        row.add_widget(self.sp_category)
        row.add_widget(self.in_date)
        box.add_widget(row)

        self.in_milestones = StyledInput(
            hint_text="Jalons séparés par virgule (ex: Prototype, Test, Release)",
            size_hint_y=None,
            height=42
        )
        box.add_widget(self.in_milestones)

        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=44)
        btn_cancel = AtelierGhostButton(text="Annuler")
        btn_cancel.bind(on_release=lambda x: self.dismiss())
        btn_submit = AtelierButton(text="Créer l'objectif")
        btn_submit.bind(on_release=self._submit)

        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_submit)
        box.add_widget(btn_box)

        self.add_widget(box)

    def _update(self, box):
        self._rect.pos = box.pos
        self._rect.size = box.size
        self._line.rounded_rectangle = (box.x, box.y, box.width, box.height, 16)

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

        box = BoxLayout(orientation="vertical", spacing=10, padding=16)
        with box.canvas.before:
            Color(rgba=BG_CARD)
            self._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[16])
            Color(rgba=BORDER_COLOR)
            self._line = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, 16), width=1.2)
        box.bind(pos=lambda *_: self._update(box), size=lambda *_: self._update(box))

        box.add_widget(Label(
            text="Nouvelle Matière Universitaire",
            font_size="17sp",
            bold=True,
            color=TEXT_PRIMARY,
            size_hint_y=None,
            height=28
        ))

        self.in_code = StyledInput(hint_text="Code UE (ex: UE 105)...", size_hint_y=None, height=42)
        box.add_widget(self.in_code)

        self.in_name = StyledInput(hint_text="Intitulé (ex: Sécurité & Cryptographie)...", size_hint_y=None, height=42)
        box.add_widget(self.in_name)

        row = BoxLayout(spacing=10, size_hint_y=None, height=42)
        self.in_prof = StyledInput(hint_text="Professeur (optionnel)", size_hint_x=0.6)
        self.in_target = StyledInput(hint_text="Note cible (ex: 16)", text="16", input_filter="float", size_hint_x=0.4)
        row.add_widget(self.in_prof)
        row.add_widget(self.in_target)
        box.add_widget(row)

        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=44)
        btn_cancel = AtelierGhostButton(text="Annuler")
        btn_cancel.bind(on_release=lambda x: self.dismiss())
        btn_submit = AtelierButton(text="Ajouter le cours")
        btn_submit.bind(on_release=self._submit)

        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_submit)
        box.add_widget(btn_box)

        self.add_widget(box)

    def _update(self, box):
        self._rect.pos = box.pos
        self._rect.size = box.size
        self._line.rounded_rectangle = (box.x, box.y, box.width, box.height, 16)

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

        box = BoxLayout(orientation="vertical", spacing=10, padding=16)
        with box.canvas.before:
            Color(rgba=BG_CARD)
            self._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[16])
            Color(rgba=BORDER_COLOR)
            self._line = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, 16), width=1.2)
        box.bind(pos=lambda *_: self._update(box), size=lambda *_: self._update(box))

        box.add_widget(Label(
            text="Ajouter un Examen / Partiel",
            font_size="17sp",
            bold=True,
            color=TEXT_PRIMARY,
            size_hint_y=None,
            height=28
        ))

        self.course_map = {f"{c['code']} - {c['name']}": c["id"] for c in courses}
        c_values = list(self.course_map.keys()) if self.course_map else ["Aucun cours"]
        self.sp_course = Spinner(
            text=c_values[0],
            values=c_values,
            background_color=BG_CARD_HOVER,
            color=GOLD,
            size_hint_y=None,
            height=42
        )
        box.add_widget(self.sp_course)

        self.in_title = StyledInput(hint_text="Titre (ex: Examen Final - Coeff 3)...", size_hint_y=None, height=42)
        box.add_widget(self.in_title)

        row = BoxLayout(spacing=10, size_hint_y=None, height=42)
        self.in_date = StyledInput(hint_text="Date (YYYY-MM-DD)", text="2024-01-20", size_hint_x=0.5)
        self.in_room = StyledInput(hint_text="Salle / Amphi", text="Amphi Turing", size_hint_x=0.5)
        row.add_widget(self.in_date)
        row.add_widget(self.in_room)
        box.add_widget(row)

        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=44)
        btn_cancel = AtelierGhostButton(text="Annuler")
        btn_cancel.bind(on_release=lambda x: self.dismiss())
        btn_submit = AtelierButton(text="Enregistrer l'examen")
        btn_submit.bind(on_release=self._submit)

        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_submit)
        box.add_widget(btn_box)

        self.add_widget(box)

    def _update(self, box):
        self._rect.pos = box.pos
        self._rect.size = box.size
        self._line.rounded_rectangle = (box.x, box.y, box.width, box.height, 16)

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
