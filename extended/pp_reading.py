"""RD-02's reading code that a synthetic check can hold before the run (`prereg/RD-02_payout_policy.md`, 5 item 3 and
9.2; its build Q-105): each measure's horizon, the blocks a reading at that horizon is read on, and the uncertainty
printed with every paired reading. No engine, no bar, no result: pure functions over per-start records and series.

**Horizons (5 item 3).** `HORIZONS` maps every measure of 9.1 items 1, 2, 4 and 7 to the sessions a start needs for it:
the card's keys take `u_select.MEASURES`' own horizons (checked against it at import, refusing), E-014's journey
variables Q-17's windows (`extended.user_readings.FIRST_WINDOW`, `YEAR_WINDOW`), the rest as declared. A share at month
m is read at 63 for m up to 3 (P's horizon) and 21 m beyond.

**Blocks (5 item 3).** `block(records, which, measure)` is `u_select.block(records, which, h)` at the measure's h:
all starts with h sessions left (None), the early block (the starts of 2023 and before less the last h), or the late
block (the starts from 2024 with h left). `by_year` gives each year's starts with h left -- means only, not purged.

**Uncertainty (9.2).** `kept_windows` (every other h-start window from the block's first start), `t_interval` (the
two-sided 90 % Student t on the kept windows' means, from 4 windows with a spread), `sign_count`, `mdd`, `describe`
(the zero-series and too-few rules), and the coverage label (`label`: gauss, ahead and paired only, below 0.88) with
the honesty series' shapes (`start_series`) and their seeds' keys (`HONESTY_KEY`, `T6_KEY`). The seed itself is the
caller's (section 11 fixes it; it is passed in, never written here).
"""
from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

import numpy as np
from scipy import stats

#: 9.2 item 2
LEVEL = 0.90
MIN_WINDOWS = 4
#: 9.2 item 7: the label's floor, and the shapes that set it
LABEL_FLOOR = 0.88
LABEL_SHAPES = ("gauss", "ahead", "paired")
#: 9.2 item 7: the honesty series per setting, and the lumpy and persistent shapes' grid
HONESTY_SERIES = 20_000
G = 0.01
PS = (0.05, 0.10, 0.20)
SS = (0.0025, 0.005, 0.01)
#: 9.2 item 7: the shapes in their declared order (indices 0 to 20)
SHAPES: tuple[tuple[str, float | None, float | None], ...] = (
    ("gauss", None, None), ("ahead", None, None), ("paired", None, None),
    *(("lumpy", p, s) for p in PS for s in SS),
    *(("persistent", p, s) for p in PS for s in SS),
)
#: the second element of the honesty series' key: the reading's table, and T-6 (section 11)
HONESTY_KEY, T6_KEY = 1, 0

MONTH = 21
#: 5 item 3's table: each measure's horizon in sessions
HORIZONS: dict[str, int] = {
    "S3a": 21,
    "P": 63, "ahead_m1": 63, "ahead_m2": 63, "ahead_m3": 63, "S3c": 63, "S5a": 63, "net_m1": 63, "net_m2": 63,
    "net_m3": 63, "cvar10_m3": 63, "P_bankroll_limit": 63,
    "S1": 126, "S3b": 126, "S4a": 126, "S5b": 126, "S5c": 126, "first_pass_sessions": 126, "first_pass_cash": 126,
    "first_payout_sessions": 126, "first_payout_cash": 126,
    "S2": 126, "S3d": 126, "Q": 126,
    "ahead_m9": 189, "net_m9": 189,
    "S4b": 252, "break_even_sessions": 252, "fell_back": 252, "deepest_fall": 252, "positive_months": 252,
    "longest_no_payout_run": 252, "monthly_net_spread": 252, "payouts_per_month": 252, "largest_month_share": 252,
}
#: the horizons the reading reads (T-3 covers each)
HORIZON_SET = (21, 63, 126, 189, 252)


def month_horizon(m: int) -> int:
    """A share at month m: 63 for m up to 3 (P's horizon, as P reads them), else 21 m."""
    m = int(m)
    if m < 1:
        raise ValueError(f"a month is at least 1, got {m}")
    return 3 * MONTH if m <= 3 else MONTH * m


