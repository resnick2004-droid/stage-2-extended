import os, sys, json, hashlib
import pandas as pd
R = r"c:\Users\resni\OneDrive\Desktop\Stage 2 - Extended\vendor\stage2\results"

# references cross-check
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for ch in iter(lambda: f.read(1 << 20), b''):
            h.update(ch)
    return h.hexdigest()
H = {p: sha(os.path.join(R, p)) for p in os.listdir(R) if not p.endswith('.manifest.json')}

def walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and len(v) == 64 and all(c in '0123456789abcdef' for c in v) and (k.endswith('.csv') or k.endswith('.json')):
                yield path + '/' + k, k, v
            else:
                yield from walk(v, path + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, path + f'[{i}]')

print('== referenced sha256 (any nested key named *.csv) ==')
for p in sorted(os.listdir(R)):
    if not p.endswith('.manifest.json'):
        continue
    m = json.load(open(os.path.join(R, p), encoding='utf-8'))
    for path, k, v in walk(m):
        got = H.get(k)
        st = 'ABSENT' if got is None else ('OK' if got == v else 'DIFF')
        if st != 'ABSENT':
            print(f'{p[:-14]:28s} {path:60s} {st}')
        else:
            print(f'{p[:-14]:28s} {path:60s} absent from snapshot')

files = sys.argv[1:]
for f in files:
    print('\n#########', f)
    df = pd.read_csv(os.path.join(R, f), low_memory=False)
    print('shape', df.shape)
    print('columns', list(df.columns))
    if 'section' in df.columns:
        print(df['section'].value_counts().to_string())
