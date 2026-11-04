"""LifeOS UI Theme & Styling utilities."""

from kivy.utils import get_color_from_hex
from lifeos.core.config import (
    HEX_CANVAS, HEX_SURFACE, HEX_CARD, HEX_CARD_HOVER,
    HEX_BORDER, HEX_GOLD, HEX_CHAMPAGNE, HEX_TEXT_PRIMARY,
    HEX_TEXT_SECONDARY, HEX_TEXT_MUTED, HEX_SUCCESS, HEX_WARNING, HEX_ERROR
)

# Colors in 0-1 float format for Kivy widgets
BG_CANVAS = get_color_from_hex(HEX_CANVAS)
BG_SURFACE = get_color_from_hex(HEX_SURFACE)
BG_CARD = get_color_from_hex(HEX_CARD)
BG_CARD_HOVER = get_color_from_hex(HEX_CARD_HOVER)
BORDER_COLOR = get_color_from_hex(HEX_BORDER)

GOLD = get_color_from_hex(HEX_GOLD)
CHAMPAGNE = get_color_from_hex(HEX_CHAMPAGNE)
TEXT_PRIMARY = get_color_from_hex(HEX_TEXT_PRIMARY)
TEXT_SECONDARY = get_color_from_hex(HEX_TEXT_SECONDARY)
TEXT_MUTED = get_color_from_hex(HEX_TEXT_MUTED)

SUCCESS = get_color_from_hex(HEX_SUCCESS)
WARNING = get_color_from_hex(HEX_WARNING)
ERROR = get_color_from_hex(HEX_ERROR)

# Priority Badge Colors
PRIORITY_COLOR_MAP = {
    "URGENT": ERROR,
    "HIGH": WARNING,
    "MEDIUM": GOLD,
    "LOW": TEXT_SECONDARY,
}
