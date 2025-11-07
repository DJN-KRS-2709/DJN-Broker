# 🤖 Agentic AI Patterns in DJN Broker

This trading bot implements **TWO complementary agentic patterns** for optimal performance:

---

## 🔄 Pattern 1: **ReAct (Reasoning + Acting)** - Real-Time Trading

**Where:** Main trading loop (`main.py`)

**Flow:**
```
1. THINK: Analyze market sentiment + momentum
         ↓
2. ACT: Execute trades on Alpaca
         ↓
3. OBSERVE: Monitor outcomes (win/loss, P&L)
         ↓
4. THINK: Learn patterns from results
         ↓
5. ACT: Adjust strategy parameters
         ↓
6. LOOP: Trade with improved strategy
```

**Implementation:**
- **Reasoning:** Sentiment analysis (NLP) + momentum calculations
- **Acting:** Execute orders via Alpaca API
- **Observing:** Store all trades in RAG memory
- **Learning:** Analyzer extracts patterns
- **Optimizing:** Strategy Optimizer adjusts parameters

**Strengths:**
✅ Fast decision-making (real-time markets)  
✅ Adaptive (learns from immediate feedback)  
✅ Continuous improvement  
✅ Handles uncertainty well  

**Use Case:**
- Live trading execution
- Quick market response
- Feedback-driven learning

---

## 🌳 Pattern 2: **Tree of Thoughts** - Strategy Optimization

**Where:** Strategy exploration (`tree_of_thoughts.py`)

**Flow:**
```
                    Root Strategy (Current)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   Higher Sent.         Lower Sent.        Focus Best 3
   (0.5 threshold)      (0.3 threshold)      Stocks
        │                   │                   │
   ├─ Wide TP          ├─ Tight SL        ├─ Large Pos
   └─ Tight SL         └─ Wide TP         └─ Small Pos
        │                   │                   │
   Simulate & Score    Simulate & Score   Simulate & Score
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                    Select Best Path ⭐
```

**Implementation:**
- **Explore:** Generate strategy variations
- **Simulate:** Test on historical data
- **Evaluate:** Score each variation
- **Backtrack:** Prune low-scoring branches
- **Select:** Choose best performing strategy

**Strengths:**
✅ Explores multiple scenarios  
✅ Finds non-obvious optimizations  
✅ Risk-free testing (simulated)  
✅ Comprehensive strategy search  

**Use Case:**
- Weekly strategy optimization
- Parameter tuning
- What-if analysis
- Before going live

---

## 🔀 **Hybrid Architecture** - Best of Both Worlds

```
┌─────────────────────────────────────────────┐
│          TREE OF THOUGHTS                   │
│  (Strategy Exploration - Weekly)            │
│                                             │
│  Explores multiple strategies               │
│  Finds optimal parameters                   │
│  Recommends best configuration              │
└────────────────┬────────────────────────────┘
                 │ Apply Best Strategy
                 ↓
┌─────────────────────────────────────────────┐
│            REACT LOOP                       │
│  (Real-Time Trading - Daily/Continuous)     │
│                                             │
│  1. Think: Analyze market                   │
│  2. Act: Execute trades                     │
│  3. Observe: Monitor results                │
│  4. Learn: Extract patterns                 │
│  5. Optimize: Adjust strategy               │
│  6. Loop: Trade better                      │
└─────────────────────────────────────────────┘
```

---

## 📊 **When to Use Which Pattern**

### Use **ReAct** when:
- ✅ Markets are open and trading live
- ✅ Need quick decisions
- ✅ Learning from real outcomes
- ✅ Adapting to changing conditions
- ✅ Continuous operation

### Use **Tree of Thoughts** when:
- ✅ Markets are closed (weekend analysis)
- ✅ Major strategy changes needed
- ✅ Want to test "what if" scenarios
- ✅ Need comprehensive optimization
- ✅ Before switching to live trading

---

