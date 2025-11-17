# 🎵 Spotify MCP Server - Quick Setup

## For Claude Desktop

### 1. Copy this configuration:

```json
{
  "mcpServers": {
    "spotify": {
      "command": "C:\\path\\to\\your\\venv\\Scripts\\python.exe",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_spotify_client_id_here",
        "SPOTIFY_CLIENT_SECRET": "your_spotify_client_secret_here",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback"
      },
      "icon": "C:\\path\\to\\spotify_mcp\\icon.svg"
    }
  }
}
```

**⚠️ Important:** 
- Replace `C:\\path\\to\\your\\venv\\Scripts\\python.exe` with your Python path
- Replace `your_spotify_client_id_here` and `your_spotify_client_secret_here` with your actual credentials from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- Replace `C:\\path\\to\\spotify_mcp\\icon.svg` with the full path to your `icon.svg` file
- **Must use `127.0.0.1`, not `localhost`** for the redirect URI

### 2. Add to Claude Desktop:

**Location:** `%APPDATA%\Claude\claude_desktop_config.json`

Or open: `C:\Users\admin\AppData\Roaming\Claude\claude_desktop_config.json`

### 3. Restart Claude Desktop

### 4. Look for the Spotify icon! 🎵

The icon should appear in the bottom-left corner with a green toggle switch. Just like the Vercel MCP server you showed me! 

## What Makes It Pretty:

✅ **Clean name:** Just "spotify" (not "spotify-mcp-server-123")  
✅ **Spotify green icon:** #1DB954 brand color with the icon property  
✅ **Official Spotify logo:** Recognizable circular icon from `icon.svg`  
✅ **Proper metadata:** Description and version info  
✅ **Works immediately:** Your credentials are configured!

**Note:** The `icon` property must point to the full absolute path of `icon.svg` for Claude Desktop to display it.

## Try These Commands:

With **58 tools** across **14 categories**, you can:

- "Play my Discover Weekly playlist"
- "What's currently playing?"
- "Search for chill jazz music"
- "Show me my top artists this month"
- "Add this song to my queue"
- "Find albums by Radiohead"
- "Save this podcast episode"
- "What audiobooks do I have saved?"
- "Show me new music releases"
- "Get recommendations based on this track"

---

**Need help?** See [CLAUDE_DESKTOP_SETUP.md](CLAUDE_DESKTOP_SETUP.md) for detailed instructions or [troubleshooting.md](troubleshooting.md) for common issues.
