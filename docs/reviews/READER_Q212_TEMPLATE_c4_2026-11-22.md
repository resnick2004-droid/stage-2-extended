# Red team diff check: Reader Q-212 round 4 fixes (`READER_Q212_TEMPLATE_c4`)

**Reviewer:** red team, 2026-11-22.

**Targets (read-only; repository and worktrees untouched)**
- **Reader worktree (`wt/wt-verify`):** uncommitted working-tree diff on top of `67cdd5e` in
  `extended/reader.py` and `tests/test_reader_q212b.py` (line numbers below refer to the current
  working-tree copies in `wt-verify`).
- **Reference baseline:** `docs/reviews/READER_Q212_TEMPLATE_c3_2026-11-22.md` (c3 #1 MATERIAL / c2 F2;
  c3 #3 MINOR / c2 F6; c3 #4 MINOR / c2 F9).
- **Brief-hint note:** The round-4 brief focused item 2 on dead `sep` and `(?m)^` (omitting c3 #3's
  `_verdict_key` row-ID renumbering) and framed item 3 as rejecting shorthand `"F-99"`. Per red-team
  rules, I ignored those framing hints and independently tested `_verdict_key`, legitimate `F_ID`
  shorthands (`"RD-06"`, `"RD-01"`..`"RD-05"`), tampered pinned files, fenced fake pins, and the
  existing `tests/test_reader_superseded.py` suite.

**Method**
- Inspected the full `git diff 67cdd5e` across `extended/reader.py` and `tests/test_reader_q212b.py` plus
  surrounding helper implementations (`_verdict_key`, `_verdict_commits`, `_declaration_files`,
  `_refuse_superseded`, `pins`, `authorise`, `_go_scan`).
- Ran targeted `pytest` (`OMP_NUM_THREADS=1`, `-p no:cacheprovider`) on `wt-verify`'s
  `tests/test_reader_q212b.py`, `tests/test_reader_go.py`, and `tests/test_reader_superseded.py`
  (**191 passed, 5 failed** — all 5 failures in `test_reader_superseded.py`).
- Ran read-only Python synthetic probes (`OMP_NUM_THREADS=1`, disposable temp dirs, cleaned up; full
  pytest suite not run; no bars, no atlas, nothing from 2026-07-17 read; no declared seed literals
  quoted):
  - **Probe 1 (F2 / `_go_scan`):** clean `prereg/` + no-op void on `E-902` (1A) and on `E-903` (1B);
    `prereg/` drift via duplicate `F-13_y.md` (1C), edited `F-13_x.md` (1D), and `G14` before `M1` (1E)
    with `void(E-902)` + `void(E-903)`; mistaken `M1` on unpinned/voided/impossible-date/second go rows
    (1F); lock-in attacks via go-after-close + `M1` before voiding (1G), bogus-sha pin + go + `M1`
    before voiding (1H), and real pin + second bogus-sha pin + go + `M1` before voiding (1I).
  - **Probe 2 (F6 / `_verdict_commits`):** standalone and inline `\x00S2X_VERDICT_COMMIT:<40hex>\x00`
    diff-line spoofing with LF and CRLF (2A); in-place row-ID renumbering `E-980` -> `E-981` (2B).
  - **Probe 3 (F9 / `authorise`):** `CHARTER.md`, missing `"F-99"`, pinned shorthand `"RD-06"`,
    `"prereg/RD-06_..."`, `Path(abs_rd06)`, `str(abs_rd06)`, superseded shorthands `"RD-01"`..`"RD-05"`
    (3A); temp tree with existing unpinned `prereg/F-99_bogus.md`, repo-root `F-99_root.md`, existing
    shorthand `"F-99"` (3B); unpinned `prereg/RD-01_bogus.md` bypass (3C); tampered `prereg/RD-06_*.md`
    sha256 mismatch (3D); fenced fake `PIN` in `DECISIONS.md` (3E).

---

## Verdict: **BLOCK**

The c3 #1 (**F2**) core regression is **fixed** (both clean no-op void and `prereg/`-drift freeze
preservation pass), and c3 #3 (**F6**) dead `sep` + `(?m)^` diff-line spoof anchor are **fixed**.
However, the c3 #4 (**F9**) fix introduces a **MATERIAL** regression: it **breaks 5 existing tests in
`tests/test_reader_superseded.py`**, falsely refuses legitimate pinned `F_ID` shorthands (`"RD-06"`),
and still lets unpinned `prereg/RD-01_bogus.md`, tampered pinned files (sha256 mismatch), and fenced
fake pins bypass the superseded-purpose guard.

