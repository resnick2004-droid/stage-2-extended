"""EXPLORATORY (D-620, program U, study U1): the user's journey over twelve months -- a start-day measurement on nine
configurations already on file. No new design; nothing is selected; beside the verdicts, never a gate.

    python scripts/user_journey.py --check --starts 4 --workers 1     # every identity and the whole pipeline on four
                                                                      #   starts a configuration; prints identity lines
                                                                      #   and timing only; nothing written to results/
    python scripts/user_journey.py --trades-hash                      # the London cell's content hash; nothing written
    python scripts/user_journey.py --workers 2                        # the study (from a clean checkout, D-474)

**Units** (D-620 (3)(a)): the replay only -- every trading day of a configuration's development window as a fresh start
(fresh bankroll, fresh accounts), its trades in historical order (D-508's engine call, `customer_slices.engine_args` /
`replay`; D-514's `hypo_hedge.run_joint` with `replay=True` for the cells run through the joint engine), each start run
for min(252, sessions left) sessions, plus runs of exactly 21, 63, 90 and 126 sessions where the start has more left.
Day 0 is the purchase evening, day k closes the k-th session, a month is 21 sessions. **Arms:** `verdict` (every R at
the bound the design's gate read: the 0.05 bound its recorded slices were built at) and `point`.

**The nine configurations** (D-620 (3)(c)), each built by the calls of the study that put it on file:

================  ======  ====================================================  ==================================
config            engine  built as                                              start-day rows on record
================  ======  ====================================================  ==================================
fv3c              single  `customer_journey`'s `fv3c` (FV3-C's development)     customer_slices.csv, customer_journey.csv
p13               single  `customer_journey`'s `p13`                            customer_slices.csv, customer_journey.csv
p14               single  `customer_journey`'s `p14`                            a3_brk30_cb20_gate_slices.csv, customer_journey.csv
p15               single  `rc_dev_test` (`rc_s100_all`)                         rc_s100_all_gate_slices.csv; its journey rows
p16               single  `rc150_dev_test` (`rc_s150_all`, news-safe)           rc_s150_all_gate_slices.csv; its journey rows
p16_funded_cap    single  P-16 with `resolved_coin.funded_cap_rule` (D-544)     none: pinned trades, the beside rows' settings
p16_4+0           joint   `rc150_firm_split`'s four Topstep seats (D-567)       rc150_firm_split.csv's journey rows
p16_5+1           joint   five Topstep + one Lucid seat (D-593), Lucid's        none; its 5 + 0 twin equals P-16's start
                          verified contract, `lucid_upper_bound`                for start
rc_s150_london    single  `rc150_dev_test`'s London window, its own bounds      none: pinned trades, the beside rows' settings
================  ======  ====================================================  ==================================

**Identities before any reading, refused otherwise** (D-620 (3)(f)): P-15's and P-16's trades by their registered
content hashes and screen rows (`rc_dev_test.trade_problems`), the London cell's by its screen row and its pinned hash;
each start's 21-, 63- and 126-session slice equal to the rows on record start for start (`customer_journey.
slice_problems`); D-518's 126-session journey unit of every start (`customer_journey._start_rows`, called on this
study's own runs) equal to `customer_journey.csv`'s start rows (FV3-C, P-13, P-14) and, over every start, its measures
equal to that file's replay rows and to the registered gate files' journey rows (P-15, P-16); the four-seat and 5 + 0
journeys equal to `rc150_firm_split.csv`'s; the 5 + 0 cell through the joint engine equal to P-16's single-engine
records start for start; every payout's arrival day (`user_journey.payout_arrivals`, from the funded accounts'
`payout_days` and `payout_cash`) equal to the campaign's own pay days, its cash summing to the engine's total, and the
fees derived from the cash equal to the engine's total, in every run; the funded-capped and London cells' settings equal
to the registered file's beside rows. A long replay's event days up to h are compared with the run of exactly h
sessions at 21, 63, 90 and 126: where they differ the start's readings at h come from the exact-length run
(`user_journey.Views`) -- counted and reported, not refused.

Writes `results/user_journey.csv` (sections `identity`, `metric`, `month`, `start`, `paired`) and
`results/user_journey_payouts.csv` (one row per payout received), with manifests; EXPLORATORY; 18 readings under
`D-620:user_journey`. A resume file outside the checkout, keyed by the code's commit, keeps every finished
configuration and arm (D-540).
"""
from __future__ import annotations

import argparse
import dataclasses
import gc
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
from propedge.research import user_journey as U  # noqa: E402

SCRIPT = U.SCRIPT
DECISION = U.DECISION
ARMS = U.ARMS
CHUNK_STARTS = 20
LONDON_CELL = "rc_s150_london"
#: the London cell's trades (`rc150_dev_test.build_cells`' `rc_s150_london`, D-533's cut), pinned from this build's
#: `--trades-hash` (a content hash of the trades; no campaign was run for it)
LONDON_TRADES_SHA256 = "6a421c7e1bc9fd69e4880381544e14d1777bf84bdef7f9fd5004f4f024ea8557"
P16_GATE_FILE = "rc_s150_all_gate.csv"
JOURNEY_FILE = "customer_journey.csv"
SPLIT_FILE = "rc150_firm_split.csv"
TWIN = "twin_5+0"

