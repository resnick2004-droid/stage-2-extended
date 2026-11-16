"""Check that every quote in firms/<slug>.json is a verbatim substring of the saved page it names.

Usage: python -I check_quotes.py <scratch-root> [slug ...]
Whitespace is collapsed and typographic quotes/dashes folded on both sides; nothing else is forgiven.
A quote whose "file" is "webfetch" cannot be byte-checked and is listed separately.
"""
import json
import os
import re
import sys

FOLD = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"',
                      "–": "-", "—": "-", " ": " ", "…": "..."})


def norm(s):
    s = s.translate(FOLD)
    s = s.replace("|", " | ")
    return re.sub(r"\s+", " ", s).strip()


def walk(obj, path=""):
    if isinstance(obj, dict):
        if "text" in obj and "file" in obj:
            yield path, obj
        for k, v in obj.items():
            yield from walk(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")


def main():
    root = sys.argv[1]
    slugs = sys.argv[2:] or sorted(f[:-5] for f in os.listdir(os.path.join(root, "firms")) if f.endswith(".json"))
    cache = {}
    total_bad = 0
    for slug in slugs:
        p = os.path.join(root, "firms", slug + ".json")
        try:
            data = json.load(open(p, encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"{slug}: JSON ERROR {e}")
            total_bad += 1
            continue
        ok = bad = wf = 0
        for path, q in walk(data):
            f = q["file"]
            if f == "webfetch":
                wf += 1
                continue
            fp = os.path.join(root, f)
            if fp not in cache:
                txt = ""
                for cand in (fp, fp + ".json.txt", fp.replace(".txt", ".scripts.txt")):
                    if os.path.exists(cand):
                        txt += "\n" + open(cand, encoding="utf-8", errors="replace").read()
                cache[fp] = norm(txt)
            if norm(q["text"]) in cache[fp]:
                ok += 1
            else:
                bad += 1
                print(f"  MISS {slug}{path}: [{f}] {q['text'][:160]!r}")
        total_bad += bad
        print(f"{slug}: {ok} quotes found verbatim, {bad} not found, {wf} via webfetch (not byte-checkable)")
    sys.exit(1 if total_bad else 0)


main()
