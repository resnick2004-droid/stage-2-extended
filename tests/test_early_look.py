"""Q-213: the early look (`scripts/early_look.py`) -- exploratory, search years only, seeds by role, the declared
design read from RL3's draft, and a page whose every figure is traced to its file. The end-to-end runs on toys in a
child process (the script's `synthetic` mode: invented bars, no store read; the vendored engine in its own process).

The seed block's guard (the lead's ruling 3: code-owned like Q-82's): every seed of `SEED_BLOCK` appears, as a word,
in no file of this tree (tracked or untracked) and of no ref outside `DECLARED_USES` and the look's own result files.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import git_scan as GS  # noqa: E402
from extended import reader as RDR  # noqa: E402
from extended import three_way_seeds as S  # noqa: E402
from extended import walker as W  # noqa: E402

SCRIPT = ROOT / "scripts" / "early_look.py"
DECLARED_USES = ("scripts/early_look.py",)        # every other file takes the block by role (`EL.issue`)
OWN_RESULTS = re.compile(r"^results/early_look_[a-z0-9_]+\.csv(\.manifest\.json)?$")


def _module():
    name = "early_look_under_test"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


EL = _module()


# ------------------------------------------------------------------------------------------------ the declaration


#: the parameter table's rows the header cites (6.1), by line
ROWS = {"level kinds": 552, "side rules": 553, "stops": 554, "R": 555, "latency L": 556, "cutoff": 574}


def _draft_row(name: str) -> list[str]:
    row = (ROOT / EL.DRAFT).read_text(encoding="utf-8").splitlines()[ROWS[name] - 1]
    assert row.startswith(f"| {name} |"), row
    return [c.strip() for c in row.strip("|").split("|")]


def test_the_header_cites_the_draft_it_reads():
    assert EL.lf_sha256(ROOT / EL.DRAFT) == EL.DRAFT_SHA256


def test_the_design_is_the_drafts_first_declared_value_of_each_searched_parameter():
    kinds = re.findall(r"`(\w+)`", _draft_row("level kinds")[3])
    assert kinds[0] == EL.KIND == "pd"
    assert _draft_row("side rules")[3].startswith("`fade`") and set(EL.RULE.values()) == {"fade"}
    assert sorted(EL.RULE) == ["hi", "lo"]
    stops = [int(x) for x in re.findall(r"\d+", _draft_row("stops")[3].split("ticks")[0])]
    assert stops[0] == EL.STOP_TICKS == 50
    cut = re.search(r"latest of (\d\d):(\d\d)", _draft_row("cutoff")[3])
    assert EL.CUTOFF == W.slot(int(cut.group(1)), int(cut.group(2)))
    assert "latency-free" in _draft_row("latency L")[2]


def test_the_header_quotes_the_line_numbers_it_cites():
    lines = (ROOT / EL.DRAFT).read_text(encoding="utf-8").splitlines()
    assert lines[552 - 1].startswith("| level kinds |") and lines[553 - 1].startswith("| side rules |")
    assert lines[554 - 1].startswith("| stops |") and lines[555 - 1].startswith("| R |")
    assert lines[574 - 1].startswith("| cutoff |") and lines[556 - 1].startswith("| latency L |")
    assert "every R of the base's carried menu" in lines[987 - 1]
    assert "one-cancels-other" in lines[967 - 1] + lines[968 - 1]
    doc = EL.__doc__
    for n in (552, 553, 554, 555, 556, 574, 987, 967):
        assert f"line {n}" in doc or f"line {n}:" in doc, n


# ------------------------------------------------------------------------------------------------ the windows


def test_the_last_day_is_the_search_years_and_a_held_out_date_refuses():
    assert EL.check_last(EL.LAST) == RDR.CHOICE_END
    for bad in ("2024-01-02", "2026-07-17"):
        with pytest.raises(EL.EarlyLookRefused, match="E-208"):
            EL.check_last(bad)


def test_the_search_cut_refuses_a_held_out_last_day():
    from extended import search_cut as SC

    with pytest.raises(SC.LateRow):
        SC.authorise(purpose="early_look_search_years", declaration=None, what="test", last="2024-01-02")


# ------------------------------------------------------------------------------------------------ the seeds


def test_seeds_come_by_role_and_spares_refuse():
    assert [EL.issue(r) for r in ("el_coins", "el_sample", "el_tests")] == list(EL.SEED_BLOCK[:3])
    for spare in ("el_spare_3", "el_spare_9"):
        with pytest.raises(EL.EarlyLookRefused, match="spare"):
            EL.issue(spare)
    with pytest.raises(EL.EarlyLookRefused):
        EL.issue("h4b_coins")
    block = list(EL.SEED_BLOCK)
    assert len(block) == 10 and all(nxt - cur == 1 for cur, nxt in zip(block, block[1:]))       # one decade
    assert len(set(EL.ROLES.values())) == len(EL.ROLES)
    assert not (set(EL.SEED_BLOCK) & (set(S.BLOCK) | set(S.H4_BLOCK)))


def _block_hits() -> list[tuple[str, str]]:
    pat = "|".join(str(s) for s in EL.SEED_BLOCK)
    out = []
    r = GS.git("grep", "--untracked", "-l", "-I", "-w", "-E", pat, cwd=ROOT, text=True, encoding="utf-8",
               errors="replace")
    if r.returncode not in (0, 1):
        raise RuntimeError(r.stderr)
    out += [("working tree", ln.strip().replace("\\", "/")) for ln in r.stdout.splitlines() if ln.strip()]
    refs = GS.git("for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", "refs/tags", cwd=ROOT,
                  text=True, encoding="utf-8")
    names = [x for x in refs.stdout.split() if x and not x.endswith("/HEAD")]
    for ref, rest in GS.grep_refs(ROOT, ["-l", "-I", "-w", "-E", pat], names, encoding="utf-8", errors="replace"):
        out.append((ref, rest.strip().replace("\\", "/")))
    return out


def test_the_seed_block_appears_in_no_other_file():
    bad = [f"{p} ({where})" for where, p in _block_hits() if p not in DECLARED_USES and not OWN_RESULTS.match(p)]
    assert not bad, "the early look's seed block named outside its declared uses:\n" + "\n".join(sorted(set(bad)))


def test_the_seed_scan_finds_the_block_where_it_is():
    hits = {p for _, p in _block_hits()}
    assert "scripts/early_look.py" in hits                                             # not vacuous


# ------------------------------------------------------------------------------------------------ the tree


def _git_repo(tmp_path: Path) -> Path:
    for a in (["init", "-q"], ["config", "user.email", "t@example.invalid"], ["config", "user.name", "t"]):
        subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "a.txt").write_text("a\n", encoding="utf-8")
    subprocess.run(["git", "add", "a.txt"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "a"], cwd=tmp_path, check=True, capture_output=True)
    return tmp_path


def test_a_dirty_tree_refuses_the_write(tmp_path):
    repo = _git_repo(tmp_path)
    EL.require_clean(repo)
    (repo / "b.txt").write_text("b\n", encoding="utf-8")
    with pytest.raises(EL.EarlyLookRefused, match="dirty"):
        EL.require_clean(repo)
    with pytest.raises(EL.EarlyLookRefused, match="dirty"):
        EL.write(pd.DataFrame({"x": [1]}), tmp_path / "out", {}, repo)


def test_the_run_refuses_outside_a_clean_run(monkeypatch):
    monkeypatch.delenv("S2X_CLEAN_RUN", raising=False)
    with pytest.raises(EL.EarlyLookRefused, match="clean run"):
        EL.run()


# ------------------------------------------------------------------------------------------------ the toy end-to-end


@pytest.fixture(scope="module")
def toy(tmp_path_factory):
    out = tmp_path_factory.mktemp("early_look_toy")
    r = subprocess.run([sys.executable, str(SCRIPT), "synthetic", "--out", str(out)], cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8", timeout=900)
    assert r.returncode == 0, r.stderr[-3000:]
    return out, json.loads(r.stdout.strip().splitlines()[-1])


def test_the_toy_run_is_labelled_exploratory_everywhere(toy):
    out, info = toy
    res = Path(info["result"])
    assert res.parent == out and res.name == f"{EL.RESULT}.csv"
    man = json.loads(Path(str(res) + ".manifest.json").read_text(encoding="utf-8"))
    assert man["exploratory"] is True and man["prereg_id"] is None
    assert man["description"].startswith(EL.LABEL)
    df = pd.read_csv(res)
    assert df["exploratory"].astype(bool).all() and (df["label"] == EL.LABEL).all()
    page = Path(info["page"]).read_text(encoding="utf-8")
    assert f"**{EL.LABEL}.**" in page.splitlines()[2]


def test_the_toy_run_reads_no_date_past_the_search_years(toy):
    out, info = toy
    man = json.loads(Path(info["result"] + ".manifest.json").read_text(encoding="utf-8"))
    p = man["parameters"]
    assert p["last_date"] <= EL.LAST and p["first_date"] >= "2020-01-02"
    df = pd.read_csv(info["result"])
    assert set(df["arm"]) == {"off"} and set(df["reading"]) == {"martingale_outcome"}


def test_the_toy_run_draws_by_role(toy):
    _, info = toy
    man = json.loads(Path(info["result"] + ".manifest.json").read_text(encoding="utf-8"))
    assert man["seed"] == EL.issue("el_coins")
    assert man["parameters"]["seed_roles"] == {"el_coins": EL.issue("el_coins"), "el_sample": EL.issue("el_sample")}
    assert man["parameters"]["part"] == EL.PART


def test_the_toy_run_reaches_the_journey_and_the_oracle(toy):
    _, info = toy
    assert info["trades"] > 0 and info["units"] > 0
    assert info["oracle"] > 0                       # every taken trade of the toys re-derived by H4's oracle
    df = pd.read_csv(info["result"])
    assert {"first_pass_days", "spent_before_first_payout", "payouts_per_month", "monthly_net_4_12_median",
            "peak_oop_12_months", "net_month_12"} <= set(df["measure"])


def test_every_figure_of_the_page_is_traced_to_the_file(toy):
    out, info = toy
    assert info["page_problems"] == []
    trace = json.loads(Path(info["page"] + ".trace.json").read_text(encoding="utf-8"))
    assert len(trace) == len(EL.PAGE_ROWS) and {t["file"] for t in trace} == {f"{EL.RESULT}.csv"}


def test_a_typed_figure_or_a_changed_cell_is_caught(toy, tmp_path):
    """Positive controls: a figure typed into the page, and a trace whose value is not its file's cell."""
    out, info = toy
    page, res = Path(info["page"]), Path(info["result"])
    typed = tmp_path / "typed.md"
    typed.write_text(page.read_text(encoding="utf-8").replace("| not read |", "| 1234 |", 1), encoding="utf-8")
    (tmp_path / "typed.md.trace.json").write_bytes(Path(str(page) + ".trace.json").read_bytes())
    assert EL.page_problems(typed, {res.name: res})
    moved = tmp_path / "moved.md"
    moved.write_bytes(page.read_bytes())
    tr = json.loads(Path(str(page) + ".trace.json").read_text(encoding="utf-8"))
    tr[0]["value"] = (tr[0]["value"] or 0.0) + 1.0
    (tmp_path / "moved.md.trace.json").write_text(json.dumps(tr), encoding="utf-8")
    assert any("its file" in p for p in EL.page_problems(moved, {res.name: res}))
