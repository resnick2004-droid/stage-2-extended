"""H4's draft declaration (`prereg/DRAFT_H4_rebaseline.md`), its T-0: checked on its own text, on its plan script, on
W42-R1's code at its commit and on the repository's files (no engine, no bar, no result file; fast).

- **the form** -- `prereg/TEMPLATE_family.md`'s sections 0 to 19 and three appendices, in order, read as LF text; a
  described reading that takes **no k** (the template's k bullet absent, CHARTER 3.7's one k per held-out test);
- **the seed table** -- section 15 lists the ten consecutive seeds of H4's block once each, three roles and seven
  spares; no other eight-digit 2026 token in the text (H3's block among them); no tracked or working text file but this
  draft (and the seed module, once it holds the block) carries a literal of the block; the arithmetic fold over every
  tracked `.py` (the three-way design test's folder) finds the block's construction only in this file, which it must
  find (the positive control); and both scans find a planted copy in a temporary repository;
- **no typed figure** -- outside the script's fenced output, the seed rows, code spans, dates, times, ids, hashes and
  section, measure and list numbers, every number of the text is one of a short list, each with its source (a typed
  figure planted in the text is caught);
- **no held-out window** -- the judged-block line names no purpose (`reader.declared_purposes`), every date after the
  search years is one of the held-out and confirmation bounds and sits in a sentence that keeps it unread, and the plan
  counts search-year sessions only;
- **the dependencies named** -- Appendix C names each with its path, its commit or its item and what H4 needs, the
  commits and files exist, the built ones hold the names H4 uses, the ones to build are marked so;
- **the measures and W42-R1's inputs** -- every measure of `docs/MEASURES.md`'s index is placed in Appendix B, and
  every key of W42-R1's `REQUIRED` and `OPTIONAL` (its `extended/wave42.py` at 2bde318) is named;
- **the plan is the script's** -- Appendix A equals `docs/plans/scripts/h4/h4_plan.py`'s output line for line; the
  script's constants equal W42-R1's at its commit, `family_stats.MDL_POWER` and `user_beside.EXACT_EVERY`; J is a
  power of two at or above the need, recomputed here; every H4-B part fits its cap at the largest assumed cost.
"""
from __future__ import annotations

import importlib.util
import math
import re
import subprocess
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "prereg" / "DRAFT_H4_rebaseline.md"
TEMPLATE = ROOT / "prereg" / "TEMPLATE_family.md"
PLAN = ROOT / "docs" / "plans" / "scripts" / "h4" / "h4_plan.py"
MEASURES = ROOT / "docs" / "MEASURES.md"
THREE_WAY_TEST = ROOT / "tests" / "test_three_way_design.py"
VENDOR_DATA = ROOT / "vendor" / "stage2" / "data"
THIS = Path(__file__).resolve().relative_to(ROOT).as_posix()

#: section 15's block, built by arithmetic so that this file holds no literal of it
_PREFIX = 2026 * 1000 + 440
H4_BLOCK = tuple(_PREFIX * 10 + i for i in range(10))
#: the files allowed to hold a literal of the block: this draft, and the seed module once it is given the block
DECLARED_USES = ("prereg/DRAFT_H4_rebaseline.md", "extended/three_way_seeds.py")
#: the files allowed to construct it by arithmetic: this test, and the seed module
DERIVED_USES = (THIS, "extended/three_way_seeds.py")
#: the commits the draft cites
W42_COMMIT, RUNNER_COMMIT = "2bde318", "adedf7f"
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".csv", ".json", ".txt", ".sha256", ".toml", ".cfg", ".ini", ".jsonl"}
SKIP_DIRS = {".git", "data", "__pycache__", ".pytest_cache", ".h4_dev"}

