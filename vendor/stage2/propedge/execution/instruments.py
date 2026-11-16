"""Instruments, integer contract sizing, and position-limit checks.

Stage one did not model contract size at all: its `$ risk` was a free real number and its
README lists "contract caps and stop distance" under *not modelled*. Stage two has to close
that gap, because two things only become visible once size is an integer number of contracts:

1. **Rounding down.** A $500 risk over a 12-tick MES stop is 33.3 contracts, so 33 are traded
   and the realised risk is $495. Harmless here; at small risks and wide stops it is not --
   at 1.6 contracts you trade 1 and risk 62 % of what you intended, and at 0.8 you cannot
   take the trade at all.
2. **The position limit.** The firm caps contracts by account size. If the cap is below the
   size a candidate's stop distance implies, the candidate cannot be traded at the tested
   risk -- which invalidates the backtest, not merely the sizing.

Both position limits are `unverified_human_input_required` in `config/rules.yaml` until T1
closes, so `contracts_for_risk` refuses to size a position by default. That refusal is the
feature: a silently-unlimited position limit would let a whole protocol comparison run on a
size the firm does not allow.

Times are US/Central throughout, because the firm's day boundary is 16:00 CT and the flatten
is 15:10 CT. Convert at the data boundary, not here.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import time
from pathlib import Path
from typing import Any

import yaml

from propedge import CONFIG_DIR

HUMAN_INPUT_MARKER = "HUMAN INPUT REQUIRED"


class PositionLimitError(RuntimeError):
    """Raised when a required size exceeds the verified position limit."""


class UnsizeableTradeError(RuntimeError):
    """Raised when the dollar risk is too small to buy even one contract."""


def _parse_ct(s: str) -> time:
    hh, mm = s.split(":")
    return time(int(hh), int(mm))


@dataclass(frozen=True)
class Instrument:
    """One tradable contract.

    Attributes:
        symbol: e.g. "MES".
        tick_size: minimum price increment, in the instrument's price units.
        tick_value: dollars per tick per contract.
        point_value: dollars per price point per contract (= tick_value / tick_size).
        session_open_ct / session_close_ct: session boundaries, US/Central.
        flatten_ct: the 15:10 CT flatten. Positions open at this time are closed at market
            and their **actual** P&L recorded -- never assumed binary
            (`vendor/propsim/HANDOFF.md` §3).
        verified: False while any value is still marked HUMAN INPUT REQUIRED.
    """

    symbol: str
    name: str
    exchange: str
    tick_size: float
    tick_value: float
    point_value: float
    currency: str
    session_open_ct: time
    session_close_ct: time
    flatten_ct: time
    source: str
    verified: bool
    note: str | None = None

    # ------------------------------------------------------------ conversions
    def ticks_to_dollars(self, ticks: float, contracts: int = 1) -> float:
        """Dollars for a move of `ticks` ticks held in `contracts` contracts."""
        return float(ticks) * self.tick_value * int(contracts)

    def price_to_ticks(self, price_distance: float) -> float:
        """A price distance expressed in ticks. Not rounded -- callers decide."""
        if self.tick_size <= 0:
            raise ValueError(f"{self.symbol}: tick_size must be positive")
        return float(price_distance) / self.tick_size

    def dollars_per_contract(self, stop_ticks: float) -> float:
        """Dollar risk of one contract for a stop `stop_ticks` ticks away."""
        if stop_ticks <= 0:
            raise ValueError("stop_ticks must be positive")
        return float(stop_ticks) * self.tick_value

    def round_to_tick(self, price: float) -> float:
        """Snap a price to the instrument's tick grid."""
        return round(float(price) / self.tick_size) * self.tick_size

    def require_verified(self) -> None:
        if not self.verified:
            raise RuntimeError(
                f"instrument {self.symbol} carries unverified values "
                f"(source: {self.source!r}). Confirm tick_size, tick_value and point_value "
                f"against the CME contract spec and the broker platform, then clear the "
                f"HUMAN INPUT REQUIRED marker in config/instruments.yaml. "
                f"See T2 in NEXT_STEPS.md and docs/HUMAN_INPUTS.md."
            )


def load_instruments(path: Path | str | None = None) -> dict[str, Instrument]:
    """Load `config/instruments.yaml`."""
    path = Path(path) if path is not None else CONFIG_DIR / "instruments.yaml"
    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    meta = doc.get("meta") or {}
    default_flatten = meta.get("flatten_ct", "15:10")
    out: dict[str, Instrument] = {}
    for sym, body in (doc.get("instruments") or {}).items():
        source = str(body.get("source", ""))
        out[sym] = Instrument(
            symbol=sym,
            name=body.get("name", sym),
            exchange=body.get("exchange", ""),
            tick_size=float(body["tick_size"]),
            tick_value=float(body["tick_value"]),
            point_value=float(body["point_value"]),
            currency=body.get("currency", "USD"),
            session_open_ct=_parse_ct(body.get("session_open_ct", "17:00")),
            session_close_ct=_parse_ct(body.get("session_close_ct", "16:00")),
            flatten_ct=_parse_ct(body.get("flatten_ct", default_flatten)),
            source=source,
            verified=HUMAN_INPUT_MARKER not in source,
            note=body.get("note"),
        )
    if not out:
        raise ValueError(f"no instruments defined in {path}")
    return out


