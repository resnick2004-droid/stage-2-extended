"""Q-70's identities (`extended/place_records.py`: the place-recording adapter, through `extended/gate.py`'s
`recorder`), refusing. Recording must change nothing, and the records must be the engine's own.

    python identity/place_records_identity.py --synthetic                    # light, the fast tier: no bar is read
    python identity/place_records_identity.py --paths 4 --only p16           # heavy (the run lock): the lead's
    python identity/place_records_identity.py --value-map 100                # heavy (the run lock): the lead's

**`--synthetic` (light).** Synthetic campaigns through the vendored engine; nothing is read but the vendored config and
P-14's no-closure table (a vendored result file). Two fixtures:

- *simple*: Q-47's own synthetic blocks and arguments (`identity/gate_identity.py`'s `syn_blocks`, `syn_kwargs`, its
  seed 20261947): rotation, flat routing, a purchase budget, the four denial levels, the placement off; recorded at
  both arms and every level;
- *the P-14 table*: P-14's own gate call (`atlas_a3.gate_kwargs`: FV3-C's protocol and sizing, the no-closure state
  table, the strict one-at-a-time gap, the purchase budget, the cross-account rule, 0 %) on trades walked by
  `extended/walker.py` (`STAGE2`, a 60-tick stop, market orders at 09:10, 10:40 and 12:10 CT) over
  `extended/synthetic_bars.py`'s bars for 2021-01-04 to 2021-06-30, at every R the table and A3's grid ask; the sides
  carry a planted edge so that accounts pass and are paid (a fixture, never a feature: with probability 0.7 a side
  follows the session's later move). Seed 20262070 (`[20262070, k]`; Q-70's fixture seed, used by no declaration).

The checks, each printed `holds:` or `FAILS:`:

1. **sources pinned** -- the vendored `simulate_lockstep_campaign`, `_run_paths` and `_path_chunk` hash to the pins;
2. **wrong pin refused**;
3. **signature mirrors the vendored campaign** -- the recorded campaign takes every vendored argument, defaults
   included, plus `path_reducer`;
4. **simple: recording on equals off** -- the gate's rows (exactly), every path's record (`portfolio_stage`'s
   composed-hook sink, every key) and the gate flag;
5. **simple: records consistent and every field present** -- no per-path problem (`PlaceRecorder.problems`), the
   trade and account columns exactly `place_fields`', each path's recorded trades the sink's `trades`;
6. **simple: every place reached** -- (b) to (e) each hold a trade (the comparison is not vacuous);
7. **P-14 table: recording on equals off** -- as 4, and the unrecorded run equals the vendored gate's;
8. **P-14 table: records consistent and every field present** -- as 5;
9. **P-14 table: every place reached** -- as 6;
10. **P-14 table: offers, dates and sides are the blocks'** -- every routed trade's offer id is a row of the walked
    table on the record's date, at its entry time and side, and the record's date is its day block's;
11. **P-14 table: R is the table's** -- every routed trade's R is the table's for its session and on the table's menu;
    the R it closed on is no larger;
12. **P-14 table: trades a year by place** -- `per_year` is the vendored counts over paths x horizon / 252 and agrees
    with the trade rows; (a) is the sum of (b) to (e);
13. **kept columns equal the full record's**;
14. **two workers equal one** -- the P-14 table's records and rows at two path workers equal one worker's (NOT
    CHECKED, said loudly, when the memory guard allows one worker -- E-033's rule);
15. **refusals** -- a recorder that is not one, an unknown arm or column, offer ids that do not number a block's
    trades, a trade table whose entry times are not the blocks', a reducer that is not one.

**`--paths N` (heavy, the run lock).** The registered gate call (as `identity/gate_identity.py` makes it, through
`extended.gate.run_gate`) twice: recording off, and recording on (both arms at 0 %, the offers the trade table's rows,
the dates its days). Each compared on the first N paths of the registered paths file, both shifts, every
`zero_edge_decomposition.PATH_COLS` column to 1e-6 (`zd.path_problems`); the records then hold: no per-path problem,
each path's recorded trades the sink's `trades`, every routed trade's offer a row of the trade table on the record's
date at its entry time. P-16 (`rc_s150_all_gate_paths.csv`; `--only p16`) and P-14 (`a3_brk30_cb20_gate_paths.csv`).

**`--value-map N` (heavy, the run lock).** D-668's records basis reproduced: P-16's and P-14's registered campaigns at
N = 100 paths (U2's re-run: the bound arm, 0 %, the registered seed and horizon), recorded at the bound arm; trades a
year by place (a) to (e) equal `u_value_map.csv`'s `place_values` `trades_per_year_records` for `p16` and `p14` to
1e-9 (family B's build item 10, family O's 18.1 item 4), and the paths equal the registered paths file's first N.

**The read (Q-48).** With `--paths` or `--value-map`, before anything runs, the engine's read is authorised through
`extended.reader.authorise_engine_read` (purpose `identity`) under this identity's decision row: `--row E-NNN`, else
`READ_ROW`, else the first row of `DECISIONS.md` that names Q-70 and an identity; none -- refused (`EXIT 3`).

Exit 0 when every part run holds; 3 when one fails or is refused. Nothing is written. Peak memory printed last.
"""
from __future__ import annotations

