"""The shared bracket walker (Q-10; bootstrap 6.2): one walk for every family's orders -- a general tool, not one
family's (F-01, which it was first built for, is expected to be withdrawn and re-declared; its words are one preset).

Given one trading day's 1-minute NQ bars and an order, it fills the order (or says why not) and walks the trade at each
R to its stop, its target or the flatten -- for the order's side and for its **mirror** (the opposite side at the same
fill bar, the same stop, targets and rules, booked by `mirror_booking`), the fill bar settled by `fill_bar`. Pure
numpy; nothing here reads a file or Stage 2's tree. `identity/walker_identity.py` holds it to Stage 2's own walk
(`propedge/research/fv3_rung_walk.py`) and to P-16's pinned trades; `tests/test_walker*.py` hold its fill and walk
rules on synthetic bars and its mirror's zero (T-13, `tests/test_walker_t13.py`).

**The clock** is Stage 2's (`collect_core`, `atlas_local.day_arrays`): one trading day's arrays o, h, l, c (NaN where
no bar; index 0 unused), indexed by each bar's **END** minute after 17:00 CT of the evening the day starts -- the bar
stamped with OPEN time hh:mm is index `slot(hh, mm) + 1` (`bar_of`), the bar ending 15:10 CT is `C_FLAT` = 1330. A
time is a `slot` (minutes after 17:00 CT; 17:00 itself is 0). A bar is present when its open is not NaN.

**Orders** (`Order`): `MARKET`, a resting `STOP_ENTRY` or a resting `LIMIT_ENTRY`, a side (+1 buy, -1 sell), the slot
`live` from which it works and, for a resting order, its price (on the tick grid) and an optional `cutoff` slot.

* It can fill only on a bar opening at or after `live` (index >= live + 1) and closing at or before `cutoff` (index <=
  cutoff), and before the walk's last bar (index < the walk's end) -- a position is never opened on the bar it would be
  flattened on (Stage 2's `entries`: no entry at or after the bar ending 15:08 CT under `STAGE2`).
* **market**: the open of the first present bar in that window (Stage 2's entry: `fast_walk.entry_bar` at delay 0, the
  first bar opening at or after the mark). No slippage in the price; its tick is a cost (`Costs`), as Stage 2 charges.
* **stop**: the first bar trading at its price (a buy stop: high >= price; a sell stop: low <= price) fills at the price
  plus `slip_ticks` (one tick, Stage 2 `config/atlas_a3.yaml` `slip_ticks`) in the order's direction -- or, when that
  bar OPENS beyond the price (a gap through), at the open plus the slippage (`Fill.gap`).
* **limit**: fills only on a bar trading **through** its price by at least a tick (a buy limit: low <= price - tick),
  at the limit price, never better (also when a bar opens through it). A bar reaching the price without trading through
  is a touch, not a fill (`Fill.touch_bar` is the first touch, filled or not: F-01's K4 reads touches against fills).
* **void** (`Fill.status` 'void'): a stop already at or through its price, or a limit already at or beyond its price
  (marketable), at `live` -- the price at `live` being the close of the last bar closed by then (`price_at`: the bar
  ending at `live` or the last earlier one; feature-rules 1). With no bar closed by `live` the ticket is void too
  ('no_reference').
* **cancelled**: no fill in the window ('cutoff' when the cutoff closed it, 'end' when the walk's end did).
* **one fill**: an order fills at most once; nothing re-arms it.
* **the trigger** (`Fill.trigger`): the first price the bars show trading at the fill condition -- a stop's price on a
  touch, the open on a gap; a tick through a limit's price, or the open when the bar opens through it; a market fill's
  open. The rule's fill is the trigger plus its offset: a stop's slippage, a limit's tick (it fills at its price while
  the market trades a tick through), nothing at the market.

**The walk** (`walk`, vectorised over a day's fills): from the fill bar to the walk's end (`Rules.walk_end`, or the
day's last bar if earlier), every present bar, excursions in whole ticks (`round(x / tick)`), stop and targets from the
fill price: the stop at S ticks against is **reached** (a touch), the target at floor(R x S) ticks (Stage 2's rounding,
`target_ticks`) needs a trade **through** it (a resting limit's fill: at least a tick beyond); a bar on which both
happen is the **stop's**. A market fill's bar is walked whole (the fill is at its open). On a **resting** fill's own
bar the order of its prices is unknown, so (F-01 section 3) **a stop touch on the fill bar is a loss and a target touch
there is not counted**. A trade reaching neither is flattened (`FLATTEN`, unresolved) by `Rules.flatten`. Kinds are
Stage 2's codes: 0 stop, 1 target, 2 flatten, 3 breakeven (`KIND_CODE` s / t / f / b). MAE (ticks) is the stop on a
stop, the running worst to the exit bar on a target or a breakeven, the whole walk's on a flatten. The exit bar of a
flatten is `Rules.walk_end`.

**Costs** (`Costs`, `cost_r`, `net_r`): Stage 2's arithmetic (`resolved_coin.cell_trades`, `atlas_a3.cell_trades`,
FV3's `Signals3.outcome`) -- in R at the stop, (entry ticks x tick value + the fee a micro-equivalent pays at the stop
+ exit ticks x tick value) / (S x tick value), the fee from `atlas_a3.fee_by_stop` (FV3-C's model at the fresh
Combine's size, the round turns of `config/fills.yaml`'s assumed model -- passed in, since it is Stage 2's engine's to
compute), exit ticks by kind `EXIT_TICKS`: a tick on a stop or a breakeven, none at a target (a limit), two on a
flatten. Entry ticks: one on a market fill (Stage 2's), none on a resting fill (a stop's slippage is in its fill price;
a limit has none).

**Rules** -- two presets, because F-01's words and Stage 2's walk differ in three places (the identity runs `STAGE2`;
F-01's build uses `DECLARED_F01`; the lead decides any change, under a decision row):

| | `STAGE2` (`fv3_rung_walk`, P-16's trades) | `DECLARED_F01` (F-01 section 3's words) |
|---|---|---|
| walk's last bar | the bar ending 15:08 CT (`FLAT_ENTRY`, 1328) | the bar ending 15:10 CT (`C_FLAT`, 1330) |
| flatten price | the worst of the bars ending 15:08-15:10 less two ticks (else the last close by 15:08) | the close of the last bar by 15:10 |
| breakeven | FV3's: at the next session open (17:00, 19:00, 08:30, 13:00 CT; its first bar within five minutes), if that open is a tick or more in favour and the trade still open, the stop moves to the entry; a later touch exits at zero ('b'), unless the target trades through on an earlier bar (a bar touching both is the target's) | none (the declared walk names no stop move) |

Common to both: the stop reached by a touch, the target by a trade through, the stop first on a two-barrier bar, a stop
booked at exactly S ticks (no gap beyond it is charged -- Stage 2's convention; F-01 is silent), the costs above with
the flatten's two exit ticks (under `STAGE2` the flatten is thus charged two ticks in its price and two in its cost, as
FV3's scorer does). The fill-bar rule applies only to resting fills, which Stage 2 never walked.

**The mirror and the fill bar: two parameters** (the lead's change of 2026-11-15, from the Phase 0 audit's D-1 and
D-13; `walk_pair`, `mirror_price`, `trade`):

* `fill_bar="declared"` -- F-01's words, per trade: on a resting fill's bar a stop touch is a loss, a target touch not
  counted. Part of that bar traded before the fill (a buy stop's bar rose through the stop from below, so its low is
  mostly pre-fill; a sell limit's bar rose to the level), so this charges the side trading in the bar's direction (a
  stop entry's rule side; a limit entry's mirror) a pre-fill adverse move its opposite is not: conservative for each
  trade alone, not side-neutral (D-1).
* `fill_bar="pair"` -- for a rule/mirror pair: if a resting fill's bar **touches** either trade's stop or target (at a
  bracket), the pair is ambiguous there -- both settled as losses (`AMBIGUOUS`, code 'a': gross -S, exit the fill bar,
  MAE S, costed as a stopped trade), zero lift, counted (`Trade.ambiguous`, `walk_pair`'s 'ambiguous'); otherwise both
  are walked from the next bar, the fill bar unread.
* `mirror_booking="rule_fill"` -- the mirror at the rule's fill price (F-01's words): it starts the rule's offset ahead
  of the rule (a tick for a stop's slippage or a limit's trade-through; more where prices skip past the trigger, D-13).
* `mirror_booking="symmetric"` -- the mirror reflected about the trigger (2 x trigger - the rule's fill), paying the
  rule's offset in its own direction.

On a tick-continuous driftless walk `pair` + `symmetric` is side-neutral by construction (the four barriers lie
symmetric about the trigger) and `declared` + `rule_fill` is not; T-13 holds both (`tests/test_walker_t13.py`). Market
fills are walked whole in every mode and both bookings put their mirror at the open.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np

# ------------------------------------------------------------------------------------------------ the clock and constants

TICK = 0.25                               # NQ / MNQ
SLIP_TICKS = 1                            # Stage 2 config/atlas_a3.yaml `slip_ticks` (one tick adverse at entry, D-95)
C_FLAT = 22 * 60 + 10                     # 1330: the bar ending 15:10 CT (Stage 2 `collect_core.C_FLAT`)
FLAT_ENTRY = C_FLAT - 2                   # 1328: the bar ending 15:08 CT (Stage 2 `orb_core.FLAT_ENTRY`)
FLATTEN_BARS = (FLAT_ENTRY, FLAT_ENTRY + 1, FLAT_ENTRY + 2)       # Stage 2 `fv3_core.FLATTEN_BARS`
SESSION_OPENS = (0, 120, 930, 1200)       # FV3's sessions: 17:00, 19:00, 08:30, 13:00 CT (`fv3_core.SESSIONS`)
BREAKEVEN_WINDOW = 5                      # the session's first bar within five minutes of its open (`fv3_core.next_open`)
NONE = -1
STOP, TARGET, FLATTEN, BREAKEVEN = 0, 1, 2, 3          # Stage 2's kinds (`fv3_rung_walk`)
AMBIGUOUS = 4                                           # the pair rule's: the fill bar touched a barrier of the pair
KIND_CODE = {STOP: "s", TARGET: "t", FLATTEN: "f", BREAKEVEN: "b", AMBIGUOUS: "a"}
STOP_EXIT_TICKS, FLATTEN_SLIP_TICKS = 1, 2
EXIT_TICKS = {STOP: STOP_EXIT_TICKS, TARGET: 0, FLATTEN: FLATTEN_SLIP_TICKS, BREAKEVEN: STOP_EXIT_TICKS,
              AMBIGUOUS: STOP_EXIT_TICKS}
MARKET, STOP_ENTRY, LIMIT_ENTRY = "market", "stop", "limit"
ORDER_KINDS = (MARKET, STOP_ENTRY, LIMIT_ENTRY)
FILL_BAR_MODES = ("declared", "pair")
MIRROR_BOOKINGS = ("rule_fill", "symmetric")
EPS = 1e-6                                # price comparisons (prices are on the 0.25 grid)


def slot(hour: int, minute: int) -> int:
    """A CT time on the trading-day clock: minutes after 17:00 CT of the evening the trading day starts (17:00 is 0).
    Equal to Stage 2's `collect_core.c_slot` at every time but 17:00 itself (which `c_slot`, a bar END time, maps to
    1440: the previous day's last bar)."""
    m = int(hour) * 60 + int(minute)
    return m - 1020 if m >= 1020 else m + 420


