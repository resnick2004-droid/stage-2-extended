"""Wave 2.1 and 2.2 of the restart plan (E-207, E-210): the design-search template and the agents, skills and commands
brought into line with the journey objective.

* **The template** (`prereg/TEMPLATE_design_search.md`) holds every field CHARTER 3.3 to 3.9 requires, E-210's two
  template clauses (m-2, m-3), R-10, and `adapter.BinaryDraw`'s signature quoted from the vendored source with its
  nearer-barrier race; it matches no declaration glob, carries no seed and types no result number.
* **The old template** (`prereg/TEMPLATE_family.md`) is marked superseded for new work and kept for the record
  (`tests/test_family_stats.py` still holds its own wording).
* **The agents, skills and commands** no longer state E-008's trade-lift line as binding, and carry what E-207 (2)
  and E-210 ask of them (the review labels, the pre-hand-back checklist, the commit-message file, the memory check, the
  measures traced to `docs/MEASURES.md`, the held-out years unread, the challenger brief, `/brief`).

Text only: no bar, no engine, no outcome.
"""
from __future__ import annotations

import fnmatch
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "prereg" / "TEMPLATE_design_search.md"
OLD_TEMPLATE = ROOT / "prereg" / "TEMPLATE_family.md"
ADAPTER = ROOT / "vendor" / "stage2" / "propedge" / "contract" / "adapter.py"
CLAUDE_DIR = ROOT / ".claude"


def _text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _test_globs() -> list[str]:
    """Every glob literal a test file applies (the prereg folder's scans among them)."""
    pats = set()
    for p in (ROOT / "tests").glob("*.py"):
        for m in re.finditer(r"\.r?glob\(\s*f?[\"']([^\"']+)[\"']", _text(p)):
            pats.add(m.group(1))
    return sorted(pats)


# ============================================================================================ A. the template is no declaration


def test_the_template_matches_no_declaration_glob_and_is_no_declaration():
    from extended import reader as RD

    name = TEMPLATE.name
    assert TEMPLATE.is_file()
    assert not RD.F_ID.match(name) and not RD.DECLARATION_PATH.fullmatch(f"prereg/{name}")
    assert not re.search(r"(?:F|RD)-\d+", name)
    globs = _test_globs()
    assert "F-*.md" in globs and "*.md" in globs                   # the scan is not vacuous
    matching = [g for g in globs if fnmatch.fnmatch(name, g) or fnmatch.fnmatch(f"prereg/{name}", g)]
    assert set(matching) <= {"*.md", "*", "**/*.md"}, matching


def test_the_template_carries_no_seed_and_types_no_result_number():
    text = _text(TEMPLATE)
    assert "\r\n" not in text, "LF text (a pin hashes the LF bytes)"
    assert not re.search(r"\b\d{8}\b", text), re.findall(r"\b\d{8}\b", text)        # no seed literal
    assert not re.search(r"\b\d{6,7}\b", text), re.findall(r"\b\d{6,7}\b", text)    # nor a near one
    assert not re.search(r"\b0\.\d{3,}\b", text), re.findall(r"\b0\.\d{3,}\b", text)
    assert not re.search(r"\$\s?\d", text), "no dollar figure: a rule value is cited by its key"


# ============================================================================================ B. every CHARTER 3.3-3.9 field


SECTIONS = (
    "## 0. In plain words",
    "## 1. The question, the firm and the baselines",
    "## 2. Years, the held-out read ledger and the confirmation window",
    "## 3. The lever space",
    "## 4. The component schedule across sessions",
    "## 5. The zero-edge convention",
    "## 6. The survey, the surrogate and the rounds",
    "## 7. The pinning row",
    "## 8. The three-way test",
    "## 9. Calibration and the power gate",
    "## 10. The pass line",
    "## 11. Beside, never deciding",
    "## 12. Seeds -- by role",
    "## 13. The count",
    "## 14. The run order",
    "## 15. What a pass and what a fail mean; the confirmation",
    "## 16. Anything chosen after seeing results",
)

