"""Executive Modules & Hub Screen for LifeOS."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivymd.uix.label import MDIcon
from lifeos.ui.theme import (
    BG_CANVAS, BG_CARD, BG_CARD_HOVER, BORDER_COLOR,
    GOLD, CHAMPAGNE, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED
)
from lifeos.ui.components.navigation import AtelierTopBar, AtelierBottomNav

class ModuleCard(ButtonBehavior, BoxLayout):
    def __init__(self, route_name, title, subtitle, icon_name, badge_text="", on_click=None, **kwargs):
        super().__init__(**kwargs)
        self.route_name = route_name
        self.on_click = on_click
        self.orientation = "horizontal"
        self.spacing = 14
        self.padding = [14, 12, 14, 12]
        self.size_hint_y = None
        self.height = 72

        with self.canvas.before:
            self._col = Color(rgba=BG_CARD)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[14])
            self._line_col = Color(rgba=BORDER_COLOR)
            self._line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 14), width=1.1)

        self.bind(pos=self._update, size=self._update, state=self._on_state)

        # Icon box
        icon_box = BoxLayout(size_hint=(None, 1), width=44)
        with icon_box.canvas.before:
            Color(GOLD[0], GOLD[1], GOLD[2], 0.12)
            self._ib_rect = RoundedRectangle(pos=icon_box.pos, size=icon_box.size, radius=[10])
        icon_box.bind(pos=lambda *_: setattr(self._ib_rect, "pos", icon_box.pos),
                      size=lambda *_: setattr(self._ib_rect, "size", icon_box.size))

        self.icon_widget = MDIcon(
            icon=icon_name,
            theme_text_color="Custom",
            text_color=GOLD,
            font_size="24sp",
            halign="center",
            pos_hint={"center_y": 0.5}
        )
        icon_box.add_widget(self.icon_widget)
        self.add_widget(icon_box)

        # Text Column
        text_col = BoxLayout(orientation="vertical", spacing=2, pos_hint={"center_y": 0.5})
        lbl_title = Label(
            text=title,
            font_size="15sp",
            bold=True,
            color=TEXT_PRIMARY,
            halign="left"
        )
        lbl_title.bind(size=lbl_title.setter("text_size"))

        lbl_sub = Label(
            text=subtitle,
            font_size="11sp",
            color=TEXT_SECONDARY,
            halign="left"
        )
        lbl_sub.bind(size=lbl_sub.setter("text_size"))

        text_col.add_widget(lbl_title)
        text_col.add_widget(lbl_sub)
        self.add_widget(text_col)

        # Chevron arrow
        lbl_arr = Label(
            text="›",
            font_size="22sp",
            bold=True,
            color=GOLD,
            size_hint=(None, 1),
            width=24
        )
        self.add_widget(lbl_arr)

    def _on_state(self, instance, value):
        if value == "down":
            self._col.rgba = BG_CARD_HOVER
            self._line_col.rgba = GOLD
        else:
            self._col.rgba = BG_CARD
            self._line_col.rgba = BORDER_COLOR

    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._line.rounded_rectangle = (self.x, self.y, self.width, self.height, 14)

    def on_release(self):
        if self.on_click:
            self.on_click(self.route_name)


class ModulesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(rgba=BG_CANVAS)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar
        self.top_bar = AtelierTopBar(
            title="LifeOS Hub",
            subtitle="ÉCOSYSTÈME DE PRODUCTIVITÉ"
        )
        self.root_box.add_widget(self.top_bar)

        # Scrollview
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=[16, 16, 16, 20],
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
        self._build_modules_list()

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_pre_enter(self):
        self.bottom_nav.set_tab("modules")

    def _handle_navigation(self, route):
        if self.manager and route != "modules":
            self.manager.current = route

    def _nav_to(self, route):
        if self.manager:
            self.manager.current = route

    def _build_modules_list(self):
        self.content.clear_widgets()

        # Category: CŒUR OPÉRATIONNEL
        lbl_cat1 = Label(
            text="CŒUR OPÉRATIONNEL",
            font_size="11sp",
            bold=True,
            color=GOLD,
            halign="left",
            size_hint_y=None,
            height=24
        )
        lbl_cat1.bind(size=lbl_cat1.setter("text_size"))
        self.content.add_widget(lbl_cat1)

        core_modules = [
            ("tasks", "Tâches & Priorités", "Gestion matricielle Eisenhower, durées & sous-tâches", "checkbox-marked-circle-outline"),
            ("projects", "Projets Stratégiques", "Suivi de progression, jalons et livrables", "folder-outline"),
            ("calendar", "Calendrier & Blocs", "Time-blocking, rendez-vous et sessions", "calendar-blank-outline"),
            ("focus", "Focus Pomodoro & Chronomètre", "Sessions profondes de 25m, alertes et logs", "timer-sand"),
        ]
        for route, title, sub, icon in core_modules:
            self.content.add_widget(ModuleCard(route, title, sub, icon, on_click=self._nav_to))

        # Category: DISCIPLINE & MAÎTRISE
        lbl_cat2 = Label(
            text="DISCIPLINE & CROISSANCE",
            font_size="11sp",
            bold=True,
            color=GOLD,
            halign="left",
            size_hint_y=None,
            height=28
        )
        lbl_cat2.bind(size=lbl_cat2.setter("text_size"))
        self.content.add_widget(lbl_cat2)

        growth_modules = [
            ("habits", "Habitudes & Rituels", "Architecture du quotidien, suivi sur 7 jours", "repeat"),
            ("streaks", "Streaks & Protocole Quotidien", "Checklist quotidienne interactive et séries de jours", "fire"),
            ("study", "Study Hub Académique", "Matières, compte à rebours partiels et révisions", "school-outline"),
            ("goals", "Objectifs & Jalons", "Horizon stratégique, progression et cibles", "target"),
        ]
        for route, title, sub, icon in growth_modules:
            self.content.add_widget(ModuleCard(route, title, sub, icon, on_click=self._nav_to))

        # Category: ANALYTIQUE & SYSTÈME
        lbl_cat3 = Label(
            text="ANALYTIQUE & SYSTÈME",
            font_size="11sp",
            bold=True,
            color=GOLD,
            halign="left",
            size_hint_y=None,
            height=28
        )
        lbl_cat3.bind(size=lbl_cat3.setter("text_size"))
        self.content.add_widget(lbl_cat3)

        sys_modules = [
            ("statistics", "Tableau de Bord Analytique", "Graphiques de volume, constance et vélocité", "chart-bar"),
            ("settings", "Paramètres & Souveraineté", "Sauvegardes JSON, base SQLite et préférences", "cog-outline"),
        ]
        for route, title, sub, icon in sys_modules:
            self.content.add_widget(ModuleCard(route, title, sub, icon, on_click=self._nav_to))
