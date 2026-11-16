"""Q-111 (E-113): the shared identities' covers (`extended/identity_cover.py`), the one declaration every runner
imports for its waits (E-104; `extended.identity_tokens.held`, Q-110).

Tested here: the four shared ids with their scripts and rows; every covered path at HEAD (or staged as an addition, the
commit being made); `BASE` leading every cover; **each cover exactly `BASE` and its script's import closure within this
repository**, computed from the syntax (`IC.imports`), with nothing unresolved and every `sys.path` change the model
knows; the import model itself on a synthetic tree (`from extended import x`, `import extended.x`, `from identity
import ...`, relative imports, bare names through `identity/`, `vendor/` never followed, function-local and
`try` imports, dynamic imports followed or reported); `cover` refusing an unknown id; and `held` on a throwaway git
repository built with an empty hooks folder: an identity is not held once its own script, a manifest or any file
under `config/` (edited or added; E-117) changed after its token, is held across a change to the log or a file it does
not cover, and a list without the script accepts the edit (the loophole the cover closes). Fast tier: no data, no
engine, no result; the git repository is a temporary folder. Tokens are composed from `IT.STEM` at run time, never
written out here.
"""
from __future__ import annotations

import functools
import os
import subprocess
from pathlib import Path

import pytest

from extended import identity_cover as IC
from extended import identity_tokens as IT
from extended.identity_tokens import Token

ROOT = Path(__file__).resolve().parent.parent
IDS = ("Q-80", "Q-89", "Q-93", "Q-101")
STAGE2 = "identity/stage2_identity.py"
_GIT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE")


@functools.lru_cache(maxsize=None)
def closure(ident: str) -> IC.Closure:
    return IC.imports(IC.SCRIPT[ident])


def git(repo: Path, *args: str) -> str:
    env = {k: v for k, v in os.environ.items() if k not in _GIT_ENV}
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, timeout=60, env=env)
    assert r.returncode == 0, (args, r.stdout, r.stderr)
    return r.stdout.strip()


# --- the declaration -------------------------------------------------------------------------------------------------

def test_the_shared_ids_are_the_four_with_their_scripts_and_rows():
    assert tuple(IC.COVER) == IDS
    assert set(IC.SCRIPT) == set(IC.ROWS) == set(IC.CERTIFIES) == set(IDS)
    assert IC.SCRIPT == {"Q-80": "identity/gate_identity.py", "Q-89": "identity/place_records_identity.py",
                         "Q-93": "identity/user_beside_identity.py", "Q-101": "identity/replay_records_identity.py"}
    assert IC.ROWS == {"Q-80": ("E-049", "E-071"), "Q-89": ("E-055",), "Q-93": ("E-059", "E-084"),
                       "Q-101": ("E-068",)}
    for ident in IDS:
        assert IT.ID.fullmatch(ident)                                  # an id the tokens' grammar admits
        assert IC.SCRIPT[ident] in IC.CERTIFIES[ident]                 # what it certifies names its own script


def test_every_cover_path_exists_at_head():
    """A file is at HEAD (or staged as an addition: the commit being made); a folder (`config/`) holds a file there."""
    paths = sorted(set().union(*IC.COVER.values()))
    known = set(git(ROOT, "ls-tree", "-r", "--name-only", "HEAD", "--", *paths).splitlines()) | \
        set(git(ROOT, "diff", "--cached", "--name-only", "--diff-filter=A", "--", *paths).splitlines())
    missing = [p for p in paths if (not any(f.startswith(p) for f in known) if p.endswith("/") else p not in known)]
    assert not missing, f"covered paths not at HEAD (nor staged as an addition): {missing}"
    assert [p for p in paths if not ((ROOT / p).is_dir() if p.endswith("/") else (ROOT / p).is_file())] == []


