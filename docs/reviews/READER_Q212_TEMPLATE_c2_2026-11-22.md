# Red team diff check: paired Reader (Q-212 round 2) + Template v3 fixes (`READER_Q212_TEMPLATE_c2`)

**Reviewer:** red team, 2026-11-22.

**Targets (read-only from git history, workspace untouched)**
- **Reader side (`wt/wt-verify`):** `51384fe..08b0b7a` (skipping master merge `7cc9499`), i.e. commit `08b0b7a`:
  `extended/reader.py`, `tests/go_cases.py`, `tests/data/go_token_golden.json`, `tests/test_reader_go.py`,
  `tests/test_reader_q212b.py`, `tests/test_reader_superseded.py`, `tests/test_reader_q173.py`,
  `tests/test_rd_search_years_drafts.py` (`tests/test_reader_q194f.py` was unchanged in this range). Line numbers below
  for the reader side are at `08b0b7a`.
- **Template side (`wt/wt-lit`):** `0fb43a0..374f333` (skipping master merge parts from `6502d87`):
  `prereg/TEMPLATE_design_search.md` (T), `prereg/TEMPLATE_heldout_test.md` (HT),
  `.claude/agents/prereg-gatekeeper.md` (GK), `tests/test_declarations_fixed.py` (DF),
  `tests/test_design_search_template.py` (TT). Line numbers below for the template side are at `374f333`.
- **Workflow / merge conflict check:** `git diff 7c047a3 374f333 -- .claude/` and
  `git diff 7c047a3 374f333 -- tests/test_declarations_fixed.py` against master HEAD (`7c047a3`, carrying Q-210
  `e7f27c8`, H3 text 2 `7e13006`, and E-277..E-280 `7c047a3`).

**Method**
- Loaded `08b0b7a:extended/reader.py`, `08b0b7a:tests/go_cases.py`, `374f333:prereg/TEMPLATE_design_search.md`,
  `374f333:tests/test_declarations_fixed.py`, and `374f333:tests/test_design_search_template.py` directly from git blobs
  in memory (`git show`), running lightweight synthetic probes (`OMP_NUM_THREADS=1`) in disposable temp directories
  (all removed at the end; full pytest suite not run; no bars, no atlas, nothing from 2026-07-17 read; no seed literal
  quoted).
- Probes executed:
  - **Probe 1 (F1):** staged-uncommitted pin commit simulation (pre-commit hook state), `--no-ff` merge commit adding
    the template pin row (E-274 (11)), and U+2028 line-break crash in DF.
  - **Probe 2 (F4):** replayed `374f333` TT's Q-212 draft (`MFFU, Rapid 50K`) and 6 second-firm tails against `08b0b7a`
    `design_search_problems`.
  - **Probe 3 (F3):** mistaken `membership:` rows targeting (a) the second counted go row, (b) a voided before-pin go
    row, (c) an impossible-date `GO_TOKEN` row, before and after voiding, plus retry recovery and unclosed-fence
    swallowing; real `DECISIONS.md` at `7c047a3`.
  - **Probe 4 (F2):** uncommitted finalists' row in working-tree `DECISIONS.md` with `log_text=None`; `git replace` on
    the runner commit hiding a modified deciding file.
  - **Probe 5 (F5):** hidden line break (U+2028) above the first `| E-NNN |` row; mid-line bare CR (`\r`).
  - **Probe 6 (F7):** search-years read under `modes_scorecard` naming `CHARTER.md`; O-7 pin rows `E-268..E-272`
    against `PIN.findall`.
  - **Probe 7 (F8):** literal NUL byte in `DECISIONS.md` (case (d) and unrelated historical NUL); in-place row-ID
    renumbering (`E-980` -> `E-981`).
  - **Probe 8 (n1):** voided later NQ confirmation-window row against both `08b0b7a` and `374f333` `_cw_problems`;
    U+2028 line shift in `_cw_problems`; MNQ-first then NQ-second window ordering.
  - **Probe 9 (F10):** replayed all 131 golden cases of `08b0b7a` and ran in-memory single-line mutations for all 9
    previously surviving go-token mutants (`m10`, `m12`, `m20`, `m29`, `m32`, `m53`, `m55`, `m59`, `m60`), plus code
    inspection for `m47b`.

---

## Verdict: **BLOCK** (both sides, plus merge conflicts on `.claude/` and DF)

Five **MATERIAL** defects block merging this pair as committed:
1. **F1's fix (template side) still deadlocks the pre-commit hook on the template pin commit itself** and fails
   permanently if the pin row lands in an E-274 (11) merge commit.
