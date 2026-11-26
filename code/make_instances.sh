#!/bin/bash
# Generates the instances used in the experiments (always the same files,
# because the seed is fixed). Run from the project root:
#   bash code/make_instances.sh
set -e
mkdir -p instances

# (c)(iii) + (d): increasing size, same parameters. CPLEX needs from
# about 1 minute (N = 20000) to several minutes (N = 60000+).
for N in 20000 30000 40000 50000 60000 80000 100000; do
  python3 code/file2.py instances/big_$N.dat --n $N --l 10 --u 40 \
    --t-frac 0.5 --e-min 100 --e-max 200 --spread 30 --seed 1
done

# (c)(ii): instances for tuning alpha (different seeds, same size)
for S in 1 2 3 4 5; do
  python3 code/file2.py instances/tune_$S.dat --n 10000 --l 10 --u 40 \
    --t-frac 0.5 --e-min 100 --e-max 200 --spread 30 --seed $((100 + S))
done
