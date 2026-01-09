"""
Collection browser panel with sortable table.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal

from cardforge.models import CollectionCard


class CollectionBrowserPanel(QWidget):
    """
    Main card collection browser with sortable table.

    Signals:
        card_selected(CollectionCard): Emitted when a card is selected
    """

    card_selected = pyqtSignal(object)  # CollectionCard

    def __init__(self, parent=None):
        super().__init__(parent)

        self.all_cards: list[CollectionCard] = []
        self.filtered_cards: list[CollectionCard] = []

        self._setup_ui()

    def _setup_ui(self):
        """Setup browser UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Name", "Set", "Rarity", "Type",
            "Quantity", "Foil", "Condition", "Value", "Total"
        ])

        # Configure table
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)

        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Set
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Rarity
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Quantity
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Foil
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Condition
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Value
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Total

        # Connect selection
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        layout.addWidget(self.table)

    def load_cards(self, cards: list[CollectionCard]):
        """Load cards into table."""
        self.all_cards = cards
        self.filtered_cards = cards.copy()
        self._populate_table(self.filtered_cards)

    def _populate_table(self, cards: list[CollectionCard]):
        """Populate table with cards."""
        self.table.setSortingEnabled(False)  # Disable sorting during population
        self.table.setRowCount(len(cards))

        for row, card_entry in enumerate(cards):
            if not card_entry.card:
                continue

            card = card_entry.card

            # Store card_entry in row for later retrieval
            name_item = QTableWidgetItem(card.name)
            name_item.setData(Qt.ItemDataRole.UserRole, card_entry)
            self.table.setItem(row, 0, name_item)

            self.table.setItem(row, 1, QTableWidgetItem(card.set_code or ''))
            self.table.setItem(row, 2, QTableWidgetItem(card.rarity or ''))
            self.table.setItem(row, 3, QTableWidgetItem(card.type_line or ''))
            self.table.setItem(row, 4, QTableWidgetItem(str(card_entry.quantity)))
            self.table.setItem(row, 5, QTableWidgetItem(card_entry.foil))
            self.table.setItem(row, 6, QTableWidgetItem(card_entry.condition))
            self.table.setItem(row, 7, QTableWidgetItem(f"${card_entry.current_price:.2f}"))
            self.table.setItem(row, 8, QTableWidgetItem(f"${card_entry.total_value:.2f}"))

        self.table.setSortingEnabled(True)  # Re-enable sorting

    def filter_cards(self, query: str):
        """Filter cards by search query."""
        if not query:
            self.filtered_cards = self.all_cards.copy()
        else:
            query_lower = query.lower()
            self.filtered_cards = [
                card_entry for card_entry in self.all_cards
                if card_entry.card and (
                    query_lower in card_entry.card.name.lower() or
                    query_lower in (card_entry.card.type_line or '').lower() or
                    query_lower in (card_entry.card.oracle_text or '').lower()
                )
            ]

        self._populate_table(self.filtered_cards)

    def clear_filter(self):
        """Clear filter and show all cards."""
        self.filtered_cards = self.all_cards.copy()
        self._populate_table(self.filtered_cards)

    def _on_selection_changed(self):
        """Handle selection change."""
        selected_items = self.table.selectedItems()
        if selected_items:
            # Get the first column item (which has our card_entry)
            row = selected_items[0].row()
            name_item = self.table.item(row, 0)
            if name_item:
                card_entry = name_item.data(Qt.ItemDataRole.UserRole)
                if card_entry:
                    self.card_selected.emit(card_entry)
