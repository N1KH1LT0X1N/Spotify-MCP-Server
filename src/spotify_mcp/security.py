"""
Enterprise-grade security features for Spotify MCP Server.

Features:
- System keychain integration
- Token revocation
- Multi-profile support
- Token rotation tracking
- Security audit logging
"""

import os
import sys
import io
import json
import time
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
from dotenv import load_dotenv, set_key

# Force UTF-8 encoding for Windows console compatibility
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, io.UnsupportedOperation):
        pass

# Optional: System keychain integration
try:
    import keyring
except ImportError:
    keyring = None

KEYRING_AVAILABLE = keyring is not None


class SecurityManager:
    """Manages security features for token storage and authentication."""
    
    SERVICE_NAME = "spotify-mcp"
    AUDIT_LOG = ".auth_audit.json"
    
    def __init__(self, profile: str = "default"):
        """
        Initialize security manager.
        
        Args:
            profile: Profile name for multi-profile support
        """
        self.profile = profile
        self.env_file = self._get_env_file(profile)
        load_dotenv(self.env_file)
        
    def _get_env_file(self, profile: str) -> str:
        """Get .env file path for profile."""
        if profile == "default":
            return ".env"
        return f".env.{profile}"
    
    # ==================== Keychain Integration ====================
    
    def use_keychain(self) -> bool:
        """Check if system keychain is available."""
        return KEYRING_AVAILABLE
    
    def save_to_keychain(self, key: str, value: str) -> bool:
        """
        Save credential to system keychain.
        
        Args:
            key: Credential key (e.g., "access_token")
            value: Credential value
            
        Returns:
            True if saved successfully
        """
        if not KEYRING_AVAILABLE:
            return False
        
        try:
            keyring.set_password(self.SERVICE_NAME, f"{self.profile}:{key}", value)
            self._log_audit("keychain_save", {"key": key, "profile": self.profile})
            return True
        except Exception as e:
            print(f"Keychain save failed: {e}")
            return False
    
    def get_from_keychain(self, key: str) -> Optional[str]:
        """
        Retrieve credential from system keychain.
        
        Args:
            key: Credential key
            
        Returns:
            Credential value or None
        """
        if not KEYRING_AVAILABLE:
            return None
        
        try:
            value = keyring.get_password(self.SERVICE_NAME, f"{self.profile}:{key}")
            if value:
                self._log_audit("keychain_access", {"key": key, "profile": self.profile})
            return value
        except Exception as e:
            print(f"Keychain access failed: {e}")
            return None
    
    def clear_keychain(self) -> bool:
        """
        Clear all credentials from system keychain for this profile.
        
        Returns:
            True if cleared successfully
        """
        if not KEYRING_AVAILABLE:
            return False
        
        keys = ["access_token", "refresh_token", "token_expires_at", 
                "client_id", "client_secret"]
        
        try:
            for key in keys:
                try:
                    keyring.delete_password(self.SERVICE_NAME, f"{self.profile}:{key}")
                except keyring.errors.PasswordDeleteError:
                    pass  # Key doesn't exist
            
            self._log_audit("keychain_clear", {"profile": self.profile})
            return True
        except Exception as e:
            print(f"Keychain clear failed: {e}")
            return False
    
    # ==================== Token Management ====================
    
    def save_tokens(self, access_token: str, refresh_token: str, 
                   expires_at: int, use_keychain: bool = False) -> bool:
        """
        Save tokens to .env or keychain.
        
        Args:
            access_token: Spotify access token
            refresh_token: Spotify refresh token
            expires_at: Token expiration timestamp
            use_keychain: Whether to use system keychain
            
        Returns:
            True if saved successfully
        """
        if use_keychain and KEYRING_AVAILABLE:
            # Save to keychain
            success = all([
                self.save_to_keychain("access_token", access_token),
                self.save_to_keychain("refresh_token", refresh_token),
                self.save_to_keychain("token_expires_at", str(expires_at))
            ])
            
            if success:
                # Also save a marker in .env to indicate keychain usage
                set_key(self.env_file, "SPOTIFY_USE_KEYCHAIN", "true")
                self._log_audit("tokens_saved", {
                    "storage": "keychain",
                    "profile": self.profile,
                    "expires_at": expires_at
                })
            return success
        else:
            # Save to .env file
            set_key(self.env_file, "SPOTIFY_ACCESS_TOKEN", access_token)
            set_key(self.env_file, "SPOTIFY_REFRESH_TOKEN", refresh_token)
            set_key(self.env_file, "SPOTIFY_TOKEN_EXPIRES_AT", str(expires_at))
            
            self._log_audit("tokens_saved", {
                "storage": "env_file",
                "profile": self.profile,
                "expires_at": expires_at
            })
            return True
    
    def get_tokens(self) -> Dict[str, Optional[str]]:
        """
        Get tokens from .env or keychain.
        
        Returns:
            Dict with access_token, refresh_token, expires_at
        """
        use_keychain = os.getenv("SPOTIFY_USE_KEYCHAIN", "").lower() == "true"
        
        if use_keychain and KEYRING_AVAILABLE:
            return {
                "access_token": self.get_from_keychain("access_token"),
                "refresh_token": self.get_from_keychain("refresh_token"),
                "expires_at": self.get_from_keychain("token_expires_at")
            }
        else:
            return {
                "access_token": os.getenv("SPOTIFY_ACCESS_TOKEN"),
                "refresh_token": os.getenv("SPOTIFY_REFRESH_TOKEN"),
                "expires_at": os.getenv("SPOTIFY_TOKEN_EXPIRES_AT")
            }
    
    def revoke_tokens(self) -> Dict[str, any]:
        """
        Revoke Spotify access and clear all tokens.
        
        Returns:
            Status dict with success and message
        """
        try:
            # Clear from .env
            set_key(self.env_file, "SPOTIFY_ACCESS_TOKEN", "")
            set_key(self.env_file, "SPOTIFY_REFRESH_TOKEN", "")
            set_key(self.env_file, "SPOTIFY_TOKEN_EXPIRES_AT", "")
            
            # Clear from keychain if used
            if os.getenv("SPOTIFY_USE_KEYCHAIN", "").lower() == "true":
                self.clear_keychain()
            
            self._log_audit("tokens_revoked", {
                "profile": self.profile,
                "timestamp": time.time()
            })
            
            return {
                "success": True,
                "message": f"Access revoked for profile '{self.profile}'. Run authentication again to restore access."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to revoke access: {str(e)}"
            }
    
    # ==================== Token Rotation Tracking ====================
    
    def track_token_rotation(self, old_refresh_token: Optional[str], 
                           new_refresh_token: str) -> None:
        """
        Track refresh token rotation for security monitoring.
        
        Args:
            old_refresh_token: Previous refresh token (last 8 chars)
            new_refresh_token: New refresh token (last 8 chars)
        """
        # Only log last 8 characters for security
        old_suffix = old_refresh_token[-8:] if old_refresh_token else "none"
        new_suffix = new_refresh_token[-8:] if new_refresh_token else "none"
        
        self._log_audit("token_rotation", {
            "profile": self.profile,
            "old_token_suffix": old_suffix,
            "new_token_suffix": new_suffix,
            "timestamp": time.time()
        })
        
        # Check for token reuse (security alert)
        if old_refresh_token and old_refresh_token == new_refresh_token:
            self._log_audit("security_alert", {
                "type": "token_reuse_detected",
                "profile": self.profile,
                "severity": "warning",
                "message": "Refresh token was not rotated during renewal"
            })
    
    # ==================== Audit Logging ====================
    
    def _log_audit(self, event_type: str, data: Dict) -> None:
        """
        Log security-related events for audit trail.
        
        Args:
            event_type: Type of event (e.g., "tokens_saved")
            data: Event-specific data
        """
        audit_log_path = Path(self.AUDIT_LOG)
        
        # Load existing log
        if audit_log_path.exists():
            with open(audit_log_path, 'r') as f:
                try:
                    log = json.load(f)
                except json.JSONDecodeError:
                    log = []
        else:
            log = []
        
        # Add new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "data": data
        }
        log.append(entry)
        
        # Keep only last 100 entries
        log = log[-100:]
        
        # Save log
        with open(audit_log_path, 'w') as f:
            json.dump(log, f, indent=2)
    
    def get_audit_log(self, limit: int = 20) -> List[Dict]:
        """
        Get recent audit log entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of audit log entries
        """
        audit_log_path = Path(self.AUDIT_LOG)
        
        if not audit_log_path.exists():
            return []
        
        with open(audit_log_path, 'r') as f:
            try:
                log = json.load(f)
                return log[-limit:]
            except json.JSONDecodeError:
                return []
    
    def check_security_alerts(self) -> List[Dict]:
        """
        Check for security alerts in audit log.
        
        Returns:
            List of security alert entries
        """
        log = self.get_audit_log(limit=100)
        return [
            entry for entry in log 
            if entry.get("event") == "security_alert"
        ]
    
    # ==================== Multi-Profile Management ====================
    
    @staticmethod
    def list_profiles() -> List[str]:
        """
        List all available authentication profiles.
        
        Returns:
            List of profile names
        """
        profiles = ["default"]
        
        # Find all .env.* files
        for file in Path(".").glob(".env.*"):
            profile = file.name.replace(".env.", "")
            if profile and profile != "example":
                profiles.append(profile)
        
        return profiles
    
    @staticmethod
    def create_profile(profile_name: str, client_id: str, client_secret: str) -> bool:
        """
        Create a new authentication profile.
        
        Args:
            profile_name: Name for the new profile
            client_id: Spotify Client ID
            client_secret: Spotify Client Secret
            
        Returns:
            True if created successfully
        """
        if profile_name == "default":
            env_file = ".env"
        else:
            env_file = f".env.{profile_name}"
        
        # Create .env file for profile
        with open(env_file, 'w') as f:
            f.write(f"""# Spotify API Credentials - Profile: {profile_name}
# Get these from: https://developer.spotify.com/dashboard/applications

SPOTIFY_CLIENT_ID={client_id}
SPOTIFY_CLIENT_SECRET={client_secret}
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback

# Token storage (auto-generated, don't edit manually)
SPOTIFY_ACCESS_TOKEN=
SPOTIFY_REFRESH_TOKEN=
SPOTIFY_TOKEN_EXPIRES_AT=
""")
        
        return True


