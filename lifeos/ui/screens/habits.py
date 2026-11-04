"""Habits Tracking Screen for LifeOS (Shadcn / React Native style)."""

from datetime import date, timedelta
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivymd.uix.button import MDIconButton
from lifeos.ui.theme import theme
from lifeos.ui.components.card import AtelierCard
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton, AtelierBadge
from lifeos.ui.components.checkbox import AtelierCheckbox
from lifeos.ui.components.navigation import AtelierTopBar, AtelierBottomNav
from lifeos.ui.components.dialogs import AddHabitDialog
from lifeos.services.data_service import ds
from lifeos.core.events import bus

class HabitWeekDots(BoxLayout):
    """Mini 7-day progress indicator row."""
    def __init__(self, days_data, habit_id, on_day_click=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = 8
        self.size_hint_y = None
        self.height = 36

        day_letters = ["L", "M", "M", "J", "V", "S", "D"]
        for i, day in enumerate(days_data):
            d_box = BoxLayout(orientation="vertical", spacing=2, size_hint_x=1.0)

            lbl_l = Label(
                text=day_letters[i % 7],
                font_size="10sp",
                bold=True,
                color=theme.primary if day["done"] else theme.text_muted,
                size_hint_y=0.45
            )
            d_box.add_widget(lbl_l)

            dot = BoxLayout(size_hint=(None, None), size=(18, 18), pos_hint={"center_x": 0.5})
            is_done = day["done"]

            with dot.canvas:
                if is_done:
                    Color(rgba=theme.primary)
                    RoundedRectangle(pos=dot.pos, size=dot.size, radius=[4])
                else:
                    Color(rgba=theme.bg_muted)
                    RoundedRectangle(pos=dot.pos, size=dot.size, radius=[4])
                    Color(rgba=theme.border)
                    Line(rounded_rectangle=(dot.x, dot.y, dot.width, dot.height, 4), width=1.0)

            def _update_dot(inst, *args, done=is_done):
                inst.canvas.clear()
                with inst.canvas:
                    if done:
                        Color(rgba=theme.primary)
                        RoundedRectangle(pos=inst.pos, size=inst.size, radius=[4])
                    else:
                        Color(rgba=theme.bg_muted)
                        RoundedRectangle(pos=inst.pos, size=inst.size, radius=[4])
                        Color(rgba=theme.border)
                        Line(rounded_rectangle=(inst.x, inst.y, inst.width, inst.height, 4), width=1.0)

            dot.bind(pos=_update_dot, size=_update_dot)
            d_box.add_widget(dot)
            self.add_widget(d_box)


class HabitCard(AtelierCard):
    def __init__(self, habit, on_toggle=None, on_delete=None, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("spacing", 10)
        kwargs.setdefault("padding", [16, 12, 16, 12])
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", 132)
        super().__init__(**kwargs)

        self.habit = habit
        self.on_toggle = on_toggle

        # Header Row: Checkbox, Name, Streak, Delete
        header_row = BoxLayout(spacing=10, size_hint_y=None, height=36)

        self.cb = AtelierCheckbox(active=habit.get("today_done", False))
        self.cb.bind(on_release=lambda _: self._toggle())
        header_row.add_widget(self.cb)

        # Title & Subtitle
        t_box = BoxLayout(orientation="vertical", spacing=1)
        lbl_name = Label(
            text=habit["name"],
            font_size="14sp",
            bold=True,
            color=theme.text_primary,
            halign="left"
        )
        lbl_name.bind(size=lbl_name.setter("text_size"))

        lbl_desc = Label(
            text=f"{habit.get('frequency', 'Quotidien')}  ·  {habit.get('description', '')[:35]}",
            font_size="11sp",
            color=theme.text_secondary,
            halign="left"
        )
        lbl_desc.bind(size=lbl_desc.setter("text_size"))

        t_box.add_widget(lbl_name)
        t_box.add_widget(lbl_desc)
        header_row.add_widget(t_box)

        # Streak pill
        streak_badge = AtelierBadge(
            text=f"{habit.get('streak_current', 0)}j"
        )
        header_row.add_widget(streak_badge)

        if on_delete:
            btn_del = MDIconButton(
                icon="delete-outline",
                theme_icon_color="Custom",
                icon_color=theme.text_muted,
                size_hint=(None, None),
                size=(32, 32),
                pos_hint={"center_y": 0.5}
            )
            btn_del.bind(on_release=lambda _: on_delete(habit["id"]))
            header_row.add_widget(btn_del)

        self.add_widget(header_row)

        # 7-day dots row
        dots = HabitWeekDots(habit.get("days", []), habit["id"])
        self.add_widget(dots)

        # Bottom info row
        bot_row = BoxLayout(size_hint_y=None, height=18)
        lbl_max = Label(
            text=f"Record : {habit.get('streak_best', 0)} jours consécutifs",
            font_size="11sp",
            color=theme.text_secondary,
            halign="left"
        )
        lbl_max.bind(size=lbl_max.setter("text_size"))
        bot_row.add_widget(lbl_max)
        self.add_widget(bot_row)

    def _toggle(self):
        if self.on_toggle:
            self.on_toggle(self.habit["id"])


class HabitsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._bg_col = Color(rgba=theme.bg_canvas)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar
        self.top_bar = AtelierTopBar(
            title="Habitudes",
            subtitle="DISCIPLINE & ARCHITECTURE DU QUOTIDIEN",
            right_icon="plus-circle-outline",
            right_action=self._open_add_dialog
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

        bus.subscribe("habits_updated", lambda *_: self.refresh_habits())
        bus.subscribe("theme_changed", self._on_theme)

        self.refresh_habits()

    def _on_theme(self, *args, **kwargs):
        self._bg_col.rgba = theme.bg_canvas
        self.refresh_habits()

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_pre_enter(self):
        self.bottom_nav.set_tab("modules")
        self.refresh_habits()

    def _handle_navigation(self, route):
        if self.manager and route != "habits":
            self.manager.current = route

    def _open_add_dialog(self):
        dialog = AddHabitDialog(on_habit_created=lambda _: self.refresh_habits())
        dialog.open()

    def refresh_habits(self):
        self.content.clear_widgets()

        habits = ds.habits.list_habits_with_logs()

        # Summary Bento
        total = len(habits)
        done_today = sum(1 for h in habits if h.get("today_done"))
        best_streak = max([h.get("streak_best", 0) for h in habits] + [0])
        success_pct = int((done_today / total * 100)) if total > 0 else 0

        kpi_card = AtelierCard(
            orientation="vertical",
            spacing=10,
            padding=[16, 14, 16, 14],
            size_hint_y=None,
            height=86
        )
        kpi_head = Label(
            text="BILAN DU PROTOCOLE QUOTIDIEN",
            font_size="10sp",
            bold=True,
            color=theme.text_secondary,
            halign="left",
            size_hint_y=None,
            height=16
        )
        kpi_head.bind(size=kpi_head.setter("text_size"))
        kpi_card.add_widget(kpi_head)

        grid = GridLayout(cols=3, spacing=10, size_hint_y=None, height=44)
        c1 = BoxLayout(orientation="vertical")
        c1.add_widget(Label(text=f"{success_pct}%", font_size="18sp", bold=True, color=theme.text_primary))
        c1.add_widget(Label(text="Taux Aujourd'hui", font_size="10sp", color=theme.text_secondary))

        c2 = BoxLayout(orientation="vertical")
        c2.add_widget(Label(text=f"{done_today}/{total}", font_size="18sp", bold=True, color=theme.primary))
        c2.add_widget(Label(text="Actives Validées", font_size="10sp", color=theme.text_secondary))

        c3 = BoxLayout(orientation="vertical")
        c3.add_widget(Label(text=f"{best_streak}j", font_size="18sp", bold=True, color=theme.text_primary))
        c3.add_widget(Label(text="Record Série", font_size="10sp", color=theme.text_secondary))

        grid.add_widget(c1)
        grid.add_widget(c2)
        grid.add_widget(c3)
        kpi_card.add_widget(grid)
        self.content.add_widget(kpi_card)

        # Header for List
        lbl_list = Label(
            text=f"RITUELS & HABITUDES ({total})",
            font_size="11sp",
            bold=True,
            color=theme.text_secondary,
            halign="left",
            size_hint_y=None,
            height=20
        )
        lbl_list.bind(size=lbl_list.setter("text_size"))
        self.content.add_widget(lbl_list)

        for h in habits:
            card = HabitCard(
                habit=h,
                on_toggle=lambda hid: ds.habits.toggle_habit_for_date(hid),
                on_delete=lambda hid: ds.habits.delete_habit(hid)
            )
            self.content.add_widget(card)

        btn_add = AtelierGhostButton(
            text="+ Créer une nouvelle routine",
            size_hint_y=None,
            height=42
        )
        btn_add.bind(on_release=lambda _: self._open_add_dialog())
        self.content.add_widget(btn_add)
