"""Q-210: the declaration lint (`scripts/decl_lint.py`), on synthetic repositories and on the record.

- **each check, failing and passing** -- on a throwaway git repository holding a synthetic decision log, template,
  seed guard, code and cited files: (1) the pin-time form, (2) template sections and their topics, items and pins,
  decision rows, commits, paths and LF sha256s, (3) counts as a product and a number, (4) seeds against a guard's own
  constants (and the lint following the guard when its `DECLARED_USES` changes: nothing copied), (5) the token
  grammar and position, (6) held-out and confirmation dates, (7) typed figures as warnings only;
- **the command** -- exit 0 clean (warnings printed), 1 with a numbered `path:line: [rule]` list, 2 when it cannot run;
- **a mutation per check, killed** -- each mutant of the lint lets that check's failing case through;
- **the record** -- every pinned declaration on master gives exactly its listed findings (each a real defect, named in
  Q-210's hand-back), and H3 at wt/wt-three f454d8d is flagged for the gatekeeper's refusal items 1 and 3 at the lines
  the gatekeeper names (skipped when this clone lacks the commits).

No bar, no result file, no engine; the synthetic repositories are temporary folders. The synthetic seed block is built
by arithmetic, so this file holds no literal of it.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "decl_lint.py"
_spec = importlib.util.spec_from_file_location("s2x_decl_lint", SCRIPT)
L = importlib.util.module_from_spec(_spec)
sys.modules["s2x_decl_lint"] = L
_spec.loader.exec_module(L)

#: a synthetic block, built by arithmetic (no literal of it in this file); unused anywhere in the repository
_P = 2026 * 1000 + 999
BLOCK = tuple(_P * 10 + i for i in range(10))
S0, S1 = BLOCK[0], BLOCK[1]
CONFIRM = "2026-07-17"

TEMPLATE = """# TEMPLATE: a design search's declaration -- copy it, never pin it

**Text v3 (2026-11-21).** The synthetic template.

**Declaration kind: design search.**

## 4. The schedule

- the flatten books at the window's start (R-10's walk).

## 5. The zero-edge convention

- **R-10: the redraw for a trade that ends at a time limit**, declared here.

## 7. The pinning row: every input of 3.8 and 3.9, in one row, before the survey

- the composite, its caps.

## 13. The count

1. One k per held-out test.
2. Every design tried is counted.

## 16. Anything chosen after seeing results
"""

DECISIONS = """# Decision log

| id | date | decision | basis |
|---|---|---|---|
| E-001 | 2026-11-15 | **The charter.** | the operator |
| E-010 | 2026-11-16 | **A row.** | the lead |
"""

GUARD = """from pathlib import Path
import nonexistent_module_never_imported  # the lint reads constants; it never imports a guard
ROOT = Path(__file__).resolve().parent.parent
_P = 2026 * 1000 + 999
SEED_BLOCK = tuple(_P * 10 + i for i in range(10))
DECLARED_USES: tuple[str, ...] = ({uses})
NOTE = ROOT / "docs" / "note.md"
"""


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)
    return r.stdout.strip()


def _commit(repo: Path, msg: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "commit", "-q",
         "--no-verify", "-m", msg)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture(scope="module")
def base_repo(tmp_path_factory) -> Path:
    """A synthetic repository: decision log, template, seed guard (allowing one declaration and one code file), a
    cited note and code; one commit on master, one on a side branch. Built once; each test works on a copy."""
    r = tmp_path_factory.mktemp("decl_lint") / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "master")
    (r / "prereg").mkdir()
    (r / "tests").mkdir()
    (r / "extended").mkdir()
    (r / "docs").mkdir()
    (r / "DECISIONS.md").write_text(DECISIONS, encoding="utf-8")
    (r / "prereg" / "TEMPLATE_design_search.md").write_text(TEMPLATE, encoding="utf-8")
    (r / "tests" / "test_guard.py").write_text(
        GUARD.format(uses='"prereg/F-20_mine.md", "extended/uses.py"'), encoding="utf-8")
    (r / "extended" / "uses.py").write_text(f"SEED = {S0}\n", encoding="utf-8")
    (r / "extended" / "stray.py").write_text(f"SEED = {S1}\n", encoding="utf-8")
    (r / "docs" / "note.md").write_text("A cited note.\n", encoding="utf-8")
    _commit(r, "base")
    _git(r, "checkout", "-q", "-b", "side")
    (r / "docs" / "side.md").write_text("side\n", encoding="utf-8")
    _commit(r, "side")
    _git(r, "checkout", "-q", "master")
    return r


@pytest.fixture()
def repo(base_repo: Path, tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    shutil.copytree(base_repo, r)
    return r


def run(repo: Path, body: str, name: str = "F-20_mine.md", **kw) -> list:
    p = repo / "prereg" / name
    p.write_text(body, encoding="utf-8")
    return L.lint(p, repo=repo, **kw)


def rules(found, severity: str | None = None) -> set[str]:
    return {p.rule for p in found if severity is None or p.severity == severity}


def errs(found) -> set[tuple[int, str]]:
    return {(p.line, p.rule) for p in found if p.severity == L.ERROR}


CLEAN = """# F-20: a synthetic declaration, declared