2. **F3's freeze (reader side) introduces a permanent lock-in state and a clean-log hijack:** a mistaken `membership:`
   row pointing to *any* earlier `GO_TOKEN` line (even a voided go row or the second go row), once voided, leaves
   `go_problems == []`, permanently hijacks `membership_event` to that wrong row, and permanently blocks any corrected
   `membership:` row.
3. **F4's plan allow-list breaks `wt-lit`'s own Q-212 test on merge** (`MFFU, Rapid 50K` vs `MFFU, rapid50k`), and
   neither T nor GK documents the plan-key format.
4. **n1's `_cw_problems` cross-check (template side) ignores `heldout-void`**, creating a permanent fast-tier lock-in
   if any later NQ/MNQ confirmation-window row is ever written and voided.
5. **`wt/wt-lit` (`374f333`) predates master's Q-210 (`decl_lint.py`), H3 pin grammar, and E-280 (6)
   (`stage2_identity.py --paths 4`)**, conflicting in 3 `.claude/` files + DF and carrying two internal contradictions
   against master rulings in `.claude/`.

**Counts: 0 CHANGES-A-CONCLUSION, 5 MATERIAL, 5 MINOR, 4 NOTE.**

| # | Severity | Side | File:line | One-line summary |
|---|---|---|---|---|
| 1 | MATERIAL | template | `374f333` DF l.92-120 | `_reader_at_row` returns `None` on an uncommitted staged pin row (deadlocking the pre-commit hook on the template pin commit itself) and skips merge commits (`git log -S` without `-m`, breaking E-274 (11) permanently); `log.splitlines()` crashes against `RD._fences` on U+2028 |
| 2 | MATERIAL | reader | `08b0b7a` reader l.2128-2142, 2184-2191, 2231-2235 | A mistaken `membership:` row naming any earlier `GO_TOKEN` line (even voided, impossible-date, or second go row), once voided, leaves `go_problems == []`, permanently hijacks `membership_event` to that wrong row, and permanently refuses any replacement `membership:` row; `membership_event` also swallows all unvoided go problems once frozen |
| 3 | MATERIAL | paired (reader + template) | `08b0b7a` reader l.1917, 2043-2050; `374f333` TT l.2138-2142, T l.53-60, GK l.55-61 | F4's plan allow-list (`rapid50k`) immediately breaks `wt-lit`'s `test_q212_the_deciding_files_field_and_mffus_exact_form` (`MFFU, Rapid 50K`) on merge, and T/GK never state that `<plan>` must be a verified rules-record key |
| 4 | MATERIAL | template | `374f333` TT l.1900-1922, 1945 | `_cw_problems` does not honour `heldout-void` on later NQ/MNQ confirmation-window rows (contradicting reader n1) and uses `log.splitlines()`, creating a permanent fast-tier lock-in on any voided later confirmation-window row |
| 5 | MATERIAL | merge / `.claude/` + DF | `7c047a3` vs `374f333` `.claude/` (5 files) + DF | `wt-lit` conflicts with master's Q-210 (`prereg-gatekeeper.md`, `prereg.md`), E-280 (6) (`merge-checklist/SKILL.md`), and H3 pin grammar (DF), and contains stale rules contradicting E-274 (3) (`worker-protocol` 3a.12) and Q-210 (`prereg-discipline`) |
| 6 | MINOR | reader | `08b0b7a` reader l.1172-1175, 1210-1231 | F8's `--text` lets any literal NUL byte in `DECISIONS.md`'s history split `r.stdout.split("\x00")`, permanently breaking `_verdict_commits` (`None`); `_verdict_key` includes `row`, missing an in-place row-ID renumbering |
| 7 | MINOR | reader | `08b0b7a` reader l.2244-2302 | `go_row_present` omits `--no-replace-objects` (`git replace` on the runner commit hides a modified deciding file) and ignores an uncommitted dirty working-tree `DECISIONS.md` when `log_text is None` |
| 8 | MINOR | template | `374f333` T l.51, 62, 673, 693; HT l.84; GK l.59, 97 | Stale `RDPIN` phrase "`extended/reader.py` at its pinning row's sha256" left unchanged despite F1's remedy (once the reader evolves, per-search checks run the reader at the go row's runner commit, not at the template pin row) |
| 9 | MINOR | reader | `08b0b7a` reader l.1552-1558 | F7's search-years guard for superseded purposes allows any existing non-F/RD file (e.g. `declaration="CHARTER.md"`) despite claiming a pinned F- or RD- declaration is required |
| 10 | MINOR | reader | `08b0b7a` reader l.765-797 | F5 leaves bare mid-line `\r` unflagged (while `str.splitlines()` still splits on it), and a hidden line break above the first `| E-NNN |` row (`row = None`) is permanently unvoidable |
| n1 | NOTE | reader | `08b0b7a` reader l.1921, 2051 | F4 closes `<plan>` by allow-list, while the optional ` -- <text>` tail still uses the 8-name blacklist (`Alpha Futures`, `MFF`, `FundedNext`, `Earn2Trade`, `Elite Trader Funding`, `DayTraders` pass) |
| n2 | NOTE | reader | `08b0b7a` reader l.975-994 | Under n1, an accidental `MNQ` confirmation-window row before `NQ` makes `heldout_window(log, "NQ", ...)` fall back to `BASE_WINDOW_ROW` because `cw[1]` (NQ) is dropped |
| n3 | NOTE | reader tests | `08b0b7a` `go_cases.py`, `test_reader_superseded.py` | F10 verified: all 10 previously surviving mutants (`m10`, `m12`, `m20`, `m29`, `m32`, `m53`, `m55`, `m59`, `m60`, `m47b`) are now killed |
| n4 | NOTE | real repo | `7c047a3` `DECISIONS.md`, `config/rules_extended.yaml` | Real `DECISIONS.md` is clean under `08b0b7a`; O-7 pin rows `E-268..E-272` produce no false positives against `SUPERSEDED`; `lucid.flex50k` currently has only `unstated`/`unverified` keys so `firm_plans()` intentionally does not filter on `status == "verified"` |

