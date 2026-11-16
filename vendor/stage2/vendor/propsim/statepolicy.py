"""
statepolicy.py — Stage 3: state-dependent (R, $risk) policies.

A policy is a callable  act(state) -> (rr, risk)  where every field of `state` is a
numpy array over accounts and the returned rr / risk are arrays too.  risk = 0 means
"no trade this slot" (ends the account's day).  Zero edge only; truncate floor mode.

state fields (all arrays):
  B          cumulative balance          F          current floor
  room       B - F                       day_pnl    today's P&L so far
  slot       trade index within the day  day        trading-day index
  best_day   (Combine) best completed day
  target     (Combine) current effective target = max(3000, best_day/0.55)
  win_days   (XFA) winning days in the current payout window
  w_days, w_profit, w_best  (XFA) consistency-window state
  paid       (XFA) True once any payout has happened
  cash       (XFA) net cash extracted so far
"""
from __future__ import annotations
import numpy as np
from propsim import Rules, EPS

MAX_SLOTS = 20


def _draw(rng, rr, risk, room):
    """Zero-edge truncated binary outcome, per account. rr/risk/room arrays."""
    c = np.minimum(risk, np.maximum(room, 0.0))
    W = rr * risk
    with np.errstate(divide="ignore", invalid="ignore"):
        p = np.where(c > 0, c / (c + W), 0.0)
    w = rng.random(len(c)) < p
    return np.where(w, W, -c)


def run_combine(rules: Rules, act, n: int, rng, max_days: int = 2000) -> dict:
    B = np.zeros(n); F = np.full(n, -rules.mll); best = np.zeros(n)
    alive = np.ones(n, bool); passed = np.zeros(n, bool); failed = np.zeros(n, bool)
    days = np.zeros(n, int); subs = np.zeros(n); pass_day = np.full(n, -1)
    for d in range(max_days):
        if not alive.any():
            break
        if d % rules.billing_days == 0:
            subs[alive] += rules.subscription
        start = alive.copy(); active = alive.copy(); day_pnl = np.zeros(n)
        for t in range(MAX_SLOTS):
            if not active.any():
                break
            target = np.maximum(rules.profit_target, best / rules.consistency_max_day_frac)
            rr, risk = act(dict(B=B, F=F, room=B - F, day_pnl=day_pnl, slot=np.full(n, t),
                                day=np.full(n, d), best_day=best, target=target))
            trade = active & (risk > 0)
            active &= trade
            if not active.any():
                break
            pnl = np.zeros(n)
            pnl[active] = _draw(rng, np.asarray(rr, float)[active], np.asarray(risk, float)[active], (B - F)[active])
            B[active] += pnl[active]; day_pnl[active] += pnl[active]
            breach = active & (B <= F + EPS)
            failed |= breach; alive &= ~breach; active &= ~breach
        days[start] += 1
        best[alive] = np.maximum(best[alive], day_pnl[alive])
        newF = np.maximum(F[alive], B[alive] - rules.mll)
        if rules.combine_mll_lock_at is not None:
            newF = np.minimum(rules.combine_mll_lock_at, newF)
        F[alive] = newF
        target = np.maximum(rules.profit_target, best / rules.consistency_max_day_frac)
        newpass = alive & (B >= target - EPS)
        passed |= newpass; pass_day[newpass] = d; alive &= ~newpass
    return dict(passed=passed, failed=failed, unresolved=alive, days=days, sub_fees=subs, pass_day=pass_day, B=B)


