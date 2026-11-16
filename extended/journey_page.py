"""The journey scorecard page (Q-69; CHARTER section 2, E-007 (e), E-008, E-014, E-015): Q-17's readings -- written by
`scripts/user_beside.py` (Q-44's clean run) as `results/user_beside.csv` and its per-start companion
`results/user_beside_starts.csv` -- turned into the page the operator reads, every number computed from the files when
the page is built and registered for the trace check.

    from extended import report as R
    R.build(R.REPORTS["journey_scorecard"])            # -> docs/report/journey_scorecard/README.md and its charts
    R.traced_numbers(R.REPORTS["journey_scorecard"])   # every number it prints, as the trace check's entries

`scripts/build_report.py --report journey_scorecard` is the command; `extended/report.py` holds the registered spec
(`JourneySpec`) and hands this module its pages. Importing it puts the vendored tree on `sys.path` (through
`extended.report`): import it in a process of its own.

**The schema is the writer's, imported, not copied**: the sections and the summary's key columns
(`extended.user_readings`: `BLOCKS`, `START_COLS`, `MONEY_COLS`, the windows, the bankroll limits, the months; its
`summary` writes every row this page reads), the responses and their parameters (`extended.user_beside.RESPONSES`),
the percentiles and the days-to-an-event rule (`extended.user_measures`), the arms, the judged block and the scorecard's
lines and directions (Stage 2's `user_journey.ARMS`, `u_select`), the frontier (Stage 2's `user_drivers.frontier` on
its `FRONTIER_MEASURES`) and design-against-luck (`user_drivers.variance_split`).

**What it reads, and refuses.** Both files through `extended.results.read_result` (each manifest checked first); both
manifests must name the writer (`JourneySpec.writer`) and the same commit, the companion must name the summary; every
section of the writer must be there, every design of the spec, the verdict arm and the response `off`, and only the
writer's responses. Then **the files are held to each other**: the writer's own `user_readings.path_rows` and
`response_rows`, run again on the per-start file, must give the summary's `path` and `response` rows -- counts exactly,
values exactly but for money, which the per-start file holds to the cent (within half a cent). A refusal raises
`extended.report.ReportError` before anything is written. With `identity_u1` set (the registered page) `build` also
holds the verdict view to Stage 2: the summary's scorecard with every response off equals Stage 2's own scorecard
(`u_select.scorecard`, as `extended.report.Starts` reads U1's start rows) for every design, both arms, all start days
and the judged block -- values within 1e-9, counts exactly -- and refuses otherwise.

**What it shows** (the verdict view -- the cautious arm, payouts never denied, the placement off, E-008 (2) -- first;
everything else labelled beside):

* side by side: P and each month's share ahead (months 1-3) on all start days and the judged block; the scorecard
  (P, S1-S5c) with each design's difference from R* = P-14 in plain "better / worse" words and the best of the three on
  each line (`u_select.row_to_beat`); the frontier on P, S1, S3a, S5a; how much of the net at each month end is the
  design and how much the start day; E-015's limits -- **pending the operator's approval**, shown as flags with no
  level (`LIMITS`, a declared hook: a level is read from a result file once a decision row approves it, never typed);
* per design: P and the money month by month with E-007 (e)'s extras (mean net, CVaR10, P under the bankroll limits,
  the effective number of independent start days, the minimum detectable difference -- blank, with the writer's
  reason); the time and money to the first pass, the first payout and break-even as distributions over start days
  (p10, p25, median, p75, p90, the spread, the share never there inside the window); the year's evenness; the spread
  of net cash at each month end (worst to best, from the per-start file) and the worst start days; beside: every firm
  response the file holds (the denial ladder, forfeiture, the placement on, the Focused Trader models) and the
  as-traded arm.

Every number printed goes through `_Page.num`, which records a `Claim` (its file, an `ask` naming how it is derived);
`traced_numbers` turns the claims into `TracedNumber` entries whose recompute derives the value from the file again.
"""
from __future__ import annotations

import math
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from extended import ROOT
from extended import report as R  # noqa: I001  (puts the vendored tree on sys.path)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import user_beside as B  # noqa: E402
from extended import user_measures as M  # noqa: E402
from extended import user_readings as UR  # noqa: E402
from extended.results import read_manifest, read_result  # noqa: E402
from propedge.reporting.trace import TracedNumber  # noqa: E402
from propedge.research import u_select as S  # noqa: E402
from propedge.research import user_drivers as D  # noqa: E402
from propedge.research import user_journey as U  # noqa: E402

ReportError = R.ReportError
NAN = float("nan")

#: the writer's sections (scripts/user_beside.py writes `identity` itself; `extended.user_readings` the rest)
SECTIONS = ("identity", "scorecard", "extra", "path", "response")
#: a summary row is named by these columns (the writer's `summary` rows and `main`'s identity rows)
KEY = ("section", "design", "arm", "response", "block", "measure", "stat")
VERDICT, BESIDE = S.ARM, S.BESIDE_ARM                   # "verdict" (cautious), "point" (as traded)
OFF = B.RESPONSES[0].name                                # every response off: the verdict view's
ALL, JUDGED = UR.BLOCKS
MONTH = UR.MONTH
FIRST_WINDOW, YEAR_WINDOW = UR.FIRST_WINDOW, UR.YEAR_WINDOW
P_MONTHS = M.P_MONTHS
#: the month ends the per-start file holds a net for (its `net_month_k` columns)
NET_MONTHS = tuple(int(c.rsplit("_", 1)[1]) for c in UR.START_COLS if c.startswith("net_month_"))
#: the distribution's points shown from the per-start file beside the writer's p10, median, p90
SPREAD_PCTS = (10, 25, 50, 75, 90)
WORST = 5                                                # the worst start days listed, by their month-3 net
WORST_BY = "net_month_3"
#: money to the cent in the per-start file: a quantile of it is within half a cent of the summary's
CENT_TOL = 0.005 + 1e-9
READ_KEY = "s2x_read"                                    # `extended.trace`'s stamp on a frame it read (see `_index`)
#: scorecard lines that are a days percentile (blank when it falls beyond the line's window)
DAYS_LINES = ("S3b",)

#: plain words for the path section's journey measures: name -> (words, unit kind, window or None)
JOURNEY = (
    ("first_pass_days", "Sessions until the first passed evaluation", "sessions", FIRST_WINDOW),
    ("spent_before_first_pass", "Cash out of pocket before the first pass ($)", "dollars", None),
    ("first_payout_days", "Sessions until the first payout arrives", "sessions", FIRST_WINDOW),
    ("spent_before_first_payout", "Cash out of pocket before the first payout ($)", "dollars", None),
    ("break_even_days", "Sessions until net cash is back to zero or above (break-even: what was spent is paid back)",
     "sessions", YEAR_WINDOW),
)
#: the per-start column behind each journey measure (its p25 and p75)
JOURNEY_COLUMN = {"first_pass_days": "first_pass", "spent_before_first_pass": "spent_before_first_pass",
                  "first_payout_days": "first_payout", "spent_before_first_payout": "spent_before_first_payout",
                  "break_even_days": "break_even_day"}
EVENNESS = (
    ("share_months_positive", "Share of the year's months with a net gain", "percent"),
    ("longest_months_without_payout", "Longest run of months without a payout (months)", "months"),
    ("sd_monthly_net", "How much the monthly net change swings (standard deviation, $)", "dollars"),
    ("payouts_per_month", "Payouts per month", "ratio"),
    ("payout_cash_per_month", "Payout cash per month ($)", "dollars"),
    ("largest_month_share", "Largest single month's share of the year's payouts (100% = all in one month)",
     "percent"),
    ("deepest_fall_after_break_even", "Deepest fall in net cash after break-even ($)", "dollars"),
)


# ------------------------------------------------------------------------------------------------ the limits (E-015)


@dataclass(frozen=True)
class Limit:
    """One of E-015's limits on what a user feels (CHARTER section 2: "bankroll and time to first payout"), declared
    without a level. E-015 (2): the lead proposes each level from this page's file -- what P-14, P-15 and P-16 achieve,
    with a margin wider than its measurement noise -- and the operator approves it before use. **A level is never
    typed**: once approved it is read from `source` (a result file with a manifest: the proposal's), the one row
    matching `where`, its column `column`; `approved` names the decision row recording the operator's approval. Until
    both are set the limit is pending and no design is flagged. A limit never fails a design (E-015 (3)): a design past
    it is shown with which limit and by how much."""

    measure: str                                       # a scorecard line (`u_select.BY_KEY`)
    words: str
    source: str = ""                                   # relative to the repository root, or absolute
    where: tuple[tuple[str, Any], ...] = ()
    column: str = "value"
    approved: str = ""

    @property
    def pending(self) -> bool:
        return not (self.source and self.approved)

    @property
    def bound(self) -> str:
        return "at most" if S.BY_KEY[self.measure].direction == S.LOWER else "at least"


