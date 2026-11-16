"""Resolve {{E:key}} / {{T:key}} / {{F:key}} tokens in deck.pptx from the document build's refs.json (so both deliverables
share one numbering). Fails if any token is unresolved."""
import json, re, zipfile, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
refs = json.load(open(os.path.join(HERE, "refs.json")))
src = os.path.join(HERE, "deck.pptx"); tmp = src + ".tmp"
def tok(m):
    kind, key = m.group(1), m.group(2)
    if key not in refs[kind]: sys.exit(f"unresolved reference {kind}:{key}")
    return str(refs[kind][key])
n = 0
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename.endswith(".xml"):
            txt = data.decode("utf8"); new, k = re.subn(r"\{\{([ETF]):([A-Za-z0-9_]+)\}\}", tok, txt); n += k
            assert "{{" not in new, f"token left in {item.filename}"
            data = new.encode("utf8")
        zout.writestr(item, data)
os.replace(tmp, src); print(f"resolved {n} reference tokens in deck.pptx")
