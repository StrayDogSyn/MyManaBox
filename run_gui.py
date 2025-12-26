#!/usr/bin/env python3
"""
CardForge GUI Launcher
Quick launcher for the CardForge graphical interface
"""

import sys
from pathlib import Path

# Ensure cardforge module can be imported
sys.path.insert(0, str(Path(__file__).parent))

from cardforge.gui.app import main

if __name__ == "__main__":
    main()
