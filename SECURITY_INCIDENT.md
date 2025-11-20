# 🚨 SECURITY INCIDENT - API Keys Exposed on GitHub

**Date:** November 20, 2025  
**Severity:** **CRITICAL**  
**Status:** Repository cleaned, but you MUST revoke all exposed keys

---

## What Happened

Your `.env` file containing ALL API keys was accidentally committed to GitHub and publicly exposed from **November 10 - November 20, 2025** (10 days).

GitHub's security scanning detected "Generic High Entropy Secret" and sent alerts to `dejank@spotify.com`.

---

## What I've Done

✅ Removed `.env` from ALL git history using `git filter-branch`  
✅ Force pushed cleaned history to GitHub  
✅ Updated your git identity to `DJN-KRS-2709 <dejan.krstic@web.de>`  
✅ Verified `.env` is in `.gitignore` to prevent future commits  

---

## ⚠️ CRITICAL: YOU MUST DO THIS NOW

**All exposed API keys MUST be revoked and regenerated immediately.**

### 1. 🔴 ALPACA API KEYS (HIGHEST PRIORITY - REAL MONEY!)

**Your live trading account with $569.38 was exposed!**

🚨 **LIVE ACCOUNT (REAL MONEY):**
- Go to: https://app.alpaca.markets/paper/dashboard/overview
- Navigate to: Account → API Keys
- **DELETE these exposed keys immediately:**
  - Key ID: `AKBFSSYMZFJTQCWO7YLN5IL4LN`
  - Secret: `D7KQSwTnoT8dz3yBczfyHkMykedLjGB2rkNVDMzW7Q36`
- Generate NEW keys
- Update `.env` with new keys

📝 **PAPER ACCOUNT:**
- Same process for paper trading keys:
  - Key ID: `PKJDXT4IJUTYOYIRMK5Q37EUQS`
  - Secret: `4XGJWx9knYpHDZL4Rjkqxum8hwrt4xNnmVo3qEh82Jf5`

### 2. 📧 EMAIL CREDENTIALS

**Your Gmail app password was exposed:**
- Go to: https://myaccount.google.com/apppasswords
- **Revoke exposed password:** `jqni mhzm jsia rquw`
- Generate a NEW app password
- Update `.env` with new password

### 3. 🔑 REDDIT API KEYS

**Your Reddit API credentials were exposed:**
- Go to: https://www.reddit.com/prefs/apps
- Find your app (should show Client ID: `OLf2IiXSy-WBCL7WEo4sFA`)
- **DELETE the app** or **regenerate the secret**
- Create a new Reddit app if needed
- Update `.env` with new credentials

### 4. 📰 NEWS API KEY

**Your NewsAPI key was exposed:**
- Go to: https://newsapi.org/account
- **Revoke key:** `4acce90c43794adca3cba5a9e33e1f52`
- Generate a NEW API key (free tier: 100 requests/day)
- Update `.env` with new key

### 5. 📊 TWELVE DATA API KEY

**Your Twelve Data API key was exposed:**
- Go to: https://twelvedata.com/account/api-keys
- **Revoke key:** `018688dead934547a18838affa96cc47`
- Generate a NEW API key
- Update `.env` with new key

### 6. ☁️ FLY.IO SECRETS

**After regenerating ALL keys above, update Fly.io:**

```bash
cd "/Users/dejank/Github/DJN Broker/DJN-Broker"

# Update Fly.io with NEW credentials
flyctl secrets set \
  ALPACA_PAPER_API_KEY="<NEW_PAPER_KEY>" \
  ALPACA_PAPER_API_SECRET="<NEW_PAPER_SECRET>" \
  ALPACA_LIVE_API_KEY="<NEW_LIVE_KEY>" \
  ALPACA_LIVE_API_SECRET="<NEW_LIVE_SECRET>" \
  REDDIT_CLIENT_ID="<NEW_REDDIT_ID>" \
  REDDIT_CLIENT_SECRET="<NEW_REDDIT_SECRET>" \
  NEWSAPI_KEY="<NEW_NEWS_KEY>" \
  TWELVE_DATA_API_KEY="<NEW_TWELVE_KEY>" \
  SMTP_PASSWORD="<NEW_GMAIL_PASSWORD>" \
  --app djn-broker
```

---

## How This Happened

1. The `.env` file was committed to git (likely with `git add -A` or `git add .`)
2. It was pushed to GitHub despite being in `.gitignore` (already existed in git)
3. GitHub's secret scanning detected it
4. Alerts sent to `dejank@spotify.com`

---

## Prevention for Future

✅ **Already Done:**
- `.env` is in `.gitignore`
- Removed from all git history
- Updated git identity to correct account

🔒 **Best Practices:**
- NEVER run `git add .env` manually
- Always use `git add -A` only after reviewing `git status`
- Use `git secrets` or pre-commit hooks to prevent secret commits
- Rotate API keys regularly (every 90 days)

---

## Timeline

- **Nov 10, 2025:** `.env` first committed with all secrets
- **Nov 10-20, 2025:** Secrets publicly visible on GitHub
- **Nov 20, 2025:** GitHub detected secrets, sent alerts
- **Nov 20, 2025:** Repository cleaned, secrets removed from history

---

## Questions?

If you need help regenerating any keys or updating Fly.io, let me know!

**Priority order:**
1. Alpaca LIVE keys (real money!)
2. Gmail password
3. Alpaca paper keys
4. Reddit, NewsAPI, Twelve Data
5. Update Fly.io with all new keys

