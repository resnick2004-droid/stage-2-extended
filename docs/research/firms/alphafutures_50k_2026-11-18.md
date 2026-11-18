# Alpha Futures $50K -- the firm's terms (Q-135c, E-196): NOT READ, blocked by the standing E-020 (2)

| field | value |
|---|---|
| task | Q-135c (E-196): read-only terms research, Alpha Futures (alpha-futures.com), $50K accounts only |
| author | scout (read-only), session of 2026-11-17 (the machine's date; the brief's path carries 2026-11-18, E-196's date, and is kept) |
| pages of alpha-futures.com fetched by this scout | **none** |
| status of every Alpha term below | **NOT READ** -- nothing here is evidence of a rule; nothing is usable by code |

## The question

What does Alpha Futures sell at $50K now (every evaluation path and any instant- or direct-funded product), with the
evaluation and the funded account read separately: costs, drawdown and limits, size, consistency, payouts, conduct,
new releases in the last six months, flip days, and the fit of each account type to the engine against Topstep's $50K
reference (RD-01 section 4.1)?

## The answer, in a few sentences

**This scout did not read Alpha Futures' pages, because a standing decision of this repository forbids it.** The brief
says the firm "has no record in the repository yet"; it has one. Q-12's survey (E-009) found that **Alpha Futures' own
terms forbid automated retrieval** -- "any automated use of the system, such as ... web scraping robots"
(`docs/research/firms_survey_2026-11-15.md:84`; `docs/research/firms_2026-11-15/firms/alpha.json`) -- and **E-020 (2)**
decided that for the eight firms with such clauses, Alpha among them, the material automated readers collected is
struck, and "their plans are read, if ever, only through the operator's own browser or with the firm's written
permission" (`DECISIONS.md:27`). E-196, which dispatched this task, does not mention or revise E-020 (2)
(`DECISIONS.md:203`), and an agent's brief cannot itself set the firm's terms aside. Fetching the firm's site with
WebFetch or curl is "automated use" on the clause's plain words, so this note does not fetch it -- not even the terms
page to re-confirm the clause, since that is also an automated read of the same site. Search-engine snippets of the
firm's pages would be a way round the clause, and are third-party material anyway, so they were not used either.

What this note does instead: (1) it lists, in **"Pages for the lead's browser"**, every page whose reading would answer
the brief, with what each must give (the lead's instruction of this session); (2) it sets out the **checklist** the
browser reading must fill, one table per account type, with the survey's struck-era *unquoted* readings beside each term
as **things to check, never as values**; (3) it gives the **engine fit** as conditional statements -- "if the page says
X, the engine needs Y" -- against Topstep's verified $50K values.

**One caution for the lead (a decision that is the lead's, not mine):** E-020 (2) names *the operator's own browser*.
If "the lead will open those in the operator's browser" means an agent driving that browser (a browser-automation
tool), that is still "automated use of the system" on the clause's words; the clean routes are the operator reading the
pages by hand (an `OPERATOR_SETUP.md` item: a page list and the fields to copy), or the firm's written permission (a
support e-mail from the operator -- which would send personal information, so it is the operator's to send, never an
agent's).

## Evidence (all of it from this repository; none from the firm)

| # | what | source |
|---|---|---|
| 1 | Alpha Futures' terms forbid automated retrieval: "any automated use of the system, such as ... web scraping robots" | `docs/research/firms_survey_2026-11-15.md:84` (recorded under E-009, 2026-11-15); `docs/research/firms_2026-11-15/firms/alpha.json` (the stub, dated 2026-11-16) |
| 2 | sites whose terms forbid automated retrieval "are not re-read by any automated reader" | `DECISIONS.md:16` (E-009, 2026-11-15) |
| 3 | the material struck; Alpha's plans read "if ever, only through the operator's own browser or with the firm's written permission" | `DECISIONS.md:27` (E-020 (2), 2026-11-16); `docs/research/firms_survey_2026-11-15.md:9-14`, `:709-711` |
| 4 | `docs/RULES_CURRENCY.md:16-19`: "Firms whose own terms forbid automated retrieval are not read by any automated reader, and their rules are not recorded here ... Reading them needs the operator's browser (Stage 2 D-574's pattern) or the firm's written permission." | repository |
| 5 | `config/rules_extended.yaml:345`: "SKIPPED, not read today: The Trading Pit and Alpha Futures (E-009's list)" (Q-26) | repository |
| 6 | E-196 (the operator's direction to model Alpha Futures, My Funded Futures, Lucid and Topstep at $50K) says "public pages only -- no account, login, form or purchase", and nothing about E-020 (2) | `DECISIONS.md:203` |
| 7 | Topstep $50K reference values used in the engine-fit section | `vendor/stage2/config/rules.yaml` lines given in that section; RD-01 section 4 (`prereg/RD-01_firm_contracts.md:220-249`) |

The firm's identity ("the futures prop firm, from its own site") could not be confirmed, for the same reason.

## Pages for the lead's browser

The addresses below are **not verified** -- this scout has not loaded the site and the repository records no Alpha URL
(the survey's page list was struck). The reader should start at the home page and follow the site's own navigation;
each row says what the page must give. Record for each: the exact URL, the article id if any, the page's own date, the
read date, and the sentences verbatim.

| # | page (start from the site's own links) | what is needed from it |
|---|---|---|
| B-1 | `https://alpha-futures.com/` (home page) and its plan or pricing picker | that it is the futures prop firm; every $50K product sold now (each evaluation path; any instant/direct-funded product); each price, and whether it is monthly or one-time, with any sale or coupon shown and its end date |
| B-2 | the firm's Terms and Conditions (and any General Service Agreement and Schedules 1-2, which the survey cited) | the automated-retrieval clause re-read verbatim with its number (it decides whether anything can ever be automated); the schedule rows for each $50K account (target, MLL, consistency, minimum days, split, seats); the conduct clauses (prohibited strategies, risk-at-evaluation-level, hedging, copying, account limits); which document governs when pages conflict |
| B-3 | the help centre's home and its article on the **Standard** $50K evaluation and its funded (Qualified) account | every term of the Standard checklist below |
| B-4 | the help centre's article(s) on the **Advanced** $50K evaluation and its funded account | every term of the Advanced checklist below |
| B-5 | any help-centre article on an **instant / direct funded** $50K product, if one is sold | its price, drawdown, consistency, payout and seat terms |
| B-6 | the help centre's drawdown article(s) (maximum loss limit) | its type (intraday trailing, end-of-day trailing, static); when and at what balance it locks; whether a breach is checked intraday; what a payout does to it |
| B-7 | the help centre's daily-loss-limit article, if any | the amount per account type; liquidate-and-pause or fail; from which balance it is measured |
| B-8 | the help centre's consistency article(s) | the exact rule for the evaluation and for the funded account of each type; the denominator (total profit, profit since the last payout, gross); which days count (losing days, the request day); what a breach does (fail, raised target, payout refused, profit deducted) |
| B-9 | the help centre's payout article(s) | buffer before the first payout; winning-day size and count; split and its schedule; minimum, maximum and caps; frequency; processing time and fees; the floor after a payout; the count before a live move |
| B-10 | the help centre's live-account / "live transition" article | the path from funded to live, and whether the move closes the household's other sim accounts (the survey listed Alpha among firms whose live move does) |
| B-11 | the help centre's position-size / scaling-plan article | maximum contracts per account type, how micros count against minis, the scaling plan by balance in the funded account |
| B-12 | the help centre's account-limit article | accounts per person and household, evaluations and funded separately, by type (the survey found the pages conflicting: 5 or 3) |
| B-13 | the help centre's news-trading article | the window (the survey read "±2 min red-folder" on the Standard funded account), which releases, which account types, what a breach does |
| B-14 | the help centre's prohibited-strategies / conduct article(s) | hedging within and across accounts and firms; copy trading and trade copiers on one's own accounts; scalping thresholds (the survey read "< 10 ticks / < 2 min"); "tight-bracket" or sim-fill exploitation; account rolling or stacking; an "all-or-nothing" rule; bots and automation; holding over the close and the weekend; flat time |
| B-15 | the site's announcements / blog / changelog for 2026-05-17 to now | every account model announced or changed in the last six months with its date (the survey read: Standard relaunched 27 July 2026; Premium discontinued, a 15 Sept 2026 post; an operational payout update around July 2026) |
| B-16 | the data-fee and platform pages | data fees in evaluation and funded; platform (and whether a platform licence is extra) |
| B-17 | any commissions page | per-side or round-turn fees for MNQ and NQ in the evaluation and the funded account, and whether exchange and NFA fees are included (for RD-01 section 4.8's cost rule) |

## The checklist, one table per account type

Every row is **NOT READ (E-020 (2))**; read date: none. The middle column is the Q-12 survey's unquoted reading of
2026-11-15, kept by E-020 "as a scout's reading only" (`docs/research/firms_survey_2026-11-15.md:13`) -- a pointer to
what to look for, never a value. "--" means the survey has nothing.

### Standard 50K -- evaluation

| term | survey's struck-era reading (to check, not evidence) | source of the pointer | status |
|---|---|---|---|
| fee, billing | $129, monthly | survey `:299` | NOT READ |
| reset, activation, data fees | activation 0 in the survey's arithmetic | survey `:299` | NOT READ |
| profit target | $3,000 | survey `:299` | NOT READ |
| maximum loss, type, lock | $2,000, end-of-day trailing, stops at start | survey `:124`, `:299` | NOT READ |
| daily loss limit | -- | -- | NOT READ |
| minimum days, time limit | -- (the T&C's 3-vs-2 conflict was about Advanced) | survey `:201` | NOT READ |
| maximum contracts, micro counting | -- | -- | NOT READ |
| consistency (rule, days, breach) | 50 % | survey `:124` | NOT READ |

### Standard 50K -- funded (Qualified)

| term | survey's reading (to check) | source of the pointer | status |
|---|---|---|---|
| activation, monthly fee | -- | -- | NOT READ |
| maximum loss, type, lock; after a payout | $2,000 end-of-day trailing, stops at start | survey `:124`, `:299` | NOT READ |
| daily loss limit | -- | -- | NOT READ |
| scaling plan by balance | -- | -- | NOT READ |
| consistency | **40 %** (a funded rule) | survey `:124`, `:346`, `:367` | NOT READ |
| buffer, winning days, frequency | -- | -- | NOT READ |
| split | 90 % from the start (an older agreement shows 70/80/90) | survey `:203`, `:299` | NOT READ |
| minimum, maximum, caps | per-payout ceiling 1,800 in the survey's arithmetic (that is 90 % of a $2,000 term; the cap itself not given) | survey `:299` | NOT READ |
| processing, payout fee | 3 days (T&C) vs <= 5 (an operational update); the fee unverified | survey `:158`, `:204` | NOT READ |
| live path | a live move that closes the household's sim accounts | survey `:464` | NOT READ |
| news | ±2 min red-folder | survey `:124`, `:443` | NOT READ |
| seats | 5 (pages conflicting with 3) | survey `:124`, `:205` | NOT READ |

### Advanced 50K -- evaluation

| term | survey's reading (to check) | source of the pointer | status |
|---|---|---|---|
| fee, billing | $209, monthly | survey `:315` | NOT READ |
| profit target | **$4,000** | survey `:35`, `:315` | NOT READ |
| maximum loss, type, lock | **$1,750**, end-of-day trailing, stops at start | survey `:35`, `:124`, `:315` | NOT READ |
| minimum days | 3 (T&C 8.1.9) vs 2 (T&C Schedule 1) | survey `:201` | NOT READ |
| consistency | 40 % | survey `:124` | NOT READ |
| daily loss limit, contracts, reset | -- | -- | NOT READ |

### Advanced 50K -- funded (Qualified)

| term | survey's reading (to check) | source of the pointer | status |
|---|---|---|---|
| maximum loss | $1,750 (product cards) vs 4 % = $2,000 (T&C Schedule 2) | survey `:202` | NOT READ |
| consistency | none | survey `:124` | NOT READ |
| split | 90 % | survey `:203`, `:315` | NOT READ |
| seats | 3 per household (a product-page FAQ says 5) | survey `:199`, `:205` | NOT READ |
| copying across one's own accounts | permitted by a help article, conflicting T&C wording | survey `:200`, `:206` | NOT READ |
| buffer, winning days, caps, frequency, scaling, news, live path | -- | -- | NOT READ |

### Premium 50K

Discontinued, on the survey's reading of a 15 Sept 2026 post (survey `:204`, `:260`). To confirm (B-15); not modelled.

### Instant- or direct-funded 50K

Unknown: the survey's record names none. To check (B-1, B-5).

### Firm-level conduct (every account type)

| term | survey's reading (to check) | status |
|---|---|---|
| automation | bots banned; hand entry fine (survey `:124`) | NOT READ |
| scalping | < 10 ticks and < 2 min banned (survey `:124`, `:456`) | NOT READ |
| sim-fill exploitation | "tight-bracket" fill exploitation banned (survey `:124`) | NOT READ |
| account rolling / stacking | banned (survey `:124`, `:459`) | NOT READ |
| an "all-or-nothing" rule | named, not described (survey `:124`) | NOT READ |
| position sizing | T&C 1.3.2: risk kept at the evaluation level (survey `:124`, `:462`) | NOT READ |
| hedging across accounts and firms; overnight and weekend holding; flat time | -- | NOT READ |

## Flip days -- what decides them, and what the reading must find

Whether the evaluation can be passed in one or two large days, and whether the funded account's first payout can come
from one or two, is decided by four facts per account type, all NOT READ:

1. **the evaluation's consistency rule and its form**: a share s with the engine's form `max(target, best day / s)`
   (Topstep's, `vendor/stage2/config/rules.yaml:80-81`, s = 0.55) never fails a big day but makes the pass need at
   least ceil(1/s) profitable days' worth of total profit; s = 0.50 would allow a pass in **two** days, s = 0.40 in
   **three**; a share read as a *fail* or as *profit deducted* would change that, and so would a rule over gross profit;
2. **the minimum trading days** (a floor independent of the share; Advanced's 3-vs-2 conflict matters here);
3. **for the first payout**: the funded consistency rule's denominator and which days count, the winning-day size and
   count, and the buffer -- a 40 % funded rule (Standard, on the survey's reading) with five winning days would make a
   one- or two-day first payout impossible; Advanced with no funded rule would leave only the day count;
4. **conduct text** that can reach a large day: T&C 1.3.2 (risk at the evaluation level) and the "all-or-nothing"
   rule, either of which could make a deliberate flip day a breach regardless of the arithmetic.

## Engine fit, conditional on what the reading finds

Topstep's reference (RD-01 4.1; `vendor/stage2/config/rules.yaml`): target $3,000 (`:28-29`), $2,000 end-of-day trailing
drawdown locking at the start (`:54-55`, `:121-122`), consistency share 0.55 (`:80-81`), 5 contracts in the evaluation
(`:136-137`), funded floor -$2,000 locking at 0 (`:211-212`, `:231-232`), five winning days of $150 (`:255-256`,
`:286-287`), cap $2,000 and 50 % of balance (`:304-305`, `:414-415`), minimum $125 (`:400-401`), split 90 % (`:432-433`),
$49 every 21 sessions (`:466-467`, `:498-499`), activation $149 (`:551-552`), five seats (`:637-638`), ladder
`0:2,1500:3,2000:5` (`:950-951`). The engine's evaluation and funded mechanics are those listed at RD-01 `:222-235`.

| if Alpha's page says (survey pointer) | the engine | needs |
|---|---|---|
| target, end-of-day trailing drawdown, lock at start (both types) | `CombineAccount` / `FundedAccount` fields | field only |
| Advanced: $4,000 / $1,750 | fields; the funded floor's $1,750-vs-$2,000 conflict needs one reading per end (RD-01 section 5's form) | field; two readings until settled |
| evaluation consistency as a raised target | the engine's own `max(target, best / s)` | field (s) |
| evaluation consistency as a fail or as profit deducted | not representable | a `CombineAccount` subclass (A-2's pattern) |
| a minimum-days count beyond the share's | not representable (the engine counts live sessions, RD-01 A-4) | A-4's pattern |
| Standard funded consistency 40 % | not representable (Topstep's Standard path has none) | a `FundedAccount` subclass (A-3 / A-5's pattern), with the denominator and the counted days as read |
| monthly billing | `subscription_fee` every `billing_days` | field |
| split 90 % flat | field | field; a 70/80/90 schedule would need a split-by-count adapter |
| a live move closing every sim account in the household | `household_closure` seam (Lucid's `HOUSEHOLD_CLOSES_AT_LIVE`, RD-01 `:266`) | field via the seam, if the count before the move is read |
| ±2 min news window on the funded account | no calendar exit in the engine | a count (as TradeDay's G-3) and, if positions are force-closed, a bracket (A-11's pattern); the gate cannot place it |
| scalping, tight-bracket, rolling, all-or-nothing, risk-at-evaluation-level | not modelled | counts (RD-01 9.3's form) or gaps priced by the denial ladder; T&C 1.3.2 could reach the state table's funded sizing (as E-012 found for Topstep) -- a written question |
| 3 seats (Advanced) | `max_active_funded_accounts` | field |

Nothing in this table is a finding about Alpha; each row is a conditional for the reader of the pages.

## What is unknown, and how it could be found

Everything about Alpha's current $50K terms is unknown to this repository in verified form. It can be found only by
(a) the operator reading the pages of B-1 to B-17 by hand and copying the sentences, URLs, ids and dates into a file
the rules-verifier then records (Stage 2 D-574's pattern; an `OPERATOR_SETUP.md` item), or (b) the firm's written
permission for an automated reader, which only the operator can request. Whether the clause still stands is itself
unknown (last recorded 2026-11-15); re-reading it is B-2's first line.

## What could not be verified

- the firm's identity on its own site;
- whether the automated-retrieval clause is still in the current terms, and its clause number;
- every term in every table above, for every account type;
- the existence of any instant- or direct-funded $50K product;
- every release or change in the last six months (the survey's three dated pointers included);
- the exact URLs of every page in "Pages for the lead's browser".

## Proposed decision row (one finished line)

| E-NNN | 2026-11-18 | **Q-135c (Alpha Futures $50K) not read: the standing E-020 (2) bars any automated reader from Alpha's site** (its terms: "any automated use of the system, such as ... web scraping robots", E-009), and E-196 did not revise it; the scout fetched no Alpha page and recorded no term. `docs/research/firms/alphafutures_50k_2026-11-18.md` lists the 17 pages that would answer E-196's questions, the checklist per account type (Standard and Advanced, evaluation and funded; Premium reported discontinued; any instant product unknown), the flip-day facts, and the engine fit as conditionals. **Decided (the lead):** Alpha's terms are read only by the operator by hand (an `OPERATOR_SETUP.md` item carrying the note's page list and fields) or with the firm's written permission; an agent-driven browser is an automated reader under the clause and is not used; until then Alpha is carried in E-196 as **unread**, with no contract, no zero-edge map and no sizing grid. | Brief Q-135c; its hand-back; E-009, E-020, E-196; Stage 2 D-574. |
