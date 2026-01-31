import yfinance as yf
import pandas as pd
import time

class RealTimeDataFeed:
    def __init__(self):
        # Dictionary mapping display names to Yahoo Finance Tickers
        self.assets = {
            "Bitcoin (BTC)": "BTC-USD",
            "Ethereum (ETH)": "ETH-USD",
            "Gold (XAU)": "GC=F",
            "Oil (Crude)": "CL=F",
            "S&P 500": "^GSPC"
        }

    def fetch_live_price(self, symbol_name):
        """
        Fetches the latest price for a given asset name.
        """
        ticker_symbol = self.assets.get(symbol_name)
        if not ticker_symbol:
            return None

        try:
            ticker = yf.Ticker(ticker_symbol)
            # rapid fetch of last minute data
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return data.iloc[-1]['Close']
            else:
                # Fallback to daily if minute data fails
                data = ticker.history(period="1d")
                if not data.empty:
                    return data.iloc[-1]['Close']
        except Exception as e:
            print(f"Error fetching price for {symbol_name}: {e}")
        return None

    def fetch_history(self, symbol_name, days=60):
        """
        Fetches historical data for analysis (SMA, RSI).
        """
        ticker_symbol = self.assets.get(symbol_name)
        if not ticker_symbol:
            return pd.DataFrame()

        try:
            ticker = yf.Ticker(ticker_symbol)
            # Fetch slightly more to account for weekends/holidays in non-crypto
            data = ticker.history(period=f"{days+20}d", interval="1d")
            return data[['Open', 'High', 'Low', 'Close']].reset_index()
        except Exception as e:
            print(f"Error fetching history for {symbol_name}: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    feed = RealTimeDataFeed()
    print("Testing Real Time Feed...")
    price = feed.fetch_live_price("Bitcoin (BTC)")
    print(f"BTC Price: {price}")

    hist = feed.fetch_history("Bitcoin (BTC)", 30)
    print(hist.tail())
