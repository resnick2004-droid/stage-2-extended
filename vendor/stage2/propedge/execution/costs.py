"""Per-trade cost in dollars, and the cost drag that makes the small-bet penalty visible.

D-03: costs are modelled in contracts and ticks, never as a fraction of dollar risk. The
reason is this module's second function. A fractional-drag model hides a real effect:

    cost per trade = contracts x (commission + slippage per contract)
    contracts      = dollar_risk / (stop_ticks x tick_value)

so cost scales with *size*, and cost **as a share of risk** is roughly constant in size but
inversely proportional to *stop distance*. Halve the stop and you double the contracts for
the same dollar risk, doubling the commission bill while the dollar risk is unchanged. A
tight-stop strategy can be arbitrarily good gross and hopeless net, and a drag model
expressed as a flat fraction of risk cannot show it.

`cost_drag_fraction` is therefore reported with every candidate: it is the number of
percentage points of edge that costs consume, directly comparable to the `e >= 0.10`
criterion. A candidate with a gross edge of 0.12 and a drag of 0.04 does not pass.
"""
from __future__ import annotations

from dataclasses import dataclass

from propedge.execution.fills import ExitReason, FillModel, Side
from propedge.execution.instruments import Instrument


@dataclass(frozen=True)
class TradeCost:
    """The cost of one round turn, in dollars and as a share of dollars risked."""

    contracts: int
    commission: float
    slippage_dollars: float
    dollars_risked: float

    @property
    def total(self) -> float:
        return self.commission + self.slippage_dollars

    @property
    def drag_fraction(self) -> float:
        """Total cost as a fraction of dollars risked.

        Directly comparable to the edge criterion: a drag of 0.04 means costs eat 4
        percentage points of `e`, so a gross edge of 0.12 nets 0.08 and fails `e >= 0.10`.
        """
        if self.dollars_risked <= 0:
            return float("nan")
        return self.total / self.dollars_risked

    @property
    def drag_ticks_per_contract(self) -> float:
        """Total cost expressed back in ticks per contract -- the unit costs are quoted in."""
        if self.contracts <= 0:
            return float("nan")
        return self.total / self.contracts


def round_turn_commission(
    fill_model: FillModel, contracts: int, instrument: Instrument | None = None
) -> float:
    """All-in round-turn cost for `contracts` contracts.

    `instrument` becomes required once `config/fills.yaml` carries per-instrument round turns:
    the flat fallback is then refused rather than applied silently, because one figure across
    contract sizes reverses the mini-versus-micro comparison instead of merely blurring it.
    See `propedge.execution.fills.FlatCommissionError`.
    """
    return fill_model.commission_for(
        contracts, instrument.symbol if instrument is not None else None
    )


def expected_slippage_dollars(
    fill_model: FillModel,
    instrument: Instrument,
    contracts: int,
    *,
    exit_reason: ExitReason = ExitReason.STOP,
) -> float:
    """Expected adverse slippage for an entry plus one exit, in dollars.

    Which exit fires matters: a stop is a market order and slips, a resting-limit target does
    not. Pricing every trade at the stop's slippage overstates costs for a strategy that
    mostly reaches its target, and pricing at the target's understates them for one that
    mostly stops out. Use the realised exit mix from the trade log where you have one.
    """
    exit_ticks = {
        ExitReason.STOP: fill_model.stop_slippage_ticks,
        ExitReason.TARGET: fill_model.target_slippage_ticks,
        ExitReason.FLATTEN: fill_model.flatten_slippage_ticks,
        ExitReason.OTHER: fill_model.flatten_slippage_ticks,
    }[exit_reason]
    ticks = fill_model.entry_slippage_ticks + exit_ticks
    return instrument.ticks_to_dollars(ticks, contracts)


def trade_cost(
    fill_model: FillModel,
    instrument: Instrument,
    *,
    contracts: int,
    dollars_risked: float,
    exit_reason: ExitReason = ExitReason.STOP,
) -> TradeCost:
    """Cost of one round turn.

    Args:
        contracts: integer contracts actually traded (from
            `propedge.execution.instruments.contracts_for_risk`).
        dollars_risked: the **realised** dollar risk of that integer size, not the intended
            one -- the denominator has to match the position that was actually taken.
        exit_reason: which exit to price the slippage at.
    """
    return TradeCost(
        contracts=contracts,
        commission=round_turn_commission(fill_model, contracts, instrument),
        slippage_dollars=expected_slippage_dollars(
            fill_model, instrument, contracts, exit_reason=exit_reason
        ),
        dollars_risked=dollars_risked,
    )


def cost_drag_fraction(
    fill_model: FillModel,
    instrument: Instrument,
    *,
    stop_ticks: float,
    dollar_risk: float,
    exit_reason: ExitReason = ExitReason.STOP,
) -> float:
    """Cost drag as a fraction of dollars risked, sized from the stop distance.

    A convenience over `trade_cost` for sweeping stop distances and risks to see where the
    small-bet and tight-stop penalties bite. Rounds contracts down, as the sizing rule does,
    and returns NaN if the risk does not buy one contract.
    """
    per_contract = instrument.dollars_per_contract(stop_ticks)
    contracts = int(dollar_risk // per_contract)
    if contracts < 1:
        return float("nan")
    realised = contracts * per_contract
    return trade_cost(
        fill_model,
        instrument,
        contracts=contracts,
        dollars_risked=realised,
        exit_reason=exit_reason,
    ).drag_fraction


def net_edge_from_gross(
    gross_edge: float,
    fill_model: FillModel,
    instrument: Instrument,
    *,
    stop_ticks: float,
    dollar_risk: float,
    exit_reason: ExitReason = ExitReason.STOP,
) -> float:
    """Net edge after costs: `gross_edge - drag`.

    A first-order convenience for sizing sweeps and feasibility checks. It is **not** a
    substitute for measuring the net edge from a trade log whose fills were priced by the
    fill model -- the realised exit mix, gapped stops and flattened trades do not reduce to a
    single subtraction. Use it to ask "can this candidate possibly clear the criterion?",
    not to report a result.
    """
    drag = cost_drag_fraction(
        fill_model,
        instrument,
        stop_ticks=stop_ticks,
        dollar_risk=dollar_risk,
        exit_reason=exit_reason,
    )
    return gross_edge - drag
