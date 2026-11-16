const fs = require("fs");
const L = require("./lib"); const N = require("./data"); const { E } = require("./report_p2");
const { run, p, rich, H1, H1n, H2, H3, pb, bullets, numbered, eq, table, card, callout, figure, NAVY, GREY } = L;
const { fmt0, fmt1, pct } = N;
const F = __dirname + "/figs/";
const $ = (x) => "$" + fmt0(x);
const EDGES = [0, 0.02, 0.05, 0.10, 0.15, 0.20];
const ep = (e) => `${(100 * e).toFixed(0)} %`;

function partVII() {
  const out = [];
  out.push(H1n("Part VII — The Conduct Finding: the Zero-Edge Campaign Is Prohibited"));
  out.push(H2("33. What the firm's terms prohibit"));
  out.push(p("Part VI shows that the contract turns a fair coin into positive expected cash. Before any of that could be used, the firm's conduct terms had to be read against the geometry. They were read on the official help centre on 21 September 2026, and they settle the question."));
  out.push(...bullets([
    "Prohibited Trading Strategies (article 10305426) defines account stacking as repeatedly trading aggressively, hitting the maximum loss limit in one account, switching to another account and repeating, with the goal of running high-risk attempts until a large win occurs, and states that this exploits risk parameters and is not permitted. The page describes its list as \"hard stops\", not gray areas.",
    "Prohibited Conduct (article 10296582) repeats the account-stacking prohibition and adds a sole-discretion catch-all for conduct that is uncommercial, games the market, is \"not a viable strategy\", or is not responsible trading.",
    "The same pages prohibit cross-account hedging and exploiting simulator fills — including relying on the lack of slippage in simulation to achieve stop-loss execution that would not happen live.",
    "The Responsible Trading Program (article 13620045) places traders whose patterns suggest unsustainable or high-risk behaviour into a programme in which Combines carry a daily loss limit and new funded accounts are Consistency-path only. Topstep's own description of those patterns includes blowing accounts, overleveraging, trading without defined risk and churning through many accounts.",
  ]));
  out.push(p("Every zero-edge profile in Part VI earns its expected value the same way: many attempts, most of which fail at the floor, each replaced by a new purchase until a large win arrives. That is the definition of account stacking, and a process with no edge is by construction not a viable strategy. The structural value measured in Part VI is therefore not a loophole around the rule; it is the thing the rule prohibits. Hypothesis H6 is rejected."));
  out.push(H2("34. The ridge candidates against the terms"));
  out.push(...table(["Candidate", "Relies on fail-and-repurchase at zero edge", "Winners larger than losers", "Largest single position (% of the $2,000 drawdown)", "Verdict at zero edge"], [
    ["Supremum policy ($2,000 at 0.825:1, then 0.675:1)", "yes", "no", "100 %", "not acceptable"],
    ["1:1 $1,500, one trade a day (recommended in Part VI)", "yes", "no (equal)", "75 %", "not acceptable"],
    ["0.5:1 $1,000, three a day", "yes", "no", "50 %", "not acceptable"],
    ["1.5:1 $1,000", "yes", "yes", "50 %", "not acceptable at e = 0"],
    ["2:1 $750", "yes", "yes", "37.5 %", "not acceptable at e = 0; most consistent member with a real edge"],
    ["Funded day-one all-in, 2:1 to 5:1", "—", "yes", "100 %", "not acceptable"],
    ["Funded all-in split into $1,500 + $500", "—", "yes", "75 % then 100 % of what remains", "not acceptable: same pattern, split"],
  ], [2700, 2000, 1500, 2000, 1880], { key: "conduct", caption: "Ridge candidates against the conduct terms", size: 17, note: "Candidates are never ranked or modified by how noticeable they are: a slower or smaller version of a prohibited pattern is still that pattern, because the rule is defined by its goal." }));
  out.push(H2("35. Constraints for a trader with a genuine edge"));
  out.push(p("The terms do not prohibit using the contract; they prohibit using it without an edge, by failing repeatedly. For a trader with a demonstrated edge the terms translate into constraints on the geometry, which Part VIII applies as selection rules:"));
  out.push(...bullets([
    "winners larger than losers (R > 1);",
    "risk per position well below the maximum — at most $1,000, half the drawdown, in the tests;",
    "no single position that decides the account, on either stage (the funded all-in is excluded);",
    "one account at a time, and no fail-and-repurchase campaign — the edge, not the replacement of failed accounts, must carry the value.",
  ]));
  return out;
}

