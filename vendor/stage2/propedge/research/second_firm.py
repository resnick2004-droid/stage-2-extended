"""D-643 (2): the sequencing option of the joint run -- the second firm opens at the first payout's arrival.

Research code: `hypo_hedge.run_joint(..., second_firm_opens="first_payout_arrival")` hands its paths to
`run_sequenced` here; absent (None, every earlier caller) `run_joint` runs exactly as before and nothing in this module
is reached. No engine file is changed (`propedge.reporting.pin.ENGINE_FILES`): the campaign engine
(`lockstep.simulate_lockstep_path`), its draws (`shared_days.SharedDayDraws`) and the firms' turn-taking
(`two_firms._Turns`, `FirmRouter`) are used as they are.

**The rule** (DECISIONS.md's D-643 (2)): "the second firm buys nothing and holds nothing until the first payout of the
campaign has ARRIVED as cash at the first firm; from the next purchase step it runs as declared."

**How it is run**, one path at a time:

1. **The first firm alone** -- `hypo_hedge.run_joint` with one firm on the first firm's setup: the 5 + 0 call of U1 and
   of D-567 / D-593, the first firm's own campaign with no second firm anywhere. Its first payout's ARRIVAL day `a`
   (`CampaignPath.days_to_first_payout`: the day the cash is received, `payout_lag_days` after the request) is the
   opening day. Until the opening the two-firm campaign IS this run -- the second firm has no account, pays no fee and
   takes no trade, so nothing it could do reaches the first firm.
2. **No arrival within the path's days: the second firm never opens.** The path is the first firm's run of step 1 and
   a second firm that did nothing: the engine's own record of a campaign of no days (`simulate_lockstep_path` with a
   horizon of zero), placed after the path's last day.
3. **An arrival on day `a`: the two-firm run with the second firm's campaign started on day `a`.** The first firm
   runs again from day 0; on the days before `a` its accounts are dealt by the ONE-firm deal (`SequencedRouter`:
   `HedgeRouter`'s own deal with one firm), exactly as in step 1. On day `a` the second firm's campaign begins as a
   fresh campaign whose day 0 is the campaign's day `a` -- the engine's path with a horizon of the days left, its
   calendar the first firm's moved by `a` (`_OffsetTable`), its hook the joint deal's (`FirmRouter` on `_OffsetTurns`).
   A fresh campaign buys at the purchase step of its day 0, after that day's session, so in the wallet's order (firm 0
   moves first each day: its payouts arrive, it buys; then firm 1) the second firm's first purchase is the next
   purchase step after the arrival -- the evening of day `a` -- and its accounts trade from day `a` + 1, routed by the
   two-firm deal with every counter as the day-0 run keeps them. From day `a` on the turn-taking, the wallet's order
   and the deal are `run_joint`'s own.
   The first firm's record through day `a` must equal step 1's (its cash, funded accounts, breaches and trades by day;
   its evaluations and funded accounts begun by then; its first payout's arrival day): checked on every opened path,
   raising otherwise -- so "the first firm before the opening is the first firm alone" is an identity of every run.
4. **The records.** The second firm's `LockstepPath` is the engine's own, moved onto the campaign's calendar
   (`on_campaign_calendar`): every calendar-day field plus `a`, the per-day series padded in front, and its cash
   series -- the pool's, as the last firm's is in a joint run -- led by the first firm's cash on the days before the
   opening (the pool then was the first firm's). A record field this module does not know is refused, never passed
   through unmoved. `JointPath.second_firm` records the option, the arrival day and the opening day.

**The pooled wallet** (D-206) is read as in every joint run: one pot, each firm handing its cash over at its day hook;
the second firm reads it first when it opens (the pot as the first firm left it before day `a`'s session) and next
after the first firm's day-`a` evening, the arrival and its purchases included. The engine ends a campaign that cannot
pay one evaluation at its start, where the day-0 firm would simply buy on a later evening: a second firm opening on a
pot below its evaluation fee is REFUSED (never met with the unbound bankroll every study here runs).

**Refused** for the second firm (each carries calendar days this module would have to move, or reads the calendar
day): a conduct model, the Focused Trader Program, a flip stream, D-630's three entry options, the daily recorder, and
a risk policy that branches on the campaign day. Two firms.

**The deal** (D-644 (2)) is any of `hypo_hedge.MODES`, by import: `unhedged`, or one of the two HYPOTHETICAL hedge
deals (`hedged`, `hedged_combines`; prohibited at both firms, tier 1 -- labelled `hypothetical_hedge` by every caller,
never a candidate). "Under the sequencing option there is no pair before Lucid opens; from then the cell's deal
applies": through the opening day the deal is the ONE-firm unhedged deal whatever the cell's (a pair needs the other
firm's account, and it holds none); the first firm's slots are kept from day 0, the second's from its opening, as a
day-0 run keeps them from its day 0.
"""
from __future__ import annotations

