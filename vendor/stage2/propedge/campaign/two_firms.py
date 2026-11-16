"""Two firms in one campaign (R7; docs/TWO_FIRMS.md): seats at Topstep and Lucid, one position at a time PER FIRM.

The operator (D-452): "one account on Topstep one on Lucid trading - We will no longer be constrained to waiting for
a trade to resolve we can just take the next signal on one firm and then the other without it having to resolve".
A second firm adds seats and a second simultaneous position -- one per firm. This module runs one lockstep campaign
per firm (`propedge.campaign.lockstep`, each with its own contract: rules, fees, caps, payout lag and timing, funded
account class), all on the same signal stream and the same shared calendar, and deals each day's signals across the
firms' accounts in one walk:

* **One position at a time per firm** (the operator's strict rule, D-429, applied per firm): a signal is refused for a
  firm while any of that firm's accounts holds a position or within `gap` minutes of one closing (D-160's five), each
  position held to its exit at the R its account trades when the log carries per-R exits (D-349), else to the log's
  exit. The other firm may take it.
* **Never opposite positions across firms, ever** (conduct tier 1, D-145): a signal whose side is opposite to a
  position open at ANY firm is refused and counted. Lucid prohibits hedging "same-account, cross-account, cross-user,
  cross-firm, correlated opposing" (`prohibited_conduct`, article 11404734, verified 2026-10-04 in the multi-firm
  ledger); Topstep prohibits opposite positions across a trader's own accounts (10296582; D-336 (iv)). Any two firms'
  instruments are treated as correlated, so the rule reads sides only. There is no switch to turn it off: a
  cross-firm hedge pair exists only as a modelled arm labelled `hypothetical_hedge` (D-452), never through this router.
* **One signal, one account** (D-157: no copy trading): a signal goes to at most one account at one firm. When both
  firms are free, the firm that has waited longest since its last routed signal takes it; inside a firm, the account
  that has waited longest (D-216), passed over when at its trade limit (D-162) or, under `able` routing, when its draw
  says it cannot take the trade (D-318).
* **One bankroll**: the campaigns share one wallet (D-206's mechanism) and take turns between their day hooks, so every
  fee and every payout moves one pot in a fixed order and a run repeats exactly from its seed.
* **Each firm's household rule** (the multi-firm repository's D-30): Lucid closes every simulated account in the
  household when a trader is moved live or cashes out ("All simulated prop accounts are closed when a trader is moved
  live, or opts out of trading live via cash-out", 16558826), and an account enters the live review pool at its fifth
  payout. `lucid_firm(household_closes_at_live=True)` -- the conservative default -- ends every Lucid seat at the close
  of the first Lucid fifth payout and buys no more Lucid accounts on that path; the Topstep seats are untouched and keep
  taking signals. False is the optimistic reading, reported beside (the event only counted). `TwoFirmRun.household()`
  reports it per firm and path.

Not supported here, refused loudly: the flip stream (D-339), the XFA second trade and the collect phase (D-368), and a
stream without each trade's entry, exit and side (without them nothing is known about overlaps or sides).
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

import numpy as np

from propedge.campaign.shared_days import ROTATION, SharedDayDraws, TradeRouter
from propedge.outcomes.distribution import DayBlock

#: D-160's flat gap, in the log's time unit (minutes), the operator's strict rule's default (D-429).
DEFAULT_GAP_MINUTES = 5.0


# ------------------------------------------------------------------------------------------------ the firms


@dataclass(frozen=True)
class FirmTerms:
    """One firm's contract at the campaign level: what `simulate_lockstep_campaign` needs to run its seats."""

    slug: str
    rules: Any                                  # the vendored engine's Rules for this firm
    funded_account_cls: type | None             # None: Topstep's FundedAccount
    max_funded: int
    max_combines: int
    max_total: int | None
    subscription: float
    billing_days: int
    activation: float
    payout_lag_days: int
    payout_timing: str
    payout_method: str
    provenance: dict[str, Any] = field(default_factory=dict)
    # R7 (multi-firm D-30): the firm's household rule -- None takes the funded class's own default (none at Topstep)
    household_closure: bool | None = None


