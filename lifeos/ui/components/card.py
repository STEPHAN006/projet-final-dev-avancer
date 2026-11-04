"""Atelier OS Card Component."""

from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import ListProperty, NumericProperty, BooleanProperty
from lifeos.ui.theme import BG_CARD, BG_CARD_HOVER, BORDER_COLOR

class AtelierCard(BoxLayout):
    bg_color = ListProperty(BG_CARD)
    border_color = ListProperty(BORDER_COLOR)
    radius = NumericProperty(14)
    has_border = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._update_rect, size=self._update_rect, bg_color=self._update_rect)
        with self.canvas.before:
            self._color_instr = Color(rgba=self.bg_color)
            self._rect_instr = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            if self.has_border:
                self._border_color_instr = Color(rgba=self.border_color)
                self._line_instr = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius), width=1.1)

    def _update_rect(self, *args):
        if hasattr(self, "_rect_instr"):
            self._color_instr.rgba = self.bg_color
            self._rect_instr.pos = self.pos
            self._rect_instr.size = self.size
            self._rect_instr.radius = [self.radius]
            if self.has_border and hasattr(self, "_line_instr"):
                self._border_color_instr.rgba = self.border_color
                self._line_instr.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)