import dataclasses
import threading
from typing import Any, Mapping, Sequence

import numpy as np

from propedge.campaign.two_firms import FirmRouter, SignalStream, _Submission, _Turns, _Wallet
from propedge.research import hypo_hedge as hh

DECISION = "D-643"
#: the option's one value: the second firm opens when the campaign's first payout has arrived at the first firm
FIRST_PAYOUT_ARRIVAL = "first_payout_arrival"
OPTIONS = (FIRST_PAYOUT_ARRIVAL,)

#: the engine's record fields this module places on the campaign's calendar -- every field of the four record classes
#: is named here once; a class with another field is refused (`_check_fields`)
_PATH_SERIES = ("cash_series", "active_funded_series", "trades_by_day")
_PATH_DAYS = ("ruin_day", "days_to_first_payout")
_PATH_KEPT = ("final_cash", "initial_bankroll", "ruined", "max_drawdown", "max_drawdown_frac", "attempts_started",
              "accounts_funded", "accounts_ever_paid", "payout_gaps", "total_fees", "total_payouts",
              "peak_queue_length", "passes_forfeited", "combines_abandoned", "passes_on_hold_at_end",
              "same_day_multi_breach_days", "max_breaches_in_one_day", "trades_sized", "trades_at_tier_cap",
              "trades_unsized", "trades_stood_aside", "trades_need_exits", "trades_room_capped", "combines_out_of_room",
              "combines_abandoned_by_policy", "funded_abandoned", "funded_flips", "funded_flips_won",
              "intended_risk_total", "intended_capped_risk_total", "realised_risk_total")
_COMBINE_DAYS = ("purchase_day", "resolved_on", "reset_days")
_COMBINE_KEPT = ("index", "passed", "failed", "unresolved", "abandoned", "pass_day", "fail_day", "days", "trades",
                 "balance", "floor", "subscriptions_paid", "sizing", "resets", "dll", "rtp", "out_of_room",
                 "abandoned_by_policy", "household_closed", "ftp_closed")
_FUNDED_DAYS = ("activation_day", "ended_on", "combine_purchase_day")
_FUNDED_KEPT = ("index", "closed", "days", "trades", "balance", "floor", "n_payouts", "first_payout_day",
                "payout_days", "payout_cash", "gross_paid", "cash", "sizing", "denied", "dll", "combine_index",
                "consistency_forced", "abandoned", "flips", "flips_won", "second_trades", "second_qualified",
                "collect_trades", "collect_qualified", "peak_before_payout", "balance_at_first_payout",
                "household_closed", "ftp_closed", "ftp_denied")
_LOCKSTEP_MOVED = ("path", "combines", "funded", "breaches_per_day", "trades", "household")
_LOCKSTEP_KEPT = ("purchase_budget",)
#: records that must be empty on the second firm's path (their options are refused: each carries calendar days)
_LOCKSTEP_EMPTY = ("conduct", "account_days", "campaign_days", "focused_trader", "wallet_stop", "pause_after_funded",
                   "seat_ramp")
