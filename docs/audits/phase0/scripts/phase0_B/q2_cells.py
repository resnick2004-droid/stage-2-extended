"""EXPLORATORY (phase 0 audit B, Q2): one row per counted cell (verdict arm, block all) of the nine family files
plus the three rows to beat -- the scorecard as each family file's `cell` section holds it."""
import pandas as pd, glob, os, numpy as np, json
D = r"C:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
K=['P','S1','S3a','S3b','S3c','S4a','S4b','S5a','S5b','S5c']
FAM = {'u_budget.csv':(1,'budget'),'u_entry.csv':(2,'entry'),'u_seats.csv':(3,'seats'),'u_hours.csv':(4,'hours'),
       'u_firms.csv':(5,'firms'),'u_consistency.csv':(6,'consistency'),'u_plan.csv':(7,'plan'),'u_limit.csv':(8,'limit'),
       'u_resolve.csv':(9,'resolve')}
out=[]
for f,(k,name) in FAM.items():
    df = pd.read_csv(os.path.join(D,f), low_memory=False)
    c = df[(df.section=='cell')&(df.block=='all')]
    keep = c[(c.role=='family cell')]
    if k==1:
        keep = pd.concat([keep, c[c.cell.isin(['p14','p15','p16'])]])
    for cell,g in keep.groupby('cell'):
        r = {'file':f,'k':k if cell not in ('p14','p15','p16') else 0,'family':name if cell not in ('p14','p15','p16') else 'rows_to_beat','cell':cell,
             'base':g['base'].iloc[0],'label':(g['label'].iloc[0] if 'label' in g.columns else np.nan),
             'counted':g['counted'].iloc[0],'overrides':g['overrides'].iloc[0]}
        for m in K:
            v = g.loc[g.measure==m,'value']
            r[m] = float(v.iloc[0]) if len(v) else np.nan
        out.append(r)
t = pd.DataFrame(out)
t.to_csv('cells_all.csv', index=False)
print(t.groupby(['k','family']).size(), len(t))
print(t.label.value_counts(dropna=False))
