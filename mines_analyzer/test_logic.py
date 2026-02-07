import unittest
import sys
import os

# Ensure the parent directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mines_analyzer.logic import calculate_next_safe_probability, calculate_multiplier, MineAnalyzer

class TestMinesLogic(unittest.TestCase):

    def setUp(self):
        self.analyzer = MineAnalyzer()
        # Mock history: Mines often at 0, 1, 2
        self.analyzer.add_game([0, 1, 2])
        self.analyzer.add_game([0, 3, 4])
        self.analyzer.add_game([0, 5, 6])

    def test_calculate_next_safe_probability(self):
        # 1 Mine, 0 revealed -> (24/25) * 100 = 96%
        prob = calculate_next_safe_probability(0, 1)
        self.assertAlmostEqual(prob, 96.0)

        # 3 Mines, 0 revealed -> (22/25) * 100 = 88%
        prob = calculate_next_safe_probability(0, 3)
        self.assertAlmostEqual(prob, 88.0)

    def test_multiplier(self):
        # 1 Mine, 1 revealed. Prob = 0.96. Multiplier ~ 1.03
        mult = calculate_multiplier(1, 1)
        self.assertTrue(1.0 < mult < 1.05)

    def test_heatmap_generation(self):
        heatmap = self.analyzer.calculate_heatmap()
        # 0 is in all 3 games -> Max value (1.0)
        self.assertAlmostEqual(heatmap[0], 1.0)
        # 1 is in 1 game -> 1/3 = 0.33
        self.assertAlmostEqual(heatmap[1], 0.3333333333333333)
        # 24 is never a mine -> 0.0
        self.assertEqual(heatmap[24], 0.0)

    def test_suggest_tile_conservative(self):
        # Conservative should avoid 0 (hotspot)
        suggestion = self.analyzer.suggest_tile([], strategy="conservative")
        self.assertNotEqual(suggestion, 0)
        self.assertTrue(0 <= suggestion < 25)

    def test_suggest_tile_aggressive(self):
        # Aggressive prefers 0 (hotspot).
        # While random, with sufficient weight it should pick 0 often, but let's just ensure it returns a valid index.
        suggestion = self.analyzer.suggest_tile([], strategy="aggressive")
        self.assertTrue(0 <= suggestion < 25)

if __name__ == '__main__':
    unittest.main()
