# 🚨 LIVE TRADING GUIDE - READ CAREFULLY 🚨

## ⚠️ IMPORTANT WARNINGS

**LIVE TRADING USES REAL MONEY. YOU CAN LOSE MONEY.**

Before enabling live trading:
1. ✅ Test extensively with paper trading first (weeks/months)
2. ✅ Understand the trading strategy completely
3. ✅ Set appropriate risk limits
4. ✅ Only invest money you can afford to lose
5. ✅ Monitor your account regularly

---

## 📊 Current Setup

### Paper Trading (Default - SAFE)
- **Endpoint:** `https://paper-api.alpaca.markets`
- **Balance:** $100,000 virtual money
- **Risk:** ZERO - No real money involved
- **Credentials:** `ALPACA_PAPER_API_KEY` and `ALPACA_PAPER_API_SECRET`

### Live Trading (Real Money - USE WITH CAUTION)
- **Endpoint:** `https://api.alpaca.markets`
- **Balance:** $0.00 (needs funding)
- **Risk:** HIGH - Real money at risk
- **Credentials:** `ALPACA_LIVE_API_KEY` and `ALPACA_LIVE_API_SECRET`

---

## 🔧 How to Enable Live Trading

### Step 1: Fund Your Live Account
1. Log in to Alpaca: https://alpaca.markets/
2. Navigate to your **Live Trading** account
3. Deposit funds via bank transfer
4. **Start small!** Recommend $500-$1000 for testing

### Step 2: Verify Live Account
```bash
python3 check_live_account.py
```
This shows your live account balance and positions.

### Step 3: Update Risk Settings (CRITICAL!)
Edit `config.yaml`:
```yaml
# Reduce capital for live trading!
capital_eur: 500  # Start small, e.g., $500

risk:
  max_positions: 2           # Limit to 2 positions max
  max_alloc_per_trade: 0.10  # Only 10% per trade (was 15%)
  stop_loss_pct: 0.03        # Tighter stop loss (3%)
  take_profit_pct: 0.05      # Tighter take profit (5%)
```

### Step 4: Enable Live Trading
Edit `config.yaml`:
```yaml
alpaca:
  paper_trading: false  # ⚠️ DANGER: This enables LIVE trading!
  use_alpaca: true
```

### Step 5: Test with Dry Run First
```bash
# This will show what trades WOULD be made (without executing)
# Check the logs carefully!
python3 main.py
```

### Step 6: Monitor Actively
After your first live trade:
- ✅ Check Alpaca dashboard immediately
- ✅ Verify orders executed correctly
- ✅ Monitor positions regularly
- ✅ Set up alerts in Alpaca

---

## 🛡️ Safety Commands

### Check Paper Account (Safe)
```bash
python3 check_alpaca_account.py
```

### Check Live Account (View Only - No Trading)
```bash
python3 check_live_account.py
```

### View Current Orders & Positions
```bash
python3 check_orders.py  # Paper account
```

### Test Trade (Paper Only)
```bash
python3 test_trade.py
```

---

## 🚨 Emergency: Close All Positions

If you need to exit all positions immediately:

```python
from trade.alpaca_broker import close_all_positions

# Close all LIVE positions (DANGER!)
close_all_positions(paper=False)
```

---

## 📋 Pre-Flight Checklist for Live Trading

Before running with `paper_trading: false`:

- [ ] I have tested for at least 2 weeks with paper trading
- [ ] I understand the trading strategy (sentiment + momentum)
- [ ] I have reviewed all generated signals and they make sense
- [ ] I have set conservative risk limits
- [ ] I have funded my live account with money I can afford to lose
- [ ] I have verified my live credentials with `check_live_account.py`
- [ ] I am ready to monitor the account actively
- [ ] I have set up stop-loss and take-profit parameters
- [ ] I understand that past performance ≠ future results
- [ ] I accept full responsibility for any losses

---

## 🔄 How to Switch Back to Paper Trading

**IMMEDIATELY stop live trading by editing `config.yaml`:**
```yaml
alpaca:
  paper_trading: true  # ← Set back to true
  use_alpaca: true
```

Then run:
```bash
python3 check_alpaca_account.py  # Should show paper account
```

---

## 📊 Recommended Testing Strategy

### Phase 1: Paper Trading (2-4 weeks)
- Run daily with paper account
- Track performance in `storage/daily_summary.csv`
- Verify sentiment analysis makes sense
- Review all generated signals

### Phase 2: Micro Live Test (1 week)
- Fund live account with $500-$1000
- Set `capital_eur: 500`
- Set `max_alloc_per_trade: 0.10` (10%)
- Monitor every single trade

### Phase 3: Scale Up (If Profitable)
- Gradually increase capital
- Never exceed what you can afford to lose
- Keep monitoring actively

---

## ⚠️ Known Risks

1. **Strategy Risk:** This is a simple sentiment + momentum strategy. It may not be profitable.
2. **Data Risk:** Yahoo Finance API can fail. News/Reddit APIs can be unavailable.
3. **Execution Risk:** Market orders can execute at worse prices than expected.
4. **Market Risk:** Markets can be volatile and unpredictable.
5. **Gap Risk:** Stocks can gap up/down overnight, bypassing stop losses.

---

## 📞 Support

- **Alpaca Support:** https://alpaca.markets/support
- **Alpaca API Docs:** https://alpaca.markets/docs/
- **GitHub Issues:** (Your repo)

---

## 🎯 Current Status

✅ **Paper Trading:** Connected ($100k virtual)
✅ **Live Trading:** Connected ($0.00 - needs funding)
🔒 **Default Mode:** PAPER TRADING (Safe)

**To check status anytime:**
```bash
python3 check_alpaca_account.py  # Paper account
python3 check_live_account.py     # Live account
```

---

## ⚖️ Legal Disclaimer

This software is provided "as is" without warranty of any kind. Trading stocks involves risk. You can lose money. The developers are not responsible for any financial losses. Use at your own risk. Not financial advice.

---

## 🚀 Remember

**START WITH PAPER TRADING.**

Only move to live trading after:
- ✅ Weeks of successful paper trading
- ✅ Complete understanding of the system
- ✅ Conservative risk settings
- ✅ Money you can afford to lose

**Good luck, and trade responsibly!** 🎯




