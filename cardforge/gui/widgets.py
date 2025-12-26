"""
CardForge GUI Widgets
Reusable UI components for the MTG Command Center
"""

import math
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, List, Set, Any
from decimal import Decimal

from .theme import Theme, Icons, RarityColors


# =============================================================================
# BASE COMPONENTS
# =============================================================================

class StyledFrame(tk.Frame):
    """Base frame with consistent styling"""

    def __init__(self, parent, **kwargs):
        bg = kwargs.pop('bg', Theme.BG_PRIMARY)
        super().__init__(parent, bg=bg, **kwargs)


class StyledButton(tk.Button):
    """Styled button with hover effects"""

    def __init__(self, parent, text, command=None, variant="primary", **kwargs):
        self.variant = variant
        self._bg = None
        self._hover_bg = None

        # Determine colors based on variant
        if variant == "primary":
            bg = Theme.ACCENT_PRIMARY
            hover_bg = Theme.ACCENT_HOVER
            active_bg = Theme.ACCENT_PRESSED
        elif variant == "secondary":
            bg = Theme.ACCENT_SUBTLE
            hover_bg = Theme.ACCENT_PRIMARY
            active_bg = Theme.ACCENT_PRESSED
        elif variant == "danger":
            bg = Theme.ERROR
            hover_bg = "#e53935"
            active_bg = "#c62828"
        elif variant == "success":
            bg = Theme.SUCCESS
            hover_bg = "#66bb6a"
            active_bg = "#388e3c"
        else:  # Default/ghost
            bg = Theme.BG_TERTIARY
            hover_bg = Theme.BG_SECONDARY
            active_bg = Theme.BG_PRIMARY

        self._bg = bg
        self._hover_bg = hover_bg

        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
            activebackground=active_bg,
            activeforeground=Theme.TEXT_PRIMARY,
            bd=0,
            padx=15,
            pady=6,
            cursor="hand2",
            **kwargs
        )

        # Hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        self.config(bg=self._hover_bg)

    def _on_leave(self, e):
        self.config(bg=self._bg)


class IconButton(tk.Button):
    """Small icon-only button"""

    def __init__(self, parent, icon: str, command=None, tooltip: str = "", **kwargs):
        super().__init__(
            parent,
            text=icon,
            command=command,
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, 12),
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            **kwargs
        )
        
        self.bind("<Enter>", lambda e: self.config(bg=Theme.BG_SECONDARY))
        self.bind("<Leave>", lambda e: self.config(bg=Theme.BG_TERTIARY))
        
        # Tooltip
        if tooltip:
            self._tooltip = tooltip
            self.bind("<Enter>", self._show_tooltip, add="+")
            self.bind("<Leave>", self._hide_tooltip, add="+")
            self._tooltip_window = None

    def _show_tooltip(self, e):
        if hasattr(self, '_tooltip'):
            x, y = e.x_root + 10, e.y_root + 10
            self._tooltip_window = tk.Toplevel(self)
            self._tooltip_window.wm_overrideredirect(True)
            self._tooltip_window.wm_geometry(f"+{x}+{y}")
            label = tk.Label(
                self._tooltip_window,
                text=self._tooltip,
                bg=Theme.BG_SECONDARY,
                fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                padx=8,
                pady=4
            )
            label.pack()

    def _hide_tooltip(self, e):
        if hasattr(self, '_tooltip_window') and self._tooltip_window:
            self._tooltip_window.destroy()
            self._tooltip_window = None


# =============================================================================
# INPUT COMPONENTS
# =============================================================================