REQUIRED = (
    # 3.3: the lever space, the survey, the surrogate, the rounds, plateaus, the ledger, L
    "docs/plans/LEVER_TABLE_topstep50k.md", "extended/lever_space.py", "fixed / searched / dropped",
    "volatility units", "the survey size", "space-filling", "the surrogate", "the rounds", "plateau",
    "results/variants.jsonl", "The latency L", "five-minute cell",
    # 3.4-3.5: signal sources, design rules, the side rule, no-harm
    "signal source", "never opposing positions", "one position at a time", "side rule", "O-4", "no-harm floor",
    "the no-harm margin", "playbook", "hand-executable", "Any hour",
    # 3.6: years, ledger, single use, embargo, re-baseline, three-way test
    "2020-01-02", "2023-12-29", "2024-01-02", "2026-07-16", "results/q82_judged_sessions.csv",
    "held-out read ledger", "written after this reading; no figure cited", "nominal", "O-1", "horizon embargo",
    "sealed", "docs/plans/THREE_WAY_TEST_design.md", "wt/wt-verify", "coin-seed leg", "time leg", "held-out leg",
    "paired", "history null",
    # 3.7: finalists, calibration, power, budget
    "finalist order rule", "fixed-sequence", "antithetic twin", "disjoint seed sets", "power gate",
    "the size that matters", "O-3", "power target", "complete over D-145's horizon", "data question",
    "0.05 / (k (k + 1))", "E-204", "held-out row", "k = 13",
    # 3.8: the pass line and the floors, the verdict
    "O-5", "intersection-union", "zero-edge long-run gate", "+1 tick", "10 % of signals missed",
    "as-traded floor", "conduct tier 1", "0 % payout denial", "Focused Trader Program off",
    "history-level false-pass rate",
    # 3.9: one row pins every input, before the survey
    "the composite", "the fallback", "P under the bankroll stop", "one, never both", "the limits",
    "the bankroll budgets", "the weights", "normalisers", "regimes", "most years", "the gate's quantile",
    "minimum count of held-out starts", "the L values", "before the survey",
    # the measures, E-210's template clauses, R-10, BinaryDraw
    "docs/MEASURES.md", "m-2", "m-3", "R-10", "BinaryDraw", "nearer barrier", "zero gross expectation",
    "stop-fill convention", "one seeded driftless path", "refused",
    # the confirmation and the house rules
    "2026-07-17", "a purchase", "exploratory", "Seeds -- by role", "by role", "nowhere else",
    "Refusals first", "clean checkout", "run.lock",
)


def test_the_template_carries_every_charter_field():
    text = _text(TEMPLATE)
    missing = [r for r in REQUIRED if r not in text]
    assert not missing, missing


def test_the_template_sections_come_in_order():
    text = _text(TEMPLATE)
    at = [text.find(s) for s in SECTIONS]
    assert all(i >= 0 for i in at), [s for s, i in zip(SECTIONS, at) if i < 0]
    assert at == sorted(at), "sections out of order"


def test_the_pinning_row_lists_every_charter_3_9_input():
    """CHARTER 3.9's bullet list, each input named inside section 7 (the one pinning row), before the survey."""
    text = _text(TEMPLATE)
    sec = text[text.index("## 7. The pinning row"):text.index("## 8. The three-way test")]
    for item in ("the limits", "the bankroll budgets", "dimension", "the weights", "the composite", "the fallback",
                 "the size that matters", "power target", "regimes", "most years", "finalist order rule",
                 "plateau rule", "the gate's quantile", "minimum count of held-out starts", "no-harm margin",
                 "the L values", "caps", "the search years only", "before the survey"):
        assert item in sec, item


def test_the_template_carries_e210_clauses_m2_m3_and_r10():
    text = _text(TEMPLATE)
    sec = text[text.index("## 5. The zero-edge convention"):text.index("## 6. The survey")]
    # m-2: trades open at once on one instrument redrawn jointly from one seeded driftless path; refused until defined
    assert re.search(r"m-2.*one instrument.*jointly.*one seeded driftless path", sec, re.S)
    assert re.search(r"no design with overlapping positions (?:is run|runs)", sec)
    # m-3: a redrawn loss carries the run's stop-fill convention
    assert re.search(r"m-3.*redrawn loss carries the run's stop-fill convention", sec, re.S)
    # R-10: the time-limited trade's redraw, zero gross expectation, racing the cushion, its volatility from causal bars
    r10 = sec[sec.index("R-10"):]
    for s in ("time limit", "zero gross expectation", "cushion", "causal"):
        assert s in r10, s


