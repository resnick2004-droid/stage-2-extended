"""Q-185: the three-way runner's **firm path** -- a lane's journey replayed through Stage 2's vendored lockstep engine,
on the firm's own verified rules, with the runner's race (or R-10's walk) as the engine's outcome draw.

    from extended import three_way_firm as TF
    rec = TF.simulate(schedule, TF.firm_for("TS"), TF.AccountPlan(), start, seed_indices, horizon, seed=..., part=...,
                      history=..., block_sessions=..., dates=session_dates)     # dates=None: a synthetic role only
    TF.J.p_b_values(rec, budget)           # the toy path's per-unit readings read it unchanged

**Why.** The runner's own replay (`three_way_journey.simulate`) is a stylised toy account. Here every lane (one unit: a
start and a coin seed index) is one path of the vendored `propedge.campaign.lockstep.simulate_lockstep_path`: the
evaluation and funded accounts, breaches, trailing floors, payouts, subscriptions and activation are the engine's, on
the firm's rules (`Firm`; Topstep's from Stage 2's verified ledger). Only each trade's outcome is this module's: the
draw the engine calls, `draw(1, rel_day, slot, cushion)`, answers with the runner's law on the coin field, keyed as
the runner keys it (`three_way_journey.CoinLanes`), so a design and its baselines stay paired on one field and the
firm path pairs with the toy path lane for lane.

**The draw's law** is the runner's (`three_way_journey._trade_mc`, Wave 3.2's last cycle), in dollars:
- the room is the one the engine hands the draw (the nearer of the floor's and, under a daily loss limit, the
  limit's); e the entry cost, x_t, x_s, x_f the target, stop and flatten exits' costs (each a worse fill's ticks
  added, measure 29); G = `t.target(e, x_t)` (the as-placed target in gross ticks: min(g, (level + e + x_t) / tick
  dollars) for a rule's profit level, booked as the engine books its need, m-2, m-3);
- **the take, at the fill** (E-247; the runner's `_l_fill` and `_classes`): taken when L_fill = min(l, room - e -
  max(x_s, x_f)) is above `EPS` dollars, for every law (a missed signal first). **Not taken where the floor binds: the
  account fails at the fill, whatever its room** -- the draw books the whole room, the engine breaches it
  (`B <= F + EPS`) and the lane counts it in `fill_failures`; **not taken where the daily loss limit binds: the day
  ends** (no further slot that session);
- the race: barrier L = min(l, room - e - x_s) (fractional, never rounded; B-1, N-5), p = L / (L + G) (+ P3's
  plant), -e + G - x_t, else -e - L - x_s -- a cushion-bound loss ends exactly on the floor;
- R-10's walk (`three_way_redraw.walk_run`, target G in ticks, barrier L / tick dollars): its exit's cost by kind; a
  flatten whose cost would pass the floor is clipped there **by the engine** (`max(pnl, -cushion)`), and fails it;
- a missed signal (measure 28) is no trade; the antithetic twin reads 1 - U; the as-walked reading (beside only) books
  the run's walked ticks on the side coin, on taken lanes only.
The draw never clips at the floor itself; the engine does (D-156).

**Accounts alternate (E-221, O-4).** Each session the day hook hands the live accounts, in the engine's rotation order,
to `extended.router.Router` (the plan's rotation, A15's declared values; the base `longest_waiting`, Stage 2 D-429):
every trade goes to **one** account, never several (copying one trade across accounts is conduct tier 1), and the
user's book (`extended.components.UserBook`) refuses two positions at once. An account's slots take its own trades in
time order; an account dealt more trades than its slots is refused. A moment read twice on one lane is refused.

**One open position across all accounts (Stage 2's strict rule, R2, D-409, D-429).** No position of the user is
entered while another is open on any account, or within `AccountPlan.strict_gap` minutes of one closing (Stage 2's
five, `rc_screen.STRICT_GAP`, the gap P-14, P-15 and P-16 were registered under); a lane that would is **refused**
(`RuntimeError`), never skipped -- the schedule is the runner's, and a schedule that breaks the rule is a property of
the design.

**H4's per-unit outputs** (MEASURES.md (30), (37)): each lane's sessions as `journey_measures.workload` and `supply`
read them -- the accounts trading the session (the engine's own trading set: those it opens with `begin_session`),
the trades entered (fill failures among them: the order was filled) with their entry and exit minutes, the signals
the schedule offers -- and from them `orders_max`, `accounts_max` and `taken_mean` per lane, always emitted.

**The calendar.** A lane's day 0 is the purchase evening; calendar day k (k = 1 .. horizon) trades the schedule's
session `start + k - 1` and closes at k; `rel[k]` is the path's cash at close k less the bankroll.

**The records** (`FirmRecords`, a `three_way_journey.Records`): `rel`, the first pass's close, the first payout's
arrival close, `P_B`'s month count (a second code path, held by `three_way_journey.p_b_values` against
`journey_measures.months_ahead_under`), the arrivals (the vendored `user_journey.payout_arrivals`), the account ordinal
(evaluations plus funded accounts, less one), the last close's live balance, the fill failures; the paths on request.

**Search years only.** No bar is read: a history enters only through its schedule. A run names its sessions' dates,
which must equal the search years' calendar session for session (`search_calendar`, derived here from the bars
manifest's `day_list`, metadata, cut at `extended.reader.CHOICE_END`) and the schedule's own dates where it carries
them, then pass `extended.search_cut.check_dates`
(Q-172; **a dependency**: until it is on this tree a local stub refuses every dated run). A run without dates is a
synthetic history, admitted only under a seed whose declared role draws synthetic histories (`three_way_seeds.STATUS`
"tests" or "design check"); a deciding role must name its dates.

**The money-carrying choices** (`AccountPlan.choices`, printed beside any result): the payout method, the seat's
freeing, the bankroll, the payout path and fraction, the rotation -- each with its class and source.

**The registered identity's seam** (`registered_runner`): the vendored path runner's signature, every path made by
this module's engine call (`path_call`) with the caller's draws passed through (`PassThrough`), so P-14's registered
gate paths can be reproduced through it (`identity/three_way_firm_identity.py`, heavy, the lead's).

**Not here.** The denial ladder (refused: the engine's ConductModel is seeded by the path, not by the unit's enforce
key); another firm than Topstep (refused: RD-01's classes read a trade-log router this draw does not carry).

Depends on Wave 3.2's runner (`three_way_journey`, `three_way_keys`, `three_way_redraw`, `three_way_seeds`). The engine
is imported lazily, in the process that replays (`use_vendored_stage2`); the law and the router are engine-free.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import date, datetime
from functools import lru_cache
from typing import Any, Sequence

import numpy as np

from extended import VENDOR_STAGE2
from extended import components as C
from extended import router as RT
from extended import three_way_journey as J
from extended import three_way_keys as K
from extended import three_way_redraw as RD
from extended import three_way_seeds as S

TASK = "Q-185"
EPS = J.EPS                     # the runner's: no take where L_fill is at most this many dollars
#: the outcome draws this path puts in the engine: the runner's race (deciding), or -- the identity's arm only -- the
#: vendored binary draws per account, as `lockstep.binary_draw_factories` builds them, through the same router
OUTCOMES = ("race", "engine_binary")
#: the path seed handed to the engine on the race arm: it drives the enforcement and flip streams only, neither of
#: which this path runs, so it moves nothing
PATH_SEED = 0
#: the seed roles whose histories are synthetic by declaration (`three_way_seeds.STATUS`): only these run undated
SYNTHETIC_STATUS = ("tests", "design check")
#: the router's firm (`extended.router.Routing(firm=...)`, Q-188c's n4: the firm's lever rows must be declared) -- the
#: design mode admits Topstep only, whose lever firm is "topstep"
FIRM = "topstep"
MANIFEST = VENDOR_STAGE2 / "data" / "bars" / "NQ" / "manifest.json"


# ------------------------------------------------------------------------------------------------ the firm, the plan


@dataclass(frozen=True)
class Firm:
    """A firm's contract as the engine reads it: `rules` (engine `Rules`), the fees, the payout lag, the funded cap
    and, for another contract, its account classes (None: the vendored Topstep classes)."""

    name: str
    rules: Any
    subscription: float
    billing_days: int
    activation: float
    payout_lag_days: int
    max_concurrent_accounts: int
    payout_method: str = ""
    combine_account_cls: type | None = None
    funded_account_cls: type | None = None
    source: str = ""


def topstep(method: str = "aeropay") -> Firm:
    """Topstep's 50K from Stage 2's verified ledger: `rules_for_method(method)` (every rule `rules_from_ledger` needs,
    refused unless verified), the method's payout lag and fee, and the verified funded cap, as the vendored campaign
    reads them. `aeropay` is the vendored campaign's and gate's own default (`simulate_lockstep_campaign`,
    `gate.run_gate`: `payout_method="aeropay"`)."""
    from extended import use_vendored_stage2

    use_vendored_stage2()
    from propedge.campaign.payout_method import payout_method_terms, rules_for_method
    from propedge.contract.rules import load_rules

    ledger = load_rules()
    rules = rules_for_method(method, ledger=ledger)
    terms = payout_method_terms(method, ledger=ledger)
    return Firm(name="TS", rules=rules, subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                activation=float(rules.activation), payout_lag_days=int(terms.lag_days),
                max_concurrent_accounts=int(ledger.value("max_active_funded_accounts")), payout_method=method,
                source=f"vendor/stage2/config/rules.yaml (verified); payout method {method} (the vendored campaign's "
                       f"default), lag {terms.lag_key}, fee {terms.fee_key} (article {terms.article_id})")


def firm_for(plan: str) -> Firm:
    """The firm of an RD-01 plan code. Only Topstep ("TS") is admitted on this path."""
    if plan == "TS":
        return topstep()
    raise NotImplementedError(f"REFUSED: the firm path admits Topstep ('TS') only; {plan!r}'s account classes "
                              "(RD-01, extended/firm_accounts.py) read a trade-log router or Lucid's setup that the "
                              "race draw does not carry -- a later item")


@dataclass(frozen=True)
class AccountPlan:
    """How the user holds accounts on the firm: seats, slots, the rotation and the funded leg's payout policy. The
    protocol's R and risk are nominal (each trade's bracket is the schedule's); the identity's binary arm reads them."""

    name: str = "one seat"
    trades_per_day: int = 4
    max_total_accounts: int | None = 1
    max_concurrent_combines: int = 1
    rotation: str = "longest_waiting"
    payout_path: str = "standard"
    keep_balance: float = 0.0
    payout_frac: float = 1.0
    initial_bankroll: float = 1_000_000.0
    reinvest: bool = True
    rr: float = 2.0
    risk: float = 500.0
    strict_gap: float = 5.0          # minutes: Stage 2's strict rule's gap (D-429; rc_screen.STRICT_GAP)
    latency: float = 5.0             # minutes from alert to order, for (30)'s screen hours (R4, D-266)

    def __post_init__(self) -> None:
        if self.rotation not in RT.ROTATIONS:                # refused unless one of A15's declared values
            raise RT.RoutingRefused(f"rotation {self.rotation!r} is not one of the declared values {RT.ROTATIONS}")
        if self.rotation == "by_component":                  # A16's pools need the Design, which this path carries not
            raise RT.RoutingRefused("by_component deals over a Design's components: not on the firm path")
        if int(self.trades_per_day) < 1:
            raise ValueError("a plan has at least one slot a session")
        if not (float(self.strict_gap) >= 0 and float(self.latency) >= 0):
            raise ValueError("the strict rule's gap and the latency are non-negative minutes")

    def choices(self, firm: Firm | None = None) -> dict[str, dict[str, Any]]:
        """Every money-carrying choice, its value, its class (fixed / searched / dropped) and its source."""
        out = {
            "seat_frees": {"value": "next_session", "class": "fixed",
                           "source": "the vendored path's default (Protocol.params has no 'seat_frees'); the engine's "
                                     "pessimistic reading, D-339 notes the help centre supports the same evening"},
            "initial_bankroll": {"value": float(self.initial_bankroll), "class": "fixed",
                                 "source": "no firm term: large enough that no path is ruined (a ruined path is "
                                           "refused); P_B's stop is read on the path (MEASURES.md section 2)"},
            "payout_path": {"value": self.payout_path, "class": "fixed",
                            "source": "Stage 2's Protocol default (the Standard path)"},
            "payout_frac": {"value": float(self.payout_frac), "class": "fixed",
                            "source": "Stage 2's Protocol default: the maximum allowed, as soon as eligible"},
            "keep_balance": {"value": float(self.keep_balance), "class": "fixed",
                             "source": "Stage 2's Protocol default (no buffer, propsim D-45 off)"},
            "rotation": {"value": self.rotation, "class": "fixed",
                         "source": "extended/router.py's base (Stage 2 D-429; lever A15's declared values)"},
            "seats": {"value": self.max_total_accounts, "class": "fixed",
                      "source": "the plan's (one seat: the toy path's one account at a time)"},
            "strict_gap": {"value": float(self.strict_gap), "class": "fixed",
                           "source": "Stage 2's strict one-position rule (R2, D-409; its gap, D-429), the gap P-14, "
                                     "P-15 and P-16 were registered under (their manifests' one_at_a_time)"},
            "latency": {"value": float(self.latency), "class": "fixed",
                        "source": "R4 (D-266): five minutes from an alert to a working order; the declaration's "
                                  "searched lever L (E-202 (2)(c)) where it searches it; reads only (30)'s screen hours"},
        }
        if firm is not None:
            out["payout_method"] = {"value": firm.payout_method, "class": "fixed", "source": firm.source}
        return out

    def protocol(self) -> Any:
        from extended import use_vendored_stage2

        use_vendored_stage2()
        from propedge.campaign.protocols import Protocol

        return Protocol(name=f"three-way firm path: {self.name}", combine_rr=float(self.rr),
                        combine_risk=float(self.risk), funded_rr=float(self.rr), funded_risk=float(self.risk),
                        trades_per_day=int(self.trades_per_day), payout_path=self.payout_path,
                        keep_balance=float(self.keep_balance), payout_frac=float(self.payout_frac),
                        family="three-way", source="extended/three_way_firm.py",
                        note="nominal R and risk: each trade's bracket and outcome are the schedule's and the race's")


# ------------------------------------------------------------------------------------------------ search years


class _CutStub:
    """Stands in for `extended.search_cut` (Q-172) until it is on this tree: refuses every dated run."""

    def check_dates(self, dates: Sequence[Any], last: Any = None, what: str = "the job") -> None:
        raise RuntimeError("REFUSED: extended.search_cut (Q-172, wt/wt-user) is not on this tree; a dated firm-path "
                           "run waits for it")


def search_cut() -> Any:
    try:
        from extended import search_cut as SC        # Q-172 (wt/wt-user): the search years' cut
    except ImportError:
        return _CutStub()
    return SC


def _as_date(x: Any) -> date:
    if isinstance(x, datetime):
        return x.date()
    if isinstance(x, date):
        return x
    return date.fromisoformat(str(x)[:10])


@lru_cache(maxsize=1)
def search_calendar() -> frozenset:
    """The search years' NQ sessions: the bars manifest's `day_list` (metadata, no price; `search_cut`'s PASSTHROUGH)
    on or before `extended.reader.CHOICE_END`."""
    from extended import reader as R

    days = json.loads(MANIFEST.read_text(encoding="utf-8"))["day_list"]
    return frozenset(d for d in (_as_date(x) for x in days) if R.CHOICE_START <= d <= R.CHOICE_END)


def check_dates(dates: Any, start: int, horizon: int, block_sessions: int, *, seed: Any,
                calendar: frozenset | None = None, schedule_dates: Any = None) -> None:
    """The window's sessions in the search years. Undated: admitted only under a synthetic role's seed. Dated (the red
    team's C1-5): the block's dates in order, none past the search years, and **equal to the run's calendar** -- the
    first `block_sessions` sessions of the search years' calendar (`search_calendar`, derived here; `calendar`
    replaces it in the tests only), so session k of the schedule is the calendar's k-th session; and, where the
    schedule carries its own dates (`schedule_dates`, a schedule's `dates`), equal to those too; then
    `search_cut.check_dates`."""
    if dates is None:
        role = getattr(seed, "role", None)
        if not (S.is_issued(seed) and S.STATUS.get(role) in SYNTHETIC_STATUS):
            raise ValueError(f"REFUSED: an undated run is a synthetic history, admitted only under a seed of a role "
                             f"whose status is one of {SYNTHETIC_STATUS}; the {role or 'unissued'} seed's run names "
                             "its sessions' dates")
        return
    if isinstance(dates, str):
        raise ValueError("dates are the block's session dates (or None for a synthetic role), not a label")
    from extended import reader as R

    ds = [_as_date(d) for d in dates]
    if len(ds) != block_sessions:
        raise ValueError(f"the block has {block_sessions} sessions but {len(ds)} dates")
    if any(b <= a for a, b in zip(ds, ds[1:])):
        raise ValueError("the block's dates are not in order")
    window = ds[start:start + horizon]
    late = [d for d in window if d > R.CHOICE_END]
    if late:
        raise ValueError(f"REFUSED (E-208): the window reads {len(late)} session(s) past the search years' last day "
                         f"{R.CHOICE_END} (first {late[0]})")
    cal = sorted(search_calendar() if calendar is None else calendar)
    if len(cal) < block_sessions or ds != cal[:block_sessions]:
        bad = next((k for k, (a, b) in enumerate(zip(ds, cal)) if a != b), min(len(ds), len(cal)))
        raise ValueError(f"REFUSED (C1-5): the run's dates do not equal the search years' calendar (session {bad}: "
                         f"{ds[bad] if bad < len(ds) else None} against {cal[bad] if bad < len(cal) else None})")
    if schedule_dates is not None and [_as_date(d) for d in schedule_dates] != ds:
        raise ValueError("REFUSED (C1-5): the schedule's own dates do not equal the run's dates")
    search_cut().check_dates(window, what="the firm path's window")


# ------------------------------------------------------------------------------------------------ the draws


def scheduled(t: J.Trade, name: str) -> C.ScheduledTrade:
    """The router's view of a scheduled trade: its session, fill and exit (its busy interval); the side is the
    martingale reading's, one side for every trade (the outcome is the redraw's)."""
    return C.ScheduledTrade(
        firm=FIRM, component=name, source="schedule", session=int(t.session), date=_label(int(t.session)),
        decision=int(t.decision),
        alert=int(t.decision), live=int(t.entry), tag="", order_kind="market", ticket_rule="", side=1,
        side_source="martingale", fill_slot=int(t.entry), fill_price=0.0, resting=False, stop_ticks=int(t.l),
        target_ticks=int(t.g), rr=float(t.g) / float(t.l), exit_slot=int(t.exit), exit_kind=str(t.exit_reason),
        flatten_slot=int(t.exit), window_flatten=False, instrument=str(t.underlying), underlying=str(t.underlying),
        gross_ticks=0, net_r=None, busy_until=int(t.exit))


def _label(session: int) -> str:
    """The router's one-call-per-day key for a schedule session (Q-188c's n5): the session's index, never a date (the
    window's dates are checked apart, `check_dates`)."""
    return f"session-{int(session)}"


