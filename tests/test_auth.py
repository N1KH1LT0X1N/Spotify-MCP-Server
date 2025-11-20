"""
Comprehensive tests for authentication module.
Tests token management, refresh logic, and SecurityManager integration.
"""

import os
import time
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spotify_mcp.auth import SpotifyAuthManager, get_spotify_client
from spotify_mcp.security import SecurityManager


# Mock SpotifyOAuth to prevent real API calls
@pytest.fixture(autouse=True)
def mock_spotify_oauth():
    """Mock SpotifyOAuth to prevent real API calls during tests."""
    with patch('spotify_mcp.auth.SpotifyOAuth') as mock_oauth:
        mock_instance = Mock()
        mock_instance.get_authorize_url.return_value = "http://mock.url"
        mock_instance.parse_response_code.return_value = "mock_code"
        mock_instance.get_access_token.return_value = {
            "access_token": "mock_access",
            "refresh_token": "mock_refresh",
            "expires_at": 9999999999
        }
        mock_instance.refresh_access_token.return_value = {
            "access_token": "new_mock_access",
            "refresh_token": "new_mock_refresh",
            "expires_at": 9999999999
        }
        mock_oauth.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("""
SPOTIFY_CLIENT_ID=test_client_id
SPOTIFY_CLIENT_SECRET=test_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
SPOTIFY_ACCESS_TOKEN=test_access_token
SPOTIFY_REFRESH_TOKEN=test_refresh_token
SPOTIFY_TOKEN_EXPIRES_AT=9999999999
""")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except:
        pass


@pytest.fixture
def mock_env(monkeypatch, temp_env_file):
    """Mock environment variables for testing."""
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
    monkeypatch.setenv("SPOTIFY_ACCESS_TOKEN", "test_access_token")
    monkeypatch.setenv("SPOTIFY_REFRESH_TOKEN", "test_refresh_token")
    monkeypatch.setenv("SPOTIFY_TOKEN_EXPIRES_AT", "9999999999")
    
    yield


class TestSpotifyAuthManager:
    """Test suite for SpotifyAuthManager."""
    
    def test_initialization(self, mock_env):
        """Test that auth manager initializes correctly."""
        auth = SpotifyAuthManager(verbose=True)
        
        assert auth.client_id == "test_client_id"
        assert auth.client_secret == "test_client_secret"
        assert auth.redirect_uri == "http://127.0.0.1:8888/callback"
        assert auth.verbose == True
        assert auth.profile == "default"
    
    def test_initialization_missing_credentials(self, monkeypatch):
        """Test that initialization fails without credentials."""
        monkeypatch.delenv("SPOTIFY_CLIENT_ID", raising=False)
        monkeypatch.delenv("SPOTIFY_CLIENT_SECRET", raising=False)
        
        with pytest.raises(ValueError, match="Missing Spotify credentials"):
            SpotifyAuthManager()
    
    def test_get_token_status_valid_token(self, mock_env):
        """Test token status with valid token."""
        auth = SpotifyAuthManager()
        status = auth.get_token_status()
        
        assert status["has_access_token"] == True
        assert status["has_refresh_token"] == True
        assert status["has_expiry"] == True
        assert status["is_expired"] == False
    
    def test_get_token_status_expired_token(self, monkeypatch):
        """Test token status with expired token."""
        expired_time = str(int(time.time()) - 3600)  # 1 hour ago
        monkeypatch.setenv("SPOTIFY_TOKEN_EXPIRES_AT", expired_time)
        monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
        monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
        
        auth = SpotifyAuthManager()
        status = auth.get_token_status()
        
        assert status["is_expired"] == True
        assert status["expires_in_seconds"] < 0
    
    def test_get_access_token_uses_cached(self, mock_env):
        """Test that cached token is used when valid."""
        auth = SpotifyAuthManager(verbose=True)
        
        with patch.object(auth, '_authenticate') as mock_auth:
            token = auth.get_access_token()
            
            # Should use cached token, not call authenticate
            mock_auth.assert_not_called()
            assert token == "test_access_token"
    
    def test_get_access_token_refreshes_expired(self, monkeypatch):
        """Test that expired token triggers refresh."""
        expired_time = str(int(time.time()) - 3600)
        monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
        monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
        monkeypatch.setenv("SPOTIFY_ACCESS_TOKEN", "old_token")
        monkeypatch.setenv("SPOTIFY_REFRESH_TOKEN", "refresh_token")
        monkeypatch.setenv("SPOTIFY_TOKEN_EXPIRES_AT", expired_time)
        
        auth = SpotifyAuthManager(verbose=True)
        
        # Mock the refresh call
        mock_token_info = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_at": int(time.time()) + 3600
        }
        
        with patch.object(auth.sp_oauth, 'refresh_access_token', return_value=mock_token_info):
            with patch.object(auth, '_save_token_info') as mock_save:
                token = auth.get_access_token()
                
                # Should refresh and save new token
                mock_save.assert_called_once()
                assert token == "new_access_token"
    
    def test_force_refresh_success(self, monkeypatch):
        """Test force refresh functionality."""
        monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
        monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
        monkeypatch.setenv("SPOTIFY_REFRESH_TOKEN", "refresh_token")
        
        auth = SpotifyAuthManager()
        
        mock_token_info = {
            "access_token": "refreshed_token",
            "refresh_token": "new_refresh_token",
            "expires_at": int(time.time()) + 3600
        }
        
        with patch.object(auth.sp_oauth, 'refresh_access_token', return_value=mock_token_info):
            with patch.object(auth, '_save_token_info'):
                result = auth.force_refresh()
                
                assert result == True
    
    def test_force_refresh_no_token(self, monkeypatch):
        """Test force refresh fails without refresh token."""
        monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
        monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
        monkeypatch.delenv("SPOTIFY_REFRESH_TOKEN", raising=False)
        
        auth = SpotifyAuthManager()
        result = auth.force_refresh()
        
        assert result == False
    
    def test_clear_tokens(self, temp_env_file, monkeypatch):
        """Test clearing tokens."""
        monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
        monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
        
        auth = SpotifyAuthManager()
        auth.env_file = temp_env_file
        
        with patch('spotify_mcp.auth.set_key') as mock_set_key:
            auth.clear_tokens()
            
            # Should clear all three token fields
            assert mock_set_key.call_count == 3


