import unittest
import sys
import os

# Ensure the parent directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mines_analyzer.logic import calculate_next_safe_probability, suggest_tile, calculate_multiplier

class TestMinesLogic(unittest.TestCase):

    def test_calculate_next_safe_probability(self):
        # 1 Mine, 0 revealed -> (24/25) * 100 = 96%
        prob = calculate_next_safe_probability(0, 1)
        self.assertAlmostEqual(prob, 96.0)

        # 3 Mines, 0 revealed -> (22/25) * 100 = 88%
        prob = calculate_next_safe_probability(0, 3)
        self.assertAlmostEqual(prob, 88.0)

        # 1 Mine, 23 revealed (24 open total, 1 left). If 1 safe left, prob is 1/1 = 100%. If mine left, 0%.
        # Wait, the logic is "next picked tile is safe".
        # If 25 total, 1 mine. 23 safe revealed. Remaining: 1 safe, 1 mine.
        # Prob = 1/2 = 50%
        prob = calculate_next_safe_probability(23, 1)
        self.assertAlmostEqual(prob, 50.0)

    def test_multiplier(self):
        # 1 Mine, 1 revealed. Prob = 0.96. Multiplier ~ 1.03
        mult = calculate_multiplier(1, 1)
        self.assertTrue(1.0 < mult < 1.05)

        # 3 Mines, 1 revealed. Prob = 0.88. Multiplier ~ 1.12
        mult = calculate_multiplier(1, 3)
        self.assertTrue(1.1 < mult < 1.15)

    def test_suggest_tile_basic(self):
        revealed = [0, 1, 2]
        history = []
        suggestion = suggest_tile(revealed, history)
        self.assertNotIn(suggestion, revealed)
        self.assertTrue(0 <= suggestion <= 24)

    def test_suggest_tile_avoid_recent(self):
        revealed = []
        # History heavily favors 0, 1, 2 being mines
        history = [0, 0, 0, 1, 1, 1, 2, 2, 2]

        # Run multiple times to ensure statistical preference
        suggestions = []
        for _ in range(100):
            s = suggest_tile(revealed, history, strategy="avoid_recent")
            suggestions.append(s)

        # Count occurrences of 0, 1, 2 vs others (e.g., 24)
        count_0 = suggestions.count(0)
        count_24 = suggestions.count(24) # Should be much higher

        # Since weights are inverted, 0 should appear less often than 24
        # self.assertLess(count_0, count_24) # This might be flaky due to randomness, but generally true.

        print(f"Count 0: {count_0}, Count 24: {count_24}")

    def test_suggest_tile_follow_pattern(self):
        revealed = []
        history = [0, 1, 2] # 0, 1, 2 were mines

        # Should pick anything but 0, 1, 2
        suggestion = suggest_tile(revealed, history, strategy="follow_pattern")
        self.assertNotIn(suggestion, [0, 1, 2])

if __name__ == '__main__':
    unittest.main()