It is fixed by the sha256 of its LF text in its decision row (E-010).

## 0. In plain words

Nothing.
"""


# ------------------------------------------------------------------------------------------------ 1. pin-time form

def test_form_a_clean_pinned_text_passes(repo):
    assert errs(run(repo, CLEAN)) == set()


@pytest.mark.parametrize("line, rule", [
    ("**Status: a draft, third text, for the red team's re-read.**", "form.head"),
    ("**Status: declared, not pinned.**", "form.head"),
    ("It will be pinned by the lead after the read.", "form.phrase"),
    ("It is pinned only after the red team's read.", "form.phrase"),
    ("It is pinned (by the sha256 of its LF text, in the lead's row) only after the red team's read.", "form.phrase"),
    ("The program family number k = ?, assigned at the pin.", "form.phrase"),
    ("The level: TBD.", "form.phrase"),
    ("| k | ? |", "form.phrase"),
    ("The id F-XX is the gatekeeper's.", "form.placeholder"),
    ("<What the search looks for, for which firm>", "form.placeholder"),
])
def test_form_a_draft_form_fails_in_a_pin_named_file(repo, line, rule):
    body = CLEAN.replace("It is fixed", line + "\n\nIt is fixed")
    assert rule in rules(run(repo, body), L.ERROR)


def test_form_a_pinning_sentence_wrapped_over_two_lines_fails(repo):
    body = CLEAN.replace("It is fixed", "It reads no session. It is pinned (by the sha256 of its LF text, in the\n"
                                        "lead's row) only after the red team's read.\n\nIt is fixed")
    assert (3, "form.phrase") in errs(run(repo, body))


def test_form_draft_names_are_not_held_to_pin_form_unless_asked(repo):
    body = CLEAN.replace("It is fixed", "**Status: a draft.**\n\nIt is fixed")
    assert "form.head" not in rules(run(repo, body, name="DRAFT_F-20_mine.md"))
    assert "form.head" in rules(run(repo, body, name="DRAFT_F-20_mine.md", pin=True))


def test_form_a_quoted_word_list_is_not_the_status(repo):
    body = CLEAN.replace("It is fixed", 'The refused words: "DRAFT", "this draft", "Not pinned".\n\nIt is fixed')
    assert not rules(run(repo, body)) & {"form.head", "form.phrase"}


# ------------------------------------------------------------------------------------------------ 2. cross-references

def test_xref_template_section_topic(repo):
    bad = CLEAN + "\n- R-10's walk is governed by template v3's section 7.\n"
    good = CLEAN + "\n- R-10's walk is governed by template v3's section 5.\n"
    assert (L_line(bad, "governed"), "xref.template-topic") in errs(run(repo, bad))
    assert "xref.template-topic" not in rules(run(repo, good))


def L_line(body: str, needle: str) -> int:
    return next(i for i, line in enumerate(body.split("\n"), 1) if needle in line)


def test_xref_template_section_and_item_exist(repo):
    assert "xref.template-section" in rules(run(repo, CLEAN + "\nAs the design-search template's section 9 says.\n"))
    assert "xref.template-item" in rules(run(repo, CLEAN + "\nThe design-search template (section 13 item 4).\n"))
    assert not rules(run(repo, CLEAN + "\nThe design-search template (section 13 item 2).\n")) & {
        "xref.template-item", "xref.template-section"}


def test_xref_a_quoted_heading_must_be_the_sections(repo):
    bad = CLEAN + "\nThe design-search template's section 5, \"The pinning row\".\n"
    good = CLEAN + "\nThe design-search template's section 5, \"The zero-edge convention\".\n"
    assert "xref.template-topic" in rules(run(repo, bad))
    assert "xref.template-topic" not in rules(run(repo, good))


def test_xref_a_template_cited_as_pinned_needs_its_pin_row(repo):
    body = CLEAN + "\n- R-10 is governed by template v3's section 5 as pinned.\n"
    assert "xref.template-unpinned" in rules(run(repo, body))
    sha = hashlib.sha256(TEMPLATE.encode()).hexdigest()
    log = DECISIONS + f"| E-011 | 2026-11-17 | `prereg/TEMPLATE_design_search.md` sha256 `{sha}` | the lead |\n"
    assert "xref.template-unpinned" not in rules(run(repo, body, decisions=log))


def test_xref_rows(repo):
    assert "xref.row" not in rules(run(repo, CLEAN + "\nAs E-001 and E-010 rule.\n"))
    found = run(repo, CLEAN + "\nAs E-999 rules.\n")
    assert any(p.rule == "xref.row" and "E-999" in p.message for p in found)


def test_xref_commits(repo):
    head = _git(repo, "rev-parse", "--short=7", "master")
    side = _git(repo, "rev-parse", "--short=7", "side")
    assert "xref.commit" not in rules(run(repo, CLEAN + f"\nThe build commit `{head}`.\n"))
    assert "xref.commit" in rules(run(repo, CLEAN + "\nThe build commit 1a2b3c4d.\n"), L.ERROR)
    assert "xref.commit" in rules(run(repo, CLEAN + f"\nThe build commit {side}.\n"), L.ERROR)
    # an abbreviation may be all letters (the fast tier drew `ceedcbb` for the side commit): checked where the text
    # calls it a commit, and an all-letter word elsewhere is not read as one
    assert "xref.commit" in rules(run(repo, CLEAN + "\nThe build commit `deadbee`.\n"), L.ERROR)
    assert "xref.commit" not in rules(run(repo, CLEAN + "\nThe wall was defaced again.\n"))
    named = run(repo, CLEAN + f"\nThe text at side `{side}`.\n")
    assert "xref.commit" in rules(named, L.WARNING) and "xref.commit" not in rules(named, L.ERROR)


def test_xref_paths(repo):
    assert "xref.path" not in rules(run(repo, CLEAN + "\nThe note `docs/note.md` and `extended/uses.py`.\n"))
    assert "xref.path" in rules(run(repo, CLEAN + "\nThe note `docs/missing_note.md`.\n"), L.ERROR)
    w = run(repo, CLEAN + "\nWritten to `results/out.csv`.\n")
    assert "xref.path" in rules(w, L.WARNING) and "xref.path" not in rules(w, L.ERROR)


def test_xref_sha256(repo):
    good = hashlib.sha256(b"A cited note.\n").hexdigest()
    assert "xref.sha256" not in rules(run(repo, CLEAN + f"\nThe note `docs/note.md` at LF sha256 `{good}`.\n"))
    bad = "0" * 64
    assert "xref.sha256" in rules(run(repo, CLEAN + f"\nThe note `docs/note.md` at LF sha256 `{bad}`.\n"))
    crlf = (repo / "docs" / "note.md")
    crlf.write_bytes(b"A cited note.\r\n")              # the LF text is hashed, as the pin test reads it
    assert "xref.sha256" not in rules(run(repo, CLEAN + f"\nThe note `docs/note.md` at LF sha256 `{good}`.\n"))


# ------------------------------------------------------------------------------------------------ 3. counts

COUNT = CLEAN + "\n## 8. The cells and the count\n\n- {line}\n"


@pytest.mark.parametrize("line", [
    "The cells: 3 x 4 = 12.",
    "k_cells = 3 x 4 = 12, each counted.",
    "**12 cells** (3 levels x 4 bounds), each counted.",
    "The checks: (classes: a, b, c = 3) x (levels = 4) = 12.",
    "10 x (16 inventory + 4 others) = 200 replays.",
])
def test_counts_a_product_and_its_number_pass(repo, line):
    assert not rules(run(repo, COUNT.format(line=line)), L.ERROR) & {"count.mismatch", "count.no-number",
                                                                     "count.no-product"}


@pytest.mark.parametrize("line, rule", [
    ("The cells: 3 x 4 = 13.", "count.mismatch"),
    ("The checks: (classes: a, b, c = 3) x (levels = 4) = 13.", "count.mismatch"),
    ("The size checks: (classes: a, b, c = 3) x (levels = 3) x R histories, per part.", "count.no-number"),
    ("The power checks: plants P2 to P4 x the grid of sizes, each reported.", "count.no-number"),
    ("The stress: 3 arms x 5 designs, per pair.", "count.no-number"),
    ("k_cells = 12, each counted.", "count.no-product"),
])
def test_counts_fail(repo, line, rule):
    assert rule in rules(run(repo, COUNT.format(line=line)), L.ERROR)


def test_counts_a_formula_outside_the_count_sections_is_not_a_count(repo):
    assert not rules(run(repo, CLEAN + "\nThe bound c_u = w x 2 r / (J x n).\n")) & {"count.no-number"}


# ------------------------------------------------------------------------------------------------ 4. seeds

SEEDS = CLEAN + "\n## 15. Seeds\n\n| seed | role |\n|---|---|\n| {s0} | the coin |\n| {s1} | spare |\n"


def test_seeds_the_declared_use_passes_and_another_file_fails(repo):
    mine = SEEDS.format(s0=S0, s1=S1)
    assert not rules(run(repo, mine), L.ERROR) & {"seed.outside-use", "seed.cited-file"}
    other = CLEAN.replace("F-20", "F-21") + f"\nIt borrows seed {S0}.\n"
    found = run(repo, other, name="F-21_other.md")
    assert "seed.outside-use" in rules(found, L.ERROR)


def test_seeds_a_cited_file_outside_the_declared_uses_fails(repo):
    body = SEEDS.format(s0=S0, s1=S1) + "\nThe code: `extended/uses.py` and `extended/stray.py`.\n"
    found = [p for p in run(repo, body) if p.rule == "seed.cited-file"]
    assert len(found) == 1 and "extended/stray.py" in found[0].message


def test_seeds_the_lint_follows_the_guards_own_constants(repo):
    """Nothing is copied: widening the guard's DECLARED_USES admits the other declaration."""
    other = CLEAN.replace("F-20", "F-21") + f"\nIt borrows seed {S0}.\n"
    assert "seed.outside-use" in rules(run(repo, other, name="F-21_other.md"))
    (repo / "tests" / "test_guard.py").write_text(
        GUARD.format(uses='"prereg/F-20_mine.md", "extended/uses.py", "prereg/F-21_other.md"'), encoding="utf-8")
    assert "seed.outside-use" not in rules(run(repo, other, name="F-21_other.md"))