def get_instrument(symbol: str, path: Path | str | None = None) -> Instrument:
    instruments = load_instruments(path)
    try:
        return instruments[symbol]
    except KeyError:
        raise KeyError(
            f"unknown instrument {symbol!r}; defined: {', '.join(sorted(instruments))}"
        ) from None


# --------------------------------------------------------------------- sizing


@dataclass(frozen=True)
class Sizing:
    """The result of converting a dollar risk into contracts.

    `intended_risk` is what was asked for; `realised_risk` is what the integer contract count
    actually risks. Their ratio is the rounding penalty, and it is reported rather than
    quietly absorbed -- at small sizes it is large.
    """

    symbol: str
    contracts: int
    stop_ticks: float
    intended_risk: float
    realised_risk: float
    dollars_per_contract: float
    position_limit: int | None

    @property
    def rounding_shortfall(self) -> float:
        """Dollars of intended risk not taken because contracts are integers."""
        return self.intended_risk - self.realised_risk

    @property
    def rounding_shortfall_frac(self) -> float:
        """Shortfall as a fraction of intended risk. Grows as size falls."""
        if self.intended_risk <= 0:
            return 0.0
        return self.rounding_shortfall / self.intended_risk


def contracts_for_risk(
    instrument: Instrument,
    stop_ticks: float,
    dollar_risk: float,
    *,
    position_limit: int | None = None,
    limit_rule: str = "combine_position_size_limit",
    ledger: Any | None = None,
    require_verified_instrument: bool = True,
) -> Sizing:
    """Integer contracts for a stop distance and a dollar risk.

    Rounds **down**: a partial contract is not tradable, and rounding up would risk more than
    the tested amount, which is the direction that breaks a backtest's conclusions.

    Args:
        instrument: the contract.
        stop_ticks: stop distance in ticks. Must be positive.
        dollar_risk: intended dollar loss if the stop is hit.
        position_limit: explicit cap in contracts. If None, it is read from the rules ledger
            under `limit_rule`, which **raises** while that rule is unverified.
        limit_rule: which ledger rule supplies the cap.
        ledger: a `RulesLedger`; loaded from `config/rules.yaml` if omitted.
        require_verified_instrument: refuse to size on an instrument whose tick values are
            still marked HUMAN INPUT REQUIRED. Tests that only exercise the arithmetic may
            pass False.

    Raises:
        UnsizeableTradeError: the dollar risk does not buy one contract at this stop.
        PositionLimitError: the required size exceeds the limit.
        UnverifiedRuleError: no explicit limit given and the ledger rule is not verified.
    """
    if require_verified_instrument:
        instrument.require_verified()
    if stop_ticks <= 0:
        raise ValueError("stop_ticks must be positive")
    if dollar_risk <= 0:
        raise ValueError("dollar_risk must be positive")

    per_contract = instrument.dollars_per_contract(stop_ticks)
    n = int(math.floor(dollar_risk / per_contract))

    if n < 1:
        raise UnsizeableTradeError(
            f"{instrument.symbol}: a {stop_ticks:g}-tick stop risks "
            f"${per_contract:,.2f} per contract, which exceeds the intended "
            f"${dollar_risk:,.2f}. One contract is the minimum tradable size, so this "
            f"combination of stop distance and dollar risk cannot be traded. Widen the "
            f"risk, tighten the stop, or use a smaller contract."
        )

    if position_limit is None:
        from propedge.contract.rules import load_rules

        ledger = ledger if ledger is not None else load_rules()
        # Raises UnverifiedRuleError while the limit is unverified. That is the point:
        # sizing without a verified cap is how a protocol comparison ends up run at a size
        # the firm does not permit.
        position_limit = int(ledger.value(limit_rule))

    if position_limit is not None and n > position_limit:
        raise PositionLimitError(
            f"{instrument.symbol}: a ${dollar_risk:,.2f} risk over a {stop_ticks:g}-tick "
            f"stop needs {n} contracts, above the position limit of {position_limit} "
            f"({limit_rule}). The candidate cannot be traded at this risk. Reduce the "
            f"dollar risk to at most ${position_limit * per_contract:,.2f}, or re-specify "
            f"the strategy -- do not silently trade a smaller size than the one tested."
        )

    return Sizing(
        symbol=instrument.symbol,
        contracts=n,
        stop_ticks=float(stop_ticks),
        intended_risk=float(dollar_risk),
        realised_risk=n * per_contract,
        dollars_per_contract=per_contract,
        position_limit=position_limit,
    )


def check_position_limit(
    contracts: int,
    *,
    position_limit: int | None = None,
    limit_rule: str = "combine_position_size_limit",
    ledger: Any | None = None,
) -> None:
    """Assert a contract count is within the limit. Raises `PositionLimitError` if not."""
    if position_limit is None:
        from propedge.contract.rules import load_rules

        ledger = ledger if ledger is not None else load_rules()
        position_limit = int(ledger.value(limit_rule))
    if contracts > position_limit:
        raise PositionLimitError(
            f"{contracts} contracts exceeds the position limit of {position_limit} "
            f"({limit_rule})"
        )


def is_after_flatten(t: time, instrument: Instrument) -> bool:
    """True if `t` (US/Central) is at or after the flatten time.

    A position open at the flatten is closed at market; its realised P&L is whatever the
    market gives, which is neither the stop nor the target. Treating those trades as binary
    is the single most common way a backtest of a bracketed strategy flatters itself.
    """
    return t >= instrument.flatten_ct