class SearchBar(StyledFrame):
    """Advanced search bar with autocomplete"""

    def __init__(self, parent, on_search: Callable, placeholder: str = "Search cards...", **kwargs):
        super().__init__(parent, **kwargs)
        self.on_search = on_search
        self.placeholder = placeholder

        # Search icon label
        tk.Label(
            self,
            text=Icons.SEARCH,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, 12)
        ).pack(side=tk.LEFT, padx=(0, 8))

        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_text_change)

        self.entry = tk.Entry(
            self,
            textvariable=self.search_var,
            width=40,
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            insertbackground=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
            bd=1,
            relief='solid'
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Clear button
        self.clear_btn = tk.Button(
            self,
            text="×",
            command=self.clear,
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, 14),
            bd=0,
            cursor="hand2"
        )
        self.clear_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Debounce timer
        self._search_timer = None

    def _on_text_change(self, *args):
        """Debounced search - wait 300ms after typing stops"""
        if self._search_timer:
            self.after_cancel(self._search_timer)

        self._search_timer = self.after(300, self._execute_search)

    def _execute_search(self):
        """Execute the search callback"""
        query = self.search_var.get()
        self.on_search(query)

    def clear(self):
        """Clear search field"""
        self.search_var.set("")
        self.entry.focus()

    def get(self):
        """Get current search text"""
        return self.search_var.get()


class StatCard(StyledFrame):
    """Metric display card"""

    def __init__(self, parent, title: str, value: str, subtitle: str = "",
                 icon: str = "", **kwargs):
        super().__init__(parent, bg=Theme.BG_SECONDARY, **kwargs)

        self.configure(relief='flat', bd=1)

        # Container for padding
        container = StyledFrame(self, bg=Theme.BG_SECONDARY)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        # Icon (if provided)
        if icon:
            tk.Label(
                container,
                text=icon,
                bg=Theme.BG_SECONDARY,
                fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, 20)
            ).pack(side=tk.LEFT, padx=(0, 10))

        # Text container
        text_container = StyledFrame(container, bg=Theme.BG_SECONDARY)
        text_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Title
        tk.Label(
            text_container,
            text=title,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
            anchor='w'
        ).pack(fill=tk.X)

        # Value
        self.value_label = tk.Label(
            text_container,
            text=value,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_LARGE, 'bold'),
            anchor='w'
        )
        self.value_label.pack(fill=tk.X)

        # Subtitle (if provided)
        if subtitle:
            tk.Label(
                text_container,
                text=subtitle,
                bg=Theme.BG_SECONDARY,
                fg=Theme.TEXT_MUTED,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
                anchor='w'
            ).pack(fill=tk.X)

    def update_value(self, value: str, subtitle: str = None):
        """Update the displayed value"""
        self.value_label.config(text=value)
        if subtitle:
            # Find subtitle label and update it
            for child in self.value_label.master.winfo_children():
                if isinstance(child, tk.Label) and child != self.value_label:
                    child.config(text=subtitle)


class LoadingOverlay(tk.Toplevel):
    """Modal loading overlay with spinner"""

    def __init__(self, parent, message="Loading..."):
        super().__init__(parent)

        # Make it modal
        self.transient(parent)
        self.grab_set()

        # Remove window decorations
        self.overrideredirect(True)

        # Semi-transparent background
        self.configure(bg=Theme.BG_PRIMARY)
        self.attributes('-alpha', 0.9)

        # Center on parent
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 150
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 50
        self.geometry(f"300x100+{x}+{y}")

        # Message
        tk.Label(
            self,
            text=message,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)
        ).pack(expand=True)

    def close(self):
        """Close the overlay"""
        self.grab_release()
        self.destroy()


class ToastNotification:
    """Non-intrusive notification"""

    @staticmethod
    def show(parent, message: str, duration: int = 3000, type: str = 'info'):
        """Show a toast notification"""
        toast = tk.Toplevel(parent)
        toast.overrideredirect(True)
        toast.attributes('-topmost', True)

        # Position in bottom-right
        screen_width = toast.winfo_screenwidth()
        screen_height = toast.winfo_screenheight()
        x = screen_width - 350
        y = screen_height - 120
        toast.geometry(f"320x80+{x}+{y}")

        # Color based on type
        color_map = {
            'success': Theme.SUCCESS,
            'error': Theme.ERROR,
            'warning': Theme.WARNING,
            'info': Theme.INFO
        }
        bg_color = color_map.get(type, Theme.INFO)

        # Container
        container = StyledFrame(toast, bg=bg_color)
        container.pack(fill=tk.BOTH, expand=True)

        # Message
        tk.Label(
            container,
            text=message,
            bg=bg_color,
            fg=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL),
            wraplength=280
        ).pack(padx=15, pady=15)

        # Auto-close
        toast.after(duration, toast.destroy)

        # Fade in
        toast.attributes('-alpha', 0.0)
        _fade_in(toast)


