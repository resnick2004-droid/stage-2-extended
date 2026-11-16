"""R11's acceptance: a completed registration's own computation rerun on today's engine and compared, file for file,
with its registered result -- a reproduction, never a verdict.

    python scripts/reproduce_registered.py --prereg P-09                  # the full reproduction, the registered paths
    python scripts/reproduce_registered.py --prereg P-11 --paths 3        # a smoke: each campaign's first 3 paths
    python scripts/reproduce_registered.py --prereg P-06 --compare-only   # compare an earlier reproduction's files again
        [--out DIR]       # default %LOCALAPPDATA%/stage2-repro/<id>, outside the repository

**What runs** (NEXT_STEPS R11: "P-06, P-09 and P-10 reproduce exactly from their captures", after the engine changes
of D-465, D-467, D-470 and D-478; P-11 beside them): the registration's registered script -- the result manifest's
`script`, checked -- through the same functions its `main` calls after the registration check, with its registered
spec, seed and parameters and the same inputs (`results/`, `runs/`, the git-ignored stores under `data/`):

    P-06  scripts/confirm_fv3.py   `main` (the captures R139-R141)            fv3_confirmation.csv + its _paths.csv
    P-09  scripts/t24_gf15b.py     its identity with P-08, then `t24_gf15._registered_run` under its SPEC
                                                                               t24_gf15b_gate.csv
    P-10  scripts/t24_confirm.py   its development-verdict check, then its `_registered_run` (the capture R152)
                                                                               t24_confirmation.csv
    P-11  scripts/a1_ins15.py      its trades and identity with the screen, then `t24_gf15._registered_run` under its
          SPEC (family A1's walk cache `data/atlas/A1` and the bars `data/bars/NQ`)
                                                                               a1_ins15_gate.csv + its _paths.csv

A completed registration is refused by its script's `main` (`PreregRegistry.require_runnable`), rightly: a rerun is not
a new verdict. So `main`'s registration check is not called; each script's `reproduce` keyword (the only seam, R11)
skips its variant-ledger append and writes through `propedge.reporting.reproduction.writer`: into the output directory
(outside the repository, never `results/`), `exploratory: true`, no registration id, the note "reproduction of P-xx,
not a verdict (R11)". What a run computes is the registered code's; the scripts' default path is unchanged. The
registered files and `results/variants.jsonl` are hashed before and after the run, and any change is an error.

**The comparison** reads both files with pandas' `float_precision="round_trip"` (D-471: the default parser can miss a
written value by its last digit): the same shape and the same columns in the same order; every numeric column equal
exactly (NaN equal to NaN; the count of differing cells and the largest absolute difference reported otherwise); every
other column equal value for value. `RUN_SPECIFIC` names the columns left out as inherently run-specific: none -- the
registered files carry no timestamp, commit or runtime column; those are in the sidecar manifest, which is not compared
(its labels differ by design). Each file's sha256 against the registered manifest's is reported beside. One line per
file, IDENTICAL or DIFFERS; the exit status is 0 only when every compared file is IDENTICAL.

**`--paths N`** below the registered count is a smoke, not the acceptance: every campaign runs its first N paths (a
k-path run's paths are the first k of a longer run's, D-465), so the per-path file is compared on each campaign's first
N paths, leaving out `ON_BASE` -- the columns read on the campaign's capital base, the p90 required bankroll over all
its paths -- and the result file on the rows no campaign produced (each registration's `campaign_sections` are left
out: the gate and every campaign row need all the registered paths). P-09 and P-10 wrote no per-path file (D-465), so
their smoke compares the path-free rows only.

A `reproduction.json` beside the files records the registration, the paths, the commit, the run's seconds and each
file's line; `--compare-only` reads its paths. Run each full reproduction alone with one BLAS thread (set here) on a
quiet machine; P-11's registered run took about 35 minutes in one process.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping

if __name__ == "__main__":                 # the registered runs' one BLAS thread (D-464 (5)), before numpy loads
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/reproduce_registered.py"
LOG = "reproduction.json"

#: Columns of a registered result CSV left out of the comparison as inherently run-specific, each with its reason.
#: Empty: every column of the six registered files (P-06's two, P-09's, P-10's, P-11's two) was read on 2026-10-30 and
#: none is a timestamp, a commit, a host or a runtime -- those live in the sidecar manifest (`timestamp`, `git_commit`,
#: `git_dirty`), which is not compared, nor are the labels a reproduction changes by design (`exploratory`,
#: `prereg_id`, `variant_count`, `notes`, `description`). P-11's `walk` row's hashes (`bars_parquet_sha256`,
#: `config_sha256`, `code_sha256`) are the walk cache's inputs, not the run's, and are compared.
RUN_SPECIFIC: dict[str, str] = {}

#: The per-path record's columns read on the campaign's capital base -- the p90 required bankroll over all its paths
#: (`portfolio_stage.composed_hook`, `portfolio.path_measures`) -- so a run of fewer paths has another base and these
#: are compared only at the registered count (as `tests/test_parallel_paths.py` reads P-06's first paths).
ON_BASE: dict[str, str] = {c: "read on the capital base of all the campaign's paths" for c in (
    "base", "sharpe", "sharpe_lb", "gain_to_pain", "log_growth_on_base", "growth_on_base", "sharpe_active")}


class Refused(RuntimeError):
    """The registration cannot be reproduced as asked; nothing is compared."""


# ------------------------------------------------------------------------------------------------- the registrations

@dataclass(frozen=True)
class Registered:
    """One completed registration: its script (the manifest's), its files and how its registered path is run."""

    pid: str
    script: str
    result: str
    paths_file: str | None
    campaign_sections: tuple[str, ...]          # result rows a campaign produced: compared only at the registered paths
    run: Callable[[Path, int | None], int]      # (output directory, paths or None for the registered count) -> status
    registered_paths: Callable[[], int]         # the most paths any of its campaigns runs, from the code
    notes: str = ""

    @property
    def files(self) -> tuple[str, ...]:
        return (self.result,) + ((self.paths_file,) if self.paths_file else ())


def _rd() -> Path:
    from propedge import RESULTS_DIR

    return RESULTS_DIR


@contextlib.contextmanager
def _t24_paths(n: int | None) -> Iterator[None]:
    """T24's campaigns' path count (`t24_wide.N_PATHS`, read by `t24_gf15.run`) set to `n` for the run, then restored;
    None leaves the registered count."""
    import t24_wide as tw

    old = tw.N_PATHS
    if n is not None:
        tw.N_PATHS = int(n)
    try:
        yield
    finally:
        tw.N_PATHS = old


def _t24_registered_paths() -> int:
    import t24_wide as tw

    return int(tw.N_PATHS)


def _p06_counts() -> tuple[int, int]:
    """P-06's gate campaigns' paths and its period campaigns' paths, from the frozen candidate."""
    import confirm_fv3 as cf

    cand = cf.candidate(cf.config())
    return int(cand["gate"]["campaign"]["n_paths"]), int(cand["portfolio"]["walkforward_paths"])


def run_p06(out: Path, n: int | None) -> int:
    """`confirm_fv3.main` with `reproduce`: the same window, candidate, seed and campaigns; with `n`, its test seam's
    `n_paths` and `period_paths` at the first n (or each campaign's own count, if smaller)."""
    import confirm_fv3 as cf

    kw: dict[str, Any] = {}
    if n is not None:
        gate_n, period_n = _p06_counts()
        kw = {"n_paths": min(int(n), gate_n), "period_paths": min(int(n), period_n)}
    return int(cf.main([], reproduce=out, **kw))


def run_p09(out: Path, n: int | None) -> int:
    """`t24_gf15b.main` after its registration check: the identity with P-08 (D-440), then T24-GF15b's spec."""
    import t24_gf15 as tg
    import t24_gf15b as tb

    rd = _rd()
    problems = tb.identity_with_p08(rd)
    if problems:
        raise Refused("T24-GF15b's trades are not P-08's -- " + "; ".join(problems))
    with _t24_paths(n):
        return int(tg._registered_run("P-09", rd, out, spec=tb.SPEC, reproduce=True))


def run_p10(out: Path, n: int | None) -> int:
    """`t24_confirm.main` after its registration check: the development verdict read, then its registered run."""
    import t24_confirm as tcf

    rd = _rd()
    word = tcf.development_verdict(rd)
    if word not in ("PASS", "CONTINUE"):
        raise Refused(f"T24-GF15b's development test reads {word!r}; its confirmation runs only after a PASS or a "
                      "CONTINUE")
    with _t24_paths(n):
        return int(tcf._registered_run("P-10", rd, out, reproduce=True))


def run_p11(out: Path, n: int | None) -> int:
    """`a1_ins15.main` after its registration check: the cell's trades, their identity with the screen, then A1-INS15's
    spec with those trades (exactly as `main` passes them)."""
    import a1_ins15 as a1
    import t24_gf15 as tg

    rd = _rd()
    t, days, rows = a1.trades(rd)
    problems = a1.identity_with_screen(rd, t, days)
    if problems:
        raise Refused("A1-INS15's trades are not the screen's cell -- " + "; ".join(problems))
    with _t24_paths(n):
        return int(tg._registered_run("P-11", rd, out, spec={**a1.SPEC, "trades": lambda _rd: (t, days, rows)},
                                      reproduce=True))


_T24_CAMPAIGNS = ("gate", "gate_at_ledger_n", "placement_on", "zero_edge_twin", "check_years", "verdict")

# TODO (A2-NB158, D-485): once the prereg-gatekeeper has registered A2-NB158's development test (its id is the
# gatekeeper's to assign; none is written here) and the run has completed, map it in REGISTERED below:
#   Registered("<id>", "scripts/a2_nb158.py", "a2_nb158_gate.csv", "a2_nb158_gate_paths.csv",
#              _T24_CAMPAIGNS + ("twin", "gf15b_twin"), run_<id>, _t24_registered_paths,
#              "reads data/atlas/A1 and data/bars/NQ (git-ignored); re-solves the cell's table (minutes)")
# with run_<id>(out, n) entering `_t24_paths(n)` and returning `a2_nb158.registered("<id>", _rd(), out, reproduce=True)`
# -- the script's own seam: the trades' and the table's identity with the screen, then `t24_gf15._registered_run` under
# its SPEC with `reproduce` set; a refusal there returns 3, which the mapping turns into `Refused`.
#
# TODO (A3-BRK30, D-494): likewise once A3-BRK30's development test is registered and run:
#   Registered("<id>", "scripts/a3_brk30.py", "a3_brk30_gate.csv", "a3_brk30_gate_paths.csv",
#              ("gate", "gate_at_ledger_n", "placement_on", "zero_edge_twin", "twin", "gf15b_twin", "check_years",
#               "verdict"), run_<id>, lambda: a3_brk30.N_PATHS,
#              "reads data/atlas/A1, data/atlas/A3 and data/bars/NQ (git-ignored); FV3-C's identity first")
# with run_<id>(out, n) returning `a3_brk30.registered("<id>", _rd(), out, reproduce=True)` (a smoke at n paths sets
# `a3_brk30.N_PATHS` for the call and restores it) -- the script's own seam: FV3-C's identity on A3's campaign path, the
# trades' identity with the screen, then every arm with `reproduce` set (written outside the repository, nothing appended
# to the variant ledger); a refusal returns 3, which the mapping turns into `Refused`.

REGISTERED: dict[str, Registered] = {
    "P-06": Registered("P-06", "scripts/confirm_fv3.py", "fv3_confirmation.csv", "fv3_confirmation_paths.csv",
                       ("gate", "twin", "period_campaign", "period", "line", "summary"), run_p06,
                       lambda: max(_p06_counts()),
                       "the gate's campaigns at the candidate's paths, each period's at its walk-forward paths"),
    "P-09": Registered("P-09", "scripts/t24_gf15b.py", "t24_gf15b_gate.csv", None, _T24_CAMPAIGNS, run_p09,
                       _t24_registered_paths, "no per-path file was registered (D-465)"),
    "P-10": Registered("P-10", "scripts/t24_confirm.py", "t24_confirmation.csv", None,
                       ("gate", "beside_at_ledger_n", "placement_on", "zero_edge_twin", "period_campaign", "verdict"),
                       run_p10, _t24_registered_paths, "no per-path file was registered (D-465)"),
    "P-11": Registered("P-11", "scripts/a1_ins15.py", "a1_ins15_gate.csv", "a1_ins15_gate_paths.csv", _T24_CAMPAIGNS,
                       run_p11, _t24_registered_paths, "reads data/atlas/A1 and data/bars/NQ (git-ignored)"),
}


# ---------------------------------------------------------------------------------------------------- the comparison

@dataclass
class Comparison:
    """One file's comparison: shape and column problems, and per column the differing cells and the largest absolute
    difference (numeric columns; None for a text column or a NaN/infinity against a value)."""

    name: str
    rows: int = 0
    columns: int = 0
    problems: list[str] = field(default_factory=list)
    diffs: dict[str, tuple[int, float | None]] = field(default_factory=dict)
    scope: str = ""
    byte_identical: bool | None = None

    @property
    def identical(self) -> bool:
        return not self.problems and not self.diffs

    def line(self) -> str:
        head = f"{'IDENTICAL' if self.identical else 'DIFFERS'}  {self.name}  {self.rows} rows x {self.columns} columns"
        if self.scope:
            head += f" ({self.scope})"
        if self.identical:
            out = head + ": every value equal"
            if self.byte_identical is not None:
                out += "; byte-identical to the registered file" if self.byte_identical else \
                    "; the bytes differ (the values do not)"
            return out
        parts = list(self.problems)
        for c, (n, mx) in self.diffs.items():
            parts.append(f"{c} ({n} cell{'s' if n != 1 else ''}" + (f", max abs {mx:.3g})" if mx is not None else ")"))
        return head + ": " + "; ".join(parts)


def read_exact(path: Path) -> pd.DataFrame:
    """A result CSV as written, every float to its last digit (D-471)."""
    return pd.read_csv(path, float_precision="round_trip", low_memory=False)


def _numeric(s: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s)


def _cell(v: Any) -> Any:
    """A value's comparable form outside a numeric column: missing as None, booleans and numbers as such, else text."""
    if v is None or (isinstance(v, float) and np.isnan(v)) or v is pd.NA or v is pd.NaT:
        return None
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    if isinstance(v, (int, float, np.integer, np.floating)):
        return float(v)
    return str(v)


def compare_column(a: pd.Series, b: pd.Series) -> tuple[int, float | None]:
    """How many cells differ, and the largest absolute difference among them where both columns are numeric and every
    differing pair is finite (None otherwise). Equality is exact; NaN equals NaN."""
    if _numeric(a) and _numeric(b):
        x, y = a.to_numpy(dtype=float), b.to_numpy(dtype=float)
        same = (x == y) | (np.isnan(x) & np.isnan(y))
        n = int((~same).sum())
        if not n:
            return 0, None
        d = np.abs(x[~same] - y[~same])
        return n, (float(d.max()) if np.isfinite(d).all() else None)
    n = sum(1 for u, v in zip(a.tolist(), b.tolist()) if _cell(u) != _cell(v))
    return int(n), None


def compare_frames(reg: pd.DataFrame, rep: pd.DataFrame, name: str, *, ignore: Mapping[str, str] | None = None,
                   partial: bool = False, scope: str = "") -> Comparison:
    """The registered frame against the reproduced one. In full mode the columns must be the same in the same order;
    `partial` (a subset of rows) compares the columns either frame fills in those rows, in the registered order."""
    ignore = dict(ignore or {})
    reg = reg.reset_index(drop=True)
    rep = rep.reset_index(drop=True)
    cols_reg = [c for c in reg.columns if c not in ignore]
    cols_rep = [c for c in rep.columns if c not in ignore]
    if partial:                                            # a column empty in these rows of both frames says nothing
        filled = lambda df, c: c in df.columns and bool(df[c].notna().any())   # noqa: E731
        keep = [c for c in dict.fromkeys(cols_reg + cols_rep) if filled(reg, c) or filled(rep, c)]
        cols_reg = [c for c in keep if c in reg.columns]
        cols_rep = [c for c in keep if c in rep.columns]
    out = Comparison(name, rows=len(rep), columns=len(cols_rep), scope=scope)
    missing = [c for c in cols_reg if c not in cols_rep]
    extra = [c for c in cols_rep if c not in cols_reg]
    if missing:
        out.problems.append(f"{len(missing)} registered column(s) missing: {missing[:8]}")
    if extra:
        out.problems.append(f"{len(extra)} column(s) not in the registered file: {extra[:8]}")
    if not partial and not missing and not extra and cols_reg != cols_rep:
        out.problems.append("the columns are in another order")
    if len(reg) != len(rep):
        out.problems.append(f"{len(rep)} rows against the registered {len(reg)}")
        return out
    for c in cols_reg:
        if c in cols_rep:
            n, mx = compare_column(reg[c], rep[c])
            if n:
                out.diffs[c] = (n, mx)
    return out


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_files(reg_path: Path, rep_path: Path, *, sections_out: tuple[str, ...] = (), first_paths: int | None = None,
                  is_paths_file: bool = False) -> Comparison:
    """One reproduced file against its registered one: whole at the registered paths; at fewer (`first_paths`) the
    per-path file on each campaign's first paths without `ON_BASE`, the result file without `sections_out`."""
    name = reg_path.name
    if not rep_path.is_file():
        c = Comparison(name)
        c.problems.append(f"not reproduced ({rep_path} missing)")
        return c
    reg, rep = read_exact(reg_path), read_exact(rep_path)
    if first_paths is None:
        c = compare_frames(reg, rep, name, ignore=RUN_SPECIFIC)
        c.byte_identical = _sha256(reg_path) == _sha256(rep_path)
        return c
    if is_paths_file:
        reg = reg[reg["path"].astype(int) < int(first_paths)]
        return compare_frames(reg, rep, name, ignore={**RUN_SPECIFIC, **ON_BASE},
                              scope=f"each campaign's first {first_paths} paths; not compared: {', '.join(ON_BASE)}")
    reg = reg[~reg["section"].astype(str).isin(sections_out)]
    rep = rep[~rep["section"].astype(str).isin(sections_out)]
    return compare_frames(reg, rep, name, ignore=RUN_SPECIFIC, partial=True,
                          scope=f"path-free rows only; not compared: the sections {', '.join(sections_out)}")


# ------------------------------------------------------------------------------------------------------------- main

def default_out(pid: str) -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / ".cache")
    return Path(base) / "stage2-repro" / pid


