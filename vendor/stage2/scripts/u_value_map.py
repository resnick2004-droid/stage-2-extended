"""EXPLORATORY (D-668; program U's U5): the contract's value map -- for each base design (P-14, A3-BRK30-CB20 on its
12.5- and 25-point rungs; P-16, `rc_s150_all` on its 37.5-point stop), its state table re-solved at $50K as D-667
solved it at the bound edge, read state by state: each state's value, the leaf the table trades there, the value
after that leaf's win less after its loss, the extra win probability that is worth a dollar there; where accounts spend
their days (the solver's own forward, and beside it the registered campaigns' records); the campaign value of one
percentage point of win probability in each place of an account's life; and the bar a signal of a given frequency
must clear. A reading of the solved tables: no campaign is run for it, no variant counted, nothing selected.

    python scripts/u_value_map.py --check               # every self-identity and the pipeline at a short horizon
                                                        #   (42 sessions) and 4 recorded paths; D-667's file is not
                                                        #   compared (other horizon); written to a temporary folder,
                                                        #   since removed
    python scripts/u_value_map.py                       # the read (one worker; from a clean checkout, D-474)

**What is solved.** `scripts/u_size_fit.py`'s own pieces, imported unchanged: its inputs (`load_inputs`: the
no-closure table's config, each base's rungs and each R's registered bound edge, `lb_gate`), its static identities and
$50K oracles, its two table identities (the table on file and D-559's), and its `solve` (lambda*, the tie-broken table
at it, through the per-R classes) at $50K only, the bound edge set. Then, per base, `propedge/research/u_value_map.py`:
the table's day loop run again with each day's closing values kept (`backward`; the funded table's on a temporary
memory-mapped file, removed after), and the fresh evaluation and the fresh funded account run forward under it
(`forward`), the leaf's terms read at every state holding mass on every day.

**Identities first, each refusing; nothing is written if one fails:**

* D-667's (`u_size_fit.static_identities`, `oracles_50k_identity`, `identity_solves`): the $50K rules, sizing and
  menus are v12's no-closure ones; the bases' rungs and edges are their gates'; the $50K oracles equal
  `state_policy_dp.oracles`' and hold 16/49, 0.327131, 2/5 and $2,000; the table on file and D-559's table are
  reproduced (the whole exported tree, the rent to 1e-9);
* the solver's code is D-667's: `state_policy.py`, `state_policy_dp.py`, `u_size_fit` (module and script),
  `a3_compliance.py` and `rc150_table_screen.py` are unchanged since D-667's commit (`git diff --quiet`);
* **the re-solve is D-667's $50K bound solve:** its rent lambda* and every reading D-667 wrote for that solve
  (`results/u_size_fit.csv`, section `reading`, 50k, bound: P(pass), payouts, fees, the sessions to a first payout, ...)
  equal the file's to 1e-9. D-667 wrote no table for its bound solves (only for its identity set), so the exported
  table's sha256 is recorded here for whoever reproduces it;
* the backward re-run is the solve: the same action and payout choice in every state on every day, the same fresh
  value; **the Bellman identity** -- every live state's value equals its leaf's expected continuation -- to 1e-6 on
  every state and day; **the values inside the bounds**: every edge being at or below zero, no funded state is worth
  more than the split times its cushion, no evaluation state more than the best pass, and (stage one's) the fresh
  evaluation's P(pass) at most 0.327131 and a funded account's expected gross payouts at most $2,000;
* the forward is the solver's: P(pass), failure, abandonment, days and days to the pass (the Combine); cash, gross,
  payouts, the share paid and closed, days (funded) equal `forward`'s to 1e-9 and its visitation exactly; **the
  occupancy's shares sum to one in every phase** (its account-days are the forward's days); **the expected sessions
  to a first payout** (the Combine's days to its pass plus the funded account's days to its first payout) equal
  D-667's `sessions_to_first_payout` for the base to 1e-6;
* the records (beside): U2's builders and campaign (`scripts/u_xfa_day_budget.py`, unchanged since D-650's 8d8e73b),
  the trades' pins and the settings as U2 checks them, and each re-run path's figures equal the registered per-path
  row (100 paths, the bound arm, 0 %).

**The file** `results/u_value_map.csv` (EXPLORATORY; no variant recorded; no seed of its own -- the solves are an
exact chain, the records' paths are drawn at each design's registered campaign seed), long format:
`section, base, phase, state, measure, value, n, unit, note`.

* `identity` -- each check, value 1 when it held (`note` says what);
* `definitions` -- per measure, its plain meaning and how it is modelled (`note`), its unit;
* `solve` -- per base: lambda*, the exported table's sha256 (`note`), P(pass), the funded account's expected gross
  payouts, the slot-days an attempt holds, attempts a seat-year;
* `phase` -- per base and phase: account-days and trades per account, the trade-weighted mean dv, the share of trade
  mass where dv < 0 (`dv_negative_trade_share`), the least dv, the fresh state's value, the states held;
* `state` -- per base, phase and state (`state` the compact key: `B=..|F=..` for the evaluation, `B=..|F=..|W=..|Q=..`
  for a funded account, `B=..|ref=..|W=..|Q=..` for a paid one -- balance and floor or last-payout balance relative to
  the start, winning days, request-day flag): `occupancy_share` (`n`: its expected account-days per account),
  `value`, `leaf_risk`, `leaf_rr` (blank without a trade), `leaf_max_trades`, `leaf_share`, `p_trade`, `dv`,
  `edge_per_dollar` (blank where no trade or dv <= 0). Only the states holding at least `STATE_KEEP_SHARE` of their
  phase's account-days are listed; `phase` rows `states_listed`, `states_held` and `share_listed` say how much is shown;
* `band` -- per base, phase and the exported table's band key (`bb=..|cb=..`): `solver_share` and `records_share` of
  the phase's account-days (the records: U2's re-run of the registered campaign, which trades the table on file, not
  this re-solve -- a comparison of where accounts are, not of decisions);
* `records_leaf` -- per base, phase and the engine's leaf name: its share of the phase's recorded account-days;
* `place_values` -- per base and place (a to e): `trades_per_attempt`, `mean_dv`, `dollars_per_trade` (of +1 point),
  `trades_per_year_forward`, `dollars_per_year_forward`, `trades_per_year_records`, `dollars_per_year_records`;
* `bar` -- per base, basis (`forward` / `records`), place (`best_place` / `every_trade`), frequency and target:
  `extra_win_prob_points` (`n`: the uses a year, `note`: the place, and whether its supply caps the uses).

The manifest records the read files' sha256 (D-667's result, the policies files, the gates, the per-path records),
each solve's and pass's seconds and the process's peak memory, the exported tables' sha256 and every interpretation.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
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

from propedge.campaign import state_policy as sp  # noqa: E402
from propedge.research import u_size_fit as U  # noqa: E402
from propedge.research import u_value_map as UV  # noqa: E402

SCRIPT = "scripts/u_value_map.py"
RESULT = "u_value_map"
D667_RESULT = "u_size_fit.csv"
D667_COMMIT = "99c1c7d"
D650_COMMIT = "8d8e73b"
SOLVER_FILES = ("propedge/campaign/state_policy.py", "scripts/state_policy_dp.py", "propedge/research/u_size_fit.py",
                "scripts/u_size_fit.py", "scripts/a3_compliance.py", "scripts/rc150_table_screen.py")
RECORD_FILES = ("scripts/u_xfa_day_budget.py", "propedge/research/u_xfa_day_budget.py")
SIZE = "50k"
EDGE_SET = "bound"
ARM = "verdict"                            # U2's name of the gate row's lower-bound arm
CHECK_HORIZON = 42
CHECK_PATHS = 4
PATHS = 100
STATE_KEEP_SHARE = 1e-4                    # a state listed when it holds at least this share of its phase's days
TOL = 1e-9
TOL_SESSIONS = 1e-6
STAGE_ONE_SUP = 0.327131
STAGE_ONE_GROSS = 2000.0

INTERPRETATIONS = (
    "The re-solve is D-667's own solve (scripts/u_size_fit.solve) at $50K and the bound edge set; D-667 wrote no table "
    "for its bound solves, so 'equals D-667's solve' is checked on its rent and every reading it wrote for that solve "
    "(to 1e-9), with the solver's code unchanged since D-667's commit; the exported table's sha256 is recorded.",
    "The solver's outcome is binary per rung: a win (its target at the action's R on the $50 grid, or in the "
    "evaluation the need-aware or consistency exit the solver applies) or a loss of the realised stake (cut to the "
    "room; at the floor the account ends, worth 0); the race against the floor lowers p and adds no outcome. The "
    "gate's shifted outcome distribution enters only as each R's lower win probability (its lb_by_rr); the solver has "
    "no intraday partial outcomes (no scratch, time exit or partial fill). dv is the value after the win outcome less "
    "after the stop outcome.",
    "dv is read at the next session's value: for a funded or paid account the value at the close after the trade, the "
    "table's payout choice there included; for the evaluation the next session's value, a pass worth the funded "
    "account's value over the days left less the activation fee (the solver's pass value).",
    "dv per state and day is averaged over the rungs by the rung's share times the share of its trades offering the "
    "action's R (conditional on a trade being taken); p_trade is that weight's sum. Per state, value and p_trade are "
    "occupancy-weighted over the days the state is held and dv is trade-weighted (occupancy x p_trade); the leaf "
    "shown is the action holding most of the state's occupancy.",
    "Values are the solver's objective: expected cash within the 504-session horizon less lambda* a live account-day "
    "(the evaluation's subscription accrued per day as well).",
    "The occupancy is the solver's forward: a fresh evaluation run to its pass, failure or abandonment; a fresh funded "
    "account run over the whole horizon from session 0 (the table's cycle accounting, as D-667's readings and "
    "state_policy_dp.cycle_rate read it), its unpaid states up to its first payout and its paid states after. A "
    "session on which the table abandons holds no account-day.",
    "The place values are first-order: with the table held fixed, +dp on every trade of a place changes an attempt's "
    "value by dp x sum(occupancy x p_trade x dv) over the place (exact at a fixed table, tested against a perturbed "
    "table; a re-solved table gains the same to first order). Per trade affected: dp x the trade-weighted mean dv.",
    "Place (c), the funded opening, is each funded account's first trade: the forward's mass at the fresh state that "
    "has never traded (every trade leaves the fresh state, so this is a layer of its own); (d) is the rest of the "
    "unpaid states' trades; (e) the paid states'; (b) the evaluation's; (a) all of them, a funded place per attempt "
    "counted at P(pass) times its funded figure.",
    "Per year of a five-seat campaign, forward basis: trades of the place an attempt x attempts a seat-year (252 "
    "sessions over the slot-days an attempt holds: the evaluation's days plus P(pass) times the funded account's, as "
    "cycle_rate counts them) x 5 seats -- the table's model, every seat an independent account trading whenever its "
    "leaf trades. Records basis, beside: the place's trades a year in U2's re-run of the registered campaign (its "
    "first 100 paths at the bound arm, 504 sessions = 2 years), whose router, budget and strict one-at-a-time rule "
    "limit the trades -- and which trades the table on file (solved at FV3-C's single edge), not this re-solve.",
    "The bar: extra win probability = target / (uses x the place's mean dv), uses = the frequency N or, where the place "
    "offers fewer trades a year on that basis, that supply (flagged 'capped'); the best place is the single place "
    "(b to e) with the highest mean dv; 'every trade' uses place (a).",
    "The records' state at a session's start is the account's previous recorded close (the fresh start on its first "
    "session); it is banded by the exported table's bands, because the engine's balances leave the $50 grid (costs) "
    "and its records carry no winning-day count; a funded session is 'paid' after the session of the first payout "
    "request (the engine's first_payout_day).",
    f"The state section lists the states holding at least {STATE_KEEP_SHARE:g} of their phase's account-days; the "
    "phase rows give how many states are held and the share listed. Every phase total and place value uses every "
    "state.",
)

UNITS = {"occupancy_share": "share", "value": "dollars", "leaf_risk": "dollars", "leaf_rr": "R",
         "leaf_max_trades": "count", "leaf_share": "share", "p_trade": "probability", "dv": "dollars",
         "edge_per_dollar": "probability"}

DEFINITIONS = (
    ("occupancy_share", "share",
     "The share of all account-days in this phase that are spent in this state.",
     "The solver's own forward: a fresh account run under the table, its expected days in the state over its expected "
     "days in the phase (n: the expected account-days per account)."),
    ("value", "dollars",
     "What an account in this state is worth to the trader from this session on, under the table.",
     "The solver's value: expected cash to the end of the 504-session horizon (payouts net of the split and the "
     "method's fee, less fees and the slot rent lambda* a live day), averaged over the days the state is held."),
    ("leaf_risk", "dollars", "The dollar risk the table takes in this state.",
     "The table's action in the state on most of the days the state is held; the realised risk is whole micros at the "
     "base's stops under the allowance."),
    ("leaf_rr", "R", "The reward-to-risk target the table takes in this state (blank: no trade).",
     "The action's R; in the evaluation a win may close earlier, at what the pass needs or at the day's consistency "
     "allowance, as the solver models it."),
    ("leaf_max_trades", "count", "How many trades the table allows in the state this session (0: it sits out).",
     "1 for a trade, 0 for no trade or abandoning the attempt: the table models one trade a session."),
    ("leaf_share", "share", "How much of the state's time the shown leaf holds.",
     "The share of the state's occupancy on its most common action (the table can change its decision by day)."),
    ("p_trade", "probability", "The chance the table's trade actually happens on a session in this state.",
     "The rungs' shares times the share of each rung's trades offering the action's R (a day without the R is a day "
     "without a trade), over the days the state is held."),
    ("dv", "dollars", "What winning this trade is worth over losing it: the value after a win less the value after a "
                      "loss.",
     "From the solver's own transition: the next state after the full win and after the full loss of the leaf at "
     "each rung (a loss to the floor ends the account, worth 0), each at the next session's value; averaged over the "
     "rungs and days by the trades taken."),
    ("edge_per_dollar", "probability", "How much extra win probability on this trade would be worth one dollar.",
     "1 / dv; blank where the table takes no trade or dv is not positive."),
    ("trades_per_attempt", "count", "How many trades of this kind one attempt (an evaluation and, if it passes, its "
                                    "funded account) holds on average.",
     "The forward's expected trades of the place; a funded place counts the pass probability times its funded "
     "account's figure."),
    ("mean_dv", "dollars", "What one won trade of this kind is worth over a lost one, on average.",
     "The trade-weighted mean of dv over the place's states and days."),
    ("dollars_per_trade", "dollars", "What one extra percentage point of win probability is worth on one trade of "
                                     "this kind.",
     "0.01 x mean_dv: first-order, the table held fixed."),
    ("trades_per_year_forward", "count", "How many trades of this kind a five-seat campaign takes in a year, in the "
                                         "table's model.",
     "Trades an attempt x attempts a seat-year (252 sessions over the slot-days an attempt holds) x 5 seats."),
    ("dollars_per_year_forward", "dollars", "What one extra percentage point on every trade of this kind adds to a "
                                            "five-seat campaign in a year, in the table's model.",
     "dollars_per_trade x trades_per_year_forward."),
    ("trades_per_year_records", "count", "How many trades of this kind the registered campaign took in a year.",
     "U2's re-run of the registered gate campaign (100 paths, the bound arm, 504 sessions): the place's trades over "
     "the path-years; its router, budget and one-position-at-a-time rule limit them."),
    ("dollars_per_year_records", "dollars", "The same year's value counted on the registered campaign's trades.",
     "dollars_per_trade (the solver's) x trades_per_year_records."),
    ("extra_win_prob_points", "percentage points",
     "The extra win probability a signal firing N times a year needs, spent in the named place, to add the target "
     "dollars a year to a five-seat campaign.",
     "target / (uses x mean_dv) x 100, uses = N, or the place's trades a year where fewer (then 'capped'); first-order, "
     "the table held fixed."),
    ("solver_share", "share", "The share of the phase's account-days the solver's forward spends in this band.",
     "The solver's occupancy summed over the states in the exported table's balance and cushion band."),
    ("records_share", "share", "The share of the phase's recorded account-days spent in this band.",
     "U2's re-run of the registered campaign: each account-day's state at the session's start (the previous close), "
     "banded as the table's export bands it."),
    ("records_leaf_share", "share", "The share of the phase's recorded account-days on which the engine's table chose "
                                    "this leaf.",
     "The leaf name the engine recorded for the session (its regime), in U2's re-run of the registered campaign."),
)


# ------------------------------------------------------------------------------------------------ rows


class Rows:
    def __init__(self):
        self.rows: list[dict[str, Any]] = []

    def add(self, section: str, measure: str, value, *, base: str = "", phase: str = "", state: str = "", n=None,
            unit: str = "", note: str = "") -> None:
        v = float("nan") if value is None else float(value)
        self.rows.append({"section": section, "base": base, "phase": phase, "state": state, "measure": measure,
                          "value": v, "n": n, "unit": unit, "note": note})

    def ident(self, check: str, note: str, *, base: str = "") -> None:
        self.add("identity", "holds", 1.0, base=base, state=check, note=note)
        print(f"identity HOLDS: {base + ': ' if base else ''}{check} -- {note}", flush=True)


def refuse(msg: str) -> None:
    raise SystemExit(f"REFUSED ({UV.DECISION}): {msg}")


def _git_unchanged(commit: str, files: tuple[str, ...]) -> bool:
    r = subprocess.run(["git", "diff", "--quiet", commit, "HEAD", "--", *files], cwd=ROOT, capture_output=True)
    if r.returncode not in (0, 1):
        refuse(f"git diff against {commit} failed: {r.stderr.decode(errors='replace').strip()}")
    st = subprocess.run(["git", "status", "--porcelain", "--", *files], cwd=ROOT, capture_output=True, text=True)
    return r.returncode == 0 and not st.stdout.strip()


def _close(a: float, b: float, tol: float) -> bool:
    if np.isnan(a) and np.isnan(b):
        return True
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))


def _policy_sha(pol) -> str:
    d = json.loads(json.dumps(pol.as_dict(), default=lambda x: x.item() if isinstance(x, np.generic) else str(x)))
    return hashlib.sha256(json.dumps(d, sort_keys=True).encode("utf-8")).hexdigest()


# ------------------------------------------------------------------------------------------------ one base's map


def value_map(base: str, I: dict, sizes: dict, out: Rows, cost: dict, *, horizon: int | None, d667: pd.DataFrame | None,
              tables: dict) -> dict[str, Any]:
    """The base's re-solve, its identities, its backward and forward passes and its rows; returns what the place
    values and the band comparison need."""
    import state_policy_dp as dp
    import u_size_fit as SF

    b = I["bases"][base]
    S = sizes[SIZE]
    cfg_s = dict(S["cfg"])
    if horizon is not None:
        cfg_s = {**cfg_s, "horizon_days": int(horizon)}
    rules = S["rules"]
    rungs = U.rungs_for_size(b["rungs"], S["sizing"])
    menu = U.size_menu(cfg_s, dp.menu_of(I["noclose"]), rungs)
    edges = b["edges"]
    scalar = float(edges[min(edges, key=lambda k: abs(k - I["fresh_fr"]))])
    print(f"{base}: the $50K bound solve (D-667's) ...", flush=True)
    s = SF.solve(cfg_s, rules, menu, edges, scalar)
    lam, rd = s["lam"], s["readings"]
    f, fsol, ff, c, csol, cf = s["objs"]
    cost[base] = {"solve_seconds": round(s["seconds"], 1), "solve_peak_mb": round(s["peak_mb"], 1),
                  "nS_funded": int(f.nS), "nS_combine": int(c.nS), "nA_funded": len(f.actions),
                  "nA_combine": len(c.actions), "rungs": int(f.nR), "rent_rounds": len(s["rounds"])}
    print(f"  lambda* {lam:.6f} in {len(s['rounds'])} rounds, {s['seconds']:.0f} s", flush=True)
    if d667 is not None:
        sel = d667[(d667["size"] == SIZE) & (d667["base"] == base) & (d667["edge"] == EDGE_SET)]
        rent = sel[sel["section"] == "rent"]
        reads = sel[sel["section"] == "reading"]
        if len(rent) != 1 or len(reads) != len(rd):
            refuse(f"{D667_RESULT} holds {len(rent)} rent rows and {len(reads)} readings for {base} at {SIZE} {EDGE_SET} "
                   f"(the solve gives {len(rd)})")
        bad = [] if _close(lam, float(rent["value"].iloc[0]), TOL) else ["lambda_star"]
        for r in reads.itertuples():
            if r.measure not in rd or not _close(float(rd[r.measure]), float(r.value), TOL):
                bad.append(str(r.measure))
        if bad:
            refuse(f"{base}: the re-solve is not D-667's $50K bound solve -- {bad}")
        out.ident("d667_bound_solve", f"the re-solve's lambda* and all {len(rd)} readings D-667 wrote for its $50K "
                                      f"bound solve of {base} (results/{D667_RESULT}) equal the file's to {TOL:g}",
                  base=base)
    T = int(cfg_s["horizon_days"])
    bands = I["noclose"]["export"]
    pol, _ = sp.export_policy(f"u_value_map_{base}_bound_50k", c, cf["visitation"], f, ff["visitation"],
                              float(bands["balance_band"]), float(bands["cushion_band"]), version=12,
                              c_pol0=csol.policy[0], f_pol0=fsol.policy[0],
                              description=dp.export_description(cfg_s, scalar, lam, 12))
    tables[base] = _policy_sha(pol)
    del pol
    out.add("solve", "lambda_star", lam, base=base, unit="dollars/slot-day", note="D-667's $50K bound solve")
    out.add("solve", "exported_table_sha256", float("nan"), base=base, note=tables[base])
    split, mll = float(rules.profit_split), float(rules.mll)
    edges_nonpos = max(float(v) for v in edges.values()) <= 1e-12
    # ---- the evaluation
    t0 = time.time()
    pv = fsol.fresh_value[1:T + 1] - rules.activation
    store_c = np.zeros((T, c.nS + 3))
    bc = UV.backward(c, csol, rules, store_c, pass_value=pv)
    fwc = UV.forward(c, csol, rules, store_c)
    # ---- the funded account (its closing values on a temporary memory-mapped file)
    tmp = Path(tempfile.mkdtemp(prefix="u_value_map_"))
    try:
        store_f = np.lib.format.open_memmap(tmp / "ext.npy", mode="w+", dtype=np.float64, shape=(T, f.nS + 3))
        bf = UV.backward(f, fsol, rules, store_f)
        store_f.flush()
        fwf = UV.forward(f, fsol, rules, store_f)
        del store_f
        gc.collect()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    cost[base]["map_seconds"] = round(time.time() - t0, 1)
    peak, _ = __import__("u_xfa_day_budget").memory_mb()
    cost[base]["peak_mb_after_map"] = round(peak, 1)
    print(f"  the value map's passes: {time.time() - t0:.0f} s; peak {peak:.0f} MB", flush=True)
    # ---- identities of the passes
    for name, bk in (("evaluation", bc), ("funded", bf)):
        if bk["policy_differs"] or bk.get("payout_differs") or bk["fresh_value_max_diff"] != 0.0:
            refuse(f"{base} {name}: the re-run differs from the solve ({bk})")
        if not bk["bellman_max_abs"] <= UV.TOL_BELLMAN:
            refuse(f"{base} {name}: the Bellman identity fails by {bk['bellman_max_abs']!r}")
    out.ident("rerun_is_solve", "the table's day loop run again gives the same action and payout choice in every state "
                                "on every day and the same fresh value, evaluation and funded", base=base)
    out.ident("bellman", f"every live state's value equals its leaf's expected continuation on every day, to "
                         f"{UV.TOL_BELLMAN:g} (largest gap: evaluation {bc['bellman_max_abs']:.3g}, funded "
                         f"{bf['bellman_max_abs']:.3g} dollars)", base=base)
    if edges_nonpos:
        if not (bf["value_over_bound_max"] <= 1e-6 and bc["value_over_bound_max"] <= 1e-6):
            refuse(f"{base}: a value outside its bound (funded {bf['value_over_bound_max']!r} over split x cushion, "
                   f"evaluation {bc['value_over_bound_max']!r} over the best pass)")
        if not (fwc["p_pass"] <= STAGE_ONE_SUP + 1e-9 and fwf["gross"] <= STAGE_ONE_GROSS + 1e-9):
            refuse(f"{base}: stage one's bounds fail (P(pass) {fwc['p_pass']!r}, gross {fwf['gross']!r})")
        out.ident("value_bounds", "every edge at or below zero: no funded state is worth more than the split times its "
                                  "cushion, no evaluation state more than the best pass; P(pass) at most 0.327131 and "
                                  "a funded account's expected gross payouts at most $2,000 (stage one)", base=base)
    else:
        refuse(f"{base}: an R's bound edge is positive; D-668's bounds are read at edges at or below zero")
    bad = [k for k, theirs in (("p_pass", "p_pass"), ("p_fail", "p_fail"), ("p_abandon", "p_abandon"),
                               ("days", "mean_days"), ("days_to_pass", "mean_days_to_pass"))
           if not _close(fwc[k], cf[theirs], TOL)]
    bad += ["evaluation visitation"] if not np.array_equal(fwc["vis"], cf["visitation"]) else []
    bad += [k for k, theirs in (("cash", "mean_cash"), ("gross", "mean_gross_paid"), ("n_pay", "mean_payouts"),
                                ("p_paid", "p_paid"), ("p_closed", "p_closed"), ("days", "mean_days"))
            if not _close(fwf[k], ff[theirs], TOL)]
    bad += ["funded visitation"] if not np.array_equal(fwf["vis"], ff["visitation"]) else []
    if bad:
        refuse(f"{base}: the forward is not the solver's -- {bad}")
    out.ident("forward_is_solvers", "the forward's P(pass), failure, abandonment, days and days to the pass (evaluation) "
                                    "and cash, gross, payouts, share paid and closed, days (funded) equal the solver's "
                                    f"forward to {TOL:g}, its visitation exactly", base=base)
    masks = {**UV.phase_masks(c), **UV.phase_masks(f)}
    tot = {ph: UV.phase_totals(fwc if ph == "combine" else fwf, masks[ph]) for ph in UV.PHASES}
    sums = {"combine": (tot["combine"]["days"], fwc["days"]),
            "funded+paid": (tot["funded"]["days"] + tot["paid"]["days"], fwf["days"])}
    for ph, (a, bb) in sums.items():
        if not _close(a, bb, TOL):
            refuse(f"{base}: the {ph} occupancy sums to {a!r} account-days, the forward's {bb!r}")
    shares_sum = {ph: float((fwc if ph == "combine" else fwf)["occ"][masks[ph]].sum() / tot[ph]["days"])
                  for ph in UV.PHASES if tot[ph]["days"] > 0}
    if any(not _close(v, 1.0, TOL) for v in shares_sum.values()):
        refuse(f"{base}: a phase's occupancy shares do not sum to one: {shares_sum}")
    out.ident("occupancy_sums", "each phase's occupancy shares sum to one; the evaluation's account-days are the "
                                "forward's days, the funded and paid ones together the funded forward's", base=base)
    if not _close(fwf["open_trades"], 1.0 - fwf["never_traded"], TOL):
        refuse(f"{base}: the opening layer does not add up")
    sessions = fwc["days_to_pass"] + fwf["days_to_first_payout"]
    if not _close(sessions, float(rd["sessions_to_first_payout"]), TOL_SESSIONS):
        refuse(f"{base}: the forward's sessions to a first payout {sessions!r}, the solve's {rd['sessions_to_first_payout']!r}")
    if d667 is not None:
        ref = d667[(d667["section"] == "reading") & (d667["size"] == SIZE) & (d667["base"] == base)
                   & (d667["edge"] == EDGE_SET) & (d667["measure"] == "sessions_to_first_payout")]
        if len(ref) != 1 or not _close(sessions, float(ref["value"].iloc[0]), TOL_SESSIONS):
            refuse(f"{base}: the forward's sessions to a first payout {sessions!r} are not D-667's")
        out.ident("sessions_to_first_payout", f"the forward's expected sessions to a first payout ({sessions:.6f}: the "
                                              "evaluation's days to its pass plus the funded account's days to its "
                                              f"first payout) equal D-667's sessions_to_first_payout to {TOL_SESSIONS:g}",
                  base=base)
    # ---- the solve's and the phases' rows
    days_attempt = float(cf["mean_days"] + cf["p_pass"] * ff["mean_days"])
    out.add("solve", "p_pass", fwc["p_pass"], base=base, unit="probability")
    out.add("solve", "gross_payouts_per_funded", fwf["gross"], base=base, unit="dollars")
    out.add("solve", "slot_days_per_attempt", days_attempt, base=base, unit="sessions",
            note="the evaluation's days plus P(pass) x the funded account's (state_policy_dp.cycle_rate)")
    out.add("solve", "attempts_per_seat_year", UV.SESSIONS_PER_YEAR / days_attempt, base=base, unit="count",
            note="252 sessions over the slot-days an attempt holds")
    out.add("solve", "sessions_to_first_payout", sessions, base=base, unit="sessions")
    for ph in UV.PHASES:
        dpo, fw = (c, fwc) if ph == "combine" else (f, fwf)
        m = masks[ph]
        t = tot[ph]
        held = np.flatnonzero(m & (fw["occ"] > 0))
        share = fw["occ"][held] / t["days"]
        keep = held[share >= STATE_KEEP_SHARE]
        out.add("phase", "account_days_per_account", t["days"], base=base, phase=ph, unit="sessions",
                note="per evaluation attempt" if ph == "combine" else "per funded account")
        out.add("phase", "trades_per_account", t["trades"], base=base, phase=ph, unit="count")
        out.add("phase", "mean_dv", t["dsum"] / t["trades"] if t["trades"] > 0 else None, base=base, phase=ph,
                unit="dollars", note="trade-weighted over the phase's states and days")
        out.add("phase", "dv_negative_trade_share", t["neg"] / t["trades"] if t["trades"] > 0 else None, base=base,
                phase=ph, unit="share", note="the share of the phase's trade mass where the win is worth less than "
                                             "the loss")
        out.add("phase", "states_held", len(held), base=base, phase=ph, unit="count")
        out.add("phase", "states_listed", len(keep), base=base, phase=ph, unit="count",
                note=f"those holding at least {STATE_KEEP_SHARE:g} of the phase's account-days")
        out.add("phase", "share_listed", float(fw["occ"][keep].sum() / t["days"]), base=base, phase=ph, unit="share")
        if ph != "paid":
            out.add("phase", "fresh_state_value", (csol if ph == "combine" else fsol).value, base=base, phase=ph,
                    unit="dollars", note="the fresh state's value on session 0")
        keys = UV.state_keys(dpo, keep)
        for s, key in zip(keep, keys):
            occ = float(fw["occ"][s])
            vis = fw["vis"][s]
            a = int(np.argmax(vis))
            r, R = dpo.actions[a]
            trade = r > 0
            pt = float(fw["tsum"][s] / occ)
            dv = float(fw["dsum"][s] / fw["tsum"][s]) if fw["tsum"][s] > 0 else float("nan")
            out.add("state", "occupancy_share", occ / t["days"], base=base, phase=ph, state=key, n=occ, unit="share")
            out.add("state", "value", float(fw["vsum"][s] / occ), base=base, phase=ph, state=key, unit="dollars")
            out.add("state", "leaf_risk", r if trade else 0.0, base=base, phase=ph, state=key, unit="dollars",
                    note="abandon" if r < 0 else ("" if trade else "no trade"))
            out.add("state", "leaf_rr", R if trade else None, base=base, phase=ph, state=key, unit="R")
            out.add("state", "leaf_max_trades", 1.0 if trade else 0.0, base=base, phase=ph, state=key, unit="count")
            out.add("state", "leaf_share", float(vis[a] / vis.sum()), base=base, phase=ph, state=key, unit="share")
            out.add("state", "p_trade", pt, base=base, phase=ph, state=key, unit="probability")
            out.add("state", "dv", dv, base=base, phase=ph, state=key, unit="dollars")
            out.add("state", "edge_per_dollar", 1.0 / dv if (np.isfinite(dv) and dv > 0) else None, base=base,
                    phase=ph, state=key, unit="probability")
    for ph, fw in (("combine", fwc), ("funded", fwf)):
        out.add("phase", "least_dv", fw["min_dv"], base=base, phase="combine" if ph == "combine" else "funded+paid",
                unit="dollars", note="the least dv over every state and day holding a trade")
    sb = {**UV.solver_bands(c, fwc, float(bands["balance_band"]), float(bands["cushion_band"]), mll),
          **UV.solver_bands(f, fwf, float(bands["balance_band"]), float(bands["cushion_band"]), mll)}
    res = {"tot": tot, "opening": {"trades": fwf["open_trades"], "dsum": fwf["open_dsum"]}, "p_pass": fwc["p_pass"],
           "days_attempt": days_attempt, "bands": sb, "rules": rules}
    del s, f, fsol, ff, c, csol, cf, store_c, fwc, fwf
    gc.collect()
    return res


# ------------------------------------------------------------------------------------------------ the records


def records(base: str, rd: Path, n_paths: int, bands: dict, out: Rows, cost: dict) -> dict[str, Any]:
    """U2's re-run of the base's registered gate campaign at the bound arm, its records read into day counts by band
    and leaf and trades by place; the identities U2 applies, refusing."""
    import customer_slices as cs
    import u_xfa_day_budget as UXS

    from propedge.campaign.lockstep import path_seeds

    t0 = time.time()
    d = UXS.DESIGN_DEFS[base]
    X = UXS.BUILDERS[base](rd)
    kw = UXS.gate_arguments(X, n_paths)
    camp = UXS.campaign_of(base, kw, X["days"])
    args = {arm: UXS.engine_args(camp, arm) for arm in UXS.ARMS}
    bad = list(X["trade_problems"]) + UXS.setting_problems(rd, d, kw, args, kw["seed"])
    if bad:
        refuse(f"{base} records: {bad[:4]}")
    out.ident("records_inputs", f"the trades are the registered run's ({X['trade_check']}); the campaign's settings "
                                f"are results/{d['gate_file']}'s gate rows at 0 % and its seed the registered "
                                f"{kw['seed']}", base=base)
    del X
    gc.collect()
    rules = kw["rules"]
    mll = float(rules.mll)
    blk = cs.arm_blocks(camp, ARM)
    a = args[ARM]
    days: Counter = Counter()
    leaves: Counter = Counter()
    places: Counter = Counter()
    figures = []
    for i, seed in enumerate(path_seeds(int(kw["seed"]), int(n_paths))):
        x, _ = UXS.one_path(blk, a, seed)
        figures.append(UXS.path_figures(i, x))
        r = UV.records_counts(x.account_days, x.trades, x.funded, combine_floor0=-mll,
                              funded_floor0=float(rules.xfa_mll_start), balance_band=float(bands["balance_band"]),
                              cushion_band=float(bands["cushion_band"]), mll=mll)
        days.update(r["days"])
        leaves.update(r["leaves"])
        places.update(r["places"])
        del x
    ref = UXS._text(rd, d["paths_file"])
    pbad = UXS.path_problems(figures, ref, UXS.DB.SHIFT_OF[ARM])
    if pbad:
        refuse(f"{base} records: {pbad[:4]}")
    if places.get("other", 0):
        refuse(f"{base} records: {places['other']} trades of an unknown kind")
    out.ident("records_paths", f"each re-run path's {', '.join(UXS.IDENTITY_COLS + UXS.IDENTITY_MORE)} equal "
                               f"results/{d['paths_file']}'s gate run at 0 % (lower_bound) for the first {n_paths} paths "
                               f"of seed {kw['seed']}'s sequence, to {UXS.TOL:g}", base=base)
    horizon = int(a["horizon"])
    years = float(n_paths) * horizon / UV.SESSIONS_PER_YEAR
    cost[f"{base}_records"] = {"paths": int(n_paths), "seconds": round(time.time() - t0, 1),
                               "peak_mb": round(UXS.memory_mb()[0], 1), "policy_id": kw["risk_policy"].id}
    print(f"{base} records: {n_paths} paths in {time.time() - t0:.0f} s", flush=True)
    res = {"days": days, "leaves": leaves, "per_year": {p: places.get(p, 0) / years for p in UV.PLACES},
           "years": years, "policy_id": kw["risk_policy"].id, "places": dict(places)}
    del camp, args, kw, blk
    gc.collect()
    return res


# ------------------------------------------------------------------------------------------------ main


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.reporting.results import sha256_of, verify_result, write_result
    import u_size_fit as SF

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="the pipeline at a short horizon and a few recorded paths; "
                    "written to a temporary folder, since removed")
    ap.add_argument("--identity", action="store_true", help="with --check: D-667's table identities too (full horizon)")
    a = ap.parse_args(argv)
    if a.identity and not a.check:
        print(f"REFUSED ({UV.DECISION}): --identity is a --check option; the read runs whole.")
        return 2
    t_all = time.time()
    rd = RESULTS_DIR
    out = Rows()
    cost: dict[str, Any] = {}
    tables: dict[str, str] = {}
    # ---- D-667's identities
    I = SF.load_inputs(rd)
    sfr = SF.Rows()
    sizes = SF.static_identities(I, sfr)
    if not a.check or a.identity:
        SF.oracles_50k_identity(I, sizes, sfr)
        t0 = time.time()
        SF.identity_solves(I, sizes, sfr)
        cost["d667_identity_solves_seconds"] = round(time.time() - t0, 1)
    for r in sfr.rows:
        if r["section"] == "identity":
            out.add("identity", "holds", 1.0, state=f"d667_{r['subject']}", note=f"D-667's identity: {r['note']}")
    for name, files, commit in (("solver_code", SOLVER_FILES, D667_COMMIT), ("records_code", RECORD_FILES, D650_COMMIT)):
        if not _git_unchanged(commit, files):
            refuse(f"{', '.join(files)} changed since {commit}")
        out.ident(name, f"{', '.join(files)} unchanged since {commit}")
    d667 = None
    if not a.check:
        ok, msg = verify_result(rd / D667_RESULT)
        if not ok:
            refuse(f"{D667_RESULT}: {msg}")
        d667 = pd.read_csv(rd / D667_RESULT, float_precision="round_trip", low_memory=False)
    horizon = CHECK_HORIZON if a.check else None
    n_paths = CHECK_PATHS if a.check else PATHS
    bands = I["noclose"]["export"]
    maps: dict[str, dict] = {}
    for base in UV.BASES:
        maps[base] = value_map(base, I, sizes, out, cost, horizon=horizon, d667=d667, tables=tables)
        gc.collect()
    recs: dict[str, dict] = {}
    for base in UV.BASES:
        recs[base] = records(base, rd, n_paths, bands, out, cost)
        gc.collect()
    # ---- the bands, the leaves, the place values and the bar
    for base in UV.BASES:
        M, Rr = maps[base], recs[base]
        stot = Counter()
        for (ph, _), v in M["bands"].items():
            stot[ph] += v
        rtot = Counter()
        for (ph, _), v in Rr["days"].items():
            rtot[ph] += v
        for key in sorted(set(M["bands"]) | set(Rr["days"])):
            ph, band = key
            out.add("band", "solver_share", M["bands"].get(key, 0.0) / stot[ph] if stot[ph] else None, base=base,
                    phase=ph, state=band, unit="share")
            out.add("band", "records_share", Rr["days"].get(key, 0) / rtot[ph] if rtot[ph] else None, base=base,
                    phase=ph, state=band, n=Rr["days"].get(key, 0), unit="share",
                    note=f"the registered campaign's records (table {Rr['policy_id']})")
        for (ph, leaf), v in sorted(Rr["leaves"].items()):
            out.add("records_leaf", "records_leaf_share", v / rtot[ph] if rtot[ph] else None, base=base, phase=ph,
                    state=leaf, n=v, unit="share")
        for ph in UV.PHASES:
            out.add("phase", "records_account_days_per_year", rtot[ph] / Rr["years"], base=base, phase=ph,
                    unit="sessions", note="the registered campaign's records, five seats")
        t = M["tot"]
        pv = UV.place_values(t["combine"], t["funded"], t["paid"], M["opening"], M["p_pass"], M["days_attempt"],
                             records_per_year=Rr["per_year"])
        for place in UV.PLACES:
            for k, v in pv[place].items():
                if k == "dsum_per_attempt":
                    continue
                unit = "count" if k.startswith("trades") else "dollars"
                out.add("place_values", k, v, base=base, phase=UV.PLACE_PHASE[place], state=place, unit=unit,
                        note=UV.PLACE_NAMES[place] + ("; +1 percentage point of win probability" if "dollars" in k
                                                      else ""))
        for basis in UV.BASES_OF_YEAR:
            for b in UV.bar_rows(pv, basis):
                note = (f"{UV.PLACE_NAMES[b['place']]}; target ${b['target']:,.0f} a year; N = {b['frequency']}"
                        + (f"; capped: the place offers {b['supply']:.2f} trades a year on this basis"
                           if b["capped"] else ""))
                out.add("bar", "extra_win_prob_points", 100.0 * b["extra_win_prob"], base=base, phase=b["where"],
                        state=f"{basis}|{b['where']}|N={b['frequency']}|target={b['target']:g}", n=b["uses"],
                        unit="percentage points", note=note)
    for m, unit, meaning, how in DEFINITIONS:
        out.add("definitions", m, None, unit=unit, note=f"Meaning: {meaning} How it is modelled: {how}")
    for place in UV.PLACES:
        out.add("definitions", place, None, note=f"Place {UV.PLACE_NAMES[place]}.")
    df = pd.DataFrame(out.rows, columns=["section", "base", "phase", "state", "measure", "value", "n", "unit", "note"])
    read_files = [D667_RESULT, SF.NOCLOSE_CSV, SF.NOCLOSE_JSON, SF.D559_CSV, SF.D559_JSON, SF.P14_GATE, SF.P16_GATE,
                  SF.P16_SCREEN, "a3_brk30_cb20_gate_paths.csv", "rc_s150_all_gate_paths.csv"]
    params = {"decision": UV.DECISION, "bases": UV.BASE_NAMES, "size": SIZE, "edge_set": EDGE_SET,
              "config": "config/state_policy_v12.yaml with funded_rules.abandon false (a3_compliance.noclose_config)",
              "horizon_days": int(I["noclose"]["horizon_days"]) if not a.check else CHECK_HORIZON,
              "records": {"paths": n_paths, "arm": ARM, "denial": 0.0, "script": "scripts/u_xfa_day_budget.py (U2)"},
              "places": UV.PLACE_NAMES, "frequencies": list(UV.FREQUENCIES), "targets": list(UV.TARGETS),
              "seats": UV.SEATS, "sessions_per_year": UV.SESSIONS_PER_YEAR, "dp": UV.DP,
              "state_keep_share": STATE_KEEP_SHARE, "d667_commit": D667_COMMIT, "d650_commit": D650_COMMIT,
              "exported_tables_sha256": tables,
              "read_files_sha256": {n: sha256_of(rd / n) for n in read_files if (rd / n).exists()},
              "interpretations": list(INTERPRETATIONS), "cost": cost, "seconds": round(time.time() - t_all, 1)}
    notes = {"status": "EXPLORATORY (D-668): a reading of the solved tables; no campaign run for it, no variant "
                       "counted, selects nothing",
             "value_model": "every value is the table's model's -- a state's continuation under the solver, not a "
                            "campaign's cash path (D-668 (5))"}
    desc = ("EXPLORATORY (D-668, program U's U5): the contract's value map -- P-14's and P-16's state tables re-solved "
            "at $50K at the bound edge (D-667's solves), every held state's value, leaf, the value of a win over a "
            "loss and the edge a dollar is worth; where accounts spend their days (the solver's forward; beside, the "
            "registered campaigns' records); the campaign value of +1 point of win probability by place of an "
            "account's life; the bar a signal of a given frequency must clear. The identities first (section "
            "identity). No seed of its own (an exact chain; the records at the registered seeds).")
    if a.check:
        tmp = Path(tempfile.mkdtemp(prefix="u_value_map_check_"))
        try:
            write_result(df, RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True, results_dir=tmp,
                         parameters=params, notes=notes, description=desc)
            by = df.groupby("section").size().to_dict()
            print(f"--check: {len(df)} rows ({by}) written to a temporary folder (removed); cost {json.dumps(cost)}; "
                  f"{time.time() - t_all:.0f} s")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return 0
    csv, _ = write_result(df, RESULT, script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                          results_dir=results_dir, parameters=params, notes=notes, description=desc)
    print(f"written: {csv} ({len(df)} rows; {time.time() - t_all:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
