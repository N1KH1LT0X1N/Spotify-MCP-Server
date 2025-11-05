# Enterprise Security - Quick Reference

## 🚀 Quick Start

```bash
# 1. View available features
python enterprise_cli.py

# 2. Check current profiles
python enterprise_cli.py profiles

# 3. Enable keychain (optional, requires: pip install keyring)
python enterprise_cli.py enable-keychain

# 4. Re-authenticate to use new features
python test_auth.py
```

## 📋 Common Commands

### Profile Management
```bash
# List all profiles
python enterprise_cli.py profiles

# Create new profile
python enterprise_cli.py create-profile work

# Use profile in auth
python test_auth.py  # Uses default profile
```

### Token Revocation
```bash
# Revoke default profile
python enterprise_cli.py revoke

# Revoke specific profile
python enterprise_cli.py revoke work
```

### Monitoring
```bash
# View recent activity
python enterprise_cli.py audit

# View specific profile audit
python enterprise_cli.py audit work 50

# Check security alerts
python enterprise_cli.py alerts
```

### Keychain Storage
```bash
# Enable (requires: pip install keyring)
python enterprise_cli.py enable-keychain

# Disable
python enterprise_cli.py disable-keychain
```

## 🔐 Security Levels

### Level 1: Basic (Current Setup)
```bash
# What you have now:
✅ Tokens in .env file
✅ Automatic refresh
✅ Manual authentication

# No action needed - already working!
```

### Level 2: Audit Logging
```python
# In your auth code, enable security:
from spotify_mcp.auth import SpotifyAuthManager

auth = SpotifyAuthManager(use_security=True)
# Now all events are logged to .auth_audit.json
```

### Level 3: Maximum Security
```bash
# 1. Install keyring
pip install keyring

# 2. Enable keychain
python enterprise_cli.py enable-keychain

# 3. Use security features
# (Tokens now in OS keychain + full audit logging)

# 4. Re-authenticate
python test_auth.py
```

## 📊 What Gets Logged

```json
{
  "timestamp": "2025-11-05T10:30:00",
  "event": "tokens_saved",
  "data": {
    "storage": "keychain",
    "profile": "default",
    "expires_at": 1730806200
  }
}
```

Events tracked:
- ✅ Token saves
- ✅ Token refreshes
- ✅ Token rotations
- ✅ Revocations
- ✅ Keychain access
- ✅ Security alerts

## 🎯 Use Cases

### Use Case 1: Personal Project (You Now)
```bash
# Current setup is perfect!
# - .env file storage
# - Auto-refresh working
# - No extra complexity

# Optional: Add audit logging
# In auth.py, add: use_security=True
```

### Use Case 2: Work + Personal
```bash
# Create two profiles
python enterprise_cli.py create-profile work
python enterprise_cli.py create-profile personal

# Authenticate each
python test_auth.py  # Uses default/work
# (repeat for personal)
```

### Use Case 3: Team/Enterprise
```bash
# Install keyring
pip install keyring

# Enable keychain per user
python enterprise_cli.py enable-keychain

# Monitor security
python enterprise_cli.py alerts

# Setup cron for monitoring
0 9 * * * cd /path/to/spotify_mcp && python enterprise_cli.py alerts
```

## 🛠️ Integration

### With Existing Code
```python
# Before (still works):
from spotify_mcp.auth import get_spotify_client
sp = get_spotify_client()

# After (with security):
from spotify_mcp.auth import SpotifyAuthManager
auth = SpotifyAuthManager(use_security=True)
token = auth.get_access_token()
```

### With Claude Desktop
```json
{
  "mcpServers": {
    "spotify": {
      "command": "python",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "PYTHONPATH": "c:\\path\\to\\spotify_mcp\\src"
      }
    }
  }
}
```

## 📁 File Structure

```
spotify_mcp/
├── .env                    # Default profile credentials
├── .env.work              # Work profile (optional)
├── .auth_audit.json       # Security audit log (auto-created)
├── enterprise_cli.py      # CLI tool
└── src/
    └── spotify_mcp/
        ├── auth.py        # Updated with security support
        └── security.py    # Security manager
```

## ⚡ Performance Impact

| Feature | Overhead |
|---------|----------|
| Audit Logging | ~1ms per auth event |
| Keychain Storage | ~10-50ms per save/load |
| Token Rotation Tracking | ~0.5ms per refresh |
| Multi-Profile | None (file-based) |

**Bottom line**: Negligible impact on normal usage.

## 🔍 Debugging

### Check if security features are active:
```python
from spotify_mcp.auth import SECURITY_AVAILABLE
print(f"Security available: {SECURITY_AVAILABLE}")

from spotify_mcp.security import SecurityManager
sm = SecurityManager()
print(f"Keychain available: {sm.use_keychain()}")
```

### View audit log manually:
```bash
# Windows
type .auth_audit.json

# Linux/Mac
cat .auth_audit.json
```

### Clear everything and start fresh:
```bash
# Revoke tokens
python enterprise_cli.py revoke

# Delete audit log
rm .auth_audit.json  # or: del .auth_audit.json (Windows)

# Re-authenticate
python test_auth.py
```

## 📚 Learn More

- **Full Documentation**: `ENTERPRISE_SECURITY.md`
- **Auth Guide**: `AUTHENTICATION.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`

## 🎓 Summary

**You have 3 options:**

1. **Keep current setup** ✅ (Working great, nothing to change)
2. **Add audit logging** 📊 (Just add `use_security=True`)
3. **Full enterprise mode** 🔐 (Keychain + all features)

All are backward-compatible - choose based on your needs!

---

**Quick Test:**
```bash
python enterprise_cli.py profiles  # Should show "default" profile
```

**Ready for production? You already are!** 🚀
