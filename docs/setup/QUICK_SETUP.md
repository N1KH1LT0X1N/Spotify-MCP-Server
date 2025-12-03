# 🎵 Quick Setup (5 minutes)

## Step 1: Get Spotify Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click **Create App**
3. Set Redirect URI to: `http://127.0.0.1:8888/callback`
4. Copy your **Client ID** and **Client Secret**

---

## Step 2: Install & Authenticate

```bash
cd spotify_mcp
pip install -e .
python -m spotify_mcp.auth
```

Complete the browser authentication when prompted.

---

## Step 3: Configure Claude Desktop

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "spotify": {
      "command": "python",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_client_id",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback",
        "PYTHONPATH": "C:\\path\\to\\spotify_mcp\\src"
      }
    }
  }
}
```

> ⚠️ Replace paths and credentials with your actual values.

---

## Step 4: Restart Claude Desktop

Look for the Spotify tools in Claude's tool list.

---

## Test It!

Ask Claude:
- "What Spotify tools do you have?"
- "Search for Taylor Swift songs"
- "What's currently playing?"

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Add `PYTHONPATH` pointing to `src` folder |
| No tokens found | Run `python -m spotify_mcp.auth` |
| Invalid redirect URI | Use `127.0.0.1` not `localhost` |
| No active device | Open Spotify app on any device |

See [troubleshooting.md](troubleshooting.md) for more solutions.