def run_xfa(rules: Rules, act, n: int, rng, horizon_days: int = 250, payout_path="standard") -> dict:
    cap = rules.std_cap if payout_path == "standard" else rules.cons_cap
    B = np.zeros(n); F = np.full(n, rules.xfa_mll_start)
    alive = np.ones(n, bool); closed = np.zeros(n, bool)
    cash = np.zeros(n); gross = np.zeros(n); npay = np.zeros(n, int); first = np.full(n, -1)
    win_days = np.zeros(n, int); w_days = np.zeros(n, int); w_profit = np.zeros(n); w_best = np.zeros(n)
    paid = np.zeros(n, bool); since_pay = np.zeros(n)
    for d in range(horizon_days):
        if not alive.any():
            break
        start = alive.copy(); active = alive.copy(); day_pnl = np.zeros(n)
        for t in range(MAX_SLOTS):
            if not active.any():
                break
            rr, risk = act(dict(B=B, F=F, room=B - F, day_pnl=day_pnl, slot=np.full(n, t), day=np.full(n, d),
                                win_days=win_days, w_days=w_days, w_profit=w_profit, w_best=w_best,
                                paid=paid, cash=cash))
            trade = active & (risk > 0)
            active &= trade
            if not active.any():
                break
            pnl = np.zeros(n)
            pnl[active] = _draw(rng, np.asarray(rr, float)[active], np.asarray(risk, float)[active], (B - F)[active])
            B[active] += pnl[active]; day_pnl[active] += pnl[active]
            breach = active & (B <= F + EPS)
            closed |= breach; alive &= ~breach; active &= ~breach
        days_mask = start & alive
        F[days_mask] = np.minimum(rules.xfa_lock_at, np.maximum(F[days_mask], B[days_mask] - rules.mll))
        w_days[days_mask] += 1; w_profit[days_mask] += day_pnl[days_mask]
        w_best[days_mask] = np.maximum(w_best[days_mask], day_pnl[days_mask])
        since_pay[days_mask] += day_pnl[days_mask]
        wd = days_mask & (day_pnl >= rules.std_winning_day_min - EPS)
        win_days[wd] += 1
        if payout_path == "standard":
            elig = days_mask & (win_days >= rules.std_winning_days)
            if rules.require_profit_since_payout:
                elig &= ~paid | (since_pay > EPS)
        else:
            elig = days_mask & (w_days >= rules.cons_min_days) & (w_profit > 0) & \
                   (w_best <= rules.cons_max_day_frac * w_profit + EPS)
        req = np.minimum(rules.payout_max_frac_of_balance * B, cap)
        do = elig & (req >= rules.payout_min - EPS)
        if do.any():
            q = req[do]
            B[do] -= q; gross[do] += q; cash[do] += rules.profit_split * q - rules.payout_fee; npay[do] += 1
            since_pay[do] = 0.0
            first[do & (first < 0)] = d
            F[do] = rules.xfa_lock_at; paid[do] = True
            win_days[do] = 0; w_days[do] = 0; w_profit[do] = 0.0; w_best[do] = 0.0
    return dict(closed=closed, cash=cash, gross=gross, n_payouts=npay, first_payout_day=first, B=B, days=None)


# ---------------------------------------------------------------- policy builders

def static(rr, risk, trades_per_day=1):
    def act(s):
        n = len(s["B"])
        return np.full(n, float(rr)), np.where(s["slot"] < trades_per_day, float(risk), 0.0)
    return act


def xfa_build_then_harvest(rr1, r1, rr2, r2, threshold, harvest_tpd=1, build_tpd=1):
    """Phase 1 ("build"): trade (rr1, r1) while balance < threshold.
    Phase 2 ("harvest"): trade (rr2, r2) once balance >= threshold (aims at winning days)."""
    def act(s):
        harvest = s["B"] >= threshold
        rr = np.where(harvest, float(rr2), float(rr1))
        tpd = np.where(harvest, harvest_tpd, build_tpd)
        risk = np.where(s["slot"] < tpd, np.where(harvest, float(r2), float(r1)), 0.0)
        return rr, risk
    return act


def xfa_stop_after_payout(base_act):
    """Wrap a policy: stop trading entirely once a payout has been taken."""
    def act(s):
        rr, risk = base_act(s)
        return rr, np.where(s["paid"], 0.0, risk)
    return act


def combine_fill_the_gap(rr, r_max, consistency_frac=0.55):
    """Risk the amount that (a) fits under the consistency cap for today and
    (b) does not overshoot the remaining target, capped at r_max, one trade a day."""
    def act(s):
        n = len(s["B"])
        gap = np.maximum(s["target"] - s["B"], 0.0)
        # largest single-day win that keeps target_eff = 3000: rr*risk <= frac*3000
        cap_win = consistency_frac * 3000.0
        risk = np.minimum(np.minimum(np.full(n, float(r_max)), np.full(n, cap_win / rr)), np.maximum(gap / rr, 1.0))
        risk = np.where(s["slot"] < 1, risk, 0.0)
        return np.full(n, float(rr)), risk
    return act
