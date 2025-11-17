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
│           ├── albums.py            # Album operations
│           ├── artists.py           # Artist operations
│           ├── audiobooks.py        # Audiobook operations
│           ├── categories.py        # Category browsing
│           ├── chapters.py          # Audiobook chapters
│           ├── episodes.py          # Podcast episodes
│           ├── genres.py            # Genre discovery
│           ├── markets.py           # Market information
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
├── 🔧 scripts/                       # Development scripts
│   ├── README.md                    # Scripts documentation
│   ├── generate_claude_config.py    # Generate Claude config
│   ├── verify_pretty_setup.py       # Verify setup
│   ├── diagnose_auth.py             # Auth diagnostics
│   ├── enterprise_cli.py            # Enterprise CLI
│   ├── verify_setup.py              # Setup verification
│   └── auto_auth.py                 # Auto auth (not recommended)
│
├── 🛠️ tools/                         # Utility tools
│   ├── verify_tools.py              # Tool verification script
│   ├── test_auth.py                 # Standalone auth testing
│   └── setup_guide.py               # Interactive setup assistant
│
├── ⚙️ .github/                       # GitHub configuration
│   ├── workflows/                   # CI/CD workflows
│   │   └── test.yml                 # Automated testing
│   └── requirements-dev.txt         # Development dependencies
│
├── 🗄️ .archive/                     # Archived old files
│   └── ...                          # Old documentation
│
├── 📄 Root Files
│   ├── README.md                    # Project overview & setup
│   ├── CHANGELOG.md                 # Version history
│   ├── CONTRIBUTING.md              # Contribution guidelines
│   ├── SECURITY.md                  # Security policy
│   ├── STRUCTURE.md                 # This file - repository structure
│   ├── LICENSE                      # MIT License
│   ├── pyproject.toml               # Package configuration
│   ├── .env.example                 # Environment template (detailed)
│   ├── .gitignore                   # Git ignore rules
│   ├── .pre-commit-config.yaml      # Pre-commit hooks
│   └── icon.svg                     # Spotify branding (Claude Desktop)
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
| **Documentation** | 20 files | Setup, development, enterprise guides |
| **Source Code** | 19 files | Main package + 14 tool modules |
| **Tests** | 4 files | Comprehensive test suite |
| **Scripts** | 6 files | Development and diagnostic tools |
| **Tools** | 3 files | Utility and verification tools |
| **Config** | 8 files | Project and environment configuration |
| **Total** | ~60 files | Clean, organized structure |
| **Tests** | 4 files | 69 tests (100% pass rate) |
| **Scripts** | 7 files | Setup, diagnostics, enterprise tools |
| **Config** | 6 files | Package, CI/CD, pre-commit |
| **Root** | 6 files | README, SECURITY, CONTRIBUTING, etc. |

**Total Tracked Files:** ~55 files (clean and organized!)

## 🎯 Key Features

### ✅ Beginner-Friendly
- **Interactive setup guide** (`setup_guide.py`) - step-by-step wizard
- **Standalone auth test** (`test_auth.py`) - verify credentials easily
- **Comprehensive docs** with copy-paste examples
- **Detailed troubleshooting** for common issues

### ✅ Production-Ready Architecture
- **Organized documentation** in `docs/` folder
- **All source code** in `src/spotify_mcp/`
- **Complete test suite** (69 tests, 100% pass rate)
- **Utility scripts** for diagnostics and setup
- **Clean root** with only essential files

### ✅ Professional Setup
- **CI/CD pipeline** with GitHub Actions
- **Pre-commit hooks** for code quality
- **46 production tools** across 9 categories
- **65 production tools** across 14 categories
- **77 production tools** across 16 categories
- **Enterprise features** (keychain, audit logging, multi-profile)

### ✅ Developer Experience
- **Clear contribution guide** with examples
- **Comprehensive API docs** and patterns
- **Active development** with roadmap
- **Type hints** and modern Python practices

## 🚀 Getting Started

**New to this project?**
1. Run `python setup_guide.py` for interactive setup
2. Or see [docs/setup/QUICK_SETUP.md](docs/setup/QUICK_SETUP.md) for fast config

**Want to contribute?**
1. Check [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
2. See Phase 2 roadmap for feature ideas
3. Open an issue to discuss your idea

**Need help?**
1. [docs/setup/troubleshooting.md](docs/setup/troubleshooting.md) for common issues
2. [docs/README.md](docs/README.md) for all documentation

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
