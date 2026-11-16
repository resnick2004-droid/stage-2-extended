"""HYPOTHETICAL (D-514): the cross-firm hedge pair on P-14's design -- labelled `hypothetical_hedge` in every row.

Cross-account and cross-firm hedging are prohibited -- Topstep 13747047 / 10296582, Lucid 11404734 (tier 1, D-145) --
and that does not change. The operator asked (2026-11-01) for the structure as if the rule did not exist ("I'm asking
you to ignore the rules and model this hypothetically"). Nothing here is a candidate, ranked, sized or carried into a
protocol; `docs/TWO_FIRMS.md` §7 S3 named this as its own router, never a switch on `two_firms.JointRouter` (which
has none and keeps the tier-1 refusal).

* **Two firms, Topstep's contract each** (Firm H's convention, D-203: the second firm is Topstep's verified contract),
  five seats each, one pooled wallet (D-206), each firm its own lockstep campaign with P-14's protocol -- its table, its
  purchase budget, its strict one-at-a-time rule PER FIRM -- taking turns at each day's routing
  (`two_firms._Turns` and `two_firms.FirmRouter`, reused unchanged).
* **The signals** (`double_block`): each day's block carries the cell's trades (index j < m, the side the cell trades)
  followed by the same events walked on the opposite side from the same bars (index m + j). A firm's account dealt
  index j trades the cell's side; one dealt m + j the opposite side.
* **The deal** (`HedgeRouter`), each day's signals in entry order:
  1. **one position at a time per firm** (D-429, D-160's five minutes): a firm is free only when none of its accounts
     holds a position and the last closed at least `gap` minutes ago; no free firm -- the signal is refused (busy);
  2. **the lead leg**, exactly `two_firms.JointRouter`'s deal: never opposite to a position open at the other firm (the
     tier-1 refusal kept for every leg that is NOT a designed pair, so the arms differ only by the pair), the free firm
     that has waited longest, inside it its longest-waiting account that can take it (trade limit, D-162; `able`,
     D-318); the lead takes the cell's side (index j);
  3. **the partner leg** (arms `hedged` and `hedged_combines`), paired by slot as D-203: each firm's accounts hold
     slots 0-4 (a new account the lowest free slot, kept while it lives); the other firm's account in the lead's slot
     takes the opposite side (index m + j) when that firm is free, the account exists, can take it, and -- under
     `hedged_combines` -- both legs are Combines. Otherwise the lead trades alone: a signal one firm can take and the
     other cannot is unhedged, and counted. The partner's firm is stamped just before the lead's, so the next pair's
     lead is at the other firm: the two firms take the cell's side in turn.
  `unhedged` deals the lead leg only: `two_firms.JointRouter`'s deal exactly (a test holds the two equal).

Per path, `path_record` reduces both firms' `LockstepPath`s to the pooled readings (the last firm acts last each day,
so its cash series is the pool's, `two_firms.TwoFirmRun`); `readings` and `slice_measures` read them.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Sequence

import numpy as np

from propedge.campaign.two_firms import FirmRouter, SignalStream, _Submission, _Turns, _Wallet
from propedge.outcomes.distribution import DayBlock

TAG = "hypothetical_hedge"
LABEL = ("HYPOTHETICAL (D-514): hypothetical_hedge -- a cross-firm hedge pair, prohibited at Topstep (13747047, "
         "10296582) and Lucid (11404734), tier 1; modelled as if the rule did not exist, never a candidate, never "
         "ranked, sized or carried into a protocol.")
VARIANT = "D-514:hypothetical_hedge"
UNHEDGED, HEDGED, HEDGED_COMBINES = "unhedged", "hedged", "hedged_combines"
MODES = (UNHEDGED, HEDGED, HEDGED_COMBINES)
SLOTS = 5
DEFAULT_GAP_MINUTES = 5.0


def require_label(rows: Sequence[Mapping[str, Any]]) -> None:
    """D-514 / docs/TWO_FIRMS.md §7 S3: no row leaves this study without the label."""
    bad = [i for i, r in enumerate(rows) if r.get("label") != TAG]
    if bad:
        raise ValueError(f"{len(bad)} row(s) without the label {TAG!r} (first: {bad[0]}): the hedge study writes "
                         "nothing unlabelled")


# ------------------------------------------------------------------------------------------------ the doubled day


def _cat(a, b):
    if a is None and b is None:
        return None
    if a is None or b is None:
        raise ValueError("the cell's and the opposite walk's blocks must carry the same fields")
    return np.concatenate([np.asarray(a), np.asarray(b)])


def _cat_rr(a: dict | None, b: dict | None) -> dict | None:
    if a is None and b is None:
        return None
    if a is None or b is None or set(a) != set(b):
        raise ValueError("the cell's and the opposite walk's blocks must carry the same R keys")
    return {k: np.concatenate([np.asarray(a[k], float), np.asarray(b[k], float)]) for k in a}


def double_block(cell: DayBlock, opposite: DayBlock) -> DayBlock:
    """One day's block for the hedge study: the cell's trades (index j < m) then the same events on the opposite side
    (index m + j). Refused unless the opposite block is the cell's events -- the same count and entries -- on the
    other side."""
    m = len(cell)
    if len(opposite) != m:
        raise ValueError(f"the opposite walk has {len(opposite)} trades on a day the cell has {m}")
    if m:
        if cell.entry_t is None or opposite.entry_t is None or not np.array_equal(
                np.asarray(cell.entry_t, float), np.asarray(opposite.entry_t, float)):
            raise ValueError("the opposite walk's entries are not the cell's: the events are not aligned")
        if cell.sides is None or opposite.sides is None or not np.array_equal(
                np.asarray(cell.sides, int), -np.asarray(opposite.sides, int)):
            raise ValueError("the opposite walk is not on the other side of every event")
    return DayBlock(pnl=_cat(cell.pnl, opposite.pnl), risked=_cat(cell.risked, opposite.risked),
                    exit_reasons=tuple(cell.exit_reasons) + tuple(opposite.exit_reasons),
                    risk_per_contract=_cat(cell.risk_per_contract, opposite.risk_per_contract),
                    mae=_cat(cell.mae, opposite.mae), entry_t=_cat(cell.entry_t, opposite.entry_t),
                    exit_t=_cat(cell.exit_t, opposite.exit_t), r_by_rr=_cat_rr(cell.r_by_rr, opposite.r_by_rr),
                    mae_by_rr=_cat_rr(cell.mae_by_rr, opposite.mae_by_rr),
                    markets=None if cell.markets is None else tuple(cell.markets) + tuple(opposite.markets or ()),
                    fee=_cat(cell.fee, opposite.fee), sides=_cat(cell.sides, opposite.sides),
                    exit_by_rr=_cat_rr(cell.exit_by_rr, opposite.exit_by_rr))


def doubled_blocks(cell: Sequence[DayBlock], opposite: Sequence[DayBlock]) -> list[DayBlock]:
    if len(cell) != len(opposite):
        raise ValueError("the cell's and the opposite walk's day sets differ")
    return [double_block(a, b) for a, b in zip(cell, opposite)]


def mirror_shift(cell: Sequence[DayBlock], opposite: Sequence[DayBlock], delta_r: float,
                 delta_by_rr: Mapping[float, float]) -> tuple[list[DayBlock], list[DayBlock]]:
    """The bound-shifted arm (D-514): the cell's trades moved to the bound of e at each R (`gate.shifted_blocks`, as
    the gate row), and the opposite walk moved the same amount the other way -- the signal's edge at its bound is the
    opposite side's edge given up by as much (the two sides read one set of bars)."""
    from propedge.campaign.gate import shifted_blocks

    d = {float(k): float(v) for k, v in delta_by_rr.items()}
    return (shifted_blocks(list(cell), float(delta_r), d),
            shifted_blocks(list(opposite), -float(delta_r), {k: -v for k, v in d.items()}))