import argparse
import inspect
import re
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import gate_identity as GI  # noqa: E402  (identity/gate_identity.py: Q-47's synthetic fixture and comparisons)
import stage2_identity as SI  # noqa: E402  (identity/stage2_identity.py: P-16's seed and paths file, peak memory)

from extended import gate as XG  # noqa: E402
from extended import place_fields as PF  # noqa: E402
from extended import place_records as PR  # noqa: E402
from extended import reader  # noqa: E402

VENDOR = ROOT / "vendor" / "stage2"
#: this identity's decision row (Q-48's read authorisation) -- the row that merges Q-70, set by the lead; until then
#: `--row`, or the first decision row naming Q-70 and an identity
READ_ROW: str | None = None
ITEM = "Q-70"
#: Q-70's fixture seed (a synthetic fixture's, not a declaration's; no prereg file or Stage 2 file names it)
SYN_SEED = 20262070
SYN_START, SYN_END = date(2021, 1, 4), date(2021, 6, 30)
SYN_STOP = 60                       # ticks: risk a micro 60 x $0.50 = $30, above FV3-C's stand-aside floor
SYN_MARKS = ((9, 10), (10, 40), (12, 10))
SYN_FOLLOW = 0.7                    # the planted edge's share of sides that follow the session's later move
SYN_COST = 0.05                     # R a trade, the fixture's costs
SYN_PATHS = 4
SYN_HORIZON = 200
TOL = 1e-6


# ------------------------------------------------------------------------------------------------ comparisons


def _rows_equal(a: pd.DataFrame, b: pd.DataFrame, what: str) -> list[str]:
    return GI.rows_problems(a, b, what)


def _sink_trades(sink: list[dict]) -> dict[tuple[str, float, int], int]:
    return {(str(r["shift"]), float(r["enforcement_p"]), int(r["path"])): int(r["trades"]) for r in sink
            if r.get("trades") is not None}


def shape_hook(hook: Any, shapes: list) -> Any:
    """The gate's path hook, noting first what every path handed to it carries: (shift, level, its ledger rows, day
    rows, campaign-day rows) -- an unrecorded gate's paths carry none."""
    def h(shift, p, paths):
        shapes.extend((shift, float(p), len(x.trades), len(x.account_days), len(x.campaign_days)) for x in paths)
        return hook(shift, p, paths)
    return h


def shape_problems(off: list, on: list, what: str) -> list[str]:
    if off != on:
        return [f"{what}: the paths handed to the gate's hook differ in what they carry (recorded rows not dropped)"]
    if any(x[2] or x[3] or x[4] for x in on):
        return [f"{what}: a path handed to the gate's hook still carries recorded rows"]
    return []


def record_problems(rec: PR.PlaceRecorder, sink: list[dict], what: str, *, full: bool = True) -> list[str]:
    """No per-path problem; the columns exactly the schema's; each recorded path's trades the sink's count."""
    out = [f"{what}: {p}" for p in rec.problems()[:8]]
    t, a = rec.trades(), rec.accounts()
    if full and tuple(t.columns) != PF.TRADE_COLUMNS:
        out.append(f"{what}: the trade columns are {list(t.columns)[:6]}..., not place_fields.TRADE_COLUMNS")
    if tuple(a.columns) != PF.ACCOUNT_COLUMNS:
        out.append(f"{what}: the account columns are not place_fields.ACCOUNT_COLUMNS")
    want = _sink_trades(sink)
    got = t.groupby(["shift", "enforcement_p", "path"]).size().to_dict() if len(t) else {}
    for key in rec.recorded():
        run = rec.run_of(*key)
        for i in range(run["n_paths"]):
            k = (key[0], float(key[1]), i)
            if int(got.get(k, 0)) != int(want.get(k, -1)):
                out.append(f"{what}: {k}: {got.get(k, 0)} recorded trades, the path's record holds {want.get(k)}")
    if not rec.recorded():
        out.append(f"{what}: nothing was recorded")
    return out[:10]


