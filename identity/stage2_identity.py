"""The identity (E-002, Q-05): the vendored Stage 2 engine reproduces P-14's and P-16's registered per-path rows, and
U1's start rows for both.

    python identity/stage2_identity.py --paths 4            # both gate identities at 4 paths (minutes)
    python identity/stage2_identity.py --paths 500 --workers 4   # every registered path (the full check)
    python identity/stage2_identity.py --only u1 --u1-starts 4   # U1's start rows at 4 starts a configuration and arm
    python identity/stage2_identity.py --only u1 --u1-starts all # every start (heavy: the run lock)
    python identity/stage2_identity.py --root "<Stage 2>" --log-reads reads.txt   # against Stage 2 itself, listing
                                                                                  #   every file the check opens

**What is compared (the gate rows).** Each registered test's `gate` run at 0 % denial, both shifts (point and the
one-sided 95 % lower bound -- the bound is the verdict arm), on every column of Stage 2's
`zero_edge_decomposition.PATH_COLS` (final cash, fees, payouts, trades, trades sized, accounts funded, attempts
started, realised risk, intended capped risk, deepest loss from start, days to first payout), to 1e-6, for the first
`--paths` paths of the registered paths file:

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

**What is compared (U1, Q-05; bootstrap 4.1 step 6; off unless `--u1-starts`).** Stage 2's user journey (D-620's U1,
`scripts/user_journey.py`) replayed by the vendored code -- nothing of the journey is re-implemented here: each
configuration's inputs by the study's own builder (`user_journey.BUILDERS`: **p14** by D-518's job builder, its table,
budget and seed; **p16** by `rc150_dev_test` with its trades' registered identity, `rc_dev_test.trade_problems`), each
arm's starts by `user_journey.run_job` (the long replay of up to 252 sessions and the exact 21/63/90/126-session runs,
`customer_slices.replay`), the rows by `user_journey.start_rows` with the `reading` column the study inserts -- against
`results/user_journey.csv`'s section `start` for that configuration and arm, read by the vendored `read_result` (its
manifest verified first). **Every column of the file** is compared on every start run: money (`first_payout_cash`,
`spent_before_*`, `net_month_*`, `fees_month_*`, `net_30`) and the ratio `monthly_mean_over_sd` to 1e-6 absolute;
counts and day indices (`start_day`, `observed`, `payouts`, `first_pass`, `first_funded`, `first_payout`) exactly;
dates, day lists and text exactly; every column start rows leave blank must be blank. The arms are those the file's
manifest records (`parameters.arms`: verdict, point). The starts are `--u1-starts` N spread evenly from the first to
the last as `user_journey.py --check --starts N` spreads them (`user_journey.start_choice`), or every start (`all`),
when the file's starts must be reproduced one for one and their count must equal the manifest's `parameters.starts`.
Beside the columns, the study's own refusing checks on the same runs: D-620's declaration (`user_journey.declaration_
problems`), the builders' identity rows, and every run's payouts and fees against the engine's own totals.

Exit 0 when every part run holds; 3 when one is refused (the differing columns printed). Nothing is written except
`--log-reads`. The process's peak memory is printed last (Windows: `GetProcessMemoryInfo`).
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve().parent.parent
DEFAULT_ROOT = HERE / "vendor" / "stage2"
P16_SEED = 20261206        # P-16's registered campaign seed (Stage 2 scripts/rc150_dev_test.py SEED; checked below)
P16_PATHS = "rc_s150_all_gate_paths.csv"

#: U1 (Q-05): the file, the configurations, and the start section's columns by how each is compared
U1_FILE = "user_journey.csv"
U1_CONFIGS = ("p14", "p16")
U1_TEXT = ("section", "reading", "config", "arm", "label", "cell", "start_date", "pass_days", "funded_days", "pay_days",
           "exact_runs_differing")
U1_COUNTS = ("start_day", "observed", "payouts", "first_pass", "first_funded", "first_payout")
U1_MONEY = ("first_payout_cash", "spent_before_first_pass", "spent_before_first_payout",
            *[f"net_month_{k}" for k in range(1, 13)], *[f"fees_month_{k}" for k in range(1, 13)], "net_30")
U1_RATIO = ("monthly_mean_over_sd",)
U1_TOL = 1e-6


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


# ------------------------------------------------------------------------------------------------ U1 (Q-05)


def _blank(v: Any) -> bool:
    return v is None or (isinstance(v, float) and math.isnan(v)) or (isinstance(v, str) and v.strip() == "")


def _number(v: Any) -> float:
    if isinstance(v, bool):
        raise ValueError(f"a flag {v!r} where a number belongs")
    return float(v)


def _as_text(v: Any) -> str:
    """A cell as text: blank as "", a whole number (a day list of one day the reader parsed) as its digits."""
    if _blank(v):
        return ""
    if isinstance(v, str):
        return v.strip()
    try:
        f = _number(v)
    except (TypeError, ValueError):
        return str(v).strip()
    return str(int(f)) if f.is_integer() else repr(f)


def _same(kind: str, a: Any, b: Any) -> bool:
    if kind == "text":
        return _as_text(a) == _as_text(b)
    if _blank(a) or _blank(b):
        return _blank(a) and _blank(b)
    try:
        x, y = _number(a), _number(b)
    except (TypeError, ValueError):
        return False
    if kind == "count":
        return x.is_integer() and y.is_integer() and int(x) == int(y)
    return abs(x - y) <= U1_TOL                      # money and the ratio


def _kind(col: str) -> str:
    if col in U1_COUNTS:
        return "count"
    if col in U1_MONEY or col in U1_RATIO:
        return "money"
    return "text"                                    # U1_TEXT, and every column start rows leave blank


def u1_compare(ours: Sequence[dict], ref: Sequence[dict], columns: Sequence[str], what: str, *,
               all_starts: bool) -> list[str]:
    """Our start rows of one configuration and arm against the file's, start for start, on every column of the file:
    the differing columns (how many starts, the first one's two values). `all_starts`: the file's starts must all be
    reproduced."""
    by: dict[int, dict] = {}
    for r in ref:
        d = int(_number(r.get("start_day")))
        if d in by:
            return [f"{what}: start {d} twice in the file"]
        by[d] = r
    mine = {int(_number(r["start_day"])): r for r in ours}
    if len(mine) != len(ours):
        return [f"{what}: a start twice in our rows"]
    out = []
    extra = sorted({k for r in ours for k in r} - set(columns))
    if extra:
        out.append(f"{what}: our rows hold columns not in the file's columns: {extra}")
    missing = sorted(set(mine) - set(by))
    if missing:
        out.append(f"{what}: {len(missing)} of our starts not in the file (first: start {missing[0]})")
    if all_starts and set(by) - set(mine):
        out.append(f"{what}: {len(set(by) - set(mine))} of the file's {len(by)} starts not reproduced")
    common = sorted(set(mine) & set(by))
    for c in columns:
        k = _kind(c)
        bad = [s for s in common if not _same(k, mine[s].get(c), by[s].get(c))]
        if bad:
            s = bad[0]
            out.append(f"{what} {c}: {len(bad)} of {len(common)} starts differ (first: start {s}: "
                       f"{mine[s].get(c)!r} against the file's {by[s].get(c)!r})")
    return out


def u1_problems(starts: int | None, workers: int) -> dict[str, dict[str, Any]]:
    """U1's start rows for P-14 and P-16 reproduced: {config: {"problems", "starts", "of", "seconds"}} (a key "u1"
    when the declaration or the reference itself is refused)."""
    import gc

    import user_journey as UJ                       # the vendored scripts/user_journey.py

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_manifest, read_result
    from propedge.research import user_journey as U

    rd = RESULTS_DIR
    decl = U.declaration()
    bad = U.declaration_problems(decl)
    if bad:
        return {"u1": {"problems": ["the vendored build is not D-620's declaration -- " + "; ".join(bad[:4])]}}
    path = rd / U1_FILE
    man = read_manifest(path)
    ref = read_result(path)                          # the manifest verified first (ValueError otherwise)
    arms = tuple(man.parameters["arms"])
    if set(arms) != set(UJ.ARMS) or len(arms) != len(UJ.ARMS):
        return {"u1": {"problems": [f"the file's arms {arms} are not the study's {UJ.ARMS}"]}}
    columns = list(man.columns)
    if list(ref.columns) != columns:
        return {"u1": {"problems": ["the file's columns are not its manifest's"]}}
    recorded = man.parameters["starts"]
    st = ref[(ref["section"] == "start") & ref["config"].isin(U1_CONFIGS)].copy()
    del ref
    gc.collect()
    defs = {c["config"]: c for c in UJ.CONFIG_DEFS}
    out: dict[str, dict[str, Any]] = {}
    for name in U1_CONFIGS:
        t0 = time.time()
        c = defs[name]
        print(f"U1 {name}: the inputs (user_journey.BUILDERS[{c['group']!r}])...", flush=True)
        jobs, idents = UJ.BUILDERS[c["group"]](rd, [name])
        probs = [f"{name}: the study's identity fails: {r['check'][:120]} -- {r['problems']}" for r in idents
                 if not r["holds"] and r["refuses"]]
        ran, of = 0, 0
        for arm in UJ.ARMS:
            job = jobs[name][arm]
            of = len(job["blocks"])
            want = int(recorded[f"{name}|{arm}"])
            if of != want:
                probs.append(f"{name} {arm}: the window holds {of} starts, the file's manifest records {want}")
            t1 = time.time()
            v = UJ.run_job(job, name, arm, starts, workers)
            outs = v["starts"]
            ran = len(outs)
            if starts is not None and [x["rec"]["start_day"] for x in outs] != UJ.start_choice(of, starts):
                probs.append(f"{name} {arm}: the starts run are not user_journey.start_choice's")
            for k in ("pay", "cash", "fee"):
                n = int(sum(x[f"{k}_bad"] for x in outs))
                if n:
                    probs.append(f"{name} {arm}: {n} runs' {k} check against the engine's totals fails")
            mine = [{**r, "reading": U.READING} for r in UJ.start_rows(c, arm, outs)]
            theirs = st[(st["config"] == name) & (st["arm"] == arm)].to_dict("records")
            if len(theirs) != want:
                probs.append(f"{name} {arm}: the file holds {len(theirs)} start rows, its manifest records {want}")
            probs += u1_compare(mine, theirs, columns, f"{name} {arm}", all_starts=starts is None)
            print(f"  U1 {name} {arm}: {ran} of {of} starts replayed and compared in {time.time() - t1:.0f} s",
                  flush=True)
        del jobs
        gc.collect()
        out[name] = {"problems": probs, "starts": ran, "of": of, "seconds": time.time() - t0, "columns": len(columns),
                     "arms": arms}
    return out


def peak_memory() -> str | None:
    """This process's peak working set and peak private commit (Windows `GetProcessMemoryInfo`), else None."""
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]

        k32 = ctypes.windll.kernel32
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        fn = ctypes.windll.psapi.GetProcessMemoryInfo
        fn.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
        m = PMC()
        m.cb = ctypes.sizeof(PMC)
        if not fn(k32.GetCurrentProcess(), ctypes.byref(m), m.cb):
            return None
        return (f"peak working set {m.PeakWorkingSetSize / 2**30:.2f} GB, peak private commit "
                f"{m.PeakPagefileUsage / 2**30:.2f} GB (this process, GetProcessMemoryInfo)")
    except Exception:                                # noqa: BLE001 -- a measurement, never a failure
        return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="the Stage 2 tree (default: vendor/stage2)")
    ap.add_argument("--paths", type=int, default=4)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--only", choices=("p14", "p16", "u1"), default=None)
    ap.add_argument("--u1-starts", default=None, help="U1's start rows at N starts a configuration and arm (spread as "
                    "user_journey.py --check spreads them), or 'all'; off by default")
    ap.add_argument("--log-reads", type=Path, default=None, help="list every file under --root the check opens")
    a = ap.parse_args(argv)
    u1_starts: int | None = None
    if a.u1_starts is not None and a.u1_starts != "all":
        try:
            u1_starts = int(a.u1_starts)
        except ValueError:
            ap.error("--u1-starts takes a whole number or 'all'")
        if u1_starts < 1:
            ap.error("--u1-starts takes a whole number of at least 1, or 'all'")
    if a.only == "u1" and a.u1_starts is None:
        ap.error("--only u1 needs --u1-starts N or all")
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
    if a.u1_starts is not None and a.only in (None, "u1"):
        for name, r in u1_problems(u1_starts, a.workers).items():
            if r["problems"]:
                out = 3
                print(f"REFUSED: U1 {name.upper()}'s start rows are not reproduced"
                      + (f" ({r['seconds']:.0f} s)" if "seconds" in r else "") + " -- " + "; ".join(r["problems"][:12]),
                      flush=True)
            else:
                print(f"identity HOLDS: U1 {name.upper()} = results/{U1_FILE}'s start rows for {name}, arms "
                      f"{' and '.join(r['arms'])}, {r['starts']} of {r['of']} starts each "
                      f"({'every one' if u1_starts is None else 'spread as user_journey.py --check spreads them'}; "
                      f"all {r['columns']} columns: money and the ratio to 1e-6, counts and days exactly, dates and "
                      f"text exactly; {r['seconds']:.0f} s)", flush=True)
    if a.log_reads is not None:
        a.log_reads.write_text("\n".join(sorted(reads)) + "\n", encoding="utf-8")
        print(f"reads: {len(reads)} files listed in {a.log_reads}")
    mem = peak_memory()
    if mem:
        print(mem + ("" if a.workers <= 1 else f"; the pool's {a.workers} workers are processes of their own, not "
                                               "counted"), flush=True)
    return out


if __name__ == "__main__":
    raise SystemExit(main())
