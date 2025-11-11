# 🚀 Setup Instructions for Dejan

**Account**: 987064219  
**Balance**: $569.38  
**Email**: dejan.krstic@web.de  
**Broker**: Alpaca  

---

## 📝 **What You Need to Do**

### **Step 1: Get Your API Secret from Alpaca**

1. Go to: https://app.alpaca.markets/brokerage/dashboard/overview
2. Log in
3. Look for "API Keys" section
4. Find your key: `AKUSSE272MUBVFISBTAFSEJUSW`
5. Click "View" or "Regenerate" to see the **Secret**
6. Copy the secret (it's a long random string)

⚠️ If you can't see the secret, click "Regenerate" to create a new key pair.

---

## 🎯 **CHOOSE YOUR MODE**

### **OPTION A: Paper Trading (RECOMMENDED - Start Here!)** ✅

**Best for**: Testing the bot safely with fake money first

**Setup**:
```bash
cd /Users/dejank/Downloads/cursor_free_trading_mvp

# Create .env file
cat > .env << 'EOF'
# Reddit API
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=trading-bot/1.0

# Alpaca API - PAPER TRADING (SAFE)
ALPACA_API_KEY=AKUSSE272MUBVFISBTAFSEJUSW
ALPACA_API_SECRET=PASTE_YOUR_SECRET_HERE
ALPACA_BASE_URL=https://paper-api.alpaca.markets
EOF

# Install Alpaca
pip3 install alpaca-trade-api

# Edit config.yaml - set paper_mode to true
nano config.yaml
# Change line to: paper_mode: true

# Test connection
python3 -c "
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()
api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_API_SECRET'),
    'https://paper-api.alpaca.markets',
    api_version='v2'
)
account = api.get_account()
print(f'✅ Paper Trading Connected!')
print(f'Virtual Balance: \${float(account.portfolio_value):,.2f}')
"

# Restart the bot
pkill -f schedule_runner
nohup python3 schedule_runner.py > scheduler.log 2>&1 &
```

**What happens**:
- ✅ Bot trades with fake $100,000
- ✅ Your real $569.38 stays safe
- ✅ See how the bot performs
- ✅ Zero risk

---

### **OPTION B: Live Trading (Real Money - Your $569.38)** 💰

**Best for**: After paper trading is successful and you're confident

**Setup**:
```bash
cd /Users/dejank/Downloads/cursor_free_trading_mvp

# Create .env file
cat > .env << 'EOF'
# Reddit API
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=trading-bot/1.0

# Alpaca API - LIVE TRADING (REAL MONEY!)
ALPACA_API_KEY=AKUSSE272MUBVFISBTAFSEJUSW
ALPACA_API_SECRET=PASTE_YOUR_SECRET_HERE
ALPACA_BASE_URL=https://api.alpaca.markets
EOF

# Install Alpaca
pip3 install alpaca-trade-api

# Edit config.yaml - set paper_mode to false
nano config.yaml
# Change line to: paper_mode: false

# Test connection
python3 -c "
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()
api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_API_SECRET'),
    'https://api.alpaca.markets',
    api_version='v2'
)
account = api.get_account()
print(f'⚠️  LIVE TRADING Connected!')
print(f'Real Balance: \${float(account.portfolio_value):,.2f}')
print(f'Buying Power: \${float(account.buying_power):,.2f}')
"

# Restart the bot
pkill -f schedule_runner
nohup python3 schedule_runner.py > scheduler.log 2>&1 &
```

**What happens**:
- ⚠️ Bot trades with your real $569.38
- ⚠️ You can make or lose money
- ⚠️ Orders execute on real market
- ⚠️ Risk involved

---

## 💡 **My Recommendation**

### **Week 1 (This Week): Paper Trading**
- Start with OPTION A (Paper Trading)
- Let it run Monday-Friday
- Monitor performance daily
- Check logs: `tail -f scheduler.log`
- Review trades: `cat storage/intended_orders.csv`

### **Week 2 (Next Week): Decide**
**Switch to Live ONLY if**:
- ✅ Paper trading was profitable
- ✅ No system errors
- ✅ You understand how it works
- ✅ You're comfortable with the risk

**How to switch**:
```bash
# Update .env file
nano .env
# Change ALPACA_BASE_URL to: https://api.alpaca.markets

# Update config.yaml
nano config.yaml
# Change paper_mode to: false

# Restart bot
pkill -f schedule_runner
nohup python3 schedule_runner.py > scheduler.log 2>&1 &
```

---

## 🛡️ **Safety Features Active**

With your $569.38 account, here's what protects you:

### **Circuit Breakers**:
- **Daily loss limit**: Stops if down $17 (3% of $569)
- **Max trades**: 5 trades per day maximum
- **Consecutive losses**: Stops after 3 losses in a row
- **Position size**: Max $57 per trade (10% of capital)

### **Emergency Stop**:
```bash
# Method 1: Kill switch file
touch /Users/dejank/Downloads/cursor_free_trading_mvp/STOP_TRADING.txt

# Method 2: Stop the process
ps aux | grep schedule_runner
kill [PID]

# Method 3: Close positions in Alpaca dashboard
# Go to: https://app.alpaca.markets/trading/portfolio
# Click "Close All Positions"
```

---

## 📊 **What to Monitor**

### **Daily Checks**:
```bash
# Check if bot is running
ps aux | grep schedule_runner

# View recent logs
tail -50 scheduler.log

# See trades
cat storage/intended_orders.csv

# Check daily summary
cat storage/daily_summary.csv
```

### **Key Metrics**:
- Total P&L
- Number of trades
- Win rate
- Current positions
- Account balance

---

## 🎯 **Next Steps**

1. **Get your API secret** from Alpaca dashboard
2. **Choose your mode**: Paper (recommended) or Live
3. **Follow the setup commands** above for your chosen mode
4. **Test the connection** with the python test command
5. **Restart the bot**
6. **Monitor closely** for the first few days

---

## 📞 **Questions?**

Once you have your API secret, let me know:
- Which mode you want to start with (Paper or Live)
- If you need help with any step
- If you encounter any errors

I'm here to help you get this running safely! 🚀

---

## ⚠️ **Important Reminders**

1. **Paper trading first** = Zero risk, perfect for learning
2. **Live trading** = Real money, start small ($569 is good)
3. **Monitor daily** = Check performance every day
4. **Can always stop** = You're in control
5. **Start conservative** = Better safe than sorry

**Ready to proceed when you have your API secret!** 🎉