#: the nine configurations (D-620 (3)(c)): how each is built (`group`), its cell, its label, and the rows on record its
#: starts must equal -- `slices` {arm: (file, its config)}, `starts` (D-518's start rows, both arms), `journey` {arm:
#: (file, the rows' filter)}
CONFIG_DEFS: tuple[dict[str, Any], ...] = (
    dict(config="fv3c", group="d518", engine="single", cell="fv3c_dev", label="", decision="D-505",
         slices={"verdict": ("customer_slices.csv", "fv3c")}, starts=(JOURNEY_FILE, "fv3c"),
         journey={a: (JOURNEY_FILE, {"section": "metric", "config": "fv3c", "source": "replay"}) for a in ARMS}),
    dict(config="p13", group="d518", engine="single", cell="a3_brk30", label="", decision="D-500",
         slices={a: ("customer_slices.csv", "p13") for a in ARMS}, starts=(JOURNEY_FILE, "p13"),
         journey={a: (JOURNEY_FILE, {"section": "metric", "config": "p13", "source": "replay"}) for a in ARMS}),
    dict(config="p14", group="d518", engine="single", cell="a3_brk30_cb20", label="", decision="D-513",
         slices={"verdict": ("a3_brk30_cb20_gate_slices.csv", "a3_brk30_cb20")}, starts=(JOURNEY_FILE, "p14"),
         journey={a: (JOURNEY_FILE, {"section": "metric", "config": "p14", "source": "replay"}) for a in ARMS}),
    dict(config="p15", group="p15", engine="single", cell="rc_s100_all", label="", decision="D-527",
         slices={"verdict": ("rc_s100_all_gate_slices.csv", "rc_s100_all")}, starts=None,
         journey={"verdict": ("rc_s100_all_gate.csv", {"section": "journey", "config": "rc_s100_all"})}),
    dict(config="p16", group="p16", engine="single", cell="rc_s150_all_nr", label="", decision="D-544",
         slices={"verdict": ("rc_s150_all_gate_slices.csv", "rc_s150_all")}, starts=None,
         journey={"verdict": (P16_GATE_FILE, {"section": "journey", "config": "rc_s150_all"})}),
    dict(config="p16_funded_cap", group="p16", engine="single", cell="rc_s150_all_nr", label="", decision="D-544",
         slices={}, starts=None, journey={}),
    dict(config="p16_4+0", group="joint", engine="joint", cell="rc_s150_all_nr", label="", decision="D-567",
         seats=(4,), slices={}, starts=None,
         journey={"verdict": (SPLIT_FILE, {"section": "journey", "cell": "4+0"})}),
    dict(config="p16_5+1", group="joint", engine="joint", cell="rc_s150_all_nr", label=U.LUCID_LABEL,
         decision="D-593", seats=(5, 1), slices={}, starts=None, journey={}),
    dict(config=LONDON_CELL, group="p16", engine="single", cell=LONDON_CELL, label="", decision="D-538",
         slices={}, starts=None, journey={}),
)
#: the 5 + 0 cell through the joint engine: an identity's side (it must equal P-16's records start for start and
#: `rc150_firm_split.csv`'s 5 + 0 journey), never a configuration or a reading
TWIN_DEF = dict(config=TWIN, group="joint", engine="joint", cell="rc_s150_all_nr", label="", decision="D-567",
                seats=(5,), slices={}, starts=None, journey={"verdict": (SPLIT_FILE, {"section": "journey", "cell": "5+0"})})
GROUPS = ("d518", "p15", "p16", "joint")


def start_choice(n: int, starts: int | None) -> list[int]:
    """The starts run: every one, or (a --check seam) `starts` of them spread evenly from the first to the last."""
    if starts is None or int(starts) >= int(n):
        return list(range(int(n)))
    return sorted({int(round(x)) for x in np.linspace(0, int(n) - 1, int(starts))})


def _join(xs) -> str:
    return " ".join(str(int(x)) for x in xs)


# ------------------------------------------------------------------------------------------------ the replay tasks


def _one_start(config: str, arm: str, s: int, date: str, long_run, exact_runs: dict, sub: float, ev_fn, pay_fn,
               tot_fn, slice_fn) -> dict[str, Any]:
    """One start from its runs (the long replay and the exact-length ones): its record (D-620 (3)(d)); the checks of
    every run's payouts and fees against the engine's own totals; the exact runs whose event days differ from the long
    replay's, with their records; and D-518's side -- the 126-session journey unit and the 21 / 63 / 126 slices, by
    `customer_journey._start_rows` on these runs."""
    import customer_journey as CJ

    bad = {"pay": 0, "cash": 0, "fee": 0}

    def record(run, ev) -> dict[str, Any]:
        cash, init, passes, funded, pays = ev
        obs = len(cash) - 1
        arr = pay_fn(run, obs)
        fees, paid = tot_fn(run)
        got = float(sum(c for _, c in arr))
        if sorted(d for d, _ in arr) != sorted(int(d) for d in pays):
            bad["pay"] += 1
        if abs(got - float(paid)) > U.TOL:
            bad["cash"] += 1
        if abs(U.fees_paid(float(cash[-1]) - float(init), got) - float(fees)) > U.TOL:
            bad["fee"] += 1
        return U.start_record(cash, init, passes, funded, arr)

    ev_long = ev_fn(long_run)
    L = len(ev_long[0]) - 1
    rec = {"start_day": int(s), "start_date": str(date), **record(long_run, ev_long)}
    exact_ev = {h: ev_fn(r) for h, r in exact_runs.items()}
    differs = []
    for h in sorted(exact_ev):
        e = exact_ev[h]
        if len(e[0]) - 1 != h:
            raise RuntimeError(f"{config} {arm} start {s}: the {h}-session run holds {len(e[0]) - 1} sessions")
        r = record(exact_runs[h], e)
        if U.events_upto(e[2], e[3], e[4], h) != U.events_upto(ev_long[2], ev_long[3], ev_long[4], h):
            differs.append(int(h))
            rec.setdefault("alt", {})[str(int(h))] = r
    w = cj.WINDOW
    run126, ev126 = (exact_runs[w], exact_ev[w]) if L > w else (long_run, ev_long)
    l126 = len(ev126[0]) - 1
    row, slices, bad126 = CJ._start_rows(config, arm, int(s), str(date), ev126,
                                         {h: exact_ev[h] for h in cj.EXACT if h < l126}, sub,
                                         lambda h, h_: slice_fn(run126 if h is None else exact_runs[h], h_, sub))
    return {"rec": rec, "row126": row, "slices": slices, "bad126": int(bad126), "checked": sorted(int(h) for h in exact_ev),
            "differs": differs, "runs": 1 + len(exact_ev), "pay_bad": bad["pay"], "cash_bad": bad["cash"],
            "fee_bad": bad["fee"]}


def _single_task(task: tuple) -> list[dict[str, Any]]:
    """(config, arm, blocks, dates, args, starts) -> every start's output (`_one_start`), one firm: D-508's engine
    call (`customer_slices.replay`), D-518's events (`customer_journey.single_events`)."""
    import warnings

    import customer_journey as CJ
    import customer_slices as cs

    warnings.filterwarnings("ignore")
    config, arm, blocks, dates, args, starts = task
    sub = float(args["path"]["subscription"])
    lag = int(args["path"]["payout_lag_days"])
    n = len(blocks)

    def pay(lp, obs):
        return U.payout_arrivals([(f.activation_day, lag, f.payout_days, f.payout_cash) for f in lp.funded], obs)

    out = []
    for s in starts:
        L = min(U.HORIZON, n - s)
        long_run = cs.replay(blocks[s:s + L], args)
        if len(long_run.path.cash_series) != L + 1:
            raise RuntimeError(f"{config} {arm} start {s}: {len(long_run.path.cash_series)} closes, not {L + 1}")
        exact = {h: cs.replay(blocks[s:s + h], args) for h in U.EXACT if h < L}
        out.append(_one_start(config, arm, s, dates[s], long_run, exact, sub, CJ.single_events, pay,
                              lambda lp: (lp.path.total_fees, lp.path.total_payouts), cs.slice_measures))
        # D-630: an entry option's own record of the long replay (`LockstepPath.wallet_stop`, `.pause_after_funded`,
        # `.seat_ramp`), carried beside the start's output only when the replay ran with one -- no key otherwise
        entry = {k: dict(getattr(long_run, k)) for k in ("wallet_stop", "pause_after_funded", "seat_ramp")
                 if getattr(long_run, k, None)}
        if entry:
            out[-1]["entry"] = entry
    return out


