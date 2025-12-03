"""
Authentication and token management for Spotify API.
Handles OAuth 2.0 flow with PKCE and automatic token refresh.
Supports enterprise security features via SecurityManager.

Enhanced with:
- Verbose logging mode
- Token status diagnostics
- Better error messages and recovery
- Force refresh capability
"""

import os
import time
import webbrowser
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Import security manager (optional)
try:
    from .security import SecurityManager
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

# Load environment variables - only if not already loaded
# Use same strategy as server.py to ensure consistency
if not os.getenv("SPOTIFY_CLIENT_ID"):
    dotenv_path = find_dotenv(usecwd=True)
    if not dotenv_path:
        project_root = Path(__file__).parent.parent.parent
        potential_env = project_root / ".env"
        if potential_env.exists():
            dotenv_path = str(potential_env)
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        load_dotenv()  # Fallback to default behavior

# Required scopes for all features
SCOPES = [
    # Playback
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
    
    # Library
    "user-library-read",
    "user-library-modify",
    
    # Playlists
    "playlist-read-private",
    "playlist-read-collaborative",
    "playlist-modify-public",
    "playlist-modify-private",
    
    # User
    "user-read-private",
    "user-read-email",
    "user-top-read",
    "user-read-recently-played",
    
    # Follow
    "user-follow-read",
    "user-follow-modify",
    
    # Images (for playlist cover upload)
    "ugc-image-upload",
    
    # Listening History (for podcast/episode playback position)
    "user-read-playback-position",
]


