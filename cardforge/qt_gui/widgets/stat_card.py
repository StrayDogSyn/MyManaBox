"""Statistics display card widget."""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..theme import THEME


class StatCard(QFrame):
    """Card widget displaying a statistic with optional trend."""
    
    def __init__(self, title: str, value: str = "0", icon: str = "", trend: str = "", parent=None):
        super().__init__(parent)
        self._title = title
        self._value = value
        self._icon = icon
        self._trend = trend
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        self.setMinimumSize(150, 100)
        self.setMaximumHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        # Header with icon and title
        header = QHBoxLayout()
        if self._icon:
            icon_label = QLabel(self._icon)
            icon_label.setFont(QFont(THEME.FONT_FAMILY, 16))
            header.addWidget(icon_label)
        
        title_label = QLabel(self._title)
        title_label.setStyleSheet(f"color: {THEME.TEXT_SECONDARY}; font-size: 11px;")
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Value row
        value_row = QHBoxLayout()
        self.value_label = QLabel(self._value)
        self.value_label.setFont(QFont(THEME.FONT_FAMILY, 24, QFont.Weight.Bold))
        value_row.addWidget(self.value_label)
        
        self.trend_label = QLabel(self._trend)
        self.trend_label.setFont(QFont(THEME.FONT_FAMILY, 11))
        value_row.addWidget(self.trend_label)
        value_row.addStretch()
        layout.addLayout(value_row)
        
        layout.addStretch()
    
    def _apply_style(self):
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {THEME.BG_SECONDARY};
                border: 1px solid {THEME.BORDER_COLOR};
                border-radius: 8px;
            }}
            StatCard:hover {{
                border-color: {THEME.ACCENT_PRIMARY};
            }}
        """)
        self._update_trend_color()
    
    def _update_trend_color(self):
        if self._trend.startswith('+'):
            color = THEME.SUCCESS
        elif self._trend.startswith('-'):
            color = THEME.ERROR
        else:
            color = THEME.TEXT_MUTED
        self.trend_label.setStyleSheet(f"color: {color};")
    
    def set_value(self, value: str):
        self._value = value
        self.value_label.setText(value)
    
    def set_trend(self, trend: str):
        self._trend = trend
        self.trend_label.setText(trend)
        self._update_trend_color()