def _joint_task(task: tuple) -> list[dict[str, Any]]:
    """(config, arm, blocks, dates, setups, seed, starts) -> the same through the joint engine (`rc150_firm_split.
    _journey_task`'s call: `hypo_hedge.run_joint` unhedged with `replay=True`, each firm on its own setup; the pooled
    wallet's cash, every firm's events; each firm's payouts at its own lag)."""
    import warnings

    import customer_journey as CJ

    from propedge.research import hypo_hedge as hh

    warnings.filterwarnings("ignore")
    config, arm, blocks, dates, setups, seed, starts = task
    sub = max(float(x.path["subscription"]) for x in setups)
    lags = [int(x.path["payout_lag_days"]) for x in setups]
    n = len(blocks)
    want = []
    for s in starts:
        L = min(U.HORIZON, n - s)
        want.append((s, L))
        want += [(s, h) for h in U.EXACT if h < L]
    specs = [hh.PathSpec(seed=int(seed), blocks=blocks[s:s + h], horizon_days=int(h) + 1, replay=True) for s, h in want]
    jps = hh.run_joint(specs, setups[0], n_firms=len(setups), mode=hh.UNHEDGED, doubled=True, firm_setups=setups)
    got = dict(zip(want, jps))

    def pay(jp, obs):
        return U.payout_arrivals([(f.activation_day, lags[i], f.payout_days, f.payout_cash)
                                  for i, lp in enumerate(jp.paths) for f in lp.funded], obs)

    def totals(jp):
        return (sum(float(lp.path.total_fees) for lp in jp.paths), sum(float(lp.path.total_payouts) for lp in jp.paths))

    out = []
    for s in starts:
        L = min(U.HORIZON, n - s)
        exact = {h: got[(s, h)] for h in U.EXACT if h < L}
        out.append(_one_start(config, arm, s, dates[s], got[(s, L)], exact, sub, CJ.joint_events, pay, totals,
                              hh.slice_measures))
    return out


def _dispatch(task: tuple) -> list[dict[str, Any]]:
    kind, t = task
    return _single_task(t) if kind == "single" else _joint_task(t)


def run_job(job: dict[str, Any], config: str, arm: str, starts: int | None, workers: int) -> dict[str, Any]:
    """One configuration and arm: every start (or the chosen ones) in chunks across a guarded pool
    (`customer_journey._pool_run`), in start order, with its wall time."""
    import customer_journey as CJ

    t0 = time.time()
    chosen = start_choice(len(job["blocks"]), starts)
    chunks = [chosen[j:j + CHUNK_STARTS] for j in range(0, len(chosen), CHUNK_STARTS)]
    if job["engine"] == "single":
        tasks = [("single", (config, arm, job["blocks"], job["dates"], job["args"], c)) for c in chunks]
    else:
        tasks = [("joint", (config, arm, job["blocks"], job["dates"], job["setups"], job["seed"], c)) for c in chunks]
    res = CJ._pool_run(tasks, _dispatch, workers, f"{config} {arm}")
    return {"starts": [x for chunk in res for x in chunk], "seconds": time.time() - t0}


# ------------------------------------------------------------------------------------------------ the inputs


def _single_jobs(camp, plan, budget) -> dict[str, dict[str, Any]]:
    """A `customer_slices.Campaign` as the two arms' jobs, exactly as `rc_dev_test.journey_and_slices` hands its
    verdict arm to the replay (the table and budget passed to `engine_args`)."""
    import customer_slices as cs

    out = {}
    for arm in ARMS:
        out[arm] = {"engine": "single", "blocks": cs.arm_blocks(camp, arm), "dates": camp.dates,
                    "args": cs.engine_args(camp.kw, arm, camp.blocks, risk_policy=plan, purchase_budget=budget),
                    "sub": float(camp.kw["rules"].subscription)}
    return out


def _rc_campaign(I: dict, b: dict, cell: str, spec):
    """An RC cell's campaign as `rc_dev_test.run` builds it: the cell's trades, the screen's 0.05 bounds
    (`atlas_a3.bounds` -- what `a3_brk30.bounds_at_n` reads and checks, and the window cells' own call), its busiest
    day's capacity, `rc_dev_test.rc_campaign`."""
    import a3_brk30 as B
    import atlas_a3 as A
    import rc_dev_test as D

    L = I["L"]
    t = b["cells"][cell]["trades"]
    if t is None:
        raise SystemExit(f"REFUSED ({DECISION}): the cell {cell} holds no trade.")
    days = b["days"]
    _, e_by, lb_by, _, _ = A.bounds(t, days, B.rrs(t), L["cfg"])
    return D.rc_campaign(I, t, days, e_by, lb_by, B.capacity(t, L["fcfg"]), spec)


def _ident(config: str, arm: str, check: str, problems: list[str], *, compared: int | None = None,
           differing: int | None = None, refuses: bool = True) -> dict[str, Any]:
    return {"section": "identity", "config": config, "arm": arm, "check": check, "holds": not problems,
            "compared": compared, "differing": differing if differing is not None else (len(problems) or 0),
            "refuses": bool(refuses), "problems": "; ".join(problems[:4])}


def build_d518(rd: Path, want: list[str]) -> tuple[dict, list[dict]]:
    """FV3-C, P-13 and P-14 by D-518's own job builder (`customer_journey.Inputs` / `replay_jobs`: its config table,
    its tables and budgets, its seeds)."""
    import customer_journey as CJ

    cfgs = [c for c in CJ.CONFIGS if c["config"] in want]
    I = CJ.Inputs(rd, cfgs)
    jobs = {}
    for c in cfgs:
        per = {}
        for kind, t in CJ.replay_jobs(I, c, 1):
            if kind != "single":
                raise SystemExit(f"REFUSED ({DECISION}): {c['config']} is not a single-firm replay.")
            _, arm, blk, dates, args, _ = t
            per[arm] = {"engine": "single", "blocks": blk, "dates": dates, "args": args, "sub": I.subscription(c)}
        jobs[c["config"]] = per
    return jobs, []


