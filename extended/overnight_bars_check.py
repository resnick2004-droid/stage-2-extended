"""Q-154 (H2 of the restart plan, E-208): the data-integrity check of NQ's **overnight** 1-minute bars -- the bars
stamped 17:00 CT (the evening reopen) to 08:29 CT the next morning, slots 0..929 of the trading-day clock -- before any
overnight trigger enters a search.

    python scripts/h2_overnight_bars.py --json <out.json> --flags <out.csv> --report docs/audits/H2_...md

**The clock is the library's.** A trading day opens at 17:00 CT the evening before (the bar's Chicago time plus seven
hours, its date: `vendor/stage2/data/README.md` section 5, `extended.features.grid`); a slot is minutes after that
17:00 (`slot(8, 30)` = 930); a bar is stamped by its OPEN minute. The overnight is slots 0..929 -- what
`extended.features.compute_overnight` reads at its alerts 17:00..08:25 (bars stamped <= alert - 1) and what RL3's `on`
level reads (`extended/triggers.py` on wt/wt-levels: bars stamped 17:00..08:29, its reference the bar stamped 08:29).
The firm's day (`extended.lever_space.trading_day`) reopens at 17:00 CT; the store's session closes at 16:00 CT, so
slots 1380..1439 (16:00-16:59 CT) are the daily halt and must hold no bar.

**What it reads.** The search years (the choice block, 2020-01-02 to 2023-12-29) through `extended.reader.read_bars`,
one calendar year at a time; never a day after 2026-07-16 (`LAST_DEV_DAY`; `assert_loaded` refuses a frame whose last
bar starts at or after 16:00 CT of that day). The held-out years (2024-01-02 to 2026-07-16) are sealed by the reader
(CHARTER 3.6-3.7, Q-158: a judged read needs a pinned declaration naming its purpose, inside a clean run, once), so
their section is built from the bar store's **manifest** only -- metadata, no bar file read, as Q-40's calendar does
(`extended/calendar_early_closes.py`) -- and every bar-level check of them is reported as not run.

**The void rules, fixed in this file before any bar was read** (`classify`): a day is VOID for an overnight source --
its overnight is not the market's, or its bars are malformed -- when

* `late_reopen`: its first bar starts after 17:05 CT (`REOPEN_TOL` minutes after the reopen);
* `long_gap`: a run of at least `VOID_GAP` (15) consecutive minutes without a bar between its first bar and the last
  overnight minute the calendar schedules (08:29, or a minute before an abbreviated session's close);
* `outside_hours`: a bar stamped 16:00-16:59 CT, or a trading day dated a Saturday or Sunday;
* `duplicate`: two bars with one timestamp, or two in one (trading day, slot);
* `clock_break`: two consecutive bars of the day whose UTC gap differs from their CT slot gap, or overnight bars under
  two UTC offsets (a daylight-saving change inside a session);
* `malformed`: an overnight bar off the 0.25 tick, with a non-positive price, a high below its open or close, a low
  above them, or a negative volume;
* `day_label`: the store's `day` disagreeing with the clock's rule;
* `two_contracts`: two contracts in one trading day;
* `purchase_seam`, `manifest_defect`: a day the manifest or Q-40's calendar names as a data-defect candidate.

A day is SPECIAL (kept, but a source must know) for: `sunday_open`, `after_closure` (the evening after a full closure),
`after_abbreviated` (after a 12:00 / 12:15 CT halt), `abbreviated_day`, `scheduled_short_overnight` (a close before
08:30 CT: Good Friday with the jobs report), `roll` (cross-day levels void), `us_dst_session` (the first session after a
US change), `london_shift` (08:00 London is not 02:00 CT), `bls_0730` (the 08:30 ET release inside the overnight),
`degraded_utc` (Databento's condition `degraded` on a UTC date the overnight spans), `gap_5_14` (a 5-14 minute gap after
the reopen: below the void line, inside a plausible trade), `no_0829_bar` (RL3 voids it itself: `no_ref_bar`).

Nothing here prints or returns a price: the outputs are counts, shares, clock labels and dates. Nothing draws randomness.
"""
from __future__ import annotations

import csv
import io
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

CHICAGO = ZoneInfo("America/Chicago")
LONDON = ZoneInfo("Europe/London")
TOKYO = ZoneInfo("Asia/Tokyo")
UTC = timezone.utc

N_SLOTS = 1440
REOPEN_CT = 17 * 60
ON_N = 930                      # slots 0..929: bars stamped 17:00 .. 08:29 CT
ON_LAST = ON_N - 1
HALT_FIRST = 1380               # 16:00 CT: slots 1380..1439 are the daily halt
TICK = 0.25
TICK_TOL = 1e-6

#: the void and special-flag thresholds (fixed before any bar was read)
REOPEN_TOL = 5
VOID_GAP = 15
SPECIAL_GAP = 5
GAP_BINS: tuple[tuple[int, int | None], ...] = ((1, 1), (2, 4), (5, 14), (15, 29), (30, None))
LOW_VOLUME = 5                  # a "thin" bar: volume at most this many contracts
DST_NEAR_DAYS = 7               # a BLS day within this many calendar days after a US change (config/dst_check.yaml)

SEARCH = (date(2020, 1, 2), date(2023, 12, 29))
HELD_OUT = (date(2024, 1, 2), date(2026, 7, 16))
LAST_DEV_DAY = date(2026, 7, 16)
CONFIRMATION_START = date(2026, 7, 17)

VOID_RULES = ("late_reopen", "long_gap", "outside_hours", "duplicate", "clock_break", "malformed", "day_label",
              "two_contracts", "purchase_seam", "manifest_defect")
SPECIAL_FLAGS = ("sunday_open", "after_closure", "after_abbreviated", "abbreviated_day", "scheduled_short_overnight",
                 "roll", "us_dst_session", "london_shift", "bls_0730", "degraded_utc", "gap_5_14", "no_0829_bar")


def slot(hour: int, minute: int) -> int:
    """CT wall-clock hh:mm on the trading-day clock (minutes after 17:00 CT)."""
    return (hour * 60 + minute - REOPEN_CT) % N_SLOTS


def label(s: int) -> str:
    m = (int(s) + REOPEN_CT) % N_SLOTS
    return f"{m // 60:02d}:{m % 60:02d}"


BLS_SLOT = slot(7, 30)          # 870: the 08:30 ET release is the bar stamped 07:30 CT
BLS_WINDOW = (slot(6, 0), ON_LAST)
BLS_WINDOW_EARLY = (slot(6, 0), slot(7, 59))      # a second reading, ending before the 08:00 pre-open hour
ON_ALERT_MARKS = tuple(range(0, ON_N, 5))


def last_dev_ts() -> int:
    """Epoch seconds of 16:00 CT on 2026-07-16: every loaded bar must start before it."""
    return int(datetime(2026, 7, 16, 16, 0, tzinfo=CHICAGO).timestamp())


def assert_loaded(ts: np.ndarray, days: Iterable[str], end: date) -> None:
    """Refuse a frame holding a bar from the confirmation window, or a day past the block's end."""
    ts = np.asarray(ts, dtype=np.int64)
    if len(ts) and int(ts.max()) >= last_dev_ts():
        raise RuntimeError("REFUSED: a loaded bar starts at or after 16:00 CT on 2026-07-16 (the confirmation window "
                           "opens with trading day 2026-07-17); stop reading")
    mx = max((date.fromisoformat(str(d)) for d in days), default=None)
    if mx is not None and (mx > end or mx >= CONFIRMATION_START):
        raise RuntimeError(f"REFUSED: a loaded trading day ({mx}) lies after the block's end {end}")


# ------------------------------------------------------------------------------------------------------------ the clock