#: the declared hook: the two limits CHARTER section 2 names, pending (no level exists; E-015 (2))
LIMITS: tuple[Limit, ...] = (
    Limit("S1", "Cash spent before the first payout, high end (p90): the bankroll a user needs"),
    Limit("S3b", "Sessions to the first payout, high end (p90): how long a user waits"),
)


def limits_of(spec: Any) -> tuple[Limit, ...]:
    got = getattr(spec, "limits", None)
    return LIMITS if got is None else tuple(got)


# ------------------------------------------------------------------------------------------------ the files


def starts_path(spec: Any, root: Path | str = ROOT) -> Path:
    p = Path(spec.starts)
    return p if p.is_absolute() else Path(root) / p


def _limit_path(lim: Limit, root: Path | str) -> Path:
    p = Path(lim.source)
    return p if p.is_absolute() else Path(root) / p


class Rows:
    """The summary file's rows, by `KEY` -> (value, n, note)."""

    def __init__(self, df: pd.DataFrame):
        missing = [c for c in (*KEY, "value", "n", "note") if c not in df.columns]
        if missing:
            raise ReportError(f"not the writer's readings file: no column {', '.join(missing)}")
        text = {c: df[c].astype(object).where(df[c].notna(), "").astype(str).str.strip().tolist() for c in KEY}
        vals = pd.to_numeric(df["value"], errors="coerce").to_numpy(float)
        ns = pd.to_numeric(df["n"], errors="coerce").to_numpy(float)
        notes = df["note"].astype(object).where(df["note"].notna(), "").astype(str).tolist()
        self.by: dict[tuple[str, ...], tuple[float, float, str]] = {}
        for i, k in enumerate(zip(*(text[c] for c in KEY))):
            if k in self.by:
                raise ReportError(f"two rows of the readings file for {k}")
            self.by[k] = (float(vals[i]), float(ns[i]), notes[i])
        self.sections = list(dict.fromkeys(text["section"]))
        self.designs = list(dict.fromkeys(d for d, s in zip(text["design"], text["section"]) if s != "identity"))
        self.arms = list(dict.fromkeys(a for a, s in zip(text["arm"], text["section"]) if s != "identity"))
        self.responses = list(dict.fromkeys(r for r, s in zip(text["response"], text["section"]) if s != "identity"))
        self.identity = [(k, v) for k, v in self.by.items() if k[0] == "identity"]

    def get(self, section: str, design: str, arm: str, response: str, block: str, measure: str,
            stat: str = "value") -> tuple[float, float, str]:
        k = (section, design, arm, response, block, measure, stat)
        if k not in self.by:
            raise ReportError(f"the readings file has no row {k}")
        return self.by[k]

    def value(self, *k: str) -> float:
        return self.get(*k)[0]

    def responses_of(self, design: str, arm: str) -> list[str]:
        """The responses the file holds for a design and arm, in the writer's order."""
        have = {k[3] for k in self.by if k[0] != "identity" and k[1] == design and k[2] == arm}
        return [r.name for r in B.RESPONSES if r.name in have]


class StartRows:
    """The per-start file's rows by (design, arm, response), each in start order."""

    def __init__(self, df: pd.DataFrame):
        missing = [c for c in UR.START_COLS if c not in df.columns]
        if missing:
            raise ReportError(f"not the writer's per-start file: no column {', '.join(missing)}")
        self.groups: dict[tuple[str, str, str], pd.DataFrame] = {}
        for k, g in df.groupby(["design", "arm", "response"], sort=False):
            g = g.sort_values("start_day", kind="stable").reset_index(drop=True)
            if g["start_day"].duplicated().any():
                raise ReportError(f"{k}: a start day appears more than once in the per-start file")
            g["start_date"] = g["start_date"].astype(str)
            self.groups[tuple(str(x) for x in k)] = g

    def table(self, design: str, arm: str, response: str) -> pd.DataFrame:
        k = (design, arm, response)
        if k not in self.groups:
            raise ReportError(f"the per-start file has no rows for {k}")
        return self.groups[k]


@dataclass
class Data:
    rows: Rows
    starts: StartRows
    manifest: Any
    starts_manifest: Any
    source: Path
    starts_source: Path
    levels: dict[int, pd.DataFrame] = field(default_factory=dict)
    cross: int = 0


def _read(path: Path) -> pd.DataFrame:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", pd.errors.DtypeWarning)
        return read_result(path)


def pairing_problems(spec: Any, man: Any, sman: Any, src: Path, ssrc: Path) -> list[str]:
    """Why the two files are not one reading of the writer's (empty: they are)."""
    out = []
    for m, p in ((man, src), (sman, ssrc)):
        if str(m.script) != spec.writer:
            out.append(f"{p.name} was written by {m.script!r}, not {spec.writer!r}")
    if str(man.git_commit) != str(sman.git_commit):
        out.append(f"the files were written at different commits ({man.git_commit} and {sman.git_commit})")
    companion = (sman.notes or {}).get("companion_of")
    if companion != src.name:
        out.append(f"{ssrc.name}'s manifest names {companion!r} as its companion, not {src.name!r}")
    return out


def schema_problems(spec: Any, rows: Rows, starts: StartRows) -> list[str]:
    out = []
    for s in SECTIONS:
        if s not in rows.sections:
            out.append(f"no section {s!r}")
    out += [f"an unknown section {s!r}" for s in rows.sections if s not in SECTIONS]
    out += [f"an unknown response {r!r} (not the writer's)" for r in rows.responses if r not in B.BY_NAME]
    for d in spec.designs:
        if d.key not in rows.designs:
            out.append(f"no rows for the design {d.key!r}")
            continue
        if OFF not in rows.responses_of(d.key, VERDICT):
            out.append(f"{d.key}: no verdict-arm rows with every response off (the verdict view)")
    if spec.r_star not in [d.key for d in spec.designs]:
        out.append(f"R* {spec.r_star!r} is not among the page's designs")
    if not starts.groups:
        out.append("the per-start file is empty")
    return out


def _same(a: float, b: float, tol: float) -> bool:
    if math.isnan(a) and math.isnan(b):
        return True
    return abs(a - b) <= tol + 1e-12 * max(1.0, abs(b))


def cross_problems(rows: Rows, starts: StartRows) -> tuple[int, list[str]]:
    """The writer's own `path_rows` and `response_rows` on the per-start file against the summary's rows: (the
    comparisons made, the differences)."""
    money = set(UR.MONEY_COLS)
    compared, out = 0, []
    for (d, a, r), t in starts.groups.items():
        for row in UR.path_rows(t) + UR.response_rows(t):
            k = (row["section"], d, a, r, row["block"], row["measure"], row["stat"])
            if k not in rows.by:
                out.append(f"the summary has no row {k}")
                continue
            v, n, _ = rows.by[k]
            tol = CENT_TOL if row["measure"] in money else 1e-9 * max(1.0, abs(v)) if math.isfinite(v) else 0.0
            compared += 1
            if int(n) != int(row["n"]) or not _same(float(row["value"]), v, tol):
                out.append(f"{k}: the per-start file gives {row['value']!r} on {row['n']}, the summary {v!r} on {n:g}")
    groups = {(k[1], k[2], k[3]) for k in rows.by if k[0] in ("path", "response")}
    out += [f"{g}: in the summary, not in the per-start file" for g in sorted(groups - set(starts.groups))]
    return compared, out


#: the two files' parse and cross-check, by the pair of sha256 their manifests record (each file verified against its
#: own by `read_result` on every load): a pair of contents is parsed and held to each other once a process
_PARSED: dict[tuple[str, str], tuple[Rows, StartRows, int, list[str]]] = {}
_PARSED_SIZE = 4


def load(spec: Any, root: Path | str = ROOT) -> Data:
    """Both files (manifests first), held to the writer and to each other; refused with `ReportError` otherwise."""
    src, ssrc = R.source_path(spec, root), starts_path(spec, root)
    df, sdf = _read(src), _read(ssrc)                  # each verified against its manifest's sha256, every time
    man, sman = read_manifest(src), read_manifest(ssrc)
    bad = pairing_problems(spec, man, sman, src, ssrc)
    if bad:
        raise ReportError("the two files are not one reading of the writer's: " + "; ".join(bad))
    key = (str(man.sha256), str(sman.sha256))
    if key not in _PARSED:
        rows, starts = Rows(df), StartRows(sdf)
        compared, cross = cross_problems(rows, starts)
        if len(_PARSED) >= _PARSED_SIZE:
            _PARSED.pop(next(iter(_PARSED)))
        _PARSED[key] = (rows, starts, compared, cross)
    rows, starts, compared, cross = _PARSED[key]
    bad = schema_problems(spec, rows, starts)
    if bad:
        raise ReportError("the readings file does not fit the page: " + "; ".join(bad[:6]))
    if cross:
        raise ReportError(f"the per-start file does not give the summary's path and response rows ({len(cross)} "
                          "differ): " + "; ".join(cross[:4]))
    data = Data(rows, starts, man, sman, src, ssrc, cross=compared)
    for i, lim in enumerate(limits_of(spec)):
        if lim.measure not in S.BY_KEY:
            raise ReportError(f"a limit on {lim.measure!r}, which is not a scorecard line")
        if not lim.pending:
            data.levels[i] = _read(_limit_path(lim, root))
    return data


