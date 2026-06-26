#!/usr/bin/env python3
"""Extract first-pass SDT validation metrics from OAI RFsim logs."""

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


def marker_seen(text: str, *patterns: str) -> str:
    return "1" if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns) else "0"


def last_match(pattern: str, text: str) -> re.Match[str] | None:
    matches = list(re.finditer(pattern, text, re.MULTILINE))
    return matches[-1] if matches else None


def extract_metrics(gnb_log: Path, ue_log: Path | None, scenario: str) -> list[dict[str, str]]:
    gnb_text = gnb_log.read_text(errors="replace")
    ue_text = ue_log.read_text(errors="replace") if ue_log and ue_log.exists() else ""
    combined = f"{gnb_text}\n{ue_text}"

    rows: list[dict[str, str]] = []
    rntis = sorted(set(re.findall(r"UE RNTI ([0-9A-Fa-f]+) CU-UE-ID", gnb_text)))

    add_metric(rows, scenario, "active_ue_count", str(len(rntis)))
    add_metric(rows, scenario, "ue_in_sync_seen", marker_seen(gnb_text, r"UE RNTI \S+ CU-UE-ID \S+ in-sync"))
    add_metric(rows, scenario, "rrc_inactive_marker_seen", marker_seen(combined, r"RRC_INACTIVE", r"RRC INACTIVE"))
    add_metric(rows, scenario, "rrc_resume_request_seen", marker_seen(combined, r"RRCResumeRequest"))
    add_metric(rows, scenario, "rrc_resume_complete_seen", marker_seen(combined, r"RRCResumeComplete"))
    add_metric(rows, scenario, "configured_grant_marker_seen", marker_seen(combined, r"configuredGrantConfig", r"configured grant"))
    add_metric(rows, scenario, "cg_sdt_marker_seen", marker_seen(combined, r"cg-SDT", r"CG SDT"))

    dlsch = last_match(r"UE\s+\S+:\s+dlsch_rounds\s+(\d+)/(\d+)/(\d+)/(\d+),\s+dlsch_errors\s+(\d+)", gnb_text)
    if dlsch:
        first, second, third, fourth, errors = (int(x) for x in dlsch.groups())
        total = first + second + third + fourth
        retrans = second + third + fourth
        add_metric(rows, scenario, "dlsch_total_rounds", str(total))
        add_metric(rows, scenario, "dlsch_errors", str(errors))
        add_metric(rows, scenario, "dlsch_retx_ratio_percent", f"{(retrans / total * 100) if total else 0:.6f}")

    ulsch = last_match(r"UE\s+\S+:\s+ulsch_rounds\s+(\d+)/(\d+)/(\d+)/(\d+),\s+ulsch_errors\s+(\d+)", gnb_text)
    if ulsch:
        first, second, third, fourth, errors = (int(x) for x in ulsch.groups())
        total = first + second + third + fourth
        retrans = second + third + fourth
        add_metric(rows, scenario, "ulsch_total_rounds", str(total))
        add_metric(rows, scenario, "ulsch_errors", str(errors))
        add_metric(rows, scenario, "ulsch_retx_ratio_percent", f"{(retrans / total * 100) if total else 0:.6f}")

    mac = last_match(r"UE\s+\S+:\s+MAC:\s+TX\s+(\d+)\s+RX\s+(\d+)\s+bytes", gnb_text)
    if mac:
        tx_bytes, rx_bytes = mac.groups()
        add_metric(rows, scenario, "gnb_mac_tx_bytes", tx_bytes)
        add_metric(rows, scenario, "gnb_mac_rx_bytes", rx_bytes)

    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gnb-log", required=True, type=Path)
    parser.add_argument("--ue-log", type=Path)
    parser.add_argument("--scenario", default="local_rfsim_ue2_minimal_sdt")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rows = extract_metrics(args.gnb_log, args.ue_log, args.scenario)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
