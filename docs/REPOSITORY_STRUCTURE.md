# Spotify MCP Server - Repository Structure

**Last Updated:** November 20, 2025  
**Version:** 1.3.0  
**Status:** ✅ Production-Grade with Enterprise Infrastructure

---

## 📁 Directory Structure

```
spotify_mcp/
│
├── 📂 src/spotify_mcp/               # Source code
│   ├── __init__.py                   # Package initialization (v1.3.0)
│   ├── server.py                     # MCP server with resources & prompts
│   ├── spotify_client.py             # Enhanced API client with metrics & caching
│   ├── auth.py                       # Authentication & token management
│   ├── prompts.py                    # 8 AI prompts for natural interaction
│   ├── resources.py                  # 8 MCP resources (playlists, library, etc.)
│   ├── metrics_server.py             # Prometheus metrics server
│   │
│   ├── tools/                        # 86 Tool implementations (16 modules)
│   │   ├── albums.py                 # 8 album tools
│   │   ├── artists.py                # 5 artist tools
│   │   ├── audiobooks.py             # 7 audiobook tools
│   │   ├── categories.py             # 2 category tools
│   │   ├── chapters.py               # 2 chapter tools
│   │   ├── episodes.py               # 6 episode tools
│   │   ├── genres.py                 # 1 genre tool
│   │   ├── library.py                # 4 library tools
│   │   ├── markets.py                # 1 market tool
│   │   ├── playback.py               # 12 playback tools ⭐
│   │   ├── playlists.py              # 14 playlist tools
│   │   ├── queue.py                  # 2 queue tools
│   │   ├── search.py                 # 2 search tools
│   │   ├── shows.py                  # 7 show tools
│   │   ├── tracks.py                 # 5 track tools (with 403 fix)
│   │   └── user.py                   # 8 user tools
│   │
│   ├── infrastructure/               # Production infrastructure 🏗️
│   │   ├── cache/                    # Intelligent caching (10-100x faster)
│   │   │   ├── decorators.py         # @cached decorator
│   │   │   ├── manager.py            # Cache orchestration
│   │   │   ├── memory.py             # In-memory cache
│   │   │   ├── redis.py              # Redis cache backend
│   │   │   ├── strategies.py         # Caching strategies
│   │   │   ├── warming.py            # Cache preloading
│   │   │   ├── invalidation.py       # Smart invalidation
│   │   │   └── statistics.py         # Performance metrics
│   │   │
│   │   ├── resilience/               # Fault tolerance & reliability
│   │   │   ├── circuit_breaker.py    # Circuit breaker pattern
│   │   │   ├── rate_limiter.py       # API rate limiting
│   │   │   ├── retry.py              # Exponential backoff retry
│   │   │   ├── fallback.py           # Graceful degradation
│   │   │   └── health_checks.py      # System health monitoring
│   │   │
│   │   ├── logging/                  # Structured logging
│   │   │   └── logger.py             # Production-grade logger
│   │   │
│   │   └── metrics/                  # Observability
│   │       ├── collectors.py         # Prometheus metrics
│   │       └── exporters.py          # Metrics exporters
│   │
│   ├── config/                       # Configuration management
│   │   └── settings.py               # Centralized settings
│   │
│   └── cli/                          # Beautiful CLI tool 🎨
│       ├── main.py                   # CLI entry point
│       ├── commands/                 # CLI commands
│       │   ├── playback.py           # Playback controls
│       │   ├── search.py             # Search commands
│       │   ├── playlist.py           # Playlist management
│       │   ├── library.py            # Library operations
│       │   ├── device.py             # Device management
│       │   ├── status.py             # Status display
│       │   └── interactive.py        # Interactive mode
│       └── utils.py                  # CLI utilities
│
├── 📂 tests/                         # Comprehensive test suite ✅
│   ├── test_mcp_server.py            # MCP server tests (6 tests)
│   ├── test_server_startup.py        # Startup tests (3 tests)
│   ├── test_caching_integration.py   # Caching system tests
│   ├── test_cli_integration.py       # CLI tests
│   ├── test_config_integration.py    # Configuration tests
│   ├── test_logging_integration.py   # Logging tests
│   ├── test_metrics_integration.py   # Metrics tests
│   └── TEST_REPORT.md                # Test results (100% pass rate)
│
├── 📂 tools/                         # Development utilities
│   ├── setup_guide.py                # Interactive setup wizard
│   ├── test_auth.py                  # Authentication testing (fixed)
│   ├── debug_audio_features.py       # 403 error debugging
│   ├── test_audio_features.py        # Audio features testing
│   ├── verify_tools.py               # Tool verification (86 tools, fixed)
│   └── README.md                     # Tools documentation
│
├── 📂 scripts/                       # Automation scripts
│   ├── auto_auth.py                  # Automated authentication
│   ├── diagnose_auth.py              # Auth diagnostics
│   ├── enterprise_cli.py             # Enterprise features
│   ├── generate_claude_config.py     # Config generator
│   └── verify_setup.py               # Setup verification
│
├── 📂 docs/                          # Documentation hub 📚
│   ├── INDEX.md                      # Complete documentation index ⭐
│   ├── REPOSITORY_STRUCTURE.md       # This file
│   │
│   ├── setup/                        # Installation guides
│   │   ├── GET_STARTED.md            # Step-by-step guide
│   │   ├── QUICK_SETUP.md            # 5-minute setup
│   │   └── troubleshooting.md        # Common issues
│   │
│   ├── troubleshooting/              # Problem resolution
│   │   └── AUDIO_FEATURES_403_FIX.md # Spotify API quota fix
│   │
│   ├── api/                          # API documentation
│   │   └── README.md                 # All 86 tools reference
│   │
│   ├── guides/                       # User guides
│   │   ├── authentication.md         # OAuth setup
│   │   ├── configuration.md          # Settings guide
│   │   └── best-practices.md         # Usage tips
│   │
│   ├── architecture/                 # System design 🏗️
│   │   ├── MCP_FEATURES.md           # MCP server features
│   │   ├── DATABASE_ASSESSMENT.md    # Data storage analysis
│   │   └── IMPLEMENTATION_TIERS.md   # Feature tiers
│   │
│   ├── development/                  # Developer docs
│   │   ├── README.md                 # Dev setup
│   │   ├── TESTING.md                # Test guide
│   │   └── STANDARDS.md              # Code standards
│   │
│   ├── planning/                     # Roadmaps & plans 🗺️
│   │   ├── PRIORITIZED_IMPLEMENTATION_PLAN.md
│   │   ├── IMPLEMENTATION_ROADMAP.md (Part 1-5)
│   │   └── [112-week implementation roadmap]
│   │
│   └── audits/                       # Reports & audits 📊
│       ├── PHASE1_SUMMARY.md         # Initial review
│       ├── PHASE1_AUDIT.md           # Detailed audit
│       ├── PHASE2_4_IMPLEMENTATION.md # Infrastructure rollout
│       ├── MCP_COMPLIANCE_AUDIT.md   # Protocol compliance
│       ├── EXECUTIVE_SUMMARY.md      # High-level overview
│       ├── FINAL_PERFECTION_REPORT.md # v1.3.0 achievement
│       ├── IMPLEMENTATION_COMPLETE.md # Completion report
│       └── IMPLEMENTATION_SUMMARY.md  # Feature summary
│
├── 📂 infrastructure/                # DevOps infrastructure 🐳
│   ├── README.md                     # Infrastructure guide
│   ├── grafana/                      # Grafana dashboards
│   │   └── provisioning/             # Dashboard configs
│   └── prometheus/                   # Prometheus setup
│       └── prometheus.yml            # Metrics config
│
├── 📂 monitoring/                    # Observability
│   ├── grafana/                      # Custom dashboards
│   │   └── dashboard.json            # Spotify MCP dashboard
│   └── prometheus/                   # Alert rules
│       └── alerts/                   # Critical alerts
│
├── 📂 .github/                       # GitHub configuration
│   └── workflows/                    # CI/CD pipelines
│       ├── test.yml                  # Automated testing
│       ├── quality.yml               # Code quality checks
│       ├── docker.yml                # Docker builds
│       └── release.yml               # Release automation
│
├── 📂 .archive/                      # Historical content
│   └── [Archived documentation]      # Previous versions
│
├── 🐳 Docker Support                 # Containerization
│   ├── Dockerfile                    # Multi-stage Docker build
│   ├── docker-compose.yml            # Full stack deployment
│   ├── .dockerignore                 # Docker ignore rules
│   └── entrypoint.sh                 # Container entry point
│
├── 📄 README.md                      # Main project README ⭐
├── 📄 CHANGELOG.md                   # Version history
├── 📄 CONTRIBUTING.md                # Contribution guide
├── 📄 SECURITY.md                    # Security policy
├── 📄 LICENSE                        # MIT License
├── 📄 pyproject.toml                 # Project config (v1.3.0)
├── 📄 .env.example                   # Environment template
├── 📄 .gitignore                     # Git ignore rules
├── 📄 .pre-commit-config.yaml        # Pre-commit hooks
└── 📄 icon.svg                       # Project icon

```

