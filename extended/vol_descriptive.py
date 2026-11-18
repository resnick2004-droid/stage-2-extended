"""Q-121 (E-157 (a1); the note `docs/research/volatility_drift_2026-11-17.md` section 4 (a)): a bars-only, side-free
descriptive of NQ's volatility in points and in percent on the **choice block only** (2020-01-02 to 2023-12-29),
by calendar year and quarter. EXPLORATORY and beside: it decides, chooses and carries nothing. No sign, no
target-against-stop split, no win share, no trade of any design.

    from extended import vol_descriptive as V
    V.check_span("2020-01-02", "2023-12-29")            # refuses any day after 2023-12-29 (2024-01-02 included)
    sessions, walks = V.describe(bars, fomc=fomc, bls=bls)  # bars: the store's frame (ts, day, open, high, low, close)
    frame = V.summarise(sessions, walks)                # the result file's rows, every section
    V.output_problems(frame)                            # [] when the frame is this reading's

    a = extended.reader.authorise(..., purpose="volatility_descriptive", declaration="prereg/RD-04_volatility_drift.md")
    V.describe(bars, fomc=fomc, bls=bls, authorised=a)  # RD-04's (a2) only: to a.end, never past 2026-07-16

**The refusal (hard, in code).** Nothing from 2023-12-30 on is described: `check_span` refuses a span reaching past
`LAST_DAY` (the choice block's last day, `extended.reader.CHOICE_END`) before anything is read, and `check_days`
refuses a frame holding any later day before anything is computed (so 2024-01-02, the judged block's first day, is
refused twice). The judged block's descriptive is (a2), a described reading of its own (Q-123, RD-04).

**The one authorisation (Q-121b; the red team's M4 and M5 on RD-04's draft, `docs/reviews/DRAFT_RD-04_2026-11-17.md`).**
`check_span`, `check_days`, `describe`, `summarise` and `output_problems` take an optional `authorised`, a reader
`extended.reader.Authorisation`. **Absent**, every behaviour is the module's before Q-121b (a0cb1ce): the last day is
`LAST_DAY`, the choice block's. **Present**, it is checked first (`check_authorisation`), before the call touches its
input: it is accepted only as a judged-block read (`judged`, the judged block among its `blocks`, `ledgered`, a
declaration sha256) of kind `described_reading` for the purpose `volatility_descriptive` (`AUTHORISED_PURPOSE`) under
`prereg/RD-04_volatility_drift.md` (`AUTHORISED_DECLARATION`), spanning from the choice block's first day or later;
anything else -- another purpose, kind or declaration, a choice-block authorisation, an object that only looks like one
-- is refused (`AuthorisationRefused`). The days then run from the authorisation's start to its end, never past
2026-07-16 (`AUTHORISED_LAST_DAY`, the development window's last). **A day from 2026-07-17 on is refused always**:
absent as past `LAST_DAY`, present as the confirmation window (`ConfirmationWindowRefused`, also the reader's class),
and an authorisation whose end reaches it is refused whatever days are asked for. The reader stays the lock; this is a
second one. The script (`scripts/vol_descriptive.py`) passes none: its CLI is unchanged and it describes the choice
block only.

**`band_mark` stays a choice-block section (M5).** `summarise` writes `band_mark` from the walks of sessions dated at
or before `CHOICE_END` only, with or without an authorisation (absent every session is, so nothing changes): under
RD-04's no `band_mark` row covers a session from 2024-01-02, and on judged sessions alone none is written.
`output_problems` refuses a `band_mark` row of any period other than the block or a year, a year after 2023 or a block
ending after 2023-12-29, in either case.

**The session** is the walker's day (`atlas_local.day_arrays`, imported from the vendored tree when bars are described):
the charted contract's bars on the trading-day clock, index j the bar's END minute after 17:00 CT, 1 .. 1330 (the bar
ending 15:10 CT the last). Its **day kind** is the walk's (`atlas_walk._kind`'s rule, re-stated here and held to
Stage 2's A1 `days` table by the script's identity): 'x' no bar, 'e' the last bar ending more than ten minutes before
15:10 CT (an early close), 'o' an FOMC day, 'b' a BLS 08:30 ET report day, else 'n'. Per session:

* `range_pts` -- max(high) - min(low) over the session's bars, in index points; `range_pct` -- 100 x `range_pts` over
  the first bar's open (the first bar that exists). No price level is written: a range is a difference, the percent a
  ratio (feature-rules section 2).
* `trail20_range_pts`, `trail20_range_pct` -- the mean of the same measure over the **20 most recent prior sessions** of
  a walked kind ('n' or 'b', the walked day set; S2's trailing rule, `s2_state_gate.trailing_windows`), the session
  itself never included; undefined (blank) with fewer than 20 such sessions before it. A session's own kind does not
  matter for its trailing value: only earlier sessions are read.
* `band_ticks_010`, `band_ticks_025` -- the scale-free bands' half-width: 0.10 and 0.25 of `trail20_range_pts`, in whole
  ticks (rounded half up, at least one tick); blank when the trailing mean is.

**The bands** (the note's 4 (a): "the side-free first-exit time of a band of fixed points around the entry ... both
sides pooled"). At each entry, for a band of half-width S ticks (the stop's distance) and every R of `RR_GRID` (every
quarter R to 3R, the union of what P-14's and P-16's tables offer), the walk is followed from the entry bar's open
``e`` both ways, with Stage 2's walk conventions (`fv3_rung_walk`): excursions in whole ticks, the entry bar counted,
a level S against the entry **reached** (an excursion of at least S) and a level T = floor(R x S + 1e-9) the other way
**traded through** (beyond T), the walk ending at the bar ending 15:08 CT (`FLAT_ENTRY`). A side-free walk does not say
which level is which: for the walk "up" the levels are e - S and e + T, for the walk "down" e + S and e - T, and each
walk's **first-exit time** is the minutes from the entry bar's start to the end of the first bar that reaches either
level (`exit bar - entry bar + 1`); a walk that reaches neither by 15:08 CT is **open**. The two walks are pooled; which
level was reached is never computed into the output. The bands: 12.5, 25 and 37.5 points (50, 100, 150 ticks: the
registered designs' stops) and 0.10 and 0.25 of the trailing range (D-238's scale-free reading). **No breakeven, no
cost, no slippage, no side**: the band is a property of the bars, not a trade (FV3's breakeven is a design's exit and
is left out; the script's identity holds every walk the breakeven cannot touch equal to `fv3_rung_walk.walk`).

**The entries.** Two sets, each walked on every session of kind 'n' or 'b' (an 'o', 'e' or 'x' session walks nothing,
as Stage 2's walks), a report day's marks before the 07:30 CT cut (`BLS_CUT`) dropped as Stage 2 drops them:

* `p16_marks` -- P-16's offers: every five minutes from 17:00 CT to 15:05 CT (`resolved_coin.marks`, 266 marks), entered
  at the first bar opening after the mark (`fast_walk.entry_bar`, delay 0, as P-16 enters);
* `p14_slots` -- P-14's hours: the start of each hour 17:00 to 14:00 CT (22 slots, the hours of its frozen rung rule),
  entered five bars late (delay 5, A3's `screen_delay_min`, as P-14 enters).

A mark has no entry when it is at or after the day's last bar, or its entry bar is at or after the bar ending 15:08 CT
(`fv3_rung_walk.entries`' rule).

**Time (feature-rules section 1).** The trailing means and the scale-free bands at a session read only earlier
sessions' bars (the shift-invariance test replaces every bar from the session's 17:00 CT on); a session's range reads
its own bars to 15:10 CT and is used at no mark of that session; a walk reads its entry bar's open and the bars from its
entry bar to the bar ending 15:08 CT (the walk is the descriptive's object, read after the mark by definition, like
Stage 2's walks).

**Summaries** (`summarise`). Medians, p10 and p90 -- each the **inverted empirical CDF** (the smallest value v with
at least the share q of the sample at or below v; no interpolation) -- with the count:

* section `session`: one row a session (every kind with a bar);
* section `range`: by period, over the walked sessions ('n', 'b'): each session measure's n, median, p10, p90;
* section `band`: by period, set, band and R, over every walk (both directions pooled, every mark of the set): the walks,
  the share open at 15:08 CT, and the first-exit time's median, p10 and p90 in minutes, an open walk counted as later
  than every exit -- a quantile that falls on an open walk is blank (the open share says why);
* section `band_mark`: the same by mark, for the whole block and by calendar year (not by quarter: the file stays
  small).

Periods: `block` (the whole span), `year` (2020 ...), `quarter` (2020Q1 ...).

This module imports no engine and reads no file: the script (`scripts/vol_descriptive.py`) reads the bars through
`extended.reader`, Stage 2's calendars and A1's day table, runs the identities and writes the file through
`extended.results`.
"""
from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from extended.reader import (CHOICE_END, CHOICE_START, CONFIRMATION_START, JUDGED_END,  # the reader imports no engine
                             JUDGED_START, Authorisation)
