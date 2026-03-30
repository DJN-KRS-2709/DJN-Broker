# GitHub Actions repository secrets

GitHub: repo → **Settings** → **Secrets and variables** → **Actions** → **Repository secrets**.

Secret names may only use letters, numbers, and underscores (no spaces).

---

## Required for live trading + CI

| Name | Value |
|------|--------|
| **ALPACA_LIVE_API_KEY** | Live **Key ID** (Alpaca dashboard → **Live** → API keys). ASCII only; re-paste if you copied fancy characters. |
| **ALPACA_LIVE_API_SECRET** | Live **secret** (shown once when created; regenerate if lost). |
| **ALPACA_PAPER_API_KEY** | Paper Key ID (used for some market-data fallbacks). |
| **ALPACA_PAPER_API_SECRET** | Paper secret. |

---

## Strongly recommended

| Name | Value |
|------|--------|
| **REDDIT_CLIENT_ID** | From [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) (create a “script” app). |
| **REDDIT_CLIENT_SECRET** | Same app. |
| **REDDIT_USER_AGENT** | One line, e.g. `DJNBrokerBot/1.0 by YourRedditUsername` (not a numeric user id). |

---

## Optional

| Name | Value |
|------|--------|
| **NEWSAPI_KEY** | From [newsapi.org](https://newsapi.org). If empty, the bot can use RSS only. |
| **NOTIFICATION_EMAIL** | Where to send the daily summary email. |
| **SMTP_EMAIL** | Sender mailbox (e.g. Gmail). |
| **SMTP_PASSWORD** | App password if using Gmail + 2FA. |
| **SMTP_SERVER** | Defaults to `smtp.gmail.com` if unset. |
| **SMTP_PORT** | Defaults to `587` if unset. |

---

## Verify locally before debugging CI

From the repo root (with `.env` or exported vars):

```bash
python3 verify_live_setup.py
```

---

## After changing secrets

Use **Actions** → **Automated Trading Bot** → **Run workflow** on branch **main** (or wait for the schedule).  
Judge **Node** / workflow warnings on a **new** run’s **Workflow file** tab (commit SHA), not an old run number.
