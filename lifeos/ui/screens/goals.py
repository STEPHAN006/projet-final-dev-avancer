"""Goals & Milestones Screen for LifeOS (Shadcn / React Native style)."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDIconButton
from lifeos.ui.theme import theme
from lifeos.ui.components.card import AtelierCard
from lifeos.ui.components.buttons import AtelierButton, AtelierGhostButton, AtelierBadge
from lifeos.ui.components.checkbox import AtelierCheckbox
from lifeos.ui.components.progress import AtelierProgressBar
from lifeos.ui.components.navigation import AtelierTopBar, AtelierBottomNav
from lifeos.ui.components.dialogs import AddGoalDialog
from lifeos.services.data_service import ds
from lifeos.core.events import bus

class GoalCard(AtelierCard):
    def __init__(self, goal, on_toggle_ms=None, on_delete=None, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("spacing", 10)
        kwargs.setdefault("padding", [16, 14, 16, 14])
        kwargs.setdefault("size_hint_y", None)
        super().__init__(**kwargs)

        self.goal = goal
        self.on_toggle_ms = on_toggle_ms

        # Top row: Category tag, Target Date, Status Badge, Delete
        top_row = BoxLayout(size_hint_y=None, height=26)
        cat_badge = AtelierBadge(text=goal.get("category", "Dev"))
        top_row.add_widget(cat_badge)

        date_str = goal.get("target_date") or "Sans date"
        lbl_date = Label(
            text=f"Échéance: {date_str}",
            font_size="11sp",
            color=theme.text_secondary,
            halign="left"
        )
        lbl_date.bind(size=lbl_date.setter("text_size"))
        top_row.add_widget(lbl_date)

        is_completed = goal.get("status") == "completed" or goal.get("progress", 0) >= 100
        st_text = "ACCOMPLI" if is_completed else "EN COURS"
        st_badge = AtelierBadge(text=st_text)
        top_row.add_widget(st_badge)

        if on_delete:
            btn_del = MDIconButton(
                icon="delete-outline",
                theme_icon_color="Custom",
                icon_color=theme.text_muted,
                size_hint=(None, None),
                size=(28, 28)
            )
            btn_del.bind(on_release=lambda _: on_delete(goal["id"]))
            top_row.add_widget(btn_del)

        self.add_widget(top_row)

        # Title
        lbl_title = Label(
            text=goal["title"],
            font_size="15sp",
            bold=True,
            color=theme.text_primary,
            halign="left",
            size_hint_y=None,
            height=26
        )
        lbl_title.bind(size=lbl_title.setter("text_size"))
        self.add_widget(lbl_title)

        if goal.get("description"):
            lbl_desc = Label(
                text=goal["description"],
                font_size="11sp",
                color=theme.text_secondary,
                halign="left",
                size_hint_y=None,
                height=20
            )
            lbl_desc.bind(size=lbl_desc.setter("text_size"))
            self.add_widget(lbl_desc)

        # Progress bar
        prog = goal.get("progress", 0)
        prog_row = BoxLayout(spacing=10, size_hint_y=None, height=18)
        p_bar = AtelierProgressBar(value=prog, size_hint_x=0.8, pos_hint={"center_y": 0.5})
        lbl_pct = Label(text=f"{prog}%", font_size="11sp", bold=True, color=theme.primary, size_hint_x=0.2)
        prog_row.add_widget(p_bar)
        prog_row.add_widget(lbl_pct)
        self.add_widget(prog_row)

        # Milestones section
        milestones = goal.get("milestones", [])
        if milestones:
            ms_title = Label(
                text=f"Jalons Clés ({sum(1 for m in milestones if m.get('done'))}/{len(milestones)})",
                font_size="11sp",
                bold=True,
                color=theme.text_secondary,
                halign="left",
                size_hint_y=None,
                height=20
            )
            ms_title.bind(size=ms_title.setter("text_size"))
            self.add_widget(ms_title)

            for idx, ms in enumerate(milestones):
                m_row = BoxLayout(spacing=8, size_hint_y=None, height=28)
                cb = AtelierCheckbox(active=ms.get("done", False), size_box=18)
                cb.bind(on_release=lambda _, i=idx: self._on_ms_click(i))
                m_row.add_widget(cb)

                m_lbl = Label(
                    text=ms.get("title", ""),
                    font_size="12sp",
                    color=theme.text_muted if ms.get("done") else theme.text_primary,
                    halign="left"
                )
                m_lbl.bind(size=m_lbl.setter("text_size"))
                m_row.add_widget(m_lbl)
                self.add_widget(m_row)

        ms_count = len(milestones)
        self.height = 130 + (ms_count * 28 + 24 if ms_count > 0 else 0)

    def _on_ms_click(self, idx):
        if self.on_toggle_ms:
            self.on_toggle_ms(self.goal["id"], idx)


class GoalsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_category = "Tous"

        with self.canvas.before:
            self._bg_col = Color(rgba=theme.bg_canvas)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.root_box = BoxLayout(orientation="vertical")

        # Top Bar
        self.top_bar = AtelierTopBar(
            title="Objectifs & Jalons",
            subtitle="HORIZON STRATÉGIQUE",
            right_icon="plus-circle-outline",
            right_action=self._open_add_dialog
        )
        self.root_box.add_widget(self.top_bar)

        # Scrollview
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = BoxLayout(
            orientation="vertical",
            spacing=14,
            padding=[16, 14, 16, 20],
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

        bus.subscribe("goals_updated", lambda *_: self.refresh_goals())
        bus.subscribe("theme_changed", self._on_theme)

        self.refresh_goals()

    def _on_theme(self, *args, **kwargs):
        self._bg_col.rgba = theme.bg_canvas
        self.refresh_goals()

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_pre_enter(self):
        self.bottom_nav.set_tab("modules")
        self.refresh_goals()

    def _handle_navigation(self, route):
        if self.manager and route != "goals":
            self.manager.current = route

    def _open_add_dialog(self):
        dialog = AddGoalDialog(on_goal_created=lambda _: self.refresh_goals())
        dialog.open()

    def refresh_goals(self):
        self.content.clear_widgets()

        goals = ds.goals.list_goals()
        total = len(goals)
        active = sum(1 for g in goals if g.get("status") != "completed")
        completed = total - active
        global_pct = int(sum(g.get("progress", 0) for g in goals) / max(total, 1))

        # 1. Summary KPI Bento
        kpi_card = AtelierCard(
            orientation="vertical",
            spacing=8,
            padding=[16, 12, 16, 12],
            size_hint_y=None,
            height=86
        )
        kpi_head = Label(
            text="PORTFOLIO DES PRIORITÉS CARDINALES",
            font_size="10sp",
            bold=True,
            color=theme.text_secondary,
            halign="left",
            size_hint_y=None,
            height=16
        )
        kpi_head.bind(size=kpi_head.setter("text_size"))
        kpi_card.add_widget(kpi_head)

        grid = GridLayout(cols=4, spacing=8, size_hint_y=None, height=44)
        c1 = BoxLayout(orientation="vertical")
        c1.add_widget(Label(text=f"{total}", font_size="17sp", bold=True, color=theme.text_primary))
        c1.add_widget(Label(text="Total", font_size="10sp", color=theme.text_secondary))

        c2 = BoxLayout(orientation="vertical")
        c2.add_widget(Label(text=f"{active}", font_size="17sp", bold=True, color=theme.primary))
        c2.add_widget(Label(text="En cours", font_size="10sp", color=theme.text_secondary))

        c3 = BoxLayout(orientation="vertical")
        c3.add_widget(Label(text=f"{completed}", font_size="17sp", bold=True, color=theme.success))
        c3.add_widget(Label(text="Validés", font_size="10sp", color=theme.text_secondary))

        c4 = BoxLayout(orientation="vertical")
        c4.add_widget(Label(text=f"{global_pct}%", font_size="17sp", bold=True, color=theme.text_primary))
        c4.add_widget(Label(text="Accompli", font_size="10sp", color=theme.text_secondary))

        grid.add_widget(c1)
        grid.add_widget(c2)
        grid.add_widget(c3)
        grid.add_widget(c4)
        kpi_card.add_widget(grid)
        self.content.add_widget(kpi_card)

        # 2. Filter Pills Row
        filter_scroll = ScrollView(size_hint=(1, None), height=38, do_scroll_y=False)
        pills_box = BoxLayout(spacing=8, size_hint_x=None, padding=[2, 0, 2, 0])
        pills_box.bind(minimum_width=pills_box.setter("width"))

        categories = ["Tous", "Dev & Pro", "Académique", "Santé", "Personnel"]
        for cat in categories:
            is_sel = (cat == self.selected_category)
            if is_sel:
                btn = AtelierButton(text=cat, font_size="11sp", size_hint=(None, None), size=(90, 34))
            else:
                btn = AtelierGhostButton(text=cat, font_size="11sp", size_hint=(None, None), size=(90, 34))
            btn.bind(on_release=lambda _, c=cat: self._set_category(c))
            pills_box.add_widget(btn)

        filter_scroll.add_widget(pills_box)
        self.content.add_widget(filter_scroll)

        # 3. Filtered Goals Cards
        filtered_goals = goals if self.selected_category == "Tous" else [
            g for g in goals if g.get("category", "") == self.selected_category
        ]

        if not filtered_goals:
            self.content.add_widget(Label(
                text="Aucun objectif dans cette catégorie.",
                font_size="13sp",
                color=theme.text_muted,
                size_hint_y=None,
                height=40
            ))
        else:
            for g in filtered_goals:
                card = GoalCard(
                    goal=g,
                    on_toggle_ms=lambda gid, idx: ds.goals.toggle_milestone(gid, idx),
                    on_delete=lambda gid: ds.goals.delete_goal(gid)
                )
                self.content.add_widget(card)

        # 4. Add button
        btn_add = AtelierGhostButton(
            text="+ Nouvel Objectif Stratégique",
            size_hint_y=None,
            height=42
        )
        btn_add.bind(on_release=lambda _: self._open_add_dialog())
        self.content.add_widget(btn_add)

    def _set_category(self, cat):
        self.selected_category = cat
        self.refresh_goals()
