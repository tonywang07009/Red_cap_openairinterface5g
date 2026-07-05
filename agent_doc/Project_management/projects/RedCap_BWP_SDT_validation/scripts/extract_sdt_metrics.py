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


def marker_count(text: str, *patterns: str) -> int:
    return sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in patterns)


def last_match(pattern: str, text: str) -> re.Match[str] | None:
    matches = list(re.finditer(pattern, text, re.MULTILINE))
    return matches[-1] if matches else None


def classify_success_counters(combined: str, scenario: str, marker_values: dict[str, str]) -> dict[str, int | str]:
    attempted = 1 if marker_values["ue_in_sync_seen"] == "1" or marker_values["rrc_inactive_marker_seen"] == "1" else 0
    fallback = 1 if marker_count(combined, r"threshold fallback", r"fallback to .*RA", r"RSRP threshold exceeded") else 0

    is_sdt_scenario = "sdt" in scenario.lower()
    if is_sdt_scenario:
        success = 1 if marker_values["cg_sdt_marker_seen"] == "1" else 0
    else:
        success = 1 if marker_values["rrc_resume_complete_seen"] == "1" else 0

    timeout = 1 if attempted and not success and not fallback else 0
    sdt_failure = 1 if attempted and is_sdt_scenario and not success and not fallback else 0
    probability = "NA" if attempted == 0 else f"{success / attempted:.6f}"
    return {
        "packet_attempt_count": attempted,
        "packet_success_count": success,
        "threshold_fallback_count": fallback,
        "timeout_failure_count": timeout,
        "sdt_failure_count": sdt_failure,
        "packet_transmission_success_probability": probability,
        "success_classifier": "cg_sdt_marker" if is_sdt_scenario else "rrc_resume_complete",
    }


def extract_metrics(gnb_log: Path, ue_log: Path | None, scenario: str) -> list[dict[str, str]]:
    gnb_text = gnb_log.read_text(errors="replace")
    ue_text = ue_log.read_text(errors="replace") if ue_log and ue_log.exists() else ""
    combined = f"{gnb_text}\n{ue_text}"

    rows: list[dict[str, str]] = []
    rntis = sorted(set(re.findall(r"UE RNTI ([0-9A-Fa-f]+) CU-UE-ID", gnb_text)))

    marker_values = {
        "ue_in_sync_seen": marker_seen(gnb_text, r"UE RNTI \S+ CU-UE-ID \S+ in-sync"),
        "rrc_inactive_marker_seen": marker_seen(combined, r"RRC_INACTIVE", r"RRC INACTIVE"),
        "rrc_resume_request_seen": marker_seen(combined, r"RRCResumeRequest"),
        "rrc_resume_complete_seen": marker_seen(combined, r"RRCResumeComplete"),
        "configured_grant_marker_seen": marker_seen(combined, r"configuredGrantConfig", r"configured grant"),
        "cg_sdt_marker_seen": marker_seen(combined, r"cg-SDT", r"CG SDT"),
    }

    add_metric(rows, scenario, "active_ue_count", str(len(rntis)))
    for metric, value in marker_values.items():
        add_metric(rows, scenario, metric, value)
    add_metric(rows, scenario, "cg_sdt_rx_candidate_count", str(marker_count(combined, r"cg-SDT PUSCH rx candidate")))
    add_metric(rows, scenario, "cg_sdt_tx_marker_count", str(marker_count(combined, r"cg-SDT.*PUSCH tx", r"autonomous CG PUSCH scheduled")))

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

    counters = classify_success_counters(combined, scenario, marker_values)
    for metric, value in counters.items():
        add_metric(rows, scenario, metric, str(value))

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