def bar_of(hour: int, minute: int) -> int:
    """The index of the bar stamped (OPENING at) hh:mm CT: it closes a minute later."""
    return slot(hour, minute) + 1


def target_ticks(R: float, stop: int) -> int:
    """The target in ticks as Stage 2 rounds it (`fv3_rung_walk.target_ticks`): floor(R x stop + 1e-9)."""
    return int(math.floor(float(R) * int(stop) + 1e-9))


def brackets(stops: Sequence[int], rrs: Sequence[float]) -> list[tuple[int, float, int]]:
    """[(stop ticks, R, target ticks)], stop by stop, R in the given order (Stage 2's `fv3_rung_walk.brackets`)."""
    return [(int(S), float(R), target_ticks(R, S)) for S in stops for R in rrs]


# ------------------------------------------------------------------------------------------------ the rules


@dataclass(frozen=True)
class Rules:
    """How a walk ends (see the module docstring's table). `walk_end`: the last bar a position is held to (a slot
    index); `flatten`: 'close' (the close of the last bar by `walk_end`) or 'worst_less_two' (Stage 2's: the worst of
    `FLATTEN_BARS` less two ticks, else the last close by the walk's end); `breakeven`: Stage 2's FV3 stop move."""

    name: str
    walk_end: int
    flatten: str
    breakeven: bool

    def __post_init__(self) -> None:
        if self.flatten not in ("close", "worst_less_two"):
            raise ValueError(f"unknown flatten rule {self.flatten!r}")
        if not 1 <= int(self.walk_end) <= C_FLAT:
            raise ValueError(f"walk_end {self.walk_end} is not a bar of the trading day (1..{C_FLAT})")


