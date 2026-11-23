
import random

def random_plan(N, L, U):
    plan = [0] * N
    i = 0
    while i < N:
        if N - i >= L and random.random() < 0.5:
            k = random.randint(L, min(U, N - i))
            for j in range(k):
                plan[i + j] = 1
            i = i + k + 1
        else:
            i = i + 1
    return plan

if __name__ == "__main__":
    for _ in range(5):
        print(random_plan(10, 2, 4))

