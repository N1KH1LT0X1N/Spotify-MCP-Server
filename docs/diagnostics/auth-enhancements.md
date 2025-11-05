# Enhanced Authentication Features

## 🎯 What's New

Your `auth.py` now includes **enhanced diagnostics and logging** for better troubleshooting and visibility!

## ✨ New Features

### 1. Verbose Logging Mode
Get detailed insights into the authentication process:

```python
from spotify_mcp.auth import SpotifyAuthManager

# Enable verbose logging
auth = SpotifyAuthManager(verbose=True)
token = auth.get_access_token()

# Logs to stderr:
# [2025-11-05 16:58:00] Checking token status...
# [2025-11-05 16:58:00] Token status: {...}
# [2025-11-05 16:58:00] ✓ Using cached access token
```

### 2. Token Status Diagnostics
Check the current state of your tokens:

```python
auth = SpotifyAuthManager()
status = auth.get_token_status()

print(status)
# {
#   'has_access_token': True,
#   'has_refresh_token': True,
#   'has_expiry': True,
#   'expires_at': '2025-11-05T17:30:10',
#   'is_expired': False,
#   'expires_in_seconds': 1939,
#   'expires_in_human': '0:32:19'
# }
```

### 3. Better Error Messages
Clear, user-friendly error messages:

```
╔═══════════════════════════════════════════════════════════╗
║           ⚠️  REFRESH TOKEN EXPIRED                      ║
╚═══════════════════════════════════════════════════════════╝
Your refresh token has expired (typically after 6 months).
You'll need to re-authorize the application.
This is normal - your new tokens will last another 6 months.
```

### 4. Force Refresh Command
Manually trigger token refresh:

```python
auth = SpotifyAuthManager()
success = auth.force_refresh()

if success:
    print("Token refreshed!")
else:
    print("Need to re-authenticate")
```

### 5. Interactive Diagnostic Tool
Run diagnostics from command line:

```bash
python -m src.spotify_mcp.auth
```

Output:
```
🔍 Spotify Authentication Diagnostic Tool

Current Token Status:
----------------------------------------
  has_access_token: True
  has_refresh_token: True
  has_expiry: True
  expires_at: 2025-11-05T17:30:10
  is_expired: False
  expires_in_seconds: 1939
  expires_in_human: 0:32:19

What would you like to do?
1. Get access token (auto-refresh if needed)
2. Force refresh
3. Clear tokens
4. Exit
>
```

## 🔧 Usage Examples

### Example 1: Troubleshooting Auth Issues
```python
from spotify_mcp.auth import SpotifyAuthManager

# Enable verbose mode for debugging
auth = SpotifyAuthManager(verbose=True)

# Check current status
status = auth.get_token_status()
print(f"Token expires in: {status['expires_in_human']}")

# Get token (with detailed logging)
token = auth.get_access_token()
```

### Example 2: Proactive Token Management
```python
auth = SpotifyAuthManager()

# Check if token is expiring soon
status = auth.get_token_status()
if status['expires_in_seconds'] < 300:  # Less than 5 minutes
    print("Token expiring soon, forcing refresh...")
    auth.force_refresh()
```

### Example 3: Quick Diagnostics
```bash
# Run diagnostic tool
python -m src.spotify_mcp.auth

# Select option 1 to test token retrieval
# Logs will show exactly what's happening
```

### Example 4: With Enterprise Security
```python
# Combine with enterprise features
auth = SpotifyAuthManager(
    profile="work",
    use_security=True,
    verbose=True
)

# Get detailed logs + security audit trail
token = auth.get_access_token()
```

## 📊 What Gets Logged (Verbose Mode)

When `verbose=True`, you see:

```
[2025-11-05 16:58:00] Checking token status...
[2025-11-05 16:58:00] Token status: {'has_access_token': True, ...}
[2025-11-05 16:58:00] ✓ Using cached access token

# Or if token expired:
[2025-11-05 16:58:00] ⚠ Token expired or expiring soon, attempting refresh...
[2025-11-05 16:58:01] ✓ Token refreshed successfully

# Or if starting OAuth:
[2025-11-05 16:58:00] Starting OAuth flow...
[2025-11-05 16:58:01] Opened browser to: https://accounts.spotify.com/...
[2025-11-05 16:58:15] Extracted auth code: AQDEcOky-f...
[2025-11-05 16:58:16] Received token info from Spotify
[2025-11-05 16:58:16] Tokens saved. Access token expires at: 2025-11-05 17:58:16
```

## 🎯 When to Use Each Feature

| Feature | When to Use |
|---------|-------------|
| **Verbose Mode** | Debugging auth issues, understanding flow |
| **Token Status** | Checking if tokens are valid before operations |
| **Force Refresh** | Testing token refresh, proactive management |
| **Diagnostic CLI** | Quick status check, troubleshooting |
| **Better Errors** | Understanding why auth failed |

## 🔄 Backward Compatibility

All existing code continues to work:

```python
# Still works exactly as before
from spotify_mcp.auth import get_spotify_client

sp = get_spotify_client()
# No changes needed!

# But you can opt-in to verbose mode:
sp = get_spotify_client(verbose=True)
```

## 🆚 Comparison

### Before (Basic)
```python
auth = SpotifyAuthManager()
token = auth.get_access_token()
# Silent operation, no visibility
```

### After (Enhanced)
```python
# Option 1: Still silent (default)
auth = SpotifyAuthManager()
token = auth.get_access_token()

# Option 2: With diagnostics
auth = SpotifyAuthManager(verbose=True)
status = auth.get_token_status()
print(f"Token valid for: {status['expires_in_human']}")
token = auth.get_access_token()
# Detailed logging to stderr

# Option 3: CLI tool
# python -m src.spotify_mcp.auth
# Interactive diagnostics
```

## 🐛 Troubleshooting Workflow

### Problem: "Authentication keeps failing"

```bash
# Step 1: Run diagnostics
python -m src.spotify_mcp.auth

# Step 2: Check token status
# (Tool shows: has_access_token, is_expired, etc.)

# Step 3: Try force refresh (option 2)
# If fails → need to re-authenticate (option 3 to clear)

# Step 4: Re-authenticate with verbose mode
python test_auth.py
# Or in code:
auth = SpotifyAuthManager(verbose=True)
token = auth.get_access_token()
```

### Problem: "Token expired after 6 months"

The enhanced error message now explains:
```
⚠️  REFRESH TOKEN EXPIRED
Your refresh token has expired (typically after 6 months).
You'll need to re-authorize the application.
This is normal - your new tokens will last another 6 months.
```

Just run `python test_auth.py` to re-authenticate.

## 📝 Summary

### What Changed
✅ Added `verbose` parameter for detailed logging
✅ Added `get_token_status()` method
✅ Added `force_refresh()` method
✅ Enhanced error messages (6-month expiry explained)
✅ Added diagnostic CLI tool
✅ Better token validation
✅ All logs go to stderr (MCP-safe)

### What Didn't Change
✅ Existing code works unchanged
✅ Default behavior identical
✅ No new dependencies
✅ Backward compatible

### When to Use
- **Daily use**: Default mode (no verbose)
- **Debugging**: Verbose mode
- **Quick check**: Diagnostic CLI
- **Testing**: Force refresh
- **Enterprise**: All features + security

---

**Try it now:**
```bash
python -m src.spotify_mcp.auth
```

Your authentication is already working - these are **optional enhancements** for better visibility and troubleshooting! 🎉