def test_seeds_guard_constants_are_read_without_import():
    g = L.guard_constants(GUARD.format(uses='"prereg/F-20_mine.md"'), "tests/test_guard.py")
    assert g is not None and g["block"] == set(BLOCK) and g["strict"]
    assert {"prereg/F-20_mine.md", "tests/test_guard.py", "docs/note.md"} <= g["allowed"]
    assert L.guard_constants("SEED_BLOCK = ().__class__.__base__.__subclasses__()\n", "x.py") is None


def test_seeds_an_unguarded_block_is_a_warning(repo):
    (repo / "tests" / "test_guard.py").unlink()
    found = run(repo, SEEDS.format(s0=S0, s1=S1))
    assert "seed.unguarded" in rules(found, L.WARNING) and not rules(found, L.ERROR) & {"seed.outside-use"}


# ------------------------------------------------------------------------------------------------ 5. tokens

@pytest.mark.parametrize("line", [
    "The verdict row: `heldout-verdict: <MARKET> F-NN @ <its LF sha256> -- <text>`.",
    "The go row: its third cell's first text is the token `go: F-NN @ <its LF sha256>`.",
    "The closing row, `heldout-closed: F-NN @ <its LF sha256> -- <cause> -- <text>`.",
    "The finalists' row: `heldout-finalists: F-NN @ <sha> list <sha>`.",
    "A row recording that an identity holds carries `identity-holds: <id>`.",
    "| E-NNN | <YYYY-MM-DD> | heldout-finalists: F-NN @ <sha> list <sha> -- the list | the lead |",
])
def test_tokens_in_grammar_pass(repo, line):
    assert not rules(run(repo, CLEAN + "\n" + line + "\n")) & {"token.grammar", "token.position"}


