"""Q-110 (E-103, E-104): the one parser of the identity-holds tokens (`extended/identity_tokens.py`) and its script
(`scripts/identity_tokens.py`).

E-104's form is positional: a row recording that an identity holds begins `| E-NNN | YYYY-MM-DD | ` and then, as the
first text of its third cell, the unquoted token (the stem, a colon and a space, the id, ` @ `, the sha, ` -- `) and
the row's text. Tested here: every breach (a) to (d) tripped and the clean cases passing; the exact-match cases (`Q-8`
is never read in `Q-80`, `Q-800`, `Q-80x`); a descriptive mention anywhere but the token position never a token,
backticked or not; `held` on a throwaway git repository (an ancestor, a non-ancestor, a covered file changed since,
the newest qualifying row); and the repository's own `DECISIONS.md` with no breach. Fast tier: nothing here reads data
or runs the engine; the git repository is a temporary folder.
"""
from __future__ import annotations

import importlib.util
import io
import re
import subprocess
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from extended import identity_tokens as IT
from extended.identity_tokens import Token

ROOT = Path(__file__).resolve().parent.parent
SHA = "f7eda0d"
STEM = "identity-holds"
HEADER = "# Decision log\n\nSome prose.\n\n| id | date | decision | basis |\n|---|---|---|---|\n"


def row(rid: str, body: str, basis: str = "The run's log.") -> str:
    return f"| {rid} | 2026-11-16 | {body} | {basis} |"


def trow(rid: str, ident: str, sha: str = SHA, text: str = "**Q-80's identity HOLDS** (EXIT 0).") -> str:
    """A row carrying the positional token for `ident` at `sha`."""
    return row(rid, f"{STEM}: {ident} @ {sha} -- {text}")


def log(*rows: str) -> str:
    return HEADER + "\n".join(rows) + "\n"


def tagged(problems: list[str], tag: str) -> list[str]:
    return [p for p in problems if p.startswith(f"({tag})")]


# --- the clean cases -------------------------------------------------------------------------------------------------

def test_a_positional_token_is_parsed_with_no_breach():
    text = log(row("E-109", "Nothing about tokens; a commit 784cae2."), trow("E-110", "Q-80"))
    assert IT.parse(text) == [Token("E-110", "Q-80", SHA)]
    assert IT.problems(text) == []


def test_queue_ids_labels_and_every_sha_length_parse():
    full = "0123456789abcdef0123456789abcdef01234567"
    text = log(trow("E-110", "Q-104d"), trow("E-111", "Q-04", "1234567"), trow("E-112", "pp_identity", full),
               trow("E-113", "t10w2"))
    assert IT.parse(text) == [Token("E-110", "Q-104d", SHA), Token("E-111", "Q-04", "1234567"),
                              Token("E-112", "pp_identity", full), Token("E-113", "t10w2", SHA)]
    assert IT.problems(text) == []


def test_an_identity_held_again_at_a_newer_commit_is_no_breach():
    text = log(trow("E-110", "Q-80", "f7eda0d"), trow("E-120", "Q-80", "a1f3415"))
    assert [t.sha for t in IT.parse(text)] == ["f7eda0d", "a1f3415"]
    assert IT.problems(text) == []


def test_the_placeholders_are_ignored_anywhere_but_the_token_position():
    e098 = row("E-098", f"A row recording that an identity holds carries `{STEM}: Q-nn`; no other row does.")
    e104 = row("E-104", f"the form `{STEM}: <id> @ <sha>` followed by a double hyphen; unquoted {STEM}: <id> too.")
    text = HEADER.replace("Some prose.", f"The rule: {STEM}: <id> @ <sha> -- text.") + e098 + "\n" + e104 + "\n"
    assert IT.parse(text) == []
    assert IT.problems(text) == []
    assert [o.kind for o in IT.occurrences(text)] == ["placeholder"] * 4


def test_crlf_line_ends_still_make_rows():
    text = log(trow("E-110", "Q-80"), trow("E-111", "Q-93")).replace("\n", "\r\n")
    assert [t.ident for t in IT.parse(text)] == ["Q-80", "Q-93"]
    assert IT.problems(text) == []