def test_base_leads_every_cover_and_every_path_is_plain():
    assert IC.BASE == ("extended/__init__.py", "config/", "vendor/MANIFEST_stage2.sha256",
                       "vendor/DATA_MANIFEST_stage2.sha256")                # E-117: config/ whole
    for ident in IDS:
        c = IC.COVER[ident]
        assert c[:len(IC.BASE)] == IC.BASE, ident
        assert c[len(IC.BASE)] == IC.SCRIPT[ident], ident              # then the identity's own script
        assert len(set(c)) == len(c), ident
        for p in c:
            assert p == p.strip() and "\\" not in p and not p.startswith(("/", ".")) and ".." not in p.split("/")
            assert not p.startswith("vendor/") or p in IC.BASE         # vendor/ only through its manifests
            assert not p.endswith("/") or p in IC.BASE                 # the one folder is BASE's config/
        assert "config/" in IC.cover(ident)


def test_each_cover_holds_its_script_and_stage2_identity_where_imported():
    for ident in IDS:
        assert IC.SCRIPT[ident] in IC.cover(ident)
        if STAGE2 in closure(ident).files:
            assert STAGE2 in IC.cover(ident), ident
    assert all(STAGE2 in IC.COVER[i] for i in IDS)                     # every one of the four imports it


@pytest.mark.parametrize("ident", IDS)
def test_each_cover_is_base_and_its_scripts_import_closure(ident):
    """The AST check: the cover cannot fall behind the code (nor keep a file the code no longer imports)."""
    c = closure(ident)
    assert c.unresolved == (), f"{ident}: imports the model cannot resolve (resolve them or extend the model): " \
                               f"{list(c.unresolved)}"
    assert c.script == IC.SCRIPT[ident] and c.script in c.files
    missing = sorted(set(c.files) - set(IC.COVER[ident]))
    assert not missing, f"{ident}'s script imports {missing}, which its cover lacks: add them to COVER[{ident!r}]"
    stale = sorted(set(IC.COVER[ident]) - set(IC.BASE) - set(c.files))
    assert not stale, f"{ident}'s cover lists {stale}, which its script no longer imports"
    assert IC.uncovered(IC.SCRIPT[ident], IC.COVER[ident]) == []


#: every `sys.path` change in the four closures, as (file, statement, the loop's iterable): `SEARCH` models exactly
#: these -- `use_vendored_stage2` puts vendor/stage2 and its scripts/ first; each identity script its root and its own
#: folder (HERE = identity/, ROOT its parent); stage2_identity's `_setup` the Stage 2 tree (vendor/stage2 unless its own
#: main is given --root) and its scripts/, and its main the root (its HERE is the root)
PATH_EDITS = {
    ("extended/__init__.py", "sys.path.remove(p)", '(str(root), str(root / "scripts"))'),
    ("extended/__init__.py", "sys.path.insert(0, p)", '(str(root), str(root / "scripts"))'),
    ("identity/gate_identity.py", "sys.path.insert(0, _p)", "(str(ROOT), str(HERE))"),
    ("identity/place_records_identity.py", "sys.path.insert(0, _p)", "(str(ROOT), str(HERE))"),
    ("identity/user_beside_identity.py", "sys.path.insert(0, _p)", "(str(ROOT), str(HERE))"),
    ("identity/replay_records_identity.py", "sys.path.insert(0, _p)", "(str(ROOT), str(HERE))"),
    ("identity/stage2_identity.py", "sys.path.insert(0, str(root))", ""),
    ("identity/stage2_identity.py", 'sys.path.insert(0, str(root / "scripts"))', ""),
    ("identity/stage2_identity.py", "sys.path.insert(0, str(HERE))", ""),
}


def test_the_import_model_knows_every_sys_path_change():
    assert IC.SEARCH == ("vendor/stage2/scripts", "vendor/stage2", ".", "identity")
    met = {(e.file, e.call, e.loop) for i in IDS for e in closure(i).path_edits}
    assert met == PATH_EDITS, f"a sys.path change the model does not know (extend SEARCH and PATH_EDITS): " \
                              f"{sorted(met - PATH_EDITS)}; gone: {sorted(PATH_EDITS - met)}"


@pytest.mark.parametrize("bad", ["Q-8", "Q-800", "Q-80x", "q-80", "Q-80 ", " Q-80", "Q-104", "pp_identity", "t10w2",
                                 "f03-a0", "<id>", "", None, 80])
def test_cover_refuses_an_unknown_id(bad):
    with pytest.raises(ValueError):
        IC.cover(bad)


