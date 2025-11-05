"""
Comprehensive tests for SecurityManager.
Tests keychain integration, audit logging, and profile management.
"""

import os
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spotify_mcp.security import SecurityManager, KEYRING_AVAILABLE


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield Path(tmpdir)
        os.chdir(old_cwd)


@pytest.fixture
def security_manager(temp_dir):
    """Create SecurityManager instance for testing."""
    return SecurityManager(profile="test")


class TestSecurityManagerInit:
    """Test SecurityManager initialization."""
    
    def test_default_profile(self, temp_dir):
        """Test initialization with default profile."""
        sm = SecurityManager()
        
        assert sm.profile == "default"
        assert sm.env_file == ".env"
    
    def test_custom_profile(self, temp_dir):
        """Test initialization with custom profile."""
        sm = SecurityManager(profile="production")
        
        assert sm.profile == "production"
        assert sm.env_file == ".env.production"


class TestKeychainIntegration:
    """Test system keychain integration."""
    
    def test_use_keychain_availability(self, security_manager):
        """Test checking keychain availability."""
        result = security_manager.use_keychain()
        
        # Should return same as KEYRING_AVAILABLE
        assert result == KEYRING_AVAILABLE
    
    @patch('spotify_mcp.security.KEYRING_AVAILABLE', True)
    def test_save_to_keychain_success(self, temp_dir):
        """Test successful save to keychain."""
        # Import and patch keyring before creating SecurityManager
        with patch('spotify_mcp.security.keyring') as mock_keyring:
            mock_keyring.set_password = Mock()
            
            security_manager = SecurityManager(profile="test")
            result = security_manager.save_to_keychain("test_key", "test_value")
            
            assert result == True
            mock_keyring.set_password.assert_called_once()
    
    @patch('spotify_mcp.security.KEYRING_AVAILABLE', False)
    def test_save_to_keychain_unavailable(self, security_manager):
        """Test save to keychain when unavailable."""
        result = security_manager.save_to_keychain("test_key", "test_value")
        
        assert result == False
    
    @patch('spotify_mcp.security.KEYRING_AVAILABLE', True)
    def test_save_to_keychain_failure(self, temp_dir):
        """Test keychain save failure handling."""
        with patch('spotify_mcp.security.keyring') as mock_keyring:
            mock_keyring.set_password = Mock(side_effect=Exception("Keychain error"))
            
            security_manager = SecurityManager(profile="test")
            result = security_manager.save_to_keychain("test_key", "test_value")
            
            assert result == False
    
    @patch('spotify_mcp.security.KEYRING_AVAILABLE', True)
    def test_get_from_keychain_success(self, temp_dir):
        """Test successful retrieval from keychain."""
        with patch('spotify_mcp.security.keyring') as mock_keyring:
            mock_keyring.get_password = Mock(return_value="stored_value")
            
            security_manager = SecurityManager(profile="test")
            result = security_manager.get_from_keychain("test_key")
            
            assert result == "stored_value"
            mock_keyring.get_password.assert_called_once()
    
    @patch('spotify_mcp.security.KEYRING_AVAILABLE', False)
    def test_get_from_keychain_unavailable(self, security_manager):
        """Test get from keychain when unavailable."""
        result = security_manager.get_from_keychain("test_key")
        
        assert result is None
    
    @patch('spotify_mcp.security.KEYRING_AVAILABLE', True)
    def test_clear_keychain_success(self, temp_dir):
        """Test clearing keychain."""
        with patch('spotify_mcp.security.keyring') as mock_keyring:
            mock_keyring.delete_password = Mock()
            
            security_manager = SecurityManager(profile="test")
            result = security_manager.clear_keychain()
            
            assert result == True
            # Should delete 5 keys
            assert mock_keyring.delete_password.call_count == 5


