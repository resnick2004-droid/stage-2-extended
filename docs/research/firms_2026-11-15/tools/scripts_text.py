"""Inline <script> bodies of an HTML file (Next.js flight data etc.), with JSON string escapes decoded.

Usage: python -I scripts_text.py in.html out.txt
Lets a reader grep page text that a JavaScript site ships inside its scripts.
"""
import sys
import re

src = open(sys.argv[1], encoding="utf-8", errors="replace").read()
bodies = re.findall(r"<script[^>]*>(.*?)</script>", src, flags=re.S | re.I)
out = []
for b in bodies:
    if not b.strip():
        continue
    t = b
    for _ in range(2):
        t = t.replace('\\"', '"').replace("\\n", "\n").replace("\\u0026", "&").replace("\\u003c", "<")
        t = t.replace("\\u003e", ">").replace("\\u2019", "’").replace("\\u2014", "—")
        t = t.replace("\\u2013", "–").replace("\\u201c", "“").replace("\\u201d", "”")
        t = t.replace("\\\\", "\\")
    out.append(t)
text = "\n\n----- script -----\n\n".join(out)
with open(sys.argv[2], "w", encoding="utf-8") as f:
    f.write(text)
print(f"{sys.argv[2]}: {len(text)} chars")
