"""The licence guard on committed tables (Q-131, E-179/E-180): no tracked or staged CSV holds or reveals an NQ price level.

    from extended.price_levels import check_tree, load_allowlist
    report = check_tree(ROOT)                      # the working tree's copy of every candidate file
    report = check_tree(ROOT, source="index")      # the index's copy (what a commit would record) -- the hook's mode
    report.refused, report.stale, report.files, report.seconds

The bars are licensed for private use (CLAUDE.md, E-002): a committed file that holds a price level, or lets one be
recomputed, redistributes them. Q-130's scan found the one offender (`results/q121_vol_descriptive_a1.csv`, never
committed): a points column beside its percentage, so `100 * range_pts / range_pct` is the session's first open. This
module is the automated form of that scan's method; `tests/test_results_no_price_levels.py` runs it in the fast tier and
`scripts/check_price_levels.py --index` runs it in the pre-commit hook on the commit's own index.

**What is scanned.** Every path in the index (tracked or staged) ending in `.csv` or `.tsv` and not under `vendor/`
(which holds `results/*.csv`). Lines starting with `#` are comments (the calendars' headers) and are skipped. Only the
header and the first `SAMPLE_ROWS` data rows of a file are read, so the check stays fast on the large result files.

**The rules** (each finding names a file, a rule, a column or column pair and a share -- never a value):

- `name`: a column named as a level -- a token of its name (split on `_`, `-`, spaces, dots and case changes) is one of
  `LEVEL_TOKENS` (open, high, low, close, price, vwap, settle, bid, ask, ...), or the name pairs an entry, exit, fill,
  stop or target with `level` / `lvl`. Whatever the column holds.
- `level`: a column whose non-empty cells are mostly numbers inside the NQ level band `BAND` and on the 0.25 tick grid
  (within `GRID_TOL` of a tick). "Mostly" (`_mostly`): at least `MOSTLY` (half) of the cells judged, and at least
  `MIN_HITS` of them (every row, in a table of fewer rows).
- `pair`: an ordered pair of numeric columns (a, b) for which `m * a / b`, for `m` in `MULTIPLIERS` (1, a ratio; 100,
  a percentage), is mostly in the band and on the grid over the rows where both are numbers and b is not zero. It
  catches a points column beside its percentage (`x_pts` / `x_pct`: `100 * x_pts / x_pct` is the level) and a sum of
  points over a count (a mean level). Reported as `a/b` or `100*a/b`. (Basis points, `10000 * a / b`, were tried and
  dropped: on the tracked files they fire about four hundred times, almost all on ratios of counts near one.)
- `timestamp`: a column of intraday timestamps (cells mostly a clock time or a date with a clock time not all
  midnight, or a name token in `TIMESTAMP_TOKENS`) in a file that also has a price-class column: one refused under
  `name`, `level` or `pair` and not allow-listed, or one named for a distance in points or ticks (`DISTANCE_TOKENS`) --
  a distance at each intraday time can rebuild a path. Reported as `ts|column`.

**The allow-list** (`config/price_level_allowlist.csv`, columns `file,rule,column,reason`): a finding is accepted only
when an entry names its file and rule exactly and its column exactly or by an `fnmatch` pattern (`*/p`: any pair over
the column `p`), with a reason classing the columns by their meaning (a count, a dollar figure, a significance level,
a clock time, a ratio that is 1/level by construction), seeded from Q-130's judged false positives. An entry that
matches no finding is **stale** and the test fails on it, so the list cannot outlive what it classed. An allow-listed
finding is not a price-class column for the timestamp rule.

**Not covered** (said so the guard is not over-trusted): rows after the first `SAMPLE_ROWS`; a long-format table whose
`value` column mixes units (each unit's rows are judged together with the rest); a level rescaled by anything other
than 1 or 100; a level rounded off the tick grid; files that are not `.csv`/`.tsv` (JSON, Parquet, images).

Light code: the standard library, numpy and `git`. Nothing here prints or returns a cell's value.
"""
from __future__ import annotations

import csv
import fnmatch
import io
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_REL = "config/price_level_allowlist.csv"

#: the NQ level band (index points) and its tick; Q-130's scan used the same band
BAND = (5000.0, 30000.0)
TICK = 0.25
#: a value is on the grid when value / TICK is within this of an integer (a twenty-fifth of a tick each side)
GRID_TOL = 0.02
#: "mostly": at least this share of the cells (or formable rows) a rule is judged over
MOSTLY = 0.5
#: and at least this many hits (or every row, in a table of fewer rows): one coincidence in a sparse column is not
#: "mostly" -- a table whose rows are levels repeats them
MIN_HITS = 3
#: data rows read per file (after the header)
SAMPLE_ROWS = 1000
#: the scale factors of the pair rule: a ratio, a percentage
MULTIPLIERS = (1.0, 100.0)

