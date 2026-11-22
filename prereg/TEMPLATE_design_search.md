# TEMPLATE: a design search's declaration -- copy it, never pin it

**What this file is.** The house form for a design search under the journey objective (`CHARTER.md` sections 2-3, in
force from E-210; the restart plan's Wave 2.1). It carries every field CHARTER 3.3 to 3.9 requires, E-210's two
template clauses (m-2, m-3) and R-10. It is not a declaration: it names no search, holds no seed, no k, no count, no
limit value and no figure, and its name matches neither the reader's grammar (`F-` or `RD-` and a number) nor any
test's declaration glob (`tests/test_design_search_template.py` holds that). It replaces `prereg/TEMPLATE_family.md`
for new work; that file is kept for the record.

**Text v3 (2026-11-21).** Re-declared as a new version by the lead's ruling (E-257) after text v2's two corrective
cycles were spent and its last re-read (`TEMPLATE_V2_c2_2026-11-21.md`) blocked it on H-1'; text v2 is kept in git
history (wt/wt-lit fad9461), the first text at 1a9be8c. Text v2 answered the red team's third read
(`TEMPLATE_AGENTS_v3_2026-11-20.md`), the full read (`TEMPLATE_V2_FULL_2026-11-20.md`) and the re-read
(`TEMPLATE_V2_c1_2026-11-20.md`); text v3 answers H-1', M-5 (c) and the minors by the lead's rulings, and the red team
reads it in full. When it stands, this
template is pinned by its sha256 in a decision row, and a declaration cites the template's pinned hash.

**Declaration kind: design search.** A declaration drafted on this template keeps this line. It never carries a
`Judged-block reads:` line; the held-out test's declaration, drafted on `prereg/TEMPLATE_heldout_test.md`, does
(`tests/test_design_search_template.py` scans every `prereg/*.md` for it).

**To use it:** copy it to `prereg/DRAFT_F-XX_<slug>.md` (a search is declared as a family: `F-` and a number at the
pin; a search assigns no k, F-HT's k is assigned at F-HT's held-out row, E-204), replace every `<...>` with the
search's own text, delete nothing but the template's instructions in *italics*, and send the draft to the `scout`'s
challenger brief (Q-150), the `red-team`, then the `prereg-gatekeeper`. The lead pins it by the sha256 of its LF text
(E-001 (b), E-003). **Nothing declared is edited: a change is a new declaration.** A section left as the template
wrote it is a gap the gatekeeper refuses.

*Every rule below is a floor (CHARTER 3.8; DIRECTIVE Part 1). A draft may tighten one only with the tightening's size
and power at the level the gate assumes (F-HT's, 0.05 / (k (k + 1)) with k = 13 next) shown before the pin (E-051,
E-015's condition); it may loosen none without the operator. A rule value is cited by its key in the verified record,
never typed. A result is cited by its file, never typed.*

## 0. In plain words (for the operator)

<What the search looks for, for which firm and account, over which sessions; what a user would do with a finalist's
playbook; what would count as a pass (beating each baseline on the pinned composite, inside every limit, with the
floors); and what a fail means -- "the search closes (a closing row); nothing of it is rerun; it spends no k", never
"we investigate further". Every parameter named here is explained in a phrase and classed fixed / searched / dropped
in the sections below.>

## 1. The question, the firm and the baselines

- **The market:** <MARKET, the reader's market code, here NQ> -- the one market this search reads; the
  membership event's scope is read from this field, never from the file's text (G-2; E-259). The field is written
  exactly `- **The market:** NQ -- ...` or `- **The market:** MNQ -- ...`: the allowed market codes are exactly `NQ`
  and `MNQ` (one underlying), and the firm line begins with exactly one of the allowed firm names `Topstep`, `MFFU` or
  `Lucid`, in that exact case (`- **The firm and account:** MFFU, <plan> -- ...`, never MFFU's long name), with no
  second firm named in the field; any other market code or firm name, or a field not in this exact form once, is
  refused by the gatekeeper at the pin and by the reader at the go row (the reader's `membership_event`,
  `extended/reader.py` at its pinning row's sha256; C-1; finding 4; n2). The free text after the market's ` -- ` names
  no other market code (n3).
- **The firm and account:** <`Topstep`, `MFFU` or `Lucid`, exactly; then `, ` and the plan> -- **exactly one firm**; a
  search naming several firms is refused (R-1; E-259). Its rules are the verified ones only (CHARTER 3.1): Stage 2's
  ledger (`vendor/stage2/config/rules.yaml`) or this repository's record (`config/rules_extended.yaml` through
  `extended/firm_terms.py`), each key `verified` under its decision row. **Every key the search reads is listed here**
  with its status; an unverified, `changed` or `unstated` key is refused by the loader and cannot be a lever.
- **The deciding files:** `extended/reader.py`, `<path>`
- *The line above is written exactly so (Q-212): one unfenced line, each path in backticks and repo-relative, no path
  twice, `extended/reader.py` among them, nothing after the last path.* It lists every file whose content decides an
  outcome of this search -- the survey runner, the engine adapters it calls, the reader -- and the reader's
  `go_row_present` (`extended/reader.py` at its pinning row's sha256) holds each byte-identical at HEAD and at the go
  row's runner commit and unchanged in the working tree (U-1; section 14 step 4). A draft without this line, or with
  it in another form, is refused.
- **Its own execution protocol** (E-202; never another firm's reused): <the protocol's file and row>.
- **The baselines** (CHARTER 2, 3.8 (b)): for Topstep, naive coin harvesting (its levers fixed here: <...>), and Stage
  2's P-14, P-15 and P-16; for another firm, the set it declares, at least the naive coin on its own protocol. **Each
  baseline runs under the design's convention** -- the reflection and the martingale-outcome reading under the same
  seed keying, the same fill and cost mechanics, no arm shift, the same verdict settings -- **at its registered
  latency** (P-14 at five minutes; P-16 scheduled, its latency variants dropped, E-203 B-2). **Each baseline's runner
  identity:** its trade times and brackets equal its registered ones, path for path (<the identity, its file, its
  columns, its tolerance>). **Each baseline's runner identity reads the search years only; it has no held-out part**
  (L-1; E-259). The registered rows are reported beside.
- **The measures** are `docs/MEASURES.md`'s, every one by the function that file names, each a distribution over
  start days (median, p10, p90) and over coin seeds, read on the common start set `E_h` at its horizon (MEASURES.md
  1.1). A measure the search reports that MEASURES.md does not define is defined here first, with its function, and
  sent to the red team with this draft.
- **What is new here** against every earlier search, family and RD map: <the overlap, and why this is not a re-run>.

## 2. Years, the held-out read ledger and the confirmation window

- **Development:** NQ 1-minute bars 2020-01-02 to 2026-07-16 only, read through `extended/reader.py` (the one door).
- **The search years** (E-208): 2020-01-02 to 2023-12-29. The search, its lever ranges, volatility units, regime
  thresholds, schedules, limits, budgets and weights read these years only.
- **The held-out years** (E-208): 2024-01-02 to 2026-07-16, on the pinned calendar `results/q82_judged_sessions.csv`
  (its session count and sha256 asserted by the runner). "Held out" means **unread by the search's code and unused by
  any choice in this declaration** (CHARTER 3.6 (a)). They are read by the held-out test only, once (section 14).
- **The horizon embargo** (CHARTER 3.6 (d); MEASURES.md 1.1): a start is read at horizon h only if h sessions remain
  in its own years; a held-out start reads only held-out sessions for its outcomes; causal look-backs into the search
  years are allowed. The longest horizon read here: <h, in sessions>; the strip it purges at the end of the search
  years: <...>.
- **The re-baseline (H4)** reads the search years only, its runner refusing held-out sessions (CHARTER 3.6
  (e)), so it computes no held-out output and CHARTER 3.6 (e)'s sealed case cannot arise here (n-2).
- **Single use per market** (CHARTER 3.6 (c); E-221, O-1): every model is
  built, tuned and chosen on the search years only (any number of internal time splits there). No firm's search spends
  NQ's held-out years alone: they are held until every **member search** -- the one design search of each of
Topstep, My Funded Futures and Lucid with a hash row before **the membership event, the first go-row token of an NQ
design search of Topstep, My Funded Futures or Lucid** (H-1'; E-257; E-259), at most one per firm, a second hash row
for a firm before the event refused by the gatekeeper at its pin and by the reader at the go row (n2) -- has a
finalists' row or a closing row, a firm with no hash row before the event being in state (c) of
`prereg/TEMPLATE_heldout_test.md`, fixed at that moment; and every finalist across the firms is then tested in
**one joint fixed-sequence test** at the full level of the one k it spends, the one use per market. That test is
**the held-out test's declaration**, one declaration of its own (E-238): it lists every firm's finalists (each by its
search declaration's hash and finalists' row), fixes the joint order, takes the k, and is
the one family that reads NQ's held-out window, so Q-158's rule (one family per market) holds unchanged. This search's
finalists enter it through this file's finalists' row
only if this search is a member (its hash row before the membership event): <its firm, whether it is a member, and
the held-out test's declaration when it exists>. A search pinned after the membership event, or a successor of a
closed search, is never a member of this F-HT; its candidates are tested only on data this line has never read (a
later purchase), under its own k; the confirmation window (NQ from 2026-07-17) is read once, only for this F-HT's
carried designs (CW-1; E-259). **Data this line has never read** is NQ bars after the confirmation window's end, or
another underlying's bars that no declaration of this repository has read (NQ and MNQ are one underlying); never NQ's
search years, held-out years or confirmation window (CW-2; B-2; finding 7). A successor search on another underlying
first needs a new decision row and a reader rule that extends the market allow-list; until both exist, its go row is a
refused problem (F9). A member's finalists are never voided. A later search on the same bars reads NQ's held-out years
and F-HT's results as a description only, after F-HT's verdict row (reader rule 4; n4), or moves its held-out years to
data not yet read (a purchase or the operator's setup).
- **The held-out read ledger** (CHARTER 3.6 (b)). Every past read of the held-out years for this search's comparators
  and trigger families, each in RD-04's leak-clause form, "written after this reading; no figure cited". CHARTER 3.6
  (b)'s list is the floor, and E-211 added Q-132 and Q-16's paired nulls; this declaration completes it:

  | read | what it read of 2024-2026 | for which comparator or trigger | row |
  |---|---|---|---|
  | <...> | <...> | <...> | <...> |

  While the ledger is not empty, **the level is printed nominal** beside the verdict (E-203 S-2's form). For Stage 2's
  baselines "held out" means unread by this search only (E-208), stated beside every comparison with them.
- **No held-out result is ever written where a later search can read it** -- not in the lever map, not in
  `results/variants.jsonl` (CHARTER 3.3 (f)). No guard does this yet (`VariantCounter` writes what it is given):
  **a build requirement** of this search's runner, with a test that a held-out row is refused before the survey runs.
- **The confirmation window:** NQ from 2026-07-17 to the last session in the purchase order's stated range, never read
  from bars, recorded in the first `heldout-window: NQ 2026-07-17 to <last> -- <text>` row, which states that it
  opens the confirmation window, not a second held-out test, and governs; any later NQ or MNQ window row from
  2026-07-17 on is refused by the reader (`extended/reader.py`; n1), this repository's `_cw_problems` only a
  cross-check; the purchase and that row come before the first finalists' row of any member (C-5; finding
  5), declared now, never read until a carried design is registered, and a purchase, the operator's (section 15); it
  is read once, only for F-HT's carried designs, and a non-member search's candidates never use it (CW-1; E-259).

## 3. The lever space

*CHARTER 3.3 (a), (g); 3.4. Start from the lever table and its loader; do not retype a range the loader reads.*

- **The lever table:** `docs/plans/LEVER_TABLE_topstep50k.md` (Q-151, E-211) at <its blob>, loaded by
  `extended/lever_space.py` (`bounds`, `check_design`). Every lever of the search is a row of that table or a row
  added here with the same columns.
- **Every lever classed fixed / searched / dropped, with its value or range and its source kind** (rule, arithmetic,
  declared, a search-year reading, to declare -- the table's section 1). A range comes only from contract arithmetic,
  the verified rules, or an RD map's search-year rows. A range drawn from a whole-window row is redrawn on the search
  years and entered in the held-out read ledger. A lever the loader refuses (`UnverifiedTerm`, `NotComputed`,
  `NotDeclared`) is not in the space until the row that settles it exists, cited here.

  | lever | layer (trigger / trade shape / account policy) | what it is, in a phrase | fixed / searched / dropped | value or range | unit | source kind and source |
  |---|---|---|---|---|---|---|
  | <...> | <...> | <...> | <...> | <...> | <...> | <...> |

- **Volatility units** where a setting must mean the same thing across the window's drift (RD-04): a stop as a
  multiple of a trailing range read from bars closed at or before the alert, the multiple's range read on the search
  years only (E-211's classing, E-157); dollar caps from the verified rules. The normaliser, its window and its bars:
  <...> (skill `feature-rules`).
- **The latency L is a searched lever** (CHARTER 3.3 (g), E-202 (2)(c)): its values (five minutes the reference, three
  and two counted variants) declared here before any read, every L tried counted in the variants ledger and the
  multiplicity, nothing chosen after a look; each finalist tested at its own L; **the five-minute cell** reported
  beside every finalist and read in the held-out test, reported, not tested. A latency-free component (RL3, E-204)
  collapses its latency cells to one.
- **Signal sources are a lever** (CHARTER 3.4): <which models and the coin, their shares, their account assignment>.
  A signal source is judged by what it adds to the mix. **Hard rule:** never opposing positions at once across accounts
  or firms (conduct tier 1); one position at a time across a firm (Stage 2 D-429).
- **Room cuts and the out-of-room rule (C-1).** A lever that cuts contracts to the floor's room -- S3's and S4's
  whole-micro room cut (Stage 2 D-313), A1's flip cut to `combine_mll`'s room, A17's sizing by distance to the floor
  -- can size a trade to zero contracts at a positive room. Section 5's out-of-room rule ends that account; a draft
  that searches such a lever names it here.
- **Combinations refused** (the table's section 4, `check_design`): <...>.
- **Fixed for every design** (the table's section 5: floors, not levers): restated by reference, never searched.

## 4. The component schedule across sessions, and the contract fit

*CHARTER 3.5. A design is a schedule of components; each component one session-specific trigger with its own trade
shape.*

- **Sessions in the search:** every session the firm allows (Asia, London, NY AM, NY PM, and the table's `evening`
  window), with their boundaries read from the verified `trading_hours` and declared rows (**Any hour**: no cap on
  trading hours, E-202 (2)(b); workload (30) reported, a ceiling only if the pinning row of section 7
  sets one as a limit, E-221). An overnight trigger enters only after H2 (the overnight data-integrity run) has
  passed: <its row>.
- **Each component:** its trigger (scheduled times, or resting orders at levels known in advance), its window, its
  trade shape, and its **schedule across sessions** -- components' windows scheduled not to collide (one position at a
  time across the firm). A trigger that reads bars obeys `feature-rules` in full (bars closed at or before the alert,
  normalised, a shift-invariance test).

  | component | session and window | trigger, and when it is known | entry type | trade shape | latency L | its source row |
  |---|---|---|---|---|---|---|
  | <...> | <...> | <...> | <...> | <...> | <...> | <...> |

- **Triggers judged on their properties, not their accuracy:** supply, timing, resolution speed for a given shape,
  clustering, how differently timed from other components, hand-executable. Each is judged by what it adds to the whole
  design.
- **The side rule** (part of every design; **ruled, E-221, O-4**). **The coin is the evaluation's device, not the
  playbook's** (section 5). In the playbook each design's side comes from **its own trigger**, held by **the
  no-harm floor** against the coin on the real path (CHARTER 3.5; E-221, E-230):
  its composite on the search years is not below the coin side's by more than the margin pinned in section 7
  (the no-harm margin), decided at the point estimate over `<S1>`'s seeds, paired on the same fills, as O-5 rules for
  limits (E-230) -- never by a test that fails only on evidence of harm; its held-out reading is reported beside,
  never judged. **A trigger whose side fails the
  no-harm floor offers no playbook side; that design is not carried.** The floor is read on the search years,
  before the finalists' row; a failing design is removed from the finalists' list then, so the fixed sequence's order
  is never set after a held-out read (section 10 (c)). A resting trigger traded as its real order clears the same
  floor. **Accounts alternate:** different accounts take different trades at different moments, the rotation a lever
  of the search, because copying one trade to every account correlates their failures and defeats the fee asymmetry.
  **The one hard rule** (conduct tier 1): no two of the user's accounts or firms hold opposite positions at once --
  while any position is open a new trade takes that position's side or is skipped, and the scheduler refuses a
  same-moment opposite side (R-12: a conduct rule, not a lever; its supply cost reported with (37)). In the evaluation
  the side coin's key carries no account or firm index and **the per-start keying is kept** (section 8); that means
  only the refusal above, never that every account copies every trade.
- **The output is a playbook:** each finalist written as a one-page set of rules (triggers, side rule, shapes, account
  policy, schedule) with the exact alert format, hand-executable.
- **The contract fit (CHARTER section 4), item by item:**

  | item | the search's answer |
  |---|---|
  | stops in the stop band, above the cost floor (`vendor/stage2/results/stop_band.csv`) | <...> |
  | at least L minutes from alert to order, by hand; a resting ticket live L minutes after it is published | <...> |
  | one position at a time per firm, five minutes flat between trades | <...> |
  | every trade resolving: at most 5 % reach the 15:10 CT flatten (D-212 as D-308 raised it); no time stops | <...> |
  | realised risk within 10 % on at least 90 % of trades, in its allowance-capped form (E-022 (1), E-032) | <...> |
  | no entry before 07:35:00 CT on a BLS 08:30 release day; FOMC days out | <...> |
  | no entry and no fill inside a verified news window; a position open at its start flattened (E-202 (2)(a), E-200 R-1); limits cancelled at its start; the closed 08:30-08:59 window for every source (E-223 M-8); **the one news-flatten convention** (E-223 M-4), every source: the flatten books at the adverse extreme of the window's first bar less two ticks, or at the position's resting stop instead if that extreme reaches it (as a stop exit) -- the as-walked and as-traded readings' convention; the deciding reading takes R-10's stopped walk to the window's start | <...> |
  | **conduct tier 1** (no hedging across accounts or firms, no simulator-fill exploitation, no maximum size into major news, no trade copied across accounts, nothing that conceals a pattern) | <...> |
  | conduct tier 2 modelled and off in the base case (D-289); tier 3 priced, 0 % denial in the verdict | <...> |
  | firm rules only verified (section 1) | <...> |
  | no automated or API order entry; designs for one user's own accounts | <...> |

## 5. The zero-edge convention

*CHARTER 3.2. Every design and every baseline, the same convention under the same seed keying.*

- **The fill** -- its time, price and supply -- comes from the real order.
- **Direction removed:** after the fill the path is reflected about the fill price with probability one half, by the
  coin of the declared seed (for a market entry, exactly a fair coin choosing the side; for a resting entry, the
  reflection, since a coin on the resting side does not remove direction, E-203 B-1, E-204 NB-1). RL3's same-bar pair
  is one realisable case (E-204).
- **The martingale-outcome reading decides** (every deciding reading of sections 8-10, except the no-harm and
  as-traded floors, read on the real path, N-1). Each trade's outcome is redrawn at the driftless first-exit odds of
  its own bracket, keyed by the declared seed; fills, timing, costs and resolution stay as run.
- **The race against the nearer barrier, with its exit cost** (the three-way design note 1.1 as N-5 and its third
  read's M-4 amend it; Stage 2 D-150, D-156). For each trade, in ticks, fractions allowed:
  - l is the stop, g the target -- **g is always the target as placed**, the nearer of the bracket's target and any
    profit level a rule set at placement (R-10's table; the level is converted to
    **net ticks after the target-side cost**, g' = min(g, level / (tick value x contracts) + x_target), fractional
    allowed, and the runner receives g' in these gross ticks); c is the room the engine hands the draw -- the nearer
    of the floor and, where it binds first, the daily loss limit -- read after the entry cost is booked; x_stop is the
    **stop-side exit cost** (the per-contract commission at the stop plus `stop_slippage_ticks` of
    `vendor/stage2/config/fills.yaml`'s profile in use), and x_target the target-side one (commission plus
    `target_slippage_ticks`).
  - **The loss barrier is L = min(l, c - x_stop), fractional, never rounded** (E-237): a cushion-bound loss ends
    exactly on the floor and breaches it, as the vendored engine's race does; rounding inward would leave every such
    loss a fraction of a tick above the floor, never breached and still billed. **p = L / (L + g).** A win gains g
    and pays x_target; a loss loses L and pays x_stop.
  - So a loss plus its exit cost never passes the floor and **the clip never binds** (the engine's
    `pnl = max(pnl, -cushion)`); every trade's gross expectation is exactly zero and its **net expectation is exactly
    minus its costs**, at every cushion.
  - **What happens at the fill is decided at the fill**, for every trade, by R-10's L_fill below -- the runner's rule,
    never the engine's (`BinaryDraw` books a no-room slot as a zero and counts it). A trade with L_fill > 0 is raced
    or walked, and has L >= L_fill > 0, so no taken trade has L <= 0. **There is no "not taken" state:** an account
    with L_fill <= 0 at a fill is failed there or stops its day (R-10, B-2).
  - The defect this rules out: racing the full cushion and then booking the loss with its stop-side cost lets the clip
    credit part of the cost back to near-floor trades -- a positive edge that grows with how often an account policy
    trades near the floor, a lever the search would find.
  - **`adapter.BinaryDraw` is the cost-free special case** (x = 0). Its signature, quoted from the vendored source
    (`vendor/stage2/propedge/contract/adapter.py`, read, never edited):

    ```
    class BinaryDraw:
        settlement = "race"
        def __init__(self, policy: Policy, edge: float, seed: int, rules: Rules | None = None)
        def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray) -> np.ndarray
    ```

    At `edge = 0` (drift form, `theta = 0`) with the floor in `truncate` mode, each call draws one uniform u per path
    and returns `+W` where `u < p`, else `-c'`, with `W = rr x risk`, `c' = min(risk, max(cushion, 0))` and
    `p = c' / (c' + W)`: the race against **the nearer barrier**, cost-free. The runner's race reduces to it at
    x = 0, which a test holds on the same uniforms. The runner draws its uniform from the coin field keyed per unit
    and moment (the design note's 1.5), never from BinaryDraw's one sequential stream.
  - The exact-fraction tests: zero gross and net = -(entry + exit costs) over fractional cushions and unequal exit
    costs, and no exit past the floor (the design note's `three_way_arith.race_redraw` is the reference law).
- **m-2 (E-210): trades open at once on one instrument are redrawn jointly, from one seeded driftless path.** The path
  is one **per unit and underlying** (NQ and MNQ are one underlying, the design note's N-4). Overlap is defined once,
  before any draw, on the scheduled entries and the run's exit times, never the path's. On that shared path every
  barrier is rounded inward to the path's lattice (the design note's N-4) -- the only place inward rounding applies.
  Until this declaration
  defines that joint law (the design note's 1.6, adopted in full, with H3-A's copy-against-stagger check passing before
  the pin), **no design with overlapping positions is run**: the runner refuses any design that can hold two positions
  of the user at once (several accounts, several firms, a second component entering while the first is open), and the
  survey's sampler refuses to propose one. Overlap across different underlyings is refused the same way until a row
  models their dependence. <This search: overlap refused / defined as follows, with its check.>
- **m-3 (E-210): a redrawn loss carries the run's stop-fill convention.** A loss is booked as a stop exit at
  `stop_slippage_ticks` with the per-contract costs at the stop; a win at the target as a limit
  (`target_slippage_ticks`); a loss at the cushion as a stop. The race's barrier already nets x_stop out of the room
  (above), so the convention costs the user and never the floor. The same for designs and baselines; the +1 and +2
  tick stresses (measure 29) add to it.
- **R-10: the redraw for a trade that ends at a time limit**, declared here with **zero gross expectation**. The house
  form, unless this declaration replaces it with another of zero gross expectation and net = -(costs) shown by an
  exact-fraction test before the pin:
  - **Decided at the fill (N-1).** For every trade, once, from what is known at its fill:
    **L_fill = min(l, c - max(x_stop, x_flat))**, fractional, never rounded (E-237), where x_flat is the flatten-side
    exit cost (commission plus `flatten_slippage_ticks`); the comparison L_fill > 0 is made to the runner's declared
    tolerance `EPS` (in dollars; `EPS`: <...>, declared here, U-1). The decision never reads the run's exit,
    **whatever its later exit**: two trades identical at the fill fare alike.
    - **L_fill > 0:** the trade is raced or walked by the table below. Both laws use the floor-side barrier
      **L_race = min(l, c - x_stop) >= L_fill**, as the runner books it (m-1): a barrier loss with its stop-side cost
      ends exactly on the floor; a walk's time exit pays the flatten-side cost, clipped at the floor's room where
      x_flat > x_stop -- that clip's credit, at most x_flat - x_stop a trade, is counted and printed beside (zero while
      the profile's stop and flatten costs are equal, as in every vendored profile).
    - **L_fill <= 0 where the floor's room binds (B-2): the account is booked as failed at the fill** -- its balance
      taken to the floor, a breach, replaced at the close as the engine does. This is the race's own limit as L goes
      to 0 (a loss of L with its cost lands on the floor), so it needs no new law. These failures are
      **counted apart** and their share reported beside the verdict.
    - **L_fill <= 0 where the daily loss limit's room binds:** the day stops (`stopped`), as the engine does.
    - **A daily loss limit at or below e + max(x_stop, x_flat)** (at the arm's stress) is refused at construction
      (m-3): it would stop every day at its first offer, an account that never trades and never fails.
    - **Zero contracts at a positive room (C-1): the account ends out of room.** The account's floor room under one
      contract's risk at **the smallest stop the design can place at the account's state** (its declared stop floor,
      as Stage 2's D-318 reads it, `sizing.py`'s smallest offered stop; never read from the path) buys no trade at
      any stop (section 3's room cuts), and never reaches a fill. Above that room, a zero at this trade's own stop is
      a no-trade slot. As Stage 2's engine rules it (D-318, D-335), the account ends
      **out of room** at that slot: it is failed, **counted apart beside the at-the-fill failures**, its share printed
      beside the verdict, and replaced as a breach is. Zero contracts from another cut (D-272's stand-aside, the
      allowance) is a no-trade slot; the declaration shows that state is not absorbing, or the design is refused.
    - So no account is ever left alive, billed and unable to trade, at a fill or at a slot. Exact tests hold both
      boundaries: an account at floor room e + max(x_stop, x_flat) - epsilon (e the entry cost) is failed; one at
      e + max(x_stop, x_flat) + epsilon takes the race; a room just above zero but under one micro's risk at the
      smallest offered stop ends out of room; one just over it is a no-trade slot at a wider stop and trades one micro
      at the smallest.
    - **Their size is to be read** before any search pins, by the light synthetic experiment of the full read's m-8
      (the lead's queue item): synthetic only, one worker, `OMP_NUM_THREADS=1`, under 500 MB, minutes; toy rules
      shaped like Topstep's, cited by their keys (`combine_mll` with its trailing lock, the daily loss limit where the
      account has one); costs from `fills.yaml`'s `assumed` profile with `round_turn_by_instrument`; brackets over S1's
      search-year range and S3's whole-micro room cut. Three arms: (i) the B-2 rule only; (ii) (i) plus the
      out-of-room rule; (iii) the vendored engine's handling (the race at the clip, and D-318). Read per offer the
      share of lanes that take, fail at the fill, end their day, end out of room, or do none of these (the invariant,
      zero in (ii)); read at the end `P_B`, replacements and the failure share by route, and the band of the n-1 note
      at a stop-only stress. Its output is a result file with its manifest, or labelled exploratory; it chooses no
      lever.
  - **The lattice step s is per trade (S-1):** s = max(1, ceil(sigma sqrt(T) / sqrt(`WALK_MAX`))) ticks -- the
    smallest whole-tick step keeping the walk's step count n at or under the runner's limit `WALK_MAX`
    (`WALK_MAX`: <...>, declared here, U-1), from sigma and T as fixed below and `WALK_MAX`, nothing else.
    It need not divide the stop or the target: fractional barriers are resolved by the driftless two-point last
    sub-step (B-1). **A trade is never refused for its step.** **One T for both s and n (s-b):** T is the limit known
    at the fill for every row, the table's last included (the fill-time law's T);
    the realised exit time decides neither s nor n.
    The barriers are not moved to the lattice; the walk's last sub-step resolves them (below).
  - **Which law applies** is read from the run's terminal state on the as-walked (reflected) path, every state mapped:

    | terminal state in the run | its law | booked at |
    |---|---|---|
    | its target | the race | target-side cost |
    | its stop | the race | `stop_slippage_ticks` and the stop's costs |
    | its stop gapped through | the race (the gap's extra fill is a path feature, read beside as-walked) | as a stop |
    | the floor or the daily loss limit, before its stop | the race (the cushion, net of x_stop, is the nearer barrier) | as a stop |
    | a profit level set by a rule (lever A3's `cap`, the consistency allowance; the need-aware pass or consistency exit, `need=x`) | the race at the as-placed target min(g, level) | target-side cost |
    | the 15:10 CT flatten | the stopped walk, T to the flatten | `flatten_slippage_ticks` |
    | a news window's start (E-202 (2)(a)) | the stopped walk, T to the window (a declared reading, m-4: the gap to E-223 M-4's as-walked cost and the news-flatten share printed beside) | `flatten_slippage_ticks` |
    | its max hold | the stopped walk, T to the max hold's end | `flatten_slippage_ticks` |
    | any other exit before its barriers (an unscheduled release's flatten) | the stopped walk, T the limit known at the fill (the flatten, a scheduled window or the max hold, whichever comes first), its share reported | `flatten_slippage_ticks` |

    A test of the build holds the mapping exhaustive: an exit reason the table does not name is refused.
  - **The stopped walk:** a symmetric driftless walk from the fill on the lattice of step s; its floor-side barrier
    is L_race = min(l, c - x_stop), fractional, never rounded (E-237), as the runner books it (m-1); its target g as
    placed. **Its last sub-step before a fractional barrier is a driftless two-point race** (E-237): at the last
    lattice point above the floor-side barrier, rho below it, a step goes down to -L_race with probability
    s / (s + rho), else up one step s -- mean zero; a fractional g' is resolved the same way on its side. **Where one
    lattice point is both the last above the floor-side barrier (rho_d below) and the last below the target (rho_u
    above)** (m-2), the step goes up to the target with probability rho_d / (rho_u + rho_d), else down to -L_race --
    mean zero, the runner's rule. It stops at the first of the two barriers or the time limit T, and its outcome is
    `+g`, `-L_race`, or the walk's value at T, each paying its exit's cost. Gross expectation is exactly zero
    (optional stopping: a bounded martingale at a bounded time); a floor-side barrier loss with its stop-side cost
    ends exactly on the floor; a time exit's flatten-side cost is clipped at the floor's room, its credit counted and
    printed beside.
  - **Its clock is fixed from the run's own causal bars:** T is the time from the fill to the limit, known at the fill
    for every row (s-b); the declared volatility estimator sigma (its window and unit: <...>) is read on
    bars closed at or before the alert, never the trade's later bars, so it is no choice made after a look. The
    estimator sets the walk's **number of steps**, n = round(sigma^2 T / s^2) (to the nearest integer, halves up, at
    least one), s the per-trade step above (so n <= `WALK_MAX`). This at-the-alert reading **overrides** the design note
    1.7's "causal volatility per bar of the trade's holding window", being the stricter.
  - Exit time, costs and resolution stay as run (CHARTER 3.2). Its draws are keyed by the coin field under their own
    draw kind (section 12). The exact-fraction test runs over a grid of (g, l, c, x, s, n) with fractional cushions
    and unequal exit costs: gross zero, net = -(costs), the floor-side barrier loss ending exactly on the floor and
    breaching it (E-237's forced-loss toy), the time exit's clip counted, and the both-barriers-within-one-step case.
  - **What the split does and does not move.** Each law has zero gross expectation given its inputs, so no trade gains
    a mean. But which trades reach a time limit is the real path's resolution structure (momentum or mean reversion
    changes how often a barrier is hit within T), and through the contract's **convexity** a different spread of
    outcomes is a different expected composite. CHARTER 3.2 keeps resolution as run, so this channel is declared, not
    removed. **Beside, per component:** the share of time-limited trades, and the **fill-time law** reading -- every
    trade takes the stopped walk with T the limit known at the fill, using no post-fill path -- with its gap from the
    deciding reading.
- **The pair rule** (`feature-rules` section 3; the Phase 0 audit's D-1, D-13). Wherever a reading compares a resting
  entry with its reflection on the real path -- the no-harm floor, the as-traded floor, the path-structure gap -- a
  pair whose fill bar touches either leg's stop or target **contributes zero lift**: both legs are booked at the
  as-walked leg's settled outcome for that pair, each with its own (equal) costs, so the pair's
  difference is exactly zero by construction. The pair is counted, its share reported and capped at <the cap>.
  Without it the stop-first fill-bar rule favours the real resting side by construction.
- **Beside, never credited:** the as-walked (reflected) result and its gap from the martingale-outcome result, the
  design's **path-structure edge**; the **as-traded** result (the real resting side, unreflected) with E-204's
  decomposition, as a stress.
- **The oracles** (CHARTER section 4, amended E-210): stage one's zero-edge ceilings are read on the martingale-outcome
  reading, where an output outside them is an engine error; an as-walked result outside them is the path-structure
  edge, reported beside, never "fixed".

## 6. The survey, the surrogate and the rounds

*CHARTER 3.3 (b)-(f), 3.9 "Search: every measure at once". Every number here is fixed before the survey and never
extended after a look.*

- **The gates read before any outcome**, per surveyed design, each refusing: supply (trades per session in every search
  year), resolution (the unresolved share at most 5 % overall and in every year, D-212), realised risk (D-212, D-308).
  A design that fails a gate is counted and its measures are not read.
- **The survey:** the survey size <N designs>, a **space-filling** sample of the lever space (<method: a scrambled
  Sobol or Latin hypercube design, its seed by role, section 12>), on the search years only, each design read on
  every measure of section 1 at every seed of the survey's seed set.
- **The surrogate:** <model class> predicting **every measure** from the levers (which levers move which measures,
  where trade-offs are unavoidable, where the ruin chance jumps); its hyperparameters fixed here or chosen by
  cross-validation inside the search years with folds in session blocks, purged and embargoed longer than the longest
  horizon read (`feature-rules` section 4), every value tried counted.
- **The rounds:** <R rounds> of <batch size> designs each, proposed **inside the limits** by constrained,
  multi-objective Bayesian optimisation (<acquisition, its constraint handling, its seed by role>); run; refit; repeat.
  **The number of rounds is fixed here and never extended after a look**; a stopping rule, if any: <a rule on the
  surrogate's own state, fixed here>.
- **The plateau rule** (CHARTER 3.3 (e)): a finalist's neighbours must also do well -- its metric and radius pinned in
  section 7.
- **The finalist order rule:** how the ordered list of finalists is produced on the search years, declared before the
  survey and pinned in section 7; the list itself pinned in the lead's row before the held-out read (section 14).
- **Every design tried** is logged in `results/variants.jsonl` with its manifest (CHARTER 3.3 (f)); the map and the
  ledger persist for the next firm, lever or model. **No held-out result** is written to either.
- **The reverse reading** (choose on the held-out years, judge on the search years) is not run before the held-out
  test; afterwards only as a described reading (CHARTER 3.6 (g)).

## 7. The pinning row: every input of 3.8 and 3.9, in one row, before the survey

*CHARTER 3.9. Every input below is set from **the search years only** (H4's search-year outputs, the lever table, the
verified rules), in one lead's row, **before the survey** runs; none is changed after a search-year result except by
re-declaring the search. The limits, the bankroll budgets, the weights and the size that matters are **the lead's**
(E-221, Wave 4.2, by the operator's delegation), set from H4's search-year results by a rule declared before H4 is
read, pinned in that one row before the survey, never after a held-out read, and written here before the pin. This
section is **never pinned alone**: the whole renamed file is frozen by its LF sha256 at the pin (section 14), with
this table filled, and every later row cites that one hash.*

| input | value | its direction or form | source (search years only) and row |
|---|---|---|---|
| **the limits**, each a floor or a ceiling, and any workload ceiling | <...> | <direction>; the point estimate governs (E-221, the lead's O-5 ruling, E-230): a design passes the limit when its point estimate is inside it, fails it when outside, never a second margin; the one-sided check's level, reported beside each limit, never deciding | the lead's, from H4's search-year results by a rule declared before H4 is read (E-221) |
| **the bankroll budgets** of measure (24) | <...> | <...> | the lead's, as the limits (E-221) |
| the **dimension** definitions, their normalisers or loadings, and their **caps** (lo, hi) with the cap margin | <...> | the composite is clipped to [0, 1] (the design note's 1.3) | H4's measure-structure analysis (Wave 4.1) |
| **the weights** | <...> | non-negative, summing to one | the lead's, from H4's search-year results by a rule declared before H4 is read (E-221) |
| **the composite** or **the fallback** -- **one, never both** | <...> | the fallback is P under the bankroll stop (`P_B`, MEASURES.md section 2), pinned in place of the composite, never tried after it | <...> |
| **the size that matters** (O-3) and the **power target** | <...> | on the composite's scale: the smallest difference that would change which design a user should run, with the power reported | the lead's, from the baselines' search-year results (E-221) |
| the **regimes** (the volatility threshold's rule) and **most years** (n_Y) with the minimum group size | <...> | from the search years, or a rule fixed in advance | <...> |
| the **finalist order rule** and the **plateau rule** (metric, radius) | <...> | <...> | <...> |
| **the gate's quantile** and the **minimum count of held-out starts** complete over its horizon | <...> | over coin seeds on the held-out years; the search years' history-block reading beside, as a consistency condition (CHARTER 3.8 (c); E-221, O-6) | <...> |
| the **no-harm margin** for the playbook's trigger sides (E-221) and for as-traded resting triggers (one margin for both, unless two are named) | <...> | <...> | <...> |
| **the do-nothing floor** (E-255) | W42-R1's do-nothing composite and `DO_NOTHING_EPS`, cited from W42-R1 at its pinning row (`extended/wave42.py`) | a design's search-year composite above it by more than `DO_NOTHING_EPS`, applied before ranking; a design not above it is no finalist; the finalist's held-out composite above it by the same margin at the verdict | E-255; W42-R1 at its pinning row |
| **the L values** in the lever space | <...> | five the reference; three and two counted | E-202 (2)(c) |
| the deciding bound's form, J (seed sets) and m (seeds per set), and the seed keying | <...> | by the composite's form (section 8) | the design note's 2.2, 2.5 |

## 8. The three-way test

*CHARTER 3.6 (f). The design is the three-way test's design note, `docs/plans/THREE_WAY_TEST_design.md` at 181eb44
(Q-153, after three red-team reads, `docs/reviews/THREE_WAY_TEST_2026-11-18.md`, `_v2_`, `_v3_`; merged, E-213);
cite the commit whose text this declaration adopts, and state every point where it departs.*

- **(i) The coin-seed leg carries the level** (E-208). Each finalist and each baseline run **paired** -- the same seeds,
  the same start days, the same keying -- on the held-out years; the replicates are disjoint coin-seed sets on the
  fixed held-out history. The hypothesis, per baseline: on the held-out years the design beats it in expectation over
  coin draws. The statistic, fixed here: <the deciding bound by the composite's form -- Hoeffding or McDiarmid over
  every start-seed term for means and shares; an empirical-Bernstein or betting bound over seed sets when a quantile
  dimension is in the composite, by the rule the design note states; no t decides>. **The level bounds coin luck given
  the held-out history; it does not bound a favourable history**: the history null's false-pass rate is read for that
  (section 9).
- **(ii) The time leg, a declared consistency condition**, not a test at the level: the difference holds in **most
  years** (n_Y, section 7) and in both volatility regimes (threshold from the search years), with start-year groups and
  regimes as the design note's 3.4 writes them; a regime absent from the held-out years is reported beside. Each
  condition's stated size, with the overlap counted, is printed beside the verdict.
- **(iii) The held-out leg:** (i) and (ii) read on the held-out years only; the runner refuses any other start or
  outcome session (a scope condition).
- **The seed keying** (the design note's 1.5): every random element of a journey a fixed function of the coin field;
  keys of fixed length per kind; the side coin's key carries no account and no firm index; each start its own draws.
  J and m fixed here and never extended after the read.
- The coin-seed spread is reported: it is the user's payout variance.

## 9. Calibration and the power gate

*CHARTER 3.7. The deciding calibration and the power gate run after this whole file is pinned (section 14) and before
the go row; they read only what this file fixed. H3's earlier runs are design checks only.*

- **Their inputs, fixed in this file before the pin:** the seeds (section 12's `<S5>`, or the pinned H3 declaration's
  block, cited with its owner), the R-10 estimator, `EPS` and `WALK_MAX` (section 5), the deciding statistic (section
  8), J and m, the plants' grid, the synthetic generator and its fitted parameters' source (search years only), and
  the replicate counts: <...>. Nothing of them is chosen after a calibration or gate output.
- **Their outputs, pinned afterwards in E-115's calibration-plan form:** each run's result file with its manifest, and
  a record `docs/calibration/<F-NN>_calibration.md` citing those files' sha256 and the verdict, pinned by its own
  sha256 in a decision row (`tests/test_declarations_fixed.py` holds it). A failed calibration or gate is that
  record's verdict; it is never re-run with another seed. **A declaration that follows one closed by a failed
  calibration or power gate cites that record, reports it beside, and uses a fresh seed block**; a failed seed block
  is never reused. **A failed limit clause or power gate is never a free retry** (M-5 (c);
  E-258 (the lead's CHARTER 3.7 reading row)): W42-R1's limits, bankroll budgets, weights and size that matters are
  never changed for any search of the line -- every search, of any firm, whose section 7 applies W42-R1 -- after any
  calibration or gate that read them; a defect found in them goes through the failure protocol as a defect on record,
  and a corrected rule is a new rule under a new row whose searches never enter this F-HT. A successor search inherits
  them unchanged, changes only what the failure's diagnosis names, citing the record, with a fresh seed block, and
  never enters this F-HT (its candidates are tested only on data this line has never read, a later purchase, under its
  own k); every closed attempt of the line is counted and printed beside the verdict.

- **The whole pinned rule is calibrated as a whole** (E-007 (f)): the composite or the fallback, the limit checks, the
  time leg's conditions and the floors, all on the martingale-outcome reading.
- **Same-design nulls:** a design against its **antithetic twin** (every coin draw u replaced by 1 - u, for the
  reflection and the redraw alike), and the same design on two **disjoint seed sets**. The rule rejects them no more
  often than its level.
- **The history null:** distinct designs equal in expectation across histories, unequal on any one (<its construction,
  per the design note's 2.7>); the whole rule's pass rate on them across synthetic and history-block-resampled
  histories is **the history-level false-pass rate**, printed beside every verdict. History blocks are at least as long
  as the composite's longest horizon.
- **The power gate**, before the go row: the whole pass line's power at the level it assumes, **the do-nothing floor
  included: a planted design not above the floor, at the search-year screen or at the held-out verdict (section 10
  (c)'s two points), counts as a fail and never leaves the count** (E-255; section 7; B-1; n6)
  -- F-HT's level 0.05 / (k (k + 1)) with k = 13 next, the
  power at every k from 14 to 20 reported beside, so a re-statement at another k is a lookup, never a new run (m-e;
  K-2), and a k beyond 20 needs a re-statement run of the gate, from the go row's runner commit at the gate's pinned
  seeds -- a re-statement only, closing nothing, exit (B) citing it; without it the pass line is refused (n-c) -- on
  synthetic paths carrying NQ's dependence, with design pairs drawn from H4's baselines and from synthetic plants, at
  a planted improvement of **the size that matters** (the lead's, from the baselines' search-year results; E-221,
  O-3), at the **power target**, under the horizon embargo; in the same run, a design equal to the best baseline on
  every limit passes every limit check, in the form in force, with at least the power target (E-015's condition); and
  **the count of held-out starts complete over D-145's horizon** reaches its pinned minimum. If any fails, **the
  search goes no further** -- no go row, no survey: CHARTER 3.7's "the search does not pin" read on this template's
  order, the file closed by a row, its k unspent (it is assigned only at a held-out row) -- and exit (B) states the
  line's power from this gate.
- **The data decision** (E-007 (2); held, E-221): more history (QuantConnect's free NQ/ES from 2009, the operator's
  setup; or older bars bought, stated, never authorised) is not added -- the operator held the purchase. The power
  gate's result is reported with the size that matters and the power (the lead's, Wave 4.2); a purchase stays the
  operator's, never asked for after a failure.

## 10. The pass line

*CHARTER 3.8. A finalist passes, in its place in the fixed sequence, when (a), (b) and (c) all hold, every deciding
reading the martingale-outcome reading for the finalist and every baseline alike.*

- **(a) Limits** (E-221, the lead's O-5 ruling, E-230; it replaces E-207's limit wording).
  **The point estimate governs:** the finalist passes a limit when its point estimate is inside it, and
  fails it when the estimate is outside -- never a second margin; the limits carry none of their own. A one-sided
  check of crossing (the red team's B-10 form), at the level pinned in section 7, is reported beside each limit and
  never decides (section 11).
- **(b) Each baseline beaten:** the composite (or the pinned fallback) above **each** baseline's, an
  **intersection-union** test with every comparison at the full level of F-HT's k, by the calibrated coin-seed
  leg on the held-out years, the time leg's conditions met. Every comparison states the finalist's L and each
  baseline's L.
- **(c) The floors:** verified rules; **conduct tier 1**; CHARTER section 4's constraints, every trade resolving among
  them; **the do-nothing floor** (E-255; W42-R1 at its pinning row): on the search years at the screen, before ranking
  and before the finalists' row, a design's composite above W42-R1's do-nothing composite by more than
  `DO_NOTHING_EPS` (a design not above it is no finalist), and on the held-out years at the verdict, the finalist's
  held-out composite above it by the same margin (else a fail at its place, whatever its test statistic, the held-out
  template's section 8); hand entry at least L minutes from alert to order; **the zero-edge long-run gate** -- the
  median log growth of the required bankroll over D-145's horizon (Stage 2 D-14) above zero at the pinned lower
  quantile **over coin seeds on the held-out years**, the search years' history-block reading beside as a
  consistency condition (CHARTER 3.8 (c); E-221, O-6), on the martingale-outcome reading, with fees, payout latency,
  the tier-2 consequences and D-145's tier-3 denial applied (the 0 % reading beside), on starts complete under the
  horizon embargo whose count reaches the pinned minimum; **the fill and supply stress** -- at **+1 tick** of worse
  fills (29) and with **10 % of signals missed** (28) the finalist still beats each baseline on the composite at the
  point estimate, both under the same stress, inside every limit in the form in force; **the playbook side's no-harm
  floor** (CHARTER 3.5; E-221, E-230): the trigger side's composite on the search years not below the coin side's by
  more than the pinned margin, read before the finalists' row -- a trigger whose side fails it offers no playbook side
  and that design is not carried; **the as-traded floors** for resting triggers traded as their real orders -- **the
  no-harm floor** on the search years, and **the as-traded floor** on the held-out years (the finalist's as-traded
  composite ahead of each baseline's as-walked composite at the point estimate). The no-harm and as-traded floors are
  read on the real path, with no redraw (N-1).
- **The verdict** is read on the martingale-outcome reading, at **0 % payout denial**, the Responsible Trading
  Program's placement off and the **Focused Trader Program off** (E-008 (2); E-007 (3); Stage 2 D-234, D-289). The
  level is printed **nominal** while the held-out read ledger is not empty, and **the history-level false-pass rate**
  is printed beside it.
- **O-6, ruled (E-221): option (a).** The held-out years hold only one disjoint block of D-145's horizon, so no
  history resample can be formed on them (the design note's 4.4). The gate's quantile is therefore over coin seeds on
  the held-out years, and the search years' history-block reading is read beside it as a consistency condition: it
  is printed beside the verdict, and a failure of it is reported with the verdict.

- **The fixed sequence over finalists** (CHARTER 3.7; E-203 S-1; E-221, O-1): every firm's ordered finalists enter
  the **one joint fixed-sequence test** of section 2, in the joint order by the rule fixed in
  `prereg/TEMPLATE_heldout_test.md` (M-1) -- run under the held-out test's declaration, one declaration of
  its own (E-238), which fixes the order across the firms before the held-out read -- each finalist at the full
  level of the one k, stopping at the first failure -- one k for the joint sequence.

## 11. Beside, never deciding

- The denial ladder; the break-even denial rate (33); the placement on; the binding Focused Trader models.
- P by month; mean net; CVaR10; P under a bankroll limit; the effective sample size (E-007 (e)).
- The frontier over every measure and a menu under the limits; every measure of `docs/MEASURES.md`.
- The as-walked result and the path-structure edge, never credited; the as-traded stress of resting triggers.
- Per component: the share of time-limited trades and the fill-time law reading's gap from the deciding reading
  (section 5, R-10); the share of pairs the pair rule settled.
- The playbook trigger side's held-out reading (E-221, O-4; its search-year no-harm floor decides, section 10 (c));
  each limit's one-sided check of crossing, limit by limit, beside its point estimate, which decides -- the
  point estimate governs, never a second margin (E-221, E-230, O-5); the long-run gate's search-year history-block
  reading (E-221, O-6).
- The five-minute cell beside every finalist; the registered rows of the baselines; the coin-seed spread.
- Per year and per regime, each difference with its coin-noise standard error; each time-leg condition's stated size.
- Not modelled, said wherever a scorecard appears: the user's time, taxes.

## 12. Seeds -- by role, found nowhere else

| seed | its role: what it draws, by draw kind |
|---|---|
| `<S0>` | the survey's space-filling sample |
| `<S1>` | the coin field on the search years: the reflection coin, the race, R-10's stopped walk, missed-signal draws (28) -- one draw kind each |
| `<S2>` | the surrogate's fitting and the round proposer's optimiser, if either draws |
| `<S3>` | the plateau rule's neighbours, if drawn |
| `<S4>` | the held-out test's coin field -- disjoint from every seed drawn on the search years |
| `<S5>` | the deciding calibration and the power gate, if not the design note's own block (cite its owner) |
| `<S6>` | spare, drawn by nothing |

- Every seed an integer written here before any run, **one role each**, a block never used before in Stage 2 or here,
  **found nowhere else**: checked by the house search with the licensed data excluded (`grep -rIlw
  --exclude-dir=.git --exclude-dir=data` over every worktree and the vendored snapshot, and `git grep` over every
  commit of every branch), and by an arithmetic fold over every tracked `.py` (the design note's section 7), the
  command and its hits written here; a test of the draft refuses its block in any other declaration.
- **Keys of fixed length per draw kind**, passed to a counter-based generator (the design note's 1.5; numpy reads
  `default_rng([a, b])` and `default_rng([a, b, 0, 0])` as one stream); other streams are children of a named seed,
  never the seed plus an offset (E-171).
- The design and every baseline read the same keys (the pairing). A seed chosen after a result is a variant. Inherited
  seeds are used only as their owners registered them, named here with their owners.

## 13. The count

- **One k per held-out test** at **0.05 / (k (k + 1))**; the one joint fixed-sequence test of every firm's finalists
  spends one k (E-221, O-1), taken by the held-out test's declaration, one declaration of its own (E-238), not by
  this search; the confirmation spends none (CHARTER 3.7). The program's numbering continues Stage 2's
  program U (E-001): **k = 13** is the next.
- **F-HT's k is assigned at its held-out row** (E-204): the held-out test's declaration is not counted by the
  gatekeeper's k rule until that row exists. That row comes before the held-out run, so E-204's repeat clause (another
  declaration taking a k between a run and its row) cannot arise. If another declaration takes a k first, F-HT's k is
  the next free one and each finalist's place power is re-stated at the new level before the held-out run
  (a lookup in each gate's output at k = 14 to 20, section 9) (exit (B) cites it); a k beyond 20 needs a re-statement
  run of the gate, from the go row's runner commit at the gate's pinned seeds -- a re-statement only, closing nothing,
  exit (B) citing it; without it the pass line is refused (n-c). F-HT withdrawn after its held-out row still spends
  its k (E-005 (d)); **a search's withdrawal before F-HT's held-out row spends nothing** -- no search holds a k.
- **Every design tried is counted** in `results/variants.jsonl`: the survey's N, every round's batch, every L, every
  failed-gate design. Written as a product and a number: <survey N + rounds x batch, each at its L values>.
- The program's honesty sentence: <what Stage 2's programs and this repository have read on these bars, and that the
  level is nominal while the ledger is not empty, the decision carried by one confirmation on unread data>.

## 14. The run order -- refusals first

1. **The reads of the draft, before anything is pinned:** the scout's challenger brief (Q-150), the red team and the
   gatekeeper read the final text with section 7's values filled in; every blocking finding answered. A value filled
   in after a read is a change: the red team checks its diff, or re-reads the draft if the value bears on a blocking
   finding. After the pin a change is a new declaration.
2. **The pin**: after H4 and Wave 4.2's inputs (the lead's, E-221) are written into section 7, the lead's row pins
   **the whole renamed file** by its LF sha256 (the gatekeeper renames and replaces `F-XX` first, then hashes).
   Section 7 is never pinned alone; the calibration's and gate's inputs are inside the frozen file. Q-158, the
   reader's held-out guard, is merged (E-222). **No search pins before E-258 (the lead's CHARTER 3.7 reading row)
   exists** in `DECISIONS.md`, its bolded title beginning `CHARTER's "pin" read`
   (`tests/test_design_search_template.py` refuses a pinned search that cites any other row, a bare number, or none).
   **A search pinned after the membership event is never a member of this F-HT** (H-1';
   E-257). **At most one member search per firm:** a second hash row for a firm before the membership event is
   refused at its pin, whether or not the first is closed (R-1; E-259); after the event a further search of the firm
   may pin, outside this F-HT, unless the no-new-pin bar holds. Refusing before it:
   the identities on record as holding (`identity/stage2_identity.py`, every baseline's runner identity, the search
   runner's own).
3. **The calibration and the power gate** (section 9), each from a **clean checkout** of a named commit
   (`scripts/run_clean.py`) under **run.lock** (one heavy run on the machine, skill `run-lock`); their outputs pinned
   in E-115's form; the data question to the operator.
4. **The go row**: its third cell's first text is the token
   `go: F-NN @ <its LF sha256> -- runner <the runner commit, 40 hex> -- <text>` (G-1, C-3; E-259), counted only
   outside any fenced block, in that exact form, at its declaration's pinned sha256, in a row strictly after that
   declaration's hash row (G-2); a go-like row that is not exactly the token is a hygiene problem that refuses every
   membership reading until a later `heldout-void: E-NNN -- <reason>` row voids it, a void of a valid row being a
   no-op, fences and voids read by the reader's own rules; so are a go row for a closed search and a second go row for
   one declaration; an HTML comment in `DECISIONS.md` is read exactly as `extended/reader.py` reads it, with no rule
   of its own (n-d) (the reader's `go_problems`, `extended/reader.py` at its pinning row's sha256, n-a); it cites the
   calibration record's hash and names, in its `runner <40 hex>` sub-form, the runner commit the calibration ran on --
   **the survey and every round run on that runner commit, bound by its sha; a change to deciding code after it is a
   new declaration** (U-1); the survey reads its own checkout's log, at a commit after the go row, bound as the reader
   binds it: HEAD descends from (or is) the runner commit, and every file of section 1's `- **The deciding files:**`
   line is byte-identical at HEAD and at the runner commit and unchanged in the working tree (the reader's `go_runner`
   and `go_row_present`; finding 2; Q-212); from here the survey may run. The lead freezes the event in the row right
   after the first counted go row, `membership: F-NN @ <its LF sha256> -- E-NNN` (the first go row's declaration, its
   pin's LF sha256, then the go row's id), which the reader enforces (F3). Under this template
   (E-258 (the lead's CHARTER 3.7 reading row)) CHARTER 3.7's "the search's pin", "does not pin" and
   "before any search is pinned", and CHARTER 3.8 (a)'s "a pinning row ... does not pin", each mean **this go row**;
   the reader's pin and every "newer than the pin" mean **the hash row** of step 2.
   A search closed by a failed calibration, limit clause or power gate gets a closing row,
   `heldout-closed: F-NN @ <its LF sha256> -- <cause> -- <text>` (`prereg/TEMPLATE_heldout_test.md`'s closed list;
   `withdrawn` only before the membership event, W-1; `defect-on-record` only with a failed check on record at or
   before the membership event's commit (or the search's own declared refusal or identity), failing when run at the
   search's go-row runner commit, and the auditor's note that it cannot be fixed without changing a declared input,
   every such close counted (C-4), D-1; E-259); no search holds a k. The data question goes to the operator with the
   gate's result before the go row. Refusing at every later step: this file still hashing to its pin
   (`tests/test_declarations_fixed.py`), the go row present (checked by code: the survey runner refuses to start
   unless the reader's `go_row_present` (`extended/reader.py` at its pinning row's sha256) holds for this file's
   pinned sha256; it is False once this search has a finalists' or closing row), a clean checkout, the run lock held
   -- **Refusals first**, each refusing.
5. **The survey** on the search years only (one clean run, from the go row's runner commit); its gates before its
   measures; logged.
6. **The rounds**, each one clean run from the go row's runner commit, collected (`/collect`), never extended.
7. **The finalists' row**: the ordered finalists, their playbooks' rules and every fitted model's hash, written as a
   finalists' list file outside `prereg/` before the row, and the row in Q-158's token form,
   `heldout-finalists: F-NN @ <sha> list <sha>` -- this file's LF sha256, then the list file's -- as the first text
   of its third cell; written before any held-out read; the scout's challenger brief and the red team on the
   finalists.
8. **The held-out row** (k assigned, E-204), written as soon as, after the membership event, every member search has a
   finalists' row or a closing row (H-1'; E-257; E-221, O-1), for the held-out test's declaration --
   one declaration of its own (E-238), drafted on `prereg/TEMPLATE_heldout_test.md` (M-1), with its own F-number, pin
   and hash. It lists every member firm's finalists by each member search declaration's hash and finalists' row, in a
   joint list file that cites each search's finalists' list by its sha256; it fixes the joint order and takes the k;
   it carries the `Judged-block reads:` line; and it is the one family that reads NQ's held-out window. Its own
   finalists' row **is its held-out row** (m-3):
   `heldout-finalists: F-HT @ <its LF sha256> list <the joint list's sha256>`, F-HT its F-number, which Q-158's rule 1
   needs, so the reader enforces "after the held-out row". The joint order alternates by rank across the firms (H-2;
   E-257), by the held-out template's rule. Then **the held-out test**, the one joint fixed-sequence test, once, from
   a clean checkout of that row's commit, in the fixed sequence; the auditor on its result.
9. **The verdict row**; a carried design's registration and the confirmation's criterion declared there.

Each run once, watched to its exit, its file written with its manifest (`extended.results.write_result`, the
declaration's id, the design count, every seed and parameter). A failed check stays on record and is diagnosed by the
failure protocol, never rerun until it passes.

**The held-out reads (E-221, O-1; E-238).** **This search carries no `Judged-block reads:` line; the held-out
test's declaration carries it.** `extended/reader.py` (Q-158, merged at E-222) honours a held-out purpose only for a
pinned declaration that names it on its own `Judged-block reads:` line (a purpose named in prose authorises nothing)
and, by rule 1, only after a finalists' token row for that declaration's own hash, newer than its pin; by rule 2 the
first family whose judged read is ledgered holds the market's window. With no line in any search, no single search can
read NQ's held-out years, even with its own finalists' token from step 7, and the held-out test's declaration -- the
one family -- reads them once. Q-158 checks the finalists' token, not the held-out row, so the held-out-row condition is
held by the declaration and the auditor. The rules, binding whatever the code does:
- a held-out read is made **only after every finalists' row and the held-out row**, all citing their declarations'
  sha256s;
- the held-out years are read **once per market**, across declarations: a re-declared search gets no fresh read; the
  market's held-out test spends them (CHARTER 3.6 (c));
- an RD declaration never reads them before the market's verdict row, and no `registered_design` read of them (of
  P-14, P-15, P-16) is made before F-HT's verdict row (L-1; E-259).

What the held-out test's declaration reads, under its own line's two house purposes: `heldout_test` reads the
finalists and every baseline on the deciding reading, the time leg's groups and regimes, the long-run gate, and the
held-out readings section 11 puts beside -- the five-minute cell, the as-walked result and the path-structure edge,
the denial ladder, the playbook trigger side's held-out reading and the fill-time law; `heldout_stress` reads the
+1 tick and 10 %-missed stresses and the as-traded floor. Nothing of this search reads the held-out years.

## 15. What a pass and what a fail mean; the confirmation

- **A pass:** the finalist is **carried** -- it takes a registration id, its playbook, the auditor's read; its one
  confirmation is read against **a criterion declared at its registration, before the read** (CHARTER 5 (A)): at least,
  on the martingale-outcome reading, ahead of each baseline on the composite at the point estimate and inside every
  limit in the form in force; at the point estimate, the as-traded floor read on the real path, and ahead of each
  baseline at +1 tick of worse fills.
- **A fail -- what a fail means:** <the search closes (a closing row); it spends no k; nothing of it is rerun; a new
  question is a new declaration citing this one; exit (B) states the line's power from the power gate>.
- **The confirmation:** NQ from 2026-07-17 to the last session in the purchase order's stated range, never read from
  bars, recorded in the first `heldout-window: NQ 2026-07-17 to <last> -- <text>` row, which states that it
  opens the confirmation window, not a second held-out test, and governs; any later NQ or MNQ window row from
  2026-07-17 on is refused by the reader (`extended/reader.py`; n1), this repository's `_cw_problems` only a
  cross-check; the purchase and that row come before the first finalists' row of any member (C-5; finding 5), read
  once, only for F-HT's carried designs; a non-member search's candidates never use it (CW-1, CW-2; E-259);
  **a purchase**, the operator's.

## 16. Anything chosen after seeing results

*(Empty at the pin. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its manifest,
and recorded in its own decision row -- never added to this file once pinned.)*

---

*Sources: `CHARTER.md` sections 2-5 (E-210); `docs/plans/AMENDMENTS_draft_2026-11-18.md` sections 5-6 (R-10, the
template's fields); `docs/reviews/AMENDMENTS_v3_2026-11-18.md` (m-2, m-3, R-10); `docs/MEASURES.md`;
`docs/plans/LEVER_TABLE_topstep50k.md`; the three-way test's design note (`wt/wt-verify`); E-204, E-207, E-208, E-210,
E-211; the superseded form `prereg/TEMPLATE_family.md`.*
