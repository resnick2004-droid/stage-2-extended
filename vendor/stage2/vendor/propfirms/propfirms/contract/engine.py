"""Generalised funded-side contract engine — T4c (docs/T4_ENGINE_FIT.md §2).

The vendored stage-one engine models Topstep's funded mechanics; the other firms'
funded sides differ in ways that are not `Rules(...)` parameter changes (payout
cycles and gates, finite lifetimes, static floors, daily loss guards, profit caps,
rolling payout caps). This module is the new code the research protocol §4 calls
for: one vectorized simulator over a `FundedConfig`, per-firm configs built from
verified spec rows only, validated by golden paths from the rule text, by exact
degenerate agreement with the vendored XFA engine under Topstep's configuration,
and by the T3 ceilings as oracles (D-13).

Evaluation side: nothing is needed here — all five evals map onto the vendored
Combine engine via `propfirms.contract.evals.eval_rules` (T4b).

Deliberately NOT implemented yet, refusing loudly rather than guessing:

* `floor_mode="intraday_trail"` (MFFU Rapid funded): the floor follows the intraday
  equity high-water mark including unrealized gains, so the state updates inside the
  trade; the binary-trade model needs the maximum-favorable-excursion law (the
  mirror of stage one's MAE law) derived and tested first.
* MFFU's funded payout sizing: its `payout_cap` and `payout_balance_consequence`
  rows are open (H-6) — the request size and post-payout state cannot be coded from
  verified rules.

Conventions (stage one's): cumulative-P&L frame, start = 0; binary trades resolved
at the labelled risk with intraday liquidation at the nearest barrier (floor or
remaining daily-loss room) as a fair barrier race; the floor LEVEL ratchets at the
day close for EOD-trailing modes while the breach test is continuous; payouts are
checked at the day close. Fees are not charged here (several `payout_fee` rows are
open, H-6); T5's EV accounting owns fees.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Any

import numpy as np

from propfirms.contract.adapter import (
    Policy, RandomDraw, Rules, p_race, theta_from_edge,
)
from propfirms.spec import FirmSpec

EPS = 1e-9

#: Sentinel a `risk_fn` returns to bet the entire current room (floor- and
#: DLL-limited): the full-risk fair trade, win +rr*room with p = (1+e)/(1+rr).
ALL_IN = float("inf")

#: BluSky's between-requests gate is verified as "one meaningful profitable day"
#: (16300846) while the sibling article words it "a trade in between payouts of
#: $500 or more" (12292284) — conflict on file (ledger §E). Until resolved, the
#: winning-day threshold is a labelled bracket, never a silent default.
BLUSKY_WINDAY_BRACKET: tuple[float, ...] = (1.0, 500.0)

_UNSET = object()


class FundedFitError(ValueError):
    """A verified rule value did not parse the way the fit expects, or the firm's
    funded mechanics are blocked on open rows / missing mechanics."""


def _require(pattern: str, text: str, where: str) -> re.Match[str]:
    m = re.search(pattern, str(text))
    if m is None:
        raise FundedFitError(f"pattern {pattern!r} not found in {where}: {text!r}")
    return m


@dataclass(frozen=True)
class FundedConfig:
    """Everything the funded simulator needs; built per firm from verified rows."""

    floor_start: float                       # initial floor, relative to start (< 0)
    floor_mode: str                          # "eod_trail" | "static" | "intraday_trail"
    trail_amount: float | None = None        # floor = max(floor, B - trail) at close
    lock_at: float | None = None             # ceiling on the trailing floor
    floor_on_payout: str = "unchanged"       # "jump_to_lock" | "unchanged"
    # day mechanics
    daily_loss_limit: float | None = None    # soft stop: day locks at -DLL (barrier)
    profit_stop_day: float | None = None     # stop trading for the day at +cap
    profit_stop_week: float | None = None    # stop trading for the week at +cap
    week_len: int = 5                        # trading days per "week"
    # payout eligibility (checked at day close, vendored ordering)
    winning_day_min: float | None = None
    winning_days_required: int = 0           # per cycle (reset on payout)
    cycle_net_min: float | None = None       # net P&L since last payout
    consistency_since_payout_frac: float | None = None  # best day <= frac * net
    requests_per_month_max: int | None = None
    month_len: int = 21                      # trading days per "month" block
    buffer_before_first_payout: float | None = None  # balance gate, first payout only
    # request sizing
    payout_frac_of_profit: float | None = 0.5  # None = all profit above start
    request_cap: float | None = None
    withdrawable_floor: float | None = None  # requests may not take B below this
    rolling_cap: float | None = None         # max gross paid per rolling window
    rolling_cap_days: int = 5
    payout_min: float = 0.0
    split: float = 1.0
    # terminators
    max_payouts: int | None = None
    total_profit_cap: float | None = None    # B + gross paid >= cap -> concluded


def simulate_funded(
    config: FundedConfig,
    policy: Policy,
    edge: float,
    n: int,
    *,
    seed: int,
    draw: Any | None = None,
    risk_fn: Any | None = None,
    horizon_days: int = 250,
    horizon_per_account: Any | None = None,
) -> dict:
    """Run `n` funded accounts in lockstep under `config`. Seed required, never
    defaulted. Mirrors the vendored XFA loop's ordering so the Topstep-shaped
    degenerate case agrees exactly (tests enforce it).

    `risk_fn(day, B, F, wins, n_payouts) -> risk array` makes the $-risk a
    function of account state (T5c, D-14): entries equal to `ALL_IN` bet the
    whole current room (the full-risk fair trade, p = (1+e)/(1+rr)); every
    finite entry must equal `policy.risk` (one harvest level per cell — its
    drift parameter is computed once), priced by the same truncate barrier race
    as the static path. One uniform per account per slot either way, so
    `risk_fn=lambda *...: full(n, policy.risk)` is bitwise-identical to the
    static run (test-enforced).
    """
    if config.floor_mode == "intraday_trail":
        raise NotImplementedError(
            "intraday-trailing floor needs the MFE excursion law (T4c, "
            "docs/T4_ENGINE_FIT.md §2) — not modelled yet, deliberately."
        )
    if config.floor_mode not in ("eod_trail", "static"):
        raise FundedFitError(f"unknown floor_mode {config.floor_mode!r}")
    if n <= 0:
        raise ValueError("n must be positive")
    if risk_fn is not None and draw is not None:
        raise ValueError("pass draw or risk_fn, not both")

    rng = np.random.default_rng(seed)
    if draw is None and risk_fn is None:
        draw = RandomDraw(policy, edge, rng, "truncate", Rules().edge_mode)
    if risk_fn is not None:
        p_allin = policy.p_win(edge)
        win_h = policy.rr * policy.risk
        theta_h = theta_from_edge(policy.risk, win_h, edge)
    hz = (np.full(n, horizon_days) if horizon_per_account is None
          else np.asarray(horizon_per_account))

    B = np.zeros(n)
    wins = np.zeros(n, int)
    F = np.full(n, config.floor_start)
    alive = np.ones(n, bool)
    closed = np.zeros(n, bool)      # breached the floor
    concluded = np.zeros(n, bool)   # hit a terminator (moved live / concluded / review)
    days = np.zeros(n, int)
    trades = np.zeros(n, int)
    cash = np.zeros(n)
    gross_paid = np.zeros(n)
    n_payouts = np.zeros(n, int)
    first_payout_day = np.full(n, -1)
    win_days = np.zeros(n, int)
    cycle_net = np.zeros(n)
    cycle_best = np.zeros(n)
    week_pnl = np.zeros(n)
    week_locked = np.zeros(n, bool)
    month_requests = np.zeros(n, int)
    paid_window = np.zeros((n, max(config.rolling_cap_days, 1)))

    for d in range(int(hz.max())):
        if d % config.week_len == 0:
            week_pnl[:] = 0.0
            week_locked[:] = False
        if config.requests_per_month_max is not None and d % config.month_len == 0:
            month_requests[:] = 0
        if config.rolling_cap is not None:
            paid_window[:, d % config.rolling_cap_days] = 0.0

        trading = alive & ~concluded & (d < hz)
        if not trading.any():
            break
        alive_at_start = trading.copy()
        active = trading & ~week_locked
        day_pnl = np.zeros(n)

        for t in range(policy.trades_per_day):
            if not active.any():
                break
            room = B - F
            if config.daily_loss_limit is not None:
                room = np.minimum(room, config.daily_loss_limit + day_pnl)
            if risk_fn is None:
                pnl = draw(n, d, t, room)
            else:
                risk = np.asarray(risk_fn(d, B, F, wins, n_payouts), dtype=float)
                allin = ~np.isfinite(risk)
                if np.any(~allin & (risk != policy.risk)):
                    raise ValueError(
                        "risk_fn finite entries must equal policy.risk (one "
                        "harvest level per cell; its drift parameter is fixed)")
                u = rng.random(n)
                room_pos = np.maximum(room, 0.0)
                pnl = np.empty(n)
                # all-in: the full-risk fair trade at the current room
                pnl[allin] = np.where(u[allin] < p_allin,
                                      policy.rr * room_pos[allin],
                                      -room_pos[allin])
                fixed = ~allin
                c = np.minimum(policy.risk, room_pos[fixed])
                pf = p_race(c, win_h, theta_h)
                pnl[fixed] = np.where(u[fixed] < pf, win_h, -c)
            pnl = np.maximum(pnl, -room)  # liquidation at the nearest barrier
            act = active & ~np.isnan(pnl)
            B[act] += pnl[act]
            wins[act & (pnl > 0)] += 1
            day_pnl[act] += pnl[act]
            trades[act] += 1
            breach = act & (B <= F + EPS)
            closed |= breach
            alive &= ~breach
            active &= ~breach
            if config.daily_loss_limit is not None:
                active &= ~(act & (day_pnl <= -config.daily_loss_limit + EPS))
            if config.profit_stop_day is not None:
                active &= ~(act & (day_pnl >= config.profit_stop_day - EPS))
            if config.profit_stop_week is not None:
                active &= ~(act & (week_pnl + day_pnl
                                   >= config.profit_stop_week - EPS))
            if policy.stop_day_on_win:
                active &= ~(act & (pnl > 0))
            if policy.stop_day_on_loss:
                active &= ~(act & (pnl < 0))

        # day close (vendored ordering: days, floor, window bookkeeping, payout)
        days[alive_at_start] += 1
        lk = alive & alive_at_start
        if config.floor_mode == "eod_trail":
            newF = np.maximum(F[lk], B[lk] - config.trail_amount)
            if config.lock_at is not None:
                newF = np.minimum(config.lock_at, newF)
            F[lk] = newF
        week_pnl[lk] += day_pnl[lk]
        if config.profit_stop_week is not None:
            week_locked |= lk & (week_pnl >= config.profit_stop_week - EPS)
        if config.winning_day_min is not None:
            win_days[lk & (day_pnl >= config.winning_day_min - EPS)] += 1
        cycle_net[lk] += day_pnl[lk]
        cycle_best[lk] = np.maximum(cycle_best[lk], day_pnl[lk])

        elig = lk.copy()
        if config.winning_days_required:
            elig &= win_days >= config.winning_days_required
        if config.cycle_net_min is not None:
            elig &= cycle_net >= config.cycle_net_min - EPS
        if config.consistency_since_payout_frac is not None:
            elig &= (cycle_net > EPS) & (
                cycle_best <= config.consistency_since_payout_frac * cycle_net + EPS)
        if config.requests_per_month_max is not None:
            elig &= month_requests < config.requests_per_month_max
        if config.max_payouts is not None:
            elig &= n_payouts < config.max_payouts
        if config.buffer_before_first_payout is not None:
            elig &= (n_payouts > 0) | (
                B >= config.buffer_before_first_payout - EPS)

        allowed = B.copy() if config.payout_frac_of_profit is None \
            else config.payout_frac_of_profit * B
        if config.request_cap is not None:
            allowed = np.minimum(allowed, config.request_cap)
        if config.withdrawable_floor is not None:
            allowed = np.minimum(allowed, B - config.withdrawable_floor)
        if config.rolling_cap is not None:
            allowed = np.minimum(
                allowed, config.rolling_cap - paid_window.sum(axis=1))
        req = policy.payout_frac * allowed
        if policy.keep_balance > 0:
            req = np.minimum(req, np.maximum(B - policy.keep_balance, 0.0))
        do = elig & (req >= config.payout_min - EPS) & (req > EPS)
        if do.any():
            q = req[do]
            B[do] -= q
            gross_paid[do] += q
            cash[do] += config.split * q
            n_payouts[do] += 1
            first = do & (first_payout_day < 0)
            first_payout_day[first] = d
            if config.rolling_cap is not None:
                paid_window[do, d % config.rolling_cap_days] += q
            if config.requests_per_month_max is not None:
                month_requests[do] += 1
            if config.floor_on_payout == "jump_to_lock":
                F[do] = np.maximum(F[do], config.lock_at)
            win_days[do] = 0
            cycle_net[do] = 0.0
            cycle_best[do] = 0.0
            if config.max_payouts is not None:
                concluded |= do & (n_payouts >= config.max_payouts)

        if config.total_profit_cap is not None:
            concluded |= lk & (B + gross_paid >= config.total_profit_cap - EPS)

    return dict(
        closed=closed, concluded=concluded, alive=alive & ~concluded,
        days=days, trades=trades, cash=cash, gross_paid=gross_paid,
        n_payouts=n_payouts, first_payout_day=first_payout_day, B=B, F=F,
        seed=int(seed),
    )


def summarize_funded(res: dict) -> dict:
    fp = res["first_payout_day"]
    got = fp >= 0
    n = len(fp)
    g = res["gross_paid"]
    return dict(
        p_any_payout=got.mean(),
        mean_cash=res["cash"].mean(),
        mean_gross=g.mean(),
        mean_gross_se=g.std(ddof=1) / np.sqrt(n) if n > 1 else np.nan,
        max_gross=g.max(),
        mean_n_payouts=res["n_payouts"].mean(),
        mean_days_to_first_payout=fp[got].mean() if got.any() else np.nan,
        p_closed=res["closed"].mean(),
        p_concluded=res["concluded"].mean(),
        mean_days_alive=res["days"].mean(),
        mean_T=(res["B"] + g).mean(),  # martingale check: <= 0 at edge 0
    )


# ----------------------------------------------------------- per-firm configs

def topstep_reference_config() -> FundedConfig:
    """The vendored XFA (standard path) as a FundedConfig — the degenerate case
    where this engine must agree with `vendor/propsim` exactly (tests enforce)."""
    r = Rules()
    return FundedConfig(
        floor_start=r.xfa_mll_start, floor_mode="eod_trail", trail_amount=r.mll,
        lock_at=r.xfa_lock_at, floor_on_payout="jump_to_lock",
        winning_day_min=r.std_winning_day_min,
        winning_days_required=r.std_winning_days,
        payout_frac_of_profit=r.payout_max_frac_of_balance,
        request_cap=r.std_cap, payout_min=r.payout_min, split=r.profit_split,
    )


def funded_config(
    slug: str,
    *,
    blusky_winning_day_min: float | object = _UNSET,
) -> tuple[FundedConfig, dict[str, Any]]:
    """One firm's FundedConfig from its verified rows, plus the assumptions/
    provenance record for result manifests. Raises for firms whose funded side is
    blocked (MFFU) rather than guessing."""
    spec = FirmSpec.load(slug)
    prov = spec.provenance()
    assumptions = [
        "payouts checked/executed at day close; fees charged in T5 accounting, "
        "not here (open payout_fee rows, H-6)",
    ]

    if slug == "my-funded-futures":
        raise FundedFitError(
            "MFFU Rapid (intraday) is out of the modelling set per D-18 — the "
            "operator dropped intraday-drawdown variants; the modelled MFFU row is "
            "'my-funded-futures-rapid-eod' (D-17). The intraday mechanic is parked "
            "(PARKING_LOT.md); its payout rows also remain open H-6."
        )

    if slug == "my-funded-futures-rapid-eod":
        # D-17/D-18: the modelled MFFU row. EOD trail locking at start+$100; the
        # verified $2,100 realized buffer gates the first payout (and implies the
        # floor has locked by then, so the open payout_balance_consequence row is
        # not an input); afterwards each payout unlocks at $500 net since the last;
        # the request cap is verified as explicitly none — the $100 locked floor is
        # the only sizing limit.
        trail = float(spec.value("funded_drawdown_amount"))
        lock = float(_require(r"locks_at_start_plus_(\d+)",
                              spec.value("funded_drawdown_type"),
                              "rapid-eod funded_drawdown_type").group(1))
        gate = str(spec.value("payout_frequency_gate"))
        buffer_usd = float(_require(r"buffer_(\d+)_realized", gate,
                                    "rapid-eod gate").group(1))
        cycle_min = float(_require(r"then_(\d+)_net_since_last_payout", gate,
                                   "rapid-eod gate").group(1))
        if str(spec.value("payout_cap")) != "none":
            raise FundedFitError(
                "rapid-eod payout_cap is no longer the verified 'none' — refit")
        if buffer_usd < lock + trail:
            raise FundedFitError(
                "rapid-eod buffer no longer covers the lock trigger — the "
                "floor-locked-before-first-payout argument fails; refit")
        cfg = FundedConfig(
            floor_start=-trail, floor_mode="eod_trail", trail_amount=trail,
            lock_at=lock, floor_on_payout="unchanged",
            cycle_net_min=cycle_min,
            buffer_before_first_payout=buffer_usd,
            payout_frac_of_profit=None, request_cap=None,
            withdrawable_floor=lock,
            payout_min=float(spec.value("payout_min")),
            split=float(spec.value("payout_split")),
        )
        assumptions += [
            "floor_on_payout 'unchanged' is exact, not assumed loosely: the $2,100 "
            "buffer means the floor is already locked at start+$100 before any "
            "payout is possible (the open payout_balance_consequence row is not an "
            "input)",
            "the $2,100 realized buffer is modelled as a balance gate at request "
            "time on the first payout",
            "with the cap verified as none, requests are limited only by the $100 "
            "locked floor (withdrawable_floor)",
        ]
        return cfg, {"provenance": prov, "assumptions": assumptions}

    if slug == "lucid-trading":
        trail = float(spec.value("funded_drawdown_amount"))
        lock = float(_require(r"start \+ \$(\d+)",
                              spec.value("payout_balance_consequence"),
                              "lucid payout_balance_consequence").group(1))
        gate = str(spec.value("payout_frequency_gate"))
        cfg = FundedConfig(
            floor_start=-trail, floor_mode="eod_trail", trail_amount=trail,
            lock_at=lock, floor_on_payout="jump_to_lock",
            winning_day_min=float(_require(r"daily profit >= \$(\d+)", gate,
                                           "lucid gate").group(1)),
            winning_days_required=int(_require(r"(\d+) days with", gate,
                                               "lucid gate").group(1)),
            cycle_net_min=float(_require(r"net profit >= \$(\d+)", gate,
                                         "lucid gate").group(1)),
            payout_frac_of_profit=0.5,
            request_cap=float(_require(r"min\(0\.50 \* profits, (\d+)\)",
                                       spec.value("payout_cap"),
                                       "lucid payout_cap").group(1)),
            payout_min=float(spec.value("payout_min")),
            split=float(spec.value("payout_split")),
            max_payouts=int(_require(r"max (\d+) payouts", gate,
                                     "lucid gate").group(1)),
        )
        assumptions.append("'profits' in the 50% request cap read as current "
                           "balance above start (balance is net of prior payouts)")
        return cfg, {"provenance": prov, "assumptions": assumptions}

    if slug == "funded-next":
        trail = float(spec.value("funded_drawdown_amount"))
        lock = float(_require(r"initial_plus_(\d+)",
                              spec.value("payout_balance_consequence"),
                              "funded-next payout_balance_consequence").group(1))
        gate = spec.value("payout_frequency_gate")
        cap = spec.value("payout_cap")
        cfg = FundedConfig(
            floor_start=-trail, floor_mode="eod_trail", trail_amount=trail,
            lock_at=lock, floor_on_payout="jump_to_lock",
            winning_day_min=float(gate["benchmark_day_min_profit_usd"]),
            winning_days_required=int(gate["benchmark_days_per_cycle"]),
            cycle_net_min=float(gate["min_cycle_profit_usd"]),
            payout_frac_of_profit=float(cap["per_cycle_fraction_of_accumulated_profit"]),
            request_cap=float(cap["per_cycle_cap_usd"]),
            payout_min=float(spec.value("payout_min")),
            split=float(spec.value("payout_split")),
            max_payouts=int(gate["lifetime_payout_cycles"]),
        )
        assumptions.append("'accumulated profit' in the 50% cycle cap read as "
                           "current balance above start")
        return cfg, {"provenance": prov, "assumptions": assumptions}

    if slug == "alpha-futures":
        trail = float(spec.value("funded_drawdown_amount"))
        _require(r"balance_reduced_mll_unchanged",
                 spec.value("payout_balance_consequence"),
                 "alpha payout_balance_consequence")
        gate = str(spec.value("payout_frequency_gate"))
        spec.value("payout_cap")  # verified-only gate before reading the note
        cap_note = spec.rules["payout_cap"].note or ""
        cfg = FundedConfig(
            floor_start=-trail, floor_mode="eod_trail", trail_amount=trail,
            lock_at=0.0, floor_on_payout="unchanged",
            daily_loss_limit=float(spec.value("funded_daily_loss_limit")),
            winning_day_min=float(_require(r"of_(\d+)_usd", gate,
                                           "alpha gate").group(1)),
            winning_days_required=int(_require(r"^(\d+)_winning_days", gate,
                                               "alpha gate").group(1)),
            consistency_since_payout_frac=float(
                spec.value("funded_consistency_rule")),
            requests_per_month_max=int(_require(r"up to (\d+) times a month",
                                                cap_note, "alpha payout_cap note"
                                                ).group(1)),
            payout_frac_of_profit=0.5,
            request_cap=float(spec.value("payout_cap")),
            payout_min=float(spec.value("payout_min")),
            split=float(spec.value("payout_split")),
        )
        assumptions += [
            "'up to 50% of the profit in your account' read as current balance "
            "above start (payout_cap note, article 9492051)",
            "calendar month approximated by 21-trading-day blocks for the "
            "4-requests-per-month limit",
            "the $1,000 Daily Loss Guard is modelled as a fair barrier race at the "
            "remaining daily room (soft stop; day locks, account survives)",
        ]
        return cfg, {"provenance": prov, "assumptions": assumptions}

    if slug == "blusky":
        if blusky_winning_day_min is _UNSET:
            raise FundedFitError(
                "BluSky's between-requests winning-day threshold has two official "
                "wordings on file (ledger §E): pass blusky_winning_day_min "
                f"explicitly, one of BLUSKY_WINDAY_BRACKET {BLUSKY_WINDAY_BRACKET}, "
                "and label the choice in the result's parameters."
            )
        if blusky_winning_day_min not in BLUSKY_WINDAY_BRACKET:
            raise FundedFitError(
                f"blusky_winning_day_min={blusky_winning_day_min!r} not in the "
                f"labelled bracket {BLUSKY_WINDAY_BRACKET}")
        cushion = float(spec.value("funded_drawdown_amount"))
        _require(r"static floor 100 unchanged",
                 spec.value("payout_balance_consequence"),
                 "blusky payout_balance_consequence")
        cons = str(spec.value("funded_consistency_rule"))
        day_cap = float(_require(r"profit caps (\d+)/day", cons,
                                 "blusky funded_consistency_rule").group(1))
        week_cap = float(_require(r"(\d+)/week", cons,
                                  "blusky funded_consistency_rule").group(1))
        spec.value("funded_type")  # verified-only gate before reading the note
        total_cap = float(_require(
            r"reaches \$([\d,]+), you must stop trading",
            spec.rules["funded_type"].note or "", "blusky funded_type note"
        ).group(1).replace(",", ""))
        cfg = FundedConfig(
            floor_start=-cushion, floor_mode="static",
            floor_on_payout="unchanged",
            profit_stop_day=day_cap, profit_stop_week=week_cap,
            winning_day_min=float(blusky_winning_day_min),  # type: ignore[arg-type]
            winning_days_required=1,
            payout_frac_of_profit=None,  # any balance above start
            rolling_cap=float(spec.value("payout_cap")), rolling_cap_days=5,
            payout_min=float(spec.value("payout_min")),
            split=float(spec.value("payout_split")),
            total_profit_cap=total_cap,
        )
        assumptions += [
            f"between-requests winning-day threshold: labelled bracket value "
            f"${blusky_winning_day_min} of {BLUSKY_WINDAY_BRACKET} (official "
            "wordings conflict, ledger §E)",
            "rolling 7-calendar-day payout cap approximated by 5 trading days; "
            "'week' profit cap by 5-trading-day blocks",
            "at the $10,000 total-profit conclusion, undistributed balance is NOT "
            "credited (Brokerage Review outcome out of scope; forfeiture on denial "
            "is the recorded risk, D-11)",
        ]
        return cfg, {"provenance": prov, "assumptions": assumptions}

    raise KeyError(f"unknown firm {slug!r}")


def simulate_eval(*args: Any, **kwargs: Any) -> dict:
    """Evals need no new engine: all five firms map onto the vendored Combine
    engine. Build the Rules with `propfirms.contract.evals.eval_rules` and run
    `propfirms.contract.adapter.run_combine` (T4b, docs/T4_ENGINE_FIT.md §1)."""
    raise NotImplementedError(
        "use propfirms.contract.evals.eval_rules + adapter.run_combine — the "
        "vendored Combine engine expresses all five firms' evaluations (T4b)."
    )