---

## Findings

### 1 (MATERIAL, template side). F1's fix deadlocks the pre-commit hook on the template pin commit itself and fails permanently on a merge commit

**Where.** `374f333:tests/test_declarations_fixed.py` l.92-120 (`_reader_at_row`, `_template_pin_problems`).

```python
def _reader_at_row(root: Path, line: str) -> bytes | None:
    r = _git(root, "log", "--format=%H", "--reverse", "-S", line, "--", "DECISIONS.md")
    commits = r.stdout.decode().split() if r.returncode == 0 else []
    if not commits:
        return None
    b = _git(root, "show", f"{commits[0]}:extended/reader.py")
    return b.stdout if b.returncode == 0 else None
```

**Evidence (Probe 1a, 1b, 1d).**
- **Pre-commit deadlock (1a):** In a synthetic repo with `W42-R1` committed, staging the valid template pin row in
  `DECISIONS.md` (the exact state when `scripts/pre-commit` runs the fast tier before creating the commit) returns:
  `["line 2: extended/reader.py at the row's own commit does not hash to its pin (F1)"]`.
  Indeed, `374f333:tests/test_declarations_fixed.py` l.162 explicitly asserts that an uncommitted pin row fails! Since
  E-060 forbids `--no-verify`, the lead can never commit the template pin row (or any future template re-pin row).