STAGE2 = Rules("stage2_fv3", FLAT_ENTRY, "worst_less_two", True)
DECLARED_F01 = Rules("f01_declared", C_FLAT, "close", False)


# ------------------------------------------------------------------------------------------------ orders and fills


@dataclass(frozen=True)
class Order:
    """`kind` MARKET / STOP_ENTRY / LIMIT_ENTRY; `side` +1 buy, -1 sell; `live` the slot it works from (fills on bars
    opening at or after it); `price` a resting order's stop or limit price (on the tick grid); `cutoff` the slot at
    which an unfilled order is cancelled (fills only on bars closing at or before it), None for none."""

    kind: str
    side: int
    live: int
    price: float | None = None
    cutoff: int | None = None

    def __post_init__(self) -> None:
        if self.kind not in ORDER_KINDS:
            raise ValueError(f"unknown order kind {self.kind!r}; one of {ORDER_KINDS}")
        if int(self.side) not in (1, -1):
            raise ValueError(f"side {self.side} is not +1 or -1")
        if self.kind != MARKET and (self.price is None or not math.isfinite(float(self.price))):
            raise ValueError(f"a {self.kind} order needs a price")


@dataclass(frozen=True)
class Fill:
    """What became of an order: `status` 'filled', 'void' or 'cancelled'; `reason` '' (filled), 'through' or
    'no_reference' (void), 'cutoff' or 'end' (cancelled); the fill `bar` (NONE unless filled) and `price` (NaN unless
    filled); `gap` a stop filled at the open of a bar opening beyond it; `resting` a stop or limit fill (the fill-bar
    rule applies); `touch_bar` a limit's first bar at its price, filled or not (a stop's fill bar; a market fill's bar);
    `reference` the price at live (`price_at`); `trigger` the first price the bars show trading at the order's fill
    condition -- a stop's price on a touch or the bar's open on a gap, a tick through a limit's price (or the open
    when the bar opens through it), a market fill's open -- NaN unless filled (the mirror's symmetric booking is
    reflected about it: `mirror_price`)."""

    status: str
    reason: str
    bar: int
    price: float
    gap: bool
    resting: bool
    touch_bar: int
    reference: float
    trigger: float = float("nan")


