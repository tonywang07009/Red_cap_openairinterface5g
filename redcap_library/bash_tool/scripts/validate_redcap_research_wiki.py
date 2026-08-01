#!/usr/bin/env python3
"""Validate the RedCap research wiki without modifying the repository."""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
WIKI_ROOT = REPO_ROOT / "agent_doc/Project_management/redcap_research_wiki"
CONTENT_DIRS = ("sources", "concepts", "systems", "decisions", "cases")
REQUIRED_FILES = ("README.md", "governance.md", "agent_goals.md", "index.md", "log.md")
REQUIRED_KEYS = ("status", "source_refs", "evidence_tier", "last_reviewed", "related_pages")
CASE_REQUIRED_KEYS = ("case_id", "case_type", "system_scope", "evidence_refs")
VALID_STATUS = {"draft", "review-required", "confirmed", "superseded"}
VALID_EVIDENCE = {"source-record", "3gpp", "paper", "runtime", "source-trace", "mixed", "inference"}
VALID_CASE_TYPES = {"resolved-problem", "blocked-path", "experiment-learning", "doc-drift"}
CLAIM_LABELS = {
    "[3GPP Evidence]",
    "[Paper Evidence]",
    "[Runtime Evidence]",
    "[Source Trace]",
    "[Inference]",
    "[Needs Verification]",
}
CLAIM_LABEL_RE = re.compile(
    r"\[(?:[A-Za-z0-9 -]+ Evidence|Source Trace|Inference|Needs Verification)\]"
)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CASE_ID_RE = re.compile(r"^CASE-\d{4}-\d{3}$")
LOG_RE = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\] (ingest|query|lint|review|supersede|capture) \| .+$", re.MULTILINE)
CASE_REQUIRED_SECTIONS = (
    "Question",
    "Context and Reproduction",
    "Expected versus Observed",
    "Evidence",
    "Competing Explanations",
    "Resolution or Next Owner",
    "Claim Boundary",
    "Documentation Impact",
)
SYSTEM_OVERVIEW_REQUIRED_SECTIONS = (
    "Scope",
    "System Flow",
    "Component Index",
    "Current State",
    "Evidence Ladder",
    "Repair Order",
    "Course Route",
    "Claim Boundary",
    "Open Questions",
)
SYSTEM_COMPONENT_REQUIRED_SECTIONS = (
    "Role",
    "Inputs and Outputs",
    "Owner and Source Trace",
    "Implementation Status",
    "Evidence and Markers",
    "Failure Propagation",
    "Repair Inventory",
    "Research Reading Card",
    "Course Route",
    "Claim Boundary",
    "Open Questions",
)


def parse_frontmatter(path: Path) -> tuple[dict[str, str], dict[str, list[str]], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) < 3 or lines[0] != "---":
        raise ValueError("missing opening frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing frontmatter delimiter") from exc

    scalars: dict[str, str] = {}
    lists: dict[str, list[str]] = {}
    active_list: str | None = None
    for line in lines[1:end]:
        if line.startswith("  - ") and active_list:
            lists[active_list].append(line[4:].strip())
            continue
        match = re.fullmatch(r"([a-z_]+):(.*)", line)
        if not match:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = match.group(1), match.group(2).strip()
        active_list = None
        if value:
            scalars[key] = value
        else:
            lists[key] = []
            active_list = key
    return scalars, lists, text


def check_local_links(path: Path, text: str, errors: list[str], repo_root: Path) -> None:
    for target in LINK_RE.findall(text):
        clean = target.split("#", 1)[0].strip()
        if not clean or clean.startswith(("http://", "https://", "mailto:", "/")):
            continue
        if not (path.parent / clean).resolve().exists():
            errors.append(f"{path.relative_to(REPO_ROOT)}: broken link {target}")


