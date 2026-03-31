import pandas as pd
import pandas_ta as ta
import numpy as np
try:
    from src import config
except ImportError:
    import config

def calculate_indicators(df):
    """
    Adds technical indicators to the DataFrame.
    """
    if df.empty:
        return df

    # Ensure we have enough data
    if len(df) < 50:
        # Not enough data for EMA50
        return df

    # RSI
    df['RSI'] = df.ta.rsi(length=config.RSI_PERIOD)

    # MACD
    macd = df.ta.macd(fast=config.MACD_FAST, slow=config.MACD_SLOW, signal=config.MACD_SIGNAL)
    if macd is not None:
        # Rename columns to standard names
        # MACD returns: MACD_..., MACDh_... (hist), MACDs_... (signal)
        # Using iloc to be safe: 0=MACD, 1=Hist, 2=Signal
        df['MACD'] = macd.iloc[:, 0]
        df['MACD_hist'] = macd.iloc[:, 1]
        df['MACD_signal'] = macd.iloc[:, 2]

    # EMA
    df['EMA_SHORT'] = df.ta.ema(length=config.EMA_SHORT)
    df['EMA_LONG'] = df.ta.ema(length=config.EMA_LONG)

    # Bollinger Bands
    bb = df.ta.bbands(length=config.BB_PERIOD, std=config.BB_STD)
    if bb is not None:
        # Using iloc to be safe: 0=Lower, 1=Middle, 2=Upper, 3=Bandwidth, 4=Percent
        df['BB_lower'] = bb.iloc[:, 0]
        df['BB_middle'] = bb.iloc[:, 1]
        df['BB_upper'] = bb.iloc[:, 2]

    return df

def analyze_market(df):
    """
    Analyzes the latest data point and returns a signal summary.
    Returns: dict with 'signal', 'strength', 'indicators'
    """
    if df.empty:
        return {"signal": "ERROR", "reason": "No data"}

    # Calculate indicators if not already present
    if 'RSI' not in df.columns:
        df = calculate_indicators(df)

    # Get latest row
    latest = df.iloc[-1]

    # Check if we have NaN values (indicators might need warmup)
    if pd.isna(latest.get('RSI')) or pd.isna(latest.get('MACD')):
        return {"signal": "NEUTRAL", "reason": "Not enough data for indicators"}

    rsi = float(latest['RSI'])
    macd = float(latest['MACD'])
    macd_signal = float(latest['MACD_signal'])
    close = float(latest['Close'])
    bb_lower = float(latest['BB_lower'])
    bb_upper = float(latest['BB_upper'])
    ema_short = float(latest['EMA_SHORT'])
    ema_long = float(latest['EMA_LONG'])

    signals = []
    score = 0 # Positive = Buy, Negative = Sell

    # RSI Analysis
    if rsi < config.RSI_OVERSOLD:
        signals.append(f"RSI Oversold ({rsi:.2f})")
        score += 2
    elif rsi > config.RSI_OVERBOUGHT:
        signals.append(f"RSI Overbought ({rsi:.2f})")
        score -= 2

    # MACD Analysis
    if macd > macd_signal:
        score += 1 # Bullish crossover/trend
    else:
        score -= 1 # Bearish

    # Bollinger Bands
    if close < bb_lower:
        signals.append("Price below Lower BB")
        score += 2
    elif close > bb_upper:
        signals.append("Price above Upper BB")
        score -= 2

    # EMA Trend
    if ema_short > ema_long:
        score += 1 # Golden Cross / Uptrend
    else:
        score -= 1 # Death Cross / Downtrend

    # Determine Final Signal
    final_signal = "NEUTRAL"
    if score >= 3:
        final_signal = "STRONG BUY"
    elif score >= 1:
        final_signal = "BUY"
    elif score <= -3:
        final_signal = "STRONG SELL"
    elif score <= -1:
        final_signal = "SELL"

    return {
        "signal": final_signal,
        "score": score,
        "details": signals,
        "indicators": {
            "RSI": rsi,
            "MACD": macd,
            "MACD_Signal": macd_signal,
            "Close": close,
            "EMA_Short": ema_short,
            "EMA_Long": ema_long,
            "BB_Lower": bb_lower,
            "BB_Upper": bb_upper
        }
    }
