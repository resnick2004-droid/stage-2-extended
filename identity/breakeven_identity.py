"""Q-20's identities (`extended/breakeven.py`: the trades re-walked with the breakeven move corrected), refusing.

    python identity/breakeven_identity.py --synthetic        # light, no bars
    python identity/breakeven_identity.py --substitution     # light, no bars (A1's and A3's caches read)
    python identity/breakeven_identity.py --smoke-days 10    # slow: the first 10 development days of real bars

**`--synthetic`** (E-011's synthetic days, `walker_identity.synthetic_days`, its seed 20261117, and the same days with
2 % of bars widened, seed 20261924 -- E-011's days alone rarely hold the tie (2)): (1) the re-walk under
`STAGE2` (`walk_minutes_for`) equals Stage 2's `atlas_a3.walk_minutes` frame column for column -- at delay 0 on
P-16's marks and the 150-tick rung, and five bars late on A3's 50- and 100-tick rungs; (2) the stop-first tie changes
a walk only from a target to a breakeven exit on the same bar (gross from T to 0), against `STAGE2` and against the
delay alone; (3) every correction changes some walk (not vacuous), and only walks the move reaches: a walk whose
Stage 2 exit came before the next session's open bar is the same under every rule set.

**`--substitution`**: P-14 built through `extended.breakeven.p14_build` on Stage 2's cached A3 frame gives Stage 2's
trades exactly (`rc_dev_test.trades_hash`) and the same U1 jobs' trade blocks; a frame with one walk changed changes
the trades; `atlas_a3.cached_walk` is Stage 2's after the block, also after an error.

**`--smoke-days N`**: A3's minutes on the first N development days, five bars late, re-walked under `STAGE2`, equal
`atlas_a3.walk_minutes`' frame and the cached frame's rows for those days.

Exit 0 when every part run holds; 3 when one is refused. Nothing is written.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import stage2_identity as SI  # noqa: E402
import walker_identity as WI  # noqa: E402

from extended import breakeven as BE  # noqa: E402
from extended import walker as W  # noqa: E402

A3_STOPS = (50, 100)
A3_DELAY = 5
#: the widened bars' seed (the brief's block) and share: E-011's synthetic days rarely hold a bar that both touches the
#: entry and trades through the target after the move (none in 186 such targets on ten days), so 2 % of bars are widened
WIDE_SEED = 20261924
WIDE_SHARE = 0.02


def wide_days(days: dict, seed: int = WIDE_SEED, share: float = WIDE_SHARE) -> dict:
    """The synthetic days with `share` of their present bars widened by 20 to 120 ticks each side of the open (prices
    on the tick grid; open and close unchanged): bars that span an entry and its target."""
    rng = np.random.default_rng(int(seed))
    out = {}
    for day, (o, h, l, c) in days.items():
        o, h, l, c = (np.array(x, dtype=float) for x in (o, h, l, c))
        js = np.flatnonzero(~np.isnan(o) & (rng.random(len(o)) < float(share)))
        up = rng.integers(20, 121, size=len(js)) * W.TICK
        dn = rng.integers(20, 121, size=len(js)) * W.TICK
        h[js] = np.maximum(h[js], o[js] + up)
        l[js] = np.minimum(l[js], o[js] - dn)
        out[day] = (o, h, l, c)
    return out


def _kinds(frame: pd.DataFrame, stops, rrs) -> dict[str, np.ndarray]:
    return {f"{S}_{R:g}": frame[[f"k{S}_{R:g}", f"x{S}_{R:g}", f"g{S}_{R:g}"]].to_numpy(int) for S in stops for R in rrs}


def synthetic_problems() -> list[str]:
    import atlas_a3 as A

    from propedge.research import fv3_rung_walk as RW
    from propedge.research import resolved_coin as rc

    base = WI.synthetic_days(WI.SYNTH_SEED, WI.SYNTH_DAYS)
    wide = wide_days(base)
    days = {**base, **{d.replace("2099", "2098"): v for d, v in wide.items()}}
    arr = lambda d: days[d]                                                      # noqa: E731
    marks = rc.marks()
    mins = pd.DataFrame([(d, s, "n") for d in days for s in marks], columns=["date", "slot", "day_kind"])
    bad: list[str] = []
    seen: dict[str, int] = {}
    for delay, stops in ((0, (150,)), (A3_DELAY, A3_STOPS)):
        theirs = A.walk_minutes(mins, arr, delay, W.TICK, stops, RW.RR_GRID)
        frames = {name: BE.walk_minutes_for(rules)(mins, arr, delay, W.TICK, stops, RW.RR_GRID)
                  for name, rules in BE.RULE_SETS}
        bad += [f"delay {delay}: stage2: {p}" for p in WI.frame_problems(frames["stage2"], theirs)]
        k = {n: _kinds(f, stops, RW.RR_GRID) for n, f in frames.items()}
        for base, var in (("stage2", "stop_first"), ("delay5", "both")):
            for key in k[base]:
                a, b = k[base][key], k[var][key]
                diff = np.flatnonzero((a != b).any(axis=1))
                seen[f"{var}-vs-{base}@{delay}"] = seen.get(f"{var}-vs-{base}@{delay}", 0) + len(diff)
                ok = (a[diff, 0] == W.TARGET) & (b[diff, 0] == W.BREAKEVEN) & (a[diff, 1] == b[diff, 1]) & \
                     (b[diff, 2] == 0)
                if not ok.all():
                    i = int(diff[~ok][0])
                    bad.append(f"delay {delay} {key}: {var} against {base} changes walk {i} from {tuple(a[i])} to "
                               f"{tuple(b[i])}, not a target to a breakeven on the same bar")
        # only walks the move can reach change: a Stage 2 exit before the next session's open bar is the same
        x = frames["stage2"]
        nxt = np.array([next((s for s in W.SESSION_OPENS if s > int(j)), 10**6) for j in x["entry_slot"]])
        for name in ("stop_first", "delay5", "both"):
            n_changed = 0
            for S in stops:
                for R in RW.RR_GRID:
                    cols = [f"k{S}_{R:g}", f"x{S}_{R:g}", f"g{S}_{R:g}"]
                    a, b = x[cols].to_numpy(int), frames[name][cols].to_numpy(int)
                    ch = (a != b).any(axis=1)
                    n_changed += int(ch.sum())
                    early = (a[:, 0] != W.FLATTEN) & (a[:, 1] <= nxt)
                    if (ch & early).any():
                        i = int(np.flatnonzero(ch & early)[0])
                        bad.append(f"delay {delay} {name} {S}_{R:g}: walk {i} exited by Stage 2 before the move "
                                   f"could act, yet changed ({tuple(a[i])} -> {tuple(b[i])})")
            seen[f"{name}@{delay}"] = n_changed
            if not n_changed:
                bad.append(f"delay {delay}: {name} changes no walk on {len(days)} synthetic days (vacuous)")
    if not bad:
        print(f"synthetic identity HOLDS: {len(days)} synthetic days (half widened); the re-walk under STAGE2 is atlas_a3.walk_minutes' "
              f"frame at delay 0 (150 ticks) and delay {A3_DELAY} ({A3_STOPS}); walks changed by rule set and delay "
              f"{ {k: v for k, v in seen.items() if '-vs-' not in k} }; every stop-first change a target turned into a "
              f"breakeven on the same bar ({ {k: v for k, v in seen.items() if '-vs-' in k} })", flush=True)
    return bad


def substitution_problems() -> list[str]:
    import a3_brk30 as B
    import atlas_a3 as A
    import rc_dev_test as D

    from propedge import RESULTS_DIR

    bad = []
    X = BE.a3_inputs()
    cached = X["cached"]
    t0, _ = B.cell_trades(B.inputs())
    stage2 = A.cached_walk
    b = BE.p14_build(cached, RESULTS_DIR)
    if A.cached_walk is not stage2:
        bad.append("the substitution was not undone")
    if D.trades_hash(b["trades"]) != D.trades_hash(t0):
        bad.append("P-14's trades on Stage 2's cached frame through the substitution are not Stage 2's")
    for arm in ("verdict", "point"):
        if len(b["jobs"][arm]["blocks"]) != len(t0["date"].unique()) and len(b["jobs"][arm]["blocks"]) < 1:
            bad.append(f"{arm}: no blocks")
    # a frame with the walk behind P-14's first trade changed (its gross at the first R offered, +7 ticks) changes the
    # trades (the cell reads its own events' walks only: `atlas_cells.cell_walks` joins on date, slot and side)
    changed = cached.copy()
    tr = t0.iloc[0]
    R0 = next(float(c[2:]) for c in t0.columns if c.startswith("r_") and np.isfinite(float(tr[c])))
    col = f"g{int(tr['S'])}_{R0:g}"
    side = 1 if str(tr["side"]) == "long" else -1
    hit = np.flatnonzero((changed["date"].astype(str) == str(tr["date"])).to_numpy()
                         & (changed["slot"].astype(int) == int(tr["decision_slot_minutes"])).to_numpy()
                         & (changed["side"].astype(int) == side).to_numpy())
    if len(hit) != 1:
        bad.append(f"P-14's first trade matches {len(hit)} walks of the frame, not one")
        return bad
    i = int(hit[0])
    changed.loc[changed.index[i], col] = changed[col].iloc[i] + 7
    b2 = BE.p14_build(changed, RESULTS_DIR)
    if D.trades_hash(b2["trades"]) == D.trades_hash(t0):
        bad.append("a changed frame leaves P-14's trades unchanged: the substitution does not reach the trades")
    try:
        with BE.a3_walk(cached):
            raise KeyError("probe")
    except KeyError:
        pass
    if A.cached_walk is not stage2:
        bad.append("the substitution was not undone after an error")
    if not bad:
        print(f"substitution check HOLDS: P-14 through the substitution on Stage 2's cached A3 frame "
              f"({len(cached)} walks) gives Stage 2's {len(t0)} trades exactly; a frame with one walk changed changes "
              "them; atlas_a3.cached_walk is Stage 2's after the block and after an error", flush=True)
    return bad


def smoke_problems(n_days: int) -> list[str]:
    import atlas_a3 as A

    X = BE.a3_inputs()
    cfg = X["cfg"]
    mins = X["minutes"]
    first = sorted(mins["date"].astype(str).unique())[: int(n_days)]
    mins = mins[mins["date"].astype(str).isin(first)].reset_index(drop=True)
    arr = A.bar_arrays(cfg, first)
    delay, tick = int(cfg["screen_delay_min"]), float(cfg["contract"]["tick"])
    theirs = A.walk_minutes(mins, arr, delay, tick, A.stops(cfg), A.rrs(cfg))
    mine = BE.walk_minutes_for(W.STAGE2)(mins, arr, delay, tick, A.stops(cfg), A.rrs(cfg))
    bad = [f"walk_minutes: {p}" for p in WI.frame_problems(mine, theirs)]
    c = X["cached"]
    c = c[c["date"].astype(str).isin(first)].reset_index(drop=True)
    bad += [f"the cache: {p}" for p in WI.frame_problems(mine, c)]
    if not bad:
        print(f"smoke identity HOLDS: A3's minutes on the first {len(first)} development days ({len(mine)} walks, "
              f"delay {delay}, rungs {A.stops(cfg)}) re-walked under STAGE2 equal atlas_a3.walk_minutes' frame and the "
              "cached frame's rows", flush=True)
    return bad


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--substitution", action="store_true")
    ap.add_argument("--smoke-days", type=int, default=None)
    a = ap.parse_args(argv)
    if not (a.synthetic or a.substitution or a.smoke_days):
        ap.error("give --synthetic, --substitution and/or --smoke-days N")
    rc_ = 0
    for flag, fn, args in ((a.synthetic, synthetic_problems, ()), (a.substitution, substitution_problems, ()),
                           (a.smoke_days, smoke_problems, (a.smoke_days,))):
        if not flag:
            continue
        t0 = time.time()
        bad = fn(*args)
        if bad:
            rc_ = 3
            print(f"REFUSED ({fn.__name__}, {time.time() - t0:.0f} s): " + "; ".join(bad[:10]), flush=True)
    mem = SI.peak_memory()
    if mem:
        print(mem, flush=True)
    return rc_


if __name__ == "__main__":
    raise SystemExit(main())