def _fade_in(window, alpha=0.0):
    """Fade in animation"""
    if alpha < 1.0:
        alpha += 0.1
        try:
            window.attributes('-alpha', alpha)
            window.after(30, lambda: _fade_in(window, alpha))
        except tk.TclError:
            pass  # Window was destroyed


# =============================================================================
# LAYOUT COMPONENTS
# =============================================================================

class PanelContainer(StyledFrame):
    """Container with title and optional minimize action"""

    def __init__(self, parent, title: str, show_minimize: bool = True, **kwargs):
        super().__init__(parent, bg=Theme.BG_SECONDARY, **kwargs)

        # Header with title and actions
        header = StyledFrame(self, bg=Theme.BG_SECONDARY)
        header.pack(fill=tk.X, padx=15, pady=(15, 10))

        # Title
        tk.Label(
            header,
            text=title,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, 12, 'bold')
        ).pack(side=tk.LEFT)

        if show_minimize:
            self.minimize_btn = tk.Button(
                header,
                text="−",
                command=self.toggle_content,
                bg=Theme.BG_TERTIARY,
                fg=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, 14),
                bd=0,
                width=2,
                cursor="hand2"
            )
            self.minimize_btn.pack(side=tk.RIGHT)

        # Content frame
        self.content = StyledFrame(self, bg=Theme.BG_SECONDARY)
        self.content.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        self.is_minimized = False

    def toggle_content(self):
        """Toggle content visibility"""
        if self.is_minimized:
            self.content.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
            self.minimize_btn.config(text="−")
        else:
            self.content.pack_forget()
            self.minimize_btn.config(text="+")
        self.is_minimized = not self.is_minimized


