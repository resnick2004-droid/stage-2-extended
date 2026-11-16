"""The report's checks (Q-27), each run in a process of its own by `tests/test_report.py` (the report imports the
vendored engine: CLAUDE.md). Every case prints one JSON line `{"problems": [...], ...}`; the test asserts it is empty.

    python tests/report_cases.py <case> <temporary folder>

Cases: `measures` (every measure against `tests/report_reference.py` on seeded synthetic files, and a hand-worked
file), `build` / `build_monthly` (a page built from a synthetic file: its parts, its labels, no untraced number, the
trace check passing on it and failing on a stale page and an edited file), `refusals`, `stage2` (the identity against
Stage 2's registered U1 readings), `no_matplotlib`, `memo` (the trace run reads a file once).
"""
from __future__ import annotations

import csv
import json
import math
import re
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import extended.report as R  # noqa: E402  (puts the vendored tree on sys.path)
import extended.results as X  # noqa: E402
import report_reference as REF  # noqa: E402
import report_synth as SY  # noqa: E402

from propedge.reporting.trace import _tokens  # noqa: E402

problems: list[str] = []
info: dict = {}


def close(a: float, b: float, rel: float = 1e-9) -> bool:
    a, b = float(a), float(b)
    if math.isnan(a) and math.isnan(b):
        return True
    return abs(a - b) <= rel * max(1.0, abs(b))


def write(df, base: Path, name: str, *, exploratory: bool = False, seed: int = SY.SEEDS[0]) -> Path:
    csv_path, _ = X.write_result(df, name, script="tests/report_synth.py", seed=seed,
                                 parameters={"generator": "tests/report_synth.py", "seed": seed},
                                 results_dir=base / "results", description="Q-27 test: synthetic start rows",
                                 exploratory=exploratory, variant_count=7)
    return csv_path


