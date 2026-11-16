# Red team: reading PP's third draft (`prereg/DRAFT_F-P_payout_policy.md`), Q-102, 2026-11-16

**Target.** `prereg/DRAFT_F-P_payout_policy.md` at 349fc2b on `wt/wt-payout`, LF sha256
`3bfbbf5c45476ad23afc4d2b0282969eaa81fc91d1875f9e6f936c6750084324` (re-hashed here, from the blob and from the working
file: both match). Merged to master since, unchanged, under E-070. Its test `tests/test_pp_draft.py` at the same commit.

**Read.** The draft in full; its test; DECISIONS E-018, E-023 to E-026, E-028, E-034, E-041, E-044, E-046, E-049 to
E-051, E-053, E-055, E-058, E-059 and E-064 to E-070 (main tree, read-only); the first review of this reading
(`docs/reviews/DRAFT_F-P_payout_policy_2026-11-16.md`, F1); the firms reading's review
(`wt-firms/docs/reviews/DRAFT_RD_firms_2026-11-16.md`, M5, m1, m4, Appendix A1); `extended/reader.py`,
`extended/gate.py`, `extended/user_beside.py` (Q-76 at f92ac5e, and master's with Q-94), `extended/user_readings.py`;
the vendored `lockstep.py` (525-860, 1380-1425, 1490-1510, 1816-1866), `risk_policy.account_state`, `u_select.block`,
`protocols.py`, `config/rules.yaml`, `config/rules_extended.yaml` (`payout_request_amount_choice`); the two pinned
calendars' hashes; the registered no-closure table's leaves (`results/state_policy_v12_noclose_policies.json`, a
configuration, not an outcome). No bar, no walk, no result file of any design or cell, no engine run.

**The brief** listed the drafter's interpretations to test and named no expected answer; none was assumed.

**Seeds in this note.** This reading's test (and the firms reading's) fails if a seed it holds "in use" or "reserved"
appears in `docs/reviews/`. This note therefore names section 11's live seeds by their role (the build's toy seed, the
honesty seed, the reserved seed), never by number. Its own synthetic checks use seed 515153 (fixed before the first
run; found nowhere in the repository).

---

## Verdict: must be redrafted (a small redraft)

One MATERIAL defect, in a declared rule: the coverage label (9.2 item 7), the draft's adoption of the firms review's
M5 remedy 3. As declared, it labels every interval the reading can print, at every window count, so it carries no
information. Seven MINOR findings and ten NOTES follow. Each is a text change; none needs a run. No look-ahead, no
cross-block leakage, no unverified rule, no carry or level language, and no choice made after a look were found.

**Pinnable once:**

1. 9.2 item 7, 7.1's label row and 0.1's first row are redrafted as M1's remedy says;
2. the minors are answered in the text;
3. the lead has checked the diff against 349fc2b. If the diff stays inside those hunks, no full re-read is needed.

The run's waits are unchanged (Q-93, Q-80, Q-44's file), plus Q-101 if m3 is answered through Q-94's recorder.

---

## Findings

### M1 (MATERIAL). The coverage label fires on every interval the reading prints, whatever its window count

**Where.**

- 9.2 item 7, the last bullet (lines 712-714): "the lowest coverage over the shapes at its (h, n_w) ... Where that is
  below **0.88**, the interval is labelled 'under-covers at this window count'";
- 7.1, the row "the coverage label" (line 455);
- 0.1, the first row (line 56).

**Evidence.**

- The settings come from dates alone (Appendix B; an exchange calendar, so approximate by a few starts). The reading
  prints an interval only at five (h, n_w):
  - P and months 1-3 (h = 63): all starts, 13 kept windows; early block 7; late block 5;
  - month 6 (h = 126): all starts, 6;
  - month 9 (h = 189): all starts, 4.
- Appendix A1 rebuilt the declared shapes exactly as `tests/test_pp_draft.py` codes them (`lumpy_sessions`,
  `persistent_sessions`, `start_series`, the separated windows). It then measured the 90 % interval's coverage at
  those five settings, 2,000 series each:

| (h, n_w) | gauss | ahead | paired | lumpy (9 shapes) | persistent (9 shapes) | lowest of all 21 | no rare session seen, p = 0.05 |
|---|---|---|---|---|---|---|---|
| (63, 13) | 0.894 | 0.895 | 0.900 | 0.618-0.867 | 0.534-0.829 | 0.534 | 26-28 % |
| (63, 7) | 0.898 | 0.904 | 0.909 | 0.461-0.830 | 0.399-0.783 | 0.399 | 47-52 % |
| (63, 5) | 0.893 | 0.886 | 0.912 | 0.371-0.825 | 0.325-0.764 | 0.325 | 57-62 % |
| (126, 6) | 0.914 | 0.893 | 0.909 | 0.410-0.853 | 0.380-0.776 | 0.380 | 51-55 % |
| (189, 4) | 0.907 | 0.868 | 0.935 | 0.323-0.818 | 0.314-0.786 | 0.314 | 63-68 % |

