"""Q-171: S1's range -- the stop width as a multiple k of the trailing range, read on the **search years only**
(2020-01-02 to 2023-12-29, E-208) -- so the design search can run on the real Topstep lever space
(`docs/plans/LEVER_TABLE_topstep50k.md`, row S1 and section 6; E-157 and E-211: a stop in volatility units is a
trade-shape lever, its multiple's range read on the search years only and entering the held-out ledger as none).

    from extended import s1_range as S
    S.check_span("2020-01-02", "2023-12-29")                 # refuses any day after 2023-12-29
    days = S.day_table(bars, fomc=fomc, bls=bls, src=sources) # one row a stored day: kind, each session's range, voids
    days = S.add_trailing(days)                               # each session's trailing range, from earlier days only
    frame = S.summarise(days, caps)                           # the result file's rows
    S.load_range(path, caps=caps)                             # the loader's read, by the manifest (lever_space)

This module imports no engine and reads no bar: `scripts/s1_range.py` reads the bars through `extended.reader`, runs the
identities and writes the file through `extended.results`.

**The sessions** (`SESSIONS`; the lever table's T2, with E-231 (3)'s per-date anchors from `day_calendar.anchored_starts`,
in minutes after the 17:00 CT reopen, i.e. the stamp slot of a window's first bar):

* `evening` -- the bars stamped from the reopen (slot 0) to before asia's anchor (09:00 Tokyo);
* `asia` -- from asia's anchor to before london's (08:00 London);
* `london` -- from london's anchor to before ny's (09:30 New York, 08:30 CT: slot 930 on every date);
* `ny` -- the regular session; the lever table's `ny_am` and `ny_pm` (split at T2b, noon New York) both take it
  (`LEVER_SESSIONS`).

**The trailing range a stop is set from** (each read from bars closed before the day's 17:00 CT reopen, so before any
alert of the day -- feature-rules section 1):

* `ny` -- **`trail20_range_pts`** exactly as Q-121 and RD-04 define it (`extended.vol_descriptive`): the mean of the
  walker day's range (max high - min low of the bars ending 17:01 .. 15:10 CT) over the 20 most recent **earlier**
  sessions of a walked kind ('n' or 'b'), blank with fewer than 20. Its population is Q-121's, so its by-year
  quantiles are held to Q-121's admitted `range` rows of 2020 to 2023 (`q121_problems`; the script's identity).
* `evening`, `asia`, `london` -- **the session's own trailing range** (RD-04's (a2) has none): the same mean over the 20
  most recent earlier days of a walked kind whose overnight is not void under the calendar (below) and whose window
  holds a bar, of the window's own range (max high - min low of the bars stamped in the window).

**The void calendar** (`extended.day_calendar.day_flags`, E-231, E-232): a day is out of a session's population when
`day_flags` gives it any void -- day-wide for `ny` (`reads_overnight=False`); with the overnight rules for the three
overnight sessions (`reads_overnight=True`), `london` also reading the bar stamped 08:29 (`reads_0829=True`, its window's
last bar) -- `VOID_RULE`. `prior_void` (the previous day's levels) is not a void here: a range is a difference inside
one day's charted contract.

**The population of a session** (`population`): the stored search-year days of a walked kind ('n' or 'b': no FOMC day,
no early close, no day without a bar), not void for the session, with a defined trailing range. `day_counts` partitions
the stored days into `kind_out`, `void`, `no_trail` and `population`; the last is the n of every share and quantile.

**The translation (declared before any run).** The caps are `lever_space.stop_caps()`: the floor F and the cap C in
ticks (TICK = 0.25 point). On a day d with trailing range T(d) points, a multiple k sets the stop **k x T(d) points,
unrounded**, and k **keeps the stop inside the caps on d** when F x TICK <= k x T(d) <= C x TICK, both edges inclusive:
k in [kmin(d), kmax(d)] with kmin(d) = F x TICK / T(d) and kmax(d) = C x TICK / T(d) (`k_bounds`). For a share q, **the
range of k** is the set of k inside the caps on at least ceil(q n) of the population's n days; `k_lo` and `k_hi` are
its least and greatest members (attained: a day enters at its kmin and leaves after its kmax), computed exactly over the
breakpoints (`k_range`), and `contiguous` says whether every k between them qualifies too (the loader refuses a gapped
range). The share each end achieves (`inside_at_lo`, `inside_at_hi`) is written beside.

* **The declared share `SHARE` = 0.95** (proposed by Q-171's builder; the lever table's wording leaves it open): a
  single extreme trailing mean does not set an end of a searched range, and at either end the design stands aside (a
  stop below the floor, or one micro's stop-out beyond the start room) on at most one day in twenty, which the
  journey prices itself. The rows for every share of `SHARES` are written beside; only `SHARE` loads.
* **The quantile rule:** the inverted empirical CDF (Q-121's: the smallest value with at least the share p of the
  sample at or below it, no interpolation; p = 0 the least), for the per-day kmin (`k_floor`) at each probability of
  `PROBS` (`quantile`). The per-day kmax is kmin x C / F on every day, so its quantiles are `k_floor` x C / F and are
  not written: a column beside `k_floor` at that fixed ratio would put every row of the file on one ratio, which the
  licence guard's pair rule refuses whenever 100 C / F falls on the tick grid.

**The file** (`COLUMNS`, sections `SECTIONS`): `days` (per session, the count of each day class), `range_k` (per session
and share: k_lo, k_hi, contiguous, the shares inside at each end) and `k_quantile` (per session and probability: the
quantiles of kmin and kmax); n is the `days` row `population`, never beside a share (the licence guard's pair rule). No
date, no price level, no range in points: k is a ratio of the caps to a range, and
the licence guard (`extended.price_levels`) is run on it by the tests.

**The loader** (`load_range`, called by `lever_space`): the file and its sidecar manifest must both exist (else `NotRead`,
which the lever space reports as `NotComputed`); then it is refused (`RangeRefused`) unless the manifest's sha256 is the
file's, its script this reading's, its tree clean and its run a clean run, its parameters this task's, the whole search
years, both identities held, the caps equal to `stop_caps()` now, and the declared share `SHARE`; and unless every
session has a finite, contiguous range at that share with 0 < k_lo < k_hi.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import day_calendar as DC
from extended import reader as R                      # constants and the refusal class only: no read here
from extended import vol_descriptive as V

TASK = "Q-171"
DECISIONS = ("E-157", "E-208", "E-211", "E-231", "E-232")
RESULT = "s1_range"
SCRIPT = "scripts/s1_range.py"
#: the reader's purpose for the search-year bars (a choice-block read: admitted without a pin, never ledgered; the
#: word 'range' and the reading's row make it traceable, and a choice word keeps it off the held-out years whatever
#: a declaration says -- `extended.reader`'s H-2 rule)
PURPOSE = "s1_lever_range_search_years"
READ_ROW = "E-211"
SEARCH_START, SEARCH_END = R.CHOICE_START, R.CHOICE_END
TICK = V.TICK
TRAIL = V.TRAIL
WALKED_KINDS = V.WALKED_KINDS
SESSIONS = ("evening", "asia", "london", "ny")
OVERNIGHT = ("evening", "asia", "london")
#: the lever table's T2 sessions and the session whose range each takes
LEVER_SESSIONS = {"evening": "evening", "asia": "asia", "london": "london", "ny_am": "ny", "ny_pm": "ny"}
#: (reads_overnight, reads_0829) for `day_calendar.day_flags`, per session
VOID_RULE = {"evening": (True, False), "asia": (True, False), "london": (True, True), "ny": (False, False)}
NY_START = 8 * 60 + 30 + 7 * 60                       # 08:30 CT as minutes after the 17:00 CT reopen (930)
#: the declared share (see the docstring) and the shares written beside
SHARE = 0.95
SHARES = (0.50, 0.75, 0.90, 0.95, 0.99, 1.00)
PROBS = (0.0, 0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1.0)
QUANTILE_RULE = "inverted empirical CDF (Q-121's; no interpolation; p = 0 the least)"
SECTIONS = ("days", "range_k", "k_quantile")
COUNT_KINDS = ("stored", "kind_out", "void", "no_trail", "population")
#: no count shares a row with a share or a probability (a count over a share can land on the level grid: the licence
#: guard's pair rule); each session's day count is its `days` row `population`
COLUMNS = ("section", "session", "count_kind", "count", "share", "prob", "k_lo", "k_hi", "contiguous",
           "inside_at_lo", "inside_at_hi", "k_floor")
#: Q-121's admitted rows (CHARTER 3.3 (a)): section `range`, by year, the measure `trail20_range_pts`, 2020 to 2023
Q121_MEASURE = "trail20_range_pts"
Q121_YEARS = tuple(str(y) for y in range(SEARCH_START.year, SEARCH_END.year + 1))
Q121_TOL = 1e-9                                       # relative, on each quantile (the CSV round trip)


class BeyondSearchYears(RuntimeError):
    """A span or a frame reaching past the search years (2023-12-29): this reading never reads the held-out years."""


class ConfirmationWindowRefused(BeyondSearchYears, R.ConfirmationWindowRefused):
    """A day from 2026-07-17 on: refused always."""


class NotRead(FileNotFoundError):
    """The loader: no result file (or no manifest beside it) yet."""


class RangeRefused(RuntimeError):
    """The loader: a file present but not this reading's, or a range that does not load."""