def validate(repo_root: Path = REPO_ROOT, wiki_root: Path = WIKI_ROOT) -> list[str]:
    errors: list[str] = []
    if not wiki_root.is_dir():
        return [f"missing wiki root: {wiki_root.relative_to(repo_root)}"]

    for name in REQUIRED_FILES:
        path = wiki_root / name
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(repo_root)}")
            continue
        check_local_links(path, path.read_text(encoding="utf-8"), errors, repo_root)

    index_path = wiki_root / "index.md"
    index_text = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""
    content_pages: list[Path] = []
    for dirname in CONTENT_DIRS:
        directory = wiki_root / dirname
        if not directory.is_dir():
            errors.append(f"missing content directory: {directory.relative_to(repo_root)}")
            continue
        content_pages.extend(path for path in sorted(directory.rglob("*.md")) if path.name != "case-template.md")

    if not content_pages:
        errors.append("wiki contains no content pages")

    for path in content_pages:
        rel_repo = path.relative_to(repo_root)
        rel_wiki = path.relative_to(wiki_root).as_posix()
        try:
            scalars, lists, text = parse_frontmatter(path)
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"{rel_repo}: {exc}")
            continue

        present = set(scalars) | set(lists)
        for key in REQUIRED_KEYS:
            if key not in present:
                errors.append(f"{rel_repo}: missing metadata {key}")
        rel_parts = path.relative_to(wiki_root).parts
        headings = set(re.findall(r"^## (.+)$", text, re.MULTILINE))
        if rel_parts[0] == "cases":
            for key in CASE_REQUIRED_KEYS:
                if key not in present:
                    errors.append(f"{rel_repo}: missing metadata {key}")
            if not CASE_ID_RE.fullmatch(scalars.get("case_id", "")):
                errors.append(f"{rel_repo}: invalid case_id {scalars.get('case_id')!r}")
            if scalars.get("case_type") not in VALID_CASE_TYPES:
                errors.append(f"{rel_repo}: invalid case_type {scalars.get('case_type')!r}")
            if not scalars.get("system_scope"):
                errors.append(f"{rel_repo}: empty system_scope")
            for section in CASE_REQUIRED_SECTIONS:
                if section not in headings:
                    errors.append(f"{rel_repo}: missing required section {section}")
        if len(rel_parts) == 3 and rel_parts[0] == "systems":
            required_sections = (
                SYSTEM_OVERVIEW_REQUIRED_SECTIONS if path.name == "overview.md" else SYSTEM_COMPONENT_REQUIRED_SECTIONS
            )
            for section in required_sections:
                if section not in headings:
                    errors.append(f"{rel_repo}: missing required section {section}")
        if scalars.get("status") not in VALID_STATUS:
            errors.append(f"{rel_repo}: invalid status {scalars.get('status')!r}")
        if scalars.get("evidence_tier") not in VALID_EVIDENCE:
            errors.append(f"{rel_repo}: invalid evidence_tier {scalars.get('evidence_tier')!r}")
        if not DATE_RE.fullmatch(scalars.get("last_reviewed", "")):
            errors.append(f"{rel_repo}: invalid last_reviewed date")

        source_refs = lists.get("source_refs", [])
        if not source_refs:
            errors.append(f"{rel_repo}: source_refs must not be empty")
        for source_ref in source_refs:
            if source_ref.startswith(("https://", "http://")):
                continue
            if not (repo_root / source_ref).exists():
                errors.append(f"{rel_repo}: missing source_ref {source_ref}")
        evidence_refs = lists.get("evidence_refs", [])
        if rel_parts[0] == "cases" and not evidence_refs:
            errors.append(f"{rel_repo}: evidence_refs must not be empty")
        for evidence_ref in evidence_refs:
            if not (repo_root / evidence_ref).exists():
                errors.append(f"{rel_repo}: missing evidence_ref {evidence_ref}")
        for related_page in lists.get("related_pages", []):
            if not (repo_root / related_page).is_file():
                errors.append(f"{rel_repo}: missing related_page {related_page}")

        if rel_wiki not in index_text:
            errors.append(f"{rel_repo}: page is not linked from index.md")
        if not any(label in text for label in CLAIM_LABELS):
            errors.append(f"{rel_repo}: no approved evidence label")
        for label in set(CLAIM_LABEL_RE.findall(text)) - CLAIM_LABELS:
            errors.append(f"{rel_repo}: unsupported evidence label {label}")
        check_local_links(path, text, errors, repo_root)

    log_path = wiki_root / "log.md"
    if log_path.is_file() and not LOG_RE.search(log_path.read_text(encoding="utf-8")):
        errors.append(f"{log_path.relative_to(repo_root)}: no parseable append-only log entry")
    return errors


