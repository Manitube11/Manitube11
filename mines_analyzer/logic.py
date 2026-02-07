import random
import math

class MineAnalyzer:
    def __init__(self, history_data=None):
        """
        Initializes the analyzer with a list of past mine locations.
        history_data: List of lists, where each inner list contains indices (0-24) of mines in a game.
        """
        self.history = history_data if history_data else []
        self.grid_size = 5
        self.total_cells = 25

    def add_game(self, mine_indices):
        """Adds a completed game's mine locations to history."""
        self.history.append(mine_indices)

    def get_mine_frequency(self):
        """Calculates how often each tile has been a mine."""
        frequency = {i: 0 for i in range(self.total_cells)}
        for game in self.history:
            for idx in game:
                if 0 <= idx < self.total_cells:
                    frequency[idx] += 1
        return frequency

    def calculate_heatmap(self):
        """
        Returns a normalized heatmap (0.0 to 1.0) where 1.0 is the most frequent mine location.
        """
        freq = self.get_mine_frequency()
        if not self.history:
            return {i: 0.0 for i in range(self.total_cells)}

        max_freq = max(freq.values()) if freq else 1
        return {k: v / max_freq for k, v in freq.items()}

    def suggest_tile(self, revealed_indices, strategy="conservative"):
        """
        Suggests a tile based on the selected strategy.
        Strategies:
        - "conservative": Avoids high-frequency mine spots (Cold spots).
        - "aggressive": Targets high-frequency mine spots (Hot spots).
        - "balanced": Random choice weighted slightly towards safer spots.
        - "pure_random": Completely random.
        """
        available_indices = [i for i in range(self.total_cells) if i not in revealed_indices]

        if not available_indices:
            return None

        if strategy == "pure_random":
            return random.choice(available_indices)

        heatmap = self.calculate_heatmap()

        if strategy == "conservative":
            # Prefer lower heatmap values (safer)
            # Weight = 1 / (heatmap_value + epsilon)
            weights = [1.0 / (heatmap[i] + 0.1) for i in available_indices]
            return random.choices(available_indices, weights=weights, k=1)[0]

        elif strategy == "aggressive":
            # Prefer higher heatmap values (riskier/hot spots)
            # Weight = heatmap_value + epsilon
            weights = [heatmap[i] + 0.1 for i in available_indices]
            return random.choices(available_indices, weights=weights, k=1)[0]

        elif strategy == "balanced":
             # Slight preference for safety but mostly random
            weights = [1.0 / (heatmap[i] + 0.5) for i in available_indices]
            return random.choices(available_indices, weights=weights, k=1)[0]

        return random.choice(available_indices)

# --- Legacy/Helper Functions ---

def calculate_next_safe_probability(revealed_count, mines_count, total_cells=25):
    """Calculates the probability that the next tile picked is safe."""
    if revealed_count >= (total_cells - mines_count):
        return 0.0

    remaining_safe = total_cells - mines_count - revealed_count
    remaining_total = total_cells - revealed_count

    if remaining_total <= 0:
        return 0.0

    return (remaining_safe / remaining_total) * 100

def calculate_multiplier(revealed_count, mines_count, total_cells=25):
    """Calculates theoretical multiplier (RTP 99%)."""
    if revealed_count == 0:
        return 1.00

    probability = 1.0
    for i in range(revealed_count):
        safe_spots = total_cells - mines_count - i
        total_spots = total_cells - i
        probability *= (safe_spots / total_spots)

    if probability == 0:
        return 0.0

    return round(0.99 / probability, 2)
