"""P13 Agents: Random baseline, Logical Agent with CSP inference, and probabilistic guessing."""
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from env import Minesweeper

class RandomAgent:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def play(self, game):
        view = game.reveal(game.R // 2, game.C // 2)
        while not game.lost and not game.won():
            hidden = [(r, c) for r in range(game.R) for c in range(game.C) if (r, c) not in game.revealed]
            if not hidden: break
            view.update(game.reveal(*self.rng.choice(hidden)))
        return game.won(), False

class LogicalAgent:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def play(self, game):
        view = game.reveal(game.R // 2, game.C // 2)
        revealed = dict(view)
        flagged = set()
        needed_guess = False

        while not game.lost and not game.won():
            safe_moves, new_mines = self.infer(revealed, flagged, game.R, game.C)
            flagged.update(new_mines)

            if safe_moves:
                for move in safe_moves:
                    if move not in revealed and move not in flagged:
                        new_view = game.reveal(*move)
                        if game.lost: break
                        revealed.update(new_view)
                continue

            needed_guess = True
            hidden = [(r, c) for r in range(game.R) for c in range(game.C) if (r, c) not in revealed and (r, c) not in flagged]
            if not hidden: break

            frontier_probs = self.get_probabilities(revealed, flagged, game.R, game.C)
            remaining_mines = game.M - len(flagged)
            non_frontier = [c for c in hidden if c not in frontier_probs]

            best_move = None
            min_prob = 1.0
            expected_frontier_mines = sum(frontier_probs.values())
            remaining_for_nf = remaining_mines - expected_frontier_mines

            if non_frontier and remaining_for_nf >= 0:
                nf_prob = remaining_for_nf / len(non_frontier)
                if nf_prob < min_prob:
                    min_prob = nf_prob
                    best_move = self.rng.choice(non_frontier)

            for cell, prob in frontier_probs.items():
                if prob < min_prob:
                    min_prob = prob
                    best_move = cell

            if best_move is None:
                best_move = self.rng.choice(hidden)

            new_view = game.reveal(*best_move)
            if game.lost: break
            revealed.update(new_view)

        return game.won(), needed_guess

    def infer(self, revealed, flagged, R, C):
        safe_moves = set()
        new_mines = set()
        changed = True
        while changed:
            changed = False
            for (r, c), count in revealed.items():
                neighbors = self.nbrs(r, c, R, C)
                hidden_neighbors = [n for n in neighbors if n not in revealed and n not in flagged]
                flagged_neighbors = [n for n in neighbors if n in flagged]
                remaining_mines = count - len(flagged_neighbors)

                if remaining_mines == 0:
                    for n in hidden_neighbors:
                        if n not in safe_moves: safe_moves.add(n); changed = True
                elif remaining_mines == len(hidden_neighbors):
                    for n in hidden_neighbors:
                        if n not in new_mines: new_mines.add(n); changed = True
        return safe_moves, new_mines

    def nbrs(self, r, c, R, C):
        return [(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                if (dr or dc) and 0 <= r + dr < R and 0 <= c + dc < C]

    def get_probabilities(self, revealed, flagged, R, C):
        constraints = []
        variables = set()
        for (r, c), count in revealed.items():
            neighbors = self.nbrs(r, c, R, C)
            hidden = [n for n in neighbors if n not in revealed and n not in flagged]
            flagged_count = sum(1 for n in neighbors if n in flagged)
            req = count - flagged_count
            if not hidden: continue
            h_set = frozenset(hidden)
            constraints.append((h_set, req))
            variables.update(hidden)

        if not variables: return {}

        var_list = list(variables)
        var_to_idx = {v: i for i, v in enumerate(var_list)}
        adj = {i: set() for i in range(len(var_list))}
        for h_set, _ in constraints:
            indices = [var_to_idx[v] for v in h_set]
            for i in indices:
                for j in indices:
                    if i != j: adj[i].add(j)

        visited = set()
        components = []
        for j in range(len(var_list)):
            if j not in visited:
                comp = []
                stack = [j]
                while stack:
                    curr = stack.pop()
                    if curr not in visited:
                        visited.add(curr); comp.append(curr)
                        for nxt in adj[curr]:
                            if nxt not in visited: stack.append(nxt)
                components.append(comp)

        probs = {}
        for comp in components:
            comp_vars = [var_list[i] for i in comp]
            comp_constraints = [(h_set, req) for h_set, req in constraints if any(v in h_set for v in comp_vars)]

            if len(comp_vars) > 20:
                for v in comp_vars: probs[v] = 0.5
                continue

            # FIX: Local index mapping to prevent IndexError
            local_var_to_idx = {v: j for j, v in enumerate(comp_vars)}
            
            valid_models = []
            n = len(comp_vars)
            for i in range(1 << n):
                assignment = [(i >> j) & 1 for j in range(n)]
                valid = True
                for h_set, req in comp_constraints:
                    if sum(assignment[local_var_to_idx[v]] for v in h_set) != req:
                        valid = False; break
                if valid: valid_models.append(assignment)

            if not valid_models:
                for v in comp_vars: probs[v] = 0.5
                continue

            total = len(valid_models)
            for j, v in enumerate(comp_vars):
                probs[v] = sum(m[j] for m in valid_models) / total

        return probs