# ==================== CLI Commands ====================

def revoke_access_cli():
    """CLI command to revoke access."""
    import sys
    
    profile = sys.argv[2] if len(sys.argv) > 2 else "default"
    security = SecurityManager(profile=profile)
    result = security.revoke_tokens()
    
    if result["success"]:
        print(f"✓ {result['message']}")
    else:
        print(f"✗ {result['message']}")
        sys.exit(1)


def audit_log_cli():
    """CLI command to view audit log."""
    import sys
    
    profile = sys.argv[2] if len(sys.argv) > 2 else "default"
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    
    security = SecurityManager(profile=profile)
    log = security.get_audit_log(limit=limit)
    
    print(f"\n{'='*60}")
    print(f"Security Audit Log (Last {len(log)} entries)")
    print(f"{'='*60}\n")
    
    for entry in log:
        print(f"[{entry['timestamp']}] {entry['event']}")
        print(f"  Data: {json.dumps(entry['data'], indent=4)}\n")


def security_alerts_cli():
    """CLI command to check security alerts."""
    security = SecurityManager()
    alerts = security.check_security_alerts()
    
    if not alerts:
        print("✓ No security alerts found")
    else:
        print(f"\n⚠️  {len(alerts)} Security Alert(s) Found:\n")
        for alert in alerts:
            print(f"[{alert['timestamp']}]")
            print(f"  Type: {alert['data'].get('type')}")
            print(f"  Severity: {alert['data'].get('severity')}")
            print(f"  Message: {alert['data'].get('message')}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m spotify_mcp.security revoke [profile]")
        print("  python -m spotify_mcp.security audit [profile] [limit]")
        print("  python -m spotify_mcp.security alerts")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "revoke":
        revoke_access_cli()
    elif command == "audit":
        audit_log_cli()
    elif command == "alerts":
        security_alerts_cli()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
