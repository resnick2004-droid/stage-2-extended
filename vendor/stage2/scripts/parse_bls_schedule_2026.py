"""Parse BLS's 2026 release-schedule page into the 2026 release days FV3-C's confirmation kits need (D-355).

    python scripts/parse_bls_schedule_2026.py

The 2009-2025 pages were fetched by script on 2026-10-05 (`scripts/parse_bls_schedule.py`, `data/raw/bls_schedule/`).
On 2026-10-13 BLS refused every automated request (403 to a scripted fetch, Access Denied to headless Edge), so the 2026
page (https://www.bls.gov/schedule/2026/home.htm) was saved by hand from the operator's browser on 2026-10-13 as a
complete web page ("Schedule of Selected Releases 2026.html"; its folder of stylesheets, scripts and images not kept)
and the HTML file is retained, byte for byte as saved, at `data/raw/bls_schedule_2026/2026.htm` -- its own folder, so
the 2009-2025 parser's glob never reads it. A browser's saved page is its serialisation of what the server sent (links
re-pointed at the local folder), not the server's raw bytes as the 2009-2025 pages are; the release tables are the
page's. The
same reading as that parser: html.parser over `<table class="release-list">`, rows whose first cell is a date and whose
time cell starts with 08:30. Writes `data/releases_bls_0830_2026.csv` (one row per 08:30 release, the validated file's
columns), `data/release_days_0830_2026.csv` (each date once, the file `fv3_kit.news_mask_2026` reads) and
`data/releases_bls_0830_2026.provenance.json` (the page's sha256 and bytes, how it was obtained). Refuses a page that is
not 2026's schedule, a date outside 2026 or a page with no 08:30 release.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "data" / "raw" / "bls_schedule_2026" / "2026.htm"
OUT = ROOT / "data"
URL = "https://www.bls.gov/schedule/2026/home.htm"


class Rows(HTMLParser):
    """`scripts/parse_bls_schedule.py`'s reader, unchanged: every row of the release-list tables, cell texts."""

    def __init__(self):
        super().__init__()
        self.in_table = self.in_cell = False
        self.row, self.rows, self.text = [], [], ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table" and "release-list" in (a.get("class") or ""):
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.row = []
        elif self.in_table and tag in ("td", "th"):
            self.in_cell, self.text = True, ""

    def handle_endtag(self, tag):
        if tag == "table" and self.in_table:
            self.in_table = False
        elif self.in_table and tag in ("td", "th") and self.in_cell:
            self.row.append(re.sub(r"\s+", " ", self.text).strip())
            self.in_cell = False
        elif self.in_table and tag == "tr" and self.row:
            self.rows.append(self.row)
            self.row = []

    def handle_data(self, data):
        if self.in_cell:
            self.text += data


def parse(page: Path) -> list[dict]:
    """Every dated release row of the page."""
    raw = page.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    if "2026" not in (re.search(r"<title>(.*?)</title>", text, re.IGNORECASE | re.DOTALL) or [None, ""])[1]:
        raise SystemExit(f"REFUSED: {page} is not BLS's 2026 schedule page (its title does not name 2026).")
    p = Rows()
    p.feed(text)
    out = []
    for r in p.rows:
        if len(r) < 3 or r[0].lower().startswith("date"):
            continue
        try:
            d = datetime.strptime(r[0], "%A, %B %d, %Y").date()
        except ValueError:
            continue
        if d.year != 2026:
            raise SystemExit(f"REFUSED: a release dated {d} on the 2026 page.")
        out.append({"date": d.isoformat(), "weekday": d.strftime("%a"), "time_et": r[1], "release": r[2]})
    return out


def main(page: Path = PAGE, out_dir: Path = OUT) -> int:
    if not page.is_file():
        print(f"REFUSED: {page} is not on record; save {URL} by hand (Ctrl+S, HTML only) and copy it there.")
        return 2
    rows = parse(page)
    e830 = sorted((r for r in rows if r["time_et"].startswith("08:30")), key=lambda r: (r["date"], r["release"]))
    if not e830:
        print("REFUSED: no 08:30 release on the page.")
        return 2
    with (out_dir / "releases_bls_0830_2026.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["date", "weekday", "time_et", "release", "source_url"])
        for r in e830:
            w.writerow([r["date"], r["weekday"], r["time_et"], r["release"], URL])
    by_date: dict[str, list[str]] = {}
    for r in e830:
        by_date.setdefault(r["date"], []).append(r["release"])
    with (out_dir / "release_days_0830_2026.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["date", "n_releases", "releases"])
        for d in sorted(by_date):
            w.writerow([d, len(by_date[d]), " | ".join(by_date[d])])
    raw = page.read_bytes()
    prov = {"what": "Every BLS news release scheduled at 08:30 AM Eastern in 2026, from the Bureau of Labor Statistics' "
                    "own 2026 schedule page, parsed as the 2009-2025 pages were; the day-level file lists each date "
                    "once with its releases.",
            "parser": "scripts/parse_bls_schedule_2026.py (html.parser over <table class='release-list'>; rows whose "
                      "first cell is a date and whose time cell starts with '08:30'; scripts/parse_bls_schedule.py's "
                      "reader)",
            "page": {"url": URL, "file": str(page.relative_to(ROOT)).replace("\\", "/"),
                     "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
                     "obtained": "saved by hand from the operator's browser on 2026-10-13 as a complete web page "
                                 "('Schedule of Selected Releases 2026.html'; the HTML file kept, its _files folder "
                                 "not) -- BLS refused automated requests that day: 403 to a scripted fetch, Access "
                                 "Denied to headless Edge"},
            "rows": len(e830), "distinct_dates": len(by_date), "all_release_rows": len(rows),
            "packaged_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "use": "FV3-C's confirmation kits (D-355): on these dates the session's fair price is the open of the 8:30 "
                   "ET candle; added to the kits' embedded table after the cores (fv3_kit.confirm_preamble); not a "
                   "firm rule, so verified here by source and hash, and checked by the data-integrity agent before "
                   "any kit is generated."}
    (out_dir / "releases_bls_0830_2026.provenance.json").write_text(json.dumps(prov, indent=1) + "\n",
                                                                     encoding="utf-8", newline="\n")
    print(f"2026: {len(rows)} release rows, {len(e830)} at 08:30 on {len(by_date)} dates; sha256 {prov['page']['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*(Path(a) for a in sys.argv[1:3])))
