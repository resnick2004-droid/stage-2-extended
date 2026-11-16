"""EXPLORATORY (phase 0 audit B, Q3): (a) the 20-seed mean of the 2000-draw lower limit on P-14 - P-16 (judged);
(b) under the same Gaussian null as q3_calib.py, the false-positive rate of a Student-t line on non-overlapping
63-start batch means (df = batches - 1) at one-sided 0.05/110, and its power for shifts of 1-4 true SEs."""
import pandas as pd, numpy as np
from scipy.stats import norm, t as tdist
from scipy.linalg import toeplitz, cholesky
s = pd.read_csv('starts.csv'); s['start_date']=pd.to_datetime(s.start_date)
def ahead(cfg):
    d = s[(s.config==cfg)&(s.arm=='verdict')&(s.observed>=63)].sort_values('start_day')
    return pd.Series((((d.net_month_1>0).astype(float)+(d.net_month_2>0)+(d.net_month_3>0))/3).values, index=d.start_date.values)
d_all = (ahead('p14')-ahead('p16')).dropna(); d = d_all[d_all.index>=pd.Timestamp('2024-01-01')].values
n=len(d); b=63; k=-(-n//b); lastlen=n-(k-1)*b; lev=0.05/110
def mbb_means(x, draws, seed):
    c = np.concatenate([[0],np.cumsum(x)]); st=np.arange(n-b+1)
    f_=c[st+b]-c[st]; p_=c[st+lastlen]-c[st]
    fi = np.random.default_rng(seed).integers(0,n-b+1,size=(draws,k))
    return (f_[fi[:,:k-1]].sum(axis=1)+p_[fi[:,k-1]])/n
los = np.array([np.percentile(mbb_means(d,2000,20261700+i),100*lev) for i in range(20)])
print('2000-draw lower limits over 20 seeds: mean %.4f sd %.4f min %.4f max %.4f' % (los.mean(), los.std(ddof=1), los.min(), los.max()))
print('200000-draw lower limit:', np.percentile(mbb_means(d,200000,20261799),100*lev))
x = d_all.values - d_all.values.mean(); N=len(x); v=(x*x).sum()/N
r = np.array([(x[:N-j]*x[j:]).sum()/N/v for j in range(63)])*(1-np.arange(63)/63)
col=np.zeros(n); col[:63]=r; L=cholesky(toeplitz(col)+1e-9*np.eye(n),lower=True); tse=np.sqrt(toeplitz(col).sum())/n
m = n//b; tcrit = tdist.isf(lev, m-1)
print('batches', m, 't critical', round(tcrit,2), ' normal', round(norm.isf(lev),2))
rng=np.random.default_rng(20261117); sims=20000
rej=np.zeros(5); rej_p=np.zeros(5)
for i in range(sims):
    y = L@rng.standard_normal(n)
    for j,shift in enumerate((0,1,2,3,4)):
        yy = y + shift*tse
        bm = yy[:m*b].reshape(m,b).mean(axis=1)
        if bm.mean() - tcrit*bm.std(ddof=1)/np.sqrt(m) > 0: rej[j]+=1
print('t on 63-start batch means: rejection rate at shifts of 0,1,2,3,4 true SEs:', np.round(rej/sims,4))
rng=np.random.default_rng(20261118); sims2=3000
for j,shift in enumerate((0,1,2,3,4)):
    c=0
    for i in range(sims2):
        yy = L@rng.standard_normal(n) + shift*tse
        lo = np.percentile(mbb_means(yy,2000,int(rng.integers(1e9))),100*lev)
        if yy.mean()>0 and lo>0: c+=1
    rej_p[j]=c/sims2
print('D-621 percentile line (2000 draws): rejection rate at shifts of 0,1,2,3,4 true SEs:', np.round(rej_p,4))
print('true SE of the null mean (unit variance) %.4f; in P units for P-14 - P-16 (sd/start 0.438): %.4f' % (tse, tse*np.std(d)))
