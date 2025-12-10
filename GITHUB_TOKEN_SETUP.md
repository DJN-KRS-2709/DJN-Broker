# 🔑 GitHub Token Setup Guide

## You Just Shared a GitHub Token - Here's What to Do

### ⚠️ URGENT: Revoke the Exposed Token

**The token you shared must be revoked immediately!**

1. Go to: https://github.com/settings/tokens
2. Find the token in your list (look for the most recent one)
3. Click **"Delete"** or **"Revoke"**
4. Confirm deletion

**Why?** This token was shared in plain text and could be logged/cached. GitHub may auto-revoke it, but you should verify manually.

---

## Creating a New Secure Token

### Step 1: Generate Token with Proper Permissions

1. **Go to GitHub Settings:**
   - https://github.com/settings/tokens
   - Click **"Generate new token"** → **"Generate new token (classic)"**

2. **Configure Token:**
   ```
   Name: DJN-Broker-Dev
   Expiration: 90 days (recommended)
   
   Scopes to select:
   ✅ repo (Full control of private repositories)
   ✅ workflow (Update GitHub Action workflows)
   
   Leave unchecked:
   ❌ admin:* (Too much power)
   ❌ delete_repo (Dangerous)
   ❌ All other admin scopes
   ```

3. **Generate and Copy:**
   - Click **"Generate token"**
   - Copy the token immediately (you won't see it again!)
   - It will look like: `ghp_aBc123...` (starts with `ghp_`)

### Step 2: Store Securely in .env File

```bash
# Navigate to project
cd /Users/dejank/Github/DJN\ Broker/DJN-Broker

# Create .env if it doesn't exist
cp .env.example .env

# Edit .env
nano .env
```

Add your token:
```bash
GITHUB_TOKEN=ghp_YourNewTokenHere
```

Save and exit (Ctrl+X, then Y, then Enter in nano).

### Step 3: Verify .env is Protected

```bash
# Check .gitignore includes .env
grep "^\.env$" .gitignore

# If not found, add it
echo ".env" >> .gitignore

# Verify .env is not tracked
git status --ignored | grep ".env"
```

### Step 4: Test Your Token

```python
# Test in Python
python3 << EOF
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('GITHUB_TOKEN')

if token and token.startswith('ghp_'):
    print("✅ GitHub token loaded successfully!")
    print(f"   Token: {token[:8]}...{token[-4:]}")
else:
    print("❌ GitHub token not found or invalid")
EOF
```

---

## Using Your Token in Code

### Python (with python-dotenv)

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Access token
github_token = os.getenv('GITHUB_TOKEN')

# Use with requests
import requests

headers = {
    'Authorization': f'Bearer {github_token}',
    'Accept': 'application/vnd.github+json'
}

response = requests.get('https://api.github.com/user', headers=headers)
print(response.json())
```

### GitHub Actions

Store as a repository secret:

1. Go to: `https://github.com/yourusername/DJN-Broker/settings/secrets/actions`
2. Click **"New repository secret"**
3. Name: `GH_TOKEN` (or `GITHUB_TOKEN` if not already used)
4. Value: Paste your token
5. Click **"Add secret"**

Use in workflow:
```yaml
name: CI
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          token: ${{ secrets.GH_TOKEN }}
      
      - name: Test with token
        env:
          GITHUB_TOKEN: ${{ secrets.GH_TOKEN }}
        run: |
          curl -H "Authorization: Bearer $GITHUB_TOKEN" \
               https://api.github.com/user
```

### Shell Scripts

```bash
#!/bin/bash
# Load .env
source .env

# Use token
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     https://api.github.com/user/repos
```

---

## Token Permissions Explained

### What Each Permission Does:

| Scope | What It Allows | Needed? |
|-------|----------------|---------|
| `repo` | Full control of repositories (read, write, delete) | ✅ Yes (for most CI/CD) |
| `repo:status` | Access commit status (read-only) | ⚠️ Use if you only need read |
| `workflow` | Update GitHub Actions workflows | ✅ Yes (if automating workflows) |
| `write:packages` | Upload packages to GitHub Packages | ❌ Only if publishing packages |
| `admin:org` | Full control of organizations | ❌ Dangerous, avoid! |
| `delete_repo` | Delete repositories | ❌ Never needed for automation |

**Principle of Least Privilege:** Only grant permissions you actually need!

---

## Token Rotation Schedule

Set a reminder to rotate tokens:

```bash
# Add to crontab (runs first day of every quarter)
# 0 9 1 */3 * /path/to/rotate_github_token.sh

# Or use calendar reminder:
# - March 1
# - June 1
# - September 1
# - December 1
```

---

## Troubleshooting

### Token Not Working?

1. **Check token is valid:**
   ```bash
   curl -H "Authorization: Bearer $GITHUB_TOKEN" \
        https://api.github.com/user
   ```

2. **Check permissions:**
   - Go to: https://github.com/settings/tokens
   - Click on your token
   - Verify scopes are correct

3. **Check expiration:**
   - Expired tokens return `401 Unauthorized`
   - Generate a new token if expired

### Token Shows in Git History?

See [SECURITY_GUIDE.md](./SECURITY_GUIDE.md) for emergency response.

---

## Best Practices Summary

✅ **DO:**
- Store tokens in `.env` (never in code)
- Set 90-day expiration
- Use minimal permissions
- Rotate regularly
- Use different tokens for dev/prod

❌ **DON'T:**
- Commit `.env` to git
- Share tokens in chat/email
- Use admin tokens for automation
- Log token values
- Use the same token everywhere

---

## Quick Commands

```bash
# Generate a new token
open https://github.com/settings/tokens/new

# Check if .env is ignored
git check-ignore .env

# View configured token (safely)
python -c "import os; from dotenv import load_dotenv; load_dotenv(); t=os.getenv('GITHUB_TOKEN', ''); print(f'{t[:8]}...{t[-4:]}' if t else 'Not set')"

# Test token with API
curl -H "Authorization: Bearer $(grep GITHUB_TOKEN .env | cut -d '=' -f2)" \
     https://api.github.com/user
```

---

## What's Next?

1. ✅ Revoke the old exposed token
2. ✅ Generate a new secure token
3. ✅ Store it in `.env`
4. ✅ Verify `.env` is in `.gitignore`
5. ✅ Test your token works
6. 📅 Set reminder to rotate in 90 days

**You're all set! Your GitHub token is now secure.** 🔒

---

**Need more help?** See [SECURITY_GUIDE.md](./SECURITY_GUIDE.md) for comprehensive security practices.

