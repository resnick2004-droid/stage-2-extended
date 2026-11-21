"""T7's admission forecast: the chance that a mark's bracket is still open at the walk's end (reaches the flatten),
F-R's HAR form (`prereg/DRAFT_F-R_resolution.md` 6.1-6.5) refitted on the **search years only** (2020-01-02 to
2023-12-29, E-208; every model built and chosen there, any number of internal time splits, E-221 O-1) -- the lever
table's row T7 and section 6 (`docs/plans/LEVER_TABLE_topstep50k.md`): "offer a mark only when it is forecast to
resolve", i.e. admit a mark at a bracket iff its forecast chance of reaching the flatten open is at most D-212's line.

    from extended import t7_forecast as T
    T.check_span("2020-01-02", "2023-12-29")                    # refuses any day after 2023-12-29
    days, O, H, L, C = T.day_grid(bars)                          # a frame's bars as [day, slot] arrays
    stats = T.window_stats(O, H, L, C)                           # per (day, mark): the window's IV and excursions
    t = T.feature_table(days, stats, kinds=kinds, voids=voids)   # one row per (frame day, mark): band, y, x1-x3
    frame, model = T.run_fit(t, q)                               # out-of-fold calibration, the final fit, the file
    T.load_forecast(path, q=q)                                   # the loader's read, by the manifest (lever_space)

This module imports no engine and reads no bar or file of data (`admission_line` reads one vendored config value, and
`load_forecast` the result file): `scripts/t7_fit.py` reads the bars through `extended.reader`, runs the identities and
writes the file through `extended.results`. **Fitting is a pure function of a feature table.**

**The clock** (`extended.features`' and the store's): a trading day opens at 17:00 CT the evening before; a slot is
minutes after that 17:00, Chicago wall clock; a bar stamped s covers s .. s+1 and closes at s+1. **The marks** `MARKS`:
every five minutes from the reopen (slot 0) to 15:05 CT (slot 1325). At mark m the alert is t = m - 5 (`ALERT_LAG`, the
reference latency L = 5) and **every feature reads bars stamped at or before m - 6 = t - 1** -- so it is causal at every
declared latency (5, 3, 2: an alert at m - 3 or m - 2 is later still). The entry is the open of the first bar stamped
at or after m (F-R 5.2); the walk ends on the bar ending 15:08 CT (`WALK_LAST_STAMP`, `walker.FLAT_ENTRY` - 1).

**The window's quantities** (`window_stats`; F-R 6.1), per (day, mark), from day d's bars stamped e .. 15:07, e the
entry bar: **IV** = (C_e - O_e)^2 + the sum of squared changes of each later present bar's close from the previous
present bar's close (points^2; within one day, so never across a roll); **up** = max high - O_e and **dn** = O_e - min
low over the same bars (the label's excursions). And the trailing hour's **rv_60** at an alert a: the root mean square
of the one-minute close changes of the day's bars stamped a - 60 .. a - 1 (at least two changes; bounded at the day's
first bar) -- exactly `extended.features`' `rv_60`; at the live alert m - 5 (`rv_live`) and at the frozen alert 08:25
(`rv_frozen`, slot 925, bars stamped at or before 08:24).

**The frame and the population** (`feature_table`): the frame is the walked sessions (Stage 2 A1's day kinds 'n', 'b';
`WALKED_KINDS`) of the read, in date order; every trailing term runs over the frame only (F-R 6.2). The void calendar
(`extended.day_calendar.day_flags`, E-231, E-232) is a **population filter**, as in S1: a (day, mark) whose band's
`VOID_RULE` voids the day has no IV, no rv and no row in the fit, and never enters a trailing term.

**The regressors** (F-R 6.2, every one from the past only; the frame's days before d):

| term | formula | reads |
|---|---|---|
| M (the normaliser) | the mean of IV(d', m) over the 22 most recent earlier frame days with a value | those days' windows m .. 15:07 |
| y (the target) | log(IV(d, m) / M) | day d's bars stamped e .. 15:07 -- the label, never a feature |
| x1 | log(IV(d', m) / M), d' the most recent earlier frame day with a value | that day's window |
| x2 | log(the mean of IV over the 5 most recent earlier frame days with a value / M) | those days' windows |
| x3 | 2 log(rv_60 / its median at the same alert over the 20 prior frame days, at least 10 with a value) = 2 x `rv_tod` | day d's bars stamped a - 60 .. a - 1; the 20 prior days' same slots |

M, x1, x2 missing (fewer than 22 earlier values), or x3 missing where the band uses it, or the day void: no forecast
(`has_forecast` False), never admitted. `reach` is the earliest frame day any of a row's features read (the purge's
input).

**The bands** (F-R 6.3; `BANDS`), each with its own coefficients: `evening` (the reopen to asia's anchor; x1, x2 only),
`asia` (to london's anchor), `london` (to 08:30 CT), with the overnight anchors per date (`day_calendar.anchored_starts`,
E-231 (3), in place of F-R's fixed CT clocks); `open` (08:30-09:00), `day1` (09:05-10:05) -- x3 **frozen** at the 08:25
alert, so no input of an opening-window mark reads a bar of its day stamped 08:30-08:59 (E-030); `day` (10:10-15:05),
x3 live. **The fit:** ordinary least squares of y on an intercept and the band's terms, one observation per (day, mark)
with a forecast and an IV, each weighted one; refused (`FitRefused`) if a band has under `MIN_ROWS` rows or a
rank-deficient design.

**From a variance forecast to the chance of being open** (F-R 6.4). V_hat = M exp(y_hat). A bracket of stop S and
target w S has u = V_hat / S^2 and the driftless textbook chance of still being open after integrated variance u,
**Psi_w(u)** (`psi`: the series of F-R section 1 (i), or the method of images below `U_SWITCH`; clipped to
[`CLIP`, 1 - `CLIP`]). **Calibrated per band:** p_hat = sigmoid(alpha + beta logit Psi_w(u)), alpha and beta by maximum
likelihood on the training rows' own fitted forecasts, applied out of fold. Under exact Brownian motion with a perfect
forecast alpha = 0, beta = 1.

* **The calibration brackets** (an interpretation: F-R calibrated at one 150-tick stop; the lever space's stops vary
  with S1): every stop S = c sqrt(M) for c in `C_GRID` (the stop in units of the window's trailing typical move, so u =
  exp(y_hat) / c^2 -- no price, no stop in points) and every w of S2's grid (`W_GRID`, declared here and checked
  against RD-05 2.6's `modes_terms.grid_w` by the loader and the tests), both sides pooled (the coin chooses the
  side), every bracket weighted one. **A stop or a w outside the calibrated grid is refused, never extrapolated**
  (`probability_open` gives NaN, which `admit` never admits).
* **The label** (`open_counts`): with E the entry, a long is open at the walk's end iff no bar from the entry bar to
  15:07 traded at E - S (a stop fills on a touch) and none traded at E + w S + one tick (a limit target fills only on a
  trade through by a tick); the short mirrored. No breakeven move (the lever table drops S7). It reads the walk's
  excursions only -- never a side's P&L.
* **Label: a market entry only.** The label models a market entry at the open of the mark's first bar, held to the
  bar stamped 15:07. It does not model a limit entry (T5), the news-window flatten (E-202 (2)(a)), entries off the
  five-minute grid (P-14's) or RL3's ticket timing; a T7 result is reported with this beside it.
* **Label: q's provenance.** q = D-212's line as D-308 raised it (5 %): Stage 2 chose that number after D-306's result
  was seen (on 2020-2021, inside the search years) and labels it so; it was a ceiling on a leg's share of trades
  reaching the flatten, used here per mark, which is far stricter. Both facts are reported beside any T7 result.

**The splits** (`fold_masks`; feature-rules section 4): test folds are the search years' calendar years `FOLD_YEARS`;
a fold's training rows are every other search-year row at least `PURGE_SESSIONS` frame sessions before the fold's
first day, or at least `EMBARGO_SESSIONS` after its last **and** whose features read no day of the fold (`reach`). Each
label resolves within its own session (one session is the longest trade), so 22 sessions -- the HAR's longest window --
is longer than the longest trade and than the longest feature window. Out of fold: the HAR's R^2 per band and fold,
and the calibration (mean p_hat, open share, log loss, Brier, a reliability table by `BIN_EDGES`, each bracket's
shares, and at q the share admitted and the open share among the admitted). **These are diagnostics, not a forward
test:** the folds include backward ones (2020 is fitted on 2021-2023). The final model is fitted on every search-year
row.

**Which model applies where (the lead's ruling).** On the search years a mark of year Y is scored by **fold Y's model**
(trained without year Y, purged and embargoed) -- never by the final model, which would be in-sample there
(`model_for`). The final all-years model is only for a later held-out application, which stays refused here (it is a
declared purpose of the joint held-out test, with its own feature builder holding to `feature_table` on the search
years first).

**The file** (`COLUMNS`, long format, one numeric column `value`; `SECTIONS`): `coef` and `calib` (each fold's and the
final fit's), `count`, `oof`, `reliability`, `bracket`. Counts are never on a row with a share. No date, no clock time,
no price, no range in points: every value is a coefficient on log ratios, a probability, a share, a loss or a count, so
**nothing in it inverts to a price range in points**; the licence guard (`extended.price_levels`) is run on it by the
tests.

**The loader** (`load_forecast`, called by `lever_space` for T7): the file and its sidecar manifest must both exist
(else `NotRead`, which the lever space reports as `NotComputed`); then it is refused (`ForecastRefused`) unless the
manifest's sha256 is the file's, its script this reading's, its tree clean and its run a clean run, its task, purpose
and read row this reading's, the whole search years, every identity held, its q equal to D-212's line now
(`admission_line`), **every declared parameter of `manifest_parameters` equal to its value now** (the alert lag, the
marks, the frozen alert, the walk's end, the bands, terms and void rules, the windows, the c and w grids, the folds,
purge and embargo, the bins), `W_GRID` equal to RD-05's grid now, its `git_commit` a named commit of this repository
(40 hexadecimal characters, not dirty, present in its history), the file's sections and folds exactly those `run_fit`
writes with `output_problems` empty, and every band of every fold's model and of the final model finite with beta > 0
(admission then falls as w rises, F-R 6.5). It returns each fold's model and the final model, labelled.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import ROOT, VENDOR_STAGE2
from extended import day_calendar as DC
from extended import features as FL
from extended import reader as R                      # constants and the refusal class only: no read here
from extended import walker as W

TASK = "T7"
DECISIONS = ("E-208", "E-211", "E-221")
RESULT = "t7_forecast"
SCRIPT = "scripts/t7_fit.py"
#: the reader's purpose: a fit on the search years (its choice words keep it off the held-out years whatever a
#: declaration says -- the reader's H-2 rule), under E-221 O-1 (every model built, tuned and chosen on the search
#: years only, any number of internal time splits)
PURPOSE = "t7_admission_forecast_fit_search_years"
READ_ROW = "E-221"
SEARCH_START, SEARCH_END = R.CHOICE_START, R.CHOICE_END
TICK = 0.25
WALKED_KINDS = ("n", "b")
N_SLOTS = FL.N_SLOTS
WALK_LAST_STAMP = W.FLAT_ENTRY - 1                    # 1327: the bar stamped 15:07, ending 15:08 CT
ALERT_LAG = 5
MARK_STEP = 5
LAST_MARK = FL.slot(15, 5)
MARKS = np.arange(0, LAST_MARK + 1, MARK_STEP)
FROZEN_ALERT = FL.slot(8, 25)                         # 925: the 08:30 mark's alert
RTH_OPEN = FL.slot(8, 30)                             # 930
OPEN_LAST, DAY1_LAST = FL.slot(9, 0), FL.slot(10, 5)
RV_WINDOW = 60
HAR_DAILY, HAR_WEEKLY, HAR_MONTHLY = 1, 5, 22
TOD_DAYS, TOD_MIN_DAYS = FL.TOD_DAYS, FL.TOD_MIN_DAYS
BANDS = ("evening", "asia", "london", "open", "day1", "day")
FROZEN_BANDS = ("open", "day1")
TERMS = {b: (("x1", "x2") if b == "evening" else ("x1", "x2", "x3")) for b in BANDS}
#: (reads_overnight, reads_0829) for `day_calendar.day_flags`, per band: the overnight bands' windows run through the
#: 08:29 bar; the opening bands' frozen x3 reads overnight bars (to 08:24); the day band reads the regular session only
VOID_RULE = {"evening": (True, True), "asia": (True, True), "london": (True, True), "open": (True, False),
             "day1": (True, False), "day": (False, False)}
#: the calibration brackets: stops in units of sqrt(M), and S2's w grid (RD-05 2.6), declared here (frozen) and
#: checked against `modes_terms.grid_w()` by the loader
C_GRID = (0.5, 0.75, 1.0, 1.5, 2.0)
W_GRID = (1.0, 1.5, 2.0, 3.0)
CLIP = 1e-6
U_SWITCH = 1.0
SERIES_TERMS = 50
IMAGE_TERMS = 20
MIN_ROWS = 50
FOLD_YEARS = tuple(range(SEARCH_START.year, SEARCH_END.year + 1))
PURGE_SESSIONS = 22
EMBARGO_SESSIONS = 22
BIN_EDGES = (0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0)
SECTIONS = ("coef", "calib", "count", "oof", "reliability", "bracket")
COLUMNS = ("section", "band", "fold", "bracket", "bin", "stat", "value")
FINAL = "final"
OOF = "oof"
#: D-212's line (D-212 (2) as D-308 raised it): Stage 2's vendored config, the key below
Q_CONFIG = "config/fv3_corrected_portfolio.yaml"
Q_KEY = ("selection", "feasibility", "flat_share_max")
Q_NOTE_KEY = ("selection", "feasibility", "flat_share_note")


def w_grid() -> tuple[float, ...]:
    """RD-05 2.6's w grid now (`modes_terms.grid_w`), which `W_GRID` must equal."""
    from extended import modes_terms as M                # light: declared values only

    return tuple(float(x) for x in M.grid_w())


