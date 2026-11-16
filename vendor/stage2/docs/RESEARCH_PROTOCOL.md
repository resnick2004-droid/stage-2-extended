# Research protocol (D-155)

Every new model goes through these eight steps, in this order, after the step-0 door D-191 added in front of them
from P-05. The operator agreed it on 2026-09-26. Each step
leaves a file behind, and each can end the model; a model that stops is a result, recorded, not a failure to hide.
Steps 1-4 fit on one page, the **model card** (`prereg/MODEL_CARD_TEMPLATE.md` → `docs/candidates/cards/<id>.md`),
written before any QuantConnect kit exists.

| step | what | leaves behind | enforced by | stops the model when |
|---|---|---|---|---|
| 0. Candidate record (D-191) | a replicated atlas row with its result file; a mechanism grade A-D; the prop-fit score, computed (D-154 met pooled and in three of every four markets on their own, the zero-micro share at most 25 % in every state, all three conduct tiers); the screen's k; the model's row in the trial ledger `prereg/models.yaml`, naming the pool it was chosen from (D-197) | the card's step-0 fields; a ledger row | `validate_card` (from P-05; IM1 and IM2 are pre-door entries); `propedge.research.ledger` | no replicated row, or the prop-fit score fails |
| 1. Hypothesis | what should make money, why it should exist, who pays; edge, contract shape or both | card §1 | `validate_card` | there is no mechanism or outside prior, only a pattern in our data |
| 2. Contract fit | sizes per lifecycle state from stage one; setups per day against D-154; copier or rotation; conduct tiers; from D-212 the trading window inside Topstep's 17:00-15:10 CT, no time stop, whole-micro risk within 10 % of each state's on 90 % of the screen's trades, and at most 5 % of them reaching the 15:10 flatten overall, per market and per year (D-308; 2 % before 2026-10-06); from D-266 the execution declaration -- manual, the latency L from the signal to a working order (at least the operator's 5 minutes), a resting entry's missed-trigger policy (skip, rest or chase), the operator's hours; from D-271 the sizes met by stop widths drawn from today's regime, and a model with several entries a day declaring its account coordination (D-269) | card §2, the card's machine-checked rows and its "Eras and today's economics" section | `validate_card` (the D-154 check reads `results/setups_per_day.csv`; the D-266 declaration and the D-271 section from ORB5 on, `PRE_D266` and `PRE_D271` naming the six cards written before them); `conduct.py` | a tier-1 conflict; too few setups a day for its size; uneven risk or trades that run to the flatten (D-212); no execution declaration, a latency below the operator's, or a resting entry with no missed-trigger policy (D-266) |
| 3. Cheap screen | the idea checked on data already on hand, against a kill line written first; from D-271 behaviour in R on every year -- gross R and net R at today's cost in R side by side, no era's costs, the per-era figures (2009-2017 and 2018 on) beside the pooled ones | card §3, a result file | `validate_card` (`screen_verdict`) | the screen says kill |
| 4. Pre-registration | the rules, every parameter fixed, searched or dropped, `k`, the development period, the D-145 gate as the pass line, the seed; from P-05 the required and available trades read from the L5 power curve (D-192) and the trial count N the bound is widened by (D-189); from D-266 the missed-trigger policy fixed before any run and the results to be reported at L = 0 and at L; from D-271 the era rule with its bootstrap seed, the stand-aside floor that defines today's regime, and the drift-matched baseline; from D-663 the four validation readings step 7 reports beside the verdict, each with its levels fixed here -- the gate row under block-resampled days (mean block 5, 21 and 63 sessions), the bound's coverage, the break-even e with its margin, and the missed-trade stress | `prereg/P-XX_*.md`, registered | the prereg-gatekeeper and `validate_prereg`, which refuse a model's pre-registration without a passing card | the gatekeeper refuses it |
| 5. QuantConnect run | the kit, locked to the development dates, with audit prices and each trade's maximum adverse excursion (D-156); the operator runs it and downloads | `runs/<id>/`, `results/manual_*.csv` | the embedded date guard; ingestion refuses code that is not the committed kit; `trade_audit.missing_fields` | — |
| 6. Verification | data integrity; every trade audited against the rules; a chart review of a seeded sample (D-148) | `results/trade_audit_*.csv`, `docs/reviews/` | the audit and the review sheet | any rule violation (a defect, diagnosed under the failure protocol) |
| 7. Prop environment | the pre-registered run goes through the lockstep engine (`propedge.campaign.lockstep`) via the registered harness, with the D-145 gate and copier against rotation as declared arms; ruin, payout latency and drawdown beside growth; the variant count; from D-271 money only under today's economics -- each R outcome paired with a stop width drawn (seeded) from today's regime's stops, the lower era bound when the eras are flagged; from D-269 each coordination option's added trades reported apart; from D-663, beside the gate row and never a verdict line: the same row with each path's days block-resampled (the stationary bootstrap, `run_gate`'s `mean_block`, at mean block 5, 21 and 63 sessions) with the required bankroll under each, the coverage of the bound of e at its registered level on block-resampled histories, the break-even e (the shift below the registered bound at which growth on the required bankroll reaches zero) with its margin, and the campaign with offered trades and whole sessions missed | result files with manifests | `propedge.campaign.gate.run_gate`, the harness | — |
| 8. Verdict | read from step 7's result files against the pass line set in step 4; from D-266 the verdict is the one at L, with L = 0 beside it; from D-271 the per-era figures beside the pooled ones and the part of e that drift alone explains; a pass earns one confirmation run on the held-back window (2025-07-01 on, D-237; 2020 on before it, D-144), once, never re-tuned; from D-663 the four validation readings are stated beside the verdict and never decide it until the operator rules otherwise (the gate is the operator's, D-145) | the pre-registration's outcome, a `DECISIONS.md` entry | the registry; the failure protocol | the gate fails (at L; at the lower era bound when the eras are flagged); the confirmation fails |

