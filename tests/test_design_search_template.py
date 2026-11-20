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


def test_a_search_carries_no_judged_block_line_and_names_its_holder():
    """B-3 (the red team's third read; E-221, O-1; E-238): `extended/reader.py` honours a held-out purpose only on the
    pinned declaration's own `Judged-block reads:` line (and, by Q-158's rule 1, after a finalists' token for its own
    hash). A search drafted on the template carries no such line, so no single search can read NQ's held-out years;
    the held-out test's declaration carries it, with its own finalists' token, and is the one family that reads them."""
    from extended import reader as RD

    text = _text(TEMPLATE)
    assert RD.DECLARED_LINE.findall(text) == [], RD.DECLARED_LINE.findall(text)
    assert RD.declared_purposes(text) == set() or not RD.declared_purposes(text)
    flat = " ".join(text.replace("**", "").split())
    assert "This search carries no `Judged-block reads:` line; the held-out test's declaration carries it." in flat
    assert "`heldout-finalists: F-HT @ <its LF sha256> list <the joint list's sha256>`" in flat
    assert "Keep the house names" not in text
    # the house purposes the held-out test's declaration names are valid reader purposes, none choosing
    for purpose in ("heldout_test", "heldout_stress"):
        assert f"`{purpose}`" in text
        assert RD.PURPOSE.fullmatch(purpose)
        assert not set(re.split(r"_+", purpose)) & RD.CHOICE_WORDS


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

#: B-1: every copy of the redraw's law races the cushion less the stop-side exit cost, fractional, never rounded
#: (E-237; text v2 -- the first text's inward rounding was the stranded-account defect).
RACE_COPIES = (
    "prereg/TEMPLATE_design_search.md",
    ".claude/agents/prereg-gatekeeper.md",
    ".claude/agents/red-team.md",
    ".claude/skills/merge-checklist/SKILL.md",
    ".claude/skills/feature-rules/SKILL.md",
    ".claude/skills/contract-engine/SKILL.md",
    ".claude/skills/prereg-discipline/SKILL.md",       # cycle 2, n-4
    ".claude/agents/auditor.md",                       # cycle 2, n-4 (its description line too)
)


def test_every_copy_of_the_race_law_uses_the_cushion_less_the_stop_side_cost():
    for rel in RACE_COPIES:
        text = _text(ROOT / rel)
        assert "min(l, c - x_stop)" in text, rel
        flat = " ".join(text.replace("**", "").split())
        assert "never rounded" in flat, rel
        assert "not taken" not in flat.replace('no "not taken" state', ""), rel     # B-2: no such state
        inward = [m.start() for m in re.finditer("rounded inward", text)]
        if rel == "prereg/TEMPLATE_design_search.md":           # only m-2's shared path rounds inward (N-4)
            m2 = text[text.index("- **m-2 (E-210)"):text.index("- **m-3 (E-210)")]
            assert all(text.index(m2) <= k < text.index(m2) + len(m2) for k in inward), inward
        else:
            assert not inward, rel
        assert not re.search(r"min\(l, c\)", text), rel          # the full-cushion form B-1 rules out
        assert "uses BinaryDraw's law" not in text, rel
        for line in text.splitlines():                  # n-4: no paraphrase of the law without its cost
            if "nearer barrier" in line and not re.search(r"x_stop|exit cost|net of|cost-free", line):
                nxt = text[text.index(line):][:400]
                assert re.search(r"x_stop|exit cost|net of|cost-free", nxt), (rel, line)
    desc = _text(CLAUDE_DIR / "agents" / "auditor.md").split("\n")[2]
    assert desc.startswith("description:") and "stop-side exit cost" in desc


def test_the_template_states_the_costed_race_and_r10_walk_exactly():
    text = _text(TEMPLATE)
    sec = text[text.index("## 5. The zero-edge convention"):text.index("## 6. The survey")]
    for s in ("L = min(l, c - x_stop)", "p = L / (L + g)", "L <= 0", "the cost-free special case", "x = 0",
              "`stop_slippage_ticks`", "`flatten_slippage_ticks`", "never rounded", "net expectation",
              "two-point race", "booked as failed at the fill", "counted apart",
              "minus its costs", "the clip never binds", "the runner's rule", "fill-time law",
              "n = round(sigma^2 T / s^2)", "overrides", "convexity", "underlying"):
        assert s in sec, s
    assert "slipping a tick" not in sec, "a rule value typed: cite fills.yaml's key"


#: m-1 (ii): every terminal state of a run trade has its law, in one table.
TERMINAL_STATES = ("target", "stop", "stop gapped through", "the floor or the daily loss limit",
                   "a profit level set by a rule", "15:10 CT flatten", "news window", "max hold", "any other exit")


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
    for s in ("after every finalists' row and the held-out row", "once per market", "Q-158",
              "no `Judged-block reads:` line", "registered_design", "five-minute cell", "path-structure edge",
              "denial ladder", "trigger side's held-out reading"):   # E-221: the model side is the trigger side
        assert s in run, s
    gk = _text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md")
    for s in ("results/read_ledger.jsonl", "an RD declaration naming any held-out purpose", "Q-158",
              "registered_design"):
        assert s in gk, s
    au = _text(CLAUDE_DIR / "agents" / "auditor.md")
    for s in ("`heldout_*`", "registered_design", "single use per market"):
        assert s in au, s


def test_the_long_run_gate_reads_as_e221_ruled_o6():
    """B-4, then E-221 (O-6, option (a)): the gate's quantile over coin seeds on the held-out years, the search years'
    history-block reading beside as a consistency condition -- in section 7's row, in 10 (c) and in O-6's line, as
    CHARTER 3.8 (c) now reads (wt/wt-infra f52c1f3)."""
    text = _text(TEMPLATE)
    flat = " ".join(text.replace("**", "").split())                  # the phrase may wrap or carry bold
    assert flat.count("over coin seeds on the held-out years") >= 3
    assert flat.count("consistency condition") >= 3
    assert "over coin seeds, given the history" not in text
    assert "coin seeds and history-block resamples" not in text      # the pre-E-221 charter wording, now replaced
    o6 = text[text.index("**O-6"):]
    o6 = o6[:o6.index("\n\n")]
    for s in ("ruled (E-221)", "option (a)", "consistency condition"):
        assert s in o6, s
    gk = _text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md")
    assert "O-6" in gk and "refuse to approve for a pin until O-6 is ruled" not in gk


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


