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


def line_timestamp(line: str) -> float | None:
    match = re.match(r"^(?P<ts>\d+\.\d+)\s+\[[^\]]+\]", line)
    return float(match.group("ts")) if match else None


def text_timestamps(text: str) -> list[float]:
    return [ts for line in text.splitlines() if (ts := line_timestamp(line)) is not None]


def add_numeric_metric(rows: list[dict[str, str]], scenario: str, metric: str, value: float | int, precision: int = 6) -> None:
    if isinstance(value, int):
        formatted = str(value)
    else:
        formatted = f"{value:.{precision}f}"
    add_metric(rows, scenario, metric, formatted)


def extract_bwp_size_metrics(rows: list[dict[str, str]], scenario: str, gnb_text: str) -> tuple[int | None, int | None]:
    default_size = None
    dedicated_size = None

    default_match = last_match(r"RedCap initial DL BWP configured: start=\d+ size=(\d+)", gnb_text)
    if not default_match:
        default_match = last_match(r"initialDLBWPSize_r17:\s*(\d+)", gnb_text)
    if default_match:
        default_size = int(default_match.group(1))
        add_metric(rows, scenario, "default_bwp_size_prb", str(default_size))

    dedicated_matches = list(re.finditer(r"BWP\s+(\d+),\s+start PRB \d+ size (\d+)", gnb_text))
    for match in dedicated_matches:
        if int(match.group(1)) != 0:
            dedicated_size = int(match.group(2))
    if dedicated_size is None:
        carrier_match = last_match(r"dl_carrierBandwidth:\s*(\d+)", gnb_text)
        if carrier_match:
            dedicated_size = int(carrier_match.group(1))
    if dedicated_size:
        add_metric(rows, scenario, "dedicated_bwp_size_prb", str(dedicated_size))

    return default_size, dedicated_size


def extract_bwp_timeline_metrics(rows: list[dict[str, str]], scenario: str, gnb_text: str) -> None:
    timestamps = text_timestamps(gnb_text)
    if not timestamps:
        return

    first_ts = min(timestamps)
    last_ts = max(timestamps)
    duration_s = max(last_ts - first_ts, 0.0)
    add_numeric_metric(rows, scenario, "log_duration_ms", duration_s * 1000)

    switches: list[tuple[float, int]] = []
    for line in gnb_text.splitlines():
        ts = line_timestamp(line)
        if ts is None:
            continue
        match = re.search(r"Switching to DL-BWP\s+(-?\d+)", line)
        if match:
            switches.append((ts, int(match.group(1))))

    if not switches:
        return

    add_metric(rows, scenario, "bwp_switch_event_count", str(len(switches)))
    residency_by_bwp: dict[int, float] = {}
    for index, (start_ts, bwp_id) in enumerate(switches):
        end_ts = switches[index + 1][0] if index + 1 < len(switches) else last_ts
        residency_by_bwp[bwp_id] = residency_by_bwp.get(bwp_id, 0.0) + max(end_ts - start_ts, 0.0)

    measured_total_s = sum(residency_by_bwp.values())
    if measured_total_s <= 0:
        return

    default_s = residency_by_bwp.get(0, 0.0)
    dedicated_s = sum(duration for bwp_id, duration in residency_by_bwp.items() if bwp_id != 0)
    default_ratio = default_s / measured_total_s * 100.0
    dedicated_ratio = dedicated_s / measured_total_s * 100.0

    add_numeric_metric(rows, scenario, "default_bwp_residency_ms", default_s * 1000)
    add_numeric_metric(rows, scenario, "dedicated_bwp_residency_ms", dedicated_s * 1000)
    add_numeric_metric(rows, scenario, "default_bwp_ratio_percent", default_ratio)
    add_numeric_metric(rows, scenario, "dedicated_bwp_ratio_percent", dedicated_ratio)


def extract_bwp_delay_metrics(rows: list[dict[str, str]], scenario: str, gnb_text: str) -> None:
    reconfig_ts = None
    for line in gnb_text.splitlines():
        if "[RedCap BWP][gNB reconfiguration]" in line:
            reconfig_ts = line_timestamp(line)
    if reconfig_ts is None:
        return

    switch_apply_ts = None
    first_sdu_ts = None
    for line in gnb_text.splitlines():
        ts = line_timestamp(line)
        if ts is None or ts < reconfig_ts:
            continue
        if switch_apply_ts is None and "Switching to DL-BWP" in line:
            switch_apply_ts = ts
        if first_sdu_ts is None and re.search(r"received SRB1 SDU|MAC:\s+TX\s+\d+\s+RX\s+\d+\s+bytes", line):
            first_sdu_ts = ts
        if switch_apply_ts is not None and first_sdu_ts is not None:
            break

    if switch_apply_ts is not None:
        add_numeric_metric(rows, scenario, "bwp_switch_apply_delay_ms", (switch_apply_ts - reconfig_ts) * 1000)
    if first_sdu_ts is not None:
        # Local proxy for PDU scheduling delay: first post-switch scheduled SDU observed in the RFsim gNB log.
        add_numeric_metric(rows, scenario, "pdu_scheduling_delay_ms", (first_sdu_ts - reconfig_ts) * 1000)