def places_reached(rec: PR.PlaceRecorder, what: str) -> list[str]:
    c: dict[str, int] = {}
    for key in rec.recorded():
        for p, v in rec.counts(*key).items():
            c[p] = c.get(p, 0) + int(v)
    empty = [p for p in PR.SINGLE_PLACES if not c.get(p, 0)]
    return [f"{what}: no trade at {empty} -- the comparison would be vacuous there"] if empty else []


# ------------------------------------------------------------------------------------------------ the P-14 fixture


def syn_trades(keys: list[float]) -> tuple[pd.DataFrame, list[str]]:
    """Market orders walked on synthetic bars at every R of `keys`, one row a filled order, in gate_blocks' columns."""
    from extended import features as F
    from extended import synthetic_bars as sb
    from extended import walker as W

    G = F.grid(sb.generate(sb.Spec(SYN_START, SYN_END, seed=SYN_SEED)))
    rng = np.random.default_rng([SYN_SEED, 1])
    i15 = keys.index(1.5)
    rows = []
    for d, day in enumerate(G.days):
        o, h, l, c = (np.r_[np.nan, X[d]] for X in (G.O, G.H, G.L, G.C))
        later = W.price_at(o, c, W.FLAT_ENTRY)
        for hh, mm in SYN_MARKS:
            live = W.slot(hh, mm)
            ref = W.price_at(o, c, live)
            follow = 1 if (np.isfinite(later) and np.isfinite(ref) and later >= ref) else -1
            side = follow if rng.random() < SYN_FOLLOW else (1 if rng.random() < 0.5 else -1)
            tr = W.trade(W.Order(W.MARKET, side, live), o, h, l, c, SYN_STOP, keys, rules=W.STAGE2)
            if tr.fill.status != "filled":
                continue
            k = tr.rule
            row: dict[str, Any] = {"date": str(day), "entry_t": float(tr.fill.bar), "stop_ticks": SYN_STOP,
                                   "side": "long" if side > 0 else "short", "flat": bool(k.kind[i15] == W.FLATTEN),
                                   "exit_t": float(k.exit[i15])}
            for i, R in enumerate(keys):
                row[f"r_{R:g}"] = float(k.gross[i]) / SYN_STOP - SYN_COST
                row[f"mae_{R:g}"] = float(k.mae[i]) / SYN_STOP
                row[f"exit_t_{R:g}"] = float(k.exit[i])
            rows.append(row)
    t = pd.DataFrame(rows)
    t.index = [f"syn{i:05d}" for i in range(len(t))]
    return t, [str(d) for d in G.days]


