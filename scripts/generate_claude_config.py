#!/usr/bin/env python3
"""Generate Claude Desktop configuration for Spotify MCP Server."""

import json
import os
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_python_path() -> str:
    """Get the current Python executable path."""
    return sys.executable


def get_src_path() -> str:
    """Get the src directory path."""
    return str(get_project_root() / "src")


def load_env_vars() -> dict:
    """Load environment variables from .env file."""
    env_file = get_project_root() / ".env"
    env_vars = {}
    
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars


def generate_config(use_venv: bool = False) -> dict:
    """Generate Claude Desktop configuration."""
    env_vars = load_env_vars()
    
    # Mask credentials for display (security)
    client_id = env_vars.get("SPOTIFY_CLIENT_ID", "your_client_id_here")
    client_secret = env_vars.get("SPOTIFY_CLIENT_SECRET", "your_client_secret_here")
    
    # Use masked values if real credentials are present
    if client_id and client_id != "your_client_id_here" and len(client_id) > 8:
        display_client_id = f"{client_id[:4]}...{client_id[-4:]}"
    else:
        display_client_id = client_id
    
    if client_secret and client_secret != "your_client_secret_here" and len(client_secret) > 8:
        display_client_secret = f"{client_secret[:4]}...{client_secret[-4:]}"
    else:
        display_client_secret = client_secret
    
    config = {
        "mcpServers": {
            "spotify": {
                "command": get_python_path() if use_venv else "python",
                "args": ["-m", "spotify_mcp.server"],
                "env": {
                    "SPOTIFY_CLIENT_ID": display_client_id,
                    "SPOTIFY_CLIENT_SECRET": display_client_secret,
                    "SPOTIFY_REDIRECT_URI": env_vars.get("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback"),
                }
            }
        }
    }
    
    # Add PYTHONPATH if not using venv
    if not use_venv:
        config["mcpServers"]["spotify"]["env"]["PYTHONPATH"] = get_src_path()
    
    return config


def get_config_path() -> Path:
    """Get the Claude Desktop config file path."""
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def main():
    """Main entry point."""
    print("🎵 Spotify MCP Server - Claude Desktop Configuration Generator")
    print("=" * 70)
    print()
    
    # Detect if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    print(f"Project root: {get_project_root()}")
    print(f"Python path: {get_python_path()}")
    print(f"In virtual environment: {'Yes' if in_venv else 'No'}")
    print()
    
    # Generate configurations
    print("Configuration Options:")
    print()
    print("1️⃣  Using Virtual Environment (Recommended if installed)")
    config_venv = generate_config(use_venv=True)
    print(json.dumps(config_venv, indent=2))
    print()
    
    print("2️⃣  Using PYTHONPATH (Recommended if not installed)")
    config_pythonpath = generate_config(use_venv=False)
    print(json.dumps(config_pythonpath, indent=2))
    print()
    
    # Show config file location
    config_path = get_config_path()
    print(f"📁 Claude Desktop config location:")
    print(f"   {config_path}")
    print()
    
    if not config_path.exists():
        print("⚠️  Config file doesn't exist yet. It will be created when you first configure Claude Desktop.")
    else:
        print("✅ Config file exists!")
        print()
        print("To add Spotify MCP Server:")
        print("1. Open the config file in your editor")
        print("2. Copy one of the configurations above")
        print("3. Replace or add to the 'mcpServers' section")
        print("4. Save and restart Claude Desktop")
    
    print()
    print("💡 Tip: Credentials are masked for security (shown as 'xxxx...yyyy')")
    print("   The actual values from your .env will be used in Claude Desktop")
    print()
    print("For more information, see CLAUDE_DESKTOP_SETUP.md")


if __name__ == "__main__":
    main()