- **Merge-commit blindness (1b):** Adding the template pin row inside a `--no-ff` merge commit — which E-274 (11)
  (`merge-checklist/SKILL.md`: *"resolve the conflict and add the row, STATUS, queue and progress lines in the same
  merge commit, so the hook runs once"*) instructs — leaves `_template_pin_problems` failing **after** the commit too:
  `["line 2: extended/reader.py at the row's own commit does not hash to its pin (F1)"]`, because `git log -S` skips
  merge commits unless `-m` is supplied.
- **Line-split mismatch (1d):** `_template_pin_problems` uses `lines = log.splitlines()` (l.101) while `_unfenced(log)`
  calls `RD._fences(log)`, which uses `_split(log)` in `08b0b7a`. A log containing U+2028 raises
  `IndexError: list index out of range`.

**Remedy.**
1. Compare each template pin row against `git --no-replace-objects show HEAD:DECISIONS.md`:
   - If `lines[i]` is **not yet present in HEAD's `DECISIONS.md`** (the commit being checked by pre-commit is introducing
     it), hash the staged/working-tree `extended/reader.py` (`git show :extended/reader.py` falling back to
     `root / "extended/reader.py"`).
   - If `lines[i]` **is** in HEAD's `DECISIONS.md`, find its introducing commit with
     `git --no-replace-objects log --format=%H --reverse --full-history -m --text --no-textconv --root -S <line> -- DECISIONS.md`
     (verifying the commit's `DECISIONS.md` holds the line) and hash `git --no-replace-objects show <c>:extended/reader.py`.
2. Replace `log.splitlines()` with `RD._split(log)`.
3. Add synthetic tests for (a) a staged, uncommitted pin row passing when `extended/reader.py` matches and failing when
   mismatched, and (b) a pin row introduced in a `--no-ff` merge commit continuing to pass after a later reader change.

---

### 2 (MATERIAL, reader side). F3's `membership:` freeze creates a permanent lock-in state and allows a voided mistaken `membership:` row to hijack `membership_event` with zero problems

**Where.** `08b0b7a:extended/reader.py` l.2128-2142 (`_go_scan`), l.2158 (`withdrawn`), l.2184-2191 (freeze check),
l.2231-2235 (`membership_event`).

**Why it breaks.**
1. `_go_scan` l.2132 matches a `membership:` row against *any* earlier unfenced `GO_TOKEN.match(lines[j])` — not
   checking whether that go row was counted, unvoided, or even had a valid date (`_valid_day`).
2. Line 2142 appends `(i, row, m, named)` to `memberships` even when `row` is later voided (`heldout-void`), and
   l.2139 rejects every subsequent `membership:` row as `"a second membership row (the first, ..., governs)"`.
3. `membership_event` l.2231 returns `s["lines"][s["frozen"][3]]` **before** checking `if s["problems"]: raise GoRefused(...)`.

**Evidence (Probe 3a, 3b, 3c, 3d).**

| Scenario | `go_problems` | `membership_event` |
|---|---|---|
| `P13, G13 (E-902), P14, G14 (E-904), M (E-905 naming E-904)` | `['E-905 ... not the first counted go row (E-902, F-13)']` | **Returns `E-904`** (silently ignores unvoided disagreement!) |
| Same + `void(E-906 -> E-905)` | **`[]` (clean!)** | **Still returns `E-904`** (F-14 hijacks membership!) |
| Same + recovery `M2 (E-907 naming E-902)` | `['E-907 (line 7): a second membership row (the first, E-905, governs)']` | **Permanent lock-in:** true `membership:` row can never be recorded |
| `bad_go (E-900 before pin), void(E-901 -> E-900), P13 (E-902), G13 (E-903), M (E-904 naming E-900), void(E-905 -> E-904)` | **`[]` (clean!)** | **Returns `E-900`** (a voided, unpinned go row!) |
| Same with impossible-date go row `E-901` (`2026-13-45`) | **`[]` (clean!)** | **Returns `E-901`** (impossible date!) |
| Valid freeze `E-903 -> E-902` + unclosed fence ` ``` ` + malformed go row `E-904` | 1 problem | **Returns `E-902`** (swallows all unvoided go problems) |

Additionally, at l.2158, `withdrawn` checks `tokens and tokens[0][0] < i` rather than the frozen event, so if `prereg/`
drift breaks `G13` and empties `tokens`, a `withdrawn` closing row is accepted after the frozen membership event.

**Remedy.**
1. In `membership_event`, raise `GoRefused` whenever `s["problems"]` is non-empty — never swallow unvoided go problems
   (including unclosed fences, hidden breaks, or unvoided membership disagreements).
2. A mistaken `membership:` row that is voided must **not** remain in `memberships` as the governing freeze or block a
   corrected `membership:` row (skip voided `membership:` rows when they disagree with `tokens[0]`, or skip voided
   `membership:` rows generally while requiring `prereg/` drift — the original F3 hole — to be repaired in `prereg/`
   rather than cleared by voiding a valid `membership:` row; remember a void of a *valid* row is already a no-op, so
   an accidental `prereg/` stray file breaks `G13` and triggers a hard disagreement problem until the stray file is
   removed, never moving the event!).
3. Require `named` to satisfy `_valid_day(g["date"])`, and compare `withdrawn` (l.2158) against `frozen[3]` when frozen.
4. Add tests for all four rows of the table above.

---

### 3 (MATERIAL, paired reader + template). F4's plan allow-list breaks `wt-lit`'s Q-212 test on merge and is undocumented in T and GK

**Where.**
- `08b0b7a:extended/reader.py` l.1917 (`_FIRM_LINE`), l.2043-2050 (`design_search_problems`);
- `374f333:tests/test_design_search_template.py` l.2138-2142 (`test_q212_the_deciding_files_field_and_mffus_exact_form`);
- `374f333:prereg/TEMPLATE_design_search.md` l.53-60; `374f333:.claude/agents/prereg-gatekeeper.md` l.55-61.

**Evidence (Probe 2a, 2b).**
- `08b0b7a` changed `_FIRM_LINE` to require `<firm>, <plan>` where `<plan>` matches `[A-Za-z0-9_]+` and is listed by
  `firm_plans()` (`combine50k`, `rapid50k`, `flex50k`, etc.).
- `374f333`'s `test_q212_the_deciding_files_field_and_mffus_exact_form` (which currently skips on `wt-lit` only because
  `wt-lit`'s reader predates Q-212, and explicitly notes `"the assertion fails, not skips, once it does"`) constructs a
  template draft with `"MFFU, Rapid 50K"` and asserts `RD.design_search_problems(draft) == []`.
- Running that exact draft against `08b0b7a`'s `design_search_problems` **fails**:
  `["the firm field is not exactly `- **The firm and account:** <one of Topstep, MFFU, Lucid>, <its plan>` (optionally ` -- <text>`): '- **The firm and account:** MFFU, Rapid 50K -- **exactly one'"]`.
  With `"MFFU, rapid50k"`, it returns `[]`.
- Neither T l.53-60 nor GK item 0 states that `<plan>` must be the verified rules record's plan key (`firm_plans()`,
  e.g., `combine50k`, `rapid50k`, `flex50k`), so any author following T or GK will write prose like `Rapid 50K` or
  `50K Combine` and be refused at the go row.

**Remedy.** Update T section 1, GK item 0, and TT l.2139 (`"MFFU, rapid50k"`) to specify the verified rules-record plan
key (`firm_plans()`), and verify TT passes with `08b0b7a`'s reader before merging.

---

### 4 (MATERIAL, template side). `_cw_problems` ignores `heldout-void`, creating a permanent fast-tier lock-in on any voided later confirmation-window row

**Where.** `374f333:tests/test_design_search_template.py` l.1900-1922 (`_cw_problems`), l.1945 (asserted on real
`DECISIONS.md`).

**Evidence (Probe 8a, 8b).**
- `08b0b7a:extended/reader.py` l.914-918 makes a later NQ/MNQ confirmation-window row **voidable** via `heldout-void`.
- `374f333`'s `_cw_problems` reads `RD.heldout_tokens(log, "window")` (which still includes voided valid tokens) and
  unconditionally appends a problem for every `wins[1:]` without consulting `heldout-void`.
- On `win1 + win2 + heldout-void(win2)`:
  - `08b0b7a` `heldout_token_problems`: `[]` (clean);
  - `374f333` `_cw_problems`: `['E-907: a later NQ window row from 2026-07-17 on (the first governs)']`.
  Because `DECISIONS.md` is append-only and TT l.1945 runs `_cw_problems(ROOT / "DECISIONS.md") == []` in the fast tier,
  one accidental later confirmation-window row — even after following the reader's prescribed void recovery — fails the
  fast tier **forever**.
- Additionally (Probe 8b), `_cw_problems` uses `lines = log.splitlines()` (l.1907) while `RD.heldout_tokens` uses
  `_split()`. Any hidden break above `wins[0]` shifts `lines[first.pos]` onto the wrong line (returning a spurious
  `"does not state that it opens the confirmation window"` or `IndexError`).

**Remedy.** Ignore `later` rows that have a later `heldout-void` targeting `w.row` (matching `reader.py:916`), replace
`log.splitlines()` with `RD._split(log)`, and add a synthetic test for a voided later confirmation-window row.

---

### 5 (MATERIAL, merge conflicts & lead-owned `.claude/` / DF overwrites). `wt/wt-lit` (`374f333`) conflicts with master's Q-210, E-280 (6), and H3 pin guard, and contradicts E-274 (3) inside `worker-protocol`

**Where.** `git diff 7c047a3 374f333 -- .claude/ tests/test_declarations_fixed.py`.

**Evidence.** `374f333` merged `6502d87` and therefore predates master's `e7f27c8` (Q-210), `7e13006` (H3 text 2), and
`7c047a3` (E-277..E-280).

- **Direct merge conflicts (resolving toward `wt-lit` would silently delete master's lead-owned rules):**
  1. `.claude/agents/prereg-gatekeeper.md` (Step 0): master (`7c047a3`) mandates `python scripts/decl_lint.py <file>`
     first (Q-210); `374f333` still reads `"No validator reads this repository's declarations field by field ...
     machine check: none exists for declarations"`.
  2. `.claude/commands/prereg.md` (Step 4): master (`7c047a3`) runs `python scripts/decl_lint.py <file>` before review
     (Q-210); `374f333` omits it.
  3. `.claude/skills/merge-checklist/SKILL.md` (Section 3): master (`7c047a3`, E-280 (6)) runs
     `python identity/stage2_identity.py --paths 4` under `run.lock` (because identity tests are marked `heavy`) and
     sets the slow-test timeout to `3600`; `374f333` drops the identity command and reverts the timeout to `1800` with
     the obsolete comment that `-m "slow and not heavy"` runs the 4-path identity.
  4. `tests/test_declarations_fixed.py`: master (`7c047a3`) carries `PIN`, `AWAITING_PIN`,
     `test_the_pin_grammar_reads_every_kind_of_declaration`, and
     `test_every_pinnable_declaration_is_pinned_or_awaiting_its_row` (H3 pin grammar); `374f333` lacks all four.
- **Non-conflicting `.claude/` files in `374f333` carrying stale or self-contradictory rules:**
  5. `.claude/skills/worker-protocol/SKILL.md` Section 3a item 12 (l.119) says `"The commit-message file in your own
     worktree"`, directly contradicting E-274 (3) (`"Commit-message and log files live outside the worktree"`) in
     Section 3 item 4 of the *same file*.
  6. `.claude/skills/prereg-discipline/SKILL.md` still states `"there is no validator for this repository's
     declarations"`, contradicting Q-210 (`scripts/decl_lint.py`).
  7. `.claude/skills/merge-checklist/SKILL.md` (Section 2, `"the review rule"`) and `.claude/agents/red-team.md` still
     require `"a full re-read"` for every fix round answering a blocking finding, whereas E-274 (9) and E-280 (6)
     established the red-team diff check per fix round while material findings remain.

**Remedy.** Merge master `7c047a3` into `wt/wt-lit` before hand-back/merge, explicitly keeping master's Q-210
(`decl_lint.py`), E-280 (6) (`stage2_identity.py --paths 4`, `3600` timeout), and DF's H3 `PIN`/`AWAITING_PIN` guard;
fix `worker-protocol/SKILL.md` 3a.12 ("outside the worktree") and `prereg-discipline/SKILL.md` (`decl_lint.py`), and
reconcile the E-274 (9) / E-280 (6) diff-check wording.

---

### 6 (MINOR, reader side). F8's `--text` splits on literal NUL bytes in `r.stdout.split("\x00")`; `_verdict_key` misses in-place row-ID renumbering

**Where.** `08b0b7a:extended/reader.py` l.1172-1175 (`_verdict_key`), l.1210-1231 (`_verdict_commits`).

**Evidence (Probe 7a, 7b, 7c).**
- **Literal NUL (7a, 7b):** `test_reader_q212b.py` tested `.gitattributes: DECISIONS.md binary`, not a literal NUL byte.
  With `--text`, git outputs any literal `\x00` inside `DECISIONS.md`'s diff, which splits `r.stdout.split("\x00")[1:]`
  mid-diff; the fragment fails `re.fullmatch(r"[0-9a-f]{40}", h)` and `_verdict_commits` returns `None`. That fails
  closed on case (d) (cannot bypass order), **but** a literal NUL in *any* historical commit of `DECISIONS.md` (even an
  unrelated earlier row) permanently causes `_verdict_commits` to return `None` for all verdicts.
- **Row-ID renumbering (7c):** `_verdict_key` keys on `(row, market, decl, sha)`. If commit X (before the read) adds
  verdict `E-980` and commit Y (after the read) edits `E-980` -> `E-981` in place (same market, decl, sha),
  `_verdict_commits(repo, V_981)` returns `[Y]` only (missing X).

**Remedy.** Use a multi-byte commit separator that cannot collide with a single NUL (or iterate commits via `rev-list`
+ `diff-tree -p`), and match verdict commits by `(market, decl, sha)` (or `row` OR `(market, decl, sha)`). Add tests
for a literal NUL byte and row-ID renumbering.

---

### 7 (MINOR, reader side). `go_row_present` omits `--no-replace-objects` and ignores uncommitted working-tree `DECISIONS.md` when `log_text` is omitted

**Where.** `08b0b7a:extended/reader.py` l.2244-2302 (`_git_bytes`, `go_row_present`).

**Evidence (Probe 4a, 4b).**
- **Replace refs (4b):** Modifying and committing `scripts/survey.py` after `runner` makes `go_row_present` return
  `False`; running `git replace <runner> <fake_commit_with_tampered_tree>` flips `go_row_present` back to **`True`**,
  because `_git_bytes`, `_blob`, and `_git(root, "merge-base", ...)` do not pass `--no-replace-objects` (unlike F8's
  `_gitnr`).
- **Dirty `DECISIONS.md` (4a):** Appending an uncommitted finalists' row to working-tree `DECISIONS.md` and calling
  `go_row_present(decl)` (with default `log_text=None`) returns **`True`**, because `go_row_present` reads only
  `HEAD:DECISIONS.md` without verifying the working-tree `DECISIONS.md` matches it.

**Remedy.** Pass `--no-replace-objects` in `_git_bytes`, `_blob`, and `go_row_present`'s ancestry check, and require
`(root / "DECISIONS.md").read_bytes().replace(b"\r\n", b"\n") == committed.replace(b"\r\n", b"\n")`.

---

### 8 (MINOR, template side). Stale `RDPIN` wording ("`extended/reader.py` at its pinning row's sha256") left unchanged after F1

**Where.** `374f333:prereg/TEMPLATE_design_search.md` l.51, 62, 673, 693; `prereg/TEMPLATE_heldout_test.md` l.84;
`.claude/agents/prereg-gatekeeper.md` l.59, 97; `tests/test_design_search_template.py` l.1852 (`RDPIN`).

**Evidence.** `READER_Q212_TEMPLATE` finding 1's remedy specified changing "`extended/reader.py` at its pinning row's
sha256" to "at the go row's runner commit" for per-search checks once `extended/reader.py` is allowed to evolve after
the template pin. All seven occurrences (including the two new deciding-files sentences in T l.62 and GK l.59) still
cite the template pinning row's sha256.

**Remedy.** Update `RDPIN` in T, HT, GK, and TT so per-search checks (`go_row_present`, `go_problems`) cite
`extended/reader.py` at the go row's runner commit.

---

### 9 (MINOR, reader side). F7's search-years guard for superseded purposes accepts any existing non-F/RD file as `declaration`

**Where.** `08b0b7a:extended/reader.py` l.1552-1558 (`authorise`).

**Evidence (Probe 6a).** For a search-years read under a superseded purpose (`modes_scorecard`), line 1552 refuses only
`declaration is None or E_ID.fullmatch(str(declaration))`, stating the read *"names its own pinned declaration (an F- or
RD- file), never none or a decision row"*. Because `_exists` accepts any file in `repo`,
`authorise("2020-01-02", "2023-12-29", purpose="modes_scorecard", declaration="CHARTER.md", repo=REPO)` is **allowed**
(`declaration="CHARTER.md"`).

