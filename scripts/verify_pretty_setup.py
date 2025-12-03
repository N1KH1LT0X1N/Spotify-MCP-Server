#!/usr/bin/env python3
"""Test script to verify the Spotify MCP Server setup for Claude Desktop."""

import json
import sys
import io
from pathlib import Path
import os

# Force UTF-8 encoding for Windows console compatibility
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, io.UnsupportedOperation):
        pass


def print_header(text: str):
    """Print a formatted header."""
    print()
    print("=" * 70)
    print(f"  {text}")
    print("=" * 70)
    print()


def check_icon():
    """Check if icon exists."""
    print_header("🎨 Icon Check")
    
    icon_path = Path(__file__).parent.parent / "icon.svg"
    
    if icon_path.exists():
        size = icon_path.stat().st_size
        print(f"✅ Icon found: {icon_path}")
        print(f"   Size: {size:,} bytes")
        
        # Check if it's valid SVG
        with open(icon_path, "r") as f:
            content = f.read()
            if "<svg" in content and "#1DB954" in content:
                print("✅ Valid SVG with Spotify green color")
            else:
                print("⚠️  SVG might be invalid or missing Spotify branding")
    else:
        print(f"❌ Icon not found at {icon_path}")
        return False
    
    return True


def check_server_metadata():
    """Check server metadata in pyproject.toml."""
    print_header("📦 Server Metadata")
    
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    if not pyproject_path.exists():
        print(f"❌ pyproject.toml not found")
        return False
    
    with open(pyproject_path, "r") as f:
        content = f.read()
        
    checks = [
        ("name = \"spotify-mcp\"", "Package name"),
        ("description = ", "Description"),
        ("🎵", "Emoji in description"),
    ]
    
    for check, label in checks:
        if check in content:
            print(f"✅ {label}")
        else:
            print(f"⚠️  {label} might be missing or different")
    
    return True


def check_claude_config():
    """Check Claude Desktop configuration."""
    print_header("⚙️  Claude Desktop Configuration")
    
    if sys.platform == "win32":
        config_path = Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "darwin":
        config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:
        config_path = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    
    print(f"Config location: {config_path}")
    
    if not config_path.exists():
        print("⚠️  Claude Desktop config not found")
        print("   Create it by adding the configuration from QUICK_SETUP.md")
        return False
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        
        if "mcpServers" in config and "spotify" in config["mcpServers"]:
            print("✅ Spotify server configured!")
            
            spotify_config = config["mcpServers"]["spotify"]
            print(f"   Command: {spotify_config.get('command', 'N/A')}")
            print(f"   Has credentials: {'Yes' if 'SPOTIFY_CLIENT_ID' in spotify_config.get('env', {}) else 'No'}")
        else:
            print("⚠️  Spotify server not found in config")
            print("   Add the configuration from QUICK_SETUP.md")
            return False
    
    except json.JSONDecodeError:
        print("❌ Config file is not valid JSON")
        return False
    
    return True


def check_setup_docs():
    """Check if setup documentation exists."""
    print_header("📚 Documentation")
    
    root = Path(__file__).parent.parent
    docs = [
        ("QUICK_SETUP.md", "Quick setup guide"),
        ("CLAUDE_DESKTOP_SETUP.md", "Detailed setup guide"),
        ("PRETTY_SETUP_SUMMARY.md", "Setup summary"),
    ]
    
    all_exist = True
    for filename, description in docs:
        path = root / filename
        if path.exists():
            print(f"✅ {description}: {filename}")
        else:
            print(f"❌ Missing: {filename}")
            all_exist = False
    
    return all_exist


def main():
    """Main entry point."""
    print()
    print("🎵" * 35)
    print("  Spotify MCP Server - Setup Verification")
    print("🎵" * 35)
    
    checks = [
        ("Icon", check_icon),
        ("Metadata", check_server_metadata),
        ("Claude Config", check_claude_config),
        ("Documentation", check_setup_docs),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            results.append((name, False))
    
    # Summary
    print_header("📊 Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "⚠️ "
        print(f"{status} {name}")
    
    print()
    print(f"Score: {passed}/{total}")
    
    if passed == total:
        print()
        print("🎉 Perfect! Everything is set up correctly!")
        print()
        print("Next steps:")
        print("1. Copy the config from QUICK_SETUP.md")
        print("2. Add it to your Claude Desktop config")
        print("3. Restart Claude Desktop")
        print("4. Look for the Spotify icon with green branding! 🎵")
    else:
        print()
        print("⚠️  Some checks failed. See details above.")
        print("   Check QUICK_SETUP.md or CLAUDE_DESKTOP_SETUP.md for help")
    
    print()


if __name__ == "__main__":
    main()
