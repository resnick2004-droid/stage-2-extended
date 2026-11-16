"""EXPLORATORY (phase 0 audit B, Q2): is S3c's rank correlation with P a sound screen or partly mechanical/driven by a
few families?  Source: cells_all.csv (built by q2_cells.py from results/u_*.csv sections `cell`, block `all`,
role `family cell`, verdict arm; plus the three rows to beat)."""
import pandas as pd, numpy as np
from scipy.stats import spearmanr
pd.set_option('display.width',250); pd.set_option('display.max_rows',500)
t = pd.read_csv('cells_all.csv')
core = t[t.k<=7].copy()          # the 61 designs of user_drivers between_designs
held = t[t.k>=8].copy()
def sp(d, a='P', b='S3c'):
    d = d[[a,b]].dropna()
    if len(d)<3: return np.nan, len(d)
    return spearmanr(d[a], d[b]).statistic, len(d)
print('n core', len(core), 'Spearman P~S3c core', sp(core))
print('check vs user_drivers 0.764550')
# leave one family out
print('\n-- leave one family out (core 61)')
for fam in sorted(core.family.unique()):
    print(f'{fam:14s}', 'n_out', (core.family==fam).sum(), 'rho without', np.round(sp(core[core.family!=fam])[0],3))
# only the cells of families with P not at the floor
print('\n-- subsets')
for name, d in [('P>=0.55', core[core.P>=0.55]), ('P>=0.60', core[core.P>=0.60]), ('P>=0.62', core[core.P>=0.62]),
                ('without consistency, plan', core[~core.family.isin(['consistency','plan'])]),
                ('without consistency, plan, firms', core[~core.family.isin(['consistency','plan','firms'])]),
                ('base p14 cells + p14', core[(core.base=='p14')|(core.cell=='p14')]),
                ('base p16 cells + p16', core[(core.base=='p16')|(core.cell=='p16')]),
                ('fee levers: budget, entry, seats', core[core.family.isin(['budget','entry','seats'])]),
                ('trading levers: hours, plan, consistency', core[core.family.isin(['hours','plan','consistency'])]),
                ('held out: limit, resolve (+3 rows)', pd.concat([held, core[core.family=='rows_to_beat']])),
                ('all 67', t)]:
    r, n = sp(d)
    print(f'{name:45s} n={n:3d} rho={r:.3f}')
# within family
print('\n-- within each family (P~S3c spearman)')
for fam, g in core.groupby('family'):
    r, n = sp(g)
    print(f'{fam:14s} n={n:2d} rho={r if np.isfinite(r) else float("nan"):.3f}  P range {g.P.min():.3f}-{g.P.max():.3f}  S3c range {g.S3c.min():.3f}-{g.S3c.max():.3f}')
# pooled within: rank within family, correlate ranks (families with >=3)
pw = []
for fam, g in core.groupby('family'):
    g = g[['P','S3c']].dropna()
    if len(g) < 3: continue
    pw.append(pd.DataFrame({'P': g.P.rank()-g.P.rank().mean(), 'S3c': g.S3c.rank()-g.S3c.rank().mean()}))
pw = pd.concat(pw)
print('pooled within-family (demeaned ranks) pearson', np.corrcoef(pw.P, pw.S3c)[0,1], len(pw))
# between family means
fm = core.groupby('family')[['P','S3c']].mean()
print('between family means spearman', spearmanr(fm.P, fm.S3c).statistic, len(fm))
# the rows to beat order: P vs S3c
print('\n-- rows to beat')
print(core[core.family=='rows_to_beat'][['cell','P','S3c']])
# Q: among cells with P within 0.05 of p14, does S3c above p14's predict higher P?
print('\n-- cells with S3c above P-14 (1.851) and their P against P-14 0.671')
hi = core[core.S3c>1.851329]
print(len(hi), 'of', core.S3c.notna().sum(), 'cells have S3c > P-14; of them P > P-14:', (hi.P>0.671168).sum())
lo = core[core.S3c<=1.851329]
print(len(lo), 'cells have S3c <= P-14; of them P > P-14:', (lo.P>0.671168).sum())
print(core[core.P>0.671168][['family','cell','base','P','S3c']].to_string())
# top-10 by S3c and their P
print('\n-- top 12 by S3c'); print(core.sort_values('S3c',ascending=False)[['family','cell','base','label','P','S3c','S1']].head(12).to_string())
print('\n-- top 12 by P'); print(core.sort_values('P',ascending=False)[['family','cell','base','label','P','S3c','S1']].head(12).to_string())
print('\n-- bottom 15 by P'); print(core.sort_values('P')[['family','cell','base','P','S3c']].head(15).to_string())
print('\n-- held out cells'); print(held[['family','cell','base','P','S3c']].to_string())
# family-level bootstrap of the spearman for the subsets (whole families resampled, seed fixed here)
rng = np.random.default_rng(20261115)
def famboot(d, draws=2000):
    fams = d.family.unique(); out=[]
    for _ in range(draws):
        pick = rng.choice(fams, size=len(fams), replace=True)
        dd = pd.concat([d[d.family==f] for f in pick])
        if dd[['P','S3c']].dropna().shape[0] >= 4 and dd.S3c.nunique()>1 and dd.P.nunique()>1:
            out.append(spearmanr(dd.P, dd.S3c).statistic)
    return np.nanpercentile(out,[2.5,97.5])
print('\nfamily bootstrap core', famboot(core))
print('family bootstrap P>=0.60', famboot(core[core.P>=0.60]))
