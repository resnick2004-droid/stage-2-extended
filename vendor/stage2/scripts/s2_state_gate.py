"""EXPLORATORY (D-578 (4)): batch S2 of the rolling model search -- the state-gated coin. P-16 unchanged except that an
offer is taken only when a declared ex-ante state holds; five cells, each judged directly by the program's four campaign
guards (no stage 1). Selects nothing by itself: a cell passing every guard is a candidate for its own registered
development test (D-578 (2)).

    python scripts/s2_state_gate.py --check                  # a smoke: ~30 walked sessions, every cell through every
                                                             #   guard at 4 paths, 2 coins; no growth printed; nothing
                                                             #   written
    python scripts/s2_state_gate.py --workers 1              # the batch (a clean checkout, D-474); writes the file

**The declaration** (`config/search_program.yaml`, batch S2, D-578) is read as text, its sha256 pinned
(`s1_sided_coin.DECLARATION_SHA256`; the file is not valid YAML as written and is never edited) and every constant of
`propedge.research.s2_state_gate` checked against its words (`declaration_problems`); a mismatch refuses.

**The reference** (P-16, D-544, D-547): `rc_s150_all` -- the 37.5-point (150-tick) news-safe coin, all-day window,
offered every five minutes and re-entering when flat, its own coin seed 20261102 -- built by
`rc_stop_walkforward.walk_stop` / `cell` on every development day, through P-14's engine call (`rc_screen.Runner`: the
no-closure table, 20 purchases and resets in 21 trading days, the strict one-at-a-time rule, five Topstep seats, the
placement off, 0 % denial), campaign seed 20261131.

**The cells** (`propedge.research.s2_state_gate`, whose docstring states every reading): vol_low / vol_mid / vol_high
(the last 30 closed 1-min bars' high-low range at the mark in the bottom / middle / top third of the same measure at the
same mark on the trailing 20 sessions) and trend / range (|c[t] - the session's 17:00 CT first-bar open| above / at or
below the trailing 20 sessions' median at the same mark). Prior sessions only; fewer than 20 prior sessions with a value
at the mark (or no value today) -> the offer is kept. The states are computed once on every walked development session
(causal: bars closed at or before the mark, earlier sessions only), so an offer's gate is the same in every run. Gating
removes offers from P-16's built trades before the engine; the offers kept keep P-16's coin side.

**The guards** (D-578 (2), D-568's): (a) G1, paired: campaign seed 20261131, 500 paths, growth on the required bankroll at
the 0.05 bound above P-16's by more than 0.05; (b) the cell's offers resolve every offered R (the table's R, D-212: at
most 5 % unresolved; the R grid's reading beside); (c) G2: at least 40 of 50 coin sequences (coin seeds 20261600 + i, 200
paths; P-16 and the gated cell both rebuilt with each coin seed, `rc150_routing.coin_cell`) on which the cell grows more
at the bound than P-16; (d) G3: not below P-16 at the bound on 2020-01-01 .. 2023-12-31 alone, nor on 2024-01-01 ..
2026-07-16 alone (`rc150_routing`'s G3 construction: each span's own cell, cutoff and pooled bound; a tie passes). G2 and
G3 run only for a cell that passes (a) and (b) (D-568's screen's rule: no other cell can be a candidate); the others carry
"not run: failed G1". Beside: the zero-edge twin, the share of offers kept, offers and trades taken a session, D-518's
journey and D-509's slice lines against FV3-C (beside, never a guard; not in --check).

**Identities, each refusing:** (i) the cell = P-16's (candidates against `rc_width_screen.csv`, content hash against
`rc150_dev_test.TRADES_SHA256`; every day only); (ii) G2's coin rebuild at P-16's coin seed = the cell; (iii) with every
gate open the gated cell's content hash = the cell's, every offer has a state row, and the cells partition the ranked
offers; (iv) at the declared counts, P-16 reproduces `rc_width_screen.csv`'s `rc_s150_all` row and
`results/rc150_routing.csv`'s R0 rows (G1 with its twin, each G2 coin, each G3 span).

**Resume** (D-540, `rc_robust.Resume`): each finished run kept outside the checkout, keyed by commit and counts; off in
--check and with --no-resume.

Writes `results/s2_state_gate.csv` (EXPLORATORY; sections declaration, identity, offers, g1, journey, slice_lines,
g2_entry, g2, g2_summary, g3, g3_summary, verdict) with its manifest; variants under `D-578:S2` (the five cells).
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable

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
from propedge.research import s2_state_gate as s2  # noqa: E402

SCRIPT = "scripts/s2_state_gate.py"
DECISION = s2.DECISION
BATCH = s2.BATCH
RESULT = "s2_state_gate"
FAMILY_ID = f"{DECISION}:{BATCH}"
CELL = "rc_s150_all"
STOP = 150
N_PATHS = S.N_PATHS                        # 500
G2_PATHS = 200
COIN_SEEDS = tuple(20261600 + i for i in range(50))   # D-578 (2) / D-568 (2), fixed before any read
G2_WINS = 40
MARGIN = 0.05
SPANS = {"early": ("2020-01-01", "2023-12-31"), "late": ("2024-01-01", "2026-07-16")}
REFERENCE = "P16"
CELLS = s2.CELLS
CHECK_DAYS = 30                            # --check: N/2 walked sessions of each span ...
CHECK_SKIP = s2.TRAIL                      # ... after each span's first 20 (so the smoke's offers are ranked)
BAR_CHUNK = 120                            # the states read the bars this many sessions at a time
ROUTING_FILE = "rc150_routing.csv"         # identity (iv): its R0 rows (D-576)
ROUTING_REF = "R0_longest_waiting"
IDENT_COLS = ("growth_on_required", "growth_on_required_point", "required_p90")
G1_SKIP = "not run: failed G1"
READING = ("EXPLORATORY (D-578 (4)): batch S2, the state-gated coin -- P-16 with offers gated by an ex-ante state, each "
           "cell judged by the program's four campaign guards; selects nothing by itself")


class Resume(RR.Resume):
    """`rc_robust.Resume` (D-540) under this batch's own file name."""

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