def _name(key: tuple[str, int]) -> str:
    return f"{key[0]}:{int(key[1])}"


class LaneDraw:
    """One account's outcome draw on one lane: the engine calls it with the account's engine day and slot."""

    settlement = "race"      # D-156: the race settles against the room it is handed

    def __init__(self, lane: "Lane", key: tuple[str, int], start_day: int, inner: Any = None):
        self.lane, self.key, self.start_day, self.inner = lane, key, int(start_day), inner

    def begin_session(self, balance: float, floor: float) -> None:
        """The engine's session hook: the account's cushion to the floor at the session's start. The engine opens
        every account trading that session (its trading set), which (30)'s accounts count; the calendar day is the
        day hook's, called first."""
        self.lane.begin(self.key, float(balance) - float(floor), self.lane.today)

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray, **kw: Any) -> np.ndarray:
        if kw:
            raise ValueError(f"REFUSED: the race draw takes no {sorted(kw)} (need-aware or stretch exits)")
        if int(n) != 1:
            raise ValueError("the lockstep path calls one account at a time")
        cal = self.start_day + 1 + int(day)
        return np.array([self.lane.outcome(self, cal, int(slot), float(np.asarray(cushion)[0]))])


class PassThrough:
    """A caller's draw passed through this module's engine call unchanged: every attribute and call is the inner
    draw's (its settlement, its session hook, its risk setter, its ledger fields)."""

    def __init__(self, inner: Any):
        object.__setattr__(self, "_inner", inner)

    def __call__(self, *a: Any, **kw: Any) -> Any:
        return self._inner(*a, **kw)

    def __getattr__(self, name: str) -> Any:
        return getattr(object.__getattribute__(self, "_inner"), name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._inner, name, value)


