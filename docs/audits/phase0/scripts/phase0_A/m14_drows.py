import re, sys
P = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\DECISIONS.md"
H = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\docs\HANDOFF_NEW_REPO_2026-11-15.md"
text = open(P, encoding='utf-8').read().splitlines()
rows = {}
for line in text:
    m = re.match(r'^\|\s*(D-\d+)\s*\|', line)
    if m:
        rows.setdefault(m.group(1), []).append(line)
hand = open(H, encoding='utf-8').read()
cited = sorted(set(re.findall(r'(?<![A-Za-z])D-(\d{2,3})', hand)), key=int)
print('cited in handoff:', len(cited), ' '.join('D-' + c for c in cited))
missing = [c for c in cited if 'D-' + c not in rows]
print('missing rows:', missing)
dup = [k for k, v in rows.items() if len(v) > 1]
print('ids with more than one row:', dup[:40])
want = sys.argv[1].split(',') if len(sys.argv) > 1 else []
lim = int(sys.argv[2]) if len(sys.argv) > 2 else 900
for w in want:
    for line in rows.get(w, ['(none)']):
        print('\n' + line[:lim])