from extended.reader import ConfirmationWindowRefused as _ReaderConfirmationWindowRefused

DECISION = "E-157"
TASK = "Q-121"
#: the last day described: the choice block's last; every later day is refused (2024-01-02 the judged block's first)
LAST_DAY = CHOICE_END
FIRST_DAY = CHOICE_START
#: Q-121b (M4): the one judged-block read this module accepts -- RD-04's (a2), a described reading, for this purpose
AUTHORISED_PURPOSE = "volatility_descriptive"
AUTHORISED_KIND = "described_reading"
AUTHORISED_DECLARATION = "prereg/RD-04_volatility_drift.md"
#: under that authorisation the last day is at most the development window's last (the judged block's); never later
AUTHORISED_LAST_DAY = JUDGED_END
TICK = 0.25
#: the bar ending 15:10 CT on the trading-day clock (collect_core.C_FLAT)
SESSION_END = 22 * 60 + 10
#: the bar ending 15:08 CT: the last bar a walk reads (orb_core.FLAT_ENTRY)
FLAT_ENTRY = SESSION_END - 2
#: the 'e' rule: a last bar ending more than ten minutes before 15:10 CT
EARLY_CLOSE_MARGIN = 10
#: a report day's marks before 07:30 CT are dropped (collect_core.c_slot(7, 30); A1's `news.bls_cut_ct`)
BLS_CUT = 7 * 60 + 30 + 420
TRAIL = 20
WALKED_KINDS = ("n", "b")
DAY_KINDS = ("x", "e", "o", "b", "n")
FIXED_BANDS_TICKS = (50, 100, 150)
RANGE_FRACTIONS = (0.10, 0.25)
#: every quarter R to 3R (fv3_rung_walk.RR_GRID): P-14 offers all of it, P-16 0.25, 1, 1.5, 2, 2.5 and 3
RR_GRID = tuple(0.25 * k for k in range(1, 13))
BANDS = ("12.5pt", "25pt", "37.5pt", "0.10rng", "0.25rng")
#: P-16's offers (resolved_coin.marks: every 5 minutes from 17:00 CT, before 15:10 CT), entered at the mark
P16_MARKS = tuple(range(0, SESSION_END, 5))
#: P-14's hours (17:00 to 14:00 CT, the hours of its rung rule), entered five bars late
P14_SLOTS = tuple(range(0, 21 * 60 + 1, 60))
SETS: dict[str, tuple[tuple[int, ...], int]] = {"p16_marks": (P16_MARKS, 0), "p14_slots": (P14_SLOTS, 5)}
QUANTILES = (("p10", 0.10), ("median", 0.50), ("p90", 0.90))
#: int16 codes of a walk's first-exit time: 1 .. 1331 minutes; open at 15:08 CT; no walk (no entry, no band)
OPEN = 32000
NONE = 32767
SESSION_MEASURES = ("range_pts", "range_pct", "trail20_range_pts", "trail20_range_pct")
SECTIONS = ("session", "range", "band", "band_mark")
COLUMNS = ("section", "period_kind", "period", "date", "day_kind", "bars", "walked", "range_pts", "range_pct",
           "trail20_range_pts", "trail20_range_pct", "band_ticks_010", "band_ticks_025", "measure", "set", "mark",
           "mark_ct", "band", "band_ticks", "rr", "n", "open_share", "median", "p10", "p90")
