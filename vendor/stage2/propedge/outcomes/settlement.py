"""How a trade settles against the room above the nearer barrier (D-156).

The firm liquidates an account the moment its balance touches the loss limit -- the trailing MLL floor, or on an RTP
Combine the $1,000 daily loss limit (D-145) -- whatever the open trade would have done next. So a trade that risks
more than the room left can end at the barrier even if it later reached its target. Stage one's binary process races
the barrier (`propsim.RandomDraw`, `floor_mode="truncate"`). A replayed trade log cannot race unless it knows how far
each trade went against it before its exit, its maximum adverse excursion (MAE).

Before D-156 every trade-log draw ignored the room and the engine clipped the loss afterwards, so a trade whose path
crossed the barrier and recovered kept its recovery; at zero edge the Combine passed above stage one's 2/5 ceiling
(`docs/audits/bmap_gate_check_2026-09-26.md`). Every draw now settles its own trades against the `cushion` the
engine hands it -- both engines hand the room there -- and declares how, in its `settlement` attribute:

* `race`        -- the draw races the barrier itself (stage one's binary process, `adapter.BinaryDraw`);
* `mae`         -- a trade-log draw with each trade's MAE: the barrier is touched when the MAE reaches the room, and
                   the trade then settles at minus the room; exact. A trade whose MAE is missing settles as below;
* `pessimistic` -- a trade-log draw without MAE: a trade that risks more than the room is assumed to have touched
                   the barrier and settles at minus the room; the lower bound of the truth;
* `legacy`      -- the pre-D-156 settlement, the trade's final P&L clipped after the fact; the upper bound, and only
                   for reproducing a pre-D-156 result, labelled as such;
* `final`       -- a scripted stream whose P&L is already the settled P&L (tests).

`propedge.campaign.lockstep` refuses a draw that does not declare one of these.

Units: MAE is in dollars at the trade's own logged risk (the same units as its P&L and dollars risked), positive
when adverse, so it rescales with the trade's P&L. A trade that never went against its entry has MAE 0.
"""
from __future__ import annotations

from typing import Any

import numpy as np

RACE = "race"
MAE = "mae"
PESSIMISTIC = "pessimistic"
LEGACY = "legacy"
FINAL = "final"
SETTLEMENTS = (RACE, MAE, PESSIMISTIC, LEGACY, FINAL)
#: Settlements a trade-log draw may carry.
TRADE_LOG_SETTLEMENTS = (MAE, PESSIMISTIC, LEGACY)

EPS = 1e-9


def check_settlement(mode: str) -> str:
    if mode not in SETTLEMENTS:
        raise ValueError(f"settlement must be one of {SETTLEMENTS}, got {mode!r}")
    return mode


def default_trade_log_settlement(blocks: Any) -> str:
    """`mae` when every block carries MAE, `pessimistic` otherwise: the safe default without the path."""
    return MAE if blocks and all(getattr(b, "mae", None) is not None for b in blocks) else PESSIMISTIC


def _shaped(x: np.ndarray, shape: tuple) -> np.ndarray:
    """`x` broadcast to `shape`, or `x` itself when it already has that shape."""
    return x if x.shape == shape else np.broadcast_to(x, shape)


def settle(pnl: np.ndarray, risk: np.ndarray, mae: np.ndarray | None, room: np.ndarray, mode: str) -> np.ndarray:
    """Settle trades (vectorised over accounts) against `room`, the dollars above the nearer barrier.

    `pnl`, `risk` and `mae` are in dollars at the size traded; NaN P&L means no trade and passes through. Under
    `race`, `legacy` and `final` the P&L is returned as given (the engine's own clip at the floor still applies).
    """
    pnl = np.asarray(pnl, dtype=float)
    if mode in (RACE, LEGACY, FINAL):
        return pnl
    # R11: an array already of the trades' shape goes in as it is -- broadcasting it to its own shape is a view of the
    # same values, shape and strides, so every operation below reads the same numbers
    room = _shaped(np.asarray(room, dtype=float), pnl.shape)
    risk = _shaped(np.asarray(risk, dtype=float), pnl.shape)
    out = np.maximum(pnl, -room)
    touched = risk > room + EPS                          # without the path: the barrier sits inside the stop
    if mode == MAE and mae is not None:
        mae = _shaped(np.asarray(mae, dtype=float), pnl.shape)
        known = ~np.isnan(mae)
        touched = np.where(known, mae >= room - EPS, touched)
    elif mode != PESSIMISTIC and mode != MAE:
        raise ValueError(f"unknown settlement {mode!r}")
    out = np.where(touched & ~np.isnan(pnl), -room, out)
    return np.where(np.isnan(pnl), np.nan, out)


#: Stage one's own draws, which cannot carry the attribute (vendor/propsim is read-only, D-01): its scripted stream
#: hands out settled P&L, and its random draw races the barrier (`floor_mode="truncate"`).
_VENDORED = {"ScriptedDraw": FINAL, "RandomDraw": RACE}


def settlement_of(draw: Any) -> str:
    """The settlement a draw declares; refuses a draw that declares none (D-156)."""
    mode = getattr(draw, "settlement", None)
    if mode is None and type(draw).__module__ == "propsim":
        mode = _VENDORED.get(type(draw).__name__)
    if mode not in SETTLEMENTS:
        raise TypeError(
            f"{type(draw).__name__} does not declare how a trade that risks more than the room left settles "
            f"(settlement={mode!r}). Every draw declares one of {SETTLEMENTS} (D-156): a trade-log draw settles "
            "against the cushion it is handed, using each trade's MAE where the log has it"
        )
    return mode


__all__ = ["RACE", "MAE", "PESSIMISTIC", "LEGACY", "FINAL", "SETTLEMENTS", "TRADE_LOG_SETTLEMENTS",
           "check_settlement", "default_trade_log_settlement", "settle", "settlement_of"]