---

## 🎯 Key Features

### ✅ 100% Spotify Web API Coverage
- **86 Tools** across **16 Categories**
- **8 Resources** for rich context (playlists, library, devices, etc.)
- **8 AI Prompts** for natural language interaction
- All endpoints implemented, tested, and production-ready

### 🏗️ Enterprise Infrastructure (v1.3.0)
- **Caching System:** 10-100x performance improvement (Redis/Memory)
- **Resilience:** Circuit breakers, rate limiting, retry logic, health checks
- **Observability:** Prometheus metrics, Grafana dashboards
- **Logging:** Structured JSON logging with correlation IDs
- **Configuration:** Centralized settings management

### 🎨 Beautiful CLI Tool
- Interactive terminal interface with Rich library
- Commands for playback, search, playlists, library
- Real-time status display and device management

### 🐳 DevOps Ready
- Multi-stage Dockerfile for optimized builds
- Docker Compose with Prometheus & Grafana
- GitHub Actions CI/CD (test, quality, docker, release)
- Pre-commit hooks for code quality

### 🧪 Comprehensive Testing
- Unit tests for all components
- Integration tests for infrastructure
- MCP protocol compliance validation
- 100% test pass rate

### 📚 Complete Documentation
- Setup guides (quick start & detailed)
- API reference for all 86 tools
- Architecture documentation
- 112-week implementation roadmap
- Troubleshooting guides (including 403 API quota fix)

