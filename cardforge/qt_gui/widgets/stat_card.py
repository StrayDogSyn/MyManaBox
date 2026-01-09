"""Statistics display card widget."""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..theme import THEME


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
