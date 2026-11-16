"""The journey scorecard page's checks (Q-69), each run in a process of its own by `tests/test_journey_page.py` (the
page imports the vendored engine: CLAUDE.md). Every case prints one JSON line `{"problems": [...], ...}`; the test
asserts it is empty.

    python tests/journey_cases.py <case> <temporary folder>

Cases:

* `page` -- a synthetic pair written through the writer's own code (`tests/journey_synth.py`, seed 20266901, the
  responses of every kind) into a temporary `results/`: the page builds; every section and every design's
  sub-section is there; the verdict view comes first and everything else is labelled beside; E-015's limits are shown
  pending with no level; every response the file holds is in each design's table; both charts are PNGs with their
  sources under them; no number on the page that is not registered (but the readings' definitions); the trace check
  passes on every number, reads each file once, and fails on a stale page and on an edited file; the page is the same
  twice; the waiting state; the refusals (another writer, a per-start file from another reading, a design not in the
  file, an unknown response, an edited file, a limit on no scorecard line); an approved limit read from a result file
  (its level traced, each design flagged inside or past it by how much, the menu read once none is pending).
* `full` -- the same page on every one of the writer's 19 responses (seed 20266902).
* `u1` -- the build-time identity: a summary whose verdict view is the writer's `scorecard_rows` on Stage 2's own U1
  start rows holds against Stage 2's file (every design, both arms, both blocks); the synthetic one does not.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import extended.report as R  # noqa: E402  (puts the vendored tree on sys.path)
import extended.results as X  # noqa: E402
import journey_synth as SY  # noqa: E402
from extended import journey_page as J  # noqa: E402

from propedge.reporting.trace import _tokens  # noqa: E402

problems: list[str] = []
info: dict = {}

#: the headings every page has, in order
HEADINGS = ("## How to read this page", "## What this page does not model, and what it assumes",
            "## Not on this page", "## The checks the file passed", "## The verdict view: the designs side by side",
            "### P and each month's share of start days ahead", "### The scorecard against R* = P-14 -- all start days",
            "### The scorecard against R* = P-14 -- judged block", "### The frontier: not beaten at once on P, S1, S3a "
            "and S5a", "### How much is the design and how much the start day", "### Limits on what a user feels "
            "(E-015): pending the operator's approval", "### Each design's P under the firm's responses (beside)",
            "### Net cash at each month end across start days", "## How the numbers on this page are kept honest")
#: each design's sub-sections, in order
DESIGN_HEADINGS = ("### P and the money, month by month",
                   "### Time and money to the first pass, the first payout and break-even",
                   "### Back to break-even, month by month", "### How even the year is",
                   "### How far ahead or behind: net cash at each month end, worst to best",
                   "### The 5 worst start days (lowest net cash at month 3)", "### Beside: the firm's responses",
                   "### Beside: the as-traded reading")
STRUCTURAL_PATTERNS = (
    r"\b\d{4}-\d{2}-\d{2}(?:T[\d:+]+)?\b",          # dates and timestamps
    r"`[^`]*`",                                      # code, file names, hashes and commits, in backticks
    r"\b(?:[A-Z]{1,3}\*?-\d+[a-z]?)\b",              # row and design ids: E-014, D-620, P-14, Q-17, F-01, S3a
    r"\bS\d[a-c]?\b",                                # the scorecard's lines
    r"Stage 2\b", r"\bsha256\b", r"\b1e-9\b", r"section \d", r"\(\d\)", r"\([a-z]\)",
    r"\(variant count in its manifest\): \d+",      # provenance, not a result
)
#: numbers a page prints as definitions, not results: months and windows, percentiles, the responses' levels and
#: thresholds, the bankroll limits, the judged block's first year, the worst-days count
STRUCTURAL = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 20, 21, 25, 42, 50, 63, 75, 90, 95, 100, 126, 252, 2000, 2500,
              2024}


def sweep(text: str, claims) -> list[str]:
    printed = {c.printed for c in claims}
    clean = text
    for pat in STRUCTURAL_PATTERNS:
        clean = re.sub(pat, " ", clean)
    return [s for s, v, _ in _tokens(clean) if s not in printed and v not in STRUCTURAL]


def spec(name: str, **kw) -> R.JourneySpec:
    base = R.REPORTS["journey_scorecard"]
    args = dict(name=name, title=f"Synthetic journey page {name}", source="results/user_beside.csv",
                starts="results/user_beside_starts.csv", designs=base.designs, writer=SY.SCRIPT, r_star="p14",
                awaits="Q-69 test", identity_u1="", out=f"docs/report/{name}")
    args.update(kw)
    return R.JourneySpec(**args)


def section(text: str, start: str, end: str = "\n## ") -> str:
    return text.split(start, 1)[1].split(end, 1)[0] if start in text else ""


def refused(what: str, fn) -> None:
    try:
        fn()
    except R.ReportError as exc:
        info.setdefault("refusals", {})[what] = str(exc)[:200]
        return
    except Exception as exc:  # noqa: BLE001
        problems.append(f"{what}: raised {type(exc).__name__} ({str(exc)[:200]}), not a ReportError")
        return
    problems.append(f"{what}: not refused")


# ------------------------------------------------------------------------------------------------ the page


def check_page(base: Path, sp: R.JourneySpec, responses: tuple[str, ...]) -> tuple[str, list]:
    import extended.trace as T

    built = R.build(sp, root=base)
    text = built.page.read_text(encoding="utf-8")
    info[f"{sp.name}_claims"] = len(built.claims)
    info[f"{sp.name}_charts"] = [p.name for p in built.charts]
    # every section, in order, and every design's
    at = [text.find(h) for h in HEADINGS]
    if any(i < 0 for i in at) or at != sorted(at):
        problems.append(f"{sp.name}: headings missing or out of order: "
                        + str([h for h, i in zip(HEADINGS, at) if i < 0]))
    for d in sp.designs:
        part = section(text, f"\n## {d.label}\n")
        if not part:
            problems.append(f"{sp.name}: no section for {d.key}")
            continue
        at = [part.find(h) for h in DESIGN_HEADINGS]
        if any(i < 0 for i in at) or at != sorted(at):
            problems.append(f"{d.key}: sub-sections missing or out of order: "
                            + str([h for h, i in zip(DESIGN_HEADINGS, at) if i < 0]))
        for words in ("**All start days.**", "**Judged block (from 2024).**"):
            if part.count(words) != 2:
                problems.append(f"{d.key}: {words!r} appears {part.count(words)} times (the journey and the spread)")
        for name, words, _, _ in J.JOURNEY:
            if f"| {words} |" not in part:
                problems.append(f"{d.key}: the journey table lacks {name}")
        resp = section(part, "### Beside: the firm's responses", "\n### ")
        for r in responses:
            lab = J.response_words(r)[0]
            if f"| {lab} |" not in resp or f"- **{lab}**:" not in resp:
                problems.append(f"{d.key}: the response {r} is not in the table and its legend")
        if "Never denied; placement off (the verdict view)" not in resp.split("\n|---|")[1].split("\n")[1]:
            problems.append(f"{d.key}: the verdict view is not the first row of the responses")
        if "minimum detectable difference in P is blank in the file -- the writer's note:" not in part:
            problems.append(f"{d.key}: the MDD's blank and its reason are not said")
    # the head: beside, exploratory, not modelled
    head = text.split("## How to read this page")[0]
    for words in ("**BESIDE, NEVER DECIDING.**", "**EXPLORATORY.**", "R* (the row to beat on P) stays P-14"):
        if words not in head:
            problems.append(f"{sp.name}: the head lacks {words!r}")
    for words in ("stops when their own money runs out", "the user's time", "taxes", "payouts never denied",
                  "placement off"):
        if words not in text:
            problems.append(f"{sp.name}: 'not modelled / assumed' lacks {words!r}")
    # the limits: pending, no level, every design flagged pending
    lim = section(text, "### Limits on what a user feels", "\n### ")
    for limit in J.limits_of(sp):
        line = [ln for ln in lim.splitlines() if ln.startswith(f"| {limit.words} |")]
        if limit.pending:
            if not line or "pending the operator's approval (E-015 (2)): no level set" not in line[0] \
                    or line[0].count("| pending |") != len(sp.designs):
                problems.append(f"{sp.name}: the limit on {limit.measure} is not shown pending: {line[:1]}")
    # the charts
    lines = text.splitlines()
    images = [(i, m.group(1)) for i, ln in enumerate(lines) for m in [re.search(r"!\[[^\]]+\]\(([^)]+\.png)\)", ln)]
              if m]
    if sorted(n for _, n in images) != ["net_months.png", "responses.png"]:
        problems.append(f"{sp.name}: charts {images}")
    for i, name in images:
        p = built.page.parent / name
        if not p.is_file() or p.read_bytes()[:4] != b"\x89PNG":
            problems.append(f"{sp.name}: chart {name} missing or not a PNG")
        after = "\n".join(lines[i + 1:i + 3])
        if "*Source:" not in after or "user_beside_starts.csv" not in after or "user_beside.csv" not in after:
            problems.append(f"{sp.name}: chart {name} has no source named under it")
    left = sweep(text, built.claims)
    if left:
        problems.append(f"{sp.name}: untraced numbers on the page: {left[:12]}")
    # the trace check: every number found, each file parsed once a run
    checks = R.traced_numbers(sp, root=base)
    if len(checks) != len(built.claims) or len(checks) < 400:
        problems.append(f"{sp.name}: {len(checks)} traced numbers for {len(built.claims)} claims")
    J._INDEX.clear()
    rep = T.run(checks, results_dir=base / "results", repo_root=base)
    info[f"{sp.name}_trace"] = rep.summary().splitlines()[0]
    if not rep.passed or rep.checked != len(checks):
        problems.append(f"{sp.name}: the trace check did not pass on the built page: "
                        + "; ".join(f.message for f in rep.failures[:5]))
    kinds = sorted(k[1] for k in J._INDEX)
    if kinds != sorted({c.kind for c in built.claims} & {"summary", "starts"}):
        problems.append(f"{sp.name}: the trace run parsed {kinds}, not each file once")
    if R.compose_text(sp, root=base) != R.compose_text(sp, root=base):
        problems.append(f"{sp.name}: the page is not the same twice")
    return text, checks


def stale_and_edited(base: Path, sp: R.JourneySpec, text: str, checks) -> None:
    import extended.trace as T

    page = R.page_path(sp, base)
    built = [c for c in J.compose(sp, J.load(sp, base), root=base).claims]
    seen = [s for s, _, _ in _tokens(text)]
    for kind in ("summary", "starts"):
        target = next(c for c in built if c.kind == kind and c.decimals == 0 and not c.as_percent
                      and abs(float(c.printed.replace(",", ""))) > 300 and seen.count(c.printed) == 1
                      and f"| {c.printed} |" in text)
        v = float(target.printed.replace(",", ""))
        page.write_text(text.replace(f"| {target.printed} |", f"| {v + 7:,.0f} |", 1), encoding="utf-8")
        rep = T.run([c for c in checks if c.label == f"{sp.name}: {target.label}"], results_dir=base / "results",
                    repo_root=base)
        if rep.passed:
            problems.append(f"{sp.name}: a stale {kind} number passed the trace check ({target.label})")
        page.write_text(text, encoding="utf-8")
    for path in (R.source_path(sp, base), J.starts_path(sp, base)):
        raw = path.read_bytes()
        path.write_bytes(raw.replace(b"p14", b"p41", 1))
        mine = [c for c in checks if Path(c.source_csv).name == path.name][:3]
        rep = T.run(mine, results_dir=base / "results", repo_root=base)
        if rep.passed or not mine or not all("source file problem" in f.message for f in rep.failures):
            problems.append(f"{sp.name}: an edited {path.name} passed the trace check")
        path.write_bytes(raw)


def waiting_checks(base: Path) -> None:
    import extended.trace as T

    empty = base / "empty"
    sp = spec("waits")
    why = R.waiting(sp, empty)
    if not why or "Q-69 test" not in why:
        problems.append(f"waiting: a page with neither file nor page is not waiting ({why!r})")
    R.REPORTS["waits"] = sp
    try:
        got = T.report_checks(["waits"], root=empty)
        if got or "waits" not in T.WAITING:
            problems.append(f"waiting: report_checks registered {len(got)} entries / did not record the wait")
        # the page built but its file gone: not waiting, and the check fails (never a silent pass)
        page = R.page_path(sp, empty)
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("a page whose file is gone\n", encoding="utf-8")
        if R.waiting(sp, empty) is not None:
            problems.append("waiting: a page that exists is still waiting")
        got = T.report_checks(["waits"], root=empty)
        rep = T.run(got, results_dir=empty / "results", repo_root=empty)
        if "waits" in T.WAITING or len(got) != 1 or rep.passed:
            problems.append("waiting: a built page without its file did not fail the trace check")
        # without `awaits` a missing file is never a wait
        if R.waiting(spec("x", awaits=""), empty) is not None:
            problems.append("waiting: a spec naming no task waits")
    finally:
        R.REPORTS.pop("waits", None)
        T.WAITING.pop("waits", None)


def refusal_checks(base: Path, sp: R.JourneySpec) -> None:
    import pandas as pd

    refused("a manifest naming another writer", lambda: J.load(spec("w", writer="scripts/user_beside.py"), base))
    refused("a design not in the file", lambda: J.load(
        spec("d", designs=(*sp.designs, R.Design("p99", "P-99", "not there", {}))), base))
    refused("R* not among the designs", lambda: J.load(spec("r", r_star="p99"), base))
    refused("a limit on no scorecard line", lambda: J.load(spec("l", limits=(J.Limit("S9", "nothing"),)), base))
    # a per-start file that is not the summary's (one design's cash before the first payout moved by $100), written
    # with a proper manifest naming the summary as its companion: only the cross-check can tell
    mixed = base / "mixed" / "results"
    mixed.mkdir(parents=True)
    for name in ("user_beside.csv", "user_beside.csv.manifest.json"):
        shutil.copy(base / "results" / name, mixed / name)
    st = X.read_result(J.starts_path(sp, base))
    st.loc[st["design"] == "p15", "spent_before_first_payout"] += 100.0
    X.write_result(st, "user_beside_starts", script=SY.SCRIPT, seed=1, parameters={}, results_dir=mixed,
                   notes={"companion_of": "user_beside.csv"})
    refused("a per-start file that is not the summary's", lambda: J.load(sp, base / "mixed"))
    # an unknown response: the summary rewritten through the writer's path with one response renamed
    df = X.read_result(base / "results" / "user_beside.csv")
    df.loc[df["response"] == "rtp_w3", "response"] = "rtp_w9"
    bad = base / "unknown" / "results"
    X.write_result(df, "user_beside", script=SY.SCRIPT, seed=1, parameters={}, results_dir=bad)
    for name in ("user_beside_starts.csv", "user_beside_starts.csv.manifest.json"):
        shutil.copy(base / "results" / name, bad / name)
    refused("an unknown response", lambda: J.load(sp, base / "unknown"))
    # an edited file is never built into a page
    src = R.source_path(sp, base)
    raw = src.read_bytes()
    src.write_bytes(raw.replace(b"scorecard", b"scoreCard", 1))
    try:
        R.build(sp, root=base, out=base / "refused_page")
        problems.append("an edited result file was built into a page")
    except ValueError:
        pass
    if (base / "refused_page" / "README.md").exists():
        problems.append("a page was written from an edited result file")
    src.write_bytes(raw)
    # a reading from an uncommitted tree is labelled not citable
    keep = {}
    for p in (src, J.starts_path(sp, base)):
        m = X.manifest_path_for(p)
        keep[m] = m.read_text(encoding="utf-8")
        man = json.loads(keep[m])
        man["git_commit"] = "0123abc-dirty"
        man["git_dirty"] = True
        m.write_text(json.dumps(man), encoding="utf-8")
    if "**NOT CITABLE.**" not in R.compose_text(sp, root=base):
        problems.append("a reading from an uncommitted tree is not labelled NOT CITABLE")
    for m, t in keep.items():
        m.write_text(t, encoding="utf-8")
    _ = pd


def approved_limits(base: Path, sp: R.JourneySpec) -> None:
    """The hook with levels: a limits file written as the lead's proposal would be (levels derived from the readings
    file, never typed), one approved, then both."""
    import pandas as pd

    import extended.trace as T

    rows = J.load(sp, base).rows
    s1 = [rows.value("scorecard", k, "verdict", "off", "all", "S1") for k in ("p14", "p15", "p16")]
    s3b = [rows.value("scorecard", k, "verdict", "off", "all", "S3b") for k in ("p14", "p15", "p16")]
    finite = [x for x in s3b if x == x]
    lv = pd.DataFrame({"measure": ["S1", "S3b"], "value": [sorted(s1)[1], max(finite) + 1.0 if finite else 1e9]})
    X.write_result(lv, "limits_proposal", script="tests/journey_cases.py", seed=None, require_seed=False,
                   parameters={"from": "user_beside.csv: the middle design's S1; the largest finite S3b plus one "
                                       "session"},
                   results_dir=base / "results")
    info["limit_s3b_blank_designs"] = len(s3b) - len(finite)
    path = "results/limits_proposal.csv"
    one = (J.Limit("S1", J.LIMITS[0].words, source=path, where=(("measure", "S1"),), approved="E-TEST"), J.LIMITS[1])
    both = (one[0], J.Limit("S3b", J.LIMITS[1].words, source=path, where=(("measure", "S3b"),), approved="E-TEST"))
    for tag, lims in (("one", one), ("both", both)):
        sl = spec(f"limits_{tag}", limits=lims)
        built = R.build(sl, root=base)
        text = built.page.read_text(encoding="utf-8")
        lim = section(text, "### Limits on what a user feels", "\n### ")
        line = [ln for ln in lim.splitlines() if ln.startswith(f"| {J.LIMITS[0].words} |")][0]
        if "(approved: E-TEST)" not in line or line.count("past it by") != 1 or line.count("| inside") != 2:
            problems.append(f"limits {tag}: the S1 line flags {line!r}")
        if tag == "one" and "limits wait for the operator's approval" not in text:
            problems.append("limits one: the menu is read with a limit pending")
        if tag == "both":
            # the menu from the file's own values: inside the S1 level (the middle design's) and a finite S3b at most
            # the level (a blank S3b is after session 126: past an "at most" limit)
            lv1, lv2 = float(lv["value"][0]), float(lv["value"][1])
            ok = [k for k, a, b in zip(("P-14", "P-15", "P-16"), s1, s3b) if a <= lv1 and b == b and b <= lv2]
            want = ("**The menu**: inside every approved limit -- " + ", ".join(ok) if ok else
                    "**The menu**: no design is inside every approved limit.")
            if want not in text:
                problems.append(f"limits both: the menu does not say {want!r}")
            line = [ln for ln in lim.splitlines() if ln.startswith(f"| {J.LIMITS[1].words} |")][0]
            if line.count("past it (the high end is after session 126)") != len(s3b) - len(finite):
                problems.append(f"limits both: a blank S3b is not shown past the limit: {line!r}")
        checks = [c for c in R.traced_numbers(sl, root=base) if "limit" in c.label]     # the page's own: case page
        kinds = {Path(c.source_csv).name for c in checks}
        if "limits_proposal.csv" not in kinds or len(checks) < 4 * len(sl.designs):
            problems.append(f"limits {tag}: the level is not traced to its file ({len(checks)} limit numbers)")
        rep = T.run(checks, results_dir=base / "results", repo_root=base)
        if not rep.passed:
            problems.append(f"limits {tag}: the trace check fails: " + "; ".join(f.message for f in rep.failures[:4]))
        if sweep(text, built.claims):
            problems.append(f"limits {tag}: untraced numbers {sweep(text, built.claims)[:8]}")


def case_page(base: Path) -> None:
    SY.write_pair(base / "results", SY.SEEDS[0], responses=SY.FAST_RESPONSES)
    sp = spec("journey_synth")
    if R.waiting(sp, base) is not None:
        problems.append("a page whose files exist is waiting")
    text, checks = check_page(base, sp, SY.FAST_RESPONSES)
    stale_and_edited(base, sp, text, checks)
    waiting_checks(base)
    refusal_checks(base, sp)
    approved_limits(base, sp)
    # the registered page is the writer's: its files, designs and writer
    W, reg = SY.writer(), R.REPORTS["journey_scorecard"]
    if (Path(reg.source).stem, Path(reg.starts).stem) != (W.RESULT, W.STARTS_RESULT) or reg.writer != W.SCRIPT:
        problems.append(f"the registered page reads {reg.source}, {reg.starts} by {reg.writer}; the writer writes "
                        f"{W.RESULT}, {W.STARTS_RESULT} as {W.SCRIPT}")
    if tuple(d.key for d in reg.designs) != tuple(W.DESIGNS) or not reg.awaits or not reg.identity_u1:
        problems.append("the registered page's designs, wait or identity are not the writer's")
    if any(not lim.pending for lim in J.LIMITS):
        problems.append("a declared limit carries a level: E-015's levels wait for the operator's approval")


def case_full(base: Path) -> None:
    from extended import user_beside as B

    SY.write_pair(base / "results", SY.SEEDS[1])
    sp = spec("journey_full")
    check_page(base, sp, tuple(r.name for r in B.RESPONSES))


def case_u1(base: Path) -> None:
    import warnings

    import pandas as pd

    from extended import user_readings as UR
    from propedge.research import u_select as S
    from propedge.research import user_journey as U

    SY.write_pair(base / "results", SY.SEEDS[0], responses=("off",))
    # absolute: the build resolves a relative `identity_u1` against its root, here the temporary folder
    sp = spec("u1", identity_u1=str(ROOT / "vendor" / "stage2" / "results" / "user_journey.csv"))
    n, bad = J.u1_identity(sp, J.load(sp, base).rows, ROOT)
    info["u1_negative"] = [n, len(bad)]
    if not bad or n != 3 * 2 * 2 * len(S.BY_KEY):
        problems.append(f"u1: the synthetic file is not refused ({len(bad)} of {n} differ)")
    try:
        R.build(sp, root=base, out=base / "u1_page")
        problems.append("u1: a page was built whose verdict view is not Stage 2's")
    except R.ReportError:
        pass
    # the positive: the verdict view made by the writer's own `scorecard_rows` from Stage 2's U1 start rows
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", pd.errors.DtypeWarning)
        df = X.read_result(ROOT / sp.identity_u1)
    start = df[df["section"] == "start"]
    out = []
    for d in ("p14", "p15", "p16"):
        for arm in U.ARMS:
            mine = start[(start["config"] == d) & (start["arm"] == arm)]
            recs = R.Starts.of(mine).records
            out += [{"design": d, "arm": arm, "response": "off", **r} for r in UR.scorecard_rows(recs)]
    rows = J.Rows(pd.DataFrame(out))
    n, bad = J.u1_identity(sp, rows, ROOT)
    info["u1_positive"] = [n, len(bad)]
    if bad or n != 3 * 2 * 2 * len(S.BY_KEY):
        problems.append(f"u1: the writer's scorecard on Stage 2's rows does not hold ({len(bad)} of {n}): {bad[:3]}")


CASES = {"page": case_page, "full": case_full, "u1": case_u1}


def main() -> int:
    case, base = sys.argv[1], Path(sys.argv[2])
    base.mkdir(parents=True, exist_ok=True)
    try:
        CASES[case](base)
    except Exception:  # noqa: BLE001 -- a crash is a problem to report, with its trace
        problems.append("crashed: " + traceback.format_exc()[-3000:])
    print(json.dumps({"problems": problems, **info}, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