@pytest.mark.parametrize("line, rule", [
    ("The verdict row: `heldout-verdict: F-NN @ <its LF sha256> -- <text>`.", "token.grammar"),
    ("The go row: `go: F-NN <its LF sha256>`.", "token.grammar"),
    ("The finalists' row: `heldout-finalists: F-NN @ <sha>`.", "token.grammar"),
    ("The closing row, `heldout-closed: F-NN @ <its LF sha256> -- <text>`.", "token.grammar"),
    ("It held: identity-holds: Q-80 @ f7eda0d -- HOLDS.", "token.position"),
])
def test_tokens_fail(repo, line, rule):
    assert rule in rules(run(repo, CLEAN + "\n" + line + "\n"), L.ERROR)


# ------------------------------------------------------------------------------------------------ 6. dates

@pytest.mark.parametrize("line", [
    "- **never read:** the held-out years (2024-01-02 to 2026-07-16).",
    f"- **The confirmation window:** NQ from {CONFIRM}, never read.",
    f"- **The confirmation:** NQ from {CONFIRM}, for a carried design only, a purchase.",
    f"- **No NQ from {CONFIRM}** is on disk or read.",
    "| `payout_min` | verified (2026-10-03) |",
    '| D-02 | "the late block from 2024-01-02 (section 5)" |',
])
def test_dates_refusals_and_calendar_dates_pass(repo, line):
    assert not rules(run(repo, CLEAN + "\n" + line + "\n")) & {"date.heldout", "date.confirmation"}