def _binary_draw_signatures() -> list[str]:
    src = _text(ADAPTER)
    cls = src[src.index("class BinaryDraw"):]
    cls = cls[:cls.index("\ndef ")]
    sigs = re.findall(r"^    (def (?:__init__|__call__)\(.*?\)(?: -> [^:]+)?):", cls, re.M)
    assert len(sigs) == 2, sigs
    assert 'settlement = "race"' in cls
    return sigs


def test_the_template_quotes_binary_draw_from_the_vendored_source():
    """The signature is quoted verbatim from `vendor/stage2/propedge/contract/adapter.py` (read, never edited), so a
    newer snapshot that changes it fails here rather than leaving the template describing a different draw."""
    text = _text(TEMPLATE)
    for sig in _binary_draw_signatures():
        assert sig in text, sig
    assert 'settlement = "race"' in text
    assert "min(risk, max(cushion, 0))" in text            # the nearer barrier, as RandomDraw's truncate mode reads it


def test_the_template_names_its_held_out_reads_as_the_reader_parses_them():
    """`extended/reader.py` authorises a held-out (judged-block) read only for a purpose named on a "Judged-block
    reads:" line of the pinned declaration, and refuses a purpose with a choice or fitting word whatever the line says.
    A search drafted on the template must carry that line, or its one held-out test cannot run."""
    from extended import reader as RD

    text = _text(TEMPLATE)
    lines = RD.DECLARED_LINE.findall(text)
    assert len(lines) == 1, lines
    purposes = RD.PURPOSE_TOKEN.findall(lines[0])
    assert purposes and len(set(purposes)) == len(purposes), purposes
    for p in purposes:
        assert RD.PURPOSE.fullmatch(p), p
        assert not set(re.split(r"_+", p.lower())) & RD.CHOICE_WORDS, p
        assert p.startswith("heldout_"), p


def test_the_template_cites_files_that_exist():
    text = _text(TEMPLATE)
    for rel in ("docs/plans/LEVER_TABLE_topstep50k.md", "docs/MEASURES.md", "extended/lever_space.py",
                "results/q82_judged_sessions.csv", "vendor/stage2/propedge/contract/adapter.py",
                "vendor/stage2/config/rules.yaml", "CHARTER.md", "prereg/TEMPLATE_family.md"):
        assert rel in text, rel
        assert (ROOT / rel).exists(), rel


# ============================================================================================ C. the old template


def test_the_old_template_is_marked_superseded_and_kept():
    head = _text(OLD_TEMPLATE)[:1500]
    assert "Superseded for new work" in head
    assert "prereg/TEMPLATE_design_search.md" in head
    assert "kept for the record" in head


# ============================================================================================ D. agents, skills, commands


def _claude_files() -> list[Path]:
    files = [p for d in ("agents", "commands") for p in (CLAUDE_DIR / d).glob("*.md")]
    files += list((CLAUDE_DIR / "skills").rglob("SKILL.md"))
    assert len(files) >= 20, files
    return files


#: E-008's line stated as binding. Each may appear only inside a sentence that says it no longer decides.
BINDING_OLD_LINE = (
    "judged on its trades first",
    "judged on trades first",
    "The selection rule, unweakened",
    "selection rule against R\\* = P-14",
    "Stage 2 D-621 (3)'s rule against",
    "the user scorecard beside, never",
    "The user scorecard is beside, never the pass line",
    "limits (operator-approved, each with a margin wider than its noise) applied as menu flags",
)


def test_no_agent_skill_or_command_states_the_old_pass_line_as_binding():
    hits = []
    for p in _claude_files():
        for line in _text(p).splitlines():
            for s in BINDING_OLD_LINE:
                if s in line and not re.search(r"no longer decid|on record|retired|CHARTER 3\.10|E-210", line):
                    hits.append(f"{p.relative_to(ROOT)}: {s}")
    assert not hits, hits


