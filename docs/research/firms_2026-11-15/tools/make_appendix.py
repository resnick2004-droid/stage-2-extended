"""Render firms/<slug>.json (quote-checked) to the note's per-firm appendix, in markdown.

Usage: python -I make_appendix.py <scratch-root> <out.md> slug1 slug2 ...
Quotes are copied from the JSON unchanged (they were checked verbatim against the saved pages).
"""
import json
import os
import sys

root, out = sys.argv[1], sys.argv[2]
slugs = sys.argv[3:]

SCREEN_ORDER = ["drawdown_eval", "drawdown_funded", "consistency_eval", "consistency_funded", "max_funded_accounts",
                "copy_trading", "opposite_positions", "news", "automation", "sizing_gambling"]


def one_line(s):
    return " ".join(str(s).split())


PAGES = {}


def page_key(qq):
    url = qq.get("url") or "(no url)"
    aid = one_line(qq.get("article_id") or "")
    pd = one_line(qq.get("page_date") or "")
    k = (url, aid, pd)
    if k not in PAGES:
        PAGES[k] = f"P{len(PAGES) + 1}"
    return PAGES[k]


def render_quote(qq):
    t = one_line(qq["text"])
    return f"\"{t}\" [{page_key(qq)}]"


def render_term(key, v, lines, indent=""):
    if not isinstance(v, dict):
        lines.append(f"{indent}- `{key}`: {one_line(v)}")
        return
    val = v.get("value")
    status = v.get("status") or "?"
    lines.append(f"{indent}- `{key}` = **{one_line(val)}** ({status})")
    for qq in v.get("quotes") or []:
        lines.append(f"{indent}  - {render_quote(qq)}")
    if v.get("looked_at"):
        lines.append(f"{indent}  - looked at: {one_line(v['looked_at'])}")
    if v.get("note"):
        lines.append(f"{indent}  - note: {one_line(v['note'])}")


lines = []
for slug in slugs:
    PAGES.clear()
    start = len(lines)
    d = json.load(open(os.path.join(root, "firms", slug + ".json"), encoding="utf-8"))
    sc = d.get("screen", {})
    lines.append(f"### {d.get('firm')} (`{slug}`) -- {sc.get('verdict')}")
    lines.append("")
    lines.append(f"Official domains: {', '.join(one_line(x) for x in d.get('official_domains', []))}. Read {d.get('date_read', '2026-11-15')}.")
    lines.append(f"Plan captured: {one_line(d.get('plan_captured'))}.")
    lines.append(f"Verdict: **{sc.get('verdict')}** -- {one_line(sc.get('verdict_reason'))}")
    if d.get("unreadable"):
        lines.append("")
        lines.append("Unreadable (not worked around):")
        for u in d["unreadable"]:
            lines.append(f"- {u.get('url')} -- {one_line(u.get('what'))}")
    if d.get("plans_seen"):
        lines.append("")
        lines.append("Plans seen:")
        for p in d["plans_seen"]:
            lines.append(f"- {one_line(p.get('name'))}: drawdown {one_line(p.get('drawdown'))}; consistency evaluation {one_line(p.get('consistency_eval'))}, funded {one_line(p.get('consistency_funded'))}")
            qq = p.get("quote")
            if isinstance(qq, dict) and qq.get("text"):
                lines.append(f"  - {render_quote(qq)}")
            elif isinstance(qq, list):
                for x in qq:
                    lines.append(f"  - {render_quote(x)}")
    for k, v in d.items():
        if k.endswith("quotes") and isinstance(v, list) and k not in ("quotes",):
            lines.append("")
            lines.append(f"{k.replace('_', ' ')}:")
            for x in v:
                lines.append(f"- {render_quote(x)}")
    lines.append("")
    lines.append("**Screen**")
    lines.append("")
    for k in SCREEN_ORDER:
        if k in sc:
            render_term(k, sc[k], lines)
    for k, v in sc.items():
        if k not in SCREEN_ORDER and k not in ("verdict", "verdict_reason"):
            render_term(k, v, lines)
    for b in [k for k in d if k.startswith("terms")]:
        if not d[b]:
            continue
        lines.append("")
        lines.append(f"**Terms (`{b}`)**")
        lines.append("")
        for k, v in d[b].items():
            render_term(k, v, lines)
    KNOWN = {"firm", "slug", "official_domains", "date_read", "unreadable", "plans_seen", "plan_captured", "screen"}
    for k, v in d.items():
        if k in KNOWN or k.startswith("terms") or (k.endswith("quotes") and isinstance(v, list)):
            continue
        lines.append("")
        lines.append(f"**{k.replace('_', ' ').capitalize()}** (reader's section)")
        lines.append("")
        if isinstance(v, dict):
            for kk, vv in v.items():
                render_term(kk, vv, lines)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    desc = "; ".join(f"{a}: {one_line(b)}" for a, b in item.items() if a != "quotes")
                    lines.append(f"- {desc}")
                    for qq in item.get("quotes") or []:
                        lines.append(f"  - {render_quote(qq)}")
                else:
                    lines.append(f"- {one_line(item)}")
        else:
            lines.append(f"- {one_line(v)}")
    lines.append("")
    plist = ["**Pages quoted** (key: URL; article id; the page's own date as shown; all read 2026-11-15)", ""]
    for (url, aid, pd), key in PAGES.items():
        plist.append(f"- [{key}] {url}" + (f"; id {aid}" if aid else "") + (f"; page date: {pd}" if pd else ""))
    plist.append("")
    lines[start + 1:start + 1] = [""] + plist
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"{out}: {sum(len(x) + 1 for x in lines)} chars, {len(lines)} lines")
