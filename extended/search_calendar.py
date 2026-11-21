"""Q-197: the pinned search-year session calendar -- every NQ session of 2020-01-02 to 2023-12-29 as the bar store's
manifest lists it, its session ordinal and sessions left (the start session counted as session 1, H4's draft and
W42-R1's B-2), its day kind and each reading class's void flag from `extended.day_calendar` (Q-166), as one result
file written by `scripts/search_calendar.py`; and the small pure loader W42-R1 and H4 import.

    from extended.search_calendar import load_search_calendar
    cal = load_search_calendar()                     # results/search_calendar.csv, checked against its manifest
    cal.dates                                        # ('2020-01-02', ..., '2023-12-29'): W42-R1's `search_calendar`
    cal.calendar_sha256                              # W42-R1's `calendar_digest(cal.dates)`: H4's `calendar_sha256`
    cal.sessions_left("2023-12-29")                  # 1: the start session is session 1

**The columns** (`COLUMNS`) hold dates, labels and integers only -- no price, no time of any price event:

* `date` (ISO), `weekday` (Mon .. Sun), `session` (1 .. N in calendar order), `sessions_left` (N - session + 1);
* `day_kind`: Q-40's kind for the date (`config/calendar_early_closes.csv`: `holiday` -- a holiday session the store
  holds, abbreviated -- `early_close`, `data_defect_candidate`), else `regular`; `roll` (the store's roll days), `bls`,
  `fomc` (0 / 1, `day_calendar.day_flags`);
* per reading class (`CLASSES`), `void_<class>` (0 / 1) and `why_void_<class>` (`day_calendar.day_flags`'s reasons,
  joined by `|`): `day` reads no overnight bar (the day-wide voids only), `overnight` reads the overnight bars (H2's
  VOID verdict and the lead's rule (2) added), `overnight_0829` also reads the bar stamped 08:29 (its absence added);
* `prior_void` (0 / 1) and `why_prior_void`: the previous day's levels unusable (a roll, after an abbreviated session
  or a closure, after a day-wide void, the store's first day); the same in every reading class.

**The guards.** A row dated after 2023-12-29 is refused (`day_calendar.HeldOutDay`; from 2026-07-17
`day_calendar.ConfirmationDay` first), by the builder, the writer's check and the loader alike. **The identities**
(`identities`, refusing with `CalendarIdentityError`): (I-1) the dates are exactly the search-year dates of H2's flags
file, their count first; (I-2) every void and prior-void flag and reason equals `day_calendar`'s own call for that day
(`day_context` for the flags at the row's session, `day_flags` for the reasons), day for day, on the rows as they
were parsed back from the CSV text about to be written.

**The digest** (`calendar_digest`) is W42-R1's (`extended/wave42.py`, wt/wt-infra 357a339): the sha256 of the ISO
dates, one a line, each ended by a newline (UTF-8). The loader recomputes it from the file and refuses a file whose
manifest records another, a file whose bytes are not its manifest's sha256, and a calendar that is not strictly
increasing from 2020-01-02 to 2023-12-29 with sessions 1 .. N.

Nothing here reads a bar, draws randomness or imports the vendored engine; the loader reads only the CSV and its
sidecar manifest.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

from extended import RESULTS_DIR
from extended import day_calendar as DC

SEARCH_START, SEARCH_END = DC.SEARCH_START, DC.SEARCH_END
CONFIRMATION_START = DC.CONFIRMATION_START
MARKET = "NQ"
RESULT_NAME = "search_calendar.csv"
DEFAULT_PATH = RESULTS_DIR / RESULT_NAME
SEP = "|"

#: the reading classes: name -> (reads_overnight, reads_0829), `day_calendar.day_flags`'s two switches
CLASSES: dict[str, tuple[bool, bool]] = {"day": (False, False), "overnight": (True, False),
                                         "overnight_0829": (True, True)}
COLUMNS: tuple[str, ...] = (
    "date", "weekday", "session", "sessions_left", "day_kind", "roll", "bls", "fomc",
    *(f"void_{c}" for c in CLASSES), "prior_void",
    *(f"why_void_{c}" for c in CLASSES), "why_prior_void",
)
INT_COLUMNS = ("session", "sessions_left")
FLAG_COLUMNS = ("roll", "bls", "fomc", *(f"void_{c}" for c in CLASSES), "prior_void")
LABEL_COLUMNS = ("weekday", "day_kind", *(f"why_void_{c}" for c in CLASSES), "why_prior_void")
DAY_KINDS = ("regular", "holiday", "early_close", "data_defect_candidate")
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

_ISO = re.compile(r"\d{4}-\d{2}-\d{2}")
_LABEL = re.compile(r"[a-z0-9_:;|]*")
_HEX64 = re.compile(r"[0-9a-f]{64}")


class CalendarIdentityError(RuntimeError):
    """An identity of the search calendar failed: nothing is written (or, after the write, the file stays on
    record and the run exits non-zero)."""


class CalendarRefused(ValueError):
    """A calendar file or table that is not the pinned search calendar's form."""


