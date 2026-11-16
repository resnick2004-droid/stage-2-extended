# Operator setup requests

The only channel for the operator's manual tasks (D-453; `docs/HANDOFF_RESET_2026-10-29.md` section 10). Every request
here is copy-paste complete: the operator needs nothing but this file to act. A request leaves the file when its
artefact (a zip's sha256, an account) is recorded in a decision row. Sessions never ask the operator anything that is
not in this file; research questions get a safe default and a status line.

## Open

### 1. ES 1-minute bars from Databento (needed by the handoff's R4 and R5; a payment, the operator's yes required)

Same shape as the NQ purchase on record (2026-10-07, $10.25 for 2020-01 to 2025-06; and the 2026-10-13 top-up):

| field | value |
|---|---|
| dataset | `GLBX.MDP3` |
| schema | `ohlcv-1m` |
| symbology | `parent` |
| symbols | `ES.FUT` |
| date range | `2020-01-01` to the day before the request (UTC) |
| encoding | CSV |
| options | pretty prices, pretty timestamps, symbols mapped |
| delivery | download; leave the zip in `Downloads`, do not rename it |

Expected cost: of the order of the NQ purchase (Databento's checkout shows the exact figure before paying; the
operator decides there). After download, tell any Stage 2 session "ES downloaded": the session records the zip's
sha256 in a decision row, imports only the days inside ES's declared windows (`config/windows.yaml`, R4) and leaves
the rest unread.

### 2. The live feed and account for FV3-C's paper shadow period (Stage 3 step 5; D-399)

The one step between the research and real money. The terminal's `NEXT_STEPS.md` step 5 names what to buy; nothing
in Stage 2 can substitute for it.

### 3. Optional: GitHub Actions is blocked by the account's billing state (no research depends on it)

The first automated test run on GitHub (2026-10-30) was refused before it started: "The job was not started because
recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans'
section in your settings." Private repositories on the free plan normally get a monthly allowance of free minutes;
this message means the account's billing needs attention first. It is a billing setting, so only you can look at it
(github.com, Settings, Billing and plans). If you leave it, nothing breaks: the full test suite runs on this PC
instead (slower, and only when the PC has memory to spare). If you fix it, say "Actions fixed" to any Stage 2 session.

### 5. Optional: two questions for Topstep support (about five minutes, no purchase)

The strongest candidate so far (P-13) closes many funded accounts on request, and its result rests on two rules Topstep's
help centre does not state. Only Topstep can answer them; until then they stay declared assumptions.

Send this to Topstep support (chat or email) and paste the reply into a text file in Downloads named
`topstep_support_reply.txt`:

> Hello. Two questions about Express Funded Accounts: (1) If I ask Support to close an Express Funded Account after
> requesting a payout but before that payout has arrived, is the payout still paid? (2) After an Express Funded Account
> is closed at my request, how soon can a new Express Funded Account be activated in its place -- the same day, the next
> trading day, or later? Thank you.

## Later, not yet

- **CL.FUT and GC.FUT** from Databento, the same request shape, once the ES family has a verdict (handoff R6/R7).
- **The NQ top-up** (2026-07-17 onward) once the shadow period's registered start fixes the reserve's end (D-399 (5)).
- **A Lucid Trading account**, only after a two-firm campaign has a confirmed PASS.

## Not needed

- A QuantConnect paid seat: superseded by local LEAN runs (handoff R12) unless R12 fails its acceptance.
- GitHub: private remotes exist for Stage 2, the Studio, the terminal, the multi-firm repo and marketing (free plan).
  Stage 2B (the literature cache) is backed up by OneDrive only, by the operator's choice.

### 6. NQ 1-minute bars from 2026-07-17 to now, from Databento (P-16's direct confirmation; a payment, the operator's yes required)

P-16 (the 37.5-point coin, D-547) is sized for NQ, so its like-for-like test on data it has never seen is NQ after the
last day already read (2026-07-16). Opening that reserved window is the operator's decision (D-107, `config/windows.yaml`);
this request is that decision plus the purchase. Same shape as the NQ purchase on record (2026-10-07) and item 1:

| field | value |
|---|---|
| dataset | `GLBX.MDP3` |
| schema | `ohlcv-1m` |
| symbology | `parent` |
| symbols | `NQ.FUT` |
| date range | `2026-07-16` to the day before the request (UTC) -- one day early on purpose: trading day 2026-07-17 opens at 17:00 CT on 2026-07-16 (22:00 UTC); the session imports only bars after the development window's last bar and checks the overlap against the store, never rewriting a development day (D-606) |
| encoding | CSV |
| options | pretty prices, pretty timestamps, symbols mapped |
| delivery | download; leave the zip in `Downloads`, do not rename it |

Expected cost: a few dollars (under four months of one symbol; Databento's checkout shows the exact figure before
paying). After download, say "NQ top-up downloaded" to any Stage 2 session: the session records the zip's sha256 in a
decision row, declares the window a confirmation window, and leaves it unread until P-16's confirmation is registered.
ES (item 1) is the separate, longer test of whether the coin carries to another market, with its stop translated by
a rule declared before any ES bar is read.

**On timing (D-604):** on P-16's own history even a three-month window cleared the growth line, but longer windows
narrow the bound; six months or more of NQ after 2026-07-16 (from about mid-January 2027) is the safer single test.
Buying earlier is fine -- the window stays unread until the confirmation is registered -- but the session will
recommend registering it on at least six months.

### 7. DONE 2026-11-14 (D-645) -- Allow the rules re-read to be applied (one sentence in chat; no purchase)

**Done:** the operator gave the word in chat; the patch is applied, the stop band's rows are unchanged and its
manifest refreshed (D-645). Nothing below is asked any more; it is kept as the record of the request.

On 2026-11-14 the rules-verifier re-read 28 Topstep rules on the official help centre and found every value
unchanged; it also verified new rows (the payout path chosen at activation, the $100K and $150K account values,
trading hours). Its edits are saved, not applied: `docs/rules/pending/rules_reread_2026-11-14.patch` (D-622,
D-623). Applying them changes `config/rules.yaml`, and a test then requires `results/stop_band.csv` to be
regenerated with `python scripts/stop_band.py`. Its rows do not change -- only its manifest's record of the
inputs -- but that rewrites a result file, which the autonomous program may not do on its own.

To allow it, write this in the Stage 2 chat:

> Apply the rules re-read and refresh the stop band's manifest.

Until then the program runs on the rules already on file (their values are the same). Two lever families wait
on it: the Consistency path by choice, and account sizes above $50K.