def _has(rel: str, *needles: str) -> None:
    text = _text(CLAUDE_DIR / rel)
    missing = [n for n in needles if n not in text]
    assert not missing, (rel, missing)


def test_the_gatekeeper_checks_the_design_search_template():
    _has("agents/prereg-gatekeeper.md", "prereg/TEMPLATE_design_search.md", "E-204", "held-out row",
         "held-out read ledger", "pinning row", "power gate", "m-2", "m-3", "R-10", "docs/MEASURES.md",
         "seeds by role", "the finalist order rule", "the side rule")


def test_the_red_team_attacks_the_new_surfaces_with_the_labels():
    _has("agents/red-team.md", "**blocking**", "**minor**", "E-207", "held-out years", "peak-picking",
         "seed reuse", "unpaired", "limits set after", "a full re-read", "diff")


def test_the_auditor_rederives_journey_measures_and_the_three_way_test():
    _has("agents/auditor.md", "docs/MEASURES.md", "three-way test", "held-out read ledger", "martingale-outcome",
         "paired")


def test_the_scout_carries_the_standing_challenger_brief():
    _has("agents/scout.md", "challenger brief", "Q-150", "journey", "docs/MEASURES.md", "before any")


def test_the_skills_carry_the_new_rules():
    _has("skills/prereg-discipline/SKILL.md", "prereg/TEMPLATE_design_search.md", "martingale-outcome",
         "held-out years", "E-210")
    _has("skills/feature-rules/SKILL.md", "search years", "held-out years", "martingale-outcome",
         "shift-invariance test")
    _has("skills/merge-checklist/SKILL.md", "docs/MEASURES.md", "paired", "held-out", "**blocking**",
         "**minor**", "full re-read", "diff")
    _has("skills/worker-protocol/SKILL.md", "pre-hand-back checklist", "commit-message file", "own worktree",
         "free memory", "1.75 GB", "docs/reviews/")


def test_the_commands_show_the_search_and_brief_the_operator():
    _has("commands/status.md", "search rounds", "baselines", "held-out read ledger")
    _has("commands/brief.md", "plain English", "traced", "result file", "limits")
    assert (CLAUDE_DIR / "commands" / "brief.md").read_text(encoding="utf-8").startswith("---\n")


# ============================================================================================ E. corrective cycle 1
# (docs/reviews/TEMPLATE_AGENTS_2026-11-18.md: B-1 to B-5, m-1 to m-8, under the coordinator's rulings)

#: B-1: every copy of the redraw's law races the cushion less the stop-side exit cost, rounded inward.
RACE_COPIES = (
    "prereg/TEMPLATE_design_search.md",
    ".claude/agents/prereg-gatekeeper.md",
    ".claude/agents/red-team.md",
    ".claude/skills/merge-checklist/SKILL.md",
    ".claude/skills/feature-rules/SKILL.md",
    ".claude/skills/contract-engine/SKILL.md",
)


def test_every_copy_of_the_race_law_uses_the_cushion_less_the_stop_side_cost():
    for rel in RACE_COPIES:
        text = _text(ROOT / rel)
        assert "min(l, c - x_stop)" in text, rel
        assert "inward" in text, rel
        assert not re.search(r"min\(l, c\)", text), rel          # the full-cushion form B-1 rules out
        assert "uses BinaryDraw's law" not in text, rel


def test_the_template_states_the_costed_race_and_r10_walk_exactly():
    text = _text(TEMPLATE)
    sec = text[text.index("## 5. The zero-edge convention"):text.index("## 6. The survey")]
    for s in ("L = min(l, c - x_stop)", "p = L / (L + g)", "L <= 0", "the cost-free special case", "x = 0",
              "`stop_slippage_ticks`", "`flatten_slippage_ticks`", "rounded inward", "net expectation",
              "minus its costs", "the clip never binds", "the runner's rule", "fill-time law",
              "n = round(sigma^2 T / s^2)", "overrides", "convexity", "underlying"):
        assert s in sec, s
    assert "slipping a tick" not in sec, "a rule value typed: cite fills.yaml's key"


#: m-1 (ii): every terminal state of a run trade has its law, in one table.
TERMINAL_STATES = ("target", "stop", "stop gapped through", "the floor or the daily loss limit", "15:10 CT flatten",
                   "news window", "max hold", "any other exit")


