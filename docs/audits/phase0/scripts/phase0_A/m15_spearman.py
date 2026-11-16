import os
import numpy as np
import pandas as pd
pd.set_option('display.width', 250)
R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
ud = pd.read_csv(os.path.join(R, 'user_drivers.csv'), low_memory=False,
                 usecols=['section', 'subject', 'subject_kind', 'measure', 'value', 'arm', 'block', 'label', 'n', 'lo', 'hi'])
dt = ud[(ud.section == 'design_table') & (ud.arm == 'verdict') & (ud.block == 'all')]
piv = dt.pivot_table(index='subject', columns='measure', values='value', aggfunc='first')
lab = dt.groupby('subject')['label'].first()
print('designs:', len(piv), ' labelled:', lab.dropna().to_dict())
print('NaN counts:', piv.isna().sum().to_dict())

def spearman(a, b):
    m = a.notna() & b.notna()
    ra, rb = a[m].rank(), b[m].rank()
    return float(np.corrcoef(ra, rb)[0, 1]), int(m.sum())

for s in ['S1', 'S3a', 'S3b', 'S3c', 'S4a', 'S4b', 'S5a']:
    r, n = spearman(piv['P'], piv[s])
    print(f'spearman P~{s}: {r:.6f} n={n}')

# standardised OLS of P on S1, S3a, S3c, S5a
X = piv[['S1', 'S3a', 'S3c', 'S5a']]
y = piv['P']
m = X.notna().all(axis=1) & y.notna()
Xs = (X[m] - X[m].mean()) / X[m].std(ddof=0)
ys = (y[m] - y[m].mean()) / y[m].std(ddof=0)
A = np.column_stack([np.ones(m.sum()), Xs.values])
beta, *_ = np.linalg.lstsq(A, ys.values, rcond=None)
res = ys.values - A @ beta
r2 = 1 - (res ** 2).sum() / ((ys.values - ys.values.mean()) ** 2).sum()
print('beta (S1,S3a,S3c,S5a):', np.round(beta[1:], 6), 'r2:', round(r2, 6), 'n:', int(m.sum()))

bd = ud[(ud.section == 'between_designs') & (ud.subject == 'without_lucid')]
print('\nwithout_lucid subject:')
print(bd[['measure', 'value', 'n', 'lo', 'hi']].to_string())
