"""EXPLORATORY (D-578, D-590): S3's candidate `lnbar1x4_follow` at the operator's latency (D-266: L = 5 minutes) -- the
side at mark t read from bars closed at or before t - 5; everything else S3's (`scripts/s3_event_kinds.py`).

    python scripts/s3_latency.py --check                     # 30 walked days only (the first 15 of each span): the
                                                             #   side identities, the lift's machinery, every guard's
                                                             #   machinery at 4 paths, 2 coins (all four run, none
                                                             #   read); no reading printed; nothing written
    python scripts/s3_latency.py --workers 1                 # the reading (a clean checkout, D-474)

**The declaration** (DECISIONS.md's D-590 row) is pinned by the sha256 of its line and checked phrase by phrase against
this build's constants (`propedge.research.s3_latency.declaration_problems`, the way `p16_slip_stress` pins D-583), with
S3's declaration pin and shared constants (`s3_event_kinds.declaration_problems`, `shared_problems`) and the engine's
constants as S3 checks them; `results/s3_event_kinds.csv` is read through its manifest and its sha256 pinned (the file
D-588 read and D-589 audited). A difference refuses.

**Identities, refusing** (D-590, as S3 checks its own): (a) the cell (`rc_stop_walkforward.cell`, 150 ticks, every
development day) is P-16's -- its count as `rc_width_screen.csv`'s `rc_s150_all`, its content hash
`rc150_dev_test.TRADES_SHA256` -- and the side table set to P-16's coin rebuilds that hash; the both-side walks carry the
cell's offers and settlement (S3's). (b) At L = 0 the latency path's side table for `lnbar1x4` equals S3's own
(`s3_event_kinds.side_table`, every rule, the rule's column) at every (walked day, mark); at L = 5 the side at t equals
the L = 0 side at t - 5 and mark 0 ties; stage 1's statistics at L = 0 equal S3's lift rows for the rule. (c) The L = 0
arm's trades carry S3's `lnbar1x4_follow` `cell_trades_sha256` and count, and its paired G1 run at seed 20261131, 500
paths reproduces that campaign row (growth on required at the bound and point, the required bankroll, the zero-edge
twin; to 1e-9). (d) The reference (P-16's coin) equals S3's `P16_coin` campaign row the same way and, as S3 checks it,
`rc_width_screen.csv`'s `rc_s150_all`; G2's and G3's references equal `rc150_routing.csv`'s R0 rows (S3's identity
(iii)).

**Guards** (D-578 (2), at S3's seeds and path counts, in D-590's order): resolution (every offered R resolves, D-212), G1
(paired growth at the bound above P-16's by more than 0.05), G2 (at least 40 of 50 coin sequences 20261600 + i at 200
paths; a tie takes the sequence's coin), G3 (not below P-16 on 2020-2023 or 2024-2026-07-16 alone). The first failing
guard ends the run; the rest are written `not_run` and the candidate is False.

**Beside, deciding nothing:** stage 1's lift for the rule at the six offered R at L = 5 (S3's bootstrap: seed 20261109,
block 21, 2,000 replicates; the studentised t per R, no family-wise selection); the share of marks whose side changes
from L = 0 (on every walked (day, mark) and on the cell's offers); with G1, the L = 5 arm's journey and its four slice
lines against FV3-C as S3 writes them for an arm.

**Resume** (D-540, `rc_robust.Resume`): each finished engine run kept outside the checkout, keyed by commit and counts;
`--no-resume`, `--resume-dir`; off in --check.

Writes `results/s3_latency.csv` (EXPLORATORY; sections declaration, identity, sides, lift, campaign, journey,
slice_lines, g2, g2_summary, g3, guard, verdict) with its manifest; one variant, `D-578:S3-L5`.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import rc_robust as RR  # noqa: E402
import rc_screen as S  # noqa: E402
import s3_event_kinds as S3X  # noqa: E402  (S3's script: its side table, grid, Resume and identity (iii))
from propedge.research import s3_event_kinds as S3  # noqa: E402
from propedge.research import s3_latency as LT  # noqa: E402

SCRIPT = "scripts/s3_latency.py"
DECISION = LT.DECISION
RESULT = LT.RESULT
FAMILY_ID = LT.FAMILY_ID
CELL = S3X.CELL
STOP = S3.STOP_TICKS
REFERENCE = LT.REFERENCE
CHECK_DAYS = S3X.CHECK_DAYS
BAR_CHUNK = S3X.BAR_CHUNK
ROUTING_FILE = S3X.ROUTING_FILE
ROUTING_REF = S3X.ROUTING_REF
READING = ("EXPLORATORY (D-578, D-590): S3's candidate lnbar1x4_follow at the operator's latency L = 5 (D-266) -- D-578's "
           "four guards against P-16 in the order resolution, G1, G2, G3; the first failure ends the run; selects "
           "nothing by itself")


class Resume(RR.Resume):
    """`rc_robust.Resume` (D-540) under this study's own file name."""

    def __init__(self, folder: Path | None, key: str):
        import json

        self.path = None if folder is None else Path(folder) / f"{RESULT}_{key}.jsonl"
        self.rows = {}
        if self.path is not None and self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    self.rows[r["_label"]] = r["row"]
            print(f"  resume: {len(self.rows)} finished run(s) read from {self.path}", flush=True)


