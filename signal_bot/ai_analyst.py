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

        # Priority list of models based on availability
        # We prioritize newer, faster models found in the user's account
        model_candidates = [
            'gemini-2.0-flash',       # Latest fast model
            'gemini-2.0-flash-lite',  # Lightweight alternative
            'gemini-1.5-flash',       # Previous standard
            'gemini-1.5-pro',
            'gemini-pro'              # Legacy fallback
        ]

        model = None
        used_model_name = ""

        for m_name in model_candidates:
            try:
                # Attempt to instantiate the model
                model = genai.GenerativeModel(m_name)
                # We make a lightweight test call or just assume it works if no error on instantiation
                # But instantiation doesn't hit the network. We'll proceed to generate content.
                used_model_name = m_name
                break
            except:
                continue

        # If loop finishes without error, 'model' is set to the first successful candidate
        # (or last if all fail instantiation, which is unlikely for the class itself).
        # Real validation happens on generate_content.

        # Prepare the data for the prompt.
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

        # We need a loop for generation because instantiation might succeed but generation fails (404)
        last_error = ""
        for m_name in model_candidates:
            try:
                model = genai.GenerativeModel(m_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                last_error = str(e)
                # If 404 or not found, continue to next model
                if "404" in str(e) or "not found" in str(e).lower():
                    continue
                else:
                    # If it's another error (auth, quota), break and return error
                    return f"Error connecting to AI ({m_name}): {str(e)}"

        return f"Error: Could not find a working model. Tried: {', '.join(model_candidates)}. Last error: {last_error}"

    except Exception as e:
        return f"Error connecting to AI: {str(e)}\n\n*Hint: Check your API Key or try again later.*"
