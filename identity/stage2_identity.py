"""The identity (E-002): the vendored Stage 2 engine reproduces P-14's and P-16's registered per-path rows.

    python identity/stage2_identity.py --paths 4            # both identities at 4 paths (minutes)
    python identity/stage2_identity.py --paths 500 --workers 4   # every registered path (the full check)
    python identity/stage2_identity.py --root "<Stage 2>" --log-reads reads.txt   # against Stage 2 itself, listing
                                                                                  #   every file the check opens

**What is compared.** Each registered test's `gate` run at 0 % denial, both shifts (point and the one-sided 95 % lower
bound -- the bound is the verdict arm), on every column of Stage 2's `zero_edge_decomposition.PATH_COLS` (final cash,
fees, payouts, trades, trades sized, accounts funded, attempts started, realised risk, intended capped risk, deepest
loss from start, days to first payout), to 1e-6, for the first `--paths` paths of the registered paths file:

* **P-14** (A3-BRK30-CB20, Stage 2 D-509/D-513): Stage 2's own identity, `rc_screen.identity_problems` -- A3-BRK30's
  trades through P-14's engine call at P-14's campaign seed 20261131 against `results/a3_brk30_cb20_gate_paths.csv`.
* **P-16** (RC150 rc_s150_all_nr, Stage 2 D-544/D-547): the cell built by `rc150_dev_test.build_cells`, its trades'
  content hash checked against the hash P-16 pinned (`rc150_dev_test.TRADES_SHA256`), then the gate run exactly as
  `rc_dev_test.run`'s `go("gate", ...)` makes it -- the era-rule bounds (`atlas_a3.bounds`, independent of N), the
  no-closure table, 20 purchases in 21 sessions, the strict rule at 5 minutes, the placement off -- at P-16's campaign
  seed 20261206, against `results/rc_s150_all_gate_paths.csv`.

The first n paths of a 500-path run equal the n-path run's paths (each path is seeded on its own; Stage 2's `--check`
modes rely on it). The denial ladder (10/25/50 %) is not drawn: the 0 % paths do not depend on it (P-14's identity
already runs at 0 % only against a run drawn with the ladder).

Exit 0 when both hold; 3 when either is refused (the problems printed). Nothing is written except `--log-reads`.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DEFAULT_ROOT = HERE / "vendor" / "stage2"
P16_SEED = 20261206        # P-16's registered campaign seed (Stage 2 scripts/rc150_dev_test.py SEED; checked below)
P16_PATHS = "rc_s150_all_gate_paths.csv"


def _setup(root: Path) -> None:
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):  # one BLAS thread (Stage 2 D-464 (5))
        os.environ.setdefault(k, "1")
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "scripts"))
    sys.dont_write_bytecode = True


def p14_problems(n: int, workers: int) -> list[str]:
    import rc_screen as S

    I = S.inputs()
    R = S.Runner(I, workers)
    return S.identity_problems(R, n)


def p16_problems(n: int, workers: int) -> list[str]:
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc150_dev_test as P
    import rc_dev_test as D
    import score_fv3_grid as gf
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.campaign import gate
    from propedge.reporting.results import read_result

    sp = P.SPEC
    if int(sp.seed) != P16_SEED:
        return [f"P-16's seed in the vendored script is {sp.seed}, not {P16_SEED}"]
    I, b = sp.build()
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    t = b["cells"][sp.cell]["trades"]
    days = b["days"]
    th = D.trades_hash(t)
    if th != sp.trades_sha256:
        return [f"P-16's trades hash {th} is not the pinned {sp.trades_sha256}"]
    keys = B.rrs(t)
    cap = B.capacity(t, fcfg)
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        return ["the blocks hold a different number of trades"]
    pcfg = fcfg["portfolio"]
    sink: list[dict] = []
    inner = ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])}, sink=sink)
    hook = lt.lever_hook(inner)
    ps._label(inner, "p16_identity")
    kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, hook, seed=P16_SEED, n_paths=int(n),
                       horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=cap, levels=(0.0,), rtp=False,
                       one_at_a_time=C.STRICT_GAP, purchase_budget=C.BUDGET)
    gate.run_gate(kw.pop("blocks"), workers=int(workers), **kw)
    ref = read_result(RESULTS_DIR / P16_PATHS)
    return zd.path_problems(sink, ref, [("p16_identity", s, "gate", s) for s in ("point", "lower_bound")], int(n))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="the Stage 2 tree (default: vendor/stage2)")
    ap.add_argument("--paths", type=int, default=4)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--only", choices=("p14", "p16"), default=None)
    ap.add_argument("--log-reads", type=Path, default=None, help="list every file under --root the check opens")
    a = ap.parse_args(argv)
    root = a.root.resolve()
    if not (root / "propedge").is_dir():
        print(f"REFUSED: {root} holds no Stage 2 engine (run scripts/vendor_stage2.py first)")
        return 3
    if not (root / "data" / "bars").is_dir() or not (root / "data" / "atlas").is_dir():
        print(f"REFUSED: {root / 'data'} has no bars or atlas (licensed, never committed; "
              "scripts/vendor_stage2.py --data copies them from Stage 2 and checks their hashes)")
        return 3
    reads: set[str] = set()
    if a.log_reads is not None:
        rs = str(root).lower()

        def audit(event, args):
            if event == "open" and args and isinstance(args[0], (str, os.PathLike)):
                p = os.path.abspath(os.fspath(args[0]))
                if p.lower().startswith(rs):
                    reads.add(os.path.relpath(p, root).replace("\\", "/"))

        sys.addaudithook(audit)
    _setup(root)
    out = 0
    for name, fn in (("p14", p14_problems), ("p16", p16_problems)):
        if a.only and a.only != name:
            continue
        t0 = time.time()
        bad = fn(a.paths, a.workers)
        took = time.time() - t0
        if bad:
            out = 3
            print(f"REFUSED: {name.upper()}'s registered paths are not reproduced ({took:.0f} s) -- " + "; ".join(bad[:8]))
        else:
            print(f"identity HOLDS: {name.upper()} = the first {a.paths} paths of its registered gate run "
                  f"(0 %, point and bound, every PATH_COLS column to 1e-6; {took:.0f} s)", flush=True)
    if a.log_reads is not None:
        a.log_reads.write_text("\n".join(sorted(reads)) + "\n", encoding="utf-8")
        print(f"reads: {len(reads)} files listed in {a.log_reads}")
    return out


if __name__ == "__main__":
    raise SystemExit(main())
