"""Shared calendar days across accounts: the copier and partitioned layouts (D-119, slice 3).

The accounts of a campaign trade the same market on the same days, and under the firm's
first-party copier (`multi_account_same_strategy`, article 8284215, D-22) their positions are
identical. The stage-level model and slice 2's independent draws resample each account's days
on their own, so the event the Responsible Trading Program names first -- "Multiple accounts
hit the Maximum Loss Limit in one day" (article 13620045, D-30) -- has probability near zero
in them by construction, and every multi-account ranking they produce is an upper bound. D-30
asked for a sensitivity arm in which correlated accounts share their days. This module is that
arm, as draw factories for `propedge.campaign.lockstep`.

One table per path maps every calendar day to one historical day, drawn once and shared by
every account. Three modes:

* **copier** -- one strategy, one group. Every account trading on a calendar day receives the
  same historical day's trades, scaled to its leg's dollar risk. Accounts that start on the
  same day are then identical and breach together by construction; accounts that started on
  different days carry different cushions and can diverge, which is the honest reading of the
  copier: it copies trades, not account state.
* **partitioned** -- several strategies, one per group, with their day blocks aligned by date
  (block `h` in every group is the same historical day, D-108a). Each account reads its own
  group's block for the shared historical day, so cross-strategy correlation enters through
  the common day and nothing else is assumed about it.
* **independent** -- each account resamples its own days (`EmpiricalDraw` with a child seed):
  exactly slice 2, kept here so the reduction is one flag away.

What is not modelled: sizing is the leg's dollar risk, as `EmpiricalDraw` scales it, until
slice 4 sizes each trade from the account's scaling tier; the copier's own restrictions (the
lead account's position ceiling, six listed restrictions) are conduct constraints scored in
T7, not mechanics here.
"""
from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

import numpy as np

from propedge.campaign.lockstep import DrawFactory, child_seed
from propedge.campaign.protocols import Protocol
from propedge.campaign.sizing import SizingRule, TierSizedDraw
from propedge.outcomes.distribution import DayBlock, EmpiricalDraw

COPIER = "copier"
PARTITIONED = "partitioned"
INDEPENDENT = "independent"
#: Each trade goes to the next live account in turn (D-130): one strategy, one position open
#: across the campaign at any time, each account seeing a share of the trades.
ROTATION = "rotation"
MODES = (COPIER, PARTITIONED, INDEPENDENT, ROTATION)

#: An account's key in the routing order: ("combine" | "funded", index).
AccountKey = tuple[str, int]

#: D-568: the opt-in routing rules. Each changes only the ORDER in which rotation offers a trade to the live accounts;
#: every check after it -- the session's cap, flat at the entry, `able`'s can-take, the strict one-at-a-time rule, the
#: opposite-side rule -- is unchanged, and the longest-waiting order (D-216) breaks every tie. None (the default) is the
#: longest-waiting order itself (D-568's R0), so every recorded run routes as before.
#:   fixed_order      R1: the day's accounts (the lockstep loop's order: earliest start first, funded before Combine on
#:                    a tie, then index) in a fixed cycle, the next trade offered first to the account after the one
#:                    the last routed trade went to (the pre-D-216 rotation, by position)
#:   combine_first    R2: Combines before funded accounts
#:   funded_first     R3: funded accounts before Combines
#:   most_room        R4: the largest cushion first (balance less floor at the session's start, the day hook's states)
#:   closest_to_goal  R5: the highest progress first -- a Combine's balance over its profit target, a funded account's
#:                    winning days over the Standard path's required days (written by the lockstep loop each day,
#:                    `TradeRouter.progress`); a unit-free share so the two kinds rank on one scale
#:   random           R6: a fresh fair permutation for every trade, from a generator seeded by (ROUTING_RANDOM_SEED,
#:                    the path's seed)
ROUTING_RULES = ("fixed_order", "combine_first", "funded_first", "most_room", "closest_to_goal", "random")
ROUTING_RANDOM_SEED = 20261500

#: Kind codes for child seeds, shared with `lockstep.binary_draw_factories`.
_KIND_COMBINE = 1
_KIND_FUNDED = 2
_KIND_FLIP = 3                                         # D-339: a funded account's flip draw


class SharedDayTable:
    """One path's calendar: calendar day -> historical day index, drawn once, shared by all."""

    def __init__(self, n_history: int, *, seed: int, initial_days: int = 1024):
        if n_history <= 0:
            raise ValueError("a shared day table needs at least one historical day")
        self.n_history = int(n_history)
        self.seed = int(seed)
        self._rng = np.random.default_rng(self.seed)
        self._assign = np.empty(0, dtype=np.int64)
        self._extend(initial_days)

    def _extend(self, upto_day: int) -> None:
        have = self._assign.shape[0]
        if upto_day < have:
            return
        extra = self._rng.integers(0, self.n_history, size=upto_day - have + 1)
        self._assign = extra if have == 0 else np.concatenate([self._assign, extra])

    def historical_day(self, calendar_day: int) -> int:
        if calendar_day < 0:
            raise ValueError(f"calendar day must be non-negative, got {calendar_day}")
        self._extend(calendar_day)
        return int(self._assign[calendar_day])


class StationaryDayTable(SharedDayTable):
    """One path's calendar under the stationary bootstrap of days (Politis and Romano, 1994; D-663): calendar day 0
    starts a block at a uniformly drawn historical day; at every later calendar day, with probability 1 / `mean_block`
    a new block starts at a uniformly drawn historical day, and otherwise the calendar takes the historical day after
    the one before it, the last historical day followed by the first (the circular wrap). Blocks then have geometric
    lengths with mean `mean_block` sessions, every historical day is equally likely on every calendar day, and
    consecutive calendar days keep history's own order inside a block -- what `SharedDayTable`'s independent draw
    (each calendar day its own uniform draw) removes. `mean_block` 1 restarts every day: the independent draw's law, on
    this table's own random stream (not `SharedDayTable`'s numbers). `mean_block` infinity never restarts: history in
    its own order from one uniform start.

    Each calendar day consumes exactly two uniforms from the table's generator -- the restart and the start -- whether or
    not the day restarts, so a calendar does not depend on how far ahead it was extended."""

    def __init__(self, n_history: int, *, seed: int, mean_block: float, initial_days: int = 1024):
        mb = float(mean_block)
        if not mb >= 1.0:                                  # NaN refused too
            raise ValueError(f"the mean block is at least one session, got {mean_block!r}")
        self.mean_block = mb
        self._p_restart = 0.0 if np.isinf(mb) else 1.0 / mb
        super().__init__(n_history, seed=seed, initial_days=initial_days)

    def _extend(self, upto_day: int) -> None:
        have = self._assign.shape[0]
        if upto_day < have:
            return
        k = upto_day - have + 1
        u = self._rng.random((k, 2))
        restart = u[:, 0] < self._p_restart
        start = np.minimum((u[:, 1] * self.n_history).astype(np.int64), self.n_history - 1)
        if have == 0:
            restart[0] = True                              # the calendar's first day starts the first block
        extra = np.empty(k, dtype=np.int64)
        prev = int(self._assign[-1]) if have else 0
        for i in range(k):
            prev = int(start[i]) if restart[i] else (prev + 1) % self.n_history
            extra[i] = prev
        self._assign = extra if have == 0 else np.concatenate([self._assign, extra])


