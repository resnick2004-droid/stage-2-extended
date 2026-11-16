import pandas as pd, glob, os
pd.set_option('display.width',250); pd.set_option('display.max_columns',80); pd.set_option('display.max_rows',500)
D = r"C:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
out=[]
for f in sorted(glob.glob(os.path.join(D,'u_*.csv'))):
    df = pd.read_csv(f, low_memory=False)
    if 'section' not in df.columns or 'judged' not in set(df.section): continue
    j = df[(df.section=='judged')&(df.measure=='P')]
    for _,r in j.iterrows():
        out.append(dict(file=os.path.basename(f), cell=r.cell, value=r.value, ref=r.reference_value, diff=r.difference, lower=r.lower, level=r.level, k=r.k, n=r.n, first=r.first_date, last=r.last_date))
    v = df[(df.section=='verdict')&(df.line=='verdict')]
    for _,r in v.iterrows():
        out[-1].update(base=r.base, family=r.family, verdict=r.verdict, cells=r.cells, program_cells=r.program_cells)
o = pd.DataFrame(out)
from scipy.stats import norm
o['z']=norm.isf(o.level)
o['se_implied']=(o['diff']-o['lower'])/o['z']
print(o.to_string())
