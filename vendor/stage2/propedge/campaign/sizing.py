"""Per-trade sizing from the account's current scaling tier (D-119, slice 4; D-32, D-53, D-117).

Stage one's engine took a dollar risk per trade as a free real number. The contract does not:
a funded account's contract allowance is a **state variable moved by its own P&L** -- the
verified ladder for the 50K account is 2 minis below a $1,500 balance, 3 to $2,000, 5 above
(`funded_scaling_plan`, article 8284223, chart read into `docs/evidence/`), at 10 micros to
the mini -- and a payout that lowers the balance lowers the tier (`scaling_tier_after_payout`,
D-53: a payout is a sizing event). The Combine's ceiling is 5 minis (`combine_position_size_limit`,
article 8284197). The tier is fixed within a session (RULES_LEDGER.md section C: "Max contracts
do not increase mid-session"), so it is read from the balance at the start of each day.

D-117 reconciles stage one's dollar pairs with those counts:

    contracts = min(floor(pair_risk / risk_per_contract), headroom_cap)
    headroom_cap = floor(headroom_frac x the CURRENT tier's micro allowance)

with `headroom_frac` = 0.75 as the declared operating rule (15 micros at the entry tier; T7
sweeps 0.60 to 0.90). The pair's dollar risk is reached only when the stop is wide enough;
below that the realised risk is capped and reported beside the intended pair. The share of
trades sized at the cap is a conduct metric (RTP trigger 2, "You max position a majority of
your trades", article 13620045) and must stay below one half.

Three sizing modes, which together are the band D-32 asked every funded result to carry:

* `fixed_risk`   -- the pair's dollar risk exactly, no contract rounding, no cap: slice 2 and 3
                    unchanged, and the optimistic bound;
* `entry_tier`   -- capped at the entry tier's headroom for the account's whole life: the
                    pessimistic bound, which never scales up;
* `current_tier` -- the model: capped at the current tier's headroom, re-read each session, so
                    growth raises the cap and a payout lowers it.

A trade needs its **risk per contract** (dollars at its stop, per micro contract), which a
`DayBlock` carries when the trade log has a contract count; synthetic blocks state it.
Everything is in micro-equivalent contracts (1 mini = 10 micros, D-52).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np

from propedge.outcomes.distribution import DayBlock

FIXED_RISK = "fixed_risk"
ENTRY_TIER = "entry_tier"
CURRENT_TIER = "current_tier"
MODES = (FIXED_RISK, ENTRY_TIER, CURRENT_TIER)

#: Micros per mini. Quoted in two verified entries' notes -- 8284197 ("Micros and minis count at
#: a 10:1 ratio") and 8284223 ("1 Mini = 10 Micro contracts") -- and recorded as D-52.
MICROS_PER_MINI = 10

#: D-117's declared operating rule; T7 sweeps 0.60 to 0.90.
DEFAULT_HEADROOM_FRAC = 0.75


# ------------------------------------------------------------------------ the ladder


@dataclass(frozen=True)
class ScalingLadder:
    """Balance thresholds (ascending) and the mini allowance from each, in micro-equivalents."""

    thresholds: tuple[float, ...]
    minis: tuple[int, ...]
    micros_per_mini: int = MICROS_PER_MINI
    source: str = ""

    def __post_init__(self) -> None:
        if not self.thresholds or len(self.thresholds) != len(self.minis):
            raise ValueError("a ladder needs one allowance per threshold")
        if list(self.thresholds) != sorted(self.thresholds):
            raise ValueError(f"ladder thresholds must ascend: {self.thresholds}")
        if self.thresholds[0] != 0.0:
            raise ValueError("the first threshold must be 0 (the account starts at a $0 balance)")
        if any(m <= 0 for m in self.minis):
            raise ValueError("every allowance must be positive")

    @classmethod
    def parse(cls, value: str, *, micros_per_mini: int = MICROS_PER_MINI, source: str = "") -> "ScalingLadder":
        """From the ledger's form `0:2,1500:3,2000:5` (balance threshold : minis)."""
        pairs = []
        for item in str(value).split(","):
            lo, minis = item.strip().split(":")
            pairs.append((float(lo), int(minis)))
        return cls(
            thresholds=tuple(p[0] for p in pairs), minis=tuple(p[1] for p in pairs),
            micros_per_mini=micros_per_mini, source=source,
        )

    @classmethod
    def from_ledger(cls, ledger: Any | None = None) -> "ScalingLadder":
        """The verified 50K funded ladder, through the rule gate."""
        if ledger is None:
            from propedge.contract.rules import load_rules

            ledger = load_rules()
        entry = ledger.entry("funded_scaling_plan")
        ladder = cls.parse(
            ledger.value("funded_scaling_plan"),
            source=f"funded_scaling_plan (article {entry.article_id}, read {entry.date_read})",
        )
        declared_entry = int(ledger.value("funded_scaling_entry_tier_minis"))
        if ladder.minis[0] != declared_entry:
            raise ValueError(
                f"the ladder's entry tier ({ladder.minis[0]} minis) disagrees with "
                f"funded_scaling_entry_tier_minis ({declared_entry})"
            )
        return ladder

    def tier_index(self, balance: float) -> int:
        """Index of the tier the balance is in (the highest threshold not above it)."""
        i = 0
        for k, lo in enumerate(self.thresholds):
            if balance >= lo:
                i = k
        return i

    def allowance_micros(self, balance: float) -> int:
        return int(self.minis[self.tier_index(balance)]) * int(self.micros_per_mini)

    @property
    def entry_allowance_micros(self) -> int:
        return int(self.minis[0]) * int(self.micros_per_mini)