class ReplayTable:
    """The as-happened calendar: the log's days in their own order, once (D-130).

    Campaign day 0 is the purchase day before the log's first session, so calendar day `t`
    is the log's day `t - 1`, and days past the end of the log carry no trades (-1): the
    accounts sit idle while fees still bill, which is what a finished log honestly implies.
    One replay is one path; the resampled tables give the distribution.
    """

    def __init__(self, n_history: int):
        if n_history <= 0:
            raise ValueError("a replay needs at least one historical day")
        self.n_history = int(n_history)
        self.seed = None

    def historical_day(self, calendar_day: int) -> int:
        if calendar_day < 0:
            raise ValueError(f"calendar day must be non-negative, got {calendar_day}")
        h = int(calendar_day) - 1
        return h if 0 <= h < self.n_history else -1


class TradeRouter:
    """Hands each of a day's trades to the account that has waited longest since its last trade (`rotation` mode).

    The lockstep loop calls `begin_day(day, keys)` before any account trades, with the live accounts in rotation order
    (earliest start first; funded before Combine on a tie; then index). **Since D-216 the turn is the account's own,
    not a position in that list**: each routed trade stamps its account, and the next trade goes to the eligible
    account with the oldest stamp. An account first seen today is stamped as of today -- it has waited since it was
    bought -- so accounts that last traded before it go first; equal stamps (accounts that have never traded and
    joined together) follow the list's order. "Take one trade, then switch accounts", by account, however accounts come
    and go. (Before D-216 trade `j` went to `keys[(k + j) % len(keys)]`, k the trades routed so far: a position in a
    list re-sorted whenever an account was replaced, so one account could trade on consecutive days while another
    waited -- found by the operator in the Studio's replay of IM2, 2026-10-01.) An account's `slot` in the engine is
    the position of its trade in its own list for the day.

    **Flat accounts only (D-159), when the log carries times.** With each trade's entry and exit time
    (`times_by_history_day`, from `DayBlock.entry_t` / `exit_t`), a trade goes to the longest-waiting account that is
    flat at its entry -- whose last trade that day exited before it -- and is skipped, and counted in `skipped`, when
    none is. No account then holds two positions at once, so the engine's settlement of an account's trades one after
    another is exact, and a per-trade size cap is the account's cap.
    """

    def __init__(self, table: Any, trades_by_history_day: Sequence[int],
                 times_by_history_day: Sequence[tuple[np.ndarray, np.ndarray]] | None = None, *, able: bool = False,
                 sides_by_history_day: Sequence[np.ndarray | None] | None = None,
                 exits_by_rr_by_history_day: Sequence[dict[float, np.ndarray] | None] | None = None,
                 outcomes_by_rr_by_history_day: Sequence[dict[float, np.ndarray] | None] | None = None,
                 one_at_a_time: float | None = None, rule: str | None = None, rule_seed: int | None = None):
        self.table = table
        self.n_trades = [int(n) for n in trades_by_history_day]
        # D-568: an opt-in routing rule (ROUTING_RULES); None routes in the longest-waiting order, as every recorded run
        if rule is not None and rule not in ROUTING_RULES:
            raise ValueError(f"routing rule must be one of {ROUTING_RULES} or None, got {rule!r}")
        self.rule = rule
        self.wants_progress = rule == "closest_to_goal"   # the lockstep loop writes `progress` before each day's hook
        self.progress: dict[AccountKey, float] = {}
        self._rule_rng = (np.random.default_rng([ROUTING_RANDOM_SEED, int(rule_seed or 0)])
                          if rule == "random" else None)
        self._fixed_next = 0                               # D-568 R1: the position in the day's list to offer first
        self.times = list(times_by_history_day) if times_by_history_day is not None else None
        # D-339: each day's trade sides (+1 / -1), for the cross-account rule; None where the log carries none
        self.sides = list(sides_by_history_day) if sides_by_history_day is not None else None
        # D-349: each day's trades' exit times at every R of the menu, so a routed position is held -- for the rule and
        # for flat-account routing -- to its exit at the R its account trades (`begin_day(..., rrs=)`); None routes by
        # the log's single exit, as before (run fv3_gf_v1 held a 3R position only to the log's 1.5R exit)
        self.exits_by_rr = list(exits_by_rr_by_history_day) if exits_by_rr_by_history_day is not None else None
        # D-368: each day's trades' net outcomes at every R, so a second signal goes to an account only after its first
        # trade left the day short of the winning-day minimum (the trader knows the first result before the second)
        self.outcomes_by_rr = (list(outcomes_by_rr_by_history_day) if outcomes_by_rr_by_history_day is not None
                               else None)
        self.seconds_routed = 0                            # D-368: second signals handed out
        self.able = bool(able)
        self.counter = 0
        self.skipped = 0
        self.routed = 0
        self.passed_over = 0                               # D-318: accounts passed over because they could not take it
        self.skipped_opposite = 0                          # D-339: signals refused -- another account held the opposite side
        # D-429: the operator's strict rule (R2, D-409) -- a trade is refused while any account holds a position or
        # within this many minutes of one closing (D-160's flat gap); None: off, every recorded run routes as before
        self.one_at_a_time = None if one_at_a_time is None else float(one_at_a_time)
        if self.one_at_a_time is not None and self.one_at_a_time < 0.0:
            raise ValueError("the one-at-a-time gap is a non-negative number of minutes (D-429)")
        self.skipped_busy = 0                              # D-429: trades refused under the strict rule
        self.flip_sides: dict[AccountKey, int] = {}        # D-339: the side each flip took today (+1 / -1)
        self._day: int | None = None
        self._assigned: dict[AccountKey, list[int]] = {}
        self._tick = 0                                     # D-216: stamps of each account's last routed trade
        self._last: dict[AccountKey, int] = {}
        # D-319 (the v6 audit): held weakly, so a finished path's accounts are freed while the gate keeps its routers
        import weakref

        self._draws: Any = weakref.WeakValueDictionary()

    def register(self, key: AccountKey, draw: Any) -> None:
        """D-318: an account's draw, so `able` routing can ask it which trades it can take."""
        self._draws[tuple(key)] = draw

    def begin_day(self, day: int, keys: Sequence[AccountKey],
                  caps: Mapping[AccountKey, int] | None = None,
                  states: Mapping[AccountKey, tuple[float, float]] | None = None,
                  flips: Sequence[tuple[AccountKey, float, float, int]] | None = None,
                  rrs: Mapping[AccountKey, float | None] | None = None,
                  seconds: Mapping[AccountKey, tuple[float, float, float]] | None = None,
                  collect: Mapping[AccountKey, float] | None = None) -> None:
        """Route the day's trades. `caps` (D-162), when the engine passes it, is each account's trade limit for the
        session from its state; an account at its limit is passed over like a busy one, and a trade no account can
        take is skipped and counted. `states` (D-205) are the accounts' balances and floors at the session's start;
        with `able` (D-318) a trade goes to the longest-waiting account that can take it -- its draw's `can_take`:
        the state's R permitted by the trade's room, a micro under the allowance and the room -- so a trade is not
        handed to an account that must let it pass while another could have taken it. Without `able` the states are
        not read and routing is as before.

        D-339, with the log's times: the day's events -- the log's trades at their entries and the flips at their
        slots (`flips`: (account, start, end, the day's direction)) -- are walked in time order. A trade whose side is
        opposite to a position open on any account at its entry is refused and counted (`skipped_opposite`: the firm
        prohibits opposite positions held at the same time across a trader's accounts, D-336 (iv)); a flip takes the
        side of any position open at its slot, else the day's direction, and holds it to its window's end
        (`flip_sides`). Without times neither applies: nothing is known about overlaps.

        D-349: `rrs` is each account's R for the session (the table's decision, else the leg's); with the day's
        per-R exits (`exits_by_rr_by_history_day`) a routed position is held to its exit at that R -- the log's single
        exit otherwise.

        D-368: `seconds` names the accounts allowed a second trade today, each with (its first trade's dollar risk, its
        R, the winning-day minimum): such an account is handed a second signal -- only one no account ahead of it in the
        rotation takes, entering after its first has closed -- when its first routed trade leaves the day short of the
        minimum and it would take the signal for the shortfall (`second_ok`), and holds it to the latest exit the trade
        carries at any R (its take-profit is set by the shortfall, which the draw settles; the latest exit is never
        earlier, so no overlap the rule forbids can be missed).

        D-368: `collect` names the accounts in the collect phase today, each with the winning-day minimum: under `able`
        such an account is asked whether it would bracket the signal at the minimum (`can_stretch`, which reads no
        outcome) in place of `can_take`, and holds the position to the latest exit the trade carries at any R."""
        h = self.table.historical_day(int(day))
        m = self.n_trades[h] if h >= 0 else 0
        self._day = int(day)
        self._assigned = {tuple(k): [] for k in keys}
        self.flip_sides = {}
        for k in self._assigned:
            self._last.setdefault(k, self._tick)           # first seen today: waiting since today
        if not keys or (not m and not flips):
            return
        pos = {k: i for i, k in enumerate(self._assigned)}
        cap = {k: (np.inf if caps is None or caps.get(k) is None else int(caps[k])) for k in pos}
        entry, exit_ = self.times[h] if (self.times is not None and h >= 0) else (None, None)
        sides = (self.sides[h] if (self.sides is not None and h >= 0 and self.sides[h] is not None) else None)
        exits_rr = (self.exits_by_rr[h] if (self.exits_by_rr is not None and h >= 0) else None)
        rr_of = {tuple(k): v for k, v in rrs.items()} if rrs else {}
        sec = {tuple(k): v for k, v in seconds.items()} if seconds else {}
        coll = {tuple(k): float(v) for k, v in collect.items()} if collect else {}
        outs_rr = (self.outcomes_by_rr[h] if (self.outcomes_by_rr is not None and h >= 0) else None)
        if sec and (outs_rr is None or exits_rr is None):
            raise ValueError("a second trade needs each trade's outcome and exit at every R (D-368)")
        if coll and exits_rr is None and m:
            raise ValueError("the collect phase needs each trade's exit at every R (D-368)")

        def second_ok(k: AccountKey, j: int) -> bool:
            """D-368: the account's first routed trade has left the day short of the minimum, and the account would take
            trade `j` for the shortfall. With the account's draw registered and the states given, its own sizing reads
            the first trade's net dollars at the contracts it holds (`trade_dollars`) and whether it would take the
            second (`can_stretch`, which reads no outcome); otherwise the first's outcome at its R times its risk."""
            risk, R, wmin = sec[k]
            j1 = self._assigned[k][0]
            drw = self._draws.get(k) if states is not None and k in states else None
            if drw is not None and hasattr(drw, "trade_dollars"):
                b, f = states[k]
                first = drw.trade_dollars(h, j1, b, f)
                if first is None or not first < float(wmin) - 1e-9:
                    return False
                return bool(drw.can_stretch(h, j, b, f, float(wmin) - first, first))
            arr = outs_rr.get(float(R)) if outs_rr is not None else None
            if arr is None or j1 >= len(arr) or not np.isfinite(arr[j1]):
                return False
            return float(arr[j1]) * float(risk) < float(wmin) - 1e-9

        def latest_exit(j: int) -> float:
            """D-368: the latest exit trade `j` carries at any R."""
            ex = [float(a[j]) for a in exits_rr.values() if a is not None and j < len(a) and np.isfinite(a[j])]
            return max(ex) if ex else float(exit_[j])

        def exit_for(k: AccountKey, j: int) -> float:
            """D-349: the trade's exit at the account's R when the day carries it, else the log's exit."""
            R = rr_of.get(k)
            if exits_rr and R is not None:
                arr = exits_rr.get(float(R))
                if arr is not None and j < len(arr) and np.isfinite(arr[j]):
                    return float(arr[j])
            return float(exit_[j])

        open_until = {k: -np.inf for k in pos}
        open_side = {k: 0 for k in pos}
        check = self.able and states is not None
        events: list[tuple[float, int, Any]] = [(float(entry[j]) if entry is not None else float(j), 0, j) for j in range(m)]
        if flips and entry is not None:                    # D-339: flips need the log's clock to sit among the trades
            for key, start, end, direction in flips:
                events.append((float(start), 1, (tuple(key), float(end), int(direction))))
        events.sort(key=lambda e: (e[0], e[1]))
        order = None                                       # R11: the waiting order, sorted again only after a routed trade
        for t, kind, payload in events:
            if kind == 1:                                  # a flip at its slot
                key, end, direction = payload
                held = [open_side[k] for k in pos if open_until[k] > t and open_side[k] != 0]
                side = held[0] if held else (1 if int(direction) >= 0 else -1)
                self.flip_sides[key] = side
                if key in pos:
                    open_until[key], open_side[key] = end, side
                continue
            j = payload
            side_j = int(sides[j]) if sides is not None and len(sides) > j else 0
            if side_j != 0 and any(open_until[k] > t and open_side[k] == -side_j for k in pos):
                self.skipped_opposite += 1                 # D-339: the firm's rule, not a capacity limit
                continue
            if (self.one_at_a_time is not None and entry is not None
                    and any(open_until[k] + self.one_at_a_time > t for k in pos)):
                self.skipped_busy += 1                     # D-429: the strict rule -- one position across all accounts
                continue
            if order is None:                              # (the stamps it sorts on change only when a trade is routed)
                order = sorted(pos, key=lambda x: (self._last[x], pos[x]))
                if self.rule is not None:                  # D-568: the rule reorders; longest-waiting breaks ties
                    order = self._rule_order(order, list(pos), states)
            for k in order:
                if len(self._assigned[k]) >= cap[k]:
                    continue
                second = bool(sec) and k in sec and len(self._assigned[k]) >= 1
                if entry is not None and not open_until[k] < entry[j]:
                    continue
                if second and not second_ok(k, j):
                    continue                               # D-368: the first made the day, or no bracket for the need
                drw = self._draws.get(k) if check and k in states and not second else None
                if drw is not None:
                    if k in coll and hasattr(drw, "can_stretch"):      # D-368: bracketed at the need
                        ok = drw.can_stretch(h, j, *states[k], coll[k])
                    else:
                        ok = drw.can_take(h, j, *states[k])
                    if not ok:
                        self.passed_over += 1
                        continue
                self._assigned[k].append(j)
                if second:
                    self.seconds_routed += 1
                if entry is not None:
                    # D-349: held to the exit at the account's R; D-368: a second trade, or one bracketed at the need in
                    # the collect phase, to its latest exit
                    open_until[k], open_side[k] = ((latest_exit(j) if (second or k in coll) else exit_for(k, j)),
                                                   side_j)
                self._tick += 1
                self._last[k] = self._tick
                if self.rule == "fixed_order":             # D-568 R1: the cycle continues after this account
                    self._fixed_next = pos[k] + 1
                order = None
                self.counter += 1
                self.routed += 1
                break
            else:
                self.skipped += 1
            if self.rule == "random":
                order = None                               # D-568 R6: a fresh permutation for every trade

    def _rule_order(self, base: list[AccountKey], day_list: list[AccountKey],
                    states: Mapping[AccountKey, tuple[float, float]] | None) -> list[AccountKey]:
        """D-568: the longest-waiting order `base` reordered by the routing rule -- a stable sort, so `base` breaks ties;
        `fixed_order` the day's list `day_list` cycled from the position after the last routed account; `random` a fair
        permutation of `base`."""
        rule = self.rule
        if rule == "random":
            return [base[i] for i in self._rule_rng.permutation(len(base))]
        if rule == "fixed_order":
            n = len(day_list)
            start = int(self._fixed_next) % n if n else 0
            return [day_list[(start + i) % n] for i in range(n)]
        if rule == "combine_first":
            return sorted(base, key=lambda k: 0 if k[0] == "combine" else 1)
        if rule == "funded_first":
            return sorted(base, key=lambda k: 0 if k[0] == "funded" else 1)
        if rule == "most_room":
            if states is None:
                raise ValueError("the most_room rule needs the accounts' balances and floors (the day hook's states)")
            return sorted(base, key=lambda k: -(float(states[k][0]) - float(states[k][1])) if k in states else np.inf)
        if rule == "closest_to_goal":
            return sorted(base, key=lambda k: -float(self.progress.get(k, 0.0)))
        raise ValueError(f"unknown routing rule {rule!r}")

    def trade_index(self, key: AccountKey, day: int, slot: int) -> int | None:
        if self._day != int(day):
            raise RuntimeError(
                f"TradeRouter.begin_day was not called for calendar day {day} (last: {self._day}); "
                "the lockstep loop must pass the router's begin_day as its day_hook"
            )
        lst = self._assigned.get(tuple(key))
        if lst is None or slot >= len(lst):
            return None
        return lst[slot]

    def assignments(self, day: int) -> dict[AccountKey, list[int]]:
        if self._day != int(day):
            raise RuntimeError(f"no assignments for day {day}")
        return {k: list(v) for k, v in self._assigned.items()}


