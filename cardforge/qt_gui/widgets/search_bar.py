"""
SearchBar widget with debouncing.
"""

from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from ..theme import THEME


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
