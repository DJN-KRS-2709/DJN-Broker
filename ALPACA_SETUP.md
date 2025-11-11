# 🔐 Alpaca Setup Instructions

## ⚠️  CRITICAL INFORMATION ⚠️

You provided the **LIVE TRADING** endpoint:
- Endpoint: `https://api.alpaca.markets`
- ⚠️  This endpoint uses **REAL MONEY**
- Your API Key: `AKUSSE272MUBVFISBTAFSEJUSW`

---

## 🛑 BEFORE PROCEEDING

### **I STRONGLY RECOMMEND:**

1. **Start with Paper Trading First** 🏃‍♂️
   - Paper endpoint: `https://paper-api.alpaca.markets`
   - Uses fake money ($100k virtual)
   - Zero risk, real market data
   - Run for 1-2 weeks before going live

2. **Verify Account Balance** 💰
   - Check how much is in account 987064219
   - Only risk money you can afford to lose
   - Recommended starting capital: $500-$1,000

3. **Complete 1 Week Paper Trading** 📊
   - Collect performance data
   - Verify strategy works
   - Test all safety features

---

## 📝 What I Need From You

### **Missing Information:**

1. **API Secret** (You only provided the key)
   - Go to: https://app.alpaca.markets/paper/dashboard/overview
   - Click on "View" next to your API key
   - Copy the **Secret** (starts with something like `abc123...`)

2. **Confirm Account Type:**
   - Is account 987064219 a **Cash** or **Margin** account?
   - Are you approved for **Pattern Day Trading**?

3. **Your Decision:**
   - Do you want to start with **Paper Trading** (recommended)?
   - Or proceed directly to **Live Trading** (higher risk)?

---

## 🔧 Setup Instructions

### **Step 1: Create .env File**

```bash
cd /Users/dejank/Downloads/cursor_free_trading_mvp
nano .env
```

### **Step 2: Add Your Credentials**

```bash
# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=trading-bot/1.0

# NewsAPI (optional)
NEWSAPI_KEY=your_newsapi_key

# ⚠️  ALPACA API - CHOOSE YOUR MODE ⚠️

# Your API Key (you provided this)
ALPACA_API_KEY=AKUSSE272MUBVFISBTAFSEJUSW

# Your API Secret (NEED THIS - get from Alpaca dashboard)
ALPACA_API_SECRET=your_secret_here

# OPTION A: Paper Trading (RECOMMENDED - Start here!)
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# OPTION B: Live Trading (REAL MONEY - Only after paper success!)
# ALPACA_BASE_URL=https://api.alpaca.markets
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

### **Step 3: Install Alpaca Library**

```bash
pip3 install alpaca-trade-api
```

### **Step 4: Update config.yaml**

```bash
nano config.yaml
```

**Find the live_trading section and update:**

```yaml
live_trading:
  enabled: true                    # Enable trading
  broker: "alpaca"                 # Using Alpaca
  account_number: "987064219"      # Your account
  
  # CHOOSE YOUR MODE:
  paper_mode: true                 # true = Paper (SAFE), false = Live (REAL MONEY)
  
  # Start conservative
  initial_capital: 500             # Start with $500
  max_position_size_pct: 0.10     # 10% per trade
  
  # Safety limits
  daily_loss_limit_pct: 0.03      # Stop if down 3%
  max_trades_per_day: 5           # Max 5 trades/day
  max_consecutive_losses: 3        # Stop after 3 losses
  
  # Alerts (UPDATE THIS!)
  alert_email: "your_email@example.com"
```

### **Step 5: Test Connection**

```bash
python3 -c "
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_API_SECRET'),
    os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets'),
    api_version='v2'
)

account = api.get_account()
print(f'✅ Connected to Alpaca!')
print(f'Account: {account.account_number}')
print(f'Status: {account.status}')
print(f'Buying Power: \${float(account.buying_power):,.2f}')
print(f'Portfolio Value: \${float(account.portfolio_value):,.2f}')
"
```

---

## 🎯 Recommended Approach

### **Week 1: Paper Trading** (THIS WEEK)
1. Set `paper_mode: true` in config.yaml
2. Use paper API endpoint
3. Let bot run for full week
4. Monitor performance daily
5. Review all trades and signals

### **Week 2: Decision Point**
**Only proceed to live if:**
- ✅ Paper trading shows positive results
- ✅ Win rate >50%
- ✅ No system errors
- ✅ You're comfortable with the risk
- ✅ Account is funded appropriately

### **Week 2+: Live Trading** (if successful)
1. Switch to `paper_mode: false`
2. Use live API endpoint
3. Start with small capital ($500-1000)
4. Monitor HOURLY
5. Gradually scale up if successful

---

## 🛡️ Safety Features Active

Your bot has these protections:
- ✅ Daily loss limit (stops at -3%)
- ✅ Max trades per day (5 max)
- ✅ Consecutive loss protection (stops after 3)
- ✅ Kill switch (create STOP_TRADING.txt to halt)
- ✅ Pre-trade validation
- ✅ Position size limits

---

## 🚨 Emergency Procedures

### **If Something Goes Wrong:**

1. **Stop the bot immediately:**
   ```bash
   # Method 1: Kill switch
   touch /Users/dejank/Downloads/cursor_free_trading_mvp/STOP_TRADING.txt
   
   # Method 2: Kill process
   ps aux | grep schedule_runner
   kill [PID]  # Replace [PID] with actual process ID
   ```

2. **Close all positions in Alpaca:**
   - Go to: https://app.alpaca.markets/trading/portfolio
   - Click "Close All Positions"

3. **Review what happened:**
   ```bash
   tail -100 scheduler.log
   cat storage/intended_orders.csv
   ```

---

## 📞 Next Steps

**Please provide:**

1. ✅ **API Secret** (you gave me the key, need the secret)
2. ✅ **Confirm Paper or Live** - which do you want to start with?
3. ✅ **Your email** for alerts
4. ✅ **Account balance** - how much is in the account?

Once I have this info, I'll help you complete the setup!

---

## ⚠️  Final Warning

**Live trading with real money involves significant risk:**
- You can lose money
- Past performance ≠ future results
- Start small and scale gradually
- Never risk more than you can afford to lose
- Paper trading success doesn't guarantee live success

**I strongly recommend paper trading first.** It's free, risk-free, and uses real market data. Perfect for testing and learning.

---

**Ready to proceed when you provide the missing information!** 🚀

