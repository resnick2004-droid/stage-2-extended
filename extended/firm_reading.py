"""RD-01's reading (`prereg/RD-01_firm_contracts.md` 6, 7, 9.2, 9.3, 10, 15): one run's cells, the oracles and the
mechanics computed while each start's ledger and accounts are alive, the scorecard per plan paired with TS by month,
the beside readings (the denial ladder, the gate with its zero-edge twin) and A-10's price grid -- as rows for
`scripts/rd01_reading.py`'s three files. The adapters are `extended.firms`' and `extended.firm_accounts`', used as
built (Q-104); nothing here changes a rule, and no rule value is typed here: every bound is read from the plan's terms.

**A cell** is one run of 7.3 (or a ladder response) at one arm: every chosen start through A-9 (`user_beside.run_starts`,
one start at a time with that start's own classes, as `firms.run_plan` composes them) -- **one pass** (the third read's
(g)): A-9's own replays are kept in this process (`firms.captured_run`: the long run with the engine's per-trade ledger
through A-9's Q-94 recorder seam, the exact-length runs as `user_beside.replay` returns them) with the adapters'
counters and request logs (`captured_start`); no second replay (`direct_start` stays only as the single pass's control
in the toys). **Refusing, at the first problem** (r5): the start's output composed again from the captured runs equals
A-9's bit for bit (`user_beside_identity.first_difference`); 9.1 items 4 and 5 on every replay; **9.2's oracles** on
every start -- every
trade's fee its plan's schedule at the contracts it holds (`fee_problems`), every request inside its plan's bounds and
every net its plan's split of it, to 1e-9 (`request_problems`: DayTraders' $50 increments, minimum, cap, request gate
and balance left; Fast Pass's cap and minimum; Quick Pay's tiered split, recomputed here; at TS and Lucid the records'
requests within the minimum and the cap and summing to the gross paid), Quick Pay's floor at every close
(`floor_oracle_breaches`, A-7's counter), and A-10's premise that the fees by kind are the engine's total. Each start's
**9.3 counts and 10.1 item 6 fields** (`start_stats`) are taken from its ledger, its records and its accounts' counters
before they are dropped (memory), written one row a start, and summed by plan, stream and block (`count_rows`).

**The verdict arm at TradeDay (r6):** A-11's booking on the point blocks, then the campaign's own registered shift
(`customer_slices.arm_blocks`' `lb - e` and `lb_by_rr - e_by_rr`, captured as U1's builder makes the arm,
`build_with_deltas`), and refused unless every day A-11 leaves untouched is U1's verdict block bit for bit
(`untouched_problems`).

**Pairing** (10.1 item 4, 10.2): the plan's start records against TS's on the same stream and arm, start for start;
each month's net read as U1 reads it (r1: `user_journey.Views`, a start whose exact-length run differed read from that
run), at its horizon (months 1-3: 63 sessions; 6: 126; 9 and 12: 252 -- n1: 6 item 4 names none for month 9, the
longer horizon taken) on the blocks `all`, `early` and `late` (`u_select.block`), with 10.2's paired reading and its
coverage label (`firm_uncertainty.coverage` by keyword, R1, every declared shape at the reading's h and n_w, cached).

**The gate beside (10.1 item 8, 9.2):** one call per corner at the plan's arguments, and the zero-edge twin as Stage 2
builds it (r8: `portfolio_stage.zero_edge_blocks` at the design's fresh R, every bound 0), read on its bound arm; on the
twin the mean gross payouts per funded account against the funded account's distance to its floor and the pass rate
per evaluation against the evaluation's floor over target plus floor, each beyond its 99.9 % Monte Carlo interval
refusing (`twin_problems`).
"""
from __future__ import annotations

import dataclasses
import math
from datetime import date as _date
from typing import Any, Callable, Sequence

import numpy as np

from extended import use_vendored_stage2

use_vendored_stage2()

from extended import firm_accounts as A  # noqa: E402
from extended import firm_counts as C  # noqa: E402
from extended import firm_terms as T  # noqa: E402
from extended import firm_uncertainty as FU  # noqa: E402
from extended import firms as F  # noqa: E402
from extended import user_beside as B  # noqa: E402
from extended import user_measures as M  # noqa: E402
from extended import walker as W  # noqa: E402

DECLARATION = "prereg/RD-01_firm_contracts.md"
PURPOSES = ("firm_scorecard", "firm_ladder_beside", "firm_gate_beside")
BLOCKS = ("all", "early", "late")
STATUS = "described, not carried"
#: 6 item 4: the horizon of a month's reading (n1: month 9 at 252, the conservative choice; 6 item 4 names none)
HORIZON_OF_MONTH = {1: 63, 2: 63, 3: 63, 6: 126, 9: 252, 12: 252}
PAIRED_MONTHS = (1, 2, 3, 6, 9, 12)
LADDER = ("denial_10", "denial_25", "denial_50")
#: 10.2 item 7: series per coverage setting
COVERAGE_SERIES = 20_000
#: 9.3's counts by block: every start's long replay for `all`; `early` and `late` by `u_select.block` at the long
#: replay's horizon, so no early count reads a 2024 session
COUNT_HORIZON = 252
#: 9.2's twin interval: two-sided 99.9 % (normal), an oracle refusing only beyond it
TWIN_Z = 3.2905
#: the ledger fields 9.2's and 9.3's per-start numbers read (the rest of each row dropped)
LEDGER_KEEP = ("kind", "index", "day", "rel_day", "slot", "historical_day", "trade_index", "contracts", "pnl", "fee",
               "u", "rr", "rr_used", "fee_adj_r", "at_need", "stretch", "balance_before", "balance_after", "floor",
               "room", "room_capped", "cap_micros", "at_cap", "intended_risk", "intended_capped_risk",
               "realised_risk", "risk_per_contract")


class Refused(RuntimeError):
    """A refusing check failed: the reading stops here (9.1, 9.2, 11; r5)."""


# ------------------------------------------------------------------------------------------------ a run's inputs


def stream_of(run: T.Run) -> str:
    return {"P-16": "p16", "P-14": "p14"}[run.stream]


def build_with_deltas(build: Callable[[], Any]) -> tuple[Any, list[tuple[float, dict[float, float] | None]]]:
    """`build()` (U1's own builder) with every non-point arm's registered shift recorded as `customer_slices.arm_blocks`
    makes it: (`lb - e`, {R: `lb_by_rr[R] - e_by_rr[R]`}) from the campaign's own arguments (r6). The vendored function
    is wrapped in this process for the call and restored; nothing vendored is edited."""
    import customer_slices as cs

    seen: list[tuple[float, dict[float, float] | None]] = []
    orig = cs.arm_blocks

    def spy(c: Any, arm: str) -> list:
        if arm != "point":
            kw = c.kw
            by = None if kw.get("e_by_rr") is None else {float(k): float(kw["lb_by_rr"][k]) - float(kw["e_by_rr"][k])
                                                         for k in kw["e_by_rr"]}
            seen.append((float(kw["lb"]) - float(kw["e"]), by))
        return orig(c, arm)

    cs.arm_blocks = spy
    try:
        out = build()
    finally:
        cs.arm_blocks = orig
    return out, seen


def _same_block(a: Any, b: Any) -> bool:
    if not np.array_equal(np.asarray(a.pnl, float), np.asarray(b.pnl, float), equal_nan=True):
        return False
    if (a.r_by_rr is None) != (b.r_by_rr is None):
        return False
    if a.r_by_rr is not None:
        if set(map(float, a.r_by_rr)) != set(map(float, b.r_by_rr)):
            return False
        for k in a.r_by_rr:
            if not np.array_equal(np.asarray(a.r_by_rr[k], float), np.asarray(b.r_by_rr[float(k)], float),
                                  equal_nan=True):
                return False
    return True


def delta_problems(point: Sequence[Any], arm: Sequence[Any], delta: tuple[float, dict | None]) -> list[str]:
    """r6: the registered shift, applied to the point blocks as `gate.shifted_blocks` applies it, is the arm's blocks
    bit for bit (the delta captured is the campaign's own)."""
    from propedge.campaign.gate import shifted_blocks

    got = shifted_blocks(list(point), float(delta[0]), delta[1])
    bad = [i for i, (a, b) in enumerate(zip(got, arm)) if not _same_block(a, b)]
    if len(got) != len(arm):
        return [f"the shifted point list holds {len(got)} days, the arm {len(arm)}"]
    return [f"{len(bad)} days of the arm are not the point blocks under the registered shift (first: {bad[0]})"] \
        if bad else []


def untouched_problems(shifted: Sequence[Any], arm: Sequence[Any], booked: Sequence[Any], point: Sequence[Any]
                       ) -> list[str]:
    """r6: on every day A-11 left as it was (`booked[i] is point[i]`), the TradeDay verdict arm is U1's bit for bit."""
    bad = [i for i, (s, a, k, p) in enumerate(zip(shifted, arm, booked, point)) if k is p and not _same_block(s, a)]
    return [f"{len(bad)} untouched days of the TradeDay verdict arm are not U1's (first: {bad[0]})"] if bad else []


def arm_inputs(point: dict[str, Any], arm_job: dict[str, Any], s: T.Settings, arm: str,
               delta: tuple[float, dict | None] | None = None) -> tuple[list[Any], list[Any] | None, dict[str, int]]:
    """One arm's blocks for a plan: at TradeDay, A-11's booking on the point blocks then the arm's registered shift
    (`delta`, r6; refused unless the untouched days are the arm's own); every other plan the arm's blocks as built.
    Also the point-arm blocks Quick Pay's bracket reads on every arm (M3: A-11's booking applied, no shift), and A-11's
    counts."""
    counts: dict[str, int] = {}
    blocks = list(arm_job["blocks"])
    ref = list(point["blocks"])
    if s.plan in ("FP", "QP"):
        ref, counts = F.tier1_arm(point["blocks"], point["dates"], s.tier1)
        if arm == "point":
            blocks = ref
        else:
            if delta is None:
                raise ValueError("REFUSED (r6): a TradeDay verdict arm takes the campaign's registered shift")
            blocks = F.tier1_arm(point["blocks"], point["dates"], s.tier1, float(delta[0]), delta[1])[0]
            bad = untouched_problems(blocks, arm_job["blocks"], ref, point["blocks"])
            if bad:
                raise Refused("r6: " + "; ".join(bad))
    return blocks, (ref if s.plan == "QP" else None), counts


