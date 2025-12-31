#!/usr/bin/env python3
"""
Quick Start Script for Smart Agriculture Platform
Helps users get the system running quickly
"""

import subprocess
import sys
import os
import time


def print_header():
    print("=" * 60)
    print("🌱 Smart Agriculture Platform - Quick Start")
    print("=" * 60)
    print()


def check_python_version():
    """Check if Python version is adequate"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def install_dependencies():
    """Install required packages"""
    print("\nInstalling dependencies...")
    print("This may take a few minutes...\n")

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"]
        )
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("   Try running manually: pip install -r requirements.txt")
        return False


def initialize_database():
    """Initialize the database"""
    print("\nInitializing database...")
    try:
        from database import DatabaseManager

        db = DatabaseManager()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False


def test_imports():
    """Test if all required modules can be imported"""
    print("\nTesting module imports...")

    modules = [
        ("fastapi", "FastAPI"),
        ("streamlit", "Streamlit"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"),
        ("plotly", "Plotly"),
        ("pandas", "Pandas"),
        ("requests", "Requests"),
    ]

    all_ok = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name}")
            all_ok = False

    return all_ok


def print_instructions():
    """Print usage instructions"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete! Here's how to start the system:")
    print("=" * 60)
    print()
    print("OPTION 1: Using two terminal windows (Recommended)")
    print("-" * 60)
    print("Terminal 1 (Backend):")
    print("  python backend.py")
    print()
    print("Terminal 2 (Frontend):")
    print("  streamlit run frontend.py")
    print()
    print("OPTION 2: Using tmux or screen")
    print("-" * 60)
    print("  tmux")
    print("  python backend.py")
    print("  # Press Ctrl+B, then D to detach")
    print("  streamlit run frontend.py")
    print()
    print("=" * 60)
    print("Access Points:")
    print("  🌐 Dashboard: http://localhost:8501")
    print("  📡 API Docs:  http://localhost:8000/docs")
    print("=" * 60)
    print()


def main():
    print_header()

    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)

    # Step 2: Install dependencies
    if not install_dependencies():
        print("\n⚠️  You can try installing dependencies manually:")
        print("   pip install -r requirements.txt")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != "y":
            sys.exit(1)

    # Step 3: Test imports
    if not test_imports():
        print("\n❌ Some modules failed to import. Please check your installation.")
        sys.exit(1)

    # Step 4: Initialize database
    if not initialize_database():
        print(
            "\n⚠️  Database initialization failed, but you can try starting the system."
        )

    # Step 5: Print instructions
    print_instructions()

    # Ask if user wants to start now
    response = input("Would you like to start the backend now? (y/n): ")
    if response.lower() == "y":
        print("\nStarting backend server...")
        print("After the backend starts, open a new terminal and run:")
        print("  streamlit run frontend.py")
        print("\nPress Ctrl+C to stop the backend when done.\n")
        time.sleep(2)

        try:
            subprocess.run([sys.executable, "backend.py"])
        except KeyboardInterrupt:
            print("\n\n👋 Backend stopped. Goodbye!")


if __name__ == "__main__":
    main()
