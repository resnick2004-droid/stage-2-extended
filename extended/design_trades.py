"""Q-213: a design's own trigger turned into a trade table in Stage 2's `resolved_coin.cell_trades` schema -- the
general real-bar route (the lead's ruling (A) on the Q-213 hand-back) by which a design reaches the firm path's
baseline mode exactly as H4's naive coin does (`extended.h4_coin_source.build_naive_coin_trades`): the trade table
feeds the vendored `rc_campaign` job, `three_way_baseline.simulate(..., outcome="race")` and H4's
`summarise_baseline_readings`, so a design and H4-B's baselines are read under one convention. Written for any design
of the lever space (Q-190's missing real-bar route): a design spec in, a trade table out.

    from extended import design_trades as DT
    spec = DT.rl3_spec("pd", cutoff, {"hi": "fade", "lo": "fade"}, stop_ticks=50)
    out = DT.build_trades(spec, hist, contexts, day_kinds=..., rr_grid=..., fresh_rr=..., fee_micro_eq=...,
                          tick_value=..., market_entry_ticks=...)      # -> DesignTrades(trades, aux, counts)
    facts = DT.facts_for(out.trades, out.aux, dates, tick_value=..., rr_cols=...)   # TB.TradeFacts by (day, j)

**What a spec is** (`DesignSpec`): a source with the trigger library's interface (`offers(hist, i, ctx)`, a `source`
name: `extended.triggers.RL3Tickets`, `P14Breakout`, `P16Marks`, or `RegisteredMarks` below), the design's **own**
side rule (`side(offer) -> +1 | -1`: for RL3 and P-14 `extended.trigger_sides.trigger_side`, never the coin -- the
evaluation's redraw removes direction later, CHARTER 2), one stop in ticks, the walk's rules (`walker.Rules`), whether
the day runs under the execution rules (`execution="journey"`: `triggers.admit`, `segments`, `rules_for` and
`window_flatten_trade` -- the news, closed and BLS windows, the calendar's voids) or as a registered design was
walked (`execution="registered"`: no calendar and no window, the source filtering its own offers; only for an
identity), and whether the offers of one group are one-cancels-other (`oco`: the first fill of a group a day stands,
the group's other tickets cancelled -- RL3 5.3 / 11.2).

**The walk** is the shared walker's (`extended.walker`, identity E-011): every fill of the day at every R of the grid,
for the rule's side and the mirror (the opposite side at the same fill bar and price, beside only), at the spec's one
stop. A position still open where a window ends its walk is booked by `triggers.window_flatten_trade`'s convention
(E-223 M-4), as the naive coin's walk books it. Costs are Stage 2's (`resolved_coin.cell_trades`' arithmetic through
`h4_coin_source._format_cell_trades`, the formatter H4's I-5 holds to P-16's trades hash): a market fill pays
`market_entry_ticks`, a resting fill none (its slippage is in its price; walker docstring) -- **one entry kind a spec**
(a design mixing market and resting entries refuses here until the formatter takes a per-row entry cost).

**The aux frame** (row for row with the trades): the session, the clock limit (the walk's end for that fill, never the
day's last bar), the move bar (`three_way_baseline.move_bar` only under a walk with the breakeven move; None
otherwise -- a walk with no move has none, so the race never applies the move law to it), the vendored move bar
beside, the volatility at the alert (`h4_coin_source.alert_sigma_cross_session`: bars closed at or before the alert;
a fill with fewer than two changes behind it is dropped and counted, as H4 drops it) and the rule's and mirror's
walked gross ticks at every R.

**Search years only** (E-208): `build_trades` refuses a history holding any day after `extended.reader.CHOICE_END`
(2023-12-29) and any day from 2026-07-17 (the confirmation window). Nothing here reads a file: the bars come in as a
`triggers.History` the caller built inside `extended.search_cut` (the reader's door for the engine's read).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import h4_coin_source as CS
from extended import reader as RDR
from extended import three_way_baseline as TB
from extended import trigger_sides as TS
from extended import triggers as T
from extended import walker as W

TASK = "Q-213"
EXECUTIONS = ("journey", "registered")
CONFIRMATION_FIRST = date(2026, 7, 17)


class DesignRefused(ValueError):
    """A spec or a history this route cannot stand behind."""


@dataclass(frozen=True)
class DesignSpec:
    """One design of a single component (the module docstring). `name` an identifier; `source` the trigger;
    `side(offer)` the design's own side; `stop_ticks` the stop; `rules` the walk; `execution` 'journey' or
    'registered'; `oco` one fill per offer group a day; `entry_kind` 'market' or 'resting' (one a spec)."""

    name: str
    source: Any
    side: Callable[[T.Offer], int]
    stop_ticks: int
    rules: W.Rules = T.JOURNEY
    execution: str = "journey"
    oco: bool = True
    entry_kind: str = "resting"

    def __post_init__(self) -> None:
        if self.execution not in EXECUTIONS:
            raise DesignRefused(f"execution is one of {EXECUTIONS}, not {self.execution!r}")
        if self.entry_kind not in ("market", "resting"):
            raise DesignRefused(f"entry_kind is 'market' or 'resting', not {self.entry_kind!r}")
        if int(self.stop_ticks) <= 0:
            raise DesignRefused("the stop is a positive number of ticks")
        if not callable(getattr(self.source, "offers", None)):
            raise DesignRefused("a source offers(hist, i, ctx) as the trigger library's do")


def rl3_spec(kind: str, cutoff: int, rule: Mapping[str, str], stop_ticks: int, *, name: str | None = None
             ) -> DesignSpec:
    """RL3's tickets of one level kind (`triggers.RL3Tickets`, latency-free: alert 08:30, live 09:00), each sided by
    the declared per-level rule through `trigger_sides.trigger_side` (a fade against the level's role, a break with
    it), walked under `triggers.JOURNEY` (no stop move, the 15:08 CT walk end, the worst of 15:08-15:10 less two
    ticks; RL3 5.4), the kind's tickets one-cancels-other."""
    trig = T.RL3Tickets(kind, int(cutoff))
    TS.check_rule(trig, dict(rule))
    frozen = dict(rule)

    def side(offer: T.Offer) -> int:
        return int(TS.trigger_side(trig, frozen, offer).side)

    return DesignSpec(name or f"rl3_{kind}", trig, side, int(stop_ticks), T.JOURNEY, "journey", True, "resting")


