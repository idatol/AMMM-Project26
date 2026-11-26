import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Makes the figures for the report and the slides from the CSV files:
#   results/tuning.csv     -> results/tuning.png
#   results/comparison.csv -> results/quality.png, results/time.png
# Run from the project root:  python3 code/make_plots.py

# Colour + marker per method (fixed, so a method looks the same everywhere)
STYLE = {
    "cplex":  ("CPLEX (optimum)", "#2a78d6", "o"),
    "greedy": ("Greedy",          "#eb6834", "s"),
    "ls":     ("Greedy + LS",     "#1baf7a", "^"),
    "grasp":  ("GRASP",           "#eda100", "D"),
}
TEXT = "#52514e"
GRID = "#e4e3df"

plt.rcParams.update({
    "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": TEXT,
    "xtick.color": TEXT, "ytick.color": TEXT, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.8, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False,
    "figure.facecolor": "white", "savefig.dpi": 200,
})


def read(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def num(x):
    return None if x in ("", None) else float(x)


def plot_tuning(rows, out):
    # Relative deviation (%) from the best energy found for that instance,
    # so instances of different size can be averaged.
    best = defaultdict(lambda: float("inf"))
    for r in rows:
        best[r["instance"]] = min(best[r["instance"]], float(r["energy"]))
    dev = defaultdict(list)
    for r in rows:
        b = best[r["instance"]]
        dev[float(r["alpha"])].append(100 * (float(r["energy"]) - b) / b)

    alphas = sorted(dev)
    xs = range(len(alphas))
    fig, ax = plt.subplots(figsize=(6, 3.5))
    for x, a in zip(xs, alphas):        # one light dot per instance
        ax.scatter([x] * len(dev[a]), dev[a], s=14, color="#2a78d6",
                   alpha=0.3, linewidths=0)
    mean = [sum(dev[a]) / len(dev[a]) for a in alphas]
    ax.plot(xs, mean, color="#2a78d6", linewidth=2, marker="o", markersize=7,
            label="mean over instances")
    ax.set_xticks(list(xs), [f"{a:g}" for a in alphas])
    ax.set_xlabel("α")
    ax.set_ylabel("deviation from best found (%)")
    ax.set_title("GRASP: tuning of α", color="#0b0b0b", loc="left")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_lines(rows, methods, key, ylabel, title, out, log=False):
    rows = sorted(rows, key=lambda r: int(r["N"]))
    fig, ax = plt.subplots(figsize=(6, 3.5))
    for m in methods:
        label, color, marker = STYLE[m]
        pts = [(int(r["N"]) / 1000, num(r[f"{m}_{key}"])) for r in rows
               if num(r.get(f"{m}_{key}")) is not None]
        if pts:
            ax.plot(*zip(*pts), color=color, marker=marker, markersize=7,
                    linewidth=2, label=label)
    if log:
        ax.set_yscale("log")
    ax.set_xlabel("instance size N (thousands)")
    ax.set_ylabel(ylabel)
    ax.set_title(title, color="#0b0b0b", loc="left")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


if __name__ == "__main__":
    if os.path.exists("results/tuning.csv"):
        plot_tuning(read("results/tuning.csv"), "results/tuning.png")
        print("Saved results/tuning.png")
    if os.path.exists("results/comparison.csv"):
        rows = read("results/comparison.csv")
        plot_lines(rows, ["greedy", "ls", "grasp"], "gap_pct",
                   "gap to CPLEX optimum (%)", "Solution quality",
                   "results/quality.png")
        plot_lines(rows, ["cplex", "greedy", "ls", "grasp"], "time_s",
                   "time (s, log scale)", "Computation time",
                   "results/time.png", log=True)
        print("Saved results/quality.png and results/time.png")
