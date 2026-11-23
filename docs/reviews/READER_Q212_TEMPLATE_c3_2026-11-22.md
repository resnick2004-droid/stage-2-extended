# Red team diff check: paired Reader (Q-212 round 3) + Template v3 fixes (`READER_Q212_TEMPLATE_c3`)

**Reviewer:** red team, 2026-11-22.

**Targets (read-only from git history, workspace untouched)**
- **Reader side (`wt/wt-verify`):** `git diff 08b0b7a..67cdd5e` (`extended/reader.py`, `tests/go_cases.py`,
  `tests/data/go_token_golden.json`, `tests/test_reader_q212b.py`). Line numbers below for the reader side are at
  `67cdd5e`.
- **Template side (`wt/wt-lit`):** `git diff 374f333..4f4d007` (`.claude/agents/prereg-gatekeeper.md`,
  `.claude/commands/prereg.md`, `.claude/skills/merge-checklist/SKILL.md`, `.claude/skills/prereg-discipline/SKILL.md`,
  `.claude/skills/worker-protocol/SKILL.md`, `prereg/TEMPLATE_design_search.md`, `prereg/TEMPLATE_heldout_test.md`,
  `tests/test_declarations_fixed.py`, `tests/test_design_search_template.py`). Line numbers below for the template side
  are at `4f4d007`.
- **Master comparison:** `git diff 6502d87..c4965bf` and read-only `git merge-tree` against current master HEAD
  (`c4965bf`).

**Method**
- Inspected both full diffs (`08b0b7a..67cdd5e` and `374f333..4f4d007`) and surrounding code at `67cdd5e` and `4f4d007`
  directly from git blobs.
- Ran read-only Python synthetic probes (`OMP_NUM_THREADS=1`) in disposable temp directories (all cleaned up; full
  pytest suite not run; no bars, no atlas, nothing from 2026-07-17 read; no declared seed literals quoted):
  - **Probe F1:** initial-commit staged pin, staged pin with unstaged reader mismatch (fails) vs staged reader match
    (passes), `--no-ff --no-commit` merge pre-commit and post-merge after later reader edit, U+2028 above pin.
  - **Probe F2:** (a) clean `prereg/` with valid `G13` + `M1` + no-op `heldout-void` on `E-902`; (b) drifted `prereg/`
    (`F-13_y.md`) + `void(E-902)` + `void(E-903)` alongside `G14`; (c) voiding valid `M1` + second `M2`; (d) unvoided
    before-pin go row `E-900` + `M` naming `E-900`.
  - **Probe F3:** ran `4f4d007` `test_design_search_template.py` Q-212 tests (including
    `test_q212_the_deciding_files_field_and_mffus_exact_form`) directly against `67cdd5e:extended/reader.py`.
  - **Probe F4:** `_cw_problems` on voided later confirmation window, U+2028 above window, voided bad first window, and
    real `DECISIONS.md`.
  - **Probe F5:** byte-by-byte diff of `tests/test_declarations_fixed.py` l.1-86 vs `c4965bf`, read-only
    `git merge-tree 6502d87 c4965bf 4f4d007` and `git merge-tree 6502d87 c4965bf 67cdd5e`, and check of
    `merge-checklist/SKILL.md` and `red-team.md` for E-274 (9) / E-280 (6) wording.
  - **Probe F6:** `_verdict_commits` with historical literal NUL, in-place row-ID renumbering (`E-980` -> `E-981`), and
    spoofed commit marker inside `DECISIONS.md`.
  - **Probe F9:** `authorise` on search years under superseded purpose `firm_gate_beside` with `CHARTER.md`, unpinned
    `prereg/F-99_bogus.md`, repo-root `F-99_root.md`, shorthand `F-99`, and an absolute `Path` to pinned
    `prereg/RD-06_firm_contracts_search_years.md`.
  - **Probe F10:** normal CRLF, mid-line bare `\r`, doubled `\r\r\n`, and EOF bare `\r`.
  - **Golden & targeted pytest:** replayed all 132 golden cases at `67cdd5e` (0 failures); ran targeted `pytest` with
    `-p no:cacheprovider` on `wt-verify`'s `test_reader_q212b.py`, `test_reader_go.py`, `test_reader_superseded.py`
    (196 passed) and `wt-lit`'s `test_declarations_fixed.py`, `test_design_search_template.py` (69 passed, 2 skipped
    only for `wt-lit`'s pre-Q-212 reader — both passed in Probe F3 against `67cdd5e`).

---

## Verdict: **BLOCK** (`wt/wt-verify` `67cdd5e` **BLOCK**; `wt/wt-lit` `4f4d007` **PASS WITH MINORS**)