def cell_job(arm_job: dict[str, Any], s: T.Settings, blocks: Sequence[Any], *, ladder: bool = False
             ) -> tuple[dict[str, Any], dict[str, Any]]:
    """The cell's job (A-1's arguments; the classes are made per start) and A-9's keywords."""
    args, kw = F.plan_args(arm_job["args"], s, blocks=blocks if s.plan not in ("TS", "LU") else None, ladder=ladder)
    if s.plan not in ("TS", "LU"):
        args = {**args, "path": {k: v for k, v in args["path"].items() if k != "combine_account_cls"}}
        kw = {k: v for k, v in kw.items() if k != "funded_account_cls"}
    return {**arm_job, "blocks": list(blocks), "args": args}, kw


def stream_context(name: str, point: dict[str, Any]) -> dict[str, Any]:
    """What every cell of a stream reads for 9.3: the dates, A-11's classification of the offered trades (5.5), the
    smallest risk a micro among them (G-10's smallest tradable size)."""
    tiers = C.tier1_trades(point["blocks"], point["dates"])
    rpc = [float(np.min(np.asarray(b.risk_per_contract, float))) for b in point["blocks"]
           if len(b.pnl) and b.risk_per_contract is not None]
    return {"name": name, "dates": list(point["dates"]), "open": set(tiers["open"]), "inside": sorted(tiers["inside"]),
            "min_rpc": float(min(rpc)) if rpc else float("nan")}


# ------------------------------------------------------------------------------------------------ one start


def _pay_totals(lag: int) -> tuple[Callable, Callable]:
    from propedge.research import user_journey as U

    def pay(lp, obs):
        return U.payout_arrivals([(f.activation_day, lag, f.payout_days, f.payout_cash) for f in lp.funded], obs)

    def totals(lp):
        return lp.path.total_fees, lp.path.total_payouts

    return pay, totals


def compose(design: str, arm: str, resp: Any, s: int, date: str, long_run: Any, exact: dict[int, Any] | None,
            sub: float, lag: int, seed: int, named: dict[str, Any]) -> dict[str, Any]:
    """A start's output from its runs, exactly as `user_beside._task` composes it (`exact` None: the long replay's
    record alone, as `_task` makes it on a start without exact-length runs)."""
    import customer_journey as CJ
    import customer_slices as cs
    import user_journey as UJ

    from propedge.research import user_journey as U

    pay, totals = _pay_totals(lag)
    mine = B.long_record(s, date, long_run, pay, totals)
    if exact is not None:
        o = UJ._one_start(design, arm, s, date, long_run, exact, sub, CJ.single_events, pay, totals, cs.slice_measures)
        r0 = {k: v for k, v in o["rec"].items() if k != "alt"}
        same = not U.record_problems(r0, mine["rec"]) and r0["start_date"] == mine["rec"]["start_date"] and \
            all(o[f"{k}_bad"] == mine[f"{k}_bad"] for k in ("pay", "cash", "fee"))
        o = {**o, "record_same": bool(same)}
    else:
        o = {**mine, "differs": [], "checked": [], "record_same": None}
    rel = np.asarray(long_run.path.cash_series, float) - float(long_run.path.initial_bankroll)
    return {"rec": o["rec"], "differs": o["differs"], "checked": o["checked"], "pay_bad": o["pay_bad"],
            "cash_bad": o["cash_bad"], "fee_bad": o["fee_bad"], "record_same": o["record_same"],
            "daily": M.daily(rel), "response": B.response_record(long_run, resp, None), "seed": int(seed), **named}


def _slim(lp: Any) -> Any:
    return dataclasses.replace(lp, trades=(), account_days=(), campaign_days=())


def _start_args(job: dict[str, Any], s: T.Settings, start: int, kw: dict[str, Any], point: list[Any] | None,
                resp: Any) -> tuple[dict[str, Any], int, int, Any, Any]:
    """(the replay arguments A-9's task makes for this start, its path seed, its long run's sessions, the funded class,
    the household reading) -- `user_beside._task`'s own composition, with the start's classes."""
    from propedge.research import user_journey as U

    if resp.kind == "forfeit":
        raise ValueError("RD-01 reads no forfeiture")
    c_cls, f_cls = F.start_classes(s, job["dates"], int(start), point)
    f_cls = f_cls if f_cls is not None else kw.get("funded_account_cls")
    args = job["args"] if c_cls is None else {**job["args"], "path": {**job["args"]["path"], "combine_account_cls": c_cls}}
    hc = kw.get("household_closure")
    a = B.response_args(args, resp, f_cls, household_closure=hc) if (f_cls is not None or hc is not None) \
        else B.response_args(args, resp)
    base = B.DENIAL_SEED if kw.get("seed_base") is None else int(kw["seed_base"])
    return a, B.start_seed(int(start), base), min(U.HORIZON, len(job["blocks"]) - int(start)), f_cls, hc


def _start_record(job: dict[str, Any], start: int, kw: dict[str, Any], a: dict[str, Any], seed: int, L: int,
                  f_cls: Any, hc: Any, long_full: Any, exact: dict[int, Any] | None, counts: list[dict[str, Any]],
                  exact_counts: dict[int, list[dict[str, Any]]]) -> dict[str, Any]:
    named = {**B.seam_parameters(hc, kw.get("seed_base")), **B.class_parameters(f_cls)}
    rules = a["path"]["rules"]
    return {"start": int(start), "date": str(job["dates"][start]), "long": _slim(long_full), "exact": exact,
            "ledger": [{k: r.get(k) for k in LEDGER_KEEP} for r in long_full.trades if r.get("contracts")],
            "seed": seed, "named": named, "counts": counts, "exact_counts": exact_counts,
            "sub": float(a["path"]["subscription"]), "lag": int(a["path"]["payout_lag_days"]),
            "billing_days": int(a["path"]["billing_days"]), "activation": float(a["path"]["activation"]),
            "payout_fee": float(rules.payout_fee), "split": float(rules.profit_split),
            "payout_min": float(rules.payout_min), "std_cap": float(rules.std_cap), "sessions": int(L),
            "sizing": a["draws"].get("sizing")}


def captured_start(job: dict[str, Any], s: T.Settings, start: int, kw: dict[str, Any], point: list[Any] | None,
                   resp: Any, every: int, counts_by_run: list[list[dict[str, Any]]],
                   got: dict[tuple[int, int], Any]) -> dict[str, Any]:
    """One start from A-9's own single pass (`firms.captured_run`): its long run (recorded, its ledger), its
    exact-length runs where A-9 makes them, every run's adapter counters and request logs -- no second replay. Refused
    unless the captured runs are exactly the start's (its seed, the long run and each exact length A-9 makes)."""
    from propedge.research import user_journey as U

    a, seed, L, f_cls, hc = _start_args(job, s, start, kw, point, resp)
    with_exact = int(start) % int(every) == 0              # A-9 composes through `_one_start` here, even with none
    hs = [h for h in U.EXACT if h < L] if with_exact else []
    want = {(int(seed), int(L))} | {(int(seed), int(h)) for h in hs}
    if set(got) != want:
        raise Refused(f"start {start}: the single pass captured {sorted(got)}, not the start's runs {sorted(want)}")
    adapters = s.plan not in ("TS", "LU")                 # TS and Lucid run no adapter account (9.1 item 5)
    if len(counts_by_run) != ((1 + len(hs)) if adapters else 0):
        raise Refused(f"start {start}: {len(counts_by_run)} replays' adapter accounts counted, not "
                      f"{(1 + len(hs)) if adapters else 0}")
    counts_by_run = counts_by_run or [[] for _ in range(1 + len(hs))]
    long_full = got[(int(seed), int(L))]
    if not long_full.trades and any(c.trades for c in long_full.combines):
        raise Refused(f"start {start}: the recorded long run carries no ledger")
    exact = {h: got[(int(seed), int(h))] for h in hs} if with_exact else None
    return _start_record(job, start, kw, a, seed, L, f_cls, hc, long_full, exact, counts_by_run[0],
                         {h: counts_by_run[1 + i] for i, h in enumerate(hs)})


def direct_start(design: str, arm: str, resp: Any, job: dict[str, Any], s: T.Settings, start: int,
                 kw: dict[str, Any], point: list[Any] | None, every: int) -> dict[str, Any]:
    """One start replayed again, apart from A-9 (the second build's route, kept as the single pass's control): the long
    run with the engine's ledger on, and the exact-length runs where A-9 makes them, with the start's classes."""
    from propedge.research import user_journey as U

    a, seed, L, f_cls, hc = _start_args(job, s, start, kw, point, resp)
    A.TALLY.clear()
    rec_args = {**a, "path": {**a["path"], "record_trades": True}}
    long_full = B.replay(job["blocks"][start:start + L], rec_args, seed)
    counts = F.split_runs(A.collect(with_requests=True))[:1]
    exact, exact_counts = None, {}
    if int(start) % int(every) == 0:
        exact = {}
        for h in U.EXACT:
            if h < L:
                exact[h] = B.replay(job["blocks"][start:start + h], a, seed)
                exact_counts[h] = A.collect(with_requests=True)
    A.TALLY.clear()
    return _start_record(job, start, kw, a, seed, L, f_cls, hc, long_full, exact, counts[0] if counts else [],
                         exact_counts)


def priced_output(design: str, arm: str, resp: Any, d: dict[str, Any], run_price: float, price: float,
                  pro_fee: float = 0.0, pro_billing_days: int | None = None) -> dict[str, Any]:
    """A start's output with every run repriced to `price` (and DayTraders' Pro fee charged): A-10."""
    def rp(lp):
        if price == run_price and not pro_fee:
            return lp
        return F.repriced(lp, run_price, price, d["billing_days"], pro_fee=pro_fee, pro_billing_days=pro_billing_days)

    exact = None if d["exact"] is None else {h: rp(lp) for h, lp in d["exact"].items()}
    sub = d["sub"] if price == run_price else float(price)
    return compose(design, arm, resp, d["start"], d["date"], rp(d["long"]), exact, sub, d["lag"], d["seed"],
                   d["named"])


def keep_direct(d: dict[str, Any]) -> dict[str, Any]:
    """What a cell keeps of a direct start once its numbers are taken: the runs A-10 reprices (memory)."""
    return {k: d[k] for k in ("start", "date", "long", "exact", "seed", "named", "sub", "lag", "billing_days")}


# ------------------------------------------------------------------------------------------------ 9.2's oracles


