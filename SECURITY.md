# Security Policy

## Overview

AutoHyperFlask takes security seriously. This document outlines our security practices and provides guidance for secure deployment.

## Reporting Security Issues

If you discover a security vulnerability, please report it responsibly:

- **DO NOT** create a public GitHub issue for security vulnerabilities
- Report security issues via [GitHub Security Advisories](https://github.com/realityinspector/auto-hyperflask/security/advisories/new)
- Or email the maintainers directly if you prefer
- Include detailed information about the vulnerability:
  - Steps to reproduce
  - Potential impact
  - Suggested fix (if you have one)
- Allow reasonable time for the issue to be addressed before public disclosure

## Security Best Practices

### 1. Environment Variables

**NEVER commit sensitive credentials to version control.**

All sensitive configuration must be stored in environment variables:

- `FLASK_SECRET_KEY` - Strong random key for session management
- `DATABASE_URL` - Database connection string with credentials
- `SMTP_PASSWORD` - Email service credentials (if used)

**How to generate secure keys:**

```bash
# Generate a secure Flask secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Configuration Files

The following files contain placeholders and **must** be configured with environment variables:

- `config_prod.yml` - Uses `${DATABASE_URL}` and `${FLASK_SECRET_KEY}`
- `config_postgres.yml` - Uses `${DATABASE_URL}` and `${FLASK_SECRET_KEY}`

**Never hardcode credentials** in configuration files.

### 3. First User Admin

The first user to register through the frontend automatically becomes an administrator. This is by design for initial setup.

**Security implications:**
- Deploy with user registration disabled initially
- Register the first admin user
- Then enable public registration OR implement invitation-only registration

### 4. Database Security

**Development:**
- Uses SQLite (file-based database)
- Database files are gitignored
- Suitable for testing only

**Production:**
- Uses PostgreSQL with TLS/SSL (`sslmode=require`)
- Credentials passed via `DATABASE_URL` environment variable
- Database backups should be encrypted

### 5. Dependencies

This project uses:
- `detect-secrets` - Automated secret scanning
- `trufflehog3` - Additional secret detection
- Regular dependency updates via Dependabot (when hosted on GitHub)

**To scan for secrets:**

```bash
# Run secret detection
detect-secrets scan --all-files .

# Check for high-entropy strings
trufflehog3 -v --no-history .
```

### 6. Deployment Checklist

Before deploying to production:

- [ ] Set strong `FLASK_SECRET_KEY` environment variable
- [ ] Configure `DATABASE_URL` with production database
- [ ] Use PostgreSQL with TLS (`sslmode=require`)
- [ ] Enable HTTPS/TLS for web traffic
- [ ] Register first admin user before enabling public registration
- [ ] Review and update `ALLOWED_HOSTS` if applicable
- [ ] Disable debug mode (`DEBUG=false`)
- [ ] Run security scan: `detect-secrets scan --all-files .`
- [ ] Run tests: `python3 -m pytest tests/ -v`
- [ ] Review application logs for sensitive data leakage

### 7. Replit Deployment

When deploying on Replit:

1. **Set Secrets** (not environment variables):
   - `FLASK_SECRET_KEY`
   - `DATABASE_URL` (if using external PostgreSQL)

2. **Never** store secrets in `.replit` or any committed file

3. Replit's deployment uses `config_prod.yml` which reads from environment variables

### 8. Known Security Considerations

**Session Management:**
- Sessions use Flask's default secure cookie implementation
- Requires `FLASK_SECRET_KEY` to be set
- Sessions are signed but not encrypted

**Authentication:**
- Uses `hyperflask-users` for authentication
- Passwords are hashed with industry-standard algorithms
- No plain-text password storage

**File Uploads:**
- Not yet implemented
- When implementing, validate file types and sanitize filenames
- Store uploads outside web root
- Scan uploaded files for malware

**SQL Injection:**
- SQLAlchemy ORM provides protection against SQL injection
- Always use parameterized queries
- Never concatenate user input into SQL

**XSS Protection:**
- Jinja2 templates auto-escape HTML by default
- Use `{{ variable }}` for safe output
- Only use `{{ variable|safe }}` for trusted content

## Security Testing

### Automated Testing

```bash
# Run all tests including security checks
npm run build
python3 -m pytest tests/ -v

# Run secret detection
detect-secrets scan --all-files .
```

### Manual Security Review

Before each release:

1. Review all configuration files for hardcoded secrets
2. Check `.gitignore` includes all sensitive files
3. Audit new dependencies for known vulnerabilities
4. Test authentication and authorization flows
5. Verify HTTPS is enforced in production

## Excluded from Security Scope

The following are NOT considered security vulnerabilities:

- Features working as documented
- Issues only affecting development/test environments
- Theoretical attacks without proof of concept
- Social engineering of administrators
- Physical access to servers

## Security Updates

We aim to address security vulnerabilities within:

- **Critical**: 24-48 hours
- **High**: 1 week
- **Medium**: 2 weeks
- **Low**: Next regular release

## License

This security policy is licensed under CC0 1.0 Universal.
