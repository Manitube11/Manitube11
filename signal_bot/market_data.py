import yfinance as yf
import pandas as pd
import numpy as np

def get_historical_data(symbol, period='1mo', interval='1d'):
    """
    Fetches historical data for a given symbol using yfinance.
    Adds professional technical indicators:
    - EMA_50 (Exponential Moving Average)
    - RSI_14 (Relative Strength Index)
    - MACD (12, 26, 9)
    - Bollinger Bands (20, 2)
    """
    try:
        # Fetch data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)

        if data.empty:
            return None

        # --- Indicators Calculation ---

        # 1. EMA 50
        data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()

        # 2. RSI 14 (Wilder's Smoothing preferred, but simple EWM is close enough for standard use)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0))
        loss = (-delta.where(delta < 0, 0))

        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()

        rs = avg_gain / avg_loss
        data['RSI_14'] = 100 - (100 / (1 + rs))

        # 3. MACD (12, 26, 9)
        k = data['Close'].ewm(span=12, adjust=False).mean()
        d = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD_Line'] = k - d
        data['MACD_Signal'] = data['MACD_Line'].ewm(span=9, adjust=False).mean()
        data['MACD_Hist'] = data['MACD_Line'] - data['MACD_Signal']

        # 4. Bollinger Bands (20, 2)
        data['BB_Middle'] = data['Close'].rolling(window=20).mean()
        std_dev = data['Close'].rolling(window=20).std()
        data['BB_Upper'] = data['BB_Middle'] + (2 * std_dev)
        data['BB_Lower'] = data['BB_Middle'] - (2 * std_dev)

        # Reset index to make Date a column
        data.reset_index(inplace=True)

        # Convert Date to string for better display/JSON compatibility
        data['Date'] = data['Date'].astype(str)

        # Fill NaNs (important for initial calculation rows)
        data.fillna(0, inplace=True)

        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