# ------------------------------------------------------------------------------------------------ the search years


def _day(x: Any) -> date:
    if isinstance(x, datetime):
        return x.date()
    if isinstance(x, date):
        return x
    return date.fromisoformat(str(x)[:10])


def check_span(start: Any, end: Any) -> tuple[date, date]:
    """`(start, end)` as days, refused before any read when either reaches past the search years
    (`ConfirmationWindowRefused` from 2026-07-17, else `BeyondSearchYears`), and (`ValueError`) when it starts before
    2020-01-02 or ends before it starts."""
    s, e = _day(start), _day(end)
    if max(s, e) >= R.CONFIRMATION_START:
        raise ConfirmationWindowRefused(f"REFUSED ({TASK}): {s} to {e} reaches {R.CONFIRMATION_START} -- NQ's "
                                        "confirmation window, never read")
    if max(s, e) > SEARCH_END:
        raise BeyondSearchYears(f"REFUSED ({TASK}): S1's range is read on the search years only ({SEARCH_START} to "
                                f"{SEARCH_END}, E-208, E-211); {s} to {e} reaches {max(s, e)}")
    if s < SEARCH_START:
        raise ValueError(f"{TASK}: {s} is before the search years open on {SEARCH_START}")
    if e < s:
        raise ValueError(f"{TASK}: {e} is before {s}")
    return s, e


