# Red team diff check: Reader Q-212 round 5 fixes (`READER_Q212_TEMPLATE_c5`)

**Reviewer:** red team, 2026-11-22.

**Targets (read-only; repository code, tests, worktrees, and git history untouched)**
- **Reader worktree (`wt/wt-verify`):** uncommitted staged+unstaged working-tree diff (`MM`) on top of
  `67cdd5e` in `extended/reader.py` and `tests/test_reader_q212b.py` (line numbers below refer to the
  current working-tree copies in `wt-verify`).
- **Reference baseline:** `docs/reviews/READER_Q212_TEMPLATE_c4_2026-11-22.md` (c4 #1 MATERIAL / F9;
  c4 #2 MINOR / `_go_matches_member`; c4 #3 MINOR / F6).
- **Brief-hint note:** Per red-team rules, I ignored the brief's implicit framing that all three items
  are cleanly resolved and independently probed edge cases (`Path` objects, fenced fake pins, duplicate
  shorthands, partial supersession `RD-05`, nonexistent `F-99` pins) and ran a mutant check against the
  new `(?m)^` regression test.

**Method**
- Inspected `git diff 67cdd5e` and surrounding helper implementations (`_verdict_key`, `_verdict_commits`,
  `pins`, `_rel`, `_declaration_files`, `_refuse_superseded`, `authorise`, `_go_scan`).
- Ran targeted `pytest` (`OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`) on
  `wt-verify`'s `tests/test_reader_q212b.py`, `tests/test_reader_superseded.py`, and
  `tests/test_reader_go.py` (**196 passed, 0 failed**).
- Ran read-only Python synthetic probes (`OMP_NUM_THREADS=1`, `python -B`, disposable `TemporaryDirectory`
  cleaned up; full pytest suite not run; no bars, no atlas, nothing from 2026-07-17 read; no declared
  seed literals quoted):
  - **Probe 1 (F9 / `authorise`):** pinned shorthand `"RD-06"`, `Path(abs_rd06)`, `str(abs_rd06)`,
    `"prereg/RD-06_..."`; superseded shorthands `"RD-01"`..`"RD-05"` and unpinned byte-copy
    `"prereg/RD-81_copy.md"`; `"CHARTER.md"`, `None`, `"E-080"` (both with `"firm_scorecard"` and
    `purpose=None`); unpinned `"prereg/RD-01_bogus.md"`, `"prereg/F-99_bogus.md"`, shorthand `"F-99"`,
    repo-root `"F-99_root.md"`; fenced fake pin matching `sha256_lf` of `F-99_bogus.md`; duplicate
    `"RD-06"` shorthand with unpinned `RD-06_extra.md`; tampered `prereg/RD-06_...` (path and shorthand).
  - **Probe 2 (MINOR #2 / `_go_matches_member`):** c4 Probes 1G (post-close go + `M1` before voiding),
    1H (bogus pin before real pin + go + `M1` before voiding), 1I (real pin + bogus pin + go + `M1`
    before voiding); go-before-real-pin + `M1` before voiding (2E); nonexistent `F-99` pin + go + `M1`
    + void both (2F); c3 core no-op void and `prereg/`-drift freeze preservation (2G).
  - **Probe 3 (MINOR #3 / F6 mutant check):** evaluated BOTH the old unanchored regex
    `r"\x00S2X_VERDICT_COMMIT:([0-9a-f]{40})\x00(?:\r?\n|$)"` and the fixed `(?m)^` regex against
    (3A) the exact payload in `test_c2_f6_verdict_commits_survives_literal_nul` and (3B) a standalone
    `\x00S2X_VERDICT_COMMIT:<40a>\x00\n` line committed in the same commit above `v1`.

---

## Verdict: **PASS WITH MINORS**

All production-code fixes in `extended/reader.py` for c4 #1 (**F9**), c4 #2 (**`_go_matches_member`**),
and c4 #3 (**F6 `(?m)^` anchor**) are verified and stand (196/196 targeted tests pass, including all 5
previously failing tests in `test_reader_superseded.py`). One **MINOR** test-quality finding remains:
the newly added `(?m)^` spoofed-separator regression test in `tests/test_reader_q212b.py` is vacuous and
does not fail if `(?m)^` is removed.

**Counts: 0 CHANGES-A-CONCLUSION, 0 MATERIAL, 1 MINOR, 3 NOTES.**

| # | Severity | Ref | File:line | One-line summary |
|---|---|---|---|---|
| 1 | MINOR | c4 #3 / c2 F6 | `tests/test_reader_q212b.py` l.268-282 | New `(?m)^` spoofed-separator regression test is vacuous (passes even if `(?m)^` is reverted) because `spoof` ends with ` \| b \|\n` instead of `\x00\n` and sits in an earlier commit than `v1` |
| n1 | NOTE | c4 #3 / c2 F6 | `extended/reader.py` l.1172-1175 | `_verdict_key` still includes `m["row"]` (in-place row-ID renumbering `E-980` -> `E-981` stays distinct); stands as a design choice if voided vs replacement verdict rows must not collide |
| n2 | NOTE | c4 #1, #2 | `tests/test_reader_q212b.py` l.254-265, 309-340 | Production code passes fenced fake pins, `Path(abs_rd06)`, and post-close / `pins_at` mismatch cases, though `test_reader_q212b.py` does not explicitly assert those specific sub-cases |
| n3 | NOTE | git state | `wt-verify` working tree | Round-5 edits remain uncommitted (`MM extended/reader.py`, `MM tests/test_reader_q212b.py` on top of `67cdd5e`) |

---

## Status of c4 Reader Findings

| c4 # | Ref | Status in c5 | Notes |
|---|---|---|---|
| #1 (MATERIAL) | F9 | **FIXED** | `_refuse_superseded` runs before the superseded-purpose pin check for non-`E_ID` declarations; `pins(_decisions(tree))`, `_declaration_files`, `_rel`, and `sha256_lf` enforce unfenced exact-hash pins. All 196 targeted tests (including all `test_reader_superseded.py`) and all Probe 1 cases pass |
| #2 (MINOR) | `_go_matches_member` | **FIXED** | `closed.get(g["decl"], len(lines)) < j` and `pin_cur[0] >= j or pin_cur[2] != g["sha"]` eliminate post-close and wrong-sha / pre-pin lock-in (Probes 2A, 2B, 2C, 2E) while preserving c3 core no-op void and `prereg/`-drift freeze (Probe 2G) |
| #3 (MINOR) | F6 | **PARTIAL (MINOR)** | Production `(?m)^` fix at `extended/reader.py` l.1217 genuinely blocks diff-line spoofing (Probe 3B), but the new test in `test_c2_f6_verdict_commits_survives_literal_nul` is vacuous against an unanchored-regex mutant (Finding 1); `_verdict_key` still includes `m["row"]` (Note n1) |

---

## Findings

### 1 (MINOR). `test_c2_f6_verdict_commits_survives_literal_nul` is vacuous for the `(?m)^` spoofed-separator fix

**Where.** `tests/test_reader_q212b.py` l.268-282 (`test_c2_f6_verdict_commits_survives_literal_nul`).

```python
# tests/test_reader_q212b.py l.271-279
    spoof = b"| E-950 | 2026-11-22 | a note with\x00nul and \x00S2X_VERDICT_COMMIT:" + b"a" * 40 + b"\x00 | b |\n"
    p.write_bytes(p.read_bytes() + spoof)
    g(t, "add", "DECISIONS.md")
    g(t, "commit", "-q", "-m", "historical nul and spoofed sep")
    v1 = VR.VERDICT_ROW
    p.write_bytes(p.read_bytes() + (v1 + "\n").encode("utf-8"))
    g(t, "add", "DECISIONS.md")
    g(t, "commit", "-q", "-m", "v1")
```

**Evidence (Probes 3A, 3B).**
The test fails to catch a regression reverting `(?m)^` in `extended/reader.py` l.1217 for two independent
reasons:
1. `spoof` puts ` | b |\n` after the trailing `\x00`, so the old unanchored regex
   `r"\x00S2X_VERDICT_COMMIT:([0-9a-f]{40})\x00(?:\r?\n|$)"` does not match `spoof` at all.
2. `spoof` is committed in an earlier commit than `v1`, so even if matched it could not split `c1`'s
   diff chunk above `+v1`.

In **Probe 3A**, running the old unanchored regex on the test's exact payload returns `[c1]` (PASS —
identical to the fixed regex). In **Probe 3B**, committing a standalone
`b"\x00S2X_VERDICT_COMMIT:" + b"a" * 40 + b"\x00\n"` line in the **same** commit immediately above `v1`
makes the old unanchored regex return `None` (FAIL), while the fixed `(?m)^` regex in `extended/reader.py`
l.1217 returns `[c1]` (PASS).

**Remedy.**
Add a standalone spoof line `b"\x00S2X_VERDICT_COMMIT:" + b"a" * 40 + b"\x00\n"` in the same commit as
`v1` immediately above `v1` inside `test_c2_f6_verdict_commits_survives_literal_nul` (keeping the earlier
historical-NUL commit as well so both behaviors remain covered).

---

## Notes

- **n1 (`_verdict_key` retains `m["row"]`).** `extended/reader.py` l.1172-1175 still returns
  `(m["row"], m["market"], m["decl"], m["sha"])`, so in-place row-ID renumbering (`E-980` -> `E-981`)
  is treated as a new verdict row rather than the same token. Per c4 #3, keeping `m["row"]` is acceptable
  as a design choice so voided and replacement verdict rows for the same `(market, decl, sha)` do not
  collide.
- **n2 (Test-coverage gaps in `tests/test_reader_q212b.py`).** Production code handles all of the
  following cleanly (verified by synthetic probes), though `tests/test_reader_q212b.py` does not
  explicitly assert them: fenced fake pins in `DECISIONS.md`, `Path` objects (`abs_rd06` rather than
  `str(abs_rd06)`), and the newly fixed post-close / `pins_at` mismatch `_go_matches_member` cases.
- **n3 (Uncommitted working tree).** `wt-verify` currently has staged+unstaged modifications
  (`MM extended/reader.py`, `MM tests/test_reader_q212b.py`) on top of `67cdd5e`.

---

## What I tried that found nothing

- **Targeted pytest (`tests/test_reader_q212b.py`, `tests/test_reader_superseded.py`,
  `tests/test_reader_go.py`):** 196 passed, 0 failed (all 5 c4 failures in `test_reader_superseded.py`
  resolved).
- **F9 (`authorise`, Probe 1):** Accepted `"RD-06"`, `Path(abs_rd06)`, `str(abs_rd06)`, and
  `"prereg/RD-06_firm_contracts_search_years.md"`. Refused `"RD-01"`..`"RD-05"` and unpinned byte-copy
  `"prereg/RD-81_copy.md"` with parent-naming `SupersededRefused` messages. Refused `"CHARTER.md"`,
  `None`, `"E-080"` (`firm_scorecard` and `purpose=None`), unpinned `"prereg/RD-01_bogus.md"`,
  `"prereg/F-99_bogus.md"`, `"F-99"`, `"F-99_root.md"`, fenced fake pins matching `sha256_lf`, duplicate
  `"RD-06"` shorthand, and tampered `RD-06` (both path and shorthand).
- **`_go_matches_member` (Probe 2):** Post-close go + `M1` before voiding (2A), bogus pin before real
  pin + go + `M1` before voiding (2B), real + bogus pin + go + `M1` before voiding (2C), and go before
  real pin + `M1` before voiding (2E) all returned `go_problems == []` and resolved `membership_event`
  to the legitimate go row. Clean no-op void and `prereg/`-drift freeze preservation (2G) both remained
  intact. (Note: Probe 2F — bogus pin for a nonexistent `F-99` + go + `M1` + void both — still triggers
  fail-closed `GoRefused`, which is an inherent consequence of `prereg/`-drift detection without git
  history because a deleted `F-13` is indistinguishable from a never-existent `F-99` given only
  `(log_text, prereg_dir)`.)
- **F6 production code (`_verdict_commits`, Probe 3B):** Standalone `\x00S2X_VERDICT_COMMIT:<40a>\x00\n`
  added in the same commit above `v1` returned `[c1]` cleanly.

## What I could not check

- **Full pytest suite and cross-branch merge with `wt-lit`:** omitted per narrow round-5 scope and
  read-only verification rules.
