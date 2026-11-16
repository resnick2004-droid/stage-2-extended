"""F-03's A0 (family O, `prereg/F-03_opening_timing.md` section 9, A0; 18.1 item 6; the second read's m2-2): the
whole-window identities, after the pin, the infrastructure identities and the family's build, **before run 1** --
under their own identity row, from a clean run under the lock (HEAVY: every development bar, every U1 start, 500 gate
paths). Written by Q-109; **not run by its builder**.

    python identity/family_o_identity.py --row E-NNN                         # HEAVY, the lead's: A0 in full
    python identity/family_o_identity.py --row E-NNN --paths 4 --starts 4    # slow (T-12): items 2-3 at 4 paths/starts
    python identity/family_o_identity.py --check-read --row E-NNN            # the read's authorisation only

**The items** (each refusing; a failure prints its first differences, the failure protocol's first step):

1. **the population builder's P-16 cell** -- `extended.opening_population.build_span` on the choice block and on the
   judged block (the reader's purpose `identity`, the row given), its two spans' P-16 trades concatenated, has P-16's
   pinned content hash (`rc150_dev_test.TRADES_SHA256`, `rc_dev_test.trades_hash`); the coin's grid built from A1's
   choice-block dates and Q-83's judged session list is the grid of A1's whole day table (the coin's digest); and the
   labels at every P-16 mark reproduce the cell's coin-side columns there (each trade's `r_<R>` at every R is its
   offer's `rl_<R>` or `rs_<R>` by the coin); and the bound arm's shift and the day capacity run 1 reads from P-16's
   registered gate file (`extended.opening_population.p16_inputs`: section `edge`'s `e` and `lb_gate`, the manifest's
   `trades_per_day_capacity`) are `atlas_a3.bounds`' and `a3_brk30.capacity`'s on those trades, exactly;
2. **the design with the state always on** -- through `extended.gate.run_gate(funded_account_cls=...)`, P-16's gate
   paths at seed 20261206 (E-004's comparison: every `zero_edge_decomposition.PATH_COLS` column, point and bound, to
   1e-6, `--paths` paths, 500 by default); and through Q-17's adapter with the family's class (Q-76's keyword), P-16's
   U1 start rows `p16`, both arms, every start (`--starts`; E-010's comparison);
3. **the design with W = 0** (the state never on, so the wait alone could move anything): the same two comparisons;
4. **Q-51 HOLDS** (E-044 (3)) cited, not re-run; and Q-17's adapter's outputs with the family's class passed and the
   wait switched off equal the vendored class's bit for bit (apart from the class's name) on every response the class
   can run -- the forfeiture's three with the composed class among them -- at `--starts` starts of P-16's verdict arm.

Nothing is written; nothing but counts, timings and equality is printed. The last line is `EXIT <code>` (0 holds,
3 refused). Its record goes in its own decision row before run 1, carrying E-104's positional token `identity-holds: <id>` with A0's
id (`extended.opening_run.A0_ID`) at the commit it held at, which run 1 refuses without.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VENDOR = ROOT / "vendor" / "stage2"
P16_TRADES_SHA256 = "17bcc29bc0c61296c872eaf04c3d49942649dcddca782836916bebdf29c9635f"
P16_GATE_SEED = 20261206
READ_FILES = ("data/atlas/A1/events.parquet", "data/atlas/A1/days.parquet", "data/bars/NQ/bars.parquet")
RESPONSES_W0 = ("off", "denial_10", "denial_25", "denial_50", "forfeit_10", "forfeit_25", "forfeit_50", "rtp",
                "rtp_w3")


def _setup() -> None:
    for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(k, "1")
    sys.path.insert(0, str(VENDOR))
    sys.path.insert(0, str(VENDOR / "scripts"))
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(HERE))
    sys.dont_write_bytecode = True


def log(msg: str) -> None:
    print(msg, flush=True)


def authorise(row: str) -> None:
    from extended import VENDOR_STAGE2, reader

    reader.authorise_engine_read(reader.CHOICE_START, reader.JUDGED_END, purpose="identity", declaration=row,
                                 files=[VENDOR_STAGE2 / f for f in READ_FILES],
                                 what=f"{row}: F-03's A0 (identity/family_o_identity.py)")


def item1(row: str) -> tuple[list[str], dict]:
    """The population builder's P-16 cell, the coin's grid and the labels (the module docstring, item 1)."""
    import numpy as np
    import pandas as pd

    import rc150_dev_test as P16
    import rc_dev_test as D

    from propedge.research import resolved_coin as rc

    from extended import opening_population as OP
    from extended import reader

    A1 = reader.read_walks("A1", "days", reader.CHOICE_START, reader.JUDGED_END, purpose="identity", declaration=row,
                           columns=["date", "day_kind"], what=f"{row}: A0, A1's whole day table")
    A1 = A1.assign(date=A1["date"].astype(str))
    whole = sorted(A1["date"])
    judged, _ = OP.read_judged_sessions(ROOT / "results")
    built = sorted(set(d for d in whole if d <= str(reader.CHOICE_END)) | set(judged))
    bad = []
    if OP.CoinArray(built, rc.marks(), rc.COIN_SEED).digest() != OP.CoinArray(whole, rc.marks(), rc.COIN_SEED).digest():
        bad.append("the coin's grid from the choice dates and Q-83's list is not A1's whole day table's")
    spans = []
    for lo, hi in ((reader.CHOICE_START, reader.CHOICE_END), (reader.JUDGED_START, reader.JUDGED_END)):
        spans.append(OP.build_span(str(lo), str(hi), whole, purpose="identity", declaration=row, log=log))
        gc_collect()
    t = pd.concat([s.trades for s in spans], ignore_index=True)
    t = t.sort_values(["date", "entry_t"], kind="stable").reset_index(drop=True)
    th = D.trades_hash(t)
    if th != P16.TRADES_SHA256 or P16.TRADES_SHA256 != P16_TRADES_SHA256:
        bad.append(f"the two spans' P-16 trades hash to {th}, not P-16's pinned {P16.TRADES_SHA256}")
    pop = pd.concat([s.population for s in spans], ignore_index=True).set_index(["date", "slot"])
    key = list(zip(t["date"].astype(str), t["decision_slot_minutes"].astype(np.int64)))
    missing = [k for k in key if k not in pop.index]
    if missing:
        bad.append(f"{len(missing)} P-16 trades have no offer in the population or labels (first {missing[0]})")
    else:
        row_ = pop.loc[key]
        coin = row_["coin"].to_numpy()
        want_side = np.where(t["side"].astype(str) == "long", 1, -1)
        if not np.array_equal(coin, want_side):
            bad.append("an offer's registered coin is not the trade's side")
        for R in spans[0].rr_grid:
            k = OP.rkey(R)
            mine = np.where(coin > 0, row_[f"rl_{k}"].to_numpy(float), row_[f"rs_{k}"].to_numpy(float))
            theirs = t[f"r_{k}"].to_numpy(float)
            if not np.array_equal(mine, theirs):
                i = int(np.flatnonzero(mine != theirs)[0])
                bad.append(f"R {k}: the labels' coin side is not the trade's r_{k} (first {key[i]}: {mine[i]!r} "
                           f"against {theirs[i]!r})")
    import a3_brk30 as B
    import atlas_a3 as A

    Pr = OP.p16_inputs()
    _, e_by, lb_by, _, _ = A.bounds(t, whole, B.rrs(t), Pr["cfg"])
    for R in B.rrs(t):
        if (e_by[R], lb_by[R]) != (Pr["e_by"].get(float(R)), Pr["lb_by"].get(float(R))):
            bad.append(f"R {R:g}: the registered shift ({Pr['e_by'].get(float(R))!r}, {Pr['lb_by'].get(float(R))!r}) "
                       f"is not atlas_a3.bounds' ({e_by[R]!r}, {lb_by[R]!r}) on the whole window")
    if int(B.capacity(t, Pr["fcfg"])) != int(Pr["cap"]):
        bad.append(f"the registered capacity {Pr['cap']} is not a3_brk30.capacity's {B.capacity(t, Pr['fcfg'])}")
    log(f"item 1: {len(t)} trades over both spans, hash {th[:16]}; {'HOLDS' if not bad else 'FAILS'}")
    return bad, {"spans": spans, "whole": whole}


def gc_collect() -> None:
    import gc

    gc.collect()


def gate_problems(make_cls, n: int, workers: int, label: str) -> list[str]:
    """P-16's gate call as `identity/gate_identity.py`'s `p16_problems` makes it, through the adapter with the class
    `make_cls(blocks)` gives for the campaign's blocks."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc150_dev_test as P
    import rc_dev_test as D
    import score_fv3_grid as gf
    import stage2_identity as SI
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    from extended import gate as XG

    sp = P.SPEC
    I, b = sp.build()
    L = I["L"]
    fcfg, tv = L["fcfg"], float(L["tv"])
    t = b["cells"][sp.cell]["trades"]
    days = b["days"]
    if D.trades_hash(t) != sp.trades_sha256:
        return ["P-16's trades are not its pinned hash"]
    keys = B.rrs(t)
    cap = B.capacity(t, fcfg)
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, L["cfg"])
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    pcfg = fcfg["portfolio"]
    ref = read_result(RESULTS_DIR / SI.P16_PATHS)
    sink: list[dict] = []
    inner = ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])}, sink=sink)
    hook = lt.lever_hook(inner)
    ps._label(inner, label)
    kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, hook, seed=P16_GATE_SEED, n_paths=int(n),
                       horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=cap, levels=(0.0,), rtp=False,
                       one_at_a_time=C.STRICT_GAP, purchase_budget=C.BUDGET)
    blk = kw.pop("blocks")
    XG.run_gate(blk, workers=int(workers), funded_account_cls=make_cls(blk), **kw)
    return zd.path_problems(sink, ref, [(label, s, "gate", s) for s in ("point", "lower_bound")], int(n))


