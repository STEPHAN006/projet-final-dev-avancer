"""Analytics & Statistics Screen for LifeOS."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
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

class WeeklyBarChart(Widget):
    """Clean custom Bar Chart drawn with Kivy graphics instructions."""
    def __init__(self, labels, values, **kwargs):
        super().__init__(**kwargs)
        self.labels = labels or ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        self.values = values or [3.5, 4.2, 5.0, 2.8, 4.0, 3.0, 2.0]
        self.size_hint_y = None
        self.height = 140
        self.bind(pos=self._redraw, size=self._redraw)

    def update_data(self, labels, values):
        self.labels = labels
        self.values = values
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        if not self.labels:
            return

        with self.canvas:
            # Baseline grid line
            Color(rgba=BORDER_COLOR)
            Line(points=[self.x + 10, self.y + 24, self.right - 10, self.y + 24], width=1.0)

            n = len(self.labels)
            avail_w = self.width - 20
            col_w = avail_w / n
            bar_w = min(24.0, col_w * 0.55)
            max_val = max(max(self.values) if self.values else 1.0, 4.0)

            chart_h = self.height - 45 # Space for top label and bottom label

            for i in range(n):
                val = self.values[i] if i < len(self.values) else 0.0
                bar_h = max(4.0, (val / max_val) * chart_h)

                cx = self.x + 10 + i * col_w + col_w / 2.0
                bx = cx - bar_w / 2.0
                by = self.y + 26

                # Bar background
                Color(rgba=BORDER_COLOR)
                RoundedRectangle(pos=(bx, by), size=(bar_w, chart_h), radius=[4])

                # Active Bar fill (Gold gradient/accent)
                Color(rgba=GOLD)
                RoundedRectangle(pos=(bx, by), size=(bar_w, bar_h), radius=[4])


class StatisticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_days = 7

        with self.canvas.before:
            Color(rgba=BG_CANVAS)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar
        self.top_bar = AtelierTopBar(
            title="Analytique & Stats",
            subtitle="DONNÉES AGRÉGÉES LOCALES"
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

        bus.subscribe("stats_updated", lambda *_: self.refresh_stats())
        bus.subscribe("tasks_updated", lambda *_: self.refresh_stats())
        bus.subscribe("focus_updated", lambda *_: self.refresh_stats())

        self.refresh_stats()

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_pre_enter(self):
        self.bottom_nav.set_tab("modules")
        self.refresh_stats()

    def _handle_navigation(self, route):
        if self.manager and route != "statistics":
            self.manager.current = route

    def refresh_stats(self):
        self.content.clear_widgets()

        report = ds.stats.get_analytics_report(days=self.selected_days)
        summary = ds.stats.get_dashboard_summary()

        # 1. Period Selector Row
        period_row = BoxLayout(spacing=8, size_hint_y=None, height=36)
        periods = [(7, "7 jours"), (30, "30 jours"), (90, "90 jours")]
        for d, lbl in periods:
            is_active = (d == self.selected_days)
            if is_active:
                btn = AtelierButton(text=lbl, font_size="11sp", size_hint_x=1.0)
            else:
                btn = AtelierGhostButton(text=lbl, font_size="11sp", size_hint_x=1.0)
            btn.bind(on_release=lambda _, days=d: self._set_period(days))
            period_row.add_widget(btn)

        self.content.add_widget(period_row)

        # 2. Executive KPI 4-Card Bento
        kpi_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=130)

        card1 = AtelierCard(orientation="vertical", spacing=2, padding=[12, 10, 12, 10])
        card1.add_widget(Label(text="TÂCHES FINIES", font_size="9sp", bold=True, color=GOLD, halign="left"))
        card1.add_widget(Label(text=f"{summary.get('completed_tasks', 48)}", font_size="22sp", bold=True, color=TEXT_PRIMARY, halign="left"))
        card1.add_widget(Label(text="Total archivé", font_size="10sp", color=TEXT_SECONDARY, halign="left"))

        card2 = AtelierCard(orientation="vertical", spacing=2, padding=[12, 10, 12, 10])
        card2.add_widget(Label(text="FOCUS CUMULÉ", font_size="9sp", bold=True, color=GOLD, halign="left"))
        card2.add_widget(Label(text=f"{report.get('total_focus_hours', 24.5):.1f}h", font_size="22sp", bold=True, color=CHAMPAGNE, halign="left"))
        card2.add_widget(Label(text=f"Sur {self.selected_days} jours", font_size="10sp", color=TEXT_SECONDARY, halign="left"))

        card3 = AtelierCard(orientation="vertical", spacing=2, padding=[12, 10, 12, 10])
        card3.add_widget(Label(text="HABITUDES", font_size="9sp", bold=True, color=GOLD, halign="left"))
        card3.add_widget(Label(text=f"{report.get('habit_consistency_pct', 88)}%", font_size="22sp", bold=True, color=SUCCESS, halign="left"))
        card3.add_widget(Label(text=f"Top streak: {summary.get('current_streak_days', 14)}j", font_size="10sp", color=TEXT_SECONDARY, halign="left"))

        card4 = AtelierCard(orientation="vertical", spacing=2, padding=[12, 10, 12, 10])
        card4.add_widget(Label(text="PRÉCISION ESTIM.", font_size="9sp", bold=True, color=GOLD, halign="left"))
        card4.add_widget(Label(text=f"{report.get('estimation_accuracy_pct', 85)}%", font_size="22sp", bold=True, color=TEXT_PRIMARY, halign="left"))
        card4.add_widget(Label(text="Planifié vs Réel", font_size="10sp", color=TEXT_SECONDARY, halign="left"))

        kpi_grid.add_widget(card1)
        kpi_grid.add_widget(card2)
        kpi_grid.add_widget(card3)
        kpi_grid.add_widget(card4)
        self.content.add_widget(kpi_grid)

        # 3. Weekly Focus Bar Chart Card
        chart_card = AtelierCard(
            orientation="vertical",
            spacing=8,
            padding=[14, 12, 14, 12],
            size_hint_y=None,
            height=210
        )
        row_c_head = BoxLayout(size_hint_y=None, height=20)
        lbl_c_title = Label(
            text="VOLUME FOCUS (HEURES / JOUR)",
            font_size="10sp",
            bold=True,
            color=GOLD,
            halign="left"
        )
        lbl_c_title.bind(size=lbl_c_title.setter("text_size"))
        row_c_head.add_widget(lbl_c_title)
        chart_card.add_widget(row_c_head)

        # Custom Bar Chart
        bar_chart = WeeklyBarChart(
            labels=report.get("focus_labels", []),
            values=report.get("focus_hours", [])
        )
        chart_card.add_widget(bar_chart)

        # Days labels row under chart
        lbls_row = BoxLayout(spacing=2, size_hint_y=None, height=20)
        for lab in report.get("focus_labels", []):
            l = Label(text=lab, font_size="10sp", bold=True, color=TEXT_SECONDARY, halign="center")
            lbls_row.add_widget(l)
        chart_card.add_widget(lbls_row)

        self.content.add_widget(chart_card)

        # 4. Time Distribution by Project / Category
        dist_card = AtelierCard(
            orientation="vertical",
            spacing=10,
            padding=[14, 12, 14, 12],
            size_hint_y=None,
            height=150
        )
        lbl_d_title = Label(
            text="RÉPARTITION DU TEMPS PAR PÔLE",
            font_size="10sp",
            bold=True,
            color=GOLD,
            halign="left",
            size_hint_y=None,
            height=16
        )
        lbl_d_title.bind(size=lbl_d_title.setter("text_size"))
        dist_card.add_widget(lbl_d_title)

        dist_data = report.get("category_distribution", {"Dev": 180, "Académique": 120, "Santé": 45})
        total_dist = max(sum(dist_data.values()), 1)

        colors_map = {
            "Dev": GOLD,
            "Académique": CHAMPAGNE,
            "Santé": SUCCESS,
            "Personnel": WARNING
        }

        for cat, val in dist_data.items():
            pct = int((val / total_dist) * 100)
            d_row = BoxLayout(spacing=8, size_hint_y=None, height=18)
            l_cat = Label(text=f"{cat} ({pct}%)", font_size="11sp", color=TEXT_PRIMARY, size_hint_x=0.4, halign="left")
            l_cat.bind(size=l_cat.setter("text_size"))
            p_bar = AtelierProgressBar(value=pct, progress_color=colors_map.get(cat, GOLD), size_hint_x=0.6, pos_hint={"center_y": 0.5})
            d_row.add_widget(l_cat)
            d_row.add_widget(p_bar)
            dist_card.add_widget(d_row)

        self.content.add_widget(dist_card)

        # 5. Offline note
        lbl_foot = Label(
            text="🔒 Données agrégées localement depuis SQLite · Zéro télémétrie",
            font_size="10sp",
            color=TEXT_MUTED,
            halign="center",
            size_hint_y=None,
            height=24
        )
        self.content.add_widget(lbl_foot)

    def _set_period(self, days):
        self.selected_days = days
        self.refresh_stats()
