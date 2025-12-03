#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spotify MCP Server - Interactive Setup Guide
Run this to get step-by-step guidance on setting up your server.
"""

import os
import sys
import io
from pathlib import Path

# Force UTF-8 encoding for Windows console compatibility
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, io.UnsupportedOperation):
        pass


def print_header(text):
    """Print a nice header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_step(number, title):
    """Print a step header."""
    print(f"\n{'─' * 70}")
    print(f">> STEP {number}: {title}")
    print('─' * 70 + "\n")


def check_python_version():
    """Check if Python version is adequate."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("!! Python 3.10+ required")
        print(f"   You have: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f">> Python {version.major}.{version.minor}.{version.micro} - Good!")
    return True


def check_env_file():
    """Check if .env file exists."""
    if Path(".env").exists():
        print(">> .env file exists")
        return True
    else:
        print("!! .env file not found")
        return False


def check_dependencies():
    """Check if dependencies are installed."""
    try:
        import mcp
        import spotipy
        import dotenv
        print(">> Dependencies installed")
        return True
    except ImportError:
        print("!! Dependencies not installed")
        return False


def main():
    """Run interactive setup guide."""
    print_header("Spotify MCP Server - Setup Guide")
    
    print("Welcome! This guide will help you set up your Spotify MCP Server.")
    print("You'll be up and running in about 5 minutes.\n")
    
    input("Press Enter to begin...")
    
    # Step 1: Check Python
    print_step(1, "Verify Python Version")
    if not check_python_version():
        print("\n!! Please upgrade Python to 3.10 or higher")
        print("   Download from: https://www.python.org/downloads/")
        return 1
    
    input("\nPress Enter to continue...")
    
    # Step 2: Install Dependencies
    print_step(2, "Install Dependencies")
    
    if check_dependencies():
        print("\nDependencies already installed! Moving on...")
    else:
        print("Installing dependencies with pip...")
        print("\n>> Run this command:")
        print("   pip install -e .")
        print("\nThis installs the server in development mode.")
        
        response = input("\nHave you run this command? (y/n): ").lower()
        if response != 'y':
            print("\n-- Setup paused. Run 'pip install -e .' then restart this guide.")
            return 0
    
    input("\nPress Enter to continue...")
    
    # Step 3: Create Spotify App
    print_step(3, "Create Spotify Developer App")
    
    print("You need a Spotify Developer account (free) to use the API.")
    print("\n>> Follow these steps:")
    print("\n1. Open: https://developer.spotify.com/dashboard")
    print("2. Log in with your Spotify account")
    print("3. Click 'Create app'")
    print("4. Fill in:")
    print("   * Name: 'My Spotify MCP' (or anything)")
    print("   * Description: 'MCP server for AI'")
    print("   * Redirect URI: http://127.0.0.1:8888/callback")
    print("     !! IMPORTANT: Use 127.0.0.1, NOT localhost!")
    print("   * Web API: Check this box")
    print("5. Save and click 'Settings'")
    print("6. Copy your Client ID and Client Secret")
    
    input("\nPress Enter when you have your credentials...")
    
    # Step 4: Configure Environment
    print_step(4, "Configure Environment")
    
    if check_env_file():
        print("\nYour .env file exists. Make sure it has:")
        print("   * SPOTIFY_CLIENT_ID")
        print("   * SPOTIFY_CLIENT_SECRET")
        print("   * SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback")
    else:
        print("Creating .env file...")
        if Path(".env.example").exists():
            print("\n>> Copying .env.example to .env...")
            import shutil
            shutil.copy(".env.example", ".env")
            print(">> Created .env file")
            print("\n>> Now edit .env and paste your credentials:")
            print("   * SPOTIFY_CLIENT_ID=<paste_your_client_id>")
            print("   * SPOTIFY_CLIENT_SECRET=<paste_your_client_secret>")
        else:
            print("!! .env.example not found")
            print("   Create .env manually with your credentials")
    
    input("\nPress Enter when .env is configured...")
    
    # Step 5: Test Authentication
    print_step(5, "Test Authentication")
    
    print("Let's verify everything works!")
    print("\n>> Run this command:")
    print("   python test_auth.py")
    print("\nThis will:")
    print("   1. Open your browser for Spotify login")
    print("   2. You'll see 'ERR_CONNECTION_REFUSED' - that's NORMAL!")
    print("   3. Copy the full URL from your browser")
    print("   4. Paste it back in the terminal")
    print("   5. Your tokens will be saved")
    
    response = input("\nRun test_auth.py now? (y/n): ").lower()
    if response == 'y':
        print("\n>> Starting authentication test...\n")
        import subprocess
        subprocess.run([sys.executable, "test_auth.py"])
    
    # Final Step: Claude Desktop
    print_step(6, "Add to Claude Desktop")
    
    print("Almost there! Final step: connect to Claude Desktop.")
    print("\n>> Configuration guide:")
    print("   docs/setup/QUICK_SETUP.md")
    print("\nThis has copy-paste config for:")
    print("   * Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print("   * macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("   * Linux: ~/.config/Claude/claude_desktop_config.json")
    
    print("\n" + "=" * 70)
    print(">> Setup Complete!")
    print("=" * 70)
    print("\n>> You're ready to control Spotify through AI!")
    print("\n>> Try saying to Claude:")
    print('   "Play my Discover Weekly playlist"')
    print('   "Search for chill jazz music"')
    print('   "What are my top artists?"')
    print("\nFull documentation: docs/README.md")
    print("Having issues? docs/setup/troubleshooting.md")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n!! Setup cancelled. Run again anytime!")
        sys.exit(0)
