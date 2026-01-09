"""Analytics dashboard panel with charts and statistics."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

try:
    import pyqtgraph as pg
    HAS_PYQTGRAPH = True
except ImportError:
    HAS_PYQTGRAPH = False

from ..widgets.stat_card import StatCard
from ..theme import THEME


class AnalyticsPanel(QWidget):
    """Analytics dashboard with statistics and charts."""
    
    refresh_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_theme()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("📊 Collection Analytics")
        header.setFont(QFont(THEME.FONT_FAMILY, 18, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self.total_cards = StatCard("Total Cards", "0", "📦")
        self.total_value = StatCard("Collection Value", "$0.00", "💰")
        self.unique_cards = StatCard("Unique Cards", "0", "🃏")
        self.avg_price = StatCard("Avg Price", "$0.00", "📈")
        
        stats_layout.addWidget(self.total_cards)
        stats_layout.addWidget(self.total_value)
        stats_layout.addWidget(self.unique_cards)
        stats_layout.addWidget(self.avg_price)
        
        layout.addLayout(stats_layout)
        
        # Charts grid
        charts_grid = QGridLayout()
        charts_grid.setSpacing(16)
        
        self.rarity_chart = self._create_chart_frame("Rarity Distribution")
        self.price_chart = self._create_chart_frame("Price Distribution")
        self.set_chart = self._create_chart_frame("Top Sets")
        self.mana_chart = self._create_chart_frame("Mana Curve")
        
        charts_grid.addWidget(self.rarity_chart, 0, 0)
        charts_grid.addWidget(self.price_chart, 0, 1)
        charts_grid.addWidget(self.set_chart, 1, 0)
        charts_grid.addWidget(self.mana_chart, 1, 1)
        
        layout.addLayout(charts_grid)
        layout.addStretch()
    
    def _create_chart_frame(self, title: str) -> QFrame:
        frame = QFrame()
        frame.setMinimumSize(300, 200)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME.BG_SECONDARY};
                border: 1px solid {THEME.BORDER_COLOR};
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setFont(QFont(THEME.FONT_FAMILY, 12, QFont.Weight.Medium))
        layout.addWidget(title_label)
        
        if HAS_PYQTGRAPH:
            plot = pg.PlotWidget()
            plot.setBackground(THEME.BG_SECONDARY)
            layout.addWidget(plot)
            frame.plot_widget = plot
        else:
            placeholder = QLabel("Install pyqtgraph for charts")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(placeholder)
        
        return frame
    
    def _apply_theme(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME.BG_PRIMARY};
                color: {THEME.TEXT_PRIMARY};
            }}
            QLabel {{
                background-color: transparent;
            }}
        """)
    
    def update_stats(self, stats: dict):
        """Update statistics display."""
        self.total_cards.set_value(f"{stats.get('total_cards', 0):,}")
        self.total_value.set_value(f"${stats.get('total_value', 0):,.2f}")
        self.unique_cards.set_value(f"{stats.get('unique_cards', 0):,}")
        self.avg_price.set_value(f"${stats.get('average_price', 0):.2f}")
        
        if 'value_change' in stats:
            change = stats['value_change']
            trend = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
            self.total_value.set_trend(trend)
