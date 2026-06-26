#!/usr/bin/env python3
"""Extract first-pass BWP validation metrics from OAI RFsim logs."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


CSV_HEADER = [
    "scenario",
    "metric",
    "paper_value",
    "local_value",
    "diff_absolute",
    "diff_percent",
]


def add_metric(rows: list[dict[str, str]], scenario: str, metric: str, value: str) -> None:
    rows.append(
        {
            "scenario": scenario,
            "metric": metric,
            "paper_value": "TBD",
            "local_value": value,
            "diff_absolute": "TBD",
            "diff_percent": "TBD",
        }
    )


def last_match(pattern: str, text: str) -> re.Match[str] | None:
    matches = list(re.finditer(pattern, text, re.MULTILINE))
    return matches[-1] if matches else None


def extract_metrics(gnb_log: Path, ric_log: Path | None, xapp_log: Path | None, scenario: str) -> list[dict[str, str]]:
    gnb_text = gnb_log.read_text(errors="replace")
    ric_text = ric_log.read_text(errors="replace") if ric_log and ric_log.exists() else ""
    xapp_text = xapp_log.read_text(errors="replace") if xapp_log and xapp_log.exists() else ""

    rows: list[dict[str, str]] = []

    rntis = sorted(set(re.findall(r"UE RNTI ([0-9A-Fa-f]+) CU-UE-ID", gnb_text)))
    add_metric(rows, scenario, "active_ue_count", str(len(rntis)))
    add_metric(rows, scenario, "unique_rnti_count", str(len(rntis)))

    add_metric(rows, scenario, "ric_e2_setup_seen", "1" if "E2 SETUP" in ric_text or "E2 SETUP RESPONSE rx" in gnb_text else "0")
    add_metric(rows, scenario, "xapp_e42_setup_seen", "1" if "E42 SETUP-RESPONSE rx" in xapp_text else "0")

    dlsch = last_match(r"UE\s+\S+:\s+dlsch_rounds\s+(\d+)/(\d+)/(\d+)/(\d+),\s+dlsch_errors\s+(\d+)", gnb_text)
    if dlsch:
        first, second, third, fourth, errors = (int(x) for x in dlsch.groups())
        total = first + second + third + fourth
        retrans = second + third + fourth
        add_metric(rows, scenario, "dlsch_total_rounds", str(total))
        add_metric(rows, scenario, "dlsch_retx_rounds", str(retrans))
        add_metric(rows, scenario, "dlsch_errors", str(errors))
        add_metric(rows, scenario, "dlsch_retx_ratio_percent", f"{(retrans / total * 100) if total else 0:.6f}")

    ulsch = last_match(r"UE\s+\S+:\s+ulsch_rounds\s+(\d+)/(\d+)/(\d+)/(\d+),\s+ulsch_errors\s+(\d+)", gnb_text)
    if ulsch:
        first, second, third, fourth, errors = (int(x) for x in ulsch.groups())
        total = first + second + third + fourth
        retrans = second + third + fourth
        add_metric(rows, scenario, "ulsch_total_rounds", str(total))
        add_metric(rows, scenario, "ulsch_retx_rounds", str(retrans))
        add_metric(rows, scenario, "ulsch_errors", str(errors))
        add_metric(rows, scenario, "ulsch_retx_ratio_percent", f"{(retrans / total * 100) if total else 0:.6f}")

    mac = last_match(r"UE\s+\S+:\s+MAC:\s+TX\s+(\d+)\s+RX\s+(\d+)\s+bytes", gnb_text)
    if mac:
        tx_bytes, rx_bytes = mac.groups()
        add_metric(rows, scenario, "gnb_mac_tx_bytes", tx_bytes)
        add_metric(rows, scenario, "gnb_mac_rx_bytes", rx_bytes)

    in_sync = "1" if re.search(r"UE RNTI \S+ CU-UE-ID \S+ in-sync", gnb_text) else "0"
    add_metric(rows, scenario, "ue_in_sync_seen", in_sync)

    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gnb-log", required=True, type=Path)
    parser.add_argument("--ric-log", type=Path)
    parser.add_argument("--xapp-log", type=Path)
    parser.add_argument("--scenario", default="local_rfsim_ue2_minimal")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rows = extract_metrics(args.gnb_log, args.ric_log, args.xapp_log, args.scenario)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
