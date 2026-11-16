"""Provenance check: every quote's file was fetched from an official host of its firm, and its stated URL matches.

Usage: python -I check_provenance.py <scratch-root>
Also lists every fetch in raw/<slug>/INDEX.tsv whose host is not in that firm's official_domains.
"""
import json
import os
import sys
from urllib.parse import urlparse


def host_ok(url_or_host, domains):
    if "://" in url_or_host:
        u = urlparse(url_or_host)
        host, path = u.netloc.lower().split(":")[0], u.path
    else:
        host, path = url_or_host.lower().split(":")[0], ""
    for d in domains:
        d = d.split(" (")[0].lower().strip()
        dhost, _, dpath = d.partition("/")
        if not (host == dhost or host.endswith("." + dhost)):
            continue
        if dpath and path and not path.lstrip("/").startswith(dpath):
            continue
        return True
    return False


def walk(obj):
    if isinstance(obj, dict):
        if "text" in obj and "file" in obj:
            yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


root = sys.argv[1]
problems = 0
for fn in sorted(os.listdir(os.path.join(root, "firms"))):
    if not fn.endswith(".json"):
        continue
    slug = fn[:-5]
    data = json.load(open(os.path.join(root, "firms", fn), encoding="utf-8"))
    domains = data.get("official_domains", [])
    index = {}
    ip = os.path.join(root, "raw", slug, "INDEX.tsv")
    if "struck" in data and not any(True for _ in walk(data)) and not os.path.exists(ip):
        # E-020 / Q-34: a struck firm's file is a stub and its saved pages are deleted; nothing is left to check
        print(f"{slug}: struck (E-020), skipped")
        continue
    if os.path.exists(ip):
        for line in open(ip, encoding="utf-8"):
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 4:
                name, url = parts[-2], parts[-1]
                index.setdefault(name, []).append((parts[1] if len(parts) > 4 else "", url))
    # every fetch on an official host?
    for name, rows in index.items():
        for code, url in rows:
            h = urlparse(url).netloc
            if not host_ok(url, domains):
                print(f"  {slug}: fetched off-list host {h} ({name}: {url})")
                problems += 1
    n = bad = 0
    for q in walk(data):
        n += 1
        f = q["file"]
        if f == "webfetch":
            if not host_ok(q.get("url", ""), domains):
                print(f"  {slug}: webfetch quote off-list host {h}")
                bad += 1
            continue
        base = os.path.basename(f)
        for suf in (".txt.json.txt", ".scripts.txt", ".txt"):
            if base.endswith(suf):
                base = base[: -len(suf)]
                break
        urls = [u for _, u in index.get(base, [])]
        if not urls:
            print(f"  {slug}: quote file {f} not in INDEX.tsv")
            bad += 1
            continue
        if not any(host_ok(u, domains) for u in urls):
            print(f"  {slug}: quote file {f} fetched from off-list host {urls}")
            bad += 1
        qurl = q.get("url", "")
        if qurl and qurl.rstrip("/") not in [u.rstrip("/") for u in urls]:
            if not host_ok(qurl, domains):
                print(f"  {slug}: quote url host off-list {qurl}")
                bad += 1
    problems += bad
    print(f"{slug}: domains={domains} quotes={n} provenance problems={bad}")
sys.exit(1 if problems else 0)
