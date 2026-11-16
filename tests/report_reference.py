"""An independent reading of the journey measures (Q-27; E-014), in plain Python on start rows -- what
`extended/report.py`'s `quantity` is checked against on synthetic files (`tests/report_cases.py`, case `measures`).

Nothing here imports numpy, pandas, the vendored engine or `extended`: each measure is written out from its definition
in `extended/report.py`'s docstring, with loops, so a shared mistake would have to be made twice. The percentile is
numpy's default (linear between the order statistics), written by hand; a days-to-event percentile counts an
unreached start as beyond the window and is blank when it falls beyond (Stage 2's `customer_journey._days_q`).

Keys follow `extended.report.quantity`'s grammar (`dist:<name>:<p10|p50|...|n|starts|stretch>`,
`share:<name>:<month>`, `share_n:<name>:<month>`, `share:fell_back`, `share_n:fell_back`, `rows`).
"""
from __future__ import annotations

import math
import statistics

MONTH, MONTHS = 21, 12
YEAR = MONTH * MONTHS
PASS_WINDOW, PAYOUT_WINDOW = 42, 126
TOL = 1e-6          # money: a net within a millionth of a dollar of zero is at zero
CENT = 0.005        # a month's payout cash, or a year's, counts only above half a cent
BEYOND = 1e9
NAN = float("nan")


def _blank(s) -> bool:
    return s is None or (isinstance(s, float) and math.isnan(s)) or str(s).strip() in ("", "nan", "NaN", "None")


def num(x) -> float:
    return NAN if _blank(x) else float(str(x).strip())


def ints(x) -> list[int]:
    return [] if _blank(x) else [int(float(v)) for v in str(x).split()]


def floats(x) -> list[float]:
    return [] if _blank(x) else [float(v) for v in str(x).split()]


def finite(x: float) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(x)


def percentile(xs: list[float], p: float) -> float:
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return NAN
    h = (n - 1) * p / 100.0
    lo = math.floor(h)
    hi = min(lo + 1, n - 1)
    return xs[lo] + (h - lo) * (xs[hi] - xs[lo])


def days_percentile(firsts: list[float], last: int, p: float) -> float:
    vals = [f if finite(f) and f <= last else BEYOND for f in firsts]
    q = percentile(vals, p)
    return q if finite(q) and q <= last else NAN