class TestSecurityManagerIntegration:
    """Test SecurityManager integration with auth."""
    
    def test_security_manager_initialization(self):
        """Test SecurityManager initializes correctly."""
        security = SecurityManager(profile="test")
        
        assert security.profile == "test"
        assert security.env_file == ".env.test"
    
    def test_save_tokens_to_env(self, temp_env_file):
        """Test saving tokens to .env file."""
        security = SecurityManager(profile="default")
        security.env_file = temp_env_file
        
        with patch('spotify_mcp.security.set_key') as mock_set_key:
            result = security.save_tokens(
                access_token="test_access",
                refresh_token="test_refresh",
                expires_at=9999999999,
                use_keychain=False
            )
            
            assert result == True
            assert mock_set_key.call_count == 3
    
    @patch('spotify_mcp.security.KEYRING_AVAILABLE', True)
    def test_save_tokens_to_keychain(self):
        """Test saving tokens to keychain when available."""
        security = SecurityManager(profile="default")
        
        with patch.object(security, 'save_to_keychain', return_value=True) as mock_save:
            result = security.save_tokens(
                access_token="test_access",
                refresh_token="test_refresh",
                expires_at=9999999999,
                use_keychain=True
            )
            
            assert result == True
            assert mock_save.call_count == 3
    
    def test_get_tokens_from_env(self, monkeypatch):
        """Test retrieving tokens from environment."""
        from unittest.mock import patch
        
        # Mock os.getenv to return our test values
        def mock_getenv(key, default=None):
            env_values = {
                "SPOTIFY_ACCESS_TOKEN": "env_access",
                "SPOTIFY_REFRESH_TOKEN": "env_refresh",
                "SPOTIFY_TOKEN_EXPIRES_AT": "9999999999"
            }
            return env_values.get(key, default)
        
        with patch('os.getenv', side_effect=mock_getenv):
            security = SecurityManager()
            tokens = security.get_tokens()
            
            assert tokens["access_token"] == "env_access"
            assert tokens["refresh_token"] == "env_refresh"
            assert tokens["expires_at"] == "9999999999"
    
    def test_revoke_tokens(self, temp_env_file):
        """Test token revocation."""
        security = SecurityManager()
        security.env_file = temp_env_file
        
        with patch('spotify_mcp.security.set_key') as mock_set_key:
            result = security.revoke_tokens()
            
            assert result["success"] == True
            assert "revoked" in result["message"].lower()
            assert mock_set_key.call_count == 3
    
    def test_track_token_rotation(self, temp_env_file):
        """Test token rotation tracking."""
        security = SecurityManager()
        
        with patch.object(security, '_log_audit') as mock_log:
            security.track_token_rotation(
                old_refresh_token="old_token_12345678",
                new_refresh_token="new_token_87654321"
            )
            
            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[0][0] == "token_rotation"
            assert "old_token_suffix" in call_args[0][1]
    
    def test_track_token_rotation_reuse_alert(self):
        """Test that token reuse triggers security alert."""
        security = SecurityManager()
        
        with patch.object(security, '_log_audit') as mock_log:
            # Same token = reuse
            security.track_token_rotation(
                old_refresh_token="same_token_12345678",
                new_refresh_token="same_token_12345678"
            )
            
            # Should log rotation + alert
            assert mock_log.call_count == 2
            alert_call = mock_log.call_args_list[1]
            assert alert_call[0][0] == "security_alert"
    
    def test_audit_logging(self, temp_env_file):
        """Test audit log functionality."""
        security = SecurityManager()
        
        # Create audit log
        security._log_audit("test_event", {"key": "value"})
        
        # Read it back
        log = security.get_audit_log(limit=10)
        
        assert len(log) > 0
        assert log[-1]["event"] == "test_event"
        assert log[-1]["data"]["key"] == "value"
    
    def test_security_alerts(self):
        """Test security alerts detection."""
        security = SecurityManager()
        
        # Create a security alert
        security._log_audit("security_alert", {
            "type": "test_alert",
            "severity": "high"
        })
        
        alerts = security.check_security_alerts()
        
        assert len(alerts) > 0
        assert alerts[-1]["event"] == "security_alert"
    
    def test_list_profiles(self):
        """Test listing available profiles."""
        profiles = SecurityManager.list_profiles()
        
        assert "default" in profiles
        assert isinstance(profiles, list)
    
    def test_create_profile(self, tmp_path):
        """Test creating a new profile."""
        os.chdir(tmp_path)
        
        result = SecurityManager.create_profile(
            profile_name="test_profile",
            client_id="test_id",
            client_secret="test_secret"
        )
        
        assert result == True
        assert Path(".env.test_profile").exists()


