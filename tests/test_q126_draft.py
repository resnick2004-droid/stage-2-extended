"""Q-126: T-0 of the second one-sample calibration plan (`docs/calibration/DRAFT_Q-126_one_sample_plan_2.md`, which the
lead may rename `Q-126_one_sample_plan_2.md` at its pin): the plan's seeds and form, and every figure it states held to
its arithmetic script (`docs/calibration/scripts/q126/q126_arith.py`). Fast tier; no engine, no bar, no run.

What it checks:
- **under either name** -- exactly one such plan under `docs/calibration/`; every check passes on a copy under the
  pinned name, and two copies at once are refused (E-095's pattern), so the test survives the rename;
- **the pin fits** `tests/test_declarations_fixed.py`'s calibration-plan pattern, read from that test's own source;
- **the seeds** -- section 4.1 lists the calibration block and the validation block once each, every role named and
  distinct; the plan writes no other eight-digit number (so no seed of another block: Q-108's two blocks, read from its
  pinned plan, and the replica's, read from Q-125's note, are checked by name too); the blocks appear, word-bounded,
  in no other file of the working tree or of any branch, remote or tag outside the declared uses (a document's mention
  outside `prereg/` and `docs/calibration/` is allowed, as Q-108's guard allows it); the lookahead test's derived range
  ends below the calibration block, by the margin the plan states;
- **the form** -- the grid and the scope-Q branch as the arithmetic declares them; Appendix B numbered 1..30, every row
  cited in the body and every citation a row;
- **the figures** -- the sizing and the floor's allowance (section 3.2), the probe (3.2, 4.3), the null counts (3.2,
  3.5), the criterion's and the floor's power (4.3), the power costs, the grid steps and the coverage (4.3, 5), each
  recomputed by the arithmetic script from its constants and Q-108's result files; and the cost (6.2), from Q-108's
  two run logs when they are present (skipped, saying so, when they are not).
"""
from __future__ import annotations

import ast
import importlib.util
import math
import re
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CALDIR = ROOT / "docs" / "calibration"
DRAFT_NAME = "DRAFT_Q-126_one_sample_plan_2.md"
PINNED_NAME = "Q-126_one_sample_plan_2.md"
ARITH = CALDIR / "scripts" / "q126" / "q126_arith.py"
Q108_PLAN = CALDIR / "Q-108_one_sample_plan.md"
Q125_NOTE = ROOT / "docs" / "research" / "Q-125_validation_failure_2026-11-17.md"
LOOKAHEAD = ROOT / "tests" / "test_features_lookahead.py"
PIN_TEST = ROOT / "tests" / "test_declarations_fixed.py"

CAL_BLOCK = tuple(range(20263010, 20263019 + 1))
VAL_BLOCK = tuple(range(20263020, 20263029 + 1))
SEEDS = CAL_BLOCK + VAL_BLOCK
SEED_PATTERN = "|".join(str(s) for s in SEEDS)
#: the repository files allowed to hold a seed of the blocks besides the plan: its declared uses. The build adds its
#: own files here (the module, the runners, their tests), as the plan's 4.1 allow-list names them.
DECLARED_USES = ("tests/test_q126_draft.py",)
LEAD_RECORDS = ("DECISIONS.md", "STATUS.md", "TASK_QUEUE.md", "PROGRESS.md")
OWN_RESULTS = re.compile(r"results/q126_[A-Za-z0-9_]+\.csv(\.manifest\.json)?")

SEED_ROW = re.compile(r"^\|\s*(\d{8})\s*\|\s*([^|]+?)\s*\|\s*$", re.MULTILINE)
EIGHT = re.compile(r"\b\d{8}\b")
B_ROW = re.compile(r"^\|\s*(\d+)\s*\|([^|]+)\|([^|]+)\|([^|]+)\|\s*$", re.MULTILINE)
B_REF = re.compile(r"\bB-(\d+)\b")


# ------------------------------------------------------------------------------------------------- the text


