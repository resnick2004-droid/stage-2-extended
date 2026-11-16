"""Machine-checkable validation of a pre-registration file.

The **prereg-gatekeeper** agent decides whether a pre-registration is complete. An agent is a
prompt, so its judgement cannot be pinned by a test; this module is the part that can be. The
agent is required to run `validate_prereg` first and to refuse whatever it refuses, so the
mandatory fields have a deterministic gate behind the judgement rather than only in front of it.

The gate reads the **Machine-checked fields** table at the top of `prereg/TEMPLATE.md`. That
table exists so the check cannot be defeated by prose: a section can be waffled, a table row
either carries a value or it does not.

What it enforces, beyond the original five (data period, fixed rules, metrics, pass/fail
criteria, seed):

* **`k` declared in advance** -- how many variants will be tried. Declared before the run, or
  the multiplicity plan is retrospective and therefore not a plan.
* **A development period and a held-out confirmation period**, or, if there is no held-out
  period, the **Bonferroni level** that will be applied instead.
* **The assumed per-trade sd and its source.** Stage one's 1.23-1.79 is the frictionless binary
  floor and may not be borrowed silently.
* **The risk denominator.** `e` is P&L over dollars risked; whether that is *intended* or
  *realised* risk changes the number, so it is stated.
* **The primary metric**, which for a campaign or a protocol comparison is growth on the required bankroll
  (`pf_growth_on_base_p50` on `pf_required_p90`, D-312, D-457).
* **The model card (D-155)** of the model under test, which must pass
  `propedge.research.model_card.validate_card`; a comparison that tests no model says `none: <reason>`.
* **From P-05, the required and available trade counts (D-192).** The required count is read from L5's
  planted-effect power curve at the registration's R, effect size and bootstrap length
  (`propedge.research.power`); the validator reads it again and refuses a stated count that differs. `assumed_sd`
  carries the required count only as a labelled fallback, where the curve does not apply.
* **From P-05, the trial count N (D-189)** the verdict's lower bound is widened by, as the ledger
  (`prereg/models.yaml`, `propedge.research.ledger`) counts it for this registration's markets, window and bars.

P-01 to P-04 were registered before D-189 and D-192 (`LEGACY`) and are not held to those two.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

#: Values that look filled in but are not.
_PLACEHOLDER = re.compile(
    r"^\s*(|-+|—+|n/?a|tbd|todo|\?+|\.\.\.|to be (decided|chosen|determined|confirmed)"
    r"|<[^>]*>|\(.*\))\s*$",
    re.IGNORECASE,
)

#: Values of `confirmation_period` that mean "there isn't one".
_NO_CONFIRMATION = re.compile(r"^\s*(none|no|n/?a|not applicable)\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class RequiredField:
    key: str
    label: str
    why: str
    numeric: bool = False


#: Always required.
REQUIRED_FIELDS: tuple[RequiredField, ...] = (
    RequiredField("data_period", "data period",
                  "the dates are fixed now, or the test is not out of sample"),
    RequiredField("seed", "seed",
                  "an integer written down now; a seed chosen after a result is a variant"),
    RequiredField("k", "k (variants declared in advance)",
                  "how many variants will be tried, declared before the run", numeric=True),
    RequiredField("development_period", "development period",
                  "the period selection is allowed to use"),
    RequiredField("confirmation_period", "held-out confirmation period",
                  "the period never used in development, tested once; or 'none'"),
    RequiredField("confirmation_tests_on_this_market",
                  "confirmation tests already run on this market's window",
                  "counted from prereg/REGISTRY.md; the window is a shared resource capped at "
                  "three tests per market (D-107)", numeric=True),
    RequiredField("assumed_sd", "assumed per-trade sd (units of risk)",
                  "the sd the sample-size claim rests on", numeric=True),
    RequiredField("assumed_sd_source", "source of the assumed sd",
                  "measured from a pilot log, or stated as an assumption -- stage one's "
                  "frictionless binary floor may not be borrowed"),
    RequiredField("risk_denominator", "risk denominator",
                  "intended or realised dollar risk; it changes e"),
    RequiredField("primary_metric", "primary metric",
                  "growth on the required bankroll (pf_growth_on_base_p50 on pf_required_p90) for a campaign or "
                  "a protocol comparison (D-312, D-457)"),
    RequiredField("model_card", "model card (D-155)",
                  "the card of the model under test, which must pass propedge.research.model_card.validate_card; "
                  "or 'none: <reason>' for a comparison that tests no model"),
)

#: A `model_card` value that says this pre-registration tests no model.
_NO_CARD = re.compile(r"^\s*none\s*[:\-—]\s*\S", re.IGNORECASE)

#: Required only when there is no held-out confirmation period.
BONFERRONI_FIELD = RequiredField(
    "bonferroni_alpha", "Bonferroni one-sided level (alpha/k)",
    "with no held-out period the level must be split across the k variants", numeric=True,
)

#: Registered before D-189 and D-192; held to neither.
LEGACY = ("P-01", "P-02", "P-03", "P-04")

#: D-192, from P-05: the power reading behind the sample-size claim.
POWER_FIELDS: tuple[RequiredField, ...] = (
    RequiredField("power_rr", "R the power is read at",
                  "the Combine's R, where the model is ranked (D-201)", numeric=True),
    RequiredField("power_effect", "effect size e at that R",
                  "the edge the test must be able to find; the card's edge_assumed", numeric=True),
    RequiredField("boot_len", "bootstrap length in days",
                  "the power curve is read at the registration's own bootstrap length", numeric=True),
    RequiredField("required_trades_source", "source of the required count",
                  "`l5_power_curve`, or `assumed_sd fallback: <why the curve does not apply>` (D-192)"),
    RequiredField("required_trades", "required trade count",
                  "trades at which the bound clears zero with the target power, read from the curve"),
    RequiredField("available_trades", "available trade count",
                  "the trades the registered period will supply, estimated before the run", numeric=True),
)

#: D-189, from P-05: the trial count the lower bound is widened by.
LEDGER_FIELD = RequiredField(
    "ledger_n", "trial count N (D-189)",
    "the registration's k plus the ledger rows that read its markets and window at its bar resolution and sat in "
    "its selection pool, counted by propedge.research.ledger", numeric=True,
)
_FALLBACK = re.compile(r"^\s*assumed_sd\s+fallback\s*:\s*\S", re.IGNORECASE)
_ID = re.compile(r"^\|\s*\*{0,2}id\*{0,2}\s*\|\s*(P-\d+)\b", re.IGNORECASE | re.MULTILINE)

#: Prose sections that must be present and non-trivial.
REQUIRED_SECTIONS: tuple[tuple[str, str], ...] = (
    ("rules fixed before the run", "every parameter must carry a value"),
    ("metrics", "what will be computed, and from what"),
    ("pass / fail criteria", "the decision rule, stated before the numbers exist"),
)


@dataclass
class PreregValidation:
    """The result of validating one pre-registration."""

    path: str | None
    fields: dict[str, str] = field(default_factory=dict)
    missing_fields: list[str] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (self.missing_fields or self.missing_sections or self.problems)

    def report(self) -> str:
        if self.ok:
            lines = ["pre-registration is complete: every machine-checked field is present."]
            lines += [f"  note: {n}" for n in self.notes]
            return "\n".join(lines)

        lines = ["REFUSED -- this pre-registration is incomplete."]
        if self.missing_fields:
            lines.append("  missing or placeholder fields:")
            for k in self.missing_fields:
                f = FIELDS_BY_KEY.get(k)
                lines.append(f"    - {f.label if f else k}: {f.why if f else 'required'}")
        if self.missing_sections:
            lines.append("  missing or empty sections:")
            for s in self.missing_sections:
                lines.append(f"    - {s}")
        for p in self.problems:
            lines.append(f"  problem: {p}")
        for n in self.notes:
            lines.append(f"  note: {n}")
        return "\n".join(lines)


FIELDS_BY_KEY: dict[str, RequiredField] = {
    f.key: f for f in (*REQUIRED_FIELDS, BONFERRONI_FIELD, *POWER_FIELDS, LEDGER_FIELD)
}


def registration_id(text: str) -> str | None:
    """The P-id in the header table, or None while it is still `P-XX`."""
    m = _ID.search(text)
    return m.group(1).upper() if m else None


def _power_problems(fields: dict[str, str], v: "PreregValidation", curve_path: Path | None) -> None:
    """D-192: the stated required count is the power curve's reading (or a labelled `assumed_sd` fallback)."""
    from propedge.research import power

    num = lambda k: float(re.search(r"-?\d+(?:\.\d+)?", fields[k].replace(",", "")).group(0))   # noqa: E731
    source = re.sub(r"[*`]", "", fields["required_trades_source"]).strip()     # keeps the underscores in the names
    if _FALLBACK.match(source):
        v.notes.append("D-192: the required count rests on assumed_sd, the labelled fallback: " + source)
        return
    if source.lower() != "l5_power_curve":
        v.problems.append("required_trades_source must be `l5_power_curve` or `assumed_sd fallback: <why>` (D-192), "
                          f"got {fields['required_trades_source']!r}")
        return
    curve, params = power.load_curve(curve_path)
    if int(num("boot_len")) != int(params.get("boot_len", -1)):
        v.problems.append(f"D-192: the power curve is at a bootstrap length of {params.get('boot_len')} days, the "
                          f"registration's is {fields['boot_len']}: the curve does not apply; use the labelled "
                          "assumed_sd fallback or a curve at this length")
        return
    try:
        reading = power.required_trades(curve, num("power_rr"), num("power_effect"))
    except ValueError as exc:
        v.problems.append(f"D-192: {exc}")
        return
    stated = _strip_emphasis(fields["required_trades"])
    need = reading["required"]
    if need is None:
        above = re.match(r"^\s*(>|above|more than)\s*([\d,]+)", stated, re.IGNORECASE)
        if not above or int(above.group(2).replace(",", "")) < reading["max_trades"]:
            v.problems.append(f"D-192: the power curve does not reach power {reading['target']:g} by its largest "
                              f"count, {reading['max_trades']}; state required_trades as '> {reading['max_trades']}'")
            return
    else:
        m = re.search(r"\d[\d,]*", stated)
        if not m or int(m.group(0).replace(",", "")) != need:
            v.problems.append(f"D-192: required_trades {fields['required_trades']!r} is not the curve's reading: {need} "
                              f"trades for power {reading['target']:g} at R {reading['R']:g}, e {reading['e_read']:g} "
                              f"({power.CURVE_FILE.name})")
            return
    avail = num("available_trades")
    at = power.power_at(curve, num("power_rr"), num("power_effect"), avail)
    v.notes.append(f"D-192: required {need if need is not None else '> ' + str(reading['max_trades'])} trades at power "
                   f"{reading['target']:g} (R {reading['R']:g}, e read at {reading['e_read']:g}); available "
                   f"{avail:g}" + (f", power there {at:.2f}" if at is not None else ", outside the curve's counts"))
    if need is None or avail < need:
        v.notes.append("D-192: the available trades are below the required count -- the test is underpowered, and a "
                       "fail on it says little")


