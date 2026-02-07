import random
import math

def calculate_next_safe_probability(revealed_count, mines_count, total_cells=25):
    """
    Calculates the probability that the next tile picked is safe.
    """
    if revealed_count >= (total_cells - mines_count):
        return 0.0

    remaining_safe = total_cells - mines_count - revealed_count
    remaining_total = total_cells - revealed_count

    if remaining_total <= 0:
        return 0.0

    return (remaining_safe / remaining_total) * 100

def calculate_multiplier(revealed_count, mines_count, total_cells=25):
    """
    Calculates the theoretical multiplier based on standard Mines game logic.
    Assumes a 1% house edge (RTP 99%).
    """
    if revealed_count == 0:
        return 1.00

    probability = 1.0
    for i in range(revealed_count):
        safe_spots = total_cells - mines_count - i
        total_spots = total_cells - i
        probability *= (safe_spots / total_spots)

    if probability == 0:
        return 0.0

    # Standard formula: 0.99 / probability
    multiplier = 0.99 / probability
    return round(multiplier, 2)

def suggest_tile(revealed_indices, history_mines, strategy="random", total_cells=25):
    """
    Suggests a tile index (0-24) based on the strategy.

    Args:
        revealed_indices (list): List of indices already revealed in the current round.
        history_mines (list): List of indices that were mines in previous rounds.
        strategy (str): 'random', 'avoid_recent', 'follow_pattern'.

    Returns:
        int: The suggested tile index.
    """
    available_indices = [i for i in range(total_cells) if i not in revealed_indices]

    if not available_indices:
        return None

    if strategy == "random":
        return random.choice(available_indices)

    elif strategy == "avoid_recent":
        # Weight tiles that have appeared in history_mines LESS
        # Count frequency of each tile in history
        counts = {i: 0 for i in available_indices}
        for idx in history_mines:
            if idx in counts:
                counts[idx] += 1

        # Invert weights: Higher count -> Lower weight
        # Add 1 to avoid division by zero
        weights = [1.0 / (counts[i] + 1) for i in available_indices]

        return random.choices(available_indices, weights=weights, k=1)[0]

    elif strategy == "follow_pattern":
        # Gambler's Fallacy: "It happened before, it will happen again" (or reverse)
        # Actually, let's make this "Safe Spots": Suggest tiles that were NOT mines recently.
        # This is effectively the same as "avoid_recent" logic.
        # Let's make "follow_pattern" strictly favor tiles that have NEVER been mines in recent history.

        safe_candidates = [i for i in available_indices if i not in history_mines]

        if safe_candidates:
            return random.choice(safe_candidates)
        else:
            # If all have been mines, fallback to least frequent
            return suggest_tile(revealed_indices, history_mines, strategy="avoid_recent")

    return random.choice(available_indices)