def check_days(days: Iterable[Any]) -> None:
    """Every day inside the search years; refused before anything is computed otherwise."""
    got = sorted({_day(d) for d in days})
    if got:
        check_span(got[-1], got[-1])
        if got[0] < SEARCH_START:
            raise ValueError(f"{TASK}: the frame holds {got[0]}, before {SEARCH_START}")


# ------------------------------------------------------------------------------------------------ the sessions


def session_windows(d: date) -> dict[str, tuple[int, int]]:
    """The overnight sessions' windows for trading day `d` as [first, end) stamp slots (minutes after the 17:00 CT
    reopen), from the local anchors of that date."""
    a = DC.anchored_starts(d)
    if a["ny"] != NY_START:
        raise ValueError(f"{d}: ny's anchor is slot {a['ny']}, not 08:30 CT")
    w = {"evening": (0, a["asia"]), "asia": (a["asia"], a["london"]), "london": (a["london"], a["ny"])}
    if not 0 < a["asia"] < a["london"] < a["ny"]:
        raise ValueError(f"{d}: the session anchors are out of order ({a})")
    return w


def window_range(h: np.ndarray, l: np.ndarray, a: int, b: int) -> float:
    """max high - min low of the bars stamped a .. b - 1; the arrays are indexed by a bar's END minute (stamp + 1).
    NaN with no bar."""
    h, l = np.asarray(h, dtype=float), np.asarray(l, dtype=float)
    hh, ll = h[a + 1: b + 1], l[a + 1: b + 1]
    if not np.isfinite(hh).any():
        return float("nan")
    return float(np.nanmax(hh) - np.nanmin(ll))


