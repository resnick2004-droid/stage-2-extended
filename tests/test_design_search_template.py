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

Text only: no bar, no engine, no outcome. **The needles hold sentences, not meaning:** an added contradiction or a
paraphrase outside a needled sentence is the gatekeeper's and the red team's to catch (the re-reads' M-4r).
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
    for s in ("at most three a market", "P-05, P-06 and P-10", "only by the operator's decision"):
        assert s in gk, s                                                                   # m-2, m-3
    gkf = _flat(gk)
    for s in ("A search assigns no k. Its pin row states \"no k (F-HT's, k = 13 next)\". F-HT's k is assigned at its "
              "held-out row, which is its finalists' token row",
              "each finalist's place power is re-stated at the new level by a lookup in its gate's output at k = 14 to "
              "20 (K-2), never a new run", "No repeat row for F-HT, ever: its held-out test runs once.",
              "E-005 (d), restated: F-HT withdrawn after its held-out row still spends its k",
              "(a search assigns no k; F-HT's k is assigned at F-HT's held-out row, E-204)"):
        assert s in gkf, s                                                                  # K-1 (E-259)
    for bad in ("A search assigns its k", "under a repeat row", "if none takes a k first", "its k is assigned later",
                "the search must re-state", "a search withdrawn after its held-out row"):
        assert bad not in gkf, bad
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
    assert "before Q-158 merges" not in gk and "the lead's CHARTER 3.7 reading row" in gk                        # m-6, m-9
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
    assert "Text v3 (2026-11-21)" in text and "fad9461" in text and "1a9be8c" in text   # the re-declaration (v3)
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


def _walk_law(l, g, s, n, rounded=False):
    """The template's walk in floats on the lattice of step s ticks from 0, barriers -l and +g in ticks: fractional in
    lattice units with the two-point last sub-steps, or (a negative control) rounded to the nearest lattice point.
    Returns (P(stop), P(target), E[X^2] in ticks^2), X the walk's value at its exit or at n steps."""
    lo, hi = -Fr(l) / s, Fr(g) / s
    if rounded:
        lo, hi = -Fr(round(lo * -1)), Fr(round(hi))
    dist, p_lo, p_hi, ex2 = {Fr(0): 1.0}, 0.0, 0.0, 0.0
    for _ in range(n):
        nxt = {}
        for x, pr in dist.items():
            du, dd = min(Fr(1), hi - x), min(Fr(1), x - lo)
            q_up = float(dd / (du + dd))
            for y, q in ((x + du, q_up), (x - dd, 1.0 - q_up)):
                if y <= lo:
                    p_lo += pr * q
                    ex2 += pr * q * float(y * s) ** 2
                elif y >= hi:
                    p_hi += pr * q
                    ex2 += pr * q * float(y * s) ** 2
                else:
                    nxt[y] = nxt.get(y, 0.0) + pr * q
        dist = nxt
    ex2 += sum(pr * float(x * s) ** 2 for x, pr in dist.items())
    return p_lo, p_hi, ex2


def test_s1_the_lattice_step_is_the_smallest_admissible_and_never_refuses():
    from math import sqrt

    assert _step(sqrt(400), 1024) == 1 and round(400 / 1 ** 2) == 400          # the read's case: one tick, n = 400
    assert _step(8 * sqrt(2), 1024) == 1                                         # two minutes before the flatten
    assert _step(96, 1024) == 3 and round(96 ** 2 / 9) == 1024                   # n held at the limit
    for root in (1, 31.9, 32, 32.1, 64, 200, 1000):
        s = _step(root, 1024)
        assert s >= 1 and round(root ** 2 / s ** 2) <= 1024                     # never refused, n within the limit
    # s-a: the template's walk against the one-tick lattice, at the coarsest n for s = 2 (sigma sqrt(T) = 32.1, n = 258)
    # and its finest (64, n = 1024); a tolerance below the gap barrier rounding opens, which the control must exceed
    for (l, g), root in (((37, 55), 32.1), ((21, 43), 32.1), ((37, 55), 64)):
        s = _step(root, 1024)
        n_s, n_1 = round(root ** 2 / s ** 2), round(root ** 2)
        assert s == 2 and n_s in (258, 1024)
        ps, pt, e2 = _walk_law(l, g, s, n_s)
        p1, t1, e21 = _walk_law(l, g, 1, n_1)
        assert abs(ps - p1) < 0.002 and abs(pt - t1) < 0.002 and abs(e2 / e21 - 1) < 0.01, (l, g, root, ps, p1)
        pr, _, _ = _walk_law(l, g, s, n_s, rounded=True)                        # the negative control
        assert abs(pr - p1) > 0.002, (l, g, root, pr, p1)
    sec = _flat(_r10_section())
    for s in ("s = max(1, ceil(sigma sqrt(T) / sqrt(`WALK_MAX`))) ticks", "It need not divide the stop or the target",
              "A trade is never refused for its step", "the fill-time law's T",
              "One T for both s and n (s-b): T is the limit known at the fill for every row, the table's last included",
              "the realised exit time decides neither s nor n",
              "The barriers are not moved to the lattice; the walk's last sub-step resolves them"):
        assert s in sec, s
    for bad in ("largest whole number of ticks", "The lattice step s is one tick", "the trade is refused",
                "T to the run's exit time", "except for the table's last row"):
        assert bad not in sec, bad
    for rel in (".claude/agents/prereg-gatekeeper.md", ".claude/agents/red-team.md",
                ".claude/skills/merge-checklist/SKILL.md"):                     # M-4r: every copy of the formula
        c = _flat(_text(ROOT / rel))
        assert ("s = max(1, ceil(sigma sqrt(T) / sqrt(`WALK_MAX`))) ticks, from sigma, T and `WALK_MAX` and nothing "
                "else, never required to divide the stop or the target, a trade never refused for its step") in c, rel
        assert "largest whole number of ticks" not in c and "largest common divisor" not in c, rel
    gk = _flat(_text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"))
    assert "the lattice step s per trade (S-1)" in gk and "refuse any other s" in gk


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
              "This declaration is written as soon as, after the membership event, every member search is in (a) or (b)",
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
              "5. Written only when, after the membership event, every member search is in a terminal state",
              "2. Its inputs come only from the pinned searches' finalists' lists, each by its sha256, each search by its "
              "pin's hash, its go row, its calibration record's sha256, its finalists' row (newer than its go row) and its "
              "runner commit (m-4)",
              "8. Each finalist's power re-stated at its place in the joint sequence by the template's declared formula",
              "keeps its place", "Refuse a pin and a token in one row, and any repeat row for F-HT",
              "Each finalist's power re-stated at its place"):
        assert s in ht_items, s
    for bad in ("any other purpose", "when the lead decides"):
        assert bad not in ht_items, bad
    assert "in the joint order by the rule fixed in `prereg/TEMPLATE_heldout_test.md` (M-1)" in _flat(_text(TEMPLATE))


MARK_SEARCH, MARK_HT = "Declaration kind: design search", "Declaration kind: held-out test"
DS_HEADINGS = ("## 5. The zero-edge convention", "## 6. The survey", "## 7. The pinning row")
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
    if MARK_SEARCH not in f and MARK_HT not in f and any(h in f for h in DS_HEADINGS):
        out.append(f"{name}: a design search's headings without the design-search marker (T-1)")
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
        if any(h in f for h in ("## 5. The zero-edge convention", "## 6. The survey", "## 7. The pinning row")):
            out.append(f"{name}: held-out-marked with a design search's headings (the re-read's N-a)")
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
    assert _line_problems("F-18_n.md", ht_ok + "\n## 6. The survey, the surrogate and the rounds\n")   # N-a
    unmarked = _text(TEMPLATE).replace(MARK_SEARCH, "Declaration kind").replace(RR, "the lead's ruling")
    assert MARK_SEARCH not in _flat(unmarked)
    assert _line_problems("F-19_t1.md", unmarked) == ["F-19_t1.md: a design search's headings without the "
                                                      "design-search marker (T-1)"]          # the review's T-1 probe
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
        four = [m.group(1) for m in re.finditer(r"(?<![\w.:-])(\d{4,})(?![\w:%-])", text)
                if not re.search(r"\bfrom $", text[max(0, m.start() - 5):m.start()])]
        assert not four, (path.name, four)                       # a year only in a date or "from 20xx"
        three = [m.group(1) for m in re.finditer(r"(?<![\w.:-])(\d{3})(?![\w:%-])", text)
                 if not text[m.end():m.end() + 3] == " MB"]
        assert not three, (path.name, three)                     # no three-digit count but the memory limit


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
#: CW-1 (E-259): a non-member's route, word for word in the template's section 2 and the held-out template's section 3
CW_SENTENCE = ("are tested only on data this line has never read (a later purchase), under its own k; the confirmation "
               "window (NQ from 2026-07-17) is read once, only for this F-HT's carried designs (CW-1; E-259)")
CAUSES = ("calibration-failed", "limit-clause-failed", "power-gate-failed", "every-design-failed-a-gate",
          "empty-finalist-list", "every-finalist-failed-no-harm", "withdrawn", "defect-on-record")


class Refused(Exception):
    """A row the membership rule refuses."""


def _firm_states(events):
    """H-1' (E-257) with E-259's R-1, W-1 and D-1, on synthetic rows in row order: ("pin", firm, search), ("go", firm,
    search), ("finalists", firm, search, ranks), ("closed", firm, search, cause), ("join", firm, search),
    ("heldout", None, None). The membership event is the first go row; each firm's one search with a hash row before
    it is that firm's member. Refuses: a second pin for a firm before the event, closed or not (R-1); a pin after
    every member is terminal and before the held-out row (the no-new-pin bar); `withdrawn` after the event (W-1); an
    unlisted cause; a closing row after a finalists' row (finalists never voided); a non-member offered as a member.
    Returns (states, due, outside): states {firm: (state, ranks)} with 'a', 'b', 'c' or 'open'; due whether F-HT is
    due; outside the searches pinned after the event."""
    pins, fin, closed, members, outside, held = {}, {}, {}, None, [], False

    def terminal():
        return members is not None and all(s in fin or s in closed for s in members.values())

    for ev in events:
        kind = ev[0]
        if kind == "heldout":
            held = True
            continue
        firm, search = ev[1], ev[2]
        assert firm in FIRMS, firm
        if kind == "pin":
            if members is not None and terminal() and not held:
                raise Refused(f"{search}: no new search may be pinned until F-HT's held-out row is written")
            if members is None:
                if firm in pins:
                    raise Refused(f"{search}: a second hash row for {firm} before the membership event (R-1)")
                pins[firm] = search
            else:                                      # after the event: outside this F-HT
                outside.append(search)
        elif kind == "go":
            if members is None:
                members = dict(pins)                   # the membership event
        elif kind == "finalists":
            fin[search] = list(ev[3])
        elif kind == "closed":
            cause = ev[3]
            if cause not in CAUSES:
                raise Refused(f"{search}: {cause!r} is not a listed cause")
            if cause == "withdrawn" and members is not None:
                raise Refused(f"{search}: withdrawn after the membership event (W-1)")
            if search in fin:
                raise Refused(f"{search}: a closing row after its finalists' row (finalists are never voided)")
            closed[search] = cause
        elif kind == "join":                           # an attempt to add a search to F-HT's membership
            if members is None or members.get(firm) != search:
                raise Refused(f"{search}: not a member of this F-HT")
    states = {}
    for firm in FIRMS:
        s = (members if members is not None else pins).get(firm)
        if s is None:
            states[firm] = ("c", []) if members is not None else ("open", [])
        elif s in fin:
            states[firm] = ("a", list(fin[s]))
        elif s in closed:
            states[firm] = ("b", [])
        else:
            states[firm] = ("open", [])
    return states, terminal(), outside


#: G-1: the go-row token, the exact first text of a decision row's third cell (the reader's positional form)
GO_TOKEN = re.compile(r"^\| (?P<row>E-\d+) \| \d{4}-\d{2}-\d{2} \| go: (?P<decl>F-\d+) @ (?P<sha>[0-9a-f]{64})"
                      r"(?= -- [^\s|]| \|)")
PIN_ROW = re.compile(r"`prereg/(F-\d+)_[^`]*\.md` sha256 `([0-9a-f]{64})`")
LOG_ROW = re.compile(r"^\| E-\d+ \|")


def _log_membership(decisions: str, scope: dict) -> tuple:
    """G-1 on a decision log: (the membership event's row id or None, {firm: its member search}). `scope` maps a
    declaration to its firm when it is an NQ design search of Topstep, My Funded Futures or Lucid. The event is the
    first go token of a declaration in scope; a member's first hash row comes strictly before the event's row (a hash
    row in the event's own row is not before it); a second firm's hash row before the event is refused (R-1)."""
    rows = [line for line in decisions.splitlines() if LOG_ROW.match(line)]
    event = next(((i, m.group("row")) for i, line in enumerate(rows)
                  if (m := GO_TOKEN.match(line)) and m.group("decl") in scope), None)
    members, seen = {}, set()
    for i, line in enumerate(rows):
        if event is not None and i >= event[0]:
            break
        for decl, _sha in PIN_ROW.findall(line):
            if decl not in scope or decl in seen:
                continue
            seen.add(decl)
            if scope[decl] in members:
                raise Refused(f"{decl}: a second hash row for {scope[decl]} before the membership event (R-1)")
            members[scope[decl]] = decl
    return (event[1] if event else None), members


def _log_scope(root: Path) -> dict:
    """The real scope: every pinned `prereg/F-NN_*.md` carrying the design-search marker, on NQ, its firm line naming
    one of the three firms."""
    names = {"Topstep": "Topstep", "My Funded Futures": "MFFU", "MFFU": "MFFU", "Lucid": "Lucid"}
    out = {}
    for pth in sorted((root / "prereg").glob("F-*.md")):
        f = _flat(_text(pth))
        m = re.search(r"The firm and account: ([A-Za-z ]+?)[,(<-]", f)
        if MARK_SEARCH in f and "NQ" in f and m and m.group(1).strip() in names:
            out[pth.name.split("_")[0]] = names[m.group(1).strip()]
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


def test_h1_membership_is_fixed_by_an_event_and_states_by_rule():
    import pytest

    # an empty history is never due: before the membership event nothing is "all terminal"
    st, due, _ = _firm_states([])
    assert not due and all(v[0] == "open" for v in st.values())
    # Topstep's finalists with no other firm pinned before the event: due only once the event has passed
    ev = [("pin", "Topstep", "F-13"), ("go", "Topstep", "F-13"), ("finalists", "Topstep", "F-13", ["t1", "t2"])]
    st, due, _ = _firm_states(ev)
    assert due and st == {"Topstep": ("a", ["t1", "t2"]), "MFFU": ("c", []), "Lucid": ("c", [])}
    st, due, _ = _firm_states(ev[:1])                                           # pinned, no go row: no event yet
    assert not due and st["MFFU"] == ("open", [])
    # all three pinned before the event are members; a member neither finalised nor closed blocks
    ev = [("pin", "Topstep", "F-13"), ("pin", "MFFU", "F-14"), ("pin", "Lucid", "F-15"), ("go", "Topstep", "F-13"),
          ("finalists", "Topstep", "F-13", ["t1"]), ("closed", "MFFU", "F-14", "power-gate-failed")]
    st, due, _ = _firm_states(ev)
    assert not due and st["Lucid"] == ("open", [])
    st, due, _ = _firm_states(ev + [("closed", "Lucid", "F-15", "empty-finalist-list")])
    assert due and st == {"Topstep": ("a", ["t1"]), "MFFU": ("b", []), "Lucid": ("b", [])}
    # a search pinned after the event, or a successor of a closed search, is never a member
    st, due, outside = _firm_states(ev[:4] + [("pin", "MFFU", "F-16")])
    assert outside == ["F-16"]
    for bad in (ev[:4] + [("pin", "MFFU", "F-16"), ("join", "MFFU", "F-16")],
                [("pin", "MFFU", "F-14"), ("go", "MFFU", "F-14"), ("closed", "MFFU", "F-14", "calibration-failed"),
                 ("pin", "MFFU", "F-16"), ("join", "MFFU", "F-16")]):
        try:
            _firm_states(bad)
            raise AssertionError("a non-member was admitted")
        except Refused:
            pass
    # the no-new-pin bar, a withdrawal after a go row, an unlisted cause, and a voided finalists' row: refused
    full = ev + [("closed", "Lucid", "F-15", "empty-finalist-list")]
    for bad in (full + [("pin", "Lucid", "F-17")],
                [("pin", "Topstep", "F-13"), ("go", "Topstep", "F-13"), ("closed", "Topstep", "F-13", "withdrawn")],
                [("pin", "Lucid", "F-17"), ("closed", "Lucid", "F-17", "the lead preferred to")],
                [("pin", "Topstep", "F-13"), ("go", "Topstep", "F-13"), ("finalists", "Topstep", "F-13", ["t1"]),
                 ("closed", "Topstep", "F-13", "power-gate-failed")]):
        try:
            _firm_states(bad)
            raise AssertionError("refusal missing")
        except Refused:
            pass
    _firm_states(full + [("heldout", None, None), ("pin", "Lucid", "F-17")])  # after the held-out row: allowed
    _firm_states([("pin", "Lucid", "F-17"), ("closed", "Lucid", "F-17", "withdrawn")])   # before the event: allowed
    # R-1 (E-259): at most one member search per firm; a second hash row before the event is refused, closed or not
    for bad in ([("pin", "Topstep", "F-13"), ("pin", "Topstep", "F-14")],
                [("pin", "Topstep", "F-13"), ("closed", "Topstep", "F-13", "calibration-failed"),
                 ("pin", "Topstep", "F-14")],
                [("pin", "Topstep", "F-13"), ("pin", "Topstep", "F-14"), ("pin", "MFFU", "F-15"),
                 ("go", "Topstep", "F-13"), ("finalists", "Topstep", "F-13", ["a1", "a2"]),
                 ("finalists", "Topstep", "F-14", ["b1"]), ("closed", "MFFU", "F-15", "power-gate-failed")]):
        with pytest.raises(Refused, match="R-1"):
            _firm_states(bad)
    # the positive control: after the event a further search of the firm pins outside this F-HT ...
    st, due, outside = _firm_states([("pin", "Topstep", "F-13"), ("go", "Topstep", "F-13"), ("pin", "Topstep", "F-14")])
    assert outside == ["F-14"] and st["Topstep"] == ("open", []) and not due
    st, _, _ = _firm_states([("pin", "Topstep", "F-13"), ("go", "Topstep", "F-13"), ("pin", "Topstep", "F-14"),
                             ("finalists", "Topstep", "F-14", ["x"]), ("finalists", "Topstep", "F-13", ["t1"])])
    assert st["Topstep"] == ("a", ["t1"])                                   # never the outside search's ranks
    # ... unless the no-new-pin bar holds
    done = [("pin", "Topstep", "F-13"), ("go", "Topstep", "F-13"), ("finalists", "Topstep", "F-13", ["t1"])]
    with pytest.raises(Refused, match="no new search"):
        _firm_states(done + [("pin", "Topstep", "F-14")])
    assert _firm_states(done + [("heldout", None, None), ("pin", "Topstep", "F-14")])[2] == ["F-14"]
    # W-1 (E-259): no withdrawal after the event, even before the member's own go row (the review's probe)
    with pytest.raises(Refused, match="W-1"):
        _firm_states([("pin", "Topstep", "F-13"), ("pin", "MFFU", "F-14"), ("pin", "Lucid", "F-15"),
                      ("go", "Topstep", "F-13"), ("finalists", "Topstep", "F-13", ["t1", "t2"]),
                      ("closed", "MFFU", "F-14", "withdrawn")])
    # D-1 (E-259): a defect on record closes a member after the event
    st, due, _ = _firm_states(done[:2] + [("closed", "Topstep", "F-13", "defect-on-record")])
    assert due and st["Topstep"] == ("b", [])
    ht = _flat(_text(HT))
    for s in ("The membership event is the first go-row token, `go: F-NN @ <its LF sha256>`, of an NQ design search of "
              "Topstep, My Funded Futures or Lucid (G-1; E-259)",
              "This F-HT's membership is fixed at that moment",
              "each firm's one design search with a hash row before the event is that firm's member (at most one per "
              "firm); a firm with no hash row before the event is in state (c) for this F-HT, fixed at that moment, "
              "before any search's search-year outcome is read",
              "`heldout-closed: F-NN @ <its LF sha256> -- <cause> -- <text>`",
              "only before the membership event; after it, a member closes only by causes 1 to 6 or 8 and is never "
              "dropped by choice (W-1; E-259)",
              "A firm's finalists are never voided",
              "No successor enters this F-HT. A search pinned after the membership event, or a successor of a closed "
              "search, is never a member of this F-HT; its candidates " + CW_SENTENCE,
              "This declaration is written as soon as, after the membership event, every member search is in (a) or "
              "(b)", "Before the event it is never due: an empty history is not \"all terminal\"",
              "Then no new search may be pinned until this declaration's held-out row is written",
              "A member search that is neither finalised nor closed blocks the declaration", "never waited out by choice"):
        assert s in ht, s
    for bad in ("latest pinned search counts", "are void once a successor", "no search of the firm was ever pinned",
                "third terminal state", "more than one member search", "search by search in the order of their hash "
                "rows", "latest member search", "by the event", "go to the confirmation window under"):
        assert bad not in ht, bad
    causes = ht[ht.index("its cause one of a closed list"):ht.index("A firm's finalists are never voided")]
    assert re.findall(r"\d\. `([a-z-]+)`", causes) == list(CAUSES), causes          # exactly the closed list
    t = _flat(_text(TEMPLATE))
    for s in ("the one design search of each of Topstep, My Funded Futures and Lucid with a hash row before the "
              "membership event, the first go-row token of an NQ design search of Topstep, My Funded Futures or Lucid "
              "(H-1'; E-257; E-259), at most one per firm, a second hash row for a firm before the event refused at "
              "its pin",
              "A search pinned after the membership event, or a successor of a closed search, is never a member of "
              "this F-HT; its candidates " + CW_SENTENCE,
              "written as soon as, after the membership event, every member search has a finalists' row or a closing "
              "row (H-1'; E-257", "A search pinned after the membership event is never a member of this F-HT",
              "The joint order alternates by rank across the firms (H-2; E-257), by the held-out template's rule"):
        assert s in t, s
    gk = _flat(_text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"))
    for s in ("Membership (H-1'; E-257): this F-HT's members are the design searches with a hash row before the "
              "membership event, the first go-row token (`go: F-NN @ <its LF sha256>`) of an NQ design search of "
              "Topstep, My Funded Futures or Lucid, at most one per firm",
              "At most one member search per firm: refuse a design search for a pin before the membership event when "
              "its firm already has a hash row, closed or not (R-1; E-259)",
              "a firm's ranks its one member search's own pinned finalist order",
              "Refuse a search pinned after the membership event, or a successor of a closed search, offered as a "
              "member", "refuse a new search for a pin after every member search is in a terminal state until F-HT's "
              "held-out row is written",
              "4. Each firm's state by membership at the fixed event (H-1'; E-257)",
              "`withdrawn` only before the membership event, `defect-on-record` citing its diagnosis row",
              "5. Written only when, after the membership event, every member search is in a terminal state"):
        assert s in gk, s
    for bad in ("search by search in the order of their hash rows", "more than one member search", "by the event",
                "by the membership event", "go to the confirmation window under"):
        assert bad not in gk and bad not in t, bad


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


RR = "E-258 (the lead's CHARTER 3.7 reading row)"
RR_PLACEHOLDER = "E-NNN (the lead's CHARTER 3.7 reading row)"
NO_RETRY = ("A failed limit clause or power gate is never a free retry (M-5 (c); " + RR + "): W42-R1's limits, "
            "bankroll budgets, weights and size that matters are never changed for any search of the line -- every "
            "search, of any firm, whose section 7 applies W42-R1 -- after any calibration or gate that read them; a "
            "defect found in them goes through the failure protocol as a defect on record, and a corrected rule is a "
            "new rule under a new row whose searches never enter this F-HT. A successor search inherits them "
            "unchanged, changes only what the failure's diagnosis names, citing the record, with a fresh seed block, "
            "and never enters this F-HT (its candidates are tested only on data this line has never read, a later "
            "purchase, under its own k); every closed attempt of the line is counted and printed beside the "
            "verdict.")


def _pin_ready(text: str, decisions: str, sha: str | None = None) -> list:
    """m-c: a design search pins only when every citation of the reading row is `E-<n> (the lead's CHARTER 3.7 reading
    row)`, at least the template's three sites, and the cited row exists in DECISIONS.md with its bolded title
    beginning `CHARTER's "pin" read`. A bare number, a deleted citation, or any other row is refused. With `sha` (a
    pinned file's LF sha256), the cited row must come before the first row carrying that hash (T-1; E-259)."""
    out = []
    rows = [line for line in decisions.splitlines() if LOG_ROW.match(line)]
    pin_at = next((i for i, line in enumerate(rows) if sha and sha in line), None)
    if sha is not None and pin_at is None:
        out.append("no row of DECISIONS.md carries this file's sha256")
    if RR_PLACEHOLDER in text:
        out.append("the CHARTER 3.7 reading row is still a placeholder")
    cited = re.findall(r"(E-\d+) \(the lead's CHARTER 3\.7 reading row\)", text)
    if len(cited) < 3:
        out.append(f"the reading row is cited {len(cited)} times, not at its three sites")
    for row in sorted(set(cited)):
        m = re.search(rf"^\| {row} \| [^|]*\| \*\*(.*)", decisions, re.M)
        if not m:
            out.append(f"{row} cited but not in DECISIONS.md")
        elif not m.group(1).startswith('CHARTER\'s "pin" read'):
            out.append(f"{row} is not the CHARTER 3.7 reading row")
        elif pin_at is not None and next(i for i, line in enumerate(rows) if line.startswith(f"| {row} |")) >= pin_at:
            out.append(f"{row} does not come before the pin row")
    return sorted(set(out))


def test_m5_no_free_retry_and_the_reading_row_before_any_pin():
    import pytest

    text = _text(TEMPLATE)
    f = _flat(text)
    for s in ("CHARTER 3.8 (a)'s \"a pinning row ... does not pin\"", "\"before any search is pinned\"",
              "the reader's pin and every \"newer than the pin\" mean the hash row",
              "No search pins before " + RR + " exists in `DECISIONS.md`, its bolded title beginning `CHARTER's \"pin\" "
              "read`"):
        assert s in f, s
    for bad in ("may re-set", "a change comes only by a decision row", "may raise", "sets new limits"):
        assert bad not in f, bad
    # M-5 (c): one sentence, word for word, in the template's section 9 and the gatekeeper's item 9
    s9 = _section(text, "## 9. Calibration", "## 10. The pass line")
    gk = _flat(_text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"))
    assert NO_RETRY in s9 and NO_RETRY in gk, NO_RETRY
    for bad in ("may re-set", "a change comes only by a decision row", "sets new limits"):
        assert bad not in gk, bad
    # m-c: the refusals, with synthetic logs
    good = "| E-901 | d | **CHARTER's \"pin\" read under the design-search template ... |\n"
    t901 = text.replace("E-258 (the lead", "E-901 (the lead")
    assert _pin_ready(t901, good) == []
    assert _pin_ready(t901, "| E-901 | d | **Something else. |\n") == ["E-901 is not the CHARTER 3.7 reading row"]
    assert _pin_ready(t901, "") == ["E-901 cited but not in DECISIONS.md"]
    assert _pin_ready(text.replace(RR, "E-901"), good)                               # a bare number
    assert _pin_ready(text.replace(RR, "the lead's ruling"), good)                    # a deleted citation
    assert _pin_ready(text.replace(RR, RR_PLACEHOLDER), good)                         # the placeholder
    log = _text(ROOT / "DECISIONS.md")
    import hashlib

    for pth in sorted((ROOT / "prereg").glob("F-*.md")):
        t2 = _text(pth)
        if MARK_SEARCH in _flat(t2):
            h = hashlib.sha256(t2.encode("utf-8")).hexdigest()
            assert not _pin_ready(t2, log, h), (pth.name, _pin_ready(t2, log, h))
    # T-1: the reading row must come before the pin row
    pin = "| E-900 | d | **Search F-13 declared ...** `prereg/F-13_x.md` sha256 `" + "a" * 64 + "` |\n"
    assert _pin_ready(t901, good + pin, "a" * 64) == []
    assert _pin_ready(t901, pin + good, "a" * 64) == ["E-901 does not come before the pin row"]
    assert _pin_ready(t901, good, "a" * 64) == ["no row of DECISIONS.md carries this file's sha256"]
    gk_items = gk[gk.index("1. Years and the held-out read ledger"):gk.index("2. The confirmation window")]
    assert "a bare number, a deleted citation or any other row is refused" in gk_items
    # the template's own citation: E-258 must be that row once master carries it (a visible skip until then)
    if not re.search(r"^\| E-258 \|", log, re.M):
        pytest.skip("E-258 (the lead's CHARTER 3.7 reading row) is not yet in DECISIONS.md on this tree")
    assert _pin_ready(text, log) == [], _pin_ready(text, log)


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
    assert "membership event" in _section(_text(TEMPLATE), "## 2. Years", "## 3. The lever space")
    for bad in ("the search's level", "the search's k"):                                              # m-e
        assert bad not in _flat(_text(TEMPLATE)), bad
    assert "power at every k from 14 to 20 reported beside, so a re-statement at another k is a lookup" in t
    # N-b: one closing-token form everywhere
    full = "`heldout-closed: F-NN @ <its LF sha256> -- <cause> -- <text>`"
    for rel in ("prereg/TEMPLATE_design_search.md", "prereg/TEMPLATE_heldout_test.md",
                ".claude/agents/prereg-gatekeeper.md"):
        c = _flat(_text(ROOT / rel))
        forms = re.findall(r"`heldout-closed:[^`]*`", c)
        assert forms and set(forms) == {full}, (rel, forms)


# ============================================================================================ L. text v3's paraphrase
# round (the re-read's M-4r): sentences in every copy, and rule-negating forms refused wherever they would go

#: a rule-negating form a paraphrase would take; none may appear in either template or the gatekeeper's file
FORBIDDEN_FORMS = (
    r"\bmay (?:raise|change|re-?set|re-?order|be repeated|be extended|be re-run|be added)\b",
    r"\bcan be (?:run|read|repeated) again\b", r"\bat any time\b", r"\bif better\b", r"\bis dropped\b",
    r"\blead(?:'s row)? (?:excludes|chooses|decides)\b", r"\bafter a fail\w*,? (?:it )?(?:goes|moves|continues)\b",
    r"\bmay set\b", r"\bunless a later\b", r"\bthe lead names\b", r"\bjudges it ready\b",     # N-1 (E-259)
    r"\bwithout a row\b", r"\blatest member search\b",
)


def test_v3_no_rule_negating_form_and_every_copy_needled():
    for path in (TEMPLATE, HT, CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"):
        f = _flat(_text(path))
        for rx in FORBIDDEN_FORMS:
            assert not re.search(rx, f), (path.name, rx, re.findall(rx, f))
    for path in (TEMPLATE, HT):
        assert set(re.findall(r"\b\d+\.\d{2,}\b", _text(path))) <= {"0.05"}, path.name   # a 1.37 or a 1.37-fold
    t = _flat(_text(TEMPLATE))
    for s in ("n = round(sigma^2 T / s^2) (to the nearest integer, halves up, at least one)",
              "a firm with no hash row before the event being in state (c)",
              "A search closed by a failed calibration, limit clause or power gate gets a closing row"):
        assert s in t, s
    ht = _flat(_text(HT))
    for s in ("Beside it, never deciding, the Frechet lower bound", "the full level 0.05 / (k (k + 1)) at every place",
              "k assigned in the row's text (E-204)", "A firm's ranks are the search's own pinned finalist order (its "
              "finalists' row, set by the finalist order rule its declaration pinned before its survey)"):
        assert s in ht, s
    gk = _flat(_text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"))
    for s in ("A firm's finalists are never voided; no successor and no search pinned after the event is a member",
              "a cause from the template's closed list"):
        assert s in gk, s


# ============================================================================================ M. E-259's pre-pin fixes
# (the red team's full read of text v3, TEMPLATE_V3_FULL_2026-11-21: R-1, W-1, CW-1, D-1, G-1, K-1, K-2, U-1, L-1,
# N-1, T-1, X-1), each sentence held where it lives

#: D-1, N-1 (W11, W12): each closed cause with its description, the pair and not only the name
CAUSE_TEXT = (
    "the deciding calibration failed;", "the power gate's limit clause failed;", "the power gate failed;",
    "every surveyed design failed a gate before its outcomes;", "the finalist order rule yielded an empty list;",
    "every finalist failed its playbook no-harm floor;",
    "a withdrawal under E-005 (d), its reason in the row, only before the membership event; after it, a member closes "
    "only by causes 1 to 6 or 8 and is never dropped by choice (W-1; E-259).",
    "a defect named by the failure protocol, cited by its diagnosis row; never a preference (D-1; E-259).",
)


def test_e259_the_go_token_fixes_the_event_in_the_log():
    import pytest

    a, b, c, d, z = ("a" * 64, "b" * 64, "c" * 64, "d" * 64, "e" * 64)
    scope = {"F-13": "Topstep", "F-14": "MFFU", "F-15": "Lucid", "F-16": "Lucid"}
    rows = ["| E-899 | 2026-11-30 | go: F-12 @ " + z + " -- an ES search's go row, outside the scope | b |",
            "| E-900 | 2026-12-01 | **Search F-13 declared.** `prereg/F-13_a.md` sha256 `" + a + "` | b |",
            "| E-901 | 2026-12-02 | **Search F-14 declared.** `prereg/F-14_b.md` sha256 `" + b + "` | b |",
            "| E-902 | 2026-12-03 | **A prose row** naming go: F-14 @ " + b + " -- not at the cell's start | b |",
            "| E-903 | 2026-12-04 | go: F-13 @ " + a + " -- the go row; `prereg/F-15_c.md` sha256 `" + c + "` | b |",
            "| E-904 | 2026-12-05 | go: F-14 @ " + b + " -- MFFU's go row | b |",
            "| E-905 | 2026-12-06 | **Search F-16 declared.** `prereg/F-16_d.md` sha256 `" + d + "` | b |"]
    log = "\n".join(rows) + "\n"
    # the event is the first in-scope token at a row's third cell; a hash row in the event's own row is not before it
    assert _log_membership(log, scope) == ("E-903", {"Topstep": "F-13", "MFFU": "F-14"})
    assert _log_membership("\n".join(rows[:4]), scope) == (None, {"Topstep": "F-13", "MFFU": "F-14"})
    assert _log_membership(log.replace("go: F-13 @ " + a + " --", "go: F-13 @ " + a + "--"), scope)[0] == "E-904"
    second = rows[:2] + ["| E-901 | 2026-12-02 | **Search F-17 declared.** `prereg/F-17_t.md` sha256 `" + b + "` |"]
    with pytest.raises(Refused, match="R-1"):
        _log_membership("\n".join(second + rows[4:]), dict(scope, **{"F-17": "Topstep"}))
    # the real log: every go token names an in-scope pinned search, and its membership parses without a refusal
    log = _text(ROOT / "DECISIONS.md")
    real = _log_scope(ROOT)
    event, members = _log_membership(log, real)
    for m in filter(None, map(GO_TOKEN.match, log.splitlines())):
        assert m.group("decl") in real, (m.group("row"), m.group("decl"))
    if event is None:
        assert not any(GO_TOKEN.match(line) for line in log.splitlines())
    assert set(members) <= set(FIRMS)
    # the token's form in every copy
    for path in (TEMPLATE, HT, CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"):
        assert "`go: F-NN @ <its LF sha256>`" in _flat(_text(path)), path.name


def test_e259_every_ruling_is_held_where_it_lives():
    text = _text(TEMPLATE)
    s1 = _section(text, "## 1. The question", "## 2. Years")
    for s in ("The firm and account: <firm, plan> -- exactly one firm; a search naming several firms is refused (R-1; "
              "E-259)",
              "Each baseline's runner identity is checked on the search years only; any held-out part compares trade "
              "times and brackets only, writes no outcome, and is entered in the held-out read ledger (L-1; E-259)"):
        assert s in s1, s                                                              # R-1, L-1
    s2 = _section(text, "## 2. Years", "## 3. The lever space")
    for s in ("only if this search is a member (its hash row before the membership event)",            # W2
              "its candidates " + CW_SENTENCE + ". A member's finalists are never voided. A later search on the same "
              "bars reads NQ's held-out years and F-HT's results as a description only",               # W10, X-1
              "it is read once, only for F-HT's carried designs, and a non-member search's candidates never use it "
              "(CW-1; E-259)"):
        assert s in s2, s
    s5 = _section(text, "## 5. The zero-edge convention", "## 6. The survey")
    for s in ("`EPS`: <...>, declared here, U-1", "`WALK_MAX`: <...>, declared here, U-1",
              "| the stopped walk, T the limit known at the fill (the flatten, a scheduled window or the max hold, "
              "whichever comes first), its share reported |"):                                         # U-1, W5
        assert s in s5, s
    s9 = _section(text, "## 9. Calibration", "## 10. The pass line")
    for s in ("the R-10 estimator, `EPS` and `WALK_MAX` (section 5)",
              "power at every k from 14 to 20 reported beside, so a re-statement at another k is a lookup, never a new "
              "run (m-e; K-2)"):
        assert s in s9, s                                                              # U-1, K-2
    s13 = _section(text, "## 13. The count", "## 14.")
    assert "(a lookup in each gate's output at k = 14 to 20, section 9)" in s13       # K-2, W7
    s14 = _section(text, "## 14. The run order", "## 15.")
    for s in ("At most one member search per firm: a second hash row for a firm before the membership event is refused "
              "at its pin, whether or not the first is closed (R-1; E-259); after the event a further search of the "
              "firm may pin, outside this F-HT, unless the no-new-pin bar holds.",
              "4. The go row: its third cell's first text is the token `go: F-NN @ <its LF sha256>` (G-1; E-259); it "
              "cites the calibration record's hash and names the runner commit the calibration ran on -- the survey "
              "and every round run on that runner commit, bound by its sha; a change to deciding code after it is a "
              "new declaration (U-1)",
              "`withdrawn` only before the membership event, W-1; `defect-on-record` citing its diagnosis row, D-1; "
              "E-259",                                                                                      # W1
              "5. The survey on the search years only (one clean run, from the go row's runner commit)",
              "6. The rounds, each one clean run from the go row's runner commit, collected",
              "no `registered_design` read of them (of P-14, P-15, P-16) is made before F-HT's verdict row (L-1; "
              "E-259)"):
        assert s in s14, s
    flat = _flat(text)
    for bad in ("without a decision row naming it", "reads them as a description only", "after any gate that read",
                "k = 14 and k = 15"):
        assert bad not in flat, bad
    ht = _flat(_text(HT))
    for s in ("At most one member search per firm (R-1; E-259): a second hash row for a firm before the membership "
              "event is refused at its pin, whether or not the first search is closed; a firm's ranks are its one "
              "member search's pinned finalist order.",                                                  # R-1, W4
              "A firm's state is its member search's, (a) or (b); (c) if it has none.",                 # W3
              "a closing row after a search's finalists' row is refused, and no later search replaces them.",   # W9
              "copy it to `prereg/DRAFT_F-XX_heldout_test_NQ.md` as soon as, after the membership event, every member "
              "search is in a terminal state (section 3)",                                               # W15
              "the full level 0.05 / (k (k + 1)) at every place -- from its own search's pinned power gate at the "
              "size that matters;",                                                                      # W16
              "The confirmation window (NQ from 2026-07-17) is read once, only for this F-HT's carried designs, and "
              "is a purchase; a non-member search's candidates never use it (CW-1; E-259)."):
        assert s in ht, s
    for i, (name, desc) in enumerate(zip(CAUSES, CAUSE_TEXT), 1):
        assert f"{i}. `{name}` -- {desc}" in ht, (i, name)                           # D-1, W11, W12
    gk = _flat(_text(CLAUDE_DIR / "agents" / "prereg-gatekeeper.md"))
    for s in ("is counted and printed beside the verdict. Refuse a draft that changes them, or a successor offered "
              "as a member.",                                                                                 # W14
              "a draft that plans a `registered_design` read of the held-out years (P-14, P-15, P-16) before F-HT's "
              "verdict row (L-1; E-259)",
              "the confirmation window is read once, only for this F-HT's carried designs, CW-1",
              "the R-10 estimator, `EPS` and `WALK_MAX`, the statistic",
              "naming the runner commit the calibration ran on, the survey and every round run on it (G-1, U-1; "
              "E-259)"):
        assert s in gk, s