def clock(ts: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(trading day as datetime64[D], slot, UTC offset in minutes) of each bar start (epoch seconds UTC)."""
    ts = np.asarray(ts, dtype=np.int64)
    t = pd.to_datetime(ts, unit="s", utc=True).tz_convert(CHICAGO)
    local = t.tz_localize(None)
    utcn = pd.to_datetime(ts, unit="s")
    off = ((local - utcn) // pd.Timedelta(minutes=1)).to_numpy(np.int64)
    shifted = local + pd.Timedelta(hours=7)
    day = shifted.normalize().to_numpy().astype("datetime64[D]")
    sl = (shifted.hour * 60 + shifted.minute).to_numpy(np.int64)
    return day, sl, off


def missing_runs(present: np.ndarray) -> np.ndarray:
    """(start, length) of every run of False in a boolean vector, as an (k, 2) int array."""
    p = np.asarray(present, dtype=bool)
    if p.size == 0:
        return np.zeros((0, 2), dtype=np.int64)
    miss = np.concatenate([[False], ~p, [False]]).astype(np.int8)
    d = np.diff(miss)
    starts = np.flatnonzero(d == 1)
    ends = np.flatnonzero(d == -1)
    return np.stack([starts, ends - starts], axis=1).astype(np.int64)


def gap_bin(length: int) -> str:
    for lo, hi in GAP_BINS:
        if length >= lo and (hi is None or length <= hi):
            return f"{lo}-{hi}" if hi is not None and hi != lo else (f"{lo}" if hi == lo else f">={lo}")
    return "0"


def us_dst_changes(years: Iterable[int]) -> list[date]:
    """The local dates on which America/Chicago's UTC offset changes (from zoneinfo, never typed)."""
    out = []
    for y in years:
        d = date(y, 1, 1)
        prev = datetime(y - 1, 12, 31, 12, tzinfo=CHICAGO).utcoffset()
        while d.year == y:
            cur = datetime(d.year, d.month, d.day, 12, tzinfo=CHICAGO).utcoffset()
            if cur != prev:
                out.append(d)
            prev = cur
            d += timedelta(days=1)
    return out


def first_session_after(change: date, days: Sequence[date]) -> date | None:
    """The first stored trading day whose session opens after a change dated `change` (its 17:00 CT open is on or
    after the change's local date)."""
    for d in days:
        if d > change:
            return d
    return None


def london_open_ct(d: date) -> str:
    """Chicago wall-clock time of 08:00 London on the calendar date `d` (the London open inside trading day d)."""
    t = datetime(d.year, d.month, d.day, 8, 0, tzinfo=LONDON).astimezone(CHICAGO)
    return f"{t.hour:02d}:{t.minute:02d}"


def tokyo_open_ct(d: date) -> str:
    """Chicago wall-clock time of 09:00 Tokyo on the calendar date `d` (the evening before trading day d in CT)."""
    t = datetime(d.year, d.month, d.day, 9, 0, tzinfo=TOKYO).astimezone(CHICAGO)
    return f"{t.hour:02d}:{t.minute:02d}"


# ------------------------------------------------------------------------------------------------------- the calendar


@dataclass
class Context:
    """One trading day's calendar context for its overnight."""
    weekday: int
    sunday_open: bool
    after_closure: bool
    after_abbreviated: bool
    abbreviated_day: bool
    close_slot: int | None            # the scheduled close as a slot, when the calendar gives one
    defect: str                       # the calendar's data_defect_candidate text, else ""

    @property
    def on_end(self) -> int:
        """The last overnight slot the calendar schedules (08:29, or a minute before an earlier close)."""
        if self.close_slot is not None and self.close_slot <= ON_LAST:
            return self.close_slot - 1
        return ON_LAST


def _close_slot(text: str) -> int | None:
    if not text:
        return None
    h, m = text.split(":")
    return slot(int(h), int(m))


def contexts(days: Sequence[date], calendar: Sequence[Mapping[str, str]]) -> dict[date, Context]:
    """Each stored trading day's context: the evening it opens (after a weekend, a full closure or an abbreviated
    session) and its own scheduled close, from the fixed calendar (`config/calendar_early_closes.csv`)."""
    by = {date.fromisoformat(r["date"]): r for r in calendar}
    out: dict[date, Context] = {}
    prev: date | None = None
    for d in days:
        r = by.get(d)
        abbreviated = bool(r and r["kind"] in ("holiday", "early_close") and r.get("close_ct"))
        close = _close_slot(r["close_ct"]) if abbreviated else None
        defect = r["source"] if (r and r["kind"] == "data_defect_candidate") else ""
        sunday = d.weekday() == 0
        closure = False
        after_abbr = False
        if prev is not None:
            k = prev + timedelta(days=1)
            while k < d:                                  # a weekday between the two stored days, closed
                if k.weekday() < 5:
                    closure = True
                k += timedelta(days=1)
            pr = by.get(prev)
            after_abbr = bool(pr and pr["kind"] in ("holiday", "early_close") and pr.get("close_ct"))
        out[d] = Context(d.weekday(), sunday, closure, after_abbr, abbreviated, close, defect)
        prev = d
    return out


# ------------------------------------------------------------------------------------------------- one chunk's days


@dataclass
class DayRecord:
    """One trading day's overnight, counts and clock labels only (never a price)."""
    day: date
    first_slot: int
    last_on_slot: int                 # -1 when no overnight bar
    n_on: int
    n_halt: int
    dup_ts: int
    dup_slot: int
    contracts: int
    contract: str
    clock_breaks: int
    offsets_on: int                   # distinct UTC offsets among the overnight bars
    first_offset: int                 # the first bar's UTC offset, minutes
    malformed: int
    zero_vol: int
    day_label_bad: int
    runs: list[tuple[int, int]]       # missing runs within [first_slot, on_end] (start slot, length)
    lead_missing: int                 # slots 0 .. first_slot - 1
    bls_argmax: int                   # the overnight slot 06:00..08:29 with the most volume (-1 if none)
    bls_argmax_early: int             # the same over 06:00..07:59
    halt_slots: list[int]             # slots of bars stamped 16:00-16:59 CT
    reopen_jump_ticks: float          # |first open - previous stored day's last close| in ticks (internal only)
    same_contract_prev: bool
    present_on: np.ndarray = field(repr=False, default_factory=lambda: np.zeros(ON_N, dtype=bool))


@dataclass
class HourAgg:
    present: np.ndarray = field(default_factory=lambda: np.zeros(16, dtype=np.int64))
    flat: np.ndarray = field(default_factory=lambda: np.zeros(16, dtype=np.int64))
    thin: np.ndarray = field(default_factory=lambda: np.zeros(16, dtype=np.int64))
    zero: np.ndarray = field(default_factory=lambda: np.zeros(16, dtype=np.int64))
    slots: np.ndarray = field(default_factory=lambda: np.zeros(16, dtype=np.int64))   # day-slots scheduled


def hour_of(s: np.ndarray) -> np.ndarray:
    """Overnight hour index: 0 = the 17:00 hour .. 15 = the 08:00 hour (08:00-08:29 only)."""
    return np.asarray(s) // 60


def day_records(df: pd.DataFrame, ctx: Mapping[date, Context], hours: HourAgg,
                prev_close: tuple[float, str] | None = None) -> tuple[list[DayRecord], tuple[float, str] | None]:
    """The per-day records of one frame of bars (ts sorted by the reader), and the carry (the last day's last close and
    contract) for the next frame. `hours` accumulates the overnight's per-hour presence, flat, thin and zero counts."""
    df = df.sort_values("ts", kind="stable").reset_index(drop=True)
    ts = df["ts"].to_numpy(np.int64)
    dkey, sl, off = clock(ts)
    uniq, di = np.unique(dkey, return_inverse=True)
    n = len(uniq)
    o, h, lo, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    v = df["volume"].to_numpy(float)
    given = df["day"].astype(str).to_numpy() if "day" in df.columns else None
    label_bad = (given != np.datetime_as_string(dkey, unit="D")) if given is not None else np.zeros(len(ts), bool)

    counts = np.zeros((n, N_SLOTS), dtype=np.int32)
    np.add.at(counts, (di, sl), 1)
    present = counts > 0
    dup_ts_mask = np.zeros(len(ts), bool)
    dup_ts_mask[1:] = ts[1:] == ts[:-1]

    pr = np.stack([o, h, lo, c])
    offtick = (np.abs(pr / TICK - np.round(pr / TICK)) > TICK_TOL).any(axis=0)
    bad = offtick | (pr <= 0).any(axis=0) | (h < np.fmax(o, c)) | (lo > np.fmin(o, c)) | (h < lo) | (v < 0)
    bad |= ~np.isfinite(pr).all(axis=0)
    flat = (o == h) & (h == lo) & (lo == c)
    on = sl <= ON_LAST

    same = np.zeros(len(ts), bool)
    same[1:] = di[1:] == di[:-1]
    dts = np.zeros(len(ts), np.int64)
    dts[1:] = (ts[1:] - ts[:-1]) // 60
    dsl = np.zeros(len(ts), np.int64)
    dsl[1:] = sl[1:] - sl[:-1]
    brk = same & (dts != dsl)

    def per_day(mask: np.ndarray) -> np.ndarray:
        return np.bincount(di[mask], minlength=n)

    n_bad, n_zero, n_brk, n_dup, n_lab = (per_day(on & bad), per_day(on & (v == 0)), per_day(brk),
                                          per_day(dup_ts_mask), per_day(label_bad))
    codes, labels = pd.factorize(df["contract"].astype(str), sort=False)
    contracts = pd.Series(codes).groupby(di).nunique().reindex(range(n), fill_value=0).to_numpy()
    first_idx = np.searchsorted(di, np.arange(n))
    last_idx = np.searchsorted(di, np.arange(n), side="right") - 1

    # per-hour aggregates of the overnight's bars
    hb = hour_of(sl[on])
    hours.present += np.bincount(hb, minlength=16)
    hours.flat += np.bincount(hb[flat[on]], minlength=16)
    hours.thin += np.bincount(hb[(v[on] <= LOW_VOLUME)], minlength=16)
    hours.zero += np.bincount(hb[(v[on] == 0)], minlength=16)

    vol = np.full((n, N_SLOTS), -1.0)
    vol[di, sl] = v                                   # a duplicated slot keeps the later bar here (counted apart)

    recs: list[DayRecord] = []
    carry = prev_close
    for i in range(n):
        d = pd.Timestamp(uniq[i]).date()
        cx = ctx.get(d)
        on_end = cx.on_end if cx is not None else ON_LAST
        pres = present[i]
        any_bar = np.flatnonzero(pres)
        first = int(any_bar[0]) if len(any_bar) else -1
        on_bars = np.flatnonzero(pres[:ON_N])
        last_on = int(on_bars[-1]) if len(on_bars) else -1
        sched = np.zeros(ON_N, dtype=np.int64)
        sched[: on_end + 1] = 1
        hours.slots += np.bincount(hour_of(np.flatnonzero(sched)), minlength=16)
        if 0 <= first <= on_end:
            seg = pres[first:on_end + 1]
            runs = [(int(a) + first, int(b)) for a, b in missing_runs(seg)]
            lead = first
        else:
            runs = []
            lead = on_end + 1
        win = vol[i, BLS_WINDOW[0]:BLS_WINDOW[1] + 1]
        bls_arg = int(np.argmax(win)) + BLS_WINDOW[0] if (win >= 0).any() else -1
        win2 = vol[i, BLS_WINDOW_EARLY[0]:BLS_WINDOW_EARLY[1] + 1]
        bls_arg2 = int(np.argmax(win2)) + BLS_WINDOW_EARLY[0] if (win2 >= 0).any() else -1
        fi, li = first_idx[i], last_idx[i]
        con = str(labels[codes[fi]])
        jump, same_prev = float("nan"), False
        if carry is not None:
            jump = abs(o[fi] - carry[0]) / TICK
            same_prev = carry[1] == con
        offs = np.unique(off[fi:li + 1][sl[fi:li + 1] <= ON_LAST])
        recs.append(DayRecord(
            day=d, first_slot=first, last_on_slot=last_on, n_on=int(len(on_bars)),
            n_halt=int(pres[HALT_FIRST:].sum()), dup_ts=int(n_dup[i]), dup_slot=int((counts[i] > 1).sum()),
            contracts=int(contracts[i]), contract=con, clock_breaks=int(n_brk[i]), offsets_on=int(len(offs)),
            first_offset=int(off[fi]), malformed=int(n_bad[i]), zero_vol=int(n_zero[i]), day_label_bad=int(n_lab[i]),
            runs=runs, lead_missing=int(lead), bls_argmax=bls_arg, bls_argmax_early=bls_arg2,
            halt_slots=[int(x) + HALT_FIRST for x in np.flatnonzero(pres[HALT_FIRST:])], reopen_jump_ticks=jump,
            same_contract_prev=same_prev, present_on=pres[:ON_N].copy()))
        carry = (float(c[li]), con)
    return recs, carry


# ------------------------------------------------------------------------------------------------------ classification


def classify(r: DayRecord, cx: Context | None, *, roll: bool, dst_session: bool, bls: bool,
             degraded: bool, seam: bool) -> tuple[list[str], list[str]]:
    """(void reasons, special flags) of one day, by the module docstring's rules."""
    void: list[str] = []
    special: list[str] = []
    on_end = cx.on_end if cx is not None else ON_LAST
    if r.first_slot < 0 or r.first_slot > REOPEN_TOL:
        void.append("late_reopen")
    if any(length >= VOID_GAP for _, length in r.runs):
        void.append("long_gap")
    if r.n_halt > 0 or r.day.weekday() >= 5:
        void.append("outside_hours")
    if r.dup_ts > 0 or r.dup_slot > 0:
        void.append("duplicate")
    if r.clock_breaks > 0 or r.offsets_on > 1:
        void.append("clock_break")
    if r.malformed > 0:
        void.append("malformed")
    if r.day_label_bad > 0:
        void.append("day_label")
    if r.contracts > 1:
        void.append("two_contracts")
    if seam:
        void.append("purchase_seam")
    if cx is not None and cx.defect and not seam:
        void.append("manifest_defect")
    if cx is not None:
        if cx.sunday_open:
            special.append("sunday_open")
        if cx.after_closure:
            special.append("after_closure")
        if cx.after_abbreviated:
            special.append("after_abbreviated")
        if cx.abbreviated_day:
            special.append("abbreviated_day")
        if on_end < ON_LAST:
            special.append("scheduled_short_overnight")
    if roll:
        special.append("roll")
    if dst_session:
        special.append("us_dst_session")
    if london_open_ct(r.day) != "02:00":
        special.append("london_shift")
    if bls:
        special.append("bls_0730")
    if degraded:
        special.append("degraded_utc")
    if any(SPECIAL_GAP <= length < VOID_GAP for _, length in r.runs):
        special.append("gap_5_14")
    if not r.present_on[ON_LAST] and on_end == ON_LAST:
        special.append("no_0829_bar")
    return void, special


def overnight_utc_dates(d: date) -> tuple[date, date]:
    """The UTC dates an overnight of trading day d spans (17:00 CT of d - 1 to 08:29 CT of d)."""
    a = datetime(d.year, d.month, d.day, 17, 0, tzinfo=CHICAGO) - timedelta(days=1)
    b = datetime(d.year, d.month, d.day, 8, 29, tzinfo=CHICAGO)
    return a.astimezone(UTC).date(), b.astimezone(UTC).date()


def degraded_days(days: Sequence[date], not_available: Mapping[str, str]) -> set[date]:
    """Trading days whose overnight spans a UTC date Databento marks other than `available`."""
    bad = {date.fromisoformat(k) for k in not_available}
    out = set()
    for d in days:
        a, b = overnight_utc_dates(d)
        if a in bad or b in bad:
            out.add(d)
    return out


# ------------------------------------------------------------------------------------------------------- aggregation


def _share(a: float, b: float) -> float | None:
    return None if not b else float(a) / float(b)


def _stretches(days: Sequence[date]) -> list[tuple[str, str, int]]:
    """Consecutive runs of stored days (each a run of the input order) as (first, last, count)."""
    out: list[list[Any]] = []
    for d in days:
        if out and (d - out[-1][1]).days <= 4:
            out[-1][1] = d
            out[-1][2] += 1
        else:
            out.append([d, d, 1])
    return [(a.isoformat(), b.isoformat(), k) for a, b, k in out]


def _month_missing(recs: Sequence[DayRecord]) -> Counter:
    out: Counter = Counter()
    for r in recs:
        out[r.day.strftime("%Y-%m")] += sum(x for _, x in r.runs)
    return out


def _outside_top_month(recs: Sequence[DayRecord]) -> tuple[str, str, int] | None:
    """(the month with the most missing minutes, the day with the most outside it, its minutes)."""
    mm = _month_missing(recs)
    if not mm or not recs:
        return None
    top = max(mm.items(), key=lambda kv: (kv[1], kv[0]))[0]
    rest = [(sum(x for _, x in r.runs), r.day.isoformat()) for r in recs if r.day.strftime("%Y-%m") != top]
    if not rest:
        return None
    m_, d_ = max(rest, key=lambda z: (z[0], z[1]))
    return top, d_, m_


def aggregate(recs: Sequence[DayRecord], ctx: Mapping[date, Context], *, block: tuple[date, date],
              rolls: Iterable[str], dst_changes: Sequence[date], bls_days: Iterable[date],
              not_available: Mapping[str, str], seams: Iterable[str], bounds: Mapping[str, Sequence[str]],
              hours: HourAgg, bls_major_days: Iterable[date] = ()) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """The block's summary (counts, shares, clock labels, dates) and its per-day flag rows."""
    recs = sorted(recs, key=lambda r: r.day)
    days = [r.day for r in recs]
    rollset = {date.fromisoformat(x) for x in rolls}
    seamset = {date.fromisoformat(x) for x in seams}
    blsset = set(bls_days)
    deg = degraded_days(days, not_available)
    dst_sessions = {}
    for ch in dst_changes:
        f = first_session_after(ch, days)
        if f is not None and block[0] <= f <= block[1] and (f - ch).days <= 4:
            dst_sessions[f] = ch
    n = len(recs)
    rows: list[dict[str, Any]] = []
    void_days: dict[str, list[str]] = {}
    void_count: Counter = Counter()
    special_count: Counter = Counter()
    special_days: dict[str, list[str]] = defaultdict(list)
    gap_bins: Counter = Counter()
    gap_bin_days: Counter = Counter()
    gap_hours = np.zeros(16, dtype=np.int64)          # gaps of >= 2 minutes by the hour they start in
    long_gaps: list[tuple[str, str, int]] = []
    missing_after_reopen = 0
    scheduled = 0
    reopen = Counter()
    for r in recs:
        cx = ctx.get(r.day)
        v, s = classify(r, cx, roll=r.day in rollset, dst_session=r.day in dst_sessions, bls=r.day in blsset,
                        degraded=r.day in deg, seam=r.day in seamset)
        for x in v:
            void_count[x] += 1
        for x in s:
            special_count[x] += 1
            special_days[x].append(r.day.isoformat())
        if v:
            void_days[r.day.isoformat()] = v
        reopen[label(r.first_slot) if r.first_slot >= 0 else "none"] += 1
        on_end = cx.on_end if cx is not None else ON_LAST
        scheduled += on_end + 1
        seen_bins = set()
        for st, length in r.runs:
            b = gap_bin(length)
            gap_bins[b] += 1
            seen_bins.add(b)
            missing_after_reopen += length
            if length >= 2:
                gap_hours[st // 60] += 1
            if length >= VOID_GAP:
                long_gaps.append((r.day.isoformat(), label(st), length))
        for b in seen_bins:
            gap_bin_days[b] += 1
        longest = max((length for _, length in r.runs), default=0)
        rows.append({
            "day": r.day.isoformat(), "weekday": r.day.strftime("%a"), "reopen_ct": label(r.first_slot)
            if r.first_slot >= 0 else "", "last_overnight_bar_ct": label(r.last_on_slot) if r.last_on_slot >= 0
            else "", "overnight_bars": r.n_on, "scheduled_overnight_minutes": on_end + 1,
            "missing_after_reopen": sum(length for _, length in r.runs), "longest_gap_min": longest,
            "gaps_ge5": sum(1 for _, length in r.runs if length >= SPECIAL_GAP),
            "gaps_ge15": sum(1 for _, length in r.runs if length >= VOID_GAP),
            "verdict": "VOID" if v else ("SPECIAL" if s else "OK"), "void": ";".join(v), "special": ";".join(s)})

    # presence at every slot an overnight source reads
    P = np.stack([r.present_on for r in recs]) if recs else np.zeros((0, ON_N), bool)
    slot_share = P.mean(axis=0) if n else np.zeros(ON_N)
    marks = [m for m in ON_ALERT_MARKS if m >= 1]
    prior_bar = {m: float(slot_share[m - 1]) for m in marks}
    any5 = {m: float(P[:, max(0, m - 5):m].any(axis=1).mean()) for m in marks} if n else {}
    c_def = {m: float(P[:, :m].any(axis=1).mean()) for m in marks} if n else {}
    lowest = sorted(prior_bar.items(), key=lambda kv: (kv[1], kv[0]))[:6]
    hour_share = [float(slot_share[h * 60:min(ON_N, (h + 1) * 60)].mean()) for h in range(16)]

    # the reopen jump on roll evenings against the other evenings (counts only)
    nonroll = np.array([r.reopen_jump_ticks for r in recs if r.day not in rollset and r.same_contract_prev
                        and np.isfinite(r.reopen_jump_ticks)])
    thr = float(np.quantile(nonroll, 0.995)) if len(nonroll) else float("nan")
    roll_recs = [r for r in recs if r.day in rollset]
    roll_jump_over = sum(1 for r in roll_recs if np.isfinite(r.reopen_jump_ticks) and r.reopen_jump_ticks > thr)
    roll_by_bars = sorted(r.day.isoformat() for r in recs if not r.same_contract_prev and np.isfinite(
        r.reopen_jump_ticks))
    roll_manifest = sorted(d.isoformat() for d in rollset if block[0] <= d <= block[1])
    roll_missing = [sum(length for _, length in r.runs) for r in roll_recs]
    other_missing = [sum(length for _, length in r.runs) for r in recs if r.day not in rollset]

    # the BLS clock check: the overnight minute 06:00..08:29 with the most volume on a release day
    def near(d: date) -> bool:
        return any(0 <= (d - ch).days <= DST_NEAR_DAYS for ch in dst_changes)

    bls_recs = [r for r in recs if r.day in blsset and r.bls_argmax >= 0]
    majset = set(bls_major_days)
    maj_recs = [r for r in bls_recs if r.day in majset]
    ctl_recs = [r for r in recs if r.day not in blsset and r.bls_argmax >= 0 and r.day.weekday() < 5]

    def clock_hits(rs: Sequence[DayRecord], early: bool = False) -> dict[str, Any]:
        k = len(rs)
        arg = (lambda r: r.bls_argmax_early) if early else (lambda r: r.bls_argmax)  # noqa: E731
        at = sum(1 for r in rs if arg(r) == BLS_SLOT)
        pm1 = sum(1 for r in rs if abs(arg(r) - BLS_SLOT) <= 1)
        hour_off = sum(1 for r in rs if abs(abs(arg(r) - BLS_SLOT) - 60) <= 1)
        miss = sorted(r.day.isoformat() for r in rs if abs(arg(r) - BLS_SLOT) > 1)
        where = Counter(label(arg(r)) for r in rs if abs(arg(r) - BLS_SLOT) > 1)
        return {"days": k, "at_0730": at, "share_at_0730": _share(at, k), "within_1min": pm1,
                "share_within_1min": _share(pm1, k), "an_hour_off": hour_off, "elsewhere_days": miss,
                "elsewhere_at": dict(where.most_common(8))}

    # DST sessions in detail
    dst_rows = []
    for ch in dst_changes:
        if not (block[0] - timedelta(days=7) <= ch <= block[1]):
            continue
        after = first_session_after(ch, days)
        before = max((d for d in days if d <= ch), default=None)
        row = {"change": ch.isoformat()}
        for tag, d in (("before", before), ("after", after)):
            r = next((x for x in recs if x.day == d), None)
            if r is None:
                row[tag] = None
                continue
            row[tag] = {"day": d.isoformat(), "reopen_ct": label(r.first_slot), "utc_offset_h": r.first_offset / 60,
                        "clock_breaks": r.clock_breaks, "offsets_in_overnight": r.offsets_on,
                        "missing_after_reopen": sum(length for _, length in r.runs),
                        "dup_slots": r.dup_slot}
        dst_rows.append(row)

    london = [d for d in days if london_open_ct(d) != "02:00"]
    tokyo = Counter(tokyo_open_ct(d) for d in days)

    # the manifest's day_bounds against the bars (so the held-out section's manifest reading can be trusted)
    agree = 0
    disagree = []
    for r in recs:
        b = bounds.get(r.day.isoformat())
        if b is not None and b[0] == label(r.first_slot):
            agree += 1
        else:
            disagree.append(r.day.isoformat())

    summary = {
        "block": [block[0].isoformat(), block[1].isoformat()], "days": n,
        "first_day": days[0].isoformat() if days else None, "last_day": days[-1].isoformat() if days else None,
        "overnight_bars": int(sum(r.n_on for r in recs)), "overnight_slots_all": n * ON_N,
        "share_present_all": _share(sum(r.n_on for r in recs), n * ON_N),
        "scheduled_after_open": scheduled, "missing_after_reopen": missing_after_reopen,
        "share_missing_after_reopen": _share(missing_after_reopen, scheduled),
        "reopen": dict(sorted(reopen.items())),
        "gap_bins": {b: gap_bins.get(b, 0) for b in [gap_bin(lo) for lo, _ in GAP_BINS]},
        "gap_bin_days": {b: gap_bin_days.get(b, 0) for b in [gap_bin(lo) for lo, _ in GAP_BINS]},
        "gap_hours_ge2": {label(h * 60): int(gap_hours[h]) for h in range(16)},
        "long_gaps": long_gaps,
        "longest_gap": max(((r.day.isoformat(), label(st), length) for r in recs for st, length in r.runs),
                           key=lambda g: g[2], default=None),
        "dup_ts": int(sum(r.dup_ts for r in recs)), "dup_slot": int(sum(r.dup_slot for r in recs)),
        "day_label_bad": int(sum(r.day_label_bad for r in recs)), "halt_bars": int(sum(r.n_halt for r in recs)),
        "halt_bar_times": [(r.day.isoformat(), label(s_)) for r in recs for s_ in r.halt_slots],
        "missing_by_month": sorted(Counter({m_: v_ for m_, v_ in _month_missing(recs).items()}).items(),
                                   key=lambda kv: (-kv[1], kv[0]))[:4],
        "max_day_missing_outside_top_month": _outside_top_month(recs),
        "most_missing_days": [(r.day.isoformat(), m_, lg_) for r, m_, lg_ in sorted(
            ((r, sum(x for _, x in r.runs), max((x for _, x in r.runs), default=0)) for r in recs),
            key=lambda z: (-z[1], z[0].day))[:12]],
        "weekend_days": sum(1 for d in days if d.weekday() >= 5),
        "two_contract_days": sum(1 for r in recs if r.contracts > 1),
        "clock_breaks": int(sum(r.clock_breaks for r in recs)),
        "mixed_offset_days": sum(1 for r in recs if r.offsets_on > 1),
        "malformed_bars": int(sum(r.malformed for r in recs)),
        "zero_volume_bars": int(sum(r.zero_vol for r in recs)),
        "hours": {label(h * 60): {"share_present": _share(hours.present[h], hours.slots[h]),
                                  "share_flat": _share(hours.flat[h], hours.present[h]),
                                  "share_thin": _share(hours.thin[h], hours.present[h]),
                                  "zero_volume": int(hours.zero[h])} for h in range(16)},
        "presence": {"bar_0829": float(slot_share[ON_LAST]) if n else None,
                     "bar_1700": float(slot_share[0]) if n else None,
                     "any_overnight_bar": float(P.any(axis=1).mean()) if n else None,
                     "prior_bar_min": min(prior_bar.values()) if prior_bar else None,
                     "prior_bar_mean": float(np.mean(list(prior_bar.values()))) if prior_bar else None,
                     "prior_bar_lowest": [(label(m), v) for m, v in lowest],
                     "window5_min": min(any5.values()) if any5 else None,
                     "close_defined_min": min(c_def.values()) if c_def else None,
                     "close_defined_at_1705": c_def.get(5),
                     "hour_share": {label(h * 60): hour_share[h] for h in range(16)}},
        "roll": {"manifest_rolls": roll_manifest, "rolls_seen_in_bars": roll_by_bars,
                 "agree": roll_by_bars == [d for d in roll_manifest if d != (days[0].isoformat() if days else "")],
                 "roll_days": len(roll_recs), "reopen_jump_over_p995": roll_jump_over,
                 "mean_missing_roll": float(np.mean(roll_missing)) if roll_missing else None,
                 "mean_missing_other": float(np.mean(other_missing)) if other_missing else None},
        "bls_clock": {"release": clock_hits(bls_recs),
                      "release_near_dst": clock_hits([r for r in bls_recs if near(r.day)]),
                      "release_away": clock_hits([r for r in bls_recs if not near(r.day)]),
                      "control_non_release": {k: v for k, v in clock_hits(ctl_recs).items() if k != "elsewhere_days"},
                      "major": clock_hits(maj_recs),
                      "major_near_dst": clock_hits([r for r in maj_recs if near(r.day)]),
                      "major_away": clock_hits([r for r in maj_recs if not near(r.day)]),
                      "early_release": clock_hits(bls_recs, early=True),
                      "early_release_near_dst": clock_hits([r for r in bls_recs if near(r.day)], early=True),
                      "early_major": clock_hits(maj_recs, early=True),
                      "early_control": {k: v for k, v in clock_hits(ctl_recs, early=True).items()
                                        if k != "elsewhere_days"}},
        "dst": dst_rows,
        "london_shift_days": len(london), "london_shift_stretches": _stretches(london),
        "tokyo_open_ct": dict(sorted(tokyo.items())),
        "manifest_bounds_agree": agree, "manifest_bounds_disagree": disagree,
        "void_count": dict(sorted(void_count.items())), "void_days": void_days,
        "void_day_count": len(void_days),
        "special_count": dict(sorted(special_count.items())),
        "special_days": {k: v for k, v in special_days.items()
                         if k in ("after_closure", "after_abbreviated", "abbreviated_day", "scheduled_short_overnight",
                                  "roll", "us_dst_session", "degraded_utc", "gap_5_14", "no_0829_bar")},
    }
    return summary, rows


# ------------------------------------------------------------------------------------------ the held-out (manifest)


def manifest_block(manifest: Mapping[str, Any], ctx: Mapping[date, Context], *, block: tuple[date, date],
                   dst_changes: Sequence[date], bls_days: Iterable[date],
                   not_available: Mapping[str, str] | None = None) -> dict[str, Any]:
    """What the manifest (metadata, no bar) shows of a block: each day's first bar (the reopen), the store's short,
    late-start and early-end days, the rolls, Databento's non-available dates, the calendar's contexts."""
    days = [date.fromisoformat(d) for d in manifest["day_list"] if block[0] <= date.fromisoformat(d) <= block[1]]
    if any(d >= CONFIRMATION_START for d in days):
        raise RuntimeError("REFUSED: the manifest lists a day in the confirmation window inside the block")
    bounds = manifest["day_bounds"]
    reopen = Counter(bounds[d.isoformat()][0] for d in days)
    late = [d.isoformat() for d in days if bounds[d.isoformat()][0] not in ("17:00", "17:01", "17:02", "17:03",
                                                                             "17:04", "17:05")]
    inblk = lambda xs: sorted(x for x in xs if block[0] <= date.fromisoformat(x) <= block[1])  # noqa: E731
    na: dict[str, str] = dict(not_available or {})
    for imp in manifest.get("imports", []):
        na.update(((imp.get("condition") or {}).get("not_available")) or {})
    deg = sorted(d.isoformat() for d in degraded_days(days, na))
    short = {}
    for k, nb in manifest.get("short_days", {}).items():
        d = date.fromisoformat(k)
        if not (block[0] <= d <= block[1]):
            continue
        cx = ctx.get(d)
        close = cx.close_slot if (cx is not None and cx.close_slot is not None) else HALT_FIRST
        short[k] = {"bars": nb, "scheduled_minutes": close, "deficit": close - nb,
                    "bounds": list(bounds.get(k, [])), "degraded": d.isoformat() in deg}
    blsset = set(bls_days)
    dst_sessions = []
    for ch in dst_changes:
        f = first_session_after(ch, days)
        if f is not None and block[0] <= f <= block[1] and (f - ch).days <= 4:
            dst_sessions.append((ch.isoformat(), f.isoformat(), bounds[f.isoformat()][0]))
    defects = sorted(d.isoformat() for d in days if ctx.get(d) is not None and ctx[d].defect)
    return {
        "block": [block[0].isoformat(), block[1].isoformat()], "days": len(days),
        "first_day": days[0].isoformat() if days else None, "last_day": days[-1].isoformat() if days else None,
        "reopen": dict(sorted(reopen.items())), "late_reopen_days": late,
        "short_days": {k: v for k, v in manifest.get("short_days", {}).items() if k in inblk(manifest.get(
            "short_days", {}))},
        "short_day_deficits": short,
        "late_start_days": inblk(manifest.get("late_start_days", [])),
        "early_end_days": inblk(manifest.get("early_end_days", [])),
        "rolls": inblk(manifest.get("rolls", [])), "degraded_overnights": deg,
        "calendar_defects": defects,
        "sunday_open": sum(1 for d in days if ctx[d].sunday_open),
        "after_closure": sorted(d.isoformat() for d in days if ctx[d].after_closure),
        "after_abbreviated": sorted(d.isoformat() for d in days if ctx[d].after_abbreviated),
        "abbreviated_day": sorted(d.isoformat() for d in days if ctx[d].abbreviated_day),
        "scheduled_short_overnight": sorted(d.isoformat() for d in days if ctx[d].on_end < ON_LAST),
        "dst_sessions": dst_sessions,
        "london_shift_days": sum(1 for d in days if london_open_ct(d) != "02:00"),
        "london_shift_stretches": _stretches([d for d in days if london_open_ct(d) != "02:00"]),
        "tokyo_open_ct": dict(sorted(Counter(tokyo_open_ct(d) for d in days).items())),
        "bls_days": sum(1 for d in days if d in blsset),
    }


# ----------------------------------------------------------------------------------------------------------- power


def power(manifest: Mapping[str, Any], sample_size_rows: Sequence[Mapping[str, str]], k: int = 13,
          block_len: int = 63) -> dict[str, Any]:
    """The sessions and 63-session blocks of each block, the family's level at k, the smallest p an exact sign-flip
    over B blocks can reach (2^-B), and the sample-size table's trades beside the sessions."""
    def count(b: tuple[date, date]) -> int:
        return sum(1 for d in manifest["day_list"] if b[0] <= date.fromisoformat(d) <= b[1])
    level = 0.05 / (k * (k + 1))
    out = {"k": k, "level": level, "block_len": block_len}
    for name, b in (("search", SEARCH), ("held_out", HELD_OUT)):
        n = count(b)
        B = n // block_len
        out[name] = {"sessions": n, "blocks": B, "min_signflip_p": 2.0 ** -B if B else None,
                     "signflip_can_reach_level": bool(B and 2.0 ** -B <= level)}
    need = 0
    while 2.0 ** -need > level:
        need += 1
    out["blocks_needed_for_signflip"] = need
    out["sample_size"] = [{"R": r["R"], "true_edge": r["true_edge"],
                           "trades_lb_above_half_edge": int(r["trades_lower_bound_above_half_edge"]),
                           "trades_lb_above_0": int(r["trades_lower_bound_above_0"])} for r in sample_size_rows]
    return out


# ------------------------------------------------------------------------------------------------------- the CSV


FLAG_COLUMNS = ("day", "weekday", "reopen_ct", "last_overnight_bar_ct", "overnight_bars",
                "scheduled_overnight_minutes", "missing_after_reopen", "longest_gap_min", "gaps_ge5", "gaps_ge15",
                "verdict", "void", "special")


def flags_csv(rows: Sequence[Mapping[str, Any]]) -> str:
    """The per-day flags as CSV text: counts, clock labels and flags, no price column."""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FLAG_COLUMNS, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: r[k] for k in FLAG_COLUMNS})
    return buf.getvalue()


