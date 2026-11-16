"""RC (rc_s100_all, D-527): the registered development test of family RC's carried cell -- P-14's registered test with
RC's trades. A seeded coin offered every five minutes all session on FV3-C's 25-point rung, taken by P-14's strict router
when every account is flat, with P-14's money side exactly.

    python scripts/rc_dev_test.py --check --paths 4 --starts 6      # every identity and arm at 4 paths, the slices and
                                                                     #   journey on the first 6 starts; nothing written,
                                                                     #   no reading printed
    python scripts/rc_dev_test.py --prereg P-xx --workers 4         # the registered test; refused without a registration

**The candidate** (D-521, D-525, D-527): `scripts/rc_reentry_screen.py`'s `rc_s100_all` cell exactly -- the walk at every
five-minute mark from 17:00 CT (`resolved_coin.marks`), the cutoff (`resolved_coin.mark_resolution`: unresolved at most
5 % at every offered R, kind columns only), the coin seeded 20261102 per date and mark, the 25-point rung, every quarter
R to 3R, FV3's costs, report days' marks before 07:30 CT dropped -- through P-14's engine call (`atlas_a3.gate_kwargs`:
FV3-C's protocol with the day capacity at the cell's busiest day, the no-closure table `state_dp_e-0.050_lamstar_noclose`
read through `a3_brk30_cb20.noclose_plan`, 20 Combine purchases and resets in any 21 trading days, the strict one-at-a-time
rule at 5 minutes, five Topstep seats, the placement off, 0 % denial in the gate), each R's 0.05 bound over 21-session
blocks by the era rule (`a3_brk30.bounds_at_n`, the screen's `atlas_a3.bounds`) and at 0.05/N.

**The seed (D-529 (2)):** every resampled arm of the registered run draws its paths at a FRESH campaign seed, `SEED` =
20261204, fixed by D-529 before anything was read at it: D-525's screen ran this cell's gate campaign at 20261131, so -- as
D-512 ruled for P-14 -- the registered gate must not reuse it. 20261131 survives only in the identities. (The build's
`--check --paths 4 --starts 6` smoke ran every arm at 20261204 at 4 paths before D-529, printing and writing nothing;
nothing was read from it.)

**The planning sd (D-529 (4)):** `assumed_sd`, a planning input and not a result, is `planning_sd`'s value at 3R -- the
sample standard deviation of each offered R's net outcome over the cell's offered candidates -- printed by
`python scripts/rc_dev_test.py --planning-sd` (nothing written) and recorded in the registered result's manifest
(`planning_sd`); it decides nothing.

**Identities first, each refusing the run before anything is written:** (a) P-14's own trades through this engine call
reproduce `results/a3_brk30_cb20_gate_paths.csv`'s gate run, point and bound at 0 % (`rc_screen.identity_problems`; the
first `--paths`); (b) the cell's trades are the screen's: their count, a day's busiest count, the day capacity, the long
share, the candidates a day and every R's unresolved share equal `results/rc_reentry_screen.csv`'s `rc_s100_all` row (that
file's sha256 pinned), and their content hash equals `TRADES_SHA256` (pinned from the build's check, so a later change to
the walk or the coin is refused); (c) at 500 paths the cell at the screen's seed 20261131 reproduces the screen's growth on
the required bankroll at the bound and the point and its required bankroll (section `screen_identity`, never a gate row)
-- before any registered arm runs at `SEED`; (d) FV3-C's slices equal `results/customer_slices.csv`'s `fv3c` verdict rows
(sha256 pinned), slice for slice.

**The arms** are P-14's, each with the cell's trades: the gate (0, 10, 25 and 50 % denial; point and bound), the bound at
0.05/N, the placement on, the zero-edge twin, the fixed-legs twin in P-06's form (section `twin`), the T24-GF15b reading
(section `gf15b_twin`, never deciding), the check period, the Focused Trader Program's 16 declared models (section `ftp`,
beside, never the gate; the binding summary as D-512 (4)) and the campaign without the strict rule (section
`unstrict_beside`, never deciding); beside them, never deciding, **the three other customer windows** (`rc_s100_asia`,
`rc_s100_london`, `rc_s100_us`: each window's own trades and bounds, its gate row at 0 %, point and bound; section
`window_beside`). The per-path record in `results/rc_s100_all_gate_paths.csv`.

**The slice lines** (D-509 (3)'s four, P-14's): over every start of the window in historical order, the cell's
bound-shifted arm against FV3-C's development configuration as frozen (`customer_slices.fv3c_campaign`, its v12 table, its
own protocol), at 63 trading days -- (a) share of slices ending positive, (b) 10th-percentile net, (c) share with no
payout, (d) needed bankroll's 95th percentile -- each no worse than FV3-C's; 21 and 126 days beside; every slice in
`results/rc_s100_all_gate_slices.csv`. The cell's slices come from D-518's journey replay (`customer_journey`'s
`_single_replay_task`: runs of exactly 21 / 63 / 126 sessions, D-508's convention, which D-518's identity tied to
`customer_slices.csv` start for start); FV3-C's from `customer_slices`' own job list. **D-518's journey readings** on the
cell's verdict arm (`customer_journey.metrics`, section `journey`) are beside, never deciding.

**The verdict** (D-509 (3), D-419): the gate's word (`t23_d20.verdict_of`, with the resolution line -- every offered R
unresolved at most 5 % overall and in its worst year -- and realised over intended capped risk at least 0.90) -- PASS at
0.05/N, CONTINUE at 0.05, FAIL below; then PASS only with the gate's PASS and all four slice lines, the gate's PASS with a
line failed is CONTINUE (consistency); otherwise the gate's word (`a3_brk30_cb20.verdict_word`).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

if __name__ == "__main__":                 # one BLAS thread (D-464 (5)), before numpy loads
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/rc_dev_test.py"
DECISION = "D-527"
MODEL = "RC"
K = 1
CELL = "rc_s100_all"
WINDOWS_BESIDE = ("rc_s100_asia", "rc_s100_london", "rc_s100_us")
RESULT = f"{CELL}_gate"
SLICES_RESULT = f"{RESULT}_slices"
#: the registered arms' campaign seed, fixed by D-529 (2) before anything was read at it (the build's 4-path smoke ran
#: every arm at it before D-529, printing and writing nothing; nothing read from it)
SEED = 20261204
SEED_BOOT = 20261017                       # P-13's and P-14's bootstrap seed, unchanged
#: the screen's campaign seed (= P-14's): used ONLY by the identities (a) and (c)
SCREEN_SEED = 20261131
N_PATHS = 500
LEVELS = (0.0, 0.10, 0.25, 0.50)
WINDOW = ("2020-01-01", "2026-07-16")
CHECK = ("2025-01-17", "2026-07-16")
ERAS = ((2020, 2022), (2023, 2026))
REALISED_MIN = 0.90
HORIZONS = (21, 63, 126)
#: the screen's file (D-527), pinned: its rc_s100_all row is the trades' identity and its growth the seed identity
SCREEN_FILE = "rc_reentry_screen.csv"
SCREEN_SHA256 = "dfd93c46deca5651e125ba63a8616b3b6f627beea87097593dbac27df4c37df1"
#: the cell's trades' content hash (`trades_hash`), pinned from the build's check runs (two builds, the same hash)
TRADES_SHA256 = "2ffcc96be321d038e039acdec1ca1f517b7797b7acdc97a07f86747e4f0a7926"
#: the screen row's columns the trades must reproduce (b)
TRADE_ID_COLS = ("candidates", "busiest_day", "capacity", "long_share", "candidates_per_day")
TOL = 1e-12
FTP_VARIANTS = f"{DECISION}:{CELL}_ftp"


@dataclass(frozen=True)
class Spec:
    """One RC cell's registered development test: everything the run reads that differs between cells (P-15's spec is
    this module's constants, `P15`; a sibling script -- `scripts/rc150_dev_test.py` -- passes its own). Two optional
    beside readings, off for P-15 so its run is unchanged: `funded_cap` (D-544: the cell with the funded leg's realised
    risk held to the 25-point cell's, `resolved_coin.funded_cap_rule`) and `multi_breach` (the share of paths with a day
    on which two or more accounts hit the loss limit, a column every gate row then carries)."""
    script: str
    decision: str
    model: str
    cell: str
    windows_beside: tuple[str, ...]
    seed: int
    screen_seed: int
    screen_file: str
    screen_sha256: str
    trades_sha256: str
    stop_ticks: int
    build: Callable[[], tuple[dict, dict]] | None = None
    funded_cap: bool = False
    multi_breach: bool = False
    describe: str = ("the {cell} coin -- offered every five minutes all session on FV3-C's 25-point rung, taken when "
                     "every account is flat")
    news_safe: bool = False

    @property
    def result(self) -> str:
        return f"{self.cell}_gate"

    @property
    def slices_result(self) -> str:
        return f"{self.result}_slices"

    @property
    def ftp_variants(self) -> str:
        return f"{self.decision}:{self.cell}_ftp"


#: P-15's spec: this module's constants exactly (its registered run, D-531, D-532)
P15 = Spec(script=SCRIPT, decision=DECISION, model=MODEL, cell=CELL, windows_beside=WINDOWS_BESIDE, seed=SEED,
           screen_seed=SCREEN_SEED, screen_file=SCREEN_FILE, screen_sha256=SCREEN_SHA256, trades_sha256=TRADES_SHA256,
           stop_ticks=100)


# ------------------------------------------------------------------------------------------------ the trades


def trades_hash(t: pd.DataFrame) -> str:
    """A content hash of the cell's trades: every column in sorted order, row order as built (date, then mark)."""
    cols = sorted(t.columns)
    h = pd.util.hash_pandas_object(t[cols].reset_index(drop=True), index=False).to_numpy()
    return hashlib.sha256(h.tobytes() + "|".join(cols).encode()).hexdigest()


