"""
Email Notifier - Sends daily trading summaries via email
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional
from utils.logger import get_logger

log = get_logger("email_notifier")


def send_trading_summary(summary: Dict, to_email: str):
    """
    Send daily trading summary via email.
    
    Args:
        summary: Trading summary dict with metrics
        to_email: Recipient email address
    """
    # Email configuration
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    from_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not from_email or not smtp_password:
        log.warning("Email credentials not configured. Skipping email notification.")
        return
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🤖 DJN Trading Bot Daily Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Create email body
        html_body = create_html_email(summary)
        text_body = create_text_email(summary)
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, smtp_password)
            server.send_message(msg)
        
        log.info(f"✅ Email summary sent to {to_email}")
        
    except Exception as e:
        log.error(f"Failed to send email: {e}")


def create_html_email(summary: Dict) -> str:
    """Create HTML email body."""
    
    # Extract summary data
    timestamp = summary.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    avg_sentiment = summary.get('avg_sentiment', 0)
    signals_count = summary.get('n_signals', 0)
    executed_count = summary.get('executed_count', 0)
    cash_left = summary.get('cash_left', 0)
    mode = summary.get('mode', 'unknown')
    
    # Performance metrics (if available)
    win_rate = summary.get('win_rate', 0)
    total_pnl = summary.get('total_pnl', 0)
    total_trades = summary.get('total_trades', 0)
    
    # Sentiment emoji
    sentiment_emoji = "🟢" if avg_sentiment > 0.5 else "🟡" if avg_sentiment > 0.3 else "🔴"
    
    # Mode emoji
    mode_emoji = "📝" if mode == "simulation" else "📄" if "paper" in mode else "💰"
    
    html = f"""
    <html>
      <head>
        <style>
          body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
          }}
          .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
          }}
          .metric-card {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
          }}
          .metric-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            font-weight: bold;
          }}
          .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-top: 5px;
          }}
          .positive {{ color: #10b981; }}
          .negative {{ color: #ef4444; }}
          .neutral {{ color: #f59e0b; }}
          .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            font-size: 12px;
            color: #666;
            text-align: center;
          }}
          .insight {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 10px;
            margin: 15px 0;
            border-radius: 5px;
          }}
        </style>
      </head>
      <body>
        <div class="header">
          <h1>🤖 DJN Trading Bot</h1>
          <p>Daily Performance Update</p>
          <p style="font-size: 14px; opacity: 0.9;">{timestamp}</p>
        </div>
        
        <div class="metric-card">
          <div class="metric-label">{sentiment_emoji} Market Sentiment</div>
          <div class="metric-value {'positive' if avg_sentiment > 0.5 else 'neutral' if avg_sentiment > 0.3 else 'negative'}">
            {avg_sentiment:.1%}
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-label">📊 Trading Activity</div>
          <div class="metric-value">
            {signals_count} Signals Generated
          </div>
          <div style="margin-top: 10px;">
            ✅ {executed_count} Orders Executed
          </div>
        </div>
        
        <div class="metric-card">
          <div class="metric-label">💰 Capital Status</div>
          <div class="metric-value">
            ${cash_left:.2f} Available
          </div>
        </div>
        
        {"" if total_trades == 0 else f'''
        <div class="metric-card">
          <div class="metric-label">📈 Overall Performance</div>
          <div class="metric-value">
            <span class="{'positive' if win_rate >= 0.55 else 'neutral' if win_rate >= 0.45 else 'negative'}">
              {win_rate:.1%} Win Rate
            </span>
          </div>
          <div style="margin-top: 10px;">
            Total Trades: {total_trades} | 
            <span class="{'positive' if total_pnl >= 0 else 'negative'}">
              P&L: ${total_pnl:.2f}
            </span>
          </div>
        </div>
        '''}
        
        <div class="insight">
          <strong>💡 Trading Mode:</strong> {mode_emoji} {mode.replace('_', ' ').title()}
        </div>
        
        <div class="footer">
          <p><strong>🤖 Your bot is trading automatically!</strong></p>
          <p>View details: <a href="https://github.com/DJN2709/DJN-Broker/actions">GitHub Actions</a></p>
          <p>Check positions: <a href="https://app.alpaca.markets/paper/dashboard/overview">Alpaca Dashboard</a></p>
          <p style="margin-top: 20px; font-size: 11px; color: #999;">
            This is an automated message from DJN Trading Bot.<br>
            Paper trading with virtual money - no real risk.
          </p>
        </div>
      </body>
    </html>
    """
    
    return html


def create_text_email(summary: Dict) -> str:
    """Create plain text email body."""
    
    timestamp = summary.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    avg_sentiment = summary.get('avg_sentiment', 0)
    signals_count = summary.get('n_signals', 0)
    executed_count = summary.get('executed_count', 0)
    cash_left = summary.get('cash_left', 0)
    mode = summary.get('mode', 'unknown')
    win_rate = summary.get('win_rate', 0)
    total_pnl = summary.get('total_pnl', 0)
    total_trades = summary.get('total_trades', 0)
    
    sentiment_status = "Bullish" if avg_sentiment > 0.5 else "Neutral" if avg_sentiment > 0.3 else "Bearish"
    
    text = f"""
    DJN TRADING BOT - DAILY UPDATE
    ==============================
    
    Date: {timestamp}
    
    MARKET SENTIMENT
    ----------------
    Status: {sentiment_status}
    Score: {avg_sentiment:.1%}
    
    TRADING ACTIVITY
    ----------------
    Signals Generated: {signals_count}
    Orders Executed: {executed_count}
    
    CAPITAL STATUS
    --------------
    Available: ${cash_left:.2f}
    Mode: {mode.replace('_', ' ').title()}
    """
    
    if total_trades > 0:
        text += f"""
    
    OVERALL PERFORMANCE
    -------------------
    Total Trades: {total_trades}
    Win Rate: {win_rate:.1%}
    Total P&L: ${total_pnl:.2f}
        """
    
    text += """
    
    LINKS
    -----
    View Runs: https://github.com/DJN2709/DJN-Broker/actions
    Alpaca Account: https://app.alpaca.markets/paper/dashboard/overview
    
    ---
    This is an automated message from DJN Trading Bot.
    Paper trading with virtual money - no real risk.
    """
    
    return text

