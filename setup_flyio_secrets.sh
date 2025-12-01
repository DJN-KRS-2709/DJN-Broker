#!/bin/bash
# Setup Fly.io secrets from .env file

echo "🔐 Setting up Fly.io secrets from .env file..."

# Read .env file and extract values
source .env

# Set all secrets in Fly.io
export FLYCTL_INSTALL="/Users/dejank/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"

flyctl secrets set \
  ALPACA_PAPER_API_KEY="$ALPACA_PAPER_API_KEY" \
  ALPACA_PAPER_API_SECRET="$ALPACA_PAPER_API_SECRET" \
  ALPACA_PAPER_BASE_URL="$ALPACA_PAPER_BASE_URL" \
  NEWSAPI_KEY="$NEWSAPI_KEY" \
  REDDIT_CLIENT_ID="$REDDIT_CLIENT_ID" \
  REDDIT_CLIENT_SECRET="$REDDIT_CLIENT_SECRET" \
  REDDIT_USER_AGENT="$REDDIT_USER_AGENT" \
  NOTIFICATION_EMAIL="$NOTIFICATION_EMAIL" \
  SMTP_EMAIL="$SMTP_EMAIL" \
  SMTP_PASSWORD="$SMTP_PASSWORD" \
  SMTP_SERVER="$SMTP_SERVER" \
  SMTP_PORT="$SMTP_PORT" \
  TWELVE_DATA_API_KEY="$TWELVE_DATA_API_KEY" \
  FINNHUB_API_KEY="${FINNHUB_API_KEY:-}" \
  ALPHA_VANTAGE_API_KEY="${ALPHA_VANTAGE_API_KEY:-}" \
  IEX_CLOUD_API_KEY="${IEX_CLOUD_API_KEY:-}" \
  --app djn-broker

echo "✅ Secrets configured successfully!"