# ------------------------------------------------------------------------------------------------------- the report


def _pct(x: float | None, nd: int = 2) -> str:
    return "n/a" if x is None else f"{100.0 * x:.{nd}f} %"


def _num(x: float | None, fmt: str = ".2f") -> str:
    return "n/a" if x is None else format(x, fmt)


def _dates(xs: Sequence[str], cap: int = 40) -> str:
    xs = list(xs)
    if not xs:
        return "none"
    s = ", ".join(xs[:cap])
    return s + (f", ... ({len(xs)} in all)" if len(xs) > cap else "")


def verdict(search: Mapping[str, Any], held_out_bar_checked: bool,
            extra: Iterable[str] = ()) -> tuple[str, list[str]]:
    """BLOCKED unless both blocks were checked at bar level, no day is void and no other check failed (`extra`: the
    data hashes, the schema); the reasons, in words."""
    why = list(extra)
    if not held_out_bar_checked:
        why.append("the held-out years' overnight bars were not read (the reader's seal, Q-158): their gaps, "
                   "duplicates, clock continuity, bar validity and slot presence are unchecked")
    if search["void_day_count"]:
        why.append(f"{search['void_day_count']} search-year overnights are void by the rules fixed before the read; "
                   "no void calendar exists yet outside this report, so a source reading overnight bars cannot drop "
                   "them by a pinned file")
    return ("BLOCKED" if why else "VALIDATED"), why


