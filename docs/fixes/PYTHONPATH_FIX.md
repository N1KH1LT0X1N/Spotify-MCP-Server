# PYTHONPATH Configuration Fix

**Date:** November 20, 2025  
**Issue:** ModuleNotFoundError when running server with Claude Desktop  
**Status:** ✅ RESOLVED

## Problem

When Claude Desktop attempted to run the Spotify MCP server, it failed with:

```
C:\Users\admin\anaconda3\python.exe: Error while finding module specification for 'spotify_mcp.server' 
(ModuleNotFoundError: No module named 'spotify_mcp')
```

## Root Cause

Python could not locate the `spotify_mcp` module because the `src` directory was not in Python's module search path. When running with the `-m` flag (e.g., `python -m spotify_mcp.server`), Python needs to know where to find the module.

The Claude Desktop configuration was missing the `PYTHONPATH` environment variable that tells Python where to search for modules.

## Solution

Added `PYTHONPATH` to the `env` section of the Claude Desktop configuration file, pointing to the `src` directory where the `spotify_mcp` module is located.

### Configuration File Location

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

### Required Configuration

```json
{
  "mcpServers": {
    "spotify": {
      "command": "C:\\Users\\admin\\anaconda3\\python.exe",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "PYTHONPATH": "C:\\Users\\admin\\OneDrive\\Documents\\GitHub\\spotify_mcp\\src",
        "SPOTIFY_CLIENT_ID": "your_client_id",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback"
      },
      "icon": "C:\\Users\\admin\\OneDrive\\Documents\\GitHub\\spotify_mcp\\icon.svg"
    }
  }
}
```

### Key Points

1. **PYTHONPATH must point to the `src` directory** - This is where the `spotify_mcp` package is located
2. **Use absolute paths** - Relative paths won't work in this context
3. **Windows path format** - Use double backslashes (`\\`) or forward slashes (`/`)
4. **Apply to your environment** - Replace the path with your actual installation directory

## Alternatives

### Option 1: Using Virtual Environment (PYTHONPATH Not Required)

If you use the Python executable from a virtual environment where the package is installed with `pip install -e .`, PYTHONPATH is not required:

```json
{
  "mcpServers": {
    "spotify": {
      "command": "C:\\path\\to\\spotify_mcp\\.venv\\Scripts\\python.exe",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_client_id",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback"
      }
    }
  }
}
```

### Option 2: System-wide Installation (PYTHONPATH Not Required)

If you install the package system-wide or user-wide with `pip install .`, PYTHONPATH is not required:

```bash
# Install the package
pip install .

# Or in editable mode
pip install -e .
```

Then use the standard Python command:

```json
{
  "mcpServers": {
    "spotify": {
      "command": "python",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_client_id",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback"
      }
    }
  }
}
```

## Testing

### Manual Test (PowerShell)

```powershell
# Set PYTHONPATH
$env:PYTHONPATH = "C:\Users\admin\OneDrive\Documents\GitHub\spotify_mcp\src"

# Test module import
python -c "from spotify_mcp.server import main; print('✓ Module found')"

# Run the server
python -m spotify_mcp.server
```

### Verification

After updating the Claude Desktop config:

1. Save the configuration file
2. Restart Claude Desktop completely (quit and reopen)
3. Check the Claude Desktop logs for any errors:
   - **Windows:** `%APPDATA%\Claude\logs\mcp-server-spotify.log`
   - **macOS:** `~/Library/Logs/Claude/mcp-server-spotify.log`
4. Look for the Spotify icon in Claude Desktop's MCP servers section
5. Try a test command: "What's my Spotify username?"

## Documentation Updates

All relevant documentation has been updated to include PYTHONPATH in configuration examples:

- ✅ `README.md` - Updated main configuration example
- ✅ `docs/setup/CLAUDE_DESKTOP_SETUP.md` - Added PYTHONPATH to all examples
- ✅ `docs/setup/QUICK_SETUP.md` - Added PYTHONPATH requirement
- ✅ `docs/setup/GET_STARTED.md` - Updated configuration examples
- ✅ `docs/setup/QUICKSTART.md` - Added PYTHONPATH to recommended config
- ✅ `docs/setup/claude-desktop.md` - Already had PYTHONPATH documented
- ✅ `docs/setup/troubleshooting.md` - Already had ModuleNotFoundError troubleshooting

## Related Issues

This issue was initially misdiagnosed as an authentication problem because:

1. The log file contained old authentication errors from October 30, 2025
2. These old errors were visible when scrolling through the log
3. The actual current error (ModuleNotFoundError from November 20, 2025) was only visible at the end of the log file

### Debugging Lesson

When troubleshooting log files:
- ✅ **Check timestamps** - Log files append, don't overwrite
- ✅ **Read from the end** - Most recent errors are at the bottom
- ✅ **Check file modification date** - Confirms when last written
- ✅ **Use `tail` or `Get-Content -Tail`** - Gets the most recent entries

## References

- [Python Module Search Path](https://docs.python.org/3/tutorial/modules.html#the-module-search-path)
- [PYTHONPATH Environment Variable](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH)
- [Claude Desktop MCP Configuration](https://modelcontextprotocol.io/docs/tools/claude-desktop)

## Status

✅ **RESOLVED** - All documentation updated with PYTHONPATH requirement  
✅ **TESTED** - Server starts successfully with PYTHONPATH set  
✅ **DOCUMENTED** - Multiple guides updated with correct configuration
