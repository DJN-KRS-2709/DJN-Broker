#!/bin/bash
# Setup .env file for DJN Broker
# This script creates a .env file template with all required environment variables

cat > .env << 'EOF'
# ============================================================================
# DJN BROKER - ENVIRONMENT VARIABLES
# ============================================================================
# Fill in your actual values below
# ============================================================================

# ----------------------------------------------------------------------------
# ALPACA TRADING API - Paper Trading (Safe for Testing)
# ----------------------------------------------------------------------------
ALPACA_PAPER_API_KEY=
ALPACA_PAPER_API_SECRET=
ALPACA_PAPER_BASE_URL=https://paper-api.alpaca.markets

# ----------------------------------------------------------------------------
# ALPACA TRADING API - LIVE Trading (⚠️ REAL MONEY!)
# ----------------------------------------------------------------------------
ALPACA_LIVE_API_KEY=
ALPACA_LIVE_API_SECRET=

# ----------------------------------------------------------------------------
# ALPACA BROKER API (Optional)
# ----------------------------------------------------------------------------
ALPACA_BROKER_CLIENT_ID=
ALPACA_BROKER_CLIENT_SECRET=
ALPACA_BROKER_SANDBOX_URL=https://broker-api.sandbox.alpaca.markets

# ----------------------------------------------------------------------------
# NEWS APIs
# ----------------------------------------------------------------------------
NEWSAPI_KEY=

# ----------------------------------------------------------------------------
# SOCIAL MEDIA APIs
# ----------------------------------------------------------------------------
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=DJN-Broker:v1.0 (by /u/your_username)

# ----------------------------------------------------------------------------
# EMAIL NOTIFICATIONS
# ----------------------------------------------------------------------------
NOTIFICATION_EMAIL=
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_PASSWORD=

# ----------------------------------------------------------------------------
# ADDITIONAL MARKET DATA APIs (Optional)
# ----------------------------------------------------------------------------
TWELVE_DATA_API_KEY=
FINNHUB_API_KEY=
ALPHA_VANTAGE_API_KEY=
IEX_CLOUD_API_KEY=

# ----------------------------------------------------------------------------
# GITHUB
# ----------------------------------------------------------------------------
GITHUB_TOKEN=

EOF

echo "✅ Created .env template"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env and fill in your credentials"
echo "   2. See GITHUB_TOKEN_SETUP.md for token setup"
echo "   3. See SECURITY_GUIDE.md for best practices"
echo ""
echo "🔐 Remember: NEVER commit .env to git!"