def selftest() -> int:
    with tempfile.TemporaryDirectory() as temporary_directory:
        repo_root = Path(temporary_directory)
        wiki_root = repo_root / "agent_doc/Project_management/redcap_research_wiki"
        for name in REQUIRED_FILES:
            (wiki_root / name).parent.mkdir(parents=True, exist_ok=True)
            (wiki_root / name).write_text("# fixture\n", encoding="utf-8")
        (wiki_root / "log.md").write_text("## [2026-01-01] capture | fixture case\n", encoding="utf-8")
        (repo_root / "fixture-source.txt").write_text("source\n", encoding="utf-8")
        (repo_root / "fixture-evidence.txt").write_text("evidence\n", encoding="utf-8")
        page = """---
status: review-required
source_refs:
  - fixture-source.txt
evidence_tier: source-record
last_reviewed: 2026-01-01
related_pages:
---

# Fixture

[Source Trace] fixture
"""
        case = """---
status: review-required
case_id: CASE-2026-001
case_type: doc-drift
system_scope: fixture
source_refs:
  - fixture-source.txt
evidence_refs:
  - fixture-evidence.txt
evidence_tier: source-trace
last_reviewed: 2026-01-01
related_pages:
  - agent_doc/Project_management/redcap_research_wiki/systems/page.md
---

# Fixture case

## Question

## Context and Reproduction

## Expected versus Observed

## Evidence

[Source Trace] fixture

## Competing Explanations

## Resolution or Next Owner

## Claim Boundary

## Documentation Impact
"""
        index_entries = []
        for dirname in CONTENT_DIRS:
            path = wiki_root / dirname / "page.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(case if dirname == "cases" else page, encoding="utf-8")
            index_entries.append(f"- {dirname}/page.md")
        nested_component = page + """

## Role

## Inputs and Outputs

## Owner and Source Trace

## Implementation Status

## Evidence and Markers

## Failure Propagation

## Repair Inventory

## Research Reading Card

## Course Route

## Claim Boundary

## Open Questions

[Concept](../../concepts/page.md)
"""
        nested_path = wiki_root / "systems/domain/component.md"
        nested_path.parent.mkdir(parents=True, exist_ok=True)
        nested_path.write_text(nested_component, encoding="utf-8")
        index_entries.append("- systems/domain/component.md")
        (wiki_root / "index.md").write_text("\n".join(index_entries), encoding="utf-8")

        assert not validate(repo_root, wiki_root), "valid case and nested system fixtures must pass"
        case_path = wiki_root / "cases/page.md"
        case_path.write_text(case.replace("## Evidence", "## Evidence Missing"), encoding="utf-8")
        assert any("missing required section Evidence" in error for error in validate(repo_root, wiki_root)), (
            "invalid case fixture must fail"
        )
        case_path.write_text(case, encoding="utf-8")
        nested_path.write_text(nested_component.replace("## Open Questions", "## Questions Missing"), encoding="utf-8")
        assert any("missing required section Open Questions" in error for error in validate(repo_root, wiki_root)), (
            "invalid nested system fixture must fail"
        )
    print("REDCAP_RESEARCH_WIKI_SELFTEST PASS valid_case=1 invalid_case=1 valid_nested=1 invalid_nested=1")
    return 0


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        return selftest()
    if len(sys.argv) != 1:
        print("usage: validate_redcap_research_wiki.py [--self-test]", file=sys.stderr)
        return 2
    errors = validate()
    if errors:
        for error in errors:
            print(f"REDCAP_RESEARCH_WIKI_CHECK FAIL {error}", file=sys.stderr)
        return 1
    pages = sum(
        1 for dirname in CONTENT_DIRS for path in (WIKI_ROOT / dirname).rglob("*.md") if path.name != "case-template.md"
    )
    print(f"REDCAP_RESEARCH_WIKI_CHECK PASS pages={pages}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
