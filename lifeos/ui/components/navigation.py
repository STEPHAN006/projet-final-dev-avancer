"""React Native / Shadcn Style Navigation Bars (TopBar & BottomBar) for LifeOS."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.properties import StringProperty
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDIcon
from lifeos.ui.theme import theme
from lifeos.core.events import bus

class AtelierTopBar(BoxLayout):
    title = StringProperty("LifeOS")
    subtitle = StringProperty("SANCTUAIRE PRIVÉ")

    def __init__(self, on_back=None, right_action=None, right_icon=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 54
        self.padding = [14, 4, 14, 4]
        self.spacing = 10

        with self.canvas.before:
            self._bg_col = Color(rgba=theme.bg_surface)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            self._border_col = Color(rgba=theme.border)
            self._border = Line(points=[self.x, self.y, self.right, self.y], width=1.0)

        self.bind(pos=self._update, size=self._update)

        # Back button or App Brand Icon
        if on_back:
            btn_back = MDIconButton(
                icon="arrow-left",
                theme_icon_color="Custom",
                icon_color=theme.text_primary,
                size_hint=(None, None),
                size=(36, 36),
                pos_hint={"center_y": 0.5}
            )
            btn_back.bind(on_release=lambda x: on_back())
            self.add_widget(btn_back)
        else:
            # Modern Brand Icon (Lightning / Pulse)
            icon_box = BoxLayout(size_hint=(None, None), size=(32, 32), pos_hint={"center_y": 0.5})
            with icon_box.canvas.before:
                self._logo_bg_col = Color(rgba=theme.bg_muted)
                self._logo_rect = RoundedRectangle(pos=icon_box.pos, size=icon_box.size, radius=[8])
            icon_box.bind(pos=lambda *_: setattr(self._logo_rect, "pos", icon_box.pos),
                          size=lambda *_: setattr(self._logo_rect, "size", icon_box.size))

            self.brand_icon = MDIcon(
                icon="lightning-bolt",
                theme_text_color="Custom",
                text_color=theme.primary,
                font_size="18sp",
                halign="center",
                valign="middle"
            )
            icon_box.add_widget(self.brand_icon)
            self.add_widget(icon_box)

        # Title & Subtitle column
        text_layout = BoxLayout(orientation="vertical", spacing=1, pos_hint={"center_y": 0.5})
        self.lbl_title = Label(
            text=self.title,
            font_size="16sp",
            bold=True,
            color=theme.text_primary,
            halign="left",
            valign="middle",
            size_hint_y=0.6
        )
        self.lbl_title.bind(size=self.lbl_title.setter("text_size"))
        self.bind(title=self.lbl_title.setter("text"))

        self.lbl_sub = Label(
            text=self.subtitle.upper(),
            font_size="10sp",
            bold=True,
            color=theme.text_secondary,
            halign="left",
            valign="middle",
            size_hint_y=0.4
        )
        self.lbl_sub.bind(size=self.lbl_sub.setter("text_size"))
        self.bind(subtitle=lambda _, val: setattr(self.lbl_sub, 'text', val.upper()))

        text_layout.add_widget(self.lbl_title)
        text_layout.add_widget(self.lbl_sub)
        self.add_widget(text_layout)

        # Theme Toggle Icon (Sun / Moon)
        t_icon = "weather-night" if theme.is_light else "white-balance-sunny"
        self.btn_theme = MDIconButton(
            icon=t_icon,
            theme_icon_color="Custom",
            icon_color=theme.text_secondary,
            size_hint=(None, None),
            size=(36, 36),
            pos_hint={"center_y": 0.5}
        )
        self.btn_theme.bind(on_release=lambda _: self._toggle_theme())
        self.add_widget(self.btn_theme)

        # Right Action if provided
        if right_action and right_icon:
            btn_right = MDIconButton(
                icon=right_icon,
                theme_icon_color="Custom",
                icon_color=theme.primary,
                size_hint=(None, None),
                size=(36, 36),
                pos_hint={"center_y": 0.5}
            )
            btn_right.bind(on_release=lambda x: right_action())
            self.add_widget(btn_right)

        bus.subscribe("theme_changed", self._on_theme)

    def _toggle_theme(self):
        theme.toggle()

    def _on_theme(self, *args, **kwargs):
        self._bg_col.rgba = theme.bg_surface
        self._border_col.rgba = theme.border
        self.lbl_title.color = theme.text_primary
        self.lbl_sub.color = theme.text_secondary
        if hasattr(self, "_logo_bg_col"):
            self._logo_bg_col.rgba = theme.bg_muted
            self.brand_icon.text_color = theme.primary
        self.btn_theme.icon = "weather-night" if theme.is_light else "white-balance-sunny"
        self.btn_theme.icon_color = theme.text_secondary

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
        self.spacing = 1
        self.padding = [0, 4, 0, 4]

        color = theme.primary if is_active else theme.text_secondary

        # Icon wrapper with subtle pill indicator
        self.icon_box = BoxLayout(size_hint=(None, None), size=(36, 24), pos_hint={"center_x": 0.5})
        with self.icon_box.canvas.before:
            self._pill_col = Color(rgba=[theme.primary[0], theme.primary[1], theme.primary[2], 0.15 if is_active else 0.0])
            self._pill = RoundedRectangle(pos=self.icon_box.pos, size=self.icon_box.size, radius=[12])
        self.icon_box.bind(pos=lambda *_: setattr(self._pill, "pos", self.icon_box.pos),
                           size=lambda *_: setattr(self._pill, "size", self.icon_box.size))

        self.icon_widget = MDIcon(
            icon=icon_name,
            theme_text_color="Custom",
            text_color=color,
            font_size="20sp",
            halign="center",
            pos_hint={"center_y": 0.5}
        )
        self.icon_box.add_widget(self.icon_widget)
        self.add_widget(self.icon_box)

        self.label_widget = Label(
            text=label_text,
            font_size="10sp",
            bold=is_active,
            color=color,
            halign="center",
            size_hint_y=None,
            height=14
        )
        self.add_widget(self.label_widget)

    def on_release(self):
        if self.on_select:
            self.on_select(self.route_name)

    def set_active(self, active: bool):
        self.is_active = active
        color = theme.primary if active else theme.text_secondary
        self.icon_widget.text_color = color
        self.label_widget.color = color
        self.label_widget.bold = active
        self._pill_col.rgba = [theme.primary[0], theme.primary[1], theme.primary[2], 0.15 if active else 0.0]


class AtelierBottomNav(BoxLayout):
    current_tab = StringProperty("dashboard")

    def __init__(self, nav_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.nav_callback = nav_callback
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 56
        self.items = {}

        with self.canvas.before:
            self._bg_col = Color(rgba=theme.bg_surface)
            self._bg = Rectangle(pos=self.pos, size=self.size)
            self._border_col = Color(rgba=theme.border)
            self._border = Line(points=[self.x, self.top, self.right, self.top], width=1.0)

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

        bus.subscribe("theme_changed", self._on_theme)

    def _on_theme(self, *args, **kwargs):
        self._bg_col.rgba = theme.bg_surface
        self._border_col.rgba = theme.border
        for r, itm in self.items.items():
            itm.set_active(r == self.current_tab)

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
