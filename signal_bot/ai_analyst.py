import google.generativeai as genai
import pandas as pd

def analyze_market(data, api_key, symbol):
    """
    Sends market data to Google Gemini for analysis.
    """
    if data is None or data.empty:
        return "No data available for analysis."

    try:
        genai.configure(api_key=api_key)

        # Try to use the newer, more stable model first, then fallback
        model_name = 'gemini-1.5-flash'

        try:
            model = genai.GenerativeModel(model_name)
        except:
             model = genai.GenerativeModel('gemini-pro')

        # Prepare the data for the prompt.
        # We'll take the last 30 records to keep the prompt size reasonable but informative.
        # We assume data now has more columns (MACD, Bollinger, etc.)
        recent_data = data.tail(30).to_string()

        prompt = f"""
        Act as a Senior Financial Analyst and Professional Trader.
        Perform a deep technical analysis for {symbol} based on the provided historical data.
        The data includes OHLCV and technical indicators (EMA, RSI, MACD, Bollinger Bands).

        Data (Last 30 candles):
        {recent_data}

        Your Task:
        1. **Trend Analysis**: Identify the immediate and primary trend (Bullish/Bearish/Ranging) using EMA and Price Action.
        2. **Indicator Analysis**:
           - Interpret RSI (Overbought/Oversold/Divergence).
           - Interpret MACD (Crossovers/Momentum).
           - Interpret Bollinger Bands (Volatility/Squeeze/Breakout).
        3. **Signal & Setup**:
           - Provide a clear signal: **STRONG BUY**, **BUY**, **NEUTRAL**, **SELL**, or **STRONG SELL**.
           - Define precise entry zone.
           - Define 2 Take Profit targets (Conservative & Aggressive).
           - Define a Stop Loss level with reasoning.
        4. **Risk Management**: Suggest appropriate leverage or risk allocation.

        **Output Language**: Persian (Farsi).
        **Tone**: Professional, confident, and structured. Use emojis for readability.
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error connecting to AI: {str(e)}\n\n*Hint: Check your API Key or try again later.*"
