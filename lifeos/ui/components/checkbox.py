"""Shadcn Style Modern Checkbox Component."""

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import BooleanProperty, ListProperty, NumericProperty
from lifeos.ui.theme import theme
from lifeos.core.events import bus

class AtelierCheckbox(ButtonBehavior, BoxLayout):
    active = BooleanProperty(False)
    size_box = NumericProperty(20)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (self.size_box, self.size_box)
        self.bind(pos=self._redraw, size=self._redraw, active=self._redraw)
        bus.subscribe("theme_changed", lambda *_: self._redraw())

    def on_release(self):
        self.active = not self.active
        super().on_release()

    def _redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            x, y = self.pos
            s = self.size_box
            radius = 5

            if self.active:
                # Active: Solid primary fill (Electric Blue)
                Color(rgba=theme.primary)
                RoundedRectangle(pos=(x, y), size=(s, s), radius=[radius])

                # Clean crisp white checkmark
                Color(1.0, 1.0, 1.0, 1.0)
                Line(points=[
                    x + s * 0.22, y + s * 0.50,
                    x + s * 0.42, y + s * 0.26,
                    x + s * 0.80, y + s * 0.74
                ], width=2.0, cap="round", joint="round")
            else:
                # Inactive: Subtle surface bg with crisp border
                Color(rgba=theme.bg_surface)
                RoundedRectangle(pos=(x, y), size=(s, s), radius=[radius])
                Color(rgba=theme.border)
                Line(rounded_rectangle=(x, y, s, s, radius), width=1.4)
