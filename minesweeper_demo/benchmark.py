"""Batch experiments using identical board seeds and protected first clicks."""
import argparse
import csv
from pathlib import Path
from time import perf_counter
from minesweeper import DemoSession


def run(games=100, height=8, width=8, mines=10, seed=0):
    rows = []
    for strategy in ("random", "logic"):
        for board_seed in range(seed, seed + games):
            session = DemoSession(height, width, mines, board_seed)
            start = perf_counter()
            while not session.game.finished:
                session.step(strategy)
            rows.append(dict(strategy=strategy, seed=board_seed,
                             height=height, width=width, mines=mines,
                             won=int(session.game.won),
                             revealed=len(session.game.revealed),
                             safe_moves=session.safe_moves, guesses=session.guesses,
                             subset_inferences=session.ai.subset_inferences,
                             seconds=round(perf_counter() - start, 6)))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--height", type=int, default=8)
    parser.add_argument("--width", type=int, default=8)
    parser.add_argument("--mines", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", default="results/draft.csv")
    args = parser.parse_args()
    if args.games < 1:
        parser.error("--games must be positive")
    rows = run(args.games, args.height, args.width, args.mines, args.seed)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    for strategy in ("random", "logic"):
        selected = [r for r in rows if r["strategy"] == strategy]
        print(f"{strategy:6}: {sum(r['won'] for r in selected)}/{args.games} wins; "
              f"mean revealed {sum(r['revealed'] for r in selected)/args.games:.1f}")
    print(f"CSV: {target}")


if __name__ == "__main__":
    main()
