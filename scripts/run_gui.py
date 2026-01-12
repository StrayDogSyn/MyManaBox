#!/usr/bin/env python3
"""
DEPRECATED: Use scripts/run_qt_gui.py for the new PyQt6 interface.
This file is kept only for backward compatibility.
"""
import warnings
import sys
from pathlib import Path

# Ensure a clear message if executed
def main():
    warnings.warn(
        "\n" + "="*60 + "\n"
        "WARNING: run_gui.py is DEPRECATED\n"
        "Please use 'python scripts/run_qt_gui.py' instead.\n"
        "This launcher will be removed in CardForge v2.0\n"
        + "="*60,
        DeprecationWarning,
        stacklevel=2
    )

    print("\n" + "="*60)
    print("DEPRECATED: This launcher is no longer supported")
    print("Please use: python scripts/run_qt_gui.py")
    print("="*60 + "\n")
    sys.exit(1)

if __name__ == "__main__":
    main()
