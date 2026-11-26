import argparse
import csv
import os
import re
import subprocess
import sys
import time

from instance import read_dat
from greedy import energy, write_sol
from construct import construct
from local_search import local_search
from grasp import grasp

# (d) Comparison: run greedy, greedy + local search and GRASP on every
# instance, read the CPLEX result from logs/<name>.cplex.log, check every
# solution with checker.py, and save everything in results/comparison.csv.
#
# Run from the project root (after code/run_cplex.sh):
#   python3 code/compare.py instances/big_*.dat --alpha 0.01 --time 120
# Solutions: solutions/<name>.<method>.sol

CHECKER = os.path.join("project", "checker.py")


def check(dat, sol):
    """Run the official checker. Returns True if it says OK and exits with 0."""
    result = subprocess.run([sys.executable, CHECKER, dat, sol],
                            capture_output=True, text=True)
    return result.returncode == 0 and "OK" in result.stdout


def cplex_result(name):
    """(energy, seconds, ticks) from the CPLEX log, or Nones if missing."""
    path = os.path.join("logs", name + ".cplex.log")
    if not os.path.exists(path):
        return None, None, None
    text = open(path).read()
    obj = re.search(r"OBJECTIVE: (\S+)", text)
    tot = re.search(r"Total \(root\+branch&cut\) =\s*([\d.]+) sec\. \(([\d.]+) ticks\)",
                    text)
    e = int(round(float(obj.group(1)))) if obj else None
    return (e, float(tot.group(1)) if tot else None,
            float(tot.group(2)) if tot else None)


def save_and_check(dat, name, method, blocks):
    sol = os.path.join("solutions", f"{name}.{method}.sol")
    write_sol(blocks, sol)
    return check(dat, sol)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare CPLEX and heuristics")
    parser.add_argument("instances", nargs="+", help=".dat files")
    parser.add_argument("--alpha", type=float, required=True,
                        help="the alpha chosen in the tuning")
    parser.add_argument("--time", type=float, default=120,
                        help="GRASP time limit in seconds")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--out", default="results/comparison.csv")
    args = parser.parse_args()

    os.makedirs("solutions", exist_ok=True)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    rows = []
    for dat in args.instances:
        inst = read_dat(dat)
        name = os.path.basename(dat).replace(".dat", "")
        cplex_e, cplex_t, cplex_ticks = cplex_result(name)
        row = {"instance": name, "N": inst["N"], "cplex_energy": cplex_e,
               "cplex_time_s": cplex_t, "cplex_ticks": cplex_ticks}

        # Greedy
        start = time.time()
        g = construct(inst)
        row["greedy_time_s"] = round(time.time() - start, 2)
        if g is None:
            row["greedy_energy"] = row["ls_energy"] = None
        else:
            row["greedy_energy"] = energy(inst, g)
            row["greedy_ok"] = save_and_check(dat, name, "greedy", g)

            # Greedy + local search (time includes the greedy)
            start = time.time()
            l = local_search(inst, g)
            row["ls_time_s"] = round(row["greedy_time_s"] + time.time() - start, 2)
            row["ls_energy"] = energy(inst, l)
            row["ls_ok"] = save_and_check(dat, name, "ls", l)

        # GRASP
        start = time.time()
        b, e, it = grasp(inst, args.alpha, args.time, 10**9, args.seed)
        row["grasp_time_s"] = round(time.time() - start, 2)
        row["grasp_iterations"] = it
        row["grasp_energy"] = e
        if b is not None:
            row["grasp_ok"] = save_and_check(dat, name, "grasp", b)

        # Gap to the CPLEX optimum, in percent
        for m in ("greedy", "ls", "grasp"):
            if cplex_e and row.get(m + "_energy") is not None:
                row[m + "_gap_pct"] = round(
                    100 * (row[m + "_energy"] - cplex_e) / cplex_e, 4)

        print(row, flush=True)
        rows.append(row)

    columns = ["instance", "N",
               "cplex_energy", "cplex_time_s", "cplex_ticks",
               "greedy_energy", "greedy_time_s", "greedy_gap_pct", "greedy_ok",
               "ls_energy", "ls_time_s", "ls_gap_pct", "ls_ok",
               "grasp_energy", "grasp_time_s", "grasp_iterations",
               "grasp_gap_pct", "grasp_ok"]
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print("Saved", args.out)
