#!/usr/bin/env python3
"""Check scored adaptive C-DRX CSV correlation and required runtime markers."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from adaptive_drx import ARRIVALS_PER_CAMPAIGN, SCORED_ARRIVALS, WARMUP_ARRIVALS, file_sha256, find_campaign, read_trace


CONTROL_MARKERS = (
    "[RedCap DRX][xApp request]",
    "[RedCap DRX][E2 ACK]",
    "[RedCap DRX][dApp ACCEPT]",
    "[RedCap DRX][gNB applied]",
    "[RedCap DRX][RRC complete]",
)
TIMEOUT_MARKER = "[RedCap DRX][control timeout]"
REJECT_PATTERN = re.compile(r"\[RedCap DRX\]\[(?:dApp REJECT|gNB reject)\]")
IPERF_METRIC_COLUMNS = {
    "burst_goodput_mbps",
    "udp_jitter_ms",
    "udp_lost_packets",
    "udp_total_packets",
    "udp_loss_percent",
}


def _contains_version(text: str, marker: str, policy_version: str, suffix: str = "") -> bool:
    pattern = (
        rf"{re.escape(marker)}[^\n]*\bpolicy_version(?:=|\s+){re.escape(policy_version)}\b"
        rf"[^\n]*{re.escape(suffix)}"
    )
    return re.search(pattern, text) is not None


def _contains_applied_profile(text: str, policy_version: str, cycle_ms: int, on_duration_ms: int) -> bool:
    pattern = (
        rf"{re.escape('[RedCap DRX][gNB applied]')}[^\n]*\bpolicy_version(?:=|\s+){re.escape(policy_version)}\b"
        rf"[^\n]*\bcycle_ms(?:=|\s+){cycle_ms}\b[^\n]*\bon_duration_ms(?:=|\s+){on_duration_ms}\b"
    )
    return re.search(pattern, text) is not None


def _distribution(values_ms: list[float], prefix: str) -> dict[str, float]:
    ordered = sorted(values_ms)
    return {
        f"{prefix}_median_ms": round(statistics.median(ordered), 6),
        f"{prefix}_p95_ms": round(ordered[math.ceil(0.95 * len(ordered)) - 1], 6),
        f"{prefix}_max_ms": round(ordered[-1], 6),
    }


def _receive_evidence(
    receive_path: Path,
    campaign_id: str,
    trace: dict[int, dict[str, str]],
) -> tuple[list[str], dict[str, int | float]]:
    with receive_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    required = {"campaign_id", "arrival_id", "source_receive_time_us"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"receive CSV requires columns: {', '.join(sorted(required))}")

    issues: list[str] = []
    expected_ids = {arrival_id for arrival_id in trace if arrival_id > WARMUP_ARRIVALS}
    arrival_ids = [int(row["arrival_id"]) for row in rows]
    if len(rows) != SCORED_ARRIVALS or set(arrival_ids) != expected_ids:
        issues.append(f"receive CSV requires {SCORED_ARRIVALS} unique scored arrivals")

    seen: set[int] = set()
    latencies_ms: list[float] = []
    for row in rows:
        arrival_id = int(row["arrival_id"])
        expected = trace.get(arrival_id)
        if arrival_id in seen:
            issues.append(f"receive arrival {arrival_id}: duplicate record")
            continue
        seen.add(arrival_id)
        if row["campaign_id"] != campaign_id:
            issues.append(f"receive arrival {arrival_id}: campaign_id mismatch")
        if expected is None or arrival_id <= WARMUP_ARRIVALS:
            issues.append(f"receive arrival {arrival_id}: not a scored trace arrival")
            continue
        scheduled_us = int(expected["scheduled_source_tx_time_us"])
        receive_us = int(row["source_receive_time_us"])
        if receive_us < scheduled_us:
            issues.append(f"receive arrival {arrival_id}: timestamp precedes scheduled transmission")
            continue
        latencies_ms.append((receive_us - scheduled_us) / 1000)

    summary: dict[str, int | float] = {}
    if len(latencies_ms) == SCORED_ARRIVALS:
        summary.update(_distribution(latencies_ms, "scheduled_to_first_receive"))
    return issues, summary


def _iperf_evidence(
    scored: list[dict[str, str]],
    required: bool,
) -> tuple[list[str], dict[str, int | float]]:
    columns = set(scored[0]) if scored else set()
    missing = sorted(IPERF_METRIC_COLUMNS - columns)
    if missing:
        return ([f"metrics CSV missing frozen iPerf fields: {','.join(missing)}"] if required else []), {}

    invalid: list[int] = []
    goodput: list[float] = []
    jitter: list[float] = []
    loss: list[float] = []
    for row in scored:
        try:
            goodput_mbps = float(row["burst_goodput_mbps"])
            jitter_ms = float(row["udp_jitter_ms"])
            lost_packets = int(row["udp_lost_packets"])
            total_packets = int(row["udp_total_packets"])
            loss_percent = float(row["udp_loss_percent"])
        except (TypeError, ValueError):
            invalid.append(int(row["arrival_id"]))
            continue
        if (
            goodput_mbps < 0
            or jitter_ms < 0
            or total_packets <= 0
            or lost_packets < 0
            or lost_packets > total_packets
            or loss_percent < 0
            or loss_percent > 100
        ):
            invalid.append(int(row["arrival_id"]))
            continue
        goodput.append(goodput_mbps)
        jitter.append(jitter_ms)
        loss.append(loss_percent)

    issues = []
    if invalid:
        suffix = "..." if len(invalid) > 10 else ""
        issues.append(f"invalid or missing iPerf metrics for arrivals: {','.join(map(str, invalid[:10]))}{suffix}")
    summary: dict[str, int | float] = {}
    if len(goodput) == SCORED_ARRIVALS:
        summary.update(
            {
                "burst_goodput_mean_mbps": round(statistics.fmean(goodput), 6),
                "udp_jitter_mean_ms": round(statistics.fmean(jitter), 6),
                "udp_loss_mean_percent": round(statistics.fmean(loss), 6),
            }
        )
    return issues, summary


def _campaign_summary_evidence(path: Path, campaign_id: str) -> tuple[list[str], dict[str, int | float]]:
    record = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "campaign_id",
        "completed_arrivals",
        "scored_arrivals_completed",
        "scored_stats_valid",
        "drx_observed_slots",
        "drx_active_slots",
        "drx_active_time_slot_ratio",
        "pdcch_monitoring_slot_ratio",
    }
    missing = sorted(required - set(record))
    if missing:
        raise ValueError(f"campaign summary missing fields: {','.join(missing)}")

    issues: list[str] = []
    if record["campaign_id"] != campaign_id:
        issues.append("campaign summary campaign_id mismatch")
    if record["completed_arrivals"] != ARRIVALS_PER_CAMPAIGN or record["scored_arrivals_completed"] != SCORED_ARRIVALS:
        issues.append("campaign summary does not cover 330 arrivals and 300 scored arrivals")
    if record["scored_stats_valid"] is not True:
        issues.append("campaign summary UE scored-slot reset/query evidence is invalid")

    try:
        observed_slots = int(record["drx_observed_slots"])
        active_slots = int(record["drx_active_slots"])
        active_ratio = float(record["drx_active_time_slot_ratio"])
        monitoring_ratio = float(record["pdcch_monitoring_slot_ratio"])
    except (TypeError, ValueError) as error:
        raise ValueError(f"campaign summary DRX metrics are not numeric: {error}") from error
    expected_ratio = active_slots / observed_slots if observed_slots > 0 else -1.0
    if observed_slots <= 0 or active_slots < 0 or active_slots > observed_slots:
        issues.append("campaign summary UE slot counters are invalid")
    if not 0 <= active_ratio <= 1 or abs(active_ratio - expected_ratio) > 1e-6:
        issues.append("campaign summary DRX Active-Time ratio does not match its counters")
    if not 0 <= monitoring_ratio <= 1 or abs(monitoring_ratio - active_ratio) > 1e-6:
        issues.append("campaign summary PDCCH monitoring ratio does not match the v1 Active-Time proxy")

    return issues, {
        "drx_observed_slots": observed_slots,
        "drx_active_slots": active_slots,
        "drx_active_time_slot_ratio": active_ratio,
        "pdcch_monitoring_slot_ratio": monitoring_ratio,
    }


def _log_evidence(logs: str, policy_versions: set[str], rnti: int) -> tuple[list[str], dict[str, int | float]]:
    issues: list[str] = []
    summary: dict[str, int | float] = {}
    timestamp_pattern = re.compile(r"(\d+(?:\.\d+)?)\s+\[")
    version_pattern = re.compile(r"\bpolicy_version(?:=|\s+)(\d+)\b")
    rnti_pattern = re.compile(rf"\bRNTI\s+(?:0x)?{rnti:04x}\b", re.IGNORECASE)
    staged: dict[str, list[float]] = defaultdict(list)
    completed: dict[str, list[float]] = defaultdict(list)
    for line in logs.splitlines():
        timestamp = timestamp_pattern.search(line)
        version = version_pattern.search(line)
        if timestamp is None or version is None or rnti_pattern.search(line) is None:
            continue
        if "[RedCap DRX][gNB staged]" in line:
            staged[version.group(1)].append(float(timestamp.group(1)))
        elif "[RedCap DRX][RRC complete]" in line and "outcome success" in line:
            completed[version.group(1)].append(float(timestamp.group(1)))

    apply_latencies_ms: list[float] = []
    missing_versions: list[str] = []
    for version in sorted(policy_versions, key=int):
        latency = None
        for completion in sorted(completed[version]):
            preceding = [timestamp for timestamp in staged[version] if timestamp <= completion]
            if preceding:
                latency = (completion - max(preceding)) * 1000
                break
        if latency is None:
            missing_versions.append(version)
        else:
            apply_latencies_ms.append(latency)
    if missing_versions:
        issues.append(f"missing timestamped staged-to-RRC-complete evidence for policy versions: {','.join(missing_versions)}")
    if apply_latencies_ms:
        summary["rrc_reconfiguration_count"] = len(apply_latencies_ms)
        summary.update(_distribution(apply_latencies_ms, "policy_apply_latency"))

    round_pattern = re.compile(
        rf"\bUE\s+{rnti:04x}:\s+(?P<link>[du]lsch)_rounds\s+(?P<rounds>\d+(?:/\d+)*)",
        re.IGNORECASE,
    )
    snapshots: dict[str, list[list[int]]] = defaultdict(list)
    for match in round_pattern.finditer(logs):
        snapshots[match.group("link").lower()].append([int(value) for value in match.group("rounds").split("/")])
    for link in ("dlsch", "ulsch"):
        if len(snapshots[link]) < 2:
            issues.append(f"missing first/last RNTI {rnti:04x} {link}_rounds snapshots")
            continue
        delta = sum(snapshots[link][-1][1:]) - sum(snapshots[link][0][1:])
        if delta < 0:
            issues.append(f"RNTI {rnti:04x} {link}_rounds counter reset during campaign")
            continue
        metric = "dl_harq_retransmission_count" if link == "dlsch" else "ul_harq_retransmission_count"
        summary[metric] = delta
    return issues, summary


def check(
    manifest_path: Path,
    campaign_id: str,
    metrics_path: Path,
    log_paths: list[Path],
    receive_path: Path | None = None,
    summary_path: Path | None = None,
    rnti: int | None = None,
    require_frozen_metrics: bool = False,
) -> tuple[list[str], dict[str, int | float]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    campaign = find_campaign(manifest, campaign_id)
    trace_record = campaign.get("trace")
    if not isinstance(trace_record, dict):
        raise ValueError("campaign trace record is missing")
    trace_path = manifest_path.parent / str(trace_record["path"])
    if file_sha256(trace_path) != trace_record.get("sha256"):
        raise ValueError(f"trace checksum mismatch: {trace_path}")
    trace = {int(row["arrival_id"]): row for row in read_trace(trace_path)}

    with metrics_path.open(encoding="utf-8", newline="") as stream:
        metrics = list(csv.DictReader(stream))
    required_columns = {
        "campaign_id",
        "arrival_id",
        "scheduled_source_tx_time_us",
        "delivery_success",
        "policy_version",
        "profile_id",
    }
    if not metrics or not required_columns.issubset(metrics[0]):
        raise ValueError(f"metrics CSV requires columns: {', '.join(sorted(required_columns))}")

    issues: list[str] = []
    scored = [row for row in metrics if int(row["arrival_id"]) > WARMUP_ARRIVALS]
    arrival_ids = [int(row["arrival_id"]) for row in scored]
    if len(scored) != SCORED_ARRIVALS or len(set(arrival_ids)) != SCORED_ARRIVALS:
        issues.append(f"expected {SCORED_ARRIVALS} unique scored records, got {len(set(arrival_ids))}")

    success_count = 0
    policy_versions: set[str] = set()
    policy_counts: Counter[str] = Counter()
    window_versions: dict[int, set[str]] = defaultdict(set)
    window_profiles: dict[int, set[str]] = defaultdict(set)
    profiles_by_version: dict[str, set[str]] = defaultdict(set)
    approved_profiles = {
        str(profile["profile_id"]): (int(profile["long_cycle_ms"]), int(profile["on_duration_ms"]))
        for profile in manifest.get("approved_profiles", [])
    }
    for row in scored:
        arrival_id = int(row["arrival_id"])
        expected = trace.get(arrival_id)
        if row["campaign_id"] != campaign_id:
            issues.append(f"arrival {arrival_id}: campaign_id mismatch")
        if expected is None or row["scheduled_source_tx_time_us"] != expected["scheduled_source_tx_time_us"]:
            issues.append(f"arrival {arrival_id}: source timestamp does not correlate with the trace")
        if not row["policy_version"]:
            issues.append(f"arrival {arrival_id}: missing policy_version")
        else:
            policy_versions.add(row["policy_version"])
            policy_counts[row["policy_version"]] += 1
            window_versions[(arrival_id - 1) // 30].add(row["policy_version"])
        if not row["profile_id"]:
            issues.append(f"arrival {arrival_id}: missing profile_id")
        else:
            window_profiles[(arrival_id - 1) // 30].add(row["profile_id"])
            if row["profile_id"] not in approved_profiles:
                issues.append(f"arrival {arrival_id}: unsupported profile_id {row['profile_id']}")
            if row["policy_version"]:
                profiles_by_version[row["policy_version"]].add(row["profile_id"])
        success_count += row["delivery_success"].strip().lower() in {"1", "true", "yes", "pass"}

    if campaign.get("arm") == "A":
        if policy_versions != {"1"} or policy_counts["1"] != SCORED_ARRIVALS:
            issues.append("expected Arm A policy_version 1 correlated to all 300 scored arrivals")
    elif len(policy_versions) != 10 or any(count != 30 for count in policy_counts.values()):
        issues.append("expected ten policy versions correlated to exactly 30 scored arrivals each")
    if any(len(versions) != 1 for versions in window_versions.values()):
        issues.append("each scored 30-arrival trace window must use exactly one policy version")
    if any(len(profiles) != 1 for profiles in window_profiles.values()):
        issues.append("each scored 30-arrival trace window must use exactly one DRX profile")

    if campaign.get("arm") == "A":
        if any(profiles != {"drx-320-10"} for profiles in window_profiles.values()):
            issues.append("Arm A must use fixed profile drx-320-10 for all scored arrivals")

    logs = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in log_paths)
    required_markers = campaign.get("required_markers", [])
    for marker in required_markers:
        if marker not in logs:
            issues.append(f"missing required runtime marker: {marker}")
    correlated_markers = (
        CONTROL_MARKERS
        if campaign.get("arm") == "B"
        else ("[RedCap DRX][gNB applied]", "[RedCap DRX][RRC complete]")
    )
    for version in sorted(policy_versions):
        for marker in correlated_markers:
            suffix = "outcome success" if marker == "[RedCap DRX][RRC complete]" else ""
            if not _contains_version(logs, marker, version, suffix):
                issues.append(f"{TIMEOUT_MARKER} policy_version {version}: missing marker {marker}")
        version_profiles = profiles_by_version[version]
        if len(version_profiles) == 1:
            profile_id = next(iter(version_profiles))
            if profile_id in approved_profiles:
                cycle_ms, on_duration_ms = approved_profiles[profile_id]
                if not _contains_applied_profile(logs, version, cycle_ms, on_duration_ms):
                    issues.append(
                        f"policy_version {version}: gNB applied profile does not match {profile_id}"
                    )
    summary: dict[str, int | float] = {
        "scored_records": len(scored),
        "delivery_success_count": success_count,
        "policy_versions": len(policy_versions),
        "policy_reject_count": len(REJECT_PATTERN.findall(logs)),
        "rollback_count": logs.count("[RedCap DRX][rollback]"),
        "rrc_reconfiguration_timeout_count": logs.count(TIMEOUT_MARKER),
    }
    iperf_issues, iperf_summary = _iperf_evidence(scored, require_frozen_metrics)
    issues.extend(iperf_issues)
    summary.update(iperf_summary)
    if receive_path is not None:
        receive_issues, receive_summary = _receive_evidence(receive_path, campaign_id, trace)
        issues.extend(receive_issues)
        summary.update(receive_summary)
    if summary_path is not None:
        summary_issues, active_time_summary = _campaign_summary_evidence(summary_path, campaign_id)
        issues.extend(summary_issues)
        summary.update(active_time_summary)
    if rnti is not None:
        log_issues, log_summary = _log_evidence(logs, policy_versions, rnti)
        issues.extend(log_issues)
        summary.update(log_summary)
    return issues, summary


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--metrics-csv", type=Path)
    parser.add_argument("--receive-csv", type=Path)
    parser.add_argument("--summary-json", type=Path)
    parser.add_argument("--rnti", type=lambda value: int(value, 0))
    parser.add_argument("--log", type=Path, action="append", default=[])
    args = parser.parse_args(argv)

    if args.metrics_csv is None or not args.log:
        print("[BLOCKED] provide --metrics-csv and at least one --log from the RFsim campaign")
        return 2
    supplied_paths = [args.manifest, args.metrics_csv, *args.log]
    if args.receive_csv is not None:
        supplied_paths.append(args.receive_csv)
    if args.summary_json is not None:
        supplied_paths.append(args.summary_json)
    missing = [path for path in supplied_paths if not path.exists()]
    if missing:
        for path in missing:
            print(f"[BLOCKED] missing external evidence: {path}")
        return 2
    try:
        issues, summary = check(
            args.manifest,
            args.campaign_id,
            args.metrics_csv,
            args.log,
            receive_path=args.receive_csv,
            summary_path=args.summary_json,
            rnti=args.rnti,
            require_frozen_metrics=True,
        )
    except (KeyError, TypeError, ValueError, csv.Error, json.JSONDecodeError) as error:
        print(f"[FAIL] invalid campaign evidence: {error}")
        return 1
    if args.receive_csv is None:
        issues.append("missing optional evidence: --receive-csv")
    if args.summary_json is None:
        issues.append("missing optional evidence: --summary-json for UE Active-Time ratios")
    if args.rnti is None:
        issues.append("missing optional evidence: --rnti for apply latency and HARQ deltas")
    print(json.dumps(summary, sort_keys=True))
    if issues:
        for issue in issues:
            print(f"[PARTIAL] {issue}")
        print("[PARTIAL] required RFsim correlation evidence is incomplete")
        return 2
    print("[PASS] traffic, receive timestamps, Active-Time, policy apply latency, HARQ deltas, and runtime markers correlate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
