"""Dashboard Home Screen (Bento Sanctuary) for LifeOS."""

from datetime import date
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDIconButton
from lifeos.ui.theme import (
    BG_CANVAS, BG_CARD, BG_CARD_HOVER, BORDER_COLOR,
    GOLD, CHAMPAGNE, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, SUCCESS
)
from lifeos.ui.components.card import AtelierCard
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton, AtelierBadge
from lifeos.ui.components.checkbox import AtelierCheckbox
from lifeos.ui.components.progress import AtelierCircularProgress
from lifeos.ui.components.navigation import AtelierTopBar, AtelierBottomNav
from lifeos.ui.components.dialogs import AddTaskDialog
from lifeos.services.data_service import ds
from lifeos.core.events import bus

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(rgba=BG_CANVAS)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Root vertical layout
        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar
        self.top_bar = AtelierTopBar(
            title="LifeOS",
            subtitle="Sanctuaire Privé",
            right_icon="plus-circle-outline",
            right_action=self._open_add_dialog
        )
        self.root_box.add_widget(self.top_bar)

        # Scrollable content
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(
            orientation="vertical",
            spacing=16,
            padding=[16, 16, 16, 20],
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)
        self.root_box.add_widget(self.scroll)

        # Bottom Nav
        self.bottom_nav = AtelierBottomNav(
            current_tab="dashboard",
            nav_callback=self._handle_navigation
        )
        self.root_box.add_widget(self.bottom_nav)

        self.add_widget(self.root_box)

        # Subscribe to reactive updates
        bus.subscribe("tasks_updated", lambda *_: self.refresh_data())
        bus.subscribe("habits_updated", lambda *_: self.refresh_data())
        bus.subscribe("focus_updated", lambda *_: self.refresh_data())

        self.refresh_data()

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_pre_enter(self):
        self.bottom_nav.set_tab("dashboard")
        self.refresh_data()

    def _open_add_dialog(self):
        dialog = AddTaskDialog(on_task_created=lambda _: self.refresh_data())
        dialog.open()

    def _handle_navigation(self, route):
        if self.manager and route != "dashboard":
            self.manager.current = route

    def refresh_data(self):
        self.content.clear_widgets()

        user_name = ds.settings.get_setting("user_name", "Thomas V.")
        summary = ds.stats.get_dashboard_summary()
        today_str = date.today().strftime("%A %d %B").capitalize()

        # 1. Header Greeting Section
        greeting_card = AtelierCard(
            orientation="vertical",
            spacing=4,
            padding=[16, 14, 16, 14],
            size_hint_y=None,
            height=86
        )
        lbl_hello = Label(
            text=f"Bonjour, {user_name} 👋",
            font_size="20sp",
            bold=True,
            color=TEXT_PRIMARY,
            halign="left",
            size_hint_y=None,
            height=28
        )
        lbl_hello.bind(size=lbl_hello.setter("text_size"))

        lbl_date = Label(
            text=f"{today_str} · Votre espace est aligné et prêt.",
            font_size="12sp",
            color=TEXT_SECONDARY,
            halign="left",
            size_hint_y=None,
            height=22
        )
        lbl_date.bind(size=lbl_date.setter("text_size"))

        greeting_card.add_widget(lbl_hello)
        greeting_card.add_widget(lbl_date)
        self.content.add_widget(greeting_card)

        # 2. Bento Masterpiece Summary Card
        bento = AtelierCard(
            orientation="horizontal",
            spacing=16,
            padding=[16, 16, 16, 16],
            size_hint_y=None,
            height=130
        )
        # Circular Progress
        circle = AtelierCircularProgress(
            value=summary["daily_progress_pct"],
            size_hint=(None, 1),
            width=90
        )
        bento.add_widget(circle)

        # Stats Column
        stats_col = BoxLayout(orientation="vertical", spacing=6)
        lbl_bento_title = Label(
            text="SYNTHÈSE DU JOUR",
            font_size="10sp",
            bold=True,
            color=GOLD,
            halign="left",
            size_hint_y=None,
            height=16
        )
        lbl_bento_title.bind(size=lbl_bento_title.setter("text_size"))

        row1 = BoxLayout(orientation="horizontal")
        lbl_focus = Label(
            text=f"Focus : [b]{summary['focus_formatted']}[/b]",
            markup=True,
            font_size="13sp",
            color=TEXT_PRIMARY,
            halign="left"
        )
        lbl_focus.bind(size=lbl_focus.setter("text_size"))
        lbl_streak = Label(
            text=f"Série : [b]{summary['current_streak_days']}j 🔥[/b]",
            markup=True,
            font_size="13sp",
            color=CHAMPAGNE,
            halign="right"
        )
        lbl_streak.bind(size=lbl_streak.setter("text_size"))
        row1.add_widget(lbl_focus)
        row1.add_widget(lbl_streak)

        row2 = BoxLayout(orientation="horizontal")
        lbl_tasks_count = Label(
            text=f"Tâches : [b]{summary['completed_tasks']} / {summary['total_tasks']}[/b]",
            markup=True,
            font_size="13sp",
            color=TEXT_PRIMARY,
            halign="left"
        )
        lbl_tasks_count.bind(size=lbl_tasks_count.setter("text_size"))
        lbl_habits_count = Label(
            text=f"Habitudes : [b]{summary['habits_done_today']} / {summary['total_habits']}[/b]",
            markup=True,
            font_size="13sp",
            color=TEXT_SECONDARY,
            halign="right"
        )
        lbl_habits_count.bind(size=lbl_habits_count.setter("text_size"))
        row2.add_widget(lbl_tasks_count)
        row2.add_widget(lbl_habits_count)

        stats_col.add_widget(lbl_bento_title)
        stats_col.add_widget(row1)
        stats_col.add_widget(row2)
        bento.add_widget(stats_col)
        self.content.add_widget(bento)

        # 3. Section: Priorités du Jour (Tâches Clés)
        sec_header = BoxLayout(size_hint_y=None, height=30)
        lbl_sec1 = Label(
            text="PRIORITÉS DU JOUR",
            font_size="12sp",
            bold=True,
            color=GOLD,
            halign="left"
        )
        lbl_sec1.bind(size=lbl_sec1.setter("text_size"))
        btn_view_tasks = AtelierGhostButton(
            text="Voir tout →",
            font_size="11sp",
            size_hint=(None, None),
            size=(80, 26)
        )
        btn_view_tasks.bind(on_release=lambda _: self._nav_to("tasks"))
        sec_header.add_widget(lbl_sec1)
        sec_header.add_widget(btn_view_tasks)
        self.content.add_widget(sec_header)

        # Tasks list items
        tasks = ds.tasks.list_tasks(filter_status="today")
        if not tasks:
            tasks = ds.tasks.list_tasks()[:4]

        for t in tasks[:4]:
            t_card = AtelierCard(
                orientation="horizontal",
                spacing=12,
                padding=[12, 10, 12, 10],
                size_hint_y=None,
                height=68
            )
            # Checkbox
            cb = AtelierCheckbox(active=bool(t["is_completed"]))
            cb.bind(on_release=lambda inst, tid=t["id"]: ds.tasks.toggle_task(tid))
            t_card.add_widget(cb)

            # Details
            col = BoxLayout(orientation="vertical", spacing=2)
            title_text = f"[s]{t['title']}[/s]" if t["is_completed"] else t["title"]
            lbl_t_title = Label(
                text=title_text,
                markup=True,
                font_size="13sp",
                bold=True,
                color=TEXT_MUTED if t["is_completed"] else TEXT_PRIMARY,
                halign="left",
                size_hint_y=None,
                height=22
            )
            lbl_t_title.bind(size=lbl_t_title.setter("text_size"))

            # Meta row
            meta_box = BoxLayout(spacing=8, size_hint_y=None, height=18)
            proj_name = t.get("project_title") or "Général"
            lbl_proj = Label(
                text=f"📁 {proj_name}",
                font_size="10sp",
                color=CHAMPAGNE,
                halign="left"
            )
            lbl_proj.bind(size=lbl_proj.setter("text_size"))
            lbl_time = Label(
                text=f"⏱ {t.get('estimated_minutes', 30)}m",
                font_size="10sp",
                color=TEXT_SECONDARY,
                halign="left"
            )
            lbl_time.bind(size=lbl_time.setter("text_size"))
            meta_box.add_widget(lbl_proj)
            meta_box.add_widget(lbl_time)

            col.add_widget(lbl_t_title)
            col.add_widget(meta_box)
            t_card.add_widget(col)

            # Priority Badge
            badge = AtelierBadge(text=t.get("priority", "MEDIUM"))
            t_card.add_widget(badge)

            # Tap card to view details
            t_card.bind(on_touch_down=lambda inst, touch, tid=t["id"]: self._on_task_card_click(inst, touch, tid))

            self.content.add_widget(t_card)

        # 4. Section: Rituels & Habitudes du Jour
        sec_header2 = BoxLayout(size_hint_y=None, height=30)
        lbl_sec2 = Label(
            text="HABITUDES DU JOUR",
            font_size="12sp",
            bold=True,
            color=GOLD,
            halign="left"
        )
        lbl_sec2.bind(size=lbl_sec2.setter("text_size"))
        btn_view_habits = AtelierGhostButton(
            text="Séries →",
            font_size="11sp",
            size_hint=(None, None),
            size=(70, 26)
        )
        btn_view_habits.bind(on_release=lambda _: self._nav_to("streaks"))
        sec_header2.add_widget(lbl_sec2)
        sec_header2.add_widget(btn_view_habits)
        self.content.add_widget(sec_header2)

        habits = ds.habits.list_habits_with_logs()
        for h in habits[:3]:
            h_card = AtelierCard(
                orientation="horizontal",
                spacing=12,
                padding=[12, 10, 12, 10],
                size_hint_y=None,
                height=54
            )
            h_cb = AtelierCheckbox(active=bool(h.get("today_done")))
            h_cb.bind(on_release=lambda inst, hid=h["id"]: ds.habits.toggle_habit_for_date(hid))
            h_card.add_widget(h_cb)

            lbl_h_name = Label(
                text=h["name"],
                font_size="13sp",
                bold=True,
                color=TEXT_PRIMARY,
                halign="left"
            )
            lbl_h_name.bind(size=lbl_h_name.setter("text_size"))
            h_card.add_widget(lbl_h_name)

            lbl_h_streak = Label(
                text=f"{h.get('streak_current', 0)}j 🔥",
                font_size="12sp",
                bold=True,
                color=GOLD,
                halign="right",
                size_hint_x=0.25
            )
            lbl_h_streak.bind(size=lbl_h_streak.setter("text_size"))
            h_card.add_widget(lbl_h_streak)

            self.content.add_widget(h_card)

        # 5. Quick Actions Bento Row (Focus Pomodoro & Study Hub)
        qa_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=74)
        btn_focus = AtelierButton(
            text="⏱ Focus Pomodoro",
            font_size="12sp",
            bg_color=GOLD
        )
        btn_focus.bind(on_release=lambda _: self._nav_to("focus"))

        btn_study = AtelierGhostButton(
            text="🎓 Study Hub",
            font_size="12sp"
        )
        btn_study.bind(on_release=lambda _: self._nav_to("study"))

        qa_grid.add_widget(btn_focus)
        qa_grid.add_widget(btn_study)
        self.content.add_widget(qa_grid)

    def _on_task_card_click(self, instance, touch, task_id):
        if instance.collide_point(*touch.pos):
            # If not clicking checkbox directly
            if touch.x > instance.x + 40:
                self._open_task_details(task_id)

    def _open_task_details(self, task_id):
        if self.manager and "task_details" in self.manager.screen_names:
            detail_screen = self.manager.get_screen("task_details")
            detail_screen.load_task(task_id)
            self.manager.current = "task_details"

    def _nav_to(self, route):
        if self.manager:
            self.manager.current = route