def micros_per_mini(plan: str) -> int:
    if plan in ("TS", "LU"):
        from propedge.campaign.sizing import MICROS_PER_MINI

        return int(MICROS_PER_MINI)
    return int(T.plan_terms(plan).micros_per_mini)


def schedule_fee(plan: str, fee_basis: str | None, contracts: int) -> float:
    """4.8: the plan's round-turn fee at `contracts` micro-equivalents -- as many minis as fit, the rest in micros."""
    sched = T.fee_schedule(plan, fee_basis) if plan == "DT" else T.fee_schedule(plan)
    pm = micros_per_mini(plan)
    n = int(contracts)
    return float((n // pm) * float(sched[1]) + (n - (n // pm) * pm) * float(sched[0]))


def fee_problems(ledger: Sequence[dict[str, Any]], s: T.Settings) -> list[str]:
    """9.2 (4.8): every executed trade's fee is its plan's schedule at the contracts it holds, to 1e-9 -- at every plan,
    TS and Lucid included; a trade priced at no schedule is refused."""
    out = []
    for r in ledger:
        n = int(r.get("contracts") or 0)
        if n <= 0:
            continue
        if r.get("fee") is None:
            out.append(f"a trade of {n} micros at day {r.get('historical_day')} carries no fee: priced at no schedule")
        elif abs(float(r["fee"]) - schedule_fee(s.plan, s.fee_basis, n)) > 1e-9:
            out.append(f"a trade of {n} micros pays {r['fee']}, the plan's schedule {schedule_fee(s.plan, s.fee_basis, n)}")
        if len(out) >= 3:
            break
    return out


def tiered_net(plan: str, request: float, before: float) -> float:
    """Quick Pay's tiered split, recomputed independently of A-7 (`tradeday.quickpay_eod50k.payout_split`): the part
    of the request above the split line of the profit at the low rate's complement, the rest at the low rate."""
    t = T.plan_terms(plan)
    above = min(float(request), max(0.0, float(before) - float(t.split_line)))
    return float(t.split_high) * above + float(t.split_low) * (float(request) - above) - float(t.payout_fee)


def _close(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))


def request_problems(d: dict[str, Any], s: T.Settings) -> tuple[list[str], int, dict[str, int]]:
    """9.2 on one start's runs (the long replay and each exact-length run): every request inside its plan's bounds and
    every net its plan's split of it, to 1e-9; and U-7's zero checks on the requests (counted, never refused): Fast
    Pass's above half the profit, Quick Pay's above the reference's amount (the ceiling's closing withdrawal excepted)
    and below its minimum. Returns (problems, requests checked, zero-check counts)."""
    probs: list[str] = []
    zero = {"zero_fp_request_above_half_profit": 0, "zero_qp_request_above_reference": 0,
            "zero_qp_request_below_min": 0}
    n = 0
    runs = [("long", d["long"], d["counts"])] + [(f"exact {h}", lp, d["exact_counts"].get(h, []))
                                                  for h, lp in (d["exact"] or {}).items()]
    t = None if s.plan in ("TS", "LU") else T.plan_terms(s.plan)
    half = float(T.stage2_value("payout_max_frac_of_balance"))       # 2.3: the declared request's half of the balance
    for tag, lp, counts in runs:
        logs = {int(g["index"]): g.get("requests", []) for g in counts if g.get("kind") == "funded"}
        for f in lp.funded:
            where = f"{tag} funded {f.index}"
            nets = [float(x) for x in f.payout_cash]
            if s.plan in ("TS", "LU"):
                split, fee, lo, cap = d["split"], d["payout_fee"], d["payout_min"], d["std_cap"]
                reqs = [(x + fee) / split for x in nets]
                n += len(reqs)
                if not _close(sum(reqs), float(f.gross_paid)):
                    probs.append(f"{where}: the requests {sum(reqs)} are not the gross paid {f.gross_paid}")
                for r in reqs:
                    if r < lo - 1e-9 or r > cap + 1e-9:
                        probs.append(f"{where}: a request of {r} outside [{lo}, {cap}]")
                continue
            log = logs.get(int(f.index))
            if log is None:
                probs.append(f"{where}: no request log from its adapter")
                continue
            if [round(q["net"], 9) for q in log] != [round(x, 9) for x in nets]:
                probs.append(f"{where}: the request log's nets are not the record's payouts")
            if not _close(sum(q["request"] for q in log), float(f.gross_paid)):
                probs.append(f"{where}: the logged requests are not the gross paid")
            for q in log:
                n += 1
                r, before, after, net = float(q["request"]), float(q["before"]), float(q["after"]), float(q["net"])
                if s.plan == "DT":
                    inc = float(t.request_increment)
                    if abs(r / inc - round(r / inc)) > 1e-9:
                        probs.append(f"{where}: a request of {r} is not in ${inc:g} increments")
                    if r < float(t.payout_min) - 1e-9 or r > float(t.payout_cap) + 1e-9:
                        probs.append(f"{where}: a request of {r} outside [{t.payout_min}, {t.payout_cap}]")
                    if after < float(t.request_leave) - 1e-9 or before < float(t.request_gate) - 1e-9:
                        probs.append(f"{where}: a request from {before} leaving {after}: outside the gate or the "
                                     "balance left")
                    if not _close(net, float(t.split) * r - float(t.payout_fee)):
                        probs.append(f"{where}: a net of {net} is not the split of {r}")
                elif s.plan == "FP":
                    if r < float(t.payout_min) - 1e-9 or r > float(t.payout_cap) + 1e-9:
                        probs.append(f"{where}: a request of {r} outside [{t.payout_min}, {t.payout_cap}]")
                    if not _close(net, float(t.split) * r - float(t.payout_fee)):
                        probs.append(f"{where}: a net of {net} is not the split of {r}")
                    zero["zero_fp_request_above_half_profit"] += int(r > half * before + 1e-9)
                elif s.plan == "QP":
                    if not _close(net, tiered_net("QP", r, before)):
                        probs.append(f"{where}: a net of {net} is not the tiered split of {r} from {before}")
                    if q.get("kind") != "ceiling_withdrawal":
                        ref = min(half * before, float(T.stage2_value("xfa_std_cap")))
                        zero["zero_qp_request_above_reference"] += int(r > ref + 1e-9)
                    zero["zero_qp_request_below_min"] += int(r < float(t.payout_min) - 1e-9)
            if len(probs) >= 3:
                return probs, n, zero
    return probs, n, zero


def fees_by_kind(d: dict[str, Any], s: T.Settings) -> tuple[dict[str, float], list[str]]:
    """10.1 item 6's fees by kind on the long replay, by A-10's arithmetic on its records, and the check that the
    evaluation, activation and reset fees are the engine's total (A-10's premise, refusing)."""
    lp, p = d["long"], d["long"].path
    subs = len(F.subscription_days(lp, d["billing_days"]))
    resets = sum(int(c.resets) for c in lp.combines)
    payouts = sum(int(f.n_payouts) for f in lp.funded)
    out = {"fees_evaluations": subs * float(d["sub"]), "fees_activation": len(lp.funded) * float(d["activation"]),
           "fees_payout": payouts * float(d["payout_fee"]), "fees_pro": 0.0}
    if s.plan == "DT":
        t = T.plan_terms("DT")
        due = F.pro_fee_days(lp, int(T.stage2_value("billing_days")), len(p.cash_series) - 1)
        out["fees_pro"] = len(due) * float(t.funded_recurring_fee)
    probs = []
    if resets == 0 and abs(out["fees_evaluations"] + out["fees_activation"] - float(p.total_fees)) > 1e-6:
        probs.append(f"the fees by kind ({out['fees_evaluations']} + {out['fees_activation']}) are not the engine's "
                     f"total {p.total_fees} (A-10's arithmetic)")
    return out, probs


# ------------------------------------------------------------------------------------------------ 9.3 per start


def _date_of(ctx: dict[str, Any], start: int, k: int) -> _date:
    d = ctx["dates"][int(start) + max(int(k), 1) - 1]
    return d if isinstance(d, _date) else _date.fromisoformat(str(d)[:10])


def _trades(ledger: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"account": (r["kind"], r["index"]), "day": int(r["day"]), "entry": float(r["trade_index"]),
             "contracts": int(r["contracts"]), "pnl": float(r["pnl"])} for r in ledger]


def uncapped_ladder_differs(ledger: Sequence[dict[str, Any]], rule: Any) -> tuple[int, int, int]:
    """9.3 (5.2's scaling row): of Fast Pass's funded trades, those an uncapped ladder (the record's two contracts plus
    one per step, without the evaluation's cap) would size differently at the session's balance -- the size it would
    take at the trade's own intended risk, allowance and room -- and the funded trades read. **Its control** (m3): the
    same rebuild under the plan's own ladder must give every trade its own contracts; the third number is the trades
    it does not (refusing, in `start_stats`)."""
    from propedge.campaign.sizing import ScalingLadder

    t = T.plan_terms("FP")
    rows = [r for r in ledger if r["kind"] == "funded" and r.get("risk_per_contract")]
    if not rows or rule is None:
        return 0, len(rows), 0
    (b0, m0), (b1, m1) = t.ladder[0], t.ladder[1]
    per, step = float(b1) - float(b0), int(m1) - int(m0)
    first: dict[tuple[int, int], float] = {}
    for r in rows:
        first.setdefault((int(r["index"]), int(r["day"])), float(r["balance_before"]))
    top = max(first.values())
    k = max(len(t.ladder), int(math.floor(max(top, 0.0) / per)) + 2)
    ladder = ScalingLadder(thresholds=tuple(float(b0) + i * per for i in range(k)),
                           minis=tuple(int(m0) + i * step for i in range(k)), micros_per_mini=int(t.micros_per_mini),
                           source="RD-01 9.3: Fast Pass's ladder without its cap")
    unc = dataclasses.replace(rule, ladder=ladder)

    def size(rr: Any, r: dict[str, Any]) -> int:
        rpc = float(r["risk_per_contract"])
        cap = rr.cap_micros("funded", first[(int(r["index"]), int(r["day"]))])
        want = int(math.floor(float(r["intended_risk"]) / rpc))
        if cap is not None:
            want = min(want, int(cap))
        if rr.room_capped("funded") and r.get("room") is not None and np.isfinite(float(r["room"])):
            want = min(want, int(math.floor(max(float(r["room"]), 0.0) / rpc + 1e-9)))
        return want

    control = sum(int(size(rule, r) != int(r["contracts"])) for r in rows)
    return sum(int(size(unc, r) != int(r["contracts"])) for r in rows), len(rows), control


