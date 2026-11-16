import pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_columns',80); pd.set_option('display.max_rows',500); pd.set_option('display.max_colwidth',60)
F = r"C:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results\user_drivers.csv"
df = pd.read_csv(F, low_memory=False)
print(df.groupby(['section','arm'],dropna=False).size())
bd = df[df.section=='between_designs']
print(bd[['subject','measure','value','n','lo','hi','mechanical','note']].to_string())
dt = df[df.section=='design_table']
print(dt[['subject','family','base','label','measure','value','n']].head(30).to_string())
print(dt.subject.nunique(), dt.family.unique())
