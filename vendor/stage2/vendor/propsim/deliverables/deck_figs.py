import os
HERE = os.path.dirname(os.path.abspath(__file__))
import numpy as np, pandas as pd, matplotlib, sys
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(HERE))
P = os.path.dirname(HERE) + "/"; OUT = HERE + "/figs/"
NAVY, TEAL, AMBER, GREY, RED = "#14343B", "#2E7D8C", "#D9822B", "#5F6B6D", "#B3412E"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": GREY, "axes.labelcolor": NAVY, "xtick.color": GREY, "ytick.color": GREY, "axes.titlesize": 13})

# barrier race, sized 6.6 x 3.1 in
fig, ax = plt.subplots(figsize=(6.6, 3.1))
rng = np.random.default_rng(4); t = np.linspace(0, 1, 400); path = np.cumsum(rng.normal(0, 60, 400)); path -= path[0]
ax.plot(t, path, color=NAVY, lw=1.6); ax.axhline(1500, xmax=0.72, color="#3E7C4A", ls="--", lw=1.8); ax.axhline(-1500, xmax=0.72, color=GREY, ls=":", lw=1.8); ax.axhline(-500, xmax=0.72, color=RED, ls="--", lw=1.8)
ax.text(1.03, 1500, "target +W = R·r", va="center", color="#3E7C4A", fontsize=12); ax.text(1.03, -1500, "chosen stop −r", va="center", color=GREY, fontsize=12); ax.text(1.03, -500, "floor: room c = B − F", va="center", color=RED, fontsize=12)
ax.set_xlim(0, 1.4); ax.set_ylim(-1900, 1900); ax.set_xlabel("session time"); ax.set_ylabel("trade P&L ($)"); ax.set_xticks([])
fig.savefig(OUT + "s_barrier_race.png", dpi=220, bbox_inches="tight"); plt.close(fig)

# EV heatmap, two panels, 8.6 x 3.6 in
g = pd.read_csv(P + "results_grid_edge0.csv")
fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.6), sharey=True)
vmin, vmax = -300, g.best_ev.max()
for ax, rule in zip(axes, ["1/day", "3/day"]):
    piv = g[g.day_rule == rule].pivot(index="rr", columns="risk", values="best_ev")
    im = ax.imshow(piv.values, aspect="auto", cmap="viridis", vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(piv.columns))); ax.set_xticklabels([f"${c}" for c in piv.columns], rotation=45, fontsize=10)
    ax.set_yticks(range(len(piv.index))); ax.set_yticklabels([f"{r}:1" for r in piv.index], fontsize=11)
    ax.set_title(f"{rule}", fontsize=13, color=NAVY); ax.set_xlabel("$ risk per trade", fontsize=11)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.values[i, j]; txt = f"{v:.0f}" if v > -999 else f"{v/1000:.1f}k"; ax.text(j, i, txt, ha="center", va="center", fontsize=9, color="white" if (v - vmin) / (vmax - vmin) < 0.6 else "black")
axes[0].set_ylabel("R:R", fontsize=12); cb = fig.colorbar(im, ax=axes, shrink=0.9, pad=0.02); cb.set_label("net $ per attempt", fontsize=10)
fig.savefig(OUT + "s_ev_heatmap.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# net distribution, 7.6 x 3.8 in
from propsim import Rules, Policy, simulate_combine
from statepolicy import run_xfa, xfa_build_then_harvest
rng = np.random.default_rng(99); n = 50000
c = simulate_combine(Rules(), Policy(rr=1, risk=1500, trades_per_day=1), 0.0, n, rng)
net = -c["sub_fees"].copy(); m = int(c["passed"].sum())
x = run_xfa(Rules(), xfa_build_then_harvest(3, 2000, 1, 150, 1), m, rng, 250, "standard")
net[c["passed"]] += x["cash"] - 149
fig, ax = plt.subplots(figsize=(7.6, 3.8))
vals, cnts = np.unique(np.round(net, -1), return_counts=True)
ax.bar(vals, cnts / n, width=80, color=NAVY); ax.set_yscale("log"); ax.set_xlabel("net cash per Combine attempt ($)"); ax.set_ylabel("probability (log scale)")
ax.annotate("failed Combine: −$49", xy=(-49, 0.6), xytext=(1500, 0.5), fontsize=11, color=GREY, arrowprops=dict(arrowstyle="->", color=GREY))
ax.annotate("passed, XFA died day one: −$198", xy=(-198, 0.2), xytext=(1500, 0.12), fontsize=11, color=GREY, arrowprops=dict(arrowstyle="->", color=GREY))
ax.text(6000, 0.02, "paid out (≈ 8 % of attempts)", fontsize=11, color=NAVY, ha="center")
fig.savefig(OUT + "s_net_distribution.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("slide figs done")
