"""EXPLORATORY (phase 0 audit B, Q1/Q5): what P rewards and ignores; the noise of the guarded measures against their
tolerances on the judged block; S3c's identity.  Source: results/user_journey.csv section start (starts.csv)."""
import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_columns',40)
s = pd.read_csv('starts.csv'); s['start_date']=pd.to_datetime(s.start_date)
v = s[s.arm=='verdict']
# 1. S3c identity: pooled payouts per fee dollar at month 3 = 1 + mean(net3)/mean(fees3)
for c in ['p14','p16']:
    g = v[(v.config==c)&(v.observed>=63)]
    s3c = (g.net_month_3+g.fees_month_3).sum()/g.fees_month_3.sum()
    print(c, 'S3c', round(s3c,6), '1+mean net3/mean fees3', round(1+g.net_month_3.mean()/g.fees_month_3.mean(),6), 'mean fees3', round(g.fees_month_3.mean(),1))
# 2. mass near zero at month ends (P-14, P-16), the purchase price
for c in ['p14','p16']:
    g = v[(v.config==c)&(v.observed>=63)]
    out = []
    for m in (1,2,3):
        x = g[f'net_month_{m}']
        out.append(dict(month=m, ahead=(x>0).mean(), within_0_100_below=((x>-100)&(x<=0)).mean(), within_0_250_below=((x>-250)&(x<=0)).mean(),
                        within_0_250_above=((x>0)&(x<=250)).mean(), within_0_500_above=((x>0)&(x<=500)).mean(),
                        not_paid=(~(g.first_payout<=21*m)).mean(), mean_net_not_ahead=x[x<=0].mean(), mean_net_ahead=x[x>0].mean()))
    print(c); print(pd.DataFrame(out).round(3).to_string(index=False))
print('evaluation fee step: spent_before_first_pass values (P-14) most common:', v[v.config=='p14'].spent_before_first_pass.value_counts().head(6).to_dict())
# 3. bankroll: distribution of cash spent before the first payout among starts ahead at month 1..3 (P-14)
g = v[(v.config=='p14')&(v.observed>=63)]
for m in (1,2,3):
    a = g[g[f'net_month_{m}']>0]
    print(f'P-14 ahead at month {m}: n={len(a)}; cash before first payout p50 {a.spent_before_first_payout.median():.0f} p90 {a.spent_before_first_payout.quantile(.9):.0f} max {a.spent_before_first_payout.max():.0f}; share needing > $2,500: {(a.spent_before_first_payout>2500).mean():.3f}')
print('P-14 all starts paid by 126: spent before first payout p90', g[g.first_payout<=126].spent_before_first_payout.quantile(.9))
# 4. what months 6 and 12 hold that no guard reads: mean nets
for c in ['p14','p15','p16','p16_4+0','p16_funded_cap']:
    gg = v[v.config==c]
    print(c, 'mean net m6 %.0f (n %d)  m12 %.0f (n %d); share ahead m6 %.3f m12 %.3f' % (gg[gg.observed>=126].net_month_6.mean(), (gg.observed>=126).sum(), gg[gg.observed>=252].net_month_12.mean(), (gg.observed>=252).sum(), (gg[gg.observed>=126].net_month_6>0).mean(), (gg[gg.observed>=252].net_month_12>0).mean()))
# 5. guards' noise on the judged block vs their tolerances: paired MBB (b=63) SE of the difference of each measure
def block_indices(n, b, draws, seed):
    rng = np.random.default_rng(seed); kk = -(-n//b)
    first = rng.integers(0, n-b+1, size=(draws,kk))
    return (first[:,:,None]+np.arange(b)[None,None,:]).reshape(draws,kk*b)[:,:n]
def meas(g, key):
    if key=='S1':
        x = g[g.first_payout<=126].spent_before_first_payout.values; return np.percentile(x,90) if len(x) else np.nan
    if key=='S3a': return (g.first_payout<=21).mean()
    if key=='S3b':
        x = np.where(g.first_payout.isna()|(g.first_payout>126), np.inf, g.first_payout); x=np.sort(x)
        q = np.percentile(np.where(np.isinf(x), 1e9, x), 90); return q if q<1e8 else np.nan
    if key=='S3c': return (g.net_month_3+g.fees_month_3).sum()/g.fees_month_3.sum()
    if key=='S4a': return (g.net_month_6>0).mean()
    if key=='S5a': return np.percentile(g.net_month_3,10)
    if key=='S5c':
        x = np.sort(g.net_month_6.values)[::-1]; k=int(np.ceil(len(x)/4)); tot=x.sum(); return x[:k].sum()/tot if tot>0 else np.nan
H = {'S1':126,'S3a':21,'S3b':126,'S3c':63,'S4a':126,'S5a':63,'S5c':126}
TOL = {'S1':('rel',0.10),'S3a':('abs',0.05),'S3b':('rel',0.10),'S3c':('rel',0.10),'S4a':('abs',0.05),'S5a':('rel',0.10),'S5c':('rel',0.10)}
J = pd.Timestamp('2024-01-01')
rows=[]
for other in ['p16','p14_point','p16_funded_cap']:
    for key,h in H.items():
        ref = v[(v.config=='p14')&(v.observed>=h)&(v.start_date>=J)].set_index('start_date').sort_index()
        if other=='p14_point':
            o = s[(s.arm=='point')&(s.config=='p14')&(s.observed>=h)&(s.start_date>=J)].set_index('start_date').sort_index()
        else:
            o = v[(v.config==other)&(v.observed>=h)&(v.start_date>=J)].set_index('start_date').sort_index()
        common = ref.index.intersection(o.index)
        R = ref.loc[common].reset_index(); O = o.loc[common].reset_index()
        r0 = meas(R,key); o0 = meas(O,key)
        idx = block_indices(len(common),63,400,20261115)
        bt = np.array([meas(O.iloc[i],key)-meas(R.iloc[i],key) for i in idx])
        kind,t = TOL[key]; allowed = t*abs(r0) if kind=='rel' else t
        rows.append(dict(pair=f'{other} vs p14', measure=key, n=len(common), p14=r0, other=o0, diff=o0-r0, se_diff=np.nanstd(bt,ddof=1), allowed=allowed, allowed_over_se=allowed/np.nanstd(bt,ddof=1)))
print(pd.DataFrame(rows).round(3).to_string(index=False))
