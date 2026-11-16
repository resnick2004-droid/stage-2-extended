"""Figures 14-17 for the value-of-edge material, drawn from the result CSVs."""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE) + "/"; OUT = HERE + "/figs/"
NAVY, TEAL, AMBER, GREY, RED, GREEN = "#14343B", "#2E7D8C", "#D9822B", "#5F6B6D", "#B3412E", "#3E7C4A"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": GREY, "axes.labelcolor": NAVY, "xtick.color": GREY, "ytick.color": GREY})
C = pd.read_csv(P + "edge/results_combine_edge.csv"); C["prof"] = C.R.map("{:g}".format) + ":1 $" + C.risk.map("{:.0f}".format)
V = pd.read_csv(P + "edge/results_value_of_edge.csv")
B = pd.concat([pd.read_csv(P + "edge/results_payout_buffer_exploratory.csv"), pd.read_csv(P + "edge/results_payout_buffer_extension.csv")])
S = pd.read_csv(P + "edge/results_sample_size.csv")

# fig14 — pass probability vs edge
fig, ax = plt.subplots(figsize=(8, 4.4))
show = [("1.5:1 $500", NAVY, "-"), ("2:1 $500", TEAL, "-"), ("2:1 $750", AMBER, "-"), ("1.5:1 $1000", GREEN, "-"), ("3:1 $500", GREY, "-"), ("3:1 $1000", RED, "-"), ("1:1 $1500", "#999999", "--")]
for prof, col, ls in show:
    s = C[C.prof == prof].sort_values("edge")
    ax.plot(s.edge * 100, s.p_pass * 100, ls, color=col, marker="o", ms=4, lw=2, label=prof + (" (reference, not admissible)" if prof == "1:1 $1500" else ""))
ax.set_xlabel("edge e (% of $ risked per trade, after costs)"); ax.set_ylabel("Combine pass probability (%)")
ax.legend(frameon=False, fontsize=9, ncol=2, loc="upper left")
fig.savefig(OUT + "fig14_pass_vs_edge.png", dpi=190, bbox_inches="tight"); plt.close(fig)

# fig15 — EV per attempt: structural vs edge (best pre-registered admissible pair, standard path)
a = V[(V.path == "standard") & (V.admissible) & (~V.exploratory)]
b = a.loc[a.groupby("edge").ev_per_attempt.idxmax()].sort_values("edge")
fig, ax = plt.subplots(figsize=(8, 4.4)); x = np.arange(len(b)); lab = [f"{e*100:g} %" for e in b.edge]
ax.bar(x, b.ev_structural, color=GREY, label="structural (present at zero edge; prohibited to exploit)")
ax.bar(x, b.ev_from_edge, bottom=b.ev_structural, color=NAVY, label="from the edge")
for i, (t, sh) in enumerate(zip(b.ev_per_attempt, b.edge_share_of_ev)):
    ax.text(i, t + 40, f"${t:,.0f}\n{sh*100:.0f} % edge", ha="center", va="bottom", fontsize=9, color=NAVY)
ax.set_xticks(x); ax.set_xticklabels(lab); ax.set_xlabel("edge e"); ax.set_ylabel("EV per Combine attempt ($)")
ax.set_ylim(0, b.ev_per_attempt.max() * 1.25); ax.legend(frameon=False, fontsize=9, loc="upper left")
fig.savefig(OUT + "fig15_edge_share.png", dpi=190, bbox_inches="tight"); plt.close(fig)

# fig16 — payout buffer
B["prof"] = B.R.map("{:g}".format) + ":1 $" + B.risk.map("{:.0f}".format)
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=False)
for ax, e in zip(axes, [0.10, 0.20]):
    for prof, col in [("1.5:1 $500", NAVY), ("2:1 $300", TEAL), ("2:1 $150", AMBER), ("1.5:1 $1000", GREEN), ("2:1 $750", GREY)]:
        s = B[(B.prof == prof) & (np.isclose(B.edge, e))].groupby("keep_balance").cash_per_year.mean().sort_index()
        ax.plot(s.index / 1000, s.values, marker="o", ms=4, lw=2, color=col, label=prof)
    ax.set_title(f"edge {e*100:g} %", color=NAVY, fontsize=12); ax.set_xlabel("buffer kept in the account ($ thousands)")
axes[0].set_ylabel("realised cash per funded account per year ($)"); axes[0].legend(frameon=False, fontsize=9)
fig.savefig(OUT + "fig16_payout_buffer.png", dpi=190, bbox_inches="tight"); plt.close(fig)

# fig17 — sample size
fig, ax = plt.subplots(figsize=(8, 4.2))
for R, col in [(1.5, NAVY), (2.0, TEAL), (3.0, RED)]:
    s = S[S.R == R].sort_values("true_edge")
    ax.plot(s.true_edge * 100, s.trades_lower_bound_above_half_edge, marker="o", lw=2, color=col, label=f"R = {R:g}:1")
ax.set_yscale("log"); ax.set_xlabel("true edge e (%)"); ax.set_ylabel("trades needed (log scale)")
for yv, txt in [(252, "1 year at 1 trade/day"), (2520, "10 years")]:
    ax.axhline(yv, color=GREY, ls=":", lw=1); ax.text(19.8, yv * 1.08, txt, ha="right", fontsize=9, color=GREY)
ax.legend(frameon=False, fontsize=10); ax.set_xticks([5, 10, 20])
fig.savefig(OUT + "fig17_sample_size.png", dpi=190, bbox_inches="tight"); plt.close(fig)
print("edge figures written")
