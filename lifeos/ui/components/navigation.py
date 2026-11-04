"""Navigation Bars (TopBar & BottomBar) for Atelier OS."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDIcon
from lifeos.ui.theme import (
    BG_SURFACE, BORDER_COLOR, GOLD, TEXT_PRIMARY,
    TEXT_SECONDARY, TEXT_MUTED
)

class AtelierTopBar(BoxLayout):
    title = StringProperty("LifeOS")
    subtitle = StringProperty("SANCTUAIRE PRIVÉ")

    def __init__(self, on_back=None, right_action=None, right_icon=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 56
        self.padding = [12, 4, 12, 4]
        self.spacing = 8

        with self.canvas.before:
            Color(rgba=BG_SURFACE)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(rgba=BORDER_COLOR)
            self._border = Line(points=[self.x, self.y, self.right, self.y], width=1.1)

        self.bind(pos=self._update, size=self._update)

        # Back button or Logo Icon
        if on_back:
            btn_back = MDIconButton(
                icon="arrow-left",
                theme_icon_color="Custom",
                icon_color=TEXT_PRIMARY,
                pos_hint={"center_y": 0.5}
            )
            btn_back.bind(on_release=lambda x: on_back())
            self.add_widget(btn_back)
        else:
            # Sanctuary symbol
            icon_box = Label(
                text="Ω",
                font_size="20sp",
                bold=True,
                color=GOLD,
                size_hint=(None, None),
                size=(36, 36),
                pos_hint={"center_y": 0.5}
            )
            self.add_widget(icon_box)

        # Title and Subtitle
        text_layout = BoxLayout(orientation="vertical", spacing=0, pos_hint={"center_y": 0.5})
        lbl_title = Label(
            text=self.title,
            font_size="16sp",
            bold=True,
            color=TEXT_PRIMARY,
            halign="left",
            valign="middle",
            size_hint_y=0.6
        )
        lbl_title.bind(size=lbl_title.setter("text_size"))
        self.bind(title=lbl_title.setter("text"))

        lbl_sub = Label(
            text=self.subtitle.upper(),
            font_size="10sp",
            color=GOLD,
            halign="left",
            valign="middle",
            size_hint_y=0.4
        )
        lbl_sub.bind(size=lbl_sub.setter("text_size"))
        self.bind(subtitle=lambda _, val: setattr(lbl_sub, 'text', val.upper()))

        text_layout.add_widget(lbl_title)
        text_layout.add_widget(lbl_sub)
        self.add_widget(text_layout)

        # Right Action if provided
        if right_action and right_icon:
            btn_right = MDIconButton(
                icon=right_icon,
                theme_icon_color="Custom",
                icon_color=GOLD,
                pos_hint={"center_y": 0.5}
            )
            btn_right.bind(on_release=lambda x: right_action())
            self.add_widget(btn_right)

    def _update(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.points = [self.x, self.y, self.right, self.y]


class NavTabItem(ButtonBehavior, BoxLayout):
    def __init__(self, route_name, label_text, icon_name, is_active=False, on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.route_name = route_name
        self.is_active = is_active
        self.on_select = on_select
        self.orientation = "vertical"
        self.spacing = 2
        self.padding = [0, 6, 0, 4]

        color = GOLD if is_active else TEXT_SECONDARY

        self.icon_widget = MDIcon(
            icon=icon_name,
            theme_text_color="Custom",
            text_color=color,
            font_size="22sp",
            halign="center",
            size_hint_y=0.65
        )
        self.add_widget(self.icon_widget)

        self.label_widget = Label(
            text=label_text,
            font_size="10sp",
            bold=is_active,
            color=color,
            halign="center",
            size_hint_y=0.35
        )
        self.add_widget(self.label_widget)

        # Active indicator pip
        self.bind(pos=self._update_pip, size=self._update_pip)

    def on_release(self):
        if self.on_select:
            self.on_select(self.route_name)

    def set_active(self, active: bool):
        self.is_active = active
        color = GOLD if active else TEXT_SECONDARY
        self.icon_widget.text_color = color
        self.label_widget.color = color
        self.label_widget.bold = active
        self._update_pip()

    def _update_pip(self, *args):
        self.canvas.after.clear()
        if self.is_active:
            with self.canvas.after:
                Color(rgba=GOLD)
                RoundedRectangle(
                    pos=(self.center_x - 10, self.y + 2),
                    size=(20, 2.5),
                    radius=[1.5]
                )


class AtelierBottomNav(BoxLayout):
    current_tab = StringProperty("dashboard")

    def __init__(self, nav_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.nav_callback = nav_callback
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 60
        self.items = {}

        with self.canvas.before:
            Color(rgba=BG_SURFACE)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(rgba=BORDER_COLOR)
            self._border = Line(points=[self.x, self.top, self.right, self.top], width=1.1)

        self.bind(pos=self._update, size=self._update)

        tabs = [
            ("dashboard", "Accueil", "view-dashboard-outline"),
            ("tasks", "Tâches", "checkbox-marked-circle-outline"),
            ("projects", "Projets", "folder-outline"),
            ("calendar", "Calendrier", "calendar-blank-outline"),
            ("modules", "Modules", "apps"),
        ]

        for route, label, icon in tabs:
            item = NavTabItem(
                route_name=route,
                label_text=label,
                icon_name=icon,
                is_active=(route == self.current_tab),
                on_select=self._on_item_click
            )
            self.items[route] = item
            self.add_widget(item)

    def _on_item_click(self, route):
        self.set_tab(route)
        if self.nav_callback:
            self.nav_callback(route)

    def set_tab(self, route):
        self.current_tab = route
        for r, itm in self.items.items():
            itm.set_active(r == route)

    def _update(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._border.points = [self.x, self.top, self.right, self.top]
