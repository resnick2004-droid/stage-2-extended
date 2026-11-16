const fs = require("fs");
const P = __dirname + "/../";
function csv(path) {
  const lines = fs.readFileSync(path, "utf8").trim().split("\n"); const h = lines[0].split(",");
  const split = (l) => { const out = []; let cur = "", q = false; for (const ch of l) { if (ch === '"') q = !q; else if (ch === "," && !q) { out.push(cur); cur = ""; } else cur += ch; } out.push(cur); return out; };
  return lines.slice(1).map(l => { const v = split(l); const o = {}; h.forEach((k, i) => { const x = v[i]; o[k] = x === "" || isNaN(Number(x)) ? x : Number(x); }); return o; });
}
const fmt0 = (x) => Math.round(x).toLocaleString("en-US");
const fmt1 = (x) => (Math.round(x * 10) / 10).toFixed(1);
const pct = (x, d = 1) => (100 * x).toFixed(d) + " %";

const grid = csv(P + "results_grid_edge0.csv");
const ladder = csv(P + "results_edge_ladder.csv");
const floorModes = csv(P + "results_floor_mode_504.csv");
const edgeConv = csv(P + "results_edge_convention.csv");
const cons = csv(P + "results_consistency_sweep.csv");
const spXfa = csv(P + "results_state_policy_xfa.csv");
const spAllin = csv(P + "results_state_policy_xfa_allin.csv");
const spK = csv(P + "results_state_policy_xfa_kallin.csv");
const spComb = csv(P + "results_state_policy_combine.csv");
const tb = csv(P + "results_timebarrier.csv");
const fin = csv(P + "results_final.csv");
const chainCheck = csv(P + "results_exact_chain_check.csv")[0];
const combEdge = csv(P + "edge/results_combine_edge.csv");
const voe = csv(P + "edge/results_value_of_edge.csv").map(r => ({ ...r, admissible: String(r.admissible) === "True", exploratory: String(r.exploratory) === "True" }));
const buffer = csv(P + "edge/results_payout_buffer_exploratory.csv").concat(csv(P + "edge/results_payout_buffer_extension.csv"));
const sampleSize = csv(P + "edge/results_sample_size.csv");
const horizon = csv(P + "optimality/results_horizon_frictions.csv").map(r => ({ ...r, net_positive_rule: String(r.net_positive_rule) === "True" }));
const dll = csv(P + "optimality/results_dll_funded.csv").map(r => ({ ...r, frictions: String(r.frictions) === "True" }));
const supremum = csv(P + "optimality/results_combine_supremum.csv");
const trace = Object.fromEntries(csv(P + "bankroll/results_payout_trace_2to1.csv").map(r => [r[Object.keys(r)[0]], r.value]));
const validationT5 = fs.readFileSync(P + "edge/validation_T5.txt", "utf8");
const t4 = fs.readFileSync(P + "optimality/results_t4_check2_propsim.txt", "utf8");
const fig13 = csv(__dirname + "/figs/fig13_stats.csv");

const z = fin.find(r => r.edge === 0);
const topEV = [...grid].sort((a, b) => b.best_ev - a.best_ev).slice(0, 5);
const topPass = [...grid].sort((a, b) => b.c_p_pass - a.c_p_pass).slice(0, 5);
const posCells = grid.filter(r => r.best_ev > 0).length;
const negByRisk = {}; grid.filter(r => r.best_ev <= 0).forEach(r => { negByRisk[r.risk] = (negByRisk[r.risk] || 0) + 1; });
const cell = (rr, risk, rule) => grid.find(r => r.rr === rr && r.risk === risk && r.day_rule === rule);
const maxPass = Math.max(...grid.map(r => r.c_p_pass));
const maxGross = Math.max(...grid.map(r => Math.max(r.xstd_mean_gross, r.xcons_mean_gross)));

// consistency-sweep peaks
const peaks = {};
for (const frac of [0.4, 0.55, 0.7, 1.0]) { peaks[frac] = {}; for (const rr of [1, 1.5, 2, 3]) { const s = cons.filter(r => r.frac === frac && r.rr === rr); const best = s.reduce((a, b) => b.ev > a.ev ? b : a); peaks[frac][rr] = best; } }

// floor modes summary
const fmCells = [...new Set(floorModes.map(r => `${r.rr}|${r.risk}|${r.day_rule}`))];
const fmRows = fmCells.map(k => { const [rr, risk, rule] = k.split("|"); const g = (m) => floorModes.find(r => r.rr === +rr && r.risk === +risk && r.day_rule === rule && r.mode === m); return { rr: +rr, risk: +risk, rule, none: g("none"), trunc: g("truncate"), resize: g("resize") }; });

// edge-convention summary
const ecPairs = []; const keys = [...new Set(edgeConv.map(r => `${r.rr}|${r.risk}|${r.day_rule}|${r.edge}`))];
for (const k of keys) { const [rr, risk, rule, e] = k.split("|"); const d = edgeConv.find(r => r.rr === +rr && r.risk === +risk && r.day_rule === rule && r.edge === +e && r.edge_mode === "drift"); const l = edgeConv.find(r => r.rr === +rr && r.risk === +risk && r.day_rule === rule && r.edge === +e && r.edge_mode === "linear"); if (d && l) ecPairs.push({ rr: +rr, risk: +risk, rule, edge: +e, drift: d.net_per_attempt, linear: l.net_per_attempt, diff: d.net_per_attempt - l.net_per_attempt, se: Math.sqrt(d.net_se ** 2 + l.net_se ** 2) }); }
const ecIdentical = ecPairs.filter(x => Math.abs(x.diff) < 1e-9).length;
const ecMaxDiff = Math.max(...ecPairs.map(x => Math.abs(x.diff)));