def flat_routing_available(blocks: Sequence[DayBlock]) -> bool:
    """D-159: whether every day with a trade carries each trade's entry and exit time (an empty day needs none), so
    rotation can route a trade only to an account that is flat. A log that times some trade days and not others is
    refused rather than silently routed without."""
    has_times = [b.entry_t is not None and b.exit_t is not None for b in blocks if len(b)]
    if any(has_times) and not all(has_times):
        raise ValueError("some trade days carry entry and exit times and some do not; D-159's flat-account "
                         "routing needs the times on every day with a trade, or on none")
    return bool(has_times) and all(has_times)


def market_count(blocks: Sequence[DayBlock], markets: int | Sequence[str] | None = None) -> int | None:
    """How many markets a log trades: the declared `markets` (a count, or the markets' names) when given, which
    overrides the blocks' labels (say, a log that writes contract months as symbols); otherwise the number of distinct
    `DayBlock.markets` labels; None when neither says (treated as one market, as before)."""
    if markets is not None:
        n = int(markets) if isinstance(markets, (int, np.integer)) else len(set(markets))
        if n < 1:
            raise ValueError(f"markets must name at least one market, got {markets!r}")
        return n
    seen = {m for b in blocks if b.markets is not None for m in b.markets}
    return len(seen) if seen else None