def check_registered(reg: Registered) -> None:
    """The registration is complete and each registered file is the one its manifest describes, of this registration
    and this script."""
    from propedge.backtest.harness import PreregRegistry
    from propedge.reporting.results import read_manifest, verify_result

    entry = PreregRegistry.load().get(reg.pid)
    if entry is None or entry.status != "complete":
        raise Refused(f"{reg.pid} is {'not registered' if entry is None else repr(entry.status)}: only a completed "
                      "registration is reproduced (a runnable one runs through its own script)")
    for f in reg.files:
        path = _rd() / f
        ok, msg = verify_result(path)
        if not ok:
            raise Refused(msg)
        m = read_manifest(path)
        if m.prereg_id != reg.pid or m.script != reg.script:
            raise Refused(f"{f}'s manifest names {m.prereg_id!r} and {m.script!r}, not {reg.pid!r} and {reg.script!r}")


def _guarded(reg: Registered) -> dict[str, Any]:
    """The registered files with their manifests, hashed, and the variant ledger's length: a reproduction changes none
    of the files and appends nothing for its registration (`_changed`)."""
    out: dict[str, Any] = {f: (_sha256(_rd() / f) if (_rd() / f).is_file() else None)
                           for f in [*reg.files, *(f + ".manifest.json" for f in reg.files)]}
    ledger = _rd() / "variants.jsonl"
    out["variants.jsonl"] = ledger.stat().st_size if ledger.is_file() else 0
    return out


