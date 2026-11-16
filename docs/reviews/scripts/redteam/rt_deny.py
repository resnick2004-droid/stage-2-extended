"""Red team: P under a uniform payout haircut (the expectation of per-payout denial with no closure), from U1's start
rows; and the all-or-nothing reading. Independent re-derivation of track C's AUDIT ESTIMATE (haircut column)."""
import numpy as np, pandas as pd
D = r"C:\Users\resni\AppData\Local\Temp\claude\197752aa8b2362c7\9862c1b3-c57d-4498-a2d7-44492c7a25e6\scratchpad\redteam"
st = pd.read_csv(D + r"\starts.csv", low_memory=False)
st = st[(st.arm == "verdict") & (st.observed >= 63)]
print(st[["pay_days", "payouts"]].head(3).to_string())
for cfg in ("p14", "p15", "p16"):
    s = st[st.config == cfg]
    out = []
    for p in (0.0, 0.10, 0.25, 0.50):
        ah = []
        for m in (1, 2, 3):
            net, fee = s[f"net_month_{m}"].values, s[f"fees_month_{m}"].values
            pay = net + fee
            ah.append(((1 - p) * pay - fee) > 0)
        P = np.mean(np.vstack(ah).mean(0))
        out.append(f"p={p:.2f}: haircut {P:.3f} all-or-nothing {(1 - p) * np.mean(np.vstack([s[f'net_month_{m}'].values > 0 for m in (1,2,3)]).mean(0)):.3f}")
    # break-even haircut where P falls to 0.5
    grid = np.linspace(0, 0.9, 901)
    Ps = [np.mean(np.vstack([((1 - q) * (s[f'net_month_{m}'].values + s[f'fees_month_{m}'].values) - s[f'fees_month_{m}'].values) > 0 for m in (1, 2, 3)]).mean(0)) for q in grid]
    print(cfg, "; ".join(out), "| haircut where P = 0.5:", grid[np.argmax(np.array(Ps) < 0.5)])
    j = s[s.start_date >= "2024-01-01"]
    Pj = [np.mean(np.vstack([((1 - q) * (j[f'net_month_{m}'].values + j[f'fees_month_{m}'].values) - j[f'fees_month_{m}'].values) > 0 for m in (1, 2, 3)]).mean(0)) for q in (0, 0.25, 0.5)]
    print("   judged block haircut 0 / 0.25 / 0.5:", np.round(Pj, 3))