def _floats(a: Sequence[Any]) -> np.ndarray:
    return np.array([np.nan if x is None else float(x) for x in a], dtype=float)


def vendored_day_arrays() -> Callable[[pd.DataFrame], tuple]:
    """`atlas_local.day_arrays`, through Q-121's door (the caller's process has the vendored tree on its path)."""
    return V.vendored_day_arrays()


def day_table(bars: pd.DataFrame, *, fomc: Iterable[int], bls: Iterable[int], src: DC.Sources | None,
              day_arrays: Callable[[pd.DataFrame], tuple] | None = None) -> pd.DataFrame:
    """One row a stored day of `bars` (grouped by `day`): its date, Q-121's day kind, each session's own range in
    points (`range_<session>`; `ny`'s is the walker day's, as Q-121's `range_pts`) and whether the calendar voids it
    for the session (`void_<session>`). The days are checked before any day's arrays are built."""
    check_days(bars["day"].astype(str).unique())
    arrays_of = day_arrays or vendored_day_arrays()
    fomc, bls = {int(x) for x in fomc}, {int(x) for x in bls}
    rows = []
    for day, g in bars.groupby("day", sort=True):
        day = str(day)
        d = _day(day)
        o, h, l, _ = (_floats(a) for a in arrays_of(g))
        rec: dict[str, Any] = {"date": day, "day_kind": V.day_kind(o, day, fomc, bls),
                               "range_ny": V.session_measures(o, h, l)["range_pts"]}
        for s, (a, b) in session_windows(d).items():
            rec[f"range_{s}"] = window_range(h, l, a, b)
        for s in SESSIONS:
            ro, r0829 = VOID_RULE[s]
            rec[f"void_{s}"] = bool(DC.day_flags(src, "NQ", d, reads_overnight=ro, reads_0829=r0829).void)
        rows.append(rec)
    cols = ["date", "day_kind"] + [f"range_{s}" for s in SESSIONS] + [f"void_{s}" for s in SESSIONS]
    return pd.DataFrame(rows, columns=cols)


# ------------------------------------------------------------------------------------------------ the trailing range


def trailing_ranges(values: Sequence[float], eligible: Sequence[bool], trail: int = TRAIL) -> np.ndarray:
    """For days in date order: the mean of `values` over the `trail` most recent EARLIER eligible days with a finite
    value (day i itself never read); NaN with fewer than `trail` of them (Q-121's `trailing_means`)."""
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


def eligible(t: pd.DataFrame, session: str) -> np.ndarray:
    """The days that may enter a session's trailing mean: a walked kind ('n', 'b'); for an overnight session also not
    void under the calendar (`ny` keeps Q-121's population)."""
    walked = t["day_kind"].isin(WALKED_KINDS).to_numpy()
    if session == "ny":
        return walked
    return walked & ~t[f"void_{session}"].to_numpy(bool)


def add_trailing(t: pd.DataFrame) -> pd.DataFrame:
    """`t` with each session's trailing range (`trail_<session>`) from earlier days only."""
    out = t.sort_values("date", kind="stable").reset_index(drop=True)
    for s in SESSIONS:
        out[f"trail_{s}"] = trailing_ranges(out[f"range_{s}"].to_numpy(), eligible(out, s))
    return out


def population(t: pd.DataFrame, session: str) -> np.ndarray:
    """The days whose trailing range enters the session's distribution: walked, not void, a defined trailing range."""
    walked = t["day_kind"].isin(WALKED_KINDS).to_numpy()
    return walked & ~t[f"void_{session}"].to_numpy(bool) & np.isfinite(t[f"trail_{session}"].to_numpy(float))


