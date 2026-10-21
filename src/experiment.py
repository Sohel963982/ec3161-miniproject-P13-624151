"""Run experiments for P13: Minesweeper Logical Agent."""
import os, sys, csv, math, time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from env import Minesweeper
from agent import RandomAgent, LogicalAgent

def wilson_ci(p, n, z=1.96):
    if n == 0: return 0.0, 0.0
    denominator = 1 + z ** 2 / n
    centre = p + z ** 2 / (2 * n)
    margin = z * math.sqrt((p * (1 - p) + z ** 2 / (4 * n)) / n)
    return max(0.0, (centre - margin) / denominator), min(1.0, (centre + margin) / denominator)

def run_agent(agent_class, game_config, num_games):
    wins = 0; guesses_needed = 0; start_time = time.time()
    for s in range(num_games):
        game = Minesweeper(rows=game_config['rows'], cols=game_config['cols'], mines=game_config['mines'], seed=s)
        agent = agent_class(seed=s)
        won, needed_guess = agent.play(game)
        if won: wins += 1
        if needed_guess: guesses_needed += 1
    time_taken = time.time() - start_time
    p = wins / num_games; ci = wilson_ci(p, num_games)
    return {'Wins': wins, 'Win_Rate': round(p, 4), 'CI_Lower': round(ci[0], 4), 'CI_Upper': round(ci[1], 4), 'Time_s': round(time_taken, 2), 'Guess_Rate': round(guesses_needed / num_games, 4)}

def main():
    CONFIGS = [
        {"rows": 9, "cols": 9, "mines": 10, "name": "Beginner", "games": 1000},
        {"rows": 16, "cols": 16, "mines": 40, "name": "Intermediate", "games": 200},
        {"rows": 30, "cols": 16, "mines": 99, "name": "Expert", "games": 50}
    ]
    all_results = []
    for cfg in CONFIGS:
        print(f"\n--- Testing {cfg['name']} Board ---")
        print(f"Running Baseline...")
        res_rand = run_agent(RandomAgent, cfg, cfg['games'])
        res_rand['Method'] = f"Baseline (Random) - {cfg['name']}"; res_rand['Games'] = cfg['games']
        all_results.append(res_rand)
        print(f"  Win Rate: {res_rand['Win_Rate']}")

        print(f"Running Logical Agent...")
        res_log = run_agent(LogicalAgent, cfg, cfg['games'])
        res_log['Method'] = f"Logical Agent - {cfg['name']}"; res_log['Games'] = cfg['games']
        all_results.append(res_log)
        print(f"  Win Rate: {res_log['Win_Rate']} | Guess Rate: {res_log['Guess_Rate']}")

    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
    os.makedirs(results_dir, exist_ok=True)
    csv_path = os.path.join(results_dir, 'metrics.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Method', 'Games', 'Wins', 'Win_Rate', 'CI_Lower', 'CI_Upper', 'Time_s', 'Guess_Rate'])
        writer.writeheader(); writer.writerows(all_results)
    print(f"\n✅ Results saved to {csv_path}")

if __name__ == "__main__":
    main()