"""
Integration tests for auth + security modules.
Tests end-to-end flows with SecurityManager enabled.
"""

import os
import time
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spotify_mcp.auth import SpotifyAuthManager
from spotify_mcp.security import SecurityManager


@pytest.fixture
def temp_env_setup(tmp_path, monkeypatch):
    """Set up temporary environment for integration tests."""
    os.chdir(tmp_path)
    
    # Create .env file
    env_file = tmp_path / ".env"
    env_file.write_text("""
SPOTIFY_CLIENT_ID=test_client_id
SPOTIFY_CLIENT_SECRET=test_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
SPOTIFY_ACCESS_TOKEN=
SPOTIFY_REFRESH_TOKEN=
SPOTIFY_TOKEN_EXPIRES_AT=
""")
    
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_client_secret")
    
    yield tmp_path


class TestAuthSecurityIntegration:
    """Test auth and security working together."""
    
    @patch('spotify_mcp.auth.SECURITY_AVAILABLE', True)
    def test_auth_with_security_save_tokens(self, temp_env_setup, monkeypatch):
        """Test auth saves tokens through SecurityManager."""
        monkeypatch.setenv("SPOTIFY_REFRESH_TOKEN", "test_refresh")
        monkeypatch.setenv("SPOTIFY_USE_KEYCHAIN", "true")  # Set keychain env var
        
        auth = SpotifyAuthManager(use_security=True, verbose=True)
        
        # Mock security manager
        mock_security = Mock(spec=SecurityManager)
        auth.security = mock_security
        
        token_info = {
            "access_token": "new_access",
            "refresh_token": "new_refresh",
            "expires_at": int(time.time()) + 3600
        }
        
        auth._save_token_info(token_info)
        
        # Verify security manager was called (use_keychain=True because env var is set)
        mock_security.save_tokens.assert_called_once_with(
            access_token="new_access",
            refresh_token="new_refresh",
            expires_at=token_info["expires_at"],
            use_keychain=True
        )
    
    @patch('spotify_mcp.auth.SECURITY_AVAILABLE', True)
    def test_token_rotation_tracked(self, temp_env_setup, monkeypatch):
        """Test that token rotation is tracked by SecurityManager."""
        # Set up expired token
        expired_time = str(int(time.time()) - 3600)
        monkeypatch.setenv("SPOTIFY_ACCESS_TOKEN", "old_access")
        monkeypatch.setenv("SPOTIFY_REFRESH_TOKEN", "old_refresh_12345678")
        monkeypatch.setenv("SPOTIFY_TOKEN_EXPIRES_AT", expired_time)
        
        auth = SpotifyAuthManager(use_security=True, verbose=True)
        
        # Mock security manager
        mock_security = Mock(spec=SecurityManager)
        auth.security = mock_security
        
        # Mock OAuth refresh
        new_token_info = {
            "access_token": "new_access",
            "refresh_token": "new_refresh_87654321",
            "expires_at": int(time.time()) + 3600
        }
        
        with patch.object(auth.sp_oauth, 'refresh_access_token', return_value=new_token_info):
            token = auth.get_access_token()
            
            # Verify rotation was tracked
            mock_security.track_token_rotation.assert_called_once()
            call_args = mock_security.track_token_rotation.call_args
            assert call_args[0][0] == "old_refresh_12345678"
            assert call_args[0][1] == "new_refresh_87654321"
    
    def test_security_manager_audit_log(self, temp_env_setup):
        """Test that security operations are logged."""
        security = SecurityManager(profile="test")
        
        # Save tokens
        security.save_tokens(
            access_token="test_access",
            refresh_token="test_refresh",
            expires_at=int(time.time()) + 3600,
            use_keychain=False
        )
        
        # Check audit log
        log = security.get_audit_log(limit=10)
        
        assert len(log) > 0
        assert any(entry["event"] == "tokens_saved" for entry in log)
    
    def test_token_revocation_flow(self, temp_env_setup):
        """Test complete token revocation flow."""
        security = SecurityManager(profile="test")
        
        # Save tokens first
        security.save_tokens(
            access_token="test_access",
            refresh_token="test_refresh",
            expires_at=int(time.time()) + 3600,
            use_keychain=False
        )
        
        # Revoke tokens
        result = security.revoke_tokens()
        
        assert result["success"] == True
        
        # Check audit log
        log = security.get_audit_log(limit=10)
        assert any(entry["event"] == "tokens_revoked" for entry in log)
    
    def test_multi_profile_support(self, temp_env_setup):
        """Test using multiple profiles."""
        # Create profiles
        SecurityManager.create_profile("prod", "prod_id", "prod_secret")
        SecurityManager.create_profile("dev", "dev_id", "dev_secret")
        
        # List profiles
        profiles = SecurityManager.list_profiles()
        
        assert "default" in profiles
        assert "prod" in profiles
        assert "dev" in profiles
        
        # Check files exist
        assert Path(".env.prod").exists()
        assert Path(".env.dev").exists()
    
    @patch('spotify_mcp.security.KEYRING_AVAILABLE', True)
    @patch('spotify_mcp.security.keyring')
    def test_keychain_integration(self, mock_keyring, temp_env_setup, monkeypatch):
        """Test keychain integration end-to-end."""
        # Configure mock keyring
        mock_keyring.set_password = Mock()
        mock_keyring.get_password = Mock(return_value="stored_value")
        
        monkeypatch.setenv("SPOTIFY_USE_KEYCHAIN", "true")
        
        security = SecurityManager()
        
        # Save to keychain
        result = security.save_tokens(
            access_token="test_access",
            refresh_token="test_refresh",
            expires_at=int(time.time()) + 3600,
            use_keychain=True
        )
        
        assert result == True
        assert mock_keyring.set_password.call_count == 3
        
        # Retrieve from keychain
        tokens = security.get_tokens()
        
        assert tokens["access_token"] == "stored_value"