One **MATERIAL** regression on the reader side (`67cdd5e`) blocks merge, plus three **MINOR** findings remaining from
c2 (`F5` item 7 on `wt-lit`; `F6` row-ID renumbering + unanchored separator and `F9` unpinned/absolute-path check on
`wt-verify`). All other c2 findings (**F1, F3, F4, F7, F8, F10**) are verified fixed.

**Counts: 0 CHANGES-A-CONCLUSION, 1 MATERIAL, 3 MINOR, 3 NOTE.**

| # | Severity | Side | c2 ref | File:line | One-line summary |
|---|---|---|---|---|---|
| 1 | MATERIAL | reader | F2 | `67cdd5e` reader l.2135-2137, 2194-2200 | `not later_void(g["row"], j)` lets a no-op void on valid `E-902` break a valid freeze and lock out re-freezing forever, and under `prereg/` drift (`F-13_y.md`) voiding `E-902`+`E-903` silently moves `membership_event` to `E-904` with `go_problems == []` |
| 2 | MINOR | template / `.claude/` | F5 (item 7) | `4f4d007` `merge-checklist/SKILL.md` l.26, `red-team.md` l.38 | Both files still require `"a full re-read"` for every blocking fix round, leaving c2 F5 item 7's E-274 (9) / E-280 (6) diff-check reconciliation unaddressed |
| 3 | MINOR | reader | F6 | `67cdd5e` reader l.1172-1175, 1211, 1218 | `_verdict_key` still includes `row`, missing in-place row-ID renumbering (`E-980` -> `E-981`); separator regex at l.1218 lacks `(?m)^` anchor (spoofable by diff content to return `None`); dead local `sep` at l.1211 |
| 4 | MINOR | reader | F9 | `67cdd5e` reader l.1553-1560 | String-only regex accepts unpinned `prereg/F-99_bogus.md` and repo-root `F-99_root.md` under a superseded purpose, while falsely refusing a legitimate absolute `Path` to pinned `prereg/RD-06_*.md` |
| n1 | NOTE | merge | F5 | `4f4d007` + `67cdd5e` vs `c4965bf` | Neither branch merged master since `6502d87`; `git merge-tree` shows mechanical conflicts in `prereg-gatekeeper.md`, `prereg.md`, and `test_declarations_fixed.py` (resolved cleanly by taking `4f4d007` plus `67cdd5e`'s `judged_line_problems` in DF) |
| n2 | NOTE | template | F8 | `4f4d007` T l.51/62/673/693, HT l.84, GK l.66/104, TT l.1852 | `RDPIN` updated everywhere to `"at the run's commit (pinned at its template pin row)"`; the parenthetical could still be misread as pinning the run's reader to the template pin row rather than the go row's runner commit |
| n3 | NOTE | template | F1 | `4f4d007` DF l.148 | `git show :extended/reader.py` omits `--no-replace-objects` (trivial consistency gap vs the other git calls in `_reader_at_row`) |

---

## Status of c2 Findings (F1-F10)

| c2 # | Severity in c2 | Status in c3 | Notes |
|---|---|---|---|
| F1 | MATERIAL | **FIXED** | Pre-commit staged pin (initial commit, mismatch, match, `--no-ff` merge) + post-merge later reader edit + U+2028 all pass (Probe F1) |
| F2 | MATERIAL | **BLOCKED (regression)** | Hijack/lock-in of mistaken `membership:` rows fixed, but new `not later_void(g["row"], j)` breaks no-op voids on valid `E-902` and defeats F3's freeze under `prereg/` drift (Finding 1 below) |
| F3 | MATERIAL | **FIXED** | `firm_plans()` plan key documented in T, GK, TT; `4f4d007` TT Q-212 tests pass directly against `67cdd5e:extended/reader.py` (Probe F3) |
| F4 | MATERIAL | **FIXED** | `_cw_problems` uses newline-only split and honours `heldout-void` on later confirmation-window rows (Probe F4) |
| F5 | MATERIAL | **PARTIAL (MINOR)** | Q-210 (`decl_lint.py`), E-280 (6) (`stage2_identity.py --paths 4`, `3600`), E-274 (3) (`worker-protocol` 3a.12), and DF H3 `PIN`/`AWAITING_PIN` all synced; item 7 (`"full re-read"` vs diff-check wording) untouched (Finding 2) |
| F6 | MINOR | **PARTIAL (MINOR)** | Literal NUL byte fixed; row-ID renumbering (`_verdict_key`) untouched, separator regex unanchored, unused `sep` (Finding 3) |
| F7 | MINOR | **FIXED** | `--no-replace-objects` added to `_blob`, `_git_bytes`, `HEAD`, and `merge-base`; dirty working-tree `DECISIONS.md` rejected when `log_text=None` |
| F8 | MINOR | **FIXED (NOTE)** | All 7 occurrences + TT `RDPIN` updated; no stale `"pinning row's sha256"` remains (n2) |
| F9 | MINOR | **PARTIAL (MINOR)** | `CHARTER.md` now refused, but regex still allows unpinned `prereg/F-99_bogus.md` / root `F-99_root.md` and falsely refuses absolute `Path` to pinned `RD-06` (Finding 4) |
| F10 | MINOR | **FIXED** | `\r` added to `_HIDDEN_BREAKS`; mid-line `\r` and doubled `\r\r\n` flagged as `U+000D` (voidable), CRLF and EOF `\r` clean (Probe F10) |

---

## Findings

### 1 (MATERIAL, reader side). F2's `not later_void(g["row"], j)` breaks no-op voids on valid go rows and lets `prereg/` drift + voids silently move a frozen `membership_event`

**Where.** `67cdd5e:extended/reader.py` l.2135-2137, l.2194-2200 (`_go_scan`); `67cdd5e:tests/go_cases.py` l.222-225
(deleted `"frozen, the problem voided, the event still kept"`).

```python
# extended/reader.py l.2135-2137
named = next((j for j in range(i) if not fenced[j] and (g := GO_TOKEN.match(lines[j]))
              and _valid_day(g["date"]) and not later_void(g["row"], j)
              and g["row"] == m["go"] and g["decl"] == m["decl"] and g["sha"] == m["sha"]), None)
```

**Evidence (Probe F2-A, F2-B).**
1. **No-op void breaks valid freeze & locks out freezing (Probe F2-A):** On a completely clean `prereg/` (`F-13`,
   `F-14`, `F-15`) with `[P13, G13 (E-902), P14, M1 (E-903 -> E-902), G14 (E-904), void(E-905 -> E-902)]`:
   - `E-902` is a valid counted go row (`tokens[0]`), so `heldout-void: E-902` is supposed to be a **no-op** (template
     l.671: *"a void of a valid row being a no-op"*).
   - Because l.2136 tests `not later_void(g["row"], j)` without checking whether `j` is in `tokens`, `named` becomes
     `None`:
     - `go_problems`: `['E-903 (line 4): a membership row naming no unvoided go row E-902 for F-13 at that sha256 above it']`
     - `membership_event`: raises `GoRefused`.
   - Even if `E-903` is then voided, no replacement `membership:` row can ever name `E-902` again because
     `later_void("E-902", 1)` remains `True` permanently.
2. **F3's freeze invariant defeated under `prereg/` drift (Probe F2-B):** With `F-13_y.md` added to `prereg/` (the
   exact drift scenario F3 was introduced to defend against) and
   `[P13, G13 (E-902), P14, M1 (E-903 -> E-902), G14 (E-904), void(E-905 -> E-902), void(E-906 -> E-903)]`:
   - `G13` fails `file_problems("F-13")` -> suppressed by `void(E-905 -> E-902)` -> excluded from `tokens`.
   - `M1` sees `later_void("E-902", 1) == True` -> `named = None` -> suppressed by `void(E-906 -> E-903)` -> excluded
     from `memberships`.
   - `G14` becomes `tokens[0]`.
   - Result: `go_problems == []` (clean!) and `membership_event` silently returns **`| E-904 | 2026-12-05 | go: F-14 @ ...`**!
     The frozen membership event moved from `E-902 (F-13)` to `E-904 (F-14)` with zero problems.