def text_rows(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def synth_spec(name: str, source: str, *, ladder: bool = True, designs=("steady", "lumpy")) -> R.ReportSpec:
    return R.ReportSpec(
        name=name, title=f"Synthetic test page {name}", source=source, where={"section": "start"},
        designs=tuple(R.Design(d, d.title(), f"the toy design {d!r}", {"config": d, "arm": "verdict"})
                      for d in designs),
        base={"denial": 0} if ladder else {}, ladder="denial", out=f"docs/report/{name}")


# ------------------------------------------------------------------------------------------------ measures

def hand_worked(base: Path) -> None:
    """Three start days worked by hand (see the numbers in the comments)."""
    rows = [
        # X: fee 100 at day 0, a fee of 250 at day 50; passes day 3; payouts 300 at 10, 100 and 50 at 60, 400 at 130
        SY.explicit_row(observed=252, fees={0: 100.0, 50: 250.0}, payouts=[(10, 300.0), (60, 100.0), (60, 50.0),
                                                                       (130, 400.0)], pass_day=3),
        # Y: fee 100 at day 0, never passes, never paid
        SY.explicit_row(observed=252, fees={0: 100.0}, payouts=[], pass_day=None),
        # Z: a late start, 30 sessions left, fee 100, never paid
        SY.explicit_row(observed=30, fees={0: 100.0}, payouts=[], pass_day=None),
    ]
    for i, r in enumerate(rows):
        r.update(config="hand", arm="verdict", start_day=float(i), start_date=f"2021-01-0{4 + i}")
    import pandas as pd

    path = write(pd.DataFrame(rows), base, "hand_worked")
    spec = R.ReportSpec(name="hand", title="hand", source=str(path), where={"section": "start"},
                        designs=(R.Design("hand", "Hand", "worked by hand", {"config": "hand"}),), ladder=None)
    df = X.read_result(path)
    st = R.starts_for(spec, df, "hand")
    import statistics

    sd = sorted([statistics.stdev([200, 0, -100, 0, 0, 0, 400, 0, 0, 0, 0, 0]), statistics.stdev([-100] + [0] * 11)])
    want = {
        "rows": 3,
        "dist:breakeven_days:n": 2, "dist:breakeven_days:p50": float("nan"),       # 10 and beyond: the median beyond
        "share:breakeven:1": 1 / 3, "share_n:breakeven:1": 3,
        "share:fell_back": 1.0, "share_n:fell_back": 1,
        "dist:breakeven_fall:p50": 250.0,                                           # 200 down to -50
        "dist:gain_months:p50": (2 / 12 + 0) / 2,                                   # X 2 of 12, Y none
        "dist:dry_months:p50": (5 + 12) / 2,                                        # X months 8-12, Y all 12
        "dist:monthly_spread:p10": sd[0] + 0.1 * (sd[1] - sd[0]),
        "dist:payouts_per_month:p50": (4 / 12) / 2,
        "dist:largest_month:p50": 400 / 850, "dist:largest_month:n": 1,             # Y has no payout: not read
        "dist:payout_gap:p50": 60.0, "dist:payout_gap:n": 2, "dist:payout_gap:starts": 2,   # 10 -> 60 -> 130
        "dist:month_payout:p50": 300.0, "dist:month_payout:n": 3,                   # 300, 150, 400
        "dist:payout_size:p50": 200.0, "dist:payout_size:n": 4,                     # 300, 100, 50, 400
        "dist:first_payout_size:p50": 300.0, "dist:first_payout_size:n": 1,
        "dist:payout_days:p50": float("nan"), "dist:payout_days:n": 2,              # 10 and never: beyond
        "dist:pass_cash:p50": 100.0, "dist:payout_cash:p50": 100.0,
        "share:paid:1": 1 / 3, "share:ahead:1": 1 / 3, "share_n:ahead:1": 3, "share_n:ahead:2": 2,
        "dist:net_12:p50": (500 - 100) / 2, "dist:net_3:p90": -100 + 0.9 * (100 - -100),
        "dist:gain_months:stretch": 2 / 252,
    }
    for k, v in want.items():
        got = R.quantity(st, k)
        if not close(got, v):
            problems.append(f"hand-worked {k}: got {got!r}, want {v!r}")
    if R.quantity(st, "dist:breakeven_days:p10") == R.quantity(st, "dist:breakeven_days:p10"):   # not NaN
        problems.append("hand-worked: a percentile beyond the window is not blank")
    if R.blank_reason(st, "dist:breakeven_days:p50") != "beyond":
        problems.append(f"hand-worked: the median break-even reads {R.blank_reason(st, 'dist:breakeven_days:p50')!r}")


def case_measures(base: Path) -> None:
    hand_worked(base)
    compared = 0
    for seed in SY.SEEDS:
        df0 = SY.frame(seed, designs=("steady", "lumpy", "poor"))
        path = write(df0, base, f"synth_{seed}", seed=seed)
        spec = synth_spec(f"s{seed}", str(path), designs=("steady", "lumpy", "poor"))
        df = X.read_result(path)                      # as the trace check reads it
        raw = text_rows(path)                         # as the reference reads it: text, no pandas
        for d in spec.designs:
            for level in (None, 0.25):
                st = R.starts_for(spec, df, d.key, level)
                lv = 0.0 if level is None else level
                mine = [REF.Row(r) for r in raw if r["config"] == d.key and float(r["denial"]) == lv]
                for k in REF.keys():
                    a, b = R.quantity(st, k), REF.quantity(mine, k)
                    compared += 1
                    if not close(a, b):
                        problems.append(f"seed {seed} {d.key} level {level} {k}: report {a!r}, reference {b!r}")
    info["compared"] = compared
    # the judged block (start days from 2024-01-01): the same measures on its rows alone
    from datetime import date

    path = write(SY.frame(SY.SEEDS[0], designs=("steady",), ladder=None, first_date=date(2023, 6, 1)), base,
                 "synth_judged")
    spec = synth_spec("j", str(path), ladder=False, designs=("steady",))
    st = R.starts_for(spec, X.read_result(path), "steady", None, "judged")
    raw = [REF.Row(r) for r in text_rows(path) if r["start_date"] >= R.JUDGED_FROM]
    if not 0 < len(raw) < 260 or int(R.quantity(st, "rows")) != len(raw):
        problems.append(f"judged block: {R.quantity(st, 'rows')} start days, {len(raw)} from {R.JUDGED_FROM} on")
    for k in REF.keys():
        a, b = R.quantity(st, k), REF.quantity(raw, k)
        compared += 1
        if not close(a, b):
            problems.append(f"judged block {k}: report {a!r}, reference {b!r}")
    info["compared"] = compared
    # the same measures with the optional columns absent: those that need them say so; the rest are unchanged
    df0 = SY.frame(SY.SEEDS[0], daily=False, cash=False, ladder=None)
    path = write(df0, base, "synth_monthly")
    spec = synth_spec("m", str(path), ladder=False)
    st = R.starts_for(spec, X.read_result(path), "steady")
    raw = [REF.Row(r) for r in text_rows(path) if r["config"] == "steady"]
    for k in REF.keys(daily=False, cash=False):
        if not close(R.quantity(st, k), REF.quantity(raw, k)):
            problems.append(f"month-end file {k}: differs from the reference")
    for k in ("dist:breakeven_days:p50", "share:fell_back", "dist:payout_size:p50", "share:breakeven:3"):
        try:
            R.quantity(st, k)
            problems.append(f"month-end file {k}: read without the column it needs")
        except R.NotInFile:
            pass


# ------------------------------------------------------------------------------------------------ build

STRUCTURAL_PATTERNS = (
    r"\b\d{4}-\d{2}-\d{2}(?:T[\d:+]+)?\b",          # dates and timestamps
    r"`[0-9a-f]{7,64}(?:-dirty)?`",                  # hashes and commits, in backticks
    r"\b(?:[A-Z]{1,3}\*?-\d+[a-z]?)\b",              # row and design ids: E-014, D-620, P-14, Q-17, F-01
    r"Stage 2\b",
    r"\bsha256\b",
)
#: numbers the page prints as structure, not results: windows and month ends, percentile names, the ladder's levels,
#: the bound's level, the manifest's variant count (provenance, not a result)
STRUCTURAL = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 21, 25, 30, 42, 50, 63, 75, 90, 95, 100, 126, 189, 252}


