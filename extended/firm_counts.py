"""RD-01's tier-1 windows and bookings (5.5, A-11) and the 9.3 counts (`prereg/RD-01_firm_contracts.md`).

**The windows (5.5).** For NQ and MNQ, TradeDay's tier-1 releases are US CPI and the employment report at 7:30 AM CT and
the FOMC statement and minutes at 1:00 PM CT (`tradeday.tier1_release_list`), every position auto-liquidated two
minutes before and nothing traded until two minutes after (`tradeday.tier1_news_auto_liquidation`). The dates come
from the files 5.5 fixes: BLS's schedules as Stage 2 vendored them (the rows whose release begins "Consumer Price Index
for" or "Employment Situation for"), Stage 2's FOMC statement days, and the pinned FOMC-minutes calendar.

**The clock** is Stage 2's (`extended.walker`): a trade's entry and exit are bar indices by each bar's END minute after
17:00 CT (the bar stamped at hh:mm is index `slot(hh, mm) + 1`). A trade is **open at a window's start** t0 when its
entry bar is stamped before t0 and its exit bar at or after t0, at any offered R (`DayBlock.exit_by_rr`); an entry bar
stamped from t0 to before the window's end is an **entry inside** the window.

**The bookings (5.5).** Strict: the whole risk lost, with a stop exit's costs. Lenient: the target less one tick, with
the flatten's two-tick cost. In R, by Stage 2's cost rule (`extended.walker.cost_r`) at the trade's stop ticks (its
`risk_per_contract` over the tick value) and its fee per micro-equivalent. "No liquidation" keeps the walked outcome.
A-11 applies them to the run's trade log before the arms are shifted, so a booked trade takes its R's verdict shift
(5.5, note C), on evaluations and Funded Sim alike; the exits stay the walked ones (the one-position rule).

**The 9.3 counts.** DayTraders' martingale steps (a trade at least twice the micro-equivalents of the trade before it
when that one closed at a loss), within one account and across the user's accounts in time order; TradeDay's trades a
session, per account and across the accounts, against its 200-trades line.

Pure Python: nothing here imports the engine.
"""
from __future__ import annotations

import csv
import hashlib
import math
from dataclasses import replace
from datetime import date
from functools import lru_cache
from typing import Any, Sequence

import numpy as np

from extended import ROOT
from extended import firm_terms as T
from extended import walker as W

BLS_CALENDARS = (ROOT / "vendor" / "stage2" / "data" / "releases_bls_0830_2009_2025.csv",
                 ROOT / "vendor" / "stage2" / "data" / "releases_bls_0830_2026.csv")
BLS_RELEASES = {"cpi": "Consumer Price Index for", "employment": "Employment Situation for"}
#: the pinned calendars RD-01 cites (5.5, 9.3): a file that does not hash to its pin is refused
FOMC_MINUTES_SHA256 = "0350d41fe224909d93ae9211761e839c4925c231b83f039ccb92f1d8a4127ce7"
EARLY_CLOSES_SHA256 = "72db4941f95320900aac29c6c047742da176cd9b55c925cc9275a18fb3e67fb2"
WINDOW_FIRST, WINDOW_LAST = date(2020, 1, 2), date(2026, 7, 16)


