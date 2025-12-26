"""
CardForge GUI Panels
Main UI panels for collection browsing
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Callable
from decimal import Decimal

from .theme import Theme, Icons, RarityColors
from .widgets import StyledFrame, StatCard
from cardforge.models import CollectionStats, CollectionCard


class StatsPanel(StyledFrame):
    """Top stats bar showing collection overview"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_SECONDARY, **kwargs)

        # Title
        tk.Label(
            self,
            text="Collection Overview",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, 12, 'bold')
        ).pack(anchor='w', padx=15, pady=(15, 10))

        # Stats container
        stats_container = StyledFrame(self, bg=Theme.BG_SECONDARY)
        stats_container.pack(fill=tk.X, padx=10, pady=(0, 15))

        # Create stat cards
        self.total_value_card = StatCard(
            stats_container,
            title="Total Value",
            value="$0.00",
            icon=Icons.DOLLAR
        )
        self.total_value_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.total_cards_card = StatCard(
            stats_container,
            title="Total Cards",
            value="0",
            subtitle="0 unique",
            icon=Icons.DECK
        )
        self.total_cards_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.avg_value_card = StatCard(
            stats_container,
            title="Average Value",
            value="$0.00",
            subtitle="per card",
            icon=Icons.STATS
        )
        self.avg_value_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.foils_card = StatCard(
            stats_container,
            title="Foils",
            value="0",
            subtitle="special printings",
            icon=Icons.SPARKLES
        )
        self.foils_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    def update_stats(self, stats: CollectionStats):
        """Update statistics from CollectionStats model"""
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


class CollectionBrowserPanel(StyledFrame):
    """Main card collection browser with table"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Configure treeview style
        self._configure_style()

        # Table configuration
        columns = {
            "name": {"width": 250, "anchor": "w"},
            "set": {"width": 80, "anchor": "w"},
            "rarity": {"width": 100, "anchor": "w"},
            "type": {"width": 150, "anchor": "w"},
            "quantity": {"width": 80, "anchor": "center"},
            "foil": {"width": 80, "anchor": "center"},
            "condition": {"width": 80, "anchor": "center"},
            "value": {"width": 100, "anchor": "e"},
            "total": {"width": 100, "anchor": "e"}
        }

        # Create tree
        column_ids = list(columns.keys())
        self.tree = ttk.Treeview(
            self,
            columns=column_ids,
            show='tree headings',
            selectmode='extended'
        )

        # Configure columns
        self.tree.column('#0', width=0, stretch=tk.NO)  # Hide tree column

        for col_id, config in columns.items():
            width = config.get('width', 100)
            anchor = config.get('anchor', 'w')

            self.tree.column(col_id, width=width, anchor=anchor)
            self.tree.heading(
                col_id,
                text=col_id.replace('_', ' ').title(),
                command=lambda c=col_id: self.sort_by_column(c)
            )

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self._on_selection_change)
        self.tree.bind('<Double-1>', self._on_double_click)

        # Sort state
        self._sort_column = None
        self._sort_reverse = False

        # Store for callbacks
        self._selection_callback: Optional[Callable] = None
        self._double_click_callback: Optional[Callable] = None

        # Store card data for each row
        self._card_data: dict = {}

    def _configure_style(self):
        """Configure treeview styling"""
        style = ttk.Style()
        style.configure(
            'Treeview',
            background=Theme.BG_TERTIARY,
            foreground=Theme.TEXT_PRIMARY,
            fieldbackground=Theme.BG_TERTIARY,
            borderwidth=0,
            rowheight=28
        )
        style.configure(
            'Treeview.Heading',
            background=Theme.BG_PRIMARY,
            foreground=Theme.TEXT_PRIMARY,
            relief='flat'
        )
        style.map('Treeview',
                  background=[('selected', Theme.ACCENT_PRIMARY)])

    def set_selection_callback(self, callback: Callable):
        """Set callback for when selection changes"""
        self._selection_callback = callback

    def set_double_click_callback(self, callback: Callable):
        """Set callback for when row is double-clicked"""
        self._double_click_callback = callback

    def _on_selection_change(self, event):
        """Handle selection change"""
        if self._selection_callback:
            selected = self.tree.selection()
            if selected:
                item_id = selected[0]
                if item_id in self._card_data:
                    self._selection_callback(self._card_data[item_id])

    def _on_double_click(self, event):
        """Handle double-click"""
        if self._double_click_callback:
            selected = self.tree.selection()
            if selected:
                item_id = selected[0]
                if item_id in self._card_data:
                    self._double_click_callback(self._card_data[item_id])

    def load_cards(self, cards: List[CollectionCard]):
        """Load cards into table"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._card_data.clear()

        # Add cards
        for card_entry in cards:
            if not card_entry.card:
                continue  # Skip if card data not loaded

            card = card_entry.card

            values = (
                card.name,
                card.set_code or '',
                card.rarity or '',
                card.type_line or '',
                card_entry.quantity,
                card_entry.foil,
                card_entry.condition,
                f"${card_entry.current_price:.2f}",
                f"${card_entry.total_value:.2f}"
            )

            item_id = self.tree.insert('', 'end', values=values)
            self._card_data[item_id] = card_entry

    def filter_cards(self, query: str):
        """Filter displayed cards by search query"""
        if not query:
            # Show all
            for item in self._card_data.keys():
                try:
                    self.tree.reattach(item, '', 'end')
                except:
                    pass
            return

        query_lower = query.lower()

        for item_id, card_entry in self._card_data.items():
            if not card_entry.card:
                continue

            card = card_entry.card

            # Search in name, type, and oracle text
            searchable = f"{card.name} {card.type_line or ''} {card.oracle_text or ''}".lower()

            if query_lower in searchable:
                try:
                    self.tree.reattach(item_id, '', 'end')
                except:
                    pass
            else:
                try:
                    self.tree.detach(item_id)
                except:
                    pass

    def sort_by_column(self, col):
        """Sort table by column"""
        # Toggle sort direction if clicking same column
        if self._sort_column == col:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_reverse = False

        self._sort_column = col

        # Get all items
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]

        # Sort
        try:
            # Try numeric sort for price columns
            if col in ('value', 'total', 'quantity'):
                items.sort(
                    key=lambda x: float(x[0].replace('$', '').replace(',', '')) if x[0] else 0,
                    reverse=self._sort_reverse
                )
            else:
                items.sort(reverse=self._sort_reverse)
        except:
            items.sort(reverse=self._sort_reverse)

        # Rearrange
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)

        # Update heading to show sort direction
        for column in self.tree['columns']:
            heading = column.replace('_', ' ').title()
            if column == col:
                heading += ' ▼' if self._sort_reverse else ' ▲'
            self.tree.heading(column, text=heading)

    def get_selected_cards(self) -> List[CollectionCard]:
        """Get currently selected cards"""
        selected = self.tree.selection()
        return [self._card_data[item_id] for item_id in selected if item_id in self._card_data]


