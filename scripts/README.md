# Utility Scripts

This folder contains utility scripts for managing and diagnosing the Spotify MCP Server.

## Scripts

### `diagnose_auth.py`
**Purpose**: Diagnostic tool for troubleshooting authentication issues.

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

### `enterprise_cli.py`
**Purpose**: Command-line interface for enterprise security features.

**Usage**:
```bash
# Revoke access for a profile
python scripts/enterprise_cli.py revoke [profile]

# View audit log
python scripts/enterprise_cli.py audit [profile] [limit]

# Check security alerts
python scripts/enterprise_cli.py alerts

# List profiles
python scripts/enterprise_cli.py profiles

# Create new profile
python scripts/enterprise_cli.py create-profile <name> <client_id> <client_secret>

# Enable keychain storage
python scripts/enterprise_cli.py enable-keychain [profile]

# Disable keychain storage
python scripts/enterprise_cli.py disable-keychain [profile]
```

**Examples**:
```bash
# Revoke production profile
python scripts/enterprise_cli.py revoke production

# View last 50 audit entries
python scripts/enterprise_cli.py audit default 50

# Create new dev profile
python scripts/enterprise_cli.py create-profile dev CLIENT_ID CLIENT_SECRET
```

---

### `verify_setup.py`
**Purpose**: Verify Spotify MCP Server installation and configuration.

**Usage**:
```bash
python scripts/verify_setup.py
```

**Checks**:
- Python version compatibility
- Required dependencies installed
- Configuration files present
- Environment variables set
- MCP server can start

---

### `auto_auth.py`
**Purpose**: Experimental automated OAuth authentication (NOT RECOMMENDED).

⚠️ **Warning**: This script uses Selenium to automate browser authentication. It requires storing your Spotify password, which is a security risk. Only use for testing/development purposes.

**Why not recommended**:
- Requires storing password in plaintext
- Adds unnecessary complexity (Selenium dependency)
- Manual OAuth flow is simple and secure
- Breaks if Spotify changes their login page

**Usage** (if you really need it):
```bash
# Not recommended - use manual OAuth instead
python scripts/auto_auth.py
```

---

## Quick Start

### First Time Setup
1. Run verification:
   ```bash
   python scripts/verify_setup.py
   ```

2. If issues, run diagnostics:
   ```bash
   python scripts/diagnose_auth.py
   ```

### Regular Usage
- **Check auth status**: `python scripts/diagnose_auth.py`
- **Revoke and re-auth**: `python scripts/enterprise_cli.py revoke`
- **View audit trail**: `python scripts/enterprise_cli.py audit`

---

## Development

### Adding New Scripts
1. Create script in this folder
2. Add entry to this README
3. Make script executable: `chmod +x script_name.py`
4. Add shebang if needed: `#!/usr/bin/env python3`

### Script Guidelines
- Include docstring with purpose and usage
- Add `if __name__ == "__main__":` guard
- Use argparse for CLI arguments
- Provide helpful error messages
- Write to stderr for diagnostics (avoid polluting stdout)

---

## Troubleshooting

### "Module not found" errors
```bash
# Install in development mode
pip install -e .
```

### "No .env file found"
```bash
# Copy example and configure
cp .env.example .env
# Edit .env with your credentials
```

### Authentication issues
```bash
# Run diagnostic tool
python scripts/diagnose_auth.py --interactive
```

---

## See Also

- [Authentication Guide](../docs/setup/authentication.md)
- [Enterprise Security](../docs/enterprise/security.md)
- [Troubleshooting Guide](../docs/setup/troubleshooting.md)
