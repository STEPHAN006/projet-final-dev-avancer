"""Calendar & Events Screen for LifeOS (Shadcn / React Native style)."""

from datetime import date, datetime, timedelta
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivymd.uix.button import MDIconButton
from lifeos.ui.theme import theme
from lifeos.ui.components.card import AtelierCard
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton
from lifeos.ui.components.navigation import AtelierTopBar, AtelierBottomNav
from lifeos.ui.components.dialogs import ShadcnInput
from lifeos.services.data_service import ds
from lifeos.core.events import bus

class CalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_date = date.today()

        with self.canvas.before:
            self._bg_col = Color(rgba=theme.bg_canvas)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar
        self.top_bar = AtelierTopBar(
            title="Calendrier",
            subtitle="Blocs & Événements",
            right_icon="plus",
            right_action=self._open_add_event_dialog
        )
        self.root_box.add_widget(self.top_bar)

        # Date Navigator Row
        nav_date_row = BoxLayout(spacing=8, padding=[16, 8, 16, 6], size_hint_y=None, height=44)

        btn_prev = MDIconButton(
            icon="chevron-left",
            theme_icon_color="Custom",
            icon_color=theme.text_primary,
            size_hint=(None, None),
            size=(36, 36)
        )
        btn_prev.bind(on_release=lambda _: self._shift_day(-1))

        self.lbl_current_day = Label(
            text="",
            font_size="14sp",
            bold=True,
            color=theme.primary,
            halign="center"
        )

        btn_today = AtelierGhostButton(text="Aujourd'hui", font_size="11sp", size_hint=(None, None), size=(84, 32))
        btn_today.bind(on_release=lambda _: self._go_today())

        btn_next = MDIconButton(
            icon="chevron-right",
            theme_icon_color="Custom",
            icon_color=theme.text_primary,
            size_hint=(None, None),
            size=(36, 36)
        )
        btn_next.bind(on_release=lambda _: self._shift_day(1))

        nav_date_row.add_widget(btn_prev)
        nav_date_row.add_widget(self.lbl_current_day)
        nav_date_row.add_widget(btn_today)
        nav_date_row.add_widget(btn_next)
        self.root_box.add_widget(nav_date_row)

        # Events ScrollView
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.events_box = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=[16, 8, 16, 20],
            size_hint_y=None
        )
        self.events_box.bind(minimum_height=self.events_box.setter("height"))
        self.scroll.add_widget(self.events_box)
        self.root_box.add_widget(self.scroll)

        # Bottom Nav
        self.bottom_nav = AtelierBottomNav(
            current_tab="calendar",
            nav_callback=self._handle_navigation
        )
        self.root_box.add_widget(self.bottom_nav)

        self.add_widget(self.root_box)

        bus.subscribe("calendar_updated", lambda *_: self.refresh_events())
        bus.subscribe("theme_changed", self._on_theme)

        self._update_date_label()
        self.refresh_events()

    def _on_theme(self, *args, **kwargs):
        self._bg_col.rgba = theme.bg_canvas
        self.lbl_current_day.color = theme.primary
        self.refresh_events()

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_pre_enter(self):
        self.bottom_nav.set_tab("calendar")
        self.refresh_events()

    def _handle_navigation(self, route):
        if self.manager and route != "calendar":
            self.manager.current = route

    def _shift_day(self, delta):
        self.selected_date += timedelta(days=delta)
        self._update_date_label()
        self.refresh_events()

    def _go_today(self):
        self.selected_date = date.today()
        self._update_date_label()
        self.refresh_events()

    def _update_date_label(self):
        self.lbl_current_day.text = self.selected_date.strftime("%A %d %B %Y").capitalize()

    def refresh_events(self):
        self.events_box.clear_widgets()
        date_str = self.selected_date.isoformat()
        events = ds.calendar.get_events_for_date(date_str)

        if not events:
            tasks_due = ds.tasks.list_tasks(filter_status="today")
            empty_box = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None, height=120)
            empty_box.add_widget(Label(
                text="Aucun événement bloqué pour ce jour.",
                font_size="13sp",
                color=theme.text_muted,
                halign="center"
            ))
            if tasks_due:
                empty_box.add_widget(Label(
                    text=f"{len(tasks_due)} tâche(s) planifiée(s) aujourd'hui.",
                    font_size="12sp",
                    color=theme.primary,
                    halign="center"
                ))
            self.events_box.add_widget(empty_box)
            return

        for ev in events:
            card = AtelierCard(
                orientation="horizontal",
                spacing=14,
                padding=[14, 12, 14, 12],
                size_hint_y=None,
                height=72
            )

            # Time Block
            time_col = BoxLayout(orientation="vertical", size_hint=(None, 1), width=80)
            lbl_time = Label(
                text=f"{ev['start_time']}\n{ev['end_time']}",
                font_size="12sp",
                bold=True,
                color=theme.primary,
                halign="center"
            )
            time_col.add_widget(lbl_time)
            card.add_widget(time_col)

            # Content
            content_col = BoxLayout(orientation="vertical", spacing=2)
            lbl_title = Label(
                text=ev["title"],
                font_size="14sp",
                bold=True,
                color=theme.text_primary,
                halign="left"
            )
            lbl_title.bind(size=lbl_title.setter("text_size"))

            loc = ev.get("location") or "Sanctuaire"
            lbl_sub = Label(
                text=f"Lieu: {loc}  ·  {ev.get('event_type', 'bloc').upper()}",
                font_size="11sp",
                color=theme.text_secondary,
                halign="left"
            )
            lbl_sub.bind(size=lbl_sub.setter("text_size"))

            content_col.add_widget(lbl_title)
            content_col.add_widget(lbl_sub)
            card.add_widget(content_col)

            # Delete button
            btn_del = MDIconButton(
                icon="close",
                theme_icon_color="Custom",
                icon_color=theme.text_muted,
                size_hint=(None, None),
                size=(32, 32),
                pos_hint={"center_y": 0.5}
            )
            btn_del.bind(on_release=lambda _, eid=ev["id"]: ds.calendar.delete_event(eid))
            card.add_widget(btn_del)

            self.events_box.add_widget(card)

    def _open_add_event_dialog(self):
        dialog = ModalView(size_hint=(0.9, None), height=360, auto_dismiss=True, background_color=[0, 0, 0, 0.55])
        box = BoxLayout(orientation="vertical", spacing=12, padding=18)
        with box.canvas.before:
            Color(rgba=theme.bg_surface)
            self._d_rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[14])
            Color(rgba=theme.border)
            self._d_line = Line(rounded_rectangle=(box.x, box.y, box.width, box.height, 14), width=1.0)
        box.bind(pos=lambda *_: setattr(self._d_rect, "pos", box.pos), size=lambda *_: setattr(self._d_rect, "size", box.size))

        box.add_widget(Label(text="Ajouter un Événement", font_size="17sp", bold=True, color=theme.text_primary, size_hint_y=None, height=26))

        in_title = ShadcnInput(hint_text="Titre (ex: Deep Work Algo)...", size_hint_y=None, height=42)
        box.add_widget(in_title)

        row_time = BoxLayout(spacing=10, size_hint_y=None, height=42)
        in_start = ShadcnInput(text="14:00", hint_text="Début", size_hint_x=0.5)
        in_end = ShadcnInput(text="15:30", hint_text="Fin", size_hint_x=0.5)
        row_time.add_widget(in_start)
        row_time.add_widget(in_end)
        box.add_widget(row_time)

        in_loc = ShadcnInput(hint_text="Lieu (ex: Amphi B / Bureau)...", size_hint_y=None, height=42)
        box.add_widget(in_loc)

        row_btns = BoxLayout(spacing=10, size_hint_y=None, height=44)
        btn_c = AtelierGhostButton(text="Annuler", size_hint_x=0.45)
        btn_c.bind(on_release=lambda _: dialog.dismiss())
        btn_ok = AtelierButton(text="Confirmer", size_hint_x=0.55)

        def _create(*_):
            t = in_title.text.strip()
            if t:
                ds.calendar.create_event(
                    title=t,
                    date_str=self.selected_date.isoformat(),
                    start_time=in_start.text.strip() or "10:00",
                    end_time=in_end.text.strip() or "11:00",
                    location=in_loc.text.strip()
                )
            dialog.dismiss()

        btn_ok.bind(on_release=_create)
        row_btns.add_widget(btn_c)
        row_btns.add_widget(btn_ok)
        box.add_widget(row_btns)

        dialog.add_widget(box)
        dialog.open()