class TabContainer(ttk.Notebook):
    """Styled tab container"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Style the notebook
        style = ttk.Style()
        style.configure(
            'TNotebook',
            background=Theme.BG_PRIMARY,
            borderwidth=0
        )
        style.configure(
            'TNotebook.Tab',
            background=Theme.BG_SECONDARY,
            foreground=Theme.TEXT_PRIMARY,
            padding=[20, 10]
        )
        style.map('TNotebook.Tab',
                  background=[('selected', Theme.ACCENT_PRIMARY)],
                  foreground=[('selected', Theme.TEXT_PRIMARY)])

    def add_tab(self, widget, title: str, icon: str = ""):
        """Add a tab with optional icon"""
        tab_text = f"{icon} {title}" if icon else title
        self.add(widget, text=tab_text)


# =============================================================================
# FILTER COMPONENTS
# =============================================================================

class FilterDropdown(StyledFrame):
    """Styled dropdown for filtering"""

    def __init__(self, parent, label: str, options: List[str], on_change: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)

        # Label
        tk.Label(
            self,
            text=label,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_SECONDARY,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL)
        ).pack(anchor='w')

        # Dropdown
        self.var = tk.StringVar()
        self.combo = ttk.Combobox(
            self,
            textvariable=self.var,
            values=options,
            state='readonly'
        )
        self.combo.pack(fill=tk.X, pady=(2, 0))

        if on_change:
            self.combo.bind('<<ComboboxSelected>>', lambda e: on_change(self.var.get()))

    def get(self) -> str:
        return self.var.get()

    def set(self, value: str):
        self.var.set(value)


class ColorFilter(StyledFrame):
    """MTG color filter with mana symbol buttons"""

    COLORS = [
        ('W', Theme.TEXT_PRIMARY, '#f0f2c0'),
        ('U', Theme.TEXT_PRIMARY, '#0e68ab'),
        ('B', Theme.TEXT_PRIMARY, '#150b00'),
        ('R', Theme.TEXT_PRIMARY, '#d3202a'),
        ('G', Theme.TEXT_PRIMARY, '#00733e')
    ]

    def __init__(self, parent, on_change: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.selected_colors: Set[str] = set()
        self.on_change = on_change
        self.buttons: Dict[str, tk.Button] = {}

        for color, fg, bg in self.COLORS:
            btn = tk.Button(
                self,
                text=color,
                width=3,
                bg=Theme.BG_TERTIARY,
                fg=fg,
                font=(Theme.FONT_FAMILY, 12, 'bold'),
                bd=1,
                relief='solid',
                cursor="hand2",
                command=lambda c=color: self._toggle_color(c)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.buttons[color] = btn

    def _toggle_color(self, color: str):
        """Toggle color selection"""
        if color in self.selected_colors:
            self.selected_colors.remove(color)
            self.buttons[color].config(relief='solid', bg=Theme.BG_TERTIARY)
        else:
            self.selected_colors.add(color)
            # Find color bg
            color_bg = next((bg for c, _, bg in self.COLORS if c == color), Theme.ACCENT_PRIMARY)
            self.buttons[color].config(relief='sunken', bg=color_bg)

        if self.on_change:
            self.on_change(list(self.selected_colors))

    def get_selected(self) -> List[str]:
        return list(self.selected_colors)

    def clear(self):
        """Clear all selections"""
        for color in list(self.selected_colors):
            self._toggle_color(color)


class PriceRangeSlider(StyledFrame):
    """Dual slider for price range filtering"""

    def __init__(self, parent, min_val: float = 0, max_val: float = 500, 
                 on_change: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.min_val = min_val
        self.max_val = max_val
        self.on_change = on_change

        # Labels
        label_frame = StyledFrame(self)
        label_frame.pack(fill=tk.X)

        self.min_label = tk.Label(
            label_frame,
            text=f"${min_val:.0f}",
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY
        )
        self.min_label.pack(side=tk.LEFT)

        self.max_label = tk.Label(
            label_frame,
            text=f"${max_val:.0f}",
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY
        )
        self.max_label.pack(side=tk.RIGHT)

        # Min slider
        self.min_slider = tk.Scale(
            self,
            from_=min_val,
            to=max_val,
            orient=tk.HORIZONTAL,
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            command=self._on_min_change,
            showvalue=0,
            highlightthickness=0
        )
        self.min_slider.pack(fill=tk.X)

        # Max slider
        self.max_slider = tk.Scale(
            self,
            from_=min_val,
            to=max_val,
            orient=tk.HORIZONTAL,
            bg=Theme.BG_TERTIARY,
            fg=Theme.TEXT_PRIMARY,
            command=self._on_max_change,
            showvalue=0,
            highlightthickness=0
        )
        self.max_slider.set(max_val)
        self.max_slider.pack(fill=tk.X)

    def _on_min_change(self, value):
        self.min_label.config(text=f"${float(value):.0f}")
        if self.on_change:
            self.on_change(float(value), self.max_slider.get())

    def _on_max_change(self, value):
        self.max_label.config(text=f"${float(value):.0f}")
        if self.on_change:
            self.on_change(self.min_slider.get(), float(value))

    def get_range(self) -> tuple:
        return (self.min_slider.get(), self.max_slider.get())


# =============================================================================
# DATA DISPLAY COMPONENTS
# =============================================================================

class MiniTable(StyledFrame):
    """Small table for displaying top N items"""

    def __init__(self, parent, title: str, columns: List[str], **kwargs):
        super().__init__(parent, bg=Theme.BG_SECONDARY, **kwargs)

        # Title
        tk.Label(
            self,
            text=title,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, 10, 'bold')
        ).pack(anchor='w', padx=10, pady=(10, 5))

        # Create tree
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show='headings',
            height=5
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def set_data(self, rows: List[tuple]):
        """Set table data"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add rows
        for row in rows:
            self.tree.insert('', 'end', values=row)