def _changed(reg: Registered, before: dict[str, Any]) -> list[str]:
    """What the run changed: a registered file or manifest, or a variant-ledger line for this registration (another
    session's appends meanwhile are not this run's)."""
    now = _guarded(reg)
    out = [f for f in before if f != "variants.jsonl" and before[f] != now[f]]
    ledger, size = _rd() / "variants.jsonl", int(before["variants.jsonl"])
    if now["variants.jsonl"] < size:
        out.append("variants.jsonl (shorter than before the run)")
    elif now["variants.jsonl"] > size:
        with open(ledger, "rb") as fh:
            fh.seek(size)
            new = [ln for ln in fh.read().decode("utf-8", errors="replace").splitlines() if ln.strip()]
        mine = [ln for ln in new if f'"prereg_id": "{reg.pid}"' in ln]
        if mine:
            out.append(f"variants.jsonl ({len(mine)} line(s) appended for {reg.pid})")
    return out


def compare(reg: Registered, out: Path, paths: int | None) -> list[Comparison]:
    """Every file of `reg`, registered against reproduced; `paths` below the registered count compares the smoke's
    part."""
    partial = paths is not None and paths < reg.registered_paths()
    first = int(paths) if partial else None
    rows = [compare_files(_rd() / reg.result, out / reg.result, sections_out=reg.campaign_sections, first_paths=first)]
    if reg.paths_file:
        rows.append(compare_files(_rd() / reg.paths_file, out / reg.paths_file, first_paths=first, is_paths_file=True))
    return rows


