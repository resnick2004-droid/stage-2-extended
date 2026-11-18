"""RD-05's run in six steps, and the refusals before each (`prereg/RD-05_firm_modes.md` 13, 18; E-200).

Every step runs from a clean checkout of a named commit (`scripts/run_clean.py`), one heavy job on the machine under
`run.lock`, and **only after the lead's row records the one before**. `step_problems(step)` lists every reason a step
may not start; a runner prints them under `--plan` and refuses (exit 3) when any is found. Nothing here reads a bar,
a trade or a result's numbers.

**The checks, by step (18's waits; 13.1; 13.2):**

* every step: the declaration's LF text hashes to the pin and `E-200` pins it (`reader.pins`); no `e015-limits:` row
  exists that this reading's menu would not apply (12.6: none is applied, so any refuses -- E-104's form);
* before step 0: the record's merge -- every Appendix R key at the status the text states (`record_problems`, T-0's
  mapping) and Q-136b's entries present; every shared identity held at a commit containing it (`waited`): Q-05 (E-010),
  Q-80, Q-93 (with Q-100), Q-101, and RD-01's `firms_identity` (Q-104), each by `identity_tokens.held` on its cover;
* before step 1: the lead's row recording step 0 -- **a positional token** (S-11, E-104's form): the row's third
  cell begins `rd05-step-recorded: 0 @ <sha> -- ` (written in documents only as that placeholder), the sha the
  recorded run's commit, an ancestor of (or) the commit being run, and the text naming `results/modes_rules.csv`;
* before step 2: `modes_coin_identity` held (its own token, its cover `modes_cover`);
* before step 3: `modes_identity` held, and a row recording step 2 (`results/modes_coin.csv`);
* before step 4: a row recording step 3 (`results/modes_reading.csv`), and Q-44's per-start file on master
  (`results/user_beside_starts.csv`);
* before step 5: a row recording step 4 (`results/modes_beside.csv`);
* steps 3 to 5 also refuse while part F's adapters are not built (`NOT_BUILT`).

**The covers** (13.1, Q-111's rule): `BASE` plus the identity's script and its import closure
(`identity_cover.imports`); `cover_problems` holds them to the rule (`identity_cover.uncovered`).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

from extended import ROOT
from extended import identity_cover as IC
from extended import identity_rows as IR
from extended import modes_terms as M
from extended import reader

#: the steps of section 18: script, purposes, weight, workers
STEPS: dict[int, dict[str, Any]] = {
    0: {"script": "scripts/modes_rules.py", "purposes": (), "weight": "light", "workers": 1,
        "writes": ("results/modes_rules.csv",)},
    1: {"script": "identity/modes_coin_identity.py identity/modes_identity.py", "purposes": ("identity",),
        "weight": "heavy", "workers": 1, "writes": ()},
    2: {"script": "scripts/modes_coin.py", "purposes": (), "weight": "heavy", "workers": 2,
        "writes": ("results/modes_coin.csv",)},
    3: {"script": "scripts/modes_reading.py", "purposes": ("modes_scorecard",), "weight": "heavy", "workers": 1,
        "writes": ("results/modes_reading.csv", "results/modes_menu.csv")},
    4: {"script": "scripts/modes_beside.py", "purposes": ("modes_ladder_beside",), "weight": "heavy", "workers": 1,
        "writes": ("results/modes_beside.csv",)},
    5: {"script": "scripts/modes_gate.py", "purposes": ("modes_gate_beside",), "weight": "heavy", "workers": 1,
        "writes": ("results/modes_gate.csv",)},
}
#: what each step's predecessor wrote, which the lead's row must name before it starts
RECORDED_BY = {1: "results/modes_rules.csv", 3: "results/modes_coin.csv", 4: "results/modes_reading.csv",
               5: "results/modes_beside.csv"}
COIN_IDENTITY = "identity/modes_coin_identity.py"
MODES_IDENTITY = "identity/modes_identity.py"
#: part F's pieces not built at this commit (the hand-back's list); a step that needs one refuses
NOT_BUILT: dict[int, str] = {
    1: "modes_coin_identity items (c) and (d) and modes_identity need part F's account classes (A-2 to A-12's account "
       "forms, A-14's composition): not built",
    3: "part F (A-14's composition of each plan on the registered trades, the account classes, A-18 in the replay, "
       "the flip on the registered trades): not built",
    4: "part F's ladder and placement replays: not built",
    5: "part F's gates through extended/gate.py with A-14's gate arguments: not built",
}
E015_ROW = re.compile(r"^\|\s*(E-\d+)\s*\|\s*\d{4}-\d{2}-\d{2}\s*\|\s*e015-limits:", re.MULTILINE)


def _decisions(repo: Path) -> str:
    p = repo / "DECISIONS.md"
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def declaration_problems(repo: Path = ROOT) -> list[str]:
    p = repo / M.DECLARATION
    if not p.is_file():
        return [f"{M.DECLARATION} is missing"]
    got = reader.sha256_lf(p)
    out = []
    if got != M.DECLARATION_SHA256:
        out.append(f"{M.DECLARATION}'s LF sha256 is {got}, not the pinned {M.DECLARATION_SHA256}")
    pins = reader.pins(_decisions(repo)).get(M.DECLARATION, set())
    if M.DECLARATION_SHA256 not in pins:
        out.append(f"no decision row pins {M.DECLARATION} at {M.DECLARATION_SHA256} (E-200)")
    return out


def e015_problems(repo: Path = ROOT) -> list[str]:
    rows = E015_ROW.findall(_decisions(repo))
    return [f"{r}: an e015-limits row exists; this reading's menu applies none (12.6) -- refused until it does"
            for r in rows]


def record_problems() -> list[str]:
    """13.2 and 4.1: every Appendix R record key at the status the text states; Stage 2's keys verified."""
    out = []
    for k, want in M.RECORD_KEYS.items():
        try:
            got = M.status(k)
        except KeyError:
            out.append(f"{k}: not in the record")
            continue
        if got != want:
            out.append(f"{k}: status {got!r} at this commit, {want!r} in the text (a change after the pin, 4.1)")
    for k in M.STAGE2_KEYS:
        try:
            M.s2(k)
        except Exception as exc:                                     # noqa: BLE001
            out.append(f"Stage 2's {k}: {exc}")
    return out


