#!/usr/bin/env bash
# fetch.sh <firm-slug> <name> <url>
# Saves raw HTML to raw/<firm>/<name>.html, visible text to raw/<firm>/<name>.txt
# (plus <name>.txt.json.txt for embedded JSON and <name>.scripts.txt for inline scripts),
# and appends "date<TAB>http<TAB>bytes<TAB>name<TAB>url" to raw/<firm>/INDEX.tsv.
# Honest client: curl's own user agent, no cookies, no forms, one request per second.
# A bot challenge (HTTP 403/503 "Just a moment...") is recorded, never worked around.
set -u
S="C:/Users/resni/AppData/Local/Temp/claude/197752aa8b2362c7/9862c1b3-c57d-4498-a2d7-44492c7a25e6/scratchpad/wt-firms"
firm="$1"; name="$2"; url="$3"
d="$S/raw/$firm"; mkdir -p "$d"
code=$(curl -sS -L --max-time 40 -o "$d/$name.html" -w "%{http_code}\t%{size_download}" "$url" 2>"$d/$name.err")
printf "%s\t%s\t%s\t%s\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$code" "$name" "$url" >> "$d/INDEX.tsv"
python -I "$S/tools/html2text.py" "$d/$name.html" "$d/$name.txt" >/dev/null 2>&1
python -I "$S/tools/scripts_text.py" "$d/$name.html" "$d/$name.scripts.txt" >/dev/null 2>&1
chars=$(wc -c < "$d/$name.txt" 2>/dev/null || echo 0)
echo "$code text=$chars $name $url"
if grep -q "Just a moment\|cf-challenge\|challenges.cloudflare.com" "$d/$name.html" 2>/dev/null; then echo "  (bot challenge served -- not worked around)"; fi
sleep 1
