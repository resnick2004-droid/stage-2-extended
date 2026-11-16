import os
import pandas as pd
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 500); pd.set_option('display.max_colwidth', 50)
R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
df = pd.read_csv(os.path.join(R, 'u_budget.csv'), low_memory=False)
c = df[df.section == 'cell']
print('cells:', c.cell.unique().tolist())
print('configs:', c.config.unique().tolist(), 'arms:', c.arm.unique().tolist(), 'blocks:', c.block.unique().tolist())
print(c.groupby(['cell', 'config', 'arm', 'block'], dropna=False).size().to_string())
x = c[c.block == 'all']
piv = x.pivot_table(index=['cell', 'config', 'arm'], columns='measure', values='value', aggfunc='first', dropna=False)
print(piv.to_string())

# rows to beat in the user_drivers design_table for comparison
ud = pd.read_csv(os.path.join(R, 'user_drivers.csv'), low_memory=False, usecols=['section', 'subject', 'subject_kind', 'measure', 'value', 'arm', 'block', 'n', 'dominated_by', 'on_frontier'])
dt = ud[(ud.section == 'design_table') & ud.subject.isin(['p14', 'p15', 'p16', 'nobudget_p14', 'seats1_p14', 'budget10_p14'])]
print(dt.pivot_table(index=['subject', 'arm', 'block'], columns='measure', values='value', aggfunc='first').to_string())
fr = ud[(ud.section == 'frontier') & ud.subject.isin(['seats1_p14', 'p15', 'p16'])]
for _, r in fr.iterrows():
    print(r.subject, 'dominated_by:', r.dominated_by)