# ------------------------------------------------------------------------------------------------ the deal


class HedgeRouter:
    """One path's deal of each day's signals across two firms (the module docstring's rules). `stream` is the
    doubled day blocks' (`SignalStream.from_blocks`); `half` says whether the stream is doubled (the signals are its
    first half) -- False for the plain cell's blocks, which only `unhedged` may deal."""

    def __init__(self, stream: SignalStream, mode: str, *, n_firms: int = 2, doubled: bool = True,
                 gap: float = DEFAULT_GAP_MINUTES, able: bool = False, slots: int = SLOTS, record: bool = False):
        if mode not in MODES:
            raise ValueError(f"mode is one of {MODES}, got {mode!r}")
        if mode != UNHEDGED and (n_firms != 2 or not doubled):
            raise ValueError("a hedged deal needs two firms and the doubled blocks")
        if not float(gap) >= 0.0:
            raise ValueError("the flat gap is a non-negative number of minutes (D-429)")
        self.stream, self.mode, self.n_firms, self.doubled = stream, mode, int(n_firms), bool(doubled)
        self.gap, self.able, self.slots = float(gap), bool(able), int(slots)
        self.tick = 0.0
        self.firm_last = [0.0] * self.n_firms
        self.acct_last: list[dict[tuple, float]] = [{} for _ in range(self.n_firms)]
        self.slot_of: list[dict[tuple, int]] = [{} for _ in range(self.n_firms)]
        self.routed = [0] * self.n_firms          # legs dealt per firm
        self.signals = 0                          # signals offered
        self.hedged = 0                           # signals dealt as a pair
        self.alone = 0                            # signals dealt to one account (unhedged)
        self.skipped_busy = 0                     # no firm free
        self.skipped_opposite = 0                 # the lead leg opposite to a position open at the other firm
        self.skipped = 0                          # a firm free but no account could take it
        self.passed_over = 0                      # `able`: an account's draw could not take it
        self.partner_missing = {"firm_busy": 0, "no_account_in_slot": 0, "not_both_combines": 0, "cannot_take": 0}
        self.combine_pairs: set[tuple[tuple, tuple]] = set()    # (firm 0's Combine key, firm 1's) traded as a pair
        self.pair_kinds: dict[str, int] = {}                     # hedged signals by the legs' kinds
        self.log: list[tuple] | None = [] if record else None
        self.day: int | None = None

    def _slots(self, f: int, keys: Sequence[tuple]) -> None:
        live = set(keys)
        for k in [k for k in self.slot_of[f] if k not in live]:
            del self.slot_of[f][k]
        used = set(self.slot_of[f].values())
        for k in keys:                                     # the engine's order: earliest start first
            if k not in self.slot_of[f]:
                free = next((s for s in range(self.slots) if s not in used), None)
                if free is not None:
                    self.slot_of[f][k] = free
                    used.add(free)

    def deal(self, day: int, subs: Sequence[_Submission]) -> list[dict[tuple, list[int]]]:
        if len(subs) != self.n_firms:
            raise RuntimeError("every firm submits its accounts each day")
        hs = {s.h for s in subs}
        if len(hs) != 1:
            raise RuntimeError(f"the firms' calendars disagree on day {day}: historical days {sorted(hs)}")
        h = hs.pop()
        self.day = int(day)
        out: list[dict[tuple, list[int]]] = [{tuple(k): [] for k in s.keys} for s in subs]
        for f, s in enumerate(subs):
            for k in s.keys:
                self.acct_last[f].setdefault(tuple(k), self.tick)
            self._slots(f, [tuple(k) for k in s.keys])
        n = self.stream.n_trades[h] if 0 <= h < len(self.stream.n_trades) else 0
        m = n // 2 if self.doubled else n
        if self.doubled and n % 2:
            raise RuntimeError(f"historical day {h}: a doubled day has an even number of trades, not {n}")
        if not m:
            return out
        entry, exit_, sides = self.stream.entry[h], self.stream.exit[h], self.stream.sides[h]
        exits_rr = self.stream.exits_by_rr[h]
        open_until = [-np.inf] * self.n_firms
        open_side = [0] * self.n_firms
        pos = [{tuple(k): i for i, k in enumerate(s.keys)} for s in subs]
        by_slot = [{s: k for k, s in self.slot_of[f].items()} for f in range(self.n_firms)]

        def exit_for(f: int, k: tuple, j: int) -> float:
            R = subs[f].rrs.get(k)
            if exits_rr and R is not None:
                arr = exits_rr.get(float(R))
                if arr is not None and j < len(arr) and np.isfinite(arr[j]):
                    return float(arr[j])
            return float(exit_[j])

        def can(f: int, k: tuple, j: int) -> bool:
            cap = subs[f].caps.get(k)
            if cap is not None and len(out[f][k]) >= int(cap):
                return False
            if self.able and k in subs[f].states:
                drw = subs[f].router._draws.get(k)
                if drw is not None and not drw.can_take(h, j, *subs[f].states[k]):
                    self.passed_over += 1
                    return False
            return True

        def take(f: int, k: tuple, j: int, stamp: float) -> None:
            out[f][k].append(j)
            open_until[f], open_side[f] = exit_for(f, k, j), int(sides[j])
            self.firm_last[f] = stamp
            self.acct_last[f][k] = stamp
            self.routed[f] += 1

        for j in sorted(range(m), key=lambda x: (float(entry[x]), x)):
            t, side = float(entry[j]), int(sides[j])
            self.signals += 1
            if any(open_until[f] > t and open_side[f] == -side for f in range(self.n_firms)):
                self.skipped_opposite += 1                   # tier 1 on every leg that is not a designed pair
                continue
            free = [f for f in range(self.n_firms) if not open_until[f] + self.gap > t]
            if not free:
                self.skipped_busy += 1
                continue
            lead = None
            for f in sorted(free, key=lambda x: (self.firm_last[x], x)):
                for k in sorted(pos[f], key=lambda x: (self.acct_last[f][x], pos[f][x])):
                    if can(f, k, j):
                        lead = (f, k)
                        break
                if lead is not None:
                    break
            if lead is None:
                self.skipped += 1
                continue
            f, k = lead
            partner = None
            if self.mode != UNHEDGED:
                g = 1 - f
                kb = by_slot[g].get(self.slot_of[f].get(k, -1))
                if g not in free:
                    self.partner_missing["firm_busy"] += 1
                elif kb is None:
                    self.partner_missing["no_account_in_slot"] += 1
                elif self.mode == HEDGED_COMBINES and (k[0] != "combine" or kb[0] != "combine"):
                    self.partner_missing["not_both_combines"] += 1
                elif not can(g, kb, m + j):
                    self.partner_missing["cannot_take"] += 1
                else:
                    partner = (g, kb)
            self.tick += 1.0
            if partner is not None:
                g, kb = partner
                take(g, kb, m + j, self.tick - 0.5)          # stamped first: the next pair's lead is at this firm
                take(f, k, j, self.tick)
                self.hedged += 1
                kinds = "-".join(sorted((k[0], kb[0])))
                self.pair_kinds[kinds] = self.pair_kinds.get(kinds, 0) + 1
                if k[0] == "combine" and kb[0] == "combine":
                    self.combine_pairs.add((k, kb) if f == 0 else (kb, k))
            else:
                take(f, k, j, self.tick)
                self.alone += 1
            if self.log is not None:
                self.log.append((int(day), int(h), int(j), int(f), k, None if partner is None else partner[1], t,
                                 open_until[f], None if partner is None else open_until[partner[0]], side))
        return out

    def counts(self) -> dict[str, Any]:
        return {"signals": self.signals, "hedged": self.hedged, "alone": self.alone,
                "skipped_busy": self.skipped_busy, "skipped_opposite": self.skipped_opposite, "skipped": self.skipped,
                "passed_over": self.passed_over, "legs": list(self.routed),
                **{f"partner_{k}": v for k, v in self.partner_missing.items()},
                **{f"pairs_{k}": v for k, v in self.pair_kinds.items()}}


