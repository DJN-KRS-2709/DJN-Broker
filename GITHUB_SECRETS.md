# GitHub Actions repository secrets

In GitHub: open your repo, then Settings, Secrets and variables, Actions, Repository secrets, New repository secret.

Secret names may only use letters, numbers, and underscores. No spaces.

---

**ALPACA_LIVE_API_KEY**  
Name: `ALPACA_LIVE_API_KEY`  
Value: Your Alpaca live account Key ID from the Alpaca website under Live trading and API Keys.

**ALPACA_LIVE_API_SECRET**  
Name: `ALPACA_LIVE_API_SECRET`  
Value: Your Alpaca live account secret key from the same Live API Keys page.

**ALPACA_PAPER_API_KEY**  
Name: `ALPACA_PAPER_API_KEY`  
Value: Your Alpaca paper account Key ID from Paper trading and API Keys.

**ALPACA_PAPER_API_SECRET**  
Name: `ALPACA_PAPER_API_SECRET`  
Value: Your Alpaca paper account secret key from the same Paper API Keys page.

**REDDIT_CLIENT_ID**  
Name: `REDDIT_CLIENT_ID`  
Value: The client id from a Reddit app you create at reddit.com prefs apps.

**REDDIT_CLIENT_SECRET**  
Name: `REDDIT_CLIENT_SECRET`  
Value: The secret from that same Reddit app.

**REDDIT_USER_AGENT**  
Name: `REDDIT_USER_AGENT`  
Value: A text string Reddit expects, for example DJNBrokerBot/1.0 by yourusername

**NEWSAPI_KEY**  
Name: `NEWSAPI_KEY`  
Value: Your API key from newsapi.org if you use NewsAPI. Optional if you rely on RSS only.

**NOTIFICATION_EMAIL**  
Name: `NOTIFICATION_EMAIL`  
Value: Email address that should receive trading notifications. Optional.

**SMTP_EMAIL**  
Name: `SMTP_EMAIL`  
Value: The email account used to send mail. Optional.

**SMTP_PASSWORD**  
Name: `SMTP_PASSWORD`  
Value: Password or app password for that email account. Optional.

---

After saving secrets, run the workflow under Actions, Automated Trading Bot, Run workflow.
