# 📚 Spotify MCP Server Documentation

> **Current Version:** 2.0.0 | **Tools:** 75 (69 standard + 6 composite) | **Status:** Production Ready

---

## 🚀 Getting Started

| Guide | Description |
|-------|-------------|
| [Quick Setup](setup/QUICK_SETUP.md) | 5-minute setup with Claude Desktop |
| [Authentication](setup/authentication.md) | OAuth setup and token management |
| [Troubleshooting](setup/troubleshooting.md) | Common issues and solutions |

---

## 📖 Core Reference

| Document | Description |
|----------|-------------|
| [Tool Reference](TOOLS.md) | Complete list of all 75 tools with examples |
| [API Reference](API.md) | Resources, prompts, schemas, and authentication |
| [Architecture](architecture/OVERVIEW.md) | System design and technical decisions |
| [Repository Structure](REPOSITORY_STRUCTURE.md) | File organization and navigation guide |

---

## 🔧 Advanced Topics

| Document | Description |
|----------|-------------|
| [Deployment Guide](DEPLOYMENT.md) | Production deployment (Docker, K8s, local) |
| [Migration Status](MIGRATION_STATUS_V3.md) | FastMCP v3.0 implementation details |
| [Validation Report](VALIDATION_REPORT.md) | Comprehensive quality audit (99/100) |
| [Cleanup Summary](CLEANUP_SUMMARY.md) | Repository cleanup and organization |
| [Enterprise Features](enterprise/README.md) | Metrics, logging, and CLI tools |
| [Diagnostics](diagnostics/tools-comparison.md) | Diagnostic tools and comparisons |

---

## 🚀 Roadmap

| Document | Description |
|----------|-------------|
| [**v3.0.0 Improvements**](IMPROVEMENTS.md) | FastMCP migration plan |

---

## 📁 Repository Structure

```
spotify_mcp/
├── src/spotify_mcp/       # Main source code
│   ├── server.py          # MCP server entry point
│   ├── auth.py            # OAuth authentication
│   ├── spotify_client.py  # API wrapper with caching
│   ├── tools/             # 75 tool implementations
│   ├── cli/               # Command-line interface
│   └── infrastructure/    # Caching, logging, metrics
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── docs/                  # Documentation (you are here)
└── tools/                 # Development & testing tools
```

---

## 🔗 Quick Links

- **Main README:** [../README.md](../README.md)
- **Contributing:** [../CONTRIBUTING.md](../CONTRIBUTING.md)
- **Security:** [../SECURITY.md](../SECURITY.md)
- **Changelog:** [../CHANGELOG.md](../CHANGELOG.md)

---

## ⚠️ Deprecated Features (Nov 27, 2024)

Spotify deprecated these APIs for development mode apps:
- ~~Audio Features & Analysis~~
- ~~Recommendations & Genre Seeds~~
- ~~Related Artists~~
- ~~Featured Playlists & Category Playlists~~
- ~~Audiobooks & Chapters~~ (require Extended Quota Mode)

These tools have been removed from the server.