#: the household rule's record (`LockstepPath.household`): its one calendar day, and its other keys
_HOUSEHOLD_DAY = "closed_on"
_HOUSEHOLD_KEPT = ("reading", "triggers", "combines_closed", "funded_closed", "passes_closed")
#: `simulate_lockstep_path`'s arguments refused on the second firm's setup when set
_REFUSED_PATH_ARGS = ("conduct", "focused_trader", "flip", "flip_draw_factory", "wallet_stop", "pause_after_funded",
                      "seat_ramp", "record_days")


def check_second_firm_opens(value: Any) -> str | None:
    """The option's value: None (off: every firm from day 0, exactly as before) or one of `OPTIONS`."""
    if value is None:
        return None
    if not isinstance(value, str) or value not in OPTIONS:
        raise ValueError(f"second_firm_opens is None or one of {OPTIONS}, got {value!r}")
    return value


# ------------------------------------------------------------------------------------------------ the deal


class SequencedRouter(hh.HedgeRouter):
    """The path's deal: `hypo_hedge.HedgeRouter` (two firms, the cell's `mode`) whose deal on a day at or before
    `open_day` -- the second firm then holds no account -- is its own UNHEDGED deal with ONE firm on the first firm's
    accounts (`deal_alone`), so the first firm is dealt, and every refusal counted, exactly as it is alone, and no pair
    is formed (D-644 (2)). After `open_day` the deal is the two-firm deal of the cell's mode unchanged, on the same
    clocks and slots."""

    def __init__(self, stream: SignalStream, open_day: int, mode: str = hh.UNHEDGED, **kw: Any):
        super().__init__(stream, mode, n_firms=2, **kw)
        self.open_day = int(open_day)
        self.days_alone = 0

    def deal_alone(self, day: int, sub: _Submission) -> dict[tuple, list[int]]:
        mode = self.mode
        self.n_firms, self.mode = 1, hh.UNHEDGED  # the one-firm deal: nothing offered to the second firm, no pair
        try:
            out = hh.HedgeRouter.deal(self, day, [sub])
        finally:
            self.n_firms, self.mode = 2, mode
        self.days_alone += 1
        return out[0]

    def deal(self, day: int, subs: Sequence[_Submission]) -> list[dict[tuple, list[int]]]:
        if int(day) <= self.open_day:
            if len(subs) != 2:
                raise RuntimeError("every firm submits its accounts each day")
            if subs[1].keys:
                raise RuntimeError(f"the second firm holds an account on day {day}, at or before its opening day "
                                   f"{self.open_day}")
            return [self.deal_alone(day, subs[0]), {}]
        return super().deal(day, subs)


class _SequencedTurns(_Turns):
    """`two_firms._Turns` for two firms where the second joins on `open_day`: before it the first firm's hook deals
    its own accounts at once (nobody else moves); from `open_day` on the turns are `_Turns`' own."""

    def __init__(self, router: Any, wallet: _Wallet, timeout: float, open_day: int):
        super().__init__(2, router, wallet, timeout)
        self.open_day = int(open_day)

    def hook(self, party: int, day: int, sub: _Submission) -> dict:
        if party == 0 and int(day) < self.open_day:
            with self.cv:
                if self.aborted:
                    raise RuntimeError("another firm's run failed")
                self.subs[0] = sub
                self.out = [self.router.deal_alone(int(day), sub), {}]
                self.out_day = int(day)
                return self.out[0]
        return super().hook(party, day, sub)


class _OffsetTurns:
    """The second firm's view of the turns: its campaign's day `d` is the campaign's day `d + offset`."""

    def __init__(self, turns: _Turns, offset: int):
        self.turns, self.offset = turns, int(offset)

    def hook(self, party: int, day: int, sub: _Submission) -> dict:
        return self.turns.hook(party, int(day) + self.offset, sub)


class _OffsetTable:
    """The path's calendar as a campaign started on day `offset` reads it: its day `d` is the calendar's `d + offset`
    (the same historical day the first firm trades that day)."""

    def __init__(self, table: Any, offset: int):
        self.table, self.offset = table, int(offset)
        self.n_history = table.n_history
        self.seed = getattr(table, "seed", None)

    def historical_day(self, calendar_day: int) -> int:
        if calendar_day < 0:
            raise ValueError(f"calendar day must be non-negative, got {calendar_day}")
        return self.table.historical_day(int(calendar_day) + self.offset)


