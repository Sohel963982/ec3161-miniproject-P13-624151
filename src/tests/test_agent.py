"""Unit tests for the Minesweeper Logical Agent."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env import Minesweeper
from agent import RandomAgent, LogicalAgent

def test_first_click_safe():
    for seed in range(100):
        game = Minesweeper(rows=9, cols=9, mines=10, seed=seed)
        game.reveal(4, 4)
        assert not game.lost
    print("First click always safe")

def test_logical_beats_random():
    wins_log = 0; wins_rand = 0
    for seed in range(100):
        g1 = Minesweeper(rows=9, cols=9, mines=10, seed=seed)
        if LogicalAgent(seed=seed).play(g1)[0]: wins_log += 1
        g2 = Minesweeper(rows=9, cols=9, mines=10, seed=seed)
        if RandomAgent(seed=seed).play(g2)[0]: wins_rand += 1
    assert wins_log > wins_rand, f"Logical ({wins_log}) should beat Random ({wins_rand})"
    print(f"Logical ({wins_log}) beats Random ({wins_rand})")

if __name__ == "__main__":
    test_first_click_safe()
    test_logical_beats_random()
    print("All tests passed!")