def g10_counts(funded: Sequence[Any], ledger: Sequence[dict[str, Any]], ctx: dict[str, Any], start: int,
               sessions: int) -> dict[str, float]:
    """G-10 at Fast Pass and Quick Pay (9.3) on one replay's funded records and ledger: the sessions with no trade per
    funded account (its live sessions less its trading ones); the accounts idle at least the record's 30 calendar days
    -- that many days with no trade between its activation, its trading days and its end (n3: dates at least 31 days
    apart); the accounts drained below the smallest tradable size -- left open at the replay's end (not breached, not
    ended by a ceiling, a fifth request or a closure: m2) with a last cushion under one micro at the stream's smallest
    stop."""
    idle_days = int(T.parse_money(r"inactive for (\d+) days", T.record_value("tradeday.inactivity_rule"),
                                  "tradeday.inactivity_rule"))
    no_trade = idle = drained = 0
    for f in funded:
        days = sorted({int(r["day"]) for r in ledger if r["kind"] == "funded" and int(r["index"]) == int(f.index)})
        no_trade += max(0, int(f.days) - len(days))
        end = int(f.ended_on) if f.ended_on is not None else int(sessions)
        marks = [int(f.activation_day)] + days + [end]
        gaps = [(_date_of(ctx, start, b) - _date_of(ctx, start, a)).days for a, b in zip(marks, marks[1:])]
        idle += int(bool(gaps) and max(gaps) - 1 >= idle_days)            # n3: the days between, not the gap
        drained += int(f.ended_on is None and not f.closed                     # m2: left open, sitting drained
                       and float(f.balance) - float(f.floor) < float(ctx["min_rpc"]) - 1e-9)
    return {"g10_funded_sessions_no_trade": no_trade, "g10_funded_accounts": len(funded),
            "g10_accounts_idle_30": idle, "g10_accounts_drained": drained}


def start_stats(d: dict[str, Any], s: T.Settings, ctx: dict[str, Any]) -> tuple[dict[str, float], list[str]]:
    """One start's 9.3 counts and 10.1 item 6 fields from its long replay's ledger, records and accounts' counters,
    and its 9.2 problems (refusing). Numbers only; `count_rows` sums them by block."""
    lp, p, led, st0 = d["long"], d["long"].path, d["ledger"], int(d["start"])
    probs: list[str] = []
    x: dict[str, float] = {}
    # 10.1 item 6: what diverges
    x["evaluations_bought"] = len(lp.combines)
    x["funded_activated"] = len(lp.funded)
    x["funded_lost"] = sum(int(f.closed) for f in lp.funded)
    x["payouts_count"] = sum(int(f.n_payouts) for f in lp.funded)
    x["payouts_gross"] = sum(float(f.gross_paid) for f in lp.funded)
    x["payouts_net"] = sum(float(c) for f in lp.funded for c in f.payout_cash)
    fees, fp = fees_by_kind(d, s)
    x.update(fees)
    probs += fp
    x["trades_taken"] = len(led)
    x["realised_risk"] = float(p.realised_risk_total)
    x["intended_capped_risk"] = float(p.intended_capped_risk_total)
    for kind, recs in (("combine", lp.combines), ("funded", lp.funded)):
        sz = [r.sizing for r in recs if r.sizing]
        x[f"realised_risk.{kind}"] = sum(float(z["realised_risk"]) for z in sz)
        x[f"intended_capped_risk.{kind}"] = sum(float(z["intended_capped_risk"]) for z in sz)
        x[f"stood_aside.{kind}"] = sum(int(z["stood_aside"]) for z in sz)
        x[f"trades.{kind}"] = sum(1 for r in led if r["kind"] == kind)
    x["stood_aside"] = float(p.trades_stood_aside)
    # 9.2: fees and requests (refusing); U-7's zero checks on requests (counted)
    probs += fee_problems(led, s)
    rp, n_req, zero = request_problems(d, s)
    probs += rp
    x["oracle_requests_checked"] = n_req
    x["oracle_trades_fee_checked"] = len(led)
    x.update(zero)
    # U-7's other zero checks
    x["zero_peak_hold_queue"] = float(p.peak_queue_length)
    x["zero_resets_bought"] = sum(int(c.resets) for c in lp.combines)
    x["zero_refused_for_cash"] = int(p.combines_abandoned) + int(p.passes_forfeited) + int(bool(p.ruined))
    if s.plan == "DT":
        late = 0
        by_index = {int(c.index): c for c in lp.combines}
        window = int(T.parse_money(r"within (\d+) days", T.record_value("daytraders.eod50k.activation_fee"),
                                   "daytraders.eod50k.activation_fee"))
        for f in lp.funded:
            c = by_index.get(int(f.combine_index))
            if c is not None and c.resolved_on is not None:
                late += int((_date_of(ctx, st0, f.activation_day) - _date_of(ctx, st0, c.resolved_on)).days > window)
        x["zero_dt_activation_late"] = late
    # the adapters' own counters (the long replay), and Quick Pay's floor oracle (refusing)
    for g in d["counts"]:
        for k, v in g.items():
            if k in ("class", "family", "kind", "index", "day", "requests") or not isinstance(v, (int, float)):
                continue
            x[f"acct.{g['kind']}.{k}"] = x.get(f"acct.{g['kind']}.{k}", 0.0) + float(v)
    for h, cs_ in d["exact_counts"].items():
        bad = sum(int(g.get("floor_oracle_breaches", 0)) for g in cs_)
        if bad:
            probs.append(f"exact {h}: Quick Pay's floor fails 9.2 at {bad} closes")
    if x.get("acct.funded.floor_oracle_breaches", 0):
        probs.append(f"Quick Pay's floor fails 9.2 at {int(x['acct.funded.floor_oracle_breaches'])} closes")
    # G-3 per TradeDay run: the executed trades open at a window's start, the signals skipped inside one
    if s.plan in ("FP", "QP"):
        x["tier1_executed_in_window"] = sum(1 for r in led if (st0 + int(r["historical_day"]), int(r["trade_index"]))
                                            in ctx["open"])
        x["tier1_signals_skipped_inside"] = sum(1 for i, _j in ctx["inside"] if st0 <= i < st0 + int(d["sessions"]))
    tr = _trades(led)
    if s.plan == "DT":
        mg = C.martingale_steps(tr)
        ma = C.martingale_accounts(tr)
        x["martingale_per_account"] = mg["per_account"]
        x["martingale_firm_wide"] = mg["firm_wide"]
        x["martingale_accounts_per_account"] = ma["per_account_accounts"]
        x["martingale_accounts_firm_wide"] = ma["firm_wide_accounts"]
        for kind in ("combine", "funded"):
            x[f"martingale_per_account.{kind}"] = ma["per_account_by_kind"].get(kind, 0)
            x[f"martingale_firm_wide.{kind}"] = ma["firm_wide_by_kind"].get(kind, 0)
        x["accounts_trading"] = ma["accounts"]
        x["dt_limit_capped_trades"] = sum(
            1 for r in led if r.get("room_capped") and r.get("room") is not None
            and float(r["room"]) + 1e-9 < float(r["balance_before"]) - float(r["floor"]))
    if s.plan in ("FP", "QP"):
        ta = C.trades_a_session(tr)
        x["max_trades_session_account"] = ta["max_per_account"]
        x["max_trades_session_across"] = ta["max_across"]
        x["sessions_above_trade_line"] = ta["sessions_above_line"]
        x.update(g10_counts(lp.funded, led, ctx, st0, int(d["sessions"])))
    if s.plan == "FP":
        n_u, n_f, n_c = uncapped_ladder_differs(led, d.get("sizing"))
        if n_c:
            probs.append(f"9.3's uncapped-ladder rebuild gives {n_c} of {n_f} funded trades other than their own "
                         "contracts under the plan's own ladder (its control, m3)")
        x["fp_uncapped_ladder_differs"] = n_u
        x["fp_funded_trades_read"] = n_f
    if s.plan == "LU":
        x["lu_fifth_payouts"] = sum(int(int(f.n_payouts) >= 5) for f in lp.funded)
        x["lu_household_closures"] = (sum(int(c.household_closed) for c in lp.combines)
                                      + sum(int(f.household_closed) for f in lp.funded))
    return x, probs


def compare_ts(d: dict[str, Any], ts: dict[str, Any] | None) -> dict[str, float]:
    """9.3 against TS on the same start: whether the plan's daily cash differs at all within 63, 126 and 252 sessions,
    and the trades both take with the contracts they hold, by account kind."""
    if ts is None or d["start"] not in ts:
        return {}
    t = ts[d["start"]]
    out: dict[str, float] = {}
    a, b = np.asarray(d["long"].path.cash_series, float), t["cash"]
    for h in (63, 126, 252):
        if len(a) > h and len(b) > h:
            out[f"differs_by_{h}"] = float(bool(np.any(np.abs(a[:h + 1] - b[:h + 1]) > 1e-9)))
    mine = {(int(r["historical_day"]), int(r["trade_index"])): (r["kind"], int(r["contracts"])) for r in d["ledger"]}
    kinds = ("combine", "funded")
    theirs = {(int(h), int(j)): (kinds[int(k)], int(n)) for h, j, k, n in zip(t["hd"], t["j"], t["kind"], t["n"])}
    for kind in kinds:
        both = [k for k, (kd, _n) in mine.items() if kd == kind and k in theirs and theirs[k][0] == kind]
        out[f"contracts_compared.{kind}"] = len(both)
        out[f"contracts_differ.{kind}"] = sum(int(mine[k][1] != theirs[k][1]) for k in both)
    return out


def ts_compact(d: dict[str, Any]) -> dict[str, Any]:
    """What TS keeps of a start for the pairing (9.3's differs and contracts), as arrays (memory: m7)."""
    led = d["ledger"]
    return {"cash": np.asarray(d["long"].path.cash_series, float),
            "hd": np.array([int(r["historical_day"]) for r in led], np.int32),
            "j": np.array([int(r["trade_index"]) for r in led], np.int32),
            "kind": np.array([0 if r["kind"] == "combine" else 1 for r in led], np.int8),
            "n": np.array([int(r["contracts"]) for r in led], np.int32)}


# ------------------------------------------------------------------------------------------------ a cell