def test_prose_is_neither_a_token_nor_a_breach():
    """A space for the hyphen is prose (the identity scripts print it and rows quote them); a mention of the token
    without its colon is a mention."""
    text = log(row("E-110", "identity holds: Q-80 at 500 paths; identity HOLDS: Q-94 U1 P14 = the file."),
               row("E-111", f"the {STEM} token is written only when it holds; the `{STEM}` tokens."),
               row("E-112", "identity holds: Q-80 @ f7eda0d -- a quoted line, not a token."))
    assert IT.parse(text) == []
    assert IT.problems(text) == []
    assert IT.occurrences(text) == []


# --- exact matching --------------------------------------------------------------------------------------------------

def test_an_id_is_never_read_inside_a_longer_one():
    text = log(trow("E-110", "Q-80"), trow("E-111", "Q-800"), trow("E-112", "Q-80x"))
    assert [t.ident for t in IT.parse(text)] == ["Q-80", "Q-800", "Q-80x"]
    assert not [t for t in IT.parse(text) if t.ident == "Q-8"]
    assert IT.problems(text) == []
    assert IT.parse(log(trow("E-110", "Q-8"))) == [Token("E-110", "Q-8", SHA)]


def test_a_label_is_never_read_inside_a_longer_one():
    assert [t.ident for t in IT.parse(log(trow("E-110", "t10w2x"), trow("E-111", "pp_identity_2")))] == \
        ["t10w2x", "pp_identity_2"]


# --- a description is never a token ----------------------------------------------------------------------------------

@pytest.mark.parametrize("line", [
    row("E-110", f"Q-80 read: {STEM}: Q-80 @ {SHA} -- HOLDS."),                       # later in the third cell
    row("E-110", f"Q-80 read: `{STEM}: Q-80 @ {SHA} -- HOLDS`."),                     # backticked
    row("E-110", "Q-80 HOLDS.", f"{STEM}: Q-80 @ {SHA} -- the sources cell"),        # a later cell
    f"Prose: {STEM}: Q-80 @ {SHA} -- HOLDS.",                                         # a line that is no row
    "  " + trow("E-110", "Q-80"),                                                     # an indented line is no row
    row("E-110", f"Q-80 read; the runner waits on {STEM}: Q-80."),
    row("E-110", f"Q-80 read; the runner waits on `{STEM}: Q-80`."),
])
def test_a_description_anywhere_but_the_token_position_is_never_a_token(line):
    text = log(line)
    assert IT.parse(text) == []
    probs = IT.problems(text)
    assert len(probs) == 1 and tagged(probs, "d"), probs


def test_a_token_beside_a_mid_row_description_counts_once():
    text = log(trow("E-110", "Q-80", text=f"Q-80 HOLDS; Q-93 waits on {STEM}: Q-93 @ a1f3415 -- later."))
    assert IT.parse(text) == [Token("E-110", "Q-80", SHA)]
    probs = IT.problems(text)
    assert len(probs) == 1 and tagged(probs, "d") and "Q-93" in probs[0], probs


# --- the breaches ----------------------------------------------------------------------------------------------------

def test_a_the_same_id_at_the_same_sha_in_two_rows_is_a_breach_naming_both():
    text = log(trow("E-110", "Q-80"), trow("E-112", "Q-80"), trow("E-113", "Q-93"))
    probs = IT.problems(text)
    assert len(probs) == 1 and tagged(probs, "a"), probs
    assert "Q-80" in probs[0] and "E-110" in probs[0] and "E-112" in probs[0] and "Q-93" not in probs[0]


def test_a_a_sha_and_its_longer_form_name_one_commit():
    probs = IT.problems(log(trow("E-110", "Q-80", "f7eda0d"), trow("E-112", "Q-80", "f7eda0d4c2")))
    assert len(probs) == 1 and tagged(probs, "a"), probs
    assert IT.problems(log(trow("E-110", "Q-80", "f7eda0d"), trow("E-112", "Q-93", "f7eda0d"))) == []


@pytest.mark.parametrize("words", [
    "the identity is still owed",
    "the payout was withheld",                       # inside a word
    "upheld by the review",
    "the held-out block",                            # a different word
    "the thresholds",
    f"the {STEM} token",                             # the stem's own -holds
    "Holds",                                         # not one of the three spellings
    "the identity holding",
])
def test_b_a_token_row_without_holds_HOLDS_or_held_is_a_breach(words):
    probs = IT.problems(log(trow("E-110", "Q-80", text=f"Q-80: {words}.")))
    assert len(probs) == 1 and tagged(probs, "b") and "E-110" in probs[0], probs