# ------------------------------------------------------------------------------------------------ the runner


@dataclass
class PathSpec:
    """One path of the joint run: its seed, its day blocks (resampled from them, or replayed in order), its horizon."""

    seed: int
    blocks: Sequence[DayBlock]
    horizon_days: int
    replay: bool = False


@dataclass
class JointPath:
    """One path's firms' `LockstepPath`s (in firm order) and its deal. `second_firm` (D-643): the sequencing option's
    record of the path (`propedge.research.second_firm.run_sequenced`); None on every run without the option."""

    paths: list[Any]
    router: HedgeRouter
    second_firm: dict[str, Any] | None = None


@dataclass
class FirmSetup:
    """What every firm's campaign shares: `SharedDayDraws`' arguments (all but blocks, seed, replay), and
    `simulate_lockstep_path`'s (all but seed, horizon, draw factories, day hook, wallet)."""

    protocol: Any
    draws: dict[str, Any]
    path: dict[str, Any]
    bankroll: float = field(default=0.0)


def run_joint(specs: Sequence[PathSpec], setup: FirmSetup, *, n_firms: int, mode: str, doubled: bool,
              gap: float = DEFAULT_GAP_MINUTES, able: bool | None = None, timeout: float = 1800.0,
              record: bool = False, firm_setups: Sequence[FirmSetup] | None = None,
              second_firm_opens: str | None = None) -> list[JointPath]:
    """Every path of `specs` with `n_firms` firms of `setup`'s contract and protocol, in threads taking turns at each
    day's deal (D-206's pattern, `two_firms._Turns`), on one wallet per path. Each firm's path is the engine's own
    (`SharedDayDraws` -> `simulate_lockstep_path`) with its router replaced by `two_firms.FirmRouter` on the joint
    deal, exactly as `two_firms.run_two_firms` builds it; one firm alone is a single-firm campaign.

    `firm_setups` (D-567's seat split): one `FirmSetup` per firm in firm order, each firm's campaign run on its own
    (`with_seats` gives a firm fewer seats and its own purchase budget); the pooled wallet's bankroll is `setup`'s.
    None (every earlier caller) runs every firm on `setup`, exactly as before.

    `second_firm_opens` (D-643 (2), the sequencing option; plain data): None (the default, every earlier caller) runs
    every firm from day 0, exactly as before -- nothing below changes. `"first_payout_arrival"`: the second of two
    firms buys nothing and holds nothing until the campaign's first payout has ARRIVED as cash at the first firm, and
    runs as declared from the next purchase step (`propedge.research.second_firm.run_sequenced`, which says how; the
    unhedged deal only). Each `JointPath.second_firm` then records the arrival day and the day the firm opened."""
    from propedge.campaign.lockstep import simulate_lockstep_path
    from propedge.campaign.shared_days import SharedDayDraws

    if second_firm_opens is not None:                    # D-643 (2): off by default; the day-0 run is the code below
        from propedge.research import second_firm as sf

        return sf.run_sequenced(specs, setup, n_firms=n_firms, mode=mode, doubled=doubled, gap=gap, able=able,
                                timeout=timeout, record=record, firm_setups=firm_setups,
                                opens=sf.check_second_firm_opens(second_firm_opens))
    if firm_setups is not None and len(firm_setups) != int(n_firms):
        raise ValueError(f"firm_setups holds {len(firm_setups)} setups for {n_firms} firms")
    per_firm = list(firm_setups) if firm_setups is not None else [setup] * int(n_firms)
    able = bool(setup.draws.get("route_able", False)) if able is None else bool(able)
    bankroll = float(setup.path["initial_bankroll"])
    if not bankroll > 0:
        raise ValueError("the pooled bankroll must be positive")
    turns: dict[int, _Turns] = {}
    lock = threading.Lock()
    out: list[list[Any]] = [[None] * len(specs) for _ in range(n_firms)]
    errors: list[BaseException] = []

    def joint(k: int) -> _Turns:
        with lock:
            if k not in turns:
                sp = specs[k]
                stream = SignalStream.from_blocks(list(sp.blocks))
                turns[k] = _Turns(n_firms, HedgeRouter(stream, mode, n_firms=n_firms, doubled=doubled, gap=gap,
                                                       able=able, record=record), _Wallet(bankroll), timeout)
                turns[k].aborted = bool(errors)
            return turns[k]

    def go(p: int) -> None:
        try:
            for k, sp in enumerate(specs):
                jt = joint(k)
                jt.enter(p)
                fs = per_firm[p]
                sd = SharedDayDraws({0: list(sp.blocks)}, protocol=fs.protocol, seed=int(sp.seed),
                                    replay=bool(sp.replay), **fs.draws)
                sd.router = FirmRouter(sd.table, [len(b) for b in sp.blocks], jt, p)
                kw = sd.lockstep_kwargs()
                if set(kw) != {"combine_draw_factory", "funded_draw_factory", "day_hook"}:
                    raise ValueError("the hedge study runs no flip stream")
                out[p][k] = simulate_lockstep_path(fs.protocol, seed=int(sp.seed), horizon_days=int(sp.horizon_days),
                                                   wallet=jt.wallet, **kw, **fs.path)
                jt.release(p)
        except BaseException as exc:                     # noqa: BLE001 -- raised again below, after the others stop
            errors.append(exc)
            with lock:
                for jt in turns.values():
                    jt.abort()

    threads = [threading.Thread(target=go, args=(p,), name=f"hedge-firm-{p}") for p in range(n_firms)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if errors:
        raise errors[0]
    return [JointPath(paths=[out[p][k] for p in range(n_firms)], router=turns[k].router) for k in range(len(specs))]


def setup_from_engine_args(args: Mapping[str, Any], *, funded_horizon_days: int | None = None,
                           combine_max_days: int | None = None) -> FirmSetup:
    """A `FirmSetup` from `customer_slices.engine_args`' output (the gate's engine call for one path, argument for
    argument); a resampled run takes the campaign's funded horizon and Combine limit (`simulate_lockstep_campaign`'s
    defaults, 504 and 2000) in place of the replay's."""
    draws = dict(args["draws"])
    path = dict(args["path"])
    if funded_horizon_days is not None:
        path["funded_horizon_days"] = int(funded_horizon_days)
    if combine_max_days is not None:
        path["combine_max_days"] = int(combine_max_days)
    protocol = draws.pop("protocol")
    if draws.get("flip") is not None:
        raise ValueError("the hedge study runs no flip stream")
    return FirmSetup(protocol=protocol, draws=draws, path=path, bankroll=float(path["initial_bankroll"]))


def with_seats(setup: FirmSetup, seats: int, budget: tuple[int, int] | None) -> FirmSetup:
    """D-567: the same firm with `seats` accounts -- its concurrent accounts, concurrent Combines and total accounts
    all set to `seats` -- and its own purchase budget (K, window) or none; everything else unchanged."""
    from propedge.campaign.lockstep import check_purchase_budget

    s = int(seats)
    if s < 1:
        raise ValueError(f"a firm has at least one seat, got {seats!r}")
    path = dict(setup.path)
    path.update(max_concurrent_accounts=s, max_concurrent_combines=s, max_total_accounts=s)
    if budget is None:
        path.pop("purchase_budget", None)
    else:
        path["purchase_budget"] = check_purchase_budget(tuple(budget))
    return replace(setup, path=path)


def with_capacity(setup: FirmSetup, trades_per_day: int) -> FirmSetup:
    """The same setup with the protocol's day capacity raised to hold a doubled day (`SharedDayDraws` refuses a log
    busier than it; an account's slots beyond its dealt trades take nothing)."""
    if int(trades_per_day) <= int(setup.protocol.trades_per_day):
        return setup
    return replace(setup, protocol=replace(setup.protocol, trades_per_day=int(trades_per_day)))


# ------------------------------------------------------------------------------------------------ the readings


def _pay_days(p: Any) -> list[int]:
    if p.days_to_first_payout is None:
        return []
    out = [int(p.days_to_first_payout)]
    for g in p.payout_gaps:
        out.append(out[-1] + int(g))
    return out


def path_record(jp: JointPath, *, margin: float) -> dict[str, Any]:
    """One path's pooled reading: the pool's cash (the last firm's series), every firm's fees, payouts, trades,
    passes (campaign day, firm, index), resolved Combines in order, payout days, and the deal's counts. The single-firm
    identity's columns (`zero_edge_decomposition.PATH_COLS`) from firm 0 as well."""
    from propedge.campaign import portfolio as pf

    last = jp.paths[-1].path
    cash = np.asarray(last.cash_series, float)
    init = float(last.initial_bankroll)
    combines = []
    passes = []
    pays: list[int] = []
    for f, lp in enumerate(jp.paths):
        for c in lp.combines:
            if c.resolved_on is not None:
                combines.append((int(c.resolved_on), f, int(c.index), bool(c.passed)))
            if c.passed and c.resolved_on is not None:
                passes.append((int(c.resolved_on), f, int(c.index)))
        pays += _pay_days(lp.path)
    combines.sort()
    passes.sort()
    passed_keys = {(f, i) for _, f, i in passes}
    pairs = [(("combine", a[1]), ("combine", b[1])) for a, b in jp.router.combine_pairs]
    pair_pass = [int((0, a[1]) in passed_keys) + int((1, b[1]) in passed_keys) for a, b in pairs]
    tbd = [np.asarray(lp.path.trades_by_day, int) for lp in jp.paths]
    n = max(len(x) for x in tbd) if tbd else 0
    trades_by_day = np.zeros(n, int)
    for x in tbd:
        trades_by_day[:len(x)] += x
    p0 = jp.paths[0].path
    return {
        "cash": cash, "initial": init, "days": int(len(cash)),
        "fees": float(sum(float(lp.path.total_fees) for lp in jp.paths)),
        "payouts_dollars": float(sum(float(lp.path.total_payouts) for lp in jp.paths)),
        "trades_by_day": trades_by_day,
        "combines_started": int(sum(len(lp.combines) for lp in jp.paths)),
        "attempts_started": int(sum(int(lp.path.attempts_started) for lp in jp.paths)),
        "accounts_funded": int(sum(int(lp.path.accounts_funded) for lp in jp.paths)),
        "resolved": [(d, bool(ok)) for d, _, _, ok in combines],
        "pass_days": [d for d, _, _ in passes], "pay_days": sorted(pays),
        "pairs": len(pairs), "pairs_with_pass": int(sum(1 for x in pair_pass if x >= 1)),
        "pairs_both_pass": int(sum(1 for x in pair_pass if x >= 2)), "pair_passes": int(sum(pair_pass)),
        "deal": jp.router.counts(),
        "net": float(cash[-1] - init) if len(cash) else float("nan"),
        "deepest_loss_from_start": pf.deepest_loss_from_start(cash, init),
        "needed": pf.deepest_loss_from_start(cash, init) + float(margin),
        # firm 0's own path, in the per-path record's columns (the single-firm identity)
        "firm0": {"final_cash": float(p0.final_cash), "fees": float(p0.total_fees), "payouts": float(p0.total_payouts),
                  "trades": int(sum(p0.trades_by_day)) if len(p0.trades_by_day) else None,
                  "trades_sized": int(p0.trades_sized), "accounts_funded": int(p0.accounts_funded),
                  "attempts_started": int(p0.attempts_started), "realised_risk": float(p0.realised_risk_total),
                  "intended_capped_risk": float(getattr(p0, "intended_capped_risk_total", 0.0)),
                  "deepest_loss_from_start": pf.deepest_loss_from_start(p0.cash_series, p0.initial_bankroll),
                  "days_to_first_payout": p0.days_to_first_payout},
    }


def _q(x: Sequence[float], q: float) -> float:
    v = np.asarray([y for y in x if y is not None and np.isfinite(y)], float)
    return float(np.percentile(v, q)) if v.size else float("nan")


def no_pass_runs(resolved: Sequence[tuple[int, bool]], n: int) -> tuple[int, int]:
    """(windows of `n` consecutive resolved Combines -- in the order they resolved -- with no pass, all such windows)."""
    seq = np.array([bool(ok) for _, ok in resolved], bool)
    if len(seq) < n:
        return 0, 0
    c = np.concatenate([[0], np.cumsum(seq)])
    w = c[n:] - c[:-n]
    return int((w == 0).sum()), int(len(w))


def _gaps(days: Sequence[int]) -> list[int]:
    d = sorted(int(x) for x in days)
    return [b - a for a, b in zip(d, d[1:])]


def _longest(days: Sequence[int], horizon: int) -> int:
    marks = [0] + sorted(int(d) for d in days) + [int(horizon)]
    return int(max(b - a for a, b in zip(marks, marks[1:])))


def readings(recs: Sequence[Mapping[str, Any]], *, margin: float, block: int = 21, first: Sequence[int] = (21, 63),
             runs: Sequence[int] = (3, 5, 10, 20)) -> dict[str, Any]:
    """One arm's pooled readings across its paths (the module docstring; D-514 (4))."""
    from types import SimpleNamespace

    from propedge.campaign import portfolio as pf

    shim = [SimpleNamespace(path=SimpleNamespace(cash_series=r["cash"], initial_bankroll=r["initial"],
                                                 total_fees=r["fees"], total_payouts=r["payouts_dollars"],
                                                 trades_by_day=r["trades_by_day"])) for r in recs]
    m = pf.measures(shim, margin=float(margin), block=int(block))
    days = int(recs[0]["days"]) if recs else 0
    months = (days - 1) / float(block) if days > 1 else float("nan")
    passes = np.array([len(r["pass_days"]) for r in recs], float)
    resolved = np.array([len(r["resolved"]) for r in recs], float)
    pays = np.array([len(r["pay_days"]) for r in recs], float)
    fees = np.array([r["fees"] for r in recs], float)
    pass_gaps = [g for r in recs for g in _gaps(r["pass_days"])]
    pay_gaps = [g for r in recs for g in _gaps(r["pay_days"])]
    horizon = days - 1
    out: dict[str, Any] = {
        "paths": len(recs), "growth_on_required": m.get("growth_on_base_p50"), "required_p90": m.get("required_p90"),
        "required_p50": m.get("required_p50"), "growth_on_required_p10": m.get("growth_on_base_p10"),
        "net_p50": m.get("net_p50"), "net_p10": m.get("net_p10"), "max_drawdown_p50": m.get("max_drawdown_p50"),
        "fees_mean": float(fees.mean()) if len(fees) else float("nan"),
        "payout_dollars_mean": float(np.mean([r["payouts_dollars"] for r in recs])) if recs else float("nan"),
        "combines_started_mean": float(np.mean([r["combines_started"] for r in recs])) if recs else float("nan"),
        "combines_resolved_mean": float(resolved.mean()) if len(resolved) else float("nan"),
        "passes_mean": float(passes.mean()) if len(passes) else float("nan"),
        "passes_p10": _q(passes, 10), "passes_p50": _q(passes, 50),
        "pass_rate_per_combine": float(passes.sum() / resolved.sum()) if resolved.sum() else float("nan"),
        "pairs_mean": float(np.mean([r["pairs"] for r in recs])) if recs else float("nan"),
        "share_pairs_with_a_pass": (float(sum(r["pairs_with_pass"] for r in recs) / sum(r["pairs"] for r in recs))
                                    if sum(r["pairs"] for r in recs) else float("nan")),
        "share_pairs_both_pass": (float(sum(r["pairs_both_pass"] for r in recs) / sum(r["pairs"] for r in recs))
                                  if sum(r["pairs"] for r in recs) else float("nan")),
        "passes_per_pair": (float(sum(r["pair_passes"] for r in recs) / sum(r["pairs"] for r in recs))
                            if sum(r["pairs"] for r in recs) else float("nan")),
        "cost_per_pass": float(fees.sum() / passes.sum()) if passes.sum() else float("nan"),
        "payouts_mean": float(pays.mean()) if len(pays) else float("nan"),
        "payouts_per_month_mean": float(pays.mean() / months) if len(pays) and months > 0 else float("nan"),
        "payouts_per_month_p10": _q(pays / months, 10) if months > 0 else float("nan"),
        "payouts_per_month_p50": _q(pays / months, 50) if months > 0 else float("nan"),
        "days_between_passes_p50": _q(pass_gaps, 50), "days_between_passes_p90": _q(pass_gaps, 90),
        "days_between_passes_max": float(max(pass_gaps)) if pass_gaps else float("nan"),
        "days_between_payouts_p50": _q(pay_gaps, 50), "days_between_payouts_p90": _q(pay_gaps, 90),
        "days_between_payouts_max": float(max(pay_gaps)) if pay_gaps else float("nan"),
        "longest_pass_drought_p50": _q([_longest(r["pass_days"], horizon) for r in recs], 50),
        "longest_pass_drought_p90": _q([_longest(r["pass_days"], horizon) for r in recs], 90),
        "longest_payout_drought_p50": _q([_longest(r["pay_days"], horizon) for r in recs], 50),
        "longest_payout_drought_p90": _q([_longest(r["pay_days"], horizon) for r in recs], 90),
        "days_to_first_pass_p50": _q([r["pass_days"][0] if r["pass_days"] else np.nan for r in recs], 50),
        "days_to_first_payout_p50": _q([r["pay_days"][0] if r["pay_days"] else np.nan for r in recs], 50),
    }
    n_months = int(horizon // block) if horizon > 0 else 0

    def empty_months(ev: Sequence[int]) -> float:
        """The share of the path's whole months (sessions 1-21, 22-42, ...) without an event."""
        got = {(int(d) - 1) // int(block) for d in ev if 1 <= int(d) <= n_months * int(block)}
        return 1.0 - len(got) / n_months if n_months else float("nan")

    out["share_months_no_pass"] = float(np.mean([empty_months(r["pass_days"]) for r in recs])) if recs else float("nan")
    out["share_months_no_payout"] = (float(np.mean([empty_months(r["pay_days"]) for r in recs])) if recs
                                     else float("nan"))
    for d in first:
        out[f"share_paths_no_pass_first_{d}"] = (float(np.mean([not any(x <= d for x in r["pass_days"]) for r in recs]))
                                                 if recs else float("nan"))
        out[f"share_paths_no_payout_first_{d}"] = (float(np.mean([not any(x <= d for x in r["pay_days"])
                                                                  for r in recs])) if recs else float("nan"))
    for n in runs:
        hit = tot = 0
        for r in recs:
            a, b = no_pass_runs(r["resolved"], int(n))
            hit, tot = hit + a, tot + b
        out[f"chance_no_pass_in_{n}_combines"] = float(hit / tot) if tot else float("nan")
    deal = [r["deal"] for r in recs]
    sig = sum(d["signals"] for d in deal)
    for key in ("hedged", "alone", "skipped_busy", "skipped_opposite", "skipped"):
        out[f"share_signals_{key}"] = float(sum(d[key] for d in deal) / sig) if sig else float("nan")
    dealt = sum(d["hedged"] + d["alone"] for d in deal)
    out["share_dealt_signals_hedged"] = float(sum(d["hedged"] for d in deal) / dealt) if dealt else float("nan")
    for key in ("firm_busy", "no_account_in_slot", "not_both_combines", "cannot_take"):
        out[f"partner_missing_{key}_per_path"] = float(np.mean([d[f"partner_{key}"] for d in deal])) if deal else 0.0
    for kinds in ("combine-combine", "combine-funded", "funded-funded"):
        out[f"hedged_{kinds.replace('-', '_')}_per_path"] = (float(np.mean([d.get(f"pairs_{kinds}", 0) for d in deal]))
                                                             if deal else 0.0)
    out["legs_per_path"] = float(np.mean([sum(d["legs"]) for d in deal])) if deal else float("nan")
    return out


def slice_measures(jp: JointPath, horizon: int, subscription: float) -> dict[str, Any]:
    """`customer_slices.slice_measures` on the pool: the pool's cash, every firm's passes and payouts."""
    last = jp.paths[-1].path
    init = float(last.initial_bankroll)
    cash = np.asarray(last.cash_series, float)
    pass_days = sorted(int(c.resolved_on) for lp in jp.paths for c in lp.combines
                       if c.passed and c.resolved_on is not None)
    pay_days = sorted(d for lp in jp.paths for d in _pay_days(lp.path))
    net = float(cash[-1] - init)
    rel = np.concatenate([[0.0], cash - init])
    dd_start = float(max(0.0, -rel.min()))
    dd_high = float((np.maximum.accumulate(rel) - rel).max())
    return {"end_net": net, "positive": bool(net > 0), "passes": len(pass_days), "payouts": len(pay_days),
            "payout_dollars": float(sum(float(lp.path.total_payouts) for lp in jp.paths)), "no_pass": not pass_days,
            "no_payout": not pay_days, "days_to_first_pass": float(pass_days[0]) if pass_days else float("nan"),
            "days_to_first_payout": float(pay_days[0]) if pay_days else float("nan"),
            "longest_pass_gap": _longest(pass_days, horizon), "longest_payout_gap": _longest(pay_days, horizon),
            "drawdown_from_start": dd_start, "drawdown_from_high": dd_high,
            "needed_bankroll": dd_start + float(subscription)}


__all__ = ["TAG", "LABEL", "VARIANT", "UNHEDGED", "HEDGED", "HEDGED_COMBINES", "MODES", "SLOTS", "require_label",
           "double_block", "doubled_blocks", "mirror_shift", "HedgeRouter", "PathSpec", "JointPath", "FirmSetup",
           "run_joint", "setup_from_engine_args", "with_seats", "with_capacity", "path_record", "readings", "no_pass_runs",
           "slice_measures"]
