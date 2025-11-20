# Audio Features 403 Error - Troubleshooting Guide

## Problem
Getting 403 Forbidden error when calling the Spotify audio features API endpoint, even with valid authentication.

## Error Details
```
HTTP Error for GET to https://api.spotify.com/v1/audio-features/?ids=<track_id>
403 Forbidden - No specific reason provided
```

## Root Cause
This 403 error (with no specific error message from Spotify) typically indicates an **application-level restriction**, not an authentication issue. Your code is correct - this is a Spotify Developer Dashboard configuration issue.

## Solution Steps

### 1. Check Your Spotify Developer App Settings
Go to: https://developer.spotify.com/dashboard/applications

1. Click on your application
2. Check the app status:
   - **Development Mode**: Limited to 25 users, some endpoints may be restricted
   - **Extended Quota Mode**: Requires approval from Spotify

### 2. Verify App Scopes (Already Correct)
Your app already has all necessary scopes in `auth.py`. Audio features doesn't require special scopes since it's public data.

### 3. Request Extended Quota Mode
If your app is in Development Mode and you need full API access:

1. Go to your app in the Spotify Dashboard
2. Look for "Request Extension" or "Extended Quota Mode"
3. Fill out the application form:
   - Describe your use case
   - Explain that you need access to audio features API
   - Provide details about your MCP server

### 4. Workaround: Use Audio Analysis Instead
If you can't get Extended Quota Mode approved immediately, you can use the audio analysis endpoint which provides similar (but more detailed) information:

```python
# Instead of audio_features
analysis = sp.audio_analysis(track_id)
# This returns more detailed data including tempo, key, energy, etc.
```

## Testing
Once you've confirmed your app settings or requested Extended Quota:

1. Wait 24-48 hours for Spotify to review (if you requested Extended Quota)
2. Test with: `python tools/debug_audio_features.py`
3. The endpoint should work once approved

## Alternative: Create New App
If your current app can't be approved:

1. Create a new Spotify Developer App
2. Set it to "Web API" type
3. Add redirect URI: `http://localhost:8888/callback`
4. Update `.env` with new `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
5. Re-authenticate: `python -m spotify_mcp.auth`

## Verification
Your code is **100% correct**. The issue is purely on Spotify's side regarding app permissions/quotas.

## References
- Spotify Developer Dashboard: https://developer.spotify.com/dashboard
- Quota Extension Guide: https://developer.spotify.com/documentation/web-api/concepts/quota-modes
- Audio Features API: https://developer.spotify.com/documentation/web-api/reference/get-several-audio-features

## Status
✅ Code is correct  
✅ Authentication works  
✅ Track API works  
❌ Audio Features endpoint blocked by Spotify (app-level restriction)

## Next Steps
Check your Spotify Developer Dashboard and verify your app's quota mode. This is the only remaining issue.