def day_counts(t: pd.DataFrame) -> dict[str, dict[str, int]]:
    """Per session: the stored days and their partition into `kind_out`, `void`, `no_trail` and `population`."""
    walked = t["day_kind"].isin(WALKED_KINDS).to_numpy()
    out = {}
    for s in SESSIONS:
        void = t[f"void_{s}"].to_numpy(bool)
        pop = population(t, s)
        out[s] = {"stored": int(len(t)), "kind_out": int((~walked).sum()), "void": int((walked & void).sum()),
                  "no_trail": int((walked & ~void & ~pop).sum()), "population": int(pop.sum())}
    return out


# ------------------------------------------------------------------------------------------------ the translation


def k_bounds(T: Sequence[float], floor_ticks: int, cap_ticks: int) -> tuple[np.ndarray, np.ndarray]:
    """Per day: the least and the greatest k whose unrounded stop k x T lies inside [floor, cap] (in points)."""
    T = np.asarray(T, dtype=float)
    if (T <= 0).any() or not np.isfinite(T).all():
        raise ValueError("a trailing range must be finite and positive")
    kmin = floor_ticks * TICK / T
    kmax = cap_ticks * TICK / T
    return kmin, kmax


def need(share: float, n: int) -> int:
    """The days a share of n requires: ceil(share x n), at least one."""
    return max(1, int(math.ceil(float(share) * n - 1e-9)))


def k_range(kmin: Sequence[float], kmax: Sequence[float], share: float) -> dict[str, Any]:
    """The range of k inside the caps on at least `need(share, n)` days (the docstring's translation): its least and
    greatest members, whether it is one interval, and the share inside at each end. Blank (NaN) when no k qualifies."""
    kmin, kmax = np.asarray(kmin, dtype=float), np.asarray(kmax, dtype=float)
    n = int(kmin.size)
    blank = {"n_days": n, "k_lo": float("nan"), "k_hi": float("nan"), "contiguous": False,
             "inside_at_lo": float("nan"), "inside_at_hi": float("nan")}
    if n == 0:
        return blank
    m = need(share, n)
    smin, smax = np.sort(kmin), np.sort(kmax)

    def inside(v):
        v = np.asarray(v, dtype=float)
        return np.searchsorted(smin, v, "right") - np.searchsorted(smax, v, "left")

    lo_c, hi_c = smin[inside(smin) >= m], smax[inside(smax) >= m]
    if lo_c.size == 0 or hi_c.size == 0:
        return blank
    lo, hi = float(lo_c.min()), float(hi_c.max())
    pts = np.unique(np.concatenate([smin, smax]))
    pts = pts[(pts >= lo) & (pts <= hi)]
    mids = (pts[:-1] + pts[1:]) / 2.0
    contiguous = bool((inside(pts) >= m).all() and (inside(mids) >= m).all())
    return {"n_days": n, "k_lo": lo, "k_hi": hi, "contiguous": contiguous,
            "inside_at_lo": float(inside(lo)) / n, "inside_at_hi": float(inside(hi)) / n}


def quantile(values: Sequence[float], p: float) -> float:
    """The inverted empirical CDF at p (p = 0 the least); NaN on an empty sample."""
    v = np.sort(np.asarray(values, dtype=float))
    if v.size == 0:
        return float("nan")
    return float(v[max(int(math.ceil(float(p) * v.size - 1e-9)), 1) - 1])


# ------------------------------------------------------------------------------------------------ the file