@pytest.mark.parametrize("line, rule", [
    ("- It reads NQ 2024-01-02 to 2026-07-16 as its late block.", "date.heldout"),
    ("- It reads 2024-01-02 to 2026-07-16; the confirmation window is never read.", "date.heldout"),
    (f"- It reads the bars from {CONFIRM} to 2026-08-01.", "date.confirmation"),
])
def test_dates_fail(repo, line, rule):
    assert rule in rules(run(repo, CLEAN + "\n" + line + "\n"), L.ERROR)


def test_dates_a_judged_block_line_admits_the_held_out_years(repo):
    body = CLEAN + "\n- It reads NQ 2024-01-02 to 2026-07-16 once.\n- **Judged-block reads:** `heldout_test`\n"
    assert "date.heldout" not in rules(run(repo, body))


# ------------------------------------------------------------------------------------------------ 7. typed figures

@pytest.mark.parametrize("line", [
    "The pass rate was its 87 % over the block.",
    "The lift came out at `0.0921` on the block.",
    "The reading gave 0.875 in all.",
])
def test_figures_warn_and_never_fail(repo, line):
    found = run(repo, CLEAN + "\n" + line + "\n")
    assert "figure.typed" in rules(found, L.WARNING) and "figure.typed" not in rules(found, L.ERROR)


@pytest.mark.parametrize("line", [
    "At most 5 % unresolved at 3R (D-212).",
    "The levels 0.05, 0.01 and 0.001.",
    "A 37.5-point stop and a 112.5-point target.",
    "Lucid's $115.50 fee.",
    "The toy's known answer 0.875, held by `test_toy`.",
    "As 10.2's window rule says.",
])
def test_figures_labelled_values_are_not_flagged(repo, line):
    assert "figure.typed" not in rules(run(repo, CLEAN + "\n" + line + "\n"))


# ------------------------------------------------------------------------------------------------ the command

def _cli(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, encoding="utf-8",
                          env=env, timeout=300)


def test_the_command_exit_codes_and_list(repo):
    p = repo / "prereg" / "F-20_mine.md"
    p.write_text(CLEAN + "\nThe pass rate was its 87 % over the block.\n", encoding="utf-8")
    r = _cli(str(p), "--repo", str(repo))
    assert r.returncode == 0, r.stdout + r.stderr                    # a warning alone never fails
    assert "[figure.typed]" in r.stdout
    p.write_text(CLEAN + "\nAs E-999 rules; k = ?\n", encoding="utf-8")
    r = _cli(str(p), "--repo", str(repo))
    assert r.returncode == 1
    lines = [x for x in r.stdout.splitlines() if x.strip()[:1].isdigit()]
    assert lines and lines[0].strip().startswith("1. ") and ":9: [" in lines[0]
    assert _cli(str(repo / "prereg" / "nothing.md"), "--repo", str(repo)).returncode == 2