class TestTokenManagement:
    """Test token save/get/revoke operations."""
    
    def test_save_tokens_to_env(self, temp_dir):
        """Test saving tokens to .env file."""
        sm = SecurityManager()
        
        with patch('spotify_mcp.security.set_key') as mock_set_key:
            result = sm.save_tokens(
                access_token="access_123",
                refresh_token="refresh_456",
                expires_at=9999999999,
                use_keychain=False
            )
            
            assert result == True
            assert mock_set_key.call_count == 3
    
    @patch('spotify_mcp.security.KEYRING_AVAILABLE', True)
    def test_save_tokens_to_keychain(self, temp_dir):
        """Test saving tokens to keychain."""
        sm = SecurityManager()
        
        with patch.object(sm, 'save_to_keychain', return_value=True) as mock_save:
            with patch('spotify_mcp.security.set_key') as mock_set_key:
                result = sm.save_tokens(
                    access_token="access_123",
                    refresh_token="refresh_456",
                    expires_at=9999999999,
                    use_keychain=True
                )
                
                assert result == True
                # Should save 3 items to keychain
                assert mock_save.call_count == 3
                # Should set keychain marker in .env
                mock_set_key.assert_called_once_with(sm.env_file, "SPOTIFY_USE_KEYCHAIN", "true")
    
    def test_get_tokens_from_env(self, temp_dir, monkeypatch):
        """Test getting tokens from environment."""
        monkeypatch.setenv("SPOTIFY_ACCESS_TOKEN", "env_access")
        monkeypatch.setenv("SPOTIFY_REFRESH_TOKEN", "env_refresh")
        monkeypatch.setenv("SPOTIFY_TOKEN_EXPIRES_AT", "9999999999")
        monkeypatch.setenv("SPOTIFY_USE_KEYCHAIN", "false")
        
        sm = SecurityManager()
        tokens = sm.get_tokens()
        
        assert tokens["access_token"] == "env_access"
        assert tokens["refresh_token"] == "env_refresh"
        assert tokens["expires_at"] == "9999999999"
    
    @patch('spotify_mcp.security.KEYRING_AVAILABLE', True)
    def test_get_tokens_from_keychain(self, temp_dir, monkeypatch):
        """Test getting tokens from keychain."""
        monkeypatch.setenv("SPOTIFY_USE_KEYCHAIN", "true")
        
        sm = SecurityManager()
        
        with patch.object(sm, 'get_from_keychain') as mock_get:
            mock_get.side_effect = lambda key: f"keychain_{key}"
            
            tokens = sm.get_tokens()
            
            assert tokens["access_token"] == "keychain_access_token"
            assert tokens["refresh_token"] == "keychain_refresh_token"
            assert tokens["expires_at"] == "keychain_token_expires_at"
    
    def test_revoke_tokens(self, temp_dir):
        """Test token revocation."""
        sm = SecurityManager()
        
        with patch('spotify_mcp.security.set_key') as mock_set_key:
            result = sm.revoke_tokens()
            
            assert result["success"] == True
            assert "revoked" in result["message"].lower()
            # Should clear 3 token fields
            assert mock_set_key.call_count == 3
    
    def test_revoke_tokens_with_keychain(self, temp_dir, monkeypatch):
        """Test token revocation with keychain."""
        monkeypatch.setenv("SPOTIFY_USE_KEYCHAIN", "true")
        sm = SecurityManager()
        
        with patch('spotify_mcp.security.set_key') as mock_set_key:
            with patch.object(sm, 'clear_keychain', return_value=True) as mock_clear:
                result = sm.revoke_tokens()
                
                assert result["success"] == True
                mock_clear.assert_called_once()
    
    def test_revoke_tokens_error_handling(self, temp_dir):
        """Test error handling during revocation."""
        sm = SecurityManager()
        
        with patch('spotify_mcp.security.set_key', side_effect=Exception("Write error")):
            result = sm.revoke_tokens()
            
            assert result["success"] == False
            assert "Failed" in result["message"]


