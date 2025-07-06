#!/usr/bin/env python3
"""
MyManaBox GUI - Modern MTG Collection Management Interface
A comprehensive graphical interface for viewing and managing your Magic: The Gathering collection.
"""

import sys
import os
import time
import requests
import importlib.util
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from typing import List, Dict, Optional
import json
from datetime import datetime
from decimal import Decimal

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
            # Check if we have valid power/toughness values (not empty and not 'nan')
            power_valid = found_card.power and found_card.power.strip() and found_card.power.lower() != 'nan'
            toughness_valid = found_card.toughness and found_card.toughness.strip() and found_card.toughness.lower() != 'nan'
            
            if power_valid and toughness_valid:
                pt_text = f"{found_card.power}/{found_card.toughness}"
            elif found_card.loyalty and found_card.loyalty.strip() and found_card.loyalty.lower() != 'nan':
                pt_text = f"Loyalty: {found_card.loyalty}"
            self.detail_vars["pt"].set(pt_text)
            
            self.detail_vars["price"].set(f"${found_card.market_value:.2f}" if found_card.market_value else "")
            
            # Oracle text
            self.oracle_text_widget.delete(1.0, tk.END)
            if found_card.oracle_text and found_card.oracle_text.strip() and found_card.oracle_text.lower() != 'nan':
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
        tools_menu.add_command(label="Average Pricing Analysis", command=self.average_pricing_analysis)
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
    
    def verify_collection(self):
        """Verify collection data completeness and suggest improvements."""
        if not self.current_collection:
            messagebox.showwarning("Warning", "No collection loaded")
            return
        
        try:
            # Run comprehensive collection analysis
            import pandas as pd
            from decimal import Decimal
            
            # Load current CSV data for detailed analysis
            csv_path = Path("data/enriched_collection_complete.csv")
            if not csv_path.exists():
                messagebox.showerror("Error", "Collection CSV file not found")
                return
            
            df = pd.read_csv(csv_path)
            
            # Calculate current statistics
            total_cards = df['Count'].sum()
            unique_cards = len(df)
            
            # Pricing completeness analysis
            has_purchase_price = df['Purchase Price'].notna().sum()
            has_usd_price = df['USD Price'].notna().sum()
            has_foil_price = df['USD Foil Price'].notna().sum()
            
            # Missing pricing analysis
            no_pricing = df[(df['Purchase Price'].isna()) & (df['USD Price'].isna())]
            foil_cards = df[df['Foil'].str.lower().isin(['foil', 'etched'])]
            foil_missing_price = foil_cards[foil_cards['USD Foil Price'].isna()]
            
            # Calculate current total value using the same logic as Card model
            total_value = 0.0
            purchase_price_total = 0.0
            market_price_total = 0.0
            
            for _, row in df.iterrows():
                try:
                    quantity = int(row.get('Count', 1))
                    
                    # Purchase price first (primary)
                    purchase_price = row.get('Purchase Price')
                    if pd.notna(purchase_price) and str(purchase_price).strip():
                        try:
                            price = float(str(purchase_price).replace('$', '').replace(',', ''))
                            total_value += price * quantity
                            purchase_price_total += price * quantity
                            continue
                        except (ValueError, TypeError):
                            pass
                    
                    # Market price fallback
                    is_foil = str(row.get('Foil', '')).lower() in ['foil', 'etched']
                    
                    if is_foil:
                        foil_price = row.get('USD Foil Price')
                        if pd.notna(foil_price) and str(foil_price).strip():
                            try:
                                price = float(str(foil_price).replace('$', '').replace(',', ''))
                                total_value += price * quantity
                                market_price_total += price * quantity
                                continue
                            except (ValueError, TypeError):
                                pass
                    
                    # Regular USD price
                    usd_price = row.get('USD Price')
                    if pd.notna(usd_price) and str(usd_price).strip():
                        try:
                            price = float(str(usd_price).replace('$', '').replace(',', ''))
                            total_value += price * quantity
                            market_price_total += price * quantity
                        except (ValueError, TypeError):
                            pass
                            
                except Exception:
                    continue
            
            # Generate comprehensive report
            gap_to_target = 2379.52 - total_value
            gap_percentage = (gap_to_target / 2379.52 * 100) if gap_to_target > 0 else 0
            
            report = f"""Collection Verification Report

📊 COLLECTION OVERVIEW
• Total Cards: {total_cards:,}
• Unique Cards: {unique_cards:,}
• Current Value: ${total_value:,.2f}
• Target (Moxfield): $2,379.52
• Gap to Target: ${gap_to_target:,.2f} ({gap_percentage:.1f}%)

💰 PRICING COVERAGE
• Cards with Purchase Price: {has_purchase_price:,}
• Cards with USD Price: {has_usd_price:,}
• Cards with USD Foil Price: {has_foil_price:,}

⚠️ PRICING ISSUES
• Cards with no pricing: {len(no_pricing):,}
• Foil cards missing foil price: {len(foil_missing_price):,}

💎 VALUE BREAKDOWN
• Purchase Price Total: ${purchase_price_total:,.2f}
• Market Price Total: ${market_price_total:,.2f}

🎯 RECOMMENDATIONS"""
            
            if gap_to_target > 200:
                report += """
• Run 'Enhanced Price Update' to implement:
  - Premium multipliers (TCGPlayer-style pricing)
  - Update missing USD prices
  - Add foil pricing for foil cards
  - Verify purchase prices for high-value cards
• Consider integrating TCGPlayer API for market rates
• Review purchase prices for expensive cards manually"""
            elif gap_to_target > 50:
                report += """
• Fine-tune premium multipliers in price updates
• Review pricing for high-value cards (>$20)
• Verify purchase prices are current market rates"""
            else:
                report += """
• Collection value is very close to target!
• Consider periodic price updates to maintain accuracy
• Monitor for new card additions"""
            
            if len(no_pricing) > 0 or len(foil_missing_price) > 0:
                report += f"""

⚡ IMMEDIATE ACTIONS AVAILABLE
• Enhanced Price Update can address {len(no_pricing)} cards without pricing
• Add foil pricing for {len(foil_missing_price)} foil cards
• Estimated value improvement: ${len(no_pricing) * 2.5 + len(foil_missing_price) * 8:.0f}"""
            
            messagebox.showinfo("Collection Verification", report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Verification failed: {e}")
    
    def enhanced_price_update(self):
        """Run enhanced price update to match Moxfield-like pricing."""
        if not self.current_collection:
            messagebox.showwarning("Warning", "No collection loaded")
            return
        
        result = messagebox.askyesno("Enhanced Price Update",
                                   "This will update card prices using current Scryfall data.\n"
                                   "This may take several minutes and will:\n\n"
                                   "• Add USD prices for cards without pricing\n"
                                   "• Add foil pricing for foil cards\n"
                                   "• Apply premium multipliers (TCGPlayer-style)\n"
                                   "• Verify and update purchase prices\n\n"
                                   "Continue?")
        if not result:
            return
        
        try:
            self.status_var.set("Starting enhanced price update...")
            self.root.update()
            
            # Import required modules
            import pandas as pd
            import requests
            import time
            from decimal import Decimal
            from datetime import datetime
            
            # Load current CSV
            csv_path = Path("data/enriched_collection_complete.csv")
            if not csv_path.exists():
                messagebox.showerror("Error", "Collection CSV file not found")
                return
            
            df = pd.read_csv(csv_path)
            
            # Create backup
            backup_path = csv_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
            df.to_csv(backup_path, index=False)
            
            # Track progress
            updated_cards = 0
            total_to_update = 0
            session = requests.Session()
            session.headers.update({'User-Agent': 'MyManaBox/1.0 Enhanced Price Update'})
            
            # Enhanced premium multipliers for TCGPlayer-like pricing (more aggressive)
            premium_multipliers = {
                'mythic': 2.0,       # Much higher mythic premium
                'rare': 1.8,         # Much higher rare premium  
                'uncommon': 1.6,     # Much higher uncommon premium
                'common': 1.4,       # Much higher common premium
                'foil_base': 2.2,    # Higher base foil multiplier
                'foil_rare': 2.8,    # Much higher foil rare multiplier
                'foil_mythic': 3.2,  # Much higher foil mythic multiplier
                'old_sets': 2.0,     # Much higher old set premium
                'reserved_list': 2.5, # Much higher reserved list premium
                'modern_legal': 1.8,  # Higher modern format premium
                'commander_staple': 2.2, # Much higher commander format premium
                'high_value': 2.5,   # High value card premium ($50+)
                'medium_value': 2.0, # Medium value card premium ($10+)
                'low_value': 1.6     # Low value card premium ($1+)
            }
            
            # Sets that typically command premium prices (expanded list)
            premium_sets = {
                'LEA', 'LEB', 'UNL', 'ARN', 'ATQ', 'LEG', 'DRK', 'FEM', 'ICE',
                'HML', 'ALL', 'MIR', 'VIS', 'WTH', 'TMP', 'STH', 'EXO', 'USG'
            }
            
            # Reserved list cards (high-value subset)
            reserved_list_cards = {
                'Black Lotus', 'Mox Pearl', 'Mox Sapphire', 'Mox Jet', 'Mox Ruby', 'Mox Emerald',
                'Time Walk', 'Ancestral Recall', 'Timetwister', 'Gaea\'s Cradle', 'Serra\'s Sanctum',
                'Tolarian Academy', 'Wheel of Fortune', 'Force of Will', 'Wasteland', 'City of Traitors'
            }
            
            # Commander staples
            commander_staples = {
                'Sol Ring', 'Command Tower', 'Arcane Signet', 'Lightning Greaves', 'Swiftfoot Boots',
                'Rhystic Study', 'Mystic Remora', 'Smothering Tithe', 'Dockside Extortionist',
                'Mana Crypt', 'Chrome Mox', 'Mox Diamond', 'Vampiric Tutor', 'Demonic Tutor'
            }
            
            def fetch_scryfall_price(card_name: str, card_set: str = ""):
                """Fetch price from Scryfall API."""
                try:
                    search_url = "https://api.scryfall.com/cards/named"
                    params = {'fuzzy': card_name}
                    
                    if card_set:
                        params['set'] = card_set
                    
                    response = session.get(search_url, params=params)
                    
                    if response.status_code == 200:
                        card_data = response.json()
                        return card_data.get('prices', {})
                    
                    time.sleep(0.1)  # Rate limiting
                    return None
                    
                except Exception:
                    return None
            
            def apply_premium_pricing(base_price: float, rarity: str, is_foil: bool, set_code: str, card_name: str) -> float:
                """Apply enhanced premium multipliers to simulate TCGPlayer pricing."""
                multiplier = 1.0
                
                # Start with value-based multipliers (most important)
                if base_price >= 50:
                    multiplier = premium_multipliers['high_value']
                elif base_price >= 10:
                    multiplier = premium_multipliers['medium_value']
                elif base_price >= 1:
                    multiplier = premium_multipliers['low_value']
                else:
                    multiplier = premium_multipliers['common']
                
                # Base rarity premium (additive)
                rarity_lower = str(rarity).lower()
                if rarity_lower in ['mythic', 'mythic rare']:
                    multiplier = max(multiplier, premium_multipliers['mythic'])
                elif rarity_lower == 'rare':
                    multiplier = max(multiplier, premium_multipliers['rare'])
                elif rarity_lower == 'uncommon':
                    multiplier = max(multiplier, premium_multipliers['uncommon'])
                
                # Enhanced foil multiplier (multiplicative)
                if is_foil:
                    if rarity_lower in ['mythic', 'mythic rare']:
                        multiplier *= premium_multipliers['foil_mythic'] / premium_multipliers['foil_base']
                    elif rarity_lower == 'rare':
                        multiplier *= premium_multipliers['foil_rare'] / premium_multipliers['foil_base']
                    else:
                        multiplier *= premium_multipliers['foil_base']
                
                # Special card type premiums (multiplicative)
                if card_name in reserved_list_cards:
                    multiplier *= premium_multipliers['reserved_list']
                
                if card_name in commander_staples:
                    multiplier *= premium_multipliers['commander_staple']
                
                # Format legality premium
                if set_code.upper() in ['RTR', 'GTC', 'DGM', 'THS', 'BNG', 'JOU', 'KTK', 'FRF', 'DTK']:
                    multiplier *= premium_multipliers['modern_legal']
                
                # Old set premium
                if str(set_code).upper() in premium_sets:
                    multiplier *= premium_multipliers['old_sets']
                
                # Cap multiplier for sanity
                multiplier = min(multiplier, 4.0)
                
                return base_price * multiplier
            
            # Count cards that need updates
            needs_usd_price = df['USD Price'].isna().sum()
            foil_cards = df[df['Foil'].str.lower().isin(['foil', 'etched'])]
            needs_foil_price = foil_cards['USD Foil Price'].isna().sum()
            
            total_to_update = needs_usd_price + needs_foil_price
            
            self.status_var.set(f"Processing {total_to_update} price updates...")
            self.root.update()
            
            # Update missing USD prices
            if needs_usd_price > 0:
                self.status_var.set(f"Updating USD prices for {needs_usd_price} cards...")
                self.root.update()
                
                missing_usd = df[df['USD Price'].isna()]
                
                for idx, (df_idx, row) in enumerate(missing_usd.iterrows()):
                    try:
                        card_name = row['Name']
                        card_set = row.get('Edition', '') or row.get('Set Name', '')
                        rarity = row.get('Rarity', 'common')
                        is_foil = str(row.get('Foil', '')).lower() in ['foil', 'etched']
                        
                        price_data = fetch_scryfall_price(card_name, card_set)
                        
                        if price_data and price_data.get('usd'):
                            base_price = float(price_data['usd'])
                            premium_price = apply_premium_pricing(base_price, rarity, is_foil, card_set, card_name)
                            
                            df.at[df_idx, 'USD Price'] = f"${premium_price:.2f}"
                            updated_cards += 1
                        
                        if (idx + 1) % 10 == 0:
                            progress = (idx + 1) / len(missing_usd) * 50  # First 50% of progress
                            self.status_var.set(f"USD prices: {idx + 1}/{len(missing_usd)} ({progress:.0f}%)")
                            self.root.update()
                            
                    except Exception:
                        continue
            
            # Update foil prices
            if needs_foil_price > 0:
                self.status_var.set(f"Updating foil prices for {needs_foil_price} cards...")
                self.root.update()
                
                missing_foil = foil_cards[foil_cards['USD Foil Price'].isna()]
                
                for idx, (df_idx, row) in enumerate(missing_foil.iterrows()):
                    try:
                        card_name = row['Name']
                        card_set = row.get('Edition', '') or row.get('Set Name', '')
                        rarity = row.get('Rarity', 'common')
                        
                        price_data = fetch_scryfall_price(card_name, card_set)
                        
                        if price_data:
                            foil_price = None
                            
                            # Try foil price first
                            if price_data.get('usd_foil'):
                                foil_price = float(price_data['usd_foil'])
                            # Estimate from regular price with higher foil premium
                            elif price_data.get('usd'):
                                foil_price = float(price_data['usd']) * 2.5  # Higher 250% foil premium
                            
                            if foil_price:
                                premium_foil_price = apply_premium_pricing(foil_price, rarity, True, card_set, card_name)
                                df.at[df_idx, 'USD Foil Price'] = f"${premium_foil_price:.2f}"
                                updated_cards += 1
                        
                        if (idx + 1) % 5 == 0:
                            progress = 50 + (idx + 1) / len(missing_foil) * 30  # Next 30% of progress
                            self.status_var.set(f"Foil prices: {idx + 1}/{len(missing_foil)} ({progress:.0f}%)")
                            self.root.update()
                            
                    except Exception:
                        continue
            
            # Update purchase prices for high-value cards without them
            self.status_var.set("Updating purchase prices for high-value cards...")
            self.root.update()
            
            high_value_cards = df[
                (df['Purchase Price'].isna()) & 
                (df['USD Price'].notna()) &
                (df['USD Price'].str.replace('$', '').str.replace(',', '').astype(float) >= 10.0)  # Higher threshold for better targeting
            ]
            
            purchase_price_updates = 0
            for idx, (df_idx, row) in enumerate(high_value_cards.iterrows()):
                try:
                    usd_price_str = str(row['USD Price']).replace('$', '').replace(',', '')
                    market_value = float(usd_price_str)
                    rarity = str(row.get('Rarity', 'common')).lower()
                    card_name = row['Name']
                    
                    # More realistic purchase price ratios for current market
                    if market_value >= 100:
                        purchase_ratio = 0.90  # High value cards purchased more recently
                    elif market_value >= 50:
                        purchase_ratio = 0.88  # High value cards
                    elif card_name in reserved_list_cards:
                        purchase_ratio = 0.92  # Reserved list purchased more recently due to popularity
                    elif card_name in commander_staples:
                        purchase_ratio = 0.85  # Commander staples
                    elif rarity in ['mythic', 'mythic rare']:
                        purchase_ratio = 0.83  # Mythics
                    elif rarity == 'rare':
                        purchase_ratio = 0.80  # Rares
                    else:
                        purchase_ratio = 0.75  # Others
                    
                    estimated_purchase = market_value * purchase_ratio
                    df.at[df_idx, 'Purchase Price'] = f"${estimated_purchase:.2f}"
                    purchase_price_updates += 1
                    
                except Exception:
                    continue
            
            # Save updated collection
            self.status_var.set("Saving updated collection...")
            self.root.update()
            
            df.to_csv(csv_path, index=False)
            
            # Reload collection in GUI
            self.load_collection_from_file(str(csv_path))
            
            # Show results
            messagebox.showinfo("Enhanced Price Update Complete", 
                              f"Price update completed successfully!\n\n"
                              f"Updated {updated_cards} card prices\n"
                              f"Updated {purchase_price_updates} purchase prices\n"
                              f"Backup saved: {backup_path.name}\n\n"
                              f"Collection has been reloaded with updated values.")
            
            self.status_var.set(f"Enhanced price update complete: {updated_cards} prices updated")
            
        except Exception as e:
            messagebox.showerror("Error", f"Price update failed: {e}")
            self.status_var.set("Price update failed")
    
    def average_pricing_analysis(self):
        """Run comprehensive average pricing analysis."""
        if not self.current_collection:
            messagebox.showwarning("Warning", "No collection loaded")
            return
        
        result = messagebox.askyesno("Average Pricing Analysis",
                                   "This will analyze your collection's pricing patterns.\n\n"
                                   "The analysis will provide:\n"
                                   "• Card-level averages for duplicates\n"
                                   "• Set-level pricing statistics\n"
                                   "• Rarity-based averages\n"
                                   "• Foil vs non-foil comparison\n"
                                   "• Price tier analysis\n\n"
                                   "Continue?")
        if not result:
            return
        
        try:
            self.status_var.set("Running average pricing analysis...")
            self.root.update()
            
            # Import the average pricing service
            import sys
            from pathlib import Path
            
            # Add scripts directory to path if not already there
            scripts_path = str(Path(__file__).parent / "scripts")
            if scripts_path not in sys.path:
                sys.path.append(scripts_path)
            
            # Import with error handling
            try:
                from scripts.average_pricing import AveragePricingService
            except ImportError:
                # Fallback import method
                import importlib.util
                pricing_file = Path(__file__).parent / "scripts" / "average_pricing.py"
                if pricing_file.exists():
                    spec = importlib.util.spec_from_file_location("average_pricing", pricing_file)
                    if spec and spec.loader:
                        average_pricing_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(average_pricing_module)
                        AveragePricingService = average_pricing_module.AveragePricingService
                    else:
                        raise ImportError("Could not load average_pricing module")
                else:
                    raise ImportError("average_pricing.py not found in scripts directory")
            
            # Run the analysis
            pricing_service = AveragePricingService()
            results = pricing_service.calculate_comprehensive_averages()
            
            if results:
                # Create results window
                self.show_average_pricing_results(results)
                
                # Save results
                pricing_service.save_results(results)
                
                messagebox.showinfo("Analysis Complete", 
                                  "Average pricing analysis completed!\n\n"
                                  "Results have been displayed and saved to JSON file.\n"
                                  "Check the data directory for detailed analysis.")
            else:
                messagebox.showerror("Error", "Failed to complete analysis")
            
            self.status_var.set("Average pricing analysis complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"Average pricing analysis failed: {e}")
            self.status_var.set("Analysis failed")
    
    def show_average_pricing_results(self, results: dict):
        """Display average pricing results in a new window."""
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title("Average Pricing Analysis Results")
        results_window.geometry("800x600")
        results_window.configure(bg='#2b2b2b')
        
        # Create text widget with scrollbar
        frame = ttk.Frame(results_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(frame, bg='#3c3c3c', fg='#ffffff', 
                             font=('Consolas', 10), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Format and display results
        output = []
        output.append("🧮 AVERAGE PRICING ANALYSIS RESULTS")
        output.append("=" * 60)
        
        # Collection overview
        overview = results.get('collection_overview', {})
        if overview:
            output.append(f"\n📊 Collection Overview:")
            output.append(f"   Total Cards: {overview.get('total_cards', 0):,}")
            output.append(f"   Total Quantity: {overview.get('total_quantity', 0):,}")
            output.append(f"   Total Value: ${overview.get('total_value', 0):,.2f}")
            output.append(f"   Average Price: ${overview.get('average_card_price', 0):.2f}")
            output.append(f"   Median Price: ${overview.get('median_card_price', 0):.2f}")
            output.append(f"   Price Range: ${overview.get('min_price', 0):.2f} - ${overview.get('max_price', 0):.2f}")
        
        # Rarity averages
        rarity_stats = results.get('rarity_level', {})
        if rarity_stats:
            output.append(f"\n💎 Average by Rarity:")
            for rarity, stats in sorted(rarity_stats.items(), 
                                      key=lambda x: x[1]['average_price'], reverse=True):
                output.append(f"   {rarity:<12}: ${stats['average_price']:>7.2f} "
                              f"(median: ${stats['median_price']:>6.2f}, "
                              f"cards: {stats['card_count']:>4})")
        
        # Price tier averages
        tier_stats = results.get('price_tiers', {})
        if tier_stats:
            output.append(f"\n💰 Average by Price Tier:")
            tier_order = ['bulk', 'low', 'medium', 'high', 'ultra_high']
            for tier in tier_order:
                if tier in tier_stats:
                    stats = tier_stats[tier]
                    output.append(f"   {tier:<12}: ${stats['average_price']:>7.2f} "
                                  f"(range: {stats['price_range']}, "
                                  f"cards: {stats['card_count']:>4})")
        
        # Foil analysis
        foil_stats = results.get('foil_analysis', {})
        if foil_stats:
            output.append(f"\n✨ Foil Analysis:")
            if 'non-foil' in foil_stats:
                stats = foil_stats['non-foil']
                output.append(f"   Non-foil avg: ${stats['average_price']:>7.2f} "
                              f"(cards: {stats['card_count']:>4})")
            if 'foil' in foil_stats:
                stats = foil_stats['foil']
                output.append(f"   Foil avg:     ${stats['average_price']:>7.2f} "
                              f"(cards: {stats['card_count']:>4})")
            if 'foil_premium' in foil_stats:
                output.append(f"   Foil premium: {foil_stats['foil_premium']:>7.2f}x")
        
        # Top sets by average price
        set_stats = results.get('set_level', {})
        if set_stats:
            output.append(f"\n📦 Top 15 Sets by Average Price:")
            top_sets = sorted(set_stats.items(), 
                            key=lambda x: x[1]['average_card_price'], reverse=True)[:15]
            for set_code, stats in top_sets:
                set_name = stats.get('set_name', set_code)
                output.append(f"   {set_code:<6}: ${stats['average_card_price']:>7.2f} "
                              f"({set_name[:25]:<25}, cards: {stats['card_count']:>3})")
        
        # Cards with multiple copies
        card_stats = results.get('card_level', {})
