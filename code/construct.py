import heapq

from greedy import prefix_sums, block_sum, added, cost, apply

# Fast version of the greedy construction in greedy.py, also used by GRASP.
#
# WHY: greedy() in greedy.py recomputes the cost of ALL candidates in every
# round. There are about N*(U-L) candidates, and many rounds, so for
# N = 30000 it takes several minutes. This version gives the SAME result
# (tested), but only recomputes what is necessary.
#
# HOW (a "lazy" priority queue / heap):
#   - All candidates are kept in a heap, sorted by their cost q.
#   - q = energy / min(R, profit) can only go UP during the construction,
#     because R (missing profit) only goes down. So a cost stored in the heap
#     is always a LOWER BOUND of the true cost.
#   - Take the top of the heap and recompute its cost with the current R:
#       * if the candidate is no longer legal (it overlaps or touches a
#         block that was added later) -> throw it away
#       * if the cost is unchanged -> it is really the cheapest: choose it
#         (every other candidate has true cost >= stored cost >= this one)
#       * otherwise -> put it back with the new cost and try again
#   - After choosing a candidate, only the two extensions of the block that
#     changed are new candidates. They are added to the heap.
#
# Heap entries: (q, kind, a, side, cand)
#   kind = 0 for a new block, 1 for an extension. Together with a and side
#   this gives the same tie-breaking order as greedy(): new blocks first,
#   ordered by (a, b), then extensions ordered by block, left before right.


_initial_heap = {}   # cache: id(inst) -> (inst, initial heap), see construct()


def is_legal(cand, on, blockset, N):
    """
    The candidate is still legal if the block it extends still exists, and
    the only ON periods in [a-1, b+1] are the periods of that old block.
    """
    old, new = cand
    if old is not None and old not in blockset:
        return False
    allowed = 0 if old is None else old[1] - old[0] + 1
    count = 0
    for i in range(max(1, new[0] - 1), min(N, new[1] + 1) + 1):
        count += on[i]
    return count == allowed


def extensions_of(block, on, N, U):
    """The (at most two) legal extensions of one block, with their sort keys."""
    a, b = block
    result = []
    if b - a + 1 < U:
        if a - 1 >= 1 and (a - 2 < 1 or on[a - 2] == 0):
            result.append(((1, a, 0), (block, (a - 1, b))))
        if b + 1 <= N and (b + 2 > N or on[b + 2] == 0):
            result.append(((1, a, 1), (block, (a, b + 1))))
    return result


def construct(inst, alpha=0.0, rng=None):
    """
    Greedy construction.
      rng = None              -> deterministic greedy (same result as greedy())
      rng given, alpha >= 0   -> GRASP construction: pick a random candidate
                                 from the RCL = { c : q(c) <= (1 + alpha) * q_min }
    Returns a sorted list of blocks, or None if the construction gets stuck.
    """
    N, L, U, T = inst["N"], inst["L"], inst["U"], inst["T"]
    if T <= 0:
        return []                    # nothing to reach: keep the machine OFF
    SP = prefix_sums(inst["P"])
    SE = prefix_sums(inst["E"])

    on = [0] * (N + 2)
    blocks = []
    blockset = set()
    profit = 0

    # Initial heap: every possible new block with positive profit.
    # It is the same in every GRASP iteration, so it is built only once per
    # instance and copied afterwards (a copy of a heap is still a heap).
    key = id(inst)
    if key not in _initial_heap:
        _initial_heap.clear()
        heap = []
        for a in range(1, N - L + 2):
            for b in range(a + L - 1, min(N, a + U - 1) + 1):
                cand = (None, (a, b))
                q = cost(cand, SP, SE, T)
                if q is not None:
                    heap.append((q, 0, a, b, cand))
        heapq.heapify(heap)
        _initial_heap[key] = (inst, heap)   # keep inst so its id stays unique
    heap = list(_initial_heap[key][1])

    def pop_cheapest(R):
        """Pop and return the truly cheapest legal entry, or None if none."""
        while heap:
            q, k, a, s, cand = heapq.heappop(heap)
            if not is_legal(cand, on, blockset, N):
                continue
            q_now = cost(cand, SP, SE, R)
            if q_now == q:
                return (q, k, a, s, cand)
            heapq.heappush(heap, (q_now, k, a, s, cand))
        return None

    while profit < T:
        R = T - profit

        best = pop_cheapest(R)
        if best is None:
            return None              # no legal candidate left: stuck

        if rng is None:
            chosen = best[4]
        else:
            # Build the RCL: all legal candidates with q <= threshold.
            # Entries with a stored cost above the threshold cannot be in it
            # (their true cost is even higher), so we stop there.
            threshold = (1 + alpha) * best[0]
            rcl = [best]
            while heap and heap[0][0] <= threshold:
                q, k, a, s, cand = heapq.heappop(heap)
                if not is_legal(cand, on, blockset, N):
                    continue
                q_now = cost(cand, SP, SE, R)
                if q_now <= threshold:
                    rcl.append((q_now, k, a, s, cand))
                else:
                    heapq.heappush(heap, (q_now, k, a, s, cand))
            chosen_entry = rng.choice(rcl)
            # The ones not chosen go back into the heap
            for entry in rcl:
                if entry is not chosen_entry:
                    heapq.heappush(heap, entry)
            chosen = chosen_entry[4]

        # Apply the chosen candidate
        old, new = chosen
        profit += added(SP, chosen)
        blocks = apply(blocks, chosen)
        if old is not None:
            blockset.discard(old)
        blockset.add(new)
        for i in range(new[0], new[1] + 1):
            on[i] = 1

        # The changed block can now be extended: add those candidates
        for (k, a, s), cand in extensions_of(new, on, N, U):
            q = cost(cand, SP, SE, T - profit if profit < T else 1)
            if q is not None:
                heapq.heappush(heap, (q, k, a, s, cand))

    return sorted(blocks)
