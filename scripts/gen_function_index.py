#!/usr/bin/env python3

"""Generate a JSON index of newly added function definitions from a git diff."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

FUNCTION_DEF_RE = re.compile(
    r"""
(?P<signature>
^[ \t]*
(?!if\b|for\b|while\b|switch\b|else\b|do\b)
(?:[A-Za-z_][\w]*[ \t\*]+)+
(?P<name>[A-Za-z_]\w*)
[ \t]*\(
(?P<params>(?:[^(){};]|\([^()]*\))*)
\)
[ \t]*\{
)
""",
    re.MULTILINE | re.VERBOSE,
)

HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(?P<start>\d+)(?:,(?P<count>\d+))? @@")


@dataclass(frozen=True)
class AddedRange:
    """Represent a 1-based inclusive added-line range."""

    start: int
    end: int

    def contains(self, line_number: int) -> bool:
        """Return True when line_number is inside this range."""
        return self.start <= line_number <= self.end


def parse_args() -> argparse.Namespace:
    """Build and parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Scan git diff and output JSON index for newly added function definitions."
    )
    parser.add_argument("--base-ref", default="HEAD~1", help="Git base ref (default: HEAD~1).")
    parser.add_argument("--head-ref", default="HEAD", help="Git head ref (default: HEAD).")
    parser.add_argument(
        "--output",
        default="scripts/output/function_index.json",
        help="Output JSON path (default: scripts/output/function_index.json).",
    )
    parser.add_argument(
        "--extensions",
        default=".c,.h,.cc,.cpp,.hpp",
        help="Comma-separated source file extensions to inspect.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output with indentation.",
    )
    return parser.parse_args()


def run_git(args: list[str]) -> str:
    """Run a git command and return stdout, raising on non-zero exit."""
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def normalize_extensions(raw: str) -> tuple[str, ...]:
    """Normalize extension CSV into a tuple of dot-prefixed extensions."""
    values = []
    for token in (part.strip() for part in raw.split(",")):
        if not token:
            continue
        values.append(token if token.startswith(".") else f".{token}")
    if not values:
        raise ValueError("At least one file extension must be provided")
    return tuple(values)


def list_changed_source_files(base_ref: str, head_ref: str, extensions: tuple[str, ...]) -> list[str]:
    """List changed source files between refs filtered by extension."""
    output = run_git(["diff", "--name-only", "--diff-filter=ACMRT", f"{base_ref}..{head_ref}"])
    files = []
    for line in output.splitlines():
        path = line.strip()
        if path.endswith(extensions):
            files.append(path)
    return files


def parse_added_ranges(patch_text: str) -> list[AddedRange]:
    """Parse unified diff text and return added-line ranges from hunk headers."""
    ranges: list[AddedRange] = []
    for line in patch_text.splitlines():
        match = HUNK_RE.match(line)
        if not match:
            continue

        start = int(match.group("start"))
        count = int(match.group("count") or "1")
        if count <= 0:
            continue

        ranges.append(AddedRange(start=start, end=start + count - 1))
    return ranges


def get_added_ranges_for_file(base_ref: str, head_ref: str, path: str) -> list[AddedRange]:
    """Return added-line ranges for a specific file between refs."""
    patch = run_git(["diff", "--unified=0", f"{base_ref}..{head_ref}", "--", path])
    return parse_added_ranges(patch)


def read_file_at_ref(ref: str, path: str) -> str:
    """Read file content from a given git ref."""
    return run_git(["show", f"{ref}:{path}"])


def extract_functions(file_content: str, path: str) -> list[dict[str, object]]:
    """Extract candidate C/C++ function definitions from file content."""
    functions: list[dict[str, object]] = []

    for match in FUNCTION_DEF_RE.finditer(file_content):
        signature = " ".join(match.group("signature").split())
        name = match.group("name")
        params = " ".join(match.group("params").split())
        start_line = file_content.count("\n", 0, match.start("signature")) + 1

        functions.append(
            {
                "name": name,
                "file": path,
                "line": start_line,
                "signature": signature,
                "parameters": params,
            }
        )

    return functions


def keep_added_functions(functions: Iterable[dict[str, object]], added_ranges: list[AddedRange]) -> list[dict[str, object]]:
    """Keep only functions whose start line is part of added lines in the diff."""
    if not added_ranges:
        return []

    kept: list[dict[str, object]] = []
    for func in functions:
        line = int(func["line"])
        if any(line_range.contains(line) for line_range in added_ranges):
            kept.append(func)
    return kept


def build_index(base_ref: str, head_ref: str, extensions: tuple[str, ...]) -> dict[str, object]:
    """Build full function index payload for changed files."""
    entries: list[dict[str, object]] = []

    changed_files = list_changed_source_files(base_ref, head_ref, extensions)
    for path in changed_files:
        added_ranges = get_added_ranges_for_file(base_ref, head_ref, path)
        if not added_ranges:
            continue

        try:
            content = read_file_at_ref(head_ref, path)
        except subprocess.CalledProcessError:
            # Skip files not present in head ref (edge-case around complex renames).
            continue

        all_functions = extract_functions(content, path)
        entries.extend(keep_added_functions(all_functions, added_ranges))

    entries.sort(key=lambda item: (str(item["file"]), int(item["line"]), str(item["name"])))

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_ref": base_ref,
        "head_ref": head_ref,
        "extensions": list(extensions),
        "function_count": len(entries),
        "functions": entries,
    }


def main() -> int:
    """Execute script entrypoint and return process exit code."""
    args = parse_args()
    extensions = normalize_extensions(args.extensions)
    output_path = Path(args.output)

    payload = build_index(args.base_ref, args.head_ref, extensions)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2 if args.pretty else None)
        handle.write("\n")

    print(f"Output JSON: {output_path}")
    print(f"Function count: {payload['function_count']}")
    print(f"Refs: {args.base_ref}..{args.head_ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
