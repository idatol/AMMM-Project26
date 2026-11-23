import argparse
import random

from file1 import random_plan


def generate_instance(N, L, U, t_frac, e_min, e_max, spread, seed):
    if not 1 <= L <= U <= N:
        raise ValueError("must have 1 <= L <= U <= N")
    if not 0 <= t_frac <= 1:
        raise ValueError("t_frac must be between 0 and 1")
    if not 0 <= e_min <= e_max or e_max == 0:
        raise ValueError("must have 0 <= e_min <= e_max and e_max > 0")
    if spread < 0:
        raise ValueError("spread must be >= 0")

    rng = random.Random(seed)

    # Profit follows energy, plus/minus spread. Small spread = strongly correlated.
    E = [rng.randint(e_min, e_max) for _ in range(N)]
    P = [max(0, e + rng.randint(-spread, spread)) for e in E]

    # T is at most the profit of a valid plan, so the instance is always feasible
    plan = [0] * N
    while sum(plan) == 0:
        plan = random_plan(N, L, U, rng)
    S = sum(P[i] for i in range(N) if plan[i] == 1)

    T = int(t_frac * S)
    return {"N": N, "L": L, "U": U, "T": T, "P": P, "E": E}


def write_dat(instance, path):
    with open(path, "w") as f:
        f.write(f"N = {instance['N']};\n")
        f.write(f"L = {instance['L']};\n")
        f.write(f"U = {instance['U']};\n")
        f.write(f"T = {instance['T']};\n")
        f.write(f"P = [{' '.join(str(v) for v in instance['P'])}];\n")
        f.write(f"E = [{' '.join(str(v) for v in instance['E'])}];\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Random instance generator")
    parser.add_argument("output", help="path of the .dat file to write")
    parser.add_argument("--n", type=int, required=True, help="number of periods")
    parser.add_argument("--l", type=int, help="min block length (default: N/50)")
    parser.add_argument("--u", type=int, help="max block length (default: 3*L)")
    parser.add_argument("--t-frac", type=float, default=0.8,
                        help="T as a fraction of the profit of a random valid plan")
    parser.add_argument("--e-min", type=int, default=50)
    parser.add_argument("--e-max", type=int, default=100)
    parser.add_argument("--spread", type=int, default=20,
                        help="max difference between P[i] and E[i]")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    L = args.l
    if L is None:
        L = max(1, args.n // 50)
        if args.u is not None:
            L = min(L, args.u)
    U = args.u if args.u is not None else min(args.n, 3 * L)

    try:
        inst = generate_instance(args.n, L, U, args.t_frac, args.e_min,
                                 args.e_max, args.spread, args.seed)
    except ValueError as err:
        parser.error(str(err))
    write_dat(inst, args.output)
