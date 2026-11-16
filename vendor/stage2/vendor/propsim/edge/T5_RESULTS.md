# T5 — Value of a demonstrated edge within the conduct constraints

Pre-registration: `PREREG_T5.md`. Scripts: `combine_exact.py`, `value_of_edge.py` (pre-registered); `xfa_small_risk_exploratory.py`, `payout_buffer_exploratory.py` and the buffer extension (exploratory, D-44/D-45). Edge e = expected P&L per trade as a fraction of $ risked, **after costs**. e = 0 rows are reference only (D-34).

## Validation (pre-registered V1–V3)

```
combine stage done 26s
xfa stage done 122s
V1 exact vs MC: 120 comparisons, 2 beyond 3 SE, max |z| 3.26 -> PASS
V2 chain 1:1 $1,500 at e=0 minus 16/49 = -1.74e-14 (PASS); grid reproduction: 10 cells, max |z| 2.32 -> PASS
V3 e=0 gross <= 2000: PASS; e=0 E[B+Q] <= 0: PASS (max z +1.45); monotone in edge: PASS
composed 1200 pairs; total 122s
V1 follow-up (D-40; seeds fixed before running), 4 largest deviations at N = 1,000,000:
1.5:1 $1000 e=0.05: exact 0.324050  MC(1M, seed 55500) 0.323498  z -1.18
1.5:1 $750 e=0.1: exact 0.355532  MC(1M, seed 55501) 0.356247  z +1.49
3.0:1 $1000 e=0.0: exact 0.170173  MC(1M, seed 55502) 0.170976  z +2.13
2.0:1 $500 e=0.0: exact 0.277285  MC(1M, seed 55503) 0.276919  z -0.82
```

## 1. Combine pass probability — exact chain (validated against Monte Carlo)

| prof        |   0.0 |   0.02 |   0.05 |   0.1 |   0.15 |   0.2 |
|:------------|------:|-------:|-------:|------:|-------:|------:|
| 1.5:1 $1000 | 0.292 |  0.305 |  0.324 | 0.357 |  0.391 | 0.426 |
| 1.5:1 $500  | 0.266 |  0.289 |  0.325 | 0.387 |  0.452 | 0.517 |
| 1.5:1 $750  | 0.271 |  0.287 |  0.312 | 0.356 |  0.4   | 0.445 |
| 1:1 $1500   | 0.327 |  0.34  |  0.36  | 0.394 |  0.43  | 0.466 |
| 2:1 $1000   | 0.231 |  0.241 |  0.257 | 0.283 |  0.309 | 0.337 |
| 2:1 $500    | 0.277 |  0.295 |  0.322 | 0.369 |  0.417 | 0.465 |
| 2:1 $750    | 0.297 |  0.309 |  0.329 | 0.362 |  0.395 | 0.429 |
| 3:1 $1000   | 0.17  |  0.178 |  0.189 | 0.209 |  0.23  | 0.251 |
| 3:1 $500    | 0.283 |  0.296 |  0.315 | 0.347 |  0.38  | 0.413 |
| 3:1 $750    | 0.207 |  0.216 |  0.23  | 0.254 |  0.279 | 0.304 |

Admissible profiles (D-36) are all rows except 1:1 $1500 (reference, not admissible).

## 2a. Best pre-registered admissible pair by EV per attempt — standard path, take-the-maximum payouts (A5), 1-year funded horizon

