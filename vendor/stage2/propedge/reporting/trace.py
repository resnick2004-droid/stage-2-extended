"""The trace check: every headline number recomputes from a result file and appears in the docs.

Modelled on `vendor/propsim/deliverables/` practice, where both deliverables took every number
from one file read from the result CSVs. The rule this enforces is the working-discipline line
"never type a result number into a document; compute it from a result file with a manifest".

A `TracedNumber` binds three things that are normally only related by hope:

    label      what the number is called in the report
    recompute  a function that derives it from a result CSV, read through
               `propedge.reporting.results.read_result` so the manifest is verified first
    documents  the files that must contain it

`run_trace_check` recomputes each one and looks for it in the named documents, tolerating the
formatting a human would actually use (thousands separators, a currency symbol, a percentage,
rounding to the number of decimals shown). A number that does not appear, or appears with a
different value, is reported -- that is the case where a document has drifted from the results
it claims to be built on.

Register the stage's headline numbers in `default_checks()` as they come into existence. An empty
set is not a pass: `/trace` says so rather than passing vacuously. Stage two's exit (B) report and
deck register theirs there (T9, D-138).

**Verdict files** (`results/*_verdict.csv`) are cited only when citable (D-185, D-195; `verdict_problems`):
its chart review recorded and passed after it, where the file is marked `verification: pending`, and the
layers L3 and L5 passed against the engine files its manifest pins. A registered number taken from a verdict
that is not citable fails, and so does any checked document that names one.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from propedge import REPO_ROOT, RESULTS_DIR
from propedge.reporting.results import read_manifest, read_result, verify_result

VERDICT_SUFFIX = "_verdict.csv"
#: D-195: the test layers a verdict needs, run against its engine files and passed
LAYER_FILES = ("l3_lookahead_canary.csv", "l5_planted_effect.csv")


def _when(timestamp: str):
    from datetime import datetime

    return datetime.fromisoformat(str(timestamp))


def verdict_problems(verdict_csv: Path | str, results_dir: Path | str | None = None) -> list[str]:
    """Why a verdict file cannot be cited yet; empty when it can.

    * D-185: a verdict marked `verification: pending` is citable only once its chart review is recorded and passed
      after it -- `<name>_verification.csv` beside `<name>_verdict.csv` (the scorer's `--record-review`), every row
      passed, its manifest dated after the verdict's.
    * D-195: L3 and L5 (`LAYER_FILES`) passed against the engine files the verdict's manifest pins -- their manifests
      carry the same engine pin, which is what "newer than its engine pin" comes to: run after the engine last
      changed. A verdict whose manifest carries no engine pin cannot be matched to its layers and is not citable.
    """
    import pandas as pd

    path = Path(verdict_csv)
    base = Path(results_dir) if results_dir is not None else path.parent
    problems: list[str] = []
    ok, msg = verify_result(path)
    if not ok:
        return [f"source file problem: {msg}"]
    manifest = read_manifest(path)
    df = pd.read_csv(path)
    if "verification" in df and df["verification"].astype(str).str.startswith("pending").any():
        review = base / path.name.replace(VERDICT_SUFFIX, "_verification.csv")
        if not review.is_file() or not verify_result(review)[0]:
            problems.append(f"verification pending (D-185): no recorded chart review ({review.name})")
        else:
            rv = pd.read_csv(review)
            if not ("passed" in rv and len(rv) and rv["passed"].astype(bool).all()):
                problems.append(f"verification pending (D-185): the recorded chart review ({review.name}) did not "
                                "pass")
            elif _when(read_manifest(review).timestamp) < _when(manifest.timestamp):
                problems.append(f"verification pending (D-185): the recorded chart review ({review.name}) is older "
                                "than the verdict")
    pin = (manifest.provenance or {}).get("engine")
    if not pin:
        problems.append("no engine pin in its manifest (D-180), so its test layers cannot be matched (D-195)")
        return problems
    for name in LAYER_FILES:
        layer = base / name
        if not layer.is_file() or not verify_result(layer)[0]:
            problems.append(f"{name} missing or unverifiable (D-195)")
            continue
        lm = read_manifest(layer)
        if ((lm.provenance or {}).get("engine") or {}).get("sha256") != pin.get("sha256"):
            problems.append(f"{name} was not run against this verdict's engine files (D-195): rerun it")
        elif not lm.parameters.get("passed"):
            problems.append(f"{name} did not pass (D-195)")
    return problems


def verdict_status(results_dir: Path | str | None = None) -> dict[str, list[str]]:
    """{verdict file name: its problems} for every verdict file in `results_dir`."""
    base = Path(results_dir) if results_dir is not None else RESULTS_DIR
    return {p.name: verdict_problems(p, base) for p in sorted(base.glob(f"*{VERDICT_SUFFIX}"))}


@dataclass(frozen=True)
class TracedNumber:
    """One headline number: where it comes from, and where it must appear.

    Attributes:
        label: how the report refers to it.
        source_csv: the result file it is derived from, relative to `results/`.
        recompute: `(DataFrame) -> float`. Must derive the number from the file, not restate
            it -- a lambda returning a literal defeats the check.
        documents: paths (relative to the repo root) that must contain the number.
        decimals: how many decimal places the documents show it to.
        as_percent: the documents show it as a percentage (0.3265 -> "32.65").
        tolerance: absolute tolerance when comparing a found number to the recomputed one.
    """

    label: str
    source_csv: str
    recompute: Callable[[Any], float]
    documents: tuple[str, ...]
    decimals: int = 2
    as_percent: bool = False
    tolerance: float = 5e-3


@dataclass
class TraceFinding:
    label: str
    ok: bool
    value: float | None
    message: str
    document: str | None = None


@dataclass
class TraceReport:
    findings: list[TraceFinding] = field(default_factory=list)
    checked: int = 0
    verdicts: dict[str, list[str]] = field(default_factory=dict)      # every verdict file and why it is not citable

    @property
    def failures(self) -> list[TraceFinding]:
        return [f for f in self.findings if not f.ok]

    @property
    def passed(self) -> bool:
        """True only if something was actually checked and every check passed.

        A report with nothing registered is **not** a pass. Returning True for an empty check
        set would give a caller -- `/trace`, `/close-check`, CI -- a green light that means
        "no numbers were verified", which is the most dangerous possible reading of a green
        light. `checked_nothing` distinguishes the two states for anyone who needs to.
        """
        return self.checked > 0 and not self.failures

    @property
    def checked_nothing(self) -> bool:
        """No numbers are registered, so the check is vacuous rather than failing."""
        return self.checked == 0

    def _verdict_lines(self) -> list[str]:
        out = []
        for name, problems in self.verdicts.items():
            out.append(f"  verdict {name}: " + ("citable" if not problems else "NOT CITABLE -- " + "; ".join(problems)))
        return out

    def summary(self) -> str:
        if self.checked == 0:
            return "\n".join([
                "trace check: NO NUMBERS REGISTERED.\n"
                "This is not a pass. Register each headline number in "
                "propedge/reporting/trace.py `default_checks()` as it is produced, so the "
                "check has something to verify. Until a result exists there is nothing to "
                "trace.", *self._verdict_lines()])
        lines = [f"trace check: {self.checked - len(self.failures)}/{self.checked} OK"]
        for f in self.findings:
            mark = "ok  " if f.ok else "FAIL"
            lines.append(f"  [{mark}] {f.label}: {f.message}")
        return "\n".join(lines + self._verdict_lines())


def _format_variants(value: float, decimals: int, as_percent: bool) -> list[str]:
    """Plausible renderings of a number in a document."""
    v = value * 100 if as_percent else value
    out = set()
    for d in {decimals, max(decimals - 1, 0), decimals + 1}:
        s = f"{v:,.{d}f}"
        out.add(s)
        out.add(s.replace(",", ""))
    if abs(v - round(v)) < 1e-9:
        out.add(f"{int(round(v)):,}")
        out.add(str(int(round(v))))
    return sorted(out)


#: A number as printed: optional minus, digits with thousands separators, optional decimals; not glued to a word.
_NUMBER = re.compile(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?")


def _tokens(text: str):
    """(as printed, value, decimals shown) for every number in `text`."""
    for m in _NUMBER.finditer(text):
        s = m.group(0).rstrip(",")
        try:
            v = float(s.replace(",", ""))
        except ValueError:
            continue
        yield s, v, (len(s.split(".", 1)[1]) if "." in s else 0)


def _find_in_text(text: str, value: float, decimals: int, as_percent: bool,
                  tolerance: float) -> tuple[bool, str]:
    """Look for `value` in `text` as a whole printed number, at the precision it is printed.

    D-140: each number in the text is parsed whole and matches only if it equals the value rounded to the decimals
    it shows (at least one fewer than `decimals`). Substring matching let a wrong last digit pass ("1.136" contains
    "1.13"; "-0.0359" contains "-0.035")."""
    target = value * 100 if as_percent else value
    nums = []
    for s, v, nd in _tokens(text):
        nums.append(v)
        if nd >= max(decimals - 1, 0) and abs(v - target) <= 0.5 * 10 ** (-nd) + 1e-12:
            return True, f"found {s!r}"

    # Not found: look for a nearby number, which usually means the document is stale rather
    # than that the number is simply absent. Saying which is the useful part.
    close = [x for x in nums if abs(x - target) < max(tolerance * 50, abs(target) * 0.02)]
    if close:
        return False, (
            f"expected ~{target:,.{decimals}f} but the document has "
            f"{close[0]:,.{decimals}f} nearby -- the document looks stale"
        )
    return False, f"expected ~{target:,.{decimals}f}; not found in the document"


def run_trace_check(
    checks: Sequence[TracedNumber] | None = None,
    *,
    results_dir: Path | str | None = None,
    repo_root: Path | str | None = None,
) -> TraceReport:
    """Recompute each registered number and confirm it appears in its documents."""
    checks = list(checks if checks is not None else default_checks())
    results_dir = Path(results_dir) if results_dir is not None else RESULTS_DIR
    repo_root = Path(repo_root) if repo_root is not None else REPO_ROOT

    report = TraceReport(verdicts=verdict_status(results_dir))
    for check in checks:
        csv = results_dir / check.source_csv
        ok, msg = verify_result(csv)
        if not ok:
            report.checked += 1
            report.findings.append(
                TraceFinding(check.label, False, None, f"source file problem: {msg}")
            )
            continue
        if report.verdicts.get(Path(check.source_csv).name):                 # D-185, D-195
            report.checked += 1
            report.findings.append(TraceFinding(
                check.label, False, None,
                "its verdict file is not citable: " + "; ".join(report.verdicts[Path(check.source_csv).name])))
            continue

        try:
            df = read_result(csv)
            value = float(check.recompute(df))
        except Exception as exc:  # noqa: BLE001 -- a broken check must be reported, not raised
            report.checked += 1
            report.findings.append(
                TraceFinding(check.label, False, None, f"recompute failed: {exc}")
            )
            continue

        for doc in check.documents:
            report.checked += 1
            path = repo_root / doc
            if not path.is_file():
                report.findings.append(
                    TraceFinding(check.label, False, value, f"document not found: {doc}", doc)
                )
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            found, why = _find_in_text(
                text, value, check.decimals, check.as_percent, check.tolerance
            )
            report.findings.append(
                TraceFinding(
                    check.label, found, value,
                    f"{why} in {doc}" if found else f"{why} ({doc})",
                    doc,
                )
            )
    # D-185, D-195: a checked document may not cite a verdict that is not citable, number or no number
    blocked = {name[:-len(".csv")]: p for name, p in report.verdicts.items() if p}
    for doc in sorted({d for c in checks for d in c.documents}):
        path = repo_root / doc
        if not blocked or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for stem, problems in blocked.items():
            if stem in text:
                report.checked += 1
                report.findings.append(TraceFinding(f"cites {stem}", False, None,
                                                    "a verdict that is not citable: " + "; ".join(problems), doc))
    return report


def untraced_numbers_in(
    document: Path | str,
    known: Iterable[float],
    *,
    tolerance: float = 5e-3,
    min_magnitude: float = 10.0,
) -> list[float]:
    """Numbers in a document that match nothing in `known`.

    A blunt instrument -- it catches page numbers, dates, article ids and rule values as well
    as untraced results -- so it is a prompt for the **results-tracer** agent to look at, not
    a gate. `min_magnitude` skips small integers, which are almost always structural.
    """
    text = Path(document).read_text(encoding="utf-8", errors="replace")
    known = list(known)
    out = []
    for m in re.findall(r"-?\d[\d,]*\.?\d*", text):
        try:
            x = float(m.replace(",", ""))
        except ValueError:
            continue
        if abs(x) < min_magnitude:
            continue
        if not any(abs(x - k) <= tolerance or abs(x - k * 100) <= tolerance for k in known):
            out.append(x)
    return out


def _gate(df):
    return df[(df["table"] == "gate") & (df["scope"] == "up|whole")].iloc[0]


def _directional(df, fill, entry):
    return df[(df["statistic"] == "directional_d") & (df["fill"] == fill) & (df["entry"] == entry)]


def _o01(df, market, col):
    return df[(df["test"] == "O01_gamma_intraday_momentum") & (df["market"] == market)][col].iloc[0]


def _weighted(df, market, col):
    g = df[df["market"] == market]
    return (g[col] * g["days"]).sum() / g["days"].sum()


def _atlas_total(_df):
    main = read_result(RESULTS_DIR / "effect_atlas.csv")
    feat = read_result(RESULTS_DIR / "effect_atlas_features.csv")
    fam = feat[feat["in_family"].astype(bool)]
    return int(main["family_size"].iloc[0]) + int(fam.groupby("family")["family_size"].max().sum())


def _days(df):
    return len(df)


def _gate_cell(column: str):
    """A portfolio-engine gate row's cell (section gate, the lower bound, 0 % denial, placement off): R2's row to beat,
    read from the run's own file, independently of `propedge/reporting/scoreboard.py`."""
    def read(df):
        g = df[(df["section"] == "gate") & (df["shift"] == "lower_bound") & (df["enforcement_p"].astype(float) == 0.0)
               & (df["placement"] == "off")]
        return float(g.iloc[0][column])
    return read


REPORT = "docs/REPORT.md"
DECK = "docs/DECK.md"


def default_checks() -> list[TracedNumber]:
    """The stage's headline numbers (T9, exit (B), D-138).

    Each recomputes from its result file here, independently of `propedge/reporting/exit_report.py`, which built the
    documents; a document that drifts from its results, or a builder that misreads a file, fails the check. Small
    integers are not registered: they appear in too many other places to prove anything.
    """
    both = (REPORT, DECK)
    return [
        TracedNumber("gap reversal: gap days in the gate", "gap_gate.csv",
                     lambda df: _gate(df)["n_days"], both, decimals=0),
        TracedNumber("gap reversal: gate effect G (%)", "gap_gate.csv",
                     lambda df: _gate(df)["G"], both, decimals=4, tolerance=5e-5),
        TracedNumber("gap reversal: G's lower bound (%)", "gap_gate.csv",
                     lambda df: _gate(df)["G_lb"], both, decimals=4, tolerance=5e-5),
        TracedNumber("ES open reversion: best plain-entry upper bound, close fill", "test1_rescore.csv",
                     lambda df: _directional(df, "close", "baseline")["hi90"].max(), both, decimals=4,
                     tolerance=5e-5),
        TracedNumber("ES open reversion: best plain-entry upper bound, next-open fill", "test1_rescore.csv",
                     lambda df: _directional(df, "next_open", "baseline")["hi90"].max(), (REPORT,), decimals=4,
                     tolerance=5e-5),
        TracedNumber("NQ open reversion: best plain-entry upper bound", "openrev_nq.csv",
                     lambda df: _directional(df, "next_open", "baseline")["hi90"].max(), both, decimals=4,
                     tolerance=5e-5),
        TracedNumber("atlas: declared tests in all families", "effect_atlas.csv", _atlas_total, both, decimals=0),
        TracedNumber("atlas O01 NQ: screen slope difference", "effect_atlas_features.csv",
                     lambda df: _o01(df, "NQ", "est"), both, decimals=4, tolerance=5e-5),
        TracedNumber("atlas O01 NQ: check slope difference", "effect_atlas_features.csv",
                     lambda df: _o01(df, "NQ", "check_est"), both, decimals=4, tolerance=5e-5),
        TracedNumber("atlas O01 NQ: check one-sided p", "effect_atlas_features.csv",
                     lambda df: _o01(df, "NQ", "check_p1"), both, decimals=4, tolerance=5e-5),
        TracedNumber("atlas O01 ES: screen slope difference", "effect_atlas_features.csv",
                     lambda df: _o01(df, "ES", "est"), both, decimals=4, tolerance=5e-5),
        TracedNumber("atlas O01 ES: check slope difference", "effect_atlas_features.csv",
                     lambda df: _o01(df, "ES", "check_est"), both, decimals=4, tolerance=5e-5),
        TracedNumber("coverage: ES days recorded", "manual_R030_atlas_ES.csv", _days, (REPORT,), decimals=0),
        # scoreable days, from the spread file: independent of the builder's own day filter, and distinct per market
        TracedNumber("coverage: ZN scoreable days", "atlas_spreads.csv",
                     lambda df: df.loc[df["market"] == "ZN", "days"].sum(), (REPORT,), decimals=0),
        TracedNumber("coverage: CL scoreable days", "atlas_spreads.csv",
                     lambda df: df.loc[df["market"] == "CL", "days"].sum(), (REPORT,), decimals=0),
        TracedNumber("spreads: NQ opening-30 mean (ticks)", "atlas_spreads.csv",
                     lambda df: _weighted(df, "NQ", "sp30_mean"), (REPORT,), decimals=3, tolerance=5e-4),
        TracedNumber("spreads: GC opening-30 mean (ticks)", "atlas_spreads.csv",
                     lambda df: _weighted(df, "GC", "sp30_mean"), (REPORT,), decimals=3, tolerance=5e-4),
        TracedNumber("spreads: CL share of minutes wider than a tick", "atlas_spreads.csv",
                     lambda df: _weighted(df, "CL", "spw_mean"), (REPORT,), decimals=3, tolerance=5e-4),
        # R2: the scoreboard's rows to beat and the last confirmation, each from its own run file
        TracedNumber("scoreboard: P-06 growth on required bankroll, bound", "fv3_confirmation.csv",
                     _gate_cell("pf_growth_on_base_p50"), both, decimals=3, tolerance=5e-4),
        TracedNumber("scoreboard: P-06 required bankroll p90", "fv3_confirmation.csv",
                     _gate_cell("pf_required_p90"), both, decimals=0, tolerance=0.5),
        TracedNumber("scoreboard: FV3-C development growth, bound", "fv3_corrected_v1.csv",
                     _gate_cell("pf_growth_on_base_p50"), both, decimals=3, tolerance=5e-4),
        TracedNumber("scoreboard: P-10 growth on required bankroll, bound", "t24_confirmation.csv",
                     _gate_cell("pf_growth_on_base_p50"), both, decimals=3, tolerance=5e-4),
        TracedNumber("scoreboard: P-11 growth on required bankroll, bound", "a1_ins15_gate.csv",
                     _gate_cell("pf_growth_on_base_p50"), both, decimals=3, tolerance=5e-4),
        TracedNumber("scoreboard: P-12 growth on required bankroll, bound", "a2_nb158_gate.csv",
                     _gate_cell("pf_growth_on_base_p50"), both, decimals=3, tolerance=5e-4),
        TracedNumber("scoreboard: P-13 growth on required bankroll, bound", "a3_brk30_gate.csv",
                     _gate_cell("pf_growth_on_base_p50"), both, decimals=3, tolerance=5e-4),
        TracedNumber("scoreboard: P-14 growth on required bankroll, bound", "a3_brk30_cb20_gate.csv",
                     _gate_cell("pf_growth_on_base_p50"), both, decimals=3, tolerance=5e-4),
    ]