#: the numbers the text may hold outside the stripped forms, each a declared value or a rule cited by its source
ALLOWED_NUMBERS = {
    **{str(d): "a single digit: a list item, a count in a sentence, a tick or a worker count" for d in range(10)},
    "10": "measure (28)'s 10 % of signals missed (CHARTER 3.8 (c)); D-212's 10 % realised-risk band",
    "20": "measure (28)'s other level, 20 %, named as not read",
    "21": "a month is 21 sessions (CHARTER 2); measures (4) and (8) at session 21",
    "63": "months 1-3, P_B's horizon (MEASURES section 2)",
    "90": "D-212's 90 % of trades (CHARTER section 4)",
    "126": "W, W42-R1's window (U1's and Q-44's ledger constant)",
    "252": "twelve months, the observation window's cap (MEASURES 1.1)",
    "2020": "the search years' first calendar year (E-208)",
    "2022": "the nested cut's year (the O-7 review)",
    "2023": "the search years' last calendar year (E-208)",
    "2024": "the held-out years' first calendar year, named as unread",
    "2026": "the held-out years' last calendar year, named as unread",
}
HELD_DATES = {"2024-01-02": "the held-out years' first day", "2026-07-16": "the held-out years' last day",
              "2026-07-17": "the confirmation window's first day"}
#: dates from here on are the record's (this program's documents, from its start in 2026-11), never a market session:
#: the development bars end 2026-07-16
RECORD_DATES_FROM = "2026-11-01"
UNREAD_WORDS = ("never read", "refus", "unread", "held-out years", "confirmation window", "held-out read")


def _lf(p: Path) -> str:
    return p.read_bytes().decode("utf-8").replace("\r\n", "\n")


@pytest.fixture(scope="module")
def text() -> str:
    return _lf(DRAFT)


def _between(t: str, start: str, end: str) -> str:
    i, j = t.index(start), t.index(end)
    return t[i + len(start):j]


def _section(t: str, n: int) -> str:
    return t[t.index(f"\n## {n}. "):t.index(f"\n## {n + 1}. ") if n < 19 else t.index("\n## Appendix A. ")]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def plan():
    return _load(PLAN, "h4_plan_for_t0")


def _git(*args: str, cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=check)


def _show(commit: str, path: str) -> str:
    return _git("show", f"{commit}:{path}").stdout


@pytest.fixture(scope="module")
def w42():
    """W42-R1's module at its commit, executed from its source (pure: it imports numpy and `family_stats` only)."""
    import sys

    name = "wave42_at_2bde318_for_h4"
    mod = types.ModuleType(name)
    sys.modules[name] = mod                      # its dataclasses look their module up there
    try:
        exec(compile(_show(W42_COMMIT, "extended/wave42.py"), name, "exec"), mod.__dict__)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return mod


# ------------------------------------------------------------------------------------------------------- the form


def test_the_form(text: str) -> None:
    assert text.startswith("# H4: ") and "**Status: a draft" in text
    assert "`prereg/TEMPLATE_family.md`'s form (sections\n0 to 19)" in text
    heads = [f"\n## {n}. " for n in range(20)] + [f"\n## Appendix {a}. " for a in "ABC"]
    pos = [text.find(h) for h in heads]
    assert all(p >= 0 for p in pos), [h for h, p in zip(heads, pos) if p < 0]
    assert pos == sorted(pos)
    tmpl = _lf(TEMPLATE)
    assert all(f"\n## {n}. " in tmpl for n in range(20)), "the template's sections are 0 to 19"


def test_it_takes_no_k(text: str) -> None:
    flat = " ".join(text.split())
    assert "takes **no k**" in flat and "**H4 takes no k**" in flat
    assert "CHARTER 3.7: one k per held-out test" in flat
    tmpl = _lf(TEMPLATE)
    assert "**k:** the next free program family number" in tmpl          # the template's k bullet ...
    assert "**k:**" not in text and "k_cells" not in text                 # ... is not carried: no k, no cells counted
    assert not re.search(r"\bk\s*=\s*\d", text), "no k value is assigned"


# --------------------------------------------------------------------------------------------------- the seeds


def test_the_seed_table(text: str) -> None:
    sec = _section(text, 15)
    rows = re.findall(r"^\| (\d{8}) \| ([^|]+) \| ([^|]+) \|$", sec, re.MULTILINE)
    assert [int(r[0]) for r in rows] == list(H4_BLOCK), "ten consecutive seeds, once each, in order"
    roles = [r[1].strip() for r in rows]
    status = [r[2].strip() for r in rows]
    assert status[:3] == ["tests", "design check", "reading"]
    assert roles[3:] == ["spare"] * 7 and status[3:] == ["spare, drawn by nothing"] * 7
    assert len(set(roles[:3])) == 3, "one role each"
    toks = set(re.findall(r"\b2026\d{4}\b", text))
    assert toks <= {str(s) for s in H4_BLOCK}, f"another block's seed in the text: {sorted(toks - set(map(str, H4_BLOCK)))}"
    assert not re.search(r"\b2026587\d\b", text), "H3's block is named by role only"
    assert "never the seed plus an offset (E-171)" in " ".join(sec.split())
    assert "`three_way_seeds.PARTS` gains `H4-0` and `H4-B`" in sec