- **All 18 lumpy and persistent shapes are below 0.88 at every setting.** The best of them is 0.867. So the lowest over
  the 21 shapes is always below 0.88, and the label is a constant.
- **The cause is not the window count.** With p = 0.05 the declared shape puts one rare session in about 1,260. Between
  a quarter and two thirds of those series show no rare session in any kept window. Their windows' means then sit near
  +g, and the interval misses above (0.35 to 0.69 of series; below, under 0.02).
- These shapes were the first review's adversarial nulls for a one-sided t at 0.05/132 (its F1 table). They were built
  to show that a test can carry falsely. They were never a calibration for a description's interval.

**The failure it allows.**

- **Input:** any paired series the menu prints an interval for. Take the all-starts P difference at n_w = 13, where
  the three shapes built like the reading's own series cover 0.89 to 0.90.
- **Output:** "under-covers at this window count", exactly as on the late block's five windows and on month 9's four.
- So the operator cannot tell a near-nominal interval from one that is not. The label also names the wrong cause.
- And which intervals to trust is left to whoever reads the menu after the results are in. That is the after-the-look
  choice a declared label exists to prevent.

**Remedy (a declared rule; the synthetic table can be computed before the pin).**

1. Label on the three shapes whose dependence matches the reading's construction. An interval is labelled "under-covers
   at this window count" where the lowest of gauss, ahead and paired at its (h, n_w) is below 0.88. On Appendix A1's
   draws that fires only at month 9's four windows (ahead 0.868).
2. Print beside every interval, without a threshold, the lowest coverage over the lumpy and persistent shapes and that
   shape's misses above and below, as one line: "if the difference is rare and lumpy". This line is where the skew
   shows, and the draft already prints the misses.
3. Optional, and descriptive only: print beside each series a fixed descriptor of its own lumpiness, so the reader
   can see which line applies. For example, the share of starts with a nonzero difference, and the largest kept
   window's share of the kept windows' total absolute mean.
4. T-6 gains one assertion at a small fixed setting: the label's rule is not constant (it is off for gauss at a large
   n_w, and on for a shape below 0.88).
5. 0.1's row restates the label accordingly.

Re-specifying p instead (so that a kept window expects at least one rare session) would also make the label move. It
would change the shapes themselves, though, and the first remedy keeps them as they are.

### MINOR

**m1. The identity door can read a policy cell, unledgered and repeatably.**

- **Where:** 8.1 (lines 514-519), 14 step 1 (lines 869-871), 15 item 3 (lines 904-905).
- **Evidence:**
  - The reader's `identity` purpose is allowed in any tree, as often as it runs, and is ledgered only inside a clean
    run (`extended/reader.py` lines 30-35, 543-548). It needs only an `identity/*.py` script and a row that mentions an
    identity (377-391).
  - `identity/pp_identity.py` runs this reading's whole adapter (the class, the held-state rule and the payout
    fields) on the whole window.
  - Nothing in the draft confines it to `ref`.
- **The failure it allows:** a policy argument or a debugging edit to the script reads `lock` or `half` on the whole
  window under `identity` before the declared run. That read is unledgered in a worktree and not limited to once.
  The menu's outcomes would then be read outside the seal, and the declared run would no longer be the first read.
- **Remedy:**
  - State that `pp_identity.py` runs the reference policy only. Its payout fields and lever flags are constants in the
    script, no argument selects a policy, and the script asserts the levers are off before its first start or path.
  - Add a fast test that holds this, and list it among the build's tests.

**m2. Measures with no declared horizon, so the early block's purge is undefined for them; T-3 omits h = 189.**

- **Where:** 5 item 3 (lines 303-310), 9.1 item 2 (lines 589-595), 9.1 item 10's "by start year" (line 649), and T-3
  (line 841).
- **Evidence:**
  - The draft gives h only for P and months 1 to 12.
  - Q-17's readings, which the menu's measures come from, read the journey variables on their own windows: 126 for the
    first pass and the first payout; 252 for break-even and for "later falls back"; twelve months for evenness
    (`extended/user_readings.py` lines 18-25).
  - Q-17 has no early block; this draft adds one "per measure".
  - T-3 checks h = 63, 126 and 252, but month 9 reads at 189.
- **The failure it allows:**
  - If the build reads "sessions to the first payout" on the early block purged at 63, starts from October to
    December 2023 read sessions of 2024.
  - The stability flag then compares an early reading that reached into the late block with the late block.
  - T-3 cannot catch it, because no horizon is declared to test.