**Remedy.**
1. At l.2135-2137, match `j` whenever `j` is a counted go row (`any(t[0] == j for t in tokens)` — so a no-op void on a
   valid go row never invalidates `named`), **or** `j` is an unfenced valid-date `GO_TOKEN` that was **not voided before
   `i`** (`not any(j < p < i for p in voids.get(g["row"], ()))`) and had a counted pin strictly before `j` at `g["sha"]`
   (so an earlier voided or unpinned go row like `E-900` is still rejected, while a formerly valid frozen `E-902` under
   later `prereg/` drift still binds `M1` even if someone appends `void(E-902)` afterward).
2. At l.2194-2200, do **not** suppress the `first != frozen` disagreement via `if not later_void(frozen[1], frozen[0]):`
   — once a `membership:` row passed l.2149 and became `frozen`, any later `prereg/` drift must be repaired in
   `prereg/`, never cleared by voiding the freeze row.
3. Add regression tests for both Probe F2-A (no-op void on valid `E-902` leaves `M1` clean and `membership_event == G13`)
   and Probe F2-B (`F-13_y.md` + `void(E-902)` + `void(E-903)` still produces a problem and `GoRefused`, never returning
   `E-904`).

---

### 2 (MINOR, template / `.claude/` side). E-274 (9) / E-280 (6) diff-check wording still unaddressed in `merge-checklist` and `red-team` (c2 F5 item 7)