def topstep_firm(*, payout_method: str = "aeropay", max_combines: int = 1, max_total: int | None = None,
                 ledger: Any | None = None) -> FirmTerms:
    """Topstep from Stage 2's verified ledger (`config/rules.yaml`), exactly as a single-firm run reads it: the rules
    for the payout method (fee and lag one choice, D-24), the funded cap `max_active_funded_accounts`, the default
    payout timing (8284233)."""
    from propedge.campaign.payout_method import payout_method_terms, rules_for_method
    from propedge.contract.payout_timing import DEFAULT_PAYOUT_TIMING
    from propedge.contract.rules import load_rules

    ledger = ledger if ledger is not None else load_rules()
    rules = rules_for_method(payout_method, ledger=ledger)
    terms = payout_method_terms(payout_method, ledger=ledger)
    return FirmTerms(
        slug="topstep", rules=rules, funded_account_cls=None,
        max_funded=int(ledger.value("max_active_funded_accounts")), max_combines=int(max_combines),
        max_total=max_total, subscription=float(rules.subscription), billing_days=int(rules.billing_days),
        activation=float(rules.activation), payout_lag_days=int(terms.lag_days), payout_timing=DEFAULT_PAYOUT_TIMING,
        payout_method=payout_method,
        provenance={"rules": "config/rules.yaml (RULES_LEDGER.md)", "payout_method": terms.as_dict()},
    )


def lucid_firm(*, open_rows: str | None = None, unpriced: str | None = None, configuration: str | None = None,
               household_closes_at_live: bool = True, max_combines: int | None = None,
               max_total: int | None = None) -> FirmTerms:
    """Lucid (LucidFlex 50K, DLL off) from the vendored ledger's verified rows (`propedge.contract.lucid`): up to 5
    funded and 10 accounts in total per household (11404617), the evaluation's one-time fee, $0 activation, the payout
    within 2 business days (12945796; the upper bound, as the lag), the request at the eligible day's close.
    `open_rows`, `unpriced` and `configuration` as `lucid_rules`: the standard 40 % configuration by default, at its
    verified price (multi-firm D-31: $115.50 one-time, reset $115); were the price rows open again a study would be
    refused, the engine's own checks passing `unpriced="engine_checks_only"`. `household_closes_at_live` (multi-firm D-30): True, the
    conservative default, ends every Lucid seat at the close of the first Lucid fifth payout and buys no more; False is
    the optimistic reading (the event only counted). `max_combines` / `max_total` default to the verified caps
    (10 evaluations; 10 in total)."""
    from propedge.contract.lucid import (LUCID_PAYOUT_TIMING, STANDARD_40, LucidFundedAccount, lucid_provenance,
                                         lucid_rules, lucid_terms)

    configuration = STANDARD_40 if configuration is None else configuration
    rules = lucid_rules(open_rows=open_rows, unpriced=unpriced, configuration=configuration)
    t = lucid_terms()
    total = t.max_total_accounts if max_total is None else int(max_total)
    combines = t.eval_count_limit if max_combines is None else int(max_combines)
    if total > t.max_total_accounts or combines > t.eval_count_limit:
        raise ValueError(f"Lucid allows {t.eval_count_limit} evaluations and {t.max_total_accounts} accounts in total "
                         f"(11404617); got combines={combines}, total={total}")
    return FirmTerms(
        slug="lucid-trading", rules=rules, funded_account_cls=LucidFundedAccount, max_funded=int(t.max_funded),
        max_combines=combines, max_total=total, subscription=float(rules.subscription),
        billing_days=int(rules.billing_days), activation=float(rules.activation),
        payout_lag_days=int(t.payout_processing_days), payout_timing=LUCID_PAYOUT_TIMING,
        payout_method="lucid (12945796: within 2 business days; fee an open row)",
        provenance=lucid_provenance(configuration, unpriced=unpriced,
                                    household_closes_at_live=household_closes_at_live),
        household_closure=bool(household_closes_at_live),
    )


@dataclass(frozen=True)
class FirmParty:
    """One firm's seats in a two-firm campaign: its contract, the protocol its accounts trade, and how trades are
    sized (a `SizingRule`, e.g. `lucid_sizing_rule()` at Lucid; None scales each trade to the leg's dollar risk) and
    decided (a `RiskPolicy`, or None for the protocol's fixed legs)."""

    firm: FirmTerms
    protocol: Any
    sizing: Any = None
    risk_policy: Any = None


