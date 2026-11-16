"""Visible text of an HTML file, tables as ' | ' rows.

Usage: python -I html2text.py in.html [out.txt]
Writes out.txt (visible text) and, if the page embeds JSON (Next.js etc.), out.txt.json.txt.
"""
import sys
import html.parser
import re

SKIP = {"script", "style", "noscript", "svg", "head", "template"}
BLOCK = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "section", "article",
         "ul", "ol", "table", "thead", "tbody", "blockquote", "header", "footer", "nav", "dt", "dd",
         "summary", "details"}
NL = "\n"


class P(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0
        self.cell = 0
        self.scripts = []
        self.in_json = False

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
            a = dict(attrs)
            if tag == "script" and a.get("type") in ("application/json", "application/ld+json"):
                self.in_json = True
            if tag == "script" and a.get("id") == "__NEXT_DATA__":
                self.in_json = True
            return
        if tag in ("td", "th"):
            self.cell += 1
            self.out.append(" | ")
        elif tag == "tr":
            self.out.append(NL)
        elif tag in BLOCK and self.cell:
            self.out.append(" ")
        elif tag in BLOCK:
            self.out.append(NL)
        if tag == "li" and not self.cell:
            self.out.append("- ")

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
            self.in_json = False
            return
        if tag in ("td", "th"):
            self.cell = max(0, self.cell - 1)
            return
        if tag in BLOCK and self.cell:
            self.out.append(" ")
        elif tag in BLOCK:
            self.out.append(NL)

    def handle_data(self, data):
        if self.skip:
            if self.in_json:
                self.scripts.append(data)
            return
        self.out.append(data)


def main():
    src = open(sys.argv[1], encoding="utf-8", errors="replace").read()
    p = P()
    p.feed(src)
    text = "".join(p.out)
    text = re.sub(r"[ \t\r\f\v ]+", " ", text)
    text = re.sub(r" *\n *", NL, text)
    text = re.sub(r"\n{3,}", NL + NL, text).strip()
    if len(sys.argv) > 2:
        out = sys.argv[2]
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        if p.scripts:
            with open(out + ".json.txt", "w", encoding="utf-8") as f:
                f.write((NL + NL).join(p.scripts))
        print(f"{out}: {len(text)} chars text, {sum(len(s) for s in p.scripts)} chars json")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(text)


main()
