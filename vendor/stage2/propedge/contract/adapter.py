"""Adapter to the stage-one contract engine vendored at `vendor/propsim/`.

The engine is **imported, never edited** (D-01). This module is the only place in the
repository that touches `vendor/propsim/`; everything else goes through the functions here.
If the engine needs to behave differently, the change goes in this module as an adapter or a
subclass -- not in the vendored tree, which a hook denies writes to and which
`tests/test_vendor_integrity.py` pins by sha256.

What the engine provides (see `vendor/propsim/propsim.py`):

    simulate_combine(rules, policy, edge, n, rng=None, draw=None, max_days=2000)
    simulate_xfa(rules, policy, edge, n, rng=None, draw=None, horizon_days=250, ...)

Both run `n` accounts in lockstep across numpy arrays and both accept a **pluggable outcome
draw**. That plug is the seam stage two needs: stage one drew binary outcomes at exactly the
labelled dollar risk, while stage two will draw from an *empirical* distribution built from a
real trade log (`propedge.outcomes.distribution`). The draw protocol is:

    draw(n, day, slot, cushion) -> np.ndarray of shape (n,), dollars of P&L

where `cushion = balance - floor` for each account and `np.nan` means "no trade in this slot"
(the mechanism `ScriptedDraw` in `vendor/propsim/test_propsim.py` uses to end a day early).
The engine truncates the returned P&L at the floor itself when `rules.liquidate_at_floor`, so
a draw must not attempt to enforce the floor.

Seeds are explicit everywhere. The engine will construct a default `np.random.default_rng()`
if given neither `rng` nor `draw`; this module never lets that happen.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Protocol

import numpy as np

from propedge import VENDOR_PROPSIM


def _ensure_vendor_on_path() -> Path:
    """Put `vendor/propsim/` on sys.path so `import propsim` resolves to the vendored copy.

    An alternative is `pip install -e vendor/propsim`, but stage one ships no packaging
    metadata and adding any would be an edit to the read-only tree. Path injection keeps the
    vendored copy byte-identical, which is the property the manifest check depends on.
    """
    if not VENDOR_PROPSIM.is_dir():
        raise FileNotFoundError(
            f"vendored stage-one engine not found at {VENDOR_PROPSIM}. "
            "See DECISIONS.md D-01: stage one is vendored read-only and must be present."
        )
    p = str(VENDOR_PROPSIM)
    if p not in sys.path:
        sys.path.insert(0, p)
    return VENDOR_PROPSIM


_ensure_vendor_on_path()

# Imported after the path injection above. Re-exported so callers never import from the
# vendored tree directly -- one seam, one place to audit.
from propsim import (  # noqa: E402
    Policy,
    RandomDraw,
    Rules,
    ScriptedDraw,
    attempt_ev,
    p_race,
    simulate_combine as _simulate_combine,
    simulate_xfa as _simulate_xfa,
    summarize_combine,
    summarize_xfa,
    theta_from_edge,
)

__all__ = [
    "Rules",
    "Policy",
    "ScriptedDraw",
    "RandomDraw",
    "BinaryDraw",
    "OutcomeDraw",
    "run_combine",
    "run_xfa",
    "keep_balance_policy",
    "summarize_combine",
    "summarize_xfa",
    "attempt_ev",
    "p_race",
    "theta_from_edge",
    "engine_version",
]


class OutcomeDraw(Protocol):
    """The pluggable outcome source.

    Mirrors `ScriptedDraw` in `vendor/propsim/test_propsim.py`: a callable, not a class
    hierarchy, so a plain function or a lambda is a valid draw.

    Args:
        n: number of accounts simulated in lockstep.
        day: 0-based trading day index.
        slot: 0-based trade slot within the day.
        cushion: array of shape (n,), `balance - floor` per account, in dollars.

    Returns:
        Array of shape (n,) of dollar P&L. `np.nan` for an account means "no trade in this
        slot"; the engine leaves that account's balance untouched and does not count a trade.

    `cushion` is the room above the nearer barrier (the floor, or on an RTP Combine the daily
    loss limit's room in the lockstep loop). The firm liquidates when the balance touches it, so
    a trade that risks more than the room can end there even if it later reached its target.
    Every draw declares in a `settlement` attribute how its trades settle against the room
    (`propedge.outcomes.settlement`, D-156) -- `race`, `mae`, `pessimistic`, `legacy` or `final`
    -- and the lockstep loop refuses a draw that declares none. The engines still apply
    `np.maximum(pnl, -cushion)` afterwards when `rules.liquidate_at_floor` is set; for a draw
    that has settled, that clip changes nothing.
    """

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray) -> np.ndarray: ...


class BinaryDraw:
    """Stage one's binary outcome draw, with an explicit seed.

    Delegates to the vendored `RandomDraw` so the semantics -- including the floor barrier
    race in `floor_mode="truncate"` and the drift solve for non-zero edge (propsim D-06) --
    are the engine's, not a reimplementation that could drift away from it. The only thing
    added here is that the seed is required rather than optional.

    This is the **validation limit**: with a zero-cost fill profile and this draw, stage two
    must reproduce stage one exactly (16/49 for 1:1 at $1,500; cells of
    `vendor/propsim/edge/results_combine_edge.csv`). See `tests/test_adapter_reproduces_stage_one.py`.
    """

    #: D-156: the vendored draw races the barrier the engine hands it as `cushion`.
    settlement = "race"

    def __init__(self, policy: Policy, edge: float, seed: int, rules: Rules | None = None):
        rules = rules or Rules()
        self.seed = int(seed)
        self._rng = np.random.default_rng(self.seed)
        self._policy, self._edge, self._rules = policy, edge, rules
        self._inner = RandomDraw(policy, edge, self._rng, rules.floor_mode, rules.edge_mode)

    def set_risk(self, risk: float, rr: float | None = None) -> None:
        """D-147: trade the next slots at `risk` dollars (and `rr`, if given). The binary process
        can honour a change of R because it has no stops or targets of its own. The inner draw is
        rebuilt on the same random stream only when something changes, so an unchanged policy
        leaves the stream, and every result, exactly as before."""
        from dataclasses import replace

        rr = self._policy.rr if rr is None else float(rr)
        if float(risk) == float(self._policy.risk) and rr == float(self._policy.rr):
            return
        self._policy = replace(self._policy, risk=float(risk), rr=rr)
        self._inner = RandomDraw(self._policy, self._edge, self._rng, self._rules.floor_mode, self._rules.edge_mode)

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray) -> np.ndarray:
        return self._inner(n, day, slot, cushion)


def engine_version() -> dict[str, Any]:
    """Provenance of the vendored engine, for result-file manifests."""
    import propsim

    return {
        "engine": "propsim (stage one, vendored)",
        "path": str(VENDOR_PROPSIM),
        "module_file": propsim.__file__,
        "docstring_first_line": (propsim.__doc__ or "").strip().splitlines()[0],
    }


def keep_balance_policy(
    rr: float,
    risk: float,
    keep_balance: float,
    *,
    trades_per_day: int = 1,
    payout_path: str = "standard",
    payout_frac: float = 1.0,
) -> Policy:
    """A funded-account policy with the `keep_balance` payout rule (propsim D-45).

    `keep_balance` is a floor on the account balance that a payout request may not take it
    below: the engine requests `min(allowed, max(balance - keep_balance, 0))`. It exists
    because any payout drops the funded floor to $0, so an early payout strands a small
    balance with no cushion.

    Stage one's best found was `rr=1.5, risk=500, keep_balance=8000`
    (`vendor/propsim/edge/T5_RESULTS.md` §3). **That is a hint, not a setting to adopt**: it
    was exploratory (propsim D-44), its grid was coarse, one optimum was still rising at the
    largest buffer tested, and it priced no payout latency, no reinvestment and no
    per-contract costs. Stage two re-derives payout policy under the time-aware objective
    (D-02), which is exactly the comparison `propedge.campaign` exists to run.

    Args:
        rr: reward multiple R (target = R x stop). Must be positive; R at or below 1 is a tier-2
            conduct flag since D-145 (D-151), reported by `Protocol.conduct_flags`, not refused.
        risk: dollar loss per trade.
        keep_balance: never request a payout that leaves the balance below this. 0 disables.
        trades_per_day: trade slots per day.
        payout_path: "standard" or "consistency".
        payout_frac: fraction of the maximum allowed request to take.
    """
    if not rr > 0:
        raise ValueError(f"rr={rr} must be positive")
    if keep_balance < 0:
        raise ValueError(f"keep_balance={keep_balance} must be >= 0")
    return Policy(
        rr=rr,
        risk=risk,
        trades_per_day=trades_per_day,
        payout_path=payout_path,
        payout_frac=payout_frac,
        keep_balance=keep_balance,
    )


@dataclass(frozen=True)
class CombineResult:
    """Summary of a Combine run, plus the raw per-account arrays for further analysis."""

    p_pass: float
    p_pass_se: float
    p_fail: float
    p_unresolved: float
    mean_days: float
    mean_sub_fees: float
    n: int
    seed: int
    raw: dict[str, Any]

    @property
    def pass_day(self) -> np.ndarray:
        """0-based day each account passed, or -1. Needed for dated cash flows."""
        return self.raw["pass_day"]


@dataclass(frozen=True)
class XfaResult:
    """Summary of a funded-account run, plus the raw per-account arrays."""

    p_any_payout: float
    mean_cash: float
    mean_gross: float
    mean_n_payouts: float
    mean_days_to_first_payout: float
    p_closed: float
    n: int
    seed: int
    raw: dict[str, Any]

    @property
    def cash(self) -> np.ndarray:
        """Net cash to the trader per account, after the profit split and any payout fee."""
        return self.raw["cash"]

    @property
    def first_payout_day(self) -> np.ndarray:
        """0-based day of the first payout, or -1. The latency the charter requires."""
        return self.raw["first_payout_day"]


def run_combine(
    policy: Policy,
    edge: float,
    n: int,
    *,
    seed: int,
    rules: Rules | None = None,
    draw: OutcomeDraw | None = None,
    max_days: int = 2000,
) -> CombineResult:
    """Run `n` Combine accounts in lockstep.

    Args:
        policy: profile (R, dollar risk, trades per day, ...).
        edge: expected P&L per trade as a fraction of dollar risk, **net of costs**. Only
            used when `draw` is None, to build the binary draw. An empirical draw carries its
            own edge and this argument is then ignored by the outcome process (it is still
            recorded, so pass the measured value for provenance).
        n: number of accounts.
        seed: explicit. Required -- there is no default RNG path here (D: seed everything).
        rules: contract rules; defaults to the stage-one defaults.
        draw: outcome source. Defaults to `BinaryDraw` (the validation limit).
        max_days: hard cap on the simulated day loop.

    Returns:
        CombineResult.
    """
    rules = rules or Rules()
    if n <= 0:
        raise ValueError("n must be positive")
    rng = np.random.default_rng(seed)
    draw = draw if draw is not None else BinaryDraw(policy, edge, seed, rules)
    raw = _simulate_combine(rules, policy, edge, n, rng=rng, draw=draw, max_days=max_days)
    s = summarize_combine(raw)
    return CombineResult(
        p_pass=float(s["p_pass"]),
        p_pass_se=float(s["p_pass_se"]),
        p_fail=float(s["p_fail"]),
        p_unresolved=float(s["p_unresolved"]),
        mean_days=float(s["mean_days"]),
        mean_sub_fees=float(s["mean_sub_fees"]),
        n=n,
        seed=int(seed),
        raw=raw,
    )


def run_xfa(
    policy: Policy,
    edge: float,
    n: int,
    *,
    seed: int,
    rules: Rules | None = None,
    draw: OutcomeDraw | None = None,
    horizon_days: int = 250,
    horizon_per_account: np.ndarray | None = None,
) -> XfaResult:
    """Run `n` funded (XFA) accounts in lockstep.

    Args as `run_combine`, plus:
        horizon_days: trading days simulated per account.
        horizon_per_account: per-account horizons, for lifecycle runs where each account
            starts when its Combine passed.

    The `keep_balance` payout policy is carried on `policy`; build one with
    `keep_balance_policy`.
    """
    rules = rules or Rules()
    if n <= 0:
        raise ValueError("n must be positive")
    rng = np.random.default_rng(seed)
    draw = draw if draw is not None else BinaryDraw(policy, edge, seed, rules)
    raw = _simulate_xfa(
        rules,
        policy,
        edge,
        n,
        rng=rng,
        draw=draw,
        horizon_days=horizon_days,
        horizon_per_account=horizon_per_account,
    )
    s = summarize_xfa(raw)
    return XfaResult(
        p_any_payout=float(s["p_any_payout"]),
        mean_cash=float(s["mean_cash"]),
        mean_gross=float(s["mean_gross"]),
        mean_n_payouts=float(s["mean_n_payouts"]),
        mean_days_to_first_payout=float(s["mean_days_to_first_payout"]),
        p_closed=float(s["p_closed"]),
        n=n,
        seed=int(seed),
        raw=raw,
    )


def rules_from_ledger(**overrides: Any) -> Rules:
    """Build engine `Rules` from `config/rules.yaml`, honouring the verified-status gate.

    Raises if any rule it needs is not marked `verified` -- which, until T1 is done, is all of
    them. That is deliberate: it is the charter rule "nothing may depend on a rule whose
    status is not verified", enforced at the point of use rather than by review.

    Until T1 closes, tests and validation runs construct `Rules()` directly (stage one's
    defaults) and say so. Research runs must come through here.
    """
    from propedge.contract.rules import RulesLedger

    ledger = RulesLedger.load()
    kw = dict(
        profit_target=ledger.value("combine_profit_target"),
        mll=ledger.value("combine_mll"),
        consistency_max_day_frac=ledger.value("combine_consistency_max_day_frac"),
        combine_mll_lock_at=ledger.value("combine_mll_lock_at"),
        xfa_mll_start=ledger.value("xfa_mll_start"),
        xfa_lock_at=ledger.value("xfa_lock_at"),
        std_winning_days=int(ledger.value("xfa_std_winning_days")),
        std_winning_day_min=ledger.value("xfa_std_winning_day_min"),
        std_cap=ledger.value("xfa_std_cap"),
        cons_min_days=int(ledger.value("xfa_cons_min_days")),
        cons_max_day_frac=ledger.value("xfa_cons_max_day_frac"),
        cons_cap=ledger.value("xfa_cons_cap"),
        payout_min=ledger.value("payout_min"),
        payout_max_frac_of_balance=ledger.value("payout_max_frac_of_balance"),
        profit_split=ledger.value("profit_split"),
        require_profit_since_payout=bool(ledger.value("require_profit_since_payout")),
        subscription=ledger.value("subscription_fee"),
        billing_days=int(ledger.value("billing_days")),
        activation=ledger.value("activation_fee"),
        reset_fee=ledger.value("reset_fee"),
    )
    kw.update(overrides)
    return Rules(**kw)
