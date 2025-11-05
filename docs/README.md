# 📚 Spotify MCP Server Documentation# 📚 Spotify MCP Server Documentation# Documentation



Complete documentation for the Spotify Model Context Protocol Server.



## 🚀 Getting StartedComplete documentation for the Spotify Model Context Protocol Server.Welcome to the Spotify MCP Server documentation!



**New to this project? Start here:**



1. **[Quick Setup Guide](setup/QUICK_SETUP.md)** - Copy-paste configuration (fastest!)## 🚀 Getting Started## 🚀 Getting Started

2. **[Get Started Guide](setup/GET_STARTED.md)** - Complete setup with visual guide  

3. **[Quickstart](setup/QUICKSTART.md)** - Detailed step-by-step setup

4. **[Claude Desktop Setup](setup/CLAUDE_DESKTOP_SETUP.md)** - Comprehensive Claude configuration

**New to this project? Start here:****New to the project?** Start here:

## 📖 Documentation Sections

- **[Quick Start Guide](../QUICKSTART.md)** - Get running in 5 minutes

### 📦 Setup & Configuration

- **[Quick Setup](setup/QUICK_SETUP.md)** - Ready-to-use configuration1. **[Quick Setup Guide](setup/QUICK_SETUP.md)** - Copy-paste configuration (fastest!)- **[Authentication Setup](setup/authentication.md)** - How authentication works

- **[Get Started](setup/GET_STARTED.md)** - Visual setup guide

- **[Quickstart Guide](setup/QUICKSTART.md)** - Complete installation guide2. **[Get Started Guide](setup/GET_STARTED.md)** - Complete setup with visual guide  - **[Claude Desktop Configuration](setup/claude-desktop.md)** - Connect to Claude Desktop

- **[Claude Desktop Setup](setup/CLAUDE_DESKTOP_SETUP.md)** - Detailed Claude configuration

- **[Authentication Setup](setup/authentication.md)** - Spotify OAuth configuration3. **[Quickstart](setup/QUICKSTART.md)** - Detailed step-by-step setup- **[Troubleshooting](setup/troubleshooting.md)** - Common issues and solutions

- **[Troubleshooting](setup/troubleshooting.md)** - Common issues and solutions

4. **[Claude Desktop Setup](setup/CLAUDE_DESKTOP_SETUP.md)** - Comprehensive Claude configuration

### 👨‍💻 Development

- **[Roadmap](development/roadmap.md)** - Project roadmap and future features## 📚 Documentation Sections

- **[Phase 0 Complete](development/PHASE_0_SUMMARY.md)** - Testing infrastructure ✅

- **[Pretty Setup Summary](development/PRETTY_SETUP_SUMMARY.md)** - Claude Desktop integration## 📖 Documentation Sections

- **[Test Fixes](development/TEST_FIXES_COMPLETE.md)** - Test implementation details

- **[Security Audit](development/SECURITY_AUDIT.md)** - Security review and fixes 🔒### Setup & Configuration



### 🏢 Enterprise Features### 📦 Setup & ConfigurationEverything you need to get up and running:

- **[Security Guide](enterprise/security.md)** - Enterprise security features

- **[Implementation Guide](enterprise/implementation.md)** - Enterprise deployment- **[Quick Setup](setup/QUICK_SETUP.md)** - Ready-to-use configuration- [Authentication](setup/authentication.md) - OAuth flow, token management

- **[Enterprise Quickstart](enterprise/quickstart.md)** - Quick enterprise setup

- **[Get Started](setup/GET_STARTED.md)** - Visual setup guide with your credentials- [Claude Desktop](setup/claude-desktop.md) - Integration guide

### 🔧 Diagnostics & Tools

- **[Auth Enhancements](diagnostics/auth-enhancements.md)** - Authentication improvements- **[Quickstart Guide](setup/QUICKSTART.md)** - Complete installation guide- [Troubleshooting](setup/troubleshooting.md) - Fix common problems

- **[Tools Comparison](diagnostics/tools-comparison.md)** - Available tools reference

- **[Claude Desktop Setup](setup/CLAUDE_DESKTOP_SETUP.md)** - Detailed Claude configuration

## 🎯 Quick Reference

- **[Authentication Setup](setup/authentication.md)** - Spotify OAuth configuration### 🏢 Enterprise Features

| I want to... | Documentation |

|--------------|---------------|- **[Troubleshooting](setup/troubleshooting.md)** - Common issues and solutionsAdvanced security and management features:

| **Set up quickly** | [Quick Setup](setup/QUICK_SETUP.md) |

| **Configure Claude Desktop** | [Get Started](setup/GET_STARTED.md) |- [Security Features](enterprise/security.md) - Keychain, audit logging, multi-profile

| **Understand authentication** | [Authentication](setup/authentication.md) |