class BeyondSearchYears(RuntimeError):
    """A span or a frame reaching past the search years (2023-12-29): this reading never reads the held-out years."""


class ConfirmationWindowRefused(BeyondSearchYears, R.ConfirmationWindowRefused):
    """A day from 2026-07-17 on: refused always."""


class FitRefused(RuntimeError):
    """A band that cannot be fitted (too few rows, a rank-deficient design, a likelihood that does not converge)."""


class NotRead(FileNotFoundError):
    """The loader: no result file (or no manifest beside it) yet."""


class ForecastRefused(RuntimeError):
    """The loader: a file present but not this reading's, or D-212's line not readable."""


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
        raise BeyondSearchYears(f"REFUSED ({TASK}): T7's forecast is fitted on the search years only ({SEARCH_START} "
                                f"to {SEARCH_END}, E-208, E-221); {s} to {e} reaches {max(s, e)}")
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


# ------------------------------------------------------------------------------------------------ the textbook law


def psi_series(b: Any, u: Any, terms: int = SERIES_TERMS) -> np.ndarray:
    """The chance a driftless Brownian motion from 0 has left neither -1 nor b after integrated variance u (F-R 1 (i)):
    the sum over odd n of 4 / (n pi) sin(n pi / (1 + b)) exp(-n^2 pi^2 u / (2 (1 + b)^2))."""
    b, u = np.broadcast_arrays(np.asarray(b, dtype=float), np.asarray(u, dtype=float))
    w = 1.0 + b
    out = np.zeros(b.shape)
    for n in range(1, 2 * terms, 2):
        out += 4.0 / (n * math.pi) * np.sin(n * math.pi / w) * np.exp(-(n * math.pi) ** 2 * u / (2.0 * w * w))
    return out


