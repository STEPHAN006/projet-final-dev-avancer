"""Splash Screen for LifeOS."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from lifeos.ui.theme import BG_CANVAS, GOLD, CHAMPAGNE, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED
from lifeos.ui.components.buttons import AtelierButton

class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(rgba=BG_CANVAS)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

        layout = BoxLayout(
            orientation="vertical",
            spacing=16,
            padding=[32, 64, 32, 64]
        )

        # Monogram
        self.lbl_logo = Label(
            text="Ω",
            font_size="64sp",
            bold=True,
            color=GOLD,
            size_hint_y=0.3
        )
        layout.add_widget(self.lbl_logo)

        # Title and Slogan
        lbl_title = Label(
            text="LifeOS",
            font_size="32sp",
            bold=True,
            color=TEXT_PRIMARY,
            size_hint_y=0.1
        )
        lbl_sub = Label(
            text="EXECUTIVE SANCTUARY",
            font_size="12sp",
            color=GOLD,
            size_hint_y=0.08
        )
        lbl_desc = Label(
            text="Espace personnel de productivité souveraine.\n100% Hors-ligne · Haute Précision · Minimaliste",
            font_size="13sp",
            color=TEXT_SECONDARY,
            halign="center",
            size_hint_y=0.15
        )
        layout.add_widget(lbl_title)
        layout.add_widget(lbl_sub)
        layout.add_widget(lbl_desc)

        # Spacer
        layout.add_widget(BoxLayout(size_hint_y=0.15))

        # Enter Button
        btn_enter = AtelierButton(
            text="Entrer dans le Sanctuaire",
            size_hint_y=None,
            height=52
        )
        btn_enter.bind(on_release=self._enter_sanctuary)
        layout.add_widget(btn_enter)

        self.add_widget(layout)

    def _update(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _enter_sanctuary(self, *args):
        if self.manager:
            self.manager.current = "dashboard"
