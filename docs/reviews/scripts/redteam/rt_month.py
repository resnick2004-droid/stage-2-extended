import numpy as np, pandas as pd
D = r"C:\Users\resni\AppData\Local\Temp\claude\197752aa8b2362c7\9862c1b3-c57d-4498-a2d7-44492c7a25e6\scratchpad\redteam"
st = pd.read_csv(D + r"\starts.csv", low_memory=False)
st = st[(st.arm == "verdict") & (st.observed >= 63)]
for cfg in ("p14", "p16"):
    s = st[st.config == cfg]
    sh = [round((s[f"net_month_{m}"] > 0).mean(), 3) for m in (1, 2, 3)]
    near = [round(((s[f"net_month_{m}"] <= 0) & (s[f"net_month_{m}"] > -250)).mean(), 3) for m in (1, 2, 3)]
    print(cfg, "share ahead m1-3", sh, "within $250 below zero m1-3", near, "bound on P gain", round(np.mean(near), 3))
