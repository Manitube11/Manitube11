import yfinance as yf
import pandas as pd
import numpy as np
import time

class RealTimeDataFeed:
    def __init__(self):
        # Expanded Asset List (Top Cryptos + Commodities)
        self.assets = {
            "Bitcoin (BTC)": "BTC-USD",
            "Ethereum (ETH)": "ETH-USD",
            "Binance Coin (BNB)": "BNB-USD",
            "Solana (SOL)": "SOL-USD",
            "XRP (XRP)": "XRP-USD",
            "Cardano (ADA)": "ADA-USD",
            "Dogecoin (DOGE)": "DOGE-USD",
            "Polkadot (DOT)": "DOT-USD",
            "Polygon (MATIC)": "MATIC-USD",
            "Litecoin (LTC)": "LTC-USD",
            "Gold (XAU)": "GC=F",
            "Oil (Crude)": "CL=F"
        }

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

            if not data.empty:
                # Clean up and ensure we have Volume
                data = data[['Open', 'High', 'Low', 'Close', 'Volume']].reset_index()
                return data
            else:
                raise Exception("Empty data returned")

        except Exception as e:
            # print(f"Warning: Could not fetch real data for {symbol_name} ({e}). Using Simulation.")
            return self._generate_dummy_data(days, symbol_name)

    def _generate_dummy_data(self, days, symbol_name):
        """Generates realistic-looking dummy data for testing."""
        np.random.seed(int(time.time()) + len(symbol_name))

        # Base price guesses
        base_prices = {
            "Bitcoin (BTC)": 95000, "Ethereum (ETH)": 3200, "Solana (SOL)": 110,
            "Gold (XAU)": 2000, "Oil (Crude)": 75
        }
        start_price = base_prices.get(symbol_name, 100)

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
    df = feed.fetch_history("Solana (SOL)", 100)
    print(df.tail())
