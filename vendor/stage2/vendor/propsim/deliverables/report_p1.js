const L = require("./lib"); const N = require("./data");
const { run, p, rich, H1, H1n, H2, H3, pb, bullets, numbered, eq, table, card, callout, figure, NAVY, GREY, CONTENT_W } = L;
const { fmt0, fmt1, pct } = N;
const $ = (x) => "$" + fmt0(x);
const SUP = N.sup(50, 0).sup_p_pass;
const E10 = N.bestPair(0.10, "standard"), E05 = N.bestPair(0.05, "standard"), E02 = N.bestPair(0.02, "standard"), E20 = N.bestPair(0.20, "standard");
const BB = { 0.05: N.evBestBuffer(0.05), 0.10: N.evBestBuffer(0.10), 0.20: N.evBestBuffer(0.20) };

function frontMatter() {
  return [
    p("", { after: 2000 }),
    p([run("What the Topstep 50K Contract Does to a Trading Process — and What a Genuine Edge Is Worth Within Its Terms", { bold: true, size: 44, color: NAVY })], { after: 200, line: 560 }),
    p([run("A reproducible study of the evaluation (Combine) and funded (XFA) contracts: how their rules transform a declared trade process, the optimal risk-to-reward and dollar-risk geometry, why the zero-edge use of that geometry is prohibited, and how much a demonstrated edge is worth inside the firm's conduct rules", { size: 25, color: GREY })], { after: 400 }),
    p([run("Research document · propsim repository · final version, 21 September 2026", { size: 22, color: GREY })], { after: 80 }),
    p([run("Companion to the presentation of the same title. Every number in the presentation traces to a section, table or result file named here.", { size: 20, italics: true, color: GREY })], { after: 80 }),
    p([run("Status: repository CLOSED. The zero-edge campaign studied in Parts IV–VI is prohibited by the firm's terms (Part VII); those results describe what the contract does, not a plan to run that campaign. The next stage is research for a demonstrated edge (Part VIII and Part XI).", { size: 20, color: NAVY, bold: true })]),
    pb(),
    H1n("Executive Summary"),
    p("This document reconstructs, end to end, a study of the Topstep 50K Trading Combine and its Express Funded Account (XFA). It began with a narrow question: if a trader's outcomes are a fair coin, with no market edge at all, can the contract's asymmetric rules turn that process into positive expected cash, and which risk-to-reward (R:R) and dollar-risk profiles do it best on each stage? It ended with a different and more useful answer, because the firm's own terms turned out to prohibit exactly the campaign the zero-edge result relies on."),
    p("The study models nothing about markets. It declares a two-outcome trade process whose win probability is pinned by the R:R, so that expected profit per trade is exactly a chosen edge e (zero in the core analysis). It passes that process through an exact re-implementation of the contract's state machine, verified against the firm's official help-centre pages, and measures what comes out: pass probability, fees, funded-account payouts and net cash. The mathematics is exact where it can be: the balance is a martingale, so optional stopping gives hard ceilings; Markov chains give exact pass probabilities; and a concave-envelope dynamic program gives the best pass probability achievable by any strategy at all. Simulation is checked against every one of these."),
    ...callout("THE SIX RESULTS THAT MATTER", [
      `1. The contract has hard ceilings. Under a fair process no strategy passes the Combine more than 40 % of the time, and no funded account pays out more than $2,000 gross in expectation. The true best over all strategies is ${(100 * SUP).toFixed(2)} %, reached in two days; the simple profile 1:1 at $1,500 once a day passes with probability exactly 16/49 = ${pct(N.exactP, 2)}, 0.06 points below it.`,
      `2. At zero edge the contract alone is worth ${$(N.evExact(N.xfaStatic))}–${$(N.evExact(N.allin[3]))} per Combine attempt, but only about ${pct(N.fig13.p_net_pos, 0)} of attempts ever make money, and the value exists only because failed attempts are cheap and replaced.`,
      "3. That campaign is prohibited. Topstep's official Prohibited Trading Strategies page defines account stacking as repeatedly trading aggressively, hitting the loss limit, switching accounts and repeating until a large win occurs, and calls such items hard stops. Every zero-edge profile relies on exactly that pattern. The structural value is the prohibited mechanism, not a loophole around it.",
      `4. With a genuine edge the contract becomes an amplifier. Within the conduct constraints (winners larger than losers, modest size, one account at a time), the share of EV that comes from the edge rather than the structure is ${pct(E02.edge_share_of_ev, 0)} at a 2 % edge, ${pct(E05.edge_share_of_ev, 0)} at 5 %, ${pct(E10.edge_share_of_ev, 0)} at 10 % and ${pct(E20.edge_share_of_ev, 0)} at 20 %. Best structures: 2:1 at $750 at low edge, 1.5:1 at $500 from about 10 %.`,
      `5. On the funded side, payout policy matters as much as R:R. Any payout moves the floor to $0, so withdrawing early strands a small balance. Keeping a buffer (about $8,000 in the tests) roughly doubles realised cash per funded account; with it, EV per attempt is about ${$(BB[0.05].ev)}, ${$(BB[0.10].ev)} and ${$(BB[0.20].ev)} at 5, 10 and 20 % edge (exploratory result).`,
      `6. Proving an edge takes years of data. At one trade a day, demonstrating a 10 % edge with a meaningful lower bound needs ${fmt0(N.ss(1.5, 0.10).trades_lower_bound_above_half_edge)}–${fmt0(N.ss(3, 0.10).trades_lower_bound_above_half_edge)} trades (${N.ss(1.5, 0.10).years_at_1_per_day}–${N.ss(3, 0.10).years_at_1_per_day} years). The research stage must work from long historical tests; a short live record checks execution only.`]),
    p("Four findings concern the modelling itself and are as important as the numbers. The earlier project run model let trades lose past the loss floor; that overshoots the 40 % ceiling and inflated expected value by up to 2.5× (Finding 1). The frozen contract artifact lacked three official rules (Combine floor lock, net profit since the last payout, payout fee), now in the engine (Finding 7). A claim that high-R funded bets gain nothing once payout frictions are charged turned out to be an artefact of a one-year horizon: the net-profit rule costs time, not money (Finding 7). And a \"value per account-year\" metric silently rewards cycling through failed attempts, so it is never reported here without its churn (Part VIII)."),
    p("Reading order: question and hypotheses (Part I); definitions, inputs and assumptions (Part II); model architecture and mathematics (Part III); analytic bounds, exact results and the proven optimum (Part IV); computational and validation method (Part V); zero-edge results (Part VI); the conduct finding (Part VII); the value of a demonstrated edge (Part VIII); sensitivity (Part IX); interpretation and limitations (Part X); conclusions and the research-stage criterion (Part XI); appendices."),
    H1n("Abstract"),
    p(`We study how the Topstep 50K Combine and Express Funded Account transform a declared trade process, and what that implies for a trader. The rules (profit target $3,000; trailing end-of-day maximum loss limit $2,000 with real-time breach and a lock at the starting balance; 55 % consistency target; two payout paths with 50 %-of-balance and dollar caps; net profit required since the previous payout; 90/10 split; $49 subscription per billing period; $149 activation) are implemented as deterministic state machines. A binary process with win probability p = (1+e)/(1+R) supplies outcomes. Optional stopping bounds P(pass) ≤ 2/5 and E[gross payouts] ≤ $2,000; an exact Markov chain gives 16/49 for 1:1 $1,500; a concave-envelope dynamic program shows the supremum over all fair strategies is ${SUP.toFixed(6)}, unchanged by an optional daily loss limit. At zero edge the best profiles yield ${$(N.evExact(N.xfaStatic))}–${$(N.evExact(N.allin[3]))} per attempt, but the firm's official terms prohibit the fail-and-repurchase campaign that value requires (account stacking). We therefore value a demonstrated edge within conduct constraints: a pre-registered study with an exact chain validated against simulation (120 comparisons) shows the edge's share of EV rising from ${pct(E02.edge_share_of_ev, 0)} at e = 0.02 to ${pct(E10.edge_share_of_ev, 0)} at e = 0.10; exploratory runs show a payout buffer roughly doubles funded-account cash at positive edge. Demonstrating e ≈ 0.10 requires 1.7–3.5 thousand trades. We identify and correct a floor-overshoot error in a prior run model, three rule omissions, a horizon artefact and a churn-rewarding metric.`),
    pb(),
    p([run("Table of Contents", { bold: true, size: 36, color: NAVY, font: "Cambria" })], { after: 200 }),
    p("%%TOC%%"),
  ];
}