def build_p15(rd: Path, want: list[str]) -> tuple[dict, list[dict]]:
    """P-15 (`rc_s100_all`) as `rc_dev_test` builds it; its trades by its screen row and its own content hash."""
    import a3_brk30_cb20 as C
    import rc_dev_test as D

    I, b = D.build_cells()
    bad = D.trade_problems(rd, b, I["L"]["fcfg"], spec=D.P15)
    idents = [_ident("p15", "", f"the trades are results/{D.P15.screen_file}'s {D.P15.cell} (count, busiest day, "
                                 "capacity, long share, candidates a day, every R's unresolved share) and their content "
                                 f"hash is P-15's registered {D.P15.trades_sha256}", bad)]
    return {"p15": _single_jobs(_rc_campaign(I, b, D.P15.cell, D.P15), I["plan"], C.BUDGET)}, idents


def settings_problems(rd: Path, section: str, window_cell: str | None, jobs: dict[str, dict]) -> list[str]:
    """What a cell's replay runs (its two arms' engine arguments, `customer_slices.engine_args`) against the registered
    file's beside rows (`rc_s150_all_gate.csv`, the section's rows at 0 %, the point arm against the point row and the
    verdict arm against the bound row): seats, table, strict rule, budget, placement, routing, mode, settlement and
    payout timing."""
    import customer_journey as CJ

    ref = _text(rd, P16_GATE_FILE)
    g = ref[ref["section"] == section]
    if window_cell is not None:
        g = g[g["window_cell"] == window_cell]
    g = g[g["enforcement_p"].astype(float) == 0.0]
    if sorted(g["shift"]) != ["lower_bound", "point"]:
        return [f"{P16_GATE_FILE} holds {len(g)} {section} rows at 0 %" + (f" for {window_cell}" if window_cell else "")]
    out = []
    for arm in ARMS:
        r = g[g["shift"] == CJ.SHIFT_OF[arm]].iloc[0]
        d, p = jobs[arm]["args"]["draws"], jobs[arm]["args"]["path"]
        budget = p.get("purchase_budget") or (None, None)
        want = {"accounts": p["max_concurrent_accounts"], "combines": p["max_concurrent_combines"],
                "total_accounts": p["max_total_accounts"], "risk_policy": getattr(p["risk_policy"], "id", None),
                "one_at_a_time": d.get("one_at_a_time"), "rtp": bool(p["conduct"].rtp),
                "routing": "able" if d["route_able"] else r["routing"] if r["routing"] != "able" else "not able",
                "cross_account_rule": bool(d["cross_account"]), "mode": d["mode"], "settlement": d["settlement"],
                "payout_timing": p["payout_timing"], "budget_k": budget[0], "budget_window_days": budget[1]}
        out += [f"{section} {arm} {k}: {v!r} against the file's {r[k]!r}" for k, v in want.items()
                if not CJ._same(v, r[k])]
    return out


def build_p16(rd: Path, want: list[str]) -> tuple[dict, list[dict]]:
    """P-16 (`rc_s150_all`, news-safe) as `rc150_dev_test` builds it, and its two beside cells built as that file's
    beside rows were: the funded-capped reading (`resolved_coin.funded_cap_rule` on the gate's sizing, D-544) and the
    London window (its own trades, bounds and capacity)."""
    import a3_brk30_cb20 as C
    import customer_slices as cs
    import rc150_dev_test as R
    import rc_dev_test as D

    from propedge.research import resolved_coin as rc

    I, b = R.build_cells()
    fcfg, plan = I["L"]["fcfg"], I["plan"]
    bad = D.trade_problems(rd, b, fcfg, spec=R.SPEC)
    p16_check = (f"the trades are results/{R.SPEC.screen_file}'s {R.SPEC.cell} (count, busiest day, capacity, long "
                 "share, candidates a day, every R's unresolved share) and their content hash is P-16's registered "
                 f"{R.SPEC.trades_sha256}")
    idents = [_ident(c, "", p16_check, bad) for c in ("p16", "p16_funded_cap") if c in want or c == "p16"]
    camp = _rc_campaign(I, b, R.SPEC.cell, R.SPEC)
    jobs = {"p16": _single_jobs(camp, plan, C.BUDGET)}
    if "p16_funded_cap" in want:
        sizing = rc.funded_cap_rule(camp.kw["sizing"], rc.REFERENCE_STOP, R.STOP)
        capped = cs.Campaign(camp.name, camp.blocks, camp.dates, {**camp.kw, "sizing": sizing})
        jobs["p16_funded_cap"] = _single_jobs(capped, plan, C.BUDGET)
        bad = settings_problems(rd, "funded_cap_beside", None, jobs["p16_funded_cap"])
        used = [jobs["p16_funded_cap"][arm]["args"]["draws"]["sizing"] for arm in ARMS]
        if any(type(x).__name__ != "FundedCapRule" or abs(float(x.funded_scale) - rc.REFERENCE_STOP / R.STOP) > 1e-12
               for x in used):
            bad.append("the sizing is not resolved_coin.funded_cap_rule's at the 25-point cell's stop over the cell's")
        if any(type(jobs["p16"][arm]["args"]["draws"]["sizing"]).__name__ == "FundedCapRule" for arm in ARMS):
            bad.append("P-16's own replay is sized by the funded cap")
        idents.append(_ident("p16_funded_cap", "", f"the settings are results/{P16_GATE_FILE}'s funded_cap_beside rows' "
                             "(five seats, the no-closure table, the strict rule, 20 purchases in 21 days, the "
                             "placement off, routing, mode, settlement, payout timing), P-16's trades and bounds, and "
                             f"the funded cap scaled by {rc.REFERENCE_STOP}/{R.STOP} (resolved_coin.funded_cap_rule)", bad))
    if LONDON_CELL in want:
        spec = dataclasses.replace(R.SPEC, cell=LONDON_CELL, trades_sha256=LONDON_TRADES_SHA256)
        bad = D.trade_problems(rd, b, fcfg, spec=spec)
        idents.append(_ident(LONDON_CELL, "", f"the trades are results/{R.SPEC.screen_file}'s {LONDON_CELL} (count, "
                             "busiest day, capacity, long share, candidates a day, every R's unresolved share) and "
                             f"their content hash is the pinned {LONDON_TRADES_SHA256}", bad))
        lcamp = _rc_campaign(I, b, LONDON_CELL, spec)
        jobs[LONDON_CELL] = _single_jobs(lcamp, plan, C.BUDGET)
        bad = settings_problems(rd, "window_beside", LONDON_CELL, jobs[LONDON_CELL])
        if any(type(jobs[LONDON_CELL][arm]["args"]["draws"]["sizing"]).__name__ == "FundedCapRule" for arm in ARMS):
            bad.append("the London cell is sized by the funded cap")
        idents.append(_ident(LONDON_CELL, "", f"the settings are results/{P16_GATE_FILE}'s window_beside rows' for "
                             f"{LONDON_CELL} (five seats, the no-closure table, the strict rule, 20 purchases in 21 "
                             "days, the placement off, routing, mode, settlement, payout timing), the cell's own "
                             "trades, its own 0.05 bounds (atlas_a3.bounds) and its own day capacity", bad))
    return {k: v for k, v in jobs.items() if k in want or k == "p16"}, idents