def _lf_sha256(path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _hhmm(m: Any) -> tuple[int, int]:
    h = int(m.group(1)) % 12 + (12 if m.group(3) == "PM" else 0)
    return h, int(m.group(2))


@lru_cache(maxsize=1)
def window_spec() -> dict[str, tuple[int, int]]:
    """{'morning': (start, end), 'afternoon': (start, end)} as slots (minutes after 17:00 CT): the releases' CT times
    from `tradeday.tier1_release_list`, the margins from `tradeday.tier1_news_auto_liquidation`."""
    lst = T.record_value("tradeday.tier1_release_list")
    liq = T.record_value("tradeday.tier1_news_auto_liquidation")
    before = int(T.parse_money(r"auto-liquidated (\d+) minutes before", liq, "tradeday.tier1_news_auto_liquidation"))
    after = int(T.parse_money(r"reopened to trade (\d+) minutes after", liq, "tradeday.tier1_news_auto_liquidation"))
    key = "tradeday.tier1_release_list"
    T.parse(r"^seven releases, CT:", lst, key)                         # the times below are Chicago's
    t = r"(\d+):(\d\d) (AM|PM)"
    cpi, emp = (_hhmm(T.parse(r"US CPI " + t, lst, key)),
                _hhmm(T.parse(r"US employment report \(Non-Farm Payrolls\) " + t, lst, key)))
    mins, stmt = (_hhmm(T.parse(r"FOMC minutes " + t, lst, key)),
                  _hhmm(T.parse(r"FOMC interest rate decision statement " + t, lst, key)))
    if cpi != emp or mins != stmt:
        raise T.TermParseError(f"{key}: the morning or the afternoon releases no longer share one time")
    am, pm = cpi, stmt
    out = {}
    for name, (h, m) in (("morning", am), ("afternoon", pm)):
        t = W.slot(h, m)
        out[name] = (t - before, t + after)
    return out


@lru_cache(maxsize=1)
def tier1_days() -> dict[date, list[str]]:
    """Every tier-1 day for NQ and MNQ in the development window, with its releases (5.5's files)."""
    from extended import calendar_fomc_minutes as M

    if _lf_sha256(M.CALENDAR_CSV) != FOMC_MINUTES_SHA256:
        raise ValueError(f"{M.CALENDAR_CSV.name} does not hash to its pin (E-050)")
    out: dict[date, list[str]] = {}

    def add(d: date, kind: str) -> None:
        if WINDOW_FIRST <= d <= WINDOW_LAST and kind not in out.setdefault(d, []):
            out[d].append(kind)

    for path in BLS_CALENDARS:
        for r in csv.DictReader(path.open(encoding="utf-8")):
            for kind, head in BLS_RELEASES.items():
                if str(r["release"]).startswith(head):
                    add(date.fromisoformat(r["date"]), kind)
    for s in M.fomc_statement_days():
        add(date.fromisoformat(str(s)), "fomc_statement")
    for d in M.release_days():
        add(d, "fomc_minutes")
    return {d: sorted(v) for d, v in sorted(out.items())}


def windows_of(kinds: Sequence[str]) -> list[str]:
    """The windows a tier-1 day's releases open: the morning (CPI, employment) and the afternoon (FOMC)."""
    out = []
    if {"cpi", "employment"} & set(kinds):
        out.append("morning")
    if {"fomc_statement", "fomc_minutes"} & set(kinds):
        out.append("afternoon")
    return out


def open_at(entry: float, exits_by_rr: dict[float, float], t0: int) -> bool:
    """A trade open at the window's start t0 at some offered R: its entry bar stamped before t0 (index <= t0) and its
    exit bar at that R stamped at or after t0 (index >= t0 + 1)."""
    if not entry <= t0:
        return False
    return any(np.isfinite(x) and x >= t0 + 1 for x in exits_by_rr.values())


def entry_inside(entry: float, window: str) -> bool:
    """An entry bar stamped inside the window: from its start to before its end."""
    t0, t1 = window_spec()[window]
    return t0 + 1 <= entry <= t1


def book(R: float, stop_ticks: int, fee_micro_eq: float, reading: str) -> float:
    """A liquidated trade's net outcome in R (5.5): 'strict' -- the whole risk lost with a stop exit's costs;
    'lenient' -- the target less one tick with the flatten's two-tick cost. 'walked' is the trade's own outcome."""
    costs = W.Costs(fee_micro_eq=float(fee_micro_eq))
    S = int(stop_ticks)
    if reading == T.STRICT:
        return float(-1.0 - W.cost_r(np.array([W.STOP]), S, entry_ticks=W.SLIP_TICKS, costs=costs)[0])
    if reading == T.LENIENT:
        gross = (W.target_ticks(float(R), S) - 1) / S
        return float(gross - W.cost_r(np.array([W.FLATTEN]), S, entry_ticks=W.SLIP_TICKS, costs=costs)[0])
    raise ValueError(f"a booking is 'strict' or 'lenient', not {reading!r} (the walked outcome is the trade's own)")


def tier1_blocks(blocks: Sequence[Any], dates: Sequence[date], reading: str) -> tuple[list[Any], dict[str, int]]:
    """A-11 on a run's trade log (point arm, before the verdict shift): on each tier-1 day, a trade open at a window's
    start is booked by `reading` ('strict', 'lenient', or 'walked' to keep it) at every R it offers, its MAE at least
    its booked loss, its exits unchanged; an entry inside a window is skipped (no outcome at any R). Other days' blocks
    are returned as they are. Also the counts: trades open at a window's start, entries inside one."""
    if reading not in (T.STRICT, T.LENIENT, "walked"):
        raise ValueError(f"unknown reading {reading!r}")
    days = tier1_days()
    spec = window_spec()
    out, n_open, n_in, both_windows = [], 0, 0, 0
    for b, d in zip(blocks, dates):
        kinds = days.get(d if isinstance(d, date) else date.fromisoformat(str(d)[:10]))
        if not kinds or b.r_by_rr is None or b.exit_by_rr is None or b.entry_t is None or len(b.pnl) == 0:
            out.append(b)
            continue
        r_by = {k: np.array(v, float) for k, v in b.r_by_rr.items()}
        mae_by = None if b.mae_by_rr is None else {k: np.array(v, float) for k, v in b.mae_by_rr.items()}
        pnl = np.array(b.pnl, float)
        changed = False
        both_windows += int(len(windows_of(kinds)) > 1)
        order = sorted(windows_of(kinds), key=lambda w: spec[w][0])      # a day's windows in time order
        for j in range(len(b.pnl)):
            ex = {float(k): float(v[j]) for k, v in b.exit_by_rr.items() if np.isfinite(float(r_by[k][j]))}
            own = float(pnl[j] / b.risked[j]) if b.risked[j] > 0 else math.nan
            for w in order:                                               # the trade counted once, at its first window
                t0 = spec[w][0]
                if entry_inside(float(b.entry_t[j]), w):
                    n_in += 1
                    changed = True
                    for k in r_by:
                        r_by[k][j] = np.nan
                    pnl[j] = np.nan
                    break
                if open_at(float(b.entry_t[j]), ex, t0):
                    n_open += 1
                    if reading == "walked":
                        break
                    S = int(round(float(b.risk_per_contract[j]) / W.Costs(fee_micro_eq=0.0).tick_value))
                    fee = float(b.fee[j]) if b.fee is not None else 0.0
                    for k in r_by:
                        # 5.5 (M1): booked only at an R at which the position is still open at the window's start --
                        # its exit bar there at or after it; at every other R the walked outcome and MAE stay
                        if not np.isfinite(r_by[k][j]) or not ex.get(float(k), -np.inf) >= t0 + 1:
                            continue
                        hit = math.isclose(float(r_by[k][j]), own, abs_tol=1e-12)
                        changed = True
                        r_by[k][j] = book(float(k), S, fee, reading)
                        if mae_by is not None and k in mae_by:
                            mae_by[k][j] = max(float(mae_by[k][j]), -float(r_by[k][j]))
                        if hit:
                            pnl[j] = r_by[k][j] * float(b.risked[j])
                    break
        out.append(replace(b, r_by_rr=r_by, mae_by_rr=mae_by, pnl=pnl) if changed else b)
    return out, {"open_at_start": n_open, "entries_inside": n_in, "days_with_both_windows": both_windows}


# ------------------------------------------------------------------------------------------------ the 9.3 counts


def martingale_steps(trades: Sequence[dict[str, Any]]) -> dict[str, int]:
    """DayTraders' martingale rule (`daytraders.martingale_rule`, 9.3): trades taken at least twice the micro-
    equivalents of the trade before them when that one closed at a loss -- within one account, and across the user's
    accounts in time order. A reading, not a ruling."""
    mult = int(T.parse_money(r"(\d+)x or more after a closed loss", T.record_value("daytraders.martingale_rule"),
                             "daytraders.martingale_rule"))
    order = sorted(range(len(trades)), key=lambda i: (trades[i]["day"], trades[i]["entry"], i))

    def step(prev: dict[str, Any], cur: dict[str, Any]) -> bool:
        return float(prev["pnl"]) < 0 and float(cur["contracts"]) >= mult * float(prev["contracts"])

    per, firm = 0, 0
    last: dict[Any, dict[str, Any]] = {}
    prev_any = None
    for i in order:
        t = trades[i]
        a = t["account"]
        if a in last and step(last[a], t):
            per += 1
        if prev_any is not None and step(prev_any, t):
            firm += 1
        last[a] = t
        prev_any = t
    return {"per_account": per, "firm_wide": firm, "trades": len(trades)}


def trade_count_line() -> int:
    """TradeDay's line: no strategy producing more than this many trades a day (`tradeday.trade_count_hold_time`)."""
    return int(T.parse_money(r"more than (\d+) trades in a day", T.record_value("tradeday.trade_count_hold_time"),
                             "tradeday.trade_count_hold_time"))


def trades_a_session(trades: Sequence[dict[str, Any]]) -> dict[str, int]:
    """TradeDay's 200-trades line (9.3): the most trades in one session in one account, and across the accounts."""
    per: dict[tuple, int] = {}
    across: dict[Any, int] = {}
    for t in trades:
        per[(t["account"], t["day"])] = per.get((t["account"], t["day"]), 0) + 1
        across[t["day"]] = across.get(t["day"], 0) + 1
    line = trade_count_line()
    return {"max_per_account": max(per.values(), default=0), "max_across": max(across.values(), default=0),
            "line": line, "sessions_above_line": sum(1 for v in across.values() if v > line)}


__all__ = ["BLS_CALENDARS", "FOMC_MINUTES_SHA256", "EARLY_CLOSES_SHA256", "window_spec", "tier1_days", "windows_of",
           "open_at", "entry_inside", "book", "tier1_blocks", "martingale_steps", "trade_count_line", "trades_a_session"]
