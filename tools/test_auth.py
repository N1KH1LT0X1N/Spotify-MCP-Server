#!/usr/bin/env python3
"""
Standalone authentication test for Spotify MCP Server.
Run this to verify your Spotify credentials and test the OAuth flow.
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from spotify_mcp.auth import SpotifyAuthManager


def main():
    """Test Spotify authentication flow."""
    print("\n" + "=" * 60)
    print("Spotify MCP Server - Authentication Test")
    print("=" * 60 + "\n")
    
    print("This will test your Spotify credentials and OAuth setup.\n")
    
    try:
        # Initialize auth manager
        print("📝 Initializing authentication...")
        auth = SpotifyAuthManager()
        
        # Check if we already have valid tokens
        if auth.get_access_token():
            print(">> Already authenticated!\n")
            
            # Get user info to verify it works
            sp = auth.get_spotify_client()
            user = sp.current_user()
            
            print("Logged in as:")
            print(f"   Name: {user.get('display_name', 'N/A')}")
            print(f"   Email: {user.get('email', 'N/A')}")
            print(f"   Account: {user.get('product', 'FREE').upper()}")
            print(f"   Country: {user.get('country', 'N/A')}")
            print(f"   Followers: {user.get('followers', {}).get('total', 0):,}")
            
            print("\n>> Your Spotify MCP Server is ready to use!")
            print("\nNext steps:")
            print("   * Add to Claude Desktop config (see docs/setup/QUICK_SETUP.md)")
            print("   * Try: 'Play my Discover Weekly playlist'")
            return 0
            
        else:
            print(">> Starting OAuth flow...\n")
            print("Your browser will open for Spotify authorization.")
            print("   1. Log in to Spotify")
            print("   2. Click 'Agree' to authorize")
            print("   3. You'll see 'ERR_CONNECTION_REFUSED' - this is NORMAL!")
            print("   4. Copy the FULL URL from your browser's address bar")
            print("      (looks like: http://127.0.0.1:8888/callback?code=...)")
            print("   5. Paste it here\n")
            
            input("Press Enter when ready to open browser...")
            
            # Get authenticated client (will trigger OAuth flow)
            sp = auth.get_spotify_client()
            
            # Verify by getting user info
            user = sp.current_user()
            
            print("\n" + "=" * 60)
            print(">> Authentication Successful!")
            print("=" * 60 + "\n")
            
            print("Your Spotify Account:")
            print(f"   Name: {user.get('display_name', 'N/A')}")
            print(f"   Email: {user.get('email', 'N/A')}")
            print(f"   Account Type: {user.get('product', 'FREE').upper()}")
            
            if user.get('product') != 'premium':
                print("\nNote: Playback control requires Spotify Premium")
                print("   You can still use search, library, and discovery features!")
            
            print("\n>> Tokens saved! They'll auto-refresh when needed.")
            print("\n>> Ready to use with Claude Desktop!")
            print("   See docs/setup/QUICK_SETUP.md for configuration.")
            
            return 0
            
    except KeyboardInterrupt:
        print("\n\n!! Authentication cancelled.")
        return 1
        
    except Exception as e:
        print(f"\n!! Authentication failed: {str(e)}\n")
        print("Troubleshooting:")
        print("   1. Check your .env file has correct credentials")
        print("   2. Verify redirect URI: http://127.0.0.1:8888/callback")
        print("   3. Make sure it matches in both:")
        print("      * .env file")
        print("      * Spotify Developer Dashboard")
        print("   4. Use 127.0.0.1, NOT localhost")
        print("\nSee docs/setup/troubleshooting.md for more help.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
