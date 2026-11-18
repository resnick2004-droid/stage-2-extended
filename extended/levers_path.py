"""RD-03's A-1 (`prereg/RD-03_contract_levers.md` 14.1; its build Q-119, E-153): Stage 2's lockstep path, re-composed in
Q-71's pattern so that the contract levers act inside it -- Back2Funded's reactivation, the hold's expiry, the
house-money fee rule, a counters channel and the Focused Trader purchase measure's counting of reactivations -- each a
marked addition, off by default.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import levers_path as LP
    lv = LP.Levers(reactivations=1, reactivation_fee=..., reactivation_window_days=..., ...)
    lp = LP.simulate_lockstep_path(protocol, ..., levers=lv)      # every vendored argument, plus this one

**Why it exists.** Every lever of RD-03 changes which offered trades are routed, bought or kept inside the path's own
end-of-day steps: a reactivation in the seat step (2.1), an expiry in the hold queue (U-1), a fee withheld at the
evening purchases, the activations and the start-of-day billing (2.3). None is reachable through a funded-account class
(Appendix C item 21: the vendored `FundedAccount` is kept so the engine admits the Focused Trader models), so the path
itself is re-composed. The vendored tree is read-only (E-002), and a module attribute of it substituted during a call is
not done (Q-47; E-011).

**The copy.** `simulate_lockstep_path` below is the vendored function's text (`propedge.campaign.lockstep`, Stage 2
f1b42e2 vendored under E-002), copied verbatim, with additions only on lines that carry the comment marker `Q-119`:

* (0) the keyword `levers` (default None), last in the signature; with None -- or with a `Levers` whose every option is
  off and whose counters are off -- no added statement does anything, so the path is the vendored one bit for bit;
* (a) the reactivation step of 2.1 first in the end-of-day seat step, with the Focused Trader bar (U-5);
* (b) the hold's expiry (U-1) just before the hold queue fills free seats;
* (c) the house-money fee rule (2.3) at every fee: the evening purchases (the loop and every one of its diagnostic
  conditions, so "refused by this alone" stays true), the activations, and the start-of-day billing; and its trigger,
  read after the day's payout arrivals;
* (d) a counters channel (`Levers.counters`): the counts of 9.3 read at each close and left, at the path's end, for the
  caller in the same process (`take_published`), which wraps the path as a `LeverPath` -- every vendored field
  unchanged, the counts beside;
* (e) the Focused Trader purchase measure's counting of reactivations (`Levers.count_reactivations`, U-6's conservative
  reading).

A reactivation debits the cash and the engine's `total_fees` together (n2). Every helper the body calls is the vendored
one, imported from the vendored module, never copied; the vendored `FundedAccount` and `CombineAccount` are used
unchanged (a reactivated account is a new instance of the path's funded class).

**The guard, refusing.** Each copied function was composed from the vendored function whose LF source hashes to its pin
(`VENDORED_SHA256`); every call of the path checks it first and refuses (`RuntimeError`) if the vendored text changed.
`recomposition_problems()` checks the composition itself: each copied function with its marked lines removed parses to
the vendored one statement for statement (the docstrings aside; `extended.campaign.recomposition_problems`).

**The path runner (A-3).** `_one_path`, `_path_chunk` and `_run_paths` are the vendored runner's text, copied verbatim,
so that a campaign's paths call this module's path: `_one_path` alone has one marked line (the path it calls, wrapped
for the counters), and `_path_chunk` and `_run_paths` none -- their names resolve to this module's. The levers travel
in the paths' keywords (`levers`), so they reach a worker with its task. `extended/campaign.py` takes this runner when
its `levers` keyword is given (lines marked Q-119), and `extended/gate.py` passes it on.

**The replay (A-2).** `levers_args` puts a cell's seat and price keywords on a replay's path arguments, and
`replay_with` gives Q-17's adapter (`extended/user_beside.py`, lines marked Q-119) the replay through this path, each
start's session dates attached (the 30 calendar days of 2.1 and U-1 read on them; in the gate, 21 sessions).
"""
from __future__ import annotations

import dataclasses
import hashlib
import inspect
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Sequence

from extended import use_vendored_stage2

use_vendored_stage2()

import numpy as np  # noqa: E402

from propedge.campaign import lockstep as _vl  # noqa: E402
from propedge.campaign.lockstep import (  # noqa: E402,F401  -- every name the vendored bodies use, the vendored objects
    ACTIVATION_ON_ACTIVATION,
    ACTIVATION_ON_PASS,
    ACTIVATION_TIMINGS,
    CampaignPath,
    CombineAccount,
    ConductModel,
    DEFAULT_PAYOUT_TIMING,
    DayHook,
    DrawFactory,
    EPS,
    FTP_CORRECTIVE,
    FTP_SLOWDOWN,
    FocusedTraderModel,
    FundedAccount,
    LockstepPath,
    Protocol,
    _KIND_ENFORCEMENT,
    _KIND_FLIP_DIRECTION,
    _WorkerEnvironment,
    _losers_not_smaller,
    _record_combine,
    _record_funded,
    _rolling_max,
    _takes_caps,
    _takes_collect,
    _takes_flips,
    _takes_rrs,
    _takes_seconds,
    _takes_states,
    binary_draw_factories,
    check_parallel_inputs,
    check_pause_after_funded,
    check_payout_timing,
    check_purchase_budget,
    check_seat_ramp,
    check_wallet_stop,
    child_seed,
    path_pool,
    session_slots,
)

#: the comment marker on every added line of this module's copied functions
MARKER = "Q-119"
#: sha256 of each vendored function's source text (LF), from which the copy below was composed (Stage 2 f1b42e2,
#: vendored under E-002; `propedge/campaign/lockstep.py`)
VENDORED_SHA256 = {
    "simulate_lockstep_path": "6435af74aa34030463cd8a7d8eb34c61869425ee2f2267c38abeaee2fd523271",
    "_one_path": "8ecfffd94d95edd404eea50c683b71cfa941fa7cde22d4f2e9661ea748b8796a",
    "_path_chunk": "bec2e5139447eb9f500694e6f92f190823b3f8021d1368627c9b0f8602ca7d56",
    "_run_paths": "2845d418ae962d3adf52814558ba0c9da7cd105845399eb2d709b8a4e0c5b378",
}

#: the house-money rules (2.3) and the expiry readings (U-1)
HOUSE_RULES = ("off", "stop", "zero")
EXPIRY_RULES = ("none", "30")

#: the counts the levers alone make: zero on every path with every option off (9.1 item 4; T-10)
LEVER_KEYS = ("reactivations", "reactivations_first", "reactivations_second", "reactivation_fees",
              "eligible_losses", "eligible_losses_first_life", "eligible_losses_later_life",
              "reactivations_refused_limit", "reactivations_refused_cash", "reactivations_refused_placement",
              "reactivations_refused_seat", "reactivations_lapsed", "reactivations_counted_in_ftp",
              "passes_expired", "passes_queued", "house_triggered", "house_purchase_days_withheld",
              "house_rebills_withheld", "house_activations_withheld", "house_closes_not_ahead",
              "house_purchases_after_trigger", "house_fees_not_ahead")
#: the engine's own counts read through the channel (any cell, `ref` included)
ENGINE_KEYS = ("fees_subscription", "fees_activation", "activations_refused_cash", "purchase_days_refused_cash",
               "max_accounts_live", "sessions_five_funded_evals_running", "same_day_bought_and_breached",
               "max_trades_one_session", "max_funded_live", "max_running",
               "evaluations_bought", "activations", "peak_queue", "max_queue_wait")
#: the lists the channel carries (per path)
LIST_KEYS = ("reactivation_days", "reactivation_ordinals", "reactivation_loss_days", "reactivated_fates",
             "queue_waits", "queue_waits_units", "house_trigger_day", "house_cash_waits", "cash_closes",
             "reactivation_wait_sessions", "reactivation_checks", "purchase_days", "acts", "fee_days")


class LeverRefused(ValueError):
    """A lever's options are not ones RD-03 declares (crossed levers, resets on, activation at the pass, ...)."""


@dataclass(frozen=True)
class Levers:
    """One cell's options for the path (A-1) and its seat and price keywords for the replay and the gate (A-2, A-3,
    A-4). Every default is off: `Levers()` is the reference. Rule values are never typed here: the cell builder
    (`extended/cl_reading.py`) loads them from their records (`extended/levers_terms.py`) and the readings table
    (`extended/levers_readings.py`).

    * `reactivations` -- L-B: 0 (off), else the per-XFA limit (1 or 2); with it `reactivation_fee`, and the window
      `reactivation_window_days` (calendar days, the replay) and `reactivation_window_sessions` (the gate);
    * `expiry` -- U-1: "none" or "30", with `expiry_days` and `expiry_sessions`;
    * `house` -- L-H: "off", "stop" or "zero";
    * `count_reactivations` -- A-1 (e): a reactivation counted in the Focused Trader purchase measure;
    * `counters` -- A-1 (d): the counts of 9.3 published at the path's end;
    * `max_concurrent_combines`, `lift_joint_cap`, `stop_buying_when_queued` -- L-I's seat keywords (None / False:
      the base's);
    * `subscription`, `activation` -- A-4's prices (None: the base's);
    * `day_ordinals` -- set per start by the replay (`with_dates`): each engine day's calendar date, so the windows are
      read in calendar days; None (the gate) reads them in sessions.
    """

    reactivations: int = 0
    reactivation_fee: float | None = None
    reactivation_window_days: int | None = None
    reactivation_window_sessions: int | None = None
    expiry: str = "none"
    expiry_days: int | None = None
    expiry_sessions: int | None = None
    house: str = "off"
    count_reactivations: bool = False
    counters: bool = False
    max_concurrent_combines: int | None = None
    lift_joint_cap: bool = False
    stop_buying_when_queued: bool | None = None
    subscription: float | None = None
    activation: float | None = None
    day_ordinals: tuple[int, ...] | None = None

    def __post_init__(self) -> None:
        bad = []
        if isinstance(self.reactivations, bool) or int(self.reactivations) != self.reactivations \
                or int(self.reactivations) < 0:
            bad.append(f"reactivations {self.reactivations!r}")
        if self.expiry not in EXPIRY_RULES:
            bad.append(f"expiry {self.expiry!r} (one of {EXPIRY_RULES})")
        if self.house not in HOUSE_RULES:
            bad.append(f"house {self.house!r} (one of {HOUSE_RULES})")
        if self.reactivations and (self.reactivation_fee is None or self.reactivation_window_days is None
                                   or self.reactivation_window_sessions is None):
            bad.append("a reactivation needs its fee and its window in days and in sessions")
        if self.expiry != "none" and (self.expiry_days is None or self.expiry_sessions is None):
            bad.append("an expiry needs its days and its sessions")
        if self.count_reactivations and not self.reactivations:
            bad.append("count_reactivations without reactivations")
        inventory = (self.max_concurrent_combines is not None or self.lift_joint_cap
                     or self.stop_buying_when_queued is not None)
        prices = self.subscription is not None or self.activation is not None
        on = [n for n, v in (("Back2Funded", bool(self.reactivations)), ("house money", self.house != "off"),
                             ("the inventory", inventory), ("the pricing path", prices)) if v]
        if len(on) > 1:
            bad.append(f"the levers are not crossed (2.5): {', '.join(on)} together")
        if self.expiry != "none" and not (inventory or self.house != "off"):
            bad.append("the hold's expiry is read only on the inventory and house-money cells (U-1)")
        if bad:
            raise LeverRefused("REFUSED (RD-03 A-1): " + "; ".join(bad))

    @property
    def path_options_on(self) -> bool:
        """Whether any option acts inside the path (A-1 (a), (b), (c), (e))."""
        return bool(self.reactivations) or self.expiry != "none" or self.house != "off" or self.count_reactivations

    @property
    def off(self) -> bool:
        """Every option at its off value and no seat or price keyword: the reference (the counters aside)."""
        return (not self.path_options_on and self.max_concurrent_combines is None and not self.lift_joint_cap
                and self.stop_buying_when_queued is None and self.subscription is None and self.activation is None)

    def with_dates(self, dates: Sequence[str]) -> "Levers":
        """These options with one replay's session dates: engine day k (k >= 1) is the k-th session, `dates[k - 1]`;
        day 0, the purchase evening before the first session, takes the first session's date (nothing that a window
        reads -- a pass, a breach -- can happen on it)."""
        ords = [date.fromisoformat(str(d)[:10]).toordinal() for d in dates]
        return dataclasses.replace(self, day_ordinals=tuple([ords[0], *ords]) if ords else ())

    def as_dict(self) -> dict[str, Any]:
        d = dataclasses.asdict(self)
        d.pop("day_ordinals", None)
        return d


@dataclass(frozen=True)
class LeverPath(LockstepPath):
    """A path with the counters channel's counts beside it (A-1 (d)): every vendored field the engine's, unchanged."""

    lever_counts: dict[str, Any] = field(default_factory=dict)


#: the counts the path left for its caller in this process (one slot; `take_published`)
_PUBLISHED: list[dict[str, Any] | None] = [None]


def take_published() -> dict[str, Any] | None:
    """The counts the last path run in this process published (and clear the slot)."""
    out, _PUBLISHED[0] = _PUBLISHED[0], None
    return out


def wrap(lp: Any, levers: Any) -> Any:
    """The path as its caller hands it on: with the counters on, a `LeverPath` with the counts it published; else the
    path itself."""
    counts = take_published()
    if levers is None or not getattr(levers, "counters", False):
        return lp
    return LeverPath(**{f.name: getattr(lp, f.name) for f in dataclasses.fields(LockstepPath)},
                     lever_counts=dict(counts or {}))


def zero_counts() -> dict[str, Any]:
    return {**{k: 0 for k in (*LEVER_KEYS, *ENGINE_KEYS)}, **{k: [] for k in LIST_KEYS}, "house_trigger_day": -1}


