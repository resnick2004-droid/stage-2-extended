import os
HERE = os.path.dirname(os.path.abspath(__file__))
import json, subprocess, re, zipfile, shutil, os, sys
from xml.sax.saxutils import escape
D = HERE + "/"; SOFFICE = os.environ.get("SOFFICE_PY", "soffice")   # a LibreOffice binary, or a .py wrapper around it
heads = json.load(open(D + "headings.json"))
CONTENT_W = 10080

def render(docx, pdf):
    cmd = (["python", SOFFICE] if SOFFICE.endswith(".py") else [SOFFICE]) + ["--headless", "--convert-to", "pdf", "--outdir", D, docx]
    subprocess.run(cmd, capture_output=True)
    made = D + os.path.basename(docx).replace(".docx", ".pdf")
    if made != pdf: shutil.move(made, pdf)

def norm(t): return re.sub(r"\s+", " ", t).strip().lower()

def page_numbers(pdf):
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
    pages = [norm(subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "-layout", pdf, "-"], capture_output=True, text=True).stdout) for i in range(1, n + 1)]
    toc_pages = {i for i, pg in enumerate(pages) if pg.count("....") >= 3}
    out = {}; start = 0
    for h in heads:
        key = norm(h["text"])[:45]
        found = None
        for i in range(start, n):
            if i in toc_pages: continue
            if key in pages[i]: found = i; break
        if found is None:  # fallback: shorter key
            key = norm(h["text"])[:25]
            for i in range(start, n):
                if i in toc_pages: continue
                if key in pages[i]: found = i; break
        if found is None: print("NOT FOUND:", h["text"]); found = start
        out[h["id"]] = found + 1; start = found  # headings are in order; the TOC page itself contains titles, so start after page of previous heading
    return out, n

def toc_xml(pn):
    tabs = f'<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="{CONTENT_W}"/></w:tabs>'
    paras = []
    for i, h in enumerate(heads):
        style = f"TOC{h['level']}"
        pre = ('<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>' if i == 0 else "")
        post = ('<w:r><w:fldChar w:fldCharType="end"/></w:r>' if i == len(heads) - 1 else "")
        paras.append(f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{tabs}</w:pPr>{pre}<w:hyperlink w:anchor="{h["id"]}" w:history="1"><w:r><w:t xml:space="preserve">{escape(h["text"])}</w:t></w:r><w:r><w:tab/></w:r><w:r><w:t>{pn[h["id"]]}</w:t></w:r></w:hyperlink>{post}</w:p>')
    return "".join(paras)

def inject(src, dst, pn):
    with zipfile.ZipFile(src) as z: files = {n: z.read(n) for n in z.namelist()}
    xml = files["word/document.xml"].decode("utf8")
    m = re.search(r"<w:p\b[^>]*>(?:(?!<w:p\b).)*?%%TOC%%.*?</w:p>", xml, re.S)
    assert m, "placeholder not found"
    xml = xml[:m.start()] + toc_xml(pn) + xml[m.end():]
    # resolve {{E:key}} / {{T:key}} / {{F:key}} reference tokens from the build's registry
    refs = json.load(open(D + "refs.json"))
    def tok(mm):
        kind, key = mm.group(1), mm.group(2)
        if key not in refs[kind]: raise KeyError(f"unresolved reference {kind}:{key}")
        return str(refs[kind][key])
    xml = re.sub(r"\{\{([ETF]):([A-Za-z0-9_]+)\}\}", tok, xml)
    assert "{{" not in xml, "unresolved token left in document"
    # renumber bookmark ids uniquely (docx-js emits duplicates)
    counter = [0]; stack = []
    def fix(mm):
        tag = mm.group(1)
        if tag == "bookmarkStart":
            counter[0] += 1; stack.append(counter[0]); return f'<w:bookmarkStart w:id="{counter[0]}"'
        return f'<w:bookmarkEnd w:id="{stack.pop()}"'
    xml = re.sub(r'<w:(bookmarkStart) w:name="(_Toc\d+)" w:id="\d+"', lambda mm: f'<w:bookmarkStart w:name="{mm.group(2)}" w:id="{mm.group(2)[4:]}"', xml)
    ends = iter(range(1, 10000))
    xml = re.sub(r'<w:bookmarkEnd w:id="\d+"', lambda mm: f'<w:bookmarkEnd w:id="{next(ends)}"', xml)
    # docx-js writes pBdr children as top,bottom,left,right; schema wants top,left,bottom,right
    xml = re.sub(r'(<w:pBdr>)(<w:top [^>]*/>)(<w:bottom [^>]*/>)(<w:left [^>]*/>)', r'\1\2\4\3', xml)
    files["word/document.xml"] = xml.encode("utf8")
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in files.items(): z.writestr(n, b)

# pass 0: guess page numbers from raw render (placeholder occupies one line)
render(D + "report_raw.docx", D + "report_raw.pdf")
pn, n0 = page_numbers(D + "report_raw.pdf")
for it in range(3):
    inject(D + "report_raw.docx", D + "report.docx", pn)
    render(D + "report.docx", D + "report.pdf")
    pn2, n = page_numbers(D + "report.pdf")
    print(f"iteration {it}: pages {n}, changed entries {sum(pn[k] != pn2[k] for k in pn)}")
    if pn2 == pn: break
    pn = pn2
print("TOC injected; final pages", n)
