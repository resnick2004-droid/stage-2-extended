"""RD-01's composition (`prereg/RD-01_firm_contracts.md` 4.6, 5, 7, 10.1): A-1 (a plan's contract applied to a design's
replay and gate arguments), A-9's keywords, A-10 (the fee arithmetic), A-11's place in a run, and the reading's
per-start runner. The accounts are `extended.firm_accounts`'; the terms `extended.firm_terms`'; the tier-1 calendar and
booking `extended.firm_counts`'. No rule value is typed here (14.2).

**A-1** (`plan_args`, `gate_args`). On a design's replay arguments (U1's `customer_slices.engine_args`: `draws`, `path`,
`seed`) a plan sets: the rules (target, drawdown, lock, consistency, the funded floor, the winning-day fields of 4.9,
cap, minimum, split, payout fee, the profit-since-request gate, fees and billing), the path's fees, billing, activation,
lag and request timing, the evaluation class on the path (`combine_account_cls`), and the sizing rule's allowances and
per-trade fee schedule (4.8). The funded class and the household reading go to A-9's keywords, never on the path
(`user_beside.base_problems` refuses them there). **TS** leaves the arguments as they are (no keyword). **LU** is
Stage 2's `rc150_firm_split.lucid_setup`, imported, on a `FirmSetup` made from the replay arguments; its funded class
and household reading are moved off the path into the keywords (`funded_account_cls`; `household_closure` False at the
lenient end, absent at the strict end -- the class's own rule, A-9), its `payout_timing` kept on the path, and its
conduct set back to `ConductModel(rtp=False, enforcement_p=0.0)` (the reading's 0 %, placement-off call). The
**seed base** (A-9 (b)) is given only for the denial ladder (10.1 item 7: 20261990).

**A-10** (`subscription_days`, `pro_fee_days`, `repriced`, `break_even_price`): exact arithmetic on a replay's purchase,
billing and activation records -- a price moves every subscription payment, DayTraders' recurring Pro fee is charged
every `billing_days` sessions after activation while the account lives -- valid because the replay's bankroll never
binds (`bankroll_never_binds`, checked on every start).

**A-11** (`tier1_arm`): the run's tier-1 booking (`firm_counts.tier1_blocks`) on the point blocks, then the arm's own
per-R shift (`gate.shifted_blocks`, as `customer_slices.arm_blocks` applies it): a booked trade takes its R's shift like
every outcome at that R (5.5, note C). Off in the gate.

**The runner** (`run_plan`): A-9 (`user_beside.run_starts`) one start at a time in the calling process, each start
with its own classes -- DayTraders' calendar (`with_calendar`), Quick Pay's point outcomes (`with_point`) -- and the
adapters' counts read after it (`firm_accounts.collect`); `workers` processes of the runner's own take the starts in
chunks.
"""
from __future__ import annotations

import dataclasses
import math
from typing import Any, Callable, Sequence

import numpy as np

from extended import use_vendored_stage2

use_vendored_stage2()

from extended import firm_accounts as A  # noqa: E402
from extended import firm_counts as C  # noqa: E402
from extended import firm_terms as T  # noqa: E402

STRICT, LENIENT = T.STRICT, T.LENIENT
#: section 12: the denial ladder's per-start seed base (A-9 (b))
LADDER_SEED = 20261990


def _vendored() -> dict[str, Any]:
    from propedge.campaign.lockstep import ConductModel
    from propedge.campaign.sizing import ScalingLadder
    from propedge.contract.lucid import ONE_TIME_BILLING_DAYS
    from propedge.contract.payout_timing import REQUEST_4_TO_5PM, REQUEST_AFTER_5PM

    return {"ConductModel": ConductModel, "ScalingLadder": ScalingLadder, "ONE_TIME": ONE_TIME_BILLING_DAYS,
            "AT_CLOSE": REQUEST_4_TO_5PM, "AFTER_5PM": REQUEST_AFTER_5PM}


# ------------------------------------------------------------------------------------------------ A-1


