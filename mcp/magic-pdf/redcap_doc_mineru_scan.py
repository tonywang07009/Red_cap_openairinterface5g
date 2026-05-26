#!/usr/bin/env python3
"""Build RedCap PDF Markdown cache with the local MinerU environment."""

from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path

from mineru.cli.common import do_parse


REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_ROOT = REPO_ROOT / "redcap_doc/specs/redcap_3gpp"
PAPER_ROOT = REPO_ROOT / "redcap_doc/evaluation_papers"
CACHE_ROOT = REPO_ROOT / "redcap_doc/mineru_markdown"
MANIFEST = CACHE_ROOT / "scan_manifest.md"


@dataclass
class PdfItem:
    kind: str
    source: Path
    output_dir: Path
    pages: int | None
    max_pages: int | None


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def page_count(path: Path) -> int | None:
    result = subprocess.run(
        ["pdfinfo", str(path)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return None
    return None


def find_markdown(output_dir: Path, source: Path) -> Path | None:
    if not output_dir.exists():
        return None

    candidates = [p for p in output_dir.rglob("*.md") if p.is_file() and p.stat().st_size > 0]
    if not candidates:
        return None

    source_name = source.name
    source_stem = source.stem
    for candidate in candidates:
        parts = set(candidate.parts)
        if source_name in parts or source_name in candidate.name or source_stem in candidate.name:
            return candidate
    return None


def parse_pdf(item: PdfItem, language: str) -> tuple[str, Path | None, str]:
    existing = find_markdown(item.output_dir, item.source)
    if existing:
        return "CACHED", existing, "existing Markdown cache"

    if item.max_pages is not None and item.pages is not None and item.pages > item.max_pages:
        return "PENDING_LARGE_PDF", None, f"{item.pages} pages exceeds threshold {item.max_pages}"

    item.output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[PARSE] {item.kind}: {rel(item.source)} -> {rel(item.output_dir)}", flush=True)

    try:
        do_parse(
            output_dir=str(item.output_dir),
            pdf_file_names=[item.source.name],
            pdf_bytes_list=[item.source.read_bytes()],
            p_lang_list=[language],
            backend="pipeline",
            parse_method="auto",
            formula_enable=False,
            table_enable=False,
            f_draw_layout_bbox=False,
            f_draw_span_bbox=False,
            f_dump_md=True,
            f_dump_middle_json=False,
            f_dump_model_output=False,
            f_dump_orig_pdf=False,
            f_dump_content_list=False,
        )
    except Exception as exc:  # keep batch moving and record the blocker
        return "FAIL", None, str(exc).replace("\n", " ")

    generated = find_markdown(item.output_dir, item.source)
    if generated:
        return "PARSED", generated, "MinerU pipeline markdown"
    return "FAIL", None, "MinerU completed but Markdown output was not found"


def inventory(max_spec_pages: int) -> list[PdfItem]:
    items: list[PdfItem] = []

    for source in sorted(PAPER_ROOT.glob("*.pdf")):
        items.append(
            PdfItem(
                kind="paper",
                source=source,
                output_dir=CACHE_ROOT / "evaluation_papers",
                pages=page_count(source),
                max_pages=None,
            )
        )

    for source in sorted(SPEC_ROOT.rglob("*.pdf")):
        category = source.parent.relative_to(SPEC_ROOT)
        items.append(
            PdfItem(
                kind="spec",
                source=source,
                output_dir=CACHE_ROOT / "specs/redcap_3gpp" / category,
                pages=page_count(source),
                max_pages=max_spec_pages,
            )
        )

    return items


def write_manifest(rows: list[tuple[PdfItem, str, Path | None, str]]) -> None:
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    lines = [
        "# RedCap MinerU Markdown Scan Manifest",
        "",
        "## Purpose",
        "- Track Markdown cache generated from RedCap specs and evaluation papers.",
        "- Use Markdown cache for quick lookup; use source PDFs for exact wording and final clause verification.",
        "- Status `[PENDING_LARGE_PDF]` means the source is too large for an interactive MinerU OCR run.",
        "",
        "## Inventory",
        "| Kind | Pages | Source PDF | Markdown Cache | Status | Note |",
        "|---|---:|---|---|---|---|",
    ]
    for item, status, output, note in rows:
        output_text = f"`{rel(output)}`" if output else "-"
        pages = item.pages if item.pages is not None else "NA"
        lines.append(
            f"| `{item.kind}` | {pages} | `{rel(item.source)}` | {output_text} | [{status}] | {note} |"
        )

    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", default="ch")
    parser.add_argument("--max-spec-pages", type=int, default=150)
    args = parser.parse_args()

    rows: list[tuple[PdfItem, str, Path | None, str]] = []
    for item in inventory(args.max_spec_pages):
        status, output, note = parse_pdf(item, args.language)
        print(f"[{status}] {rel(item.source)}", flush=True)
        rows.append((item, status, output, note))

    write_manifest(rows)
    print(f"[MANIFEST] {rel(MANIFEST)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
