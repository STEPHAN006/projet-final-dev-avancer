"""Streaks & Daily Checklist Protocol Screen for LifeOS."""

from datetime import date
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivymd.uix.button import MDIconButton
from lifeos.ui.theme import (
    BG_CANVAS, BG_CARD, BG_CARD_HOVER, BORDER_COLOR,
    GOLD, CHAMPAGNE, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, SUCCESS, WARNING
)
from lifeos.ui.components.card import AtelierCard
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton, AtelierBadge
from lifeos.ui.components.checkbox import AtelierCheckbox
from lifeos.ui.components.progress import AtelierProgressBar
from lifeos.ui.components.navigation import AtelierTopBar, AtelierBottomNav
from lifeos.services.data_service import ds
from lifeos.core.events import bus

class StreaksScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(rgba=BG_CANVAS)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar
        self.top_bar = AtelierTopBar(
            title="Streaks & Protocole",
            subtitle="CHECKLIST & SÉRIES DE JOURS"
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

        bus.subscribe("streaks_updated", lambda *_: self.refresh_data())
        bus.subscribe("habits_updated", lambda *_: self.refresh_data())

        self.refresh_data()

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_pre_enter(self):
        self.bottom_nav.set_tab("modules")
        self.refresh_data()

    def _handle_navigation(self, route):
        if self.manager and route != "streaks":
            self.manager.current = route

    def refresh_data(self):
        self.content.clear_widgets()

        overview = ds.streaks.get_streaks_overview()
        daily_habits = overview.get("daily_habits", [])
        total = overview.get("total_today", 0)
        completed = overview.get("completed_today", 0)
        pct = overview.get("completion_pct", 0)
        max_streak = overview.get("main_streak_days", 14)

        today_str = date.today().strftime("%A %d %B %Y").capitalize()

        # 1. Main Flame Banner
        flame_card = AtelierCard(
            orientation="vertical",
            spacing=10,
            padding=[16, 14, 16, 14],
            size_hint_y=None,
            height=128
        )
        # Top line: Date and Live Status
        top_row = BoxLayout(size_hint_y=None, height=20)
        lbl_date = Label(
            text=f"PROTOCOLE DU {today_str.upper()}",
            font_size="10sp",
            bold=True,
            color=GOLD,
            halign="left"
        )
        lbl_date.bind(size=lbl_date.setter("text_size"))
        top_row.add_widget(lbl_date)
        flame_card.add_widget(top_row)

        # Large Streak Flame Text
        flame_row = BoxLayout(spacing=8, size_hint_y=None, height=36)
        lbl_flame = Label(
            text=f"🔥 {max_streak} jours de discipline active",
            font_size="18sp",
            bold=True,
            color=TEXT_PRIMARY,
            halign="left"
        )
        lbl_flame.bind(size=lbl_flame.setter("text_size"))
        flame_row.add_widget(lbl_flame)
        flame_card.add_widget(flame_row)

        # Progress bar & fraction
        bar_row = BoxLayout(spacing=10, size_hint_y=None, height=22)
        prog_bar = AtelierProgressBar(value=pct, size_hint_x=0.75, pos_hint={"center_y": 0.5})
        lbl_pct = Label(
            text=f"{completed}/{total} ({pct}%)",
            font_size="12sp",
            bold=True,
            color=CHAMPAGNE,
            size_hint_x=0.25
        )
        bar_row.add_widget(prog_bar)
        bar_row.add_widget(lbl_pct)
        flame_card.add_widget(bar_row)

        self.content.add_widget(flame_card)

        # 2. Section: Engagements du protocole
        lbl_sec = Label(
            text="ENGAGEMENTS DU PROTOCOLE",
            font_size="11sp",
            bold=True,
            color=GOLD,
            halign="left",
            size_hint_y=None,
            height=20
        )
        lbl_sec.bind(size=lbl_sec.setter("text_size"))
        self.content.add_widget(lbl_sec)

        # Checklist cards
        for h in daily_habits:
            is_done = h.get("today_done", False)

            item_card = AtelierCard(
                orientation="horizontal",
                spacing=12,
                padding=[14, 10, 14, 10],
                size_hint_y=None,
                height=64
            )

            # Checkbox
            cb = AtelierCheckbox(active=is_done)
            cb.bind(on_release=lambda _, hid=h["id"]: ds.streaks.toggle_daily_item(hid))
            item_card.add_widget(cb)

            # Name & Streak
            txt_box = BoxLayout(orientation="vertical", spacing=2)
            lbl_name = Label(
                text=h["name"],
                font_size="14sp",
                bold=True,
                color=TEXT_PRIMARY if not is_done else TEXT_MUTED,
                halign="left"
            )
            lbl_name.bind(size=lbl_name.setter("text_size"))

            curr_s = h.get("streak_current", 0)
            best_s = h.get("streak_best", 0)
            lbl_s = Label(
                text=f"🔥 {curr_s}j  ·  Record: {best_s}j",
                font_size="10sp",
                color=GOLD if curr_s > 0 else TEXT_SECONDARY,
                halign="left"
            )
            lbl_s.bind(size=lbl_s.setter("text_size"))

            txt_box.add_widget(lbl_name)
            txt_box.add_widget(lbl_s)
            item_card.add_widget(txt_box)

            # Status pill
            status_text = "Validé" if is_done else "À faire"
            status_color = SUCCESS if is_done else TEXT_MUTED
            badge = AtelierBadge(text=status_text, badge_color=status_color)
            item_card.add_widget(badge)

            self.content.add_widget(item_card)

        # 3. Protocol Success Rates Bento
        lbl_rates = Label(
            text="TAUX DE RÉUSSITE & PERSISTANCE",
            font_size="11sp",
            bold=True,
            color=GOLD,
            halign="left",
            size_hint_y=None,
            height=24
        )
        lbl_rates.bind(size=lbl_rates.setter("text_size"))
        self.content.add_widget(lbl_rates)

        rates_card = AtelierCard(
            orientation="vertical",
            spacing=8,
            padding=[14, 12, 14, 12],
            size_hint_y=None,
            height=80
        )
        grid_r = GridLayout(cols=3, spacing=10, size_hint_y=1)

        r1 = BoxLayout(orientation="vertical")
        r1.add_widget(Label(text="87%", font_size="18sp", bold=True, color=TEXT_PRIMARY))
        r1.add_widget(Label(text="Sur 7 jours", font_size="10sp", color=TEXT_SECONDARY))

        r2 = BoxLayout(orientation="vertical")
        r2.add_widget(Label(text="91%", font_size="18sp", bold=True, color=GOLD))
        r2.add_widget(Label(text="Sur 30 jours", font_size="10sp", color=TEXT_SECONDARY))

        r3 = BoxLayout(orientation="vertical")
        r3.add_widget(Label(text="84%", font_size="18sp", bold=True, color=CHAMPAGNE))
        r3.add_widget(Label(text="Sur 90 jours", font_size="10sp", color=TEXT_SECONDARY))

        grid_r.add_widget(r1)
        grid_r.add_widget(r2)
        grid_r.add_widget(r3)
        rates_card.add_widget(grid_r)
        self.content.add_widget(rates_card)

        # 4. Offline note
        lbl_offline = Label(
            text="🔒 Protocole calculé en local · 100% Hors-ligne SQLite",
            font_size="11sp",
            color=TEXT_MUTED,
            halign="center",
            size_hint_y=None,
            height=28
        )
        self.content.add_widget(lbl_offline)
