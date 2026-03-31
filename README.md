# Telegram Signal Bot with AI Analysis

This bot provides real-time trading signals for Crypto, Stocks, and Forex (Gold) using technical analysis (RSI, MACD, EMA, Bollinger Bands) and AI-powered insights from Google Gemini.

## Features

- **Multi-Asset Support:** Analyzes Crypto (via CoinGecko), Stocks, and Gold (via Yahoo Finance).
- **Technical Analysis:** Calculates RSI, MACD, EMA trends, and Bollinger Bands.
- **AI Integration:** Uses Google Gemini (Flash 2.0) to generate professional trading summaries and risk assessments.
- **Telegram Commands:**
  - `/analyze <symbol>`: Get an instant report (e.g., `/analyze BTC`, `/analyze AAPL`).
  - `/start`: Welcome message.
  - `/help`: List commands.
- **Automatic Alerts:** Monitors configured assets every hour and sends alerts for "Strong Buy/Sell" signals.

## Setup Instructions

1.  **Install Python:** Ensure you have Python installed (3.10+ recommended).
2.  **Get API Keys:**
    - **Telegram Bot Token:** You provided: `8415108013:AAG9_GgOVuCRGVR8j1aWz2mLzvVjH7F5GP8`
    - **Gemini API Key:** Get it from [Google AI Studio](https://aistudio.google.com/).
    - **CoinGecko API Key:** You provided: `CG-xPNuLpcPm6VzrDwivBH6VciX`
3.  **Configure `.env`:**
    - **Note:** The `install.bat` script will create a `.env` file from `.env.example` if it doesn't exist.
    - Open the `.env` file in a text editor.
    - Fill in the keys:
      ```
      TELEGRAM_TOKEN=8415108013:AAG9_GgOVuCRGVR8j1aWz2mLzvVjH7F5GP8
      TELEGRAM_CHAT_ID=1784010723
      COINGECKO_API_KEY=CG-xPNuLpcPm6VzrDwivBH6VciX
      GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE
      ```
    - Verify other keys are correct.
4.  **Install Dependencies:**
    - Double-click `install.bat`.
5.  **Run the Bot:**
    - Double-click `run.bat`.

## Configuration

You can customize the list of assets to monitor in `src/config.py`:
- `CRYPTO_PAIRS`: List of crypto symbols (e.g., ["BTC", "ETH"]).
- `STOCK_SYMBOLS`: List of stock tickers (e.g., ["AAPL", "TSLA"]).
- `FOREX_PAIRS`: List of forex/commodity tickers (e.g., ["GC=F"] for Gold).

## Troubleshooting

- **"AI Analysis Unavailable":** Check if `GEMINI_API_KEY` is set correctly in `.env`.
- **Connection Errors:** Ensure you have internet access. If you are in a restricted region, you might need a VPN/Proxy (the bot uses standard HTTPS requests).

## License

MIT