#: words no column of this reading may carry: it has no side, no level split, no outcome
FORBIDDEN_WORDS = ("side", "long", "short", "win", "won", "loss", "lost", "target", "stop", "pnl", "profit", "gross",
                   "net", "payout", "pass", "price", "high", "low", "close", "first_open", "coin")


class BeyondChoiceBlock(RuntimeError):
    """A span or a frame reaching past the choice block (2023-12-29): this reading never describes the judged block."""


class AuthorisationRefused(BeyondChoiceBlock):
    """Q-121b: an `authorised` that is not RD-04's judged `volatility_descriptive` read, or a day outside what it
    authorises; raised before the call touches its input."""


class ConfirmationWindowRefused(BeyondChoiceBlock, _ReaderConfirmationWindowRefused):
    """Q-121b: a day from 2026-07-17 on, or an authorisation reaching it -- refused always."""


# ------------------------------------------------------------------------------------------------------ the refusal


def _day(x: Any) -> date:
    if isinstance(x, datetime):                         # a pandas Timestamp is a datetime
        return x.date()
    if isinstance(x, date):
        return x
    return date.fromisoformat(str(x)[:10])


def check_authorisation(authorised: Any) -> None:
    """Nothing when `authorised` is None (the choice block only). Otherwise refused unless it is RD-04's judged read
    (the module's docstring): `ConfirmationWindowRefused` when its span reaches 2026-07-17, `AuthorisationRefused` for
    anything else that is not that read."""
    if authorised is None:
        return
    if not isinstance(authorised, Authorisation):
        raise AuthorisationRefused(f"REFUSED: Q-121b: authorised is a {type(authorised).__name__}, not an "
                                   "extended.reader.Authorisation; nothing is read or computed")
    try:
        s, e = _day(authorised.start), _day(authorised.end)
    except (TypeError, ValueError) as exc:
        raise AuthorisationRefused(f"REFUSED: Q-121b: the authorisation's span is not two days ({exc})") from None
    if max(s, e) >= CONFIRMATION_START:
        raise ConfirmationWindowRefused(
            f"REFUSED: Q-121b: the authorisation reaches {max(s, e)} -- NQ from {CONFIRMATION_START} is the declared "
            "confirmation window, never described; nothing is read or computed")
    why = []
    if authorised.judged is not True or "judged" not in tuple(authorised.blocks or ()):
        why.append("it is not a judged-block read")
    if authorised.kind != AUTHORISED_KIND:
        why.append(f"its kind is {authorised.kind!r}, not {AUTHORISED_KIND!r}")
    if authorised.purpose != AUTHORISED_PURPOSE:
        why.append(f"its purpose is {authorised.purpose!r}, not {AUTHORISED_PURPOSE!r}")
    if authorised.declaration != AUTHORISED_DECLARATION:
        why.append(f"its declaration is {authorised.declaration!r}, not {AUTHORISED_DECLARATION!r}")
    if authorised.ledgered is not True:
        why.append("it is not ledgered")
    if not (isinstance(authorised.declaration_sha256, str) and len(authorised.declaration_sha256) == 64):
        why.append("it carries no declaration sha256")
    if s < FIRST_DAY or e < s:
        why.append(f"its span {s} to {e} is not inside the development window")
    if why:
        raise AuthorisationRefused("REFUSED: Q-121b accepts one judged-block read only -- a described reading for "
                                   f"{AUTHORISED_PURPOSE!r} under {AUTHORISED_DECLARATION} -- and this one is not it: "
                                   + "; ".join(why) + "; nothing is read or computed")


