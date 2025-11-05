# Enterprise Security Features

This document describes the enterprise-grade security features available in the Spotify MCP Server.

## 🎯 Overview

The security module provides:
- ✅ **System Keychain Integration** - Store tokens in OS-level secure storage
- ✅ **Token Revocation** - Explicitly revoke access
- ✅ **Multi-Profile Support** - Multiple Spotify accounts/environments
- ✅ **Token Rotation Tracking** - Monitor refresh token rotation
- ✅ **Security Audit Log** - Track all authentication events

## 📦 Installation

### Basic (Default)
No additional dependencies required. Uses `.env` file storage.

### Enterprise Features
Install optional dependencies for full feature set:

```bash
pip install keyring
```

## 🔐 Feature 1: System Keychain Integration

Store tokens in your OS-level secure storage instead of plain text `.env` files.

### Supported Platforms
- **Windows**: Windows Credential Manager
- **macOS**: Keychain Access
- **Linux**: Secret Service (gnome-keyring, kwallet)

### Enable Keychain Storage

```bash
# Enable for default profile
python enterprise_cli.py enable-keychain

# Enable for specific profile
python enterprise_cli.py enable-keychain work
```

### How It Works

```
┌─────────────────────────────────────────────────────────┐
│ Without Keychain (Default)                              │
│ Tokens stored in: .env (plain text file)               │
│ Security: ⚠️  File-level permissions only               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ With Keychain (Enterprise)                              │
│ Tokens stored in: OS Keychain (encrypted)              │
│ Security: ✅ OS-level encryption + authentication       │
└─────────────────────────────────────────────────────────┘
```

### Migrate to Keychain

```bash
# 1. Enable keychain
python enterprise_cli.py enable-keychain

# 2. Re-authenticate (tokens will be saved to keychain)
python test_auth.py

# 3. Verify (.env will only have marker, not actual tokens)
cat .env  # Shows SPOTIFY_USE_KEYCHAIN=true
```

## 🚫 Feature 2: Token Revocation

Explicitly revoke Spotify access and clear all tokens.

### Revoke Access

```bash
# Revoke default profile
python enterprise_cli.py revoke

# Revoke specific profile
python enterprise_cli.py revoke work
```

### What Gets Cleared
- ✅ Access token (from .env or keychain)
- ✅ Refresh token (from .env or keychain)
- ✅ Token expiration timestamp
- ✅ Audit log entry created

### When to Use
- **Security Incident**: Suspected credential exposure
- **Employee Offboarding**: Remove access for departed team members
- **Credential Rotation**: Force re-authentication with new credentials
- **Testing**: Clean slate for auth testing

## 👥 Feature 3: Multi-Profile Support

Manage multiple Spotify accounts or environments (dev/staging/prod).

### List Profiles

```bash
python enterprise_cli.py profiles
```

Output:
```
======================================================================
Available Authentication Profiles
======================================================================

  • default              ✓ Active         (.env)
  • work                 ✓ Active         (.env.work)
  • personal             ✗ Not configured (.env.personal)

======================================================================
Total profiles: 3
```

### Create New Profile

```bash
python enterprise_cli.py create-profile work
```

This creates `.env.work` with separate credentials.

### Use Profile

**In Python code:**
```python
from spotify_mcp.auth import SpotifyAuthManager

# Use specific profile
auth = SpotifyAuthManager(profile="work")
```

**With server:**
```bash
# Start server with profile
python -m spotify_mcp.server --profile work
```

**In Claude Desktop config:**
```json
{
  "mcpServers": {
    "spotify-work": {
      "command": "python",
      "args": [
        "-m", "spotify_mcp.server",
        "--profile", "work"
      ]
    }
  }
}
```

### Profile File Structure

```
project/
├── .env              # default profile
├── .env.work         # work profile
├── .env.personal     # personal profile
└── .env.staging      # staging profile
```

## 🔄 Feature 4: Token Rotation Tracking

Automatically track when refresh tokens are rotated (security monitoring).

