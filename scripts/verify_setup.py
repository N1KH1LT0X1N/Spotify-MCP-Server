#!/usr/bin/env python3
"""
Setup verification script for Spotify MCP Server.
Checks that all dependencies are installed and configuration is correct.
"""

import sys
import os


def check_python_version():
    """Check Python version is 3.10 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Check that required packages are installed."""
    required = ["mcp", "spotipy", "dotenv", "pydantic"]
    missing = []
    
    for package in required:
        try:
            if package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"❌ {package} not installed")
            missing.append(package)
    
    if missing:
        print("\nInstall missing packages with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True


def check_env_file():
    """Check .env file exists and has required variables."""
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        print("   Copy .env.example to .env and fill in your credentials")
        return False
    
    print("✓ .env file exists")
    
    # Load and check required variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "SPOTIFY_REDIRECT_URI"]
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f"your_{var.lower().replace('spotify_', '')}":
            missing.append(var)
        else:
            print(f"✓ {var} configured")
    
    if missing:
        print(f"\n❌ Missing or incomplete configuration:")
        for var in missing:
            print(f"   - {var}")
        print("\nEdit .env file and add your Spotify credentials")
        print("Get them from: https://developer.spotify.com/dashboard")
        return False
    
    return True


def check_spotify_app():
    """Provide instructions for creating Spotify app."""
    print("\nSpotify App Setup:")
    print("1. Go to https://developer.spotify.com/dashboard")
    print("2. Log in with your Spotify account")
    print("3. Click 'Create app'")
    print("4. Fill in:")
    print("   - App name: (anything you like)")
    print("   - Redirect URI: http://127.0.0.1:8888/callback")
    print("   ⚠️  IMPORTANT: Use 127.0.0.1, not localhost!")
    print("5. Copy Client ID and Client Secret to .env file")


def main():
    """Run all checks."""
    print("Spotify MCP Server - Setup Verification\n")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Configuration", check_env_file),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("\n✅ All checks passed! Your Spotify MCP Server is ready!")
        print("\n🚀 Next Steps:")
        print("\n1. Standalone testing:")
        print("   python test_auth.py")
        print("\n2. Use with Claude Desktop:")
        print("   See docs/setup/QUICK_SETUP.md for configuration")
        print("\n3. On first run, you'll authenticate with Spotify in your browser.")
        print("   After authorization, copy the full URL and paste it back.")
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        check_spotify_app()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
