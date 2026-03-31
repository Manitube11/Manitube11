import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import functools

try:
    from src import config
    from src.data_fetcher import get_fetcher
    from src.indicators import analyze_market
    from src.ai_agent import get_ai_summary
except ImportError:
    import config
    from data_fetcher import get_fetcher
    from indicators import analyze_market
    from ai_agent import get_ai_summary

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store last alert times to avoid spam
last_alert_times = {}
ALERT_COOLDOWN = timedelta(hours=4)

async def run_blocking(func, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to the Signal Bot! Use /analyze <symbol> to get a report."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Commands:\n/analyze <symbol> - Analyze a crypto or stock (e.g., /analyze BTC, /analyze AAPL)\n/start - Start the bot"
    )

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a symbol. Usage: /analyze BTC")
        return

    symbol = context.args[0].upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Analyzing {symbol}...")

    # Determine asset type (heuristic)
    # Crypto usually 3-4 chars, Stocks often similar but we check crypto first
    # Or check if it's in our known lists?
    # Simple heuristic: If it fails crypto, try stock.

    # Run fetcher in executor
    def fetch_data(sym):
        fetcher = get_fetcher("crypto")
        df = fetcher.get_historical_data(sym)
        if df.empty:
            fetcher = get_fetcher("stock")
            df = fetcher.get_historical_data(sym)
            return df, "Stock" if not df.empty else "Unknown"
        return df, "Crypto"

    df, asset_type = await run_blocking(fetch_data, symbol)

    if df.empty:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Could not find data for {symbol}.")
        return

    # Analyze (CPU bound but fast, can stay in main thread or move to executor)
    # We'll keep it simple
    analysis = analyze_market(df)

    if analysis['signal'] == "ERROR":
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error analyzing data: {analysis.get('reason')}")
        return

    # AI Summary (Network bound, blocking)
    ai_summary = await run_blocking(
        get_ai_summary,
        symbol,
        analysis['indicators']['Close'],
        analysis['indicators'],
        analysis['signal']
    )

    # Format Message
    message = (
        f"📊 *Analysis for {symbol} ({asset_type})*\n"
        f"Price: {analysis['indicators']['Close']:.2f}\n"
        f"Signal: *{analysis['signal']}* (Score: {analysis['score']})\n\n"
        f"Technical Indicators:\n"
        f"• RSI: {analysis['indicators']['RSI']:.2f}\n"
        f"• MACD: {analysis['indicators']['MACD']:.2f}\n"
        f"• BB: {analysis['indicators']['BB_Lower']:.2f} / {analysis['indicators']['BB_Upper']:.2f}\n\n"
        f"🤖 *AI Insight:*\n{ai_summary}"
    )

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='Markdown')

async def check_alerts(context: ContextTypes.DEFAULT_TYPE):
    """Background job to check for strong signals."""
    logger.info("Running background alert check...")

    # Combined list of assets to check
    assets = [("crypto", s) for s in config.CRYPTO_PAIRS] + \
             [("stock", s) for s in config.STOCK_SYMBOLS] + \
             [("forex", s) for s in config.FOREX_PAIRS]

    for asset_type, symbol in assets:
        try:
            # Fetch data (blocking)
            def fetch_and_analyze(atype, sym):
                f = get_fetcher(atype)
                d = f.get_historical_data(sym)
                if d.empty: return None
                return analyze_market(d)

            analysis = await run_blocking(fetch_and_analyze, asset_type, symbol)

            if not analysis:
                continue

            signal = analysis['signal']

            # Check for strong signals
            if "STRONG" in signal:
                # Check cooldown
                last_time = last_alert_times.get(symbol)
                if last_time and datetime.now() - last_time < ALERT_COOLDOWN:
                    continue

                # Generate AI Summary for the alert (blocking)
                ai_summary = await run_blocking(
                    get_ai_summary,
                    symbol,
                    analysis['indicators']['Close'],
                    analysis['indicators'],
                    signal
                )

                message = (
                    f"🚨 *ALERT: {symbol} - {signal}* 🚨\n"
                    f"Price: {analysis['indicators']['Close']:.2f}\n"
                    f"Score: {analysis['score']}\n\n"
                    f"🤖 *AI Insight:*\n{ai_summary}"
                )

                # Send to configured Chat ID
                if config.TELEGRAM_CHAT_ID:
                    await context.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
                    last_alert_times[symbol] = datetime.now()
                else:
                    logger.warning("TELEGRAM_CHAT_ID not set. Cannot send alert.")

        except Exception as e:
            logger.error(f"Error checking alert for {symbol}: {e}")

def run_bot():
    if not config.TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN not set in config.")
        return

    application = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("analyze", analyze))

    # Add JobQueue for background tasks
    if application.job_queue:
        # Run every 60 minutes (3600 seconds)
        application.job_queue.run_repeating(check_alerts, interval=3600, first=10)
        print("Background alert monitoring enabled.")
    else:
        logger.warning("JobQueue not available. Background alerts disabled.")

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    run_bot()