def build_cells() -> tuple[dict, dict]:
    """(P-14's inputs and the no-closure plan, `rc_reentry_screen.build`'s output: the walk, cutoff and cells)."""
    import rc_reentry_screen as RS
    import rc_screen as S

    I = S.inputs()
    return I, RS.build(I)


def trade_problems(rd: Path, b: dict, fcfg: dict, *, sha256: str | None = None, spec: "Spec | None" = None
                   ) -> list[str]:
    """(b): the cell's trades against its screen's row (P-15: `rc_reentry_screen.csv`'s `rc_s100_all`) and the pinned
    content hash."""
    import a3_brk30 as B
    import atlas_a3 as A

    sp = P15 if spec is None else spec
    path = Path(rd) / sp.screen_file
    want = sp.screen_sha256 if sha256 is None else sha256
    if hashlib.sha256(path.read_bytes()).hexdigest() != want:
        return [f"{sp.screen_file} is not the file fixed at registration (sha256 {want[:12]})"]
    s = B._exact(path)
    row = s[(s["section"] == "cell") & (s["cell"].astype(str) == sp.cell)]
    if len(row) != 1:
        return [f"{sp.screen_file} holds {len(row)} rows for {sp.cell}"]
    row = row.iloc[0]
    t = b["cells"][sp.cell]["trades"]
    days = b["days"]
    res, _ = A.resolution(t, b["rr_grid"])
    mine = {"candidates": len(t), "busiest_day": B.busiest(t), "capacity": B.capacity(t, fcfg),
            "long_share": float((t["side"] == "long").mean()), "candidates_per_day": float(len(t) / len(days)), **res}
    out = []
    for k, v in mine.items():
        if k in row.index and not B._same(v, row[k]):
            out.append(f"{k}: {v!r} against the screen's {row[k]!r}")
    if trades_hash(t) != sp.trades_sha256:
        out.append(f"the trades' content hash {trades_hash(t)[:12]} is not the pinned {sp.trades_sha256[:12]}")
    return out


