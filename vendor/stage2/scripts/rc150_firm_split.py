"""EXPLORATORY (D-567): the seat split -- the same small number of seats spread over two firms, against all of them at
one firm, on P-16's cell -- unhedged and (labelled `hypothetical_hedge`, never a candidate) hedged.

    python scripts/rc150_firm_split.py --check --paths 4 --starts 6     # every identity, every cell; nothing written
    python scripts/rc150_firm_split.py --workers 2                      # the screen (from a clean checkout, D-474)
    python scripts/rc150_firm_split.py --second-firm lucid --workers 1  # D-575: firm 1 on Lucid's verified contract

The operator (2026-11-04): "how a combination of firms work without scaling ... What if we split the accounts evenly. 2
on topstep 2 on another firm or vice versa. This can include hypothetical hedging scenario vs non hedging". The point
of a split is not more seats but two firms: each firm holds one position at a time (D-429), so two firms can hold two
positions at once, and each firm's accounts are their own campaign (their own purchase budget, their own rotation).

**The cells** (firm 0 is Topstep; firm 1 the second firm on Topstep's verified contract -- Firm H's convention, D-203,
labelled `assumed_second_firm`, since Lucid's prices are unread, D-561):

=============  =====  ============  ==========================================================================
cell           seats  deal          note
=============  =====  ============  ==========================================================================
5+0            5      unhedged      the reference: P-16's design through the joint engine (one firm)
4+0            4      unhedged      four seats at one firm
2+2            2 + 2  unhedged      four seats split evenly (`assumed_second_firm`)
2+2_hedged     2 + 2  hedged        each signal's lead leg and the other firm's account in its slot on the opposite
                                    side, D-514's deal (`hypothetical_hedge`; prohibited, Topstep 13747047, Lucid
                                    11404734 -- tier 1; never a candidate)
3+2            3 + 2  unhedged      five seats split (`assumed_second_firm`)
3+2_hedged     3 + 2  hedged        as 2+2_hedged; the lead's slot 2 at Topstep has no partner at firm 1 (two
                                    seats), so it trades alone -- counted (`partner_missing_no_account_in_slot`)
=============  =====  ============  ==========================================================================

Each firm's campaign is P-16's (the no-closure v12 table, P-14's protocol, the strict rule per firm) with its seats
set (`hypo_hedge.with_seats`: concurrent accounts, concurrent Combines and total accounts) and its own purchase budget
of floor(20 x seats / 5) Combine purchases and resets in 21 trading days -- P-14's 20 at five seats, scaled to the
seats (2 seats: 8; 3: 12; 4: 16). One pooled wallet per path (D-206). The trades: P-16's cell `rc_s150_all` (the
37.5-point news-safe coin, re-entering when flat), and for the hedged deal the same events on the opposite side (the
coin's other side, built by the same walk with the coin's sides negated), at the screen's seeds (campaign 20261131,
coin 20261102), 500 paths; the bound arm shifts the cell to its 0.05 bound and the opposite side the same amount the
other way (`hypo_hedge.mirror_shift`); each cell's zero-edge twin at the point.

**Identities first, each refusing:** (a) the cell's content hash is P-16's (`rc150_dev_test.TRADES_SHA256`) and the
opposite side has exactly one row for every one of its events, on the other side; (b) the 5+0 cell through the joint
engine reproduces P-16's single-firm engine call (`rc_screen.Runner`) path for path on
`zero_edge_decomposition.PATH_COLS` for the first `IDENTITY_PATHS` paths at both shifts, and its growth on the required
bankroll and required bankroll at that path count; (c) in the full run, the 5+0 cell at 500 paths reproduces
`rc_width_screen.csv`'s `rc_s150_all` growth at the bound and the point and its required bankroll.

**Readings** (`hypo_hedge.readings`, pooled over the firms): growth on the required bankroll at the bound and the
point, the required bankroll, pass rate per Combine, payouts a month, days to the first pass and payout, droughts,
cost per pass, the deal's shares (hedged, alone, skipped busy / opposite); D-518's journey on the bound arm's replay
(every start, historical order; `customer_journey`'s units and metrics) and D-508's slices summarised beside.

Writes `results/rc150_firm_split.csv` (sections identity, cell, twin, journey, slices), EXPLORATORY, variants under
`D-567:rc150_firm_split` (the four unhedged cells) and `D-567:hypothetical_hedge` (the two hedged). A resume file outside
the checkout keeps every finished run (D-540).

**`--second-firm lucid` (D-575; the default stays `topstep`, D-567/D-571 unchanged):** firm 1 runs Lucid's verified
contract (LucidFlex 50K, DLL off, 40 % standard; multi-firm D-31, stage-two D-574) -- `lucid_rules` (the evaluation
$115.50 one-time, resets never bought, the funded $2,000 EOD MLL locking at start + $100, five days of $150 and $1 net
a cycle, 50 % of the balance above start up to $2,000, a 90 % split, at most five payouts), `LucidFundedAccount` with
the household rule's conservative reading (`HOUSEHOLD_CLOSES_AT_LIVE`: the first fifth payout ends every Lucid seat),
Lucid's sizing limits (40 micros in the evaluation; the funded ladder 2 / 3 / 4 minis at $0 / $1,000 / $2,000) on
P-16's sizing rule otherwise (mode, headroom, stand-aside, room cap, and the fee schedule -- Topstep's all-in round
turns, above Lucid's listed commissions: conservative), the payout two business days after the request (12945796's
upper bound), the request at the eligible day's close, no conduct model (Topstep's RTP is Topstep's). Lucid's
`funded_monthly_fee` and `payout_fee` rows are unverified and charged at zero: every Lucid figure is an UPPER BOUND in
them. Firm 0 is Topstep exactly as in D-567. The cells: 5+0 (the reference), 4+0, 3+2, 2+3, 2+2 (Topstep + Lucid
seats) and the hedged 3+2 / 2+3 / 2+2 (`hypothetical_hedge`, never a candidate). Beside them a `sizes` section: each
firm's realised contracts per trade by account kind on the first `IDENTITY_PATHS` paths at the point (Lucid's 40-micro
evaluation cap at the cell's 37.5-point stop), and per cell the household rule's closures. Writes
`results/rc150_firm_split_lucid.csv`, EXPLORATORY, variants under `D-575:rc150_firm_split_lucid` and
`D-575:hypothetical_hedge`.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
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

from propedge.research import customer_journey as cj  # noqa: E402
from propedge.research import hypo_hedge as hh  # noqa: E402

SCRIPT = "scripts/rc150_firm_split.py"
DECISION = "D-567"
RESULT = "rc150_firm_split"
FAMILY_ID = f"{DECISION}:rc150_firm_split"
HYPO_FAMILY_ID = f"{DECISION}:hypothetical_hedge"
ASSUMED = "assumed_second_firm"
N_PATHS = 500
IDENTITY_PATHS = 20
SHIFTS = ("point", "lower_bound")
FULL_SEATS, FULL_BUDGET, BUDGET_WINDOW = 5, 20, 21
#: (cell, seats per firm in firm order, the deal)
CELLS: tuple[tuple[str, tuple[int, ...], str], ...] = (
    ("5+0", (5,), hh.UNHEDGED),
    ("4+0", (4,), hh.UNHEDGED),
    ("2+2", (2, 2), hh.UNHEDGED),
    ("2+2_hedged", (2, 2), hh.HEDGED),
    ("3+2", (3, 2), hh.UNHEDGED),
    ("3+2_hedged", (3, 2), hh.HEDGED),
)
REFERENCE = "5+0"
LUCID = "lucid"
LUCID_LABEL = "lucid_upper_bound"
#: D-575: the cells with Lucid as firm 1 (seats: Topstep's first, then Lucid's)
LUCID_CELLS: tuple[tuple[str, tuple[int, ...], str], ...] = (
    ("5+0", (5,), hh.UNHEDGED),
    ("4+0", (4,), hh.UNHEDGED),
    ("3+2", (3, 2), hh.UNHEDGED),
    ("2+3", (2, 3), hh.UNHEDGED),
    ("2+2", (2, 2), hh.UNHEDGED),
    ("3+2_hedged", (3, 2), hh.HEDGED),
    ("2+3_hedged", (2, 3), hh.HEDGED),
    ("2+2_hedged", (2, 2), hh.HEDGED),
)
CHUNK_PATHS = 25
CHUNK_STARTS = 40
TOL = 1e-9
READING = ("EXPLORATORY (D-567): the seat split on P-16's cell; the second firm on Topstep's contract "
           "(assumed_second_firm); hedged cells hypothetical_hedge, never a candidate; beside the verdicts, never a gate")
LUCID_READING = ("EXPLORATORY (D-575): the seat split on P-16's cell with Lucid's verified contract as firm 1 (multi-firm "
                 "D-31; its funded_monthly_fee and payout_fee uncharged: an upper bound); hedged cells "
                 "hypothetical_hedge, never a candidate; beside the verdicts, never a gate")


@dataclasses.dataclass(frozen=True)
class Study:
    """One reading of the seat split: the second firm, its cells, its result file, decision and variant families."""

    second_firm: str
    decision: str
    result: str
    family: str
    hypo_family: str
    split_label: str
    reading: str
    cells: tuple[tuple[str, tuple[int, ...], str], ...]


SECOND_FIRM_NOTE = {
    "topstep": "Topstep's verified contract under Firm H's convention (D-203): assumed_second_firm",
    LUCID: ("Lucid's verified contract (LucidFlex 50K, DLL off, 40 %; multi-firm D-31, vendored D-574): evaluation "
            "$115.50 one-time, no resets bought, LucidFundedAccount with the household rule's conservative reading, "
            "40-micro evaluation cap and the 2/3/4-mini funded ladder on P-16's sizing rule (Topstep's fee schedule, "
            "conservative), payout lag 2 business days, no conduct model; funded_monthly_fee and payout_fee "
            "uncharged (upper bound)"),
}
LABEL_NOTE = {
    "topstep": f"{ASSUMED} rows rest on a second firm with Topstep's contract",
    LUCID: f"{LUCID_LABEL} rows run Lucid's verified contract with its two open fee rows uncharged (an upper bound)",
}
STUDIES = {
    "topstep": Study("topstep", DECISION, RESULT, FAMILY_ID, HYPO_FAMILY_ID, ASSUMED, READING, CELLS),
    LUCID: Study(LUCID, "D-575", "rc150_firm_split_lucid", "D-575:rc150_firm_split_lucid", "D-575:hypothetical_hedge",
                 LUCID_LABEL, LUCID_READING, LUCID_CELLS),
}


def budget_for(seats: int) -> tuple[int, int]:
    """P-14's budget (20 purchases and resets in 21 trading days at five seats) scaled to a firm's seats, floored."""
    return (int(FULL_BUDGET * int(seats) // FULL_SEATS), BUDGET_WINDOW)


def label_of(seats: tuple[int, ...], mode: str, study: Study = STUDIES["topstep"]) -> str:
    if mode != hh.UNHEDGED:
        return hh.TAG
    return study.split_label if len(seats) > 1 else ""


def family_of(mode: str, study: Study = STUDIES["topstep"]) -> str:
    return study.hypo_family if mode != hh.UNHEDGED else study.family


# ------------------------------------------------------------------------------------------------ the resume file


class Resume:
    """D-540's pattern: each finished run's readings kept outside the checkout, keyed by the code's commit and the path
    and start counts, so a run killed by the machine resumes. Off in --check."""

    def __init__(self, folder: Path | None, key: str, result: str = RESULT):
        self.path = None if folder is None else Path(folder) / f"{result}_{key}.jsonl"
        self.rows: dict[str, Any] = {}
        if self.path is not None and self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    self.rows[r["_label"]] = r["value"]
            print(f"  resume: {len(self.rows)} finished run(s) read from {self.path}", flush=True)

    def get(self, label: str) -> Any:
        return self.rows.get(label)

    def put(self, label: str, value: Any) -> None:
        self.rows[label] = value
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"_label": label, "value": value}, default=_jsonable) + "\n")


def _jsonable(x: Any) -> Any:
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return float(x)
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, np.ndarray):
        return x.tolist()
    return str(x)


def _cached(resume: Resume | None, label: str, make) -> Any:
    v = resume.get(label) if resume is not None else None
    if v is None:
        v = json.loads(json.dumps(make(), default=_jsonable))
        if resume is not None:
            resume.put(label, v)
    return v


# ------------------------------------------------------------------------------------------------ the inputs


def inputs(second_firm: str = "topstep") -> dict[str, Any]:
    """P-16's cell and its opposite side, the blocks, the bounds and the engine's arguments (the gate's call, as
    `rc_screen.Runner` and `hypo_hedge_a3.inputs` build them); firm 1's setups (`camp1`, `rep1`): Topstep's own (the
    default, D-567) or Lucid's (`lucid_setup`, D-575)."""
    if second_firm not in STUDIES:
        raise ValueError(f"second firm {second_firm!r} is not one of {sorted(STUDIES)}")
    import a3_brk30 as B
    import atlas_a3 as A
    import customer_slices as cs
    import hypo_hedge_a3 as ha
    import rc150_dev_test as R
    import rc_dev_test as D
    import rc_screen as S
    import rc_width_screen as W
    import score_fv3_grid as gf

    from propedge.research import resolved_coin as rc

    I, b = R.build_cells()
    t = b["cells"][R.CELL]["trades"]
    if t is None or D.trades_hash(t) != R.TRADES_SHA256:
        raise SystemExit(f"REFUSED ({DECISION}): the cell is not P-16's (content hash).")
    orig = rc.coin_table

    def negated(*a, **k):
        return {key: -int(v) for key, v in orig(*a, **k).items()}

    rc.coin_table = negated                 # the same walk, every coin side the other way (restored below)
    try:
        bo = W.build(I, (R.STOP,))
    finally:
        rc.coin_table = orig
    f = bo["cells"][R.CELL]["trades"]
    if f is None or len(f) != len(t):
        raise SystemExit(f"REFUSED ({DECISION}): the opposite side holds {0 if f is None else len(f)} trades, not "
                         f"{len(t)}.")
    fa = ha.align_opposite(t, f)
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    days = list(b["days"])
    keys = B.rrs(t)
    if B.rrs(fa) != keys:
        raise SystemExit(f"REFUSED ({DECISION}): the opposite side carries other R values.")
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
    _, e_opp, _, _, _ = A.bounds(fa, days, keys, cfg)
    cell, n1 = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    opp, n2 = gf.gate_blocks(fa, days, tv, keys, require_sides=True, require_exits=True)
    if n1 != len(t) or n2 != len(t):
        raise SystemExit(f"REFUSED ({DECISION}): the blocks hold a different number of trades.")
    cap = B.capacity(t, fcfg)
    horizon = int(fcfg["gate"]["campaign"]["horizon_days"])
    kw = A.gate_kwargs(cell, fcfg, tv, I["plan"], e_by, lb_by, None, seed=S.SEED, n_paths=N_PATHS, horizon=horizon,
                       capacity=cap, levels=(0.0,), rtp=False, one_at_a_time=S.STRICT_GAP, purchase_budget=S.BUDGET)
    kw.pop("blocks")
    args = cs.engine_args(kw, "point", cell, purchase_budget=S.BUDGET)
    camp = hh.with_capacity(hh.setup_from_engine_args(args, funded_horizon_days=horizon, combine_max_days=2000),
                            2 * cap)
    rep = hh.with_capacity(hh.setup_from_engine_args(args), 2 * cap)
    p = camp.path
    if (int(p["max_concurrent_accounts"]), int(p["max_concurrent_combines"]), int(p["max_total_accounts"] or 0),
            tuple(p.get("purchase_budget") or ())) != (FULL_SEATS, FULL_SEATS, FULL_SEATS, (FULL_BUDGET, BUDGET_WINDOW)):
        raise SystemExit(f"REFUSED ({DECISION}): P-16's engine call is not five seats with the 20-in-21 budget.")
    camp1, rep1 = (camp, rep) if second_firm == "topstep" else (lucid_setup(camp), lucid_setup(rep))
    return {"I": I, "b": b, "t": t, "fa": fa, "cell": cell, "opp": opp, "days": days, "e_by": e_by, "lb_by": lb_by,
            "camp1": camp1, "rep1": rep1, "second_firm": second_firm, "e_opp": e_opp, "delta_r": float(kw["lb"]) - float(kw["e"]),
            "delta_by_rr": {float(k): float(lb_by[k]) - float(e_by[k]) for k in e_by},
            "fresh_rr": float(fcfg["state_policy"]["fresh"]["funded_rr"]), "cap": int(cap), "horizon": horizon,
            "camp": camp, "rep": rep, "margin": float(fcfg["portfolio"]["margin"]),
            "subscription": float(rep.path["subscription"])}