def sweep(text: str, claims) -> list[str]:
    printed = {c.printed for c in claims}
    clean = text
    for pat in STRUCTURAL_PATTERNS:
        clean = re.sub(pat, " ", clean)
    out = []
    for s, v, _ in _tokens(clean):
        if s in printed or v in STRUCTURAL:
            continue
        out.append(s)
    return out


def check_page(base: Path, spec: R.ReportSpec, *, daily: bool, exploratory: bool, ladder: bool) -> None:
    import extended.trace as T              # imported where used: its import lists the registered pages' numbers

    built = R.build(spec, root=base)
    page = built.page
    text = page.read_text(encoding="utf-8")
    info[f"{spec.name}_claims"] = len(built.claims)
    info[f"{spec.name}_charts"] = [p.name for p in built.charts]
    # every image exists, is a PNG, and has its source named under it
    lines = text.splitlines()
    images = [(i, m.group(1)) for i, ln in enumerate(lines) for m in [re.search(r"!\[[^\]]+\]\(([^)]+\.png)\)", ln)]
              if m]
    if len(images) < 2 + 2 * len(spec.designs):
        problems.append(f"{spec.name}: {len(images)} charts on the page")
    for i, name in images:
        p = page.parent / name
        if not p.is_file() or p.read_bytes()[:4] != b"\x89PNG":
            problems.append(f"{spec.name}: chart {name} missing or not a PNG")
        after = "\n".join(lines[i + 1:i + 3])
        if "*Source:" not in after or spec.source.replace("\\", "/").split("/")[-1] not in after:
            problems.append(f"{spec.name}: chart {name} has no source named under it")
    for words in ("stops when their own money runs out", "the user's time", "taxes"):
        if words not in text:
            problems.append(f"{spec.name}: 'not modelled' lacks {words!r}")
    if ("EXPLORATORY" in text) != exploratory:
        problems.append(f"{spec.name}: the exploratory label is {'missing' if exploratory else 'there'}")
    if ladder:
        for lv in ("0%", "10%", "25%", "50%"):
            if f"| {lv} |" not in text:
                problems.append(f"{spec.name}: the denial ladder lacks the {lv} row")
    elif "payout-denial ladder: not in this file" not in text:
        problems.append(f"{spec.name}: the missing ladder is not said")
    be_rows = [ln for ln in lines if ln.startswith("| Sessions until net cash is back to zero")]
    if not be_rows or (("not in this file" in be_rows[0]) == daily):
        problems.append(f"{spec.name}: the break-even row reads {be_rows[:1]!r} (daily: {daily})")
    left = sweep(text, built.claims)
    if left:
        problems.append(f"{spec.name}: untraced numbers on the page: {left[:12]}")
    # the trace check on the page: every claim found; then a stale page and an edited file fail
    checks = R.traced_numbers(spec, root=base)
    if len(checks) != len(built.claims) or len(checks) < 40:
        problems.append(f"{spec.name}: {len(checks)} traced numbers for {len(built.claims)} claims")
    rep = T.run(checks, results_dir=base / "results", repo_root=base)
    info[f"{spec.name}_trace"] = rep.summary().splitlines()[0]
    if not rep.passed or rep.checked != len(checks):
        problems.append(f"{spec.name}: the trace check did not pass on the built page: "
                        + "; ".join(f.message for f in rep.failures[:5]))
    if R.compose_text(spec, root=base) != R.compose_text(spec, root=base):
        problems.append(f"{spec.name}: the page is not the same twice")
    # a stale page: one money figure, printed once on the page, moved by a few dollars
    seen = [s for s, _, _ in _tokens(text)]
    target = next(c for c in built.claims if c.decimals == 0 and not c.as_percent
                  and abs(float(c.printed.replace(",", ""))) > 500 and seen.count(c.printed) == 1
                  and f"| {c.printed} |" in text)
    v = float(target.printed.replace(",", ""))
    stale = text.replace(f"| {target.printed} |", f"| {v + 7:,.0f} |", 1)
    if stale == text:
        problems.append(f"{spec.name}: could not stage a stale page for {target.label}")
    page.write_text(stale, encoding="utf-8")
    rep2 = T.run([c for c in checks if c.label == f"{spec.name}: {target.label}"], results_dir=base / "results",
                 repo_root=base)
    if rep2.passed:
        problems.append(f"{spec.name}: a stale number passed the trace check")
    page.write_text(text, encoding="utf-8")
    src = R.source_path(spec, base)
    raw = src.read_bytes()
    src.write_bytes(raw.replace(b"start", b"stArt", 1))
    rep3 = T.run(checks[:3], results_dir=base / "results", repo_root=base)
    if rep3.passed or not all("source file problem" in f.message for f in rep3.failures):
        problems.append(f"{spec.name}: an edited result file passed the trace check")
    src.write_bytes(raw)


