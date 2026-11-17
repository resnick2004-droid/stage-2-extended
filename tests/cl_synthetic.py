"""RD-03's build checks on synthetic campaigns (`prereg/RD-03_contract_levers.md` 14.3; its build Q-119): one section a
process (the vendored engine on this process's `sys.path`), each printing one JSON line whose `problems` must be empty.

    python tests/cl_synthetic.py <repository root> <section>      # sections: SECTIONS below

The toy campaigns draw from section 12's toy seed (`TOY_SEED`, "the build's toy campaigns"); no other seed of the
block is written here. Nothing here reads a bar or the atlas.
"""
from __future__ import annotations

import dataclasses
import hashlib
import inspect
import json
import subprocess
import sys
import time
import types
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
for _p in (str(ROOT), str(ROOT / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import levers_path as LP  # noqa: E402
from extended import levers_readings as LR  # noqa: E402
from extended import levers_terms as LT  # noqa: E402
from propedge.campaign import lockstep as V  # noqa: E402
from propedge.campaign.lockstep import ConductModel, FocusedTraderModel, binary_draw_factories  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.contract.adapter import rules_from_ledger  # noqa: E402

#: section 12: "the build's toy campaigns (T-1 to T-5, T-7, T-10, T-12, T-13, T-15) and T-3's synthetic late block"
TOY_SEED = 20262241
#: the adapters before Q-119 (master at the build's base, 15c5042), pinned by the sha256 of their LF text (T-15)
BASE_COMMIT = "15c5042"
BEFORE_SHA256 = {"extended/user_beside.py": "3750f76ac565f1d944b91783375940bbd9cbfcdda7f911237558581166c79466",
                 "extended/gate.py": "760af451467afa2c9c1eedd8bc948ce7c00e608fc405fe35b5133b448be6dc91"}
RULES = rules_from_ledger()
PROTO = Protocol(name="cl_toy", combine_rr=2.0, combine_risk=1000.0, funded_rr=2.0, funded_risk=1000.0,
                 trades_per_day=1, max_concurrent_accounts=5)
FEE = LT.reactivation_fee()
WIN_D = LT.reactivation_window_days()
WIN_S = LT.sessions_for_days(WIN_D)
CAP = LT.funded_cap()
SUB, ACT = LT.standard_prices()
NAF_SUB, NAF_ACT = LT.naf_prices()
EXP_D = int(LR.reading("expiry_30_calendar_days"))
EXP_S = LT.sessions_for_days(EXP_D)
problems: list[str] = []
notes: list[str] = []


def check(ok: bool, what: str) -> None:
    if not ok:
        problems.append(what)


# ------------------------------------------------------------------------------------------------ the toys


def path_kw(edge: float = 0.05, seed: int = TOY_SEED, bankroll: float = 1e9, **over):
    c, f = binary_draw_factories(PROTO, edge, seed, RULES)
    kw = dict(edge=edge, rules=RULES, initial_bankroll=bankroll, max_concurrent_accounts=CAP, subscription=SUB,
              billing_days=int(RULES.billing_days), activation=ACT, payout_lag_days=3, max_concurrent_combines=CAP,
              max_total_accounts=CAP, conduct=ConductModel(rtp=False, enforcement_p=0.0), combine_max_days=2000,
              funded_horizon_days=100_000, combine_draw_factory=c, funded_draw_factory=f, purchase_budget=(20, 21))
    kw.update(over)
    return kw


def run(levers=None, horizon: int = 253, seed: int = 7, vendored: bool = False, **kw):
    a = path_kw(**kw)
    if vendored:
        return V.simulate_lockstep_path(PROTO, seed=seed, horizon_days=horizon, **a)
    LP.take_published()
    lp = LP.simulate_lockstep_path(PROTO, seed=seed, horizon_days=horizon, **a, levers=levers)
    return lp, LP.take_published()


def diff(a, b, where: str = "") -> str | None:
    """The first difference between two engine objects, field by field (arrays exactly, NaN equal to NaN)."""
    if dataclasses.is_dataclass(a) and dataclasses.is_dataclass(b):
        for f in dataclasses.fields(a):
            if f.name == "lever_counts":
                continue
            d = diff(getattr(a, f.name), getattr(b, f.name), f"{where}.{f.name}")
            if d:
                return d
        return None
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        x, y = np.asarray(a), np.asarray(b)
        if x.shape != y.shape or not np.array_equal(x, y, equal_nan=x.dtype.kind == "f"):
            return where
        return None
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            return f"{where} keys"
        for k in a:
            d = diff(a[k], b[k], f"{where}[{k!r}]")
            if d:
                return d
        return None
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return f"{where} length"
        for i, (x, y) in enumerate(zip(a, b)):
            d = diff(x, y, f"{where}[{i}]")
            if d:
                return d
        return None
    if isinstance(a, float) and isinstance(b, float) and a != a and b != b:
        return None
    return None if a == b else where


def b2f(limit: int = 1, **kw) -> LP.Levers:
    return LP.Levers(reactivations=limit, reactivation_fee=FEE, reactivation_window_days=WIN_D,
                     reactivation_window_sessions=WIN_S, counters=True, **kw)


def inv(c: int, bank: bool, expiry: str = "none", sessions: int | None = None, **kw) -> LP.Levers:
    e = {} if expiry == "none" else {"expiry": "30", "expiry_days": EXP_D, "expiry_sessions": sessions or EXP_S}
    return LP.Levers(max_concurrent_combines=c, lift_joint_cap=True, stop_buying_when_queued=not bank, counters=True,
                     **e, **kw)


def inv_kw(lv: LP.Levers) -> dict:
    return dict(max_concurrent_combines=lv.max_concurrent_combines, max_total_accounts=None,
                stop_buying_when_queued=lv.stop_buying_when_queued)


def house(rule: str, expiry: str = "none", sessions: int | None = None) -> LP.Levers:
    e = {} if expiry == "none" else {"expiry": "30", "expiry_days": EXP_D, "expiry_sessions": sessions or EXP_S}
    return LP.Levers(house=rule, counters=True, **e)


def refused(fn, exc=Exception) -> bool:
    try:
        fn()
    except exc:
        return True
    return False


# ------------------------------------------------------------------------------------------------ the replay toy


def toy_job(n_days: int = 150, start: str = "2023-01-02", seed: int = TOY_SEED, bad_every: int = 13):
    from propedge.campaign.payout_method import payout_method_terms
    from propedge.contract.rules import load_rules
    from propedge.outcomes.distribution import DayBlock

    from extended import user_beside as B

    rng = np.random.default_rng([seed, 3])
    days = [d.date().isoformat() for d in pd.bdate_range(start, periods=n_days)]
    blocks = []
    for i in range(n_days):
        k = 1 + (i % 4)
        et = np.array([500.0 + 60.0 * j for j in range(k)])
        bad = (i % bad_every) in (bad_every - 2, bad_every - 1)
        win = np.array([(not bad) and rng.random() < 0.6 for _ in range(k)])
        blocks.append(DayBlock(pnl=np.where(win, 1000.0, -500.0), risked=np.full(k, 500.0),
                               exit_reasons=tuple("target" if w else "stop" for w in win), entry_t=et, exit_t=et + 30.0))
    proto = Protocol(name="cl_replay_toy", combine_rr=2.0, combine_risk=500.0, funded_rr=2.0, funded_risk=500.0,
                     trades_per_day=4, max_concurrent_accounts=CAP)
    lag = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
    args = {"draws": {"protocol": proto, "mode": "rotation", "flip": None},
            "path": dict(edge=0.0, rules=RULES, initial_bankroll=1e9, max_concurrent_accounts=CAP, subscription=SUB,
                         billing_days=int(RULES.billing_days), activation=ACT, payout_lag_days=lag,
                         max_concurrent_combines=CAP, max_total_accounts=CAP,
                         conduct=ConductModel(rtp=False, enforcement_p=0.0), combine_max_days=2000,
                         funded_horizon_days=100_000, purchase_budget=(20, 21)),
            "seed": B.SEED_BLOCK[1]}
    return {"engine": "single", "blocks": blocks, "dates": days, "args": args}


def outs_diff(a, b) -> str | None:
    if len(a) != len(b):
        return "the number of starts"
    for x, y in zip(a, b):
        d = diff(x, y, f"start {x['rec']['start_day']}")
        if d:
            return d
    return None


# ------------------------------------------------------------------------------------------------ sections


def t1() -> None:
    """T-1: A-1 with every option off equals the vendored path bit for bit; its guard; its recomposition proof."""
    for seed in (3, 7, 11):
        for extra in ({}, {"record_trades": True, "record_days": True},
                      {"conduct": ConductModel(rtp=True, enforcement_p=0.25)},
                      {"focused_trader": FocusedTraderModel(path="corrective", window_days=21, funded_lost=3)}):
            a = run(vendored=True, seed=seed, **extra)
            for lv in (None, LP.Levers(), LP.Levers(counters=True)):
                b, _ = run(lv, seed=seed, **extra)
                d = diff(a, b)
                check(d is None, f"T-1: off ({lv}) differs from the vendored path at {d} (seed {seed}, {list(extra)})")
    probs = LP.recomposition_problems()
    check(not any(probs.values()), f"T-1: the recomposition proof fails: {probs}")
    ml = LP.marked_lines()
    check(ml["simulate_lockstep_path"] > 0 and ml["_one_path"] == 1 and ml["_path_chunk"] == 0
          and ml["_run_paths"] == 0, f"T-1: the marked lines are not the declared additions: {ml}")
    wrong = dict(LP.VENDORED_SHA256, simulate_lockstep_path="0" * 64)
    check(refused(lambda: LP.check_vendored_source(wrong), RuntimeError), "T-1: the guard does not refuse a changed source")
    check(LP.vendored_sha256() == LP.VENDORED_SHA256, "T-1: the vendored sources are not the pinned ones")
    # the replay through A-1 with every option off: the vendored replay, start for start (the shared day draws)
    from extended import user_beside as B

    job = toy_job()
    for s in (0, 17, 40):
        sl = job["blocks"][s:s + 90]
        a = B.replay(sl, job["args"], 5)
        rp = LP.replay_with(LP.Levers(counters=True), job["blocks"], job["dates"], B.replay, LP.StartCounts())
        d = diff(a, rp(sl, job["args"], 5))
        check(d is None, f"T-1: the replay through A-1 differs from the vendored replay at start {s}: {d}")


class Stub:
    """A funded account's fields the reactivation reads (T-2's component in isolation)."""

    def __init__(self, index, ended_on, closed=True, n_payouts=0, denied=0, abandoned=False, household_closed=False,
                 ftp_closed=False):
        self.index, self.ended_on, self.closed, self.n_payouts, self.denied = index, ended_on, closed, n_payouts, denied
        self.abandoned, self.household_closed, self.ftp_closed = abandoned, household_closed, ftp_closed
        self.policy_override, self.dll, self.combine_index, self.combine_purchase_day = None, None, index, 0


def _reactivate(state, day, cash, funded, ftp_placed=None):
    fin: list = []
    f = binary_draw_factories(PROTO, 0.0, 1, RULES)[1]
    return state.reactivate(day, cash, 0.0, 100, funded, fin, V.FundedAccount, f, None, RULES, 504, V.DEFAULT_PAYOUT_TIMING, ftp_placed, None, CAP), fin


def t2() -> None:
    """T-2: L-B -- eligibility, the limit, the price, the timing, the seat, the cash, the lapse, the placement bar, the
    account restarted, counted as funded and lost and not as a purchase."""
    S = LP.LeverState
    st = S(b2f(2), initial_bankroll=0.0, horizon_days=100)
    cases = {"a breach before any request": (Stub(1, 5), True), "after a request": (Stub(2, 5, n_payouts=1), False),
             "a horizon closure": (Stub(3, 5, closed=False), False), "a denial's closure": (Stub(4, 5, denied=1), False),
             "a household closure": (Stub(5, 5, closed=False, household_closed=True), False),
             "a Focused Trader closure": (Stub(6, 5, closed=False, ftp_closed=True), False),
             "an abandon": (Stub(7, 5, abandoned=True), False)}
    for what, (a, want) in cases.items():
        check(st._eligible(a) == want, f"T-2: eligibility wrong for {what}")
    # immediate reactivation: the lost account leaves, the new one takes its seat, cash and fees together
    st = S(b2f(1), initial_bankroll=0.0, horizon_days=100)
    lost = Stub(1, 5)
    others = [Stub(i, None, closed=False) for i in (2, 3, 4, 5)]
    (cash, fees, nf, funded), fin = _reactivate(st, 5, 10_000.0, [lost, *others])
    check(len(funded) == 5 and lost not in funded and fin == [lost], "T-2: the lost account does not leave at once")
    new = funded[-1]
    check(isinstance(new, V.FundedAccount) and new.activation_day == 5 and new.start_day == 6, "T-2: not trading from "
          "the next session")
    check(new.B == 0.0 and new.F == float(RULES.xfa_mll_start) and new.win_days == 0 and new.n_payouts == 0,
          "T-2: the account is not restarted (balance $0, floor, no winning days, unpaid)")
    check(abs(cash - (10_000.0 - FEE)) < 1e-9 and abs(fees - FEE) < 1e-9 and nf == 101, "T-2: cash and fees not "
          "debited together at the record's price")
    # the limit across lives: the new account's own loss is its XFA's second
    new.closed, new.ended_on = True, 9
    (cash2, _, _, funded2), _ = _reactivate(st, 9, 10_000.0, funded)
    check(st.c["reactivations"] == 1 and len(st.refused["limit"]) == 1, "T-2: the limit of 1 per XFA not held across lives")
    st2 = S(b2f(2), initial_bankroll=0.0, horizon_days=100)
    lost = Stub(1, 5)
    (_, _, _, f2), _ = _reactivate(st2, 5, 10_000.0, [lost])
    f2[-1].closed, f2[-1].ended_on = True, 8
    _reactivate(st2, 8, 10_000.0, f2)
    check(st2.c["reactivations"] == 2 and st2.c["reactivations_second"] == 1, "T-2: the limit of 2 not reached")
    # the cash cannot pay: offered each evening within the window, then lapsed; barred under a placement
    st3 = S(b2f(1), initial_bankroll=0.0, horizon_days=100)
    lost = Stub(1, 5)
    (c3, _, _, f3), _ = _reactivate(st3, 5, 10.0, [lost])
    check(st3.c["reactivations"] == 0 and len(st3.waiting) == 1 and lost in f3, "T-2: not left waiting for cash")
    _reactivate(st3, 5 + WIN_S, 10.0, [x for x in f3 if x is not lost])
    check(len(st3.waiting) == 1, "T-2: lapsed inside the window")
    _reactivate(st3, 6 + WIN_S, 10.0, [])
    check(len(st3.waiting) == 0 and st3.c["reactivations_lapsed"] == 1, "T-2: no lapse after the window (sessions)")
    st4 = S(b2f(1).with_dates(pd.bdate_range("2024-01-01", periods=60).strftime("%Y-%m-%d").tolist()),
            initial_bankroll=0.0, horizon_days=60)
    lost = Stub(1, 3)
    _reactivate(st4, 3, 10.0, [lost])
    o = st4.lv.day_ordinals
    last_in = max(d for d in range(3, 60) if o[d] - o[3] <= WIN_D)
    _reactivate(st4, last_in, 10.0, [])
    check(len(st4.waiting) == 1, "T-2: lapsed inside the 30 calendar days")
    _reactivate(st4, last_in + 1, 10.0, [])
    check(st4.c["reactivations_lapsed"] == 1, "T-2: no lapse after 30 calendar days")
    st5 = S(b2f(1), initial_bankroll=0.0, horizon_days=100)
    _reactivate(st5, 5, 10_000.0, [Stub(1, 5)], ftp_placed={"path": "slowdown"})
    check(st5.c["reactivations"] == 0 and len(st5.refused["placement"]) == 1, "T-2: not barred under a placement")
    # on a toy campaign: every reactivation at the price and of an eligible loss, never a sixth, the evening's first
    base, _ = run(None, edge=0.05)
    for limit in (1, 2):
        lp, c = run(b2f(limit), edge=0.05, record_trades=True)
        check(c["reactivations"] > 0, f"T-2: the toy makes no reactivation at limit {limit}")
        check(max(c["reactivation_ordinals"] or [0]) <= limit, f"T-2: beyond the limit {limit}")
        check(abs(c["reactivation_fees"] - FEE * c["reactivations"]) < 1e-6 and not c["fees_by_kind_problem"],
              "T-2: the fees by kind")
        check(c["max_funded_live"] <= CAP and c["max_accounts_live"] <= CAP, "T-2: a sixth account (or the joint cap "
              "moved by the swap)")
        check(set(c["reactivation_days"]) <= set(c["reactivation_loss_days"]), "T-2: a reactivation not on its "
              "breach's evening")
        react = {f["index"]: f["activation_day"] for f in c["reactivated_fates"]}
        for f in lp.funded:
            if f.index in react:
                check(f.activation_day == react[f.index], "T-2: the reactivated record's activation day")
        check(lp.purchase_budget["purchases_and_resets"] == c["evaluations_bought"], "T-2: a reactivation counted in "
              "the purchase budget")
        cash = np.asarray(lp.path.cash_series, float)
        check(abs((lp.path.initial_bankroll - cash[-1]) + lp.path.total_payouts - lp.path.total_fees) < 1e-6,
              "T-2: U1's check of fees against the cash fails")
    # the counted reading: the Focused Trader purchase measure counts each reactivation (a model that never places)
    ftp = FocusedTraderModel(path="slowdown", window_days=21, combine_purchases=10 ** 6)
    a, ca = run(b2f(1), focused_trader=ftp)
    b, cb = run(b2f(1, count_reactivations=True), focused_trader=ftp)
    check(b.focused_trader["total_combine_purchases_and_resets"] == a.focused_trader[
        "total_combine_purchases_and_resets"] + cb["reactivations"] and cb["reactivations_counted_in_ftp"]
          == cb["reactivations"], "T-2: the counted reading does not count each reactivation")
    check(a.focused_trader["total_funded_lost"] >= ca["eligible_losses"], "T-2: a reactivated account's loss not "
          "counted among funded accounts lost")


def t4() -> None:
    """T-4: L-I -- the seat limits five each, resets off and activation on activation, the sentinel never loaded,
    the keywords reaching the path, C = 5 equal to its base until its first pass, the queue at five funded only,
    banking, the expiry, an expiry beyond the horizon."""
    from extended import cl_reading as CL

    job = toy_job()
    check(not CL.seat_limit_problems(job["args"]["path"]), "T-4: the toy's seat limits are not read as five each")
    bad = dict(job["args"]["path"], max_total_accounts=4)
    check(bool(CL.seat_limit_problems(bad)), "T-4: a joint cap of 4 is not refused")
    check(refused(lambda: run(LP.Levers(counters=True), reset_failed_combines=True), LP.LeverRefused),
          "T-4: resets on not refused")
    check(refused(lambda: run(LP.Levers(counters=True), activation_timing=V.ACTIVATION_ON_PASS), LP.LeverRefused),
          "T-4: activation at the pass not refused")
    check(refused(lambda: LT.stage2_value("hold_expiry_days"), LT.NeverLoaded), "T-4: Stage 2's sentinel loads")
    check(refused(lambda: LT.record_value("hold_expiry_days"), LT.NeverLoaded), "T-4: the record's unstated loads")
    lv = CL.cell_levers("inv7_bank_30", CAP)
    a = LP.levers_args(job["args"], lv)
    check(a["path"]["max_concurrent_combines"] == CAP + 2 and a["path"]["max_total_accounts"] is None
          and a["path"]["stop_buying_when_queued"] is False, "T-4: the seat keywords do not reach the replay's path")
    check(LP.levers_args(job["args"], None) is job["args"], "T-4: absent changes the arguments")
    # at C = 5 the cell equals its base until its first pass; the queue forms only at five funded
    base, cb = run(LP.Levers(counters=True), edge=0.08, record_days=True)
    for bank in (True, False):
        lv = inv(CAP, bank)
        lp, c = run(lv, edge=0.08, record_days=True, **inv_kw(lv))
        p = min([r.resolved_on for r in lp.combines if r.passed] or [len(c["cash_closes"])])
        check(np.array_equal(np.asarray(c["cash_closes"][:p]), np.asarray(cb["cash_closes"][:p])),
              f"T-4: C = 5 differs from its base before its first pass (banking {bank})")
        waited = [f for f in lp.funded if f.activation_day > [r.resolved_on for r in lp.combines
                                                                if r.index == f.combine_index][0]]
        for f in waited:
            pd_ = [r.resolved_on for r in lp.combines if r.index == f.combine_index][0]
            check(lp.campaign_days[pd_]["active_funded"] >= CAP, "T-4: a queue formed below five funded")
    lb, cbk = run(inv(CAP + 2, True), edge=0.08, **inv_kw(inv(CAP + 2, True)))
    lh, chd = run(inv(CAP + 2, False), edge=0.08, **inv_kw(inv(CAP + 2, False)))
    check(cbk["passes_queued"] > 0, "T-4: the toy forms no queue")
    check(cbk["evaluations_bought"] > chd["evaluations_bought"], "T-4: banking on does not buy while passes wait")
    # the expiry: removed past the window, unpaid and unseated; beyond the horizon equals exp_none
    l2 = inv(CAP + 2, True, "30", sessions=2)
    lx, cx = run(l2, edge=0.08, **inv_kw(l2))
    check(cx["passes_expired"] > 0 and max(cx["queue_waits"] or [0]) <= 2, "T-4: the expiry does not remove a pass "
          "past its window")
    act = sum(1 for f in lx.funded) - cx["reactivations"]
    check(abs(cx["fees_activation"] - ACT * act) < 1e-6, "T-4: a lost pass paid its activation")
    l9 = inv(CAP + 2, True, "30", sessions=10 ** 6)
    l0 = inv(CAP + 2, True)
    a9, _ = run(l9, edge=0.08, **inv_kw(l9))
    a0, _ = run(l0, edge=0.08, **inv_kw(l0))
    check(diff(a9, a0) is None, "T-4: an expiry beyond the horizon differs from exp_none")
    # the component in isolation: the 30 calendar days on the replay's dates
    st = LP.LeverState(inv(CAP + 2, True, "30").with_dates(pd.bdate_range("2024-01-01", periods=60)
                                                              .strftime("%Y-%m-%d").tolist()), initial_bankroll=0.0,
                       horizon_days=60)

    class C:
        def __init__(self, i, r):
            self.index, self.resolved_on = i, r

    o = st.lv.day_ordinals
    q = [C(1, 2)]
    last_in = max(d for d in range(2, 60) if o[d] - o[2] <= EXP_D)
    st.expire(last_in, q)
    check(len(q) == 1, "T-4: expired inside 30 calendar days")
    st.expire(last_in + 1, q)
    check(not q and st.c["passes_expired"] == 1, "T-4: not expired at the first close past 30 calendar days")


def t5() -> None:
    """T-5: L-H -- the trigger, equal to the base before it, no fee leaving net cash at or below zero after it,
    house_stop buying nothing, the rebill withheld, a pass waiting for cash (and lost under exp_30), every branch of
    the purchase step, the trigger unreachable equal to the base, ahead at every close after the trigger."""
    st = LP.LeverState(house("zero"), initial_bankroll=1000.0, horizon_days=50)
    st.after_arrivals(3, 1000.0)
    check(st.triggered is None, "T-5: triggered at net zero")
    st.after_arrivals(4, 1000.5)
    check(st.triggered == 4, "T-5: not triggered at the first close above zero")
    st.after_arrivals(5, 5000.0)
    check(st.triggered == 4, "T-5: the trigger moved")
    check(st.withholds_purchase(1049.0, SUB) and not st.withholds_purchase(1100.0, SUB), "T-5: zero's purchase rule")
    check(st.withholds_rebill(1049.0, SUB, 6) and not st.withholds_rebill(2000.0, SUB, 6), "T-5: zero's rebill rule")
    s2 = LP.LeverState(house("stop"), initial_bankroll=1000.0, horizon_days=50)
    check(not s2.withholds_purchase(9e9, SUB), "T-5: stop withholds before the trigger")
    s2.after_arrivals(1, 1001.0)
    check(s2.withholds_purchase(9e9, SUB) and s2.withholds_rebill(9e9, SUB, 2), "T-5: stop's rules after the trigger")
    src = inspect.getsource(LP.simulate_lockstep_path)
    check(src.count("lv.withholds_purchase(cash, subscription)") == 5, "T-5: the rule does not reach every branch of "
          "the purchase step (the loop, its three diagnostics and the step's own count)")
    base, cb = run(LP.Levers(counters=True), edge=0.05)
    for rule in ("stop", "zero"):
        for expiry in ("none", "30"):
            lp, c = run(house(rule, expiry), edge=0.05)
            t = c["house_trigger_day"]
            check(t > 0, f"T-5: the toy never triggers ({rule}, {expiry})")
            check(np.array_equal(np.asarray(c["cash_closes"][:t]), np.asarray(cb["cash_closes"][:t])),
                  f"T-5: not equal to the base before the trigger ({rule}, {expiry})")
            cash = np.asarray(c["cash_closes"], float) - 1e9
            check(bool((cash[t:] > 0).all()) and c["house_closes_not_ahead"] == 0, f"T-5: a close after the trigger "
                  f"at or below zero ({rule}, {expiry})")
            if rule == "stop":
                check(c["house_purchases_after_trigger"] == 0, "T-5: house_stop bought after the trigger")
                ends = [r for r in lp.combines if r.abandoned and r.resolved_on is not None and r.resolved_on > t]
                check(c["house_rebills_withheld"] == len(ends), "T-5: the withheld rebills are not the evaluations "
                      "abandoned at their billing day")
    # the trigger unreachable equals the base
    lp0, _ = run(house("zero"), edge=-0.5)
    b0 = run(None, edge=-0.5)[0]
    check(diff(lp0, b0) is None, "T-5: the trigger unreachable differs from the base")
    # a pass waits for cash: small bankroll toy, activation withheld while net cash cannot pay it; exp_30 loses it
    stw = LP.LeverState(house("stop", "30", sessions=2), initial_bankroll=1000.0, horizon_days=50)
    stw.after_arrivals(1, 1100.0)

    class C:
        def __init__(self, i, r):
            self.index, self.resolved_on = i, r

    p = C(9, 3)
    check(stw.withholds_activation(1100.0, 149.0, p) and stw.cash_wait[9] == 1, "T-5: the activation not withheld "
          "for cash")
    check(not stw.withholds_activation(1200.0, 149.0, p), "T-5: an activation that leaves net cash above zero withheld")
    q = [p]
    stw.expire(6, q)
    check(not q and stw.c["passes_expired"] == 1, "T-5: a pass waiting for cash not lost under exp_30")


def t7() -> None:
    """T-7: 9.2's oracles, each shown to fire on a hand-broken case."""
    from extended import cl_reading as CL

    good = LP.zero_counts()
    good.update(cash_closes=[0.0, 1.0], fees_subscription=SUB * 3, fees_activation=ACT)
    cases = [("b2f1", {"reactivation_ordinals": [2], "reactivations": 1, "reactivation_fees": FEE}),
             ("b2f1", {"reactivations": 1, "reactivation_fees": FEE + 1}),
             ("b2f2", {"same_day_bought_and_breached": 1}),
             ("b2f1", {"max_funded_live": CAP + 1}),
             ("inv7_bank_none", {"max_running": CAP + 3}),
             ("inv5_bank_30", {"queue_waits": [EXP_D + 1]}),
             ("house_zero_none", {"house_closes_not_ahead": 1}),
             ("house_stop_none", {"house_purchases_after_trigger": 1}),
             ("naf", {"fees_activation": 1.0, "fees_subscription": NAF_SUB * 2}),
             ("naf", {"fees_subscription": NAF_SUB * 2 + 1}),
             ("inv5_hold_none", {"fees_by_kind_problem": True})]
    for cell, broken in cases:
        lv = CL.cell_levers(cell, CAP)
        ok_run = {"counts": {0: dict(good, **({"fees_subscription": NAF_SUB * 2, "fees_activation": 0.0}
                                              if cell == "naf" else {}))}, "outs": [], "levers": lv}
        check(not CL.replay_oracle_problems(cell, ok_run, None), f"T-7: {cell}'s oracles fire on a good case")
        bad_run = {"counts": {0: dict(ok_run["counts"][0], **broken)}, "outs": [], "levers": lv}
        check(bool(CL.replay_oracle_problems(cell, bad_run, None)), f"T-7: {cell}'s oracle misses {broken}")
    # house money ahead wherever its base is
    rec = lambda nets: {"start_day": 0, "net_month": nets}  # noqa: E731
    lv = CL.cell_levers("house_stop_none", CAP)
    r = {"counts": {0: good}, "outs": [{"rec": rec([1.0, -1.0])}], "levers": lv}
    b = {"outs": [{"rec": rec([1.0, 2.0])}]}
    check(bool(CL.replay_oracle_problems("house_stop_none", r, b)), "T-7: not ahead where the base is, unseen")
    # the gate's: the pass rate per evaluation and the budget
    t = CL.CLGateTally(None)
    t.passes = [90, 100]
    check(refused(lambda: CL.gate_oracle_rows({"design": "toy", "cell": "b2f1"}, True, t), CL.Refused),
          "T-7: a pass rate of 0.9 per evaluation passes the oracle")
    t2_ = CL.CLGateTally(None)
    t2_.budget_over = 1
    check(refused(lambda: CL.gate_oracle_rows({"design": "toy", "cell": "b2f1"}, False, t2_), CL.Refused),
          "T-7: a budget exceeded passes the oracle")


def t10() -> None:
    """T-10: the counters channel -- every replay output, gate row and path record equal with it off and on, at one
    worker and at two; the counts the path's own; in ref every lever count zero."""
    from extended import user_beside as B

    job = toy_job()
    starts = [0, 9, 21, 42]
    for workers in (1, 2):
        a = B.run_starts("toy", "point", B.BY_NAME["off"], job, starts, workers, chunk=2)
        sink = LP.LeverSink()
        b = B.run_starts("toy", "point", B.BY_NAME["off"], job, starts, workers, chunk=2,
                         levers=LP.Levers(counters=True), lever_sink=sink)
        c = B.run_starts("toy", "point", B.BY_NAME["off"], job, starts, workers, chunk=2, levers=LP.Levers())
        check(outs_diff(a, b) is None and outs_diff(a, c) is None, f"T-10: the replay differs with the counters on "
              f"({workers} workers): {outs_diff(a, b)} {outs_diff(a, c)}")
        tot = {k: sum(float(v.get(k, 0) or 0) for v in sink.starts("toy", "point", "off").values())
               for k in LP.LEVER_KEYS}
        check(not any(tot.values()), f"T-10: a lever count nonzero in ref ({workers} workers)")
        check(sorted(sink.starts("toy", "point", "off")) == starts, "T-10: the counts are not one a start")
    # the counts are the path's own (the day recorder's fees, the engine's totals)
    lp, cnt = run(b2f(1), record_days=True)
    days = lp.campaign_days
    check(abs(cnt["fees_subscription"] - sum(d["fee_subscription"] for d in days)) < 1e-6 and
          abs(cnt["fees_activation"] - sum(d["fee_activation"] for d in days)) < 1e-6, "T-10: the fees by kind are "
          "not the day recorder's")
    check(abs(cnt["fees_subscription"] + cnt["fees_activation"] + cnt["reactivation_fees"] - lp.path.total_fees) < 1e-6,
          "T-10: the fees by kind do not sum to the engine's total")
    check(cnt["max_trades_one_session"] == max(lp.path.trades_by_day), "T-10: the most trades in a session")
    # the gate: rows and paths equal with the counters on and off, at one worker and two
    import gate_identity as GI

    from extended import gate as XG

    blocks = GI.syn_blocks()
    for workers in (1, 2):
        kw = GI.syn_kwargs()
        got = []

        def hook(shift, p, paths):
            got.extend(getattr(x, "lever_counts", None) for x in paths)
            return {}

        if workers == 1:
            a, _ = XG.run_gate(blocks, workers=1, **kw)
            b, _ = XG.run_gate(blocks, workers=1, levers=LP.Levers(counters=True), path_hook=hook, **GI.syn_kwargs())
        else:
            ra, (a, _) = GI.at_two_workers(lambda: XG.run_gate(blocks, workers=2, **kw), "T-10 gate off")
            rb, (b, _) = GI.at_two_workers(lambda: XG.run_gate(blocks, workers=2, levers=LP.Levers(counters=True),
                                                               path_hook=hook, **GI.syn_kwargs()), "T-10 gate on")
            if not (ra and rb):
                notes.append("NOT CHECKED (not a pass): T-10's gate at two workers -- the memory guard fell back")
        cols = [c for c in a.columns]
        d = diff(a[cols].to_dict("list"), b[cols].to_dict("list"))
        check(d is None, f"T-10: the gate's rows differ with the counters on ({workers} workers): {d}")
        check(all(isinstance(x, dict) and not any(x.get(k) for k in LP.LEVER_KEYS) for x in got) and got,
              f"T-10: the gate's paths do not carry zero lever counts ({workers} workers)")
        check(set(b.columns) - set(a.columns) == {"levers"}, "T-10: the gate names the levers only when given")


def t13() -> None:
    """T-13: A-4 -- in naf every evaluation fee $95 a cycle and every activation $0, in the replay and the gate;
    nothing else changes; with Standard's prices given it equals the base."""
    from extended import cl_reading as CL
    from extended import user_beside as B

    job = toy_job()
    starts = [0, 30]
    lv = CL.cell_levers("naf", CAP)
    check(lv.subscription == NAF_SUB and lv.activation == NAF_ACT, "T-13: the prices are not the record's")
    sink = LP.LeverSink()
    o = B.run_starts("toy", "point", B.BY_NAME["off"], job, starts, 1, levers=lv, lever_sink=sink)
    for s, c in sink.starts("toy", "point", "off").items():
        k = c["fees_subscription"] / NAF_SUB
        check(abs(k - round(k)) < 1e-9 and c["fees_activation"] == 0.0, f"T-13: start {s}: a fee not at naf's price")
    std = LP.Levers(subscription=SUB, activation=ACT)
    a = B.run_starts("toy", "point", B.BY_NAME["off"], job, starts, 1)
    b = B.run_starts("toy", "point", B.BY_NAME["off"], job, starts, 1, levers=std)
    check(outs_diff(a, b) is None, "T-13: Standard's prices given differ from the base")
    passes = [len(x["rec"]["pass_days"]) for x in o]
    passes0 = [len(x["rec"]["pass_days"]) for x in a]
    check(passes == passes0, "T-13: naf changed the passes (only the fees may change, the bankroll unbound)")
    import gate_identity as GI

    from extended import gate as XG

    blocks = GI.syn_blocks()
    a, _ = XG.run_gate(blocks, **GI.syn_kwargs())
    b, _ = XG.run_gate(blocks, subscription=SUB, activation=ACT, **GI.syn_kwargs())
    cols = list(a.columns)
    check(diff(a[cols].to_dict("list"), b[cols].to_dict("list")) is None, "T-13: the gate at Standard's prices differs")
    got = []
    XG.run_gate(blocks, subscription=NAF_SUB, activation=NAF_ACT, levers=LP.Levers(counters=True),
                path_hook=lambda s, p, paths: got.extend(x.lever_counts for x in paths) or {}, **GI.syn_kwargs())
    check(got and all(abs(c["fees_subscription"] / NAF_SUB - round(c["fees_subscription"] / NAF_SUB)) < 1e-9
                      and c["fees_activation"] == 0.0 for c in got), "T-13: the gate's naf fees")


def _before(rel: str) -> types.ModuleType:
    raw = subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE_COMMIT}:{rel}"], capture_output=True, check=True).stdout
    src = raw.decode("utf-8").replace("\r\n", "\n")
    sha = hashlib.sha256(src.encode("utf-8")).hexdigest()
    if sha != BEFORE_SHA256[rel]:
        raise RuntimeError(f"{rel} at {BASE_COMMIT} hashes to {sha}, not the pinned {BEFORE_SHA256[rel]}")
    mod = types.ModuleType(rel.replace("/", "_").replace(".py", "_before_q119"))
    mod.__file__ = f"<{BASE_COMMIT}:{rel}>"
    sys.modules[mod.__name__] = mod
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod


def t15() -> None:
    """T-15: A-2 and A-3 absent -- every task, replay, output and gate row as before Q-119, bit for bit, on all of
    Q-17's responses; given, the Focused Trader models admitted with the vendored class; resets off on every cell."""
    import customer_journey as CJ

    from extended import cl_reading as CL
    from extended import user_beside as B

    old = _before("extended/user_beside.py")
    job = toy_job(n_days=120)
    starts = [0, 11, 33]
    calls: list = []
    real = CJ._pool_run

    def pool(tasks, fn, workers, what):
        calls.append([t for t in tasks])
        return real(tasks, fn, workers, what)

    CJ._pool_run = pool
    try:
        for resp in B.RESPONSES:
            calls.clear()
            a = old.run_starts("toy", "point", old.BY_NAME[resp.name], job, starts, 1)
            ta = calls[-1]
            calls.clear()
            b = B.run_starts("toy", "point", B.BY_NAME[resp.name], job, starts, 1)
            tb = calls[-1]
            check(outs_diff(a, b) is None, f"T-15: {resp.name}: the outputs differ from before Q-119")
            check(len(ta) == len(tb) and all(len(x) == len(y) for x, y in zip(ta, tb)), f"T-15: {resp.name}: the "
                  "tasks differ from before Q-119")
        ftp = B.BY_NAME["ftp_corrective_lost_3"]
        sink = LP.LeverSink()
        o = B.run_starts("toy", "point", ftp, job, starts, 1, levers=CL.cell_levers("b2f1", CAP), lever_sink=sink)
        check(len(o) == len(starts), "T-15: the Focused Trader models not admitted with the levers")
    finally:
        CJ._pool_run = real
    gold = _before("extended/gate.py")
    import gate_identity as GI

    from extended import gate as XG

    blocks = GI.syn_blocks()
    a, pa = gold.run_gate(blocks, **GI.syn_kwargs())
    b, pb = XG.run_gate(blocks, **GI.syn_kwargs())
    check(pa == pb and diff(a.to_dict("list"), b.to_dict("list")) is None, "T-15: the gate's rows differ from before")
    for cell in CL.NEW_CELLS:
        lv = CL.cell_levers(cell, CAP)
        check(refused(lambda: LP.levers_args({"path": {"reset_failed_combines": True}}, lv), LP.LeverRefused),
              f"T-15: {cell} runs with resets on")
    # the campaign with no levers is the vendored campaign
    from extended import campaign as XC

    kw = dict(edge=0.05, seed=5, initial_bankroll=5000.0, rules=RULES, horizon_days=80, n_paths=4,
              max_concurrent_accounts=CAP, require_verified_cap=False, payout_lag_days=3)
    s1, p1 = V.simulate_lockstep_campaign(PROTO, **kw)
    s2, p2 = XC.simulate_lockstep_campaign(PROTO, **kw)
    check(diff(p1, p2) is None, "T-15: the campaign without levers differs from the vendored one")
    s3, p3 = XC.simulate_lockstep_campaign(PROTO, levers=LP.Levers(), **kw)
    check(diff(p1, [x for x in p3]) is None, "T-15: the campaign with levers off differs from the vendored one")


def t3() -> None:
    """T-3: every early-block reading is byte-identical when every session from 2024-01-02 on is replaced (the toy's
    late block drawn again from the toy seed), at every horizon of section 5's table (the toy has one arm: the
    verdict arm's bound, a constant, is not in play)."""
    from extended import cl_reading as CL
    from propedge.outcomes.distribution import DayBlock

    def reading(job):
        runs = {}
        for cell in ("ref", "b2f1", "house_stop_none"):
            x = CL.replay_run(job, "toy", "point", cell, "off", list(range(len(job["blocks"]))), 1, record=False)
            runs[CL.run_key("toy", "point", cell)] = x
        rows = CL.reading_rows(runs, {}, set())
        t = pd.DataFrame([r for r in rows if r["block"] == "early"])
        return t.to_csv(index=False)

    job = toy_job(n_days=200, start="2023-07-03")
    first = reading(job)
    rng = np.random.default_rng([TOY_SEED, 4])
    late = [i for i, d in enumerate(job["dates"]) if d >= "2024-01-02"]
    check(len(late) > 30, "T-3: the toy has no late block")
    for i in late:
        k = int(rng.integers(1, 5))
        et = np.array([500.0 + 60.0 * j for j in range(k)])
        win = rng.random(k) < 0.3
        job["blocks"][i] = DayBlock(pnl=np.where(win, 1000.0, -500.0), risked=np.full(k, 500.0),
                                    exit_reasons=tuple("target" if w else "stop" for w in win), entry_t=et,
                                    exit_t=et + 30.0)
    second = reading(job)
    check(first == second, "T-3: an early-block reading changed when the late sessions were replaced")
    check(len(first.splitlines()) > 100, "T-3: the early block holds too few readings to test")


def t6() -> None:
    """T-6: 10.2 on RD-02's functions with this reading's seed -- the kept windows, the interval from 4 kept windows
    with a spread, the sign count, the zero-series rule, the MDD's formula, the honesty series' keys (the test's
    [seed, 0, ...] never the reading's [seed, 1, ...])."""
    from scipy import stats

    from extended import cl_reading as CL
    from extended import pp_reading as RD

    seed = CL.declared_seed(CL.HONESTY_ROLE, ROOT, strict=False)
    check(CL.declared_seed(CL.TOY_ROLE, ROOT, strict=False) == TOY_SEED, "T-6: the toy seed is not section 12's")
    w = RD.kept_windows(40, 5)
    check(w == [(0, 5), (10, 15), (20, 25), (30, 35)], f"T-6: the kept windows {w}")
    m = [1.0, 2.0, 3.0, 4.0]
    lo, hi = RD.t_interval(m)
    se = np.std(m, ddof=1) / 2.0
    t = stats.t.ppf(0.95, 3)
    check(abs(lo - (2.5 - t * se)) < 1e-12 and abs(hi - (2.5 + t * se)) < 1e-12, "T-6: the interval")
    check(RD.t_interval([1.0, 1.0, 1.0, 1.0]) is None and RD.t_interval([1.0, 2.0, 3.0]) is None,
          "T-6: an interval where none may be printed")
    check(RD.sign_count([1.0, 2.0, 3.0], [1.0, 1.0, 4.0]) == (1, 1, 1), "T-6: the sign count")
    check(RD.describe(np.zeros(50), 5) == "identical on these trades", "T-6: the zero-series rule")
    check(abs(RD.mdd(m) - (stats.t.ppf(0.95, 3) + stats.t.ppf(0.80, 3)) * se) < 1e-12, "T-6: the MDD's formula")
    a = RD.honesty_rng(seed, 2, 63, 8).random(3)
    b = np.random.default_rng([seed, 1, 2, 63, 8]).random(3)
    c = np.random.default_rng([seed, 0, 2, 63, 8]).random(3)
    check(np.array_equal(a, b) and not np.array_equal(a, c), "T-6: the honesty series' keys")


def _card(p: float, s1: float) -> dict:
    from extended import cl_reading as CL

    return {b: {"P": {"value": p}, "S1": {"value": s1}, "S3a": {"value": 0.0}, "S5a": {"value": 0.0}}
            for b, _ in CL.BLOCKS}


def t14() -> None:
    """T-14: the menu -- no P without its guard row; every house-money row labelled "gaming P (E-134 (2))" and never
    ordered on P; the frontier without the house-money cells and the version with them labelled; the flags
    mechanical."""
    from extended import cl_reading as CL
    from extended import pp_inputs as PI

    R = CL._row
    rows = []
    cells = ("ref", "b2f1", "inv5_bank_none", "inv5_bank_30", "house_stop_none", "naf")
    pdiff = {"b2f1": (0.02, 0.01, -0.01), "inv5_bank_none": (0.01, 0.01, 0.01), "inv5_bank_30": (-0.01, -0.01, -0.01),
             "house_stop_none": (0.05, 0.05, 0.05), "naf": (0.0, 0.0, 0.0)}
    for c in cells:
        for b in ("all", "early", "late"):
            k = dict(design="p14", arm="verdict", cell=c, mode="declared", response="off", block=b)
            rows.append(R(section="scorecard", part="card", **k, measure="card_P", stat="value", value=0.5))
            for g in CL.GUARD_COLUMNS:
                rows.append(R(section="guard", part="guard", **k, measure=g, stat="value", value=1.0))
            for g in CL.GATE_GUARD:
                rows.append(R(section="guard", part="guard", **k, measure=g, stat="gate", value=0.1))
            if c != "ref":
                i = ("all", "early", "late").index(b)
                rows.append(R(section="paired", part="paired", **k, base="ref", measure="P", stat="mean",
                              value=pdiff[c][i]))
                for g in CL.GUARD_COLUMNS:
                    rows.append(R(section="guard", part="guard", **k, base="ref", measure=g, stat="cell_less_base",
                                  value=pdiff[c][i]))
    reading = pd.DataFrame(rows, columns=list(PI.ROW_KEYS))
    menu = CL.menu_table(reading, (), set())
    by = {r["cell"]: r for _, r in menu.iterrows()}
    check(set(by) == set(cells), f"T-14: the menu's cells {sorted(by)}")
    check(list(menu["cell"]) == [c for c in ("ref", *CL.NEW_CELLS) if c in cells],
          "T-14: the menu is not in the grid's order (it may never be ordered on P)")
    check("gaming P (E-134 (2))" in by["house_stop_none"]["flags"] and not by["house_stop_none"]["ordered_on_P"],
          "T-14: the house-money row is not labelled gaming P")
    check("not stable across blocks" in by["b2f1"]["flags"], "T-14: the stability flag is not mechanical")
    check("not stable across blocks" not in by["inv5_bank_none"]["flags"], "T-14: a stable cell flagged")
    check("depends on the hold's expiry" in by["inv5_bank_30"]["flags"]
          and "depends on the hold's expiry" in by["inv5_bank_none"]["flags"], "T-14: the expiry flag")
    check("Focused Trader models not read" in by["naf"]["labels"]
          and "Focused Trader models not read" in by["house_stop_none"]["labels"], "T-14: the Focused Trader gap")
    check("first-order, the table fixed" in by["b2f1"]["labels"]
          and "bought before the 17:00 CT reopening" in by["b2f1"]["labels"], "T-14: the Back2Funded labels")
    bad = menu.drop(columns=[c for c in menu.columns if c.startswith("guard_net_m1")])
    check(refused(lambda: CL.check_menu(bad), CL.Refused), "T-14: a P printed without its guard row passes")
    bad2 = menu.copy()
    bad2.loc[bad2["cell"] == "house_stop_none", "flags"] = ""
    check(refused(lambda: CL.check_menu(bad2), CL.Refused), "T-14: a house-money row without its label passes")
    bad3 = menu.copy()
    bad3.loc[bad3["cell"] == "naf", "labels"] = "described, not carried"
    check(refused(lambda: CL.check_menu(bad3), CL.Refused), "T-14: a naf row without the gap passes")
    cards = {"ref": _card(0.5, 0.5), "b2f1": _card(0.55, 0.4), "house_stop_none": _card(0.9, 0.4)}
    key = dict(design="p14", arm="verdict", mode="declared", response="off")
    f0 = CL.frontier_rows(cards, key, with_house=False)
    f1 = CL.frontier_rows(cards, key, with_house=True)
    check({r["cell"] for r in f0} == {"ref", "b2f1"}, "T-14: the frontier holds a house-money cell")
    check({r["cell"] for r in f1} == set(cards) and all("gaming P (E-134 (2))" in r["note"] for r in f1),
          "T-14: the frontier with house money not labelled")
    check(any(r["value"] == 1.0 for r in f0 if r["cell"] == "b2f1")
          and not any(r["value"] == 1.0 for r in f1 if r["cell"] == "b2f1"), "T-14: the frontier's dominance")


SECTIONS = {"t1": t1, "t2": t2, "t3": t3, "t4": t4, "t5": t5, "t6": t6, "t7": t7, "t10": t10, "t13": t13, "t14": t14,
            "t15": t15}


def main() -> None:
    name = sys.argv[2]
    t0 = time.time()
    SECTIONS[name]()
    print(json.dumps({"section": name, "n_problems": len(problems), "problems": problems[:40], "notes": notes,
                      "seconds": round(time.time() - t0, 1)}))


if __name__ == "__main__":
    main()
