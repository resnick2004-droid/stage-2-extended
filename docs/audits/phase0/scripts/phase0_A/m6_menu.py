import os
import pandas as pd
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 500)
R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
ud = pd.read_csv(os.path.join(R, 'user_drivers.csv'), low_memory=False, usecols=['section', 'subject', 'subject_kind', 'measure', 'value', 'arm', 'block', 'label'])
dt = ud[(ud.section == 'design_table') & (ud.arm == 'verdict')]
print('design_table blocks:', dt.block.unique().tolist(), 'kinds:', dt.subject_kind.unique().tolist())
dt = dt[dt.block == 'all']
piv = dt.pivot_table(index='subject', columns='measure', values='value', aggfunc='first')
lab = dt.groupby('subject')['label'].first()
piv['label'] = lab
print('n designs in design_table (verdict, all):', len(piv))
for name, lim in [('lowest_cost', 2000), ('balanced', 2500), ('best_result', None)]:
    e = piv[(piv.S4b >= 0.95)]
    if lim is not None:
        e = e[e.S1 <= lim]
    e = e.sort_values(['P', 'S1'], ascending=[False, True])
    print(f'\n{name}: eligible={len(e)}')
    print(e[['P', 'S1', 'S3a', 'S4b', 'S5a', 'label']].head(6).to_string())
print('\nwallet1000 rows:')
print(piv.loc[[i for i in piv.index if i.startswith('wallet1000') or i.startswith('seats1')], ['P', 'S1', 'S3a', 'S4b', 'S5a']].to_string())
print('\ntop P overall:')
print(piv.sort_values('P', ascending=False)[['P', 'S1', 'S3a', 'S3c', 'S4b', 'S5a', 'label']].head(8).to_string())
