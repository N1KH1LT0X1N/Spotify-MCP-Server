# Troubleshooting Guide

Common issues and their solutions for the Spotify MCP Server.

## 🔴 Critical Issues We Encountered (And Fixed!)

### Issue 1: ModuleNotFoundError: No module named 'spotify_mcp'

**Symptom:**
```
C:\Users\admin\anaconda3\python.exe: Error while finding module specification for 'spotify_mcp.server' 
(ModuleNotFoundError: No module named 'spotify_mcp')
```

**Cause:**
Python cannot find the `spotify_mcp` module because the `src` directory is not in Python's module search path.

**Solution:**
Add the `src` directory to `PYTHONPATH`:

**For Windows (PowerShell):**
```powershell
$env:PYTHONPATH = "c:\path\to\spotify_mcp\src"
```

**For Claude Desktop config:**
```json
{
  "mcpServers": {
    "spotify": {
      "command": "C:\\Users\\admin\\anaconda3\\python.exe",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "PYTHONPATH": "c:\\Users\\admin\\OneDrive\\Documents\\GitHub\\spotify_mcp\\src",
        "SPOTIFY_CLIENT_ID": "your_client_id",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback"
      }
    }
  }
}
```

---

### Issue 2: ERR_CONNECTION_REFUSED on 127.0.0.1:8888

**Symptom:**
Browser shows "This site can't be reached" or "ERR_CONNECTION_REFUSED" after clicking "Agree" on Spotify authorization.

**This is NORMAL and EXPECTED!** ✅

**Explanation:**
The authentication flow uses a **manual OAuth redirect** - there's no local server listening on port 8888. Instead:

1. Spotify redirects to `http://127.0.0.1:8888/callback?code=...`
2. Browser shows connection refused (because nothing is listening)
3. The authorization **code is in the URL** - that's what matters!

**What to do:**
1. **Don't panic** - this is correct behavior
2. **Look at your browser's address bar**
3. **Copy the ENTIRE URL** (including `?code=...`)
4. **Paste it** back to the terminal/application prompting for it

**Example URL:**
```
http://127.0.0.1:8888/callback?code=AQCnf4jUZLh...very_long_code...
```

---

### Issue 3: "Unexpected token" / Invalid JSON errors in Claude Desktop

**Symptom:**
```
MCP spotify: Unexpected token 'P', "Paste the "... is not valid JSON
MCP spotify: Unexpected token 'O', "Opening br"... is not valid JSON
MCP spotify: Unexpected token 'A', "After auth"... is not valid JSON
```

**Cause:**
The authentication prompts were being printed to **stdout**, which interferes with MCP's JSON-RPC protocol over stdin/stdout.

**Solution (Fixed in code):**
We modified `src/spotify_mcp/auth.py` to print authentication prompts to **stderr** instead of stdout:

```python
def _authenticate(self) -> str:
    import sys
    
    # Write to stderr instead of stdout to avoid interfering with MCP JSON-RPC
    def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)
    
    eprint("\n=== Spotify Authentication Required ===")
    eprint("Opening browser for authentication...")
    # ... rest of authentication flow uses eprint()
```

**If you still see this:**
1. Make sure you have the latest version of `src/spotify_mcp/auth.py`
2. Restart Claude Desktop after updating the code

---

### Issue 4: Tokens not being saved to .env file

**Symptom:**
Authentication completes successfully, but `.env` file still shows empty token fields:
```
SPOTIFY_ACCESS_TOKEN=
SPOTIFY_REFRESH_TOKEN=
SPOTIFY_TOKEN_EXPIRES_AT=
```

**Cause:**
The `SpotifyAuthManager` was using `os.getcwd()` to find the `.env` file, but the current working directory might not be the project root.

**Solution (Fixed in code):**
We updated `src/spotify_mcp/auth.py` to search for the `.env` file in parent directories:

