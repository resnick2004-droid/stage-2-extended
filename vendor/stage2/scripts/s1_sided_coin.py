"""EXPLORATORY (D-578): batch S1 of the rolling model search -- the sided coin. P-16's cell with each offer's side taken
from a declared rule on bars closed at or before the mark instead of the coin; a family-wise per-offer lift test
(stage 1) and, for its survivors only, P-16's paired campaign with D-578's four guards (stage 2).

    python scripts/s1_sided_coin.py --check                  # 30 walked days only (the first 15 of each span): the
                                                             #   construction identities, stage 1, stage 2's machinery
                                                             #   on a smoke arm at 4 paths, 2 coins; no lift printed;
                                                             #   nothing written (the pinned identities need every day)
    python scripts/s1_sided_coin.py --workers 2              # the reading (a clean checkout, D-474)

**The declaration** (`config/search_program.yaml`, batch S1, D-578) is read as text, its sha256 pinned
(`s1_sided_coin.DECLARATION_SHA256`) and every constant checked against it before anything is built; a difference
refuses.

**The cell** (P-16, D-544, D-547): `rc_stop_walkforward.walk_stop` / `cell` at 150 ticks on every development day -- the
cell rc150_routing used (`rc_s150_all` in `rc_width_screen.csv` is already the news-safe build, `drop_release_minute`,
so it IS P-16's `rc_s150_all_nr`: its content hash is `rc150_dev_test.TRADES_SHA256`, the trades P-16 registered).

**Identities first, refusing:** (i) the cell's count against `rc_width_screen.csv`'s `rc_s150_all` and its content hash
against `rc150_dev_test.TRADES_SHA256`; the side table set to P-16's own `coin_table` through `campaign_coins` rebuilds
the same content hash; the both-side walks (every coin long, every coin short) carry the cell's exact offers, and the
cell's net R at every R equals its coin side's -- so the lift's twin is P-16's own settlement; (ii) the reference
(P-16's coin, the current router) at seed 20261131, 500 paths, reproduces `rc_width_screen.csv`'s `rc_s150_all` growth
at the bound and point and its required bankroll (as rc150_routing's G1 reference did); (iii) stage 2's reference rows
across coins and on the two spans equal rc150_routing.csv's R0 rows (the same construction at the same seeds).

**Stage 1** (`s1_sided_coin.lift_matrix` / `stage1`): every offer of the cell, every offered R, the lift over the coin twin;
ties excluded and counted; the sessions are the cell's walked development days (normal and report days, as A4's); the
studentised max-statistic family-wise at 0.025 (block 21, 2,000 replicates, seed 20261105), BH at 10 % beside.

**Stage 2** (survivors only, each (rule, sign)): the cell rebuilt with `coins` replaced by the rule's sides (a tie keeps
the coin sequence's own side) -- G1, paired: campaign seed 20261131, 500 paths, the zero-edge twin, D-518's journey and
D-509's slice lines beside (rc150_routing's G1); G2: 50 coin sequences (20261600 + i), 200 paths, P-16 rebuilt with each
and the rule with ties from the same sequence; G3: 2020-2023 and 2024-2026-07-16 alone (each span's own cutoff and pooled
bound, `rc_stop_walkforward`), 500 paths. D-578 (2)'s guards: (a) G1 growth at the bound above the reference's by more
than 0.05; (b) every offered R resolves (D-212); (c) at least 40 of 50 coin sequences won; (d) not below the reference
on either span.

**Resume** (D-540's form, `rc_robust`'s): each finished engine run kept outside the checkout, keyed by commit and counts;
`--no-resume`, `--resume-dir`; off in --check.

Writes `results/s1_sided_coin.csv` (EXPLORATORY; sections declaration, menu, identity, lift, bootstrap, survivors,
campaign, journey, slice_lines, g2, g2_summary, g3, verdict) with its manifest; 15 variants under `D-578:S1`.
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
from propedge.research import s1_sided_coin as S1  # noqa: E402

SCRIPT = "scripts/s1_sided_coin.py"
DECISION = S1.DECISION
RESULT = "s1_sided_coin"
FAMILY_ID = S1.FAMILY_ID
CELL = "rc_s150_all"
STOP = S1.STOP_TICKS
REFERENCE = "P16_coin"
SMOKE_ARM = ("mom1", 1)                    # --check only: stage 2's machinery on one arm (a smoke's survivors mean nothing)
CHECK_DAYS = 30
ROUTING_FILE = "rc150_routing.csv"         # identity (iii): its R0 rows (D-576)
ROUTING_REF = "R0_longest_waiting"
READING = ("EXPLORATORY (D-578): batch S1, the sided coin -- a family-wise per-offer lift test at 0.025 and, for its "
           "survivors only, P-16's paired campaign with D-578's four guards; selects nothing by itself")
IDENT_COLS = ("growth_on_required", "growth_on_required_point", "required_p90")


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


#: the bars are read this many store days at a time (with the previous store day for pday), so the whole window is never
#: in memory at once
BAR_CHUNK = 120


def side_table(cfg: dict, side_days: list[str], marks: list[int]) -> dict[str, np.ndarray]:
    """{date: (marks, rules) int8 sides} on `side_days` from the development bars (the window guard first): each day's
    arrays as the walk reads them (`atlas_local.day_arrays`), pday from the store's previous session. Read in chunks of
    `BAR_CHUNK` store days, each with the store day before it."""
    from propedge.data.bars import read_bars, trading_days
    from propedge.research import atlas_local

    store = [str(d) for d in trading_days(cfg["market"])]
    pos = {d: i for i, d in enumerate(store)}
    want = sorted(set(side_days))
    missing = [d for d in want if d not in pos]
    if missing:
        raise SystemExit(f"REFUSED ({DECISION}): {len(missing)} walked day(s) not in the bar store, e.g. {missing[:3]}")
    out: dict[str, np.ndarray] = {}
    idx = sorted(pos[d] for d in want)
    runs: list[list[int]] = []
    for i in idx:                                  # consecutive store days, at most BAR_CHUNK a read
        if runs and i == runs[-1][-1] + 1 and len(runs[-1]) < BAR_CHUNK:
            runs[-1].append(i)
        else:
            runs.append([i])
    for run in runs:
        lo = store[max(run[0] - 1, 0)]
        mine = {store[i] for i in run}             # the read's first day (the prior session) is only read, never set
        bars = read_bars(cfg["market"], lo, store[run[-1]], "development", what="S1 sided coin (D-578)")
        prior = S1.session_signs(bars[["day", "ts", "open", "close"]])
        for day, g in bars.groupby("day", sort=True):
            day = str(day)
            if day not in mine:
                continue
            o, h, l, c = atlas_local.day_arrays(g)
            # the store's first day has no prior session in the window: a tie (session_signs gives 0)
            sd = S1.day_sides(o, h, l, c, marks, prior_sign=prior.get(day, 0) if pos[day] > 0 else 0)
            out[day] = np.stack([sd[n] for n in S1.RULE_NAMES], axis=1).astype(np.int8)
        del bars, prior
    for d in side_days:                            # a walked day with no bars: every rule ties
        out.setdefault(d, np.zeros((len(marks), len(S1.RULE_NAMES)), dtype=np.int8))
    return out


def grid_keys(table: dict[str, np.ndarray], marks: list[int]) -> tuple[list[tuple[str, int]], np.ndarray]:
    """Every (date, mark) the side table holds, in date then mark order, with its (n, rules) sides."""
    keys = [(d, int(m)) for d in sorted(table) for m in marks]
    sides = np.concatenate([table[d] for d in sorted(table)], axis=0) if table else np.zeros((0, len(S1.RULE_NAMES)))
    return keys, sides


def arm_coins(base: dict, keys: list, sides: np.ndarray, arm: tuple[str, int]) -> dict:
    q = S1.RULE_NAMES.index(arm[0])
    return S1.campaign_coins(base, keys, sides[:, q], arm[1])


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
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
    from propedge.reporting.results import read_result, write_result
    from propedge.research import resolved_coin as rc

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="a smoke: identities, stage 1 on the first days, stage 2's "
                                                         "machinery on one arm at a few paths; nothing written")
    ap.add_argument("--days", type=int, default=None,
                    help=f"--check: walk only N walked days, the first N/2 of each span ({CHECK_DAYS})")
    ap.add_argument("--paths", type=int, default=None, help="--check: G1 and G3 paths (4)")
    ap.add_argument("--g2-paths", type=int, default=None, help="--check: G2 paths (4)")
    ap.add_argument("--coins", type=int, default=None, help="--check: the first coin sequences of G2 (2)")
    ap.add_argument("--starts", type=int, default=None, help="--check: the journey's first starts (6)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true", help="D-540: neither keep nor read finished runs' rows")
    ap.add_argument("--resume-dir", default=None, help="D-540: where finished runs' rows are kept (outside the checkout)")
    a = ap.parse_args(argv)
    if not a.check and any(x is not None for x in (a.days, a.paths, a.g2_paths, a.coins, a.starts)):
        print(f"REFUSED ({DECISION}): the reading runs every day, {S1.N_PATHS} / {S1.G2_PATHS} paths, "
              f"{len(S1.COIN_SEEDS)} coins and every start; a smaller run is --check (writes nothing).")
        return 2
    n_paths = (a.paths or 4) if a.check else S1.N_PATHS
    g2_paths = (a.g2_paths or 4) if a.check else S1.G2_PATHS
    n_coins = (a.coins or 2) if a.check else len(S1.COIN_SEEDS)
    starts = (a.starts or 6) if a.check else None
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()

    # ---- the declaration and the constants it fixes
    decl = S1.declaration()
    bad = S1.declaration_problems(decl)
    fixed = {"campaign seed": (S.SEED, S1.CAMPAIGN_SEED), "paths": (S.N_PATHS, S1.N_PATHS),
             "coin seeds": (tuple(RT.COIN_SEEDS), tuple(S1.COIN_SEEDS)), "g2 paths": (RT.G2_PATHS, S1.G2_PATHS),
             "g2 wins": (RT.G2_WINS, S1.G2_WINS), "margin": (RT.MARGIN, S1.MARGIN),
             "spans": ({k: tuple(v) for k, v in WF.SPANS.items()}, {k: tuple(v) for k, v in S1.SPANS.items()}),
             "stop": (RT.STOP, S1.STOP_TICKS), "cell": (RT.CELL, CELL)}
    bad += [f"{k}: the engine's {v[0]!r} against S1's {v[1]!r}" for k, v in fixed.items() if v[0] != v[1]]
    if bad:
        print(f"REFUSED ({DECISION}): the build is not D-578's declaration -- " + "; ".join(bad))
        return 2
    print(f"the declaration HOLDS: {decl['path']} (sha256 {decl['sha256'][:16]}); 15 rules, 90 hypotheses", flush=True)

    # ---- the cell and identity (i)
    srow = PS.screen_row(RESULTS_DIR)
    print("P-14's inputs, the no-closure plan and the 37.5-point walk...", flush=True)
    I = S.inputs()
    L = I["L"]
    offered = tuple(sorted(float(R) for R in zd.policy_rrs(I["plan"])))
    if offered != tuple(float(x) for x in S1.OFFERED_R):
        print(f"REFUSED ({DECISION}): the table offers R {offered}, not D-578's {S1.OFFERED_R}.")
        return 2
    if a.check:                                    # a smoke: the first N/2 walked days of each span, nothing else walked
        dk = L["days"].copy()
        dk["date"] = dk["date"].astype(str)
        dk = dk.sort_values("date").reset_index(drop=True)
        wk = dk[dk["day_kind"].astype(str).isin(m0.WALK_DAY_KINDS)]
        half = max(int(a.days or CHECK_DAYS) // 2, 1)
        pick = [d for lo, hi in S1.SPANS.values() for d in wk[(wk["date"] >= lo) & (wk["date"] <= hi)]["date"][:half]]
        L = {**L, "days": dk[dk["date"].isin(pick)].reset_index(drop=True)}
        I = {**I, "L": L}
    W = WF.walk_stop(I, STOP)
    days = list(W["days"])
    t = WF.cell(W, STOP, days)["trades"]
    h = D.trades_hash(t)
    idents = []
    if a.check:
        print(f"identity (i): the pinned count and content hash are not comparable on a --check subset ({len(days)} "
              f"days, {len(t)} candidates); the construction identities below run on it", flush=True)
    else:
        bad = []
        if int(len(t)) != int(srow["candidates"]):
            bad.append(f"{len(t)} candidates against the screen's {int(srow['candidates'])}")
        if h != R150.TRADES_SHA256:
            bad.append(f"content hash {h[:16]} against the pinned {R150.TRADES_SHA256[:16]}")
        if bad:
            print(f"REFUSED ({DECISION}): the cell is not P-16's {CELL} -- " + "; ".join(bad))
            return 3
        idents.append({"section": "identity", "holds": True,
                       "check": f"the cell's trades (rc_stop_walkforward.cell on every development day): {len(t)} "
                                f"candidates as {PS.SCREEN_FILE}'s {CELL}; content hash {h} = "
                                "rc150_dev_test.TRADES_SHA256 (P-16's)"})
        print(f"identity (i) HOLDS: the cell = P-16's {CELL} ({len(t)} candidates; content hash {h[:16]})", flush=True)
    marks = rc.marks()
    kinds = dict(W["kinds"])
    walked = [d for d in days if kinds.get(d) in m0.WALK_DAY_KINDS]
    side_days = walked
    # the both-side walks: every coin long, every coin short -- the cell's offers and P-16's own settlement
    tk = list(zip(t["date"].astype(str), t["decision_slot_minutes"].astype(int)))
    coin = np.array([W["coins"][k] for k in tk], dtype=int)
    rcols = [f"r_{R:g}" for R in S1.OFFERED_R]
    gcols = [f"r_{R:g}" for R in W["rr_grid"]]
    both = {}
    for s in (1, -1):
        ts = WF.cell({**W, "coins": {k: s for k in W["coins"]}}, STOP, days)["trades"]
        sk = list(zip(ts["date"].astype(str), ts["decision_slot_minutes"].astype(int)))
        if sk != tk:
            print(f"REFUSED ({DECISION}): the {'long' if s > 0 else 'short'} walk's offers are not the cell's.")
            return 3
        both[s] = ts[gcols].to_numpy(float)
        del ts
    mine = np.where(coin[:, None] > 0, both[1], both[-1])
    if not np.array_equal(mine, t[gcols].to_numpy(float)):
        print(f"REFUSED ({DECISION}): the cell's net R is not its coin side's in the both-side walks.")
        return 3
    ri = [gcols.index(c) for c in rcols]
    r_long, r_short = both[1][:, ri], both[-1][:, ri]
    del both, mine
    idents.append({"section": "identity", "holds": True,
                   "check": "the both-side walks (every coin long, every coin short) offer exactly the cell's "
                            f"{len(tk)} (date, mark) in its order, and the cell's net R at every R of the grid equals "
                            "its coin side's: the lift's coin twin is P-16's own settlement"})
    print("identity (i) HOLDS: the both-side walks carry the cell's offers and settlement", flush=True)

    # ---- the sides
    t0 = time.time()
    table = side_table(L["cfg"], side_days, marks)
    keys, sides_grid = grid_keys(table, marks)
    print(f"the sides: {len(S1.RULE_NAMES)} rules on {len(table)} walked days x {len(marks)} marks, "
          f"{time.time() - t0:.0f} s", flush=True)
    hc = D.trades_hash(WF.cell({**W, "coins": S1.campaign_coins(W["coins"], keys, [W["coins"][k] for k in keys])},
                               STOP, days)["trades"])
    if hc != h:
        print(f"REFUSED ({DECISION}): the side table set to P-16's coin rebuilds {hc[:16]}, not {h[:16]}.")
        return 3
    idents.append({"section": "identity", "holds": True,
                   "check": f"the side table set to P-16's coin_table (seed {rc.COIN_SEED}) through campaign_coins "
                            "rebuilds the cell's content hash: stage 2's construction is P-16's"})
    print("identity (i) HOLDS: the side table set to P-16's coin rebuilds the cell's content hash", flush=True)
    mi = {int(m): i for i, m in enumerate(marks)}
    in_side = np.array([d in table for d, _ in tk])
    sides = np.zeros((len(tk), len(S1.RULE_NAMES)), dtype=np.int8)
    for i, (d, m) in enumerate(tk):
        if d in table:
            sides[i] = table[d][mi[int(m)]]

    resume = None
    if not a.check and not a.no_resume:
        import subprocess

        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = Resume(folder, f"{commit}_{n_paths}_{g2_paths}")

    # ---- identity (ii): the reference's paired run
    t0 = time.time()

    def make_ref():
        r = RT.run_rule(I, REFERENCE, None, t, days, n_paths, a.workers, twin=True)
        df = r.pop("df")
        if n_paths == S1.N_PATHS:
            prob = PS.growth_problems(df, srow)
            if prob:
                raise SystemExit(f"REFUSED ({DECISION}): the reference is not {PS.SCREEN_FILE}'s {CELL} -- "
                                 + "; ".join(prob))
        return {"section": "campaign", "arm": REFERENCE, "rule": "", "sign": 0, "candidates": int(len(t)),
                "side_rule": f"P-16's coin_table (seed {rc.COIN_SEED})", **r}

    ref_g1 = _cached(resume, "g1 reference", make_ref)
    if n_paths == S1.N_PATHS:
        idents.append({"section": "identity", "holds": True,
                       "check": f"the reference (P-16's coin, the current router) at seed {S.SEED}, {S1.N_PATHS} paths, "
                                f"reproduces results/{PS.SCREEN_FILE}'s {CELL} growth at the bound and point and its "
                                "required bankroll"})
        print(f"identity (ii) HOLDS: the reference at {S1.N_PATHS} paths = {PS.SCREEN_FILE}'s {CELL} "
              f"({time.time() - t0:.0f} s)", flush=True)
    else:
        print(f"identity (ii): not comparable at {n_paths} paths (needs {S1.N_PATHS}); the reference ran "
              f"({time.time() - t0:.0f} s)", flush=True)

    # ---- stage 1: the lift
    t0 = time.time()
    sess = [d for d in walked if d in table]
    si = {d: i for i, d in enumerate(sess)}
    sub = in_side
    rl, rs, sg = r_long[sub], r_short[sub], sides[sub]
    di = np.array([si[d] for (d, _), k in zip(tk, sub) if k], dtype=np.int64)
    nR = len(S1.OFFERED_R)
    H = len(S1.RULE_NAMES) * nR
    day_sum, day_n = np.zeros((len(sess), H)), np.zeros((len(sess), H))
    side_r = np.full(H, np.nan)
    for q in range(len(S1.RULE_NAMES)):                    # one rule at a time: (offers, 6) in memory, not (offers, 90)
        cols = slice(q * nR, (q + 1) * nR)
        lq = S1.lift_matrix(rl, rs, sg[:, [q]])
        day_sum[:, cols], day_n[:, cols] = S1.accumulate(di, lq, len(sess))
        s = sg[:, q]
        if (s != 0).any():
            side_r[cols] = np.where(s[s != 0, None] > 0, rl[s != 0], rs[s != 0]).mean(axis=0)
        del lq
    test = S1.stage1(day_sum, day_n)
    offers = int(sub.sum())
    ties = (sg == 0).sum(axis=0)
    hyp = S1.hypotheses().assign(
        offers=offers, ties=np.repeat(ties, nR), tie_share=np.repeat(ties / max(offers, 1), nR), trades=test["trades"],
        mean_lift=test["mean"], sd_boot=test["sd"], t_boot=test["t"], p_boot=test["p"], survives=test["survives"],
        bh_reject=test["bh"], side_sign=np.where(test["mean"] > 0, 1, -1),
        winning_side=np.where(test["mean"] > 0, "follow", "fade"), mean_r_rule_side=side_r)
    surv = S1.survivors(hyp)
    print(f"stage 1: {len(hyp)} hypotheses on {offers} offers over {len(sess)} sessions, {S1.BOOT_REPS} replicates, "
          f"{time.time() - t0:.0f} s" + ("" if a.check else f"; {len(surv)} surviving (rule, sign)"), flush=True)
    menu = []
    for q, n in enumerate(S1.RULE_NAMES):
        s = sg[:, q]
        menu.append({"section": "menu", "rule": n, "definition": S1.DEFINITIONS[n], "offers": offers,
                     "ties": int((s == 0).sum()), "tie_share": float((s == 0).mean()) if offers else float("nan"),
                     "long_share_of_sided": float((s > 0).sum() / max(int((s != 0).sum()), 1))})
    arms = [SMOKE_ARM] if a.check else surv

    # ---- stage 2: survivors only
    g1: dict[str, dict] = {}
    extra: list[dict] = []
    g2_rows: list[dict] = []
    g3_rows: list[dict] = []
    verd: list[dict] = []
    g2s: list[dict] = []
    res_ref, ok_ref = A.resolution(t, W["offered_rr"])
    if arms:
        fsl = PS.fv3c_slices(RESULTS_DIR)
        routing = read_result(rd / ROUTING_FILE) if (rd / ROUTING_FILE).is_file() else None
        t0 = time.time()

        def journey(tt: pd.DataFrame, name: str) -> dict[str, Any]:
            """D-518's journey and D-509's slice lines beside (rc150_routing's); not in --check -- the slice lines read
            horizons a 30-day smoke does not have."""
            if a.check:
                return {"journey": [], "lines": [], "lines_hold": None}
            return RT.journey_and_lines(I, tt, days, None, name, fsl, a.workers, starts)

        def make_ref_journey():
            jl = journey(t, REFERENCE)
            return {"journey": jl["journey"], "lines": jl["lines"], "lines_hold": jl["lines_hold"]}

        rj = _cached(resume, "journey reference", make_ref_journey)
        g1[REFERENCE] = {**ref_g1, "every_offered_r_resolves": bool(ok_ref), "slice_lines_hold": rj["lines_hold"]}
        extra += [{**r, "arm": REFERENCE} for r in rj["journey"]] + [{**r, "arm": REFERENCE} for r in rj["lines"]]
        print(f"  G1 {REFERENCE}: journey done ({time.time() - t0:.0f} s)", flush=True)
        for arm in arms:
            name = S1.arm_name(*arm)
            t0 = time.time()

            def make(arm=arm, name=name):
                ta = WF.cell({**W, "coins": arm_coins(W["coins"], keys, sides_grid, arm)}, STOP, days)["trades"]
                res_off, ok_off = A.resolution(ta, W["offered_rr"])
                _, ok_grid = A.resolution(ta, W["rr_grid"])
                r = RT.run_rule(I, name, None, ta, days, n_paths, a.workers, twin=True)
                r.pop("df")
                jl = journey(ta, name)
                row = {"section": "campaign", "arm": name, "rule": arm[0], "sign": int(arm[1]),
                       "candidates": int(len(ta)), "side_rule": f"{arm[0]} {'followed' if arm[1] > 0 else 'faded'}; "
                                                                f"a tie takes P-16's coin side",
                       "cell_trades_sha256": D.trades_hash(ta), **r, **res_off,
                       "every_offered_r_resolves": bool(ok_off), "every_grid_r_resolves": bool(ok_grid),
                       "slice_lines_hold": jl["lines_hold"]}
                return {"row": row, "journey": jl["journey"], "lines": jl["lines"]}

            res = _cached(resume, f"g1 {name}", make)
            g1[name] = res["row"]
            extra += [{**r, "arm": name} for r in res["journey"]] + [{**r, "arm": name} for r in res["lines"]]
            print(f"  G1 {name}: done ({time.time() - t0:.0f} s)", flush=True)
        ref = float(g1[REFERENCE]["growth_on_required"])
        for r in g1.values():
            r["growth_minus_reference"] = float(r["growth_on_required"]) - ref

        # ---- G2: across coin sequences
        dd = L["days"]["date"].astype(str).tolist()
        for s in S1.COIN_SEEDS[:n_coins]:
            t0 = time.time()
            base = rc.coin_table(dd, marks, seed=int(s))

            def make_g2(s=s, base=base, arm=None):
                if arm is None:
                    ts, name = WF.cell({**W, "coins": base}, STOP, days)["trades"], REFERENCE
                else:
                    name = S1.arm_name(*arm)
                    ts = WF.cell({**W, "coins": arm_coins(base, keys, sides_grid, arm)}, STOP, days)["trades"]
                r = RT.run_rule(I, f"g2 {s} {name}", None, ts, days, g2_paths, a.workers)
                r.pop("df")
                return {"section": "g2", "coin_seed": int(s), "arm": name, **r}

            row = _cached(resume, f"g2 {s} {REFERENCE}", make_g2)
            if routing is not None and g2_paths == S1.G2_PATHS:
                prob = _routing_problems(routing, "g2", row, coin_seed=int(s))
                if prob:
                    print(f"REFUSED ({DECISION}): G2's reference on coin {s} is not {ROUTING_FILE}'s {ROUTING_REF} -- "
                          + "; ".join(prob))
                    return 3
            g2_rows.append(row)
            for arm in arms:
                g2_rows.append(_cached(resume, f"g2 {s} {S1.arm_name(*arm)}",
                                       lambda s=s, base=base, arm=arm: make_g2(s, base, arm)))
            print(f"  G2 coin {s}: done ({time.time() - t0:.0f} s)", flush=True)
            del base
        if routing is not None and g2_paths == S1.G2_PATHS:
            idents.append({"section": "identity", "holds": True,
                           "check": f"G2's reference on every coin sequence equals {ROUTING_FILE}'s {ROUTING_REF} row "
                                    "(growth at the bound and point, required bankroll)"})
        g2s = S1.g2_summary(g2_rows, [S1.arm_name(*x) for x in arms], REFERENCE)

        # ---- G3: early then late
        span_g: dict[str, dict[str, float]] = {}
        for span, (lo, hi) in S1.SPANS.items():
            sd = WF.span_days(days, lo, hi)
            for arm in [None] + list(arms):
                name = REFERENCE if arm is None else S1.arm_name(*arm)

                def make_g3(arm=arm, name=name, span=span, sd=sd):
                    coins = W["coins"] if arm is None else arm_coins(W["coins"], keys, sides_grid, arm)
                    ts = WF.cell({**W, "coins": coins}, STOP, sd)["trades"]
                    head = {"section": "g3", "span": span, "span_first": sd[0], "span_last": sd[-1],
                            "sessions": len(sd), "arm": name}
                    if ts is None or not len(ts):          # the span's own cutoff admits no mark (only on a smoke)
                        return {**head, "candidates": 0, "growth_on_required": float("nan"),
                                "note": "no mark admitted on this span alone"}
                    bounds = B.check_bounds(ts, sd, B.rrs(ts))
                    r = RT.run_rule(I, f"g3 {span} {name}", None, ts, sd, n_paths, a.workers, bounds=bounds)
                    r.pop("df")
                    return {"section": "g3", "span": span, "span_first": sd[0], "span_last": sd[-1],
                            "sessions": len(sd), "arm": name, "candidates": int(len(ts)), **r}

                row = _cached(resume, f"g3 {span} {name}", make_g3)
                if arm is None and routing is not None and n_paths == S1.N_PATHS:
                    prob = _routing_problems(routing, "g3", row, span=span)
                    if prob:
                        print(f"REFUSED ({DECISION}): G3's reference on {span} is not {ROUTING_FILE}'s {ROUTING_REF} "
                              "-- " + "; ".join(prob))
                        return 3
                g3_rows.append(row)
                span_g.setdefault(name, {})[span] = float(row["growth_on_required"])
            print(f"  G3 {span}: done ({len(sd)} sessions; candidates "
                  f"{[r['candidates'] for r in g3_rows if r['span'] == span]})", flush=True)
        if routing is not None and n_paths == S1.N_PATHS:
            idents.append({"section": "identity", "holds": True,
                           "check": f"G3's reference on each span equals {ROUTING_FILE}'s {ROUTING_REF} row"})
        g2_by = {r["arm"]: r for r in g2s}
        for arm in arms:
            name = S1.arm_name(*arm)
            verd.append(S1.verdict(name, g1[name]["growth_on_required"], ref, g1[name]["every_offered_r_resolves"],
                                   g2_by.get(name), span_g.get(name, {}), span_g.get(REFERENCE, {})))

    seconds = time.time() - t_all
    if a.check:
        print(f"--check done: identities, stage 1 on {len(sess)} sessions, stage 2's machinery on "
              f"{S1.arm_name(*SMOKE_ARM)} (G1/G3 {n_paths} paths, G2 {g2_paths} paths on {n_coins} coins); no lift "
              f"printed; nothing written. {seconds:.0f} s")
        return 0
    boot_row = {"section": "bootstrap", "reps": S1.BOOT_REPS, "mean_block": S1.BOOT_BLOCK, "seed": S1.BOOT_SEED,
                "statistic": "studentised mean lift (mean / bootstrap sd), two-sided max over every rule and R",
                "fwer": S1.ALPHA, "critical_t": test["crit"], "hypotheses": int(len(hyp)), "sessions": len(sess),
                "offers": offers, "survivors": int(hyp["survives"].sum()), "surviving_arms": len(surv),
                "bh_q": S1.BH_Q, "bh_rejections": int(np.sum(test["bh"])),
                **{f"max_abs_t_{k}": v for k, v in test["max_quantiles"].items()}}
    decl_row = {"section": "declaration", "check": f"config/search_program.yaml sha256 {decl['sha256']} (D-578), "
                                                   "batch S1 read as text; every constant agrees", "holds": True}
    surv_rows = hyp[hyp["survives"].astype(bool)].assign(section="survivors")
    out = pd.concat([pd.DataFrame([decl_row] + menu + idents), hyp.assign(section="lift"), pd.DataFrame([boot_row]),
                     surv_rows, pd.DataFrame(list(g1.values()) + extra + g2_rows + g2s + g3_rows + verd)],
                    ignore_index=True)
    out.insert(1, "reading", READING)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for n in S1.RULE_NAMES:
        counter.record(prereg_id=FAMILY_ID, seed=S1.BOOT_SEED, exploratory=True,
                       params={"study": "D-578 batch S1, the sided coin", "cell": CELL, "rule": n,
                               "definition": S1.DEFINITIONS[n], "offered_r": list(S1.OFFERED_R),
                               "fwer": S1.ALPHA, "boot_seed": S1.BOOT_SEED},
                       label=f"D-578's S1: {n} (follow and fade, one two-sided test)")
    write_result(out, RESULT, script=SCRIPT, seed=S1.BOOT_SEED, exploratory=True, results_dir=results_dir,
                 variant_count=S1.N_VARIANTS,
                 parameters={"decision": DECISION, "batch": S1.BATCH, "declaration_sha256": decl["sha256"],
                             "cell": CELL, "stop_ticks": STOP, "rules": list(S1.RULE_NAMES),
                             "offered_r": list(S1.OFFERED_R), "boot_reps": S1.BOOT_REPS, "boot_block": S1.BOOT_BLOCK,
                             "boot_seed": S1.BOOT_SEED, "fwer": S1.ALPHA, "bh_q": S1.BH_Q,
                             "sessions": "the cell's walked development days (normal and report days)",
                             "campaign_seed": S.SEED, "coin_seed": rc.COIN_SEED, "g1_paths": S1.N_PATHS,
                             "g2_coin_seeds": [S1.COIN_SEEDS[0], S1.COIN_SEEDS[-1]], "g2_paths": S1.G2_PATHS,
                             "g2_wins_needed": S1.G2_WINS, "g3_spans": {k: list(v) for k, v in S1.SPANS.items()},
                             "margin": S1.MARGIN, "arms": [S1.arm_name(*x) for x in surv],
                             "cell_trades_sha256": h, "reference_resolution": res_ref,
                             "fv3c_slices": "results/customer_slices.csv (sha256 pinned), read, never rerun",
                             "workers": int(a.workers), "seconds": round(seconds, 1)},
                 notes={"status": READING, "selection": "stage 1's family-wise survivors alone run stage 2; BH beside, "
                                                        "never selecting; a candidate needs all four D-578 (2) guards"},
                 description="EXPLORATORY (D-578, batch S1): P-16's cell with each offer's side from one of 15 declared "
                             "bar rules (momentum, since the open, prior session, range position, latest breakout) "
                             "instead of the coin; the per-offer lift over the coin twin at every offered R, a "
                             "studentised max-statistic block bootstrap family-wise at 0.025 (BH at 10 % beside), and "
                             "for survivors P-16's paired campaign with D-578's four guards.")
    if verd:
        print(pd.DataFrame(verd).to_string(index=False))
    print(f"written: {RESULT}.csv ({len(surv)} surviving arms; {seconds:.0f} s)")
    return 0


def _routing_problems(routing: pd.DataFrame, section: str, row: dict, **match) -> list[str]:
    """Identity (iii): this study's reference row against rc150_routing.csv's R0 row of the same section and coin or
    span (growth at the bound and point, required bankroll; exact to 1e-9)."""
    r = routing[(routing["section"].astype(str) == section) & (routing["rule"].astype(str) == ROUTING_REF)]
    for k, v in match.items():
        col = r[k]
        r = r[(col.astype(float).astype(int) == int(v))] if k == "coin_seed" else r[col.astype(str) == str(v)]
    if len(r) != 1:
        return [f"{len(r)} {ROUTING_REF} rows for {match}"]
    out = []
    for c in IDENT_COLS:
        mine, want = float(row[c]), float(r.iloc[0][c])
        if not np.isclose(mine, want, rtol=0, atol=1e-9):
            out.append(f"{c}: {mine!r} against {want!r}")
    return out


if __name__ == "__main__":
    raise SystemExit(main())
