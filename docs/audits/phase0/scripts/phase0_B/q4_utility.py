"""EXPLORATORY (phase 0 audit B, Q4): would a utility over the distribution rank U1's configurations differently from P?
Source: results/user_journey.csv section start (starts.csv), every configuration, both arms; starts with >= 63
sessions (P's population, D-627 (1)).  Paired MBB intervals against P-14 on common start dates (block 63 and 126,
2000 draws, seed 20261115)."""
import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_columns',40); pd.set_option('display.max_rows',200)
s = pd.read_csv('starts.csv'); s['start_date']=pd.to_datetime(s.start_date)
s = s[s.observed>=63].copy()
for m in (1,2,3):
    s[f'a{m}'] = (s[f'net_month_{m}']>0).astype(float)
s['A'] = (s.a1+s.a2+s.a3)/3
# deepest known dip by month m: the cash before the first payout if paid by then, and the month-end nets
for m in (1,2,3):
    paid = s.first_payout <= 21*m
    dip = np.where(paid, s.spent_before_first_payout.fillna(0), 0.0)
    mins = -np.minimum.reduce([s[f'net_month_{j}'] for j in range(1,m+1)])
    s[f'dip{m}'] = np.maximum(dip, mins)
for B in (2000, 2500):
    s[f'AB{B}'] = sum(((s[f'net_month_{m}']>0) & (s[f'dip{m}']<=B)).astype(float) for m in (1,2,3))/3
    s[f'A3B{B}'] = ((s.net_month_3>0)&(s.dip3<=B)).astype(float)
x = s.net_month_3
s['LA2'] = x + np.minimum(x,0)                 # losses weighted twice
s['N3'] = x
W = 10000.0
s['LOG10k'] = np.log1p(x/W)                     # log utility of a $10,000 bankroll (all month-3 nets > -$10,000)
print('min month-3 net over all configs/arms:', x.min())
def cvar(v, q=0.10):
    v = np.sort(np.asarray(v,float)); k = max(1,int(np.ceil(q*len(v)))); return v[:k].mean()
def summarise(g):
    return pd.Series({'n':len(g),'P':g.A.mean(),'ahead_m1':g.a1.mean(),'ahead_m3':g.a3.mean(),
        'P_B2000':g.AB2000.mean(),'P_B2500':g.AB2500.mean(),'m3_B2000':g['A3B2000'].mean(),'m3_B2500':g['A3B2500'].mean(),
        'mean_net3':g.N3.mean(),'LA2_net3':g.LA2.mean(),'CVaR10_net3':cvar(g.N3),'p10_net3':np.percentile(g.N3,10),
        'CE_log10k':W*np.expm1(g.LOG10k.mean()),'S3c':(g.net_month_3+g.fees_month_3).sum()/g.fees_month_3.sum(),
        'mean_fees3':g.fees_month_3.mean()})
blocks = {'all': s, 'judged': s[s.start_date>=pd.Timestamp('2024-01-01')]}
res = {}
for bn, d in blocks.items():
    for arm in ('verdict','point'):
        t = d[d.arm==arm].groupby('config').apply(summarise)
        res[(bn,arm)] = t
        print(f'\n===== block {bn}, arm {arm}')
        print(t.round(3).to_string())
        meas = ['P','P_B2000','P_B2500','mean_net3','LA2_net3','CVaR10_net3','CE_log10k','S3c']
        rk = t[meas].rank(ascending=False).astype(int)
        print('ranks (1 = best):'); print(rk.to_string())
        elig = t.loc[['p14','p15','p16'], meas].rank(ascending=False).astype(int)
        print('ranks among the three rows to beat:'); print(elig.to_string())
# paired differences against P-14 with MBB SEs, verdict arm
def block_indices(n, b, draws, seed):
    rng = np.random.default_rng(seed); kk = -(-n//b)
    first = rng.integers(0, n-b+1, size=(draws,kk))
    return (first[:,:,None]+np.arange(b)[None,None,:]).reshape(draws,kk*b)[:,:n]
cols = {'P':'A','P_B2000':'AB2000','P_B2500':'AB2500','mean_net3':'N3','LA2_net3':'LA2'}
for bn, d in blocks.items():
    v = d[d.arm=='verdict']
    ref = v[v.config=='p14'].set_index('start_date')
    print(f'\n===== paired against P-14, verdict, block {bn}: difference (config - P-14), SE by MBB b=63 / b=126; |z|<2 marked ~')
    rows=[]
    for c in sorted(v.config.unique()):
        if c=='p14': continue
        o = v[v.config==c].set_index('start_date')
        common = ref.index.intersection(o.index).sort_values()
        r = {'config':c,'n':len(common)}
        for name,col in cols.items():
            dd = (o.loc[common,col]-ref.loc[common,col]).values
            se63 = dd[block_indices(len(dd),63,2000,20261115)].mean(axis=1).std(ddof=1)
            se126 = dd[block_indices(len(dd),126,2000,20261115)].mean(axis=1).std(ddof=1)
            se = max(se63,se126)
            r[name] = f"{dd.mean():+.3f}" if 'net' not in name else f"{dd.mean():+.0f}"
            r[name] += f" ({se63:.3f}/{se126:.3f})" if 'net' not in name else f" ({se63:.0f}/{se126:.0f})"
            r[name] += ' ~' if abs(dd.mean()) < 2*se else ''
        # CVaR10 difference via MBB on the paired dates (statistic not a mean)
        a = o.loc[common,'N3'].values; bref = ref.loc[common,'N3'].values
        idx = block_indices(len(a),126,1000,20261115)
        bt = np.array([cvar(a[i])-cvar(bref[i]) for i in idx])
        dcv = cvar(a)-cvar(bref)
        r['CVaR10'] = f"{dcv:+.0f} ({bt.std(ddof=1):.0f})" + (' ~' if abs(dcv) < 2*bt.std(ddof=1) else '')
        rows.append(r)
    print(pd.DataFrame(rows).to_string(index=False))