LEVEL_TOKENS = frozenset({
    "open", "opens", "high", "highs", "low", "lows", "close", "closes", "price", "prices", "px", "vwap", "twap",
    "settle", "settles", "settlement", "ohlc", "ohlcv", "bid", "ask", "hod", "lod", "quote", "quotes",
})
_LEVEL_SIDE = frozenset({"entry", "exit", "fill", "stop", "target", "limit"})
_LEVEL_WORD = frozenset({"level", "lvl", "levels"})
DISTANCE_TOKENS = frozenset({"pts", "points", "point", "ticks", "tick"})
TIMESTAMP_TOKENS = frozenset({"ts", "timestamp", "timestamps", "datetime"})

SUFFIXES = (".csv", ".tsv")
RULES = ("name", "level", "pair", "timestamp")

_TIME_RE = re.compile(
    r"^\s*(?:(?P<date>\d{4}-\d{2}-\d{2})[ T])?(?P<h>\d{1,2}):(?P<m>\d{2})(?::(?P<s>\d{2})(?:\.\d+)?)?"
    r"\s*(?:Z|[+-]\d{2}:?\d{2}|[A-Za-z]{2,4})?\s*$")
_SPLIT_RE = re.compile(r"[^A-Za-z0-9]+")
_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


@dataclass(frozen=True)
class Finding:
    file: str
    rule: str
    column: str
    share: float

    def __str__(self) -> str:                      # names and a share only
        return f"{self.file}: {self.rule} {self.column} (share {self.share:.2f})"


@dataclass(frozen=True)
class Allow:
    file: str
    rule: str
    column: str
    reason: str

    def key(self) -> tuple[str, str, str]:
        return (self.file, self.rule, self.column)

    def accepts(self, f: "Finding") -> bool:
        """Same file and rule; the column equal, or matching the entry's `fnmatch` pattern (`*`, `?`)."""
        return f.file == self.file and f.rule == self.rule and fnmatch.fnmatchcase(f.column, self.column)


@dataclass
class Report:
    files: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    refused: list[Finding] = field(default_factory=list)
    stale: list[Allow] = field(default_factory=list)
    seconds: float = 0.0


# ---------------------------------------------------------------------------------------------------- names and cells

def name_tokens(name: str) -> list[str]:
    parts = _SPLIT_RE.split(_CAMEL_RE.sub("_", name.strip()))
    return [p.lower() for p in parts if p]


def is_level_name(name: str) -> bool:
    toks = name_tokens(name)
    if any(t in LEVEL_TOKENS for t in toks):
        return True
    return any(t in _LEVEL_SIDE for t in toks) and any(t in _LEVEL_WORD for t in toks)


def is_distance_name(name: str) -> bool:
    return any(t in DISTANCE_TOKENS for t in name_tokens(name))


def _to_float(cell: str) -> float:
    s = cell.strip()
    if not s:
        return np.nan
    try:
        v = float(s)
    except ValueError:
        return np.nan
    return v if np.isfinite(v) else np.nan


def on_level(x: np.ndarray, band: tuple[float, float] = BAND, tick: float = TICK) -> np.ndarray:
    """True where x is a number inside the band and on the tick grid (NaN is never)."""
    with np.errstate(invalid="ignore"):
        q = x / tick
        return np.isfinite(x) & (x >= band[0]) & (x <= band[1]) & (np.abs(q - np.rint(q)) <= GRID_TOL)


def _mostly(hits: int, denom: int, nrow: int) -> bool:
    return denom > 0 and hits >= MOSTLY * denom and hits >= min(MIN_HITS, nrow)


def _is_intraday(name: str, cells: Sequence[str]) -> bool:
    if any(t in TIMESTAMP_TOKENS for t in name_tokens(name)):
        return True
    vals = [c for c in cells if c.strip()]
    if not vals:
        return False
    matches = [m for m in (_TIME_RE.match(c) for c in vals) if m is not None]
    if len(matches) < MOSTLY * len(vals):
        return False
    # a date column written with a midnight time is a date, not an intraday stamp
    return any(not (int(m["h"]) == 0 and int(m["m"]) == 0 and int(m["s"] or 0) == 0) for m in matches)


# ------------------------------------------------------------------------------------------------------- one table