@dataclass
class TradeLog:
    """What one lane's draws did, trade by trade (kept on request). Each row: the calendar day, slot, account name,
    moment, the room handed, the floor's room, the class ('race', 'walk', 'fill_fail', 'day_end', 'missed',
    'as_walked'), the barrier L in dollars, p (a race; a walk's exit kind), G in ticks, the gross, the costs, the
    change returned."""

    rows: list = field(default_factory=list)


class Lane:
    """One unit (start, seed index j) of a start's coin field, its router and its accounts' session states."""

    def __init__(self, sim: "_Start", j: int):
        self.sim, self.j = sim, int(j)
        self.router = RT.Router(RT.Routing(sim.plan.rotation, firm=FIRM))
        self.dealt: dict[int, dict[str, list[J.Trade]]] = {}
        self.taken: set = set()
        self.state: dict[str, list] = {}
        self.fill_failures = 0
        self.open_days: dict[int, int] = {}                  # calendar day -> accounts the engine opened
        self.entered: dict[int, list[tuple[int, int]]] = {}  # calendar day -> (entry, exit) minutes of trades entered
        self.held: dict[int, list[tuple[int, int, int]]] = {}  # session -> positions (entry, exit, moment)
        self.log = TradeLog() if sim.log else None
        self.today: int | None = None

    def day_hook(self, day: int, keys: list) -> None:
        """The engine's day hook: today's live accounts in its rotation order; the session's trades dealt by the
        router, one account each."""
        s = self.sim
        trades = s.by_session.get(s.start + int(day) - 1, ()) if int(day) >= 1 else ()
        names = [_name(k) for k in keys]
        dealt: dict[str, list[J.Trade]] = {n: [] for n in names}
        if trades and names:
            sts = [scheduled(t, s.name) for t in trades]
            back = {id(x): t for x, t in zip(sts, trades)}
            ses = int(trades[0].session)
            for rt in self.router.route([C.DaySchedule(FIRM, ses, _label(ses), sts)], {FIRM: names},
                                        date=_label(ses)):
                dealt[rt.account].append(back[id(rt.trade)])
            for n, lst in dealt.items():
                if len(lst) > s.plan.trades_per_day:
                    raise ValueError(f"REFUSED: account {n} is dealt {len(lst)} trades on day {day} but holds "
                                     f"{s.plan.trades_per_day} slots (a trade would be dropped)")
        self.dealt[int(day)] = dealt
        self.today = int(day)

    def begin(self, key: tuple[str, int], cushion: float, cal: int | None = None) -> None:
        self.state[_name(key)] = [cushion, 0.0, False]       # the floor's room at the start, today's net, day ended
        if cal is not None:
            self.open_days[int(cal)] = self.open_days.get(int(cal), 0) + 1

    def hold(self, t: J.Trade, cal: int) -> None:
        """Stage 2's strict rule: refused when the position would open while another of the user's is open, on any
        account, or within `strict_gap` minutes of one closing (the absolute clock: session x 1440 + minute)."""
        gap = float(self.sim.plan.strict_gap)
        a0, a1 = t.session * K.DAY_SLOTS + t.entry, t.session * K.DAY_SLOTS + t.exit
        for s in (t.session - 1, t.session, t.session + 1):
            for b0, b1, m in self.held.get(s, ()):
                if a0 < b1 + gap and b0 < a1 + gap:
                    raise RuntimeError(f"REFUSED (D-409 R2, D-429): the position at moment {t.moment} opens while the "
                                       f"one at moment {m} is open or within {gap:g} minutes of its close")
        self.held.setdefault(t.session, []).append((a0, a1, t.moment))
        self.entered.setdefault(int(cal), []).append((int(t.entry), int(t.exit)))

    def days(self, horizon: int) -> list[dict[str, Any]]:
        """The lane's sessions 1 .. horizon as `journey_measures.workload` and `supply` read them."""
        s = self.sim
        return [{"accounts": self.open_days.get(k, 0), "taken": tuple(self.entered.get(k, ())),
                 "offered": tuple(float(t.entry) for t in s.by_session.get(s.start + k - 1, ()))}
                for k in range(1, int(horizon) + 1)]

    def _note(self, *row: Any) -> None:
        if self.log is not None:
            self.log.rows.append(row)

    def outcome(self, draw: LaneDraw, cal: int, slot: int, room: float) -> float:
        name = _name(draw.key)
        mine = self.dealt.get(cal, {}).get(name, [])
        if slot >= len(mine):
            return math.nan
        t = mine[slot]
        if t.moment in self.taken:
            raise RuntimeError(f"REFUSED: the moment {t.moment} offered twice on one lane (a copied trade)")
        self.taken.add(t.moment)
        st = self.state.get(name)
        if st is None:
            raise RuntimeError("the engine did not open the account's session (begin_session)")
        if st[2]:
            self._note(cal, slot, name, t.moment, room, math.nan, "day_end", 0.0, math.nan, 0.0, 0.0, 0.0, math.nan)
            return math.nan
        floor_room = st[0] + st[1]
        if draw.inner is not None:                       # the identity's binary arm: the vendored draw itself
            out = float(draw.inner(1, cal - draw.start_day - 1, slot, np.array([room]))[0])
        else:
            out = self.law(t, room, floor_room, cal, slot, name, st)
        if not math.isnan(out):
            self.hold(t, cal)                                # entered: one open position across all accounts
            st[1] += max(out, -room)                         # the engine's clips: the floor's and the limit's room
        return out

    def law(self, t: J.Trade, room: float, floor_room: float, cal: int, slot: int, name: str, st: list) -> float:
        s, arm = self.sim, self.sim.arm
        if arm.missed_q > 0 and s.uniform(t, K.MISSED, self.j) < arm.missed_q:
            self._note(cal, slot, name, t.moment, room, floor_room, "missed", 0.0, math.nan, 0.0, 0.0, 0.0, math.nan)
            return math.nan
        extra = float(arm.worse_ticks) * t.tvn
        e, xt, xs, xf = t.entry_cost + extra, t.x_target + extra, t.x_stop + extra, t.x_flat + extra
        G = float(t.target(e, xt))
        win_d = G * t.tvn
        L_fill = min(float(t.l) * t.tvn, room - e - max(xs, xf))
        if not L_fill > EPS:                                 # the take refused at the fill (E-247)
            if floor_room <= room + EPS:                     # the floor binds: failed at the fill
                self.fill_failures += 1
                self._note(cal, slot, name, t.moment, room, floor_room, "fill_fail", 0.0, math.nan, G, 0.0, 0.0,
                           -room)
                return -room
            st[2] = True                                     # the daily loss limit binds: the day ends
            self._note(cal, slot, name, t.moment, room, floor_room, "day_end", 0.0, math.nan, G, 0.0, 0.0, math.nan)
            return math.nan
        if arm.reading == "as_walked":
            if t.walked_ticks is None:
                raise ValueError("the as-walked reading needs each trade's walked ticks")
            side = 1.0 if s.uniform(t, K.SIDE, self.j) < 0.5 else -1.0
            gross = side * float(t.walked_ticks) * t.tvn
            out = -e + gross - xs                           # beside only: the stop side's cost on every exit (n-5)
            self._note(cal, slot, name, t.moment, room, floor_room, "as_walked", math.nan, math.nan, G, gross, e + xs,
                       out)
            return out
        L = min(float(t.l) * t.tvn, room - e - xs)
        if t.law == "race":
            p = L / (L + win_d)
            win = bool(RD.race_outcome(np.array([s.uniform(t, K.RACE, self.j)]), np.array([p]), arm.plant_eps)[0])
            out = (-e + win_d - xt) if win else (-e - L - xs)
            self._note(cal, slot, name, t.moment, room, floor_room, "race", L, p, G, win_d if win else -L,
                       e + (xt if win else xs), out)
            return out
        step = int(t.walk_step)
        coins, j = s.coins, self.j
        coins.record(t, K.WALK, [j])

        def read(rows, first, count):
            return coins.coin(t, K.WALK, count, np.asarray([j])[rows], first=first, record=False)

        v, k = RD.walk_run(read, 1, G, np.array([L / t.tvn]), step, int(t.walk_n), J.WALK_CHUNK)
        kind = int(k[0])
        gross = float(v[0]) * t.tvn
        cost = xt if kind == 1 else xs if kind == -1 else xf
        out = -e + gross - cost                             # a flatten past the floor: the engine clips it
        self._note(cal, slot, name, t.moment, room, floor_room, "walk", L, float(kind), G, gross, e + cost, out)
        return out


