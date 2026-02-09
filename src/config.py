import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# APIs
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# Trading Settings
CRYPTO_PAIRS = ["BTC", "ETH", "SOL", "BNB"]  # Default list for alerts
STOCK_SYMBOLS = ["AAPL", "TSLA", "MSFT"]
FOREX_PAIRS = ["GC=F"] # Gold (GC=F from yfinance)

# Indicators
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
EMA_SHORT = 20
EMA_LONG = 50
BB_PERIOD = 20
BB_STD = 2

# Alert Thresholds
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