## Rules that hold at every step

- **Anything chosen after seeing results is exploratory**, labelled so in its manifest and reported separately. A
  corrected model is a new card with its own variant count, never an edit to the old one (D-148).
- **Validation gates test a frozen candidate; they are never tuning signals (D-277).** No parameter optimisation is
  permitted after observing the result of a validation gate unless that optimisation was explicitly authorised as
  part of the current search stage; any post-gate optimisation creates a new candidate that must restart the
  validation sequence. A search optimises only inside its declared, bounded space on the data the stage permits,
  then freezes; its gates (the walk-forward continuation gate W1, then W2, B and G, then the held-back
  confirmation) are passed in order. W1 failing invalidates the execution model and closes its branch; a later
  gate failing closes that specification; the confirmation failing closes it; all passing lets it move to
  execution, paper or live testing. A closure binds the defined hypothesis and specification, not the market or
  the strategy family: a genuinely different hypothesis may be researched later, but a closed specification is
  never resurrected by a new parameter combination.
- **A failed check is kept on record and diagnosed** (terminal states → stage decomposition → component in isolation →
  replication with seeds fixed first), never rerun until it passes.
- **Numbers come from result files with manifests**; nothing is typed into a document.
- **A verdict is cited only when it is citable** (D-185, D-195, D-202): its chart review recorded and passed after
  it, and the test layers L3 (`results/l3_lookahead_canary.csv`) and L5 (`results/l5_planted_effect.csv`) passed
  against the engine files its manifest pins. The trace check refuses a number from, or a document naming, a
  verdict that is not. Rerun `scripts/l3_lookahead_canary.py` and `scripts/l5_planted_effect.py` after any change to
  an engine file.
- **Sizes start from stage one's contract results** (`vendor/propsim/edge/T5_RESULTS.md` §2a; D-114): the strategy is
  sized to the contract, never the contract bent to the strategy.
- **The Studio (Stage 2C) is the inspection view** for step 7's run and for exploratory what-ifs. Its own runs are
  exploratory, never a verdict or a source for a number in a document.
- **Every campaign result states its settlement** (D-156): `mae` (exact), `pessimistic` (a log without MAE: the lower
  bound) or `legacy` (pre-D-156 only, the upper bound). A verdict from a pessimistic run that passes stands; one that
  fails is read beside the model's MAE-settled run before it is final.
- **The gate resamples single days independently; its dependence on that is reported, not assumed away (D-663).** `gate.run_gate` gives each calendar day of a path one historical day drawn independently with replacement, so a
  path keeps nothing of the order of history's days. Every verdict from D-663 carries, beside it, the gate row with
  the days drawn in blocks (`mean_block`; `shared_days.StationaryDayTable`), the bound's coverage, the break-even e
  and the missed-trade stress (steps 4, 7 and 8). They are read beside the verdict, never as a verdict line, until
  the operator rules otherwise.
- **Hypothetical studies of prohibited patterns** (D-153) are not models and do not enter this protocol.

## Screening rules (D-201)

- **One mechanism plus at most one filter per screen.** A second filter is a second screen.
- **The feature-level k counts every filter tried**, kept or not, and enters D-189's N through the ledger (D-197).
- **Candidates are ranked by the lower bound of the edge at the family's Combine R**, subject to D-154's setups per
  day: every candidate passes through the Combine first.