_BLOCK_RE = r"\b(" + "|".join(str(s) for s in range(_PREFIX * 10, _PREFIX * 10 + 10)) + r")\b"


def _git_hits(repo: Path) -> set[str]:
    out = _git("grep", "-IlwE", _BLOCK_RE, cwd=repo, check=False).stdout
    return {line.strip() for line in out.splitlines() if line.strip()}


def _working_hits(base: Path) -> set[str]:
    pat = re.compile(_BLOCK_RE)
    found = set()
    for p in base.rglob("*"):
        rel = p.relative_to(base)
        if not p.is_file() or p.suffix not in TEXT_SUFFIXES or SKIP_DIRS & set(rel.parts[:-1]):
            continue
        if VENDOR_DATA in p.parents:
            continue
        if pat.search(p.read_text(encoding="utf-8", errors="replace")):
            found.add(rel.as_posix())
    return found


def test_the_block_nowhere_else_tracked() -> None:
    hits = _git_hits(ROOT)
    assert hits <= set(DECLARED_USES), f"a literal of H4's block outside its declared uses: {sorted(hits)}"


def test_the_block_nowhere_else_working() -> None:
    hits = _working_hits(ROOT)
    assert "prereg/DRAFT_H4_rebaseline.md" in hits, "the scan must find the draft's own table (positive control)"
    assert hits <= set(DECLARED_USES), f"a literal of H4's block outside its declared uses: {sorted(hits)}"


def test_the_scans_find_a_planted_seed(tmp_path: Path) -> None:
    _git("init", "-q", cwd=tmp_path)
    (tmp_path / "x.md").write_text(f"a seed {H4_BLOCK[7]} here\n", encoding="utf-8")
    (tmp_path / "y.txt").write_text(f"not a seed: {H4_BLOCK[7]}1 nor 1{H4_BLOCK[7]}\n", encoding="utf-8")
    _git("add", "x.md", "y.txt", cwd=tmp_path)
    assert _git_hits(tmp_path) == {"x.md"}
    assert _working_hits(tmp_path) == {"x.md"}


@pytest.fixture(scope="module")
def folder():
    """The three-way design test's arithmetic folder (pure-literal expressions, names, `**`, tuple unpacking and
    augmented assignment; its N-9), loaded from that file, never copied."""
    return _load(THREE_WAY_TEST, "three_way_design_folder_for_h4")._Folder


def _fold_hits(folder, source: str) -> list[int]:
    import ast
    import warnings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(source)
    except SyntaxError:
        return []
    f = folder({_PREFIX, _PREFIX * 10, *H4_BLOCK})
    f.visit(tree)
    return sorted(set(f.lines))


def test_the_fold_finds_the_construction_only_where_declared(folder) -> None:
    files = _git("ls-files", "*.py").stdout.splitlines()
    found = set()
    for f in files:
        p = ROOT / f
        if p.is_file() and VENDOR_DATA not in p.parents and _fold_hits(folder, p.read_text("utf-8", errors="replace")):
            found.add(f)
    if _git("ls-files", THIS).stdout.strip():
        assert THIS in found, "the fold must find this file's own construction of the block (positive control)"
    assert found <= set(DERIVED_USES), f"H4's block is built by arithmetic outside its declared uses: {found}"


def test_the_fold_sees_a_planted_construction(folder) -> None:
    src = "Y = 2 ** 11 - 22\nP = Y * 1000 + 440\nS = P * 10 + 2\nQ = 2026 * 1000 + 441\n"
    assert _fold_hits(folder, src) == [2, 3]


# --------------------------------------------------------------------------------------------- no typed figure


