"""Atelier OS Buttons and Badges."""

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import ListProperty, NumericProperty, StringProperty, BooleanProperty
from kivymd.uix.button import MDIconButton
from lifeos.ui.theme import (
    GOLD, CHAMPAGNE, BG_CARD, BG_CARD_HOVER, BORDER_COLOR,
    TEXT_PRIMARY, TEXT_SECONDARY, PRIORITY_COLOR_MAP
)

class AtelierButton(Button):
    bg_color = ListProperty(GOLD)
    border_color = ListProperty(GOLD)
    text_color = ListProperty([0.06, 0.07, 0.08, 1.0]) # Deep obsidian text
    radius = NumericProperty(10)

    def __init__(self, **kwargs):
        kwargs.setdefault("background_color", [0, 0, 0, 0])
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("bold", True)
        super().__init__(**kwargs)
        self.color = self.text_color
        self.bind(pos=self._update, size=self._update, state=self._on_state)
        with self.canvas.before:
            self._col = Color(rgba=self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])

    def _on_state(self, instance, value):
        if value == "down":
            self._col.rgba = CHAMPAGNE
        else:
            self._col.rgba = self.bg_color

    def _update(self, *args):
        if hasattr(self, "_rect"):
            self._rect.pos = self.pos
            self._rect.size = self.size
            self._rect.radius = [self.radius]

class AtelierGhostButton(Button):
    bg_color = ListProperty([0, 0, 0, 0])
    border_color = ListProperty(BORDER_COLOR)
    text_color = ListProperty(TEXT_PRIMARY)
    radius = NumericProperty(10)

    def __init__(self, **kwargs):
        kwargs.setdefault("background_color", [0, 0, 0, 0])
        kwargs.setdefault("background_normal", "")
        super().__init__(**kwargs)
        self.color = self.text_color
        self.bind(pos=self._update, size=self._update, state=self._on_state)
        with self.canvas.before:
            self._col = Color(rgba=self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self._line_col = Color(rgba=self.border_color)
            self._line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius), width=1.1)

    def _on_state(self, instance, value):
        if value == "down":
            self._col.rgba = BG_CARD_HOVER
            self._line_col.rgba = GOLD
        else:
            self._col.rgba = self.bg_color
            self._line_col.rgba = self.border_color

    def _update(self, *args):
        if hasattr(self, "_rect"):
            self._rect.pos = self.pos
            self._rect.size = self.size
            self._rect.radius = [self.radius]
            self._line.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)

class AtelierBadge(BoxLayout):
    text = StringProperty("MEDIUM")
    badge_color = ListProperty(GOLD)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.height = 24
        self.padding = [8, 2, 8, 2]
        self.radius = 12

        self.label = Label(
            text=self.text.upper(),
            font_size="10sp",
            bold=True,
            color=self.badge_color,
            size_hint=(None, None),
            height=20
        )
        self.label.bind(texture_size=lambda _, sz: setattr(self.label, 'width', sz[0]))
        self.bind(text=self._on_text_change)
        self.add_widget(self.label)
        self.bind(pos=self._update, size=self._update)

        with self.canvas.before:
            # subtle semi-transparent background
            self._bg_col = Color(self.badge_color[0], self.badge_color[1], self.badge_color[2], 0.15)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self._line_col = Color(self.badge_color[0], self.badge_color[1], self.badge_color[2], 0.4)
            self._line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius), width=1.0)

    def _on_text_change(self, instance, val):
        self.label.text = val.upper()
        col = PRIORITY_COLOR_MAP.get(val.upper(), GOLD)
        self.badge_color = col
        self.label.color = col
        self._bg_col.rgba = [col[0], col[1], col[2], 0.15]
        self._line_col.rgba = [col[0], col[1], col[2], 0.4]
        self.width = self.label.width + 16

    def _update(self, *args):
        self.width = self.label.width + 16
        if hasattr(self, "_rect"):
            self._rect.pos = self.pos
            self._rect.size = self.size
            self._line.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)