# ------------------------------------------------------------------------------------------------ the records


def _check_fields() -> None:
    """Refuse an engine whose records carry a field this module does not place on the campaign's calendar."""
    from propedge.campaign.lockstep import CombineRecord, FundedRecord, LockstepPath
    from propedge.campaign.reinvest import CampaignPath

    for cls, known in ((CampaignPath, _PATH_SERIES + _PATH_DAYS + _PATH_KEPT),
                       (CombineRecord, _COMBINE_DAYS + _COMBINE_KEPT), (FundedRecord, _FUNDED_DAYS + _FUNDED_KEPT),
                       (LockstepPath, _LOCKSTEP_MOVED + _LOCKSTEP_KEPT + _LOCKSTEP_EMPTY)):
        names = [f.name for f in dataclasses.fields(cls)]
        if sorted(names) != sorted(known):
            raise RuntimeError(f"{DECISION}: {cls.__name__}'s fields are not the ones the sequencing option places on "
                               f"the campaign's calendar (unknown: {sorted(set(names) - set(known))}; gone: "
                               f"{sorted(set(known) - set(names))}): say for each new field whether it holds a "
                               "calendar day before a sequenced run is read")


def _moved(day: Any, offset: int) -> Any:
    return None if day is None else int(day) + int(offset)


def on_campaign_calendar(lp: Any, offset: int, pool_before: Sequence[float], *, final_cash: float | None = None,
                         never_ruined: bool = False) -> Any:
    """A `LockstepPath` of a campaign started on the campaign's day `offset`, on the campaign's calendar: every
    calendar day plus `offset` (an evaluation's purchase, resolution and reset days; a funded account's activation,
    end and its evaluation's purchase day; the ruin day; the first payout's arrival; the household rule's closing day;
    a recorded trade's day), the per-day series led by `offset` days of nothing (no funded account, no breach, no
    trade) and the cash series by `pool_before` -- the pot on those days, the other firm's. Engine-relative fields (an
    account's pass, fail and payout days, counted from its own first session) are unchanged. `final_cash`: the pot at
    the path's end in place of the path's own (a campaign of no days); `never_ruined`: a firm that never opened is not
    a ruined campaign."""
    _check_fields()
    k = int(offset)
    if k < 0 or len(pool_before) != k:
        raise ValueError(f"the pot before the opening holds {len(pool_before)} days for an offset of {offset}")
    busy = [name for name in _LOCKSTEP_EMPTY if getattr(lp, name)]
    if busy and not (busy == ["conduct"] and set(lp.conduct) <= {"resets"}):
        raise ValueError(f"{DECISION}: the second firm's path carries {busy}, whose records hold calendar days this "
                         "option does not move")
    p = lp.path
    path = dataclasses.replace(
        p, cash_series=np.concatenate([np.asarray(pool_before, float), np.asarray(p.cash_series, float)]),
        active_funded_series=np.concatenate([np.zeros(k, dtype=np.asarray(p.active_funded_series).dtype),
                                             np.asarray(p.active_funded_series)]),
        trades_by_day=(0,) * k + tuple(int(x) for x in p.trades_by_day),
        ruin_day=None if never_ruined else _moved(p.ruin_day, k), ruined=False if never_ruined else p.ruined,
        days_to_first_payout=_moved(p.days_to_first_payout, k),
        final_cash=float(p.final_cash) if final_cash is None else float(final_cash))
    combines = tuple(dataclasses.replace(c, purchase_day=_moved(c.purchase_day, k), resolved_on=_moved(c.resolved_on, k),
                                         reset_days=tuple(int(d) + k for d in c.reset_days)) for c in lp.combines)
    funded = tuple(dataclasses.replace(
        f, activation_day=_moved(f.activation_day, k), ended_on=_moved(f.ended_on, k),
        combine_purchase_day=int(f.combine_purchase_day) + k if int(f.combine_purchase_day) >= 0
        else f.combine_purchase_day) for f in lp.funded)
    household = dict(lp.household)
    if household:
        if sorted(household) != sorted((_HOUSEHOLD_DAY, *_HOUSEHOLD_KEPT)):
            raise RuntimeError(f"{DECISION}: the household record's keys are {sorted(household)}")
        if int(household[_HOUSEHOLD_DAY]) >= 0:
            household[_HOUSEHOLD_DAY] = int(household[_HOUSEHOLD_DAY]) + k
    breaches = np.asarray(lp.breaches_per_day)
    return dataclasses.replace(
        lp, path=path, combines=combines, funded=funded,
        breaches_per_day=np.concatenate([np.zeros(k, dtype=breaches.dtype), breaches]),
        trades=tuple({**t, "day": int(t["day"]) + k} for t in lp.trades), household=household)