def _stripped(t: str) -> str:
    """The text less what may hold a number: the script's fenced output, code spans, the seed rows, Appendix B's table
    (its numbers are MEASURES' own and its horizons are checked apart), dates, clock times, ids (E-208, P-14, H3-D,
    W42-R1, RD-04 ...), short codes (H4, S1, T4, U1), hashes, measure and list references, section numbers."""
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = t.replace(_between(t, "<!-- h4_measures: begin -->", "<!-- h4_measures: end -->"), " ")
    t = re.sub(r"`[^`\n]*`", " ", t)
    t = re.sub(r"^\| \d{8} \|.*$", " ", t, flags=re.M)
    t = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " ", t)
    t = re.sub(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", " ", t)
    t = re.sub(r"\b[A-Za-z]{1,4}\d*-\d+[A-Za-z]?\b", " ", t)
    t = re.sub(r"\b[A-Z]{1,2}\d{1,2}\b", " ", t)
    t = re.sub(r"\b[0-9a-f]{7,64}\b", " ", t)
    t = re.sub(r"\(\d{1,2}\)", " ", t)
    t = re.sub(r"\b(?:sections?|measures?|Appendix|its|the note's|note)\s+\d{1,2}(?:\.\d{1,2})?(?:\s+to\s+\d{1,2})?\b",
               " ", t)
    t = re.sub(r"\b2\^\d{1,2}\b", " ", t)                                   # the key words' bound, 2^32
    t = re.sub(r"\b\d{1,2}'s\b", " ", t)
    t = re.sub(r"\b(?:CHARTER|MEASURES|Wave|note|note's|its|W42-R1|sections?)\s+[1-9]\.\d{1,2}\b", " ", t)
    t = re.sub(r"^## \d{1,2}\. ", " ", t, flags=re.M)
    return t


def _numbers(t: str) -> set[str]:
    return set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])", _stripped(t)))


def test_no_typed_figure(text: str) -> None:
    extra = _numbers(text) - set(ALLOWED_NUMBERS)
    assert not extra, f"numbers typed outside the declared list (compute them in the script): {sorted(extra)}"


def test_no_typed_figure_catches_a_planted_one(text: str) -> None:
    for plant in ("the coin seeds are J = 128 here", "a gap of 0.0092 resolved", "the cap is 2.5 GB"):
        planted = text.replace("## 10. Power before the pin: J", f"## 10. Power before the pin: J\n\n{plant}")
        assert _numbers(planted) - set(ALLOWED_NUMBERS), plant


def test_every_figure_of_the_plan_is_in_the_scripts_block(text: str, plan) -> None:
    """J, the session counts and every hour appear only inside Appendix A's block."""
    J = plan.j_h4()
    outside = re.sub(r"```.*?```", " ", text, flags=re.S)
    for v in (J, plan.j_needed(), plan.units_needed(), plan.sessions_upper(), plan.sessions_lower()):
        assert not re.search(rf"(?<![\w.]){v}(?![\w])", outside), v


# ------------------------------------------------------------------------------------------- no held-out window


def test_no_held_out_window(text: str, plan) -> None:
    from extended import reader

    assert reader.declared_purposes(text) == frozenset(), "the judged-block line names no purpose"
    assert re.search(r"^- \*\*Judged-block reads:\*\* none\.$", text, re.MULTILINE)
    for line in text.splitlines():
        for d in re.findall(r"\b\d{4}-\d{2}-\d{2}\b", line):
            if d >= RECORD_DATES_FROM:                  # a date of the record (a review's, the seed search's)
                continue
            if d > "2023-12-29":
                assert d in HELD_DATES, f"a date after the search years that is no declared bound: {d}"
                assert any(w in line for w in UNREAD_WORDS) or line.startswith("| never read"), line
    assert plan.A.SEARCH == ("2020-01-02", "2023-12-29")
    report = plan.report()
    assert not re.search(r"\b202[4-9]-\d{2}-\d{2}\b", report), "the plan counts search-year sessions only"
    assert "refusing any span reaching 2024-01-02" in text and "`HeldOutRefused`" in text


# -------------------------------------------------------------------------------------------- the dependencies