_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _ledger_problems(fields: dict[str, str], v: "PreregValidation", ledger_path: Path | None) -> None:
    """D-189: the stated N is the ledger's count for the card's model, markets and the development period."""
    from propedge import REPO_ROOT
    from propedge.research import ledger as lg

    stated = int(float(re.search(r"\d+(?:\.\d+)?", fields["ledger_n"]).group(0)))
    k_m = re.search(r"\d+", fields.get("k", ""))
    card = (fields.get("model_card") or "").strip().strip("`*").strip()
    if not k_m:
        return                                              # k's own check reports it
    k = int(k_m.group(0))
    if not card or _is_placeholder(card) or _NO_CARD.match(card):
        if stated != k:
            v.problems.append(f"D-189: a registration that tests no model has no selection pool, so N is its k ({k}); "
                              f"ledger_n says {stated}")
        return
    from propedge.research.model_card import validate_card

    card_path = REPO_ROOT / card
    if not card_path.is_file():
        return                                              # the card's own check reports it
    cf = validate_card(card_path).fields
    model = (cf.get("model") or "").strip().strip("`")
    markets = [m.strip() for m in re.sub(r"\(.*?\)", "", cf.get("markets", "")).split(",") if m.strip()]
    dates = _DATE.findall(fields.get("development_period", ""))
    if len(dates) < 2:
        v.problems.append("D-189: development_period needs its first and last dates (YYYY-MM-DD) to count N")
        return
    try:
        led = lg.load_ledger(ledger_path)
        got = lg.count_n(led, model=model, k=k, markets=markets, window=(dates[0], dates[-1]))
    except (KeyError, lg.LedgerError) as exc:
        v.problems.append(f"D-189: {exc}")
        return
    if got["N"] != stated:
        v.problems.append(f"D-189: ledger_n {stated} is not the ledger's count, {got['N']} (k {k} plus "
                          + ", ".join(f"{rid} {t}" for rid, t, _ in got["rows"]) + f"; pool {got['pool']})")
    else:
        v.notes.append(f"D-189: N = {got['N']} (k {k} plus {len(got['rows'])} ledger rows in pool {got['pool']}); "
                       f"the verdict's bound is at one-sided 0.05/{got['N']}")


