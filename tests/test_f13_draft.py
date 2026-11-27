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
AWAIT = "awaiting W42-R1's application, Q-189"
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
TO_BUILD = ("extended/survey_parts.py",)
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
        assert f in files and f"`{f}` is new: it is written by this search's build, before the pin" in _flat(text)
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
    assert s["objective"]["rule_id"] == SV.W42_RULE
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
    assert "**Awaiting W42-R1's application (Q-189), and what else stands before the pin.**" in head
    rows = _rows(_section(text, 7))
    for name, key in W42_ROWS.items():
        hit = [r for r in rows if r[0].startswith(name)]
        assert len(hit) == 1, name
        assert "<...>" in hit[0][1] and AWAIT in hit[0][1], f"{name}: its value is W42-R1's, left blank until Q-189"
        assert key in head, f"{key}: the head's list names the output key"
    s = _spec(text)
    assert s["objective"]["values_row"].startswith("<...>") and "Q-189" in s["objective"]["values_row"]
    assert str(s["no_harm"]["margin"]).startswith("<...>") and str(s["no_harm"]["margin_row"]).startswith("<...>")
    assert "<...> (awaiting H3-D's declaration" in _flat(_section(text, 9))


def test_the_lint_is_clean_and_its_pin_errors_are_the_placeholders(text: str) -> None:
    r = subprocess.run([sys.executable, str(LINT), str(DRAFT), "--pin"], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600)
    assert r.returncode == 1, r.stdout + r.stderr
    out = r.stdout.splitlines()
    end = next((i for i, ln in enumerate(out) if ln.startswith("warnings")), len(out))
    errs = [ln for ln in out[:end] if re.match(r"\s*\d+\. ", ln)]
    lines = text.splitlines()
    assert errs, "the pin-mode lint finds the placeholders"
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
    assert plain.returncode == 0, plain.stdout + plain.stderr


def test_the_screen_and_the_deciding_size_are_declared(text: str) -> None:
    """The lead's addition on Q-214: the early rounds' seeds and start stride, the promotion and the precision each size
    gives, fixed before any read."""
    s = _spec(text)
    sc = s["screen"]
    assert sc["seeds"] == [0, 1, 2, 3] and set(sc["seeds"]) < set(s["protocol"]["seeds"])
    assert sc["start_stride"] == 4 and sc["start_offset"] == 0 and sc["promote"] == 32
    assert sc["roles"] == ["survey"] + [f"round-{i}" for i in range(1, 5)]
    assert s["rounds"]["count"] == 8 and s["rounds"]["batch"] >= sc["promote"]
    sec = _flat(_section(text, 6))
    for x in ("**the screen size**, for the survey and rounds 1 to 4", "**every 4th start**",
              "**the deciding size**, for rounds 5 to 8", "**the promotion**, between round 4 and round 5",
              "**the finalist candidates are ranked only among deciding-size readings**",
              "MDE(n) = (z_0.95 + z_power) sigma / sqrt(n)",
              "**the screen's MDE is four times the deciding size's**", "**a build requirement:**"):
        assert x in sec, x
    # the stated ratio is the arithmetic of the declared sizes: sqrt((16 seeds x every start) / (4 seeds x a quarter))
    full, scr = len(s["protocol"]["seeds"]) * 1.0, len(sc["seeds"]) / sc["start_stride"]
    assert (full / scr) ** 0.5 == 4.0
    assert "never a screen reading, section 6" in _flat(_section(text, 7))
    assert "the promotion: 32 screened cells re-read at the deciding size" in _flat(_section(text, 13))
