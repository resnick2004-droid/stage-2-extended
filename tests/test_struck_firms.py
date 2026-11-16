"""Q-34 (E-020 (2)): what automated readers collected from the eight firms whose own terms forbid automated retrieval
is struck from the repository, and nothing else in the Q-12 survey's evidence moved.

- each of the eight per-firm files is a stub {"firm", "struck", "date"} naming the clause, quoted as recorded
  (config/rules_extended.yaml for FunderPro, Aqua and FundedNext; E-009's note for the other five);
- each of their Appendix A sections in the survey note is the heading, the screen's one-line verdict without quotes,
  and one line naming the clause and E-020;
- the quotes of theirs that the note's body carried are gone (pinned below as hashes, never as text);
- the other fourteen firms' files and Appendix A sections are byte-for-byte what they were at ec5b77d;
- the note's checkers skip a struck firm, and still refuse a quote placed under a struck firm's heading.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
RESEARCH = ROOT / "docs" / "research"
FIRMS = RESEARCH / "firms_2026-11-15" / "firms"
TOOLS = RESEARCH / "firms_2026-11-15" / "tools"
NOTE = RESEARCH / "firms_survey_2026-11-15.md"
RULES = ROOT / "config" / "rules_extended.yaml"

PREFIX = "E-020: the firm's own terms forbid automated retrieval -- "
STRUCK_LINE = "Struck (E-020): the firm's own terms forbid automated retrieval -- "
DATE = "2026-11-16"

# slug: (the firm's name as in its file at ec5b77d, its screen verdict there)
STRUCK = {
    "tradeify": ("Tradeify", "PASS"),
    "tradingpit": ("The Trading Pit", "PASS"),
    "goat": ("Goat Funded Futures (GFF)", "PASS"),
    "alpha": ("Alpha Futures", "PASS"),
    "futuresdesk": ("The Futures Desk (TS TFD Buyer, LLC; Topstep affiliate)", "FAIL"),
    "funderpro": ("FunderPro Futures (FunderPro Ltd., Malta)", "PASS"),
    "aqua": ("Aqua Futures (AquaFutures / AquaFunded Futures)", "PASS"),
    "fundednext": ("FundedNext Futures", "PASS"),
}
# Their clause is recorded in config/rules_extended.yaml (Q-26, E-020); the other five's in E-009's note.
Q26 = {"funderpro": "funderpro.automated_retrieval_terms", "aqua": "aqua.automated_retrieval_terms",
       "fundednext": "fundednext.automated_retrieval_terms"}

# The appendix order at ec5b77d (assemble.py's ORDER); it does not change.
ORDER = ["funderpro", "daytraders", "tradingpit", "aqua", "alpha", "lucid", "tradeify", "blusky", "e2t",
         "fundednext", "tradeday", "topone", "fxify", "ffn", "mffu", "phidias",
         "goat", "bulenox", "tpt", "legends", "purdia", "futuresdesk"]
KEPT = [s for s in ORDER if s not in STRUCK]

# sha256 of each kept firm's file at ec5b77d (CRLF folded to LF).
KEPT_FILES = {
    "daytraders": "5eb71f4e763826f008d6a9004bf98b7d294f1ddee84ea4e71e425ed819314628",
    "lucid": "3b45855295464c550bba8cb4457ecec11605d299e2c14d73af313343f6a6531e",
    "blusky": "c90e2364cab17564b0a2bcb575f5343b5285ca3bdfa50ab414c679d1ecdd3647",
    "e2t": "f0dbba6b56665f7d81da8dd4650e5c6e25067828ae5424586e53a47fe35a320a",
    "tradeday": "e76af1175811dc2b84949945827c3b0f11844e18cb3c6c94337903a2bf18ecf5",
    "topone": "11e85f3ff45571941901ad6bbfcef3c38c65b9b0262e64981685f18781a903d1",
    "fxify": "97a7e78a14deaff970fddf679f6286f296619ec6a4b4c3219dcfc11d1fec63a3",
    "ffn": "de827bc94247d81211b69bb3fc1a86d68e63ffa82c9bdcc1a685b014eae84e3e",
    "mffu": "c57381d9e7e45058172c7ac829f4db486f8586e3a44b71e1c87bf2bec232221f",
    "phidias": "eb8a1183cc5fb7e400d9b07e30cd5a3b0ef85e6fbd52af7e62eb85f00715081d",
    "bulenox": "07e23236811cae1a0b40cad90b181e29550357eea33dc0ba225a1d7b41f97a4e",
    "tpt": "3d80c4698fc3a9b3042dce2b683d3397b4eca9822cb13d86cf90a8032ec576c7",
    "legends": "87935be86d4bf1437c4adeeb7e3287c52d86fe9dae71ebcd38b5e85888dc5b13",
    "purdia": "f85107184025155a16ee628c18c3d07ccbf41fcb7b09b4dbe8ad6d72c724e809",
}
# sha256 of each kept firm's Appendix A section at ec5b77d (from its heading to the next heading; LF).
KEPT_SECTIONS = {
    "daytraders": "29ef6f1cd7a49415a2ac42f5d0f47f0ea3305d9921ef1cf65bb2a2a002dcb0b8",
    "lucid": "6d4481ec2e8a07879e0310e0f6741e075554f004dfc3cf43aa43927dc6962ea6",
    "blusky": "562371ffa2b5854ef747bfe584fa6c0a5f03d0744f206e4855218f5fa80ffe1f",
    "e2t": "6fd3b5b0c6d9375eb74172c5698c6f60903ceff510185be41aa80209cae0d6ea",
    "tradeday": "6dad907d088c7970dedd59b92af4de0688eed7f80bdd40ff9d60a1f6dd8e746c",
    "topone": "3ed1bdbfe85ec10dceeb6f832fb7494f925f57877a84f9191126699cbfca6c90",
    "fxify": "7cee309f3e78e8ff1116aa4a10e8223bf1bbf28b404c8a0cc14d829f2fcadcc2",
    "ffn": "375adb227bebf55e9b7dd55d7a15eab7d5b164d4f1645c85b7db81c12a3641a2",
    "mffu": "b4ace9c85342b9665f7dff15e45a5a91c8a2434767dc1b66c51535436dd71451",
    "phidias": "a1d6cc1a2e2d52be0f37a0cab06f34ed9c8af845f06167e7452e18478599078a",
    "bulenox": "2ef205456bed544f26498d8f996ab19b38a997259ac704fb21dfe6050acb8747",
    "tpt": "aa9a8648b6a07d72f01d2ce26e4b60cd60cfc30cd8533fd8ba4e4524cd9dbb0b",
    "legends": "2a83542fdd7db593e5261541925cc71a5ec79df217bdde006239391d7e6916d7",
    "purdia": "f93d495196e3c5cd496ca51eb664803fd688b252a261e63d52de79fb475bab57",
}
# h16() of each struck firm's clause segments as E-009's note recorded them at ec5b77d (body lines 70-76; The
# Futures Desk's from its Appendix A automation quote [P2]).
E009_CLAUSE_SEGMENTS = {
    "tradeify": {'8687ed7ac5e948a3', 'bf4bce8ec2656c7c'},
    "tradingpit": {'65865dab49cb6955'},
    "goat": {'1260212f395581e6', 'a59537bb30b7b35b'},
    "alpha": {'0555a25a3f84bd92', '96478f8ddf43bfcf'},
    "futuresdesk": {'e1373d8ea9f34682'},
}
# h16() of the struck firms' quoted fragments in the note's body at ec5b77d (lines 37, 100, 102-105, 108, 115, 120,
# 163-189, 298, 344, 382-383, 441, extracted by quoted_fragments()), keeping only fragments of three or more words that
# occur in no kept firm's file (so a kept firm's own quote can never trip this).
REMOVED_BODY_QUOTES = frozenset({
    "04cad69f58474751",
    "17ee0e2d5ef135e3",
    "43a97af728e41261",
    "63902e383e9b0ecc",
    "6c4eef7c28b6cb50",
    "6da7bf6d16d58682",
    "81dfb2a732f94ca8",
    "8283de29ba92a93a",
    "8e225a8af648715d",
    "a11958a6fa44226f",
    "aafdadd7b7007ae0",
    "b133cba5228c0f45",
    "b253c43b1ab67c07",
    "b31210e5e76d7b72",
    "b5583acd7fa9d072",
    "d0705ac65c444066",
    "d4ec31e6b34f39f6",
    "d6b614af5e9c6964",
    "dcd5e31edd9b36b0",
    "e7e03efe5d9e3bc6",
    "eb605297b03a9c9d",
    "ef97051b1ca2b5f9",
    "f7bbfc1b71d90746",
    "fbb9a6092b5c5d95",
})

FOLD = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " ", "…": "..."})
QRE = re.compile(r'"([^"\n]{2,}?)"|“([^”\n]{2,}?)”|(?<![A-Za-z])\'([^\'\n]{2,}?)\'(?![A-Za-z])')
HEADING = re.compile(r"^### .*\(`([a-z0-9]+)`\) --")


def norm(s: str) -> str:
    """The checkers' fold: typographic quotes and dashes, then whitespace collapsed."""
    return re.sub(r"\s+", " ", s.translate(FOLD).replace("|", " | ")).strip()