def scan_table(file: str, header: Sequence[str], rows: Sequence[Sequence[str]], *,
               allow: Iterable[Allow] = (), band: tuple[float, float] = BAND, tick: float = TICK) -> list[Finding]:
    """Every finding of the four rules on one table (the allow-list is used only to decide price class for the
    timestamp rule; the caller filters the findings themselves)."""
    header = [h.strip() for h in header]
    ncol = len(header)
    cells = [[(r[j] if j < len(r) else "") for r in rows] for j in range(ncol)]
    found: list[Finding] = []

    for j, name in enumerate(header):
        if is_level_name(name):
            found.append(Finding(file, "name", name, 1.0))

    nrow = len(rows)
    if nrow and ncol:
        M = np.array([[_to_float(c) for c in col] for col in cells], dtype=float).T      # (rows, cols)
        fin = np.isfinite(M)
        nonempty = np.array([[bool(c.strip()) for c in col] for col in cells], dtype=bool).T
        # level: share of non-empty cells in band and on grid
        hits = on_level(M, band, tick).sum(axis=0)
        denom = nonempty.sum(axis=0)
        for j, name in enumerate(header):
            if denom[j] and _mostly(hits[j], denom[j], nrow):
                found.append(Finding(file, "level", name, float(hits[j] / denom[j])))
        # pairs: m * a / b over the rows where both are numbers and b != 0
        numeric = [j for j in range(ncol) if fin[:, j].any()]
        if len(numeric) >= 2:
            A = M[:, numeric]
            FA = fin[:, numeric]
            for jb_i, jb in enumerate(numeric):
                b = M[:, jb]
                ok_b = np.isfinite(b) & (b != 0)
                if not ok_b.any():
                    continue
                form = FA & ok_b[:, None]
                nform = form.sum(axis=0)
                with np.errstate(divide="ignore", invalid="ignore"):
                    R = np.where(form, A / np.where(ok_b, b, 1.0)[:, None], np.nan)
                for m in MULTIPLIERS:
                    h = on_level(R * m, band, tick).sum(axis=0)
                    for ja_i in np.flatnonzero((nform > 0) & (h >= MOSTLY * nform) & (h >= min(MIN_HITS, nrow))):
                        if ja_i == jb_i:
                            continue
                        a = header[numeric[ja_i]]
                        lab = f"{a}/{header[jb]}" if m == 1.0 else f"{m:g}*{a}/{header[jb]}"
                        found.append(Finding(file, "pair", lab, float(h[ja_i] / nform[ja_i])))

    # timestamps beside a price-class column
    allow = list(allow)
    price_cols: set[str] = set()
    for f in found:
        if any(a.accepts(f) for a in allow):
            continue
        if f.rule in ("name", "level"):
            price_cols.add(f.column)
        elif f.rule == "pair":
            ab = f.column.split("*", 1)[-1]
            price_cols.update(ab.split("/", 1))
    price_cols.update(h for h in header if is_distance_name(h))
    for j, name in enumerate(header):
        if _is_intraday(name, cells[j]):
            for pc in sorted(price_cols - {name}):
                found.append(Finding(file, "timestamp", f"{name}|{pc}", 1.0))
    return found


def read_sample(lines: Iterable[str], *, delimiter: str = ",", sample_rows: int = SAMPLE_ROWS
               ) -> tuple[list[str], list[list[str]]]:
    """The header and up to `sample_rows` data rows of a delimited text, '#' comment lines skipped."""
    def body() -> Iterator[str]:
        for line in lines:
            if line.lstrip("﻿").startswith("#"):
                continue
            yield line.lstrip("﻿") if line.startswith("﻿") else line
    reader = csv.reader(body(), delimiter=delimiter)
    header: list[str] = []
    rows: list[list[str]] = []
    for row in reader:
        if not header:
            if row:
                header = row
            continue
        if not row:
            continue
        rows.append(row)
        if len(rows) >= sample_rows:
            break
    return header, rows


def scan_lines(file: str, lines: Iterable[str], *, allow: Iterable[Allow] = (),
               sample_rows: int = SAMPLE_ROWS) -> list[Finding]:
    delim = "\t" if file.lower().endswith(".tsv") else ","
    header, rows = read_sample(lines, delimiter=delim, sample_rows=sample_rows)
    return scan_table(file, header, rows, allow=allow)


def scan_path(path: Path | str, *, name: str | None = None, allow: Iterable[Allow] = (),
              sample_rows: int = SAMPLE_ROWS) -> list[Finding]:
    p = Path(path)
    with open(p, encoding="utf-8", errors="replace", newline="") as fh:
        return scan_lines(name or p.as_posix(), fh, allow=allow, sample_rows=sample_rows)


# ----------------------------------------------------------------------------------------------------- the allow-list