def screen_growth_problems(rd: Path, df: pd.DataFrame, spec: "Spec | None" = None) -> list[str]:
    """(c): the cell's campaign at the screen's seed against its screen's row (500 paths)."""
    import a3_brk30 as B

    sp = P15 if spec is None else spec
    s = B._exact(Path(rd) / sp.screen_file)
    row = s[(s["section"] == "cell") & (s["cell"].astype(str) == sp.cell)].iloc[0]
    at = {sh: df[(df["shift"] == sh) & np.isclose(df["enforcement_p"].astype(float), 0.0)].iloc[0]
          for sh in ("point", "lower_bound")}
    pairs = (("growth_on_required", at["lower_bound"]["pf_growth_on_base_p50"]),
             ("growth_on_required_point", at["point"]["pf_growth_on_base_p50"]),
             ("required_p90", at["lower_bound"]["pf_required_p90"]))
    return [f"{k}: {float(v)!r} against the screen's {row[k]!r}" for k, v in pairs if not B._same(v, row[k])]


def planning_sd(t: pd.DataFrame) -> dict[float, dict[str, float]]:
    """D-529 (4)'s planning input: each offered R's net outcome's sample sd (ddof 1) over the cell's offered candidates,
    with their count. Not a result; it decides nothing."""
    from a3_brk30 import rrs

    out = {}
    for R in rrs(t):
        x = t[f"r_{R:g}"].to_numpy(float)
        x = x[np.isfinite(x)]
        if len(x) > 1:
            out[float(R)] = {"sd": float(x.std(ddof=1)), "n": int(len(x))}
    return out


#: the share of paths with a day on which two or more accounts hit the loss limit (RTP trigger 1, D-30): the engine's
#: `CampaignPath.same_day_multi_breach_days`, as `reinvest`'s summary reads it -- promised by P-13's and P-14's files and
#: missing from their gate rows (the audits' repeated finding); off for P-15 (`Spec.multi_breach`)
MULTI_BREACH = "share_paths_with_same_day_multi_breach"


def multi_breach_share(paths) -> float:
    """The share of `paths` with at least one day on which two or more accounts hit the loss limit."""
    if not len(paths):
        return float("nan")
    return float(np.mean([int(getattr(x.path, "same_day_multi_breach_days", 0) or 0) > 0 for x in paths]))


# ------------------------------------------------------------------------------------------------ the slices and journey


def rc_campaign(I: dict, t: pd.DataFrame, days: list[str], e_by: dict, lb_by: dict, cap: int,
                spec: "Spec | None" = None):
    """The cell as a `customer_slices.Campaign` (its point blocks, dates and P-14's engine arguments at SEED; the replay
    draws nothing)."""
    import atlas_a3 as A
    import customer_slices as cs
    import score_fv3_grid as gf

    from a3_brk30 import rrs

    sp = P15 if spec is None else spec
    L = I["L"]
    fcfg, tv = L["fcfg"], float(L["tv"])
    blocks, n_used = gf.gate_blocks(t, days, tv, rrs(t), require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, None, seed=sp.seed, n_paths=1,
                       horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=cap, levels=(0.0,), rtp=False,
                       one_at_a_time=float(_strict_gap()))
    blocks = kw.pop("blocks")
    kw.pop("path_hook")
    kw.pop("n_paths")
    return cs.Campaign(sp.cell, list(blocks), [str(d) for d in days], kw)


def _strict_gap() -> float:
    import a3_brk30_cb20 as C

    return float(C.STRICT_GAP)