def run_cell(design: str, arm: str, resp: Any, job: dict[str, Any], s: T.Settings, starts: Sequence[int],
             kw: dict[str, Any], point: list[Any] | None, *, direct: bool = True, exact_every: int | None = None,
             ctx: dict[str, Any] | None = None, ts: dict[int, dict[str, Any]] | None = None,
             keep_ts: bool = False, keep_directs: bool = True) -> dict[str, Any]:
    """Every chosen start of one cell. `keep_directs`: keep each start's runs for A-10 (DayTraders' reading and the
    price grid reprice them); other cells drop them as each start's numbers are taken (memory). **One pass through
    A-9** (the third read's (g)): with `direct`, A-9's own
    replays are captured in this process (`firms.captured_run`: the long run through A-9's Q-94 recorder, the
    exact-length runs as `user_beside.replay` returns them) and read for 9.1 items 4 and 5, 9.2's oracles, the start's
    9.3 numbers and A-10 -- no second replay; the start's output composed again from the captured runs must be A-9's
    bit for bit (`first_difference`; a guard on the capture, not a second run). Stops at the first start with a
    refusing problem (r5). Without `direct`, item 5 on A-9's own account counts."""
    every = 1 if resp.kind == "off" else int(B.EXACT_EVERY if exact_every is None else exact_every)
    what = f"{design} {arm} {resp.name}"
    problems: list[str] = []
    checks = {"starts_compared": 0, "trades": 0, "accounts": 0}
    if not direct:
        runs = F.run_plan(design, arm, resp, job, s, list(starts), kw, point=point)
        outs = [o for o, _ in runs]
        counts = [c[0] if c else [] for _, c in runs]
        for o, c in zip(outs, counts):
            p = class_problems(c, s)
            checks["accounts"] += len(c)
            if p:
                problems += [f"{what} start {o['rec']['start_day']}: item 5: {q}" for q in p]
                break
        return {"outs": outs, "counts": counts, "directs": [], "stats": {}, "problems": problems, "checks": checks,
                "ts": None}
    from user_beside_identity import first_difference

    outs, counts, directs, stats, compact = [], [], [], {}, {}
    for st in starts:
        ((o, by_run, got, q94),) = F.run_plan(design, arm, resp, job, s, [int(st)], kw, point=point, capture=True)
        outs.append(o)
        counts.append(by_run[0] if by_run else [])
        if q94:                                         # V5: the recorder's own checks of the recorded long run
            problems += [f"{what} start {st}: Q-94's recorder check: {q}" for q in q94[:3]]
            break
        try:
            d = captured_start(job, s, int(st), kw, point, resp, every, by_run, got)
        except Refused as exc:
            problems.append(f"{what}: {exc}")
            break
        del got
        mine = priced_output(design, arm, resp, d, d["sub"], d["sub"])
        diff = first_difference(o, mine)
        if diff:
            problems.append(f"{what} start {st}: the composition from the captured runs is not A-9's -- {diff}")
        tp = trade_problems(d["ledger"], job["blocks"][int(st):])
        problems += [f"{what} start {st}: item 4: {p}" for p in tp[:3]]
        problems += [f"{what} start {st}: item 5: {p}" for p in class_problems(d["counts"], s)]
        checks["starts_compared"] += 1
        checks["trades"] += len(d["ledger"])
        checks["accounts"] += len(d["counts"])
        if ctx is not None:
            x, sp = start_stats(d, s, ctx)
            x.update(compare_ts(d, ts))
            stats[int(st)] = x
            problems += [f"{what} start {st}: 9.2: {p}" for p in sp]
        if keep_ts:
            compact[int(st)] = ts_compact(d)
        if keep_directs:
            directs.append(keep_direct(d))
        del d
        if problems:
            break                                                     # r5: the reading stops at the first refusal
    return {"outs": outs, "counts": counts, "directs": directs, "stats": stats, "problems": problems,
            "checks": checks, "ts": compact if keep_ts else None}


def trade_problems(ledger: Sequence[dict[str, Any]], blocks: Sequence[Any]) -> list[str]:
    """9.1 item 4 on one replay's ledger: each trade's day and index are a trade of `blocks` (the replay's own), its
    outcome the block's own at its R plus its fee re-pricing (D-324) -- or, at Quick Pay, at most that (a breach at a
    floor its own peak raised ends it sooner, 5.4)."""
    probs = []
    for r in ledger:
        h, j = int(r.get("historical_day", -1)), int(r.get("trade_index", -1))
        if not (0 <= h < len(blocks)) or not (0 <= j < len(blocks[h].pnl)):
            probs.append(f"a trade at day {h} index {j} is not in the design's blocks")
            continue
        if r.get("race_law") is not None:                 # Q-185c (C2-7): a race-arm row books the race, not the log
            if r.get("u") is not None or r.get("mae") is not None:
                probs.append(f"the race-arm trade at day {h} index {j} carries a historical outcome (u or mae)")
            continue
        R = r.get("rr_used", r.get("rr"))
        if R is None or blocks[h].r_by_rr is None or r.get("at_need") or r.get("stretch") or r.get("u") is None:
            continue
        want = float(blocks[h].r_by_rr[float(R)][j]) + float(r.get("fee_adj_r") or 0.0)
        if not np.isclose(float(r["u"]), want, atol=1e-9):
            probs.append(f"the trade at day {h} index {j} books {r['u']} at R {R}, the block's own is {want}")
    return probs


def class_problems(counts: Sequence[dict[str, Any]], s: T.Settings) -> list[str]:
    """9.1 item 5 on one replay (m4): at TS and LU no adapter account; at a plan every adapter account of exactly the
    class `classes_for` names for its kind (through the per-start subclasses' bases)."""
    c_cls, f_cls = A.classes_for(s)
    want = {"combine": None if c_cls is None else c_cls.__name__, "funded": None if f_cls is None else f_cls.__name__}
    bad = [g for g in counts if g.get("family") != want.get(g["kind"])]
    return [f"{len(bad)} accounts not of the plan's own class (first: {bad[0]['class']} as {bad[0]['kind']}, want "
            f"{want.get(bad[0]['kind'])})"] if bad else []


def reading_outs(cell: dict[str, Any], design: str, arm: str, resp: Any, s: T.Settings) -> list[dict[str, Any]]:
    """The outputs a reading reads: A-9's, except at DayTraders, where the recurring Pro fee is charged (A-10)."""
    if s.plan != "DT":
        return cell["outs"]
    t = T.plan_terms("DT")
    return [priced_output(design, arm, resp, d, d["sub"], d["sub"], pro_fee=float(t.funded_recurring_fee),
                          pro_billing_days=int(T.stage2_value("billing_days"))) for d in cell["directs"]]


# ------------------------------------------------------------------------------------------------ 9.3 by block


def _blocks_of(recs: Sequence[dict[str, Any]], h: int) -> dict[str, set[int]]:
    from propedge.research import u_select as S

    out = {"all": {int(r["start_day"]) for r in recs}}
    for b in ("early", "late"):
        out[b] = {int(r["start_day"]) for r in S.block(list(recs), b, int(h))}
    return out


#: 9.3's ratios, each from two summed numbers: (name, numerator, denominator)
RATIOS = (("realised_to_intended_capped", "realised_risk", "intended_capped_risk"),
          ("realised_to_intended_capped.combine", "realised_risk.combine", "intended_capped_risk.combine"),
          ("realised_to_intended_capped.funded", "realised_risk.funded", "intended_capped_risk.funded"),
          ("share_contracts_differ.combine", "contracts_differ.combine", "contracts_compared.combine"),
          ("share_contracts_differ.funded", "contracts_differ.funded", "contracts_compared.funded"),
          ("share_martingale_per_account", "martingale_per_account", "trades_taken"),
          ("share_martingale_firm_wide", "martingale_firm_wide", "trades_taken"),
          ("g10_sessions_no_trade_per_funded_account", "g10_funded_sessions_no_trade", "g10_funded_accounts"),
          ("share_fp_uncapped_ladder_differs", "fp_uncapped_ladder_differs", "fp_funded_trades_read"))