function partI() {
  return [
    H1("Part I — Research Question, Objective and Hypotheses"),
    H2("1. Research questions"),
    p("The study was designed around one question and, after the conduct terms were read, answers a second."),
    ...callout("RESEARCH QUESTIONS", [
      "Q1 (contract). Given a trading process with exactly zero expected profit per trade, what does the Topstep 50K contract — evaluation and funded stages together — do to it, and which risk-to-reward and dollar-risk profiles extract the most expected cash on each stage?",
      "Q2 (permitted use). Which uses of that geometry does the firm permit, and how much is a genuine, demonstrated edge worth inside those limits?"]),
    p("The objective for Q1 is a pair of profiles with exact numbers attached and the ceiling no profile can exceed. The objective for Q2 is a set of conduct-consistent profiles, a table of value against edge, and a specification the next research stage can test candidate strategies against."),
    H2("2. Why the contract is the object of study"),
    p("In a brokerage account a losing trade reduces capital and nothing else. In a prop-firm account the same loss can also move the account's legal state: it can breach the trailing maximum loss limit (MLL) and end the account, it can raise the profit target through the consistency rule, or it can leave the trader paying another subscription. A winning trade can move the floor up, inflate the target, or create payout eligibility. The account is a state machine with absorbing states and a fee clock, so identical trade outcomes can have very different cash consequences. That asymmetry is what makes it meaningful to ask what the contract does, independent of trading skill — and, as Part VII shows, it is also exactly what the firm's conduct rules are written to stop traders exploiting."),
    H2("3. Hypotheses"),
    ...table(["ID", "Hypothesis", "Status after this study"], [
      ["H1", "Under a zero-edge process the contract produces positive expected net cash per Combine attempt for at least one admissible static profile.", `Supported as a property of the contract (${N.posCells} of 160 grid cells positive), but the campaign it requires is prohibited (H6).`],
      ["H2", "Pass probability is materially different across profiles.", "Not supported: 24–33 % across the useful region; EV differences come from time and the consistency/floor geometry."],
      ["H3", "At fixed R and trades per day, expected value has an interior maximum in $ risk.", "Supported; mechanism identified: the consistency cap for R ≥ 1.5, the loss floor for R ≤ 1."],
      ["H4", "A state-dependent policy improves on the best static profile.", `Combine: no — and proven: the best possible is ${(100 * SUP).toFixed(2)} % against 32.65 %. XFA at zero edge: yes (day-one all-in), but excluded by H6.`],
      ["H5", "Correlated or hedged multi-account portfolios change expected cash.", "Rejected on theory (EV is additive); cross-account hedging is separately prohibited."],
      ["H6", "The zero-edge campaign is a permitted use of the contract.", "Rejected: it is the named account-stacking prohibition (Part VII)."],
      ["H7", "Within the conduct constraints, a genuine edge is amplified by the contract, and its share of EV grows with its size.", "Supported (Part VIII, pre-registered and validated)."],
    ], [700, 5000, 4380], { caption: "Hypotheses and their disposition", key: "hyp", size: 18 }),
    H2("4. Scope"),
    p("Inside scope: the Combine and XFA rules as published; a declared binary trade process with a stated edge; fees; day structure; both payout paths; state-dependent policies; the conduct terms as they bear on the geometry; and, as one deliberate step outside the contract, a session time barrier. Outside scope: any market model, strategy or alpha research, instrument selection, contract-size feasibility, commissions (treated only as part of the edge), operations, and any campaign design built on repeated failure (Part VII)."),
    p("The distinction the document rests on: the engine answers what the rules do to a declared process. It does not answer what process a real trading system can generate. That is the next stage's question, and Part XI states what it must demonstrate."),
  ];
}