def test_the_dependencies_are_named(text: str) -> None:
    dep = _between(text, "<!-- h4_dependencies: begin -->", "<!-- h4_dependencies: end -->")
    rows = [r for r in dep.splitlines() if r.startswith("| ") and not r.startswith("| dependency") and "---" not in r]
    names = [r.split("|")[1].strip() for r in rows]
    want = ("the seed-paired runner", "the firm path", "the cut", "the seed module's H4 block", "W42-R1",
            "the starts and the as-traded replays", "the measures", "the naive coin's source", "the reader")
    assert tuple(names) == want, names
    for r in rows:
        cells = [c.strip() for c in r.split("|")[1:-1]]
        assert len(cells) == 4 and all(cells), r
        assert len(cells[3]) > 60, f"what H4 needs from {cells[0]} is stated: {cells[3]!r}"
    by = {r.split("|")[1].strip(): r for r in rows}
    assert "`extended/three_way_runner.py` on wt/wt-three adedf7f" in by["the seed-paired runner"]
    assert "RB-1" in by["the seed-paired runner"]
    assert "the build item after Q-170" in by["the firm path"] and "**to build**" in by["the firm path"]
    assert "`vendor/stage2/propedge/campaign/lockstep.py`" in by["the firm path"]
    assert "`extended/search_cut.py`, being built under Q-172" in by["the cut"] and "**to build**" in by["the cut"]
    assert "**to build**" in by["the seed module's H4 block"]
    assert "wt/wt-infra 2bde318" in by["W42-R1"]
    assert 'journey_block="search"' in by["the starts and the as-traded replays"]
    for commit, path in ((RUNNER_COMMIT, "extended/three_way_runner.py"),
                         (RUNNER_COMMIT, "extended/three_way_seeds.py"),
                         (W42_COMMIT, "docs/plans/WAVE42_SETTING_RULE.md"), (W42_COMMIT, "extended/wave42.py")):
        assert _git("cat-file", "-e", f"{commit}:{path}", check=False).returncode == 0, (commit, path)
    runner = _show(RUNNER_COMMIT, "extended/three_way_runner.py")
    for name in ("class Plan", "def stress_arms", "def paired", "def matrix", "class HeldOutRefused",
                 'BASELINES = ("naive_coin", "p14", "p15", "p16")'):
        assert name in runner, name
    assert (ROOT / "vendor" / "stage2" / "propedge" / "campaign" / "lockstep.py").is_file()
    assert not (ROOT / "extended" / "search_cut.py").exists() or "search_cut" in text


def test_the_built_dependencies_hold_the_names_h4_uses() -> None:
    from extended import components, journey_measures, journey_readings, triggers, user_beside

    assert "search" in user_beside.JOURNEY_BLOCK_NAMES and "off" in user_beside.BY_NAME
    assert user_beside.BY_NAME["off"].kind == "off" and user_beside.BY_NAME["off"].enforcement_p == 0.0
    import inspect

    sig = inspect.signature(user_beside.run_starts).parameters
    assert "journey" in sig and "journey_block" in sig
    for f in ("coin_readings", "design_coin_readings", "variance_decomposition", "peak_oop", "bankroll_stop",
              "workload", "supply"):
        assert callable(getattr(journey_measures, f)), f
    assert callable(journey_readings.summary)
    assert hasattr(triggers, "CoinMarks") and callable(components.coin_component)
    assert callable(components.schedule_day)
    assert (ROOT / "extended" / "router.py").is_file()


# --------------------------------------------------------------------------------- the measures and W42-R1's keys


def test_every_measure_is_placed(text: str) -> None:
    index = _between(_lf(MEASURES), "<!-- measures-index:start -->", "<!-- measures-index:end -->")
    theirs = [int(m) for m in re.findall(r"^\| (\d+) \|", index, re.MULTILINE)]
    table = _between(text, "<!-- h4_measures: begin -->", "<!-- h4_measures: end -->")
    rows = re.findall(r"^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", table, re.MULTILINE)
    assert [int(r[0]) for r in rows] == theirs, "every measure of the index, once each, in order"
    allowed_where = {"W", "21", "63", "126", "252", "63, 126, 252", "each month", "—", "each headline's",
                     "each measure's", "the search years", "W, its share paid beside"}
    for n, _, status, where, _ in rows:
        s = status.strip()
        assert s.startswith(("read", "**not read**", "its ingredients read", "the comparator")), (n, s)
        assert where.strip() in allowed_where, (n, where)
    by = {int(r[0]): r for r in rows}
    assert by[33][2].strip().startswith("**not read**")
    assert "10 %" in by[28][2] and "+1 tick" in by[29][2]