# --------------------------------------------------------------------------------------------- the stream


@dataclass(frozen=True)
class SignalStream:
    """Each historical day's signals as the joint walk reads them: count, entries, exits, sides and per-R exits."""

    n_trades: tuple[int, ...]
    entry: tuple[np.ndarray, ...]
    exit: tuple[np.ndarray, ...]
    sides: tuple[np.ndarray, ...]
    exits_by_rr: tuple[dict[float, np.ndarray] | None, ...]

    @classmethod
    def from_blocks(cls, blocks: Sequence[DayBlock]) -> "SignalStream":
        n, en, ex, sd, er = [], [], [], [], []
        for i, b in enumerate(blocks):
            m = len(b)
            if m and (b.entry_t is None or b.exit_t is None or b.sides is None):
                raise ValueError(
                    f"day block {i} has trades without entry and exit times or sides: two firms are routed only on a "
                    "stream that says when each position is open and on which side (one position per firm, D-429; "
                    "never opposite across firms, tier 1)")
            side = np.asarray(b.sides if b.sides is not None else [], int)
            if m and not np.all(np.isin(side, (-1, 1))):
                raise ValueError(f"day block {i}: every side is +1 or -1 (a trade without a side cannot be checked)")
            n.append(m)
            en.append(np.asarray(b.entry_t if b.entry_t is not None else [], float))
            ex.append(np.asarray(b.exit_t if b.exit_t is not None else [], float))
            sd.append(side)
            er.append(b.exit_by_rr)
        return cls(tuple(n), tuple(en), tuple(ex), tuple(sd), tuple(er))


# ------------------------------------------------------------------------------------------- the joint walk


@dataclass
class _Submission:
    keys: list[tuple]
    caps: dict
    states: dict
    rrs: dict
    h: int
    router: Any


