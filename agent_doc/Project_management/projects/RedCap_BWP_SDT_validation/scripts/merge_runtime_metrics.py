#!/usr/bin/env python3
"""Merge runtime metric rows into the paper/local comparison CSV."""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path


CSV_HEADER = [
    "scenario",
    "metric",
    "paper_value",
    "local_value",
    "diff_absolute",
    "diff_percent",
]


def as_decimal(value: str) -> Decimal | None:
    if value in {"", "TBD", "NA", "[TBD]", "[NA]"}:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return None


def compute_diff(row: dict[str, str]) -> None:
    paper = as_decimal(row.get("paper_value", ""))
    local = as_decimal(row.get("local_value", ""))
    if paper is None or local is None:
        row["diff_absolute"] = "TBD"
        row["diff_percent"] = "TBD"
        return
    row["diff_absolute"] = str(local - paper)
    row["diff_percent"] = "NA" if paper == 0 else f"{((local - paper) / paper * Decimal(100)):.6f}"


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def merge_runtime(target: Path, runtime: Path, replace_scenario: bool = False) -> int:
    target_rows = read_rows(target)
    runtime_rows = read_rows(runtime)
    by_key = {(row["scenario"], row["metric"]): row for row in target_rows}
    runtime_keys = {(row["scenario"], row["metric"]) for row in runtime_rows}

    updates = 0
    for runtime_row in runtime_rows:
        key = (runtime_row["scenario"], runtime_row["metric"])
        target_row = by_key.get(key)
        if target_row is None:
            target_row = {
                "scenario": key[0],
                "metric": key[1],
                "paper_value": runtime_row.get("paper_value", "TBD"),
                "local_value": "TBD",
                "diff_absolute": "TBD",
                "diff_percent": "TBD",
            }
            target_rows.append(target_row)
            by_key[key] = target_row

        target_row["local_value"] = runtime_row.get("local_value", "TBD")
        compute_diff(target_row)
        updates += 1

    if replace_scenario:
        runtime_scenarios = {scenario for scenario, _metric in runtime_keys}
        for target_row in target_rows:
            key = (target_row["scenario"], target_row["metric"])
            if target_row["scenario"] in runtime_scenarios and key not in runtime_keys:
                target_row["local_value"] = "TBD"
                compute_diff(target_row)
                updates += 1

    write_rows(target, target_rows)
    return updates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--runtime", required=True, type=Path)
    parser.add_argument(
        "--replace-scenario",
        action="store_true",
        help="reset stale local values for metrics in the same runtime scenario that are absent from the runtime CSV",
    )
    args = parser.parse_args()

    updates = merge_runtime(args.target, args.runtime, replace_scenario=args.replace_scenario)
    print(f"merged {updates} runtime rows into {args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