@pytest.mark.parametrize("words", ["the identity holds", "identity HOLDS", "it held", "**HOLDS**", "(held)"])
def test_b_holds_HOLDS_or_held_as_a_word_satisfies_the_check(words):
    assert IT.problems(log(trow("E-110", "Q-80", text=f"Q-80: {words}."))) == []


def test_b_the_word_may_stand_in_the_sources_cell():
    assert IT.problems(log(row("E-110", f"{STEM}: Q-80 @ {SHA} -- Q-80 read.", "The log: identity HOLDS."))) == []


@pytest.mark.parametrize("body", [
    f"`{STEM}: Q-80 @ {SHA}` -- HOLDS",              # backticks
    f"`{STEM}: Q-80 @ {SHA} -- HOLDS`",
    f"{STEM}: `Q-80` @ {SHA} -- HOLDS",
    f"**{STEM}: Q-80 @ {SHA} -- HOLDS**",            # emphasis before it
    f"  {STEM}: Q-80 @ {SHA} -- HOLDS",              # spaces before it
    f"{STEM}:Q-80 @ {SHA} -- HOLDS",                 # no space after the colon
    f"{STEM}:  Q-80 @ {SHA} -- HOLDS",               # two
    f"{STEM} : Q-80 @ {SHA} -- HOLDS",               # a space before the colon
    f"{STEM}:\u00a0Q-80 @ {SHA} -- HOLDS",           # a no-break space
    f"{STEM} Q-80 @ {SHA} -- HOLDS",                 # no colon
    f"Identity-holds: Q-80 @ {SHA} -- HOLDS",        # another case
    f"identity_holds: Q-80 @ {SHA} -- HOLDS",        # another joiner
    f"identity\u2011holds: Q-80 @ {SHA} -- HOLDS",   # a non-breaking hyphen
    f"identity-hold: Q-80 @ {SHA} -- HOLDS",
    f"{STEM}: P-14 @ {SHA} -- HOLDS",                # a bad id
    f"{STEM}: Q-80xy @ {SHA} -- HOLDS",
    f"{STEM}: q-80 @ {SHA} -- HOLDS",
    f"{STEM}: 80 @ {SHA} -- HOLDS",
    f"{STEM}: Q-80, Q-93 @ {SHA} -- HOLDS",
    f"{STEM}: <id> @ <sha> -- HOLDS",                # a placeholder where a token belongs
    f"{STEM}: Q-nn @ {SHA} -- HOLDS",
    f"{STEM}: Q-80 {SHA} -- HOLDS",                  # no @
    f"{STEM}: Q-80 @{SHA} -- HOLDS",
    f"{STEM}: Q-80  @ {SHA} -- HOLDS",
    f"{STEM}: Q-80 @ f7eda0 -- HOLDS",               # a bad sha: six
    f"{STEM}: Q-80 @ F7EDA0D -- HOLDS",              # upper case
    f"{STEM}: Q-80 @ f7eda0g -- HOLDS",
    f"{STEM}: Q-80 @ 0123456789abcdef0123456789abcdef012345678 -- HOLDS",   # 41
    f"{STEM}: Q-80 @ {SHA} - HOLDS",                 # no double hyphen
    f"{STEM}: Q-80 @ {SHA} HOLDS",
    f"{STEM}: Q-80 @ {SHA} \u2014 HOLDS",            # a dash for the double hyphen
    f"{STEM}: Q-80 @ {SHA} --HOLDS",
    f"{STEM}: Q-80 @ {SHA} --  HOLDS",
    f"{STEM}: Q-80 @ {SHA} --",                      # no text
])
def test_c_a_malformed_positional_token_is_a_breach_and_never_a_token(body):
    text = log(row("E-110", body, "The log: identity HOLDS."))
    assert IT.parse(text) == []
    probs = IT.problems(text)
    assert len(probs) == 1 and tagged(probs, "c") and "E-110" in probs[0], probs


