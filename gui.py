#!/usr/bin/env python3
"""
MyManaBox GUI - Modern MTG Collection Management Interface
A comprehensive graphical interface for viewing and managing your Magic: The Gathering collection.
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from typing import List, Dict, Optional
import json

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.data import CSVLoader, ScryfallClient
    from src.services import CollectionService, SearchService, AnalyticsService
    from src.models import Collection, Card
    from src.utils import Constants
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure you're running from the MyManaBox directory")
    sys.exit(1)


class CardTableWidget:
    """Advanced table widget for displaying card collection data."""
    
    def __init__(self, parent, on_selection_change=None):
        self.parent = parent
        self.on_selection_change = on_selection_change
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview with scrollbars
        self.tree_frame = ttk.Frame(self.frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Define columns based on the target interface
        self.columns = [
            "Qty", "Name", "Set", "Condition", "Language", "Foil", 
            "Rarity", "Type", "CMC", "Colors", "Price", "Total"
        ]
        
        self.tree = ttk.Treeview(self.tree_frame, columns=self.columns, show='headings', height=25)
        
        # Configure column headers and widths to match target
        column_widths = {
            "Qty": 50, "Name": 250, "Set": 180, "Condition": 90, "Language": 70,
            "Foil": 50, "Rarity": 90, "Type": 200, "CMC": 50, "Colors": 70,
            "Price": 80, "Total": 80
        }
        
        # Configure columns with better alignment
        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            width = column_widths.get(col, 100)
            self.tree.column(col, width=width, minwidth=50)
            
            # Center align numeric columns
            if col in ["Qty", "CMC", "Price", "Total"]:
                self.tree.column(col, anchor='center')
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self._on_selection)
        
        # Store sort direction
        self.sort_reverse = {}
        
        # Store current data
        self.current_data = []
    
    def sort_column(self, col):
        """Sort treeview by column."""
        reverse = self.sort_reverse.get(col, False)
        self.sort_reverse[col] = not reverse
        
        # Get all items and sort
        items = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        
        # Convert to appropriate type for sorting
        try:
            # Try numeric sort first
            items = [(float(str(val).replace('$', '').replace(',', '') if val else 0), child) for val, child in items]
        except ValueError:
            # Fall back to string sort
            items = [(str(val).lower(), child) for val, child in items]
        
        items.sort(reverse=reverse)
        
        # Rearrange items in tree
        for index, (val, child) in enumerate(items):
            self.tree.move(child, '', index)
    
    def _on_selection(self, event):
        """Handle selection change."""
        if self.on_selection_change:
            selected_items = self.tree.selection()
            if selected_items:
                item = selected_items[0]
                values = self.tree.item(item, 'values')
                self.on_selection_change(values)
    
    def populate_data(self, cards: List[Card]):
        """Populate the table with card data."""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.current_data = cards

        # Add card data
        for card in cards:
            # Use the same price priority as the card model: purchase price first, then market value
            price_val = float(card.purchase_price) if card.purchase_price else (float(card.market_value) if card.market_value else 0.0)
            total_val = price_val * card.count if price_val else 0.0
            
            values = [
                str(card.count),
                card.name,
                card.set_name or card.edition,
                card.condition.value if card.condition else "NM",
                "EN",  # Default language
                "Foil" if card.foil else "",  # Fixed: Show "Foil" only for foil cards, empty for non-foil
                card.rarity.value if card.rarity else "",
                card.type_line or "",
                str(card.cmc) if card.cmc else "",
                "|".join(c.value for c in card.colors) if card.colors else "",
                f"${price_val:.2f}" if price_val > 0 else "",
                f"${total_val:.2f}" if total_val > 0 else ""
            ]
            self.tree.insert('', 'end', values=values)
    
    def filter_data(self, search_term: str):
        """Filter the displayed data based on search term."""
        if not search_term:
            self.populate_data(self.current_data)
            return
        
        filtered_cards = [
            card for card in self.current_data
            if search_term.lower() in card.name.lower() or
               search_term.lower() in card.edition.lower() or
               (card.type_line and search_term.lower() in card.type_line.lower())
        ]
        
        # Clear and repopulate with filtered data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for card in filtered_cards:
            # Calculate total value
            market_val = float(card.market_value) if card.market_value else 0.0
            total_val = market_val * card.count if market_val else 0.0
            
            values = [
                str(card.count),
                card.name,
                card.set_name or card.edition,
                card.condition.value if card.condition else "NM",
                "EN",
                "Yes" if card.foil else "",
                card.rarity.value if card.rarity else "",
                card.type_line or "",
                str(card.cmc) if card.cmc else "",
                "|".join(c.value for c in card.colors) if card.colors else "",
                f"${market_val:.2f}" if market_val > 0 else "",
                f"${total_val:.2f}" if total_val > 0 else ""
            ]
            self.tree.insert('', 'end', values=values)


class CardDetailPanel:
    """Panel showing detailed information about selected card."""
    
    def __init__(self, parent, main_gui=None):
        self.frame = ttk.LabelFrame(parent, text="Card Details", padding=15)
        self.frame.pack(fill=tk.X, pady=(0, 10))
        self.main_gui = main_gui
        
        # Create detail labels with better spacing
        self.detail_vars = {}
        detail_fields = [
            ("Name", "name"), ("Set", "set"), ("Rarity", "rarity"),
            ("Type", "type"), ("Mana Cost", "mana_cost"), ("CMC", "cmc"),
            ("Power/Toughness", "pt"), ("Market Price", "price")
        ]
        
        for i, (label, key) in enumerate(detail_fields):
            # Create frame for each field
            field_frame = ttk.Frame(self.frame)
            field_frame.pack(fill=tk.X, pady=3)
            
            # Label
            ttk.Label(field_frame, text=f"{label}:", 
                     font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, anchor='w')
            
            # Value
            var = tk.StringVar()
            self.detail_vars[key] = var
            ttk.Label(field_frame, textvariable=var, 
                     font=('Segoe UI', 9)).pack(side=tk.RIGHT, anchor='e')
        
        # Oracle text in a separate section
        oracle_frame = ttk.Frame(self.frame)
        oracle_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        ttk.Label(oracle_frame, text="Oracle Text:", 
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w')
        
        # Text widget for oracle text
        text_frame = ttk.Frame(oracle_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        self.oracle_text_widget = tk.Text(text_frame, height=6, width=30, wrap=tk.WORD, 
                                        font=('Segoe UI', 8),
                                        bg='#404040', fg='white', borderwidth=1,
                                        relief='solid', insertbackground='white')
        self.oracle_text_widget.pack(fill=tk.BOTH, expand=True)
    
    def update_details(self, card_values):
        """Update the detail panel with selected card information."""
        if not card_values or len(card_values) < 2:
            self.clear_details()
            return

        # Find the actual card object from the current data
        card_name = card_values[1] if len(card_values) > 1 else ""
        
        # Try to find the card in the current collection for full details
        found_card = None
        if self.main_gui and self.main_gui.current_collection:
            for card in self.main_gui.current_collection.cards:
                if card.name == card_name:
                    found_card = card
                    break
        
        if found_card:
            # Use full card data
            self.detail_vars["name"].set(found_card.name)
            self.detail_vars["set"].set(found_card.set_name or found_card.edition)
            self.detail_vars["rarity"].set(found_card.rarity.value if found_card.rarity else "")
            self.detail_vars["type"].set(found_card.type_line or "")
            self.detail_vars["mana_cost"].set(found_card.mana_cost or "")
            self.detail_vars["cmc"].set(str(found_card.cmc) if found_card.cmc else "")
            
            # Power/Toughness or Loyalty
            pt_text = ""
            if found_card.power and found_card.toughness:
                pt_text = f"{found_card.power}/{found_card.toughness}"
            elif found_card.loyalty:
                pt_text = f"Loyalty: {found_card.loyalty}"
            self.detail_vars["pt"].set(pt_text)
            
            self.detail_vars["price"].set(f"${found_card.market_value:.2f}" if found_card.market_value else "")
            
            # Oracle text
            self.oracle_text_widget.delete(1.0, tk.END)
            if found_card.oracle_text:
                self.oracle_text_widget.insert(1.0, found_card.oracle_text)
            else:
                self.oracle_text_widget.insert(1.0, "No oracle text available")
        else:
            # Fall back to table values
            self.detail_vars["name"].set(card_values[1] if len(card_values) > 1 else "")
            self.detail_vars["set"].set(card_values[2] if len(card_values) > 2 else "")
            self.detail_vars["rarity"].set(card_values[6] if len(card_values) > 6 else "")
            self.detail_vars["type"].set(card_values[7] if len(card_values) > 7 else "")
            self.detail_vars["mana_cost"].set("")
            self.detail_vars["cmc"].set(card_values[8] if len(card_values) > 8 else "")
            self.detail_vars["pt"].set("")
            self.detail_vars["price"].set(card_values[10] if len(card_values) > 10 else "")
            
            self.oracle_text_widget.delete(1.0, tk.END)
            self.oracle_text_widget.insert(1.0, "Card details not available")
    
    def clear_details(self):
        """Clear all detail fields."""
        for var in self.detail_vars.values():
            var.set("")
        self.oracle_text_widget.delete(1.0, tk.END)


class CollectionStatsPanel:
    """Panel showing collection statistics."""
    
    def __init__(self, parent):
        # Main stats frame with modern styling
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.X, pady=(0, 10))
        
        # Stats container with better layout
        stats_container = ttk.Frame(self.frame)
        stats_container.pack(fill=tk.X)
        
        # Define stat labels with improved styling
        self.stat_vars = {}
        stats = [
            ("Total Cards:", "total_cards"),
            ("Unique Cards:", "unique_cards"), 
            ("Total Value:", "total_value"),
            ("Average Value:", "avg_value")
        ]
        
        # Create stats in a horizontal layout
        for i, (label, key) in enumerate(stats):
            stat_frame = ttk.Frame(stats_container)
            stat_frame.pack(side=tk.LEFT, padx=(0, 30) if i < len(stats)-1 else (0, 0))
            
            # Label
            label_widget = ttk.Label(stat_frame, text=label, font=('Segoe UI', 10, 'bold'))
            label_widget.pack(anchor='w')
            
            # Value
            var = tk.StringVar()
            self.stat_vars[key] = var
            value_widget = ttk.Label(stat_frame, textvariable=var, font=('Segoe UI', 14, 'bold'))
            value_widget.pack(anchor='w')
        
        # Add a separator line
        separator = ttk.Separator(self.frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(10, 0))
    
    def update_stats(self, collection: Collection):
        """Update statistics from collection."""
        self.stat_vars["total_cards"].set(f"{collection.total_cards:,}")
        self.stat_vars["unique_cards"].set(f"{collection.unique_cards:,}")
        self.stat_vars["total_value"].set(f"${collection.total_value:,.2f}")
        
        avg_value = collection.total_value / collection.total_cards if collection.total_cards > 0 else 0
        self.stat_vars["avg_value"].set(f"${avg_value:.2f}")


class MyManaBoxGUI:
    """Main GUI application for MyManaBox."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MyManaBox - MTG Collection Manager")
        self.root.geometry("1600x900")
        self.root.minsize(1200, 700)
        
        # Initialize services
        self.csv_loader = None
        self.collection_service = None
        self.search_service = None
        self.current_collection = None
        
        # Setup GUI
        self.setup_styles()
        self.create_menu()
        self.create_toolbar()
        self.create_main_interface()
        self.create_status_bar()
        
        # Load default collection if available
        self.load_default_collection()
    
    def setup_styles(self):
        """Configure ttk styles for modern appearance."""
        style = ttk.Style()
        
        # Set a modern theme
        style.theme_use('clam')
        
        # Define color scheme (dark theme)
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        select_color = '#404040'
        accent_color = '#0078d4'
        header_color = '#333333'
        
        # Configure root window
        self.root.configure(bg=bg_color)
        
        # Configure general styles
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 14, 'bold'), 
                       background=bg_color, 
                       foreground=fg_color)
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 11, 'bold'), 
                       background=bg_color, 
                       foreground=fg_color)
        
        # Configure treeview for modern look
        style.configure('Treeview', 
                       background=bg_color,
                       foreground=fg_color,
                       fieldbackground=bg_color,
                       borderwidth=0,
                       rowheight=28,
                       font=('Segoe UI', 9))
        
        style.configure('Treeview.Heading', 
                       background=header_color,
                       foreground=fg_color,
                       borderwidth=1,
                       relief='flat',
                       font=('Segoe UI', 9, 'bold'))
        
        style.map('Treeview.Heading',
                 background=[('active', accent_color)])
        
        style.map('Treeview',
                 background=[('selected', accent_color)],
                 foreground=[('selected', fg_color)])
        
        # Configure frames
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelFrame', 
                       background=bg_color,
                       foreground=fg_color,
                       borderwidth=1,
                       relief='solid')
        style.configure('TLabelFrame.Label', 
                       background=bg_color,
                       foreground=fg_color,
                       font=('Segoe UI', 10, 'bold'))
        
        # Configure labels
        style.configure('TLabel', 
                       background=bg_color,
                       foreground=fg_color,
                       font=('Segoe UI', 9))
        
        # Configure buttons
        style.configure('TButton',
                       background=accent_color,
                       foreground=fg_color,
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 9))
        
        style.map('TButton',
                 background=[('active', '#106ebe'),
                            ('pressed', '#005a9e')])
        
        # Configure entry widgets
        style.configure('TEntry',
                       fieldbackground=select_color,
                       borderwidth=1,
                       insertcolor=fg_color,
                       foreground=fg_color,
                       font=('Segoe UI', 9))
        
        # Configure combobox
        style.configure('TCombobox',
                       fieldbackground=select_color,
                       borderwidth=1,
                       foreground=fg_color,
                       font=('Segoe UI', 9))
        
        # Configure checkbutton
        style.configure('TCheckbutton',
                       background=bg_color,
                       foreground=fg_color,
                       focuscolor='none',
                       font=('Segoe UI', 9))
    
    def create_menu(self):
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Collection...", command=self.open_collection)
        file_menu.add_command(label="Import from Moxfield...", command=self.import_moxfield)
        file_menu.add_separator()
        file_menu.add_command(label="Export Collection...", command=self.export_collection)
        file_menu.add_command(label="Export Enriched...", command=self.export_enriched)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Enrich Collection", command=self.enrich_collection)
        tools_menu.add_command(label="Update Prices", command=self.update_prices)
        tools_menu.add_command(label="Verify Collection", command=self.verify_collection)
        tools_menu.add_separator()
        tools_menu.add_command(label="Enhanced Price Update", command=self.enhanced_price_update)
        tools_menu.add_command(label="Analytics", command=self.show_analytics)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_toolbar(self):
        """Create toolbar with common actions."""
        # Main toolbar frame with padding
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        # Left side - Collection info and filters
        left_frame = ttk.Frame(toolbar)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Collection title
        title_label = ttk.Label(left_frame, text="Collection Overview", style='Title.TLabel')
        title_label.pack(side=tk.LEFT, anchor='w')
        
        # Search frame (moved to right side)
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.RIGHT)
        
        # Search with modern styling
        ttk.Label(search_frame, text="Search:", style='Header.TLabel').pack(side=tk.LEFT, padx=(0, 8))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25, font=('Segoe UI', 10))
        search_entry.pack(side=tk.LEFT, padx=(0, 8))
        
        # Action buttons with modern styling
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Refresh", command=self.refresh_collection).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Enrich", command=self.enrich_collection).pack(side=tk.LEFT, padx=2)
    
    def create_main_interface(self):
        """Create the main interface layout."""
        # Main container with better padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 10))
        
        # Top stats panel (similar to target)
        self.stats_panel = CollectionStatsPanel(main_container)
        
        # Main content area with paned window
        content_paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        content_paned.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel for table (larger portion)
        left_panel = ttk.Frame(content_paned)
        content_paned.add(left_panel, weight=4)
        
        # Card table with modern styling
        self.card_table = CardTableWidget(left_panel, on_selection_change=self.on_card_selection)
        
        # Right panel for details and filters (smaller portion)
        right_panel = ttk.Frame(content_paned)
        content_paned.add(right_panel, weight=1)
        
        # Card details panel
        self.detail_panel = CardDetailPanel(right_panel, main_gui=self)
        
        # Filters panel
        self.create_filter_panel(right_panel)
    
    def create_filter_panel(self, parent):
        """Create filter options panel."""
        filter_frame = ttk.LabelFrame(parent, text="Filters", padding=15)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Rarity filter
        rarity_frame = ttk.Frame(filter_frame)
        rarity_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(rarity_frame, text="Rarity:", font=('Segoe UI', 9, 'bold')).pack(anchor='w')
        self.rarity_var = tk.StringVar()
        rarity_combo = ttk.Combobox(rarity_frame, textvariable=self.rarity_var, 
                                  values=["All", "Common", "Uncommon", "Rare", "Mythic"],
                                  state='readonly', width=15)
        rarity_combo.pack(fill=tk.X, pady=(2, 0))
        rarity_combo.set("All")
        
        # Set filter
        set_frame = ttk.Frame(filter_frame)
        set_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(set_frame, text="Set:", font=('Segoe UI', 9, 'bold')).pack(anchor='w')
        self.set_var = tk.StringVar()
        self.set_combo = ttk.Combobox(set_frame, textvariable=self.set_var,
                                     state='readonly', width=15)
        self.set_combo.pack(fill=tk.X, pady=(2, 0))
        self.set_combo.set("All")
        
        # Foil filter
        foil_frame = ttk.Frame(filter_frame)
        foil_frame.pack(fill=tk.X, pady=5)
        
        self.foil_var = tk.BooleanVar()
        ttk.Checkbutton(foil_frame, text="Foils Only", 
                       variable=self.foil_var).pack(anchor='w')
        
        # Apply filters button
        ttk.Button(filter_frame, text="Apply Filters", 
                  command=self.apply_filters).pack(fill=tk.X, pady=(10, 0))
    
    def create_status_bar(self):
        """Create status bar."""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=(0, 10))
        
        # Add separator
        separator = ttk.Separator(status_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 5))
        
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, 
                              font=('Segoe UI', 9), anchor=tk.W)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def load_default_collection(self):
        """Load the default collection if available."""
        try:
            csv_path = Path("data/enriched_collection_complete.csv")
            if csv_path.exists():
                self.load_collection_from_file(str(csv_path))
            elif Path("data/moxfield_export.csv").exists():
                self.load_collection_from_file("data/moxfield_export.csv")
            else:
                self.status_var.set("No collection found. Use File > Open Collection to load data.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load default collection: {e}")
    
    def load_collection_from_file(self, file_path: str):
        """Load collection from specified file."""
        try:
            self.status_var.set("Loading collection...")
            self.root.update()
            
            # Initialize services
            self.csv_loader = CSVLoader(file_path)
            scryfall_client = ScryfallClient()
            self.collection_service = CollectionService(self.csv_loader, scryfall_client)
            
            # Load collection
            if self.collection_service.load_collection():
                self.current_collection = self.collection_service.get_collection()
                
                if self.current_collection:
                    # Update GUI
                    self.card_table.populate_data(self.current_collection.cards)
                    self.stats_panel.update_stats(self.current_collection)
                    
                    # Update set filter options
                    sets = sorted(set(card.set_name or card.edition for card in self.current_collection.cards 
                                    if card.set_name or card.edition))
                    # Update set combobox values
                    if hasattr(self, 'set_combo'):
                        self.set_combo['values'] = ["All"] + sets
                    
                    self.status_var.set(f"Loaded {self.current_collection.total_cards} cards "
                                      f"({self.current_collection.unique_cards} unique)")
                else:
                    self.status_var.set("Failed to load collection")
            else:
                messagebox.showerror("Error", "Failed to load collection from file")
                self.status_var.set("Failed to load collection")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading collection: {e}")
            self.status_var.set("Error loading collection")
    
    def on_search_change(self, *args):
        """Handle search text change."""
        if hasattr(self, 'card_table'):
            search_term = self.search_var.get()
            self.card_table.filter_data(search_term)
    
    def clear_search(self):
        """Clear search field."""
        self.search_var.set("")
    
    def on_card_selection(self, card_values):
        """Handle card selection in table."""
        self.detail_panel.update_details(card_values)
    
    def apply_filters(self):
        """Apply selected filters to the collection view."""
        if not self.current_collection:
            return
        
        filtered_cards = self.current_collection.cards
        
        # Apply rarity filter
        rarity_filter = self.rarity_var.get()
        if rarity_filter and rarity_filter != "All":
            filtered_cards = [card for card in filtered_cards 
                             if card.rarity and card.rarity.value.lower() == rarity_filter.lower()]
        
        # Apply set filter
        set_filter = self.set_var.get()
        if set_filter and set_filter != "All":
            filtered_cards = [card for card in filtered_cards 
                             if (card.set_name and set_filter in card.set_name) or 
                                (card.edition and set_filter in card.edition)]
        
        # Apply foil filter
        if self.foil_var.get():
            filtered_cards = [card for card in filtered_cards if card.foil]
        
        # Apply search filter if active
        search_term = self.search_var.get()
        if search_term:
            filtered_cards = [
                card for card in filtered_cards
                if search_term.lower() in card.name.lower() or
                   (card.edition and search_term.lower() in card.edition.lower()) or
                   (card.type_line and search_term.lower() in card.type_line.lower())
            ]
        
        # Update table
        self.card_table.populate_data(filtered_cards)
        self.status_var.set(f"Showing {len(filtered_cards)} cards")
    
    def refresh_collection(self):
        """Refresh the collection display."""
        if self.current_collection:
            self.card_table.populate_data(self.current_collection.cards)
            self.stats_panel.update_stats(self.current_collection)
            self.status_var.set("Collection refreshed")
    
    # Menu command methods
    def open_collection(self):
        """Open collection file dialog."""
        file_path = filedialog.askopenfilename(
            title="Open Collection",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.load_collection_from_file(file_path)
    
    def import_moxfield(self):
        """Import from Moxfield export."""
        file_path = filedialog.askopenfilename(
            title="Import Moxfield Export",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.load_collection_from_file(file_path)
    
    def export_collection(self):
        """Export collection to CSV."""
        if not self.current_collection:
            messagebox.showwarning("Warning", "No collection loaded")
            return
        
        if not self.collection_service:
            messagebox.showerror("Error", "Collection service not initialized")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Collection",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            try:
                self.collection_service.save_collection(file_path)
                messagebox.showinfo("Success", f"Collection exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def export_enriched(self):
        """Export enriched collection."""
        if not self.current_collection:
            messagebox.showwarning("Warning", "No collection loaded")
            return
        
        if not self.collection_service:
            messagebox.showerror("Error", "Collection service not initialized")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Enriched Collection",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            try:
                # For now, just export the regular collection since export_enriched_collection doesn't exist
                self.collection_service.save_collection(file_path)
                messagebox.showinfo("Success", f"Collection exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export collection: {e}")
    
    def enrich_collection(self):
        """Enrich collection with Scryfall data."""
        if not self.current_collection:
            messagebox.showwarning("Warning", "No collection loaded")
            return
        
        if not self.collection_service:
            messagebox.showerror("Error", "Collection service not initialized")
            return
        
        result = messagebox.askyesno("Enrich Collection", 
                                   "This will fetch data from Scryfall API. Continue?")
        if result:
            try:
                self.status_var.set("Enriching collection...")
                self.root.update()
                
                enriched_count = self.collection_service.enrich_collection_data()
                
                # Refresh display
                self.refresh_collection()
                
                messagebox.showinfo("Success", f"Enriched {enriched_count} cards with Scryfall data")
                self.status_var.set(f"Enriched {enriched_count} cards")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to enrich collection: {e}")
                self.status_var.set("Enrichment failed")
    
    def update_prices(self):
        """Update card prices from Scryfall."""
        messagebox.showinfo("Update Prices", "Price update functionality would be implemented here")
    
    def show_analytics(self):
        """Show collection analytics window."""
        messagebox.showinfo("Analytics", "Analytics window would be implemented here")
    
    def show_about(self):
        """Show about dialog."""
        about_text = """MyManaBox GUI v1.0
        
A comprehensive Magic: The Gathering collection manager with Scryfall integration.

Features:
• View and manage your MTG collection
• Enrich cards with Scryfall data
• Search and filter capabilities
• Collection statistics and analytics
• Import/Export functionality

Built with Python and tkinter."""
        
        messagebox.showinfo("About MyManaBox", about_text)
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point for the GUI application."""
    try:
        app = MyManaBoxGUI()
        app.run()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        messagebox.showerror("Error", f"Failed to start MyManaBox GUI: {e}")


if __name__ == "__main__":
    main()
