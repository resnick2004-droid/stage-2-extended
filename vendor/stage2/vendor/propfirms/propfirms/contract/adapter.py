"""Adapter to the stage-one contract engine vendored at `vendor/propsim/`.

The engine is **imported, never edited** (D-01). This module is the only place in the
repository that touches `vendor/propsim/`; everything else goes through the functions
here. If another firm's mechanics need the engine to behave differently, the change goes
in `propfirms/` (this module, or `propfirms/contract/engine.py`) — never in the vendored
tree, which a hook denies writes to and which `tests/test_vendor_integrity.py` pins by
sha256.

What the engine provides (see `vendor/propsim/propsim.py`):

    simulate_combine(rules, policy, edge, n, rng=None, draw=None, max_days=2000)
    simulate_xfa(rules, policy, edge, n, rng=None, draw=None, horizon_days=250, ...)

Both run `n` accounts in lockstep and both accept a pluggable outcome draw
(`draw(n, day, slot, cushion) -> np.ndarray`), which is the seam for empirical trade
distributions. The engine expresses **Topstep's** mechanics: EOD-trailing drawdown
locking at the 16:00 CT close, its consistency rules and payout paths. T4 records, per
firm, which mechanics map onto it (often just parameter changes via `Rules(...)`) and
which need new code in `engine.py` (an intraday-trailing drawdown is the expected case).

Seeds are explicit everywhere. The engine would construct a default RNG if given none;
this module never lets that happen.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np

from propfirms import VENDOR_PROPSIM


def _ensure_vendor_on_path() -> Path:
    """Put `vendor/propsim/` on sys.path so `import propsim` resolves to the vendored copy.

    Path injection rather than installation: stage one ships no packaging metadata, and
    adding any would be an edit to the read-only tree (D-01). Keeping the copy
    byte-identical is the property the manifest check depends on.
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
    "RandomDraw",
    "ScriptedDraw",
    "run_combine",
    "run_xfa",
    "combine_exact",
    "summarize_combine",
    "summarize_xfa",
    "attempt_ev",
    "p_race",
    "theta_from_edge",
    "engine_version",
]


def engine_version() -> dict[str, Any]:
    """Provenance of the vendored engine, for result-file manifests."""
    import propsim

    return {
        "engine": "propsim (stage one, vendored)",
        "path": str(VENDOR_PROPSIM),
        "module_file": propsim.__file__,
        "docstring_first_line": (propsim.__doc__ or "").strip().splitlines()[0],
    }


def run_combine(
    policy: Policy,
    edge: float,
    n: int,
    *,
    seed: int,
    rules: Rules | None = None,
    draw: Any | None = None,
    max_days: int = 2000,
) -> dict[str, Any]:
    """Run `n` evaluation accounts in lockstep. The seed is required, never defaulted."""
    rules = rules or Rules()
    if n <= 0:
        raise ValueError("n must be positive")
    rng = np.random.default_rng(seed)
    if draw is None:
        draw = RandomDraw(policy, edge, rng, rules.floor_mode, rules.edge_mode)
    raw = _simulate_combine(rules, policy, edge, n, rng=rng, draw=draw, max_days=max_days)
    out = dict(summarize_combine(raw))
    out["raw"] = raw
    out["seed"] = int(seed)
    return out


def run_xfa(
    policy: Policy,
    edge: float,
    n: int,
    *,
    seed: int,
    rules: Rules | None = None,
    draw: Any | None = None,
    horizon_days: int = 250,
) -> dict[str, Any]:
    """Run `n` funded accounts in lockstep. The seed is required, never defaulted."""
    rules = rules or Rules()
    if n <= 0:
        raise ValueError("n must be positive")
    rng = np.random.default_rng(seed)
    if draw is None:
        draw = RandomDraw(policy, edge, rng, rules.floor_mode, rules.edge_mode)
    raw = _simulate_xfa(
        rules, policy, edge, n, rng=rng, draw=draw, horizon_days=horizon_days
    )
    out = dict(summarize_xfa(raw))
    out["raw"] = raw
    out["seed"] = int(seed)
    return out


def combine_exact(R: float, r: float, e: float, **kwargs: Any) -> dict[str, float]:
    """Stage one's exact Combine chain (`vendor/propsim/edge/combine_exact.py`).

    Deterministic — no seed. The canonical oracle: `combine_exact(1.0, 1500.0, 0.0)`
    gives p_pass = 16/49 (propsim; `vendor/propsim/README.md`).
    """
    edge_dir = str(VENDOR_PROPSIM / "edge")
    if edge_dir not in sys.path:
        sys.path.insert(0, edge_dir)
    from combine_exact import combine_exact as _combine_exact  # noqa: E402

    return _combine_exact(R, r, e, **kwargs)