# ------------------------------------------------------------------------------------------------ the numbers


def _starts_values(t: pd.DataFrame, block: str, column: str) -> tuple[np.ndarray, int | None]:
    """The per-start values a distribution reads (the writer's eligibility, `user_readings._elig`) and, for days to
    an event, its window (an unreached start counts as beyond it)."""
    if column.startswith("net_month_"):
        e = UR._elig(t, block, MONTH * int(column.rsplit("_", 1)[1]))
        x = t[column].to_numpy(float)[e]
        return x[np.isfinite(x)], None
    if column in ("first_pass", "first_payout"):
        return t[column].to_numpy(float)[UR._elig(t, block, FIRST_WINDOW)], FIRST_WINDOW
    if column == "break_even_day":
        return t[column].to_numpy(float)[UR._elig(t, block, YEAR_WINDOW)], YEAR_WINDOW
    if column in ("spent_before_first_pass", "spent_before_first_payout"):
        e = UR._elig(t, block, FIRST_WINDOW)
        f = t[column[len("spent_before_"):]].to_numpy(float)
        hit = e & np.isfinite(f) & (f <= FIRST_WINDOW)
        x = t[column].to_numpy(float)[hit]
        return x[np.isfinite(x)], None
    raise KeyError(column)


def _worst(t: pd.DataFrame, block: str) -> pd.DataFrame:
    e = UR._elig(t, block, MONTH * int(WORST_BY.rsplit("_", 1)[1])) & np.isfinite(t[WORST_BY].to_numpy(float))
    return t[e].sort_values([WORST_BY, "start_day"], kind="stable").reset_index(drop=True)


def summary_value(rows: Rows, ask: tuple) -> float:
    how, *a = ask
    if how == "row":
        return rows.value(*a)
    if how == "n":
        return rows.get(*a)[1]
    if how == "never":
        return 1.0 - rows.value(*a)
    if how == "spread":
        sec, d, arm, r, b, m = a
        return rows.value(sec, d, arm, r, b, m, "p90") - rows.value(sec, d, arm, r, b, m, "p10")
    if how == "diff":
        d, ref, arm, r, b, m = a
        return rows.value("scorecard", d, arm, r, b, m) - rows.value("scorecard", ref, arm, r, b, m)
    if how in ("ident_held", "ident_rows"):
        held = [v[0] for k, v in rows.identity if k[6] == "holds"]
        return float(sum(1 for x in held if x == 1.0)) if how == "ident_held" else float(len(held))
    if how in ("exact_differ", "exact_checked"):
        got = [v for k, v in rows.identity if k[6] == "count"]
        return float(sum(v[0] for v in got)) if how == "exact_differ" else float(sum(v[1] for v in got))
    if how in ("gap", "gap_below"):                    # a design's distance past an approved limit's level
        d, arm, r, b, m, path, where, column = a
        level = cell_value(_read(Path(path)), where, column)
        gap = rows.value("scorecard", d, arm, r, b, m) - level
        return gap if how == "gap" else -gap
    raise KeyError(ask)


def starts_value(starts: StartRows, ask: tuple) -> float:
    how, *a = ask
    if how == "q":
        d, arm, r, b, column, stat = a
        x, window = _starts_values(starts.table(d, arm, r), b, column)
        if stat == "n":
            return float(len(x))
        if stat == "never":
            hit = np.isfinite(x) & (x <= window)
            return float(1.0 - hit.mean()) if len(x) else NAN
        if not len(x):
            return NAN
        if stat in ("min", "max"):
            return float(x.min() if stat == "min" else x.max())
        if stat == "spread":
            return float(np.percentile(x, 90) - np.percentile(x, 10))
        p = float(stat[1:])
        return M.days_quantile(x, window, p) if window is not None else float(np.percentile(x, p))
    if how == "worst":
        d, arm, r, b, rank, column = a
        w = _worst(starts.table(d, arm, r), b)
        return float(w.loc[int(rank), column]) if int(rank) < len(w) else NAN
    if how == "rows":
        return float(len(starts.table(*a)))
    if how == "worst_n":
        d, arm, r, b = a
        return float(len(_worst(starts.table(d, arm, r), b)))
    if how == "luck":
        designs, arm, r, b, m, stat = a
        nets = {}
        for d in designs:
            t = starts.table(d, arm, r)
            x = t[f"net_month_{m}"].to_numpy(float)[UR._elig(t, b, MONTH * int(m))]
            nets[d] = x
        return float(D.variance_split(nets)[stat])
    raise KeyError(ask)


def cell_value(df: pd.DataFrame, where: Sequence[tuple[str, Any]], column: str) -> float:
    """One cell of a limit's source file: the one row matching `where`."""
    m = pd.Series(True, index=df.index)
    for col, want in where:
        if col not in df.columns:
            raise ReportError(f"the limit's file has no column {col!r}")
        m &= R._match(df[col], want)
    if int(m.sum()) != 1:
        raise ReportError(f"{int(m.sum())} rows of the limit's file match {dict(where)} (one is needed)")
    return float(pd.to_numeric(df.loc[m, column], errors="coerce").iloc[0])


#: indexes of frames the trace check hands over, by `extended.trace`'s stamp (path, size, mtime, sha256): one parse a
#: file a trace run, however many of its numbers are checked
_INDEX: dict[tuple, Any] = {}
_INDEX_SIZE = 8


def _index(df: pd.DataFrame, kind: str) -> Any:
    key = df.attrs.get(READ_KEY)
    if key is not None and (key, kind) in _INDEX:
        return _INDEX[(key, kind)]
    got = Rows(df) if kind == "summary" else StartRows(df) if kind == "starts" else df
    if key is not None:
        if len(_INDEX) >= _INDEX_SIZE:
            _INDEX.pop(next(iter(_INDEX)))
        _INDEX[(key, kind)] = got
    return got


def value_of(kind: str, ask: tuple, obj: Any) -> float:
    """A claim's value from its file's index (`Rows`, `StartRows`) or, for a limit's level, its frame."""
    if kind == "summary":
        return summary_value(obj, ask)
    if kind == "starts":
        return starts_value(obj, ask)
    if kind == "limit":
        return cell_value(obj, ask[1], ask[2])
    raise KeyError(kind)


# ------------------------------------------------------------------------------------------------ the page


@dataclass(frozen=True)
class Claim:
    """One number the page prints: what it is, which file (`kind`: summary, starts or a limit's `source`), how it is
    derived (`ask`), and how it is printed (`decimals`, `as_percent`, `printed` without its unit)."""

    label: str
    kind: str
    source: str
    ask: tuple
    decimals: int
    as_percent: bool
    printed: str


class _Page:
    def __init__(self, data: Data, root: Path | str):
        self.data, self.root = data, root
        self.lines: list[str] = []
        self.claims: list[Claim] = []

    def add(self, *lines: str) -> None:
        self.lines.extend(lines)

    def source(self, kind: str, ask: tuple) -> str:
        if kind == "summary":
            return str(self.data.source)
        if kind == "starts":
            return str(self.data.starts_source)
        return str(ask[0])

    def obj(self, kind: str, ask: tuple) -> Any:
        if kind == "summary":
            return self.data.rows
        if kind == "starts":
            return self.data.starts
        return self.data.levels[int(ask[3])]

    def get(self, kind: str, ask: tuple) -> float:
        return value_of(kind, ask, self.obj(kind, ask))

    def num(self, v: float, unit: str, label: str, kind: str, ask: tuple, *, signed: bool = False) -> str:
        if not math.isfinite(v):
            raise ValueError(f"{label}: a blank is not a number to print")
        s = R._fmt(v, unit)
        dec, pct = R.KINDS[unit]
        if signed and v > 0:
            s = "+" + s
        self.claims.append(Claim(label, kind, self.source(kind, ask), ask, dec, pct, s.lstrip("+")))
        if signed and pct:
            return s + " pts"
        return s + ("%" if pct else "")

    def cell(self, kind: str, ask: tuple, unit: str, label: str, *, blank: str = "--", signed: bool = False) -> str:
        v = self.get(kind, ask)
        return self.num(v, unit, label, kind, ask, signed=signed) if math.isfinite(v) else blank

    def days(self, kind: str, ask: tuple, label: str, window: int | None, n: float) -> str:
        """A days percentile: "after session W" when it falls beyond its window with start days to read."""
        v = self.get(kind, ask)
        if math.isfinite(v):
            return self.num(v, "sessions", label, kind, ask)
        return f"after session {window}" if (window is not None and n) else "--"

    def text(self) -> str:
        return "\n".join(self.lines).rstrip() + "\n"


