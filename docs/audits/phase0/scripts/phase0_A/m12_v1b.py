import os
import pandas as pd
pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 300); pd.set_option('display.max_colwidth', 200)
R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
rd = lambda t: pd.read_csv(os.path.join(R, f'v1_validation_{t}.csv'), low_memory=False)
a1 = rd('a1')
print('== a1 ==')
print(a1[a1.section == 'a1'][['subject', 'arm', 'scheme', 'mean_block', 'pf_growth_on_base_p50', 'registered_pf_growth_on_base_p50', 'growth_above_zero', 'paths']].to_string())
b2 = rd('b2')
print('\n== b2 ==')
x = b2[b2.section == 'b2']
print(x[['subject', 'arm', 'scheme', 'registered_bound_fresh_funded_r', 'break_even_e_fresh_funded_r', 'bracketed', 'break_even_shift', 'margin', 'margin_at_least', 'steps_run', 'first_step_at_or_below_zero', 'note']].to_string())
y = b2[b2.section == 'b2_curve']
print(y[['subject', 'arm', 'step', 'shift_r', 'pf_growth_on_base_p50', 'growth_above_zero']].to_string())
c1 = rd('c1')
print('\n== c1_summary ==')
s = c1[c1.section == 'c1_summary']
print(s[['subject', 'arm', 'kind', 'p', 'realisations', 'share_realisations_growth_above_zero', 'pf_growth_on_base_p50_min', 'pf_growth_on_base_p50_max']].to_string())
c2 = rd('c2')
print('\n== c2 ==')
print(c2[c2.section.isin(['c2', 'c2_reading', 'c2_not_done'])][['section', 'subject', 'arm', 'family', 'level', 'pf_growth_on_base_p50', 'growth_above_zero', 'lowest_level_growth_at_bound_at_or_below_zero', 'note', 'reading']].to_string())
