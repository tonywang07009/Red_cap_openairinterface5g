#!/usr/bin/env python3

"""Parse iperf3 UL JSON report and produce CSV + PASS/FAIL summary."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

CSV_COLUMNS = [
    "timestamp",
    "interval_sec",
    "throughput_ul_mbps",
    "lost_packets",
    "jitter_ms",
]


def parse_args() -> argparse.Namespace:
    """Build and parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert iperf3 UL JSON report to CSV and evaluate mean UL throughput."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to iperf3 JSON report generated with `iperf3 -J`.",
    )
    parser.add_argument(
        "--output",
        default="/tmp/redcap_ul_summary.csv",
        help="Output CSV path (default: /tmp/redcap_ul_summary.csv).",
    )
    parser.add_argument(
        "--threshold-mbps",
        type=float,
        default=30.0,
        help="PASS threshold for mean UL throughput in Mbps (default: 30).",
    )
    return parser.parse_args()


def load_report(path: Path) -> dict[str, Any]:
    """Load and return iperf3 JSON report content."""
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Invalid iperf JSON: top-level payload must be an object")
    return payload


def extract_interval_metrics(interval: dict[str, Any]) -> dict[str, float]:
    """Extract UL metrics from a single interval block."""
    data: dict[str, Any] | None = None

    sum_data = interval.get("sum")
    if isinstance(sum_data, dict) and "bits_per_second" in sum_data:
        data = sum_data

    if data is None:
        streams = interval.get("streams", [])
        if isinstance(streams, list):
            for stream in streams:
                if not isinstance(stream, dict):
                    continue
                udp = stream.get("udp")
                if isinstance(udp, dict) and "bits_per_second" in udp:
                    data = udp
                    break

    if data is None:
        raise ValueError("Interval does not contain UDP metrics with bits_per_second")

    start = float(data.get("start", 0.0))
    end = float(data.get("end", start))
    seconds = float(data.get("seconds", max(end - start, 0.0)))

    return {
        "start": start,
        "seconds": seconds,
        "throughput_ul_mbps": float(data.get("bits_per_second", 0.0)) / 1_000_000.0,
        "lost_packets": float(data.get("lost_packets", 0.0)),
        "jitter_ms": float(data.get("jitter_ms", 0.0)),
    }


def format_timestamp(start_epoch: int | None, start_offset_sec: float) -> str:
    """Format interval timestamp using report start epoch and interval offset."""
    if start_epoch is None:
        return f"offset+{start_offset_sec:.3f}s"

    dt = datetime.fromtimestamp(start_epoch + start_offset_sec, tz=timezone.utc)
    return dt.isoformat()


def build_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Build CSV rows from iperf interval metrics."""
    intervals = report.get("intervals", [])
    if not isinstance(intervals, list):
        raise ValueError("Invalid iperf JSON: 'intervals' must be a list")

    start_timestamp = report.get("start", {}).get("timestamp", {}).get("timesecs")
    start_epoch = int(start_timestamp) if isinstance(start_timestamp, (int, float)) else None

    rows: list[dict[str, Any]] = []
    for interval in intervals:
        if not isinstance(interval, dict):
            continue

        metrics = extract_interval_metrics(interval)
        rows.append(
            {
                "timestamp": format_timestamp(start_epoch, metrics["start"]),
                "interval_sec": f"{metrics['seconds']:.6f}",
                "throughput_ul_mbps": f"{metrics['throughput_ul_mbps']:.6f}",
                "lost_packets": str(int(round(metrics["lost_packets"]))),
                "jitter_ms": f"{metrics['jitter_ms']:.6f}",
            }
        )

    if not rows:
        raise ValueError("No interval metrics found in iperf JSON")

    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    """Write parsed rows to CSV output path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def compute_mean_throughput(rows: list[dict[str, Any]]) -> float:
    """Compute mean UL throughput in Mbps from CSV rows."""
    return mean(float(row["throughput_ul_mbps"]) for row in rows)


def main() -> int:
    """Execute CLI workflow and return process exit code."""
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    report = load_report(input_path)
    rows = build_rows(report)
    write_csv(rows, output_path)

    mean_throughput = compute_mean_throughput(rows)
    passed = mean_throughput >= args.threshold_mbps

    print(f"Input JSON: {input_path}")
    print(f"Output CSV: {output_path}")
    print(f"Processed intervals: {len(rows)}")
    print(f"Mean UL throughput: {mean_throughput:.3f} Mbps")
    if passed:
        print(f"Result: PASS (mean UL >= {args.threshold_mbps:g} Mbps)")
        return 0

    print(f"Result: FAIL (mean UL < {args.threshold_mbps:g} Mbps)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