**Where.** `4f4d007:.claude/skills/merge-checklist/SKILL.md` l.26; `4f4d007:.claude/agents/red-team.md` l.38.

**Evidence.** Both files still state that a branch answering a blocking finding goes back to the red team for *"a full
re-read"*, whereas E-274 (9) and E-280 (6) established the red-team diff check per fix round while material findings
remain. All other items of c2 F5 (Q-210 `decl_lint.py` in `prereg-gatekeeper.md`, `prereg.md`, and
`prereg-discipline/SKILL.md`; E-280 (6) `stage2_identity.py --paths 4` and `3600` timeout in
`merge-checklist/SKILL.md`; E-274 (3) outside-worktree commit files in `worker-protocol/SKILL.md` 3a.12; and master's
`PIN`/`AWAITING_PIN` guard in `tests/test_declarations_fixed.py`) are cleanly fixed.

**Remedy.** Update those two sentences to reflect the E-274 (9) / E-280 (6) diff-check rule (or record an explicit
deferral).

---

### 3 (MINOR, reader side). `_verdict_commits` still misses in-place row-ID renumbering and uses an unanchored separator regex (c2 F6)

**Where.** `67cdd5e:extended/reader.py` l.1172-1175 (`_verdict_key`), l.1211 & l.1218 (`_verdict_commits`).

**Evidence (Probe F6-a, F6-b, F6-c).**
- Probe F6-a confirmed literal NUL bytes in historical `DECISIONS.md` commits no longer break `_verdict_commits`.
- **Row-ID renumbering (Probe F6-b):** `_verdict_key` still returns `(m["row"], m["market"], m["decl"], m["sha"])`.
  When commit `c1` adds verdict `E-980` and commit `c2` renumbers it in place to `E-981` (same market, decl, sha),
  `_verdict_commits(t, v981)` returns `[c2]` only, missing `c1`.
- **Unanchored separator (Probe F6-c):** Line 1218 matches
  `r"\x00S2X_VERDICT_COMMIT:([0-9a-f]{40})\x00(?:\r?\n|$)"` without `(?m)^`. A `DECISIONS.md` line containing that
  literal byte sequence splits a diff chunk (causing `_commit_holds_line` to fail on the spoofed hash and returning
  `None`). Anchoring with `(?m)^` cannot match any git `-p` content line (which always begins with `+`, `-`, or ` `).
  Line 1211's `sep = "\x00S2X_VERDICT_COMMIT:"` is also an unused dead local.

**Remedy.** Drop `m["row"]` from `_verdict_key` (key on `(m["market"], m["decl"], m["sha"])`), anchor the regex at
l.1218 with `(?m)^`, remove dead `sep` at l.1211, and add a row-ID renumbering test.

---

### 4 (MINOR, reader side). F9's superseded-purpose guard uses a path-string regex instead of checking a pinned `prereg/` declaration

**Where.** `67cdd5e:extended/reader.py` l.1553-1560 (`authorise`).

```python
and (declaration is None or E_ID.fullmatch(str(declaration))
     or not re.fullmatch(r"(?:prereg/)?(?:F|RD)-\d+(?:_[^/\\]+\.md)?",
                         str(declaration).replace("\\", "/")))
```

**Evidence (Probe F9).** Under superseded purpose `firm_gate_beside` on the search years (`2020-01-02` to `2023-12-29`):
- `declaration="CHARTER.md"` is now properly **REFUSED** (`SupersededRefused`).
- **Unpinned files allowed:** `declaration="prereg/F-99_bogus.md"`, repo-root `declaration="F-99_root.md"`, and
  shorthand `declaration="F-99"` (resolving to unpinned `prereg/F-99_bogus.md`) are all **ALLOWED**, despite the
  error text stating a read under a superseded purpose *"names its own pinned declaration (an F- or RD- file)"*.
- **Legitimate absolute `Path` falsely refused:** `declaration=tree / "prereg" / "RD-06_firm_contracts_search_years.md"`
  (which `_exists` at l.1529 and `_declaration_files` at l.1392 both accept) raises **`SupersededRefused`** because
  `str(declaration)` starts with the absolute tree path rather than `prereg/`.