def p14_table_inputs() -> dict[str, Any]:
    """P-14's own gate call on the synthetic walked trades: (kwargs without the hook and blocks, blocks, trades, days,
    the table's R menu)."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import score_fv3_grid as gf
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR

    cfg = A.config(B.FAMILY)
    fcfg = A.fv3_config(cfg)
    tv = float(A.TICK_VALUE)
    plan = C.noclose_plan(RESULTS_DIR)
    menu = sorted(float(R) for R in zd.policy_rrs(plan))
    keys = sorted({float(R) for R in A.rrs(cfg)} | set(menu))
    t, days = syn_trades(keys)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise RuntimeError("the synthetic blocks hold a different number of trades")
    e_by = {R: float(t[f"r_{R:g}"].mean()) for R in keys}
    lb_by = {R: e_by[R] - 0.05 for R in keys}
    kw = A.gate_kwargs(blocks, fcfg, tv, plan, e_by, lb_by, None, seed=SYN_SEED, n_paths=SYN_PATHS,
                       horizon=SYN_HORIZON, capacity=B.capacity(t, fcfg), levels=(0.0,), rtp=False,
                       one_at_a_time=C.STRICT_GAP, purchase_budget=C.BUDGET)
    kw.pop("blocks")
    kw.pop("path_hook")
    return {"kw": kw, "blocks": blocks, "t": t, "days": days, "menu": menu, "fcfg": fcfg}


def _p14_hook(fcfg: dict, label: str):
    import fv3d_lever_test as lt
    import portfolio_stage as ps

    sink: list[dict] = []
    inner = ps.composed_hook({"margin": float(fcfg["portfolio"]["margin"]),
                              "block_days": int(fcfg["portfolio"]["block_days"])}, sink=sink)
    ps._label(inner, label)
    return lt.lever_hook(inner), sink


def offer_problems(rec_t: pd.DataFrame, t: pd.DataFrame, days: list[str], what: str) -> list[str]:
    """Every routed trade's offer is a row of the trade table on the record's date, at its entry time and side, and the
    record's date is its day block's."""
    s = rec_t[rec_t["source"] == "strategy"]
    if not len(s):
        return [f"{what}: no routed trade recorded"]
    out = []
    missing = ~s["offer"].isin(t.index)
    if missing.any():
        return [f"{what}: {int(missing.sum())} recorded offers are not rows of the trade table"]
    row = t.loc[s["offer"].to_numpy()]
    if not np.array_equal(row["date"].astype(str).to_numpy(), s["date"].astype(str).to_numpy()):
        out.append(f"{what}: an offer's date is not the record's")
    if not np.array_equal(row["entry_t"].to_numpy(float), s["entry_t"].to_numpy(float)):
        out.append(f"{what}: an offer's entry time is not the record's")
    sides = np.where(row["side"].astype(str).str.lower().to_numpy() == "long", 1, -1)
    if not np.array_equal(sides, s["side"].to_numpy(int)):
        out.append(f"{what}: an offer's side is not the record's")
    hd = np.asarray(days, dtype=object)[s["historical_day"].to_numpy(int)]
    if not np.array_equal(hd.astype(str), s["date"].astype(str).to_numpy()):
        out.append(f"{what}: a record's date is not its day block's")
    return out


def synthetic_problems() -> dict[str, list[str]]:
    """Each check's problems (an empty list where it holds), in the docstring's order."""
    from propedge.campaign import gate as vg
    from propedge.campaign import lockstep as L
    from propedge.campaign.lockstep import path_pool

    out: dict[str, list[str]] = {}
    got = PR.vendored_campaign_sha256()
    out["sources pinned"] = [f"{k} hashes to {got[k]}, the pin is {v}" for k, v in PR.VENDORED_CAMPAIGN_SHA256.items()
                             if got.get(k) != v]
    try:
        PR.check_vendored_campaign_source({k: "0" * 64 for k in PR.VENDORED_CAMPAIGN_SHA256})
        out["wrong pin refused"] = ["a wrong pin was not refused"]
    except RuntimeError:
        out["wrong pin refused"] = []
    sa = inspect.signature(L.simulate_lockstep_campaign).parameters
    sb = inspect.signature(PR.simulate_lockstep_campaign_recorded).parameters
    p = [f"{k}: {sa[k]} against {sb.get(k)}" for k in sa if k not in sb or str(sa[k]) != str(sb[k])]
    if [k for k in sb if k not in sa] != ["path_reducer"]:
        p.append(f"the recorded campaign adds {[k for k in sb if k not in sa]}, not only path_reducer")
    out["signature mirrors the vendored campaign"] = p

    # ---- simple: Q-47's fixture, both arms and every level recorded
    blocks, kw = GI.syn_blocks(), GI.syn_kwargs()
    h0, s0 = GI._hook()
    sh0: list = []
    rows0, ok0 = XG.run_gate(blocks, path_hook=shape_hook(h0, sh0), **kw)
    h1, s1 = GI._hook()
    sh1: list = []
    rec = PR.PlaceRecorder(dates=[f"d{h:03d}" for h in range(len(blocks))])
    rows1, ok1 = XG.run_gate(blocks, path_hook=shape_hook(h1, sh1), recorder=rec, **kw)
    p = (_rows_equal(rows0, rows1, "simple") + GI.sink_problems(s0, s1, "simple")
         + shape_problems(sh0, sh1, "simple"))
    if ok0 != ok1:
        p.append(f"simple: the gate flag {ok1} against {ok0}")
    if len(rec.recorded()) != len(rows0):                     # a gate row is one (shift, level) campaign
        p.append(f"simple: {len(rec.recorded())} campaigns recorded for the gate's {len(rows0)} rows")
    out["simple: recording on equals off"] = p
    out["simple: records consistent and every field present"] = record_problems(rec, s1, "simple")
    out["simple: every place reached"] = places_reached(rec, "simple")

    # ---- the P-14 table on walked synthetic trades, the bound arm at 0 % recorded
    P = p14_table_inputs()
    kw14, b14 = P["kw"], P["blocks"]
    ids = PR.block_offer_ids(P["t"], P["days"], b14)
    hv, sv = _p14_hook(P["fcfg"], "q70_syn")
    rows_v, ok_v = vg.run_gate(b14, path_hook=hv, **kw14)
    h0, s0 = _p14_hook(P["fcfg"], "q70_syn")
    sh0 = []
    rows0, ok0 = XG.run_gate(b14, path_hook=shape_hook(h0, sh0), **kw14)
    h1, s1 = _p14_hook(P["fcfg"], "q70_syn")
    sh1 = []
    rec = PR.PlaceRecorder(shifts=("lower_bound",), levels=(0.0,), dates=P["days"], offer_ids=ids)
    rows1, ok1 = XG.run_gate(b14, path_hook=shape_hook(h1, sh1), recorder=rec, **kw14)
    p = (_rows_equal(rows_v, rows0, "P-14 table, off against the vendored gate")
         + GI.sink_problems(sv, s0, "P-14 table, off against the vendored gate")
         + _rows_equal(rows0, rows1, "P-14 table") + GI.sink_problems(s0, s1, "P-14 table")
         + shape_problems(sh0, sh1, "P-14 table"))
    if not (ok_v == ok0 == ok1):
        p.append(f"P-14 table: the gate flags {ok_v}, {ok0}, {ok1}")
    out["P-14 table: recording on equals off"] = p
    out["P-14 table: records consistent and every field present"] = record_problems(rec, s1, "P-14 table")
    out["P-14 table: every place reached"] = places_reached(rec, "P-14 table")
    t14 = rec.trades()
    st = t14[t14["source"] == "strategy"]
    print(f"(the P-14 table fixture: {len(P['t'])} walked offers on {len(P['days'])} sessions; recorded "
          f"{len(t14)} trades on {SYN_PATHS} paths -- by place {t14['place'].value_counts().sort_index().to_dict()}; "
          f"R asked {sorted(set(np.round(st['rr'], 3)))}; need exits {int(t14['at_need'].sum())}; "
          f"{int(rec.accounts()['opened'].sum())} of {len(rec.accounts())} funded accounts opened)", flush=True)
    out["P-14 table: offers, dates and sides are the blocks'"] = offer_problems(t14, P["t"], P["days"], "P-14 table")
    s = t14[t14["source"] == "strategy"]
    p = []
    if not len(s) or not np.isfinite(s["rr"].to_numpy(float)).all():
        p.append("P-14 table: a routed trade has no R")
    elif not set(np.round(s["rr"].unique(), 9)) <= set(np.round(P["menu"], 9)):
        p.append(f"P-14 table: R {sorted(set(s['rr']) - set(P['menu']))} is not on the table's menu")
    if len(s) and not np.allclose(s["rr"].to_numpy(float), s["policy_rr"].to_numpy(float), rtol=0, atol=1e-12):
        p.append("P-14 table: a routed trade's R is not its session's table R")
    ru = s["rr_used"].to_numpy(float)
    if len(s) and not (np.isnan(ru) | (ru <= s["rr"].to_numpy(float) + 1e-12)).all():
        p.append("P-14 table: a trade closed on an R above the table's")
    if len(s) and len(set(np.round(s["rr"], 9))) < 2:
        p.append("P-14 table: the table asked one R only -- the R field is not exercised")
    out["P-14 table: R is the table's"] = p
    p = []
    run = rec.run_of("lower_bound", 0.0)
    years = run["n_paths"] * run["horizon_days"] / PR.SESSIONS_PER_YEAR
    py, c = rec.per_year("lower_bound", 0.0), t14["place"].value_counts()
    for pl in PR.SINGLE_PLACES:
        if abs(py[pl] - float(c.get(pl, 0)) / years) > 1e-12:
            p.append(f"P-14 table: {pl} a year {py[pl]} against the rows' {float(c.get(pl, 0)) / years}")
    if abs(py["a_every_trade"] - sum(py[pl] for pl in PR.SINGLE_PLACES)) > 1e-9:
        p.append("P-14 table: (a) is not the sum of (b) to (e)")
    if len(rec.openings()) != int(rec.accounts()["opened"].sum()):
        p.append("P-14 table: the openings are not the accounts that opened")
    out["P-14 table: trades a year by place"] = p

    # ---- kept columns
    keep = ("path", "place", "offer", "rr", "date", "account_session")
    rk = PR.PlaceRecorder(shifts=("lower_bound",), levels=(0.0,), dates=P["days"], offer_ids=ids, columns=keep)
    h2, s2 = _p14_hook(P["fcfg"], "q70_syn")
    XG.run_gate(b14, path_hook=h2, recorder=rk, **kw14)
    order = [c for c in PF.TRADE_COLUMNS if c in keep]         # kept columns come in the schema's order
    a, b = rk.trades(), t14[order]
    p = [] if list(a.columns) == order else [f"kept columns: {list(a.columns)}, not {order}"]
    if not p:
        try:
            pd.testing.assert_frame_equal(a.reset_index(drop=True), b.reset_index(drop=True), check_exact=True)
        except AssertionError as exc:
            p.append(f"kept columns differ: {str(exc).splitlines()[0]}")
    out["kept columns equal the full record's"] = p

    # ---- two workers
    pool, n = path_pool(2, n_tasks=SYN_PATHS, memory_per_worker_gb=0.5)
    if pool is not None:
        pool.shutdown()
    if int(n) < 2:
        print(f"NOT CHECKED (not a pass): two workers equal one -- the memory guard allows {n} worker(s) now",
              flush=True)
        out["two workers equal one"] = []
    else:
        h3, s3 = _p14_hook(P["fcfg"], "q70_syn")
        r2 = PR.PlaceRecorder(shifts=("lower_bound",), levels=(0.0,), dates=P["days"], offer_ids=ids)
        rows2, _ = XG.run_gate(b14, path_hook=h3, recorder=r2, workers=2, memory_per_worker_gb=0.5, **kw14)
        p = _rows_equal(rows1, rows2, "two workers") + GI.sink_problems(s1, s3, "two workers")
        try:
            pd.testing.assert_frame_equal(t14, r2.trades(), check_exact=True)
            pd.testing.assert_frame_equal(rec.accounts(), r2.accounts(), check_exact=True)
        except AssertionError as exc:
            p.append(f"two workers: the records differ -- {str(exc).splitlines()[0]}")
        out["two workers equal one"] = p

    # ---- refusals
    p = []

    def refused(fn, exc: type, what: str) -> None:
        try:
            fn()
            p.append(f"not refused: {what}")
        except exc:
            pass

    refused(lambda: XG.run_gate(blocks, recorder=object(), **kw), TypeError, "a recorder that is not one")
    refused(lambda: PR.PlaceRecorder(shifts=("bound",)), ValueError, "an unknown arm")
    refused(lambda: PR.PlaceRecorder(columns=("no_such",)), ValueError, "an unknown column")
    short = [x[:-1] if len(x) else x for x in ids]
    refused(lambda: XG.run_gate(b14, recorder=PR.PlaceRecorder(offer_ids=short), **kw14), ValueError,
            "offer ids that do not number a block's trades")
    bad_t = P["t"].copy()
    bad_t.iloc[0, bad_t.columns.get_loc("entry_t")] += 1.0
    refused(lambda: PR.block_offer_ids(bad_t, P["days"], b14), ValueError,
            "a table whose entry times are not the blocks'")
    refused(lambda: PR.simulate_lockstep_campaign_recorded(kw14["protocol"], edge=0.0, seed=1, initial_bankroll=1.0,
                                                           path_reducer=object()),
            TypeError, "a reducer that is not one")
    out["refusals"] = p
    return out


# ------------------------------------------------------------------------------------------------ the registered calls


def p16_call(n: int) -> dict[str, Any]:
    """P-16's gate call as identity/gate_identity.py's `p16_problems` makes it (kwargs without blocks and hook)."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import rc150_dev_test as P
    import rc_dev_test as D
    import score_fv3_grid as gf

    sp = P.SPEC
    if int(sp.seed) != SI.P16_SEED:
        raise RuntimeError(f"P-16's seed in the vendored script is {sp.seed}, not {SI.P16_SEED}")
    I, b = sp.build()
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    t = b["cells"][sp.cell]["trades"]
    days = [str(d) for d in b["days"]]
    th = D.trades_hash(t)
    if th != sp.trades_sha256:
        raise RuntimeError(f"P-16's trades hash {th} is not the pinned {sp.trades_sha256}")
    keys = B.rrs(t)
    _, e_by, lb_by, _, _ = A.bounds(t, b["days"], keys, cfg)
    blocks, n_used = gf.gate_blocks(t, b["days"], tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise RuntimeError("the blocks hold a different number of trades")
    kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, None, seed=SI.P16_SEED, n_paths=int(n),
                       horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=B.capacity(t, fcfg),
                       levels=(0.0,), rtp=False, one_at_a_time=C.STRICT_GAP, purchase_budget=C.BUDGET)
    kw.pop("blocks")
    kw.pop("path_hook")
    return {"kw": kw, "blocks": blocks, "t": t, "days": days, "fcfg": fcfg, "paths_file": SI.P16_PATHS,
            "base": "p16", "name": "P-16"}