def count_rows(stats: dict[int, dict[str, float]], recs: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """9.3 for one cell, by block: each number summed over the block's starts (a `max_` or `zero_peak_` number its
    largest), each share of starts differing their mean, and `RATIOS` from the sums."""
    blocks = _blocks_of(recs, COUNT_HORIZON)
    keys = sorted({k for x in stats.values() for k in x})
    rows = []
    for b in BLOCKS:
        sel = [stats[s0] for s0 in sorted(stats) if s0 in blocks[b]]
        tot: dict[str, float] = {}
        for k in keys:
            vals = [float(x[k]) for x in sel if k in x]
            if k.startswith("differs_by_"):
                v = float(np.mean(vals)) if vals else float("nan")
                rows.append({"subsection": "count", "block": b, "measure": f"share_starts_{k}", "stat": "value",
                             "value": v, "n": len(vals)})
                continue
            v = (max(vals) if vals else float("nan")) if (k.startswith("max_") or k.startswith("zero_peak")) \
                else float(np.sum(vals))
            tot[k] = v
            rows.append({"subsection": "count", "block": b, "measure": k, "stat": "value", "value": v,
                         "n": len(vals)})
        for name, num, den in RATIOS:
            if num in tot and den in tot:
                v = tot[num] / tot[den] if tot[den] else float("nan")
                rows.append({"subsection": "count", "block": b, "measure": name, "stat": "value", "value": v,
                             "n": len(sel)})
    return rows


#: 10.1 item 6's fields (each plan against TS), from `start_stats`
DIVERGE = ("funded_activated", "funded_lost", "evaluations_bought", "fees_evaluations", "fees_activation",
           "fees_payout", "fees_pro", "payouts_count", "payouts_gross", "payouts_net", "trades_taken",
           "realised_risk")


def diverge_rows(stats: dict[int, dict[str, float]], ts_stats: dict[int, dict[str, float]],
                 recs: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """10.1 item 6, each plan against TS on the same starts, by block: the plan's mean, TS's, the mean difference and
    its distribution over starts, and the shares above, equal and below."""
    blocks = _blocks_of(recs, COUNT_HORIZON)
    rows = []
    for b in BLOCKS:
        common = [s0 for s0 in sorted(stats) if s0 in ts_stats and s0 in blocks[b]]
        for k in DIVERGE:
            x = np.array([float(stats[s0].get(k, np.nan)) for s0 in common], float)
            y = np.array([float(ts_stats[s0].get(k, np.nan)) for s0 in common], float)
            ok = np.isfinite(x) & np.isfinite(y)
            dlt = (x - y)[ok]
            base = {"subsection": "item_6", "block": b, "measure": k, "n": int(ok.sum())}
            rows.append({**base, "stat": "plan_mean", "value": float(np.mean(x[ok])) if ok.any() else float("nan")})
            rows.append({**base, "stat": "ts_mean", "value": float(np.mean(y[ok])) if ok.any() else float("nan")})
            rows.append({**base, "stat": "mean_difference", "value": float(np.mean(dlt)) if ok.any() else float("nan")})
            q = M.quantiles(dlt)
            rows += [{**base, "stat": f"difference_p{p}", "value": q[f"p{p}"]} for p in M.PERCENTILES]
            for nm, v in (("above", dlt > 1e-9), ("equal", np.abs(dlt) <= 1e-9), ("below", dlt < -1e-9)):
                rows.append({**base, "stat": f"share_{nm}", "value": float(v.mean()) if ok.any() else float("nan")})
    return rows


# ------------------------------------------------------------------------------------------------ the pairing


_COVERAGE: dict[tuple[int, int], dict[str, float]] = {}


def coverage_shapes_at(h: int, n_w: int, n_series: int = COVERAGE_SERIES) -> dict[str, float]:
    """10.2 item 7: the coverage of every declared shape at (h, n_w), the coverage seed, `n_series` series (R1: the
    keyword-only `firm_uncertainty.coverage` called by keyword), cached for the run."""
    key = (int(h), int(n_w))
    if key not in _COVERAGE:
        _COVERAGE[key] = {sh: FU.coverage(sh, h=int(h), n_w=int(n_w), n_series=int(n_series), seed=FU.SEED)
                          for sh in FU.coverage_shapes()}
    return _COVERAGE[key]


def coverage_of(h: int, n_w: int, n_series: int = COVERAGE_SERIES) -> float:
    """The worst coverage over the declared shapes at (h, n_w)."""
    return min(coverage_shapes_at(h, n_w, n_series).values())


def coverage_rows() -> list[dict[str, Any]]:
    """The `coverage` section: every setting a reading used, every shape, its coverage, and the worst."""
    rows = []
    for (h, n_w), by in sorted(_COVERAGE.items()):
        for sh, v in sorted(by.items()):
            rows.append({"section": "coverage", "subsection": "shape", "horizon": h, "n_w": n_w, "measure": sh,
                         "stat": "coverage", "value": float(v)})
        worst = min(by.values())
        rows.append({"section": "coverage", "subsection": "worst", "horizon": h, "n_w": n_w, "measure": "worst",
                     "stat": "coverage", "value": float(worst), "note": FU.coverage_label(worst) or ""})
    return rows


def _nets(recs: Sequence[dict[str, Any]], m: int) -> np.ndarray:
    """Each start's month-m net as U1 reads it (r1): `user_journey.Views`, a start whose exact-length run differed read
    from that run."""
    from propedge.research import user_journey as U

    if not recs:
        return np.array([], float)
    return np.asarray(U._net_at(U.Views(list(recs)), U.MONTH * int(m)), float)


def paired_rows(plan: list[dict[str, Any]], ts: list[dict[str, Any]], *, coverage: bool = True,
                coverage_series: int = COVERAGE_SERIES) -> list[dict[str, Any]]:
    """10.1 item 4 on the plan's and TS's start records (same stream and arm): by month and block, the per-start
    difference's distribution, the shares better / equal / worse, the share-ahead cross tab (months 1-3), and the mean
    difference with 10.2's reading."""
    from propedge.research import u_select as S

    tr = {int(r["start_day"]): r for r in ts}
    rows = []
    for m in PAIRED_MONTHS:
        h = HORIZON_OF_MONTH[m]
        for b in BLOCKS:
            mine = [r for r in S.block(list(plan), None if b == "all" else b, h) if int(r["start_day"]) in tr]
            theirs = [tr[int(r["start_day"])] for r in mine]
            x, y = _nets(mine, m), _nets(theirs, m)
            ok = np.isfinite(x) & np.isfinite(y)
            diff = (x - y)[ok]
            n = int(ok.sum())
            base = {"subsection": "net_month", "block": b, "month": m, "horizon": h, "measure": f"net_month_{m}",
                    "n": n}
            q = M.quantiles(diff)
            rows += [{**base, "stat": f"p{p}", "value": q[f"p{p}"]} for p in M.PERCENTILES]
            for k, v in (("better", diff > 1e-9), ("equal", np.abs(diff) <= 1e-9), ("worse", diff < -1e-9)):
                rows.append({**base, "stat": f"share_{k}", "value": float(v.mean()) if n else float("nan")})
            if m <= 3:
                ax, ay = x[ok] > 0, y[ok] > 0
                for k, v in (("plan_not_ts", ax & ~ay), ("both", ax & ay), ("neither", ~ax & ~ay),
                             ("ts_not_plan", ~ax & ay)):
                    rows.append({**base, "measure": f"ahead_month_{m}", "stat": f"share_{k}",
                                 "value": float(v.mean()) if n else float("nan")})
            r = FU.paired_reading(diff, h)
            rows.append({**base, "stat": "mean", "value": r["mean"], "note": r["note"]})
            rows.append({**base, "stat": "n_w", "value": float(r["n_w"])})
            rows.append({**base, "stat": "n_eff", "value": float(r["n_eff"])})
            for k in ("above", "equal", "below"):
                rows.append({**base, "stat": f"windows_{k}", "value": float(r["signs"][k])})
            if r["interval"] is not None:
                rows.append({**base, "stat": "mdd", "value": float(r["mdd"])})
                rows.append({**base, "stat": "interval_lo", "value": float(r["interval"][0])})
                rows.append({**base, "stat": "interval_hi", "value": float(r["interval"][1])})
                if coverage:
                    cov = coverage_of(h, int(r["n_w"]), coverage_series)
                    rows.append({**base, "stat": "coverage", "value": cov, "note": FU.coverage_label(cov) or ""})
    return rows


def paired_scorecard_rows(plan: list[dict[str, Any]], ts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The card (P, S1 ... S5c) on the plan's starts paired with TS's (`u_select.scorecard(paired_with=)`), and TS's
    on the same starts, by block."""
    from propedge.research import u_select as S

    out = []
    for b in BLOCKS:
        which = None if b == "all" else b
        mine = S.scorecard(plan, which, paired_with=ts)
        theirs = S.scorecard(ts, which, paired_with=plan)
        for k in mine:
            out.append({"subsection": "card", "block": b, "measure": k, "stat": "plan", "value": mine[k]["value"],
                        "n": mine[k]["n"]})
            out.append({"subsection": "card", "block": b, "measure": k, "stat": "ts", "value": theirs[k]["value"],
                        "n": theirs[k]["n"]})
    return out


def u1_reported_keys() -> list[tuple[str, str, int]]:
    """10.1 item 1's reported lines as `USER_MILESTONES.md` defines them (M1), each (line, U1's key, the horizon a start
    needs): S2 -- sessions to the first pass p90 and cash spent before it p90; S3d -- the first payout's cash p50; Q --
    the mean value under Q1 (at 21 sessions, and 30 and 42 as its sensitivity) and Q2; S6 -- luck against design: the
    net's spread across starts and its mean at months 1, 3, 6 and 12, each start's monthly mean over its spread (p10,
    p50, p90). The share paid by session 21 by start year is S6's too (`u1_reported_rows`). The keys are U1's own
    (`propedge.research.user_journey.metric_rows`), built from its constants."""
    from propedge.research import user_journey as U

    out = [("S2", f"first_pass:days_p90@{U.PASS_WINDOW}", U.PASS_WINDOW),
           ("S2", f"first_pass:spent_before_p90@{U.PASS_WINDOW}", U.PASS_WINDOW),
           ("S3d", f"first_payout:cash_p50@{U.PAYOUT_WINDOW}", U.PAYOUT_WINDOW)]
    out += [("Q", f"quit:q1_mean_net@{d}", U.QUIT_END) for d in (U.QUIT_DAY, *U.QUIT_SENSITIVITY)]
    out.append(("Q", f"quit:q2_mean_net@{U.QUIT_CHECK}", U.QUIT_END))
    for m in U.LUCK_MONTHS:
        out.append(("S6", f"luck:sd_net_across_starts@{U.MONTH * m}", U.MONTH * m))
        out.append(("S6", f"luck:net_mean@{U.MONTH * m}", U.MONTH * m))
    out += [("S6", f"luck:monthly_mean_over_sd_p{q}@{U.HORIZON}", U.HORIZON) for q in (10, 50, 90)]
    return out


def u1_reported_rows(recs: Sequence[dict[str, Any]], paired_with: Sequence[dict[str, Any]] | None = None
                     ) -> list[dict[str, Any]]:
    """M1: S2, S3d, Q and S6's per-run parts by U1's own readings (`user_journey.metric_rows` through `Views`, so a
    start whose exact-length run differs is read from that run, D-620 (3)(f)), each on its block's starts with its own
    horizon (`u_select.block`, as the card reads P and the guarded measures); `paired_with` -- the other side's records,
    each line then read on the start dates both sides hold, as the paired card. No replay: the cell's records."""
    from propedge.research import u_select as S
    from propedge.research import user_journey as U

    keys = u1_reported_keys()
    year_key = f"luck:share_paid_by@{U.PAID_BY_YEAR_DAY}"
    rows = []
    for b in BLOCKS:
        which = None if b == "all" else b
        for h in sorted({k[2] for k in keys} | {U.PAID_BY_YEAR_DAY}):
            mine = S.block(list(recs), which, h)
            if paired_with is not None:
                dates = {str(r["start_date"]) for r in S.block(list(paired_with), which, h)}
                mine = [r for r in mine if str(r["start_date"]) in dates]
            got = {r["key"]: r for r in U.metric_rows(U.Views(mine))} if mine else {}
            want = [(line, key) for line, key, hh in keys if hh == h]
            if h == U.PAID_BY_YEAR_DAY:
                want += [("S6", k) for k in sorted(got) if k.startswith(year_key + "[")]
            for line, key in want:
                r = got.get(key)
                if r is None and mine:                  # n4: a key U1 no longer makes is a refusal, not a blank line
                    raise Refused(f"M1: U1's metric_rows made no {key} on the {b} block's {len(mine)} starts")
                rows.append({"subsection": "u1_reported", "block": b, "horizon": h, "measure": key, "stat": line,
                             "value": float("nan") if r is None else float(r["value"]),
                             "n": 0 if r is None else int(r["n"])})
    return rows


def luck_across(by_run: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """M1: S6's part that needs every configuration (`user_journey.luck_rows`) across one stream and arm's runs, by
    block: at months 1, 3, 6 and 12 the spread of the runs' mean nets, and each run's spread across starts over it.
    `by_run`: {run: its `u1_reported_rows` (unpaired)}."""
    from propedge.research import user_journey as U

    rows = []
    for b in BLOCKS:
        cfg = {run: [{"key": r["measure"], "value": r["value"]} for r in rs if r["block"] == b]
               for run, rs in by_run.items()}
        for r in U.luck_rows(cfg):
            rows.append({"subsection": "u1_luck", "block": b, "run": r["config"], "measure": r["key"], "stat": "S6",
                         "value": float(r["value"]), "n": int(r["n"])})
    return rows


def coverage_settings(recs: Sequence[dict[str, Any]]) -> set[tuple[int, int]]:
    """m6: every (h, n_w) a reading of this stream can use -- each block's starts at each horizon, windowed on start
    positions (10.2 item 1), with an interval from four kept windows -- known from the block sizes before any reading."""
    from propedge.research import u_select as S

    out = set()
    for h in sorted(set(HORIZON_OF_MONTH.values())):
        for b in BLOCKS:
            nw = FU.n_windows(len(S.block(list(recs), None if b == "all" else b, h)), h)
            if nw >= FU.MIN_WINDOWS:
                out.add((int(h), int(nw)))
    return out


# ------------------------------------------------------------------------------------------------ 9.3, the stream


def tier1_count_rows(stream: str, blocks: Sequence[Any], dates: Sequence[Any]) -> list[dict[str, Any]]:
    """G-3's count (9.3's first line): the offered trades open at a window's start at any offered R, and the entries
    inside a window, by release and year."""
    days, spec = C.tier1_days(), C.window_spec()
    tab: dict[tuple[str, int, str], int] = {}
    for b, dd in zip(blocks, dates):
        d = dd if isinstance(dd, _date) else _date.fromisoformat(str(dd)[:10])
        kinds = days.get(d)
        if not kinds or b.r_by_rr is None or b.exit_by_rr is None or b.entry_t is None:
            continue
        for kind in kinds:
            w = C.windows_of([kind])[0]
            for j in range(len(b.pnl)):
                ex = {float(k): float(v[j]) for k, v in b.exit_by_rr.items() if np.isfinite(float(b.r_by_rr[k][j]))}
                if C.entry_inside(float(b.entry_t[j]), w):
                    tab[(kind, d.year, "entries_inside")] = tab.get((kind, d.year, "entries_inside"), 0) + 1
                elif C.open_at(float(b.entry_t[j]), ex, spec[w][0]):
                    tab[(kind, d.year, "open_at_start")] = tab.get((kind, d.year, "open_at_start"), 0) + 1
    return [{"subsection": "tier1_count", "stream": stream, "release": k, "year": y, "measure": what,
             "value": float(v)} for (k, y, what), v in sorted(tab.items())]


def p16_count_nonzero(rows: Sequence[dict[str, Any]]) -> bool:
    """5.5: the four conditional runs are added when P-16's count of trades open at a window's start is not zero."""
    return any(r["stream"] == "p16" and r["measure"] == "open_at_start" and r["value"] > 0 for r in rows)


def exit_problems(blocks: Sequence[Any], dates: Sequence[Any]) -> dict[str, int]:
    """9.3's must-be-zero checks on the offered trades: any exit after 15:10 CT at any offered R; any trade on an
    early-close session (E-029's calendar)."""
    from extended import calendar_early_closes as E

    if C._lf_sha256(E.CALENDAR_CSV) != C.EARLY_CLOSES_SHA256:
        raise ValueError("config/calendar_early_closes.csv is not the text's pinned calendar (E-029)")
    early = {r["date"] for r in E.read_calendar() if r["close_ct"] and r["close_ct"] < "15:20"}
    late = sum(int(np.nansum(np.where(np.isfinite(np.asarray(v, float)), np.asarray(v, float) > W.C_FLAT, False)))
               for b in blocks if b.exit_by_rr is not None for v in b.exit_by_rr.values())
    on_early = sum(len(b.pnl) for b, d in zip(blocks, dates) if str(d)[:10] in early)
    return {"zero_exits_after_flat": int(late), "zero_trades_on_early_close": int(on_early)}


# ------------------------------------------------------------------------------------------------ A-10's grid


def grid_prices(s: T.Settings) -> list[float]:
    """10.1 item 9: U-2's grid and every listed price (DT, FP, QP); Lucid's struck list price beside its own."""
    if s.plan == "LU":
        return [T.lucid_list_price()]
    listed = {"FP": T.declared("FP.price.listed"), "QP": T.declared("QP.price.listed")}.get(s.plan, ())
    return sorted(set(T.DT_PRICE_GRID) | {float(p) for p in listed})


def _card(recs: list[dict[str, Any]], which: str | None) -> dict[str, float]:
    from propedge.research import u_select as S

    return {k: float(v["value"]) for k, v in S.scorecard(recs, which).items()}


def _m3(recs: list[dict[str, Any]]) -> float:
    x = _nets([r for r in recs if int(r["observed"]) >= HORIZON_OF_MONTH[3]], 3)
    return float(np.nanmean(x)) if len(x) else float("nan")


LUCID_NOTE = "Lucid's price is verified; beside"


def break_even_known(measure: Callable[[float], float], target: float, known: dict[float, float], lo: float,
                     hi: float, tol: float) -> float | None:
    """`firms.break_even_price`'s bisection, step for step -- the same endpoints, midpoints, tests and answer -- with
    each midpoint's side of the target read from the grid's own values where the measure's monotonicity decides it:
    the measure falls in price (a dearer evaluation only subtracts cash, exactly, from every close), so between two
    grid prices p1 < m < p2, f(p2) above the target puts f(m) above it and f(p1) below puts f(m) below it, strictly;
    only an undecided midpoint is recomposed. `known` must be the measure's own values at the grid prices; refused
    (`ValueError`) if they do not fall in price, which would void the inference."""
    ks = sorted(known)
    if any(known[q] > known[p_] + 1e-12 for p_, q in zip(ks, ks[1:])):
        raise ValueError("the grid's values do not fall in price: the side of a midpoint cannot be read from them")

    def f(x: float) -> float:
        return float(known[x]) - target if x in known else float(measure(x)) - target

    def side(m: float) -> float:
        below, above = [q for q in ks if q < m], [q for q in ks if q > m]
        if below and above:                       # a margin, so float noise at the target can never decide a side
            if known[min(above)] - target > 1e-9:
                return 1.0
            if known[max(below)] - target < -1e-9:
                return -1.0
        return float(measure(m)) - target

    f_lo, f_hi = f(float(lo)), f(float(hi))
    if f_lo == 0.0:
        return float(lo)
    if f_hi == 0.0:
        return float(hi)
    if f_lo * f_hi > 0:
        return None
    x, y = float(lo), float(hi)
    while y - x > tol:
        m = 0.5 * (x + y)
        fm = side(m)
        if fm == 0.0:
            return m
        if (fm > 0) == (f_lo > 0):
            x = m
        else:
            y = m
    return 0.5 * (x + y)


#: 10.1 item 9's break-even search: $0 to the grid's top, bisected to a cent (the build's resolution, unchanged)
BREAK_EVEN_TOL = 0.01


def grid_rows(cell: dict[str, Any], design: str, arm: str, resp: Any, s: T.Settings,
              ts_recs: list[dict[str, Any]] | None, *, search: str = "known") -> tuple[list[dict[str, Any]],
                                                                                         dict[float, list[dict]]]:
    """Every money measure and P at each price, by A-10's arithmetic on every run of every start; and the break-even
    price against TS for P, S5a and the mean month-3 net ($0 to $250, to a cent; Lucid's too, r3, labelled). One
    recomposition per price, shared by the grid and the three searches (memoised); `search` "known" bisects through
    `break_even_known` (the grid's values decide a midpoint's side where they can), "plain" through
    `firms.break_even_price` -- the same answers, the toys show (`tests/rd01_reading_synthetic.py`). Returns (rows, the
    records at each price); the recompositions made are counted on the break-even rows."""
    from propedge.research import u_select as S

    pro = (float(T.plan_terms("DT").funded_recurring_fee), int(T.stage2_value("billing_days"))) if s.plan == "DT" \
        else (0.0, None)
    run_price = float(cell["directs"][0]["sub"]) if cell["directs"] else float("nan")
    note = LUCID_NOTE if s.plan == "LU" else ""
    memo: dict[float, list[dict[str, Any]]] = {}

    def recs_at(p: float) -> list[dict[str, Any]]:
        if float(p) not in memo:
            memo[float(p)] = [priced_output(design, arm, resp, d, run_price, p, pro[0], pro[1])["rec"]
                              for d in cell["directs"]]
        return memo[float(p)]

    def value(recs: list[dict[str, Any]], key: str) -> float:
        if key == "mean_net_month_3":
            return _m3(S.block(recs, None, HORIZON_OF_MONTH[3]))
        return _card(recs, None)[key]

    rows, at = [], {}
    known: dict[str, dict[float, float]] = {"P": {}, "S5a": {}, "mean_net_month_3": {}}
    for p in [run_price] + [q for q in grid_prices(s) if q != run_price]:
        recs = recs_at(p)
        at[p] = recs
        for b in BLOCKS:
            which = None if b == "all" else b
            card = _card(recs, which)
            for k, v in card.items():
                rows.append({"subsection": "price_grid", "block": b, "price": p, "measure": k, "value": v,
                             "note": note})
                if b == "all" and k in known:
                    known[k][float(p)] = float(v)
            sub = S.block(recs, which, HORIZON_OF_MONTH[3])
            m3 = _m3(sub)
            rows.append({"subsection": "price_grid", "block": b, "price": p, "measure": "mean_net_month_3",
                         "value": m3, "note": note})
            if b == "all":
                known["mean_net_month_3"][float(p)] = float(m3)
    n_grid = len(memo)
    if ts_recs is not None:
        ts_card = _card(ts_recs, None)
        ts_m3 = _m3(S.block(ts_recs, None, HORIZON_OF_MONTH[3]))
        hi = float(T.DT_PRICE_GRID[-1])
        for key, target in (("P", ts_card.get("P")), ("S5a", ts_card.get("S5a")), ("mean_net_month_3", ts_m3)):
            if target is None or not np.isfinite(target):
                continue

            calls = [0]

            def measure(p: float, key=key, calls=calls) -> float:
                calls[0] += 1
                return value(recs_at(p), key)

            before = len(memo)
            if search == "plain":
                be = F.break_even_price(measure, float(target), 0.0, hi, tol=BREAK_EVEN_TOL)
            else:
                kn = {q: v for q, v in known[key].items() if 0.0 <= q <= hi and np.isfinite(v)}
                be = break_even_known(measure, float(target), kn, 0.0, hi, BREAK_EVEN_TOL)
            rows.append({"subsection": "break_even", "block": "all", "price": float("nan") if be is None else be,
                         "measure": key, "value": float(target), "n": len(memo) - before, "measure_calls": calls[0],
                         "note": "; ".join(x for x in ("none in range" if be is None else "", note,
                                                       f"{len(memo) - before} recompositions beyond the grid's "
                                                       f"{n_grid}") if x)})
    return rows, at


def grid_problems(at: dict[float, list[dict]], other: dict[str, Any] | None, other_price: float, tol: float = 1e-6
                  ) -> list[str]:
    """10.1 item 9's refusing check: the arithmetic at the bracket's other end equals that price's own run on every
    start, every money field and the event days, to 1e-6."""
    if other is None or other_price not in at:
        return []
    mine = {int(r["start_day"]): r for r in at[other_price]}
    probs = []
    for o in other["outs"]:
        r = o["rec"]
        m = mine.get(int(r["start_day"]))
        if m is None:
            probs.append(f"start {r['start_day']}: no repriced record")
            continue
        for k in ("net_month", "fees_month", "pay_days", "pay_cash", "pass_days", "funded_days"):
            a, b = m.get(k), r.get(k)
            a = [np.nan if v is None else float(v) for v in (a or [])]
            b = [np.nan if v is None else float(v) for v in (b or [])]
            if len(a) != len(b) or any(not (np.isnan(x) and np.isnan(y)) and abs(x - y) > tol for x, y in zip(a, b)):
                probs.append(f"start {r['start_day']}: {k} at ${other_price:g} is not the price run's")
                break
    return probs


# ------------------------------------------------------------------------------------------------ the gate beside


def twin_measures(paths: Sequence[Any]) -> dict[str, float]:
    """9.2 on a gate arm's paths: the mean gross payouts per funded account and the pass rate per resolved evaluation
    (passed or failed; m5 -- the others, unresolved at the horizon or closed otherwise, counted beside), each a ratio of
    sums over paths, with their delta-method Monte Carlo standard errors."""
    g = np.array([sum(float(f.gross_paid) for f in lp.funded) for lp in paths], float)
    n = np.array([len(lp.funded) for lp in paths], float)
    w = np.array([sum(int(c.passed) for c in lp.combines) for lp in paths], float)
    a = np.array([sum(int(bool(c.passed) or bool(c.failed)) for c in lp.combines) for lp in paths], float)   # m5
    other = float(sum(len(lp.combines) for lp in paths) - a.sum())

    def ratio(num: np.ndarray, den: np.ndarray) -> tuple[float, float]:
        if den.sum() <= 0:
            return float("nan"), float("nan")
        r = float(num.sum() / den.sum())
        if len(num) < 2:
            return r, float("nan")
        e = num - r * den
        return r, float(math.sqrt(float(np.sum(e ** 2)) / (len(num) - 1) / len(num)) / float(den.mean()))

    rg, sg = ratio(g, n)
    rp, sp = ratio(w, a)
    return {"twin_funded": float(n.sum()), "twin_gross_per_funded": rg, "twin_gross_per_funded_se": sg,
            "twin_evaluations_resolved": float(a.sum()), "twin_evaluations_unresolved_or_closed": other,
            "twin_pass_rate": rp, "twin_pass_rate_se": sp}


def twin_bounds(s: T.Settings, rules: Any) -> tuple[float, float]:
    """9.2's two ceilings for a plan: the funded account's distance from its start to its floor (the mean gross payouts
    per funded account of any fair strategy, the martingale bound), and the evaluation's floor distance over target
    plus floor (propsim D-02's pass rate of any fair strategy)."""
    if s.plan in ("TS", "LU"):
        funded = -float(rules.xfa_mll_start)
        target, floor = float(rules.profit_target), float(rules.mll)
    else:
        t = T.plan_terms(s.plan)
        funded, target, floor = float(t.funded_mll), float(t.eval_target), float(t.eval_mll)
    return funded, floor / (target + floor)


def twin_problems(row: dict[str, Any], s: T.Settings, rules: Any) -> list[str]:
    """9.2, refusing: on the zero-edge twin, the mean gross payouts per funded account above its ceiling, or the pass
    rate per evaluation above its, each beyond the 99.9 % interval -- an engine error, never a finding."""
    pay_cap, pass_cap = twin_bounds(s, rules)
    out = []
    for k, cap in (("twin_gross_per_funded", pay_cap), ("twin_pass_rate", pass_cap)):
        v, se = float(row.get(k, np.nan)), float(row.get(f"{k}_se", np.nan))
        if np.isfinite(v) and np.isfinite(se) and v - TWIN_Z * se > cap + 1e-9:
            out.append(f"{s.plan} {s.corner}: the zero-edge twin's {k} {v:.4f} (se {se:.4f}) is above {cap:g} beyond "
                       "its interval (9.2: an engine error)")
    return out


def gate_rows(blocks: Sequence[Any], kw: dict[str, Any], s: T.Settings, run_gate: Callable, *, fresh_rr: float,
              workers: int = 1, hook_factory: Callable[[str], tuple[Any, list]] | None = None
              ) -> tuple[list[dict[str, Any]], dict[str, list], list[str], list[str]]:
    """10.1 item 8 for one corner: the gate's rows at the plan's arguments (A-1 on the gate, A-8's seams; the placement
    off), point and bound, one call (Quick Pay's class holds the gate's point blocks and classifies on them on both
    arms, M3); and the zero-edge twin as Stage 2 builds it (r8: `portfolio_stage.zero_edge_blocks` at the design's
    fresh R, every bound 0) at the log's own per-trade fees (m4: no plan schedule re-prices it, so its game is fair),
    read on its bound arm, with 9.2's two oracles (`twin_problems`). Labelled: A-11 off;
    DayTraders' inactivity on 21 sessions; its recurring fee left out. Returns (rows, sinks by call, labels, the
    oracles' problems)."""
    import portfolio_stage as ps

    g = F.gate_args(kw, s, point_blocks=blocks if s.plan == "QP" else None)
    e, lb = float(g["e"]), float(g["lb"])
    e_by_rr, lb_by_rr = dict(g["e_by_rr"]), dict(g["lb_by_rr"])
    rules = g["rules"]
    g = {k: v for k, v in g.items() if k not in ("e", "lb", "e_by_rr", "lb_by_rr", "path_hook")}
    if s.plan != "TS" and g.get("rtp", True) is not False:
        raise ValueError("RD-01's gate beside runs with the placement off (rtp=False) at every plan but TS")
    sinks: dict[str, list] = {}
    labels = []
    if s.plan in ("FP", "QP"):
        labels.append("tier-1 liquidation not applied")
    if s.plan == "DT":
        labels += ["inactivity on 21 sessions, not 30 calendar days", "recurring Pro fee left out: an upper bound"]
    zero = {k: 0.0 for k in e_by_rr}

    def call(label: str, blk: Sequence[Any], e_s: float, lb_s: float, e_by: dict, lb_by: dict, keep: tuple[str, ...],
             oracle: bool) -> list[dict[str, Any]]:
        k = dict(g)
        if oracle:                    # m4: the twin at the log's own per-trade fees, so exactly zero-edge (9.2's game)
            k["sizing"] = dataclasses.replace(k["sizing"], fee_schedule=None)
        inner = None
        if hook_factory is not None:
            inner, sinks[label] = hook_factory(label)
        if oracle:
            def hook(shift, p, paths, inner=inner):
                out = dict(inner(shift, p, paths) or {}) if inner is not None else {}
                out.update(twin_measures(paths))
                return out
            k["path_hook"] = hook
        elif inner is not None:
            k["path_hook"] = inner
        rows, _passed = run_gate(list(blk), e=e_s, lb=lb_s, e_by_rr=e_by, lb_by_rr=lb_by, workers=workers, **k)
        return [{**r, "reading": label} for r in rows.to_dict("records") if r.get("shift") in keep]

    twin = ps.zero_edge_blocks(list(blocks), e_by_rr, float(fresh_rr))
    out = call("plan", blocks, e, lb, e_by_rr, lb_by_rr, ("point", "lower_bound"), False)
    tw = call("zero_edge", twin, 0.0, 0.0, zero, zero, ("lower_bound",), True)
    pay_cap, pass_cap = twin_bounds(s, rules)
    tw = [{**r, "twin_gross_per_funded_ceiling": pay_cap, "twin_pass_rate_ceiling": pass_cap,
           "twin_fresh_rr": float(fresh_rr)} for r in tw]
    probs = [p for r in tw for p in twin_problems(r, s, rules)]
    rows = [{**r, "section": "gate", "labels": "; ".join(labels), "status": STATUS} for r in out + tw]
    return rows, sinks, labels, probs


__all__ = ["DECLARATION", "PURPOSES", "BLOCKS", "STATUS", "LADDER", "Refused", "stream_of", "build_with_deltas",
           "delta_problems", "untouched_problems", "arm_inputs", "cell_job", "stream_context", "compose",
           "direct_start", "priced_output", "keep_direct", "schedule_fee", "fee_problems", "tiered_net",
           "request_problems", "fees_by_kind", "uncapped_ladder_differs", "start_stats", "compare_ts", "ts_compact",
           "run_cell", "trade_problems", "class_problems", "reading_outs", "count_rows", "diverge_rows",
           "coverage_shapes_at", "coverage_of", "coverage_rows", "paired_rows", "paired_scorecard_rows",
           "tier1_count_rows", "p16_count_nonzero", "exit_problems", "grid_prices", "grid_rows", "grid_problems",
           "twin_measures", "twin_bounds", "twin_problems", "gate_rows", "break_even_known", "BREAK_EVEN_TOL",
           "u1_reported_keys", "u1_reported_rows", "luck_across", "coverage_settings", "captured_start", "g10_counts"]
