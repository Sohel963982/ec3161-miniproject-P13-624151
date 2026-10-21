# starter/minesweeper.py
"""P13 starter: Minesweeper (beginner 9x9, 10 mines). First click is always safe."""
import random


class Minesweeper:
    def __init__(self, rows=9, cols=9, mines=10, seed=None):
        self.R, self.C, self.M = rows, cols, mines
        self.rng = random.Random(seed)
        self.mines = None
        self.revealed, self.lost = set(), False

    def nbrs(self, r, c):
        return [(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                if (dr or dc) and 0 <= r + dr < self.R and 0 <= c + dc < self.C]

    def _place(self, safe):
        cells = [(r, c) for r in range(self.R) for c in range(self.C) if (r, c) != safe]
        self.mines = set(self.rng.sample(cells, self.M))

    def count(self, r, c):
        return sum(n in self.mines for n in self.nbrs(r, c))

    def reveal(self, r, c):
        """Returns the newly visible {cell: number}; sets self.lost if a mine is hit."""
        if self.mines is None:
            self._place((r, c))
        if (r, c) in self.mines:
            self.lost = True
            return {}
        out, stack = {}, [(r, c)]
        while stack:
            cell = stack.pop()
            if cell in self.revealed:
                continue
            self.revealed.add(cell)
            out[cell] = self.count(*cell)
            if out[cell] == 0:
                stack += [n for n in self.nbrs(*cell) if n not in self.revealed]
        return out

    def won(self):
        return len(self.revealed) == self.R * self.C - self.M


def random_player(game):
    view = {}
    view.update(game.reveal(game.R // 2, game.C // 2))
    while not game.lost and not game.won():
        hidden = [(r, c) for r in range(game.R) for c in range(game.C)
                  if (r, c) not in game.revealed]
        view.update(game.reveal(*game.rng.choice(hidden)))
    return game.won()


if __name__ == "__main__":
    wins = sum(random_player(Minesweeper(seed=s)) for s in range(1000))
    print("random clicking after a safe centre click, 1000 games: wins =", wins)