# ============================================================================================ F. corrective cycle 2
# (docs/reviews/TEMPLATE_AGENTS_v2_2026-11-18.md: N-1, N-2, n-1 to n-6, under the coordinator's rulings)

from fractions import Fraction as Fr


def _r10_section() -> str:
    text = _text(TEMPLATE)
    return text[text.index("- **R-10:"):text.index("- **The pair rule**")]


def _l_fill(l, c, x_stop, x_flat):
    """The template's fill rule (N-1, text v2): L_fill = min(l, c - max(x_stop, x_flat)), fractional, never rounded."""
    return min(Fr(l), Fr(c) - max(Fr(x_stop), Fr(x_flat)))


WALK_EXITS = ("15:10 CT flatten", "news window", "max hold", "any other exit")


def _fate(l, c, x_stop, x_flat, exit_, binds="floor"):
    """A trade's fate as the template's R-10 writes it, given the run's exit (which only picks the law): decided at
    the fill by L_fill; the law's own barrier used only for a taken trade."""
    lf = _l_fill(l, c, x_stop, x_flat)
    if lf <= 0:
        return ("failed at the fill" if binds == "floor" else "day stopped"), None
    # both laws race the floor side at L_race (m-1, the runner's booking); the fill's decision is L_fill's
    return ("walk" if any(w in exit_ for w in WALK_EXITS) else "race"), min(Fr(l), Fr(c) - Fr(x_stop))


def _fate_by_law(l, c, x_stop, x_flat, exit_):
    """The defect N-1 rules out (the runner's m-1 at adedf7f): the take read from the exit's own law."""
    walk = any(w in exit_ for w in WALK_EXITS)
    bar = min(Fr(l), Fr(c) - (max(Fr(x_stop), Fr(x_flat)) if walk else Fr(x_stop)))
    return ("walk" if walk else "race") if bar > 0 else "failed at the fill"


def test_n1_everything_is_decided_at_the_fill_whatever_the_exit():
    sec = _r10_section()
    assert "L_fill = min(l, c - max(x_stop, x_flat))" in sec
    assert "at the fill" in sec and "whatever its later exit" in sec
    assert "per trade (S-1)" in sec and "`WALK_MAX`" in sec                    # the lattice step, declared
    assert "not taken" not in sec.replace('no "not taken" state', "")
    exits = [r.split("|")[1].strip() for r in sec[sec.index("| terminal state in the run |"):].split("\n\n")[0]
             .splitlines()[2:] if r.strip().startswith("|")]
    assert len(exits) == len(TERMINAL_STATES)
    for l in (8, 20, 40):
        for c in (Fr(1, 3), Fr(9, 10), Fr(5, 2), Fr(19, 1), Fr(77, 4), Fr(60)):
            for xs, xf in ((Fr(1), Fr(1)), (Fr(3, 2), Fr(1)), (Fr(2, 5), Fr(6, 5))):
                fates = {e: _fate(l, c, xs, xf, e) for e in exits}
                taken = {e: f[0] in ("race", "walk") for e, f in fates.items()}
                assert len(set(taken.values())) == 1, (l, c, xs, xf, fates)   # alike whatever the exit
                for e, (kind, bar) in fates.items():
                    if bar is not None:
                        x = xs                                          # a barrier loss pays the stop's cost
                        assert bar > 0 and -bar - x >= -c                       # never past the floor
    # positive control: probe 1 of the third read (tick 5, e = x_stop = 2 dollars, x_flat = 6, room half a tick above
    # e + x_stop) -- the law-by-exit rule takes it as a race and fails it as a walk; the template's rule does not
    xs, xf, c = Fr(2, 5), Fr(6, 5), Fr(2, 5) + Fr(1, 2)
    assert {_fate_by_law(20, c, xs, xf, e) for e in ("its stop", "the 15:10 CT flatten")} == {"race",
                                                                                           "failed at the fill"}
    assert {_fate(20, c, xs, xf, e)[0] for e in ("its stop", "the 15:10 CT flatten")} == {"failed at the fill"}


def test_b2_no_account_is_left_alive_and_unable_to_trade():
    """B-2: an account at floor room e + max(x_stop, x_flat) - epsilon is failed at the fill; one at + epsilon takes
    the race (e the entry cost; c = room - e). Where the daily loss limit binds, the day stops instead."""
    e, xs, xf = Fr(2, 5), Fr(2, 5), Fr(6, 5)
    for eps in (Fr(1, 10**6), Fr(1, 7), Fr(1, 2)):
        below, above = e + max(xs, xf) - eps, e + max(xs, xf) + eps
        assert _fate(20, below - e, xs, xf, "its stop")[0] == "failed at the fill"
        assert _fate(20, above - e, xs, xf, "its stop")[0] == "race"
        assert _fate(20, below - e, xs, xf, "its stop", binds="dll")[0] == "day stopped"
    sec = _r10_section()
    for s in ("booked as failed at the fill", "the race's own limit as L goes", "counted apart",
              "the day stops", "no account is ever left alive"):
        assert s in " ".join(sec.replace("**", "").split()), s


def _walk_mean_and_floor(g, L, n):
    """The template's walk on the unit lattice from 0, its barriers +g and -L possibly fractional: from x the up move
    goes du = min(1, g - x) and the down move dd = min(1, x + L), up with probability dd / (du + dd) -- so a plain
    point steps +-1 at one half, the last point above -L (rho below) goes down to -L with probability 1 / (1 + rho),
    and a point within one step of both barriers goes up with probability rho_d / (rho_u + rho_d) (m-2). Stopped at a
    barrier or after n steps. Returns (the exact mean, the set of floor-side exits)."""
    g, L = Fr(g), Fr(L)
    dist = {Fr(0): Fr(1)}
    mean, lows = Fr(0), set()
    for _ in range(n):
        nxt = {}
        for x, pr in dist.items():
            du, dd = min(Fr(1), g - x), min(Fr(1), x + L)
            for y, q in ((x + du, dd / (du + dd)), (x - dd, du / (du + dd))):
                if y >= g or y <= -L:
                    mean += pr * q * y
                    if y <= -L:
                        lows.add(y)
                else:
                    nxt[y] = nxt.get(y, Fr(0)) + pr * q
        dist = nxt
    mean += sum(x * pr for x, pr in dist.items())
    return mean, lows