**Remedy.** When `purpose in _superseded_purposes(tree)` on the search years, require `declaration` to resolve to a
pinned `prereg/(F|RD)-*.md` file (present in `DECISIONS.md` by `PIN` at its LF sha256) that is not superseded for that
purpose.

---

### 10 (MINOR, reader side). F5 leaves bare mid-line `\r` unflagged, and a preamble hidden break above the first row is unvoidable

**Where.** `08b0b7a:extended/reader.py` l.765-797 (`_split`, `_HIDDEN_BREAKS`, `_break_problems`).

**Evidence (Probe 5a, 5b).**
- **Bare `\r` (5b):** `"prose\r| E-902 | ..."` is not matched by `_HIDDEN_BREAKS` (`go_problems == []`,
  `heldout_token_problems == []`), so `_split` keeps 2 lines while `str.splitlines()` (still used in DF, TT
  `_cw_problems`, and `reader.py:missing_lines`) splits it into 3.
- **Preamble hidden break (5a):** A U+2028 on line 1 before the first `| E-NNN |` row has `row = None`;
  `if row is not None and any(...)` can never clear it by an appended `heldout-void` (permanent lock-in if ever present
  in an append-only log; real `DECISIONS.md` has none).

**Remedy.** Include `\r` in `_HIDDEN_BREAKS` (safe because `_split` strips one trailing `\r` from each `\n`-delimited
line before `_break_problems` scans it, so only bare mid-line or doubled `\r` remains), and note preamble-break
immutability (guarded by `decisions_append_only.py`).

