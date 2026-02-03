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

        # Use a model that supports text generation. 'gemini-pro' is standard.
        model = genai.GenerativeModel('gemini-pro')

        # Prepare the data for the prompt.
        # We'll take the last 30 records to keep the prompt size reasonable but informative.
        recent_data = data.tail(30).to_string()

        prompt = f"""
        You are a professional financial trading assistant.
        Analyze the following historical market data for {symbol}.
        The data includes Price (Open, High, Low, Close, Volume) and technical indicators (SMA_50, RSI_14).

        Data (Last 30 records):
        {recent_data}

        Task:
        1. Analyze the current trend based on Price action and moving averages.
        2. Evaluate the RSI levels (Overbought/Oversold).
        3. Provide a clear trading signal: BUY, SELL, or HOLD.
        4. Suggest potential Entry, Take Profit, and Stop Loss levels if applicable.
        5. Provide the output in Persian (Farsi).

        Format your response clearly using bullet points.
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error connecting to AI: {str(e)}"