@pytest.mark.parametrize("line", [
    f"|E-110| 2026-11-16 | {STEM}: Q-80 @ {SHA} -- HOLDS | x |",          # the bars' spacing
    f"| E-110 |  2026-11-16 | {STEM}: Q-80 @ {SHA} -- HOLDS | x |",
    f"| E-110 | 16 Nov | {STEM}: Q-80 @ {SHA} -- HOLDS | x |",              # not a date
    f"| E-110 | 2026-11-16 |{STEM}: Q-80 @ {SHA} -- HOLDS | x |",           # no space before the token
])
def test_c_the_row_start_is_exact(line):
    text = log(line)
    assert IT.parse(text) == []
    probs = IT.problems(text)
    assert len(probs) == 1 and tagged(probs, "c"), probs


@pytest.mark.parametrize("mention", [
    f"{STEM}: Q-80",
    f"`{STEM}: Q-80`",
    f"{STEM}:Q-80",
    f"IDENTITY-HOLDS: Q-80",
    f"identity_holds: Q-80",
    f"{STEM} Q-80",
    f"{STEM}: Q-nnx",                                # not the placeholder
    f"{STEM}: <ident>",
    f"{STEM}:",
])
def test_d_a_non_placeholder_string_elsewhere_is_a_breach(mention):
    text = log(row("E-110", f"Q-80 read; {mention} is written when it holds."))
    probs = IT.problems(text)
    assert IT.parse(text) == []
    assert len(probs) == 1 and tagged(probs, "d") and "E-110" in probs[0], probs


def test_d_a_line_that_is_no_row_names_its_line():
    text = HEADER.replace("Some prose.", f"Prose with {STEM}: Q-80 in it.")
    probs = IT.problems(text)
    assert len(probs) == 1 and tagged(probs, "d") and "line 3" in probs[0], probs


def test_the_breaches_are_counted_independently():
    text = log(trow("E-110", "Q-80"), trow("E-111", "Q-80", text="owed, see E-110"),
               row("E-112", f"{STEM}:Q-9 @ {SHA} -- HOLDS"), row("E-113", f"x {STEM}: Q-9"))
    probs = IT.problems(text)
    assert [p[:3] for p in probs] == ["(a)", "(b)", "(c)", "(d)"], probs


def test_no_problem_message_is_ever_a_token():
    """A message the lead might copy into a row's third cell is never read as a token."""
    text = log(trow("E-110", "Q-80"), trow("E-111", "Q-80"), trow("E-112", "t10w2", text="owed"),
               row("E-113", f"{STEM}:Q-9 @ {SHA} -- HOLDS"), "prose " + f"{STEM}: Q-93")
    probs = IT.problems(text)
    assert len(probs) == 4, probs
    assert IT.parse(log(*(row(f"E-2{i:02d}", p) for i, p in enumerate(probs)))) == []


CONTEXTS = ["{s}", "x {s} y", "({s})", "**{s}**", "{s}.", "a{s}b", "`{s}`", "`{s} `", "` {s}`", "`run {s}`",
            "'{s}'", "\"{s}\"", "{s} @ " + SHA + " -- HOLDS", "`{s} @ " + SHA + "` -- HOLDS"]


@pytest.mark.parametrize("ident", ["Q-80", "Q-8", "Q-104d", "pp_identity", "t10w2"])
@pytest.mark.parametrize("context", CONTEXTS)
@pytest.mark.parametrize("where", ["third", "later", "sources"])
def test_no_silent_string(ident, context, where):
    """Wherever the stem, a colon and a real id stand, the guard either parses the token at its position or reports
    a breach: a clean report means every such string in the log is a token."""
    s = context.format(s=f"{STEM}: {ident}")
    line = {"third": row("E-110", s, "identity HOLDS"), "later": row("E-110", f"Q-80 HOLDS at {SHA}; {s}"),
            "sources": row("E-110", f"Q-80 HOLDS at {SHA}.", s)}[where]
    text = log(line)
    if IT.problems(text) == []:
        assert IT.parse(text) == [Token("E-110", ident, SHA)], line


# --- held(): on a throwaway git repository ---------------------------------------------------------------------------

def git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, (args, r.stdout, r.stderr)
    return r.stdout.strip()


