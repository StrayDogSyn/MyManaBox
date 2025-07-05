#!/usr/bin/env python3
"""
Development utility script for MyManaBox project.
Provides common development tasks and maintenance operations.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from typing import Optional

PROJECT_ROOT = Path(__file__).parent


def run_command(command: str, description: Optional[str] = None) -> bool:
    """Run a shell command and return success status."""
    if description:
        print(f"Running: {description}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=PROJECT_ROOT)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with return code {e.returncode}")
        return False


def clean_project():
    """Clean up temporary files and cache directories."""
    print("Cleaning project...")
    
    # Remove Python cache directories
    cache_dirs = list(PROJECT_ROOT.rglob("__pycache__"))
    for cache_dir in cache_dirs:
        print(f"Removing {cache_dir}")
        subprocess.run(f'rmdir /s /q "{cache_dir}"', shell=True)
    
    # Remove .pyc files
    pyc_files = list(PROJECT_ROOT.rglob("*.pyc"))
    for pyc_file in pyc_files:
        print(f"Removing {pyc_file}")
        pyc_file.unlink()
    
    print("Project cleaned!")


def run_tests():
    """Run all tests."""
    print("Running tests...")
    
    # Run Python tests
    test_files = [
        "tests/test_refactored.py",
        "tests/test_mymanabox.py"
    ]
    
    for test_file in test_files:
        if (PROJECT_ROOT / test_file).exists():
            if not run_command(f"python {test_file}", f"Running {test_file}"):
                return False
    
    print("All tests passed!")
    return True


def format_code():
    """Format code using black (if available)."""
    print("Formatting code...")
    
    try:
        # Check if black is available
        subprocess.run("black --version", shell=True, check=True, capture_output=True)
        run_command("black src/ main.py dev.py", "Formatting Python code")
    except subprocess.CalledProcessError:
        print("Black not available, skipping code formatting")
        print("Install with: pip install black")


def lint_code():
    """Run linting checks."""
    print("Running linting...")
    
    try:
        # Check if flake8 is available
        subprocess.run("flake8 --version", shell=True, check=True, capture_output=True)
        run_command("flake8 src/ main.py --max-line-length=88", "Running flake8")
    except subprocess.CalledProcessError:
        print("Flake8 not available, skipping linting")
        print("Install with: pip install flake8")


def setup_dev():
    """Set up development environment."""
    print("Setting up development environment...")
    
    # Install requirements
    run_command("pip install -r requirements.txt", "Installing requirements")
    
    # Install optional dev dependencies
    dev_packages = ["pytest", "black", "flake8", "mypy"]
    for package in dev_packages:
        run_command(f"pip install {package}", f"Installing {package}")
    
    print("Development environment set up!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MyManaBox development utility")
    parser.add_argument("command", choices=[
        "clean", "test", "format", "lint", "setup", "all"
    ], help="Command to run")
    
    args = parser.parse_args()
    
    if args.command == "clean":
        clean_project()
    elif args.command == "test":
        run_tests()
    elif args.command == "format":
        format_code()
    elif args.command == "lint":
        lint_code()
    elif args.command == "setup":
        setup_dev()
    elif args.command == "all":
        print("Running all development tasks...")
        clean_project()
        format_code()
        lint_code()
        run_tests()
        print("All tasks completed!")


if __name__ == "__main__":
    main()