class ProgressBar(StyledFrame):
    """Styled progress bar with label"""

    def __init__(self, parent, label: str = "Progress", **kwargs):
        super().__init__(parent, **kwargs)

        # Label
        self.label = tk.Label(
            self,
            text=label,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_SECONDARY
        )
        self.label.pack(anchor='w')

        # Progress
        self.progress = ttk.Progressbar(
            self,
            mode='determinate',
            length=300
        )
        self.progress.pack(fill=tk.X, pady=(5, 0))

        # Percentage
        self.pct_label = tk.Label(
            self,
            text="0%",
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY
        )
        self.pct_label.pack(anchor='e')

    def set_progress(self, value: int, maximum: int = 100):
        """Update progress"""
        percentage = (value / maximum) * 100 if maximum > 0 else 0
        self.progress['value'] = percentage
        self.pct_label.config(text=f"{percentage:.0f}%")
        self.update()


class BadgeLabel(tk.Label):
    """Colored badge for statuses (rarity, condition, etc.)"""

    RARITY_COLORS = {
        'common': RarityColors.COMMON,
        'uncommon': RarityColors.UNCOMMON,
        'rare': RarityColors.RARE,
        'mythic': RarityColors.MYTHIC,
        'special': RarityColors.SPECIAL,
    }

    def __init__(self, parent, text: str, badge_type: str = 'rarity', **kwargs):
        bg_color = self.RARITY_COLORS.get(text.lower(), Theme.BG_TERTIARY)

        # Ensure text is readable
        fg_color = Theme.TEXT_PRIMARY
        if text.lower() in ['rare', 'mythic']:
            fg_color = '#000000'

        super().__init__(
            parent,
            text=text,
            bg=bg_color,
            fg=fg_color,
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL, 'bold'),
            padx=8,
            pady=2,
            relief='flat',
            **kwargs
        )


# =============================================================================
# CHART COMPONENTS (No matplotlib dependency)
# =============================================================================

class SimpleBarChart(tk.Canvas):
    """Simple bar chart without matplotlib dependency"""

    def __init__(self, parent, width: int = 300, height: int = 200, **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=Theme.BG_SECONDARY,
            highlightthickness=0,
            **kwargs
        )
        self.chart_width = width
        self.chart_height = height

    def plot(self, labels: List[str], values: List[float], colors: List[str] = None):
        """Plot bar chart"""
        self.delete('all')

        if not values:
            return

        # Calculate dimensions
        bar_width = self.chart_width / (len(values) * 2)
        max_value = max(values) if max(values) > 0 else 1
        y_scale = (self.chart_height - 40) / max_value

        x = bar_width / 2
        for i, (label, value) in enumerate(zip(labels, values)):
            # Bar
            bar_height = value * y_scale
            color = colors[i] if colors and i < len(colors) else Theme.ACCENT_PRIMARY

            self.create_rectangle(
                x, self.chart_height - bar_height - 20,
                x + bar_width, self.chart_height - 20,
                fill=color,
                outline=''
            )

            # Label
            self.create_text(
                x + bar_width / 2,
                self.chart_height - 5,
                text=label[:8],  # Truncate long labels
                fill=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, 8)
            )

            # Value
            self.create_text(
                x + bar_width / 2,
                self.chart_height - bar_height - 25,
                text=str(int(value)),
                fill=Theme.TEXT_PRIMARY,
                font=(Theme.FONT_FAMILY, 8, 'bold')
            )

            x += bar_width * 2