def plan_rules(base: Any, s: T.Settings) -> Any:
    """The plan's `Rules`: the design's own (`base`) with the plan's terms in place (4.3-4.5, 4.9; section 5's ends)."""
    p = s.plan
    if p == "TS":
        return base
    t = T.plan_terms(p)
    V = _vendored()
    one_time = t.billing == "one_time"
    kw: dict[str, Any] = dict(
        profit_target=float(t.eval_target), mll=float(t.eval_mll), consistency_max_day_frac=float(t.eval_consistency),
        combine_mll_lock_at=float(t.eval_lock), xfa_mll_start=-float(t.funded_mll), xfa_lock_at=float(t.funded_lock),
        payout_min=float(t.payout_min), subscription=float(s.price),
        billing_days=int(V["ONE_TIME"]) if one_time else int(T.stage2_value("billing_days")),
        activation=float(t.activation), payout_fee=float(t.payout_fee))
    if p == "DT":
        kw.update(std_winning_day_min=float(t.winning_day_min), std_cap=float(t.payout_cap), profit_split=float(t.split))
    elif p == "FP":
        kw.update(std_winning_days=int(t.winning_days), std_winning_day_min=float(t.winning_day_min),
                  std_cap=float(t.payout_cap), profit_split=float(t.split), require_profit_since_payout=True)
    elif p == "QP":                                # the tiered split is the class's; the cap the reference's (5.3)
        kw.update(profit_split=1.0, require_profit_since_payout=False)
    else:
        raise ValueError(f"plan {p!r} has no rules of its own here (LU's are lucid_setup's)")
    return dataclasses.replace(base, **kw)


def plan_sizing(sz: Any, s: T.Settings) -> Any:
    """The sizing rule with the plan's allowances (evaluation limit, funded ladder) and per-trade fee schedule (4.8)."""
    if s.plan == "TS":
        return sz
    t = T.plan_terms(s.plan)
    V = _vendored()
    ladder = V["ScalingLadder"](thresholds=tuple(float(a) for a, _ in t.ladder), minis=tuple(int(m) for _, m in t.ladder),
                                micros_per_mini=int(t.micros_per_mini), source=f"RD-01 {s.plan}")
    return dataclasses.replace(sz, ladder=ladder, combine_limit_micros=int(t.eval_position_micros),
                               fee_schedule=T.fee_schedule(s.plan, s.fee_basis))


def fee_problems(blocks: Sequence[Any]) -> list[str]:
    """4.8: a plan's fee schedule re-prices each trade's own fee, so every day with a trade must carry it."""
    bad = [i for i, b in enumerate(blocks) if len(b.pnl) and getattr(b, "fee", None) is None]
    return [f"{len(bad)} days with trades carry no per-trade fee (first: block {bad[0]}): the build stops (4.8)"] \
        if bad else []


def _lucid(args: dict[str, Any], s: T.Settings) -> tuple[dict[str, Any], dict[str, Any]]:
    import rc150_firm_split as RS

    from propedge.research import hypo_hedge as hh

    V = _vendored()
    draws = dict(args["draws"])
    base = hh.FirmSetup(protocol=draws["protocol"], draws=draws, path=dict(args["path"]))
    lu = RS.lucid_setup(base)
    path = dict(lu.path)
    cls = path.pop("funded_account_cls")
    path.pop("household_closure")
    path["conduct"] = V["ConductModel"](rtp=False, enforcement_p=0.0)
    fs = lu.draws["sizing"].fee_schedule
    if fs is not None and tuple(float(x) for x in fs) != T.fee_schedule("LU"):
        raise ValueError(f"REFUSED (A-1, 4.8): the design's fee schedule {fs} is not LU's {T.fee_schedule('LU')}")
    kw: dict[str, Any] = {"funded_account_cls": cls}
    if s.household is False:                       # the lenient reach; the strict one is the class's own rule (A-9)
        kw["household_closure"] = False
    # 4.8: LU's per-trade costs are TS's -- the design's own sizing fee schedule, which lucid_setup keeps
    return {**args, "draws": dict(lu.draws), "path": path}, kw