@dataclass(frozen=True)
class RegisteredMarks:
    """A registered design's market marks for an identity (`execution="registered"`): on each day, a market order at
    every mark (live at the mark, latency 0), on a report day (`ctx.bls`) only the marks at or after `report_clear`
    (P-16: A3's 07:30 CT cut and D-533's 07:35 CT release-minute cut, `h4_coin_source.build_p16_i5_trades`). The
    side is the caller's table's (`sides[(date, mark)]`), passed as the spec's side."""

    marks: tuple[int, ...]
    report_clear: int
    source: str = field(default="registered", init=False)

    def offers(self, hist: T.History, i: int, ctx: T.DayContext) -> list[T.Offer]:
        ms = [m for m in sorted(int(x) for x in self.marks) if not (ctx.bls and m < int(self.report_clear))]
        return [T.Offer("registered", int(i), m, 0, m, m, T.MARKET, tag=hist.days[i]) for m in ms]


def registered_spec(marks: Sequence[int], sides: Mapping[tuple[str, int], int], stop_ticks: int, *,
                    report_clear: int, name: str = "registered") -> DesignSpec:
    """A registered design's marks and sides through this route's walk (`walker.STAGE2`, no calendar, no window):
    the identity's spec (P-16's marks and `coin_table` sides reproduce P-16's search-year trades hash)."""
    src = RegisteredMarks(tuple(int(m) for m in marks), int(report_clear))

    def side(offer: T.Offer) -> int:
        return int(sides[(str(offer.tag), int(offer.decision))])

    return DesignSpec(name, src, side, int(stop_ticks), W.STAGE2, "registered", False, "market")


@dataclass
class DesignTrades:
    """`trades` in `resolved_coin.cell_trades`' schema; `aux` row for row (the module docstring); `counts`."""

    trades: pd.DataFrame
    aux: pd.DataFrame
    counts: dict[str, Any]


def check_search_days(days: Sequence[str], what: str = "the history") -> None:
    """Refuse any day after the search years' last day (E-208) or in the confirmation window."""
    late = [d for d in days if date.fromisoformat(str(d)[:10]) > RDR.CHOICE_END]
    if late:
        conf = [d for d in late if date.fromisoformat(str(d)[:10]) >= CONFIRMATION_FIRST]
        if conf:
            raise DesignRefused(f"REFUSED: {what} holds {len(conf)} day(s) of the confirmation window (first {conf[0]})")
        raise DesignRefused(f"REFUSED (E-208): {what} holds {len(late)} day(s) after the search years' last day "
                            f"{RDR.CHOICE_END} (first {late[0]})")


