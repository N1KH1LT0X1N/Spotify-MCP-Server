# Spotify MCP Server - Repository Structure

**Last Updated:** November 17, 2025  
**Version:** 1.0.4  
**Status:** ✅ Clean & Production-Ready

---

## 📁 Directory Structure

```
spotify_mcp/
│
├── 📂 src/spotify_mcp/          # Source code
│   ├── __init__.py              # Package initialization (86 tools)
│   ├── server.py                # MCP server implementation
│   ├── spotify_client.py        # Spotify API client wrapper
│   ├── auth.py                  # Authentication & token management
│   └── tools/                   # Tool implementations (16 modules)
│       ├── albums.py            # 8 album tools
│       ├── artists.py           # 5 artist tools
│       ├── audiobooks.py        # 7 audiobook tools
│       ├── categories.py        # 2 category tools
│       ├── chapters.py          # 2 chapter tools
│       ├── episodes.py          # 6 episode tools
│       ├── genres.py            # 1 genre tool
│       ├── library.py           # 4 library tools
│       ├── markets.py           # 1 market tool
│       ├── playback.py          # 12 playback tools ⭐
│       ├── playlists.py         # 14 playlist tools
│       ├── queue.py             # 2 queue tools
│       ├── search.py            # 2 search tools
│       ├── shows.py             # 7 show tools
│       ├── tracks.py            # 5 track tools
│       └── user.py              # 8 user tools
│
├── 📂 tests/                    # Test suite
│   ├── test_auth.py             # Authentication tests
│   ├── test_integration.py      # Integration tests
│   ├── test_security.py         # Security tests
│   ├── test_mcp_server.py       # Comprehensive MCP tests ✅
│   ├── test_server_startup.py   # Server startup tests ✅
│   └── TEST_REPORT.md           # Test results documentation
│
├── 📂 scripts/                  # Utility scripts
│   ├── auto_auth.py             # Automated authentication
│   ├── diagnose_auth.py         # Authentication diagnostics
│   ├── enterprise_cli.py        # Enterprise features CLI
│   ├── generate_claude_config.py # Claude Desktop config generator
│   ├── verify_setup.py          # Setup verification
│   ├── verify_pretty_setup.py   # Pretty setup verification
│   └── README.md                # Scripts documentation
│
├── 📂 tools/                    # Developer tools
│   ├── setup_guide.py           # Interactive setup guide
│   ├── test_auth.py             # Authentication testing
│   ├── test_new_playlists.py    # Playlist feature tests
│   ├── verify_tools.py          # Tool verification (86 tools)
│   └── README.md                # Tools documentation
│
├── 📂 docs/                     # Documentation
│   ├── README.md                # Documentation index
│   ├── setup/                   # Setup guides
│   │   ├── GET_STARTED.md       # Getting started guide
│   │   ├── QUICK_SETUP.md       # Quick setup guide
│   │   └── troubleshooting.md   # Troubleshooting guide
│   └── examples/                # Usage examples
│
├── 📂 .archive/                 # Archived documentation
│   └── [Historical docs]        # Previous versions & plans
│
├── 📂 .github/                  # GitHub configuration
│   └── workflows/               # CI/CD workflows
│
├── 📄 README.md                 # Main project README ⭐
├── 📄 CHANGELOG.md              # Version history
├── 📄 CONTRIBUTING.md           # Contribution guidelines
├── 📄 SECURITY.md               # Security policy
├── 📄 STRUCTURE.md              # Production structure overview
├── 📄 LICENSE                   # MIT License
├── 📄 pyproject.toml            # Python project configuration
├── 📄 .env.example              # Environment variables template
├── 📄 .gitignore                # Git ignore rules
└── 📄 icon.svg                  # Project icon

```

---

## 🎯 Key Features

### ✅ 100% Spotify Web API Coverage
- **86 Tools** across **16 Categories**
- All endpoints implemented and tested
- Production-ready with comprehensive error handling

### 🧪 Comprehensive Testing
- Unit tests for authentication and security
- Integration tests for API interactions
- MCP server validation tests
- 100% test pass rate

### 📚 Complete Documentation
- Setup guides (quick start & detailed)
- API reference for all 86 tools
- Troubleshooting guides
- Example usage patterns

### 🛠️ Developer Tools
- Interactive setup wizard
- Authentication diagnostics
- Tool verification utilities
- Configuration generators

---

## 🚀 Quick Navigation

### For Users
- **Getting Started:** `docs/setup/GET_STARTED.md`
- **Quick Setup:** `docs/setup/QUICK_SETUP.md`
- **Troubleshooting:** `docs/setup/troubleshooting.md`

### For Developers
- **Source Code:** `src/spotify_mcp/`
- **Tests:** `tests/`
- **Contributing:** `CONTRIBUTING.md`

### For Maintainers
- **Version History:** `CHANGELOG.md`
- **Security Policy:** `SECURITY.md`
- **Project Structure:** `STRUCTURE.md`

---

## 📊 Repository Statistics

| Metric | Value |
|--------|-------|
| Total Tools | 86 |
| Tool Categories | 16 |
| API Coverage | 100% |
| Test Pass Rate | 100% |
| Python Files | 22 |
| Lines of Code | ~15,000+ |
| Documentation Pages | 10+ |

---

## 🔧 Development Workflow

1. **Setup Development Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -e .
   ```

2. **Run Tests**
   ```bash
   python tests/test_mcp_server.py
   python tests/test_server_startup.py
   ```

3. **Verify Tools**
   ```bash
   python tools/verify_tools.py
   ```

4. **Start Server**
   ```bash
   python -m spotify_mcp.server
   ```

---

## 🧹 Maintenance

### Files Excluded from Git
- `.env` - Environment variables (use `.env.example` as template)
- `.cache` - Spotify token cache
- `.venv/` - Virtual environment
- `__pycache__/` - Python cache
- `.coverage` - Test coverage data
- `.auth_audit.json` - Security audit logs

### Archived Content
Historical documentation and old implementation files are stored in `.archive/` for reference.

---

## 📝 Version Information

**Current Version:** 1.0.4  
**Release Date:** November 17, 2025  
**Latest Feature:** Get Recently Played Tracks (Player category)

See `CHANGELOG.md` for complete version history.

---

**Repository:** Clean, organized, and production-ready! ✅