@pytest.fixture(scope="module")
def repo(tmp_path_factory) -> dict:
    """master: c1 (a.py, b.py, pkg/m.py) -> c2 (b.py changed) -> c3 (notes.md added; HEAD); side: c1 -> s1."""
    t = tmp_path_factory.mktemp("held_repo")
    git(t, "init", "-q", "-b", "master")
    git(t, "config", "user.email", "t@example.invalid")
    git(t, "config", "user.name", "t")
    git(t, "config", "core.autocrlf", "false")

    def commit(msg: str, files: dict[str, str]) -> str:
        for rel, body in files.items():
            (t / rel).parent.mkdir(parents=True, exist_ok=True)
            (t / rel).write_text(body, encoding="utf-8")
        git(t, "add", "-A")
        git(t, "commit", "-q", "-m", msg)
        return git(t, "rev-parse", "HEAD")

    c1 = commit("c1", {"a.py": "a = 1\n", "b.py": "b = 1\n", "pkg/m.py": "m = 1\n"})
    c2 = commit("c2", {"b.py": "b = 2\n"})
    c3 = commit("c3", {"notes.md": "a record\n"})
    git(t, "checkout", "-q", "-b", "side", c1)
    s1 = commit("s1", {"notes.md": "a side record\n"})
    git(t, "checkout", "-q", "master")
    return {"path": t, "c1": c1, "c2": c2, "c3": c3, "s1": s1}


def H(text: str, repo: dict, ident: str = "Q-80", covered=("a.py",), head: str = "HEAD"):
    return IT.held(text, ident, repo["path"], head, list(covered))


def test_held_an_ancestor_with_its_covered_files_unchanged(repo):
    text = log(trow("E-110", "Q-80", repo["c1"][:10]))
    assert H(text, repo) == Token("E-110", "Q-80", repo["c1"][:10])
    assert H(text, repo, covered=("a.py", "pkg/m.py")) is not None
    assert H(text, repo, covered=("pkg\\m.py",)) is not None          # a Windows separator is read as git's
    assert H(text, repo, covered=("pkg",)) is not None                 # a folder covers what is under it


def test_held_at_head_itself(repo):
    text = log(trow("E-110", "Q-80", repo["c3"][:7]))
    assert H(text, repo, covered=("a.py", "b.py", "notes.md")) == Token("E-110", "Q-80", repo["c3"][:7])


def test_not_held_when_a_covered_file_changed_since(repo):
    text = log(trow("E-110", "Q-80", repo["c1"][:10]))
    assert H(text, repo, covered=("b.py",)) is None
    assert H(text, repo, covered=("a.py", "b.py")) is None
    tok, why = IT.held_report(text, "Q-80", repo["path"], "HEAD", ["b.py"])
    assert tok is None and any("b.py" in w for w in why), why


def test_held_again_after_the_change_at_the_newer_commit(repo):
    text = log(trow("E-110", "Q-80", repo["c1"][:10]), trow("E-120", "Q-80", repo["c2"][:10]))
    assert H(text, repo, covered=("b.py",)) == Token("E-120", "Q-80", repo["c2"][:10])


def test_not_held_at_a_commit_that_is_not_an_ancestor(repo):
    text = log(trow("E-110", "Q-80", repo["s1"][:10]))
    assert H(text, repo) is None                                       # a.py is the same on both sides
    assert H(text, repo, head=repo["s1"]) == Token("E-110", "Q-80", repo["s1"][:10])
    assert H(log(trow("E-110", "Q-80", repo["c2"][:10])), repo, head=repo["c1"]) is None   # a descendant of the head


def test_held_is_the_newest_qualifying_row_by_its_number(repo):
    both = [trow("E-120", "Q-80", repo["c2"][:10]), trow("E-110", "Q-80", repo["c1"][:10])]
    assert H(log(*both), repo).row == "E-120"                          # file order reversed: the number decides
    skip = [trow("E-110", "Q-80", repo["c1"][:10]), trow("E-120", "Q-80", repo["s1"][:10])]
    assert H(log(*skip), repo).row == "E-110"                          # the newest is off the head's line
    unknown = [trow("E-110", "Q-80", repo["c1"][:10]), trow("E-120", "Q-80", "deadbeef00")]
    assert H(log(*unknown), repo).row == "E-110"                       # a sha not in the repository
    owed = [trow("E-110", "Q-80", repo["c1"][:10]), trow("E-120", "Q-80", repo["c3"][:10], "owed, not run")]
    assert H(log(*owed), repo).row == "E-110"                          # a row with breach (b) admits nothing


