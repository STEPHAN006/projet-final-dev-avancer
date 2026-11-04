"""LifeOS UI Theme & Styling System (Shadcn / React Native / Linear Style).
Supports both Modern Light Mode and Crisp Dark Mode.
"""

from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from lifeos.core.events import bus

class Theme:
    """Dynamic Theme Engine providing modern Shadcn / React Native tokens."""

    def __init__(self, mode: str = "light"):
        self.mode = mode

    @property
    def is_light(self) -> bool:
        return self.mode == "light"

    # --- Canvas & Surfaces ---
    @property
    def bg_canvas(self) -> list[float]:
        return get_color_from_hex("#F8FAFC" if self.is_light else "#090D16")

    @property
    def bg_surface(self) -> list[float]:
        return get_color_from_hex("#FFFFFF" if self.is_light else "#0F172A")

    @property
    def bg_card(self) -> list[float]:
        return get_color_from_hex("#FFFFFF" if self.is_light else "#141C2E")

    @property
    def bg_card_hover(self) -> list[float]:
        return get_color_from_hex("#F1F5F9" if self.is_light else "#1E293B")

    @property
    def bg_input(self) -> list[float]:
        return get_color_from_hex("#FFFFFF" if self.is_light else "#0F172A")

    @property
    def bg_muted(self) -> list[float]:
        return get_color_from_hex("#F1F5F9" if self.is_light else "#1E293B")

    # --- Borders ---
    @property
    def border(self) -> list[float]:
        return get_color_from_hex("#E2E8F0" if self.is_light else "#222F43")

    @property
    def border_subtle(self) -> list[float]:
        return get_color_from_hex("#F1F5F9" if self.is_light else "#192231")

    @property
    def border_focus(self) -> list[float]:
        return get_color_from_hex("#2563EB" if self.is_light else "#3B82F6")

    # --- Brand & Accents ---
    @property
    def primary(self) -> list[float]:
        # Electric Blue / Modern Indigo
        return get_color_from_hex("#2563EB" if self.is_light else "#3B82F6")

    @property
    def primary_dark(self) -> list[float]:
        # Shadcn Zinc-900 style
        return get_color_from_hex("#0F172A" if self.is_light else "#F8FAFC")

    @property
    def primary_text(self) -> list[float]:
        return get_color_from_hex("#FFFFFF" if self.is_light else "#0F172A")

    @property
    def accent(self) -> list[float]:
        return get_color_from_hex("#6366F1" if self.is_light else "#818CF8")

    # --- Typography ---
    @property
    def text_primary(self) -> list[float]:
        return get_color_from_hex("#0F172A" if self.is_light else "#F8FAFC")

    @property
    def text_secondary(self) -> list[float]:
        return get_color_from_hex("#64748B" if self.is_light else "#94A3B8")

    @property
    def text_muted(self) -> list[float]:
        return get_color_from_hex("#94A3B8" if self.is_light else "#64748B")

    # --- Semantic States ---
    @property
    def success(self) -> list[float]:
        return get_color_from_hex("#10B981" if self.is_light else "#34D399")

    @property
    def warning(self) -> list[float]:
        return get_color_from_hex("#F59E0B" if self.is_light else "#FBBF24")

    @property
    def error(self) -> list[float]:
        return get_color_from_hex("#EF4444" if self.is_light else "#F87171")

    @property
    def info(self) -> list[float]:
        return get_color_from_hex("#0EA5E9" if self.is_light else "#38BDF8")

    # --- Badge Colors (Shadcn Soft Pastels) ---
    def badge_colors(self, priority: str) -> tuple[list[float], list[float]]:
        p = priority.upper()
        if p == "URGENT":
            bg = [0.99, 0.89, 0.89, 1.0] if self.is_light else [0.93, 0.27, 0.27, 0.18]
            fg = get_color_from_hex("#DC2626" if self.is_light else "#F87171")
        elif p == "HIGH":
            bg = [0.99, 0.95, 0.78, 1.0] if self.is_light else [0.98, 0.75, 0.14, 0.18]
            fg = get_color_from_hex("#D97706" if self.is_light else "#FBBF24")
        elif p == "MEDIUM":
            bg = [0.93, 0.96, 1.0, 1.0] if self.is_light else [0.23, 0.51, 0.96, 0.18]
            fg = get_color_from_hex("#2563EB" if self.is_light else "#60A5FA")
        else: # LOW or default
            bg = [0.95, 0.96, 0.98, 1.0] if self.is_light else [0.4, 0.45, 0.55, 0.18]
            fg = get_color_from_hex("#475569" if self.is_light else "#94A3B8")
        return bg, fg

    def toggle(self):
        self.mode = "dark" if self.mode == "light" else "light"
        try:
            Window.clearcolor = self.bg_canvas
        except Exception:
            pass
        bus.emit("theme_changed", mode=self.mode)

    def set_mode(self, mode: str):
        if mode in ("light", "dark"):
            self.mode = mode
            try:
                Window.clearcolor = self.bg_canvas
            except Exception:
                pass
            bus.emit("theme_changed", mode=self.mode)

theme = Theme(mode="light")

# Backwards-compatible module-level constants
def _get_prop(name):
    return getattr(theme, name)

# Shortcuts
BG_CANVAS = theme.bg_canvas
BG_SURFACE = theme.bg_surface
BG_CARD = theme.bg_card
BG_CARD_HOVER = theme.bg_card_hover
BORDER_COLOR = theme.border
GOLD = theme.primary
CHAMPAGNE = theme.accent
TEXT_PRIMARY = theme.text_primary
TEXT_SECONDARY = theme.text_secondary
TEXT_MUTED = theme.text_muted
SUCCESS = theme.success
WARNING = theme.warning
ERROR = theme.error

PRIORITY_COLOR_MAP = {
    "URGENT": theme.error,
    "HIGH": theme.warning,
    "MEDIUM": theme.primary,
    "LOW": theme.text_secondary,
}