class _Start:
    """The lanes of one start: one coin field (`three_way_journey.CoinLanes`), its race, side and missed uniforms read
    for every lane at once the first time any lane needs a trade's."""

    def __init__(self, schedule: J.Schedule, plan: AccountPlan, start: int, arm: J.ArmSpec, coins: Any, log: bool):
        self.by_session, self.name, self.plan = schedule.by_session, schedule.name, plan
        self.start, self.arm, self.coins, self.log = int(start), arm, coins, log
        self.cache: dict[tuple[int, int], np.ndarray] = {}

    def uniform(self, t: J.Trade, kind: int, j: int) -> float:
        key = (t.moment, int(kind))
        u = self.cache.get(key)
        if u is None:
            u = self.coins.coin(t, kind)[:, 0]
            self.cache[key] = u
        return float(u[j])


# ------------------------------------------------------------------------------------------------ the engine call


def engine_kwargs(firm: Firm, plan: AccountPlan, horizon: int, *, record_trades: bool = False,
                  record_days: bool = False) -> dict[str, Any]:
    """The path's keywords for `simulate_lockstep_path`: the firm's terms and the plan's seats, over horizon + 1 days."""
    kw = dict(edge=0.0, rules=firm.rules, initial_bankroll=float(plan.initial_bankroll), horizon_days=int(horizon) + 1,
              max_concurrent_accounts=int(firm.max_concurrent_accounts), subscription=float(firm.subscription),
              billing_days=int(firm.billing_days), activation=float(firm.activation),
              payout_lag_days=int(firm.payout_lag_days), max_concurrent_combines=int(plan.max_concurrent_combines),
              reinvest=bool(plan.reinvest), max_total_accounts=plan.max_total_accounts,
              record_trades=bool(record_trades), record_days=bool(record_days))
    if firm.combine_account_cls is not None:
        kw["combine_account_cls"] = firm.combine_account_cls
    if firm.funded_account_cls is not None:
        kw["funded_account_cls"] = firm.funded_account_cls
    return kw