def case_build(base: Path) -> None:
    from datetime import date

    path = write(SY.frame(SY.SEEDS[1], designs=("steady", "lumpy"), starts=150, sessions=300,
                          first_date=date(2023, 9, 1)), base, "synth_page", exploratory=True, seed=SY.SEEDS[1])
    spec = synth_spec("synth_daily", "results/" + path.name)
    check_page(base, spec, daily=True, exploratory=True, ladder=True)
    text = (base / spec.out / "README.md").read_text(encoding="utf-8")
    for d in spec.designs:
        part = text.split(f"## {d.short}: ")[1].split("\n## ")[0]
        judged = part.split("### The same on the judged block")[1].split("### ")[0] if "judged block" in part else ""
        if "| Sessions until the first payout arrives |" not in judged:
            problems.append(f"{d.key}: the judged block's journey table is missing")
        if "| Judged block | Start days read |" not in part:
            problems.append(f"{d.key}: the scorecard has no judged-block column")
    built = R.traced_numbers(spec, root=base)
    if not any(" judged block | " in c.label for c in built):
        problems.append("no judged-block number is traced")


def case_build_monthly(base: Path) -> None:
    path = write(SY.frame(SY.SEEDS[2], designs=("steady", "lumpy", "poor"), daily=False, cash=False, ladder=None,
                          starts=150, sessions=300), base, "synth_monthly_page", seed=SY.SEEDS[2])
    spec = synth_spec("synth_monthly", "results/" + path.name, ladder=False, designs=("steady", "lumpy", "poor"))
    check_page(base, spec, daily=False, exploratory=False, ladder=False)
    text = (base / spec.out / "README.md").read_text(encoding="utf-8")
    if text.count("none in this file") != 3:
        problems.append("monthly page: the empty judged block is not said for each design")
    for words in ("Size of each payout", "Back to break-even at least once"):
        row = [ln for ln in text.splitlines() if words in ln and ln.startswith("|")]
        if not row or "not in this file" not in row[0]:
            problems.append(f"monthly page: the row {words!r} does not say 'not in this file': {row[:1]}")


