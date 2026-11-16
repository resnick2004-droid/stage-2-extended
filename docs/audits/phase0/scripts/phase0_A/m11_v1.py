import os, json
import pandas as pd
pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 300); pd.set_option('display.max_colwidth', 80)
R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
for t in ['a0', 'a1', 'a2', 'b1', 'b2', 'b3', 'c1', 'c2']:
    f = f'v1_validation_{t}.csv'
    df = pd.read_csv(os.path.join(R, f), low_memory=False)
    m = json.load(open(os.path.join(R, f + '.manifest.json'), encoding='utf-8'))
    print(f'\n########## {f} {df.shape}')
    print('desc:', m.get('description', '')[:600])
    print('notes:', json.dumps(m.get('notes'))[:900])
    print('cols:', list(df.columns))
    for c in ['section', 'check', 'design', 'config', 'arm', 'block', 'verdict', 'holds', 'status', 'pass', 'passes', 'result']:
        if c in df.columns:
            vc = df[c].value_counts(dropna=False)
            if len(vc) <= 30:
                print(f'  {c}:', vc.to_dict())
