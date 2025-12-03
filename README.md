# 🎵 Spotify MCP Server

<div align="center">
  <img src="icon.svg" alt="Spotify MCP Server" width="120" height="120">
  <br><br>
  
  [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
  [![MCP](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
  
  **Control Spotify with natural language through Claude Desktop.**
  
  *81 tools • 8 resources • 8 prompts*
</div>

---

## ⚡ Quick Start

```bash
# 1. Install
pip install -e .

# 2. Authenticate with Spotify
python -m spotify_mcp.auth

# 3. Add to Claude Desktop config (see docs/setup/QUICK_SETUP.md)
```

📖 **Full Setup Guide:** [docs/setup/QUICK_SETUP.md](docs/setup/QUICK_SETUP.md)

---

## 🎯 What You Can Do

Just talk naturally:

| Category | Examples |
|----------|----------|
| **Playback** | "Play my Discover Weekly" • "Skip this song" • "Volume to 50%" |
| **Search** | "Find chill jazz" • "Search for Radiohead albums" |
| **Library** | "Save this track" • "Show my top artists" |
| **Playlists** | "Create a workout playlist" • "Add this to my queue" |
| **Discovery** | "What's new this week?" • "Show artist's top tracks" |

---

## 🛠️ Tools (81)

| Category | Count | Description |
|----------|-------|-------------|
| Playback | 12 | Play, pause, skip, volume, shuffle, seek |
| Playlists | 12 | Create, modify, follow, manage covers |
| Albums | 8 | Browse, save, new releases |
| User | 8 | Profile, top items, following |
| Shows | 7 | Podcasts and episodes |
| Episodes | 6 | Save and manage podcast episodes |
| Artists | 4 | Details, discography, top tracks |
| Library | 4 | Saved tracks management |
| Categories | 2 | Browse categories |
| Queue | 2 | View and add to queue |
| Tracks | 2 | Track details |
| Search | 1 | Universal search |
| Markets | 1 | Available markets |
| **Composite** | 6 | Multi-step operations |

📖 **Full Tool Reference:** [docs/TOOLS.md](docs/TOOLS.md)

---

## 📋 Requirements

- Python 3.10+
- Spotify account (Premium for playback control)
- [Spotify Developer App](https://developer.spotify.com/dashboard)

---

## 🔧 Configuration

### Claude Desktop

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "spotify": {
      "command": "python",
      "args": ["-m", "spotify_mcp.server"],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_client_id",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret",
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback",
        "PYTHONPATH": "/path/to/spotify_mcp/src"
      }
    }
  }
}
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Set `PYTHONPATH` to `src` directory |
| No tokens | Run `python -m spotify_mcp.auth` |
| Invalid redirect URI | Use `127.0.0.1` not `localhost` |
| No active device | Open Spotify on any device |
| Premium required | Playback control needs Premium |

📖 **Full Guide:** [docs/setup/troubleshooting.md](docs/setup/troubleshooting.md)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Quick Setup](docs/setup/QUICK_SETUP.md) | Get started in 5 minutes |
| [Tool Reference](docs/TOOLS.md) | All 75 tools explained |
| [API Reference](docs/API.md) | Resources, prompts, schemas |
| [Deployment](docs/DEPLOYMENT.md) | Production deployment guide |
| [Architecture](docs/architecture/OVERVIEW.md) | System design |

---

## 🚀 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code quality
black src/ tests/
isort src/ tests/
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

<div align="center">
  
**[Documentation](docs/INDEX.md)** • **[Contributing](CONTRIBUTING.md)** • **[Security](SECURITY.md)**

Made with 🎵 for the AI + Music community

</div>
