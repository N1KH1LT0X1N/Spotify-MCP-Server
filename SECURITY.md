# Security Policy

## 🔒 Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## 🚨 Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### For Critical Issues (exposed credentials, RCE, etc.)

1. **DO NOT** open a public GitHub issue
2. Email the maintainer directly (check package.json for contact)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### For Non-Critical Issues

1. Open a GitHub issue with label `security`
2. Provide detailed information about the issue
3. Wait for maintainer response

## 🛡️ Security Best Practices for Users

### Protect Your Credentials

1. **Never commit `.env` files** to version control
2. **Rotate credentials regularly** (every 90 days)
3. **Use environment-specific credentials** (dev, staging, prod)
4. **Enable keyring/keychain** for encrypted token storage

### Token Management

1. **Tokens auto-refresh** 60 seconds before expiry
2. **Revoke access** when no longer needed:
   ```bash
   python scripts/enterprise_cli.py revoke
   ```
3. **Monitor audit logs** for suspicious activity:
   ```bash
   python scripts/enterprise_cli.py audit
   ```

### OAuth Security

1. **Use `127.0.0.1`** (not `localhost`) for redirect URI
2. **Never share** authorization codes or tokens
3. **Verify redirect URIs** in Spotify Developer Dashboard
4. **Use HTTPS** for production deployments

### Code Security

1. **Keep dependencies updated**:
   ```bash
   pip install --upgrade -r requirements-dev.txt
   ```
2. **Run security scans**:
   ```bash
   # With pre-commit hooks
   pre-commit run --all-files
   ```
3. **Review audit logs** regularly:
   ```bash
   cat .auth_audit.json | jq '.alerts'
   ```

## 🔍 Known Security Considerations

### 1. Local Token Storage

**Issue:** Tokens stored in `.env` or OS keychain

**Mitigation:**
- `.env` file permissions should be `600` (user read/write only)
- Use keyring for encrypted storage:
  ```bash
  python scripts/enterprise_cli.py enable-keychain
  ```

### 2. OAuth Redirect URI

**Issue:** Using `http://127.0.0.1:8888/callback` (not HTTPS)

**Impact:** 
- Acceptable for localhost development
- **DO NOT** use HTTP redirect URIs for production/public deployments

**Mitigation:**
- For production, use HTTPS redirect URI
- Update in both `.env` and Spotify Developer Dashboard

### 3. Rate Limiting

**Issue:** No client-side rate limiting

**Impact:**
- Excessive API calls could hit Spotify rate limits
- Temporary API access suspension

**Mitigation:**
- Server implements exponential backoff
- Monitor usage in audit logs
- Implement client-side throttling if needed

## 🔐 Security Features

### Implemented

- ✅ OAuth 2.0 authentication
- ✅ Automatic token refresh
- ✅ Token rotation tracking
- ✅ Audit logging
- ✅ Keyring integration (optional)
- ✅ Token revocation support
- ✅ Multi-profile support
- ✅ Input validation

### Planned

- ⏳ PKCE (Proof Key for Code Exchange) support
- ⏳ Client-side rate limiting
- ⏳ Token encryption at rest
- ⏳ Automated security scanning in CI/CD

## 📚 Security Resources

- [Spotify Security Best Practices](https://developer.spotify.com/documentation/general/guides/authorization-guide/)
- [OAuth 2.0 Security](https://oauth.net/2/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security](https://python.readthedocs.io/en/latest/library/security_warnings.html)

## ✅ Security Checklist for Contributors

Before submitting a PR, ensure:

- [ ] No hardcoded credentials in code or docs
- [ ] No sensitive data in commit messages
- [ ] Input validation for all user inputs
- [ ] Proper error handling (no stack traces to users)
- [ ] Dependencies are up to date
- [ ] Tests pass security checks
- [ ] Documentation updated if security changes

## 📞 Contact

For security-related questions or concerns:
- Check existing issues with `security` label
- Open a new issue (for non-critical items)
- Email maintainer directly (for critical issues)

---

**Last Updated:** November 5, 2025