# --------------------------------------------------------------------------------------------------------- the digest


def calendar_digest(dates: Sequence[Any]) -> str:
    """W42-R1's digest: the sha256 of the ISO dates, one per line, each line ended by a newline (UTF-8)."""
    return hashlib.sha256("".join(f"{d}\n" for d in dates).encode("utf-8")).hexdigest()


def sha256_file(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def data_manifest_sha(manifest_file: Path | str, rel: str) -> str | None:
    """The sha256 a `sha256sum`-form list (`vendor/DATA_MANIFEST_stage2.sha256`) records for `rel`; None if absent."""
    p = Path(manifest_file)
    if not p.is_file():
        return None
    for line in p.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip("*") == rel:
            return parts[0]
    return None


# ------------------------------------------------------------------------------------------------------- the guards


def guard_date(d: date) -> None:
    """Refuse a date of the confirmation window first, then any date after the search years or before them."""
    if d >= CONFIRMATION_START:
        raise DC.ConfirmationDay(f"{d} lies in NQ's confirmation window (from {CONFIRMATION_START}): never read")
    if d > SEARCH_END:
        raise DC.HeldOutDay(f"{d} lies after the search years ({SEARCH_START} to {SEARCH_END}): the search calendar "
                            "holds none")
    if d < SEARCH_START:
        raise CalendarRefused(f"{d} lies before the search years ({SEARCH_START})")


# ------------------------------------------------------------------------------------------------------ the builder


def _kind(src: DC.Sources, d: date) -> str:
    row = src.calendar.get(d)
    k = row["kind"] if row else "regular"
    if k not in DAY_KINDS:
        raise CalendarRefused(f"{d}: Q-40's kind {k!r} is not one of {DAY_KINDS[1:]}")
    return k


def build_rows(src: DC.Sources, *, rules: Any = None) -> list[dict[str, Any]]:
    """One row a stored search-year session of `src`, in calendar order (the module docstring's columns)."""
    days = list(src.days)
    for d in days:
        guard_date(d)
    n = len(days)
    out = []
    for i, d in enumerate(days):
        per = {c: DC.day_flags(src, MARKET, d, reads_overnight=on, reads_0829=b829, rules=rules)
               for c, (on, b829) in CLASSES.items()}
        f0 = per["day"]
        row: dict[str, Any] = {"date": d.isoformat(), "weekday": WEEKDAYS[d.weekday()], "session": i + 1,
                               "sessions_left": n - i, "day_kind": _kind(src, d), "roll": int(d in src.rolls),
                               "bls": int(f0.bls), "fomc": int(f0.fomc)}
        for c, f in per.items():
            row[f"void_{c}"] = int(bool(f.void))
        row["prior_void"] = int(bool(f0.prior_void))
        for c, f in per.items():
            row[f"why_void_{c}"] = SEP.join(f.void)
        row["why_prior_void"] = SEP.join(f0.prior_void)
        out.append(row)
    return out


# ------------------------------------------------------------------------------------------- the form of the table


def check_rows(rows: Sequence[Mapping[str, Any]], *, require_span: bool = True) -> list[str]:
    """Refuse a table that is not the search calendar's form: exactly `COLUMNS`; dates ISO, strictly increasing, inside
    the search years (the confirmation window refused first); sessions 1 .. N and sessions left N .. 1; flags 0 / 1;
    labels of `[a-z0-9_:;|]` only; with `require_span`, first 2020-01-02 and last 2023-12-29. Returns the dates."""
    if not rows:
        raise CalendarRefused("the search calendar has no session")
    dates: list[date] = []
    for r in rows:
        if tuple(r.keys()) != COLUMNS:
            raise CalendarRefused(f"the columns are {tuple(r.keys())}, not {COLUMNS}")
        s = str(r["date"])
        if not _ISO.fullmatch(s):
            raise CalendarRefused(f"{s!r} is not an ISO date")
        dates.append(date.fromisoformat(s))
    for d in dates:                                     # every date guarded before any other check
        guard_date(d)
    if any(b <= a for a, b in zip(dates, dates[1:])):
        raise CalendarRefused("the dates are not strictly increasing")
    if require_span and (dates[0] != SEARCH_START or dates[-1] != SEARCH_END):
        raise CalendarRefused(f"the search calendar runs from {SEARCH_START} to {SEARCH_END}; this one from "
                              f"{dates[0]} to {dates[-1]}")
    n = len(rows)
    for i, (r, d) in enumerate(zip(rows, dates)):
        for k in INT_COLUMNS + FLAG_COLUMNS:
            v = r[k]
            if isinstance(v, bool) or not isinstance(v, int):
                raise CalendarRefused(f"{d} {k}: {v!r} is not an integer")
        if r["session"] != i + 1 or r["sessions_left"] != n - i:
            raise CalendarRefused(f"{d}: session {r['session']} / sessions left {r['sessions_left']}, not "
                                  f"{i + 1} / {n - i} (the start session is session 1)")
        for k in FLAG_COLUMNS:
            if r[k] not in (0, 1):
                raise CalendarRefused(f"{d} {k}: {r[k]!r} is not 0 or 1")
        for k in LABEL_COLUMNS:
            if not isinstance(r[k], str) or not _LABEL.fullmatch(r[k].lower() if k == "weekday" else r[k]):
                raise CalendarRefused(f"{d} {k}: {r[k]!r} is not a label")
        if r["weekday"] != WEEKDAYS[d.weekday()]:
            raise CalendarRefused(f"{d}: weekday {r['weekday']!r} is not {WEEKDAYS[d.weekday()]!r}")
        if r["day_kind"] not in DAY_KINDS:
            raise CalendarRefused(f"{d}: day kind {r['day_kind']!r} is not one of {DAY_KINDS}")
        for c in CLASSES:
            if bool(r[f"void_{c}"]) != bool(r[f"why_void_{c}"]):
                raise CalendarRefused(f"{d}: void_{c} and its reasons disagree")
        if bool(r["prior_void"]) != bool(r["why_prior_void"]):
            raise CalendarRefused(f"{d}: prior_void and its reasons disagree")
    return [d.isoformat() for d in dates]


# ------------------------------------------------------------------------------------------- the CSV text and back


def to_csv_text(rows: Sequence[Mapping[str, Any]]) -> str:
    """The rows as CSV text, `COLUMNS` in order (the identities run on this text parsed back)."""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(COLUMNS), lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: r[k] for k in COLUMNS})
    return buf.getvalue()