def path_call(protocol: Any, *, seed: int, path_kwargs: dict[str, Any], combine_draw_factory: Any,
              funded_draw_factory: Any, day_hook: Any = None) -> Any:
    """This module's one engine call: one path of the vendored lockstep."""
    from extended import use_vendored_stage2

    use_vendored_stage2()
    from propedge.campaign import lockstep as LS

    return LS.simulate_lockstep_path(protocol, seed=int(seed), combine_draw_factory=combine_draw_factory,
                                     funded_draw_factory=funded_draw_factory, day_hook=day_hook, **path_kwargs)


def registered_runner(protocol: Any, path_kwargs: dict[str, Any], seeds: Sequence[int], draw_factories_for_path: Any,
                      flip_for_path: Any, wallet_for_path: Any, *, workers: int = 1, pool: Any = None,
                      memory_per_worker_gb: float | None = None) -> list:
    """The vendored `lockstep._run_paths`'s signature, every path made by `path_call` with the caller's draws passed
    through (`PassThrough`) and its day hook unchanged -- the seam the registered identity runs P-14's gate through.
    One process; no flip stream; no shared wallet."""
    if int(workers) != 1 or pool is not None:
        raise ValueError("the firm path's registered runner runs its paths in one process")
    if flip_for_path is not None or wallet_for_path is not None or draw_factories_for_path is None:
        raise ValueError("the firm path's registered runner takes the caller's draw factories, no flip and no wallet")
    out = []
    for s in seeds:
        made = draw_factories_for_path(int(s))
        if len(made) == 3:
            cf, ff, hook = made
        elif len(made) == 2:
            (cf, ff), hook = made, None
        else:
            raise ValueError("the firm path's registered runner takes no flip stream")
        out.append(path_call(protocol, seed=int(s), path_kwargs=path_kwargs,
                             combine_draw_factory=lambda i, d, _f=cf: PassThrough(_f(i, d)),
                             funded_draw_factory=lambda i, d, _f=ff: PassThrough(_f(i, d)), day_hook=hook))
    return out


