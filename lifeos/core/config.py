"""Configuration and Design Tokens for LifeOS (Atelier OS).
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "lifeos.db"

# Atelier OS Color Palette
# Hex values
HEX_CANVAS = "#101114"          # Deep base canvas
HEX_SURFACE = "#17191E"         # Navbars, headers, sidebars
HEX_CARD = "#1E2027"            # Cards and standard containers
HEX_CARD_HOVER = "#262933"      # Elevated and hover states
HEX_BORDER = "#282B34"          # Structural borders and dividers
HEX_BORDER_LIGHT = "#343538"    # Subtle dividers

HEX_GOLD = "#C6A76B"            # Signature luxury gold
HEX_CHAMPAGNE = "#DFBA7B"       # Secondary champagne highlight
HEX_GOLD_DIM = "#8F7647"        # Dimmed gold for disabled/subtle

HEX_TEXT_PRIMARY = "#F5F5F5"    # High-contrast readable text
HEX_TEXT_SECONDARY = "#92949E"  # Low-distraction secondary text
HEX_TEXT_MUTED = "#63656E"      # Inactive captions

HEX_SUCCESS = "#4EAA78"         # Green
HEX_WARNING = "#E5A93B"         # Amber
HEX_ERROR = "#E05D52"           # Coral / urgent red
HEX_INFO = "#6B9EE8"            # Soft blue

def hex_to_rgba(hex_str: str, alpha: float = 1.0) -> list[float]:
    """Convert a hex color string to Kivy RGBA (values from 0.0 to 1.0)."""
    hex_str = hex_str.lstrip("#")
    r = int(hex_str[0:2], 16) / 255.0
    g = int(hex_str[2:4], 16) / 255.0
    b = int(hex_str[4:6], 16) / 255.0
    return [r, g, b, alpha]

# Kivy RGBA Colors
COLOR_CANVAS = hex_to_rgba(HEX_CANVAS)
COLOR_SURFACE = hex_to_rgba(HEX_SURFACE)
COLOR_CARD = hex_to_rgba(HEX_CARD)
COLOR_CARD_HOVER = hex_to_rgba(HEX_CARD_HOVER)
COLOR_BORDER = hex_to_rgba(HEX_BORDER)
COLOR_GOLD = hex_to_rgba(HEX_GOLD)
COLOR_CHAMPAGNE = hex_to_rgba(HEX_CHAMPAGNE)
COLOR_TEXT_PRIMARY = hex_to_rgba(HEX_TEXT_PRIMARY)
COLOR_TEXT_SECONDARY = hex_to_rgba(HEX_TEXT_SECONDARY)
COLOR_TEXT_MUTED = hex_to_rgba(HEX_TEXT_MUTED)

COLOR_SUCCESS = hex_to_rgba(HEX_SUCCESS)
COLOR_WARNING = hex_to_rgba(HEX_WARNING)
COLOR_ERROR = hex_to_rgba(HEX_ERROR)
COLOR_INFO = hex_to_rgba(HEX_INFO)

# Priorities
PRIORITY_URGENT = "URGENT"
PRIORITY_HIGH = "HIGH"
PRIORITY_MEDIUM = "MEDIUM"
PRIORITY_LOW = "LOW"

PRIORITY_COLORS = {
    PRIORITY_URGENT: HEX_ERROR,
    PRIORITY_HIGH: HEX_WARNING,
    PRIORITY_MEDIUM: HEX_GOLD,
    PRIORITY_LOW: HEX_TEXT_SECONDARY,
}
