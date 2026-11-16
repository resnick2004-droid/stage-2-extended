"""Eval-side engine fit (T4b): each firm's evaluation on the vendored Combine engine.

Finding on record (docs/T4_ENGINE_FIT.md §1): all five shortlisted evaluations map
onto `vendor/propsim` `simulate_combine` through `Rules(...)` parameter changes alone —
same EOD-trailing floor with intraday truncation, same `max(target, best_day/frac)`
consistency semantics, lock level per firm. This module builds those Rules from the
firm's verified spec rows; every number passes through `FirmSpec.value()` (verified
rows only), and the one figure carried inside a verified row's quoted note
(FundedNext's lock, stated as an absolute $50,100) is parsed fail-loud the way
`scripts/run_ceilings.py` does.

Conventions (same as the engine's):
* cumulative-P&L frame — start = 0, floor starts at -mll, lock levels are relative
  to start (+100 = start + $100);
* fee fields are zeroed except Alpha's monthly subscription, which the engine's
  billing cycle models (~21 trading days/month). One-time fees enter T5's EV
  accounting from the spec directly, never the simulation.
* the Rules built here parameterize the **Combine side only**. Funded mechanics are
  `propfirms/contract/engine.py` (T4c); do not hand these Rules to `run_xfa`.

BluSky: `eval_drawdown_lock` is an open rule (H-6), so there is no default. The
caller must choose from `BLUSKY_LOCK_BRACKET` — None (floor never locks; strictly
worse for the trader) or 100.0 (the pattern every sibling firm follows) — and carry
the choice into any result's parameters as a labelled assumption.
"""
from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path
from typing import Any

from propfirms.contract.adapter import Rules
from propfirms.spec import FirmSpec

FIRM_SLUGS = (
    "lucid-trading",
    "my-funded-futures",
    "funded-next",
    "blusky",
    "alpha-futures",
    # The MFFU variant that replaced intraday Rapid as the modelled row (D-17/D-18).
    # Its eval is EOD-trailing with the same +$100 lock; the 30% consistency rule
    # (vs intraday's 50%) forces >= 4 profitable days, so the verified
    # eval_min_days = 4 is non-binding, like the others.
    "my-funded-futures-rapid-eod",
)

#: The labelled bracket for BluSky's open eval lock row (docs/T4_ENGINE_FIT.md §1.1).
BLUSKY_LOCK_BRACKET: tuple[float | None, ...] = (None, 100.0)

_UNSET = object()

#: Topstep's billing cycle in trading days (vendored Rules default); Alpha's calendar
#: month is approximated by the same 21 trading days — stated wherever results use it.
_TRADING_DAYS_PER_MONTH = 21


class EvalFitError(ValueError):
    """A verified rule value did not parse the way the fit expects — the yaml has
    changed since the fit was written. Re-derive; never guess."""


def _require(pattern: str, text: str, where: str) -> re.Match[str]:
    m = re.search(pattern, text)
    if m is None:
        raise EvalFitError(
            f"pattern {pattern!r} not found in {where}: {text!r}"
        )
    return m


def _lock_level(slug: str, spec: FirmSpec) -> float | None:
    """The Combine floor lock level, relative to start, from the verified rows."""
    if slug in ("lucid-trading", "my-funded-futures", "my-funded-futures-rapid-eod"):
        value = str(spec.value("eval_drawdown_lock"))
        return float(_require(r"start_plus_(\d+)$", value,
                              f"{slug} eval_drawdown_lock value").group(1))
    if slug == "funded-next":
        # Verified value is the absolute level ($50,100); the relative offset is in
        # the same verified row's quoted conclusion ("initial balance + $100").
        spec.value("eval_drawdown_lock")  # verified-only gate
        note = spec.rules["eval_drawdown_lock"].note or ""
        return float(_require(r"initial balance \+ \$(\d+)", note,
                              "funded-next eval_drawdown_lock note").group(1))
    if slug == "alpha-futures":
        value = str(spec.value("eval_drawdown_lock"))
        if value != "locks_at_starting_balance":
            raise EvalFitError(f"alpha eval_drawdown_lock changed: {value!r}")
        return 0.0
    raise EvalFitError(f"no lock handler for {slug!r}")