def _git_head() -> str:
    from propedge.reporting.results import git_commit

    return git_commit()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--prereg", required=True, choices=sorted(REGISTERED))
    ap.add_argument("--paths", type=int, default=None,
                    help="each campaign's first N paths (a smoke); default the registered count (the acceptance)")
    ap.add_argument("--out", type=Path, default=None, help="output directory, outside the repository")
    ap.add_argument("--compare-only", action="store_true", help="compare the files already in --out")
    a = ap.parse_args(argv)
    from propedge.reporting.reproduction import ReproductionDirError, check_out_dir

    reg = REGISTERED[a.prereg]
    if a.paths is not None and a.paths < 1:
        print("REFUSED: --paths is at least 1.")
        return 2
    try:
        out = check_out_dir(a.out if a.out is not None else default_out(reg.pid))
        check_registered(reg)
    except (Refused, ReproductionDirError) as exc:
        print(f"REFUSED: {exc}")
        return 2
    log_path = out / LOG
    paths = a.paths
    log: dict[str, Any] = {}
    if a.compare_only:
        if not log_path.is_file():
            print(f"REFUSED: {log_path} does not exist; run the reproduction first.")
            return 2
        log = json.loads(log_path.read_text(encoding="utf-8"))
        if log.get("prereg") != reg.pid:
            print(f"REFUSED: {log_path} records {log.get('prereg')!r}, not {reg.pid}.")
            return 2
        paths = log.get("paths") if a.paths is None else a.paths
    else:
        n_reg = reg.registered_paths()
        if paths is not None and paths >= n_reg:
            paths = None                                       # at or above the registered count: the registered run
        out.mkdir(parents=True, exist_ok=True)
        for f in (*reg.files, LOG):                            # nothing left from an earlier reproduction is compared
            for p in (out / f, out / (f + ".manifest.json")):
                if p.is_file():
                    p.unlink()
        mode = f"a smoke at each campaign's first {paths} paths" if paths is not None else \
            f"the full reproduction, the registered paths (up to {n_reg})"
        print(f"{reg.pid}: {reg.script}, {mode}, into {out} -- {reg.notes}")
        before = _guarded(reg)
        log = {"prereg": reg.pid, "script": reg.script, "paths": paths, "registered_paths": n_reg,
               "git_commit": _git_head(), "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "note": f"reproduction of {reg.pid}, not a verdict (R11)",
               "blas_threads": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS",
                                                                "MKL_NUM_THREADS")}}
        t0 = time.perf_counter()
        try:
            status = reg.run(out, paths)
        except Refused as exc:
            print(f"REFUSED: {exc}")
            return 2
        log["seconds"] = round(time.perf_counter() - t0, 1)
        log["run_status"] = status
        changed = _changed(reg, before)
        if changed:
            print(f"ERROR: the registered files or the variant ledger changed during the reproduction: {changed}")
            log["changed_in_results"] = changed
            log_path.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
            return 3
        if status != 0:
            print(f"ERROR: the registered code path returned {status}; nothing to compare.")
            log_path.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
            return 3
        print(f"ran in {log['seconds']:.0f} s")
    rows = compare(reg, out, paths)
    for c in rows:
        print(c.line())
    ok = all(c.identical for c in rows)
    if paths is not None:
        print(f"SMOKE at {paths} paths -- not R11's acceptance: the gate rows need the registered paths.")
    log["comparison"] = {c.name: {"identical": c.identical, "line": c.line()} for c in rows}
    log["compared"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    log_path.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
