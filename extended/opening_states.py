"""F-03 (family O, `prereg/F-03_opening_timing.md`, pinned by E-095): the states a waiting funded account waits for,
computed only from bars closed by each offer's alert (section 6; build item 18.1 item 1).

    from extended import opening_states as OS
    st = OS.compute(bars, marks=OS.POPULATION_MARKS)          # the frame: P-16's walked sessions only (6.1)
    st.in_state("s1"), st.share("u3"), st.forecast.coefficients_sha256

**The cells.** s1 (unexpected volatility), s2 (a trending night) and u3 (family R's fast forecast) are built. **s3 is
not built**: it was dropped at the pin by 6.6's drop rule (E-095); it stays counted (`CELLS`, four cells) and asking
for it raises `CellDropped`.

**The clock** (6.1; `extended.features`): a trading day opens at 17:00 CT the evening before; a slot is minutes after
that 17:00 (`features.slot`), Chicago wall clock (a DST change moves no slot). A bar stamped at slot s covers s and
closes at s + 1. **At mark m the alert is t = m - 5 and a state reads only the day's bars stamped at slots <= m - 6
and the bars of earlier sessions.** The population's latest mark is 08:25 (slot 925): no state reads a bar of the
alert's day stamped 08:30 or later. Every window over a day's bars is bounded at the day's first bar (prefix sums and
prefix maxima from slot 0; no negative-index slicing).

**The quantities** (6.2), each a log ratio of prices within one trading day:

| name | formula | reads |
|---|---|---|
| LR(d) | ln(max high / min low) over day d's bars (17:00-15:59) | day d's bars; used only on later days |
| LRS(d, m) | ln(max high / min low) over day d's bars stamped 17:00 .. m - 6; missing with fewer than 15 bars present | day d up to m - 6 |
| DIS(d, m) | abs(ln(close of the last bar stamped at or before m - 6 / open of day d's first bar)) | day d up to m - 6 |
| har(x)(d) | (x(d-1) + mean x(d-5..d-1) + mean x(d-22..d-1)) / 3, unfitted; defined only when all 22 prior values are present | the 22 prior walked sessions |
| H(d) | har(LR)(d) | the 22 prior sessions' whole days |
| HS(d, m) | har(LRS(., m))(d) | the 22 prior sessions' same window |

**The states** (6.3, 6.4): s1 when U(d, m) = ln(LRS / HS)'s share is above 2/3, from the 17:30 mark; s2 when T(d, m) =
DIS / H's share is above 2/3, from the 17:30 mark; u3 when y_hat(d, m)'s share is above 2/3, from 17:00. A **share** is
(the prior values below + half the equal ones) / their count over the 250 prior walked sessions' values at the same
mark that are present, at least 120 of them (else undefined, not in state); strict inequalities.

**u3's forecast** (6.5; family R's draft section 6 restated): the target IV(d, m) -- the sum of squared one-minute price
changes in points^2 from the entry bar (the first present bar stamped at or after m) to the bar ending 15:08 CT
(stamped 15:07), the first change that bar's close less its open, then each present bar's close less the previous
present bar's close -- a label for the fit only; M(d, m) the mean of IV(., m) over the 22 prior walked sessions (all 22
present); y = ln(IV / M). Regressors: x1 = ln(IV(d - 1, m) / M), x2 = ln(mean IV over the 5 prior sessions / M), x3 =
2 x `rv_tod` at the alert (`features.compute`'s formula extended to overnight alerts: rv_60 the root mean square of the
one-minute close changes over the bars stamped t - 60 .. t - 1, bounded at the day's first bar, at least two changes;
its median over the 20 prior walked sessions at the same slot, at least 10, else missing). Bands: `evening` 17:00-17:55
(x1, x2), `asia` 18:00-01:55 and `london` 02:00-08:25 (x1, x2, x3): ordinary least squares with an intercept, weight
one, one observation per (session, population mark) -- 3 + 4 + 4 = 11 coefficients; refused when a band's design is
rank-deficient. Walk-forward inside the choice block: test years 2021, 2022 and 2023, each fitted on the choice block's
sessions before it less the last 22 (expanding); the final fit on every choice-block session with a value; the final
coefficients serialised to canonical JSON and hashed (`Forecast.coefficients_sha256`). y_hat's share at day d uses the
fit that forecasts day d (its test year's fold; on the judged block the final fit) for d and for the 250 prior
sessions alike.

The frame is P-16's walked sessions only (6.1, the review's n4): the caller hands this module those sessions' bars, so
every trailing window runs over walked sessions. No state reads a side, an outcome, a calendar or a price level.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import features as F

#: the four declared cells, counted (17 item 2); s3 dropped at the pin (E-095), never built
CELLS = ("s1", "s2", "s3", "u3")
DROPPED = ("s3",)
BUILT = tuple(c for c in CELLS if c not in DROPPED)
#: each cell's index in the seeds' `[seed, c, ...]` (16; 7.1: 0 s1, 1 s2, 2 s3, 3 u3)
CELL_INDEX = {c: i for i, c in enumerate(CELLS)}
#: the stated signs (1 (iv)); every cell is judged one-sided for a positive lift
SIGNS = {"s1": "positive", "s2": "positive", "s3": "positive", "u3": "negative"}

#: the population's marks (5.2): every five minutes from 17:00 to 08:25 CT (slots 0 .. 925)
POPULATION_MARKS: tuple[int, ...] = tuple(range(F.slot(17, 0), F.slot(8, 25) + 1, 5))
#: a report day's population starts at 07:40 CT (strictly after 07:35:00; E-007 (d), E-039 (1))
REPORT_DAY_FIRST_MARK = F.slot(7, 40)
#: s1 and s2 exist from the 17:30 mark (half an hour of the night; 6.3, the review's m1)
NIGHT_FIRST_MARK = F.slot(17, 30)
#: the latest mark (08:25) and the window no state may read (6.1)
LAST_MARK = F.slot(8, 25)
#: LRS is missing with fewer than this many bars present by m - 6 (6.2)
THIN_NIGHT_BARS = 15
#: the HAR terms (Corsi 2009): daily, weekly, monthly
HAR_TERMS = (1, 5, 22)
#: the rolling third (6.4)
SHARE_WINDOW, SHARE_MIN = 250, 120
UPPER, LOWER = 2.0 / 3.0, 1.0 / 3.0
#: u3: the IV window ends with the bar ending 15:08 CT, stamped 15:07
IV_LAST_SLOT = F.slot(15, 7)
IV_PRIOR = 22
X2_PRIOR = 5
RV_WINDOW = 60
TOD_DAYS, TOD_MIN = 20, 10
#: the bands (6.5) as [first, last] slots, and their regressors
BANDS = {"evening": (F.slot(17, 0), F.slot(17, 55), ("x1", "x2")),
         "asia": (F.slot(18, 0), F.slot(1, 55), ("x1", "x2", "x3")),
         "london": (F.slot(2, 0), F.slot(8, 25), ("x1", "x2", "x3"))}
N_COEFFICIENTS = sum(1 + len(t) for _, _, t in BANDS.values())          # 11
#: the walk-forward's test years and the purge before each (6.5)
TEST_YEARS = (2021, 2022, 2023)
FOLD_GAP = 22
CHOICE_FIRST, CHOICE_LAST = "2020-01-02", "2023-12-29"
JUDGED_FIRST = "2024-01-02"


class CellDropped(KeyError):
    """A cell dropped at the pin by 6.6's rule (E-095): counted, never built."""


