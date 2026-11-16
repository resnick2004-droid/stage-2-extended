import pandas as pd, os
F = r"C:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results\user_journey.csv"
df = pd.read_csv(F, usecols=['section','config','arm'], low_memory=False)
print(df.groupby(['section']).size())
print(df[df.section=='start'].groupby(['config','arm']).size())
