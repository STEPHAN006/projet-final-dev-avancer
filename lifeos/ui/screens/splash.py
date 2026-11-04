"""Splash Screen for LifeOS (Shadcn / React Native style)."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivymd.uix.label import MDIcon
from lifeos.ui.theme import theme
from lifeos.ui.components.buttons import AtelierButton
from lifeos.core.events import bus

class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._bg_col = Color(rgba=theme.bg_canvas)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

        layout = BoxLayout(
            orientation="vertical",
            spacing=16,
            padding=[32, 64, 32, 64]
        )

        # Brand Icon Container
        icon_wrapper = BoxLayout(size_hint=(None, None), size=(72, 72), pos_hint={"center_x": 0.5})
        with icon_wrapper.canvas.before:
            self._iw_col = Color(theme.primary[0], theme.primary[1], theme.primary[2], 0.12)
            self._iw_rect = RoundedRectangle(pos=icon_wrapper.pos, size=icon_wrapper.size, radius=[20])
        icon_wrapper.bind(pos=lambda *_: setattr(self._iw_rect, "pos", icon_wrapper.pos),
                          size=lambda *_: setattr(self._iw_rect, "size", icon_wrapper.size))

        self.brand_icon = MDIcon(
            icon="lightning-bolt",
            theme_text_color="Custom",
            text_color=theme.primary,
            font_size="40sp",
            halign="center",
            valign="middle"
        )
        icon_wrapper.add_widget(self.brand_icon)
        layout.add_widget(icon_wrapper)

        # Title and Slogan
        self.lbl_title = Label(
            text="LifeOS",
            font_size="32sp",
            bold=True,
            color=theme.text_primary,
            size_hint_y=0.1
        )
        self.lbl_sub = Label(
            text="PERSONAL PRODUCTIVITY OS",
            font_size="11sp",
            bold=True,
            color=theme.primary,
            size_hint_y=0.08
        )
        self.lbl_desc = Label(
            text="Système personnel moderne et souverain.\n100% Hors-ligne · Haute Précision · Minimaliste",
            font_size="13sp",
            color=theme.text_secondary,
            halign="center",
            size_hint_y=0.15
        )
        layout.add_widget(self.lbl_title)
        layout.add_widget(self.lbl_sub)
        layout.add_widget(self.lbl_desc)

        # Spacer
        layout.add_widget(BoxLayout(size_hint_y=0.15))

        # Enter Button
        btn_enter = AtelierButton(
            text="Entrer dans le Sanctuaire",
            size_hint_y=None,
            height=50
        )
        btn_enter.bind(on_release=self._enter_sanctuary)
        layout.add_widget(btn_enter)

        self.add_widget(layout)

        bus.subscribe("theme_changed", self._on_theme)

    def _on_theme(self, *args, **kwargs):
        self._bg_col.rgba = theme.bg_canvas
        self.lbl_title.color = theme.text_primary
        self.lbl_sub.color = theme.primary
        self.lbl_desc.color = theme.text_secondary
        self._iw_col.rgba = [theme.primary[0], theme.primary[1], theme.primary[2], 0.12]
        self.brand_icon.text_color = theme.primary

    def _update(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _enter_sanctuary(self, *args):
        if self.manager:
            self.manager.current = "dashboard"