class TestTokenRotation:
    """Test token rotation tracking."""
    
    def test_track_token_rotation(self, security_manager):
        """Test normal token rotation tracking."""
        with patch.object(security_manager, '_log_audit') as mock_log:
            security_manager.track_token_rotation(
                old_refresh_token="old_token_abcd1234",
                new_refresh_token="new_token_wxyz9876"
            )
            
            mock_log.assert_called_once()
            call_args = mock_log.call_args[0]
            
            assert call_args[0] == "token_rotation"
            assert call_args[1]["old_token_suffix"] == "abcd1234"
            assert call_args[1]["new_token_suffix"] == "wxyz9876"
    
    def test_track_token_rotation_no_old_token(self, security_manager):
        """Test rotation tracking with no previous token."""
        with patch.object(security_manager, '_log_audit') as mock_log:
            security_manager.track_token_rotation(
                old_refresh_token=None,
                new_refresh_token="new_token_wxyz9876"
            )
            
            call_args = mock_log.call_args[0]
            assert call_args[1]["old_token_suffix"] == "none"
    
    def test_track_token_reuse_alert(self, security_manager):
        """Test security alert on token reuse."""
        with patch.object(security_manager, '_log_audit') as mock_log:
            same_token = "same_token_12345678"
            security_manager.track_token_rotation(
                old_refresh_token=same_token,
                new_refresh_token=same_token
            )
            
            # Should log rotation + security alert
            assert mock_log.call_count == 2
            
            # Check alert
            alert_call = mock_log.call_args_list[1]
            assert alert_call[0][0] == "security_alert"
            assert alert_call[0][1]["type"] == "token_reuse_detected"
            assert alert_call[0][1]["severity"] == "warning"


class TestAuditLogging:
    """Test audit logging functionality."""
    
    def test_log_audit(self, temp_dir, security_manager):
        """Test logging an audit event."""
        security_manager._log_audit("test_event", {"key": "value"})
        
        # Check file was created
        audit_path = Path(security_manager.AUDIT_LOG)
        assert audit_path.exists()
        
        # Check content
        with open(audit_path, 'r') as f:
            log = json.load(f)
        
        assert len(log) == 1
        assert log[0]["event"] == "test_event"
        assert log[0]["data"]["key"] == "value"
        assert "timestamp" in log[0]
    
    def test_log_audit_multiple_entries(self, temp_dir, security_manager):
        """Test multiple audit entries."""
        for i in range(5):
            security_manager._log_audit(f"event_{i}", {"index": i})
        
        log = security_manager.get_audit_log(limit=10)
        
        assert len(log) == 5
        assert log[-1]["event"] == "event_4"
    
    def test_log_audit_max_entries(self, temp_dir, security_manager):
        """Test audit log keeps only last 100 entries."""
        # Add 150 entries
        for i in range(150):
            security_manager._log_audit(f"event_{i}", {"index": i})
        
        # Check file
        with open(security_manager.AUDIT_LOG, 'r') as f:
            log = json.load(f)
        
        # Should keep only last 100
        assert len(log) == 100
        assert log[0]["data"]["index"] == 50  # First entry is #50
        assert log[-1]["data"]["index"] == 149  # Last entry is #149
    
    def test_get_audit_log_with_limit(self, temp_dir, security_manager):
        """Test getting audit log with limit."""
        for i in range(20):
            security_manager._log_audit(f"event_{i}", {"index": i})
        
        log = security_manager.get_audit_log(limit=5)
        
        assert len(log) == 5
        assert log[-1]["event"] == "event_19"
    
    def test_get_audit_log_empty(self, temp_dir, security_manager):
        """Test getting audit log when empty."""
        log = security_manager.get_audit_log()
        
        assert log == []
    
    def test_get_audit_log_corrupted_file(self, temp_dir, security_manager):
        """Test handling corrupted audit log."""
        # Create corrupted file
        with open(security_manager.AUDIT_LOG, 'w') as f:
            f.write("corrupted json{")
        
        log = security_manager.get_audit_log()
        
        assert log == []