**Counts: 0 CHANGES-A-CONCLUSION, 1 MATERIAL, 2 MINOR, 1 NOTE.**

| # | Severity | Ref | File:line | One-line summary |
|---|---|---|---|---|
| 1 | MATERIAL | c3 #4 / c2 F9 | `extended/reader.py` l.1552-1575; `tests/test_reader_q212b.py` l.308-319 | F9 guard breaks 5 tests in `test_reader_superseded.py`, refuses pinned shorthand `"RD-06"`, and allows unpinned `prereg/RD-01_bogus.md`, sha256-tampered pinned files, and fenced fake pins; new test never creates unpinned files |
| 2 | MINOR | c3 #1 / c2 F2 | `extended/reader.py` l.2093, 2103, 2157-2168 | `_go_matches_member` omits `closed` and `pins_at` consistency checks, so a mistaken `M1` written before voiding a post-close or wrong-sha go row still locks out the log permanently |
| 3 | MINOR | c3 #3 / c2 F6 | `extended/reader.py` l.1172-1175; `tests/test_reader_q212b.py` l.268-281 | `_verdict_key` still includes `m["row"]` (missing in-place `E-980` -> `E-981` renumbering), and no regression test was added for `(?m)^` diff-line spoofing |
| n1 | NOTE | git state | `wt-verify` working tree | Round-4 edits are uncommitted (`M extended/reader.py`, `M tests/test_reader_q212b.py` on top of `67cdd5e`) |

---

## Status of c3 Reader Findings

| c3 # | c2 ref | Status in c4 | Notes |
|---|---|---|---|
| #1 (MATERIAL) | F2 | **FIXED (with MINOR edge case)** | Both clean no-op void (Probe 1A/1B) and `prereg/`-drift freeze preservation (Probe 1C/1D/1E) pass; mistaken `M1` on voided/unpinned/bad-date/second go rows passes (Probe 1F); narrower post-close / wrong-sha lock-in remains (Finding 2) |
| #3 (MINOR) | F6 | **PARTIAL (MINOR)** | Dead `sep` removed and `(?m)^` anchor blocks diff-line spoofing (Probe 2A); `_verdict_key` row-ID renumbering still unaddressed and untested (Finding 3) |
| #4 (MINOR) | F9 | **BLOCKED (MATERIAL regression)** | Unpinned `prereg/F-99_bogus.md`, root `F-99_root.md`, and `CHARTER.md` now refused, and absolute `Path` to `RD-06` accepted; but 5 tests in `test_reader_superseded.py` fail, pinned `"RD-06"` shorthand is refused, and 3 bypasses remain (Finding 1) |

---

## Findings

### 1 (MATERIAL). F9 fix breaks 5 existing `test_reader_superseded.py` tests, refuses pinned `F_ID` shorthands (`"RD-06"`), and leaves 3 bypasses in `authorise`

**Where.** `extended/reader.py` l.1552-1575 (`authorise`); `tests/test_reader_q212b.py` l.308-319
(`test_c2_f9_superseded_purpose_rejects_non_prereg_file`).

