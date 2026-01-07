"""
Card detail display panel.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..theme import THEME
from cardforge.models import CollectionCard


class CardDetailPanel(QWidget):
    """
    Right panel showing selected card details.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._setup_ui()
        self._show_placeholder()

    def _setup_ui(self):
        """Setup detail panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("Card Details")
        title.setProperty("class", "heading")
        title.setFont(THEME.get_font("heading", bold=True))
        layout.addWidget(title)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)

    def _show_placeholder(self):
        """Show placeholder when no card selected."""
        self._clear_content()

        placeholder = QLabel("Select a card to view details")
        placeholder.setProperty("class", "muted")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setFont(THEME.get_font("normal"))
        self.content_layout.addWidget(placeholder)

    def _clear_content(self):
        """Clear all content."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def show_card(self, card_entry: CollectionCard):
        """Display card details."""
        self._clear_content()

        if not card_entry.card:
            self._show_placeholder()
            return

        card = card_entry.card

        # Card name
        name_label = QLabel(card.name)
        name_label.setFont(THEME.get_font("title", bold=True))
        name_label.setWordWrap(True)
        self.content_layout.addWidget(name_label)

        # Mana cost
        if card.mana_cost:
            mana_label = QLabel(card.mana_cost)
            mana_label.setProperty("class", "subtitle")
            mana_label.setFont(THEME.get_font("normal"))
            self.content_layout.addWidget(mana_label)

        # Type line
        if card.type_line:
            type_label = QLabel(card.type_line)
            type_label.setProperty("class", "subtitle")
            type_label.setFont(THEME.get_font("normal"))
            type_label.setWordWrap(True)
            self.content_layout.addWidget(type_label)

        # Spacing
        self.content_layout.addSpacing(10)

        # Oracle text
        if card.oracle_text:
            oracle_frame = QFrame()
            oracle_frame.setFrameShape(QFrame.Shape.Box)
            oracle_frame.setStyleSheet(f"background-color: {THEME.BG_SECONDARY}; padding: 10px;")

            oracle_layout = QVBoxLayout(oracle_frame)
            oracle_text = QLabel(card.oracle_text)
            oracle_text.setWordWrap(True)
            oracle_text.setFont(THEME.get_font("small"))
            oracle_layout.addWidget(oracle_text)

            self.content_layout.addWidget(oracle_frame)

        # Spacing
        self.content_layout.addSpacing(10)

        # Collection info
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.Box)
        info_frame.setStyleSheet(f"background-color: {THEME.BG_SECONDARY}; padding: 10px;")

        info_layout = QVBoxLayout(info_frame)

        self._add_info_row(info_layout, "Set:", card.set_code or 'Unknown')
        self._add_info_row(info_layout, "Rarity:", card.rarity or 'Unknown')
        self._add_info_row(info_layout, "Quantity:", str(card_entry.quantity))
        self._add_info_row(info_layout, "Foil:", card_entry.foil)
        self._add_info_row(info_layout, "Condition:", card_entry.condition)

        self.content_layout.addWidget(info_frame)

        # Spacing
        self.content_layout.addSpacing(10)

        # Pricing info
        price_frame = QFrame()
        price_frame.setFrameShape(QFrame.Shape.Box)
        price_frame.setStyleSheet(f"background-color: {THEME.BG_SECONDARY}; padding: 10px;")

        price_layout = QVBoxLayout(price_frame)

        self._add_info_row(price_layout, "Market Price:", f"${card_entry.current_price:.2f}")
        self._add_info_row(price_layout, "Total Value:", f"${card_entry.total_value:.2f}", bold=True)

        if card_entry.purchase_price:
            self._add_info_row(price_layout, "Purchase Price:", f"${card_entry.purchase_price:.2f}")
            if card_entry.gain_loss:
                color = THEME.SUCCESS if card_entry.gain_loss > 0 else THEME.ERROR
                self._add_info_row(
                    price_layout,
                    "Gain/Loss:",
                    f"${card_entry.gain_loss:.2f}",
                    value_color=color
                )

        self.content_layout.addWidget(price_frame)

        # Add stretch at the end
        self.content_layout.addStretch()

    def _add_info_row(self, layout: QVBoxLayout, label_text: str, value_text: str,
                      bold: bool = False, value_color: str = None):
        """Add an info row to the layout."""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 2, 0, 2)

        label = QLabel(label_text)
        label.setProperty("class", "muted")
        label.setFont(THEME.get_font("small"))
        label.setMinimumWidth(120)
        row_layout.addWidget(label)

        value = QLabel(value_text)
        value.setFont(THEME.get_font("normal", bold=bold))
        if value_color:
            value.setStyleSheet(f"color: {value_color};")
        row_layout.addWidget(value)
        row_layout.addStretch()

        layout.addWidget(row_widget)