def _arrays(o, h, l, c) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    return tuple(np.asarray(x, dtype=float) for x in (o, h, l, c))      # type: ignore[return-value]


def last_bar(o) -> int | None:
    """The day's last present bar at or before 15:10 CT (Stage 2's `fast_walk.last_bar(o, C_FLAT)`), or None."""
    o = np.asarray(o, dtype=float)
    idx = np.flatnonzero(~np.isnan(o[: min(C_FLAT, len(o) - 1) + 1]))
    idx = idx[idx >= 1]
    return int(idx[-1]) if idx.size else None


def walk_end(o, rules: Rules) -> int | None:
    """The walk's last bar on this day: `rules.walk_end`, or the day's last bar if earlier; None on a day with no bar."""
    last = last_bar(o)
    return None if last is None else min(last, int(rules.walk_end))


def price_at(o, c, t: int) -> float:
    """The price at slot t: the close of the last present bar closed by t (index <= t), NaN if none."""
    o, c = np.asarray(o, dtype=float), np.asarray(c, dtype=float)
    hi = min(int(t), len(o) - 1)
    if hi < 1:
        return float("nan")
    idx = np.flatnonzero(~np.isnan(o[1: hi + 1]))
    return float(c[int(idx[-1]) + 1]) if idx.size else float("nan")


def _on_grid(price: float, tick: float) -> None:
    q = float(price) / float(tick)
    if abs(q - round(q)) > 1e-6:
        raise ValueError(f"price {price} is not on the {tick} tick grid")


def _window(o: np.ndarray, order: Order, end: int) -> tuple[np.ndarray, str]:
    """The present bars an order may fill on, and the reason it would be cancelled at the window's close."""
    hi, why = end - 1, "end"
    if order.cutoff is not None and int(order.cutoff) < hi:
        hi, why = int(order.cutoff), "cutoff"
    lo = int(order.live) + 1
    if hi < lo:
        return np.zeros(0, dtype=int), why
    js = np.arange(lo, hi + 1)
    return js[~np.isnan(o[js])], why


def fill_order(order: Order, o, h, l, c, *, tick: float = TICK, slip_ticks: float = SLIP_TICKS,
               rules: Rules = DECLARED_F01) -> Fill:
    """The order on one day's bars (the module docstring's fill rules)."""
    o, h, l, c = _arrays(o, h, l, c)
    resting = order.kind != MARKET
    ref = price_at(o, c, int(order.live))
    nan = float("nan")
    end = walk_end(o, rules)
    if end is None:
        return Fill("cancelled", "end", NONE, nan, False, resting, NONE, ref)
    js, why = _window(o, order, end)
    if order.kind == MARKET:
        if not js.size:
            return Fill("cancelled", why, NONE, nan, False, False, NONE, ref)
        j = int(js[0])
        return Fill("filled", "", j, float(o[j]), False, False, j, ref, float(o[j]))
    P, d = float(order.price), int(order.side)
    _on_grid(P, tick)
    if math.isnan(ref):
        return Fill("void", "no_reference", NONE, nan, False, True, NONE, ref)
    if order.kind == STOP_ENTRY:
        through = ref >= P - EPS if d > 0 else ref <= P + EPS
    else:
        through = ref <= P + EPS if d > 0 else ref >= P - EPS
    if through:
        return Fill("void", "through", NONE, nan, False, True, NONE, ref)
    if order.kind == STOP_ENTRY:
        hit = h[js] >= P - EPS if d > 0 else l[js] <= P + EPS
        if not hit.any():
            return Fill("cancelled", why, NONE, nan, False, True, NONE, ref)
        j = int(js[int(np.argmax(hit))])
        gap = d * (o[j] - P) > EPS
        x = float(o[j]) if gap else P
        return Fill("filled", "", j, x + d * float(slip_ticks) * float(tick), bool(gap), True, j, ref, x)
    touch = l[js] <= P + EPS if d > 0 else h[js] >= P - EPS
    thru = l[js] <= P - tick + EPS if d > 0 else h[js] >= P + tick - EPS
    tb = int(js[int(np.argmax(touch))]) if touch.any() else NONE
    if not thru.any():
        return Fill("cancelled", why, NONE, nan, False, True, tb, ref)
    j = int(js[int(np.argmax(thru))])
    through = P - d * float(tick)
    x = float(o[j]) if d * (through - o[j]) > -EPS else through          # opened at or beyond a tick through
    return Fill("filled", "", j, P, False, True, tb, ref, x)


