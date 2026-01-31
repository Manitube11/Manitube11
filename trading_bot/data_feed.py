import yfinance as yf
import pandas as pd
import numpy as np
import time

class RealTimeDataFeed:
    def __init__(self):
        # Default Assets (Top Crypto, Forex, Commodities, Stocks, Indices)
        self.default_assets = {
            # --- Crypto ---
            "Bitcoin (BTC)": "BTC-USD",
            "Ethereum (ETH)": "ETH-USD",
            "Solana (SOL)": "SOL-USD",
            "XRP (XRP)": "XRP-USD",
            "Binance Coin (BNB)": "BNB-USD",
            "Dogecoin (DOGE)": "DOGE-USD",
            "Cardano (ADA)": "ADA-USD",
            "Tron (TRX)": "TRX-USD",
            "Avalanche (AVAX)": "AVAX-USD",
            "Chainlink (LINK)": "LINK-USD",
            "Shiba Inu (SHIB)": "SHIB-USD",
            "Polkadot (DOT)": "DOT-USD",
            "Litecoin (LTC)": "LTC-USD",
            "Bitcoin Cash (BCH)": "BCH-USD",
            "Uniswap (UNI)": "UNI-USD",
            "Pepe (PEPE)": "PEPE-USD",

            # --- Commodities ---
            "Gold (XAU)": "GC=F",
            "Silver (XAG)": "SI=F",
            "Oil (Crude)": "CL=F",
            "Natural Gas": "NG=F",

            # --- Forex ---
            "EUR/USD": "EURUSD=X",
            "GBP/USD": "GBPUSD=X",
            "USD/JPY": "JPY=X",

            # --- US Tech Stocks ---
            "Apple (AAPL)": "AAPL",
            "Nvidia (NVDA)": "NVDA",
            "Tesla (TSLA)": "TSLA",
            "Microsoft (MSFT)": "MSFT",
            "Amazon (AMZN)": "AMZN",
            "Google (GOOG)": "GOOG",
            "Meta (META)": "META",

            # --- Indices ---
            "S&P 500": "^GSPC",
            "Nasdaq 100": "^IXIC",
        }

        # Working dictionary (starts with defaults, can be modified)
        self.assets = self.default_assets.copy()

    def add_asset(self, name, ticker):
        """Adds a new asset to the watchlist."""
        self.assets[name] = ticker

    def remove_asset(self, name):
        """Removes an asset from the watchlist."""
        if name in self.assets:
            del self.assets[name]

    def fetch_history(self, symbol_name, days=100):
        """
        Fetches historical data including Volume for advanced analysis.
        Tries yfinance first; falls back to simulation if that fails (for testing/offline).
        """
        ticker_symbol = self.assets.get(symbol_name)
        if not ticker_symbol:
            return pd.DataFrame()

        try:
            ticker = yf.Ticker(ticker_symbol)
            # Fetch daily data
            data = ticker.history(period=f"{days}d", interval="1d")

            if not data.empty and len(data) > 10: # Ensure we have enough data
                # Clean up and ensure we have Volume
                data = data[['Open', 'High', 'Low', 'Close', 'Volume']].reset_index()
                return data
            else:
                # If data is empty or too short, raise exception to trigger fallback
                raise Exception(f"Insufficient data for {ticker_symbol}")

        except Exception as e:
            # print(f"Warning: Could not fetch real data for {symbol_name} ({e}). Using Simulation.")
            return self._generate_dummy_data(days, symbol_name)

    def _generate_dummy_data(self, days, symbol_name):
        """Generates realistic-looking dummy data for testing."""
        np.random.seed(int(time.time()) + len(symbol_name))

        # Base price guesses
        base_prices = {
            "Bitcoin (BTC)": 95000, "Ethereum (ETH)": 3200, "Solana (SOL)": 110,
            "Gold (XAU)": 2000, "Oil (Crude)": 75, "Apple (AAPL)": 230
        }
        start_price = base_prices.get(symbol_name, 100) # Default to 100 if unknown

        # Geometric Brownian Motion
        mu = 0.0002  # drift
        sigma = 0.02 # volatility
        dt = 1

        prices = [start_price]
        for _ in range(days):
            price = prices[-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.normal())
            prices.append(price)

        df = pd.DataFrame()
        df['Close'] = prices[1:]
        df['Open'] = [p * (1 + np.random.uniform(-0.01, 0.01)) for p in df['Close']]
        df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + np.random.uniform(0, 0.02))
        df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - np.random.uniform(0, 0.02))
        df['Volume'] = np.random.randint(1000, 100000, size=days)

        return df

if __name__ == "__main__":
    feed = RealTimeDataFeed()
    print("Testing Feed with Extended Assets...")
    # Test a stock
    df = feed.fetch_history("Apple (AAPL)", 100)
    print("AAPL Data Check:", not df.empty)
