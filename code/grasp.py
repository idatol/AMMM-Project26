import argparse
import random
import sys
import time

from instance import read_dat
from greedy import energy, write_sol
from construct import construct
from local_search import local_search

# GRASP = Greedy Randomized Adaptive Search Procedure.
#
# Repeat until the time (or iteration) limit is reached:
#   1. Construction: like the greedy, but instead of always taking the
#      cheapest candidate, pick a RANDOM one among the "good enough" ones
#      (the Restricted Candidate List, RCL).
#   2. Local search on the constructed solution.
#   3. Keep the best solution seen so far.
#
# RCL (minimization, q = greedy cost from greedy.py):
#   RCL = { c : q(c) <= (1 + alpha) * q_min }
#   alpha = 0    -> only the cheapest candidates (= pure greedy, random ties)
#   alpha = 0.05 -> every candidate at most 5 % more expensive than the best
# We use this relative form instead of q_min + alpha * (q_max - q_min)
# because q_max is huge (a candidate with almost no profit gets an enormous
# q), so even a small alpha would let almost every candidate in. It also lets
# construct.py build the RCL without looking at every candidate.
#
# The construction itself is in construct.py (shared with the greedy).


def grasp(inst, alpha, max_time, max_iters, seed):
    """
    Run GRASP and return (best blocks, best energy, iterations done).
    Stops after max_time seconds or max_iters iterations, whichever is first.
    """
    rng = random.Random(seed)
    best_blocks = None
    best_energy = None
    start = time.time()
    it = 0

    while it < max_iters and time.time() - start < max_time:
        it += 1
        blocks = construct(inst, alpha, rng)
        if blocks is None:
            continue           # this construction got stuck: try again

        blocks = local_search(inst, blocks)
        e = energy(inst, blocks)
        if best_energy is None or e < best_energy:
            best_blocks, best_energy = blocks, e

    return best_blocks, best_energy, it


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GRASP")
    parser.add_argument("input", help="path of the .dat file")
    parser.add_argument("output", help="path of the .sol file to write")
    parser.add_argument("--alpha", type=float, default=0.002)
    parser.add_argument("--time", type=float, default=60,
                        help="time limit in seconds")
    parser.add_argument("--iters", type=int, default=10**9,
                        help="maximum number of iterations")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    inst = read_dat(args.input)
    start = time.time()
    blocks, e, it = grasp(inst, args.alpha, args.time, args.iters, args.seed)

    if blocks is None:
        print("No feasible solution found", file=sys.stderr)
        sys.exit(1)

    write_sol(blocks, args.output)
    print("Energy:", e)
    print("Iterations:", it)
    print(f"Time: {time.time() - start:.3f} s")