function partVIII() {
  const out = [];
  out.push(H1n("Part VIII — The Value of a Demonstrated Edge"));
  out.push(p("With the zero-edge campaign excluded, the useful question becomes: for a trader with a real edge e after costs, trading within the constraints of §35, what is the contract worth and which structure should they use? The study was pre-registered (edge/PREREG_T5.md) before any run: profiles, edges, metrics and validation criteria were fixed in advance, and two analyses added after seeing the results are labelled exploratory."));
  out.push(H2("36. Design"));
  out.push(...bullets([
    "Admissible Combine and funded profiles: R ∈ {1.5, 2, 3} × $ risk ∈ {$500, $750, $1,000}, one trade a day, static on both stages. Reference only: 1:1 $1,500 (not admissible), to price the constraints.",
    "Edges e ∈ {0, 0.02, 0.05, 0.10, 0.15, 0.20}; e = 0 is reported only as the structural reference.",
    "Combine stage: the exact chain of §20.1, with Monte Carlo (N = 200,000 per cell) as validator. Funded stage: Monte Carlo (N = 50,000), one-year horizon, Standard path and the Consistency path the Responsible Trading Program would impose, net-profit rule on, fee-free payout method.",
    "Composition: stages are independent given a pass, so any (Combine, funded) pair is composed exactly: EV per attempt = P(pass) × (funded cash − 149) − E[subscriptions].",
  ]));
  out.push(H2("37. Validation"));
  const v = N.validationT5;
  const grab = (re) => (v.match(re) || [, "?"])[1];
  out.push(...table(["Check (pre-registered)", "Criterion", "Result"], [
    ["V1 exact chain vs Monte Carlo, Combine P(pass) and E[days], all profiles and edges", "≤ 2 of 120 beyond 3 SE; none beyond 4 SE", `${grab(/(\d+) beyond 3 SE/)} beyond 3 SE, max |z| ${grab(/max \|z\| ([\d.]+) -> PASS/)} — PASS`],
    ["V1 follow-up: four largest deviations at N = 1,000,000, seeds fixed beforehand", "diagnosis (§23.1)", "all within 2.13 SE, signs mixed — chance"],
    ["V2 chain reproduces 16/49 at e = 0", "|difference| < 10⁻⁹", `${grab(/16\/49 = ([-\d.e]+)/)} — PASS`],
    ["V2 chain reproduces the stored zero-edge grid", "all within 3 SE", `max |z| ${grab(/grid reproduction: \d+ cells, max \|z\| ([\d.]+)/)} — PASS`],
    ["V3 zero-edge funded bounds (gross ≤ $2,000; E[B + Q] ≤ 0)", "within 3 SE", "PASS"],
    ["V3 funded cash non-decreasing in edge, every profile and path", "no drop > 3 SE", "PASS"],
  ], [4300, 2700, 3080], { key: "val", caption: "Validation of the value-of-edge study (edge/validation_T5.txt)", size: 17 }));
  out.push(H2("38. Combine pass probability against edge"));
  const profs = [[1.5, 500], [2, 500], [2, 750], [1.5, 1000], [3, 500], [1.5, 750], [3, 750], [2, 1000], [3, 1000], [1, 1500]];
  out.push(...table(["Profile", ...EDGES.map(ep)], profs.map(([R, r]) => [`${R}:1 $${fmt0(r)}${R === 1 ? " (reference)" : ""}`, ...EDGES.map(e => pct(N.ce(R, r, e).p_pass, 1))]),
    [2600, 1250, 1250, 1250, 1250, 1240, 1240], { key: "passedge", caption: "Exact Combine pass probability by profile and edge (edge/results_combine_edge.csv)", size: 17 }));
  out.push(...figure(F + "fig14_pass_vs_edge.png", "Pass probability against edge. Small risk with moderate R (1.5:1 $500) overtakes every other profile from about a 5 % edge because it takes more trades before the account resolves, letting the edge average out; high R with large risk (3:1 $1,000) is the weakest throughout.", { key: "passedge" }));
  out.push(p("Two rules explain the table. Higher R means more variance: at 3:1 a trade wins about one time in four, so results swing and the Combine resolves on luck. Larger $ risk means fewer trades before resolution, so the edge has less room to work. The reference 1:1 $1,500 passes most often at low edge but is excluded by the constraints."));
  out.push(H2("39. EV per attempt, and how much of it comes from the edge"));
  const rows = EDGES.map(e => { const b = N.bestPair(e, "standard"); return [ep(e), `${b.combine_profile} → ${b.xfa_profile}`, pct(b.p_pass, 1), $(b.ev_per_attempt), $(b.ev_structural), $(b.ev_from_edge), pct(b.edge_share_of_ev, 0), fmt1(b.failed_combines_per_year)]; });
  out.push(...table(["Edge", "Best admissible pair (Combine → funded)", "P(pass)", "EV per attempt", "structural", "from the edge", "edge share", "failed Combines / year"], rows,
    [800, 2400, 1000, 1200, 1100, 1200, 1000, 1380], { key: "edgeshare", caption: "Best pre-registered admissible pair by EV per attempt, Standard path, full payouts at eligibility, one-year funded horizon (edge/results_value_of_edge.csv)", size: 16 }));
  out.push(...figure(F + "fig15_edge_share.png", "EV per attempt split into its structural part (present at zero edge; prohibited to exploit) and the part that comes from the edge.", { key: "edgeshare" }));
  out.push(p(`Below a 5 % edge most of the value is structural and the churn is high: at 2 % only ${pct(N.bestPair(0.02, "standard").edge_share_of_ev, 0)} of EV comes from the edge, with about ${fmt0(N.bestPair(0.02, "standard").failed_combines_per_year)} failed Combines a year on one account slot run continuously. At 10 % the edge supplies ${pct(N.bestPair(0.10, "standard").edge_share_of_ev, 0)} and failures fall to about ${fmt0(N.bestPair(0.10, "standard").failed_combines_per_year)} a year. The best Combine structure shifts from 2:1 $750 at low edge to 1.5:1 $500 from 10 %. On the Consistency path (the Responsible Trading Program case) the same pairs are worth about 10–20 % less (edge/T5_RESULTS.md §2b).`));
  out.push(p("One metric is deliberately not the headline. A \"value per account-year\" rate — EV per attempt divided by the time an attempt occupies — also rewards cycling through failed attempts: at zero edge it reported thousands of dollars a year, which is the prohibited pattern's value. It is reported in the result file only beside its churn (failed Combines per year) and the edge/structural split."));
  out.push(H2("40. The funded account: payout policy is first-order at positive edge (exploratory)"));
  out.push(p("Any payout moves the floor to $0 (official rule). An account that withdraws early is left protected only by its own balance, so a small balance with a small bet is soon wiped out — at zero edge this costs nothing, but with a real edge it throws away the compounding the edge would produce. The exploratory runs compared taking the full allowed payout at once with a buffer rule that never withdraws below a kept balance (§13):"));
  const bprof = [[1.5, 500], [2, 300], [2, 150], [1.5, 1000], [2, 750]];
  const keeps = [0, 2000, 5000, 8000];
  const cellB = (R, r, e, k) => { const b = N.buf(R, r, e, k); return b ? $(b.cash_per_year) : "—"; };
  out.push(...table(["Funded profile", ...keeps.map(k => `keep $${fmt0(k)}, e = 10 %`), "keep $0, e = 20 %", "keep $8,000, e = 20 %"],
    bprof.map(([R, r]) => [`${R}:1 $${fmt0(r)}`, ...keeps.map(k => cellB(R, r, 0.10, k)), cellB(R, r, 0.20, 0), cellB(R, r, 0.20, 8000)]),
    [1700, 1400, 1400, 1400, 1400, 1400, 1380], { key: "buffer", caption: "Realised cash per funded account per year over a two-year horizon, by payout buffer (edge/results_payout_buffer_*.csv; exploratory)", size: 16, note: "Balance still in the account at the horizon is not counted, so larger buffers are understated. — = not run." }));
  out.push(...figure(F + "fig16_payout_buffer.png", "Realised cash per year against the buffer kept in the account, at 10 % and 20 % edge. The best buffers are interior: about $8,000 for 1.5:1 $500, about $3,000 for 2:1 $150.", { key: "buffer", maxWidth: 6.9 }));
  const b10 = N.bestBuf(0.10), b20 = N.bestBuf(0.20), t10 = N.bestTakeMax(0.10), t20 = N.bestTakeMax(0.20);
  out.push(p(`Best found: ${b10.R}:1 at $${fmt0(b10.risk)} with a $${fmt0(b10.keep_balance)} buffer — ${$(b10.cash_per_year)} a year at 10 % edge against ${$(t10.cash_per_year)} for the best take-everything policy, and ${$(b20.cash_per_year)} against ${$(t20.cash_per_year)} at 20 %. Every buffer respects the zero-edge ceilings. These are exploratory results on a coarse grid; they establish the direction and size of the effect, not a tuned optimum.`));
  out.push(H2("41. Value per attempt with the best funded policy"));
  out.push(...table(["Edge", "Combine profile", "P(pass)", "Funded policy", "Funded cash, 2 years", "EV per Combine attempt"],
    [0.05, 0.10, 0.20].map(e => { const b = N.evBestBuffer(e); return [ep(e), b.combine, pct(b.p_pass, 1), `${b.funded.R}:1 $${fmt0(b.funded.risk)}, keep $${fmt0(b.funded.keep_balance)}`, $(b.funded2y), $(b.ev)]; }),
    [900, 1600, 1100, 2700, 1800, 1980], { key: "evbuffer", caption: "EV per Combine attempt with the best funded policy found (composed from edge/results_combine_edge.csv and the buffer results; exploratory)", size: 17 }));
  out.push(p("Value grows much faster than edge: from 10 % to 20 % the EV per attempt rises roughly fivefold. Fee risk becomes small at these edges — at 10 % with 1.5:1 $500 a Combine fails about 61 % of the time, so eight failures in a row have probability about 2 %. The binding risk is no longer running out of fee money; it is believing in an edge that is not there."));
  out.push(H2("42. How much data a demonstrated edge needs"));
  out.push(p("A single bracket trade returns +R or −1 in units of risk, so its standard deviation is (1+R)·√(p(1−p)). For the one-sided 95 % lower bound on the measured edge to exceed half the true edge, the number of trades must satisfy:"));
  out.push(...eq("n ≥ ( 1.645 · (1+R) √(p(1−p)) / (e/2) )²,   p = (1+e)/(1+R)", [["n", "trades in the out-of-sample test"], ["1.645", "one-sided 95 % normal quantile"]], { key: "samplesize" })); E.samplesize = L.eqNum();
  out.push(...table(["R", "e = 5 %", "e = 10 %", "e = 20 %"], [1.5, 2, 3].map(R => [`${R}:1`, ...[0.05, 0.10, 0.20].map(e => { const s = N.ss(R, e); return `${fmt0(s.trades_lower_bound_above_half_edge)} trades (${s.years_at_1_per_day} yrs)`; })]),
    [1400, 2900, 2900, 2880], { key: "samples", caption: "Trades needed to demonstrate an edge (lower bound above half the true edge; years at one trade a day; edge/results_sample_size.csv)", size: 18 }));
  out.push(...figure(F + "fig17_sample_size.png", "Trades needed to demonstrate an edge, log scale. A 10 % edge needs years of one-trade-a-day data; lower R needs fewer trades.", { key: "samples" }));
  out.push(p("An edge of the size that matters cannot be demonstrated from a short live record at one trade a day. The research stage must test on long historical data with realistic costs and fills, and treat any live or paper record as a check on execution, not as proof of edge."));
  return out;
}