class RankDeficient(RuntimeError):
    """A band's design matrix is rank-deficient: the fit is refused (6.5; the failure protocol)."""


def check_cell(cell: str) -> str:
    if cell in DROPPED:
        raise CellDropped(f"{cell} was dropped at the pin by section 6.6's drop rule (E-095): counted, not built")
    if cell not in BUILT:
        raise KeyError(f"unknown cell {cell!r}; the family's cells are {CELLS}")
    return cell


def band_of(mark: int) -> str:
    for name, (lo, hi, _) in BANDS.items():
        if lo <= int(mark) <= hi:
            return name
    raise ValueError(f"mark {F.slot_label(mark)} is in no band of 6.5")


# ------------------------------------------------------------------------------------------------ helpers


def _prior_window(x: np.ndarray, k: int) -> np.ndarray:
    """W[d, :] = x[d-k .. d-1] (NaN before the frame), shape (n, k) for a 1-d x."""
    pad = np.concatenate([np.full(k, np.nan), np.asarray(x, float)])
    return np.lib.stride_tricks.sliding_window_view(pad, k)[: len(x)]


def har(x: np.ndarray) -> np.ndarray:
    """6.2's unfitted HAR mean over the prior walked sessions, NaN unless all 22 prior values are present. `x` is 1-d
    (sessions) or 2-d (sessions x marks; each column separately)."""
    x = np.asarray(x, float)
    if x.ndim == 2:
        return np.column_stack([har(x[:, j]) for j in range(x.shape[1])]) if x.shape[1] else x.copy()
    W = _prior_window(x, HAR_TERMS[-1])
    full = ~np.isnan(W).any(axis=1)
    out = (W[:, -1] + W[:, -5:].mean(axis=1) + W.mean(axis=1)) / 3.0
    return np.where(full, out, np.nan)