def first_firm_problems(joint: Any, alone: Any, open_day: int) -> list[str]:
    """Every way the first firm's record in the two-firm run differs, through the opening day, from its run alone
    (both `LockstepPath`s): the per-day cash, funded accounts, breaches and trades of days 0 .. `open_day`; the
    evaluations bought by then (and how each resolved by then) and the funded accounts activated by then; the first
    payout's arrival day, which is `open_day` in both."""
    a = int(open_day)
    out = []
    for what, x, y in (("cash", joint.path.cash_series, alone.path.cash_series),
                       ("active funded accounts", joint.path.active_funded_series, alone.path.active_funded_series),
                       ("breaches", joint.breaches_per_day, alone.breaches_per_day),
                       ("trades", joint.path.trades_by_day, alone.path.trades_by_day)):
        if not np.array_equal(np.asarray(x)[:a + 1], np.asarray(y)[:a + 1]):
            out.append(f"the {what} by day through day {a}")

    def combines(lp: Any) -> list[tuple]:
        return [(c.index, c.purchase_day, (c.resolved_on, c.passed, c.failed) if c.resolved_on is not None
                 and c.resolved_on <= a else None) for c in lp.combines if c.purchase_day <= a]

    def funded(lp: Any) -> list[tuple]:
        return [(f.index, f.activation_day, f.combine_index) for f in lp.funded if f.activation_day <= a]

    if combines(joint) != combines(alone):
        out.append(f"the evaluations bought through day {a}")
    if funded(joint) != funded(alone):
        out.append(f"the funded accounts activated through day {a}")
    if joint.path.days_to_first_payout != a or alone.path.days_to_first_payout != a:
        out.append(f"the first payout's arrival day ({joint.path.days_to_first_payout} in the two-firm run, "
                   f"{alone.path.days_to_first_payout} alone, the opening day {a})")
    return out


# ------------------------------------------------------------------------------------------------ the runner


def _policy_reads_the_day(policy: Any) -> bool:
    """Whether a risk policy's tree branches on the campaign day (`account_state`'s `day`)."""
    as_dict = getattr(policy, "as_dict", None)
    if not callable(as_dict):
        return False

    def walk(n: Any) -> bool:
        if isinstance(n, Mapping):
            return n.get("on") == "day" or any(walk(v) for v in n.values())
        if isinstance(n, (list, tuple)):
            return any(walk(v) for v in n)
        return False

    return walk(as_dict())


def setup_problems(second: Any) -> list[str]:
    """Every way the second firm's `FirmSetup` cannot be started late (an empty list: it can). An argument is set when
    it is anything but None or False -- a wallet stop of zero dollars is a wallet stop."""
    out = [f"{k} is set" for k in _REFUSED_PATH_ARGS
           if second.path.get(k) is not None and second.path.get(k) is not False]
    if second.draws.get("flip") is not None:
        out.append("a flip stream is set")
    if _policy_reads_the_day(second.path.get("risk_policy")):
        out.append("its risk policy branches on the campaign day")
    return out


def _draws(sp: Any, fs: Any) -> Any:
    from propedge.campaign.shared_days import SharedDayDraws

    return SharedDayDraws({0: list(sp.blocks)}, protocol=fs.protocol, seed=int(sp.seed), replay=bool(sp.replay),
                          **fs.draws)