def eval_rules(
    slug: str,
    *,
    blusky_eval_lock: float | None | object = _UNSET,
    firms_dir: Path | None = None,
) -> Rules:
    """The vendored engine's Rules for one firm's evaluation, from verified rows."""
    if slug not in FIRM_SLUGS:
        raise KeyError(f"unknown firm {slug!r}; known: {FIRM_SLUGS}")
    spec = FirmSpec.load(slug, firms_dir)

    if slug == "blusky":
        if blusky_eval_lock is _UNSET:
            raise EvalFitError(
                "BluSky's eval_drawdown_lock is an open rule (H-6): pass "
                "blusky_eval_lock explicitly, one of BLUSKY_LOCK_BRACKET "
                f"{BLUSKY_LOCK_BRACKET}, and label the choice in the result's "
                "parameters."
            )
        if blusky_eval_lock not in BLUSKY_LOCK_BRACKET:
            raise EvalFitError(
                f"blusky_eval_lock={blusky_eval_lock!r} is not in the labelled "
                f"bracket {BLUSKY_LOCK_BRACKET}"
            )
        lock: float | None = blusky_eval_lock  # type: ignore[assignment]
    else:
        if blusky_eval_lock is not _UNSET:
            raise EvalFitError("blusky_eval_lock applies to 'blusky' only")
        lock = _lock_level(slug, spec)

    subscription = 0.0
    if slug == "alpha-futures":
        # The one subscription-billed eval ($129/month, verified); the engine's
        # cycle bills every `billing_days` trading days.
        subscription = float(spec.value("eval_fee"))

    return replace(
        Rules(),
        profit_target=float(spec.value("eval_profit_target")),
        mll=float(spec.value("eval_drawdown_amount")),
        combine_mll_lock_at=lock,
        consistency_max_day_frac=float(spec.value("eval_consistency_rule")),
        subscription=subscription,
        billing_days=_TRADING_DAYS_PER_MONTH,
        activation=0.0,
        reset_fee=0.0,
        payout_fee=0.0,
        # floor_mode stays "truncate": every firm's verified drawdown rows state the
        # level trails EOD while the breach is tested on floating equity intraday.
    )


def eval_fit(
    slug: str,
    *,
    blusky_eval_lock: float | None | object = _UNSET,
    firms_dir: Path | None = None,
) -> dict[str, Any]:
    """Rules plus the provenance/assumption record a result manifest needs."""
    spec = FirmSpec.load(slug, firms_dir)
    rules = eval_rules(slug, blusky_eval_lock=blusky_eval_lock, firms_dir=firms_dir)
    assumptions = [
        "pass checked at day close (stage-one convention; no firm states "
        "intraday-vs-close explicitly)",
        "fees other than a subscription are charged outside the engine "
        "(T5 EV accounting reads them from the spec)",
    ]
    if slug == "blusky":
        assumptions.append(
            f"eval_drawdown_lock OPEN (H-6): bracket value {blusky_eval_lock!r} "
            f"of {BLUSKY_LOCK_BRACKET} — labelled assumption, not a verified rule"
        )
    if slug == "lucid-trading":
        assumptions.append(
            "DLL OFF, 40 % checkout variant (verified option; its price is the "
            "eval_fee row, verified D-31 from the official pricing card; charged "
            "outside the engine)"
        )
    if slug == "alpha-futures":
        assumptions.append(
            "calendar-month billing approximated by the engine's 21-trading-day "
            "cycle"
        )
    return {
        "firm": slug,
        "rules": rules,
        "assumptions": assumptions,
        "provenance": spec.provenance(),
    }
