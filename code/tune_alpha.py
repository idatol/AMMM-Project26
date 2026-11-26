import argparse
import csv
import os
import time

from instance import read_dat
from grasp import grasp

# (c)(ii) Tuning of alpha: run GRASP with every alpha on every tuning
# instance, with the same time limit, and save the best energy found.
#
# Run from the project root:
#   python3 code/tune_alpha.py instances/tune_*.dat --time 60
# Result: results/tuning.csv (one row per instance and alpha)

ALPHAS = [0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tune alpha for GRASP")
    parser.add_argument("instances", nargs="+", help=".dat files")
    parser.add_argument("--time", type=float, default=60,
                        help="time limit per GRASP run in seconds")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--out", default="results/tuning.csv")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["instance", "N", "alpha", "energy", "iterations",
                         "time_s"])
        for path in args.instances:
            inst = read_dat(path)
            name = os.path.basename(path).replace(".dat", "")
            for alpha in ALPHAS:
                start = time.time()
                _, e, it = grasp(inst, alpha, args.time, 10**9, args.seed)
                elapsed = time.time() - start
                writer.writerow([name, inst["N"], alpha, e, it,
                                 f"{elapsed:.1f}"])
                f.flush()
                print(name, "alpha", alpha, "energy", e, "iterations", it,
                      flush=True)
