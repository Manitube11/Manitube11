import pandas as pd
import numpy as np

class MarketAnalyzer:
    def __init__(self):
        pass

    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0))
        loss = (-delta.where(delta < 0, 0))
        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_atr(self, df, period=14):
        """
        Average True Range (ATR) for Volatility and Stop Loss.
        """
        high = df['High']
        low = df['Low']
        close = df['Close'].shift(1)

        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

    def check_volume_spike(self, curr):
        """Detects Whale Activity (Volume > 2.5x Average)."""
        if pd.isna(curr['Vol_SMA']): return False
        if curr['Volume'] > (curr['Vol_SMA'] * 2.5):
            return True
        return False

    def detect_whale_activity(self, df):
        """
        Scans for abnormal volume surges in the recent candles.
        Returns: Boolean (True if Whale Detected)
        """
        if len(df) < 20: return False
        curr = df.iloc[-1]
        return self.check_volume_spike(curr)

    def analyze(self, df):
        """
        Advanced Technical Analysis (Brain of the Bot).
        """
        df = df.copy()

        # 1. Moving Averages (Trend)
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()

        # 2. Momentum (MACD)
        exp12 = df['Close'].ewm(span=12, adjust=False).mean()
        exp26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp12 - exp26
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # 3. RSI
        df['RSI'] = self.calculate_rsi(df['Close'])

        # 4. Volatility (ATR)
        df['ATR'] = self.calculate_atr(df)

        # 5. Volume Trend (Simple)
        df['Vol_SMA'] = df['Volume'].rolling(window=20).mean()

        return df

    def generate_signal(self, df, symbol):
        """
        Generates a Professional VIP Signal based on analyzed data.
        Returns a dict with 'Type': 'BUY'/'SELL'/'WAIT' and details.
        """
        if len(df) < 50: # Not enough data
            return {
                "Symbol": symbol, "Type": "WAIT", "Reason": "Insufficient Data",
                "Entry": 0, "StopLoss": 0, "TP1": 0, "TP2": 0, "TP3": 0, "RiskLevel": "-", "RSI": 0,
                "Whale": False
            }

        curr = df.iloc[-1]
        prev = df.iloc[-2]

        # --- Whale Check ---
        is_whale = self.check_volume_spike(curr)

        # --- 1. Trend Filter ---
        # Bullish: Price > EMA 50 > EMA 200
        is_bullish_trend = (curr['Close'] > curr['EMA_50']) and (curr['EMA_50'] > curr['EMA_200'])
        is_bearish_trend = (curr['Close'] < curr['EMA_50']) and (curr['EMA_50'] < curr['EMA_200'])

        signal_type = None
        reasons = []
        status_msg = "Market Choppy"

        # --- 2. Entry Logic (MACD Crossover + RSI + Volume) ---

        # BUY SETUP
        # MACD crosses above Signal Line AND RSI is not Overbought (< 70)
        macd_cross_up = (prev['MACD'] <= prev['Signal_Line']) and (curr['MACD'] > curr['Signal_Line'])

        if is_bullish_trend:
            status_msg = "Uptrend (Waiting for Dip/Cross)"
            if macd_cross_up and curr['RSI'] < 70:
                signal_type = "BUY"
                reasons.append("Trend Following (Uptrend)")
                reasons.append("MACD Bullish Cross")

        # SELL SETUP
        # MACD crosses below Signal Line AND RSI is not Oversold (> 30)
        macd_cross_down = (prev['MACD'] >= prev['Signal_Line']) and (curr['MACD'] < curr['Signal_Line'])

        if is_bearish_trend:
            status_msg = "Downtrend (Waiting for Rally/Cross)"
            if macd_cross_down and curr['RSI'] > 30:
                signal_type = "SELL"
                reasons.append("Trend Following (Downtrend)")
                reasons.append("MACD Bearish Cross")

        # --- 3. Extra Confirmations (Whale Alert) ---
        if is_whale:
            if signal_type:
                reasons.append("🐋 WHALE ALERT (Volume Surge)")
            else:
                status_msg += " [🐋 WHALE DETECTED]"

        if signal_type and curr['Volume'] > curr['Vol_SMA']:
             reasons.append("High Volume Support")

        # --- 4. Risk Management (ATR Based) ---
        atr = curr['ATR']
        entry_price = curr['Close']

        if not signal_type:
            return {
                "Symbol": symbol,
                "Type": "WAIT",
                "Entry": entry_price,
                "StopLoss": 0, "TP1": 0, "TP2": 0, "TP3": 0,
                "RiskLevel": "-",
                "Reason": status_msg,
                "RSI": curr['RSI'],
                "Whale": is_whale,
                "Time": pd.Timestamp.now().strftime("%H:%M:%S")
            }

        # Multipliers for SL and TP
        sl_mult = 1.5  # Stop Loss distance (1.5x ATR)
        tp_risk_reward = [1.5, 2.5, 4.0] # Risk/Reward Ratios

        if signal_type == "BUY":
            sl_price = entry_price - (atr * sl_mult)
            risk = entry_price - sl_price
            tp1 = entry_price + (risk * tp_risk_reward[0])
            tp2 = entry_price + (risk * tp_risk_reward[1])
            tp3 = entry_price + (risk * tp_risk_reward[2])

        else: # SELL
            sl_price = entry_price + (atr * sl_mult)
            risk = sl_price - entry_price
            tp1 = entry_price - (risk * tp_risk_reward[0])
            tp2 = entry_price - (risk * tp_risk_reward[1])
            tp3 = entry_price - (risk * tp_risk_reward[2])

        # Risk Level
        risk_pct = (risk / entry_price) * 100
        risk_level = self._get_risk_label(risk_pct)

        return {
            "Symbol": symbol,
            "Type": signal_type,
            "Entry": entry_price,
            "StopLoss": sl_price,
            "TP1": tp1,
            "TP2": tp2,
            "TP3": tp3,
            "RiskLevel": risk_level,
            "Reason": " + ".join(reasons),
            "RSI": curr['RSI'],
            "Whale": is_whale,
            "Time": pd.Timestamp.now().strftime("%H:%M:%S")
        }

if __name__ == "__main__":
    from data_feed import RealTimeDataFeed
    feed = RealTimeDataFeed()
    # Mock data fetch for test
    try:
        df, _ = feed.fetch_history("Bitcoin (BTC)", 200)
        an = MarketAnalyzer()
        df = an.analyze(df)
        sig = an.generate_signal(df, "BTC")
        print("Analyzed Data Tail:")
        print(df[['Close', 'EMA_50', 'MACD', 'ATR', 'Vol_SMA']].tail())
        print(f"\nSignal Check: Whale={sig['Whale']}")
    except:
        pass