class TestSecurityAlerts:
    """Test security alert detection."""
    
    def test_check_security_alerts_empty(self, temp_dir, security_manager):
        """Test checking alerts when none exist."""
        alerts = security_manager.check_security_alerts()
        
        assert alerts == []
    
    def test_check_security_alerts_found(self, temp_dir, security_manager):
        """Test finding security alerts."""
        # Add some regular events
        security_manager._log_audit("tokens_saved", {"test": "data"})
        security_manager._log_audit("keychain_access", {"test": "data"})
        
        # Add security alerts
        security_manager._log_audit("security_alert", {
            "type": "test_alert",
            "severity": "high"
        })
        security_manager._log_audit("security_alert", {
            "type": "another_alert",
            "severity": "medium"
        })
        
        alerts = security_manager.check_security_alerts()
        
        assert len(alerts) == 2
        assert alerts[0]["event"] == "security_alert"
        assert alerts[1]["event"] == "security_alert"


class TestProfileManagement:
    """Test multi-profile management."""
    
    def test_list_profiles_default_only(self, temp_dir):
        """Test listing profiles with only default."""
        profiles = SecurityManager.list_profiles()
        
        assert "default" in profiles
        assert isinstance(profiles, list)
    
    def test_list_profiles_multiple(self, temp_dir):
        """Test listing multiple profiles."""
        # Create some profile files
        Path(".env.production").touch()
        Path(".env.staging").touch()
        Path(".env.example").touch()  # Should be ignored
        
        profiles = SecurityManager.list_profiles()
        
        assert "default" in profiles
        assert "production" in profiles
        assert "staging" in profiles
        assert "example" not in profiles
    
    def test_create_profile_default(self, temp_dir):
        """Test creating default profile."""
        result = SecurityManager.create_profile(
            profile_name="default",
            client_id="test_id",
            client_secret="test_secret"
        )
        
        assert result == True
        assert Path(".env").exists()
        
        # Check content
        with open(".env", 'r') as f:
            content = f.read()
        
        assert "test_id" in content
        assert "test_secret" in content
    
    def test_create_profile_custom(self, temp_dir):
        """Test creating custom profile."""
        result = SecurityManager.create_profile(
            profile_name="production",
            client_id="prod_id",
            client_secret="prod_secret"
        )
        
        assert result == True
        assert Path(".env.production").exists()
        
        # Check content
        with open(".env.production", 'r') as f:
            content = f.read()
        
        assert "prod_id" in content
        assert "prod_secret" in content
        assert "Profile: production" in content


class TestCLICommands:
    """Test CLI command functions."""
    
    def test_revoke_access_cli_success(self, temp_dir):
        """Test revoke CLI command."""
        from spotify_mcp.security import revoke_access_cli
        
        with patch('sys.argv', ['security.py', 'revoke', 'test']):
            with patch('spotify_mcp.security.SecurityManager') as mock_sm:
                mock_instance = Mock()
                mock_instance.revoke_tokens.return_value = {
                    "success": True,
                    "message": "Revoked successfully"
                }
                mock_sm.return_value = mock_instance
                
                revoke_access_cli()
                
                mock_sm.assert_called_once_with(profile="test")
    
    def test_audit_log_cli(self, temp_dir, capsys):
        """Test audit log CLI command."""
        from spotify_mcp.security import audit_log_cli
        
        sm = SecurityManager()
        sm._log_audit("test_event", {"key": "value"})
        
        with patch('sys.argv', ['security.py', 'audit']):
            audit_log_cli()
        
        captured = capsys.readouterr()
        assert "Security Audit Log" in captured.out
        assert "test_event" in captured.out
    
    def test_security_alerts_cli_empty(self, temp_dir, capsys):
        """Test security alerts CLI with no alerts."""
        from spotify_mcp.security import security_alerts_cli
        
        with patch('sys.argv', ['security.py', 'alerts']):
            security_alerts_cli()
        
        captured = capsys.readouterr()
        assert "No security alerts" in captured.out
    
    def test_security_alerts_cli_found(self, temp_dir, capsys):
        """Test security alerts CLI with alerts."""
        from spotify_mcp.security import security_alerts_cli
        
        sm = SecurityManager()
        sm._log_audit("security_alert", {
            "type": "test_alert",
            "severity": "high",
            "message": "Test alert message"
        })
        
        with patch('sys.argv', ['security.py', 'alerts']):
            security_alerts_cli()
        
        captured = capsys.readouterr()
        assert "Security Alert" in captured.out
        assert "test_alert" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