class TestErrorHandling:
    """Test error handling in integration scenarios."""
    
    def test_auth_handles_refresh_failure_gracefully(self, temp_env_setup, monkeypatch):
        """Test that auth handles refresh failures gracefully."""
        expired_time = str(int(time.time()) - 3600)
        monkeypatch.setenv("SPOTIFY_ACCESS_TOKEN", "old_token")
        monkeypatch.setenv("SPOTIFY_REFRESH_TOKEN", "invalid_refresh")
        monkeypatch.setenv("SPOTIFY_TOKEN_EXPIRES_AT", expired_time)
        
        auth = SpotifyAuthManager(verbose=True)
        
        # Mock failed refresh
        with patch.object(auth.sp_oauth, 'refresh_access_token', side_effect=Exception("Invalid token")):
            with patch.object(auth, '_authenticate', return_value="new_token"):
                # Should fall back to re-authentication
                token = auth.get_access_token()
                assert token == "new_token"
    
    def test_security_manager_handles_corrupted_audit_log(self, temp_env_setup):
        """Test handling of corrupted audit log."""
        security = SecurityManager()
        
        # Create corrupted audit log
        with open(security.AUDIT_LOG, 'w') as f:
            f.write("not valid json{")
        
        # Should handle gracefully
        log = security.get_audit_log()
        assert log == []
        
        # Should still be able to add new entries
        security._log_audit("test_event", {"data": "value"})
        
        new_log = security.get_audit_log()
        assert len(new_log) == 1


class TestSecurityFeatures:
    """Test security-specific features."""
    
    def test_token_reuse_detection(self, temp_env_setup):
        """Test detection of refresh token reuse."""
        security = SecurityManager()
        
        same_token = "same_token_12345678"
        
        # Track rotation with same token
        security.track_token_rotation(same_token, same_token)
        
        # Check for security alert
        alerts = security.check_security_alerts()
        
        assert len(alerts) > 0
        assert alerts[-1]["data"]["type"] == "token_reuse_detected"
    
    def test_audit_log_rotation(self, temp_env_setup):
        """Test that audit log keeps only recent entries."""
        security = SecurityManager()
        
        # Add 150 entries
        for i in range(150):
            security._log_audit(f"event_{i}", {"index": i})
        
        # Check that only last 100 are kept
        log = security.get_audit_log(limit=200)
        
        assert len(log) == 100
        assert log[0]["data"]["index"] == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
