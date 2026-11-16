"""Tabulate the Combine pass-probability supremum over all fair strategies, with and without the $1,000 DLL."""
import pandas as pd
from combine_supremum import solve
rows = []
for dll in [None, 1000.0]:
    for h in [500, 250, 100, 50]:
        v, it, *_ = solve(h, dll=dll)
        rows.append(dict(grid_step=h, dll=dll or 0, sup_p_pass=v, days_to_converge=it,
                         two_day_family_best_on_grid=max(4e6 / ((2000 + X) * (5000 - X)) for X in range(1350, 1651) if X % h == 0 or h > 150 and X == 1500)))
pd.DataFrame(rows).to_csv("results_combine_supremum.csv", index=False); print(pd.DataFrame(rows).to_string(index=False))
