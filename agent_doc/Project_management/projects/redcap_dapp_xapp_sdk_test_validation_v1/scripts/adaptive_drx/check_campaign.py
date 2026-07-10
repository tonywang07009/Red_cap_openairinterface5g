#!/usr/bin/env python3
"""Check scored adaptive C-DRX CSV correlation and required runtime markers."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from adaptive_drx import SCORED_ARRIVALS, WARMUP_ARRIVALS, file_sha256, find_campaign, read_trace


CONTROL_MARKERS = (
    "[RedCap DRX][xApp request]",
    "[RedCap DRX][E2 ACK]",
    "[RedCap DRX][dApp ACCEPT]",
    "[RedCap DRX][gNB applied]",
    "[RedCap DRX][RRC complete]",
)
TIMEOUT_MARKER = "[RedCap DRX][control timeout]"


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


def check(
    manifest_path: Path,
    campaign_id: str,
    metrics_path: Path,
    log_paths: list[Path],
) -> tuple[list[str], dict[str, int]]:
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

    if len(policy_versions) != 10 or any(count != 30 for count in policy_counts.values()):
        issues.append("expected ten policy versions correlated to exactly 30 scored arrivals each")
    if any(len(versions) != 1 for versions in window_versions.values()):
        issues.append("each scored 30-arrival trace window must use exactly one policy version")
    if any(len(profiles) != 1 for profiles in window_profiles.values()):
        issues.append("each scored 30-arrival trace window must use exactly one DRX profile")

    if campaign.get("arm") == "A":
        schedule = campaign.get("profile_schedule", [])
        expected = {int(item["scored_window_id"]): item["profile_id"] for item in schedule}
        for window_id, profiles in window_profiles.items():
            if profiles and next(iter(profiles)) != expected.get(window_id):
                issues.append(f"scored window {window_id}: Arm A profile does not match the seeded schedule")

    logs = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in log_paths)
    required_markers = campaign.get("required_markers", [])
    for marker in required_markers:
        if marker not in logs:
            issues.append(f"missing required runtime marker: {marker}")
    correlated_markers = CONTROL_MARKERS if campaign.get("arm") == "B" else ("[RedCap DRX][gNB applied]",)
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
    return issues, {"scored_records": len(scored), "delivery_success_count": success_count, "policy_versions": len(policy_versions)}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--metrics-csv", type=Path)
    parser.add_argument("--log", type=Path, action="append", default=[])
    args = parser.parse_args(argv)

    if args.metrics_csv is None or not args.log:
        print("[BLOCKED] provide --metrics-csv and at least one --log from the RFsim campaign")
        return 2
    missing = [path for path in [args.manifest, args.metrics_csv, *args.log] if not path.exists()]
    if missing:
        for path in missing:
            print(f"[BLOCKED] missing external evidence: {path}")
        return 2
    try:
        issues, summary = check(args.manifest, args.campaign_id, args.metrics_csv, args.log)
    except (KeyError, TypeError, ValueError, csv.Error, json.JSONDecodeError) as error:
        print(f"[FAIL] invalid campaign evidence: {error}")
        return 1
    print(json.dumps(summary, sort_keys=True))
    if issues:
        for issue in issues:
            print(f"[PARTIAL] {issue}")
        print("[PARTIAL] required RFsim correlation evidence is incomplete")
        return 2
    print("[PASS] 300 scored records, policy versions, source timestamps, and runtime markers correlate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