# ------------------------------------------------------------------------------------------------ the records


@dataclass
class FirmRecords(J.Records):
    """`three_way_journey.Records` on the firm path, with the firm, the engine's paths and the draws' logs when kept."""

    firm: str = ""
    paths: tuple = ()
    logs: tuple = ()
    orders_max: np.ndarray | None = None      # H4: (30)'s orders a session, its maximum per lane
    accounts_max: np.ndarray | None = None    # H4: (30)'s accounts trading a session, its maximum per lane
    taken_mean: np.ndarray | None = None      # H4: (37)'s trades entered a session, its mean per lane
    workload: tuple = ()                      # (30) per lane: `journey_measures.workload`'s dict
    supply: tuple = ()                        # (37) per lane: `journey_measures.supply`'s dict
    days: tuple = ()                          # each lane's sessions as (30) and (37) read them (kept with `log`)


def months_ahead(rel: np.ndarray, horizon: int, budget: float | None) -> int:
    """`P_B`'s count as the toy path makes it: at close 21 m (m = 1 .. 3, within the horizon) ahead above `TOL` with
    the peak out-of-pocket through the closes before it at most the budget."""
    n = 0
    for m in (1, 2, 3):
        k = J.MONTH * m
        if k > horizon:
            break
        spent = max(0.0, -float(np.min(rel[:k])))
        if rel[k] > J.TOL and (budget is None or spent <= float(budget)):
            n += 1
    return n


