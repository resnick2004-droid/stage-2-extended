"""Q-214: the Topstep survey's declaration draft (`prereg/DRAFT_F-13_topstep_survey.md`), its form checks -- on its own
text, on the reader's and the survey runner's own rules, and on the repository's files (no engine run, no bar, no
result file; fast). Modelled on `tests/test_h4_draft.py`'s form checks.

- **the template's fields** -- every numbered heading of `prereg/TEMPLATE_design_search.md` (text v3, E-284), word for
  word and in order; the design-search marker; the market, firm and deciding-files lines read exactly as the reader
  reads them (`reader.design_search_problems`, with planted controls); every rule key the levers lean on listed with
  its status in the record; every lever of `lever_space.LEVERS` classed once, as the loader classes it;
- **the survey-spec block** -- JSON with `survey.SPEC_KEYS` exactly, its seeds section 12's by role, its selection and
  re-read seed indices disjoint, its blocks inside the search years; once its placeholders are filled with fixture
  values it loads through `survey.load_spec`, and unfilled it is refused (`SpecRefused`);
- **the count** -- written as a product and a number, equal to the spec's sizes;
- **seeds by role** -- section 12's ten consecutive seeds once each, every other seed named by role only, the block's
  literal in no other tracked or committable file, and built by arithmetic in no other tracked `.py` (the three-way
  design test's folder and H4's widened evaluator, loaded from those files, never copied), with planted controls;
- **no held-out read** -- no `Judged-block reads:` purpose; a held-out date only in a never-read or refusal sentence;
  the confirmation window only as declared; the protocol's outcomes read through 2023-12-29 at the latest;
- **the placeholders until W42-R1 is applied (Q-189)** -- section 7's eight inputs from W42-R1's output, the spec's
  values and margin rows, and H3-D's inputs, each still `<...>`, and the lint's pin-mode errors exactly those (and the
  gatekeeper's `F-XX`), its plain mode clean.

At the pin the file is renamed (`F-XX` replaced) and this test's `DRAFT`, `DECLARED_USES` and the placeholder checks
move with it (as `tests/test_h4_draft.py`'s did).
"""
from __future__ import annotations

import ast
import hashlib
import copy
import importlib.util
import json
import re
import subprocess
import sys
import warnings
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "prereg" / "DRAFT_F-13_topstep_survey.md"
TEMPLATE = ROOT / "prereg" / "TEMPLATE_design_search.md"
THREE_WAY_TEST = ROOT / "tests" / "test_three_way_design.py"
H4_TEST = ROOT / "tests" / "test_h4_draft.py"
LINT = ROOT / "scripts" / "decl_lint.py"
VENDOR_DATA = ROOT / "vendor" / "stage2" / "data"
THIS = Path(__file__).resolve().relative_to(ROOT).as_posix()

#: section 12's block, built by arithmetic so that this file holds no literal of it
_PREFIX = 2026 * 1000 + 451
F13_BLOCK = tuple(_PREFIX * 10 + i for i in range(10))
#: exported under `SEED_BLOCK` so `scripts/decl_lint.py` recognises this draft's seed guard
SEED_BLOCK = F13_BLOCK
#: the files allowed to hold a literal of the block: the declaration only (the seed module joins at the build)
DECLARED_USES = ("prereg/DRAFT_F-13_topstep_survey.md",)
#: the files allowed to construct it by arithmetic: this test
DERIVED_USES = (THIS,)
#: the roles, in section 12's order (S5 is H3's deciding roles, cited by role, between S4 and S6)
ROLES = ("tests", "S0", "S1", "S2", "S3", "S4", "S6", "spare", "spare", "spare")
SKIP_DIRS = {".git", "data", "__pycache__", ".pytest_cache", "node_modules"}
MARK = "**Declaration kind: design search.**"
AWAIT = "awaiting W42-R2's application, Q-189"
#: decision rows the draft cites that the lead's records commit adds to master (E-296, E-297): the plain lint may
#: report them missing only while master lacks them -- the allowance expires by itself once the rows land
PENDING_ROWS = ("E-296", "E-297")
#: section 7's inputs that come from W42-R1's applied output, each with the output key the head list names
W42_ROWS = {
    "**the limits**": "`limits`",
    "**the bankroll budgets**": "`budgets`",
    "the **dimension** definitions": "`dimensions`",
    "**the weights**": "`weights`",
    "**the composite** or **the fallback**": "`form`",
    "**the size that matters**": "`delta_star`",
    "the **no-harm margin**": "`delta_star`",
    "**the do-nothing floor**": "`null_journeys`",
}
TO_BUILD = ("extended/survey_parts.py", "extended/survey_route.py", "extended/wave42_r2.py",
            "scripts/wave42_r2_apply.py")
HELD_FIRST, HELD_LAST, CONFIRM, SEARCH_LAST = "2024-01-02", "2026-07-16", "2026-07-17", "2023-12-29"
RECORD_DATES_FROM = "2026-11-01"
UNREAD = re.compile(r"never read|refus|unread|held-out years|confirmation window|read ledger|written after")


def _lf(p: Path) -> str:
    return p.read_bytes().decode("utf-8").replace("\r\n", "\n")


def _flat(s: str) -> str:
    return " ".join(s.split())


def _git(*args: str, cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          check=check)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def text() -> str:
    return _lf(DRAFT)


def _section(t: str, n: int) -> str:
    i = t.index(f"\n## {n}. ")
    j = t.find(f"\n## {n + 1}. ", i + 1)
    return t[i:j if j >= 0 else len(t)]


def _unfenced(t: str) -> str:
    return re.sub(r"^```.*?^```[ \t]*$", " ", t, flags=re.M | re.S)


