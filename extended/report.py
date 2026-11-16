"""The dispersion report (Q-27; the operator, E-014, E-015): a result file of start rows turned into a page the
operator reads in a few minutes -- the spread over start days of every journey variable, the payouts' sizes and gaps,
the evenness trade-off and the denial ladder -- every number computed from its file and registered for the trace check.

    from extended import report as R
    R.build(R.REPORTS["demo_stage2_u1"])            # -> docs/report/demo_stage2_u1/README.md and its charts
    R.traced_numbers(R.REPORTS["demo_stage2_u1"])   # every number the page prints, as the trace check's entries

`scripts/build_report.py` is the command; `extended/trace.py` registers every page of `REPORTS`, so
`scripts/trace_check.py` recomputes each number from its file and finds it on the page. Importing this module puts the
vendored tree on `sys.path`: import it in a process of its own.

**What it reads.** A result file, through `extended.results.read_result` (its manifest checked first), whose rows are
start records in the form of Stage 2's U1 file (`vendor/stage2/results/user_journey.csv`, section `start`; Stage 2
D-620): one row per design, scenario and start day, with `start_day`, `start_date`, `observed`, `pay_days`,
`first_pass`, `first_payout`, `first_payout_cash`, `spent_before_first_pass`, `spent_before_first_payout`,
`net_month_1..12` and `fees_month_1..12` (`REQUIRED`). A spec (`ReportSpec`) names the rows: `where` (every design),
each design's own `where`, and `base` (the scenario every figure but the ladder reads). Optional columns open more of
the page; without them the page says "not in this file":

* `net_by_session` -- the net cash at the closes 0 .. observed, space-separated (U1's `start_record` `cash - initial`):
  the daily measures and the session-by-session curves. Refused unless it equals the month-end nets.
* `pay_cash` -- every payout's cash, in `pay_days`' order: the size of every payout. Refused unless the payouts by each
  month end equal its net plus its fees.
* the ladder column (`denial`) -- the row's payout-denial level (0, 0.10, 0.25, 0.50): the denial ladder.

**How each figure is read** (a month is 21 sessions, the year 252: U1's `MONTH`, `HORIZON`; percentiles numpy's
linear; a figure at h sessions reads the start days with at least h sessions left, as U1 does):

* first pass and first payout (E-014 (1), (2)): the sessions to it over the start days with 42 (pass) or 126 (payout)
  sessions left, a start day not there by then counted as later and a percentile that lands there shown as "after
  session h" (Stage 2's `customer_journey._days_q`, imported); the cash out of pocket before it (U1's
  `spent_before_*`: the deepest the cash went below the start) over those that got there -- U1's own readings;
* break-even (E-014 (3); daily only): the first session k >= 1 whose closing net is at or above zero (within a
  millionth of a dollar, U1's `TOL`), over the start days with 252 sessions left, unreached counted as later; the
  share of those back within the year whose net later closes below zero; the deepest fall of the net from its running
  high after break-even, in dollars;
* the year's evenness (E-014 (4)), per start day with the whole year left: the share of its twelve months whose net
  change (month 1's from zero) is above zero; the longest run of consecutive months with no payout arriving
  (`pay_days`, month of session d = (d - 1) // 21, as U1's `payout_rhythm`); the standard deviation (ddof 1) of the
  twelve monthly changes; payouts per month (those arriving by session 252, over twelve); the largest month's payout
  cash over the year's (payouts received by a month end = its net + its fees, U1's convention), on start days paid
  more than half a cent in the year;
* payouts: every payout's size (with `pay_cash`) or the first payout's (U1's `cash_p*`); the payout cash of each month
  with one; the sessions between one payout day and the next (same-session payouts are one payout day), pooled over
  the start days with the year left;
* the month-end shares (ahead: net above zero; paid by then; back to break-even by then) on each month's own start
  days, U1's `periodic:share_positive` and `share_by`; **P and S1-S5c by Stage 2's own code**
  (`u_select.scorecard` on `u_select.records_from_start_rows`: nothing re-implemented), P reading months 1-3 on the
  start days with 63 sessions;
* the judged block (E-014: "all starts and the judged block"): the journey table and the scorecard again on the start
  days from `JUDGED_FROM` (2024-01-01) on -- Stage 2 D-621 (4)(b)'s block, `u_select`'s `late`;
* "separate stretches": the start days read over the sessions each spans -- a rough count of non-overlapping histories
  behind a figure, beside it (the effective-sample reading proper is Q-17's).

Every number printed goes through `_Page.num`, which records a `Claim` (label, design, ladder level, the `quantity`
key, the decimals shown): `traced_numbers` turns the claims into `TracedNumber` entries whose recompute derives the
value from the file again (`quantity` on the rows the claim names). The independent check of the measures is
`tests/report_reference.py` (plain Python); the identity against Stage 2's registered U1 readings is
`tests/report_cases.py`'s `stage2` case.

**The journey scorecard page (Q-69).** A second kind of registered page, `JourneySpec` (`journey_scorecard`): Q-17's
readings file and its per-start companion (`scripts/user_beside.py`), composed by `extended/journey_page.py` --
`build`, `traced_numbers` and `compose_text` hand a `JourneySpec` to it. A registered page may name the task that
writes its files (`awaits`); while neither its files nor its page exist it is waiting (`waiting`): it has no number to
trace, the trace check lists it as waiting, `--all` skips it and `--report` refuses it. Q-86's money reading
(`JourneySpec.spend`, `results/user_spend.csv`) adds a section of its own, shown when that file exists and saying it
waits otherwise; the page itself waits only for Q-44's two files.
"""
from __future__ import annotations

import hashlib
import json
import math
import warnings
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Mapping

from extended import ROOT, use_vendored_stage2

use_vendored_stage2()

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended.results import read_manifest, read_result  # noqa: E402
from propedge.reporting.trace import TracedNumber  # noqa: E402
from propedge.research import u_select as S  # noqa: E402
from propedge.research import user_journey as U  # noqa: E402
from propedge.research.customer_journey import _days_q, _q  # noqa: E402

MONTH, MONTHS, YEAR = U.MONTH, U.MONTHS, U.HORIZON          # 21, 12, 252
PASS_WINDOW, PAYOUT_WINDOW = U.PASS_WINDOW, U.PAYOUT_WINDOW  # 42, 126
P_HORIZON = S.P_HORIZON                                      # 63
#: the judged block: the start days from the first session of this year on (Stage 2 D-621 (4)(b), `u_select`'s `late`)
JUDGED_FROM = f"{S.JUDGED_FIRST_YEAR}-01-01"
TABLE_MONTHS = (1, 2, 3, 6, 12)
FAN_PCTS = (10, 25, 50, 75, 90)
TOL = U.TOL                       # a net within a millionth of a dollar of zero is at zero
CENT = 0.005                      # a month's (or a year's) payout cash counts only above half a cent
PATH_COL, CASH_COL = "net_by_session", "pay_cash"
PAGE = "README.md"
REQUIRED = ("start_day", "start_date", "observed", "pay_days", "first_pass", "first_payout", "first_payout_cash",
            "spent_before_first_pass", "spent_before_first_payout",
            *[f"net_month_{k}" for k in range(1, MONTHS + 1)], *[f"fees_month_{k}" for k in range(1, MONTHS + 1)])
#: the columns a design's rows are read from (`u_select.records_from_start_rows` reads them; its pass and funded day
#: lists are left out -- no measure here or in Stage 2's scorecard reads them)
READ_COLS = (*REQUIRED, "first_funded", "net_30", "exact_runs_differing", PATH_COL, CASH_COL)
NAN = float("nan")


class ReportError(ValueError):
    """The file cannot be read as the spec says: refused, never guessed."""


class NotInFile(LookupError):
    """A measure needs a column this file does not hold."""


# ------------------------------------------------------------------------------------------------ the specs


@dataclass(frozen=True)
class Design:
    """One design on the page: `key` (file names, claims), `short` (charts), `label` (plain words), `where` (its
    rows)."""

    key: str
    short: str
    label: str
    where: Mapping[str, Any]


@dataclass(frozen=True)
class ReportSpec:
    """A page: its source file (relative to the repository root), the rows every design reads (`where`), the designs,
    the base case among the scenario columns (`base`), the ladder's column, the labels. `out` defaults to
    docs/report/<name>."""

    name: str
    title: str
    source: str
    designs: tuple[Design, ...]
    where: Mapping[str, Any] = field(default_factory=dict)
    base: Mapping[str, Any] = field(default_factory=dict)
    ladder: str | None = "denial"
    judged_block: bool = True
    demonstration: bool = False
    note: str = ""
    out: str = ""

    @property
    def out_dir(self) -> str:
        return self.out or f"docs/report/{self.name}"

    def design(self, key: str) -> Design:
        for d in self.designs:
            if d.key == key:
                return d
        raise ReportError(f"no design {key!r} in the spec {self.name!r}")


