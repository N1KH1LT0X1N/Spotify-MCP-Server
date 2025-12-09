# 📁 Repository Structure

This document provides an overview of the Spotify MCP Server repository organization.

## Root Directory

```
spotify_mcp/
├── src/                    # Source code
├── tests/                  # Test suite
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── tools/                  # Setup and testing tools
├── infrastructure/         # Deployment configurations
├── monitoring/             # Monitoring and metrics
├── .archive/              # Historical documentation
├── .github/               # GitHub workflows and configs
├── README.md              # Project overview
├── CHANGELOG.md           # Version history
├── STATUS.md              # Current project status
├── SECURITY.md            # Security documentation
├── CONTRIBUTING.md        # Contribution guidelines
├── LICENSE                # MIT License
├── pyproject.toml         # Python project configuration
├── Dockerfile             # Container image definition
├── docker-compose.yml     # Multi-container setup
└── .gitignore            # Git ignore rules
```

## Source Code (`src/spotify_mcp/`)

Main application code:

```
src/spotify_mcp/
├── spotify_server.py      # Main FastMCP server (3,215 lines)
├── server.py              # Compatibility shim (157 lines)
├── auth.py                # OAuth 2.0 authentication
├── spotify_client.py      # Spotify API client wrapper
├── models.py              # Pydantic data models
├── resources.py           # MCP resource handlers
├── prompts.py             # MCP prompt templates
├── security.py            # Security and encryption
├── metrics_server.py      # Prometheus metrics
├── __init__.py           # Package initialization
└── tools/                # Tool implementations
    ├── playback.py       # Playback control (12 tools)
    ├── playlists.py      # Playlist management (12 tools)
    ├── albums.py         # Album operations (8 tools)
    ├── user.py           # User profile & top items (8 tools)
    ├── shows.py          # Podcast shows (7 tools)
    ├── episodes.py       # Podcast episodes (6 tools)
    ├── composite.py      # Multi-step operations (6 tools)
    ├── library.py        # Saved tracks (4 tools)
    ├── artists.py        # Artist info (4 tools)
    ├── categories.py     # Browse categories (2 tools)
    ├── queue.py          # Queue management (2 tools)
    ├── tracks.py         # Track details (2 tools)
    ├── search.py         # Search functionality (1 tool)
    └── markets.py        # Available markets (1 tool)
```

**Total**: 75 tools across 14 modules

## Tests (`tests/`)

Test suite with 100% pass rate:

```
tests/
├── test_mcp_server.py     # Main test suite (6 tests)
├── test_auth.py           # Authentication tests
├── test_spotify_client.py # Client wrapper tests
└── conftest.py            # Pytest configuration
```

## Documentation (`docs/`)

Comprehensive documentation:

```
docs/
├── API.md                 # Complete API reference
├── TOOLS.md              # All 75 tools documented
├── DEPLOYMENT.md         # Production deployment guide
├── MIGRATION_STATUS_V3.md # FastMCP implementation details
├── VALIDATION_REPORT.md  # Validation audit (99/100)
├── CLEANUP_SUMMARY.md    # Repository cleanup details
├── architecture/         # System design documents
│   ├── OVERVIEW.md
│   ├── DATA_FLOW.md
│   └── SECURITY.md
├── setup/                # Setup guides
│   ├── QUICK_SETUP.md
│   ├── authentication.md
│   └── troubleshooting.md
├── diagnostics/          # Diagnostic guides
└── enterprise/           # Enterprise features
```

## Utility Scripts (`scripts/`)

Helper scripts for development:

```
scripts/
├── diagnose_auth.py           # Authentication diagnostics
├── generate_claude_config.py  # Config generator
├── verify_pretty_setup.py     # Setup verification
├── verify_setup.py           # Basic setup check
├── auto_auth.py              # Automated OAuth flow
├── enterprise_cli.py         # Enterprise features
└── README.md                 # Script documentation
```

## Tools (`tools/`)

Setup and testing utilities:

```
tools/
├── setup_guide.py             # Interactive setup
├── test_auth.py              # Auth testing
├── verify_tools.py           # Tool registration check
├── test_all_endpoints.py     # Endpoint testing
├── test_mutation_endpoints.py # Write operation tests
├── test_new_playlists.py     # Playlist tests
└── README.md                 # Tool documentation
```