# ------------------------------------------------------------------------- the rule


@dataclass(frozen=True)
class SizingRule:
    """How a leg's dollar risk becomes contracts on a given day."""

    mode: str
    ladder: ScalingLadder
    combine_limit_micros: int
    headroom_frac: float = DEFAULT_HEADROOM_FRAC
    #: D-272 (1) as the engine's rule (D-301): per account kind, (the least share of the state's risk the sized trade
    #: must carry, the least risk per micro -- the cost floor, in dollars); a trade below either is no trade for that
    #: account in that slot. None: every sized trade is taken, however little of the risk the cap carries.
    stand_aside: tuple[tuple[str, float, float], ...] | None = None
    #: D-313 (the operator, 2026-10-07): the account kinds whose trades never risk more than the room above the floor --
    #: the contracts cut to the whole micros the room carries ("full port what's left"), so a stop-out loses what was
    #: declared. None: a trade may risk more than the room, and the floor liquidates it there (D-156).
    room_cap: tuple[str, ...] | None = None
    #: D-324 (the v7 audit, finding 2): (round-turn fee a micro, round-turn fee a mini). With it a draw whose blocks carry
    #: each trade's fee per micro-equivalent (`DayBlock.fee`, priced at the log's size) re-prices the fee at the
    #: contracts the trade actually holds -- as many minis as fit, the rest in micros. None: the log's fee stands.
    fee_schedule: tuple[float, float] | None = None

    def __post_init__(self) -> None:
        if self.fee_schedule is not None and (len(self.fee_schedule) != 2 or any(float(x) < 0 for x in self.fee_schedule)):
            raise ValueError(f"fee_schedule is (fee a micro, fee a mini), both at least 0, got {self.fee_schedule!r}")
        if self.mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}, got {self.mode!r}")
        if not 0.0 < self.headroom_frac <= 1.0:
            raise ValueError(f"headroom_frac must be in (0, 1], got {self.headroom_frac}")
        if self.combine_limit_micros <= 0:
            raise ValueError("combine_limit_micros must be positive")
        if self.stand_aside is not None:
            seen = set()
            for entry in self.stand_aside:
                if len(entry) != 3 or entry[0] not in ("combine", "funded"):
                    raise ValueError(f"stand_aside entries are (kind, min_risk_share, floor_risk_per_contract), got {entry!r}")
                kind, share, floor = entry
                if not 0.0 <= float(share) <= 1.0 or float(floor) < 0.0:
                    raise ValueError(f"stand_aside for {kind!r}: the share must be in [0, 1] and the floor at least 0")
                if kind in seen:
                    raise ValueError(f"stand_aside names {kind!r} twice")
                seen.add(kind)
        if self.room_cap is not None and any(k not in ("combine", "funded") for k in self.room_cap):
            raise ValueError(f"room_cap names account kinds 'combine' and 'funded' only, got {self.room_cap!r}")

    def room_capped(self, kind: str) -> bool:
        """D-313: whether `kind`'s trades are cut to the room above the floor."""
        return self.room_cap is not None and kind in self.room_cap

    def fee_dollars(self, micros: int) -> float:
        """D-324: the round-turn fee of a trade `micros` micro-equivalents large -- as many minis as fit, the rest in
        micros (the fill model's mini-mix rule)."""
        if self.fee_schedule is None:
            raise ValueError("no fee schedule")
        n = int(micros)
        minis = n // MICROS_PER_MINI
        return float(minis * float(self.fee_schedule[1]) + (n - minis * MICROS_PER_MINI) * float(self.fee_schedule[0]))

    def stand_aside_for(self, kind: str) -> tuple[float, float] | None:
        """(min_risk_share, floor_risk_per_contract) for `kind`, or None where no stand-aside applies."""
        if self.stand_aside is None:
            return None
        for k, share, floor in self.stand_aside:
            if k == kind:
                return float(share), float(floor)
        return None

    @classmethod
    def from_ledger(
        cls, mode: str = CURRENT_TIER, *, headroom_frac: float = DEFAULT_HEADROOM_FRAC,
        ledger: Any | None = None,
    ) -> "SizingRule":
        if ledger is None:
            from propedge.contract.rules import load_rules

            ledger = load_rules()
        return cls(
            mode=mode,
            ladder=ScalingLadder.from_ledger(ledger),
            combine_limit_micros=int(ledger.value("combine_position_size_limit")) * MICROS_PER_MINI,
            headroom_frac=headroom_frac,
        )

    def allowance_micros(self, kind: str, balance: float) -> int:
        """The tier's full allowance today: the Combine's fixed ceiling, or the ladder's."""
        if kind == "combine":
            return int(self.combine_limit_micros)
        if kind == "funded":
            if self.mode == ENTRY_TIER:
                return self.ladder.entry_allowance_micros
            return self.ladder.allowance_micros(balance)
        raise ValueError(f"kind must be 'combine' or 'funded', got {kind!r}")

    def cap_micros(self, kind: str, balance: float) -> int | None:
        """The headroom cap for today, or None under `fixed_risk`."""
        if self.mode == FIXED_RISK:
            return None
        return int(math.floor(self.headroom_frac * self.allowance_micros(kind, balance)))

    def band(self) -> tuple["SizingRule", "SizingRule", "SizingRule"]:
        """The three modes with these parameters: (entry_tier, current_tier, fixed_risk)."""
        mk = lambda mode: SizingRule(  # noqa: E731
            mode=mode, ladder=self.ladder, combine_limit_micros=self.combine_limit_micros,
            headroom_frac=self.headroom_frac, stand_aside=self.stand_aside, room_cap=self.room_cap,
            fee_schedule=self.fee_schedule,
        )
        return mk(ENTRY_TIER), mk(CURRENT_TIER), mk(FIXED_RISK)

    def as_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "headroom_frac": self.headroom_frac,
            "ladder_thresholds": list(self.ladder.thresholds),
            "ladder_minis": list(self.ladder.minis),
            "micros_per_mini": self.ladder.micros_per_mini,
            "combine_limit_micros": self.combine_limit_micros,
            "ladder_source": self.ladder.source,
            "stand_aside": (None if self.stand_aside is None
                            else {k: {"min_risk_share": s, "floor_risk_per_contract": f} for k, s, f in self.stand_aside}),
            "room_cap": None if self.room_cap is None else list(self.room_cap),
            **({} if self.fee_schedule is None else {"fee_schedule": [float(x) for x in self.fee_schedule]}),   # D-324
        }


