# 🔐 Quick Security Reference Card

**Keep this handy for quick lookups!**

---

## 🚨 Emergency: Token Exposed

```bash
# 1. REVOKE IMMEDIATELY
open https://github.com/settings/tokens  # GitHub
open https://app.alpaca.markets/paper/dashboard/overview  # Alpaca

# 2. Generate new token and update .env
nano .env

# 3. Test it works
python -c "from dotenv import load_dotenv; load_dotenv(); print('OK')"
```

---

## 📦 Quick Setup (New Project)

```bash
cd /Users/dejank/Github/DJN\ Broker/DJN-Broker

# 1. Create .env
./setup_env.sh

# 2. Edit with your credentials
nano .env

# 3. Verify security
git status --ignored | grep .env  # Should show ".env"
grep "^\.env$" .gitignore          # Should find it

# 4. Test
python check_alpaca_account.py
```

---

## 🔑 Most Important Environment Variables

```bash
# Paper Trading (Safe - Start Here!)
ALPACA_PAPER_API_KEY=PKxxxxxx
ALPACA_PAPER_API_SECRET=xxxxxxxx

# GitHub (for CI/CD)
GITHUB_TOKEN=ghp_xxxxxx

# Email Notifications
NOTIFICATION_EMAIL=you@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx

# News & Social
NEWSAPI_KEY=xxxxxx
REDDIT_CLIENT_ID=xxxxxx
REDDIT_CLIENT_SECRET=xxxxxx
```

---

## ✅ Security Self-Check

```bash
# Is .env protected?
cat .gitignore | grep "^\.env$"  # Should print ".env"

# Is .env tracked by git?
git ls-files | grep ".env"  # Should be EMPTY

# Are there secrets in code?
grep -r "API_KEY\s*=\s*['\"]" . --exclude-dir=.git --exclude=".env"  # Should be EMPTY

# Can Python load .env?
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ OK' if os.getenv('ALPACA_PAPER_API_KEY') else '❌ NO KEYS')"
```

---

## 🔄 Token Rotation (Every 90 Days)

```bash
# 1. Generate new token
open https://github.com/settings/tokens/new

# 2. Update .env
nano .env

# 3. Test
python -c "from dotenv import load_dotenv; load_dotenv(); print('OK')"

# 4. Delete old token
open https://github.com/settings/tokens

# 5. Set reminder for 90 days from now
```

---

## 📊 Check Token Permissions

### GitHub Token Scopes
```bash
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     https://api.github.com/user -I | grep "X-OAuth-Scopes"
```

**Should see:** `repo, workflow` (minimal permissions)  
**Should NOT see:** `admin:org, delete_repo` (too powerful!)

---

## 🚀 Deploy Secrets to Fly.io

```bash
# Sync all secrets from .env
./setup_flyio_secrets.sh

# Verify (values hidden)
flyctl secrets list

# Individual secret update
flyctl secrets set GITHUB_TOKEN="ghp_newtoken"
```

---

## 🔍 Audit Git History for Secrets

```bash
# Search for common secret patterns
git log --all --full-history -S "ALPACA_API_KEY"
git log --all --full-history -S "ghp_"
git log --all --full-history -S "password"

# Check if .env was ever committed
git log --all --full-history -- .env

# If found secrets, see SECURITY_INCIDENT.md
```

---

## 📝 Testing Credentials

### Test Alpaca Connection
```bash
python check_alpaca_account.py
```

Expected output:
```
✅ Connected to Alpaca (PAPER trading)
Account: $99000.00 portfolio
```

### Test GitHub Token
```bash
curl -H "Authorization: Bearer $(grep GITHUB_TOKEN .env | cut -d '=' -f2)" \
     https://api.github.com/user | jq '.login'
```

### Test Email
```python
python -c "
from utils.email_notifier import send_trading_summary
summary = {'avg_sentiment': 0.5, 'n_signals': 3}
send_trading_summary(summary, 'your@email.com')
"
```

---

## ⚠️ Before Going Live

- [ ] Completed 30+ successful paper trades
- [ ] Win rate > 60%
- [ ] Fully understand risks
- [ ] Have `ALPACA_LIVE_API_KEY` ready
- [ ] Set `paper_trading: false` in `config.yaml`
- [ ] Start with small capital ($100-500)
- [ ] Monitor constantly first week

---

## 📚 Full Documentation

- **Comprehensive Guide:** [SECURITY_GUIDE.md](./SECURITY_GUIDE.md)
- **GitHub Tokens:** [GITHUB_TOKEN_SETUP.md](./GITHUB_TOKEN_SETUP.md)
- **Setup Checklist:** [SETUP_CHECKLIST.md](./SETUP_CHECKLIST.md)
- **Previous Incident:** [SECURITY_INCIDENT.md](./SECURITY_INCIDENT.md)

---

## 🆘 When In Doubt

**Golden Rules:**
1. 🚫 Never commit `.env` to git
2. 🔄 Rotate tokens every 90 days
3. 🎯 Use minimal permissions
4. 📝 Test in paper mode first
5. 🔐 Revoke immediately if exposed

**Still Unsure?** Read the full guides or ask questions!

---

**Remember:** A few minutes of security diligence prevents hours of incident response! 🛡️

