"""RD-01's engine tests on toy campaigns (`prereg/RD-01_firm_contracts.md` 14.3: T-1 to T-7, T-10, T-12 to T-15's engine
parts), run by `tests/test_rd01_engine.py` in a process of its own (the vendored tree goes on its `sys.path`). Synthetic
trades only -- no bar, no atlas: each toy trade is a walk's booking made by hand (a stop in ticks, a favourable
excursion, a stop or a flatten as its terminal exit; its outcome at each R of a quarter-R-like menu, its MAE, its exit
times), drawn from the declared seed 20261992 (section 12: the build's toy campaigns).

    python tests/rd01_synthetic.py <repository root>        # prints one JSON line last: {check: value}

Every check is computed here against an oracle written from the declaration's words, independently of the adapter's
code; the test file asserts each.
"""
from __future__ import annotations

import dataclasses
import json
import sys
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(sys.argv[1])
for _p in (str(REPO), str(REPO / "identity")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from extended import use_vendored_stage2  # noqa: E402

use_vendored_stage2()
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import user_beside_identity as I  # noqa: E402

from extended import firm_accounts as A  # noqa: E402
from extended import firm_counts as C  # noqa: E402
from extended import firm_terms as T  # noqa: E402
from extended import firms as F  # noqa: E402
from extended import user_beside as B  # noqa: E402
from extended import walker as W  # noqa: E402
from propedge.campaign.lockstep import ConductModel, FundedAccount, CombineAccount  # noqa: E402
from propedge.campaign.payout_method import payout_method_terms  # noqa: E402
from propedge.campaign.protocols import Protocol  # noqa: E402
from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy, Tiers  # noqa: E402
from propedge.campaign.sizing import CURRENT_TIER, MICROS_PER_MINI, SizingRule  # noqa: E402
from propedge.contract.adapter import rules_from_ledger  # noqa: E402
from propedge.contract.payout_timing import REQUEST_4_TO_5PM  # noqa: E402
from propedge.contract.rules import load_rules  # noqa: E402
from propedge.outcomes.distribution import DayBlock  # noqa: E402

SEED = 20261992
RS = (1.0, 1.5, 2.0, 2.5, 3.0)
TV = 0.5
LOG_FEE = 1.22
LOG_MICROS = 4
N_DAYS = 200
QUIET = range(110, 136)                       # a spell of sessions with no trade: DayTraders' inactivity reaches
EPS = 1e-9
out: dict[str, Any] = {}
t_all = time.time()


# ------------------------------------------------------------------------------------------------ toy trades


def _trade(rng: np.random.Generator, entry: int, bias: float, fee: float, flat: int, zero: bool = False
           ) -> dict[str, Any]:
    """One toy trade. `zero`: P(the excursion reaches x stops) = 1 / (1 + x) and every other exit a stop -- zero edge
    at every R before costs (9.2's twin)."""
    S = int(rng.choice([40, 60, 80]))
    c = (TV + fee) / (S * TV)                                        # one entry tick and the fee, in R
    if zero:
        mfe = float(S * (1.0 / max(rng.random(), 1e-12) - 1.0))
        stop = True
    else:
        mfe = float(rng.exponential(S * bias))
        stop = bool(rng.random() < 0.6)
    p = int(np.floor(mfe * rng.uniform(0.0, 0.9)))
    term_u = -1.0 - (TV + fee + TV) / (S * TV) if stop else (p - 2) / S - c
    term_t = int(min(entry + int(rng.integers(5, 240)), flat)) if stop else flat
    r_by, mae_by, ex_by = {}, {}, {}
    for R in RS:
        tt = W.target_ticks(R, S)
        if mfe >= tt:
            r_by[R] = tt / S - c
            ex_by[R] = float(entry + 1 + int((term_t - entry - 1) * min(1.0, tt / max(mfe, 1.0))))
            mae_by[R] = float(rng.uniform(0.0, 0.8))
        else:
            r_by[R] = term_u
            ex_by[R] = float(term_t)
            mae_by[R] = float(max(rng.uniform(0.0, 0.8), -term_u))
    return {"S": S, "entry": int(entry), "r": r_by, "mae": mae_by, "ex": ex_by}


def toy_blocks(seed: int = SEED, n: int = N_DAYS, bias: float = 2.0, fee: float = LOG_FEE, quiet=QUIET,
               extra: dict[int, list[dict]] | None = None, zero: bool = False) -> tuple[list[DayBlock], list[str]]:
    rng = np.random.default_rng(seed)
    days = [d.date().isoformat() for d in pd.bdate_range("2024-01-02", periods=n)]
    blocks = []
    flat = W.C_FLAT - 2
    for i in range(n):
        k = 0 if i in quiet else int(rng.integers(0, 4))
        trades = [_trade(rng, W.bar_of(8, 40) + 50 * j, bias, fee, flat, zero) for j in range(k)]
        trades += (extra or {}).get(i, [])
        blocks.append(_block(sorted(trades, key=lambda t: t["entry"]), fee))
    return blocks, days


def _block(trades: list[dict], fee: float) -> DayBlock:
    n = len(trades)
    if n == 0:
        z = np.zeros(0)
        return DayBlock(pnl=z, risked=z, exit_reasons=(), risk_per_contract=z, mae=z, entry_t=z, exit_t=z,
                        r_by_rr={R: z for R in RS}, mae_by_rr={R: z for R in RS}, fee=z, sides=z,
                        exit_by_rr={R: z for R in RS})
    entries = [t["entry"] for t in trades]
    S = np.array([t["S"] for t in trades], float)
    risked = S * TV * LOG_MICROS
    r_by = {R: np.array([t["r"][R] for t in trades]) for R in RS}
    mae_by = {R: np.array([t["mae"][R] for t in trades]) for R in RS}
    ex_by = {R: np.array([t["ex"][R] for t in trades]) for R in RS}
    return DayBlock(pnl=r_by[2.0] * risked, risked=risked, exit_reasons=tuple("x" for _ in trades),
                    risk_per_contract=S * TV, mae=mae_by[2.0] * risked, entry_t=np.array(entries, float),
                    exit_t=ex_by[2.0], r_by_rr=r_by, mae_by_rr=mae_by, fee=np.full(n, fee), sides=np.ones(n),
                    exit_by_rr=ex_by)


def toy_policy(combine_risk: float = 300.0, funded_risk: float = 300.0, request_day_trades: bool = True) -> RiskPolicy:
    comb = Tiers("balance", ((-1e9, Leaf("combine base", combine_risk, 2.0)), (3000.0, Leaf("combine top", 150.0, 2.0))))
    rd = Leaf("request day", funded_risk, 1.5) if request_day_trades else Leaf("request day", funded_risk, 1.5,
                                                                                max_trades=0)
    fund = Tiers("request_day", ((0.0, Leaf("funded", funded_risk, 2.0)), (1.0, rd)))
    return RiskPolicy(id="rd01_toy", root=Phase(combine=comb, funded=fund))


RULES = rules_from_ledger()
LAG = int(payout_method_terms("aeropay", ledger=load_rules()).lag_days)
SIZING = dataclasses.replace(SizingRule.from_ledger(CURRENT_TIER), fee_schedule=T.fee_schedule("TS"))
PROTO = Protocol(name="rd01_toy", combine_rr=2.0, combine_risk=300.0, funded_rr=2.0, funded_risk=300.0,
                 trades_per_day=4, max_concurrent_accounts=5)


def toy_args(policy: RiskPolicy | None = None, **path_kw: Any) -> dict[str, Any]:
    path = dict(edge=0.0, rules=RULES, initial_bankroll=1e9, max_concurrent_accounts=5,
                subscription=float(RULES.subscription), billing_days=int(RULES.billing_days),
                activation=float(RULES.activation), payout_lag_days=LAG, max_concurrent_combines=5,
                max_total_accounts=5, conduct=ConductModel(rtp=False, enforcement_p=0.0), combine_max_days=2000,
                funded_horizon_days=100_000, purchase_budget=(20, 21), risk_policy=policy or toy_policy())
    path.update(path_kw)
    return {"draws": {"protocol": PROTO, "mode": "rotation", "flip": None, "sizing": SIZING},
            "path": path, "seed": B.SEED_BLOCK[1]}


def replay(blocks, args, seed: int = SEED, **extra):
    a = {**args, "path": {**args["path"], **extra}}
    return B.replay(blocks, a, seed)


def plain(lp: Any) -> Any:
    return dataclasses.asdict(lp)


def diff(a: Any, b: Any) -> str | None:
    return I.first_difference(plain(a), plain(b))


# ------------------------------------------------------------------------------------------------ traced classes

TRACED: list[Any] = []


def traced(cls: type) -> type:
    """A test subclass recording, at each close, the fields the oracles read."""

    def trade_day(self, *a, **k):
        is_f = isinstance(self, FundedAccount)
        b0 = float(self.B)
        r = cls.trade_day(self, *a, **k)
        day = a[4] if is_f else a[3]
        row = {"day": int(day), "B0": b0, "B": float(self.B), "F": float(self.F), "pnl": float(self.last_day_pnl),
               "trades": int(self.trades), "days": int(self.days)}
        if is_f:
            row.update(net=r, win_days=int(self.win_days), since_pay=float(self.since_pay),
                       rdn=bool(self.request_day_next), lrd=bool(self.last_request_day), n_payouts=int(self.n_payouts),
                       last_request=float(self.last_request), w_best=float(self.w_best), w_profit=float(self.w_profit),
                       gross_paid=float(self.gross_paid), closed=bool(self.closed), ended_on=self.ended_on,
                       eligible=bool(self.last_eligible), q=getattr(self, "q", None),
                       true_wd=getattr(self, "_true_win_days", None), g_peak=getattr(self, "g_peak", None))
        else:
            row.update(passed=bool(self.passed), failed=bool(self.failed), best=float(self.best_day),
                       resolved=self.resolved_on, qd=getattr(self, "qualifying_days", None),
                       trade_days=getattr(self, "trade_days", None), abandoned=bool(self.abandoned))
        self.__dict__.setdefault("trace", []).append(row)
        return r

    def post(self):
        cls.__post_init__(self)
        self.__dict__["trace"] = []
        TRACED.append(self)

    return type(f"Traced{cls.__name__}", (cls,), {"trade_day": trade_day, "__post_init__": post,
                                                  "__module__": __name__})


def run_plan_direct(blocks, days, s: T.Settings, policy=None, start: int = 0, trace: bool = True, **extra):
    """One replay of the toy campaign under a plan's settings (A-1's arguments, the plan's classes with the start's
    calendar and no arm shift), the traced classes when asked."""
    args, kw = F.plan_args(toy_args(policy), s, blocks=blocks)
    c_cls, f_cls = F.start_classes(s, days, start, None)
    if f_cls is None:
        f_cls = kw.get("funded_account_cls")
    c_cls = c_cls or CombineAccount
    f_cls = f_cls or FundedAccount
    if trace:
        c_cls, f_cls = traced(c_cls), traced(f_cls)
    TRACED.clear()
    A.TALLY.clear()
    path = {**args["path"], "combine_account_cls": c_cls, "funded_account_cls": f_cls, "record_days": True,
            "record_trades": True, **extra}
    if "household_closure" in kw:
        path["household_closure"] = kw["household_closure"]
    lp = B.replay(blocks[start:], {**args, "path": path}, SEED)
    accts = list(TRACED)
    return lp, accts, args


blocks, days = toy_blocks()
rich_blocks, _ = toy_blocks(seed=SEED, bias=2.6, quiet=())      # a richer edge, no quiet spell
dates = [date.fromisoformat(d) for d in days]

# ------------------------------------------------------------------------------------------------ T-1: the twins

t0 = time.time()
base = toy_args()
ref = replay(blocks, base, record_days=True, record_trades=True)
out["t1_base_paid"] = int(sum(f.n_payouts for f in ref.funded))
out["t1_base_passes"] = int(sum(c.passed for c in ref.combines))
twins = {}
for name, kind, cls in A.TWINS:
    key = "combine_account_cls" if kind == "combine" else "funded_account_cls"
    lp = replay(blocks, base, record_days=True, record_trades=True, **{key: cls})
    twins[name] = diff(ref, lp)
both = replay(blocks, base, record_days=True, record_trades=True, combine_account_cls=A.TWINS[2][2],
              funded_account_cls=A.TWINS[4][2])
twins["A-4+A-7"] = diff(ref, both)
out["t1_twins"] = twins
args_ts, kw_ts = F.plan_args(base, T.settings_for("TS", "reference"))
out["t1_ts_args_unchanged"] = bool(args_ts is base and kw_ts == {})
out["t1_seconds"] = round(time.time() - t0, 1)

# ------------------------------------------------------------------------------------------------ T-2: DayTraders

t0 = time.time()
DT_S = T.settings_for("DT", T.STRICT)
lp_dll, acc_dll, _ = run_plan_direct(blocks, days, DT_S, policy=toy_policy(combine_risk=1300.0, funded_risk=1300.0))
out["t2_dll_run"] = [sum(1 for a in acc_dll for r in a.trace if r["pnl"] <= -1250.0 + EPS),
                     min(r["pnl"] for a in acc_dll for r in a.trace),
                     sum(1 for a in acc_dll for i, r in enumerate(a.trace) if r["pnl"] <= -1250.0 + EPS
                         and i + 1 < len(a.trace) and not a.trace[i + 1].get("failed", False)
                         and not a.trace[i + 1].get("closed", False))]
lp_dt, acc_dt, args_dt = run_plan_direct(blocks, days, DT_S, policy=toy_policy(combine_risk=700.0, funded_risk=250.0))
dt_t = T.plan_terms("DT")
comb = [a for a in acc_dt if isinstance(a, CombineAccount)]
fund = [a for a in acc_dt if isinstance(a, FundedAccount)]
probs: list[str] = []
seen = {"qd_held": 0, "passes": 0, "dll_days": 0, "inactive_c": 0, "inactive_f": 0, "payouts": 0, "rounded": 0,
        "gate_or_share_held": 0, "rd_excluded": 0}


def inactive_oracle(trace: list[dict], anchor_date: date, cal: list[date], first_cal_day: int) -> int | None:
    """The first close at which a 30-day window from the anchor (or from the last $200 day) has ended, or will end
    before the next session, with no $200 day -- or None."""
    last = anchor_date - pd.Timedelta(days=1).to_pytimedelta()
    for row in trace:
        d = cal[row["day"] - 1]
        if row["pnl"] >= float(dt_t.qualifying_day_min) - EPS:
            last = d
        nxt = cal[row["day"]] if row["day"] < len(cal) else None
        if (d - last).days >= int(dt_t.inactivity_window_days) or (nxt is not None and (nxt - last).days > 30):
            return row["day"]
    return None


for c in comb:
    q = 0
    for row in c.trace:
        if row["failed"]:
            break
        if row["pnl"] <= -1250.0 + EPS:
            seen["dll_days"] += 1
        if row["pnl"] < -1250.0 - 1e-6:
            probs.append(f"evaluation {c.index}: a day lost {row['pnl']} past the soft limit")
        if row["pnl"] >= 200.0 - EPS and row["B"] > EPS and row["best"] <= 0.5 * row["B"] + EPS:
            q += 1
        target = max(3000.0, row["best"] / 0.5)
        if row["passed"] and (q < 2 or row["B"] < target - EPS):
            probs.append(f"evaluation {c.index}: passed with {q} Qualifying Days at day {row['day']}")
        if not row["passed"] and row["B"] >= target - EPS and q >= 2 and not row["abandoned"]:
            probs.append(f"evaluation {c.index}: not passed at day {row['day']} with the target and {q} days")
        if row["B"] >= target - EPS and q < 2:
            seen["qd_held"] += 1
        seen["passes"] += int(row["passed"])
    want = inactive_oracle(c.trace, (dates[c.purchase_day - 1] if c.purchase_day >= 1 else
                                     dates[0] - pd.Timedelta(days=1).to_pytimedelta()), dates, 0)
    got = c.trace[-1]["day"] if c.inactive_closed else None
    if not any(r["passed"] or r["failed"] for r in c.trace) and want != got:
        probs.append(f"evaluation {c.index}: inactivity closed at {got}, the oracle says {want}")
    seen["inactive_c"] += int(c.inactive_closed)
# the evaluation at target with days owed reads the table's top cell
top_rows = [r for r in lp_dt.trades if r["kind"] == "combine" and float(r["in_balance"]) >= 3000.0]
out["t2_top_cell_regimes"] = sorted({str(r["regime"]).split(" / ")[-1] for r in top_rows})
_, acc_rich, _ = run_plan_direct(rich_blocks, days, T.settings_for("DT", T.STRICT, flip="inact"),
                                 policy=toy_policy(combine_risk=700.0, funded_risk=250.0))
_, acc_small, _ = run_plan_direct(rich_blocks, days, T.settings_for("DT", T.STRICT, flip="inact"),
                                  policy=toy_policy(combine_risk=700.0, funded_risk=120.0))   # small days: held
fund_rich = [a for a in acc_rich + acc_small if isinstance(a, FundedAccount)]
for a in fund + fund_rich:
    q = 0
    for i, row in enumerate(a.trace):
        if row["closed"]:
            break
        if row["pnl"] < -1250.0 - 1e-6:
            probs.append(f"Pro {a.index}: a day lost {row['pnl']} past the soft limit")
        share = row["w_profit"] > EPS and row["w_best"] <= 0.3 * row["w_profit"] + EPS if row["net"] is None else None
        if row["lrd"]:
            seen["rd_excluded"] += 1
        if row["net"] is not None:
            r = row["last_request"]
            seen["payouts"] += 1
            bc = row["B"] + r
            if abs(r / 50.0 - round(r / 50.0)) > 1e-9 or r < 500.0 - EPS or r > 2000.0 + EPS:
                probs.append(f"Pro {a.index}: request {r} off its bounds")
            if bc - r < 2000.0 - EPS or bc < 2600.0 - EPS:
                probs.append(f"Pro {a.index}: request {r} from {bc} leaves less than $2,000 or under the $2,600 gate")
            if abs(row["net"] - r) > 1e-9:
                probs.append(f"Pro {a.index}: net {row['net']} is not 100 % of {r}")
            if abs(row["F"]) > 1e-9 or (i and abs(a.trace[i - 1]["F"]) > 1e-9):
                probs.append(f"Pro {a.index}: the floor is not at start around the payout ({row['F']})")
            want = min(0.5 * bc, 2000.0, bc - 2000.0)
            seen["rounded"] += int(r < want - EPS)
            q = 0
            if row["win_days"] != 0:
                probs.append(f"Pro {a.index}: win_days {row['win_days']} after a payout")
            continue
        if not row["lrd"] and row["pnl"] >= 200.0 - EPS and share:
            q += 1
        if row["q"] != q:
            probs.append(f"Pro {a.index}: q {row['q']} against the oracle's {q} at day {row['day']}")
            break
        held = q >= 8 and not (row["B"] >= 2600.0 - EPS and share)
        seen["gate_or_share_held"] += int(held)
        want_wd = 4 if held else min(5, max(0, q - 3))
        if row["win_days"] != want_wd:
            probs.append(f"Pro {a.index}: win_days {row['win_days']} against 4.9's {want_wd} at day {row['day']}")
            break
        if row["eligible"] != (q >= 8 and row["B"] >= 2600.0 - EPS and bool(share)):
            probs.append(f"Pro {a.index}: eligible {row['eligible']} against the oracle at day {row['day']}")
            break
    seen["inactive_f"] += int(a.inactive_closed)
    if a.inactive_closed:
        want = inactive_oracle(a.trace, dates[a.activation_day - 1], dates, 0)
        if want != a.trace[-1]["day"]:
            probs.append(f"Pro {a.index}: inactivity closed at {a.trace[-1]['day']}, the oracle says {want}")
out["t2_problems"] = probs[:10]
out["t2_seen"] = seen
out["t2_dll"] = sorted({c.dll for c in comb} | {a.dll for a in fund})
out["t2_rules"] = [args_dt["path"]["rules"].std_winning_days, args_dt["path"]["rules"].std_winning_day_min]
# the gate's translation: 21 sessions without a calendar
gate_cls = A.CLASSES[("DT", "combine", True)]
out["t2_gate_window"] = A.gate_window_sessions()
out["t2_gate_class_has_no_calendar"] = gate_cls.CALENDAR is None
# the recurring Pro fee's due sessions
due = F.pro_fee_days(lp_dt, 21, len(lp_dt.path.cash_series) - 1)
manual = sorted(f.activation_day + 1 + 21 * k for f in lp_dt.funded for k in range(1, 40)
                if f.activation_day + 1 + 21 * k <= (len(lp_dt.path.cash_series) - 1 if f.ended_on is None
                                                     else min(f.ended_on, len(lp_dt.path.cash_series) - 1)))
out["t2_pro_fee_days_ok"] = due == manual
out["t2_pro_fee_days_n"] = len(due)
out["t2_fee_basis"] = [list(F.plan_args(toy_args(), T.settings_for("DT", e))[0]["draws"]["sizing"].fee_schedule)
                       for e in (T.STRICT, T.LENIENT)]
out["t2_seconds"] = round(time.time() - t0, 1)

# ------------------------------------------------------------------------------------------------ T-3: Fast Pass

t0 = time.time()
fp_blocks = rich_blocks
res3 = {}
for paid in (False, True):
    s = dataclasses.replace(T.settings_for("FP", T.STRICT), fifth_paid=paid)
    lp, accts, args = run_plan_direct(fp_blocks, days, s)
    fund = [a for a in accts if isinstance(a, FundedAccount)]
    p3: list[str] = []
    forced = sum(a.forced_untraded for a in fund)
    rd_traded = 0
    redealt = 0
    led = list(lp.trades)
    for a in fund:
        best = 0.0
        for i, row in enumerate(a.trace):
            if row["closed"]:
                break
            best = max(best, row["pnl"])
            gross = (row["B"] + (row["last_request"] if row["net"] is not None else 0.0)) + \
                (row["gross_paid"] - (row["last_request"] if row["net"] is not None else 0.0))
            if row["net"] is not None:
                if best > 0.45 * gross + EPS:
                    p3.append(f"funded {a.index}: paid with a best day {best} over 45 % of {gross}")
                if row["last_request"] > 1500.0 + EPS or abs(row["net"] - 0.8 * row["last_request"]) > 1e-9:
                    p3.append(f"funded {a.index}: request {row['last_request']} net {row['net']}")
            if row["lrd"]:                                       # the session after a request: no trade
                prev = a.trace[i - 1]["trades"] if i else 0
                if row["trades"] != prev:
                    rd_traded += 1
                others = [t for t in led if t["day"] == row["day"] and not (t["kind"] == "funded"
                                                                              and t["index"] == a.index)]
                redealt += int(bool(others))
        if a.n_payouts > int(T.plan_terms("FP").fifth_request) - (0 if paid else 1):
            p3.append(f"funded {a.index}: {a.n_payouts} payouts at the {'paid' if paid else 'unpaid'} end")
    ended = [a for a in fund if a.fifth_ended]
    res3["paid" if paid else "unpaid"] = {
        "problems": p3[:8], "forced": int(forced), "request_days_traded": rd_traded, "redealt": redealt,
        "fifth_ended": len(ended), "fifth_payouts": sorted({a.n_payouts for a in ended}),
        "fifth_unpaid": int(sum(a.fifth_unpaid for a in fund)),
        "ladder": [list(args["draws"]["sizing"].ladder.thresholds), list(args["draws"]["sizing"].ladder.minis)],
        "held": int(sum(a.sessions_held for a in fund)), "share_blocked": int(sum(a.share_blocked for a in fund))}
out["t3"] = res3
out["t3_seconds"] = round(time.time() - t0, 1)

# ------------------------------------------------------------------------------------------------ T-4: Quick Pay


@dataclass
class Pol:
    trades_per_day: int = 1
    stop_day_on_win: bool = False
    stop_day_on_loss: bool = False
    payout_path: str = "standard"
    payout_frac: float = 1.0
    keep_balance: float = 0.0


class Stub:
    settlement = "pessimistic"

    def __init__(self, pnls):
        self.pnls = list(pnls)
        self.last_trade = None

    def __call__(self, n, day, slot, cushion, **kw):
        return np.array([self.pnls.pop(0) if self.pnls else np.nan])


QP_RULES = F.plan_rules(RULES, T.settings_for("QP", T.STRICT))


def qp(attrs: dict, pnls, B0: float = 0.0, **kw):
    cls = type("QPProbe", (A.QuickPayFunded,), {"INTRADAY": False, **attrs, "__module__": __name__})
    a = cls(index=0, activation_day=0, draw=Stub(pnls), horizon_days=10**6, floor_start=QP_RULES.xfa_mll_start,
            payout_timing=REQUEST_4_TO_5PM)
    a.B = float(B0)
    a.g_peak = float(B0)
    return a


t4: dict[str, Any] = {}
a = qp({}, [500.0])
net = a.trade_day(QP_RULES, Pol(payout_frac=0.0), 2000.0, 0, 1)
t4["floor_at_500"] = [a.B, a.F, net]
a = qp({}, [500.0])
net = a.trade_day(QP_RULES, Pol(payout_frac=2.0), 2000.0, 0, 1)
t4["after_500_payout"] = [a.B, a.F, net, a.last_request]
a = qp({}, [1000.0], B0=5000.0)
net = a.trade_day(QP_RULES, Pol(), 3000.0, 0, 1)
t4["split_6000_3000"] = [net, a.split_crossing]
for end in (T.STRICT, T.LENIENT):
    a = qp({"CEILING": end}, [1000.0], B0=9500.0)
    net = a.trade_day(QP_RULES, Pol(), 2000.0, 0, 1)
    t4[f"ceiling_{end}"] = [net, a.B, a.ended_on, a.ceiling_forfeit, a.n_payouts, a.cash]
# the cadence reading: five days of $150 since the last request, every session counted, none excluded
a = qp({"REQUEST": "cadence"}, [200.0] * 6)
nets = [a.trade_day(QP_RULES, Pol(), 2000.0, d, d + 1) for d in range(6)]
t4["cadence"] = [n is not None for n in nets] + [a.request_day_next]
a = qp({"REQUEST": "every"}, [200.0] * 3)
nets = [a.trade_day(QP_RULES, Pol(), 2000.0, d, d + 1) for d in range(3)]
t4["every"] = [n is not None for n in nets] + [a.win_days]

# 5.4's bounds on hand-built trades (S = 40 ticks, 5 micros: risk $100; the log's fee $1.22)
S4, N4, FEE4 = 40, 5, 1.22
c4 = (TV + FEE4) / (S4 * TV)
won = {R: W.target_ticks(R, S4) / S4 - c4 for R in RS}
flat_u = (30 - 2) / S4 - c4                                         # a profitable flatten at 30 ticks
stop_u = -1.0 - (TV + FEE4 + TV) / (S4 * TV)
cases = {"won_at_2": {1.0: won[1.0], 1.5: won[1.5], 2.0: won[2.0], 2.5: stop_u, 3.0: stop_u},
         "lo_1_flatten": {1.0: won[1.0], 1.5: flat_u, 2.0: flat_u, 2.5: flat_u, 3.0: flat_u},
         "none": {1.0: stop_u, 1.5: stop_u, 2.0: stop_u, 2.5: stop_u, 3.0: stop_u}}
t4["brackets"] = {k: A.peak_bracket(v, 2.0, S4, FEE4) for k, v in cases.items()}


class Inner:
    def __init__(self, by):
        self._fee = [np.array([FEE4])]
        self._r_by_rr = [{R: np.array([u]) for R, u in by.items()}]


peaks = {}
for k, by in cases.items():
    for peak in ("pess", "opt"):
        a = qp({"INTRADAY": True, "PEAK": peak}, [], B0=1000.0)
        a.F = -1000.0
        u = by[2.0]
        lt = {"historical_day": 0, "trade_index": 0, "realised_risk": N4 * S4 * TV, "contracts": N4,
              "risk_per_contract": S4 * TV, "rr": 2.0, "mae": 0.5 * N4 * S4 * TV}
        got = a._through_trade(u * N4 * S4 * TV, lt, Inner(by))
        peaks[f"{k}_{peak}"] = [round(a.g_peak - 1000.0, 9), round(a.F, 9), round(got, 9)]
t4["peaks"] = peaks
# a peak that raises the floor above the trade's later low: ended at the raised floor
a = qp({"INTRADAY": True, "PEAK": "pess"}, [], B0=50.0)        # $1,800 paid: the floor at -$150 before the trade
a.gross_paid, a.g_peak, a.F = 1800.0, 1850.0, -150.0
lt = {"historical_day": 0, "trade_index": 0, "realised_risk": N4 * S4 * TV, "contracts": N4,
      "risk_per_contract": S4 * TV, "rr": 2.0, "mae": 0.5 * N4 * S4 * TV}
got = a._through_trade(stop_u * N4 * S4 * TV, lt, Inner(cases["lo_1_flatten"] | {2.0: stop_u}))
t4["raised_floor_breach"] = [round(got, 9), round(a.F, 9), a.breaches_at_raised_floor, round(stop_u * N4 * S4 * TV, 9)]
t4["won_at"] = [A.won_at(won[2.0], 2.0, S4, FEE4), A.won_at(won[2.0] + 1.0 / S4, 2.0, S4, FEE4),
                A.won_at(won[2.0] - 1.0 / S4, 2.0, S4, FEE4)]
try:
    A.won_at(won[2.0] + 0.5, 2.0, S4, FEE4)
    t4["won_at_refuses_above"] = False
except ValueError:
    t4["won_at_refuses_above"] = True
out["t4"] = t4

# Quick Pay on the toy campaign: the floor oracle (9.2) and the table's inputs
qp_res = {}
for req in ("every", "cadence"):
    s = dataclasses.replace(T.settings_for("QP", T.STRICT), request=req)
    lp, accts, args = run_plan_direct(blocks, days, s)
    fund = [a for a in accts if isinstance(a, FundedAccount)]
    p4: list[str] = []
    for a in fund:
        g_close_peak = 0.0
        for row in a.trace:
            if row["closed"]:
                break
            g = row["B"] + row["gross_paid"]
            g_close_peak = max(g_close_peak, g)
            eod = min(0.0, max(-2000.0, g_close_peak - 2000.0))
            if row["F"] < eod - 1e-9 or row["F"] > 1e-9:
                p4.append(f"QP {a.index}: floor {row['F']} under the end-of-day trailing floor {eod} or above start")
            if row["net"] is not None and row["last_request"] < 250.0 - EPS:
                p4.append(f"QP {a.index}: request {row['last_request']} under $250")
            if row["rdn"]:
                p4.append(f"QP {a.index}: a request day excluded")
            if req == "every" and row["win_days"] != (5 if row["days"] >= 1 else 0):
                p4.append(f"QP {a.index}: win_days {row['win_days']}")
    qp_res[req] = {"problems": p4[:8], "payouts": int(sum(a.n_payouts for a in fund)),
                   "rises": int(sum(a.floor_rises for a in fund)),
                   "tiers": [int(sum(getattr(a, k) for a in fund)) for k in ("split_low", "split_crossing",
                                                                            "split_high")]}
out["t4_runs"] = qp_res

# ------------------------------------------------------------------------------------------------ T-5: TradeDay days

t0 = time.time()
pol5 = toy_policy(combine_risk=900.0)
res5 = {}
for plan, d in (("FP", 3), ("FP", 7), ("QP", 5), ("QP", 7)):
    s = dataclasses.replace(T.settings_for(plan, T.STRICT), min_days=d)
    lp, accts, args = run_plan_direct(blocks, days, s, policy=pol5)
    comb = [a for a in accts if isinstance(a, CombineAccount)]
    p5: list[str] = []
    logging_two = 0
    one_micro = True
    redealt = 0
    led = list(lp.trades)
    t = T.plan_terms(plan)
    n_log_oracle = 0
    for c in comb:
        td, prev = 0, {"B": 0.0, "best": 0.0, "trades": 0}
        for row in c.trace:
            start_logging = (td < d and prev["B"] >= max(float(t.eval_target),
                                                          prev["best"] / float(t.eval_consistency)) - EPS)
            traded = row["trades"] > prev["trades"]
            td += int(traded)
            if row["trade_days"] != td:
                p5.append(f"{plan}{d} evaluation {c.index}: {row['trade_days']} trading days against {td}")
                break
            target = max(float(t.eval_target), row["best"] / float(t.eval_consistency))
            if row["passed"] and td < d:
                p5.append(f"{plan}{d} evaluation {c.index}: passed with {td} trading days")
            if not row["passed"] and not row["failed"] and row["B"] >= target - EPS and td >= d:
                p5.append(f"{plan}{d} evaluation {c.index}: not passed at day {row['day']} with the days and target")
            if start_logging:                                    # at target with days owed at the session's start
                n_log_oracle += 1
                rs = [x for x in led if x["kind"] == "combine" and x["index"] == c.index and x["day"] == row["day"]]
                logging_two += int(len(rs) > 1)
                one_micro = one_micro and all(int(x["contracts"]) == 1 for x in rs)
                n_sig = len(blocks[row["day"] - 1].pnl)
                others = [x for x in led if x["day"] == row["day"] and not (x["kind"] == "combine"
                                                                            and x["index"] == c.index)]
                redealt += int(len(rs) == 1 and n_sig > 1 and bool(others))
            prev = row
    res5[f"{plan}{d}"] = {"problems": p5[:6], "logging_oracle": n_log_oracle,
                          "logging_sessions": int(sum(c.logging_sessions for c in comb)),
                          "logging_trades": int(sum(c.logging_trades for c in comb)), "two_a_session": logging_two,
                          "one_micro": one_micro, "redealt": redealt,
                          "passes": int(sum(c.passed for c in lp.combines))}
out["t5"] = res5
out["t5_seconds"] = round(time.time() - t0, 1)

# ------------------------------------------------------------------------------------------------ T-6: A-10

t0 = time.time()
s_hi = T.settings_for("DT", T.STRICT)
s_lo = T.settings_for("DT", T.STRICT, flip="price")
lp_hi, _, _ = run_plan_direct(blocks, days, s_hi, trace=False)
lp_lo, _, _ = run_plan_direct(blocks, days, s_lo, trace=False)
out["t6_records_same"] = I.first_difference([dataclasses.asdict(x) for x in lp_hi.combines + lp_hi.funded],
                                            [dataclasses.asdict(x) for x in lp_lo.combines + lp_lo.funded])
rp = F.repriced(lp_lo, s_lo.price, s_hi.price, 21)
out["t6_cash_max_diff"] = float(np.max(np.abs(rp.path.cash_series - lp_hi.path.cash_series)))
out["t6_fields"] = {k: abs(float(getattr(rp.path, k)) - float(getattr(lp_hi.path, k))) for k in
                    ("final_cash", "total_fees", "max_drawdown", "max_drawdown_frac")}
out["t6_subscriptions"] = len(F.subscription_days(lp_hi, 21))
out["t6_never_binds"] = F.bankroll_never_binds(lp_hi)
out["t6_break_even"] = [F.break_even_price(lambda p: 100.0 - 2.0 * p, 40.0),
                        F.break_even_price(lambda p: 100.0 - 2.0 * p, 120.0),
                        F.break_even_price(lambda p: 100.0 - 2.0 * p, -500.0)]
out["t6_seconds"] = round(time.time() - t0, 1)

# ------------------------------------------------------------------------------------------------ T-7: 9.2's oracles

t0 = time.time()
zero_blocks, _ = toy_blocks(seed=SEED + 1, fee=0.0, quiet=(), zero=True)
oracle = {}
for plan in ("DT", "FP", "QP"):
    s = T.settings_for(plan, T.STRICT)
    gross, n_f, passes, n_c = [], 0, 0, 0
    fee_bad = 0
    for k in range(12):
        perm = np.random.default_rng(SEED + 100 + k).permutation(len(zero_blocks))
        bl = [zero_blocks[i] for i in perm]
        lp, _, args = run_plan_direct(bl, days, s, trace=False)
        rule = args["draws"]["sizing"]
        for f in lp.funded:
            gross.append(float(f.gross_paid))
        passes += sum(c.passed for c in lp.combines)
        n_c += len([c for c in lp.combines if c.resolved_on is not None])
        for r in lp.trades:
            if r.get("contracts") and abs(float(r.get("fee", -1.0)) - rule.fee_dollars(int(r["contracts"]))) > 1e-9:
                fee_bad += 1
    g = np.asarray(gross, float)
    se = float(g.std(ddof=1) / np.sqrt(len(g))) if len(g) > 1 else float("inf")
    pr = passes / max(n_c, 1)
    oracle[plan] = {"mean_gross": float(g.mean()) if len(g) else 0.0, "se": se, "n_funded": len(g),
                    "pass_rate": pr, "pass_se": float(np.sqrt(0.4 * 0.6 / max(n_c, 1))), "n_resolved": n_c,
                    "fee_bad": fee_bad}
out["t7"] = oracle
out["t7_seconds"] = round(time.time() - t0, 1)

# ------------------------------------------------------------------------------------------------ T-10, T-12, T-13

gkw = {"rules": RULES, "sizing": SIZING, "seed": 1}
out["t10_ts_unchanged"] = F.gate_args(gkw, T.settings_for("TS", "reference")) is gkw
g_dt = F.gate_args(gkw, T.settings_for("DT", T.STRICT))
out["t10_dt_seams"] = sorted(k for k in g_dt if k not in gkw)
out["t13_gate_has_no_tier1"] = not any("tier" in k for k in g_dt) and \
    not any("tier" in k for k in F.gate_args(gkw, T.settings_for("FP", T.STRICT)))

t12 = {}
for plan, end in (("TS", None), ("LU", None), ("DT", T.STRICT), ("DT", T.LENIENT), ("FP", None), ("QP", None)):
    sched = T.fee_schedule(plan, end)
    s = T.settings_for(plan, end or T.STRICT) if plan not in ("TS",) else T.settings_for("TS", "reference")
    a_, _ = F.plan_args(toy_args(), s)
    rule = a_["draws"]["sizing"]
    t12[f"{plan}{'' if end is None else '-' + end}"] = [list(rule.fee_schedule), rule.fee_dollars(26),
                                                        2 * sched[1] + 6 * sched[0]]
out["t12"] = t12
out["t12_micros_per_mini"] = MICROS_PER_MINI

# T-13: a hand-built trade open at 12:58 CT on an FOMC-minutes date at R >= 2 only
mins = sorted(d for d, k in C.tier1_days().items() if "fomc_minutes" in k and d >= dates[0] and d <= dates[-1])
i13 = dates.index(mins[0]) if mins else None
S13 = 40
open_t = {"S": S13, "entry": W.bar_of(12, 30),
          "r": {R: (W.target_ticks(R, S13) / S13 - (TV + LOG_FEE) / (S13 * TV)) if R <= 1.0 else
                (-1.0 - (2 * TV + LOG_FEE) / (S13 * TV)) for R in RS},
          "mae": {R: 0.3 if R <= 1.0 else 1.1 for R in RS},
          "ex": {R: float(W.bar_of(12, 50)) if R <= 1.0 else float(W.bar_of(13, 30)) for R in RS}}
b13, _ = toy_blocks(extra={i13: [open_t]} if i13 is not None else None)
st, n_st = C.tier1_blocks(b13, dates, "strict")
_, n_wk = C.tier1_blocks(b13, dates, "walked")
out["t13_minutes_day"] = None if i13 is None else str(mins[0])
out["t13_counts"] = [n_st, n_wk]
out["t13_untouched_same"] = all(x is y for x, y, d in zip(st, b13, dates) if d not in C.tier1_days())
lp13, _, a13 = run_plan_direct(st, days, T.settings_for("FP", T.STRICT), trace=False)
led13 = [{"account": (r["kind"], r["index"]), "day": r["day"],
          "entry": float(st[r["historical_day"]].entry_t[r["trade_index"]]), "contracts": int(r["contracts"]),
          "pnl": float(r["pnl"])} for r in lp13.trades if r.get("contracts")]
mg = C.martingale_steps(led13)


def brute_martingale(trades):
    """9.3's count, recomputed: per account, a trade at least twice its account's previous trade's micros when that
    trade closed at a loss."""
    n = 0
    last: dict = {}
    for t in sorted(trades, key=lambda x: (x["day"], x["entry"])):
        p = last.get(t["account"])
        if p is not None and p["pnl"] < 0 and t["contracts"] >= 2 * p["contracts"]:
            n += 1
        last[t["account"]] = t
    return n


out["t13_martingale"] = [mg["per_account"], brute_martingale(led13), mg["trades"], len(led13)]
out["t13_sessions"] = C.trades_a_session(led13)

# ------------------------------------------------------------------------------------------------ T-14: 4.9's fields

out["t14_rules"] = {p: [F.plan_args(toy_args(), T.settings_for(p, T.STRICT if p != "TS" else "reference"))[0]["path"]
                        ["rules"].std_winning_days,
                        F.plan_args(toy_args(), T.settings_for(p, T.STRICT if p != "TS" else "reference"))[0]["path"]
                        ["rules"].std_winning_day_min] for p in ("TS", "DT", "FP", "QP")}
s_fp = T.settings_for("FP", T.STRICT)
lp, accts, _ = run_plan_direct(blocks, days, s_fp)
p14: list[str] = []
for a in [x for x in accts if isinstance(x, FundedAccount)]:
    for row in a.trace:
        if row["closed"]:
            break
        if row["win_days"] not in (row["true_wd"], 4):
            p14.append(f"FP {a.index}: win_days {row['win_days']} is neither the engine's {row['true_wd']} nor 4")
        if row["net"] is not None and not row["rdn"] and a.FIFTH != "unpaid":
            p14.append(f"FP {a.index}: no request day after a request")
out["t14_fp_problems"] = p14[:6]
out["t14_fp_held"] = int(sum(a.sessions_held for a in accts if isinstance(a, FundedAccount)))

# ------------------------------------------------------------------------------------------------ T-15: A-9

job = {"engine": "single", "blocks": blocks, "dates": days, "args": toy_args()}
starts = [0, 7, 30]
direct = B.run_starts("syn", "point", B.BY_NAME["off"], job, starts, 1)
via = F.run_plan("syn", "point", B.BY_NAME["off"], job, T.settings_for("TS", "reference"), starts, {})
out["t15_ts_runner_same"] = I.first_difference(direct, [o for o, _ in via])
lu_args, lu_kw = F.plan_args(toy_args(), T.settings_for("LU", T.LENIENT))
lu_args_s, lu_kw_s = F.plan_args(toy_args(), T.settings_for("LU", T.STRICT), ladder=True)
out["t15_lu_keywords"] = [sorted(lu_kw), lu_kw.get("household_closure"), B.class_name(lu_kw["funded_account_cls"]),
                          sorted(lu_kw_s), lu_kw_s.get("seed_base")]
out["t15_lu_base_problems"] = B.base_problems(lu_args)
out["t15_lu_path"] = [lu_args["path"].get("payout_timing"), "funded_account_cls" in lu_args["path"],
                      "household_closure" in lu_args["path"]]
lu_job = {**job, "args": lu_args}
lu_out = F.run_plan("syn", "point", B.BY_NAME["off"], lu_job, T.settings_for("LU", T.LENIENT), [0, 30], lu_kw)
out["t15_lu_named"] = [(o.get("household_closure"), o.get("funded_account_cls")) for o, _ in lu_out]
lad = F.run_plan("syn", "point", B.BY_NAME["off"], job, T.settings_for("TS", "reference"), [0], {"seed_base": F.LADDER_SEED})
out["t15_ladder_seed"] = [lad[0][0].get("seed_base"), lad[0][0]["seed"] == B.start_seed(0, F.LADDER_SEED)]
dt_job = {**job, "args": F.plan_args(toy_args(), T.settings_for("DT", T.STRICT))[0]}
dt_kw = F.plan_args(toy_args(), T.settings_for("DT", T.STRICT))[1]
dt_out = F.run_plan("syn", "point", B.BY_NAME["off"], dt_job, T.settings_for("DT", T.STRICT), [0, 30], dt_kw)
out["t15_dt_runner"] = [o["funded_account_cls"] for o, _ in dt_out] + [len(c[0]) if c else 0 for _, c in dt_out]
out["seconds"] = round(time.time() - t_all, 1)
print(json.dumps(out, default=str))
