"""RD-05's coin engine A-0 (`prereg/RD-05_firm_modes.md` 4.3, 9.1-9.3, 2.6; Q-71's pattern): stage one's
`propsim.simulate_combine` and `simulate_xfa` copied verbatim with marked additions, and the coin's draws.

**The copies.** `simulate_combine` and `simulate_xfa` below are the vendored functions' text
(`vendor/stage2/vendor/propsim/propsim.py`, Stage 2 f1b42e2 under E-002), with one keyword added last (`spec`, default
None) and hook statements, **every added line carrying the comment marker RD-05**. With `spec` None every hook is
skipped and every output array equals the vendored function's on the same seed and draw, bit for bit (T-1; 13.1 1 (a)).
`check_vendored_sources` refuses unless the vendored functions hash to `VENDORED_SHA256` (a newer snapshot is a new
row); `recomposition_problems` proves the copy with its marked lines removed parses to the vendored function, statement
for statement (`extended.campaign.recomposition_problems`, reused).

**The additions (4.3), each behind its spec's terms, each off unless the mode-corner has the rule:**

* A-1 the soft daily loss limit: a trade's room is the smaller of the room above the floor and the day's remaining
  limit (`room`); the account is not failed.
* A-2 the evaluation's minimum trading days: a pass needs that many sessions with an executed trade (`eval_pass`).
* A-3 the lifespan (the evaluation ends unpassed at the start of the session the lifespan reaches) and inactivity (an
  account with no trade in the window's sessions ends; on the gross coin it cannot bind, G-9, checked).
* A-5 the funded floor's own rules: a static floor (restored after the engine's trail); the floor at a payout is the
  engine's `xfa_lock_at` (checked equal to the plan's lock); U-16's strict end (trailing uncapped until the first
  payout).
* A-6 `RI`'s intraday equity trail, exact on the coin within its read set (9.2): the floor after a trade is the lower
  of the lock (U-29's timing) and the trail from the equity peak, the trade's own peak included (the draw's
  `peak`, drawn on `coin_peak` for every account every slot, N-2).
* A-7 Labs' Daily path, A-8 My Funded Futures' buffer gate and cadence, A-9 Pro's clock, A-10 Builder's gate, A-17
  LucidFlex's cycle gate and count (`funded_gate`); A-11 the end by count and the verified single-day ceiling ("moved
  to Live": the excess forfeited, the account's life ends at that close, never a payout, its balance not credited);
  A-16 the request-day exclusion (the session after a request counts toward no window).
* the two policies (2.6): `steady (w, r)`; `flip (w, r)` -- the first `k` sessions at `r_flip`, then steady (the
  draws); the costed coin (9.2, `CostedCoinDraw`); A-13's online counters, O(accounts): the flip and steady wins, the
  session each gate last turned true (S-4), the ending and its cause, the conduct exposures, the fairness martingale's
  sums.

**The oracles' facts come from the engine, never from the draw** (Q-138's first corrective cycle, B-1). The spec
computes each trade's chance (`c / (c + w r)` at the room its own `room` hook handed, or the costed race at the size it
recomputes from that room and the tier's allowance), its span and its outcome (the trade's change in the balance, which
must be exactly the win or the loss -- anything else is an exact-check breach), and at `RI` the probability-integral
value of the peak the engine applied, from 9.2's law written out on the spec's side. A draw that is biased, mis-sized
or mis-costed therefore breaches 9.6; the draw's own `last` carries only the peak and the size, read as facts.

Every value comes from `extended.modes_terms` (the record by key); none is typed here (17.2).
"""
from __future__ import annotations

import hashlib
import inspect
import math
from dataclasses import dataclass, field, replace
from typing import Any

import numpy as np

from extended import use_vendored_stage2

use_vendored_stage2()

import sys  # noqa: E402

from propedge.contract import adapter as _adapter  # noqa: E402,F401  -- puts the vendored propsim on sys.path

#: the vendored stage-one engine, as Stage 2's adapter imported it (the vendored tree's manifest covers it)
_vp = sys.modules["propsim"]
EPS, Policy, RandomDraw, Rules, p_race = _vp.EPS, _vp.Policy, _vp.RandomDraw, _vp.Rules, _vp.p_race

from extended import modes_terms as M  # noqa: E402
from extended.campaign import recomposition_problems as _recomposition  # noqa: E402

#: sha256 of the vendored functions' source text (LF) from which the copies were composed (Stage 2 f1b42e2)
VENDORED_SHA256 = {"simulate_combine": "7d92f9ec8fbcb5ff42cc5a1d6b42c29bcb2862f8d445bbae6af83f266c7e7443",
                   "simulate_xfa": "bc54c9157611d1511019512314946a0e7a4469bc075759cf9232e17222d3ac00"}
MARKER = "RD-05"
INF = float("inf")


def _src_sha(fn: Any) -> str:
    return hashlib.sha256(inspect.getsource(fn).replace("\r\n", "\n").encode("utf-8")).hexdigest()


def check_vendored_sources() -> None:
    """Refuse (`RuntimeError`) unless the vendored functions are the ones the copies were composed from."""
    for name, want in VENDORED_SHA256.items():
        got = _src_sha(getattr(_vp, name))
        if got != want:
            raise RuntimeError(f"REFUSED (RD-05 A-0): the vendored propsim.{name} hashes to {got}, not the {want} this "
                               "engine was composed from; re-compose extended/modes_engine.py under the new snapshot")


def recomposition_problems() -> list[str]:
    """Each copy with its marked lines removed against the vendored function, statement for statement."""
    out = []
    for ours, theirs in ((simulate_combine, _vp.simulate_combine), (simulate_xfa, _vp.simulate_xfa)):
        out += [f"{theirs.__name__}: {p}" for p in _recomposition(ours, theirs, (MARKER,))]
    return out


# ------------------------------------------------------------------------------------------------ the copies


