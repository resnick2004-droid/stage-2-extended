"""Compact digest of firms/<slug>.json: verdict, plans, and each term's value/status (no quotes).

Usage: python -I digest.py <scratch-root> [slug ...] [--keys k1,k2]
"""
import json
import os
import sys

root = sys.argv[1]
args = sys.argv[2:]
keys = None
if "--keys" in args:
    i = args.index("--keys")
    keys = args[i + 1].split(",")
    args = args[:i] + args[i + 2:]
slugs = args or sorted(f[:-5] for f in os.listdir(os.path.join(root, "firms")) if f.endswith(".json"))
sys.stdout.reconfigure(encoding="utf-8")
for slug in slugs:
    d = json.load(open(os.path.join(root, "firms", slug + ".json"), encoding="utf-8"))
    sc = d.get("screen", {})
    print(f"#### {slug}: {d.get('firm')} | plan: {d.get('plan_captured')}")
    print(f"  VERDICT {sc.get('verdict')}: {sc.get('verdict_reason')}")
    if keys is None:
        for p in d.get("plans_seen", []):
            print(f"  plan: {p.get('name')} | dd: {p.get('drawdown')} | cons eval: {p.get('consistency_eval')} | cons funded: {p.get('consistency_funded')}")
        for k, v in sc.items():
            if isinstance(v, dict):
                print(f"  screen.{k}: [{v.get('status')}] {str(v.get('value'))[:200]}")
    blocks = [k for k in d if k.startswith("terms")]
    for b in blocks:
        print(f"  --- {b}")
        for k, v in d[b].items():
            if keys and k not in keys:
                continue
            if isinstance(v, dict):
                val = str(v.get("value"))
                note = str(v.get("note") or "")
                print(f"    {k}: [{v.get('status')}] {val[:220]}" + (f"  || note: {note[:260]}" if note and keys else ""))
            else:
                print(f"    {k}: {str(v)[:200]}")
    print()
