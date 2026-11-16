"""
propsim.py — Gate-1 contract engine for Topstep 50K (A0, 2026-09-12b, no-DLL instance).

Run model (per operator gate 1.8):
  * binary resolution at exactly the labelled $ risk (win = +R*r, loss = -r)
  * no MAE, no stop distance, no contract rounding, no size feasibility
  * commissions / slippage = 0 (edge parameter is the only drag)
  * balance is cumulative net P&L from 0; $50k is a display offset only

Edge convention: expected P&L per trade = edge * r  ->  p_win = (1 + edge) / (1 + R).
edge = 0 is exact break-even; negative edge models commission/slippage drag.

Day model: every account trades every trading day. A day consists of up to
`trades_per_day` binary trades, optionally stopping early on the first win/loss.
The 16:00 CT lock happens after the last trade of the day (ratchet, best-day,
pass/payout checks). Subscription is charged at the start of days 0, 21, 42, ...

All sims run in lockstep across a numpy array of N accounts.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

EPS = 1e-9


@dataclass
class Rules:
    # Combine
    profit_target: float = 3000.0
    mll: float = 2000.0
    consistency_max_day_frac: float = 0.55
    # XFA
    xfa_mll_start: float = -2000.0
    xfa_lock_at: float = 0.0
    std_winning_days: int = 5
    std_winning_day_min: float = 150.0
    std_cap: float = 2000.0
    cons_min_days: int = 3
    cons_max_day_frac: float = 0.4
    cons_cap: float = 3000.0
    payout_min: float = 125.0
    payout_max_frac_of_balance: float = 0.5
    profit_split: float = 0.9
    # Combine floor lock: official help center (Sep 2026) — "Once it reaches your starting
    # balance, it locks permanently" applies to the Combine as well as the XFA. None disables.
    combine_mll_lock_at: float | None = 0.0
    # Payout frictions not in A0 (third-party sources, Sep 2026): per-payout processing fee
    # (official page: none for Wise/Aeropay) and, on the Standard path, >$0 net profit since
    # the previous payout for second-and-later requests.
    payout_fee: float = 0.0
    require_profit_since_payout: bool = False
    # Fees
    subscription: float = 49.0
    billing_days: int = 21
    activation: float = 149.0
    reset_fee: float = 49.0
    b2f_fee: float = 599.0
    b2f_max: int = 2
    # What happens when chosen $ risk r exceeds the room c = B - F above the floor.
    #   "resize":   trader sizes down: risk c, target R*c, p_win unchanged (keeps R)
    #   "truncate": full-size trade liquidated at the floor: risk c, target R*r,
    #               p_win = (1+edge)*c/(c+R*r)  (Brownian barrier race, EV = edge*c)
    #   "none":     gate-1.8 no-MAE model; overshoots the floor and inflates P(pass)
    # "truncate" is the contract-faithful default: Topstep liquidates at the floor.
    floor_mode: str = "truncate"
    # How edge carries over when the floor is closer than the stop (truncate mode only):
    #   "drift":  edge is a drift-per-variance theta fixed by (r, W, e) at the trade's own
    #             stop/target; the floor is a closer exit on the same path (exact).
    #   "linear": EV at the floor = e * c  (first-order approximation of "drift").
    edge_mode: str = "drift"

    @property
    def liquidate_at_floor(self) -> bool:
        return self.floor_mode != "none"


@dataclass
class Policy:
    rr: float                     # reward multiple R
    risk: float                   # $ loss per trade r
    trades_per_day: int = 1
    stop_day_on_win: bool = False
    stop_day_on_loss: bool = False
    payout_path: str = "standard"  # "standard" | "consistency"
    payout_frac: float = 1.0       # fraction of max allowed request to take
    keep_balance: float = 0.0      # never request below this balance (0 = off; D-45). Delays the first payout until B >= keep + minimum

    def p_win(self, edge: float) -> float:
        p = (1.0 + edge) / (1.0 + self.rr)
        if not 0.0 < p < 1.0:
            raise ValueError(f"p_win={p} out of range for rr={self.rr}, edge={edge}")
        return p

    @property
    def label(self) -> str:
        s = f"{self.rr}:1 ${self.risk:.0f} {self.trades_per_day}/day"
        if self.stop_day_on_win:
            s += " stopW"
        if self.stop_day_on_loss:
            s += " stopL"
        return s


class RandomDraw:
    """Default outcome source: iid Bernoulli wins, mapped to $ P&L."""
    def __init__(self, policy: Policy, edge: float, rng: np.random.Generator,
                 floor_mode: str = "truncate", edge_mode: str = "drift"):
        self.p = policy.p_win(edge)
        self.edge = edge
        self.rr = policy.rr
        self.risk = policy.risk
        self.win = policy.rr * policy.risk
        self.rng = rng
        self.mode = floor_mode
        self.edge_mode = edge_mode
        self.theta = theta_from_edge(self.risk, self.win, edge) if edge_mode == "drift" else None

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray) -> np.ndarray:
        u = self.rng.random(n)
        if self.mode == "resize":
            c = np.minimum(self.risk, np.maximum(cushion, 0.0))
            return np.where(u < self.p, self.rr * c, -c)
        if self.mode == "truncate":
            c = np.minimum(self.risk, np.maximum(cushion, 0.0))
            if self.edge_mode == "drift":
                p = p_race(c, self.win, self.theta)
            else:
                p = np.clip((1.0 + self.edge) * c / (c + self.win), 0.0, 1.0)
            return np.where(u < p, self.win, -c)
        return np.where(u < self.p, self.win, -self.risk)


class ScriptedDraw:
    """Deterministic outcome source for golden-path tests (n must be 1).
    script: list of days; each day is a list of $ P&L per trade slot."""
    def __init__(self, script):
        self.script = script

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray) -> np.ndarray:
        assert n == 1
        try:
            return np.array([float(self.script[day][slot])])
        except IndexError:
            return np.array([np.nan])  # signals "no trade this slot"


def simulate_combine(rules: Rules, policy: Policy, edge: float, n: int,
                     rng: np.random.Generator | None = None, draw=None,
                     max_days: int = 2000) -> dict:
    rng = rng or np.random.default_rng()
    draw = draw or RandomDraw(policy, edge, rng, rules.floor_mode, rules.edge_mode)

    B = np.zeros(n)
    F = np.full(n, -rules.mll)
    best_day = np.zeros(n)
    alive = np.ones(n, bool)
    passed = np.zeros(n, bool)
    failed = np.zeros(n, bool)
    days = np.zeros(n, int)
    trades = np.zeros(n, int)
    sub_fees = np.zeros(n)
    pass_day = np.full(n, -1)
    fail_day = np.full(n, -1)

    for d in range(max_days):
        if not alive.any():
            break
        if d % rules.billing_days == 0:
            sub_fees[alive] += rules.subscription
        alive_at_start = alive.copy()
        active = alive.copy()
        day_pnl = np.zeros(n)
        for t in range(policy.trades_per_day):
            if not active.any():
                break
            cushion = B - F
            pnl = draw(n, d, t, cushion)
            if rules.liquidate_at_floor:
                pnl = np.maximum(pnl, -cushion)
            act = active & ~np.isnan(pnl)
            B[act] += pnl[act]
            day_pnl[act] += pnl[act]
            trades[act] += 1
            breach = act & (B <= F + EPS)
            failed |= breach
            fail_day[breach] = d
            alive &= ~breach
            active &= ~breach
            if policy.stop_day_on_win:
                active &= ~(act & (pnl > 0))
            if policy.stop_day_on_loss:
                active &= ~(act & (pnl < 0))
        # 16:00 CT lock
        days[alive_at_start] += 1
        best_day[alive] = np.maximum(best_day[alive], day_pnl[alive])
        newF = np.maximum(F[alive], B[alive] - rules.mll)
        if rules.combine_mll_lock_at is not None:
            newF = np.minimum(rules.combine_mll_lock_at, newF)
        F[alive] = newF
        target_eff = np.maximum(rules.profit_target, best_day / rules.consistency_max_day_frac)
        newpass = alive & (B >= target_eff - EPS)
        passed |= newpass
        pass_day[newpass] = d
        alive &= ~newpass

    return dict(
        passed=passed, failed=failed, unresolved=alive,
        days=days, trades=trades, sub_fees=sub_fees,
        pass_day=pass_day, fail_day=fail_day,
        B=B, F=F, best_day=best_day,
    )


def simulate_xfa(rules: Rules, policy: Policy, edge: float, n: int,
                 rng: np.random.Generator | None = None, draw=None,
                 horizon_days: int = 250, horizon_per_account=None) -> dict:
    rng = rng or np.random.default_rng()
    draw = draw or RandomDraw(policy, edge, rng, rules.floor_mode, rules.edge_mode)
    hz = np.full(n, horizon_days) if horizon_per_account is None else np.asarray(horizon_per_account)
    cap = rules.std_cap if policy.payout_path == "standard" else rules.cons_cap

    B = np.zeros(n)
    F = np.full(n, rules.xfa_mll_start)
    alive = np.ones(n, bool)
    closed = np.zeros(n, bool)
    days = np.zeros(n, int)
    trades = np.zeros(n, int)
    cash = np.zeros(n)            # net to trader (after split)
    gross_paid = np.zeros(n)      # total requests
    n_payouts = np.zeros(n, int)
    first_payout_day = np.full(n, -1)
    # payout window state
    win_days = np.zeros(n, int)
    win_days_total = np.zeros(n, int)
    w_days = np.zeros(n, int)
    w_profit = np.zeros(n)
    w_best = np.zeros(n)
    since_pay = np.zeros(n)        # net P&L since last payout
    paid_once = np.zeros(n, bool)

    for d in range(int(hz.max())):
        trading = alive & (d < hz)
        if not trading.any():
            break
        alive_at_start = trading.copy()
        active = trading.copy()
        day_pnl = np.zeros(n)
        for t in range(policy.trades_per_day):
            if not active.any():
                break
            cushion = B - F
            pnl = draw(n, d, t, cushion)
            if rules.liquidate_at_floor:
                pnl = np.maximum(pnl, -cushion)
            act = active & ~np.isnan(pnl)
            B[act] += pnl[act]
            day_pnl[act] += pnl[act]
            trades[act] += 1
            breach = act & (B <= F + EPS)
            closed |= breach
            alive &= ~breach
            active &= ~breach
            if policy.stop_day_on_win:
                active &= ~(act & (pnl > 0))
            if policy.stop_day_on_loss:
                active &= ~(act & (pnl < 0))
        # 16:00 CT lock (only accounts that traded today)
        days[alive_at_start] += 1
        lk = alive & alive_at_start
        F[lk] = np.minimum(rules.xfa_lock_at, np.maximum(F[lk], B[lk] - rules.mll))
        # window bookkeeping (completed day)
        w_days[lk] += 1
        w_profit[lk] += day_pnl[lk]
        w_best[lk] = np.maximum(w_best[lk], day_pnl[lk])
        since_pay[lk] += day_pnl[lk]
        wd = lk & (day_pnl >= rules.std_winning_day_min - EPS)
        win_days[wd] += 1
        win_days_total[wd] += 1
        # eligibility
        if policy.payout_path == "standard":
            elig = lk & (win_days >= rules.std_winning_days)
            if rules.require_profit_since_payout:
                elig &= ~paid_once | (since_pay > EPS)
        else:
            elig = lk & (w_days >= rules.cons_min_days) & (w_profit > 0) & \
                   (w_best <= rules.cons_max_day_frac * w_profit + EPS)
        allowed = np.minimum(rules.payout_max_frac_of_balance * B, cap)
        req = policy.payout_frac * allowed
        if policy.keep_balance > 0:
            req = np.minimum(req, np.maximum(B - policy.keep_balance, 0.0))
        do = elig & (req >= rules.payout_min - EPS)
        if do.any():
            q = req[do]
            B[do] -= q
            gross_paid[do] += q
            cash[do] += rules.profit_split * q - rules.payout_fee
            n_payouts[do] += 1
            since_pay[do] = 0.0
            paid_once[do] = True
            first = do & (first_payout_day < 0)
            first_payout_day[first] = d
            F[do] = rules.xfa_lock_at          # floor -> 0 outright on payout
            win_days[do] = 0
            w_days[do] = 0
            w_profit[do] = 0.0
            w_best[do] = 0.0

    return dict(
        closed=closed, alive=alive, days=days, trades=trades,
        cash=cash, gross_paid=gross_paid, n_payouts=n_payouts,
        first_payout_day=first_payout_day, B=B, F=F,
        win_days_total=win_days_total,
    )


def summarize_combine(res: dict) -> dict:
    n = len(res["passed"])
    pp = res["passed"].mean()
    return dict(
        p_pass=pp,
        p_pass_se=np.sqrt(pp * (1 - pp) / n),
        p_fail=res["failed"].mean(),
        p_unresolved=res["unresolved"].mean(),
        mean_days=res["days"].mean(),
        mean_days_pass=res["days"][res["passed"]].mean() if res["passed"].any() else np.nan,
        mean_days_fail=res["days"][res["failed"]].mean() if res["failed"].any() else np.nan,
        mean_trades=res["trades"].mean(),
        mean_sub_fees=res["sub_fees"].mean(),
        mean_B_final=res["B"].mean(),   # martingale check: ~0 at edge 0
    )


def summarize_xfa(res: dict) -> dict:
    fp = res["first_payout_day"]
    got = fp >= 0
    return dict(
        p_any_payout=got.mean(),
        mean_cash=res["cash"].mean(),
        mean_gross=res["gross_paid"].mean(),
        mean_n_payouts=res["n_payouts"].mean(),
        mean_days_to_first_payout=fp[got].mean() if got.any() else np.nan,
        p_closed=res["closed"].mean(),
        mean_days_alive=res["days"].mean(),
        mean_T=(res["B"] + res["gross_paid"]).mean(),  # Fatou check: <= 0 at edge 0
    )


def attempt_ev(comb: dict, xfa: dict, rules: Rules) -> dict:
    """Expected net cash per Combine attempt (one Combine -> maybe one XFA)."""
    ev = comb["p_pass"] * (xfa["mean_cash"] - rules.activation) - comb["mean_sub_fees"]
    cost = comb["mean_sub_fees"] + comb["p_pass"] * rules.activation
    return dict(ev_per_attempt=ev, cost_per_attempt=cost,
                extraction_ratio=(cost + ev) / cost if cost > 0 else np.nan)


def simulate_lifecycle(rules: Rules, policy: Policy, edge: float, n: int,
                       rng: np.random.Generator | None = None, total_days: int = 504) -> dict:
    """One continuous lifecycle: Combine then (if passed) XFA, within `total_days`
    trading days in total. Net = XFA cash - activation - Combine subscriptions."""
    rng = rng or np.random.default_rng()
    c = simulate_combine(rules, policy, edge, n, rng, max_days=total_days)
    passed = c["passed"]
    m = int(passed.sum())
    net = -c["sub_fees"].copy()
    cash = np.zeros(n); got = np.zeros(n, bool); npay = np.zeros(n, int)
    if m:
        hz = total_days - (c["pass_day"][passed] + 1)
        x = simulate_xfa(rules, policy, edge, m, rng, horizon_days=total_days, horizon_per_account=hz)
        cash[passed] = x["cash"]
        got[passed] = x["first_payout_day"] >= 0
        npay[passed] = x["n_payouts"]
        net[passed] += x["cash"] - rules.activation
    return dict(p_pass=passed.mean(), p_payout=got.mean(), mean_cash=cash.mean(),
                mean_net=net.mean(), p_net_pos=(net > 0).mean(),
                mean_sub_fees=c["sub_fees"].mean(), mean_n_payouts=npay.mean(),
                p_unresolved=c["unresolved"].mean(), net=net)


# ---------------------------------------------------------------------------
# Barrier probabilities with drift.  theta = 2*mu/sigma^2 (drift per unit variance).
# P(reach +b before -a from 0) = (1 - e^{-theta a}) / (1 - e^{-theta (a+b)}).
# theta is fixed by the edge definition at the trade's own stop/target:
#     p_race(r, W, theta) = (1 + e) / (1 + R)
# and the floor at -c (c < r) is then just a closer exit on the same path.
# ---------------------------------------------------------------------------

def p_race(a, b, theta: float):
    """P(reach +b before -a) for a path with drift-per-variance theta; a may be an array."""
    a = np.asarray(a, float)
    if abs(theta) < 1e-12:
        return a / (a + b)
    num = -np.expm1(-theta * a)
    den = -np.expm1(-theta * (a + b))
    return np.where(a <= 0, 0.0, num / den)


def theta_from_edge(r: float, W: float, edge: float) -> float:
    """Solve p_race(r, W, theta) = (1+edge)*r/(r+W) for theta (monotone; bisection)."""
    target = (1.0 + edge) * r / (r + W)
    if not 0.0 < target < 1.0:
        raise ValueError("edge out of range")
    if abs(edge) < 1e-12:
        return 0.0
    scale = 1.0 / (r + W)                       # theta is O(2e/W); start there
    lo, hi = (0.0, scale) if edge > 0 else (-scale, 0.0)
    # widen bracket until it contains the root
    f = lambda th: float(p_race(r, W, th)) - target
    while f(hi) < 0 and edge > 0:
        hi *= 2
    while f(lo) > 0 and edge < 0:
        lo *= 2
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------------
# Adverse-excursion law (reference for an MAE-reporting generator).
# For a driftless continuous martingale racing a stop at -r against a target
# at +W, the excursion of a *winning* trade satisfies
#     P(MAE >= c | win) = W (r - c) / (r (c + W)),   0 <= c <= r,
# with no free parameters. A losing trade has MAE = r. Liquidating whenever
# MAE >= room c reproduces the truncated win probability c / (c + W) exactly.
# With drift theta (edge_mode "drift"):
#     P(MAE >= c | win) = [1 - p_race(c, W, theta)] * p_race(r - c, W + c, theta) / p_race(r, W, theta)
# which reduces to the closed form above at theta = 0. Liquidating at MAE >= room
# reproduces p_race(c, W, theta) exactly in both cases.
# ---------------------------------------------------------------------------

def mae_survival_given_win(c, r, W, theta: float = 0.0):
    c = np.asarray(c, float)
    if abs(theta) < 1e-12:
        return W * (r - c) / (r * (c + W))
    return (1.0 - p_race(c, W, theta)) * p_race(r - c, W + c, theta) / float(p_race(r, W, theta))


def sample_mae_given_win(rng: np.random.Generator, n: int, r: float, W: float,
                         theta: float = 0.0) -> np.ndarray:
    """Inverse-transform sample of a winning trade's MAE. Closed form at theta = 0,
    vectorised bisection on the monotone survival function otherwise."""
    s = rng.random(n)                     # survival level ~ U(0,1)
    if abs(theta) < 1e-12:
        return W * r * (1.0 - s) / (s * r + W)
    lo, hi = np.zeros(n), np.full(n, float(r))
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        big = mae_survival_given_win(mid, r, W, theta) > s   # survival decreasing in c
        lo = np.where(big, mid, lo)
        hi = np.where(big, hi, mid)
    return 0.5 * (lo + hi)
