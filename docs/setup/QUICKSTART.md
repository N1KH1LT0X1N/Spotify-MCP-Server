# Quick Start Guide

Get your Spotify MCP server running in 5 minutes!

## Step 1: Install Dependencies (1 minute)

```bash
cd spotify-mcp
pip install -e .
```

## Step 2: Create Spotify App (2 minutes)

1. Visit https://developer.spotify.com/dashboard
2. Click **"Create app"**
3. Fill in:
   - **Name**: "My Spotify MCP" (or anything)
   - **Description**: "MCP server for AI assistant"
   - **Redirect URI**: `http://127.0.0.1:8888/callback` ⚠️ **MUST use 127.0.0.1, not localhost**
   - **APIs**: Select "Web API"
4. Click **"Save"**
5. Click **"Settings"** to see your credentials

**Important:** Spotify requires the explicit IPv4 address `127.0.0.1` instead of `localhost`.

## Step 3: Configure Environment (1 minute)

```bash
# Copy example config
cp .env.example .env

# Edit .env and paste your credentials
nano .env  # or use any editor
```

Your `.env` should look like:
```
SPOTIFY_CLIENT_ID=abc123...
SPOTIFY_CLIENT_SECRET=def456...
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

**Note:** Use `127.0.0.1`, not `localhost` - Spotify requires the explicit IPv4 address.

## Step 4: Verify Setup (30 seconds)

```bash
python verify_setup.py
```

If all checks pass ✓, you're ready!

## Step 5: First Run (30 seconds)

### Option A: Test Authentication Standalone

```bash
python test_auth.py
```

**First time only:** Your browser will open for Spotify authorization.
1. Log in to Spotify
2. Click "Agree"
3. **You'll see "ERR_CONNECTION_REFUSED" - this is NORMAL!**
4. Copy the **full URL** from your browser's address bar (looks like `http://127.0.0.1:8888/callback?code=...`)
5. Paste it back in the terminal

Done! Your tokens are saved and will auto-refresh.

### Option B: Use with Claude Desktop Directly

Skip standalone testing and authenticate through Claude Desktop (see below).

## Using with Claude Desktop

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Linux:** `~/.config/Claude/claude_desktop_config.json`

### Recommended Configuration (with PYTHONPATH):

```json
{
  "mcpServers": {
    "spotify": {
      "command": "python",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "PYTHONPATH": "/full/path/to/spotify-mcp/src",
        "SPOTIFY_CLIENT_ID": "your_client_id_here",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret_here",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback"
      }
    }
  }
}
```

**Windows example:**
```json
{
  "mcpServers": {
    "spotify": {
      "command": "C:\\Users\\YourName\\anaconda3\\python.exe",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "PYTHONPATH": "c:\\Users\\YourName\\Documents\\GitHub\\spotify_mcp\\src",
        "SPOTIFY_CLIENT_ID": "abcd1234...",
        "SPOTIFY_CLIENT_SECRET": "efgh5678...",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback"
      }
    }
  }
}
```

**Important:**
- Use **full paths** (not relative paths)
- On Windows, use `\\` for path separators
- Set `PYTHONPATH` to the `src` directory
- Use `127.0.0.1`, not `localhost`

Restart Claude Desktop and you'll see Spotify tools available! 🎉

## Quick Test

Ask Claude:
- "What's currently playing on Spotify?"
- "Search for Bohemian Rhapsody and play it"
- "Create a playlist called 'AI Picks' and add some tracks"
- "What are my top artists this month?"

## Troubleshooting

### "ModuleNotFoundError: No module named 'spotify_mcp'"
Add `PYTHONPATH` to your environment or Claude Desktop config pointing to the `src` directory.

### "ERR_CONNECTION_REFUSED" after clicking Agree
**This is NORMAL!** Copy the full URL from your browser's address bar (including the `?code=...` part) and paste it when prompted.

### Authentication prompts appearing as errors in Claude
Make sure you're using the latest code - authentication prompts should go to stderr, not stdout.

### Tokens not saving
Run `python test_auth.py` to verify authentication works and tokens are saved to `.env`.

### "Invalid redirect URI"
1. Use `http://127.0.0.1:8888/callback` (not `localhost`)
2. Make sure it's added in your Spotify Developer Dashboard
3. Make sure it matches exactly in `.env` and Claude config

For more troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## What's Included

**22 Tools Ready to Use:**
- Playback control (play, pause, skip, volume, shuffle, repeat, seek)
- Device management
- Search (tracks, albums, artists, playlists)
- Recommendations
- Library management (save/remove tracks)
- Playlist creation and management
- Queue management
- User profile and top tracks/artists

## Next Steps

- Check out the full [README.md](README.md) for all features
- See tool documentation in the code for advanced usage
- Star the repo if you find it useful!
