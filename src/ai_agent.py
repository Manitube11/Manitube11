import google.generativeai as genai
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
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.model = self._get_model()
                self.enabled = True
            except Exception as e:
                print(f"Error configuring Gemini: {e}")
        else:
            print("Warning: GEMINI_API_KEY not set. AI analysis disabled.")

    def _get_model(self):
        """
        Attempts to find a valid model, starting with gemini-2.0-flash.
        """
        models_to_try = [
            'gemini-2.0-flash',
            'gemini-2.0-flash-lite',
            'gemini-1.5-flash',
            'gemini-pro'
        ]

        # We can't easily check availability without trying to list models or generate
        # But for now, we'll return the first one and rely on runtime errors or implement a check.
        # Actually, listing models requires API call.
        try:
            available_models = [m.name for m in genai.list_models()]
            # This returns 'models/gemini-pro' etc.
            # We need to map our preferences to available ones.
            for preferred in models_to_try:
                for available in available_models:
                    if preferred in available:
                        print(f"Using AI Model: {available}")
                        return genai.GenerativeModel(available)
        except Exception as e:
            print(f"Error listing models: {e}. Defaulting to gemini-1.5-flash")

        return genai.GenerativeModel('gemini-1.5-flash')

    def get_analysis(self, symbol, price, indicators, signal):
        """
        Generates a short analysis using Gemini.
        """
        if not self.enabled:
            return "AI Analysis Unavailable (API Key missing)."

        # Format prompt
        # Ensure indicators are strings or formatted numbers
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
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating AI analysis: {e}")
            return "AI Analysis failed due to an error."

# Singleton instance
agent = AIAgent()

def get_ai_summary(symbol, price, indicators, signal):
    return agent.get_analysis(symbol, price, indicators, signal)
