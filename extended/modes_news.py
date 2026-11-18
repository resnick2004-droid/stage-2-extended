"""RD-05's news rule, decided at entry (`prereg/RD-05_firm_modes.md` 4.3 A-18, 4.7 items 1 and 3; E-200 R-1).

**Which accounts a verified rule reaches** (4.7 item 1). A firm news rule applies only when its record key is
verified: My Funded Futures' Tier-1 rule (`mffu.news_tier1_rule`, verified) names the Rapid and Pro sim-funded
accounts and permits every evaluation and Builder plan; it reaches `RE`'s and `RED`'s funded accounts only at U-31's
strict end (their own `mffu.rapideod50k.funded_news` is unverified). Topstep's `tier1_news_events_restriction` is
`changed` and the Labs cap takes its windows from it: no rule reaches `TS` or any Labs account here (U1's own rule
stands there).

**The window** is the record's minutes around each release's time (`window_minutes`, parsed, never typed), on a release
day of the pinned calendar (`config/calendar_fomc_minutes.csv`, E-050).

**At entry (R-1).** An entry's time is its order's live time -- the alert plus the registered protocol's hand-entry
latency, known at the alert from the clock alone: no entry whose order would go live inside a window; an alert inside a
window whose order goes live after it is not refused; a working entry order at a window's start is cancelled ("no
positions or orders"). **At the window's start** a position open then is flattened at the 1-minute bar stamped at the
window's first minute, priced at its open with the active fill profile's flatten slippage; RD-01 G-3's bracket beside
(strict: the full stop loss; lenient: the target less a tick, with the flatten's cost).

The replay's integration (A-18 inside part F's router and walk) is part F's; these are the decisions it calls.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from extended import modes_terms as M
from extended.firm_terms import parse, record_entry


def window_minutes() -> tuple[int, int]:
    """The minutes before and after a release, parsed from the verified `mffu.news_tier1_rule`."""
    v = M.rv("mffu.news_tier1_rule")
    m = parse(r"from (\d+) minutes before to (\d+) minutes after the release", v, "mffu.news_tier1_rule")
    return int(m.group(1)), int(m.group(2))


def reaches(config: str, kind: str, corner: str) -> bool:
    """4.7 item 1: whether a verified firm news rule reaches an account of this configuration and kind at a corner."""
    if record_entry("mffu.news_tier1_rule").get("status") != "verified":
        return False
    if kind != M.FUNDED:
        parse(r"permitted on all evaluations", M.rv("mffu.news_tier1_rule"), "mffu.news_tier1_rule")
        return False
    rule = M.rv("mffu.news_tier1_rule")
    parse(r"prohibited on Rapid Sim Funded and Pro Sim Funded", rule, "mffu.news_tier1_rule")
    if config == "RI":
        return M.status("mffu.rapid50k.funded_news") == "verified"
    if config in ("PRO", "PRO1"):
        return M.status("mffu.pro50k.funded_news") == "verified"
    if config in ("RE", "RED"):
        return bool(M.end("U-31", corner))
    return False


@dataclass(frozen=True)
class Window:
    start: datetime
    end: datetime

    def contains(self, t: datetime) -> bool:
        return self.start <= t <= self.end


def window_at(release: datetime) -> Window:
    before, after = window_minutes()
    return Window(release - timedelta(minutes=before), release + timedelta(minutes=after))


def entry_refused(alert: datetime, latency_minutes: int, windows: list[Window]) -> bool:
    """R-1: refused iff the order's live time (the alert plus the hand-entry latency) falls inside a window."""
    live = alert + timedelta(minutes=int(latency_minutes))
    return any(w.contains(live) for w in windows)


def order_cancelled(alert: datetime, latency_minutes: int, filled_at: datetime | None, windows: list[Window]) -> bool:
    """R-1: a working entry order (live, not yet filled) at a window's start is cancelled."""
    live = alert + timedelta(minutes=int(latency_minutes))
    for w in windows:
        if live < w.start and (filled_at is None or filled_at >= w.start):
            return True
    return False


def forced_flat(entry_fill: datetime, exit_time: datetime, windows: list[Window]) -> Window | None:
    """A position open at a window's start is flattened at that bar: the first window whose start lies strictly after
    the fill and at or before the position's own exit."""
    for w in sorted(windows, key=lambda x: x.start):
        if entry_fill < w.start <= exit_time:
            return w
    return None


def flatten_price(bar_open: float, side: int, tick_size: float) -> float:
    """The forced flat's price: the window's first bar's open, the active profile's flatten slippage against the
    position (`side` +1 long, -1 short)."""
    slip = M.fill_slippage()["flatten_slippage_ticks"]
    return float(bar_open) - int(side) * float(slip) * float(tick_size)


def g3_bracket(stop_loss: float, target_gain: float, tick_value: float, flatten_cost: float) -> tuple[float, float]:
    """RD-01 G-3's bracket on a flattened trade's own P&L: (strict: the full stop loss; lenient: the target less a
    tick, with the flatten's cost)."""
    return (-abs(float(stop_loss)), abs(float(target_gain)) - float(tick_value) - float(flatten_cost))


__all__ = ["window_minutes", "reaches", "Window", "window_at", "entry_refused", "order_cancelled", "forced_flat",
           "flatten_price", "g3_bracket", "tier1_counts"]


def tier1_counts(trades: list[dict], windows: list[Window], reached: set[int]) -> dict[str, int]:
    """4.7 item 1's tier-1 counts on a firm's trade records (each a dict: `account`, `entry`, `exit`, `live`
    (the order's live time), `full_allowance`), every one of which must be zero (13.1; a nonzero count is an engine
    error): positions open at once across the firm's accounts (D-429, one position at a time); an entry live inside
    a verified window at an account a rule reaches; a position there held through a window's start; a trade at the
    full allowance into a window (maximum size into major news)."""
    out = {"overlapping_positions": 0, "entry_inside_window": 0, "held_through_window_start": 0,
           "full_size_into_news": 0}
    ts = sorted(trades, key=lambda x: x["entry"])
    for a, b in zip(ts, ts[1:]):
        if b["entry"] < a["exit"]:
            out["overlapping_positions"] += 1
    for t in trades:
        if int(t["account"]) not in reached:
            continue
        if any(w.contains(t["live"]) for w in windows):
            out["entry_inside_window"] += 1
        if any(t["entry"] < w.start < t["exit"] for w in windows):
            out["held_through_window_start"] += 1
        if t.get("full_allowance") and any(t["entry"] <= w.end and t["exit"] >= w.start for w in windows):
            out["full_size_into_news"] += 1
    return out