class JointRouter:
    """One path's deal of each day's signals across the firms' accounts (the module docstring's rules)."""

    def __init__(self, stream: SignalStream, n_firms: int, *, gap: float = DEFAULT_GAP_MINUTES, able: bool = False,
                 record: bool = False):
        if not float(gap) >= 0.0:
            raise ValueError("the flat gap is a non-negative number of minutes (D-429)")
        self.stream, self.n_firms, self.gap, self.able = stream, int(n_firms), float(gap), bool(able)
        self.tick = 0
        self.firm_last = [0] * self.n_firms
        self.acct_last: list[dict[tuple, int]] = [{} for _ in range(self.n_firms)]
        self.routed = [0] * self.n_firms
        self.skipped_busy = 0              # every firm held a position (or was inside the gap)
        self.skipped_opposite = 0          # opposite to a position open at some firm: tier 1
        self.skipped = 0                   # a firm was free but none of its accounts could take it
        self.passed_over = 0               # `able`: an account's draw could not take it
        self.second_positions = 0          # routed while another firm held a position (same side)
        self.log: list[tuple] | None = [] if record else None
        self.day: int | None = None

    def deal(self, day: int, subs: Sequence[_Submission]) -> list[dict[tuple, list[int]]]:
        if len(subs) != self.n_firms:
            raise RuntimeError("every firm submits its accounts each day")
        hs = {s.h for s in subs}
        if len(hs) != 1:
            raise RuntimeError(f"the firms' calendars disagree on day {day}: historical days {sorted(hs)} -- the "
                               "parties must share one seed (one shared calendar)")
        h = hs.pop()
        self.day = int(day)
        out: list[dict[tuple, list[int]]] = [{tuple(k): [] for k in s.keys} for s in subs]
        for f, s in enumerate(subs):
            for k in s.keys:
                self.acct_last[f].setdefault(tuple(k), self.tick)      # first seen today: waiting since today
        m = self.stream.n_trades[h] if 0 <= h < len(self.stream.n_trades) else 0
        if not m:
            return out
        entry, exit_, sides = self.stream.entry[h], self.stream.exit[h], self.stream.sides[h]
        exits_rr = self.stream.exits_by_rr[h]
        open_until = [-np.inf] * self.n_firms
        open_side = [0] * self.n_firms
        pos = [{tuple(k): i for i, k in enumerate(s.keys)} for s in subs]

        def exit_for(f: int, k: tuple, j: int) -> float:
            R = subs[f].rrs.get(k)
            if exits_rr and R is not None:
                arr = exits_rr.get(float(R))
                if arr is not None and j < len(arr) and np.isfinite(arr[j]):
                    return float(arr[j])
            return float(exit_[j])

        for j in sorted(range(m), key=lambda x: (float(entry[x]), x)):
            t, side = float(entry[j]), int(sides[j])
            if any(open_until[f] > t and open_side[f] == -side for f in range(self.n_firms)):
                self.skipped_opposite += 1                       # tier 1: never opposite across firms
                continue
            free = [f for f in range(self.n_firms) if not open_until[f] + self.gap > t]
            if not free:
                self.skipped_busy += 1                           # D-429, per firm: every firm holds a position
                continue
            taken = False
            for f in sorted(free, key=lambda x: (self.firm_last[x], x)):
                sub = subs[f]
                for k in sorted(pos[f], key=lambda x: (self.acct_last[f][x], pos[f][x])):
                    cap = sub.caps.get(k)
                    if cap is not None and len(out[f][k]) >= int(cap):
                        continue
                    if self.able and k in sub.states:
                        drw = sub.router._draws.get(k)
                        if drw is not None and not drw.can_take(h, j, *sub.states[k]):
                            self.passed_over += 1
                            continue
                    out[f][k].append(j)
                    held_elsewhere = any(open_until[g] > t for g in range(self.n_firms) if g != f)
                    self.second_positions += int(held_elsewhere)
                    open_until[f], open_side[f] = exit_for(f, k, j), side
                    self.tick += 1
                    self.firm_last[f] = self.tick
                    self.acct_last[f][k] = self.tick
                    self.routed[f] += 1
                    if self.log is not None:
                        self.log.append((int(day), int(h), int(j), int(f), k, t, open_until[f], side))
                    taken = True
                    break
                if taken:
                    break
            if not taken:
                self.skipped += 1
        return out

    def counts(self) -> dict[str, Any]:
        return {"routed": list(self.routed), "skipped_busy": self.skipped_busy,
                "skipped_opposite": self.skipped_opposite, "skipped": self.skipped,
                "passed_over": self.passed_over, "second_positions": self.second_positions}


class _Wallet:
    """D-206: the cash pot the firms' campaigns share."""

    def __init__(self, cash: float):
        self.cash = float(cash)


class _Turns:
    """One path's firms taking turns between their day hooks (D-206's pattern, for any number of firms): firm 0 runs
    up to its hook, then firm 1 up to its, ...; the last firm's hook deals the day's signals to all, and firm 0 goes on.
    Only one firm moves at a time, so the shared wallet sees every flow in a fixed order and the run repeats."""

    def __init__(self, n: int, router: JointRouter, wallet: _Wallet, timeout: float):
        self.n, self.router, self.wallet, self.timeout = int(n), router, wallet, float(timeout)
        self.cv = threading.Condition()
        self.turn = 0
        self.subs: list = [None] * self.n
        self.out: list = [None] * self.n
        self.out_day: int | None = None
        self.aborted = False

    def _wait(self, cond) -> None:
        if not self.cv.wait_for(lambda: self.aborted or cond(), timeout=self.timeout):
            raise RuntimeError("the firms' turns timed out")
        if self.aborted:
            raise RuntimeError("another firm's run failed")

    def abort(self) -> None:
        with self.cv:
            self.aborted = True
            self.cv.notify_all()

    def enter(self, party: int) -> None:
        with self.cv:
            self._wait(lambda: self.turn == party)

    def release(self, party: int) -> None:
        with self.cv:
            self.turn = (party + 1) % self.n
            self.cv.notify_all()

    def hook(self, party: int, day: int, sub: _Submission) -> dict:
        with self.cv:
            self.subs[party] = sub
            if party < self.n - 1:
                self.turn = party + 1
                self.cv.notify_all()
                self._wait(lambda: self.out_day == day and self.turn == party)
            else:
                self.out = self.router.deal(day, self.subs)
                self.out_day = day
                self.turn = 0
                self.cv.notify_all()
                self._wait(lambda: self.turn == party)
            return self.out[party]


