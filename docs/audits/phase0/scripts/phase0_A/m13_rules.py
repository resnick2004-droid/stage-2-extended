import yaml, json
P = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\config\rules.yaml"
d = yaml.safe_load(open(P, encoding='utf-8'))
rules = d['rules']
keys = ['combine_profit_target', 'combine_mll', 'combine_mll_lock_at', 'combine_consistency_max_day_frac', 'combine_position_size_limit',
        'xfa_mll_start', 'xfa_lock_at', 'xfa_cons_max_day_frac', 'xfa_std_winning_days', 'xfa_std_winning_day_min', 'xfa_cons_min_days',
        'funded_scaling_plan', 'funded_scaling_entry_tier_minis', 'payout_max_frac_of_balance', 'xfa_std_cap', 'xfa_cons_cap', 'profit_split', 'payout_min',
        'subscription_fee', 'reset_fee', 'activation_fee', 'max_active_funded_accounts', 'xfa_cap_shared_across_sizes', 'xfa_closure_at_request']
for k in keys:
    r = rules.get(k)
    if r is None:
        print(k, 'MISSING'); continue
    out = {kk: r.get(kk) for kk in ['value', 'status', 'source', 'article', 'article_id', 'url', 'verified', 'verified_on', 'unit'] if kk in r}
    if not out:
        out = {kk: (str(v)[:120]) for kk, v in r.items()}
    print(k, json.dumps(out, default=str)[:420])
