import yfinance as yf
import pandas as pd
import numpy as np
import time
import requests

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
        Fetches historical data including Volume.
        Returns: (DataFrame, source_type) where source_type is 'LIVE' or 'SIM'.
        """
        ticker_symbol = self.assets.get(symbol_name)
        if not ticker_symbol:
            return pd.DataFrame(), "NONE"

        if ticker_symbol.startswith('$'):
            ticker_symbol = ticker_symbol.replace('$', '')

        try:
            # 1. Try yfinance
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(period=f"{days}d", interval="1d")

            if not data.empty and len(data) > 10:
                data = data[['Open', 'High', 'Low', 'Close', 'Volume']].reset_index()
                # Ensure timezone naive for consistency
                if data['Date'].dt.tz is not None:
                    data['Date'] = data['Date'].dt.tz_localize(None)
                return data, "LIVE"
            else:
                raise Exception("Empty data from yfinance")

        except Exception as e:
            # 2. Fallback
            # Try to get a real price to anchor the simulation
            real_price = self._fetch_current_price_fallback(ticker_symbol)

            print(f"[Data Feed] Warning: Live data failed for {symbol_name}. Switching to Simulation (Anchor Price: {real_price})")

            # Generate dummy data anchored to the real price (or a realistic default)
            df = self._generate_dummy_data(days, symbol_name, anchor_price=real_price)
            return df, "SIM"

    def _fetch_current_price_fallback(self, ticker):
        """
        Tries to fetch the current price from alternative public APIs (Binance)
        to make the simulation realistic. Returns None if it fails.
        """
        # Simple mapping for Binance (remove -USD, append USDT)
        # This is a 'best effort' mapping
        try:
            symbol = ticker.replace("-USD", "USDT")
            if "=" in symbol or "^" in symbol: return None # Skip futures/indices for simple API

            # Binance API
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                data = r.json()
                return float(data['price'])
        except:
            pass
        return None

    def _generate_dummy_data(self, days, symbol_name, anchor_price=None):
        """
        Generates dummy data.
        If anchor_price is provided, the data ends near that price.
        Otherwise, uses realistic hardcoded defaults.
        """
        np.random.seed(int(time.time()) + len(symbol_name))

        # Realistic Fallback Prices (Updated Feb 2025)
        base_prices = {
            "Bitcoin (BTC)": 78000,
            "Ethereum (ETH)": 2600,
            "Solana (SOL)": 95,
            "XRP (XRP)": 1.10,
            "Binance Coin (BNB)": 600,
            "Dogecoin (DOGE)": 0.14,
            "Cardano (ADA)": 0.45,
            "Tron (TRX)": 0.12,
            "Avalanche (AVAX)": 35,
            "Chainlink (LINK)": 15,
            "Shiba Inu (SHIB)": 0.00002,
            "Polkadot (DOT)": 7.00,
            "Litecoin (LTC)": 70,

            "Gold (XAU)": 2050,
            "Oil (Crude)": 75,
            "Apple (AAPL)": 225,
            "Nvidia (NVDA)": 120,
            "Tesla (TSLA)": 200,
            "Microsoft (MSFT)": 415,
            "Google (GOOG)": 175,
            "Meta (META)": 470,

            "EUR/USD": 1.08,
            "GBP/USD": 1.26,
            "USD/JPY": 150,
        }

        # Determine target price
        if anchor_price:
            target_price = anchor_price
        else:
            # Fuzzy match or default
            target_price = 100 # absolute fallback
            for key, val in base_prices.items():
                if key in symbol_name:
                    target_price = val
                    break

        # Generate History Backwards from Target
        prices = [target_price]

        mu = 0.0002  # drift
        sigma = 0.02 # volatility
        dt = 1

        # We generate backwards so the *last* point is the target price
        for _ in range(days):
            # Inverse GBM roughly
            prev_price = prices[-1] / np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.normal())
            prices.append(prev_price)

        prices.reverse() # Now it flows from past to target

        df = pd.DataFrame()
        df['Close'] = prices[1:]
        df['Open'] = [p * (1 + np.random.uniform(-0.01, 0.01)) for p in df['Close']]
        df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + np.random.uniform(0, 0.02))
        df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - np.random.uniform(0, 0.02))
        df['Volume'] = np.random.randint(1000, 100000, size=days)

        end_date = pd.Timestamp.now()
        df['Date'] = pd.date_range(end=end_date, periods=len(df), freq='D')

        return df

if __name__ == "__main__":
    feed = RealTimeDataFeed()
    print("Testing Feed...")
    # Test fallback
    # We can't force fallback easily without mocking, but we can call _generate
    df, source = feed.fetch_history("Bitcoin (BTC)", 100)
    print(f"BTC Source: {source}, Last Price: {df['Close'].iloc[-1]:.2f}")