def test_b1_the_walk_with_a_fractional_barrier_is_exactly_driftless_and_lands_on_the_floor():
    """E-237's forced-loss toy as the template's exact-fraction case: zero mean at a fractional barrier, and a
    floor-side loss ending exactly at -L_fill, so with the cost it lands on the floor (c - max x = L_fill)."""
    for g in (Fr(1, 3), Fr(3, 4), 3, 5, 8):                         # a fractional g' under one step: m-2's case
        for L in (Fr(37, 3), Fr(7, 2), Fr(5, 4), Fr(1, 2), Fr(4)):
            for n in (1, 4, 9, 15):
                mean, lows = _walk_mean_and_floor(g, L, n)
                assert mean == 0, (g, L, n, mean)
                assert lows <= {-L}, lows
    xs, xf, c = Fr(2, 5), Fr(6, 5), Fr(77, 10)
    race_l = min(Fr(40), c - xs)                                    # m-1: the walk's floor side is L_race
    assert -race_l - xs == -c                                       # a floor-bound barrier loss lands on the floor
    assert -(race_l - Fr(1, 10)) - xf < -c                          # a time exit near it: the flatten clip binds


def test_n2_a_rule_exit_at_a_profit_level_takes_the_race_at_the_as_placed_target():
    sec = _r10_section()
    table = sec[sec.index("| terminal state in the run |"):].split("\n\n")[0]
    row = next(r for r in table.splitlines() if "a profit level set by a rule" in r)
    assert "the race" in row and "min(g, level)" in row and "`cap`" in row and "need=x" in row
    other = next(r for r in table.splitlines() if "any other exit" in r)
    assert "a rule's exit" not in other
    text = _text(TEMPLATE)
    assert "g is always the target as placed" in text


def test_cycle2_minors_are_carried():
    text = _text(TEMPLATE)
    run = text[text.index("## 14. The run order"):text.index("## 15.")]
    assert "CHARTER 3.7" in run and "the lead's CHARTER 3.7 reading row" in run                                    # n-1
    assert "the final text with section 7's values filled in" in run                                   # n-2
    assert "E-222" in run and "heldout-finalists: F-NN @ <sha> list <sha>" in run                       # n-3, m-6
    assert "held by the declaration and the auditor" in run
    assert "is merged (E-222)" in run and "No design search pins before Q-158 merges" not in run      # m-6
    assert "queued" not in run.split("Q-158")[1][:40]
    gk = _text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md")
    assert "heldout-finalists: F-NN @ <sha> list <sha>" in gk and "merged, E-222" in gk
    assert "before Q-158 merges" not in gk and "reading row of CHARTER 3.7" in gk                        # m-6, m-9
    assert "(queued for wt-verify)" not in gk
    sec5 = text[text.index("## 5. The zero-edge convention"):text.index("## 6. The survey")]
    pair = sec5[sec5.index("- **The pair rule**"):]
    fr = _text(CLAUDE_DIR / "skills" / "feature-rules" / "SKILL.md")
    for s in ("as-walked leg's settled outcome", "difference is exactly zero"):                      # n-5
        assert s in pair and s in fr, s
    sec9 = text[text.index("## 9. Calibration"):text.index("## 10. The pass line")]
    assert "cites that record" in sec9 and "fresh seed block" in sec9                                  # n-6
    assert "fresh seed block" in gk


# ============================================================================================ G. E-221 (the operator's
# open items ruled; the constitution aligned on wt/wt-infra f52c1f3) and E-223's M-4 news-flatten convention

#: wording the rulings retired: none may remain as the template's rule
E221_RETIRED = (
    "pending the operator, O-4", "Until O-4 is", "the operator's (Wave 4.2)", "the operator's trade-off answers",
    "a margin wider than its noise", "O-5**'s pending form", "O-5's pending form", "only if the operator sets one",
    "Which firm's\n  search spends them", "the operator's, open", "Wave 4.2's operator inputs", "and O-1 and O-6 ruled",
    "the model-side reading",
)


def test_e221_rulings_are_in_the_template_each_marked():
    text = _text(TEMPLATE)
    left = [s for s in E221_RETIRED if s in text]
    assert not left, left
    for needle in (
        "one joint fixed-sequence test",                                   # O-1
        "Topstep, My Funded Futures and Lucid",
        "built, tuned and chosen on the search years only",
        "sets one as a limit, E-221",                                       # the workload ceiling
        "The coin is the evaluation's device, not the",                     # O-4
        "Accounts alternate:", "The one hard rule", "the per-start keying is kept",
        "the lead's, from H4's search-year results by a rule declared before H4 is read (E-221)",   # Wave 4.2
        "The point estimate governs",                                       # O-5 (E-230)
        "the lead's, from the baselines' search-year results (E-221)",     # O-3
        "O-6, ruled (E-221): option (a)",                                   # O-6
        "The playbook trigger side's held-out reading (E-221, O-4",         # the verdict's beside line
    ):
        assert needle in _flat(text), needle                       # whitespace- and bold-insensitive
    # each paragraph carrying a ruling names E-221
    for para in text.split("\n- "):
        if any(s in para for s in ("one joint fixed-sequence test", "Accounts alternate", "O-6, ruled",
                                   "The point estimate governs")):
            assert "E-221" in para, para[:120]


def test_e223_m4_one_news_flatten_convention():
    text = _text(TEMPLATE)
    row = next(r for r in text.splitlines() if r.strip().startswith("| no entry and no fill inside a verified news"))
    for s in ("E-223 M-4", "every source", "adverse extreme of the window's first bar less two ticks",
              "resting stop instead if that extreme reaches it", "E-223 M-8"):
        assert s in row, s


# ============================================================================================ H. the lead's rulings on
# the two open points (E-230: O-5, the point estimate governs; the joint held-out test its own declaration)

#: the pre-E-230 O-5 wording -- a one-sided check that decides -- gone from every copy
O5_RETIRED = ("failing one only when the evidence shows it crosses", "fails a limit only when the evidence shows",
              "failing only when the one-sided check shows", "the single margin, applied once",
              "the single margin applied once")
O5_COPIES = ("prereg/TEMPLATE_design_search.md", ".claude/agents/prereg-gatekeeper.md", ".claude/agents/auditor.md",
             ".claude/skills/prereg-discipline/SKILL.md")


