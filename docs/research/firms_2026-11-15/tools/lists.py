"""Generated lists for the note's body: UNVERIFIED terms per plan block, and recorded official-page conflicts.

Usage: python -I lists.py <scratch-root> unverified|conflicts|matrix slug1 slug2 ...
"""
import json
import os
import re
import sys

root, mode = sys.argv[1], sys.argv[2]
slugs = sys.argv[3:]
sys.stdout.reconfigure(encoding="utf-8")


def one(s):
    return " ".join(str(s).split())


MATRIX_KEYS = ["eval_profit_target", "eval_drawdown_amount", "eval_drawdown_type", "eval_drawdown_lock",
               "eval_consistency_rule", "eval_fee", "activation_fee", "funded_drawdown_type",
               "payout_balance_consequence", "funded_consistency_rule", "payout_cap", "payout_frequency_gate",
               "payout_split", "max_accounts"]

for slug in slugs:
    d = json.load(open(os.path.join(root, "firms", slug + ".json"), encoding="utf-8"))
    blocks = [k for k in d if k.startswith("terms") and d[k]]
    if mode == "unverified":
        items = []
        for b in blocks:
            for k, v in d[b].items():
                if isinstance(v, dict) and not str(v.get("status", "")).startswith("verified"):
                    items.append(f"`{b}.{k}`" if b != "terms" else f"`{k}`")
        sc = d.get("screen", {})
        for k, v in sc.items():
            if isinstance(v, dict) and not str(v.get("status", "")).startswith("verified"):
                items.append(f"screen `{k}`")
        print(f"- **{d['firm']}** ({len(items)}): " + (", ".join(items) if items else "none"))
    elif mode == "conflicts":
        seen = set()
        for where, obj in [("screen", d.get("screen", {}))] + [(b, d[b]) for b in blocks]:
            for k, v in obj.items():
                if not isinstance(v, dict):
                    continue
                note = one(v.get("note") or "")
                if re.search(r"conflict|contradict|disagree", note, re.I) and note not in seen:
                    seen.add(note)
                    print(f"- **{d['firm']}** `{k}`: {note}")
    elif mode == "matrix":
        for b in blocks:
            print(f"#### {d['firm']} -- `{b}`")
            for k in MATRIX_KEYS:
                v = d[b].get(k)
                if isinstance(v, dict):
                    print(f"- {k}: {one(v.get('value'))} [{v.get('status')}]")
