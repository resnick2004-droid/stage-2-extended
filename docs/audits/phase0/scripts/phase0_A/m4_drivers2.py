import os
import pandas as pd
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 500); pd.set_option('display.max_colwidth', 70)
R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
df = pd.read_csv(os.path.join(R, 'user_drivers.csv'), low_memory=False)

def nn(d):
    return d.loc[:, d.notna().any()]

ac = df[df.section == 'accounting']
print('== accounting: spread_share rows, p14 ==')
x = ac[(ac.subject == 'p14') & ac.measure.str.startswith('spread_share')]
print(x[['subject', 'arm', 'month', 'measure', 'value', 'n']].to_string())
print('accounting subjects:', ac.subject.unique().tolist())

dv = df[df.section == 'design_vs_luck']
print('\n== design_vs_luck ==')
cols = [c for c in ['subject', 'subject_kind', 'arm', 'month', 'measure', 'value', 'n', 'outcome', 'statistic', 'note'] if c in dv.columns]
d2 = nn(dv)
print('cols:', list(d2.columns))
print(dv[dv.measure.isin(['design_share', 'designs'])][cols].to_string())

for sec in ['frontier', 'menu', 'parameters', 'funded_facts']:
    s = nn(df[df.section == sec])
    print(f'\n== {sec} == cols:', list(s.columns))
    keep = [c for c in ['subject', 'subject_kind', 'arm', 'month', 'measure', 'value', 'n', 'pick', 'picked', 'limit', 'floor', 'eligible', 'tied', 'on_frontier', 'dominated_by', 'family', 'label', 'pool'] if c in s.columns]
    print(s[keep].to_string())
