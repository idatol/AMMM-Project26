import argparse
import sys

from instance import read_dat

# A block is a tuple (a, b): ON from period a to period b, both included.
# Periods are numbered 1..N, as in the output format.
#
# A solution is a list of blocks. Two blocks must always have at least one
# OFF period between them (the checker does NOT test this, so we must).
#
# A candidate is a tuple (old, new):
#   old = None    -> add the new block
#   old = (a, b)  -> replace the block old by new (old extended by one period)


def prefix_sums(values):
    """
    Return a list S of length N+1 where S[i] = sum of the first i values.
    Example: [1, 9, 1] -> [0, 1, 10, 11]
    """
    S = [0]
    for v in values:
        S.append(S[-1] + v)
    return S


def block_sum(S, a, b):
    """
    Sum over the periods a..b, in O(1).
    Example: S = [0, 1, 10, 11], a = 2, b = 3 -> 10
    """
    return S[b] - S[a - 1]

def new_block_candidates(inst, blocks):
    """
    All (None, (a, b)) such that L <= b-a+1 <= U, b <= N, and there is at
    least one OFF period between (a, b) and every block in blocks.
    Example: N=6, L=2, U=3, blocks=[(1, 2)]
             -> (4,5) (4,6) (5,6)
    """
    N, L, U = inst["N"], inst["L"], inst["U"]

    # on[i] = 1 if period i is ON. Positions 0 and N+1 are always OFF.
    on = [0] * (N + 2)
    for (a, b) in blocks:
        for i in range(a, b + 1):
            on[i] = 1

    candidates = []
    for a in range(1, N - L + 2):
        if on[a - 1] == 1:
            continue

        for b in range(a, min(N, a + U - 1) + 1):
            if on[b] == 1 or on[b + 1] == 1:
                break

            if b - a + 1 >= L:
                candidates.append((None, (a, b)))

    return candidates


def extension_candidates(inst, blocks):
    """
    All ((a, b), (a-1, b)) and ((a, b), (a, b+1)) that are legal: the length
    stays <= U, we stay inside 1..N, and at least one OFF period remains
    towards the other blocks.
    Example: N=6, U=3, blocks=[(1, 2), (4, 5)]
             -> ((4, 5), (4, 6))      (period 3 must stay OFF)
    """
    N, U = inst["N"], inst["U"]
    candidates = []

    blocks = sorted(blocks)
    for i in range(len(blocks)):
        a, b = blocks[i]
        if b - a + 1 == U:
            continue
        if a - 1 >= 1 and (i == 0 or blocks[i - 1][1] < a - 2):
            candidates.append(((a, b), (a - 1, b)))
        if b + 1 <= N and (i == len(blocks) - 1 or blocks[i + 1][0] > b + 2):
            candidates.append(((a, b), (a, b + 1)))

    return candidates


def added(S, cand):
    """Sum of the periods a candidate turns ON (S = prefix sums of P or E)."""
    old, new = cand
    total = block_sum(S, new[0], new[1])
    if old is not None:
        total -= block_sum(S, old[0], old[1])
    return total


def cost(cand, SP, SE, R):
    """
    Greedy cost q = added energy / min(R, added profit), where R > 0 is the
    profit still missing. Lower is better. Return None if added profit is 0.
    Example: added energy 6, added profit 12, R = 10 -> 0.6
    """
    profit = added(SP, cand)
    if profit == 0:
        return None
    return added(SE, cand) / min(R, profit)


def apply(blocks, cand):
    """Return a new list of blocks with the candidate applied."""
    old, new = cand
    return [block for block in blocks if block != old] + [new]


def greedy(inst):
    """Return a list of blocks, or None if the greedy gets stuck before T."""
    T = inst["T"]
    SP = prefix_sums(inst["P"])
    SE = prefix_sums(inst["E"])
    blocks = []
    profit = 0

    while profit < T:
        R = T - profit
        candidates = (new_block_candidates(inst, blocks)
                      + extension_candidates(inst, blocks))

        best = None
        best_cost = None
        for cand in candidates:
                c = cost(cand, SP, SE, R)
                if c is not None and (best is None or c < best_cost):
                    best = cand
                    best_cost = c


        # No usable candidate left: the greedy is stuck
        if best is None:
            return None

        # (Glemmer du profit, blir løkken feil!)
        profit += added(SP, best)
        blocks = apply(blocks, best)

    return sorted(blocks)


def energy(inst, blocks):
    SE = prefix_sums(inst["E"])
    return sum(block_sum(SE, a, b) for (a, b) in blocks)


def write_sol(blocks, path):
    with open(path, "w") as f:
        for (a, b) in blocks:
            f.write(f"{a} {b}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Greedy constructive algorithm")
    parser.add_argument("input", help="path of the .dat file")
    parser.add_argument("output", help="path of the .sol file to write")
    args = parser.parse_args()

    inst = read_dat(args.input)
    blocks = greedy(inst)
    if blocks is None:
        print("No feasible solution found", file=sys.stderr)
        sys.exit(1)

    write_sol(blocks, args.output)
    print("Energy:", energy(inst, blocks))