def _kwargs(sd: Any) -> dict[str, Any]:
    kw = sd.lockstep_kwargs()
    if set(kw) != {"combine_draw_factory", "funded_draw_factory", "day_hook"}:
        raise ValueError("the joint run takes no flip stream")
    return kw


def _refuse_draw(index: int, start_day: int) -> Any:
    raise RuntimeError(f"{DECISION}: a firm that never opened asked for a draw")


def never_opened(alone: Any, second: Any, horizon_days: int) -> Any:
    """The second firm's record on a path where no payout arrived: the engine's own record of a campaign of no days
    (`simulate_lockstep_path` with a horizon of zero: no purchase, no account, no fee, every record in the engine's
    own shape) placed after the path's last day -- the pot's cash on every day is the first firm's."""
    from propedge.campaign.lockstep import simulate_lockstep_path

    empty = simulate_lockstep_path(second.protocol, seed=0, horizon_days=0, combine_draw_factory=_refuse_draw,
                                   funded_draw_factory=_refuse_draw, **second.path)
    cash = np.asarray(alone.path.cash_series, float)
    if len(cash) != int(horizon_days):
        raise RuntimeError(f"the first firm's run holds {len(cash)} days, not {horizon_days}")
    return on_campaign_calendar(empty, int(horizon_days), cash, final_cash=float(alone.path.final_cash),
                                never_ruined=True)


def run_opened(sp: Any, open_day: int, first: Any, second: Any, *, doubled: bool, gap: float, able: bool,
               timeout: float, record: bool, mode: str = hh.UNHEDGED) -> tuple[list[Any], Any]:
    """One path with the second firm's campaign started on `open_day` (the module docstring's step 3): (the two firms'
    `LockstepPath`s -- the second's in ITS OWN days, day 0 the opening day -- and the deal). Each firm in its own
    thread, taking turns at each day's deal on one wallet, as `hypo_hedge.run_joint` runs them."""
    from propedge.campaign.lockstep import simulate_lockstep_path

    a, H = int(open_day), int(sp.horizon_days)
    if not 0 <= a < H:
        raise ValueError(f"the opening day {open_day} is not one of the path's {H} days")
    bankroll = float(first.path["initial_bankroll"])
    router = SequencedRouter(SignalStream.from_blocks(list(sp.blocks)), a, mode, doubled=doubled, gap=gap,
                             able=able, record=record)
    jt = _SequencedTurns(router, _Wallet(bankroll), timeout, a)
    out: list[Any] = [None, None]
    errors: list[BaseException] = []
    counts = [len(b) for b in sp.blocks]

    def go_first() -> None:
        try:
            jt.enter(0)
            sd = _draws(sp, first)
            sd.router = FirmRouter(sd.table, counts, jt, 0)
            out[0] = simulate_lockstep_path(first.protocol, seed=int(sp.seed), horizon_days=H, wallet=jt.wallet,
                                            **_kwargs(sd), **first.path)
            jt.release(0)
        except BaseException as exc:                     # noqa: BLE001 -- raised again below, after the other stops
            errors.append(exc)
            jt.abort()

    def go_second() -> None:
        try:
            jt.enter(1)                                  # the first firm has reached the opening day's hook
            if float(jt.wallet.cash) < float(second.path["subscription"]):
                raise ValueError(f"{DECISION}: on its opening day {a} the pot holds less than the second firm's "
                                 "evaluation fee; the engine would end that firm's campaign there, where the day-0 "
                                 "firm would buy on a later evening -- refused, not approximated")
            sd = _draws(sp, second)
            sd.table = _OffsetTable(sd.table, a)         # its day d is the campaign's day d + a
            sd.router = FirmRouter(sd.table, counts, _OffsetTurns(jt, a), 1)
            out[1] = simulate_lockstep_path(second.protocol, seed=int(sp.seed), horizon_days=H - a, wallet=jt.wallet,
                                            **_kwargs(sd), **second.path)
            jt.release(1)
        except BaseException as exc:                     # noqa: BLE001
            errors.append(exc)
            jt.abort()

    threads = [threading.Thread(target=go_first, name="sequenced-firm-0"),
               threading.Thread(target=go_second, name="sequenced-firm-1")]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if errors:
        raise errors[0]
    return out, router


