import os
import pandas as pd
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 500); pd.set_option('display.max_colwidth', 60)
R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
df = pd.read_csv(os.path.join(R, 'user_drivers.csv'), low_memory=False)
print(df['section'].value_counts().to_string())

def nn(d):
    return d.loc[:, d.notna().any()]

bd = df[df.section == 'between_designs']
import sys
if len(sys.argv)>1:
    bd = bd.iloc[0:0]; df_wd_skip=True
print('\n== between_designs ==')
print(bd.groupby(['subject_kind', 'subject', 'arm'], dropna=False).size().to_string())
print(nn(bd[bd.subject == 'all_cells']).drop(columns=['section'], errors='ignore').to_string())

wd = df[df.section == 'within_design']
print('\n== within_design key combos ==')
print(wd.groupby(['subject', 'arm', 'month'], dropna=False).size().to_string())
x = wd[(wd.subject == 'p14') & (wd.month == 1)]
print(nn(x)[['subject', 'arm', 'month', 'measure', 'value', 'lo', 'hi', 'n']].to_string())

ac = df[df.section == 'accounting']
print('\n== accounting ==')
x = ac[(ac.subject == 'p14')]
print(nn(x).drop(columns=['section','reading'],errors='ignore').to_string())

dv = df[df.section == 'design_vs_luck']
print('\n== design_vs_luck ==')
print(nn(dv).drop(columns=['section']).to_string())