def horizon(measure: str) -> int:
    """5 item 3: a measure's horizon; a share at month m by `month_horizon` (keys `share_m<m>`, `paired_m<m>`)."""
    if measure in HORIZONS:
        return HORIZONS[measure]
    for prefix in ("share_m", "paired_m", "broken_even_m"):
        if measure.startswith(prefix) and measure[len(prefix):].isdigit():
            return month_horizon(int(measure[len(prefix):]))
    raise KeyError(f"no declared horizon for {measure!r} (RD-02 5 item 3)")


def card_horizon_problems() -> list[str]:
    """The card's keys against `u_select.MEASURES` (the vendored scorecard's own horizons): empty when they agree."""
    from propedge.research import u_select as US

    out = []
    for m in US.MEASURES:
        if m.key in HORIZONS and HORIZONS[m.key] != int(m.horizon):
            out.append(f"{m.key}: {HORIZONS[m.key]} here, {m.horizon} in u_select")
        if m.key not in HORIZONS:
            out.append(f"{m.key}: no horizon here")
    if HORIZONS["P"] != int(US.P_HORIZON):
        out.append(f"P: {HORIZONS['P']} here, P_HORIZON {US.P_HORIZON}")
    return out


def journey_horizon_problems() -> list[str]:
    """E-014's journey variables against Q-17's windows (`extended.user_readings`)."""
    from extended import user_readings as R

    out = []
    for k in ("first_pass_sessions", "first_pass_cash", "first_payout_sessions", "first_payout_cash"):
        if HORIZONS[k] != int(R.FIRST_WINDOW):
            out.append(f"{k}: {HORIZONS[k]}, Q-17's FIRST_WINDOW {R.FIRST_WINDOW}")
    for k in ("break_even_sessions", "fell_back", "deepest_fall", "positive_months", "longest_no_payout_run",
              "monthly_net_spread", "payouts_per_month", "largest_month_share"):
        if HORIZONS[k] != int(R.YEAR_WINDOW):
            out.append(f"{k}: {HORIZONS[k]}, Q-17's YEAR_WINDOW {R.YEAR_WINDOW}")
    return out


def block(records: Sequence[Mapping[str, Any]], which: str | None, measure: str) -> list[Mapping[str, Any]]:
    """5 item 3: `u_select.block` at the measure's horizon."""
    from propedge.research import u_select as US

    return US.block(records, which, horizon(measure))


def by_year(records: Sequence[Mapping[str, Any]], measure: str) -> dict[int, list[Mapping[str, Any]]]:
    """9.1 item 10: each start year's starts with the measure's h left -- means only, not purged."""
    h = horizon(measure)
    out: dict[int, list[Mapping[str, Any]]] = {}
    for r in sorted(records, key=lambda r: int(r["start_day"])):
        if int(r["observed"]) >= h:
            out.setdefault(int(str(r["start_date"])[:4]), []).append(r)
    return out


def reading(records: Sequence[Mapping[str, Any]], which: str | None, measure: str,
            value: Callable[[Mapping[str, Any], int], float]) -> dict[str, Any]:
    """A measure's per-start values on a block (`value(record, h)` reads the start's first h sessions) and their
    summary: the starts, the mean, p10, p50, p90."""
    h = horizon(measure)
    sel = block(records, which, measure)
    v = np.array([float(value(r, h)) for r in sel], float)
    q = np.percentile(v, [10, 50, 90]) if v.size else np.full(3, np.nan)
    return {"measure": measure, "h": h, "block": which, "starts": [int(r["start_day"]) for r in sel],
            "values": v, "mean": float(v.mean()) if v.size else float("nan"), "p10": float(q[0]),
            "p50": float(q[1]), "p90": float(q[2])}


# ------------------------------------------------------------------------------------------------ 9.2


def kept_windows(n_starts: int, h: int, rule: str = "separated") -> list[tuple[int, int]]:
    """9.2 item 1: the [first, last + 1) start indices of the windows: h consecutive starts from the block's first, a
    last incomplete window dropped; `separated` keeps every other one from the first (the declared rule), `adjacent`
    all (the second version's, kept for its honesty check's contrast)."""
    n_all = int(n_starts) // int(h)
    if rule == "separated":
        js = range(0, n_all, 2)
    elif rule == "adjacent":
        js = range(n_all)
    else:
        raise ValueError(rule)
    return [(j * int(h), (j + 1) * int(h)) for j in js]


