import argparse
import sys
import time

from instance import read_dat
from construct import construct
from greedy import prefix_sums, block_sum, energy, write_sol

# Local search: start from a feasible solution (a list of blocks) and keep
# making small changes ("moves") as long as they lower the energy and the
# profit stays >= T. Stop when no move improves the solution (local optimum).
#
# A move is a tuple (i, j, new):
#   remove the blocks i..j (positions in the sorted list, j = i or j = i+1)
#   and put the block new in their place (new = None means: put nothing back).
#
# The new block must fit in the "gap" that is left after the removal, so that
# there is still at least one OFF period towards the neighbouring blocks.
#
# Neighbourhoods:
#   1. REMOVE   (i, i, None):   remove block i completely
#   2. REPLACE  (i, i, new):    move / shrink / grow block i inside its gap
#   3. MERGE    (i, i+1, new):  replace two neighbouring blocks by one block
#                               anywhere in their common gap
#
# Example why MERGE is needed (project.1): greedy gives (1,2) + (4,5) with
# energy 9. No single block can change without touching the other, but
# merging them into (1,4) gives energy 8, which is optimal.


def gap(inst, blocks, i, j):
    """
    The interval [lo, hi] that is free if blocks i..j are removed.
    One period next to each remaining neighbour must stay OFF.
    """
    lo = blocks[i - 1][1] + 2 if i > 0 else 1
    hi = blocks[j + 1][0] - 2 if j + 1 < len(blocks) else inst["N"]
    return lo, hi


def blocks_in_gap(inst, lo, hi):
    """All legal blocks (a, b) with lo <= a <= b <= hi and L <= length <= U."""
    L, U = inst["L"], inst["U"]
    for a in range(lo, hi - L + 2):
        for b in range(a + L - 1, min(hi, a + U - 1) + 1):
            yield (a, b)


def best_move(inst, blocks, SP, SE, profit):
    """
    Best improvement: look at every move in the three neighbourhoods and
    return the one that lowers the energy the most while keeping
    profit >= T. Returns (move, delta_profit), or (None, 0) if no move
    improves the solution.
    """
    T, L, U = inst["T"], inst["L"], inst["U"]
    best = None
    best_dE = 0         # only accept moves with delta energy < 0
    best_dP = 0

    for i in range(len(blocks)):
        for j in (i, i + 1):
            if j >= len(blocks):
                continue

            # Energy and profit we lose by removing blocks i..j
            old_E = sum(block_sum(SE, a, b) for (a, b) in blocks[i:j + 1])
            old_P = sum(block_sum(SP, a, b) for (a, b) in blocks[i:j + 1])

            # Neighbourhood 1: REMOVE (only for a single block)
            if i == j:
                dE, dP = -old_E, -old_P
                if profit + dP >= T and dE < best_dE:
                    best, best_dE, best_dP = (i, j, None), dE, dP

            # Neighbourhoods 2 and 3: REPLACE / MERGE
            # Try every legal block (a, b) in the gap. This is the same as
            # looping over blocks_in_gap(), but written out with the prefix
            # sums directly, because this is the hottest loop of the program.
            lo, hi = gap(inst, blocks, i, j)
            for a in range(lo, hi - L + 2):
                base_E = SE[a - 1] + old_E    # dE = SE[b] - base_E
                base_P = SP[a - 1] + old_P    # dP = SP[b] - base_P
                for b in range(a + L - 1, min(hi, a + U - 1) + 1):
                    dE = SE[b] - base_E
                    if dE >= best_dE:
                        continue      # not better than what we have: skip fast
                    dP = SP[b] - base_P
                    if profit + dP >= T:
                        best, best_dE, best_dP = (i, j, (a, b)), dE, dP

    return best, best_dP


def apply_move(blocks, move):
    """Return a new sorted list of blocks with the move applied."""
    i, j, new = move
    rest = blocks[:i] + blocks[j + 1:]
    if new is not None:
        rest.append(new)
    return sorted(rest)


def local_search(inst, blocks):
    """
    Improve a feasible solution until no move helps.
    Returns the improved list of blocks.
    """
    SP = prefix_sums(inst["P"])
    SE = prefix_sums(inst["E"])
    blocks = sorted(blocks)
    profit = sum(block_sum(SP, a, b) for (a, b) in blocks)

    while True:
        move, dP = best_move(inst, blocks, SP, SE, profit)
        if move is None:
            return blocks      # local optimum reached
        blocks = apply_move(blocks, move)
        profit += dP


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Greedy + local search")
    parser.add_argument("input", help="path of the .dat file")
    parser.add_argument("output", help="path of the .sol file to write")
    args = parser.parse_args()

    inst = read_dat(args.input)
    start = time.time()

    blocks = construct(inst)
    if blocks is None:
        print("No feasible solution found", file=sys.stderr)
        sys.exit(1)
    greedy_energy = energy(inst, blocks)

    blocks = local_search(inst, blocks)

    write_sol(blocks, args.output)
    print("Greedy energy:", greedy_energy)
    print("Energy:", energy(inst, blocks))
    print(f"Time: {time.time() - start:.3f} s")