- **Remedy:**
  - Add a table giving each measure of 9.1 items 1 and 2 its h: Q-17's windows, and each S measure's horizon from
    `USER_MILESTONES.md`.
  - Run T-3 over every h in that table, 189 included.
  - The by-year readings state their purge, or say "means only, not purged".

**m3. Where 8.1 item 4's and 8.3's counts come from is not declared, and part of it contradicts 13.1.**

- **Where:** 8.1 item 4 (lines 533-536), 13.1 item 3 (lines 815-818, "none of Q-71's seams and no recorder"), 8.3
  (lines 568-570).
- **Evidence:**
  - Item 4 compares "the recorder's `eligible` column" with the vendored engine's on the starts and on the gate's
    paths.
  - The U1 replay through `run_starts` turns on no day recorder (`customer_slices.engine_args` passes none). The only
    declared way to turn it on is Q-94's `recorder` keyword (E-068, merged after this draft), whose heavy identity
    (Q-101) is owed.
  - The gate is declared without a recorder.
  - 8.3's "the engine's own count of trades sized at the allowance" is `FundedAccount.at_max`, a per-account total.
    It cannot be split by day or by 13:00 CT without the trade ledger.
- **The failure it allows:** the build either turns a recorder on that no identity covers, or meets item 4 with a
  comparison that cannot fail. Both are possible: the class restores `last_eligible` from the same vendored method it
  is then compared against.
- **Remedy:** name each count's source.
  - The class's own counters (held fires, held first requests, closes where the policy's eligibility differs from
    the firm's) need no recorder, on the replay and the gate alike.
  - For the minutes-release count, use the trade ledger through Q-94's recorder, with Q-101 added to 14's waits. Or
    reduce the count to offered trades only.

**m4. What a failed check leaves behind.**

- **Where:** 8.1's last paragraph (lines 544-546) and 14 step 2 (lines 872-874).
- **Evidence:** items 4 to 6 are checked "on its own replays" inside the reading's run. The draft does not say that
  `ref` is replayed and checked before any new cell, nor that a failure writes nothing.
- **The failure it allows:**
  - Item 6, the ladder at `ref` under `payout_ladder_beside`, fails after the headline cells have been replayed.
  - Their rows exist while the adapter is diagnosed.
  - The fix that the `repeat=` run then uses can be informed by them.