def test_held_reads_only_the_exact_id_and_only_positional_tokens(repo):
    text = log(trow("E-110", "Q-80", repo["c1"][:10]),
               row("E-111", f"Q-93 HOLDS; {STEM}: Q-93 @ {repo['c1'][:10]} -- a description."),
               row("E-112", f"`{STEM}: Q-94 @ {repo['c1'][:10]}` -- HOLDS"))
    assert H(text, repo, "Q-8") is None
    assert H(text, repo, "Q-800") is None
    assert H(text, repo, "Q-93") is None
    assert H(text, repo, "Q-94") is None
    assert H(text, repo, "Q-80") is not None


def test_held_refuses_a_misuse(repo):
    text = log(trow("E-110", "Q-80", repo["c1"][:10]))
    with pytest.raises(ValueError):
        H(text, repo, covered=())                                      # an identity covers some code
    with pytest.raises(ValueError):
        H(text, repo, covered=("missing.py",))                         # a covered path not at the head
    with pytest.raises(ValueError):
        H(text, repo, covered=(str(repo["path"] / "a.py"),))           # absolute
    with pytest.raises(ValueError):
        H(text, repo, head="no-such-ref")
    with pytest.raises(ValueError):
        H(text, repo, ident="Q-80 ")                                   # not an id
    with pytest.raises(TypeError):
        IT.held(text, "Q-80", repo["path"], "HEAD", "a.py")             # a string, not a list of paths


# --- the repository's own log ----------------------------------------------------------------------------------------

def test_the_repository_decision_log_has_no_breach():
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    assert IT.problems(text) == []
    # not vacuous: the scan sees E-098's and E-099's placeholders in the real log
    rows = {o.row for o in IT.occurrences(text) if o.kind == "placeholder"}
    assert {"E-098", "E-099"} <= rows


# --- the script ------------------------------------------------------------------------------------------------------

def _script():
    spec = importlib.util.spec_from_file_location("s2x_identity_tokens", ROOT / "scripts" / "identity_tokens.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run(*argv: str) -> tuple[int, str]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = _script().main(list(argv))
    return code, buf.getvalue()


def test_the_script_lists_tokens_and_exits_zero_on_a_clean_log(tmp_path):
    p = tmp_path / "DECISIONS.md"
    p.write_text(log(trow("E-110", "Q-80"), trow("E-111", "t10w2")), encoding="utf-8")
    code, out = _run("--path", str(p))
    assert code == 0, out
    assert re.search(r"E-110\s+Q-80\s+at f7eda0d", out) and re.search(r"E-111\s+t10w2", out)
    assert "breaches: none" in out


def test_the_script_exits_one_on_a_breach_and_lists_it(tmp_path):
    p = tmp_path / "DECISIONS.md"
    p.write_text(log(trow("E-110", "Q-80"), trow("E-111", "Q-80")), encoding="utf-8")
    code, out = _run("--path", str(p))
    assert code == 1, out
    assert "(a)" in out and "E-110" in out and "E-111" in out


def test_the_script_exits_two_when_the_log_cannot_be_read(tmp_path):
    code, out = _run("--path", str(tmp_path / "missing.md"))
    assert code == 2, out


def test_the_script_reports_held_and_not_held(tmp_path, repo):
    p = tmp_path / "DECISIONS.md"
    p.write_text(log(trow("E-110", "Q-80", repo["c1"][:10])), encoding="utf-8")
    base = ("--path", str(p), "--repo", str(repo["path"]))
    code, out = _run(*base, "--held", "Q-80", "a.py", "pkg/m.py")
    assert code == 0, out
    assert re.search(r"Q-80: held .*E-110", out)
    code, out = _run(*base, "--held", "Q-80", "a.py", "--held", "Q-80", "b.py")
    assert code == 3, out
    assert "NOT held" in out and "b.py" in out
    code, out = _run(*base, "--held", "Q-80", "missing.py")
    assert code == 2, out