```python
# extended/reader.py l.1552-1575
        if (purpose is not None and purpose not in (IDENTITY, REGISTERED_DESIGN) and SUPERSEDED
                and purpose in _superseded_purposes(tree)):    # Q-212, F7 / c2 F9
            ok_decl = False
            if declaration is not None and not E_ID.fullmatch(str(declaration)):
                dp = Path(declaration)
                if not dp.is_absolute():
                    dp = tree / dp
                ...
                if (dp_res is not None and dp_res.parent == prereg_res
                        and re.fullmatch(r"(?:F|RD)-\d+_[^/\\]+\.md", dp_res.name)):
                    rel_decl = f"prereg/{dp_res.name}"
                    pinned_rels = {rel for rel, _ in PIN.findall(_decisions(tree))}
                    ok_decl = (rel_decl in pinned_rels) or (
                        any(re.fullmatch(r"RD-0[1-5]_.*\.md", dp_res.name) for _ in (0,))
                    )
            if not ok_decl:
                raise SupersededRefused(what, f"{purpose!r} is a purpose a superseded declaration names, ...")
        _refuse_superseded(declaration, tree, what, purpose)
```

**Evidence.**
1. **5 existing tests FAIL in `tests/test_reader_superseded.py`:**
   Running `pytest -p no:cacheprovider -q tests/test_reader_superseded.py` fails on:
   - `test_a_read_authorised_by_each_superseded_file_is_refused[2020-01-02-2023-12-29-prereg/RD-01_firm_contracts.md]`
   - `test_a_read_authorised_by_each_superseded_file_is_refused[2020-01-02-2023-12-29-prereg/RD-02_payout_policy.md]`
   - `test_a_read_authorised_by_each_superseded_file_is_refused[2020-01-02-2023-12-29-prereg/RD-03_contract_levers.md]`
   - `test_a_read_authorised_by_each_superseded_file_is_refused[2020-01-02-2023-12-29-prereg/RD-04_volatility_drift.md]`
   - `test_rd05_is_superseded_for_its_part_f_alone[2020-01-02-2023-12-29]`
   Because `authorise` does `Path(declaration)` instead of `_declaration_files(declaration, tree)` AND
   runs `if not ok_decl:` **before** `_refuse_superseded`, passing `"RD-01"`..`"RD-05"` (or an unpinned
   copy `"prereg/RD-81_copy.md"` of `RD-05`'s bytes) raises the generic `"names its own pinned
   declaration"` refusal instead of `_refuse_superseded`'s message naming the superseded parent (which
   `test_reader_superseded.py` l.66 and l.100 assert).
2. **Legitimate pinned shorthand `"RD-06"` falsely refused (Probe 3A):**
   `R.authorise("2020-01-02", "2023-12-29", purpose="firm_scorecard", declaration="RD-06", repo=WT)`
   raises `SupersededRefused`, even though `_exists` (l.1526) and `_declaration_files` (l.1389) accept
   `F_ID` shorthands and `prereg/RD-06_firm_contracts_search_years.md` is pinned and not superseded.
3. **Hardcoded `RD-0[1-5]_.*\.md` bypass allows unpinned spoof files (Probe 3C):**
   Line 1568-1570 exempts any filename matching `RD-0[1-5]_.*\.md` from `pinned_rels`. In a temp tree
   containing an unpinned `prereg/RD-01_bogus.md` (not in `DECISIONS.md` pins, not matching
   `SUPERSEDED` path or bytes), `authorise(..., purpose="firm_scorecard",
   declaration="prereg/RD-01_bogus.md")` returns **`ALLOWED`**.
4. **SHA-256 not verified and fenced `PIN` lines trusted (Probes 3D, 3E):**
   Line 1567 uses `{rel for rel, _ in PIN.findall(_decisions(tree))}`, discarding the sha256 and
   ignoring code fences (unlike the existing `pins(text)` helper at l.499).
   - **Probe 3D:** Appending `# TAMPERED` to `prereg/RD-06_firm_contracts_search_years.md` (breaking its
     pin sha256) still returns **`ALLOWED`**.
   - **Probe 3E:** Appending a fenced fake pin (` ```\n| E-999 | ... | `prereg/F-99_bogus.md` sha256
     `0000...` |\n``` `) to `DECISIONS.md` causes unpinned `prereg/F-99_bogus.md` to return
     **`ALLOWED`**.