def h16(s: str) -> str:
    return hashlib.sha256(norm(s).encode("utf-8")).hexdigest()[:16]


def lf_bytes(p: Path) -> bytes:
    return p.read_bytes().replace(b"\r\n", b"\n")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def note_text() -> str:
    return lf_bytes(NOTE).decode("utf-8")


def appendix_sections(text: str) -> dict[str, str]:
    """Each firm's Appendix A section, keyed by slug, in order: from its heading line to the next heading or the end."""
    app = text.split("\n## Appendix A.", 1)[1].split("\n")
    starts = [(i, m.group(1)) for i, line in enumerate(app) if (m := HEADING.match(line))]
    out = {}
    for n, (i, slug) in enumerate(starts):
        j = starts[n + 1][0] if n + 1 < len(starts) else len(app)
        out[slug] = "\n".join(app[i:j])
    return out


def quoted_fragments(line: str) -> list[str]:
    """Every quoted fragment on one line, and each part of it between ellipses."""
    out = []
    for m in QRE.finditer(line):
        fr = next(g for g in m.groups() if g)
        out.append(fr)
        parts = [p.strip() for p in re.split(r"\.\.\.|…", fr)]
        if len(parts) > 1:
            out.extend(p for p in parts if p)
    return out


def stub(slug: str) -> dict:
    return json.loads((FIRMS / f"{slug}.json").read_text(encoding="utf-8"))


