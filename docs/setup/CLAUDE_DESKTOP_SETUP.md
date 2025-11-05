# 🎵 Claude Desktop Setup

Make your Spotify MCP Server look beautiful in Claude Desktop!

## Configuration

### Windows

Edit: `%APPDATA%\Claude\claude_desktop_config.json`

### macOS

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Linux

Edit: `~/.config/Claude/claude_desktop_config.json`

## Configuration File

```json
{
  "mcpServers": {
    "spotify": {
      "command": "python",
      "args": [
        "-m",
        "spotify_mcp.server"
      ],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_client_id_here",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret_here",
        "SPOTIFY_REDIRECT_URI": "http://localhost:8888/callback",
        "PYTHONPATH": "C:\\Users\\admin\\OneDrive\\Documents\\GitHub\\spotify_mcp\\src"
      }
    }
  }
}
```

**Important Notes:**

1. **Replace credentials**: Update `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` with your actual values
2. **Update PYTHONPATH**: Change the path to match your installation directory
3. **Use absolute paths**: The path must be absolute, not relative
4. **Windows paths**: Use double backslashes (`\\`) or forward slashes (`/`)

## Alternative: Using Full Python Path

If you installed the package in a virtual environment:

```json
{
  "mcpServers": {
    "spotify": {
      "command": "C:\\Users\\admin\\OneDrive\\Documents\\GitHub\\spotify_mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "spotify_mcp.server"
      ],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_client_id_here",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret_here",
        "SPOTIFY_REDIRECT_URI": "http://localhost:8888/callback"
      }
    }
  }
}
```

## Alternative: Using Editable Install

If you installed with `pip install -e .`:

```json
{
  "mcpServers": {
    "spotify": {
      "command": "python",
      "args": [
        "-m",
        "spotify_mcp.server"
      ],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_client_id_here",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret_here",
        "SPOTIFY_REDIRECT_URI": "http://localhost:8888/callback"
      }
    }
  }
}
```

## Verification

1. Save the configuration file
2. Restart Claude Desktop completely
3. Look for the Spotify icon in the bottom-left corner
4. The icon should appear with a green toggle switch
5. Enable the toggle to connect

## Troubleshooting

### Server Not Appearing

- Make sure the JSON is valid (no trailing commas, proper quotes)
- Check that all paths are absolute and correct
- Verify Python is accessible from the command line

### Server Shows but Won't Connect

- Check your credentials are correct
- Verify PYTHONPATH is set correctly
- Make sure you've authenticated at least once (run `python scripts/diagnose_auth.py`)

### Testing the Server Manually

```bash
# Set PYTHONPATH
$env:PYTHONPATH = "C:\Users\admin\OneDrive\Documents\GitHub\spotify_mcp\src"

# Run the server
python -m spotify_mcp.server
```

If this works, your configuration is correct!

## Icon

The Spotify icon (`icon.svg`) is automatically used by Claude Desktop when available in the project root. The green Spotify brand color (#1DB954) makes it instantly recognizable!