class LeverState:
    """One path's lever state and counts. Built by `begin` (None when nothing is on, so the copied path is the vendored
    one); every method is called from a marked line of the copied path."""

    def __init__(self, levers: Levers, *, initial_bankroll: float, horizon_days: int):
        self.lv = levers
        self.initial = float(initial_bankroll)
        self.horizon = int(horizon_days)
        self.counting = bool(levers.counters)
        self.reactivating = bool(levers.reactivations)
        self.expiring = levers.expiry != "none"
        self.house = levers.house
        self.house_on = levers.house != "off"
        self.triggered: int | None = None
        self.c = zero_counts()
        self.root: dict[int, int] = {}          # funded index -> its XFA's first index
        self.used: dict[int, int] = {}          # an XFA's reactivations so far
        self.waiting: list[tuple[Any, int, int]] = []   # (the lost account, its closure day, its XFA) to reactivate
        self.reactivated: dict[int, int] = {}   # reactivated index -> 1 or 2
        self.refused: dict[str, set] = {"limit": set(), "cash": set(), "placement": set(), "seat": set()}
        self.queued: dict[int, int] = {}        # a pass's index -> the evening it was first left waiting
        self.cash_wait: dict[int, int] = {}     # a pass's index -> the evenings its activation was withheld
        self.seen_combines = 0
        self.ftp_counted = 0
        self.acts = np.zeros((int(horizon_days), 3), dtype=np.int16)    # m4: running, live funded, queue, per close

    @staticmethod
    def begin(levers: Any, *, initial_bankroll: float, horizon_days: int, reset_failed_combines: bool,
              activation_timing: str) -> "LeverState | None":
        if levers is None:
            return None
        if not isinstance(levers, Levers):
            raise TypeError(f"levers must be an extended.levers_path.Levers, got {type(levers).__name__}")
        if reset_failed_combines:
            raise LeverRefused("REFUSED (RD-03 2.5): every cell runs with reset_failed_combines False")
        if activation_timing != ACTIVATION_ON_ACTIVATION:
            raise LeverRefused("REFUSED (RD-03 T-4): every cell runs with the activation paid on activation")
        if not levers.path_options_on and not levers.counters:
            return None
        return LeverState(levers, initial_bankroll=initial_bankroll, horizon_days=horizon_days)

    # ---- time
    def elapsed(self, d0: int, d1: int) -> int:
        """Calendar days from engine day d0 to d1 on the replay's dates; sessions in the gate (no dates)."""
        o = self.lv.day_ordinals
        if o is None:
            return int(d1) - int(d0)
        return int(o[min(int(d1), len(o) - 1)]) - int(o[min(int(d0), len(o) - 1)])

    def _limit(self, days: int | None, sessions: int | None) -> int:
        return int(sessions) if self.lv.day_ordinals is None else int(days)

    # ---- (c) house money
    def _net(self, cash: float) -> float:
        return float(cash) - self.initial

    def after_arrivals(self, day: int, cash: float) -> None:
        """The trigger (2.3): the first close at which net cash is above zero, after the day's arrivals."""
        if self.house_on and self.triggered is None and self._net(cash) > EPS:
            self.triggered = int(day)
            self.c["house_triggered"] = 1
            self.c["house_trigger_day"] = int(day)

    def withholds_purchase(self, cash: float, fee: float) -> bool:
        """Whether house money refuses an evaluation purchase now (pure: read in the loop and its diagnostics)."""
        if not self.house_on or self.triggered is None:
            return False
        if self.house == "stop":
            return True
        return self._net(float(cash) - float(fee)) <= EPS

    def withholds_activation(self, cash: float, fee: float, c: Any) -> bool:
        """Whether house money refuses the activation of the pass `c` now (and counts it): after the trigger only if
        net cash after it would not be above zero, under either rule; the pass waits on hold."""
        if not self.house_on or self.triggered is None:
            return False
        if self._net(float(cash) - float(fee)) > EPS:
            return False
        self.c["house_activations_withheld"] += 1
        self.cash_wait[int(c.index)] = self.cash_wait.get(int(c.index), 0) + 1
        return True

    def withholds_rebill(self, cash: float, fee: float, day: int) -> bool:
        """Whether house money withholds a running evaluation's rebill (and counts it): under `stop` every rebill after
        the trigger, under `zero` one that would not leave net cash above zero; the evaluation is abandoned at the start
        of its billing day, before that day trades (U-2)."""
        if not self.house_on or self.triggered is None:
            return False
        if self.house == "zero" and self._net(float(cash) - float(fee)) > EPS:
            return False
        self.c["house_rebills_withheld"] += 1
        return True

    # ---- (a) Back2Funded
    def _eligible(self, a: Any) -> bool:
        """2.1 and U-7: ended by an MLL breach in the engine's sense -- `closed`, not at the policy's request, not by a
        tier-3 denial, a household rule or the Focused Trader Program -- with no payout requested in its current life."""
        return (bool(a.closed) and not bool(getattr(a, "abandoned", False)) and int(getattr(a, "denied", 0)) == 0
                and not bool(getattr(a, "household_closed", False)) and not bool(getattr(a, "ftp_closed", False))
                and int(a.n_payouts) == 0)

    def reactivate(self, day: int, cash: float, total_fees: float, accounts_funded: int, funded: list,
                   finished_funded: list, funded_cls: type, factory: Any, flip_factory: Any, rules: Any,
                   funded_horizon_days: int, payout_timing: str, ftp_placed: Any, ftp_bought: Any,
                   cap: int) -> tuple[float, float, int, list]:
        """2.1: at this evening's start, every eligible loss of today is offered a reactivation, up to its XFA's limit;
        one the cash cannot pay is offered again each later evening within the window, then lapses. A reactivation
        takes the lost account's seat (it leaves the funded list now), is bought before the hold queue and the
        purchases, and trades from the next session."""
        lv = self.lv
        out = list(funded)
        for a in funded:
            if a.ended_on is None or int(a.ended_on) != int(day) or not self._eligible(a):
                continue
            root = self.root.get(int(a.index), int(a.index))
            self.c["eligible_losses"] += 1
            self.c["eligible_losses_later_life" if int(a.index) in self.reactivated else
                   "eligible_losses_first_life"] += 1
            self.c["reactivation_loss_days"].append(int(day))
            if self.used.get(root, 0) >= int(lv.reactivations):
                self.refused["limit"].add(int(a.index))
                continue
            self.waiting.append((a, int(day), root))
        keep: list[tuple[Any, int, int]] = []
        window = self._limit(lv.reactivation_window_days, lv.reactivation_window_sessions)
        fee = float(lv.reactivation_fee)
        for a, closed_on, root in self.waiting:
            if self.elapsed(closed_on, day) > window:
                self.c["reactivations_lapsed"] += 1
                continue
            if ftp_placed is not None:                      # U-5: barred under a placement in force
                self.refused["placement"].add(int(a.index))
                keep.append((a, closed_on, root))
                continue
            present = any(x is a for x in out)
            if not present and len(out) >= int(cap):         # a later evening: a seat is needed (never a sixth)
                self.refused["seat"].add(int(a.index))
                keep.append((a, closed_on, root))
                continue
            if cash < fee:
                self.refused["cash"].add(int(a.index))
                keep.append((a, closed_on, root))
                continue
            self.c["reactivation_checks"].append(
                (int(self._eligible(a)), int(day) - int(closed_on), int(ftp_placed is not None),
                 int(int(a.index) in self.refused["cash"])))
            cash -= fee
            total_fees += fee
            self.fee_paid(cash, day)
            j = int(accounts_funded)
            if present:
                out = [x for x in out if x is not a]
                finished_funded.append(a)
            out.append(funded_cls(
                index=j, activation_day=day, draw=factory(j, day), horizon_days=int(funded_horizon_days),
                floor_start=rules.xfa_mll_start, policy_override=a.policy_override, dll=a.dll,
                combine_index=a.combine_index, combine_purchase_day=a.combine_purchase_day,
                payout_timing=payout_timing,
                flip_draw=flip_factory(j, day) if flip_factory is not None else None))
            accounts_funded += 1
            self.used[root] = self.used.get(root, 0) + 1
            self.root[j] = root
            self.reactivated[j] = self.used[root]
            self.c["reactivations"] += 1
            self.c["reactivations_first" if self.used[root] == 1 else "reactivations_second"] += 1
            self.c["reactivation_fees"] += fee
            self.c["reactivation_days"].append(int(day))
            self.c["reactivation_wait_sessions"].append(int(day) + 1 - int(closed_on))
            self.c["reactivation_ordinals"].append(int(self.used[root]))
            if lv.count_reactivations and ftp_bought is not None:      # (e): U-6's conservative reading
                ftp_bought[day] += 1
                self.c["reactivations_counted_in_ftp"] += 1
        self.waiting = keep
        return cash, total_fees, accounts_funded, out

    # ---- (b) the hold's expiry
    def expire(self, day: int, queue: list) -> None:
        """U-1's `exp_30`: a pass not activated within the window of the close it passed at is lost at the first close
        past it, unpaid and unseated (removed from the queue in place)."""
        window = self._limit(self.lv.expiry_days, self.lv.expiry_sessions)
        kept = []
        for c in queue:
            if self.elapsed(int(c.resolved_on), day) > window:
                self.c["passes_expired"] += 1
                continue
            kept.append(c)
        queue[:] = kept

    def fee_paid(self, cash: float, day: int) -> None:
        """m3: every fee paid after house money's trigger is read at the act -- net cash after it above zero."""
        if self.house_on and self.triggered is not None and self._net(cash) <= EPS:
            self.c["house_fees_not_ahead"] += 1

    def activated(self, c: Any, day: int, cash: float | None = None) -> None:
        """A pass activated tonight: its wait (calendar days on the replay, sessions in the gate) if it waited."""
        self.c["activations"] += 1
        if cash is not None:
            self.fee_paid(cash, day)
        if int(c.resolved_on) < int(day):
            w = self.elapsed(int(c.resolved_on), day)
            self.c["queue_waits"].append(w)
            self.c["max_queue_wait"] = max(int(self.c["max_queue_wait"]), w)   # the evening it leaves the queue
        if int(c.index) in self.cash_wait:
            self.c["house_cash_waits"].append(int(self.cash_wait.pop(int(c.index))))

    def count(self, key: str) -> None:
        self.c[key] += 1

    # ---- the purchase step's diagnostics (9.3)
    def purchase_step(self, *, others_allow: bool, house_refuses: bool, cash_refuses: bool) -> None:
        if others_allow and house_refuses:
            self.c["house_purchase_days_withheld"] += 1
        if others_allow and cash_refuses and not house_refuses:
            self.c["purchase_days_refused_cash"] += 1

    # ---- (d) the day's counts
    def end_of_day(self, day: int, cash: float, running: list, funded: list, queue: list,
                   finished_combines: list, cap: int) -> None:
        live_f = [a for a in funded if a.ended_on is None]
        self.c["max_funded_live"] = max(int(self.c["max_funded_live"]), len(live_f))
        self.c["max_running"] = max(int(self.c["max_running"]), len(running))
        self.c["peak_queue"] = max(int(self.c["peak_queue"]), len(queue))
        for c in queue:                                   # the longest any pass has waited at a close (U-1's pair)
            self.c["max_queue_wait"] = max(int(self.c["max_queue_wait"]), self.elapsed(int(c.resolved_on), day))
        bought = sum(1 for c in running if int(c.purchase_day) == int(day))
        self.c["evaluations_bought"] += bought
        self.c["purchase_days"].extend([int(day)] * bought)
        if int(day) < len(self.acts):
            self.acts[int(day)] = (len(running), len(live_f), len(queue))
        if self.house_on and self.triggered is not None:
            self.c["house_purchases_after_trigger"] += sum(1 for c in running if int(c.purchase_day) == int(day))
        self.c["max_accounts_live"] = max(int(self.c["max_accounts_live"]), len(running) + len(live_f) + len(queue))
        if len(live_f) >= int(cap) and running:
            self.c["sessions_five_funded_evals_running"] += 1
        for c in queue:
            if int(c.resolved_on) < int(day) or int(c.index) in self.cash_wait:
                self.queued.setdefault(int(c.index), int(day))
        self.c["passes_queued"] = len(self.queued)
        if self.house_on and self.triggered is not None:
            if self._net(cash) <= EPS:                     # the construction of 2.3, read at every close after it
                self.c["house_closes_not_ahead"] += 1
        for c in finished_combines[self.seen_combines:]:
            if c.failed and c.resolved_on is not None and int(c.resolved_on) == int(c.purchase_day):
                self.c["same_day_bought_and_breached"] += 1
        self.seen_combines = len(finished_combines)
        for a in funded:
            if (int(a.index) in self.reactivated and a.ended_on is not None and int(a.ended_on) == int(a.activation_day)
                    and bool(a.closed) and not bool(getattr(a, "abandoned", False))):   # a breach, not a closure
                self.c["same_day_bought_and_breached"] += 1

    def publish(self, *, all_funded: list, fee_sub: Any, fee_act: Any, trades_by_day: Any, total_fees: float,
                cash_series: Any) -> None:
        """At the path's end: the counts left for the caller (`take_published`), with the reactivated accounts'
        fates and the fees by kind, checked against the engine's total (a reactivation is a fee of its own kind)."""
        if not self.counting:
            return
        c = self.c
        c["reactivations_refused_limit"] = len(self.refused["limit"])
        c["reactivations_refused_cash"] = len(self.refused["cash"])
        c["reactivations_refused_placement"] = len(self.refused["placement"])
        c["reactivations_refused_seat"] = len(self.refused["seat"])
        c["fees_subscription"] = float(np.sum(fee_sub))
        c["fees_activation"] = float(np.sum(fee_act))
        c["max_trades_one_session"] = int(np.max(trades_by_day)) if len(trades_by_day) else 0
        fates = []
        for a in all_funded:
            k = self.reactivated.get(int(a.index))
            if k is None:
                continue
            won = bool(a.pnls) and float(a.pnls[0]) > 0
            fates.append({"index": int(a.index), "ordinal": int(k), "activation_day": int(a.activation_day),
                          "won_opening": won, "paid": int(a.n_payouts) > 0,
                          "lost_before_payout": bool(a.closed) and int(a.n_payouts) == 0,
                          "ended_on": -1 if a.ended_on is None else int(a.ended_on)})
        c["reactivated_fates"] = fates
        c["fees_total_engine"] = float(total_fees)
        c["cash_closes"] = np.asarray(cash_series, dtype=float).copy()
        c["acts"] = self.acts
        c["fee_days"] = np.stack([np.asarray(fee_sub, float), np.asarray(fee_act, float)], axis=1)
        c["fees_by_kind_problem"] = abs(c["fees_subscription"] + c["fees_activation"] + float(c["reactivation_fees"])
                                        - float(total_fees)) > 1e-6
        _PUBLISHED[0] = {k: (list(v) if isinstance(v, list) else v) for k, v in c.items()}
        # the refusals of 9.3, each printed: the limit, the cash, the placement, and the seat a delayed one may lack