def test_every_w42_input_is_named(text: str, w42) -> None:
    keys = set(w42.REQUIRED) | set(w42.OPTIONAL)
    assert {"spent_before_first_payout", "first_payout_days", "cash_to_first_pass", "peak_oop_12_months",
            "share_months_positive", "orders_max", "accounts_max", "taken_mean"} <= keys
    sec = _section(text, 9)
    table = _between(text, "<!-- h4_measures: begin -->", "<!-- h4_measures: end -->")
    for k in sorted(keys):
        if re.fullmatch(r"(net|peak)_month_\d", k):
            stem = k.rsplit("_", 1)[0]
            assert f"`{stem}_1` to `{stem}_3`" in sec, k
            assert f"`{k}`" in table, k
        else:
            assert f"`{k}`" in sec and f"`{k}`" in table, k
    for k in ("P_B", "`run_out`", "`not_paid_within_B`", "the per-unit spending before the first\n  payout"):
        assert k in sec, k
    assert w42.BASELINES == ("naive_coin", "p14", "p15", "p16") and w42.BLOCK == "search"


# --------------------------------------------------------------------------------------------- the plan, and J


def test_the_plan_is_the_scripts(text: str, plan) -> None:
    block = _between(text, "<!-- h4_plan: begin -->", "<!-- h4_plan: end -->").strip()
    assert block.startswith("```text\n") and block.endswith("\n```")
    assert block[len("```text\n"):-len("\n```")] == plan.report()


def test_the_scripts_constants_are_their_sources(plan, w42) -> None:
    from extended import family_stats, user_beside

    assert plan.W42_COMMIT == W42_COMMIT
    assert (plan.RESOLVE_Z, plan.DELTA_MIN, plan.W42_W) == (w42.RESOLVE_Z, w42.DELTA_MIN, w42.W)
    assert plan.POWER == w42.POWER_TARGET == family_stats.MDL_POWER
    assert plan.BASELINES == w42.BASELINES
    assert plan.EXACT_EVERY == user_beside.EXACT_EVERY
    assert plan.WINDOWS == (w42.W, 252) and plan.DIM_HORIZONS == tuple(sorted({d.horizon for d in w42.DIMENSIONS}))
    vend = (ROOT / "vendor" / "stage2" / "propedge" / "research" / "user_journey.py").read_text("utf-8")
    assert f"EXACT = {plan.EXACT!r}" in vend
    assert plan.A.SEARCH == ("2020-01-02", "2023-12-29") and plan.SEARCH_YEARS == 4


def test_j_is_a_power_of_two_at_or_above_the_need(plan) -> None:
    """Recomputed here from the formula, not read from the script's own functions."""
    from scipy import stats

    z = float(stats.norm.ppf(plan.POWER))
    n_units = math.ceil(((plan.RESOLVE_Z + z) / plan.DELTA_MIN) ** 2)
    import numpy as np

    weekdays = int(np.busday_count(np.datetime64("2020-01-02"), np.datetime64("2023-12-30")))
    lower = weekdays - plan.HOLIDAYS_A_YEAR * plan.SEARCH_YEARS
    need = math.ceil(n_units / (lower - max(plan.DIM_HORIZONS) + 1))
    J = plan.j_h4()
    assert J == plan.J_H4 if hasattr(plan, "J_H4") else True
    assert J >= need and J & (J - 1) == 0 and J < 2 * need, (J, need)
    for h in plan.DIM_HORIZONS:            # at J, a gap of DELTA_MIN is resolved at every horizon, at the lower bound
        assert (plan.RESOLVE_Z + z) / math.sqrt(J * (lower - h + 1)) <= plan.DELTA_MIN
    assert (plan.RESOLVE_Z + z) / math.sqrt((J // 2) * (lower - max(plan.DIM_HORIZONS) + 1)) > plan.DELTA_MIN \
        or J // 2 < need


def test_every_part_fits_its_cap_at_the_largest_assumed_cost(plan) -> None:
    A = plan.A
    w = plan.part_work(plan.j_h4())
    assert A.hours(w, max(A.COSTS_US)) <= A.PART_CAP_H
    assert plan.j_h4() * plan.BATCH_STARTS <= A.max_lanes()
    assert len(plan.ARM_RUNS) == 4 and {a for a, _, _ in plan.ARM_RUNS} == {"off", "worse_1", "missed_0.1"}


def test_the_responses_and_the_stress_arms(text: str) -> None:
    flat = " ".join(text.split())
    for phrase in ("`off` only", "`worse_1`", "`missed_0.1`", "the runner's `worse_2` arm is not run by H4",
                   "0 % payout denial, the placement off, the Focused Trader Program off"):
        assert phrase in flat, phrase