def last_day(authorised: Authorisation | None = None) -> date:
    """The last day described: `LAST_DAY` absent; under RD-04's authorisation its end, at most `AUTHORISED_LAST_DAY`
    (2026-07-16)."""
    if authorised is None:
        return LAST_DAY
    check_authorisation(authorised)
    return min(_day(authorised.end), AUTHORISED_LAST_DAY)


def first_day(authorised: Authorisation | None = None) -> date:
    """The first day described: `FIRST_DAY` absent; under RD-04's authorisation its start."""
    if authorised is None:
        return FIRST_DAY
    check_authorisation(authorised)
    return max(_day(authorised.start), FIRST_DAY)


def _check_authorised_days(got: Sequence[date], authorised: Authorisation, what: str) -> None:
    late = [d for d in got if d >= CONFIRMATION_START]
    if late:
        raise ConfirmationWindowRefused(f"REFUSED: Q-121b: {what} reaches {late[0]} -- NQ from {CONFIRMATION_START} is "
                                        "the declared confirmation window, never described; nothing is computed")
    lo, hi = first_day(authorised), last_day(authorised)
    out = [d for d in got if d < lo or d > hi]
    if out:
        raise AuthorisationRefused(f"REFUSED: Q-121b: {what} holds {len(out)} day(s) outside the authorised {lo} to "
                                   f"{hi} (first {out[0]}); nothing is computed")


def check_span(start: Any, end: Any, *, authorised: Authorisation | None = None) -> tuple[date, date]:
    """`(start, end)` as days; refused (`BeyondChoiceBlock`) when either reaches past `LAST_DAY` -- checked first,
    before any read -- and (`ValueError`) when it starts before the choice block or ends before it starts. Under
    `authorised` (checked first): refused when it reaches 2026-07-17 (`ConfirmationWindowRefused`) or leaves the
    authorised span (`AuthorisationRefused`)."""
    if authorised is not None:
        check_authorisation(authorised)
        s, e = _day(start), _day(end)
        _check_authorised_days(sorted({s, e}), authorised, f"the span {s} to {e}")
        if e < s:
            raise ValueError(f"Q-121: {e} is before {s}")
        return s, e
    s, e = _day(start), _day(end)
    if max(s, e) > LAST_DAY:
        raise BeyondChoiceBlock(
            f"REFUSED: Q-121 describes the choice block only ({FIRST_DAY} to {LAST_DAY}); {s} to {e} reaches "
            f"{max(s, e)} -- the judged block (from {JUDGED_START}) is (a2)'s, under a pinned described reading (E-157)")
    if s < FIRST_DAY:
        raise ValueError(f"Q-121: {s} is before the development window opens on {FIRST_DAY}")
    if e < s:
        raise ValueError(f"Q-121: {e} is before {s}")
    return s, e


def check_days(days: Iterable[Any], *, authorised: Authorisation | None = None) -> None:
    """Every day of a frame at or before `LAST_DAY`; refused (`BeyondChoiceBlock`) otherwise, before anything is
    computed. Under `authorised` (checked before `days` is read): every day inside the authorised span, never from
    2026-07-17 (`ConfirmationWindowRefused`)."""
    if authorised is not None:
        check_authorisation(authorised)
        got = sorted({_day(d) for d in days})
        _check_authorised_days(got, authorised, "the frame")
        return
    late = sorted({_day(d) for d in days if _day(d) > LAST_DAY})
    if late:
        raise BeyondChoiceBlock(f"REFUSED: the frame holds {len(late)} day(s) after {LAST_DAY}, from {late[0]} -- "
                                "Q-121 describes the choice block only; nothing is computed")


# ------------------------------------------------------------------------------------------------------ the session


def yymmdd(day: str) -> int:
    """`atlas_local.yymmdd`: the calendars' key."""
    d = _day(day)
    return (d.year % 100) * 10000 + d.month * 100 + d.day


def last_bar(o: np.ndarray, flat: int = SESSION_END) -> int | None:
    """`fast_walk.last_bar`: the day's last bar at or before `flat`."""
    idx = np.flatnonzero(~np.isnan(o[: min(flat, len(o) - 1) + 1]))
    return int(idx[-1]) if idx.size else None


def day_kind(o: np.ndarray, day: str, fomc: Iterable[int], bls: Iterable[int]) -> str:
    """The walk's day kind (`atlas_walk._kind`'s rule): 'x', 'e', 'o', 'b' or 'n'."""
    last = last_bar(o)
    if last is None:
        return "x"
    if last < SESSION_END - EARLY_CLOSE_MARGIN:
        return "e"
    key = yymmdd(day)
    if key in set(fomc):
        return "o"
    if key in set(bls):
        return "b"
    return "n"


def session_measures(o: np.ndarray, h: np.ndarray, l: np.ndarray) -> dict[str, float]:
    """The session's bar count, its high-low range in points and in percent of its first open (NaN with no bar)."""
    present = ~np.isnan(o)
    n = int(present.sum())
    if n == 0:
        return {"bars": 0, "range_pts": float("nan"), "range_pct": float("nan")}
    first_open = float(o[np.flatnonzero(present)[0]])
    rng = float(np.nanmax(h) - np.nanmin(l))
    return {"bars": n, "range_pts": rng, "range_pct": 100.0 * rng / first_open}


