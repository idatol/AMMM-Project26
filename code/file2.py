
import random

from file1 import random_plan

def generate_instance(N):
    L = random.randint(1, N // 2)
    U = random.randint(L, N)
    P = [random.randint(1, 10) for _ in range(N)]
    E = [random.randint(1, 10) for _ in range(N)]

    S = 0
    while S == 0:
        plan = random_plan(N, L, U)
        S = sum(P[i] for i in range(N) if plan[i] == 1)

    T = random.randint(S // 2, S)
    return {"N": N, "L": L, "U": U, "T": T, "P": P, "E": E}


def write_dat(instance, path):
    with open(path, "w") as f:
        f.write(f"N = {instance['N']};\n");
        f.write(f"L = {instance['L']};\n");
        f.write(f"U = {instance['U']};\n");
        f.write(f"T = {instance['T']};\n");
        f.write(f"P = [{' '.join(str(v) for v in instance['P'])}];\n");
        f.write(f"E = [{' '.join(str(v) for v in instance['E'])}];\n");

if __name__ == "__main__":
    inst = generate_instance(10)
    print(inst)
    write_dat(inst, "test.dat")