def summarise(t: pd.DataFrame, caps: Mapping[str, Any]) -> pd.DataFrame:
    """The result file's rows (`COLUMNS`, sections `SECTIONS` in order) from the day table with its trailing ranges."""
    F, C = int(caps["floor_ticks"]), int(caps["cap_ticks"])
    check_days(t["date"].astype(str).tolist())
    counts = day_counts(t)
    rows: list[dict[str, Any]] = []
    for s in SESSIONS:
        for kind in COUNT_KINDS:
            rows.append({"section": "days", "session": s, "count_kind": kind, "count": counts[s][kind]})
    bounds = {}
    for s in SESSIONS:
        T = t.loc[population(t, s), f"trail_{s}"].to_numpy(float)
        bounds[s] = k_bounds(T, F, C) if T.size else (np.array([]), np.array([]))
    for s in SESSIONS:
        for q in SHARES:
            r = k_range(*bounds[s], q)
            if r.pop("n_days") != counts[s]["population"]:
                raise ValueError(f"{s}: the translation's days are not the population's")
            rows.append({"section": "range_k", "session": s, "share": q, **r})
    for s in SESSIONS:
        kmin = bounds[s][0]
        for p in PROBS:
            rows.append({"section": "k_quantile", "session": s, "prob": p, "k_floor": quantile(kmin, p)})
    out = pd.DataFrame(rows, columns=list(COLUMNS))
    out["count"] = out["count"].astype("Int64")
    out["contiguous"] = out["contiguous"].astype("boolean")
    return out


def output_problems(frame: pd.DataFrame) -> list[str]:
    """Why a frame is not this reading's: columns not `COLUMNS`, a level-named column, a section or session missing,
    the day counts not a partition, a share or probability outside [0, 1], k_lo above k_hi, a quantile out of order."""
    from extended.price_levels import is_level_name

    bad = []
    if list(frame.columns) != list(COLUMNS):
        bad.append(f"columns are not COLUMNS: {list(frame.columns)}")
    names = [c for c in frame.columns if is_level_name(str(c))]
    if names:
        bad.append(f"level-named columns {names}")
    if bad:
        return bad
    if set(frame["section"]) != set(SECTIONS):
        bad.append(f"sections {sorted(set(frame['section']))}, not {list(SECTIONS)}")
    for sec in SECTIONS:
        have = set(frame.loc[frame["section"] == sec, "session"])
        if have != set(SESSIONS):
            bad.append(f"section {sec}: sessions {sorted(have)}")
    d = frame[frame["section"] == "days"]
    for s in SESSIONS:
        c = dict(zip(d.loc[d["session"] == s, "count_kind"], d.loc[d["session"] == s, "count"]))
        if set(c) != set(COUNT_KINDS):
            bad.append(f"days {s}: kinds {sorted(c)}")
            continue
        if c["kind_out"] + c["void"] + c["no_trail"] + c["population"] != c["stored"] or min(c.values()) < 0:
            bad.append(f"days {s}: the counts do not partition the stored days")
    for col in ("share", "prob", "inside_at_lo", "inside_at_hi"):
        x = pd.to_numeric(frame[col], errors="coerce").dropna()
        if ((x < 0) | (x > 1)).any():
            bad.append(f"{col} outside [0, 1]")
    rk = frame[frame["section"] == "range_k"]
    lo, hi = pd.to_numeric(rk["k_lo"], errors="coerce"), pd.to_numeric(rk["k_hi"], errors="coerce")
    both = lo.notna() & hi.notna()
    if (lo[both] > hi[both]).any() or (lo[both] <= 0).any():
        bad.append("a range_k row with k_lo above k_hi or not positive")
    kq = frame[frame["section"] == "k_quantile"]
    for s in SESSIONS:
        q = kq[kq["session"] == s].sort_values("prob")
        for col in ("k_floor",):
            x = pd.to_numeric(q[col], errors="coerce").dropna()
            if not x.is_monotonic_increasing:
                bad.append(f"k_quantile {s}: {col} out of order")
    return bad