def market_fill_bars(o, lives, *, rules: Rules = DECLARED_F01) -> np.ndarray:
    """Vectorised market fills (no cutoff): for each live slot the first present bar opening at or after it and before
    the walk's end, NONE where there is none -- `fill_order(Order(MARKET, ...))`'s bar, for many orders at once."""
    o = np.asarray(o, dtype=float)
    lives = np.asarray(lives, dtype=int)
    end = walk_end(o, rules)
    if end is None:
        return np.full(lives.shape, NONE)
    n = len(o)
    nxt = np.full(n + 1, NONE)
    for j in range(end - 1, 0, -1):            # the next present bar at or after j, below the walk's end
        nxt[j] = j if not np.isnan(o[j]) else nxt[j + 1]
    first = np.clip(lives + 1, 0, n)
    out = np.where(first < end, nxt[np.minimum(first, n)], NONE)
    return np.where(first >= 1, out, NONE)


# ------------------------------------------------------------------------------------------------ the walk


def walk(o, h, l, c, fill_bars, fill_prices, sides, resting, bracket_list, *, tick: float = TICK,
         rules: Rules = DECLARED_F01, from_next=False) -> dict[str, np.ndarray]:
    """Every fill (bar, price, side, resting) walked at every bracket of `bracket_list` [(S, R, T)]: 'kind', 'exit'
    (bar), 'mae' (ticks) and 'gross' (ticks), each of shape (fills, brackets), int32 (Stage 2's walk frame's types).
    `resting` fills take the declared fill-bar rule (a stop touch on the fill bar counts, a target touch does not);
    `from_next` fills (the pair rule's clean pairs, `walk_pair`) are walked from the bar after the fill bar, which is
    not read at all; other fills are walked from their fill bar whole (a market fill at its open)."""
    o, h, l, c = _arrays(o, h, l, c)
    je = np.asarray(fill_bars, dtype=int).reshape(-1)
    e = np.asarray(fill_prices, dtype=float).reshape(-1)
    d = np.asarray(sides, dtype=float).reshape(-1)
    nxt = np.broadcast_to(np.asarray(from_next, dtype=bool), je.shape)
    rest = np.broadcast_to(np.asarray(resting, dtype=bool), je.shape) & ~nxt
    bl = list(bracket_list)
    Wn, B, n = len(je), len(bl), len(o)
    out = {k: np.zeros((Wn, B), dtype=np.int32) for k in ("kind", "exit", "mae", "gross")}
    if Wn == 0:
        return out
    if not (len(e) == len(d) == Wn):
        raise ValueError("fill bars, prices and sides differ in length")
    end = walk_end(o, rules)
    if end is None:
        raise ValueError("a day with no bar has no fill")
    if (je < 1).any() or (je >= end).any() or np.isnan(o[je]).any():
        raise ValueError("a fill before the first bar, at or after the walk's end, or on a bar with no open")
    J = np.arange(n)
    present = ~np.isnan(o)
    live = present[None, :] & (J[None, :] >= (je + nxt)[:, None]) & (J[None, :] <= end)
    long = d[:, None] > 0
    with np.errstate(invalid="ignore"):
        fav = np.where(long, h[None, :] - e[:, None], e[:, None] - l[None, :])
        adv = np.where(long, e[:, None] - l[None, :], h[None, :] - e[:, None])
        fav = np.where(live, np.round(fav / tick), -np.inf)
        adv = np.where(live, np.round(adv / tick), -np.inf)
    rows = np.arange(Wn)
    if rest.any():                             # the fill-bar rule: a resting fill's target is not counted on its bar
        fav[rows[rest], je[rest]] = -np.inf
    rmf = np.maximum.accumulate(fav, axis=1)
    rma = np.maximum.accumulate(adv, axis=1)

    def first(rm: np.ndarray, thr: float, strict: bool) -> np.ndarray:
        m = rm > thr if strict else rm >= thr
        k = m.argmax(axis=1)
        return np.where(m[rows, k], k, NONE)

    def mae_at(j: np.ndarray) -> np.ndarray:
        return np.maximum(0.0, rma[rows, np.where(j >= 0, j, n - 1)])

    # the flatten's move
    jc = next((j for j in range(min(end, n - 1), 0, -1) if not np.isnan(c[j])), None)
    with np.errstate(invalid="ignore"):
        close = np.round(d * (c[jc] - e) / tick) if jc is not None else np.zeros(Wn)
    if rules.flatten == "worst_less_two":
        fb = [j for j in FLATTEN_BARS if j < n]
        with np.errstate(invalid="ignore"):
            wv = (np.stack([np.where(d > 0, l[j] - e, e - h[j]) for j in fb], axis=1) if fb
                  else np.full((Wn, 1), np.nan))
        has_w = ~np.isnan(wv).all(axis=1)
        worst = np.where(has_w, np.round(np.min(np.where(np.isnan(wv), np.inf, wv), axis=1) / tick), np.nan)
        flat_move = np.where(has_w, worst - FLATTEN_SLIP_TICKS, close)
    else:
        flat_move = close
    # FV3's breakeven (STAGE2 only)
    if rules.breakeven:
        jn = np.full(Wn, NONE)
        for u in np.unique(je):
            s = next((s for s in SESSION_OPENS if s > u), None)
            if s is None:
                continue
            xs = [x for x in range(s + 1, min(s + 1 + BREAKEVEN_WINDOW, end + 1)) if present[x]]
            if xs:
                jn[je == u] = xs[0]
        has_jn = jn != NONE
        with np.errstate(invalid="ignore"):
            be_fav = np.where(has_jn, np.round(d * (o[np.where(has_jn, jn, 0)] - e) / tick), 0.0)
            reach = np.where(long, l[None, :] <= e[:, None], h[None, :] >= e[:, None])
        touch_m = (present[None, :] & (J[None, :] >= jn[:, None]) & (J[None, :] <= end) & has_jn[:, None] & reach)
        k = touch_m.argmax(axis=1)
        touch = np.where(touch_m[rows, k], k, NONE)
        be_ok = has_jn & (be_fav > 0)
    mae_all = mae_at(np.full(Wn, n - 1))
    stops_at: dict[int, np.ndarray] = {}
    targets_at: dict[int, np.ndarray] = {}
    for b, (S, _R, T) in enumerate(bl):
        if S not in stops_at:
            stops_at[S] = first(rma, S, strict=False)
        if T not in targets_at:
            targets_at[T] = first(rmf, T, strict=True)
        ja, js = stops_at[S], targets_at[T]
        stop = (ja != NONE) & ((js == NONE) | (ja <= js))
        tgt = ~stop & (js != NONE)
        off = np.where(stop, ja, np.where(tgt, js, NONE))
        kind = np.where(stop, STOP, np.where(tgt, TARGET, FLATTEN))
        ex = np.where(off != NONE, off, int(rules.walk_end))
        mae = np.where(stop, float(S), np.where(tgt, mae_at(js), mae_all))
        if rules.breakeven:
            app = be_ok & ((off == NONE) | (jn < off))
            bt = app & (touch != NONE) & ((js == NONE) | (touch < js))
            btg = app & ~bt & (js != NONE)
            bop = app & ~bt & ~btg
            kind = np.where(bt, BREAKEVEN, np.where(btg, TARGET, np.where(bop, FLATTEN, kind)))
            ex = np.where(bt, touch, np.where(btg, js, np.where(bop, int(rules.walk_end), ex)))
            mae = np.where(bt, mae_at(touch), np.where(btg, mae_at(js), np.where(bop, mae_all, mae)))
        gross = np.select([kind == STOP, kind == TARGET, kind == BREAKEVEN], [-float(S), float(T), 0.0], flat_move)
        out["kind"][:, b] = kind
        out["exit"][:, b] = ex
        out["mae"][:, b] = mae
        out["gross"][:, b] = gross
    return out