def window_means(series: np.ndarray, h: int, rule: str = "separated") -> np.ndarray:
    """The kept windows' means of a per-start series (the last axis)."""
    y = np.asarray(series, float)
    w = kept_windows(y.shape[-1], h, rule)
    if not w:
        return np.zeros(y.shape[:-1] + (0,))
    return np.stack([y[..., a:b].mean(axis=-1) for a, b in w], axis=-1)


def t_interval(means: Sequence[float]) -> tuple[float, float] | None:
    """9.2 item 2: the two-sided 90 % Student-t interval on the kept windows' means, n_w - 1 degrees of freedom; None
    below 4 windows or with no spread (item 6)."""
    m = np.asarray(means, float)
    n = m.size
    if n < MIN_WINDOWS:
        return None
    se = m.std(ddof=1) / np.sqrt(n)
    if not se > 0:
        return None
    t = stats.t.ppf(0.5 + LEVEL / 2, n - 1)
    return float(m.mean() - t * se), float(m.mean() + t * se)


def mdd(means: Sequence[float]) -> float | None:
    """9.2 item 5: (t(0.95; n_w - 1) + t(0.80; n_w - 1)) x the kept windows' standard error; None as the interval."""
    m = np.asarray(means, float)
    n = m.size
    if n < MIN_WINDOWS:
        return None
    se = m.std(ddof=1) / np.sqrt(n)
    if not se > 0:
        return None
    return float((stats.t.ppf(0.95, n - 1) + stats.t.ppf(0.80, n - 1)) * se)


def sign_count(cell_means: Sequence[float], base_means: Sequence[float]) -> tuple[int, int, int]:
    """9.2 item 3: in how many kept windows the cell's mean is above, equal to and below its base's."""
    c, b = np.asarray(cell_means, float), np.asarray(base_means, float)
    return int(np.sum(c > b)), int(np.sum(c == b)), int(np.sum(c < b))


def describe(per_start_diff: Sequence[float], h: int) -> str:
    """9.2 items 2 and 6: what a reading prints -- "identical on these trades" (zero on every start), "too few
    separated windows for an interval" (under 4 kept), "no spread across the separated windows" (kept means all
    equal), or "interval"."""
    d = np.asarray(per_start_diff, float)
    if not np.any(d != 0):
        return "identical on these trades"
    m = window_means(d, h)
    if m.size < MIN_WINDOWS:
        return "too few separated windows for an interval"
    if not np.std(m, ddof=1) > 0:
        return "no spread across the separated windows"
    return "interval"


def label(coverage: Mapping[str, float]) -> bool:
    """9.2 item 7 (Q-102's M1): "under-covers at this window count" where the lowest coverage of gauss, ahead and
    paired is below 0.88; the lumpy and persistent shapes are printed beside and never set it."""
    return min(float(coverage[k]) for k in LABEL_SHAPES) < LABEL_FLOOR


def rare_line(coverage: Mapping[str, float], above: Mapping[str, float], below: Mapping[str, float]
              ) -> dict[str, Any]:
    """9.2 item 7: the line beside every interval -- the lowest coverage over the lumpy and persistent shapes, its
    shape, and that shape's misses above and below (no threshold)."""
    rare = {k: float(v) for k, v in coverage.items() if k.startswith(("lumpy", "persistent"))}
    k = min(rare, key=lambda x: (rare[x], x))
    return {"shape": k, "coverage": rare[k], "miss_above": float(above[k]), "miss_below": float(below[k])}


def shape_name(kind: str, p: float | None, s: float | None) -> str:
    return kind if p is None else f"{kind}_{p:g}_{s:g}"


# ---- the honesty series (9.2 item 7), on sessions as the reading's own series are built


def per_start_means(x: np.ndarray, h: int) -> np.ndarray:
    """(reps, n_sessions) per-session values -> (reps, n_sessions - h + 1): each start's mean of its own h sessions."""
    c = np.zeros((x.shape[0], x.shape[1] + 1))
    np.cumsum(x, axis=1, out=c[:, 1:])
    return (c[:, h:] - c[:, :-h]) / h


def lumpy_sessions(rng: Any, shape: tuple[int, int], h: int, p: float, s: float, g: float = G) -> np.ndarray:
    q = p / h
    rare = rng.random(shape) < q
    return np.where(rare, -g * (1 - q) / q, g) + rng.normal(0.0, s * np.sqrt(h), shape)