def _spec(t: str) -> dict:
    m = re.findall(r"^```survey-spec[ \t]*\n(.*?)^```[ \t]*$", t, flags=re.M | re.S)
    assert len(m) == 1, "exactly one survey-spec block"
    return json.loads(m[0])


def _rows(sec: str) -> list[list[str]]:
    return [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in sec.splitlines()
            if ln.lstrip().startswith("|") and not re.match(r"^\s*\|[-| ]+\|\s*$", ln)]


# ------------------------------------------------------------------------------------------ the template's fields


def test_the_templates_sections_word_for_word_and_in_order(text: str) -> None:
    heads = re.findall(r"^## \d+\. .*$", _lf(TEMPLATE), flags=re.M)
    assert len(heads) == 17, heads                                       # sections 0 to 16
    mine = re.findall(r"^## \d+\. .*$", text, flags=re.M)
    assert mine == heads, [h for h in heads if h not in mine] or mine
    assert text.startswith("# F-XX: "), "the id is the gatekeeper's"
    assert MARK in text and "**Declaration kind: held-out test.**" not in text
    assert "`876be096402fc7d024037a9a81a2bef1fd2852f7ba1714c3389c23007b4ddc09`" in text     # E-284's template pin
    assert "*To use it:*" not in text and "**To use it:**" not in text, "the template's instructions are deleted"


def test_the_scope_fields_read_as_the_reader_reads_them(text: str) -> None:
    from extended import reader as R

    assert R.design_search_problems(text) == []
    plans = R.firm_plans()
    assert "combine50k" in plans["Topstep"]
    files = R._deciding_files(text)
    assert files and files[0] == "extended/reader.py" and "extended/survey.py" in files
    for f in files:
        assert (ROOT / f).is_file() or f in TO_BUILD, f"a deciding file that is neither here nor declared to build: {f}"
    for f in TO_BUILD:
        assert f in files, f
    assert ("`extended/survey_parts.py`, `extended/survey_route.py`, `extended/wave42_r2.py` and "
            "`scripts/wave42_r2_apply.py` are written by the build before the pin") in _flat(text)
    # planted controls: each field in another form is a problem
    line = next(ln for ln in text.splitlines() if ln.startswith("- **The market:**"))
    assert R.design_search_problems(text.replace(line, line.replace("NQ --", "ES --", 1)))
    firm = next(ln for ln in text.splitlines() if ln.startswith("- **The firm and account:**"))
    assert R.design_search_problems(text.replace(firm, firm.replace("Topstep,", "MFFU,", 1)))
    assert R.design_search_problems(text.replace(firm, firm + " and Lucid"))
    dec = next(ln for ln in text.splitlines() if ln.startswith("- **The deciding files:**"))
    assert R.design_search_problems(text.replace(dec, dec.replace("`extended/reader.py`, ", "", 1)))
    assert R.design_search_problems(text.replace(dec, dec + " (and the rest)"))


def test_every_rule_key_is_listed_with_its_status(text: str) -> None:
    from extended import lever_space as LS

    sec = _section(text, 1)
    rows = _rows(sec)
    keys = sorted({k for lv in LS.LEVERS.values() for k in lv.keys})
    keys += ["back2funded_fee_by_pricing_path", "tier1_news_events_restriction", "economic_releases_list",
             "cross_account_opposite_positions", "cross_account_hedging",
             "prohibited_strategy_max_size_into_major_news"]
    for k in keys:
        hit = [r for r in rows if f"`{k}`" in r[0]]
        assert len(hit) == 1, f"{k}: listed {len(hit)} times in section 1's key table"
        status = LS.rule_status(k)[1]
        assert status in hit[0][2], f"{k}: the table says {hit[0][2]!r}, the record {status!r}"


def test_every_lever_is_classed_once_as_the_loader_classes_it(text: str) -> None:
    from extended import lever_space as LS

    rows = [r for r in _rows(_section(text, 3)) if re.fullmatch(r"[TSA]\d+b?", r[0])]
    ids = [r[0] for r in rows]
    assert sorted(ids) == sorted(LS.LEVERS), sorted(set(ids) ^ set(LS.LEVERS))
    assert len(ids) == len(set(ids)), "each lever once"
    word = {LS.SEARCHED: "searched", LS.FIXED: "fixed", LS.DROPPED: "dropped"}
    for r in rows:
        assert r[3].startswith(word[LS.LEVERS[r[0]].cls]), (r[0], r[3])
        assert r[1] == LS.LEVERS[r[0]].layer, (r[0], r[1])
    t1 = next(r for r in rows if r[0] == "T1")
    assert "**narrowed here**" in t1[4] and "`trigger_sides.NO_SIDE`" in t1[4]
    held = {r[0] for r in rows if "**held until wired**" in r[3]}
    assert held == set(LS.HELD_UNTIL_WIRED)


# ---------------------------------------------------------------------------------------------- the survey-spec