_cached = RR._cached


# ------------------------------------------------------------------------------------------------ the sides


def lag_side_table(cfg: dict, side_days: list[str], marks: list[int], latencies: tuple[int, ...]
                   ) -> dict[int, dict[str, np.ndarray]]:
    """{L: {date: (marks,) int8 sides of the rule at latency L}} on `side_days` from the development bars (the window
    guard first), each day's arrays as the walk reads them (`atlas_local.day_arrays`) and S3's chunks of store days;
    each side `s3_latency.lagged_day_sides` (S3's `day_sides` at t - L). A walked day with no bars ties at every mark."""
    from propedge.data.bars import read_bars, trading_days
    from propedge.research import atlas_local

    store = [str(d) for d in trading_days(cfg["market"])]
    pos = {d: i for i, d in enumerate(store)}
    want = sorted(set(side_days))
    missing = [d for d in want if d not in pos]
    if missing:
        raise SystemExit(f"REFUSED ({DECISION}): {len(missing)} walked day(s) not in the bar store, e.g. {missing[:3]}")
    out: dict[int, dict[str, np.ndarray]] = {int(L): {} for L in latencies}
    runs: list[list[int]] = []
    for i in sorted(pos[d] for d in want):
        if runs and i == runs[-1][-1] + 1 and len(runs[-1]) < BAR_CHUNK:
            runs[-1].append(i)
        else:
            runs.append([i])
    for run in runs:
        mine = {store[i] for i in run}
        bars = read_bars(cfg["market"], store[run[0]], store[run[-1]], "development", what="S3 latency (D-590)")
        for day, g in bars.groupby("day", sort=True):
            day = str(day)
            if day not in mine:
                continue
            o, h, l, c = atlas_local.day_arrays(g)
            for L in latencies:
                out[int(L)][day] = LT.lagged_day_sides(o, h, l, c, marks, int(L))[LT.RULE]
        del bars
    for L in latencies:
        for d in side_days:
            out[int(L)].setdefault(d, np.zeros(len(marks), dtype=np.int8))
    return out