def persistent_states(rng: Any, shape: tuple[int, int], h: int, p: float) -> np.ndarray:
    reps, n = shape
    r, stay = p / h, 1.0 - 1.0 / h
    pi = r / (r + 1.0 / h)
    out = np.empty(shape, bool)
    out[:, 0] = rng.random(reps) < pi
    u = rng.random(shape)
    for t in range(1, n):
        out[:, t] = np.where(out[:, t - 1], u[:, t] < stay, u[:, t] < r)
    return out


def persistent_sessions(rng: Any, shape: tuple[int, int], h: int, p: float, s: float, g: float = G) -> np.ndarray:
    r = p / h
    pi = r / (r + 1.0 / h)
    rare = persistent_states(rng, shape, h, p)
    return np.where(rare, -g * (1 - pi) / pi, g) + rng.normal(0.0, s * np.sqrt(h), shape)


def start_series(kind: str, rng: Any, reps: int, n_starts: int, h: int, p: float | None = None,
                 s: float | None = None) -> np.ndarray:
    """(reps, n_starts) per-start series of known zero mean, built from sessions: 9.2 item 7's five kinds."""
    n_sess = n_starts + h - 1
    if kind == "gauss":
        return per_start_means(rng.standard_normal((reps, n_sess)), h)
    if kind == "ahead":
        return (per_start_means(rng.standard_normal((reps, n_sess)), h) > 0).astype(float) - 0.5
    if kind == "paired":
        z = rng.standard_normal((reps, n_sess))
        a = per_start_means(0.8 * z + 0.6 * rng.standard_normal((reps, n_sess)), h)
        b = per_start_means(0.8 * z + 0.6 * rng.standard_normal((reps, n_sess)), h)
        return (a > 0).astype(float) - (b > 0).astype(float)
    if kind == "lumpy":
        return per_start_means(lumpy_sessions(rng, (reps, n_sess), h, p, s), h)
    if kind == "persistent":
        return per_start_means(persistent_sessions(rng, (reps, n_sess), h, p, s), h)
    raise ValueError(kind)


def coverage(kind: str, n_w: int, h: int, rng: Any, reps: int, *, rule: str = "separated", p: float | None = None,
             s: float | None = None, chunk: int = 500) -> dict[str, float]:
    """The share of `reps` zero-mean series whose 90 % interval on `rule`'s windows holds 0, and the shares missing
    above and below."""
    n_starts = ((2 * n_w - 1) if rule == "separated" else n_w) * h
    w = kept_windows(n_starts, h, rule)
    if len(w) != n_w:
        raise RuntimeError(f"{len(w)} windows, not {n_w}")
    t = stats.t.ppf(0.5 + LEVEL / 2, n_w - 1)
    hits = above = below = 0
    for k in range(0, reps, chunk):
        y = start_series(kind, rng, min(chunk, reps - k), n_starts, h, p, s)
        m = np.stack([y[:, a:b].mean(axis=1) for a, b in w], axis=1)
        mu = m.mean(axis=1)
        se = m.std(axis=1, ddof=1) / np.sqrt(n_w)
        lo, hi = mu - t * se, mu + t * se
        hits += int(np.sum((lo <= 0) & (0 <= hi)))
        above += int(np.sum(lo > 0))
        below += int(np.sum(hi < 0))
    return {"coverage": hits / reps, "miss_above": above / reps, "miss_below": below / reps}


def honesty_rng(seed: int, shape_index: int, h: int, n_w: int) -> Any:
    """9.2 item 7: a setting's generator, `default_rng([seed, 1, shape, h, n_w])` (section 11's key)."""
    return np.random.default_rng([int(seed), HONESTY_KEY, int(shape_index), int(h), int(n_w)])


__all__ = ["LEVEL", "MIN_WINDOWS", "LABEL_FLOOR", "LABEL_SHAPES", "HONESTY_SERIES", "SHAPES", "HONESTY_KEY", "T6_KEY",
           "HORIZONS", "HORIZON_SET", "month_horizon", "horizon", "card_horizon_problems", "journey_horizon_problems",
           "block", "by_year", "reading", "kept_windows", "window_means", "t_interval", "mdd", "sign_count",
           "describe", "label", "rare_line", "shape_name", "per_start_means", "lumpy_sessions", "persistent_states",
           "persistent_sessions", "start_series", "coverage", "honesty_rng"]
