"""
CardForge PyQt6 Theme System
Centralized styling using Qt Style Sheets (QSS)
"""

from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt


class CardForgeTheme:
    """
    CardForge design system - consistent with Tkinter GUI but leveraging Qt's power.

    Provides colors, fonts, and complete QSS stylesheets.
    """

    # =========================================================================
    # COLORS
    # =========================================================================

    # Background colors
    BG_PRIMARY = "#1a1625"      # Main window background
    BG_SECONDARY = "#241e35"    # Panel backgrounds
    BG_TERTIARY = "#2a2235"     # Input fields, cards
    BG_HOVER = "#322a45"        # Hover states

    # Accent colors (Purple theme)
    ACCENT_PRIMARY = "#5a4fcf"
    ACCENT_HOVER = "#6a5fdf"
    ACCENT_PRESSED = "#4a3fbf"
    ACCENT_SUBTLE = "#7c6dd8"
    ACCENT_LIGHT = "#8c7de8"

    # Text colors
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#b8b0d0"
    TEXT_MUTED = "#8a829d"
    TEXT_DISABLED = "#5a5268"

    # Semantic colors
    SUCCESS = "#4caf50"
    WARNING = "#ff9800"
    ERROR = "#f44336"
    INFO = "#2196f3"

    # MTG Colors (for mana symbols and color filters)
    MTG_WHITE = "#f0f2c0"
    MTG_BLUE = "#0e68ab"
    MTG_BLACK = "#150b00"
    MTG_RED = "#d3202a"
    MTG_GREEN = "#00733e"
    MTG_COLORLESS = "#bfb5af"

    # Rarity colors
    RARITY_COMMON = "#000000"
    RARITY_UNCOMMON = "#6e7c82"
    RARITY_RARE = "#c0a062"
    RARITY_MYTHIC = "#e87722"
    RARITY_SPECIAL = "#a947ba"

    # UI elements
    BORDER_COLOR = "#3a3248"
    SELECTION_COLOR = ACCENT_PRIMARY
    SCROLLBAR_BG = BG_TERTIARY
    SCROLLBAR_HANDLE = ACCENT_SUBTLE

    # =========================================================================
    # TYPOGRAPHY
    # =========================================================================

    FONT_FAMILY = "Segoe UI"  # Windows default, fallback to system
    FONT_SIZE_SMALL = 9
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_LARGE = 12
    FONT_SIZE_HEADING = 14
    FONT_SIZE_TITLE = 16

    # =========================================================================
    # LAYOUT
    # =========================================================================

    PADDING_SMALL = 4
    PADDING_NORMAL = 8
    PADDING_LARGE = 12
    PADDING_XLARGE = 16

    BORDER_RADIUS = 4
    BORDER_WIDTH = 1

    SPACING_SMALL = 4
    SPACING_NORMAL = 8
    SPACING_LARGE = 12

    # =========================================================================
    # QSS STYLESHEET
    # =========================================================================

    @classmethod
    def get_stylesheet(cls) -> str:
        """
        Get the complete application stylesheet.

        This is a comprehensive QSS (Qt Style Sheet) that styles all widgets.
        Similar to CSS for web, but for Qt applications.
        """
        return f"""
        /* ============================================================
           GLOBAL APPLICATION STYLES
           ============================================================ */

        QWidget {{
            background-color: {cls.BG_PRIMARY};
            color: {cls.TEXT_PRIMARY};
            font-family: "{cls.FONT_FAMILY}";
            font-size: {cls.FONT_SIZE_NORMAL}pt;
        }}

        /* ============================================================
           MAIN WINDOW & PANELS
           ============================================================ */

        QMainWindow {{
            background-color: {cls.BG_PRIMARY};
        }}

        QFrame {{
            background-color: {cls.BG_SECONDARY};
            border: none;
            border-radius: {cls.BORDER_RADIUS}px;
        }}

        QGroupBox {{
            background-color: {cls.BG_SECONDARY};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: {cls.BORDER_RADIUS}px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
            color: {cls.TEXT_PRIMARY};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: {cls.TEXT_PRIMARY};
        }}

        /* ============================================================
           BUTTONS
           ============================================================ */

        QPushButton {{
            background-color: {cls.ACCENT_PRIMARY};
            color: {cls.TEXT_PRIMARY};
            border: none;
            border-radius: {cls.BORDER_RADIUS}px;
            padding: 8px 16px;
            font-weight: bold;
            min-width: 80px;
        }}

        QPushButton:hover {{
            background-color: {cls.ACCENT_HOVER};
        }}

        QPushButton:pressed {{
            background-color: {cls.ACCENT_PRESSED};
        }}

        QPushButton:disabled {{
            background-color: {cls.BG_TERTIARY};
            color: {cls.TEXT_DISABLED};
        }}

        QPushButton[class="secondary"] {{
            background-color: {cls.BG_TERTIARY};
            color: {cls.TEXT_SECONDARY};
        }}

        QPushButton[class="secondary"]:hover {{
            background-color: {cls.BG_HOVER};
            color: {cls.TEXT_PRIMARY};
        }}

        QPushButton[class="danger"] {{
            background-color: {cls.ERROR};
        }}

        QPushButton[class="success"] {{
            background-color: {cls.SUCCESS};
        }}

        /* ============================================================
           INPUT FIELDS
           ============================================================ */

        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {cls.BG_TERTIARY};
            color: {cls.TEXT_PRIMARY};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: {cls.BORDER_RADIUS}px;
            padding: 6px 12px;
            selection-background-color: {cls.ACCENT_PRIMARY};
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {cls.ACCENT_PRIMARY};
        }}

        QLineEdit:disabled, QTextEdit:disabled {{
            background-color: {cls.BG_SECONDARY};
            color: {cls.TEXT_DISABLED};
        }}

        /* ============================================================
           COMBOBOX (DROPDOWN)
           ============================================================ */

        QComboBox {{
            background-color: {cls.BG_TERTIARY};
            color: {cls.TEXT_PRIMARY};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: {cls.BORDER_RADIUS}px;
            padding: 6px 12px;
            min-width: 100px;
        }}

        QComboBox:hover {{
            background-color: {cls.BG_HOVER};
            border-color: {cls.ACCENT_SUBTLE};
        }}

        QComboBox:focus {{
            border: 1px solid {cls.ACCENT_PRIMARY};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {cls.TEXT_SECONDARY};
            margin-right: 8px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {cls.BG_TERTIARY};
            color: {cls.TEXT_PRIMARY};
            selection-background-color: {cls.ACCENT_PRIMARY};
            selection-color: {cls.TEXT_PRIMARY};
            border: 1px solid {cls.BORDER_COLOR};
        }}

        /* ============================================================
           TABLES & TREE VIEWS
           ============================================================ */

        QTableView, QTreeView {{
            background-color: {cls.BG_TERTIARY};
            alternate-background-color: {cls.BG_SECONDARY};
            color: {cls.TEXT_PRIMARY};
            gridline-color: {cls.BORDER_COLOR};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: {cls.BORDER_RADIUS}px;
            selection-background-color: {cls.ACCENT_PRIMARY};
            selection-color: {cls.TEXT_PRIMARY};
        }}

        QTableView::item, QTreeView::item {{
            padding: 4px;
            border: none;
        }}

        QTableView::item:hover, QTreeView::item:hover {{
            background-color: {cls.BG_HOVER};
        }}

        QTableView::item:selected, QTreeView::item:selected {{
            background-color: {cls.ACCENT_PRIMARY};
        }}

        QHeaderView {{
            background-color: {cls.BG_PRIMARY};
            color: {cls.TEXT_PRIMARY};
            border: none;
        }}

        QHeaderView::section {{
            background-color: {cls.BG_SECONDARY};
            color: {cls.TEXT_PRIMARY};
            padding: 8px;
            border: none;
            border-right: 1px solid {cls.BORDER_COLOR};
            border-bottom: 1px solid {cls.BORDER_COLOR};
            font-weight: bold;
        }}

        QHeaderView::section:hover {{
            background-color: {cls.BG_HOVER};
        }}

        /* ============================================================
           SCROLLBARS
           ============================================================ */

        QScrollBar:vertical {{
            background-color: {cls.BG_PRIMARY};
            width: 12px;
            margin: 0px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {cls.SCROLLBAR_HANDLE};
            min-height: 20px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {cls.ACCENT_HOVER};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar:horizontal {{
            background-color: {cls.BG_PRIMARY};
            height: 12px;
            margin: 0px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {cls.SCROLLBAR_HANDLE};
            min-width: 20px;
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {cls.ACCENT_HOVER};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* ============================================================
           LABELS & TEXT
           ============================================================ */

        QLabel {{
            background-color: transparent;
            color: {cls.TEXT_PRIMARY};
        }}

        QLabel[class="heading"] {{
            font-size: {cls.FONT_SIZE_HEADING}pt;
            font-weight: bold;
            color: {cls.TEXT_PRIMARY};
        }}

        QLabel[class="title"] {{
            font-size: {cls.FONT_SIZE_TITLE}pt;
            font-weight: bold;
            color: {cls.TEXT_PRIMARY};
        }}

        QLabel[class="subtitle"] {{
            font-size: {cls.FONT_SIZE_NORMAL}pt;
            color: {cls.TEXT_SECONDARY};
        }}

        QLabel[class="muted"] {{
            color: {cls.TEXT_MUTED};
        }}

        /* ============================================================
           TAB WIDGET
           ============================================================ */

        QTabWidget::pane {{
            background-color: {cls.BG_SECONDARY};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: {cls.BORDER_RADIUS}px;
            top: -1px;
        }}

        QTabBar::tab {{
            background-color: {cls.BG_TERTIARY};
            color: {cls.TEXT_SECONDARY};
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: {cls.BORDER_RADIUS}px;
            border-top-right-radius: {cls.BORDER_RADIUS}px;
        }}

        QTabBar::tab:selected {{
            background-color: {cls.ACCENT_PRIMARY};
            color: {cls.TEXT_PRIMARY};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {cls.BG_HOVER};
            color: {cls.TEXT_PRIMARY};
        }}

        /* ============================================================
           MENU & MENU BAR
           ============================================================ */

        QMenuBar {{
            background-color: {cls.BG_PRIMARY};
            color: {cls.TEXT_PRIMARY};
            border-bottom: 1px solid {cls.BORDER_COLOR};
        }}

        QMenuBar::item {{
            padding: 8px 12px;
            background-color: transparent;
        }}

        QMenuBar::item:selected {{
            background-color: {cls.BG_HOVER};
        }}

        QMenu {{
            background-color: {cls.BG_SECONDARY};
            color: {cls.TEXT_PRIMARY};
            border: 1px solid {cls.BORDER_COLOR};
        }}

        QMenu::item {{
            padding: 8px 30px 8px 20px;
        }}

        QMenu::item:selected {{
            background-color: {cls.ACCENT_PRIMARY};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {cls.BORDER_COLOR};
            margin: 4px 0px;
        }}

        /* ============================================================
           STATUS BAR
           ============================================================ */

        QStatusBar {{
            background-color: {cls.BG_SECONDARY};
            color: {cls.TEXT_SECONDARY};
            border-top: 1px solid {cls.BORDER_COLOR};
        }}

        QStatusBar::item {{
            border: none;
        }}

        /* ============================================================
           PROGRESS BAR
           ============================================================ */

        QProgressBar {{
            background-color: {cls.BG_TERTIARY};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: {cls.BORDER_RADIUS}px;
            text-align: center;
            color: {cls.TEXT_PRIMARY};
        }}

        QProgressBar::chunk {{
            background-color: {cls.ACCENT_PRIMARY};
            border-radius: {cls.BORDER_RADIUS}px;
        }}

        /* ============================================================
           TOOLTIPS
           ============================================================ */

        QToolTip {{
            background-color: {cls.BG_TERTIARY};
            color: {cls.TEXT_PRIMARY};
            border: 1px solid {cls.BORDER_COLOR};
            padding: 4px;
            border-radius: {cls.BORDER_RADIUS}px;
        }}

        /* ============================================================
           SPLITTER
           ============================================================ */

        QSplitter::handle {{
            background-color: {cls.BORDER_COLOR};
        }}

        QSplitter::handle:hover {{
            background-color: {cls.ACCENT_SUBTLE};
        }}

        QSplitter::handle:horizontal {{
            width: 2px;
        }}

        QSplitter::handle:vertical {{
            height: 2px;
        }}
        """

    @classmethod
    def create_palette(cls) -> QPalette:
        """
        Create a QPalette for the application.

        This provides a fallback color scheme for widgets that don't
        fully support QSS styling.
        """
        palette = QPalette()

        # Window colors
        palette.setColor(QPalette.ColorRole.Window, QColor(cls.BG_PRIMARY))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(cls.TEXT_PRIMARY))

        # Base colors (for input fields)
        palette.setColor(QPalette.ColorRole.Base, QColor(cls.BG_TERTIARY))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(cls.BG_SECONDARY))

        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(cls.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(cls.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(cls.TEXT_MUTED))

        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(cls.ACCENT_PRIMARY))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(cls.TEXT_PRIMARY))

        # Highlight colors (selection)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(cls.ACCENT_PRIMARY))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(cls.TEXT_PRIMARY))

        # Links
        palette.setColor(QPalette.ColorRole.Link, QColor(cls.ACCENT_SUBTLE))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(cls.ACCENT_PRESSED))

        # Disabled colors
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText,
                        QColor(cls.TEXT_DISABLED))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,
                        QColor(cls.TEXT_DISABLED))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText,
                        QColor(cls.TEXT_DISABLED))

        return palette

    @classmethod
    def get_font(cls, size: str = "normal", bold: bool = False) -> QFont:
        """
        Get a themed font.

        Args:
            size: Font size preset ("small", "normal", "large", "heading", "title")
            bold: Whether the font should be bold

        Returns:
            Configured QFont
        """
        size_map = {
            "small": cls.FONT_SIZE_SMALL,
            "normal": cls.FONT_SIZE_NORMAL,
            "large": cls.FONT_SIZE_LARGE,
            "heading": cls.FONT_SIZE_HEADING,
            "title": cls.FONT_SIZE_TITLE,
        }

        font_size = size_map.get(size, cls.FONT_SIZE_NORMAL)
        font = QFont(cls.FONT_FAMILY, font_size)

        if bold:
            font.setWeight(QFont.Weight.Bold)

        return font


# Convenience exports
THEME = CardForgeTheme