- **Remedy:**
  - Order step 2 as follows: `ref` at `off`, then `ref`'s ladder and placement; then items 4 and 6; only then the new
    cells, each checked under item 5 before any reading of it.
  - On any failure, nothing of a new cell is computed, written or printed (the rule Q-17's runner keeps: "Any failure:
    nothing written").

**m5. Many marginal 90 % intervals, with no count beside them.**

- **Where:** 9.1 items 4 and 10; 9.2 items 2 and 5.
- **Evidence:**
  - The menu prints a marginal interval for each measure, month, cell or comparison, block and arm: some hundreds.
  - With no effect anywhere, about one in ten excludes zero.
  - The MDD is worded as a detection ("wholly on one side of zero").
- **The failure it allows:** the operator, choosing from the menu, reads chance exclusions as findings.
- **Remedy:** print with the menu three things: the number of intervals printed; that each is marginal, not
  simultaneous; and the count expected to exclude zero by chance alone (a tenth of them). This is a count, not a level
  and not a correction. The firms review's m1 offered such a count as its alternative.

**m6. `lock` under the placement is a narrower policy than 6.1 declares, and it is stated as if by definition.**

- **Where:** 9.1 item 7 (lines 624-630; "L1 and the held-state rule do not -- both are defined on the Standard path's
  eligibility").
- **Evidence:**
  - 6.1 defines `lock` by the loss limit's lock, not by the path.
  - The floor hardens at $0 on any payout, on either path (`lockstep.py` line 832). So the stranded-cushion mechanism
    behind `lock` applies to Consistency accounts too.
  - The adapter cannot hold a Consistency request, because that path's eligibility is computed inline in `trade_day`
    (lines 800-806), with no seam at the close. That is the engine's constraint, not the lever's definition.
- **The failure it allows:** the `rtp` rows of `lock` and `lock_half` read "`lock` for accounts activated before the
  placement". A reader takes them for "`lock` under the placement".
- **Remedy:**
  - State it as the engine's constraint.
  - Label those rows "L1 on Standard-path accounts only".
  - Count per cell the Consistency accounts' first payouts taken with the floor below $0, which are the ones `lock`
    would have held.

**m7. Stale citations.**

- **Where:** 0.1 (the Q-76 row, line 63), 8.1 (lines 511-512), 13.1 item 1 (line 796, "its merge pending at this
  draft"), 14 (line 863, "Q-76's commit").
- **Evidence:**
  - Q-76 merged under E-059. Its (2) is the lead's ruling that 7.2 follows (E-070 (5) cites it so); the draft never
    cites E-059.
  - The owed U1 identity with a class is Q-93 (E-059 (1); E-066's queue). The draft says "owed (heavy)" with no id.
  - Master's adapter now also carries Q-94's `recorder` keyword (E-068). With the keyword absent, it equals Q-76's
    adapter bit for bit.
- **Remedy:**
  - Cite E-059 (1) and (2).
  - Name Q-93 in 8.1 and in 14's waits.
  - Record in the manifest the adapter commit actually run, not "Q-76's commit".

### NOTE

**n1. Where an interval exists at all, from dates.**

- Appendix B's counts: at month 12 even all starts keep 3 windows, so no block prints an interval there. At months 6
  and 9, only all starts do (6 and 4).
- So 5 item 4's "may hold fewer than four" is certain.
- 2's N4 expects any gain at months 6 to 12. That is where the separated rule leaves least: v2's adjacent rule had 5
  windows at month 12 on all starts.
- Print the table in 5 item 4 now. E-064 asked the firms reading to state each change's effect on what it can show.

**n2. The drafter's interpretation "every cell runs the class" holds, but its reason is weaker than stated.**

- The held-state rule can be computed from `risk_policy.account_state`'s inputs (`win_days`, `line_gap`, the phase,
  the balance and the cushion; lines 331-353).
- So `ref` and `half` could run on the vendored `FundedAccount` with a risk-policy held rule, and keep the ten Focused
  Trader models. Only `lock` and `lock_half` need the class.
- The "two code paths" objection (7.2) is what 8.1's reference identity answers.
- The cost of the choice: no Focused Trader reading for `half`. That is the lever that keeps accounts alive, and the
  models count accounts lost.
- E-070 (5) accepted the choice. The menu's gap line should name `half` explicitly.

**n3. The ladder inheriting Q-17's start seeds holds.**

- Each start's path seed is `child_seed(Q-17's base, 0, start index)`: the same for every response, cell, arm and the
  exact runs (`extended/user_beside.py` at f92ac5e lines 35-41, 150-154; master 164).
- One uniform is drawn per exposed payout, in order. Exact runs are made on every start for `off` and on every 21st
  otherwise (f92ac5e 98-102, 533; master 116, 564).
- Q-44 runs every start (`scripts/user_beside.py` line 127). So 8.1 item 6 is a real check, start for start.

**n4. The identity script's name and row hold with the reader** (an `identity/*.py` script and a row that mentions an
identity; `reader.py` lines 377-391). m1 concerns its scope.

**n5. The session-built shapes and the mirror's drop.**

- The re-specification is faithful to v2's per-window p: p is the expected number of rare sessions per h.
- The persistent shape probes the one-session gap between kept windows. A kept window's last start reads up to the
  second session before the next kept window's first, so one session between them is read by neither.
- Dropping the mirror is correct: |mean| <= t * se is unchanged when a series is negated.
- M1 is about the label's use of these shapes, not their construction.

**n6. The seed test scans `docs/reviews/`.**

- A review that quotes one of this reading's live seeds fails the suite. This note names them by role.
- For T-0 and T-9, consider matching the contexts where a seed is set (`default_rng(`, `seed=`) in scratch scripts,
  or exempting prose `.md`, so that a review can quote what it checks.
- This is not a defect of the declaration.

**n7. The gate rows' arm.** 8.1 item 1 holds the class at the 0 % arm only. 9.1 item 8 should say that its rows are
the 0 % arm with the placement off, or extend the identity to every arm the rows use (`run_gate` runs the denial levels
and the placement by default).

**n8. 8.2's martingale oracle is valid; its tolerance is not fixed.**

- The oracle holds: at zero edge, with the floor only rising and liquidation at the floor, expected withdrawals are at
  most the start's $2,000 cushion.
- Fix its Monte Carlo tolerance now (for example the mean plus three standard errors over the accounts of 500 paths),
  so that a pass is not decided at the run.

**n9. Appendix A's purpose (the lead's item 4) and its controls.**

- `registered_design` admits only P-14, P-15 and P-16 as registered, from `scripts/`, and is never limited to once
  (`reader.py` lines 36-41). D-564's buffer cells are variants of P-16, not registered designs. So that purpose fits
  badly.
- Either give Appendix A a pinned RD declaration (once-limited), or a row naming P-16 that states the two replaced
  Protocol fields, with the reader taught that case.
- Its controls hold on the table. Every five-day no-trade leaf, funded or paid, is at a balance of $500 or more (25 of
  105 funded states and 22 of 113 paid, with no request the day before). So no control account can sit.

**n10. Wording.** 6.3's "P-14's request" also governs P-16's cells. P-16's protocol has the same payout fields (D-564's
(0, 1.0) is P-16's own), so the value is the same. Write "the base's request".

---

## What I tried that found nothing

1. **Look-ahead in `lock`.**
   - The floor is updated from the close's balance (`lockstep.py` line 784) before `_standard_eligible` is called (line
     801), and the request is made after 5:00 PM CT.
   - `lock`'s test therefore uses only the close it decides at.
   - The held flag is read at the next session's start from the last close.
2. **The restored `eligible` (F7).**
   - `last_eligible` is read only by the daily recorder (`lockstep.py` line 1864). No engine logic uses it.
   - So restoring the firm's value changes no path.
3. **The Focused Trader refusal.** `funded_cls is not FundedAccount` raises (lines 1403-1408; an identity check, so a
   subclass is refused), and Q-76's `class_problems` refuses it first (master line 277).
4. **The placement.**
   - The Consistency path's eligibility is inline (lines 800-806) and never calls `_standard_eligible`.
   - `rtp_policy` is the funded policy with only the path replaced (lines 1500-1503), so `payout_frac` carries.
   - Placement accounts take the Consistency cap (lines 1820-1822), so T-5's "half of its maximum" is well defined.
5. **`half`'s seam.** `payout_frac` is a field of the vendored `Protocol` (`protocols.py` lines 79 and 123). D-564's
   runner replaces exactly that field.
6. **The reader.**
   - The line parses to three purposes, none with a choosing word.
   - The once-rule is per declaration and purpose, and `repeat=` needs a row naming the file (`reader.py` lines
     478-501).
   - `tests/test_pp_draft.py` ran here: 17 passed, under a time limit, with no cache and no bytecode written. The
     worktree's status was empty before and after.
7. **The rules.** All fifteen keys of section 4's table are in `vendor/stage2/config/rules.yaml`, status `verified`,
   at the articles cited (8284233, 8284204, 8284215).
   - The request amount stays `unstated` in `config/rules_extended.yaml` (E-034), and the draft labels it an
     assumption everywhere `half` is read.
8. **The calendars.** The LF sha256 of `config/calendar_early_closes.csv` and of `config/calendar_fomc_minutes.csv`
   match section 4's.
9. **The table's claims (6.3, T-4), re-derived from the vendored leaves (Appendix C).**
   - The four-day leaf trades at every balance of at least $250 with no request the day before, in both phases.
   - The two funded bands in the held region where the rule changes R at the same $500 risk:
     - balance $250-500, cushion $250-500: 1.5R becomes 1R;
     - balance $500-750, cushion $750-1,000: 2R becomes 1.5R.
   - A third change (to $1,500 at 3R) is at a balance of -$750. A request there is below $125, so the band is never
     held.
   - In the paid phase's held region (balance $250-500, a profit since the payout) the four-day leaf equals the
     five-day leaf ($500 at 1R).
   - The minimal rescue therefore differs from the declared rule only in those two funded bands, as T-4 says.
10. **The early purge.** `u_select.block(..., "early", h)` keeps `start_day <= last - h` (`u_select.py` line 280). A
    start reads at most to the session before 2023's last, so no early reading at horizon h touches 2024.
11. **The windows.** Kept windows share no session; adjacent ones share h - 1. On the three regular shapes, Appendix
    A1 reproduces the firms review's A1 and the draft's T-6 (0.87 to 0.94 separated).
12. **The MDD.** The formula and its about 80 % rate are held by the draft's test (noncentral t).
13. **Language.** Every "carry", "pass line", "level", "power", "confirmation" and "detectable" in the draft is a
    negation, a citation of the engine's sense, or the MDD's name. No sentence claims a result.
14. **E-058's committed text** (15 item 2) matches the brief the draft cites: windows separated by h starts, and the
    check rebuilt on overlapping series. No difference to read.
15. **The seed block.** A word-bounded search of every local and remote ref finds the block where section 11 says,
    and nowhere else. The build's toy seed is in the two identity files, as stated.
16. **Prior exposure.**
    - The third drafter's reads (section 3) are code, rules, calendars and the registered table.
    - No result file of a payout cell exists to have been opened (Q-44's files are not yet written).
    - The verdict arm's whole-window bound is disclosed (N2).

## What I could not check

- Anything on real data: P-14's and P-16's gate paths and U1 rows with this class, Q-80's and Q-93's identities, and
  the counts of 8.3. Nothing was run.
- The blocks' exact start counts. Appendix B uses an NYSE-style calendar, not U1's start dates, which sit in result
  files I did not open. The conclusions hold for any session count between 1,511 and 1,700, except that the early block
  at h = 63 could keep 8 windows rather than 7.
- Each ledger entry's read date (section 4's "read" column). Status, value and article were checked.
- Where the build will put the held-state rule (the class or a risk policy). 13.1 item 2 leaves it to the build.
- Whether `dataclasses.replace` of P-16's `Protocol` has any side effect. D-565's 500-path reproduction covered it for
  the gate, not for the U1 replay. 8.1's reference run through "the payout fields" would show a no-op replace, if the
  build passes `payout_frac` = 1.0 through it.

---

## Appendix A. The synthetic checks (scratchpad; synthetic data only; seed fixed before the first run)

### A1. The declared shapes' coverage at the reading's own settings (M1), seed 515153

Run with Python 3.12, numpy and scipy: `python pp_shapes_coverage.py 2000`. The shapes are coded as
`tests/test_pp_draft.py` codes them.

```python
"""Red-team check (Q-102), synthetic only, seed 515153 fixed before the first run."""
import sys
import numpy as np
from scipy import stats

SEED = 515153
REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
CHUNK = 500
G = 0.01
PS = (0.05, 0.10, 0.20)
SS = (0.0025, 0.005, 0.01)
SETTINGS = ((63, 13), (63, 7), (63, 5), (126, 6), (189, 4))


def per_start_means(x, h):
    c = np.zeros((x.shape[0], x.shape[1] + 1))
    np.cumsum(x, axis=1, out=c[:, 1:])
    return (c[:, h:] - c[:, :-h]) / h


def lumpy(rng, shape, h, p, s):
    q = p / h
    rare = rng.random(shape) < q
    return np.where(rare, -G * (1 - q) / q, G) + rng.normal(0.0, s * np.sqrt(h), shape), rare


def persistent(rng, shape, h, p, s):
    reps, n = shape
    r, stay = p / h, 1.0 - 1.0 / h
    pi = r / (r + 1.0 / h)
    st = np.empty(shape, bool)
    st[:, 0] = rng.random(reps) < pi
    u = rng.random(shape)
    for t in range(1, n):
        st[:, t] = np.where(st[:, t - 1], u[:, t] < stay, u[:, t] < r)
    return np.where(st, -G * (1 - pi) / pi, G) + rng.normal(0.0, s * np.sqrt(h), shape), st


def series(kind, rng, reps, n_starts, h, p=None, s=None):
    n_sess = n_starts + h - 1
    if kind == "gauss":
        return per_start_means(rng.standard_normal((reps, n_sess)), h), None
    if kind == "ahead":
        return (per_start_means(rng.standard_normal((reps, n_sess)), h) > 0).astype(float) - 0.5, None
    if kind == "paired":
        z = rng.standard_normal((reps, n_sess))
        a = per_start_means(0.8 * z + 0.6 * rng.standard_normal((reps, n_sess)), h)
        b = per_start_means(0.8 * z + 0.6 * rng.standard_normal((reps, n_sess)), h)
        return (a > 0).astype(float) - (b > 0).astype(float), None
    x, rare = (lumpy if kind == "lumpy" else persistent)(rng, (reps, n_sess), h, p, s)
    return per_start_means(x, h), rare


def cover(kind, h, n_w, case, p=None, s=None):
    rng = np.random.default_rng([SEED, case, h, n_w])
    n_starts = (2 * n_w - 1) * h
    w = [(2 * j * h, (2 * j + 1) * h) for j in range(n_w)]          # every other h-start window, from the first
    t = stats.t.ppf(0.95, n_w - 1)
    hits = above = below = norare = 0
    for k in range(0, REPS, CHUNK):
        m_ = min(CHUNK, REPS - k)
        y, rare = series(kind, rng, m_, n_starts, h, p, s)
        m = np.stack([y[:, a:b].mean(axis=1) for a, b in w], axis=1)
        mu = m.mean(axis=1)
        se = m.std(axis=1, ddof=1) / np.sqrt(n_w)
        lo, hi = mu - t * se, mu + t * se
        hits += int(np.sum((lo <= 0) & (0 <= hi)))
        above += int(np.sum(lo > 0))
        below += int(np.sum(hi < 0))
        if rare is not None:
            seen = np.zeros(rare.shape[1], bool)
            for a, b in w:
                seen[a:b + h - 1] = True                              # the sessions the kept windows read
            norare += int(np.sum(~rare[:, seen].any(axis=1)))
    return hits / REPS, above / REPS, below / REPS, (norare / REPS if kind in ("lumpy", "persistent") else float("nan"))


def main():
    shapes = [("gauss", None, None), ("ahead", None, None), ("paired", None, None)]
    shapes += [("lumpy", p, s) for p in PS for s in SS]
    shapes += [("persistent", p, s) for p in PS for s in SS]
    for h, n_w in SETTINGS:
        lows = []
        for i, (kind, p, s) in enumerate(shapes):
            c, a, b, nr = cover(kind, h, n_w, i, p, s)
            lows.append((c, kind, p, s))
            print(h, n_w, i, kind, p, s, f"{c:.3f} {a:.3f} {b:.3f} {nr:.3f}")
        c, kind, p, s = min(lows)
        print(f"  lowest: {c:.3f} ({kind} p={p} s={s}) -> label {'FIRES' if c < 0.88 else 'off'}")


if __name__ == "__main__":
    main()
```

The output, per setting: coverage, then misses above, misses below, and the share of series with no rare session in
any kept window. The nominal value is 0.90; at 2,000 series a setting the standard error is about 0.007 near 0.90 and
0.011 near 0.50.

| shape (index) | (63, 13) | (63, 7) | (63, 5) | (126, 6) | (189, 4) |
|---|---|---|---|---|---|
| gauss (0) | 0.894 | 0.898 | 0.893 | 0.914 | 0.907 |
| ahead (1) | 0.895 | 0.904 | 0.886 | 0.893 | 0.868 |
| paired (2) | 0.900 | 0.909 | 0.912 | 0.909 | 0.935 |
| lumpy p 0.05, s 0.0025 / 0.005 / 0.01 (3-5) | 0.640 / 0.618 / 0.647 | 0.467 / 0.461 / 0.509 | 0.371 / 0.387 / 0.546 | 0.410 / 0.430 / 0.532 | 0.323 / 0.337 / 0.596 |
| lumpy p 0.10 (6-8) | 0.770 / 0.782 / 0.796 | 0.655 / 0.671 / 0.718 | 0.552 / 0.568 / 0.690 | 0.602 / 0.637 / 0.700 | 0.513 / 0.520 / 0.712 |
| lumpy p 0.20 (9-11) | 0.828 / 0.866 / 0.867 | 0.801 / 0.809 / 0.830 | 0.751 / 0.751 / 0.825 | 0.768 / 0.786 / 0.853 | 0.695 / 0.703 / 0.818 |
| persistent p 0.05 (12-14) | 0.534 / 0.546 / 0.568 | 0.403 / 0.399 / 0.483 | 0.325 / 0.358 / 0.545 | 0.380 / 0.391 / 0.496 | 0.314 / 0.316 / 0.583 |
| persistent p 0.10 (15-17) | 0.684 / 0.706 / 0.724 | 0.587 / 0.584 / 0.643 | 0.519 / 0.526 / 0.657 | 0.551 / 0.578 / 0.673 | 0.471 / 0.491 / 0.685 |
| persistent p 0.20 (18-20) | 0.792 / 0.793 / 0.829 | 0.709 / 0.740 / 0.783 | 0.681 / 0.680 / 0.764 | 0.700 / 0.716 / 0.776 | 0.650 / 0.675 / 0.786 |
| lowest of the 21 | 0.534 | 0.399 | 0.325 | 0.380 | 0.314 |
| lowest of gauss, ahead, paired | 0.894 | 0.898 | 0.886 | 0.893 | 0.868 |

The misses are almost all above:

- at (63, 13), lumpy p 0.05: 0.35 to 0.38 above, 0.004 below;
- at (189, 4), persistent p 0.05: 0.41 to 0.69 above, under 0.005 below.

The share with no rare session seen at p = 0.05 is 0.26 to 0.28 at (63, 13), and 0.63 to 0.68 at (189, 4).

### A2. The draft's own test

`PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/test_pp_draft.py` in the worktree, under a
400 s limit: 17 passed. `git status` was empty before and after.

## Appendix B. Kept windows per block and horizon, from dates only (n1, M1's settings)

The script below uses an NYSE-style calendar, 2020-01-02 to 2026-07-16; U1's own start dates were not read. It gives
1,642 sessions: 1,005 to the end of 2023 and 637 from 2024. Each block's starts are taken as `u_select.block` takes
them; the windows are whole h-start windows, and every other one is kept.

```python
import pandas as pd
from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, nearest_workday, USMartinLutherKingJr, \
    USPresidentsDay, GoodFriday, USMemorialDay, USLaborDay, USThanksgivingDay
class NYSE(AbstractHolidayCalendar):
    rules = [Holiday("NY", month=1, day=1, observance=nearest_workday), USMartinLutherKingJr, USPresidentsDay, GoodFriday,
             USMemorialDay, Holiday("J19", month=6, day=19, start_date="2022-01-01", observance=nearest_workday),
             Holiday("J4", month=7, day=4, observance=nearest_workday), USLaborDay, USThanksgivingDay,
             Holiday("X", month=12, day=25, observance=nearest_workday)]
days = pd.bdate_range("2020-01-02", "2026-07-16", freq="C", holidays=NYSE().holidays("2019-12-01", "2026-12-31"))
n = len(days); n_early = int((days.year <= 2023).sum()); n_late = n - n_early
for h in (63, 126, 189, 252):
    for b, s in {"all": n - h + 1, "early": max(0, n_early - h), "late": max(0, n_late - h + 1)}.items():
        w = s // h; print(h, b, s, w, (w + 1) // 2)
```

| h (months) | all starts: starts, windows, kept | early | late |
|---|---|---|---|
| 63 (1-3) | 1,580, 25, **13** | 942, 14, **7** | 575, 9, **5** |
| 126 (6) | 1,517, 12, **6** | 879, 6, 3 | 512, 4, 2 |
| 189 (9) | 1,454, 7, **4** | 816, 4, 2 | 449, 2, 1 |
| 252 (12) | 1,391, 5, 3 | 753, 2, 1 | 386, 1, 1 |

Bold marks a setting at which an interval is printed (4 kept windows or more).

## Appendix C. The table walk (6.3, T-4, Appendix A's controls)

The leaves of `state_dp_e-0.050_lamstar_noclose` (`vendor/stage2/results/state_policy_v12_noclose_policies.json`) were
walked by phase. The funded phase is split on balance, cushion, request day and winning days; the paid phase also on
the line gap (`risk_policy.account_state`: profit since the last payout).

The comparison keeps the request-day band at 0 and pairs, for every other state, the winning-days band 4 with band 5.

- **Funded, 105 such states.**
  - The five-day leaf is no-trade in 25 of them, every one at a balance of $500 or more.
  - The four-day leaf is never no-trade at a balance of $250 or more.
  - The five-day leaf trades but the four-day differs in three states:
    - balance -$750, cushion $1,250: $500 at 1.5R becomes $1,500 at 3R (never held: the request is below $125);
    - balance $250, cushion $250: $500 at 1.5R becomes $500 at 1R;
    - balance $500, cushion $750: $500 at 2R becomes $500 at 1.5R.
- **Paid, 113 such states.**
  - The five-day leaf is no-trade in 22, every one at a balance of $500 or more with a profit since the payout.
  - The four-day leaf is never no-trade at a balance of $250 or more.
  - Its 24 differences from the five-day leaf all lie at a line gap below $0.01 (no profit since the payout: not
    eligible, so never held).
  - At balance $250 with a profit since the payout (the paid held region under `half`), both leaves are $500 at 1R.

---

## The proposed decision row (the lead numbers and commits it)

| E-NNN | 2026-11-16 | **The red team's read of reading PP's third draft (Q-102, `docs/reviews/DRAFT_F-P_payout_policy_v3_2026-11-16.md`, on 349fc2b): must be redrafted before the pin -- one MATERIAL defect and seven minors, each a text change; no run, no outcome read.** (M1) 9.2 item 7's label fires on every interval the reading can print: on the declared lumpy and persistent shapes the separated-window interval covers 0.31-0.87 at every (h, n_w) the blocks give (the lowest over the 21 shapes 0.31-0.53; at p = 0.05 a quarter to two thirds of those series show no rare session), so "under-covers at this window count" is a constant that names the wrong cause -- **the label on the three shapes built like the reading's series** (gauss, ahead, paired; it then fires only at month 9's four windows), the lumpy and persistent coverage with its misses above and below printed beside every interval without a threshold. Minors: `identity/pp_identity.py` runs the reference policy only, held by a test (the identity door is unlimited and unledgered outside a clean run); each measure's horizon declared (Q-17's 126 and 252 windows) and T-3 over every h, 189 included; the source of 8.1 item 4's and 8.3's counts named (the class's counters, or Q-94's recorder with Q-101 among the waits); `ref` replayed and checked before any new cell, nothing written on a failure; the number of marginal intervals printed with the menu; `lock` under the placement labelled "L1 on Standard-path accounts only", with the Consistency first payouts below a locked floor counted; E-059, Q-93 and the adapter's run commit cited. The drafter's interpretations: every cell on the class holds (E-070 (5); `half` could have kept the Focused Trader models through a risk-policy held rule -- the gap named for `half` on the menu); the ladder on Q-17's start seeds holds; the session-built shapes are faithful and the mirror's drop correct; the identity script's name and row hold; 6.3's and T-4's table claims and Appendix A's zero-sit controls re-derived from the vendored table, and they hold. **Before the pin:** the redraft's diff (9.2 item 7, 7.1's label row, 0.1's first row, the minors' hunks) checked by the lead against 349fc2b. | The review and its hand-back; E-023, E-025, E-051, E-058, E-059, E-064, E-068, E-070. |
