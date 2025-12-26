"""
CardForge GUI Theme
Design system constants and styling
"""


class Theme:
    """Design system constants - CardForge brand identity"""

    # Background colors
    BG_PRIMARY = "#1a1625"      # Main window
    BG_SECONDARY = "#241e35"    # Panels
    BG_TERTIARY = "#2a2235"     # Input fields

    # Accent colors (Purple theme)
    ACCENT_PRIMARY = "#5a4fcf"
    ACCENT_HOVER = "#6a5fdf"
    ACCENT_PRESSED = "#4a3fbf"
    ACCENT_SUBTLE = "#7c6dd8"

    # Text colors
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#b8b0d0"
    TEXT_MUTED = "#8a829d"

    # Semantic colors
    SUCCESS = "#4caf50"
    WARNING = "#ff9800"
    ERROR = "#f44336"
    INFO = "#2196f3"

    # MTG Colors
    MTG_WHITE = "#f0f2c0"
    MTG_BLUE = "#0e68ab"
    MTG_BLACK = "#150b00"
    MTG_RED = "#d3202a"
    MTG_GREEN = "#00733e"
    MTG_COLORLESS = "#bfb5af"

    # Layout
    PADDING = 8
    BORDER_RADIUS = 4

    # Typography
    FONT_FAMILY = "Segoe UI"  # Windows default
    FONT_SIZE_LARGE = 14
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_SMALL = 9


class Icons:
    """Unicode icons for better UX"""
    SEARCH = "🔍"
    REFRESH = "↻"
    SYNC = "⟳"
    EXPORT = "⬆"
    IMPORT = "⬇"
    SETTINGS = "⚙"
    HELP = "?"
    STATS = "📊"
    DECK = "🃏"
    DOLLAR = "💰"
    SPARKLES = "✨"
    CHECK = "✓"
    CROSS = "✗"
    CARD = "🎴"
    CHART = "📈"
    DATABASE = "🗄"
    LINK = "🔗"
    WARNING = "⚠"
    INFO = "ℹ"
    SORT_ASC = "▲"
    SORT_DESC = "▼"


class RarityColors:
    """Rarity-based colors"""
    COMMON = "#000000"
    UNCOMMON = "#6e7c82"
    RARE = "#c0a062"
    MYTHIC = "#e87722"
    SPECIAL = "#a947ba"
