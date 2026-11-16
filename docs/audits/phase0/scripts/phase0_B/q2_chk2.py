import pandas as pd, os
D = r"C:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
for f in ['u_firms.csv','u_hours.csv','u_consistency.csv','u_resolve.csv','u_limit.csv']:
    df = pd.read_csv(os.path.join(D,f), low_memory=False)
    c = df[(df.section=='cell')]
    print(f, c.groupby(['role','counted']+(['label'] if 'label' in c.columns else []),dropna=False).cell.unique().to_dict())