### How It Works

Every time your access token is refreshed:
```python
# Automatic tracking in background
old_token: "AQA...abc"  # Last 8 chars logged
new_token: "AQA...xyz"  # Last 8 chars logged

# Audit log entry created:
{
  "event": "token_rotation",
  "old_token_suffix": "...abc",
  "new_token_suffix": "...xyz",
  "timestamp": "2025-11-05T10:30:00"
}
```

### Security Alert: Token Reuse Detected

If Spotify doesn't rotate the refresh token (rare), an alert is logged:

```json
{
  "event": "security_alert",
  "type": "token_reuse_detected",
  "severity": "warning",
  "message": "Refresh token was not rotated during renewal"
}
```

### View Rotation History

```bash
# View audit log for rotation events
python enterprise_cli.py audit default 50 | grep token_rotation
```

## 📊 Feature 5: Security Audit Log

All authentication events are logged for security monitoring.

### View Audit Log

```bash
# Last 20 events (default)
python enterprise_cli.py audit

# Last 50 events for specific profile
python enterprise_cli.py audit work 50
```

### Logged Events

| Event | Description |
|-------|-------------|
| `tokens_saved` | Tokens saved to storage |
| `token_rotation` | Refresh token was rotated |
| `tokens_revoked` | Access was explicitly revoked |
| `keychain_save` | Token saved to OS keychain |
| `keychain_access` | Token retrieved from keychain |
| `security_alert` | Security issue detected |

### Example Output

```
======================================================================
Security Audit Log - Profile: default (Last 5 entries)
======================================================================

┌─ [2025-11-05T10:30:15]
│  Event: token_rotation
│    profile: default
│    old_token_suffix: ...Qwerty
│    new_token_suffix: ...Asdfgh
│    timestamp: 1730802615
└─

┌─ [2025-11-05T10:30:16]
│  Event: tokens_saved
│    storage: keychain
│    profile: default
│    expires_at: 1730806215
└─
```

### Check Security Alerts

```bash
python enterprise_cli.py alerts
```

Output if alerts found:
```
⚠️  2 Security Alert(s) Found:

======================================================================

[2025-11-05T08:15:22]
  Type: token_reuse_detected
  Severity: WARNING
  Profile: default
  Message: Refresh token was not rotated during renewal

[2025-11-05T09:30:45]
  Type: suspicious_access_pattern
  Severity: INFO
  Profile: work
  Message: Multiple rapid token refreshes detected

======================================================================
```

## 🎯 Usage Examples

### Example 1: Personal + Work Accounts

```bash
# Setup
python enterprise_cli.py create-profile personal
python enterprise_cli.py create-profile work

# Authenticate both
PROFILE=personal python test_auth.py
PROFILE=work python test_auth.py

# Use in code
from spotify_mcp.auth import SpotifyAuthManager

personal = SpotifyAuthManager(profile="personal")
work = SpotifyAuthManager(profile="work")
```

### Example 2: Maximum Security Setup

```bash
# 1. Install keyring
pip install keyring

# 2. Enable keychain storage
python enterprise_cli.py enable-keychain

# 3. Enable security features in code
from spotify_mcp.auth import SpotifyAuthManager

auth = SpotifyAuthManager(
    profile="default",
    use_security=True  # Enables all enterprise features
)
```

### Example 3: Monitoring & Alerts

```bash
# Check for security issues daily
python enterprise_cli.py alerts

# Review recent activity
python enterprise_cli.py audit default 100

# Automated monitoring (cron/scheduled task)
0 9 * * * cd /path/to/spotify_mcp && python enterprise_cli.py alerts
```

### Example 4: Credential Rotation

```bash
# 1. Revoke old access
python enterprise_cli.py revoke

# 2. Update credentials in .env
# (Edit SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)

# 3. Re-authenticate
python test_auth.py

# 4. Verify in audit log
python enterprise_cli.py audit
```

## 🔧 Configuration

### Environment Variables