def rolling_share(x: np.ndarray, window: int = SHARE_WINDOW, min_count: int = SHARE_MIN) -> np.ndarray:
    """6.4's share: for each session d (rows) -- per column when 2-d -- (the prior values below x[d] + half the equal
    ones) / their count, over the `window` prior sessions with a value; NaN with fewer than `min_count` or x[d]
    missing (S2's mid-rank rule, D-581 (6), over a year)."""
    x = np.asarray(x, float)
    if x.ndim == 2:
        return np.column_stack([rolling_share(x[:, j], window, min_count) for j in range(x.shape[1])])             if x.shape[1] else x.copy()
    W = _prior_window(x, window)
    have = ~np.isnan(W)
    cnt = have.sum(axis=1)
    with np.errstate(invalid="ignore"):
        below = (W < x[:, None]).sum(axis=1)
        equal = (W == x[:, None]).sum(axis=1)
        out = (below + 0.5 * equal) / np.where(cnt > 0, cnt, 1)
    return np.where((cnt >= min_count) & ~np.isnan(x), out, np.nan)


def _cff(C: np.ndarray) -> np.ndarray:
    idx = np.where(~np.isnan(C), np.arange(C.shape[1]), -1)
    np.maximum.accumulate(idx, axis=1, out=idx)
    out = np.take_along_axis(C, np.maximum(idx, 0), axis=1)
    out[idx < 0] = np.nan
    return out


def rv60(C: np.ndarray, alerts: Sequence[int]) -> np.ndarray:
    """rv_60 at each alert slot t (columns): sqrt(sum of squared one-minute close changes over the bars stamped
    t - 60 .. t - 1 / their count), each change a bar's close less the previous present bar's close within the day (the
    day's first bar has none), the window bounded at the day's first bar; NaN with fewer than two changes --
    `features.compute`'s formula, at any alert."""
    Cff = _cff(C)
    prev = np.concatenate([np.full((C.shape[0], 1), np.nan), Cff[:, :-1]], axis=1)
    dC = C - prev
    ok = ~np.isnan(dC)
    cs2 = np.cumsum(np.where(ok, dC * dC, 0.0), axis=1)
    csn = np.cumsum(ok, axis=1, dtype=np.int64)
    out = np.full((C.shape[0], len(alerts)), np.nan)
    for k, t in enumerate(alerts):
        t = int(t)
        if t - 1 < 0:
            continue
        hi2, hin = cs2[:, t - 1], csn[:, t - 1]
        if t - 1 - RV_WINDOW >= 0:
            s2, n = hi2 - cs2[:, t - 1 - RV_WINDOW], hin - csn[:, t - 1 - RV_WINDOW]
        else:
            s2, n = hi2, hin
        with np.errstate(invalid="ignore", divide="ignore"):
            out[:, k] = np.where(n >= 2, np.sqrt(s2 / np.where(n > 0, n, 1)), np.nan)
    return out


