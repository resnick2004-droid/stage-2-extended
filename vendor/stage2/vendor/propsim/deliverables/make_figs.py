import os
HERE = os.path.dirname(os.path.abspath(__file__))
import numpy as np, pandas as pd, matplotlib, os, sys
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
sys.path.insert(0, os.path.dirname(HERE))
P = os.path.dirname(HERE) + "/"
OUT = HERE + "/figs/"; os.makedirs(OUT, exist_ok=True)
NAVY, TEAL, AMBER, GREY, LIGHT, RED = "#14343B", "#2E7D8C", "#D9822B", "#5F6B6D", "#E8EEF0", "#B3412E"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": GREY, "axes.labelcolor": NAVY, "xtick.color": GREY, "ytick.color": GREY})

def box(ax, x, y, w, h, text, fc=LIGHT, ec=NAVY, fs=12, bold=False, tc=NAVY):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03", fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc, fontweight="bold" if bold else "normal", wrap=True)

def arrow(ax, x0, y0, x1, y1, color=NAVY, text=None, fs=11):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=14, color=color, lw=1.3))
    if text:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.03, text, ha="center", va="bottom", fontsize=fs, color=color)

# ---------------- fig01 architecture ----------------
fig, ax = plt.subplots(figsize=(11, 4.0)); ax.set_xlim(0, 11); ax.set_ylim(0.6, 4.4); ax.axis("off")
Y, H = 2.5, 1.3
box(ax, 0.2, Y, 1.7, H, "POLICY\n(R, $ risk,\nday rule) π(S)", fc="#FBEFE3", ec=AMBER, fs=10)
box(ax, 2.35, Y, 1.8, H, "FAIR\nGENERATOR\np = (1+e)/(1+R)", fc=LIGHT, fs=10)
box(ax, 4.6, Y, 2.0, H, "COMBINE\nratchet · 55 % rule\nliquidation\npass / fail", fc="#DCEBEE", ec=TEAL, fs=9.5)
box(ax, 7.05, Y, 2.0, H, "XFA\nfloor −2,000 → 0\npayout paths\nclosed / paid", fc="#DCEBEE", ec=TEAL, fs=9.5)
box(ax, 9.5, Y, 1.3, H, "CASH\n0.9 q\n− fees", fc=NAVY, ec=NAVY, tc="white", bold=True, fs=10)
for x0, x1 in [(1.9, 2.35), (4.15, 4.6), (6.6, 7.05), (9.05, 9.5)]: arrow(ax, x0, Y + H / 2, x1, Y + H / 2)
for xm, t in [(2.12, "(R, r)"), (4.37, "P&L"), (6.82, "pass, +$149")]: ax.text(xm, Y + H + 0.12, t, ha="center", va="bottom", fontsize=9, color=GREY)
box(ax, 0.2, 0.8, 1.9, 1.1, "ANALYTIC BOUNDS\nP(pass) ≤ 2/5\nE[gross] ≤ $2,000", fc="#FBEFE3", ec=AMBER, fs=9.5)
box(ax, 2.6, 0.8, 2.1, 1.1, "FEE CLOCK\n$49 per billing period\nactivation $149", fc="white", ec=GREY, fs=9.5)
box(ax, 5.2, 0.8, 2.1, 1.1, "FLOOR CONVENTION\ntruncate at room c\np = c/(c+W) at e = 0", fc="white", ec=GREY, fs=9.5)
box(ax, 7.8, 0.8, 2.1, 1.1, "SESSION BARRIER\nzero-edge all-in only\n15:10 CT flatten", fc="white", ec=GREY, fs=9.5)
arrow(ax, 3.65, 1.9, 5.3, Y, color=GREY); arrow(ax, 6.25, 1.9, 5.9, Y, color=GREY); arrow(ax, 8.85, 1.9, 8.3, Y, color=GREY)
fig.savefig(OUT + "fig01_architecture.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# ---------------- fig02 combine state machine ----------------
fig, ax = plt.subplots(figsize=(10, 3.6)); ax.set_xlim(0, 10); ax.set_ylim(0.3, 3.9); ax.axis("off")
box(ax, 3.4, 2.4, 3.2, 1.3, "ACTIVE\ntrade: B += X, D += X\nbreach if B ≤ F (real time)", fc="#DCEBEE", ec=TEAL, fs=11)
box(ax, 0.3, 0.5, 2.6, 1.1, "FAILED\nB = F at breach", fc="#F6DEDA", ec=RED, fs=11)
box(ax, 7.1, 0.5, 2.6, 1.1, "PASSED\nB ≥ max(3000, B_d/0.55)\nat the lock → XFA", fc="#E1EFDF", ec="#3E7C4A", fs=11)
box(ax, 3.4, 0.5, 3.2, 1.1, "16:00 CT LOCK\nB_d = max(B_d, D)\nF = min(0, max(F, B − 2000))\npass test; D = 0", fc="white", ec=GREY, fs=10)
arrow(ax, 5.0, 2.4, 5.0, 1.6, text="each day"); arrow(ax, 3.6, 2.6, 1.9, 1.6, color=RED, text="B ≤ F"); arrow(ax, 6.4, 1.05, 7.1, 1.05, color="#3E7C4A")
arrow(ax, 3.6, 1.05, 2.9, 1.05, color=GREY); arrow(ax, 5.8, 1.6, 5.8, 2.4, color=GREY, text="next day")
fig.savefig(OUT + "fig02_combine_state_machine.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# ---------------- fig03 barrier race ----------------
fig, ax = plt.subplots(figsize=(8, 3.6))
rng = np.random.default_rng(4); t = np.linspace(0, 1, 400); path = np.cumsum(rng.normal(0, 60, 400)); path -= path[0]
ax.plot(t, path, color=NAVY, lw=1.2); ax.axhline(1500, xmax=0.74, color="#3E7C4A", ls="--"); ax.axhline(-1500, xmax=0.74, color=GREY, ls=":"); ax.axhline(-500, xmax=0.74, color=RED, ls="--")
ax.text(1.02, 1500, "target +W = R·r", va="center", color="#3E7C4A"); ax.text(1.02, -1500, "chosen stop −r", va="center", color=GREY); ax.text(1.02, -500, "floor: room c = B − F", va="center", color=RED)
ax.set_xlim(0, 1.35); ax.set_ylim(-1900, 1900); ax.set_xlabel("session time"); ax.set_ylabel("trade P&L ($)"); ax.set_xticks([])
ax.set_title("Floor-consistent truncation: with the floor closer than the stop the trade is a race between −c and +W, won with probability c/(c+W) at zero edge", fontsize=9, color=GREY, loc="left")
fig.savefig(OUT + "fig03_barrier_race.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# ---------------- fig04/05 heatmaps from grid ----------------
g = pd.read_csv(P + "results_grid_edge0.csv")
def heat(col, title, fname, fmt, vmin=None, cmap="viridis"):
    rules = ["1/day", "3/day"]
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.0), sharey=True)
    vmax = g[col].max(); vmin = g[col].min() if vmin is None else vmin
    for ax, rule in zip(axes, rules):
        piv = g[g.day_rule == rule].pivot(index="rr", columns="risk", values=col)
        im = ax.imshow(piv.values, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_xticks(range(len(piv.columns))); ax.set_xticklabels([f"${c}" for c in piv.columns], rotation=45, fontsize=11)
        ax.set_yticks(range(len(piv.index))); ax.set_yticklabels([f"{r}:1" for r in piv.index], fontsize=11)
        ax.set_title(rule, fontsize=13, color=NAVY); ax.set_xlabel("$ risk per trade", fontsize=11)
        for i in range(piv.shape[0]):
            for j in range(piv.shape[1]):
                v = piv.values[i, j]; txt = fmt.format(v) if v > -999 else f"{v/1000:.1f}k"; ax.text(j, i, txt, ha="center", va="center", fontsize=10, color="white" if (v - vmin) / (vmax - vmin) < 0.6 else "black")
    axes[0].set_ylabel("R:R", fontsize=12); fig.colorbar(im, ax=axes, shrink=0.9, pad=0.02)
    fig.savefig(OUT + fname, dpi=170, bbox_inches="tight"); plt.close(fig)
heat("c_p_pass", "Combine pass probability by profile at zero edge (N = 10,000 per cell; analytic ceiling 0.40)", "fig04_pass_heatmap.png", "{:.2f}")
heat("best_ev", "Expected net $ per Combine attempt at zero edge, best payout path (colour clipped at −300)", "fig05_ev_heatmap.png", "{:.0f}", vmin=-300)

# ---------------- fig06 EV vs risk ridge (1/day) ----------------
fig, ax = plt.subplots(figsize=(8, 4))
for rr, c in zip([0.5, 1.0, 1.5, 2.0, 3.0], [GREY, NAVY, TEAL, AMBER, RED]):
    s = g[(g.day_rule == "1/day") & (g.rr == rr)].sort_values("risk")
    ax.plot(s.risk, s.best_ev, marker="o", ms=4, color=c, label=f"R = {rr}:1")
ax.axhline(0, color=GREY, lw=0.8); ax.set_ylim(-450, 260); ax.set_xlabel("$ risk per trade"); ax.set_ylabel("expected net $ per attempt")
ax.legend(frameon=False, fontsize=8, ncol=5, loc="lower right")
ax.set_title("EV per attempt against $ risk, one trade per day: subscription drag on the left, consistency/floor turnover on the right", fontsize=9, color=GREY, loc="left")
fig.savefig(OUT + "fig06_ev_vs_risk_ridge.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# ---------------- fig07 consistency sweep ----------------
cs = pd.read_csv(P + "results_consistency_sweep.csv")
pk = cs.loc[cs.groupby(["frac", "rr"])["ev"].idxmax()].copy(); pk["Rr"] = pk.rr * pk.risk
fig, ax = plt.subplots(figsize=(8, 4))
for rr, c in zip([1.0, 1.5, 2.0, 3.0], [NAVY, TEAL, AMBER, RED]):
    s = pk[pk.rr == rr].sort_values("frac"); ax.plot(s.frac, s.Rr, marker="o", color=c, label=f"R = {rr}:1 (measured peak R·r)")
fr = np.array([0.4, 0.55, 0.7, 1.0]); ax.plot(fr, fr * 3000, color=GREY, ls="--", label="consistency bound frac × 3,000")
ax.axhline(1500, color=NAVY, ls=":", lw=0.8); ax.text(0.78, 1560, "R = 1 capped by the MLL at $1,500", fontsize=9, color=NAVY)
ax.set_xlabel("consistency_max_day_frac"); ax.set_ylabel("R × $risk at the EV peak"); ax.legend(frameon=False, fontsize=8, loc="upper left")
ax.set_title("H3 mechanism test: the EV peak in $risk tracks the consistency bound for R ≥ 1.5 and the floor for R = 1", fontsize=9, color=GREY, loc="left")
fig.savefig(OUT + "fig07_consistency_sweep.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# ---------------- fig08 floor modes ----------------
fm = pd.read_csv(P + "results_floor_mode_504.csv")
fm["cell"] = fm.rr.astype(str) + ":1 $" + fm.risk.astype(str) + " " + fm.day_rule
cells = fm.cell.unique(); x = np.arange(len(cells)); w = 0.27
fig, ax = plt.subplots(figsize=(10, 4))
for i, (mode, c) in enumerate(zip(["none", "truncate", "resize"], [RED, NAVY, TEAL])):
    s = fm[fm["mode"] == mode].set_index("cell").loc[cells]
    ax.bar(x + (i - 1) * w, s.net_per_attempt, w, yerr=s.net_se, color=c, label=mode, capsize=2)
ax.set_xticks(x); ax.set_xticklabels(cells, rotation=35, ha="right", fontsize=8); ax.set_ylabel("net $ per attempt (504-day lifecycle)"); ax.legend(frameon=False)
ax.set_title("Floor convention: the gate-1.8 'none' model overshoots the floor and inflates EV in every cell; truncate and resize agree within noise", fontsize=9, color=GREY, loc="left")
fig.savefig(OUT + "fig08_floor_modes.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# ---------------- fig09 Markov chain 16/49 ----------------
fig, ax = plt.subplots(figsize=(10, 4.0)); ax.set_xlim(0, 10); ax.set_ylim(0, 4.0); ax.axis("off")
BW, BH = 2.3, 1.05; XS = [0.2, 3.85, 7.5]; YT, YB = 2.75, 0.35
box(ax, XS[0], YT, BW, BH, "D (start)\nB = 0,  F = −2000\nbet 1500,  p = ½", fc=LIGHT, fs=10)
box(ax, XS[1], YT, BW, BH, "A\nB = 1500,  F = −500\nbet 1500,  p = ½", fc=LIGHT, fs=10)
box(ax, XS[2], YT, BW, BH, "PASS\nB = 3000", fc="#E1EFDF", ec="#3E7C4A", bold=True, fs=12)
box(ax, XS[0], YB, BW, BH, "B′\nB = −1500,  F = −2000\nbet 500,  p = ¼", fc=LIGHT, fs=10)
box(ax, XS[1], YB, BW, BH, "C\nB = 0,  F = −500\nbet 500,  p = ¼", fc=LIGHT, fs=10)
box(ax, XS[2], YB, BW, BH, "FAIL\nB = F", fc="#F6DEDA", ec=RED, bold=True, fs=12)
ym_t, ym_b = YT + BH / 2, YB + BH / 2
arrow(ax, XS[0] + BW, ym_t, XS[1], ym_t); ax.text((XS[0] + BW + XS[1]) / 2, ym_t + 0.08, "win ½", ha="center", fontsize=10, color=NAVY)
arrow(ax, XS[1] + BW, ym_t, XS[2], ym_t, color="#3E7C4A"); ax.text((XS[1] + BW + XS[2]) / 2, ym_t + 0.08, "win ½", ha="center", fontsize=10, color="#3E7C4A")
for x in (XS[0], XS[1]):
    arrow(ax, x + 0.55, YT, x + 0.55, YB + BH, color=RED); ax.text(x + 0.45, 2.05, "lose ½", ha="right", fontsize=10, color=RED)
arrow(ax, XS[0] + BW - 0.55, YB + BH, XS[0] + BW - 0.55, YT, color=NAVY); ax.text(XS[0] + BW - 0.45, 2.05, "win ¼ → D", ha="left", fontsize=10, color=NAVY)
arrow(ax, XS[1] + BW - 0.55, YB + BH, XS[1] + BW - 0.55, YT, color=NAVY); ax.text(XS[1] + BW - 0.45, 2.05, "win ¼ → A", ha="left", fontsize=10, color=NAVY)
arrow(ax, XS[1] + BW, ym_b, XS[2], ym_b, color=RED); ax.text((XS[1] + BW + XS[2]) / 2, ym_b + 0.08, "lose ¾", ha="center", fontsize=10, color=RED)
ax.plot([XS[0] + BW / 2, XS[0] + BW / 2], [YB, 0.12], color=RED, lw=1.3); ax.plot([XS[0] + BW / 2, XS[2] + BW / 2], [0.12, 0.12], color=RED, lw=1.3)
arrow(ax, XS[2] + BW / 2, 0.12, XS[2] + BW / 2, YB, color=RED); ax.text(5.0, 0.16, "lose ¾ (from B′)", ha="center", fontsize=10, color=RED)
fig.savefig(OUT + "fig09_markov_16_49.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# ---------------- fig10 XFA all-in vs R ----------------
fin = pd.read_csv(P + "results_final.csv"); z = fin[fin.edge == 0].iloc[0]
Rs = [1, 2, 3, 5]; meas = [z[f"allin_{r}to1"] for r in Rs]; fr_ = [z[f"allin_{r}to1_frictions"] for r in Rs]; ana = [0.9 * 2000 * r / (1 + r) for r in Rs]
fig, ax = plt.subplots(figsize=(8, 4)); rr_ = np.linspace(0.5, 8, 100)
ax.plot(rr_, 0.9 * 2000 * rr_ / (1 + rr_), color=GREY, ls="--", label="analytic 0.9·2000·R/(1+R)")
ax.plot(Rs, meas, "o", color=NAVY, ms=7, label="measured, no frictions (N = 100k)"); ax.plot(Rs, fr_, "s", color=AMBER, ms=6, label="measured, $30 fee + profit-since-payout")
ax.axhline(float(z.xfa_static_net), color=TEAL, ls=":", label=f"best static profile 2:1 $750 (${z.xfa_static_net:.0f})"); ax.axhline(1800, color=RED, lw=0.8, ls="-.", label="theoretical cap 0.9 × $2,000")
ax.set_xlabel("R of the day-one bet on the full $2,000 cushion"); ax.set_ylabel("net $ per XFA"); ax.set_ylim(600, 1900); ax.legend(frameon=False, fontsize=8, loc="upper left")
ax.set_title("XFA extraction: the day-one all-in reaches 0.9·2,000·R/(1+R) exactly; frictions cap the gain at high R", fontsize=9, color=GREY, loc="left")
fig.savefig(OUT + "fig10_xfa_allin.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# ---------------- fig11 time barrier ----------------
tb = pd.read_csv(P + "results_timebarrier.csv")
fig, ax = plt.subplots(figsize=(8, 4))
for rr, c in zip([1, 2, 3, 5], [GREY, NAVY, TEAL, AMBER]):
    s = tb[tb.rr == rr].sort_values("sigma_over_cushion"); ax.plot(s.sigma_over_cushion, s.net, marker="o", color=c, label=f"R = {rr}:1")
ax.axhline(float(z.xfa_static_net), color=RED, ls=":", label="static 2:1 $750 fallback"); ax.set_xscale("log"); ax.set_xticks([0.25, 0.5, 1, 2, 4, 8]); ax.set_xticklabels(["0.25", "0.5", "1", "2", "4", "8"])
ax.set_xlabel("s = session σ of the max-size position ÷ $2,000 cushion (log scale)"); ax.set_ylabel("net $ per XFA"); ax.legend(frameon=False, fontsize=8)
ax.set_title("Session time barrier: the day-one policy only beats the static profile once s ≥ ~0.75; R matters only for s ≥ 2", fontsize=9, color=GREY, loc="left")
fig.savefig(OUT + "fig11_timebarrier.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# ---------------- fig12 edge ladder final profile ----------------
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(fin.edge, fin.ev_attempt_static, marker="o", color=NAVY, label="Combine 1:1 $1,500 + static XFA 2:1 $750")
ax.plot(fin.edge, fin.ev_attempt_static_frictions, marker="s", color=AMBER, label="same, with payout frictions")
ax.axhline(0, color=GREY, lw=0.8); ax.set_xlabel("edge e (expected P&L per trade as a fraction of $ risked)"); ax.set_ylabel("expected net $ per Combine attempt")
ax.legend(frameon=False, fontsize=8); ax.set_title("Robustness to edge: the recommended profiles stay EV-positive down to e = −0.10 (N = 100k per point)", fontsize=9, color=GREY, loc="left")
fig.savefig(OUT + "fig12_edge_ladder.png", dpi=170, bbox_inches="tight"); plt.close(fig)

# ---------------- fig13 net distribution per attempt ----------------
from propsim import Rules, Policy, simulate_combine
from statepolicy import run_xfa, xfa_build_then_harvest
rng = np.random.default_rng(99); n = 50000
c = simulate_combine(Rules(), Policy(rr=1, risk=1500, trades_per_day=1), 0.0, n, rng)
net = -c["sub_fees"].copy(); m = int(c["passed"].sum())
x = run_xfa(Rules(), xfa_build_then_harvest(3, 2000, 1, 150, 1), m, rng, 250, "standard")
net[c["passed"]] += x["cash"] - 149
fig, ax = plt.subplots(figsize=(8, 3.8))
vals, cnts = np.unique(np.round(net, -1), return_counts=True)
ax.bar(vals, cnts / n, width=80, color=NAVY); ax.set_yscale("log"); ax.set_xlabel("net cash per Combine attempt ($)"); ax.set_ylabel("probability (log scale)")
ax.set_title(f"Distribution of net cash per attempt, Combine 1:1 $1,500 → XFA day-one 3:1 all-in (N = 50,000): mean ${net.mean():.0f}, P(net > 0) = {(net>0).mean():.1%}", fontsize=9, color=GREY, loc="left")
fig.savefig(OUT + "fig13_net_distribution.png", dpi=170, bbox_inches="tight"); plt.close(fig)
pd.DataFrame(dict(stat=["mean_net", "p_net_pos", "p_pass", "p_payout", "p5", "p50", "p95"],
                  value=[net.mean(), (net > 0).mean(), c["passed"].mean(), (net > 0).mean(), np.percentile(net, 5), np.percentile(net, 50), np.percentile(net, 95)])).to_csv(OUT + "fig13_stats.csv", index=False)
print("figures done")
