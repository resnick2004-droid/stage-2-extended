"""EXPLORATORY (phase 0 audit B): extract section `start` of results/user_journey.csv (every configuration and arm)
with the columns the audit reads, to a local parquet-free CSV in the scratchpad."""
import pandas as pd
F = r"C:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results\user_journey.csv"
cols = ['section','config','arm','start_day','start_date','observed','payouts','first_pass','first_payout','first_payout_cash',
        'spent_before_first_pass','spent_before_first_payout','exact_runs_differing'] + \
       [f'net_month_{m}' for m in range(1,13)] + [f'fees_month_{m}' for m in (1,2,3,6,12)]
df = pd.read_csv(F, usecols=cols, low_memory=False)
s = df[df.section=='start'].drop(columns='section')
print(s.shape, s.exact_runs_differing.value_counts(dropna=False).head())
s.to_csv('starts.csv', index=False)