def test_the_spec_block_holds_the_runners_keys_and_section_12s_seeds(text: str) -> None:
    from extended import search_space as SS, survey as SV

    s = _spec(text)
    assert set(s) == set(SV.SPEC_KEYS) | {"screen"}, "the runner's keys and the declared screen (a build item)"
    for k, want in SV.SPEC_KEYS.items():
        if want is not None and k != "plateau":
            assert set(s[k]) == set(want), k
    assert s["baselines"]["names"] == list(SV.BASELINES)
    seeds = dict(zip(ROLES, F13_BLOCK))
    assert s["survey"]["seed"] == seeds["S0"] and s["survey"]["method"] == "sobol"
    assert s["baselines"]["seed"] == seeds["S1"]
    assert s["rounds"]["seed"] == seeds["S2"]
    assert s["plateau"]["seed"] == seeds["S3"] and s["plateau"]["box_seed"] is None
    used = {s["survey"]["seed"], s["baselines"]["seed"], s["rounds"]["seed"], s["plateau"]["seed"]}
    assert not used & {seeds["S4"], seeds["S6"], *F13_BLOCK[7:]}, "S4 and the spares draw nothing here"
    sel, rer = s["protocol"]["seeds"], s["finalists"]["reread_seeds"]
    assert sel == list(range(16)) and rer == list(range(16, 80))
    assert not set(sel) & set(rer) and len(rer) >= SS.MIN_REREAD_SEEDS
    assert s["plateau"]["rule"]["margin"] == SV.DELTA_STAR and s["plateau"]["rule"]["side"] == "worse"
    assert s["objective"]["rule_id"] == "W42-R2"                 # E-296: W42-R2, never W42-R1
    if SV.W42_RULE != "W42-R2":                                  # the head's build item 1 moves it
        assert "`survey.W42_RULE` and `load_objective` read W42-R2's rule id" in _flat(text)
    for b in s["protocol"]["blocks"]:
        assert "2020-01-02" <= b[0] <= b[1] <= SEARCH_LAST
    assert SS.reads_through(s["protocol"]["blocks"], s["protocol"]["horizon"]).isoformat() <= SEARCH_LAST
    assert all(p["id"].startswith("extended.") for p in s["parts"].values())


def _filled(s: dict) -> dict:
    """The spec with every placeholder replaced by a fixture value of its form (never a value of the search)."""
    f = copy.deepcopy(s)
    hexed = "0" * 64
    f["prereg_id"] = "F-99"
    f["protocol"]["sha256"] = hexed
    f["objective"].update(values_row="E-999", code_sha256=hexed)
    f["no_harm"] = {"margin": 0.01, "margin_row": "E-999"}
    f["plateau"]["rule"].update(steps={"A6": 1}, tolerance_se=2.5)
    for k, part in f["parts"].items():
        part["sha256"] = hexed
        if k != "engine":
            part["data"] = {}
        if k == "space":
            part["digest"] = hexed
    return f


def test_the_spec_loads_once_filled_and_is_refused_unfilled(text: str) -> None:
    from extended import survey as SV

    s = _spec(text)
    with pytest.raises(SV.SpecRefused):
        SV.load_spec(text)                                 # the placeholders refuse (the refusal intended)
    filled = _filled(s)
    with pytest.raises(SV.SpecRefused):                    # today's runner refuses the screen key: a build item
        SV.load_spec(f"```survey-spec\n{json.dumps(filled)}\n```\n")
    filled.pop("screen")
    with pytest.raises(SV.SpecRefused):                    # today's runner refuses W42-R2's rule id: build item 1
        SV.load_spec(f"```survey-spec\n{json.dumps(filled)}\n```\n")
    filled["objective"]["rule_id"] = SV.W42_RULE           # the form check only, at today's rule id
    body = json.dumps(filled, indent=2)
    got = SV.load_spec(f"```survey-spec\n{body}\n```\n")
    assert got.survey_n == 512 and got.rounds == 8 and got.candidates == 4 and got.z == 2.0
    placeholders = [m for m in re.findall(r'"<\.\.\.>[^"]*"', text)]
    assert len(placeholders) >= 12, "the build's and W42-R1's values are left visibly blank"


def test_the_count_is_a_product_and_a_number_equal_to_the_spec(text: str) -> None:
    s = _spec(text)
    n, r, b = s["survey"]["n"], s["rounds"]["count"], s["rounds"]["batch"]
    sec = _flat(_section(text, 13))
    assert f"the rounds' {r} x {b} = {r * b} designs, so `k_cells` = {n} + {r * b} = {n + r * b} designs read" in sec
    assert s["survey"]["max_proposals"] == 64 * n and f"at most 64 x {n} = {64 * n} proposals" in sec
    assert f"at most {s['finalists']['candidates']} more cells" in sec
    assert f"**{n} designs**" in _flat(_section(text, 6)) and f"**{r} rounds of {b} designs each**" in _flat(
        _section(text, 6))


# ------------------------------------------------------------------------------------------------------- seeds


def test_the_seed_table_by_role(text: str) -> None:
    sec = _section(text, 12)
    rows = re.findall(r"^\| (\d{8}) \| ([^|]+) \|$", sec, re.MULTILINE)
    assert [int(r[0]) for r in rows] == list(F13_BLOCK), "ten consecutive seeds, once each, in order"
    roles = [r[1].strip() for r in rows]
    for lab, role in zip(ROLES, roles):
        if lab.startswith("S"):
            assert role.startswith(f"`{lab}`: "), (lab, role)
    assert roles[0].startswith("the unit tests") and roles[7:] == ["spare, drawn by nothing"] * 3
    assert "drawn by nothing in this search" in roles[5] and roles[6].startswith("`S6`: spare, drawn by nothing")
    assert "| H3's deciding roles | `S5`:" in sec
    toks = set(re.findall(r"(?<![\w.-])2026\d{4}(?![\w-])", text))
    assert toks <= {str(x) for x in F13_BLOCK}, f"another block's seed in the text: {sorted(toks)}"
    flat = _flat(sec)
    for s in ("never the seed plus an offset (E-171)", "`ProvenanceRefused`", "**H4's coin role `h4b_coins`**",
              "`git grep -IlwE` over every branch, remote and tag", "`git log --all -G`"):
        assert s in flat, s


def test_the_inherited_roles_exist_where_cited() -> None:
    from extended import three_way_seeds as TS

    for role in ("h3d_histories", "h3d_coins", "h3d2_history_null", "h3d3_plants"):
        assert TS.STATUS[role] == "deciding", role
    assert TS.H4_STATUS["h4b_coins"] == "reading" and TS.PARTS["H4-B"]
    assert not set(F13_BLOCK) & (set(TS.BLOCK) | set(TS.H4_BLOCK))