def prior_median(X: np.ndarray, k: int = TOD_DAYS, min_count: int = TOD_MIN) -> np.ndarray:
    """med[d, j] = the median of X[d-k..d-1, j] over its present values (NaN if fewer than `min_count`): the library's
    trailing time-of-day median (`features._prior_median`), imported."""
    return F._prior_median(np.asarray(X, float), k, min_count)


# ------------------------------------------------------------------------------------------------ the quantities


@dataclass
class Quantities:
    """6.2's quantities on a frame of walked sessions: rows the sessions, columns `marks`."""
    days: list[date]
    marks: tuple[int, ...]
    LR: np.ndarray
    LRS: np.ndarray
    DIS: np.ndarray
    H: np.ndarray
    HS: np.ndarray
    IV: np.ndarray
    x3: np.ndarray


def quantities(g: F.Grid, marks: Sequence[int] = POPULATION_MARKS) -> Quantities:
    """Every quantity of 6.2 and u3's inputs on the grid `g` (P-16's walked sessions only)."""
    marks = tuple(int(m) for m in marks)
    if not marks or min(marks) < 0 or max(marks) > LAST_MARK:
        raise ValueError("the population's marks lie in 17:00 .. 08:25 CT (slots 0 .. 925)")
    O, H, L, C = g.O, g.H, g.L, g.C
    n = len(g.days)
    with np.errstate(divide="ignore", invalid="ignore"):
        LR = np.log(np.fmax.reduce(H, axis=1) / np.fmin.reduce(L, axis=1))
        Hcum, Lcum = np.fmax.accumulate(H, axis=1), np.fmin.accumulate(L, axis=1)
        cnt = np.cumsum(~np.isnan(C), axis=1, dtype=np.int64)
        Cff = _cff(C)
        present = ~np.isnan(O)
        has = present.any(axis=1)
        first = np.argmax(present, axis=1)
        O_first = np.where(has, O[np.arange(n), first], np.nan)
        LRS = np.full((n, len(marks)), np.nan)
        DIS = np.full((n, len(marks)), np.nan)
        for k, m in enumerate(marks):
            last = m - 6                                        # the last slot the alert at m - 5 may read
            if last < 0:
                continue
            ok = cnt[:, last] >= THIN_NIGHT_BARS
            LRS[:, k] = np.where(ok, np.log(Hcum[:, last] / Lcum[:, last]), np.nan)
            seen = has & (first <= last)
            DIS[:, k] = np.where(seen, np.abs(np.log(Cff[:, last] / O_first)), np.nan)
        # u3's target: from the entry bar (the first present bar at or after m) to the bar stamped 15:07
        prev = np.concatenate([np.full((n, 1), np.nan), Cff[:, :-1]], axis=1)
        sq = np.where(~np.isnan(C) & ~np.isnan(prev), (C - prev) ** 2, 0.0)
        cs = np.cumsum(sq, axis=1)
        nxt = np.where(present, np.arange(C.shape[1]), C.shape[1])
        nxt = np.minimum.accumulate(nxt[:, ::-1], axis=1)[:, ::-1]           # the first present slot at or after
        IV = np.full((n, len(marks)), np.nan)
        rows = np.arange(n)
        for k, m in enumerate(marks):
            j = nxt[:, m]
            okj = j <= IV_LAST_SLOT
            jj = np.minimum(j, IV_LAST_SLOT)
            first_sq = (C[rows, jj] - O[rows, jj]) ** 2
            IV[:, k] = np.where(okj, first_sq + cs[:, IV_LAST_SLOT] - cs[rows, jj], np.nan)
        alerts = [m - 5 for m in marks]
        RV = rv60(C, alerts)
        med = prior_median(RV)
        x3 = 2.0 * np.log(RV / med)
    return Quantities(list(g.days), marks, LR, LRS, DIS, har(LR), har(LRS), IV, x3)


