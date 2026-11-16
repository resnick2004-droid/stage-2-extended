"""Family R's drop rule (prereg/DRAFT_F-R_resolution.md 6.6, LF sha256 311293be...) applied mechanically to Q-55's
results/calibration_power.csv, under every reading the text leaves open. Reads the CSV only (pandas and the csv module);
imports nothing from the repository. Prints empty / not empty and line numbers; no figure."""
import csv
from pathlib import Path

R = Path(r"C:/Users/resni/OneDrive/Desktop/Stage 2 - Extended/results/calibration_power.csv")
rows = list(csv.DictReader(open(R, newline="")))           # line = index + 2 (header is line 1)


def pick(model, share, value, method, k, df_rule):
    return [(i + 2, r) for i, r in enumerate(rows)
            if r["part"] == "two_sample" and r["df_rule"] == df_rule and r["form"] == "placebo-selection"
            and r["model"] == model and r["share"] != "" and float(r["share"]) == share and r["value"] == value
            and r["method"] == method and r["k"] != "" and float(r["k"]) == k]


print("the rule as written: class block63 (the slower of block21..block63), share 0.5, cons, k = 15 column")
for df_rule in ("treated", "all"):
    for value in ("net3", "win1"):
        for model in ("block63", "block21"):
            for method, k in (("cons", 15), ("cons", 11), ("t21w", 11)):
                sel = pick(model, 0.5, value, method, k, df_rule)
                status = ("EMPTY" if sel[0][1]["difference80"] == "" else "not empty") if len(sel) == 1 else "n/a"
                print(f"df_rule={df_rule:7s} value={value} model={model:7s} method={method} k={k}: rows {len(sel)}; "
                      f"line(s) {[ln for ln, _ in sel]}; null {[r['null'] for _, r in sel]}; difference80 {status}"
                      + (f"; shift80 {'empty' if sel[0][1]['shift80'] == '' else 'not empty'}" if len(sel) == 1 else ""))