# ------------------------------------------------------------------------------------------------ mutations

MUTANTS = {
    "form": (lambda mp: (mp.setattr(L, "HEAD_DRAFT", L.re.compile(r"(?!x)x")), mp.setattr(L, "BODY_FORM", ())),
             CLEAN.replace("It is fixed", "**Status: a draft.** It will be pinned.\n\nIt is fixed"), "form.head"),
    "template-topic": (lambda mp: mp.setattr(L.Lint, "_topic", lambda *a, **k: None),
                       CLEAN + "\n- R-10's walk is governed by template v3's section 7.\n", "xref.template-topic"),
    "template-item": (lambda mp: mp.setattr(L, "TEMPLATE_CITE", L.re.compile(r"(?!x)x(?P<tpl>)(?P<num>)(?P<item>)")),
                      CLEAN + "\nThe design-search template (section 13 item 4).\n", "xref.template-item"),
    "rows": (lambda mp: mp.setattr(L, "E_ROW", L.re.compile(r"(?!x)x(\d)")), CLEAN + "\nAs E-999 rules.\n",
             "xref.row"),
    "commits": (lambda mp: mp.setattr(L, "SHA", L.re.compile(r"(?!x)x([0-9a-f])")),
                CLEAN + "\nThe build commit 1a2b3c4d.\n", "xref.commit"),
    "paths": (lambda mp: mp.setattr(L.Lint, "_resolve", lambda self, t: (t, True)),
              CLEAN + "\nThe note `docs/missing_note.md`.\n", "xref.path"),
    "sha256": (lambda mp: mp.setattr(L, "SHA256_CITE", L.re.compile(r"(?!x)x(?P<path>)(?P<mid>)(?P<hex>)")),
               CLEAN + "\nThe note `docs/note.md` at LF sha256 `" + "0" * 64 + "`.\n", "xref.sha256"),
    "counts-product": (lambda mp: mp.setattr(L.Lint, "_products", staticmethod(lambda u: [])),
                       COUNT.format(line="The power checks: plants P2 to P4 x the grid of sizes, each reported."),
                       "count.no-number"),
    "counts-kcells": (lambda mp: mp.setattr(L, "K_CELLS_NUMBER", L.re.compile(r"(?!x)x(\d)")),
                      COUNT.format(line="k_cells = 12, each counted."), "count.no-product"),
    "seeds": (lambda mp: mp.setattr(L, "guard_constants", lambda src, rel: None),
              CLEAN.replace("F-20", "F-21") + f"\nIt borrows seed {S0}.\n", "seed.outside-use"),
    "tokens-grammar": (lambda mp: mp.setattr(L.Lint, "_grammar", staticmethod(lambda kind, stem, row: True)),
                       CLEAN + "\nThe go row: `go: F-NN <its LF sha256>`.\n", "token.grammar"),
    "tokens-position": (lambda mp: mp.setattr(L.IT, "TOKEN_LIKE", L.re.compile(r"(?!x)x")),
                        CLEAN + "\nIt held: identity-holds: Q-80 @ f7eda0d -- HOLDS.\n", "token.position"),
    "dates-heldout": (lambda mp: mp.setattr(L, "HELD_OUT", (L.date(2024, 1, 3), L.date(2026, 7, 15))),
                      CLEAN + "\n- It reads NQ 2024-01-02 to 2026-07-16 as its late block.\n", "date.heldout"),
    "dates-confirmation": (lambda mp: mp.setattr(L, "CONFIRMATION", L.date(2026, 7, 18)),
                           CLEAN + f"\n- It reads the bars from {CONFIRM}.\n", "date.confirmation"),
    "figures": (lambda mp: mp.setattr(L, "FIGURE_LABEL", L.re.compile(r"")),
                CLEAN + "\nThe pass rate was its 87 % over the block.\n", "figure.typed"),
}