def run_sequenced(specs: Sequence[Any], setup: Any, *, n_firms: int, mode: str, doubled: bool, gap: float,
                  able: bool | None, timeout: float, record: bool, firm_setups: Sequence[Any] | None,
                  opens: str) -> list[Any]:
    """`hypo_hedge.run_joint`'s paths under the sequencing option (the module docstring): one `JointPath` a path, the
    firms' `LockstepPath`s on the campaign's calendar, `second_firm` its record -- the option, the first payout's
    arrival day at the first firm (None: none arrived), the day the second firm opened (the same day, or None) and the
    path's days."""
    if check_second_firm_opens(opens) != FIRST_PAYOUT_ARRIVAL:
        raise ValueError(f"the sequenced run is the option {FIRST_PAYOUT_ARRIVAL!r}, got {opens!r}")
    if int(n_firms) != 2:
        raise ValueError(f"{DECISION}: the sequencing option is two firms' (a first and a second), got {n_firms}")
    if mode not in hh.MODES:
        raise ValueError(f"{DECISION}: the deal is one of {hh.MODES}, got {mode!r}")
    if mode != hh.UNHEDGED and not doubled:
        raise ValueError("a hedged deal needs the doubled blocks")
    if firm_setups is not None and len(firm_setups) != 2:
        raise ValueError(f"firm_setups holds {len(firm_setups)} setups for 2 firms")
    first, second = list(firm_setups) if firm_setups is not None else [setup, setup]
    bad = setup_problems(second)
    if bad:
        raise ValueError(f"{DECISION}: the second firm's setup cannot be started late -- " + "; ".join(bad))
    able = bool(setup.draws.get("route_able", False)) if able is None else bool(able)
    if float(first.path["initial_bankroll"]) != float(setup.path["initial_bankroll"]):
        raise ValueError("the first firm's bankroll is not the pot's")
    _check_fields()
    out = []
    for sp in specs:
        H = int(sp.horizon_days)
        # 1. the first firm alone: its own campaign, the one-firm joint call
        solo = hh.run_joint([sp], first, n_firms=1, mode=hh.UNHEDGED, doubled=doubled, gap=gap, able=able,
                            timeout=timeout, record=record, firm_setups=[first])[0]
        alone = solo.paths[0]
        a = alone.path.days_to_first_payout
        if a is None or int(a) >= H:
            # 2. no payout arrived: the second firm never opens
            jp = hh.JointPath(paths=[alone, never_opened(alone, second, H)], router=solo.router)
            arrival = opened = None
        else:
            # 3. the two-firm run with the second firm's campaign started on the arrival day
            a = int(a)
            paths, router = run_opened(sp, a, first, second, doubled=doubled, gap=gap, able=able, timeout=timeout,
                                       record=record, mode=mode)
            bad = first_firm_problems(paths[0], alone, a)
            if bad:
                raise RuntimeError(f"{DECISION}: before its opening on day {a} the two-firm run's first firm is not "
                                   "the first firm alone -- " + "; ".join(bad))
            late = on_campaign_calendar(paths[1], a, np.asarray(paths[0].path.cash_series, float)[:a])
            jp = hh.JointPath(paths=[paths[0], late], router=router)
            arrival = opened = a
        jp.second_firm = {"decision": DECISION, "opens": FIRST_PAYOUT_ARRIVAL, "mode": mode,
                          "first_payout_arrival": arrival,
                          "opened_on": opened, "days": H, "first_firm_alone_through_opening": opened is not None}
        out.append(jp)
    return out


__all__ = ["DECISION", "FIRST_PAYOUT_ARRIVAL", "OPTIONS", "check_second_firm_opens", "SequencedRouter",
           "on_campaign_calendar", "first_firm_problems", "setup_problems", "never_opened",
           "run_opened", "run_sequenced"]