# ------------------------------------------------------------------------------------------------ u3's forecast


@dataclass
class Regressors:
    y: np.ndarray
    x1: np.ndarray
    x2: np.ndarray
    x3: np.ndarray


def regressors(q: Quantities) -> Regressors:
    """y (the label, for fitting only), x1, x2 and x3 (6.5), sessions x marks."""
    IV = q.IV
    n = IV.shape[0]
    M = np.full_like(IV, np.nan)
    X2 = np.full_like(IV, np.nan)
    X1 = np.full_like(IV, np.nan)
    for k in range(IV.shape[1]):
        W = _prior_window(IV[:, k], IV_PRIOR)
        M[:, k] = np.where(~np.isnan(W).any(axis=1), W.mean(axis=1), np.nan)
        W5 = W[:, -X2_PRIOR:]
        X2[:, k] = np.where(~np.isnan(W5).any(axis=1), W5.mean(axis=1), np.nan)
        X1[1:, k] = IV[:-1, k]
    with np.errstate(divide="ignore", invalid="ignore"):
        y = np.log(IV / M)
        x1 = np.log(X1 / M)
        x2 = np.log(X2 / M)
    bad = lambda a: np.where(np.isfinite(a), a, np.nan)               # noqa: E731
    del n
    return Regressors(bad(y), bad(x1), bad(x2), bad(q.x3))


