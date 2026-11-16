import os
import pandas as pd
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 500); pd.set_option('display.max_colwidth', 120)
R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
for f in ['a3_brk30_cb20_gate.csv', 'rc_s150_all_gate.csv']:
    df = pd.read_csv(os.path.join(R, f), low_memory=False)
    print('\n#####', f, df.shape, 'sections:', df.section.unique().tolist())
    x = df[df.section == 'policy_fresh']
    x = x.loc[:, x.notna().any()]
    print(x.to_string()[:3000])
    rc = [c for c in df.columns if 'realis' in c.lower() or 'risk' in c.lower() or 'contracts' in c.lower()]
    print('risk-like columns:', rc)

vm = pd.read_csv(os.path.join(R, 'u_value_map.csv'), low_memory=False)
print('\n##### u_value_map sections:', vm.section.value_counts().to_string())
m = vm[vm.measure.str.contains('realis|risk|contracts', case=False, na=False)]
print(m.groupby(['section', 'base', 'phase', 'measure']).size().to_string()[:3000])
