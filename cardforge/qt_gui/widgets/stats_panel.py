"""
Stats panel showing collection overview.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt6.QtGui import QFont

from ..theme import THEME
from .stat_card import StatCard


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