function partIX() {
  const out = [];
  out.push(H1n("Part IX — Sensitivity and Robustness"));
  out.push(H2("43. Sensitivity to edge at the zero-edge profile"));
  out.push(p("For the Part VI profiles, a negative edge stands in for costs. The recommended zero-edge profiles were re-run at six edges (N = 100,000 each)."));
  out.push(...table(["edge e", "P(pass)", "XFA static net", "EV / attempt", "EV / attempt with frictions"],
    N.fin.map(r => [r.edge.toFixed(2), `${pct(r.c_p_pass, 2)} ± ${pct(r.c_p_pass_se, 2)}`, $(r.xfa_static_net), $(r.ev_attempt_static), $(r.ev_attempt_static_frictions)]),
    [1500, 2600, 2000, 2000, 1980], { key: "ladder", caption: "Edge ladder for the zero-edge profiles (results_final.csv)" }));
  out.push(...figure(F + "fig12_edge_ladder.png", "EV per attempt against edge for the zero-edge profiles. Positive down to e = −0.10 — which is exactly why the structural value is exploitable without skill, and why it is prohibited.", { key: "ladder" }));
  out.push(H2("44. Sensitivity to the consistency fraction"));
  out.push(p(`Finding 5 is itself a sensitivity analysis: the Combine optimum moves with the consistency fraction exactly as the mechanism predicts, and EV at the optimum ranges from about $${fmt0(N.peaks[0.4][2].ev)} (fraction 0.40) to about $${fmt0(N.peaks[1][2].ev)} (rule inert) at R = 2.`));
  out.push(H2("45. Robustness checks"));
  out.push(...bullets([
    `Ceiling oracle: no grid cell exceeds P(pass) = 0.40 + 4 SE; the maximum funded gross across 320 cell-paths is $${fmt0(N.maxGross)} < $2,000.`,
    `Exact results: 16/49 reproduced by Monte Carlo at N = ${fmt0(N.mcN)} (z = ${N.mcZ >= 0 ? "+" : ""}${N.mcZ.toFixed(2)}); the supremum ${N.sup(50, 0).sup_p_pass.toFixed(6)} reproduced by simulation of the supremum policy (pooled 5M, z = +1.13); the exact edge chain agrees with Monte Carlo in 120 comparisons.`,
    "Identities: the day-one all-in matches 0.9·2,000·R/(1+R) at four values of R; the time-barrier model recovers the binary limits at s = 8; the all-in identity survives both a $1,000 daily loss limit and a split into $1,500 + $500.",
    `Conventions: truncate and resize agree within noise in nine cells (Table {{T:fm}}); drift and linear edge conventions are identical in ${N.ecIdentical} of ${N.ecPairs.length} cells.`,
    "Horizon: the 250-day funded horizon does not bind without frictions (P(closed) = 1.000) but does bind at R ≥ 3 with the net-profit rule; results that depend on it were re-run at up to 1,000 days (Finding 7).",
    "Seeds: every result file records its seed; comparisons are paired; pre-registered checks that failed are kept on record with their diagnosis (§23.1).",
  ]));
  return out;
}

