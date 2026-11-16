import pandas as pd
pd.set_option('display.width',200)
F = r"C:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results\user_drivers.csv"
df = pd.read_csv(F, low_memory=False, usecols=['section','subject','measure','value','n','arm','month','note'])
d = df[(df.section=='design_vs_luck')&(df.arm=='verdict')&(df.measure=='design_share')]
print(d[['subject','month','value','n']].to_string(index=False))