def records_of(path: Any, *, bankroll: float, lag: int, horizon: int, budget: float | None) -> dict[str, Any]:
    """One lane's record fields from its engine path."""
    from propedge.research.user_journey import payout_arrivals

    rel = np.asarray(path.path.cash_series, float)[:horizon + 1] - float(bankroll)
    passes = [c.resolved_on for c in path.combines if c.passed and c.resolved_on is not None]
    arr = payout_arrivals([(f.activation_day, int(lag), f.payout_days, f.payout_cash) for f in path.funded],
                          int(horizon))
    live_c = [c.balance for c in path.combines if c.resolved_on is None and not (c.passed or c.failed)]
    live_f = [f.balance for f in path.funded if f.ended_on is None and not f.closed]
    return {"rel": rel, "first_pass": min(passes) if passes else -1, "arrivals": arr,
            "first_pay": arr[0][0] if arr else -1, "ahead": months_ahead(rel, horizon, budget),
            "accounts": len(path.combines) + len(path.funded) - 1, "balance": float(sum(live_c) + sum(live_f))}


def _check_schedule(schedule: J.Schedule, plan: AccountPlan, start: int, horizon: int) -> None:
    most = max((len(v) for k, v in schedule.by_session.items() if start <= k < start + horizon), default=0)
    if plan.max_total_accounts is not None and most > plan.trades_per_day * int(plan.max_total_accounts):
        raise ValueError(f"REFUSED: a session holds {most} trades but the plan has {plan.trades_per_day} slots on "
                         f"each of {plan.max_total_accounts} seats (a trade would be dropped)")