def trailing_means(values: Sequence[float], eligible: Sequence[bool], trail: int = TRAIL) -> np.ndarray:
    """For sessions in date order: the mean of `values` over the `trail` most recent EARLIER sessions that are eligible
    with a finite value (row i itself never read); NaN with fewer than `trail` of them."""
    v = np.asarray(values, dtype=float)
    ok = np.asarray(eligible, dtype=bool) & np.isfinite(v)
    out = np.full(len(v), np.nan)
    window: list[float] = []
    for i in range(len(v)):
        if len(window) >= trail:
            out[i] = float(np.mean(window[-trail:]))
        if ok[i]:
            window.append(float(v[i]))
    return out


def band_ticks(trail_range_pts: float, fraction: float) -> int | None:
    """A scale-free band's half-width: `fraction` of the trailing range, in whole ticks (half up), at least one; None
    when the trailing range is undefined."""
    if not np.isfinite(trail_range_pts):
        return None
    return max(1, int(math.floor(fraction * float(trail_range_pts) / TICK + 0.5)))


def target_ticks(R: float, S: int) -> int:
    """`fv3_rung_walk.target_ticks`: floor(R x S + 1e-9)."""
    return int(math.floor(float(R) * int(S) + 1e-9))


# ------------------------------------------------------------------------------------------------------ the walks


def entries(o: np.ndarray, marks: Sequence[int], delay: int, cut: int | None = None) -> list[tuple[int, int]]:
    """[(mark, entry bar)] -- `fv3_rung_walk.entries`' rule with `fast_walk.entry_bar`: the `delay`-th bar with an open
    after the mark, at or before the day's last bar, before the bar ending 15:08 CT; a mark at or after the last bar, or
    before `cut` (a report day's), has none."""
    last = last_bar(o)
    if last is None:
        return []
    end = min(last, FLAT_ENTRY)
    out = []
    for t in marks:
        t = int(t)
        if t >= last or (cut is not None and t < int(cut)):
            continue
        idx = np.flatnonzero(~np.isnan(o[t + 1: last + 1]))
        if idx.size <= int(delay):
            continue
        je = int(idx[int(delay)]) + t + 1
        if je >= end:
            continue
        out.append((t, je))
    return out


def first_exits(o: np.ndarray, h: np.ndarray, l: np.ndarray, entry_bars: Sequence[int],
                bands_ticks: Sequence[int | None], rr: Sequence[float] = RR_GRID) -> np.ndarray:
    """int16 codes (walks, 2, bands, R): each entry's two side-free walks' first-exit time in minutes (exit bar - entry
    bar + 1), `OPEN` when neither level is reached by the bar ending 15:08 CT, `NONE` for a band that is None. Index 1 of
    the second axis is the walk 'up' (levels e - S and e + T), 0 the walk 'down' -- an order, never written out."""
    o, h, l = (np.asarray(x, dtype=float) for x in (o, h, l))
    je = np.asarray(entry_bars, dtype=int)
    W, B, K = len(je), len(bands_ticks), len(rr)
    out = np.full((W, 2, B, K), NONE, dtype=np.int16)
    if W == 0:
        return out
    last = last_bar(o)
    if last is None:
        raise ValueError("a day with no bar has no entry")
    end = min(last, FLAT_ENTRY)
    if (je >= end).any() or np.isnan(o[je]).any():
        raise ValueError("an entry at or after 15:08 CT, or on a bar with no open")
    n = end + 1
    e = o[je]
    J = np.arange(n)
    live = (~np.isnan(o[:n]))[None, :] & (J[None, :] >= je[:, None])
    with np.errstate(invalid="ignore"):
        up = np.where(live, np.round((h[None, :n] - e[:, None]) / TICK), -np.inf)
        down = np.where(live, np.round((e[:, None] - l[None, :n]) / TICK), -np.inf)
    U = np.maximum.accumulate(up, axis=1)            # the running excursion above the entry, in ticks
    D = np.maximum.accumulate(down, axis=1)          # below it
    reach: dict[tuple[str, float], np.ndarray] = {}   # first bar at which the running excursion is >= x (n: never)
    through: dict[tuple[str, float], np.ndarray] = {}  # first bar at which it is > x

    def first_ge(name: str, M: np.ndarray, x: float) -> np.ndarray:
        if (name, x) not in reach:
            reach[(name, x)] = (M < x).sum(axis=1)   # monotone rows: the count below x is the first index at or above
        return reach[(name, x)]

    def first_gt(name: str, M: np.ndarray, x: float) -> np.ndarray:
        if (name, x) not in through:
            through[(name, x)] = (M <= x).sum(axis=1)
        return through[(name, x)]

    for b, S in enumerate(bands_ticks):
        if S is None:
            continue
        S = int(S)
        if S < 1:
            raise ValueError(f"a band of {S} ticks")
        for k, R in enumerate(rr):
            T = target_ticks(R, S)
            # the walk 'up': e - S reached (D >= S) or e + T traded through (U > T); 'down': the mirror
            for w, (a, z) in enumerate(((first_ge("U", U, S), first_gt("D", D, T)),
                                        (first_ge("D", D, S), first_gt("U", U, T)))):
                j = np.minimum(a, z)
                out[:, w, b, k] = np.where(j < n, j - je + 1, OPEN).astype(np.int16)
    return out