def arm_blocks(X: dict, shift: str, *, twin: bool = False) -> list:
    """The doubled blocks of one arm: as traded, at the bound (the cell shifted, the opposite mirrored), or the zero-edge
    twin (both sides shifted to zero edge at every R, at the point)."""
    import portfolio_stage as ps

    if twin:
        return hh.doubled_blocks(ps.zero_edge_blocks(X["cell"], X["e_by"], X["fresh_rr"]),
                                 ps.zero_edge_blocks(X["opp"], X["e_opp"], X["fresh_rr"]))
    if shift == "point":
        return hh.doubled_blocks(X["cell"], X["opp"])
    if shift != "lower_bound":
        raise ValueError(shift)
    c, o = hh.mirror_shift(X["cell"], X["opp"], X["delta_r"], X["delta_by_rr"])
    return hh.doubled_blocks(c, o)


def lucid_setup(base: hh.FirmSetup) -> hh.FirmSetup:
    """D-575: P-16's firm setup with Lucid's verified contract in place of Topstep's (the module docstring): its rules,
    fees, funded account class and household rule, payout lag and timing, and its sizing limits on P-16's sizing rule;
    no conduct model. Everything else -- the protocol, the state table, the draws' settlement and routing -- is P-16's."""
    from propedge.contract.lucid import (LUCID_PAYOUT_TIMING, OPEN_ROWS_UPPER_BOUND, STANDARD_40, LucidFundedAccount,
                                         lucid_price, lucid_rules, lucid_sizing_rule, lucid_terms)

    if not lucid_price(STANDARD_40).verified:
        raise SystemExit("REFUSED (D-575): Lucid's evaluation price is not verified in the vendored ledger.")
    rules = lucid_rules(open_rows=OPEN_ROWS_UPPER_BOUND, configuration=STANDARD_40)
    t = lucid_terms()
    sz = base.draws.get("sizing")
    if sz is None:
        raise SystemExit("REFUSED (D-575): P-16's draws carry no sizing rule; Lucid's limits need one.")
    if base.path.get("reset_failed_combines"):
        raise SystemExit("REFUSED (D-575): P-16's campaign buys no resets; a Lucid firm must not either.")
    lz = lucid_sizing_rule(sz.mode, headroom_frac=sz.headroom_frac)
    sizing = dataclasses.replace(sz, ladder=lz.ladder, combine_limit_micros=lz.combine_limit_micros)
    path = dict(base.path)
    path.update(rules=rules, subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                activation=float(rules.activation), payout_lag_days=int(t.payout_processing_days), conduct=None,
                payout_timing=LUCID_PAYOUT_TIMING, funded_account_cls=LucidFundedAccount,
                household_closure=bool(LucidFundedAccount.HOUSEHOLD_CLOSES_AT_LIVE))
    return dataclasses.replace(base, draws={**base.draws, "sizing": sizing}, path=path)


