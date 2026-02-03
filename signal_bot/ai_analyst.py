import google.generativeai as genai
import pandas as pd
import time
import re

def analyze_market(data, api_key, symbol):
    """
    Sends market data to Google Gemini for analysis.
    Includes robust handling for Rate Limits (429) and Model Not Found (404).
    """
    if data is None or data.empty:
        return "No data available for analysis."

    try:
        genai.configure(api_key=api_key)

        # Priority list of models
        model_candidates = [
            'gemini-2.0-flash',
            'gemini-2.0-flash-lite',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro'
        ]

        # Optimize Data to reduce tokens (Send last 15 rows + specific indicator summary)
        # This helps avoid token limits in free tier
        recent_data = data.tail(15).to_string()

        prompt = f"""
        Act as a Senior Financial Analyst and Professional Trader.
        Perform a deep technical analysis for {symbol} based on the provided historical data.
        The data includes OHLCV and technical indicators (EMA, RSI, MACD, Bollinger Bands).

        Data (Last 15 candles):
        {recent_data}

        Your Task:
        1. **Trend Analysis**: Identify the immediate and primary trend (Bullish/Bearish/Ranging).
        2. **Indicator Analysis**: Interpret RSI, MACD, and Bollinger Bands.
        3. **Signal & Setup**:
           - Provide a clear signal: **STRONG BUY**, **BUY**, **NEUTRAL**, **SELL**, or **STRONG SELL**.
           - Define precise entry zone.
           - Define 2 Take Profit targets (Conservative & Aggressive).
           - Define a Stop Loss level.
        4. **Risk Management**: Suggest appropriate leverage.

        **Output Language**: Persian (Farsi).
        **Tone**: Professional, confident, and structured. Use emojis.
        """

        last_error = ""

        for m_name in model_candidates:
            # Simple Retry Logic for each model (3 attempts)
            for attempt in range(3):
                try:
                    model = genai.GenerativeModel(m_name)
                    response = model.generate_content(prompt)
                    return response.text

                except Exception as e:
                    error_str = str(e).lower()
                    last_error = str(e)

                    # Case 1: Model Not Found (404) -> Break inner loop, try next model
                    if "404" in error_str or "not found" in error_str:
                        break

                    # Case 2: Rate Limit / Quota Exceeded (429) -> Wait and Retry same model
                    elif "429" in error_str or "quota" in error_str:
                        # Extract wait time if available, else default backoff
                        wait_time = 10 * (attempt + 1) # 10s, 20s, 30s
                        if "retry in" in error_str:
                            try:
                                # Regex to find something like "39.87s"
                                match = re.search(r'retry in (\d+(\.\d+)?)s', error_str)
                                if match:
                                    wait_time = float(match.group(1)) + 1 # Add 1s buffer
                            except:
                                pass

                        # Only sleep if it's not the last attempt
                        if attempt < 2:
                            time.sleep(wait_time)
                            continue # Retry the loop
                        else:
                            # If failed 3 times, move to next model (maybe a cheaper/different one works?)
                            break

                    # Case 3: Other errors -> Break and try next model
                    else:
                        break

        # If all models failed
        return f"⚠️ خطا در اتصال به هوش مصنوعی (All models failed).\n\nLast Error: {last_error}\n\n*پیشنهاد: لطفاً ۱ دقیقه صبر کنید و دوباره تلاش کنید (محدودیت رایگان گوگل).* "

    except Exception as e:
        return f"Error connecting to AI: {str(e)}\n\n*Hint: Check your API Key.*"