@dataclass(frozen=True)
class _Fill:
    offer: T.Offer
    side: int
    bar: int
    price: float
    resting: bool
    rules: W.Rules


def _fill(spec: DesignSpec, offer: T.Offer, side: int, o, h, l, c, ctx: T.DayContext | None, tick: float = W.TICK
          ) -> tuple[_Fill | None, str]:
    """The offer's fill on its day (or why not): under 'journey' each working stretch (`triggers.segments`) is one
    walker order, live at the stretch's start, cut off at its end, walked by `rules_for`, until one fills or voids;
    under 'registered' one order from the offer's live slot with no cutoff."""
    kind, price = T.order_for(offer, side)
    if spec.execution == "registered":
        stretches = [(int(offer.live), None if offer.expires is None else int(offer.expires))]
    else:
        stretches = T.segments(offer, ctx)
    why = "no_stretch"
    for lv, last in stretches:
        er = spec.rules if spec.execution == "registered" else T.rules_for(lv, ctx, spec.rules)
        order = W.Order(kind, int(side), int(lv), price, None if last is None else int(last) + 1)
        f = W.fill_order(order, o, h, l, c, tick=tick, rules=er)
        if f.status == "filled":
            return _Fill(offer, int(side), int(f.bar), float(f.price), bool(f.resting), er), ""
        why = f"{f.status}:{f.reason}"
        if f.status == "void":
            break
    return None, why


def _walk(o, h, l, c, fills: Sequence[_Fill], stop_ticks: int, rr_grid: Sequence[float], base: W.Rules,
          tick: float = W.TICK) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """The day's fills under one walk (they share `fills[0].rules`), the rule's side and the mirror, at every R; a
    position open where a window ends the walk booked at the window's flatten bar (E-223 M-4, as
    `h4_coin_source._walk_day_both_sides` books it)."""
    er = fills[0].rules
    bl = W.brackets((int(stop_ticks),), rr_grid)
    fb = np.array([f.bar for f in fills], dtype=int)
    fp = np.array([f.price for f in fills], dtype=float)
    sd = np.array([f.side for f in fills], dtype=float)
    rest = np.array([f.resting for f in fills], dtype=bool)
    rule = W.walk(o, h, l, c, fb, fp, sd, rest, bl, tick=tick, rules=er)
    mirr = W.walk(o, h, l, c, fb, fp, -sd, rest, bl, tick=tick, rules=er)
    if int(er.walk_end) < int(base.walk_end) and W.walk_end(o, er) == int(er.walk_end):
        fbw = T.flatten_bar(o, er, base)
        if fbw is not None:
            S = int(stop_ticks)
            for k in range(len(fills)):
                for res, s in ((rule, int(sd[k])), (mirr, -int(sd[k]))):
                    fl = res["kind"][k] == W.FLATTEN
                    if not fl.any():
                        continue
                    adverse = float(l[fbw]) if s > 0 else float(h[fbw])
                    a = int(round(s * (float(fp[k]) - adverse) / tick))
                    if a >= S:
                        res["kind"][k, fl], res["gross"][k, fl], res["mae"][k, fl] = W.STOP, -S, S
                    else:
                        res["gross"][k, fl] = -a - W.FLATTEN_SLIP_TICKS
                        res["mae"][k, fl] = np.maximum(res["mae"][k, fl], max(a, 0))
                    res["exit"][k, fl] = fbw
    return rule, mirr