class CardDetailPanel(StyledFrame):
    """Right panel showing selected card details"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG_PRIMARY, **kwargs)

        # Title
        self.title_label = tk.Label(
            self,
            text="Card Details",
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, 12, 'bold')
        )
        self.title_label.pack(anchor='w', padx=15, pady=(15, 10))

        # Scrollable container
        canvas = tk.Canvas(self, bg=Theme.BG_PRIMARY, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.detail_frame = StyledFrame(canvas, bg=Theme.BG_PRIMARY)

        self.detail_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.detail_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")

        # Placeholder
        self._show_placeholder()

    def _show_placeholder(self):
        """Show placeholder when no card selected"""
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.detail_frame,
            text="Select a card to view details",
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_MUTED,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)
        ).pack(pady=50)

    def show_card(self, card_entry: CollectionCard):
        """Display card details"""
        # Clear existing
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        if not card_entry.card:
            self._show_placeholder()
            return

        card = card_entry.card

        # Card name
        tk.Label(
            self.detail_frame,
            text=card.name,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, 14, 'bold'),
            wraplength=280,
            justify='left'
        ).pack(anchor='w', pady=(0, 5))

        # Mana cost
        if card.mana_cost:
            tk.Label(
                self.detail_frame,
                text=card.mana_cost,
                bg=Theme.BG_PRIMARY,
                fg=Theme.TEXT_SECONDARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)
            ).pack(anchor='w', pady=(0, 10))

        # Type line
        tk.Label(
            self.detail_frame,
            text=card.type_line or '',
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
            wraplength=280,
            justify='left'
        ).pack(anchor='w', pady=(0, 10))

        # Oracle text
        if card.oracle_text:
            text_frame = StyledFrame(self.detail_frame, bg=Theme.BG_SECONDARY)
            text_frame.pack(fill=tk.X, pady=(0, 10))

            tk.Label(
                text_frame,
                text=card.oracle_text,
                bg=Theme.BG_SECONDARY,
                fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                wraplength=260,
                justify='left'
            ).pack(padx=10, pady=10)

        # Collection info
        info_frame = StyledFrame(self.detail_frame, bg=Theme.BG_SECONDARY)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self._add_info_row(info_frame, "Set:", card.set_code or 'Unknown')
        self._add_info_row(info_frame, "Rarity:", card.rarity or 'Unknown')
        self._add_info_row(info_frame, "Quantity:", str(card_entry.quantity))
        self._add_info_row(info_frame, "Foil:", card_entry.foil)
        self._add_info_row(info_frame, "Condition:", card_entry.condition)

        # Pricing info
        price_frame = StyledFrame(self.detail_frame, bg=Theme.BG_SECONDARY)
        price_frame.pack(fill=tk.X, pady=(0, 10))

        self._add_info_row(price_frame, "Market Price:", f"${card_entry.current_price:.2f}")
        self._add_info_row(price_frame, "Total Value:", f"${card_entry.total_value:.2f}", bold=True)

        if card_entry.purchase_price:
            self._add_info_row(price_frame, "Purchase Price:", f"${card_entry.purchase_price:.2f}")
            if card_entry.gain_loss:
                color = Theme.SUCCESS if card_entry.gain_loss > 0 else Theme.ERROR
                self._add_info_row(
                    price_frame,
                    "Gain/Loss:",
                    f"${card_entry.gain_loss:.2f}",
                    value_color=color
                )

    def _add_info_row(self, parent, label: str, value: str, bold: bool = False, value_color: str = None):
        """Add an info row to the detail panel"""
        row = StyledFrame(parent, bg=Theme.BG_SECONDARY)
        row.pack(fill=tk.X, padx=10, pady=2)

        tk.Label(
            row,
            text=label,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_MUTED,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
            anchor='w',
            width=15
        ).pack(side=tk.LEFT)

        font_style = (Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL, 'bold' if bold else 'normal')
        fg_color = value_color if value_color else Theme.TEXT_PRIMARY

        tk.Label(
            row,
            text=value,
            bg=Theme.BG_SECONDARY,
            fg=fg_color,
            font=font_style,
            anchor='w'
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
