"""
CardForge GUI Module
Tkinter-based graphical interface for CardForge
"""

from .app import CardForgeGUI, main
from .async_bridge import AsyncBridge
from .theme import Theme, Icons, RarityColors

# Widgets
from .widgets import (
    StyledFrame,
    StyledButton,
    IconButton,
    SearchBar,
    StatCard,
    LoadingOverlay,
    ToastNotification,
    PanelContainer,
    TabContainer,
    FilterDropdown,
    ColorFilter,
    PriceRangeSlider,
    MiniTable,
    ProgressBar,
    BadgeLabel,
    SimpleBarChart,
    SimplePieChart,
    LoadingSpinner,
    VirtualScrollTree,
)

# Panels
from .panels import (
    StatsPanel,
    CollectionBrowserPanel,
    CardDetailPanel,
)

__all__ = [
    # Main application
    'CardForgeGUI',
    'main',
    'AsyncBridge',

    # Theme
    'Theme',
    'Icons',
    'RarityColors',

    # Base widgets
    'StyledFrame',
    'StyledButton',
    'IconButton',
    'SearchBar',
    'StatCard',
    'LoadingOverlay',
    'ToastNotification',

    # Layout components
    'PanelContainer',
    'TabContainer',

    # Filter components
    'FilterDropdown',
    'ColorFilter',
    'PriceRangeSlider',

    # Data display
    'MiniTable',
    'ProgressBar',
    'BadgeLabel',
    'VirtualScrollTree',

    # Charts
    'SimpleBarChart',
    'SimplePieChart',
    'LoadingSpinner',

    # Panels
    'StatsPanel',
    'CollectionBrowserPanel',
    'CardDetailPanel',
]