class SpotifyAuthManager:
    """Manages Spotify authentication and token refresh with enhanced diagnostics."""
    
    def __init__(self, profile: str = "default", use_security: bool = False, verbose: bool = False):
        """
        Initialize auth manager.
        
        Args:
            profile: Profile name for multi-profile support
            use_security: Whether to use enterprise security features
            verbose: Enable detailed logging for diagnostics
        """
        self.profile = profile
        self.use_security = use_security and SECURITY_AVAILABLE
        self.verbose = verbose
        
        # Initialize security manager if available
        if self.use_security:
            self.security = SecurityManager(profile=profile)
        else:
            self.security = None
        
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Missing Spotify credentials. Please set SPOTIFY_CLIENT_ID and "
                "SPOTIFY_CLIENT_SECRET in your .env file.\n"
                "Get credentials from: https://developer.spotify.com/dashboard"
            )
        
        # Find .env file - check current directory first, then parent directories
        current_dir = os.getcwd()
        env_file = os.path.join(current_dir, ".env")
        
        # If .env not found in cwd, try to find project root
        if not os.path.exists(env_file):
            # Look for .env by going up directories until we find it or hit root
            search_dir = current_dir
            for _ in range(5):  # Search up to 5 levels
                test_path = os.path.join(search_dir, ".env")
                if os.path.exists(test_path):
                    env_file = test_path
                    break
                parent = os.path.dirname(search_dir)
                if parent == search_dir:  # Hit root
                    break
                search_dir = parent
        
        self.env_file = env_file
        self.sp_oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=" ".join(SCOPES),
            open_browser=True,
            cache_handler=None,  # We'll manage tokens ourselves
        )
    
    def _log(self, message: str):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            import sys
            print(f"[{timestamp}] {message}", file=sys.stderr)
    
    def get_token_status(self) -> dict:
        """Get detailed status of current tokens."""
        access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
        refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
        expires_at = os.getenv("SPOTIFY_TOKEN_EXPIRES_AT")
        
        status = {
            "has_access_token": bool(access_token),
            "has_refresh_token": bool(refresh_token),
            "has_expiry": bool(expires_at),
        }
        
        if expires_at:
            try:
                expires_timestamp = float(expires_at)
                expires_datetime = datetime.fromtimestamp(expires_timestamp)
                now = datetime.now()
                
                status["expires_at"] = expires_datetime.isoformat()
                status["is_expired"] = expires_timestamp <= time.time()
                status["expires_in_seconds"] = int(expires_timestamp - time.time())
                status["expires_in_human"] = str(expires_datetime - now)
            except (ValueError, OSError):
                status["expires_at"] = "invalid"
                status["is_expired"] = True
        
        return status
        
    def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        If no token exists, initiates OAuth flow.
        """
        # Check for existing token
        access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
        refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
        expires_at = os.getenv("SPOTIFY_TOKEN_EXPIRES_AT")
        
        self._log("Checking token status...")
        if self.verbose:
            status = self.get_token_status()
            self._log(f"Token status: {status}")
        
        # If we have a token and it's not expired, use it
        if access_token and expires_at:
            if float(expires_at) > time.time() + 60:  # Add 60s buffer
                self._log("✓ Using cached access token")
                return access_token
            
            # Token expired, try to refresh
            if refresh_token:
                self._log("⚠ Token expired or expiring soon, attempting refresh...")
                try:
                    # Track old token for rotation monitoring
                    old_refresh_token = refresh_token if self.use_security else None
                    
                    token_info = self.sp_oauth.refresh_access_token(refresh_token)
                    
                    # Track token rotation if security enabled
                    if self.use_security and old_refresh_token:
                        new_refresh_token = token_info.get("refresh_token", refresh_token)
                        self.security.track_token_rotation(old_refresh_token, new_refresh_token)
                    
                    self._save_token_info(token_info)
                    self._log("✓ Token refreshed successfully")
                    return token_info["access_token"]
                except Exception as e:
                    self._log(f"✗ Token refresh failed: {e}")
                    
                    # Better error messages
                    if "invalid" in str(e).lower() or "expired" in str(e).lower():
                        import sys
                        print("\n" + "="*60, file=sys.stderr)
                        print("⚠️  REFRESH TOKEN EXPIRED", file=sys.stderr)
                        print("="*60, file=sys.stderr)
                        print("Your refresh token has expired (typically after 6 months).", file=sys.stderr)
                        print("You'll need to re-authorize the application.", file=sys.stderr)
                        print("This is normal - your new tokens will last another 6 months.", file=sys.stderr)
                        print("="*60 + "\n", file=sys.stderr)
                    else:
                        import sys
                        print(f"\nError refreshing token: {e}", file=sys.stderr)
                        print("Will attempt to re-authenticate...\n", file=sys.stderr)
        
        # No valid token, start OAuth flow
        self._log("Starting OAuth flow...")
        return self._authenticate()
    
    def _authenticate(self) -> str:
        """Perform full OAuth authentication flow."""
        import sys
        
        # Write to stderr instead of stdout to avoid interfering with MCP JSON-RPC
        def eprint(*args, **kwargs):
            print(*args, file=sys.stderr, **kwargs)
        
        eprint("\n" + "="*60)
        eprint("🔐 SPOTIFY AUTHENTICATION REQUIRED")
        eprint("="*60)
        eprint("Opening browser for authorization...")
        eprint("After authorizing, you'll be redirected to 127.0.0.1")
        eprint("Copy the full URL from your browser and paste it here.")
        eprint("="*60 + "\n")
        
        # Get authorization URL
        auth_url = self.sp_oauth.get_authorize_url()
        
        try:
            webbrowser.open(auth_url)
            self._log(f"Opened browser to: {auth_url}")
        except Exception as e:
            self._log(f"Failed to open browser: {e}")
            eprint(f"Failed to open browser automatically: {e}")
        
        # Wait for user to paste the redirect URL
        eprint(f"If browser didn't open, go to:\n{auth_url}\n")
        eprint("Paste the redirect URL here: ")
        response_url = input().strip()
        
        # Validate the redirect URL to prevent injection
        if not response_url.startswith(self.redirect_uri.split('?')[0]):
            raise ValueError(f"Invalid redirect URL. Must start with: {self.redirect_uri}")
        
        # Extract code and get token
        try:
            code = self.sp_oauth.parse_response_code(response_url)
            self._log(f"Extracted auth code: {code[:10]}...")
            
            token_info = self.sp_oauth.get_access_token(code, check_cache=False)
            self._log("Received token info from Spotify")
            
            # Save token info
            self._save_token_info(token_info)
            
            eprint("\n" + "="*60)
            eprint("✓ AUTHENTICATION SUCCESSFUL")
            eprint("="*60)
            eprint("Your tokens have been saved and will auto-refresh.")
            eprint("You won't need to do this again for ~6 months.")
            eprint("="*60 + "\n")
            
            return token_info["access_token"]
            
        except Exception as e:
            self._log(f"✗ Authentication failed: {e}")
            eprint(f"\n✗ Authentication failed: {e}\n")
            raise
    
    def _save_token_info(self, token_info: dict):
        """Save token information to .env file or system keychain."""
        # Use security manager if enabled
        if self.use_security:
            use_keychain = os.getenv("SPOTIFY_USE_KEYCHAIN", "").lower() == "true"
            self.security.save_tokens(
                access_token=token_info["access_token"],
                refresh_token=token_info["refresh_token"],
                expires_at=token_info["expires_at"],
                use_keychain=use_keychain
            )
            return
        
        # Standard .env file storage
        if not os.path.exists(self.env_file):
            # Create .env from .env.example if it doesn't exist
            example_file = os.path.join(os.getcwd(), ".env.example")
            if os.path.exists(example_file):
                with open(example_file, 'r') as f:
                    with open(self.env_file, 'w') as new_f:
                        new_f.write(f.read())
        
        # Validate token_info
        required_keys = ["access_token", "refresh_token", "expires_at"]
        for key in required_keys:
            if key not in token_info:
                self._log(f"⚠ Missing {key} in token_info")
        
        set_key(self.env_file, "SPOTIFY_ACCESS_TOKEN", token_info["access_token"])
        set_key(self.env_file, "SPOTIFY_REFRESH_TOKEN", token_info["refresh_token"])
        set_key(self.env_file, "SPOTIFY_TOKEN_EXPIRES_AT", str(token_info["expires_at"]))
        
        # Log token expiry
        if self.verbose:
            expires_at = datetime.fromtimestamp(token_info["expires_at"])
            self._log(f"Tokens saved. Access token expires at: {expires_at}")
        
        # Reload environment variables
        load_dotenv(override=True)
    
    def is_authenticated(self) -> bool:
        """Check if we have valid authentication."""
        return bool(os.getenv("SPOTIFY_ACCESS_TOKEN"))
    
    def force_refresh(self) -> bool:
        """Force a token refresh. Returns True if successful."""
        refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
        
        if not refresh_token:
            import sys
            print("✗ No refresh token found. Need to re-authenticate.", file=sys.stderr)
            return False
        
        try:
            import sys
            print("Forcing token refresh...", file=sys.stderr)
            token_info = self.sp_oauth.refresh_access_token(refresh_token)
            self._save_token_info(token_info)
            print("✓ Token refreshed successfully!", file=sys.stderr)
            return True
        except Exception as e:
            import sys
            print(f"✗ Refresh failed: {e}", file=sys.stderr)
            return False
    
    def clear_tokens(self):
        """Clear saved tokens (useful for re-authentication)."""
        set_key(self.env_file, "SPOTIFY_ACCESS_TOKEN", "")
        set_key(self.env_file, "SPOTIFY_REFRESH_TOKEN", "")
        set_key(self.env_file, "SPOTIFY_TOKEN_EXPIRES_AT", "")
        load_dotenv(override=True)
        import sys
        print("✓ Tokens cleared", file=sys.stderr)


def get_spotify_client(verbose: bool = False) -> spotipy.Spotify:
    """
    Get an authenticated Spotify client.
    Handles token refresh automatically.
    
    Args:
        verbose: Enable detailed logging for diagnostics
    """
    auth_manager = SpotifyAuthManager(verbose=verbose)
    token = auth_manager.get_access_token()
    
    return spotipy.Spotify(auth=token)


# Diagnostic CLI Tool
if __name__ == "__main__":
    import sys
    
    print("\n🔍 Spotify Authentication Diagnostic Tool\n")
    
    auth = SpotifyAuthManager(verbose=True)
    
    print("Current Token Status:")
    print("-" * 40)
    status = auth.get_token_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    print()
    
    print("What would you like to do?")
    print("1. Get access token (auto-refresh if needed)")
    print("2. Force refresh")
    print("3. Clear tokens")
    print("4. Exit")
    choice = input("> ").strip()
    
    if choice == "1":
        try:
            token = auth.get_access_token()
            print(f"\n✓ Got access token: {token[:20]}...\n", file=sys.stderr)
        except Exception as e:
            print(f"\n✗ Failed: {e}\n", file=sys.stderr)
    elif choice == "2":
        auth.force_refresh()
    elif choice == "3":
        auth.clear_tokens()
    else:
        print("Exiting...")