_BLOCK_RE = r"\b(" + "|".join(str(s) for s in range(_PREFIX * 10, _PREFIX * 10 + 10)) + r")\b"
_BLOCK_BYTES = re.compile(_BLOCK_RE.encode("ascii"))


def _git_hits(repo: Path) -> set[str]:
    out = _git("grep", "-IlwE", _BLOCK_RE, cwd=repo, check=False).stdout
    return {line.strip() for line in out.splitlines() if line.strip()}


def _file_hit(p: Path) -> bool:
    data = p.read_bytes()
    return b"\0" not in data[:8192] and bool(_BLOCK_BYTES.search(data))


def _working_hits(base: Path) -> set[str]:
    """Every file git can commit: tracked, and untracked files not git-ignored, of any suffix; binaries skipped."""
    out = _git("ls-files", "-z", "--cached", "--others", "--exclude-standard", cwd=base).stdout
    found = set()
    for rel_s in sorted({r for r in out.split("\0") if r}):
        p, rel = base / rel_s, Path(rel_s)
        if not p.is_file() or SKIP_DIRS & set(rel.parts[:-1]) or VENDOR_DATA in p.parents:
            continue
        try:
            if _file_hit(p):
                found.add(rel.as_posix())
        except OSError:
            continue
    return found


def test_the_block_nowhere_else() -> None:
    tracked = _git_hits(ROOT)
    assert tracked <= set(DECLARED_USES), f"a literal of the block outside its declared uses: {sorted(tracked)}"
    working = _working_hits(ROOT)
    assert DECLARED_USES[0] in working, "the scan must find the draft's own table (positive control)"
    assert working <= set(DECLARED_USES), f"a literal of the block outside its declared uses: {sorted(working)}"


def test_the_scans_find_a_planted_seed(tmp_path: Path) -> None:
    _git("init", "-q", cwd=tmp_path)
    (tmp_path / "x.md").write_text(f"a seed {F13_BLOCK[3]} here\n", encoding="utf-8")
    (tmp_path / "y.txt").write_text(f"not a seed: {F13_BLOCK[3]}1 nor 1{F13_BLOCK[3]}\n", encoding="utf-8")
    (tmp_path / "run.log").write_text(f"an untracked log naming {F13_BLOCK[5]}\n", encoding="utf-8")
    (tmp_path / "blob.bin").write_bytes(b"\0" + str(F13_BLOCK[5]).encode())
    (tmp_path / ".gitignore").write_text("scratch/\n", encoding="utf-8")
    (tmp_path / "scratch").mkdir()
    (tmp_path / "scratch" / "backup.md").write_text(f"ignored {F13_BLOCK[2]}\n", encoding="utf-8")
    _git("add", "x.md", "y.txt", cwd=tmp_path)
    assert _git_hits(tmp_path) == {"x.md"}
    assert _working_hits(tmp_path) == {"x.md", "run.log"}


@pytest.fixture(scope="module")
def fold():
    """The three-way design test's folder and H4's widened evaluator, loaded from their files, never copied."""
    folder = _load(THREE_WAY_TEST, "three_way_design_folder_for_f13")._Folder
    widened = _load(H4_TEST, "h4_draft_widened_for_f13")._Widened
    targets = {_PREFIX, _PREFIX * 10, *F13_BLOCK}

    def hits(source: str) -> list[int]:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tree = ast.parse(source)
        except SyntaxError:
            return []
        f, w = folder(targets), widened(targets)
        f.visit(tree)
        w.visit(tree)
        return sorted(set(f.lines) | set(w.lines))

    return hits


def test_the_fold_finds_the_construction_only_where_declared(fold) -> None:
    found = set()
    for f in _git("ls-files", "*.py").stdout.splitlines():
        p = ROOT / f
        if p.is_file() and VENDOR_DATA not in p.parents and fold(p.read_text("utf-8", errors="replace")):
            found.add(f)
    if _git("ls-files", THIS).stdout.strip():
        assert THIS in found, "the fold must find this file's own construction of the block (positive control)"
    assert found <= set(DERIVED_USES), f"the block is built by arithmetic outside its declared uses: {found}"


@pytest.mark.parametrize("src", [
    "P = 2026 * 1000 + 451\nS = P * 10 + 3\n",
    'S = int("2026451" + "3")\n',
    'S = int(f"{2026451}3")\n',
    "S = sum([20264000, 513])\n",
])
def test_the_fold_sees_a_planted_construction(fold, src: str) -> None:
    assert fold(src), src


def test_the_fold_ignores_a_near_miss(fold) -> None:
    assert fold("Q = 2026 * 1000 + 452\nR = int('2026452' + '3')\nT = 'P = 2026 * 1000 + 451'\n") == []


# --------------------------------------------------------------------------------------------- no held-out read


def test_no_held_out_read(text: str) -> None:
    from extended import reader as R

    assert R.declared_purposes(text) == frozenset(), "a design search names no held-out purpose"
    assert not re.search(r"^- \*\*Judged-block reads:\*\*", text, re.M)
    body = _unfenced(text)
    for sent in re.split(r"(?<=\.)\s+(?=[A-Z*(`])", _flat(body)):
        for d in re.findall(r"\b\d{4}-\d{2}-\d{2}\b", sent):
            if d >= RECORD_DATES_FROM or d <= SEARCH_LAST:
                continue
            assert d in (HELD_FIRST, HELD_LAST, CONFIRM), f"a date after the search years that is no declared bound: {d}"
            assert UNREAD.search(sent), sent[:200]
    for line in body.splitlines():
        if CONFIRM in line:
            assert re.search(r"confirmation|refused|heldout-window", line), line
    assert "Nothing of this search reads the held-out years." in _flat(text)