def _block_section(a, blk: Mapping[str, Any], meta: Mapping[str, Any], title: str) -> None:
    a(f"## {title}")
    a("")
    a(f"{blk['days']} trading days, {blk['first_day']} to {blk['last_day']}; {blk['overnight_bars']} overnight "
      f"bars of {blk['overnight_slots_all']} day-minutes 17:00-08:29 ({_pct(blk['share_present_all'])} present).")
    a("")
    a("| check | result |")
    a("|---|---|")
    a(f"| schema, dtypes | {meta['schema']} |")
    a(f"| `day` against the clock's rule | {blk['day_label_bad']} bars disagree |")
    a(f"| duplicate timestamps / two bars in one (day, slot) | {blk['dup_ts']} / {blk['dup_slot']} |")
    a("| out-of-order timestamps | not checkable through the reader (it sorts by `ts`, stably); after the sort, "
      "duplicates as above |")
    a(f"| bars stamped 16:00-16:59 CT / trading days dated a weekend | {blk['halt_bars']} "
      f"({', '.join(f'{d} {x} CT' for d, x in blk['halt_bar_times']) or 'none'}) / {blk['weekend_days']} |")
    a(f"| days holding two contracts | {blk['two_contract_days']} |")
    a(f"| clock breaks (consecutive bars whose UTC gap differs from their CT slot gap) | {blk['clock_breaks']} |")
    a(f"| overnights under two UTC offsets | {blk['mixed_offset_days']} |")
    a(f"| malformed overnight bars (off tick, price <= 0, high/low not bracketing open and close, volume < 0) | "
      f"{blk['malformed_bars']} |")
    a(f"| zero-volume overnight bars | {blk['zero_volume_bars']} |")
    a(f"| minutes missing between the reopen and the scheduled overnight end, of the scheduled overnight minutes "
      f"(17:00 to 08:29, or to an earlier close) | {blk['missing_after_reopen']} of {blk['scheduled_after_open']} "
      f"({_pct(blk['share_missing_after_reopen'], 3)}) |")
    lg = blk["longest_gap"]
    a(f"| longest gap | {lg[2]} minutes from {lg[1]} CT on trading day {lg[0]} |" if lg else "| longest gap | none |")
    a("")
    a("**Gaps after the reopen** (runs of minutes with no bar; a minute without a trade has no bar), by length: "
      "runs, and days holding at least one:")
    a("")
    a("| run length (minutes) | runs | days |")
    a("|---|---|---|")
    for b, k in blk["gap_bins"].items():
        a(f"| {b} | {k} | {blk['gap_bin_days'][b]} |")
    a("")
    om = blk.get("max_day_missing_outside_top_month")
    a("**Where the missing minutes concentrate** (calendar month: minutes missing after the reopen): "
      + ", ".join(f"{m_} {v_}" for m_, v_ in blk.get("missing_by_month", []))
      + (f"; outside {om[0]}, the most on any day is {om[2]} minutes ({om[1]})." if om else "."))
    a("")
    a("**The days with the most minutes missing after the reopen** (trading day, minutes missing, longest run): "
      + ", ".join(f"{d} ({m_}, {lg_})" for d, m_, lg_ in blk["most_missing_days"]) + ".")
    a("")
    a(f"**Gaps of {VOID_GAP} minutes or more** (each voids its day; trading day, start CT, minutes): "
      + (", ".join(f"{d} {t} ({k})" for d, t, k in blk["long_gaps"]) or "none") + ".")
    a("")
    a("**Where gaps of 2 minutes or more start, by CT hour** (the thin hours):")
    a("")
    a("| hour | " + " | ".join(blk["gap_hours_ge2"]) + " |")
    a("|---|" + "---|" * len(blk["gap_hours_ge2"]))
    a("| gaps | " + " | ".join(str(x) for x in blk["gap_hours_ge2"].values()) + " |")
    a("")
    a(f"**Bars by CT hour** (share of scheduled day-minutes holding a bar; of the bars, the share flat -- open = high = "
      f"low = close -- and the share thin, volume <= {LOW_VOLUME}):")
    a("")
    a("| hour | present | flat | thin | zero volume |")
    a("|---|---|---|---|---|")
    for hh, x in blk["hours"].items():
        a(f"| {hh} | {_pct(x['share_present'])} | {_pct(x['share_flat'])} | {_pct(x['share_thin'])} | "
          f"{x['zero_volume']} |")
    a("")
    pr = blk["presence"]
    a("**The slots the overnight sources read** (share of the block's days):")
    a("")
    a(f"- RL3 `on`: the bar stamped 08:29 (its reference; `no_ref_bar` otherwise) {_pct(pr['bar_0829'])}; at least one "
      f"bar 17:00-08:29 {_pct(pr['any_overnight_bar'])}.")
    a(f"- `compute_overnight`: the bar stamped at alert - 1, over the alerts 17:05..08:25: lowest "
      f"{_pct(pr['prior_bar_min'])}, mean {_pct(pr['prior_bar_mean'])}; the lowest alerts "
      + ", ".join(f"{t} ({_pct(x)})" for t, x in pr["prior_bar_lowest"])
      + f". At least one bar in the five minutes before the alert: lowest {_pct(pr['window5_min'])}. The close c "
      f"defined (any bar of the day before the alert): at 17:05 {_pct(pr['close_defined_at_1705'])}, lowest over "
      f"the alerts {_pct(pr['close_defined_min'])}. The bar stamped 17:00: {_pct(pr['bar_1700'])}.")
    a("")
    rl = blk["roll"]
    a(f"**Roll evenings:** {rl['roll_days']} roll days in the block; the days the bars change contract "
      f"{'agree' if rl['agree'] else 'DISAGREE'} with the manifest's `rolls` ({_dates(rl['manifest_rolls'])}). On "
      f"{rl['reopen_jump_over_p995']} of {rl['roll_days']} the reopen jump (first open against the previous day's "
      "last close, in ticks) exceeds the 99.5th percentile of the non-roll evenings' -- the calendar spread the raw "
      "series carries, fictitious as a move. Minutes missing after the reopen, mean a day: roll days "
      f"{_num(rl['mean_missing_roll'])}, other days {_num(rl['mean_missing_other'])}. Inside a roll day the series is "
      "one contract (two-contract days above).")
    a("")
    bc = blk["bls_clock"]
    a("**The clock check on release days** (the 08:30 ET BLS release is the bar stamped 07:30 CT; the overnight "
      "minute 06:00-08:29 CT with the most volume):")
    a("")
    a("| days | n | at 07:30 | within a minute | an hour off |")
    a("|---|---|---|---|---|")
    near_txt = f"within {DST_NEAR_DAYS} days after a US change"
    for tag, nm in (("release", "all release days"),
                    ("release_near_dst", f"release days {near_txt}"),
                    ("release_away", "the other release days"),
                    ("control_non_release", "non-release weekdays (control)"),
                    ("major", "major releases (Employment Situation, CPI)"),
                    ("major_near_dst", f"major releases {near_txt}"),
                    ("major_away", "the other major releases"),
                    ("early_release", "all release days, window 06:00-07:59"),
                    ("early_release_near_dst", f"release days {near_txt}, window 06:00-07:59"),
                    ("early_major", "major releases, window 06:00-07:59"),
                    ("early_control", "non-release weekdays, window 06:00-07:59")):
        x = bc.get(tag)
        if x is None:
            continue
        a(f"| {nm} | {x['days']} | {_pct(x['share_at_0730'], 1)} | {_pct(x['share_within_1min'], 1)} | "
          f"{x['an_hour_off']} |")
    a("")
    a("The first four rows are the reading fixed before the first run; the rest were added after it, to diagnose its "
      "low share (minor releases move little; the 08:00 hour's pre-open volume competes) -- the first reading stays "
      "on record. Where the busiest minute falls instead (all release days, window to 08:29): "
      f"{bc['release'].get('elsewhere_at', {})}; window to 07:59: "
      f"{(bc.get('early_release') or {}).get('elsewhere_at', {})}.")
    a("")
    a(f"Release days whose busiest minute is elsewhere: {_dates(bc['release']['elsewhere_days'])}.")
    a("")
    a("**The daylight-saving transitions** (each change is at 02:00 local on a Sunday, while the market is shut between "
      "Friday 16:00 and Sunday 17:00 CT; the last session before it and the first after):")
    a("")
    a("| change | before: day, reopen, UTC offset | after: day, reopen, UTC offset | after: breaks / offsets / dup "
      "slots / missing |")
    a("|---|---|---|---|")
    for r in blk["dst"]:
        b, f = r.get("before"), r.get("after")
        fb = f"{b['day']}, {b['reopen_ct']}, {b['utc_offset_h']:+.0f} h" if b else "--"
        ff = f"{f['day']}, {f['reopen_ct']}, {f['utc_offset_h']:+.0f} h" if f else "--"
        fx = (f"{f['clock_breaks']} / {f['offsets_in_overnight']} / {f['dup_slots']} / {f['missing_after_reopen']}"
              if f else "--")
        a(f"| {r['change']} | {fb} | {ff} | {fx} |")
    a("")
    a(f"Across the block: {blk['clock_breaks']} clock breaks and {blk['mixed_offset_days']} overnights under two UTC "
      "offsets.")
    a("")
    a("**Session boundaries abroad** (not a data defect -- the declared windows are fixed in CT, "
      "`lever_space.declared('windows_ct')`): 08:00 London is not 02:00 CT on "
      f"{blk['london_shift_days']} days (the US and the UK change on different Sundays): "
      + (", ".join(f"{x} to {y} ({k})" for x, y, k in blk["london_shift_stretches"]) or "none")
      + f". 09:00 Tokyo falls at CT {blk['tokyo_open_ct']} (days), so `asia` from 18:00 CT is Tokyo's open only "
      "under US standard time.")
    a("")
    a("**Void and special days** (rules fixed in `extended/overnight_bars_check.py` before the read):")
    a("")
    a(f"- **VOID: {blk['void_day_count']} days.** By rule: {blk['void_count'] or 'none'}.")
    for d, rs in blk["void_days"].items():
        a(f"  - {d}: {', '.join(rs)}")
    a(f"- **SPECIAL** (counts by flag): {blk['special_count']}.")
    for k, xs in blk["special_days"].items():
        if k == "roll":
            continue
        a(f"  - `{k}`: {_dates(xs)}")
    a("")