## Infrastructure (`infrastructure/`)

Deployment configurations:

```
infrastructure/
├── kubernetes/            # K8s manifests
├── terraform/            # Infrastructure as code
├── helm/                 # Helm charts
└── docker/              # Docker configs
```

## Monitoring (`monitoring/`)

Observability and metrics:

```
monitoring/
├── prometheus/           # Prometheus configs
├── grafana/             # Grafana dashboards
└── alerts/              # Alert rules
```

## Archive (`.archive/`)

Historical documentation (not for active use):

```
.archive/
├── BUILD_SUMMARY.md
├── CHANGELOG_v1.0.md
├── IMPLEMENTATION_SUMMARY.md
├── README_OLD.md
└── ... (various old docs)
```

## Key Files

### Root Configuration Files

- **`pyproject.toml`** - Python project metadata, dependencies, build configuration
- **`.env.example`** - Template for environment variables
- **`.gitignore`** - Git ignore patterns for cache, secrets, artifacts
- **`.dockerignore`** - Docker ignore patterns
- **`.pre-commit-config.yaml`** - Pre-commit hook configuration

### Docker Files

- **`Dockerfile`** - Production container image
- **`docker-compose.yml`** - Multi-container orchestration
- **`entrypoint.sh`** - Container startup script

### Documentation Files

- **`README.md`** - Project overview, quick start, features (162 lines)
- **`CHANGELOG.md`** - Version history with v2.0.0 release notes
- **`STATUS.md`** - Comprehensive project status (402 lines)
- **`SECURITY.md`** - Security features and OAuth implementation
- **`CONTRIBUTING.md`** - Contribution guidelines
- **`LICENSE`** - MIT License

## File Organization Principles

### ✅ Keep in Root
- Essential documentation (README, CHANGELOG, LICENSE)
- Configuration files (pyproject.toml, .env.example)
- Deployment files (Dockerfile, docker-compose.yml)
- Security and contribution docs

### 📁 Move to `docs/`
- API reference and technical documentation
- Architecture and design documents
- Setup guides and tutorials
- Validation and audit reports

### 🗄️ Archive in `.archive/`
- Old implementation summaries
- Historical migration notes
- Deprecated documentation
- Previous version READMEs

### 🚫 Never Commit (see `.gitignore`)
- Runtime cache (`.cache`, `__pycache__/`)
- Test artifacts (`htmlcov/`, `.coverage`)
- Security logs (`.auth_audit.json`)
- IDE configs (`.vscode/`, `.idea/`)
- Environment files (`.env` - only `.env.example`)

## Navigation Tips

### For Users
1. Start with `README.md` for overview
2. Follow `docs/setup/QUICK_SETUP.md` for installation
3. Check `docs/TOOLS.md` for available commands
4. Reference `docs/DEPLOYMENT.md` for production setup

### For Developers
1. Review `src/spotify_mcp/spotify_server.py` for main server
2. Check `src/spotify_mcp/tools/` for tool implementations
3. Read `docs/API.md` for API reference
4. See `tests/` for test examples
5. Review `docs/architecture/` for system design

### For Contributors
1. Read `CONTRIBUTING.md` for guidelines
2. Check `STATUS.md` for current state
3. Review `CHANGELOG.md` for version history
4. See `docs/VALIDATION_REPORT.md` for quality standards

## Clean Repository Commands

### Remove all cache and artifacts:
```bash
# PowerShell
Remove-Item -Path .cache,.coverage,.pytest_cache/,htmlcov/,__pycache__/ -Recurse -Force -ErrorAction SilentlyContinue

# Bash
rm -rf .cache .coverage .pytest_cache/ htmlcov/ **/__pycache__/
```

### Check repository cleanliness:
```bash
git status --ignored
```

### Verify no secrets in history:
```bash
git log -p | grep -i "client_secret\|api_key"
```

---

**Last Updated**: December 9, 2025  
**Repository Version**: v2.0.0  
**Structure Status**: ✅ Clean and Organized
