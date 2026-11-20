#!/bin/sh
# Q-193 measurement matrix: slices A and B at n = 2, 3, 4 under --dist loadfile and --dist load.
cd "C:/Users/resni/AppData/Local/stage2-extended-wt/wt-xdist" || exit 1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
A="tests/test_fasttier_lock.py tests/test_heavy_marker_guard.py tests/test_git_hook_verdicts.py tests/test_hooks.py tests/test_install_hooks.py tests/test_run_lock.py tests/test_run_clean.py tests/test_heavy_guard.py"
B="tests/test_cl_build.py tests/test_replay_records.py tests/test_q35_openings.py tests/test_user_spend.py tests/test_family_o_stage_c.py tests/test_family_o_runner.py tests/test_rd01_reading.py tests/test_walker.py tests/test_family_stats.py tests/test_lever_space_firms.py"
for s in A B; do
  eval files=\$$s
  for d in loadfile load; do
    for n in 2 3 4; do
      tag="${s}_n${n}_${d}"
      echo "=== $tag $(date -u +%H:%M:%S)"
      python scripts/xdist_measure.py --out .q193_meas/$tag.json -- python -m pytest -o addopts= -q -m "not slow and not heavy" -p no:cacheprovider -n $n --dist $d $files > .q193_meas/$tag.log 2>&1
      echo "rc=$? $(grep -E 'passed|failed' .q193_meas/$tag.log | tail -1)"
    done
  done
done
echo DONE
