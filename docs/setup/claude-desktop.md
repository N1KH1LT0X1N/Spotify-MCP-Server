# Claude Desktop Configuration Example

This file shows how to configure the Spotify MCP server with Claude Desktop.

## Configuration File Location

### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Linux
```
~/.config/Claude/claude_desktop_config.json
```

## Configuration Options

### Option 1: Using Environment Variables in Config (Recommended)

This approach sets PYTHONPATH and credentials directly in the config:

**Windows:**
```json
{
  "mcpServers": {
    "spotify": {
      "command": "C:\\Users\\YourName\\anaconda3\\python.exe",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "PYTHONPATH": "c:\\Users\\YourName\\Documents\\GitHub\\spotify_mcp\\src",
        "SPOTIFY_CLIENT_ID": "your_client_id_here",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret_here",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback"
      },
      "icon": "c:\\Users\\YourName\\Documents\\GitHub\\spotify_mcp\\icon.svg"
    }
  }
}
```

**macOS/Linux:**
```json
{
  "mcpServers": {
    "spotify": {
      "command": "python3",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "PYTHONPATH": "/Users/yourname/projects/spotify-mcp/src",
        "SPOTIFY_CLIENT_ID": "your_client_id_here",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret_here",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback"
      },
      "icon": "/Users/yourname/projects/spotify-mcp/icon.svg"
    }
  }
}
```

**Important Notes:**
- Use **full paths** (not relative paths like `~/` or `./`)
- On Windows, use `\\` for path separators
- `PYTHONPATH` must point to the `src` directory
- Add `icon` property for the Spotify logo to appear
- **Use `127.0.0.1`, not `localhost`** (Spotify requirement)

### Option 2: Using .env File (Alternative)

If you've already set up a `.env` file in the project and want to use those credentials:

```json
{
  "mcpServers": {
    "spotify": {
      "command": "python",
      "args": ["-m", "spotify_mcp.server"],
      "cwd": "/absolute/path/to/spotify-mcp",
      "env": {
        "PYTHONPATH": "/absolute/path/to/spotify-mcp/src"
      },
      "icon": "/absolute/path/to/spotify-mcp/icon.svg"
    }
  }
}
```

**Note:** You still need to set `PYTHONPATH`! The `.env` file will be automatically found by searching parent directories.

### Option 3: Using Virtual Environment

If you want to use a specific Python virtual environment:

```json
{
  "mcpServers": {
    "spotify": {
      "command": "/absolute/path/to/spotify-mcp/venv/bin/python",
      "args": ["-m", "spotify_mcp.server"],
      "cwd": "/absolute/path/to/spotify-mcp",
      "icon": "/absolute/path/to/spotify-mcp/icon.svg"
    }
  }
}
```

## Multiple Server Configuration

You can run multiple MCP servers alongside Spotify:

```json
{
  "mcpServers": {
    "spotify": {
      "command": "python",
      "args": ["-m", "spotify_mcp.server"],
      "cwd": "/path/to/spotify-mcp",
      "env": {
        "SPOTIFY_CLIENT_ID": "your_client_id_here",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret_here"
      },
      "icon": "/path/to/spotify-mcp/icon.svg"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/username/Documents"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your_github_token"
      }
    }
  }
}
```

## Troubleshooting Configuration

### Common Issues and Solutions

#### "ModuleNotFoundError: No module named 'spotify_mcp'"

**Problem:** Python can't find the spotify_mcp module.

**Solution:** Add `PYTHONPATH` pointing to the `src` directory:
```json
{
  "env": {
    "PYTHONPATH": "c:\\full\\path\\to\\spotify_mcp\\src"
  }
}
```

#### "Unexpected token" / Invalid JSON errors

**Problem:** Authentication prompts interfering with MCP JSON-RPC protocol.

**Solution:** Make sure you're using the latest version of the code where authentication outputs to stderr instead of stdout. Update your repository and restart Claude Desktop.

#### "Could not load app settings" / UTF-8 BOM Error

**Problem:** Claude Desktop shows JSON parse error with "Unexpected token".

**Solution:** The config file has a UTF-8 BOM. Remove it with:
```powershell
$content = Get-Content "$env:APPDATA\Claude\claude_desktop_config.json" -Raw
[System.IO.File]::WriteAllText("$env:APPDATA\Claude\claude_desktop_config.json", $content, (New-Object System.Text.UTF8Encoding $false))
```

See [troubleshooting.md](troubleshooting.md) for more details.

#### "ERR_CONNECTION_REFUSED" during authentication

**This is NORMAL!** When authenticating:
1. Browser redirects to `http://127.0.0.1:8888/callback?code=...`
2. Shows "connection refused" (no server listening - this is expected)
3. The authorization code is in the URL
4. When Claude prompts you, paste the full URL from your browser

#### Tokens not being saved

**Problem:** Authentication completes but tokens don't persist.

**Solution:** 
1. Run standalone test: `python test_auth.py` in the project directory
2. Verify tokens are in `.env` file after authentication
3. Make sure the `.env` file is in the project root

#### "Invalid redirect URI"

**Problem:** Redirect URI mismatch.

**Solution:**
1. **Use `http://127.0.0.1:8888/callback`** (not `localhost`)
2. Add it to Spotify Developer Dashboard exactly as shown
3. Use the same value in `.env` and Claude config

### Can't Find Python
Use the full path to Python:
```bash
# Find Python path
which python
# or
which python3
```

### Finding Python Path

**Windows:**
```powershell
where python
# or
where python3
```

**macOS/Linux:**
```bash
which python
# or
which python3
```

Then use that full path in the config.
```json
{
  "command": "/usr/local/bin/python3",
  ...
}
```

### Module Not Found Error
Make sure the `cwd` points to the spotify-mcp directory and you've installed it:
```bash
cd /path/to/spotify-mcp
pip install -e .
```

### Authentication Issues
On first run through Claude Desktop, you'll need to authenticate:

1. Claude will show authentication prompts in the chat
2. Your browser opens to Spotify authorization
3. Click "Agree"
4. **You'll see "ERR_CONNECTION_REFUSED" - this is NORMAL**
5. Copy the full URL from your browser's address bar
6. Paste it back to Claude when prompted
7. Tokens are automatically saved to `.env` for future use

**Pre-authenticate (Optional):**
You can authenticate before using Claude Desktop:
```bash
cd /path/to/spotify-mcp
python test_auth.py
```

This saves tokens to `.env`, then Claude Desktop will use them automatically.

### More Help

For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

### Finding Logs (if needed)

**macOS:**
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

**Windows:**
```
%LOCALAPPDATA%\Claude\logs
```

## Verifying Configuration

After updating the config:

1. **Restart Claude Desktop** completely (quit and reopen)
2. Start a new conversation
3. Look for the 🔌 icon indicating MCP servers are connected
4. Try a test query: "What's my Spotify username?"

If you see Spotify tools available in Claude's tool panel, you're all set! 🎉

## Getting Help

If something isn't working:
1. Check the troubleshooting section above
2. Run `python verify_setup.py` in the project directory
3. Check Claude Desktop logs
4. Make sure all paths are absolute, not relative
5. Ensure Spotify credentials are correct

## Example Queries to Try

Once configured, ask Claude:
- "What's currently playing on my Spotify?"
- "Search for songs by The Beatles"
- "Create a playlist called 'Focus Music'"
- "What are my top 10 artists this month?"
- "Add Bohemian Rhapsody to my queue"
- "Show me my saved tracks"
- "Get recommendations based on this track: [paste Spotify URL]"