def test_e230_the_point_estimate_governs_every_limit():
    for rel in O5_COPIES:
        text = _text(ROOT / rel)
        flat = " ".join(text.replace("**", "").split())
        left = [s for s in O5_RETIRED if s in flat]
        assert not left, (rel, left)
        assert "point estimate governs" in flat, rel
        assert "never a second margin" in flat, rel
    text = _text(TEMPLATE)
    sec10 = text[text.index("## 10. The pass line"):text.index("## 11.")]
    a = sec10[sec10.index("- **(a) Limits"):sec10.index("- **(b)")]
    for s in ("E-230", "passes a limit when its point estimate is inside it", "fails it when the estimate is outside",
              "reported beside each limit"):
        assert s in " ".join(a.replace("**", "").split()), s
    row = next(r for r in text.splitlines() if r.startswith("| **the limits**"))
    assert "E-230" in row and "point estimate governs" in row and "reported beside" in row


def test_e230_the_joint_held_out_test_is_one_declaration_of_its_own():
    text = _text(TEMPLATE)
    flat = lambda s: " ".join(s.replace("**", "").split())
    sec = {
        "2": text[text.index("## 2. Years"):text.index("## 3. The lever space")],
        "10": text[text.index("## 10. The pass line"):text.index("## 11.")],
        "13": text[text.index("## 13. The count"):text.index("## 14.")],
        "14.8": text[text.index("8. **The held-out row**"):text.index("9. **The verdict row**")],
    }
    for name, body in sec.items():
        f = flat(body)
        assert "the held-out test's declaration" in f, name
        assert "E-238" in f, name                                          # m-7
    for s in ("one declaration of its own", "lists every firm's finalists", "fixes the joint order", "takes the k",
              "the one family that reads NQ's held-out window", "Q-158's rule"):
        assert s in flat(sec["2"]), s
    gk = flat(_text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"))
    for s in ("the held-out test's declaration", "one declaration of its own", "the one family that reads NQ's held-out window"):
        assert s in gk, s


# ============================================================================================ I. text v2 (the red team's
# third read: B-4, m-3, m-4, m-8, m-10; the version)


def test_v2_the_playbook_side_is_held_by_its_no_harm_floor():
    """B-4: CHARTER 3.5's no-harm floor for the playbook's trigger side, in its own words, read on the search years
    before the finalists' row, a failing design not carried -- in section 4 and 10 (c); section 11 only its held-out
    reading; the gatekeeper's item 4 too."""
    text = _text(TEMPLATE)
    f = lambda s: " ".join(s.replace("**", "").split())
    s4 = f(text[text.index("## 4. The component schedule"):text.index("## 5. The zero-edge")])
    s10 = f(text[text.index("## 10. The pass line"):text.index("## 11.")])
    s11 = f(text[text.index("## 11."):text.index("## 12.")])
    for body in (s4, s10):
        assert "offers no playbook side" in body and "not carried" in body and "before the finalists' row" in body
        assert "on the search years" in body
    assert ("its composite on the search years is not below the coin side's by more than the margin pinned in "
            "section 7") in s4
    assert "trigger side's held-out reading" in s11
    gk = f(_text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"))
    assert "a trigger whose side fails it offers no playbook side; that design is not carried" in gk


def test_v2_minors():
    text = _text(TEMPLATE)
    f = " ".join(text.replace("**", "").split())
    assert "Text v2 (2026-11-20)" in text and "1a9be8c" in text                      # the re-declaration
    assert "net ticks after the target-side cost" in f                                # m-3
    news = next(r for r in text.splitlines() if "| a news window's start" in r)
    assert "declared reading" in news and "printed beside" in news and "E-223 M-4" in news   # m-4
    rt = " ".join(_text(CLAUDE_DIR / "agents" / "red-team.md").split())
    assert "decided at the fill" in rt and "profit level" in rt and "never rounded" in rt   # m-8
    for rel in ("commands/brief.md", "commands/status.md"):
        assert "E-230" in _text(CLAUDE_DIR / rel), rel                                # m-10


# ============================================================================================ J. text v2, corrective
# cycle 1 (the red team's full read TEMPLATE_V2_FULL_2026-11-20: C-1, M-1 to M-4, m-1 to m-8)

HT = ROOT / "prereg" / "TEMPLATE_heldout_test.md"


def _flat(s: str) -> str:
    return " ".join(s.replace("**", "").split())


def _section(text: str, start: str, end: str) -> str:
    i = text.index(start)
    return _flat(text[i:text.index(end, i + 1)])


def _slot(room, rpc_this, rpc_min, max_contracts=20):
    """C-1's rule as Stage 2's D-318 reads it (`sizing.py`'s smallest offered stop; the re-read's m-1): a floor room
    under one contract's risk at the smallest stop the design can place ends the account out of room; above it, a
    zero at this trade's own stop is a no-trade slot."""
    if 0 < room < rpc_min:
        return "out of room"
    n = min(max_contracts, int(Fr(room) // Fr(rpc_this)))
    return "no-trade slot" if n == 0 else n


def test_c1_zero_contracts_at_a_positive_room_ends_out_of_room():
    rpc_min, rpc_this = Fr(10), Fr(20)                           # one micro's risk at the smallest and this stop
    for eps in (Fr(1, 10**6), Fr(1, 3)):
        assert _slot(eps, rpc_this, rpc_min) == "out of room"                # just above zero
        assert _slot(rpc_min - eps, rpc_this, rpc_min) == "out of room"      # just under one micro at the smallest
        assert _slot(rpc_min + eps, rpc_this, rpc_min) == "no-trade slot"    # buys a micro only at a smaller stop
        assert _slot(rpc_this + eps, rpc_this, rpc_min) == 1                 # one micro at this stop
    text = _text(TEMPLATE)
    sec5 = _section(text, "## 5. The zero-edge", "## 6. The survey")
    for s in ("Zero contracts at a positive room (C-1): the account ends out of room", "D-318, D-335",
              "the smallest stop the design can place at the account's state",
              "Above that room, a zero at this trade's own stop is a no-trade slot",
              "it is failed, counted apart beside the at-the-fill failures, its share printed beside the verdict, and "
              "replaced as a breach is",
              "the declaration shows that state is not absorbing, or the design is refused",
              "a room just above zero but under one micro's risk at the smallest offered stop ends out of room",
              "So no account is ever left alive, billed and unable to trade, at a fill or at a slot"):
        assert s in sec5, s
    for bad in ("kept alive", "not replaced"):
        assert bad not in sec5, bad
    sec3 = _section(text, "## 3. The lever space", "## 4.")
    for s in ("S3's and S4's whole-micro room cut", "A1's flip", "A17's sizing", "Section 5's out-of-room rule ends "
              "that account"):
        assert s in sec3, s
    for rel in RACE_COPIES:
        assert "out of room" in _flat(_text(ROOT / rel)), rel
    assert "refuse a draft with a room cut (S3, S4, A1, A17) and no out-of-room rule" in _flat(
        _text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"))


def _step(sigma_root_t, walk_max):
    """S-1's rule: the smallest whole-tick step keeping n <= walk_max, s = max(1, ceil(sigma sqrt(T) / sqrt(walk_max)));
    never refused."""
    from math import ceil, sqrt

    return max(1, ceil(sigma_root_t / sqrt(walk_max)))


def _p_stop(l, g, s, n):
    """The walk's P(floor-side exit) in floats on the lattice of step s ticks from 0, barriers -l and +g in ticks,
    fractional in lattice units (the two-point last sub-steps), n steps."""
    lo, hi = -Fr(l) / s, Fr(g) / s
    dist, p_stop = {Fr(0): 1.0}, 0.0
    for _ in range(n):
        nxt = {}
        for x, pr in dist.items():
            du, dd = min(Fr(1), hi - x), min(Fr(1), x - lo)
            q_up = float(dd / (du + dd))
            for y, q in ((x + du, q_up), (x - dd, 1.0 - q_up)):
                if y <= lo:
                    p_stop += pr * q
                elif y < hi:
                    nxt[y] = nxt.get(y, 0.0) + pr * q
        dist = nxt
    return p_stop


def test_s1_the_lattice_step_is_the_smallest_admissible_and_never_refuses():
    from math import sqrt

    assert _step(sqrt(400), 1024) == 1 and round(400 / 1 ** 2) == 400          # the read's case: one tick, n = 400
    assert _step(8 * sqrt(2), 1024) == 1                                         # two minutes before the flatten
    assert _step(96, 1024) == 3 and round(96 ** 2 / 9) == 1024                   # n held at the limit
    for root in (1, 31.9, 32, 32.1, 64, 200, 1000):
        s = _step(root, 1024)
        assert s >= 1 and round(root ** 2 / s ** 2) <= 1024                     # never refused, n within the limit
    # the probe case: a coprime bracket, s = 2 at n = 1024 against the one-tick lattice at n = 4096 (exact laws)
    p2, p1 = _p_stop(37, 55, 2, 1024), _p_stop(37, 55, 1, 4096)
    assert abs(p2 - p1) < 0.02, (p2, p1)
    sec = _flat(_r10_section())
    for s in ("s = max(1, ceil(sigma sqrt(T) / sqrt(`WALK_MAX`))) ticks", "It need not divide the stop or the target",
              "A trade is never refused for its step", "the fill-time law's T"):
        assert s in sec, s
    for bad in ("largest whole number of ticks", "The lattice step s is one tick", "the trade is refused"):
        assert bad not in sec, bad
    gk = _flat(_text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"))
    assert "the lattice step s per trade (S-1)" in gk and "refuse any other s" in gk
    assert "largest whole number of ticks" not in gk


def test_m1_the_held_out_test_has_its_own_form():
    from extended import reader as RD

    text = _text(HT)
    f = _flat(text)
    name = HT.name
    assert not RD.F_ID.match(name) and not RD.DECLARATION_PATH.fullmatch(f"prereg/{name}")
    matching = [g for g in _test_globs() if fnmatch.fnmatch(name, g) or fnmatch.fnmatch(f"prereg/{name}", g)]
    assert set(matching) <= {"*.md", "*", "**/*.md"}, matching
    assert "\r\n" not in text and not re.search(r"\b\d{6,8}\b", text) and not re.search(r"\$\s?\d", text)
    for s in ("Declaration kind: held-out test",
              "Its inputs come only from the pinned searches' finalists' lists, each by its sha256",
              "Anything new -- a reading, a baseline, a floor relaxed, a statistic, a seed, code -- is refused",
              "the order alternates by rank across the firms (H-2): rank 1 of Topstep, rank 1 of My Funded Futures "
              "(MFFU), rank 1 of Lucid, then rank 2 of each in the same firm order, and so on; a firm whose list is "
              "exhausted is skipped",
              "A firm's ranks are the search's own pinned finalist order",
              "before any search is declared", "A researcher's choice after a read is never the order",
              "listed as none and keeps its place",
              "This declaration is written as soon as every firm is in a terminal state",
              "`heldout-finalists: F-HT @ <its LF sha256> list <the joint list's sha256>`",
              "the pin and the token in one row are refused", "its power at this place (independence)",
              "Exit (B) cites this table", "This declaration chooses nothing",
              "one-sided level 0.05 / (k (k + 1))", "in the joint order, stopping at the first failure",
              "A fail at a place: the sequence stops there; every later finalist is untested",
              "Each read is made once", "No repeat row", "a seed, code -- is refused.",
              "A runner without that identity refuses the run."):
        assert s in f, s
    for bad in ("may re-order", "waits for its successor", "moves on to the next firm", "may be repeated",
                "skipping any failure", "0.05 / k ", "when the lead decides"):
        assert bad not in f, bad
    rows = f[f.index("## 5. The rows, in order"):f.index("## 6.")]
    order = [rows.find(s) for s in ("The pin row", "The held-out row, which is its finalists' token row (m-3), newer "
                                    "than the pin row", "The held-out test", "The verdict row")]
    assert all(i >= 0 for i in order) and order == sorted(order), order
    lines = RD.DECLARED_LINE.findall(text)
    assert len(lines) == 1 and RD.PURPOSE_TOKEN.findall(lines[0]) == ["heldout_test", "heldout_stress"], lines
    gk = _flat(_text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"))
    ht_items = gk[gk.index("## The held-out test's declaration"):gk.index("## k: counted")]
    for s in ("## The held-out test's declaration (`prereg/TEMPLATE_heldout_test.md`; M-1)", "Refuse anything new",
              "with `heldout_test` and `heldout_stress` only.",
              "alternating by rank across the firms in the order Topstep, My Funded Futures (MFFU), Lucid",
              "5. Written only when every firm is in a terminal state",
              "keeps its place", "Refuse a pin and a token in one row, and any repeat row for F-HT",
              "Each finalist's power re-stated at its place"):
        assert s in ht_items, s
    for bad in ("any other purpose", "when the lead decides"):
        assert bad not in ht_items, bad
    assert "in the joint order by the rule fixed in `prereg/TEMPLATE_heldout_test.md` (M-1)" in _flat(_text(TEMPLATE))


MARK_SEARCH, MARK_HT = "Declaration kind: design search", "Declaration kind: held-out test"
HT_HEADINGS = ("## 1. Its inputs", "## 2. The joint order", "## 3. The firms' states", "## 5. The rows, in order",
               "## 6. Power at each place")


def _line_problems(name: str, text: str) -> list:
    """M-2's scan with the re-read's m-2: a design search never carries a `Judged-block reads:` line; a new declaration
    (F-13 on, or any draft) with one must be held-out-marked; a held-out-marked file names exactly the two house
    purposes, carries the held-out template's headings and not the design-search marker."""
    from extended import reader as RD

    purposes, f = RD.declared_purposes(text), _flat(text)
    out = []
    if MARK_SEARCH in f and purposes:
        out.append(f"{name}: a design search carries a Judged-block reads line {sorted(purposes)}")
    m = re.match(r"(?:DRAFT_)?F-(\d+|XX)", name)
    new = bool(m) and (m.group(1) == "XX" or int(m.group(1)) >= 13)
    if purposes and new and MARK_HT not in f:
        out.append(f"{name}: a new declaration with a Judged-block reads line is not the held-out test's")
    if MARK_HT in f:
        if set(purposes) != {"heldout_test", "heldout_stress"}:
            out.append(f"{name}: a held-out-marked file names {sorted(purposes)}")
        if MARK_SEARCH in f:
            out.append(f"{name}: carries both markers")
        if not all(h in f for h in HT_HEADINGS):
            out.append(f"{name}: held-out-marked without the held-out template's headings")
    return out


def test_m2_no_search_declaration_draft_or_pinned_carries_a_judged_block_line():
    problems, ht_files = [], []
    for pth in sorted((ROOT / "prereg").glob("*.md")):
        if pth.name.startswith("TEMPLATE_"):
            continue
        problems += _line_problems(pth.name, _text(pth))
        if MARK_HT in _flat(_text(pth)) and pth.name.startswith("F-"):
            ht_files.append(pth.name)
    assert not problems, problems
    assert len(ht_files) <= 1, ht_files                                   # at most one held-out-marked F- file (NQ)
    assert not _line_problems("DRAFT_F-XX_x.md", _text(TEMPLATE)) and not _line_problems("DRAFT_F-XX_h.md", _text(HT))
    # positive controls
    bad = "**Declaration kind: design search.**\n\n- **Judged-block reads:** `stage_C_judgement`\n"
    assert _line_problems("DRAFT_F-XX_bad.md", bad)
    assert _line_problems("F-14_bad.md", "- **Judged-block reads:** `heldout_test`\n")
    assert not _line_problems("F-03_old.md", "- **Judged-block reads:** `stage_C_judgement`\n")   # pinned before
    ht_ok = _text(HT)
    assert _line_problems("F-15_x.md", ht_ok.replace("`heldout_test`, `heldout_stress`",
                                                     "`heldout_test`, `heldout_stress`, `late_block_description`"))
    assert _line_problems("F-15_y.md", ht_ok.replace("`heldout_test`, `heldout_stress`", "`late_block_description`"))
    assert _line_problems("F-16_z.md", ht_ok + "\n**Declaration kind: design search.**\n")
    assert _line_problems("F-17_w.md", "**Declaration kind: held-out test.**\n\n- **Judged-block reads:** "
                                       "`heldout_test`, `heldout_stress`\n")
    # the gatekeeper's refusal, held (the full read's J2, J3)
    gk = _flat(_text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"))
    item1 = gk[gk.index("1. Years and the held-out read ledger"):gk.index("2. The confirmation window")]
    assert "A search declaration carries no `Judged-block reads:` line" in item1
    assert "may carry a `Judged-block reads:` line" not in gk
    refuse = item1[item1.index("Refuse:"):]
    assert refuse.startswith("Refuse: - a search draft that carries a `Judged-block reads:` line"), refuse[:120]
    t = _flat(_text(TEMPLATE))
    assert ("Declaration kind: design search. A declaration drafted on this template keeps this line. It never "
            "carries a `Judged-block reads:` line;") in t                 # the re-read's J5, J6


#: M-4: the rule-carrying phrases each mutant of the full read touched, each in its own section (flattened)
RULE_NEEDLES = (
    ("## 5.", "## 6.", "L_fill <= 0 where the floor's room binds (B-2): the account is booked as failed at the fill"),
    ("## 5.", "## 6.", "L_fill <= 0 where the daily loss limit's room binds: the day stops"),
    ("## 5.", "## 6.", "e + max(x_stop, x_flat) - epsilon (e the entry cost) is failed; one at e + max(x_stop, x_flat) "
                       "+ epsilon takes the race"),
    ("## 5.", "## 6.", "its floor-side barrier is L_race = min(l, c - x_stop)"),
    ("## 5.", "## 6.", "a step goes down to -L_race with probability s / (s + rho), else up one step s"),
    ("## 5.", "## 6.", "So a loss plus its exit cost never passes the floor and the clip never binds"),
    ("## 4.", "## 5.", "The floor is read on the search years, before the finalists' row; a failing design is removed "
                       "from the finalists' list then"),
    ("## 4.", "## 5.", "is not below the coin side's by more than the margin pinned in section 7"),
    ("## 10.", "## 11.", "the trigger side's composite on the search years not below the coin side's by more than the "
                         "pinned margin, read before the finalists' row"),
    ("## 9.", "## 10.", "If any fails, the search goes no further -- no go row, no survey"),
    ("## 9.", "## 10.", "it is never re-run with another seed"),
    ("## 6.", "## 7.", "The number of rounds is fixed here and never extended after a look"),
    ("## 6.", "## 7.", "The gates read before any outcome"),
    ("## 2.", "## 3.", "a start is read at horizon h only if h sessions remain in its own years"),
    ("## 12.", "## 13.", "the held-out test's coin field -- disjoint from every seed drawn on the search years"),
    ("## 13.", "## 14.", "One k per held-out test at 0.05 / (k (k + 1))"),
    ("## 14.", "## 15.", "it carries the `Judged-block reads:` line"),
    ("## 14.", "## 15.", "Nothing of this search reads the held-out years."),
    ("## 10.", "## 11.", "which fixes the order across the firms before the held-out read"),
)


def test_m4_every_rule_carrying_phrase_is_held_in_its_section():
    text = _text(TEMPLATE)
    for a, b, needle in RULE_NEEDLES:
        assert needle in _section(text, a, b), (a, needle)
    flat = _flat(text)
    for bad in ("not significantly below", "may be extended", "may reuse", "may be re-run", "after the outcomes",
                "proceeds, its power", "after the held-out read", "reads the five-minute cell on the held-out"):
        assert bad not in flat, bad
    gk = _flat(_text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"))
    assert "L_fill <= 0 where the floor's room binds books the account as failed at the fill" in gk
    assert "kept, the trade skipped" not in gk


#: the rule values the templates cite (percentages, and the program's level); any other figure is a typed number
ALLOWED_PCT = {"0 %", "5 %", "10 %", "20 %", "25 %", "90 %"}   # 90 %: CHARTER 4's realised-risk rule


def test_m4_no_typed_figure_in_either_template():
    for path in (TEMPLATE, HT):
        text = _text(path)
        pcts = {p.replace("%", " %").replace("  ", " ") for p in re.findall(r"\b\d+(?:\.\d+)? ?%", text)}
        assert pcts <= ALLOWED_PCT, (path.name, pcts - ALLOWED_PCT)
        assert set(re.findall(r"(?<![\w.])0\.\d+", text)) <= {"0.05"}, path.name
        assert not re.search(r"\b\d{3,}\s*(?:USD|dollars)\b", text), path.name
        assert not re.search(r"\$\s?\d", text), path.name
        units = r"(?:times|x\b|%|ticks?|points?|USD|dollars|designs?|sessions?|accounts?)"
        assert not re.search(r"\b\d+\.\d+\s*" + units, text), (path.name, re.findall(r"\b\d+\.\d+\s*" + units, text))
        assert not re.search(r"\b(?:is|are|was|be|=)\s+\d+\.\d+\b", text), path.name   # "of 3.8 (c)" is a section
        big = [int(n) for n in re.findall(r"(?<![\w.-])(\d{4,})(?![\w-])", text)]
        assert all(2000 <= n <= 2099 for n in big), (path.name, big)           # only years, outside dates and keys


def test_cycle1_minors():
    f = _flat(_text(TEMPLATE))
    assert "Where one lattice point is both the last above the floor-side barrier" in f                  # m-2
    assert "rho_d / (rho_u + rho_d)" in f
    assert "A daily loss limit at or below e + max(x_stop, x_flat)" in f and "refused at construction" in f  # m-3
    assert "The power gate, before the go row" in f and "The power gate, before the pin" not in f      # m-4
    assert "decided at the point estimate over `<S1>`'s seeds, paired on the same fills" in f           # m-5
    assert "never by a test that fails only on evidence of harm" in f
    for rel in (".claude/skills/feature-rules/SKILL.md", ".claude/skills/contract-engine/SKILL.md"):    # m-6
        c = _flat(_text(ROOT / rel))
        assert "L_fill = min(l, c - max(x_stop, x_flat))" in c and "where the daily loss limit binds" in c, rel
    au = _flat(_text(CLAUDE_DIR / "agents" / "auditor.md"))
    assert "F-HT, the one declaration that reads them" in au and "the joint order" in au
    assert "failed its no-harm floor before the finalists' row" in au
    for s in ("Three arms: (i) the B-2 rule only; (ii) (i) plus the out-of-room rule; (iii) the vendored engine's",
              "the invariant, zero in (ii)", "it chooses no lever"):                                       # m-8
        assert s in f, s
    assert "the runner receives g' in these gross ticks" in f                                           # n-1


# ============================================================================================ K. text v2, corrective
# cycle 2 (the red team's re-read TEMPLATE_V2_c1_2026-11-20: S-1, H-1, H-2, M-4, M-5, m-1 to m-6)

FIRMS = ("Topstep", "MFFU", "Lucid")
CAUSES = ("calibration-failed", "limit-clause-failed", "power-gate-failed", "every-design-failed-a-gate",
          "empty-finalist-list", "every-finalist-failed-no-harm", "withdrawn")


def _firm_states(events):
    """H-1's closed list from synthetic rows, in row order: ("pin", firm, search), ("finalists", firm, search, ranks),
    ("closed", firm, search, cause). Only a firm's latest pinned search counts. Returns {firm: (state, ranks)} with
    state 'a', 'b', 'c' or 'open' (a pinned search neither finalised nor closed: it blocks the declaration)."""
    latest, fin, closed = {}, {}, {}
    for ev in events:
        kind, firm, search = ev[0], ev[1], ev[2]
        assert firm in FIRMS, firm
        if kind == "pin":
            latest[firm] = search
        elif kind == "finalists":
            fin[search] = list(ev[3])
        elif kind == "closed":
            assert ev[3] in CAUSES, ev[3]
            closed[search] = ev[3]
    out = {}
    for firm in FIRMS:
        s = latest.get(firm)
        if s is None:
            out[firm] = ("c", [])
        elif s in fin:
            out[firm] = ("a", fin[s])
        elif s in closed:
            out[firm] = ("b", [])
        else:
            out[firm] = ("open", [])
    return out


def _joint_order(states):
    """H-2: alternate by rank across the firms in the fixed order; a firm whose list is exhausted is skipped."""
    lists = [(firm, states[firm][1]) for firm in FIRMS]
    order, rank = [], 0
    while any(rank < len(ranks) for _, ranks in lists):
        order += [(firm, ranks[rank]) for firm, ranks in lists if rank < len(ranks)]
        rank += 1
    return order


def _place_power(pis):
    """H-2's declared formula: the product of the earlier and its own powers at the full level (independence), and
    the Frechet lower bound beside."""
    out, prod, total = [], 1.0, 0.0
    for i, p in enumerate(pis, 1):
        prod, total = prod * p, total + p
        out.append((prod, max(0.0, total - (i - 1))))
    return out


def test_h1_the_firms_states_are_a_closed_list_decided_by_rule():
    ev = [("pin", "Topstep", "F-13"), ("closed", "Topstep", "F-13", "power-gate-failed"),
          ("pin", "Topstep", "F-15"), ("finalists", "Topstep", "F-15", ["t1", "t2"]),
          ("pin", "MFFU", "F-14"), ("finalists", "MFFU", "F-14", ["m1"])]
    st = _firm_states(ev)
    assert st == {"Topstep": ("a", ["t1", "t2"]), "MFFU": ("a", ["m1"]), "Lucid": ("c", [])}
    # a successor voids the earlier finalists: the latest search counts
    st2 = _firm_states(ev + [("pin", "MFFU", "F-16")])
    assert st2["MFFU"] == ("open", [])                                         # it blocks until closed or finalised
    st3 = _firm_states(ev + [("pin", "MFFU", "F-16"), ("closed", "MFFU", "F-16", "empty-finalist-list")])
    assert st3["MFFU"] == ("b", [])
    try:
        _firm_states([("pin", "Lucid", "F-17"), ("closed", "Lucid", "F-17", "the lead preferred to")])
        raise AssertionError("an unlisted cause was accepted")
    except AssertionError as e:
        assert "unlisted" not in str(e)
    ht = _flat(_text(HT))
    for s in ("The firms are fixed now: Topstep, My Funded Futures (MFFU), Lucid",
              "Only a firm's latest pinned search counts. An earlier search's finalists are void once a successor is "
              "pinned", "(a) finalists: its latest pinned search has a finalists' row",
              "(b) none: its latest pinned search has a closing row", "(c) none: no search of the firm was ever pinned",
              "`heldout-closed: F-NN @ <its LF sha256> -- <cause> -- <text>`",
              "After the third terminal state, no new search may be pinned until this declaration's held-out row is "
              "written", "A pinned search that is neither finalised nor closed blocks the declaration",
              "never waited out by choice"):
        assert s in ht, s
    causes = ht[ht.index("its cause one of a closed list"):ht.index("This declaration is written as soon as")]
    assert re.findall(r"\d\. `([a-z-]+)`", causes) == list(CAUSES), causes          # exactly the closed list
    gk = _flat(_text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"))
    assert "after the third firm's terminal state until F-HT's held-out row is written (H-1)" in gk


def test_h2_the_joint_order_alternates_by_rank_and_place_power_is_declared():
    st = {"Topstep": ("a", ["t1", "t2", "t3"]), "MFFU": ("b", []), "Lucid": ("a", ["l1"])}
    assert _joint_order(st) == [("Topstep", "t1"), ("Lucid", "l1"), ("Topstep", "t2"), ("Topstep", "t3")]
    st = {"Topstep": ("a", ["t1"]), "MFFU": ("a", ["m1", "m2"]), "Lucid": ("a", ["l1", "l2"])}
    assert [x for _, x in _joint_order(st)] == ["t1", "m1", "l1", "m2", "l2"]
    pw = _place_power([0.8, 0.8, 0.8])
    assert abs(pw[2][0] - 0.512) < 1e-9 and abs(pw[2][1] - 0.4) < 1e-9
    ht = _flat(_text(HT))
    for s in ("the three-way design note's power for finalist j at the level the sequence assigns to its place",
              "independence across finalists", "the power at place i is the product of pi_1 to pi_i",
              "the Frechet lower bound", "max(0, pi_1 + ... + pi_i - (i - 1))"):
        assert s in ht, s


RR = "E-NNN (the lead's CHARTER 3.7 reading row)"


def _pin_ready(text: str, decisions: str) -> list:
    """M-5: a design search pins only when the CHARTER 3.7 reading row is cited by a number that exists."""
    out = []
    if RR in text:
        out.append("the CHARTER 3.7 reading row is still a placeholder")
    for row in re.findall(r"(E-\d+) \(the lead's CHARTER 3\.7 reading row\)", text):
        if not re.search(rf"^\| {row} \|", decisions, re.M):
            out.append(f"{row} cited but not in DECISIONS.md")
    return sorted(set(out))


def test_m5_no_free_retry_and_the_reading_row_before_any_pin():
    text = _text(TEMPLATE)
    f = _flat(text)
    for s in ("A failed limit clause or power gate is never a free retry",
              "the successor inherits W42-R1's limits, bankroll budgets, weights and size that matters unchanged",
              "a change comes only by a decision row declared before any further search-year read, and is labelled",
              "every closed attempt of the line is counted and printed beside the verdict",
              "CHARTER 3.8 (a)'s \"a pinning row ... does not pin\"", "\"before any search is pinned\"",
              "the reader's pin and every \"newer than the pin\" mean the hash row",
              "No search pins while " + RR + " is a placeholder"):
        assert s in f, s
    assert "may re-set" not in f
    assert _pin_ready(text, "") == ["the CHARTER 3.7 reading row is still a placeholder"]   # the template refuses
    assert _pin_ready(text.replace("E-NNN (the lead", "E-999 (the lead"), "| E-999 | d | x |\n") == []
    assert _pin_ready(text.replace("E-NNN (the lead", "E-998 (the lead"), "") == ["E-998 cited but not in DECISIONS.md"]
    log = _text(ROOT / "DECISIONS.md")
    for pth in sorted((ROOT / "prereg").glob("F-*.md")):
        t2 = _text(pth)
        if MARK_SEARCH in _flat(t2):
            assert not _pin_ready(t2, log), (pth.name, _pin_ready(t2, log))
    gk = _flat(_text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"))
    for s in ("A failed limit clause or power gate is never a free retry",
              "refuse a successor that re-sets them any other way", "while " + RR + " is a placeholder"):
        assert s in gk, s


def test_cycle2_c2_minors():
    ht = _flat(_text(HT))
    for s in ("its go row", "its calibration record's sha256", "the runner commit that produced the finalists",
              "a new runner with its own identity, reproducing that search's search-year outputs path for path",
              "this template is pinned by its sha256 in a decision row", "CHARTER 3.6 (c)'s firm list",
              "The marker is valid only on a declaration written from this template and pinned as F-HT"):
        assert s in ht, s                                                       # m-2, m-4, m-5
    t = _flat(_text(TEMPLATE))
    assert "this template is pinned by its sha256 in a decision row" in t       # m-5
    s13 = _section(_text(TEMPLATE), "## 13. The count", "## 14.")
    assert "F-HT's k is assigned at its held-out row" in s13                    # m-6
    assert "a search's withdrawal before F-HT's held-out row spends nothing" in s13
    assert "this search's k" not in s13 and "this search is not counted" not in s13
    s14 = _section(_text(TEMPLATE), "## 14. The run order", "## 15.")
    assert "Its own finalists' row is its held-out row (m-3)" in s14            # m-3
    assert "terminal state" in _section(_text(TEMPLATE), "## 2. Years", "## 3. The lever space")