# ------------------------------------------------------------------------------------------------ pure parts (tested)


def g1_passes(row: dict, ref_growth: float) -> dict[str, bool]:
    """Guards (a) and (b) for one cell's G1 row."""
    diff = float(row["growth_on_required"]) - float(ref_growth)
    return {"a_paired_beats_by_margin": bool(np.isfinite(diff) and diff > MARGIN),
            "b_every_offered_r_resolves": bool(row.get("every_offered_r_resolves", False))}


def g2_entry(g1: dict[str, dict]) -> list[dict]:
    """Per cell: whether G2 and G3 run -- only for a cell passing (a) and (b)."""
    ref = float(g1[REFERENCE]["growth_on_required"])
    out = []
    for c in CELLS:
        p = g1_passes(g1[c], ref)
        enters = bool(all(p.values()))
        out.append({"section": "g2_entry", "cell": c, "growth_minus_reference": float(g1[c]["growth_on_required"]) - ref,
                    **p, "enters_g2_g3": enters, "why": "passes (a) and (b)" if enters else G1_SKIP})
    return out


def g2_summary(rows: list[dict], names, wins_needed: int = G2_WINS) -> list[dict]:
    """Per cell: the coins on which it grows more at the bound than P-16 on the same coin, and whether that reaches
    `wins_needed`. `rows` hold (coin_seed, cell, growth_on_required)."""
    by: dict[int, dict[str, float]] = {}
    for r in rows:
        by.setdefault(int(r["coin_seed"]), {})[str(r["cell"])] = float(r["growth_on_required"])
    out = []
    for n in names:
        diffs = [v[n] - v[REFERENCE] for v in by.values() if n in v and REFERENCE in v]
        wins = int(sum(d > 0 for d in diffs))
        out.append({"section": "g2_summary", "cell": n, "coins": len(diffs), "wins": wins,
                    "mean_difference": float(np.mean(diffs)) if diffs else float("nan"),
                    "wins_needed": int(wins_needed), "passes_g2": bool(len(diffs) and wins >= wins_needed)})
    return out