def firm_setups(X: dict, kind: str, seats: tuple[int, ...]) -> list[hh.FirmSetup]:
    """Firm 0 on `X[kind]` (Topstep, P-16's), every later firm on `X[kind + "1"]` (the second firm's), each with its
    seats and its own budget. A Lucid firm's seats stay within its verified caps (5 funded, 10 accounts in total)."""
    out = [hh.with_seats(X[kind], seats[0], budget_for(seats[0]))]
    for s in seats[1:]:
        if X.get("second_firm") == LUCID:
            from propedge.contract.lucid import lucid_terms

            t = lucid_terms()
            if s > min(t.max_funded, t.eval_count_limit, t.max_total_accounts):
                raise ValueError(f"Lucid allows {t.max_funded} funded and {t.max_total_accounts} accounts; got {s} seats")
        out.append(hh.with_seats(X[kind + "1"], s, budget_for(s)))
    return out


# ------------------------------------------------------------------------------------------------ the tasks


def _paths_task(task: tuple) -> list[dict]:
    """(cell, mode, shift, blocks, setups, [(index, seed)], margin, horizon) -> each path's pooled record."""
    import warnings

    warnings.filterwarnings("ignore")
    cell, mode, shift, blocks, setups, items, margin, horizon = task
    specs = [hh.PathSpec(seed=int(s), blocks=blocks, horizon_days=int(horizon)) for _, s in items]
    jps = hh.run_joint(specs, setups[0], n_firms=len(setups), mode=mode, doubled=True, firm_setups=setups)
    out = []
    for (i, s), jp in zip(items, jps):
        r = hh.path_record(jp, margin=margin)
        r.update({"cell": cell, "shift": shift, "path": int(i), "seed": int(s)})
        hold = [lp.household for lp in jp.paths if lp.household]
        if hold:                                       # D-575: a firm with a household rule (Lucid's): its closing day
            r["household_closed_on"] = int(max(int(h["closed_on"]) for h in hold))
        out.append(r)
    return out


