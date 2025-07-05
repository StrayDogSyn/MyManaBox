#!/usr/bin/env python3
"""Simple GUI launcher for MyManaBox."""

import sys
import os
from pathlib import Path

# Ensure we're in the right directory
project_root = Path(__file__).parent
os.chdir(project_root)

# Add src to path
sys.path.insert(0, str(project_root / "src"))

try:
    # Import and run the GUI
    from gui import MyManaBoxGUI
    
    print("Starting MyManaBox GUI...")
    app = MyManaBoxGUI()
    app.run()
    
except Exception as e:
    print(f"Error starting GUI: {e}")
    import traceback
    traceback.print_exc()