|   edge | combine_profile   | xfa_profile   |   p_pass |   xfa_cash_1y |   ev_per_attempt |   ev_structural |   ev_from_edge |   edge_share_of_ev |   failed_combines_per_year |
|-------:|:------------------|:--------------|---------:|--------------:|-----------------:|----------------:|---------------:|-------------------:|---------------------------:|
|   0    | 2:1 $750          | 1.5:1 $1000   |    0.297 |       835.904 |          154.689 |         154.689 |          0     |              0     |                     23.843 |
|   0.02 | 2:1 $750          | 1.5:1 $1000   |    0.309 |       974.599 |          206.33  |         154.689 |         51.641 |              0.25  |                     22.067 |
|   0.05 | 2:1 $750          | 1.5:1 $1000   |    0.329 |      1265.44  |          317.903 |         154.689 |        163.214 |              0.513 |                     19.078 |
|   0.1  | 1.5:1 $500        | 1.5:1 $1000   |    0.387 |      1984.13  |          657.941 |         129.959 |        527.981 |              0.802 |                      8.249 |
|   0.15 | 1.5:1 $500        | 1.5:1 $1000   |    0.452 |      3175.83  |         1315.26  |         129.959 |       1185.3   |              0.901 |                      5.829 |
|   0.2  | 1.5:1 $500        | 1.5:1 $1000   |    0.517 |      5080.44  |         2496.01  |         129.959 |       2366.05  |              0.948 |                      3.876 |

## 2b. Best pre-registered admissible pair by EV per attempt — consistency path, take-the-maximum payouts (A5), 1-year funded horizon

|   edge | combine_profile   | xfa_profile   |   p_pass |   xfa_cash_1y |   ev_per_attempt |   ev_structural |   ev_from_edge |   edge_share_of_ev |   failed_combines_per_year |
|-------:|:------------------|:--------------|---------:|--------------:|-----------------:|----------------:|---------------:|-------------------:|---------------------------:|
|   0    | 2:1 $750          | 2:1 $750      |    0.297 |       842.062 |          156.515 |         156.515 |          0     |              0     |                     24.298 |
|   0.02 | 2:1 $750          | 2:1 $750      |    0.309 |       963.903 |          203.022 |         156.515 |         46.507 |              0.229 |                     22.704 |
|   0.05 | 2:1 $750          | 1.5:1 $1000   |    0.329 |      1176.22  |          288.584 |         145.432 |        143.152 |              0.496 |                     21.368 |
|   0.1  | 1.5:1 $500        | 1.5:1 $1000   |    0.387 |      1752.69  |          568.259 |         121.652 |        446.607 |              0.786 |                      9.108 |
|   0.15 | 1.5:1 $500        | 1.5:1 $1000   |    0.452 |      2733.6   |         1115.33  |         121.652 |        993.675 |              0.891 |                      6.71  |
|   0.2  | 1.5:1 $500        | 1.5:1 $1000   |    0.517 |      4177.28  |         2029.18  |         121.652 |       1907.53  |              0.94  |                      4.724 |

`ev_structural` is the value present at zero edge — the contract asymmetry the firm prohibits exploiting (D-34). `edge_share_of_ev` is the share that comes from the edge itself. `failed_combines_per_year` makes the churn visible for one account slot run continuously.

## 3. Funded account: payout policy is first-order at positive edge (exploratory, D-45)

Realised cash per year over a two-year horizon, standard path, net-positive rule on. Balance left in the account at the horizon is **not** counted (conservative).

