#!/bin/bash

echo "═══════════════════════════════════════════════════════════"
echo "🚀 GitHub Actions Setup Guide"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Your code is already pushed to GitHub! ✅"
echo "Repository: https://github.com/DJN2709/DJN-Broker"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📝 STEP 1: Add Secrets to GitHub"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Go to: https://github.com/DJN2709/DJN-Broker/settings/secrets/actions"
echo ""
echo "Click 'New repository secret' and add these 8 secrets:"
echo ""
echo "1. REDDIT_CLIENT_ID"
echo "2. REDDIT_CLIENT_SECRET"
echo "3. REDDIT_USER_AGENT"
echo "4. NEWSAPI_KEY (optional)"
echo "5. ALPACA_PAPER_API_KEY"
echo "6. ALPACA_PAPER_API_SECRET"
echo "7. ALPACA_LIVE_API_KEY"
echo "8. ALPACA_LIVE_API_SECRET"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "⚡ STEP 2: Enable GitHub Actions"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Go to: https://github.com/DJN2709/DJN-Broker/actions"
echo "Click: 'I understand my workflows, go ahead and enable them'"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ STEP 3: You're Done!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Your bot will now run automatically 4x per day:"
echo "  • 09:00 Berlin time"
echo "  • 15:35 Berlin time (US market open)"
echo "  • 18:00 Berlin time (US midday)"
echo "  • 21:30 Berlin time (before US close)"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📊 Monitor Your Bot:"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "View runs: https://github.com/DJN2709/DJN-Broker/actions"
echo "Check logs: Click on any run → View job"
echo "Manual run: Actions → Automated Trading Bot → Run workflow"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🎉 Your computer can be OFF - bot keeps trading!"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Open browser to GitHub secrets page
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "https://github.com/DJN2709/DJN-Broker/settings/secrets/actions"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "https://github.com/DJN2709/DJN-Broker/settings/secrets/actions" 2>/dev/null
fi