def p14_call(n: int) -> dict[str, Any]:
    """P-14's gate call as `rc_screen.Runner.run` makes it for `rc_screen.identity_problems` (gate_identity's)."""
    import a3_brk30 as B
    import atlas_a3 as A
    import rc_screen as S
    import score_fv3_grid as gf

    I = S.inputs()
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    t, days = B.cell_trades(L)
    keys = B.rrs(t)
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
    blocks, n_used = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n_used != len(t):
        raise RuntimeError("the blocks hold a different number of trades")
    kw = A.gate_kwargs(blocks, fcfg, tv, I["plan"], e_by, lb_by, None, seed=S.SEED, n_paths=int(n),
                       horizon=int(fcfg["gate"]["campaign"]["horizon_days"]), capacity=B.capacity(t, fcfg),
                       levels=(0.0,), rtp=False, one_at_a_time=S.STRICT_GAP, purchase_budget=S.BUDGET)
    kw.pop("blocks")
    kw.pop("path_hook")
    return {"kw": kw, "blocks": blocks, "t": t, "days": [str(d) for d in days], "fcfg": fcfg,
            "paths_file": S.P14_PATHS, "base": "p14", "name": "P-14"}


def registered_problems(X: dict[str, Any], n: int, workers: int, *, shifts: tuple[str, ...],
                        arms: tuple[str, ...] = ("recording off", "recording on")
                        ) -> tuple[dict[str, list[str]], PR.PlaceRecorder]:
    """The registered call through the adapter, recording off and on (`arms`): each arm's paths against the registered
    file's first n (both shifts, PATH_COLS, 1e-6), and the records' problems. ({arm: problems}, the recorder)."""
    import zero_edge_decomposition as zd

    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    ref = read_result(RESULTS_DIR / X["paths_file"])
    out: dict[str, list[str]] = {}
    rec = None
    for arm in arms:
        label = f"{X['base']}_q70_{arm.split()[1]}"
        hook, sink = _p14_hook(X["fcfg"], label)
        kw = dict(X["kw"], n_paths=int(n))
        if arm == "recording on":
            rec = PR.PlaceRecorder(shifts=shifts, levels=(0.0,), dates=X["days"],
                                   offer_ids=PR.block_offer_ids(X["t"], X["days"], X["blocks"]))
            XG.run_gate(X["blocks"], path_hook=hook, recorder=rec, workers=int(workers), **kw)
        else:
            XG.run_gate(X["blocks"], path_hook=hook, workers=int(workers), **kw)
        out[arm] = zd.path_problems(sink, ref, [(label, s, "gate", s) for s in ("point", "lower_bound")], int(n))
        if arm == "recording on":
            out["records"] = (record_problems(rec, sink, f"{X['name']} records")
                              + offer_problems(rec.trades(), X["t"], X["days"], f"{X['name']} records"))
    return out, rec