def check_layout(mode: str, blocks: Sequence[DayBlock], *, flat_routing: bool,
                 markets: int | Sequence[str] | None = None) -> int | None:
    """Refuse an account layout that would stack one log's markets in one account (audit 2026-09-27, finding 5).

    A multi-market log's trades overlap in time: several markets are open at once. The engine settles an account's
    trades one after another, so an account handed two of them at once is modelled as if it held one position at a
    time. `rotation` avoids that only by flat routing (D-159), which needs each trade's entry and exit time;
    `independent` hands every account whole days of every market's trades. Returns the market count."""
    n = market_count(blocks, markets)
    if n is None or n <= 1:
        return n
    if mode == ROTATION and not flat_routing:
        raise ValueError(
            f"rotation on a log with {n} markets needs flat-account routing (D-159), and the day blocks carry no entry "
            "and exit times: one account could hold several markets' positions at once while the engine settled them "
            "one after another. Give every trade day entry_t and exit_t, or run one market per log "
            "(audit 2026-09-27, finding 5)."
        )
    if mode == INDEPENDENT:
        raise ValueError(
            f"the independent layout on a log with {n} markets is refused: each account would replay whole days of "
            "every market's trades, holding positions the engine settles one after another. Use rotation with entry "
            "and exit times (D-159), or one group per market under partitioned (audit 2026-09-27, finding 5)."
        )
    return n


