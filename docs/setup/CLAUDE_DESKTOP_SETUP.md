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
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback",
        "PYTHONPATH": "C:\\Users\\admin\\OneDrive\\Documents\\GitHub\\spotify_mcp\\src"
      },
      "icon": "C:\\Users\\admin\\OneDrive\\Documents\\GitHub\\spotify_mcp\\icon.svg"
    }
  }
}
```

**Important Notes:**

1. **Replace credentials**: Update `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` with your actual values
2. **Update PYTHONPATH**: Change the path to match your installation directory
3. **Update icon path**: Change to your full path to `icon.svg`
4. **Use absolute paths**: All paths must be absolute, not relative
5. **Windows paths**: Use double backslashes (`\\`) or forward slashes (`/`)
6. **Use 127.0.0.1**: Spotify requires `127.0.0.1`, not `localhost`

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
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback",
        "PYTHONPATH": "C:\\Users\\admin\\OneDrive\\Documents\\GitHub\\spotify_mcp\\src"
      },
      "icon": "C:\\Users\\admin\\OneDrive\\Documents\\GitHub\\spotify_mcp\\icon.svg"
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
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback"
      },
      "icon": "C:\\full\\path\\to\\spotify_mcp\\icon.svg"
    }
  }
}
```

**Note:** If you installed with `pip install -e .`, PYTHONPATH is not required because the package is already in the Python path.
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

### "Could not load app settings" / JSON Parse Error

**Symptom:** Claude Desktop shows "Unexpected token" or "is not valid JSON" error

**Cause:** The configuration file has a UTF-8 BOM (Byte Order Mark) that Claude Desktop cannot parse

**Solution:**
1. Open PowerShell in the project directory
2. Run this command to remove the BOM:
   ```powershell
   $content = Get-Content "$env:APPDATA\Claude\claude_desktop_config.json" -Raw
   [System.IO.File]::WriteAllText("$env:APPDATA\Claude\claude_desktop_config.json", $content, (New-Object System.Text.UTF8Encoding $false))
   ```
3. Restart Claude Desktop

**Prevention:** Always edit the config file with VS Code or Notepad++, not PowerShell's `Set-Content` which adds BOM.

### Server Shows but Won't Connect

- Check your credentials are correct
- Verify PYTHONPATH is set correctly in the config
- Make sure you've authenticated at least once (run `python scripts/diagnose_auth.py`)
- Verify redirect URI is `http://127.0.0.1:8888/callback` (not `localhost`)

### ModuleNotFoundError

**Symptom:** Error: `ModuleNotFoundError: No module named 'spotify_mcp'`

**Cause:** PYTHONPATH is not set in the environment variables

**Solution:** Add `"PYTHONPATH": "C:\\path\\to\\spotify_mcp\\src"` to the `env` section of your Claude Desktop config (see examples above). The PYTHONPATH must point to the `src` directory where the `spotify_mcp` module is located.

### Testing the Server Manually

```bash
# Set PYTHONPATH
$env:PYTHONPATH = "C:\Users\admin\OneDrive\Documents\GitHub\spotify_mcp\src"

# Run the server
python -m spotify_mcp.server
```

If this works, your configuration is correct!

## Icon

To display the Spotify icon in Claude Desktop:

1. **Add the `icon` property** to your configuration with the full path to `icon.svg`
2. **Use absolute paths** - relative paths won't work
3. **Restart Claude Desktop** completely after adding the icon

Example:
```json
{
  "mcpServers": {
    "spotify": {
      ...
      "icon": "C:\\Users\\YourName\\Documents\\GitHub\\spotify_mcp\\icon.svg"
    }
  }
}
```

The green Spotify brand color (#1DB954) makes it instantly recognizable in the Claude Desktop UI!
