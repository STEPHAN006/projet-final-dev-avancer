"""Shadcn / React Native Buttons and Badges."""

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import ListProperty, NumericProperty, StringProperty
from lifeos.ui.theme import theme
from lifeos.core.events import bus

class AtelierButton(Button):
    """Shadcn Primary Button: Crisp solid background, high contrast text."""
    bg_color = ListProperty([])
    text_color = ListProperty([])
    radius = NumericProperty(8)

    def __init__(self, **kwargs):
        kwargs.setdefault("background_color", [0, 0, 0, 0])
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("bold", True)

        if "bg_color" not in kwargs:
            kwargs["bg_color"] = theme.primary
        if "text_color" not in kwargs:
            kwargs["text_color"] = theme.primary_text

        super().__init__(**kwargs)
        self.color = self.text_color
        self.bind(pos=self._update, size=self._update, state=self._on_state)

        with self.canvas.before:
            self._col = Color(rgba=self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])

        bus.subscribe("theme_changed", self._on_theme)

    def _on_theme(self, *args, **kwargs):
        self.bg_color = theme.primary
        self.text_color = theme.primary_text
        self.color = self.text_color
        self._update()

    def _on_state(self, instance, value):
        if value == "down":
            self._col.rgba = [c * 0.85 for c in self.bg_color[:3]] + [1.0]
        else:
            self._col.rgba = self.bg_color

    def _update(self, *args):
        if hasattr(self, "_rect"):
            self._rect.pos = self.pos
            self._rect.size = self.size
            self._rect.radius = [self.radius]
            self._col.rgba = self.bg_color


class AtelierGhostButton(Button):
    """Shadcn Outline / Ghost Button: 1px subtle border, high contrast text."""
    bg_color = ListProperty([])
    border_color = ListProperty([])
    text_color = ListProperty([])
    radius = NumericProperty(8)

    def __init__(self, **kwargs):
        kwargs.setdefault("background_color", [0, 0, 0, 0])
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("bold", False)

        if "bg_color" not in kwargs:
            kwargs["bg_color"] = [0, 0, 0, 0]
        if "border_color" not in kwargs:
            kwargs["border_color"] = theme.border
        if "text_color" not in kwargs:
            kwargs["text_color"] = theme.text_primary

        super().__init__(**kwargs)
        self.color = self.text_color
        self.bind(pos=self._update, size=self._update, state=self._on_state)

        with self.canvas.before:
            self._col = Color(rgba=self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self._line_col = Color(rgba=self.border_color)
            self._line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius), width=1.0)

        bus.subscribe("theme_changed", self._on_theme)

    def _on_theme(self, *args, **kwargs):
        self.border_color = theme.border
        self.text_color = theme.text_primary
        self.color = self.text_color
        self._update()

    def _on_state(self, instance, value):
        if value == "down":
            self._col.rgba = theme.bg_muted
        else:
            self._col.rgba = self.bg_color

    def _update(self, *args):
        if hasattr(self, "_rect"):
            self._rect.pos = self.pos
            self._rect.size = self.size
            self._rect.radius = [self.radius]
            self._line.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)
            self._line_col.rgba = self.border_color


class AtelierBadge(BoxLayout):
    """Shadcn Style Soft Pill Badge: subtle pastel background + crisp saturated label."""
    text = StringProperty("MEDIUM")

    def __init__(self, **kwargs):
        badge_col = kwargs.pop("badge_color", None)
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.height = 22
        self.padding = [8, 2, 8, 2]
        self.radius = 6

        bg_c, fg_c = theme.badge_colors(self.text)
        if badge_col:
            fg_c = badge_col
            bg_c = [badge_col[0], badge_col[1], badge_col[2], 0.15]

        self.label = Label(
            text=self.text.upper(),
            font_size="10sp",
            bold=True,
            color=fg_c,
            size_hint=(None, None),
            height=18
        )
        self.label.bind(texture_size=lambda _, sz: setattr(self.label, 'width', sz[0]))
        self.bind(text=self._on_text_change)
        self.add_widget(self.label)
        self.bind(pos=self._update, size=self._update)

        with self.canvas.before:
            self._bg_col = Color(rgba=bg_c)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])

        bus.subscribe("theme_changed", self._on_theme)

    def _on_theme(self, *args, **kwargs):
        self._on_text_change(None, self.text)

    def _on_text_change(self, instance, val):
        self.label.text = val.upper()
        bg_c, fg_c = theme.badge_colors(val)
        self.label.color = fg_c
        self._bg_col.rgba = bg_c
        self.width = self.label.width + 16

    def _update(self, *args):
        self.width = self.label.width + 16
        if hasattr(self, "_rect"):
            self._rect.pos = self.pos
            self._rect.size = self.size
            self._rect.radius = [self.radius]