def terms_problems() -> list[str]:
    """13.2: every role of every mode-corner resolves -- a refusal of the loaders or of A-19 is a problem."""
    out = []
    for m in M.MODE_CORNERS:
        try:
            M.mode_corner_terms(m)
        except Exception as exc:                                     # noqa: BLE001
            out.append(f"Appendix M row {m.index} ({m.mode} {m.corner}): {type(exc).__name__}: {exc}")
    return out


def modes_cover(script: str, repo: Path = ROOT) -> tuple[str, ...]:
    """13.1's covers: `BASE`, the script and its import closure."""
    return tuple(dict.fromkeys(IC.BASE + IC.imports(script, repo).files))


def cover_problems(repo: Path = ROOT) -> list[str]:
    out = []
    for s in (COIN_IDENTITY, MODES_IDENTITY):
        out += [f"{s}'s cover: {q}" for q in IC.uncovered(s, modes_cover(s, repo), repo)]
    return out


def shared_waits() -> tuple[IR.Waited, ...]:
    """13.1's shared identities: Q-05 (E-010; U1's start rows through `identity/stage2_identity.py`, by the same rule),
    Q-80, Q-93 (whose cover holds Q-100's), Q-101, and RD-01's `firms_identity` (Q-104)."""
    q05 = tuple(dict.fromkeys(IC.BASE + IC.imports("identity/stage2_identity.py", ROOT).files))
    return (IR.Waited("Q-05", "U1's start rows (E-010)", q05),
            IR.Waited("Q-80", "Q-71's 500-path gate identities", IC.cover("Q-80")),
            IR.Waited("Q-93", "U1's adapter identity with Q-100's", IC.cover("Q-93")),
            IR.Waited("Q-101", "the replay records' identity (E-068)", IC.cover("Q-101")),
            IR.Waited("Q-104", "RD-01's identity stage, identity/firms_identity.py", IR.cover("Q-104")))


