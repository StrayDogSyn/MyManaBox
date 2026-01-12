"""CardForge GUI - Desktop Interface.

This module provides the PyQt6 desktop interface following clean architecture:

Responsibilities:
- Qt event handling
- UI rendering
- User interaction
- Background threads for I/O operations

Rules:
- Calls services (not repositories directly)
- No business logic (that's in services)
- No database access (that's in data)
- Uses async bridge for non-blocking operations

Usage:
    # Run the GUI application
    python -m gui
    
    # Or from code
    from gui import CardForgeApp, MainWindow, main
    main()
"""

# Re-export from cardforge.qt_gui for clean architecture
from cardforge.qt_gui import (
    CardForgeApp,
    MainWindow,
)

from cardforge.qt_gui.app import main

__all__ = [
    # Main application
    "CardForgeApp",
    "MainWindow",
    "main",
]