def u1_problems(make_cls, starts: int | None, workers: int, what: str) -> list[str]:
    """P-16's U1 start rows (both arms) through Q-17's adapter with the class `make_cls(job)` gives."""
    import user_beside_identity as I
    import user_journey as UJ

    from propedge import RESULTS_DIR

    from extended import user_beside as B

    ref = I.u1_reference(Path(RESULTS_DIR), ["p16"])
    jobs, c, probs = I.build(Path(RESULTS_DIR), "p16")
    for arm in UJ.ARMS:
        job = jobs[arm]
        n = len(job["blocks"])
        chosen = UJ.start_choice(n, starts)
        cls = make_cls(job)
        outs = B.run_starts("p16", arm, B.BY_NAME["off"], job, chosen, int(workers), funded_account_cls=cls)
        probs += [f"{what}: {p}" for p in I.u1_compare_outs("p16", c, arm, outs, ref, n, starts)]
    return probs


def item4(starts: int, workers: int) -> list[str]:
    """Q-17's adapter's outputs with the family's class, the wait switched off, equal the vendored class's (every
    response the class can run, the forfeiture's three among them), at `starts` starts of P-16's verdict arm."""
    import numpy as np
    import user_beside_identity as I
    import user_journey as UJ

    from propedge import RESULTS_DIR

    from extended import opening_wait as OW
    from extended import user_beside as B

    jobs, _, probs = I.build(Path(RESULTS_DIR), "p16")
    job = jobs["verdict"]
    chosen = UJ.start_choice(len(job["blocks"]), starts)
    cls = OW.waiting_class(OW.WaitSpec.for_blocks("w0_off", job["blocks"],
                                                  [np.zeros(len(b), bool) for b in job["blocks"]], W=0))
    for name in RESPONSES_W0:
        base = B.run_starts("p16", "verdict", B.BY_NAME[name], job, chosen, int(workers))
        got = B.run_starts("p16", "verdict", B.BY_NAME[name], job, chosen, int(workers), funded_account_cls=cls)
        probs += I.class_outs_problems(base, got, cls, f"item 4 {name}")
    return probs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--row", required=True, help="A0's identity row (E-NNN), naming an identity")
    ap.add_argument("--paths", type=int, default=500)
    ap.add_argument("--starts", type=int, default=None, help="U1 starts (default: every start)")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--check-read", action="store_true")
    a = ap.parse_args(argv)
    _setup()
    from extended import reader

    try:
        authorise(a.row)
    except (reader.ReadRefused, FileNotFoundError, ValueError) as exc:
        log(f"REFUSED: {exc}")
        return 3
    log(f"reader: identity under {a.row} AUTHORISED")
    if a.check_read:
        return 0
    import numpy as np

    from extended import opening_wait as OW

    t0 = time.time()
    bad, _ = item1(a.row)
    bad += [f"item 2 gate: {p}" for p in gate_problems(
        lambda blk: OW.waiting_class(OW.WaitSpec.for_index("a0_always_gate", None)), a.paths, a.workers,
        "fo_a0_always")]
    bad += u1_problems(lambda job: OW.waiting_class(OW.WaitSpec.for_blocks("a0_always", job["blocks"], None)),
                       a.starts, a.workers, "item 2 U1")
    bad += [f"item 3 gate: {p}" for p in gate_problems(
        lambda blk: OW.waiting_class(OW.WaitSpec.for_index("a0_w0_gate", [np.zeros(len(b), bool) for b in blk], W=0)),
        a.paths, a.workers, "fo_a0_w0")]
    bad += u1_problems(lambda job: OW.waiting_class(OW.WaitSpec.for_blocks(
        "a0_w0", job["blocks"], [np.zeros(len(b), bool) for b in job["blocks"]], W=0)), a.starts, a.workers,
        "item 3 U1")
    bad += item4(a.starts or 21, a.workers)
    log("item 4: Q-51 HOLDS is cited (E-044 (3)), not re-run")
    if bad:
        log("A0 FAILS: " + "; ".join(bad[:10]))
        return 3
    log(f"A0 HOLDS: items 1-4 ({time.time() - t0:.0f} s)")
    return 0


if __name__ == "__main__":
    code = main()
    print(f"EXIT {code}", flush=True)
    sys.exit(code)
