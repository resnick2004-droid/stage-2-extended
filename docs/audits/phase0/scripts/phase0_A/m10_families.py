import os, json
import pandas as pd
pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 500); pd.set_option('display.max_colwidth', 70)
R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"
fams = ['u_budget', 'u_entry', 'u_seats', 'u_hours', 'u_firms', 'u_consistency', 'u_plan', 'u_limit', 'u_resolve']
total_cells = 0
for f in fams:
    df = pd.read_csv(os.path.join(R, f + '.csv'), low_memory=False)
    m = json.load(open(os.path.join(R, f + '.csv.manifest.json'), encoding='utf-8'))
    p = m['parameters']
    print(f"\n########## {f}  k={p.get('k')} level={p.get('level')} family_id={p.get('family_id')} variant_count={m.get('variant_count')} program_cells={p.get('program_cells')} chosen_base={p.get('chosen_base')}")
    print('  program_by_family:', p.get('program_by_family'))
    j = df[df.section == 'judged']
    cols = [c for c in ['cell', 'base', 'role', 'block', 'measure', 'value', 'reference', 'reference_value', 'difference', 'lower', 'level', 'n', 'n_reference', 'status', 'allowed', 'worse_by'] if c in j.columns]
    print(j[cols].to_string())
    v = df[df.section == 'verdict']
    vcols = [c for c in ['cell', 'chosen', 'line', 'status', 'verdict', 'first_failing', 'family', 'decision', 'cells', 'program_cells', 'program_families', 'k', 'level', 'counted'] if c in v.columns]
    print(v[vcols].to_string())
    ch = df[df.section == 'choice']
    ccols = [c for c in ['cell', 'base', 'block', 'measure', 'value', 'chosen', 'n'] if c in ch.columns]
    print('choice (P rows):')
    print(ch[ch.measure == 'P'][ccols].to_string() if 'measure' in ch.columns else ch.head().to_string())
