"""EXPLORATORY (phase 0 audit B): build a per-cell scorecard table from the family files' `cell` sections (block all)
and the user_drivers design_table, to test S3c against P."""
import pandas as pd, glob, os, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_columns',80); pd.set_option('display.max_rows',500)
D = r"C:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
rows=[]
for f in sorted(glob.glob(os.path.join(D,'u_*.csv'))):
    df = pd.read_csv(f, low_memory=False)
    if 'section' not in df.columns or 'cell' not in set(df.section): continue
    c = df[(df.section=='cell')]
    if 'block' in c.columns: c = c[c.block=='all']
    lab = c['label'] if 'label' in c.columns else pd.Series('', index=c.index)
    for _,r in c.iterrows():
        rows.append(dict(file=os.path.basename(f), cell=r.cell, base=r.base, role=r.role, counted=r.counted, label=(r['label'] if 'label' in c.columns else np.nan), measure=r.measure, value=r.value, n=r.n))
t = pd.DataFrame(rows)
w = t.pivot_table(index=['file','cell','counted'], columns='measure', values='value', aggfunc='first').reset_index()
lab = t.groupby(['file','cell'])['label'].first().reset_index()
base = t.groupby(['file','cell'])['base'].first().reset_index()
w = w.merge(lab,on=['file','cell']).merge(base,on=['file','cell'])
print(w.to_string())
w.to_csv('family_cells.csv', index=False)
dd = pd.read_csv(os.path.join(D,'user_drivers.csv'), low_memory=False)
dt = dd[dd.section=='design_table']
dw = dt.pivot_table(index=['subject','family','base'], columns='measure', values='value', aggfunc='first').reset_index()
lab2 = dt.groupby('subject')['label'].first().reset_index()
dw = dw.merge(lab2, on='subject')
dw.to_csv('design_table_wide.csv', index=False)
print(dw.to_string())
