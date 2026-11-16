import hashlib, json, os, glob
R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for ch in iter(lambda: f.read(1 << 20), b''):
            h.update(ch)
    return h.hexdigest()

hashes = {}
for p in sorted(os.listdir(R)):
    fp = os.path.join(R, p)
    if p.endswith('.manifest.json'):
        continue
    hashes[p] = sha(fp)

print("== own manifest vs file ==")
for p in sorted(os.listdir(R)):
    if not p.endswith('.manifest.json'):
        continue
    m = json.load(open(os.path.join(R, p), encoding='utf-8'))
    target = p[:-len('.manifest.json')]
    got = hashes.get(target)
    want = m.get('sha256')
    # count rows
    nrows = None
    if os.path.exists(os.path.join(R, target)):
        with open(os.path.join(R, target), 'rb') as f:
            nrows = sum(1 for _ in f) - 1
    print(f"{target:40s} {'OK ' if got == want else 'MISMATCH'} rows_manifest={m.get('rows')} rows_file={nrows} commit={str(m.get('git_commit'))[:8]} dirty={m.get('git_dirty')} script={m.get('script')} seed={m.get('seed')} ts={m.get('timestamp')} prereg={m.get('prereg_id')}")
    if got != want:
        print("   file:", got, "\n   mani:", want)

print("\n== provenance sources cross-check ==")
for p in sorted(os.listdir(R)):
    if not p.endswith('.manifest.json'):
        continue
    m = json.load(open(os.path.join(R, p), encoding='utf-8'))
    prov = m.get('provenance') or {}
    srcs = prov.get('sources') if isinstance(prov, dict) else None
    if not srcs:
        continue
    for s, info in srcs.items():
        if not isinstance(info, dict):
            continue
        want = info.get('sha256')
        got = hashes.get(s)
        st = 'ABSENT' if got is None else ('OK' if got == want else 'DIFF')
        print(f"{p[:-14]:28s} cites {s:32s} {st} (cited commit {str(info.get('git_commit'))[:8]})")

# files without manifests
print("\n== files without manifest ==")
for p in hashes:
    if not os.path.exists(os.path.join(R, p + '.manifest.json')):
        print(p, hashes[p])
