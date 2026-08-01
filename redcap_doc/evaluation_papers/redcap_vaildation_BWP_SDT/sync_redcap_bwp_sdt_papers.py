#!/usr/bin/env python3
"""Sync RedCap BWP/SDT paper PDFs to Markdown and metadata.

This script is intentionally local and deterministic:
- scan PDFs in this directory
- convert missing or stale Markdown with markitdown
- refresh redcap_vaildation_BWP_SDT_index.json
- optionally refresh the SymDex text index for this paper folder
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "redcap_vaildation_BWP_SDT_index.json"

KNOWN_OUTPUTS = {
    "paper1_BWP_switching.pdf": "paper1_BWP_switching.md",
    "paper2_SDT_small_data.pdf": "paper2_SDT_small_data.md",
    "Impact_of_Bandwidth_Part_BWP_Switching_on_5G_NR_System_Performance.pdf": "paper1_BWP_switching.md",
    "Novel_Random_Access_Schemes_for_Small_Data_Transmission.pdf": "paper2_SDT_small_data.md",
}

PREFERRED_PDF_ALIASES = {
    "paper1_BWP_switching.pdf": "Impact_of_Bandwidth_Part_BWP_Switching_on_5G_NR_System_Performance.pdf",
    "paper2_SDT_small_data.pdf": "Novel_Random_Access_Schemes_for_Small_Data_Transmission.pdf",
}

KNOWN_METADATA = {
    "paper1_BWP_switching.md": {
        "paper_id": "paper1_BWP_switching",
        "title": "Impact of Bandwidth Part (BWP) Switching on 5G NR System Performance",
        "authors": [
            "Fuad Abinader",
            "Andrea Marcano",
            "Karol Schober",
            "Riikka Nurminen",
            "Tero Henttonen",
            "Hisashi Onozawa",
            "Elena Virtej",
        ],
        "year": "2019",
        "keywords": ["5G NR", "Bandwidth Parts", "BWP adaptation", "BWP inactivity timer", "BWP switch delay"],
        "scenario_tags": ["BWP switching", "system-level simulation", "TDD", "FTP3 traffic", "Poisson arrivals"],
        "target_technology": "BWP switching with inactivity timer and switch delay",
    },
    "paper2_SDT_small_data.md": {
        "paper_id": "paper2_SDT_small_data",
        "title": "Novel Random Access Schemes for Small Data Transmission",
        "authors": ["Hui Zhou", "Yansha Deng", "Luca Feltrin", "Andreas Hoglund", "Mischa Dohler"],
        "year": "2022",
        "keywords": ["Grant-based", "Grant-free", "4-step RA", "2-step RA", "Small Data Transmission", "RRC Inactive"],
        "scenario_tags": ["RA-SDT", "CG-SDT placeholder", "RRC Inactive", "Poisson packet arrival", "PPP devices"],
        "target_technology": "4/2-step SDT random access for small data transmission",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def markdown_name(pdf: Path) -> str:
    if pdf.name in KNOWN_OUTPUTS:
        return KNOWN_OUTPUTS[pdf.name]
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", pdf.stem).strip("_").lower()
    return f"{cleaned}.md"


def iter_source_pdfs() -> list[Path]:
    """Return one source PDF per paper, preferring stable user-facing aliases."""
    by_name = {pdf.name: pdf for pdf in ROOT.glob("*.pdf")}
    consumed: set[str] = set()
    selected: list[Path] = []

    for alias, canonical in PREFERRED_PDF_ALIASES.items():
        if alias in by_name:
            selected.append(by_name[alias])
            consumed.add(alias)
            consumed.add(canonical)
        elif canonical in by_name:
            selected.append(by_name[canonical])
            consumed.add(canonical)

    selected.extend(pdf for name, pdf in sorted(by_name.items()) if name not in consumed)
    return selected


def maybe_convert(pdf: Path, md: Path, markitdown_bin: str) -> bool:
    if md.exists() and md.stat().st_mtime >= pdf.stat().st_mtime:
        return False
    subprocess.run([markitdown_bin, str(pdf), "-o", str(md)], cwd=ROOT, check=True)
    return True


def build_record(pdf: Path, md: Path, converted: bool) -> dict:
    metadata = KNOWN_METADATA.get(md.name, {})
    resolved = pdf.resolve()
    return {
        "paper_id": metadata.get("paper_id", md.stem),
        "title": metadata.get("title", md.stem.replace("_", " ")),
        "authors": metadata.get("authors", []),
        "year": metadata.get("year", "TBD"),
        "keywords": metadata.get("keywords", []),
        "scenario_tags": metadata.get("scenario_tags", []),
        "target_technology": metadata.get("target_technology", "TBD"),
        "source_pdf": pdf.name,
        "source_pdf_resolved": resolved.name,
        "markdown_path": md.name,
        "source_pdf_sha256": sha256(pdf),
        "markdown_sha256": sha256(md) if md.exists() else None,
        "extraction_status": "converted" if converted else "up_to_date",
    }


def refresh_symdex(symdex_bin: str | None) -> str:
    if not symdex_bin:
        return "skipped"
    repo_root = ROOT.parents[2]
    state_dir = repo_root / ".symdex"
    subprocess.run(
        [
            symdex_bin,
            "--state-dir",
            str(state_dir),
            "index",
            "--repo",
            "redcap_bwp_sdt_papers",
            str(ROOT),
        ],
        cwd=repo_root,
        check=True,
    )
    return "refreshed"


def pdf_snapshot() -> tuple[tuple[str, int, int], ...]:
    return tuple((pdf.name, pdf.stat().st_mtime_ns, pdf.stat().st_size) for pdf in sorted(ROOT.glob("*.pdf")))


def sync_once(markitdown_bin: str, symdex_bin: str | None) -> None:
    if not Path(markitdown_bin).exists():
        raise SystemExit(f"markitdown not found: {markitdown_bin}")

    records = []
    for pdf in iter_source_pdfs():
        md = ROOT / markdown_name(pdf)
        converted = maybe_convert(pdf, md, markitdown_bin)
        records.append(build_record(pdf, md, converted))

    payload = {
        "index_name": "redcap_vaildation_BWP_SDT_index",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "directory": str(ROOT),
        "symdex_repo": "redcap_bwp_sdt_papers",
        "symdex_status": refresh_symdex(symdex_bin),
        "papers": records,
    }
    INDEX.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {INDEX}")


def watch_loop(markitdown_bin: str, symdex_bin: str | None, interval: float, cycles: int | None) -> None:
    last_snapshot: tuple[tuple[str, int, int], ...] | None = None
    completed = 0

    while True:
        current = pdf_snapshot()
        if current != last_snapshot:
            sync_once(markitdown_bin, symdex_bin)
            last_snapshot = current

        completed += 1
        if cycles is not None and completed >= cycles:
            return
        time.sleep(interval)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--markitdown", default=shutil.which("markitdown") or "/home/tonywang/miniforge3/envs/mcp/bin/markitdown")
    parser.add_argument("--symdex", default=shutil.which("symdex") or "/home/tonywang/miniforge3/bin/symdex")
    parser.add_argument("--skip-symdex", action="store_true")
    parser.add_argument("--watch", action="store_true", help="poll this directory and resync whenever PDF files change")
    parser.add_argument("--watch-interval", type=float, default=30.0, help="seconds between PDF directory scans in watch mode")
    parser.add_argument("--watch-cycles", type=int, default=None, help="optional finite watch loop count for validation")
    args = parser.parse_args()

    symdex_bin = None if args.skip_symdex else args.symdex
    if args.watch:
        watch_loop(args.markitdown, symdex_bin, args.watch_interval, args.watch_cycles)
    else:
        sync_once(args.markitdown, symdex_bin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