# ------------------------------------------------------------------------------------------------ costs


@dataclass(frozen=True)
class Costs:
    """Stage 2's per-trade costs: `fee_micro_eq` the fee a micro-equivalent pays at the trade's stop
    (`atlas_a3.fee_by_stop`), `tick_value` MNQ's $0.50, `market_entry_ticks` the tick a market fill pays (Stage 2's
    `slip_ticks` charged as a cost; a resting fill pays none -- its slippage, if any, is in its price)."""

    fee_micro_eq: float
    tick_value: float = 0.5
    market_entry_ticks: float = float(SLIP_TICKS)

    def entry_ticks(self, order_kind: str) -> float:
        return float(self.market_entry_ticks) if order_kind == MARKET else 0.0


def cost_r(kind, stop_ticks: int, *, entry_ticks: float, costs: Costs) -> np.ndarray:
    """The cost in R at the stop: (entry ticks x tv + fee + exit ticks x tv) / (S x tv), in Stage 2's order of
    operations (`resolved_coin.cell_trades`), so the result is Stage 2's to the bit."""
    k = np.asarray(kind)
    ex = np.array([float(EXIT_TICKS[int(x)]) for x in k.reshape(-1)]).reshape(k.shape)
    td = float(costs.tick_value)
    return (float(entry_ticks) * td + float(costs.fee_micro_eq) + ex * td) / (int(stop_ticks) * td)