---

## Notes

- **n1 (F4 tail blacklist).** `08b0b7a` closes `<plan>` via `firm_plans()` (matching E-280 (4)), while the optional
  ` -- <text>` tail still checks `_FIRM_NAMES`'s 8-name blacklist. Probe 2c confirmed `"Topstep, combine50k -- shared
  with Alpha Futures 50K"`, `"... -- via MFF"`, `"... -- also FundedNext"`, `"... -- shared with Earn2Trade"`,
  `"... -- Elite Trader Funding"`, and `"... -- also DayTraders eod50k"` all return `[]`. (Gatekeeper reading still
  covers the tail.)
- **n2 (n1 MNQ-first ordering).** Probe 8c showed that if an accidental `MNQ` confirmation-window row appears before
  the `NQ` confirmation-window row, `_window_rows` drops the `NQ` row as `cw[1]` and keeps only `MNQ`, causing
  `heldout_window(log, "NQ", ...)` to fall back to `BASE_WINDOW_ROW`.
- **n3 (F10 mutant verification).** Replaying all 131 golden cases of `08b0b7a` gave 0 baseline failures, and in-memory
  single-line mutations confirmed all 9 go-token surviving mutants from `READER_Q212_TEMPLATE` are now killed: `m10` (1
  case), `m12` (1), `m20` (1), `m29` (2), `m32` (1), `m53` (1), `m55` (1), `m59` (2), `m60` (1). Code inspection of
  `test_reader_superseded.py::test_an_edited_superseded_file_at_its_own_path_is_refused` confirms `m47b` is killed too.
