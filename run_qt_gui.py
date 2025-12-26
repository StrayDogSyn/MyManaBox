#!/usr/bin/env python3
"""
CardForge PyQt6 GUI Launcher
Quick launcher for the CardForge PyQt6 graphical interface
"""

import sys
from pathlib import Path

# Ensure cardforge module can be imported
sys.path.insert(0, str(Path(__file__).parent))

from cardforge.qt_gui.app import main

if __name__ == "__main__":
    main()