def build_joint(rd: Path, want: list[str]) -> tuple[dict, list[dict]]:
    """The cells run through the joint engine, by `rc150_firm_split`'s own inputs with Lucid as firm 1
    (`inputs("lucid")`: P-16's cell by its content hash, the opposite side aligned, P-16's engine arguments, Lucid's
    verified contract), its arms' blocks (`arm_blocks`) and its firms' replay setups (`firm_setups`): four Topstep
    seats, five Topstep seats plus one Lucid seat, and the 5 + 0 twin."""
    import customer_journey as CJ
    import rc150_firm_split as F
    import rc_screen as S

    X = F.inputs(F.LUCID)                   # refuses unless the cell's content hash is P-16's
    blocks = {arm: F.arm_blocks(X, CJ.SHIFT_OF[arm]) for arm in ARMS}
    jobs, idents = {}, []
    for c in (*CONFIG_DEFS, TWIN_DEF):
        if c["group"] != "joint" or c["config"] not in want:
            continue
        setups = F.firm_setups(X, "rep", c["seats"])
        jobs[c["config"]] = {arm: {"engine": "joint", "blocks": blocks[arm], "dates": list(X["days"]), "setups": setups,
                                   "seed": int(S.SEED), "sub": max(float(x.path["subscription"]) for x in setups)}
                             for arm in ARMS}
        if c["config"] != TWIN:
            idents.append(_ident(c["config"], "", "the trades are P-16's by their registered content hash "
                                 "(rc150_firm_split.inputs), the opposite side aligned one for one; seats "
                                 + "+".join(str(s) for s in c["seats"]) + ", each firm's budget floor(20 x seats / 5) in "
                                 "21 trading days" + ("; firm 1 Lucid's verified contract, its two unpriced fees at "
                                                      "zero (lucid_upper_bound)" if len(c["seats"]) > 1 else ""), []))
    return jobs, idents


BUILDERS = {"d518": build_d518, "p15": build_p15, "p16": build_p16, "joint": build_joint}


# ------------------------------------------------------------------------------------------------ the identities

_TEXT: dict[str, pd.DataFrame] = {}


def _text(rd: Path, name: str) -> pd.DataFrame:
    """A result file on record as text (its manifest checked first), read once."""
    from propedge.reporting.results import verify_result

    if name not in _TEXT:
        ok, msg = verify_result(Path(rd) / name)
        if not ok:
            raise SystemExit(f"REFUSED ({DECISION}): {name}: {msg}")
        _TEXT[name] = pd.read_csv(Path(rd) / name, dtype=str, keep_default_na=False, low_memory=False)
    return _TEXT[name]


def _where(df: pd.DataFrame, where: dict[str, str], arm: str) -> pd.DataFrame:
    m = df["arm"] == arm
    for k, v in where.items():
        m &= df[k] == v
    return df[m]