# ------------------------------------------------------------------------------- the placeholders until Q-189


def test_the_w42_placeholders_stand_until_w42r1_is_applied(text: str) -> None:
    head = _flat(text[:text.index("\n## 0. ")])
    assert "**Awaiting W42-R2's application (Q-189), and what else stands before the pin.**" in head
    rows = _rows(_section(text, 7))
    for name, key in W42_ROWS.items():
        hit = [r for r in rows if r[0].startswith(name)]
        assert len(hit) == 1, name
        assert "<...>" in hit[0][1] and AWAIT in hit[0][1], f"{name}: its value is W42-R2's, left blank until Q-189"
        assert key in head, f"{key}: the head's list names the output key"
    s = _spec(text)
    assert s["objective"]["values_row"].startswith("<...>") and "Q-189" in s["objective"]["values_row"]
    assert str(s["no_harm"]["margin"]).startswith("<...>") and str(s["no_harm"]["margin_row"]).startswith("<...>")
    assert "<...> (**the H3-D placeholder**, awaiting H3-D's declaration" in _flat(_section(text, 9))


def test_the_lint_is_clean_and_its_pin_errors_are_the_placeholders(text: str) -> None:
    r = subprocess.run([sys.executable, str(LINT), str(DRAFT), "--pin"], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600)
    assert r.returncode == 1, r.stdout + r.stderr
    out = r.stdout.splitlines()
    end = next((i for i, ln in enumerate(out) if ln.startswith("warnings")), len(out))
    errs = [ln for ln in out[:end] if re.match(r"\s*\d+\. ", ln)]
    lines = text.splitlines()
    assert errs, "the pin-mode lint finds the placeholders"
    master_log = _git("show", "master:DECISIONS.md", check=False).stdout
    pending = {r for r in PENDING_ROWS if not re.search(rf"^\| {r} \|", master_log, re.M)}
    errs = [e for e in errs if not any(f"[xref.row] {r} is not a row" in e for r in pending)]
    for e in errs:
        m = re.search(r":(\d+): \[(form\.placeholder|form\.phrase)\] ", e)
        assert m, f"a pin-mode error that is not a placeholder: {e}"
        ln = lines[int(m.group(1)) - 1]
        assert "<...>" in ln or "F-XX" in ln, e
    flagged = {int(re.search(r":(\d+): ", e).group(1)) for e in errs}
    sec7 = [i + 1 for i, ln in enumerate(lines) if AWAIT in ln and ln.startswith("|")]
    assert set(sec7) <= flagged and len(sec7) == len(W42_ROWS)
    plain = subprocess.run([sys.executable, str(LINT), str(DRAFT)], cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=600)
    master_log = _git("show", "master:DECISIONS.md", check=False).stdout
    pending = {r for r in PENDING_ROWS if not re.search(rf"^\| {r} \|", master_log, re.M)}
    out = plain.stdout.splitlines()
    end = next((i for i, ln in enumerate(out) if ln.startswith("warnings")), len(out))
    errs = [ln for ln in out[:end] if re.match(r"\s*\d+\. ", ln)]
    other = [e for e in errs if not any(f"[xref.row] {r} is not a row" in e for r in pending)]
    assert not other, plain.stdout + plain.stderr
    assert plain.returncode == (1 if errs else 0), plain.stdout


def test_the_screen_and_the_deciding_size_are_declared(text: str) -> None:
    """The lead's addition on Q-214: the early rounds' seeds and start stride, the promotion and the precision each size
    gives, fixed before any read."""
    s = _spec(text)
    sc = s["screen"]
    sel, rer, scr = set(s["protocol"]["seeds"]), set(s["finalists"]["reread_seeds"]), set(sc["seeds"])
    assert sc["seeds"] == [80, 81, 82, 83], "the screen's own indices (B-3)"
    assert not (scr & sel) and not (scr & rer) and not (sel & rer), "the three index ranges are disjoint (B-3)"
    assert sc["start_stride"] == 4 and sc["start_offset"] == 0 and sc["promote"] == 32
    assert sc["roles"] == ["survey"] + [f"round-{i}" for i in range(1, 5)]
    assert s["rounds"]["count"] == 8 and s["rounds"]["batch"] >= sc["promote"]
    sec = _flat(_section(text, 6))
    for x in ("**the screen size**, for the survey and rounds 1 to 4", "**every 4th start**",
              "**the deciding size**, for rounds 5 to 8", "**the promotion**, between round 4 and round 5",
              "**the finalist candidates are ranked only among deciding-size readings**",
              "MDE(n) = (z_0.95 + z_power) sigma / sqrt(n)",
              "**the screen's MDE is four times the deciding size's**", "**a build requirement** (the head's item 3):"):
        assert x in sec, x
    # the stated ratio is the arithmetic of the declared sizes: sqrt((16 seeds x every start) / (4 seeds x a quarter))
    full, scr = len(s["protocol"]["seeds"]) * 1.0, len(sc["seeds"]) / sc["start_stride"]
    assert (full / scr) ** 0.5 == 4.0
    assert "never a screen reading, section 6" in _flat(_section(text, 7))
    assert "the promotion: 32 screened cells re-read at the deciding size" in _flat(_section(text, 13))


# ------------------------------------------------------------------- text 2: the two reads' findings, each a test


#: the words a unit that names W42-R1 must carry beside it: W42-R2 is the rule, W42-R1 only its parent (E-296)
W42R1_BESIDE = ("W42-R2", "carried", "never applied", "parent")
W42R1_LIMITS = ("not_paid_within_B", "peak_oop_12_months_p90", "first_payout_days_p50", "orders_max_p90",
                "accounts_max_p90", "taken_mean_p10")