def clause_segments(struck: str) -> list[str]:
    """The quoted clause in a stub's `struck` text: from its first double quote to its last, split at ' ... '."""
    rest = struck[len(PREFIX):]
    a, b = rest.index('"'), rest.rindex('"')
    assert b > a + 1, struck
    return [s.strip() for s in rest[a + 1:b].split(" ... ") if s.strip()]


# ---- the stubs -----------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("slug", sorted(STRUCK))
def test_stub_has_the_briefs_shape(slug):
    d = stub(slug)
    assert set(d) == {"firm", "struck", "date"}, slug
    assert d["firm"] == STRUCK[slug][0]
    assert d["date"] == DATE
    assert d["struck"].startswith(PREFIX)
    assert clause_segments(d["struck"])


@pytest.mark.parametrize("slug", sorted(STRUCK))
def test_stub_quotes_the_clause_as_recorded(slug):
    segs = clause_segments(stub(slug)["struck"])
    if slug in Q26:
        entries = {e["key"]: e for e in yaml.safe_load(RULES.read_text(encoding="utf-8"))["rules"]}
        recorded = norm(entries[Q26[slug]]["quote"])
        for s in segs:
            assert norm(s) in recorded, (slug, s)
    else:
        assert {h16(s) for s in segs} == E009_CLAUSE_SEGMENTS[slug], slug


def test_firm_files_are_the_same_twenty_two():
    assert sorted(p.stem for p in FIRMS.glob("*.json")) == sorted(ORDER)


@pytest.mark.parametrize("slug", KEPT)
def test_kept_firm_file_untouched(slug):
    assert sha(lf_bytes(FIRMS / f"{slug}.json")) == KEPT_FILES[slug], slug


# ---- the note ------------------------------------------------------------------------------------------------------

def test_appendix_keeps_its_firms_and_order():
    assert list(appendix_sections(note_text())) == ORDER


@pytest.mark.parametrize("slug", KEPT)
def test_kept_appendix_section_untouched(slug):
    assert sha(appendix_sections(note_text())[slug].encode("utf-8")) == KEPT_SECTIONS[slug], slug


@pytest.mark.parametrize("slug", sorted(STRUCK))
def test_struck_appendix_section_is_one_line(slug):
    firm, verdict = STRUCK[slug]
    lines = appendix_sections(note_text())[slug].rstrip("\n").split("\n")
    assert len(lines) == 5 and lines[1] == "" and lines[3] == "", lines
    heading, verdict_line, struck_line = lines[0], lines[2], lines[4]
    assert heading == f"### {firm} (`{slug}`) -- {verdict}"
    assert verdict_line.startswith(f"Verdict: **{verdict}** -- ")
    assert not quoted_fragments(verdict_line), verdict_line       # the screen's verdict, without quotes
    assert struck_line.startswith(STRUCK_LINE)
    for s in clause_segments(stub(slug)["struck"]):
        assert norm(s) in norm(struck_line), (slug, s)
    for line in (verdict_line, struck_line):
        assert "http" not in line and not re.search(r"\[P\d+\]", line), line


