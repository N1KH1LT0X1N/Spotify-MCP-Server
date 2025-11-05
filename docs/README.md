# Documentation

Welcome to the Spotify MCP Server documentation!

## 🚀 Getting Started

**New to the project?** Start here:
- **[Quick Start Guide](../QUICKSTART.md)** - Get running in 5 minutes
- **[Authentication Setup](setup/authentication.md)** - How authentication works
- **[Claude Desktop Configuration](setup/claude-desktop.md)** - Connect to Claude Desktop
- **[Troubleshooting](setup/troubleshooting.md)** - Common issues and solutions

## 📚 Documentation Sections

### Setup & Configuration
Everything you need to get up and running:
- [Authentication](setup/authentication.md) - OAuth flow, token management
- [Claude Desktop](setup/claude-desktop.md) - Integration guide
- [Troubleshooting](setup/troubleshooting.md) - Fix common problems

### 🏢 Enterprise Features
Advanced security and management features:
- [Security Features](enterprise/security.md) - Keychain, audit logging, multi-profile
- [Quick Start](enterprise/quickstart.md) - Enterprise features reference
- [Implementation Details](enterprise/implementation.md) - Technical architecture

### 🔧 Diagnostic Tools
Tools for troubleshooting and monitoring:
- [Tools Comparison](diagnostics/tools-comparison.md) - Which tool to use when
- [Auth Enhancements](diagnostics/auth-enhancements.md) - Enhanced authentication features

### 👨‍💻 Development
For contributors and developers:
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute
- [Roadmap](development/roadmap.md) - Future plans
- [Project Structure](../) - Repository organization

## 🆘 Need Help?

### Quick Commands

```bash
# Check if everything is working
python diagnose_auth.py

# Interactive diagnostics
python diagnose_auth.py --interactive

# Test authentication
python test_auth.py

# View built-in diagnostics
python -m src.spotify_mcp.auth
```

### Common Issues

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError | Set PYTHONPATH to `src` directory |
| ERR_CONNECTION_REFUSED | Normal! Copy the URL from browser |
| Token expired | Auto-refreshes automatically |
| Need to re-auth | Run `python test_auth.py` |

See [Troubleshooting Guide](setup/troubleshooting.md) for more.

## 📖 Documentation Structure

```
docs/
├── README.md (you are here)
├── setup/
│   ├── authentication.md
│   ├── claude-desktop.md
│   └── troubleshooting.md
├── enterprise/
│   ├── security.md
│   ├── quickstart.md
│   └── implementation.md
├── diagnostics/
│   ├── tools-comparison.md
│   └── auth-enhancements.md
└── development/
    └── roadmap.md
```

## 🔗 External Resources

- **Spotify API Documentation**: https://developer.spotify.com/documentation/web-api
- **MCP Protocol**: https://modelcontextprotocol.io
- **GitHub Repository**: https://github.com/N1KH1LT0X1N/Spotify-MCP-Server
- **Issues & Support**: https://github.com/N1KH1LT0X1N/Spotify-MCP-Server/issues

## 📝 Quick Links

### For New Users
1. [Quick Start](../QUICKSTART.md) → Get running
2. [Troubleshooting](setup/troubleshooting.md) → If stuck
3. [Claude Desktop Setup](setup/claude-desktop.md) → Connect to Claude

### For Advanced Users
1. [Enterprise Features](enterprise/security.md) → Security & multi-profile
2. [Diagnostic Tools](diagnostics/tools-comparison.md) → Advanced debugging
3. [Development](development/roadmap.md) → Contribute

---

**Still can't find what you're looking for?** [Open an issue](https://github.com/N1KH1LT0X1N/Spotify-MCP-Server/issues)!