def test_cover_gives_the_declared_tuple():
    for ident in IDS:
        assert IC.cover(ident) is IC.COVER[ident] and isinstance(IC.cover(ident), tuple)


def test_uncovered_names_what_a_runners_list_lacks():
    """RD-02's list for Q-80 at the time of Q-111 (the gate, the campaign, the manifests): the script and the rest of
    its closure are named."""
    short = ("extended/gate.py", "extended/campaign.py", "vendor/MANIFEST_stage2.sha256",
             "vendor/DATA_MANIFEST_stage2.sha256")
    gaps = IC.uncovered(IC.SCRIPT["Q-80"], short)
    assert "identity/gate_identity.py: not covered" in gaps
    assert {g.split(":")[0] for g in gaps} == set(IC.COVER["Q-80"]) - set(short)
    assert IC.uncovered(IC.SCRIPT["Q-80"], ["extended", "identity\\", "vendor", "config/"]) == []   # folders: all under
    assert IC.uncovered(IC.SCRIPT["Q-80"], ["extended", "identity", "vendor", "config/rules_extended.yaml"]) == \
        ["config/: not covered"]                                         # one file of config/ is not the folder
    with pytest.raises(TypeError):
        IC.uncovered(IC.SCRIPT["Q-80"], "extended")
    with pytest.raises(ValueError):
        IC.imports("vendor/stage2/scripts/user_journey.py")             # a vendored script is not followed
    with pytest.raises(ValueError):
        IC.imports("identity/no_such_identity.py")


# --- the import model on a synthetic tree ----------------------------------------------------------------------------

