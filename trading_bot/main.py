import pandas as pd
import sys
import os

# Add current directory to path so imports work if run from inside/outside
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from market_sim import MarketSimulator
from analyzer import MarketAnalyzer
from notifier import TelegramNotifier
from trader import TradingEngine

def main():
    print("=======================================================")
    print("   ManiTube Trading Engine - Professional Prototype    ")
    print("             سیستم معاملاتی هوشمند مانی‌تیوب             ")
    print("=======================================================\n")

    # 1. Configuration
    # Updated with user provided credentials
    TELEGRAM_BOT_TOKEN = "8415108013:AAG9_GgOVuCRGVR8j1aWz2mLzvVjH7F5GP8"
    TELEGRAM_CHAT_ID = "25355589"

    # Check if still default (safety check, though we just set them)
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN" or TELEGRAM_CHAT_ID == "YOUR_CHAT_ID":
        print("\n[WARNING] Telegram is not configured properly.")
        print("[هشدار] تنظیمات تلگرام انجام نشده است. لطفاً فایل main.py را ویرایش کنید.")
        print("برای پیدا کردن Chat ID می‌توانید فایل 'trading_bot/get_chat_id.py' را اجرا کنید.\n")
        show_footer_help = True
    else:
        show_footer_help = False

    # 2. Initialization
    print("[1/4] Initializing Modules (ماژول‌ها)...")
    sim = MarketSimulator(start_price=65000, volatility=0.80)
    analyzer = MarketAnalyzer()
    notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    trader = TradingEngine(initial_cash=10000, notifier=notifier)

    # 3. Market Simulation
    print("[2/4] Simulating Market Data (شبیه‌سازی بازار)...")
    # Generating 90 days to ensure enough data for 30-day MA and then 60 days of trading
    raw_data = sim.generate_data(days=90)

    # 4. Analysis
    print("[3/4] Analyzing Indicators (تحلیل شاخص‌ها)...")
    analyzed_data = analyzer.analyze(raw_data)

    # 5. Trading Execution
    print("[4/4] Running Trading Strategy (اجرای استراتژی)...")
    # We slice to the last 60 days for the actual trading loop as requested,
    # but keeping enough history for MA calculation
    trading_data = analyzed_data.iloc[-60:].copy()
    ledger = trader.run_backtest(trading_data)

    # 6. Reporting
    print("\n" + "="*80)
    print("DAILY TRADING LEDGER (دفتر کل معاملات روزانه)")
    print("="*80)

    # Format columns for display
    display_ledger = ledger[['Date', 'Price', 'Signal', 'Action', 'Holdings', 'Cash', 'Portfolio Value']].copy()
    display_ledger['Price'] = display_ledger['Price'].apply(lambda x: f"${x:,.2f}")
    display_ledger['Cash'] = display_ledger['Cash'].apply(lambda x: f"${x:,.2f}")
    display_ledger['Portfolio Value'] = display_ledger['Portfolio Value'].apply(lambda x: f"${x:,.2f}")
    display_ledger['Holdings'] = display_ledger['Holdings'].apply(lambda x: f"{x:.4f} BTC")

    # Print all rows
    print(display_ledger.to_string(index=False))

    # Performance Summary
    perf = trader.calculate_performance()

    print("\n" + "="*40)
    print("PERFORMANCE SUMMARY (خلاصه عملکرد)")
    print("="*40)
    if perf:
        print(f"Total Return (بازده کل):      {perf['Total Return']:.2f}%")
        print(f"Total Trades (تعداد معاملات): {perf['Total Trades']}")
        print(f"Win Rate (نرخ برد):           {perf['Win Rate']:.1f}%")
        print(f"Max Drawdown (حداکثر افت):    {perf['Max Drawdown']:.2f}%")
        print(f"Final Value (ارزش نهایی):     ${perf['Final Value']:,.2f}")
    else:
        print("No trades were executed.")
    print("="*40)

    # Only show the help footer if config is missing
    if show_footer_help:
        print("\n[INFO] To enable Telegram notifications, edit 'main.py' and set TELEGRAM_BOT_TOKEN.")
        print("[راهنما] برای فعال‌سازی تلگرام، فایل main.py را ویرایش کرده و توکن ربات را وارد کنید.")

if __name__ == "__main__":
    main()