## 🚀 **How to Use Both Patterns**

### Daily: ReAct (Automatic)
```bash
# Runs automatically 4x per day
python3 schedule_runner.py &
```
- Trades continuously
- Learns from each trade
- Makes small incremental adjustments

### Weekly: Tree of Thoughts (Manual)
```bash
# Run once a week for deep analysis
python3 run_strategy_exploration.py
```
- Explores 10-20 strategy variations
- Simulates on historical data
- Recommends major optimizations

---

## 💡 **Why This Combination Works**

### ReAct Alone:
- ❌ Can get stuck in local optima
- ❌ Only makes incremental changes
- ❌ Might miss better strategies

### Tree of Thoughts Alone:
- ❌ Too slow for real-time trading
- ❌ Requires lots of historical data
- ❌ Can't adapt to live conditions

### ReAct + ToT Together:
- ✅ Fast real-time decisions (ReAct)
- ✅ Deep strategic thinking (ToT)
- ✅ Continuous + periodic optimization
- ✅ Explores broadly + adapts quickly
- ✅ Best of both worlds! 🎯

---

## 📈 **Performance Impact**

| Pattern | Speed | Adaptability | Exploration | Best For |
|---------|-------|--------------|-------------|----------|
| ReAct | ⚡⚡⚡ Fast | ⭐⭐⭐ High | ⭐ Limited | Live Trading |
| ToT | 🐌 Slow | ⭐ Limited | ⭐⭐⭐ Deep | Strategy Optimization |
| Hybrid | ⚡⚡ Good | ⭐⭐⭐ High | ⭐⭐⭐ Deep | **Everything** |

---

## 🛠️ **Implementation Details**

### ReAct Components:
- `main.py` - Main trading loop
- `learning/trade_memory.py` - Stores observations
- `learning/analyzer.py` - Extracts patterns
- `learning/strategy_optimizer.py` - Adapts strategy

### ToT Components:
- `learning/tree_of_thoughts.py` - Strategy exploration
- `run_strategy_exploration.py` - CLI tool

### Integration:
1. **Daily:** ReAct runs automatically
2. **Weekly:** Run ToT analysis manually
3. **Apply:** ToT recommendations → ReAct parameters
4. **Repeat:** Continuous improvement!

---

## 📚 **Further Reading**

**ReAct Paper:**
- ["ReAct: Synergizing Reasoning and Acting in Language Models"](https://arxiv.org/abs/2210.03629)
- Focus: Iterative reasoning + action cycles

**Tree of Thoughts Paper:**
- ["Tree of Thoughts: Deliberate Problem Solving with Large Language Models"](https://arxiv.org/abs/2305.10601)
- Focus: Multi-path exploration + backtracking

---

## 🎯 **Quick Start**

### 1. Run ReAct (Automatic Trading)
```bash
python3 schedule_runner.py &
```
Runs 4x daily, learns continuously.

### 2. Run ToT (Weekly Optimization)
```bash
# After 1-2 weeks of trading
python3 run_strategy_exploration.py
```
Explores strategies, recommends optimizations.

### 3. View What Was Learned
```bash
python3 show_learnings.py
```
Shows insights from both patterns.

---

## 🏆 **The Result**

A trading bot that:
- ✅ Thinks fast (ReAct)
- ✅ Thinks deep (ToT)
- ✅ Learns continuously (ReAct)
- ✅ Optimizes comprehensively (ToT)
- ✅ Adapts to markets (ReAct)
- ✅ Finds better strategies (ToT)

**= Maximum Performance** 🚀

---

## ⚠️ **Important Notes**

1. **Run ToT weekly** - Not every day (needs data to accumulate)
2. **Review ToT suggestions** - Don't blindly apply all changes
3. **Let ReAct adapt** - Give it time to learn (10+ trades)
4. **Monitor both** - Check logs and learnings regularly

---

Built with ❤️ for intelligent, adaptive trading.