def test_r10_maps_every_terminal_state_to_a_law():
    text = _text(TEMPLATE)
    sec = text[text.index("| terminal state in the run |"):]
    table = sec[:sec.index("\n\n")]
    rows = [r for r in table.splitlines()[2:] if r.strip().startswith("|")]
    assert len(rows) == len(TERMINAL_STATES), rows
    for state, row in zip(TERMINAL_STATES, rows):
        cells = row.split("|")
        assert state in cells[1], (state, row)
        assert ("race" in cells[2]) != ("stopped walk" in cells[2]), row        # exactly one law each


def test_the_whole_file_is_pinned_once_and_section_7_never_alone():
    """B-2: the whole renamed file is frozen by its hash at the first pin; section 7 is never pinned alone; the
    calibration's and power gate's inputs sit in the file; their outputs are pinned in E-115's form."""
    text = _text(TEMPLATE)
    assert "never pinned alone" in text
    assert "pinned first, alone" not in text and "from this heading to the next" not in text
    sec9 = text[text.index("## 9. Calibration"):text.index("## 10. The pass line")]
    for s in ("E-115", "docs/calibration/", "seeds", "estimator", "before the pin"):
        assert s in sec9, s
    run = text[text.index("## 14. The run order"):text.index("## 15.")]
    order = [run.find(s) for s in ("challenger brief", "**The pin**", "**The calibration and the power gate**",
                                   "**The go row**", "**The survey**", "**The finalists' row**",
                                   "**The held-out row**")]
    assert all(i >= 0 for i in order) and order == sorted(order), order


def _pin_hashes(log: str) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for rel, h in re.findall(r"`(prereg/(?:F|RD)-\d+[^`]*\.md)` sha256 `([0-9a-f]{64})`", log):
        out.setdefault(rel, set()).add(h)
    return out


