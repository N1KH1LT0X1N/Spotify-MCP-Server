# 📚 Spotify MCP Server Documentation

Complete documentation for the Spotify Model Context Protocol Server with **58 tools** across **14 categories**.

## 🚀 Getting Started

**New to this project? Start here:**

1. **[Quick Setup Guide](setup/QUICK_SETUP.md)** - Copy-paste configuration (fastest!)
2. **[Get Started Guide](setup/GET_STARTED.md)** - Complete setup with visual guide
3. **[Quickstart](setup/QUICKSTART.md)** - Detailed step-by-step setup
4. **[Claude Desktop Setup](setup/CLAUDE_DESKTOP_SETUP.md)** - Comprehensive Claude configuration

## 📖 Documentation Sections

### 📦 Setup & Configuration

Everything you need to get up and running:

- **[Quick Setup](setup/QUICK_SETUP.md)** - Ready-to-use configuration
- **[Get Started](setup/GET_STARTED.md)** - Visual setup guide
- **[Quickstart Guide](setup/QUICKSTART.md)** - Complete installation guide
- **[Claude Desktop Setup](setup/CLAUDE_DESKTOP_SETUP.md)** - Detailed Claude configuration
- **[Authentication Setup](setup/authentication.md)** - Spotify OAuth configuration
- **[Troubleshooting](setup/troubleshooting.md)** - Common issues and solutions

### 👨‍💻 Development

For contributors and developers:

- **[Roadmap](development/roadmap.md)** - Project roadmap and future features
- **[Phase 0 Complete](development/PHASE_0_SUMMARY.md)** - Testing infrastructure ✅
- **[Pretty Setup Summary](development/PRETTY_SETUP_SUMMARY.md)** - Claude Desktop integration
- **[Test Fixes](development/TEST_FIXES_COMPLETE.md)** - Test implementation details
- **[Security Audit](development/SECURITY_AUDIT.md)** - Security review and fixes 🔒

### 🏢 Enterprise Features

Advanced security and management features:

- **[Security Guide](enterprise/security.md)** - Enterprise security features
- **[Implementation Guide](enterprise/implementation.md)** - Enterprise deployment
- **[Enterprise Quickstart](enterprise/quickstart.md)** - Quick enterprise setup

### 🔧 Diagnostics & Tools

Tools for troubleshooting and monitoring:

- **[Auth Enhancements](diagnostics/auth-enhancements.md)** - Authentication improvements
- **[Tools Comparison](diagnostics/tools-comparison.md)** - Available tools reference

## 🎯 Quick Reference

| I want to... | Documentation |
|--------------|---------------|
| **Set up quickly** | [Quick Setup](setup/QUICK_SETUP.md) |
| **Configure Claude Desktop** | [Get Started](setup/GET_STARTED.md) |
| **Understand authentication** | [Authentication](setup/authentication.md) |
| **Fix an issue** | [Troubleshooting](setup/troubleshooting.md) |
| **Use enterprise features** | [Security Guide](enterprise/security.md) |
| **Review security** | [Security Audit](development/SECURITY_AUDIT.md) |
| **Contribute** | [Contributing](../CONTRIBUTING.md) |

## 🆘 Need Help?

### Diagnostic Scripts

```bash
# Check authentication status
python scripts/diagnose_auth.py

# Verify Claude Desktop setup
python scripts/verify_pretty_setup.py

# Generate Claude configuration
python scripts/generate_claude_config.py
```

### Common Issues

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError | Set `PYTHONPATH` to `src` directory |
| ERR_CONNECTION_REFUSED | Normal! Copy the URL from browser |
| Token expired | Auto-refreshes automatically |
| Server not in Claude | Check [Get Started](setup/GET_STARTED.md) |

See **[Troubleshooting Guide](setup/troubleshooting.md)** for complete solutions.

## 📁 Repository Structure

```
spotify_mcp/
├── 📚 docs/              Documentation
│   ├── setup/           Setup and configuration
│   ├── development/     Development docs
│   ├── enterprise/      Enterprise features
│   └── diagnostics/     Diagnostic tools
├── 📦 src/              Source code
│   └── spotify_mcp/     Main package (58 tools, 14 categories)
│       ├── tools/       MCP tool implementations
│       ├── auth.py      Authentication
│       ├── server.py    MCP server
│       └── ...
├── 🧪 tests/            Test suite (69 tests, 100% pass)
├── 🔧 scripts/          Utility scripts
├── ⚙️ .github/          CI/CD workflows
├── 🎨 icon.svg          Spotify branding
├── 📄 README.md         Project overview
└── 📝 pyproject.toml    Package configuration
```

## 🤝 Contributing

See **[CONTRIBUTING.md](../CONTRIBUTING.md)** for guidelines on:

- Code style and standards
- Testing requirements
- Pull request process
- Development setup

## 🔒 Security

See **[SECURITY.md](../SECURITY.md)** for:

- Security policy
- Vulnerability reporting
- Best practices
- Security features

For security audit results, see **[Security Audit Report](development/SECURITY_AUDIT.md)**

## 🔗 External Resources

- **[Spotify Web API](https://developer.spotify.com/documentation/web-api)** - Official API docs
- **[Model Context Protocol](https://modelcontextprotocol.io)** - MCP specification
- **[GitHub Repository](https://github.com/N1KH1LT0X1N/Spotify-MCP-Server)** - Source code
- **[Issues](https://github.com/N1KH1LT0X1N/Spotify-MCP-Server/issues)** - Bug reports & features

## 📄 License

MIT License - see **[LICENSE](../LICENSE)** for details.

---

**Can't find what you need?** Open an [issue](https://github.com/N1KH1LT0X1N/Spotify-MCP-Server/issues) or check the [Troubleshooting Guide](setup/troubleshooting.md)!