def psi_images(b: Any, u: Any, terms: int = IMAGE_TERMS) -> np.ndarray:
    """The same chance by the method of images on (-1, b), width W = 1 + b: the sum over k of
    Phi((b + 2kW)/s) - Phi((-1 + 2kW)/s) - Phi((b + 2 + 2kW)/s) + Phi((1 + 2kW)/s), s = sqrt(u)."""
    from scipy.special import ndtr

    b, u = np.broadcast_arrays(np.asarray(b, dtype=float), np.asarray(u, dtype=float))
    w = 1.0 + b
    s = np.sqrt(np.maximum(u, 1e-300))
    out = np.zeros(b.shape)
    for k in range(-terms, terms + 1):
        sh = 2.0 * k * w
        out += ndtr((b + sh) / s) - ndtr((-1.0 + sh) / s) - ndtr((b + 2.0 + sh) / s) + ndtr((1.0 + sh) / s)
    return out


def psi(b: Any, u: Any) -> np.ndarray:
    """Psi_b(u): the images below `U_SWITCH`, the series at and above it; 1 at u <= 0."""
    b, u = np.broadcast_arrays(np.asarray(b, dtype=float), np.asarray(u, dtype=float))
    out = np.ones(b.shape)
    lo = (u > 0) & (u < U_SWITCH)
    hi = u >= U_SWITCH
    if lo.any():
        out[lo] = psi_images(b[lo], u[lo])
    if hi.any():
        out[hi] = psi_series(b[hi], u[hi])
    return np.clip(out, 0.0, 1.0)


def logit(p: Any) -> np.ndarray:
    p = np.clip(np.asarray(p, dtype=float), CLIP, 1.0 - CLIP)
    return np.log(p / (1.0 - p))


def sigmoid(z: Any) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    return 0.5 * (1.0 + np.tanh(0.5 * z))


# ------------------------------------------------------------------------------------------------ the bars