#: D-518's start row: the columns compared start for start (its unit, its event days, its month-end nets)
START_COLS = (*cj.UNIT_COLS, "start_date", "pass_days", "funded_days", "pay_days",
              *[f"net_month_{k}" for k in range(1, cj.WINDOW // cj.MONTH + 1)])


def start_row_problems(rows: list[dict], ref: pd.DataFrame, what: str) -> list[str]:
    """Our 126-session journey rows against D-518's start rows on record, start for start on `START_COLS`."""
    import customer_journey as CJ

    by = {int(float(d)): i for i, d in enumerate(ref["start_day"])}
    out = []
    missing = [r["start_day"] for r in rows if int(r["start_day"]) not in by]
    if missing:
        return [f"{what}: {len(missing)} starts not on record (first: {missing[0]})"]
    for c in START_COLS:
        bad = [r["start_day"] for r in rows if not CJ._same(r.get(c), ref[c].iloc[by[int(r["start_day"])]])]
        if bad:
            out.append(f"{what} {c}: {len(bad)} starts differ (first: start {bad[0]})")
    return out


def journey_problems(rows: list[dict], sub: float, ref: pd.DataFrame, what: str) -> list[str]:
    """D-518's measures over our 126-session journey rows (`customer_journey.metrics`) against the rows on record:
    every measure's value and count."""
    import customer_journey as CJ

    mine = cj.metrics(pd.DataFrame(rows), float(sub))
    theirs = {str(k): (v, n) for k, v, n in zip(ref["key"], ref["value"], ref["n"])}
    out = []
    if len(mine) != len(theirs):
        out.append(f"{what}: {len(mine)} measures against {len(theirs)} on record")
    for m in mine:
        key = cj.metric_key(m["milestone"], m["measure"], m["at_days"])
        if key not in theirs:
            out.append(f"{what} {key}: not on record")
        elif not (CJ._same(m["value"], theirs[key][0]) and CJ._same(m["n"], theirs[key][1])):
            out.append(f"{what} {key}: differs from the record")
    return out


def twin_problems(twin: list[dict], ref: list[dict], what: str) -> list[str]:
    """The 5 + 0 cell through the joint engine against P-16's single-engine records, start for start."""
    by = {int(x["rec"]["start_day"]): x["rec"] for x in ref}
    if sorted(by) != sorted(int(x["rec"]["start_day"]) for x in twin):
        return [f"{what}: the starts differ ({len(twin)} against {len(by)})"]
    keys: dict[str, int] = {}
    for x in twin:
        a, b = x["rec"], by[int(x["rec"]["start_day"])]
        bad = U.record_problems(a, b) + ([] if a["start_date"] == b["start_date"] else ["start_date"]) \
            + ([] if sorted(a.get("alt") or {}) == sorted(b.get("alt") or {}) else ["alt"])
        for k in bad:
            keys[k] = keys.get(k, 0) + 1
    return [f"{what} {k}: {n} starts differ" for k, n in keys.items()]


def config_identities(c: dict, arm: str, outs: list[dict], sub: float, rd: Path, all_starts: bool
                      ) -> tuple[list[dict], list[str]]:
    """One configuration and arm's identities from its starts' outputs: (the identity rows, the notes of what could
    not be compared on a part of the starts)."""
    import customer_journey as CJ

    name = c["config"]
    rows, notes = [], []
    runs = int(sum(x["runs"] for x in outs))
    nbad = int(sum(x["pay_bad"] + x["cash_bad"] + x["fee_bad"] for x in outs))
    detail = [f"{k}: {int(sum(x[k + '_bad'] for x in outs))} runs" for k in ("pay", "cash", "fee")
              if sum(x[k + "_bad"] for x in outs)]
    rows.append(_ident(name, arm, "every payout's arrival day (the account's activation day + 1 + its payout day + the "
                       "firm's lag, from the funded accounts' payout_days) equals the campaign's own pay days; the "
                       "payouts' cash (payout_cash) sums to the engine's total payouts; the fees derived from the cash "
                       "(payouts received less the net) equal the engine's total fees -- in every run, long and exact",
                       detail, compared=runs, differing=nbad))
    checked = int(sum(len(x["checked"]) for x in outs))
    differs = int(sum(len(x["differs"]) for x in outs))
    rows.append(_ident(name, arm, "the long replay's pass, activation and pay days up to h equal those of the run of "
                       "exactly h sessions at " + ", ".join(str(h) for h in U.EXACT) + " (where they differ the start's "
                       "readings at h are read from the exact-length run)",
                       [f"{differs} exact runs differ"] if differs else [], compared=checked, differing=differs,
                       refuses=False))
    bad126 = int(sum(x["bad126"] for x in outs))
    for a, (file, cfg) in c["slices"].items():
        if a != arm:
            continue
        sl = pd.DataFrame([s for x in outs for s in x["slices"]])
        bad = CJ.slice_problems(sl, rd / file, cfg, arm) if len(sl) else ["no slice ran"]
        rows.append(_ident(name, arm, f"each start's 21-, 63- and 126-session slice (runs of exactly that length) equals "
                           f"results/{file}'s '{cfg}' rows start for start", bad, compared=len(sl)))
    if c["starts"] is not None:
        file, cfg = c["starts"]
        ref = _where(_text(rd, file), {"section": "start", "config": cfg}, arm)
        bad = start_row_problems([x["row126"] for x in outs], ref, f"{name} {arm}")
        if bad126:
            bad.append(f"{bad126} exact runs' event days differ from the 126-session run's")
        rows.append(_ident(name, arm, f"D-518's 126-session journey of each start (its unit, event days and month-end "
                           f"nets) equals results/{file}'s '{cfg}' start rows start for start", bad, compared=len(outs)))
    if arm in c["journey"]:
        file, where = c["journey"][arm]
        what = f"the 126-session journey measures (customer_journey.metrics) equal results/{file}'s rows ({where})"
        if all_starts:
            bad = journey_problems([x["row126"] for x in outs], sub, _where(_text(rd, file), where, arm),
                                   f"{name} {arm}")
            if bad126:
                bad.append(f"{bad126} exact runs' event days differ from the 126-session run's")
            rows.append(_ident(name, arm, what, bad, compared=len(outs)))
        else:
            notes.append(f"{name} {arm}: {what} -- needs every start; not compared on {len(outs)} starts")
    return rows, notes


# ------------------------------------------------------------------------------------------------ the tables


def start_rows(c: dict, arm: str, outs: list[dict]) -> list[dict[str, Any]]:
    """Section `start`: one row a start -- what D-620 (3)(d) lists (the payouts' cash in the payouts file), the net at
    session 30 (Q1's sensitivity), the start's monthly mean over sd, and the exact runs that differed."""
    rows = []
    for x in outs:
        r = x["rec"]
        rows.append({"section": "start", "config": c["config"], "arm": arm, "label": c["label"], "cell": c["cell"],
                     "start_day": int(r["start_day"]), "start_date": r["start_date"], "observed": int(r["observed"]),
                     "pass_days": _join(r["pass_days"]), "funded_days": _join(r["funded_days"]),
                     "pay_days": _join(r["pay_days"]), "payouts": len(r["pay_days"]),
                     **{k: r[k] for k in ("first_pass", "first_funded", "first_payout", "first_payout_cash",
                                          "spent_before_first_pass", "spent_before_first_payout")},
                     **{f"net_month_{k}": r["net_month"][k - 1] for k in range(1, U.MONTHS + 1)},
                     **{f"fees_month_{k}": r["fees_month"][k - 1] for k in range(1, U.MONTHS + 1)},
                     "net_30": r["net_30"], "monthly_mean_over_sd": U.monthly_mean_over_sd(
                         [float("nan") if v is None else v for v in r["net_month"]]),
                     "exact_runs_differing": _join(x["differs"])})
    return rows


def payout_rows(c: dict, arm: str, outs: list[dict]) -> list[dict[str, Any]]:
    """One row per payout received (the long replay's), D-620 (3)(g)'s five columns: configuration, arm, start (the
    start's day index; its date and the configuration's label are in section `start`), arrival day, cash."""
    return [{"config": c["config"], "arm": arm, "start_day": int(x["rec"]["start_day"]), "day": int(d), "cash": float(v)}
            for x in outs for d, v in zip(x["rec"]["pay_days"], x["rec"]["pay_cash"])]


PAYOUT_COLS = ("config", "arm", "start_day", "day", "cash")


def readings(defs: list[dict], outs: dict[tuple[str, str], list[dict]]) -> tuple[list[dict], list[dict], list[dict]]:
    """The readings of D-620 (3)(e) from the starts' records: (section `metric` rows, section `month` rows, section
    `paired` rows)."""
    head = {c["config"]: {"config": c["config"], "label": c["label"], "cell": c["cell"]} for c in defs}
    views = {k: U.Views([x["rec"] for x in v]) for k, v in outs.items() if k[0] in head}
    metric, month, paired = [], [], []
    for arm in ARMS:
        per = {}
        for c in defs:
            V = views[(c["config"], arm)]
            per[c["config"]] = U.metric_rows(V)
            for r in per[c["config"]]:
                (month if r["section"] == "month" else metric).append({**head[c["config"]], "arm": arm, **r})
        for r in U.luck_rows(per):
            cfg = r.pop("config")
            month.append({**head.get(cfg, {"config": cfg, "label": "", "cell": ""}), "arm": arm, **r})
        if (U.REFERENCE, arm) in views:
            for c in defs:
                if c["config"] == U.REFERENCE:
                    continue
                for r in U.paired_rows(views[(c["config"], arm)], views[(U.REFERENCE, arm)]):
                    paired.append({**head[c["config"]], "arm": arm, "reference": U.REFERENCE, **r})
    return metric, month, paired


# ------------------------------------------------------------------------------------------------ the study


def trades_hash() -> int:
    """`--trades-hash`: the London cell's content hash (and P-16's beside its pin); a reading of no campaign."""
    import rc150_dev_test as R
    import rc_dev_test as D

    _, b = R.build_cells()
    for cell, pin in ((R.SPEC.cell, R.SPEC.trades_sha256), (LONDON_CELL, LONDON_TRADES_SHA256)):
        t = b["cells"][cell]["trades"]
        print(f"{cell}: content hash {D.trades_hash(t)} (pinned: {pin})")
    print("nothing written (--trades-hash).")
    return 0


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import subprocess
    import tempfile

    import rc150_firm_split as F

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import sha256_of, write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="every identity and the pipeline; identity lines and timing "
                    "only; nothing written to results/")
    ap.add_argument("--starts", type=int, default=None, help="with --check: this many starts a configuration, spread "
                    "evenly over its window")
    ap.add_argument("--configs", default=None, help="with --check: a comma-separated subset of the configurations")
    ap.add_argument("--workers", type=int, default=1, help="replay workers (the memory guard may grant fewer)")
    ap.add_argument("--no-resume", action="store_true", help="D-540: neither keep nor read finished runs")
    ap.add_argument("--resume-dir", default=None, help="D-540: where finished runs are kept (outside the checkout)")
    ap.add_argument("--trades-hash", action="store_true", help="print the London cell's content hash; nothing written")
    a = ap.parse_args(argv)
    if a.trades_hash:
        return trades_hash()
    if not a.check and (a.starts is not None or a.configs is not None):
        print(f"REFUSED ({DECISION}): the study runs every start of all nine configurations; a smaller run is --check.")
        return 2
    rd = RESULTS_DIR
    t_all = time.time()

    # ---- the declaration
    decl = U.declaration()
    bad = U.declaration_problems(decl)
    if tuple(cj.EXACT) != tuple(U.EXACT) or cj.MONTH != U.MONTH or tuple(c["config"] for c in CONFIG_DEFS) != U.CONFIGS:
        bad.append("the exact-length runs, the month or the configurations are not the module's")
    if bad:
        print(f"REFUSED ({DECISION}): the build is not D-620's declaration -- " + "; ".join(bad[:8]))
        return 3
    print(f"the declaration HOLDS: {DECISION}'s row (sha256 {decl['sha256'][:16]}) and every phrase the build's "
          "constants rest on", flush=True)
    idents: list[dict] = [_ident("", "", f"DECISIONS.md's {DECISION} row (sha256 {decl['sha256']}) and every phrase "
                                 "this build's constants rest on", [])]
    names = U.CONFIGS if a.configs is None else tuple(x for x in a.configs.split(",") if x)
    unknown = [x for x in names if x not in U.CONFIGS]
    if unknown:
        print(f"REFUSED ({DECISION}): not a configuration: {unknown}")
        return 2
    defs = [c for c in CONFIG_DEFS if c["config"] in names]

    resume = None
    if not a.check and not a.no_resume:
        commit = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip() or "nocommit"
        folder = Path(a.resume_dir) if a.resume_dir else (
            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stage2-runs" / "resume")
        resume = F.Resume(folder, f"{commit}_all", U.RESULT)

    outs: dict[tuple[str, str], list[dict]] = {}
    timing: dict[str, dict[str, Any]] = {}
    failures: list[str] = []
    notes: list[str] = []

    def settle(rows: list[dict]) -> bool:
        """Print each identity's line and keep its row; False when one that refuses fails."""
        ok = True
        for r in rows:
            idents.append(r)
            who = " ".join(x for x in (r["config"], r["arm"]) if x) or DECISION
            count = "" if r["compared"] is None else f" [{r['compared']} compared, {r['differing']} differing]"
            if r["holds"]:
                print(f"identity HOLDS: {who}: {r['check']}{count}", flush=True)
            elif not r["refuses"]:
                print(f"identity DIFFERS (read from the exact-length run, not a refusal): {who}: {r['check']}{count}",
                      flush=True)
            else:
                print(f"identity FAILS: {who}: {r['check']}{count} -- {r['problems']}", flush=True)
                failures.append(f"{who}: {r['problems']}")
                ok = False
        return ok

    for group in GROUPS:
        want = [c["config"] for c in defs if c["group"] == group]
        todo = [c for c in defs if c["group"] == group]
        if group == "joint" and U.REFERENCE in names and any(c["group"] == "joint" for c in defs):
            want, todo = [TWIN, *want], [TWIN_DEF, *todo]
        if not want:
            continue
        print(f"the inputs of {want}...", flush=True)
        t0 = time.time()
        jobs, rows = BUILDERS[group](rd, want)
        print(f"timing: the inputs of {want}: {time.time() - t0:.0f} s", flush=True)
        if not settle(rows) and not a.check:
            print(f"REFUSED ({DECISION}): " + "; ".join(failures[:6]))
            return 3
        for c in todo:
            name = c["config"]
            if name not in jobs:
                continue
            sub = float(jobs[name][ARMS[0]]["sub"])
            for arm in ARMS:
                job = jobs[name][arm]

                def make(job=job, c=c, name=name, arm=arm, sub=sub) -> dict[str, Any]:
                    """The arm's starts and its identities (kept together: a resumed run reads both back, D-540). The
                    kept starts hold the record and the exact runs that differed; the twin's are compared here and
                    not kept."""
                    v = run_job(job, name, arm, a.starts, a.workers)
                    rows, more = config_identities(c, arm, v["starts"], sub, rd, a.starts is None)
                    if name == TWIN:
                        bad = twin_problems(v["starts"], outs[(U.REFERENCE, arm)], f"5+0 {arm}")
                        rows.append(_ident("p16_5+1", arm, "the 5 + 0 cell through the joint engine (the 5 + 1 cell's "
                                           "twin) equals P-16's single-engine records start for start (the sessions "
                                           "observed and every event day exactly; every payout's cash, month-end net "
                                           "and fees to 1e-6)", bad, compared=len(v["starts"])))
                    keep = [] if name == TWIN else [{"rec": x["rec"], "differs": x["differs"]} for x in v["starts"]]
                    return {"starts": keep, "n": len(v["starts"]), "idents": rows, "notes": more,
                            "seconds": v["seconds"]}

                v = F._cached(resume, f"{name}|{arm}", make)
                outs[(name, arm)] = v["starts"]
                n, secs = int(v["n"]), float(v["seconds"])
                timing[f"{name}|{arm}"] = {"engine": c["engine"], "starts": n, "seconds": round(secs, 1)}
                print(f"timing: {name} {arm} ({c['engine']} engine): {n} starts in {secs:.1f} s "
                      f"({secs / max(n, 1):.2f} s a start)", flush=True)
                notes += list(v["notes"])
                if not settle(list(v["idents"])) and not a.check:
                    print(f"REFUSED ({DECISION}): " + "; ".join(failures[:6]))
                    return 3
        del jobs
        gc.collect()
    for line in notes:
        print(f"identity NOT COMPARED: {line}", flush=True)
    if failures:
        print(f"REFUSED ({DECISION}): {len(failures)} identities fail; nothing read, nothing written -- "
              + "; ".join(failures[:8]))
        return 3

    # ---- the readings (only now)
    t0 = time.time()
    metric, month, paired = readings(defs, outs)
    starts, payouts = [], []
    for c in defs:
        for arm in ARMS:
            starts += start_rows(c, arm, outs[(c["config"], arm)])
            payouts += payout_rows(c, arm, outs[(c["config"], arm)])
    for r in idents:
        r.pop("problems", None)
    res = pd.DataFrame(idents + metric + month + starts + paired)
    res.insert(1, "reading", U.READING)
    pay = pd.DataFrame(payouts, columns=list(PAYOUT_COLS))
    print(f"timing: the readings: {time.time() - t0:.0f} s", flush=True)
    seconds = time.time() - t_all
    replaced = {f"{k[0]}|{k[1]}": int(sum(len(x["differs"]) for x in v)) for k, v in outs.items() if k[0] != TWIN}
    params = {"decision": DECISION, "study": U.STUDY, "declaration_sha256": decl["sha256"],
              "configs": [{k: (list(v) if isinstance(v, tuple) else v) for k, v in c.items()
                           if k not in ("slices", "starts", "journey")} for c in defs],
              "arms": {"verdict": "every R at the 0.05 bound the design's gate read (the lower_bound arm its recorded "
                                  "slices and journeys were built at); the cells on P-16's trades at P-16's; the London "
                                  "cell at its own (the registered file's beside rows')", "point": "as traded"},
              "horizon": U.HORIZON, "month": U.MONTH, "exact_runs": list(U.EXACT),
              "reference": U.REFERENCE, "limit_reference": U.LIMIT_REFERENCE,
              "bootstrap": {"seed": U.BOOT_SEED, "draws": U.BOOT_DRAWS, "alpha": U.ALPHA, "interval": "two-sided "
                            "percentile", "block": "the reading's horizon in sessions (start days in date order)"},
              "seeds": {"campaign": U.CAMPAIGN_SEED, "coin": U.COIN_SEED,
                        "note": "a replay draws nothing; each configuration's replay is passed the seed its own study "
                                "passed"},
              "conventions": {
                  "net": "cash at a close less the start (the bankroll never binds); month-end and session-30 nets are "
                         "the long replay's closes",
                  "fees": "payouts received by the close less the net at it, to 1e-6",
                  "blank": "a reading with no eligible start, a percentile beyond the observed days, a concentration "
                           "whose total is not positive, an interval with fewer common starts than one block",
                  "first_payout_cash": "the first payout to arrive (same day: the engine's account order)",
                  "concentration": "the ceil(n / 4) largest nets over the total",
                  "sd": "sample standard deviations (ddof 1)",
                  "exact_runs": "a start whose long replay's event days up to h differ from the exact h-session run's "
                                "is read from the exact run at h"},
              "starts": {k: v["starts"] for k, v in timing.items() if not k.startswith(TWIN)},
              "starts_read_from_an_exact_run": replaced,
              "references": {f: sha256_of(rd / f) for f in sorted({x[0] for c in (*defs, TWIN_DEF) for x in
                                                                   [*c["slices"].values(), *c["journey"].values(),
                                                                    *([c["starts"]] if c["starts"] else [])]}
                                                                  | {P16_GATE_FILE})},
              "london_trades_sha256": LONDON_TRADES_SHA256, "timing": timing, "workers": int(a.workers),
              "seconds": round(seconds, 1)}
    notes_ = {"status": U.READING, "variant_count_rule": f"one reading per configuration and arm, under {U.FAMILY_ID}",
              "labels": f"{U.LUCID_LABEL}: the 5 + 1 cell runs Lucid's verified contract with its two unpriced fees at "
                        "zero -- every figure of it is an upper bound on them",
              "selection": "none (D-620 (3)(h)); U1's reading gets its own decision row, built from this file"}

    def write(target: Path | None) -> None:
        counter = VariantCounter(path=(Path(target) if target is not None else rd) / "variants.jsonl")
        for c in defs:
            for arm in ARMS:
                counter.record(prereg_id=U.FAMILY_ID, seed=U.CAMPAIGN_SEED, exploratory=True,
                               params={"study": "the user's journey (D-620, U1)", "config": c["config"], "arm": arm,
                                       "cell": c["cell"], "label": c["label"], "horizon": U.HORIZON},
                               label=f"D-620's user journey: {c['config']} ({arm})"
                                     + (f" -- {c['label']}" if c["label"] else ""))
        write_result(res, U.RESULT, script=SCRIPT, seed=U.BOOT_SEED, exploratory=True, results_dir=target,
                     variant_count=len(defs) * len(ARMS), parameters=params, notes=notes_,
                     description="EXPLORATORY (D-620, U1): every trading day of each configuration's development window "
                                 "as a fresh start, replayed for up to 252 sessions in historical order -- the first "
                                 "pass and payout, the net at each month end, payouts per dollar of fees, the payout "
                                 "rhythm, the quit rules, luck against design (sections metric and month), every "
                                 "start's record (section start) and each configuration's paired difference from P-16 "
                                 "with a moving-block bootstrap interval (section paired); the identities first "
                                 "(section identity). No new design; no selection.")
        write_result(pay, U.PAYOUTS_RESULT, script=SCRIPT, seed=U.BOOT_SEED, exploratory=True, results_dir=target,
                     variant_count=len(defs) * len(ARMS),
                     parameters={"result": f"{U.RESULT}.csv", "decision": DECISION,
                                 "start_day": "the start's day index in its configuration's window (its date and "
                                              f"the configuration's label are in {U.RESULT}.csv's section start)",
                                 "day": "the campaign day the payout's cash arrives (day 0 the purchase evening)",
                                 "cash": "net to the trader, the engine's payout_cash"},
                     notes={"status": U.READING, "companion_of": f"{U.RESULT}.csv"},
                     description="EXPLORATORY (D-620, U1): one row per payout received by a replay start within its "
                                 "observed sessions -- configuration, arm, start, arrival day, cash.")

    if a.check:
        with tempfile.TemporaryDirectory(prefix="user_journey_check_") as td:
            write(Path(td))
            wrote = sorted(p.name for p in Path(td).iterdir())
        print(f"every identity holds; the pipeline ran on {'every' if a.starts is None else a.starts} start(s) of "
              f"{[c['config'] for c in defs]} at both arms and wrote {wrote} to a temporary folder, since removed; "
              f"nothing written to results/, no reading printed (--check). {seconds:.0f} s")
        return 0
    write(results_dir)
    print(f"written: {U.RESULT}.csv ({len(res)} rows) and {U.PAYOUTS_RESULT}.csv ({len(pay)} rows); {seconds:.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