@dataclass(frozen=True)
class JourneySpec:
    """A journey scorecard page (Q-69; `extended/journey_page.py`): Q-17's readings file (`source`, written by
    `writer`: sections identity, scorecard, extra, path, response) and its per-start companion (`starts`), both
    relative to the repository root. `designs`: the file's `design` values (`Design.key`; `where` unused); `r_star`
    the row to beat on P (CHARTER section 3); `awaits` the task that writes the files -- while neither file nor the
    page exists the page waits (`waiting`) and has no number to trace; `limits` E-015's limits (None: the declared
    `journey_page.LIMITS`); `identity_u1` Stage 2's U1 file the verdict view is held to when the page is built ("":
    none). `spend` Q-86's money reading (`scripts/user_spend.py`, `spend_writer`), relative to the root: its section is
    shown when the file exists and says it waits for `spend_awaits` otherwise ("": no such section)."""

    name: str
    title: str
    source: str
    starts: str
    designs: tuple[Design, ...]
    writer: str = "scripts/user_beside.py"
    r_star: str = "p14"
    awaits: str = ""
    limits: tuple | None = None
    identity_u1: str = ""
    spend: str = ""
    spend_writer: str = "scripts/user_spend.py"
    spend_awaits: str = ""
    note: str = ""
    out: str = ""

    @property
    def out_dir(self) -> str:
        return self.out or f"docs/report/{self.name}"

    def design(self, key: str) -> Design:
        for d in self.designs:
            if d.key == key:
                return d
        raise ReportError(f"no design {key!r} in the spec {self.name!r}")


def spec_from_dict(d: Mapping[str, Any]) -> ReportSpec:
    """A spec from plain data (`scripts/build_report.py --spec <file.json>`)."""
    designs = tuple(Design(x["key"], x.get("short", x["key"]), x.get("label", x["key"]), dict(x.get("where", {})))
                    for x in d["designs"])
    return ReportSpec(name=d["name"], title=d.get("title", d["name"]), source=d["source"], designs=designs,
                      where=dict(d.get("where", {})), base=dict(d.get("base", {})), ladder=d.get("ladder", "denial"),
                      demonstration=bool(d.get("demonstration", False)), note=d.get("note", ""), out=d.get("out", ""))


#: the registered pages: `extended/trace.py` traces every number of each (its REPORT_PAGES)
REPORTS: dict[str, ReportSpec | JourneySpec] = {
    "demo_stage2_u1": ReportSpec(
        name="demo_stage2_u1",
        title="Demonstration: how spread out a user's journey is -- P-14 and P-16 on Stage 2's U1 file",
        source="vendor/stage2/results/user_journey.csv",
        where={"section": "start"},
        designs=(
            Design("p14_verdict", "P-14", "P-14, the row to beat (R*): a breakout on half-hour bars, five Topstep "
                   "accounts -- the cautious reading", {"config": "p14", "arm": "verdict"}),
            Design("p16_verdict", "P-16", "P-16: a fair coin picks each trade's side (no signal), on wider stops "
                   "-- the cautious reading", {"config": "p16", "arm": "verdict"}),
        ),
        demonstration=True,
        note="Stage 2's U1 file holds each start day's first pass and first payout, the cash before each and the "
             "month-end nets and fees; it has no daily cash and no payout one by one, so the measures that need them "
             "are shown as \"not in this file\". The as-traded (point) arm is in the same file and not shown: the "
             "charter judges on the cautious reading. This repository's own file of these readings is Q-17's "
             "(`results/user_beside.csv`, not yet written).",
    ),
    "journey_scorecard": JourneySpec(
        name="journey_scorecard",
        title="The user's journey, start day by start day: P-14, P-15 and P-16, and the firm's responses beside",
        source="results/user_beside.csv",
        starts="results/user_beside_starts.csv",
        designs=(
            Design("p14", "P-14", "P-14, the row to beat (R*): a breakout on half-hour bars, five Topstep accounts",
                   {}),
            Design("p15", "P-15", "P-15: a fair coin picks each trade's side (no signal)", {}),
            Design("p16", "P-16", "P-16: the same kind of coin on wider stops", {}),
        ),
        r_star="p14",
        awaits="Q-44",
        identity_u1="vendor/stage2/results/user_journey.csv",
        spend="results/user_spend.csv",
        spend_awaits="Q-86",
    ),
}


def waiting(spec: Any, root: Path | str = ROOT) -> str | None:
    """Why a registered page has no number yet, or None. Only a spec naming the task that writes its files (`awaits`)
    can wait, and only while none of its files and not its page exist: then nothing exists to trace. Once a file or
    the page exists the page is traced in full, and fails the check if it cannot be."""
    task = getattr(spec, "awaits", "")
    if not task:
        return None
    files = [source_path(spec, root)] + ([Path(root) / spec.starts] if isinstance(spec, JourneySpec) else [])
    if any(f.exists() for f in files) or page_path(spec, root).exists():
        return None
    return (f"its file {spec.source} is not written yet ({task} writes it) and the page is not built: no number "
            "exists to trace")


def source_path(spec: ReportSpec, root: Path | str = ROOT) -> Path:
    p = Path(spec.source)
    return p if p.is_absolute() else Path(root) / p


def page_path(spec: ReportSpec, root: Path | str = ROOT) -> Path:
    return Path(root) / spec.out_dir / PAGE


def _rel(p: Path, root: Path | str) -> str:
    try:
        return Path(p).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return Path(p).as_posix()


def read(spec: ReportSpec, root: Path | str = ROOT) -> tuple[pd.DataFrame, Any]:
    """The source file as the trace check reads it (the vendored `read_result`: the manifest first), and its
    manifest."""
    path = source_path(spec, root)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", pd.errors.DtypeWarning)
        df = read_result(path)
    return df, read_manifest(path)


# ------------------------------------------------------------------------------------------------ the rows


def _match(s: pd.Series, want: Any) -> pd.Series:
    if isinstance(want, bool) or not isinstance(want, (int, float)):
        if isinstance(s.dtype, pd.StringDtype):          # text as text; an object column may mix types
            return (s == str(want)).fillna(False).astype(bool)
        return s.astype(str).str.strip() == str(want)
    return (pd.to_numeric(s, errors="coerce") - float(want)).abs() <= 1e-9


def _mask(df: pd.DataFrame, where: Mapping[str, Any]) -> pd.Series:
    m = pd.Series(True, index=df.index)
    for col, want in where.items():
        if col not in df.columns:
            raise ReportError(f"the file has no column {col!r} (a filter of the spec)")
        m &= _match(df[col], want)
    return m


def filters(spec: ReportSpec, design: Design, level: float | None = None) -> dict[str, Any]:
    f = {**spec.where, **design.where, **spec.base}
    if level is not None:
        if not spec.ladder:
            raise ReportError("a ladder level was asked of a spec with no ladder column")
        f[spec.ladder] = float(level)
    return f


def design_rows(spec: ReportSpec, df: pd.DataFrame, key: str, level: float | None = None,
                block: str | None = None) -> pd.DataFrame:
    f = filters(spec, spec.design(key), level)
    rows = df[_mask(df, f)]
    if not len(rows):
        raise ReportError(f"no rows for {key!r} where {_where_text(f)}")
    if block is not None:
        if block != "judged":
            raise ReportError(f"no block {block!r} (the judged block is 'judged')")
        rows = rows[rows["start_date"].astype(str).str[:10] >= JUDGED_FROM]
        if not len(rows):
            raise ReportError(f"no start day of {key!r} in the judged block (from {JUDGED_FROM})")
    return rows


def starts_for(spec: ReportSpec, df: pd.DataFrame, key: str, level: float | None = None,
               block: str | None = None) -> "Starts":
    """The design's start days (at a ladder level, else the base case; all of them, or the judged block's) from the
    file's frame."""
    return Starts.of(design_rows(spec, df, key, level, block))


def ladder_levels(spec: ReportSpec, df: pd.DataFrame, key: str) -> list[float]:
    """The ladder's levels the file holds for the design (the base case's other columns held); none without the
    column."""
    if not spec.ladder or spec.ladder not in df.columns:
        return []
    f = {k: v for k, v in filters(spec, spec.design(key)).items() if k != spec.ladder}
    lv = pd.to_numeric(df.loc[_mask(df, f), spec.ladder], errors="coerce").dropna().unique()
    return sorted(float(x) for x in lv)


def _where_text(f: Mapping[str, Any]) -> str:
    return ", ".join(f"{k} = {v:g}" if isinstance(v, float) else f"{k} = {v}" for k, v in f.items())


