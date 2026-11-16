const pptxgen = require("pptxgenjs"); const fs = require("fs");
const N = require("./data"); const { fmt0, fmt1, pct } = N;
const F = __dirname + "/figs/";
const NAVY = "14343B", TEAL = "2E7D8C", AMBER = "D9822B", GREY = "5F6B6D", LIGHT = "E8EEF0", PALE = "F4F7F8", RED = "B3412E", WHITE = "FFFFFF", GREEN = "3E7C4A";
const HF = "Cambria", BF = "Calibri";
const pres = new pptxgen(); pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
const STUDY = "Topstep 50K contract study — final version";
let n = 0;
const $ = (x) => "$" + fmt0(x);

function frame(kicker, narrative, title, source) {
  const s = pres.addSlide(); n += 1; s.background = { color: WHITE };
  s.addText([{ text: kicker.toUpperCase() + "     ", options: { bold: true, color: TEAL, fontSize: 10, charSpacing: 1 } }, { text: narrative, options: { italic: true, color: GREY, fontSize: 10 } }],
    { x: 0.5, y: 0.28, w: 12.3, h: 0.3, fontFace: BF, isTextBox: true, margin: 0 });
  s.addText(title, { x: 0.5, y: 0.6, w: 12.3, h: 0.7, fontFace: HF, fontSize: 28, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  if (source) s.addText("Source: " + source, { x: 0.5, y: 6.85, w: 8.5, h: 0.3, fontFace: BF, fontSize: 9, italic: true, color: GREY, isTextBox: true, margin: 0 });
  s.addText(STUDY, { x: 0.5, y: 7.1, w: 10, h: 0.25, fontFace: BF, fontSize: 8, color: GREY, isTextBox: true, margin: 0 });
  s.addText(String(n), { x: 12.3, y: 7.1, w: 0.5, h: 0.25, fontFace: BF, fontSize: 8, color: GREY, align: "right", isTextBox: true, margin: 0 });
  return s;
}
function bulletsBox(s, items, x, y, w, h, fs = 13) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 6 } })), { x, y, w, h, fontFace: BF, fontSize: fs, color: "222222", valign: "top", isTextBox: true, margin: 2 });
}
function card(s, x, y, w, h, title, body, fill = PALE, fs = 12, titleColor = NAVY) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: LIGHT, width: 0.75 }, rectRadius: 0.08 });
  s.addText(title, { x: x + 0.15, y: y + 0.1, w: w - 0.3, h: 0.35, fontFace: BF, fontSize: 12, bold: true, color: titleColor, isTextBox: true, margin: 0 });
  s.addText(body, { x: x + 0.15, y: y + 0.45, w: w - 0.3, h: h - 0.55, fontFace: BF, fontSize: fs, color: "222222", valign: "top", isTextBox: true, margin: 0 });
}
function eqBox(s, x, y, w, text, num) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h: 0.5, fill: { color: PALE }, line: { color: LIGHT, width: 0.75 } });
  s.addText(text, { x: x + 0.1, y, w: w - 0.9, h: 0.5, fontFace: "Cambria Math", fontSize: 14, color: NAVY, valign: "middle", isTextBox: true, margin: 0 });
  if (num) s.addText("(" + num + ")", { x: x + w - 0.8, y, w: 0.7, h: 0.5, fontFace: BF, fontSize: 10, color: GREY, align: "right", valign: "middle", isTextBox: true, margin: 0 });
}
function stat(s, x, y, w, big, label, color = NAVY) {
  s.addText(big, { x, y, w, h: 0.9, fontFace: HF, fontSize: 40, bold: true, color, align: "center", isTextBox: true, margin: 0 });
  s.addText(label, { x, y: y + 0.9, w, h: 0.6, fontFace: BF, fontSize: 11, color: GREY, align: "center", valign: "top", isTextBox: true, margin: 0 });
}
function tbl(s, header, rows, x, y, w, colW, fs = 10, rowH) {
  const hdr = header.map(h => ({ text: h, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: fs, fontFace: BF, valign: "middle" } }));
  const body = rows.map((r, i) => r.map(c => ({ text: String(c), options: { fontSize: fs, fontFace: BF, color: "222222", fill: { color: i % 2 ? PALE : WHITE }, valign: "middle" } })));
  s.addTable([hdr, ...body], { x, y, w, colW, border: { type: "solid", pt: 0.5, color: "C9D3D6" }, margin: 0.05, rowH });
}
function dbox(s, x, y, w, h, title, body, fill = PALE, line = NAVY, tc = NAVY, bodyFs = 10.5) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: line, width: 1.25 }, rectRadius: 0.06 });
  s.addText([{ text: title, options: { bold: true, fontSize: 11.5, color: tc, breakLine: true } }, { text: body, options: { fontSize: bodyFs, color: tc } }],
    { x: x + 0.05, y, w: w - 0.1, h, fontFace: BF, align: "center", valign: "middle", isTextBox: true, margin: 0 });
}
function arr(s, x1, y1, x2, y2, color = NAVY, width = 1.5, dash) {
  const o = { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), line: { color, width, endArrowType: "triangle" } };
  if (dash) o.line.dashType = dash;
  if (x2 < x1) o.flipH = true; if (y2 < y1) o.flipV = true;
  s.addShape(pres.shapes.LINE, o);
}
function lbl(s, text, x, y, w, color = NAVY, fs = 9.5, align = "center") { s.addText(text, { x, y, w, h: 0.3, fontFace: BF, fontSize: fs, color, align, valign: "middle", isTextBox: true, margin: 0 }); }
const ALT = {
  "s_barrier_race.png": "Price path racing a target at +W against a floor at -c that sits closer than the chosen stop -r",
  "s_ev_heatmap.png": "Heatmap of expected net dollars per attempt by R:R and dollar risk, one and three trades per day",
  "fig16_payout_buffer.png": "Realised cash per funded account per year against the buffer kept in the account, at 10 and 20 percent edge",
  "s_net_distribution.png": "Log-scale histogram of net cash per attempt: mass at -$49 and -$198, long right tail of payouts",
};
function img(s, file, x, y, w, h) { s.addImage({ path: F + file, x, y, w, h, altText: ALT[file] || file.replace(/[_.]/g, " "), sizing: { type: "contain", w, h } }); }
const chartBase = (title) => ({ showTitle: true, title, titleFontFace: BF, titleFontSize: 12, titleColor: NAVY, catAxisLabelColor: GREY, valAxisLabelColor: GREY, catAxisLabelFontSize: 10, valAxisLabelFontSize: 10, valGridLine: { color: "E3E8EA", size: 0.5 }, catGridLine: { style: "none" }, showLegend: true, legendFontSize: 10, legendColor: GREY, legendPos: "b", chartColors: [NAVY, TEAL, AMBER, RED, GREY] });