def simulate_combine(rules: Rules, policy: Policy, edge: float, n: int,
                     rng: np.random.Generator | None = None, draw=None,
                     max_days: int = 2000,
                     spec=None,  # RD-05
                     ) -> dict:
    check_vendored_sources()  # RD-05
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
    st = spec.start(n, draw) if spec is not None else None  # RD-05

    for d in range(max_days):
        if not alive.any():
            break
        if spec is not None: spec.session_start(st, d, alive, B, F)  # RD-05
        if d % rules.billing_days == 0:
            sub_fees[alive] += rules.subscription
        alive_at_start = alive.copy()
        active = alive.copy()
        day_pnl = np.zeros(n)
        for t in range(policy.trades_per_day):
            if not active.any():
                break
            cushion = B - F
            if spec is not None: cushion = spec.room(st, cushion, day_pnl)  # RD-05
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
        if spec is not None: spec.after_trades(st, d, alive_at_start, alive, day_pnl, B, F, trades)  # RD-05
        # 16:00 CT lock
        days[alive_at_start] += 1
        best_day[alive] = np.maximum(best_day[alive], day_pnl[alive])
        F_prev = F.copy() if spec is not None else None  # RD-05
        newF = np.maximum(F[alive], B[alive] - rules.mll)
        if rules.combine_mll_lock_at is not None:
            newF = np.minimum(rules.combine_mll_lock_at, newF)
        F[alive] = newF
        if spec is not None: spec.eval_floor(st, alive, F, F_prev)  # RD-05
        target_eff = np.maximum(rules.profit_target, best_day / rules.consistency_max_day_frac)
        newpass = alive & (B >= target_eff - EPS)
        if spec is not None: newpass = spec.eval_pass(st, d, alive, B, best_day, newpass)  # RD-05
        passed |= newpass
        pass_day[newpass] = d
        alive &= ~newpass

    out = dict(  # RD-05
        passed=passed, failed=failed, unresolved=alive,  # RD-05
        days=days, trades=trades, sub_fees=sub_fees,  # RD-05
        pass_day=pass_day, fail_day=fail_day,  # RD-05
        B=B, F=F, best_day=best_day,  # RD-05
    )  # RD-05
    if spec is not None: return spec.outputs(st, out)  # RD-05
    return dict(
        passed=passed, failed=failed, unresolved=alive,
        days=days, trades=trades, sub_fees=sub_fees,
        pass_day=pass_day, fail_day=fail_day,
        B=B, F=F, best_day=best_day,
    )


def simulate_xfa(rules: Rules, policy: Policy, edge: float, n: int,
                 rng: np.random.Generator | None = None, draw=None,
                 horizon_days: int = 250, horizon_per_account=None,
                 spec=None,  # RD-05
                 ) -> dict:
    check_vendored_sources()  # RD-05
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
    st = spec.start(n, draw) if spec is not None else None  # RD-05

    for d in range(int(hz.max())):
        trading = alive & (d < hz)
        if not trading.any():
            break
        if spec is not None: spec.session_start(st, d, trading, B, F)  # RD-05
        alive_at_start = trading.copy()
        active = trading.copy()
        day_pnl = np.zeros(n)
        for t in range(policy.trades_per_day):
            if not active.any():
                break
            cushion = B - F
            if spec is not None: cushion = spec.room(st, cushion, day_pnl)  # RD-05
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
        if spec is not None: spec.after_trades(st, d, alive_at_start, alive, day_pnl, B, F, trades)  # RD-05
        # 16:00 CT lock (only accounts that traded today)
        days[alive_at_start] += 1
        lk = alive & alive_at_start
        F_prev = F.copy() if spec is not None else None  # RD-05
        F[lk] = np.minimum(rules.xfa_lock_at, np.maximum(F[lk], B[lk] - rules.mll))
        if spec is not None: spec.funded_floor(st, lk, F, F_prev, B, paid_once)  # RD-05
        # window bookkeeping (completed day)
        w_days[lk] += 1
        w_profit[lk] += day_pnl[lk]
        w_best[lk] = np.maximum(w_best[lk], day_pnl[lk])
        since_pay[lk] += day_pnl[lk]
        wd = lk & (day_pnl >= rules.std_winning_day_min - EPS)
        win_days[wd] += 1
        win_days_total[wd] += 1
        if spec is not None: spec.after_window(st, lk, day_pnl, win_days, win_days_total, w_days)  # RD-05
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
        if spec is not None: elig, req = spec.funded_gate(st, d, lk, day_pnl, B, elig, req, since_pay, paid_once, n_payouts, win_days, w_days, w_profit, w_best)  # RD-05
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
        if spec is not None: spec.after_payouts(st, d, do, req, B, F, alive, n_payouts, cash, gross_paid)  # RD-05

    out = dict(  # RD-05
        closed=closed, alive=alive, days=days, trades=trades,  # RD-05
        cash=cash, gross_paid=gross_paid, n_payouts=n_payouts,  # RD-05
        first_payout_day=first_payout_day, B=B, F=F,  # RD-05
        win_days_total=win_days_total,  # RD-05
    )  # RD-05
    if spec is not None: return spec.outputs(st, out)  # RD-05
    return dict(
        closed=closed, alive=alive, days=days, trades=trades,
        cash=cash, gross_paid=gross_paid, n_payouts=n_payouts,
        first_payout_day=first_payout_day, B=B, F=F,
        win_days_total=win_days_total,
    )


# ------------------------------------------------------------------------------------------------ the draws


def peak_survival(x: Any, a: Any, b: Any) -> np.ndarray:
    """9.2: `P(m >= x | loss) = a (b - x) / (b (a + x))` for `0 <= x < b` -- a losing trade's highest point racing a
    lower exit at `-a` against a target at `+b` (`propsim.mae_survival_given_win` with the exits exchanged)."""
    x, a, b = np.asarray(x, float), np.asarray(a, float), np.asarray(b, float)
    return np.asarray(_vp.mae_survival_given_win(x, b, a, 0.0), float)


def peak_inverse(s: Any, a: Any, b: Any) -> np.ndarray:
    """The inverse transform of `peak_survival` at a survival level `s` (`propsim.sample_mae_given_win`'s closed form
    with the exits exchanged): `a b (1 - s) / (s b + a)`."""
    s, a, b = np.asarray(s, float), np.asarray(a, float), np.asarray(b, float)
    return a * b * (1.0 - s) / (s * b + a)


class CoinDraw:
    """The gross coin (9.2): the vendored `RandomDraw`'s zero-edge truncated race, its risk per account set by the
    policy -- `steady (w, r)`, or `flip (w, r)`: `r_flip` for sessions below `k`, then `r`. It draws `n` uniforms every
    slot for every account (so a `(w, r)` stream pairs every mode-corner, policy and stop, S1), and, with a peak stream,
    `n` more every slot for `RI`'s losing-trade peaks (N-2). With `k` 0 it is the vendored `RandomDraw` at zero edge,
    output for output (T-1). Each call's trade facts are kept for the hooks (`last`)."""

    def __init__(self, w: float, r: float, rng: np.random.Generator, *, k: int = 0, r_flip: float | None = None,
                 peak_rng: np.random.Generator | None = None):
        self.w, self.r, self.rng = float(w), float(r), rng
        self.k, self.r_flip = int(k), (None if r_flip is None else float(r_flip))
        if self.k > 0 and self.r_flip is None:
            raise ValueError("a flip policy needs r_flip")
        self.peak_rng = peak_rng
        self.last: dict[str, np.ndarray] = {}

    def risk_at(self, day: int) -> float:
        return self.r_flip if (self.k > 0 and int(day) < self.k) else self.r

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray) -> np.ndarray:
        u = self.rng.random(n)
        risk = self.risk_at(day)
        win = self.w * risk
        c = np.minimum(risk, np.maximum(cushion, 0.0))
        p = p_race(c, win, 0.0)
        pnl = np.where(u < p, win, -c)
        hit = u < p
        last = {"p": np.asarray(p, float), "span": c + win, "hit": hit, "gross": pnl, "cost": np.zeros(n),
                "risk": np.full(n, risk), "room_cut": c < risk - EPS, "flip": np.full(n, self.k > 0 and day < self.k),
                "contracts": np.zeros(n, int)}
        if self.peak_rng is not None:
            s = self.peak_rng.random(n)
            with np.errstate(invalid="ignore", divide="ignore"):       # a zero room (an ended account): unused
                peak = np.where(hit, win, peak_inverse(s, np.maximum(c, 0.0), win))
                last["peak"] = peak
                last["peak_F"] = 1.0 - peak_survival(np.minimum(peak, win), np.maximum(c, 0.0), win)
        self.last = last
        return pnl