def manifest_parameters(caps: Mapping[str, Any], *, identities: Mapping[str, str],
                        span: tuple[date, date]) -> dict[str, Any]:
    """The manifest's parameters: everything the loader checks, and the declared rules of the reading."""
    return {
        "task": TASK, "decisions": list(DECISIONS), "span": [span[0].isoformat(), span[1].isoformat()],
        "purpose": PURPOSE, "read_row": READ_ROW,
        "caps": {"floor_ticks": int(caps["floor_ticks"]), "cap_ticks": int(caps["cap_ticks"])},
        "caps_detail": {k: caps[k] for k in caps if k not in ("floor_ticks", "cap_ticks")},
        "tick": TICK, "trail_days": TRAIL, "walked_kinds": list(WALKED_KINDS), "sessions": list(SESSIONS),
        "lever_sessions": dict(LEVER_SESSIONS),
        "void_rule": {s: {"reads_overnight": ro, "reads_0829": r} for s, (ro, r) in VOID_RULE.items()},
        "ny_range": "trail20_range_pts (Q-121 / RD-04): the walker day's range, 20 prior walked sessions",
        "overnight_range": "the session window's own range (anchored per date), 20 prior walked non-void days",
        "translation": "k inside the caps on d iff floor x tick <= k x T(d) <= cap x tick (unrounded, inclusive)",
        "share_declared": SHARE, "shares": list(SHARES), "probs": list(PROBS), "quantile_rule": QUANTILE_RULE,
        "identities": dict(identities),
    }


# ------------------------------------------------------------------------------------------------ Q-121's identity


def q121_like_rows(t: pd.DataFrame) -> list[dict[str, str]]:
    """Q-121's `range` rows by year for `trail20_range_pts`, rebuilt from `ny`'s trailing range (the tests' fixture
    and the identity's other side): its walked sessions with a finite value, by the trading day's year."""
    walked = t[t["day_kind"].isin(WALKED_KINDS)]
    years = pd.to_datetime(walked["date"]).dt.year.astype(str)
    out = []
    for y in sorted(years.unique()):
        q = V.value_quantiles(walked.loc[(years == y).to_numpy(), "trail_ny"].to_numpy(float))
        out.append({"section": "range", "period_kind": "year", "period": y, "measure": Q121_MEASURE,
                    **{k: str(q[k]) for k in ("n", "median", "p10", "p90")}})
    return out


def q121_problems(t: pd.DataFrame, rows: Sequence[Mapping[str, str]], *, tol: float = Q121_TOL) -> list[str]:
    """`ny`'s `trail20_range_pts` by year against Q-121's admitted `range` rows (`period_kind` year, the measure
    `trail20_range_pts`): the count equal, the median, p10 and p90 within `tol` relative, for every year of `t`."""
    want = {r["period"]: r for r in rows if r.get("section") == "range" and r.get("period_kind") == "year"
            and r.get("measure") == Q121_MEASURE and r.get("period") in Q121_YEARS}
    bad = []
    for mine in q121_like_rows(t):
        y = mine["period"]
        if y not in want:
            bad.append(f"q121: no admitted row for {y}")
            continue
        w = want[y]
        if int(float(w["n"])) != int(mine["n"]):
            bad.append(f"q121 {y}: the counts differ")
        for k in ("median", "p10", "p90"):
            a, b = float(w[k]), float(mine[k])
            if not (math.isclose(a, b, rel_tol=tol, abs_tol=0.0) or (math.isnan(a) and math.isnan(b))):
                bad.append(f"q121 {y}: {k} differs")
    if not want:
        bad.append("q121: no admitted row at all")
    return bad


# ------------------------------------------------------------------------------------------------ the loader


def manifest_path(path: Path | str) -> Path:
    return Path(str(path) + ".manifest.json")


