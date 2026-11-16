import pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_columns',80); pd.set_option('display.max_rows',500); pd.set_option('display.max_colwidth',50)
D = r"C:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results\u_budget.csv"
df = pd.read_csv(D, low_memory=False)
c = df[df.section=='cell']
print(c[['cell','base','role','block','measure','value','n','counted','overrides']].head(40).to_string())
print(c.block.unique(), c.cell.unique())
for s in ['choice','judged','guards','verdict']:
    print(df[df.section==s].dropna(axis=1,how='all').to_string())