5. **Vacuous regression test (`tests/test_reader_q212b.py` l.308-319):**
   `test_c2_f9_superseded_purpose_rejects_non_prereg_file(tmp_path)` accepts `tmp_path` without using
   it. Its `"F-99"` assertion runs against `ROOT` with `pytest.raises((R.SupersededRefused,
   R.ReadRefused))`, where `F-99` does not exist and fails at `_exists` (`ReadRefused`) before reaching
   the superseded-purpose guard at all; it never tests an existing unpinned `prereg/F-99_bogus.md`,
   repo-root `F-99_root.md`, `Path` object, tampered sha256, or pinned `"RD-06"` shorthand.

**Remedy.**
In `authorise` (l.1552-1575), handle the ordering cleanly without the `RD-0[1-5]` hack:
1. When `purpose in _superseded_purposes(tree)` and (`declaration is None` or
   `E_ID.fullmatch(str(declaration))`), raise `SupersededRefused` with `"never none or a decision row"`
   first (preserving `test_a_decision_row_resolves_to_its_pin` l.111).
2. Next, call `_refuse_superseded(declaration, tree, what, purpose)` (so `"RD-01"`..`"RD-05"`,
   edited `RD-01`..`RD-05`, and unpinned byte-copies like `"prereg/RD-81_copy.md"` are refused with
   their parent-naming message, passing all 5 tests in `test_reader_superseded.py`).
3. Then, for `purpose in _superseded_purposes(tree)`, resolve `files = _declaration_files(declaration,
   tree)` and require:
   - `len(files) == 1`,
   - `dp_res = files[0].resolve()` has `dp_res.parent == (tree / "prereg").resolve()` and
     `re.fullmatch(r"(?:F|RD)-\d+_[^/\\]+\.md", dp_res.name)`, and
   - `sha256_lf(dp_res) in pins(_decisions(tree)).get(f"prereg/{dp_res.name}", ())` (using `pins()` so
     fenced blocks are ignored and the file bytes match its pin).
4. Update `test_c2_f9_superseded_purpose_rejects_non_prereg_file(tmp_path)` to build a temp tree and
   assert `SupersededRefused` on existing `prereg/F-99_bogus.md`, root `F-99_root.md`, shorthand `"F-99"`
   (when `F-99_bogus.md` exists), `prereg/RD-01_bogus.md`, tampered `prereg/RD-06_*.md`, and fenced
   fake pin, while accepting `"RD-06"`, `"prereg/RD-06_..."`, and `Path(abs_rd06)`.

---

### 2 (MINOR). `_go_matches_member` still allows permanent lock-in if a mistaken `M1` is written before voiding a post-close or wrong-sha go row

**Where.** `extended/reader.py` l.2093, 2103, 2157-2168 (`_go_scan`).

```python
# extended/reader.py l.2164-2167
if j in tok_pos:
    return True
return (not voided_before(g["row"], j, i)
        and log_pins.get((g["decl"], g["sha"]), i) < j)
```

**Evidence (Probes 1G, 1H, 1I).**
- **Probe 1G (go row after closing row + mistaken `M1` before voiding):** On clean `prereg/` with
  `[P13, C13(E-901, withdrawn), G13(E-902), M1(E-903 -> E-902), void(E-905 -> E-902), void(E-906 ->
  E-903), P14, G14(E-904)]`, `E-902` was invalid (after closing row `E-901`) and both `E-902` and
  `E-903` were voided. Because `_go_matches_member` does not check `closed.get(g["decl"], len(lines))
  >= j`, `M1` becomes `frozen` and locks out the log permanently:
  `go_problems == ['E-903 (line 4): the membership event recorded here (E-902, F-13) is not the first
  counted go row computed now (E-904, F-14)']`, `membership_event` raises `GoRefused`.
- **Probes 1H, 1I (bogus/wrong-sha pin row + mistaken go + `M1` before voiding):** Because
  `log_pins.setdefault((decl, sha), i)` at l.2103 records every `PIN` regex match even when `decl` has a
  different counted pin in `pins_at` (Probe 1I) or the pin sha never matched `prereg/` (Probe 1H),
  writing `[P13_bogus(000..), G_bogus(E-900), M1(E-901 -> E-900), void(E-900), void(E-901), P13, G13]`
  similarly locks out `G13` permanently (`GoRefused`).

