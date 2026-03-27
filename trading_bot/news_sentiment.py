import requests
import xml.etree.ElementTree as ET
import time
import re

class NewsAnalyzer:
    def __init__(self):
        # Public Crypto News RSS Feeds
        self.rss_urls = [
            "https://cointelegraph.com/rss",
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
        ]

        # Simple Sentiment Keywords
        self.bullish_keywords = [
            "bull", "bullish", "record", "high", "growth", "soar", "gain", "profit",
            "up", "etf", "approval", "win", "jump", "rally", "surge", "adoption", "launch"
        ]
        self.bearish_keywords = [
            "bear", "bearish", "crash", "loss", "ban", "regulation", "sec", "lawsuit",
            "down", "drop", "hack", "scam", "fraud", "fear", "sell", "dump", "fall"
        ]

        self.last_fetch_time = 0
        self.cached_sentiment = "Neutral (Waiting...)"
        self.cached_score = 50

    def fetch_sentiment(self):
        """
        Fetches RSS feeds, analyzes titles for sentiment keywords, returns a score (0-100).
        0 = Extreme Fear, 100 = Extreme Greed
        """
        current_time = time.time()
        # Cache for 10 minutes (600 seconds) to avoid spamming
        if current_time - self.last_fetch_time < 600:
            return self.cached_sentiment, self.cached_score

        try:
            total_score = 50
            headlines_analyzed = 0

            for url in self.rss_urls:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        root = ET.fromstring(response.content)
                        # Find all <item> -> <title>
                        for item in root.findall('.//item'):
                            title_elem = item.find('title')
                            if title_elem is not None:
                                title = title_elem.text.lower()
                                score_change = self._analyze_text(title)
                                total_score += score_change
                                headlines_analyzed += 1
                                if headlines_analyzed > 20: break # Limit processing
                except Exception as e:
                    print(f"News Fetch Error ({url}): {e}")
                    continue

            # Normalize Score (0-100)
            total_score = max(0, min(100, total_score))
            self.cached_score = total_score
            self.last_fetch_time = current_time

            # Determine Label
            if total_score >= 75:
                self.cached_sentiment = "Extreme Greed 🤑"
            elif total_score >= 60:
                self.cached_sentiment = "Greed 🟢"
            elif total_score <= 25:
                self.cached_sentiment = "Extreme Fear 😱"
            elif total_score <= 40:
                self.cached_sentiment = "Fear 🔴"
            else:
                self.cached_sentiment = "Neutral 😐"

            return self.cached_sentiment, self.cached_score

        except Exception as e:
            print(f"Sentiment Analysis Error: {e}")
            return "Error (Check Net)", 50

    def _analyze_text(self, text):
        score = 0
        # Check Bullish
        for word in self.bullish_keywords:
            if re.search(r'\b' + re.escape(word) + r'\b', text):
                score += 2 # Stronger weight

        # Check Bearish
        for word in self.bearish_keywords:
            if re.search(r'\b' + re.escape(word) + r'\b', text):
                score -= 2

        return score

if __name__ == "__main__":
    analyzer = NewsAnalyzer()
    print("Fetching Global Sentiment...")
    label, score = analyzer.fetch_sentiment()
    print(f"Sentiment: {label} (Score: {score})")