|                          |   0.0 |   0.05 |   0.1 |   0.2 |
|:-------------------------|------:|-------:|------:|------:|
| ('1.5:1 $1000', 0.0)     |   432 |    686 |  1262 |  4075 |
| ('1.5:1 $1000', 1000.0)  |   410 |    698 |  1255 |  4163 |
| ('1.5:1 $1000', 2000.0)  |   417 |    710 |  1291 |  4210 |
| ('1.5:1 $1000', 3000.0)  |   409 |    711 |  1332 |  4537 |
| ('1.5:1 $1000', 5000.0)  |   397 |    803 |  1633 |  5551 |
| ('1.5:1 $1000', 8000.0)  |   nan |    907 |  1925 |  6479 |
| ('1.5:1 $1000', 12000.0) |   nan |    989 |  2168 |  6792 |
| ('1.5:1 $500', 0.0)      |   355 |    474 |   631 |  1268 |
| ('1.5:1 $500', 1000.0)   |   368 |    501 |   695 |  1383 |
| ('1.5:1 $500', 2000.0)   |   374 |    582 |   869 |  2070 |
| ('1.5:1 $500', 3000.0)   |   384 |    653 |  1134 |  3461 |
| ('1.5:1 $500', 5000.0)   |   387 |    847 |  1818 |  6681 |
| ('1.5:1 $500', 8000.0)   |   nan |   1006 |  2411 |  8313 |
| ('1.5:1 $500', 12000.0)  |   nan |    844 |  2234 |  7903 |
| ('2:1 $150', 0.0)        |   190 |    243 |   309 |   523 |
| ('2:1 $150', 1000.0)     |   309 |    481 |   713 |  1466 |
| ('2:1 $150', 2000.0)     |   346 |    712 |  1358 |  3785 |
| ('2:1 $150', 3000.0)     |   313 |    769 |  1594 |  4481 |
| ('2:1 $150', 5000.0)     |   175 |    547 |  1293 |  4001 |
| ('2:1 $150', 8000.0)     |   nan |    232 |   716 |  2941 |
| ('2:1 $150', 12000.0)    |   nan |     45 |   223 |  1660 |
| ('2:1 $300', 0.0)        |   301 |    387 |   505 |   882 |
| ('2:1 $300', 1000.0)     |   346 |    466 |   631 |  1157 |
| ('2:1 $300', 2000.0)     |   376 |    576 |   890 |  2078 |
| ('2:1 $300', 3000.0)     |   376 |    686 |  1226 |  3637 |
| ('2:1 $300', 5000.0)     |   352 |    834 |  1777 |  5670 |
| ('2:1 $300', 8000.0)     |   nan |    739 |  1736 |  5641 |
| ('2:1 $300', 12000.0)    |   nan |    480 |  1276 |  4782 |
| ('2:1 $750', 0.0)        |   423 |    650 |  1054 |  3123 |
| ('2:1 $750', 1000.0)     |   426 |    652 |  1109 |  3060 |
| ('2:1 $750', 2000.0)     |   415 |    663 |  1107 |  3224 |
| ('2:1 $750', 3000.0)     |   412 |    699 |  1179 |  3543 |
| ('2:1 $750', 5000.0)     |   417 |    761 |  1393 |  4441 |

### Best funded policy found per edge

|   edge | prof       |   keep_balance |   cash_per_year |   p_alive_2y |   unrealised_2y |   take_max_best_profile |
|-------:|:-----------|---------------:|----------------:|-------------:|----------------:|------------------------:|
|   0.05 | 1.5:1 $500 |           8000 |         1006.22 |         0.05 |          290.86 |                  685.78 |
|   0.1  | 1.5:1 $500 |           8000 |         2410.73 |         0.12 |          832.24 |                 1261.69 |
|   0.2  | 1.5:1 $500 |           8000 |         8313.04 |         0.36 |         2801.5  |                 4074.94 |

## 4. Value per Combine attempt with the best funded policy found

|   edge | combine_profile   |   p_pass | funded_policy           |   funded_cash_2y |   ev_per_attempt |
|-------:|:------------------|---------:|:------------------------|-----------------:|-----------------:|
|   0.05 | 2:1 $750          |    0.329 | 1.5:1 $500, keep $8,000 |          2012.44 |          563.397 |
|   0.1  | 1.5:1 $500        |    0.387 | 1.5:1 $500, keep $8,000 |          4821.47 |         1757.4   |
|   0.2  | 1.5:1 $500        |    0.517 | 1.5:1 $500, keep $8,000 |         16626.1  |         8463.81  |

## Caveats

- Funded values use a two-year horizon and count only realised cash; larger buffers leave more unrealised balance, so they are understated.
- The buffer and small-risk results are exploratory (chosen after seeing the pre-registered results); their grids are coarse and one optimum (1.5:1 $1,000) is still rising at the largest buffer tested.
- One trade per day; fixed risk; no contract-size (scaling plan) limits; drift convention for edge; exact-at-stop fills. A real edge must survive realistic fills (Prohibited Trading Strategies: no reliance on SIM stop fills).
- Edge is per trade after costs. Commissions and slippage are the difference between a gross and a net edge.