# ------------------------------------------------------------------------ one trade


@dataclass(frozen=True)
class SizedTrade:
    contracts: int
    intended_risk: float
    realised_risk: float
    risk_per_contract: float
    cap_micros: int | None
    at_cap: bool

    @property
    def unsized(self) -> bool:
        return self.contracts == 0

    @property
    def intended_capped_risk(self) -> float:
        """D-306: the intention the allowance can carry at this stop -- the pair's risk, or the cap's worth of
        contracts when that is less. Realised over it measures the sizing's fidelity given the allowance (P4);
        realised over the raw intention, beside it, measures how much the allowance binds."""
        if self.cap_micros is None:
            return float(self.intended_risk)
        return float(min(self.intended_risk, int(self.cap_micros) * self.risk_per_contract))


def size_trade(target_risk: float, risk_per_contract: float, cap_micros: int | None) -> SizedTrade:
    """Integer micro contracts for a dollar risk, rounded **down** and capped (D-117).

    `at_cap` is true when the uncapped count reached the cap: that trade is sized at the tier
    maximum the operating rule allows, which is what RTP trigger 2 counts.
    """
    if target_risk <= 0:
        raise ValueError("target_risk must be positive")
    if not risk_per_contract > 0:
        raise ValueError(f"risk_per_contract must be positive, got {risk_per_contract}")
    n = int(math.floor(target_risk / risk_per_contract))
    at_cap = cap_micros is not None and n >= cap_micros
    if cap_micros is not None:
        n = min(n, int(cap_micros))
    return SizedTrade(
        contracts=n, intended_risk=float(target_risk), realised_risk=n * float(risk_per_contract),
        risk_per_contract=float(risk_per_contract), cap_micros=cap_micros, at_cap=bool(at_cap),
    )


# --------------------------------------------------------------------- the draw


@dataclass
class SizingStats:
    """What sizing did to one account, for the record and the conduct metrics."""

    trades: int = 0
    unsized: int = 0
    at_cap: int = 0
    stood_aside: int = 0                 # D-272 (1): the allowance carried too little of the risk, or the stop was under the floor
    need_exits: int = 0                  # D-306: Combine trades closed at what the account needed to pass, short of the state's target
    room_capped: int = 0                 # D-313: trades cut to the room above the floor
    no_outcome: int = 0                  # D-315: slots whose trade has no outcome at the state's R (no trade)
    intended_risk: float = 0.0
    intended_capped_risk: float = 0.0    # D-306: the intention the allowance could carry (SizedTrade.intended_capped_risk)
    realised_risk: float = 0.0
    days_by_allowance: dict[int, int] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "trades": self.trades, "unsized": self.unsized, "at_cap": self.at_cap, "stood_aside": self.stood_aside,
            "need_exits": self.need_exits, "room_capped": self.room_capped, "no_outcome": self.no_outcome,
            "intended_risk": self.intended_risk,
            "intended_capped_risk": self.intended_capped_risk, "realised_risk": self.realised_risk,
            "days_by_allowance": dict(sorted(self.days_by_allowance.items())),
        }


def _log_arrays(blocks: Sequence[DayBlock], rule: SizingRule, cache: dict) -> dict:
    """R11: what a `TierSizedDraw` reads from its log -- each day's arrays as float, its outcomes and MAE at each R, its
    fee, each trade's risk per contract (tier sizing only) and the R values every day carrying outcomes carries --
    built once into `cache` and returned. The caller shares one cache among the accounts drawing from the same list of
    day blocks (`SharedDayDraws`, per group, as `offered_cache`): each account used to convert every day again. The
    values are read, never written, so sharing them changes nothing."""
    if cache.get("blocks") is not None and cache["blocks"] is not blocks:
        raise ValueError("a log cache belongs to one list of day blocks; this one was built from another")
    if "pnl" not in cache:
        carried = [b.r_by_rr for b in blocks if b.r_by_rr is not None]
        cache.update(
            blocks=blocks,
            pnl=[np.asarray(b.pnl, dtype=float) for b in blocks],
            risked=[np.asarray(b.risked, dtype=float) for b in blocks],
            mae=[None if b.mae is None else np.asarray(b.mae, dtype=float) for b in blocks],
            # D-162: outcomes at several R per trade, when the log carries them; `set_risk(risk, rr)` picks one
            r_by_rr=[b.r_by_rr for b in blocks],
            mae_by_rr=[b.mae_by_rr for b in blocks],
            fee=[getattr(b, "fee", None) for b in blocks],     # D-324: the fee a micro-equivalent the log priced in
            # the R values every day that carries outcomes carries (`set_risk` refuses any other); None: no day does
            rr_everywhere=frozenset(set.intersection(*(set(r) for r in carried))) if carried else None,
        )
    if rule.mode != FIXED_RISK and "rpc" not in cache:
        rpc = []
        for b in blocks:
            if b.risk_per_contract is None:
                raise ValueError(
                    "tier sizing needs each trade's risk per contract, which these day "
                    "blocks do not carry: build them from a trade log with a contract "
                    "count, or state risk_per_contract when synthesising them"
                )
            rpc.append(np.asarray(b.risk_per_contract, dtype=float))
        cache["rpc"] = rpc
    return cache


