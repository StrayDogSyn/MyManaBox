"""
CardForge PyQt6 Application
Application entry point and configuration
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from .theme import THEME
from .main_window import MainWindow


# Enable high DPI scaling BEFORE any QApplication is created
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)


class CardForgeApp(QApplication):
    """
    CardForge Qt Application.

    Handles application-level configuration and theming.
    """

    def __init__(self, argv):
        super().__init__(argv)

        # Application metadata
        self.setApplicationName("CardForge")
        self.setApplicationVersion("2.0.0")
        self.setOrganizationName("StrayDog Syndications")
        self.setOrganizationDomain("github.com/StrayDogSyn/MyManaBox")

        # Apply theme
        self._apply_theme()

    def _apply_theme(self):
        """Apply CardForge theme to the application."""
        # Set palette (fallback for unstyled widgets)
        self.setPalette(THEME.create_palette())

        # Set stylesheet (primary styling method)
        self.setStyleSheet(THEME.get_stylesheet())

        # Set default font
        self.setFont(THEME.get_font("normal"))


def main():
    """
    Main entry point for the PyQt6 GUI.

    Usage:
        python -m cardforge.qt_gui.app
        # or
        python run_qt_gui.py
    """
    # Create application
    app = CardForgeApp(sys.argv)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