def plan_args(args: dict[str, Any], s: T.Settings, *, blocks: Sequence[Any] | None = None,
              ladder: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    """A-1: (the replay arguments with the plan's contract, A-9's keywords for `user_beside.run_starts`). TS: the
    arguments unchanged and no keyword. `blocks` (the run's), when given, are checked for 4.8's per-trade fee.
    `ladder`: the seed base of the denial ladder (10.1 item 7) among the keywords."""
    kw: dict[str, Any] = {}
    if s.plan == "TS":
        out = args
    elif s.plan == "LU":
        out, kw = _lucid(args, s)
    else:
        V = _vendored()
        sz = args["draws"].get("sizing")
        if sz is None:
            raise ValueError("REFUSED (A-1): the design's draws carry no sizing rule; a plan's allowances need one")
        if blocks is not None:
            bad = fee_problems(blocks)
            if bad:
                raise ValueError("REFUSED (A-1): " + "; ".join(bad))
        t = T.plan_terms(s.plan)
        rules = plan_rules(args["path"]["rules"], s)
        lag = int(s.lag) if s.plan == "DT" else int(t.lag_days)
        combine_cls, funded_cls = A.classes_for(s)
        path = dict(args["path"])
        if "combine_account_cls" in path:
            raise ValueError("REFUSED (A-1): the design's path already carries an evaluation class")
        path.update(rules=rules, subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                    activation=float(rules.activation), payout_lag_days=lag, combine_account_cls=combine_cls,
                    payout_timing=V["AT_CLOSE"] if s.plan == "QP" else V["AFTER_5PM"])
        out = {**args, "draws": {**args["draws"], "sizing": plan_sizing(sz, s)}, "path": path}
        kw = {"funded_account_cls": funded_cls}
    if ladder:
        kw["seed_base"] = LADDER_SEED
    return out, kw


def gate_args(gate_kw: dict[str, Any], s: T.Settings, *, point_blocks: Sequence[Any] | None = None
              ) -> dict[str, Any]:
    """A-1 on a design's gate arguments (`extended.gate.run_gate`'s keywords): the rules, sizing, lag, request timing,
    classes and household reading (A-8's seams), and the placement off (`rtp=False`, m5: no conduct model runs at LU,
    DT, FP or QP, 2.3). TS: unchanged. LU: `rc150_firm_split.lucid_setup`'s own output (m5), on a setup made from the
    gate's arguments. DayTraders' classes read 21 sessions (no calendar); its recurring fee is not in the gate. Quick
    Pay's class holds the gate's point blocks (`point_blocks`, M3): its bracket reads them on both of the gate's arms,
    the shifted arm keeping the point list's order; refused without them."""
    if s.plan == "TS":
        return gate_kw
    if s.plan == "LU":
        import rc150_firm_split as RS

        from propedge.research import hypo_hedge as hh

        lu = RS.lucid_setup(hh.FirmSetup(protocol=gate_kw["protocol"], draws={"sizing": gate_kw["sizing"]},
                                         path={"rules": gate_kw["rules"]}))
        out = {**gate_kw, "rules": lu.path["rules"], "sizing": lu.draws["sizing"],
               "payout_lag_days": int(lu.path["payout_lag_days"]), "payout_timing": lu.path["payout_timing"],
               "funded_account_cls": lu.path["funded_account_cls"], "rtp": False}
        if s.household is False:
            out["household_closure"] = False
        return out
    V = _vendored()
    t = T.plan_terms(s.plan)
    combine_cls, funded_cls = A.classes_for(s)
    if s.plan == "QP":
        if point_blocks is None:
            raise ValueError("REFUSED (A-7, M3): Quick Pay's gate class classifies on the point outcomes: give the "
                             "gate's point blocks")
        funded_cls = A.with_point(funded_cls, point_blocks)
    return {**gate_kw, "rules": plan_rules(gate_kw["rules"], s), "sizing": plan_sizing(gate_kw["sizing"], s),
            "payout_lag_days": int(s.lag) if s.plan == "DT" else int(t.lag_days),
            "payout_timing": V["AT_CLOSE"] if s.plan == "QP" else V["AFTER_5PM"],
            "combine_account_cls": combine_cls, "funded_account_cls": funded_cls, "rtp": False}


# ------------------------------------------------------------------------------------------------ A-10


def subscription_days(lp: Any, billing_days: int) -> list[int]:
    """Every evaluation subscription payment's day: the purchase, then each rebill (`lockstep.py` 1588-1609: due at the
    start of `purchase + 1 + k x billing_days`)."""
    out = []
    for c in lp.combines:
        out.append(int(c.purchase_day))
        out += [int(c.purchase_day) + 1 + k * int(billing_days) for k in range(1, int(c.subscriptions_paid))]
    return sorted(out)


def pro_fee_days(lp: Any, billing_days: int, last_day: int) -> list[int]:
    """DayTraders' recurring Pro fee (`daytraders.eod50k.funded_monthly_fee`): due at the start of `activation + 1 +
    k x billing_days`, k >= 1, while the account lives (its last session at or after the due day), within the replay."""
    out = []
    for a in lp.funded:
        end = int(last_day) if a.ended_on is None else min(int(a.ended_on), int(last_day))
        k = 1
        while int(a.activation_day) + 1 + k * int(billing_days) <= end:
            out.append(int(a.activation_day) + 1 + k * int(billing_days))
            k += 1
    return sorted(out)


def _charged(cash: np.ndarray, days: Sequence[int], amount: float) -> np.ndarray:
    out = np.asarray(cash, float).copy()
    for d in days:
        out[int(d):] -= float(amount)
    return out


def bankroll_never_binds(lp: Any) -> bool:
    """A-10's premise on one replay: no purchase or subscription was refused for cash (`combines_abandoned`), no pass
    forfeited for its activation fee, never ruined."""
    p = lp.path
    return not p.ruined and int(p.combines_abandoned) == 0 and int(p.passes_forfeited) == 0


def repriced(lp: Any, run_price: float, price: float, billing_days: int, *, pro_fee: float = 0.0,
             pro_billing_days: int | None = None) -> Any:
    """The replay `lp` at another evaluation price (and, given `pro_fee`, with DayTraders' recurring Pro fee charged):
    the records unchanged, the cash series, final cash, total fees and drawdowns moved by exact arithmetic. Refused
    when the replay's bankroll bound (`bankroll_never_binds`)."""
    if not bankroll_never_binds(lp):
        raise ValueError("REFUSED (A-10): the replay's bankroll bound, so a purchase depends on cash")
    p = lp.path
    subs = subscription_days(lp, billing_days)
    cash = _charged(p.cash_series, subs, float(price) - float(run_price))
    fees = float(p.total_fees) + len(subs) * (float(price) - float(run_price))
    if pro_fee:
        due = pro_fee_days(lp, int(pro_billing_days or billing_days), len(cash) - 1)
        cash = _charged(cash, due, float(pro_fee))
        fees += len(due) * float(pro_fee)
    peak = np.maximum.accumulate(np.concatenate([[float(p.initial_bankroll)], cash]))[1:]
    dd = float(np.max(peak - cash)) if len(cash) else 0.0
    pk = float(max(float(p.initial_bankroll), float(np.max(cash)) if len(cash) else 0.0))
    path = dataclasses.replace(p, cash_series=cash, final_cash=float(cash[-1]), total_fees=fees, max_drawdown=dd,
                               max_drawdown_frac=float(dd / pk) if pk else 0.0)
    return dataclasses.replace(lp, path=path)


def break_even_price(measure: Callable[[float], float], target: float, lo: float = 0.0, hi: float | None = None,
                     tol: float = 1e-6) -> float | None:
    """10.1 item 9: the price in [lo, hi] at which `measure(price)` (falling in price) equals `target` -- bisection on
    the exact arithmetic -- or None ("none in range"). `hi` defaults to the grid's top."""
    hi = float(T.DT_PRICE_GRID[-1]) if hi is None else float(hi)
    f_lo, f_hi = float(measure(lo)) - target, float(measure(hi)) - target
    if f_lo == 0.0:
        return float(lo)
    if f_hi == 0.0:
        return float(hi)
    if f_lo * f_hi > 0:
        return None
    a, b = float(lo), float(hi)
    while b - a > tol:
        m = 0.5 * (a + b)
        fm = float(measure(m)) - target
        if fm == 0.0:
            return m
        if (fm > 0) == (f_lo > 0):
            a = m
        else:
            b = m
    return 0.5 * (a + b)


# ------------------------------------------------------------------------------------------------ A-11 and the arms


def arm_delta(point: Sequence[Any], arm: Sequence[Any], tol: float = 1e-9) -> tuple[float, dict[float, float] | None]:
    """The arm's shift read off its blocks against the point blocks (`gate.shifted_blocks`' delta_r and per-R delta),
    refused unless every trade moved by the same amount at each R."""
    dr, dby = None, {}
    for p, a in zip(point, arm):
        if not len(p.pnl):
            continue
        d = (np.asarray(a.pnl, float) - np.asarray(p.pnl, float)) / np.asarray(p.risked, float)
        dr = float(d[0]) if dr is None else dr
        if np.any(np.abs(d - dr) > tol):
            raise ValueError("the arm's P&L shift is not one delta")
        for k, v in (p.r_by_rr or {}).items():
            dv = np.asarray(a.r_by_rr[k], float) - np.asarray(v, float)
            ok = np.isfinite(dv)
            if ok.any():
                dby.setdefault(float(k), float(dv[ok][0]))
                if np.any(np.abs(dv[ok] - dby[float(k)]) > tol):
                    raise ValueError(f"the arm's shift at R {k} is not one delta")
    return (0.0 if dr is None else dr), (dby or None)


def tier1_arm(point: Sequence[Any], dates: Sequence[Any], reading: str, delta_r: float = 0.0,
              delta_by_rr: dict[float, float] | None = None) -> tuple[list[Any], dict[str, int]]:
    """A-11 for one arm: the tier-1 booking on the point blocks, then the arm's shift (none on the point arm)."""
    from propedge.campaign.gate import shifted_blocks

    blocks, counts = C.tier1_blocks(list(point), list(dates), reading)
    if delta_by_rr is None and delta_r == 0.0:
        return blocks, counts
    return shifted_blocks(blocks, float(delta_r), delta_by_rr), counts


# ------------------------------------------------------------------------------------------------ the runner


def start_classes(s: T.Settings, dates: Sequence[Any], start: int, point: Sequence[Any] | None
                  ) -> tuple[type | None, type | None]:
    """One start's (evaluation class, funded class): the plan's, with DayTraders' calendar from that start's sessions
    and Quick Pay's point outcomes from that start (`point`: the run's point-arm blocks, A-11 applied; M3), refused
    at Quick Pay without them."""
    c_cls, f_cls = A.classes_for(s)
    if s.plan == "DT" and s.inactivity:
        c_cls, f_cls = A.with_calendar(c_cls, dates[start:]), A.with_calendar(f_cls, dates[start:])
    if s.plan == "QP":
        if point is None:
            raise ValueError("REFUSED (A-7, M3): Quick Pay's class classifies on the run's point outcomes: give them")
        f_cls = A.with_point(f_cls, point[start:])
    return c_cls, f_cls


def split_runs(counts: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """A start's account counts cut into its replays (the long run first, then each exact-length run): each replay
    begins with its first evaluation (index 0)."""
    runs: list[list[dict[str, Any]]] = []
    for c in counts:
        if c["kind"] == "combine" and c["index"] == 0 or not runs:
            runs.append([])
        runs[-1].append(c)
    return runs


def captured_run(B: Any, design: str, arm: str, resp: Any, job: dict[str, Any], start: int, kw: dict[str, Any]
                 ) -> tuple[dict[str, Any], dict[tuple[int, int], Any], list[str]]:
    """The single pass (the third read's (g)): one start through A-9 (`run_starts`) with its long replay recorded by
    A-9's own Q-94 recorder seam, and every replay A-9 makes captured in this process as `user_beside.replay` returns
    it -- {(path seed, sessions): the engine's path}, the long run's with its per-trade ledger. Nothing A-9 is handed
    changes but the recorder; Q-94's identity holds its outputs bit for bit with it on. The wrap of this repository's
    `user_beside.replay` (not a vendored function) is restored whatever happens. Also returned: the recorder's own
    per-start checks of the recorded long run (Q-94's `record_path` and opening checks; V5: read, never discarded)."""
    from extended import replay_records as RR

    got: dict[tuple[int, int], Any] = {}
    rec = RR.ReplayRecorder(columns=())
    orig = B.replay

    def spy(blocks: Any, args: Any, path_seed: int) -> Any:
        lp = orig(blocks, args, path_seed)
        got[(int(path_seed), len(blocks))] = lp
        return lp

    B.replay = spy
    try:
        o = B.run_starts(design, arm, resp, job, [int(start)], 1, recorder=rec, **kw)
    finally:
        B.replay = orig
    checks = [str(q) for r in rec.per_start(design, arm, resp.name) for q in r["problems"]]
    return o[0], got, checks


def _chunk(task: tuple) -> list[tuple]:
    design, arm, resp_name, job, s, starts, kw, point = task[:8]
    capture = bool(task[8]) if len(task) > 8 else False
    from extended import user_beside as B

    resp = B.BY_NAME[resp_name]
    out = []
    for st in starts:
        c_cls, f_cls = start_classes(s, job["dates"], int(st), point)
        j = job
        if c_cls is not None:
            j = {**job, "args": {**job["args"], "path": {**job["args"]["path"], "combine_account_cls": c_cls}}}
        k = {**kw, **({} if f_cls is None else {"funded_account_cls": f_cls})}
        A.TALLY.clear()
        if capture:                                # every replay's counts and request logs, its paths, Q-94's checks
            o, got, checks = captured_run(B, design, arm, resp, j, int(st), k)
            out.append((o, split_runs(A.collect(with_requests=True)), got, checks))
        else:
            o = B.run_starts(design, arm, resp, j, [int(st)], 1, **k)
            out.append((o[0], split_runs(A.collect())[:1]))
    return out


def run_plan(design: str, arm: str, resp: Any, job: dict[str, Any], s: T.Settings, starts: Sequence[int],
             keywords: dict[str, Any], *, point: Sequence[Any] | None = None, workers: int = 1,
             chunk: int = 20, capture: bool = False) -> list[tuple]:
    """Every start of one design, arm, response and plan setting: (A-9's output, the long replay's account counts),
    in start order. `job` carries the plan's arguments (`plan_args`), without the classes, which are made per start;
    `keywords` A-9's (the funded class is replaced by each start's own). At `workers` > 1 the starts run in chunks in
    processes of this runner's own, each at one engine worker. `capture` (one worker only): the single pass
    (`captured_run`) -- each start's (output, every replay's account counts with their request logs, its replays'
    paths by (seed, sessions), the recorder's per-start problems)."""
    kw = {k: v for k, v in keywords.items() if k != "funded_account_cls"}
    if s.plan in ("TS", "LU") and keywords.get("funded_account_cls") is not None:
        kw["funded_account_cls"] = keywords["funded_account_cls"]
    if capture and int(workers) > 1:
        raise ValueError("the single pass captures the replays in this process: one worker")
    chunks = [list(starts[i:i + chunk]) for i in range(0, len(starts), chunk)]
    tasks = [(design, arm, resp.name, job, s, c, kw, point, capture) for c in chunks]
    if int(workers) <= 1:
        res = [_chunk(t) for t in tasks]
    else:
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=int(workers)) as ex:
            res = list(ex.map(_chunk, tasks))
    return [x for part in res for x in part]


__all__ = ["LADDER_SEED", "plan_rules", "plan_sizing", "fee_problems", "plan_args", "gate_args", "subscription_days",
           "pro_fee_days", "bankroll_never_binds", "repriced", "break_even_price", "arm_delta", "tier1_arm",
           "start_classes", "split_runs", "captured_run", "run_plan"]