def _journey_task(task: tuple) -> dict[str, Any]:
    """(cell, mode, blocks, dates, setups, seed, starts) -> every start's journey row and its D-508 slices, on the
    replay (`customer_journey._start_rows`: the long run plus runs of exactly 21 / 63 / 90 sessions)."""
    import warnings

    import customer_journey as CJ

    warnings.filterwarnings("ignore")
    cell, mode, blocks, dates, setups, seed, starts = task
    sub = max(float(s.path["subscription"]) for s in setups)     # the margin: the dearest firm's evaluation (D-575)
    n = len(blocks)
    want = []
    for s in starts:
        L = min(cj.WINDOW, n - s)
        want.append((s, L))
        want += [(s, h) for h in cj.EXACT if h < L]
    specs = [hh.PathSpec(seed=int(seed), blocks=blocks[s:s + h], horizon_days=int(h) + 1, replay=True) for s, h in want]
    jps = hh.run_joint(specs, setups[0], n_firms=len(setups), mode=mode, doubled=True, firm_setups=setups)
    got = dict(zip(want, jps))
    rows, slices, bad = [], [], 0
    for s in starts:
        L = min(cj.WINDOW, n - s)
        long_ = got[(s, L)]
        lps = {h: got[(s, h)] for h in cj.EXACT if h < L}
        r, sl, b = CJ._start_rows(cell, "verdict", s, dates[s], CJ.joint_events(long_),
                                  {h: CJ.joint_events(x) for h, x in lps.items()}, sub,
                                  lambda h, h_, _l=long_, _x=lps: hh.slice_measures(_l if h is None else _x[h], h_, sub))
        rows.append(r)
        slices += sl
        bad += b
    return {"rows": rows, "slices": slices, "bad": bad}