def extract_bwp_estimated_power_metric(
    rows: list[dict[str, str]],
    scenario: str,
    gnb_text: str,
    default_size: int | None,
    dedicated_size: int | None,
) -> None:
    if not default_size or not dedicated_size or dedicated_size <= 0:
        return
    ratio_row = next((row for row in rows if row["metric"] == "default_bwp_ratio_percent"), None)
    if ratio_row is None:
        return
    default_ratio = float(ratio_row["local_value"]) / 100.0
    power_saving = default_ratio * max(0.0, 1.0 - (default_size / dedicated_size)) * 100.0
    add_numeric_metric(rows, scenario, "power_saving_percent", power_saving)
    add_metric(rows, scenario, "power_saving_estimation_model", "default_ratio_x_prb_delta")


def extract_throughput_metric(rows: list[dict[str, str]], scenario: str, gnb_text: str) -> None:
    timestamps = text_timestamps(gnb_text)
    if not timestamps:
        return
    duration_s = max(max(timestamps) - min(timestamps), 0.0)
    mac = last_match(r"UE\s+\S+:\s+MAC:\s+TX\s+(\d+)\s+RX\s+(\d+)\s+bytes", gnb_text)
    if not mac or duration_s <= 0:
        return
    tx_bytes, rx_bytes = (int(value) for value in mac.groups())
    add_numeric_metric(rows, scenario, "gnb_mac_total_throughput_mbps", (tx_bytes + rx_bytes) * 8.0 / duration_s / 1_000_000)
    add_numeric_metric(rows, scenario, "gnb_mac_rx_throughput_mbps", rx_bytes * 8.0 / duration_s / 1_000_000)


def extract_metrics(
    gnb_log: Path,
    ric_log: Path | None,
    xapp_log: Path | None,
    ue_log: Path | None,
    scenario: str,
) -> list[dict[str, str]]:
    gnb_text = gnb_log.read_text(errors="replace")
    ric_text = ric_log.read_text(errors="replace") if ric_log and ric_log.exists() else ""
    xapp_text = xapp_log.read_text(errors="replace") if xapp_log and xapp_log.exists() else ""
    ue_text = ue_log.read_text(errors="replace") if ue_log and ue_log.exists() else ""

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
    extract_throughput_metric(rows, scenario, gnb_text)

    in_sync = "1" if re.search(r"UE RNTI \S+ CU-UE-ID \S+ in-sync", gnb_text) else "0"
    add_metric(rows, scenario, "ue_in_sync_seen", in_sync)

    bwp_reconfigs = list(re.finditer(r"\[RedCap BWP\]\[gNB reconfiguration\].*?new_bwp_id\s+(-?\d+)", gnb_text))
    add_metric(rows, scenario, "bwp_gnb_reconfiguration_count", str(len(bwp_reconfigs)))
    if bwp_reconfigs:
        add_metric(rows, scenario, "bwp_gnb_reconfiguration_last_new_bwp_id", bwp_reconfigs[-1].group(1))

    bwp_interrupts = list(re.finditer(r"\[RedCap BWP\]\[gNB interrupt\].*?slots\s+(\d+)", gnb_text))
    add_metric(rows, scenario, "bwp_gnb_interrupt_count", str(len(bwp_interrupts)))
    if bwp_interrupts:
        add_metric(rows, scenario, "bwp_gnb_interrupt_last_slots", bwp_interrupts[-1].group(1))

    ue_ra_ops = list(
        re.finditer(
            r"\[RedCap BWP\]\[UE RA\].*?old_dl_bwp_id\s+(-?\d+).*?old_ul_bwp_id\s+(-?\d+).*?"
            r"new_dl_bwp_id\s+(-?\d+).*?new_ul_bwp_id\s+(-?\d+)",
            ue_text,
        )
    )
    add_metric(rows, scenario, "bwp_ue_ra_operation_count", str(len(ue_ra_ops)))
    add_metric(
        rows,
        scenario,
        "bwp_ue_ra_bwp_change_count",
        str(
            sum(1 for match in ue_ra_ops if match.group(1) != match.group(3) or match.group(2) != match.group(4))
        ),
    )
    gap_seen = "1" if "bwp_inactivity_timer=not_implemented" in ue_text else "0"
    add_metric(rows, scenario, "bwp_inactivity_timer_gap_seen", gap_seen)

    default_size, dedicated_size = extract_bwp_size_metrics(rows, scenario, gnb_text)
    extract_bwp_timeline_metrics(rows, scenario, gnb_text)
    extract_bwp_delay_metrics(rows, scenario, gnb_text)
    extract_bwp_estimated_power_metric(rows, scenario, gnb_text, default_size, dedicated_size)

    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gnb-log", required=True, type=Path)
    parser.add_argument("--ric-log", type=Path)
    parser.add_argument("--xapp-log", type=Path)
    parser.add_argument("--ue-log", type=Path)
    parser.add_argument("--scenario", default="local_rfsim_ue2_minimal")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rows = extract_metrics(args.gnb_log, args.ric_log, args.xapp_log, args.ue_log, args.scenario)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
