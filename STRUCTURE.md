# 📁 Repository Structure

Clean and organized structure of the Spotify MCP Server project.

```
spotify_mcp/
│
├── 📚 docs/                          # All documentation
│   ├── README.md                     # Documentation index
│   ├── setup/                        # Setup guides
│   │   ├── QUICK_SETUP.md           # Copy-paste config (fastest!)
│   │   ├── GET_STARTED.md           # Visual setup guide
│   │   ├── QUICKSTART.md            # Detailed setup
│   │   ├── CLAUDE_DESKTOP_SETUP.md  # Claude configuration
│   │   ├── authentication.md         # OAuth setup
│   │   └── troubleshooting.md        # Common issues
│   ├── development/                  # Development docs
│   │   ├── roadmap.md               # Project roadmap
│   │   ├── PHASE_0_SUMMARY.md       # Testing complete
│   │   ├── PRETTY_SETUP_SUMMARY.md  # Claude integration
│   │   ├── TEST_FIXES_COMPLETE.md   # Test details
│   │   └── SECURITY_AUDIT.md        # Security audit report
│   ├── enterprise/                   # Enterprise features
│   │   ├── security.md              # Security guide
│   │   ├── implementation.md         # Deployment guide
│   │   └── quickstart.md            # Quick enterprise setup
│   └── diagnostics/                  # Diagnostic tools
│       ├── auth-enhancements.md      # Auth improvements
│       └── tools-comparison.md       # Tools reference
│
├── 📦 src/                           # Source code
│   └── spotify_mcp/                  # Main package
│       ├── __init__.py              # Package init
│       ├── server.py                # MCP server
│       ├── auth.py                  # OAuth authentication
│       ├── spotify_client.py        # Spotify API wrapper
│       ├── security.py              # Enterprise security
│       └── tools/                   # MCP tool implementations
│           ├── __init__.py
│           ├── playback.py          # Playback control
│           ├── search.py            # Search & discovery
│           ├── library.py           # Library management
│           ├── playlists.py         # Playlist operations
│           ├── queue.py             # Queue management
│           └── user.py              # User info
│
├── 🧪 tests/                         # Test suite (69 tests, 100% pass)
│   ├── conftest.py                  # Pytest configuration
│   ├── test_auth.py                 # Auth tests (24 tests)
│   ├── test_security.py             # Security tests (35 tests)
│   └── test_integration.py          # Integration tests (10 tests)
│
├── 🔧 scripts/                       # Utility scripts
│   ├── README.md                    # Scripts documentation
│   ├── generate_claude_config.py    # Generate Claude config
│   ├── verify_pretty_setup.py       # Verify setup
│   ├── diagnose_auth.py             # Auth diagnostics
│   ├── enterprise_cli.py            # Enterprise CLI
│   ├── verify_setup.py              # Setup verification
│   └── auto_auth.py                 # Auto auth (not recommended)
│
├── ⚙️ .github/                       # GitHub configuration
│   └── workflows/                   # CI/CD workflows
│       └── test.yml                 # Automated testing
│
├── 🗄️ .archive/                     # Archived old files
│   └── ...                          # Old documentation
│
├── 📄 Root Files
│   ├── README.md                    # Project overview
│   ├── CONTRIBUTING.md              # Contribution guidelines
│   ├── SECURITY.md                  # Security policy
│   ├── STRUCTURE.md                 # This file - repository structure
│   ├── LICENSE                      # MIT License
│   ├── pyproject.toml               # Package configuration
│   ├── .env.example                 # Environment template
│   ├── .gitignore                   # Git ignore rules
│   ├── .pre-commit-config.yaml      # Pre-commit hooks
│   ├── icon.svg                     # Spotify branding (Claude Desktop)
│   └── requirements-dev.txt         # Dev dependencies
│
└── 🔒 Generated/Runtime Files
    ├── .env                         # Your credentials (git-ignored)
    ├── .cache                       # Spotify token cache (git-ignored)
    ├── .auth_audit.json             # Security audit log (git-ignored)
    ├── .venv/                       # Virtual environment (git-ignored)
    ├── .pytest_cache/               # Pytest cache (git-ignored)
    ├── .coverage                    # Coverage data (git-ignored)
    └── htmlcov/                     # Coverage report (git-ignored)
```

## 📊 File Count Summary

| Category | Count | Description |
|----------|-------|-------------|
| **Documentation** | 16 files | Setup, development, enterprise guides |
| **Source Code** | 11 files | Main package + 6 tool modules |
| **Tests** | 4 files | 69 tests (100% pass rate) |
| **Scripts** | 7 files | Setup, diagnostics, enterprise tools |
| **Config** | 6 files | Package, CI/CD, pre-commit |
| **Root** | 6 files | README, SECURITY, CONTRIBUTING, etc. |

**Total Tracked Files:** ~50 files (clean and organized!)

## 🎯 Key Features

### ✅ Clean Structure
- **Organized documentation** in `docs/` folder
- **All source code** in `src/spotify_mcp/`
- **Complete test suite** in `tests/`
- **Utility scripts** in `scripts/`
- **Minimal root directory** (only 4 essential files)

### ✅ Professional Setup
- **CI/CD pipeline** with GitHub Actions
- **Pre-commit hooks** for code quality
- **Comprehensive tests** (69 tests, 86% security coverage)
- **Enterprise features** (keychain, audit logging, multi-profile)

### ✅ Great Documentation
- **Quick setup guides** for fast onboarding
- **Detailed troubleshooting** for common issues
- **Enterprise guides** for advanced features
- **Development docs** for contributors

## 🚀 Getting Started

1. **First time?** Start with [docs/setup/QUICK_SETUP.md](docs/setup/QUICK_SETUP.md)
2. **Want details?** See [docs/setup/GET_STARTED.md](docs/setup/GET_STARTED.md)
3. **Need help?** Check [docs/setup/troubleshooting.md](docs/setup/troubleshooting.md)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code style guidelines
- Testing requirements
- Pull request process
- Development setup

## 📝 Notes

- **No build artifacts** tracked in git
- **Security files** (.env, .cache, .auth_audit.json) are git-ignored
- **Old documentation** archived in `.archive/` folder
- **Test coverage reports** in `htmlcov/` (git-ignored)