- **n4 (Real log & rules record).** On real `DECISIONS.md` (`7c047a3`), `08b0b7a` returns `go_problems == []`,
  `heldout_token_problems == []`, `membership_event == None`. O-7 pin rows `E-268..E-272` each carry only their new
  `RD-06..RD-10` pin in `PIN.findall` (no false positive against `SUPERSEDED`). In `config/rules_extended.yaml`,
  `lucid.flex50k` currently has only `unstated`/`unverified` keys, so `firm_plans()` intentionally does not filter by
  `status == "verified"` (`extended/firm_terms.py` enforces verified keys at load).

---

## What I tried that found nothing

- **F2 (non-replace checks):** verified `go_row_present` binds `ROOT`, rejects nested `prereg/`, rejects other trees'
  declarations, rejects uncommitted go rows when `HEAD:DECISIONS.md` lacks them, catches `--skip-worktree` and
  `--assume-unchanged` edits to deciding files via direct blob comparison, and rejects a caller `log_text` differing
  from `HEAD:DECISIONS.md`.
- **F6:** verified `go_row_present` checks `heldout_token_problems(log)` before returning `True`, stopping rounds on
  malformed finalists' rows (and resuming if voided).
- **F7 (RD-05 part F & O-7 pins):** verified `RD-05` is refused on all three part-F purposes (`modes_scorecard`,
  `modes_ladder_beside`, `modes_gate_beside`) while keeping its steps 0-2 on the search years; verified `E-080`
  resolves to RD-01; verified `test_rd_search_years_drafts.py`'s `SUPERSEDED_LIST` exemption skips only the reader's
  `SUPERSEDED` assignment; verified O-7 pin rows `E-268..E-272` trigger no false positives in `PIN.findall`.