def parse_csv_text(text: str) -> list[dict[str, Any]]:
    """CSV text back to rows: the integer columns as int, the rest as text (blank stays "")."""
    rd = csv.DictReader(io.StringIO(text))
    if tuple(rd.fieldnames or ()) != COLUMNS:
        raise CalendarRefused(f"the file's columns are {tuple(rd.fieldnames or ())}, not {COLUMNS}")
    out = []
    for r in rd:
        row: dict[str, Any] = {}
        for k in COLUMNS:
            v = r[k]
            if v is None:
                raise CalendarRefused("a row is short of columns")
            if k in INT_COLUMNS + FLAG_COLUMNS:
                if not re.fullmatch(r"-?\d+", v):
                    raise CalendarRefused(f"{r['date']} {k}: {v!r} is not an integer")
                row[k] = int(v)
            else:
                row[k] = v
        if None in r:
            raise CalendarRefused(f"{r['date']}: a row has more cells than columns")
        out.append(row)
    return out


# ---------------------------------------------------------------------------------------------------- the identities


def identities(rows: Sequence[Mapping[str, Any]], src: DC.Sources, *, rules: Any = None) -> dict[str, Any]:
    """(I-1) and (I-2) of the module docstring, refusing (`CalendarIdentityError`); returns what each compared."""
    dates = [str(r["date"]) for r in rows]
    h2 = sorted(d.isoformat() for d in src.flags)
    if len(dates) != len(h2):
        raise CalendarIdentityError(f"(I-1) the calendar holds {len(dates)} dates, H2's flags file "
                                    f"{len(h2)} search-year dates")
    if dates != h2:
        diff = sorted(set(dates) ^ set(h2))
        raise CalendarIdentityError(f"(I-1) the dates differ from H2's flags file's, first at {diff[:3]}")
    stored = [d.isoformat() for d in src.days]
    if dates != stored:
        raise CalendarIdentityError("(I-1) the dates differ from the store manifest's search-year day_list")
    void_days = {c: 0 for c in CLASSES}
    prior = 0
    for r in rows:
        d = date.fromisoformat(str(r["date"]))
        for c, (on, b829) in CLASSES.items():
            ctx = DC.day_context(src, MARKET, d, int(r["session"]), reads_overnight=on, reads_0829=b829, rules=rules)
            f = DC.day_flags(src, MARKET, d, reads_overnight=on, reads_0829=b829, rules=rules)
            if int(r[f"void_{c}"]) != int(ctx.void) or str(r[f"why_void_{c}"]) != SEP.join(f.void):
                raise CalendarIdentityError(f"(I-2) {d} {c}: the table says void={r[f'void_{c}']} "
                                            f"({r[f'why_void_{c}']!r}); day_calendar says void={int(ctx.void)} "
                                            f"({SEP.join(f.void)!r})")
            if int(r["prior_void"]) != int(ctx.prior_void) or str(r["why_prior_void"]) != SEP.join(f.prior_void):
                raise CalendarIdentityError(f"(I-2) {d} {c}: prior_void differs from day_calendar's call")
            if int(r["bls"]) != int(ctx.bls) or int(r["fomc"]) != int(ctx.fomc):
                raise CalendarIdentityError(f"(I-2) {d}: bls / fomc differ from day_calendar's call")
            void_days[c] += int(ctx.void)
        prior += int(r["prior_void"])
    h2_void = sorted(d.isoformat() for d, f in src.flags.items() if f["verdict"] == "VOID")
    by_date = {str(r["date"]): r for r in rows}
    missed = [d for d in h2_void if not (by_date[d]["void_overnight"] and by_date[d]["void_overnight_0829"])]
    if missed:
        raise CalendarIdentityError(f"(I-2) H2's VOID days {missed[:3]} are not void in the overnight classes")
    return {"I-1": {"dates": len(dates), "h2_flags_dates": len(h2), "held": True},
            "I-2": {"days": len(rows), "classes": list(CLASSES), "void_days": void_days, "prior_void_days": prior,
                    "h2_void_days": len(h2_void), "held": True}}