def _pool(tasks: list[tuple], fn, workers: int, what: str) -> list:
    import customer_journey as CJ

    return CJ._pool_run(tasks, fn, workers, what)


# ------------------------------------------------------------------------------------------------ the runs


def run_paths(X: dict, cell: str, seats: tuple[int, ...], mode: str, blocks: list, shift: str, n_paths: int,
              workers: int) -> list[dict]:
    from propedge.campaign.lockstep import path_seeds

    import rc_screen as S

    setups = firm_setups(X, "camp", seats)
    seeds = list(enumerate(path_seeds(int(S.SEED), int(n_paths))))
    tasks = [(cell, mode, shift, blocks, setups, seeds[j:j + CHUNK_PATHS], X["margin"], X["horizon"])
             for j in range(0, len(seeds), CHUNK_PATHS)]
    recs = [r for chunk in _pool(tasks, _paths_task, workers, f"{cell} {shift}") for r in chunk]
    return sorted(recs, key=lambda r: r["path"])


def readings_of(recs: list[dict], X: dict) -> dict[str, Any]:
    out = hh.readings(recs, margin=X["margin"])
    tb = [np.asarray(r["trades_by_day"], float) for r in recs]
    out["trades_taken_per_session"] = float(np.mean([x[1:].mean() if len(x) > 1 else np.nan for x in tb]))
    closed = [int(r["household_closed_on"]) for r in recs if "household_closed_on" in r]
    if closed:                                         # D-575: Lucid's household rule (the conservative reading)
        hit = [d for d in closed if d >= 0]
        out["household_closed_share"] = float(len(hit) / len(closed))
        out["household_closed_day_p50"] = float(np.median(hit)) if hit else float("nan")
    return out


