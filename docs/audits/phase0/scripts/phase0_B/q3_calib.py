"""EXPLORATORY (phase 0 audit B, Q3): (a) the shape of the 63-block MBB distribution of the judged-block paired mean
(P-14 - P-16, verdict) in its far tail; (b) the false-positive rate of D-621 (3)(i)'s line at one-sided 0.05/110
under a Gaussian null whose autocorrelation is the observed one (full-sample ACF to lag 62, tapered) -- the
bootstrap's best case.  Seeds fixed here: 20261115 (+i)."""
import pandas as pd, numpy as np
from scipy.stats import norm, skew, kurtosis
from scipy.linalg import toeplitz, cholesky
s = pd.read_csv('starts.csv'); s['start_date']=pd.to_datetime(s.start_date)
def ahead(cfg, arm='verdict'):
    d = s[(s.config==cfg)&(s.arm==arm)&(s.observed>=63)].sort_values('start_day')
    a = ((d.net_month_1>0).astype(float)+(d.net_month_2>0)+(d.net_month_3>0))/3.0
    return pd.Series(a.values, index=d.start_date.values)
d_all = (ahead('p14')-ahead('p16')).dropna()
d = d_all[d_all.index>=pd.Timestamp('2024-01-01')].values
n=len(d); b=63; k=-(-n//b); lev=0.05/110
# block sums via cumsum; last block truncated to n-(k-1)*b
cs = np.concatenate([[0],np.cumsum(d)])
starts = np.arange(n-b+1)
full = cs[starts+b]-cs[starts]
lastlen = n-(k-1)*b
part = cs[starts+lastlen]-cs[starts]
rng = np.random.default_rng(20261115)
D = 400000
first = rng.integers(0,n-b+1,size=(D,k))
bm = (full[first[:,:k-1]].sum(axis=1)+part[first[:,k-1]])/n
z = (bm-bm.mean())/bm.std()
print('n',n,'blocks',k,'last block',lastlen)
print('bootstrap mean %.4f (sample %.4f) sd %.4f skew %.3f excess kurtosis %.3f'%(bm.mean(), d.mean(), bm.std(), skew(bm), kurtosis(bm)))
for q in (lev, 0.001, 0.005, 0.0125, 0.025, 0.05):
    print(f'  quantile {q:.6f}: standardized {np.quantile(z,q):+.3f}  normal {norm.ppf(q):+.3f}')
# (b) Gaussian null with the observed ACF (full sample, lags 0..62, Bartlett taper)
x = d_all.values - d_all.values.mean(); N=len(x); v=(x*x).sum()/N
r = np.array([(x[:N-j]*x[j:]).sum()/N/v for j in range(63)])
r = r*(1-np.arange(63)/63)
col = np.zeros(n); col[:63]=r
T = toeplitz(col)
w,_ = np.linalg.eigh(T); print('min eigenvalue of the null covariance', w.min())
L = cholesky(T+1e-9*np.eye(n), lower=True)
true_sd = np.sqrt(T.sum())/n
print('null true SE of the mean (unit variance per start):', true_sd, ' n_eff', 1/true_sd**2)
sims=4000; draws=2000
rej=0; rej_norm=0; los=[]
sim_rng = np.random.default_rng(20261116)
for i in range(sims):
    y = L @ sim_rng.standard_normal(n)
    c = np.concatenate([[0],np.cumsum(y)])
    f_ = c[starts+b]-c[starts]; p_ = c[starts+lastlen]-c[starts]
    fi = sim_rng.integers(0,n-b+1,size=(draws,k))
    bb = (f_[fi[:,:k-1]].sum(axis=1)+p_[fi[:,k-1]])/n
    lo = np.percentile(bb, 100*lev)
    m = y.mean()
    if m>0 and lo>0: rej+=1
    if m - norm.isf(lev)*bb.std(ddof=1) > 0: rej_norm+=1
    los.append((lo-m)/true_sd)
los=np.array(los)
print(f'false-positive rate of the percentile line: {rej}/{sims} = {rej/sims:.4f}  (nominal {lev:.5f}, ratio {rej/sims/lev:.1f}x)')
print(f'false-positive rate of a normal line with the MBB SE: {rej_norm}/{sims} = {rej_norm/sims:.4f}')
print('lower limit minus the mean, in true SEs: median %.2f, 10th pct %.2f, 90th pct %.2f (a calibrated limit sits at %.2f)'%(np.median(los), np.percentile(los,10), np.percentile(los,90), -norm.isf(lev)))
