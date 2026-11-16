"""Parse the BLS release-schedule pages (https://www.bls.gov/schedule/<year>/home.htm, 2009-2025, retained as fetched
on 2026-10-05 under data/raw/bls_schedule/ -- US federal government work, public domain) into one table: date, weekday,
time (ET), release and the source URL for every scheduled news release, then the 08:30 AM subset and the day-level file
FV3 reads (D-293). The provenance file beside the outputs records the fetch time and the sha256 of every page.

    python scripts/parse_bls_schedule.py        # rewrites the three CSVs under data/ from the retained pages
"""
import csv
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "data" / "raw" / "bls_schedule"
OUT = ROOT / "data"


class Rows(HTMLParser):
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


out = []
for f in sorted(HERE.glob("*.htm")):
    year = int(f.stem)
    p = Rows()
    p.feed(f.read_text(encoding="utf-8", errors="replace"))
    n = 0
    for r in p.rows:
        if len(r) < 3 or r[0].lower().startswith("date"):
            continue
        try:
            d = datetime.strptime(r[0], "%A, %B %d, %Y").date()
        except ValueError:
            continue
        time, release = r[1], r[2]
        out.append({"date": d.isoformat(), "weekday": d.strftime("%a"), "time_et": time, "release": release,
                    "year": year, "source": f"https://www.bls.gov/schedule/{year}/home.htm"})
        n += 1
    print(f"{year}: {n} rows")

with (OUT / "releases_bls_all_2009_2025.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
e830 = sorted((r for r in out if r["time_et"].startswith("08:30")), key=lambda r: (r["date"], r["release"]))
with (OUT / "releases_bls_0830_2009_2025.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["date", "weekday", "time_et", "release", "source_url"])      # the validated file's columns
    for r in e830:
        w.writerow([r["date"], r["weekday"], r["time_et"], r["release"], r["source"]])
by_date = {}
for r in e830:
    by_date.setdefault(r["date"], []).append(r["release"])
with (OUT / "release_days_0830_2009_2025.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["date", "n_releases", "releases"])
    for d in sorted(by_date):
        w.writerow([d, len(by_date[d]), " | ".join(by_date[d])])
print("all rows", len(out), "| 08:30 rows", len(e830), "| distinct 08:30 dates", len({r["date"] for r in e830}))
from collections import Counter
names = Counter(re.sub(r" for .*$", "", r["release"]) for r in e830)
for k, v in names.most_common(20):
    print(f"  {v:4d}  {k}")
times = Counter(r["time_et"] for r in out)
print("times:", times.most_common(8))
