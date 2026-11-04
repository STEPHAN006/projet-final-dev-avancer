"""Executive Modules & Hub Screen for LifeOS (Shadcn / React Native style)."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivymd.uix.label import MDIcon
from lifeos.ui.theme import theme
from lifeos.ui.components.navigation import AtelierTopBar, AtelierBottomNav
from lifeos.core.events import bus

class ModuleCard(ButtonBehavior, BoxLayout):
    def __init__(self, route_name, title, subtitle, icon_name, on_click=None, **kwargs):
        super().__init__(**kwargs)
        self.route_name = route_name
        self.on_click = on_click
        self.orientation = "horizontal"
        self.spacing = 14
        self.padding = [14, 12, 14, 12]
        self.size_hint_y = None
        self.height = 70

        with self.canvas.before:
            self._col = Color(rgba=theme.bg_card)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
            self._line_col = Color(rgba=theme.border)
            self._line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 12), width=1.0)

        self.bind(pos=self._update, size=self._update, state=self._on_state)

        # Icon box
        icon_box = BoxLayout(size_hint=(None, None), size=(40, 40), pos_hint={"center_y": 0.5})
        with icon_box.canvas.before:
            self._ib_col = Color(theme.primary[0], theme.primary[1], theme.primary[2], 0.12)
            self._ib_rect = RoundedRectangle(pos=icon_box.pos, size=icon_box.size, radius=[10])
        icon_box.bind(pos=lambda *_: setattr(self._ib_rect, "pos", icon_box.pos),
                      size=lambda *_: setattr(self._ib_rect, "size", icon_box.size))

        self.icon_widget = MDIcon(
            icon=icon_name,
            theme_text_color="Custom",
            text_color=theme.primary,
            font_size="22sp",
            halign="center",
            pos_hint={"center_y": 0.5}
        )
        icon_box.add_widget(self.icon_widget)
        self.add_widget(icon_box)

        # Text Column
        text_col = BoxLayout(orientation="vertical", spacing=2, pos_hint={"center_y": 0.5})
        self.lbl_title = Label(
            text=title,
            font_size="14sp",
            bold=True,
            color=theme.text_primary,
            halign="left"
        )
        self.lbl_title.bind(size=self.lbl_title.setter("text_size"))

        self.lbl_sub = Label(
            text=subtitle,
            font_size="11sp",
            color=theme.text_secondary,
            halign="left"
        )
        self.lbl_sub.bind(size=self.lbl_sub.setter("text_size"))

        text_col.add_widget(self.lbl_title)
        text_col.add_widget(self.lbl_sub)
        self.add_widget(text_col)

        # Chevron arrow icon
        self.chev = MDIcon(
            icon="chevron-right",
            theme_text_color="Custom",
            text_color=theme.text_muted,
            font_size="20sp",
            size_hint=(None, None),
            size=(24, 24),
            pos_hint={"center_y": 0.5}
        )
        self.add_widget(self.chev)

        bus.subscribe("theme_changed", self._on_theme)

    def _on_theme(self, *args, **kwargs):
        self._col.rgba = theme.bg_card
        self._line_col.rgba = theme.border
        self._ib_col.rgba = [theme.primary[0], theme.primary[1], theme.primary[2], 0.12]
        self.icon_widget.text_color = theme.primary
        self.lbl_title.color = theme.text_primary
        self.lbl_sub.color = theme.text_secondary
        self.chev.text_color = theme.text_muted

    def _on_state(self, instance, value):
        if value == "down":
            self._col.rgba = theme.bg_card_hover
        else:
            self._col.rgba = theme.bg_card

    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._line.rounded_rectangle = (self.x, self.y, self.width, self.height, 12)

    def on_release(self):
        if self.on_click:
            self.on_click(self.route_name)


class ModulesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._bg_col = Color(rgba=theme.bg_canvas)
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
        self._build_modules_list()

        bus.subscribe("theme_changed", self._on_theme)

    def _on_theme(self, *args, **kwargs):
        self._bg_col.rgba = theme.bg_canvas
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

        # Section 1
        self._add_header("CŒUR OPÉRATIONNEL")
        core = [
            ("tasks", "Tâches & Priorités", "Gestion matricielle, durées et sous-tâches", "checkbox-marked-circle-outline"),
            ("projects", "Projets Stratégiques", "Suivi de progression, jalons et livrables", "folder-outline"),
            ("calendar", "Calendrier & Blocs", "Time-blocking, rendez-vous et sessions", "calendar-blank-outline"),
            ("focus", "Focus Pomodoro & Chrono", "Sessions profondes de 25m et alertes", "timer-sand"),
        ]
        for route, title, sub, icon in core:
            self.content.add_widget(ModuleCard(route, title, sub, icon, on_click=self._nav_to))

        # Section 2
        self._add_header("DISCIPLINE & CROISSANCE")
        growth = [
            ("habits", "Habitudes & Rituels", "Architecture du quotidien, suivi sur 7 jours", "repeat"),
            ("streaks", "Streaks & Protocole", "Checklist quotidienne et séries consécutives", "fire"),
            ("study", "Study Hub Académique", "Matières, compte à rebours partiels et révisions", "school-outline"),
            ("goals", "Objectifs & Jalons", "Horizon stratégique, progression et cibles", "target"),
        ]
        for route, title, sub, icon in growth:
            self.content.add_widget(ModuleCard(route, title, sub, icon, on_click=self._nav_to))

        # Section 3
        self._add_header("ANALYTIQUE & SYSTÈME")
        sys_mods = [
            ("statistics", "Tableau de Bord Analytique", "Graphiques de volume, constance et vélocité", "chart-bar"),
            ("settings", "Paramètres & Thèmes", "Sauvegardes JSON, mode clair/sombre et SQLite", "cog-outline"),
        ]
        for route, title, sub, icon in sys_mods:
            self.content.add_widget(ModuleCard(route, title, sub, icon, on_click=self._nav_to))

    def _add_header(self, text):
        lbl = Label(
            text=text,
            font_size="11sp",
            bold=True,
            color=theme.text_secondary,
            halign="left",
            size_hint_y=None,
            height=26
        )
        lbl.bind(size=lbl.setter("text_size"))
        self.content.add_widget(lbl)
