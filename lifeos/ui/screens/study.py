"""Study Hub Screen for LifeOS (Shadcn / React Native style)."""

from datetime import date, datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDIconButton
from lifeos.ui.theme import theme
from lifeos.ui.components.card import AtelierCard
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton, AtelierBadge
from lifeos.ui.components.progress import AtelierProgressBar
from lifeos.ui.components.navigation import AtelierTopBar, AtelierBottomNav
from lifeos.ui.components.dialogs import AddCourseDialog, AddExamDialog
from lifeos.services.data_service import ds
from lifeos.core.events import bus

class StudyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._bg_col = Color(rgba=theme.bg_canvas)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar
        self.top_bar = AtelierTopBar(
            title="Study Hub",
            subtitle="SUIVI ACADÉMIQUE & RÉVISIONS",
            right_icon="plus-circle-outline",
            right_action=self._open_add_menu
        )
        self.root_box.add_widget(self.top_bar)

        # Scrollview
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(
            orientation="vertical",
            spacing=14,
            padding=[16, 14, 16, 20],
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)
        self.root_box.add_widget(self.scroll)

        # Bottom Nav
        self.bottom_nav = AtelierBottomNav(
            current_tab="modules",
            nav_callback=self._handle_navigation
        )
        self.root_box.add_widget(self.bottom_nav)

        self.add_widget(self.root_box)

        bus.subscribe("study_updated", lambda *_: self.refresh_data())
        bus.subscribe("focus_updated", lambda *_: self.refresh_data())
        bus.subscribe("theme_changed", self._on_theme)

        self.refresh_data()

    def _on_theme(self, *args, **kwargs):
        self._bg_col.rgba = theme.bg_canvas
        self.refresh_data()

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_pre_enter(self):
        self.bottom_nav.set_tab("modules")
        self.refresh_data()

    def _handle_navigation(self, route):
        if self.manager and route != "study":
            self.manager.current = route

    def _open_add_menu(self):
        courses = ds.study.list_courses()
        dialog = AddExamDialog(courses=courses, on_exam_created=lambda _: self.refresh_data())
        dialog.open()

    def _open_add_course(self):
        dialog = AddCourseDialog(on_course_created=lambda _: self.refresh_data())
        dialog.open()

    def refresh_data(self):
        self.content.clear_widgets()

        courses = ds.study.list_courses()
        exams = ds.study.list_upcoming_exams()

        # 1. Summary Metrics Bento
        stats_card = AtelierCard(
            orientation="vertical",
            spacing=10,
            padding=[16, 14, 16, 14],
            size_hint_y=None,
            height=90
        )
        lbl_head = Label(
            text="SEMESTRE 1  ·  CYCLE MASTER & LICENCE",
            font_size="10sp",
            bold=True,
            color=theme.text_secondary,
            halign="left",
            size_hint_y=None,
            height=16
        )
        lbl_head.bind(size=lbl_head.setter("text_size"))
        stats_card.add_widget(lbl_head)

        metrics_grid = GridLayout(cols=3, spacing=10, size_hint_y=None, height=44)
        m1 = BoxLayout(orientation="vertical")
        m1.add_widget(Label(text=f"{len(courses)}", font_size="18sp", bold=True, color=theme.text_primary))
        m1.add_widget(Label(text="Matières", font_size="10sp", color=theme.text_secondary))

        m2 = BoxLayout(orientation="vertical")
        m2.add_widget(Label(text=f"{len(exams)}", font_size="18sp", bold=True, color=theme.primary))
        m2.add_widget(Label(text="Examens", font_size="10sp", color=theme.text_secondary))

        avg_target = sum(c.get("target_grade", 14.0) for c in courses) / max(len(courses), 1)
        m3 = BoxLayout(orientation="vertical")
        m3.add_widget(Label(text=f"{avg_target:.1f}/20", font_size="18sp", bold=True, color=theme.text_primary))
        m3.add_widget(Label(text="Moy. Cible", font_size="10sp", color=theme.text_secondary))

        metrics_grid.add_widget(m1)
        metrics_grid.add_widget(m2)
        metrics_grid.add_widget(m3)
        stats_card.add_widget(metrics_grid)
        self.content.add_widget(stats_card)

        # 2. Interactive Study Session Action Card
        session_card = AtelierCard(
            orientation="horizontal",
            spacing=12,
            padding=[16, 12, 16, 12],
            size_hint_y=None,
            height=66
        )
        sess_text = BoxLayout(orientation="vertical", spacing=2)
        sess_title = Label(
            text="Lancer une Session Focus d'Étude",
            font_size="14sp",
            bold=True,
            color=theme.text_primary,
            halign="left"
        )
        sess_title.bind(size=sess_title.setter("text_size"))
        sess_sub = Label(
            text="Pomodoro 50m focus / 10m pause · Mémorisation",
            font_size="11sp",
            color=theme.text_secondary,
            halign="left"
        )
        sess_sub.bind(size=sess_sub.setter("text_size"))
        sess_text.add_widget(sess_title)
        sess_text.add_widget(sess_sub)
        session_card.add_widget(sess_text)

        btn_go = AtelierButton(
            text="Démarrer",
            font_size="12sp",
            size_hint=(None, None),
            size=(86, 36),
            pos_hint={"center_y": 0.5}
        )
        btn_go.bind(on_release=lambda _: self._start_focus_session())
        session_card.add_widget(btn_go)
        self.content.add_widget(session_card)

        # 3. Prochains Examens & Échéances
        sec_ex = BoxLayout(size_hint_y=None, height=28)
        lbl_ex = Label(
            text="PROCHAINS EXAMENS & ÉCHÉANCES",
            font_size="11sp",
            bold=True,
            color=theme.text_secondary,
            halign="left"
        )
        lbl_ex.bind(size=lbl_ex.setter("text_size"))
        sec_ex.add_widget(lbl_ex)

        btn_add_ex = AtelierGhostButton(
            text="+ Examen",
            font_size="11sp",
            size_hint=(None, 1),
            width=76
        )
        btn_add_ex.bind(on_release=lambda _: self._open_add_menu())
        sec_ex.add_widget(btn_add_ex)
        self.content.add_widget(sec_ex)

        if not exams:
            no_ex = Label(
                text="Aucun examen planifié.",
                font_size="12sp",
                color=theme.text_muted,
                size_hint_y=None,
                height=30
            )
            self.content.add_widget(no_ex)
        else:
            today = date.today()
            for ex in exams:
                card = AtelierCard(
                    orientation="vertical",
                    spacing=6,
                    padding=[14, 10, 14, 10],
                    size_hint_y=None,
                    height=80
                )
                top_row = BoxLayout(size_hint_y=None, height=22)
                lbl_cname = Label(
                    text=f"{ex.get('course_code', 'UE')} · {ex.get('course_name', '')}",
                    font_size="12sp",
                    bold=True,
                    color=theme.primary,
                    halign="left"
                )
                lbl_cname.bind(size=lbl_cname.setter("text_size"))

                try:
                    ex_d = datetime.strptime(ex["date"], "%Y-%m-%d").date()
                    diff = (ex_d - today).days
                    d_text = f"J-{diff}" if diff > 0 else ("Aujourd'hui" if diff == 0 else f"+{abs(diff)}j")
                except Exception:
                    d_text = ex["date"]

                badge = AtelierBadge(text=d_text)
                top_row.add_widget(lbl_cname)
                top_row.add_widget(badge)
                card.add_widget(top_row)

                lbl_title = Label(
                    text=ex["title"],
                    font_size="13sp",
                    bold=True,
                    color=theme.text_primary,
                    halign="left"
                )
                lbl_title.bind(size=lbl_title.setter("text_size"))
                card.add_widget(lbl_title)

                sub_row = BoxLayout(size_hint_y=None, height=18)
                lbl_info = Label(
                    text=f"Date: {ex['date']}  ·  Salle: {ex.get('room', 'Amphi')}  ·  Coeff {ex.get('weight', 1.0)}",
                    font_size="11sp",
                    color=theme.text_secondary,
                    halign="left"
                )
                lbl_info.bind(size=lbl_info.setter("text_size"))
                sub_row.add_widget(lbl_info)
                card.add_widget(sub_row)

                self.content.add_widget(card)

        # 4. Matières Universitaires
        sec_courses = BoxLayout(size_hint_y=None, height=28)
        lbl_cs = Label(
            text="MATIÈRES UNIVERSITAIRES",
            font_size="11sp",
            bold=True,
            color=theme.text_secondary,
            halign="left"
        )
        lbl_cs.bind(size=lbl_cs.setter("text_size"))
        sec_courses.add_widget(lbl_cs)

        btn_add_c = AtelierGhostButton(
            text="+ Matière",
            font_size="11sp",
            size_hint=(None, 1),
            width=76
        )
        btn_add_c.bind(on_release=lambda _: self._open_add_course())
        sec_courses.add_widget(btn_add_c)
        self.content.add_widget(sec_courses)

        for c in courses:
            c_card = AtelierCard(
                orientation="vertical",
                spacing=8,
                padding=[14, 12, 14, 12],
                size_hint_y=None,
                height=96
            )

            row_top = BoxLayout(size_hint_y=None, height=22)
            lbl_code = Label(
                text=f"{c['code']} · {c.get('semester', 'S1')}",
                font_size="11sp",
                bold=True,
                color=theme.primary,
                halign="left"
            )
            lbl_code.bind(size=lbl_code.setter("text_size"))

            lbl_grade = Label(
                text=f"Cible: {c.get('target_grade', 16)}/20",
                font_size="11sp",
                bold=True,
                color=theme.text_secondary,
                halign="right"
            )
            lbl_grade.bind(size=lbl_grade.setter("text_size"))

            row_top.add_widget(lbl_code)
            row_top.add_widget(lbl_grade)
            c_card.add_widget(row_top)

            lbl_name = Label(
                text=c["name"],
                font_size="14sp",
                bold=True,
                color=theme.text_primary,
                halign="left"
            )
            lbl_name.bind(size=lbl_name.setter("text_size"))
            c_card.add_widget(lbl_name)

            curr = c.get("current_grade", 14.0)
            target = max(c.get("target_grade", 16.0), 1.0)
            pct = min(100, int((curr / target) * 100))

            prog_row = BoxLayout(spacing=10, size_hint_y=None, height=16)
            prog_bar = AtelierProgressBar(value=pct, size_hint_x=0.8, pos_hint={"center_y": 0.5})
            lbl_pct = Label(text=f"{pct}%", font_size="11sp", bold=True, color=theme.text_secondary, size_hint_x=0.2)
            prog_row.add_widget(prog_bar)
            prog_row.add_widget(lbl_pct)
            c_card.add_widget(prog_row)

            self.content.add_widget(c_card)

    def _start_focus_session(self):
        if self.manager:
            self.manager.current = "focus"