def g3_summary(growth: dict[str, dict[str, float]], names) -> list[dict]:
    """Guard (d) per cell: not below P-16 at the bound on the early span alone nor on the late span alone (a tie
    passes). `growth` is {span: {cell: growth at the bound}}."""
    out = []
    for n in names:
        r = {"section": "g3_summary", "cell": n}
        ok = True
        for span in SPANS:
            g, ref = growth.get(span, {}).get(n, float("nan")), growth.get(span, {}).get(REFERENCE, float("nan"))
            r[f"{span}_growth"], r[f"{span}_reference"] = float(g), float(ref)
            r[f"{span}_growth_minus_reference"] = float(g) - float(ref)
            ok = ok and bool(np.isfinite(g) and np.isfinite(ref) and g >= ref)
        r["passes_g3"] = bool(ok)
        out.append(r)
    return out


def verdict(g1: dict[str, dict], g2s: list[dict], g3s: list[dict]) -> list[dict]:
    """D-578 (2) per cell: every guard; a candidate only if all four hold."""
    ref = float(g1[REFERENCE]["growth_on_required"])
    p2 = {r["cell"]: bool(r.get("passes_g2", False)) for r in g2s}
    p3 = {r["cell"]: bool(r.get("passes_g3", False)) for r in g3s}
    out = []
    for c in CELLS:
        checks = {**g1_passes(g1[c], ref), "c_wins_coin_sequences": p2.get(c, False),
                  "d_not_below_on_either_span": p3.get(c, False)}
        out.append({"section": "verdict", "cell": c, "growth_minus_reference": float(g1[c]["growth_on_required"]) - ref,
                    **checks, "candidate": bool(all(checks.values()))})
    return out


