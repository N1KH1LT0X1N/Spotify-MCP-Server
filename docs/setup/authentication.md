# Authentication Guide

## How Authentication Works

This MCP server uses **one-time manual authentication** followed by **automatic token refresh**.

### The Process:

```
┌─────────────────────────────────────────────────────────┐
│ 1. Initial Setup (ONE TIME - Manual)                   │
│    Run: python test_auth.py                            │
│    → Opens browser → Authorize → Paste URL            │
│    → Tokens saved to .env                              │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Automatic Forever After                             │
│    • Access token valid for 1 hour                     │
│    • Auto-refreshes using refresh token                │
│    • Refresh token valid for months                    │
│    • No manual intervention needed                     │
└─────────────────────────────────────────────────────────┘
```

## When Do You Need to Re-Authenticate?

You only need to run `python test_auth.py` again if:

- ❌ **Initial setup** (first time using the server)
- ❌ **Tokens cleared** (`.env` file deleted or tokens removed)
- ❌ **Credentials rotated** (Client ID or Secret changed in Spotify Dashboard)
- ❌ **Refresh token expired** (very rare - usually valid for 6+ months)

## When You DON'T Need to Re-Authenticate:

- ✅ **Server restarts** - tokens persist in `.env`
- ✅ **Claude Desktop restarts** - tokens persist
- ✅ **Computer restarts** - tokens persist
- ✅ **Access token expires** - auto-refreshes silently
- ✅ **Daily usage** - works seamlessly

## How Token Refresh Works

Your `auth.py` handles this automatically:

```python
def get_access_token(self):
    # 1. Check if current token is still valid
    if token_valid:
        return access_token  # ✅ Use existing token
    
    # 2. Token expired? Refresh it automatically
    if has_refresh_token:
        new_token = refresh_access_token(refresh_token)
        save_to_env(new_token)
        return new_token  # ✅ Silent renewal
    
    # 3. No valid tokens? Only then do manual auth
    return manual_authentication()
```

## Troubleshooting

### "Authentication Required" Error
**Cause:** No valid tokens in `.env`  
**Solution:** Run `python test_auth.py`

### "Invalid Client Secret" Error
**Cause:** Credentials in `.env` don't match Spotify Dashboard  
**Solution:**
1. Go to https://developer.spotify.com/dashboard
2. Verify Client ID and Client Secret match `.env`
3. If rotated, update `.env` and re-authenticate

### "Token Refresh Failed" Error
**Cause:** Refresh token expired or invalidated  
**Solution:** Run `python test_auth.py` to get new tokens

## Security Notes

- ✅ Tokens stored locally in `.env` (gitignored)
- ✅ No passwords stored anywhere
- ✅ Refresh token rotates automatically
- ✅ Follows OAuth 2.0 best practices
- ❌ Never commit `.env` to git

## Token Lifespan

| Token Type | Lifespan | Refresh Method |
|------------|----------|----------------|
| Access Token | 1 hour | Automatic using refresh token |
| Refresh Token | ~6 months | Manual re-authentication |

## Best Practices

1. **Keep credentials secret** - Never share Client Secret
2. **Don't rotate unnecessarily** - Only rotate if compromised
3. **Backup your `.env`** - Prevents re-authentication if file lost
4. **Monitor expiration** - Server logs when token refresh happens

## Why Not Fully Automate?

You might wonder: "Why not automate the initial authentication too?"

**Reasons we keep manual OAuth:**
- **Security**: No passwords stored
- **Spotify's design**: OAuth requires user consent
- **Simplicity**: One-time setup vs complex automation
- **Reliability**: Doesn't break when Spotify UI changes
- **Best practice**: OAuth is meant to be user-authorized

## Summary

**You authenticate once, then forget about it!** 🎉

The system is designed for **"set it and forget it"** - that one manual authentication gives you months of automatic, seamless access. This is actually the optimal user experience for OAuth-based systems.
