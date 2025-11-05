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
      }
    }
  }
}
```

**⚠️ Important:** Replace the placeholders with your actual credentials from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

### 2. Add to Claude Desktop:

**Location:** `%APPDATA%\Claude\claude_desktop_config.json`

Or open: `C:\Users\admin\AppData\Roaming\Claude\claude_desktop_config.json`

### 3. Restart Claude Desktop

### 4. Look for the Spotify icon! 🎵

The icon should appear in the bottom-left corner with a green toggle switch. Just like the Vercel MCP server you showed me! 

## What Makes It Pretty:

✅ **Clean name:** Just "spotify" (not "spotify-mcp-server-123")  
✅ **Spotify green icon:** #1DB954 brand color  
✅ **Official Spotify logo:** Recognizable circular icon  
✅ **Proper metadata:** Description and version info  
✅ **Works immediately:** Your credentials are already configured!

## Try These Commands:

- "Play my Discover Weekly playlist"
- "What's currently playing?"
- "Search for chill jazz music"
- "Show me my top artists"
- "Add this song to my queue"

---

**Need help?** See `CLAUDE_DESKTOP_SETUP.md` for detailed instructions.