def net_r(gross_ticks, kind, stop_ticks: int, *, entry_ticks: float, costs: Costs) -> np.ndarray:
    """The net outcome in R: gross ticks / S less `cost_r` (Stage 2's `r_` column)."""
    return (np.asarray(gross_ticks, dtype=float) / int(stop_ticks)
            - cost_r(kind, stop_ticks, entry_ticks=entry_ticks, costs=costs))


# ------------------------------------------------------------------------------------------------ the mirror and the pair


def mirror_price(fill: Fill, mirror_booking: str = "rule_fill") -> float:
    """The mirror's booking price: 'rule_fill' -- the rule's own fill price (F-01's words); 'symmetric' -- reflected
    about the trigger price, 2 x trigger - fill, so the mirror pays the rule's offset from the trigger in its own
    direction (the Phase 0 audit's D-13: a break's mirror sells a tick below the stop's price; a fade's mirror buys a
    tick above the print a tick through the limit). A market fill's trigger is its fill: both modes book the open."""
    if mirror_booking not in MIRROR_BOOKINGS:
        raise ValueError(f"unknown mirror booking {mirror_booking!r}; one of {MIRROR_BOOKINGS}")
    if mirror_booking == "rule_fill" or math.isnan(fill.trigger):
        return float(fill.price)
    return 2.0 * float(fill.trigger) - float(fill.price)


def walk_pair(o, h, l, c, fill_bars, rule_prices, mirror_prices, sides, resting, bracket_list, *,
              tick: float = TICK, rules: Rules = DECLARED_F01, fill_bar: str = "declared") -> dict[str, np.ndarray]:
    """Each fill's rule trade (side `sides`, at `rule_prices`) and its mirror (the opposite side at `mirror_prices`, the
    same fill bar, stop, targets and rules), settled on the fill bar by `fill_bar`:

    * 'declared' -- F-01's rule, per trade: on a resting fill's bar a stop touch is a loss, a target touch not counted;
    * 'pair' -- the audit's D-1 repair, per pair and bracket: if a resting fill's bar TOUCHES either trade's stop or
      target, the pair is ambiguous at that bracket and both trades are settled as losses (`AMBIGUOUS`: gross -S, exit
      the fill bar, MAE S; zero lift, counted); otherwise both are walked from the next bar (the fill bar unread).

    Market fills (not resting) are walked from their bar whole in both modes. Returns 'rule' and 'mirror' (each
    `walk`'s dict) and 'ambiguous' (fills x brackets, bool; all False under 'declared')."""
    if fill_bar not in FILL_BAR_MODES:
        raise ValueError(f"unknown fill-bar mode {fill_bar!r}; one of {FILL_BAR_MODES}")
    o, h, l, c = _arrays(o, h, l, c)
    je = np.asarray(fill_bars, dtype=int).reshape(-1)
    d = np.asarray(sides, dtype=float).reshape(-1)
    er = np.asarray(rule_prices, dtype=float).reshape(-1)
    em = np.asarray(mirror_prices, dtype=float).reshape(-1)
    rest = np.broadcast_to(np.asarray(resting, dtype=bool), je.shape)
    bl = list(bracket_list)
    if fill_bar == "declared":
        r = walk(o, h, l, c, je, er, d, rest, bl, tick=tick, rules=rules)
        m = walk(o, h, l, c, je, em, -d, rest, bl, tick=tick, rules=rules)
        return {"rule": r, "mirror": m, "ambiguous": np.zeros((len(je), len(bl)), dtype=bool)}
    r = walk(o, h, l, c, je, er, d, False, bl, tick=tick, rules=rules, from_next=rest)
    m = walk(o, h, l, c, je, em, -d, False, bl, tick=tick, rules=rules, from_next=rest)
    amb = np.zeros((len(je), len(bl)), dtype=bool)
    if rest.any() and len(bl):
        hj, lj = h[je], l[je]
        with np.errstate(invalid="ignore"):
            # each trade's excursions on the fill bar, in ticks, for its own side (the mirror's side is -d)
            fav_r = np.round(np.where(d > 0, hj - er, er - lj) / tick)
            adv_r = np.round(np.where(d > 0, er - lj, hj - er) / tick)
            fav_m = np.round(np.where(d > 0, em - lj, hj - em) / tick)
            adv_m = np.round(np.where(d > 0, hj - em, em - lj) / tick)
        for b, (S, _R, T) in enumerate(bl):
            amb[:, b] = rest & ((adv_r >= S) | (fav_r >= T) | (adv_m >= S) | (fav_m >= T))
        for res in (r, m):
            for b, (S, _R, _T) in enumerate(bl):
                a = amb[:, b]
                res["kind"][a, b] = AMBIGUOUS
                res["gross"][a, b] = -int(S)
                res["exit"][a, b] = je[a]
                res["mae"][a, b] = int(S)
    return {"rule": r, "mirror": m, "ambiguous": amb}


