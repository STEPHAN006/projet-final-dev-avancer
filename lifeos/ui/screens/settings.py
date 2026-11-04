"""Settings & Offline Sovereignty Screen for LifeOS."""

import json
from pathlib import Path
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivymd.uix.button import MDIconButton
from lifeos.ui.theme import (
    BG_CANVAS, BG_CARD, BG_CARD_HOVER, BORDER_COLOR,
    GOLD, CHAMPAGNE, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, SUCCESS, WARNING, ERROR
)
from lifeos.ui.components.card import AtelierCard
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton, AtelierBadge
from lifeos.ui.components.checkbox import AtelierCheckbox
from lifeos.ui.components.navigation import AtelierTopBar, AtelierBottomNav
from lifeos.ui.components.dialogs import StyledInput
from lifeos.services.data_service import ds
from lifeos.core.config import DATA_DIR
from lifeos.core.events import bus

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(rgba=BG_CANVAS)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar
        self.top_bar = AtelierTopBar(
            title="Paramètres",
            subtitle="PRÉFÉRENCES & SOUVERAINETÉ"
        )
        self.root_box.add_widget(self.top_bar)

        # Scrollview
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(
            orientation="vertical",
            spacing=14,
            padding=[16, 14, 16, 24],
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)
        self.root_box.add_widget(self.scroll)

        # Bottom Nav
        self.bottom_nav = AtelierBottomNav(
            current_tab="modules",
            nav_callback=self._handle_navigation
        )
        self.root_box.add_widget(self.bottom_nav)

        self.add_widget(self.root_box)

        self.refresh_settings()

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_pre_enter(self):
        self.bottom_nav.set_tab("modules")
        self.refresh_settings()

    def _handle_navigation(self, route):
        if self.manager and route != "settings":
            self.manager.current = route

    def refresh_settings(self):
        self.content.clear_widgets()

        user_name = ds.settings.get_setting("user_name", "Thomas V.")
        theme_mode = ds.settings.get_setting("theme_mode", "dark")
        focus_dur = ds.settings.get_setting("focus_duration", "25")
        sound_enabled = ds.settings.get_setting("sound_enabled", "1") == "1"
        notif_enabled = ds.settings.get_setting("notif_enabled", "1") == "1"

        # 1. Profile / Identity Section
        self._add_section_title("1. IDENTITÉ & PROFIL")
        card_profile = AtelierCard(
            orientation="vertical",
            spacing=10,
            padding=[14, 12, 14, 12],
            size_hint_y=None,
            height=96
        )
        lbl_p_title = Label(
            text="Nom d'affichage du sanctuaire",
            font_size="13sp",
            bold=True,
            color=TEXT_PRIMARY,
            halign="left",
            size_hint_y=None,
            height=20
        )
        lbl_p_title.bind(size=lbl_p_title.setter("text_size"))
        card_profile.add_widget(lbl_p_title)

        row_p = BoxLayout(spacing=10, size_hint_y=None, height=42)
        in_name = StyledInput(text=user_name, hint_text="Votre nom...", size_hint_x=0.7)
        btn_save_name = AtelierButton(text="Sauvegarder", font_size="11sp", size_hint_x=0.3)

        def _save_name(*_):
            val = in_name.text.strip()
            if val:
                ds.settings.set_setting("user_name", val)
                btn_save_name.text = "✓ Enregistré"

        btn_save_name.bind(on_release=_save_name)
        row_p.add_widget(in_name)
        row_p.add_widget(btn_save_name)
        card_profile.add_widget(row_p)
        self.content.add_widget(card_profile)

        # 2. Appearance Section
        self._add_section_title("2. APPARENCE & THÈME")
        card_app = AtelierCard(
            orientation="vertical",
            spacing=10,
            padding=[14, 12, 14, 12],
            size_hint_y=None,
            height=110
        )
        lbl_a1 = Label(text="Thème visuel actif", font_size="13sp", bold=True, color=TEXT_PRIMARY, halign="left", size_hint_y=None, height=20)
        lbl_a1.bind(size=lbl_a1.setter("text_size"))
        card_app.add_widget(lbl_a1)

        row_thm = BoxLayout(spacing=8, size_hint_y=None, height=36)
        btn_thm1 = AtelierButton(text="Atelier Noir (OLED)", font_size="10sp", size_hint_x=0.5)
        btn_thm2 = AtelierGhostButton(text="Minimal Clair", font_size="10sp", size_hint_x=0.5)
        row_thm.add_widget(btn_thm1)
        row_thm.add_widget(btn_thm2)
        card_app.add_widget(row_thm)

        lbl_a_desc = Label(
            text="Palette optimisée #101114 avec micro-accents or et champagne.",
            font_size="10sp",
            color=TEXT_MUTED,
            halign="left",
            size_hint_y=None,
            height=18
        )
        lbl_a_desc.bind(size=lbl_a_desc.setter("text_size"))
        card_app.add_widget(lbl_a_desc)
        self.content.add_widget(card_app)

        # 3. Focus & Pomodoro Settings
        self._add_section_title("3. FOCUS & POMODORO")
        card_foc = AtelierCard(
            orientation="vertical",
            spacing=10,
            padding=[14, 12, 14, 12],
            size_hint_y=None,
            height=120
        )
        lbl_f_title = Label(text="Durée de concentration par défaut", font_size="13sp", bold=True, color=TEXT_PRIMARY, halign="left", size_hint_y=None, height=20)
        lbl_f_title.bind(size=lbl_f_title.setter("text_size"))
        card_foc.add_widget(lbl_f_title)

        row_f_dur = BoxLayout(spacing=6, size_hint_y=None, height=34)
        for dur in ["15", "25", "50", "90"]:
            is_active = (dur == focus_dur)
            b = AtelierButton(text=f"{dur} min", font_size="10sp", size_hint_x=0.25) if is_active else AtelierGhostButton(text=f"{dur} min", font_size="10sp", size_hint_x=0.25)
            b.bind(on_release=lambda _, d=dur: self._set_focus_dur(d))
            row_f_dur.add_widget(b)
        card_foc.add_widget(row_f_dur)

        row_sound = BoxLayout(spacing=10, size_hint_y=None, height=30)
        cb_sound = AtelierCheckbox(active=sound_enabled, size_box=20)
        cb_sound.bind(on_release=lambda _: ds.settings.set_setting("sound_enabled", "0" if sound_enabled else "1"))
        lbl_snd = Label(text="Sons & vibrations haptiques de clôture", font_size="12sp", color=TEXT_PRIMARY, halign="left")
        lbl_snd.bind(size=lbl_snd.setter("text_size"))
        row_sound.add_widget(cb_sound)
        row_sound.add_widget(lbl_snd)
        card_foc.add_widget(row_sound)

        self.content.add_widget(card_foc)

        # 4. Notifications Locales
        self._add_section_title("4. NOTIFICATIONS LOCALES")
        card_notif = AtelierCard(
            orientation="vertical",
            spacing=8,
            padding=[14, 12, 14, 12],
            size_hint_y=None,
            height=72
        )
        row_n = BoxLayout(spacing=10, size_hint_y=None, height=30)
        cb_notif = AtelierCheckbox(active=notif_enabled, size_box=20)
        cb_notif.bind(on_release=lambda _: ds.settings.set_setting("notif_enabled", "0" if notif_enabled else "1"))
        lbl_n = Label(text="Rappels quotidiens (21h30 bilan & checklist)", font_size="12sp", color=TEXT_PRIMARY, halign="left")
        lbl_n.bind(size=lbl_n.setter("text_size"))
        row_n.add_widget(cb_notif)
        row_n.add_widget(lbl_n)
        card_notif.add_widget(row_n)

        lbl_n_sub = Label(text="Daemon d'alerte 100% interne, aucun appel réseau.", font_size="10sp", color=TEXT_MUTED, halign="left", size_hint_y=None, height=18)
        lbl_n_sub.bind(size=lbl_n_sub.setter("text_size"))
        card_notif.add_widget(lbl_n_sub)
        self.content.add_widget(card_notif)

        # 5. SQLite Data Sovereignty & Backups
        self._add_section_title("5. GESTION DES DONNÉES & SOUVERAINETÉ")
        card_db = AtelierCard(
            orientation="vertical",
            spacing=10,
            padding=[14, 12, 14, 12],
            size_hint_y=None,
            height=160
        )
        lbl_db_info = Label(
            text="Base SQLite Locale · Mode WAL actif · Zero-Cloud",
            font_size="12sp",
            bold=True,
            color=GOLD,
            halign="left",
            size_hint_y=None,
            height=20
        )
        lbl_db_info.bind(size=lbl_db_info.setter("text_size"))
        card_db.add_widget(lbl_db_info)

        self.lbl_backup_status = Label(
            text="Toutes vos données résident uniquement sur votre appareil.",
            font_size="11sp",
            color=TEXT_SECONDARY,
            halign="left",
            size_hint_y=None,
            height=20
        )
        self.lbl_backup_status.bind(size=self.lbl_backup_status.setter("text_size"))
        card_db.add_widget(self.lbl_backup_status)

        row_db_actions = BoxLayout(spacing=10, size_hint_y=None, height=42)

        btn_export = AtelierButton(text="📥 Exporter JSON", font_size="11sp", size_hint_x=0.5)
        btn_export.bind(on_release=lambda _: self._export_backup())

        btn_reset = AtelierGhostButton(text="↺ Données Seed", font_size="11sp", size_hint_x=0.5)
        btn_reset.bind(on_release=lambda _: self._reset_seed())

        row_db_actions.add_widget(btn_export)
        row_db_actions.add_widget(btn_reset)
        card_db.add_widget(row_db_actions)

        self.content.add_widget(card_db)

        # Version footer
        lbl_ver = Label(
            text="LifeOS v1.0.0 · Atelier Executive System · Linux & Android",
            font_size="10sp",
            color=TEXT_MUTED,
            halign="center",
            size_hint_y=None,
            height=30
        )
        self.content.add_widget(lbl_ver)

    def _add_section_title(self, text):
        lbl = Label(
            text=text,
            font_size="11sp",
            bold=True,
            color=GOLD,
            halign="left",
            size_hint_y=None,
            height=26
        )
        lbl.bind(size=lbl.setter("text_size"))
        self.content.add_widget(lbl)

    def _set_focus_dur(self, dur):
        ds.settings.set_setting("focus_duration", dur)
        self.refresh_settings()

    def _export_backup(self):
        backup = ds.settings.export_full_backup()
        export_file = DATA_DIR / "backup_lifeos.json"
        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(backup, f, indent=2, ensure_ascii=False)
        self.lbl_backup_status.text = f"✓ Sauvegarde exportée : {export_file.name}"
        self.lbl_backup_status.color = SUCCESS

    def _reset_seed(self):
        ds.settings.reset_to_seed()
        self.lbl_backup_status.text = "✓ Base réinitialisée avec les données de départ"
        self.lbl_backup_status.color = GOLD
        self.refresh_settings()