def _parse_fields(text: str) -> dict[str, str]:
    """Read `| key | value |` rows from the Machine-checked fields table.

    Accepts a backticked key (`` `k` ``) so the table renders readably, and ignores the header
    and separator rows.
    """
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        key = cells[0].strip().strip("`").strip()
        if not re.fullmatch(r"[a-z_][a-z0-9_]*", key):
            continue
        if key == "key":       # the table's own header row
            continue
        out[key] = cells[1].strip()
    return out


def _strip_emphasis(value: str) -> str:
    """Remove markdown emphasis and code ticks, for placeholder detection only.

    The template writes its placeholders as `*(explanation)*` so they render as italic hints.
    Without stripping the emphasis those read as filled-in values and the template itself would
    validate -- which `tests/test_prereg_validation.py` checks it does not.
    """
    return re.sub(r"[*_`]", "", value or "").strip()


def _is_placeholder(value: str) -> bool:
    return bool(_PLACEHOLDER.match(_strip_emphasis(value)))


def _section_bodies(text: str) -> dict[str, str]:
    """Map lower-cased heading text (numbering stripped) to the body beneath it."""
    out: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^#{2,}\s+(.*?)\s*$", line)
        if m:
            if current is not None:
                out[current] = "\n".join(buf)
            heading = re.sub(r"^\d+[a-z]?[.)]?\s*", "", m.group(1)).strip().lower()
            current = heading
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        out[current] = "\n".join(buf)
    return out


