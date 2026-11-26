#!/bin/bash
# Solves the given instances with CPLEX and saves solution + log, e.g.
#   bash code/run_cplex.sh instances/big_20000.dat instances/big_30000.dat
# Results: solutions/<name>.cplex.sol and logs/<name>.cplex.log
OPLRUN=~/Applications/CPLEX_Studio222/opl/bin/arm64_osx/oplrun
export DYLD_LIBRARY_PATH=$(dirname $OPLRUN)
mkdir -p solutions logs
for dat in "$@"; do
  name=$(basename "$dat" .dat)
  echo "== $name"
  # OPL writes output.sol next to the .mod file, not in the current folder
  rm -f CourseProject/output.sol
  start=$(date +%s)
  $OPLRUN CourseProject/CourseProject.mod "$dat" > logs/$name.cplex.log 2>&1
  echo "wall time: $(( $(date +%s) - start )) s" | tee -a logs/$name.cplex.log
  grep -E "OBJECTIVE|Total \(root" logs/$name.cplex.log
  if [ -f CourseProject/output.sol ]; then
    mv CourseProject/output.sol solutions/$name.cplex.sol
    python3 project/checker.py "$dat" solutions/$name.cplex.sol
  fi
done
