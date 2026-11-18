# TEMPLATE: a design search's declaration -- copy it, never pin it

**What this file is.** The house form for a design search under the journey objective (`CHARTER.md` sections 2-3, in
force from E-210; the restart plan's Wave 2.1). It carries every field CHARTER 3.3 to 3.9 requires, E-210's two
template clauses (m-2, m-3) and R-10. It is not a declaration: it names no search, holds no seed, no k, no count, no
limit value and no figure, and its name matches neither the reader's grammar (`F-` or `RD-` and a number) nor any
test's declaration glob (`tests/test_design_search_template.py` holds that). It replaces `prereg/TEMPLATE_family.md`
for new work; that file is kept for the record.

**To use it:** copy it to `prereg/DRAFT_F-XX_<slug>.md` (a search is declared as a family: `F-` and a number at the
pin, its k assigned at its held-out row, E-204), replace every `<...>` with the search's own text, delete nothing but
the template's instructions in *italics*, and send the draft to the `scout`'s challenger brief (Q-150), the
`red-team`, then the `prereg-gatekeeper`. The lead pins it by the sha256 of its LF text (E-001 (b), E-003). **Nothing
declared is edited: a change is a new declaration.** A section left as the template wrote it is a gap the gatekeeper
refuses.

*Every rule below is a floor (CHARTER 3.8; DIRECTIVE Part 1). A draft may tighten one only with the tightening's size
and power at the search's level shown before the pin (E-051, E-015's condition); it may loosen none without the
operator. A rule value is cited by its key in the verified record, never typed. A result is cited by its file, never
typed.*

## 0. In plain words (for the operator)

<What the search looks for, for which firm and account, over which sessions; what a user would do with a finalist's
playbook; what would count as a pass (beating each baseline on the pinned composite, inside every limit, with the
floors); and what a fail means -- "the search closes, its k spent", never "we investigate further". Every parameter
named here is explained in a phrase and classed fixed / searched / dropped in the sections below.>

## 1. The question, the firm and the baselines

- **The firm and account:** <firm, plan>. Its rules are the verified ones only (CHARTER 3.1): Stage 2's ledger
  (`vendor/stage2/config/rules.yaml`) or this repository's record (`config/rules_extended.yaml` through
  `extended/firm_terms.py`), each key `verified` under its decision row. **Every key the search reads is listed here**
  with its status; an unverified, `changed` or `unstated` key is refused by the loader and cannot be a lever.
