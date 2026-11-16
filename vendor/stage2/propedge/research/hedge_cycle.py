"""HYPOTHETICAL (D-619): the hedge cycle -- `hypothetical_hedge` in every row, EXPLORATORY, never a candidate.

Cross-account and cross-firm hedging are prohibited -- Topstep 13747047 / 10296582, Lucid 11404734 (tier 1, D-145) --
and that does not change. The operator (2026-11-14) asked for the cycle as if the rule did not exist:

1. **Evaluations at both firms** with P-16's executions (its engine call, S seats a firm), until each firm has passed
   one; the first firm to pass stops buying and trading and its funded account waits.
2. **One hedge**, the session after the later pass: firm A long and firm B short (a seeded coin per cycle) on one
   shared 1:1 bracket, 20 micros a side at a 50-point stop ($2,000, each leg's whole room); the loser is lost at its
   limit and the winner closed at the same price; a bracket that resolves neither way is flattened on both and the
   hedge repeats the next session, the balances carried.
3. **The survivor's flip days**: one of P-16's trades a session at `micros` (the smallest whole-micro count whose
   median winning trade nets the winning-day minimum), stepped through the firm's own funded class (`FundedAccount`,
   `LucidFundedAccount`) until its first payout request, at the maximum the firm allows; then retired. The cycle ends
   at that request (or the survivor's breach) and both firms start new evaluations the next session.

The evaluation phase is an `Episode`: one firm's campaign (the engine's single-firm path) from fresh until its first
pass -- its fees by day and its purchase days -- drawn independently for the two firms from a library the script
builds (`scripts/hedge_cycle.py`; D-619 (4) declares the approximation). This module holds the pieces and the cycle;
it reads no data.

**The static firm** (D-619 (2b), hypothetical): Topstep's contract with the loss floor fixed at the start less the MLL
on the evaluation and the funded account (`static_rules`), checked on the close only (the script's draws settle at
the trade's own outcome), and five days of $150 or more required beside the target to pass the evaluation
(`StaticCombineAccount`); Topstep's Standard path already requires them for a payout.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Any, Callable, ClassVar, Mapping, Sequence

import numpy as np

from propedge.campaign.lockstep import EPS, CombineAccount, FundedAccount

TAG = "hypothetical_hedge"
DECISION = "D-619"
VARIANT_FAMILY = f"{DECISION}:{TAG}"
LABEL = ("HYPOTHETICAL (D-619): hypothetical_hedge -- a cross-firm hedge cycle, prohibited at Topstep (13747047, "
         "10296582) and Lucid (11404734), tier 1; modelled as if the rule did not exist, never a candidate.")
GREEN_DAY_MIN = 150.0                   # D-619 (2b): the static firm's green day ($150 net or more)
GREEN_DAYS = 5                          # ... and the number required to pass its evaluation
HEDGE_MICROS = 20                       # the funded entry allowance at both firms
HEDGE_STOP_TICKS = 200                  # 50 NQ points: 20 MNQ x 200 ticks x $0.50 = $2,000
NO_TRADE = "n"                          # a session without an offered mark


# ------------------------------------------------------------------------------------------------ the static firm


def static_rules(rules: Any) -> Any:
    """The static firm's rules: `rules` with the loss floor fixed at the start less the MLL -- on the evaluation (the
    lock at -MLL holds the floor where it starts) and on the funded account (its start and its lock at -MLL)."""
    m = float(rules.mll)
    return replace(rules, combine_mll_lock_at=-m, xfa_mll_start=-m, xfa_lock_at=-m)


@dataclass
class StaticCombineAccount(CombineAccount):
    """An evaluation that also needs `GREEN_DAYS` days of `GREEN_DAY_MIN` or more beside the target to pass: a day's
    close at the target without them is not a pass, and the account trades on."""

    GREEN_DAYS: ClassVar[int] = GREEN_DAYS
    GREEN_DAY_MIN: ClassVar[float] = GREEN_DAY_MIN
    green_days: int = 0

    def trade_day(self, rules: Any, policy: Any, rel_day: int, calendar_day: int,
                  ledger: list[dict[str, Any]] | None = None, need_aware: bool = False,
                  consistency_cap: bool = False) -> None:
        super().trade_day(rules, policy, rel_day, calendar_day, ledger=ledger, need_aware=need_aware,
                          consistency_cap=consistency_cap)
        if self.failed:
            return
        if self.last_day_pnl >= self.GREEN_DAY_MIN - EPS:
            self.green_days += 1
        if self.passed and self.green_days < self.GREEN_DAYS:
            self.passed = False
            self.pass_day = -1
            self.resolved_on = None

    def reset(self, calendar_day: int, *, rtp_dll: float | None = None) -> None:
        super().reset(calendar_day, rtp_dll=rtp_dll)
        self.green_days = 0


# ------------------------------------------------------------------------------------------------ the pieces


def survivor_micros(win_per_micro: np.ndarray, bar: float) -> int:
    """The smallest whole-micro count whose median winning trade nets at least `bar`."""
    w = np.asarray(win_per_micro, float)
    w = w[np.isfinite(w) & (w > 0)]
    if not len(w):
        raise ValueError("no winning trade to size the survivor from")
    return int(math.ceil(float(bar) / float(np.median(w)) - 1e-12))


def hedge_winner(long_kind: str, short_kind: str) -> str | None:
    """Which leg of the shared bracket wins: the leg whose target is touched first ('long' / 'short'); the other leg
    is stopped. None when neither leg reaches its target or its stop (flattened, or no trade that session)."""
    lt, st = long_kind == "t", short_kind == "t"
    if lt and st:
        raise ValueError("both legs of one bracket cannot reach their targets")
    if lt or short_kind == "s" and not st:
        return "long" if lt or short_kind == "s" else None
    if st or long_kind == "s":
        return "short"
    return None


@dataclass(frozen=True)
class HedgeDay:
    """One session's hedge on the shared bracket: each leg's exit kind and P&L in dollars at `HEDGE_MICROS`."""

    long_kind: str
    short_kind: str
    long_pnl: float
    short_pnl: float


def bracket_pair(o: Sequence[float | None], h: Sequence[float | None], l: Sequence[float | None],
                 c: Sequence[float | None], t: int, *, stop: float, slip: float, last: int, micros: int,
                 point_value: float, fee_rt: float) -> HedgeDay | None:
    """The hedge's shared bracket on one day's bars (`propedge.outcomes.resolution_core`'s clock and rules; missing
    bars None): both legs enter at the open of the first bar after slot `t`, one tick (`slip`) adverse each; each leg's
    stop `stop` points from its own fill; the first stop touched decides -- the loser out at its stop (at the bar's open
    when it opens through it), the winner closed at that same price, one tick adverse; a bar touching both stops takes
    the one nearer its open first; neither by bar `last` flattens both at the last close, one tick adverse. P&L in
    dollars at `micros` less a round turn each. Kinds: winner 't', loser 's', flattened 'f'. None: no bar to enter."""
    j0 = next((j for j in range(t + 1, last + 1) if o[j] is not None), None)
    if j0 is None:
        return None
    el, es = float(o[j0]) + slip, float(o[j0]) - slip
    sl, ss = el - stop, es + stop

    def usd(g: float) -> float:
        return g * point_value * micros - fee_rt * micros

    close = None
    for j in range(j0, last + 1):
        if o[j] is None:
            continue
        oj = float(o[j])
        up = float(h[j]) >= ss - 1e-12 or (j != j0 and oj >= ss)
        dn = float(l[j]) <= sl + 1e-12 or (j != j0 and oj <= sl)
        if up and dn:
            up, dn = (True, False) if (ss - oj) <= (oj - sl) else (False, True)
        if up:
            fill = max(ss, oj) if j != j0 else ss
            return HedgeDay("t", "s", usd((fill - slip) - el), usd(es - fill))
        if dn:
            fill = min(sl, oj) if j != j0 else sl
            return HedgeDay("s", "t", usd(fill - el), usd(es - (fill + slip)))
        close = float(c[j])
    return HedgeDay("f", "f", usd((close - slip) - el), usd(es - (close + slip)))


def survivor_policy(protocol: Any) -> Any:
    """The survivor's funded policy: the protocol's, one trade a session, the Standard path, the whole allowed request."""
    return replace(protocol.funded_policy(), trades_per_day=1, payout_path="standard", payout_frac=1.0,
                   keep_balance=0.0, stop_day_on_win=False, stop_day_on_loss=False)


def topstep_timing() -> str:
    from propedge.campaign.lockstep import DEFAULT_PAYOUT_TIMING

    return DEFAULT_PAYOUT_TIMING


class _StreamDraw:
    """The survivor's trades, one a session: the session's P&L from `pnls` (NaN: no trade), extended by `more()`."""

    settlement = "final"                 # already settled: the bracket's own outcome (D-156's scripted stream)

    def __init__(self, pnls: Sequence[float], more: Callable[[], float] | None = None):
        self.pnls = [float(x) for x in pnls]
        self.more = more
        self.last_trade = None

    def __call__(self, n: int, rel_day: int, slot: int, room: np.ndarray, **_: Any) -> np.ndarray:
        if slot > 0:
            return np.array([np.nan])
        while rel_day >= len(self.pnls) and self.more is not None:
            self.pnls.append(float(self.more()))
        return np.array([self.pnls[rel_day] if rel_day < len(self.pnls) else np.nan])


@dataclass(frozen=True)
class SurvivorOutcome:
    requested: bool
    request_day: int | None
    net: float
    breached: bool
    sessions: int


def run_survivor(funded_cls: type, rules: Any, policy: Any, *, cap: float, activation_day: int,
                 pnls: Sequence[float], payout_timing: str, more: Callable[[], float] | None = None,
                 max_sessions: int | None = None) -> SurvivorOutcome:
    """The survivor through its firm's own funded class from its first session (`activation_day`, the first hedge
    session): one session a calendar day, until its first payout request (`requested`), its breach, or the sessions
    run out (`max_sessions`, else the stream's length)."""
    draw = _StreamDraw(pnls, more)
    acc = funded_cls(index=0, activation_day=int(activation_day), draw=draw, horizon_days=10**9,
                     floor_start=float(rules.xfa_mll_start), payout_timing=payout_timing)
    n = int(max_sessions) if max_sessions is not None else len(draw.pnls)
    for k in range(n):
        net = acc.trade_day(rules, policy, float(cap), k, int(activation_day) + k)
        if net is not None:
            return SurvivorOutcome(True, int(activation_day) + k, float(net), False, k + 1)
        if acc.closed:
            return SurvivorOutcome(False, int(activation_day) + k, 0.0, True, k + 1)
    return SurvivorOutcome(False, None, 0.0, False, n)


# ------------------------------------------------------------------------------------------------ the cycle


@dataclass(frozen=True)
class Episode:
    """One firm's evaluation phase from fresh: the day of its first pass (None: none within the episode), the fee paid
    on each day from day 0 to the pass (or the episode's end), and the days evaluations were bought."""

    pass_day: int | None
    fees: np.ndarray
    purchase_days: tuple[int, ...]


def episode_of(lp: Any, initial: float) -> Episode:
    """An `Episode` from one single-firm `LockstepPath`: the first pass (its close's calendar day), the cash spent each
    day up to it, and the purchases made by then. Refuses a path whose cash rose before its first pass (nothing but
    fees can move it then)."""
    passes = [int(c.resolved_on) for c in lp.combines if c.passed and c.resolved_on is not None]
    first = min(passes) if passes else None
    cash = np.asarray(lp.path.cash_series, float)
    end = first if first is not None else len(cash) - 1
    seg = np.r_[float(initial), cash[:end + 1]]
    fees = -np.diff(seg)
    if (fees < -1e-6).any():
        raise ValueError("an episode's cash rose before its first pass")
    return Episode(pass_day=first, fees=np.clip(fees, 0.0, None),
                   purchase_days=tuple(int(c.purchase_day) for c in lp.combines if int(c.purchase_day) <= end))


@dataclass(frozen=True)
class FirmModel:
    """One firm's side of the cycle: its funded contract for the survivor, its activation fee and payout lag, and the
    survivor's size in micros."""

    name: str
    rules: Any
    policy: Any
    cap: float
    funded_cls: type
    payout_timing: str
    lag_days: int
    activation: float
    micros: int


def simulate_path(*, seed: int, horizon: int, firms: tuple[FirmModel, FirmModel],
                  libraries: tuple[Sequence[Episode], Sequence[Episode]], hedge_days: Sequence[HedgeDay | None],
                  survivor_per_micro: np.ndarray, max_cycles: int | None = None,
                  hedge_order: Sequence[int] | None = None) -> dict[str, Any]:
    """One path of `horizon` sessions: cycles until the horizon (or `max_cycles`). Days are calendar sessions from 0;
    every draw from `seed`'s stream. `hedge_days` and `survivor_per_micro` are the session tables a hedge and a
    survivor trade are drawn from (uniformly; `hedge_order` gives the hedge's draws in order, for tests). Returns the
    path's cash flows by day and its events."""
    rng = np.random.default_rng(int(seed))
    H = int(horizon)
    flows = np.zeros(H)
    out: dict[str, Any] = {"payout_days": [], "request_days": [], "payout_nets": [], "hedge_days": [],
                           "hedge_flat_sessions": 0, "evaluations": 0, "funded_lost": 0, "survivor_breaches": 0,
                           "cycles_started": 0, "first_pass_days": [], "second_pass_days": []}
    order = iter(hedge_order) if hedge_order is not None else None
    surv = np.asarray(survivor_per_micro, float)
    t = 0
    while t < H and (max_cycles is None or out["cycles_started"] < int(max_cycles)):
        out["cycles_started"] += 1
        passes: list[int | None] = []
        for f in (0, 1):
            lib = libraries[f]
            T, p = t, None
            while T < H:
                e = lib[int(rng.integers(len(lib)))]
                for k, fee in enumerate(e.fees):
                    if T + k < H:
                        flows[T + k] -= float(fee)
                out["evaluations"] += sum(1 for d in e.purchase_days if T + d < H)
                if e.pass_day is not None:
                    p = T + int(e.pass_day)
                    break
                T += len(e.fees)
            passes.append(p if p is not None and p < H else None)
        if any(p is None for p in passes):
            break
        for f in (0, 1):
            if passes[f] + 1 < H:
                flows[passes[f] + 1] -= float(firms[f].activation)
        out["first_pass_days"].append(min(passes))
        out["second_pass_days"].append(max(passes))
        h0 = max(passes) + 1
        h = h0
        pre: list[list[float]] = [[], []]
        winner = None
        win_pnl = float("nan")
        while h < H:
            hd = hedge_days[next(order)] if order is not None else hedge_days[int(rng.integers(len(hedge_days)))]
            long_firm = int(rng.integers(2))
            w = None if hd is None else hedge_winner(hd.long_kind, hd.short_kind)
            if w is None:
                lp_, sp_ = (np.nan, np.nan) if hd is None else (hd.long_pnl, hd.short_pnl)
                pre[long_firm].append(float(lp_))
                pre[1 - long_firm].append(float(sp_))
                if hd is not None and hd.long_kind != NO_TRADE:
                    out["hedge_flat_sessions"] += 1
                h += 1
                continue
            winner = long_firm if w == "long" else 1 - long_firm
            win_pnl = float(hd.long_pnl if w == "long" else hd.short_pnl)
            break
        if winner is None:
            break
        out["hedge_days"].append(h)
        out["funded_lost"] += 1
        fm = firms[winner]

        def more(fm=fm) -> float:
            return float(surv[int(rng.integers(len(surv)))]) * fm.micros

        res = run_survivor(fm.funded_cls, fm.rules, fm.policy, cap=fm.cap, activation_day=h0,
                           pnls=pre[winner] + [win_pnl], payout_timing=fm.payout_timing, more=more,
                           max_sessions=H - h0)
        if res.requested:
            arrival = int(res.request_day) + int(fm.lag_days)
            out["request_days"].append(int(res.request_day))
            if arrival < H:
                flows[arrival] += float(res.net)
                out["payout_days"].append(arrival)
                out["payout_nets"].append(float(res.net))
            t = int(res.request_day) + 1
        elif res.breached:
            out["funded_lost"] += 1
            out["survivor_breaches"] += 1
            t = int(res.request_day) + 1
        else:
            break
    out["flows"] = flows
    out["fees"] = float(-flows[flows < 0].sum())
    return out


# ------------------------------------------------------------------------------------------------ the readings


def _pct(x: Sequence[float], q: float) -> float:
    from propedge.campaign.portfolio import _pct as pct

    return pct(list(map(float, x)), q)


def readings(recs: Sequence[Mapping[str, Any]], *, horizon: int, margin: float, block: int = 21) -> dict[str, Any]:
    """D-619 (6)'s measures over the paths of one cell and arm. A path without a payout counts its upfront bankroll over
    the whole horizon and its days to a first payout as the horizon; a path with fewer than two payouts counts its gap
    between payouts as the horizon (D-619 (7))."""
    from propedge.campaign.portfolio import path_measures

    H = int(horizon)
    upfront, required, first, per_month, gaps, empty, net = [], [], [], [], [], [], []
    for r in recs:
        c = np.cumsum(np.asarray(r["flows"], float))
        pays = sorted(int(d) for d in r["payout_days"])
        until = pays[0] if pays else len(c) - 1
        upfront.append(max(0.0, -float(c[:until + 1].min())) + margin)
        required.append(max(0.0, -float(c.min())) + margin)
        first.append(pays[0] if pays else H)
        per_month.append(len(pays) / (H / block))
        g = list(np.diff(pays)) if len(pays) >= 2 else [H]
        gaps.extend(int(x) for x in g)
        nb = H // block
        empty.append(sum(1 for i in range(nb) if not any(i * block <= d < (i + 1) * block for d in pays)) / nb)
        net.append(float(c[-1]))
    base = _pct(required, 90)
    growth = [path_measures(np.cumsum(np.asarray(r["flows"], float)), 0.0, base, float(r["fees"]),
                            float(sum(r["payout_nets"])), None)["growth_on_base"] for r in recs]
    n_pay = sum(len(r["payout_days"]) for r in recs)
    ev = sum(int(r["evaluations"]) for r in recs)
    lost = sum(int(r["funded_lost"]) for r in recs)
    fees = sum(float(r["fees"]) for r in recs)
    return {
        "paths": len(recs),
        "upfront_to_first_payout_p50": _pct(upfront, 50), "upfront_to_first_payout_p90": _pct(upfront, 90),
        "upfront_to_first_payout_p99": _pct(upfront, 99),
        "required_p50": _pct(required, 50), "required_p90": base,
        "days_to_first_payout_p50": _pct(first, 50), "days_to_first_payout_p90": _pct(first, 90),
        "share_paths_no_payout": float(np.mean([len(r["payout_days"]) == 0 for r in recs])),
        "payouts_per_month_p50": _pct(per_month, 50), "payouts_per_month_p10": _pct(per_month, 10),
        "payouts_mean": n_pay / len(recs) if recs else float("nan"),
        "gap_p50": _pct(gaps, 50), "gap_p90": _pct(gaps, 90), "gap_max": float(max(gaps)) if gaps else float("nan"),
        "share_months_no_payout": float(np.mean(empty)),
        "net_p50": _pct(net, 50), "net_p10": _pct(net, 10),
        "growth_on_required_p50": _pct(growth, 50), "growth_on_required_p10": _pct(growth, 10),
        "evaluations_per_payout": ev / n_pay if n_pay else float("nan"),
        "funded_lost_per_payout": lost / n_pay if n_pay else float("nan"),
        "fees_per_payout": fees / n_pay if n_pay else float("nan"),
        "hedge_flat_sessions_mean": float(np.mean([r.get("hedge_flat_sessions", 0) for r in recs])),
        "survivor_breaches_mean": float(np.mean([r.get("survivor_breaches", 0) for r in recs])),
    }


def frontier(rows: Sequence[Mapping[str, Any]], x: str, y: str) -> list[int]:
    """Indices of the rows on the frontier of `x` against `y`, both smaller-is-better (no other row at or below both,
    below in one)."""
    out = []
    for i, a in enumerate(rows):
        if not any((b[x] <= a[x] and b[y] <= a[y]) and (b[x] < a[x] or b[y] < a[y]) for j, b in enumerate(rows) if j != i):
            out.append(i)
    return out


def ranking(rows: Sequence[Mapping[str, Any]], *, tolerance: float = 0.10) -> dict[str, Any]:
    """D-619 (7): the most consistent rows (p90 gap within `tolerance` of the smallest) and, of them, the one with the
    smallest p90 upfront bankroll to the first payout; the frontier of that bankroll against the p90 gap."""
    best_gap = min(float(r["gap_p90"]) for r in rows)
    near = [i for i, r in enumerate(rows) if float(r["gap_p90"]) <= (1.0 + tolerance) * best_gap + EPS]
    named = min(near, key=lambda i: (float(rows[i]["upfront_to_first_payout_p90"]), float(rows[i]["gap_p90"])))
    return {"best_gap_p90": best_gap, "within_tolerance": near, "named": named,
            "frontier": frontier(rows, "upfront_to_first_payout_p90", "gap_p90")}


__all__ = ["TAG", "DECISION", "VARIANT_FAMILY", "LABEL", "GREEN_DAY_MIN", "GREEN_DAYS", "HEDGE_MICROS",
           "HEDGE_STOP_TICKS", "NO_TRADE", "static_rules", "StaticCombineAccount", "survivor_micros", "hedge_winner",
           "HedgeDay", "survivor_policy", "topstep_timing", "SurvivorOutcome", "run_survivor", "Episode", "episode_of",
           "FirmModel", "simulate_path", "readings", "frontier", "ranking"]