def value_map_problems(X: dict[str, Any], rec: PR.PlaceRecorder) -> list[str]:
    """Trades a year by place at the bound arm, 0 %, against u_value_map.csv's records basis for the base."""
    from propedge import RESULTS_DIR
    from propedge.reporting.results import read_result

    vm = read_result(RESULTS_DIR / "u_value_map.csv")
    rows = vm[(vm["section"].astype(str) == "place_values") & (vm["base"].astype(str) == X["base"])
              & (vm["measure"].astype(str) == "trades_per_year_records")]
    py = rec.per_year("lower_bound", 0.0)
    out = []
    for place in PR.PLACES:
        r = rows[rows["state"].astype(str) == place]
        if len(r) != 1:
            out.append(f"{X['name']}: u_value_map.csv holds {len(r)} rows for {place}")
            continue
        want = float(r["value"].iloc[0])
        if not abs(py[place] - want) <= 1e-9 * max(1.0, abs(want)):
            out.append(f"{X['name']}: {place} trades a year {py[place]!r} against the value map's {want!r}")
    return out


# ------------------------------------------------------------------------------------------------ main


def decision_row(given: str | None) -> str | None:
    """This identity's decision row: given, else READ_ROW, else the first row naming Q-70 and an identity."""
    if given:
        return given
    if READ_ROW:
        return READ_ROW
    p = ROOT / "DECISIONS.md"
    text = p.read_text(encoding="utf-8") if p.is_file() else ""
    for line in text.splitlines():
        m = re.match(r"^\|\s*(E-\d{3,})\s*\|", line)
        if m and re.search(rf"(?<![\w-]){re.escape(ITEM)}(?!\d)", line) and "identit" in line.lower():
            return m.group(1)
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--synthetic", action="store_true", help="the light identity on synthetic campaigns (no bars)")
    ap.add_argument("--paths", type=int, default=None, help="the registered gate paths at N paths (heavy)")
    ap.add_argument("--value-map", type=int, default=None, help="the value map's records basis at N = 100 (heavy)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--only", choices=("p14", "p16"), default=None)
    ap.add_argument("--row", default=None, help="this identity's decision row (E-NNN) for the read's authorisation")
    a = ap.parse_args(argv)
    if not a.synthetic and a.paths is None and a.value_map is None:
        ap.error("give --synthetic, --paths N or --value-map N")
    for name, v in (("--paths", a.paths), ("--value-map", a.value_map)):
        if v is not None and v < 1:
            ap.error(f"{name} takes a whole number of at least 1")
    names = [n for n in ("P-16", "P-14") if a.only is None or n.replace("-", "").lower() == a.only]
    if a.paths is not None or a.value_map is not None:
        row = decision_row(a.row)
        try:                                        # Q-48: the engine's read authorised (ledgered in a clean run only)
            if row is None:
                raise reader.ReadRefused(f"REFUSED: {ITEM}'s identity names no decision row: give --row E-NNN (the "
                                         "row that merges Q-70) or set READ_ROW")
            reader.authorise_engine_read(reader.CHOICE_START, reader.JUDGED_END, purpose=reader.IDENTITY,
                                         declaration=row, files=SI.engine_files(VENDOR, bars="P-16" in names),
                                         what=f"{row}'s identity (identity/place_records_identity.py): "
                                              f"{' and '.join(names)} registered gate campaigns through the "
                                              f"place-recording adapter ({a.paths or a.value_map} paths)")
        except (reader.ReadRefused, FileNotFoundError) as exc:
            print(SI.refusal(exc))
            print("EXIT 3", flush=True)
            return 3
    bad = False
    t0 = time.time()
    if a.synthetic:
        res = synthetic_problems()
        for check, probs in res.items():
            if probs:
                bad = True
                print(f"FAILS: {check} -- " + "; ".join(probs))
            else:
                print(f"holds: {check}")
        print(("synthetic identity FAILS" if any(res.values()) else "synthetic identity HOLDS") +
              f" ({ITEM}, extended.place_records; {time.time() - t0:.0f} s)", flush=True)
    calls = {"P-16": p16_call, "P-14": p14_call}
    if a.paths is not None:
        for name in names:
            t1 = time.time()
            print(f"{name}: the registered gate call through extended.gate, recording off and on, {a.paths} paths...",
                  flush=True)
            X = calls[name](int(a.paths))
            res, rec = registered_problems(X, int(a.paths), int(a.workers), shifts=PR.SHIFTS)
            for arm in ("recording off", "recording on"):
                if res[arm]:
                    bad = True
                    print(f"identity FAILS: {name} gate through extended.gate ({arm}) -- {len(res[arm])} problem(s): "
                          + "; ".join(res[arm][:6]), flush=True)
                else:
                    print(f"identity HOLDS: {name} gate through extended.gate ({arm}) -- the first {a.paths} paths of "
                          f"results/{X['paths_file']}'s gate run, both shifts, every PATH_COLS column to 1e-6",
                          flush=True)
            if res["records"]:
                bad = True
                print(f"records FAIL: {name} -- " + "; ".join(res["records"][:6]), flush=True)
            else:
                n_t = len(rec.trades())
                print(f"records HOLD: {name} -- {n_t} trades recorded over both shifts at 0 %, each path's count the "
                      "path's record's, the places records_counts', every routed offer a row of the trade table",
                      flush=True)
            del X, rec
            print(f"  {name}: {time.time() - t1:.0f} s", flush=True)
    if a.value_map is not None:
        for name in names:
            t1 = time.time()
            print(f"{name}: the value map's records basis, {a.value_map} paths, the bound arm at 0 %...", flush=True)
            X = calls[name](int(a.value_map))
            res, rec = registered_problems(X, int(a.value_map), int(a.workers), shifts=("lower_bound",),
                                           arms=("recording on",))
            probs = res["recording on"] + res["records"] + value_map_problems(X, rec)
            if probs:
                bad = True
                print(f"value-map identity FAILS: {name} -- " + "; ".join(probs[:6]), flush=True)
            else:
                print(f"value-map identity HOLDS: {name} -- trades a year by place (a) to (e) equal "
                      f"u_value_map.csv's trades_per_year_records for {X['base']} to 1e-9; the first {a.value_map} "
                      f"paths equal results/{X['paths_file']}'s", flush=True)
            del X, rec
            print(f"  {name}: {time.time() - t1:.0f} s", flush=True)
    pm = SI.peak_memory()
    if pm:
        print(pm)
    print(f"EXIT {3 if bad else 0}", flush=True)
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