class TierSizedDraw:
    """An account's draw with per-session tier sizing over a day table.

    Called as `draw(1, rel_day, slot, cushion)` like every draw here. The lockstep loop calls
    `begin_session(balance, floor)` before the account's first slot each day, which is where
    the tier is read (the balance at the start of the session; the cap is fixed within it).

    Under `fixed_risk` the dollar P&L is `pnl x (target / risked)`, the same arithmetic as
    `shared_days.scaled_pnl`, so that mode is bit-identical to slices 2 and 3. Under the tier
    modes it is `pnl x (realised / risked)` with `realised = contracts x risk_per_contract`,
    which equals the fixed-risk value exactly whenever the cap does not bind and the pair's
    risk is a whole number of contracts.

    **Need-aware exits (D-306; the operator, 2026-10-06).** The lockstep loop may call the draw with `need=`: the
    dollars the Combine must net on this trade to pass at the lock. When the log carries outcomes at several R
    (D-162) and the need is below the state's target, the trade is closed at the need instead of run to the full
    target: the draw walks the carried R values from the smallest at or above `need / realised risk` up to the
    state's R; the first whose net outcome reaches the need settles the trade at exactly the need (`at_need`); a
    stopped trade (an outcome at or below zero) is the same at every target and settles as it is; an outcome short
    of the need but positive (a target hit whose costs leave it short, or a flatten, which is the same at every
    target) moves on to the next R; a trade stopped or scratched before the need settles at the state's own R outcome
    (D-314: once each R is shifted to its own lower bound the losses differ by target, and the trade was placed as the
    state's bracket). The MAE is the bracket's that settled it, so a breach before the exit is still a breach (D-156).
    `takes_need` tells the loop the draw honours it.
    """

    takes_need = True

    def __init__(
        self,
        table: Any,
        blocks: Sequence[DayBlock],
        *,
        start_day: int,
        kind: str,
        rule: SizingRule,
        target_risk: float,
        relative_days: bool = False,
        router: Any | None = None,
        key: tuple[str, int] | None = None,
        settlement: str | None = None,
        offered_cache: dict | None = None,
        log_cache: dict | None = None,
    ):
        """`relative_days=True` indexes the table by the account's own engine day rather than
        the calendar day: for a private (independent) table that is the same assignment
        `EmpiricalDraw` makes, so the unsized and sized independent draws agree exactly; a
        shared table is always indexed by the calendar day. `router` and `key` route the
        day's trades under `rotation` mode (`shared_days.TradeRouter`). `settlement` is how a
        trade that risks more than the room settles (D-156, `propedge.outcomes.settlement`);
        None: `mae` when every block carries MAE, else `pessimistic`. `log_cache` (R11): a dict the
        accounts drawing from the same `blocks` share, so the log's arrays are built once
        (`_log_arrays`); None builds them for this account alone, as before."""
        from propedge.outcomes.settlement import TRADE_LOG_SETTLEMENTS, default_trade_log_settlement

        if kind not in ("combine", "funded"):
            raise ValueError(f"kind must be 'combine' or 'funded', got {kind!r}")
        if target_risk <= 0:
            raise ValueError("target_risk must be positive")
        self.settlement = settlement or default_trade_log_settlement(list(blocks))
        if self.settlement not in TRADE_LOG_SETTLEMENTS:
            raise ValueError(f"a trade-log draw settles by one of {TRADE_LOG_SETTLEMENTS}, got {self.settlement!r}")
        self.table = table
        self.start_day = int(start_day)
        self.relative_days = bool(relative_days)
        self.router = router
        self.base_risk = float(target_risk)
        self.key = key
        self.last_trade: dict[str, Any] | None = None
        self.kind = kind
        self.rule = rule
        self.target_risk = float(target_risk)
        self.stats = SizingStats()
        self._cap: int | None = None
        self._session_open = False
        self.current_allowance_micros: int | None = None   # set by begin_session
        self.current_cap_micros: int | None = None

        # R11: the log's arrays, built once per log when the caller shares `log_cache` (`_log_arrays`)
        log = _log_arrays(blocks, rule, {} if log_cache is None else log_cache)
        self._pnl, self._risked, self._mae = log["pnl"], log["risked"], log["mae"]
        # D-162: outcomes at several R per trade, when the log carries them; `set_risk(risk, rr)` picks one
        self._r_by_rr, self._mae_by_rr = log["r_by_rr"], log["mae_by_rr"]
        self._fee = log["fee"]                                  # D-324: the fee a micro-equivalent the log priced in
        self._rr_everywhere: frozenset | None = log["rr_everywhere"]
        self._rr: float | None = None
        # D-368: the second trades taken in the stretch mode, those closed at the need, and those whose need lay beyond
        # the menu's widest target
        self.stretch_trades = 0
        self.stretch_at_need = 0
        self.stretch_out_of_menu = 0
        self._rpc = None if rule.mode == FIXED_RISK else log["rpc"]     # checked by `_log_arrays`
        # D-318 / D-319: the smallest stop offering each R, read once per log -- shared by every account of a path when
        # the caller passes `offered_cache` (the v6 audit: each attempt rescanned the log)
        self._min_rpc: dict[float | None, float] = {} if offered_cache is None else offered_cache
        register = getattr(router, "register", None)
        if register is not None and key is not None:
            register(key, self)                         # D-318: the router asks the draw which trades it can take

    def _min_offered_rpc(self, rr: float | None) -> float:
        """D-318: the least risk per micro among the log's trades that carry an outcome at `rr` (every trade when None)
        -- the smallest stop at which the account's R is ever offered. A property of the log, read once per R."""
        if rr not in self._min_rpc:
            rpcs, oks = [], []
            for h, rpc in enumerate(self._rpc or []):
                by = self._r_by_rr[h]
                if not len(rpc) or (rr is not None and (by is None or rr not in by)):
                    continue
                rpcs.append(rpc)
                oks.append(np.ones(len(rpc), bool) if rr is None else np.isfinite(np.asarray(by[rr], float)))
            if rpcs:
                allr, allok = np.concatenate(rpcs), np.concatenate(oks)
                self._min_rpc[rr] = float(np.min(allr[allok])) if allok.any() else np.inf
            else:
                self._min_rpc[rr] = np.inf
        return self._min_rpc[rr]

    def out_of_room(self, balance: float, floor: float) -> bool:
        """D-318: a room-capped account whose room above the floor buys no micro at any stop its state's R is offered
        at can never trade again, and never fails -- out of room. False where the room is not capped."""
        if not self.rule.room_capped(self.kind) or self._rpc is None:
            return False
        return float(balance) - float(floor) + 1e-9 < self._min_offered_rpc(self._rr)

    def can_take(self, h: int, j: int, balance: float, floor: float) -> bool:
        """D-318: whether trade `j` of historical day `h` would be taken by this account at the start of today's session
        -- an outcome at the state's R (the room rule, read at entry), a stop at or above the cost floor, and at least
        one micro under the allowance and (where capped) the room. Nothing about the trade's outcome is read beyond
        whether the room rule permits the R, so routing on it looks at nothing the entry does not know."""
        if self._rr is not None and not np.isfinite(float(self._r_by_rr[h][self._rr][j])):
            return False
        room = float(balance) - float(floor)
        room_cap = self.rule.room_capped(self.kind)
        if self.rule.mode == FIXED_RISK:
            return (min(self.target_risk, room) if room_cap else self.target_risk) > 0
        sized = size_trade(self.target_risk, float(self._rpc[h][j]), self.rule.cap_micros(self.kind, float(balance)))
        sa = self.rule.stand_aside_for(self.kind)
        if sa is not None and (sized.realised_risk + 1e-9 < sa[0] * sized.intended_risk
                               or sized.risk_per_contract + 1e-9 < sa[1]):
            return False
        n = sized.contracts
        if room_cap:
            n = min(n, int(math.floor(max(room, 0.0) / sized.risk_per_contract + 1e-9)))
        return n >= 1

    def set_risk(self, risk: float, rr: float | None = None) -> None:
        """D-147: size the next trades to `risk` dollars. A trade log fixed R when each stop and
        target were placed, so a policy that sets R is refused -- unless the log carries each
        trade's outcome at that R (D-162: `DayBlock.r_by_rr`), in which case the next trades are
        read at it."""
        if rr is not None:
            rr = float(rr)
            if self._rr_everywhere is None or rr not in self._rr_everywhere:     # R11: read once per log
                raise ValueError(
                    "this draw replays trades whose R was fixed by their stop and target; a risk "
                    "policy may change the dollar risk (contracts) but not R, unless the log carries "
                    f"every trade's outcome at R = {rr:g} (DayBlock.r_by_rr, D-162). Leave the policy's rr "
                    "empty, or export the strategy's outcomes at that R"
                )
        if not risk > 0:
            raise ValueError("risk must be positive")
        self.target_risk = float(risk)
        self._rr = rr

    def begin_session(self, balance: float, floor: float) -> None:
        """Read the tier from the balance at the start of the day; the cap holds all day."""
        self._cap = self.rule.cap_micros(self.kind, float(balance))
        allowance = self.rule.allowance_micros(self.kind, float(balance))
        self.current_allowance_micros = allowance
        self.current_cap_micros = self._cap
        self.stats.days_by_allowance[allowance] = self.stats.days_by_allowance.get(allowance, 0) + 1
        self._session_open = True

    def _outcome(self, h: int, j: int) -> tuple[float, float]:
        """(net outcome, MAE) in units of the trade's risk: the log's own, or at the R the state calls for (D-162)."""
        risked = self._risked[h][j]
        if self._rr is None:
            u = float(self._pnl[h][j] / risked) if risked > 0 else float("nan")
            mae_u = (float(self._mae[h][j] / risked) if self._mae[h] is not None and risked > 0
                     else float("nan"))             # MAE in units of the trade's own risk
            return u, mae_u
        u = float(self._r_by_rr[h][self._rr][j])
        by = self._mae_by_rr[h]
        return u, (float(by[self._rr][j]) if by is not None and self._rr in by else float("nan"))

    def _need_exit(self, h: int, j: int, risk: float, need: float | None, u: float, mae_u: float, adj: float = 0.0
                   ) -> tuple[float, float, float | None, bool]:
        """D-306: (outcome, MAE, the R that settled it, closed at the need). See the class docstring. `adj` (D-324):
        the fee re-pricing in R, added to every R's outcome the walk reads (`u` arrives with it already)."""
        if need is None or self._rr is None or not risk > 0 or not np.isfinite(need) or need <= 0:
            return u, mae_u, self._rr, False
        by = self._r_by_rr[h]
        need_r = float(need) / float(risk)
        if by is None or need_r > self._rr + 1e-9:          # the state's own target cannot pass: the trade as it is
            return u, mae_u, self._rr, False
        maes = self._mae_by_rr[h]
        for R in sorted(k for k in by if need_r - 1e-9 <= k <= self._rr + 1e-9):
            u_r = float(by[R][j]) + float(adj)
            if np.isnan(u_r):
                continue                                     # this target is not permitted for the trade
            if u_r >= need_r - 1e-9:                         # the net outcome at this target reaches the need
                m = float(maes[R][j]) if maes is not None and R in maes else float("nan")
                return u_r, m, float(R), True
            if u_r <= 0.0:
                # D-314: stopped or scratched before the need -- the trade was placed as the state's bracket and the
                # need-aware exit is a take-profit only, so it settles at the state's own R outcome and MAE (each R's
                # outcomes differ once shifted to their own lower bound; before D-314 this returned this R's)
                return u, mae_u, self._rr, False
        return u, mae_u, self._rr, False                     # no carried target reaches it: the state's own outcome

    def _plain_size(self, h: int, j: int, room: float, cap_micros: int | None) -> tuple[dict[str, Any] | None, str]:
        """D-368: trade `j` of historical day `h` sized as `__call__` sizes it -- the state's dollar risk in whole micros
        under `cap_micros`, the stand-aside, the room cap, the fee re-priced at the contracts (D-324) -- without touching
        the stats. (the size, "") or (None, "stood_aside" | "unsized")."""
        room_cap = self.rule.room_capped(self.kind) and np.isfinite(room)
        if self.rule.mode == FIXED_RISK:
            risk = min(self.target_risk, max(room, 0.0)) if room_cap else self.target_risk
            if not risk > 0:
                return None, "unsized"
            return {"risk": risk, "intended": self.target_risk, "capped_intention": risk, "contracts": None,
                    "rpc": None, "cap_micros": None, "at_cap": False, "adj": 0.0, "fee": None}, ""
        sized = size_trade(self.target_risk, float(self._rpc[h][j]), cap_micros)
        sa = self.rule.stand_aside_for(self.kind)
        if sa is not None and (sized.realised_risk + 1e-9 < sa[0] * sized.intended_risk
                               or sized.risk_per_contract + 1e-9 < sa[1]):
            return None, "stood_aside"
        capped_intention = sized.intended_capped_risk
        n = sized.contracts
        if room_cap:
            n = min(n, int(math.floor(max(room, 0.0) / sized.risk_per_contract + 1e-9)))
            capped_intention = min(capped_intention, max(room, 0.0))
        if n < 1:
            return None, "unsized"
        risk = n * sized.risk_per_contract
        adj, fee = 0.0, None
        fees = self._fee[h]
        if self.rule.fee_schedule is not None and fees is not None:
            fee = self.rule.fee_dollars(n)
            adj = (float(fees[j]) * n - fee) / risk
        return {"risk": risk, "intended": sized.intended_risk, "capped_intention": capped_intention, "contracts": n,
                "rpc": sized.risk_per_contract, "cap_micros": sized.cap_micros, "at_cap": sized.at_cap,
                "adj": adj, "fee": fee}, ""

    def trade_dollars(self, h: int, j: int, balance: float, floor: float) -> float | None:
        """D-368: the net dollars trade `j` of historical day `h` closes at for this account -- at its state's R and the
        size it holds at today's session start (the allowance read from `balance`), before any settlement against the
        floor -- or None when the account would not take it. The router reads it for an account's first trade of the
        day, which has closed before the second signal's entry, to know whether the day stands short of the
        winning-day minimum."""
        u, _ = self._outcome(h, j)
        if not np.isfinite(u):
            return None
        cap = None if self.rule.mode == FIXED_RISK else self.rule.cap_micros(self.kind, float(balance))
        s, _why = self._plain_size(h, j, float(balance) - float(floor), cap)
        if s is None:
            return None
        return (u + s["adj"]) * s["risk"]

    def _stretch_start(self, h: int, j: int, need_r: float) -> tuple[float | None, str]:
        """D-368: the second trade's bracket -- the smallest carried R at or above the shortfall `need_r` that the room
        rule permits for trade `j` (an entry-known fact, as `can_take` reads it); (None, "out_of_menu") when the
        shortfall is beyond the menu's widest target, (None, "no_outcome") when the room permits none that reaches it."""
        by = self._r_by_rr[h]
        grid = sorted(float(k) for k in by if k >= need_r - 1e-9) if by is not None else []
        if not grid:
            return None, "out_of_menu"
        for R in grid:
            if np.isfinite(float(by[R][j])):
                return R, ""
        return None, "no_outcome"

    def can_stretch(self, h: int, j: int, balance: float, floor: float, need: float, first: float = 0.0) -> bool:
        """D-368: whether this account would take trade `j` as its second trade for a shortfall of `need` dollars --
        `balance` and `floor` the session start's (the allowance is read from them, as `begin_session` will read it;
        the router runs before it), `first` the first trade's net dollars, so the room is the one after it: at least one
        micro, a carried target at or above the shortfall that the room rule permits. Reads no outcome."""
        if not (np.isfinite(need) and need > 0):
            return False
        cap = None if self.rule.mode == FIXED_RISK else self.rule.cap_micros(self.kind, float(balance))
        s, _why = self._plain_size(h, j, float(balance) + float(first) - float(floor), cap)
        if s is None:
            return False
        R, _why = self._stretch_start(h, j, float(need) / s["risk"])
        return R is not None

    def _stretch(self, h: int, j: int, cushion: np.ndarray, need: float | None) -> np.ndarray:
        """D-368: an XFA's second trade of a day whose first left it short of the winning-day minimum. Sized as any
        trade (`_plain_size`), with a take-profit at `need` -- the shortfall -- read as D-306's need-aware exit reads
        one: the carried targets from the shortfall upward, the first whose net outcome reaches the need closes it at
        exactly the need; a target stopped or scratched before it (net outcome at or below zero) settles there; a target
        reached but short of the need after costs passes to the next; none reaching it settles at the last read. The
        discrete menu can only miss a need reached between two targets: a pessimistic reading, never an optimistic one.
        No carried target at or above the shortfall that the room permits: no trade."""
        if self._r_by_rr[h] is None or need is None or not np.isfinite(need) or need <= 0:
            return np.array([np.nan])
        if self.rule.mode != FIXED_RISK and not self._session_open:
            raise RuntimeError("TierSizedDraw was called before begin_session()")
        room = float(np.asarray(cushion, dtype=float).ravel()[0])
        s, why = self._plain_size(h, j, room, None if self.rule.mode == FIXED_RISK else self._cap)
        if s is None:
            if why == "stood_aside":
                self.stats.stood_aside += 1
            else:
                self.stats.unsized += 1
            return np.array([np.nan])
        risk, adj = float(s["risk"]), float(s["adj"])
        need_r = float(need) / risk
        R0, why = self._stretch_start(h, j, need_r)
        if R0 is None:
            if why == "out_of_menu":
                self.stretch_out_of_menu += 1               # the shortfall is beyond the menu's widest target
            else:
                self.stats.no_outcome += 1                  # the room rule permits no target that reaches it
            return np.array([np.nan])
        by, maes = self._r_by_rr[h], self._mae_by_rr[h]
        u, R, at_need = float("nan"), R0, False
        for k in sorted(float(x) for x in by if x >= R0 - 1e-9):
            u_k = float(by[k][j])
            if not np.isfinite(u_k):
                continue                                    # the room does not permit this target
            u, R = u_k + adj, k
            if u >= need_r - 1e-9:
                at_need = True                              # the need reached: closed at it
                break
            if u <= 0.0:
                break                                       # stopped or scratched before the need
        mae_u = float(maes[R][j]) if maes is not None and R in maes else float("nan")
        if np.isfinite(mae_u):
            mae_u = max(mae_u, -u)
        self.stats.trades += 1
        self.stats.intended_risk += float(s["intended"])
        self.stats.intended_capped_risk += float(s["capped_intention"])
        self.stats.realised_risk += risk
        self.stats.need_exits += int(at_need)
        if s["at_cap"]:
            self.stats.at_cap += 1
        self.stretch_trades += 1
        self.stretch_at_need += int(at_need)
        self.last_trade = {
            "historical_day": h, "trade_index": int(j), "u": u, "contracts": s["contracts"],
            "intended_risk": s["intended"], "realised_risk": risk, "intended_capped_risk": s["capped_intention"],
            "risk_per_contract": s["rpc"], "cap_micros": s["cap_micros"], "at_cap": s["at_cap"], "mae": mae_u * risk,
            "settlement": self.settlement, "rr": R0, "rr_used": R, "need": need, "at_need": at_need,
            "room": room, "stretch": True, **({} if s["fee"] is None else {"fee": s["fee"], "fee_adj_r": adj}),
        }
        return self._settle(float(need) if at_need else u * risk, risk, mae_u * risk, cushion)

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray, need: float | None = None,
                 stretch: bool = False) -> np.ndarray:
        if n != 1:
            raise ValueError(f"TierSizedDraw serves one account at a time, got n={n}")
        self.last_trade = None
        t = int(day) if self.relative_days else self.start_day + 1 + int(day)
        h = self.table.historical_day(t)
        if h < 0:
            return np.array([np.nan])
        pnl = self._pnl[h]
        j = slot if self.router is None else self.router.trade_index(self.key, t, slot)
        if j is None or j >= len(pnl):
            return np.array([np.nan])
        if stretch:                                         # D-368: the second trade's own bracket
            return self._stretch(h, j, cushion, need)
        u, mae_u = self._outcome(h, j)
        if self._rr is not None and not np.isfinite(u):
            # D-315 (D-162): no outcome at the state's R -- the room rule leaves it blank -- is no trade in this slot,
            # need or not, decided before the need-aware walk could find a win at a lower target (a look-ahead that
            # D-314's walk let through); not counted among the sized trades
            self.stats.no_outcome += 1
            self.last_trade = None
            return np.array([np.nan])
        room = float(np.asarray(cushion, dtype=float).ravel()[0])
        room_cap = self.rule.room_capped(self.kind) and np.isfinite(room)
        if self.rule.mode == FIXED_RISK:
            risk = self.target_risk
            capped_by_room = room_cap and risk > room + 1e-9
            if capped_by_room:                          # D-313: never more than the room above the floor
                risk = max(room, 0.0)
            if not risk > 0:
                self.stats.unsized += 1
                return np.array([np.nan])
            u, mae_u, rr_used, at_need = self._need_exit(h, j, risk, need, u, mae_u)
            self.stats.trades += 1
            self.stats.intended_risk += self.target_risk
            self.stats.intended_capped_risk += risk
            self.stats.realised_risk += risk
            self.stats.need_exits += int(at_need)
            self.stats.room_capped += int(capped_by_room)
            self.last_trade = {
                "historical_day": h, "trade_index": int(j), "u": u, "contracts": None,
                "intended_risk": self.target_risk, "realised_risk": risk, "intended_capped_risk": risk,
                "risk_per_contract": None, "cap_micros": None, "at_cap": False,
                "mae": mae_u * risk, "settlement": self.settlement, "rr": self._rr, "rr_used": rr_used,
                "need": need, "at_need": at_need, "room": room, "room_capped": bool(capped_by_room),
            }
            return self._settle(float(need) if at_need else u * risk, risk, mae_u * risk, cushion)
        if not self._session_open:
            raise RuntimeError(
                "TierSizedDraw was called before begin_session(): the tier must be read from "
                "the balance at the start of the day"
            )
        sized = size_trade(self.target_risk, float(self._rpc[h][j]), self._cap)
        sa = self.rule.stand_aside_for(self.kind)
        if sa is not None and (sized.realised_risk + 1e-9 < sa[0] * sized.intended_risk
                               or sized.risk_per_contract + 1e-9 < sa[1]):
            # D-272 (1) as the engine's rule (D-301): the allowance carries too little of the state's risk at this
            # stop, or the stop is under the cost floor -- no trade in this slot for this account
            self.stats.stood_aside += 1
            self.last_trade = {
                "historical_day": h, "trade_index": int(j), "u": u, "contracts": 0,
                "intended_risk": sized.intended_risk, "realised_risk": 0.0,
                "intended_capped_risk": sized.intended_capped_risk,
                "risk_per_contract": sized.risk_per_contract, "cap_micros": sized.cap_micros,
                "at_cap": False, "mae": 0.0, "settlement": self.settlement, "rr": self._rr, "stood_aside": True,
            }
            return np.array([np.nan])
        capped_intention = sized.intended_capped_risk
        capped_by_room = False
        if room_cap:                                    # D-313: the whole micros the room above the floor carries
            n_room = int(math.floor(max(room, 0.0) / sized.risk_per_contract + 1e-9))
            if n_room < sized.contracts:
                capped_by_room = True
                sized = SizedTrade(contracts=n_room, intended_risk=sized.intended_risk,
                                   realised_risk=n_room * sized.risk_per_contract,
                                   risk_per_contract=sized.risk_per_contract, cap_micros=sized.cap_micros,
                                   at_cap=sized.at_cap)
            capped_intention = min(capped_intention, max(room, 0.0))
        # D-324 (the v7 audit, finding 2): the fee at the contracts this trade holds -- as many minis as fit, the rest
        # in micros -- in place of the fee the log priced at its own size; every R's outcome moves by the same amount
        adj, fee_paid = 0.0, None
        fees = self._fee[h]
        if self.rule.fee_schedule is not None and fees is not None and sized.contracts > 0:
            fee_paid = self.rule.fee_dollars(sized.contracts)
            adj = (float(fees[j]) * sized.contracts - fee_paid) / sized.realised_risk
            u = u + adj
            if np.isfinite(mae_u):
                mae_u = max(mae_u, -u)                  # the MAE is never below the loss it closes at
        u, mae_u, rr_used, at_need = self._need_exit(h, j, sized.realised_risk, need, u, mae_u, adj)
        self.stats.trades += 1
        self.stats.intended_risk += sized.intended_risk
        self.stats.intended_capped_risk += capped_intention
        self.stats.realised_risk += sized.realised_risk
        self.stats.need_exits += int(at_need)
        self.stats.room_capped += int(capped_by_room)
        if sized.at_cap:
            self.stats.at_cap += 1
        self.last_trade = {
            "historical_day": h, "trade_index": int(j), "u": u, "contracts": sized.contracts,
            "intended_risk": sized.intended_risk, "realised_risk": sized.realised_risk,
            "intended_capped_risk": capped_intention,
            "risk_per_contract": sized.risk_per_contract, "cap_micros": sized.cap_micros,
            "at_cap": sized.at_cap, "mae": mae_u * sized.realised_risk, "settlement": self.settlement,
            "rr": self._rr, "rr_used": rr_used, "need": need, "at_need": at_need,
            "room": room, "room_capped": capped_by_room,
            **({} if fee_paid is None else {"fee": fee_paid, "fee_adj_r": adj}),     # D-324
        }
        if sized.unsized:
            self.stats.unsized += 1
            return np.array([np.nan])           # no trade: the risk does not buy one contract
        return self._settle(float(need) if at_need else u * sized.realised_risk, sized.realised_risk,
                            mae_u * sized.realised_risk, cushion)

    def _settle(self, pnl: float, risk: float, mae: float, cushion: np.ndarray) -> np.ndarray:
        """D-156: settle the trade against the room the engine handed over as `cushion`."""
        from propedge.outcomes.settlement import settle

        return settle(np.array([float(pnl)]), np.array([float(risk)]), np.array([float(mae)]),     # R11: the risk in
                      np.asarray(cushion, dtype=float), self.settlement)                          # the trade's shape

    def provenance(self) -> dict[str, Any]:
        return {"draw": "TierSizedDraw", "kind": self.kind, "target_risk": self.target_risk,
                "settlement": self.settlement, **self.rule.as_dict()}


__all__ = [
    "FIXED_RISK",
    "ENTRY_TIER",
    "CURRENT_TIER",
    "MODES",
    "MICROS_PER_MINI",
    "DEFAULT_HEADROOM_FRAC",
    "ScalingLadder",
    "SizingRule",
    "SizedTrade",
    "size_trade",
    "SizingStats",
    "TierSizedDraw",
]
