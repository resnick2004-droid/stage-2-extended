# Success criteria — the single source (R1, D-457)

What decides a candidate, what is read beside the verdict and never decides it, and what is reported with a FLAG
level. This file replaces the scattered statements in D-145, D-189, D-230, D-234, D-289, D-304/305, D-312, D-337,
D-355, D-398, D-400, D-419, D-439 and `docs/DEPLOYMENT_PROTOCOL.md` **for every registration from D-457 on**; where
an older row or document reads differently, this file governs and the older text stays on record as written
(`DECISIONS.md` is append-only). Registrations already run keep the lines they were registered with: P-06's PASS
and P-10's FAIL stand exactly as recorded (D-361, D-450).

No result number is typed here. Every level that depends on data is computed into a result file with a manifest
and named below by file and column; `/trace` checks the documents that print them.

---

## 1. The gate — decides a candidate (D-145 as amended)

**Metric: growth on the required bankroll.** The median path's growth on the bankroll the run itself required:
`pf_growth_on_base_p50`, read on `pf_required_p90` (the 90th percentile across the run's paths of each path's deepest
loss from the start plus one Combine subscription, D-312, D-319). The bankroll is an output of the run, never a
preset figure (D-312). `median_log_growth` is the engine's notional-bankroll column (D-451 F4): reported, never the
gate, and never compared with the metric above.

**The gate row** of a campaign result file: section `gate`, `shift` = `lower_bound`, `enforcement_p` = 0,
`placement` = off — the first row the verdict scripts mark `is_gate_row`:

- each R's trade outcomes shifted down so their mean equals the one-sided 95 % lower bound of `e` over 21-session
  blocks (D-237 (4));
- fees and payout latency applied; the Standard payout path;
- the Responsible Trading Program's placement **off** (D-289, the operator) and contracts at the full verified
  allowance;
- payout denial at **0 %** (D-234, the operator).

**The gate passes** when the gate row's growth on the required bankroll is above zero, at the confidence level §2
sets for the kind of verdict.

## 2. The verdict's confidence level — the 0.05/N sentence (D-189, D-230, D-419)

> **A development verdict is read at `e`'s one-sided bound at 0.05/N, N the trial ledger's count for the candidate's
> pool (`prereg/models.yaml`, `count_n`); a confirmation — one configuration fixed in advance, read once on a window
> that played no part in choosing it — is read at the registered one-sided 0.05, with the bound at 0.05/N reported
> beside it, never as the verdict.**

So, on development data (D-419):

| verdict | when |
|---|---|
| **PASS** | the gate grows at the 0.05/N bound and the resolution lines of §3 hold |
| **CONTINUE** (exploratory, not a pass) | the gate grows at the 0.05 bound only; one confirmation on unread data decides it — "the confirmation window carries the decision, never a smaller N" (D-189) |
| **FAIL** | the gate does not grow at the 0.05 bound, or a resolution line fails |