function partII() {
  return [
    H1("Part II — Definitions, Inputs and Assumptions"),
    H2("5. Definitions of terms and variables"),
    ...table(["Term / symbol", "Definition", "Type"], [
      ["Combine", "Topstep's evaluation account. Pass by reaching the profit target under the loss and consistency rules; $49 per billing period.", "contract"],
      ["XFA", "Express Funded Account, entered on passing after a $149 activation. Balance starts at 0; payouts are real cash.", "contract"],
      ["B", "Balance: cumulative net P&L from 0.", "state"],
      ["F", "Current loss floor (MLL), balance-relative. Starts −2,000, ratchets at the lock, locks at 0; in the XFA also set to 0 after any payout.", "state"],
      ["c = B − F", "Room: the dollar loss the account can absorb before liquidation.", "derived"],
      ["D, B_d", "Today's P&L; best completed day.", "state"],
      ["R, r, W", "Reward multiple; dollar risk per trade; dollar win W = R·r.", "policy / derived"],
      ["e", "Edge: expected P&L per trade as a fraction of $ risked, after costs. e = 0 is exact break-even.", "declared"],
      ["p", "Win probability of a trade: p = (1+e)/(1+R).", "derived"],
      ["Attempt", "One Combine purchase through to failure, or pass then XFA closure. Net cash = 0.9 × payouts − activation − subscriptions − payout fees.", "output"],
      ["Structural EV", "Expected cash per attempt at e = 0: the value the contract's asymmetry creates without any edge. Its exploitation through repeated failed attempts is prohibited (Part VII).", "output"],
      ["Edge share", "(EV at edge e − structural EV) ÷ EV at edge e.", "output"],
      ["Buffer (keep_balance)", "Funded-account payout rule: request only what leaves at least this balance in the account.", "policy"],
      ["s", "Session volatility ratio: session σ of the max-size position's P&L ÷ $2,000 (used for the zero-edge all-in only).", "external"],
      ["Truncate / resize / none", "Conventions for a trade whose stop lies beyond the room (§11).", "model"],
    ], [2000, 6680, 1400], { caption: "Vocabulary and variables used throughout", key: "vocab", size: 18 }),
    H2("6. Contract inputs and their provenance"),
    p("Every parameter the engine reads is listed in Table {{T:inputs}} with its source. All were read on the firm's official help-centre pages on 20–21 September 2026; items marked ADDED were missing from the project's earlier frozen contract artifact (A0) or from this engine's earlier copy."),
    ...table(["Parameter", "Value used", "Provenance", "Status"], [
      ["Profit target / MLL", "$3,000 / $2,000 trailing end-of-day, breach in real time incl. unrealised P&L", "8284197 / 8284204", "confirmed"],
      ["MLL lock", "the floor never rises above the starting balance (\"once it reaches your starting balance, it locks permanently\")", "8284204 (live 2026-09-21, marked updated that week)", "ADDED to the Combine engine; A0 lacked it"],
      ["Consistency target", "best day ≤ 55 % of profit, else target = best day ÷ 0.55", "8284208", "confirmed (third-party guides say 50 %)"],
      ["Fees", "$49 subscription per billing period (source: every 30 days; modelled as 21 trading days); $149 activation", "8284121 / pricing", "confirmed; convention D-31"],
      ["XFA MLL", "−$2,000 → locks at 0 → $0 after any payout", "8284204 / 8284233", "confirmed"],
      ["Standard payout path", "5 winning days ≥ $150; ≤ 50 % of balance; cap $2,000; minimum $125; 90/10", "8284233", "confirmed"],
      ["Net profit since last payout", "later Standard payouts need > $0 net since the previous one; first payout exempt", "8284233", "ADDED to propsim (missing from A0's field list; already enforced by the project's E1 engine)"],
      ["Consistency payout path", "≥ 3 trading days; best day ≤ 40 % of window profit; cap $3,000", "8284233 / 8284208", "confirmed"],
      ["Payout fee", "$30 for ACH and wire; none for Aeropay, Prop-to-Brokerage, Wise (some regions)", "8284233", "ADDED as an optional friction; avoidable"],
      ["Daily Loss Limit option", "$1,000 (50K); fixed if set at Combine checkout; applies in the XFA; doubles payout caps ($4,000 / $6,000) as a limited-time offer", "10490293 / 8284233", "modelled as a sensitivity (Finding 7)"],
      ["Account limits", "Combines unlimited; up to 5 active XFAs, further passes on hold; Back2Funded ≤ 2", "8284197 / 8284121 / 8284215", "confirmed"],
      ["Prohibited conduct", "account stacking; \"not a viable strategy\" catch-all; cross-account hedging; SIM-fill exploitation", "10305426 / 10296582", "analysed in Part VII"],
      ["Responsible Trading Program", "placement after Risk Team review for unsustainable or high-risk patterns; new XFAs Consistency-path only; Combines carry a DLL", "13620045", "analysed in Parts VII–VIII"],
    ], [1900, 3500, 2300, 2380], { caption: "Contract inputs, values, provenance and verification status", key: "inputs", size: 16, tight: true, keep: false, note: "Numbers are help-centre article identifiers (help.topstep.com/en/articles/…). The rules were revised several times between late 2025 and mid-2026 and should be re-verified before any use." }),
    H2("7. Assumptions"),
    p("Observed inputs are the contract values in Table {{T:inputs}}. Everything else the model needs but the contract does not state is listed here by kind."),
    ...table(["#", "Assumption", "Kind", "Effect if wrong"], [
      ["A1", "Two-point trades: win +R·r or lose −r, independent, with p = (1+e)/(1+R).", "declared process", "Defines the object of study; not a market claim."],
      ["A2", "Every account trades every trading day; trades per day is a policy variable.", "modelling", "Changes time to resolution and subscription drag; explored."],
      ["A3", "A stop beyond the room is liquidated at the floor with the barrier-race probability (truncate).", "derived from the contract", "The alternative ('none') is shown to be an error (Finding 1)."],
      ["A4", "For e ≠ 0, edge is a constant drift per unit variance fixed at the trade's own stop and target.", "additional modelling", "Numerically indistinguishable from the first-order alternative (Finding 4)."],
      ["A5", "Zero-edge analysis: payouts taken at eligibility for the full allowed amount. Edge analysis: also a buffer rule.", "policy", "At positive edge this matters a great deal (Part VIII)."],
      ["A6", "XFA horizon 250 trading days in the zero-edge grid; up to 1,000 where the net-profit rule binds; 252 and 504 in Part VIII.", "modelling", "Binds at R ≥ 3 with the net-profit rule (Finding 7)."],
      ["A7", "Commissions and slippage enter only through e (net edge).", "declared scope", "The research stage must measure them."],
      ["A8", "The session time-barrier model treats intra-session P&L as Brownian with one volatility parameter.", "additional; zero-edge all-in only", "Used to map the all-in onto a measurable quantity."],
      ["A9", "Exact-at-stop fills.", "modelling", "Real fills slip; relying on SIM stop fills is itself prohibited. A real edge must survive realistic fills."],
      ["A10", "Conduct constraints (Part VII) are applied as selection rules, not modelled as firm behaviour.", "scope", "The firm's discretion is not predictable; the constraints follow its stated criteria."],
    ], [500, 4600, 2200, 2780], { caption: "Assumptions by kind", key: "assumptions", size: 17 }),
  ];
}

module.exports = { frontMatter, partI, partII };