function partX() {
  const out = [];
  out.push(H1n("Part X — Interpretation and Limitations"));
  out.push(H2("46. What the results mean"));
  out.push(p("The contract does convert a fair process into positive expected cash, and the conversion is tightly bounded: 40 % on the Combine, of which the best possible strategy reaches 32.7 %, and the $2,000 cushion on the funded account. Every profile choice at zero edge is a choice about where to lose: quickly and at the deepest floor (good), or slowly while the floor climbs (bad). That is why the funded optimum is a single all-or-nothing bet, and why pass probability hardly discriminates between profiles while time does."));
  out.push(p("The same asymmetry is what the firm's conduct rules target. The value exists because failure is cheap and repeatable, so extracting it means failing repeatedly — the named prohibition. The positive result at zero edge is therefore best read as a precise description of what the firm is protecting itself against."));
  out.push(p("With a genuine edge the picture inverts. The contract becomes an amplifier: modest bets with moderate R let the edge average out before the account resolves, and a funded account kept alive with a buffer compounds it. The structure that was optimal at zero edge (large, single, account-deciding bets) is the wrong structure for an edge, as well as a prohibited one."));
  out.push(H2("47. What the results do not mean"));
  out.push(...bullets([
    "They do not mean a trader can make money without skill: the zero-edge route is prohibited, and the value of an edge depends entirely on that edge being real.",
    "They do not show that any strategy has an edge. The engine values an edge; it cannot find one.",
    "They do not price discretion: the firm may still review any pattern, and its terms change over time.",
  ]));
  out.push(H2("48. Limitations and uncertainties"));
  out.push(...table(["Limitation", "Where it enters", "Direction of bias", "How it could be resolved"], [
    ["Binary two-outcome trades", "all results", "real trades have a distribution of outcomes", "replace the draw with the empirical outcome distribution of a candidate strategy"],
    ["One trade per day, fixed $ risk", "Part VIII", "more trades per day would need fewer calendar days to demonstrate an edge", "extend the admissible set once a candidate's frequency is known"],
    ["Exact-at-stop fills", "all results", "overstates results; relying on SIM fills is itself prohibited", "measure fills; require the edge net of realistic slippage"],
    ["Drift convention for edge inside truncated trades", "Part VIII", "second-order at |e| ≤ 0.10", "empirical excursion data"],
    ["No scaling-plan contract limits", "large balances", "may constrain size at high balances", "add the scaling plan to the engine"],
    ["Funded horizons (1–2 years; unrealised balance not counted)", "Part VIII", "understates buffered accounts", "longer horizons"],
    ["Buffer and small-risk results are exploratory", "§40–41", "chosen after seeing results; coarse grids", "pre-register a buffer study for the actual candidate"],
    ["Firm discretion and rule changes", "all", "one-directional: can only reduce realised value", "re-verify the terms before use"],
  ], [2300, 1700, 2900, 3180], { key: "limits", caption: "Limitations, their entry points and remedies", size: 17 }));
  return out;
}