A family pre-registration (the handoff's §7 item 3) counts its whole grid in N.

## 3. Lines every verdict carries

**Resolution and fidelity** (D-212, D-306, D-308, D-312, D-441), on development and on confirmation:

- every trade is held to its stop or its target (no time stop); at most 5 % of each leg's trades reach the firm's
  flatten, overall and in every year, in the trades as taken, per market (D-212; the 5 % of D-308 (3), kept by the
  operator in D-432; D-434);
- realised risk at least 0.9 of the allowance-capped intention on the gate row
  (`realised_to_intended_capped_risk`), risk declared per stop width in whole micros (D-312 (1));
- every offered R resolves on development data (each R in the menu has trades, D-437).

**Confirmation lines** (D-355 as amended here). A confirmation passes on all three:

- **C1 — the gate** of §1 at the registered 0.05 bound, over the window's 21-session blocks;
- **C2 — every counted period** (at least 40 trading days, FOMC days out) grows on its own campaign at the point,
  its activity bound above one half (the one-sided Wilson bound of the share of days with a trade, D-305), and no
  path's Sharpe changes sign without its idle blocks; at least two counted periods;
- **C4 — fidelity**: the resolution and fidelity lines above, and no counted period without a gate trade.

**C3 is no longer a confirmation line.** D-355 wrote both "C3: break-even denial at least 0.25 and the bound arm above
zero at 10 % denial" and "beside, never as the verdict: 10 / 25 / 50 % denial", and the conflict with D-234 ("the
gate's tier-3 denial probability is 0 %; 10, 25 and 50 % are reported beside every verdict, never as the rule") was
never reconciled. From D-457 every denial reading is beside the verdict (§4). P-10's registered FAIL on C3 stands as
the record of the conflict (D-450, D-452); read without C3 it met every line, and that reading is exploratory because
the window had been read — it is not a confirmed pass (the NQB1 precedent, D-235).

**The confirmation window** (D-107, D-237, D-451, D-452):

- declared per market in `config/windows.yaml` **before any development read** of that market (R4), read once per
  registered test, at most three registered confirmation tests per market (D-107);
- as long as the data allows, so the bound's width does not decide the verdict by itself: the registration states
  the window's 21-session block count beside development's;
- before registering, the Combine's headroom over its target is checked against the window's bound: a plan whose
  Combine passes with little room turns the bound's flat shift into lost passes (D-451 (3)); the check and its
  numbers go in the pre-registration.

## 4. Beside every verdict — reported, never deciding (D-145, D-189, D-234, D-289, D-355)

From the same result file, every time:

- growth on the required bankroll at 10, 25 and 50 % denial at the bound, and the **break-even denial**
  (`pf_break_even_denial_p50`: the share of payouts the firm would have to deny for the median path's growth to reach
  zero) — the tier-3 enforcement risk, priced and never a verdict line (D-234);
- the placement **on** (D-289);
- the **zero-edge twin** (the same campaign with every R's edge set to zero) — where the money comes from (D-145);
  and, where the policy is a table, the fixed-legs twin (D-355; P-06's form);
- each R's realised per-trade sd against the registered `assumed_sd` (D-192, D-355);
- the point arm (outcomes as measured);
- `e` and its bound per R, and propsim D-47's criterion (e ≥ 0.10 net, bound ≥ 0.05);
- on a confirmation, each R's bound at 0.05/N and the deflated Sharpe at N (D-189, D-230);
- the pattern measures of tier 3 (Combine purchases per path and the most in any 21 days, closures at request,
  payouts exposed) and the Focused Trader Program -- its "excessive recycling" has no published threshold (D-447), so
  for a campaign of the breach-and-repurchase kind it is read as D-495 found it on Topstep's pages and D-497 models it
  (a Slowdown or Corrective placement at declared, swept thresholds; D-498's `results/ftp_sweep.csv` on FV3-C's and
  P-11's campaigns): the growth that survives each threshold, beside the verdict, never as it (D-234);
- the notional engine's `median_log_growth`;
- from D-663, the four validation readings (`docs/RESEARCH_PROTOCOL.md` steps 4, 7 and 8): the gate row with each
  path's days block-resampled (the stationary bootstrap at mean block 5, 21 and 63 sessions; the gate itself draws
  single days independently) and the required bankroll under each; the coverage of the bound of `e` at its
  registered level; the break-even `e` and its margin below the registered bound; and the missed-trade stress
  (offered trades and whole sessions missed) -- beside the verdict, never a verdict line, until the operator rules
  otherwise (D-145).

## 5. Reported with a FLAG level (proposed here, adopted by D-457)

These have had no threshold. Each is reported beside every verdict with a **FLAG** when it is worse than FV3-C's own
confirmation — the only candidate to pass one (P-06) — on its bad tail. A FLAG never changes the gate's verdict; it
is read with §6 when deciding whether to pursue a candidate, and it travels into the shadow period's pre-registration.

**The rule, one for every measure:** the candidate's gate-row median path is flagged when it is beyond **P-06's
lower-bound arm's 90th-percentile path** in the measure's bad direction (the 10th percentile where higher is better).
The percentile is the engine's (`propedge.campaign.portfolio._pct`: numpy's linear interpolation, a missing value left
out, an infinite one counted), so "the 90th-percentile path" is a level that may fall between two paths. The levels
belong to P-06's campaign -- 504 sessions, 500 paths, Topstep's seats and subscription; a candidate run on another
horizon, path count or firm is not comparable with them, and its FLAGs read "not applicable" until levels of its kind
are computed (D-475).
The levels are computed by `scripts/success_thresholds.py` into `results/success_thresholds.csv` from P-06's own
paths — the gate's paths (`results/fv3_confirmation_paths.csv`) and, for the measures that need each path's cash by
day, the same campaign re-run with every path's record (`results/fv3c_confirmation_path_detail.csv`, reproducing the
saved paths path for path before any measure is read; exploratory, never the verdict). The output's `source`
column names the detail file for all seven levels: on the columns both files hold they are identical path for path,
so the levels are the same from either.

| measure | candidate's column (gate row) | bad direction | P-06 per-path column |
|---|---|---|---|
| required bankroll | `pf_required_p50` | higher | deepest loss from the start + one subscription |
| largest drawdown | `pf_max_drawdown_p50` | higher | `max_drawdown` |
| days to the first payout | `median_days_to_first_payout` | higher | `days_to_first_payout` |
| payouts a month | `st_payouts_per_month_p50` | lower | payouts per 21-session month |
| share of red months | `st_red_share_p50` | higher | red 21-session months / months |
| month-to-month spread | `st_month_sd_p50` | higher | sd of 21-session net |
| days underwater | `st_underwater_days_p50` | higher | days below the previous high |

Reported without a level, because the candidate's file has no median-path column to hold against P-06's paths: the
required bankroll's p90, p99 and worst; the worst and best month (`st_worst_month_p05`, `st_best_month_p95`); the
Combine pass share and the days to a pass; the mean gross payout (`mean_payout_gross`, a mean over payouts); payouts
per path (`median_payouts_per_path`).

## 6. Beat FV3-C's row or stop (D-365, D-382, D-452)

`results/scoreboard.csv` (R2) holds every registered run's gate row. A candidate whose growth on the required bankroll
at the bound does not beat FV3-C's row **of the same kind** (D-455 (2)) — FV3-C's development baseline for a development run,
P-06 for a confirmation — is not pursued past its verdict, whatever the verdict says; its required bankroll and the
§5 FLAGs are read beside. A PASS that beats the row queues for the shadow period behind FV3-C and gets no levers
(D-419).

## 7. The shadow period and real capital (`docs/DEPLOYMENT_PROTOCOL.md`)

The deployment protocol's gates stand, with the confirmation read by §3 (C3 beside) and these readings named:

- **The required-bankroll p95 path** (the protocol's §4.6 and §5, D-400's P2): the 95th percentile, across the
  confirmation run's lower-bound-arm paths (run "gate placement off", 0 % denial), of each path's deepest loss from
  the start — `propedge.campaign.criteria.paths_quantile(..., "deepest_loss_from_start", 95)`; the live drawdown from
  the start is held inside it. The point arm's p95 is the FLAG level (D-400). Both are in
  `results/success_thresholds.csv`.
- The bankroll funded at the confirmation run's required p90, p99 in reserve (D-337). `pf_required_p90` already
  holds one subscription (each path's deepest loss from the start plus one Combine's subscription,
  `propedge.campaign.portfolio.required_bankroll`); the deployment protocol's "plus one subscription" names that
  margin, not a second one (D-475's reading; a second would be a change to D-337).
- The shadow period's acceptance and kill rules as the protocol's §4 and §5 (D-337, D-398, D-400).

## 8. What changed, and where (D-457)

1. C3 removed as a confirmation line; every denial reading beside the verdict (§3, §4; D-234).
2. The gate's metric named everywhere as growth on the required bankroll (`CLAUDE.md`, `CHARTER.md` by D-454;
   `prereg/TEMPLATE.md` and `propedge/backtest/prereg.py`'s field description here).
3. The required-bankroll p95 path computed by code and tested (`propedge/campaign/criteria.py`).
4. The 0.05/N sentence settled (§2) and written into `prereg/TEMPLATE.md`.
5. Confirmation windows declared per market before any development read (§3; built by R4).
6. FLAG levels for the measures that had none, from P-06's own paths (§5).
