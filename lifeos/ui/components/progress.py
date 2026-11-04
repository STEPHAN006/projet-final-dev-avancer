"""Progress Bars and Circular Gauges for Atelier OS."""

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.properties import NumericProperty, ListProperty
from lifeos.ui.theme import GOLD, BORDER_COLOR, TEXT_PRIMARY, BG_CARD

class AtelierProgressBar(Widget):
    value = NumericProperty(0) # 0 to 100
    track_color = ListProperty(BORDER_COLOR)
    progress_color = ListProperty(GOLD)
    bar_height = NumericProperty(5)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = self.bar_height
        self.bind(pos=self._update, size=self._update, value=self._update)
        with self.canvas:
            self._col_track = Color(rgba=self.track_color)
            self._track = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.bar_height / 2])
            self._col_prog = Color(rgba=self.progress_color)
            self._prog = RoundedRectangle(pos=self.pos, size=(0, self.height), radius=[self.bar_height / 2])

    def _update(self, *args):
        if hasattr(self, "_track"):
            self._col_track.rgba = self.track_color
            self._col_prog.rgba = self.progress_color
            self._track.pos = self.pos
            self._track.size = (self.width, self.bar_height)
            self._track.radius = [self.bar_height / 2]

            prog_width = max(0, min(self.width, (self.value / 100.0) * self.width))
            self._prog.pos = self.pos
            self._prog.size = (prog_width, self.bar_height)
            self._prog.radius = [self.bar_height / 2]

class AtelierCircularProgress(BoxLayout):
    value = NumericProperty(70) # 0 to 100
    progress_color = ListProperty(GOLD)
    track_color = ListProperty(BORDER_COLOR)
    stroke_width = NumericProperty(7)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.label = Label(
            text=f"{int(self.value)}%",
            font_size="16sp",
            bold=True,
            color=TEXT_PRIMARY,
            halign="center",
            valign="middle"
        )
        self.add_widget(self.label)
        self.bind(pos=self._redraw, size=self._redraw, value=self._redraw)

    def _redraw(self, *args):
        self.label.text = f"{int(self.value)}%"
        self.canvas.before.clear()
        with self.canvas.before:
            d = min(self.width, self.height) - self.stroke_width * 2
            x = self.center_x - d / 2
            y = self.center_y - d / 2

            # Background circle track
            Color(rgba=self.track_color)
            Line(ellipse=(x, y, d, d), width=self.stroke_width)

            # Active arc
            angle = (self.value / 100.0) * 360.0
            if angle > 0:
                Color(rgba=self.progress_color)
                Line(ellipse=(x, y, d, d, 0, angle), width=self.stroke_width, cap="round")
