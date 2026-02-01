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

    def _smart_fetch(self, ticker_symbol, period, interval):
        """
        Helper: Tries to fetch data. If empty and no hyphen, tries appending -USD.
        Returns: (DataFrame, Used_Ticker)
        """
        # 1. Try Original
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period, interval=interval)

        if not df.empty:
            return df, ticker_symbol

        # 2. Smart Retry: Append -USD if likely crypto (no hyphen, no =, no ^)
        if "-" not in ticker_symbol and "=" not in ticker_symbol and "^" not in ticker_symbol:
            smart_ticker = f"{ticker_symbol}-USD"
            ticker = yf.Ticker(smart_ticker)
            df = ticker.history(period=period, interval=interval)
            if not df.empty:
                return df, smart_ticker

        return df, ticker_symbol

    def get_live_price(self, symbol_name):
        """
        FAST PATH: Fetches only the latest price using 1-minute intervals.
        """
        ticker_symbol = self.assets.get(symbol_name)
        if not ticker_symbol:
            return None, "NONE"

        if ticker_symbol.startswith('$'):
            ticker_symbol = ticker_symbol.replace('$', '')

        try:
            # Smart Fetch (Try "BONK" -> "BONK-USD" if needed)
            df, used_ticker = self._smart_fetch(ticker_symbol, "1d", "1m")

            if not df.empty:
                return df['Close'].iloc[-1], "LIVE"

            # Try fast_info on the *last successful* ticker (used_ticker)
            ticker = yf.Ticker(used_ticker)
            if hasattr(ticker, 'fast_info') and 'last_price' in ticker.fast_info:
                 return ticker.fast_info['last_price'], "LIVE"

        except Exception as e:
            pass

        # Fallback: Try Binance API
        price = self._fetch_current_price_fallback(ticker_symbol)
        if price:
            return price, "LIVE"

        # Final Fallback: Simulation
        try:
            df = self._generate_dummy_data(2, symbol_name)
            return df['Close'].iloc[-1], "SIM"
        except:
            return 0.0, "SIM"

    def fetch_history(self, symbol_name, days=100):
        """
        SLOW PATH: Fetches historical data including Volume.
        """
        ticker_symbol = self.assets.get(symbol_name)
        if not ticker_symbol:
            return pd.DataFrame(), "NONE"

        if ticker_symbol.startswith('$'):
            ticker_symbol = ticker_symbol.replace('$', '')

        try:
            # Smart Fetch
            df, used_ticker = self._smart_fetch(ticker_symbol, f"{days}d", "1d")

            if not df.empty and len(df) > 10:
                df = df[['Open', 'High', 'Low', 'Close', 'Volume']].reset_index()
                if df['Date'].dt.tz is not None:
                    df['Date'] = df['Date'].dt.tz_localize(None)

                # If we successfully corrected the ticker (e.g. BONK -> BONK-USD),
                # we should probably update the map so next time it's faster.
                if used_ticker != ticker_symbol:
                    self.assets[symbol_name] = used_ticker

                return df, "LIVE"
            else:
                raise Exception("Empty data from yfinance")

        except Exception as e:
            # Fallback
            real_price = self._fetch_current_price_fallback(ticker_symbol)
            print(f"[Data Feed] Warning: Live data failed for {symbol_name}. Switching to Simulation (Anchor Price: {real_price})")
            df = self._generate_dummy_data(days, symbol_name, anchor_price=real_price)
            return df, "SIM"

    def _fetch_current_price_fallback(self, ticker):
        """
        Tries to fetch the current price from alternative public APIs (Binance).
        """
        try:
            # Try to guess the pair for Binance
            # If ticker is "BONK", make it "BONKUSDT"
            # If ticker is "BONK-USD", make it "BONKUSDT"
            symbol = ticker.replace("-USD", "USDT")
            if "-" not in ticker and "USDT" not in symbol:
                symbol += "USDT"

            if "=" in symbol or "^" in symbol: return None

            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                data = r.json()
                return float(data['price'])
        except:
            pass
        return None

    def _generate_dummy_data(self, days, symbol_name, anchor_price=None):
        """Generates dummy data."""
        np.random.seed(int(time.time()) + len(symbol_name))

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

        if anchor_price:
            target_price = anchor_price
        else:
            target_price = 100
            for key, val in base_prices.items():
                if key in symbol_name:
                    target_price = val
                    break

        prices = [target_price]
        mu = 0.0002
        sigma = 0.02
        dt = 1

        for _ in range(days):
            prev_price = prices[-1] / np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.normal())
            prices.append(prev_price)

        prices.reverse()

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
    print("Testing Feed Smart Fetch...")

    # Test 1: Known bad ticker (DOGE) -> Should correct to DOGE-USD
    print("Test 1: Fetching 'DOGE' (no suffix)...")
    feed.add_asset("Doge Test", "DOGE")
    df, src = feed.fetch_history("Doge Test", 10)
    print(f"Result: {src}, Rows: {len(df)}")

    # Check if correction persisted
    print(f"Corrected Ticker in Map: {feed.assets['Doge Test']}")