#: the vendored sources are checked once a process, at the first path (A-1's guard)
_GUARDED: list[bool] = []


def _guard() -> None:
    if not _GUARDED:
        check_vendored_source()
        _GUARDED.append(True)


# ------------------------------------------------------------------------------------------------ the copies
# Everything from here to the guard's section is the vendored text; every added line is marked Q-119.


def simulate_lockstep_path(
    protocol: Protocol,
    *,
    edge: float,
    seed: int,
    rules: Any,
    initial_bankroll: float,
    horizon_days: int,
    max_concurrent_accounts: int,
    subscription: float,
    billing_days: int,
    activation: float,
    payout_lag_days: int,
    max_concurrent_combines: int = 1,
    reinvest: bool = True,
    max_attempts: int | None = None,
    stop_buying_when_queued: bool = True,
    activation_timing: str = ACTIVATION_ON_ACTIVATION,
    combine_max_days: int = 2000,
    funded_horizon_days: int = 504,
    combine_draw_factory: DrawFactory | None = None,
    funded_draw_factory: DrawFactory | None = None,
    day_hook: DayHook | None = None,
    record_trades: bool = False,
    conduct: ConductModel | None = None,
    record_days: bool = False,
    near_miss_frac: float = 0.2,
    reset_failed_combines: bool = False,
    reset_fee: float | None = None,
    risk_policy: Any = None,
    max_total_accounts: int | None = None,
    payout_timing: str = DEFAULT_PAYOUT_TIMING,
    wallet: Any = None,
    flip_draw_factory: Callable[[int, int], Any] | None = None,
    flip: Any = None,
    funded_account_cls: type | None = None,
    household_closure: bool | None = None,
    focused_trader: FocusedTraderModel | None = None,
    purchase_budget: tuple[int, int] | None = None,
    combine_account_cls: type | None = None,
    wallet_stop: float | None = None,
    pause_after_funded: int | None = None,
    seat_ramp: int | None = None,
    levers: Any = None,  # Q-119
) -> LockstepPath:
    """Simulate one campaign, stepping every live account through each calendar day.

    D-619: `combine_account_cls` is the evaluation account's class -- a subclass of `CombineAccount` for another
    contract's evaluation (`propedge.research.hedge_cycle.StaticCombineAccount`, a HYPOTHETICAL firm's green-day pass
    rule); None is `CombineAccount`, Topstep's, exactly as before.

    D-495 (4): `focused_trader` is Topstep's Focused Trader Program (`FocusedTraderModel`, article 10551016) as a
    campaign-level event: the declared pattern measures watched over a rolling window and, once one reaches its
    declared threshold, the declared path's placement -- Slowdown (no purchases or resets, then one account at a time)
    or Corrective (every account closed at that close, pending payouts denied, one account at a time for six months).
    None (the default) runs none of it, exactly as before; a model whose thresholds are never reached leaves the path
    identical to None. `LockstepPath.focused_trader` records the model, every placement and the measures' maxima.
    Topstep's program: refused with another firm's funded class.

    D-501: `purchase_budget=(K, window_days)` is a self-imposed restraint, the campaign's own (no firm rule): a Combine
    purchase or a reset is refused while the campaign's Combine purchases and resets in the last `window_days` trading
    days (that day included, its purchases so far counted) have reached K; a refused reset ends the Combine as a
    failure, as any refused reset does; purchases resume as the window rolls. None (the default) runs none of it,
    exactly as before. `LockstepPath.purchase_budget` records the budget, the purchases and resets taken, their
    rolling maximum, the days a purchase was refused by the budget alone and the resets it refused.

    D-630: three more restraints of the campaign's own on buying evaluations (no firm rule), each None (the default)
    for off, exactly as before, and each a condition of the purchase step beside the budget's -- a purchase is made
    only when every condition allows it. (a) `wallet_stop=W`: no Combine is bought while the cash out of pocket
    (`initial_bankroll` less the cash at that moment, read before each purchase) is above W dollars; subscriptions
    already running and activation fees are paid as before. (b) `pause_after_funded=F` (D-632's wording; no latch):
    no Combine is bought at a purchase step where the campaign holds at least F funded accounts (activated and not
    ended, counted after that evening's activations) and its first payout has not yet ARRIVED (the cash received,
    `payout_lag_days` after the request); when it holds fewer than F, purchases are as the base's -- the condition is
    read again at every purchase step -- and once the first payout has arrived the option never binds again; open
    Combines keep trading and their passes are activated as before. (c) `seat_ramp=s0`: the
    campaign holds at most s0 accounts of both kinds together (running Combines, funded accounts, passes waiting) and
    one more for each payout that has arrived, up to the base's `max_total_accounts`, which it needs; the funded and
    the Combine limits follow, since neither count can pass the total. As with the budget (D-502) a reset counts with
    the purchases under (a) and (b) -- a refused reset ends its Combine as a failure -- while (c) never refuses one (a
    reset keeps a seat already held). `LockstepPath.wallet_stop`, `.pause_after_funded` and `.seat_ramp` record each
    option, the days it alone refused a purchase and the resets it refused; the pause's record also counts the
    purchase steps at which its condition held, their separate spells, and the days purchases resumed because the
    funded accounts held fell below F.

    R7 (docs/TWO_FIRMS.md): `funded_account_cls` is the funded account's class -- a subclass of `FundedAccount` for
    another firm's funded contract (`propedge.contract.lucid.LucidFundedAccount`); None is `FundedAccount`, Topstep's,
    exactly as before.

    R7 (the multi-firm repository's D-30; docs/TWO_FIRMS.md): `household_closure` applies a funded class's household
    rule. A class that has one says so with `HOUSEHOLD_CLOSES_AT_LIVE` (its default reading) and raises
    `closes_household` on the account that triggers it (Lucid: the account took its fifth payout and the household
    enters the live review pool, 12945796, 16558826). With the rule on, the first account to raise it at a close ends
    every other live account of this campaign at that close (`close_household`: no breach, nothing of a balance
    credited; payouts already requested still arrive), a pass waiting for a seat or made that day is never activated,
    and the path buys nothing more. None takes the class's default; False only counts the triggers (the optimistic
    reading). `LockstepPath.household` records the reading and the counts. A class without the rule (Topstep's) records
    nothing and refuses True.

    D-339: `flip_draw_factory(index, activation_day)` gives each funded account its flip draw and `flip` is the
    `FlipSpec` (the slots and the window the router reads); a policy decision whose source is 'flip' then draws the
    account's own bracket that session instead of a routed signal.

    Arguments match `reinvest.simulate_path` where they overlap, with the same meaning. The
    additions:

    Args:
        rules: engine `Rules` (the contract). Pass `rules_from_ledger()` for a research run;
            `Rules()` is stage one's defaults, for validation.
        combine_max_days: trading days after which an unresolved Combine ends without a pass,
            as the engine's `max_days`; it then frees nothing and buys nothing.
        funded_horizon_days: trading days after which a funded account is closed out, as the
            attempt pool's fixed funded horizon. Inherited from the stage-level model so the
            two agree; a later slice may let a funded account live to the campaign horizon.
        combine_draw_factory / funded_draw_factory: `factory(index, start_day) -> draw`; None
            uses independent binary draws at `edge` (`binary_draw_factories`).
        day_hook: called before any account trades on a day with the live accounts in
            rotation order (earliest start first, funded before Combine on a tie, then index);
            `shared_days.SharedDayDraws.day_hook` under `rotation` mode. None otherwise.
        record_trades: keep the per-trade ledger on the result (`LockstepPath.trades`).
        conduct: D-145's tiers 2 and 3 (`ConductModel`); None runs neither, exactly as before.
        record_days: D-146's daily recorder (`LockstepPath.account_days`, `campaign_days`).
            Reads state only; the path is identical with it on or off.
        near_miss_frac: the recorder's near-miss threshold, a declared value: a session that
            closes with less than this share of the MLL left above the floor, without breaching,
            is an MLL near-miss; a daily-loss-limited session that loses more than (1 - this)
            of the limit without reaching it is a daily-loss near-miss.
        reset_failed_combines: D-146: a Combine that hits the loss limit is reset for
            `reset_fee` (the verified `reset_fee` on `rules` if None) and trades again from the
            next session, keeping its subscription; when the bankroll cannot pay the fee it ends
            as a failure. Off by default: a failure is replaced by a new purchase (D-34).
        risk_policy: D-147: a `propedge.campaign.risk_policy.RiskPolicy`. At the start of every
            account's session the policy reads the account's state (phase, balance, cushion to
            the MLL, days in state) and sets the session's dollar risk (and R, where the draw
            can honour it) through the draw's `set_risk`; every ledger row and every recorded
            account-day carries the decision (policy, regime, inputs, risk, R). None keeps each
            leg's fixed risk, exactly as before; `RiskPolicy.from_protocol` reproduces it too.
        max_total_accounts: a cap on live accounts of both kinds together -- running Combines,
            funded accounts and passes waiting for a slot; a Combine is bought only while the
            total is below it (D-34's "at most 5 concurrent accounts including Combines"). With
            the cap at or below the funded cap a pass never waits. None: no joint cap, as before.
        payout_timing: when a funded account requests its payout (8284233,
            `propedge.contract.payout_timing`). The default, `REQUEST_AFTER_5PM`, is the rule for a
            request made after 5:00 PM CT: the next trading day is the Payout request day and does
            not count toward the new cycle. `REQUEST_4_TO_5PM` is the engine's old timing and
            requires the operator to submit between 4:00 and 5:00 PM CT on the eligible day. Either
            way the balance and the MLL change at the request, before the next session, and the
            payout is dated on the eligible day.
        wallet: D-206: a cash pot shared with another campaign, any object with a `cash` attribute. The path
            starts from `wallet.cash` instead of `initial_bankroll`, hands its cash to the wallet just before
            each call of `day_hook` and takes it back just after, and leaves its final cash there; the campaigns
            sharing it must take turns between their hooks (the hook is where they meet). None: the path's own
            cash, exactly as before.
    """
    check_payout_timing(payout_timing)
    _guard()  # Q-119
    lv = LeverState.begin(levers, initial_bankroll=float(initial_bankroll), horizon_days=int(horizon_days),  # Q-119
                           reset_failed_combines=reset_failed_combines, activation_timing=activation_timing)  # Q-119
    combine_cls = CombineAccount if combine_account_cls is None else combine_account_cls  # D-619
    if not (isinstance(combine_cls, type) and issubclass(combine_cls, CombineAccount)):
        raise TypeError(f"combine_account_cls must be CombineAccount or a subclass of it, got {combine_account_cls!r}")
    funded_cls = FundedAccount if funded_account_cls is None else funded_account_cls      # R7
    if not (isinstance(funded_cls, type) and issubclass(funded_cls, FundedAccount)):
        raise TypeError(f"funded_account_cls must be FundedAccount or a subclass of it, got {funded_account_cls!r}")
    household_rule = hasattr(funded_cls, "HOUSEHOLD_CLOSES_AT_LIVE")                       # R7 (multi-firm D-30)
    if household_closure and not household_rule:
        raise ValueError(f"{funded_cls.__qualname__} has no household rule: household_closure=True applies only to a "
                         "funded class that declares one (HOUSEHOLD_CLOSES_AT_LIVE)")
    household_on = household_rule and bool(
        funded_cls.HOUSEHOLD_CLOSES_AT_LIVE if household_closure is None else household_closure)
    budget_k, budget_w = check_purchase_budget(purchase_budget)                              # D-501
    wallet_w = check_wallet_stop(wallet_stop)                                                # D-630 (a)
    pause_f = check_pause_after_funded(pause_after_funded)                                   # D-630 (b)
    ramp_s0 = check_seat_ramp(seat_ramp, max_total_accounts)                                 # D-630 (c)
    ftp = focused_trader                                                                     # D-495 (4)
    if ftp is not None:
        if not isinstance(ftp, FocusedTraderModel):
            raise TypeError(f"focused_trader must be a FocusedTraderModel, got {type(ftp).__name__}")
        if funded_cls is not FundedAccount:
            raise ValueError("the Focused Trader Program is Topstep's (10551016): it applies to Topstep's FundedAccount "
                             f"only, not {funded_cls.__qualname__}")
    if risk_policy is not None:
        risk_policy.validate()
    if activation_timing not in ACTIVATION_TIMINGS:
        raise ValueError(
            f"activation_timing must be one of {ACTIVATION_TIMINGS}, got {activation_timing!r}"
        )
    on_pass = activation_timing == ACTIVATION_ON_PASS
    if combine_draw_factory is None or funded_draw_factory is None:
        default_c, default_f = binary_draw_factories(protocol, edge, seed, rules)
        combine_draw_factory = combine_draw_factory or default_c
        funded_draw_factory = funded_draw_factory or default_f

    combine_policy = protocol.combine_policy()
    funded_policy = protocol.funded_policy()
    cap = rules.std_cap if funded_policy.payout_path == "standard" else rules.cons_cap
    hook_takes_caps = _takes_caps(day_hook)       # D-162: a hook that accepts each account's trade limit
    hook_takes_states = hook_takes_caps and _takes_states(day_hook)   # D-205: and each account's balance and floor
    hook_takes_flips = hook_takes_states and _takes_flips(day_hook)   # D-339: and the day's flips
    hook_takes_rrs = hook_takes_flips and _takes_rrs(day_hook)        # D-349: and each account's R for the session
    hook_takes_seconds = hook_takes_rrs and _takes_seconds(day_hook)  # D-368: and the accounts allowed a second trade
    hook_takes_collect = hook_takes_seconds and _takes_collect(day_hook)   # D-368: and the accounts collecting
    if flip is not None and flip_draw_factory is None:
        raise ValueError("a flip stream needs a flip draw factory (D-339)")
    seat_frees = str((getattr(protocol, "params", None) or {}).get("seat_frees", "next_session"))   # D-339
    if seat_frees not in ("next_session", "same_evening"):
        raise ValueError(f"seat_frees is 'next_session' or 'same_evening', got {seat_frees!r}")
    seat_same_evening = seat_frees == "same_evening"
    flip_rng = np.random.default_rng(child_seed(seed, _KIND_FLIP_DIRECTION, 0)) if flip is not None else None

    cash = float(initial_bankroll) if wallet is None else float(wallet.cash)   # D-206: a shared pot
    peak_cash = cash
    max_dd = 0.0

    running: list[CombineAccount] = []
    funded: list[FundedAccount] = []
    queue: list[CombineAccount] = []
    pending: list[tuple[int, float, FundedAccount]] = []     # (arrival day, amount, account)
    finished_combines: list[CombineAccount] = []
    finished_funded: list[FundedAccount] = []
    finished_trades, n_finished_c, n_finished_f = 0, 0, 0      # R11: the finished accounts' trades, kept as a total
    capped_memo: dict = {}                                     # R11: `_capped`'s protocols, one per (protocol, limit)

    cash_series = np.zeros(horizon_days, dtype=float)
    active_series = np.zeros(horizon_days, dtype=int)
    breaches_per_day = np.zeros(horizon_days, dtype=int)
    trades_by_day = np.zeros(horizon_days, dtype=int)     # D-305: executed trades across every account, per day
    trades_so_far = 0
    # D-306: the protocol declares need-aware Combine exits in its params; a draw that cannot honour them is unchanged
    need_aware = bool((getattr(protocol, "params", None) or {}).get("need_aware_exits", False))
    # D-313: and the Combine's consistency-capped exits (a day never lifts the target when the pass cannot be taken)
    consistency_cap = bool((getattr(protocol, "params", None) or {}).get("consistency_cap_exits", False))
    # D-324: a policy's no-trade states hold only Standard-path funded accounts (`_capped` below)
    standard_waits_only = bool((getattr(protocol, "params", None) or {}).get("no_trade_standard_path_only", False))
    # D-328: the policy's dollar inputs read to the cent, as the firm's ledger carries them
    decision_cents = bool((getattr(protocol, "params", None) or {}).get("decision_inputs_cents", False))
    # D-368: an XFA collecting Standard-path winning days may take a second trade after a first that left the day short
    xfa_second = bool((getattr(protocol, "params", None) or {}).get("xfa_second_trade", False))
    # D-368: the collect phase -- an XFA collecting Standard-path winning days whose balance has reached this many dollars
    # above its start trades at the fresh funded leg's dollar risk with a take-profit at the shortfall to the minimum
    collect_from = (getattr(protocol, "params", None) or {}).get("xfa_collect_from")
    collect_from = None if collect_from is None else float(collect_from)
    if collect_from is not None and xfa_second:
        raise ValueError("xfa_collect_from and xfa_second_trade together are not defined (D-368): test them apart")

    ruined = False
    ruin_day: int | None = None
    attempts_started = 0
    accounts_funded = 0
    accounts_ever_paid = 0
    total_fees = 0.0
    total_payouts = 0.0
    peak_queue = 0
    passes_forfeited = 0
    combines_abandoned = 0
    combines_out_of_room = 0                      # D-318
    combines_abandoned_by_policy = 0              # D-329: attempts the policy cancelled
    funded_abandoned = 0                          # D-329: XFAs the policy closed
    passes_on_hold_at_end = 0
    multi_breach_days = 0
    max_breached = 0
    payout_days_campaign: list[int] = []
    ledger: list[dict[str, Any]] | None = [] if record_trades else None

    # D-145 state. Nothing below reads it when `conduct` is None.
    rtp_day: int | None = None                 # the day RTP placement took effect from the next day
    rtp_trigger = ""
    rtp_warning_days: list[int] = []           # trigger days answered by a warning (D-220)
    enforce_rng = (np.random.default_rng(child_seed(seed, _KIND_ENFORCEMENT, 0))
                   if conduct is not None else None)
    payouts_requested = payouts_exposed = payouts_denied = 0
    purchase_days: list[int] = []
    rtp_policy = None
    if conduct is not None and conduct.rtp:
        from dataclasses import replace as _replace
        rtp_policy = _replace(funded_policy, payout_path="consistency")

    def _rtp_dll_on(d: int) -> float | None:
        # The RTP daily loss limit for an account bought, reset or activated on calendar day `d`: placement decided
        # at a day's close applies from the next day (13620045: "All new Trading Combines® and XFAs automatically
        # get a Daily Loss Limit (DLL)"; "If Reset, the new Trading Combine will follow RTP rules").
        if conduct is not None and rtp_day is not None and d > rtp_day:
            return float(conduct.rtp_dll)
        return None

    # D-146 state. The fee arrays are cheap and always kept; rows are built only when recording.
    fee_sub = np.zeros(horizon_days)
    fee_act = np.zeros(horizon_days)
    fee_reset = np.zeros(horizon_days)
    pay_in = np.zeros(horizon_days)
    account_days: list[dict[str, Any]] = []
    the_reset_fee = float(getattr(rules, "reset_fee", 0.0) if reset_fee is None else reset_fee)
    resets_taken = 0
    # R7 (multi-firm D-30): the household rule's state; read only when the funded class has the rule.
    household_closed_on: int | None = None
    household_triggers = household_combines = household_funded = household_passes = 0
    # D-495 (4): the Focused Trader Program's state; nothing below reads it when `focused_trader` is None.
    ftp_bought = np.zeros(horizon_days, dtype=int)        # Combine purchases and resets, per day
    ftp_lost = np.zeros(horizon_days, dtype=int)          # funded accounts lost (breach, closure at request, denial)
    ftp_placed: dict[str, Any] | None = None              # the placement in force
    ftp_until: int | None = None                          # Corrective: the last day of its limit
    ftp_watch_from = 0                                    # the measures count from this day (after a program ended)
    ftp_done = False                                      # a program ended and `repeat` is off: nothing more watched
    ftp_placements: list[dict[str, Any]] = []
    ftp_blocked_days = ftp_resets_refused = 0
    # D-501: the purchase budget's state; nothing below reads it when `purchase_budget` is None.
    budget_on = purchase_budget is not None
    budget_bought = np.zeros(horizon_days, dtype=int)     # Combine purchases and resets, per day
    budget_blocked_days = budget_resets_refused = 0

    def _budget_spent(d: int) -> bool:
        # D-501: the purchases and resets in the last `budget_w` trading days (day d included) have reached K
        return budget_on and int(budget_bought[max(0, d - budget_w + 1):d + 1].sum()) >= budget_k

    # D-630: the three entry options' state; nothing below reads it when all three are None.
    entry_on = wallet_w is not None or pause_f is not None or ramp_s0 is not None
    start_bankroll = float(initial_bankroll)              # (a): the cash out of pocket is this less the cash
    wallet_blocked_days = wallet_resets_refused = 0
    wallet_first_blocked = wallet_final = -1
    wallet_max_out = 0.0                                  # the most out of pocket just before a purchase or reset taken
    pause_first = -1                                      # (b): the first day the pause refused a purchase or a reset
    pause_in_force = pause_now = False                    # its condition at the last purchase step; at today's resets
    pause_blocked_days = pause_resets_refused = 0
    pause_days = pause_spells = 0                         # purchase steps at which the condition held; their spells
    pause_resumed: list[int] = []                         # days it stopped holding because fewer than F were held
    ramp_base = int(max_total_accounts) if ramp_s0 is not None else 0
    ramp_blocked_days = 0
    ramp_first_blocked = -1
    ramp_full_on = (0 if ramp_s0 >= ramp_base else -1) if ramp_s0 is not None else -1

    def _entry_refusals(cash_now: float, held: int, paused: bool, arrived: int) -> tuple[bool, bool, bool]:
        # D-630: which options refuse a purchase now -- (a) the cash out of pocket above W, (b) the pause's condition,
        # (c) the accounts held at the ramp's seats (s0 and one more for each payout arrived)
        return (wallet_w is not None and start_bankroll - cash_now > wallet_w,
                paused,
                ramp_s0 is not None and held >= ramp_s0 + arrived)

    if cash < subscription:
        cash_series[:] = cash
        return LockstepPath(
            path=CampaignPath(
                final_cash=cash, initial_bankroll=float(initial_bankroll),
                cash_series=cash_series, active_funded_series=active_series,
                ruined=True, ruin_day=0, max_drawdown=0.0, max_drawdown_frac=0.0,
                attempts_started=0, accounts_funded=0, accounts_ever_paid=0,
                days_to_first_payout=None, payout_gaps=(), total_fees=0.0,
                total_payouts=0.0, peak_queue_length=0,
            ),
            combines=(), funded=(), breaches_per_day=breaches_per_day,
        )

    for day in range(horizon_days):
        # D-495 (4): a Corrective placement's limit ends after its trading days; the program ends and, with `repeat`,
        # the measures are watched again from today. A placement made at a close binds from the next day.
        if ftp_placed is not None and ftp_until is not None and day > ftp_until:
            ftp_placed["ended_on"] = int(ftp_until)
            ftp_placed, ftp_until, ftp_watch_from = None, None, day
            ftp_done = not ftp.repeat
        ftp_in_force = ftp_placed is not None
        ftp_no_resets = ftp_in_force and ftp_placed["path"] == FTP_SLOWDOWN
        # 1. subscriptions due at the start of the day. Engine day 0 is the day after purchase,
        #    so the k-th rebill (engine day k * billing_days) falls on purchase + 1 + k * billing_days.
        keep: list[CombineAccount] = []
        for c in running:
            elapsed = day - c.purchase_day
            due = 1 + max(0, (elapsed - 1) // billing_days)
            alive = True
            while c.subs_paid < due:
                if cash < subscription:
                    alive = False
                    combines_abandoned += 1
                    break
                if lv is not None and lv.withholds_rebill(cash, subscription, day):  # Q-119
                    alive = False  # Q-119
                    break  # Q-119
                cash -= subscription
                total_fees += subscription
                fee_sub[day] += subscription
                c.subs_paid += 1
                if lv is not None:  # Q-119
                    lv.fee_paid(cash, day)  # Q-119
            if alive:
                keep.append(c)
            else:
                c.abandoned = True
                c.resolved_on = day
                finished_combines.append(c)
        running = keep

        # 2. every live account trades today's session and locks at 16:00 CT. A draw that
        #    sizes from the tier reads the balance at the start of the session (D-53; the tier
        #    is fixed within a session) through `begin_session`; other draws have no such hook.
        #    Under rotation the router is told, first, which accounts are live today and in
        #    what order (earliest start first, funded before Combine on a tie, then index).
        trading_c = [c for c in running if day >= c.start_day and c.alive]
        trading_f = [a for a in funded if day >= a.start_day and a.alive and a.ended_on is None]

        def _decide(acct: Any, kind: str) -> None:
            # D-147: the policy reads the account's state at the start of the session.
            if risk_policy is None:
                return
            from propedge.campaign.risk_policy import account_state

            dec = risk_policy.decide(account_state(acct, kind=kind, day=day, cents=decision_cents))
            if getattr(dec, "abandon", False):                    # D-329: nothing to size; the account ends below
                acct.decision = dec
                return
            if getattr(dec, "source", "strategy") == "flip":      # D-339: the account's own bracket today, no signal
                if kind != "funded" or getattr(acct, "flip_draw", None) is None:
                    raise ValueError("a flip decision needs a funded account with a flip draw (D-339)")
                acct.flip_today = True
                acct.flip_draw.set_risk(dec.risk, dec.rr)
                acct.decision = dec
                return
            setr = getattr(acct.draw, "set_risk", None)
            if setr is None:
                raise ValueError(
                    f"a risk policy needs a draw that can change its risk; {type(acct.draw).__name__} "
                    "cannot (use the binary draws or SharedDayDraws)"
                )
            setr(dec.risk, dec.rr)
            acct.decision = dec

        def _stamp(acct: Any, n0: int) -> None:
            if ledger is not None and acct.decision is not None:
                row = acct.decision.as_row()
                for r in ledger[n0:]:
                    r.update(row)

        def _capped(pol: Any, acct: Any) -> Any:
            # D-162: the session's trade slots, limited by the state's `max_trades` when the policy sets one.
            dec = acct.decision if risk_policy is not None else None
            if dec is None or dec.max_trades is None or int(dec.max_trades) >= int(pol.trades_per_day):
                return pol
            waits = not (standard_waits_only and getattr(acct, "policy_override", None) is not None)
            mt = session_slots(int(pol.trades_per_day), dec.max_trades, waits=waits)
            if mt >= int(pol.trades_per_day):
                return pol
            hit = capped_memo.get((id(pol), mt))           # R11: the same frozen protocol, built once per path
            if hit is not None and hit[0] is pol:
                return hit[1]
            from dataclasses import replace as _rep
            out = _rep(pol, trades_per_day=mt)
            capped_memo[(id(pol), mt)] = (pol, out)        # the key's protocol held, so its id cannot be reused
            return out

        # D-162: every account's session decision comes first, so the day hook (rotation's router) can be told each
        # account's trade limit before it routes; the decision reads the state at the start of the session either way.
        for c in trading_c:
            _decide(c, "combine")
        for a in trading_f:
            a.flip_today = False                              # D-339: a flip session is the day's decision, never carried
            _decide(a, "funded")
        # D-339 / D-343: the day's shared direction (one seeded draw a day) and each flip's slot, set on the flip draw
        # for its ledger row whether or not a router reads them
        flip_direction, flip_slots = 0, {}
        if flip is not None and any(a.flip_today for a in trading_f):
            flip_direction = 1 if float(flip_rng.random()) < 0.5 else -1
            for a in trading_f:
                if a.flip_today:
                    flip_slots[a.index] = flip.slot_for(day, a.index, max_concurrent_accounts)
                    a.flip_draw.today = (int(flip_slots[a.index]), int(flip_direction))
        # D-318: a room-capped Combine whose room buys no trade at its state's R is out of room -- it ends here, before
        # the router sees it, and its slot frees like any failed attempt's; a draw without the room cap never is.
        for c in trading_c:
            oor = getattr(c.draw, "out_of_room", None)
            if oor is not None and oor(c.B, c.F):
                c.finish_out_of_room(day - c.start_day, day)
                combines_out_of_room += 1
        # D-329: the policy's abandon read at the session's start -- the account ends before the router sees it and its
        # slot frees: a Combine cancelled, an XFA closed at the trader's request, nothing credited. Since D-334 the
        # abandon is taken at the previous close (below), which reads the same state, so this fires only for a state
        # that close could not read.
        for c in trading_c:
            if c.alive and c.decision is not None and getattr(c.decision, "abandon", False):
                c.finish_abandoned(day)
                combines_abandoned_by_policy += 1
        for a in trading_f:
            if a.alive and a.decision is not None and getattr(a.decision, "abandon", False):
                a.close_abandoned(day)
                funded_abandoned += 1
        trading_c = [c for c in trading_c if c.alive]
        trading_f = [a for a in trading_f if a.alive]
        # D-368: the XFAs that may take a second trade today -- a strategy session of one trade, collecting the Standard
        # path's winning days, not the Payout request day, no daily loss limit -- with the risk and R of their first
        # and the minimum, for the router
        second_keys: dict[tuple[str, int], tuple[float, float, float]] = {}
        if xfa_second:
            if not hook_takes_seconds:
                raise ValueError("xfa_second_trade needs the rotation router's day hook (D-368): only it hands a second "
                                 "signal after a first that fell short")
            for a in trading_f:
                dec = a.decision
                leg = a.policy_override or funded_policy
                if (not a.flip_today and dec is not None and getattr(dec, "source", "strategy") == "strategy"
                        and dec.max_trades is not None and int(dec.max_trades) == 1
                        and leg.payout_path == "standard" and a.win_days < int(rules.std_winning_days)
                        and not a.request_day_next and a.dll is None):
                    rr1 = float(dec.rr) if getattr(dec, "rr", None) is not None else float(leg.rr)
                    second_keys[("funded", a.index)] = (float(dec.risk), rr1, float(rules.std_winning_day_min))
        # D-368: the XFAs in the collect phase today -- a strategy session the table trades, collecting the Standard
        # path's winning days, not the Payout request day, no daily loss limit, the balance at or above `collect_from`
        # -- each sized at the fresh funded leg's dollar risk (the table's own fresh decision, D-329), its R unchanged
        collect_keys: dict[tuple[str, int], float] = {}
        by_table = [a for a in trading_f if not a.flip_today and a.decision is not None
                    and getattr(a.decision, "source", "strategy") == "collect"
                    and (a.decision.max_trades is None or int(a.decision.max_trades) >= 1)]
        if collect_from is not None or by_table:
            if not hook_takes_collect:
                raise ValueError("a collect phase or a collect decision needs the rotation router's day hook (D-368, "
                                 "D-379): only it asks an account whether it would bracket a signal at the need")
            for a in by_table:
                # D-379: the table's own collect decision -- the leaf's risk (set by `_decide`), the take-profit at the
                # shortfall to the winning-day minimum
                collect_keys[("funded", a.index)] = float(rules.std_winning_day_min)
            for a in (trading_f if collect_from is not None else []):
                dec = a.decision
                leg = a.policy_override or funded_policy
                if (not a.flip_today and dec is not None and getattr(dec, "source", "strategy") == "strategy"
                        and (dec.max_trades is None or int(dec.max_trades) >= 1)
                        and leg.payout_path == "standard" and a.win_days < int(rules.std_winning_days)
                        and not a.request_day_next and a.dll is None and a.B >= collect_from - EPS):
                    a.draw.set_risk(float(protocol.funded_risk), dec.rr)
                    collect_keys[("funded", a.index)] = float(rules.std_winning_day_min)
        if day_hook is not None:
            order = sorted(
                [(a.start_day, 0, a.index, ("funded", a.index)) for a in trading_f]
                + [(c.start_day, 1, c.index, ("combine", c.index)) for c in trading_c]
            )
            keys = [k for _, _, _, k in order]
            owner = getattr(day_hook, "__self__", None)
            if getattr(owner, "wants_progress", False):   # D-568 R5: each account's progress toward its goal, unit-free
                owner.progress = {("combine", c.index): max(0.0, float(c.B)) / float(rules.profit_target)
                                  for c in trading_c}
                owner.progress.update({("funded", a.index): float(a.win_days) / float(rules.std_winning_days)
                                       for a in trading_f})
            if wallet is not None:                      # D-206: the pot holds the cash while the other campaign moves
                wallet.cash = cash
            if hook_takes_caps:
                caps = {("combine", c.index): int(_capped(combine_policy, c).trades_per_day) for c in trading_c}
                # D-339: a flip-state account takes no routed signal today (its bracket is its own)
                caps.update({("funded", a.index): (0 if a.flip_today else
                                                   int(_capped(a.policy_override or funded_policy, a).trades_per_day))
                             for a in trading_f})
                caps.update({k: 2 for k in second_keys})                  # D-368: a second only after a first short
                if hook_takes_states:
                    states = {("combine", c.index): (float(c.B), float(c.F)) for c in trading_c}
                    states.update({("funded", a.index): (float(a.B), float(a.F)) for a in trading_f})
                    if hook_takes_flips and (flip is not None or hook_takes_rrs):
                        # D-339: each flip's slot, window and the day's direction, so the router places the flips
                        # among the log's trades for the cross-account rule
                        # D-384: the window of the account's own bracket (a menu's pick), the stream's otherwise
                        flips = ([(("funded", a.index), float(flip_slots[a.index]),
                                   float(flip_slots[a.index] + getattr(a.flip_draw, "spec", flip).window_minutes(
                                       flip_slots[a.index])), flip_direction)
                                  for a in trading_f if a.flip_today] if flip is not None else [])
                        if hook_takes_rrs:
                            # D-349: each account's R for the session -- the table's decision, else the leg's -- so the
                            # router holds a routed position to its exit at that R (the rule's and flat routing's clock)
                            def _rr_of(acct: Any, leg: Any) -> float:
                                dec = acct.decision
                                return float(dec.rr) if (dec is not None and getattr(dec, "rr", None) is not None) else float(leg.rr)
                            rrs = {("combine", c.index): _rr_of(c, combine_policy) for c in trading_c}
                            rrs.update({("funded", a.index): _rr_of(a, a.policy_override or funded_policy) for a in trading_f})
                            if collect_from is not None or collect_keys:   # D-368, D-379: the accounts collecting
                                day_hook(day, keys, caps, states, flips, rrs, second_keys, collect_keys)
                            elif xfa_second:                      # D-368: the accounts allowed a second trade
                                day_hook(day, keys, caps, states, flips, rrs, second_keys)
                            else:
                                day_hook(day, keys, caps, states, flips, rrs)
                        else:
                            day_hook(day, keys, caps, states, flips)
                    else:
                        day_hook(day, keys, caps, states)
                else:
                    day_hook(day, keys, caps)
            else:
                day_hook(day, keys)
            if wallet is not None:
                cash = float(wallet.cash)

        for c in trading_c:
            begin = getattr(c.draw, "begin_session", None)
            if begin is not None:
                begin(balance=c.B, floor=c.F)
            n0 = len(ledger) if ledger is not None else 0
            c.trade_day(rules, _capped(combine_policy, c), day - c.start_day, day, ledger=ledger,
                        need_aware=need_aware, consistency_cap=consistency_cap)
            _stamp(c, n0)
            if c.alive and c.days >= combine_max_days:
                c.unresolved = True
                c.resolved_on = day
        requested_today: list[tuple[int, float, FundedAccount]] = []
        for a in trading_f:
            begin = getattr(a.draw, "begin_session", None)
            if begin is not None:
                begin(balance=a.B, floor=a.F)
            pol = _capped(a.policy_override if a.policy_override is not None else funded_policy, a)
            a_cap = cap if a.policy_override is None else (
                rules.std_cap if pol.payout_path == "standard" else rules.cons_cap)
            second_ok = ("funded", a.index) in second_keys                 # D-368
            if second_ok and int(pol.trades_per_day) < 2:
                from dataclasses import replace as _rep2
                pol = _rep2(pol, trades_per_day=2)
            n0 = len(ledger) if ledger is not None else 0
            net = a.trade_day(rules, pol, a_cap, day - a.start_day, day, ledger=ledger, second_trade=second_ok,
                              collect=("funded", a.index) in collect_keys)
            _stamp(a, n0)
            if net is not None:
                entry = (day + int(payout_lag_days), net, a)
                pending.append(entry)
                requested_today.append(entry)
        if record_days:
            mll = float(rules.mll)
            for c in trading_c:
                room = float(c.B - c.F)
                row = {
                    "day": day, "kind": "combine", "index": c.index,
                    "state": ("failed" if c.failed else "passed" if c.passed else "unresolved" if c.unresolved else "combine"),
                    "balance": float(c.B), "floor": float(c.F), "room": room, "day_pnl": float(c.last_day_pnl),
                    "near_mll": bool(not c.failed and room < near_miss_frac * mll),
                    "near_dll": bool(c.dll is not None and not c.failed
                                     and -c.dll + EPS < c.last_day_pnl <= -(1.0 - near_miss_frac) * c.dll),
                    "consistency_binding": bool(not c.failed and c.last_target > rules.profit_target + EPS),
                    "target": float(c.last_target), "eligible": None, "requested": 0.0,
                    "attempt": c.resets,
                    "regime": c.decision.regime if c.decision is not None else None,
                    "policy_risk": c.decision.risk if c.decision is not None else None,
                }
                account_days.append(row)
            for a in trading_f:
                room = float(a.B - a.F)
                req = next((float(a.last_request) for e in requested_today if e[2] is a), 0.0)
                row = {
                    "day": day, "kind": "funded", "index": a.index,
                    "state": ("closed" if a.closed else "paid" if a.n_payouts > 0 else "funded"),
                    "balance": float(a.B), "floor": float(a.F), "room": room, "day_pnl": float(a.last_day_pnl),
                    "near_mll": bool(not a.closed and room < near_miss_frac * mll),
                    "near_dll": bool(a.dll is not None and not a.closed
                                     and -a.dll + EPS < a.last_day_pnl <= -(1.0 - near_miss_frac) * a.dll),
                    "consistency_binding": bool(a.last_cons_blocked),
                    "target": None, "eligible": bool(a.last_eligible), "requested": req,
                    "attempt": 0,
                    "regime": a.decision.regime if a.decision is not None else None,
                    "policy_risk": a.decision.risk if a.decision is not None else None,
                }
                account_days.append(row)
        # D-334: the policy's abandon is taken at the close whose state decides it. The inputs the policy reads are the
        # close's (the balance and floor lock at 16:00 CT; the payout conditions settle there), so the next session's
        # decision is known now: the account is read as that session will find it (`day + 1` for the day-keyed
        # inputs) and, if the decision is abandon, ends at this close -- a Combine cancelled this evening, its
        # replacement bought below and trading tomorrow, as after a breach; an XFA closed at the trader's request, its
        # slot freed tomorrow, as after any closure. An abandon then costs the slot what a breach costs, which is what
        # the table prices (the audit of D-333, finding 3: read at the next session's start, the abandon idled the slot
        # one session more than a breach, 5-6 % of the slot-days available).
        if day + 1 < horizon_days:
            if risk_policy is not None:
                from propedge.campaign.risk_policy import account_state

                for c in trading_c:
                    if not c.alive:
                        continue
                    dec = risk_policy.decide(account_state(c, kind="combine", day=day + 1, cents=decision_cents))
                    if getattr(dec, "abandon", False):
                        c.finish_abandoned(day)
                        combines_abandoned_by_policy += 1
                    else:
                        # D-335: the next session's risk and R on the draw now, so the room below is read at them -- the
                        # same call `_decide` makes at that session's start, which repeats it unchanged
                        setr = getattr(c.draw, "set_risk", None)
                        if setr is not None:
                            setr(dec.risk, dec.rr)
                for a in trading_f:
                    if a.alive and a.ended_on is None and getattr(
                            risk_policy.decide(account_state(a, kind="funded", day=day + 1, cents=decision_cents)), "abandon", False):
                        a.close_abandoned(day)
                        funded_abandoned += 1
            # D-335 (the audit of D-334, finding 9): a room-capped Combine whose room buys no trade at its next session's R
            # is out of room at this close and ends now (D-318: a failed attempt, not a breach), its replacement bought
            # below -- the same timing as the abandon above, which is read first, so a state the policy abandons is
            # counted as abandoned as before and no policy campaign's row can change; without a policy (the fixed-legs
            # twin) this is the only way such an attempt ends. The start-of-session check above remains for a state this
            # close could not read.
            for c in trading_c:
                oor = getattr(c.draw, "out_of_room", None)
                if c.alive and oor is not None and oor(c.B, c.F):
                    c.finish_out_of_room(day - c.start_day, day)
                    combines_out_of_room += 1
        # Accounts that hit the loss limit today, Combine or funded. Two or more on one day is
        # the Responsible Trading Program's first trigger (D-30); only a loop that steps
        # accounts through the same day can count it.
        breached_today = sum(1 for c in running if c.failed and not c.out_of_room and c.resolved_on == day) + sum(
            1 for a in funded if a.closed and not a.abandoned and a.ended_on == day      # D-329: a closure, no breach
        )
        breaches_per_day[day] = breached_today
        if breached_today >= 2:
            multi_breach_days += 1
        max_breached = max(max_breached, breached_today)

        if conduct is not None:
            # Tier 3 (D-145): a payout requested while the campaign shows the stacking pattern is
            # exposed; an exposed payout is denied, and its account closed, with the stated
            # probability. One draw per exposed payout, whatever the probability.
            lo = max(0, day - conduct.pattern_window_days + 1)
            exposed = int(breaches_per_day[lo:day + 1].sum()) >= conduct.pattern_breaches
            for entry in requested_today:
                payouts_requested += 1
                if not exposed:
                    continue
                payouts_exposed += 1
                if float(enforce_rng.random()) < conduct.enforcement_p:
                    payouts_denied += 1
                    pending.remove(entry)
                    entry[2].deny_last_payout(day)
            # Tier 2 (D-145): Responsible Trading Program placement, effective from tomorrow; the
            # first `rtp_warnings` trigger days bring a warning instead (D-220).
            if conduct.rtp and rtp_day is None:
                traded = trading_c + trading_f
                fired = ""
                if breached_today >= 2:
                    fired = "multiple accounts hit the MLL in one day"
                elif any(_losers_not_smaller(x.pnls, conduct.losers_window, conduct.min_trades)
                         for x in traded):
                    fired = "losers not smaller than winners"
                elif any(len(x.pnls) >= conduct.min_trades
                         and x.at_max > conduct.max_position_share * len(x.pnls) for x in traded):
                    fired = "maximum position on most trades"
                if fired and len(rtp_warning_days) < conduct.rtp_warnings:
                    rtp_warning_days.append(day)
                elif fired:
                    rtp_trigger, rtp_day = fired, day

        # R7 (multi-firm D-30; docs/TWO_FIRMS.md): the household rule, read once the day's payouts are requested (and any
        # denied). An account that raised it at this close is counted (Lucid: its fifth payout -- the household enters
        # the live review pool, and a live move or the cash-out closes every simulated account, 16558826); with the rule
        # on, the first one ends every other live account here and the path buys nothing more.
        if household_rule:
            raised = [a for a in funded if a.ended_on == day and getattr(a, "closes_household", False)]
            household_triggers += len(raised)
            if raised and household_on and household_closed_on is None:
                household_closed_on = day
                for c in running:
                    if c.alive:
                        c.close_household(day)
                        household_combines += 1
                for a in funded:
                    if a.ended_on is None and a.alive:
                        a.close_household(day)
                        household_funded += 1
                for c in queue:
                    c.household_closed = True
                household_passes += len(queue)
                queue.clear()

        # D-495 (4): the funded accounts lost today -- ended by a breach, a closure at request or a tier-3 denial's
        # closure -- counted while they are still in `funded` (step 5 moves them).
        if ftp is not None:
            ftp_lost[day] = sum(1 for a in funded if a.closed and a.ended_on == day)

        # 3. payouts arriving today, in the order they were requested.
        still_pending: list[tuple[int, float, FundedAccount]] = []
        for arrival, amount, acc in pending:
            if arrival <= day:
                cash += amount
                total_payouts += amount
                pay_in[day] += amount
                payout_days_campaign.append(day)
                if not acc.ever_credited:
                    acc.ever_credited = True
                    accounts_ever_paid += 1
            else:
                still_pending.append((arrival, amount, acc))
        pending = still_pending
        if lv is not None:  # Q-119
            lv.after_arrivals(day, cash)  # Q-119
        if entry_on:
            # D-630 (b), D-632: the pause's condition as today's resets find it -- F funded accounts held (before this
            # evening's activations) and no payout arrived (the arrivals are just above)
            pause_now = (pause_f is not None and not payout_days_campaign
                         and sum(1 for a in funded if a.ended_on is None) >= pause_f)
            # D-630 (c): the day the ramp reached the base's seats
            if ramp_s0 is not None and ramp_full_on < 0 and ramp_s0 + len(payout_days_campaign) >= ramp_base:
                ramp_full_on = day

        # 4. Combines that resolved today: a pass joins the hold queue; anything else ends.
        still: list[CombineAccount] = []
        for c in running:
            if c.resolved_on is None:
                still.append(c)
                continue
            # D-146: a failure answered with a reset. The breach was counted above; the account
            # keeps its subscription and trades again tomorrow from its starting balance.
            if (reset_failed_combines and c.failed and c.resolved_on == day
                    and cash >= the_reset_fee and ftp_no_resets):
                ftp_resets_refused += 1                       # D-495 (4): "You cannot purchase new ... Resets"
            elif (reset_failed_combines and c.failed and c.resolved_on == day
                    and cash >= the_reset_fee and _budget_spent(day)):
                budget_resets_refused += 1                    # D-501: the budget refuses the reset; the Combine fails
            elif (reset_failed_combines and c.failed and c.resolved_on == day
                    and cash >= the_reset_fee and wallet_w is not None and start_bankroll - cash > wallet_w):
                wallet_resets_refused += 1                    # D-630 (a): as the budget's refusal; the Combine fails
            elif (reset_failed_combines and c.failed and c.resolved_on == day
                    and cash >= the_reset_fee and pause_now):
                pause_resets_refused += 1                     # D-630 (b): as the budget's refusal; the Combine fails
                pause_first = day if pause_first < 0 else pause_first
            elif (reset_failed_combines and c.failed and c.resolved_on == day
                    and cash >= the_reset_fee):
                if ftp is not None:
                    ftp_bought[day] += 1                      # D-495 (4): a reset counts with the purchases
                if budget_on:
                    budget_bought[day] += 1                   # D-501: a reset counts with the purchases
                if wallet_w is not None:
                    wallet_max_out = max(wallet_max_out, start_bankroll - cash)   # D-630 (a)
                cash -= the_reset_fee
                total_fees += the_reset_fee
                fee_reset[day] += the_reset_fee
                resets_taken += 1
                c.reset(day, rtp_dll=_rtp_dll_on(day))
                still.append(c)
                continue
            finished_combines.append(c)
            if c.passed:
                if household_closed_on is not None:          # R7: the household rule closed it with its pass
                    c.household_closed = True
                    household_passes += 1
                    continue
                if on_pass:
                    if cash < activation:
                        passes_forfeited += 1
                        continue
                    cash -= activation
                    total_fees += activation
                    fee_act[day] += activation
                queue.append(c)
        running = still

        # 5. funded accounts that finished free their seat: the day after they ended (the stage-level loop's
        #    convention, which the lockstep reproduces exactly by default -- the validation limit), or at that close
        #    under `Protocol.params["seat_frees"] == "same_evening"` (D-339; the help centre, re-read 2026-10-10 under
        #    D-336: activation is "minutes after paying the Activation Fee" and a breached XFA is "closed at the end of
        #    the day", so a waiting pass activates the same evening and trades the next session; the default idles the
        #    seat one session per funded ending, pessimistic by up to a session) ...
        if lv is not None and lv.reactivating:  # Q-119
            cash, total_fees, accounts_funded, funded = lv.reactivate(  # Q-119
                day, cash, total_fees, accounts_funded, funded, finished_funded, funded_cls, funded_draw_factory,  # Q-119
                flip_draw_factory, rules, funded_horizon_days, payout_timing, ftp_placed,  # Q-119
                ftp_bought if ftp is not None else None, max_concurrent_accounts)  # Q-119
        ended = (lambda a: a.ended_on is not None and (a.ended_on <= day if seat_same_evening else a.ended_on < day))
        ending = [a for a in funded if ended(a)]
        finished_funded.extend(ending)
        funded = [a for a in funded if not ended(a)]
        # ... and the hold queue fills any free slot, paying the activation fee then (D-21).
        if lv is not None and lv.expiring:  # Q-119
            lv.expire(day, queue)  # Q-119
        while queue and len(funded) < max_concurrent_accounts:
            c = queue[0]
            if not on_pass:
                if cash < activation:
                    if lv is not None:  # Q-119
                        lv.count("activations_refused_cash")  # Q-119
                    break
                if lv is not None and lv.withholds_activation(cash, activation, c):  # Q-119
                    break  # Q-119
                cash -= activation
                total_fees += activation
                fee_act[day] += activation
            queue.pop(0)
            if lv is not None:  # Q-119
                lv.activated(c, day, cash)  # Q-119
            j = accounts_funded
            # RTP (13620045): the path is decided by the Combine, not the activation day. A Combine bought (or reset)
            # under RTP is a Consistency Trading Combine and its pass is activated on the Consistency path; "Any
            # Standard Trading Combine subscription started before RTP placement will remain as a Standard Trading
            # Combine. If passed, it may be activated as either a Standard XFA or Consistency XFA" -- the protocol's
            # path. Either way an XFA activated after placement carries the daily loss limit ("XFAs activated from
            # Trading Combines purchased before your RTP placement can be Standard or Consistency with a Daily Loss
            # Limit").
            funded.append(
                funded_cls(
                    index=j, activation_day=day, draw=funded_draw_factory(j, day),
                    horizon_days=int(funded_horizon_days), floor_start=rules.xfa_mll_start,
                    policy_override=rtp_policy if (rtp_policy is not None and c.rtp) else None,
                    dll=_rtp_dll_on(day), combine_index=c.index, combine_purchase_day=c.purchase_day,
                    payout_timing=payout_timing,
                    flip_draw=flip_draw_factory(j, day) if flip_draw_factory is not None else None,   # D-339
                )
            )
            accounts_funded += 1
        peak_queue = max(peak_queue, len(queue))

        # 6. new Combines. With reinvestment off, only the initial bankroll is ever spent.
        spendable = cash if reinvest else min(cash, float(initial_bankroll) - total_fees)
        blocked_by_queue = stop_buying_when_queued and bool(queue)
        # D-630 (b), D-632: the pause's condition, read again at every purchase step -- the campaign holds at least F
        # funded accounts (activated, this evening's included, and not ended) and its first payout has not arrived.
        # No latch: with fewer than F held the purchases below are the base's.
        if pause_f is not None:
            held_before = pause_in_force
            pause_in_force = (not payout_days_campaign
                              and sum(1 for a in funded if a.ended_on is None) >= pause_f)
            if pause_in_force:
                pause_days += 1
                pause_spells += 0 if held_before else 1
            elif held_before and not payout_days_campaign:
                pause_resumed.append(day)                     # fewer than F held again, no payout yet
        if ftp_in_force and (                                 # D-495 (4): a purchase the program alone refuses today
            not blocked_by_queue
            and len(running) < max_concurrent_combines
            and (max_total_accounts is None or len(running) + len(funded) + len(queue) < max_total_accounts)
            and spendable >= subscription
            and (max_attempts is None or attempts_started < max_attempts)
            and household_closed_on is None
            and len(running) + len(funded) + len(queue) >= ftp.account_limit
            and not (lv is not None and lv.withholds_purchase(cash, subscription))  # Q-119
            and not (entry_on and any(_entry_refusals(       # D-630: nor an entry option
                cash, len(running) + len(funded) + len(queue), pause_in_force, len(payout_days_campaign))))
        ):
            ftp_blocked_days += 1
        while (
            not blocked_by_queue
            and len(running) < max_concurrent_combines
            and (max_total_accounts is None or len(running) + len(funded) + len(queue) < max_total_accounts)
            and spendable >= subscription
            and (max_attempts is None or attempts_started < max_attempts)
            and household_closed_on is None                  # R7: the household rule ended the campaign's buying
            # D-495 (4): under the Focused Trader Program at most `account_limit` live account ("1 active $50K account
            # at a time", 10551016): no purchase while the current accounts are open
            and (not ftp_in_force or len(running) + len(funded) + len(queue) < ftp.account_limit)
            and not _budget_spent(day)                       # D-501: the self-imposed purchase budget
            and not (lv is not None and lv.withholds_purchase(cash, subscription))  # Q-119
            and not (entry_on and any(_entry_refusals(       # D-630: the wallet stop, the pause, the seat ramp
                cash, len(running) + len(funded) + len(queue), pause_in_force, len(payout_days_campaign))))
        ):
            k = attempts_started
            if wallet_w is not None:
                wallet_max_out = max(wallet_max_out, start_bankroll - cash)       # D-630 (a)
            cash -= subscription
            spendable -= subscription
            total_fees += subscription
            fee_sub[day] += subscription
            if lv is not None:  # Q-119
                lv.fee_paid(cash, day)  # Q-119
            running.append(
                combine_cls(
                    index=k, purchase_day=day, draw=combine_draw_factory(k, day),
                    floor_start=-rules.mll,
                    dll=_rtp_dll_on(day), rtp=_rtp_dll_on(day) is not None,
                )
            )
            purchase_days.append(day)
            attempts_started += 1
            if ftp is not None:
                ftp_bought[day] += 1                          # D-495 (4)
            if budget_on:
                budget_bought[day] += 1                       # D-501
        if budget_on and _budget_spent(day) and (            # D-501: a day the budget alone stopped a purchase
            not blocked_by_queue
            and not (lv is not None and lv.withholds_purchase(cash, subscription))  # Q-119
            and len(running) < max_concurrent_combines
            and (max_total_accounts is None or len(running) + len(funded) + len(queue) < max_total_accounts)
            and spendable >= subscription
            and (max_attempts is None or attempts_started < max_attempts)
            and household_closed_on is None
            and (not ftp_in_force or len(running) + len(funded) + len(queue) < ftp.account_limit)
            and not (entry_on and any(_entry_refusals(       # D-630: nor an entry option
                cash, len(running) + len(funded) + len(queue), pause_in_force, len(payout_days_campaign))))
        ):
            budget_blocked_days += 1
        if entry_on and (                                     # D-630: a day one entry option alone stopped a purchase
            not blocked_by_queue
            and not (lv is not None and lv.withholds_purchase(cash, subscription))  # Q-119
            and len(running) < max_concurrent_combines
            and (max_total_accounts is None or len(running) + len(funded) + len(queue) < max_total_accounts)
            and spendable >= subscription
            and (max_attempts is None or attempts_started < max_attempts)
            and household_closed_on is None
            and (not ftp_in_force or len(running) + len(funded) + len(queue) < ftp.account_limit)
            and not _budget_spent(day)
        ):
            refusals = _entry_refusals(cash, len(running) + len(funded) + len(queue), pause_in_force,
                                       len(payout_days_campaign))
            if sum(refusals) == 1:
                if refusals[0]:
                    wallet_blocked_days += 1
                    wallet_first_blocked = day if wallet_first_blocked < 0 else wallet_first_blocked
                elif refusals[1]:
                    pause_blocked_days += 1
                    pause_first = day if pause_first < 0 else pause_first
                else:
                    ramp_blocked_days += 1
                    ramp_first_blocked = day if ramp_first_blocked < 0 else ramp_first_blocked
        if lv is not None:  # Q-119
            lv.purchase_step(  # Q-119
                others_allow=(not blocked_by_queue and len(running) < max_concurrent_combines  # Q-119
                              and (max_total_accounts is None  # Q-119
                                   or len(running) + len(funded) + len(queue) < max_total_accounts)  # Q-119
                              and (max_attempts is None or attempts_started < max_attempts)  # Q-119
                              and household_closed_on is None  # Q-119
                              and (not ftp_in_force or len(running) + len(funded) + len(queue) < ftp.account_limit)  # Q-119
                              and not _budget_spent(day)  # Q-119
                              and not (entry_on and any(_entry_refusals(  # Q-119
                                  cash, len(running) + len(funded) + len(queue), pause_in_force,  # Q-119
                                  len(payout_days_campaign))))),  # Q-119
                house_refuses=lv.withholds_purchase(cash, subscription),  # Q-119
                cash_refuses=spendable < subscription)  # Q-119
        # D-630 (a): a stop that can no longer lift -- above W with nothing live, no pass waiting and no payout on its
        # way, so the cash cannot rise: the stop is final. Recorded only; the campaign idles to the horizon and is not
        # ruined by it (step 7 reads the cash against the fees). The pause cannot end so (D-632): with no funded
        # account held it does not bind.
        if (wallet_w is not None and wallet_final < 0 and start_bankroll - cash > wallet_w and not running
                and not queue and not pending and not any(a.ended_on is None for a in funded)):
            wallet_final = day

        # D-495 (4): the Focused Trader Program's placement, read at this close once the day's purchases are made: the
        # first watched measure at its declared threshold over the window places the campaign on the declared path,
        # binding from tomorrow. A Corrective placement closes every live account here (no breach, nothing refunded),
        # removes the passes waiting for a seat and denies every payout requested and not yet arrived (10551016).
        if ftp is not None and ftp_placed is None and not ftp_done:
            lo = max(0, day - int(ftp.window_days) + 1, ftp_watch_from)
            crossed = []
            if ftp.combine_purchases is not None:
                v = int(ftp_bought[lo:day + 1].sum())
                if v >= int(ftp.combine_purchases):
                    crossed.append(("combine_purchases", v))
            if ftp.funded_lost is not None:
                v = int(ftp_lost[lo:day + 1].sum())
                if v >= int(ftp.funded_lost):
                    crossed.append(("funded_lost", v))
            if crossed:
                ftp_placed = {"day": int(day), "path": ftp.path, "measure": crossed[0][0], "value": crossed[0][1],
                              "measures": dict(crossed), "combines_closed": 0, "funded_closed": 0,
                              "passes_removed": 0, "payouts_denied": 0, "payout_cash_denied": 0.0, "ended_on": -1}
                ftp_placements.append(ftp_placed)
                if ftp.path == FTP_CORRECTIVE:
                    ftp_until = day + int(ftp.corrective_days)
                    for c in running:
                        c.close_ftp(day)
                        finished_combines.append(c)
                    ftp_placed["combines_closed"] = len(running)
                    running = []
                    for c in queue:
                        c.ftp_closed = True
                    ftp_placed["passes_removed"] = len(queue)
                    queue.clear()
                    for a in funded:
                        if a.ended_on is None:
                            a.close_ftp(day)
                            ftp_placed["funded_closed"] += 1
                    for _, amount, acc in reversed(pending):      # an account's pending payouts are its latest
                        acc.deny_pending_ftp(amount, rules)
                        ftp_placed["payouts_denied"] += 1
                        ftp_placed["payout_cash_denied"] += float(amount)
                    pending = []

        # 7. ruin: nothing live, and the campaign cannot take its next step (after the household rule there is none).
        if not ruined and household_closed_on is None:
            nothing_live = not running and not funded
            if queue:
                stuck = cash < activation and (stop_buying_when_queued or cash < subscription)
            else:
                stuck = cash < subscription
            if nothing_live and stuck:
                ruined = True
                ruin_day = day

        if lv is not None:  # Q-119
            lv.end_of_day(day, cash, running, funded, queue, finished_combines, max_concurrent_accounts)  # Q-119
        cash_series[day] = cash
        active_series[day] = len(funded)
        # R11: a finished account never trades again and the finished lists only grow, so their trades are added once,
        # as each account finishes; the same integer total as summing them all each day
        for c in finished_combines[n_finished_c:]:
            finished_trades += c.trades
        for a in finished_funded[n_finished_f:]:
            finished_trades += a.trades
        n_finished_c, n_finished_f = len(finished_combines), len(finished_funded)
        now_trades = finished_trades + sum(c.trades for c in running) + sum(a.trades for a in funded)
        trades_by_day[day] = now_trades - trades_so_far       # D-305: the day's executed trades, every account
        trades_so_far = now_trades
        peak_cash = max(peak_cash, cash)
        max_dd = max(max_dd, peak_cash - cash)

    if wallet is not None:                              # D-206: leave the final cash in the shared pot
        wallet.cash = cash
    if queue:
        if len(funded) < max_concurrent_accounts and not on_pass:
            passes_forfeited += len(queue)
        else:
            passes_on_hold_at_end = len(queue)

    if lv is not None:  # Q-119
        lv.publish(all_funded=finished_funded + funded, fee_sub=fee_sub, fee_act=fee_act,  # Q-119
                   trades_by_day=trades_by_day, total_fees=total_fees, cash_series=cash_series)  # Q-119
    gaps = tuple(
        int(b - a) for a, b in zip(payout_days_campaign, payout_days_campaign[1:])
    )
    # Sizing diagnostics, summed over every account whose draw sized trades in contracts.
    sized = at_cap = unsized = stood = need_exits = room_capped = 0
    intended = realised = intended_capped = 0.0
    for acct in finished_combines + running + finished_funded + funded:
        stats = getattr(acct.draw, "stats", None)
        if stats is None:
            continue
        sized += int(stats.trades)
        at_cap += int(stats.at_cap)
        unsized += int(stats.unsized)
        stood += int(getattr(stats, "stood_aside", 0))
        need_exits += int(getattr(stats, "need_exits", 0))
        room_capped += int(getattr(stats, "room_capped", 0))
        intended += float(stats.intended_risk)
        intended_capped += float(getattr(stats, "intended_capped_risk", stats.intended_risk))
        realised += float(stats.realised_risk)
    path = CampaignPath(
        final_cash=float(cash),
        initial_bankroll=float(initial_bankroll),
        cash_series=cash_series,
        active_funded_series=active_series,
        trades_by_day=tuple(int(x) for x in trades_by_day),
        ruined=ruined,
        ruin_day=ruin_day,
        max_drawdown=float(max_dd),
        max_drawdown_frac=float(max_dd / peak_cash) if peak_cash else 0.0,
        attempts_started=attempts_started,
        accounts_funded=accounts_funded,
        accounts_ever_paid=accounts_ever_paid,
        days_to_first_payout=payout_days_campaign[0] if payout_days_campaign else None,
        payout_gaps=gaps,
        total_fees=float(total_fees),
        total_payouts=float(total_payouts),
        peak_queue_length=peak_queue,
        passes_forfeited=passes_forfeited,
        combines_abandoned=combines_abandoned,
        passes_on_hold_at_end=passes_on_hold_at_end,
        same_day_multi_breach_days=multi_breach_days,
        max_breaches_in_one_day=max_breached,
        trades_sized=sized,
        trades_at_tier_cap=at_cap,
        trades_unsized=unsized,
        trades_stood_aside=stood,
        trades_need_exits=need_exits,
        trades_room_capped=room_capped,
        combines_out_of_room=combines_out_of_room,
        combines_abandoned_by_policy=combines_abandoned_by_policy,
        funded_abandoned=funded_abandoned,
        funded_flips=sum(int(a.flips) for a in finished_funded + funded),             # D-339
        funded_flips_won=sum(int(a.flips_won) for a in finished_funded + funded),
        intended_risk_total=intended,
        intended_capped_risk_total=intended_capped,
        realised_risk_total=realised,
    )
    # A queued pass is already in `finished_combines` (it resolved); only the unresolved ones
    # in `running` are missing from it.
    all_combines = sorted(finished_combines + running, key=lambda c: c.index)
    all_funded = sorted(finished_funded + funded, key=lambda a: a.index)
    conduct_out: dict[str, Any] = {}
    if conduct is not None:
        w = conduct.pattern_window_days
        bought = np.zeros(horizon_days, dtype=int)
        for d in purchase_days:
            bought[d] += 1
        roll = lambda x: int(np.convolve(x, np.ones(w, dtype=int), "valid").max()) if len(x) >= w \
            else int(x.sum())                                                          # noqa: E731
        conduct_out = {
            "rtp_placed_day": -1 if rtp_day is None else int(rtp_day), "rtp_trigger": rtp_trigger,
            "payouts_requested": payouts_requested, "payouts_exposed": payouts_exposed,
            "payouts_denied": payouts_denied, "max_mll_breaches_in_window": roll(breaches_per_day),
            "max_combine_purchases_in_window": roll(bought), "combine_purchases": len(purchase_days),
            "mll_breaches": int(breaches_per_day.sum()), "window_days": w,
        }
        if conduct.rtp_warnings:
            conduct_out["rtp_warning_days"] = tuple(rtp_warning_days)
    if reset_failed_combines:
        conduct_out = dict(conduct_out, resets=resets_taken)
    campaign_days: tuple[dict[str, Any], ...] = ()
    if record_days:
        campaign_days = tuple(
            {"day": d, "fee_subscription": float(fee_sub[d]), "fee_activation": float(fee_act[d]),
             "fee_reset": float(fee_reset[d]), "payouts_in": float(pay_in[d]), "cash": float(cash_series[d]),
             "active_funded": int(active_series[d]), "breaches": int(breaches_per_day[d])}
            for d in range(horizon_days)
        )
    return LockstepPath(
        path=path,
        combines=tuple(_record_combine(c) for c in all_combines),
        funded=tuple(_record_funded(a) for a in all_funded),
        breaches_per_day=breaches_per_day,
        trades=tuple(ledger) if ledger is not None else (),
        conduct=conduct_out,
        account_days=tuple(account_days),
        campaign_days=campaign_days,
        focused_trader=({} if ftp is None else {
            "decision": "D-495", "model": ftp.as_dict(), "placements": tuple(dict(x) for x in ftp_placements),
            "placed": bool(ftp_placements), "first_placed_day": int(ftp_placements[0]["day"]) if ftp_placements else -1,
            "total_combine_purchases_and_resets": int(ftp_bought.sum()), "total_funded_lost": int(ftp_lost.sum()),
            "max_combine_purchases_in_window": _rolling_max(ftp_bought, int(ftp.window_days)),
            "max_funded_lost_in_window": _rolling_max(ftp_lost, int(ftp.window_days)),
            "purchase_days_blocked": int(ftp_blocked_days), "resets_refused": int(ftp_resets_refused),
            **{k: sum(x[k] for x in ftp_placements) for k in ("combines_closed", "funded_closed", "passes_removed",
                                                              "payouts_denied", "payout_cash_denied")}}),
        purchase_budget=({} if not budget_on else {
            "decision": "D-501", "k": int(budget_k), "window_days": int(budget_w),
            "purchases_and_resets": int(budget_bought.sum()),
            "max_purchases_in_window": _rolling_max(budget_bought, int(budget_w)),
            "purchase_days_blocked": int(budget_blocked_days), "resets_refused": int(budget_resets_refused)}),
        wallet_stop=({} if wallet_w is None else {
            "decision": "D-630", "w": float(wallet_w), "purchase_days_blocked": int(wallet_blocked_days),
            "resets_refused": int(wallet_resets_refused), "first_blocked_day": int(wallet_first_blocked),
            "max_out_of_pocket_at_purchase": float(wallet_max_out), "final_on": int(wallet_final),
            "on_at_end": bool(start_bankroll - cash > wallet_w)}),      # above W at the horizon: the stop is on
        pause_after_funded=({} if pause_f is None else {
            "decision": "D-630", "wording": "D-632", "f": int(pause_f), "paused_on": int(pause_first),
            "released_on": int(payout_days_campaign[0]) if (pause_first >= 0 and payout_days_campaign) else -1,
            "purchase_days_blocked": int(pause_blocked_days), "resets_refused": int(pause_resets_refused),
            "in_force_days": int(pause_days), "spells": int(pause_spells),
            "resumed_below_f": len(pause_resumed), "resumed_below_f_days": tuple(int(d) for d in pause_resumed)}),
        seat_ramp=({} if ramp_s0 is None else {
            "decision": "D-630", "s0": int(ramp_s0), "base_seats": int(ramp_base),
            "payouts_arrived": len(payout_days_campaign),
            "seats_at_end": int(min(ramp_base, ramp_s0 + len(payout_days_campaign))),
            "purchase_days_blocked": int(ramp_blocked_days), "first_blocked_day": int(ramp_first_blocked),
            "full_on": int(ramp_full_on)}),
        household=({"reading": "closes_household" if household_on else "count_only",
                    "triggers": household_triggers,
                    "closed_on": -1 if household_closed_on is None else int(household_closed_on),
                    "combines_closed": household_combines, "funded_closed": household_funded,
                    "passes_closed": household_passes} if household_rule else {}),
    )


def _one_path(protocol: Protocol, path_index: int, path_seed: int, path_kwargs: dict[str, Any],
              draw_factories_for_path: Callable[[int], tuple] | None, flip_for_path: Callable[[int], tuple] | None,
              wallet_for_path: Callable[[int], Any] | None) -> LockstepPath:
    """One path of `simulate_lockstep_campaign` from its seed: the draws the caller's factory makes for it (or the
    independent binary draws), then `simulate_lockstep_path`."""
    simulate_lockstep_path = counted(path_kwargs.get("levers"))  # Q-119
    hook: DayHook | None = None
    if draw_factories_for_path is not None:
        made = draw_factories_for_path(path_seed)
        flip_factory = flip_spec = None
        if len(made) == 5:                            # D-339: with the flip stream's draw factory and spec
            c_factory, f_factory, hook, flip_factory, flip_spec = made
        elif len(made) == 3:
            c_factory, f_factory, hook = made
        else:
            c_factory, f_factory = made
    else:
        c_factory, f_factory = binary_draw_factories(protocol, path_kwargs["edge"], path_seed, path_kwargs["rules"])
        # D-339: the flip stream beside the binary draws, when the caller gives one (the table's campaign check)
        flip_factory, flip_spec = flip_for_path(path_seed) if flip_for_path is not None else (None, None)
    return simulate_lockstep_path(
        protocol, seed=path_seed,
        combine_draw_factory=c_factory, funded_draw_factory=f_factory, day_hook=hook,
        flip_draw_factory=flip_factory, flip=flip_spec,                                       # D-339
        wallet=wallet_for_path(path_index) if wallet_for_path is not None else None,
        **path_kwargs,
    )


def _path_chunk(task: tuple) -> tuple[list[LockstepPath], Any]:
    """A worker's share: its paths in order, and the draw factory's `export_state()` after them (None without one)."""
    protocol, path_kwargs, factories, flip_for_path, items = task
    out = [_one_path(protocol, i, s, path_kwargs, factories, flip_for_path, None) for i, s in items]
    export = getattr(factories, "export_state", None)
    return out, (export() if callable(export) else None)


def _run_paths(protocol: Protocol, path_kwargs: dict[str, Any], seeds: Sequence[int],
               draw_factories_for_path: Callable[[int], tuple] | None, flip_for_path: Callable[[int], tuple] | None,
               wallet_for_path: Callable[[int], Any] | None, *, workers: int = 1, pool: Any = None,
               memory_per_worker_gb: float | None = None) -> list[LockstepPath]:
    """The paths in path order: here, one after another (workers 1, or the guard allowing one), or split into
    contiguous chunks across a process pool and put back in order (R11)."""
    items = list(enumerate(seeds))
    if int(workers) > 1 or pool is not None:         # refused whatever the memory guard then allows
        check_parallel_inputs(protocol, path_kwargs, draw_factories_for_path, flip_for_path,
                              wallet_for_path=wallet_for_path)
    own = None
    n = 1
    if pool is not None:
        n = max(1, int(workers))
    elif int(workers) > 1 and len(items) > 1:
        own, n = path_pool(int(workers), n_tasks=len(items), memory_per_worker_gb=memory_per_worker_gb)
    if (pool is None and own is None) or len(items) <= 1:
        if own is not None:
            own.shutdown()
        return [_one_path(protocol, i, s, path_kwargs, draw_factories_for_path, flip_for_path, wallet_for_path)
                for i, s in items]
    k = min(len(items), 4 * n)                        # a few chunks a worker, so a slow chunk does not idle the rest
    bounds = [round(j * len(items) / k) for j in range(k + 1)]
    tasks = [(protocol, path_kwargs, draw_factories_for_path, flip_for_path, items[bounds[j]:bounds[j + 1]])
             for j in range(k)]
    try:
        with _WorkerEnvironment():                    # workers start during the submissions, with one BLAS thread
            futures = [(pool or own).submit(_path_chunk, task) for task in tasks]
        done = [f.result() for f in futures]
    finally:
        if own is not None:
            own.shutdown()
    results: list[LockstepPath] = []
    absorb = getattr(draw_factories_for_path, "import_state", None)
    for chunk, state in done:
        results.extend(chunk)
        if state is not None and callable(absorb):
            absorb(state)
    return results


# ------------------------------------------------------------------------------------------------ the guard and the proof


def source_sha256(fn: Callable) -> str:
    """The sha256 of a function's source text, with line endings normalised to LF."""
    src = inspect.getsource(fn).replace("\r\n", "\n")
    return hashlib.sha256(src.encode("utf-8")).hexdigest()


def vendored_sha256() -> dict[str, str]:
    """Each copied vendored function's LF source sha256, as the vendored module holds it now."""
    return {name: source_sha256(getattr(_vl, name)) for name in VENDORED_SHA256}


def check_vendored_source(expected: dict[str, str] | None = None) -> None:
    """Refuse (`RuntimeError`) unless every vendored function this module copies is the one it was composed from."""
    want = VENDORED_SHA256 if expected is None else dict(expected)
    got = vendored_sha256()
    bad = [f"{k}: {got.get(k)} not {v}" for k, v in want.items() if got.get(k) != v]
    if bad:
        raise RuntimeError("REFUSED (RD-03 A-1): the vendored lockstep functions changed -- " + "; ".join(bad)
                           + " -- re-compose extended/levers_path.py under the new snapshot's row")


COPIES = ("simulate_lockstep_path", "_one_path", "_path_chunk", "_run_paths")


def recomposition_problems() -> dict[str, list[str]]:
    """Each copied function against the vendored one, statement for statement, with every line marked Q-119 removed
    (`extended.campaign.recomposition_problems`); empty lists when the marked lines are the only differences."""
    from extended.campaign import recomposition_problems as rp

    here = globals()
    return {name: rp(here[name], getattr(_vl, name), (MARKER,)) for name in COPIES}


def marked_lines() -> dict[str, int]:
    """How many lines of each copy carry the marker (the additions; zero for the runner's two verbatim copies)."""
    import re

    pat = re.compile(r"#\s*" + re.escape(MARKER) + r"\b")
    return {name: sum(1 for ln in inspect.getsource(globals()[name]).split("\n") if pat.search(ln)) for name in COPIES}


# ------------------------------------------------------------------------------------------------ the counted path


def counted(levers: Any) -> Callable:
    """The path `_one_path` calls: this module's, with the counts wrapped onto it when the counters are on (A-1 (d))."""
    if levers is None:
        return simulate_lockstep_path

    def run(*args: Any, **kw: Any) -> Any:
        take_published()
        return wrap(simulate_lockstep_path(*args, **kw), levers)

    return run


# ------------------------------------------------------------------------------------------------ A-2: the replay


def check_levers(levers: Any) -> Levers | None:
    """None, or a `Levers` (`TypeError` otherwise)."""
    if levers is None:
        return None
    if not isinstance(levers, Levers):
        raise TypeError(f"levers must be an extended.levers_path.Levers, got {type(levers).__name__}")
    return levers


def levers_args(a: dict[str, Any], levers: Levers | None) -> dict[str, Any]:
    """A replay's arguments with a cell's seat and price keywords on its path (A-2, A-4): `max_concurrent_combines`,
    `max_total_accounts` (None when the joint cap is lifted), `stop_buying_when_queued`, `subscription` and
    `activation`, each only when the cell sets it. None: the arguments unchanged (the same object)."""
    if levers is None:
        return a
    path = dict(a["path"])
    if path.get("reset_failed_combines"):
        raise LeverRefused("REFUSED (RD-03 2.5): every cell runs with reset_failed_combines False")
    if levers.max_concurrent_combines is not None:
        path["max_concurrent_combines"] = int(levers.max_concurrent_combines)
    if levers.lift_joint_cap:
        path["max_total_accounts"] = None
    if levers.stop_buying_when_queued is not None:
        path["stop_buying_when_queued"] = bool(levers.stop_buying_when_queued)
    if levers.subscription is not None:
        path["subscription"] = float(levers.subscription)
    if levers.activation is not None:
        path["activation"] = float(levers.activation)
    return {**a, "path": path}


class StartCounts:
    """One task's counts by start, from the replays it ran (each start's longest run: the long replay; the exact-length
    runs are not counted)."""

    def __init__(self) -> None:
        self.by: dict[int, tuple[int, dict[str, Any]]] = {}

    def add(self, s: int, h: int, counts: dict[str, Any] | None) -> None:
        if counts is None:
            counts = zero_counts()
        if int(s) not in self.by or int(h) > self.by[int(s)][0]:
            self.by[int(s)] = (int(h), counts)

    def items(self) -> list[tuple[int, dict[str, Any]]]:
        return [(s, c) for s, (_, c) in sorted(self.by.items())]


def replay_with(levers: Levers | None, blocks: Sequence[Any], dates: Sequence[str], fallback: Callable,
                sink: StartCounts | None = None) -> Callable:
    """Q-17's replay (`extended.user_beside.replay`) through this path (A-2): `fallback` itself when `levers` is None;
    else a replay of the same signature `(blocks[s:s + h], args, path_seed)` that finds the slice's start among the
    task's blocks (by identity), attaches its session dates (`Levers.with_dates`) and runs this module's path with the
    options -- the shared day draws as the vendored replay makes them. With the counters on, each run's counts go to
    `sink` by start (the longest run of a start kept)."""
    if levers is None:
        return fallback
    where = {id(b): i for i, b in enumerate(blocks)}

    def replay(sl: Sequence[Any], args: dict[str, Any], path_seed: int):
        from propedge.campaign.shared_days import SharedDayDraws

        n = len(sl)
        i0 = where.get(id(sl[0])) if n else None
        if i0 is None or where.get(id(sl[-1])) != i0 + n - 1:
            raise RuntimeError("REFUSED (RD-03 A-2): a replay's blocks are not a slice of the task's blocks")
        lv = levers.with_dates(dates[i0:i0 + n])
        sd = SharedDayDraws({0: list(sl)}, seed=args["seed"], replay=True, **args["draws"])
        take_published()
        lp = simulate_lockstep_path(args["draws"]["protocol"], seed=int(path_seed), horizon_days=n + 1,
                                    **args["path"], **sd.lockstep_kwargs(), levers=lv)
        counts = take_published()
        if sink is not None and levers.counters:
            sink.add(i0, n, counts)
        return lp

    return replay


class LeverSink:
    """`run_starts(..., levers=L, lever_sink=S)`'s counts, by (design, arm, response) and start: each start's long
    replay's counts (A-1 (d))."""

    def __init__(self) -> None:
        self._by: dict[tuple[str, str, str], dict[int, dict[str, Any]]] = {}

    def collect(self, design: str, arm: str, response: str, items: Sequence[tuple[int, dict[str, Any]]]) -> None:
        key = (str(design), str(arm), str(response))
        if key in self._by:
            raise RuntimeError(f"the sink already holds {key}: each run is counted once")
        self._by[key] = {int(s): dict(c) for s, c in items}

    def starts(self, design: str, arm: str, response: str) -> dict[int, dict[str, Any]]:
        return self._by[(str(design), str(arm), str(response))]

    def keys(self) -> list[tuple[str, str, str]]:
        return list(self._by)


def check_run_levers(levers: Any, lever_sink: Any, counters: Any = None, funded_account_cls: Any = None) -> None:
    """A-2's refusals before any start runs: `levers` a `Levers` (`TypeError`); a sink exactly when the counters are on
    (`ValueError`); not with RD-02's counters' channel or a declared funded class (`ValueError`: not composed --
    RD-03's cells run Topstep's vendored class)."""
    if levers is None:
        if lever_sink is not None:
            raise ValueError("lever_sink without levers")
        return
    check_levers(levers)
    if bool(levers.counters) != (lever_sink is not None):
        raise ValueError("lever_sink is given exactly when the levers' counters are on")
    if lever_sink is not None and not isinstance(lever_sink, LeverSink):
        raise TypeError(f"lever_sink must be an extended.levers_path.LeverSink, got {type(lever_sink).__name__}")
    if counters is not None:
        raise ValueError("RD-02's counters' channel and RD-03's levers together are not composed")
    if funded_account_cls is not None:
        raise ValueError("RD-03's levers run Topstep's vendored FundedAccount (the Focused Trader models admitted); a "
                         "declared funded class is not composed with them")


# ------------------------------------------------------------------------------------------------ A-3: the gate


def gate_lever_arguments(levers: Any, stop_buying_when_queued: Any, subscription: Any, activation: Any
                         ) -> dict[str, Any]:
    """A-3's keywords for the campaign, each only when given: `levers` (the path's options), `stop_buying_when_queued`,
    `subscription` and `activation` (A-4). Empty when none is given."""
    out: dict[str, Any] = {}
    lv = check_levers(levers)
    if lv is not None:
        if lv.day_ordinals is not None:
            raise LeverRefused("REFUSED (RD-03 A-3): the gate's windows run on sessions (no dates)")
        out["levers"] = lv
    if stop_buying_when_queued is not None:
        if not isinstance(stop_buying_when_queued, (bool, np.bool_)):
            raise TypeError(f"stop_buying_when_queued must be a bool, got {stop_buying_when_queued!r}")
        out["stop_buying_when_queued"] = bool(stop_buying_when_queued)
    for k, v in (("subscription", subscription), ("activation", activation)):
        if v is not None:
            if isinstance(v, bool) or not isinstance(v, (int, float, np.floating, np.integer)) or float(v) < 0:
                raise TypeError(f"{k} must be a price of at least 0, got {v!r}")
            out[k] = float(v)
    return out


def gate_lever_columns(kw: dict[str, Any]) -> dict[str, Any]:
    """The row columns naming A-3's keywords given."""
    out = {k: v for k, v in kw.items() if k != "levers"}
    if "levers" in kw:
        out["levers"] = repr(sorted((k, v) for k, v in kw["levers"].as_dict().items()))
    return out


def lever_runner(levers: Any, runner: Callable, path_reducer: Any = None) -> Callable:
    """The campaign's path runner with levers (A-3): this module's `_run_paths` when given (refused with Q-70's place
    recorder, not composed), else `runner` unchanged."""
    if levers is None:
        return runner
    if path_reducer is not None:
        raise ValueError("RD-03's levers and Q-70's place recorder together are not composed")
    return _run_paths


__all__ = ["MARKER", "VENDORED_SHA256", "HOUSE_RULES", "EXPIRY_RULES", "LEVER_KEYS", "ENGINE_KEYS", "LIST_KEYS",
           "LeverRefused", "Levers", "LeverPath", "LeverState", "take_published", "wrap", "zero_counts",
           "simulate_lockstep_path", "_one_path", "_path_chunk", "_run_paths", "source_sha256", "vendored_sha256",
           "check_vendored_source", "COPIES", "recomposition_problems", "marked_lines", "counted", "check_levers",
           "levers_args", "StartCounts", "replay_with", "LeverSink", "check_run_levers", "gate_lever_arguments",
           "gate_lever_columns", "lever_runner"]
