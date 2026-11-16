"""EXPLORATORY (phase 0 audit B, Q4): how often each of the three rows to beat ranks first under each measure when the
common start dates are resampled jointly (MBB, blocks of 126 starts, 1000 draws, seed 20261119); verdict arm, starts
with >= 63 sessions; all starts and the judged block.  Also P's difference by month (P-14 - P-16)."""
import pandas as pd, numpy as np
s = pd.read_csv('starts.csv'); s['start_date']=pd.to_datetime(s.start_date)
v = s[(s.arm=='verdict')&(s.observed>=63)&(s.config.isin(['p14','p15','p16']))].copy()
v['A']=((v.net_month_1>0).astype(float)+(v.net_month_2>0)+(v.net_month_3>0))/3
for m in (1,2,3):
    paid = v.first_payout<=21*m
    dip = np.where(paid, v.spent_before_first_payout.fillna(0), 0.0)
    mins = -np.minimum.reduce([v[f'net_month_{j}'] for j in range(1,m+1)])
    v[f'dip{m}']=np.maximum(dip,mins)
v['AB2500']=sum(((v[f'net_month_{m}']>0)&(v[f'dip{m}']<=2500)).astype(float) for m in (1,2,3))/3
v['N3']=v.net_month_3; v['LA2']=v.N3+np.minimum(v.N3,0)
for blk in ('all','judged'):
    w = v if blk=='all' else v[v.start_date>=pd.Timestamp('2024-01-01')]
    piv = {c: w[w.config==c].set_index('start_date').sort_index() for c in ['p14','p15','p16']}
    dates = piv['p14'].index.intersection(piv['p15'].index).intersection(piv['p16'].index)
    n=len(dates); b=126; k=-(-n//b)
    rng=np.random.default_rng(20261119)
    first=rng.integers(0,n-b+1,size=(1000,k)); idx=(first[:,:,None]+np.arange(b)).reshape(1000,k*b)[:,:n]
    out={}
    for col in ['A','AB2500','N3','LA2','CVaR10']:
        if col=='CVaR10':
            arr = np.stack([np.sort(piv[c].loc[dates,'N3'].values) for c in ['p14','p15','p16']])
            raw = np.stack([piv[c].loc[dates,'N3'].values for c in ['p14','p15','p16']])
            q = int(np.ceil(0.1*n))
            stats = np.stack([np.sort(raw[:,i],axis=1)[:,:q].mean(axis=1) for i in idx])
        else:
            raw = np.stack([piv[c].loc[dates,col].values for c in ['p14','p15','p16']])
            stats = np.stack([raw[:,i].mean(axis=1) for i in idx])
        first_ = np.bincount(stats.argmax(axis=1), minlength=3)/len(idx)
        out[col] = dict(zip(['p14','p15','p16'], np.round(first_,3)))
    print(blk, n, out)
    for m in (1,2,3):
        a=(piv['p14'].loc[dates,f'net_month_{m}']>0).mean(); c=(piv['p16'].loc[dates,f'net_month_{m}']>0).mean()
        print(f'   month {m}: P-14 {a:.3f} P-16 {c:.3f} diff {a-c:+.3f}')
