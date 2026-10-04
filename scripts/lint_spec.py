#!/usr/bin/env python3
"""
lint_spec.py — checks a spliteasy spec file against the project constitution.

Usage:
    python scripts/lint_spec.py specs/auth-001.md [specs/group-001.md ...]
    python scripts/lint_spec.py specs/*.md

Exits 1 if any spec fails any check (for CI); 0 if all pass.

This script implements the *Test:* lines from docs/constitution.md as
literally as possible. Each check function below is labelled with the
constitution section it enforces, so the two stay easy to keep in sync
by hand. It does not implement:
  - Section 2's "was this change genuinely breaking/additive/patch"
    judgment call — that's a human review step, not a lint check.
  - Section 6's "project actually runs on this stack" check — that's
    a CI job of its own (pytest / dependency check), not spec-lint.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Config: shared constants pulled from the constitution / glossary
# ---------------------------------------------------------------------------

VALID_STATUSES = {
    "draft", "in_review", "active", "deprecated",
    "superseded", "archived", "abandoned",
}
STRICT_STATUSES = {"in_review", "active"}
FROZEN_STATUSES = {"deprecated", "superseded", "archived"}

REQUIRED_SECTIONS = [
    "User Story",
    "Scope",
    "Dependencies",
    "Business Rules",
    "Scenarios",
    "Non-Functional Requirements",
    "Traceability Table",
    "Open Questions",
    "Changelog",
]

SCENARIO_GROUPS = [
    "Happy path",
    "Failure paths",
    "Boundary conditions",
    "Verification scenarios",
]

BANNED_WORDS = [
    "fast", "performant", "real-time", "instantaneous",
    "scalable", "robust", "heavy load",
    "user-friendly", "intuitive", "seamless", "modern",
    "usually", "generally", "often", "sometimes", "as needed",
    "etc.", "and/or",
]

# Glossary of registered module names. Extend this list (Constitution
# Section 12) whenever a new module spec is added.
KNOWN_MODULES = {"auth", "lockout", "group", "expense", "settlement",
                  "notification", "late-fee"}

BUSINESS_GOALS_FILE = Path("docs/business-goals.md")

ID_RE = r"[A-Za-z][A-Za-z0-9-]*"  # module-name token, e.g. "auth", "late-fee"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
HEADING_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)
REQ_ID_RE = re.compile(r"\bSE-(" + ID_RE + r")-(\d{3})-(BR|NFR)-(\d{3})\b")
BARE_REQ_RE = re.compile(r"\b(BR|NFR)-(\d{3})\b")
DECLARED_REQ_RE = re.compile(r"\*\*(BR|NFR)-(\d{3})\*\*:")
SCN_DECL_RE = re.compile(
    r"\*\*SCN-(\d{3})\*\*\s*\(Traces to:\s*(BR|NFR)-(\d{3})\)"
)
BG_REF_RE = re.compile(r"\bBG-(\d{3})\b")


def declared_requirements(sections: dict) -> set[str]:
    """Requirements actually *declared* in this spec: a bold
    '**BR-001**:' or '**NFR-001**:' line inside the Business Rules or
    Non-Functional Requirements sections. Deliberately narrower than
    'BR-### appears anywhere in the file', because Dependencies and
    other prose may legitimately reference another spec's requirement
    (e.g. "SE-auth-001's BR-005 enforces the lock this spec relies
    on") without that being a local declaration.
    """
    text = (sections.get("Business Rules", "")
            + sections.get("Non-Functional Requirements", ""))
    return {f"{kind}-{num}" for kind, num in DECLARED_REQ_RE.findall(text)}


@dataclass
class Result:
    path: Path
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors


def load_business_goals() -> set[str]:
    if not BUSINESS_GOALS_FILE.exists():
        return set()
    text = BUSINESS_GOALS_FILE.read_text()
    return set(re.findall(r"\bBG-(\d{3})\b", text))


def parse_frontmatter(text: str, r: Result) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        r.err("Missing or malformed YAML frontmatter (must start the file "
              "with a '---' block).")
        return {}
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        r.err(f"Frontmatter is not valid YAML: {e}")
        return {}
    return data


# ---------------------------------------------------------------------------
# Section 4 — frontmatter fields, id format, business_goals
# ---------------------------------------------------------------------------

def check_frontmatter(fm: dict, r: Result, known_goals: set[str]) -> tuple[str | None, str]:
    """Returns (module_name, status) for use by later checks."""
    required_fields = ["id", "version", "status", "depends_on", "business_goals"]
    for field_name in required_fields:
        if field_name not in fm:
            r.err(f"Frontmatter missing required field: '{field_name}' "
                  f"(Constitution §4).")

    spec_id = fm.get("id", "")
    module_match = re.fullmatch(r"SE-(" + ID_RE + r")-(\d{3})", str(spec_id))
    module_name = None
    if not spec_id:
        pass  # already reported above
    elif not module_match:
        r.err(f"Frontmatter 'id' = '{spec_id}' does not match "
              f"SE-<module-name>-### (Constitution §4).")
    else:
        module_name = module_match.group(1)
        if module_name not in KNOWN_MODULES:
            r.err(f"Module '{module_name}' is not registered in the "
                  f"glossary (Constitution §12). Add it before merging.")

    status = str(fm.get("status", ""))
    if status and status not in VALID_STATUSES:
        r.err(f"Frontmatter 'status' = '{status}' is not one of "
              f"{sorted(VALID_STATUSES)} (Constitution §4).")

    goals = fm.get("business_goals", [])
    if isinstance(goals, str):
        r.err("Frontmatter 'business_goals' must be a YAML list, e.g. "
              "[BG-001], not a bare string (Constitution §4).")
        goals = [goals]
    if not goals:
        r.err("Frontmatter 'business_goals' must list at least one "
              "BG-### (Constitution §4).")
    for g in goals:
        gm = re.fullmatch(r"BG-(\d{3})", str(g))
        if not gm:
            r.err(f"business_goals entry '{g}' does not match BG-### "
                  f"(Constitution §4).")
        elif known_goals and gm.group(1) not in known_goals:
            r.err(f"business_goals entry '{g}' is not defined in "
                  f"{BUSINESS_GOALS_FILE} (Constitution §7).")

    return module_name, status


# ---------------------------------------------------------------------------
# Section 7 — nine sections present, in order; Changelog matches version
# ---------------------------------------------------------------------------

def check_sections(text: str, fm: dict, r: Result) -> dict[str, str]:
    headings = HEADING_RE.findall(text)
    # Only compare the top-level required ones, in order, allowing extra
    # non-required ## headings (e.g. none expected today, but be lenient).
    present_required = [h for h in headings if h in REQUIRED_SECTIONS]
    if present_required != REQUIRED_SECTIONS:
        missing = [s for s in REQUIRED_SECTIONS if s not in headings]
        out_of_order = present_required != REQUIRED_SECTIONS and not missing
        if missing:
            r.err(f"Missing required section(s): {missing} (Constitution §7).")
        if out_of_order:
            r.err(f"Sections are present but out of order: got "
                  f"{present_required}, expected {REQUIRED_SECTIONS} "
                  f"(Constitution §7).")

    # Split into per-section text blocks for later checks.
    sections: dict[str, str] = {}
    matches = list(HEADING_RE.finditer(text))
    for i, m in enumerate(matches):
        name = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[name] = text[start:end]

    # Changelog must have an entry for the current version.
    version = str(fm.get("version", ""))
    changelog = sections.get("Changelog", "")
    if version and version not in changelog:
        r.err(f"No Changelog entry found for current version '{version}' "
              f"(Constitution §7).")

    return sections


# ---------------------------------------------------------------------------
# Section 1 — every requirement <-> scenario, bidirectional, 1:1 on the
# scenario side
# ---------------------------------------------------------------------------

def check_requirement_scenario_graph(text: str, sections: dict, module_name: str | None,
                                      status: str, r: Result) -> None:
    strict = status in STRICT_STATUSES

    # Only requirements actually declared in THIS spec's own Business
    # Rules / NFR sections — not every BR-###/NFR-### substring in the
    # whole document (Dependencies may legitimately reference another
    # spec's requirement by number).
    bare_reqs = declared_requirements(sections)

    # All scenario declarations with their claimed parent.
    scn_section = sections.get("Scenarios", "")
    decls = SCN_DECL_RE.findall(scn_section)  # (scn_num, kind, req_num)
    scn_ids = [f"SCN-{n}" for n, _, _ in decls]

    # Every SCN unique within spec.
    dupes = {s for s in scn_ids if scn_ids.count(s) > 1}
    if dupes:
        r.err(f"Duplicate scenario ID(s) within this spec: {sorted(dupes)} "
              f"(Constitution §1).")

    # Every SCN's parent requirement must exist in this spec.
    for num, kind, req_num in decls:
        parent = f"{kind}-{req_num}"
        if parent not in bare_reqs:
            r.err(f"SCN-{num} declares parent {parent}, but {parent} is "
                  f"not defined anywhere in this spec (Constitution §1).")

    # Every requirement must have >=1 scenario (strict statuses only).
    reqs_with_scn = {f"{kind}-{req_num}" for _, kind, req_num in decls}
    if strict:
        for req in sorted(bare_reqs):
            if req not in reqs_with_scn:
                r.err(f"{req} has no linked SCN-### (Constitution §1, "
                      f"required for status='{status}').")


# ---------------------------------------------------------------------------
# Section 8 — four scenario groups present
# ---------------------------------------------------------------------------

def check_scenario_groups(sections: dict, status: str, r: Result) -> None:
    scn_text = sections.get("Scenarios", "")
    strict = status in STRICT_STATUSES
    if status in {"draft", "abandoned"}:
        if not scn_text.strip():
            r.warn("Scenarios section is empty (allowed for draft/abandoned).")
        return

    sub_re = re.compile(r"^###\s+(.+)$", re.MULTILINE)
    found_groups = sub_re.findall(scn_text)
    for group in SCENARIO_GROUPS:
        if group not in found_groups:
            r.err(f"Scenarios section missing subgroup '### {group}' "
                  f"(Constitution §8).")
            continue
        if strict:
            # crude check: does this group's slice contain a SCN-### or
            # an explicit not-applicable statement?
            idx = found_groups.index(group)
            starts = [m.start() for m in sub_re.finditer(scn_text)]
            start = starts[idx]
            end = starts[idx + 1] if idx + 1 < len(starts) else len(scn_text)
            block = scn_text[start:end]
            has_scn = bool(re.search(r"SCN-\d{3}", block))
            has_na = bool(re.search(r"none|not applicable", block, re.IGNORECASE))
            if not (has_scn or has_na):
                r.err(f"'{group}' has no SCN-### and no explicit "
                      f"not-applicable statement (Constitution §8).")


# ---------------------------------------------------------------------------
# Section 9 — NFRs are measurable, threshold stated once
# ---------------------------------------------------------------------------

def check_nfrs(sections: dict, text: str, r: Result) -> None:
    nfr_text = sections.get("Non-Functional Requirements", "")
    nfr_ids = re.findall(r"\*\*NFR-(\d{3})\*\*", nfr_text)
    numeric_re = re.compile(
        r"\d+\s*(ms|s|%|seconds?|requests?|hours?|minutes?|hrs?|days?)",
        re.IGNORECASE,
    )
    for num in nfr_ids:
        # crude: find the NFR's own line and check it has a number+unit
        m = re.search(rf"\*\*NFR-{num}\*\*.*", nfr_text)
        line = m.group(0) if m else ""
        if not numeric_re.search(line):
            r.warn(f"NFR-{num} may lack a numeric threshold + unit "
                   f"(Constitution §9) — verify manually.")


# ---------------------------------------------------------------------------
# Section 10 — traceability table completeness + consistency with inline tags
# ---------------------------------------------------------------------------

def check_traceability_table(sections: dict, text: str, module_name: str | None, r: Result) -> None:
    table = sections.get("Traceability Table", "")
    rows = [
        line for line in table.splitlines()
        if line.strip().startswith("|") and "---" not in line
        and "Requirement ID" not in line
    ]
    parsed = []
    for line in rows:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            r.err(f"Traceability Table row has fewer than 5 columns: '{line}'")
            continue
        req_id, desc, bg, scns, tests = cells[:5]
        parsed.append((req_id, desc, bg, scns, tests))

        if not re.search(r"\bBG-\d{3}\b", bg):
            r.err(f"Traceability row for {req_id} has no BG-### in "
                  f"Business Goal column (Constitution §10).")
        if "None" not in scns and not re.search(r"SCN-\d{3}", scns):
            r.err(f"Traceability row for {req_id} has no SCN-### and no "
                  f"explicit 'None' reason (Constitution §10).")
        if tests != "TBD" and module_name:
            if not re.fullmatch(rf"TC-{re.escape(module_name)}-\d{{3}}"
                                 rf"(,\s*TC-{re.escape(module_name)}-\d{{3}})*",
                                 tests):
                r.err(f"Traceability row for {req_id} Test(s) column "
                      f"'{tests}' is not TBD and does not match "
                      f"TC-{module_name}-### (Constitution §10).")

    # Every declared BR/NFR (Business Rules / NFR sections only) must
    # have a row — not every BR-###/NFR-### substring anywhere in the
    # document.
    bare_reqs = declared_requirements(sections)
    row_reqs = set()
    for req_id, *_ in parsed:
        rm = re.search(r"(BR|NFR)-(\d{3})$", req_id)
        if rm:
            row_reqs.add(f"{rm.group(1)}-{rm.group(2)}")
    missing_rows = bare_reqs - row_reqs
    if missing_rows:
        r.err(f"Requirement(s) with no Traceability Table row: "
              f"{sorted(missing_rows)} (Constitution §10).")

    # Inline (Traces to: ...) tags are the source of truth; table must
    # not contradict them for a given requirement's scenario set.
    inline_map: dict[str, set[str]] = {}
    for num, kind, req_num in SCN_DECL_RE.findall(text):
        inline_map.setdefault(f"{kind}-{req_num}", set()).add(f"SCN-{num}")
    for req_id, _, _, scns, _ in parsed:
        rm = re.search(r"(BR|NFR)-(\d{3})$", req_id)
        if not rm:
            continue
        key = f"{rm.group(1)}-{rm.group(2)}"
        table_scns = set(re.findall(r"SCN-\d{3}", scns))
        inline_scns = inline_map.get(key, set())
        if table_scns != inline_scns:
            r.err(f"{req_id}: Traceability Table lists {sorted(table_scns) or '{}'} "
                  f"but inline (Traces to:) tags say {sorted(inline_scns) or '{}'} — "
                  f"inline tags are the source of truth (Constitution §10). "
                  f"If a table scenario ID belongs to a *different* requirement "
                  f"in this spec, that scenario is being shared between two "
                  f"requirements, which Constitution §1 forbids.")


# ---------------------------------------------------------------------------
# Section 11 — banned vague words
# ---------------------------------------------------------------------------

def check_banned_words(sections: dict, r: Result) -> None:
    scope_text = sections.get("Business Rules", "") + sections.get(
        "Non-Functional Requirements", "")
    lowered = scope_text.lower()
    for word in BANNED_WORDS:
        if word in lowered:
            r.err(f"Banned vague word '{word}' found in Business Rules / "
                  f"NFRs (Constitution §11).")


# ---------------------------------------------------------------------------
# Section 3 — money handling statement present
# ---------------------------------------------------------------------------

def check_money_handling(sections: dict, r: Result) -> None:
    br_text = sections.get("Business Rules", "")
    if "money handling" not in br_text.lower() and "monetary values" not in br_text.lower():
        r.err("Business Rules section does not state how money is "
              "handled (or 'No monetary values.') (Constitution §3).")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def lint_file(path: Path, known_goals: set[str]) -> Result:
    r = Result(path=path)
    text = path.read_text()

    fm = parse_frontmatter(text, r)
    module_name, status = check_frontmatter(fm, r, known_goals)
    sections = check_sections(text, fm, r)
    check_requirement_scenario_graph(text, sections, module_name, status, r)
    check_scenario_groups(sections, status, r)
    check_nfrs(sections, text, r)
    check_traceability_table(sections, text, module_name, r)
    check_banned_words(sections, r)
    check_money_handling(sections, r)

    return r


def expand_paths(argv: list[str]) -> list[Path]:
    """Expand directories (recursively) into their .md files; skip
    non-.md files silently; keep .md files as given."""
    out: list[Path] = []
    for arg in argv:
        p = Path(arg)
        if p.is_dir():
            out.extend(sorted(p.rglob("*.md")))
        elif p.suffix == ".md":
            out.append(p)
        else:
            print(f"skipping non-.md path: {p}", file=sys.stderr)
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: lint_spec.py <spec.md | dir> [...]", file=sys.stderr)
        return 2

    paths = expand_paths(argv)
    if not paths:
        print("no .md spec files found in the given paths", file=sys.stderr)
        return 2

    known_goals = load_business_goals()
    if not known_goals:
        print(f"warning: {BUSINESS_GOALS_FILE} not found or empty — "
              f"skipping BG-### existence checks\n", file=sys.stderr)

    any_failed = False
    for path in paths:
        result = lint_file(path, known_goals)
        status_word = "PASS" if result.ok else "FAIL"
        print(f"\n=== {path}  [{status_word}] ===")
        for e in result.errors:
            print(f"  ERROR: {e}")
        for w in result.warnings:
            print(f"  warn:  {w}")
        if not result.errors and not result.warnings:
            print("  (no issues)")
        any_failed = any_failed or not result.ok

    print()
    return 1 if any_failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))