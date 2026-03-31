from google import genai
import os
try:
    from src import config
except ImportError:
    import config

class AIAgent:
    def __init__(self):
        self.enabled = False
        if config.GEMINI_API_KEY and config.GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
            try:
                # Initialize client
                self.client = genai.Client(api_key=config.GEMINI_API_KEY)
                self.enabled = True
            except Exception as e:
                print(f"Error configuring Gemini: {e}")
        else:
            print("Warning: GEMINI_API_KEY not set. AI analysis disabled.")

    def get_analysis(self, symbol, price, indicators, signal):
        """
        Generates a short analysis using Gemini via the new google-genai SDK.
        """
        if not self.enabled:
            return "AI Analysis Unavailable (API Key missing)."

        # Format prompt
        rsi = indicators.get('RSI', 'N/A')
        if isinstance(rsi, (int, float)): rsi = f"{rsi:.2f}"

        macd = indicators.get('MACD', 'N/A')
        if isinstance(macd, (int, float)): macd = f"{macd:.2f}"

        macd_signal = indicators.get('MACD_Signal', 'N/A')
        if isinstance(macd_signal, (int, float)): macd_signal = f"{macd_signal:.2f}"

        ema_short = indicators.get('EMA_Short', 'N/A')
        if isinstance(ema_short, (int, float)): ema_short = f"{ema_short:.2f}"

        ema_long = indicators.get('EMA_Long', 'N/A')
        if isinstance(ema_long, (int, float)): ema_long = f"{ema_long:.2f}"

        bb_lower = indicators.get('BB_Lower', 'N/A')
        if isinstance(bb_lower, (int, float)): bb_lower = f"{bb_lower:.2f}"

        bb_upper = indicators.get('BB_Upper', 'N/A')
        if isinstance(bb_upper, (int, float)): bb_upper = f"{bb_upper:.2f}"

        prompt = (
            f"You are a professional financial analyst. Analyze the following market data for {symbol} and provide a concise trading summary (max 3 sentences).\n\n"
            f"**Market Data:**\n"
            f"- Price: {price}\n"
            f"- Signal: {signal}\n"
            f"- RSI: {rsi}\n"
            f"- MACD: {macd} (Signal: {macd_signal})\n"
            f"- EMA Trend: Short ({ema_short}) vs Long ({ema_long})\n"
            f"- Bollinger Bands: Lower ({bb_lower}) / Upper ({bb_upper})\n\n"
            f"**Task:**\n"
            f"1. Confirm or question the technical signal based on the indicators.\n"
            f"2. Identify key resistance/support levels if obvious from BB.\n"
            f"3. Provide a risk assessment (Low/Medium/High).\n\n"
            f"Output format:\n"
            f"**Analysis:** [Your summary]\n"
            f"**Risk:** [Risk Level]"
        )

        try:
            # Using new client syntax
            # Prioritize 'gemini-2.0-flash'
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            return response.text
        except Exception as e:
            # Fallback attempts if the model name is wrong or deprecated
            try:
                print(f"Primary model failed ({e}), trying gemini-1.5-flash...")
                response = self.client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt
                )
                return response.text
            except Exception as e2:
                print(f"Error generating AI analysis: {e2}")
                return "AI Analysis failed due to an error."

# Singleton instance
agent = AIAgent()

def get_ai_summary(symbol, price, indicators, signal):
    return agent.get_analysis(symbol, price, indicators, signal)