@pytest.mark.parametrize("slug", sorted(STRUCK))
def test_body_names_each_clause_with_e020(slug):
    body = norm(note_text().split("\n## Appendix A.", 1)[0])
    for s in clause_segments(stub(slug)["struck"]):
        i = body.find(norm(s))
        assert i >= 0, (slug, s)
        assert "E-020" in body[i:i + 1500], slug


def test_removed_body_quotes_are_gone():
    found = []
    for n, line in enumerate(note_text().split("\n"), 1):
        for fr in quoted_fragments(line):
            if h16(fr) in REMOVED_BODY_QUOTES:
                found.append((n, h16(fr)))
    assert not found, found


def test_removed_body_quotes_pinned():
    assert len(REMOVED_BODY_QUOTES) >= 20


# ---- the note's checkers skip a struck firm ------------------------------------------------------------------------

def _run(script: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", str(TOOLS / script), *map(str, args)], capture_output=True,
                          text=True, encoding="utf-8", timeout=120)


def _synthetic_root(tmp_path: Path) -> Path:
    """One readable firm `kept` (one quote, its saved page, its fetch index) and one struck firm `gone` (a stub)."""
    (tmp_path / "firms").mkdir()
    (tmp_path / "raw" / "kept").mkdir(parents=True)
    (tmp_path / "raw" / "kept" / "home.txt").write_text("The target is $3,000. Nothing else.", encoding="utf-8")
    (tmp_path / "raw" / "kept" / "INDEX.tsv").write_text(
        "2026-11-15T00:00:00Z\t200\thome\thttps://kept.example/\n", encoding="utf-8")
    kept = {"firm": "Kept Firm", "slug": "kept", "official_domains": ["kept.example"],
            "terms": {"eval_profit_target": {"value": 3000, "status": "verified", "quotes": [
                {"text": "The target is $3,000.", "file": "raw/kept/home.txt", "url": "https://kept.example/"}]}}}
    (tmp_path / "firms" / "kept.json").write_text(json.dumps(kept), encoding="utf-8")
    (tmp_path / "firms" / "gone.json").write_text(json.dumps(
        {"firm": "Gone Firm", "struck": PREFIX + 'Terms: "no robots"', "date": DATE}), encoding="utf-8")
    return tmp_path


def _note(tmp_path: Path, struck_body: str) -> Path:
    p = tmp_path / "note.md"
    p.write_text("# Note\n\n## Appendix A. Terms\n\n### Kept Firm (`kept`) -- PASS\n\n"
                 '  - "The target is $3,000." [P1]\n\n### Gone Firm (`gone`) -- PASS\n\n' + struck_body,
                 encoding="utf-8")
    return p


def test_check_quotes_skips_a_struck_firm(tmp_path):
    r = _run("check_quotes.py", _synthetic_root(tmp_path))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "kept: 1 quotes found verbatim, 0 not found" in r.stdout
    assert "gone: struck (E-020), skipped" in r.stdout


def test_check_provenance_skips_a_struck_firm(tmp_path):
    r = _run("check_provenance.py", _synthetic_root(tmp_path))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "kept: domains=['kept.example'] quotes=1 provenance problems=0" in r.stdout
    assert "gone: struck (E-020), skipped" in r.stdout


def test_check_note_skips_a_struck_section(tmp_path):
    root = _synthetic_root(tmp_path)
    r = _run("check_note.py", root, _note(tmp_path, "Verdict: **PASS** -- x\n\n" + STRUCK_LINE + 'Terms: "no robots"\n'))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "note quotes found verbatim: 1; not found: 0" in r.stdout
    assert "struck sections skipped: 1 (gone)" in r.stdout


def test_check_note_refuses_a_quote_under_a_struck_heading(tmp_path):
    root = _synthetic_root(tmp_path)
    r = _run("check_note.py", root, _note(tmp_path, '  - "The target is $3,000." [P1]\n'))
    assert r.returncode == 1, r.stdout + r.stderr
    assert "QUOTE UNDER STRUCK HEADING gone" in r.stdout
