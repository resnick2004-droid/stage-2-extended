"""EXPLORATORY (D-578, D-610): batch S4 of the rolling model search -- the sided coin with each offer's side from the
Point & Figure chart. S3's design exactly (`scripts/s3_event_kinds.py`, D-586, D-587): P-16's cell with each offer's
side taken from one of 10 declared P&F rules (the most recent catapult / plain triple top at five boxes, D-607's
engine) read at t - 5 minutes (D-589) instead of the coin; a family-wise per-offer lift test (stage 1) and, for its
survivors only, P-16's paired campaign with D-578's four guards (stage 2).

    python scripts/s4_pf_side.py --check                 # every identity on every day (the cell = P-16's by content
                                                         #   hash, the both-side walks, the setups = pf_fit_setups.csv,
                                                         #   the lag, the side table set to P-16's coin = P-16's hash),
                                                         #   then a smoke on 30 walked days (the first 15 of each
                                                         #   span): stage 1's machinery, stage 2's on one arm at 4
                                                         #   paths, 2 coins; no lift printed; nothing written
    python scripts/s4_pf_side.py --workers 1             # the reading (a clean checkout, D-474)

**The declaration (identity (c))** (`config/search_program_s4.yaml`, D-610) is read (valid YAML), its sha256 of the LF
text pinned (`s4_pf_side.DECLARATION_SHA256`), the program file's pin (`s1_sided_coin.DECLARATION_SHA256`) checked, and
every constant checked against its words before anything is built; a difference refuses.

**The cell** (P-16, D-544, D-547): `rc_stop_walkforward.walk_stop` / `cell` at 150 ticks on every development day --
`rc_s150_all` in `rc_width_screen.csv`, the news-safe build, whose content hash is `rc150_dev_test.TRADES_SHA256`.

**Identities first, refusing:** (a) the cell's count against `rc_width_screen.csv`'s `rc_s150_all` and its content hash
against `rc150_dev_test.TRADES_SHA256`; the side table set to P-16's own `coin_table` (seed 20261102) through
`campaign_coins` rebuilds the same content hash; the both-side walks carry the cell's exact offers and its settlement;
(b) the engine's setups at boxes 2.5, 5, 7.5 and 10 points are `results/pf_fit_setups.csv`'s (pinned by its manifest's
sha256) fixed-reading catapult rows and plain rows -- counts per kind and, row by row, date, trigger end slot, side,
kind and box; the bars are the ones pf_fit read (count and the store's sha256) and the chart restarts at every contract
change; the lag: the side at mark t is the lag-0 side at t - 5 (the previous mark), marks 0 and 5 tie; (c) the
declaration. On the full run also S3's: the reference at seed 20261131, 500 paths, reproduces `rc_width_screen.csv`'s
`rc_s150_all` row; stage 2's reference rows across coins and on the two spans equal `rc150_routing.csv`'s R0 rows.

**The sides** (`propedge.research.s4_pf_side`, whose docstring states every reading): the development bars read once
(`scripts/pf_fit.load`, purpose development: the window guard), one `pnf.scan` per box over the whole span; each rule's
setups mapped to (trading day, trigger end slot); at mark t the most recent setup that day ending at or before t - 5.

**Stage 1 / stage 2:** S1's, at alpha 0.05 / 20, bootstrap seed 20261712 (block 21, 2,000 replicates), BH at 10 % beside;
stage 2 for survivors only: G1 paired (campaign seed 20261131, 500 paths, the twin, journey and slice lines beside), G2
(50 coin sequences 20261600 + i, 200 paths; a tie takes the sequence's coin), G3 (2020-2023 and 2024-2026-07-16 alone);
D-578 (2)'s guards. With no survivor: stage 1 and the reference's paired row only.

**Resume** (D-540, `rc_robust.Resume`): each finished engine run kept outside the checkout, keyed by commit and counts;
`--no-resume`, `--resume-dir`; off in --check.

Writes `results/s4_pf_side.csv` (EXPLORATORY; sections declaration, menu, identity, lift, bootstrap, survivors,
campaign, journey, slice_lines, g2, g2_summary, g3, verdict) with its manifest; 10 variants under `D-578:S4`.
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
import s1_sided_coin as S1S  # noqa: E402  (S1's script: its identity (iii) check, reused)
from propedge.research import s4_pf_side as S4  # noqa: E402

SCRIPT = "scripts/s4_pf_side.py"
DECISION = S4.DECISION
RESULT = "s4_pf_side"
FAMILY_ID = S4.FAMILY_ID
CELL = "rc_s150_all"
STOP = S4.STOP_TICKS
REFERENCE = "P16_coin"
SMOKE_ARM = ("pfc5", 1)                    # --check only: stage 2's machinery on one arm (a smoke's survivors mean nothing)
CHECK_DAYS = 30
ROUTING_FILE = S1S.ROUTING_FILE            # identity (iii): its R0 rows (D-576)
ROUTING_REF = S1S.ROUTING_REF
READING = ("EXPLORATORY (D-578, D-610): batch S4, the sided coin with the side from the P&F chart (the most recent "
           "catapult / plain triple top at five boxes, read at t - 5) -- a family-wise per-offer lift test at 0.05 / 20 "
           "and, for its survivors only, P-16's paired campaign with D-578's four guards; selects nothing by itself")
_routing_problems = S1S._routing_problems


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


def grid_keys(table: dict[str, np.ndarray], marks: list[int]) -> tuple[list[tuple[str, int]], np.ndarray]:
    """Every (date, mark) the side table holds, in date then mark order, with its (n, rules) sides (S3's)."""
    keys = [(d, int(m)) for d in sorted(table) for m in marks]
    sides = np.concatenate([table[d] for d in sorted(table)], axis=0) if table else np.zeros((0, len(S4.RULE_NAMES)))
    return keys, sides


# ------------------------------------------------------------------------------------------------ the sides


def pf_setups(results_dir: Path) -> tuple[dict[float, pd.DataFrame], list[dict], list[str], dict[str, Any]]:
    """({box: `s4_pf_side.scan_events`}, identity rows, problems, provenance): the development bars as pf_fit read them,
    one `pnf.scan` per box over the whole span, and identity (b) against `results/pf_fit_setups.csv`."""
    import pf_fit as PFS

    from propedge.data.bars import manifest
    from propedge.reporting.results import read_manifest, read_result
    from propedge.research import pf_fit as PF
    from propedge.research import pnf

    rows: list[dict] = []
    bad: list[str] = []

    def ident(check: str, problems: list[str]) -> None:
        rows.append({"section": "identity", "holds": not problems, "check": check, "problems": "; ".join(problems)})
        print(("identity (b) HOLDS: " if not problems else "identity (b) FAILS: ") + check
              + ("" if not problems else " -- " + "; ".join(problems)), flush=True)
        bad.extend(problems)

    path = Path(results_dir) / S4.PF_SETUPS_FILE
    fm = read_manifest(path)
    file_rows = read_result(path)                  # the file's own sha256 against its manifest
    ident(f"results/{S4.PF_SETUPS_FILE} is the file D-609 read (manifest sha256 {S4.PF_SETUPS_SHA256[:16]}, the file "
          "matching its manifest)",
          [] if fm.sha256 == S4.PF_SETUPS_SHA256 else [f"its manifest's sha256 is {str(fm.sha256)[:16]}"])
    t0 = time.time()
    bars = PFS.load(PF.DEV_START, PF.DEV_END)
    m = manifest(PF.MARKET) or {}
    want_n = int(fm.parameters.get("bars_read", -1))
    want_store = fm.parameters.get("bar_store_sha256")
    prob = []
    if len(bars) != want_n:
        prob.append(f"{len(bars)} bars read against pf_fit's {want_n}")
    if m.get("parquet_sha256") != want_store:
        prob.append(f"the bar store's sha256 {str(m.get('parquet_sha256'))[:16]} is not pf_fit's {str(want_store)[:16]}")
    if len(bars) and str(bars["day"].max()) > PF.DEV_END:
        prob.append(f"a bar after {PF.DEV_END}")
    ident(f"the bars are pf_fit's: {PF.DEV_START} .. {PF.DEV_END} through the window guard (purpose development), "
          f"{len(bars)} bars, the store's sha256 as pf_fit's manifest records it", prob)
    con = bars["contract"].astype(str).to_numpy()
    changes = [i for i in range(1, len(con)) if con[i] != con[i - 1]]
    hi, lo, cl = bars["high"].to_numpy(), bars["low"].to_numpy(), bars["close"].to_numpy()
    ev: dict[float, pd.DataFrame] = {}
    restart_bad = []
    for box in S4.BOXES:
        tb = time.time()
        res = pnf.scan(hi, lo, cl, con, box=box)
        if res["restarts"] != changes:
            restart_bad.append(f"box {box:g}: {len(res['restarts'])} restarts, not the {len(changes)} contract changes")
        ev[box] = S4.scan_events(bars, box, result=res)
        print(f"  box {box:g}: the scan, {time.time() - tb:.0f} s", flush=True)
        del res
    ident(f"the chart restarts at every contract change ({len(changes)}) on every box", restart_bad)
    ident(f"the engine's fixed-reading catapults (r7_low) and plain triples at boxes {list(S4.PF_FIT_BOXES)} are "
          f"results/{S4.PF_SETUPS_FILE}'s: counts per kind and, row by row in order, {', '.join(S4.IDENT_FIELDS)}",
          S4.setups_problems(file_rows, ev))
    prov = {"bars_read": int(len(bars)), "bar_store_sha256": m.get("parquet_sha256"), "restarts": len(changes),
            "pf_fit_setups_sha256": fm.sha256, "scan_seconds": round(time.time() - t0, 1),
            "_bar_days": set(bars["day"].astype(str).unique())}
    del bars, file_rows
    return ev, rows, bad, prov


def lag_problems(events_by_rule: dict[str, pd.DataFrame], table: dict[str, np.ndarray], marks: list[int]) -> list[str]:
    """The lag, refusing: on every day the L = 5 side at mark t equals the L = 0 side at t - 5 (the previous mark on
    P-16's five-minute grid) and marks 0 and 5 tie -- so the table is not the L = 0 table by mistake. The rules are
    `events_by_rule`'s, in its order (the table's columns)."""
    days = sorted(table)
    zero = S4.side_table(events_by_rule, days, marks, lag=0, rules=list(events_by_rule))
    M = np.asarray(marks)
    if not (len(M) > 2 and M[0] == 0 and np.all(np.diff(M) == S4.LATENCY_MIN)):
        return ["the marks are not a five-minute grid from 0"]
    out = []
    for d in days:
        a, z = table[d], zero[d]
        if np.any(a[:2] != 0):
            out.append(f"{d}: mark 0 or 5 is not a tie")
        elif not np.array_equal(a[1:], z[:-1]):
            out.append(f"{d}: the side at t is not the lag-0 side at t - 5")
        if len(out) > 3:
            break
    return out


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="every identity, then a smoke: stage 1 on the first days, "
                                                         "stage 2's machinery on one arm at a few paths; nothing written")
    ap.add_argument("--days", type=int, default=None,
                    help=f"--check: the smoke's walked days, the first N/2 of each span ({CHECK_DAYS})")
    ap.add_argument("--paths", type=int, default=None, help="--check: G1 and G3 paths (4)")
    ap.add_argument("--g2-paths", type=int, default=None, help="--check: G2 paths (4)")
    ap.add_argument("--coins", type=int, default=None, help="--check: the first coin sequences of G2 (2)")
    ap.add_argument("--starts", type=int, default=None, help="--check: the journey's first starts (6)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true", help="D-540: neither keep nor read finished runs' rows")
    ap.add_argument("--resume-dir", default=None, help="D-540: where finished runs' rows are kept (outside the checkout)")
    a = ap.parse_args(argv)
    if not a.check and any(x is not None for x in (a.days, a.paths, a.g2_paths, a.coins, a.starts)):
        print(f"REFUSED ({DECISION}): the reading runs every day, {S4.N_PATHS} / {S4.G2_PATHS} paths, "
              f"{len(S4.COIN_SEEDS)} coins and every start; a smaller run is --check (writes nothing).")
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
    from propedge.reporting.results import read_result, write_result
    from propedge.research import resolved_coin as rc

    n_paths = (a.paths or 4) if a.check else S4.N_PATHS
    g2_paths = (a.g2_paths or 4) if a.check else S4.G2_PATHS
    n_coins = (a.coins or 2) if a.check else len(S4.COIN_SEEDS)
    starts = (a.starts or 6) if a.check else None
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()

    # ---- identity (c): the declaration and the constants it fixes
    decl = S4.declaration()
    bad = S4.declaration_problems(decl) + S4.shared_problems()
    fixed = {"campaign seed": (S.SEED, S4.CAMPAIGN_SEED), "paths": (S.N_PATHS, S4.N_PATHS),
             "coin seeds": (tuple(RT.COIN_SEEDS), tuple(S4.COIN_SEEDS)), "g2 paths": (RT.G2_PATHS, S4.G2_PATHS),
             "g2 wins": (RT.G2_WINS, S4.G2_WINS), "margin": (RT.MARGIN, S4.MARGIN),
             "spans": ({k: tuple(v) for k, v in WF.SPANS.items()}, {k: tuple(v) for k, v in S4.SPANS.items()}),
             "stop": (RT.STOP, S4.STOP_TICKS), "cell": (RT.CELL, CELL)}
    bad += [f"{k}: the engine's {v[0]!r} against S4's {v[1]!r}" for k, v in fixed.items() if v[0] != v[1]]
    if bad:
        print(f"REFUSED ({DECISION}): the build is not D-610's declaration -- " + "; ".join(bad))
        return 2
    print(f"identity (c) HOLDS: the declaration {decl['path']} (sha256 {decl['sha256'][:16]}); {len(S4.RULE_NAMES)} "
          f"rules, {S4.N_HYPOTHESES} hypotheses, latency {S4.LATENCY_MIN} min", flush=True)
    idents: list[dict] = []

    # ---- the cell and identity (a), on every day in both modes (the walk is under a minute)
    srow = PS.screen_row(RESULTS_DIR)
    print("P-14's inputs, the no-closure plan and the 37.5-point walk...", flush=True)
    I = S.inputs()
    L = I["L"]
    offered = tuple(sorted(float(R) for R in zd.policy_rrs(I["plan"])))
    if offered != tuple(float(x) for x in S4.OFFERED_R):
        print(f"REFUSED ({DECISION}): the table offers R {offered}, not D-610's {S4.OFFERED_R}.")
        return 2
    W = WF.walk_stop(I, STOP)
    days = list(W["days"])
    t = WF.cell(W, STOP, days)["trades"]
    h = D.trades_hash(t)
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
    print(f"identity (a) HOLDS: the cell = P-16's {CELL} ({len(t)} candidates; content hash {h[:16]})", flush=True)
    marks = rc.marks()
    kinds = dict(W["kinds"])
    walked = [d for d in days if kinds.get(d) in m0.WALK_DAY_KINDS]
    # the both-side walks: every coin long, every coin short -- the cell's offers and P-16's own settlement
    tk = list(zip(t["date"].astype(str), t["decision_slot_minutes"].astype(int)))
    coin = np.array([W["coins"][k] for k in tk], dtype=int)
    rcols = [f"r_{R:g}" for R in S4.OFFERED_R]
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
    print("identity (a) HOLDS: the both-side walks carry the cell's offers and settlement", flush=True)

    # ---- the setups (identity (b)) and the sides
    ev, rows_b, bad, prov = pf_setups(RESULTS_DIR)
    if bad:
        print(f"REFUSED ({DECISION}): identity (b) fails -- " + "; ".join(bad))
        return 3
    idents += rows_b
    bar_days = prov.pop("_bar_days")
    missing = [d for d in walked if d not in bar_days]
    if missing:                                    # S3's refusal: a walked day with no bars would tie all day unseen
        print(f"REFUSED ({DECISION}): {len(missing)} walked day(s) not in the bars read, e.g. {missing[:3]}")
        return 3
    t0 = time.time()
    events_by_rule = {n: S4.rule_events(ev[box], fam) for n, fam, box in S4.RULES}
    table = S4.side_table(events_by_rule, walked, marks)
    lp = lag_problems(events_by_rule, table, marks)
    if lp:
        print(f"REFUSED ({DECISION}): the lag is not t - {S4.LATENCY_MIN} -- " + "; ".join(lp))
        return 3
    idents.append({"section": "identity", "holds": True,
                   "check": f"the lag: on every walked day the side at mark t (setups ending at or before t - "
                            f"{S4.LATENCY_MIN} that trading day) equals the lag-0 side at t - {S4.LATENCY_MIN} (the "
                            "previous mark); marks 0 and 5 tie"})
    print(f"identity (b) HOLDS: the lag -- the side at t is the lag-0 side at t - {S4.LATENCY_MIN}; marks 0 and 5 tie",
          flush=True)
    keys, sides_grid = grid_keys(table, marks)
    print(f"the sides: {len(S4.RULE_NAMES)} rules on {len(table)} walked days x {len(marks)} marks, "
          f"{time.time() - t0:.0f} s", flush=True)
    hc = D.trades_hash(WF.cell({**W, "coins": S4.campaign_coins(W["coins"], keys, [W["coins"][k] for k in keys])},
                               STOP, days)["trades"])
    if hc != h or hc != R150.TRADES_SHA256:
        print(f"REFUSED ({DECISION}): the side table set to P-16's coin rebuilds {hc[:16]}, not P-16's {h[:16]}.")
        return 3
    idents.append({"section": "identity", "holds": True,
                   "check": f"every rule's side replaced by P-16's coin_table (seed {rc.COIN_SEED}) through "
                            "campaign_coins rebuilds the cell's content hash = rc150_dev_test.TRADES_SHA256: stage 2's "
                            "construction is P-16's"})
    print("identity (a) HOLDS: every side replaced by P-16's coin rebuilds P-16's content hash", flush=True)
    mi = {int(m): i for i, m in enumerate(marks)}
    sides = np.zeros((len(tk), len(S4.RULE_NAMES)), dtype=np.int8)
    for i, (d, m) in enumerate(tk):
        if d in table:
            sides[i] = table[d][mi[int(m)]]

    # ---- the smoke's days (--check) or every day
    if a.check:
        half = max(int(a.days or CHECK_DAYS) // 2, 1)
        pick = set(d for lo, hi in S4.SPANS.values() for d in WF.span_days(walked, lo, hi)[:half])
        sdays = [d for d in days if d in pick]
        t_s = WF.cell(W, STOP, sdays)["trades"]
        print(f"--check: the smoke on {len(sdays)} walked days ({len(t_s)} candidates)", flush=True)
    else:
        sdays, t_s = days, t
    sset = set(sdays)
    in_side = np.array([d in table and d in sset for d, _ in tk])

    resume = None
    if not a.check and not a.no_resume:
        import subprocess

        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = Resume(folder, f"{commit}_{n_paths}_{g2_paths}")

    # ---- the reference's paired run (S3's identity (ii) at 500 paths)
    t0 = time.time()

    def make_ref():
        r = RT.run_rule(I, REFERENCE, None, t_s, sdays, n_paths, a.workers, twin=True)
        df = r.pop("df")
        if n_paths == S4.N_PATHS and not a.check:
            prob = PS.growth_problems(df, srow)
            if prob:
                raise SystemExit(f"REFUSED ({DECISION}): the reference is not {PS.SCREEN_FILE}'s {CELL} -- "
                                 + "; ".join(prob))
        return {"section": "campaign", "arm": REFERENCE, "rule": "", "sign": 0, "candidates": int(len(t_s)),
                "side_rule": f"P-16's coin_table (seed {rc.COIN_SEED})", **r}

    ref_g1 = _cached(resume, "g1 reference", make_ref)
    if n_paths == S4.N_PATHS and not a.check:
        idents.append({"section": "identity", "holds": True,
                       "check": f"the reference (P-16's coin, the current router) at seed {S.SEED}, {S4.N_PATHS} paths, "
                                f"reproduces results/{PS.SCREEN_FILE}'s {CELL} growth at the bound and point and its "
                                "required bankroll"})
        print(f"identity (ii) HOLDS: the reference at {S4.N_PATHS} paths = {PS.SCREEN_FILE}'s {CELL} "
              f"({time.time() - t0:.0f} s)", flush=True)
    else:
        print(f"identity (ii): not comparable on the smoke ({n_paths} paths, {len(sdays)} days); the reference ran "
              f"({time.time() - t0:.0f} s)", flush=True)

    # ---- stage 1: the lift
    t0 = time.time()
    sess = [d for d in walked if d in table and d in sset]
    si = {d: i for i, d in enumerate(sess)}
    sub = in_side
    rl, rs, sg = r_long[sub], r_short[sub], sides[sub]
    di = np.array([si[d] for (d, _), k in zip(tk, sub) if k], dtype=np.int64)
    nR = len(S4.OFFERED_R)
    H = len(S4.RULE_NAMES) * nR
    day_sum, day_n = np.zeros((len(sess), H)), np.zeros((len(sess), H))
    side_r = np.full(H, np.nan)
    for q in range(len(S4.RULE_NAMES)):                    # one rule at a time: (offers, 6) in memory, not (offers, 60)
        cols = slice(q * nR, (q + 1) * nR)
        lq = S4.lift_matrix(rl, rs, sg[:, [q]])
        day_sum[:, cols], day_n[:, cols] = S4.accumulate(di, lq, len(sess))
        s = sg[:, q]
        if (s != 0).any():
            side_r[cols] = np.where(s[s != 0, None] > 0, rl[s != 0], rs[s != 0]).mean(axis=0)
        del lq
    test = S4.stage1(day_sum, day_n)
    offers = int(sub.sum())
    ties = (sg == 0).sum(axis=0)
    hyp = S4.hypotheses().assign(
        offers=offers, ties=np.repeat(ties, nR), tie_share=np.repeat(ties / max(offers, 1), nR), trades=test["trades"],
        mean_lift=test["mean"], sd_boot=test["sd"], t_boot=test["t"], p_boot=test["p"], survives=test["survives"],
        bh_reject=test["bh"], side_sign=np.where(test["mean"] > 0, 1, -1),
        winning_side=np.where(test["mean"] > 0, "follow", "fade"), mean_r_rule_side=side_r)
    surv = S4.survivors(hyp)
    print(f"stage 1: {len(hyp)} hypotheses on {offers} offers over {len(sess)} sessions, {S4.BOOT_REPS} replicates, "
          f"{time.time() - t0:.0f} s" + ("" if a.check else f"; {len(surv)} surviving (rule, sign)"), flush=True)
    wset = set(sess)
    menu = []
    for q, (n, fam, box) in enumerate(S4.RULES):
        s = sg[:, q]
        e = events_by_rule[n]
        ew = e[e["date"].astype(str).isin(wset).to_numpy()]
        slot = ew["trigger_end_slot"].to_numpy()
        menu.append({"section": "menu", "rule": n, "definition": S4.DEFINITIONS[n], "family": fam, "box_points": box,
                     "offers": offers, "ties": int((s == 0).sum()),
                     "tie_share": float((s == 0).mean()) if offers else float("nan"),
                     "long_share_of_sided": float((s > 0).sum() / max(int((s != 0).sum()), 1)),
                     "setups_walked_sessions": int(len(ew)), "setups_in_hours": int((slot < 1330).sum()),
                     "setups_readable_by_last_mark": int((slot <= S4.LAST_MARK_SLOT - S4.LATENCY_MIN).sum()),
                     "setups_long_share": float((ew["side"] > 0).mean()) if len(ew) else float("nan")})
    arms = [SMOKE_ARM] if a.check else surv

    # ---- stage 2: survivors only
    g1: dict[str, dict] = {}
    extra: list[dict] = []
    g2_rows: list[dict] = []
    g3_rows: list[dict] = []
    verd: list[dict] = []
    g2s: list[dict] = []
    res_ref, ok_ref = A.resolution(t_s, W["offered_rr"])
    if arms:
        fsl = PS.fv3c_slices(RESULTS_DIR)
        routing = read_result(rd / ROUTING_FILE) if (rd / ROUTING_FILE).is_file() else None
        t0 = time.time()

        def journey(tt: pd.DataFrame, name: str) -> dict[str, Any]:
            """D-518's journey and D-509's slice lines beside (rc150_routing's); not in --check."""
            if a.check:
                return {"journey": [], "lines": [], "lines_hold": None}
            return RT.journey_and_lines(I, tt, sdays, None, name, fsl, a.workers, starts)

        def make_ref_journey():
            jl = journey(t_s, REFERENCE)
            return {"journey": jl["journey"], "lines": jl["lines"], "lines_hold": jl["lines_hold"]}

        rj = _cached(resume, "journey reference", make_ref_journey)
        g1[REFERENCE] = {**ref_g1, "every_offered_r_resolves": bool(ok_ref), "slice_lines_hold": rj["lines_hold"]}
        extra += [{**r, "arm": REFERENCE} for r in rj["journey"]] + [{**r, "arm": REFERENCE} for r in rj["lines"]]
        print(f"  G1 {REFERENCE}: journey done ({time.time() - t0:.0f} s)", flush=True)
        for arm in arms:
            name = S4.arm_name(*arm)
            t0 = time.time()

            def make(arm=arm, name=name):
                ta = WF.cell({**W, "coins": arm_coins(W["coins"], keys, sides_grid, arm)}, STOP, sdays)["trades"]
                res_off, ok_off = A.resolution(ta, W["offered_rr"])
                _, ok_grid = A.resolution(ta, W["rr_grid"])
                r = RT.run_rule(I, name, None, ta, sdays, n_paths, a.workers, twin=True)
                r.pop("df")
                jl = journey(ta, name)
                row = {"section": "campaign", "arm": name, "rule": arm[0], "sign": int(arm[1]),
                       "candidates": int(len(ta)), "side_rule": f"{arm[0]} {'followed' if arm[1] > 0 else 'faded'} at "
                                                                f"t - {S4.LATENCY_MIN}; a tie takes P-16's coin side",
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
        for s in S4.COIN_SEEDS[:n_coins]:
            t0 = time.time()
            base = rc.coin_table(dd, marks, seed=int(s))

            def make_g2(s=s, base=base, arm=None):
                if arm is None:
                    ts, name = WF.cell({**W, "coins": base}, STOP, sdays)["trades"], REFERENCE
                else:
                    name = S4.arm_name(*arm)
                    ts = WF.cell({**W, "coins": arm_coins(base, keys, sides_grid, arm)}, STOP, sdays)["trades"]
                r = RT.run_rule(I, f"g2 {s} {name}", None, ts, sdays, g2_paths, a.workers)
                r.pop("df")
                return {"section": "g2", "coin_seed": int(s), "arm": name, **r}

            row = _cached(resume, f"g2 {s} {REFERENCE}", make_g2)
            if routing is not None and g2_paths == S4.G2_PATHS and not a.check:
                prob = _routing_problems(routing, "g2", row, coin_seed=int(s))
                if prob:
                    print(f"REFUSED ({DECISION}): G2's reference on coin {s} is not {ROUTING_FILE}'s {ROUTING_REF} -- "
                          + "; ".join(prob))
                    return 3
            g2_rows.append(row)
            for arm in arms:
                g2_rows.append(_cached(resume, f"g2 {s} {S4.arm_name(*arm)}",
                                       lambda s=s, base=base, arm=arm: make_g2(s, base, arm)))
            print(f"  G2 coin {s}: done ({time.time() - t0:.0f} s)", flush=True)
            del base
        if routing is not None and g2_paths == S4.G2_PATHS and not a.check:
            idents.append({"section": "identity", "holds": True,
                           "check": f"G2's reference on every coin sequence equals {ROUTING_FILE}'s {ROUTING_REF} row "
                                    "(growth at the bound and point, required bankroll)"})
        g2s = S4.g2_summary(g2_rows, [S4.arm_name(*x) for x in arms], REFERENCE)

        # ---- G3: early then late
        span_g: dict[str, dict[str, float]] = {}
        for span, (lo, hi) in S4.SPANS.items():
            sd = WF.span_days(sdays, lo, hi)
            for arm in [None] + list(arms):
                name = REFERENCE if arm is None else S4.arm_name(*arm)

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
                    return {**head, "candidates": int(len(ts)), **r}

                row = _cached(resume, f"g3 {span} {name}", make_g3)
                if arm is None and routing is not None and n_paths == S4.N_PATHS and not a.check:
                    prob = _routing_problems(routing, "g3", row, span=span)
                    if prob:
                        print(f"REFUSED ({DECISION}): G3's reference on {span} is not {ROUTING_FILE}'s {ROUTING_REF} "
                              "-- " + "; ".join(prob))
                        return 3
                g3_rows.append(row)
                span_g.setdefault(name, {})[span] = float(row["growth_on_required"])
            print(f"  G3 {span}: done ({len(sd)} sessions; candidates "
                  f"{[r['candidates'] for r in g3_rows if r['span'] == span]})", flush=True)
        if routing is not None and n_paths == S4.N_PATHS and not a.check:
            idents.append({"section": "identity", "holds": True,
                           "check": f"G3's reference on each span equals {ROUTING_FILE}'s {ROUTING_REF} row"})
        g2_by = {r["arm"]: r for r in g2s}
        for arm in arms:
            name = S4.arm_name(*arm)
            verd.append(S4.verdict(name, g1[name]["growth_on_required"], ref, g1[name]["every_offered_r_resolves"],
                                   g2_by.get(name), span_g.get(name, {}), span_g.get(REFERENCE, {})))
    else:                                          # D-610: with no survivor, stage 1 and the reference's paired row
        g1[REFERENCE] = {**ref_g1, "every_offered_r_resolves": bool(ok_ref)}

    seconds = time.time() - t_all
    if a.check:
        print(f"--check done: every identity on every day; the smoke -- stage 1 on {len(sess)} sessions, stage 2's "
              f"machinery on {S4.arm_name(*SMOKE_ARM)} (G1/G3 {n_paths} paths, G2 {g2_paths} paths on {n_coins} "
              f"coins); no lift printed; nothing written. {seconds:.0f} s")
        return 0
    boot_row = {"section": "bootstrap", "reps": S4.BOOT_REPS, "mean_block": S4.BOOT_BLOCK, "seed": S4.BOOT_SEED,
                "statistic": "studentised mean lift (mean / bootstrap sd), two-sided max over every rule and R",
                "fwer": S4.ALPHA, "critical_t": test["crit"], "hypotheses": int(len(hyp)), "sessions": len(sess),
                "offers": offers, "survivors": int(hyp["survives"].sum()), "surviving_arms": len(surv),
                "bh_q": S4.BH_Q, "bh_rejections": int(np.sum(test["bh"])),
                **{f"max_abs_t_{k}": v for k, v in test["max_quantiles"].items()}}
    decl_row = {"section": "declaration", "holds": True,
                "check": f"config/search_program_s4.yaml sha256 {decl['sha256']} (D-610; LF text), the program file's "
                         f"pin {decl['program_sha256'][:16]} (D-578); every constant agrees"}
    surv_rows = hyp[hyp["survives"].astype(bool)].assign(section="survivors")
    out = pd.concat([pd.DataFrame([decl_row] + menu + idents), hyp.assign(section="lift"), pd.DataFrame([boot_row]),
                     surv_rows, pd.DataFrame(list(g1.values()) + extra + g2_rows + g2s + g3_rows + verd)],
                    ignore_index=True)
    out.insert(1, "reading", READING)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for n in S4.RULE_NAMES:
        counter.record(prereg_id=FAMILY_ID, seed=S4.BOOT_SEED, exploratory=True,
                       params={"study": "D-578 batch S4 (D-610), the sided coin with the P&F side", "cell": CELL,
                               "rule": n, "definition": S4.DEFINITIONS[n], "latency_minutes": S4.LATENCY_MIN,
                               "offered_r": list(S4.OFFERED_R), "fwer": S4.ALPHA, "boot_seed": S4.BOOT_SEED},
                       label=f"D-578's S4: {n} (follow and fade, one two-sided test; read at t - {S4.LATENCY_MIN})")
    write_result(out, RESULT, script=SCRIPT, seed=S4.BOOT_SEED, exploratory=True, results_dir=results_dir,
                 variant_count=S4.N_VARIANTS,
                 parameters={"decision": DECISION, "declared_by": S4.DECLARED_BY, "batch": S4.BATCH,
                             "declaration_sha256": decl["sha256"], "program_sha256": decl["program_sha256"],
                             "cell": CELL, "stop_ticks": STOP, "rules": list(S4.RULE_NAMES),
                             "boxes_points": list(S4.BOXES), "latency_minutes": S4.LATENCY_MIN,
                             "catapult_reading": S4.FIXED_READING, **prov,
                             "offered_r": list(S4.OFFERED_R), "boot_reps": S4.BOOT_REPS, "boot_block": S4.BOOT_BLOCK,
                             "boot_seed": S4.BOOT_SEED, "fwer": S4.ALPHA, "bh_q": S4.BH_Q,
                             "sessions": "the cell's walked development days (normal and report days)",
                             "campaign_seed": S.SEED, "coin_seed": rc.COIN_SEED, "g1_paths": S4.N_PATHS,
                             "g2_coin_seeds": [S4.COIN_SEEDS[0], S4.COIN_SEEDS[-1]], "g2_paths": S4.G2_PATHS,
                             "g2_wins_needed": S4.G2_WINS, "g3_spans": {k: list(v) for k, v in S4.SPANS.items()},
                             "margin": S4.MARGIN, "arms": [S4.arm_name(*x) for x in surv],
                             "cell_trades_sha256": h, "reference_resolution": res_ref,
                             "fv3c_slices": "results/customer_slices.csv (sha256 pinned), read, never rerun",
                             "workers": int(a.workers), "seconds": round(seconds, 1)},
                 notes={"status": READING, "selection": "stage 1's family-wise survivors alone run stage 2; BH beside, "
                                                        "never selecting; a candidate needs all four D-578 (2) guards"},
                 description="EXPLORATORY (D-578, batch S4, D-610): P-16's cell with each offer's side from one of 10 "
                             "declared Point & Figure rules (the most recent fixed-reading catapult or plain triple "
                             "top / bottom at boxes 2.5, 5, 6.25, 7.5 and 10 points, D-607's engine, read at t - 5 "
                             "minutes the same trading day) instead of the coin; the per-offer lift over the coin twin "
                             "at every offered R, a studentised max-statistic block bootstrap family-wise at 0.05 / 20 "
                             "(BH at 10 % beside), and for survivors P-16's paired campaign with D-578's four guards.")
    if verd:
        print(pd.DataFrame(verd).to_string(index=False))
    print(f"written: {RESULT}.csv ({len(surv)} surviving arms; {seconds:.0f} s)")
    return 0


def arm_coins(base: dict, keys: list, sides: np.ndarray, arm: tuple[str, int]) -> dict:
    q = S4.RULE_NAMES.index(arm[0])
    return S4.campaign_coins(base, keys, sides[:, q], arm[1])


if __name__ == "__main__":
    raise SystemExit(main())