**Remedy.** Resolve `files = _declaration_files(declaration, tree)` and require `len(files) == 1`, its repo-relative
path `_rel(files[0], tree)` matching `prereg/(?:F|RD)-\d+[^/]*\.md`, and `(rel, sha256_lf(files[0]))` present in
`PIN.findall(_decisions(tree))`.

---

## Notes

- **n1 (Merge state vs `c4965bf`).** Neither `wt/wt-verify` nor `wt/wt-lit` merged master after `6502d87` (per E-274's
  rule against asking workers to commit conflicted merges of master). Read-only `git merge-tree` confirms mechanical
  3-way conflicts in `prereg-gatekeeper.md`, `prereg.md`, and `tests/test_declarations_fixed.py` for `wt-lit`, and in
  `tests/test_declarations_fixed.py` for `wt-verify`. Because `4f4d007` lines 1-86 of `test_declarations_fixed.py` match
  `c4965bf` byte-for-byte and its `.claude/` files carry master's Q-210 and E-280 (6) edits, the lead can resolve at
  merge time by taking `4f4d007`'s `.claude/` files and combining master's `PIN`/`AWAITING_PIN` + `wt-verify`'s
  `judged_line_problems` + `wt-lit`'s `_template_pin_problems` in `test_declarations_fixed.py`.
- **n2 (F8 `RDPIN` parenthetical).** All 7 occurrences in T, HT, GK and `RDPIN` in TT now read
  `` `extended/reader.py` at the run's commit (pinned at its template pin row) ``, removing the stale `"at its pinning
  row's sha256"`. The parenthetical `(pinned at its template pin row)` is slightly ambiguous once the reader evolves
  (the template pin row pins the old reader; each run's reader is bound by the go row's runner commit and deciding
  files).
- **n3 (F1 staged blob replace ref).** `4f4d007:tests/test_declarations_fixed.py` l.148 calls
  `_git(root, "show", ":extended/reader.py")` without `--no-replace-objects` (trivial consistency gap vs lines 144,
  153, 157, 160).

---

## What I tried that found nothing

- **F1 (`4f4d007` DF):** staged uncommitted pin on initial commit (no HEAD), staged pin matching staged reader, staged
  pin failing when staged reader is stale despite updated working-tree reader, `--no-ff --no-commit` merge pre-commit,
  post-merge after later reader edit, and U+2028 above the pin row — all behaved correctly.
- **F3 (`4f4d007` + `67cdd5e` paired):** ran `test_q212_the_deciding_files_field_and_mffus_exact_form`,
  `test_q212_the_reader_carries_the_go_token_rules`, `test_rq212_template_side_f3_f9_n2_n3`, `test_e259_*`, and
  `test_c5_*` from `4f4d007` directly against `67cdd5e:extended/reader.py` — all passed.
- **F4 (`4f4d007` `_cw_problems`):** verified voided later confirmation window clears (`[]`), U+2028 above window does
  not shift lines or raise, and real `DECISIONS.md` returns `[]`. (Verified voiding a bad *first* confirmation window
  is refused by both `reader.py` and `_cw_problems` consistently.)
- **F7 (`67cdd5e` `go_row_present`):** verified `--no-replace-objects` is passed on every git call in `go_row_present`
  and its helpers (`_blob`, `_git_bytes`, `_gitnr`), and dirty working-tree `DECISIONS.md` is rejected even when
  `log_text=None` (`test_c2_f7_go_row_present_ignores_replace_refs_and_dirty_decisions` passes).
- **F10 (`67cdd5e` `_HIDDEN_BREAKS`):** verified normal CRLF and EOF bare `\r` are clean while mid-line bare `\r` and
  doubled `\r\r\n` are flagged as `U+000D` and voidable.
- **Golden suite & targeted pytest:** all 132 golden cases at `67cdd5e` passed (0 failures); `wt-verify` targeted
  tests (`test_reader_q212b.py`, `test_reader_go.py`, `test_reader_superseded.py`) passed (196 passed); `wt-lit`
  targeted tests (`test_declarations_fixed.py`, `test_design_search_template.py`) passed (69 passed, 2 skipped only due
  to `wt-lit`'s pre-Q-212 reader).

## What I could not check

- **Full pytest suite and actual merged worktree checkout:** omitted per narrow diff-check scope and memory constraints;
  cross-branch verification was performed via in-memory module loading of `67cdd5e:extended/reader.py` into `4f4d007`
  tests and read-only `git merge-tree`.