# ------------------------------------------------------------------------------------------------ refusals

def case_refusals(base: Path) -> None:
    import pandas as pd

    df0 = SY.frame(SY.SEEDS[0], designs=("steady",), starts=40, ladder=(0.0, 0.5))
    path = write(df0, base, "refuse_base")
    good = synth_spec("r", str(path), designs=("steady",))
    df = X.read_result(path)

    def refused(what: str, fn) -> None:
        try:
            fn()
        except R.ReportError as exc:
            info.setdefault("refusals", {})[what] = str(exc)[:160]
            return
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{what}: raised {type(exc).__name__} ({exc}), not a ReportError")
            return
        problems.append(f"{what}: not refused")

    refused("a design with no rows", lambda: R.starts_for(
        R.ReportSpec("r", "r", str(path), (R.Design("nobody", "N", "n", {"config": "nobody"}),),
                     where={"section": "start"}, base={"denial": 0}), df, "nobody"))
    refused("the ladder's levels mixed (no base)", lambda: R.starts_for(
        R.ReportSpec("r", "r", str(path), good.designs, where={"section": "start"}), df, "steady"))
    refused("a filter on a column the file lacks", lambda: R.starts_for(
        R.ReportSpec("r", "r", str(path), good.designs, where={"secton": "start"}, base={"denial": 0}), df, "steady"))
    bad = df.copy()
    i = bad.index[(bad["config"] == "steady") & (bad["denial"] == 0)][0]
    p = bad.at[i, "net_by_session"].split()
    p[21] = repr(float(p[21]) + 5.0)
    bad.at[i, "net_by_session"] = " ".join(p)
    refused("a daily path that disagrees with the month-end net", lambda: R.starts_for(good, bad, "steady"))
    bad = df.copy()
    j = bad.index[(bad["config"] == "steady") & (bad["denial"] == 0) & (bad["pay_cash"].astype(str).str.len() > 0)
                  & (bad["observed"] >= 63)][0]
    c = bad.at[j, "pay_cash"].split()
    c[0] = repr(float(c[0]) + 1.0)
    bad.at[j, "pay_cash"] = " ".join(c)
    refused("payouts that disagree with the month-end nets and fees", lambda: R.starts_for(good, bad, "steady"))
    refused("a missing required column", lambda: R.starts_for(good, df.drop(columns=["fees_month_3"]), "steady"))
    raw = path.read_bytes()
    path.write_bytes(raw.replace(b"steady", b"steadY", 1))
    try:
        R.build(good, root=base, out=base / "refused_page")
        problems.append("an edited result file was built into a page")
    except ValueError:
        pass
    if (base / "refused_page" / "README.md").exists():
        problems.append("a page was written from an edited result file")
    path.write_bytes(raw)
    # a file whose manifest records an uncommitted tree is built, but labelled not citable
    m = X.manifest_path_for(path)
    man = json.loads(m.read_text(encoding="utf-8"))
    man["git_commit"] = "0123abc-dirty"
    man["git_dirty"] = True
    m.write_text(json.dumps(man), encoding="utf-8")
    text = R.compose_text(good, root=base)
    if "NOT CITABLE" not in text:
        problems.append("a reading from an uncommitted tree is not labelled NOT CITABLE")
    _ = pd


# ------------------------------------------------------------------------------------------------ Stage 2

