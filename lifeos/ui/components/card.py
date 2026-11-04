"""Shadcn / React Native Card Component for LifeOS."""

from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import ListProperty, NumericProperty, BooleanProperty
from lifeos.ui.theme import theme
from lifeos.core.events import bus

class AtelierCard(BoxLayout):
    bg_color = ListProperty([])
    border_color = ListProperty([])
    radius = NumericProperty(12)
    has_border = BooleanProperty(True)

    def __init__(self, **kwargs):
        if "bg_color" not in kwargs:
            kwargs["bg_color"] = theme.bg_card
        if "border_color" not in kwargs:
            kwargs["border_color"] = theme.border

        super().__init__(**kwargs)
        self.bind(pos=self._update_rect, size=self._update_rect, bg_color=self._update_rect, border_color=self._update_rect)

        with self.canvas.before:
            self._color_instr = Color(rgba=self.bg_color)
            self._rect_instr = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            if self.has_border:
                self._border_color_instr = Color(rgba=self.border_color)
                self._line_instr = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius), width=1.0)

        bus.subscribe("theme_changed", self._on_theme_changed)

    def _on_theme_changed(self, *args, **kwargs):
        self.bg_color = theme.bg_card
        self.border_color = theme.border
        self._update_rect()

    def _update_rect(self, *args):
        if hasattr(self, "_rect_instr"):
            self._color_instr.rgba = self.bg_color
            self._rect_instr.pos = self.pos
            self._rect_instr.size = self.size
            self._rect_instr.radius = [self.radius]
            if self.has_border and hasattr(self, "_line_instr"):
                self._border_color_instr.rgba = self.border_color
                self._line_instr.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)