NEWS_CALENDARS = ("vendor/stage2/data/release_days_0830_2009_2025.csv",
                  "vendor/stage2/config/sources/fomc_statements_2020_2024q1.csv")
SEARCH_YEARS = {"2020", "2021", "2022", "2023"}
NEEDED_DECIDING = ("extended/design_trades.py", "extended/three_way_runner.py", "extended/three_way_stats.py",
                   "extended/three_way_s1.py", "extended/features.py", "extended/s1_range.py", "extended/t7_forecast.py",
                   "extended/family_stats.py", "extended/h4_coin_source.py", "extended/wave42_r2.py",
                   "scripts/wave42_r2_apply.py", "identity/h4_registered_constants.py",
                   "config/calendar_fomc_minutes.csv")


def _units(t: str) -> list[str]:
    """The text's units -- list items, table rows, paragraphs -- each flattened (fences out)."""
    parts = re.split(r"\n(?=\s*(?:- |\| |\d+\. |#))|\n\n", _unfenced(t))
    return [_flat(u) for u in parts if u.strip()]


def _head(t: str) -> str:
    return _flat(t[:t.index("\n## 0. ")])


def test_b1_w42r2_is_the_rule_everywhere(text: str) -> None:
    from extended import wave42 as W

    for u in _units(text):
        if "W42-R1" in u:
            assert any(k in u for k in W42R1_BESIDE), f"W42-R1 named as the rule: {u[:160]}"
    assert tuple(lim.name for lim in W.LIMITS) == W42R1_LIMITS, "W42-R1's six limits, which W42-R2 carries"
    lim = next(r for r in _rows(_section(text, 7)) if r[0].startswith("**the limits**"))[1]
    for n in W42R1_LIMITS + ("net_month_12_p50",):
        assert f"`{n}`" in lim, n
    assert "The seven are W42-R2's (`wave42_r2.LIMITS`)" in lim
    r2 = _git("show", "wt/wt-w42r2:extended/wave42_r2.py", check=False)
    if r2.returncode == 0:                                       # W42-R2's own text, where its branch is present
        assert 'LimitSpec("net_month_12_p50", "(12)", NET12_KEY, "floor", YEAR, "p50"' in r2.stdout
    assert "one for each of W42-R2's seven limits" in _flat(_section(text, 6))
    assert "the seven limit measures" in _spec(text)["protocol"]["sha256"]
    head = _head(text)
    for x in ("`extended/wave42_r2.py`", "`scripts/wave42_r2_apply.py`", "`results/w42_r2_values.csv`",
              "`config/w42_r2_pin.json`", "**W42-R2 merged and pinned**"):
        assert x in head, x
    assert ("`limit_estimate`, `limit_check` and `limit_per_seed_sd` imported from it, never from `extended.wave42`"
            in head), "the limits' scoring is W42-R2's (the Q-221 worker's report)"
    assert "wt/wt-w42r2 at `db3cc27`" in head and "sd\\*, the largest per-seed sd of the four baselines" in head
    tip = _git("show", "db3cc27:extended/wave42_r2.py", check=False)
    if tip.returncode == 0:                                      # the cited commit holds the three functions
        for fn in ("limit_estimate", "limit_check", "limit_per_seed_sd"):
            assert re.search(rf"^def {fn}\(", tip.stdout, re.M), fn
    assert ("so M-5 (c)'s \"a corrected rule ... whose searches never enter this F-HT\" does not reach this search, "
            "whose membership is unaffected") in _flat(_section(text, 9))


def test_b2_the_keep_rule_is_the_point_estimate_and_the_gate_models_the_pipeline(text: str) -> None:
    order = _flat(next(r for r in _rows(_section(text, 7)) if r[0].startswith("the **finalist order rule**"))[1])
    assert "**kept only if its re-read point estimate beats each baseline on the composite**" in order
    assert "printed beside and never deciding; the held-out test, not the search, bounds coin luck" in order
    assert "by more than delta\\* at the t threshold" not in order
    gate = _flat(_section(text, 9))
    assert "**The gate simulates the whole selection pipeline**" in gate
    for stage in ("the screen at its size with its floors", "the promotion", "the deciding size", "the top-4 cut",
                  "the point-estimate keep rule", "the plateau", "and then the held-out pass line"):
        assert stage in gate, stage
    assert "**the power reported is that whole pipeline's**" in gate and "on the same route" in gate
    assert "**The keep rule's power**" in _flat(_section(text, 6))


def test_b4_the_early_look_is_disclosed_dated_and_counted(text: str) -> None:
    from datetime import datetime

    assert "Q-213's exploratory early look" in _flat(_section(text, 1))
    s2 = _flat(_section(text, 2))
    assert "**The search-year reads before the pin**" in s2 and "| the lead and the operator |" in s2
    s16 = _section(text, 16)
    labelled = [r for r in _rows(s16) if r[-1].startswith("**yes")]
    for x in ("T1 narrowed", "the no-harm margin", "the screen", "`net_month_12_p50`", "this text 2's fixes"):
        assert any(x in r[0] for r in labelled), x
    man = json.loads((ROOT / "results" / "early_look_rl3_pd_fade.csv.manifest.json").read_text(encoding="utf-8"))
    assert man["exploratory"] is True and man["timestamp"][:19] in _flat(s16)
    side_rule = datetime.fromisoformat(_git("log", "-1", "--format=%cI", "457f577").stdout.strip())
    assert side_rule < datetime.fromisoformat(man["timestamp"]), "the `fade` rule was fixed before the look"
    assert "commit `457f577` (2026-11-20)" in _flat(s16)
    assert "**beside the count, the early look's one cell**" in _flat(_section(text, 13))