def s3_rows(s3: pd.DataFrame) -> dict[str, Any]:
    """S3's rows this check compares with: the two campaign rows and the rule's six lift rows (in R order)."""
    camp = s3[s3["section"].astype(str) == "campaign"]
    out: dict[str, Any] = {}
    for arm in (REFERENCE, LT.S3_ARM):
        r = camp[camp["arm"].astype(str) == arm]
        if len(r) != 1:
            raise SystemExit(f"REFUSED ({DECISION}): {LT.S3_RESULT_FILE} holds {len(r)} {arm} campaign rows, not one")
        out[arm] = r.iloc[0].to_dict()
    lf = s3[(s3["section"].astype(str) == "lift") & (s3["rule"].astype(str) == LT.RULE)].copy()
    lf["R"] = lf["R"].astype(float)
    lf = lf.sort_values("R")
    if tuple(lf["R"]) != tuple(float(x) for x in LT.OFFERED_R):
        raise SystemExit(f"REFUSED ({DECISION}): {LT.S3_RESULT_FILE}'s {LT.RULE} lift rows are at R {list(lf['R'])}")
    out["lift"] = {"trades": lf["trades"].to_numpy(float), "mean": lf["mean_lift"].to_numpy(float),
                   "sd": lf["sd_boot"].to_numpy(float), "t": lf["t_boot"].to_numpy(float),
                   "p": lf["p_boot"].to_numpy(float)}
    return out


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="a smoke: the side identities, the lift's and every guard's "
                                                         "machinery at a few paths; nothing read, nothing written")
    ap.add_argument("--days", type=int, default=None,
                    help=f"--check: walk only N walked days, the first N/2 of each span ({CHECK_DAYS})")
    ap.add_argument("--paths", type=int, default=None, help="--check: G1 and G3 paths (4)")
    ap.add_argument("--g2-paths", type=int, default=None, help="--check: G2 paths (4)")
    ap.add_argument("--coins", type=int, default=None, help="--check: the first coin sequences of G2 (2)")
    ap.add_argument("--starts", type=int, default=None, help="--check: the journey's first starts (unused: no journey)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true", help="D-540: neither keep nor read finished runs' rows")
    ap.add_argument("--resume-dir", default=None, help="D-540: where finished runs' rows are kept (outside the checkout)")
    a = ap.parse_args(argv)
    if not a.check and any(x is not None for x in (a.days, a.paths, a.g2_paths, a.coins, a.starts)):
        print(f"REFUSED ({DECISION}): the reading runs every day, {LT.N_PATHS} / {LT.G2_PATHS} paths, "
              f"{len(LT.COIN_SEEDS)} coins and every start; a smaller run is --check (writes nothing).")
        return 2
    if not a.check and int(a.workers) != 1:
        print(f"REFUSED ({LT.DECLARED_BY}): the reading runs at workers 1.")
        return 2

    import a3_brk30 as B
    import a3_resolution_map as m0
    import atlas_a3 as A
    import rc150_dev_test as R150
    import rc150_payout_screen as PS
    import rc150_routing as RT
    import rc_dev_test as D
    import rc_stop_walkforward as WF
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import read_manifest, read_result, write_result
    from propedge.research import resolved_coin as rc

    n_paths = (a.paths or 4) if a.check else LT.N_PATHS
    g2_paths = (a.g2_paths or 4) if a.check else LT.G2_PATHS
    n_coins = (a.coins or 2) if a.check else len(LT.COIN_SEEDS)
    full = not a.check
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()

    # ---- the declaration, S3's build and the engine's constants
    decl = LT.declaration()
    bad = LT.declaration_problems(decl)
    fixed = {"campaign seed": (S.SEED, LT.CAMPAIGN_SEED), "paths": (S.N_PATHS, LT.N_PATHS),
             "coin seeds": (tuple(RT.COIN_SEEDS), tuple(LT.COIN_SEEDS)), "g2 paths": (RT.G2_PATHS, LT.G2_PATHS),
             "g2 wins": (RT.G2_WINS, LT.G2_WINS), "margin": (RT.MARGIN, LT.MARGIN),
             "spans": ({k: tuple(v) for k, v in WF.SPANS.items()}, {k: tuple(v) for k, v in LT.SPANS.items()}),
             "stop": (RT.STOP, LT.STOP_TICKS), "cell": (RT.CELL, CELL)}
    bad += [f"{k}: the engine's {v[0]!r} against S3's {v[1]!r}" for k, v in fixed.items() if v[0] != v[1]]
    s3_path = RESULTS_DIR / LT.S3_RESULT_FILE
    try:
        s3 = read_result(s3_path)
        s3_sha = read_manifest(s3_path).sha256
    except (OSError, ValueError) as e:
        s3, s3_sha = None, f"unreadable ({e})"
    if s3_sha != LT.S3_RESULT_SHA256:
        bad.append(f"{LT.S3_RESULT_FILE} is {str(s3_sha)[:16]}, not the file D-588 read ({LT.S3_RESULT_SHA256[:16]})")
    if bad:
        print(f"REFUSED ({DECISION}): the build is not D-590's declaration -- " + "; ".join(bad))
        return 2
    S3R = s3_rows(s3)
    print(f"the declaration HOLDS: {LT.DECLARED_BY}'s row (sha256 {decl['sha256'][:16]}); S3's build and "
          f"{LT.S3_RESULT_FILE} (sha256 {s3_sha[:16]}); L = {LT.LATENCY}, rule {LT.RULE}, sign +{LT.SIGN}", flush=True)

    # ---- the cell and identity (a)
    srow = PS.screen_row(RESULTS_DIR)
    print("P-14's inputs, the no-closure plan and the 37.5-point walk...", flush=True)
    I = S.inputs()
    L = I["L"]
    offered = tuple(sorted(float(R) for R in zd.policy_rrs(I["plan"])))
    if offered != tuple(float(x) for x in LT.OFFERED_R):
        print(f"REFUSED ({DECISION}): the table offers R {offered}, not S3's {LT.OFFERED_R}.")
        return 2
    if a.check:                                    # a smoke: the first N/2 walked days of each span, nothing else walked
        dk = L["days"].copy()
        dk["date"] = dk["date"].astype(str)
        dk = dk.sort_values("date").reset_index(drop=True)
        wk = dk[dk["day_kind"].astype(str).isin(m0.WALK_DAY_KINDS)]
        half = max(int(a.days or CHECK_DAYS) // 2, 1)
        pick = [d for lo, hi in LT.SPANS.values() for d in wk[(wk["date"] >= lo) & (wk["date"] <= hi)]["date"][:half]]
        L = {**L, "days": dk[dk["date"].isin(pick)].reset_index(drop=True)}
        I = {**I, "L": L}
    W = WF.walk_stop(I, STOP)
    days = list(W["days"])
    t = WF.cell(W, STOP, days)["trades"]
    h = D.trades_hash(t)
    idents: list[dict] = []

    def ident(name: str, check: str) -> None:
        idents.append({"section": "identity", "identity": name, "holds": True, "check": check})
        print(f"identity ({name}) HOLDS: {check[:110]}", flush=True)

    if full:
        bad = []
        if int(len(t)) != int(srow["candidates"]):
            bad.append(f"{len(t)} candidates against the screen's {int(srow['candidates'])}")
        if h != R150.TRADES_SHA256:
            bad.append(f"content hash {h[:16]} against the pinned {R150.TRADES_SHA256[:16]}")
        if bad:
            print(f"REFUSED ({DECISION}): the cell is not P-16's {CELL} -- " + "; ".join(bad))
            return 3
        ident("a", f"the cell's trades (rc_stop_walkforward.cell on every development day): {len(t)} candidates as "
                   f"{PS.SCREEN_FILE}'s {CELL}; content hash {h} = rc150_dev_test.TRADES_SHA256 (P-16's)")
    else:
        print(f"identity (a): the pinned count and content hash are not comparable on a --check subset ({len(days)} "
              f"days, {len(t)} candidates); the construction identities below run on it", flush=True)
    marks = rc.marks()
    kinds = dict(W["kinds"])
    walked = [d for d in days if kinds.get(d) in m0.WALK_DAY_KINDS]
    tk = list(zip(t["date"].astype(str), t["decision_slot_minutes"].astype(int)))
    coin = np.array([W["coins"][k] for k in tk], dtype=int)
    rcols = [f"r_{R:g}" for R in LT.OFFERED_R]
    gcols = [f"r_{R:g}" for R in W["rr_grid"]]
    both = {}
    for s in (1, -1):                              # S3's both-side walks: the lift's coin twin is P-16's settlement
        ts = WF.cell({**W, "coins": {k: s for k in W["coins"]}}, STOP, days)["trades"]
        sk = list(zip(ts["date"].astype(str), ts["decision_slot_minutes"].astype(int)))
        if sk != tk:
            print(f"REFUSED ({DECISION}): the {'long' if s > 0 else 'short'} walk's offers are not the cell's.")
            return 3
        both[s] = ts[gcols].to_numpy(float)
        del ts
    if not np.array_equal(np.where(coin[:, None] > 0, both[1], both[-1]), t[gcols].to_numpy(float)):
        print(f"REFUSED ({DECISION}): the cell's net R is not its coin side's in the both-side walks.")
        return 3
    ri = [gcols.index(c) for c in rcols]
    r_long, r_short = both[1][:, ri], both[-1][:, ri]
    del both
    ident("a", f"the both-side walks offer exactly the cell's {len(tk)} (date, mark) and its net R is its coin side's")

    # ---- the sides and identity (b)
    t0 = time.time()
    s3_table, _ = S3X.side_table(L["cfg"], walked, marks)                 # S3's own, every rule, L = 0
    lag = lag_side_table(L["cfg"], walked, marks, (0, LT.LATENCY))       # this check's, the rule, L = 0 and L = 5
    q = LT.RULE_INDEX
    s3_col = {d: v[:, q].astype(np.int8) for d, v in s3_table.items()}
    diff = [d for d in sorted(s3_col) if d not in lag[0] or not np.array_equal(lag[0][d], s3_col[d])]
    if sorted(lag[0]) != sorted(s3_col) or diff:
        print(f"REFUSED ({DECISION}): at L = 0 the side table is not S3's for {LT.RULE} on {len(diff)} day(s), e.g. "
              f"{diff[:3]}")
        return 3
    ident("b", f"at L = 0 the latency path's side table for {LT.RULE} equals S3's (s3_event_kinds.side_table, its "
               f"column) at every mark of {len(s3_col)} walked days x {len(marks)} marks")
    prob = LT.shift_problems(s3_col, lag[LT.LATENCY], marks, LT.LATENCY)
    if prob:
        print(f"REFUSED ({DECISION}): the L = {LT.LATENCY} side is not S3's at t - {LT.LATENCY} -- " + "; ".join(prob[:3]))
        return 3
    ident("b", f"at L = {LT.LATENCY} the side at every mark t equals S3's L = 0 side at t - {LT.LATENCY}; marks before "
               f"minute {LT.LATENCY} tie")
    keys, _ = S3X.grid_keys(s3_table, marks)
    col0 = np.concatenate([s3_col[d] for d in sorted(s3_col)]) if s3_col else np.zeros(0, dtype=np.int8)
    col5 = np.concatenate([lag[LT.LATENCY][d] for d in sorted(s3_col)]) if s3_col else np.zeros(0, dtype=np.int8)
    del s3_table
    print(f"the sides: {LT.RULE} at L = 0 and L = {LT.LATENCY} on {len(s3_col)} walked days, {time.time() - t0:.0f} s",
          flush=True)
    hc = D.trades_hash(WF.cell({**W, "coins": S3.campaign_coins(W["coins"], keys, [W["coins"][k] for k in keys])},
                               STOP, days)["trades"])
    if hc != h:
        print(f"REFUSED ({DECISION}): the side table set to P-16's coin rebuilds {hc[:16]}, not {h[:16]}.")
        return 3
    ident("a", f"the side table set to P-16's coin_table (seed {rc.COIN_SEED}) through campaign_coins rebuilds the "
               "cell's content hash: the campaign's construction is P-16's")
    mi = {int(m): i for i, m in enumerate(marks)}
    in_side = np.array([d in s3_col for d, _ in tk], dtype=bool)
    off0 = np.array([s3_col[d][mi[int(m)]] if d in s3_col else 0 for d, m in tk], dtype=np.int8)
    off5 = np.array([lag[LT.LATENCY][d][mi[int(m)]] if d in s3_col else 0 for d, m in tk], dtype=np.int8)
    del lag
    side_rows = [{"section": "sides", "rule": LT.RULE, "latency": LT.LATENCY, "over": over, **LT.changed_share(x, y)}
                 for over, x, y in (("every walked (day, mark)", col0, col5),
                                    ("the cell's offers", off0[in_side], off5[in_side]))]

    # ---- stage 1, beside (and identity (b)'s L = 0 reproduction of S3's lift rows)
    t0 = time.time()
    sess = [d for d in walked if d in s3_col]
    si = {d: i for i, d in enumerate(sess)}
    rl, rs = r_long[in_side], r_short[in_side]
    di = np.array([si[d] for (d, _), k in zip(tk, in_side) if k], dtype=np.int64)
    lift = {}
    lift_rows = []
    for lat, sg in ((0, off0[in_side]), (LT.LATENCY, off5[in_side])):
        lq = S3.lift_matrix(rl, rs, sg[:, None])
        ds, dn = S3.accumulate(di, lq, len(sess))
        st = LT.lift_beside(ds, dn)
        lift[lat] = st
        sided = sg != 0
        side_r = (np.where(sg[sided, None] > 0, rl[sided], rs[sided]).mean(axis=0) if sided.any()
                  else np.full(len(LT.OFFERED_R), np.nan))
        for j, R in enumerate(LT.OFFERED_R):
            lift_rows.append({"section": "lift", "rule": LT.RULE, "latency": lat, "R": float(R), "sessions": len(sess),
                              "offers": int(len(sg)), "ties": int((sg == 0).sum()), "trades": float(st["trades"][j]),
                              "mean_lift": float(st["mean"][j]), "sd_boot": float(st["sd"][j]),
                              "t_boot": float(st["t"][j]), "p_boot": float(st["p"][j]),
                              "mean_r_rule_side": float(side_r[j]), "boot_seed": LT.BOOT_SEED,
                              "mean_block": LT.BOOT_BLOCK, "reps": LT.BOOT_REPS,
                              "selection": "none (one rule; beside, deciding nothing)" if lat else
                                           "identity: S3's lift rows for the rule"})
    if full:
        prob = LT.lift_problems(lift[0], S3R["lift"])
        if prob:
            print(f"REFUSED ({DECISION}): stage 1 at L = 0 is not S3's lift for {LT.RULE} -- " + "; ".join(prob))
            return 3
        ident("b", f"stage 1 at L = 0 (S3's bootstrap, seed {LT.BOOT_SEED}) equals {LT.S3_RESULT_FILE}'s lift rows for "
                   f"{LT.RULE} at every offered R")
    print(f"stage 1 (beside): {LT.RULE} at L = 0 and L = {LT.LATENCY} on {int(in_side.sum())} offers over {len(sess)} "
          f"sessions, {time.time() - t0:.0f} s", flush=True)

    # ---- the arms' trades: only the sides move
    t0c = WF.cell({**W, "coins": S3.campaign_coins(W["coins"], keys, col0, LT.SIGN)}, STOP, days)["trades"]
    t5 = WF.cell({**W, "coins": S3.campaign_coins(W["coins"], keys, col5, LT.SIGN)}, STOP, days)["trades"]
    h0, h5 = D.trades_hash(t0c), D.trades_hash(t5)
    if full:
        want = S3R[LT.S3_ARM]
        bad = []
        if h0 != str(want["cell_trades_sha256"]):
            bad.append(f"content hash {h0[:16]} against S3's {str(want['cell_trades_sha256'])[:16]}")
        if int(len(t0c)) != int(float(want["candidates"])):
            bad.append(f"{len(t0c)} candidates against S3's {int(float(want['candidates']))}")
        if bad:
            print(f"REFUSED ({DECISION}): the L = 0 arm's trades are not S3's {LT.S3_ARM} -- " + "; ".join(bad))
            return 3
        ident("c", f"the L = 0 arm's trades carry {LT.S3_RESULT_FILE}'s {LT.S3_ARM} cell_trades_sha256 {h0} and its "
                   f"{len(t0c)} candidates")

    resume = None
    if full and not a.no_resume:
        import subprocess

        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = Resume(folder, f"{commit}_{n_paths}_{g2_paths}")

    # ---- identity (d): the reference's paired run is S3's P16_coin row
    t0 = time.time()

    def make_ref():
        r = RT.run_rule(I, REFERENCE, None, t, days, n_paths, a.workers, twin=True)
        df = r.pop("df")
        if full:
            prob = PS.growth_problems(df, srow)
            if prob:
                raise SystemExit(f"REFUSED ({DECISION}): the reference is not {PS.SCREEN_FILE}'s {CELL} -- "
                                 + "; ".join(prob))
        return {"section": "campaign", "arm": REFERENCE, "rule": "", "sign": 0, "latency": 0,
                "candidates": int(len(t)), "side_rule": f"P-16's coin_table (seed {rc.COIN_SEED})",
                "cell_trades_sha256": h, **r}

    ref_g1 = _cached(resume, "g1 reference", make_ref)
    if full:
        prob = LT.row_problems(ref_g1, S3R[REFERENCE])
        if prob:
            print(f"REFUSED ({DECISION}): the reference is not {LT.S3_RESULT_FILE}'s {REFERENCE} row -- "
                  + "; ".join(prob))
            return 3
        ident("d", f"the reference (P-16's coin) at seed {S.SEED}, {LT.N_PATHS} paths equals {LT.S3_RESULT_FILE}'s "
                   f"{REFERENCE} campaign row and {PS.SCREEN_FILE}'s {CELL} ({time.time() - t0:.0f} s)")
    ref = float(ref_g1["growth_on_required"])

    # ---- identity (c): the L = 0 arm's paired run is S3's lnbar1x4_follow row
    t0 = time.time()

    def make_l0():
        r = RT.run_rule(I, LT.ARM_L0, None, t0c, days, n_paths, a.workers, twin=True)
        r.pop("df")
        return {"section": "campaign", "arm": LT.ARM_L0, "rule": LT.RULE, "sign": LT.SIGN, "latency": 0,
                "candidates": int(len(t0c)), "side_rule": f"{LT.RULE} followed, read at t (S3's); a tie takes P-16's "
                                                           "coin side", "cell_trades_sha256": h0, **r}

    l0_g1 = _cached(resume, f"g1 {LT.ARM_L0}", make_l0)
    if full:
        prob = LT.row_problems(l0_g1, S3R[LT.S3_ARM])
        if prob:
            print(f"REFUSED ({DECISION}): the L = 0 arm is not {LT.S3_RESULT_FILE}'s {LT.S3_ARM} row -- "
                  + "; ".join(prob))
            return 3
        ident("c", f"the L = 0 arm's paired G1 run at seed {S.SEED}, {LT.N_PATHS} paths reproduces "
                   f"{LT.S3_RESULT_FILE}'s {LT.S3_ARM} campaign row ({time.time() - t0:.0f} s)")

    # ---- the guards, in D-590's order; the first failure ends the run (--check runs every guard's machinery)
    done: list[dict] = []
    run_all = a.check
    campaign = [ref_g1, l0_g1]
    extra: list[dict] = []
    g2_rows: list[dict] = []
    g2s: list[dict] = []
    g3_rows: list[dict] = []
    nan = float("nan")

    def v(**kw) -> dict:
        args = {"g1_growth": nan, "ref_growth": ref, "resolves": False, "g2_row": None, "span_growth": {},
                "span_ref": {}, **kw}
        return S3.verdict(LT.ARM, args["g1_growth"], args["ref_growth"], args["resolves"], args["g2_row"],
                          args["span_growth"], args["span_ref"])

    def due(guard: str) -> bool:
        return run_all or LT.next_guard(done) == guard

    # resolution
    res_off, ok_off = A.resolution(t5, W["offered_rr"])
    _, ok_grid = A.resolution(t5, W["rr_grid"])
    done.append({"guard": "resolution", "passes": LT.guard_check("resolution", v(resolves=bool(ok_off))),
                 "needed": "every offered R unresolved at most 5 % overall and in its worst year (D-212)",
                 "every_grid_r_resolves": bool(ok_grid), **res_off})
    # G1
    g1_row = None
    if due("g1"):
        t0 = time.time()

        def make_g1():
            r = RT.run_rule(I, LT.ARM, None, t5, days, n_paths, a.workers, twin=True)
            r.pop("df")
            if a.check:
                jl = {"journey": [], "lines": [], "lines_hold": None}
            else:
                jl = RT.journey_and_lines(I, t5, days, None, LT.ARM, PS.fv3c_slices(RESULTS_DIR), a.workers, None)
            row = {"section": "campaign", "arm": LT.ARM, "rule": LT.RULE, "sign": LT.SIGN, "latency": LT.LATENCY,
                   "candidates": int(len(t5)), "side_rule": f"{LT.RULE} followed, read at t - {LT.LATENCY} (bars closed "
                                                            f"at or before it); a tie takes P-16's coin side",
                   "cell_trades_sha256": h5, **r, **res_off, "every_offered_r_resolves": bool(ok_off),
                   "every_grid_r_resolves": bool(ok_grid), "slice_lines_hold": jl["lines_hold"]}
            return {"row": row, "journey": jl["journey"], "lines": jl["lines"]}

        res = _cached(resume, f"g1 {LT.ARM}", make_g1)
        g1_row = res["row"]
        campaign.append(g1_row)
        extra += [{**r, "arm": LT.ARM} for r in res["journey"]] + [{**r, "arm": LT.ARM} for r in res["lines"]]
        g = float(g1_row["growth_on_required"])
        done.append({"guard": "g1", "passes": LT.guard_check("g1", v(g1_growth=g)), "value": g, "reference_value": ref,
                     "difference": g - ref, "needed": f"difference > {LT.MARGIN}"})
        print(f"  G1 {LT.ARM}: done ({time.time() - t0:.0f} s)", flush=True)
    for r in campaign:
        r["growth_minus_reference"] = float(r["growth_on_required"]) - ref
    # G2
    if due("g2"):
        routing = read_result(RESULTS_DIR / ROUTING_FILE) if (RESULTS_DIR / ROUTING_FILE).is_file() else None
        dd = L["days"]["date"].astype(str).tolist()
        for s in LT.COIN_SEEDS[:n_coins]:
            t0 = time.time()
            base = rc.coin_table(dd, marks, seed=int(s))

            def make_g2(s=s, base=base, arm=False):
                coins = S3.campaign_coins(base, keys, col5, LT.SIGN) if arm else base
                name = LT.ARM if arm else REFERENCE
                ts = WF.cell({**W, "coins": coins}, STOP, days)["trades"]
                r = RT.run_rule(I, f"g2 {s} {name}", None, ts, days, g2_paths, a.workers)
                r.pop("df")
                return {"section": "g2", "coin_seed": int(s), "arm": name, **r}

            row = _cached(resume, f"g2 {s} {REFERENCE}", make_g2)
            if routing is not None and full:
                prob = S3X._routing_problems(routing, "g2", row, coin_seed=int(s))
                if prob:
                    print(f"REFUSED ({DECISION}): G2's reference on coin {s} is not {ROUTING_FILE}'s {ROUTING_REF} -- "
                          + "; ".join(prob))
                    return 3
            g2_rows.append(row)
            g2_rows.append(_cached(resume, f"g2 {s} {LT.ARM}", lambda s=s, base=base: make_g2(s, base, True)))
            print(f"  G2 coin {s}: done ({time.time() - t0:.0f} s)", flush=True)
            del base
        if routing is not None and full:
            ident("d", f"G2's reference on every coin sequence equals {ROUTING_FILE}'s {ROUTING_REF} row")
        g2s = S3.g2_summary(g2_rows, [LT.ARM], REFERENCE)
        done.append({"guard": "g2", "passes": LT.guard_check("g2", v(g2_row=g2s[0])), "value": g2s[0]["wins"],
                     "coins": g2s[0]["coins"], "needed": f"wins >= {LT.G2_WINS} of {len(LT.COIN_SEEDS)}"})
    # G3
    span_g: dict[str, dict[str, float]] = {}
    if due("g3"):
        routing = read_result(RESULTS_DIR / ROUTING_FILE) if (RESULTS_DIR / ROUTING_FILE).is_file() else None
        for span, (lo, hi) in LT.SPANS.items():
            sd = WF.span_days(days, lo, hi)
            for arm in (False, True):
                name = LT.ARM if arm else REFERENCE

                def make_g3(arm=arm, name=name, span=span, sd=sd):
                    coins = S3.campaign_coins(W["coins"], keys, col5, LT.SIGN) if arm else W["coins"]
                    ts = WF.cell({**W, "coins": coins}, STOP, sd)["trades"]
                    head = {"section": "g3", "span": span, "span_first": sd[0], "span_last": sd[-1],
                            "sessions": len(sd), "arm": name}
                    if ts is None or not len(ts):          # the span's own cutoff admits no mark (only on a smoke)
                        return {**head, "candidates": 0, "growth_on_required": float("nan"),
                                "note": "no mark admitted on this span alone"}
                    bounds = B.check_bounds(ts, sd, B.rrs(ts))
                    r = RT.run_rule(I, f"g3 {span} {name}", None, ts, sd, n_paths, a.workers, bounds=bounds)
                    r.pop("df")
                    return {**head, "candidates": int(len(ts)), **r}

                row = _cached(resume, f"g3 {span} {name}", make_g3)
                if not arm and routing is not None and full:
                    prob = S3X._routing_problems(routing, "g3", row, span=span)
                    if prob:
                        print(f"REFUSED ({DECISION}): G3's reference on {span} is not {ROUTING_FILE}'s {ROUTING_REF} "
                              "-- " + "; ".join(prob))
                        return 3
                g3_rows.append(row)
                span_g.setdefault(name, {})[span] = float(row["growth_on_required"])
            print(f"  G3 {span}: done ({len(sd)} sessions)", flush=True)
        if routing is not None and full:
            ident("d", f"G3's reference on each span equals {ROUTING_FILE}'s {ROUTING_REF} row")
        sg_, sr_ = span_g.get(LT.ARM, {}), span_g.get(REFERENCE, {})
        done.append({"guard": "g3", "passes": LT.guard_check("g3", v(span_growth=sg_, span_ref=sr_)),
                     **{f"{k}_difference": float(sg_.get(k, nan)) - float(sr_.get(k, nan)) for k in LT.SPANS},
                     "needed": "not below the reference on either span alone"})

    # ---- the verdict
    upto = next((i + 1 for i, g in enumerate(done) if not g["passes"]), len(done))
    guard_out, verdict = LT.guard_rows(LT.ARM, done[:upto])
    if len(done[:upto]) == len(LT.GUARDS):
        s3v = v(g1_growth=float(g1_row["growth_on_required"]), resolves=bool(ok_off), g2_row=g2s[0],
                span_growth=span_g.get(LT.ARM, {}), span_ref=span_g.get(REFERENCE, {}))
        if not LT.verdict_agrees(verdict, s3v):
            print(f"REFUSED ({DECISION}): the staged verdict is not S3's verdict on the same four guards.")
            return 3
        verdict.update({k: s3v[k] for k in ("growth_minus_reference", "early_growth_minus_reference",
                                             "late_growth_minus_reference")})
    seconds = time.time() - t_all
    if a.check:
        print(f"--check done: identities (b) and the construction on {len(sess)} sessions; stage 1's machinery at L = 0 "
              f"and {LT.LATENCY}; every guard's machinery on {LT.ARM} (G1/G3 {n_paths} paths, G2 {g2_paths} paths on "
              f"{n_coins} coins); no reading printed; nothing written. {seconds:.0f} s")
        return 0
    decl_row = {"section": "declaration", "holds": True,
                "check": f"DECISIONS.md's {LT.DECLARED_BY} row sha256 {decl['sha256']} (LF line); every phrase and "
                         f"constant agrees; S3's declaration and constants; {LT.S3_RESULT_FILE} sha256 {s3_sha}"}
    out = pd.concat([pd.DataFrame([decl_row] + idents + side_rows + lift_rows + campaign + extra + g2_rows + g2s
                                  + g3_rows + guard_out + [verdict])], ignore_index=True)
    out.insert(1, "reading", READING)
    counter = VariantCounter(path=rd / "variants.jsonl")
    counter.record(prereg_id=FAMILY_ID, seed=LT.CAMPAIGN_SEED, exploratory=True,
                   params={"study": "D-590, S3's candidate at the operator's latency", "cell": CELL, "rule": LT.RULE,
                           "sign": LT.SIGN, "latency_minutes": LT.LATENCY, "offered_r": list(LT.OFFERED_R),
                           "campaign_seed": LT.CAMPAIGN_SEED},
                   label=f"D-578's S3-L5: {LT.S3_ARM} with the side read at t - {LT.LATENCY}")
    write_result(out, RESULT, script=SCRIPT, seed=LT.CAMPAIGN_SEED, exploratory=True, results_dir=results_dir,
                 variant_count=LT.N_VARIANTS,
                 parameters={"decision": DECISION, "declared_by": LT.DECLARED_BY, "variant": FAMILY_ID,
                             "declaration_sha256": decl["sha256"], "s3_result_sha256": s3_sha, "cell": CELL,
                             "stop_ticks": STOP, "rule": LT.RULE, "sign": LT.SIGN, "latency_minutes": LT.LATENCY,
                             "lag": "the side at mark t is S3's day_sides at t - L (bars ending at or before t - L); "
                                    "t - L < 0 ties and takes the coin's side",
                             "offered_r": list(LT.OFFERED_R), "boot_reps": LT.BOOT_REPS, "boot_block": LT.BOOT_BLOCK,
                             "boot_seed": LT.BOOT_SEED, "campaign_seed": S.SEED, "coin_seed": rc.COIN_SEED,
                             "g1_paths": LT.N_PATHS, "g2_coin_seeds": [LT.COIN_SEEDS[0], LT.COIN_SEEDS[-1]],
                             "g2_paths": LT.G2_PATHS, "g2_wins_needed": LT.G2_WINS,
                             "g3_spans": {k: list(x) for k, x in LT.SPANS.items()}, "margin": LT.MARGIN,
                             "guards": list(LT.GUARDS), "guards_run": [g["guard"] for g in done[:upto]],
                             "cell_trades_sha256": h, "l0_trades_sha256": h0, "l5_trades_sha256": h5,
                             "ident_atol": LT.IDENT_ATOL,
                             "fv3c_slices": "results/customer_slices.csv (sha256 pinned), read, never rerun",
                             "workers": int(a.workers), "seconds": round(seconds, 1)},
                 notes={"status": READING, "selection": "none: one declared variant; the first failing guard ends the "
                                                        "run, the rest not_run; a candidate needs all four"},
                 description="EXPLORATORY (D-578, D-590): S3's candidate lnbar1x4_follow with its side read from bars "
                             "closed at or before t - 5 minutes (the operator's latency, D-266); P-16's cell otherwise; "
                             "D-578's four guards against P-16 in the order resolution, G1, G2, G3, the first failure "
                             "ending the run; stage 1's lift at L = 5 and the share of changed sides beside.")
    print(pd.DataFrame(guard_out)[["order", "guard", "status"]].to_string(index=False))
    print(f"candidate: {verdict['candidate']}; written: {RESULT}.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
