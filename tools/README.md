# 🛠️ Utility Tools

Helper tools for setup, testing, and verification of the Spotify MCP Server.

## Tools

### `setup_guide.py`

**Interactive setup assistant** - Guides you through the complete setup process.

**Usage**:
```bash
python tools/setup_guide.py
```

**Features**:
- Step-by-step configuration
- Credential validation
- Environment setup
- Claude Desktop integration
- Troubleshooting help

---

### `test_auth.py`

**Standalone authentication testing** - Test your Spotify OAuth setup.

**Usage**:
```bash
python tools/test_auth.py
```

**Features**:
- Validates credentials
- Tests OAuth flow
- Token refresh testing
- Clear error messages
- No MCP server required

---

### `verify_tools.py`

**Tool registration verification** - Confirms all 58 tools are properly registered.

**Usage**:
```bash
python tools/verify_tools.py
```

**Output**:
```
🎵 Spotify MCP Server - Tool Verification

Playback Control............ 11 tools
Search & Discovery..........  2 tools
Library Management..........  4 tools
[...all categories...]
Total....................... 58 tools

✅ All 58 tools successfully registered!
```

---

## Quick Commands

```bash
# Interactive setup
python tools/setup_guide.py

# Test authentication
python tools/test_auth.py

# Verify tool registration
python tools/verify_tools.py
```

---

## Related

For development and diagnostic scripts, see [scripts/README.md](../scripts/README.md).

For documentation, see [docs/README.md](../docs/README.md).
