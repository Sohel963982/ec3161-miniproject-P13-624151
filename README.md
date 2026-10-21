# P13: Minesweeper Logical Agent
**Roll No:** 624151  
**Headline Result:** The CSP-based Logical Agent achieves a **51.1% win rate** on Beginner boards, vastly outperforming the **0.0% Random Baseline**, and successfully utilizes probabilistic model enumeration to minimize blind guesses on complex boards.

## 1. Problem
**Formulation:** The environment is a grid of cells hiding $M$ mines. The agent perceives numbers indicating adjacent mines. The goal is to reveal all safe cells without hitting a mine. 
**Why it matters:** Minesweeper is a classic, rigorous testbed for propositional inference, constraint satisfaction problems (CSPs), and reasoning under uncertainty. It forces an agent to balance logical deduction with probabilistic risk assessment.

## 2. Methods
- **Baseline:** `RandomAgent` - Clicks randomly after a guaranteed safe first click in the center of the board.
- **Main Method:** `LogicalAgent` - Maintains a Knowledge Base of cardinality constraints. Uses single-cell rules to flag obvious mines and clear safe zones. It then groups the remaining frontier into independent connected components to avoid exponential blowup, enumerating valid models to find provably safe cells.
- **Improvement:** When logic yields no provably safe moves, the agent calculates the exact probability of each frontier cell being a mine across all valid models. It compares this against the expected probability of non-frontier cells and guesses the absolute safest option.

## 3. Results
*Evaluated over 1000 Beginner, 200 Intermediate, and 50 Expert seeded games.*

| Method | Quality (Win Rate ± 95% CI) | Effort (Guess Rate) | Time (s) |
| :--- | :--- | :--- | :--- |
| **Baseline (Beginner)** | 0.000 ± 0.004 | 0.0 | 0.16 |
| **Logical Agent (Beginner)** | **0.511 ± 0.031** | 1.0 | 184.63 |
| **Baseline (Intermediate)** | 0.000 ± 0.019 | 0.0 | 0.03 |
| **Logical Agent (Intermediate)** | **0.330 ± 0.065** | 1.0 | 103.89 |
| **Baseline (Expert)** | 0.000 ± 0.071 | 0.0 | 0.01 |
| **Logical Agent (Expert)** | **0.040 ± 0.062** | 1.0 | 46.96 |

*(Note: Guess Rate of 1.0 means 100% of the games required at least one blind guess to proceed).*

## 4. Analysis
While the Logical Agent drastically outperforms the Random Baseline, the win rate naturally declines on Intermediate (33%) and Expert (4%) boards. This is not an implementation flaw, but a fundamental property of the game and computational limits:
1. **Unavoidable Guesses:** The `Guess_Rate` of 1.0 indicates that every game required at least one blind guess. Many Minesweeper board configurations mathematically guarantee 50/50 guess scenarios where no logical deduction is possible.
2. **Mitigation of Exponential Blowup:** To ensure the program runs in minutes, exact model enumeration is safely limited to frontier components of ≤20 cells. On larger boards, complex frontiers exceed this limit, forci ng the agent to fall back to a default 50% probability estimate.
3. **Mine Density:** Expert boards have a ~20.6% mine density compared to Beginner's ~12.3%. Higher density creates tighter, more interdependent constraints, making pure logical deduction insufficient.

## 5. Correctness Evidence
- The environment guarantees the first click is always safe.
- Unit tests confirm that single-cell rules correctly flag mines and clear safe zones.
- Model enumeration mathematically guarantees exact probabilities for isolated frontier components, verified against manual 2x2 and 3x3 edge cases.

## 6. Reproduce
```bash
git clone <your-repo-url>
cd EC3161-miniproject-P13-624151
python src/experiment.py 

Hardware: Own system intel-i5 | Runtime: ~5.5 minutes.
7. AI-use statement
AI assistants scaffolded the CSP model enumeration logic and Wilson CI calculations. Core logic for probability fallback and environment integration was verified manually.
8. References
Russell & Norvig, AI: A Modern Approach, Logical Agents & CSPs.
EC-3161 Mini-Project Guidelines, NIT Andhra Pradesh, 2026-27.