```bash
# Enable keychain storage
SPOTIFY_USE_KEYCHAIN=true

# Client credentials (per profile)
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

### Audit Log Location

- **File**: `.auth_audit.json` (in project root)
- **Format**: JSON array of events
- **Retention**: Last 100 events automatically
- **Permissions**: Same as `.env` file

## 🔒 Security Best Practices

### ✅ Recommended

1. **Use keychain storage** for production deployments
2. **Enable security features** with `use_security=True`
3. **Monitor audit logs** regularly for suspicious activity
4. **Rotate credentials** if exposure suspected
5. **Use separate profiles** for different environments
6. **Review security alerts** daily

### ⚠️ Important

- Audit log (`.auth_audit.json`) contains metadata only, not actual tokens
- Always add `.auth_audit.json` to `.gitignore`
- Never commit `.env` or `.env.*` files
- Keychain storage requires OS authentication

### 🚫 Don't

- Don't disable security features in production
- Don't share `.env` files between profiles
- Don't ignore security alerts
- Don't store credentials in version control

## 🆚 Comparison: Basic vs Enterprise

| Feature | Basic | Enterprise |
|---------|-------|------------|
| Token Storage | `.env` file | OS Keychain |
| Encryption | ❌ None | ✅ OS-level |
| Multi-Profile | ❌ No | ✅ Yes |
| Audit Logging | ❌ No | ✅ Yes |
| Token Rotation Tracking | ❌ No | ✅ Yes |
| Security Alerts | ❌ No | ✅ Yes |
| Revocation Command | ❌ Manual | ✅ Automated |
| Dependencies | spotipy only | spotipy + keyring |

## 🐛 Troubleshooting

### Keyring Not Working

**Error**: `keyring` module not found

**Solution**:
```bash
pip install keyring
```

### Can't Access Keychain

**Error**: Permission denied accessing keychain

**Solution** (macOS):
```bash
# Grant Terminal access to Keychain
# System Preferences → Security & Privacy → Privacy → Keychain
```

**Solution** (Linux):
```bash
# Install keyring backend
sudo apt install gnome-keyring  # Ubuntu/Debian
```

### Profile Not Found

**Error**: Profile 'work' not found

**Solution**:
```bash
# Create profile first
python enterprise_cli.py create-profile work
```

### Audit Log Too Large

If `.auth_audit.json` grows large:

```python
# Automatic cleanup (keeps last 100 entries)
# Done automatically by SecurityManager

# Manual cleanup
rm .auth_audit.json
```

## 📚 API Reference

### SecurityManager Class

```python
from spotify_mcp.security import SecurityManager

# Initialize
security = SecurityManager(profile="default")

# Keychain operations
security.save_to_keychain("access_token", token)
token = security.get_from_keychain("access_token")
security.clear_keychain()

# Token management
security.save_tokens(access, refresh, expires_at, use_keychain=True)
tokens = security.get_tokens()
result = security.revoke_tokens()

# Monitoring
security.track_token_rotation(old_token, new_token)
log = security.get_audit_log(limit=20)
alerts = security.check_security_alerts()

# Profiles
profiles = SecurityManager.list_profiles()
SecurityManager.create_profile("work", client_id, client_secret)
```

## 🚀 Next Steps

1. **Try it**: `python enterprise_cli.py profiles`
2. **Enable keychain**: `python enterprise_cli.py enable-keychain`
3. **Monitor**: `python enterprise_cli.py audit`
4. **Create profile**: `python enterprise_cli.py create-profile work`

## 📝 Summary

These enterprise features transform the Spotify MCP Server from a basic auth system into a **production-ready, auditable, secure authentication framework** suitable for:

- 🏢 **Enterprise deployments**
- 🔐 **Security-conscious environments**
- 👥 **Multi-user/multi-account scenarios**
- 📊 **Compliance requirements**
- 🛡️ **Threat monitoring**

All features are **optional** and **backward-compatible** - existing setups continue working without changes!