class Row:
    def __init__(self, r: dict):
        self.start_day = int(float(r["start_day"]))
        self.observed = int(float(r["observed"]))
        self.pays = sorted(ints(r.get("pay_days")))
        self.pay_cash = floats(r.get("pay_cash")) if "pay_cash" in r else None
        self.path = floats(r.get("net_by_session")) if "net_by_session" in r else None
        self.first_pass = num(r.get("first_pass"))
        self.first_payout = num(r.get("first_payout"))
        self.first_payout_cash = num(r.get("first_payout_cash"))
        self.spent_pass = num(r.get("spent_before_first_pass"))
        self.spent_payout = num(r.get("spent_before_first_payout"))
        self.net = [num(r.get(f"net_month_{k}")) for k in range(1, MONTHS + 1)]
        self.fees = [num(r.get(f"fees_month_{k}")) for k in range(1, MONTHS + 1)]

    # -- the year's evenness (start days with the whole year observed)
    def year_ok(self) -> bool:
        return self.observed >= YEAR and all(finite(x) for x in self.net + self.fees)

    def changes(self) -> list[float]:
        out, prev = [], 0.0
        for x in self.net:
            out.append(x - prev)
            prev = x
        return out

    def received(self) -> list[float]:
        return [n + f for n, f in zip(self.net, self.fees)]

    def paid_months(self) -> list[float]:
        out, prev = [], 0.0
        for x in self.received():
            out.append(x - prev)
            prev = x
        return out

    def month_counts(self) -> list[int]:
        c = [0] * MONTHS
        for d in self.pays:
            if 1 <= d <= YEAR:
                c[(d - 1) // MONTH] += 1
        return c

    def gain_share(self) -> float:
        ch = self.changes()
        return sum(1 for x in ch if x > 0) / len(ch)

    def dry_run(self) -> float:
        best = run = 0
        for c in self.month_counts():
            run = run + 1 if c == 0 else 0
            best = max(best, run)
        return float(best)

    def monthly_sd(self) -> float:
        return statistics.stdev(self.changes())

    def per_month(self) -> float:
        return sum(1 for d in self.pays if d <= YEAR) / MONTHS

    def largest_share(self) -> float:
        total = self.received()[-1]
        if not total > CENT:
            return NAN
        return max(self.paid_months()) / total

    def gaps(self) -> list[float]:
        days = sorted({d for d in self.pays if d <= YEAR})
        return [float(b - a) for a, b in zip(days, days[1:])]

    # -- the daily path
    def be_day(self) -> float:
        if not hasattr(self, "_be"):
            self._be = NAN
            for k in range(1, min(self.observed, YEAR) + 1):
                if self.path[k] >= -TOL:
                    self._be = float(k)
                    break
        return self._be

    def fell_back(self) -> bool:
        b = self.be_day()
        return finite(b) and any(self.path[j] < -TOL for j in range(int(b) + 1, min(self.observed, YEAR) + 1))

    def fall(self) -> float:
        b = self.be_day()
        if not finite(b):
            return NAN
        high, worst = -math.inf, 0.0
        for j in range(int(b), min(self.observed, YEAR) + 1):
            high = max(high, self.path[j])
            worst = max(worst, high - self.path[j])
        return worst


# --------------------------------------------------------------------------------------------- the distributions

def _dist(rows: list[Row], name: str) -> tuple[list[float], int, int | None, int]:
    """(values, start days read, the days window when it is a days-to-event reading, the window in sessions)."""
    if name in ("pass_days", "pass_cash"):
        w = PASS_WINDOW
        el = [r for r in rows if r.observed >= w]
        if name == "pass_days":
            return [r.first_pass for r in el], len(el), w, w
        got = [r for r in el if finite(r.first_pass) and r.first_pass <= w]
        return [r.spent_pass for r in got], len(got), None, w
    if name in ("payout_days", "payout_cash", "first_payout_size"):
        w = PAYOUT_WINDOW
        el = [r for r in rows if r.observed >= w]
        if name == "payout_days":
            return [r.first_payout for r in el], len(el), w, w
        got = [r for r in el if finite(r.first_payout) and r.first_payout <= w]
        if name == "payout_cash":
            return [r.spent_payout for r in got], len(got), None, w
        return [r.first_payout_cash for r in got], len(got), None, w
    if name.startswith("net_"):
        m = int(name.split("_")[1])
        el = [r for r in rows if r.observed >= MONTH * m and finite(r.net[m - 1])]
        return [r.net[m - 1] for r in el], len(el), None, MONTH * m
    year = [r for r in rows if r.year_ok()]
    if name == "breakeven_days":
        el = [r for r in rows if r.observed >= YEAR]
        return [r.be_day() for r in el], len(el), YEAR, YEAR
    if name == "breakeven_fall":
        el = [r for r in rows if r.observed >= YEAR and finite(r.be_day())]
        return [r.fall() for r in el], len(el), None, YEAR
    per_start = {"gain_months": Row.gain_share, "dry_months": Row.dry_run, "monthly_spread": Row.monthly_sd,
                 "payouts_per_month": Row.per_month}
    if name in per_start:
        return [per_start[name](r) for r in year], len(year), None, YEAR
    if name == "largest_month":
        vals = [r.largest_share() for r in year]
        vals = [v for v in vals if finite(v)]
        return vals, len(vals), None, YEAR
    if name == "payout_size":
        vals = [c for r in year for d, c in zip(r.pays, r.pay_cash) if d <= YEAR]
        return vals, len(year), None, YEAR
    if name == "month_payout":
        vals = [x for r in year for x in r.paid_months() if x > CENT]
        return vals, len(year), None, YEAR
    if name == "payout_gap":
        vals = [g for r in year for g in r.gaps()]
        return vals, len(year), None, YEAR
    raise KeyError(name)


def quantity(raw_rows: list, key: str) -> float:
    """One number from a design's start rows (dicts as read from the CSV, or `Row`s parsed once)."""
    rows = [r if isinstance(r, Row) else Row(r) for r in raw_rows]
    if key == "rows":
        return float(len(rows))
    parts = key.split(":")
    if parts[0] == "dist":
        vals, starts, last, window = _dist(rows, parts[1])
        stat = parts[2]
        if stat == "n":
            return float(len(vals) if parts[1] in ("payout_size", "month_payout", "payout_gap") else starts)
        if stat == "starts":
            return float(starts)
        if stat == "stretch":
            return starts / window
        p = float(stat[1:])
        if last is not None:
            return days_percentile(vals, last, p) if vals else NAN
        return percentile([v for v in vals if finite(v)], p)
    if parts[0] in ("share", "share_n"):
        if parts[1] == "fell_back":
            el = [r for r in rows if r.observed >= YEAR and finite(r.be_day())]
            if parts[0] == "share_n":
                return float(len(el))
            return sum(1 for r in el if r.fell_back()) / len(el) if el else NAN
        m = int(parts[2])
        d = MONTH * m
        if parts[1] == "ahead":
            el = [r for r in rows if r.observed >= d and finite(r.net[m - 1])]
            hit = [r.net[m - 1] > 0 for r in el]
        elif parts[1] == "paid":
            el = [r for r in rows if r.observed >= d]
            hit = [finite(r.first_payout) and r.first_payout <= d for r in el]
        elif parts[1] == "breakeven":
            el = [r for r in rows if r.observed >= d]
            hit = [finite(r.be_day()) and r.be_day() <= d for r in el]
        else:
            raise KeyError(key)
        if parts[0] == "share_n":
            return float(len(el))
        return sum(hit) / len(el) if el else NAN
    raise KeyError(key)


#: every key the reference reads, for a file with the daily path and every payout's cash
DIST_NAMES = ("pass_days", "pass_cash", "payout_days", "payout_cash", "first_payout_size", "net_1", "net_3", "net_12",
              "breakeven_days", "breakeven_fall", "gain_months", "dry_months", "monthly_spread", "payouts_per_month",
              "largest_month", "payout_size", "month_payout", "payout_gap")
DAILY = ("breakeven_days", "breakeven_fall")
CASH = ("payout_size",)


def keys(*, daily: bool = True, cash: bool = True) -> list[str]:
    out = ["rows"]
    for name in DIST_NAMES:
        if (name in DAILY and not daily) or (name in CASH and not cash):
            continue
        out += [f"dist:{name}:{s}" for s in ("p10", "p25", "p50", "p75", "p90", "n", "starts", "stretch")]
    for m in (1, 2, 3, 6, 12):
        for s in ("ahead", "paid") + (("breakeven",) if daily else ()):
            out += [f"share:{s}:{m}", f"share_n:{s}:{m}"]
    if daily:
        out += ["share:fell_back", "share_n:fell_back"]
    return out