# ------------------------------------------------------------------------------------------------ one order, both sides


@dataclass(frozen=True)
class Outcome:
    """One side's walk at each R (arrays over R): kind, exit bar, MAE and gross in ticks; `net_r` when costs are given."""

    kind: np.ndarray
    exit: np.ndarray
    mae: np.ndarray
    gross: np.ndarray
    net_r: np.ndarray | None

    @property
    def win(self) -> np.ndarray:
        return self.kind == TARGET

    @property
    def unresolved(self) -> np.ndarray:
        return self.kind == FLATTEN

    @property
    def ambiguous(self) -> np.ndarray:
        return self.kind == AMBIGUOUS


@dataclass(frozen=True)
class Trade:
    """An order's fill and, when it filled, its walk (`rule`) and its mirror's (`mirror`, booked at `mirror_price`) at
    each R of `rrs`; `ambiguous` the pair rule's mark by R (all False under the declared fill-bar rule); the modes."""

    order: Order
    fill: Fill
    stop_ticks: int
    rrs: tuple[float, ...]
    rule: Outcome | None
    mirror: Outcome | None
    mirror_price: float = float("nan")
    ambiguous: np.ndarray | None = None
    fill_bar: str = "declared"
    mirror_booking: str = "rule_fill"


def trade(order: Order, o, h, l, c, stop_ticks: int, rrs: Sequence[float], *, rules: Rules = DECLARED_F01,
          costs: Costs | None = None, tick: float = TICK, slip_ticks: float = SLIP_TICKS, fill_bar: str = "declared",
          mirror_booking: str = "rule_fill") -> Trade:
    """Fill one order and walk it and its mirror at the stop and every R (`walk_pair`, `mirror_price`). The mirror pays
    the rule's entry cost (a market fill's tick; none on a resting fill)."""
    if fill_bar not in FILL_BAR_MODES:
        raise ValueError(f"unknown fill-bar mode {fill_bar!r}; one of {FILL_BAR_MODES}")
    if mirror_booking not in MIRROR_BOOKINGS:
        raise ValueError(f"unknown mirror booking {mirror_booking!r}; one of {MIRROR_BOOKINGS}")
    S, rr = int(stop_ticks), tuple(float(R) for R in rrs)
    f = fill_order(order, o, h, l, c, tick=tick, slip_ticks=slip_ticks, rules=rules)
    if f.status != "filled":
        return Trade(order, f, S, rr, None, None, fill_bar=fill_bar, mirror_booking=mirror_booking)
    mp = mirror_price(f, mirror_booking)
    res = walk_pair(o, h, l, c, [f.bar], [f.price], [mp], [int(order.side)], [f.resting], brackets((S,), rr),
                    tick=tick, rules=rules, fill_bar=fill_bar)
    sides = []
    for key in ("rule", "mirror"):
        x = res[key]
        k = x["kind"][0]
        nr = (net_r(x["gross"][0], k, S, entry_ticks=costs.entry_ticks(order.kind), costs=costs)
              if costs is not None else None)
        sides.append(Outcome(k, x["exit"][0], x["mae"][0], x["gross"][0], nr))
    return Trade(order, f, S, rr, sides[0], sides[1], mp, res["ambiguous"][0], fill_bar, mirror_booking)


__all__ = ["TICK", "SLIP_TICKS", "C_FLAT", "FLAT_ENTRY", "FLATTEN_BARS", "SESSION_OPENS", "NONE", "STOP", "TARGET",
           "FLATTEN", "BREAKEVEN", "AMBIGUOUS", "KIND_CODE", "EXIT_TICKS", "MARKET", "STOP_ENTRY", "LIMIT_ENTRY",
           "FILL_BAR_MODES", "MIRROR_BOOKINGS", "slot", "bar_of", "target_ticks", "brackets", "Rules", "STAGE2",
           "DECLARED_F01", "Order", "Fill", "last_bar", "walk_end", "price_at", "fill_order", "market_fill_bars",
           "walk", "Costs", "cost_r", "net_r", "mirror_price", "walk_pair", "Outcome", "Trade", "trade"]
