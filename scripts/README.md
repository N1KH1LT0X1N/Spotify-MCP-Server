# 🔧 Utility Scripts# Utility Scripts



Helper scripts for managing and diagnosing the Spotify MCP Server.This folder contains utility scripts for managing and diagnosing the Spotify MCP Server.



## 🚀 Quick Start Scripts## Scripts



### `generate_claude_config.py` ⭐### `diagnose_auth.py`

**Generate Claude Desktop configuration automatically****Purpose**: Diagnostic tool for troubleshooting authentication issues.



```bash**Usage**:

python scripts/generate_claude_config.py```bash

```# Auto-diagnosis mode (recommended)

python scripts/diagnose_auth.py

**What it does:**

- Detects your Python environment# Interactive menu mode

- Loads credentials from `.env`python scripts/diagnose_auth.py --interactive

- Shows config file location```

- Provides ready-to-use configurations

**Features**:

---- Checks .env file configuration

- Validates credentials

### `verify_pretty_setup.py` ✅- Tests token refresh

**Verify Claude Desktop setup is complete**- Provides clear guidance and next steps

- Interactive troubleshooting menu

```bash

python scripts/verify_pretty_setup.py---

```

### `enterprise_cli.py`

**Checks:****Purpose**: Command-line interface for enterprise security features.

- Icon file exists and is valid

- Server metadata is correct**Usage**:

- Claude Desktop config is present```bash

- Documentation is available# Revoke access for a profile

python scripts/enterprise_cli.py revoke [profile]

---

# View audit log

### `diagnose_auth.py` 🔍python scripts/enterprise_cli.py audit [profile] [limit]

**Diagnose authentication issues**

# Check security alerts

```bashpython scripts/enterprise_cli.py alerts

# Auto-diagnosis mode (recommended)

python scripts/diagnose_auth.py# List profiles

python scripts/enterprise_cli.py profiles

# Interactive menu mode

python scripts/diagnose_auth.py --interactive# Create new profile

```python scripts/enterprise_cli.py create-profile <name> <client_id> <client_secret>



**Features:**# Enable keychain storage

- Checks `.env` file configurationpython scripts/enterprise_cli.py enable-keychain [profile]

- Validates Spotify credentials

- Tests token refresh# Disable keychain storage

- Provides clear guidancepython scripts/enterprise_cli.py disable-keychain [profile]

- Interactive troubleshooting menu```



---**Examples**:

```bash

## 🏢 Enterprise Scripts# Revoke production profile

python scripts/enterprise_cli.py revoke production

### `enterprise_cli.py`

**Command-line interface for enterprise security features**# View last 50 audit entries

python scripts/enterprise_cli.py audit default 50

```bash

# Common commands# Create new dev profile

python scripts/enterprise_cli.py profiles        # List profilespython scripts/enterprise_cli.py create-profile dev CLIENT_ID CLIENT_SECRET

python scripts/enterprise_cli.py audit           # View audit log```

python scripts/enterprise_cli.py revoke          # Revoke access

python scripts/enterprise_cli.py alerts          # Check alerts---



# Profile management### `verify_setup.py`

python scripts/enterprise_cli.py create-profile <name> <client_id> <client_secret>**Purpose**: Verify Spotify MCP Server installation and configuration.

python scripts/enterprise_cli.py enable-keychain [profile]

python scripts/enterprise_cli.py disable-keychain [profile]**Usage**:

``````bash

python scripts/verify_setup.py

---```



## 🧪 Setup & Verification**Checks**:

- Python version compatibility

### `verify_setup.py`- Required dependencies installed

**Verify installation and configuration**- Configuration files present

- Environment variables set

```bash- MCP server can start

python scripts/verify_setup.py

```---



**Checks:**### `auto_auth.py`

- ✅ Python version (3.10+)**Purpose**: Experimental automated OAuth authentication (NOT RECOMMENDED).

- ✅ Dependencies installed

- ✅ Configuration files present⚠️ **Warning**: This script uses Selenium to automate browser authentication. It requires storing your Spotify password, which is a security risk. Only use for testing/development purposes.

- ✅ Environment variables set

- ✅ MCP server can start**Why not recommended**:

- Requires storing password in plaintext

---- Adds unnecessary complexity (Selenium dependency)

- Manual OAuth flow is simple and secure

## ⚠️ Experimental Scripts- Breaks if Spotify changes their login page



### `auto_auth.py`**Usage** (if you really need it):

**Automated OAuth (NOT RECOMMENDED)**```bash

# Not recommended - use manual OAuth instead

⚠️ **Security Risk**: Requires storing password in plaintext. Only for testing/development.python scripts/auto_auth.py

```

---

---

## 📋 Usage Guide

## Quick Start

### First Time Setup

### First Time Setup

1. **Verify installation:**1. Run verification:

   ```bash   ```bash

   python scripts/verify_setup.py   python scripts/verify_setup.py

   ```   ```



2. **Check authentication:**2. If issues, run diagnostics:

   ```bash   ```bash

   python scripts/diagnose_auth.py   python scripts/diagnose_auth.py

   ```   ```



3. **Generate Claude config:**### Regular Usage

   ```bash- **Check auth status**: `python scripts/diagnose_auth.py`

   python scripts/generate_claude_config.py- **Revoke and re-auth**: `python scripts/enterprise_cli.py revoke`

   ```- **View audit trail**: `python scripts/enterprise_cli.py audit`



4. **Verify Claude setup:**---

   ```bash

   python scripts/verify_pretty_setup.py## Development

   ```

### Adding New Scripts

### Regular Usage1. Create script in this folder

2. Add entry to this README

- **Check auth status**: `python scripts/diagnose_auth.py`3. Make script executable: `chmod +x script_name.py`

- **Update Claude config**: `python scripts/generate_claude_config.py`4. Add shebang if needed: `#!/usr/bin/env python3`

- **Verify setup**: `python scripts/verify_pretty_setup.py`

- **Enterprise features**: `python scripts/enterprise_cli.py --help`### Script Guidelines

- Include docstring with purpose and usage

---- Add `if __name__ == "__main__":` guard

- Use argparse for CLI arguments

## 🆘 Troubleshooting- Provide helpful error messages

- Write to stderr for diagnostics (avoid polluting stdout)

### "Module not found" errors

```bash---

# Set PYTHONPATH

export PYTHONPATH="src"  # Linux/Mac## Troubleshooting

$env:PYTHONPATH="src"    # Windows PowerShell

### "Module not found" errors

# Or install in development mode```bash

pip install -e .# Install in development mode

```pip install -e .

```

### "No .env file found"

```bash### "No .env file found"

# Copy example and configure```bash

cp .env.example .env# Copy example and configure

# Edit .env with your credentialscp .env.example .env

```# Edit .env with your credentials

```

### Authentication issues

```bash### Authentication issues

# Run interactive diagnostics```bash

python scripts/diagnose_auth.py --interactive# Run diagnostic tool

```python scripts/diagnose_auth.py --interactive

```

---

---

## 📚 See Also

## See Also

- **[Quick Setup Guide](../docs/setup/QUICK_SETUP.md)** - Get started fast

- **[Authentication Guide](../docs/setup/authentication.md)** - OAuth setup- [Authentication Guide](../docs/setup/authentication.md)

- **[Enterprise Security](../docs/enterprise/security.md)** - Advanced features- [Enterprise Security](../docs/enterprise/security.md)

- **[Troubleshooting Guide](../docs/setup/troubleshooting.md)** - Fix common issues- [Troubleshooting Guide](../docs/setup/troubleshooting.md)

