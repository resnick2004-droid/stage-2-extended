"""EXPLORATORY (phase 0 audit B, Q2): what goes with P among the designs near the top (P >= 0.60) -- cells_all.csv."""
import pandas as pd, numpy as np
from scipy.stats import spearmanr
t = pd.read_csv('cells_all.csv'); core = t[t.k<=7]
for name, d in [('core 61', core), ('P>=0.60 (22)', core[core.P>=0.60]), ('P>=0.55 (33)', core[core.P>=0.55]), ('all 67, P>=0.60', t[t.P>=0.60])]:
    out = {}
    for m in ['S1','S3a','S3b','S3c','S4a','S5a','S5b','S5c']:
        dd = d[['P',m]].dropna()
        out[m] = round(spearmanr(dd.P, dd[m]).statistic,2)
    print(name, len(d), out)
top = core[core.P>=0.60].sort_values('P', ascending=False)
print(top[['family','cell','base','P','S1','S3a','S3c','S5a']].round(3).to_string(index=False))
# ranking by S3c vs by P among the 22: where does the P-best sit by S3c?
top = top.assign(rank_P=top.P.rank(ascending=False), rank_S3c=top.S3c.rank(ascending=False))
print(top[['cell','rank_P','rank_S3c']].to_string(index=False))
