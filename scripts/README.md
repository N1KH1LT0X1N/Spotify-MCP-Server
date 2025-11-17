# 🔧 Utility Scripts

Helper scripts for managing and diagnosing the Spotify MCP Server.

## Scripts Overview

### `diagnose_auth.py`

**Purpose**: Comprehensive authentication diagnostics

**Usage**:
```bash
# Auto-diagnosis mode (recommended)
python scripts/diagnose_auth.py

# Interactive menu mode
python scripts/diagnose_auth.py --interactive
```

**Features**:
- Checks .env file configuration
- Validates credentials
- Tests token refresh
- Provides clear guidance and next steps
- Interactive troubleshooting menu

---

### `generate_claude_config.py`

**Purpose**: Generate Claude Desktop configuration automatically

**Usage**:
```bash
python scripts/generate_claude_config.py
```

**What it does**:
- Detects your Python environment
- Loads credentials from `.env`
- Shows config file location
- Provides ready-to-use configurations
- Supports multiple configuration formats

---

### `verify_pretty_setup.py`

**Purpose**: Verify Claude Desktop setup is complete

**Usage**:
```bash
python scripts/verify_pretty_setup.py
```

**What it does**:
- Checks Claude Desktop config file
- Validates MCP server configuration
- Verifies icon path
- Tests environment variables
- Provides setup completion report

---

### `verify_setup.py`

**Purpose**: Comprehensive setup verification

**Usage**:
```bash
python scripts/verify_setup.py
```

**What it does**:
- Validates Python environment
- Checks dependencies
- Tests authentication
- Verifies MCP server configuration
- Provides detailed diagnostics

---

### `enterprise_cli.py`

**Purpose**: Enterprise features CLI (keychain, audit logging, multi-profile)

**Usage**:
```bash
# Show enterprise features
python scripts/enterprise_cli.py

# Enable keychain storage
python scripts/enterprise_cli.py --enable-keychain

# Enable audit logging
python scripts/enterprise_cli.py --enable-audit

# Switch profiles
python scripts/enterprise_cli.py --profile work
```

**Features**:
- Secure credential storage in system keychain
- Audit logging for security compliance
- Multi-profile support
- Enhanced security features

---

### `auto_auth.py`

**Purpose**: Automated authentication (⚠️ not recommended for production)

**Usage**:
```bash
python scripts/auto_auth.py
```

**Warning**: This script automates the OAuth flow and is **not recommended** for production use. Use only for development/testing purposes.

---

## Quick Commands

### Diagnose Authentication Issues
```bash
python scripts/diagnose_auth.py
```

### Generate Claude Config
```bash
python scripts/generate_claude_config.py
```

### Verify Setup
```bash
python scripts/verify_setup.py
```

### Enable Enterprise Features
```bash
python scripts/enterprise_cli.py --enable-keychain
```

---

## Common Workflows

### First-Time Setup
1. Run `python scripts/verify_setup.py` to check requirements
2. Run `python scripts/diagnose_auth.py` to configure authentication
3. Run `python scripts/generate_claude_config.py` for Claude Desktop config
4. Run `python scripts/verify_pretty_setup.py` to confirm setup

### Troubleshooting Auth
1. Run `python scripts/diagnose_auth.py --interactive`
2. Follow the interactive troubleshooting menu
3. Test authentication with the tool

### Enterprise Setup
1. Run `python scripts/enterprise_cli.py --enable-keychain`
2. Run `python scripts/enterprise_cli.py --enable-audit`
3. Configure profiles as needed

---

## Requirements

All scripts require:
- Python 3.10+
- Installed dependencies (`pip install -e .`)
- `.env` file with Spotify credentials (for auth scripts)

---

## Getting Help

Each script supports `--help` flag:

```bash
python scripts/diagnose_auth.py --help
python scripts/enterprise_cli.py --help
```

For more documentation, see:
- [Setup Guide](../docs/setup/QUICK_SETUP.md)
- [Troubleshooting](../docs/setup/troubleshooting.md)
- [Enterprise Features](../docs/enterprise/security.md)

