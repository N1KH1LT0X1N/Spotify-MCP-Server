#!/usr/bin/env python
"""
Enterprise Security CLI for Spotify MCP Server

Commands:
  revoke [profile]          - Revoke access and clear tokens
  audit [profile] [limit]   - View security audit log
  alerts                    - Check for security alerts
  profiles                  - List all authentication profiles
  create-profile <name>     - Create new authentication profile
  enable-keychain          - Enable system keychain storage
  disable-keychain         - Disable system keychain storage
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from spotify_mcp.security import SecurityManager


def print_usage():
    """Print usage information."""
    print(__doc__)
    print("\nExamples:")
    print("  python enterprise_cli.py revoke")
    print("  python enterprise_cli.py revoke work")
    print("  python enterprise_cli.py audit default 50")
    print("  python enterprise_cli.py profiles")
    print("  python enterprise_cli.py create-profile work")
    print("  python enterprise_cli.py enable-keychain")


def cmd_revoke(args):
    """Revoke access command."""
    profile = args[0] if args else "default"
    security = SecurityManager(profile=profile)
    result = security.revoke_tokens()
    
    if result["success"]:
        print(f"✓ {result['message']}")
    else:
        print(f"✗ {result['message']}")
        sys.exit(1)


def cmd_audit(args):
    """View audit log command."""
    profile = args[0] if len(args) > 0 else "default"
    limit = int(args[1]) if len(args) > 1 else 20
    
    security = SecurityManager(profile=profile)
    log = security.get_audit_log(limit=limit)
    
    if not log:
        print(f"No audit log entries found for profile '{profile}'")
        return
    
    print(f"\n{'='*70}")
    print(f"Security Audit Log - Profile: {profile} (Last {len(log)} entries)")
    print(f"{'='*70}\n")
    
    for entry in log:
        print(f"┌─ [{entry['timestamp']}]")
        print(f"│  Event: {entry['event']}")
        
        for key, value in entry['data'].items():
            print(f"│    {key}: {value}")
        print("└─")
        print()


def cmd_alerts(args):
    """Check security alerts command."""
    security = SecurityManager()
    alerts = security.check_security_alerts()
    
    if not alerts:
        print("✓ No security alerts found")
    else:
        print(f"\n⚠️  {len(alerts)} Security Alert(s) Found:\n")
        print("="*70)
        
        for alert in alerts:
            print(f"\n[{alert['timestamp']}]")
            print(f"  Type: {alert['data'].get('type')}")
            print(f"  Severity: {alert['data'].get('severity', 'unknown').upper()}")
            print(f"  Profile: {alert['data'].get('profile', 'unknown')}")
            print(f"  Message: {alert['data'].get('message')}")
        
        print("\n" + "="*70)
        print("\n💡 Tip: Run 'python enterprise_cli.py audit' for more details")


def cmd_profiles(args):
    """List profiles command."""
    profiles = SecurityManager.list_profiles()
    
    print(f"\n{'='*70}")
    print("Available Authentication Profiles")
    print(f"{'='*70}\n")
    
    for profile in profiles:
        env_file = ".env" if profile == "default" else f".env.{profile}"
        exists = os.path.exists(env_file)
        status = "✓ Active" if exists else "✗ Not configured"
        
        print(f"  • {profile:20s} {status:15s} ({env_file})")
    
    print(f"\n{'='*70}")
    print(f"Total profiles: {len(profiles)}")
    print("\n💡 Tip: Use 'python enterprise_cli.py create-profile <name>' to add new profile")


def cmd_create_profile(args):
    """Create profile command."""
    if not args:
        print("✗ Error: Profile name required")
        print("Usage: python enterprise_cli.py create-profile <name>")
        sys.exit(1)
    
    profile_name = args[0]
    
    # Get credentials
    print(f"\n{'='*70}")
    print(f"Creating Authentication Profile: {profile_name}")
    print(f"{'='*70}\n")
    
    print("Get your Spotify credentials from:")
    print("https://developer.spotify.com/dashboard/applications\n")
    
    client_id = input("Enter Spotify Client ID: ").strip()
    client_secret = input("Enter Spotify Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("\n✗ Error: Client ID and Secret are required")
        sys.exit(1)
    
    # Create profile
    success = SecurityManager.create_profile(profile_name, client_id, client_secret)
    
    if success:
        env_file = ".env" if profile_name == "default" else f".env.{profile_name}"
        print(f"\n✓ Profile '{profile_name}' created successfully!")
        print(f"  Configuration saved to: {env_file}")
        print(f"\nNext steps:")
        print(f"  1. Run: python test_auth.py  # Will use profile '{profile_name}'")
        print(f"  2. Or specify profile explicitly in your server config")
    else:
        print(f"\n✗ Failed to create profile '{profile_name}'")
        sys.exit(1)


def cmd_enable_keychain(args):
    """Enable keychain storage command."""
    try:
        import keyring
        
        profile = args[0] if args else "default"
        env_file = ".env" if profile == "default" else f".env.{profile}"
        
        if not os.path.exists(env_file):
            print(f"✗ Error: Profile '{profile}' not found")
            sys.exit(1)
        
        from dotenv import set_key
        set_key(env_file, "SPOTIFY_USE_KEYCHAIN", "true")
        
        print(f"✓ System keychain storage enabled for profile '{profile}'")
        print("\n⚠️  Note: You'll need to re-authenticate for tokens to be saved to keychain")
        print("Run: python test_auth.py")
        
    except ImportError:
        print("✗ Error: keyring package not installed")
        print("\nInstall with: pip install keyring")
        sys.exit(1)


def cmd_disable_keychain(args):
    """Disable keychain storage command."""
    profile = args[0] if args else "default"
    env_file = ".env" if profile == "default" else f".env.{profile}"
    
    if not os.path.exists(env_file):
        print(f"✗ Error: Profile '{profile}' not found")
        sys.exit(1)
    
    from dotenv import set_key
    set_key(env_file, "SPOTIFY_USE_KEYCHAIN", "false")
    
    print(f"✓ System keychain storage disabled for profile '{profile}'")
    print("Tokens will be saved to .env file")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    commands = {
        "revoke": cmd_revoke,
        "audit": cmd_audit,
        "alerts": cmd_alerts,
        "profiles": cmd_profiles,
        "create-profile": cmd_create_profile,
        "enable-keychain": cmd_enable_keychain,
        "disable-keychain": cmd_disable_keychain,
    }
    
    if command in commands:
        try:
            commands[command](args)
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)
    else:
        print(f"✗ Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
