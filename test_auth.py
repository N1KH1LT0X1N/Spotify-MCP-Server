#!/usr/bin/env python3
"""Test authentication and verify tokens are saved."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from spotify_mcp.auth import get_spotify_client
from dotenv import load_dotenv

def main():
    print("=" * 60)
    print("Testing Spotify Authentication")
    print("=" * 60)
    
    try:
        # This will authenticate if needed
        print("\nConnecting to Spotify...")
        client = get_spotify_client()
        
        # Get user info
        user = client.current_user()
        
        print("\n" + "=" * 60)
        print("✓ Authentication Successful!")
        print("=" * 60)
        print(f"\nUser: {user['display_name']}")
        print(f"Email: {user.get('email', 'N/A')}")
        print(f"Country: {user.get('country', 'N/A')}")
        print(f"Account: {user.get('product', 'free').upper()}")
        
        # Check if tokens were saved
        print("\n" + "-" * 60)
        print("Checking .env file...")
        load_dotenv(override=True)
        
        access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
        refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
        expires_at = os.getenv("SPOTIFY_TOKEN_EXPIRES_AT")
        
        if access_token and refresh_token and expires_at:
            print("✓ Access token saved")
            print("✓ Refresh token saved")
            print("✓ Expiry time saved")
            print(f"\nToken expires at: {expires_at}")
        else:
            print("⚠ Warning: Tokens may not be saved to .env file")
            print(f"  Access token: {'Found' if access_token else 'Missing'}")
            print(f"  Refresh token: {'Found' if refresh_token else 'Missing'}")
            print(f"  Expires at: {'Found' if expires_at else 'Missing'}")
        
        print("\n" + "=" * 60)
        print("You can now use the MCP server with Claude Desktop!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ Authentication Failed")
        print("=" * 60)
        print(f"\nError: {e}")
        print("\nPlease check:")
        print("1. Your Spotify credentials in .env are correct")
        print("2. The redirect URI is added to Spotify Dashboard")
        print("3. You completed the OAuth flow correctly")
        sys.exit(1)

if __name__ == "__main__":
    main()
