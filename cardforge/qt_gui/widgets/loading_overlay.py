"""
Loading overlay dialog.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from ..theme import THEME


class LoadingOverlay(QDialog):
    """
    Modal loading overlay with message.

    Shows a loading message in the center of the parent window.
    """

    def __init__(self, parent, message: str = "Loading..."):
        super().__init__(parent)

        # Make it modal
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog
        )

        # Semi-transparent background
        self.setStyleSheet(f"""
            QDialog {{
                background-color: rgba(26, 22, 37, 230);
            }}
            QLabel {{
                color: {THEME.TEXT_PRIMARY};
                font-size: {THEME.FONT_SIZE_LARGE}pt;
            }}
        """)

        # Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Message
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(THEME.get_font("large"))
        layout.addWidget(label)

        # Size to parent
        if parent:
            self.setGeometry(parent.geometry())

    def show(self):
        """Show the overlay."""
        super().show()
        # Center on parent
        if self.parent():
            parent_geometry = self.parent().geometry()
            self.setGeometry(parent_geometry)