def test_b5_s1_is_searched_in_every_run(text: str) -> None:
    row = next(r for r in _rows(_section(text, 3)) if r[0] == "S1")[4]
    assert "**searched in every run**" in row and "never falling back to `NotComputed`" in row
    assert "computed with S1 active" in row and "carried as refused" not in row
    assert re.search(r"raw sha256 `[0-9a-f]{64}`", row)
    assert "results/s1_range.csv" in _spec(text)["parts"]["space"]["data"]
    assert "**S1's file in clean runs** (E-297 (3))" in _head(text)


def test_b6_the_major_news_list_is_declared_and_its_calendars_cover_the_search_years(text: str) -> None:
    row = _flat(next(r for r in _rows(_section(text, 4)) if r[0].startswith("**conduct tier 1**"))[1])
    assert "**the declared reading of \"a scheduled major news event\"**" in row
    cited = tuple(re.findall(r"`(vendor/stage2/[^`]+\.csv)`", row))
    assert cited == NEWS_CALENDARS, cited
    for p in cited:
        assert _git("ls-files", p).stdout.strip() == p, f"{p} is a tracked file"
        days = [ln.split(",")[0] for ln in (ROOT / p).read_text(encoding="utf-8").splitlines()
                if re.match(r"\d{4}-\d{2}-\d{2},", ln)]
        assert SEARCH_YEARS <= {d[:4] for d in days}, f"{p} covers every search year"
    assert "BEA's GDP releases, whose calendar exists in neither this repository nor the vendored tree" in row
    assert "a refusing count on the taken-trade log" in row and "built with a planted violation that fails it" in row
    assert "**no verified news window reaches Topstep's accounts**" in _flat(_section(text, 4))


def test_the_deciding_files_cover_the_import_closure(text: str) -> None:
    from extended import reader as R, survey as SV

    files = set(R._deciding_files(text))
    for f in sorted(files):
        if f.startswith("extended/") and f.endswith(".py") and (ROOT / f).is_file() and not f.endswith("__init__.py"):
            for src in SV.closure_files(f[:-3].replace("/", ".")).values():
                rel = Path(src).resolve().relative_to(ROOT.resolve()).as_posix()
                assert rel in files, f"{f} imports {rel}, which the deciding-files line omits"
    for need in NEEDED_DECIDING:
        assert need in files, need


def test_the_ledger_carries_h4s_rows_and_every_read_ledger_ref(text: str) -> None:
    s2 = _flat(_section(text, 2))
    for x in ("the busiest-day capacity", "the bar store manifest's held-out metadata",
              "the registered-constants run itself", "U1's `EXACT` horizons"):
        assert x in s2, x
    refs = set()
    for ln in (ROOT / "results" / "read_ledger.jsonl").read_text(encoding="utf-8").splitlines():
        if ln.strip():
            refs.add(json.loads(ln)["declaration"].get("ref"))
    refs.discard(None)
    assert refs, "the read ledger's rows (a scan that can find nothing is no check)"
    for r in sorted(refs):
        assert r in s2, f"the read ledger's {r} has no row in section 2"
    assert "F-01 (withdrawn, E-007) and F-03 (closed with its judged block not read, E-192)" in _flat(_section(text, 13))


def test_the_sizes_are_final_in_the_file(text: str) -> None:
    f, s6 = _flat(text), _flat(_section(text, 6))
    assert "**They are sized from compute cost only, never from any reading of an outcome.**" in s6
    assert "**The sizes never move after the hash:**" in s6 and "the survey's wall-clock T = c U / w" in s6
    for gone in ("the lead sizes them in the pinning row", "the values below are the drafted ones"):
        assert gone not in f, gone


def test_the_stress_arms_are_defined_and_built_before_the_pin(text: str) -> None:
    from extended import three_way_journey as J

    s10 = _flat(_section(text, 10))
    assert "`three_way_journey.ArmSpec(worse_ticks=1)` and `ArmSpec(missed_q=0.10)`" in s10
    assert "**their code is built, reviewed and merged before the pin**" in s10
    assert "built after the pin" not in _flat(text)
    J.ArmSpec(worse_ticks=1), J.ArmSpec(missed_q=0.10)
    src = (ROOT / "scripts" / "h4_rebaseline.py").read_text(encoding="utf-8")
    assert "J.ArmSpec(worse_ticks=1)" in src and "J.ArmSpec(missed_q=0.10)" in src


def test_k_max_is_the_loaded_spaces(text: str) -> None:
    """The plateau's largest neighbourhood, recomputed from the space (S1's slot dimension added where this tree lacks
    its git-ignored file), at the narrowed sources."""
    from extended import lever_space as LS, search_space as SS

    sources = {"evening": ("p14",), "asia": ("p14",), "london": ("p14",), "ny_am": ("p14", "rl3"), "ny_pm": ("p14",)}
    sp = SS.from_lever_space(slots={k: 1 for k in sources})
    total, has_s1 = 0, set()
    for d in sp.dims:
        slot = d.name.split(".")[0] if "." in d.name else None
        part = d.name.rsplit(".", 1)[-1]
        if slot is None:
            total += 2 if d.kind != SS.CAT else len(d.values) - 1
        elif part == "on":
            total += len(d.values) - 1
        elif part == "T1":
            total += len(sources[slot]) - 1
        elif part in ("T4", "T5"):
            key = f"{slot}.0.T1"
            total += max(len(d.cells({key: src})) for src in sources[slot]) - 1
        else:
            total += 2
            if part == "S1":
                has_s1.add(slot)
    total += 2 * len(set(sources) - has_s1)                      # S1 where `results/s1_range.csv` is absent
    assert "S1" in LS.LEVERS and total == 85, total
    assert "**k_max = 85**" in _flat(_section(text, 7)) and "4 x 85 = 340" in _flat(_section(text, 13))
    assert "768 + 4 + 340 = 1112" in _flat(_section(text, 13))


