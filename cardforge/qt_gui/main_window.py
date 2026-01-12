"""
CardForge Main Window
Primary application window using PyQt6
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QMenuBar, QMenu, QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QAction, QKeySequence

from .theme import THEME
from .async_bridge import AsyncBridge
from .widgets import SearchBar, StatsPanel, LoadingOverlay
from .panels import CollectionBrowserPanel, CardDetailPanel
from .panels.analytics_panel import AnalyticsPanel

from cardforge.services import CollectionService, CardService
from cardforge.models import CollectionStats


class MainWindow(QMainWindow):
    """
    Main application window.

    Layout:
    ┌─────────────────────────────────────────────────────────┐
    │ Menu Bar                                                 │
    ├─────────────────────────────────────────────────────────┤
    │ Toolbar (Search + Actions)                              │
    ├─────────────────────────────────────────────────────────┤
    │ Stats Panel (4 metrics)                                 │
    ├─────────────────────────────────────────────────────────┤
    │ ┌────────────────────────┬──────────────────────────┐  │
    │ │                        │                          │  │
    │ │  Collection Browser    │    Card Details          │  │
    │ │  (70%)                 │    (30%)                 │  │
    │ │                        │                          │  │
    │ └────────────────────────┴──────────────────────────┘  │
    ├─────────────────────────────────────────────────────────┤
    │ Status Bar                                              │
    └─────────────────────────────────────────────────────────┘
    """

    def __init__(self):
        super().__init__()

        # Services
        self.collection_service = CollectionService()
        self.card_service = CardService()

        # Async bridge
        self.async_bridge = AsyncBridge()

        # State
        self.current_collection_id: int | None = None
        self.current_stats: CollectionStats | None = None

        # Setup UI
        self._setup_window()
        self._create_menu_bar()
        self._create_central_widget()
        self._create_status_bar()

        # Load initial data
        self._load_collection()

    def _setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle("CardForge - MTG Collection Manager")
        self.setMinimumSize(1400, 800)
        self.resize(1600, 900)

    def _create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        import_action = QAction("&Import CSV...", self)
        import_action.setShortcut(QKeySequence("Ctrl+I"))
        import_action.triggered.connect(self._import_csv)
        file_menu.addAction(import_action)

        export_action = QAction("&Export Collection...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self._export_collection)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Collection Menu
        collection_menu = menubar.addMenu("&Collection")

        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self._refresh_collection)
        collection_menu.addAction(refresh_action)

        duplicates_action = QAction("Find &Duplicates", self)
        duplicates_action.triggered.connect(self._find_duplicates)
        collection_menu.addAction(duplicates_action)

        analytics_action = QAction("📊 &Analytics Dashboard", self)
        analytics_action.setShortcut(QKeySequence("Ctrl+Shift+A"))
        analytics_action.triggered.connect(self._show_analytics)
        collection_menu.addAction(analytics_action)

        collection_menu.addSeparator()

        add_card_action = QAction("&Add Card...", self)
        add_card_action.setShortcut(QKeySequence("Ctrl+N"))
        add_card_action.triggered.connect(self._add_card)
        collection_menu.addAction(add_card_action)

        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")

        sync_sets_action = QAction("Sync &Sets from Scryfall", self)
        sync_sets_action.triggered.connect(self._sync_sets)
        tools_menu.addAction(sync_sets_action)

        update_prices_action = QAction("Update &Prices", self)
        update_prices_action.triggered.connect(self._update_prices)
        tools_menu.addAction(update_prices_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About CardForge", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_central_widget(self):
        """Create the main content area."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Toolbar with search
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        self.search_bar = SearchBar()
        self.search_bar.search_triggered.connect(self._on_search)
        toolbar_layout.addWidget(self.search_bar, 1)  # Stretch

        # TODO: Add action buttons

        layout.addWidget(toolbar)

        # Stats panel
        self.stats_panel = StatsPanel()
        layout.addWidget(self.stats_panel)

        # Main content: splitter with browser and details
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.browser_panel = CollectionBrowserPanel()
        self.browser_panel.card_selected.connect(self._on_card_selected)
        splitter.addWidget(self.browser_panel)

        self.detail_panel = CardDetailPanel()
        splitter.addWidget(self.detail_panel)

        # Set initial splitter proportions (70/30)
        splitter.setSizes([700, 300])

        layout.addWidget(splitter, 1)  # Stretch

    def _create_status_bar(self):
        """Create status bar."""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
    
    def _show_analytics(self):
        """Show analytics dashboard in a separate window."""
        if not hasattr(self, 'analytics_window') or not self.analytics_window.isVisible():
            from PyQt6.QtWidgets import QDialog
            self.analytics_window = QDialog(self)
            self.analytics_window.setWindowTitle("Collection Analytics")
            self.analytics_window.resize(1200, 800)
            
            layout = QVBoxLayout(self.analytics_window)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.analytics_panel = AnalyticsPanel()
            layout.addWidget(self.analytics_panel)
            
            # Update with current stats
            if self.current_stats:
                stats_dict = {
                    'total_cards': self.current_stats.total_cards,
                    'total_value': float(self.current_stats.total_value),
                    'unique_cards': self.current_stats.unique_cards,
                    'average_price': float(self.current_stats.average_price) if self.current_stats.average_price else 0.0,
                }
                self.analytics_panel.update_stats(stats_dict)
        
        self.analytics_window.show()
        self.analytics_window.raise_()
        self.analytics_window.activateWindow()

    # =========================================================================
    # DATA LOADING
    # =========================================================================

    def _load_collection(self):
        """Load collection data asynchronously."""
        loading = LoadingOverlay(self, "Loading collection...")
        loading.show()

        async def load():
            collection = await self.collection_service.get_or_create_default()
            self.current_collection_id = collection.id

            stats = await self.collection_service.get_stats(collection.id)
            cards = await self.collection_service.get_cards(collection.id, limit=100000)

            return stats, cards

        def on_success(result):
            stats, cards = result
            self.current_stats = stats

            # Update UI
            self.stats_panel.update_stats(stats)
            self.browser_panel.load_cards(cards)

            self.statusBar.showMessage(f"Loaded {len(cards)} cards")
            loading.close()

        def on_error(error):
            loading.close()
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load collection:\n{error}"
            )
            self.statusBar.showMessage("Error loading collection")

        self.async_bridge.run_async(load(), on_success, on_error)

    @pyqtSlot()
    def _refresh_collection(self):
        """Refresh collection display."""
        self._load_collection()

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    @pyqtSlot(str)
    def _on_search(self, query: str):
        """Handle search query."""
        if query:
            self.statusBar.showMessage(f"Searching for: {query}")
            self.browser_panel.filter_cards(query)
        else:
            self.browser_panel.clear_filter()
            self.statusBar.showMessage("Ready")

    @pyqtSlot(object)
    def _on_card_selected(self, card_entry):
        """Handle card selection."""
        self.detail_panel.show_card(card_entry)
        if card_entry.card:
            self.statusBar.showMessage(f"Selected: {card_entry.card.name}")

    # =========================================================================
    # MENU ACTIONS
    # =========================================================================

    @pyqtSlot()
    def _import_csv(self):
        """Import CSV file."""
        QMessageBox.information(
            self,
            "Import CSV",
            "CSV import will be implemented in the next task."
        )

    @pyqtSlot()
    def _export_collection(self):
        """Export collection."""
        QMessageBox.information(
            self,
            "Export Collection",
            "Export functionality will be implemented soon."
        )

    @pyqtSlot()
    def _add_card(self):
        """Add card to collection."""
        QMessageBox.information(
            self,
            "Add Card",
            "Add card dialog will be implemented soon."
        )

    @pyqtSlot()
    def _find_duplicates(self):
        """Find duplicate cards."""
        loading = LoadingOverlay(self, "Finding duplicates...")
        loading.show()

        async def find():
            return await self.collection_service.find_duplicates()

        def on_success(duplicates):
            loading.close()
            if duplicates:
                QMessageBox.information(
                    self,
                    "Duplicates Found",
                    f"Found {len(duplicates)} cards with duplicates"
                )
            else:
                QMessageBox.information(
                    self,
                    "No Duplicates",
                    "No duplicate cards found"
                )

        def on_error(error):
            loading.close()
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to find duplicates:\n{error}"
            )

        self.async_bridge.run_async(find(), on_success, on_error)

    @pyqtSlot()
    def _sync_sets(self):
        """Sync sets from Scryfall."""
        reply = QMessageBox.question(
            self,
            "Sync Sets",
            "Fetch all set metadata from Scryfall?\nThis may take a few minutes.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            loading = LoadingOverlay(self, "Syncing sets from Scryfall...")
            loading.show()

            async def sync():
                return await self.card_service.sync_sets_metadata()

            def on_success(count):
                loading.close()
                QMessageBox.information(
                    self,
                    "Sync Complete",
                    f"Successfully synced {count} sets from Scryfall!"
                )

            def on_error(error):
                loading.close()
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to sync sets:\n{error}"
                )

            self.async_bridge.run_async(sync(), on_success, on_error)

    @pyqtSlot()
    def _update_prices(self):
        """Update card prices."""
        QMessageBox.information(
            self,
            "Update Prices",
            "Price update functionality will be implemented soon."
        )

    @pyqtSlot()
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About CardForge",
            """<h2>CardForge - MTG Collection Manager</h2>
            <p><b>Version:</b> 2.0.0</p>
            <p><b>Built with:</b> Python + PyQt6</p>

            <h3>Features:</h3>
            <ul>
                <li>Collection management</li>
                <li>Deck building</li>
                <li>Price tracking</li>
                <li>AI integration via MCP</li>
            </ul>

            <p><i>Magic: The Gathering is © Wizards of the Coast.<br>
            CardForge is not affiliated with or endorsed by Wizards of the Coast.</i></p>
            """
        )

    def closeEvent(self, event):
        """Handle window close event."""
        # Cancel any running async operations
        self.async_bridge.cancel_all()
        event.accept()