function partXI() {
  const out = [];
  out.push(H1n("Part XI — Conclusions"));
  out.push(p("Each conclusion is stated with the part of the analysis that supports it and nothing further."));
  out.push(...numbered([
    `Under a fair process no strategy passes the Combine more than 40 % of the time and no funded account pays out more than $2,000 gross in expectation; the best achievable pass probability over all strategies is ${N.sup(50, 0).sup_p_pass.toFixed(4)} (Part IV).`,
    `At zero edge the best geometry is the ridge R × $ risk ≈ $1,500 on the Combine (1:1 $1,500 passes with probability exactly 16/49) and a single account-deciding bet on the funded side (net 0.9·2,000·R/(1+R)); together they are worth ${$(N.evExact(N.xfaStatic))}–${$(N.evExact(N.allin[3]))} per attempt, with only ${pct(N.fig13.p_net_pos, 0)} of attempts ever positive (Parts IV, VI).`,
    "That value exists only through repeated failure and replacement, which the firm prohibits as account stacking; a zero-edge process is also \"not a viable strategy\" under its terms. The zero-edge campaign is not a usable plan (Part VII).",
    `Within the conduct constraints, a genuine edge is amplified by the contract. Its share of EV is ${pct(N.bestPair(0.05, "standard").edge_share_of_ev, 0)} at a 5 % edge and ${pct(N.bestPair(0.10, "standard").edge_share_of_ev, 0)} at 10 %. Best structures: 2:1 $750 at low edge, 1.5:1 $500 from about 10 %; high R with large risk (3:1 $1,000) is the weakest (Part VIII, pre-registered and validated).`,
    `At positive edge the funded payout policy matters as much as the R:R: keeping a buffer roughly doubles realised cash per funded account, and with it EV per attempt is about ${$(N.evBestBuffer(0.10).ev)} at a 10 % edge (Part VIII, exploratory).`,
    `Demonstrating a 10 % edge needs ${fmt0(N.ss(1.5, 0.10).trades_lower_bound_above_half_edge)}–${fmt0(N.ss(3, 0.10).trades_lower_bound_above_half_edge)} trades; at one trade a day that is ${N.ss(1.5, 0.10).years_at_1_per_day}–${N.ss(3, 0.10).years_at_1_per_day} years, so long historical tests are required (Part VIII).`,
    "Four modelling errors were found and corrected along the way: trades overshooting the floor in the earlier run model, three missing rules, a horizon artefact in the high-R funded comparison, and a per-year metric that rewarded churn (Findings 1 and 7, Part VIII).",
  ]));
  out.push(H2("49. The criterion for the research stage (pre-registered)"));
  out.push(...callout("WHAT THE NEXT STAGE MUST DEMONSTRATE", [
    "An edge e — mean P&L per trade ÷ $ risked, net of commissions and slippage, with realistic fills — measured out of sample on the bracket structure the account will use (R between 1.5 and 3, 15:10 CT flatten applied).",
    "Pursue a candidate only if the point estimate is e ≥ 0.10 and the one-sided 95 % lower bound is ≥ 0.05. Below that, the edge cannot be distinguished from the structural value.",
    "Use the lower bound, not the point estimate, for every sizing or money decision; value the candidate with the engine as in HANDOFF.md, replacing the binary draw with its empirical outcome distribution where needed.",
    "Respect §35: winners larger than losers, modest size, no account-deciding position, one account at a time, no fail-and-repurchase campaign.",
  ]));
  out.push(p("With this criterion the repository's question is closed. What remains is finding and demonstrating an edge, which is research, not modelling."));
  return out;
}

