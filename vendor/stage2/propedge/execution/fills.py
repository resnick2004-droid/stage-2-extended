"""The fill model: what price a trade actually gets.

The criterion is `e >= 0.10` **net**. Stage one measured a gross edge and folded commissions
into a negative edge parameter; the gap between gross and net is where a candidate dies, so
stage two models it explicitly and in the right units -- **slippage in ticks, commission per
contract per side** (D-03).

Three exits, each with its own fill behaviour:

* **stop** -- a market order once touched, so it is the most adverse. When price *gaps*
  through the stop rather than trading through it, the fill is at the next available price,
  not at the stop. Filling a gapped stop at the stop price is precisely what the firm's
  Prohibited Trading Strategies calls out ("exploiting the relative lack of slippage in SIM to
  achieve impossible stop-loss execution"), so it is available only in the `zero_cost`
  validation profile and is refused elsewhere.
* **target** -- a resting limit. It fills at the limit price (no adverse slippage) but only if
  price trades *through* it; assuming a fill on a touch flatters every result.
* **flatten** -- the 15:10 CT market exit. Its P&L is whatever the market gives. Recording it
  as a stop or a target is the mistake `vendor/propsim/HANDOFF.md` §3 warns about.

`FillModel.zero_cost()` is the validation limit: zero slippage, zero commission, exact fills.
With it the model returns exactly the binary P&L (+R*r on a target, -r on a stop), which is
what lets stage two be shown to reduce to stage one.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from propedge import CONFIG_DIR
from propedge.execution.instruments import Instrument

HUMAN_INPUT_MARKER = "HUMAN INPUT REQUIRED"
#: D-95: an operator-instructed assumption is still an assumption, and is flagged as one.
ASSUMED_MARKER = "ASSUMED"


class ExitReason(str, Enum):
    """How a trade ended. Mirrors the trade-log schema in `propedge.outcomes.tradelog`."""

    TARGET = "target"
    STOP = "stop"
    FLATTEN = "flatten"
    OTHER = "other"


class Side(str, Enum):
    LONG = "long"
    SHORT = "short"

    @property
    def sign(self) -> int:
        return 1 if self is Side.LONG else -1


class ImpossibleFillError(RuntimeError):
    """Raised when a configuration would produce a fill the market would not give."""


class FlatCommissionError(RuntimeError):
    """Raised when a flat per-contract commission is used although per-instrument values exist.

    A single commission across contract sizes does not merely blur the answer, it reverses it.
    A flat $1.44 round turn applied to both a $12.50-tick ES and a $1.25-tick MES gives minis a
    tenfold cost advantage; the published schedule makes it about threefold. Cost drag decides
    whether a candidate can clear the criterion at all, so once `round_turn_by_instrument` is
    populated the flat path is closed rather than left as a silent fallback.
    """


@dataclass(frozen=True)
class Fill:
    """One completed trade, priced.

    `gross_pnl` is the P&L from the price move alone; `net_pnl` subtracts commissions and
    exchange fees for both sides. `slippage_dollars` is the cost of the adverse fills, broken
    out so a result can say how much of the gross-to-net gap is slippage and how much is
    commission.
    """

    entry_price: float
    exit_price: float
    contracts: int
    side: Side
    exit_reason: ExitReason
    gross_pnl: float
    net_pnl: float
    commission: float
    slippage_dollars: float
    slippage_ticks: float


@dataclass(frozen=True)
class FillModel:
    """Fill and cost parameters, loaded from `config/fills.yaml`.

    Attributes:
        entry_slippage_ticks: adverse ticks on entry.
        stop_slippage_ticks: adverse ticks on a stop that trades through.
        target_slippage_ticks: adverse ticks on a target (normally 0 for a resting limit).
        flatten_slippage_ticks: adverse ticks on the 15:10 CT market exit.
        gap_through_stop: "next_price" (realistic) or "exact" (only in `zero_cost`).
        require_trade_through_for_target: a touch is not a fill.
        commission_per_contract_per_side / exchange_fees_per_contract_per_side: USD.
        is_assumption: True while any value is still an unmeasured placeholder. Results
            computed with an assumption profile must say so.
    """

    name: str
    entry_slippage_ticks: float = 0.0
    stop_slippage_ticks: float = 0.0
    target_slippage_ticks: float = 0.0
    flatten_slippage_ticks: float = 0.0
    gap_through_stop: str = "next_price"
    require_trade_through_for_target: bool = True
    commission_per_contract_per_side: float = 0.0
    exchange_fees_per_contract_per_side: float = 0.0
    is_assumption: bool = True
    status: str = ""
    sources: dict[str, str] = field(default_factory=dict)
    #: symbol -> all-in round-turn cost per contract. When non-empty, the flat
    #: commission path is refused -- see `FlatCommissionError`.
    round_turn_by_instrument: dict[str, float] = field(default_factory=dict)
    round_turn_source: str = ""

    # --------------------------------------------------------------- loading
    @classmethod
    def load(cls, profile: str | None = None, path: Path | str | None = None) -> "FillModel":
        path = Path(path) if path is not None else CONFIG_DIR / "fills.yaml"
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        profiles = doc.get("profiles") or {}
        name = profile or (doc.get("meta") or {}).get("active_profile") or "assumed"
        if name not in profiles:
            raise KeyError(
                f"no fill profile {name!r} in {path}; defined: {', '.join(sorted(profiles))}"
            )
        body = profiles[name]
        status = str(body.get("status", ""))
        rt = doc.get("round_turn_by_instrument") or {}
        # The zero-cost validation profile is definitionally free, so it never picks up
        # per-instrument costs -- that is what makes it reproduce stage one exactly. Any other
        # profile that is free by definition (zero_cost_gap_fill, D-83) opts out explicitly.
        free = name == "zero_cost" or body.get("apply_round_turn_by_instrument") is False
        rt_values = {} if free else dict(rt.get("values") or {})
        return cls(
            name=name,
            round_turn_by_instrument={k: float(v) for k, v in rt_values.items()},
            round_turn_source=str(rt.get("source", "")),
            entry_slippage_ticks=float(body.get("entry_slippage_ticks", 0.0)),
            stop_slippage_ticks=float(body.get("stop_slippage_ticks", 0.0)),
            target_slippage_ticks=float(body.get("target_slippage_ticks", 0.0)),
            flatten_slippage_ticks=float(body.get("flatten_slippage_ticks", 0.0)),
            gap_through_stop=str(body.get("gap_through_stop", "next_price")),
            require_trade_through_for_target=bool(
                body.get("require_trade_through_for_target", True)
            ),
            commission_per_contract_per_side=float(
                body.get("commission_per_contract_per_side", 0.0)
            ),
            exchange_fees_per_contract_per_side=float(
                body.get("exchange_fees_per_contract_per_side", 0.0)
            ),
            is_assumption=HUMAN_INPUT_MARKER in status or ASSUMED_MARKER in status,
            status=status,
            sources=dict(body.get("sources") or {}),
        )

    @classmethod
    def zero_cost(cls) -> "FillModel":
        """The validation limit: no slippage, no commission, exact fills.

        Reproduces stage one's binary model exactly. `gap_through_stop="exact"` is permitted
        here and only here -- it is the assumption stage one made, and reproducing stage one
        is the whole purpose of this profile.
        """
        return cls(
            name="zero_cost",
            gap_through_stop="exact",
            require_trade_through_for_target=False,
            is_assumption=False,
            status="exact",
        )

    # ------------------------------------------------------------- properties
    @property
    def cost_per_contract_per_side(self) -> float:
        return self.commission_per_contract_per_side + self.exchange_fees_per_contract_per_side

    @property
    def is_zero_cost(self) -> bool:
        return (
            self.cost_per_contract_per_side == 0.0
            and self.entry_slippage_ticks == 0.0
            and self.stop_slippage_ticks == 0.0
            and self.target_slippage_ticks == 0.0
            and self.flatten_slippage_ticks == 0.0
        )

    def validate(self) -> None:
        """Refuse configurations that would produce impossible fills."""
        if self.gap_through_stop not in {"exact", "next_price"}:
            raise ValueError(
                f"gap_through_stop must be 'exact' or 'next_price', got "
                f"{self.gap_through_stop!r}"
            )
        if self.gap_through_stop == "exact" and self.name != "zero_cost":
            raise ImpossibleFillError(
                f"fill profile {self.name!r} sets gap_through_stop='exact', which fills a "
                "stop at the stop price even when the market gapped past it. That is the "
                "SIM-fill exploitation the firm prohibits (Prohibited Trading Strategies: "
                "'exploiting the relative lack of slippage in SIM to achieve impossible "
                "stop-loss execution'), and it is a conduct guardrail in CHARTER.md. Only "
                "the zero_cost validation profile may use it."
            )
        for field_name in (
            "entry_slippage_ticks",
            "stop_slippage_ticks",
            "target_slippage_ticks",
            "flatten_slippage_ticks",
        ):
            if getattr(self, field_name) < 0:
                raise ValueError(
                    f"{field_name} is negative; slippage is adverse by convention, so a "
                    "positive number always costs money and a negative one would model the "
                    "market paying you to trade"
                )

    # ------------------------------------------------------------------ fills
    def commission_for(self, contracts: int, symbol: str | None = None) -> float:
        """All-in round-turn cost for `contracts` contracts of `symbol`.

        Uses `round_turn_by_instrument[symbol]` when per-instrument values are configured. The
        flat `2 x cost_per_contract_per_side` path survives only while that map is empty --
        otherwise it raises, because a flat figure across contract sizes reverses the
        mini-versus-micro comparison rather than merely blurring it.

        Raises:
            FlatCommissionError: per-instrument values exist but no symbol was given, or the
                symbol has no entry.
        """
        if not self.round_turn_by_instrument:
            return 2.0 * contracts * self.cost_per_contract_per_side

        if symbol is None:
            raise FlatCommissionError(
                f"fill profile {self.name!r} has per-instrument round-turn costs "
                f"({sorted(self.round_turn_by_instrument)}) but commission_for() was called "
                "without a symbol, which would fall back to a flat per-contract figure. Pass "
                "the instrument's symbol."
            )
        try:
            return contracts * self.round_turn_by_instrument[symbol]
        except KeyError:
            raise FlatCommissionError(
                f"no round-turn cost configured for {symbol!r} in config/fills.yaml "
                f"(have: {sorted(self.round_turn_by_instrument)}). Add it rather than falling "
                "back to the flat figure -- cost drag decides candidate viability and a flat "
                "figure is wrong across contract sizes."
            ) from None

    def entry_fill_price(
        self, instrument: Instrument, intended_price: float, side: Side
    ) -> float:
        """Entry price after adverse slippage (a long pays up, a short sells down)."""
        adverse = side.sign * self.entry_slippage_ticks * instrument.tick_size
        return intended_price + adverse

    def exit_fill_price(
        self,
        instrument: Instrument,
        *,
        exit_reason: ExitReason,
        intended_price: float,
        side: Side,
        next_available_price: float | None = None,
        gapped: bool = False,
    ) -> float:
        """Exit price after slippage and gap handling.

        Args:
            exit_reason: which exit fired.
            intended_price: the stop price, the target price, or the market price at flatten.
            side: the position's side.
            next_available_price: the first tradable price after a gap. Required when
                `gapped` is True and `gap_through_stop == "next_price"`.
            gapped: price gapped past the level rather than trading through it.
        """
        if exit_reason is ExitReason.STOP:
            if gapped:
                if self.gap_through_stop == "exact":
                    self.validate()  # raises outside zero_cost
                    return intended_price
                if next_available_price is None:
                    raise ImpossibleFillError(
                        "price gapped through the stop but no next_available_price was "
                        "given. A gapped stop fills at the next available price; filling it "
                        "at the stop price is an impossible fill."
                    )
                return next_available_price
            # Traded through: market order, adverse slippage. Exiting a long is a sell, so
            # the adverse direction is the opposite of the entry's.
            return intended_price - side.sign * self.stop_slippage_ticks * instrument.tick_size

        if exit_reason is ExitReason.TARGET:
            return intended_price - side.sign * self.target_slippage_ticks * instrument.tick_size

        # FLATTEN / OTHER: market order at whatever the market gives.
        return intended_price - side.sign * self.flatten_slippage_ticks * instrument.tick_size

    def fill(
        self,
        instrument: Instrument,
        *,
        side: Side,
        contracts: int,
        intended_entry: float,
        intended_exit: float,
        exit_reason: ExitReason,
        next_available_price: float | None = None,
        gapped: bool = False,
    ) -> Fill:
        """Price a complete trade, gross and net.

        With `FillModel.zero_cost()` this returns exactly the binary P&L: for a stop at
        `stop_ticks` away, `net_pnl == -r`; for a target at `R * stop_ticks` away,
        `net_pnl == +R * r`. `tests/test_fills_zero_cost_limit.py` asserts it.
        """
        self.validate()
        if contracts < 1:
            raise ValueError("contracts must be at least 1")

        entry = self.entry_fill_price(instrument, intended_entry, side)
        exit_price = self.exit_fill_price(
            instrument,
            exit_reason=exit_reason,
            intended_price=intended_exit,
            side=side,
            next_available_price=next_available_price,
            gapped=gapped,
        )

        gross = side.sign * (exit_price - entry) * instrument.point_value * contracts
        commission = self.commission_for(contracts, instrument.symbol)
        net = gross - commission

        ideal_gross = (
            side.sign * (intended_exit - intended_entry) * instrument.point_value * contracts
        )
        slippage_dollars = ideal_gross - gross
        slip_ticks = (
            slippage_dollars / (instrument.tick_value * contracts)
            if instrument.tick_value and contracts
            else 0.0
        )

        return Fill(
            entry_price=entry,
            exit_price=exit_price,
            contracts=contracts,
            side=side,
            exit_reason=exit_reason,
            gross_pnl=gross,
            net_pnl=net,
            commission=commission,
            slippage_dollars=slippage_dollars,
            slippage_ticks=slip_ticks,
        )

    def provenance(self) -> dict[str, Any]:
        """Parameters and their sources, for a result-file manifest."""
        return {
            "fill_profile": self.name,
            "is_assumption": self.is_assumption,
            "status": self.status,
            "entry_slippage_ticks": self.entry_slippage_ticks,
            "stop_slippage_ticks": self.stop_slippage_ticks,
            "target_slippage_ticks": self.target_slippage_ticks,
            "flatten_slippage_ticks": self.flatten_slippage_ticks,
            "gap_through_stop": self.gap_through_stop,
            "require_trade_through_for_target": self.require_trade_through_for_target,
            "commission_per_contract_per_side": self.commission_per_contract_per_side,
            "exchange_fees_per_contract_per_side": self.exchange_fees_per_contract_per_side,
            "sources": self.sources,
        }