def _sizes_task(task: tuple) -> list[dict]:
    """(cell, mode, blocks, setups, [(index, seed)], horizon) -> every firm's executed sized trades on these paths: the
    account kind, contracts (micros), the allowance cap, whether it bound, intended and realised risk."""
    import warnings

    warnings.filterwarnings("ignore")
    cell, mode, blocks, setups, items, horizon = task
    rec = [dataclasses.replace(s, path={**s.path, "record_trades": True}) for s in setups]
    specs = [hh.PathSpec(seed=int(sd), blocks=blocks, horizon_days=int(horizon)) for _, sd in items]
    jps = hh.run_joint(specs, rec[0], n_firms=len(rec), mode=mode, doubled=True, firm_setups=rec)
    out = []
    for (i, _), jp in zip(items, jps):
        for f, lp in enumerate(jp.paths):
            for t in lp.trades:
                if t.get("contracts") is None:
                    continue
                out.append({"path": int(i), "firm": f, "kind": str(t["kind"]), "contracts": int(t["contracts"]),
                            "cap_micros": float(t.get("cap_micros") or np.nan), "at_cap": bool(t.get("at_cap")),
                            "intended_risk": float(t.get("intended_risk") or np.nan),
                            "realised_risk": float(t.get("realised_risk") or np.nan),
                            "room_capped": bool(t.get("room_capped", False))})
    return out


def run_sizes(X: dict, cell: str, seats: tuple[int, ...], mode: str, n_paths: int, workers: int) -> list[dict]:
    """D-575: realised contracts per trade by firm and account kind on the first `n_paths` paths at the point."""
    from propedge.campaign.lockstep import path_seeds

    import rc_screen as S

    setups = firm_setups(X, "camp", seats)
    seeds = list(enumerate(path_seeds(int(S.SEED), int(n_paths))))
    blocks = arm_blocks(X, "point")
    tasks = [(cell, mode, blocks, setups, seeds[j:j + CHUNK_PATHS], X["horizon"])
             for j in range(0, len(seeds), CHUNK_PATHS)]
    df = pd.DataFrame([r for chunk in _pool(tasks, _sizes_task, workers, f"{cell} sizes") for r in chunk])
    names = ["topstep"] + [X["second_firm"]] * (len(seats) - 1)
    rows = []
    if not len(df):
        return rows
    for (f, kind), g in df.groupby(["firm", "kind"]):
        c = g["contracts"].astype(float)
        rows.append({"section": "sizes", "cell": cell, "firm": int(f), "firm_name": names[int(f)], "kind": kind,
                     "paths": int(n_paths), "trades": int(len(g)), "micros_mean": float(c.mean()),
                     "micros_p10": float(c.quantile(0.10)), "micros_p50": float(c.median()),
                     "micros_p90": float(c.quantile(0.90)), "micros_max": float(c.max()),
                     "cap_micros_p50": float(g["cap_micros"].median()), "at_cap_share": float(g["at_cap"].mean()),
                     "room_capped_share": float(g["room_capped"].mean()),
                     "realised_over_intended": float(g["realised_risk"].sum() / g["intended_risk"].sum())})
    return rows


def run_journey(X: dict, cell: str, seats: tuple[int, ...], mode: str, starts: int | None, workers: int
                ) -> tuple[list[dict], list[dict], int]:
    import rc_screen as S

    blocks = arm_blocks(X, "lower_bound")
    setups = firm_setups(X, "rep", seats)
    n = len(blocks) if starts is None else min(int(starts), len(blocks))
    tasks = [(cell, mode, blocks, X["days"], setups, int(S.SEED), list(range(j, min(n, j + CHUNK_STARTS))))
             for j in range(0, n, CHUNK_STARTS)]
    res = _pool(tasks, _journey_task, workers, f"{cell} journey")
    return ([r for x in res for r in x["rows"]], [s for x in res for s in x["slices"]], int(sum(x["bad"] for x in res)))


# ------------------------------------------------------------------------------------------------ the identities


def runner_identity(X: dict, n: int, workers: int) -> list[str]:
    """(b): the 5+0 cell through the joint engine against P-16's single-firm engine call (`rc_screen.Runner`) for the
    first `n` paths, both shifts, on PATH_COLS; and its growth on the required bankroll and required bankroll at `n`."""
    import rc_screen as S
    import zero_edge_decomposition as zd

    R = S.Runner(X["I"], workers)
    df = R.run("p16_single", X["t"], X["days"], int(n))
    ref = pd.DataFrame(R.sink)
    mine, problems = [], []
    seats = dict((c, s) for c, s, _ in CELLS)[REFERENCE]
    for shift in SHIFTS:
        recs = run_paths(X, REFERENCE, seats, hh.UNHEDGED, arm_blocks(X, shift), shift, n, workers)
        mine += [{"run": "joint", "shift": shift, "enforcement_p": 0.0, "path": r["path"], **r["firm0"]} for r in recs]
        g = readings_of(recs, X)
        row = df[(df["shift"] == shift) & np.isclose(df["enforcement_p"].astype(float), 0.0)].iloc[0]
        for mine_col, theirs in (("growth_on_required", "pf_growth_on_base_p50"), ("required_p90", "pf_required_p90")):
            a, b = float(g[mine_col]), float(row[theirs])
            if not (abs(a - b) <= TOL or (np.isnan(a) and np.isnan(b))):
                problems.append(f"{shift} {mine_col}: joint {a!r} against the single-firm call's {b!r}")
    problems += zd.path_problems(mine, ref, [("joint", s, "p16_single", s) for s in SHIFTS], int(n))
    return problems