def day_grid(bars: pd.DataFrame) -> tuple[list[date], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """A frame's bars as [trading day, slot] arrays (NaN where no bar), days sorted -- the clock of
    `extended.features.grid`; the `day` column, if present, is checked against `ts`."""
    ts = bars["ts"].to_numpy(np.int64)
    if len(ts) == 0:
        raise ValueError("no bars")
    if (ts % 60).any():
        raise ValueError("a bar's ts is not a whole minute")
    shifted = (pd.to_datetime(ts, unit="s", utc=True).tz_convert(FL.CHICAGO).tz_localize(None)
               + pd.Timedelta(hours=7))
    dkey = shifted.normalize().to_numpy().astype("datetime64[D]")
    slotv = (shifted.hour * 60 + shifted.minute).to_numpy(np.int64)
    if "day" in bars.columns:
        if not np.array_equal(bars["day"].astype(str).to_numpy(), np.datetime_as_string(dkey, unit="D")):
            raise ValueError("the bars' `day` disagrees with their ts (trading day = Chicago time + 7 hours, its date)")
    uniq, di = np.unique(dkey, return_inverse=True)
    days = [pd.Timestamp(x).date() for x in uniq]
    check_days(days)
    flat = di * N_SLOTS + slotv
    if len(np.unique(flat)) != len(flat):
        raise ValueError("two bars share a trading day and minute")
    out = []
    for col in ("open", "high", "low", "close"):
        a = np.full(len(uniq) * N_SLOTS, np.nan)
        a[flat] = bars[col].to_numpy(dtype=float)
        out.append(a.reshape(len(uniq), N_SLOTS))
    return (days, *out)


def _close_changes(C: np.ndarray) -> np.ndarray:
    """Each bar's close less the previous present bar's close of the same day (NaN with no bar or no earlier bar)."""
    idx = np.where(~np.isnan(C), np.arange(C.shape[1]), -1)
    np.maximum.accumulate(idx, axis=1, out=idx)
    ff = np.take_along_axis(C, np.maximum(idx, 0), axis=1)
    ff[idx < 0] = np.nan
    prev = np.concatenate([np.full((C.shape[0], 1), np.nan), ff[:, :-1]], axis=1)
    return C - prev


def rv_at(dC: np.ndarray, alerts: Sequence[int], window: int = RV_WINDOW) -> np.ndarray:
    """rv_60 at each alert slot a: sqrt(mean of dC^2 over the day's slots max(0, a - window) .. a - 1), at least two
    changes, else NaN; NaN at a < 1 (no bar of the day closed). `extended.features`' formula."""
    ok = ~np.isnan(dC)
    cs2 = np.cumsum(np.where(ok, dC * dC, 0.0), axis=1)
    csn = np.cumsum(ok, axis=1, dtype=np.int64)
    out = np.full((dC.shape[0], len(alerts)), np.nan)
    for k, a in enumerate(alerts):
        a = int(a)
        if a < 1:
            continue
        lo = a - window
        s2 = cs2[:, a - 1] - (cs2[:, lo - 1] if lo >= 1 else 0.0)
        n = csn[:, a - 1] - (csn[:, lo - 1] if lo >= 1 else 0)
        with np.errstate(divide="ignore", invalid="ignore"):
            out[:, k] = np.where(n >= 2, np.sqrt(s2 / np.maximum(n, 1)), np.nan)
    return out


def window_stats(O: np.ndarray, H: np.ndarray, L: np.ndarray, C: np.ndarray) -> dict[str, np.ndarray]:
    """Per (day, mark of `MARKS`): `iv`, `up`, `dn` of the window from the entry bar (the first bar stamped at or
    after the mark) to the bar stamped `WALK_LAST_STAMP` (NaN with no entry bar), and `rv_live` (rv_60 at the alert
    m - 5); per day, `rv_frozen` (rv_60 at 08:25)."""
    n = O.shape[0]
    E = WALK_LAST_STAMP
    Cw, Ow, Hw, Lw = C[:, :E + 1], O[:, :E + 1], H[:, :E + 1], L[:, :E + 1]
    present = ~np.isnan(Cw)
    idx = np.where(present, np.arange(E + 1), E + 1)
    nxt = np.minimum.accumulate(idx[:, ::-1], axis=1)[:, ::-1]
    Hs = np.fmax.accumulate(Hw[:, ::-1], axis=1)[:, ::-1]
    Ls = np.fmin.accumulate(Lw[:, ::-1], axis=1)[:, ::-1]
    dC = _close_changes(C)
    sq = np.where(np.isnan(dC[:, :E + 1]), 0.0, dC[:, :E + 1] ** 2)
    suf = np.concatenate([np.cumsum(sq[:, ::-1], axis=1)[:, ::-1], np.zeros((n, 1))], axis=1)   # suf[j] = sum j..E
    e = nxt[:, MARKS]
    valid = e <= E
    ec = np.minimum(e, E)
    rows = np.arange(n)[:, None]
    entry = Ow[rows, ec]
    iv = (Cw[rows, ec] - entry) ** 2 + suf[rows, ec + 1]
    up = Hs[rows, ec] - entry
    dn = entry - Ls[rows, ec]
    for a in (iv, up, dn):
        a[~valid] = np.nan
    return {"iv": iv, "up": up, "dn": dn, "rv_live": rv_at(dC, MARKS - ALERT_LAG),
            "rv_frozen": rv_at(dC, [FROZEN_ALERT])[:, 0]}


# ------------------------------------------------------------------------------------------------ the feature table


def bands_for(days: Sequence[date]) -> np.ndarray:
    """(day, mark) -> index into `BANDS`, with asia's and london's anchors per date."""
    out = np.empty((len(days), len(MARKS)), dtype=np.int8)
    for i, d in enumerate(days):
        a = DC.anchored_starts(d)
        if a["ny"] != RTH_OPEN or not 0 < a["asia"] < a["london"] < RTH_OPEN:
            raise ValueError(f"{d}: the session anchors are out of order ({a})")
        out[i] = np.select([MARKS < a["asia"], MARKS < a["london"], MARKS < RTH_OPEN, MARKS <= OPEN_LAST,
                            MARKS <= DAY1_LAST], [0, 1, 2, 3, 4], 5)
    return out


def prior_means(X: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Per column: the mean of the k most recent EARLIER finite values (row i itself never read) and the row of the
    earliest of them; NaN / -1 with fewer than k."""
    n, m = X.shape
    out = np.full((n, m), np.nan)
    first = np.full((n, m), -1, dtype=np.int64)
    for j in range(m):
        ok = np.isfinite(X[:, j])
        rows = np.flatnonzero(ok)
        cs = np.concatenate([[0.0], np.cumsum(X[rows, j])])
        c = np.cumsum(ok) - ok                           # finite values strictly before row i
        has = c >= k
        out[has, j] = (cs[c[has]] - cs[c[has] - k]) / k
        first[has, j] = rows[c[has] - k]
    return out, first


def feature_table(days: Sequence[date], stats: Mapping[str, np.ndarray], *, kinds: Mapping[date, str] | None = None,
                  voids: Mapping[str, Sequence[bool]] | None = None) -> pd.DataFrame:
    """One row per (frame day, mark): `date`, `day_index` (in the frame), `mark` (slot), `band`, `has_forecast`, the
    target `y`, the features `x1`, `x2`, `x3`, `reach`, and the label's normalised excursions `up_n`, `dn_n`, `tick_n`
    (each over sqrt(M)). `kinds` (A1's day kind by date; None: every day walked) sets the frame; `voids` (band ->
    a flag per day of `days`; None: none) the population filter."""
    days = [_day(d) for d in days]
    check_days(days)
    if any(b <= a for a, b in zip(days, days[1:])):
        raise ValueError("the days are not in strictly increasing order")
    keep = np.array([kinds is None or kinds.get(d) in WALKED_KINDS for d in days], dtype=bool)
    ix = np.flatnonzero(keep)
    fd = [days[i] for i in ix]
    nf, K = len(fd), len(MARKS)
    band = bands_for(fd) if nf else np.empty((0, K), dtype=np.int8)
    void = np.zeros((nf, K), dtype=bool)
    void_frozen = np.zeros(nf, dtype=bool)
    if voids is not None:
        for bi, b in enumerate(BANDS):
            v = np.asarray(voids[b], dtype=bool)[ix]
            void |= (band == bi) & v[:, None]
        void_frozen = np.asarray(voids[FROZEN_BANDS[0]], dtype=bool)[ix]
    iv = np.asarray(stats["iv"], dtype=float)[ix]
    with np.errstate(invalid="ignore"):
        ivv = np.where(void | ~(iv > 0), np.nan, iv)
    p1, _ = prior_means(ivv, HAR_DAILY)
    p5, _ = prior_means(ivv, HAR_WEEKLY)
    m22, reach22 = prior_means(ivv, HAR_MONTHLY)
    rl = np.where(void, np.nan, np.asarray(stats["rv_live"], dtype=float)[ix])
    rf = np.where(void_frozen, np.nan, np.asarray(stats["rv_frozen"], dtype=float)[ix])
    with np.errstate(divide="ignore", invalid="ignore"):
        ml = FL._prior_median(rl, TOD_DAYS, TOD_MIN_DAYS) if nf else rl
        mf = FL._prior_median(rf[:, None], TOD_DAYS, TOD_MIN_DAYS)[:, 0] if nf else rf
        x3_live = 2.0 * np.log(rl / ml)
        x3_frozen = 2.0 * np.log(rf / mf)
        frozen = np.isin(band, [BANDS.index(b) for b in FROZEN_BANDS])
        x3 = np.where(frozen, x3_frozen[:, None], x3_live)
        x3[band == BANDS.index("evening")] = np.nan
        y = np.log(ivv / m22)
        x1 = np.log(p1 / m22)
        x2 = np.log(p5 / m22)
        sq = np.sqrt(m22)
        up_n = np.asarray(stats["up"], dtype=float)[ix] / sq
        dn_n = np.asarray(stats["dn"], dtype=float)[ix] / sq
        tick_n = TICK / sq
    need3 = band != BANDS.index("evening")
    has = np.isfinite(m22) & np.isfinite(x1) & np.isfinite(x2) & (~need3 | np.isfinite(x3)) & ~void
    di = np.repeat(np.arange(nf), K).reshape(nf, K)
    reach = np.where(reach22 >= 0, np.minimum(reach22, di - TOD_DAYS), -1)
    flat = lambda a: np.asarray(a).reshape(-1)  # noqa: E731
    return pd.DataFrame({
        "date": np.repeat([d.isoformat() for d in fd], K), "day_index": flat(di),
        "mark": np.tile(MARKS, nf), "band": np.asarray(BANDS, dtype=object)[flat(band)] if nf else [],
        "has_forecast": flat(has), "y": flat(y), "x1": flat(x1), "x2": flat(x2), "x3": flat(x3),
        "reach": flat(reach), "up_n": flat(up_n), "dn_n": flat(dn_n), "tick_n": flat(tick_n)})


# ------------------------------------------------------------------------------------------------ the splits


def fold_masks(t: pd.DataFrame, year: int, *, purge: int = PURGE_SESSIONS,
               embargo: int = EMBARGO_SESSIONS) -> tuple[np.ndarray, np.ndarray]:
    """(train, test) row masks for the test fold `year`: the test rows are the year's; a training row is outside it,
    at least `purge` frame sessions before its first day, or at least `embargo` after its last and reading no day of
    it (`reach` after the fold)."""
    di = t["day_index"].to_numpy(np.int64)
    yr = pd.to_datetime(t["date"]).dt.year.to_numpy()
    test = yr == int(year)
    if not test.any():
        raise FitRefused(f"no row in the test fold {year}")
    lo, hi = int(di[test].min()), int(di[test].max())
    reach = t["reach"].to_numpy(np.int64)
    before = di < lo - purge
    after = (di > hi + embargo) & (reach > hi)
    return ~test & (before | after), test


def fit_rows(t: pd.DataFrame) -> np.ndarray:
    """The rows a fit may use: a forecast, a finite target and finite excursions."""
    return (t["has_forecast"].to_numpy(bool) & np.isfinite(t["y"].to_numpy(float))
            & np.isfinite(t["up_n"].to_numpy(float)) & np.isfinite(t["dn_n"].to_numpy(float)))


def _design(t: pd.DataFrame, band: str, mask: np.ndarray) -> np.ndarray:
    sel = mask & (t["band"].to_numpy() == band)
    cols = [np.ones(int(sel.sum()))] + [t[c].to_numpy(float)[sel] for c in TERMS[band]]
    return np.column_stack(cols)


def fit_har(t: pd.DataFrame, mask: np.ndarray) -> dict[str, dict[str, float]]:
    """Per band: OLS of y on an intercept and the band's terms over the rows of `mask` that `fit_rows` admits."""
    check_days(t["date"].unique())
    ok = mask & fit_rows(t)
    out = {}
    for b in BANDS:
        X = _design(t, b, ok)
        yv = t["y"].to_numpy(float)[ok & (t["band"].to_numpy() == b)]
        if len(yv) < MIN_ROWS:
            raise FitRefused(f"band {b}: {len(yv)} rows, under {MIN_ROWS}")
        if np.linalg.matrix_rank(X) < X.shape[1]:
            raise FitRefused(f"band {b}: a rank-deficient design")
        coef = np.linalg.lstsq(X, yv, rcond=None)[0]
        out[b] = dict(zip(("const",) + TERMS[b], (float(c) for c in coef)))
    return out


def predict_y(har: Mapping[str, Mapping[str, float]], t: pd.DataFrame) -> np.ndarray:
    """y_hat per row (NaN without a forecast)."""
    out = np.full(len(t), np.nan)
    bands = t["band"].to_numpy()
    has = t["has_forecast"].to_numpy(bool)
    for b in BANDS:
        sel = has & (bands == b)
        c = har[b]
        v = np.full(int(sel.sum()), c["const"])
        for term in TERMS[b]:
            v = v + c[term] * t[term].to_numpy(float)[sel]
        out[sel] = v
    return out


def open_counts(up_n: np.ndarray, dn_n: np.ndarray, tick_n: np.ndarray, c: float, w: float) -> np.ndarray:
    """How many of the two sides of a bracket (stop c, target w c, in units of sqrt(M)) are still open at the walk's
    end: a long is open iff dn < c (no touch of its stop) and up < w c + tick (no trade through its target); a short
    mirrored."""
    long_open = (dn_n < c) & (up_n < w * c + tick_n)
    short_open = (up_n < c) & (dn_n < w * c + tick_n)
    return long_open.astype(np.int8) + short_open.astype(np.int8)


def brackets() -> list[tuple[float, float]]:
    return [(c, w) for c in C_GRID for w in W_GRID]


def bracket_label(c: float, w: float) -> str:
    return f"c{c:g}w{w:g}"


def bracket_obs(t: pd.DataFrame, y_hat: np.ndarray, mask: np.ndarray) -> dict[str, np.ndarray]:
    """Every (row of `mask` with a forecast and a label, bracket) observation: its band, bracket, z = logit Psi_w(u)
    with u = exp(y_hat) / c^2, and k, the open sides of two."""
    ok = mask & fit_rows(t) & np.isfinite(y_hat)
    bands = np.array([BANDS.index(b) for b in t["band"].to_numpy()[ok]], dtype=np.int8)
    eh = np.exp(y_hat[ok])
    up, dn, tk = (t[c].to_numpy(float)[ok] for c in ("up_n", "dn_n", "tick_n"))
    parts: dict[str, list[np.ndarray]] = {"band": [], "bracket": [], "z": [], "k": []}
    for j, (c, w) in enumerate(brackets()):
        parts["band"].append(bands)
        parts["bracket"].append(np.full(len(bands), j, dtype=np.int16))
        parts["z"].append(logit(psi(w, eh / (c * c))))
        parts["k"].append(open_counts(up, dn, tk, c, w))
    return {k: (np.concatenate(v) if v else np.empty(0)) for k, v in parts.items()}


def fit_logistic(z: np.ndarray, k: np.ndarray, trials: int = 2, *, max_iter: int = 100) -> tuple[float, float]:
    """(alpha, beta) maximising sum k log p + (trials - k) log(1 - p), p = sigmoid(alpha + beta z), by Newton."""
    z = np.asarray(z, dtype=float)
    k = np.asarray(k, dtype=float)
    if len(z) < MIN_ROWS or np.ptp(z) == 0 or k.min() == k.max():
        raise FitRefused("the calibration has too few observations, one value of z, or one outcome")
    X = np.column_stack([np.ones(len(z)), z])
    th = np.zeros(2)
    for _ in range(max_iter):
        p = sigmoid(X @ th)
        g = X.T @ (k - trials * p)
        wgt = trials * p * (1.0 - p)
        Hm = (X * wgt[:, None]).T @ X
        try:
            step = np.linalg.solve(Hm, g)
        except np.linalg.LinAlgError:
            raise FitRefused("the calibration's information matrix is singular") from None
        th = th + step
        if not np.all(np.isfinite(th)):
            raise FitRefused("the calibration diverged")
        if np.max(np.abs(step)) < 1e-10:
            return float(th[0]), float(th[1])
    raise FitRefused("the calibration did not converge")


def fit_calibration(obs: Mapping[str, np.ndarray]) -> dict[str, tuple[float, float]]:
    out = {}
    for bi, b in enumerate(BANDS):
        sel = obs["band"] == bi
        try:
            out[b] = fit_logistic(obs["z"][sel], obs["k"][sel])
        except FitRefused as exc:
            raise FitRefused(f"band {b}: {exc}") from None
    return out


def calibrated(cal: Mapping[str, tuple[float, float]], band_idx: np.ndarray, z: np.ndarray) -> np.ndarray:
    a = np.array([cal[b][0] for b in BANDS])[band_idx]
    bta = np.array([cal[b][1] for b in BANDS])[band_idx]
    return sigmoid(a + bta * z)


def fit_model(t: pd.DataFrame, mask: np.ndarray) -> dict[str, Any]:
    """The HAR and its calibration on the rows of `mask` (the calibration on the rows' own fitted forecasts)."""
    har = fit_har(t, mask)
    obs = bracket_obs(t, predict_y(har, t), mask)
    return {"har": har, "calibration": fit_calibration(obs)}


# ------------------------------------------------------------------------------------------------ the reading


def _r(section: str, stat: str, value: float, *, band: str = "", fold: str = "", bracket: str = "",
       bin_: str = "") -> dict[str, Any]:
    return {"section": section, "band": band, "fold": fold, "bracket": bracket, "bin": bin_, "stat": stat,
            "value": float(value)}


def _fold(year: int | str) -> str:
    return year if isinstance(year, str) else f"y{int(year)}"


def _model_rows(model: Mapping[str, Any], fold: str) -> list[dict[str, Any]]:
    rows = []
    for b in BANDS:
        for term, v in model["har"][b].items():
            rows.append(_r("coef", term, v, band=b, fold=fold))
        a, bt = model["calibration"][b]
        rows += [_r("calib", "alpha", a, band=b, fold=fold), _r("calib", "beta", bt, band=b, fold=fold)]
    return rows


def _scores(p: np.ndarray, k: np.ndarray) -> dict[str, float]:
    pc = np.clip(p, CLIP, 1.0 - CLIP)
    ll = -(k * np.log(pc) + (2 - k) * np.log(1.0 - pc)) / 2.0
    br = (k * (1.0 - p) ** 2 + (2 - k) * p ** 2) / 2.0
    return {"mean_p": float(p.mean()), "open_share": float(k.sum() / (2.0 * len(k))), "log_loss": float(ll.mean()),
            "brier": float(br.mean())}


def _at_q(p: np.ndarray, k: np.ndarray, q: float) -> list[tuple[str, float]]:
    adm = p <= q
    out = [("admitted_share_at_q", float(adm.mean()))]
    if adm.any():
        out.append(("open_share_admitted", float(k[adm].sum() / (2.0 * adm.sum()))))
    return out


def run_fit(t: pd.DataFrame, q: float) -> tuple[pd.DataFrame, dict[str, Any]]:
    """The out-of-fold folds, the final fit and the result frame (`COLUMNS`); the final model beside."""
    check_days(t["date"].unique())
    rows: list[dict[str, Any]] = []
    ok = fit_rows(t)
    bands = t["band"].to_numpy()
    yv = t["y"].to_numpy(float)
    pooled: dict[str, list[np.ndarray]] = {"band": [], "bracket": [], "p": [], "k": []}
    present = set(pd.to_datetime(t["date"]).dt.year.unique())
    for year in [y for y in FOLD_YEARS if y in present]:     # every year in a whole-span run (the loader's check)
        fold = _fold(year)
        train, test = fold_masks(t, year)
        model = fit_model(t, train)
        rows += _model_rows(model, fold)
        yh = predict_y(model["har"], t)
        obs = bracket_obs(t, yh, test)
        p = calibrated(model["calibration"], obs["band"].astype(np.int64), obs["z"])
        for bi, b in enumerate(BANDS):
            tr, te = train & ok & (bands == b), test & ok & (bands == b)
            rows += [_r("count", "rows_train", tr.sum(), band=b, fold=fold),
                     _r("count", "rows_test", te.sum(), band=b, fold=fold)]
            if te.sum() >= 2:
                res = yv[te] - yh[te]
                tot = yv[te] - yv[te].mean()
                rows.append(_r("oof", "har_r2", 1.0 - float(res @ res) / float(tot @ tot), band=b, fold=fold))
            sel = obs["band"] == bi
            if sel.any():
                rows += [_r("oof", s, v, band=b, fold=fold) for s, v in _scores(p[sel], obs["k"][sel]).items()]
        for key, v in (("band", obs["band"]), ("bracket", obs["bracket"]), ("p", p), ("k", obs["k"])):
            pooled[key].append(v)
    P = {k: np.concatenate(v) for k, v in pooled.items()}
    for bi, b in enumerate(BANDS):
        sel = P["band"] == bi
        rows.append(_r("count", "obs_oof", sel.sum(), band=b, fold=OOF))
        if not sel.any():
            continue
        p, k = P["p"][sel], P["k"][sel]
        rows += [_r("oof", s, v, band=b, fold=OOF) for s, v in _scores(p, k).items()]
        rows += [_r("oof", s, v, band=b, fold=OOF) for s, v in _at_q(p, k, q)]
        cut = np.clip(np.searchsorted(BIN_EDGES, p, side="right") - 1, 0, len(BIN_EDGES) - 2)
        for j in range(len(BIN_EDGES) - 1):
            s = cut == j
            lab = f"b{j}"
            rows.append(_r("reliability", "obs", s.sum(), band=b, fold=OOF, bin_=lab))
            if s.any():
                rows += [_r("reliability", "mean_p", p[s].mean(), band=b, fold=OOF, bin_=lab),
                         _r("reliability", "open_share", k[s].sum() / (2.0 * s.sum()), band=b, fold=OOF, bin_=lab)]
        for j, (c, w) in enumerate(brackets()):
            s = P["bracket"][sel] == j
            if s.any():
                lab = bracket_label(c, w)
                rows += [_r("bracket", "mean_p", p[s].mean(), band=b, fold=OOF, bracket=lab),
                         _r("bracket", "open_share", k[s].sum() / (2.0 * s.sum()), band=b, fold=OOF, bracket=lab)]
                rows += [_r("bracket", st, v, band=b, fold=OOF, bracket=lab) for st, v in _at_q(p[s], k[s], q)]
    final = fit_model(t, np.ones(len(t), dtype=bool))
    rows += _model_rows(final, FINAL)
    for b in BANDS:
        rows += [_r("count", "rows_final", (ok & (bands == b)).sum(), band=b, fold=FINAL),
                 _r("count", "rows_no_forecast", (~t["has_forecast"].to_numpy(bool) & (bands == b)).sum(), band=b,
                    fold=FINAL)]
    return pd.DataFrame(rows, columns=list(COLUMNS)), final


def output_problems(frame: pd.DataFrame) -> list[str]:
    """Why a frame is not this reading's: columns not `COLUMNS`, a level-named column, an unknown section or band, a
    final model missing a band's coefficient or calibration, a probability or share outside [0, 1], a negative count."""
    from extended.price_levels import is_level_name

    bad = []
    if list(frame.columns) != list(COLUMNS):
        return [f"columns are not COLUMNS: {list(frame.columns)}"]
    names = [c for c in frame.columns if is_level_name(str(c))]
    if names:
        bad.append(f"level-named columns {names}")
    if not set(frame["section"]) <= set(SECTIONS):
        bad.append(f"unknown sections {sorted(set(frame['section']) - set(SECTIONS))}")
    if not set(frame["band"]) <= set(BANDS):
        bad.append("unknown bands")
    fin = frame[frame["fold"] == FINAL]
    for b in BANDS:
        have = set(fin.loc[(fin["section"] == "coef") & (fin["band"] == b), "stat"])
        if have != {"const", *TERMS[b]}:
            bad.append(f"final coef {b}: {sorted(have)}")
        cal = set(fin.loc[(fin["section"] == "calib") & (fin["band"] == b), "stat"])
        if cal != {"alpha", "beta"}:
            bad.append(f"final calib {b}: {sorted(cal)}")
    v = pd.to_numeric(frame["value"], errors="coerce")
    shares = frame["stat"].isin(["mean_p", "open_share", "admitted_share_at_q", "open_share_admitted", "brier"])
    if ((v[shares] < 0) | (v[shares] > 1)).any():
        bad.append("a probability or share outside [0, 1]")
    if (v[frame["section"] == "count"] < 0).any() or (v[frame["stat"] == "obs"] < 0).any():
        bad.append("a negative count")
    if not np.isfinite(v[frame["section"].isin(["coef", "calib"])]).all():
        bad.append("a coefficient that is not finite")
    return bad


def manifest_parameters(q: float, q_source: Mapping[str, Any], *, identities: Mapping[str, str],
                        span: tuple[date, date]) -> dict[str, Any]:
    """The manifest's parameters: everything the loader checks, and the declared rules of the reading."""
    return {
        "task": TASK, "decisions": list(DECISIONS), "span": [span[0].isoformat(), span[1].isoformat()],
        "purpose": PURPOSE, "read_row": READ_ROW, "q": float(q), "q_source": dict(q_source),
        "marks": [int(MARKS[0]), int(MARKS[-1]), MARK_STEP], "alert_lag": ALERT_LAG, "frozen_alert": FROZEN_ALERT,
        "walk_last_stamp": WALK_LAST_STAMP, "tick": TICK, "walked_kinds": list(WALKED_KINDS), "bands": list(BANDS),
        "terms": {b: list(v) for b, v in TERMS.items()},
        "void_rule": {b: {"reads_overnight": ro, "reads_0829": r} for b, (ro, r) in VOID_RULE.items()},
        "har_windows": [HAR_DAILY, HAR_WEEKLY, HAR_MONTHLY], "rv_window": RV_WINDOW,
        "tod": [TOD_DAYS, TOD_MIN_DAYS], "c_grid": list(C_GRID), "w_grid": list(W_GRID), "clip": CLIP,
        "fold_years": list(FOLD_YEARS), "purge_sessions": PURGE_SESSIONS, "embargo_sessions": EMBARGO_SESSIONS,
        "bin_edges": list(BIN_EDGES), "identities": dict(identities),
    }


# ------------------------------------------------------------------------------------------------ the line and the loader


def admission_line(config: Path | None = None) -> tuple[float, dict[str, Any]]:
    """D-212's line, q: Stage 2's `selection.feasibility.flat_share_max` (D-212 (2) as D-308 raised it), read from the
    vendored config, its note checked to cite D-212. `ForecastRefused` if it is not there."""
    import yaml

    p = Path(config) if config is not None else VENDOR_STAGE2 / Q_CONFIG
    try:
        doc = yaml.safe_load(p.read_text(encoding="utf-8"))
        v, note = doc, doc
        for k in Q_KEY:
            v = v[k]
        for k in Q_NOTE_KEY:
            note = note[k]
    except (OSError, KeyError, TypeError) as exc:
        raise ForecastRefused(f"{TASK}: D-212's line is not readable at {p} ({exc!r})") from None
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 < float(v) < 1 or "D-212" not in str(note):
        raise ForecastRefused(f"{TASK}: {'.'.join(Q_KEY)} in {p} is not D-212's line")
    return float(v), {"file": f"vendor/stage2/{Q_CONFIG}", "key": ".".join(Q_KEY), "row": "Stage 2 D-212 (2), D-308"}


def manifest_path(path: Path | str) -> Path:
    return Path(str(path) + ".manifest.json")


#: the manifest parameters the loader holds to their values now (all of `manifest_parameters` but these)
NOT_COMPARED = ("identities", "span", "q_source")
FOLD_LABEL = ("search years: applied to marks of this fold's year only (trained without it, purged and embargoed); "
              "the backward folds make the out-of-fold numbers diagnostics, not a forward test")
FINAL_LABEL = ("held-out application only (trained on every search-year row, in-sample on the search years); "
               "applying T7 on the held-out years stays refused until the joint held-out test declares it")
_SHA = re.compile(r"[0-9a-f]{40}")


def _commit_problem(commit: Any, repo: Path = ROOT) -> str | None:
    """Why `commit` is not a named, clean commit of this repository (None if it is)."""
    c = str(commit or "")
    if not _SHA.fullmatch(c):
        return f"its git_commit {c!r} is not a named commit (40 hexadecimal characters, not dirty)"
    try:
        r = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", c + "^{commit}"], capture_output=True,
                           timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        return f"its git_commit cannot be checked ({exc!r})"
    return None if r.returncode == 0 else f"its git_commit {c} is not a commit of this repository"


def _model_from(rows: Sequence[Mapping[str, str]], fold: str, p: Path) -> dict[str, Any]:
    har: dict[str, dict[str, float]] = {}
    cal: dict[str, tuple[float, float]] = {}
    for b in BANDS:
        coef = {r["stat"]: float(r["value"]) for r in rows if r["fold"] == fold and r["section"] == "coef"
                and r["band"] == b}
        cc = {r["stat"]: float(r["value"]) for r in rows if r["fold"] == fold and r["section"] == "calib"
              and r["band"] == b}
        if set(coef) != {"const", *TERMS[b]} or set(cc) != {"alpha", "beta"}:
            raise ForecastRefused(f"REFUSED ({TASK}): {p}: band {b}'s {fold} model is incomplete")
        if not all(math.isfinite(v) for v in (*coef.values(), *cc.values())):
            raise ForecastRefused(f"REFUSED ({TASK}): {p}: band {b}'s {fold} model is not finite")
        if not cc["beta"] > 0:
            raise ForecastRefused(f"REFUSED ({TASK}): {p}: band {b}'s {fold} beta is not positive (F-R 6.5)")
        har[b], cal[b] = coef, (cc["alpha"], cc["beta"])
    return {"har": har, "calibration": cal, "fold": fold, "label": FINAL_LABEL if fold == FINAL else FOLD_LABEL}


def load_forecast(path: Path | str, *, q: float, repo: Path | str = ROOT) -> dict[str, Any]:
    """Each fold's model and the final model from the result file, labelled, after its manifest (the docstring's
    loader). `NotRead` when the file or its manifest is absent; `ForecastRefused` for anything else that is not this
    reading's."""
    p = Path(path)
    mp = manifest_path(p)
    if not p.is_file() or not mp.is_file():
        raise NotRead(f"{TASK}: no T7 reading at {p} (with its manifest) yet")
    raw = p.read_bytes()
    try:
        m = json.loads(mp.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ForecastRefused(f"{mp}: the manifest is not JSON ({exc})") from None
    sha = hashlib.sha256(raw).hexdigest()
    why = []
    if m.get("sha256") != sha:
        why.append("its sha256 is not the manifest's")
    if m.get("script") != SCRIPT:
        why.append(f"its script is {m.get('script')!r}, not {SCRIPT}")
    if m.get("git_dirty") is not False or str(m.get("git_commit", "")).endswith("-dirty"):
        why.append("it was written from a dirty tree")
    else:
        cp = _commit_problem(m.get("git_commit"), Path(repo))
        if cp:
            why.append(cp)
    clean = (m.get("provenance") or {}).get("clean_run")
    if not (isinstance(clean, dict) and clean.get("name")):
        why.append("it is not a clean run's (no provenance.clean_run)")
    par = m.get("parameters") or {}
    if par.get("task") != TASK or par.get("purpose") != PURPOSE or par.get("read_row") != READ_ROW:
        why.append("its task, purpose or read row is not this reading's")
    if par.get("span") != [SEARCH_START.isoformat(), SEARCH_END.isoformat()]:
        why.append(f"its span {par.get('span')} is not the whole search years")
    ids = par.get("identities") or {}
    if not ids or any(v != "HELD" for v in ids.values()):
        why.append(f"its identities {ids} did not all hold")
    if par.get("q") != float(q):
        why.append("its q is not D-212's line now")
    want = json.loads(json.dumps(manifest_parameters(q, {}, identities={}, span=(SEARCH_START, SEARCH_END))))
    differ = sorted(k for k in want if k not in NOT_COMPARED and par.get(k) != want[k])
    if differ:
        why.append(f"its declared parameters {differ} differ from the definitions now")
    if W_GRID != w_grid():
        why.append("W_GRID is not RD-05's w grid now")
    if why:
        raise ForecastRefused(f"REFUSED ({TASK}): {p} is not this reading's -- " + "; ".join(why))
    frame = pd.read_csv(io.BytesIO(raw), keep_default_na=False, dtype={c: str for c in COLUMNS if c != "value"})
    folds = {_fold(y) for y in FOLD_YEARS}
    bad = output_problems(frame)
    if set(frame["section"]) != set(SECTIONS):
        bad.append(f"its sections {sorted(set(frame['section']))} are not {list(SECTIONS)}")
    if set(frame["fold"]) != folds | {OOF, FINAL}:
        bad.append(f"its folds {sorted(set(frame['fold']))} are not every search year's, {OOF!r} and {FINAL!r}")
    if bad:
        raise ForecastRefused(f"REFUSED ({TASK}): {p}: the file is not run_fit's -- " + "; ".join(bad[:4]))
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    fold_models = {f: _model_from(rows, f, p) for f in sorted(folds)}
    final = _model_from(rows, FINAL, p)
    return {"fold_models": fold_models, "final_model": final, "q": float(q), "sha256": sha,
            "git_commit": m.get("git_commit"), "manifest": str(mp)}


def model_for(got: Mapping[str, Any], day: Any) -> dict[str, Any]:
    """The model that scores a mark of `day`: on the search years, the fold model of its year (out of fold); after
    them, refused (a held-out application is not declared here)."""
    d = _day(day)
    check_span(d, d)                                     # refuses any day after 2023-12-29
    return got["fold_models"][_fold(d.year)]


def probability_open(model: Mapping[str, Any], band: str, x: Mapping[str, float], m_var: float, stop: float,
                     w: float) -> float:
    """p_hat for one mark: the band's HAR at the features `x`, V_hat = m_var exp(y_hat) (m_var the mark's M, in the
    stop's units squared), u = V_hat / stop^2, calibrated. NaN -- never admitted -- if a feature is missing, or if the
    stop in units of sqrt(M) or w lies outside the calibrated grid (`C_GRID`, `W_GRID`): never extrapolated."""
    c = model["har"][band]
    y = c["const"] + sum(c[term] * float(x[term]) for term in TERMS[band])
    if not (math.isfinite(y) and m_var > 0 and stop > 0):
        return float("nan")
    cs = stop / math.sqrt(m_var)
    if not (min(C_GRID) <= cs <= max(C_GRID) and min(W_GRID) <= w <= max(W_GRID)):
        return float("nan")
    z = logit(psi(w, m_var * math.exp(y) / (stop * stop)))
    a, b = model["calibration"][band]
    return float(sigmoid(a + b * z))


def admit(p: float, q: float) -> bool:
    """T7's rule: admit iff the forecast chance of reaching the flatten open is at most q (a missing p never)."""
    return bool(math.isfinite(p) and p <= q)


__all__ = ["TASK", "DECISIONS", "RESULT", "SCRIPT", "PURPOSE", "READ_ROW", "SEARCH_START", "SEARCH_END", "TICK",
           "WALKED_KINDS", "WALK_LAST_STAMP", "ALERT_LAG", "MARKS", "FROZEN_ALERT", "BANDS", "FROZEN_BANDS", "TERMS",
           "VOID_RULE", "C_GRID", "W_GRID", "FOLD_YEARS", "PURGE_SESSIONS", "EMBARGO_SESSIONS", "BIN_EDGES",
           "SECTIONS", "COLUMNS", "FINAL", "OOF", "BeyondSearchYears", "ConfirmationWindowRefused", "FitRefused",
           "NotRead", "ForecastRefused", "check_span", "check_days", "psi", "psi_series", "psi_images", "logit",
           "sigmoid", "day_grid", "rv_at", "window_stats", "bands_for", "prior_means", "feature_table", "fold_masks",
           "fit_rows", "fit_har", "predict_y", "open_counts", "brackets", "bracket_label", "bracket_obs",
           "fit_logistic", "fit_calibration", "calibrated", "fit_model", "run_fit", "output_problems",
           "manifest_parameters", "admission_line", "manifest_path", "load_forecast", "model_for",
           "probability_open", "admit", "w_grid", "NOT_COMPARED", "FOLD_LABEL", "FINAL_LABEL"]
