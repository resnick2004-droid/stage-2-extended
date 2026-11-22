"""Q-166: the void calendar as code -- one function giving a trading day's `extended.triggers.DayContext` (its `bls`,
`fomc`, `void` and `prior_void` flags) from the verified sources, and the local-time anchoring of the session windows
(the lead's ruling (3) on H2).

    from extended import day_calendar as DC
    src = DC.load_sources(flags=Path(".../results/h2_overnight_flags.csv"))
    ctx = DC.day_context(src, "NQ", date(2021, 3, 15), session=301, reads_overnight=True, reads_0829=True)
    why = DC.day_flags(src, "NQ", date(2021, 3, 15), reads_overnight=True)      # the reasons behind the flags
    DC.anchored_starts(date(2021, 3, 15))      # {'asia': 120, 'london': 600, 'ny': 930}: minutes after the reopen

**The sources** (`load_sources`; nothing here reads a bar):

* the BLS 08:30 ET release days and the FOMC statement lists, as `extended.features.load_calendars` reads them from
  Stage 2's vendored calendars (published in advance; `fomc` is a **scheduled** meeting's statement day that was held);
* Q-40's calendar of holidays, early closes and data-defect candidates (`config/calendar_early_closes.csv`);
* the bar store's manifest (`vendor/stage2/data/bars/NQ/manifest.json`, metadata only): its `day_list`, `rolls`,
  `early_end_days` and each day's last bar (`day_bounds`), **for the search years only** -- every entry after
  2023-12-29 is dropped as the file is read;
* H2's per-day flags (`results/h2_overnight_flags.csv`, Q-154's clean run q154-h2 of 3cf3453), checked against its
  sidecar manifest's sha256 when the manifest is beside it; a row after 2023-12-29 refuses the file.

**The rules** (`day_flags`). A **day-wide void** (every source): Q-40's `data_defect_candidate`; the manifest's
`early_end_days`; a scheduled close (Q-40 `holiday` or `early_close` with a close) at or before the walk's last bar;
and -- the red team's m-3 -- no bar stamped at or after the walk's last bar under `rules` (`triggers.JOURNEY`: the bar
ending 15:08 CT, stamped 15:07). An **overnight void** (a source reading overnight bars, `reads_overnight`): H2's
VOID verdict (its six fixed-rule days), and the lead's rule (2): more minutes missing after the reopen than the most on
any search-year day outside March 2020 (computed from the flags file, `rule2_threshold`), and, for a source reading
the bar stamped 08:29 (`reads_0829`), a day without it -- H2's `no_0829_bar`, or a scheduled overnight that ends
before it (the Good Friday jobs-report days end at 08:14). **prior_void** (the previous day's levels): a roll day (the
store's raw prices: cross-day levels are the old contract's), the evening after an abbreviated session, the evening
after a closure (a weekday without a session between two stored days), the day after a day-wide void, the store's
first day. **Recorded, no flag**: a Sunday open; a scheduled overnight end before 08:29; on an overnight source,
H2's special flags.

**Held-out years.** A context is given only for a stored search-year day (2020-01-02 to 2023-12-29); any later date
raises `HeldOutDay` (the confirmation window's `ConfirmationDay` first). `held_out_record` lists, for the record only,
what the manifest and Q-40 show of the held-out years -- the candidates the joint held-out test's declaration names --
and is never used for a context.

**The session anchors** (`anchored_starts`): asia at 09:00 Tokyo, london at 08:00 London, ny at 09:30 New York (08:30
CT), each converted for the trading day's own date by zoneinfo, as minutes after the 17:00 CT reopen of the evening the
day opens -- never a fixed CT clock time. The Tokyo open falls on the evening before the trading day's date in CT.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo

from extended import ROOT, VENDOR_STAGE2

CHICAGO = ZoneInfo("America/Chicago")
REOPEN_MIN = 17 * 60
DAY_MIN = 1440

SEARCH_START, SEARCH_END = date(2020, 1, 2), date(2023, 12, 29)
CONFIRMATION_START = date(2026, 7, 17)
MARKETS = ("NQ",)
EXCLUDED_MONTH = "2020-03"        # rule (2): the threshold is the most missing outside this month

CALENDAR_CSV = ROOT / "config" / "calendar_early_closes.csv"
MANIFEST = VENDOR_STAGE2 / "data" / "bars" / "NQ" / "manifest.json"
FLAGS_RESULT = ROOT / "results" / "h2_overnight_flags.csv"
FLAGS_RUN = Path.home() / "AppData" / "Local" / "stage2-extended-runs" / "q154-h2" / "results" / "h2_overnight_flags.csv"

#: the lead's ruling (3): each session window's open in its own market's local time
LOCAL_ANCHORS: dict[str, tuple[str, int, int]] = {"asia": ("Asia/Tokyo", 9, 0), "london": ("Europe/London", 8, 0),
                                                  "ny": ("America/New_York", 9, 30)}


class HeldOutDay(ValueError):
    """A context asked for a day after the search years."""


class ConfirmationDay(HeldOutDay):
    """A context asked for a day of NQ's confirmation window (2026-07-17 on)."""


