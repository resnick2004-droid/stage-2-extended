import pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_columns',80); pd.set_option('display.max_rows',500); pd.set_option('display.max_colwidth',120)
D = r"C:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results\u_budget.csv"
df = pd.read_csv(D, low_memory=False)
c = df[(df.section=='cell')&(df.cell=='budget15')&(df.measure.isin(['P','S3c']))]
print(c[['cell','base','role','block','measure','value','n','counted','overrides']].to_string())
print(df[df.section=='cell'].groupby(['cell','role','counted']).size())
