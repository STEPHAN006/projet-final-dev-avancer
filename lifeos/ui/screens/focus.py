"""Focus & Pomodoro Screen for LifeOS (Deep Work Sanctuary)."""

from datetime import date
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivymd.uix.button import MDIconButton
from lifeos.ui.theme import (
    BG_CANVAS, BG_CARD, BG_CARD_HOVER, BORDER_COLOR,
    GOLD, CHAMPAGNE, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, SUCCESS, WARNING, ERROR
)
from lifeos.ui.components.card import AtelierCard
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton, AtelierBadge
from lifeos.ui.components.progress import AtelierProgressBar
from lifeos.ui.components.navigation import AtelierTopBar, AtelierBottomNav
from lifeos.services.data_service import ds
from lifeos.core.events import bus

class FocusScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Timer states
        self.mode = "pomodoro" # pomodoro (25m), short_break (5m), long_break (15m), stopwatch
        self.preset_seconds = 25 * 60
        self.remaining_seconds = 25 * 60
        self.is_running = False
        self.current_cycle = 1
        self.max_cycles = 4
        self.timer_event = None

        with self.canvas.before:
            Color(rgba=BG_CANVAS)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar
        self.top_bar = AtelierTopBar(
            title="Focus Pomodoro",
            subtitle="SANCTUAIRE DE CONCENTRATION"
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

        self._build_ui()
        bus.subscribe("focus_updated", lambda *_: self._refresh_stats())

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_pre_enter(self):
        self.bottom_nav.set_tab("modules")
        self._refresh_stats()

    def _handle_navigation(self, route):
        if self.manager and route != "focus":
            self.manager.current = route

    def _build_ui(self):
        self.content.clear_widgets()

        # 1. Mode Presets Row
        mode_row = BoxLayout(spacing=6, size_hint_y=None, height=36)
        modes = [
            ("pomodoro", "Pomodoro (25m)"),
            ("short_break", "Pause (5m)"),
            ("long_break", "Longue (15m)"),
            ("stopwatch", "Libre"),
        ]
        self.mode_buttons = {}
        for m_key, m_label in modes:
            is_active = (m_key == self.mode)
            if is_active:
                btn = AtelierButton(text=m_label, font_size="10sp", size_hint_x=1.0)
            else:
                btn = AtelierGhostButton(text=m_label, font_size="10sp", size_hint_x=1.0)
            btn.bind(on_release=lambda _, k=m_key: self._set_mode(k))
            self.mode_buttons[m_key] = btn
            mode_row.add_widget(btn)

        self.content.add_widget(mode_row)

        # 2. Main Dial / Timer Display Card
        timer_card = AtelierCard(
            orientation="vertical",
            spacing=10,
            padding=[20, 20, 20, 20],
            size_hint_y=None,
            height=200
        )

        self.lbl_cycle = Label(
            text=f"Cycle {self.current_cycle} sur {self.max_cycles} · Deep Work",
            font_size="11sp",
            bold=True,
            color=GOLD,
            halign="center",
            size_hint_y=None,
            height=20
        )
        timer_card.add_widget(self.lbl_cycle)

        self.lbl_timer = Label(
            text=self._format_time(self.remaining_seconds),
            font_size="48sp",
            bold=True,
            color=TEXT_PRIMARY,
            halign="center",
            size_hint_y=None,
            height=70
        )
        timer_card.add_widget(self.lbl_timer)

        self.prog_timer = AtelierProgressBar(value=100, size_hint_y=None, height=6)
        timer_card.add_widget(self.prog_timer)

        # Controls Row (Reset, Start/Pause, Finish)
        ctrl_row = BoxLayout(spacing=12, size_hint_y=None, height=44)
        btn_reset = AtelierGhostButton(text="↺ Réinitialiser", font_size="12sp", size_hint_x=0.35)
        btn_reset.bind(on_release=lambda _: self._reset_timer())

        self.btn_toggle = AtelierButton(
            text="▶ Démarrer",
            font_size="13sp",
            size_hint_x=0.45,
            bg_color=GOLD
        )
        self.btn_toggle.bind(on_release=lambda _: self._toggle_timer())

        btn_log = AtelierGhostButton(text="✓ Valider", font_size="12sp", size_hint_x=0.25)
        btn_log.bind(on_release=lambda _: self._finish_session(manual=True))

        ctrl_row.add_widget(btn_reset)
        ctrl_row.add_widget(self.btn_toggle)
        ctrl_row.add_widget(btn_log)
        timer_card.add_widget(ctrl_row)

        self.content.add_widget(timer_card)

        # 3. Context Link (Task / Subject)
        ctx_card = AtelierCard(
            orientation="vertical",
            spacing=8,
            padding=[14, 12, 14, 12],
            size_hint_y=None,
            height=90
        )
        lbl_ctx_title = Label(
            text="CONTEXTE D'ANCRAGE & TÂCHE LIÉE",
            font_size="10sp",
            bold=True,
            color=GOLD,
            halign="left",
            size_hint_y=None,
            height=16
        )
        lbl_ctx_title.bind(size=lbl_ctx_title.setter("text_size"))
        ctx_card.add_widget(lbl_ctx_title)

        tasks = ds.tasks.list_tasks(filter_status="pending")
        self.task_map = {f"{t['title'][:32]}": t["id"] for t in tasks}
        self.task_map["Session Libre (Générale)"] = None
        task_choices = list(self.task_map.keys())

        self.sp_task = Spinner(
            text=task_choices[0],
            values=task_choices,
            background_color=BG_CARD_HOVER,
            color=TEXT_PRIMARY,
            size_hint_y=None,
            height=40
        )
        ctx_card.add_widget(self.sp_task)
        self.content.add_widget(ctx_card)

        # 4. Today Statistics Section
        self.stats_container = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        self.stats_container.bind(minimum_height=self.stats_container.setter("height"))
        self.content.add_widget(self.stats_container)

        self._refresh_stats()

    def _format_time(self, seconds: int) -> str:
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"

    def _set_mode(self, mode):
        self._stop_ticker()
        self.mode = mode
        if mode == "pomodoro":
            self.preset_seconds = 25 * 60
            self.lbl_cycle.text = f"Cycle {self.current_cycle} sur {self.max_cycles} · Deep Work"
        elif mode == "short_break":
            self.preset_seconds = 5 * 60
            self.lbl_cycle.text = "Pause Récupération Rapide"
        elif mode == "long_break":
            self.preset_seconds = 15 * 60
            self.lbl_cycle.text = "Pause Longue & Déconnexion"
        elif mode == "stopwatch":
            self.preset_seconds = 0
            self.lbl_cycle.text = "Chronomètre Libre"

        self.remaining_seconds = self.preset_seconds
        self.lbl_timer.text = self._format_time(self.remaining_seconds)
        self.prog_timer.value = 100
        self.btn_toggle.text = "▶ Démarrer"
        self._build_ui()

    def _toggle_timer(self):
        if self.is_running:
            self._pause_timer()
        else:
            self._start_timer()

    def _start_timer(self):
        self.is_running = True
        self.btn_toggle.text = "⏸ Pause"
        if not self.timer_event:
            self.timer_event = Clock.schedule_interval(self._tick, 1.0)

    def _pause_timer(self):
        self.is_running = False
        self.btn_toggle.text = "▶ Reprendre"
        self._stop_ticker()

    def _stop_ticker(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

    def _reset_timer(self):
        self._stop_ticker()
        self.is_running = False
        self.remaining_seconds = self.preset_seconds
        self.lbl_timer.text = self._format_time(self.remaining_seconds)
        self.prog_timer.value = 100
        self.btn_toggle.text = "▶ Démarrer"

    def _tick(self, dt):
        if self.mode == "stopwatch":
            self.remaining_seconds += 1
            self.lbl_timer.text = self._format_time(self.remaining_seconds)
            self.prog_timer.value = min(100, (self.remaining_seconds % 3600) / 36)
        else:
            if self.remaining_seconds > 0:
                self.remaining_seconds -= 1
                self.lbl_timer.text = self._format_time(self.remaining_seconds)
                pct = int((self.remaining_seconds / max(self.preset_seconds, 1)) * 100)
                self.prog_timer.value = pct
            else:
                self._finish_session(manual=False)

    def _finish_session(self, manual=False):
        self._stop_ticker()
        self.is_running = False

        if self.mode == "stopwatch":
            duration = max(1, self.remaining_seconds // 60)
        else:
            elapsed = self.preset_seconds - self.remaining_seconds
            duration = max(1, elapsed // 60) if manual else (self.preset_seconds // 60)

        # Log session to database
        task_id = self.task_map.get(self.sp_task.text) if hasattr(self, "sp_task") else None
        title = self.sp_task.text if hasattr(self, "sp_task") else "Focus Pomodoro"
        ds.focus.log_session(
            title=title,
            duration_minutes=duration,
            mode=self.mode,
            task_id=task_id
        )

        if self.mode == "pomodoro":
            self.current_cycle = (self.current_cycle % self.max_cycles) + 1

        self._reset_timer()
        self._refresh_stats()

    def _refresh_stats(self):
        self.stats_container.clear_widgets()

        stats = ds.focus.get_today_focus_stats()
        total_m = stats.get("total_minutes", 0)
        count = stats.get("session_count", 0)
        formatted = stats.get("formatted_time", "0m")

        kpi_card = AtelierCard(
            orientation="vertical",
            spacing=8,
            padding=[14, 12, 14, 12],
            size_hint_y=None,
            height=86
        )
        lbl_k_head = Label(
            text="STATISTIQUES DU JOUR  ·  OBJECTIF 4H",
            font_size="10sp",
            bold=True,
            color=GOLD,
            halign="left",
            size_hint_y=None,
            height=16
        )
        lbl_k_head.bind(size=lbl_k_head.setter("text_size"))
        kpi_card.add_widget(lbl_k_head)

        grid = GridLayout(cols=3, spacing=10, size_hint_y=1)
        c1 = BoxLayout(orientation="vertical")
        c1.add_widget(Label(text=formatted, font_size="18sp", bold=True, color=TEXT_PRIMARY))
        c1.add_widget(Label(text="Durée Totale", font_size="10sp", color=TEXT_SECONDARY))

        c2 = BoxLayout(orientation="vertical")
        c2.add_widget(Label(text=f"{count}", font_size="18sp", bold=True, color=GOLD))
        c2.add_widget(Label(text="Sessions Finies", font_size="10sp", color=TEXT_SECONDARY))

        # Goal completion % (4h = 240 mins)
        comp_pct = min(100, int((total_m / 240.0) * 100))
        c3 = BoxLayout(orientation="vertical")
        c3.add_widget(Label(text=f"{comp_pct}%", font_size="18sp", bold=True, color=CHAMPAGNE))
        c3.add_widget(Label(text="Complétion", font_size="10sp", color=TEXT_SECONDARY))

        grid.add_widget(c1)
        grid.add_widget(c2)
        grid.add_widget(c3)
        kpi_card.add_widget(grid)
        self.stats_container.add_widget(kpi_card)

        # Recent sessions
        recent = stats.get("recent_sessions", [])
        if recent:
            lbl_rec = Label(
                text="SESSIONS RÉCENTES",
                font_size="11sp",
                bold=True,
                color=GOLD,
                halign="left",
                size_hint_y=None,
                height=22
            )
            lbl_rec.bind(size=lbl_rec.setter("text_size"))
            self.stats_container.add_widget(lbl_rec)

            for s in recent[:4]:
                r_card = AtelierCard(
                    orientation="horizontal",
                    spacing=10,
                    padding=[12, 8, 12, 8],
                    size_hint_y=None,
                    height=52
                )
                txt_b = BoxLayout(orientation="vertical", spacing=2)
                t_lbl = Label(text=s["title"][:30], font_size="13sp", bold=True, color=TEXT_PRIMARY, halign="left")
                t_lbl.bind(size=t_lbl.setter("text_size"))
                time_str = s.get("completed_at", "")[11:16]
                m_lbl = Label(text=f"{s.get('mode', 'pomodoro').upper()}  ·  {time_str}", font_size="10sp", color=TEXT_SECONDARY, halign="left")
                m_lbl.bind(size=m_lbl.setter("text_size"))
                txt_b.add_widget(t_lbl)
                txt_b.add_widget(m_lbl)
                r_card.add_widget(txt_b)

                badge = AtelierBadge(text=f"{s['duration_minutes']} min", badge_color=GOLD)
                r_card.add_widget(badge)
                self.stats_container.add_widget(r_card)
