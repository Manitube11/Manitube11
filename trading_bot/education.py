
EDUCATIONAL_CONTENT = {
    "RSI": "Relative Strength Index (RSI) is a momentum indicator that measures the magnitude of recent price changes to evaluate overbought or oversold conditions. Values above 70 indicate overbought (potential sell), while values below 30 indicate oversold (potential buy).",

    "MACD": "Moving Average Convergence Divergence (MACD) is a trend-following momentum indicator that shows the relationship between two moving averages of a security's price. A MACD crossing above the signal line is bullish, while crossing below is bearish.",

    "EMA": "Exponential Moving Average (EMA) is a type of moving average that places a greater weight and significance on the most recent data points. It reacts more significantly to recent price changes than a simple moving average (SMA).",

    "Stop Loss": "A Stop Loss order is an order placed with a broker to buy or sell a specific stock once the stock reaches a certain price. It is designed to limit an investor's loss on a position in a security.",

    "Take Profit": "A Take Profit order is a standing order to sell a security once it reaches a certain level of profit. It allows traders to lock in profits automatically.",

    "Support": "Support is a price level where a downtrend tends to pause due to a concentration of demand (buying interest).",

    "Resistance": "Resistance is a price level where an uptrend tends to pause due to a concentration of supply (selling interest).",

    "Trend": "The general direction in which a market or asset is moving. An uptrend is marked by higher highs and higher lows, while a downtrend is marked by lower highs and lower lows.",

    "Volume": "Volume is the number of shares or contracts traded in a security or an entire market during a given period of time. High volume often validates a trend.",

    "Risk Management": "The process of identifying, analyzing, and accepting or mitigating uncertainty in investment decisions. Essential for long-term survival in trading.",

    "Whale": "A term used to describe individuals or entities that hold large amounts of a cryptocurrency or asset. Whale movements can significantly impact market prices."
}

def get_definition(term):
    """Returns the definition of a term if it exists (case-insensitive)."""
    term = term.upper()
    for key, value in EDUCATIONAL_CONTENT.items():
        if key.upper() == term:
            return f"🎓 **{key}:**\n{value}"

    return "Unknown term. Try: RSI, MACD, EMA, Stop Loss, Whale, etc."

def get_all_topics():
    """Returns a list of all available topics."""
    return ", ".join(EDUCATIONAL_CONTENT.keys())