@dataclass(frozen=True)
class SizeTable:
    """The costed coin's sizes in increasing realised risk at one stop (9.2, D-324 mixed sizing): each a (minis,
    micros) with its stop-out cost -- the stop's dollars, the entry and stop ticks of slippage, the round turn."""

    minis: np.ndarray
    micros: np.ndarray
    realised: np.ndarray
    stopout: np.ndarray
    cost_win: np.ndarray
    cost_loss: np.ndarray


def size_table(s: int, allowance: M.Allowance, schedule: str) -> SizeTable:
    """Every size the counting allows at the top of its allowance, as mixed sizing would choose it for some budget,
    in increasing realised risk; refused unless the stop-out cost increases with it (so the largest size within a
    room is a search)."""
    tv = M.tick_values()
    mpm = M.micros_per_mini()
    slip = M.fill_slippage()
    mnq, nq = M.round_turn(schedule)
    combos: list[tuple[int, int]] = []
    if allowance.counting == "ratio":
        for me in range(int(allowance.micros) + 1):
            combos.append((min(me // mpm, int(allowance.minis)), me - min(me // mpm, int(allowance.minis)) * mpm))
    else:
        for a in range(int(allowance.minis) + 1):
            for b in range(int(allowance.minis) + 1 - a):
                combos.append((a, b))
        combos.sort(key=lambda x: (x[0] * tv["NQ"] + x[1] * tv["MNQ"], x[0]))
    mi = np.array([c[0] for c in combos], int)
    mc = np.array([c[1] for c in combos], int)
    realised = s * (mi * tv["NQ"] + mc * tv["MNQ"])
    per_tick = mi * tv["NQ"] + mc * tv["MNQ"]
    fee = mi * nq + mc * mnq
    cw = fee + slip["entry_slippage_ticks"] * per_tick + slip["target_slippage_ticks"] * per_tick
    cl = fee + (slip["entry_slippage_ticks"] + slip["stop_slippage_ticks"]) * per_tick
    stopout = realised + cl
    if np.any(np.diff(realised) <= 0) or np.any(np.diff(stopout) <= 0):
        raise ValueError(f"the costed coin's sizes at {s} ticks are not increasing in risk and stop-out cost")
    return SizeTable(mi, mc, realised, stopout, cw, cl)


def tier_cap_index(table: SizeTable, allowance: M.Allowance, balance: np.ndarray) -> np.ndarray:
    """The current tier's allowance (the ladder by the balance above start; flat otherwise) as an index into the
    size table: the largest size the tier allows."""
    n = len(balance)
    mpm = M.micros_per_mini()
    if allowance.ladder is None:
        return np.full(n, len(table.realised) - 1)
    thr = np.array([t for t, _ in allowance.ladder], float)
    minis = np.array([m for _, m in allowance.ladder], int)
    tier = np.clip(np.searchsorted(thr, balance + EPS, side="right") - 1, 0, len(thr) - 1)
    if allowance.counting == "ratio":
        me = table.minis * mpm + table.micros
        return np.searchsorted(me, minis[tier] * mpm, side="right") - 1
    tot = table.minis + table.micros
    caps = {int(m): int(np.max(np.nonzero(tot <= m)[0])) for m in set(minis.tolist())}
    return np.array([caps[int(m)] for m in minis[tier]])


class CostedCoinDraw:
    """The costed coin (9.2): at each trade `n` is recomputed from that trade's room -- the largest size whose stop-out
    (the stop's dollars, the stop and entry ticks, the round turn) lies within the room and the day's remaining limit,
    at most part B's contracts for `r` at `s` and the current tier's allowance; costs inside the room. A size below the
    registered rule's stand-aside share of `r`, or a stop below its cost floor, is no trade (NaN: the session is a
    no-trade session, counted toward inactivity). The bracket is driftless at the realised risk `r'`, its target at
    `w r'`; costs subtracted at the exit. With a peak stream (`RI`, the lead's R-c) a losing trade's highest point is
    drawn from 9.2's law at `a = r'`, `b = w r'`, `n` uniforms every slot for every account (N-2)."""

    def __init__(self, w: float, r: float, s: int, allowance: M.Allowance, schedule: str, kind: str,
                 rng: np.random.Generator, peak_rng: np.random.Generator | None = None):
        self.w, self.r, self.s, self.rng, self.kind = float(w), float(r), int(s), rng, kind
        self.allowance = allowance
        self.table = size_table(int(s), allowance, schedule)
        sa = M.registered_stand_aside()["combine" if kind == M.EVAL else "funded"]
        self.share, self.floor_ticks = float(sa[0]), int(sa[1])
        # part B's contracts for r at s: the largest size whose realised risk is at most r
        self.risk_cap = int(np.searchsorted(self.table.realised, float(r) + EPS, side="right") - 1)
        self.cap_index = np.full(1, len(self.table.realised) - 1)
        self.peak_rng = peak_rng
        self.last: dict[str, np.ndarray] = {}

    def set_tier(self, n: int, balance: np.ndarray) -> None:
        self.cap_index = tier_cap_index(self.table, self.allowance, np.asarray(balance, float)[:n])

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray) -> np.ndarray:
        u = self.rng.random(n)
        tb = self.table
        idx = np.searchsorted(tb.stopout, np.maximum(cushion, 0.0) + EPS, side="right") - 1
        idx = np.minimum(np.minimum(idx, self.risk_cap), self.cap_index)
        idx = np.maximum(idx, 0)
        realised = tb.realised[idx]
        take = (idx > 0) & (realised >= self.share * self.r - EPS) & (self.s >= self.floor_ticks)
        p = np.full(n, 1.0 / (1.0 + self.w))
        hit = u < p
        gross = np.where(hit, self.w * realised, -realised)
        cost = np.where(hit, tb.cost_win[idx], tb.cost_loss[idx])
        pnl = np.where(take, gross - cost, np.nan)
        self.last = {"contracts": np.where(take, tb.minis[idx] * M.micros_per_mini() + tb.micros[idx], 0),
                     "full_allowance": take & (idx == self.cap_index), "index": idx}
        if self.peak_rng is not None:
            s = self.peak_rng.random(n)
            with np.errstate(invalid="ignore", divide="ignore"):
                self.last["peak"] = np.where(hit, self.w * realised, peak_inverse(s, realised, self.w * realised))
        return pnl


# ------------------------------------------------------------------------------------------------ the specs


class _State:
    """A run's per-account state for the hooks (O(accounts), A-13)."""

    def __init__(self, **kw: Any):
        self.__dict__.update(kw)


@dataclass
class _Fair:
    S: float = 0.0
    V: float = 0.0
    b: float = 0.0
    trades: int = 0


TOL = float(M.declared("exact.tol"))                         # 17.2's table (V-6)


def loss_peak_cdf(m: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """9.2's law of a losing trade's highest point, written out here on the spec's side (independent of the draw's
    `peak_inverse` and of `peak_survival`): `F(x) = 1 - a (b - x) / (b (a + x))` for `0 <= x < b`."""
    with np.errstate(invalid="ignore", divide="ignore"):
        return 1.0 - a * (b - m) / (b * (a + m))


def _fair_add(fair: _Fair, ex: np.ndarray, p: np.ndarray, span: np.ndarray, hit: np.ndarray) -> None:
    """9.6's fairness martingale over the executed trades, from the spec's engine-side facts (B-1): (1{target} - p)
    x span, `p` the trade's chance at its room (`c / (c + w r)`, or the costed race at its realised risk)."""
    if not ex.any():
        return
    p, span, h = p[ex], span[ex], hit[ex].astype(float)
    fair.S += float(np.sum((h - p) * span))
    fair.V += float(np.sum(p * (1.0 - p) * span ** 2))
    fair.b = max(fair.b, float(np.max(span)))
    fair.trades += int(ex.sum())


def _fair_add_peaks(fair: _Fair, lose: np.ndarray, F: np.ndarray, span: np.ndarray) -> None:
    """N-2: `RI`'s losing-trade peaks by their probability-integral increment (F(m) - 1/2) x span, variance
    span^2 / 12, bound span / 2."""
    if not lose.any():
        return
    half = M.NOT_RULE_VALUES["half"]
    sp = span[lose]
    fair.S += float(np.sum((F[lose] - half) * sp))
    fair.V += float(np.sum(sp ** 2) / M.NOT_RULE_VALUES["uniform_var"])
    fair.b = max(fair.b, float(np.max(sp)) * half)


EXACT = ("malformed_outcome", "trade_taken_unpredicted", "loss_beyond_room", "peak_out_of_law", "net_not_split",
         "paid_not_request", "forfeit_not_at_ceiling", "request_out_of_bounds")


class _Spec:
    """What both modes' specs share: the trade's engine-side facts (B-1), the exact checks (S-3), the counters."""

    t: Any
    w: float
    r: float
    k: int
    r_flip: float | None
    coin: str
    stop: int | None
    kind: str

    def _base_state(self, n: int, draw: Any) -> dict[str, Any]:
        z = lambda dt=float: np.zeros(n, dt)  # noqa: E731
        st = dict(n=n, draw=draw, fair=_Fair(), trades_prev=np.zeros(n, int), idle=np.zeros(n, int),
                  room_last=np.full(n, INF), traded=np.zeros(n, bool), gross_sum=z(), costs=z(),
                  room_cuts=np.zeros(n, int), flip_trades=np.zeros(n, int), full_allowance=np.zeros(n, int),
                  max_contracts=np.zeros(n, int), hist=None, no_trade_sessions=np.zeros(n, int),
                  flip_wins=np.zeros(n, int), steady_wins=np.zeros(n, int), exact={k: 0 for k in EXACT},
                  table=None, cap_index=np.zeros(n, int))
        if self.coin == "costed":
            st["table"] = size_table(int(self.stop), self.t.allowance, self.t.commission)
            st["cap_index"] = tier_cap_index(st["table"], self.t.allowance, np.zeros(n))
            draw.set_tier(n, np.zeros(n))
            st["hist"] = np.zeros((n, _hist_size(draw)), np.int32)
        return st

    def risk_at(self, d: int) -> float:
        return float(self.r_flip) if (self.k > 0 and d < self.k) else float(self.r)

    def _set_tier(self, st: _State, B: np.ndarray) -> None:
        if self.coin == "costed":
            st.draw.set_tier(st.n, B)
            st.cap_index = tier_cap_index(st.table, self.t.allowance, np.asarray(B, float))

    def _room(self, st: _State, cushion: np.ndarray, day_pnl: np.ndarray) -> np.ndarray:
        t = self.t
        room = np.full(st.n, INF) if getattr(t, "close_only", False) else cushion
        if t.dll is not None:                                                     # A-1, and N-3 at a close-only corner
            room = np.minimum(room, float(t.dll) + day_pnl)
        st.room_last = np.array(room, float)
        return room

    def _trade_facts(self, st: _State, d: int, alive_at_start: np.ndarray, ex: np.ndarray, pnl: np.ndarray
                     ) -> dict[str, np.ndarray]:
        """The trade's chance, span, outcome, gross P&L and costs, from engine facts only (B-1): the room the hook
        handed, the cell's `w` and risk schedule, the trade's change in the balance (`pnl`), and on the costed coin the
        size and costs recomputed here against the fee schedule. A change in the balance that is neither the trade's
        win nor its loss is an exact-check breach (S-3)."""
        n = st.n
        room = np.maximum(st.room_last, 0.0)
        if self.coin == "gross":
            risk = self.risk_at(d)
            win = self.w * risk
            c = np.minimum(risk, room)
            with np.errstate(invalid="ignore", divide="ignore"):
                p = c / (c + win)
            span = c + win
            hit = ex & (np.abs(pnl - win) <= TOL * max(1.0, win))
            loss = ex & (np.abs(pnl + c) <= TOL * max(1.0, win))
            cost = np.zeros(n)
            st.room_cuts[ex & (c < risk - EPS) & (self.k > 0 and d < self.k)] += 1
            take = alive_at_start.copy()
            a, b = c, np.full(n, win)
        else:
            tb = st.table
            sa = M.registered_stand_aside()["combine" if self.kind == M.EVAL else "funded"]
            risk_cap = int(np.searchsorted(tb.realised, float(self.r) + EPS, side="right") - 1)
            idx = np.searchsorted(tb.stopout, room + EPS, side="right") - 1
            idx = np.maximum(np.minimum(np.minimum(idx, risk_cap), st.cap_index), 0)
            rr = tb.realised[idx]
            take = alive_at_start & (idx > 0) & (rr >= float(sa[0]) * self.r - EPS) & (int(self.stop) >= int(sa[1]))
            p = np.full(n, 1.0 / (1.0 + self.w))
            span = rr * (1.0 + self.w)
            w_amt, l_amt = self.w * rr - tb.cost_win[idx], -rr - tb.cost_loss[idx]
            hit = ex & (np.abs(pnl - w_amt) <= TOL * max(1.0, float(np.max(span))))
            loss = ex & (np.abs(pnl - l_amt) <= TOL * max(1.0, float(np.max(span))))
            cost = np.where(hit, tb.cost_win[idx], tb.cost_loss[idx])
            mpm = M.micros_per_mini()
            contracts = tb.minis[idx] * mpm + tb.micros[idx]
            st.full_allowance[ex & (idx == st.cap_index)] += 1
            st.max_contracts = np.maximum(st.max_contracts, np.where(ex, contracts, 0))
            rows = np.nonzero(ex)[0]
            np.add.at(st.hist, (rows, np.minimum(contracts[rows], st.hist.shape[1] - 1)), 1)
            a, b = rr, self.w * rr
        st.exact["malformed_outcome"] += int(np.sum(ex & ~hit & ~loss))
        st.exact["trade_taken_unpredicted"] += int(np.sum(ex != (take & alive_at_start)))
        st.exact["loss_beyond_room"] += int(np.sum(ex & (-pnl > room + TOL * np.maximum(1.0, room))))
        return {"p": p, "span": span, "hit": hit, "loss": loss, "cost": cost, "a": a, "b": b}

    def _book(self, st: _State, d: int, alive_at_start: np.ndarray, day_pnl: np.ndarray, trades: np.ndarray,
              peaks: bool) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        ex = trades > st.trades_prev
        st.trades_prev = trades.copy()
        st.traded = ex
        f = self._trade_facts(st, d, alive_at_start, ex, day_pnl)
        _fair_add(st.fair, ex, f["p"], f["span"], f["hit"])
        if peaks:                                                                # A-6 / R-c: the peak the engine applies
            m = np.asarray(st.draw.last["peak"], float)
            lose = ex & f["loss"]
            bad = ex & f["hit"] & (np.abs(m - f["b"]) > TOL * np.maximum(1.0, f["b"]))
            bad |= lose & ((m < -TOL) | (m >= f["b"]))
            st.exact["peak_out_of_law"] += int(np.sum(bad))
            F = loss_peak_cdf(np.clip(m, 0.0, None), f["a"], f["b"])
            _fair_add_peaks(st.fair, lose, F, f["span"])
            f["peak"] = m
        st.gross_sum[ex] += day_pnl[ex] + f["cost"][ex]
        st.costs[ex] += f["cost"][ex]
        st.flip_trades[ex & (self.k > 0 and d < self.k)] += 1
        win = ex & (day_pnl > EPS)
        (st.flip_wins if (self.k > 0 and d < self.k) else st.steady_wins)[win] += 1
        idle = alive_at_start & ~ex
        st.no_trade_sessions[idle] += 1
        st.idle[ex] = 0
        st.idle[idle] += 1
        return ex, f

    def _rise(self, st: _State, d: int, name: str, cond: np.ndarray, live: np.ndarray) -> None:
        """S-4: the session each gate last turned true (its false-to-true change), among the live accounts."""
        prev = st.gate_prev[name]
        rise = live & cond & ~prev
        st.gate_rise[name][rise] = d
        st.gate_prev[name] = np.where(live, cond, prev)

    def _common_outputs(self, st: _State, out: dict[str, Any]) -> None:
        out.update(gross_sum=st.gross_sum, costs=st.costs, room_cuts=st.room_cuts, flip_trades=st.flip_trades,
                   full_allowance=st.full_allowance, no_trade_sessions=st.no_trade_sessions,
                   flip_wins=st.flip_wins, steady_wins=st.steady_wins, exact=dict(st.exact),
                   fair=dict(S=st.fair.S, V=st.fair.V, b=st.fair.b, trades=st.fair.trades),
                   s8_ratio_max=_s8_ratio(st.hist) if st.hist is not None else None,
                   size_spread=_size_spread(st.hist) if st.hist is not None else None, max_contracts=st.max_contracts)


class EvalSpec(_Spec):
    """One evaluation mode-corner's run on the coin: its terms, the cell `(w, r)`, the policy and the coin."""

    kind = M.EVAL
    GATES = ("base_target", "consistency_target", "min_days")

    def __init__(self, terms: M.EvalTerms, w: float, r: float, *, policy: str = "steady", coin: str = "gross",
                 stop: int | None = None):
        self.t, self.w, self.r, self.policy, self.coin, self.stop = terms, float(w), float(r), policy, coin, stop
        from extended import modes_rules as R

        self.k = R.k_eval(terms) if policy == "flip" else 0
        self.r_flip = R.r_flip(M.EVAL, terms, w)["r_flip"] if policy == "flip" else None
        if policy not in ("steady", "flip") or coin not in ("gross", "costed"):
            raise ValueError((policy, coin))
        if coin == "costed" and (policy != "steady" or stop is None):
            raise ValueError("the costed coin runs steady at a declared stop (9.1)")

    def rules(self) -> Rules:
        t = self.t
        return replace(Rules(), profit_target=float(t.target), mll=float(t.mll),
                       consistency_max_day_frac=INF if t.consistency is None else float(t.consistency),
                       combine_mll_lock_at=None if t.floor == "static" else t.lock,
                       subscription=0.0 if t.subscription is None else float(t.subscription),
                       billing_days=int(t.billing) if t.billing else int(M.NOT_RULE_VALUES["never"]))

    def policy_obj(self) -> Policy:
        return Policy(rr=self.w, risk=self.r)

    def draw(self, rng: np.random.Generator) -> Any:
        if self.coin == "costed":
            return CostedCoinDraw(self.w, self.r, int(self.stop), self.t.allowance, self.t.commission, M.EVAL, rng)
        return CoinDraw(self.w, self.r, rng, k=self.k, r_flip=self.r_flip)

    # ---- hooks
    def start(self, n: int, draw: Any) -> _State:
        st = _State(**self._base_state(n, draw))
        st.days_traded = np.zeros(n, int)
        st.win_sum = np.zeros(n)
        st.expired = np.zeros(n, bool)
        st.inactive = np.zeros(n, bool)
        st.raised = np.zeros(n, bool)
        st.gate_prev = {g: np.zeros(n, bool) for g in self.GATES}
        st.gate_rise = {g: np.full(n, -1) for g in self.GATES}
        return st

    def session_start(self, st: _State, d: int, alive: np.ndarray, B: np.ndarray, F: np.ndarray) -> None:
        self._set_tier(st, B)
        if self.t.lifespan is not None and d >= int(self.t.lifespan):              # A-3: the lifespan ends it
            exp = alive.copy()
            st.expired |= exp
            alive &= ~exp

    def room(self, st: _State, cushion: np.ndarray, day_pnl: np.ndarray) -> np.ndarray:
        return self._room(st, cushion, day_pnl)                                   # U-27 lenient; A-1

    def after_trades(self, st: _State, d: int, alive_at_start: np.ndarray, alive: np.ndarray, day_pnl: np.ndarray,
                     B: np.ndarray, F: np.ndarray, trades: np.ndarray) -> None:
        ex, _f = self._book(st, d, alive_at_start, day_pnl, trades, peaks=False)
        st.days_traded[ex] += 1
        win = ex & (day_pnl > EPS)
        st.win_sum[win] += day_pnl[win]
        if self.t.inactivity is not None:                                         # A-3: the window untraded
            gone = alive & (st.idle >= int(self.t.inactivity))
            st.inactive |= gone
            alive &= ~gone

    def eval_floor(self, st: _State, alive: np.ndarray, F: np.ndarray, F_prev: np.ndarray) -> None:
        if self.t.floor == "static":                                              # A-5's evaluation form: never moves
            F[alive] = F_prev[alive]

    def eval_pass(self, st: _State, d: int, alive: np.ndarray, B: np.ndarray, best_day: np.ndarray,
                  newpass: np.ndarray) -> np.ndarray:
        t = self.t
        tgt = alive & (B >= float(t.target) - EPS)
        if t.consistency is None:
            cons = alive.copy()
        elif t.consistency_base == "wins":                                        # U-15 lenient: the winning days
            cons = alive & (best_day <= float(t.consistency) * st.win_sum + EPS)
        else:
            cons = alive & (B >= best_day / float(t.consistency) - EPS)
        md = alive.copy() if t.min_days is None else alive & (st.days_traded >= int(t.min_days))
        for g, cond in zip(self.GATES, (tgt, cons, md)):
            self._rise(st, d, g, cond, alive)
        st.raised |= alive & tgt & ~cons
        if t.consistency_base == "wins":
            return tgt & cons & md
        return newpass & md                                                        # the engine's own, with A-2

    def outputs(self, st: _State, out: dict[str, Any]) -> dict[str, Any]:
        out = dict(out)
        out["unresolved"] = out["unresolved"] & ~st.expired & ~st.inactive
        last_gate = np.full(st.n, "", dtype=object)
        p = out["passed"]
        g = np.stack([st.gate_rise[x] for x in self.GATES])
        idx = np.argmax(g, axis=0)                   # the gate that turned true last (ties: target, consistency, days)
        names = np.array(self.GATES, dtype=object)
        last_gate[p] = names[idx[p]]
        last_gate[p & (idx == 1) & ~st.raised] = "base_target"
        cause = np.full(st.n, "", dtype=object)
        cause[out["failed"]] = "floor"
        cause[st.expired] = "lifespan"
        cause[st.inactive] = "inactivity"
        cause[out["unresolved"]] = "censored"
        self._common_outputs(st, out)
        out.update(expired=st.expired, inactive=st.inactive, last_gate=last_gate, cause=cause, raised=st.raised,
                   days_traded=st.days_traded, gate_rise={k: v.copy() for k, v in st.gate_rise.items()})
        return out


def _hist_size(draw: "CostedCoinDraw") -> int:
    tb = draw.table
    return int(np.max(tb.minis * M.micros_per_mini() + tb.micros)) + 1


def _s8_ratio(hist: np.ndarray) -> np.ndarray:
    """4.7 item 5: each account's largest trade's contracts over the median of its other trades (the histogram)."""
    n, m = hist.shape
    sizes = np.arange(m)
    out = np.full(n, np.nan)
    tot = hist.sum(axis=1)
    two = int(M.NOT_RULE_VALUES["pair"])                       # a largest trade and at least one other
    for i in np.nonzero(tot >= two)[0]:
        h = hist[i].copy()
        top = int(np.max(np.nonzero(h)[0]))
        h[top] -= 1
        cum = np.cumsum(h)
        k = cum[-1]
        med = (sizes[np.searchsorted(cum, (k + 1) // two)] + sizes[np.searchsorted(cum, k // two + 1)]) / float(two)
        out[i] = top / med if med > 0 else np.nan
    return out


def _size_spread(hist: np.ndarray) -> dict[str, np.ndarray]:
    """4.7 item 5 (S-10): the spread of each account's trade sizes -- the range and the standard deviation of its
    contracts (micro-equivalents), from the histogram; NaN for an account with no trade."""
    sizes = np.arange(hist.shape[1], dtype=float)
    tot = hist.sum(axis=1).astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = (hist * sizes).sum(axis=1) / tot
        var = (hist * sizes ** 2).sum(axis=1) / tot - mean ** 2
    has = hist > 0
    hi = np.where(has.any(axis=1), (has * sizes).max(axis=1), np.nan)
    lo = np.where(has.any(axis=1), np.where(has, sizes, np.inf).min(axis=1), np.nan)
    return {"range": hi - lo, "sd": np.sqrt(np.maximum(var, 0.0))}


class FundedSpec(_Spec):
    """One funded mode-corner's run on the coin."""

    kind = M.FUNDED
    GATES = ("winning_days", "cycle_share", "cycle_days", "buffer_min", "clock", "profit_since")

    def __init__(self, terms: M.FundedTerms, w: float, r: float, *, policy: str = "steady", coin: str = "gross",
                 stop: int | None = None):
        self.t, self.w, self.r, self.policy, self.coin, self.stop = terms, float(w), float(r), policy, coin, stop
        from extended import modes_rules as R

        self.R = R
        self.k = R.k_funded(terms)["k_F"] if policy == "flip" else 0
        self.r_flip = R.r_flip(M.FUNDED, terms, w)["r_flip"] if policy == "flip" else None
        if terms.lock is not None and terms.floor_at_payout is not None and abs(terms.lock - terms.floor_at_payout) > EPS:
            raise ValueError(f"{terms.mode}: the floor at a payout {terms.floor_at_payout} is not its lock {terms.lock}; "
                             "the engine sets xfa_lock_at at a payout (A-5)")
        if coin == "costed" and (policy != "steady" or stop is None):
            raise ValueError("the costed coin runs steady at a declared stop (9.1)")

    def rules(self) -> Rules:
        t = self.t
        at_pay = t.floor_at_payout if t.floor_at_payout is not None else 0.0
        big = float(M.NOT_RULE_VALUES["never"])
        return replace(Rules(), xfa_mll_start=float(t.floor_start), mll=float(t.mll), xfa_lock_at=float(at_pay),
                       std_winning_days=int(t.winning_days) if t.winning_days is not None else 0,
                       std_winning_day_min=float(t.winning_day_min) if t.winning_day_min is not None else 0.0,
                       std_cap=float(t.cap) if t.cap is not None else big,
                       cons_min_days=int(t.cons_min_days) if t.cons_min_days is not None else 0,
                       cons_max_day_frac=float(t.cons_share) if t.cons_share is not None else 1.0,
                       cons_cap=float(t.cap) if t.cap is not None else big, payout_min=float(t.payout_min),
                       payout_max_frac_of_balance=float(t.frac) if t.frac is not None else 1.0,
                       profit_split=float(t.split), require_profit_since_payout=bool(t.profit_since_required),
                       payout_fee=0.0)

    def policy_obj(self) -> Policy:
        return Policy(rr=self.w, risk=self.r, payout_path="consistency" if self.t.gate == "ts_con" else "standard")

    def peaks(self) -> bool:
        return self.t.floor == "intraday"

    def draw(self, rng: np.random.Generator, peak_rng: np.random.Generator | None = None) -> Any:
        pr = peak_rng if self.peaks() else None
        if self.peaks() and pr is None:
            raise ValueError("RI's funded mode draws its peaks on the coin_peak stream (N-2)")
        if self.coin == "costed":
            return CostedCoinDraw(self.w, self.r, int(self.stop), self.t.allowance, self.t.commission, M.FUNDED, rng,
                                  peak_rng=pr)
        return CoinDraw(self.w, self.r, rng, k=self.k, r_flip=self.r_flip, peak_rng=pr)

    # ---- hooks
    def start(self, n: int, draw: Any) -> _State:
        z = lambda dt=float: np.zeros(n, dt)  # noqa: E731
        st = _State(**self._base_state(n, draw))
        st.first_trade = np.full(n, -1)
        st.last_req = np.full(n, -1)
        st.excl_next = np.zeros(n, bool)
        st.pending = z()
        st.peak_eq = z()
        st.moved_live = np.zeros(n, bool)
        st.forfeit = z()
        st.inactive = np.zeros(n, bool)
        st.count_end = np.zeros(n, bool)
        st.flip_wins_at_first = np.full(n, -1)
        st.steady_wins_at_first = np.full(n, -1)
        st.balance_at_first = np.full(n, np.nan)
        st.paid = np.zeros(n, bool)
        st.cash_prev = z()
        st.paid_prev = z()
        st.gate_prev = {g: np.zeros(n, bool) for g in self.GATES}
        st.gate_rise = {g: np.full(n, -1) for g in self.GATES}
        return st

    def session_start(self, st: _State, d: int, trading: np.ndarray, B: np.ndarray, F: np.ndarray) -> None:
        self._set_tier(st, B)

    def room(self, st: _State, cushion: np.ndarray, day_pnl: np.ndarray) -> np.ndarray:
        return self._room(st, cushion, day_pnl)

    def after_trades(self, st: _State, d: int, alive_at_start: np.ndarray, alive: np.ndarray, day_pnl: np.ndarray,
                     B: np.ndarray, F: np.ndarray, trades: np.ndarray) -> None:
        t = self.t
        ex, f = self._book(st, d, alive_at_start, day_pnl, trades, peaks=self.peaks())
        st.first_trade[ex & (st.first_trade < 0)] = d
        if self.peaks():                                                           # A-6: the equity peak (R-c: gross)
            before = B - np.where(ex, day_pnl, 0.0)
            pk = np.where(ex, before + f["peak"], B)
            st.peak_eq = np.maximum(st.peak_eq, np.maximum(pk, B))
        if t.ceiling is not None:                                                  # A-11: the single-day ceiling
            over = alive & (day_pnl > float(t.ceiling) + EPS)
            if over.any():
                excess = day_pnl[over] - float(t.ceiling)
                B[over] -= excess
                st.forfeit[over] += excess
                st.moved_live |= over
                alive &= ~over
                net = day_pnl[over] - excess
                st.exact["forfeit_not_at_ceiling"] += int(np.sum(np.abs(net - float(t.ceiling)) > TOL * float(t.ceiling)))
        if t.inactivity is not None:                                               # A-3
            gone = alive & (st.idle >= int(t.inactivity))
            st.inactive |= gone
            alive &= ~gone

    def funded_floor(self, st: _State, lk: np.ndarray, F: np.ndarray, F_prev: np.ndarray, B: np.ndarray,
                     paid_once: np.ndarray) -> None:
        t = self.t
        if t.floor == "static":                                                    # A-5: never moves
            F[lk] = F_prev[lk]
        elif t.floor == "intraday":                                                # A-6 with U-29's timing
            trail = np.maximum(F_prev, st.peak_eq - float(t.mll))
            capped = np.minimum(float(t.lock), trail)
            use_cap = paid_once if t.lock_timing == "first_payout" else np.ones(st.n, bool)
            F[lk] = np.where(use_cap, capped, trail)[lk]
        elif t.lock_timing == "pro_strict":                                        # U-16 strict: uncapped till paid
            unpaid = lk & ~paid_once
            F[unpaid] = np.maximum(F_prev[unpaid], B[unpaid] - float(t.mll))

    def after_window(self, st: _State, lk: np.ndarray, day_pnl: np.ndarray, win_days: np.ndarray,
                     win_days_total: np.ndarray, w_days: np.ndarray) -> None:
        if self.coin == "costed":                                                  # S-8: an untraded session is no
            w_days[lk & ~st.traded] -= 1                                           # cycle day
        if self.t.request_day_excluded:                                            # A-16
            ex = st.excl_next & lk
            wd = ex & (day_pnl >= float(self.t.winning_day_min) - EPS)
            win_days[wd] -= 1
            win_days_total[wd] -= 1
            st.excl_next[lk] = False

    def funded_gate(self, st: _State, d: int, lk: np.ndarray, day_pnl: np.ndarray, B: np.ndarray, elig: np.ndarray,
                    req: np.ndarray, since_pay: np.ndarray, paid_once: np.ndarray, n_payouts: np.ndarray,
                    win_days: np.ndarray, w_days: np.ndarray, w_profit: np.ndarray, w_best: np.ndarray
                    ) -> tuple[np.ndarray, np.ndarray]:
        t, g = self.t, self.t.gate
        pmin = float(t.payout_min)
        live = lk & ~paid_once                                                     # the gates to the first payout

        def mark(name: str, cond: np.ndarray) -> None:
            self._rise(st, d, name, cond, live)

        if g in ("ts_std", "labs_5wd"):
            mark("winning_days", win_days >= int(t.winning_days))
            return elig, req
        if g == "ts_con":
            mark("cycle_days", w_days >= int(t.cons_min_days))
            mark("cycle_share", (w_profit > 0) & (w_best <= float(t.cons_share) * w_profit + EPS))
            return elig, req
        if g == "lucid":
            mark("winning_days", win_days >= int(t.winning_days))
            mark("profit_since", since_pay >= float(t.since_min) - EPS)
            e = lk & (win_days >= int(t.winning_days)) & (since_pay >= float(t.since_min) - EPS) & \
                (n_payouts < int(t.max_payouts))
            return e, req
        if g == "labs_daily":
            above = np.maximum(B - float(t.buffer), 0.0)
            since_ok = ~paid_once | (since_pay > EPS)
            if t.request == "labs_daily_strict":                                   # U-22 strict: yesterday's profit
                r = np.minimum(np.minimum(st.pending, above), float(t.cap))
                st.pending = np.where(lk, np.maximum(0.0, np.minimum(day_pnl, above)), 0.0)
            else:
                r = np.minimum(above, float(t.cap))
            mark("buffer_min", above >= pmin - EPS)
            return lk & since_ok, r
        first_ok = lk & (st.first_trade >= 0) & (d >= st.first_trade + int(t.wait_first or 0))
        mark("clock", first_ok)
        if g == "mffu_buffer":
            mark("buffer_min", B - float(t.buffer) >= pmin - EPS)
            e = first_ok.copy()
            if t.since_min is not None:
                e &= ~paid_once | (since_pay >= float(t.since_min) - EPS)
            return e, self._request(B)
        if g == "pro_clock":
            gap_ok = ~paid_once | (d >= st.last_req + int(t.wait_between))
            mark("buffer_min", self._request(B) >= pmin - EPS)
            return first_ok & gap_ok, self._request(B)
        if g == "builder":
            first_cycle = ~paid_once
            above = B - float(t.buffer)
            base = np.where(first_cycle, above if t.first_cycle_base == "above_buffer" else w_profit, w_profit)
            share_ok = (base > EPS) & (w_best <= float(t.cycle_share) * base + EPS)
            prof_ok = np.where(first_cycle, above >= float(t.first_profit_above_buffer) - EPS,
                               since_pay >= float(t.since_min) - EPS)
            days_ok = w_days >= int(t.cycle_days)
            mark("cycle_share", share_ok)
            mark("cycle_days", days_ok)
            mark("buffer_min", prof_ok)
            e = first_ok & share_ok & prof_ok & days_ok & (n_payouts < int(t.max_payouts))
            return e, np.maximum(0.0, np.minimum(float(t.cap), above))
        raise ValueError(g)

    def _request(self, B: np.ndarray) -> np.ndarray:
        """9.2's request at U-25's end (`modes_rules.request_amount`, vectorised); U-17's lenient end literal (R-d):
        the quoted share of the balance only while it is inside the buffer."""
        t = self.t
        withdraw = np.maximum(B - float(t.buffer), 0.0)
        if t.within_buffer_share is not None:
            inside = B < float(t.buffer)
            withdraw = np.where(inside, float(t.within_buffer_share) * np.maximum(B, 0.0), withdraw)
        if t.request == "u25_strict":
            return np.maximum(0.0, np.minimum(np.minimum(float(t.frac) * B, self.R.reference_cap()), withdraw))
        if t.request == "u25_lenient":
            return withdraw
        raise ValueError(t.request)

    def after_payouts(self, st: _State, d: int, do: np.ndarray, req: np.ndarray, B: np.ndarray, F: np.ndarray,
                      alive: np.ndarray, n_payouts: np.ndarray, cash: np.ndarray, gross_paid: np.ndarray) -> None:
        t = self.t
        dc, dg = cash - st.cash_prev, gross_paid - st.paid_prev                    # S-3: every net its split
        want_c = np.where(do, float(t.split) * req, 0.0)
        want_g = np.where(do, req, 0.0)
        st.exact["net_not_split"] += int(np.sum(np.abs(dc - want_c) > TOL * np.maximum(1.0, np.abs(want_c))))
        st.exact["paid_not_request"] += int(np.sum(np.abs(dg - want_g) > TOL * np.maximum(1.0, np.abs(want_g))))
        st.cash_prev, st.paid_prev = cash.copy(), gross_paid.copy()
        if not do.any():
            return
        first = do & ~st.paid
        st.balance_at_first[first] = B[first] + req[first]
        st.flip_wins_at_first[first] = st.flip_wins[first]
        st.steady_wins_at_first[first] = st.steady_wins[first]
        st.paid |= do
        st.last_req[do] = d
        bad = do & (req < float(t.payout_min) - EPS)
        if t.cap is not None:
            bad |= do & (req > float(t.cap) + EPS)
        st.exact["request_out_of_bounds"] += int(np.sum(bad))
        if t.request_day_excluded:
            st.excl_next |= do
        if t.max_payouts is not None:                                              # A-11 / A-17: the end by count
            end = do & (n_payouts >= int(t.max_payouts))
            st.count_end |= end
            alive &= ~end

    def outputs(self, st: _State, out: dict[str, Any]) -> dict[str, Any]:
        out = dict(out)
        ended = st.moved_live | st.inactive | st.count_end
        out["alive"] = out["alive"] & ~ended
        cause = np.full(st.n, "", dtype=object)
        nopay = out["first_payout_day"] < 0
        cause[nopay & out["closed"]] = "floor"
        cause[nopay & st.inactive] = "inactivity"
        cause[nopay & st.moved_live] = "moved_to_live"
        cause[nopay & out["alive"]] = "censored"
        self._common_outputs(st, out)
        out.update(moved_live=st.moved_live, forfeit=st.forfeit, inactive=st.inactive, count_end=st.count_end,
                   flip_wins_at_first=st.flip_wins_at_first, steady_wins_at_first=st.steady_wins_at_first,
                   balance_at_first=st.balance_at_first, gate_rise={k: v.copy() for k, v in st.gate_rise.items()},
                   cause=cause, first_trade=st.first_trade)
        return out


# ------------------------------------------------------------------------------------------------ one run

#: S-7: the declared coin streams are drawn only by step 2's `main`, after its refusals cleared
DECLARED_ROLES = ("coin_eval", "coin_funded", "coin_peak")
_DECLARED_STREAMS = {"cleared": False}


def allow_declared_streams(cleared_by: str) -> None:
    """Called only by `scripts/modes_coin.py`'s `main`, after `step_problems(2)` came back empty."""
    if cleared_by != "scripts/modes_coin.py main: step_problems(2) empty":
        raise RuntimeError("only step 2's main clears the declared coin streams (S-7)")
    _DECLARED_STREAMS["cleared"] = True


def stream(role: str, w_index: int, r_index: int) -> np.random.Generator:
    """Section 15's keyed stream: `[seed, w_index, r_index]`, the same for every mode-corner, policy and stop. The
    three declared coin roles refuse unless step 2's refusals cleared (S-7)."""
    if role in DECLARED_ROLES and not _DECLARED_STREAMS["cleared"]:
        raise RuntimeError(f"REFUSED (S-7): the declared stream {role!r} is drawn only by step 2's main, after its "
                           "refusals cleared")
    return np.random.default_rng([M.seed(role), int(w_index), int(r_index)])


def run_eval(spec: EvalSpec, n: int, rng: np.random.Generator, horizon: int | None = None) -> dict[str, Any]:
    """One evaluation run of the coin (9.1): `n` accounts to their resolution or the horizon."""
    hz = int(M.declared("horizon.eval")) if horizon is None else int(horizon)
    draw = spec.draw(rng)
    return simulate_combine(spec.rules(), spec.policy_obj(), 0.0, int(n), rng=rng, draw=draw, max_days=hz, spec=spec)


def run_funded(spec: FundedSpec, n: int, rng: np.random.Generator, peak_rng: np.random.Generator | None = None,
               horizon: int | None = None) -> dict[str, Any]:
    """One funded run of the coin (9.1): `n` accounts from activation to their ending or the horizon."""
    hz = int(M.declared("horizon.funded")) if horizon is None else int(horizon)
    draw = spec.draw(rng, peak_rng)
    return simulate_xfa(spec.rules(), spec.policy_obj(), 0.0, int(n), rng=rng, draw=draw, horizon_days=hz, spec=spec)


def spec_for(m: M.ModeCorner, w: float, r: float, *, policy: str = "steady", coin: str = "gross",
             stop: int | None = None) -> EvalSpec | FundedSpec:
    t = M.mode_corner_terms(m)
    if m.kind == M.EVAL:
        return EvalSpec(t, w, r, policy=policy, coin=coin, stop=stop)
    return FundedSpec(t, w, r, policy=policy, coin=coin, stop=stop)


__all__ = ["VENDORED_SHA256", "MARKER", "check_vendored_sources", "recomposition_problems", "simulate_combine",
           "simulate_xfa", "peak_survival", "peak_inverse", "loss_peak_cdf", "CoinDraw", "SizeTable", "size_table",
           "tier_cap_index", "CostedCoinDraw", "EvalSpec", "FundedSpec", "EXACT", "DECLARED_ROLES",
           "allow_declared_streams", "stream", "run_eval", "run_funded", "spec_for"]
