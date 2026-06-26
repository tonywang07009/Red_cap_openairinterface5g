#!/usr/bin/env python3
"""Apply manually digitized paper curve values to BWP/SDT result CSV files."""

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


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "exp_result"


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
    if paper == 0:
        row["diff_percent"] = "NA"
    else:
        row["diff_percent"] = f"{((local - paper) / paper * Decimal(100)):.6f}"


def read_result(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_result(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def apply_template(template: Path, include_tbd: bool) -> int:
    with template.open(newline="", encoding="utf-8") as handle:
        digitized_rows = list(csv.DictReader(handle))

    grouped: dict[str, list[dict[str, str]]] = {}
    for row in digitized_rows:
        paper_value = row.get("paper_value", "TBD")
        if as_decimal(paper_value) is None and not include_tbd:
            continue
        grouped.setdefault(row["target_csv"], []).append(row)

    updates = 0
    for csv_name, template_rows in grouped.items():
        result_path = RESULT_DIR / csv_name
        result_rows = read_result(result_path)
        by_key = {(row["scenario"], row["metric"]): row for row in result_rows}

        for template_row in template_rows:
            key = (template_row["scenario"], template_row["metric"])
            result_row = by_key.get(key)
            if result_row is None:
                result_row = {
                    "scenario": key[0],
                    "metric": key[1],
                    "paper_value": "TBD",
                    "local_value": "TBD",
                    "diff_absolute": "TBD",
                    "diff_percent": "TBD",
                }
                result_rows.append(result_row)
                by_key[key] = result_row

            result_row["paper_value"] = template_row.get("paper_value", "TBD")
            compute_diff(result_row)
            updates += 1

        write_result(result_path, result_rows)

    return updates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=Path, default=RESULT_DIR / "paper_curve_digitization_template.csv")
    parser.add_argument("--include-tbd", action="store_true", help="also seed TBD rows into result CSV files")
    args = parser.parse_args()

    updates = apply_template(args.template, args.include_tbd)
    print(f"applied {updates} digitized paper rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