class SimplePieChart(tk.Canvas):
    """Simple pie chart without matplotlib dependency"""

    def __init__(self, parent, size: int = 200, **kwargs):
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=Theme.BG_SECONDARY,
            highlightthickness=0,
            **kwargs
        )
        self.size = size
        self.center = size / 2
        self.radius = size / 2 - 30

    def plot(self, labels: List[str], values: List[float], colors: List[str]):
        """Plot pie chart"""
        self.delete('all')

        if not values or sum(values) == 0:
            return

        total = sum(values)
        start_angle = 90  # Start from top

        for i, (label, value) in enumerate(zip(labels, values)):
            # Calculate slice
            extent = (value / total) * 360

            # Draw slice
            self.create_arc(
                self.center - self.radius,
                self.center - self.radius,
                self.center + self.radius,
                self.center + self.radius,
                start=start_angle,
                extent=-extent,  # Negative for clockwise
                fill=colors[i] if i < len(colors) else Theme.ACCENT_PRIMARY,
                outline=Theme.BG_SECONDARY,
                width=2
            )

            # Label position (middle of arc)
            angle_rad = math.radians(start_angle - extent / 2)
            label_r = self.radius + 20
            label_x = self.center + label_r * math.cos(angle_rad)
            label_y = self.center - label_r * math.sin(angle_rad)

            # Only show label if slice is big enough
            if extent > 20:
                self.create_text(
                    label_x, label_y,
                    text=f"{label}\n{int(value)}",
                    fill=Theme.TEXT_PRIMARY,
                    font=(Theme.FONT_FAMILY, 8),
                    justify='center'
                )

            start_angle -= extent


class LoadingSpinner(tk.Canvas):
    """Animated loading spinner"""

    def __init__(self, parent, size: int = 50, **kwargs):
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=Theme.BG_PRIMARY,
            highlightthickness=0,
            **kwargs
        )
        self.size = size
        self.angle = 0
        self.is_spinning = False

    def start(self):
        """Start spinning"""
        self.is_spinning = True
        self._spin()

    def stop(self):
        """Stop spinning"""
        self.is_spinning = False
        self.delete('all')

    def _spin(self):
        if not self.is_spinning:
            return

        self.delete('all')

        # Draw arc
        self.create_arc(
            5, 5, self.size - 5, self.size - 5,
            start=self.angle,
            extent=270,
            width=3,
            outline=Theme.ACCENT_PRIMARY,
            style='arc'
        )

        self.angle = (self.angle + 10) % 360
        self.after(50, self._spin)


# =============================================================================
# VIRTUAL SCROLL TABLE
# =============================================================================

class VirtualScrollTree(ttk.Treeview):
    """High-performance treeview with sorting"""

    def __init__(self, parent, columns: Dict[str, Dict], **kwargs):
        column_ids = list(columns.keys())

        super().__init__(
            parent,
            columns=column_ids,
            show='headings',
            **kwargs
        )

        # Configure styles
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

        # Configure columns
        self.column('#0', width=0, stretch=tk.NO)  # Hide tree column

        for col_id, config in columns.items():
            width = config.get('width', 100)
            anchor = config.get('anchor', 'w')

            self.column(col_id, width=width, anchor=anchor)
            self.heading(
                col_id,
                text=col_id.replace('_', ' ').title(),
                command=lambda c=col_id: self.sort_by_column(c)
            )

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.yview)
        self.configure(yscrollcommand=self.scrollbar.set)

        # Sort state
        self._sort_column = None
        self._sort_reverse = False

    def sort_by_column(self, col: str):
        """Sort table by column"""
        if self._sort_column == col:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_reverse = False

        self._sort_column = col

        # Get all items with values
        items = [(self.set(item, col), item) for item in self.get_children('')]

        # Try numeric sort
        try:
            items.sort(key=lambda x: float(x[0].replace('$', '').replace(',', '')), 
                      reverse=self._sort_reverse)
        except (ValueError, AttributeError):
            items.sort(reverse=self._sort_reverse)

        # Rearrange
        for index, (_, item) in enumerate(items):
            self.move(item, '', index)

        # Update headings
        for column in self['columns']:
            heading = column.replace('_', ' ').title()
            if column == col:
                heading += f" {Icons.SORT_DESC if self._sort_reverse else Icons.SORT_ASC}"
            self.heading(column, text=heading)
