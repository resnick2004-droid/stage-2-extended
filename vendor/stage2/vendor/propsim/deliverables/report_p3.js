const L = require("./lib"); const N = require("./data"); const { E } = require("./report_p2");
const { run, p, rich, H1, H1n, H2, H3, pb, bullets, numbered, eq, table, card, callout, figure, NAVY, GREY } = L;
const { fmt0, fmt1, pct } = N;
const F = __dirname + "/figs/";
const $ = (x) => "$" + fmt0(x);

function partVI() {
  const out = [];
  out.push(H1n("Part VI — Results at Zero Edge: What the Contract Does"));
  out.push(...callout("HOW TO READ THIS PART", ["Everything in Part VI is measured at zero edge. It describes what the contract does to a fair process and which geometry extracts the most from it. The campaign these results require — many attempts, most failing at the floor, each replaced — is prohibited by the firm (Part VII). Read Part VI as a description of the contract, not as a plan."]));
  out.push(p("Results are presented in the order they were established, because each one conditions the next: the floor convention had to be settled before the grid could be trusted; the grid located the ridge; the sweep explained it; the state-dependent layer found the funded-side optimum; verification against the official rules corrected the engine; the time barrier turned the funded optimum into a measurable condition. Each finding is given as a card (question, method, result, meaning, what it does not establish), followed by the evidence and the arithmetic."));

  // ---- Finding 1
  out.push(H2("24. Finding 1 — The floor-overshoot error and its correction"));
  out.push(...card([
    ["RESEARCH QUESTION", "Does the 'binary resolution at the labelled dollar risk, no excursion' run model (gate 1.8) represent the contract's real-time breach rule?"],
    ["METHOD", "Run the static profile 1:1, $1,500, one trade a day at e = 0 under three floor conventions (none, truncate, resize) and compare with the analytic ceiling; solve the 'none' chain by hand; repeat on nine cells over a 504-day continuous lifecycle with shared seeds."],
    ["RESULT", `Under 'none' the profile passes with probability exactly 4/9 = 44.4 %, above the 40 % ceiling, with failures landing at −$3,000. Under truncate it passes at 16/49 = 32.7 %. Across nine cells the 'none' model inflates net per attempt in ${N.fmRows.filter(r => r.none.net_per_attempt / r.trunc.net_per_attempt > 1.05).length} of 9 (by ${Math.min(...N.fmRows.filter(r => r.none.net_per_attempt / r.trunc.net_per_attempt > 1.05).map(r => r.none.net_per_attempt / r.trunc.net_per_attempt)).toFixed(2)}× to ${Math.max(...N.fmRows.map(r => r.none.net_per_attempt / r.trunc.net_per_attempt)).toFixed(2)}×) and is neutral in one (1.5:1 $1,000, where the bet rarely meets a raised floor); truncate and resize agree within noise in every cell.`],
    ["WHAT IT MEANS", "Letting a trade lose past the floor preserves the martingale by making failures deeper than the contract allows, which manufactures pass probability. Any result computed that way ranks large-bet profiles too high. Truncate is the contract rule; resize is a legitimate solver choice with the same expectation."],
    ["WHAT IT DOES NOT ESTABLISH", "It says nothing about execution, stop placement or slippage. It is a statement about which mathematical object represents the intraday breach rule."],
  ]));
  out.push(p("The hand solution for 'none'. With no truncation the four states are D(0,−2000), A(1500,−500), C(0,−500) and B'(−1500,−2000) with full-size bets throughout: a = ½ + ½c, c = ½a ⇒ a = 2/3; d = ½a + ½b', b' = ½d ⇒ d = 1/3 + ¼d ⇒ d = 4/9. Fair-game conservation still holds — pass mass 4/9 at +3,000, fail mass 1/3 at −3,000 (through B') and 2/9 at −1,500 (through C): 4/9·3,000 − 1/3·3,000 − 2/9·1,500 = 1,333 − 1,000 − 333 = 0 — but the −3,000 and −1,500 leaves lie below the floors in force, which the contract cannot produce. The table below gives the nine-cell comparison."));
  out.push(...table(["Profile", "none", "truncate", "resize", "none ÷ truncate", "P(net > 0), truncate"],
    N.fmRows.map(r => [`${r.rr}:1 $${r.risk} ${r.rule}`, $(r.none.net_per_attempt), `${$(r.trunc.net_per_attempt)} ± ${fmt0(r.trunc.net_se)}`, $(r.resize.net_per_attempt), (r.none.net_per_attempt / r.trunc.net_per_attempt).toFixed(2) + "×", pct(r.trunc.p_net_pos)]),
    [2500, 1300, 1900, 1300, 1500, 1580], { key: "fm", caption: "Net cash per attempt over a 504-day continuous lifecycle under the three floor conventions (N = 20,000, seeds shared across conventions; results_floor_mode_504.csv)", note: "Standard errors shown for truncate; those for the other conventions are similar. The last column is the first appearance of the study's most sobering number: only 6–14 % of attempts end cash-positive." }));
  out.push(...figure(F + "fig08_floor_modes.png", "The same table as bars. The inflation is largest where a trade most often meets a raised floor: large bets, and any profile after an XFA payout has moved the floor to 0.", { key: "floor" }));

  // ---- Finding 2
  out.push(H2("25. Finding 2 — The static profile grid"));
  out.push(...card([
    ["RESEARCH QUESTION", "Across static (R, r, day rule) profiles, which pass most often and which produce the most expected cash per attempt at zero edge?"],
    ["METHOD", "160 cells (5 R × 8 r × 4 day rules), 10,000 accounts each, Combine to resolution then XFA for 250 days on each payout path; EV per attempt by Eq. (" + E.evatt + ") with the better path."],
    ["RESULT", `Pass probability is bounded by 40 % and realised at 24–33 % across the useful region (maximum ${pct(N.maxPass)}). EV is positive in ${N.posCells} of 160 cells; the best three are ${N.topEV.slice(0, 3).map(r => `${r.rr}:1 $${r.risk} ${r.day_rule} (${$(r.best_ev)})`).join(", ")}. The 49 negative cells are ${N.negByRisk[50] + N.negByRisk[100] + N.negByRisk[200] + N.negByRisk[300] + (N.negByRisk[500] || 0)} at $50–$500 risk and ${N.negByRisk[1500] || 0} at $1,500.`],
    ["WHAT IT MEANS", "H1 is supported as a property of the contract: it turns a fair process into ≈ $200 of expected cash per attempt (the mechanism Part VII shows is prohibited to exploit). The top cells ($197, $196, $187) are within two standard errors of each other, so the result is a ridge — R × $ risk ≈ $1,500 with $ risk ≤ $1,500 — not a single winner; 1:1 $1,500 is preferred because it is exactly solvable and resolves fastest. H2 is not: pass probability barely discriminates. What separates profiles is time-to-resolution (subscription drag at small r) and the consistency/floor geometry (turnover at large r)."],
    ["WHAT IT DOES NOT ESTABLISH", "Nothing about achievable execution of a $1,500 single trade, nor about variance: the grid reports expectations only."],
  ]));
  out.push(...figure(F + "fig04_pass_heatmap.png", "Combine pass probability by profile at e = 0, one and three trades a day (the 3/day stop-on-win and 6/day rules are in results_grid_edge0.csv). The surface is nearly flat in the interior; small bets fall off through ratchet leak over long horizons, large bets through consistency-rule inflation and floor kills.", { key: "passmap", maxWidth: 6.9 }));
  out.push(...figure(F + "fig05_ev_heatmap.png", "Expected net cash per attempt (best payout path), one and three trades a day. The negative band at $50–$200 is subscription drag: those profiles take 80–1,100 trading days to resolve. Values below −$999 are printed in thousands.", { key: "evmap", maxWidth: 6.9 }));
  out.push(...figure(F + "fig06_ev_vs_risk_ridge.png", "EV against $ risk at one trade a day, one line per R. Every line rises out of the subscription region, peaks, and turns over; the peak location is the subject of Finding 5.", { key: "ridge" }));
  const c50 = N.cell(1, 50, "1/day"), c1500 = N.cell(1, 1500, "1/day");
  out.push(p(`Worked example of subscription drag. At 1:1, $50, one trade a day, the Combine resolves in ${fmt0(c50.c_mean_days)} trading days on average and pays ${$(c50.c_mean_sub_fees)} in subscriptions; at 1:1, $1,500 it resolves in ${fmt1(c1500.c_mean_days)} days for $49. The pass probabilities are ${pct(c50.c_p_pass)} and ${pct(c1500.c_p_pass)}; the $${fmt0(c1500.best_ev - c50.best_ev)} EV difference between the cells is almost entirely the fee clock.`));
  out.push(...table(["R:R", "$ risk", "day rule", "P(pass)", "mean days", "sub $", "XFA net (std / cons)", "best path", "EV / attempt"],
    N.topEV.map(r => [r.rr + ":1", "$" + r.risk, r.day_rule, pct(r.c_p_pass), fmt1(r.c_mean_days), fmt0(r.c_mean_sub_fees), `${fmt0(r.xstd_mean_cash)} / ${fmt0(r.xcons_mean_cash)}`, r.best_path, $(r.best_ev)]),
    [700, 800, 1300, 900, 1000, 800, 1900, 1200, 1480], { key: "top5", caption: "The five best static cells by expected net cash per attempt (results_grid_edge0.csv)", size: 17 }));

  // ---- Finding 3
  out.push(H2("26. Finding 3 — Distribution of outcomes: the expectation is carried by a small minority"));
  out.push(...card([
    ["RESEARCH QUESTION", "What does an EV of ≈ $200 per attempt look like as a distribution?"],
    ["METHOD", "504-day continuous lifecycles (Table {{T:fm}}) and a 50,000-account run of the recommended combined policy (Combine 1:1 $1,500 → XFA day-one 3:1 all-in) recording net cash per attempt."],
    ["RESULT", `For the best static cells only 6–7 % of attempts end cash-positive (13–14 % at $300–500 risk; Table {{T:fm}}). For the recommended combined policy: mean ${$(N.fig13.mean_net)}, P(net > 0) = ${pct(N.fig13.p_net_pos)}, median ${$(N.fig13.p50)}, 5th percentile ${$(N.fig13.p5)}, 95th percentile ${$(N.fig13.p95)}.`],
    ["WHAT IT MEANS", "The typical attempt loses the subscription; about one in three loses the activation as well; roughly one in twelve pays out. Any live use is a portfolio of many attempts and must be sized to survive long runs of zero."],
    ["WHAT IT DOES NOT ESTABLISH", "Bankroll requirements or the effect of correlation across accounts (which changes variance, not the mean)."],
  ]));
  out.push(...figure(F + "fig13_net_distribution.png", "Net cash per attempt for the recommended combined policy. The mass at −$49 is failed Combines; at −$198 passed Combines whose XFA died on day one; the right tail is the ≈ 8 % of attempts that pass and pay out.", { key: "dist" }));

  // ---- Finding 4
  out.push(H2("27. Finding 4 — Edge convention: no effect on the ranking"));
  out.push(...card([
    ["RESEARCH QUESTION", "Does the choice between the exact drift convention and the linear approximation (§12) change any result on the edge ladder?"],
    ["METHOD", "Five profiles × six edges under both conventions with shared seeds; paired differences in net per attempt."],
    ["RESULT", `${N.ecIdentical} of ${N.ecPairs.length} cells are bit-identical; the largest difference is $${N.ecMaxDiff.toFixed(2)}, all non-zero differences sit at e ∈ {−0.10, −0.05}, and every cell at e ∈ {0, 0.02, 0.05} is identical to the last digit.`],
    ["WHAT IT MEANS", "The break-even edge e* per profile does not depend on the convention. The convention was nevertheless fixed and recorded before the non-zero-edge cells were run, because the argument that it does not matter is itself derived from results."],
    ["WHAT IT DOES NOT ESTABLISH", "That the drift model is the right process for real markets; it establishes only that the two candidate conventions cannot be told apart at the ladder's edge levels."],
  ]));

  // ---- Finding 5
  out.push(H2("28. Finding 5 — H3: the interior maximum in $ risk is the consistency rule"));
  out.push(...card([
    ["RESEARCH QUESTION", "Why does EV peak at an interior $ risk, and where?"],
    ["METHOD", "Sweep the consistency fraction over {0.40, 0.55, 0.70, 1.00 (inert)} at one trade a day for R ∈ {1, 1.5, 2, 3} and r up to $2,000 (N = 15,000), and read off the r at which EV peaks. Prediction if the peak is the consistency objective: the largest bet whose single-day win does not raise the target, R·r = frac × 3,000."],
    ["RESULT", `Peak R·r at frac 0.55: ${[1.5, 2, 3].map(r => fmt0(N.peaks[0.55][r].risk * r)).join(" / ")} for R = 1.5 / 2 / 3 (bound 1,650); at 0.40: ${[1.5, 2, 3].map(r => fmt0(N.peaks[0.4][r].risk * r)).join(" / ")} (bound 1,200); at 0.70: ${[1.5, 2, 3].map(r => fmt0(N.peaks[0.7][r].risk * r)).join(" / ")} (bound 2,100); with the rule inert: ${[1.5, 2, 3].map(r => fmt0(N.peaks[1][r].risk * r)).join(" / ")} (one win passes). For R = 1 the peak stays at r = $${fmt0(N.peaks[0.55][1].risk)} under every fraction.`],
    ["WHAT IT MEANS", "For R ≥ 1.5 the optimum is the largest bet whose single win stays under the consistency cap, and it slides with the cap. For R ≤ 1 the optimum is pinned by the loss floor: at r ≥ $1,750 one loss leaves less than one more loss of room above −$2,000. The ridge is min(consistency cap, floor cap). The recommended Combine profile sits on it."],
    ["WHAT IT DOES NOT ESTABLISH", "The peaks are read at $100–150 resolution and the surface has an integer sawtooth (the number of wins needed to reach $3,000), so the exact optimum within a slice is not resolved beyond that grain."],
  ]));
  out.push(...figure(F + "fig07_consistency_sweep.png", "Measured EV-peak location against the consistency bound. The three R ≥ 1.5 lines track the dashed bound; R = 1 stays on the floor cap.", { key: "sweep" }));
  out.push(...table(["frac", "bound frac × 3,000", "peak R·r (R = 1.5 / 2 / 3)", "peak r at R = 1"],
    [0.4, 0.55, 0.7, 1].map(f => [f.toFixed(2), fmt0(f * 3000), [1.5, 2, 3].map(r => fmt0(N.peaks[f][r].risk * r)).join(" / "), "$" + fmt0(N.peaks[f][1].risk)]),
    [1500, 2500, 3600, 2480], { key: "h3", caption: "H3 mechanism test (results_consistency_sweep.csv, N = 15,000; peak SE ≈ $2–3)" }));

  // ---- Finding 6
  out.push(H2("29. Finding 6 — State-dependent policies: the funded side has a closed-form optimum, the evaluation side does not move"));
  out.push(...card([
    ["RESEARCH QUESTION", "Can choosing R and $ risk from the account state beat the best static profile on either side?"],
    ["METHOD", "Policies of Eq. (" + E.pi + ") evaluated on the state engine at e = 0: for the XFA, build-then-harvest families, day-one all-in at R ∈ {1,2,3,5,8}, k consecutive all-ins, stop-after-payout; for the Combine, fill-the-gap, consistency-capped and lottery-then-fill. Results checked against Eq. (" + E.allin + ")."],
    ["RESULT", `XFA: the day-one all-in nets ${$(N.allinDay1(1, 150).cash)} / ${$(N.allinDay1(3, 150).cash)} / ${$(N.allinDay1(5, 150).cash)} / ${$(N.allinDay1(8, 150).cash)} at R = 1 / 3 / 5 / 8 (N = 20,000), against ${$(N.sp("static 2:1 $750").cash)} static — matching 0.9·2000·R/(1+R) to within noise at every R. The original build-then-harvest example (2:1 $1,000 then 1:1 $150) nets ${$(N.sp("build 2:1 $1000 -> harvest 1:1 $150 @B>=2000").cash)} with P(payout) ${pct(N.sp("build 2:1 $1000 -> harvest 1:1 $150 @B>=2000").p_payout, 0)} vs ${pct(N.sp("static 2:1 $750").p_payout, 0)}: same expectation, more payouts, lower variance. Combine: every state policy lands at 31–33 % except the 3:1 day-one lottery (${pct(N.spComb.find(r => r.policy.startsWith("day-1 3:1")).p_pass)}), versus 32.9 % static.`],
    ["WHAT IT MEANS", "H4 splits. On the XFA the whole value is in the first bet: minimise the ratchet leak by letting losing paths die before any lock. On the Combine the consistency rule punishes exactly the move that helps on the XFA, so the static ridge profile is already optimal to within noise."],
    ["WHAT IT DOES NOT ESTABLISH", "That the day-one bet is executable (Finding 8) or permitted: it is the clearest instance of the prohibited pattern (Part VII). The Combine result is strengthened to a proof in §19.1: no strategy can beat 16/49 by more than 0.06 points."],
  ]));
  out.push(...table(["Policy (XFA, Standard path)", "net $ / XFA", "SE", "P(payout)", "gross $", "payouts / acct"],
    ["static 2:1 $750", "static 1:1 $1500", "static 1:1 $150", "build 2:1 $1000 -> harvest 1:1 $150 @B>=2000", "build 2:1 $1000 -> harvest 1:1 $300 @B>=2000", "build 2:1 $1000 -> harvest 1:1 $150, stop after payout"].map(k => { const r = N.sp(k); return [r.policy, fmt0(r.cash), fmt0(r.se), pct(r.p_payout), fmt0(r.gross), r.payouts.toFixed(2)]; })
      .concat([1, 2, 3, 5, 8].map(rr => { const r = N.allinDay1(rr, 150); return [r.policy, fmt0(r.cash), fmt0(r.se), pct(r.p_payout), fmt0(r.gross), r.payouts.toFixed(2)]; })),
    [4300, 1200, 800, 1200, 1200, 1380], { key: "xfapol", caption: "XFA state-dependent policies at e = 0 (results_state_policy_xfa.csv, results_state_policy_xfa_allin.csv; N = 20,000)", size: 17, note: "Stopping after the first payout leaves the remaining balance unrealised and halves the result: the harvest is where the second half of the value is recovered." }));
  out.push(...figure(F + "fig10_xfa_allin.png", "Net per XFA for the day-one all-in against R (N = 100,000, results_final.csv), the analytic curve, the static baseline and the theoretical cap.", { key: "allin" }));
  out.push(p(`Repeated all-ins. Two consecutive all-ins on day one at 3:1 net ${$(N.allinK(3, 2).net)} (bound 2,000 × (1 − (1/4)²) = 1,875 gross), better than one (${$(N.allinK(3, 1).net)}); three collapse to ${$(N.allinK(3, 3).net)} because the surviving balance (≈ $126,000) cannot be withdrawn inside the horizon under the $2,000-per-cycle cap. The model wants as much day-one variance as the payout cap and horizon allow; the achievable point is fixed by constraints outside the contract (session volatility, contract caps, conduct rules), which is why Finding 8 exists.`));
  out.push(...table(["Combine policy", "P(pass)", "SE", "mean days"], N.spComb.map(r => [r.policy, pct(r.p_pass), pct(r.se, 2), fmt1(r.mean_days)]), [4600, 1600, 1600, 2280], { key: "combpol", caption: "Combine state-dependent policies at e = 0 (results_state_policy_combine.csv, N = 30,000)", size: 17 }));

  // ---- Finding 7
  out.push(H2("30. Finding 7 — Verification against the official rules, the horizon correction, and the DLL option"));
  out.push(...card([
    ["RESEARCH QUESTION", "Do the rules the engine implements match the firm's published rules, and do the funded-side conclusions survive them?"],
    ["METHOD", "Every parameter in Table {{T:inputs}} re-read on the official help centre (2026-09-20/21); discrepancies added to the engine as parameters with golden-path tests; affected experiments re-run. The funded all-in re-run with the net-profit rule at 250, 500 and 1,000-day horizons (optimality/results_horizon_frictions.csv), and with the optional daily loss limit (optimality/results_dll_funded.csv)."],
    ["RESULT", `Three corrections: (i) the Combine MLL locks at the starting balance — the project's frozen artifact A0 ratcheted without cap; (ii) later Standard-path payouts require net profit since the previous one — missing from A0's field list and from this engine's earlier copy, though the project's own E1 engine already enforced it; (iii) a $30 fee applies to ACH and wire payouts only. With the net-profit rule, the 250-day horizon binds at R ≥ 3: ${pct(1 - N.hz(5, 30, 250).p_closed, 1)} of 5:1 accounts are still open at 250 days; run to 1,000 days the 5:1 bet nets ${$(N.hz(5, 30, 1000).net)} against ${$(N.hz(3, 30, 1000).net)} for 3:1 (with the fee). The DLL doubles the Standard cap to $4,000 but gains only ${$(N.dllRow(3, "DLL-capped", 4000, true).net - N.dllRow(3, "single", 2000, true).net)} per XFA at 3:1 and ${$(N.dllRow(5, "DLL-capped", 4000, true).net - N.dllRow(5, "single", 2000, true).net)} at 5:1 (with frictions), because the 50 %-of-balance limit binds first.`],
    ["WHAT IT MEANS", "(i) binds only above $2,000 of balance: 7 of the 8 large-bet negative grid cells turned positive and the top profiles did not move. The earlier statement that 5:1 adds nothing over 3:1 once frictions are charged was an artefact of the one-year horizon: the net-profit rule costs time, not money. The DLL leaves the all-in identity intact (a losing day does not ratchet the floor) and is worth little at R ≤ 3."],
    ["WHAT IT DOES NOT ESTABLISH", "How the firm exercises discretion — that is Part VII — or anything at positive edge."],
  ]));
  out.push(...table(["Day-one bet", "net, no frictions", "net, with frictions (250 days)", "with frictions, 1,000 days", "per attempt, no frictions (exact 16/49)"],
    [1, 2, 3, 5].map(r => [r + ":1", `${$(N.allin[r])} ± ${fmt0(N.allinSE[r])}`, $(N.allinFr[r]), N.hz(r, 30, 1000) ? $(N.hz(r, 30, 1000).net) : "—", $(N.evExact(N.allin[r]))]),
    [1500, 2300, 2300, 2000, 1980], { key: "fric", caption: "Effect of the payout frictions on the zero-edge funded all-in (results_final.csv, results_horizon_frictions.csv; N = 100,000)", note: "Frictions = $30 per payout plus the net-profit-since-payout rule. The fee is avoidable (fee-free payout methods exist); the net-profit rule is not, and mainly delays payouts at high R. The 1:1 row was not re-run at 1,000 days." }));

  // ---- Finding 8
  out.push(H2("31. Finding 8 — The session time barrier would decide the zero-edge funded number"));
  out.push(...card([
    ["RESEARCH QUESTION", "The contract engine lets a $6,000 target resolve within a day. When the 15:10 CT flatten is a third exit, how large an R can the day-one bet actually realise?"],
    ["METHOD", "Eq. (" + E.session + ") with Brownian-bridge barrier detection; all-in repeated until B ≥ 2,000 or death; N = 20,000 per (s, R); harvest credited at measured efficiency. Validated by recovering the binary model as s → ∞ (R = 5, s = 8: P = 0.165 vs 1/6; gross $1,653 vs $1,667)."],
    ["RESULT", `Net per XFA (no frictions): s = 0.25 → ${$(N.tbRow(0.25, 1).net)}–${$(N.tbRow(0.25, 5).net)} regardless of R; s = 0.5 → ${$(N.tbRow(0.5, 2).net)}–${$(N.tbRow(0.5, 1).net)}; s = 1 → ${$(N.tbRow(1, 1).net)}–${$(N.tbRow(1, 3).net)}; s = 2 → ${$(N.tbRow(2, 3).net)} at R = 3; s = 4 → ${$(N.tbRow(4, 3).net)} / ${$(N.tbRow(4, 5).net)} at R = 3 / 5. Below s ≈ 0.75 the policy nets less than the static profile (${$(N.xfaStatic)}).`],
    ["WHAT IT MEANS", "If the maximum-size position cannot move about a cushion's worth in a session, the day-one bet degrades into a multi-day grind that ratchets, and the static profile is better. The funded-side answer is therefore conditional on one measurable number, s, which sits outside the contract."],
    ["WHAT IT DOES NOT ESTABLISH", "The value of s for any instrument: that is the Stage-2 measurement. It also assumes constant intra-session volatility (Assumption A8)."],
  ]));
  out.push(...figure(F + "fig11_timebarrier.png", "Net per XFA against s = session σ / cushion for the day-one all-in. The static fallback is the dotted line; the crossover is near s ≈ 0.75, and R only separates the lines from s ≈ 2 upward.", { key: "tb" }));
  out.push(...table(["s = σ_session / 2,000", "R = 1", "R = 2", "R = 3", "R = 5", "mean days to resolve (R = 3)"],
    [0.25, 0.5, 1, 2, 4, 8].map(s => [s.toString(), $(N.tbRow(s, 1).net), $(N.tbRow(s, 2).net), $(N.tbRow(s, 3).net), $(N.tbRow(s, 5).net), fmt1(N.tbRow(s, 3).mean_days)]),
    [2300, 1400, 1400, 1400, 1400, 2180], { key: "tbtab", caption: "Day-one all-in net per XFA under the session time barrier (results_timebarrier.csv, N = 20,000; SE $1–7)", note: "Binary-model limits: $900 / $1,200 / $1,350 / $1,500. The s = 8 row recovers them within noise." }));

  // ---- Final results
  out.push(H2("32. Zero-edge results in one table"));
  out.push(p("The table collects the zero-edge numbers the study stands on. EV per attempt uses the exact pass probability 16/49 and the exact expected subscription from the chain, rather than a Monte-Carlo pass rate. These are properties of the contract; Part VII explains why the campaign they describe cannot be run."));
  out.push(...table(["Quantity", "Value", "Basis"], [
    ["Combine profile", "static 1:1, $1,500, one trade per day (the ridge: R × $ risk ≈ $1,500)", "Findings 2, 5"],
    ["P(pass), exact", "16/49 = " + pct(N.exactP, 2), "Markov chain, Eq. (" + E.markov + ")"],
    ["P(pass), Monte Carlo", `${N.mcP.toFixed(5)} ± ${N.mcSE.toFixed(5)}`, `N = ${fmt0(N.mcN)}, z = ${N.mcZ >= 0 ? "+" : ""}${N.mcZ.toFixed(2)} (results_exact_chain_check.csv)`],
    ["Best possible over all strategies", `${N.sup(50, 0).sup_p_pass.toFixed(6)}`, "concave-envelope DP, Eq. (" + E.supremum + ")"],
    ["Mean trading days; subscription", `${fmt1(N.meanDays)} days; $49.00`, "N = 100,000"],
    ["XFA static profile", `2:1 $750 one trade/day: ${$(N.xfaStatic)} net`, "N = 100,000"],
    ["XFA day-one all-in, net", `${$(N.allin[1])} / ${$(N.allin[2])} / ${$(N.allin[3])} / ${$(N.allin[5])} at R = 1 / 2 / 3 / 5`, "analytic 900 / 1,200 / 1,350 / 1,500"],
    ["EV per attempt, static funded profile", $(N.evExact(N.xfaStatic)), "Eq. (" + E.evatt + ") with 16/49"],
    ["EV per attempt, 3:1 day-one all-in", $(N.evExact(N.allin[3])), "Eq. (" + E.evatt + ") with 16/49"],
    ["P(net > 0) per attempt", `${pct(N.fig13.p_net_pos)} (combined policy); 6–14 % (static cells)`, "N = 50,000; Table {{T:fm}}"],
    ["Analytic ceilings", "P(pass) ≤ 40 %; E[gross payouts] ≤ $2,000 (net ≤ $1,800)", "Eqs. (" + E.ceiling + "), (" + E.xceil + ")"],
  ], [3000, 4300, 2780], { key: "final", caption: "Zero-edge results", size: 18 }));
  return out;
}

module.exports = { partVI };