#: (my key, U1's key in vendor/stage2/results/user_journey.csv, U1's n key or None, a transform of mine)
def _identity_pairs() -> list[tuple[str, str, str | None, str]]:
    out = []
    for m in (1, 2, 3, 6, 9, 12):
        d = 21 * m
        out.append((f"share:ahead:{m}", f"periodic:share_positive@{d}", f"share_n:ahead:{m}", "same"))
        for p in (5, 10, 25, 50, 75, 90):
            out.append((f"dist:net_{m}:p{p}", f"periodic:net_p{p}@{d}", f"dist:net_{m}:n", "same"))
    for m in (1, 2, 3, 6):
        out.append((f"share:paid:{m}", f"consistency:share_no_payout_by@{21 * m}", f"share_n:paid:{m}", "one_minus"))
        out.append((f"share:paid:{m}", f"first_payout:share_by@{21 * m}", f"share_n:paid:{m}", "same"))
    for p in (50, 90):
        out.append((f"dist:pass_days:p{p}", f"first_pass:days_p{p}@42", "dist:pass_days:n", "same"))
    for p in (50, 90, 95):
        out.append((f"dist:pass_cash:p{p}", f"first_pass:spent_before_p{p}@42", "dist:pass_days:n", "same"))
        out.append((f"dist:payout_days:p{p}", f"first_payout:days_p{p}@126", "dist:payout_days:n", "same"))
        out.append((f"dist:payout_cash:p{p}", f"first_payout:spent_before_p{p}@126", "dist:payout_days:n", "same"))
    for p in (10, 50, 90):
        out.append((f"dist:first_payout_size:p{p}", f"first_payout:cash_p{p}@126", "dist:payout_days:n", "same"))
    for k, u1 in (("score:S1", "first_payout:spent_before_p90@126"), ("score:S3a", "first_payout:share_by@21"),
                  ("score:S3b", "first_payout:days_p90@126"),
                  ("score:S3c", "money_back:payouts_per_fee_dollar_pooled@63"),
                  ("score:S4a", "periodic:share_positive@126"), ("score:S4b", "periodic:share_positive@252"),
                  ("score:S5a", "periodic:net_p10@63"), ("score:S5b", "consistency:longest_gap_p90@126"),
                  ("score:S5c", "consistency:concentration@126")):
        out.append((k, u1, k.replace("score:", "score_n:"), "same"))
    return out


def case_stage2(_base: Path) -> None:
    import warnings

    import pandas as pd

    src = ROOT / "vendor" / "stage2" / "results" / "user_journey.csv"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", pd.errors.DtypeWarning)
        df = X.read_result(src)                     # as the trace check reads it
    reg = df[df["section"].isin(["metric", "month"])]
    designs = tuple(R.Design(f"{c}_{a}", c, c, {"config": c, "arm": a})
                    for c in ("p14", "p16") for a in ("verdict", "point"))
    spec = R.ReportSpec("s2", "s2", str(src), designs, where={"section": "start"}, ladder=None)
    pairs = _identity_pairs()
    held = compared = differ = 0
    for d in designs:
        st = R.starts_for(spec, df, d.key)
        rows = reg[(reg["config"] == d.where["config"]) & (reg["arm"] == d.where["arm"])]
        twin = "p16" if d.where["config"] == "p14" else "p14"
        other = reg[(reg["config"] == twin) & (reg["arm"] == d.where["arm"])]
        by = dict(zip(rows["key"], zip(rows["value"].astype(float), rows["n"].astype(float))))
        by_other = dict(zip(other["key"], other["value"].astype(float)))
        for mine, u1, nkey, how in pairs:
            if u1 not in by:
                problems.append(f"{d.key}: Stage 2's file has no row {u1}")
                continue
            v, n = by[u1]
            got = R.quantity(st, mine)
            if how == "one_minus":
                got = 1.0 - got
            compared += 1
            if close(got, v) and (nkey is None or int(R.quantity(st, nkey)) == int(n)):
                held += 1
            else:
                problems.append(f"{d.key} {mine} vs {u1}: report {got!r} (n {R.quantity(st, nkey) if nkey else '-'}), "
                                f"Stage 2 {v!r} (n {n})")
            if not close(got, by_other.get(u1, float("nan"))):
                differ += 1
        # P: Stage 2's own scorecard on the same starts (u_select.scorecard) -- the report must hand it every start
        if int(R.quantity(st, "rows")) != 1691 or int(R.quantity(st, "score_n:P")) != 1629:
            problems.append(f"{d.key}: {R.quantity(st, 'rows')} start rows, P on {R.quantity(st, 'score_n:P')}")
        # the judged block: the report's date cut against Stage 2's own block (u_select.scorecard(records, "late"))
        from propedge.research import u_select as S

        late = S.scorecard(st.records, "late")
        jb = R.starts_for(spec, df, d.key, None, "judged")
        for key in late:
            compared += 1
            got, n = R.quantity(jb, f"score:{key}"), R.quantity(jb, f"score_n:{key}")
            if close(got, late[key]["value"]) and int(n) == int(late[key]["n"]):
                held += 1
            else:
                problems.append(f"{d.key} judged block {key}: report {got!r} (n {n}), Stage 2's late block "
                                f"{late[key]['value']!r} (n {late[key]['n']})")
    info.update(compared=compared, held=held, differ_from_the_other_design=differ)
    # the negative control: read against the other design's registered rows, most comparisons must fail
    control = len(pairs) * len(designs)
    if differ < 0.8 * control:
        problems.append(f"negative control: only {differ} of {control} differ from the other design's rows")