function appendices() {
  const out = [];
  out.push(H1("Appendix A — Vocabulary"));
  out.push(...table(["Term", "Meaning in this study"], [
    ["Account stacking", "The firm's name for repeatedly trading aggressively to the loss limit, switching accounts and repeating until a large win; prohibited."],
    ["Attempt", "One Combine purchase followed, if passed, by one funded account run to closure or horizon."],
    ["Buffer", "Payout rule that never withdraws below a kept balance (keep_balance)."],
    ["Cushion / room", "Dollars the account can lose before liquidation: B − F."],
    ["Demonstrated edge", "An edge measured out of sample, net of costs and realistic fills, with a lower confidence bound above the criterion (§49)."],
    ["Edge share", "The fraction of EV per attempt not present at zero edge."],
    ["Fair process", "Trade outcomes with E[X] = 0 exactly: p = 1/(1+R)."],
    ["Harvest", "Small-bet trading after a large first win, to accumulate winning days and payouts."],
    ["Leak", "Cushion consumed by the ratchet on paths that die without paying out."],
    ["Lock", "The 16:00 CT event at which a day's P&L becomes final and the floor, best day and eligibility update."],
    ["Ridge", "The locus of EV-maximising $ risk across R at a fixed day rule: R × $ risk ≈ $1,500."],
    ["Structural EV", "Expected cash per attempt at zero edge."],
    ["Supremum", "The best pass probability achievable by any strategy (§19.1)."],
    ["Truncate", "Liquidation of a trade at the floor with the barrier-race probability c/(c+W)."],
  ], [2200, 7880], { size: 18 }));
  out.push(H1n("Appendix B — Notation"));
  out.push(...table(["Symbol", "Meaning", "Units"], [
    ["B, F, D, B_d", "balance, floor, today's P&L, best day", "$"], ["c", "room B − F", "$"], ["R, r, W", "reward multiple, dollar risk, dollar win R·r", "—, $, $"],
    ["e, p", "edge; win probability (1+e)/(1+R)", "—"], ["θ", "drift per unit variance 2μ/σ²", "1/$"], ["q, Q, C", "one payout request; cumulative gross payouts; cumulative cash", "$"],
    ["k", "kept balance under the buffer rule", "$"], ["V, cav", "best achievable pass probability; upper concave envelope", "—"],
    ["τ", "stopping time", "days"], ["T", "B + Q, the funded-account martingale", "$"], ["s", "session σ ÷ 2,000", "—"], ["π", "policy", "—"], ["n, SE", "trades or accounts; standard error", "—"],
  ], [2400, 6180, 1500], { size: 18 }));
  out.push(H1n("Appendix C — Equation reference"));
  const eqRows = [["p", "p = (1+e)/(1+R)", "declared process"], ["ev", "E[X] = e·r", "edge definition"], ["lock", "Combine trade and lock updates", "contract"],
    ["trunc", "P(win | c) = c/(c+W)", "floor convention"], ["mae", "zero-edge excursion law", "generator"], ["race", "drifted barrier race", "edge convention"], ["identity", "drifted liquidation identity", "edge convention"],
    ["payout", "funded payout", "contract"], ["pi", "(R_t, r_t) = π(S_t)", "policy"], ["session", "session barrier", "zero-edge all-in"], ["ceiling", "P(pass) ≤ 2/5", "bound"],
    ["xceil", "E[Q] ≤ 2,000", "bound"], ["leak", "E[Q] = (1 − P_pay)(2,000 − E[ratchet])", "leak identity"], ["allin", "E[Q] = 2,000·R/(1+R)", "funded optimum at zero edge"],
    ["markov", "16/49", "exact Combine profile"], ["supremum", "concave-envelope Bellman equation", "optimum over all strategies"], ["se", "standard errors", "statistics"],
    ["evatt", "EV per attempt", "output metric"], ["samplesize", "trades to demonstrate an edge", "research criterion"]];
  out.push(...table(["Eq.", "Statement", "Role"], eqRows.map(([k, s, r]) => [`{{E:${k}}}`, s, r]), [900, 5600, 3580], { size: 18 }));
  out.push(H1n("Appendix D — Test and validation architecture"));
  const desc = JSON.parse(fs.readFileSync(__dirname + "/test_descriptions.json", "utf8"));
  const names = [...fs.readFileSync(__dirname + "/../test_propsim.py", "utf8").matchAll(/^def test_(\w+)/gm)].map(m => m[1]);
  out.push(p(`test_propsim.py contains ${names.length} tests (read from the file at build time). Each is listed with what it pins.`, { keepNext: true }));
  out.push(...table(["Test", "Pins"], names.map(n => [n, desc[n] || "—"]), [4200, 5880], { size: 16 }));
  out.push(H1n("Appendix E — Decision log"));
  const dl = fs.readFileSync(__dirname + "/../DECISIONS.md", "utf8").split("\n").filter(l => /^\| D-\d+ /.test(l)).map(l => l.split("|").map(x => x.trim()));
  out.push(p(`Every modelling, scope and process decision, as recorded in DECISIONS.md (${dl.length} entries, read at build time). Decisions are never edited; a reversal is a new entry that cites the old one.`, { keepNext: true }));
  out.push(...table(["#", "Date", "Decision"], dl.map(c => [c[1], c[2], c[3].replace(/\*\*/g, "").replace(/`/g, "")]), [700, 1300, 8080], { size: 15 }));
  out.push(H1n("Appendix F — Result files and reproduction"));
  out.push(p("All numbers are produced by seeded scripts in the propsim repository and stored in the result files named beside each table. Top level: engine (propsim.py, statepolicy.py, timebarrier.py), tests, run_*.py and results_*.csv. optimality/: supremum, DLL, horizon and cross-check results. edge/: the pre-registered value-of-edge study, its validation and the exploratory runs. bankroll/: the zero-edge fee-bankroll model, kept as a record only because it models the prohibited campaign. deliverables/: the sources that build this document and the presentation. The repository ships as \"EV Backtest Results.zip\"; its closing record is CLOSED.md."));
  return out;
}

module.exports = { partVII, partVIII, partIX, partX, partXI, appendices };