@dataclass
class Composed:
    text: str
    claims: list[Claim]
    charts: list[R.Chart]


def response_words(name: str) -> tuple[str, str]:
    """(a short label, the plain explanation) of one of the writer's responses; the pattern's parameters are the
    engine's own (`lockstep.ConductModel`, as the writer builds it)."""
    from propedge.campaign.lockstep import ConductModel

    r = B.BY_NAME[name]
    c = ConductModel(rtp=bool(r.rtp), enforcement_p=float(r.enforcement_p), rtp_warnings=int(r.rtp_warnings))
    pct = f"{100 * r.enforcement_p:g}%"
    pattern = (f"a payout asked for on a day when the accounts have hit the maximum loss limit {c.pattern_breaches} "
               f"or more times in the last {c.pattern_window_days} trading days is refused with chance {pct}, and "
               "that account closed (the firm's account-stacking rule, as the engine models it)")
    if r.kind == "off":
        return ("Never denied; placement off (the verdict view)",
                "payouts are never refused and the firm's Responsible Trading placement is off -- the reading the "
                "charter's verdict keeps (E-008 (2))")
    if r.kind == "denial":
        return f"Payout denial, {pct}", pattern
    if r.kind == "forfeit":
        return (f"Forfeiture, {pct}",
                f"{pattern}; and a refusal ends every account on the profile: nothing more is bought and every payout "
                "still to arrive is lost (all-accounts forfeiture, the Terms of Use as the Phase 0 audit read them)")
    if r.kind == "rtp":
        w = int(r.rtp_warnings)
        return ("Placement on" + (f", {w} warnings first" if w else ", no warning"),
                "the firm's Responsible Trading Program switched on: on its trigger (two or more accounts at the "
                "maximum loss limit in one day, an average losing trade not smaller than the average winner, or full "
                "size on most trades) the trader is placed in it to the end -- a daily loss limit on every new "
                "evaluation and funded account" + (f"; the first {w} triggers bring a warning instead" if w else
                                                   "; no warning first, the strictest reading (the gate's own)"))
    if r.kind == "ftp":
        bought = r.ftp_measure == "combine_purchases"
        return (f"Focused Trader, {r.ftp_path}, {int(r.ftp_threshold)}+ {'bought' if bought else 'lost'}",
                f"the firm's Focused Trader Program, {r.ftp_path.title()} path, triggered once "
                f"{int(r.ftp_threshold)} or more {'evaluations are bought' if bought else 'funded accounts are lost'} "
                f"within {B.FTP_WINDOW} sessions (one of the models that can bind under the design's purchase budget)")
    raise KeyError(name)


def _blocks(rows: Rows, d: str) -> list[tuple[str, str]]:
    """(block, its words) the file holds for a design's verdict view."""
    have = {k[4] for k in rows.by if k[0] == "scorecard" and k[1] == d and k[2] == VERDICT and k[3] == OFF}
    words = {ALL: "All start days", JUDGED: f"Judged block (from {S.JUDGED_FIRST_YEAR})"}
    return [(b, words[b]) for b in UR.BLOCKS if b in have]