# ------------------------------------------------------------------------------------------------ the rest

def case_no_matplotlib(base: Path) -> None:
    import extended.trace as T

    path = write(SY.frame(SY.SEEDS[0], designs=("steady",), starts=60, ladder=None), base, "synth_nompl")
    spec = synth_spec("nompl", "results/" + path.name, ladder=False, designs=("steady",))
    R._have_matplotlib = lambda: False
    built = R.build(spec, root=base)
    text = built.page.read_text(encoding="utf-8")
    if ".png" in text or built.charts:
        problems.append("charts drawn without matplotlib")
    if "matplotlib is not installed" not in text:
        problems.append("the page does not say why it has no charts")
    rep = T.run(R.traced_numbers(spec, root=base), results_dir=base / "results", repo_root=base)
    if not rep.passed:
        problems.append("the trace check fails on the tables-only page")


def case_memo(base: Path) -> None:
    import extended.trace as T
    import pandas as pd
    import propedge.reporting.trace as VT

    X.write_result(pd.DataFrame({"x": [1.0, 2.0, 4.0]}), "memo", script="t", seed=1, parameters={},
                   results_dir=base / "results")
    (base / "docs").mkdir(exist_ok=True)
    (base / "docs" / "m.md").write_text("mean 2.33, max 4.00, min 1.00\n", encoding="utf-8")
    checks = [T.TracedNumber("mean", "memo.csv", lambda df: df["x"].mean(), ("docs/m.md",)),
              T.TracedNumber("max", "memo.csv", lambda df: df["x"].max(), ("docs/m.md",)),
              T.TracedNumber("min", "memo.csv", lambda df: df["x"].min(), ("docs/m.md",))]
    calls = []
    original = VT.read_result

    def counting(p, *, verify=True):
        calls.append(str(p))
        return original(p, verify=verify)

    VT.read_result = counting
    rep = T.run(checks, results_dir=base / "results", repo_root=base)
    if not rep.passed or rep.checked != 3:
        problems.append(f"memo: the run did not pass ({rep.summary()})")
    if len(calls) != 1:
        problems.append(f"memo: the file was read {len(calls)} times for three numbers")
    if VT.read_result is not counting:
        problems.append("memo: the vendored module's read_result was not restored")
    VT.read_result = original
    # every registered page is traced, and nothing traced is unregistered
    if set(T.REPORT_PAGES) != set(R.REPORTS):
        problems.append(f"extended/trace.py traces {sorted(T.REPORT_PAGES)}; extended/report.py registers "
                        f"{sorted(R.REPORTS)}")
    names = {c.label.split(':')[0] for c in T.REGISTRY}
    # Q-69: a registered page waiting for its files (neither they nor the page exist) has no number to register; any
    # other page must have its numbers in the registry, and a waiting page must truly have nothing written
    if not set(R.REPORTS) - set(T.WAITING) <= names:
        problems.append(f"the registry holds no numbers of {sorted(set(R.REPORTS) - set(T.WAITING) - names)}")
    for name in T.WAITING:
        spec = R.REPORTS[name]
        if R.waiting(spec) is None or R.page_path(spec).exists() or R.source_path(spec).exists():
            problems.append(f"{name} is listed as waiting but its file or page exists")


CASES = {"measures": case_measures, "build": case_build, "build_monthly": case_build_monthly,
         "refusals": case_refusals, "stage2": case_stage2, "no_matplotlib": case_no_matplotlib, "memo": case_memo}


def main() -> int:
    case, base = sys.argv[1], Path(sys.argv[2])
    base.mkdir(parents=True, exist_ok=True)
    try:
        CASES[case](base)
    except Exception:  # noqa: BLE001 -- a crash is a problem to report, with its trace
        problems.append("crashed: " + traceback.format_exc()[-2500:])
    print(json.dumps({"problems": problems, **info}, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
