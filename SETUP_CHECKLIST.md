# ✅ Security Setup Checklist

Use this checklist after receiving any new tokens or credentials.

## 🚨 Immediate Actions (If Token Exposed)

- [ ] **Revoke the exposed token immediately**
  - GitHub: https://github.com/settings/tokens
  - Alpaca: Dashboard → API Keys → Delete
  - Other services: See SECURITY_GUIDE.md

- [ ] **Check for unauthorized access**
  - Review recent activity
  - Check trading history (if Alpaca)
  - Review GitHub commits/PRs

- [ ] **Document the incident**
  - When was it exposed?
  - Where was it shared?
  - What permissions did it have?

## 🔐 Secure Setup Process

### 1. Environment File Setup
- [ ] Run setup script: `./setup_env.sh`
- [ ] Edit `.env` with real values: `nano .env`
- [ ] Verify `.env` is in `.gitignore`
- [ ] Test config loads: `python -c "from dotenv import load_dotenv; load_dotenv(); print('OK')"`

### 2. GitHub Token Setup
- [ ] Go to https://github.com/settings/tokens
- [ ] Generate new token (classic)
- [ ] Set expiration: 90 days
- [ ] Grant minimal scopes: `repo`, `workflow` only
- [ ] Copy token and store in `.env`
- [ ] Test token: See GITHUB_TOKEN_SETUP.md

### 3. Alpaca Trading Keys (Paper Mode First!)
- [ ] Go to https://app.alpaca.markets/paper/dashboard/overview
- [ ] Generate new paper trading keys
- [ ] Store `ALPACA_PAPER_API_KEY` and `ALPACA_PAPER_API_SECRET` in `.env`
- [ ] Test connection: `python check_alpaca_account.py`
- [ ] Verify paper trading in `config.yaml`: `paper_trading: true`

### 4. News & Social Media APIs
- [ ] NewsAPI: Get key from https://newsapi.org/account
- [ ] Reddit: Create app at https://www.reddit.com/prefs/apps
- [ ] Store keys in `.env`

### 5. Email Notifications (Optional)
- [ ] Enable 2FA on Gmail
- [ ] Generate app password: https://myaccount.google.com/apppasswords
- [ ] Store `SMTP_PASSWORD` in `.env`

### 6. Verify Security
- [ ] `.env` file exists and has real values
- [ ] `.env` is in `.gitignore`
- [ ] `.env` is NOT tracked by git: `git status --ignored | grep .env`
- [ ] No secrets in code: `grep -r "API_KEY\s*=\s*['\"]" . --exclude=".env"`
- [ ] Test application starts without errors

## 📅 Ongoing Maintenance

### Weekly
- [ ] Review trading logs for anomalies
- [ ] Check email notifications are working
- [ ] Verify paper trading mode is still enabled (if not ready for live)

### Monthly
- [ ] Review API usage and costs
- [ ] Check token expiration dates
- [ ] Review trading performance and learnings

### Quarterly (Every 3 Months)
- [ ] Rotate GitHub token
- [ ] Review and update all API keys
- [ ] Audit security practices
- [ ] Review `.gitignore` and `.env` files

## 🚀 Deployment Checklist

### Before Deploying to Fly.io
- [ ] Test locally with paper trading
- [ ] Verify `.env` has all required keys
- [ ] Set secrets in Fly.io: `./setup_flyio_secrets.sh`
- [ ] Verify secrets: `flyctl secrets list`
- [ ] Deploy: `flyctl deploy`
- [ ] Monitor logs: `flyctl logs`

### Before Switching to Live Trading
- [ ] Complete at least 30 paper trades successfully
- [ ] Win rate > 60%
- [ ] Understand all risks
- [ ] Have risk management rules in place
- [ ] Set `paper_trading: false` in `config.yaml`
- [ ] Update `.env` with live Alpaca keys
- [ ] Start with small capital
- [ ] Monitor constantly for first week

## 📚 Resources

- [SECURITY_GUIDE.md](./SECURITY_GUIDE.md) - Comprehensive security practices
- [GITHUB_TOKEN_SETUP.md](./GITHUB_TOKEN_SETUP.md) - GitHub token management
- [SECURITY_INCIDENT.md](./SECURITY_INCIDENT.md) - Previous incident learnings
- [LIVE_TRADING_GUIDE.md](./LIVE_TRADING_GUIDE.md) - Going live safely

## ❓ Questions?

If you're unsure about any step:
1. Read the detailed guides linked above
2. Test in paper trading mode first
3. Review the code to understand what each key does
4. When in doubt, keep paper trading enabled!

---

**Last Updated:** December 8, 2025
**Next Security Audit:** March 8, 2026