- **F8 (non-NUL / non-renumbering cases):** verified shallow clone returns `None`, replace refs are ignored via
  `--no-replace-objects`, `.gitattributes binary` / `-diff` / `textconv` are bypassed via `--text --no-textconv`, root
  commits are read via `--root`, and tail-text edits in place match by `_verdict_key`.
- **F9, n2, n3 (template text):** verified F9's another-underlying requirement appears in T, HT, and GK; verified n2's
  `"refused by the gatekeeper at its pin and by the reader at the go row"` appears in T and HT; verified n3's market
  free-text rule appears in T.
- **n4 (`membership_event` default `prereg_dir`):** verified `Path` input uses `log_text.parent / "prereg"` and a raw
  `str` not matching `ROOT / "DECISIONS.md"` raises `GoRefused`.
- **F10:** all 10 previously surviving mutants killed (n3 above).

## What I could not check

- **Full pytest suite and real merge-tree execution:** omitted per tight memory constraints; all behavioral checks ran
  as targeted in-memory / synthetic-repo Python probes on the exact git blobs at `08b0b7a`, `374f333`, and `7c047a3`.
- **Every non-conflicting prose change across the 17 `.claude/` files in `wt-lit`:** checked all master-touched files
  and targeted rule contradictions (`decl_lint`, `stage2_identity`, `E-274`, `C3-2`, `full re-read`, `worktree`), not a
  line-by-line editorial audit of Wave 2's older `.claude/` rewrite.
- **A real survey runner calling `go_row_present`:** verified on the reader function and synthetic git trees only.