def test_the_minors_of_both_reads(text: str) -> None:
    f, s = _flat(text), _spec(text)
    assert s["parts"]["runner"]["params"]["coin_role"] == "survey_topstep_coins" and "f_xx" not in text
    s12 = _flat(_section(text, 12))
    assert "`S1`: the search-year coin role (not the stop-width lever S1)" in s12 and "one role, the pairing" in s12
    assert "`S4`: proposed for the held-out test's coin field, which F-HT owns" in s12
    assert "S1's seeds" not in f and "S1's selection seeds" not in f
    assert "**c_u**, the design note's 2.2 (a) item 4" in _flat(_section(text, 8))
    assert "the vendored engine's reading" in next(r for r in _rows(_section(text, 3)) if r[0] == "A9")[4]
    s6 = _flat(_section(text, 6))
    for x in ("`kappa`, the lower confidence bound's width", "`p_feasible`, its feasibility threshold", "(`centres`)",
              "(`local`,", "**The protocol's horizon is 0 sessions**",
              "**A departure from CHARTER 3.3 (d)'s \"constrained, multi-objective\" form, stated**",
              "**each design is read at the screen size**", "**Its edge cases:** fewer than 32 passers promote every",
              "**are applied on the deciding-size reading before ranking**",
              "`survey._keep`", "`survey.finalist_candidates`", "`survey.run_rounds`", "`survey.read_design`"):
        assert x in s6, x
    s11 = _flat(_section(text, 11))
    for x in ("**E-294 (4)'s reporting, deciding nothing:**", "**contract-only**", "**execution-fit block**",
              "**edge-sensitivity reading**"):
        assert x in s11, x
    assert "**the schedule builder reads `day_calendar.day_context` for designs and baselines alike**" in _flat(
        _section(text, 4))
    assert "the plateau's power against a spike of twice delta\\* at these 64 indices" in _flat(_section(text, 7))
    assert "H4 read only through W42-R2's output" in _flat(_section(text, 9))
    assert "**the H3-D placeholder**" in _head(text)
    for gone in ("the lead's ruling, Q-214", "the lead's ruling on Q-214", "on this text's first read (Q-214)"):
        assert gone not in f, gone


RL3_DRAFT = ROOT / "prereg" / "DRAFT_F-RL3_resting_levels.md"


def test_q215_the_routes_three_declarations_and_t1s_narrowing(text: str) -> None:
    """Q-215's real-bar route cannot choose these: S1's whole-tick rule, RL3's level kind and cutoff, T7 at `off`; and
    the space's T1 narrowed to the declared triggers."""
    from extended import triggers as T, vol_descriptive as VD

    s1 = next(r for r in _rows(_section(text, 3)) if r[0] == "S1")[4]
    assert "rounded half up to whole ticks, at least one, by `vol_descriptive.band_ticks`" in s1
    assert "the caps are checked on the unrounded k x T(d)" in s1
    assert VD.band_ticks(1.0, 1.0) >= 1                          # the cited rule exists and rounds to whole ticks
    t7 = next(r for r in _rows(_section(text, 3)) if r[0] == "T7")
    assert t7[3].startswith("searched in the table, **held at `off` in this search**") and "`off` only" in t7[4]
    sp = _spec(text)
    assert sp["parts"]["space"]["params"]["held"] == {"T7": "off"}
    src = sp["parts"]["space"]["params"]["sources"]
    assert set(x for v in src.values() for x in v) == {"p14", "rl3"} and src["ny_am"] == ["p14", "rl3"]
    rl3 = sp["parts"]["runner"]["params"]["source_params"]["rl3"]
    assert rl3 == {"kind": "pd", "cutoff_ct": "14:30"}
    assert rl3["kind"] in T.RL3_KINDS and rl3["kind"] == T.RL3_KINDS[0], "RL3's draft lists `pd` first"
    hh, mm = (int(x) for x in rl3["cutoff_ct"].split(":"))
    from extended import walker as W
    assert W.slot(hh, mm) == max(T.RL3_CUTOFFS), "14:30 CT, the latest declared cutoff"
    row = _flat(_section(text, 4))
    assert "**its level kind `pd` (the prior regular session's high and low) and its cutoff 14:30 CT, fixed, not searched**" in row
    sha = hashlib.sha256(_lf(RL3_DRAFT).encode("utf-8")).hexdigest()
    assert f"LF sha256 `{sha}`" in row, "RL3's draft cited at its own hash"
    head = _head(text)
    assert "the route refuses `coin` and `p16` by name (`trigger_sides.NO_SIDE`)" in head
    assert "`extended/survey_route.py` (wt/wt-survey `d64aced`" in head


def test_q215_red_team_s2_onto_r_and_refused_points(text: str) -> None:
    """BUILD_Q215_ROUTE B-1 and m-3: one rule for S2 onto the engine's R, and a refused route point never scored."""
    s2 = next(r for r in _rows(_section(text, 3)) if r[0] == "S2")[4]
    assert "**one rule for S2 onto the engine's R**" in s2
    assert "each trade is read only at its own component's w" in s2 and "outcomes at every other w" in s2 and "masked" in s2
    assert "the runner refuses a taken trade whose R differs from its own w" in s2
    gates = _flat(_section(text, 6))
    assert "**A point the route refuses**" in gates and "**is recorded as a refused cell with its reason and never scored**" in gates
    assert "it is never given an infeasible reading" in gates
    t7 = next(r for r in _rows(_section(text, 3)) if r[0] == "T7")
    assert "**held at `off` in this search**" in t7[3]