def slot_of(text: str) -> int:
    h, m = text.split(":")
    return (int(h) * 60 + int(m) - REOPEN_MIN) % DAY_MIN


def label(s: int) -> str:
    m = (int(s) + REOPEN_MIN) % DAY_MIN
    return f"{m // 60:02d}:{m % 60:02d}"


# ------------------------------------------------------------------------------------------------------ the sources


@dataclass
class Sources:
    """Everything a context is built from, for the search years only."""
    days: list[date]
    calendar: dict[date, dict[str, str]]
    rolls: frozenset[date]
    early_end: frozenset[date]
    last_bar: dict[date, str]                         # the day's last bar start, CT HH:MM (the manifest's day_bounds)
    bls: frozenset[date]
    fomc: frozenset[date]                             # scheduled statement days that were held
    flags: dict[date, dict[str, str]] = field(default_factory=dict)
    flags_sha256: str | None = None

    def __post_init__(self) -> None:
        self.days = sorted(self.days)
        late = [d for d in self.days if d > SEARCH_END]
        if late:
            raise HeldOutDay(f"the sources hold a day after the search years ({late[0]}); they are built for "
                             f"{SEARCH_START} to {SEARCH_END} only")
        self._index = {d: i for i, d in enumerate(self.days)}

    def threshold(self) -> int:
        """Rule (2)'s threshold from this source's flags, computed once."""
        if getattr(self, "_rule2", None) is None:
            self._rule2 = rule2_threshold(self.flags)
        return self._rule2

    def previous(self, d: date) -> date | None:
        i = self._index[d]
        return self.days[i - 1] if i else None


def _in_search(d: date) -> bool:
    return SEARCH_START <= d <= SEARCH_END


