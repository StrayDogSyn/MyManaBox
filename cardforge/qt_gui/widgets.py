"""
CardForge PyQt6 Widgets
Reusable UI components
"""

from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from .theme import THEME


class SearchBar(QWidget):
    """
    Advanced search bar with debouncing.

    Signals:
        search_triggered(str): Emitted when search query changes (after debounce)
    """

    search_triggered = pyqtSignal(str)

    def __init__(self, placeholder: str = "Search cards...", parent=None):
        super().__init__(parent)

        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(300)  # 300ms debounce
        self.debounce_timer.timeout.connect(self._emit_search)

        self._setup_ui(placeholder)

    def _setup_ui(self, placeholder: str):
        """Setup search bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Search icon (using Unicode)
        icon_label = QLabel("🔍")
        icon_label.setFont(QFont(THEME.FONT_FAMILY, 12))
        layout.addWidget(icon_label)

        # Search input
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.input, 1)  # Stretch

        # Clear button
        self.clear_btn = QPushButton("×")
        self.clear_btn.setMaximumWidth(30)
        self.clear_btn.setFont(QFont(THEME.FONT_FAMILY, 14))
        self.clear_btn.clicked.connect(self.clear)
        layout.addWidget(self.clear_btn)

    def _on_text_changed(self, text: str):
        """Handle text change with debouncing."""
        self.debounce_timer.stop()
        self.debounce_timer.start()

    def _emit_search(self):
        """Emit search signal."""
        self.search_triggered.emit(self.input.text())

    def clear(self):
        """Clear search field."""
        self.input.clear()
        self.input.setFocus()

    def get_text(self) -> str:
        """Get current search text."""
        return self.input.text()


class StatCard(QFrame):
    """
    Metric display card.

    Shows a title, main value, and optional subtitle.
    """

    def __init__(self, title: str, value: str = "0", subtitle: str = "",
                 icon: str = "", parent=None):
        super().__init__(parent)

        self.setFrameShape(QFrame.Shape.Box)
        self.setObjectName("statCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)

        # Icon (if provided)
        if icon:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont(THEME.FONT_FAMILY, 20))
            layout.addWidget(icon_label)

        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        # Title
        title_label = QLabel(title)
        title_label.setProperty("class", "subtitle")
        title_label.setFont(THEME.get_font("small"))
        text_layout.addWidget(title_label)

        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(THEME.get_font("large", bold=True))
        text_layout.addWidget(self.value_label)

        # Subtitle (if provided)
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setProperty("class", "muted")
            self.subtitle_label.setFont(THEME.get_font("small"))
            text_layout.addWidget(self.subtitle_label)
        else:
            self.subtitle_label = None

        layout.addLayout(text_layout, 1)  # Stretch

    def update_value(self, value: str, subtitle: str = None):
        """Update the displayed value."""
        self.value_label.setText(value)
        if subtitle and self.subtitle_label:
            self.subtitle_label.setText(subtitle)


class StatsPanel(QFrame):
    """
    Top stats bar showing collection overview.

    Displays 4 stat cards: Total Value, Total Cards, Average Value, Foils.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameShape(QFrame.Shape.Box)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("Collection Overview")
        title.setProperty("class", "heading")
        title.setFont(THEME.get_font("heading", bold=True))
        layout.addWidget(title)

        # Stats container
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)

        # Create stat cards
        self.total_value_card = StatCard("Total Value", "$0.00", icon="💰")
        stats_layout.addWidget(self.total_value_card)

        self.total_cards_card = StatCard("Total Cards", "0", "0 unique", icon="🃏")
        stats_layout.addWidget(self.total_cards_card)

        self.avg_value_card = StatCard("Average Value", "$0.00", "per card", icon="📊")
        stats_layout.addWidget(self.avg_value_card)

        self.foils_card = StatCard("Foils", "0", "special printings", icon="✨")
        stats_layout.addWidget(self.foils_card)

        layout.addLayout(stats_layout)

    def update_stats(self, stats):
        """Update statistics from CollectionStats model."""
        self.total_value_card.update_value(f"${stats.total_value:,.2f}")
        self.total_cards_card.update_value(
            f"{stats.total_cards:,}",
            f"{stats.unique_cards:,} unique"
        )
        self.avg_value_card.update_value(f"${stats.avg_card_value:.2f}")
        self.foils_card.update_value(
            f"{stats.foil_count:,}",
            f"{stats.unique_sets} sets"
        )


class LoadingOverlay(QDialog):
    """
    Modal loading overlay with message.

    Shows a loading message in the center of the parent window.
    """

    def __init__(self, parent, message: str = "Loading..."):
        super().__init__(parent)

        # Make it modal
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog
        )

        # Semi-transparent background
        self.setStyleSheet(f"""
            QDialog {{
                background-color: rgba(26, 22, 37, 230);
            }}
            QLabel {{
                color: {THEME.TEXT_PRIMARY};
                font-size: {THEME.FONT_SIZE_LARGE}pt;
            }}
        """)

        # Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Message
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(THEME.get_font("large"))
        layout.addWidget(label)

        # Size to parent
        if parent:
            self.setGeometry(parent.geometry())

    def show(self):
        """Show the overlay."""
        super().show()
        # Center on parent
        if self.parent():
            parent_geometry = self.parent().geometry()
            self.setGeometry(parent_geometry)