// ================= NEW 1 Title
{
  const s = pres.addSlide(); n += 1; s.background = { color: NAVY };
  s.addText("What the Topstep 50K Contract Does to a Trading Process — and What a Genuine Edge Is Worth Within Its Terms", { x: 0.7, y: 1.1, w: 11.9, h: 1.9, fontFace: HF, fontSize: 32, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText("Contract geometry, proven optima, the conduct finding, and the value of a demonstrated edge", { x: 0.7, y: 3.1, w: 11.5, h: 0.6, fontFace: BF, fontSize: 17, color: "CADCE0", isTextBox: true, margin: 0 });
  s.addText("A reproducible study: question → assumptions → inputs → model → mathematics → calculations → results → interpretation → limitations", { x: 0.7, y: 3.8, w: 11.5, h: 0.5, fontFace: BF, fontSize: 12, italic: true, color: "9FB7BD", isTextBox: true, margin: 0 });
  s.addText("propsim repository · final version, 21 September 2026 · companion to the research document (every number traces to a section, table or result file)", { x: 0.7, y: 5.5, w: 11.9, h: 0.4, fontFace: BF, fontSize: 11, color: "CADCE0", isTextBox: true, margin: 0 });
  s.addText("Status: CLOSED. The zero-edge campaign is prohibited by the firm's terms (account stacking); the next stage is research for a demonstrated edge", { x: 0.7, y: 5.95, w: 11.9, h: 0.5, fontFace: BF, fontSize: 12, bold: true, color: AMBER, isTextBox: true, margin: 0 });
}
// ================= NEW 2 Research questions
{
  const s = frame("The research questions", "The study was built around one question and, after reading the firm's terms, answers a second.", "What does the contract do — and what may a trader actually use?", "Research document Part I §1");
  card(s, 0.5, 1.6, 5.9, 2.7, "Q1 — the contract", "Given a trade process with exactly zero expected profit, what does the Topstep 50K contract (Combine + funded account) do to it, and which R:R and $-risk profiles extract the most on each stage?", PALE, 15);
  card(s, 6.9, 1.6, 5.9, 2.7, "Q2 — permitted use", "Which uses of that geometry does the firm permit, and how much is a genuine, demonstrated edge worth inside those limits?", "DCEBEE", 15);
  bulletsBox(s, ["The account is a state machine, not a P&L summary: a loss can end it, a win can raise its floor or its target, and every month costs a fee.",
    "That asymmetry is what the contract study measures — and exactly what the firm's conduct rules are written to stop traders exploiting.",
    "Nothing about markets is modelled: the trade process is declared, with a stated edge e."], 0.5, 4.6, 12.3, 2.0, 14);
}
// ================= NEW 3 Hypotheses
{
  const s = frame("Hypotheses", "Seven testable statements, each with the verdict the analysis returned.", "Hypotheses and verdicts", "Research document Part I §3, Table {{T:hyp}}");
  tbl(s, ["ID", "Hypothesis", "Verdict"], [
    ["H1", "At zero edge the contract yields positive expected cash per attempt", `Supported as a contract property (${N.posCells} of 160 cells) — but see H6`],
    ["H2", "Pass probability differs materially across profiles", "Not supported: 24–33 %; time and geometry drive EV"],
    ["H3", "EV has an interior maximum in $ risk", "Supported: consistency cap (R ≥ 1.5) or floor (R ≤ 1)"],
    ["H4", "A state-dependent policy beats the best static one", `Combine: no — proven optimum ${(100 * N.sup(50, 0).sup_p_pass).toFixed(2)} % vs 32.65 %. Funded: yes at e = 0, but excluded`],
    ["H5", "Hedged / correlated portfolios change expected cash", "Rejected: EV is additive; hedging is prohibited anyway"],
    ["H6", "The zero-edge campaign is a permitted use", "Rejected: it is the named account-stacking prohibition"],
    ["H7", "Within the conduct rules a genuine edge is amplified", "Supported (pre-registered, validated)"],
  ], 0.5, 1.5, 12.3, [0.6, 5.9, 5.8], 12, 0.62);
}
// ================= 4 Framework
{
  const s = frame("Research framework", "The model is a pipeline; every box is a separately testable component.", "Architecture: policy → fair generator → Combine → XFA → cash", "Research document Part III §8, Figure {{F:arch}}");
  const Y1 = 1.7, H1 = 1.5;
  dbox(s, 0.5, Y1, 1.5, H1, "POLICY", "(R, $ risk, day rule)\nstatic or state-\ndependent π(S)", "FBEFE3", AMBER);
  dbox(s, 2.45, Y1, 1.5, H1, "FAIR GENERATOR", "p = (1+e)/(1+R)\nwin +R·r, lose −r\nthe only random step");
  dbox(s, 4.4, Y1, 1.7, H1, "COMBINE", "floor ratchet · 0.55 rule\nintraday liquidation\npass / fail", "DCEBEE", TEAL);
  dbox(s, 6.55, Y1, 1.7, H1, "XFA", "floor −2,000 → 0\npayout paths · caps\nclosed / paid", "DCEBEE", TEAL);
  dbox(s, 8.7, Y1, 0.9, H1, "CASH", "0.9 q\n− fees", NAVY, NAVY, WHITE);
  arr(s, 2.0, Y1 + 0.75, 2.45, Y1 + 0.75); arr(s, 3.95, Y1 + 0.75, 4.4, Y1 + 0.75); arr(s, 6.1, Y1 + 0.75, 6.55, Y1 + 0.75); arr(s, 8.25, Y1 + 0.75, 8.7, Y1 + 0.75);
  lbl(s, "(R, r)", 1.72, Y1 - 0.32, 1.0, GREY); lbl(s, "P&L sequence", 3.55, Y1 - 0.32, 1.25, GREY); lbl(s, "pass (+$149)", 5.7, Y1 - 0.32, 1.25, GREY);
  const Y2 = 4.35, H2 = 1.45;
  dbox(s, 0.5, Y2, 2.05, H2, "ANALYTIC BOUNDS", "P(pass) ≤ 2/5\nE[gross] ≤ $2,000\n16/49 exact chain", "FBEFE3", AMBER);
  dbox(s, 2.85, Y2, 2.05, H2, "FEE CLOCK", "$49 per 21 trading days\nactivation $149\nreset $49", WHITE, GREY);
  dbox(s, 5.2, Y2, 2.05, H2, "FLOOR CONVENTION", "truncate at room c\np = c/(c+W) at e = 0\ndrift θ for e ≠ 0", WHITE, GREY);
  dbox(s, 7.55, Y2, 2.05, H2, "SESSION BARRIER", "zero-edge all-in only\n15:10 CT flatten\nσ_session ÷ cushion", WHITE, GREY);
  // connector rail from the support layer into both state machines
  s.addShape(pres.shapes.LINE, { x: 1.525, y: 3.85, w: 7.05, h: 0, line: { color: GREY, width: 1 } });
  for (const cx of [1.525, 3.875, 6.225, 8.575]) s.addShape(pres.shapes.LINE, { x: cx, y: 3.85, w: 0, h: 0.5, line: { color: GREY, width: 1 } });
  arr(s, 5.25, 3.85, 5.25, Y1 + H1, GREY, 1.25); arr(s, 7.4, 3.85, 7.4, Y1 + H1, GREY, 1.25);
  lbl(s, "bounds run as oracles", 4.0, 3.95, 2.1, GREY, 9, "left");
  bulletsBox(s, ["Only the generator is random; every other box is deterministic given its inputs.", "Golden-path tests validate the contract on scripted outcome sequences before any Monte Carlo runs.", "The fee clock and floor convention feed both state machines; the session barrier is used in one Stage-2 experiment only.", "The analytic bounds (Part IV) run as oracles on every Monte-Carlo cell."], 10.0, 1.7, 2.8, 4.9, 12);
}
// ================= NEW 5 Inputs
{
  const s = frame("Inputs", "Every parameter the engine reads, from the firm's official help centre (read 20–21 September 2026).", "Contract inputs and their provenance", "Research document Part II §6, Table {{T:inputs}}");
  tbl(s, ["Parameter", "Value", "Source (article)", "Status"], [
    ["Profit target / loss limit", "$3,000 / $2,000 trailing end-of-day, breach in real time", "8284197 / 8284204", "confirmed"],
    ["Loss-limit lock", "floor never rises above the starting balance", "8284204", "added (A0 lacked it)"],
    ["Consistency", "best day ≤ 55 % of profit, else target = best ÷ 0.55", "8284208", "confirmed"],
    ["Fees", "$49 per billing period (modelled as 21 trading days); $149 activation", "8284121", "confirmed"],
    ["Funded payouts", "5 winning days ≥ $150; ≤ 50 % of balance; cap $2,000; min $125; 90/10", "8284233", "confirmed"],
    ["Profit since last payout", "> $0 required for later payouts; first exempt", "8284233", "added to propsim"],
    ["Payout fee", "$30 ACH/wire only; free methods exist", "8284233", "optional friction"],
    ["Daily Loss Limit option", "$1,000; doubles caps (limited-time offer)", "10490293 / 8284233", "sensitivity"],
    ["Account limits", "Combines unlimited; ≤ 5 funded, more on hold", "8284197 / 8284215", "confirmed"],
    ["Conduct", "account stacking; \"not a viable strategy\"; hedging; SIM fills", "10305426 / 10296582", "Part VII"],
  ], 0.5, 1.5, 12.3, [2.4, 5.0, 2.3, 2.6], 11, 0.44);
}
// ================= NEW 6 Assumptions
{
  const s = frame("Assumptions", "Separated by kind so that no assumption is mistaken for an observed input.", "What the model assumes beyond the contract", "Research document Part II §7, Table {{T:assumptions}}");
  card(s, 0.5, 1.5, 4.0, 2.4, "Declared process (A1)", "Two-point trades: win +R·r or lose −r, independent, p = (1+e)/(1+R). e is after costs. Not a market claim.", PALE, 13);
  card(s, 4.65, 1.5, 4.0, 2.4, "From the contract (A3)", "Real-time breach ⇒ a stop beyond the room is a barrier race: liquidate at the floor with p = c/(c+W).", "DCEBEE", 13);
  card(s, 8.8, 1.5, 4.0, 2.4, "Additional modelling (A4, A8)", "Edge as constant drift per unit variance. Session barrier for the zero-edge all-in only.", "FBEFE3", 13);
  card(s, 0.5, 4.1, 4.0, 2.4, "Policy (A2, A5)", "One trade a day in the edge study. Payouts at eligibility; at positive edge also a buffer rule.", PALE, 13);
  card(s, 4.65, 4.1, 4.0, 2.4, "Fills (A9)", "Exact at the stop. Real fills slip, and relying on SIM stop fills is itself prohibited — a real edge must survive realistic fills.", PALE, 13);
  card(s, 8.8, 4.1, 4.0, 2.4, "Conduct (A10)", "The firm's stated criteria are applied as selection rules; its discretion is not modelled.", "F6DEDA", 13);
}
// ================= 7 Generator
{
  const s = frame("Mathematical framework — the generator", "Win rate is never a free parameter; it is the price of the R:R.", "The fair trade generator: win probability is pinned by R", "Research document Part III §9, Eqs. ({{E:p}})–({{E:ev}})");
  eqBox(s, 0.5, 1.55, 6.0, "p = (1 + e) / (1 + R)", "{{E:p}}");
  eqBox(s, 0.5, 2.2, 6.0, "E[X] = p·R·r − (1 − p)·r = e·r", "{{E:ev}}");
  s.addText("p win probability; R reward multiple; r $ risk; e declared edge (expected P&L per trade as a fraction of r). Worked: R = 2, e = 0 → p = 1/3; a $750 risk wins $1,500 one time in three: E[X] = (1/3)(1,500) − (2/3)(750) = 0.", { x: 0.5, y: 2.85, w: 6.0, h: 1.4, fontFace: BF, fontSize: 12, color: "222222", isTextBox: true, margin: 0 });
  s.addChart(pres.charts.BAR, [{ name: "p at e = 0", labels: ["0.5:1", "1:1", "1.5:1", "2:1", "3:1", "5:1", "8:1"], values: [0.667, 0.5, 0.4, 0.333, 0.25, 0.167, 0.111] }],
    { x: 6.9, y: 1.5, w: 5.9, h: 4.9, ...chartBase("Fair win probability implied by R (Table {{T:pwin}})"), showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 9, dataLabelFormatCode: "0.00", showLegend: false, chartColors: [NAVY], valAxisMaxVal: 0.8, catAxisTitle: "R:R", showCatAxisTitle: true, catAxisTitleFontSize: 9 });
  bulletsBox(s, ["Every profile in the grid is compared at identical expected profit per trade.", "The generator knows only (R, r, e); it never sees the account. This is what lets the same machinery serve the project's rules engine."], 0.5, 4.4, 6.0, 2.2, 13);
}
// ================= 8 Combine SM
{
  const s = frame("How the model works — Combine", "Trades act intraday; the floor, best day and pass test act only at the 16:00 lock.", "The Combine state machine: S = (B, F, D, B_d)", "Research document Part III §10, Eqs. ({{E:sc}})–({{E:lock}}), Figure {{F:sm}}");
  dbox(s, 2.9, 1.5, 3.0, 1.25, "ACTIVE", "trade: B += X, D += X\nbreach test after every fill", "DCEBEE", TEAL, NAVY, 11);
  dbox(s, 2.9, 3.4, 3.0, 1.3, "16:00 CT LOCK", "B_d ← max(B_d, D)\nF ← min(0, max(F, B − 2000))\npass test, then D = 0", WHITE, GREY, NAVY, 10.5);
  dbox(s, 0.5, 3.4, 1.9, 1.3, "FAILED", "B ≤ F intraday\nlands exactly on F\n(reset $49 = new attempt)", "F6DEDA", RED, NAVY, 10.5);
  dbox(s, 6.4, 3.4, 1.9, 1.3, "PASSED", "B ≥ max(3000, B_d/0.55)\nat the lock\n→ XFA (+$149)", "E1EFDF", GREEN, NAVY, 10.5);
  arr(s, 4.1, 2.75, 4.1, 3.4); lbl(s, "end of day", 4.2, 2.9, 1.0, GREY, 9.5, "left");
  arr(s, 4.9, 3.4, 4.9, 2.75, GREY); lbl(s, "else next day (+$49 / 21 d)", 5.0, 2.9, 1.9, GREY, 9.5, "left");
  arr(s, 2.9, 2.35, 1.45, 3.4, RED); lbl(s, "B ≤ F", 1.5, 2.55, 0.8, RED, 9.5);
  arr(s, 5.9, 4.05, 6.4, 4.05, GREEN);
  eqBox(s, 0.5, 5.05, 12.3, "Trade:   B ← B + X;   D ← D + X;   FAIL if B ≤ F   (after every fill)", 4);
  eqBox(s, 0.5, 5.7, 12.3, "Lock:   B_d ← max(B_d, D);   F ← min(0, max(F, B − 2000));   PASS if B ≥ max(3000, B_d / 0.55)", 5);
  bulletsBox(s, ["A single-day profit above $1,650 raises the target (1,650 / 0.55 = 3,000).", "The best day is measured on the day it occurs, so a pass never happens on the best day itself: the minimum path is two days (+1,650 then +1,350).", "Fee clock: $49 at day 0 and every 21 trading days; $149 on passing.", "The floor never rises above $0 (official lock rule).", "All four facts are pinned by golden-path tests."], 8.7, 1.5, 4.1, 3.4, 12);
}
// ================= 9 Floor race
{
  const s = frame("How the model works — floor liquidation", "The firm liquidates the instant equity touches the floor, so a stop beyond the room is not a stop.", "A trade with the floor closer than its stop is a barrier race", "Research document Part III §11, Eqs. ({{E:trunc}})–({{E:mae}}), Figure {{F:race}}");
  img(s, "s_barrier_race.png", 0.5, 1.45, 6.6, 3.05);
  eqBox(s, 0.5, 5.0, 6.6, "c = min(r, B − F);   P(win | room c) = c / (c + W)", 6);
  eqBox(s, 0.5, 5.65, 6.6, "P(MAE ≥ c | win) = W (r − c) / ( r (c + W) )", "{{E:mae}}");
  card(s, 7.4, 1.5, 5.4, 2.3, "Worked example", "Risk $1,500 at 1:1 with $500 of room: c = 500, W = 1,500 → P(win) = 500 / 2,000 = 25 % (not 50 %), loss if it loses = $500 (not $1,500). E[X] = 0.25 × 1,500 − 0.75 × 500 = 0: still fair.", PALE, 12);
  card(s, 7.4, 3.95, 5.4, 2.6, "Why Eq. ({{E:mae}}) exists", "The project's generator may not see the balance and its rules engine may not use randomness. Emitting each trade's maximum adverse excursion from this parameter-free law lets the existing liquidation logic reproduce c/(c+W) exactly (identity proven to 1e−12). It is a martingale consequence, not measured market excursion.", "DCEBEE", 11);
}
// ================= 10 XFA SM
{
  const s = frame("How the model works — XFA", "The funded account pays real cash; a payout is a state transition, not just a withdrawal.", "The XFA state machine: eligibility, request, floor to zero", "Research document Part III §13, Eqs. ({{E:sx}})–({{E:payout}})");
  eqBox(s, 0.5, 1.5, 12.3, "Lock:  F ← min(0, max(F, B − 2000));  w += 1 if D ≥ 150;  window profit Π, best Π_best, days N_d updated", 12);
  eqBox(s, 0.5, 2.1, 12.3, "Eligible:  Standard  w ≥ 5 ∧ (¬paid ∨ Π_since > 0)      Consistency  N_d ≥ 3 ∧ Π > 0 ∧ Π_best ≤ 0.4 Π", "{{E:elig}}");
  eqBox(s, 0.5, 2.7, 12.3, "Payout:  q = min(0.5 B, cap);  if q ≥ 125:  B ← B − q,  C ← C + 0.9 q − f,  F ← 0,  window ← ∅", 14);
  tbl(s, ["Day", "P&L", "B after", "F after lock", "w", "Event"], [
    ["1", "+300", "300", "−1,700", "1", ""], ["2", "+300", "600", "−1,400", "2", ""], ["3", "+300", "900", "−1,100", "3", ""], ["4", "+300", "1,200", "−800", "4", ""],
    ["5", "+300", "1,500", "→ 0", "5", "eligible; q = min(750, 2,000) = 750; cash 675; B = 750"], ["6", "−750", "0", "0", "—", "B ≤ F: closed"],
  ], 0.5, 3.45, 7.6, [0.6, 0.8, 1.0, 1.2, 0.5, 3.5], 11, 0.45);
  card(s, 8.4, 3.45, 4.4, 3.2, "What the payout did to the state", "After the request the trader holds $750 above a floor of $0 in a fair game. The most they can ever expect to extract from what remains is $750. The cushion that made the account valuable is gone the moment the first payout is taken — and it was already being eaten by the ratchet on the way up.", "FBEFE3", 12);
}
// ================= 11 Bounds
{
  const s = frame("Mathematical framework — bounds", "Before any simulation: the balance is a martingale, so optional stopping gives ceilings no policy can beat.", "Two ceilings and the identity that organises the funded side", "Research document Part IV §16–17, Eqs. ({{E:ceiling}})–({{E:leak}})");
  stat(s, 0.5, 1.5, 4.0, "≤ 2/5", "Combine pass probability under any fair process\n3000·P ≤ 2000·(1 − P)");
  stat(s, 4.65, 1.5, 4.0, "≤ $2,000", "expected gross XFA payouts\nE[Q] ≤ −E[F_τ] ≤ 2000  (Fatou on T = B + Q)");
  stat(s, 8.8, 1.5, 4.0, "$1,800", "net cap after the 90/10 split\napproached as R → ∞", AMBER);
  eqBox(s, 0.5, 3.6, 12.3, "E[Q] = ( 1 − P(payout) ) × ( 2000 − E[ratchet | no payout] )", "{{E:leak}}");
  bulletsBox(s, ["In a fair game the expected amount you can walk away with equals the expected amount you are allowed to lose for free. Every rule that shrinks the free loss — the end-of-day ratchet, the jump of the floor to $0 after a payout — shrinks extraction one for one.",
    `Worked on the best static XFA profile (2:1 $750): P(payout) = ${pct(N.sp("static 2:1 $750").p_payout, 1)}, E[Q] = ${$(N.sp("static 2:1 $750").gross)} ⇒ losing paths had ${$(2000 - N.sp("static 2:1 $750").gross / (1 - N.sp("static 2:1 $750").p_payout))} of cushion eaten by the ratchet before they died. That is the leak the funded policy must minimise.`,
    "Both ceilings run as oracles on every Monte-Carlo cell."], 0.5, 4.3, 12.3, 2.5, 14);
}
// ================= 12 Exact chain
{
  const s = frame("Mathematical framework — exact result", "For the recommended Combine profile the chain has four transient states and can be solved by hand.", "P(pass) = 16/49 for 1:1, $1,500, one trade a day", "Research document Part IV §19, Eq. ({{E:markov}}), Figure {{F:markov}}");
  const bw = 2.0, bh = 1.05;
  dbox(s, 0.5, 1.55, bw, bh, "D (start)", "B = 0, F = −2,000\nroom 2,000, bet 1,500, p = ½", PALE, NAVY, NAVY, 10);
  dbox(s, 3.4, 1.55, bw, bh, "A", "B = 1,500, F = −500\nroom 2,000, bet 1,500, p = ½", PALE, NAVY, NAVY, 10);
  dbox(s, 6.3, 1.55, bw, bh, "PASS", "B = 3,000", "E1EFDF", GREEN, NAVY, 11);
  dbox(s, 0.5, 3.55, bw, bh, "B′", "B = −1,500, F = −2,000\nroom 500 → bet 500, p = ¼", PALE, NAVY, NAVY, 10);
  dbox(s, 3.4, 3.55, bw, bh, "C", "B = 0, F = −500\nroom 500 → bet 500, p = ¼", PALE, NAVY, NAVY, 10);
  dbox(s, 6.3, 3.55, bw, bh, "FAIL", "B = F", "F6DEDA", RED, NAVY, 11);
  arr(s, 2.5, 2.07, 3.4, 2.07); lbl(s, "win ½", 2.5, 1.72, 0.9, NAVY);
  arr(s, 5.4, 2.07, 6.3, 2.07, GREEN); lbl(s, "win ½", 5.4, 1.72, 0.9, GREEN);
  arr(s, 1.0, 2.6, 1.0, 3.55, RED); lbl(s, "lose ½", 0.4, 2.95, 0.7, RED, 9.5, "left");
  arr(s, 3.9, 2.6, 3.9, 3.55, RED); lbl(s, "lose ½", 3.3, 2.95, 0.7, RED, 9.5, "left");
  arr(s, 2.0, 3.55, 2.0, 2.6); lbl(s, "win ¼", 2.05, 2.95, 0.7, NAVY, 9.5, "left");
  arr(s, 4.9, 3.55, 4.9, 2.6); lbl(s, "win ¼", 4.95, 2.95, 0.7, NAVY, 9.5, "left");
  arr(s, 5.4, 4.07, 6.3, 4.07, RED); lbl(s, "lose ¾", 5.4, 3.72, 0.9, RED);
  s.addShape(pres.shapes.LINE, { x: 1.5, y: 4.6, w: 0, h: 0.35, line: { color: RED, width: 1.5 } });
  s.addShape(pres.shapes.LINE, { x: 1.5, y: 4.95, w: 5.8, h: 0, line: { color: RED, width: 1.5 } });
  arr(s, 7.3, 4.95, 7.3, 4.6, RED); lbl(s, "lose ¾", 3.4, 4.98, 2.0, RED);
  eqBox(s, 0.5, 5.5, 7.8, "a = ½ + ½c,  c = ¼a,  d = ½a + ½b′,  b′ = ¼d  ⇒  a = 4/7,  d = 16/49", "{{E:markov}}");
  card(s, 8.7, 1.5, 4.1, 4.6, "Checks", `Monte Carlo: ${N.mcP.toFixed(5)} ± ${N.mcSE.toFixed(5)} at N = ${fmt0(N.mcN)} (z = ${N.mcZ >= 0 ? "+" : ""}${N.mcZ.toFixed(2)}).\n\nFair-game conservation: 16/49 × 3,000 − 21/49 × 2,000 − 12/49 × 500 = 0.\n\nConsistency rule never binds (1,500 / 0.55 = 2,727 < 3,000): the profile sits on the H3 ridge.\n\nFloor lock never binds (balance ≤ $1,500 before the passing trade), so the rule correction leaves 16/49 unchanged.`, PALE, 12.5);
}
// ================= NEW 13 Proven optimum
{
  const s = frame("Mathematical framework — the optimum", "Is 16/49 just the best of the policies tried, or close to the best possible?", "No strategy can beat 16/49 by more than 0.06 points", "Research document Part IV §19.1, Eq. ({{E:supremum}}); optimality/results_combine_supremum.csv");
  eqBox(s, 0.5, 1.55, 12.3, "V(B, F, B_d) = cav_x [ g(x) ](B):  best pass probability = concave envelope of next-day values over end-of-day balances x ≥ F", "{{E:supremum}}");
  stat(s, 0.5, 2.4, 3.9, N.sup(50, 0).sup_p_pass.toFixed(4), "best possible over ALL fair strategies\n(concave-envelope dynamic program)");
  stat(s, 4.7, 2.4, 3.9, "0.3265", "1:1 $1,500 once a day\n(exactly 16/49)", TEAL);
  stat(s, 8.9, 2.4, 3.9, N.sup(50, 1000).sup_p_pass.toFixed(4), "with the $1,000 daily loss limit\n(unchanged)", AMBER);
  bulletsBox(s, ["Why it works: within a day, a fair process can end at any mix of balances with the right average, as long as it stays at or above the floor. So the best achievable value is a concave envelope, iterated until it stops changing.",
    "Attained in two days: close day one at +$1,350 or +$1,650 risking the full $2,000, then race the remainder. Multi-day strategies add nothing.",
    "Validated: grid refinement from $500 to $50; simulation of the optimal policy. First run z = +3.15 (fail), diagnosed as chance; five further seeds pooled to z = +1.13.",
    "The solver's first version returned exactly 0.40 — end-of-day mass below the floor. The ceiling oracle caught it."], 0.5, 4.2, 12.3, 2.5, 12);
}
// ================= NEW 14 Methods
{
  const s = frame("Modelling / simulation process", "Seeded, vectorised, exact where possible, pre-registered where it matters.", "Computational method and validation", "Research document Part V §20–23, Table {{T:register}}");
  tbl(s, ["Experiment", "What varies", "N / method", "Feeds"], [
    ["Static grid", "R × $ risk × day rule × payout path (160 cells)", "10,000", "Findings 2, 5"],
    ["Floor / edge conventions", "none / truncate / resize; drift vs linear", "paired seeds", "Findings 1, 4"],
    ["State policies + supremum", "all-in, fill-the-gap; concave-envelope DP", "20–40k; exact", "Finding 6, §19.1"],
    ["Rules, horizon, DLL", "floor lock, profit-since-payout, 250–1,000 days", "100,000", "Finding 7"],
    ["Value of edge (pre-registered)", "10 profiles × 6 edges × 2 paths", "exact chain + MC", "Part VIII"],
    ["Payout buffer (exploratory)", "funded size × edge × buffer", "40–50k", "Part VIII"],
  ], 0.5, 1.5, 7.6, [2.1, 3.1, 1.3, 1.1], 11, 0.62);
  card(s, 8.4, 1.5, 4.4, 2.5, "33 automated tests", "Golden paths from the rule text · analytic oracles (ceilings, martingale) · exact identities (16/49, liquidation identity, θ solver) · sampler checks. The deterministic machine is validated before any random run.", PALE, 12);
  card(s, 8.4, 4.15, 4.4, 2.5, "Pre-registration & failure protocol", "Criteria written before running. A failed check is kept on record and diagnosed: terminal states → stage decomposition → component in isolation → fresh-seed replication. Never rerun until it passes.", "DCEBEE", 12);
}
// ================= 14 Finding 1
{
  const s = frame("Finding 1 — floor overshoot", "The earlier run model let a trade lose past the floor. That manufactures pass probability.", "Letting trades overshoot the floor inflated EV by up to 2.5×", "Research document Part VI §24, Table {{T:fm}}; results_floor_mode_504.csv");
  const labels = N.fmRows.map(r => `${r.rr}:1 $${r.risk} ${r.rule}`);
  s.addChart(pres.charts.BAR, [
    { name: "none (gate 1.8)", labels, values: N.fmRows.map(r => +r.none.net_per_attempt.toFixed(0)) },
    { name: "truncate (contract)", labels, values: N.fmRows.map(r => +r.trunc.net_per_attempt.toFixed(0)) },
    { name: "resize (policy)", labels, values: N.fmRows.map(r => +r.resize.net_per_attempt.toFixed(0)) },
  ], { x: 0.5, y: 1.45, w: 8.0, h: 5.2, ...chartBase("Net $ per attempt, 504-day lifecycle, seeds shared (N = 20,000)"), chartColors: [RED, NAVY, TEAL], showValue: false, catAxisLabelFontSize: 8, valAxisTitle: "$ per attempt", showValAxisTitle: true, valAxisTitleFontSize: 9 });
  bulletsBox(s, ["1:1 $1,500 under 'none' passes with probability exactly 4/9 = 44.4 %, above the 40 % ceiling; failures land at −$3,000.", "Under truncate: 16/49 = 32.7 %.", "'none' inflates 8 of 9 cells by 1.13×–2.45×; neutral in one.", "Truncate and resize agree within noise everywhere: both are fair; truncate is the contract rule, resize a solver choice.", "The ceiling oracle is what caught it."], 8.8, 1.5, 4.0, 5.2, 11);
}
// ================= 15 Finding 2 grid
{
  const s = frame("Finding 2 — the static grid", "160 profiles at zero edge. Pass probability is flat; time and geometry decide EV.", `EV is positive in ${N.posCells} of 160 cells; the ridge is R × $ risk ≈ $1,500`, "Research document Part VI §25, Figures {{F:passmap}}–{{F:evmap}}, Table {{T:top5}}; results_grid_edge0.csv");
  img(s, "s_ev_heatmap.png", 0.5, 1.45, 8.6, 3.45);
  tbl(s, ["R:R", "$ risk", "day rule", "P(pass)", "days", "EV / attempt"], N.topEV.slice(0, 4).map(r => [r.rr + ":1", "$" + r.risk, r.day_rule, pct(r.c_p_pass), fmt1(r.c_mean_days), $(r.best_ev)]), 0.5, 5.15, 8.6, [0.9, 1.1, 2.0, 1.4, 1.2, 2.0], 10, 0.3);
  bulletsBox(s, [`Maximum pass probability ${pct(N.maxPass)} against a 40 % ceiling; 24–33 % across the useful region.`, `Negative band at $50–$500 is the fee clock: a $50 bet takes ${fmt0(N.cell(1, 50, "1/day").c_mean_days)} trading days to resolve and pays ${$(N.cell(1, 50, "1/day").c_mean_sub_fees)} in subscriptions.`, "Large single-day wins inflate the target; the surface turns over on the right.", "H1 supported, H2 not."], 9.4, 1.5, 3.4, 5.1, 11);
}
// ================= 16 ridge chart
{
  const s = frame("Finding 2 — the ridge", "Every line rises out of the subscription region, peaks, and turns over.", "EV against $ risk at one trade a day", "Research document Part VI §25, Figure {{F:ridge}}; results_grid_edge0.csv");
  const g = require("./data");
  const risks = [50, 100, 200, 300, 500, 750, 1000, 1500];
  const series = [0.5, 1, 1.5, 2, 3].map(rr => ({ name: `R = ${rr}:1`, labels: risks.map(r => "$" + r), values: risks.map(r => +Math.max(-450, g.cell(rr, r, "1/day").best_ev).toFixed(0)) }));
  s.addChart(pres.charts.LINE, series, { x: 0.5, y: 1.45, w: 8.4, h: 5.2, ...chartBase("Expected net $ per attempt (values below −450 clipped for scale)"), lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 5, valAxisTitle: "$ per attempt", showValAxisTitle: true, valAxisTitleFontSize: 9, catAxisTitle: "$ risk per trade", showCatAxisTitle: true, catAxisTitleFontSize: 9 });
  bulletsBox(s, ["Peaks: R = 1 at $1,500; 1.5 at $1,000; 2 at $750; 3 at $500 — the product R × $ risk ≈ $1,500 in every case.", "That constant is the subject of Finding 5.", "The surface has an integer sawtooth (wins needed to reach $3,000), so peaks are read at $100–150 grain."], 9.2, 1.5, 3.6, 5.0, 12);
}
// ================= 17 Finding 5 H3
{
  const s = frame("Finding 5 — H3 mechanism", "If the ridge is the consistency objective it must move when the fraction is swept. It does.", "The interior maximum in $ risk is the consistency cap", "Research document Part VI §28, Table {{T:h3}}, Figure {{F:sweep}}; results_consistency_sweep.csv");
  const fr = [0.4, 0.55, 0.7, 1.0];
  const series = [1.5, 2, 3].map(rr => ({ name: `measured peak R·r, R = ${rr}:1`, labels: fr.map(String), values: fr.map(f => N.peaks[f][rr].risk * rr) }));
  series.push({ name: "bound frac × 3,000", labels: fr.map(String), values: fr.map(f => f * 3000) });
  series.push({ name: "R = 1 peak r (floor-capped)", labels: fr.map(String), values: fr.map(f => N.peaks[f][1].risk) });
  s.addChart(pres.charts.LINE, series, { x: 0.5, y: 1.45, w: 8.0, h: 5.2, ...chartBase("EV-peak location vs consistency fraction (N = 15,000; peak SE $2–3)"), chartColors: [TEAL, AMBER, RED, GREY, NAVY], lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 6, catAxisTitle: "consistency_max_day_frac", showCatAxisTitle: true, catAxisTitleFontSize: 9, valAxisTitle: "R × $ risk at the peak", showValAxisTitle: true, valAxisTitleFontSize: 9 });
  bulletsBox(s, ["For R ≥ 1.5 the optimum is the largest bet whose single win stays under frac × 3,000, and it slides with the fraction. Rule inert → peak jumps to R·r = 3,000 ('one win passes').", "For R = 1 the peak is pinned at $1,500 under every fraction: at r ≥ $1,750 one loss leaves less than one more loss of room above −$2,000.", "Ridge = min(consistency cap, floor cap). The recommended Combine profile sits on it."], 8.8, 1.5, 4.0, 5.2, 11);
}
// ================= 18 Finding 6 XFA
{
  const s = frame("Finding 6 — the funded optimum (zero edge)", "The clearest case of the prohibited pattern (Part VII) — shown to explain the contract, not to be traded.", "One day-one bet on the full cushion: net = 0.9·2,000·R/(1+R)", "Research document Part VI §29, Eq. ({{E:allin}}), Table {{T:xfapol}}, Figure {{F:allin}}; results_final.csv (N = 100,000)");
  const Rs = [1, 2, 3, 5];
  s.addChart(pres.charts.LINE, [
    { name: "measured, no frictions", labels: Rs.map(r => r + ":1"), values: Rs.map(r => +N.allin[r].toFixed(0)) },
    { name: "measured, with frictions", labels: Rs.map(r => r + ":1"), values: Rs.map(r => +N.allinFr[r].toFixed(0)) },
    { name: "analytic 0.9·2000·R/(1+R)", labels: Rs.map(r => r + ":1"), values: Rs.map(r => +(1800 * r / (1 + r)).toFixed(0)) },
    { name: "best static (2:1 $750)", labels: Rs.map(r => r + ":1"), values: Rs.map(() => +N.xfaStatic.toFixed(0)) },
  ], { x: 0.5, y: 1.45, w: 7.6, h: 3.7, ...chartBase("Net $ per XFA against R of the day-one bet"), chartColors: [NAVY, AMBER, GREY, TEAL], lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 6, valAxisMinVal: 600, valAxisMaxVal: 1800, catAxisTitle: "R of the day-one bet", showCatAxisTitle: true, catAxisTitleFontSize: 9 });
  tbl(s, ["R", "measured", "with frictions", "analytic 1800·R/(1+R)", "SE"], Rs.map(r => [r + ":1", $(N.allin[r]), $(N.allinFr[r]), $(1800 * r / (1 + r)), "± " + fmt0(N.allinSE[r])]), 0.5, 5.3, 7.6, [0.8, 1.5, 1.7, 2.4, 1.2], 10.5, 0.27);
  card(s, 8.4, 1.5, 4.4, 2.3, "Why it works", "With probability R/(1+R) the bet loses and the account dies at −$2,000 with zero ratchet, contributing the full cushion to −E[F_τ]. With probability 1/(1+R) the balance is 2,000R, the floor locks at 0, and the harvest recovers the balance in expectation, paid out over several weeks in withdrawals capped at 50 % of the balance and $2,000.", PALE, 11);
  card(s, 8.4, 3.95, 4.4, 2.7, "What the harvest cannot change", `Harvest size ($150 vs $300 vs $500), trades per day and horizon make no difference. 'Build 2:1 $1,000 then harvest' nets ${$(N.sp("build 2:1 $1000 -> harvest 1:1 $150 @B>=2000").cash)} — the static EV with P(payout) ${pct(N.sp("build 2:1 $1000 -> harvest 1:1 $150 @B>=2000").p_payout, 0)} instead of ${pct(N.sp("static 2:1 $750").p_payout, 0)}: it reshapes the distribution, not the mean. Two consecutive all-ins beat one (${$(N.allinK(3, 2).net)} vs ${$(N.allinK(3, 1).net)} at 3:1); three collapse (${$(N.allinK(3, 3).net)}) under the payout cap.`, "DCEBEE", 10.5);
}
// ================= 19 Finding 6 Combine
{
  const s = frame("Finding 6 — the evaluation side", "The move that helps on the XFA is exactly what the consistency rule punishes on the Combine.", "No state-dependent Combine policy beats the static ridge profile", "Research document Part VI §29, Table {{T:combpol}}; results_state_policy_combine.csv (N = 30,000)");
  tbl(s, ["Combine policy", "P(pass)", "SE", "mean days"], N.spComb.map(r => [r.policy, pct(r.p_pass), pct(r.se, 2), fmt1(r.mean_days)]), 0.5, 1.5, 7.8, [4.2, 1.2, 1.2, 1.2], 12, 0.5);
  card(s, 8.6, 1.5, 4.2, 5.0, "Reading the table", `Every fill-the-gap and lottery variant lands at 30–33 %, the same as static 1:1 $1,500 (${pct(N.spComb[0].p_pass)}). The 3:1 day-one lottery drops to ${pct(N.spComb.find(r => r.policy.startsWith("day-1 3:1")).p_pass)}: a $6,000 first day sets target_eff = $10,909.\n\nThe Combine already sits at 32.7 % against a 40 % ceiling; the remaining gap is rule structure (55 % consistency + ratchet), not profile choice — and §19.1 proves no strategy can beat 16/49 by more than 0.06 points.\n\nH4 therefore splits: XFA yes, Combine no.`, PALE, 11);
}
// ================= NEW 20 Finding 7
{
  const s = frame("Finding 7 — rules, horizon, DLL", "Official rules re-read; three corrections, one withdrawn claim, one option priced.", "Three rule corrections, a horizon artefact, and the DLL option", "Research document Part VI §30, Table {{T:fric}}; results_horizon_frictions.csv, results_dll_funded.csv");
  tbl(s, ["Item", "Finding", "Effect"], [
    ["Combine loss-limit lock", "floor locks at the starting balance (A0 ratcheted without cap)", "binds only above $2,000; top profiles unchanged"],
    ["Profit since last payout", "missing from A0's field list and propsim's early copy; E1 already enforced it", "costs time, not money"],
    ["Payout fee", "$30 for ACH / wire only", "avoidable"],
    ["Horizon (withdrawn claim)", `"5:1 adds nothing over 3:1 with frictions" was a 250-day artefact: at 1,000 days 5:1 ${$(N.hz(5, 30, 1000).net)} vs 3:1 ${$(N.hz(3, 30, 1000).net)}`, "high R harvests slower"],
    ["Daily Loss Limit", `doubles the cap to $4,000; gain ${$(N.dllRow(3, "DLL-capped", 4000, true).net - N.dllRow(3, "single", 2000, true).net)} per funded account at 3:1, ${$(N.dllRow(5, "DLL-capped", 4000, true).net - N.dllRow(5, "single", 2000, true).net)} at 5:1`, "the 50 %-of-balance limit binds first"],
  ], 0.5, 1.5, 12.3, [2.6, 6.3, 3.4], 12, 0.72);
  s.addText("All at zero edge. The all-in identity survives the DLL and the 75 % split: a losing day never ratchets the floor.", { x: 0.5, y: 6.0, w: 12.3, h: 0.5, fontFace: BF, fontSize: 13, italic: true, color: NAVY, isTextBox: true, margin: 0 });
}
// ================= 21 Finding 8 time barrier
{
  const s = frame("Finding 8 — the session time barrier", "The contract engine has no clock inside a day. The live product flattens at 15:10 CT.", "At zero edge the funded number would depend on one quantity, s", "Research document Part VI §31, Eq. ({{E:session}}), Table {{T:tbtab}}, Figure {{F:tb}}; results_timebarrier.csv (N = 20,000)");
  const ss = [0.25, 0.5, 1, 2, 4, 8];
  const series = [1, 2, 3, 5].map(rr => ({ name: `R = ${rr}:1`, labels: ss.map(String), values: ss.map(x => +N.tbRow(x, rr).net.toFixed(0)) }));
  series.push({ name: "static fallback 2:1 $750", labels: ss.map(String), values: ss.map(() => +N.xfaStatic.toFixed(0)) });
  s.addChart(pres.charts.LINE, series, { x: 0.5, y: 1.45, w: 7.8, h: 5.2, ...chartBase("Day-one all-in: net $ per XFA against s (Brownian-bridge exact barriers)"), chartColors: [GREY, NAVY, TEAL, AMBER, RED], lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 5, catAxisTitle: "s = session σ / cushion", showCatAxisTitle: true, catAxisTitleFontSize: 9, valAxisTitle: "$ per XFA", showValAxisTitle: true, valAxisTitleFontSize: 9 });
  card(s, 8.6, 1.5, 4.2, 2.3, "Method", "Intra-session P&L of the max-size position as a fair Brownian path with session σ; exits at the floor, the target, or the 15:10 flatten at current P&L. All-in repeated on the remaining room until B ≥ 2,000 or death. Validated: s = 8 recovers the binary limits (R = 5: P = 0.165 vs 1/6).", PALE, 10.5);
  card(s, 8.6, 3.95, 4.2, 2.7, "Result", `s ≤ 0.5 → ${$(N.tbRow(0.5, 2).net)}–${$(N.tbRow(0.5, 1).net)}, below the static ${$(N.xfaStatic)}: the all-in degrades into a multi-day grind that ratchets.\ns = 1 → ≈ ${$(N.tbRow(1, 1).net)}–${$(N.tbRow(1, 3).net)}, R irrelevant.\ns = 2 → ${$(N.tbRow(2, 3).net)} at R = 3.\ns ≥ 4 → ${$(N.tbRow(4, 3).net)} / ${$(N.tbRow(4, 5).net)} at R = 3 / 5.\nCrossover ≈ 0.75. s is a Stage-2 measurement, not a contract fact.`, "DCEBEE", 10.5);
}
// ================= NEW 22 Zero-edge results
{
  const s = frame("Zero-edge results", "What the contract does to a fair coin — properties of the contract, not a plan (Part VII).", "At zero edge: 16/49 to pass, $183–$346 per attempt, 8 % ever positive", "Research document Part VI §32, Table {{T:final}}");
  stat(s, 0.5, 1.45, 3.0, "16/49", `Combine pass, exact\n(MC ${N.mcP.toFixed(4)} ± ${N.mcSE.toFixed(4)}, N = 2M)`);
  stat(s, 3.6, 1.45, 3.0, $(N.evExact(N.xfaStatic)), "EV per attempt\nstatic funded 2:1 $750", TEAL);
  stat(s, 6.7, 1.45, 3.0, $(N.evExact(N.allin[3])), "EV per attempt\nfunded 3:1 all-in", AMBER);
  stat(s, 9.8, 1.45, 3.0, pct(N.fig13.p_net_pos, 0), `of attempts ever positive\n(median attempt ${$(N.fig13.p50)})`, RED);
  tbl(s, ["Quantity", "Value", "Basis"], [
    ["Combine ridge", "R × $ risk ≈ $1,500, $ risk ≤ $1,500 (1:1 $1,500, 2:1 $750, 1.5:1 $1,000 …)", "Findings 2, 5"],
    ["Best possible pass rate", N.sup(50, 0).sup_p_pass.toFixed(6), "Eq. ({{E:supremum}})"],
    ["Funded optimum (zero edge)", "one account-deciding bet: net 0.9·2,000·R/(1+R); static 2:1 $750 nets " + $(N.xfaStatic), "Eq. ({{E:allin}})"],
    ["EV per attempt", "exact 16/49 × (funded net − 149) − $49", "Eq. ({{E:evatt}})"],
    ["Ceilings", "P(pass) ≤ 40 %; E[gross payouts] ≤ $2,000", "Eqs. ({{E:ceiling}}), ({{E:xceil}})"],
  ], 0.5, 3.5, 12.3, [2.6, 6.9, 2.8], 12, 0.5);
}
// ================= 23 Distribution
{
  const s = frame("Finding 3 — what the expectation looks like", "An EV of a few hundred dollars is carried by one attempt in twelve.", "Net cash per attempt under the recommended combined policy", "Research document Part VI §26, Figure {{F:dist}}; fig13_stats.csv (N = 50,000)");
  img(s, "s_net_distribution.png", 0.5, 1.5, 7.8, 3.9);
  tbl(s, ["Statistic", "Value"], [["mean", $(N.fig13.mean_net)], ["P(net > 0)", pct(N.fig13.p_net_pos)], ["5th percentile", $(N.fig13.p5)], ["median", $(N.fig13.p50)], ["95th percentile", $(N.fig13.p95)], ["P(pass)", pct(N.fig13.p_pass)]], 8.6, 1.5, 4.2, [2.2, 2.0], 11);
  bulletsBox(s, ["The mass at −$49 is failed Combines; at −$198, passed Combines whose XFA died on day one.", "Static cells: only 6–14 % of attempts positive (Table {{T:fm}}).", "This is the profile of the prohibited campaign: the value sits in a few wins among many failures (Part VII)."], 8.6, 4.2, 4.2, 2.5, 11);
}
// ================= NEW 25 Conduct finding
{
  const s = frame("Part VII — the conduct finding", "Before any of Part VI could be used, the firm's terms had to be read against it.", "The zero-edge campaign is the named prohibition", "Research document Part VII §33; help-centre articles 10305426, 10296582, 13620045");
  card(s, 0.5, 1.5, 6.0, 2.55, "Account stacking (Prohibited Trading Strategies)", "Repeatedly trading aggressively, hitting the loss limit in one account, switching accounts and repeating until a large win — prohibited as exploiting risk parameters. The page calls its list \"hard stops\", not gray areas.", "F6DEDA", 13);
  card(s, 6.8, 1.5, 6.0, 2.55, "\"Not a viable strategy\" (Prohibited Conduct)", "A sole-discretion catch-all also covers uncommercial conduct, gaming the market and irresponsible trading. A process with no edge is, by construction, not a viable strategy.", "F6DEDA", 13);
  card(s, 0.5, 4.25, 6.0, 2.35, "Responsible Trading Program", "Patterns like blowing accounts, overleveraging and churning accounts can place a trader in RTP: Combines carry a DLL, new funded accounts are Consistency-path only.", PALE, 13);
  card(s, 6.8, 4.25, 6.0, 2.35, "What follows", "Every zero-edge profile earns its value by failing repeatedly and replacing the account. The structural value is not a loophole around the rule — it is what the rule prohibits. H6 rejected.", NAVY, 13, WHITE);
}
// ================= NEW 26 Candidates vs terms
{
  const s = frame("Part VII — candidates and constraints", "Candidates are never ranked by how noticeable they are: the rule is defined by its goal.", "No zero-edge candidate is acceptable; the constraints for a real edge", "Research document Part VII §34–35, Table {{T:conduct}}");
  tbl(s, ["Candidate", "Fail-and-repurchase at e = 0", "Winners > losers", "Largest position", "Verdict"], [
    ["Supremum policy ($2,000 bets)", "yes", "no", "100 %", "not acceptable"],
    ["1:1 $1,500 (Part VI optimum)", "yes", "equal", "75 %", "not acceptable"],
    ["1.5:1 $1,000", "yes", "yes", "50 %", "not at e = 0"],
    ["2:1 $750", "yes", "yes", "37.5 %", "not at e = 0; best fit with an edge"],
    ["Funded all-in (whole or split)", "—", "yes", "100 %", "not acceptable"],
  ], 0.5, 1.5, 7.6, [2.5, 1.7, 1.1, 1.1, 1.2], 11, 0.6);
  card(s, 8.4, 1.5, 4.4, 5.0, "Constraints for a trader with an edge", "• Winners larger than losers (R > 1)\n\n• Risk per position well below the maximum (≤ $1,000, half the drawdown, in the tests)\n\n• No single position that decides the account, on either stage\n\n• One account at a time; no fail-and-repurchase campaign — the edge must carry the value", "DCEBEE", 13);
}
// ================= NEW 27 Value of edge: design and validation
{
  const s = frame("Part VIII — the value of a demonstrated edge", "Pre-registered before any run; two later analyses labelled exploratory.", "Design and validation of the value-of-edge study", "Research document Part VIII §36–37, Table {{T:val}}; edge/PREREG_T5.md, edge/validation_T5.txt");
  card(s, 0.5, 1.5, 5.4, 5.0, "Design", "Profiles: R ∈ {1.5, 2, 3} × $ risk ∈ {$500, $750, $1,000}, one trade a day (reference: 1:1 $1,500, not admissible)\n\nEdges: 0, 2, 5, 10, 15, 20 % (after costs)\n\nCombine: exact Markov chain; Monte Carlo as validator\n\nFunded: Monte Carlo, 1 year, Standard and Consistency (RTP) paths, net-profit rule on\n\nComposition: EV = P(pass) × (funded cash − 149) − subscriptions", PALE, 12);
  tbl(s, ["Pre-registered check", "Result"], [
    ["V1 exact chain vs Monte Carlo (120 comparisons)", "2 beyond 3 SE, max 3.26 — PASS"],
    ["V1 follow-up at N = 1M (fresh seeds)", "all within 2.13 SE — chance"],
    ["V2 chain reproduces 16/49", "to 1.7 × 10⁻¹⁴ — PASS"],
    ["V2 chain reproduces the stored grid", "max |z| 2.32 — PASS"],
    ["V3 zero-edge funded bounds", "PASS"],
    ["V3 value non-decreasing in edge", "PASS"],
  ], 6.2, 1.5, 6.6, [3.8, 2.8], 12, 0.62);
  s.addText("Two methods — an exact chain and simulation — agree everywhere.", { x: 6.2, y: 6.0, w: 6.6, h: 0.5, fontFace: BF, fontSize: 13, italic: true, color: NAVY, isTextBox: true, margin: 0 });
}
// ================= NEW 28 Pass vs edge
{
  const s = frame("Part VIII — Combine pass probability", "Two rules explain the chart: higher R means more variance; larger $ risk means fewer trades for the edge to work.", "Small risk with moderate R wins once the edge is real", "Research document Part VIII §38, Table {{T:passedge}}, Figure {{F:passedge}}; edge/results_combine_edge.csv");
  const E6 = [0, 0.02, 0.05, 0.10, 0.15, 0.20], lab = E6.map(e => `${(100 * e).toFixed(0)} %`);
  const prof = [[1.5, 500], [2, 750], [1.5, 1000], [3, 500], [3, 1000], [1, 1500]];
  s.addChart(pres.charts.LINE, prof.map(([R, r]) => ({ name: `${R}:1 $${fmt0(r)}${R === 1 ? " (ref.)" : ""}`, labels: lab, values: E6.map(e => +(100 * N.ce(R, r, e).p_pass).toFixed(1)) })),
    { x: 0.5, y: 1.45, w: 8.0, h: 5.2, ...chartBase("Exact Combine pass probability (%) against edge"), chartColors: [NAVY, AMBER, GREEN, TEAL, RED, "999999"], lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 6, catAxisTitle: "edge (after costs)", showCatAxisTitle: true, catAxisTitleFontSize: 10, valAxisMinVal: 15, valAxisMaxVal: 55 });
  bulletsBox(s, [`At 10 % edge: 1.5:1 $500 passes ${pct(N.ce(1.5, 500, 0.10).p_pass, 1)}, 2:1 $750 ${pct(N.ce(2, 750, 0.10).p_pass, 1)}, 3:1 $1,000 only ${pct(N.ce(3, 1000, 0.10).p_pass, 1)}.`,
    "At 3:1 a trade wins about one time in four, so the Combine resolves on luck.",
    "Big bets resolve the account in a few flips; small bets give the edge room to average out.",
    "The reference 1:1 $1,500 passes most at low edge but is excluded by the constraints."], 8.8, 1.5, 4.0, 5.1, 13);
}
// ================= NEW 29 EV and edge share
{
  const s = frame("Part VIII — EV per attempt", "Below a 5 % edge most of the value is the prohibited structural part; at 10 % the edge does the work.", "How much of the EV comes from the edge", "Research document Part VIII §39, Table {{T:edgeshare}}, Figure {{F:edgeshare}}; edge/results_value_of_edge.csv");
  const E6 = [0, 0.02, 0.05, 0.10, 0.15, 0.20], lab = E6.map(e => `${(100 * e).toFixed(0)} %`), B = E6.map(e => N.bestPair(e, "standard"));
  s.addChart(pres.charts.BAR, [{ name: "structural (present at zero edge)", labels: lab, values: B.map(b => Math.round(b.ev_structural)) }, { name: "from the edge", labels: lab, values: B.map(b => Math.round(b.ev_from_edge)) }],
    { x: 0.5, y: 1.45, w: 7.6, h: 5.2, barGrouping: "stacked", ...chartBase("EV per Combine attempt ($), best admissible pair"), chartColors: ["9AA5A7", NAVY], showValue: false, catAxisTitle: "edge (after costs)", showCatAxisTitle: true, catAxisTitleFontSize: 10 });
  tbl(s, ["Edge", "EV", "edge share", "failed Combines / yr"], B.map((b, i) => [lab[i], $(b.ev_per_attempt), pct(b.edge_share_of_ev, 0), fmt1(b.failed_combines_per_year)]), 8.4, 1.5, 4.4, [0.9, 1.1, 1.1, 1.3], 12, 0.42);
  s.addText("A \"value per account-year\" rate is never shown alone: it rewards cycling through failed attempts.", { x: 8.4, y: 4.7, w: 4.4, h: 1.2, fontFace: BF, fontSize: 12, italic: true, color: NAVY, isTextBox: true, margin: 0 });
}
// ================= NEW 30 Payout buffer
{
  const s = frame("Part VIII — the funded account (exploratory)", "Any payout moves the floor to $0, so withdrawing early strands a small balance.", "Keep a buffer: payout policy matters as much as R:R", "Research document Part VIII §40, Table {{T:buffer}}, Figure {{F:buffer}}; edge/results_payout_buffer_*.csv");
  img(s, "fig16_payout_buffer.png", 0.5, 1.45, 8.2, 3.6);
  const b10 = N.bestBuf(0.10), b20 = N.bestBuf(0.20), t10 = N.bestTakeMax(0.10), t20 = N.bestTakeMax(0.20);
  stat(s, 8.9, 1.45, 3.9, $(b10.cash_per_year), `per funded account per year at 10 % edge\nwith a $${fmt0(b10.keep_balance)} buffer (vs ${$(t10.cash_per_year)})`, NAVY);
  stat(s, 8.9, 3.3, 3.9, $(b20.cash_per_year), `at 20 % edge (vs ${$(t20.cash_per_year)})`, TEAL);
  bulletsBox(s, [`Best found: ${b10.R}:1 at $${fmt0(b10.risk)}, keeping about $${fmt0(b10.keep_balance)} in the account — roughly double the take-everything policy.`,
    "Every buffer respects the zero-edge ceilings: no value is created where there should be none.",
    "Exploratory (chosen after seeing results), coarse grid; unrealised balance at the horizon is not counted."], 0.5, 5.2, 12.3, 1.5, 12);
}
// ================= NEW 31 Value per attempt and data needed
{
  const s = frame("Part VIII — value and proof", "Value grows much faster than edge; proving the edge takes years of trades.", "What an edge is worth, and what it takes to demonstrate it", "Research document Part VIII §41–42, Tables {{T:evbuffer}}, {{T:samples}}, Eq. ({{E:samplesize}}); edge/results_sample_size.csv");
  const V = [0.05, 0.10, 0.20].map(e => N.evBestBuffer(e));
  stat(s, 0.5, 1.45, 2.0, $(V[0].ev), "EV per attempt\nat 5 % edge", GREY);
  stat(s, 2.6, 1.45, 2.0, $(V[1].ev), "at 10 %", NAVY);
  stat(s, 4.7, 1.45, 2.0, $(V[2].ev), "at 20 %", TEAL);
  s.addText("Best admissible Combine profile + buffered funded account (exploratory funded policy)", { x: 0.5, y: 2.95, w: 6.2, h: 0.5, fontFace: BF, fontSize: 11, italic: true, color: GREY, isTextBox: true, margin: 0 });
  eqBox(s, 0.5, 3.6, 6.2, "n ≥ ( 1.645 · (1+R)√(p(1−p)) / (e/2) )²", "{{E:samplesize}}");
  bulletsBox(s, ["Fee risk becomes small: at 10 % edge, eight failed Combines in a row has probability ≈ 2 %.", "The real risk of ruin is believing in an edge that is not there."], 0.5, 4.3, 6.2, 2.2, 13);
  tbl(s, ["R", "e = 5 %", "e = 10 %", "e = 20 %"], [1.5, 2, 3].map(R => [`${R}:1`, ...[0.05, 0.10, 0.20].map(e => { const x = N.ss(R, e); return `${fmt0(x.trades_lower_bound_above_half_edge)} (${x.years_at_1_per_day} yrs)`; })]), 7.0, 1.5, 5.8, [0.8, 1.7, 1.65, 1.65], 12, 0.5);
  s.addText("Trades needed for the 95 % lower bound to exceed half the true edge (years at one trade a day). A short live record cannot prove a 10 % edge.", { x: 7.0, y: 3.7, w: 5.8, h: 1.2, fontFace: BF, fontSize: 12, italic: true, color: NAVY, isTextBox: true, margin: 0 });
}
// ================= NEW 32 Sensitivity & robustness
{
  const s = frame("Sensitivity and robustness", "Several independent methods agree on the exact numbers.", "Robustness checks", "Research document Part IX, Table {{T:ladder}}, Figure {{F:ladder}}; results_final.csv");
  s.addChart(pres.charts.LINE, [{ name: "EV / attempt, zero-edge profiles", labels: N.fin.map(r => r.edge.toFixed(2)), values: N.fin.map(r => +r.ev_attempt_static.toFixed(0)) }],
    { x: 0.5, y: 1.45, w: 6.4, h: 4.6, ...chartBase("Zero-edge profiles: EV per attempt vs edge (costs as negative edge)"), chartColors: [NAVY], lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 6, showValue: true, dataLabelPosition: "t", dataLabelFontSize: 9, showLegend: false });
  s.addText("Positive even at −10 % edge — which is exactly why the structural value needs no skill, and why it is prohibited.", { x: 0.5, y: 6.1, w: 6.4, h: 0.6, fontFace: BF, fontSize: 12, italic: true, color: NAVY, isTextBox: true, margin: 0 });
  bulletsBox(s, [`Ceilings: no grid cell above 0.40 + 4 SE; max funded gross $${fmt0(N.maxGross)}.`,
    `16/49 by simulation at N = 2M (z = ${N.mcZ >= 0 ? "+" : ""}${N.mcZ.toFixed(2)}); supremum by simulation (pooled z = +1.13); edge chain vs MC in 120 comparisons.`,
    "Identities: all-in 0.9·2,000·R/(1+R) at four R; survives the DLL and a 75 % split; time barrier recovers the binary limits.",
    `Conventions: truncate ≈ resize (9 cells); drift ≡ linear in ${N.ecIdentical} of ${N.ecPairs.length} cells.`,
    "Horizon binds only with the net-profit rule at R ≥ 3 — re-run to 1,000 days.",
    "Every result file seeded; failed checks kept on record with their diagnosis."], 7.2, 1.5, 5.6, 5.2, 12);
}
// ================= NEW 33 Limitations
{
  const s = frame("Limitations", "What separates the model from the product, with the direction of each bias.", "Limitations and uncertainties", "Research document Part X §48, Table {{T:limits}}");
  tbl(s, ["Limitation", "Direction of bias", "How to resolve"], [
    ["Binary two-outcome trades", "real trades have an outcome distribution", "use the candidate's empirical distribution"],
    ["One trade a day, fixed $ risk", "more trades per day would shorten the proof", "extend once a candidate's frequency is known"],
    ["Exact-at-stop fills", "overstates results; SIM-fill reliance is prohibited", "require the edge net of realistic slippage"],
    ["Drift convention inside truncated trades", "second-order at |e| ≤ 10 %", "empirical excursion data"],
    ["No scaling-plan limits; 1–2 year funded horizons", "understates buffered accounts", "longer horizons; add the scaling plan"],
    ["Buffer and small-risk results exploratory", "chosen after seeing results", "pre-register for the actual candidate"],
    ["Firm discretion; rule changes", "can only reduce realised value", "re-verify the terms before use"],
  ], 0.5, 1.5, 12.3, [3.9, 4.3, 4.1], 12, 0.6);
}
// ================= NEW 34 Interpretation
{
  const s = frame("Interpretation", "The same asymmetry that creates the value is what the rules protect.", "What the results mean — and what they do not", "Research document Part X §46–47");
  card(s, 0.5, 1.5, 6.0, 5.0, "What they mean", "At zero edge every profile choice is a choice about where to lose: quickly at the deepest floor (good) or slowly while the floor climbs (bad). That is why the funded optimum is one all-or-nothing bet.\n\nThe value exists because failure is cheap and repeatable — precisely the pattern the firm prohibits. The zero-edge result describes what the firm protects itself against.\n\nWith a genuine edge the picture inverts: modest bets let the edge average out, and a buffered funded account compounds it. The zero-edge optimum is the wrong structure for an edge as well as a prohibited one.", PALE, 13);
  card(s, 6.8, 1.5, 6.0, 5.0, "What they do not mean", "• Not a way to make money without skill: the zero-edge route is prohibited, and an edge's value depends on the edge being real.\n\n• Not evidence that any strategy has an edge: the engine values an edge; it cannot find one.\n\n• Not a price for discretion: the firm may review any pattern, and its terms change.", "FBEFE3", 13);
}
// ================= NEW 35 Conclusions
{
  const s = frame("Conclusions", "Seven statements, each supported by a named part of the analysis and nothing further.", "Conclusions", "Research document Part XI");
  const items = [
    `Ceilings: P(pass) ≤ 40 %, E[gross payouts] ≤ $2,000; best possible pass rate over all strategies ${N.sup(50, 0).sup_p_pass.toFixed(4)} (Part IV).`,
    `Zero-edge geometry: the ridge R × $ risk ≈ $1,500 (1:1 $1,500 passes exactly 16/49) plus one account-deciding funded bet; ${$(N.evExact(N.xfaStatic))}–${$(N.evExact(N.allin[3]))} per attempt, ${pct(N.fig13.p_net_pos, 0)} ever positive (Part VI).`,
    "That value needs repeated failure and replacement — prohibited as account stacking. Not a usable plan (Part VII).",
    `With a genuine edge the contract amplifies it: edge share ${pct(N.bestPair(0.05, "standard").edge_share_of_ev, 0)} at 5 %, ${pct(N.bestPair(0.10, "standard").edge_share_of_ev, 0)} at 10 %; best 2:1 $750 at low edge, 1.5:1 $500 from 10 % (Part VIII).`,
    `A funded payout buffer roughly doubles realised cash; EV per attempt ≈ ${$(N.evBestBuffer(0.10).ev)} at 10 % edge (exploratory).`,
    `Demonstrating a 10 % edge needs ${fmt0(N.ss(1.5, 0.10).trades_lower_bound_above_half_edge)}–${fmt0(N.ss(3, 0.10).trades_lower_bound_above_half_edge)} trades — years at one a day.`,
    "Four modelling errors found and corrected: floor overshoot, three missing rules, a horizon artefact, a churn-rewarding metric.",
  ];
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: { type: "number" }, breakLine: i < items.length - 1, paraSpaceAfter: 8 } })), { x: 0.5, y: 1.5, w: 12.3, h: 5.2, fontFace: BF, fontSize: 14, color: "222222", valign: "top", isTextBox: true, margin: 2 });
}
// ================= NEW 36 Research criterion
{
  const s = frame("The criterion for the next stage (pre-registered)", "Written before any candidate is tested, so it cannot be tuned to one.", "What the research stage must demonstrate", "Research document Part XI §49; HANDOFF.md");
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.5, w: 12.3, h: 3.5, fill: { color: PALE }, line: { color: AMBER, width: 1.5 }, rectRadius: 0.08 });
  s.addText([
    { text: "Edge e = mean P&L per trade ÷ $ risked — net of commissions and slippage, with realistic fills, out of sample", options: { bold: true, color: NAVY, breakLine: true, paraSpaceAfter: 10 } },
    { text: "Pursue a candidate only if e ≥ 10 % and its one-sided 95 % lower bound ≥ 5 %", options: { breakLine: true, paraSpaceAfter: 8 } },
    { text: "Measured on the bracket the account will use: R between 1.5 and 3, 15:10 CT flatten applied", options: { breakLine: true, paraSpaceAfter: 8 } },
    { text: "Use the lower bound, never the point estimate, for any sizing or money decision", options: { breakLine: true, paraSpaceAfter: 8 } },
    { text: "Respect the constraints: winners > losers, modest size, no account-deciding position, one account at a time", options: {} },
  ], { x: 0.75, y: 1.7, w: 11.8, h: 3.2, fontFace: BF, fontSize: 15, color: "222222", valign: "top", isTextBox: true, margin: 0 });
  s.addText("With this criterion the repository's question is closed. Finding and demonstrating an edge is research, not modelling.", { x: 0.5, y: 5.3, w: 12.3, h: 0.6, fontFace: HF, fontSize: 18, italic: true, color: NAVY, isTextBox: true, margin: 0 });
}
// ================= NEW 37 Appendix equations
{
  const s = frame("Appendix — equation reference", "Numbers are generated by the document build and shared by both deliverables.", "Governing equations", "Research document Appendix C");
  tbl(s, ["Eq.", "Statement", "Role"], [
    ["{{E:p}}–{{E:ev}}", "p = (1+e)/(1+R);  E[X] = e·r", "declared process"],
    ["{{E:sc}}–{{E:lock}}", "Combine state, trade, lock: F ← min(0, max(F, B − 2000)); PASS if B ≥ max(3000, B_d/0.55)", "Combine"],
    ["{{E:trunc}}", "c = min(r, B − F);  P(win | c) = c/(c + W)", "floor convention"],
    ["{{E:race}}–{{E:identity}}", "drifted barrier race, θ solve, liquidation identity", "edge convention"],
    ["{{E:sx}}–{{E:payout}}", "funded state, lock, eligibility, payout q = min(0.5B, cap)", "funded"],
    ["{{E:ceiling}}", "P(pass) ≤ 2/5", "ceiling"],
    ["{{E:xceil}}–{{E:leak}}", "E[Q] ≤ 2,000;  E[Q] = (1 − P_pay)(2,000 − E[ratchet])", "funded ceiling, leak"],
    ["{{E:allin}}", "E[Q] = 2,000·R/(1+R)", "zero-edge funded optimum"],
    ["{{E:markov}}", "d = 16/49", "exact Combine profile"],
    ["{{E:supremum}}", "V = cav_x[g(x)] — best pass probability over all strategies", "proven optimum"],
    ["{{E:se}}, {{E:evatt}}", "standard errors; EV = P(pass)(X − 149) − S_sub", "statistics, output"],
    ["{{E:samplesize}}", "n ≥ (1.645·(1+R)√(p(1−p))/(e/2))²", "research criterion"],
  ], 0.5, 1.5, 12.3, [1.4, 8.0, 2.9], 11, 0.38);
}
// ================= NEW 38 Appendix validation + files
{
  const s = frame("Appendix — validation and reproducibility", "Every number is produced by a seeded script and stored in a result file.", "Tests, records and result files", "Research document Appendices D–F; EV Backtest Results.zip");
  card(s, 0.5, 1.5, 6.0, 5.0, "33 automated tests (test_propsim.py)", "Golden paths from the rule text (two-day pass, best-day trap, floor lock, intraday breach, billing, funded payouts, caps, day counting, buffer rule).\n\nOracles: P(pass) ≤ 0.40 + 4 SE; E[Q] ≤ $2,000; martingale checks.\n\nExact identities: 16/49; liquidation identity to 1e−12; θ solver.\n\nRecords: DECISIONS.md (47 entries), pre-registrations, failed checks kept with their diagnosis.", PALE, 12);
  card(s, 6.8, 1.5, 6.0, 5.0, "Repository layout", "propsim.py, statepolicy.py, timebarrier.py — engines\nrun_*.py → results_*.csv — zero-edge studies\noptimality/ — supremum, DLL, horizon, cross-checks\nedge/ — pre-registered value-of-edge study + exploratory runs\nbankroll/ — zero-edge fee model (record only: prohibited campaign)\ndeliverables/ — sources for this deck and the document\nHANDOFF.md — the research-stage specification\n\nRun: python -m pytest test_propsim.py -q, then any script. All seeded.", "DCEBEE", 12);
}
pres.writeFile({ fileName: __dirname + "/deck.pptx" }).then(() => console.log("deck written, slides:", n));