def scaled_pnl(block: DayBlock, risk: float) -> np.ndarray:
    """The block's trades rescaled to `risk` dollars per trade, as `EmpiricalDraw` does it."""
    with np.errstate(divide="ignore", invalid="ignore"):
        factor = np.where(block.risked > 0, float(risk) / block.risked, np.nan)
    return block.pnl * factor


def scaled_mae(block: DayBlock, risk: float) -> np.ndarray | None:
    """The block's MAE rescaled by the same factor as its P&L (D-156); None when the block has none."""
    if block.mae is None:
        return None
    with np.errstate(divide="ignore", invalid="ignore"):
        factor = np.where(block.risked > 0, float(risk) / block.risked, np.nan)
    return block.mae * factor


class SharedDayDraw:
    """An account's draw over a shared table: `draw(1, rel_day, slot, cushion)`.

    The account's calendar day is `start_day + 1 + rel_day` (engine day 0 is the day after
    purchase or activation, the convention of `lockstep.py`); the table names the historical
    day; the group's pre-scaled block supplies the slot's P&L, NaN past the day's trade count.
    Each trade is settled against the room the engine hands it as `cushion` (D-156): every
    trade risks the leg's dollar risk, and its MAE, where the log has one, is scaled with it.
    """

    def __init__(
        self, table: Any, pnl_by_day: Sequence[np.ndarray], start_day: int,
        *, router: TradeRouter | None = None, key: AccountKey | None = None,
        mae_by_day: Sequence[np.ndarray | None] | None = None, settlement: str = "pessimistic",
    ):
        from propedge.outcomes.settlement import TRADE_LOG_SETTLEMENTS

        if settlement not in TRADE_LOG_SETTLEMENTS:
            raise ValueError(f"a trade-log draw settles by one of {TRADE_LOG_SETTLEMENTS}, got {settlement!r}")
        self.table = table
        self._pnl = pnl_by_day
        self._mae = mae_by_day
        self.settlement = settlement
        self.start_day = int(start_day)
        self.router = router
        self.key = key
        self.last_trade: dict[str, Any] | None = None   # what the last call handed out
        self.base_risk: float | None = None   # the leg risk the day blocks were scaled to
        self._scale = 1.0

    def set_risk(self, risk: float, rr: float | None = None) -> None:
        """D-147: trade at `risk` dollars instead of the leg risk the blocks were scaled to.
        R is the log's (fixed by each trade's stop and target), so a policy setting R is refused."""
        if rr is not None:
            raise ValueError(
                "this draw replays trades whose R was fixed by their stop and target; a risk "
                "policy may change the dollar risk but not R"
            )
        if self.base_risk is None or not self.base_risk > 0:
            raise ValueError("this draw does not know the risk its trades were scaled to")
        self._scale = float(risk) / self.base_risk

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray) -> np.ndarray:
        if n != 1:
            raise ValueError(f"SharedDayDraw serves one account at a time, got n={n}")
        self.last_trade = None
        t = self.start_day + 1 + int(day)
        h = self.table.historical_day(t)
        if h < 0:
            return np.array([np.nan])
        pnl = self._pnl[h]
        j = slot if self.router is None else self.router.trade_index(self.key, t, slot)
        if j is None or j >= len(pnl):
            return np.array([np.nan])
        from propedge.outcomes.settlement import settle

        risk = float(self.base_risk) * self._scale if self.base_risk else float("nan")
        mae_day = self._mae[h] if self._mae is not None else None
        mae = float(mae_day[j]) * self._scale if mae_day is not None else float("nan")
        settled = settle(np.array([float(pnl[j]) * self._scale]), risk, np.array([mae]),
                         np.asarray(cushion, dtype=float), self.settlement)
        self.last_trade = {"historical_day": h, "trade_index": int(j), "risk": risk, "mae": mae,
                           "settlement": self.settlement}
        return settled