class FirmRouter(TradeRouter):
    """One firm's router: hands its accounts and their limits to the path's joint walk and routes what it is dealt."""

    def __init__(self, table: Any, trades_by_history_day: Sequence[int], turns: _Turns, party: int):
        super().__init__(table, trades_by_history_day)
        self.turns, self.party = turns, int(party)

    def begin_day(self, day: int, keys: Sequence[tuple], caps: Mapping[tuple, int] | None = None,
                  states: Mapping[tuple, tuple[float, float]] | None = None, flips: Sequence | None = None,
                  rrs: Mapping[tuple, float | None] | None = None, seconds: Mapping | None = None,
                  collect: Mapping | None = None) -> None:
        if flips:
            raise ValueError("the two-firm router does not route a flip stream (D-339)")
        if seconds or collect:
            raise ValueError("the two-firm router does not route the XFA second trade or the collect phase (D-368)")
        h = self.table.historical_day(int(day))
        self._day = int(day)
        sub = _Submission(keys=[tuple(k) for k in keys], caps={tuple(k): v for k, v in (caps or {}).items()},
                          states={tuple(k): v for k, v in (states or {}).items()},
                          rrs={tuple(k): v for k, v in (rrs or {}).items()}, h=int(h), router=self)
        dealt = self.turns.hook(self.party, int(day), sub)
        self._assigned = {tuple(k): list(dealt.get(tuple(k), [])) for k in keys}
        self.routed += sum(len(v) for v in self._assigned.values())


# --------------------------------------------------------------------------------------------- the runner


@dataclass
class TwoFirmRun:
    """Per firm (in the parties' order) the campaign summary and its paths; per path the joint walk (its counts and,
    when recorded, its log) and the shared wallet's daily cash (the last firm acts last each day, so its cash series is
    the pool's)."""

    firms: list[str]
    results: list[tuple[Any, list[Any]]]
    joints: list[JointRouter]
    pooled_cash: list[np.ndarray]
    bankroll: float
    provenance: dict[str, Any]

    def household(self) -> dict[str, list[dict[str, Any]]]:
        """R7 (multi-firm D-30): per firm, each path's household-rule record (`LockstepPath.household`: the reading, the
        triggers -- a Lucid account's fifth payout --, the close it ended the firm's seats on or -1, and what it ended);
        an empty record for a firm without the rule (Topstep)."""
        return {slug: [p.household for p in paths] for slug, (_, paths) in zip(self.firms, self.results)}