def validate_prereg(source: str | Path, *, curve_path: Path | None = None,
                    ledger_path: Path | None = None) -> PreregValidation:
    """Validate a pre-registration. `source` is a path or the file's text.

    Returns a `PreregValidation`; never raises on incompleteness -- incompleteness is the
    normal finding and the caller reports it. `curve_path` and `ledger_path` default to the
    repository's power curve (D-192) and ledger (D-189).
    """
    path: str | None = None
    if isinstance(source, Path) or (
        isinstance(source, str) and "\n" not in source and len(source) < 4096
        and Path(source).suffix == ".md"
    ):
        p = Path(source)
        if not p.is_file():
            raise FileNotFoundError(f"pre-registration not found: {p}")
        path = str(p)
        text = p.read_text(encoding="utf-8")
    else:
        text = str(source)

    v = PreregValidation(path=path)
    v.fields = _parse_fields(text)

    for f in REQUIRED_FIELDS:
        value = v.fields.get(f.key)
        if value is None or _is_placeholder(value):
            v.missing_fields.append(f.key)
            continue
        if f.numeric and not re.search(r"\d", value):
            v.problems.append(
                f"{f.label} must be a number, got {value!r}"
            )

    # Conditional: no held-out confirmation period -> a Bonferroni level is required.
    conf = v.fields.get("confirmation_period", "")
    if conf and not _is_placeholder(conf) and _NO_CONFIRMATION.match(conf):
        bval = v.fields.get(BONFERRONI_FIELD.key)
        if bval is None or _is_placeholder(bval):
            v.missing_fields.append(BONFERRONI_FIELD.key)
        elif not re.search(r"\d", bval):
            v.problems.append(
                f"{BONFERRONI_FIELD.label} must be a number, got {bval!r}"
            )
        k_raw = v.fields.get("k", "")
        k_match = re.search(r"\d+", k_raw or "")
        if k_match and int(k_match.group(0)) > 1:
            v.notes.append(
                f"no held-out confirmation period and k = {k_match.group(0)}: the verdict must "
                "use the Bonferroni-adjusted bound, and an unadjusted bound on the selected "
                "variant is exploratory"
            )

    # D-189 and D-192, from P-05: the power reading and the trial count.
    pid = registration_id(text)
    if pid in LEGACY:
        v.notes.append(f"{pid} was registered before D-189 and D-192: no power reading or trial count required")
    else:
        missing_new = []
        for f in (*POWER_FIELDS, LEDGER_FIELD):
            value = v.fields.get(f.key)
            if value is None or _is_placeholder(value):
                v.missing_fields.append(f.key)
                missing_new.append(f.key)
            elif f.numeric and not re.search(r"\d", value):
                v.problems.append(f"{f.label} must be a number, got {value!r}")
                missing_new.append(f.key)
        if not any(k in missing_new for k in (f.key for f in POWER_FIELDS)):
            _power_problems(v.fields, v, curve_path)
        if LEDGER_FIELD.key not in missing_new:
            _ledger_problems(v.fields, v, ledger_path)

    # D-155: a model's pre-registration names a model card that passes its own check.
    card = (v.fields.get("model_card") or "").strip().strip("`*").strip()     # a path keeps its underscores
    if card and not _is_placeholder(card) and not _NO_CARD.match(card):
        from propedge import REPO_ROOT
        from propedge.research.model_card import validate_card

        card_path = REPO_ROOT / card.strip()
        if not card_path.is_file():
            v.problems.append(f"model card {card!r} not found (D-155)")
        else:
            cv = validate_card(card_path, for_prereg=True)
            if not cv.ok:
                v.problems.append(f"model card {card!r} does not pass its check (D-155):\n" + cv.report())

    sections = _section_bodies(text)
    for name, why in REQUIRED_SECTIONS:
        body = None
        for heading, text_body in sections.items():
            if name in heading:
                body = text_body
                break
        if body is None:
            v.missing_sections.append(f"{name} ({why})")
        elif len(re.sub(r"[\s*_>|\-]", "", body)) < 40:
            v.missing_sections.append(f"{name} -- present but effectively empty ({why})")

    # Written after a run? A pre-registration that cites results is not one.
    if re.search(r"\bresults?/[A-Za-z0-9_\-]+\.csv\b", text) and "Outcome" not in text:
        v.problems.append(
            "the file references a result CSV; a pre-registration written after a run is "
            "exploratory and must be reported as such, not registered"
        )

    return v