def _gatekeeper_rename_and_hash(draft: Path, nn: str) -> tuple[Path, str]:
    """The gatekeeper's steps 2-3, as its file writes them: rename, replace `F-XX`, then hash the LF bytes."""
    import hashlib

    new = draft.with_name(draft.name.replace("DRAFT_F-XX", f"F-{nn}"))
    new.write_bytes(draft.read_bytes().replace(b"F-XX", f"F-{nn}".encode()))
    draft.unlink()
    return new, hashlib.sha256(new.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def test_the_gatekeepers_rename_leaves_the_hash_as_pinned(tmp_path):
    """B-2: the rename comes before the hash, so the pinned hash is the renamed file's and nothing the gatekeeper does
    afterwards changes a byte; every row citing a declaration cites one hash, so the reader's `pins()` sees one."""
    import hashlib

    from extended import reader as RD

    pre = tmp_path / "prereg"
    pre.mkdir()
    draft = pre / "DRAFT_F-XX_toy.md"
    draft.write_text(_text(TEMPLATE).replace("# TEMPLATE: a design search's declaration", "# F-XX: toy"),
                     encoding="utf-8", newline="\n")
    pinned, h = _gatekeeper_rename_and_hash(draft, "13")
    assert b"F-XX" not in pinned.read_bytes()
    rel = f"prereg/{pinned.name}"
    log = (f"| E-901 | d | pin `{rel}` sha256 `{h}` |\n"
           f"| E-902 | d | go row: `{rel}` sha256 `{h}` and the calibration record |\n")
    assert RD.pins(log) == {rel: {h}}
    assert hashlib.sha256(pinned.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == h
    # positive control: a second hash for the same file is what the reader refuses for good
    bad = log + f"| E-903 | d | `{rel}` sha256 `{'0' * 64}` |\n"
    assert len(RD.pins(bad)[rel]) == 2
    # the gatekeeper's text orders the rename before the hash, and keeps one hash
    gk = _text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md")
    assert gk.index("**Rename**") < gk.index("**Hash the final file's LF text**")
    assert "one hash" in gk


def test_every_pinned_declaration_carries_one_hash_in_the_log():
    log = _text(ROOT / "DECISIONS.md")
    multi = {rel: hs for rel, hs in _pin_hashes(log).items() if len(hs) > 1}
    assert not multi, multi


def test_held_out_reads_are_tied_to_the_run_order_and_the_market():
    """B-3: a `heldout_*` read only after the finalists' row and the held-out row; once per market across
    declarations; RD declarations never; no new registered_design read without a row; Q-158 the guard to come."""
    text = _text(TEMPLATE)
    run = text[text.index("## 14. The run order"):text.index("## 15.")]
    for s in ("after the finalists' row and the held-out row", "once per market", "Q-158",
              "no `Judged-block reads:` line", "registered_design", "five-minute cell", "path-structure edge",
              "denial ladder", "model-side"):
        assert s in run, s
    gk = _text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md")
    for s in ("results/read_ledger.jsonl", "an RD declaration naming any held-out purpose", "Q-158",
              "registered_design"):
        assert s in gk, s
    au = _text(CLAUDE_DIR / "agents" / "auditor.md")
    for s in ("`heldout_*`", "registered_design", "single use per market"):
        assert s in au, s


def test_the_long_run_gate_keeps_the_charter_quantile_and_o6_is_open():
    """B-4: CHARTER 3.8 (c)'s 'over coin seeds and history-block resamples' kept; O-6 states both options; no pin."""
    text = _text(TEMPLATE)
    assert text.count("coin seeds and history-block resamples") >= 2
    assert "over coin seeds, given the history" not in text
    o6 = text[text.index("**O-6"):]
    o6 = o6[:o6.index("\n\n")]
    for s in ("(a)", "(b)", "coin seeds only on the held-out years", "search years only", "No search pins"):
        assert s in o6, s
    assert "O-6" in _text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md")


def test_the_pair_rule_settlement_is_restored():
    """B-5: wherever a floor compares a resting entry with its reflection, a pair touching either leg's stop or target
    on the fill bar contributes zero lift, for the reason Phase 0's D-1 and D-13 give."""
    fr = _text(CLAUDE_DIR / "skills" / "feature-rules" / "SKILL.md")
    for s in ("contributes zero lift", "D-1", "D-13", "no-harm floor", "as-traded floor", "stop first"):
        assert s in fr, s
    text = _text(TEMPLATE)
    sec = text[text.index("## 5. The zero-edge convention"):text.index("## 6. The survey")]
    assert "contributes zero lift" in sec and "pair rule" in sec


def test_the_minor_findings_are_carried():
    gk = _text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md")
    for s in ("takes a k first", "E-005 (d)", "re-state", "at most three a market", "P-05, P-06 and P-10",
              "only by the operator's decision"):
        assert s in gk, s                                                                   # m-2, m-3
    rt = _text(CLAUDE_DIR / "agents" / "red-team.md")
    for s in ("sealed", "reverse reading", "intersection-union", "complete-start minimum", "tier-3 denial",
              "Focused Trader Program off"):
        assert s in rt, s                                                                   # m-4
    au = _text(CLAUDE_DIR / "agents" / "auditor.md")
    for s in ("sealed", "reverse reading", "denial rung", "Focused Trader Program off"):
        assert s in au, s                                                                   # m-4
    sc = _text(CLAUDE_DIR / "agents" / "scout.md")
    for s in ("2024-01-02", "never edits the finalist list"):
        assert s in sc, s                                                                   # m-5
    wp = _text(CLAUDE_DIR / "skills" / "worker-protocol" / "SKILL.md")
    for s in ("0. **The never lines.**", "2026-07-17", "vendor/", "licence guard", "clean run", "docs/MEASURES.md",
              "x_stop"):
        assert s in wp, s                                                                   # m-6
    assert ".commit_msg_*" in _text(ROOT / ".gitignore").splitlines()                         # m-6
    text = _text(TEMPLATE)
    for s in ("per unit and underlying", "a build requirement", "docs/plans/THREE_WAY_TEST_design.md` at"):
        assert s in text, s                                                                 # m-7
    assert "being revised" not in text
    assert (ROOT / "docs" / "plans" / "THREE_WAY_TEST_design.md").is_file()
    tr = _text(CLAUDE_DIR / "agents" / "results-tracer.md")
    assert "D-621 (5)" not in tr and "cell count" not in tr and "every design tried" in tr     # m-8