class TestAuthWithSecurity:
    """Test auth manager with security features enabled."""
    
    @patch('spotify_mcp.auth.SECURITY_AVAILABLE', True)
    def test_auth_with_security_enabled(self, monkeypatch):
        """Test auth manager with security features."""
        monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
        monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
        
        with patch('spotify_mcp.auth.SecurityManager') as mock_security:
            auth = SpotifyAuthManager(use_security=True)
            
            assert auth.use_security == True
            assert auth.security is not None
    
    @patch('spotify_mcp.auth.SECURITY_AVAILABLE', True)
    def test_save_with_security_manager(self, monkeypatch):
        """Test saving tokens through SecurityManager."""
        monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
        monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
        
        auth = SpotifyAuthManager(use_security=True)
        
        mock_security = Mock()
        auth.security = mock_security
        
        token_info = {
            "access_token": "test_access",
            "refresh_token": "test_refresh",
            "expires_at": 9999999999
        }
        
        auth._save_token_info(token_info)
        
        # Should call security manager's save_tokens
        mock_security.save_tokens.assert_called_once()


class TestGetSpotifyClient:
    """Test the convenience function for getting authenticated client."""
    
    def test_get_spotify_client(self, monkeypatch):
        """Test getting authenticated Spotify client."""
        monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
        monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
        monkeypatch.setenv("SPOTIFY_ACCESS_TOKEN", "test_token")
        monkeypatch.setenv("SPOTIFY_REFRESH_TOKEN", "refresh")
        monkeypatch.setenv("SPOTIFY_TOKEN_EXPIRES_AT", "9999999999")
        
        with patch('spotify_mcp.auth.spotipy.Spotify') as mock_spotify:
            client = get_spotify_client(verbose=True)
            
            # Should create Spotify client with token
            mock_spotify.assert_called_once()


# Integration tests
class TestEndToEndFlow:
    """Test complete authentication flows."""
    
    def test_full_token_refresh_cycle(self, monkeypatch):
        """Test complete token refresh cycle."""
        # Setup expired token
        expired_time = str(int(time.time()) - 3600)
        monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
        monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
        monkeypatch.setenv("SPOTIFY_ACCESS_TOKEN", "old_token")
        monkeypatch.setenv("SPOTIFY_REFRESH_TOKEN", "refresh_token")
        monkeypatch.setenv("SPOTIFY_TOKEN_EXPIRES_AT", expired_time)
        
        auth = SpotifyAuthManager(verbose=True, use_security=True)
        
        # Mock both the OAuth refresh and security tracking
        mock_token_info = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_at": int(time.time()) + 3600
        }
        
        with patch.object(auth.sp_oauth, 'refresh_access_token', return_value=mock_token_info):
            with patch.object(auth, '_save_token_info'):
                if auth.use_security and auth.security:
                    with patch.object(auth.security, 'track_token_rotation'):
                        token = auth.get_access_token()
                else:
                    token = auth.get_access_token()
                
                assert token == "new_access_token"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