def read_flags(path: Path) -> tuple[dict[date, dict[str, str]], str]:
    """H2's per-day flags (search years only), checked against the sidecar manifest's sha256 when it is beside."""
    raw = Path(path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    side = Path(str(path) + ".manifest.json")
    if side.is_file():
        want = json.loads(side.read_text(encoding="utf-8")).get("sha256")
        if want and want != sha:
            raise ValueError(f"{path}: sha256 {sha} differs from its manifest's {want}")
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    out = {}
    for r in rows:
        d = date.fromisoformat(r["day"])
        if not _in_search(d):
            raise HeldOutDay(f"{path}: a row dated {d}, outside the search years; the flags file is refused")
        out[d] = r
    return out, sha


def default_flags_path() -> Path:
    """The collected result if the lead has committed it, else the clean run's checkout."""
    return FLAGS_RESULT if FLAGS_RESULT.is_file() else FLAGS_RUN


def load_sources(flags: Path | None = None, *, manifest: Path = MANIFEST, calendar: Path = CALENDAR_CSV) -> Sources:
    from extended import features as F
    from extended.calendar_early_closes import read_calendar

    m = json.loads(Path(manifest).read_text(encoding="utf-8"))
    days = [date.fromisoformat(x) for x in m["day_list"]]
    days = [d for d in days if _in_search(d)]                              # nothing after the search years kept
    keep = lambda xs: frozenset(d for d in (date.fromisoformat(x) for x in xs) if _in_search(d))  # noqa: E731
    bounds = {date.fromisoformat(k): v[1] for k, v in m["day_bounds"].items() if _in_search(date.fromisoformat(k))}
    cal = {date.fromisoformat(r["date"]): r for r in read_calendar(calendar) if _in_search(date.fromisoformat(r["date"]))}
    c = F.load_calendars()
    fomc = frozenset(d for d, until in c.fomc_scheduled if until is None and _in_search(d))
    rows, sha = read_flags(flags if flags is not None else default_flags_path())
    return Sources(days, cal, keep(m["rolls"]), keep(m["early_end_days"]), bounds,
                   frozenset(d for d in c.bls if _in_search(d)), fomc, rows, sha)


def rule2_threshold(flags: Mapping[date, Mapping[str, str]]) -> int:
    """The most minutes missing after the reopen on any search-year day outside March 2020 (the lead's rule (2))."""
    vals = [int(r["missing_after_reopen"]) for d, r in flags.items() if d.strftime("%Y-%m") != EXCLUDED_MONTH]
    if not vals:
        raise ValueError("no flags row outside March 2020: rule (2)'s threshold is undefined")
    return max(vals)


# --------------------------------------------------------------------------------------------------------- the rules


@dataclass(frozen=True)
class DayFlags:
    day: date
    void: tuple[str, ...]
    prior_void: tuple[str, ...]
    noted: tuple[str, ...]
    bls: bool
    fomc: bool


def _walk_last_stamp(rules: Any) -> int:
    """The slot of the bar a walk under `rules` ends on: the walker indexes bars by their END minute."""
    return int(rules.walk_end) - 1


def _scheduled_close(row: Mapping[str, str] | None) -> int | None:
    if row and row["kind"] in ("holiday", "early_close") and row.get("close_ct"):
        return slot_of(row["close_ct"])
    return None


def _check(market: str, d: date, src: Sources) -> None:
    if market not in MARKETS:
        raise ValueError(f"the calendar is NQ's (CME equity-index futures); {market!r} has none here")
    if d >= CONFIRMATION_START:
        raise ConfirmationDay(f"{d} lies in NQ's confirmation window (from {CONFIRMATION_START}): never read")
    if d > SEARCH_END:
        raise HeldOutDay(f"{d} lies after the search years: a held-out day's context belongs to the joint held-out "
                         "test's declared read (the lead's ruling (1) on H2)")
    if d not in src._index:
        raise KeyError(f"{d} is not a stored trading day")


def _day_void(src: Sources, d: date, last_stamp: int) -> list[str]:
    out = []
    row = src.calendar.get(d)
    if row and row["kind"] == "data_defect_candidate":
        out.append("data_defect")
    if d in src.early_end:
        out.append("early_end")
    close = _scheduled_close(row)
    if close is not None and close - 1 < last_stamp:
        out.append("early_close")
    lb = src.last_bar.get(d)
    if lb is None or slot_of(lb) < last_stamp:
        out.append(f"no_bar_at_{label(last_stamp)}")
    return out


def day_flags(src: Sources, market: str, d: date, *, reads_overnight: bool = False, reads_0829: bool = False,
              rules: Any = None) -> DayFlags:
    """Every reason behind a day's flags (the module docstring's rules)."""
    if rules is None:
        from extended import triggers as T
        rules = T.JOURNEY
    _check(market, d, src)
    last_stamp = _walk_last_stamp(rules)
    void = _day_void(src, d, last_stamp)
    noted: list[str] = []
    row = src.calendar.get(d)
    close = _scheduled_close(row)
    on_end = slot_of("08:29")
    if close is not None and close - 1 < on_end:
        noted.append(f"overnight_ends_{label(close - 1)}")
    if d.weekday() == 0:
        noted.append("sunday_open")
    if reads_overnight:
        f = src.flags.get(d)
        if f is None:
            raise KeyError(f"{d}: no H2 flags row; an overnight source's day cannot be judged")
        if f["verdict"] == "VOID":
            void.append("h2_void:" + f["void"])
        if int(f["missing_after_reopen"]) > src.threshold():
            void.append("h2_missing")
        if reads_0829 and ("no_0829_bar" in f["special"].split(";") or (close is not None and close - 1 < on_end)):
            void.append("no_0829_bar")
        noted += [f"h2:{x}" for x in f["special"].split(";") if x]
    prior = _prior_scheduled(src, d)
    prev = src.previous(d)
    if prev is not None and _day_void(src, prev, last_stamp):
        prior.append("prior_day_void")
    return DayFlags(d, tuple(void), tuple(prior), tuple(noted), d in src.bls, d in src.fomc)


def _prior_scheduled(src: Sources, d: date) -> list[str]:
    """The previous-day reasons a calendar gives in advance: the store's first day, a roll, the evening after a
    scheduled close, the evening after a closure (a weekday without a session between two stored days)."""
    prior: list[str] = []
    prev = src.previous(d)
    if prev is None:
        prior.append("first_day")
    else:
        if d in src.rolls:
            prior.append("roll")
        if _scheduled_close(src.calendar.get(prev)) is not None:
            prior.append("after_abbreviated")
        k = prev + timedelta(days=1)
        while k < d:
            if k.weekday() < 5:
                prior.append("after_closure")
                break
            k += timedelta(days=1)
    return prior


def _closed_all_day(src: Sources, k: date) -> bool:
    """A weekday the calendar schedules the exchange shut all day (Q-40: a holiday without a close)."""
    row = src.calendar.get(k)
    return row is not None and row["kind"] == "holiday" and not row.get("close_ct")


def data_void(src: Sources, d: date, *, rules: Any = None) -> tuple[str, ...]:
    """The data voids of a stored day (`_day_void`: a data-defect candidate, an early end of its bars, a scheduled close
    before the walk's last bar, no bar at the walk's last stamp), for the playbook's check that a previous day's bars
    can give levels (the lead's ruling on C3-1: a prior-level alert on a data-void previous day refuses)."""
    if rules is None:
        from extended import triggers as T
        rules = T.JOURNEY
    return tuple(_day_void(src, d, _walk_last_stamp(rules)))


def prior_session(src: Sources, d: date) -> date | None:
    """**The previous session by the calendar** (the lead's C3-1 ruling on Wave 3.5, withdrawing N-c2-2): the last
    weekday before `d` that the calendar does not schedule shut all day, whether or not the store holds it; None when
    it falls before the store's first day."""
    k = d - timedelta(days=1)
    while k.weekday() >= 5 or _closed_all_day(src, k):
        k -= timedelta(days=1)
    return k if src.days and k >= src.days[0] else None


def _prior_known(src: Sources, d: date) -> list[str]:
    """The previous-day reasons known before the day's alert, all from the calendar (C3-1): no previous session in
    the store's span (`first_day`), a roll, a scheduled close on the calendar's previous session (`after_abbreviated`,
    whether or not the store holds that session), a scheduled closure between it and `d` (`after_closure`). Whether
    the store's previous day is that session is the alert's check (`playbook`: a data mismatch, never a void)."""
    prev = prior_session(src, d)
    if prev is None:
        return ["first_day"]
    prior: list[str] = []
    if d in src.rolls:
        prior.append("roll")
    if _scheduled_close(src.calendar.get(prev)) is not None:
        prior.append("after_abbreviated")
    k = prev + timedelta(days=1)
    while k < d:
        if k.weekday() < 5 and _closed_all_day(src, k):
            prior.append("after_closure")
            break
        k += timedelta(days=1)
    return prior


#: what `alert_context` leaves out: data-defect filters known only after the alert (research-only, the lead's B-5
#: ruling on Wave 3.5): the day's own last bar, an early end of its bars, a data-defect candidate, H2's overnight
#: counts, and the previous day's data voids
RESEARCH_ONLY = ("no_bar_at_walk_end", "early_end", "data_defect", "h2_void", "h2_missing", "prior_day_void")


def alert_context(src: Sources, market: str, d: date, session: int, *, windows: Sequence[Any] = (),
                  rules: Any = None):
    """**The day as known before its first alert** (the lead's B-5 ruling on Wave 3.5): the `DayContext` a hand-traded
    alert may read -- `bls` and `fomc` (published in advance), `void` for a scheduled close (Q-40's `holiday` or
    `early_close` with a close) at or before the walk's last bar, `prior_void` from the calendar's previous-day
    reasons (`_prior_known`: a closure only when the calendar schedules it), and the verified news `windows` the caller passes from its record. None of
    `RESEARCH_ONLY` is read. Held-out and confirmation-window days refuse as in `day_flags`, until a live calendar is
    declared under its own row."""
    from extended import triggers as T

    if rules is None:
        rules = T.JOURNEY
    _check(market, d, src)
    close = _scheduled_close(src.calendar.get(d))
    void = close is not None and close - 1 < _walk_last_stamp(rules)
    return T.DayContext(int(session), d.isoformat(), bls=d in src.bls, fomc=d in src.fomc, void=bool(void),
                        prior_void=bool(_prior_known(src, d)), windows=tuple(windows))


def day_context(src: Sources, market: str, d: date, session: int, *, reads_overnight: bool = False,
                reads_0829: bool = False, rules: Any = None):
    """The `extended.triggers.DayContext` of trading day `d` at history index `session`: `bls`, `fomc`, `void` and
    `prior_void` from `day_flags`; no verified news window is added here (`windows` empty)."""
    from extended import triggers as T

    f = day_flags(src, market, d, reads_overnight=reads_overnight, reads_0829=reads_0829, rules=rules)
    return T.DayContext(int(session), d.isoformat(), bls=f.bls, fomc=f.fomc, void=bool(f.void),
                        prior_void=bool(f.prior_void))


# ----------------------------------------------------------------------------------------------- the held-out record


def held_out_record(manifest: Path = MANIFEST, calendar: Path = CALENDAR_CSV,
                    start: date = date(2024, 1, 2), end: date = date(2026, 7, 16)) -> dict[str, Any]:
    """For the record only (never a context): the held-out days the manifest and Q-40 flag -- metadata, no bar."""
    from extended.calendar_early_closes import read_calendar

    m = json.loads(Path(manifest).read_text(encoding="utf-8"))
    inr = lambda x: start <= date.fromisoformat(x) <= end  # noqa: E731
    days = [x for x in m["day_list"] if inr(x)]
    if any(date.fromisoformat(x) >= CONFIRMATION_START for x in days):
        raise ConfirmationDay("the manifest lists a confirmation-window day inside the held-out span")
    late = sorted(x for x in days if slot_of(m["day_bounds"][x][0]) > 0)
    return {"late_reopen": late,
            "short_days": {k: v for k, v in m.get("short_days", {}).items() if inr(k)},
            "early_end_days": sorted(x for x in m.get("early_end_days", []) if inr(x)),
            "data_defect_candidates": sorted(r["date"] for r in read_calendar(calendar)
                                             if r["kind"] == "data_defect_candidate" and inr(r["date"]))}


# ----------------------------------------------------------------------------------------------- the session anchors


def anchored_starts(d: date) -> dict[str, int]:
    """Each declared session's start for trading day `d`, in minutes after the 17:00 CT reopen of the evening before
    `d`, from its local market time (`LOCAL_ANCHORS`), DST-aware on both sides."""
    reopen = datetime(d.year, d.month, d.day, 17, 0, tzinfo=CHICAGO) - timedelta(days=1)
    out = {}
    for name, (tz, h, m) in LOCAL_ANCHORS.items():
        z = ZoneInfo(tz)
        for cand in (d - timedelta(days=1), d):                        # the local open inside the trading day
            t = datetime(cand.year, cand.month, cand.day, h, m, tzinfo=z)
            off = (t - reopen) // timedelta(minutes=1)
            if 0 <= off < DAY_MIN:
                out[name] = int(off)
                break
        else:
            raise ValueError(f"{name}'s local open does not fall inside trading day {d}")
    return out
