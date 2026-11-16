"""Gate-1 static policy grid.

Usage: python run_grid.py [--n 10000] [--horizon 250] [--out results]
"""
import argparse, itertools, time
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from propsim import (Rules, Policy, simulate_combine, simulate_xfa,
                     summarize_combine, summarize_xfa, attempt_ev)

RRS = [0.5, 1.0, 1.5, 2.0, 3.0]
RISKS = [50, 100, 200, 300, 500, 750, 1000, 1500]
DAY_RULES = {                     # (trades_per_day, stop_on_win, stop_on_loss)
    "1/day":        (1, False, False),
    "3/day":        (3, False, False),
    "3/day stopW":  (3, True, False),
    "6/day":        (6, False, False),
}
PATHS = ["standard", "consistency"]
EDGE_LADDER = [-0.10, -0.05, -0.02, 0.0, 0.02, 0.05]


def run_cell(rules, rr, risk, rule, edge, n, horizon, seed):
    tpd, sw, sl = DAY_RULES[rule]
    rng = np.random.default_rng(seed)
    pol = Policy(rr=rr, risk=risk, trades_per_day=tpd, stop_day_on_win=sw, stop_day_on_loss=sl)
    c = summarize_combine(simulate_combine(rules, pol, edge, n, rng))
    row = dict(rr=rr, risk=risk, day_rule=rule, edge=edge, **{f"c_{k}": v for k, v in c.items()})
    for path in PATHS:
        pol.payout_path = path
        x = summarize_xfa(simulate_xfa(rules, pol, edge, n, rng, horizon_days=horizon))
        ev = attempt_ev(c, x, rules)
        tag = "std" if path == "standard" else "cons"
        row.update({f"x{tag}_{k}": v for k, v in x.items()})
        row.update({f"{tag}_{k}": v for k, v in ev.items()})
    row["best_ev"] = max(row["std_ev_per_attempt"], row["cons_ev_per_attempt"])
    row["best_path"] = "standard" if row["std_ev_per_attempt"] >= row["cons_ev_per_attempt"] else "consistency"
    return row


def heatmap(df, col, title, fname, fmt="{:.2f}", vmin=None):
    rules = list(DAY_RULES)
    fig, axes = plt.subplots(1, len(rules), figsize=(4.2 * len(rules), 4.2), sharey=True)
    vmin, vmax = (df[col].min() if vmin is None else vmin), df[col].max()
    for ax, rule in zip(axes, rules):
        piv = df[df.day_rule == rule].pivot(index="rr", columns="risk", values=col)
        im = ax.imshow(piv.values, aspect="auto", cmap="viridis", vmin=vmin, vmax=vmax)
        ax.set_xticks(range(len(piv.columns))); ax.set_xticklabels([f"${c}" for c in piv.columns], rotation=45)
        ax.set_yticks(range(len(piv.index))); ax.set_yticklabels([f"{r}:1" for r in piv.index])
        ax.set_title(rule); ax.set_xlabel("$ risk")
        for i in range(piv.shape[0]):
            for j in range(piv.shape[1]):
                ax.text(j, i, fmt.format(piv.values[i, j]), ha="center", va="center", fontsize=7, color="w")
    axes[0].set_ylabel("R:R")
    fig.suptitle(title); fig.colorbar(im, ax=axes, shrink=0.8)
    fig.savefig(fname, dpi=130, bbox_inches="tight"); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--horizon", type=int, default=250)
    ap.add_argument("--out", default="results")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--plot-only", action="store_true", help="redraw the heatmaps from the stored grid CSV without rerunning")
    a = ap.parse_args()
    if a.plot_only:
        df = pd.read_csv(f"{a.out}_grid_edge0.csv")
        heatmap(df, "c_p_pass", "Combine pass probability (edge 0)", f"{a.out}_pass_rate.png")
        heatmap(df, "best_ev", "Expected net $ per Combine attempt (edge 0, best payout path)", f"{a.out}_ev.png", "{:.0f}", vmin=-300)
        heatmap(df, "c_mean_sub_fees", "Expected subscription $ per attempt", f"{a.out}_subfees.png", "{:.0f}")
        print("plots redrawn from", f"{a.out}_grid_edge0.csv"); return
    rules = Rules()
    t0 = time.time()

    rows = []
    for i, (rr, risk, rule) in enumerate(itertools.product(RRS, RISKS, DAY_RULES)):
        rows.append(run_cell(rules, rr, risk, rule, 0.0, a.n, a.horizon, a.seed + i))
    df = pd.DataFrame(rows)
    df.to_csv(f"{a.out}_grid_edge0.csv", index=False)
    print(f"grid done: {len(df)} cells in {time.time()-t0:.0f}s")

    # Bound checks
    viol = df[df.c_p_pass > 0.40 + 4 * df.c_p_pass_se]
    print("pass-rate bound violations:", len(viol))
    print("max XFA gross (std/cons):", df.xstd_mean_gross.max().round(1), df.xcons_mean_gross.max().round(1))

    # Edge ladder on top-5 EV cells and top-3 pass-rate cells
    top_ev = df.nlargest(5, "best_ev")[["rr", "risk", "day_rule"]].values.tolist()
    top_pass = df.nlargest(3, "c_p_pass")[["rr", "risk", "day_rule"]].values.tolist()
    ladder = []
    for j, (rr, risk, rule) in enumerate({tuple(x) for x in top_ev + top_pass}):
        for e in EDGE_LADDER:
            ladder.append(run_cell(rules, rr, risk, rule, e, a.n, a.horizon, a.seed + 10_000 + j))
    ld = pd.DataFrame(ladder)
    ld.to_csv(f"{a.out}_edge_ladder.csv", index=False)
    print(f"edge ladder done in {time.time()-t0:.0f}s")

    heatmap(df, "c_p_pass", "Combine pass probability (edge 0)", f"{a.out}_pass_rate.png")
    heatmap(df, "best_ev", "Expected net $ per Combine attempt (edge 0, best payout path)", f"{a.out}_ev.png", "{:.0f}", vmin=-300)
    heatmap(df, "c_mean_sub_fees", "Expected subscription $ per attempt", f"{a.out}_subfees.png", "{:.0f}")

    # Console summary
    pd.set_option("display.width", 200); pd.set_option("display.max_columns", 30)
    cols = ["rr", "risk", "day_rule", "c_p_pass", "c_mean_days", "c_mean_sub_fees",
            "xstd_mean_cash", "xcons_mean_cash", "best_path", "best_ev"]
    print("\n=== Top 12 by EV per attempt ===")
    print(df.nlargest(12, "best_ev")[cols].to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print("\n=== Top 8 by pass rate ===")
    print(df.nlargest(8, "c_p_pass")[cols].to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print("\n=== Edge ladder (best EV per attempt) ===")
    print(ld.pivot_table(index=["rr", "risk", "day_rule"], columns="edge", values="best_ev")
            .to_string(float_format=lambda v: f"{v:.0f}"))


if __name__ == "__main__":
    main()
