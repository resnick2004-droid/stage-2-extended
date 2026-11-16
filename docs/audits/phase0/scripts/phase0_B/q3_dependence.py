"""EXPLORATORY (phase 0 audit B, Q3): dependence of the per-start paired difference in P and the honesty of the
63-session moving-block bootstrap.  Source: results/user_journey.csv section start, arm verdict (starts.csv)."""
import pandas as pd, numpy as np
from scipy.stats import norm
s = pd.read_csv('starts.csv')
s['start_date'] = pd.to_datetime(s.start_date)
def ahead(cfg, arm='verdict'):
    d = s[(s.config==cfg)&(s.arm==arm)&(s.observed>=63)].sort_values('start_day')
    a = ((d.net_month_1>0).astype(float)+(d.net_month_2>0)+(d.net_month_3>0))/3.0
    return pd.Series(a.values, index=d.start_date.values)
A = {c: ahead(c) for c in ['p14','p15','p16','p13','p16_4+0','p16_funded_cap','p16_5+1','rc_s150_london']}
A['p14_point'] = ahead('p14','point')
def acf(x, maxlag):
    x = np.asarray(x,float); x = x - x.mean(); n=len(x); v = (x*x).sum()/n
    return np.array([ (x[:n-k]*x[k:]).sum()/n/v for k in range(maxlag+1)])
def bartlett_lrv(x, L):
    r = acf(x, L); w = 1 - np.arange(L+1)/(L+1)
    g0 = np.var(x)
    return g0*(1 + 2*np.sum(w[1:]*r[1:]))
def batch_var(x, b):
    x = np.asarray(x,float); m = len(x)//b
    if m < 2: return np.nan
    bm = x[:m*b].reshape(m,b).mean(axis=1)
    return b*np.var(bm, ddof=1)    # long-run variance estimate
def block_indices(n, b, draws, seed):
    rng = np.random.default_rng(seed); k = -(-n//b)
    first = rng.integers(0, n-b+1, size=(draws,k))
    return (first[:,:,None]+np.arange(b)[None,None,:]).reshape(draws,k*b)[:,:n]
def mbb(x, b, draws=2000, seed=20261700):
    x = np.asarray(x,float); idx = block_indices(len(x), b, draws, seed)
    return x[idx].mean(axis=1)
judged_from = pd.Timestamp('2024-01-01')
def pair(a, b):
    d = (A[a] - A[b]).dropna()
    return d
print('=== P-14 minus P-16, verdict, per-start (months ahead of 3)/3, starts with >=63 sessions')
d_all = pair('p14','p16')
d_j = d_all[d_all.index >= judged_from]
print('n all', len(d_all), 'first', d_all.index.min().date(), 'last', d_all.index.max().date())
print('n judged', len(d_j), 'first', d_j.index.min().date(), 'last', d_j.index.max().date())
print('mean diff all %.4f judged %.4f' % (d_all.mean(), d_j.mean()))
print('P14 judged %.4f P16 judged %.4f' % (A['p14'][A['p14'].index>=judged_from].mean(), A['p16'][A['p16'].index>=judged_from].mean()))
lags = [1,2,5,10,21,42,63,84,105,126,168,189,252]
for name, x in [('all', d_all.values), ('judged', d_j.values)]:
    r = acf(x, 260)
    print(name, 'acf', ' '.join(f'{k}:{r[k]:.2f}' for k in lags if k < len(x)))
    fz = np.argmax(r[1:] <= 0)+1
    print(name, 'first lag with acf<=0:', fz, ' sum of acf to first zero:', round(r[1:fz].sum(),1))
    v0 = np.var(x)
    for L in (21, 63, 126, 189, 252):
        lrv = bartlett_lrv(x, L)
        print(f'  {name} Bartlett L={L}: LRV/var={lrv/v0:6.1f}  n_eff={len(x)*v0/lrv:6.1f}  SE(mean)={np.sqrt(lrv/len(x)):.4f}')
    for b in (21, 63, 126, 189):
        bv = batch_var(x, b)
        print(f'  {name} batch means b={b}: m={len(x)//b} LRV/var={bv/v0:6.1f} n_eff={len(x)*v0/bv:6.1f} SE={np.sqrt(bv/len(x)):.4f}')
    for b in (1, 21, 63, 126, 189, 252):
        bt = mbb(x, b)
        print(f'  {name} MBB b={b}: SE={bt.std(ddof=1):.4f}  n_eff={v0/bt.var(ddof=1):6.1f}')
# naive iid SE
print('iid SE judged', np.std(d_j.values)/np.sqrt(len(d_j)))
# The one-sided level of family k=10
lev = 0.05/110
z = norm.isf(lev); zb = norm.isf(0.2)
print('level', lev, 'z', z)
# MDD for several pairs on judged block (SE from MBB b=63 and Bartlett L=126)
print('\n=== MDD in P on the judged block, one-sided 0.05/110, 80% power: (z_a + z_0.8) * SE')
for a,b in [('p14','p16'),('p14','p15'),('p14','p13'),('p16','p16_4+0'),('p16','p16_funded_cap'),('p16','p16_5+1'),('p14','p14_point'),('p15','p16')]:
    d = pair(a,b); d = d[d.index>=judged_from].values
    se63 = mbb(d,63).std(ddof=1); se126 = mbb(d,126).std(ddof=1); seB = np.sqrt(bartlett_lrv(d,126)/len(d))
    print(f'{a:>8s} - {b:15s} n={len(d)} diff={d.mean():+.4f} sd/start={d.std():.3f} SE63={se63:.4f} SE126={se126:.4f} SE_BartL126={seB:.4f}  MDD(63)={(z+zb)*se63:.3f} MDD(126)={(z+zb)*se126:.3f}  thresh(50%pow,63)={z*se63:.3f}')
# Monte Carlo instability of the 0.05/110 lower limit with 2000 draws
print('\n=== the one-sided lower limit at 0.05/110 from 2000 draws (np.percentile linear at 100*level) under 20 seeds; P-14 - P-16 judged')
d = d_j.values
los = []
for sd in range(20):
    bt = mbb(d, 63, 2000, 20261700+sd) - d.mean()
    los.append(np.percentile(mbb(d,63,2000,20261700+sd), 100*lev))
los = np.array(los)
print('lower limits: min %.4f max %.4f sd %.4f; at seed 20261700 %.4f' % (los.min(), los.max(), los.std(ddof=1), los[0]))
print('rank used: index', 100*lev/100*(2000-1))
# same at 20000 draws for comparison
los2 = [np.percentile(mbb(d,63,20000,20261800+sd), 100*lev) for sd in range(5)]
print('20000 draws lower limits', np.round(los2,4))
# a normal-theory lower limit with the MBB SE
print('normal lower limit diff - z*SE63', d.mean() - z*mbb(d,63).std(ddof=1))
# start-year structure: per year mean diff
y = pd.Series(d_all.values, index=d_all.index.year)
print('\nper start year P14-P16 mean diff:', y.groupby(level=0).mean().round(3).to_dict())
print('per start year n:', y.groupby(level=0).size().to_dict())