- **One candidate at a time**: the next is not registered until the current one has its step-8 development verdict.
- **Every screen and verdict prints the break-even hit rate** per market and R beside the edge (the cost drag c, p* =
  (1 + c) / (1 + r), the target-hit rate with its lower bound, the time exits' share and mean R); the gate's edge
  test is unchanged.

## Execution by hand (D-266)

The operator trades every signal by hand ("this won't be automated"), so for every card written from D-266 on,
ORB5's the first (IM1, IM2, NQB1, NQB2 and the ORB2 and ORB3 drafts pre-date it, `PRE_D266`):

- **The card declares its execution** (step 2, `validate_card`): `manual`; the latency L in minutes from the signal to
  a working order, at least the operator's 5 -- every model is scored at the operator's latency, so a card may
  declare more, never less; and the hours, `unconstrained` (the operator's: no hours constraint) or a window that
  holds the model's trading window. An order is modelled working only from the signal + L; with rotation one account
  takes each signal, so L is per signal.
- **What a missed trigger does is declared before any run** (steps 2 and 4): a resting stop or limit entry's trigger
  before the order works is skipped, left resting at its level until it next trades through, or chased at the market,
  where the spread is its cost. ORB5's capture (R105-R107) scores all three at L = 5 and only skip at other latencies.
- **Results are reported at L = 0 and at L; the verdict is the one at L** (steps 7 and 8). Every test before D-266
  assumed L = 0, which overstates what can be traded by hand.

## The eras and today's economics (D-271)

Behaviour is estimated in R on every year, money only under today's tick economics, and the eras are tested, not
assumed, to be one population. For every model from ORB5 on, fixed before any of its data is read and stated in the
card's "Eras and today's economics" section (`validate_card` checks each rule is stated, never its numbers; `PRE_D271`
names the six cards written before it):

- **The per-era report and its rule** (steps 3, 4 and 8): beside the pooled figures, e, its one-sided 95 % lower
  bound, the skew of R per trade, the median time to the stop and the share still open at 15:08, for 2009-2017 and
  2018 on separately. The eras are flagged as different when the 95 % interval of the difference in their mean gross
  R, from a bootstrap that resamples whole years (its seed fixed in the pre-registration), excludes zero; when flagged,
  the money steps use the lower of the two eras' bounds, never the pooled one.
- **No era's costs in the behaviour step** (step 3): gross R and net R at today's cost in R side by side -- ORB3's
  measure (D-257), now the rule for every model; era-specific costs enter only the money steps, which are today's.
- **"Today" is a regime, defined by the stop** (steps 2 and 7): a day belongs to today's economics when its stop in
  ticks is at least the stand-aside floor (45 MNQ ticks unless T16 item 2(c) fixes another), so the definition
  survives a change in NQ's range; the behaviour step can condition on it, the money steps inherit it, and that old
  days clearing the floor are the old era's volatile days -- a selected sample -- is reported with them.
- **Sizing draws a distribution** (steps 2 and 7): in the contract fit and the campaign each R outcome is paired with a
  stop width drawn (seeded) from today's regime's own stops -- the 2020 to June 2025 days at or above the floor -- so
  the day-to-day spread of realised risk, and the cap it meets, reaches the money numbers.
- **The baseline controls for the market's drift** (steps 3 and 8): the no-skill baseline (D-246's random entries) is
  rebuilt with the model's own long/short share and entry times, year by year, and the part of e that drift alone
  explains is reported -- random directions at 50/50 would credit a long-leaning model with NQ's rise.
- **Volume and depth** at the entry and flatten minutes are taken up by the simulator-fill capture for a configuration
  that clears the walk-forward (D-263). The Studio's replays stay views: a plain replay is shown on 2020 on, and
  campaign numbers come from today's regime and its stop widths.
- **Account coordination (D-269)**, where a model has several entries a day (step 2, declared before the run): one
  position at a time (D-160, the rule for every model but ORB5), or ORB5's option beside it -- each entry to its own
  free account, direction-locked, so no account is ever opposite another (tier 1, D-145) and none carries a copy
  (D-157). For each option the trades it adds over one position at a time are reported apart -- their own e, its
  bound and their costs -- the options ranked by time-aware return at the bound of e (step 7), with the tier-2
  consequence of several accounts at the MLL in one day applied.

## What the steps cost

Steps 1-3 cost nothing but thought and data already on hand, and most ideas should end there: the VIX check stopped
an options-data trial (`results/bmap_vix_check.csv`), and arithmetic settled the hedging question (D-153). Steps 5-8
cost the operator's QuantConnect time and the data caps, so they are spent only on a model that survived 1-4.
