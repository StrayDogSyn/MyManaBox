#!/usr/bin/env python3
"""
CardForge PyQt6 GUI Launcher
Quick launcher for the CardForge PyQt6 graphical interface
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cardforge.qt_gui.app import main

if __name__ == "__main__":
    main()