def own_wait(step: int) -> tuple[IR.Waited, ...]:
    if step == 2:
        return (IR.Waited("modes_coin_identity", "RD-05's coin identity (13.1 1)", modes_cover(COIN_IDENTITY)),)
    if step == 3:
        return (IR.Waited("modes_identity", "RD-05's replay identity (13.1 2)", modes_cover(MODES_IDENTITY)),)
    return ()


STEP_STEM = "rd05-step-recorded"
STEP_TOKEN = re.compile(rf"^\|\s*(E-\d+)\s*\|\s*\d{{4}}-\d{{2}}-\d{{2}}\s*\|\s*{STEP_STEM}: (\d) @ ([0-9a-f]{{7,40}}) -- "
                        r"([^|]*)\|", re.MULTILINE)


def step_cell(step: int, sha: str, text: str) -> str:
    """The third cell of the lead's row recording step `step` (S-11), for tests and for the lead."""
    if not re.fullmatch(r"[0-9a-f]{7,40}", str(sha)) or not str(text).strip():
        raise ValueError("a step's record names a 7- to 40-hex sha and its text")
    return f"{STEP_STEM}: {int(step)} @ {sha} -- {text}"


def _ancestor(repo: Path, sha: str, head: str) -> bool:
    r = subprocess.run(["git", "merge-base", "--is-ancestor", sha, head], cwd=str(repo), capture_output=True)
    return r.returncode == 0


def recorded(step_done: int, path: str, repo: Path = ROOT, *, decisions_text: str | None = None,
             head: str = "HEAD") -> bool:
    """S-11: whether a decision row's third cell begins with step `step_done`'s positional token, at a sha that is
    the commit being run or an ancestor of it, its text naming the step's result file. Text elsewhere never counts."""
    text = _decisions(repo) if decisions_text is None else decisions_text
    for m in STEP_TOKEN.finditer(text):
        if int(m.group(2)) == int(step_done) and path in m.group(4) and _ancestor(repo, m.group(3), head):
            return True
    return False


def step_problems(step: int, repo: Path = ROOT, *, head: str = "HEAD") -> list[str]:
    """Every reason step `step` may not start (section 18), in order."""
    if step not in STEPS:
        raise ValueError(f"no step {step}")
    out = declaration_problems(repo) + e015_problems(repo)
    out += record_problems() + terms_problems()
    if step == 0:
        probs, _ = IR.waited_problems(repo, shared_waits(), head=head)
        out += probs
    if step in RECORDED_BY and not recorded(step - 1, RECORDED_BY[step], repo, head=head):
        out.append(f"no decision row records step {step - 1} by its token ({STEP_STEM}: {step - 1} @ <sha> -- naming "
                   f"{RECORDED_BY[step]})")
    if step in (2, 3):
        probs, _ = IR.waited_problems(repo, own_wait(step), head=head)
        out += probs
    if step == 4 and not (repo / "results" / "user_beside_starts.csv").is_file():
        out.append("Q-44's per-start file (results/user_beside_starts.csv) is not on this commit")
    if step in NOT_BUILT:
        out.append(f"NOT BUILT: {NOT_BUILT[step]}")
    return out


def head_sha(repo: Path = ROOT) -> str:
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo), capture_output=True, text=True)
    return r.stdout.strip()


__all__ = ["STEPS", "RECORDED_BY", "NOT_BUILT", "COIN_IDENTITY", "MODES_IDENTITY", "declaration_problems",
           "e015_problems", "record_problems", "terms_problems", "modes_cover", "cover_problems", "shared_waits",
           "own_wait", "STEP_STEM", "STEP_TOKEN", "step_cell", "recorded", "step_problems", "head_sha"]