**Remedy.**
In `_go_matches_member` (l.2166-2167), also require `closed.get(g["decl"], len(lines)) >= j` and, when
`g["decl"] in pins_at`, require `pins_at[g["decl"]][0] < j and pins_at[g["decl"]][2] == g["sha"]`
(falling back to `log_pins` only when `g["decl"] not in pins_at`, i.e., under `prereg/` drift).

---

### 3 (MINOR). `_verdict_key` still includes `m["row"]` (missing row-ID renumbering) and `(?m)^` spoof fix has no regression test

**Where.** `extended/reader.py` l.1172-1175 (`_verdict_key`); `tests/test_reader_q212b.py` l.268-281.

**Evidence (Probe 2B).**
- Dead `sep` was removed and `(?m)^` at l.1217 fixes diff-line spoofing (Probe 2A passed).
- However, `_verdict_key` at l.1175 still returns `(m["row"], m["market"], m["decl"], m["sha"])`. In
  Probe 2B, commit `c1` adds verdict `E-980` and commit `c2` renumbers it in place to `E-981` (same
  market, decl, sha): `_verdict_commits(t, v981)` returns `[c2]` only, missing `c1`.
- `tests/test_reader_q212b.py` has no regression test for either the `(?m)^` diff-line spoof fix or
  row-ID renumbering.

**Remedy.**
Either drop `m["row"]` from `_verdict_key` (keying on `(m["market"], m["decl"], m["sha"])`) and test
row-ID renumbering, or explicitly record keeping `m["row"]` as a design ruling (if distinct voided vs
replacement verdict rows for the same `(market, decl, sha)` must not collide); in either case, add a
regression test for `(?m)^` diff-line spoofing to `tests/test_reader_q212b.py`.

---

## Notes

- **n1 (Uncommitted working tree).** The round-4 edits in `wt-verify` are currently uncommitted
  (`M extended/reader.py`, `M tests/test_reader_q212b.py` on top of `67cdd5e`).

---

## What I tried that found nothing

- **F2 core scenarios (Probes 1A-1F):**
  - Clean `prereg/` + no-op `void(E-905 -> E-902)` after `M1` (1A) and no-op `void(E-905 -> E-903)`
    (1B): both return `go_problems == []` and `membership_event == G13`.
  - `prereg/` drift via duplicate `F-13_y.md` (1C), edited `F-13_x.md` (1D), and `G14` before `M1` (1E)
    with `void(E-905 -> E-902)` + `void(E-906 -> E-903)`: all flag `E-903` in `go_problems` and raise
    `GoRefused` from `membership_event` (never shifting to `E-904`).
  - Mistaken `M1` on voided-before-`M1`, unpinned, impossible-date, and second go rows (1F and all 8
    sub-cases of `test_c2_f2_mistaken_membership_row_never_hijacks_or_locks_out`): all passed cleanly.
- **F6 dead `sep` and `(?m)^` diff-line spoofing (Probe 2A):** Standalone and inline
  `\x00S2X_VERDICT_COMMIT:<40hex>\x00` lines (LF and CRLF) in `DECISIONS.md` history did not spoof
  `_verdict_commits` (`hits == [c1]`).
- **F9 subset that does work (Probes 3A, 3B):** `CHARTER.md`, existing unpinned `prereg/F-99_bogus.md`,
  repo-root `F-99_root.md`, and existing unpinned shorthand `"F-99"` all raise `SupersededRefused`;
  `"prereg/RD-06_firm_contracts_search_years.md"`, `Path(abs_rd06)`, and `str(abs_rd06)` are all
  accepted.
- **Targeted reader tests (`test_reader_q212b.py`, `test_reader_go.py`):** All tests in both files
  (including all 132 golden cases) passed (191 passed across the 3 targeted files; all 5 failures were
  in `test_reader_superseded.py`).

## What I could not check

- **Full pytest suite and cross-branch merge with `wt-lit`:** omitted per narrow round-4 diff-check
  scope and memory constraints.