def journey_and_slices(camp, plan, budget, workers: int, starts: int | None, cell: str = CELL
                       ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """D-518's journey replay of the cell's verdict arm over every start (or the first `starts`): (the units -- one
    journey row a start -- and the cell's slices at 21 / 63 / 126 in `customer_slices.SLICE_COLS`' form)."""
    import customer_journey as cjS
    import customer_slices as cs

    blk = cs.arm_blocks(camp, "verdict")
    args = cs.engine_args(camp.kw, "verdict", camp.blocks, risk_policy=plan, purchase_budget=budget)
    n = len(blk) if starts is None else min(int(starts), len(blk))
    tasks = [(cell, "verdict", blk, camp.dates, args, list(range(j, min(n, j + cjS.CHUNK_STARTS))))
             for j in range(0, n, cjS.CHUNK_STARTS)]
    res = cjS._pool_run(tasks, cjS._single_replay_task, workers, f"{cell} journey replay")
    bad = int(sum(x["bad"] for x in res))
    if bad:
        raise SystemExit(f"REFUSED: {bad} exact runs whose event days differ from the long run's (D-518's identity).")
    units = pd.DataFrame([r for x in res for r in x["rows"]])
    sl = pd.DataFrame([{"section": "slice", "config": cell, "arm": "verdict", **s} for x in res for s in x["slices"]])
    sl = sl[list(cs.SLICE_COLS)].sort_values(["horizon", "start_day"], kind="stable").reset_index(drop=True)
    return units, sl


def fv3c_slices(rd: Path, workers: int, starts: int | None) -> pd.DataFrame:
    """FV3-C's development configuration's slices by `customer_slices`' own job list (its v12 table, its own protocol)."""
    import customer_slices as cs

    c = cs.fv3c_campaign(Path(rd))
    blk = cs.arm_blocks(c, "verdict")
    args = cs.engine_args(c.kw, "verdict", c.blocks, risk_policy=c.kw["risk_policy"], purchase_budget=None)
    items = cs.slice_items(len(blk), HORIZONS)
    if starts is not None:
        items = [(s, h) for s, h in items if s < int(starts)]
    return pd.DataFrame(cs.run_slices([("fv3c", "verdict", blk, c.dates, args, items)], int(workers)),
                        columns=list(cs.SLICE_COLS))


def fv3c_slice_problems(rd: Path, sl: pd.DataFrame) -> list[str]:
    """(d): FV3-C's slices against `customer_slices.csv`'s `fv3c` verdict rows (sha256 pinned), start for start."""
    import a3_brk30_cb20 as C

    ref = C._pinned(rd, C.SLICES_REFERENCE, C.SLICES_REFERENCE_SHA256)
    ref = ref[(ref["section"] == "slice") & (ref["arm"].astype(str) == "verdict") & (ref["config"].astype(str) == "fv3c")]
    a = sl.sort_values(["horizon", "start_day"]).reset_index(drop=True)
    b = ref.merge(a[["horizon", "start_day"]].astype(float), on=["horizon", "start_day"], how="inner")
    b = b.sort_values(["horizon", "start_day"]).reset_index(drop=True)
    if len(a) != len(b):
        return [f"FV3-C: {len(a)} slices against {C.SLICES_REFERENCE}'s {len(b)}"]
    out = []
    for c in C.SLICE_ID_COLS:
        bad = [i for i in range(len(a)) if not C._slice_same(a[c].iloc[i], b[c].iloc[i])]
        if bad:
            i = bad[0]
            out.append(f"FV3-C {c}: horizon {int(a['horizon'].iloc[i])} start {int(a['start_day'].iloc[i])} "
                       f"{a[c].iloc[i]!r} against {b[c].iloc[i]!r} ({len(bad)} differ)")
    return out


# ------------------------------------------------------------------------------------------------ the run


def run(pid: str | None, rd: Path, results_dir: Path | None, *, workers: int = 1, n_paths: int = N_PATHS,
        starts: int | None = None, check: bool = False, spec: "Spec | None" = None) -> int:
    """The identities, every arm, the slices, the journey, the verdict and the files (`check`: nothing written, no
    reading printed)."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import confirm_fv3 as cf
    import customer_slices as cs
    import fv3d_lever_test as lt
    import portfolio_stage as ps
    import rc_screen as S
    import score_fv3_grid as gf
    import t23_d20 as td
    import t24_gf15 as tg

    from propedge.backtest.harness import VariantCounter
    from propedge.campaign import gate
    from propedge.reporting.results import write_result
    from propedge.research import customer_journey as cj
    from propedge.research import ledger as lg
    from propedge.research import resolved_coin as rc

    sp = P15 if spec is None else spec
    t_all = time.time()
    print("P-14's inputs, the no-closure plan, the walk and the cells...", flush=True)
    I, b = (sp.build or build_cells)()
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    nc = I["plan"]
    t = b["cells"][sp.cell]["trades"]
    days = b["days"]
    # (a) P-14's trades through this engine call
    R = S.Runner(I, workers)
    bad = S.identity_problems(R, n_paths)
    if bad:
        print(f"REFUSED ({sp.decision}): P-14's trades are not {S.P14_PATHS} -- " + "; ".join(bad[:8]))
        return 3
    print(f"identity HOLDS: P-14's trades = the first {n_paths} paths of {S.P14_PATHS} (gate, 0 %, point and bound)",
          flush=True)
    # (b) the trades are the screen's cell
    bad = trade_problems(rd, b, fcfg, spec=sp)
    if bad:
        print(f"REFUSED ({sp.decision}): the trades are not {sp.screen_file}'s {sp.cell} -- " + "; ".join(bad[:8]))
        return 3
    th = trades_hash(t)
    print(f"identity HOLDS: the trades = {sp.screen_file}'s {sp.cell} ({len(t)} candidates; content hash {th[:16]})",
          flush=True)
    camp = fcfg["gate"]["campaign"]
    horizon = int(camp["horizon_days"])
    keys = B.rrs(t)
    cap = B.capacity(t, fcfg)
    n_led = lg.count_n(lg.load_ledger(), model=sp.model, k=K, markets=["NQ"], window=WINDOW)["N"]
    st, e_by, lb_by, lbn_by, era_rows, flagged = B.bounds_at_n(t, days, cfg, n_led)
    by_k = cf.edge_stats(t, keys, days, 21, K)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise SystemExit("REFUSED: the blocks hold a different number of trades.")
    pcfg = fcfg["portfolio"]
    paths_rows: list[dict] = []
    inner = ps.composed_hook({"margin": float(pcfg["margin"]), "block_days": int(pcfg["block_days"])}, sink=paths_rows)
    hook = lt.lever_hook(inner)
    if sp.multi_breach:
        lever = hook

        def hook(shift, p, paths):  # noqa: F811 -- the lever hook plus the multi-breach share (the audits' finding)
            out = lever(shift, p, paths)
            out[MULTI_BREACH] = multi_breach_share(paths)
            return out

    def go(section: str, blk, eb, lbb, *, plan=nc, levels=(0.0,), rtp=False, strict=True, focused_trader=None,
           budget=C.BUDGET, seed=sp.seed, capacity=cap, funded_cap=False) -> pd.DataFrame:
        ps._label(inner, section)
        kw = A.gate_kwargs(blk, fcfg, tv, plan, eb, lbb, hook, seed=int(seed), n_paths=int(n_paths), horizon=horizon,
                           capacity=capacity, levels=levels, rtp=rtp,
                           one_at_a_time=C.STRICT_GAP if strict else None, focused_trader=focused_trader,
                           purchase_budget=budget)
        if funded_cap:                     # D-544: the funded leg's realised risk held to the 25-point cell's
            kw["sizing"] = rc.funded_cap_rule(kw["sizing"], rc.REFERENCE_STOP, sp.stop_ticks)
        df, _ = gate.run_gate(kw.pop("blocks"), workers=int(workers), **kw)
        df["placement"] = "on" if rtp else "off"
        df.insert(0, "section", section)
        return df

    # (c) the screen's growth at its own seed, before any registered arm draws at sp.seed
    s_df = go("screen_identity", blocks, e_by, lb_by, seed=sp.screen_seed)
    s_df["is_gate_row"] = False
    if int(n_paths) == N_PATHS:
        bad = screen_growth_problems(rd, s_df, sp)
        if bad:
            print(f"REFUSED ({sp.decision}): the cell at seed {sp.screen_seed} is not {sp.screen_file}'s {sp.cell} -- "
                  + "; ".join(bad))
            return 3
        print(f"identity HOLDS: the cell at seed {sp.screen_seed} = {sp.screen_file}'s growth and required bankroll", flush=True)
    else:
        print(f"identity (c) needs all {N_PATHS} paths (growth reads every path); not compared at {n_paths}", flush=True)
    # (d) FV3-C's slices, then the cell's journey and slices
    fsl = fv3c_slices(rd, workers, starts)
    bad = fv3c_slice_problems(rd, fsl)
    if bad:
        print(f"REFUSED ({sp.decision}): FV3-C's slices are not {C.SLICES_REFERENCE}'s -- " + "; ".join(bad[:8]))
        return 3
    print(f"identity HOLDS: FV3-C's slices = {C.SLICES_REFERENCE}'s fv3c verdict rows", flush=True)
    rcamp = rc_campaign(I, t, days, e_by, lb_by, cap, sp)
    units, rsl = journey_and_slices(rcamp, nc, C.BUDGET, workers, starts, sp.cell)
    sl = pd.concat([rsl, fsl], ignore_index=True)
    summ = cs.summarise(sl)
    lines = C.slice_lines(summ, candidate=sp.cell, reference="fv3c")
    lines_hold = all(r["holds"] for r in lines)
    _, common_summ = C.common_slices(sl, candidate=sp.cell, reference="fv3c")
    sub = float(rcamp.kw["rules"].subscription)
    journey = pd.DataFrame([{"section": "journey", "config": sp.cell, "arm": "verdict", "source": "replay",
                             "key": cj.metric_key(m["milestone"], m["measure"], m["at_days"]), **m,
                             "reading": "beside, never deciding (D-518's measures)"} for m in cj.metrics(units, sub)])
    # the registered arms, every one at the fresh seed
    gate_df = go("gate", blocks, e_by, lb_by, levels=LEVELS)
    n_df = go("gate_at_ledger_n", blocks, e_by, lbn_by)
    n_df = n_df[n_df["shift"] == "lower_bound"]
    on_df = go("placement_on", blocks, e_by, lb_by, rtp=True)
    fr = B.fresh_rr(L)[1]
    zero = {k: 0.0 for k in e_by}
    z_df = go("zero_edge_twin", ps.zero_edge_blocks(blocks, e_by, fr), zero, zero)
    z_df = z_df[z_df["shift"] == "point"]
    f_df = go("twin fixed_legs", blocks, e_by, lb_by, plan=B.fixed_legs())
    f_df = f_df[f_df["shift"] == "point"].copy()
    f_df["section"], f_df["twin"] = "twin", "fixed_legs"
    g15_df = go("gf15b_twin", blocks, e_by, lb_by, plan=B.gf15b_plan())
    tc_, dc = lt.in_period(t, days, *CHECK)
    ec, lbc = B.check_bounds(tc_, dc, keys)
    bc, _ = gf.gate_blocks(tc_, dc, tv, keys, require_sides=True, require_exits=True)
    c_df = go("check_years", bc, ec, lbc)
    grid = B.ftp_grid()
    ftp_df = B.ftp_frame(gate_df, [go(f"ftp {mdl.label}", blocks, e_by, lb_by, focused_trader=mdl) for mdl in grid])
    ftp_df["reading"] = "beside the verdict, never the gate (D-234, D-497, D-499, D-509)"
    u_df = go("unstrict_beside", blocks, e_by, lb_by, strict=False)
    u_df["is_gate_row"] = False
    u_df["reading"] = "beside the verdict, never deciding: the campaign without the strict rule (D-499's form)"
    w_parts = []
    for w in sp.windows_beside:
        tw = b["cells"][w]["trades"]
        kw_ = B.rrs(tw)
        _, ew, lw, _, _ = A.bounds(tw, days, kw_, cfg)
        bw, nw = gf.gate_blocks(tw, days, tv, kw_, require_sides=True, require_exits=True)
        if nw != len(tw):
            raise SystemExit(f"REFUSED: {w}'s blocks hold a different number of trades.")
        wdf = go(f"window {w}", bw, ew, lw, capacity=B.capacity(tw, fcfg))
        wdf["section"], wdf["window_cell"], wdf["is_gate_row"] = "window_beside", w, False
        wdf["reading"] = "beside, never deciding: a customer window's own trades and bounds (D-525 (3))"
        w_parts.append(wdf)
    cap_parts: list[pd.DataFrame] = []
    if sp.funded_cap:
        fc = go("funded_cap_beside", blocks, e_by, lb_by, funded_cap=True)
        fct = go("funded_cap_twin", ps.zero_edge_blocks(blocks, e_by, fr), zero, zero, funded_cap=True)
        fct = fct[fct["shift"] == "point"].copy()
        for part in (fc, fct):
            part["is_gate_row"] = False
            part["reading"] = ("beside, never deciding: the funded leg's realised risk held to the 25-point cell's "
                               "(resolved_coin.funded_cap_rule; D-542, D-544)")
        cap_parts = [fc, fct]
    if check:
        print(f"every identity holds and every arm ran at {n_paths} paths; the slices and journey on "
              f"{'every' if starts is None else starts} start(s); nothing written, no reading printed (--check). "
              f"{time.time() - t_all:.0f} s")
        return 0
    row = gate_df[(gate_df["shift"] == "lower_bound") & np.isclose(gate_df["enforcement_p"].astype(float), 0.0)].iloc[0]
    g = float(row["pf_growth_on_base_p50"])
    g_n = float(n_df.iloc[0]["pf_growth_on_base_p50"])
    res_rows = B.resolution_rows(t, keys)
    resolves = all(r["resolves"] for r in res_rows)
    realised = float(row.get("realised_to_intended_capped_risk", float("nan")))
    fidelity = bool(np.isfinite(realised) and realised >= REALISED_MIN)
    gate_word = td.verdict_of(g, g_n) if (resolves and fidelity) else "FAIL"
    word = C.verdict_word(gate_word, lines_hold)

    def at(df, shift, level=0.0):
        r = df[(df["shift"] == shift) & np.isclose(df["enforcement_p"].astype(float), level)]
        return float(r.iloc[0]["pf_growth_on_base_p50"]) if len(r) else float("nan")

    def col(r, c):
        return float(r[c]) if c in r.index and pd.notna(r[c]) else float("nan")

    beside_v = {f"tier3_{c}": col(row, c) for c in B.TIER3}
    for c in ("share_trades_skipped_busy", "share_trades_skipped_opposite", *C.BUDGET_COLS):
        beside_v[c] = col(row, c)
    beside_v.update({f"growth_bound_denial_{int(round(p * 100))}": at(gate_df, "lower_bound", p) for p in LEVELS[1:]})
    beside_v.update({"growth_point": at(gate_df, "point"), "growth_placement_on": at(on_df, "lower_bound"),
                     "growth_zero_edge_twin": at(z_df, "point"), "growth_fixed_legs_twin": at(f_df, "point"),
                     "growth_gf15b_point": at(g15_df, "point"), "growth_gf15b_bound": at(g15_df, "lower_bound"),
                     "growth_check_years_bound": at(c_df, "lower_bound"),
                     "growth_unstrict_point": at(u_df, "point"), "growth_unstrict_bound": at(u_df, "lower_bound")})
    beside_v["strict_rule_cost_bound"] = beside_v["growth_unstrict_bound"] - g
    if sp.funded_cap:
        beside_v.update({"growth_funded_cap_bound": at(cap_parts[0], "lower_bound"),
                         "growth_funded_cap_point": at(cap_parts[0], "point"),
                         "growth_funded_cap_twin": at(cap_parts[1], "point")})
    if sp.multi_breach:
        beside_v[MULTI_BREACH] = col(row, MULTI_BREACH)
    for wdf in w_parts:
        w = str(wdf["window_cell"].iloc[0])
        beside_v[f"growth_{w}_bound"] = at(wdf, "lower_bound")
        beside_v[f"growth_{w}_point"] = at(wdf, "point")
    beside_v.update(B.ftp_summary(ftp_df))
    beside_v.update(C.ftp_binding_summary(ftp_df))
    for r in lines:
        beside_v.update({f"slice_{r['line']}_{r['measure']}_candidate": r["candidate"],
                         f"slice_{r['line']}_{r['measure']}_fv3c": r["reference"],
                         f"slice_{r['line']}_holds": r["holds"]})
    edges = pd.DataFrame([{"section": "edge", "rr": Rr, "e": st[Rr]["e"], "lb": st[Rr]["lb"], "n": st[Rr]["n"],
                           "blocks": st[Rr]["blocks"], "sd": st[Rr]["sd"], "lb_at_ledger_n": st[Rr]["lb_at_n"],
                           "ledger_n": n_led, "lb_at_k": by_k[Rr]["lb_at_n"], "k": K, "lb_gate": lb_by[Rr],
                           "lb_gate_at_ledger_n": lbn_by[Rr],
                           "d47_met": bool(st[Rr]["n"] > 0 and st[Rr]["e"] >= 0.10 and st[Rr]["lb"] >= 0.05)}
                          for Rr in keys])
    verdict = pd.DataFrame([{"section": "verdict", "prereg": pid, "gate_growth_on_base_p50": g,
                             "gate_at_ledger_n_growth_on_base_p50": g_n, "resolves": resolves, "gate_verdict": gate_word,
                             "slice_lines_hold": lines_hold, "slice_line_horizon": C.LINE_HORIZON, "verdict": word,
                             "era_flagged": flagged, "bounds_read": "the lower era's" if flagged else "pooled",
                             "trades_offered": len(t), "days": len(days),
                             "realised_to_intended_capped_risk": realised, "realised_min": REALISED_MIN,
                             "fidelity": fidelity, "trades_per_day_capacity": cap, "busiest_day": B.busiest(t),
                             "ledger_n": n_led, "one_at_a_time": C.STRICT_GAP, "risk_policy_id": nc.id,
                             "budget_k": C.BUDGET[0], "budget_window_days": C.BUDGET[1], "trades_sha256": th,
                             **beside_v}])
    summ_out = summ.copy()
    summ_out["section"] = "slices"
    summ_out["reading"] = np.where(summ_out["horizon"].astype(int) == C.LINE_HORIZON,
                                   "the slice lines' horizon (D-509 (3))", "beside (D-509 (3))")
    idents = [{"section": "identity", "holds": True,
               "check": f"(a) P-14's trades through this engine call reproduce the first {n_paths} paths of "
                        f"results/{S.P14_PATHS}'s gate run, point and bound at 0 %, at seed {sp.screen_seed}"},
              {"section": "identity", "holds": True,
               "check": f"(b) the trades are results/{sp.screen_file}'s {sp.cell} (count, busiest day, capacity, long "
                        f"share, candidates a day, every R's unresolved share; content hash {th})"},
              {"section": "identity", "holds": True,
               "check": f"(c) the cell at seed {sp.screen_seed} reproduces the screen's growth on the required bankroll "
                        "at the bound and the point and its required bankroll (section screen_identity)"},
              {"section": "identity", "holds": True,
               "check": f"(d) FV3-C's slices equal results/{C.SLICES_REFERENCE}'s fv3c verdict rows"}]
    besides = pd.DataFrame(res_rows + idents + B.fresh_rows(nc) + B.drift_rows(t, keys)
                           + tg.period_rows(t, days, keys, n_led, window=WINDOW, check=CHECK, era_spans=ERAS)
                           + era_rows + tg.sharpe_rows(t, days, keys, n_led))
    res = pd.concat([gate_df, n_df, on_df, z_df, f_df, g15_df, c_df, ftp_df, u_df, *w_parts, *cap_parts, s_df, edges,
                     besides,
                     summ_out, common_summ, pd.DataFrame(lines), journey, verdict], ignore_index=True)
    counter = VariantCounter(path=Path(rd) / "variants.jsonl")
    counter.record(prereg_id=pid, seed=sp.seed, exploratory=False,
                   params={"study": f"{sp.model} gate", "decision": sp.decision, "cell": sp.cell, "table": nc.id,
                           "budget": list(C.BUDGET)},
                   label=f"{sp.model}'s registered test ({pid})")
    for mdl in grid:
        counter.record(prereg_id=sp.ftp_variants, seed=sp.seed, exploratory=True,
                       params={"study": f"{sp.model} Focused Trader Program reading", "registration": pid,
                               **mdl.as_dict(), "paths": n_paths, "horizon": horizon},
                       label=f"Focused Trader Program beside {sp.model} ({pid}): {mdl.label}")
    params = {"decision": sp.decision, "prereg": pid, "model": sp.model, "cell": sp.cell, "k": K, "ledger_n": n_led,
              "seed": sp.seed, "seed_bootstrap": SEED_BOOT, "seed_screen": sp.screen_seed, "n_paths": n_paths,
              "horizon": horizon, "levels": list(LEVELS), "window": list(WINDOW), "check": list(CHECK),
              "eras": [list(x) for x in ERAS], "realised_min": REALISED_MIN, "policy_id": nc.id,
              "budget": list(C.BUDGET), "one_at_a_time": C.STRICT_GAP, "trades_per_day_capacity": cap,
              "trades_sha256": th, "screen": f"results/{sp.screen_file}",
              "planning_sd": {f"{R:g}": v for R, v in planning_sd(t).items()},
              "planning_sd_note": "D-529 (4): a planning input (assumed_sd is its 3R value), not a result; decides nothing",
              "windows_beside": list(sp.windows_beside), "slice_horizons": list(HORIZONS),
              "slice_line_horizon": C.LINE_HORIZON,
              "slice_lines": [{"line": a, "measure": c, "better": d} for a, c, d in C.SLICE_LINES],
              "slices": "the cell's from customer_journey's replay (runs of exactly 21/63/126 sessions), FV3-C's from "
                        "customer_slices' job list; FV3-C's checked against results/customer_slices.csv",
              "journey": "D-518's measures on the cell's verdict-arm replay, beside, never deciding",
              "verdict_rule": "D-509 (3): PASS = the gate's PASS and all four slice lines; the gate's PASS with a line "
                              "failed = CONTINUE (consistency); otherwise the gate's word (D-419)",
              "ftp_models": [mdl.as_dict() for mdl in grid], "ftp_variant_label": sp.ftp_variants,
              "fixed_legs": B.fixed_legs_values(), "fixed_legs_config": B.FIXED_LEGS_CONFIG,
              "stop_ticks": int(sp.stop_ticks), "news_safe": bool(sp.news_safe), "funded_cap_beside": bool(sp.funded_cap),
              "multi_breach_measure": MULTI_BREACH if sp.multi_breach else None,
              "workers": int(workers), "seconds": round(time.time() - t_all, 1),
              "bars": "data/bars/NQ (Databento GLBX.MDP3 ohlcv-1m, D-458)"}
    status = f"the registered test of {sp.model} {sp.cell} ({pid}, {sp.decision})"
    write_result(res, sp.result, script=sp.script, seed=sp.seed, exploratory=False, results_dir=results_dir, prereg_id=pid,
                 variant_count=counter.count(pid), parameters=params, notes={"status": status},
                 description=(f"{sp.model}'s registered development test ({sp.decision}): "
                              + sp.describe.format(cell=sp.cell) + " -- through "
                              "P-14's engine call (the no-closure table, 20 purchases in 21 days, the strict rule); the "
                              "D-145 gate at 0.05/N and 0.05 and D-509's four slice lines against FV3-C; beside it "
                              "P-14's arms, the customer windows and D-518's journey readings, never the gate."))
    write_result(pd.DataFrame(paths_rows), f"{sp.result}_paths", script=sp.script, seed=sp.seed, exploratory=False,
                 prereg_id=pid, results_dir=results_dir, variant_count=counter.count(pid),
                 parameters={"result": f"{sp.result}.csv", "prereg": pid, "model": sp.model},
                 notes={"status": status, "companion_of": f"{sp.result}.csv"},
                 description=f"The per-path record of {sp.result}.csv: every resampled path of every campaign, by section.")
    write_result(sl, sp.slices_result, script=sp.script, seed=sp.seed, exploratory=False, prereg_id=pid,
                 results_dir=results_dir, variant_count=counter.count(pid),
                 parameters={"result": f"{sp.result}.csv", "prereg": pid, "model": sp.model, "horizons": list(HORIZONS)},
                 notes={"status": status, "companion_of": f"{sp.result}.csv"},
                 description=f"Every slice behind {sp.result}.csv's slice lines: the cell's and FV3-C's starts in "
                             "historical order for 21, 63 and 126 trading days.")
    print(f"VERDICT ({pid}): {word} -- the gate {gate_word}: growth on the required bankroll {g:+.4f} at the 95 % "
          f"bound, {g_n:+.4f} at 0.05/{n_led}; resolves {resolves}; realised {realised:.4f}; the slice lines "
          + ", ".join(f"({r['line']}) {r['holds']}" for r in lines))
    return 0


def main(argv: list[str] | None = None, *, results_dir: Path | None = None, spec: "Spec | None" = None) -> int:
    from propedge import RESULTS_DIR

    sp = P15 if spec is None else spec
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--prereg", default=None)
    ap.add_argument("--check", action="store_true", help="every identity and arm at --paths; nothing written")
    ap.add_argument("--paths", type=int, default=N_PATHS)
    ap.add_argument("--starts", type=int, default=None, help="with --check: the slices and journey on the first starts")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--planning-sd", action="store_true", help="print D-529 (4)'s planning sd by R; nothing written")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if a.planning_sd:
        _, b = (sp.build or build_cells)()
        for R, v in planning_sd(b["cells"][sp.cell]["trades"]).items():
            print(f"planning sd at R {R:g}: {v['sd']:.4f} over {v['n']} offered candidates")
        print("D-529 (4): a planning input, not a result; nothing written.")
        return 0
    if a.check:
        return run(None, rd, results_dir, workers=a.workers, n_paths=a.paths, starts=a.starts, check=True, spec=sp)
    if int(a.paths) != N_PATHS or a.starts is not None:
        print(f"REFUSED ({sp.decision}): the registered test runs {N_PATHS} paths and every start; smaller is --check.")
        return 2
    from propedge.backtest.harness import PreregRegistry, UnregisteredRunError

    try:
        PreregRegistry.load().require_runnable(a.prereg)
    except UnregisteredRunError as exc:
        print(f"REFUSED ({sp.decision}): {exc}")
        return 2
    return run(a.prereg, rd, results_dir, workers=a.workers, spec=sp)


if __name__ == "__main__":
    raise SystemExit(main())
