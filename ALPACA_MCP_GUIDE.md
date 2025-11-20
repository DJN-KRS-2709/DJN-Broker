# 🤖 Alpaca MCP Server Guide

## What is Alpaca MCP?

The **Alpaca MCP (Model Context Protocol) Server** lets you interact with your Alpaca trading account using **natural language** in AI chat interfaces like Claude Desktop, Cursor, ChatGPT, etc.

**You can now:**
- 💬 Chat with AI about your portfolio
- 📊 Get real-time market data
- 💼 Place trades with natural language
- 🔍 Analyze trading performance
- 📈 Pull historical data

---

## ✅ Installation Complete!

Your MCP server is configured for:
- ✅ **Claude Desktop**: `~/.config/claude-desktop/config.json`
- ✅ **Cursor IDE**: `~/Library/Application Support/Cursor/User/mcp_settings.json`
- ✅ **Paper Trading Mode**: Safe testing with $100k virtual money

---

## 🚀 How to Use

### **1. Restart Your Apps**

After installation, restart:
- Claude Desktop (Cmd+Q, then reopen)
- Cursor IDE (Cmd+Q, then reopen)

### **2. Verify Connection**

In Claude Desktop or Cursor, ask:
```
Check my Alpaca account status
```

You should see:
- ✅ Account balance
- ✅ Buying power
- ✅ Open positions
- ✅ Portfolio value

---

## 💡 Example Commands You Can Try

### **Portfolio Management**

```
What's my current portfolio value?
```

```
Show me all my open positions
```

```
What's my buying power?
```

```
Show me my recent trades
```

### **Market Data**

```
What's the current price of AAPL?
```

```
Get me the latest news for TSLA
```

```
Show me NVDA's price history for the last 7 days
```

```
What are the top gainers today?
```

### **Trading (Paper Mode)**

```
Buy $500 worth of AAPL at market price
```

```
Sell all my MSFT shares
```

```
Place a limit order to buy 10 shares of GOOGL at $170
```

```
Set a stop-loss for my NVDA position at 5% below current price
```

### **Analysis**

```
Analyze my portfolio performance this week
```

```
What's my best performing stock?
```

```
Calculate my total P&L for November
```

```
Show me my win rate
```

---

## 🎯 How This Complements Your Automated Bot

| Feature | Automated Bot | MCP Server |
|---------|--------------|------------|
| **When it runs** | Daily at 20:00 CET | Anytime you ask |
| **Trading style** | Automated signals | Manual decisions |
| **Strategy** | Sentiment + momentum | Your discretion |
| **Interface** | Email summaries | Chat with AI |
| **Use case** | Systematic trading | Interactive analysis |

### **Perfect Workflow:**

1. **🤖 Automated Bot** trades daily at 20:00 CET
2. **📧 Email** sends you summary
3. **💬 MCP** lets you chat: "Show me today's trades"
4. **🔍 Analyze** with AI: "Why did we buy NVDA today?"
5. **👤 Override** if needed: "Sell NVDA now"

---

## 🛡️ Safety Features

✅ **Paper Trading Mode** - No real money at risk  
✅ **Confirmation Required** - AI shows you the trade before executing  
✅ **Full Visibility** - See every parameter and payload  
✅ **Same Account** - Uses your existing paper trading account  

---

## 📚 Advanced Usage

### **Multi-Asset Trading**

```
Buy $1000 worth of crypto: 50% BTC, 50% ETH
```

```
Create an iron condor spread on SPY
```

### **Portfolio Optimization**

```
Rebalance my portfolio to 40% tech, 30% finance, 30% healthcare
```

```
What would happen if I sold all losing positions?
```

### **Risk Management**

```
Set stop-losses at 5% for all my positions
```

```
Show me my portfolio's beta
```

---

## 🔧 Configuration

### **Switch to Live Trading** (⚠️ Use with Caution!)

Edit your config file:
```json
{
  "mcpServers": {
    "alpaca": {
      "env": {
        "ALPACA_API_KEY": "YOUR_LIVE_KEY",
        "ALPACA_API_SECRET": "YOUR_LIVE_SECRET",
        "ALPACA_PAPER": "false"  // ⚠️ REAL MONEY!
      }
    }
  }
}
```

### **Add More MCP Servers**

You can add multiple MCP servers for different services:
```json
{
  "mcpServers": {
    "alpaca": { ... },
    "financial-data": { ... },
    "news-api": { ... }
  }
}
```

---

## 🆘 Troubleshooting

### **MCP Not Working?**

1. **Check Node.js is installed:**
   ```bash
   node --version
   npx --version
   ```

2. **Verify config file exists:**
   ```bash
   cat ~/.config/claude-desktop/config.json
   ```

3. **Test MCP server manually:**
   ```bash
   npx -y @alpacahq/mcp-server-alpaca
   ```

4. **Restart your AI app** (Cmd+Q, reopen)

### **"Unauthorized" Error?**

- Check API keys in config match your `.env` file
- Verify `ALPACA_PAPER: "true"` for paper trading

### **Commands Not Working?**

- Make sure you're in Claude Desktop or Cursor (not web version)
- Try: "List available tools" to see if Alpaca MCP loaded
- Restart the app

---

## 📖 Resources

- **Alpaca MCP Docs**: https://alpaca.markets/docs/mcp
- **MCP Protocol**: https://modelcontextprotocol.io
- **Your Bot Repo**: https://github.com/DJN-KRS-2709/DJN-Broker

---

## 💡 Pro Tips

1. **Start with queries** before trades: "Show my portfolio" before "Buy AAPL"
2. **Use dollar amounts** for fractional shares: "Buy $500 of TSLA"
3. **Be specific** with orders: "Market order" vs "Limit order at $150"
4. **Check first**: "What's NVDA's price?" before "Buy 10 shares"
5. **Use stop-losses**: "Set stop-loss at 5%" for risk management

---

## 🎉 You're Ready!

Your Alpaca MCP Server is configured and ready to use!

**Try your first command in Claude Desktop or Cursor:**
```
Show me my Alpaca account status
```

Happy trading! 🚀📈