| **Fix an issue** | [Troubleshooting](setup/troubleshooting.md) |### 👨‍💻 Development- [Quick Start](enterprise/quickstart.md) - Enterprise features reference

| **Use enterprise features** | [Security Guide](enterprise/security.md) |

| **Review security** | [Security Audit](development/SECURITY_AUDIT.md) |- **[Roadmap](development/roadmap.md)** - Project roadmap and future features- [Implementation Details](enterprise/implementation.md) - Technical architecture

| **Contribute** | [Contributing](../CONTRIBUTING.md) |

- **[Phase 0 Complete](development/PHASE_0_SUMMARY.md)** - Testing infrastructure ✅

## 🆘 Need Help?

- **[Pretty Setup Summary](development/PRETTY_SETUP_SUMMARY.md)** - Claude Desktop integration### 🔧 Diagnostic Tools

### Diagnostic Scripts

- **[Test Fixes](development/TEST_FIXES_COMPLETE.md)** - Test implementation detailsTools for troubleshooting and monitoring:

```bash

# Check authentication status- [Tools Comparison](diagnostics/tools-comparison.md) - Which tool to use when

python scripts/diagnose_auth.py

### 🏢 Enterprise Features- [Auth Enhancements](diagnostics/auth-enhancements.md) - Enhanced authentication features

# Verify Claude Desktop setup

python scripts/verify_pretty_setup.py- **[Security Guide](enterprise/security.md)** - Enterprise security features



# Generate Claude configuration- **[Implementation Guide](enterprise/implementation.md)** - Enterprise deployment### 👨‍💻 Development

python scripts/generate_claude_config.py

```- **[Enterprise Quickstart](enterprise/quickstart.md)** - Quick enterprise setupFor contributors and developers:



### Common Issues- [Contributing Guide](../CONTRIBUTING.md) - How to contribute



| Problem | Solution |### 🔧 Diagnostics & Tools- [Roadmap](development/roadmap.md) - Future plans

|---------|----------|

| ModuleNotFoundError | Set `PYTHONPATH` to `src` directory |- **[Auth Enhancements](diagnostics/auth-enhancements.md)** - Authentication improvements- [Project Structure](../) - Repository organization

| ERR_CONNECTION_REFUSED | Normal! Copy the URL from browser |

| Token expired | Auto-refreshes automatically |- **[Tools Comparison](diagnostics/tools-comparison.md)** - Available tools reference

| Server not in Claude | Check [Get Started](setup/GET_STARTED.md) |

## 🆘 Need Help?

See **[Troubleshooting Guide](setup/troubleshooting.md)** for complete solutions.

## 🎯 Quick Reference

## 📁 Repository Structure

### Quick Commands

```

spotify_mcp/| I want to... | Documentation |

├── 📚 docs/              Documentation

│   ├── setup/           Setup and configuration|--------------|---------------|```bash

│   ├── development/     Development docs & security audit

│   ├── enterprise/      Enterprise features| **Set up quickly** | [Quick Setup](setup/QUICK_SETUP.md) |# Check if everything is working

│   └── diagnostics/     Diagnostic tools

├── 📦 src/              Source code| **Configure Claude Desktop** | [Get Started](setup/GET_STARTED.md) |python diagnose_auth.py

│   └── spotify_mcp/     Main package

│       ├── tools/       MCP tool implementations| **Understand authentication** | [Authentication](setup/authentication.md) |

│       ├── auth.py      Authentication

│       ├── server.py    MCP server| **Fix an issue** | [Troubleshooting](setup/troubleshooting.md) |# Interactive diagnostics

│       └── ...

├── 🧪 tests/            Test suite (69 tests, 100% pass)| **Use enterprise features** | [Security Guide](enterprise/security.md) |python diagnose_auth.py --interactive

├── 🔧 scripts/          Utility scripts

├── ⚙️ .github/          CI/CD workflows| **Contribute** | [Contributing](../CONTRIBUTING.md) |

├── 🎨 icon.svg          Spotify branding

├── 📄 README.md         Project overview# Test authentication

├── 🔒 SECURITY.md       Security policy

└── 📝 pyproject.toml    Package configuration## 🆘 Need Help?python test_auth.py