def build_trades(spec: DesignSpec, hist: T.History, contexts: Callable[[int], T.DayContext], *,
                 day_kinds: Mapping[str, str], rr_grid: Sequence[float], fresh_rr: float, fee_micro_eq: float,
                 tick_value: float, market_entry_ticks: float, days: Sequence[int] | None = None,
                 tick: float = W.TICK) -> DesignTrades:
    """The design's trades on the history's days (all, or the indices `days`), in `cell_trades`' schema, with the aux
    frame and the counts (offers, admitted, refused by reason, filled, unfilled by reason, OCO-cancelled, dropped for
    want of a volatility -- under 'journey' only; a registered table is kept whole, its volatility NaN there)."""
    check_search_days(hist.days)
    rr = tuple(float(R) for R in rr_grid)
    entry_ticks = float(market_entry_ticks) if spec.entry_kind == "market" else 0.0
    closes = [hist.c[i] for i in range(len(hist))]
    rows: list[dict[str, Any]] = []
    aux_rows: list[dict[str, Any]] = []
    counts: dict[str, Any] = {"days": 0, "offers": 0, "admitted": 0, "filled": 0, "oco_cancelled": 0,
                              "dropped_sigma_lt_2": 0, "refused": {}, "unfilled": {}}
    idx = range(len(hist)) if days is None else [int(i) for i in days]
    for i in idx:
        d = hist.days[i]
        ctx = contexts(i)
        counts["days"] += 1
        offers = spec.source.offers(hist, i, ctx)
        counts["offers"] += len(offers)
        if spec.execution == "journey":
            kept, refused = T.admit(offers, ctx)
            for _, why in refused:
                counts["refused"][why] = counts["refused"].get(why, 0) + 1
        else:
            kept = list(offers)
        counts["admitted"] += len(kept)
        o, h, l, c = hist.day(i)
        if not kept or W.last_bar(o) is None:
            continue
        fills: list[_Fill] = []
        for off in kept:
            side = int(spec.side(off))
            if side not in (1, -1):
                raise DesignRefused(f"the spec's side for {off.tag or off.decision} is {side}, not +1 or -1")
            if spec.entry_kind == "market" and off.entry != T.MARKET:
                raise DesignRefused("one entry kind a spec: a market spec offered a resting order")
            if spec.entry_kind == "resting" and off.entry == T.MARKET:
                raise DesignRefused("one entry kind a spec: a resting spec offered a market order")
            f, why = _fill(spec, off, side, o, h, l, c, ctx, tick)
            if f is None:
                counts["unfilled"][why] = counts["unfilled"].get(why, 0) + 1
            else:
                fills.append(f)
        if spec.oco and fills:
            first: dict[str, _Fill] = {}
            for f in sorted(fills, key=lambda x: (x.bar, x.offer.sub)):
                g = f.offer.group or f"{f.offer.decision}:{f.offer.sub}"
                if g in first:
                    counts["oco_cancelled"] += 1
                else:
                    first[g] = f
            fills = sorted(first.values(), key=lambda x: (x.bar, x.offer.sub))
        by_rules: dict[W.Rules, list[_Fill]] = {}
        for f in fills:
            by_rules.setdefault(f.rules, []).append(f)
        dk = str(day_kinds.get(d, "b" if (ctx is not None and ctx.bls) else "n"))
        for er, group in by_rules.items():
            rule, mirr = _walk(o, h, l, c, group, spec.stop_ticks, rr, spec.rules, tick)
            end = int(W.walk_end(o, er) or er.walk_end)
            for k, f in enumerate(group):
                sig = CS.alert_sigma_cross_session(closes, i, int(f.offer.alert), tick=tick)
                if sig is None and spec.execution == "journey":
                    counts["dropped_sigma_lt_2"] += 1          # H4's F4-1 drop, as the naive coin's builder drops it
                    continue
                sig = float("nan") if sig is None else sig      # registered: the table is the registered one, whole
                rec: dict[str, Any] = {"date": d, "day_kind": dk, "decision_slot_minutes": int(f.offer.decision),
                                       "entry_t": int(f.bar), "side_int": int(f.side)}
                move = spec.rules.breakeven
                ax: dict[str, Any] = {"date": d, "entry_t": float(f.bar), "decision_slot_minutes": int(f.offer.decision),
                                      "session": int(i), "time_limit": int(er.walk_end),
                                      "be_open": TB.move_bar(int(f.bar)) if move else None,
                                      "be_vendored": CS.vendored_move_bar(o, int(f.bar), end) if move else None,
                                      "sigma": float(sig), "tag": str(f.offer.tag), "resting": bool(f.resting)}
                for b, R in enumerate(rr):
                    rec[f"_k_{R:g}"] = int(rule["kind"][k, b])
                    rec[f"_x_{R:g}"] = int(rule["exit"][k, b])
                    rec[f"_a_{R:g}"] = int(rule["mae"][k, b])
                    rec[f"_g_{R:g}"] = int(rule["gross"][k, b])
                    ax[f"mirr_g_{R:g}"] = float(mirr["gross"][k, b])
                    ax[f"rule_g_{R:g}"] = float(rule["gross"][k, b])
                rows.append(rec)
                aux_rows.append(ax)
                counts["filled"] += 1
    trades = CS._format_cell_trades(rows, spec.stop_ticks, rr, fresh_rr, fee_micro_eq, tick_value, entry_ticks)
    if aux_rows:
        aux = pd.DataFrame(aux_rows).sort_values(["date", "entry_t", "decision_slot_minutes"], kind="stable")
        aux = aux.sort_values(["date", "entry_t"], kind="stable").reset_index(drop=True)
    else:
        aux = pd.DataFrame()
    counts["refused"] = dict(sorted(counts["refused"].items()))
    counts["unfilled"] = dict(sorted(counts["unfilled"].items()))
    counts["entry_ticks"] = entry_ticks
    return DesignTrades(trades, aux, counts)