---

## 🚀 Quick Navigation

### For Users
- **Getting Started:** `docs/setup/GET_STARTED.md`
- **Quick Setup (5 min):** `docs/setup/QUICK_SETUP.md`
- **Troubleshooting:** `docs/setup/troubleshooting.md`
- **Fix 403 Errors:** `docs/troubleshooting/AUDIO_FEATURES_403_FIX.md`
- **All Documentation:** `docs/INDEX.md`

### For Developers
- **Source Code:** `src/spotify_mcp/`
- **Infrastructure:** `src/spotify_mcp/infrastructure/`
- **CLI Tools:** `src/spotify_mcp/cli/`
- **Tests:** `tests/`
- **Contributing:** `CONTRIBUTING.md`
- **Development Guide:** `docs/development/README.md`

### For DevOps
- **Docker Setup:** `Dockerfile`, `docker-compose.yml`
- **Infrastructure:** `infrastructure/README.md`
- **CI/CD:** `.github/workflows/`
- **Monitoring:** `monitoring/grafana/`, `monitoring/prometheus/`

### For Maintainers
- **Version History:** `CHANGELOG.md`
- **Security Policy:** `SECURITY.md`
- **Audit Reports:** `docs/audits/`
- **Roadmaps:** `docs/planning/`

---

## 📊 Repository Statistics

| Metric | Value |
|--------|-------|
| Version | 1.3.0 |
| Total Tools | 86 |
| Resources | 8 |
| Prompts | 8 |
| Tool Categories | 16 |
| API Coverage | 100% |
| Test Pass Rate | 100% |
| Infrastructure Modules | 4 (cache, resilience, logging, metrics) |
| CLI Commands | 7 |
| Python Files | 70+ |
| Lines of Code | ~25,000+ |
| Documentation Pages | 50+ |
| GitHub Actions Workflows | 4 |

---

## 🔧 Development Workflow

1. **Setup Development Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or: source .venv/bin/activate  # Linux/Mac
   pip install -e ".[dev,all]"
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Spotify credentials
   python -m spotify_mcp.auth
   ```

3. **Run Tests**
   ```bash
   # All tests
   pytest
   
   # Specific test suites
   python tests/test_mcp_server.py
   python tests/test_server_startup.py
   python tests/test_caching_integration.py
   ```

4. **Verify Tools & Setup**
   ```bash
   python tools/verify_tools.py        # Verify 86 tools
   python tools/test_auth.py           # Test authentication
   python scripts/verify_setup.py      # Complete setup check
   ```

5. **Start Server**
   ```bash
   # Standard mode
   python -m spotify_mcp.server
   
   # With CLI
   spotify-mcp-cli status
   spotify-mcp-cli playback play
   ```

6. **Docker Development**
   ```bash
   # Build and run with monitoring
   docker-compose up -d
   
   # View logs
   docker-compose logs -f spotify-mcp
   
   # Access Grafana: http://localhost:3000
   # Access Prometheus: http://localhost:9090
   ```

---

## 🧹 Maintenance

### Files Excluded from Git
- `.env` - Environment variables (use `.env.example` as template)
- `.cache` - Spotify token cache
- `.auth_audit.json` - Security audit logs
- `.venv/` - Virtual environment
- `__pycache__/` - Python cache
- `.coverage` - Test coverage data
- `htmlcov/` - Coverage HTML reports
- `.pytest_cache/` - Pytest cache
- `*.pyc` - Compiled Python files

### Archived Content
Historical documentation and old implementation files are stored in `.archive/` for reference.

### Configuration Files
- `.pre-commit-config.yaml` - Git pre-commit hooks
- `.dockerignore` - Docker build exclusions
- `pyproject.toml` - Python project configuration
- `.gitignore` - Git ignore rules

---

## 📝 Version Information

**Current Version:** 1.3.0  
**Release Date:** November 19, 2025  
**Latest Features:** 
- Production-grade infrastructure (caching, resilience, metrics)
- 8 MCP Resources and 8 AI Prompts
- Beautiful CLI tool with Rich
- Docker & monitoring support
- Bug fixes for audio features 403 error

See `CHANGELOG.md` for complete version history.

---

## 🏆 Project Milestones

- **v1.0.0** - Initial release with 86 tools
- **v1.2.0** - Phase 1 audit and comprehensive testing
- **v1.3.0** - Enterprise infrastructure and MCP compliance ⭐

---

**Repository:** Production-ready with enterprise-grade infrastructure! 🚀✅

**Documentation Index:** See `docs/INDEX.md` for complete navigation.
