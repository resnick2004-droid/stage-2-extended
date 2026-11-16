import os
import pandas as pd
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 500); pd.set_option('display.max_colwidth', 110)
R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
vm = pd.read_csv(os.path.join(R, 'u_value_map.csv'), low_memory=False)
for s in ['place_values', 'bar', 'solve', 'phase']:
    x = vm[vm.section == s]
    print(f'\n===== {s} =====')
    print(x[['base', 'phase', 'state', 'measure', 'value', 'n', 'unit', 'note']].to_string())
for p in ['a3_brk30_cb20_gate_paths.csv', 'rc_s150_all_gate_paths.csv']:
    print(p, list(pd.read_csv(os.path.join(R, p), nrows=2).columns))