def facts_for(trades: pd.DataFrame, aux: pd.DataFrame, dates: Sequence[str], *, tick_value: float,
              rr_cols: Sequence[float], entry_ticks: float) -> dict[tuple[int, int], TB.TradeFacts]:
    """`three_way_baseline.TradeFacts` for every trade, keyed (block day index, index within the day) in the order
    `score_fv3_grid.gate_blocks` builds the blocks (date, then entry), the move bar from the aux frame (None for a walk
    without the move), the walked and mirror gross ticks at every R (beside only)."""
    if len(trades) != len(aux):
        raise DesignRefused("the trades and the aux frame differ in length")
    if len(trades) and (list(trades["date"].astype(str)) != list(aux["date"].astype(str))
                        or not np.array_equal(trades["entry_t"].to_numpy(float), aux["entry_t"].to_numpy(float))):
        raise DesignRefused("the aux frame is not row for row with the trades")
    at = {str(d): i for i, d in enumerate(dates)}
    facts: dict[tuple[int, int], TB.TradeFacts] = {}
    per_day: dict[int, int] = {}
    for p in range(len(trades)):
        r, a = trades.iloc[p], aux.iloc[p]
        di = at[str(r["date"])]
        j = per_day.get(di, 0)
        per_day[di] = j + 1
        ent = int(round(float(r["entry_t"])))
        S = int(r["S"])
        be = a["be_open"]
        be = None if (be is None or (isinstance(be, float) and math.isnan(be))) else int(be)
        bv = a["be_vendored"]
        bv = None if (bv is None or (isinstance(bv, float) and math.isnan(bv))) else int(bv)
        lim = max(ent, int(a["time_limit"]))
        kinds, walked, mirror = {}, {}, {}
        for R in rr_cols:
            code = str(r[f"o_{R:g}"])
            if code not in TB.KINDS:
                raise DesignRefused(f"exit kind {code!r} at R {R:g} is not one of {TB.KINDS}")
            kinds[float(R)] = code
            walked[float(R)] = float(r[f"g_{R:g}"]) * S
            mirror[float(R)] = float(a[f"mirr_g_{R:g}"])
        facts[(di, j)] = TB.TradeFacts(
            decision=int(r["decision_slot_minutes"]), entry=ent, stop_ticks=S, tick_value=float(tick_value),
            kinds=kinds, limit=lim, sigma=float(a["sigma"]), be_open=be, be_vendored=bv, e_ticks=float(entry_ticks),
            xt_ticks=float(W.EXIT_TICKS[W.TARGET]), xs_ticks=float(W.EXIT_TICKS[W.STOP]),
            xf_ticks=float(W.EXIT_TICKS[W.FLATTEN]), fee_per_contract=float(r["fee_micro_eq"]), walked=walked,
            walked_mirror=mirror, underlying="NQ")
    return facts


def history_from_arrays(days: Sequence[str], arrays: Mapping[str, tuple[np.ndarray, ...]]) -> T.History:
    """A `triggers.History` from Stage 2's per-day walker arrays (`atlas_a3.bar_arrays`' layout: index the bar's end
    minute, NaN where no bar), days in order; refused past the search years."""
    check_search_days(days)
    if any(b <= a for a, b in zip(days, days[1:])):
        raise DesignRefused("the days are not in order")
    n = {len(arrays[str(d)][0]) for d in days}
    if len(n) != 1:
        raise DesignRefused(f"the day arrays differ in length: {sorted(n)}")
    stack = [np.vstack([np.asarray(arrays[str(d)][k], dtype=float) for d in days]) for k in range(4)]
    return T.History.from_arrays(tuple(str(d) for d in days), tuple("" for _ in days), *stack)


__all__ = ["TASK", "EXECUTIONS", "DesignRefused", "DesignSpec", "rl3_spec", "RegisteredMarks", "registered_spec",
           "DesignTrades", "check_search_days", "build_trades", "facts_for", "history_from_arrays"]
