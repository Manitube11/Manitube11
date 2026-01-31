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
        Returns a dict or None.
        """
        if len(df) < 50: # Not enough data
            return None

        curr = df.iloc[-1]
        prev = df.iloc[-2]

        # --- 1. Trend Filter ---
        # Bullish: Price > EMA 50 > EMA 200
        is_bullish_trend = (curr['Close'] > curr['EMA_50']) and (curr['EMA_50'] > curr['EMA_200'])
        is_bearish_trend = (curr['Close'] < curr['EMA_50']) and (curr['EMA_50'] < curr['EMA_200'])

        signal_type = None
        reasons = []

        # --- 2. Entry Logic (MACD Crossover + RSI + Volume) ---

        # BUY SETUP
        # MACD crosses above Signal Line AND RSI is not Overbought (< 70)
        macd_cross_up = (prev['MACD'] <= prev['Signal_Line']) and (curr['MACD'] > curr['Signal_Line'])

        if is_bullish_trend and macd_cross_up and curr['RSI'] < 70:
            signal_type = "BUY"
            reasons.append("Trend Following (Uptrend)")
            reasons.append("MACD Bullish Cross")
            if curr['Volume'] > curr['Vol_SMA']:
                reasons.append("High Volume Support")

        # SELL SETUP
        # MACD crosses below Signal Line AND RSI is not Oversold (> 30)
        macd_cross_down = (prev['MACD'] >= prev['Signal_Line']) and (curr['MACD'] < curr['Signal_Line'])

        if is_bearish_trend and macd_cross_down and curr['RSI'] > 30:
            signal_type = "SELL"
            reasons.append("Trend Following (Downtrend)")
            reasons.append("MACD Bearish Cross")
            if curr['Volume'] > curr['Vol_SMA']:
                reasons.append("High Volume Support")

        if not signal_type:
            return None

        # --- 3. Risk Management (ATR Based) ---
        atr = curr['ATR']
        entry_price = curr['Close']

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
        if risk_pct < 2:
            risk_level = "Low (کم ریسک)"
        elif risk_pct < 5:
            risk_level = "Medium (متوسط)"
        else:
            risk_level = "High (پر ریسک - احتیاط)"

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
            "Time": pd.Timestamp.now().strftime("%H:%M:%S")
        }

if __name__ == "__main__":
    from data_feed import RealTimeDataFeed
    feed = RealTimeDataFeed()
    df = feed.fetch_history("Bitcoin (BTC)", 200)

    an = MarketAnalyzer()
    df = an.analyze(df)
    sig = an.generate_signal(df, "BTC")
    print("Analyzed Data Tail:")
    print(df[['Close', 'EMA_50', 'MACD', 'ATR']].tail())
    print("\nSignal Check:")
    if sig:
        print(sig)
    else:
        print("No Signal Detected (Current market condition doesn't meet VIP criteria)")
