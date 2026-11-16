# Pre-registration — T4 check 2 on propsim (written before running)

Policy: Combine, day 1 risk $2,000 at R = 0.825 (win +$1,650); if won, day 2 risk $2,000 at R = 0.675 (win +$1,350); no other trades.
Prediction: P(pass) = (2000/3650)(2000/3350) = 0.327131. Every pass on day 2 at exactly B = 3,000; every fail at the floor
(day 1 at -2,000; day 2 at -350). Mean terminal balance = 0 (fair game).
Run: N = 1,000,000, seed 20260921, truncate floor mode, e = 0. Pass criterion: |measured - predicted| <= 3 SE.