class SharedDayDraws:
    """Draw factories for the lockstep loop under one of the three modes.

    Args:
        blocks_by_group: per-group day blocks. In `partitioned` mode the lists must be the
            same length and aligned by date; in `copier` mode there is exactly one group.
        protocol: supplies the two legs' dollar risk, which each block is scaled to.
        seed: explicit. The table and every per-account draw derive from it.
        mode: `copier`, `partitioned`, `independent` or `rotation` (each trade to the next
            live account in turn; one strategy in one group).
        group_of: `(kind, index) -> group`, where kind is "combine" or "funded" and index is
            the account's number in activation order. Required for `partitioned`; ignored by
            `copier` and `rotation` (one group); optional for `independent` (default: group 0).
        sizing: a `propedge.campaign.sizing.SizingRule`, or None. With a rule, every account's
            draw sizes each trade in contracts from the account's tier at the start of the
            session (D-32, D-53, D-117) and the blocks must carry `risk_per_contract`; the
            rule's `fixed_risk` mode is bit-identical to no rule at all. Without one, trades
            are scaled to the leg's dollar risk as before.
        replay: True plays the log's days in their own order, once (`ReplayTable`): the
            as-happened replay, one path. False (the default) resamples days. Replay is not
            defined for `independent` mode.
        settlement: how a trade that risks more than the room settles (D-156,
            `propedge.outcomes.settlement`): `mae` (exact; needs each trade's MAE), `pessimistic`
            (every such trade touched the barrier: the lower bound) or `legacy` (the pre-D-156
            upper bound, only to reproduce an old result). None: `mae` when every block carries
            MAE, else `pessimistic`.
        markets: how many markets the log trades (a count or the names), overriding the blocks'
            own `DayBlock.markets` labels; None reads the labels. A multi-market log is refused
            under `rotation` without entry and exit times and under `independent`
            (`check_layout`; audit 2026-09-27, finding 5).

    The protocol's `trades_per_day` must be at least the busiest day's trade count, or the
    engine would drop trades silently; this is checked at construction.
    """

    def __init__(
        self,
        blocks_by_group: Mapping[int, Sequence[DayBlock]],
        *,
        protocol: Protocol,
        seed: int,
        mode: str = COPIER,
        group_of: Callable[[str, int], int] | None = None,
        sizing: SizingRule | None = None,
        replay: bool = False,
        settlement: str | None = None,
        markets: int | Sequence[str] | None = None,
        route_able: bool = False,
        flip: Any = None,
        cross_account: bool = False,
        hold_to_own_exit: bool = False,
        one_at_a_time: float | None = None,
        routing_rule: str | None = None,
        mean_block: float | None = None,
    ):
        """`route_able` (D-318): rotation hands each trade to the longest-waiting account that can take it
        (`TradeRouter(able=True)`); False routes as before. `cross_account` (D-339; the firm's rule, D-336 (iv)): the
        router reads each trade's side and refuses a signal opposite to a position open on any account; it needs the
        log's entry and exit times. Off by default, so every recorded run reproduces. `flip` (D-339): the flip stream's
        `FlipSpec`; with it the lockstep kwargs carry a flip draw factory (one seeded `FlipDraw` per funded account) and
        the spec; a flip's side follows the positions open on the other accounts, so it needs the rule on.
        `hold_to_own_exit` (D-351; the v2 audit's finding 5): flat-account routing holds a routed position to its exit
        at the R its account trades (the blocks' `exit_by_rr`, the day hook's `rrs`) even without the cross-account
        rule, which implies it; off by default, so every run recorded before D-351 reproduces (those held a position
        only to the log's single exit, the fresh Combine's, so an account at 3R could be handed a later trade).
        `one_at_a_time` (D-429; the operator's R2, D-409): rotation refuses a trade while any account holds a position
        or within that many minutes of one closing, each position held to its exit at its account's R (it implies the
        holding); it needs the log's entry and exit times. None: off, so every recorded run reproduces.
        `routing_rule` (D-568): one of `ROUTING_RULES`, the order in which rotation offers a trade to the accounts
        (`random` seeded by this path's seed); None: the longest-waiting order, so every recorded run reproduces.
        `mean_block` (D-663): the path's calendar from the stationary bootstrap of days at that mean block length in
        sessions (`StationaryDayTable`, seeded as the shared table is) in place of one independent draw a day; rotation
        only, never with `replay` (a replay draws nothing) -- every other layout is refused, not having been verified
        under it. None (the default): `SharedDayTable`, so every recorded run and every pickled state is unchanged."""
        from propedge.outcomes.settlement import TRADE_LOG_SETTLEMENTS, default_trade_log_settlement

        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
        if routing_rule is not None and mode != ROTATION:
            raise ValueError(f"a routing rule (D-568) orders rotation's offers; mode {mode!r} has no router")
        if flip is not None and not cross_account:
            raise ValueError("a flip stream needs the cross-account rule on (D-339): a flip's side follows the positions "
                             "open on the other accounts")
        if not blocks_by_group:
            raise ValueError("blocks_by_group is empty")
        lengths = {g: len(b) for g, b in blocks_by_group.items()}
        if any(n == 0 for n in lengths.values()):
            raise ValueError(f"every group needs at least one day block; got {lengths}")
        if mode in (COPIER, ROTATION) and len(blocks_by_group) != 1:
            raise ValueError(
                f"{mode} mode is one strategy in one group; got groups {sorted(blocks_by_group)}"
            )
        if replay and mode == INDEPENDENT:
            raise ValueError("an as-happened replay has one calendar; independent mode has none")
        if mean_block is not None:                         # D-663: verified under rotation's one shared calendar only
            if replay:
                raise ValueError("a mean block resamples days; an as-happened replay draws none (D-663)")
            if mode != ROTATION:
                raise ValueError(f"block-resampled days are verified under rotation only (D-663); mode {mode!r} is "
                                 "refused")
            if not float(mean_block) >= 1.0:
                raise ValueError(f"the mean block is at least one session, got {mean_block!r}")
        busiest = max(len(b) for blocks in blocks_by_group.values() for b in blocks)
        if int(protocol.trades_per_day) < busiest:
            raise ValueError(
                f"the protocol's trades_per_day ({protocol.trades_per_day}) is below the log's "
                f"busiest day ({busiest} trades); the engine would drop trades. Set "
                "trades_per_day to at least the busiest day"
            )
        if mode == PARTITIONED:
            if len(set(lengths.values())) != 1:
                raise ValueError(
                    "partitioned mode needs the groups' day blocks aligned by date, so every "
                    f"group must have the same number of days; got {lengths}"
                )
            if group_of is None:
                raise ValueError("partitioned mode needs group_of(kind, index) -> group")

        self.mode = mode
        self.replay = bool(replay)
        self.seed = int(seed)
        self.protocol = protocol
        self.sizing = sizing
        self.blocks_by_group = {int(g): list(b) for g, b in blocks_by_group.items()}
        every_block = [b for blocks in self.blocks_by_group.values() for b in blocks]
        self.settlement = settlement or default_trade_log_settlement(every_block)
        if self.settlement not in TRADE_LOG_SETTLEMENTS:
            raise ValueError(f"settlement must be one of {TRADE_LOG_SETTLEMENTS}, got {self.settlement!r}")
        self.n_history = min(lengths.values())
        only_group = next(iter(self.blocks_by_group))
        if mode in (COPIER, ROTATION):
            self.group_of: Callable[[str, int], int] = lambda kind, index: only_group
        elif group_of is None:
            self.group_of = lambda kind, index: only_group
        else:
            self.group_of = group_of

        self.mean_block = None if mean_block is None else float(mean_block)             # D-663
        self.table: Any = (
            ReplayTable(self.n_history) if self.replay
            else SharedDayTable(self.n_history, seed=child_seed(self.seed, 0, 0)) if self.mean_block is None
            else StationaryDayTable(self.n_history, seed=child_seed(self.seed, 0, 0), mean_block=self.mean_block)
        )
        # D-159: flat-account routing when every day with trades carries entry and exit times (an empty day needs
        # none); a log that times some trade days and not others is refused rather than silently routed without.
        route_blocks = self.blocks_by_group[only_group]
        self.flat_routing = flat_routing_available(route_blocks)
        # Audit 2026-09-27, finding 5: a multi-market log is never stacked in one account without flat routing.
        self.markets: int | None = None
        if mode == ROTATION:
            self.markets = check_layout(mode, route_blocks, flat_routing=self.flat_routing, markets=markets)
        elif mode == INDEPENDENT:
            for blocks in self.blocks_by_group.values():
                n = check_layout(mode, blocks, flat_routing=False,
                                 markets=markets if len(self.blocks_by_group) == 1 else None)
                self.markets = n if self.markets is None else max(self.markets, n or 1)
        self.flip = flip                                   # D-339
        self.cross_account = bool(cross_account)           # D-339
        self.one_at_a_time = None if one_at_a_time is None else float(one_at_a_time)    # D-429
        self.hold_to_own_exit = (bool(hold_to_own_exit) or self.cross_account     # D-351: the rule implies the holding
                                 or self.one_at_a_time is not None)                # D-429: and so does the strict rule
        if self.one_at_a_time is not None and mode != ROTATION:
            raise ValueError("the one-at-a-time rule routes trades to accounts: rotation only (D-429)")
        if self.hold_to_own_exit and mode == ROTATION and not self.flat_routing:
            raise ValueError("holding a position to its own exit needs the log's entry and exit times on every trade "
                             "day (D-351): without them nothing is known about which positions are open")
        if self.cross_account and mode == ROTATION and not self.flat_routing:
            raise ValueError("the cross-account rule needs the log's entry and exit times on every trade day (D-339): "
                             "without them nothing is known about which positions overlap")
        if self.cross_account and mode == ROTATION and any(len(b) and b.sides is None for b in route_blocks):
            # D-348: run fv3_gf_v1 declared the rule on blocks without sides and refused nothing -- a silent no-op
            raise ValueError("the cross-account rule needs each trade's side on every trade day (D-339, D-348): a day "
                             "with trades carries none, so no opposite position could ever be found")
        if self.hold_to_own_exit and mode == ROTATION and any(len(b) and b.exit_by_rr is None for b in route_blocks):
            # D-349: the same run held every position only to the log's 1.5R exit, where no two trades overlap; D-351:
            # the holding on its own needs the same per-R exits
            raise ValueError("holding a position to its own exit (and the cross-account rule, which implies it) needs each "
                             "trade's exit time at every R on every trade day (D-349, D-351): a day with trades carries "
                             "only the log's single exit, so a position held to a wider target would be closed too early")
        # D-368: an XFA's second trade after a first short of the winning-day minimum -- the router reads each trade's
        # outcome at every R to know it, and holds the second to its latest exit, so it needs the per-R exits
        self.xfa_second = bool((getattr(protocol, "params", None) or {}).get("xfa_second_trade", False))
        if self.xfa_second and (mode != ROTATION or not self.hold_to_own_exit
                                or any(len(b) and (b.r_by_rr is None or b.exit_by_rr is None) for b in route_blocks)):
            raise ValueError("xfa_second_trade needs rotation with each trade's outcome and exit at every R and the "
                             "holding to its own exit (D-368)")
        # D-368: the collect phase brackets a trade at the shortfall to the winning-day minimum -- its outcome read at every
        # R by the draw -- and the router holds it to its latest exit, so it needs the same
        self.xfa_collect = (getattr(protocol, "params", None) or {}).get("xfa_collect_from") is not None
        if self.xfa_collect and (mode != ROTATION or not self.hold_to_own_exit
                                 or any(len(b) and (b.r_by_rr is None or b.exit_by_rr is None) for b in route_blocks)):
            raise ValueError("xfa_collect_from needs rotation with each trade's outcome and exit at every R and the "
                             "holding to its own exit (D-368)")
        self.router: TradeRouter | None = (
            TradeRouter(self.table, [len(b) for b in route_blocks],
                        [(np.asarray(b.entry_t if b.entry_t is not None else [], float),
                          np.asarray(b.exit_t if b.exit_t is not None else [], float)) for b in route_blocks]
                        if self.flat_routing else None, able=bool(route_able),
                        # D-339: the trades' sides reach the router only under the rule, so routing without it is as before
                        sides_by_history_day=([(np.asarray(b.sides, int) if b.sides is not None else None)
                                               for b in route_blocks] if self.cross_account else None),
                        # D-349 / D-351: the per-R exits reach the router under the rule or the holding switch; runs
                        # recorded before D-351 (neither on) route by the log's single exit, as they did
                        exits_by_rr_by_history_day=([b.exit_by_rr for b in route_blocks] if self.hold_to_own_exit else None),
                        outcomes_by_rr_by_history_day=([b.r_by_rr for b in route_blocks] if self.xfa_second else None),
                        one_at_a_time=self.one_at_a_time,                                             # D-429
                        rule=routing_rule, rule_seed=int(seed))                                       # D-568
            if mode == ROTATION else None
        )
        # D-319: the smallest stop offering each R, read once per group and shared by the group's draws
        self._offered: dict[int, dict] = {int(g): {} for g in self.blocks_by_group}
        # R11: the log's arrays, built once per group and shared by the group's sized draws (`sizing._log_arrays`)
        self._logs: dict[int, dict] = {int(g): {} for g in self.blocks_by_group}
        # Blocks pre-scaled once per (group, leg); accounts share the arrays.
        self._pnl: dict[tuple[int, str], list[np.ndarray]] = {}
        self._mae: dict[tuple[int, str], list[np.ndarray | None]] = {}
        for g, blocks in self.blocks_by_group.items():
            self._pnl[(g, "combine")] = [scaled_pnl(b, protocol.combine_risk) for b in blocks]
            self._pnl[(g, "funded")] = [scaled_pnl(b, protocol.funded_risk) for b in blocks]
            self._mae[(g, "combine")] = [scaled_mae(b, protocol.combine_risk) for b in blocks]
            self._mae[(g, "funded")] = [scaled_mae(b, protocol.funded_risk) for b in blocks]

    def _group(self, kind: str, index: int) -> int:
        g = int(self.group_of(kind, index))
        if g not in self.blocks_by_group:
            raise KeyError(f"group_of({kind!r}, {index}) = {g}, which has no day blocks")
        return g

    def draw_for(self, kind: str, index: int, start_day: int):
        """The draw one account uses; the lockstep factories call this."""
        if kind not in ("combine", "funded"):
            raise ValueError(f"kind must be 'combine' or 'funded', got {kind!r}")
        g = self._group(kind, index)
        risk = self.protocol.combine_risk if kind == "combine" else self.protocol.funded_risk
        code = _KIND_COMBINE if kind == "combine" else _KIND_FUNDED
        if self.sizing is not None:
            # A private day table under `independent` draws the same assignment sequence as
            # `EmpiricalDraw` does for one account from the same child seed, so the two
            # constructions agree exactly (tests/test_sizing.py).
            table = (
                SharedDayTable(self.n_history, seed=child_seed(self.seed, code, index))
                if self.mode == INDEPENDENT else self.table
            )
            return TierSizedDraw(
                table, self.blocks_by_group[g], start_day=start_day, kind=kind,
                rule=self.sizing, target_risk=risk, relative_days=(self.mode == INDEPENDENT),
                router=self.router, key=(kind, int(index)), settlement=self.settlement,
                offered_cache=self._offered[g], log_cache=self._logs[g],
            )
        if self.mode == INDEPENDENT:
            return EmpiricalDraw(
                self.blocks_by_group[g], 1, seed=child_seed(self.seed, code, index),
                scale_to_risk=risk, settlement=self.settlement,
            )
        d = SharedDayDraw(
            self.table, self._pnl[(g, kind)], start_day, router=self.router, key=(kind, int(index)),
            mae_by_day=self._mae[(g, kind)], settlement=self.settlement,
        )
        d.base_risk = float(risk)
        return d

    def factories(self) -> tuple[DrawFactory, DrawFactory]:
        """`(combine_factory, funded_factory)` for `simulate_lockstep_path`."""
        return (
            lambda index, start_day: self.draw_for("combine", index, start_day),
            lambda index, start_day: self.draw_for("funded", index, start_day),
        )

    @property
    def day_hook(self) -> Callable[[int, Sequence[AccountKey]], None] | None:
        """For `simulate_lockstep_path(day_hook=...)`: the router's `begin_day` under
        `rotation`, None otherwise."""
        return self.router.begin_day if self.router is not None else None

    def flip_draw_for(self, index: int, start_day: int):
        """D-339: one funded account's flip draw, seeded from the path seed and the account's index; D-343: under the
        spec's `copy` every account's draw shares one seed, so the flip-state accounts share each day's outcome."""
        from propedge.campaign.flip import FlipDraw

        if self.flip is None:
            raise ValueError("no flip stream was declared for these draws")
        return FlipDraw(self.flip, seed=child_seed(self.seed, _KIND_FLIP, 0 if getattr(self.flip, "copy", False) else int(index)))

    def lockstep_kwargs(self) -> dict[str, Any]:
        """Everything the lockstep loop needs from here: the two factories and the day hook; with a flip stream
        (D-339) the flip draw factory and the spec as well."""
        c, f = self.factories()
        out: dict[str, Any] = {"combine_draw_factory": c, "funded_draw_factory": f, "day_hook": self.day_hook}
        if self.flip is not None:
            out["flip_draw_factory"] = lambda index, start_day: self.flip_draw_for(index, start_day)
            out["flip"] = self.flip
        return out

    def provenance(self) -> dict[str, Any]:
        return {
            **({} if self.mean_block is None else {"mean_block": self.mean_block}),         # D-663: only when set
            "draws": "propedge.campaign.shared_days.SharedDayDraws",
            "mode": self.mode,
            "replay": self.replay,
            "groups": sorted(self.blocks_by_group),
            "n_history_days": self.n_history,
            "seed": self.seed,
            "combine_risk": self.protocol.combine_risk,
            "funded_risk": self.protocol.funded_risk,
            "sizing": self.sizing.as_dict() if self.sizing is not None else "fixed dollar risk per leg",
            "settlement": self.settlement,
            "cross_account_rule": self.cross_account,                                        # D-339
            "flip": self.flip.as_dict() if self.flip is not None else None,                 # D-339
            "one_at_a_time": self.one_at_a_time,                                             # D-429
        }


__all__ = [
    "ROUTING_RULES", "ROUTING_RANDOM_SEED",
    "COPIER",
    "PARTITIONED",
    "INDEPENDENT",
    "ROTATION",
    "MODES",
    "AccountKey",
    "SharedDayTable",
    "StationaryDayTable",
    "ReplayTable",
    "TradeRouter",
    "SharedDayDraw",
    "SharedDayDraws",
    "check_layout",
    "flat_routing_available",
    "market_count",
    "scaled_mae",
    "scaled_pnl",
]