def run_two_firms(blocks: Sequence[DayBlock], parties: Sequence[FirmParty], *, seed: int, n_paths: int,
                  horizon_days: int, bankroll: float, gap: float = DEFAULT_GAP_MINUTES, settlement: str | None = None,
                  route_able: bool = False, record: bool = False, markets: int | Sequence[str] | None = None,
                  record_trades: bool = False, timeout: float = 900.0) -> TwoFirmRun:
    """Run the firms' seats on one signal stream and one shared bankroll, one position at a time per firm, never
    opposite across firms. Every firm's campaign runs with the same `seed`, so they share each path's calendar.
    No conduct model runs (`conduct=None`): Topstep's RTP and stacking pattern are Topstep's programs, read beside a
    single-firm verdict; a two-firm verdict states its own (docs/TWO_FIRMS.md). `record` keeps each path's joint
    walk (`JointRouter.log`: day, historical day, signal, firm, account, entry, the exit it is held to, side);
    `record_trades` keeps every executed trade on each firm's paths (`LockstepPath.trades`)."""
    from propedge.campaign.lockstep import simulate_lockstep_campaign

    if len(parties) < 2:
        raise ValueError("two firms or more")
    slugs = [p.firm.slug for p in parties]
    if len(set(slugs)) != len(slugs):
        raise ValueError(f"each firm once: {slugs}")
    short = [p.firm.slug for p in parties if float(bankroll) < float(p.firm.subscription)]
    if short:
        # a path that cannot buy its first evaluation returns before its first day hook, and the other firms would wait
        raise ValueError(f"the bankroll {bankroll} is below the evaluation fee at {short}")
    stream = SignalStream.from_blocks(blocks)
    n = len(parties)
    joints: dict[int, _Turns] = {}
    lock = threading.Lock()
    out: list = [None] * n
    errors: list = []

    def joint(k: int) -> _Turns:
        with lock:
            if k not in joints:
                joints[k] = _Turns(n, JointRouter(stream, n, gap=gap, able=route_able, record=record),
                                   _Wallet(bankroll), timeout)
                joints[k].aborted = bool(errors)         # a firm has failed: nobody waits on a new path
            return joints[k]

    def go(p: int) -> None:
        party = parties[p]
        firm = party.firm
        made = [0]

        def draws(path_seed: int):
            k = made[0]
            if k > 0:
                joint(k - 1).release(p)                  # the last path is over for this firm: the next firm goes on
            jt = joint(k)
            jt.enter(p)
            made[0] += 1
            sd = SharedDayDraws({0: list(blocks)}, protocol=party.protocol, seed=path_seed, mode=ROTATION,
                                sizing=party.sizing, settlement=settlement, markets=markets, route_able=route_able)
            sd.router = FirmRouter(sd.table, [len(b) for b in blocks], jt, p)
            kw = sd.lockstep_kwargs()
            return kw["combine_draw_factory"], kw["funded_draw_factory"], kw["day_hook"]

        try:
            out[p] = simulate_lockstep_campaign(
                party.protocol, edge=0.0, seed=seed, rules=firm.rules, initial_bankroll=bankroll,
                horizon_days=horizon_days, n_paths=n_paths, subscription=firm.subscription,
                billing_days=firm.billing_days, activation=firm.activation, payout_lag_days=firm.payout_lag_days,
                payout_method=firm.payout_method, max_concurrent_accounts=firm.max_funded,
                max_concurrent_combines=firm.max_combines, max_total_accounts=firm.max_total,
                require_verified_cap=False, conduct=None, risk_policy=party.risk_policy,
                draw_factories_for_path=draws, wallet_for_path=lambda k: joint(k).wallet,
                payout_timing=firm.payout_timing, funded_account_cls=firm.funded_account_cls,
                household_closure=firm.household_closure, record_trades=record_trades)
        except BaseException as exc:                     # noqa: BLE001 -- raised again below, after the others stop
            errors.append(exc)
            with lock:
                for jt in joints.values():
                    jt.abort()
        finally:
            with lock:
                last = max(joints) if joints else None
            if last is not None:
                joint(last).release(p)

    threads = [threading.Thread(target=go, args=(p,), name=f"firm-{slugs[p]}") for p in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if errors:
        raise errors[0]
    ks = sorted(joints)
    last_paths = out[-1][1]
    return TwoFirmRun(
        firms=slugs, results=list(out), joints=[joints[k].router for k in ks],
        pooled_cash=[np.asarray(p.path.cash_series, float) for p in last_paths], bankroll=float(bankroll),
        provenance={
            "simulation": "propedge.campaign.two_firms.run_two_firms",
            "firms": {p.firm.slug: {**p.firm.provenance, "max_funded": p.firm.max_funded,
                                    "max_combines": p.firm.max_combines, "max_total": p.firm.max_total,
                                    "payout_lag_days": p.firm.payout_lag_days, "payout_timing": p.firm.payout_timing,
                                    "household_closure": p.firm.household_closure}
                      for p in parties},
            "routing": {"one_position_per_firm_gap_minutes": float(gap), "cross_firm_opposite": "refused (tier 1)",
                        "firm_order": "the firm waiting longest since its last routed signal", "able": bool(route_able)},
            "bankroll": "one shared wallet (D-206)", "seed": int(seed), "n_paths": int(n_paths),
            "horizon_days": int(horizon_days),
        },
    )


__all__ = ["DEFAULT_GAP_MINUTES", "FirmTerms", "FirmParty", "SignalStream", "JointRouter", "FirmRouter", "TwoFirmRun",
           "topstep_firm", "lucid_firm", "run_two_firms"]
