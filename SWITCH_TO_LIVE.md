# 🔄 How to Switch Between Paper and Live Trading

**Your Current Setup:**
- ✅ Paper Trading: Account PA3KBA0PAM8S ($99,999.83 fake money)
- ✅ Live Trading: Account 987064219 ($569.38 real money)
- 🎯 Currently Active: **PAPER TRADING** (safe)

---

## 📊 **Your Two Accounts**

### **Paper Account (Currently Active)** 📄
- Account: PA3KBA0PAM8S
- Balance: $99,999.83 (fake money)
- Risk: ZERO
- Purpose: Testing and learning

### **Live Account (Ready When You Are)** 💰
- Account: 987064219
- Balance: $569.38 (real money)
- Risk: HIGH
- Purpose: Real trading

---

## 🔄 **How to Switch to Live Trading**

### **When to Switch:**
Only switch to live when:
- ✅ You've run paper trading for at least 5-7 days
- ✅ Paper trading shows positive results
- ✅ You understand how the system works
- ✅ You're comfortable with the risk
- ✅ You've reviewed all trades and performance

### **Steps to Switch (5 minutes):**

#### **Step 1: Update .env File**
```bash
cd /Users/dejank/Downloads/cursor_free_trading_mvp
nano .env
```

Find these lines:
```bash
# ACTIVE CONFIGURATION
# Currently using: PAPER TRADING (SAFE)
ALPACA_API_KEY=PK3NXEEPUU5YSUNWDGLFBBGYLL
ALPACA_API_SECRET=Dgrfxy5Tm9NLEMhFfHZ5XWbPsc4vQDKR4WurnQa4YAuv
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

Change to:
```bash
# ACTIVE CONFIGURATION
# Currently using: LIVE TRADING (REAL MONEY!)
ALPACA_API_KEY=AKBFSSYMZFJTQCWO7YLN5IL4LN
ALPACA_API_SECRET=D7KQSwTnoT8dz3yBczfyHkMykedLjGB2rkNVDMzW7Q36
ALPACA_BASE_URL=https://api.alpaca.markets
```

Save: `Ctrl+X`, then `Y`, then `Enter`

#### **Step 2: Update config.yaml**
```bash
nano config.yaml
```

Find:
```yaml
live_trading:
  enabled: true
  account_number: "PA3KBA0PAM8S"
  paper_mode: true
```

Change to:
```yaml
live_trading:
  enabled: true
  account_number: "987064219"
  paper_mode: false
```

Save: `Ctrl+X`, then `Y`, then `Enter`

#### **Step 3: Test Connection**
```bash
python3 -c "
import alpaca_trade_api as tradeapi

api = tradeapi.REST(
    'AKBFSSYMZFJTQCWO7YLN5IL4LN',
    'D7KQSwTnoT8dz3yBczfyHkMykedLjGB2rkNVDMzW7Q36',
    'https://api.alpaca.markets',
    api_version='v2'
)

account = api.get_account()
print('✅ Connected to LIVE TRADING account')
print(f'Account: {account.account_number}')
print(f'Balance: \${float(account.portfolio_value):,.2f}')
"
```

#### **Step 4: Restart Bot**
```bash
pkill -f schedule_runner
nohup python3 schedule_runner.py > scheduler.log 2>&1 &
```

#### **Step 5: Verify**
```bash
tail -20 scheduler.log
```

---

## 🔙 **How to Switch Back to Paper Trading**

If you want to go back to paper trading:

#### **Step 1: Update .env**
```bash
nano .env
```

Change ACTIVE CONFIGURATION back to paper credentials

#### **Step 2: Update config.yaml**
```bash
nano config.yaml
```

Change:
- `account_number: "PA3KBA0PAM8S"`
- `paper_mode: true`

#### **Step 3: Restart**
```bash
pkill -f schedule_runner
nohup python3 schedule_runner.py > scheduler.log 2>&1 &
```

---

## 📊 **Monitoring Your Accounts**

### **Check Paper Trading Performance:**
```bash
# View recent paper trades
cat storage/intended_orders.csv

# Daily summary
cat storage/daily_summary.csv

# Live logs
tail -f scheduler.log
```

### **Check Live Trading (When Active):**
Same commands, plus:
- Go to: https://app.alpaca.markets/trading/portfolio
- View real positions and P&L
- Check actual orders executed

---

## 🎯 **Recommended Timeline**

### **Week 1 (Nov 11-15): Paper Trading** 📄
- **Monday-Friday**: Let bot run with paper account
- **Daily**: Check `storage/daily_summary.csv`
- **Goal**: Collect 5 days of performance data

**Questions to answer:**
- Is the bot generating signals?
- Are trades being executed?
- What's the win rate?
- Any errors or crashes?

### **Week 2 (Nov 18+): Decision Point** 🎲

**If Paper Trading Was Successful:**
- ✅ Positive P&L
- ✅ No major errors
- ✅ Win rate >50%
- ✅ You feel confident

→ **Switch to Live Trading** using the steps above

**If Paper Trading Was Not Successful:**
- ❌ Negative P&L
- ❌ System errors
- ❌ Low win rate

→ **Keep Paper Trading**, adjust strategy, or stop

---

## 🛡️ **Safety Reminders**

### **Before Going Live:**
- [ ] Run paper trading for at least 5 days
- [ ] Review all trades generated
- [ ] Check system has no errors
- [ ] Verify you understand the signals
- [ ] Confirm you're comfortable with $569.38 at risk

### **When Live:**
- [ ] Start with small capital ($569.38 is good)
- [ ] Monitor HOURLY the first day
- [ ] Check before/after market close
- [ ] Review every trade
- [ ] Be ready to stop if needed

### **Emergency Stop (Live Trading):**
```bash
# Stop the bot
pkill -f schedule_runner

# Or create kill switch
touch STOP_TRADING.txt

# Close all positions immediately
# Go to: https://app.alpaca.markets/trading/portfolio
# Click "Close All Positions"
```

---

## 📈 **Performance Tracking**

### **Paper Trading Metrics:**
Track these before switching to live:
- Total P&L: $___
- Number of trades: ___
- Winning trades: ___
- Losing trades: ___
- Win rate: ___%
- Largest gain: $___
- Largest loss: $___
- Max drawdown: ___%

### **Example Good Results:**
```
Total P&L: +$847 (from $100k paper)
Trades: 23
Winners: 14
Losers: 9
Win rate: 60.8%
Max drawdown: -3.2%
✅ Ready for live trading!
```

### **Example Poor Results:**
```
Total P&L: -$2,341 (from $100k paper)
Trades: 31
Winners: 11  
Losers: 20
Win rate: 35.5%
Max drawdown: -8.9%
❌ NOT ready - keep testing!
```

---

## 🎯 **Current Status**

✅ **Paper Account**: Active (PA3KBA0PAM8S)  
⏸️ **Live Account**: Ready but not active (987064219)  
📋 **Mode**: Paper Trading (safe)  
🤖 **Bot Status**: Running (PID: 67364)  
⏰ **Next Run**: Today at 9:35 AM ET  

---

## 💡 **Key Points**

1. **Paper first** = Smart, safe approach
2. **Test thoroughly** = At least 5-7 days
3. **Review results** = Don't rush to live
4. **Start small** = $569 is perfect starting size
5. **Monitor closely** = Especially first week live
6. **Can switch back** = Not locked into live

---

**Questions? Let me know!** 🚀

Good luck with your paper trading this week!

