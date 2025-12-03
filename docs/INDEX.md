# 📚 Spotify MCP Server Documentation

> **Current Version:** 2.0.0 | **Tools:** 75 (69 standard + 6 composite)

---

## 🚀 Getting Started

| Guide | Description |
|-------|-------------|
| [Quick Setup](setup/QUICK_SETUP.md) | 5-minute setup with Claude Desktop |
| [Authentication](setup/authentication.md) | OAuth setup and token management |
| [Troubleshooting](setup/troubleshooting.md) | Common issues and solutions |

---

## 📖 Reference

| Document | Description |
|----------|-------------|
| [Tool Reference](TOOLS.md) | Complete list of all 75 tools |
| [Architecture](architecture/OVERVIEW.md) | System design and decisions |
| [API Reference](API.md) | Resources, prompts, and schemas |

---

## 🔧 Advanced

| Document | Description |
|----------|-------------|
| [Enterprise Features](enterprise/quickstart.md) | Metrics, logging, CLI |
| [Diagnostics](diagnostics/tools-comparison.md) | Diagnostic tools comparison |
| [Deployment](DEPLOYMENT.md) | Production deployment guide |

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
