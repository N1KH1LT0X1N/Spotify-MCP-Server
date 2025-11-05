# Diagnostic Tools Comparison

## Overview

You now have **3 diagnostic tools** for troubleshooting authentication:

## 🔧 Tool Comparison

### 1. `diagnose_auth.py` (Standalone Script) ⭐ RECOMMENDED

**Best for:** First-time users, quick status checks, guided troubleshooting

```bash
# Auto-diagnosis (recommended)
python diagnose_auth.py

# Interactive menu
python diagnose_auth.py --interactive
```

**Features:**
- ✅ Automatic diagnosis with guidance
- ✅ Checks .env file existence
- ✅ Validates credentials present
- ✅ Token status check
- ✅ Tests token refresh
- ✅ Clear, user-friendly output
- ✅ Interactive menu (6 options)
- ✅ No Python knowledge needed

**Output Example:**
```
✅ ALL GOOD: You have valid tokens!
   Token expires in: 0:28:21

   ✓ Your tokens will auto-refresh when needed
   ✓ You should NOT need to manually re-authenticate
   ✓ System is working correctly
```

---

### 2. `python -m src.spotify_mcp.auth` (Module Tool)

**Best for:** Python developers, verbose logging

```bash
python -m src.spotify_mcp.auth
```

**Features:**
- ✅ Token status check
- ✅ Get access token
- ✅ Force refresh
- ✅ Clear tokens
- ✅ Verbose logging mode
- ⚠️ Requires Python module knowledge

**Output Example:**
```
🔍 Spotify Authentication Diagnostic Tool

Current Token Status:
----------------------------------------
  has_access_token: True
  has_refresh_token: True
  expires_in_seconds: 1939
```

---

### 3. `test_auth.py` (Test Script)

**Best for:** Initial authentication, testing auth flow

```bash
python test_auth.py
```

**Features:**
- ✅ Full authentication test
- ✅ Verifies tokens saved
- ✅ Shows user info
- ✅ Clear success/failure messages
- ⚠️ Doesn't show detailed diagnostics

**Output Example:**
```
✓ Authentication Successful!

User: N1K
Email: nikhilpise69@gmail.com
Account: PREMIUM
```

---

## 📊 When to Use Each Tool

| Scenario | Use This Tool |
|----------|---------------|
| **First time setup** | `python diagnose_auth.py` |
| **"Something's wrong"** | `python diagnose_auth.py` |
| **Quick status check** | `python diagnose_auth.py` |
| **Initial authentication** | `python test_auth.py` |
| **Verbose debugging** | `python -m src.spotify_mcp.auth` |
| **Force token refresh** | `python diagnose_auth.py --interactive` |
| **Clear tokens** | `python diagnose_auth.py --interactive` |
| **Check user info** | `python test_auth.py` |

---

## 🎯 Quick Command Reference

### Problem: "Is my setup working?"
```bash
python diagnose_auth.py
```

### Problem: "I need to clear tokens"
```bash
python diagnose_auth.py --interactive
# Choose option 4
```

### Problem: "I want to see detailed logs"
```bash
python -m src.spotify_mcp.auth
# Choose option 1
```

### Problem: "First time authenticating"
```bash
python test_auth.py
```

---

## 🆚 Feature Matrix

| Feature | diagnose_auth.py | Module Tool | test_auth.py |
|---------|------------------|-------------|--------------|
| Auto-diagnosis | ✅ | ❌ | ❌ |
| .env file check | ✅ | ❌ | ❌ |
| Credential validation | ✅ | ❌ | ❌ |
| Token status | ✅ | ✅ | ✅ |
| Force refresh | ✅ | ✅ | ✅ |
| Clear tokens | ✅ | ✅ | ✅ |
| Interactive menu | ✅ | ✅ | ❌ |
| Verbose logging | ✅ | ✅ | ❌ |
| User info display | ❌ | ❌ | ✅ |
| Guided help | ✅ | ❌ | ❌ |
| User-friendly | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

---

## 💡 Recommendations

### For Regular Users
**Start with:** `python diagnose_auth.py`
- Most user-friendly
- Automatic problem detection
- Clear guidance

### For Developers
**Start with:** `python -m src.spotify_mcp.auth`
- More technical output
- Verbose logging available
- Direct module access

### For Initial Setup
**Start with:** `python test_auth.py`
- Simple authentication test
- Shows your Spotify user info
- Confirms setup working

---

## 🚀 Workflow Examples

### Scenario 1: Brand New Setup
```bash
# 1. Check if credentials are set
python diagnose_auth.py
# Shows: "Not yet authenticated"

# 2. Authenticate
python test_auth.py
# Opens browser, paste URL, tokens saved

# 3. Verify everything works
python diagnose_auth.py
# Shows: "ALL GOOD: You have valid tokens!"
```

### Scenario 2: Something Broke
```bash
# 1. Quick diagnosis
python diagnose_auth.py
# Shows what's wrong + recommended action

# 2. If tokens need clearing
python diagnose_auth.py --interactive
# Choose option 4 to clear

# 3. Re-authenticate
python test_auth.py
```

### Scenario 3: Advanced Debugging
```bash
# 1. Check status with verbose logging
python -m src.spotify_mcp.auth
# Choose option 1

# Logs show:
# [timestamp] Checking token status...
# [timestamp] ✓ Using cached access token

# 2. If you need more control
python diagnose_auth.py --interactive
# Interactive menu with all options
```

---

## 📝 Summary

**Quick Reference:**
- 🎯 **Most users:** `python diagnose_auth.py`
- 🔧 **Developers:** `python -m src.spotify_mcp.auth`
- ✅ **Initial auth:** `python test_auth.py`

**All three tools are complementary** - use whichever fits your needs! The standalone `diagnose_auth.py` is recommended for most users because it provides automatic diagnosis and clear guidance.