def _blank(x: Any) -> bool:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return True
    return str(x).strip() in ("", "nan", "NaN", "None")


def _floats(x: Any) -> np.ndarray:
    return np.zeros(0) if _blank(x) else np.array([float(v) for v in str(x).split()], float)


_CACHE: dict[str, "Starts"] = {}
_CACHE_SIZE = 32


def _fingerprint(rows: pd.DataFrame, cols: list[str]) -> str:
    """The rows' content in those columns, as a sha256: numbers by their bytes, text as written. Two frames read from
    one file give one fingerprint; a cell changed gives another."""
    h = hashlib.sha256(repr(cols).encode())
    for c in cols:
        s = rows[c]
        if pd.api.types.is_numeric_dtype(s.dtype) and not pd.api.types.is_bool_dtype(s.dtype):
            h.update(b"n")
            h.update(np.ascontiguousarray(s.to_numpy(float)).tobytes())
        else:
            h.update(b"s")
            h.update("".join(map(str, s.tolist())).encode("utf-8", "surrogatepass"))
    return h.hexdigest()


class Starts:
    """One design's start days (one scenario), in start order: U1's records (the vendored parse) and the arrays every
    measure reads. `Starts.of(rows)` keeps the last few by the content of their rows, so the trace check's many
    recomputes of one design parse it once."""

    @classmethod
    def of(cls, rows: pd.DataFrame) -> "Starts":
        missing = [c for c in REQUIRED if c not in rows.columns]
        if missing:
            raise ReportError(f"not a file of start rows: no column {', '.join(missing)}")
        cols = [c for c in READ_COLS if c in rows.columns]
        key = _fingerprint(rows, cols)
        st = _CACHE.get(key)
        if st is None:
            st = cls(rows[cols])
            if len(_CACHE) >= _CACHE_SIZE:
                _CACHE.pop(next(iter(_CACHE)))
            _CACHE[key] = st
        return st

    def __init__(self, rows: pd.DataFrame):
        days = pd.to_numeric(rows["start_day"], errors="coerce")
        if days.isna().any():
            raise ReportError("a start row without its start day")
        if days.duplicated().any():
            raise ReportError(f"{int(days.duplicated().sum())} start days appear more than once among the design's "
                              "rows: the rows mix scenarios -- name the scenario columns (the ladder's among them) in "
                              "the spec's `base`")
        rows = rows.iloc[np.argsort(days.to_numpy(float), kind="stable")]
        recs, alt = S.records_from_start_rows(rows.to_dict("records"))
        if alt:
            raise ReportError(f"{len(alt)} start days were read by Stage 2 from exact-length runs this file does not "
                              "hold (exact_runs_differing): their readings cannot be reproduced from it")
        self.records = recs
        self.V = U.Views(recs)
        t = self.V.base
        self.n = len(t)
        self.day = t["start_day"].to_numpy(int)
        self.date = t["start_date"].astype(str).to_numpy()
        self.obs = t["observed"].to_numpy(int)
        self.first_pass = t["first_pass"].to_numpy(float)
        self.first_payout = t["first_payout"].to_numpy(float)
        self.first_payout_cash = t["first_payout_cash"].to_numpy(float)
        self.spent_pass = t["spent_before_first_pass"].to_numpy(float)
        self.spent_payout = t["spent_before_first_payout"].to_numpy(float)
        self.net = t[[f"net_month_{k}" for k in range(1, MONTHS + 1)]].to_numpy(float)
        self.fees = t[[f"fees_month_{k}" for k in range(1, MONTHS + 1)]].to_numpy(float)
        self.pays = [np.asarray(p, int) for p in t["pays"]]
        self.path = self._paths(rows[PATH_COL]) if PATH_COL in rows.columns else None
        self.cash = [_floats(x) for x in rows[CASH_COL]] if CASH_COL in rows.columns else None
        self._check()

    def _paths(self, col: pd.Series) -> np.ndarray:
        P = np.full((self.n, YEAR + 1), np.nan)
        for i, x in enumerate(col):
            v = _floats(x)
            if len(v) != self.obs[i] + 1:
                raise ReportError(f"start day {self.day[i]}: its daily net holds {len(v)} closes for "
                                  f"{self.obs[i]} sessions observed (closes 0 .. observed)")
            k = min(len(v), YEAR + 1)
            P[i, :k] = v[:k]
        return P

    def _check(self) -> None:
        if self.path is not None:
            for m in range(1, MONTHS + 1):
                d = MONTH * m
                ok = self.obs >= d
                x, y = self.path[ok, d], self.net[ok, m - 1]
                bad = ~(np.abs(x - y) <= TOL + 1e-9 * np.abs(y))
                if bad.any():
                    raise ReportError(f"start day {self.day[ok][bad][0]}: its daily net at session {d} is not its "
                                      f"month-{m} net")
        if self.cash is not None:
            for i in range(self.n):
                c, p = self.cash[i], self.pays[i]
                if len(c) != len(p):
                    raise ReportError(f"start day {self.day[i]}: {len(c)} payout amounts for {len(p)} payout days")
                for m in range(1, MONTHS + 1):
                    d = MONTH * m
                    if self.obs[i] < d:
                        break
                    got, want = float(c[p <= d].sum()), self.net[i, m - 1] + self.fees[i, m - 1]
                    if not abs(got - want) <= 1e-5 + 1e-9 * abs(want):
                        raise ReportError(f"start day {self.day[i]}: its payouts by session {d} add to {got:.6f}, "
                                          f"its month-{m} net and fees to {want:.6f}")

    # -- what the measures read
    def need_path(self) -> np.ndarray:
        if self.path is None:
            raise NotInFile(f"the daily net cash (column {PATH_COL!r})")
        return self.path

    def need_cash(self) -> list[np.ndarray]:
        if self.cash is None:
            raise NotInFile(f"each payout's cash (column {CASH_COL!r})")
        return self.cash

    @cached_property
    def year_ok(self) -> np.ndarray:
        return (self.obs >= YEAR) & np.isfinite(self.net).all(1) & np.isfinite(self.fees).all(1)

    @cached_property
    def received(self) -> np.ndarray:
        return self.net + self.fees

    @cached_property
    def paid_month(self) -> np.ndarray:
        return np.diff(np.concatenate([np.zeros((self.n, 1)), self.received], 1), axis=1)

    @cached_property
    def change(self) -> np.ndarray:
        return np.diff(np.concatenate([np.zeros((self.n, 1)), self.net], 1), axis=1)

    @cached_property
    def counts(self) -> np.ndarray:
        c = np.zeros((self.n, MONTHS), int)
        for i, p in enumerate(self.pays):
            p = p[(p >= 1) & (p <= YEAR)]
            np.add.at(c[i], (p - 1) // MONTH, 1)
        return c

    def _year(self, v: np.ndarray) -> np.ndarray:
        return np.where(self.year_ok, v, np.nan)

    @cached_property
    def gain_share(self) -> np.ndarray:
        return self._year((self.change > 0).mean(1))

    @cached_property
    def dry_run(self) -> np.ndarray:
        out = np.zeros(self.n)
        for i, row in enumerate(self.counts):
            best = run = 0
            for c in row:
                run = run + 1 if c == 0 else 0
                best = max(best, run)
            out[i] = best
        return self._year(out)

    @cached_property
    def monthly_sd(self) -> np.ndarray:
        with np.errstate(invalid="ignore"):
            return self._year(self.change.std(1, ddof=1))

    @cached_property
    def per_month(self) -> np.ndarray:
        return self._year(self.counts.sum(1) / MONTHS)

    @cached_property
    def largest_share(self) -> np.ndarray:
        tot = self.received[:, -1]
        with np.errstate(invalid="ignore", divide="ignore"):
            v = np.where(tot > CENT, self.paid_month.max(1) / tot, np.nan)
        return self._year(v)

    @cached_property
    def be(self) -> np.ndarray:
        P = self.need_path()
        with np.errstate(invalid="ignore"):
            hit = P[:, 1:] >= -TOL
        first = np.argmax(hit, axis=1) + 1.0
        return np.where(hit.any(1), first, np.nan)

    @cached_property
    def fell(self) -> np.ndarray:
        P, b = self.need_path(), self.be
        out = np.zeros(self.n, bool)
        for i in np.flatnonzero(np.isfinite(b)):
            with np.errstate(invalid="ignore"):
                out[i] = bool((P[i, int(b[i]) + 1:] < -TOL).any())
        return out

    @cached_property
    def fall(self) -> np.ndarray:
        P, b = self.need_path(), self.be
        out = np.full(self.n, np.nan)
        for i in np.flatnonzero(np.isfinite(b)):
            x = P[i, int(b[i]):]
            x = x[np.isfinite(x)]
            out[i] = float(np.max(np.maximum.accumulate(x) - x))
        return out

    @cached_property
    def scorecard(self) -> dict[str, dict[str, Any]]:
        """Stage 2's own scorecard (P and S1-S5c, D-621) on these start days (`u_select.scorecard`)."""
        return S.scorecard(self.records)


# ------------------------------------------------------------------------------------------------ the measures


@dataclass(frozen=True)
class Measure:
    """A distribution over start days the page shows: its plain words, its unit, which start days it reads, the column
    it needs (if optional), whether it pools many values a start day."""

    name: str
    label: str
    kind: str
    over: str
    needs: str | None = None
    pooled: bool = False


JOURNEY: tuple[Measure, ...] = (
    Measure("pass_days", "Sessions until the first passed evaluation", "sessions",
            "start days with 42 sessions left (one not passed by then counts as later)"),
    Measure("pass_cash", "Cash out of pocket before the first pass ($)", "dollars",
            "start days that passed within 42 sessions"),
    Measure("payout_days", "Sessions until the first payout arrives", "sessions",
            "start days with 126 sessions left (one not paid by then counts as later)"),
    Measure("payout_cash", "Cash out of pocket before the first payout ($)", "dollars",
            "start days paid within 126 sessions"),
    Measure("breakeven_days", "Sessions until net cash is back to zero (break-even)", "sessions",
            "start days with 252 sessions left (one not back by then counts as later)", needs=PATH_COL),
    Measure("breakeven_fall", "Deepest fall in net cash after break-even ($)", "dollars",
            "start days back to break-even within 252 sessions", needs=PATH_COL),
    Measure("net_3", "Net cash at the end of month 3 ($)", "dollars", "start days with 63 sessions left"),
    Measure("net_12", "Net cash at the end of month 12 ($)", "dollars", "start days with 252 sessions left"),
    Measure("gain_months", "Share of the year's months with a net gain", "percent",
            "start days with 252 sessions left"),
    Measure("dry_months", "Longest run of months without a payout (months)", "months",
            "start days with 252 sessions left"),
    Measure("monthly_spread", "How much the monthly net change swings (standard deviation, $)", "dollars",
            "start days with 252 sessions left"),
    Measure("payouts_per_month", "Payouts per month", "ratio", "start days with 252 sessions left"),
    Measure("largest_month", "Largest single month's share of the year's payouts", "percent",
            "start days paid in the year (252 sessions left)"),
)
PAYOUTS: tuple[Measure, ...] = (
    Measure("payout_size", "Size of each payout ($)", "dollars", "payouts", needs=CASH_COL, pooled=True),
    Measure("first_payout_size", "Size of the first payout ($)", "dollars", "start days paid within 126 sessions"),
    Measure("month_payout", "Payout cash received in a month, months with a payout ($)", "dollars",
            "months with a payout", pooled=True),
    Measure("payout_gap", "Sessions between one payout day and the next", "sessions", "gaps between payout days",
            pooled=True),
)
BY_NAME = {m.name: m for m in JOURNEY + PAYOUTS}

#: the scorecard's lines in plain words (CHARTER section 2; Stage 2 D-621): key -> (words, unit)
SCORE_WORDS: dict[str, tuple[str, str]] = {
    "P": ("Start days ahead, averaged over months 1, 2 and 3 -- the primary measure", "percent"),
    "S1": ("Cash spent before the first payout, high end (p90): the bankroll a user needs", "dollars"),
    "S3a": ("Start days paid within a month (by session 21)", "percent"),
    "S3b": ("Sessions to the first payout, high end (p90)", "sessions"),
    "S3c": ("Payouts received per dollar of fees by month 3, all start days pooled", "ratio"),
    "S4a": ("Start days ahead at month 6", "percent"),
    "S4b": ("Start days ahead at month 12", "percent"),
    "S5a": ("Net cash at month 3 of the unlucky tenth of start days (p10)", "dollars"),
    "S5b": ("Longest wait between payouts within 126 sessions, high end (p90)", "sessions"),
    "S5c": ("How concentrated month 6's money is: the best quarter of start days' share of the total", "percent"),
}


@dataclass(frozen=True)
class Dist:
    values: np.ndarray
    starts: int                 # the start days read
    days_last: int | None       # a days-to-event reading: unreached counts as later than this session
    window: int                 # the sessions each start day spans for it
    pooled: bool = False

    @property
    def n(self) -> int:
        return len(self.values) if self.pooled else self.starts


def dist(st: Starts, name: str) -> Dist:
    """The values a distribution reads (see the module's docstring for each)."""
    if name in ("pass_days", "pass_cash"):
        el = st.obs >= PASS_WINDOW
        if name == "pass_days":
            return Dist(st.first_pass[el], int(el.sum()), PASS_WINDOW, PASS_WINDOW)
        r = el & np.isfinite(st.first_pass) & (st.first_pass <= PASS_WINDOW)
        return Dist(st.spent_pass[r], int(r.sum()), None, PASS_WINDOW)
    if name in ("payout_days", "payout_cash", "first_payout_size"):
        el = st.obs >= PAYOUT_WINDOW
        if name == "payout_days":
            return Dist(st.first_payout[el], int(el.sum()), PAYOUT_WINDOW, PAYOUT_WINDOW)
        r = el & np.isfinite(st.first_payout) & (st.first_payout <= PAYOUT_WINDOW)
        x = st.spent_payout if name == "payout_cash" else st.first_payout_cash
        return Dist(x[r], int(r.sum()), None, PAYOUT_WINDOW)
    if name.startswith("net_"):
        m = int(name.split("_")[1])
        x = st.net[:, m - 1]
        el = (st.obs >= MONTH * m) & np.isfinite(x)
        return Dist(x[el], int(el.sum()), None, MONTH * m)
    if name == "breakeven_days":
        st.need_path()
        el = st.obs >= YEAR
        return Dist(st.be[el], int(el.sum()), YEAR, YEAR)
    if name == "breakeven_fall":
        st.need_path()
        r = (st.obs >= YEAR) & np.isfinite(st.be)
        return Dist(st.fall[r], int(r.sum()), None, YEAR)
    per_start = {"gain_months": "gain_share", "dry_months": "dry_run", "monthly_spread": "monthly_sd",
                 "payouts_per_month": "per_month"}
    y = st.year_ok
    if name in per_start:
        return Dist(getattr(st, per_start[name])[y], int(y.sum()), None, YEAR)
    if name == "largest_month":
        v = st.largest_share[y]
        v = v[np.isfinite(v)]
        return Dist(v, len(v), None, YEAR)
    if name == "payout_size":
        cash = st.need_cash()
        parts = [cash[i][st.pays[i] <= YEAR] for i in np.flatnonzero(y)]
        return Dist(np.concatenate(parts) if parts else np.zeros(0), int(y.sum()), None, YEAR, pooled=True)
    if name == "month_payout":
        v = st.paid_month[y].ravel()
        return Dist(v[v > CENT], int(y.sum()), None, YEAR, pooled=True)
    if name == "payout_gap":
        parts = [np.diff(np.unique(st.pays[i][st.pays[i] <= YEAR])).astype(float) for i in np.flatnonzero(y)]
        return Dist(np.concatenate(parts) if parts else np.zeros(0), int(y.sum()), None, YEAR, pooled=True)
    raise KeyError(name)


def quantity(st: Starts, key: str) -> float:
    """One number of the page from the design's start days. Keys: `rows`; `dist:<measure>:<p10|p25|p50|p75|p90|p5|p95
    |n|starts|stretch>`; `share:<ahead|paid|breakeven>:<month>` and `share_n:...` (its start days);
    `share:fell_back`, `share_n:fell_back`; `score:<P|S1|...>` and `score_n:...` (Stage 2's scorecard). A blank (no
    start day to read, or a days percentile beyond its window) is NaN; a measure needing an absent column raises
    `NotInFile`."""
    if key == "rows":
        return float(st.n)
    kind, *rest = key.split(":")
    if kind == "dist":
        name, stat = rest
        d = dist(st, name)
        if stat == "n":
            return float(d.n)
        if stat == "starts":
            return float(d.starts)
        if stat == "stretch":
            return d.starts / d.window
        p = float(stat[1:])
        if d.days_last is not None:
            return _days_q(d.values, d.days_last, p) if len(d.values) else NAN
        return _q(d.values[np.isfinite(d.values)], p)
    if kind in ("share", "share_n"):
        if rest[0] == "fell_back":
            st.need_path()
            el = (st.obs >= YEAR) & np.isfinite(st.be)
            n = int(el.sum())
            return float(n) if kind == "share_n" else (float(st.fell[el].mean()) if n else NAN)
        name, m = rest[0], int(rest[1])
        d = MONTH * m
        if name == "ahead":
            x = st.net[:, m - 1]
            el, hit = (st.obs >= d) & np.isfinite(x), x > 0
        elif name == "paid":
            el, hit = st.obs >= d, np.isfinite(st.first_payout) & (st.first_payout <= d)
        elif name == "breakeven":
            st.need_path()
            el, hit = st.obs >= d, np.isfinite(st.be) & (st.be <= d)
        else:
            raise KeyError(key)
        n = int(el.sum())
        return float(n) if kind == "share_n" else (float(hit[el].mean()) if n else NAN)
    if kind in ("score", "score_n"):
        e = st.scorecard[rest[0]]
        return float(e["value"] if kind == "score" else e["n"])
    raise KeyError(key)


def blank_reason(st: Starts, key: str) -> str | None:
    """Why a number is not printed: `not_in_file`, `beyond` (a days percentile past its window), `none` (nothing to
    read); None when it is a number."""
    try:
        v = quantity(st, key)
    except NotInFile:
        return "not_in_file"
    if math.isfinite(v):
        return None
    if key.startswith("dist:"):
        name, stat = key.split(":")[1:]
        d = dist(st, name)
        if d.n and d.days_last is not None and stat.startswith("p"):
            return "beyond"
    return "none"


# ------------------------------------------------------------------------------------------------ the page


@dataclass(frozen=True)
class Claim:
    """One number the page prints: what it is, which rows it reads (design, ladder level), the `quantity` key, and how
    it is printed (`decimals`, `as_percent`, `printed`: the number as it appears, without its unit)."""

    label: str
    design: str
    level: float | None
    what: str
    decimals: int
    as_percent: bool
    printed: str
    block: str | None = None


#: unit -> (decimals shown, shown as a percentage)
KINDS = {"sessions": (0, False), "dollars": (0, False), "percent": (1, True), "months": (1, False),
         "count": (0, False), "ratio": (2, False), "stretch": (1, False)}


def _fmt(v: float, kind: str) -> str:
    if kind == "sessions":
        return f"{v:,.0f}" if abs(v - round(v)) < 1e-9 else f"{v:,.1f}"
    if kind == "dollars":
        s = f"{v:,.0f}"
        return "0" if s == "-0" else s
    if kind == "percent":
        s = f"{100 * v:.1f}"
        return "0.0" if s == "-0.0" else s
    if kind == "count":
        return f"{int(round(v)):,d}"
    if kind in ("months", "stretch"):
        return f"{v:,.1f}"
    return f"{v:,.2f}"


class _Page:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.claims: list[Claim] = []

    def add(self, *lines: str) -> None:
        self.lines.extend(lines)

    def num(self, v: float, kind: str, label: str, design: str, what: str, level: float | None = None,
            block: str | None = None) -> str:
        if not math.isfinite(v):
            raise ValueError(f"{label}: a blank is not a number to print")
        s = _fmt(v, kind)
        dec, pct = KINDS[kind]
        self.claims.append(Claim(label, design, level, what, dec, pct, s, block))
        return s + ("%" if pct else "")

    def q(self, st: Starts, key: str, kind: str, label: str, design: str, level: float | None = None,
          block: str | None = None) -> str:
        why = blank_reason(st, key)
        if why == "not_in_file":
            return "not in this file"
        if why == "beyond":
            return f"after session {dist(st, key.split(':')[1]).days_last}"
        if why == "none":
            return "none to read"
        return self.num(quantity(st, key), kind, label, design, key, level, block)

    def text(self) -> str:
        return "\n".join(self.lines).rstrip() + "\n"


@dataclass
class Chart:
    file: str
    kind: str
    payload: dict


@dataclass
class Composed:
    text: str
    claims: list[Claim]
    charts: list[Chart]


@dataclass
class Built:
    page: Path
    charts: list[Path]
    claims: list[Claim]


def _have_matplotlib() -> bool:
    """Whether matplotlib is installed (found, not imported: the trace check's listing of a page's numbers draws
    nothing). Without it the page is tables only and says so."""
    import importlib.util

    return importlib.util.find_spec("matplotlib") is not None


def _pyplot():
    """matplotlib's pyplot on the Agg backend, or None when it cannot be loaded."""
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt

        return plt
    except Exception:  # noqa: BLE001 -- any failure to load it means no charts, said on the page
        return None


def _lvl(level: float) -> str:
    return f"{100 * level:g}%"


def compose(spec: ReportSpec, df: pd.DataFrame, manifest: Any, *, root: Path | str = ROOT) -> Composed:
    """The page's text, the numbers it prints (claims) and the charts it shows, from the file's frame."""
    P = _Page()
    src = _rel(source_path(spec, root), root)
    sha = str(manifest.sha256)[:12]
    commit = str(manifest.git_commit)
    base = {d.key: starts_for(spec, df, d.key) for d in spec.designs}
    levels = {d.key: ladder_levels(spec, df, d.key) for d in spec.designs}
    has_path = all(st.path is not None for st in base.values())
    has_cash = all(st.cash is not None for st in base.values())
    has_ladder = bool(spec.ladder) and spec.ladder in df.columns
    plt_ok = _have_matplotlib()
    charts: list[Chart] = []

    def caption(d: Design | None, extra: str = "") -> str:
        rows = _where_text(filters(spec, d)) if d is not None else _where_text({**spec.where, **spec.base})
        return f"*Source: `{src}`, rows where {rows}; sha256 `{sha}`, manifest checked before reading.{extra}*"

    def image(file: str, alt: str, kind: str, payload: dict, cap: str) -> None:
        if plt_ok:
            charts.append(Chart(file, kind, payload))
            P.add(f"![{alt}]({file})", "", cap, "")
        else:
            P.add("*Chart not drawn: matplotlib is not installed here; the tables carry the figures.*", "", cap, "")

    # -- the head
    P.add(f"# {spec.title}", "")
    if spec.demonstration:
        P.add("> **DEMONSTRATION on Stage 2's file.** This page shows how the report reads a result file. Its figures "
              "are computed from the start rows already in that file; no result of this repository is on it, and "
              "nothing is chosen from it.", ">")
    if bool(getattr(manifest, "exploratory", False)):
        P.add("> **EXPLORATORY.** The file's manifest marks it exploratory: its readings were not declared as a test "
              "before they were run. They are reported apart from any declared result and decide nothing.", ">")
    if commit.endswith("-dirty") or bool(getattr(manifest, "git_dirty", False)):
        P.add(f"> **NOT CITABLE.** The file was written from a tree with uncommitted changes (`{commit}`); a result is "
              "citable only when written from a clean checkout of a named commit.", ">")
    if P.lines[-1] == ">":
        P.lines.pop()
        P.add("")
    decl = f"declared under {manifest.prereg_id}" if getattr(manifest, "prereg_id", None) else "no declaration named"
    count = getattr(manifest, "variant_count", None)
    P.add(f"**Source.** `{src}`, its rows where {_where_text(spec.where) or 'all rows'}; the manifest checked before "
          f"reading (sha256 `{sha}`); written by `{manifest.script}` at commit `{commit[:12]}` on "
          f"{str(manifest.timestamp)[:10]}; {decl}"
          + (f"; variant count in its manifest: {count}" if count is not None else "") + ".",
          "**Built by** `python scripts/build_report.py "
          + (f"--report {spec.name}" if spec.name in REPORTS else "--spec <its JSON spec>")
          + "` (`extended/report.py`). The page is rebuilt from the file, never edited by hand.", "")
    if spec.note:
        P.add(spec.note, "")

    P.add("## How to read this page", "",
          "- **A start day** is one simulated user who begins on that trading day with fresh accounts; the design's "
          "trades are replayed in historical order. Every figure is a spread across start days -- what different "
          "users would have lived -- not one user's luck.",
          "- **Net cash** is payouts received less every fee paid, so far. **Ahead** means net cash above zero; "
          "**break-even** means net cash back to zero or above.",
          "- **Low end, middle, high end** are the 10th percentile, the median and the 90th percentile across start "
          "days: one start day in ten is at or below the low end, half are below the middle, one in ten is at or "
          "above the high end. For sessions and cash spent, the high end is the slow, expensive tenth; for net cash, "
          "the low end is the unlucky tenth.",
          "- A **month** is 21 trading sessions; the year is 252. A figure read at a month reads only the start days "
          "with that much history after them, so later start days drop out of the later figures.",
          "- **The cautious reading** (Stage 2's verdict arm): every trade's result moved down to the one-sided 95 % "
          "lower bound of what its history supports -- the reading the charter judges on.",
          "- **Start days overlap.** Two start days a week apart share most of their trades, so a thousand start days "
          "are far fewer independent histories. \"Separate stretches\" divides the start days read by the sessions "
          "each one spans: a rough count of non-overlapping histories behind the figure.", "")

    P.add("## What this page does not model", "",
          "Not modelled (CHARTER section 2): a user who stops when their own money runs out -- the replay keeps paying "
          "fees, so there is no ruin figure; the user's time; taxes.", "",
          "Assumed, as Stage 2's engine models them: payouts never denied in every figure outside the denial ladder "
          "(Stage 2 D-234); the firm's Responsible Trading placement off (Stage 2 D-289); fills, the payout lag and "
          "the spacing of payouts as the engine models them, not as observed; the firm's rules as Stage 2's verified "
          "ledger holds them (`vendor/stage2/config/rules.yaml`).", "")
    P.add("## Not on this page", "",
          "- the frontier of designs on P, S1, S3a and S5a, and the menu read under limits on what a user feels (the "
          "limits are not yet approved: E-015 (2));",
          "- Stage 2's long-run gate (growth on the required bankroll at the bound): it is in each design's gate file;",
          "- each figure's uncertainty from the effective number of independent starts, and the share of a result "
          "that is the start day's luck rather than the design (Q-17's readings).", "")
    missing = []
    if not has_path:
        missing.append("- **the daily net cash** (column `net_by_session`): sessions to break-even, the share that "
                       "falls back below it, the deepest fall after it and the session-by-session curves are shown as "
                       "\"not in this file\"; the net-cash bands and the break-even curve are read at month ends only;")
    if not has_cash:
        missing.append("- **each payout's cash** (column `pay_cash`): the size of every payout is not shown, only the "
                       "first payout's;")
    if not has_ladder:
        missing.append(f"- **the payout-denial ladder: not in this file** (column `{spec.ladder or 'denial'}`): every "
                       "figure has payouts never denied.")
    if missing:
        P.add("## Not in this file", "", *missing, "")

    # -- each design
    for d in spec.designs:
        st = base[d.key]
        k = d.key
        P.add(f"## {d.label if d.label.startswith(d.short) else f'{d.short}: {d.label}'}", "",
              f"{P.num(st.n, 'count', f'{d.short} | start days in the file', k, 'rows')} start days, "
              f"{st.date[0]} to {st.date[-1]}. Each figure reads the start days with enough sessions left for it "
              "(\"read over\").", "")

        judged = None
        if spec.judged_block:
            try:
                judged = starts_for(spec, df, k, None, "judged")
            except ReportError:
                judged = None

        def journey(s_: Starts, tag: str, block: str | None) -> None:
            P.add("| What it measures | Low end (p10) | Middle (median) | High end (p90) | Start days read | "
                  "Separate stretches (about) | Read over |", "|---|---:|---:|---:|---:|---:|---|")
            for m in JOURNEY:
                try:
                    dd = dist(s_, m.name)
                except NotInFile:
                    P.add(f"| {m.label} | not in this file | not in this file | not in this file | not in this file "
                          f"| not in this file | {m.over} |")
                    continue
                cells = [P.q(s_, f"dist:{m.name}:p{p}", m.kind, f"{tag} | {m.label} | p{p}", k, None, block)
                         for p in (10, 50, 90)]
                n = (P.num(dd.n, "count", f"{tag} | {m.label} | start days read", k, f"dist:{m.name}:n", None,
                           block) if dd.n else "0")
                stretch = (P.num(dd.starts / dd.window, "stretch", f"{tag} | {m.label} | separate stretches", k,
                                 f"dist:{m.name}:stretch", None, block) if dd.starts else "0")
                P.add(f"| {m.label} | {' | '.join(cells)} | {n} | {stretch} | {m.over} |")
            P.add("", "*\"After session h\": more than a tenth (or half) of the start days had not got there within h "
                  "sessions. \"None to read\": no start day to read.*", "")

        P.add("### The journey, start day by start day", "")
        journey(st, d.short, None)
        if spec.judged_block:
            P.add("### The same on the judged block", "")
            if judged is None:
                P.add(f"The judged block (the start days from {JUDGED_FROM} on; Stage 2 D-621 (4)(b)): none in this "
                      "file.", "")
            else:
                nj = P.num(judged.n, "count", f"{d.short} judged block | start days", k, "rows", None, "judged")
                P.add(f"The judged block is the start days from {JUDGED_FROM} on (Stage 2 D-621 (4)(b)), the block a "
                      f"design is judged on: {nj} of them. Its later start days have less history after them, so its "
                      "longer readings rest on few separate stretches.", "")
                journey(judged, f"{d.short} judged block", "judged")

        P.add("### Month by month", "", "| | " + " | ".join(f"Month {m}" for m in TABLE_MONTHS) + " |",
              "|---|" + "---:|" * len(TABLE_MONTHS))
        for name, words in (("ahead", "Ahead: net cash above zero"), ("paid", "Paid at least once by then"),
                            ("breakeven", "Back to break-even at least once by then")):
            cells = []
            for m in TABLE_MONTHS:
                try:
                    v = quantity(st, f"share:{name}:{m}")
                except NotInFile:
                    cells.append("not in this file")
                    continue
                cells.append(P.num(v, "percent", f"{d.short} | {words} | month {m}", k, f"share:{name}:{m}")
                             if math.isfinite(v) else "none to read")
            P.add(f"| {words} | " + " | ".join(cells) + " |")
        cells = [P.num(quantity(st, f"share_n:ahead:{m}"), "count", f"{d.short} | start days read | month {m}", k,
                       f"share_n:ahead:{m}") for m in TABLE_MONTHS]
        P.add("| Start days read | " + " | ".join(cells) + " |", "")
        p = quantity(st, "score:P")
        if math.isfinite(p):
            P.add(f"**P**, the share of start days ahead averaged over months 1, 2 and 3 on the same start days (the "
                  f"{P.num(quantity(st, 'score_n:P'), 'count', f'{d.short} | P | start days read', k, 'score_n:P')} "
                  f"with three months left): **{P.num(p, 'percent', f'{d.short} | P', k, 'score:P')}**. It can "
                  "differ a little from the mean of the first three shares above, which each read their own start "
                  "days.", "")
        try:
            fb = quantity(st, "share:fell_back")
            nb = quantity(st, "share_n:fell_back")
            if nb:
                back = P.num(nb, "count", f"{d.short} | back to break-even within the year", k, "share_n:fell_back")
                fell = P.num(fb, "percent", f"{d.short} | fell back below zero after break-even", k,
                             "share:fell_back")
                P.add(f"Of the {back} start days back to break-even within the year, {fell} fell below zero again "
                      "later in the year.", "")
            else:
                P.add("No start day was back to break-even within the year.", "")
        except NotInFile:
            P.add("The share that falls back below zero after break-even: not in this file (it needs the daily net "
                  "cash).", "")

        P.add("### The scorecard: P never alone", "",
              "The primary measure P beside the guarded measures (CHARTER section 2), by Stage 2's own code "
              "(`u_select.scorecard`).", "",
              "| Measure | What it is | All start days | Start days read |"
              + (" Judged block | Start days read |" if judged is not None else "") + " Better when |",
              "|---|---|---:|---:|" + ("---:|---:|" if judged is not None else "") + "---|")
        for key, (words, kind) in SCORE_WORDS.items():
            cells = []
            for s_, tag, block in ((st, d.short, None), (judged, f"{d.short} judged block", "judged")):
                if s_ is None:
                    continue
                v, n = quantity(s_, f"score:{key}"), quantity(s_, f"score_n:{key}")
                cells.append(P.num(v, kind, f"{tag} | {key}", k, f"score:{key}", None, block) if math.isfinite(v)
                             else "none to read")
                cells.append(P.num(n, "count", f"{tag} | {key} | start days read", k, f"score_n:{key}", None, block)
                             if n else "0")
            P.add(f"| {key} | {words} | " + " | ".join(cells) + f" | {S.BY_KEY[key].direction} |")
        P.add("")

        P.add("### Net cash over the first year", "")
        n1, n12 = quantity(st, "dist:net_1:n"), quantity(st, "dist:net_12:n")
        extra = (f" Each point reads the start days with that many sessions left: "
                 f"{P.num(n1, 'count', f'{d.short} | start days read | month 1', k, 'dist:net_1:n')} at month 1, "
                 f"{P.num(n12, 'count', f'{d.short} | start days read | month 12', k, 'dist:net_12:n')} at month 12."
                 if n1 and n12 else "")
        image(f"fan_{k}.png", f"Net cash by session for {d.short}: the middle start day and the bands holding half "
              "and eight in ten of the start days", "fan", {"design": k}, caption(d, extra))

        P.add("### Payouts", "",
              "| What | Low end (p10) | Middle (median) | High end (p90) | Read over |", "|---|---:|---:|---:|---|")
        for m in PAYOUTS:
            try:
                dd = dist(st, m.name)
            except NotInFile:
                P.add(f"| {m.label} | not in this file | not in this file | not in this file | every one of the "
                      f"year's {m.over} |")
                continue
            cells = [P.q(st, f"dist:{m.name}:p{p}", m.kind, f"{d.short} | {m.label} | p{p}", k) for p in (10, 50, 90)]
            n = (P.num(dd.n, "count", f"{d.short} | {m.label} | {'count' if m.pooled else 'start days read'}", k,
                       f"dist:{m.name}:n") if dd.n else "0")
            if m.pooled:
                starts = (P.num(dd.starts, "count", f"{d.short} | {m.label} | start days", k, f"dist:{m.name}:starts")
                          if dd.starts else "0")
                over = f"{n} {m.over}, from {starts} start days with 252 sessions left"
            else:
                over = f"{n} {m.over}"
            P.add(f"| {m.label} | {' | '.join(cells)} | {over} |")
        P.add("", "*Payouts arriving on the same session count as one payout day for the gaps.*", "")
        image(f"payouts_{k}.png", f"Payouts for {d.short}: their sizes, the gaps between payout days, and the largest "
              "month's share of the year's payouts", "payouts", {"design": k}, caption(d))

        P.add("### Payout denial", "")
        if levels[k]:
            P.add("The same design with each payout withheld with the probability on the left (the engine's model: the "
                  "payout withheld and that account closed).", "",
                  "| Payout denial | P | Ahead at month 3 | Net cash at month 3, middle ($) | Paid within 126 "
                  "sessions | Payouts per fee dollar by month 3 (S3c) | Largest month's share, middle |",
                  "|---|---:|---:|---:|---:|---:|---:|")
            for lv in levels[k]:
                sl = starts_for(spec, df, k, lv)
                tag = f"{d.short} at {_lvl(lv)} denial"
                cells = [P.q(sl, "score:P", "percent", f"{tag} | P", k, lv),
                         P.q(sl, "share:ahead:3", "percent", f"{tag} | ahead at month 3", k, lv),
                         P.q(sl, "dist:net_3:p50", "dollars", f"{tag} | net cash at month 3, middle", k, lv),
                         P.q(sl, "share:paid:6", "percent", f"{tag} | paid within 126 sessions", k, lv),
                         P.q(sl, "score:S3c", "ratio", f"{tag} | S3c", k, lv),
                         P.q(sl, "dist:largest_month:p50", "percent", f"{tag} | largest month's share, middle", k, lv)]
                P.add(f"| {_lvl(lv)} | " + " | ".join(cells) + " |")
            P.add("")
        else:
            P.add("The payout-denial ladder: not in this file. Every figure above has payouts never denied.", "")

    # -- side by side
    P.add("## The designs side by side", "", "### Back to break-even", "")
    image("breakeven.png", "The share of start days at or above break-even, session by session, for each design",
          "breakeven", {}, caption(None))
    P.add("The solid lines: the share of start days at or above break-even at that session. "
          + ("The dashed lines: the share back at break-even at least once by then; the gap between the two is start "
             "days that fell back." if has_path else "Read at month ends only: the file has no daily net cash."), "")
    P.add("### Evenness against being ahead", "")
    image("tradeoff.png", "Each design placed by the share of start days ahead (P) against two measures of how even "
          "the path is", "tradeoff", {}, caption(None))
    P.add("Each point is one design. Higher is more start days ahead (P). On the left, further right is a more even "
          "path (more of the year's months with a net gain); on the right, further left is more even (a smaller "
          "largest month). The chart shows the trade-off; it does not choose: designs are compared by limits first, "
          "then the best inside them, with the limits approved by the operator (E-015).", "")

    P.add("## How the numbers on this page are kept honest", "")
    if spec.name in REPORTS:
        P.add("Every number above is computed from the source file when the page is built and registered in "
              "`extended/trace.py`; `python scripts/trace_check.py` recomputes each one from the file, after checking "
              "its manifest, and finds it on this page. Dates and the manifest's identifiers are provenance, not "
              "results.")
    else:
        P.add("**NOT TRACED.** This page is not registered in `extended/trace.py`: its numbers are computed from the "
              "file, but no standing check confirms the page still matches it.")
    return Composed(P.text(), P.claims, charts)


def compose_text(spec: ReportSpec, *, root: Path | str = ROOT) -> str:
    if isinstance(spec, JourneySpec):
        from extended import journey_page as J

        return J.compose_text(spec, root=root)
    df, man = read(spec, root)
    return compose(spec, df, man, root=root).text


# ------------------------------------------------------------------------------------------------ the charts

BLUE, ORANGE, GREEN, PINK, SKY, VERMILLION, BLACK = ("#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9",
                                                    "#D55E00", "#000000")
#: Okabe-Ito colours (colour-blind safe), each with its own marker and line style so colour is never the only cue
COLORS = (BLUE, ORANGE, GREEN, PINK, SKY, VERMILLION, BLACK)
MARKERS = ("o", "s", "^", "D", "v", "P", "X")
STYLE = {"figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
         "axes.edgecolor": "#333333", "axes.labelcolor": "#1a1a1a", "text.color": "#1a1a1a",
         "xtick.color": "#333333", "ytick.color": "#333333", "axes.grid": True, "grid.color": "#dddddd",
         "grid.linewidth": 0.8, "font.size": 10, "axes.titlesize": 11, "legend.framealpha": 0.95}
MONTH_TICKS = (0, 21, 42, 63, 126, 189, 252)


def _thousands(v, _pos=None) -> str:
    return f"{v:,.0f}"




def fan_series(st: Starts) -> tuple[np.ndarray, np.ndarray, str]:
    """(sessions, the percentiles `FAN_PCTS` of the net at each, `daily` or `monthly`)."""
    if st.path is not None:
        M = st.path[:, 1:YEAR + 1]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            q = np.nanpercentile(M, FAN_PCTS, axis=0)
        return np.arange(1, YEAR + 1), q, "daily"
    x = MONTH * np.arange(1, MONTHS + 1)
    q = np.array([[quantity(st, f"dist:net_{m}:p{p}") for m in range(1, MONTHS + 1)] for p in FAN_PCTS])
    return x, q, "monthly"


def breakeven_series(st: Starts) -> tuple[np.ndarray, np.ndarray, np.ndarray | None, str]:
    """(sessions, the share at or above break-even at each, the share back at break-even at least once by each (daily
    only), the resolution)."""
    if st.path is not None:
        M = st.path[:, 1:YEAR + 1]
        seen = np.isfinite(M)
        x = np.arange(1, YEAR + 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            at = ((M >= -TOL) & seen).sum(0) / seen.sum(0)
            reached = ((st.be[:, None] <= x[None, :]) & seen).sum(0) / seen.sum(0)
        return x, at, reached, "daily"
    x = MONTH * np.arange(1, MONTHS + 1)
    at = []
    for m in range(1, MONTHS + 1):
        v = st.net[:, m - 1]
        el = (st.obs >= MONTH * m) & np.isfinite(v)
        at.append(float((v[el] >= -TOL).mean()) if el.any() else np.nan)
    return x, np.array(at), None, "monthly"


def _months_axis(ax) -> None:
    ax.set_xlim(0, YEAR + 4)
    ax.set_xticks(MONTH_TICKS)
    top = ax.secondary_xaxis("top", functions=(lambda s: s / MONTH, lambda m: m * MONTH))
    top.set_xticks([1, 2, 3, 6, 9, 12])
    top.set_xlabel("Months since the start day")


def _draw_fan(plt, path: Path, st: Starts, d: Design) -> None:
    from matplotlib.ticker import FuncFormatter

    x, q, res = fan_series(st)
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    mk = dict(marker="o", ms=4) if res == "monthly" else {}
    ax.fill_between(x, q[0], q[4], color=SKY, alpha=0.35, lw=0, label="8 in 10 start days (10th to 90th percentile)")
    ax.fill_between(x, q[1], q[3], color=BLUE, alpha=0.45, lw=0, label="half of start days (25th to 75th percentile)")
    ax.plot(x, q[2], color=BLACK, lw=2, label="the middle start day (median)", **mk)
    ax.axhline(0, color=VERMILLION, ls="--", lw=1.6, label="break-even: net cash = 0")
    _months_axis(ax)
    ax.set_xlabel("Trading sessions since the start day (21 sessions = one month)")
    ax.set_ylabel("Net cash so far (US dollars)")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_title(f"{d.short}: net cash so far, across start days", loc="left")
    ax.legend(loc="upper left", fontsize=8.5)
    if res == "monthly":
        ax.text(0.99, 0.02, "read at month ends only (the file has no daily cash); lines join the month ends",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=8, color="#444444")
    fig.tight_layout()
    fig.savefig(path, dpi=110, metadata={"Software": None})
    plt.close(fig)


def _hist(ax, vals: np.ndarray, bins, xlabel: str, ylabel: str) -> None:
    vals = vals[np.isfinite(vals)]
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if not len(vals):
        ax.text(0.5, 0.5, "nothing to read", ha="center", va="center", transform=ax.transAxes)
        return
    ax.hist(vals, bins=bins(vals) if callable(bins) else bins, color=BLUE, edgecolor="white", lw=0.5)
    ax.axvline(float(np.median(vals)), color=BLACK, ls="--", lw=1.5, label="the middle (median)")
    ax.set_ylim(0, ax.get_ylim()[1] * 1.2)
    from matplotlib.ticker import FuncFormatter

    ax.yaxis.set_major_formatter(FuncFormatter(_thousands))
    ax.legend(fontsize=8, loc="upper left" if float(np.median(vals)) > float(np.mean(ax.get_xlim())) else "upper right")


def _money_bins(v: np.ndarray):
    lo, hi = float(v.min()), float(v.max())
    return np.linspace(lo, hi if hi > lo else lo + 1, 31)


def _gap_bins(v: np.ndarray):
    step = max(1, int(math.ceil(float(v.max()) / 40)))
    return np.arange(0.5, float(v.max()) + step + 0.5, step)


def _draw_payouts(plt, path: Path, st: Starts, d: Design) -> None:
    from matplotlib.ticker import FuncFormatter

    fig, ax = plt.subplots(1, 3, figsize=(12.5, 4.0))
    if st.cash is not None:
        sizes, what, unit = dist(st, "payout_size").values, "Size of each payout (US dollars)", "Number of payouts"
    else:
        sizes, what, unit = dist(st, "first_payout_size").values, "Size of the first payout (US dollars)", \
            "Number of start days"
    _hist(ax[0], sizes, _money_bins, what, unit)
    ax[0].xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    _hist(ax[1], dist(st, "payout_gap").values, _gap_bins, "Sessions between one payout day and the next",
          "Number of gaps")
    _hist(ax[2], 100 * dist(st, "largest_month").values, np.arange(0, 102.5, 2.5),
          "Largest single month's share\nof the year's payouts (%; 100 = one lump)", "Number of start days")
    ax[2].set_xlim(0, 100)
    fig.suptitle(f"{d.short}: payouts", x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=110, metadata={"Software": None})
    plt.close(fig)


def _draw_breakeven(plt, path: Path, spec: ReportSpec, base: dict[str, Starts]) -> None:
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    for i, d in enumerate(spec.designs):
        x, at, reached, res = breakeven_series(base[d.key])
        c, mk = COLORS[i % len(COLORS)], MARKERS[i % len(MARKERS)]
        every = None if res == "monthly" else MONTH
        ax.plot(x, 100 * at, color=c, lw=2, marker=mk, ms=5, markevery=every,
                label=f"{d.short}: at or above break-even at that session")
        if reached is not None:
            ax.plot(x, 100 * reached, color=c, lw=1.5, ls="--", marker=mk, ms=4, markevery=every, mfc="white",
                    label=f"{d.short}: back to break-even at least once by then")
    _months_axis(ax)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Trading sessions since the start day (21 sessions = one month)")
    ax.set_ylabel("Share of start days (%)")
    ax.set_title("Back to break-even: the share of start days with net cash at or above zero", loc="left")
    ax.legend(loc="lower right", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(path, dpi=110, metadata={"Software": None})
    plt.close(fig)


def _draw_tradeoff(plt, path: Path, spec: ReportSpec, base: dict[str, Starts]) -> None:
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.6), sharey=True)
    for j, (name, xlabel) in enumerate((("gain_months", "Share of the year's months with a net gain,\nmiddle start "
                                         "day (%) -- further right is more even"),
                                        ("largest_month", "Largest single month's share of the year's payouts,\n"
                                         "middle start day (%) -- further left is more even"))):
        for i, d in enumerate(spec.designs):
            st = base[d.key]
            x, y = quantity(st, f"dist:{name}:p50"), quantity(st, "score:P")
            if not (math.isfinite(x) and math.isfinite(y)):
                continue
            ax[j].scatter(100 * x, 100 * y, s=80, color=COLORS[i % len(COLORS)], marker=MARKERS[i % len(MARKERS)],
                          edgecolor=BLACK, lw=0.6, zorder=3, label=d.short)
            ax[j].annotate(d.short, (100 * x, 100 * y), xytext=(7, 6), textcoords="offset points", fontsize=9)
        ax[j].set_xlabel(xlabel)
        ax[j].margins(0.25)
    ax[0].set_ylabel("Start days ahead, months 1 to 3 averaged (P, %)")
    ax[0].legend(loc="best", fontsize=8.5)
    fig.suptitle("Evenness against being ahead (each point is one design)", x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=110, metadata={"Software": None})
    plt.close(fig)


def _draw(plt, chart: Chart, out: Path, spec: ReportSpec, base: dict[str, Starts]) -> Path:
    path = out / chart.file
    with plt.rc_context(STYLE):
        if chart.kind == "fan":
            _draw_fan(plt, path, base[chart.payload["design"]], spec.design(chart.payload["design"]))
        elif chart.kind == "payouts":
            _draw_payouts(plt, path, base[chart.payload["design"]], spec.design(chart.payload["design"]))
        elif chart.kind == "breakeven":
            _draw_breakeven(plt, path, spec, base)
        elif chart.kind == "tradeoff":
            _draw_tradeoff(plt, path, spec, base)
        else:
            raise KeyError(chart.kind)
    return path


# ------------------------------------------------------------------------------------------------ build and trace


def build(spec: ReportSpec, *, root: Path | str = ROOT, out: Path | str | None = None) -> Built:
    """Read the file (manifest first), compose the page, draw its charts, write `<out>/README.md`. Refuses (raises)
    before writing anything when the file fails its manifest or the spec does not fit it. Charts this build did not
    draw are removed from the folder. A `JourneySpec` is `extended.journey_page`'s page."""
    if isinstance(spec, JourneySpec):
        from extended import journey_page as J

        return J.build(spec, root=root, out=out)
    df, man = read(spec, root)
    composed = compose(spec, df, man, root=root)
    folder = Path(out) if out is not None else Path(root) / spec.out_dir
    folder.mkdir(parents=True, exist_ok=True)
    drawn: list[Path] = []
    if composed.charts:
        plt = _pyplot()
        if plt is None:
            raise ReportError("matplotlib is installed but cannot be loaded: nothing written")
        base = {d.key: starts_for(spec, df, d.key) for d in spec.designs}
        drawn = [_draw(plt, c, folder, spec, base) for c in composed.charts]
    for old in folder.glob("*.png"):
        if old not in drawn:
            old.unlink()
    page = folder / PAGE
    page.write_text(composed.text, encoding="utf-8", newline="\n")
    return Built(page, drawn, composed.claims)


class _Recompute:
    """A claim's value from the file's frame, as the trace check hands it over: the claim's rows, its `quantity`."""

    def __init__(self, spec: ReportSpec, claim: Claim):
        self.spec, self.claim = spec, claim

    def __call__(self, df: pd.DataFrame) -> float:
        c = self.claim
        return quantity(starts_for(self.spec, df, c.design, c.level, c.block), c.what)


def traced_numbers(spec: ReportSpec, *, root: Path | str = ROOT) -> list[TracedNumber]:
    """Every number the page prints as a `TracedNumber`: recomputed from the source file (the trace check reads it
    through the vendored `read_result`, its manifest first) and looked for on the page."""
    if isinstance(spec, JourneySpec):
        from extended import journey_page as J

        return J.traced_numbers(spec, root=root)
    df, man = read(spec, root)
    composed = compose(spec, df, man, root=root)
    src = str(source_path(spec, root).resolve())
    doc = page_path(spec, root).relative_to(Path(root)).as_posix()
    return [TracedNumber(label=f"{spec.name}: {c.label}", source_csv=src, recompute=_Recompute(spec, c),
                         documents=(doc,), decimals=c.decimals, as_percent=c.as_percent,
                         tolerance=0.5 * 10 ** (-c.decimals)) for c in composed.claims]


def describe(spec: ReportSpec) -> str:
    return json.dumps({"name": spec.name, "source": spec.source, "out": spec.out_dir,
                       "designs": [d.key for d in spec.designs]})


__all__ = ["REPORTS", "ReportSpec", "JourneySpec", "waiting", "Design", "ReportError", "NotInFile", "Starts",
           "starts_for", "quantity", "blank_reason", "dist", "compose", "compose_text", "build", "traced_numbers", "spec_from_dict",
           "source_path", "page_path", "JOURNEY", "PAYOUTS", "SCORE_WORDS"]