# ------------------------------------------------------------------------------------------------------- the loader


@dataclass(frozen=True)
class SearchCalendar:
    """The pinned search calendar as the loader read it."""
    dates: tuple[str, ...]
    calendar_sha256: str              # W42-R1's `calendar_digest(dates)`: what H4's manifest records
    file_sha256: str                  # the CSV's bytes, as its sidecar manifest records them
    rows: tuple[Mapping[str, Any], ...]
    path: str

    def session(self, day: Any) -> int:
        """The day's session ordinal (1 .. N); KeyError for a date that is not a session."""
        return int(self._index()[str(day)[:10]]) + 1

    def sessions_left(self, day: Any) -> int:
        """Sessions left in the search years from `day`, the day itself counted (H4's `obs` before its cap)."""
        return len(self.dates) - self.session(day) + 1

    def _index(self) -> dict[str, int]:
        return {d: i for i, d in enumerate(self.dates)}


def load_search_calendar(path: Path | str | None = None) -> SearchCalendar:
    """The pinned search calendar (default `results/search_calendar.csv`), refused unless its bytes are its sidecar
    manifest's sha256, the manifest records the calendar's digest as recomputed, and the table is the search
    calendar's form (`check_rows`, the full span). Pure: reads the two files, writes nothing."""
    p = Path(path) if path is not None else DEFAULT_PATH
    raw = p.read_bytes()
    side = Path(str(p) + ".manifest.json")
    if not side.is_file():
        raise CalendarRefused(f"{p}: no sidecar manifest beside it; the search calendar is read only with its manifest")
    man = json.loads(side.read_text(encoding="utf-8"))
    sha = hashlib.sha256(raw).hexdigest()
    if man.get("sha256") != sha:
        raise CalendarRefused(f"{p}: sha256 {sha} differs from its manifest's {man.get('sha256')}")
    rows = parse_csv_text(raw.decode("utf-8"))
    dates = tuple(check_rows(rows, require_span=True))
    digest = calendar_digest(dates)
    want = (man.get("parameters") or {}).get("calendar_sha256")
    if not (isinstance(want, str) and _HEX64.fullmatch(want)) or want != digest:
        raise CalendarRefused(f"{p}: the calendar's digest {digest} is not the manifest's calendar_sha256 {want}")
    return SearchCalendar(dates, digest, sha, tuple(rows), str(p))


__all__ = ["SEARCH_START", "SEARCH_END", "CONFIRMATION_START", "RESULT_NAME", "DEFAULT_PATH", "CLASSES", "COLUMNS",
           "DAY_KINDS", "CalendarIdentityError", "CalendarRefused", "SearchCalendar", "calendar_digest", "sha256_file",
           "data_manifest_sha", "guard_date", "build_rows", "check_rows", "to_csv_text", "parse_csv_text", "identities",
           "load_search_calendar"]