def smoke_pick(walked: list[str], n: int, skip: int = CHECK_SKIP) -> list[str]:
    """--check: n/2 walked sessions of each span, after each span's first `skip` (whose offers the trailing rule
    leaves unranked)."""
    half = max(int(n) // 2, 1)
    return [d for lo, hi in SPANS.values() for d in sorted(x for x in walked if lo <= x <= hi)[skip:skip + half]]


def chunked_arrays(cfg: dict, dates: list[str], chunk: int = BAR_CHUNK) -> Callable[[str], tuple]:
    """`atlas_a3.bar_arrays` read `chunk` sessions at a time (the window guard on each read), for `state_table`'s walk
    through the sessions in date order -- the whole window is never in memory at once."""
    from propedge.data.bars import read_bars
    from propedge.research import atlas_local

    ds = sorted(str(d) for d in dates)
    pos = {d: i for i, d in enumerate(ds)}
    held: dict[str, Any] = {}

    def arrays(day: str):
        day = str(day)
        if day not in held:
            held.clear()
            i = pos[day]
            part = ds[i:i + int(chunk)]
            bars = read_bars(cfg["market"], part[0], part[-1], "development", what="S2 state gate (D-578)")
            want = set(part)
            for d, g in bars.groupby("day", sort=False):
                if str(d) in want:
                    held[str(d)] = tuple(np.array([np.nan if x is None else x for x in v], dtype=float)
                                         for v in atlas_local.day_arrays(g))
            for d in part:
                held.setdefault(d, tuple(np.full(atlas_local.FLAT_MIN + 1, np.nan) for _ in range(4)))
            del bars
        return held[day]

    return arrays


def restrict(t: pd.DataFrame | None, days: list[str]) -> pd.DataFrame | None:
    """The trades on `days` only; order and columns unchanged; None when none."""
    if t is None:
        return None
    out = t[t["date"].astype(str).isin(set(days))].reset_index(drop=True)
    return out if len(out) else None


def routing_problems(routing: pd.DataFrame, section: str, row: dict, cols=IDENT_COLS, **match) -> list[str]:
    """Identity (iv): P-16's row here against `rc150_routing.csv`'s R0 row of the same section and coin or span (exact to
    1e-9)."""
    r = routing[(routing["section"].astype(str) == section) & (routing["rule"].astype(str) == ROUTING_REF)]
    for k, v in match.items():
        col = r[k]
        r = r[(col.astype(float).astype(int) == int(v))] if k == "coin_seed" else r[col.astype(str) == str(v)]
    if len(r) != 1:
        return [f"{len(r)} {ROUTING_REF} rows for {section} {match}"]
    out = []
    for c in cols:
        mine, want = float(row[c]), float(r.iloc[0][c])
        if not np.isclose(mine, want, rtol=0, atol=1e-9):
            out.append(f"{section} {match} {c}: {mine!r} against {want!r}")
    return out


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

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import read_result, write_result
    from propedge.research import resolved_coin as rc

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="a smoke: ~30 walked sessions, every cell through every guard "
                                                         "at a few paths; no growth printed; nothing written")
    ap.add_argument("--days", type=int, default=None, help=f"--check: walked sessions, half in each span ({CHECK_DAYS})")
    ap.add_argument("--paths", type=int, default=None, help="--check: G1 and G3 paths (4)")
    ap.add_argument("--g2-paths", type=int, default=None, help="--check: G2 paths (4)")
    ap.add_argument("--coins", type=int, default=None, help="--check: the first coin sequences of G2 (2)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--no-resume", action="store_true", help="D-540: neither keep nor read finished runs' rows")
    ap.add_argument("--resume-dir", default=None, help="D-540: where finished runs' rows are kept (outside the checkout)")
    a = ap.parse_args(argv)
    if not a.check and any(x is not None for x in (a.days, a.paths, a.g2_paths, a.coins)):
        print(f"REFUSED ({DECISION}): the batch runs every day, {N_PATHS} / {G2_PATHS} paths, {len(COIN_SEEDS)} coins "
              "and every journey start; a smaller run is --check (writes nothing).")
        return 2
    n_paths = (a.paths or 4) if a.check else N_PATHS
    g2_paths = (a.g2_paths or 4) if a.check else G2_PATHS
    n_coins = (a.coins or 2) if a.check else len(COIN_SEEDS)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()

    # ---- the declaration and the constants it fixes
    decl = s2.declaration()
    bad = s2.declaration_problems(decl)
    fixed = {"campaign seed": (S.SEED, 20261131), "paths": (S.N_PATHS, N_PATHS), "coin seed": (rc.COIN_SEED, s2.COIN_SEED),
             "coin seeds": (tuple(RT.COIN_SEEDS), COIN_SEEDS), "g2 paths": (RT.G2_PATHS, G2_PATHS),
             "g2 wins": (RT.G2_WINS, G2_WINS), "margin": (RT.MARGIN, MARGIN),
             "spans": ({k: tuple(v) for k, v in WF.SPANS.items()}, {k: tuple(v) for k, v in SPANS.items()}),
             "stop": (RT.STOP, STOP), "cell": (RT.CELL, CELL), "walk kinds": (tuple(m0.WALK_DAY_KINDS), s2.WALK_KINDS)}
    bad += [f"{k}: the engine's {v[0]!r} against S2's {v[1]!r}" for k, v in fixed.items() if v[0] != v[1]]
    if bad:
        print(f"REFUSED ({DECISION}): the build is not D-578's declaration -- " + "; ".join(bad))
        return 2
    print(f"the declaration HOLDS: {decl['path']} (sha256 {decl['sha256'][:16]}); S2's cells {decl['cells']}", flush=True)
    idents = [{"section": "declaration", "holds": True,
               "check": f"config/search_program.yaml sha256 {decl['sha256']} (D-578), batch S2 read as text; cells "
                        f"{list(CELLS)}, alpha {s2.ALPHA:g}, {s2.N_VARIANTS} variants; every constant agrees"}]

    # ---- the cell and identities (i), (ii)
    srow = PS.screen_row(RESULTS_DIR)
    print("P-14's inputs, the no-closure plan and the 37.5-point walk...", flush=True)
    I = S.inputs()
    L = I["L"]
    dk = L["days"].copy()
    dk["date"] = dk["date"].astype(str)
    kinds = dict(zip(dk["date"], dk["day_kind"].astype(str)))
    walked_all = sorted(d for d, k in kinds.items() if k in s2.WALK_KINDS)
    if a.check:                                    # a smoke: N/2 walked sessions of each span; nothing else walked
        pick = set(smoke_pick(walked_all, a.days or CHECK_DAYS))
        I = {**I, "L": {**L, "days": dk[dk["date"].isin(pick)].reset_index(drop=True)}}
    W = WF.walk_stop(I, STOP)
    days = list(W["days"])
    t = WF.cell(W, STOP, days)["trades"]
    h = D.trades_hash(t)
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
                       "check": f"(i) the cell's trades (rc_stop_walkforward.cell on every development day): {len(t)} "
                                f"candidates as {PS.SCREEN_FILE}'s {CELL}; content hash {h} = "
                                "rc150_dev_test.TRADES_SHA256 (P-16's)"})
        print(f"identity (i) HOLDS: the cell = P-16's {CELL} ({len(t)} candidates; content hash {h[:16]})", flush=True)
    hc = D.trades_hash(RT.coin_cell(W, I, rc.COIN_SEED, days))
    if hc != h:
        print(f"REFUSED ({DECISION}): rebuilding the cell at P-16's coin seed gives {hc[:16]}, not {h[:16]}.")
        return 3
    idents.append({"section": "identity", "holds": True,
                   "check": f"(ii) G2's coin rebuild (rc150_routing.coin_cell) at P-16's coin seed {rc.COIN_SEED} "
                            "reproduces the cell's content hash"})
    print("identity (ii) HOLDS: G2's coin rebuild at P-16's seed = the cell", flush=True)

    # ---- the states (every walked development session, every mark) and identity (iii)
    t0 = time.time()
    ST = s2.state_table(walked_all, kinds, chunked_arrays(L["cfg"], walked_all), rc.marks())
    print(f"  the states: {len(ST)} (session, mark) rows on {len(walked_all)} sessions, {time.time() - t0:.0f} s",
          flush=True)
    ho = D.trades_hash(s2.gate(t, ST, s2.OPEN))
    if ho != h:
        print(f"REFUSED ({DECISION}): with every gate open the cell hashes {ho[:16]}, not {h[:16]}.")
        return 3
    bad = s2.partition_problems(t, ST)
    if bad:
        print(f"REFUSED ({DECISION}): the cells do not partition the offers -- " + "; ".join(bad))
        return 3
    idents.append({"section": "identity", "holds": True,
                   "check": "(iii) with every gate open (s2_state_gate.gate, cell 'open') the cell's content hash is "
                            f"unchanged ({h}); every offer has a state row; vol_low / vol_mid / vol_high keep every "
                            "ranked offer exactly once and trend / range likewise, every unranked offer kept by all"})
    print("identity (iii) HOLDS: every gate open = the cell; the cells partition the ranked offers", flush=True)
    offers = [{"section": "offers", **r} for r in s2.offer_counts(t, ST)]
    gated = {REFERENCE: t, **{c: s2.gate(t, ST, c) for c in CELLS}}

    resume = None
    if not a.check and not a.no_resume:
        import subprocess

        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = Resume(folder, f"{commit}_{n_paths}_{g2_paths}")
    declared = not a.check
    routing = read_result(RESULTS_DIR / ROUTING_FILE) if declared else None

    # ---- G1: paired, guards (a) and (b)
    g1: dict[str, dict] = {}
    extra: list[dict] = []
    fsl = PS.fv3c_slices(RESULTS_DIR) if declared else None
    for name in (REFERENCE, *CELLS):
        t0 = time.time()

        def make(name=name, tc=gated[name]):
            res_off, ok_off = A.resolution(tc, W["offered_rr"]) if tc is not None else ({}, False)
            _, ok_grid = A.resolution(tc, W["rr_grid"]) if tc is not None else ({}, False)
            head = {"section": "g1", "cell": name, "candidates": 0 if tc is None else int(len(tc)),
                    "candidates_per_session": 0.0 if tc is None else float(len(tc) / len(days)),
                    "kept_share": 0.0 if tc is None else float(len(tc) / len(t)),
                    "cell_trades_sha256": "" if tc is None else D.trades_hash(tc), **res_off,
                    "every_offered_r_resolves": bool(ok_off), "every_grid_r_resolves": bool(ok_grid)}
            if tc is None:
                return {"row": {**head, "growth_on_required": float("nan"), "note": "no offer kept"},
                        "journey": [], "lines": []}
            r = RT.run_rule(I, name, None, tc, days, n_paths, a.workers, twin=True)
            df = r.pop("df")
            if name == REFERENCE and declared:
                prob = PS.growth_problems(df, srow)
                if prob:
                    raise SystemExit(f"REFUSED ({DECISION}): P-16 is not {PS.SCREEN_FILE}'s {CELL} -- " + "; ".join(prob))
            if declared:                           # beside; not in --check (a smoke has no 63- or 126-day horizon)
                jl = RT.journey_and_lines(I, tc, days, None, name, fsl, a.workers, None)
            else:
                jl = {"journey": [], "lines": [], "lines_hold": None}
            rn = lambda x: {("cell" if k == "rule" else k): v for k, v in x.items()}   # noqa: E731
            return {"row": {**head, **r, "slice_lines_hold": jl["lines_hold"]},
                    "journey": [rn(x) for x in jl["journey"]], "lines": [rn(x) for x in jl["lines"]]}

        res = _cached(resume, f"g1 {name}", make)
        g1[name] = res["row"]
        extra += res["journey"] + res["lines"]
        print(f"  G1 {name}: done ({time.time() - t0:.0f} s)", flush=True)
    if declared:
        prob = routing_problems(routing, "g1", g1[REFERENCE], IDENT_COLS + ("growth_zero_edge_twin",))
        if prob:
            print(f"REFUSED ({DECISION}): P-16's G1 run is not {ROUTING_FILE}'s {ROUTING_REF} -- " + "; ".join(prob))
            return 3
        idents.append({"section": "identity", "holds": True,
                       "check": f"(iv) P-16 at seed {S.SEED}, {N_PATHS} paths, reproduces results/{PS.SCREEN_FILE}'s "
                                f"{CELL} growth at the bound and point and its required bankroll, and results/"
                                f"{ROUTING_FILE}'s {ROUTING_REF} G1 row (with the zero-edge twin)"})
        print(f"identity (iv) HOLDS: P-16 at {N_PATHS} paths = {PS.SCREEN_FILE}'s {CELL} and {ROUTING_FILE}'s "
              f"{ROUTING_REF}", flush=True)
    ref = float(g1[REFERENCE]["growth_on_required"])
    for r in g1.values():
        r["growth_minus_reference"] = float(r["growth_on_required"]) - ref

    # ---- which cells go on: (a) and (b) both hold (in --check every cell runs, no reading is used or printed)
    entry = g2_entry(g1)
    on = list(CELLS) if a.check else [r["cell"] for r in entry if r["enters_g2_g3"]]
    if not a.check:
        print(f"  G2/G3 run for: {on or 'none'}", flush=True)

    # ---- G2: across coin sequences
    g2_rows: list[dict] = []
    if on:
        for s in COIN_SEEDS[:n_coins]:
            t0 = time.time()
            ts = RT.coin_cell(W, I, s, days)
            for name in (REFERENCE, *on):

                def make_g2(name=name, s=s, tc=(ts if name == REFERENCE else s2.gate(ts, ST, name))):
                    if tc is None:
                        return {"section": "g2", "coin_seed": int(s), "cell": name, "candidates": 0,
                                "growth_on_required": float("nan"), "note": "no offer kept"}
                    r = RT.run_rule(I, f"g2 {s} {name}", None, tc, days, g2_paths, a.workers)
                    r.pop("df")
                    return {"section": "g2", "coin_seed": int(s), "cell": name, "candidates": int(len(tc)), **r}

                row = _cached(resume, f"g2 {s} {name}", make_g2)
                if name == REFERENCE and declared:
                    prob = routing_problems(routing, "g2", row, coin_seed=int(s))
                    if prob:
                        print(f"REFUSED ({DECISION}): P-16 on coin {s} is not {ROUTING_FILE}'s {ROUTING_REF} -- "
                              + "; ".join(prob))
                        return 3
                g2_rows.append(row)
            del ts
            print(f"  G2 coin {s}: done ({time.time() - t0:.0f} s)", flush=True)
        if declared:
            idents.append({"section": "identity", "holds": True,
                           "check": f"(iv) P-16 on each of the {len(COIN_SEEDS)} coin sequences at {G2_PATHS} paths "
                                    f"reproduces results/{ROUTING_FILE}'s {ROUTING_REF} G2 row"})
    g2s = g2_summary(g2_rows, on) if g2_rows else []
    g2s += [{"section": "g2_summary", "cell": c, "coins": 0, "wins": 0, "wins_needed": int(G2_WINS), "passes_g2": False,
             "note": G1_SKIP} for c in CELLS if c not in on]

    # ---- G3: each span alone
    g3_rows: list[dict] = []
    growth: dict[str, dict[str, float]] = {}
    if on:
        for span, (lo, hi) in SPANS.items():
            sd = WF.span_days(days, lo, hi)
            ts = WF.cell(W, STOP, sd)["trades"]
            for name in (REFERENCE, *on):

                def make_g3(name=name, span=span, sd=sd, tc=(ts if name == REFERENCE else s2.gate(ts, ST, name))):
                    head = {"section": "g3", "span": span, "span_first": sd[0], "span_last": sd[-1],
                            "sessions": len(sd), "cell": name}
                    if tc is None or not len(tc):
                        return {**head, "candidates": 0, "growth_on_required": float("nan"),
                                "note": "no offer kept on this span alone"}
                    bounds = B.check_bounds(tc, sd, B.rrs(tc))
                    r = RT.run_rule(I, f"g3 {span} {name}", None, tc, sd, n_paths, a.workers, bounds=bounds)
                    r.pop("df")
                    return {**head, "candidates": int(len(tc)), **r}

                row = _cached(resume, f"g3 {span} {name}", make_g3)
                if name == REFERENCE and declared:
                    prob = routing_problems(routing, "g3", row, span=span)
                    if prob:
                        print(f"REFUSED ({DECISION}): P-16 on the {span} span is not {ROUTING_FILE}'s {ROUTING_REF} -- "
                              + "; ".join(prob))
                        return 3
                g3_rows.append(row)
                growth.setdefault(span, {})[name] = float(row["growth_on_required"])
            print(f"  G3 {span}: done ({len(sd)} sessions)", flush=True)
        if declared:
            idents.append({"section": "identity", "holds": True,
                           "check": f"(iv) P-16 on each span alone at {N_PATHS} paths reproduces results/{ROUTING_FILE}'s "
                                    f"{ROUTING_REF} G3 rows"})
    g3s = g3_summary(growth, on) if on else []
    g3s += [{"section": "g3_summary", "cell": c, "passes_g3": False, "note": G1_SKIP} for c in CELLS if c not in on]

    seconds = time.time() - t_all
    if a.check:
        print(f"--check done: the declaration, identities (ii) and (iii) on {len(days)} sessions ({len(t)} offers; "
              f"kept shares {[round(r['kept_share'], 3) for r in offers]}), every cell through G1 / G2 / G3 (G1/G3 "
              f"{n_paths} paths, G2 {g2_paths} paths on {n_coins} coins); no growth printed; nothing written. "
              f"{seconds:.0f} s")
        return 0
    verd = verdict(g1, g2s, g3s)
    out = pd.DataFrame(idents + offers + list(g1.values()) + extra + entry + g2_rows + g2s + g3_rows + g3s + verd)
    out.insert(1, "reading", READING)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for c in CELLS:
        counter.record(prereg_id=FAMILY_ID, seed=S.SEED, exploratory=True,
                       params={"study": "D-578 batch S2, the state-gated coin", "reference": CELL, "cell": c,
                               "state": list(s2.RULES[c]), "vol_bars": s2.VOL_BARS, "trail": s2.TRAIL,
                               "coin_seed": rc.COIN_SEED, "g1_paths": N_PATHS, "g2_coins": len(COIN_SEEDS),
                               "g2_paths": G2_PATHS, "g3_spans": list(SPANS)},
                       label=f"D-578's S2: {c}")
    write_result(out, RESULT, script=SCRIPT, seed=S.SEED, exploratory=True, results_dir=results_dir,
                 variant_count=s2.N_VARIANTS,
                 parameters={"decision": DECISION, "batch": BATCH, "alpha": s2.ALPHA,
                             "declaration_sha256": decl["sha256"], "reference": f"P-16 ({CELL})", "stop_ticks": STOP,
                             "cells": {c: list(s2.RULES[c]) for c in CELLS}, "vol_bars": s2.VOL_BARS,
                             "trail_sessions": s2.TRAIL, "walk_kinds": list(s2.WALK_KINDS),
                             "campaign_seed": S.SEED, "coin_seed": rc.COIN_SEED, "g1_paths": N_PATHS,
                             "g2_coin_seeds": [COIN_SEEDS[0], COIN_SEEDS[-1]], "g2_paths": G2_PATHS,
                             "g2_wins_needed": G2_WINS, "g3_spans": {k: list(v) for k, v in SPANS.items()},
                             "margin": MARGIN, "g2_g3_run_for": on, "g2_g3_rule": "only cells passing (a) and (b)",
                             "guard_b": "every offered R (the table's) at most 5 % unresolved; the grid's beside",
                             "cell_trades_sha256": h,
                             "fv3c_slices": "results/customer_slices.csv (sha256 pinned), read, never rerun",
                             "workers": int(a.workers), "seconds": round(seconds, 1)},
                 notes={"status": READING, "selection": "D-578 (2): a cell passing all four guards becomes a candidate "
                                                         "with its own registered development test",
                        "state_readings": "propedge/research/s2_state_gate.py's docstring"},
                 description="EXPLORATORY (D-578, batch S2): P-16 (the 37.5-point news-safe coin) with offers gated by "
                             "five ex-ante states (the last 30 bars' range in the bottom / middle / top third; the "
                             "distance from the 17:00 open above / at or below its median; each against the trailing "
                             "20 sessions at the same mark, prior only), each judged by D-578's four guards (paired 500 "
                             "paths, resolution, 50 coin sequences at 200 paths, early/late spans).")
    pd.set_option("display.width", 250)
    print(pd.DataFrame(verd).to_string(index=False))
    print(f"written: {RESULT}.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
