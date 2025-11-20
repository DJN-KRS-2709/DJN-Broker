#!/bin/bash

echo "🚀 Setting up Alpaca MCP Server..."
echo ""

# Check if npx is available
if ! command -v npx &> /dev/null; then
    echo "❌ Node.js/npx not found. Installing via Homebrew..."
    brew install node
fi

echo "✅ Node.js installed"
echo ""

# Create MCP configuration directory
mkdir -p ~/.config/claude-desktop

echo "📝 Creating Claude Desktop MCP configuration..."

# Create Claude Desktop config with Alpaca MCP
cat > ~/.config/claude-desktop/config.json << 'CLAUDE_CONFIG'
{
  "mcpServers": {
    "alpaca": {
      "command": "npx",
      "args": [
        "-y",
        "@alpacahq/mcp-server-alpaca"
      ],
      "env": {
        "ALPACA_API_KEY": "YOUR_ALPACA_API_KEY",
        "ALPACA_API_SECRET": "YOUR_ALPACA_API_SECRET",
        "ALPACA_PAPER": "true"
      }
    }
  }
}
CLAUDE_CONFIG

echo "✅ Claude Desktop config created at ~/.config/claude-desktop/config.json"
echo ""
echo "📝 Next steps:"
echo "1. Edit ~/.config/claude-desktop/config.json"
echo "2. Replace YOUR_ALPACA_API_KEY with: $(grep ALPACA_PAPER_API_KEY .env | cut -d '=' -f2)"
echo "3. Replace YOUR_ALPACA_API_SECRET with: $(grep ALPACA_PAPER_API_SECRET .env | cut -d '=' -f2)"
echo "4. Restart Claude Desktop"
echo ""
echo "🎉 Setup complete!"