@pytest.mark.parametrize("name", sorted(MUTANTS))
def test_each_mutant_is_killed(repo, monkeypatch, name):
    """The check's failing case is flagged by the lint and is not flagged by the mutant: the tests above kill it."""
    mutate, body, rule = MUTANTS[name]
    fname = "F-21_other.md" if name == "seeds" else "F-20_mine.md"
    assert rule in rules(run(repo, body, name=fname)), f"the unmutated lint misses {rule}"
    mutate(monkeypatch)
    assert rule not in rules(run(repo, body, name=fname)), f"mutant {name} survives"


# ------------------------------------------------------------------------------------------------ the record

#: the pinned declarations on master when the lint was built, and their errors -- each a real defect (Q-210's
#: hand-back), none a false alarm. A declaration pinned later is not listed: it must lint clean (the gatekeeper runs the
#: lint before it approves), so a later pin needs no edit here
PINNED = {
    "prereg/F-01_resting_order_level_atlas.md": {(130, "date.heldout"), (150, "date.heldout")},
    "prereg/F-03_opening_timing.md": set(),
    "prereg/RD-01_firm_contracts.md": {(1167, "form.phrase")},
    "prereg/RD-02_payout_policy.md": set(),
    "prereg/RD-03_contract_levers.md": set(),
    "prereg/RD-04_volatility_drift.md": {(892, "xref.template-item")},
    "prereg/RD-05_firm_modes.md": {(1, "form.head"), (3, "form.head"), (1203, "form.phrase")},
    "prereg/RD-06_firm_contracts_search_years.md": set(),
    "prereg/RD-07_payout_policy_search_years.md": set(),
    "prereg/RD-08_contract_levers_search_years.md": set(),
    "prereg/RD-09_firm_modes_part_f_search_years.md": set(),
    "prereg/RD-10_volatility_drift_search_years.md": set(),
}


def _pins() -> list[str]:
    """Every declaration pinned in this tree's decision log, read as `tests/test_declarations_fixed.py` reads them."""
    log = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    return sorted(set(L.re.findall(r"`(prereg/(?:F|RD)-\d+[^`]*\.md)` sha256 `[0-9a-f]{64}`", log)))


def test_the_listed_declarations_are_pinned():
    assert set(PINNED) <= set(_pins()), sorted(set(PINNED) - set(_pins()))


@pytest.mark.parametrize("rel", _pins())
def test_every_pinned_declaration_gives_exactly_its_listed_defects(rel):
    """A listed declaration gives exactly its listed errors; one pinned after the lint gives none."""
    found = L.lint(ROOT / rel, repo=ROOT)
    assert errs(found) == PINNED.get(rel, set()), sorted(p.render() for p in found if p.severity == L.ERROR)


def _have(*commits: str) -> bool:
    return all(subprocess.run(["git", "cat-file", "-e", f"{c}^{{commit}}"], cwd=ROOT, capture_output=True)
               .returncode == 0 for c in commits)


@pytest.mark.skipif(not _have("f454d8d", "a611a65"), reason="wt/wt-three f454d8d or wt/wt-lit a611a65 not in this clone")
def test_h3_at_f454d8d_is_flagged_for_the_gatekeepers_items_1_and_3(tmp_path):
    """`docs/reviews/GK_H3_c2_2026-11-22.md`: item 1 (R-10 cited at template v3's section 7, which holds no R-10, and
    "as pinned" with no pin row) at l.131, l.396-397 and Appendix D's l.583; item 3 (the counts not written as a
    product and a number) at l.156-162."""
    def show(spec: str, dest: Path) -> Path:
        dest.write_bytes(subprocess.run(["git", "show", spec], cwd=ROOT, capture_output=True, check=True).stdout)
        return dest
    decl = show("f454d8d:prereg/H3_three_way.md", tmp_path / "H3_three_way.md")
    tpl = show("a611a65:prereg/TEMPLATE_design_search.md", tmp_path / "TEMPLATE_design_search.md")
    found = L.lint(decl, repo=ROOT, rev="f454d8d", rel="prereg/H3_three_way.md", templates=[tpl])
    e = errs(found)
    for line in (131, 396, 583):
        assert (line, "xref.template-topic") in e and (line, "xref.template-unpinned") in e, sorted(e)
    for line in (156, 160):
        assert (line, "count.no-number") in e, sorted(e)
    assert {r for _, r in e} <= {"xref.template-topic", "xref.template-unpinned", "count.no-number"}, sorted(e)
