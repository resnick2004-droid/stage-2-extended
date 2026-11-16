"""EXPLORATORY (phase 0 audit B, Q3 continued): MBB edge weights on the judged block; the year rule's pass chance for a
true improvement; per-month dependence. Source: user_journey.csv section start, verdict (starts.csv)."""
import pandas as pd, numpy as np
from scipy.stats import norm
s = pd.read_csv('starts.csv'); s['start_date']=pd.to_datetime(s.start_date)
def ahead(cfg, arm='verdict', months=(1,2,3)):
    d = s[(s.config==cfg)&(s.arm==arm)&(s.observed>=63)].sort_values('start_day')
    a = sum((d[f'net_month_{m}']>0).astype(float) for m in months)/len(months)
    return pd.Series(a.values, index=d.start_date.values)
d_all = (ahead('p14')-ahead('p16')).dropna()
J = d_all.index>=pd.Timestamp('2024-01-01')
d = d_all[J].values; n=len(d); b=63; k=-(-n//b); lastlen=n-(k-1)*b
# exact inclusion weights of the MBB as implemented
w = np.zeros(n)
for st in range(n-b+1):
    w[st:st+b] += (k-1)/(n-b+1)
    w[st:st+lastlen] += 1/(n-b+1)
w /= w.sum()
print('edge weights: first start %.3f x, middle %.3f x, last start %.3f x of uniform' % (w[0]*n, w[n//2]*n, w[-1]*n))
print('bootstrap centre (weighted mean) %.4f vs the sample mean %.4f' % ((w*d).sum(), d.mean()))
# per quarter of the judged block
q = pd.Series(d, index=d_all.index[J]).groupby(pd.Series(d_all.index[J]).dt.to_period('Q').values).mean()
print('P14-P16 per start quarter (judged):', q.round(3).to_dict())
# share of P from each month, and per month
for cfg in ['p14','p15','p16']:
    print(cfg, 'share ahead m1/m2/m3 all:', [round(ahead(cfg,months=(m,)).mean(),3) for m in (1,2,3)],
          'judged:', [round(ahead(cfg,months=(m,))[ahead(cfg,months=(m,)).index>=pd.Timestamp('2024-01-01')].mean(),3) for m in (1,2,3)])
# year rule: per-year SE of the paired difference by MBB within the year (b=63), for two pairs
def block_indices(n, b, draws, seed):
    rng = np.random.default_rng(seed); kk = -(-n//b)
    first = rng.integers(0, n-b+1, size=(draws,kk))
    return (first[:,:,None]+np.arange(b)[None,None,:]).reshape(draws,kk*b)[:,:n]
for a,bb in [('p14','p16'),('p14','p13'),('p16','p16_funded_cap')]:
    dd = (ahead(a)-ahead(bb)).dropna()
    ses = []
    for y,g in dd.groupby(dd.index.year):
        x = g.values
        if len(x) < 63: continue
        bt = x[block_indices(len(x),63,2000,20261115)].mean(axis=1)
        ses.append((y, len(x), bt.std(ddof=1)))
    se_y = np.array([e[2] for e in ses]); ny = len(se_y)
    out = []
    for delta in (0.0, 0.02, 0.05, 0.10):
        p_worse = norm.cdf(-delta/se_y)
        # P(at most one year worse) with independent years (Poisson-binomial)
        probs = np.array([1.0])
        for p in p_worse:
            probs = np.convolve(probs, [1-p, p])
        out.append((delta, round(probs[:2].sum(),3)))
    print(f'{a}-{bb}: per-year SE (MBB b=63):', [(e[0], e[1], round(e[2],3)) for e in ses], ' P(pass year rule | true diff):', out)
