import os, sys
import pandas as pd
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 1000); pd.set_option('display.max_colwidth', 90)
R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
df = pd.read_csv(os.path.join(R, 'u_xfa_day_budget.csv'), low_memory=False)
print('designs:', df.design.unique().tolist(), 'prereg:', df.prereg.unique().tolist(), 'arms:', df.arm.unique().tolist(), 'basis:', df.basis.unique().tolist())
secs = sys.argv[1:]
for s in secs:
    x = df[(df.section == s) & (df.arm.isin(['verdict', 'bound'])) & df.design.isin(['p14', 'p15', 'p16', 'P-14', 'P-15', 'P-16'])]
    if x.empty:
        x = df[(df.section == s)]
    print(f'\n===== {s} ({len(x)} rows) =====')
    print(x[['design', 'arm', 'group', 'measure', 'value', 'n', 'basis', 'note']].to_string())
