"""
CardForge GUI Application
Main application window and controller
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
from pathlib import Path
from typing import Optional, List

from .async_bridge import AsyncBridge
from .theme import Theme, Icons
from .widgets import StyledFrame, StyledButton, SearchBar, LoadingOverlay, ToastNotification
from .panels import StatsPanel, CollectionBrowserPanel, CardDetailPanel

from cardforge.services import CollectionService, CardService
from cardforge.models import CollectionStats, CollectionCard


class CardForgeGUI(tk.Tk):
    """Main CardForge GUI application"""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("CardForge - MTG Collection Manager")
        self.geometry("1600x900")
        self.minsize(1400, 800)
        self.configure(bg=Theme.BG_PRIMARY)

        # Initialize async bridge
        self.async_bridge = AsyncBridge()
        self.async_bridge.start()

        # Initialize services
        self.collection_service = CollectionService()
        self.card_service = CardService()

        # State
        self.current_cards: List[CollectionCard] = []
        self.current_stats: Optional[CollectionStats] = None

        # Build UI
        self._create_menu_bar()
        self._create_toolbar()
        self._create_main_layout()
        self._create_status_bar()

        # Load initial data
        self.after(100, self._load_collection)

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # =========================================================================
    # UI CREATION
    # =========================================================================

    def _create_menu_bar(self):
        """Create application menu"""
        menubar = tk.Menu(self, bg=Theme.BG_PRIMARY, fg=Theme.TEXT_PRIMARY)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=Theme.BG_SECONDARY,
                            fg=Theme.TEXT_PRIMARY)
        file_menu.add_command(label="Import CSV...",
                              command=self._import_csv,
                              accelerator="Ctrl+I")
        file_menu.add_command(label="Export Collection...",
                              command=self._export_collection,
                              accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        # Collection menu
        collection_menu = tk.Menu(menubar, tearoff=0, bg=Theme.BG_SECONDARY,
                                  fg=Theme.TEXT_PRIMARY)
        collection_menu.add_command(label="Refresh",
                                     command=self._refresh_collection,
                                     accelerator="F5")
        collection_menu.add_command(label="Find Duplicates",
                                     command=self._find_duplicates)
        collection_menu.add_separator()
        collection_menu.add_command(label="Add Card...",
                                     command=self._add_card_dialog,
                                     accelerator="Ctrl+N")
        menubar.add_cascade(label="Collection", menu=collection_menu)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=Theme.BG_SECONDARY,
                             fg=Theme.TEXT_PRIMARY)
        tools_menu.add_command(label="Sync Sets from Scryfall",
                               command=self._sync_sets)
        tools_menu.add_command(label="Update Prices",
                               command=self._update_prices)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=Theme.BG_SECONDARY,
                            fg=Theme.TEXT_PRIMARY)
        help_menu.add_command(label="About CardForge",
                              command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

        # Bind keyboard shortcuts
        self.bind('<Control-i>', lambda e: self._import_csv())
        self.bind('<Control-e>', lambda e: self._export_collection())
        self.bind('<Control-n>', lambda e: self._add_card_dialog())
        self.bind('<F5>', lambda e: self._refresh_collection())

    def _create_toolbar(self):
        """Create main toolbar"""
        toolbar = StyledFrame(self, bg=Theme.BG_PRIMARY)
        toolbar.pack(fill=tk.X, padx=10, pady=(10, 0))

        # Search bar
        self.search_bar = SearchBar(
            toolbar,
            on_search=self._on_search,
            placeholder="Search your collection..."
        )
        self.search_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Action buttons
        StyledButton(
            toolbar,
            text=f"{Icons.REFRESH} Refresh",
            command=self._refresh_collection,
            variant="secondary"
        ).pack(side=tk.RIGHT, padx=(5, 0))

        StyledButton(
            toolbar,
            text=f"{Icons.IMPORT} Import",
            command=self._import_csv,
            variant="secondary"
        ).pack(side=tk.RIGHT, padx=(5, 0))

    def _create_main_layout(self):
        """Create main content area"""
        # Container
        main_container = StyledFrame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Stats panel at top
        self.stats_panel = StatsPanel(main_container)
        self.stats_panel.pack(fill=tk.X, pady=(0, 10))

        # Paned window for resizable panels
        paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left: Collection browser (70%)
        self.browser_panel = CollectionBrowserPanel(paned)
        self.browser_panel.set_selection_callback(self._on_card_selected)
        self.browser_panel.set_double_click_callback(self._on_card_double_click)
        paned.add(self.browser_panel, weight=70)

        # Right: Card details (30%)
        self.detail_panel = CardDetailPanel(paned)
        paned.add(self.detail_panel, weight=30)

    def _create_status_bar(self):
        """Create bottom status bar"""
        status_frame = StyledFrame(self, bg=Theme.BG_SECONDARY)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(
            status_frame,
            textvariable=self.status_var,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
            anchor='w'
        ).pack(side=tk.LEFT, padx=10, pady=5)

        # Card count label
        self.count_var = tk.StringVar(value="")
        tk.Label(
            status_frame,
            textvariable=self.count_var,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
            anchor='e'
        ).pack(side=tk.RIGHT, padx=10, pady=5)

    # =========================================================================
    # DATA LOADING
    # =========================================================================

    def _load_collection(self):
        """Load collection data"""
        loading = LoadingOverlay(self, "Loading collection...")

        def on_success(result):
            stats, cards = result
            self.current_stats = stats
            self.current_cards = cards

            # Update UI
            if stats:
                self.stats_panel.update_stats(stats)
            if cards:
                self.browser_panel.load_cards(cards)
                self.count_var.set(f"{len(cards)} cards loaded")

            self.status_var.set("Collection loaded successfully")
            loading.close()

        def on_error(error):
            loading.close()
            messagebox.showerror("Error", f"Failed to load collection:\n{error}")
            self.status_var.set("Error loading collection")

        # Run async
        async def load():
            collection = await self.collection_service.get_or_create_default()
            stats = await self.collection_service.get_stats(collection.id)
            cards = await self.collection_service.get_cards(collection.id, limit=1000)
            return stats, cards

        self.async_bridge.run_async(
            load(),
            callback=on_success,
            error_callback=on_error
        )

    def _refresh_collection(self):
        """Refresh collection display"""
        self._load_collection()
        ToastNotification.show(self, "Collection refreshed", type='success')

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    def _on_search(self, query: str):
        """Handle search"""
        if query:
            self.status_var.set(f"Searching for: {query}")
            self.browser_panel.filter_cards(query)
        else:
            # Clear filter
            self.browser_panel.load_cards(self.current_cards)
            self.status_var.set("Ready")

    def _on_card_selected(self, card_entry: CollectionCard):
        """Handle card selection"""
        if card_entry.card:
            self.detail_panel.show_card(card_entry)
            self.status_var.set(f"Selected: {card_entry.card.name}")

    def _on_card_double_click(self, card_entry: CollectionCard):
        """Handle card double-click"""
        # Could open edit dialog or Scryfall page
        pass

    # =========================================================================
    # MENU ACTIONS
    # =========================================================================

    def _import_csv(self):
        """Import CSV file"""
        filename = filedialog.askopenfilename(
            title="Import Collection CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filename:
            # TODO: Implement CSV import via service
            messagebox.showinfo("Import", f"CSV import not yet implemented.\nFile: {filename}")

    def _export_collection(self):
        """Export collection"""
        filename = filedialog.asksaveasfilename(
            title="Export Collection",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")]
        )

        if filename:
            # TODO: Implement export via service
            messagebox.showinfo("Export", f"Export not yet implemented.\nFile: {filename}")

    def _add_card_dialog(self):
        """Show add card dialog"""
        # TODO: Implement add card dialog
        messagebox.showinfo("Add Card", "Add card dialog not yet implemented")

    def _find_duplicates(self):
        """Find duplicate cards"""
        loading = LoadingOverlay(self, "Finding duplicates...")

        def on_success(duplicates):
            loading.close()
            if duplicates:
                # TODO: Show duplicates in a dialog
                messagebox.showinfo(
                    "Duplicates Found",
                    f"Found {len(duplicates)} cards with duplicates"
                )
            else:
                messagebox.showinfo("Duplicates", "No duplicates found")

        def on_error(error):
            loading.close()
            messagebox.showerror("Error", f"Failed to find duplicates:\n{error}")

        self.async_bridge.run_async(
            self.collection_service.find_duplicates(),
            callback=on_success,
            error_callback=on_error
        )

    def _sync_sets(self):
        """Sync sets from Scryfall"""
        result = messagebox.askyesno(
            "Sync Sets",
            "Fetch all set metadata from Scryfall?\nThis may take a few minutes."
        )

        if result:
            loading = LoadingOverlay(self, "Syncing sets from Scryfall...")

            def on_success(count):
                loading.close()
                ToastNotification.show(
                    self,
                    f"Synced {count} sets successfully!",
                    type='success'
                )

            def on_error(error):
                loading.close()
                messagebox.showerror("Error", f"Failed to sync sets:\n{error}")

            self.async_bridge.run_async(
                self.card_service.sync_sets_metadata(),
                callback=on_success,
                error_callback=on_error
            )

    def _update_prices(self):
        """Update card prices"""
        messagebox.showinfo("Update Prices", "Price update not yet implemented")

    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About CardForge",
            "CardForge - MTG Collection Manager\n\n"
            "Version: 1.0.0\n\n"
            "Features:\n"
            "• Collection management\n"
            "• Deck building\n"
            "• Price tracking\n"
            "• AI integration via MCP\n\n"
            "Built with Python + Tkinter"
        )

    # =========================================================================
    # CLEANUP
    # =========================================================================

    def _on_close(self):
        """Handle window close"""
        self.async_bridge.stop()
        self.destroy()


def main():
    """Application entry point"""
    try:
        app = CardForgeGUI()
        app.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")
        messagebox.showerror("Fatal Error", f"Application crashed:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