```python
def __init__(self):
    # Find .env file - check current directory first, then parent directories
    current_dir = os.getcwd()
    env_file = os.path.join(current_dir, ".env")
    
    # If .env not found in cwd, try to find project root
    if not os.path.exists(env_file):
        # Look for .env by going up directories until we find it or hit root
        search_dir = current_dir
        for _ in range(5):  # Search up to 5 levels
            test_path = os.path.join(search_dir, ".env")
            if os.path.exists(test_path):
                env_file = test_path
                break
            parent = os.path.dirname(search_dir)
            if parent == search_dir:  # Hit root
                break
            search_dir = parent
    
    self.env_file = env_file
```

**Verification:**
After authentication, your `.env` should look like:
```properties
SPOTIFY_ACCESS_TOKEN='BQAZLohFiEeh2vBjTM7ckE3yn...'
SPOTIFY_REFRESH_TOKEN='AQDBMnJIU6T6WqbO42YJ8oLU...'
SPOTIFY_TOKEN_EXPIRES_AT='1761853022'
```

---

### Issue 5: "localhost" vs "127.0.0.1" redirect URI

**Symptom:**
Spotify API returns an error about invalid redirect URI, even though it looks correct.

**Cause:**
Spotify's API documentation now explicitly requires using **127.0.0.1** (IPv4 address) instead of `localhost` for loopback addresses.

**Solution:**
Use `http://127.0.0.1:8888/callback` everywhere:

1. **In your `.env` file:**
   ```properties
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
   ```

2. **In Spotify Developer Dashboard:**
   - Go to https://developer.spotify.com/dashboard
   - Edit your app settings
   - Add redirect URI: `http://127.0.0.1:8888/callback`
   - Click Save

3. **In Claude Desktop config:**
   ```json
   "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback"
   ```

**Note:** We've updated all documentation and default values to use `127.0.0.1`.

---

### Issue 6: "Could not load app settings" / UTF-8 BOM in Claude Desktop Config

**Symptom:**
Claude Desktop shows an error on startup:
```
Could not load app settings
There was an error reading or parsing claude_desktop_config.json: Unexpected token "," "/" "m"... is not valid JSON
```

**Cause:**
The configuration file `claude_desktop_config.json` has a UTF-8 BOM (Byte Order Mark) - three invisible bytes at the start of the file that Claude Desktop's JSON parser cannot handle. This commonly happens when editing the file with PowerShell's `Set-Content` command or certain text editors.

**Solution:**
Remove the BOM from the file:

**Windows (PowerShell):**
```powershell
$content = Get-Content "$env:APPDATA\Claude\claude_desktop_config.json" -Raw
[System.IO.File]::WriteAllText("$env:APPDATA\Claude\claude_desktop_config.json", $content, (New-Object System.Text.UTF8Encoding $false))
```