```



## 🤝 Contributing

### Diagnostic Scripts# View built-in diagnostics

See **[CONTRIBUTING.md](../CONTRIBUTING.md)** for guidelines on:

- Code style and standardspython -m src.spotify_mcp.auth

- Testing requirements

- Pull request process```bash```

- Development setup

# Check authentication status

## 🔒 Security

python scripts/diagnose_auth.py### Common Issues

See **[SECURITY.md](../SECURITY.md)** for:

- Security policy

- Vulnerability reporting

- Best practices# Verify Claude Desktop setup| Problem | Solution |

- Security features

python scripts/verify_pretty_setup.py|---------|----------|

For security audit results, see **[Security Audit Report](development/SECURITY_AUDIT.md)**

| ModuleNotFoundError | Set PYTHONPATH to `src` directory |

## 🔗 External Resources

# Generate Claude configuration| ERR_CONNECTION_REFUSED | Normal! Copy the URL from browser |

- **[Spotify Web API](https://developer.spotify.com/documentation/web-api)** - Official API docs

- **[Model Context Protocol](https://modelcontextprotocol.io)** - MCP specificationpython scripts/generate_claude_config.py| Token expired | Auto-refreshes automatically |

- **[GitHub Repository](https://github.com/N1KH1LT0X1N/Spotify-MCP-Server)** - Source code

- **[Issues](https://github.com/N1KH1LT0X1N/Spotify-MCP-Server/issues)** - Bug reports & features```| Need to re-auth | Run `python test_auth.py` |



## 📄 License



MIT License - see **[LICENSE](../LICENSE)** for details.### Common IssuesSee [Troubleshooting Guide](setup/troubleshooting.md) for more.



---



**Can't find what you need?** Open an [issue](https://github.com/N1KH1LT0X1N/Spotify-MCP-Server/issues) or check the [Troubleshooting Guide](setup/troubleshooting.md)!| Problem | Solution |## 📖 Documentation Structure


|---------|----------|

| ModuleNotFoundError | Set `PYTHONPATH` to `src` directory |```

| ERR_CONNECTION_REFUSED | Normal! Copy the URL from browser |docs/

| Token expired | Auto-refreshes automatically |├── README.md (you are here)

| Server not in Claude | Check [Get Started](setup/GET_STARTED.md) |├── setup/

│   ├── authentication.md

See **[Troubleshooting Guide](setup/troubleshooting.md)** for complete solutions.│   ├── claude-desktop.md

│   └── troubleshooting.md

## 📁 Repository Structure├── enterprise/

│   ├── security.md

```│   ├── quickstart.md

spotify_mcp/│   └── implementation.md

├── 📚 docs/              Documentation├── diagnostics/

│   ├── setup/           Setup and configuration│   ├── tools-comparison.md

│   ├── development/     Development docs│   └── auth-enhancements.md

│   ├── enterprise/      Enterprise features└── development/

│   └── diagnostics/     Diagnostic tools    └── roadmap.md

├── 📦 src/              Source code```

│   └── spotify_mcp/     Main package

│       ├── tools/       MCP tool implementations## 🔗 External Resources

│       ├── auth.py      Authentication

│       ├── server.py    MCP server- **Spotify API Documentation**: https://developer.spotify.com/documentation/web-api

│       └── ...- **MCP Protocol**: https://modelcontextprotocol.io

├── 🧪 tests/            Test suite (69 tests, 100% pass)- **GitHub Repository**: https://github.com/N1KH1LT0X1N/Spotify-MCP-Server

├── 🔧 scripts/          Utility scripts- **Issues & Support**: https://github.com/N1KH1LT0X1N/Spotify-MCP-Server/issues

├── ⚙️ .github/          CI/CD workflows

├── 🎨 icon.svg          Spotify branding## 📝 Quick Links

├── 📄 README.md         Project overview

└── 📝 pyproject.toml    Package configuration### For New Users

```1. [Quick Start](../QUICKSTART.md) → Get running

2. [Troubleshooting](setup/troubleshooting.md) → If stuck

## 🤝 Contributing3. [Claude Desktop Setup](setup/claude-desktop.md) → Connect to Claude



See **[CONTRIBUTING.md](../CONTRIBUTING.md)** for guidelines on:### For Advanced Users

- Code style and standards1. [Enterprise Features](enterprise/security.md) → Security & multi-profile

- Testing requirements2. [Diagnostic Tools](diagnostics/tools-comparison.md) → Advanced debugging

- Pull request process3. [Development](development/roadmap.md) → Contribute

- Development setup

---

## 🔗 External Resources

**Still can't find what you're looking for?** [Open an issue](https://github.com/N1KH1LT0X1N/Spotify-MCP-Server/issues)!

- **[Spotify Web API](https://developer.spotify.com/documentation/web-api)** - Official API docs
- **[Model Context Protocol](https://modelcontextprotocol.io)** - MCP specification
- **[GitHub Repository](https://github.com/N1KH1LT0X1N/Spotify-MCP-Server)** - Source code
- **[Issues](https://github.com/N1KH1LT0X1N/Spotify-MCP-Server/issues)** - Bug reports & features

## 📄 License

MIT License - see **[LICENSE](../LICENSE)** for details.

---

**Can't find what you need?** Open an [issue](https://github.com/N1KH1LT0X1N/Spotify-MCP-Server/issues) or check the [Troubleshooting Guide](setup/troubleshooting.md)!
