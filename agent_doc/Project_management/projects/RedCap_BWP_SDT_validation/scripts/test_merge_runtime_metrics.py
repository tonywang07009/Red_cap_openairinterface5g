#!/usr/bin/env python3
"""Smoke-test runtime metric merge behavior."""

from __future__ import annotations

import csv
from pathlib import Path
from tempfile import TemporaryDirectory

from merge_runtime_metrics import CSV_HEADER, merge_runtime


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {(row["scenario"], row["metric"]): row for row in csv.DictReader(handle)}


def main() -> int:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / "target.csv"
        runtime = root / "runtime.csv"
        write_rows(
            target,
            [
                {
                    "scenario": "scenario_a",
                    "metric": "stale_metric",
                    "paper_value": "10",
                    "local_value": "4",
                    "diff_absolute": "-6",
                    "diff_percent": "-60.000000",
                },
                {
                    "scenario": "scenario_a",
                    "metric": "fresh_metric",
                    "paper_value": "2",
                    "local_value": "TBD",
                    "diff_absolute": "TBD",
                    "diff_percent": "TBD",
                },
            ],
        )
        write_rows(
            runtime,
            [
                {
                    "scenario": "scenario_a",
                    "metric": "fresh_metric",
                    "paper_value": "TBD",
                    "local_value": "3",
                    "diff_absolute": "TBD",
                    "diff_percent": "TBD",
                }
            ],
        )

        merge_runtime(target, runtime, replace_scenario=True)
        rows = read_rows(target)

    assert rows[("scenario_a", "fresh_metric")]["local_value"] == "3"
    assert rows[("scenario_a", "fresh_metric")]["diff_absolute"] == "1"
    assert rows[("scenario_a", "stale_metric")]["local_value"] == "TBD"
    assert rows[("scenario_a", "stale_metric")]["diff_absolute"] == "TBD"
    print("Runtime merge smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