def walk_session(o: np.ndarray, h: np.ndarray, l: np.ndarray, kind: str, bands_ticks: Sequence[int | None],
                 sets: Mapping[str, tuple[Sequence[int], int]] = SETS, cut: int = BLS_CUT,
                 rr: Sequence[float] = RR_GRID) -> dict[str, np.ndarray]:
    """{set: int16 codes (marks of the set, 2, bands, R)} for one session -- every code `NONE` on a session not walked
    (kind not 'n' or 'b') and at a mark with no entry."""
    out = {}
    for name, (marks, delay) in sets.items():
        codes = np.full((len(marks), 2, len(bands_ticks), len(rr)), NONE, dtype=np.int16)
        if kind in WALKED_KINDS:
            ent = entries(o, marks, delay, cut if kind == "b" else None)
            if ent:
                pos = {int(m): i for i, m in enumerate(marks)}
                rows = [pos[t] for t, _ in ent]
                codes[rows] = first_exits(o, h, l, [j for _, j in ent], bands_ticks, rr)
        out[name] = codes
    return out


def _as_float(a: Sequence[Any]) -> np.ndarray:
    return np.array([np.nan if x is None else float(x) for x in a], dtype=float)


def vendored_day_arrays() -> Callable[[pd.DataFrame], tuple]:
    """`atlas_local.day_arrays` from the vendored tree (the caller's process has put it on `sys.path`)."""
    from propedge.research.atlas_local import day_arrays

    return day_arrays