def plan(base: Path = CALDIR) -> Path:
    found = sorted(p for p in base.glob("*Q-126_one_sample_plan_2.md") if p.name in (DRAFT_NAME, PINNED_NAME))
    assert len(found) == 1, f"exactly one Q-126 plan expected under {base}, found {found}"
    return found[0]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def section(body: str, heading: str) -> str:
    """The text from the heading line starting with `heading` to the next heading of the same or a higher level."""
    level = len(heading.split(" ", 1)[0])
    lines = body.split("\n")
    start = None
    for i, line in enumerate(lines):
        if start is None and line.startswith(heading):
            start = i
            continue
        if start is not None and line.startswith("#"):
            hashes = len(line) - len(line.lstrip("#"))
            if hashes <= level and line[hashes:hashes + 1] == " ":
                return "\n".join(lines[start:i])
    assert start is not None, f"no heading starting {heading!r}"
    return "\n".join(lines[start:])


@lru_cache(maxsize=1)
def arith():
    spec = importlib.util.spec_from_file_location("q126_arith_for_test", ARITH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@lru_cache(maxsize=1)
def costs():
    A = arith()
    return A.power_costs(ROOT), A.interpolated(ROOT)


@lru_cache(maxsize=1)
def cover():
    return arith().coverage(ROOT)


def foreign_seeds() -> set[int]:
    """Q-108's two blocks (its 4.1 tables, ranges included) and the replica's seed, read from their own files."""
    q108 = section(read(Q108_PLAN), "### 4.1")
    out = {int(s) for s, _ in SEED_ROW.findall(q108)}
    for a, b in re.findall(r"^\|\s*(\d{8})-(\d{8})\s*\|", q108, re.MULTILINE):
        out |= set(range(int(a), int(b) + 1))
    rep = re.search(r"^SEED_REPLICA = (\d+)$", read(Q125_NOTE), re.MULTILINE)
    assert rep, "the replica's seed line is not in Q-125's Appendix A"
    out.add(int(rep.group(1)))
    assert len(out) >= 20, "Q-108's seed tables were not read"
    return out


# ------------------------------------------------------------------------------------------------- the checks, as
# functions of the text, so that the rename test runs each on a copy under the pinned name


def check_pin_form(body: str, name: str) -> None:
    assert body.startswith("# Q-126: "), "the title"
    src = PIN_TEST.read_text(encoding="utf-8")
    pat = r"`(docs/calibration/[^`]+\.md)` sha256 `([0-9a-f]{64})`"
    assert pat in src, "the calibration-plan pin pattern changed in tests/test_declarations_fixed.py: re-read it"
    row = f"| E-NNN | ... `docs/calibration/{name}` sha256 `{'0' * 64}` ... |"
    assert re.findall(pat, row) == [(f"docs/calibration/{name}", "0" * 64)], "the plan's path does not fit the pin"
    assert "c8e7424b46ff0c60ecb5b3ea875ac3b77e70f090a52f0cc0d999d7e416486d7e" in body, "Q-108's pinned plan, by hash"
    assert "## Appendix B" in body and "## Appendix A" in body


def check_seed_tables(body: str, name: str) -> None:
    rows = SEED_ROW.findall(section(body, "### 4.1"))
    seeds = [int(s) for s, _ in rows]
    assert seeds == list(SEEDS), f"4.1 must list the two blocks once each, in order: {seeds}"
    for block in (CAL_BLOCK, VAL_BLOCK):
        roles = [r.strip() for s, r in rows if int(s) in block]
        assert all(roles) and len(set(roles)) == len(roles), "every seed named by a distinct role"
    cal_roles = [r for s, r in rows if int(s) in CAL_BLOCK]
    val_roles = [r for s, r in rows if int(s) in VAL_BLOCK]
    assert cal_roles[-1].startswith("the probe's Monte Carlo side draws"), "the calibration block's last role: the probe"
    assert val_roles[-1].startswith("spare, drawn by nothing")
    assert f"**Calibration block, {CAL_BLOCK[0]}-{CAL_BLOCK[-1]}:**" in body
    assert f"**Validation block, {VAL_BLOCK[0]}-{VAL_BLOCK[-1]}:**" in body


def check_no_foreign_seed(body: str, name: str) -> None:
    eights = {int(x) for x in EIGHT.findall(body)}
    assert eights <= set(SEEDS), f"eight-digit numbers outside the plan's blocks: {sorted(eights - set(SEEDS))}"
    hits = [s for s in foreign_seeds() if re.search(rf"\b{s}\b", body)]
    assert not hits, "a seed of another block is written in the plan"


def check_grid(body: str, name: str) -> None:
    A = arith()
    s22 = section(body, "### 2.2")
    rows = re.findall(r"^\|\s*(\d)\s*\|\s*`([a-z0-9_.]+)`[^|]*\|\s*([0-9.]+)\s*\|[^|]*\|"
                      r"\s*(yes|no)\s*\|\s*([^|]+?)\s*\|$",
                      s22, re.MULTILINE)
    assert [int(r[0]) for r in rows] == list(range(1, 9)), rows
    grid = tuple(float(r[2]) for r in rows[:7])
    assert grid == A.GRID, grid
    assert [r[1] for r in rows[:7]] == [A.name_of(m) for m in A.GRID]
    assert rows[7][1] == "cons_bm_m1.25" and float(rows[7][2]) == 1.25
    assert all(r[3] == "yes" for r in rows), "every candidate is in scope D"
    branch = [r[1] for r in rows if r[4].strip("*") == "yes"]
    assert branch == [A.name_of(m) for m in A.GRID if m >= A.Q_BRANCH_MIN], branch


def check_appendix_b(body: str, name: str) -> None:
    app = section(body, "## Appendix B")
    rows = B_ROW.findall(app)
    nums = [int(r[0]) for r in rows]
    assert nums == list(range(1, 31)), f"Appendix B must number 30 choices 1..30: {nums}"
    for n, choice, where, why in rows:
        assert choice.strip() and where.strip() and why.strip(), f"B-{n} lacks its text, its place or its basis"
    before = body[:body.index("## Appendix B")]
    cited = {int(x) for x in B_REF.findall(before)}
    assert cited == set(nums), f"cited but not listed: {sorted(cited - set(nums))}; listed, never cited: " \
                               f"{sorted(set(nums) - cited)}"


def check_sizing(body: str, name: str) -> None:
    A = arith()
    s32 = flat(section(body, "### 3.2"))
    n = A.n_val()
    N = A.CAL_SUBSETS_PER_SIZE * len(A.SIZES)
    Nmin = A.min_cal_subsets()
    assert N >= Nmin, "the declared subsets do not meet the plan's own rule"
    assert A.CAL_SUBSETS_PER_SIZE - 20 < math.ceil(Nmin / len(A.SIZES)) <= A.CAL_SUBSETS_PER_SIZE, \
        "the declared count is the rule's minimum rounded up to a multiple of 20"
    must = [
        f"**{n} subsets**", f"**{n * len(A.VALUES) * len(A.EXACT_MODELS):,} exact subset nulls**",
        f"r_V = 1 - {A.VAL_PASS}^(1/{n}) = {A.punished_rate():.4e}",
        f"**at least {Nmin:,} subsets pooled, {math.ceil(Nmin / len(A.SIZES))} a size.**",
        f"**Declared: {A.CAL_SUBSETS_PER_SIZE} subsets at each size, {N:,} in all**",
        f"j = 0 to {A.CAL_SUBSETS_PER_SIZE - 1}",
        f"are {A.minimax_one(1.0):.4f} and {A.minimax_nested(1.0):.4f}",
        f"r_V was seen with probability {A.detection(n, A.punished_rate()):.4f}",
        f"Each size has {A.CAL_SUBSETS_PER_SIZE} calibration subsets against {A.VAL_SUBSETS_PER_SIZE} validation",
    ]
    for s in must:
        assert s in s32, f"3.2 lacks {s!r}"


def check_floor(body: str, name: str) -> None:
    """The floor at zero tolerance (E-176) and everything stated about it in 3.2 and 4.3, with E-173's reversed
    allowance and the c = 0..3 comparison held as the declared reading beside."""
    A = arith()
    n = A.n_val()
    N = A.CAL_SUBSETS_PER_SIZE * len(A.SIZES)
    assert A.ALLOWANCE == 0, "the declared floor is zero tolerance (E-176)"
    c3 = A.allowance(N, n)
    assert c3 == A.E173_ALLOWANCE == 3, "E-173's least allowance, the reading beside"
    r95, rV = A.guard_rate(n), A.punished_rate(n)
    b0, b3 = A.rule_bounds(N, n, 0), A.rule_bounds(N, n, c3)
    assert abs(b0["nested"] - n / (N + n)) < 1e-12, "the closed form at c = 0"
    beside = A.bound_by_subsets(n=n)
    s32 = flat(section(body, "### 3.2"))
    for s in ("A candidate is refused if **any** of the 3,300 subsets is bad (c = 0).",
              f"At r_V the floor sees a bad subset, and refuses, with probability {A.detection(N, rV):.4f}",
              f"by 3/{N:,} = {3 / N:.4e}, at which the validation's exact part passes with probability "
              f"{(1 - 3 / N) ** n:.4f}",
              f"bound that size's rate at {A.cp_upper(0, A.CAL_SUBSETS_PER_SIZE):.4e}",
              f"{b0['one']:.4f} for one candidate", f"{b0['nested']:.4f} for a branch nested in m",
              f"**{b0['primary']:.4f} for the primary**", f"{b0['nested']:.4f} when the scope-Q branch is the primary",
              f"**{b0['second']:.4f} for the second statistic**", f"{b0['all']:.4f} over the whole rule",
              f"which is {c3} -- so that",
              f"r_95 = 1 - {A.GUARD_PASS}^(1/{n}) = {r95:.4e}",
              f"refuses a candidate there with {1 - A.floor_admits(r95, N, 0):.4f}; E-173's c = {c3} would refuse it "
              f"with {1 - A.floor_admits(r95, N, c3):.4f} (c = {c3 - 1} with {1 - A.floor_admits(r95, N, c3 - 1):.4f})",
              f"rises to {b3['all']:.4f} over the rule ({b3['primary']:.4f} for the primary), against {b0['all']:.4f} "
              f"at c = 0",
              f"towards {1 - A.GUARD_PASS:.2f}",
              f"{beside[1][2]:.4f} at {beside[1][0]:,} subsets, {beside[2][2]:.4f} at {beside[2][0]:,} and "
              f"{beside[3][2]:.4f} at {beside[3][0]:,}"):
        assert s in s32, f"3.2 lacks {s!r}"
    steps = A.step_costs(ROOT)
    lo, hi = min(z for *_, z in steps), max(z for *_, z in steps)
    assert f"about {lo:.2f} to {hi:.2f} more minimum detectable lift" in s32
    s43 = section(body, "### 4.3")
    rates = [(r, "") for r in A.FLOOR_RATES[:4]] + [(r95, " (r_95)"), (rV, " (r_V)")] + \
            [(r, "") for r in A.FLOOR_RATES[4:]]
    for r, lab in rates:
        row = (f"| {r:.4e}{lab} | {A.floor_admits(r, N, 0):.4f} | {A.floor_admits(r, N, c3):.4f} | "
               f"{(1 - r) ** n:.4f} |")
        assert row in s43, f"4.3 lacks the floor row {row!r}"
    for c in A.COMPARED:
        b = A.rule_bounds(N, n, c)
        lab = {0: " (declared)", c3: " (E-173, reversed)"}.get(c, "")
        row = (f"| {c}{lab} | {1 - A.floor_admits(r95, N, c):.4f} | {1 - A.floor_admits(rV, N, c):.4f} | "
               f"{b['one']:.4f} | {b['nested']:.4f} | {b['primary']:.4f} | {b['second']:.4f} | {b['all']:.4f} |")
        assert row in s43, f"4.3 lacks the comparison row {row!r}"
    f43 = flat(s43)
    assert (f"98.9 % of the time, with probability {1 - A.floor_admits(1e-4, N, 0):.4f}, and one at r_95 with "
            f"{1 - A.floor_admits(r95, N, 0):.4f}") in f43
    assert round(100 * (1 - 1e-4) ** n, 1) == 98.9
    assert f"keeping the rule's chance of losing the line at {b0['all']:.4f}" in f43
    txt = (f"{steps[0][2]:.3f} from `{steps[0][0]}` to `{steps[0][1]}`, "
           + ", ".join(f"{z:.3f} to `{y}`" for _, y, z in steps[1:-1]) + f" and {steps[-1][2]:.3f} to `{steps[-1][1]}`")
    assert txt in f43, f"4.3 lacks the grid steps {txt!r}"
    assert f"{b0['one']:.4f} at c = 0, the declared floor ({b3['one']:.4f} at E-173's c = {c3})" in f43
    assert (f"**at the declared c = 0 it is n/(N + n) = {b0['nested']:.4f}, whatever the rates and however fine the "
            f"grid** ({b3['nested']:.4f} at E-173's c = {c3})") in f43
    assert f"catch a bad-subset rate of 1e-03 with probability {1 - (1 - 1e-3) ** n:.4f}" in f43
    assert "**no subset of the 3,300 is bad**" in flat(section(body, "### 4.2"))


def check_probe(body: str, name: str) -> None:
    A = arith()
    m = A.probe_nulls()
    s32 = flat(section(body, "### 3.2"))
    assert (f"{A.PROBE_PER_SIZE} x {len(A.SIZES)} x {len(A.PROBE_MODELS)} x {len(A.VALUES)} = **{m} probed nulls**"
            in s32)
    assert f"the {A.PROBE_PER_SIZE} sizing subsets with the largest exact size" in s32
    s43 = section(body, "### 4.3")
    for rho in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        row = f"| {rho} | {A.null_fail(rho):.3e} | {A.probe_refusal(rho):.4f} | {A.mc_pass(rho):.4f} |"
        assert row in s43, f"4.3 lacks the probe row {row!r}"
        assert A.probe_refusal(rho) <= 1 - A.mc_pass(rho) + 1e-12, "the probe is stricter than the validation"
    s42 = flat(section(body, "### 4.2"))
    assert "4. **No probed null reaches its failure count**" in s42 or "**No probed null reaches its failure count**" \
        in s42


def check_costs(body: str, name: str) -> None:
    """Section 6.2's cost lines, from Q-108's two run logs; a no-op when the logs are absent (the test below says so)."""
    A = arith()
    if not A.logs_present():
        return
    cs, vs = A.log_stats(A.CAL_LOG), A.log_stats(A.VAL_LOG)
    c = A.cost(cs, vs)
    s62 = flat(section(body, "### 6.2"))
    for s in (f"**the core:** {c['core'][0]:.1f} to {c['core'][1]:.1f} hours",
              f"({vs['exit_s']} s and {cs['exit_s']} s)",
              f"at {A.per_subset_value(vs):.2f} to {A.per_subset_value(cs):.2f} s a subset-value: "
              f"**{c['sizing'][0]:.1f} to {c['sizing'][1]:.1f} hours**",
              f"{A.probe_nulls()} Monte Carlo nulls at {vs['mc_mean']:.2f} to {cs['mc_mean']:.2f} s each: "
              f"{c['probe'][0]:.1f} to {c['probe'][1]:.1f} hours",
              f"the five exact models: {c['drift'][0]:.1f} to {c['drift'][1]:.1f} hours",
              f"**in all: {c['total'][0]:.1f} to {c['total'][1]:.1f} hours.**",
              f"at or below {cs['ws_max_mb']} MB", f"peaked at {cs['pairs_peak_mb']} MB"):
        assert s in s62, f"6.2 lacks {s!r}"


def check_counts(body: str, name: str) -> None:
    A = arith()
    core_exact, core_mc = 1170, A.MC_NULLS
    core = core_exact + core_mc
    extra = (A.CAL_SUBSETS_PER_SIZE - A.VAL_SUBSETS_PER_SIZE) * len(A.SIZES)
    sizing = extra * len(A.VALUES) * len(A.EXACT_MODELS)
    exact = core_exact + sizing
    probe = A.probe_nulls()
    rule13 = exact + core_mc
    rule = rule13 + probe
    N = A.CAL_SUBSETS_PER_SIZE * len(A.SIZES)
    drift = A.DRIFT_SCENARIOS * A.DRIFT_POPULATIONS * len(A.DRIFT_MODELS)
    s32, s35 = flat(section(body, "### 3.2")), flat(section(body, "### 3.5"))
    for s in (f"{extra:,} sizing subsets x 2 values x 5 exact models = **{sizing:,} sizing nulls**",
              f"{exact:,} exact nulls (20 on the fixed streams) and {core_mc:,} Monte Carlo, **{rule13:,} in conditions "
              f"1 to 3**", f"the {probe} probed nulls in condition 4: **{rule:,} in the rule**",
              f"{N * len(A.VALUES) * len(A.EXACT_MODELS):,} on subsets, {N * len(A.VALUES):,} of them at L = 42"):
        assert s in s32, f"3.2 lacks {s!r}"
    for s in (f"| {core:,} |", f"| {sizing:,} |", f"| {probe} |",
              f"| **{rule:,}** | {exact:,} exact, {core_mc + probe:,} Monte Carlo |",
              f"| **{core:,}** |", f"| {drift:,} |"):
        assert s in s35, f"3.5 lacks {s!r}"
    assert f"{drift:,} nulls beside" in flat(section(body, "### 3.3"))
    assert f"0 to {exact - 1:,} at the calibration, 0 to {core_exact - 1:,}" in flat(body)
    assert f"**Size:** {rule:,} nulls in the rule -- {exact:,} exact and {core_mc + probe:,} Monte Carlo" in \
        flat(section(body, "### 6.2"))


def check_criterion_power(body: str, name: str) -> None:
    A = arith()
    s43 = flat(section(body, "### 4.3"))
    fails = ", ".join(str(A.FAIL[k]) for k in A.KS[:-1]) + f" and {A.FAIL[A.KS[-1]]}"
    assert f"fewer rejections than {fails} at k = 13..20" in s43
    n = A.n_val()
    r95 = A.guard_rate(n)
    for label, r in (("1e-04", 1e-4), (f"r_95, {r95:.4e}", r95), ("1e-03", 1e-3), ("0.01", 0.01)):
        assert re.search(rf"a (pooled bad-subset )?rate of {re.escape(label)} \| "
                         rf"{(1 - r) ** n:.4f} \|", s43), f"4.3 lacks the exact-part row at {label}"
    for rho, txt in ((0.5, "every one of the 1,123 nulls at 0.5 of nominal"), (0.6, "every null at 0.6 of nominal"),
                     (0.7, "every null at 0.7 of nominal"), (0.8, "every null at 0.8 of nominal"),
                     (0.9, "every null at 0.9 of nominal"), (1.0, "every null exactly at nominal")):
        assert f"{txt} | {A.mc_pass(rho):.4f} |" in s43, f"4.3 lacks the Monte Carlo row at {rho}"
    tol = {rho: round(A.tolerated(rho)) for rho in (1.0, 0.9, 0.8, 0.7)}
    assert (f"at most {tol[1.0]} nulls exactly at nominal, {tol[0.9]} at 0.9 of nominal, {tol[0.8]} at 0.8 and "
            f"{tol[0.7]} at 0.7") in s43
    pm = A.choice_p_mc(ROOT)
    for c in (("cons_m1.25", "Q"), ("cons_m1.25", "D"), ("cons_m1.5", "Q"), ("cons_bm_m1.25", "D")):
        assert f"{pm[c]:.6f}" == "1.000000", c
    assert "P_MC was 1.000000" in s43


def check_power_costs(body: str, name: str) -> None:
    pc, ip = costs()
    s5 = section(body, "## 5.")
    for cand, (how, lo, hi) in pc.items():
        if how == "file":
            cell = f"{lo:.3f}"
        else:
            cell = f"{lo:.3f} to {hi:.3f} (linear interpolation {ip[cand]:.3f})"
        assert re.search(rf"^\| `{re.escape(cand)}` \| [0-9.]+ \| {re.escape(cell)} \|", s5, re.MULTILINE), \
            f"section 5 lacks {cand}'s cost {cell}"
    assert f"A ratio of {pc['cons_m1.5'][1]:.3f} means" in flat(s5)


def check_coverage(body: str, name: str) -> None:
    mean, lo, hi = cover()
    s5 = section(body, "## 5.")
    labels = {"flip21": "flips at 21", "flip42": "flips at 42", "flip55": "flips at 55", "flip63": "flips at 63",
              "alt45": "alternating 45", "alt55": "alternating 55", "markov30": "Markov, dwell 30",
              "markov50": "Markov, dwell 50", "markov80": "Markov, dwell 80"}
    for m, lab in labels.items():
        row = f"| {lab} | {mean[m]:.3f} | {lo[m]:.3f} to {hi[m]:.3f} |"
        assert row in s5, f"section 5 lacks {row!r}"
    for m in ("flip1", "flip5", "coin"):
        assert (mean[m], lo[m], hi[m]) == (1.0, 1.0, 1.0), m
    assert "| flips at 1 and 5, the coin | 1.000 | 1.000 to 1.000 |" in s5
    words = {2: "two", 9: "nine"}
    assert round(5 * (1 - mean["markov50"])) == 2 and round(10 * (1 - mean["markov80"])) == 9
    assert (f"about {words[2]} in five at a mean dwell of 50 sessions, and {words[9]} in ten at 80"
            in flat(s5))
    A = arith()
    assert f"had a worst flip-42 ratio of {A.worst_flip42('cons_m1.5', 'Q', ROOT):.3f}" in flat(s5)


CHECKS = (check_pin_form, check_seed_tables, check_no_foreign_seed, check_grid, check_appendix_b, check_sizing,
          check_floor, check_probe, check_counts, check_criterion_power, check_power_costs, check_coverage, check_costs)


@pytest.mark.parametrize("check", CHECKS, ids=[c.__name__ for c in CHECKS])
def test_the_plan(check):
    p = plan()
    check(read(p), p.name)


def test_the_cost_figures_against_the_logs():
    """Section 6.2 against Q-108's two run logs: skipped, saying so, where the logs are not on this machine."""
    if not arith().logs_present():
        pytest.skip("Q-108's run logs are not present: the cost figures of 6.2 are not checked here")
    p = plan()
    check_costs(read(p), p.name)


def test_every_check_holds_under_the_pinned_name_and_two_copies_are_refused(tmp_path):
    src = plan()
    shutil.copyfile(src, tmp_path / PINNED_NAME)
    found = plan(tmp_path)
    assert found.name == PINNED_NAME
    for check in CHECKS:
        check(read(found), found.name)
    shutil.copyfile(src, tmp_path / DRAFT_NAME)
    with pytest.raises(AssertionError, match="exactly one"):
        plan(tmp_path)


def test_the_checks_can_fail():
    """Not vacuous: a foreign eight-digit number, a seed row dropped, a smaller declared count, a wrong cost, an
    uncited Appendix B row are each refused."""
    p = plan()
    body = read(p)
    with pytest.raises(AssertionError):
        check_no_foreign_seed(body + f"\n{CAL_BLOCK[0] - 1}\n", p.name)
    row = next(line for line in section(body, "### 4.1").split("\n") if line.startswith(f"| {VAL_BLOCK[3]} |"))
    with pytest.raises(AssertionError):
        check_seed_tables(body.replace(row + "\n", ""), p.name)
    with pytest.raises(AssertionError):
        check_sizing(body.replace("**Declared: 660 subsets at each size", "**Declared: 600 subsets at each size"),
                     p.name)
    with pytest.raises(AssertionError):
        check_power_costs(body.replace("| `cons_m2` | 2.0 | 1.567 |", "| `cons_m2` | 2.0 | 1.500 |"), p.name)
    with pytest.raises(AssertionError):
        check_appendix_b(body.replace("(after the look, B-9)", "(after the look)"), p.name)
    with pytest.raises(AssertionError):
        check_floor(body.replace("is bad (c = 0).", "is bad (c = 1)."), p.name)
    with pytest.raises(AssertionError):
        check_floor(body.replace("| 2 | 0.1840 | 0.5818 |", "| 2 | 0.1840 | 0.6000 |"), p.name)
    with pytest.raises(AssertionError):
        check_probe(body.replace("| 0.8 | 1.431e-03 | 0.7321 |", "| 0.8 | 1.431e-03 | 0.7000 |"), p.name)
    if arith().logs_present():
        with pytest.raises(AssertionError):
            check_costs(body.replace("**in all: 15.4 to", "**in all: 12.0 to"), p.name)


# ------------------------------------------------------------------------------------------------- the seeds in files


def _git(*a: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")


def _allowed(path: str) -> bool:
    path = path.replace("\\", "/")
    if path in (f"docs/calibration/{DRAFT_NAME}", f"docs/calibration/{PINNED_NAME}") or path in DECLARED_USES:
        return True
    if path in LEAD_RECORDS or OWN_RESULTS.fullmatch(path):
        return True
    # a document's mention (a review, an audit, a brief, a note) is allowed, as Q-108's guard allows it -- but not a
    # declaration's or another calibration plan's
    return path.lower().endswith(".md") and not path.startswith(("prereg/", "docs/calibration/"))


def test_the_blocks_appear_in_no_other_file():
    """The working tree (tracked and untracked, not ignored: the licensed data's junctions are ignored) and every
    branch, remote and tag, word-bounded."""
    r = _git("grep", "--untracked", "-l", "-I", "-w", "-E", SEED_PATTERN)
    assert r.returncode in (0, 1), r.stderr
    hits = [f"working tree: {p}" for p in r.stdout.splitlines() if not _allowed(p)]
    refs = _git("for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", "refs/tags").stdout.split()
    refs = [x for x in refs if not x.endswith("/HEAD")]
    for i in range(0, len(refs), 40):
        r = _git("grep", "-l", "-I", "-w", "-E", SEED_PATTERN, *refs[i:i + 40], "--")
        assert r.returncode in (0, 1), r.stderr
        for line in r.stdout.splitlines():
            ref, _, path = line.partition(":")
            if not _allowed(path):
                hits.append(f"{ref}: {path}")
    assert not hits, "\n".join(sorted(set(hits)))


def test_the_scan_finds_a_seed_where_it_is():
    r = _git("grep", "--untracked", "-l", "-I", "-w", "-E", SEED_PATTERN)
    assert "tests/test_q126_draft.py" in r.stdout.splitlines(), "the scan does not see this file's own blocks"


def test_the_lookahead_range_ends_below_the_calibration_block():
    """`SEED_REPLACE + 1000 + i` over the 790 alert marks (that test's own text): its last value below the block, by
    the margin section 4.1 states."""
    text = LOOKAHEAD.read_text(encoding="utf-8")
    tree = ast.parse(text)
    replace = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Tuple):
            names = [t.id for t in node.targets[0].elts if isinstance(t, ast.Name)]
            if "SEED_REPLACE" in names and isinstance(node.value, ast.Tuple):
                replace = node.value.elts[names.index("SEED_REPLACE")].value
    assert isinstance(replace, int), "SEED_REPLACE not found"
    assert "seed=SEED_REPLACE + 1000 + i" in text
    marks = int(re.search(r"len\(rows\) == (\d+)", text).group(1))
    last = replace + 1000 + marks - 1
    assert last < CAL_BLOCK[0]
    gap = CAL_BLOCK[0] - last
    assert f"last value is {gap} below the calibration block's first seed" in flat(read(plan()))


@pytest.mark.slow
def test_the_derived_guard_refuses_nothing():
    """Q-108's AST fold guard (`scripts/q108_calibrate.py`), re-pointed at this plan's blocks with no allow-list."""
    spec = importlib.util.spec_from_file_location("q108_guard_for_q126", ROOT / "scripts" / "q108_calibrate.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    mod.CAL_BLOCK, mod.VAL_BLOCK = CAL_BLOCK, VAL_BLOCK
    mod.SEED_ALLOW, mod.SEED_ALLOW_PREFIXES = frozenset(), ("\0",)
    problems, prints = mod.derived_problems(ROOT)
    assert not problems, problems
    assert any("SEED_REPLACE + 1000 + i" in p for p in prints)