- **Its own execution protocol** (E-202; never another firm's reused): <the protocol's file and row>.
- **The baselines** (CHARTER 2, 3.8 (b)): for Topstep, naive coin harvesting (its levers fixed here: <...>), and Stage
  2's P-14, P-15 and P-16; for another firm, the set it declares, at least the naive coin on its own protocol. **Each
  baseline runs under the design's convention** -- the reflection and the martingale-outcome reading under the same
  seed keying, the same fill and cost mechanics, no arm shift, the same verdict settings -- **at its registered
  latency** (P-14 at five minutes; P-16 scheduled, its latency variants dropped, E-203 B-2). **Each baseline's runner
  identity:** its trade times and brackets equal its registered ones, path for path (<the identity, its file, its
  columns, its tolerance>). The registered rows are reported beside.
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
- **The re-baseline (H4)** reads the search years only, its runner refusing held-out sessions; any held-out output it
  computes is **sealed** (its hash recorded, the file unopened) until the held-out test (CHARTER 3.6 (e)).
- **Single use per market** (CHARTER 3.6 (c)): this search <does / does not> spend NQ's held-out years. Which firm's
  search spends them, or whether one search covers several firms, is the operator's (**O-1**): <the operator's
  ruling and its row, or "pending -- this search does not pin until it is ruled">. A later search on the same bars
  reads them as a description only, or moves its held-out years to data not yet read (a purchase or the operator's
  setup).
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
- **The confirmation window:** NQ from 2026-07-17, declared now, never read until a carried design is registered, and
  a purchase, the operator's (section 15).

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
- **Combinations refused** (the table's section 4, `check_design`): <...>.
- **Fixed for every design** (the table's section 5: floors, not levers): restated by reference, never searched.

## 4. The component schedule across sessions, and the contract fit

*CHARTER 3.5. A design is a schedule of components; each component one session-specific trigger with its own trade
shape.*

- **Sessions in the search:** every session the firm allows (Asia, London, NY AM, NY PM, and the table's `evening`
  window), with their boundaries read from the verified `trading_hours` and declared rows (**Any hour**: no cap on
  trading hours, E-202 (2)(b); workload (30) reported, a ceiling only if the operator sets one as a limit). An
  overnight trigger enters only after H2 (the overnight data-integrity run) has passed: <its row>.
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
- **The side rule** (part of every design; **pending the operator, O-4**). Evaluated: one literal coin draw per moment,
  shared by all the user's accounts and firms. Under any side rule, while any position is open a new trade takes that
  position's side or is skipped (R-12: a conduct rule, not a lever; its supply cost reported with (37)). Until O-4 is
  ruled, every playbook states the coin side, with the model-side and as-traded readings beside, and no playbook goes
  to a user. A model side, or a resting trigger traded as its real order, appears in a playbook only if it clears **the
  no-harm floor** (section 10 (c); the no-harm margin pinned in section 7).
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
  | no entry and no fill inside a verified news window; a position open at its start flattened (E-202 (2)(a), E-200 R-1); limits cancelled at its start | <...> |
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
  - l is the stop, g the target; c is the room the engine hands the draw -- the nearer of the floor and, where it
    binds first, the daily loss limit -- read after the entry cost is booked; x_stop is the **stop-side exit cost**
    (the per-contract commission at the stop plus `stop_slippage_ticks` of `vendor/stage2/config/fills.yaml`'s
    profile in use), and x_target the target-side one (commission plus `target_slippage_ticks`).
  - **The loss barrier is L = min(l, c - x_stop)**, rounded inward to the tick lattice when the cushion binds (a
    fractional cushion never rounds outward: rounding outward and then clipping would bring back the edge this rules
    out, N-4). **p = L / (L + g).** A win gains g and pays x_target; a loss loses L and pays x_stop.
  - So a loss plus its exit cost never passes the floor and **the clip never binds** (the engine's
    `pnl = max(pnl, -cushion)`); every trade's gross expectation is exactly zero and its **net expectation is exactly
    minus its costs**, at every cushion.
  - **A trade with L <= 0 is not taken** -- the runner's rule; `BinaryDraw` books such a slot as a zero and counts it,
    so the runner, not the engine's draw, decides it, and counts it apart.
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
  before any draw, on the scheduled entries and the run's exit times, never the path's. Until this declaration
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
  - **Which law applies** is read from the run's terminal state on the as-walked (reflected) path, every state mapped:

    | terminal state in the run | its law | booked at |
    |---|---|---|
    | its target | the race | target-side cost |
    | its stop | the race | `stop_slippage_ticks` and the stop's costs |
    | its stop gapped through | the race (the gap's extra fill is a path feature, read beside as-walked) | as a stop |
    | the floor or the daily loss limit, before its stop | the race (the cushion is the nearer barrier) | as a stop |
    | the 15:10 CT flatten | the stopped walk, T to the flatten | `flatten_slippage_ticks` |
    | a news window's start (E-202 (2)(a)) | the stopped walk, T to the window | `flatten_slippage_ticks` |
    | its max hold | the stopped walk, T to the max hold's end | `flatten_slippage_ticks` |
    | any other exit (an unscheduled release's flatten, a rule's exit) | the stopped walk, T to the run's exit time, its share reported | `flatten_slippage_ticks` |

    A test of the build holds the mapping exhaustive: an exit reason the table does not name is refused.
  - **The stopped walk:** a symmetric driftless walk from the fill on a lattice of step s ticks, s dividing l and g;
    its loss barrier is the race's L = min(l, c - x_stop) with x_stop replaced by the larger of x_stop and the
    flatten-side exit cost (commission plus `flatten_slippage_ticks`), **rounded inward** to the lattice; its target
    g. It stops at the first of the two barriers or the time limit T, and its outcome is `+g`, `-L`, or the walk's
    value at T, each paying its exit's cost. Gross expectation is exactly zero (optional stopping: a bounded
    martingale at a bounded time), and no exit passes the floor, so the clip never binds. A trade with L <= 0 on the
    lattice is not taken (the runner's rule).
  - **Its clock is fixed from the run's own causal bars:** T is the time from the fill to the limit, known at the fill
    except for the table's last row; the declared volatility estimator sigma (its window and unit: <...>) is read on
    bars closed at or before the alert, never the trade's later bars, so it is no choice made after a look. The
    estimator sets the walk's **number of steps**, n = round(sigma^2 T / s^2) (to the nearest integer, halves up, at
    least one); the lattice's step is fixed by the barriers. This at-the-alert reading **overrides** the design note
    1.7's "causal volatility per bar of the trade's holding window", being the stricter.
  - Exit time, costs and resolution stay as run (CHARTER 3.2). Its draws are keyed by the coin field under their own
    draw kind (section 12). The exact-fraction test runs over a grid of (g, l, c, x, s, n) with fractional cushions
    and unequal exit costs: gross zero, net = -(costs), no exit past the floor.
  - **What the split does and does not move.** Each law has zero gross expectation given its inputs, so no trade gains
    a mean. But which trades reach a time limit is the real path's resolution structure (momentum or mean reversion
    changes how often a barrier is hit within T), and through the contract's **convexity** a different spread of
    outcomes is a different expected composite. CHARTER 3.2 keeps resolution as run, so this channel is declared, not
    removed. **Beside, per component:** the share of time-limited trades, and the **fill-time law** reading -- every
    trade takes the stopped walk with T the limit known at the fill, using no post-fill path -- with its gap from the
    deciding reading.
- **The pair rule** (`feature-rules` section 3; the Phase 0 audit's D-1, D-13). Wherever a reading compares a resting
  entry with its reflection on the real path -- the no-harm floor, the as-traded floor, the path-structure gap -- a
  pair whose fill bar touches either leg's stop or target **contributes zero lift** (both legs settled alike), and is
  counted, its share reported and capped at <the cap>. Without it the stop-first fill-bar rule favours the real
  resting side by construction.
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
re-declaring the search. The operator's inputs (the limits, the bankroll budgets, the weights, the size that matters)
come from Wave 4.2 and their row, and are written here before the pin. This section is **never pinned alone**: the
whole renamed file is frozen by its LF sha256 at the pin (section 14), with this table filled, and every later row cites
that one hash.*

| input | value | its direction or form | source (search years only) and row |
|---|---|---|---|
| **the limits**, each a floor or a ceiling | <...> | <direction>; the form in force (E-207: inside with a margin wider than its noise, the margin's level) and **O-5**'s pending form (a one-sided check's level) | <...> |
| **the bankroll budgets** of measure (24) | <...> | <...> | the operator's (Wave 4.2) |
| the **dimension** definitions, their normalisers or loadings, and their **caps** (lo, hi) with the cap margin | <...> | the composite is clipped to [0, 1] (the design note's 1.3) | H4's measure-structure analysis (Wave 4.1) |
| **the weights** | <...> | non-negative, summing to one | the operator's trade-off answers (Wave 4.2) |
| **the composite** or **the fallback** -- **one, never both** | <...> | the fallback is P under the bankroll stop (`P_B`, MEASURES.md section 2), pinned in place of the composite, never tried after it | <...> |
| **the size that matters** (O-3) and the **power target** | <...> | on the composite's scale | the operator's (Wave 4.2) |
| the **regimes** (the volatility threshold's rule) and **most years** (n_Y) with the minimum group size | <...> | from the search years, or a rule fixed in advance | <...> |
| the **finalist order rule** and the **plateau rule** (metric, radius) | <...> | <...> | <...> |
| **the gate's quantile** and the **minimum count of held-out starts** complete over its horizon | <...> | over coin seeds and history-block resamples (CHARTER 3.8 (c)); how it is formed on the held-out years is O-6 (section 10) | <...> |
| the **no-harm margin** for model sides and for as-traded resting triggers (one margin for both, unless two are named) | <...> | <...> | <...> |
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
  block, cited with its owner), the R-10 estimator (section 5), the deciding statistic (section 8), J and m, the
  plants' grid, the synthetic generator and its fitted parameters' source (search years only), and the replicate
  counts: <...>. Nothing of them is chosen after a calibration or gate output.
- **Their outputs, pinned afterwards in E-115's calibration-plan form:** each run's result file with its manifest, and
  a record `docs/calibration/<F-NN>_calibration.md` citing those files' sha256 and the verdict, pinned by its own
  sha256 in a decision row (`tests/test_declarations_fixed.py` holds it). A failed calibration or gate is that record's
  verdict; it is never re-run with another seed.

- **The whole pinned rule is calibrated as a whole** (E-007 (f)): the composite or the fallback, the limit checks, the
  time leg's conditions and the floors, all on the martingale-outcome reading.
- **Same-design nulls:** a design against its **antithetic twin** (every coin draw u replaced by 1 - u, for the
  reflection and the redraw alike), and the same design on two **disjoint seed sets**. The rule rejects them no more
  often than its level.
- **The history null:** distinct designs equal in expectation across histories, unequal on any one (<its construction,
  per the design note's 2.7>); the whole rule's pass rate on them across synthetic and history-block-resampled
  histories is **the history-level false-pass rate**, printed beside every verdict. History blocks are at least as long
  as the composite's longest horizon.
- **The power gate**, before the pin: the whole pass line's power at the search's level, on synthetic paths carrying
  NQ's dependence, with design pairs drawn from H4's baselines and from synthetic plants, at a planted improvement of
  **the size that matters** (O-3), at the **power target**, under the horizon embargo; in the same run, a design equal
  to the best baseline on every limit passes every limit check, in the form in force, with at least the power target
  (E-015's condition); and **the count of held-out starts complete over D-145's horizon** reaches its pinned minimum.
  If any fails, **the search goes no further** -- no go row, no survey: CHARTER 3.7's "the search does not pin" read on
  this template's order, the file closed by a row, its k unspent (it is assigned only at a held-out row) -- and exit
  (B) states the line's power from this gate.
- **The data question** (E-007 (2)): more history (QuantConnect's free NQ/ES from 2009, the operator's setup; or older
  bars bought, stated, never authorised) is put to the operator with the power gate's result, before the go row, never
  after a failure.

## 10. The pass line

*CHARTER 3.8. A finalist passes, in its place in the fixed sequence, when (a), (b) and (c) all hold, every deciding
reading the martingale-outcome reading for the finalist and every baseline alike.*

- **(a) Limits.** In force (E-207): the finalist stays inside every operator limit with a margin wider than its noise,
  one margin applied once. Pending (**O-5**): a limit fails only if a one-sided check at the pinned level shows it
  crossed -- computed and reported beside until ruled.
- **(b) Each baseline beaten:** the composite (or the pinned fallback) above **each** baseline's, an
  **intersection-union** test with every comparison at the full level of the search's k, by the calibrated coin-seed
  leg on the held-out years, the time leg's conditions met. Every comparison states the finalist's L and each
  baseline's L.
- **(c) The floors:** verified rules; **conduct tier 1**; CHARTER section 4's constraints, every trade resolving among
  them; hand entry at least L minutes from alert to order; **the zero-edge long-run gate** -- the median log growth of
  the required bankroll over D-145's horizon (Stage 2 D-14) above zero at the pinned lower quantile over **coin seeds
  and history-block resamples** (CHARTER 3.8 (c), unchanged; see O-6), on the martingale-outcome reading, with fees,
  payout latency, the tier-2 consequences and D-145's tier-3 denial applied (the 0 % reading beside), on starts
  complete under the horizon embargo whose count reaches the pinned minimum; **the fill and supply stress** -- at **+1 tick** of worse fills (29) and with
  **10 % of signals missed** (28) the finalist still beats each baseline on the composite at the point estimate,
  both under the same stress, inside every limit in the form in force; **the as-traded floors** for resting triggers
  traded as their real orders -- **the no-harm floor** on the search years, and **the as-traded floor** on the held-out years (the
  finalist's as-traded composite ahead of each baseline's as-walked composite at the point estimate). The no-harm and
  as-traded floors are read on the real path, with no redraw (N-1).
- **The verdict** is read on the martingale-outcome reading, at **0 % payout denial**, the Responsible Trading
  Program's placement off and the **Focused Trader Program off** (E-008 (2); E-007 (3); Stage 2 D-234, D-289). The
  level is printed **nominal** while the held-out read ledger is not empty, and **the history-level false-pass rate**
  is printed beside it.
- **O-6, the long-run gate's history resamples on the held-out years -- the operator's, open.** CHARTER 3.8 (c) reads
  the gate's quantile over coin seeds and history-block resamples, but the held-out years hold only one disjoint
  block of D-145's horizon, so the history part cannot be formed on them (the design note's 4.4). Two options, neither
  chosen here: (a) coin seeds only on the held-out years, with the search years' history-block reading beside; (b)
  the gate read on the search years only, over coin seeds and history-block resamples. Either loosens a floor as the
  charter writes it, so it is the operator's (DIRECTIVE Part 1). No search pins until the operator rules O-6; the
  ruling's row is cited here: <...>.

- **The fixed sequence over finalists** (CHARTER 3.7; E-203 S-1): the ordered finalists are tested by fixed-sequence
  testing, each at the full level of the search's k, stopping at the first failure -- one k for the sequence.

## 11. Beside, never deciding

- The denial ladder; the break-even denial rate (33); the placement on; the binding Focused Trader models.
- P by month; mean net; CVaR10; P under a bankroll limit; the effective sample size (E-007 (e)).
- The frontier over every measure and a menu under the limits; every measure of `docs/MEASURES.md`.
- The as-walked result and the path-structure edge, never credited; the as-traded stress of resting triggers.
- Per component: the share of time-limited trades and the fill-time law reading's gap from the deciding reading
  (section 5, R-10); the share of pairs the pair rule settled.
- The model-side reading, where a playbook uses one; the limit check in O-5's pending form.
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

- **One k per held-out test** at **0.05 / (k (k + 1))**; the fixed sequence over finalists spends one k; the
  confirmation spends none (CHARTER 3.7). The program's numbering continues Stage 2's program U (E-001): **k = 13** is
  the next.
- **k is assigned at the held-out row** (E-204): this search is not counted by the gatekeeper's k rule until that row
  exists. On this template the held-out row comes before the held-out run, so E-204's repeat clause (another
  declaration taking a k between a run and its row) cannot arise; were the order ever reversed, the run is repeated at
  the new level under a repeat row. If another declaration takes a k first, this search's k is the next free one and
  its power is re-stated at the new level before the held-out run (exit (B) cites it). A search withdrawn after its
  held-out row still spends its k (E-005 (d)).
- **Every design tried is counted** in `results/variants.jsonl`: the survey's N, every round's batch, every L, every
  failed-gate design. Written as a product and a number: <survey N + rounds x batch, each at its L values>.
- The program's honesty sentence: <what Stage 2's programs and this repository have read on these bars, and that the
  level is nominal while the ledger is not empty, the decision carried by one confirmation on unread data>.

## 14. The run order -- refusals first

1. **The reads of the draft, before anything is pinned:** the scout's challenger brief (Q-150), the red team, the
   gatekeeper; every blocking finding answered. After the pin a change is a new declaration.
2. **The pin**: after H4 and Wave 4.2's operator inputs are written into section 7, and O-1 and O-6 ruled, the lead's
   row pins **the whole renamed file** by its LF sha256 (the gatekeeper renames and replaces `F-XX` first, then
   hashes). Section 7 is never pinned alone; the calibration's and gate's inputs are inside the frozen file.
   Refusing before it: the identities on record as holding (`identity/stage2_identity.py`, every baseline's runner
   identity, the search runner's own).
3. **The calibration and the power gate** (section 9), each from a **clean checkout** of a named commit
   (`scripts/run_clean.py`) under **run.lock** (one heavy run on the machine, skill `run-lock`); their outputs pinned
   in E-115's form; the data question to the operator.
4. **The go row**: cites this file's one hash and the calibration record's; from here the survey may run. Refusing at
   every later step: this file still hashing to its pin (`tests/test_declarations_fixed.py`), the go row present, a
   clean checkout, the run lock held -- **Refusals first**, each refusing.
5. **The survey** on the search years only (one clean run); its gates before its measures; logged.
6. **The rounds**, each one clean run, collected (`/collect`), never extended.
7. **The finalists' row**: the ordered finalists, their playbooks' rules and every fitted model's hash, citing this
   file's hash, written before any held-out read; the scout's challenger brief and the red team on the finalists.
8. **The held-out row** (k assigned, E-204), citing this file's hash and the finalists' row; then **the held-out
   test**, once, from a clean checkout of that row's commit, in the fixed sequence; the auditor on its result.
9. **The verdict row**; a carried design's registration and the confirmation's criterion declared there.

Each run once, watched to its exit, its file written with its manifest (`extended.results.write_result`, the
declaration's id, the design count, every seed and parameter). A failed check stays on record and is diagnosed by the
failure protocol, never rerun until it passes.

**The held-out reads.** `extended/reader.py` authorises a read of the held-out years for a purpose named on the line
below of the pinned file, from a clean run, once per declaration and purpose; a purpose with a choice or fitting word
(search, fit, select, tune, train) is refused whatever the line says. The reader does not yet tie a read to the run
order or the market, so these rules are the declaration's, binding now, and **Q-158** (queued for wt-verify) is the
guard to come:
- a `heldout_*` read is made **only after the finalists' row and the held-out row**, both citing this file's sha256;
- the held-out years are read **once per market**, across declarations: a re-declared search (a new file, the same
  house line) gets no fresh read; the market's first held-out test spends them (CHARTER 3.6 (c));
- a search that does not spend the market's held-out years carries **no `Judged-block reads:` line** -- delete the
  line below;
- an RD declaration never reads them before the market's verdict row, and no new `registered_design` read of them (of
  P-14, P-15, P-16) is made without a decision row naming it.

*Keep the house names; add a purpose only for a read the held-out test makes, never one that chooses.*

- **Judged-block reads:** `heldout_test`, `heldout_stress`

`heldout_test` reads the finalists and every baseline on the deciding reading, the time leg's groups and regimes, the
long-run gate, and the held-out readings section 11 puts beside: the five-minute cell, the as-walked result and the
path-structure edge, the denial ladder, the model-side reading and the fill-time law. `heldout_stress` reads the
+1 tick and 10 %-missed stresses and the as-traded floor. Nothing else of this search reads the held-out years.

## 15. What a pass and what a fail mean; the confirmation

- **A pass:** the finalist is **carried** -- it takes a registration id, its playbook, the auditor's read; its one
  confirmation is read against **a criterion declared at its registration, before the read** (CHARTER 5 (A)): at least,
  on the martingale-outcome reading, ahead of each baseline on the composite at the point estimate and inside every
  limit in the form in force; at the point estimate, the as-traded floor read on the real path, and ahead of each
  baseline at +1 tick of worse fills.
- **A fail -- what a fail means:** <the search closes; its k is spent; nothing of it is rerun; a new question is a new
  declaration citing this one; exit (B) states the line's power from the power gate>.
- **The confirmation:** NQ from 2026-07-17, read once, only for a carried design; **a purchase**, the operator's.

## 16. Anything chosen after seeing results

*(Empty at the pin. Anything added after a reading is exploratory, reported apart, `exploratory=True` in its manifest,
and recorded in its own decision row -- never added to this file once pinned.)*

---

*Sources: `CHARTER.md` sections 2-5 (E-210); `docs/plans/AMENDMENTS_draft_2026-11-18.md` sections 5-6 (R-10, the
template's fields); `docs/reviews/AMENDMENTS_v3_2026-11-18.md` (m-2, m-3, R-10); `docs/MEASURES.md`;
`docs/plans/LEVER_TABLE_topstep50k.md`; the three-way test's design note (`wt/wt-verify`); E-204, E-207, E-208, E-210,
E-211; the superseded form `prereg/TEMPLATE_family.md`.*