def compose(spec: Any, data: Data, *, root: Path | str = ROOT, identity: tuple[int, list[str]] | None = None
            ) -> Composed:
    """The page's text, its claims and its charts from the two files' indexes."""
    P = _Page(data, root)
    rows, starts = data.rows, data.starts
    man, sman = data.manifest, data.starts_manifest
    src, ssrc = R._rel(data.source, root), R._rel(data.starts_source, root)
    sha, ssha = str(man.sha256)[:12], str(sman.sha256)[:12]
    commit = str(man.git_commit)
    keys = [d.key for d in spec.designs]
    short = {d.key: d.short for d in spec.designs}
    rstar = spec.r_star
    plt_ok = R._have_matplotlib()
    charts: list[R.Chart] = []
    S_ = "summary"
    T_ = "starts"

    def caption(extra: str = "") -> str:
        return (f"*Source: `{ssrc}` (sha256 `{ssha}`) and `{src}` (sha256 `{sha}`), manifests checked before reading."
                f"{extra}*")

    def image(file: str, alt: str, kind: str, payload: dict, cap: str) -> None:
        if plt_ok:
            charts.append(R.Chart(file, kind, payload))
            P.add(f"![{alt}]({file})", "", cap, "")
        else:
            P.add("*Chart not drawn: matplotlib is not installed here; the tables carry the figures.*", "", cap, "")

    def row(section, d, arm, r, b, measure, stat="value") -> tuple:
        return ("row", section, d, arm, r, b, measure, stat)

    def score(k: str, b: str, key: str, unit: str, tag: str = "") -> str:
        """A verdict-view scorecard value; a blank days percentile with start days to read is beyond its window."""
        ask = row("scorecard", k, VERDICT, OFF, b, key)
        if key in DAYS_LINES and not math.isfinite(P.get("summary", ask)) and rows.get(*ask[1:])[1]:
            return f"after session {S.BY_KEY[key].horizon}"
        return P.cell("summary", ask, unit, f"{short[k]} | {b} | {key}{tag}")

    # -- the head
    P.add(f"# {spec.title}", "")
    P.add("> **BESIDE, NEVER DECIDING.** A design passes only on its own trades: their lift over the coin twin, by a "
          "calibrated statistic (CHARTER section 3, E-008). This page is the user scorecard reported beside that "
          "judgement -- nothing on it passes or fails a design, and nothing is chosen from it. R* (the row to beat on "
          f"P) stays {short[rstar]}.", ">")
    if bool(getattr(man, "exploratory", False)):
        P.add("> **EXPLORATORY.** The file's manifest marks it exploratory: its readings were not declared as a test "
              "before they were run. They are reported apart from any declared result and decide nothing.", ">")
    if commit.endswith("-dirty") or bool(getattr(man, "git_dirty", False)):
        P.add(f"> **NOT CITABLE.** The file was written from a tree with uncommitted changes (`{commit}`); a result is "
              "citable only when written from a clean checkout of a named commit.", ">")
    P.lines.pop()
    P.add("")
    count = getattr(man, "variant_count", None)
    P.add(f"**Source.** `{src}` (sha256 `{sha}`) and its per-start companion `{ssrc}` (sha256 `{ssha}`), both "
          f"written by `{man.script}` at commit `{commit[:12]}` on {str(man.timestamp)[:10]}; the manifests checked "
          "before reading" + (f"; readings in the file (variant count in its manifest): {count}" if count is not None
                              else "") + ". Q-17's readings (E-024), run as Q-44.",
          "**Built by** `python scripts/build_report.py --report " + spec.name + "` (`extended/journey_page.py`). The "
          "page is rebuilt from the files, never edited by hand.", "")
    if spec.note:
        P.add(spec.note, "")

    P.add("## How to read this page", "",
          "- **A start day** is one simulated user who begins on that trading day with fresh accounts; the design's "
          "trades are replayed in historical order. Every figure is a spread across start days -- what different "
          "users would have lived -- not one user's luck.",
          "- **Net cash** is payouts received less every fee paid, so far. **Ahead** means net cash above zero. "
          "**Break-even** means net cash back to zero or above: what was spent has been paid back.",
          "- **P** is the primary measure: the share of start days ahead at the end of month 1, month 2 and month 3, "
          "averaged. A **month** is 21 trading sessions; the year is 252.",
          "- **Low end (p10), p25, middle (median), p75, high end (p90)** are points of the spread across start days: "
          "one start day in ten is at or below the low end, a quarter at or below p25, half below the middle. For "
          "sessions and cash spent the high end is the slow, expensive tenth; for net cash the low end is the unlucky "
          "tenth. **Spread** is the high end less the low end.",
          f"- **Never there inside the window**: the share of start days that had not got there within the window "
          f"({FIRST_WINDOW} sessions for the first pass and payout, {YEAR_WINDOW} for break-even). \"After session "
          "W\" means more than a tenth (or a quarter, or half) of the start days had not got there within it.",
          "- **The verdict view** is the cautious reading (every trade's result moved down to the one-sided 95 % "
          "lower bound of what its history supports), payouts never denied and the firm's Responsible Trading "
          "placement off -- what the charter's verdict keeps (E-008 (2)). **Beside** marks every other reading: the "
          "firm's responses, the as-traded arm. They are shown so their effect is visible; they decide nothing.",
          f"- **The judged block** is the start days from {S.JUDGED_FIRST_YEAR} on (Stage 2 D-621 (4)(b)). Later start "
          "days have less history after them, so the longer readings there rest on few start days.",
          "- **Start days overlap.** Two start days a week apart share most of their trades, so many start days are "
          "far fewer independent histories: \"about N independent start days\" (the effective number) says how many "
          "a figure rests on.", "")

    conv = (man.parameters or {}).get("conventions") or {}
    P.add("## What this page does not model, and what it assumes", "",
          "Not modelled (CHARTER section 2): a user who stops when their own money runs out -- the replay keeps paying "
          "fees, so there is no ruin figure; the user's time; taxes.", "",
          "Assumed, as Stage 2's engine models them: fills, the payout lag and the spacing of payouts as the engine "
          "models them, not as observed; the firm's rules as Stage 2's verified ledger holds them "
          "(`vendor/stage2/config/rules.yaml`); in the verdict view, payouts never denied (Stage 2 D-234) and the "
          "placement off (Stage 2 D-289). The firm's responses beside are the engine's models of those programs, "
          "not observed behaviour.", "")
    if conv:
        P.add("How the readings were made (the file's manifest, `parameters.conventions`):", "")
        P.add(*[f"- **{k.replace('_', ' ')}**: {v}" for k, v in conv.items()], "")
    P.add("## Not on this page", "",
          "- the cash out of pocket before break-even: the file records the cash before the first pass and before the "
          "first payout, not the deepest point before break-even;",
          "- the trades' lift over the coin twin and Stage 2's long-run gate (growth on the required bankroll at the "
          "bound): they are each design's own files -- the pass line and a floor, never this page;",
          "- a calibrated uncertainty of P and the minimum detectable difference: the writer leaves it blank until "
          "TASK_QUEUE Q-16's calibrated comparison (its note is shown with each design).", "")

    # -- the checks the file passed
    held = P.cell(S_, ("ident_held",), "count", "identity checks that hold")
    total = P.cell(S_, ("ident_rows",), "count", "identity checks")
    differ = P.cell(S_, ("exact_differ",), "count", "exact-length runs that differ", blank="0")
    checked = P.cell(S_, ("exact_checked",), "count", "start days with exact-length runs checked", blank="0")
    P.add("## The checks the file passed", "",
          f"The writer refuses to write unless every one of its checks holds; the file records them (section "
          f"`identity`): {held} of {total} hold -- with every response off, the replay equals Stage 2's own U1 start "
          "rows on every start and column; every run's payouts and fees equal the engine's totals; the extra P equals "
          "the scorecard's; P under each bankroll limit is ordered below P; every share is between 0 and 1. "
          f"Exact-length runs whose event days differ from the long replay's: {differ}, over {checked} start-day "
          "readings that made them (the scorecard reads an exact-length run where one differs; the per-start figures "
          "read each start day's long replay).", "")
    P.add("Checked when this page was built: the per-start file gives every one of the summary's path and response "
          "rows by the writer's own code (`extended.user_readings.path_rows`, `response_rows`) -- counts exactly, "
          "money to the cent.", "")
    if identity is not None:
        P.add("Checked when this page was built: the verdict view's scorecard (every response off) equals Stage 2's "
              f"own scorecard of its U1 start rows (`{spec.identity_u1}`) on every line, for every design, both arms, "
              "all start days and the judged block -- values within 1e-9, counts exactly.", "")

    # -- side by side
    P.add("## The verdict view: the designs side by side", "",
          "The cautious reading, payouts never denied, placement off. Each design's own section below has the "
          "detail.", "")
    P.add("### P and each month's share of start days ahead", "")
    blocks = _blocks(rows, rstar)
    cols = []
    for b, w in blocks:
        cols += [f"{w}: ahead at month {m}" for m in P_MONTHS] + [f"{w}: **P**", f"{w}: start days read"]
    P.add("| Design | " + " | ".join(cols) + " |", "|---|" + "---:|" * len(cols))
    for k in keys:
        cells = []
        for b, w in blocks:
            for m in P_MONTHS:
                cells.append(P.cell(S_, row("extra", k, VERDICT, OFF, b, f"share_ahead_month_{m}"), "percent",
                                    f"{short[k]} | {b} | ahead at month {m}"))
            p = P.cell(S_, row("extra", k, VERDICT, OFF, b, "P"), "percent", f"{short[k]} | {b} | P")
            cells.append(f"**{p}**")
            cells.append(P.cell(S_, ("n", "extra", k, VERDICT, OFF, b, "P", "value"), "count",
                                f"{short[k]} | {b} | P start days", blank="0"))
        P.add(f"| {short[k]} | " + " | ".join(cells) + " |")
    P.add("", "*P reads the start days with three months left; each month's share reads the same start days.*", "")

    cards = {b: {k: {key: {"value": rows.value("scorecard", k, VERDICT, OFF, b, key),
                           "n": rows.get("scorecard", k, VERDICT, OFF, b, key)[1]} for key in S.BY_KEY}
                 for k in keys} for b, _ in blocks}
    for b, w in blocks:
        P.add(f"### The scorecard against R* = {short[rstar]} -- {w.lower()}", "",
              "P beside the guarded measures (CHARTER section 2), by Stage 2's own code. \"Better\" and \"worse\" "
              f"are in each measure's own direction; the difference is the design's value less {short[rstar]}'s.", "")
        others = [k for k in keys if k != rstar]
        hdr = ["Measure", "What it is", "Better when", short[rstar]]
        for k in others:
            hdr += [short[k], f"{short[k]} less {short[rstar]}"]
        rtb = None
        if set(S.ROWS_TO_BEAT) <= set(keys):
            rtb = S.row_to_beat({k: cards[b][k] for k in S.ROWS_TO_BEAT})["by_measure"]
            hdr.append("Best of the three")
        P.add("| " + " | ".join(hdr) + " |", "|---|---|---|" + "---:|" * (1 + 2 * len(others)) +
              ("---|" if rtb else ""))
        for key, (words, unit) in R.SCORE_WORDS.items():
            m = S.BY_KEY[key]
            cells = [score(rstar, b, key, unit)]
            for k in others:
                cells.append(score(k, b, key, unit))
                dv = P.get(S_, ("diff", k, rstar, VERDICT, OFF, b, key))
                if math.isfinite(dv):
                    word = "same" if abs(dv) < 1e-12 else (
                        "better" if (dv > 0) == (m.direction == S.HIGHER) else "worse")
                    cells.append(P.num(dv, unit, f"{short[k]} less {short[rstar]} | {b} | {key}", S_,
                                       ("diff", k, rstar, VERDICT, OFF, b, key), signed=True) + f" ({word})")
                else:
                    cells.append("--")
            best = ""
            if rtb is not None:
                c = rtb[key]["config"]
                best = f" | {short.get(c, c) if c else '--'}"
            P.add(f"| {key} | {words} | {m.direction} | " + " | ".join(cells) + best + " |")
        P.add("")

    P.add("### The frontier: not beaten at once on P, S1, S3a and S5a", "",
          "A design is beaten at once when another is at least as good on all four -- more start days ahead (P), "
          "less cash needed before the first payout (S1), more paid within a month (S3a), a better unlucky tenth at "
          "month 3 (S5a) -- and better on one. The frontier is the designs nothing beats so (Stage 2's "
          "`user_drivers.frontier`). It shows the trade-offs; it does not choose.", "",
          "| Design | " + " | ".join(f"{w}: on the frontier | {w}: beaten at once by" for _, w in blocks) + " |",
          "|---|" + "---|---|" * len(blocks))
    fronts = {}
    for b, _ in blocks:
        cells = [{"design": k, "label": "", "measures": {m: cards[b][k][m]["value"] for m, _ in D.FRONTIER_MEASURES}}
                 for k in keys]
        fronts[b] = D.frontier(cells)
    for k in keys:
        cells = []
        for b, _ in blocks:
            f = fronts[b][k]
            cells.append("yes" if f["on_frontier"] else ("no" if f["pool"] else "not read (a measure is blank)"))
            cells.append(", ".join(short.get(x, x) for x in f["dominated_by"]) or "--")
        P.add(f"| {short[k]} | " + " | ".join(cells) + " |")
    P.add("")

    P.add("### How much is the design and how much the start day", "",
          "The spread of net cash across every start day of the designs, split into the part between the designs' "
          "averages (the design) and the part within each design across start days (the start day's luck) -- Stage "
          "2's `user_drivers.variance_split`, on each start day's long replay (the per-start file).", "",
          "| Month end | Share that is the design | Share that is the start day | Start days pooled |",
          "|---|---:|---:|---:|")
    for m in NET_MONTHS:
        a = (tuple(keys), VERDICT, OFF, ALL, m)
        cells = [P.cell(T_, ("luck", *a, "design_share"), "percent", f"design share | month {m}"),
                 P.cell(T_, ("luck", *a, "start_day_share"), "percent", f"start-day share | month {m}"),
                 P.cell(T_, ("luck", *a, "n"), "count", f"start days pooled | month {m}", blank="0")]
        P.add(f"| Month {m} | " + " | ".join(cells) + " |")
    P.add("")

    lims = limits_of(spec)
    P.add("### Limits on what a user feels (E-015): pending the operator's approval", "",
          "Designs are compared by limits first, then the best P inside them (E-015). Each limit's level is proposed "
          "by the lead from this file -- what P-14, P-15 and P-16 achieve, with a margin wider than its measurement "
          "noise -- and **approved by the operator before use**. A limit never fails a design: a design past it is "
          "shown with which limit and by how much. Until a level is approved the limit is shown pending, with no "
          "level, and no design is flagged.", "",
          "| Limit | Bound | Level | " + " | ".join(f"{short[k]} (all start days) | {short[k]}: flag" for k in keys)
          + " |", "|---|---|---|" + "---:|---|" * len(keys))
    inside = {k: True for k in keys}
    for i, lim in enumerate(lims):
        unit = R.SCORE_WORDS[lim.measure][1]
        blank_level = False
        if lim.pending:
            level = "pending the operator's approval (E-015 (2)): no level set"
        else:
            lp = str(_limit_path(lim, root))
            lv = P.get("limit", (lp, lim.where, lim.column, i))
            blank_level = not math.isfinite(lv)
            shown = ("blank in its file: not applied" if blank_level else
                     P.num(lv, unit, f"limit {lim.measure} | level", "limit", (lp, lim.where, lim.column, i)))
            level = f"{shown} (approved: {lim.approved})"
        cells = []
        for k in keys:
            cells.append(score(k, ALL, lim.measure, unit, " | limit"))
            if lim.pending:
                cells.append("pending")
                continue
            if blank_level:
                cells.append("not read")
                inside[k] = False
                continue
            # how far past the level, in the limit's own direction: above an "at most", below an "at least"
            ask = ("gap" if lim.bound == "at most" else "gap_below", k, VERDICT, OFF, ALL, lim.measure,
                   str(_limit_path(lim, root)), lim.where, lim.column)
            g = P.get(S_, ask)
            beyond = (lim.measure in DAYS_LINES and lim.bound == "at most"
                      and rows.get("scorecard", k, VERDICT, OFF, ALL, lim.measure)[1] > 0)
            if not math.isfinite(g) and beyond:
                cells.append(f"past it (the high end is after session {S.BY_KEY[lim.measure].horizon})")
                inside[k] = False
            elif not math.isfinite(g):
                cells.append("not read")
                inside[k] = False
            elif g > 0:
                inside[k] = False
                cells.append("past it by " + P.num(g, unit, f"{short[k]} | past limit {lim.measure} by", S_, ask))
            else:
                cells.append("inside")
        P.add(f"| {lim.words} | {lim.bound} | {level} | " + " | ".join(cells) + " |")
    P.add("")
    pending = [lim for lim in lims if lim.pending]
    if pending:
        P.add(f"**The menu** (the best P inside every limit) is not read: {len(pending)} of {len(lims)} limits wait "
              "for the operator's approval.", "")
    else:
        ok = [k for k in keys if inside[k]]
        if ok:
            best = max(ok, key=lambda k: rows.value("scorecard", k, VERDICT, OFF, ALL, "P"))
            P.add("**The menu**: inside every approved limit -- " + ", ".join(short[k] for k in ok)
                  + f"; the best P among them: {short[best]}.", "")
        else:
            P.add("**The menu**: no design is inside every approved limit.", "")
    P.add("### Each design's P under the firm's responses (beside)", "")
    image("responses.png", "P for each design under each firm response, the verdict view marked", "responses", {},
          caption(""))
    P.add("### Net cash at each month end across start days", "")
    image("net_months.png", "Net cash at months 1 to 12 across start days for each design: the middle and the bands "
          "holding half and eight in ten of the start days", "net_months", {}, caption(" Each start day's long "
                                                                                       "replay, the verdict view."))

    # -- each design
    for d in spec.designs:
        k = d.key
        P.add(f"## {d.label if d.label.startswith(d.short) else f'{d.short}: {d.label}'}", "")
        t0 = starts.table(k, VERDICT, OFF)
        n0 = P.cell(T_, ("rows", k, VERDICT, OFF), "count", f"{d.short} | start days in the file")
        P.add(f"{n0} start days, {t0['start_date'].iloc[0]} to {t0['start_date'].iloc[-1]}. Every table is the "
              "verdict view unless it says beside; each figure reads the start days with enough sessions left for "
              "it.", "")
        bl = _blocks(rows, k)

        P.add("### P and the money, month by month", "",
              "| What | " + " | ".join(w for _, w in bl) + " |", "|---|" + "---:|" * len(bl))
        extra = [(f"share_ahead_month_{m}", f"Start days ahead at the end of month {m}", "percent") for m in P_MONTHS]
        extra += [("P", "**P**: the three months' shares averaged", "percent")]
        extra += [(f"mean_net_month_{m}", f"Average net cash at the end of month {m} ($)", "dollars") for m in P_MONTHS]
        extra += [("cvar10_net_month_3", "Average month-3 net cash of the unluckiest tenth of start days (CVaR10, $)",
                   "dollars")]
        for lim in UR.BANKROLL_LIMITS:
            extra += [(f"P_bankroll_{int(lim)}", f"P counting a start day ahead only if it spent at most "
                       f"${lim:,.0f} before its first payout", "percent"),
                      (f"share_spent_over_{int(lim)}", f"Start days that spent more than ${lim:,.0f} before their "
                       "first payout", "percent")]
        extra += [("n_eff_bartlett", "About how many independent start days P rests on (the effective number)",
                   "stretch"),
                  ("n_nonoverlapping", "Separate three-month stretches among the start days read", "stretch")]
        for name, words, unit in extra:
            cells = [P.cell(S_, row("extra", k, VERDICT, OFF, b, name), unit, f"{d.short} | {b} | {name}")
                     for b, _ in bl]
            P.add(f"| {words} | " + " | ".join(cells) + " |")
        cells = [P.cell(S_, ("n", "extra", k, VERDICT, OFF, b, "P", "value"), "count",
                        f"{d.short} | {b} | P start days", blank="0") for b, _ in bl]
        P.add("| Start days read (three months left) | " + " | ".join(cells) + " |", "")
        mdd = rows.get("extra", k, VERDICT, OFF, ALL, "mdd_P")
        neff = rows.get("extra", k, VERDICT, OFF, ALL, "n_eff_bartlett")[2]
        P.add("*The minimum detectable difference in P is blank in the file" + (f" -- the writer's note: {mdd[2]}"
                                                                               if mdd[2] else "") + ". The effective "
              "number" + (f": {neff}" if neff else "") + ".*", "")

        P.add("### Time and money to the first pass, the first payout and break-even", "")
        for b, w in bl:
            P.add(f"**{w}.**", "",
                  "| What | Low end (p10) | p25 | Middle (median) | p75 | High end (p90) | Spread (p90 less p10) | "
                  "Never there inside the window | Start days read |", "|---|" + "---:|" * 8)
            for name, words, unit, window in JOURNEY:
                n = rows.get("path", k, VERDICT, OFF, b, name, "p50")[1]
                col = JOURNEY_COLUMN[name]

                def q(stat: str) -> str:
                    if stat in ("p10", "p50", "p90"):
                        ask = row("path", k, VERDICT, OFF, b, name, stat)
                        if window is not None:
                            return P.days(S_, ask, f"{d.short} | {b} | {name} | {stat}", window, n)
                        return P.cell(S_, ask, unit, f"{d.short} | {b} | {name} | {stat}")
                    ask = ("q", k, VERDICT, OFF, b, col, stat)
                    if window is not None:
                        return P.days(T_, ask, f"{d.short} | {b} | {name} | {stat}", window, n)
                    return P.cell(T_, ask, unit, f"{d.short} | {b} | {name} | {stat}")

                cells = [q(s) for s in ("p10", "p25", "p50", "p75", "p90")]
                cells.append(P.cell(S_, ("spread", "path", k, VERDICT, OFF, b, name), unit,
                                    f"{d.short} | {b} | {name} | spread"))
                if window is not None:
                    cells.append(P.cell(S_, ("never", "path", k, VERDICT, OFF, b, name, f"share_by_{window}"),
                                        "percent", f"{d.short} | {b} | {name} | never within {window}"))
                else:
                    cells.append("--")
                cells.append(P.num(n, "count", f"{d.short} | {b} | {name} | start days read", S_,
                                   ("n", "path", k, VERDICT, OFF, b, name, "p50")) if n else "0")
                P.add(f"| {words} | " + " | ".join(cells) + " |")
            P.add("")
        P.add("*Sessions to the first pass and payout read the start days with "
              f"{FIRST_WINDOW} sessions left, break-even those with {YEAR_WINDOW}; the cash before an event reads "
              f"those that got there within {FIRST_WINDOW}. \"--\": the spread cannot be read (its high end is after "
              "the window). The cash out of pocket before break-even is not in the file. p25 and p75 are read from "
              "the per-start file, the rest from the summary.*", "")

        P.add("### Back to break-even, month by month", "",
              "| | " + " | ".join(f"Month {m}" for m in UR.BREAK_EVEN_MONTHS) + " | Fell below zero again later |",
              "|---|" + "---:|" * (len(UR.BREAK_EVEN_MONTHS) + 1))
        for b, w in bl:
            cells = [P.cell(S_, row("path", k, VERDICT, OFF, b, "break_even", f"share_by_month_{m}"), "percent",
                            f"{d.short} | {b} | back to break-even by month {m}") for m in UR.BREAK_EVEN_MONTHS]
            cells.append(P.cell(S_, row("path", k, VERDICT, OFF, b, "break_even", "share_fell_back"), "percent",
                                f"{d.short} | {b} | fell back"))
            P.add(f"| {w}: back to break-even at least once by then | " + " | ".join(cells) + " |")
        P.add("", "*\"Fell below zero again later\": of the start days back to break-even within the year, the share "
              "whose net cash later closed below zero.*", "")

        P.add("### How even the year is", "",
              "Per start day with the whole year left (" + f"{YEAR_WINDOW} sessions), then spread across start days.",
              "", "| What | " + " | ".join(f"{w}: low end | {w}: middle | {w}: high end | {w}: average"
                                          for _, w in bl) + " |", "|---|" + "---:|---:|---:|---:|" * len(bl))
        for name, words, unit in EVENNESS:
            cells = []
            for b, _ in bl:
                cells += [P.cell(S_, row("path", k, VERDICT, OFF, b, name, f"p{p}"), unit,
                                 f"{d.short} | {b} | {name} | p{p}") for p in M.PERCENTILES]
                mean = ("path", k, VERDICT, OFF, b, name, "mean")
                cells.append(P.cell(S_, ("row", *mean), unit, f"{d.short} | {b} | {name} | mean")
                             if ("path", k, VERDICT, OFF, b, name, "mean") in rows.by else "--")
            P.add(f"| {words} | " + " | ".join(cells) + " |")
        P.add("", "*The deepest fall reads the start days back to break-even within the year; the largest month's "
              "share those paid within it.*", "")

        P.add("### How far ahead or behind: net cash at each month end, worst to best", "",
              "From each start day's long replay (the per-start file).", "")
        for b, w in bl:
            P.add(f"**{w}.**", "", "| Month end | Worst | p10 | p25 | Middle | p75 | p90 | Best | Spread (p90 less "
                  "p10) | Start days read |", "|---|" + "---:|" * 9)
            for m in NET_MONTHS:
                col = f"net_month_{m}"
                cells = [P.cell(T_, ("q", k, VERDICT, OFF, b, col, s), "dollars", f"{d.short} | {b} | {col} | {s}")
                         for s in ("min", *(f"p{p}" for p in SPREAD_PCTS), "max", "spread")]
                cells.append(P.cell(T_, ("q", k, VERDICT, OFF, b, col, "n"), "count",
                                    f"{d.short} | {b} | {col} | start days", blank="0"))
                P.add(f"| Month {m} ($) | " + " | ".join(cells) + " |")
            P.add("")

        P.add(f"### The {WORST} worst start days (lowest net cash at month 3)", "",
              "| Start day | Net cash at month 3 ($) | Net cash at month 12 ($) | Cash before the first payout ($) | "
              "Sessions to the first payout | Sessions to break-even |", "|---|---:|---:|---:|---:|---:|")
        w = _worst(t0, ALL)
        for i in range(min(WORST, len(w))):
            r_ = w.iloc[i]

            def wc(col: str, unit: str, none: str) -> str:
                ask = ("worst", k, VERDICT, OFF, ALL, i, col)
                return P.cell(T_, ask, unit, f"{d.short} | worst {i + 1} | {col}", blank=none)

            P.add(f"| {r_['start_date']} | {wc('net_month_3', 'dollars', '--')} | "
                  f"{wc('net_month_12', 'dollars', 'not observed')} | "
                  f"{wc('spent_before_first_payout', 'dollars', 'no payout')} | "
                  f"{wc('first_payout', 'sessions', 'no payout')} | "
                  f"{wc('break_even_day', 'sessions', 'not back')} |")
        P.add("", "*\"Not observed\": fewer than 252 sessions left after that start day. \"No payout\", \"not back\": "
              "none within the sessions observed.*", "")

        resp = rows.responses_of(k, VERDICT)
        P.add("### Beside: the firm's responses", "",
              "The same design with one of the firm's programs switched on, as the engine models it -- the denial "
              "ladder, forfeiture, the Responsible Trading placement, the Focused Trader models. **Beside, never "
              "deciding**: the verdict keeps payouts never denied and the placement off (E-008 (2)). All start days.",
              "", "| Response | P | Ahead at month 3 | Average net at month 3 ($) | Unlucky tenth's month-3 net "
              "(S5a, $) | Cash before the first payout, high end (S1, $) | Acted by month 3 | Acted by month 12 | "
              "Payouts denied per start day | Cash forfeited per start day ($) | P, judged block |",
              "|---|" + "---:|" * 10)
        for r in resp:
            lab = response_words(r)[0]
            tag = f"{d.short} | {r}"
            cells = [P.cell(S_, row("scorecard", k, VERDICT, r, ALL, "P"), "percent", f"{tag} | P"),
                     P.cell(S_, row("extra", k, VERDICT, r, ALL, "share_ahead_month_3"), "percent",
                            f"{tag} | ahead at month 3"),
                     P.cell(S_, row("extra", k, VERDICT, r, ALL, "mean_net_month_3"), "dollars",
                            f"{tag} | mean net month 3"),
                     P.cell(S_, row("scorecard", k, VERDICT, r, ALL, "S5a"), "dollars", f"{tag} | S5a"),
                     P.cell(S_, row("scorecard", k, VERDICT, r, ALL, "S1"), "dollars", f"{tag} | S1"),
                     P.cell(S_, row("response", k, VERDICT, r, ALL, "acted", "share_by_month_3"), "percent",
                            f"{tag} | acted by month 3"),
                     P.cell(S_, row("response", k, VERDICT, r, ALL, "acted", "share_by_month_12"), "percent",
                            f"{tag} | acted by month 12"),
                     P.cell(S_, row("response", k, VERDICT, r, ALL, "payouts_denied", "mean"), "ratio",
                            f"{tag} | payouts denied"),
                     P.cell(S_, row("response", k, VERDICT, r, ALL, "cash_forfeited", "mean"), "dollars",
                            f"{tag} | cash forfeited"),
                     P.cell(S_, row("scorecard", k, VERDICT, r, JUDGED, "P"), "percent", f"{tag} | judged P")
                     if ("scorecard", k, VERDICT, r, JUDGED, "P", "value") in rows.by else "--"]
            P.add(f"| {lab} | " + " | ".join(cells) + " |")
        P.add("", "What each response is:", "")
        P.add(*[f"- **{response_words(r)[0]}**: {response_words(r)[1]}." for r in resp], "")
        P.add("*\"Acted\": the share of start days on which the response had acted (its first denial, placement or "
              "forfeiture) by that month end. \"--\": not this response's (no cash is forfeited without "
              "forfeiture).*", "")

        if BESIDE in rows.arms and OFF in rows.responses_of(k, BESIDE):
            P.add("### Beside: the as-traded reading", "",
                  "The same design with every trade's result as it happened (Stage 2's point arm), payouts never "
                  "denied, placement off -- beside the cautious reading the charter judges on.", "",
                  "| What | Cautious (the verdict view) | As traded (beside) |", "|---|---:|---:|")
            for key in ("P", "S1", "S3a", "S5a", "S4b"):
                words, unit = R.SCORE_WORDS[key]
                cells = [P.cell(S_, row("scorecard", k, arm, OFF, ALL, key), unit, f"{d.short} | {arm} | {key}")
                         for arm in (VERDICT, BESIDE)]
                P.add(f"| {key}: {words} | " + " | ".join(cells) + " |")
            P.add("")

    P.add("## How the numbers on this page are kept honest", "",
          "Every number above is computed from the two files when the page is built and registered in "
          "`extended/trace.py`; `python scripts/trace_check.py` recomputes each one from its file, after checking "
          "its manifest, and finds it on this page. Dates, the manifests' identifiers, the windows, the months, the "
          "responses' parameters and the bankroll limits are the readings' definitions, not results.")
    return Composed(P.text(), P.claims, charts)