def _design(R: Regressors, marks: Sequence[int], band: str, rows: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The band's (X, y) over sessions `rows` (a boolean mask) at the band's population marks, rows with every term
    present (sessions-major, marks ascending)."""
    lo, hi, terms = BANDS[band]
    cols = [k for k, m in enumerate(marks) if lo <= m <= hi]
    if not cols:
        return np.empty((0, 1 + len(terms))), np.empty(0)
    parts = [getattr(R, t)[rows][:, cols].ravel() for t in terms]
    yy = R.y[rows][:, cols].ravel()
    X = np.column_stack([np.ones_like(yy)] + parts)
    ok = np.isfinite(yy) & np.isfinite(X).all(axis=1)
    return X[ok], yy[ok]


def ols(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Ordinary least squares, deterministic; refused (`RankDeficient`) when X is rank-deficient."""
    if X.shape[0] < X.shape[1] or np.linalg.matrix_rank(X) < X.shape[1]:
        raise RankDeficient(f"the design ({X.shape[0]} rows, {X.shape[1]} terms) is rank-deficient: the fit is "
                            "refused (6.5)")
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def fit(R: Regressors, marks: Sequence[int], rows: np.ndarray) -> dict[str, list[float]]:
    """The 11 coefficients on the sessions `rows`: {band: [intercept, terms...]}."""
    return {band: [float(b) for b in ols(*_design(R, marks, band, rows))] for band in BANDS}


def predict(R: Regressors, marks: Sequence[int], coef: Mapping[str, Sequence[float]]) -> np.ndarray:
    """y_hat at every (session, mark) with its terms present, by `coef`."""
    out = np.full(R.y.shape, np.nan)
    for k, m in enumerate(marks):
        lo, hi, terms = BANDS[band_of(m)]
        b = np.asarray(coef[band_of(m)], float)
        val = b[0] + sum(b[i + 1] * getattr(R, t)[:, k] for i, t in enumerate(terms))
        out[:, k] = val
    return out


def canonical_json(coef: Mapping[str, Sequence[float]]) -> str:
    """The coefficients as canonical JSON: bands sorted, each with its term names, floats by `repr`."""
    body = {band: {"terms": ["intercept", *BANDS[band][2]], "beta": [repr(float(x)) for x in coef[band]]}
            for band in sorted(coef)}
    return json.dumps(body, sort_keys=True, separators=(",", ":"))


def coefficients_sha256(coef: Mapping[str, Sequence[float]]) -> str:
    return hashlib.sha256(canonical_json(coef).encode("utf-8")).hexdigest()


def coefficients_from_json(text: str) -> dict[str, list[float]]:
    body = json.loads(text)
    out = {}
    for band, v in body.items():
        if band not in BANDS or v["terms"] != ["intercept", *BANDS[band][2]]:
            raise ValueError(f"the forecast's JSON band {band!r} is not 6.5's")
        out[band] = [float(x) for x in v["beta"]]
    if set(out) != set(BANDS):
        raise ValueError("the forecast's JSON does not hold every band")
    return out


@dataclass
class Forecast:
    """u3's walk-forward: each fold's coefficients (by test year), the final fit, and the hash of its canonical JSON."""
    folds: dict[int, dict[str, list[float]]]
    final: dict[str, list[float]] | None
    coefficients_sha256: str | None
    fold_rows: dict[int, int] = field(default_factory=dict)


def walk_forward(R: Regressors, days: Sequence[date], marks: Sequence[int], *, test_years: Sequence[int] = TEST_YEARS,
                 gap: int = FOLD_GAP, choice_last: str = CHOICE_LAST, final: bool = True,
                 frozen: Mapping[str, Sequence[float]] | None = None) -> Forecast:
    """6.5's walk-forward inside the choice block: each test year fitted on the choice block's sessions before it less
    the last `gap` (a year with no session in the frame is skipped); the final fit on every choice-block session (or,
    with `frozen`, the pinned final coefficients instead -- the judge's entry point fits nothing, T-9)."""
    ds = np.array([d.isoformat() for d in days])
    choice = (ds >= CHOICE_FIRST) & (ds <= choice_last)
    folds, rows_used = {}, {}
    for Y in test_years:
        in_y = np.array([d.year == int(Y) for d in days])
        if not in_y.any():
            continue
        first = int(np.argmax(in_y))
        train = np.zeros(len(days), dtype=bool)
        hi = max(0, first - int(gap))
        train[:hi] = True
        train &= choice
        folds[int(Y)] = fit(R, marks, train)
        rows_used[int(Y)] = int(train.sum())
    if frozen is not None:
        fin = {b: [float(x) for x in v] for b, v in frozen.items()}
    elif final:
        fin = fit(R, marks, choice)
    else:
        fin = None
    return Forecast(folds, fin, coefficients_sha256(fin) if fin is not None else None, rows_used)


def _forecasting_fits(days: Sequence[date], fc: Forecast) -> list[tuple[np.ndarray, Mapping[str, Sequence[float]]]]:
    ds = [d.isoformat() for d in days]
    fits: list[tuple[np.ndarray, Mapping[str, Sequence[float]]]] = []
    for Y, coef in fc.folds.items():
        fits.append((np.array([d.year == Y for d in days]), coef))
    if fc.final is not None:
        fits.append((np.array([x >= JUDGED_FIRST for x in ds]), fc.final))
    return fits


def forecast_values(R: Regressors, days: Sequence[date], marks: Sequence[int], fc: Forecast) -> np.ndarray:
    """y_hat at each (session, mark) by the fit that forecasts the session (its test year's fold; the final fit from
    the judged block's first session); NaN where none does."""
    out = np.full(R.y.shape, np.nan)
    for rows, coef in _forecasting_fits(days, fc):
        if rows.any():
            out[rows] = predict(R, marks, coef)[rows]
    return out


def forecast_shares(R: Regressors, days: Sequence[date], marks: Sequence[int], fc: Forecast) -> np.ndarray:
    """y_hat's share at each (session, mark): the session's own fit (its test year's fold; the final fit from the
    judged block's first session) for it and for its 250 prior sessions alike; NaN where no fit forecasts the day."""
    out = np.full(R.y.shape, np.nan)
    for rows, coef in _forecasting_fits(days, fc):
        if rows.any():
            sh = rolling_share(predict(R, marks, coef))
            out[rows] = sh[rows]
    return out


# ------------------------------------------------------------------------------------------------ the states


@dataclass
class States:
    """Every built cell's share and in-state flag at every (session, mark) of the frame."""
    days: list[date]
    marks: tuple[int, ...]
    shares: dict[str, np.ndarray]
    forecast: Forecast | None
    quantities: Quantities | None = None
    y_hat: np.ndarray | None = None
    y: np.ndarray | None = None

    def share(self, cell: str) -> np.ndarray:
        return self.shares[check_cell(cell)]

    def in_state(self, cell: str) -> np.ndarray:
        """The cell's flag (6.3, 6.4): its share strictly above 2/3; undefined -> not in state; s1 and s2 never before
        the 17:30 mark."""
        sh = self.share(cell)
        with np.errstate(invalid="ignore"):
            on = sh > UPPER
        on = on & ~np.isnan(sh)
        if cell in ("s1", "s2"):
            on[:, [k for k, m in enumerate(self.marks) if m < NIGHT_FIRST_MARK]] = False
        return on

    def frame(self) -> pd.DataFrame:
        """One row a (session, mark): date, mark, each built cell's share and flag."""
        n, K = len(self.days), len(self.marks)
        out: dict[str, Any] = {"date": np.repeat([d.isoformat() for d in self.days], K),
                               "slot": np.tile(np.asarray(self.marks, dtype=np.int64), n)}
        for c in BUILT:
            out[f"share_{c}"] = self.share(c).ravel()
            out[f"in_{c}"] = self.in_state(c).ravel()
        return pd.DataFrame(out)


def compute(bars: pd.DataFrame | F.Grid, marks: Sequence[int] = POPULATION_MARKS, *,
            test_years: Sequence[int] = TEST_YEARS, choice_last: str = CHOICE_LAST,
            frozen: Mapping[str, Sequence[float]] | None = None, final: bool = True,
            keep_quantities: bool = False) -> States:
    """s1, s2 and u3 at every (walked session, mark) of `bars` (or its grid). u3 by 6.5's walk-forward (`frozen`: the
    pinned final coefficients, for the judged block -- nothing is fitted then but the folds, which read the choice
    block only)."""
    g = bars if isinstance(bars, F.Grid) else F.grid(bars)
    q = quantities(g, marks)
    with np.errstate(divide="ignore", invalid="ignore"):
        U = np.log(q.LRS / q.HS)
        T = q.DIS / q.H[:, None]
    U = np.where(np.isfinite(U), U, np.nan)
    T = np.where(np.isfinite(T), T, np.nan)
    shares = {"s1": rolling_share(U), "s2": rolling_share(T)}
    R = regressors(q)
    fc = walk_forward(R, q.days, q.marks, test_years=test_years, choice_last=choice_last, frozen=frozen, final=final)
    shares["u3"] = forecast_shares(R, q.days, q.marks, fc)
    return States(q.days, q.marks, shares, fc, q if keep_quantities else None, forecast_values(R, q.days, q.marks, fc),
                  R.y)


def states_sha256(frame: pd.DataFrame, cells: Iterable[str] = BUILT) -> str:
    """The hash of the population's state columns (18.1 item 1: written as boolean columns and hashed before any
    replay reads them): date, slot and each cell's flag, in row order."""
    cols = ["date", "slot", *[f"in_{c}" for c in cells]]
    h = hashlib.sha256()
    h.update("|".join(cols).encode())
    for c in cols:
        v = frame[c].to_numpy()
        h.update((np.asarray(v).astype(str).tobytes() if v.dtype == object else np.ascontiguousarray(v).tobytes()))
    return h.hexdigest()


__all__ = ["CELLS", "DROPPED", "BUILT", "CELL_INDEX", "SIGNS", "POPULATION_MARKS", "REPORT_DAY_FIRST_MARK",
           "NIGHT_FIRST_MARK", "LAST_MARK", "BANDS", "N_COEFFICIENTS", "TEST_YEARS", "CellDropped", "RankDeficient",
           "check_cell", "band_of", "har", "rolling_share", "rv60", "prior_median", "Quantities", "quantities",
           "Regressors", "regressors", "ols", "fit", "predict", "canonical_json", "coefficients_sha256",
           "coefficients_from_json", "Forecast", "walk_forward", "forecast_values", "forecast_shares", "States", "compute",
           "states_sha256"]


# ------------------------------------------------------------------------------------------------ A3 on any frame


def _grid_copy(g: F.Grid, upto: int | None = None) -> F.Grid:
    k = len(g.days) if upto is None else int(upto)
    return F.Grid(list(g.days[:k]), g.contract[:k].copy(), *(X[:k].copy() for X in (g.O, g.H, g.L, g.C, g.V)))


def replaced_grid(g: F.Grid, d: int, cut: int, rng: np.random.Generator) -> F.Grid:
    """Every bar at or after slot `cut` of session d, and every bar of a later session, replaced by a seeded walk."""
    h = _grid_copy(g)
    mask = np.zeros(g.O.shape, dtype=bool)
    mask[d, max(cut, 0):] = True
    mask[d + 1:, :] = True
    mask &= ~np.isnan(g.O)
    k = int(mask.sum())
    walk = 9000.0 + 0.25 * np.cumsum(np.rint(rng.normal(0.0, 40.0, k)))
    o = walk + 0.25 * np.rint(rng.normal(0.0, 10.0, k))
    wid = 0.25 * np.rint(np.abs(rng.normal(0.0, 30.0, (k, 2))))
    h.O[mask], h.C[mask] = o, walk
    h.H[mask] = np.maximum(o, walk) + wid[:, 0]
    h.L[mask] = np.minimum(o, walk) - wid[:, 1]
    h.V[mask] = rng.integers(1, 50_000, k)
    return h


def deleted_grid(g: F.Grid, d: int, cut: int) -> F.Grid:
    """Every bar at or after the cut deleted (session d's from the cut; later sessions leave the frame)."""
    h = _grid_copy(g, d + 1)
    for X in (h.O, h.H, h.L, h.C, h.V):
        X[d, max(cut, 0):] = np.nan
    return h


def invariance_problems(g: F.Grid, st: States, cuts: Sequence[tuple[int, int]], seed: int, **kw: Any) -> list[str]:
    """A3 (T-2's test on a frame): at each cut (session d, mark m) every bar stamped at or after m - 5 replaced by a
    walk seeded `[seed, j]` (j the cut's index), and separately deleted; every built cell's share and flag and every
    y_hat at every (session, mark) whose alert is at or before the cut's must be unchanged. `kw` as `compute`'s."""
    out: list[str] = []
    for j, (d, m) in enumerate(cuts):
        vis = np.zeros((len(st.days), len(st.marks)), dtype=bool)
        vis[:d] = True
        vis[d, [k for k, mm in enumerate(st.marks) if mm <= m]] = True
        for name, h in (("replaced", replaced_grid(g, d, m - 5, np.random.default_rng([int(seed), j]))),
                        ("deleted", deleted_grid(g, d, m - 5))):
            got = compute(h, st.marks, **kw)
            n = len(got.days)
            v = vis[:n]
            for c in BUILT:
                if not np.array_equal(got.share(c)[v], st.share(c)[:n][v], equal_nan=True):
                    out.append(f"A3: {c}'s share moved at {st.days[d]} {F.slot_label(m)} ({name})")
            if not np.array_equal(got.y_hat[v], st.y_hat[:n][v], equal_nan=True):
                out.append(f"A3: y_hat moved at {st.days[d]} {F.slot_label(m)} ({name})")
            if out:
                return out
    return out
