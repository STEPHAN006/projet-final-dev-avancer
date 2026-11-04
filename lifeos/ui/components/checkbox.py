"""Atelier OS Custom Checkbox Component."""

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import BooleanProperty, ListProperty, NumericProperty
from lifeos.ui.theme import GOLD, BORDER_COLOR, BG_CARD

class AtelierCheckbox(ButtonBehavior, BoxLayout):
    active = BooleanProperty(False)
    active_color = ListProperty(GOLD)
    inactive_border = ListProperty(BORDER_COLOR)
    size_box = NumericProperty(22)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (self.size_box, self.size_box)
        self.bind(pos=self._redraw, size=self._redraw, active=self._redraw)

    def on_release(self):
        self.active = not self.active
        super().on_release()

    def _redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            x, y = self.pos
            s = self.size_box
            radius = 6

            if self.active:
                # Solid gold fill
                Color(rgba=self.active_color)
                RoundedRectangle(pos=(x, y), size=(s, s), radius=[radius])

                # Dark checkmark mark inside
                Color(0.06, 0.07, 0.08, 1.0)
                Line(points=[
                    x + s * 0.25, y + s * 0.50,
                    x + s * 0.45, y + s * 0.28,
                    x + s * 0.78, y + s * 0.72
                ], width=2.0, cap="round", joint="round")
            else:
                # Idle state: transparent background with subtle border
                Color(rgba=self.inactive_border)
                Line(rounded_rectangle=(x, y, s, s, radius), width=1.4)
