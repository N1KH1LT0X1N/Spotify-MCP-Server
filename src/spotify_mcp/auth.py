"""
Authentication and token management for Spotify API.
Handles OAuth 2.0 flow with PKCE and automatic token refresh.
"""

import os
import time
import webbrowser
from typing import Optional
from dotenv import load_dotenv, set_key
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables
load_dotenv()

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
]


class SpotifyAuthManager:
    """Manages Spotify authentication and token refresh."""
    
    def __init__(self):
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
        
    def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        If no token exists, initiates OAuth flow.
        """
        # Check for existing token
        access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
        refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
        expires_at = os.getenv("SPOTIFY_TOKEN_EXPIRES_AT")
        
        # If we have a token and it's not expired, use it
        if access_token and expires_at:
            if float(expires_at) > time.time() + 60:  # Add 60s buffer
                return access_token
            
            # Token expired, try to refresh
            if refresh_token:
                try:
                    token_info = self.sp_oauth.refresh_access_token(refresh_token)
                    self._save_token_info(token_info)
                    return token_info["access_token"]
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    print("Re-authenticating...")
        
        # No valid token, start OAuth flow
        return self._authenticate()
    
    def _authenticate(self) -> str:
        """Perform full OAuth authentication flow."""
        import sys
        
        # Write to stderr instead of stdout to avoid interfering with MCP JSON-RPC
        def eprint(*args, **kwargs):
            print(*args, file=sys.stderr, **kwargs)
        
        eprint("\n=== Spotify Authentication Required ===")
        eprint("Opening browser for authentication...")
        eprint("After authorizing, you'll be redirected to 127.0.0.1")
        eprint("Copy the full URL from your browser and paste it here.\n")
        
        # Get authorization URL
        auth_url = self.sp_oauth.get_authorize_url()
        webbrowser.open(auth_url)
        
        # Wait for user to paste the redirect URL
        eprint(f"If browser didn't open, go to: {auth_url}\n")
        eprint("Paste the redirect URL here: ")
        response_url = input().strip()
        
        # Extract code and get token
        code = self.sp_oauth.parse_response_code(response_url)
        token_info = self.sp_oauth.get_access_token(code, check_cache=False)
        
        # Save token info
        self._save_token_info(token_info)
        
        eprint("\n✓ Authentication successful! Token saved.\n")
        return token_info["access_token"]
    
    def _save_token_info(self, token_info: dict):
        """Save token information to .env file."""
        if not os.path.exists(self.env_file):
            # Create .env from .env.example if it doesn't exist
            example_file = os.path.join(os.getcwd(), ".env.example")
            if os.path.exists(example_file):
                with open(example_file, 'r') as f:
                    with open(self.env_file, 'w') as new_f:
                        new_f.write(f.read())
        
        set_key(self.env_file, "SPOTIFY_ACCESS_TOKEN", token_info["access_token"])
        set_key(self.env_file, "SPOTIFY_REFRESH_TOKEN", token_info["refresh_token"])
        set_key(self.env_file, "SPOTIFY_TOKEN_EXPIRES_AT", str(token_info["expires_at"]))
        
        # Reload environment variables
        load_dotenv(override=True)
    
    def is_authenticated(self) -> bool:
        """Check if we have valid authentication."""
        return bool(os.getenv("SPOTIFY_ACCESS_TOKEN"))
    
    def clear_tokens(self):
        """Clear saved tokens (useful for re-authentication)."""
        set_key(self.env_file, "SPOTIFY_ACCESS_TOKEN", "")
        set_key(self.env_file, "SPOTIFY_REFRESH_TOKEN", "")
        set_key(self.env_file, "SPOTIFY_TOKEN_EXPIRES_AT", "")
        load_dotenv(override=True)
        print("Tokens cleared. Run again to re-authenticate.")


def get_spotify_client() -> spotipy.Spotify:
    """
    Get an authenticated Spotify client.
    Handles token refresh automatically.
    """
    auth_manager = SpotifyAuthManager()
    token = auth_manager.get_access_token()
    
    return spotipy.Spotify(auth=token)
