#!/usr/bin/env python3
"""
Spotify Auth Diagnostic Tool

Use this to:
- Check token status
- Force refresh tokens
- Re-authenticate if needed
- Clear tokens

Run: python diagnose_auth.py
Run: python diagnose_auth.py --interactive
"""

import os
import sys
import io
from datetime import datetime
from dotenv import load_dotenv

# Force UTF-8 encoding for Windows console compatibility
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        # Only wrap if not already wrapped and if buffer is available
        if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        if not isinstance(sys.stderr, io.TextIOWrapper) or sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except (AttributeError, io.UnsupportedOperation, ValueError):
        # Fallback: try reconfigure if available
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
            except (AttributeError, ValueError):
                pass

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from spotify_mcp.auth import SpotifyAuthManager

load_dotenv()


def print_header(text):
    """Print a nice header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def check_env_file():
    """Check if .env file exists and has tokens."""
    print_header("1. Checking .env File")
    
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("   Copy .env.example to .env and add your credentials")
        return False
    
    print("✓ .env file exists")
    
    # Check for credentials
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    print(f"   Client ID: {'Present' if client_id else '❌ Missing'}")
    print(f"   Client Secret: {'Present' if client_secret else '❌ Missing'}")
    
    if not client_id or not client_secret:
        print("\n❌ Missing Spotify credentials!")
        print("   Get them from: https://developer.spotify.com/dashboard")
        return False
    
    # Check for tokens
    access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
    refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
    expires_at = os.getenv("SPOTIFY_TOKEN_EXPIRES_AT")
    
    print(f"   Access token: {'Present' if access_token else 'Not yet authenticated'}")
    print(f"   Refresh token: {'Present' if refresh_token else 'Not yet authenticated'}")
    print(f"   Expiry time: {'Present' if expires_at else 'Not yet authenticated'}")
    
    return True


def check_token_status():
    """Check the status of tokens."""
    print_header("2. Token Status")
    
    try:
        auth = SpotifyAuthManager()
        status = auth.get_token_status()
        
        print(f"Has access token: {status.get('has_access_token')}")
        print(f"Has refresh token: {status.get('has_refresh_token')}")
        
        if status.get('expires_at'):
            print(f"Expires at: {status.get('expires_at')}")
            print(f"Is expired: {status.get('is_expired')}")
            
            if not status.get('is_expired'):
                print(f"Time until expiry: {status.get('expires_in_human')}")
            else:
                print("⚠️  Token is EXPIRED - needs refresh or re-auth")
        
        return status
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return None


def test_refresh():
    """Try to refresh the token."""
    print_header("3. Testing Token Refresh")
    
    try:
        auth = SpotifyAuthManager()
        
        if not os.getenv("SPOTIFY_REFRESH_TOKEN"):
            print("❌ No refresh token found - cannot refresh")
            print("   You'll need to authenticate first")
            return False
        
        print("Attempting to refresh token...")
        
        try:
            # Try to get token (will auto-refresh if needed)
            token = auth.get_access_token()
            print("✓ Token refresh successful!")
            print(f"   New token: {token[:20]}...")
            return True
        except Exception as e:
            print(f"❌ Refresh failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error during refresh: {e}")
        return False


def interactive_menu():
    """Show interactive menu."""
    print_header("🔧 Spotify Auth Diagnostic Tool - Interactive Mode")
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Check auth status")
        print("2. Test token refresh")
        print("3. Force re-authentication")
        print("4. Clear all tokens")
        print("5. View token details (verbose)")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            check_env_file()
            check_token_status()
            
        elif choice == "2":
            success = test_refresh()
            if success:
                print("\n✓ Your tokens are working correctly!")
            else:
                print("\n⚠️  Token refresh failed - you may need to re-authenticate")
                
        elif choice == "3":
            print("\n⚠️  This will clear your tokens and require re-authentication")
            confirm = input("Are you sure? (yes/no): ").strip().lower()
            
            if confirm == "yes":
                try:
                    auth = SpotifyAuthManager()
                    auth.clear_tokens()
                    print("\n✓ Tokens cleared")
                    print("Getting new token...")
                    token = auth.get_access_token()
                    print("✓ Re-authentication complete!")
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                print("Cancelled")
                
        elif choice == "4":
            print("\n⚠️  This will clear your tokens")
            confirm = input("Are you sure? (yes/no): ").strip().lower()
            
            if confirm == "yes":
                try:
                    auth = SpotifyAuthManager()
                    auth.clear_tokens()
                    print("✓ Tokens cleared")
                    print("\nRun 'python test_auth.py' to re-authenticate")
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                print("Cancelled")
        
        elif choice == "5":
            print("\n" + "="*60)
            print("Token Details (Verbose)")
            print("="*60)
            try:
                auth = SpotifyAuthManager(verbose=True)
                status = auth.get_token_status()
                
                for key, value in status.items():
                    print(f"{key:30s}: {value}")
                    
                print("\nTrying to get access token...")
                token = auth.get_access_token()
                print(f"\n✓ Token retrieved: {token[:30]}...")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                
        elif choice == "6":
            print("\nGoodbye!")
            break
            
        else:
            print("❌ Invalid choice")


def auto_diagnose():
    """Run automatic diagnostics."""
    print_header("🔍 Spotify Auth Diagnostics")
    
    # Step 1: Check .env
    if not check_env_file():
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("1. Create .env file from .env.example")
        print("2. Add your Spotify Client ID and Client Secret")
        print("3. Get credentials from: https://developer.spotify.com/dashboard")
        print("4. Run this diagnostic again")
        return
    
    # Step 2: Check token status
    status = check_token_status()
    if not status:
        return
    
    # Step 3: Determine issue
    print_header("4. Diagnosis")
    
    if not status.get('has_access_token'):
        print("ℹ️  STATUS: Not yet authenticated")
        print("   This is normal for first-time setup")
        print("\n   NEXT STEPS:")
        print("   1. Run: python test_auth.py")
        print("   2. Authorize in browser")
        print("   3. Paste redirect URL")
        print("   4. Tokens will be saved automatically")
        
    elif not status.get('has_refresh_token'):
        print("⚠️  ISSUE: No refresh token found")
        print("   This is unusual - token may be corrupted")
        print("\n   ACTION: Re-authenticate")
        print("   Run: python test_auth.py")
        
    elif status.get('is_expired'):
        print("⚠️  STATUS: Token is expired")
        print("   This is normal - tokens expire after 1 hour")
        print("   They should auto-refresh automatically")
        print("\nTesting auto-refresh now...")
        if test_refresh():
            print("\n✅ ALL GOOD: Tokens are working!")
            print("   Auto-refresh is functioning correctly")
        else:
            print("\n❌ PROBLEM: Token refresh failed")
            print("\n   POSSIBLE CAUSES:")
            print("   - Refresh token expired (after ~6 months of inactivity)")
            print("   - You revoked app access in Spotify Dashboard")
            print("   - Client Secret was rotated")
            print("\n   ACTION: Re-authenticate")
            print("   Run: python test_auth.py")
    else:
        print("✅ ALL GOOD: You have valid tokens!")
        expires_in = status.get('expires_in_human', 'unknown')
        print(f"   Token expires in: {expires_in}")
        print("\n   ✓ Your tokens will auto-refresh when needed")
        print("   ✓ You should NOT need to manually re-authenticate")
        print("   ✓ System is working correctly")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_menu()
    else:
        auto_diagnose()
        print("\n" + "="*60)
        print("💡 TIP: Run with --interactive for more options")
        print("   python diagnose_auth.py --interactive")
        print("="*60 + "\n")
