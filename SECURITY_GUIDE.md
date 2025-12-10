# 🔐 Security Guide - Token & Credentials Management

## Table of Contents
1. [Quick Setup](#quick-setup)
2. [Security Best Practices](#security-best-practices)
3. [Token Management](#token-management)
4. [Emergency Response](#emergency-response)
5. [Deployment Security](#deployment-security)

---

## Quick Setup

### 1. Initial Setup

```bash
# Navigate to project directory
cd /Users/dejank/Github/DJN\ Broker/DJN-Broker

# Copy the template
cp .env.example .env

# Open .env and fill in your credentials
nano .env  # or use your preferred editor
```

### 2. Verify .env is Protected

```bash
# Check that .env is in .gitignore
grep "^\.env$" .gitignore

# Verify .env is not tracked by git
git status --ignored | grep ".env"
```

### 3. Test Your Configuration

```python
# Run this to verify environment variables load correctly
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ Config loaded!' if os.getenv('ALPACA_PAPER_API_KEY') else '❌ No keys found')"
```

---

## Security Best Practices

### ✅ DO's

1. **Use Environment Variables for ALL Secrets**
   ```python
   # Good
   api_key = os.getenv('ALPACA_PAPER_API_KEY')
   
   # Bad
   api_key = "PK1234567890"
   ```

2. **Use Different Tokens for Different Environments**
   - Development: Paper trading keys, sandbox APIs
   - Production: Live trading keys (with caution!)
   - CI/CD: Read-only tokens with minimal permissions

3. **Rotate Tokens Regularly**
   - GitHub tokens: Every 90 days
   - Trading API keys: Every 6 months
   - Email passwords: Every year
   - Immediately after any security incident

4. **Use Minimal Permissions**
   - GitHub tokens: Only grant `repo` and `workflow` if needed
   - Trading APIs: Use paper trading keys for testing
   - Never use admin/owner tokens for automation

5. **Set Expiration Dates**
   - GitHub: Set 90-day expiration when creating tokens
   - APIs: Use short-lived tokens when possible

### ❌ DON'Ts

1. **Never Commit Secrets to Git**
   ```bash
   # Bad - these should NEVER be in code
   ALPACA_KEY = "PK1234567890"
   password = "mypassword123"
   ```

2. **Never Share Tokens in Chat/Email**
   - Use secure password managers (1Password, Bitwarden)
   - Share through encrypted channels only

3. **Never Log Secrets**
   ```python
   # Bad
   log.info(f"Using API key: {api_key}")
   
   # Good
   log.info("API key configured")
   ```

4. **Never Use Production Secrets in Development**
   - Keep paper/sandbox keys for local dev
   - Only use live keys in production environment

---

## Token Management

### GitHub Personal Access Tokens

**Creating a Secure Token:**

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Configure:
   - **Name**: `DJN-Broker-CI` (descriptive name)
   - **Expiration**: 90 days
   - **Scopes**:
     - `repo` (if you need full repo access)
     - `workflow` (if using GitHub Actions)
     - Avoid `admin:*` unless absolutely necessary

4. Copy the token IMMEDIATELY (you can't see it again)
5. Store in `.env` file:
```bash
GITHUB_TOKEN=ghp_YourTokenHere
```

**Rotating GitHub Tokens:**

```bash
# 1. Generate new token (see above)
# 2. Update .env with new token
# 3. Test your workflows
# 4. Delete old token from GitHub settings
```

### Alpaca Trading API Keys

**Paper Trading (Safe):**
- Go to: https://app.alpaca.markets/paper/dashboard/overview
- Click "Generate API Keys"
- Store in `.env`:
  ```bash
  ALPACA_PAPER_API_KEY=PKxxxxxx
  ALPACA_PAPER_API_SECRET=xxxxxxxx
  ```

**Live Trading (⚠️ REAL MONEY!):**
- Only use when you're 100% confident
- Go to: https://app.alpaca.markets/live/dashboard/overview
- Generate separate keys
- Store in `.env`:
  ```bash
  ALPACA_LIVE_API_KEY=AKxxxxxx
  ALPACA_LIVE_API_SECRET=xxxxxxxx
  ```

### Reddit API Keys

1. Go to: https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in:
   - **Name**: DJN-Broker
   - **Type**: Script
   - **Redirect URI**: http://localhost:8080
4. Copy Client ID and Secret
5. Store in `.env`:
   ```bash
   REDDIT_CLIENT_ID=xxxxxxxx
   REDDIT_CLIENT_SECRET=xxxxxxxx
   REDDIT_USER_AGENT=DJN-Broker:v1.0 (by /u/your_username)
   ```

### Email (Gmail App Password)

1. Enable 2FA on your Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate app password for "Mail"
4. Store in `.env`:
   ```bash
   NOTIFICATION_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

---

## Emergency Response

### If a Token is Leaked

**IMMEDIATE ACTIONS:**

1. **Revoke the Token**
   - GitHub: https://github.com/settings/tokens → Delete
   - Alpaca: Dashboard → Revoke keys
   - Reddit: https://www.reddit.com/prefs/apps → Delete app
   - Email: Revoke app password

2. **Check for Unauthorized Access**
   - GitHub: Check recent activity, commits, PRs
   - Alpaca: Check trading history, positions, orders
   - Email: Check sent items, filters, forwarding rules

3. **Generate New Token**
   - Follow the token creation steps above
   - Update `.env` with new credentials
   - Test your application

4. **Review Security**
   - Check `.gitignore` includes `.env`
   - Scan git history: `git log --all -S "API_KEY"`
   - If secrets in history, see [SECURITY_INCIDENT.md](./SECURITY_INCIDENT.md)

### Cleaning Git History

If you accidentally committed secrets:

```bash
# ⚠️ WARNING: This rewrites git history - coordinate with team first!

# Install BFG Repo-Cleaner
brew install bfg  # macOS

# Backup your repo
cp -r . ../djn-broker-backup

# Remove .env from all commits
bfg --delete-files .env

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (⚠️ DANGER!)
git push origin --force --all
```

**Better approach:** Contact GitHub Support to purge sensitive data.

---

## Deployment Security

### Fly.io Secrets

```bash
# Set secrets from .env file
source .env

flyctl secrets set \
  ALPACA_PAPER_API_KEY="$ALPACA_PAPER_API_KEY" \
  ALPACA_PAPER_API_SECRET="$ALPACA_PAPER_API_SECRET" \
  NEWSAPI_KEY="$NEWSAPI_KEY" \
  REDDIT_CLIENT_ID="$REDDIT_CLIENT_ID" \
  REDDIT_CLIENT_SECRET="$REDDIT_CLIENT_SECRET" \
  SMTP_PASSWORD="$SMTP_PASSWORD"

# Verify secrets are set (values hidden)
flyctl secrets list
```

### GitHub Actions Secrets

1. Go to: https://github.com/yourusername/DJN-Broker/settings/secrets/actions
2. Click "New repository secret"
3. Add each secret:
   - Name: `ALPACA_PAPER_API_KEY`
   - Value: (paste from `.env`)
4. Use in workflows:
   ```yaml
   env:
     ALPACA_PAPER_API_KEY: ${{ secrets.ALPACA_PAPER_API_KEY }}
   ```

### Docker Secrets

**Never build secrets into images:**

```dockerfile
# Bad - secrets in image layers
ENV ALPACA_API_KEY=PK123456

# Good - use runtime environment
ENV ALPACA_API_KEY=${ALPACA_API_KEY}
```

**Use docker-compose with env_file:**

```yaml
services:
  djn-broker:
    image: djn-broker:latest
    env_file:
      - .env  # Not committed to git
```

---

## Quick Reference

### Environment Variables Checklist

Essential for trading:
- [ ] `ALPACA_PAPER_API_KEY`
- [ ] `ALPACA_PAPER_API_SECRET`

Optional but recommended:
- [ ] `NEWSAPI_KEY`
- [ ] `REDDIT_CLIENT_ID`
- [ ] `REDDIT_CLIENT_SECRET`
- [ ] `NOTIFICATION_EMAIL`
- [ ] `SMTP_PASSWORD`

For CI/CD:
- [ ] `GITHUB_TOKEN`

### Security Audit Commands

```bash
# Check for secrets in git history
git log --all --full-history -S "ALPACA" -S "API_KEY"

# Check for secrets in current codebase
grep -r "API_KEY\s*=\s*['\"]" . --exclude-dir=.git --exclude=".env*"

# Verify .gitignore
cat .gitignore | grep -E "\.env$|secrets|credentials"

# Check what's being tracked
git ls-files | grep -E "\.env$|secret|credential"
```

---

## Resources

- [GitHub Token Best Practices](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Alpaca API Security](https://alpaca.markets/docs/api-references/trading-api/)
- [OWASP Secrets Management](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password)
- [12 Factor App - Config](https://12factor.net/config)

---

## Support

If you discover a security vulnerability:
1. **DO NOT** open a public GitHub issue
2. Revoke affected credentials immediately
3. Review this guide's emergency response section
4. Document the incident for future reference

---

**Remember:** Security is not a one-time setup—it's an ongoing practice. Review this guide regularly and keep your tokens secure! 🔒

