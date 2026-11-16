"""Check every quote rendered in the note's Appendix A against the saved pages of its firm.

Usage: python -I check_note.py <scratch-root> <note.md>
A quote line is '  - "<text>" [Pn]'; the firm is the nearest '### ... (`slug`) --' heading above it.
"""
import glob
import os
import re
import sys

FOLD = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"',
                      "–": "-", "—": "-", " ": " ", "…": "..."})


def norm(s):
    s = s.translate(FOLD).replace("|", " | ")
    return re.sub(r"\s+", " ", s).strip()


S, note = sys.argv[1], sys.argv[2]
text = open(note, encoding="utf-8").read()
app = text.split("## Appendix A.", 1)[1]
slug = None
cache = {}
ok = bad = 0
for line in app.splitlines():
    m = re.match(r"^### .*\(`([a-z0-9]+)`\) --", line)
    if m:
        slug = m.group(1)
        if slug not in cache:
            blob = ""
            for f in glob.glob(os.path.join(S, "raw", slug, "*.txt")):
                blob += "\n" + open(f, encoding="utf-8", errors="replace").read()
            cache[slug] = norm(blob)
        continue
    m = re.match(r'^\s*- "(.*)" \[P\d+\]$', line)
    if m and slug:
        if norm(m.group(1)) in cache[slug]:
            ok += 1
        else:
            bad += 1
            print("MISS", slug, m.group(1)[:150])
print(f"note quotes found verbatim: {ok}; not found: {bad}")
sys.exit(1 if bad else 0)
