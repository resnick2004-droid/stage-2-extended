"""Check every quote rendered in the note's Appendix A against the saved pages of its firm.

Usage: python -I check_note.py <scratch-root> <note.md>
A quote line is '  - "<text>" [Pn]'; the firm is the nearest '### ... (`slug`) --' heading above it.
A firm whose <scratch-root>/firms/<slug>.json is a struck stub (E-020, Q-34) is skipped: its saved pages are deleted,
and any quote line under its heading is refused.
"""
import glob
import json
import os
import re
import sys

FOLD = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"',
                      "–": "-", "—": "-", " ": " ", "…": "..."})


def norm(s):
    s = s.translate(FOLD).replace("|", " | ")
    return re.sub(r"\s+", " ", s).strip()


def struck(slug):
    p = os.path.join(S, "firms", slug + ".json")
    return os.path.exists(p) and "struck" in json.load(open(p, encoding="utf-8"))


S, note = sys.argv[1], sys.argv[2]
text = open(note, encoding="utf-8").read()
app = text.split("## Appendix A.", 1)[1]
slug = None
cache = {}
skipped = []
ok = bad = 0
for line in app.splitlines():
    m = re.match(r"^### .*\(`([a-z0-9]+)`\) --", line)
    if m:
        slug = m.group(1)
        if struck(slug):
            if slug not in skipped:
                skipped.append(slug)
            continue
        if slug not in cache:
            blob = ""
            for f in glob.glob(os.path.join(S, "raw", slug, "*.txt")):
                blob += "\n" + open(f, encoding="utf-8", errors="replace").read()
            cache[slug] = norm(blob)
        continue
    m = re.match(r'^\s*- "(.*)" \[P\d+\]$', line)
    if m and slug:
        if slug in skipped:
            bad += 1
            print("QUOTE UNDER STRUCK HEADING", slug, m.group(1)[:150])
        elif norm(m.group(1)) in cache[slug]:
            ok += 1
        else:
            bad += 1
            print("MISS", slug, m.group(1)[:150])
print(f"note quotes found verbatim: {ok}; not found: {bad}")
print(f"struck sections skipped: {len(skipped)} ({', '.join(skipped)})")
sys.exit(1 if bad else 0)
