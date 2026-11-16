"""EXPLORATORY (phase 0 audit B, Q2): S3c as a kill-screen (drop cells with S3c below R*'s) vs as a ranking target."""
import pandas as pd, numpy as np
t = pd.read_csv('cells_all.csv')
r = t[t.cell=='p14'].iloc[0]
o = t[t.cell!='p14']
print('cells other than P-14:', len(o))
print('S3c > P-14:', (o.S3c>r.S3c).sum(), ' of which P > P-14:', ((o.S3c>r.S3c)&(o.P>r.P)).sum())
print('S3c <= P-14:', (o.S3c<=r.S3c).sum(), ' of which P > P-14:', ((o.S3c<=r.S3c)&(o.P>r.P)).sum())
print(o[o.P>r.P][['family','cell','P','S3c','S1','S3a','S5a']].to_string(index=False))
print('P-14', r.P, r.S3c)
# rank of P-14 and of the P-best by S3c among top region
top = t[(t.P>=0.60)&(t.k<=7)].copy()
top['rS3c']=top.S3c.rank(ascending=False); top['rP']=top.P.rank(ascending=False)
print(top[top.cell.isin(['p14','nobudget_p14','p16','seats1','budget10'])][['cell','rP','rS3c']])
# the top-5 by S3c in the whole core 61: their P and rank in P
core=t[t.k<=7].copy(); core['rP']=core.P.rank(ascending=False); core['rS3c']=core.S3c.rank(ascending=False)
print(core.sort_values('rS3c').head(5)[['cell','family','P','S3c','rP']].to_string(index=False))