def tree(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(body, encoding="utf-8")
    return root


SYNTH = {
    "extended/__init__.py": "ROOT = 1\n",
    "extended/a.py": "from . import b\nfrom .c import x\nfrom .pkg import deep\n",
    "extended/b.py": "",
    "extended/c.py": "x = 1\n",
    "extended/pkg/__init__.py": "",
    "extended/pkg/deep.py": "from .. import d\n",
    "extended/d.py": "import extended.e\n",
    "extended/e.py": "def f():\n    from extended import g as G\n    return G\n",
    "extended/g.py": "import os\nimport numpy\nfrom collections import OrderedDict\n",
    "extended/f.py": "",
    "extended/unused.py": "x = 1\n",
    "identity/s.py": ("import sys\nimport helper\nfrom extended import a, ROOT\nfrom identity import h2\n"
                      "import scripts.tool\nimport vend\nfrom propedge.core import thing\n"
                      "if sys.platform == 'never':\n    import extended.f\n"),
    "identity/helper.py": "x = 1\n",
    "identity/h2.py": "try:\n    from extended import f\nexcept ImportError:\n    f = None\n",
    "scripts/tool.py": "",
    "vendor/stage2/scripts/vend.py": "import extended.unused\nimport no_such_module_q111\n",
    "vendor/stage2/propedge/__init__.py": "",
    "vendor/stage2/propedge/core.py": "import extended.unused\nthing = 1\n",
}


def test_the_closure_follows_every_import_form_and_never_vendor(tmp_path):
    root = tree(tmp_path, SYNTH)
    c = IC.imports("identity/s.py", root)
    assert c.unresolved == ()
    assert set(c.files) == {"identity/s.py", "identity/helper.py", "identity/h2.py", "extended/__init__.py",
                            "extended/a.py", "extended/b.py", "extended/c.py", "extended/pkg/__init__.py",
                            "extended/pkg/deep.py", "extended/d.py", "extended/e.py", "extended/g.py",
                            "extended/f.py", "scripts/tool.py"}
    assert "extended/unused.py" not in c.files                           # reached only through vendor/: not followed
    assert IC.uncovered("identity/s.py", ["vendor", "config", "extended", "identity", "scripts"], root) == []
    assert IC.uncovered("identity/s.py", ["vendor", "config", "extended", "identity"], root) == \
        ["scripts/tool.py: not covered"]


def test_the_closure_reports_what_it_cannot_resolve(tmp_path, monkeypatch):
    elsewhere = tmp_path / "elsewhere"
    tree(tmp_path, {
        "extended/__init__.py": "",
        "extended/lit.py": "",
        "extended/lit2.py": "",
        "elsewhere/hidden_q111.py": "",
        "identity/bad.py": (
            "import importlib\n"                                                    # 1
            "name = 'extended.lit'\n"                                               # 2
            "importlib.import_module(name)\n"                                       # 3 reported: not a literal
            "importlib.import_module('extended.lit')\n"                             # 4 followed
            "__import__('extended.lit2')\n"                                         # 5 followed
            "spec = importlib.util.spec_from_file_location('m', 'p.py')\n"          # 6 reported: by path
            "exec('import os')\n"                                                   # 7 reported: text run
            "import no_such_module_q111\n"                                          # 8 reported: nowhere
            "import extended.missing\n"                                             # 9 reported: not found
            "from extended import *\n"                                              # 10 reported: star
            "from .nowhere import y\n"                                              # 11 reported: relative
            "import hidden_q111\n"                                                  # 12 reported: only via this path
            "frame = None\n"                                                        # 13
            "def g(df):\n"                                                          # 14
            "    return df.eval('a + b')\n"                                         # 15 not an import
        ),
    })
    monkeypatch.syspath_prepend(str(elsewhere))
    c = IC.imports("identity/bad.py", tmp_path)
    assert {"extended/lit.py", "extended/lit2.py"} <= set(c.files)
    lines = sorted(int(u.split(":")[1]) for u in c.unresolved)
    assert lines == [3, 6, 7, 8, 9, 10, 11, 12], c.unresolved
    assert any("found only through this process's own path" in u for u in c.unresolved)
    assert all(u.startswith("identity/bad.py:") for u in c.unresolved)
    assert IC.uncovered("identity/bad.py", ["extended", "identity", "vendor", "config"], tmp_path) == \
        [f"unresolved: {u}" for u in c.unresolved]


def test_the_closure_lists_every_sys_path_change(tmp_path):
    tree(tmp_path, {"identity/p.py": ("import sys\nfrom pathlib import Path\nfor q in ('a', 'b'):\n"
                                      "    sys.path.insert(0, q)\nsys.path.append('c')\nsys.path[0] = 'd'\n"
                                      "sys.path = []\nfrom sys import path\n")})
    edits = IC.imports("identity/p.py", tmp_path).path_edits
    assert [(e.line, e.call, e.loop) for e in edits] == [
        (4, "sys.path.insert(0, q)", "('a', 'b')"), (5, "sys.path.append('c')", ""), (6, "sys.path[0] = 'd'", ""),
        (7, "sys.path = []", ""), (8, "from sys import path", "")]


# --- held() on a throwaway repository --------------------------------------------------------------------------------

HEADER = "# Decision log\n\n| id | date | decision | basis |\n|---|---|---|---|\n"


def token_row(n: int, ident: str, sha: str) -> str:
    return f"| E-{n} | 2026-11-16 | {IT.STEM}: {ident} @ {sha} -- **{ident}'s identity HOLDS** (a throwaway row). | " \
           "the test's log |"


@pytest.fixture(scope="module")
def tokens_repo(tmp_path_factory) -> dict:
    """c0: every covered path of the four (stubs; the folder `config/` with one file), the log, a note; c1 (`log`):
    the log with each identity's token at c0. From c1, one branch a change: each identity's own script (its id), a
    manifest (`manifest`), a file under config/ edited (`config`) and one added (`config_new`), and the note with a
    later row (`notes`)."""
    hooks = tmp_path_factory.mktemp("empty_hooks")
    t = tmp_path_factory.mktemp("cover_repo")
    git(t, "init", "-q", f"--template={hooks}", "-b", "master")
    git(t, "config", "core.hooksPath", str(hooks))
    git(t, "config", "user.email", "t@example.invalid")
    git(t, "config", "user.name", "t")
    git(t, "config", "core.autocrlf", "false")
    assert list(hooks.iterdir()) == [] and not list((t / ".git" / "hooks").glob("*"))

    def commit(msg: str, files: dict[str, str]) -> str:
        tree(t, files)
        git(t, "add", "-A")
        git(t, "commit", "-q", "-m", msg)
        return git(t, "rev-parse", "HEAD")

    paths = sorted(set().union(*IC.COVER.values()))
    stubs = {(f"{p}rules_extended.yaml" if p.endswith("/") else p): f"# {p}\n" for p in paths}
    c0 = commit("c0", {**stubs, "DECISIONS.md": HEADER, "notes.md": "a note\n"})
    text = HEADER + "\n".join(token_row(900 + i, ident, c0[:12]) for i, ident in enumerate(IDS)) + "\n"
    out = {"path": t, "text": text, "c0": c0, "log": commit("c1: the tokens", {"DECISIONS.md": text})}
    changes = {**{i: {IC.SCRIPT[i]: f"# {IC.SCRIPT[i]}, edited after its token\n"} for i in IDS},
               "manifest": {"vendor/MANIFEST_stage2.sha256": "a new snapshot\n"},
               "config": {"config/rules_extended.yaml": "# a rule changed after the tokens\n"},
               "config_new": {"config/calendar_new.csv": "date,kind\n"},
               "notes": {"notes.md": "another note\n",
                         "DECISIONS.md": text + "| E-990 | 2026-11-16 | A later row. | the test |\n"}}
    for name, files in changes.items():
        git(t, "checkout", "-q", "-B", f"b{len(out)}", out["log"])
        out[name] = commit(name, files)
    git(t, "checkout", "-q", "master")
    return out


def held(r: dict, ident: str, head: str, covered=None):
    return IT.held(r["text"], ident, r["path"], r[head], list(IC.cover(ident) if covered is None else covered))


def test_the_throwaway_log_is_clean(tokens_repo):
    assert IT.problems(tokens_repo["text"]) == []
    assert [t.ident for t in IT.parse(tokens_repo["text"])] == list(IDS)


@pytest.mark.parametrize("ident", IDS)
def test_held_across_the_log_and_an_uncovered_file(tokens_repo, ident):
    want = Token(f"E-{900 + IDS.index(ident)}", ident, tokens_repo["c0"][:12])
    assert held(tokens_repo, ident, "log") == want                    # the token's own row came after its commit
    assert held(tokens_repo, ident, "notes") == want                  # a note and a later row change nothing covered


@pytest.mark.parametrize("ident", IDS)
def test_not_held_once_its_own_script_changed_after_its_token(tokens_repo, ident):
    r = tokens_repo
    tok, why = IT.held_report(r["text"], ident, r["path"], r[ident], list(IC.cover(ident)))
    assert tok is None and len(why) == 1 and IC.SCRIPT[ident] in why[0], why
    without = [p for p in IC.cover(ident) if p != IC.SCRIPT[ident]]
    assert held(r, ident, ident, without) is not None                 # a list without the script accepts the edit


def test_a_script_another_identity_imports_refuses_that_one_too(tokens_repo):
    r = tokens_repo
    assert held(r, "Q-89", "Q-80") is None                            # place_records_identity imports gate_identity
    assert held(r, "Q-101", "Q-93") is None                           # replay_records_identity imports user_beside's
    assert held(r, "Q-93", "Q-80") is not None                        # user_beside_identity does not import gate's


@pytest.mark.parametrize("ident", IDS)
def test_not_held_once_a_manifest_changed(tokens_repo, ident):
    tok, why = IT.held_report(tokens_repo["text"], ident, tokens_repo["path"], tokens_repo["manifest"],
                              list(IC.cover(ident)))
    assert tok is None and "vendor/MANIFEST_stage2.sha256" in why[0], why


@pytest.mark.parametrize("ident", IDS)
def test_not_held_once_a_file_under_config_changed(tokens_repo, ident):
    """E-117: config/ is in BASE whole -- a file under it edited, or one added, after the token fails every wait."""
    r = tokens_repo
    for head, changed in (("config", "config/rules_extended.yaml"), ("config_new", "config/calendar_new.csv")):
        tok, why = IT.held_report(r["text"], ident, r["path"], r[head], list(IC.cover(ident)))
        assert tok is None and len(why) == 1 and changed in why[0], (head, why)
