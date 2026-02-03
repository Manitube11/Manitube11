import yfinance as yf
import pandas as pd

def get_historical_data(symbol, period='1mo', interval='1d'):
    """
    Fetches historical data for a given symbol using yfinance.
    Adds basic technical indicators (SMA_50, RSI_14).
    """
    try:
        # Fetch data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)

        if data.empty:
            return None

        # Calculate Simple Moving Average (SMA 50)
        data['SMA_50'] = data['Close'].rolling(window=50).mean()

        # Calculate RSI (14)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

        rs = gain / loss
        data['RSI_14'] = 100 - (100 / (1 + rs))

        # Reset index to make Date a column
        data.reset_index(inplace=True)

        # Convert Date to string for better display/JSON compatibility
        data['Date'] = data['Date'].astype(str)

        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
