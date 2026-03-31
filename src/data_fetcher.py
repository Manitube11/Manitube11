import requests
import pandas as pd
import yfinance as yf
import datetime
import os
try:
    from src import config
except ImportError:
    import config

class DataFetcher:
    """Base class for fetching market data."""
    def get_historical_data(self, symbol, days=30):
        raise NotImplementedError

class CryptoFetcher(DataFetcher):
    """Fetches crypto data from CoinGecko."""
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {
            "x-cg-demo-api-key": config.COINGECKO_API_KEY
        }
        # Simple mapping for common symbols
        self.symbol_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "BNB": "binancecoin",
            "XRP": "ripple",
            "ADA": "cardano",
            "DOGE": "dogecoin",
            "DOT": "polkadot",
            "LTC": "litecoin",
            "SHIB": "shiba-inu"
        }

    def _get_coin_id(self, symbol):
        # Remove USDT if present (e.g., BTCUSDT -> BTC)
        clean_symbol = symbol.upper().replace("USDT", "").replace("USD", "")
        return self.symbol_map.get(clean_symbol, clean_symbol.lower())

    def get_historical_data(self, symbol, days=30):
        """
        Fetches historical OHLC data for a crypto symbol.
        Symbol: 'BTC', 'ETH', 'BTCUSDT' -> converted to CoinGecko ID.
        """
        coin_id = self._get_coin_id(symbol)

        # specific endpoint for OHLC: /coins/{id}/ohlc?vs_currency=usd&days={days}
        # Note: CoinGecko OHLC only supports specific day ranges: 1, 7, 14, 30, 90, 180, 365, max
        if days <= 1:
            days_param = "1"
        elif days <= 7:
            days_param = "7"
        elif days <= 14:
            days_param = "14"
        elif days <= 30:
            days_param = "30"
        else:
            days_param = "max"

        url = f"{self.base_url}/coins/{coin_id}/ohlc"
        params = {
            "vs_currency": "usd",
            "days": days_param
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                return pd.DataFrame()

            # Data format: [[time, open, high, low, close], ...]
            # Columns: Timestamp, Open, High, Low, Close
            df = pd.DataFrame(data, columns=["Date", "Open", "High", "Low", "Close"])
            df["Date"] = pd.to_datetime(df["Date"], unit="ms")
            df.set_index("Date", inplace=True)
            return df
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {symbol} ({coin_id}): {e}")
            return pd.DataFrame()

class StockFetcher(DataFetcher):
    """Fetches stock and commodity data from Yahoo Finance."""
    def get_historical_data(self, symbol, days=30):
        """
        Fetches historical data using yfinance.
        Symbol: 'AAPL', 'GC=F' (Gold), etc.
        """
        try:
            # yfinance period: 1mo, 3mo, 6mo, 1y, etc.
            period = "1mo"
            if days > 30:
                period = "3mo"

            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval="1d")

            if df.empty:
                print(f"No data found for {symbol}")
                return pd.DataFrame()

            # yfinance returns: Open, High, Low, Close, Volume, Dividends, Stock Splits
            # Ensure index is datetime
            # df.index is already DatetimeIndex
            return df[["Open", "High", "Low", "Close", "Volume"]]
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {e}")
            return pd.DataFrame()

def get_fetcher(asset_type):
    if asset_type == "crypto":
        return CryptoFetcher()
    elif asset_type == "stock" or asset_type == "forex" or asset_type == "gold":
        return StockFetcher()
    else:
        # Default to StockFetcher if unsure (yfinance covers a lot)
        return StockFetcher()