def load_range(path: Path | str, *, caps: Mapping[str, Any], share: float = SHARE) -> dict[str, Any]:
    """Each session's k range at `share` from the result file, after its manifest (the docstring's loader). `NotRead`
    when the file or its manifest is absent; `RangeRefused` for anything else that is not this reading's."""
    p = Path(path)
    mp = manifest_path(p)
    if not p.is_file() or not mp.is_file():
        raise NotRead(f"{TASK}: no S1 reading at {p} (with its manifest) yet")
    raw = p.read_bytes()
    try:
        m = json.loads(mp.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise RangeRefused(f"{mp}: the manifest is not JSON ({exc})") from None
    sha = hashlib.sha256(raw).hexdigest()
    why = []
    if m.get("sha256") != sha:
        why.append("its sha256 is not the manifest's")
    if m.get("script") != SCRIPT:
        why.append(f"its script is {m.get('script')!r}, not {SCRIPT}")
    if m.get("git_dirty") is not False or str(m.get("git_commit", "")).endswith("-dirty"):
        why.append("it was written from a dirty tree")
    clean = (m.get("provenance") or {}).get("clean_run")
    if not (isinstance(clean, dict) and clean.get("name")):
        why.append("it is not a clean run's (no provenance.clean_run)")
    par = m.get("parameters") or {}
    if par.get("task") != TASK:
        why.append(f"its task is {par.get('task')!r}")
    if par.get("span") != [SEARCH_START.isoformat(), SEARCH_END.isoformat()]:
        why.append(f"its span {par.get('span')} is not the whole search years")
    ids = par.get("identities") or {}
    if not ids or any(v != "HELD" for v in ids.values()):
        why.append(f"its identities {ids} did not all hold")
    got_caps = par.get("caps") or {}
    if (got_caps.get("floor_ticks"), got_caps.get("cap_ticks")) != (int(caps["floor_ticks"]), int(caps["cap_ticks"])):
        why.append("its caps are not stop_caps() now (a rule changed since the reading)")
    if par.get("share_declared") != share:
        why.append(f"its declared share {par.get('share_declared')} is not {share}")
    if why:
        raise RangeRefused(f"REFUSED ({TASK}): {p} is not this reading's -- " + "; ".join(why))
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    by: dict[str, tuple[float, float]] = {}
    n_days: dict[str, int] = {}
    for s in SESSIONS:
        pop = [r for r in rows if r.get("section") == "days" and r.get("session") == s
               and r.get("count_kind") == "population"]
        if len(pop) != 1 or not pop[0].get("count"):
            raise RangeRefused(f"REFUSED ({TASK}): {p}: no single population count for {s}")
        n_days[s] = int(float(pop[0]["count"]))
        hit = [r for r in rows if r.get("section") == "range_k" and r.get("session") == s
               and r.get("share") not in (None, "") and math.isclose(float(r["share"]), share)]
        if len(hit) != 1:
            raise RangeRefused(f"REFUSED ({TASK}): {p}: {len(hit)} range_k rows for {s} at share {share}")
        r = hit[0]
        lo, hi = float(r["k_lo"] or "nan"), float(r["k_hi"] or "nan")
        if not (math.isfinite(lo) and math.isfinite(hi) and 0 < lo < hi) or r.get("contiguous") != "True":
            raise RangeRefused(f"REFUSED ({TASK}): {s}'s k range at share {share} does not load (blank, empty or "
                               "gapped)")
        by[s] = (lo, hi)
    return {"by_session": by, "n_days": n_days, "share": share, "sha256": sha, "git_commit": m.get("git_commit"),
            "manifest": str(mp)}


__all__ = ["TASK", "DECISIONS", "RESULT", "SCRIPT", "PURPOSE", "READ_ROW", "SEARCH_START", "SEARCH_END", "TICK",
           "TRAIL", "SESSIONS", "OVERNIGHT", "LEVER_SESSIONS", "VOID_RULE", "SHARE", "SHARES", "PROBS",
           "QUANTILE_RULE", "SECTIONS", "COUNT_KINDS", "COLUMNS", "BeyondSearchYears", "ConfirmationWindowRefused",
           "NotRead", "RangeRefused", "check_span", "check_days", "session_windows", "window_range", "day_table",
           "trailing_ranges", "eligible", "add_trailing", "population", "day_counts", "k_bounds", "need", "k_range",
           "quantile", "summarise", "output_problems", "manifest_parameters", "q121_like_rows", "q121_problems",
           "manifest_path", "load_range"]