def render(res: Mapping[str, Any]) -> str:
    s, h, pw, meta = res["search"], res["held_out"], res["power"], res["meta"]
    v, why = verdict(s, res.get("held_out_bar_checked", False), res.get("extra_reasons", ()))
    L: list[str] = []
    a = L.append
    a(f"**Verdict: {v}**")
    a("")
    a(f"# H2 (Q-154): NQ overnight 1-minute bars, 17:00 to 08:30 CT -- data integrity, {meta['date']}")
    a("")
    a("Rendered by `scripts/h2_overnight_bars.py` from its JSON (`extended/overnight_bars_check.py`); every number "
      "below is computed from the bars or the store's manifest by that script, none typed. Counts, shares, clock "
      "labels and dates only: no price, return or range.")
    a("")
    a("**Why blocked:**" if v == "BLOCKED" else "**Validated.**")
    for w in why:
        a(f"- {w}.")
    a("")
    a("## Can the family's question be answered on this data?")
    a("")
    ps, ph = pw["search"], pw["held_out"]
    a(f"The held-out block holds {ph['sessions']} sessions, {ph['blocks']} whole {pw['block_len']}-session blocks; an "
      f"exact sign-flip over {ph['blocks']} blocks cannot reach below {_num(ph['min_signflip_p'], '.3g')}, against the family's "
      f"level 0.05 / ({pw['k']} x {pw['k'] + 1}) = {pw['level']:.3g} (that needs {pw['blocks_needed_for_signflip']} "
      f"blocks): {'it can reach it' if ph['signflip_can_reach_level'] else 'it cannot reach it'} -- so, as E-208 "
      "records, only the paired coin-seed leg can carry the level and the years leg is a consistency condition. The "
      f"search block holds {ps['sessions']} sessions ({ps['blocks']} blocks). An overnight source adds offer moments "
      "inside sessions, not sessions: it does not change this arithmetic.")
    a("")
    a("Stage one's sample-size table (`vendor/stage2/vendor/propsim/edge/results_sample_size.csv`): the trades a "
      "demonstrated edge e needs, beside the sessions here (at one trade a session):")
    a("")
    a("| R | e | trades (lower bound above e/2) | search sessions | held-out sessions |")
    a("|---|---|---|---|---|")
    for r in pw["sample_size"]:
        a(f"| {r['R']} | {r['true_edge']} | {r['trades_lb_above_half_edge']} | {ps['sessions']} | {ph['sessions']} |")
    a("")
    a("The journey objective judges P on coin-sided designs, not an edge, so the table bounds only a claim of edge, "
      "which no overnight trigger here makes.")
    a("")
    a("## Source, span and the confirmation window")
    a("")
    m = meta["manifest"]
    a(f"- **Store:** `vendor/stage2/data/bars/NQ/` (Stage 2 {m['decision']}), {m['licence']}; tick {m['tick']}; "
      f"`parquet_sha256` `{m['parquet_sha256']}`. `python scripts/vendor_stage2.py --verify`: {meta['verify']}.")
    for imp in m["imports"]:
        a(f"- **Purchase** `{imp['source']}` (`{imp['csv']}`; {imp['dataset']}, {imp['schema']}, "
          f"{', '.join(imp['symbols'])}), imported {imp['imported']}; days dropped by the windows guard "
          f"{imp['days_dropped_by_window']} (first: {imp['first_dropped_day']}). Cost: not recorded in the manifest.")
    a(f"- **Span stored:** {m['first_day']} to {m['last_day']}, {m['days']} trading days, {m['rows']} bars. "
      f"**Nothing from the confirmation window is present:** the store's last day is {m['last_day']}; every frame "
      f"loaded was asserted to hold no bar starting at or after 16:00 CT on {LAST_DEV_DAY} (`assert_loaded`); the "
      f"last search day loaded is {s['last_day']}.")
    a("- **Contract continuation:** one outright a trading day, the previous day's outright-volume leader (Stage 2 "
      "D-98); **raw prices**, no back- or ratio-adjustment, so a cross-day level jumps by the calendar spread on a "
      f"roll day ({len(m['rolls'])} rolls in the store). `vendor/stage2/data/README.md` section 5.")
    a("- **Calendar used:** `config/calendar_early_closes.csv` (Q-40: the U.S. exchange holiday rules, cross-checked "
      "against the manifest; CME's pages refuse scripted reads); BLS 08:30 ET release days from the vendored "
      "schedule parses (`extended.features.load_calendars`). No CME calendar is vendored under "
      "`vendor/stage2/config/sources/` (FOMC and EIA schedules only).")
    a("")
    a("## The clock: what the code assumes and what the data shows")
    a("")
    a("- README section 5: a session opens at 17:00 CT the evening before; `day` = the bar's Chicago time plus seven "
      "hours, its date; `ts` the bar's **start**. `extended.lever_space.trading_day()`: reopen "
      f"{meta['trading_day']['reopen_ct']} CT, flat {meta['trading_day']['flat_ct']} CT. The features grid and RL3's "
      "`on` level read slots 0..929 (bars stamped 17:00..08:29); RL3's reference is the bar stamped 08:29.")
    a(f"- **The daily maintenance break** is the 16:00-16:59 CT halt: bars stamped there in the search years: "
      f"{s['halt_bars']}. No break inside 17:00-08:29 is scheduled; the gap clock below shows none recurring.")
    a(f"- **Reopen** (the first bar of each search-year day, CT, days): {s['reopen']}.")
    a(f"- **The manifest's `day_bounds` against the bars** (search years): the first bar agrees on "
      f"{s['manifest_bounds_agree']} of {s['days']} days (disagreeing: {_dates(s['manifest_bounds_disagree'])}) -- "
      "the basis for reading the held-out reopen times from the manifest.")
    a("")
    _block_section(a, s, meta, "The search years, 2020-01-02 to 2023-12-29 (bars read)")
    a("## The held-out years, 2024-01-02 to 2026-07-16 (manifest only; bars not read)")
    a("")
    a("The reader seals these years (`extended/reader.py`, CHARTER 3.6-3.7, Q-158): a read touching them needs a pinned "
      "declaration naming its purpose on a `Judged-block reads:` line, inside a clean run, once. No declaration names "
      "a data check, so the bars were **not read**. What the manifest -- metadata, no bar -- shows:")
    a("")
    a(f"- {h['days']} trading days, {h['first_day']} to {h['last_day']}; reopen (first bar, CT, days): {h['reopen']}.")
    a(f"- Reopen after 17:05 CT: {_dates(h['late_reopen_days'])}. The manifest's late-start days: "
      f"{_dates(h['late_start_days'])}; short days (< 1,000 bars): {h['short_days'] or 'none'}; days ending before "
      f"15:00 CT: {len(h['early_end_days'])}.")
    a("- The manifest's short days against their scheduled length (17:00 to the scheduled close; trading day: bars "
      "/ scheduled minutes, deficit, first-last bar CT, Databento degraded): "
      + ("; ".join(f"{k}: {v['bars']} / {v['scheduled_minutes']}, {v['deficit']}, {'-'.join(v['bounds'])}"
                   f"{', degraded' if v['degraded'] else ''}" for k, v in h.get("short_day_deficits", {}).items())
         or "none") + ".")
    a(f"- Q-40's data-defect candidates: {_dates(h['calendar_defects'])}.")
    a(f"- Overnights spanning a UTC date Databento marks `degraded`: {_dates(h['degraded_overnights'])}.")
    a(f"- Rolls: {_dates(h['rolls'])}.")
    a(f"- Evenings: Sunday opens {h['sunday_open']}; after a full closure {_dates(h['after_closure'])}; after an "
      f"abbreviated session {_dates(h['after_abbreviated'])}; abbreviated days {len(h['abbreviated_day'])}; a "
      f"scheduled close before 08:30 CT (the overnight itself cut) {_dates(h['scheduled_short_overnight'])}.")
    a("- First sessions after a US daylight-saving change (change -> session, its reopen per the manifest): "
      + (", ".join(f"{c} -> {d} {t}" for c, d, t in h["dst_sessions"]) or "none") + ".")
    a(f"- 08:00 London not at 02:00 CT: {h['london_shift_days']} days; BLS 07:30 CT release days: {h['bls_days']}.")
    a("- **Not checked** (they need the bars): gaps and their clock, duplicates, the 16:00-16:59 halt, clock continuity "
      "across the DST sessions, malformed or zero-volume bars, flat and thin shares, slot presence for the features "
      "and RL3's `on`, the roll-evening jump, the BLS clock check.")
    a("")
    a("## Known limitations")
    a("")
    a("- **The held-out years' overnight bars are unchecked.** Until a row authorises their read, no overnight source "
      "may be judged on them.")
    a("- **A minute without a trade has no bar.** A 1-4 minute gap in the thin hours is the market, not a defect; an "
      "order inside it fills on the next bar's range, and a fill on a bar that gaps past a stop is the stop-fill "
      "convention's question (conduct tier 1), not this data's.")
    om = s.get("max_day_missing_outside_top_month")
    if om:
        a(f"- **The gaps sit in one month ({om[0]}).** The void rule fixed before the read (a run of {VOID_GAP} "
          "minutes or more) leaves that month's days with many shorter gaps SPECIAL (`gap_5_14`, `no_0829_bar`), not "
          "VOID; the days with the most missing minutes are listed above. Whether an overnight source drops the whole "
          "month, or those days, is a decision for its own row, made from this list and not from outcomes.")
    a("- **Stray bars stamped 16:59 CT** (the table above) belong to the day they close (Chicago + 7 h) and fall "
      "after its overnight; what they move is the next day's cross-day reads of the previous close "
      "(`extended.features`' day-level last close), and the fixed rule voids their day as outside the session.")
    a("- **Raw prices across rolls.** A cross-day level is the old contract's price on a roll day; the features set such "
      "features NaN there and RL3 voids `pd` and `pdc`. A roll day's own overnight levels (RL3 `on`) are within one "
      "contract and stand.")
    a("- **Out-of-order rows in the file** cannot be seen through the reader, which sorts; the importer writes the file "
      "sorted (README section 5), and a double-write would survive the stable sort as a duplicate.")
    a("- **The day boundary** is the store's (Chicago + 7 h): 16:59 CT belongs to the day it closes, 17:00 to the next. "
      "CME books a holiday's abbreviated session to the next business day; the store dates it to the holiday (Q-40).")
    a("- **Session windows abroad** are fixed in CT: London's 08:00 and Tokyo's 09:00 move against them for parts of "
      "each year, so a source keyed to `london` or `asia` reads a different market hour on those days.")
    a("")
    a("## What a future session must not assume")
    a("")
    a("- That the held-out overnight bars are clean because the search years' are.")
    a("- That every overnight minute has a bar, or that a feature at an overnight alert reads a bar stamped at alert - 1 "
      "(it reads the last bar before the alert, forward-filled).")
    a("- That the 08:29 bar exists (RL3 voids the day without it), or that the overnight runs to 08:29 on a Good Friday "
      "with the jobs report (the session closes 08:15 CT).")
    a("- That the series is continuous across a roll or across the purchase seam (2025-06-30 / 2025-07-01).")
    a("- That a CT session window is the same market hour abroad all year.")
    a("")
    a("## To unblock")
    a("")
    a("1. A decision row authorising this check's held-out read by a mechanism the reader accepts (a pinned "
      "declaration whose `Judged-block reads:` line names a data-integrity purpose, run once in a clean run), then "
      "`scripts/h2_overnight_bars.py --held-out` from that clean run, the held-out section rendered from the bars by "
      "the same code.")
    a("2. The void list as a pinned calendar (this script's re-runnable output, dates and reasons only, outside "
      "`vendor/`) under its own row, read by every overnight source before it builds its offers.")
    a("")
    a("## Reproduce")
    a("")
    a(f"`python scripts/h2_overnight_bars.py` (outputs: this report, its JSON, the flags "
      f"`{meta.get('flags') or 'not in the repository (a worktree run)'}`), commit "
      f"`{meta['commit']}` ({meta['tree']}); run {meta['ran']} under the run lock with `OMP_NUM_THREADS=1`. The code "
      "run, by sha256: " + ", ".join(f"`{k}` `{v}`" for k, v in (meta.get("code_sha256") or {}).items()) + ".")
    rr = meta.get("rendered")
    if rr:
        a(f"Re-rendered without reading a bar (`--render`) from the run's JSON `{rr['json']}` (sha256 "
          f"`{rr['json_sha256']}`) by `extended/overnight_bars_check.py` sha256 `{rr['renderer_sha256']}`: the "
          "computation is the run's; only the report's wording changed after it.")
    a("")
    return "\n".join(L)