// state policies
const sp = (name) => spXfa.find(r => r.policy.startsWith(name));
const allin = (rr, k) => spK.find(r => r.rr === rr && r.allins === k);
const allinDay1 = (rr, r2) => spAllin.find(r => r.policy.startsWith(`day-1 bet ${rr}:1 $2000 -> harvest 1:1 $${r2}`));

// time barrier
const tbRow = (s, rr) => tb.find(r => Math.abs(r.sigma_over_cushion - s) < 1e-9 && r.rr === rr);

const N = {
  exactP: 16 / 49, mcP: chainCheck.mc_p_pass, mcSE: chainCheck.se, mcN: chainCheck.N, mcZ: chainCheck.z, mc100k: z.c_p_pass, mc100kSE: z.c_p_pass_se, meanDays: z.c_mean_days,
  xfaStatic: z.xfa_static_net, xfaStaticFr: z.xfa_static_net_frictions, evStatic: z.ev_attempt_static, evStaticFr: z.ev_attempt_static_frictions,
  allin: { 1: z.allin_1to1, 2: z.allin_2to1, 3: z.allin_3to1, 5: z.allin_5to1 }, allinFr: { 1: z.allin_1to1_frictions, 2: z.allin_2to1_frictions, 3: z.allin_3to1_frictions, 5: z.allin_5to1_frictions },
  allinSE: { 1: z.allin_1to1_se, 2: z.allin_2to1_se, 3: z.allin_3to1_se, 5: z.allin_5to1_se },
  evAllin: { 1: z.ev_attempt_allin_1to1, 2: z.ev_attempt_allin_2to1, 3: z.ev_attempt_allin_3to1, 5: z.ev_attempt_allin_5to1 },
  evAllinFr: { 1: z.ev_attempt_allin_1to1_frictions, 2: z.ev_attempt_allin_2to1_frictions, 3: z.ev_attempt_allin_3to1_frictions, 5: z.ev_attempt_allin_5to1_frictions },
  posCells, negByRisk, topEV, topPass, maxPass, maxGross, cell, peaks, fmRows, ecPairs, ecIdentical, ecMaxDiff, sp, allinK: allin, allinDay1, spK, tbRow, tb, fin, ladder, cons, spComb, spXfa, spAllin, fig13: Object.fromEntries(fig13.map(r => [r.stat, r.value])),
  // --- edge stage (T5) and audit follow-ups
  combEdge, voe, buffer, sampleSize, horizon, dll, supremum, trace, validationT5, t4,
  ce: (R, risk, e) => combEdge.find(r => r.R === R && r.risk === risk && Math.abs(r.edge - e) < 1e-9),
  bestPair: (e, path) => voe.filter(r => r.path === path && r.admissible && !r.exploratory && Math.abs(r.edge - e) < 1e-9).reduce((a, b) => b.ev_per_attempt > a.ev_per_attempt ? b : a),
  pairRow: (e, path, c, x) => voe.find(r => r.path === path && r.combine_profile === c && r.xfa_profile === x && Math.abs(r.edge - e) < 1e-9),
  buf: (R, risk, e, k) => buffer.find(r => r.R === R && r.risk === risk && Math.abs(r.edge - e) < 1e-9 && r.keep_balance === k),
  bestBuf: (e) => buffer.filter(r => Math.abs(r.edge - e) < 1e-9).reduce((a, b) => b.cash_per_year > a.cash_per_year ? b : a),
  bestTakeMax: (e) => buffer.filter(r => Math.abs(r.edge - e) < 1e-9 && r.keep_balance === 0).reduce((a, b) => b.cash_per_year > a.cash_per_year ? b : a),
  hz: (R, fee, H) => horizon.find(r => r.R === R && r.fee === fee && r.net_positive_rule && r.horizon === H),
  dllRow: (R, policy, cap, fr) => dll.find(r => r.R === R && r.policy.startsWith(policy) && r.cap === cap && r.frictions === fr),
  sup: (h, dllv) => supremum.find(r => r.grid_step === h && r.dll === dllv),
  ss: (R, e) => sampleSize.find(r => r.R === R && Math.abs(r.true_edge - e) < 1e-9),
  evExact: (xfaNet) => (16 / 49) * (xfaNet - 149) - combEdge.find(r => r.R === 1 && r.risk === 1500 && r.edge === 0).mean_sub,
  evBestBuffer: (e) => { const b = buffer.filter(r => Math.abs(r.edge - e) < 1e-9).reduce((a, c) => c.cash_per_year > a.cash_per_year ? c : a);
    const cands = combEdge.filter(r => Math.abs(r.edge - e) < 1e-9 && !(r.R === 1 && r.risk === 1500));
    const best = cands.map(c => ({ c, ev: c.p_pass * (2 * b.cash_per_year - 149) - c.mean_sub })).reduce((a, c) => c.ev > a.ev ? c : a);
    return { ev: best.ev, combine: `${best.c.R}:1 $${best.c.risk}`, p_pass: best.c.p_pass, funded: b, funded2y: 2 * b.cash_per_year }; },
  fmt0, fmt1, pct,
};
module.exports = N;
