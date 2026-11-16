import pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_columns',80)
F = r"C:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results\user_journey.csv"
cols = ['section','config','arm','start_day','start_date','observed','pass_days','funded_days','pay_days','payouts','first_pass','first_funded','first_payout','first_payout_cash','spent_before_first_pass','spent_before_first_payout','net_month_1','net_month_2','net_month_3','net_month_6','net_month_12','fees_month_1','fees_month_3','net_30']
df = pd.read_csv(F, usecols=cols, low_memory=False)
s = df[(df.section=='start')&(df.config=='p14')&(df.arm=='verdict')]
print(s.head(5).T)
print(s.tail(3).T)
print(s.describe().T)
