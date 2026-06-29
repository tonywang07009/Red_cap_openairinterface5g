#!/usr/bin/env python3
"""Aggregate repeated SDT runtime rows into scenario success probabilities."""

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


PROJECT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_TARGET = PROJECT_DIR / "exp_result" / "SDT_results.csv"
DEFAULT_OUTPUT = PROJECT_DIR / "exp_result" / "SDT_repeated_run_aggregate.csv"
DEFAULT_RUNTIME_GLOB = "test_log/redcap_bwp_sdt_validation/*_sdt/sdt_runtime_metrics.csv"


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


def metric_map(rows: list[dict[str, str]]) -> dict[str, str]:
    return {row["metric"]: row.get("local_value", "TBD") for row in rows}


def int_metric(metrics: dict[str, str], name: str) -> int:
    value = metrics.get(name, "0")
    try:
        return int(Decimal(value))
    except (InvalidOperation, ValueError):
        return 0


def derived_counters_from_markers(scenario: str, metrics: dict[str, str]) -> dict[str, int]:
    attempted = 1 if metrics.get("ue_in_sync_seen") == "1" or metrics.get("rrc_inactive_marker_seen") == "1" else 0
    is_sdt = "sdt" in scenario.lower()
    success = 1 if (is_sdt and metrics.get("cg_sdt_marker_seen") == "1") else 0
    if not is_sdt and metrics.get("rrc_resume_complete_seen") == "1":
        success = 1
    fallback = int_metric(metrics, "threshold_fallback_count")
    timeout = 1 if attempted and not success and not fallback else 0
    sdt_failure = 1 if attempted and is_sdt and not success and not fallback else 0
    return {
        "packet_attempt_count": attempted,
        "packet_success_count": success,
        "threshold_fallback_count": fallback,
        "timeout_failure_count": timeout,
        "sdt_failure_count": sdt_failure,
    }


def aggregate_runtime_csvs(runtime_paths: list[Path]) -> list[dict[str, str]]:
    grouped: dict[str, dict[str, int]] = {}
    for runtime_path in runtime_paths:
        rows = read_rows(runtime_path)
        if not rows:
            continue
        scenario = rows[0]["scenario"]
        metrics = metric_map(rows)
        current = grouped.setdefault(
            scenario,
            {
                "packet_attempt_count": 0,
                "packet_success_count": 0,
                "threshold_fallback_count": 0,
                "timeout_failure_count": 0,
                "sdt_failure_count": 0,
                "run_count": 0,
            },
        )
        counters = (
            {metric: int_metric(metrics, metric) for metric in current if metric != "run_count"}
            if "packet_attempt_count" in metrics
            else derived_counters_from_markers(scenario, metrics)
        )
        current["packet_attempt_count"] += counters["packet_attempt_count"]
        current["packet_success_count"] += counters["packet_success_count"]
        current["threshold_fallback_count"] += counters["threshold_fallback_count"]
        current["timeout_failure_count"] += counters["timeout_failure_count"]
        current["sdt_failure_count"] += counters["sdt_failure_count"]
        current["run_count"] += 1

    aggregate_rows: list[dict[str, str]] = []
    for scenario, counters in sorted(grouped.items()):
        attempted = counters["packet_attempt_count"]
        probability = "NA" if attempted == 0 else f"{counters['packet_success_count'] / attempted:.6f}"
        values: dict[str, str] = {
            "packet_transmission_success_probability": probability,
            "packet_attempt_count": str(attempted),
            "packet_success_count": str(counters["packet_success_count"]),
            "threshold_fallback_count": str(counters["threshold_fallback_count"]),
            "timeout_failure_count": str(counters["timeout_failure_count"]),
            "sdt_failure_count": str(counters["sdt_failure_count"]),
            "run_count": str(counters["run_count"]),
        }
        for metric, value in values.items():
            aggregate_rows.append(
                {
                    "scenario": scenario,
                    "metric": metric,
                    "paper_value": "TBD",
                    "local_value": value,
                    "diff_absolute": "TBD",
                    "diff_percent": "TBD",
                }
            )
    return aggregate_rows


def merge_rows(target: Path, aggregate_rows: list[dict[str, str]]) -> None:
    target_rows = read_rows(target)
    by_key = {(row["scenario"], row["metric"]): row for row in target_rows}
    for aggregate_row in aggregate_rows:
        key = (aggregate_row["scenario"], aggregate_row["metric"])
        target_row = by_key.get(key)
        if target_row is None:
            target_row = {
                "scenario": key[0],
                "metric": key[1],
                "paper_value": aggregate_row.get("paper_value", "TBD"),
                "local_value": "TBD",
                "diff_absolute": "TBD",
                "diff_percent": "TBD",
            }
            target_rows.append(target_row)
            by_key[key] = target_row
        target_row["local_value"] = aggregate_row["local_value"]
        compute_diff(target_row)
    write_rows(target, target_rows)


def resolve_runtime_paths(pattern: str) -> list[Path]:
    if Path(pattern).is_absolute():
        return sorted(path for path in Path("/").glob(pattern[1:]) if path.is_file())
    return sorted(path for path in REPO_ROOT.glob(pattern) if path.is_file())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-glob", default=DEFAULT_RUNTIME_GLOB)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-merge", action="store_true")
    args = parser.parse_args()

    runtime_paths = resolve_runtime_paths(args.runtime_glob)
    aggregate_rows = aggregate_runtime_csvs(runtime_paths)
    write_rows(args.output, aggregate_rows)
    if not args.no_merge:
        merge_rows(args.target, aggregate_rows)
    print(f"aggregated {len(runtime_paths)} runtime CSV files into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