def load_allowlist(path: Path | str | None = None) -> list[Allow]:
    p = Path(path) if path is not None else ROOT / ALLOWLIST_REL
    with open(p, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(line for line in fh if not line.startswith("#")))
    out: list[Allow] = []
    seen: set[tuple[str, str, str]] = set()
    for i, r in enumerate(rows, start=2):
        a = Allow(*(str(r.get(k) or "").strip() for k in ("file", "rule", "column", "reason")))
        if not (a.file and a.rule and a.column and a.reason):
            raise ValueError(f"{p.name} entry {i}: file, rule, column and reason are all required")
        if a.rule not in RULES:
            raise ValueError(f"{p.name} entry {i}: rule {a.rule!r} is not one of {RULES}")
        if a.key() in seen:
            raise ValueError(f"{p.name} entry {i}: a duplicate of an earlier entry")
        seen.add(a.key())
        out.append(a)
    return out


def apply_allowlist(findings: Sequence[Finding], allow: Sequence[Allow]) -> tuple[list[Finding], list[Allow]]:
    """(the findings no entry accepts, the entries that accepted none -- stale)."""
    used = [False] * len(allow)
    refused: list[Finding] = []
    for f in findings:
        hit = False
        for i, a in enumerate(allow):
            if a.accepts(f):
                used[i] = hit = True
        if not hit:
            refused.append(f)
    return refused, [a for a, u in zip(allow, used) if not u]


# ---------------------------------------------------------------------------------------------------------- the tree

def _git(root: Path, *args: str, env: Mapping[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, timeout=60, env=env)


def _git_env(index_file: str | None) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_PREFIX")}
    env.pop("GIT_INDEX_FILE", None)
    if index_file:
        env["GIT_INDEX_FILE"] = str(Path(index_file).absolute())     # git may hand a hook a relative path
    return env


def is_candidate(path: str) -> bool:
    return path.lower().endswith(SUFFIXES) and not path.startswith("vendor/")


def candidate_entries(root: Path, index_file: str | None = None) -> list[tuple[str, str]]:
    """(path, blob sha) of every index entry the guard covers: tracked or staged, `.csv`/`.tsv`, outside `vendor/`."""
    out = _git(root, "ls-files", "-s", "-z", env=_git_env(index_file))
    if out.returncode:
        raise RuntimeError(f"git ls-files failed in {root}: {out.stderr.decode(errors='replace').strip()}")
    entries: list[tuple[str, str]] = []
    for rec in out.stdout.decode("utf-8", errors="replace").split("\0"):
        if not rec:
            continue
        meta, path = rec.split("\t", 1)
        mode, sha, stage = meta.split()
        if stage in ("0", "2") and is_candidate(path):
            entries.append((path, sha))
    return sorted(set(entries))


def _blob_lines(root: Path, sha: str, sample_rows: int) -> list[str]:
    """The first lines of a blob, enough for the header, comments and the sample; the rest is not read."""
    proc = subprocess.Popen(["git", "cat-file", "blob", sha], cwd=root, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, env=_git_env(None))
    lines: list[str] = []
    data_lines = 0
    try:
        assert proc.stdout is not None
        text = io.TextIOWrapper(proc.stdout, encoding="utf-8", errors="replace", newline="")
        for line in text:
            lines.append(line)
            if not line.startswith("#"):
                data_lines += 1
                if data_lines > sample_rows + 1:
                    break
    finally:
        proc.kill()
        proc.wait(timeout=30)
    return lines


def check_tree(root: Path | str = ROOT, *, source: str = "worktree", index_file: str | None = None,
               allow: Sequence[Allow] | None = None, allowlist: Path | str | None = None,
               sample_rows: int = SAMPLE_ROWS) -> Report:
    """Scan every candidate file of `root` and judge the findings against the allow-list.

    `source="worktree"` reads the working tree's copy (the index's when the file is missing from the working tree);
    `source="index"` reads the index's blob -- what a commit records -- from `index_file` (the hook passes git's
    GIT_INDEX_FILE) or the default index."""
    if source not in ("worktree", "index"):
        raise ValueError("source is 'worktree' or 'index'")
    root = Path(root)
    t0 = time.perf_counter()
    if allow is None:
        allow = load_allowlist(allowlist if allowlist is not None else root / ALLOWLIST_REL)
    rep = Report()
    for path, sha in candidate_entries(root, index_file):
        rep.files.append(path)
        wt = root / path
        if source == "worktree" and wt.is_file():
            rep.findings.extend(scan_path(wt, name=path, allow=allow, sample_rows=sample_rows))
        else:
            rep.findings.extend(scan_lines(path, _blob_lines(root, sha, sample_rows), allow=allow,
                                           sample_rows=sample_rows))
    rep.refused, rep.stale = apply_allowlist(rep.findings, allow)
    rep.seconds = time.perf_counter() - t0
    return rep