# ------------------------------------------------------------------------------------------------ the charts


def _draw_responses(plt, path: Path, spec: Any, data: Data) -> None:
    rows = data.rows
    keys = [d.key for d in spec.designs]
    names = rows.responses_of(spec.r_star, VERDICT)
    fig, ax = plt.subplots(figsize=(9.5, 0.42 * len(names) + 1.8))
    y = np.arange(len(names))[::-1]
    for i, d in enumerate(spec.designs):
        x = [100 * rows.value("scorecard", d.key, VERDICT, r, ALL, "P") if r in rows.responses_of(d.key, VERDICT)
             else np.nan for r in names]
        ax.scatter(x, y + (i - (len(keys) - 1) / 2) * 0.18, s=46, color=R.COLORS[i % len(R.COLORS)],
                   marker=R.MARKERS[i % len(R.MARKERS)], edgecolor=R.BLACK, lw=0.5, zorder=3, label=d.short)
    ax.set_yticks(y)
    ax.set_yticklabels([response_words(r)[0] for r in names], fontsize=8.5)
    ax.axhspan(y[0] - 0.45, y[0] + 0.45, color="#eeeeee", zorder=0)
    ax.set_xlabel("Start days ahead, months 1 to 3 averaged (P, %) -- all start days, the cautious reading")
    ax.set_title("P under each firm response (the shaded row is the verdict view; the rest are beside)", loc="left")
    ax.legend(loc="lower right", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(path, dpi=110, metadata={"Software": None})
    plt.close(fig)


def _draw_net_months(plt, path: Path, spec: Any, data: Data) -> None:
    from matplotlib.ticker import FuncFormatter

    n = len(spec.designs)
    fig, axes = plt.subplots(1, n, figsize=(4.0 * n + 0.6, 4.2), sharey=True, squeeze=False)
    for i, d in enumerate(spec.designs):
        ax = axes[0][i]
        t = data.starts.table(d.key, VERDICT, OFF)
        q = np.array([[starts_value(data.starts, ("q", d.key, VERDICT, OFF, ALL, f"net_month_{m}", f"p{p}"))
                       for m in NET_MONTHS] for p in SPREAD_PCTS])
        x = np.array(NET_MONTHS, float)
        c = R.COLORS[i % len(R.COLORS)]
        ax.fill_between(x, q[0], q[4], color=c, alpha=0.22, lw=0, label="8 in 10 start days (p10 to p90)")
        ax.fill_between(x, q[1], q[3], color=c, alpha=0.45, lw=0, label="half of start days (p25 to p75)")
        ax.plot(x, q[2], color=R.BLACK, lw=2, marker=R.MARKERS[i % len(R.MARKERS)], ms=5, label="the middle (median)")
        ax.axhline(0, color=R.VERMILLION, ls="--", lw=1.4, label="break-even: net cash = 0")
        ax.set_xticks(list(NET_MONTHS))
        ax.set_xlabel("Months since the start day")
        ax.set_title(f"{d.short} ({len(t):,d} start days)", loc="left")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
        if i == 0:
            ax.set_ylabel("Net cash so far (US dollars)")
            ax.legend(loc="upper left", fontsize=8)
    fig.suptitle("Net cash at each month end across start days (the verdict view)", x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=110, metadata={"Software": None})
    plt.close(fig)


def _draw(plt, chart: R.Chart, out: Path, spec: Any, data: Data) -> Path:
    path = out / chart.file
    with plt.rc_context(R.STYLE):
        if chart.kind == "responses":
            _draw_responses(plt, path, spec, data)
        elif chart.kind == "net_months":
            _draw_net_months(plt, path, spec, data)
        else:
            raise KeyError(chart.kind)
    return path


# ------------------------------------------------------------------------------------------------ the identity


def u1_identity(spec: Any, rows: Rows, root: Path | str = ROOT) -> tuple[int, list[str]]:
    """The verdict view's scorecard (every response off) against Stage 2's own scorecard of its U1 start rows
    (`spec.identity_u1`, read as `extended.report.Starts` reads it: `u_select.records_from_start_rows`), every design,
    both arms, all start days (`u_select.scorecard`) and the judged block (`u_select.scorecard(..., "late")`): (the
    comparisons made, the differences)."""
    path = Path(spec.identity_u1)
    path = path if path.is_absolute() else Path(root) / path
    df = _read(path)
    start = df[df["section"].astype(str) == "start"]
    compared, out = 0, []
    for d in spec.designs:
        for arm in U.ARMS:
            if OFF not in rows.responses_of(d.key, arm):
                out.append(f"{d.key} {arm}: no rows with every response off")
                continue
            mine = start[(start["config"].astype(str) == d.key) & (start["arm"].astype(str) == arm)]
            if not len(mine):
                out.append(f"{d.key} {arm}: Stage 2's file has no start rows")
                continue
            st = R.Starts.of(mine)
            for b, card in ((ALL, S.scorecard(st.records)), (JUDGED, S.scorecard(st.records, S.LATE))):
                for key, v in card.items():
                    got, n, _ = rows.get("scorecard", d.key, arm, OFF, b, key)
                    compared += 1
                    if not (_same(got, float(v["value"]), 1e-9 * max(1.0, abs(float(v["value"]))))
                            and int(n) == int(v["n"])):
                        out.append(f"{d.key} {arm} {b} {key}: the file {got!r} on {n:g}, Stage 2 {v['value']!r} on "
                                   f"{v['n']}")
    return compared, out


# ------------------------------------------------------------------------------------------------ build and trace


def compose_text(spec: Any, *, root: Path | str = ROOT) -> str:
    return compose(spec, load(spec, root), root=root).text


def build(spec: Any, *, root: Path | str = ROOT, out: Path | str | None = None) -> R.Built:
    """Read both files (manifests first), hold them to the writer, to each other and (registered) to Stage 2, compose
    the page, draw its charts, write `<out>/README.md`. Refuses (raises) before writing anything."""
    data = load(spec, root)
    ident = None
    if spec.identity_u1:
        ident = u1_identity(spec, data.rows, root)
        if ident[1]:
            raise ReportError(f"the verdict view is not Stage 2's U1 scorecard ({len(ident[1])} of {ident[0]} "
                              "differ): " + "; ".join(ident[1][:4]))
    composed = compose(spec, data, root=root, identity=ident)
    folder = Path(out) if out is not None else Path(root) / spec.out_dir
    folder.mkdir(parents=True, exist_ok=True)
    drawn: list[Path] = []
    if composed.charts:
        plt = R._pyplot()
        if plt is None:
            raise ReportError("matplotlib is installed but cannot be loaded: nothing written")
        drawn = [_draw(plt, c, folder, spec, data) for c in composed.charts]
    for old in folder.glob("*.png"):
        if old not in drawn:
            old.unlink()
    page = folder / R.PAGE
    page.write_text(composed.text, encoding="utf-8", newline="\n")
    return R.Built(page, drawn, composed.claims)


class _Recompute:
    """A claim's value from the frame the trace check hands over (its file read through the vendored `read_result`,
    the manifest checked first)."""

    def __init__(self, claim: Claim):
        self.claim = claim

    def __call__(self, df: pd.DataFrame) -> float:
        c = self.claim
        return value_of(c.kind, c.ask, _index(df, c.kind))


def traced_numbers(spec: Any, *, root: Path | str = ROOT) -> list[TracedNumber]:
    """Every number the page prints as a `TracedNumber`, recomputed from its own file and looked for on the page."""
    composed = compose(spec, load(spec, root), root=root)
    doc = R.page_path(spec, root).relative_to(Path(root)).as_posix()
    return [TracedNumber(label=f"{spec.name}: {c.label}", source_csv=str(Path(c.source).resolve()),
                         recompute=_Recompute(c), documents=(doc,), decimals=c.decimals, as_percent=c.as_percent,
                         tolerance=0.5 * 10 ** (-c.decimals)) for c in composed.claims]


__all__ = ["LIMITS", "Limit", "Rows", "StartRows", "Data", "Claim", "load", "compose", "compose_text", "build",
           "traced_numbers", "u1_identity", "cross_problems", "pairing_problems", "schema_problems",
           "response_words", "summary_value", "starts_value", "starts_path"]