def screen_identity(rows: dict[str, dict], rd: Path) -> list[str]:
    """(c), the full run: the 5+0 cell at 500 paths against `rc_width_screen.csv`'s `rc_s150_all`."""
    from propedge.reporting.results import read_result

    ref = read_result(Path(rd) / "rc_width_screen.csv")
    r = ref[(ref["section"].astype(str) == "cell") & (ref["cell"].astype(str) == "rc_s150_all")]
    if len(r) != 1:
        return [f"rc_width_screen.csv holds {len(r)} rc_s150_all cell rows, not one"]
    r = r.iloc[0]
    out = []
    for mine, theirs in ((rows["lower_bound"]["growth_on_required"], r["growth_on_required"]),
                         (rows["point"]["growth_on_required"], r["growth_on_required_point"]),
                         (rows["lower_bound"]["required_p90"], r["required_p90"])):
        if not abs(float(mine) - float(theirs)) <= TOL:
            out.append(f"5+0 at {N_PATHS} paths: {float(mine)!r} against rc_width_screen.csv's {float(theirs)!r}")
    return out


# ------------------------------------------------------------------------------------------------ the study


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import subprocess

    import customer_slices as cs

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="every identity and cell at --paths; nothing written")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--paths", type=int, default=None, help="test seam (with --check): paths a run")
    ap.add_argument("--starts", type=int, default=None, help="test seam (with --check): replay starts a cell")
    ap.add_argument("--only", default=None, help="test seam (with --check): a comma-separated subset of cells")
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--resume-dir", default=None)
    ap.add_argument("--second-firm", choices=sorted(STUDIES), default="topstep",
                    help="firm 1's contract: topstep (D-567, assumed_second_firm) or lucid (D-575, verified)")
    a = ap.parse_args(argv)
    st = STUDIES[a.second_firm]
    if not a.check and (a.paths is not None or a.starts is not None or a.only is not None):
        print(f"REFUSED ({st.decision}): a reading runs every cell at {N_PATHS} paths and every start; use --check.")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    n_paths = N_PATHS if a.paths is None else int(a.paths)
    id_paths = IDENTITY_PATHS if not a.check else min(IDENTITY_PATHS, n_paths)
    cells = [c for c in st.cells if a.only is None or c[0] in a.only.split(",")]
    t_all = time.time()
    print(f"P-16's cell, the opposite side, the blocks and the engine's arguments (second firm: {st.second_firm})...",
          flush=True)
    X = inputs(st.second_firm)
    print(f"identity HOLDS: the cell = P-16's rc_s150_all ({len(X['t'])} candidates); the opposite side aligned "
          f"({len(X['fa'])} rows)", flush=True)
    bad = runner_identity(X, id_paths, a.workers)
    if bad:
        print(f"REFUSED ({DECISION}): the joint engine's 5+0 is not P-16's single-firm call -- " + "; ".join(bad[:8]))
        return 3
    print(f"identity HOLDS: 5+0 through the joint engine = P-16's single-firm call, the first {id_paths} paths at both "
          "shifts (PATH_COLS), growth and required bankroll", flush=True)
    resume = None
    if not a.check and not a.no_resume:
        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = Resume(folder, f"{commit}_{n_paths}_{a.starts or 'all'}", st.result)
    idents = [{"section": "identity", "check": "the cell's content hash is P-16's (rc150_dev_test.TRADES_SHA256); the "
                                               "opposite side aligned one for one on the other side", "holds": True},
              {"section": "identity", "check": f"5+0 through the joint engine reproduces P-16's single-firm engine call "
                                               f"(rc_screen.Runner) path for path on PATH_COLS for the first {id_paths} "
                                               "paths at both shifts, and its growth and required bankroll there",
               "holds": True}]
    rows: list[dict] = []
    journeys: list[dict] = []
    slice_rows: list[dict] = []
    size_rows: list[dict] = []
    for name, seats, mode in cells:
        t0 = time.time()
        lab = label_of(seats, mode, st)
        per = {}
        for shift in SHIFTS:
            per[shift] = _cached(resume, f"{name}|{shift}", lambda name=name, seats=seats, mode=mode, shift=shift:
                                 readings_of(run_paths(X, name, seats, mode, arm_blocks(X, shift), shift, n_paths,
                                                       a.workers), X))
        tw = _cached(resume, f"{name}|twin", lambda name=name, seats=seats, mode=mode:
                     readings_of(run_paths(X, name, seats, mode, arm_blocks(X, "point", twin=True), "point", n_paths,
                                           a.workers), X))
        if name == REFERENCE and not a.check:
            badc = screen_identity(per, rd)
            if badc:
                print(f"REFUSED ({DECISION}): " + "; ".join(badc))
                return 3
            idents.append({"section": "identity", "holds": True,
                           "check": f"5+0 at {N_PATHS} paths reproduces results/rc_width_screen.csv's rc_s150_all "
                                    "(growth at the bound and the point, required bankroll)"})
        jv = _cached(resume, f"{name}|journey", lambda name=name, seats=seats, mode=mode:
                     dict(zip(("rows", "slices", "bad"), run_journey(X, name, seats, mode, a.starts, a.workers))))
        if int(jv["bad"]):
            print(f"REFUSED ({DECISION}): {name}: {jv['bad']} exact replays whose event days differ from the long run's")
            return 3
        u = pd.DataFrame(jv["rows"])
        cell_sub = max(float(s.path["subscription"]) for s in firm_setups(X, "rep", seats))
        for m in cj.metrics(u, cell_sub):
            journeys.append({"section": "journey", "cell": name, "label": lab, "arm": "verdict",
                             "key": cj.metric_key(m["milestone"], m["measure"], m["at_days"]), **m})
        sl = pd.DataFrame(jv["slices"])
        if len(sl):
            summ = cs.summarise(sl.assign(config=name, arm="verdict"))
            for r in summ.to_dict("records"):
                slice_rows.append({**r, "section": "slices", "cell": name, "label": lab})
        for shift in SHIFTS:
            rows.append({"section": "cell", "cell": name, "label": lab, "mode": mode, "firms": len(seats),
                         "seats": "+".join(str(s) for s in seats), "seats_total": int(sum(seats)),
                         "budgets": "+".join(str(budget_for(s)[0]) for s in seats), "shift": shift,
                         **{k: v for k, v in per[shift].items() if not isinstance(v, (list, dict))}})
        rows.append({"section": "twin", "cell": name, "label": lab, "mode": mode, "seats": "+".join(map(str, seats)),
                     "shift": "point", **{k: v for k, v in tw.items() if not isinstance(v, (list, dict))}})
        if st.second_firm == LUCID:                    # D-575: realised sizes under each firm's limits
            sz = _cached(resume, f"{name}|sizes", lambda name=name, seats=seats, mode=mode:
                         run_sizes(X, name, seats, mode, id_paths, a.workers))
            size_rows += [{**r, "label": lab, "mode": mode, "seats": "+".join(map(str, seats))} for r in sz]
        print(f"  {name}: done ({time.time() - t0:.0f} s)", flush=True)
    secs = time.time() - t_all
    if a.check:
        if st.second_firm == LUCID and not any(r["firm_name"] == LUCID for r in size_rows):
            print(f"REFUSED ({st.decision}): no Lucid trade was sized in the check.")
            return 3
        print(f"every identity holds; cells {[c[0] for c in cells]} ran at {n_paths} paths and "
              f"{'every' if a.starts is None else a.starts} start(s); nothing written, no reading printed (--check). "
              f"{secs:.0f} s")
        return 0
    res = pd.DataFrame(idents + rows + journeys + slice_rows + size_rows)
    res.insert(1, "reading", st.reading)
    hyp = res[res["label"].astype(str) == hh.TAG]
    hh.require_label(hyp.to_dict("records"))
    counter = VariantCounter(path=rd / "variants.jsonl")
    for name, seats, mode in st.cells:
        counter.record(prereg_id=family_of(mode, st), seed=20261131, exploratory=True,
                       params={"study": f"{st.decision}'s seat split on P-16's cell", "cell": name,
                               "seats": list(seats), "mode": mode, "budgets": [budget_for(s)[0] for s in seats],
                               "paths": n_paths, **({} if st.second_firm == "topstep" else
                                                    {"second_firm": st.second_firm})},
                       label=f"{st.decision}'s seat split: {name}" + (f" -- {hh.TAG}" if mode != hh.UNHEDGED else ""))
    params = {"decision": st.decision, "cells": [{"cell": c, "seats": list(s), "mode": m,
                                                  "label": label_of(s, m, st),
                                                  "budgets": [budget_for(x)[0] for x in s]} for c, s, m in st.cells],
              "campaign_seed": 20261131, "coin_seed": 20261102, "n_paths": n_paths, "identity_paths": id_paths,
              "budget_rule": "floor(20 x seats / 5) purchases and resets in 21 trading days, per firm",
              "second_firm": SECOND_FIRM_NOTE[st.second_firm],
              "hedge": "D-514's deal: the lead leg and the other firm's account in its slot on the opposite side; a slot "
                       "with no account at the other firm trades alone (counted)",
              "bound": "the cell at its 0.05 bound, the opposite side mirrored (hypo_hedge.mirror_shift)",
              "journey": "customer_journey's units and metrics on the bound arm's replay, every start",
              "seconds": round(secs, 1), "workers": int(a.workers)}
    if st.second_firm == LUCID:
        from propedge.contract.lucid import STANDARD_40, lucid_provenance

        params["lucid"] = lucid_provenance(STANDARD_40)
        params["journey_margin"] = "one evaluation of the dearest firm in the cell"
        params["sizes"] = f"realised contracts per trade, the first {id_paths} paths at the point"
    write_result(res, st.result, script=SCRIPT, seed=20261131, exploratory=True, results_dir=results_dir,
                 variant_count=len(st.cells), parameters=params,
                 notes={"status": st.reading, "labels": f"{hh.TAG} rows are prohibited conduct, never a candidate; "
                                                        + LABEL_NOTE[st.second_firm]},
                 description=f"EXPLORATORY ({st.decision}): P-16's cell with its seats split over two firms "
                             f"({', '.join(c for c, s, m in st.cells if len(s) > 1 and m == hh.UNHEDGED)}) against "
                             "one firm (5+0, 4+0), unhedged and hedged (hypothetical_hedge); growth on the required "
                             "bankroll, the deal's shares, pass and payout steadiness, D-518's journey"
                             + ("; realised sizes under each firm's limits." if st.second_firm == LUCID else "."))
    print(f"written: {st.result}.csv ({secs:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