**macOS/Linux:**
```bash
# Check if BOM exists
file ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Remove BOM if present
sed -i '1s/^\xEF\xBB\xBF//' ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Prevention:**
- Edit the config file with **VS Code**, **Notepad++**, or similar editors
- **Avoid PowerShell's `Set-Content`** - it adds BOM by default
- If using PowerShell, use `[System.IO.File]::WriteAllText()` with UTF-8 encoding (no BOM)

**Verification:**
After removing the BOM, restart Claude Desktop. It should open without errors.

---

## 🟡 Common Issues

### Authentication Required Every Time

**Symptom:**
Server asks for authentication on every run, even though you've authenticated before.

**Causes & Solutions:**

1. **Tokens not saved to `.env`**
   - Check if your `.env` file has the token values
   - Run the test script: `python test_auth.py`

2. **Tokens expired and refresh failed**
   - Delete the old tokens from `.env`
   - Re-authenticate: `python test_auth.py`

3. **Wrong working directory**
   - Make sure you're running from the project root
   - Or use PYTHONPATH as shown above

---

### "No active device" Error

**Symptom:**
```json
{
  "error": "NO_ACTIVE_DEVICE",
  "message": "Player command failed: No active device found"
}
```

**Cause:**
Spotify needs an active device to control playback.

**Solution:**
1. Open Spotify on any device (desktop, mobile, web player)
2. Start playing something
3. Try the command again

**Note:** The device doesn't need to be actively playing - just opened and logged in.

---

### "Premium Required" Error

**Symptom:**
Commands like `play`, `pause`, `skip` fail with premium required error.

**Cause:**
Spotify's Web API only allows playback control with Premium accounts.

**What Works Without Premium:**
- ✅ Search
- ✅ Get recommendations
- ✅ Library management (save/remove tracks)
- ✅ Playlist operations (create, modify)
- ✅ User profile and stats

**What Requires Premium:**
- ❌ Play/pause/skip
- ❌ Volume control
- ❌ Device transfer
- ❌ Seek position
- ❌ Shuffle/repeat

---

### Rate Limit Errors

**Symptom:**
```json
{
  "error": "Rate limit exceeded. Retry after 2 seconds"
}
```

**Cause:**
Making too many API requests in a short time.

**Solution:**
The server automatically handles rate limits with exponential backoff. Just wait a moment and try again.

---

### Token Refresh Failed

**Symptom:**
```
Error refreshing token: ...
Re-authenticating...
```

**Cause:**
The refresh token is invalid or expired (rare, but can happen).

**Solution:**
1. Delete tokens from `.env`:
   ```properties
   SPOTIFY_ACCESS_TOKEN=
   SPOTIFY_REFRESH_TOKEN=
   SPOTIFY_TOKEN_EXPIRES_AT=
   ```
2. Re-authenticate: `python test_auth.py`

---

## 🔧 Diagnostic Commands

### Verify Setup
```bash
python verify_setup.py
```
Checks Python version, dependencies, and `.env` configuration.

### Test Authentication
```bash
python test_auth.py
```
Authenticates with Spotify and verifies tokens are saved.

### Check Environment Variables
**Windows:**
```powershell
cd c:\path\to\spotify_mcp
$env:PYTHONPATH = "src"
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(f'Client ID: {os.getenv(\"SPOTIFY_CLIENT_ID\")[:10]}...'); print(f'Redirect: {os.getenv(\"SPOTIFY_REDIRECT_URI\")}'); print(f'Token: {\"Set\" if os.getenv(\"SPOTIFY_ACCESS_TOKEN\") else \"Not set\"}')"
```

### Test Module Import
```bash
python -c "import sys; sys.path.insert(0, 'src'); from spotify_mcp.auth import get_spotify_client; print('✓ Module imports successfully')"
```

---

## 📋 Pre-Flight Checklist

Before reporting an issue, verify:

- [ ] Python 3.10 or higher installed
- [ ] All dependencies installed (`pip install -e .`)
- [ ] `.env` file exists with correct credentials
- [ ] Redirect URI in Spotify Dashboard matches `.env` (use `127.0.0.1`, not `localhost`)
- [ ] PYTHONPATH is set correctly (if running manually)
- [ ] Authenticated at least once (`python test_auth.py`)
- [ ] Tokens are saved in `.env` file

---

## 🆘 Getting Help

If you're still stuck after checking this guide:

1. **Run diagnostics:**
   ```bash
   python verify_setup.py
   python test_auth.py
   ```

2. **Check Claude Desktop logs** (if using with Claude):
   - **Windows:** `%LOCALAPPDATA%\Claude\logs`
   - **macOS:** `~/Library/Logs/Claude/mcp*.log`
   - **Linux:** `~/.config/Claude/logs`

3. **Enable debug output:**
   Add to your environment:
   ```bash
   export SPOTIPY_TRACE=1
   ```

4. **Verify Spotify API status:**
   Check https://developer.spotify.com/status

5. **Create an issue** with:
   - Operating system
   - Python version
   - Output from `scripts/verify_setup.py`
   - Error messages (without credentials!)
   - Steps to reproduce

---

## ✅ Success Indicators

You know everything is working when:

✅ `python scripts/verify_setup.py` shows all checks passed  
✅ `python test_auth.py` successfully authenticates  
✅ `.env` file contains long token strings  
✅ Claude Desktop shows Spotify tools available (🔌 icon)  
✅ Commands execute without errors  

Happy listening! 🎵