def describe(bars: pd.DataFrame, *, fomc: Iterable[int], bls: Iterable[int], cut: int = BLS_CUT,
             day_arrays: Callable[[pd.DataFrame], tuple] | None = None,
             sets: Mapping[str, tuple[Sequence[int], int]] = SETS,
             keep_arrays: bool = False,
             authorised: Authorisation | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """(the session table, the walks) for every trading day in `bars` (the store's frame: `ts`, `day`, `open`, `high`,
    `low`, `close`), refused when a day is past `LAST_DAY`. The walks: {"dates": the walked sessions' dates, set: int16
    codes (walked sessions, marks, 2, bands, R)} with each session's bands `BANDS` (the fixed three, then the trailing
    range's two, `NONE` when undefined). `keep_arrays` adds {"arrays": {date: (o, h, l, c)}} for the identities.
    `authorised` (Q-121b): RD-04's judged read, checked before `bars` is touched; then days to its end."""
    check_authorisation(authorised)
    check_days(bars["day"].astype(str).unique(), authorised=authorised)
    arrays_of = day_arrays or vendored_day_arrays()
    fomc, bls = {int(x) for x in fomc}, {int(x) for x in bls}
    rows, arrays = [], {}
    for day, g in bars.groupby("day", sort=True):
        day = str(day)
        o, h, l, c = (_as_float(a) for a in arrays_of(g))
        kind = day_kind(o, day, fomc, bls)
        rows.append({"date": day, "day_kind": kind, **session_measures(o, h, l)})
        arrays[day] = (o, h, l, c)
    sessions = pd.DataFrame(rows, columns=["date", "day_kind", "bars", "range_pts", "range_pct"])
    elig = sessions["day_kind"].isin(WALKED_KINDS).to_numpy()
    for m in ("range_pts", "range_pct"):
        sessions[f"trail20_{m}"] = trailing_means(sessions[m].to_numpy(), elig)
    for frac, col in zip(RANGE_FRACTIONS, ("band_ticks_010", "band_ticks_025")):
        sessions[col] = pd.array([band_ticks(x, frac) for x in sessions["trail20_range_pts"]], dtype="Int64")
    sessions["walked"] = elig
    walked = sessions[elig]
    walks: dict[str, Any] = {"dates": walked["date"].tolist()}
    per = {name: [] for name in sets}
    for r in walked.itertuples(index=False):
        o, h, l, _ = arrays[r.date]
        bt = [*FIXED_BANDS_TICKS, *(None if pd.isna(x) else int(x) for x in (r.band_ticks_010, r.band_ticks_025))]
        for name, codes in walk_session(o, h, l, r.day_kind, bt, sets, cut).items():
            per[name].append(codes)
    for name, (marks, _) in sets.items():
        walks[name] = (np.stack(per[name]) if per[name]
                       else np.full((0, len(marks), 2, len(BANDS), len(RR_GRID)), NONE, dtype=np.int16))
    if keep_arrays:
        walks["arrays"] = arrays
    return sessions, walks


# ------------------------------------------------------------------------------------------------------ summaries


def quantiles(codes: np.ndarray, qs: Sequence[float] = tuple(q for _, q in QUANTILES)) -> dict[str, np.ndarray]:
    """Along axis 0 of an int16 code array: the count of walks (codes other than `NONE`), the open share, and each
    q's inverted-CDF quantile (the k-th smallest, k = ceil(q n)) -- NaN where it falls on an open walk or n is 0."""
    X = np.sort(np.asarray(codes), axis=0)
    n = (X != NONE).sum(axis=0)
    opened = (X == OPEN).sum(axis=0)
    out: dict[str, np.ndarray] = {"n": n, "open_share": np.where(n > 0, opened / np.maximum(n, 1), np.nan)}
    for q in qs:
        k = np.maximum(np.ceil(q * n - 1e-9).astype(int), 1) - 1
        v = np.take_along_axis(X, np.minimum(k, X.shape[0] - 1)[None, ...], axis=0)[0].astype(float)
        out[str(q)] = np.where((n > 0) & (v < OPEN), v, np.nan)
    return out


def value_quantiles(values: Sequence[float]) -> dict[str, float]:
    """n, median, p10, p90 of finite values (the same inverted-CDF rule)."""
    v = np.sort(np.asarray(values, dtype=float)[np.isfinite(np.asarray(values, dtype=float))])
    out: dict[str, float] = {"n": int(v.size)}
    for name, q in QUANTILES:
        out[name] = float(v[max(int(math.ceil(q * v.size - 1e-9)), 1) - 1]) if v.size else float("nan")
    return out


def periods(dates: Sequence[str], kinds: Sequence[str] = ("block", "year", "quarter")) -> list[tuple[str, str, np.ndarray]]:
    """[(period kind, period, boolean mask over `dates`)]: the whole span, each calendar year, each quarter."""
    d = pd.to_datetime(pd.Series(list(dates), dtype=str))
    out = []
    if "block" in kinds and len(d):
        out.append(("block", f"{min(dates)}..{max(dates)}", np.ones(len(d), dtype=bool)))
    if "year" in kinds:
        for y in sorted(d.dt.year.unique()):
            out.append(("year", str(int(y)), (d.dt.year == y).to_numpy()))
    if "quarter" in kinds:
        q = d.dt.year.astype(str) + "Q" + d.dt.quarter.astype(str)
        for p in sorted(q.unique()):
            out.append(("quarter", str(p), (q == p).to_numpy()))
    return out


def ct(slot: int) -> str:
    """`resolved_coin.ct`: a trading-day-clock slot as HH:MM CT."""
    m = (int(slot) + 17 * 60) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


def _band_ticks_label(b: int) -> Any:
    return FIXED_BANDS_TICKS[b] if b < len(FIXED_BANDS_TICKS) else None


def summarise(sessions: pd.DataFrame, walks: Mapping[str, Any],
              sets: Mapping[str, tuple[Sequence[int], int]] = SETS, *,
              authorised: Authorisation | None = None) -> pd.DataFrame:
    """The result file's rows (`COLUMNS`), sections `SECTIONS` in order. The session table's days are checked first
    (`check_days`, under `authorised` if given). `band_mark` is written from the walks of sessions dated at or before
    `CHOICE_END` only (M5): never a row for a session from 2024-01-02."""
    check_authorisation(authorised)
    check_days(sessions["date"].astype(str).tolist(), authorised=authorised)
    rows: list[dict[str, Any]] = []
    for r in sessions.itertuples(index=False):
        rows.append({"section": "session", "date": r.date, "day_kind": r.day_kind, "bars": int(r.bars),
                     "walked": bool(r.walked), "range_pts": r.range_pts, "range_pct": r.range_pct,
                     "trail20_range_pts": r.trail20_range_pts, "trail20_range_pct": r.trail20_range_pct,
                     "band_ticks_010": r.band_ticks_010, "band_ticks_025": r.band_ticks_025})
    walked = sessions[sessions["walked"].astype(bool)].reset_index(drop=True)
    for pk, p, m in periods(walked["date"].tolist()):
        for meas in SESSION_MEASURES:
            rows.append({"section": "range", "period_kind": pk, "period": p, "measure": meas,
                         **value_quantiles(walked.loc[m, meas].to_numpy())})
    dates = list(walks["dates"])
    if dates != walked["date"].tolist():
        raise ValueError("the walks' sessions are not the session table's walked sessions")
    B, K = len(BANDS), len(RR_GRID)
    for name, (marks, _) in sets.items():
        E = walks[name]
        for pk, p, m in periods(dates):
            sub = E[m]                                                  # (sessions, marks, 2, B, K)
            pooled = quantiles(sub.reshape(-1, B, K))
            for b in range(B):
                for k in range(K):
                    rows.append({"section": "band", "period_kind": pk, "period": p, "set": name, "band": BANDS[b],
                                 "band_ticks": _band_ticks_label(b), "rr": RR_GRID[k],
                                 **_q_row(pooled, (b, k))})
        choice = np.array([_day(d) <= CHOICE_END for d in dates], dtype=bool)
        Ec = E[choice]                                                  # M5: the choice block's sessions only
        for pk, p, m in periods([d for d, k in zip(dates, choice) if k], ("block", "year")):
            sub = np.moveaxis(Ec[m], 1, 2)                              # (sessions, 2, marks, B, K)
            by_mark = quantiles(sub.reshape(-1, len(marks), B, K))
            for i, mk in enumerate(marks):
                for b in range(B):
                    for k in range(K):
                        rows.append({"section": "band_mark", "period_kind": pk, "period": p, "set": name,
                                     "mark": int(mk), "mark_ct": ct(mk), "band": BANDS[b],
                                     "band_ticks": _band_ticks_label(b), "rr": RR_GRID[k],
                                     **_q_row(by_mark, (i, b, k))})
    out = pd.DataFrame(rows, columns=list(COLUMNS))
    for c in ("bars", "band_ticks_010", "band_ticks_025", "mark", "band_ticks", "n"):
        out[c] = out[c].astype("Int64")
    return out


def _band_mark_late(bm: pd.DataFrame) -> pd.Series:
    """Per `band_mark` row: whether its period is anything but the block or a year inside the choice block."""
    pk, p = bm["period_kind"].astype(str), bm["period"].astype(str)
    year_ok = p.str.fullmatch(r"\d{4}") & (p <= str(CHOICE_END.year))
    ends = p.str.split("..", regex=False).str[-1]
    block_ok = ends.str.fullmatch(r"\d{4}-\d{2}-\d{2}") & (ends <= CHOICE_END.isoformat())
    return ~(((pk == "year") & year_ok) | ((pk == "block") & block_ok))


def _q_row(q: Mapping[str, np.ndarray], idx: tuple[int, ...]) -> dict[str, Any]:
    out: dict[str, Any] = {"n": int(q["n"][idx]), "open_share": float(q["open_share"][idx])}
    for name, v in QUANTILES:
        out[name] = float(q[str(v)][idx])
    return out


def output_problems(frame: pd.DataFrame, *, authorised: Authorisation | None = None) -> list[str]:
    """Why a frame is not this reading's: columns not `COLUMNS` exactly, a forbidden word in a column, a section
    unknown or missing, a session past `LAST_DAY`, a share outside [0, 1], a count below zero, a quantile out of
    order, a `band_mark` row reaching past the choice block (M5). Under `authorised` (checked first; refused by raising,
    before `frame` is touched): a session outside the authorised span or from 2026-07-17, and `band_mark` not required
    (none is written on judged sessions alone)."""
    check_authorisation(authorised)
    bad = []
    if list(frame.columns) != list(COLUMNS):
        bad.append(f"columns are not COLUMNS: {list(frame.columns)}")
    words = [c for c in frame.columns if any(w in str(c).lower() for w in FORBIDDEN_WORDS)]
    if words:
        bad.append(f"columns carrying a forbidden word: {words}")
    if "section" in frame:
        have = set(frame["section"].astype(str))
        if have - set(SECTIONS):
            bad.append(f"unknown sections {sorted(have - set(SECTIONS))}")
        need = set(SECTIONS) if authorised is None else set(SECTIONS) - {"band_mark"}
        if need - have:
            bad.append(f"missing sections {sorted(need - have)}")
    if "date" in frame:
        d = frame["date"].dropna().astype(str)
        if authorised is None:
            if (d > LAST_DAY.isoformat()).any() or (d < FIRST_DAY.isoformat()).any():
                bad.append("a session outside the choice block")
        else:
            if (d >= CONFIRMATION_START.isoformat()).any():
                bad.append(f"a session in the confirmation window (from {CONFIRMATION_START})")
            if (d > last_day(authorised).isoformat()).any() or (d < first_day(authorised).isoformat()).any():
                bad.append("a session outside the authorised span")
    if {"section", "period_kind", "period"} <= set(frame.columns):
        bm = frame[frame["section"].astype(str) == "band_mark"]
        if len(bm) and _band_mark_late(bm).any():
            bad.append(f"a band_mark row reaching past the choice block ({CHOICE_END}): band_mark is the choice "
                       "block's section only (M5)")
    if "open_share" in frame:
        s = frame["open_share"].dropna()
        if ((s < 0) | (s > 1)).any():
            bad.append("an open share outside [0, 1]")
    if "n" in frame and (frame["n"].dropna() < 0).any():
        bad.append("a negative count")
    if {"p10", "median", "p90"} <= set(frame.columns):
        q = frame[["p10", "median", "p90"]].astype(float)
        both = q.notna().all(axis=1)
        if ((q.loc[both, "p10"] > q.loc[both, "median"]) | (q.loc[both, "median"] > q.loc[both, "p90"])).any():
            bad.append("a quantile out of order")
    return bad


__all__ = ["DECISION", "TASK", "LAST_DAY", "FIRST_DAY", "TICK", "SESSION_END", "FLAT_ENTRY", "BLS_CUT", "TRAIL",
           "WALKED_KINDS", "FIXED_BANDS_TICKS", "RANGE_FRACTIONS", "RR_GRID", "BANDS", "P16_MARKS", "P14_SLOTS", "SETS",
           "OPEN", "NONE", "COLUMNS", "SECTIONS", "BeyondChoiceBlock", "AuthorisationRefused",
           "ConfirmationWindowRefused", "AUTHORISED_PURPOSE", "AUTHORISED_KIND", "AUTHORISED_DECLARATION",
           "AUTHORISED_LAST_DAY",
           "check_authorisation", "last_day", "first_day", "check_span", "check_days", "yymmdd", "last_bar",
           "day_kind", "session_measures", "trailing_means", "band_ticks", "target_ticks", "entries", "first_exits",
           "walk_session", "describe", "quantiles", "value_quantiles", "periods", "ct", "summarise", "output_problems"]