def simulate(schedule: J.Schedule, firm: Firm, plan: AccountPlan, start: int, seed_indices: Sequence[int],
             horizon: int, *, seed: int, part: int, history: int, block_sessions: int, dates: Any = None,
             arm: J.ArmSpec = J.ArmSpec(), budget: float | None = None, guard: K.KeyGuard | None = None,
             outcome: str = "race", binary_seed: int | None = None, keep_paths: bool = False,
             record_trades: bool = False, record_days: bool = False, log: bool = False,
             calendar: frozenset | None = None) -> FirmRecords:
    """The units (start, c), c in `seed_indices`, each one path of the vendored lockstep on `firm`'s rules under
    `plan`, the trades of sessions start .. start + horizon - 1 drawn by the runner's law on the unit's coin field.
    Exactly `horizon` sessions are traded (closes 0 .. horizon). `outcome="engine_binary"` (the identity's arm) puts
    the vendored binary draws in instead, from `binary_seed`, through the same router and slots."""
    J.check_window(start, horizon, block_sessions)
    check_dates(dates, start, horizon, block_sessions, seed=seed, calendar=calendar,
                schedule_dates=getattr(schedule, "dates", None))
    idx = [int(c) for c in seed_indices]
    if len(set(idx)) != len(idx):
        raise ValueError("REFUSED: a seed index repeats (two lanes would read one coin field)")
    if outcome not in OUTCOMES:
        raise ValueError(f"outcome is one of {OUTCOMES}, got {outcome!r}")
    if arm.enforcement_q > 0:
        raise ValueError("REFUSED: the denial ladder is not built on the firm path (the engine's ConductModel is "
                         "seeded by the path, not by the unit's enforce key); 0 % is the verdict's")
    if outcome == "engine_binary" and binary_seed is None:
        raise ValueError("the binary arm takes an explicit seed")
    _check_schedule(schedule, plan, start, horizon)
    protocol = plan.protocol()
    from propedge.campaign import lockstep as LS

    coins = J.CoinLanes(seed, part, history, start, idx, guard, arm.twin)
    st = _Start(schedule, plan, start, arm, coins, log)
    n = len(idx)
    out: dict[str, list] = {k: [] for k in ("rel", "first_pass", "first_pay", "ahead", "accounts", "balance",
                                            "arrivals")}
    fills, paths, logs, works, sups, dayss = [], [], [], [], [], []
    from extended import journey_measures as JM

    kw = engine_kwargs(firm, plan, horizon, record_trades=record_trades, record_days=record_days)
    for j in range(n):
        lane = Lane(st, j)
        if outcome == "engine_binary":
            bc, bf = LS.binary_draw_factories(protocol, 0.0, int(binary_seed), firm.rules)
            cf = lambda i, d, _l=lane, _b=bc: LaneDraw(_l, ("combine", i), d, _b(i, d))
            ff = lambda i, d, _l=lane, _b=bf: LaneDraw(_l, ("funded", i), d, _b(i, d))
        else:
            cf = lambda i, d, _l=lane: LaneDraw(_l, ("combine", i), d)
            ff = lambda i, d, _l=lane: LaneDraw(_l, ("funded", i), d)
        path = path_call(protocol, seed=PATH_SEED, path_kwargs=kw, combine_draw_factory=cf, funded_draw_factory=ff,
                         day_hook=lane.day_hook)
        if path.path.ruined:
            raise RuntimeError(f"REFUSED: lane {j} of start {start} ran out of bankroll at day {path.path.ruin_day}; "
                               "P_B's stop is read on the path, so the plan's bankroll must cover every path")
        r = records_of(path, bankroll=plan.initial_bankroll, lag=firm.payout_lag_days, horizon=horizon, budget=budget)
        for k in out:
            out[k].append(r[k])
        fills.append(lane.fill_failures)
        dd = lane.days(horizon)
        works.append(JM.workload(dd, float(plan.latency)))
        sups.append(JM.supply(dd))
        if log:
            dayss.append(dd)
        if keep_paths:
            paths.append(path)
        if log:
            logs.append(lane.log.rows)
    return FirmRecords(start=int(start), seed_indices=tuple(idx), rel=np.asarray(out["rel"]).reshape(n, horizon + 1),
                       first_pass=np.asarray(out["first_pass"], np.int64),
                       first_pay=np.asarray(out["first_pay"], np.int64), ahead=np.asarray(out["ahead"], np.int64),
                       arrivals=out["arrivals"], accounts=np.asarray(out["accounts"], np.int64), budget=budget,
                       balance=np.asarray(out["balance"], float), fill_failures=np.asarray(fills, np.int64),
                       firm=firm.name, paths=tuple(paths), logs=tuple(logs),
                       orders_max=np.asarray([w["orders_max"] for w in works], float),
                       accounts_max=np.asarray([w["accounts_max"] for w in works], float),
                       taken_mean=np.asarray([x["taken_mean"] for x in sups], float), workload=tuple(works),
                       supply=tuple(sups), days=tuple(dayss))


__all__ = ["TASK", "EPS", "OUTCOMES", "PATH_SEED", "SYNTHETIC_STATUS", "Firm", "topstep", "firm_for", "AccountPlan",
           "search_cut", "search_calendar", "check_dates", "scheduled", "LaneDraw", "PassThrough", "TradeLog", "Lane",
           "engine_kwargs", "path_call", "registered_runner", "FirmRecords", "months_ahead", "records_of",
           "simulate"]
