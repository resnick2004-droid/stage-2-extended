import pandas as pd, glob, os
pd.set_option('display.width',250); pd.set_option('display.max_columns',80); pd.set_option('display.max_rows',500)
D = r"C:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
for f in sorted(glob.glob(os.path.join(D,'u_*.csv'))):
    df = pd.read_csv(f, low_memory=False)
    print(os.path.basename(f), df.shape)
    print('  cols:', list(df.columns)[:40])
    if 'section' in df.columns:
        print('  ', df.groupby('section').size().to_dict())
