#!/usr/bin/env python3
"""Plan or run one frozen 330-arrival adaptive C-DRX iPerf2 campaign."""

from __future__ import annotations

import argparse
import contextlib
import csv
import importlib
import json
import re
import shlex
import shutil
import socket
import subprocess
import time
from pathlib import Path
from typing import Iterable

from adaptive_drx import (
    APPROVED_PROFILES,
    ARRIVALS_PER_CAMPAIGN,
    WARMUP_ARRIVALS,
    AdaptiveDrxPredictor,
    DrxProfile,
    file_sha256,
    find_campaign,
    read_trace,
)


IPERF2_UDP_REPORT_RE = re.compile(
    r"(?m)^.*?\b(?P<bitrate>[0-9]+(?:\.[0-9]+)?)\s+(?P<unit>[kKMG]?)bits/sec\s+"
    r"(?P<jitter>[0-9]+(?:\.[0-9]+)?)\s+ms\s+"
    r"(?P<lost>[0-9]+)\s*/\s*(?P<total>[0-9]+)\s+\((?P<loss>[0-9]+(?:\.[0-9]+)?)%\).*$"
)
UE_DRX_STATS_MARKER = "[RedCap DRX][UE stats]"


def parse_iperf2_udp_report(text: str) -> dict[str, float | int] | None:
    """Return metrics from the final iPerf2 UDP receiver/server report."""
    matches = list(IPERF2_UDP_REPORT_RE.finditer(text))
    if not matches:
        return None
    match = matches[-1]
    lost = int(match.group("lost"))
    total = int(match.group("total"))
    if total <= 0 or lost > total:
        return None
    unit_scale = {"": 1e-6, "K": 1e-3, "M": 1.0, "G": 1e3}
    unit = match.group("unit").upper()
    return {
        "burst_goodput_mbps": float(match.group("bitrate")) * unit_scale[unit],
        "udp_jitter_ms": float(match.group("jitter")),
        "udp_lost_packets": lost,
        "udp_total_packets": total,
        "udp_loss_percent": float(match.group("loss")),
    }


def iperf_delivery_success(returncode: int, report: dict[str, float | int] | None) -> bool:
    return (
        returncode == 0
        and report is not None
        and int(report["udp_total_packets"]) > int(report["udp_lost_packets"])
    )


def parse_ue_drx_stats(text: str) -> dict[str, int] | None:
    for line in reversed(text.splitlines()):
        if UE_DRX_STATS_MARKER not in line:
            continue
        observed = re.search(r"\bobserved_slots=(\d+)\b", line)
        active = re.search(r"\bactive_slots=(\d+)\b", line)
        if observed is None or active is None:
            return None
        values = {"observed_slots": int(observed.group(1)), "active_slots": int(active.group(1))}
        if values["active_slots"] > values["observed_slots"]:
            return None
        return values
    return None


def _query_ue_drx_stats(host: str, port: int, reset: bool) -> dict[str, int]:
    command = f"ciUE drx_stats{' reset' if reset else ''}\n"
    chunks: list[bytes] = []
    with socket.create_connection((host, port), timeout=2.0) as connection:
        connection.sendall(command.encode("ascii"))
        connection.shutdown(socket.SHUT_WR)
        while True:
            try:
                chunk = connection.recv(4096)
            except TimeoutError:
                break
            if not chunk:
                break
            chunks.append(chunk)
    response = b"".join(chunks).decode("utf-8", errors="replace")
    stats = parse_ue_drx_stats(response)
    if stats is None:
        raise RuntimeError(f"ciUE DRX stats marker missing from response: {response.strip()}")
    return stats


def iperf_command(
    server: str,
    row: dict[str, str],
    iperf: str = "iperf",
    traffic_prefix: Iterable[str] = (),
    bind_address: str | None = None,
) -> list[str]:
    scheduled_seconds = int(row["scheduled_source_tx_time_us"]) / 1_000_000
    command = [
        *traffic_prefix,
        iperf,
        "-c",
        server,
        "-u",
        "-b",
        "10000000",
        "-n",
        "32768",
        "-l",
        "1200",
    ]
    if bind_address is not None:
        command.extend(["-B", bind_address])
    command.extend(["--txstart-time", f"{scheduled_seconds:.6f}", "--trip-times"])
    if row["direction"] == "downlink":
        command.append("-R")
    return command


def load_campaign(manifest_path: Path, campaign_id: str) -> tuple[dict[str, object], list[dict[str, str]]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    campaign = find_campaign(manifest, campaign_id)
    trace_record = campaign.get("trace")
    if not isinstance(trace_record, dict):
        raise ValueError("campaign trace record is missing")
    trace_path = manifest_path.parent / str(trace_record["path"])
    if file_sha256(trace_path) != trace_record.get("sha256"):
        raise ValueError(f"trace checksum mismatch: {trace_path}")
    rows = read_trace(trace_path)
    if any(row["direction"] != campaign.get("direction") for row in rows):
        raise ValueError("trace direction does not match the selected campaign")
    return campaign, rows


def _versioned_marker(text: str, marker: str, policy_version: int, suffix: str = "") -> bool:
    pattern = rf"{re.escape(marker)}[^\n]*\bpolicy_version(?:=|\s+){policy_version}\b[^\n]*{re.escape(suffix)}"
    return re.search(pattern, text) is not None


def _wait_for_commit(log_path: Path, start_offset: int, policy_version: int, arm: str, timeout_s: float) -> bool:
    markers = ["[RedCap DRX][gNB applied]"]
    if arm == "B":
        markers[:0] = ["[RedCap DRX][xApp request]", "[RedCap DRX][E2 ACK]", "[RedCap DRX][dApp ACCEPT]"]
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if log_path.exists():
            with log_path.open("r", encoding="utf-8", errors="replace") as stream:
                stream.seek(start_offset)
                text = stream.read()
            if all(_versioned_marker(text, marker, policy_version) for marker in markers) and _versioned_marker(
                text, "[RedCap DRX][RRC complete]", policy_version, "outcome success"
            ):
                return True
        time.sleep(0.05)
    return False


def _send_local_drx_policy(
    host: str,
    port: int,
    rnti: int,
    policy_version: int,
    profile: DrxProfile,
) -> None:
    if policy_version == 0:
        command = f"ci bootstrap_drx_policy {profile.long_cycle_ms} {profile.on_duration_ms} 0x{rnti:04x}\n"
    else:
        command = (
            f"ci trigger_drx_policy {policy_version} {profile.long_cycle_ms} "
            f"{profile.on_duration_ms} 0 0 0x{rnti:04x}\n"
        )
    with socket.create_connection((host, port), timeout=2.0) as connection:
        connection.sendall(command.encode("ascii"))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--server", required=True, help="iPerf2 server address reachable from the UE-side client")
    parser.add_argument("--bind-address", help="UE PDU-session address used by iPerf2 -B, for example 10.0.0.2")
    parser.add_argument("--iperf", default="iperf", help="iPerf2 client executable")
    parser.add_argument(
        "--traffic-prefix",
        help="shell-like argv prefix for the UE traffic namespace, for example 'docker exec <UE container>'",
    )
    parser.add_argument("--command-plan", type=Path, required=True, help="JSONL command/evidence output")
    parser.add_argument("--metrics-csv", type=Path, help="scored correlation CSV; defaults beside --command-plan")
    parser.add_argument("--execute", action="store_true", help="execute instead of only writing the 330-command plan")
    parser.add_argument("--rnti", type=lambda value: int(value, 0), help="gNB C-RNTI used by the local Arm A control")
    parser.add_argument("--rrc-ue-id", type=lambda value: int(value, 0), help="E2SM-RC UE ID used by Arm B")
    parser.add_argument("--node-index", type=int, default=0, help="FlexRIC E2 node index for Arm B")
    parser.add_argument("--gnb-control-host", default="127.0.0.1")
    parser.add_argument("--gnb-control-port", type=int, default=9091)
    parser.add_argument("--ue-control-host", default="127.0.0.1")
    parser.add_argument("--ue-control-port", type=int, default=8091)
    parser.add_argument("--runtime-log", type=Path, help="combined gNB/UE runtime log used for policy commit")
    parser.add_argument("--summary-json", type=Path, help="campaign-level DRX metric summary; defaults beside --command-plan")
    parser.add_argument("--control-timeout-s", type=float, default=5.0)
    args = parser.parse_args(argv)

    try:
        traffic_prefix = shlex.split(args.traffic_prefix) if args.traffic_prefix else []
    except ValueError as error:
        print(f"[BLOCKED] invalid --traffic-prefix: {error}")
        return 2

    campaign, rows = load_campaign(args.manifest, args.campaign_id)
    if len(rows) != ARRIVALS_PER_CAMPAIGN:
        raise ValueError(f"campaign requires exactly {ARRIVALS_PER_CAMPAIGN} arrivals")
    command_executable = traffic_prefix[0] if traffic_prefix else args.iperf
    if args.execute and shutil.which(command_executable) is None:
        print(f"[BLOCKED] traffic command executable not found: {command_executable}")
        return 2
    if args.execute and args.runtime_log is None:
        print("[BLOCKED] --runtime-log is required to commit a policy window")
        return 2
    if args.execute and args.bind_address is None:
        print("[BLOCKED] --bind-address is required to keep traffic on the UE PDU-session route")
        return 2
    if args.execute and args.rnti is None:
        print("[BLOCKED] --rnti is required for the local DRX baseline")
        return 2
    if args.execute and campaign["arm"] == "B" and args.rrc_ue_id is None:
        print("[BLOCKED] --rrc-ue-id is required for Arm B E2SM-RC control")
        return 2
    if args.control_timeout_s <= 0:
        print("[BLOCKED] --control-timeout-s must be positive")
        return 2
    if not 1 <= args.ue_control_port <= 65535:
        print("[BLOCKED] --ue-control-port must be between 1 and 65535")
        return 2
    if args.execute and int(rows[0]["scheduled_source_tx_time_us"]) <= time.time_ns() // 1000:
        print("[BLOCKED] first --txstart-time is not in the future; regenerate the trace with a future start epoch")
        return 2

    ric = node_id = None
    if args.execute and campaign["arm"] == "B":
        try:
            ric = importlib.import_module("xapp_sdk")
            ric.init()
            nodes = ric.conn_e2_nodes()
            if args.node_index < 0 or args.node_index >= len(nodes):
                print(f"[BLOCKED] FlexRIC E2 node index is unavailable: {args.node_index}")
                return 2
            node_id = nodes[args.node_index].id
        except (ImportError, RuntimeError) as error:
            print(f"[BLOCKED] FlexRIC xapp_sdk is unavailable: {error}")
            return 2

    args.command_plan.parent.mkdir(parents=True, exist_ok=True)
    metrics_path = args.metrics_csv or args.command_plan.with_suffix(".metrics.csv")
    summary_path = args.summary_json or args.command_plan.with_suffix(".summary.json")
    if args.execute:
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
    failures = 0
    evidence_errors: list[str] = []
    completed_arrivals = 0
    warmup_stats: dict[str, int] | None = None
    scored_stats: dict[str, int] | None = None
    predictor = AdaptiveDrxPredictor() if campaign["arm"] == "B" else None
    profiles = {profile.profile_id: profile for profile in APPROVED_PROFILES}
    initial_profile = campaign.get("initial_profile")
    if not isinstance(initial_profile, dict) or str(initial_profile.get("profile_id")) not in profiles:
        raise ValueError("campaign initial_profile is missing or unsupported")
    current_profile = profiles[str(initial_profile["profile_id"])]
    current_policy_version = 0
    log_start = args.runtime_log.stat().st_size if args.runtime_log and args.runtime_log.exists() else 0
    with contextlib.ExitStack() as stack:
        stream = stack.enter_context(args.command_plan.open("w", encoding="utf-8"))
        metrics_writer = None
        if args.execute:
            metrics_stream = stack.enter_context(metrics_path.open("w", encoding="utf-8", newline=""))
            metrics_writer = csv.DictWriter(
                metrics_stream,
                fieldnames=(
                    "campaign_id",
                    "arrival_id",
                    "scheduled_source_tx_time_us",
                    "delivery_success",
                    "policy_version",
                    "profile_id",
                    "client_launch_time_us",
                    "iperf_returncode",
                    "burst_goodput_mbps",
                    "udp_jitter_ms",
                    "udp_lost_packets",
                    "udp_total_packets",
                    "udp_loss_percent",
                ),
            )
            metrics_writer.writeheader()
        baseline_control: dict[str, object] | None = None
        if campaign["arm"] in {"A", "B"}:
            policy_version = int(campaign.get("baseline_policy_version", 1)) if campaign["arm"] == "A" else 0
            accepted = True
            error = None
            if args.execute:
                try:
                    _send_local_drx_policy(
                        args.gnb_control_host,
                        args.gnb_control_port,
                        args.rnti,
                        policy_version,
                        current_profile,
                    )
                    accepted = _wait_for_commit(
                        args.runtime_log,
                        log_start,
                        policy_version,
                        "A",
                        args.control_timeout_s,
                    )
                except OSError as caught:
                    accepted = False
                    error = str(caught)
            baseline_control = {
                "phase": "pre_campaign" if campaign["arm"] == "A" else "pre_campaign_rollback_baseline",
                "policy_version": policy_version,
                "profile_id": current_profile.profile_id,
                "long_cycle_ms": current_profile.long_cycle_ms,
                "on_duration_ms": current_profile.on_duration_ms,
                "accepted": accepted,
            }
            if error is not None:
                baseline_control["error"] = error
            if not accepted:
                stream.write(json.dumps({"campaign_id": campaign["id"], "control": baseline_control}, separators=(",", ":")) + "\n")
                print(f"[PARTIAL] [RedCap DRX][control timeout] policy_version={policy_version}")
                return 2
            current_policy_version = policy_version
        for row in rows:
            arrival_id = int(row["arrival_id"])
            control: dict[str, object] | None = None
            if campaign["arm"] == "B" and arrival_id > WARMUP_ARRIVALS and (arrival_id - WARMUP_ARRIVALS - 1) % 30 == 0:
                window_id = (arrival_id - WARMUP_ARRIVALS - 1) // 30 + 1
                assert predictor is not None
                intent = predictor.propose(
                    campaign_id=str(campaign["id"]),
                    direction=str(campaign["direction"]),
                    window_id=window_id,
                    policy_version=window_id,
                    ric_request_id=window_id,
                    rnti=args.rrc_ue_id or 1,
                    previous_profile_id=current_profile.profile_id,
                )
                profile = profiles[intent.selected_profile_id]
                planned_version = intent.policy_version
                retained_samples = list(predictor.samples)

                policy_version = planned_version
                accepted = True
                control_error = None
                if args.execute:
                    try:
                        assert ric is not None and node_id is not None
                        policy_version = int(ric.control_drx_sm(node_id, args.rrc_ue_id, profile.long_cycle_ms))
                        accepted = policy_version > 0
                    except (OSError, RuntimeError) as error:
                        accepted = False
                        control_error = str(error)
                    if accepted:
                        accepted = _wait_for_commit(
                            args.runtime_log,
                            log_start,
                            policy_version,
                            str(campaign["arm"]),
                            args.control_timeout_s,
                        )
                predictor.resolve(accepted)
                intent_record = intent.to_dict()
                intent_record["e2sm_rc_request"]["ric_request_id"] = policy_version
                intent_record["e2sm_rc_request"]["policy_version"] = policy_version
                control = {
                    **intent_record,
                    "planned_policy_version": planned_version,
                    "policy_version": policy_version,
                    "profile_id": profile.profile_id,
                    "long_cycle_ms": profile.long_cycle_ms,
                    "on_duration_ms": profile.on_duration_ms,
                    "accepted": accepted,
                }
                if control_error is not None:
                    control["error"] = control_error
                if not accepted:
                    trace_record = campaign["trace"]
                    assert isinstance(trace_record, dict)
                    control["retained_window"] = {
                        "trace_sha256": trace_record["sha256"],
                        "arrival_id_start": arrival_id - 30,
                        "arrival_id_end": arrival_id - 1,
                        "intervals_us": retained_samples,
                    }
                    stream.write(json.dumps({"campaign_id": campaign["id"], "control": control}, separators=(",", ":")) + "\n")
                    print(f"[PARTIAL] [RedCap DRX][control timeout] policy_version={policy_version}")
                    return 2
                current_policy_version = policy_version
                current_profile = profile

            command = iperf_command(args.server, row, args.iperf, traffic_prefix, args.bind_address)
            record: dict[str, object] = {
                "campaign_id": campaign["id"],
                "arm": campaign["arm"],
                "arrival_id": arrival_id,
                "direction": row["direction"],
                "traffic_source": row["traffic_source"],
                "scheduled_source_tx_time_us": int(row["scheduled_source_tx_time_us"]),
                "policy_version": current_policy_version,
                "profile_id": current_profile.profile_id,
                "command": command,
                "executed": args.execute,
            }
            if arrival_id == 1 and baseline_control is not None:
                record["control"] = baseline_control
            elif control is not None:
                record["control"] = control
            if args.execute:
                record["client_launch_time_us"] = time.time_ns() // 1000
                result = subprocess.run(command, capture_output=True, text=True, check=False)
                record.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
                report = parse_iperf2_udp_report("\n".join((result.stdout, result.stderr)))
                delivery_success = iperf_delivery_success(result.returncode, report)
                if report is None:
                    record["iperf_metrics_error"] = "receiver_report_missing_or_invalid"
                    evidence_errors.append(f"arrival {arrival_id}: iPerf2 UDP receiver report missing or invalid")
                else:
                    record["iperf_metrics"] = report
                failures += not delivery_success
                assert metrics_writer is not None
                metrics_writer.writerow(
                    {
                        "campaign_id": campaign["id"],
                        "arrival_id": arrival_id,
                        "scheduled_source_tx_time_us": row["scheduled_source_tx_time_us"],
                        "delivery_success": int(delivery_success),
                        "policy_version": current_policy_version,
                        "profile_id": current_profile.profile_id,
                        "client_launch_time_us": record["client_launch_time_us"],
                        "iperf_returncode": result.returncode,
                        **(report or {}),
                    }
                )
                completed_arrivals = arrival_id
            stream.write(json.dumps(record, separators=(",", ":")) + "\n")
            if args.execute and arrival_id == WARMUP_ARRIVALS:
                try:
                    warmup_stats = _query_ue_drx_stats(args.ue_control_host, args.ue_control_port, True)
                except (OSError, RuntimeError) as error:
                    failures += 1
                    evidence_errors.append(f"warm-up UE DRX stats reset failed: {error}")
            if predictor is not None:
                predictor.observe(int(row["interval_us"]))

    if not args.execute:
        print(f"[PLAN] wrote {len(rows)} iPerf2 commands to {args.command_plan}")
        print("[BLOCKED] RFsim/iPerf2 execution and source receive timestamps are external evidence")
        return 2
    try:
        scored_stats = _query_ue_drx_stats(args.ue_control_host, args.ue_control_port, False)
    except (OSError, RuntimeError) as error:
        failures += 1
        evidence_errors.append(f"final UE DRX stats query failed: {error}")

    scored_stats_valid = warmup_stats is not None and scored_stats is not None
    observed_slots = scored_stats["observed_slots"] if scored_stats_valid else None
    active_slots = scored_stats["active_slots"] if scored_stats_valid else None
    active_ratio = active_slots / observed_slots if observed_slots else None
    summary = {
        "schema_version": 1,
        "campaign_id": campaign["id"],
        "completed_arrivals": completed_arrivals,
        "scored_arrivals_completed": max(0, completed_arrivals - WARMUP_ARRIVALS),
        "scored_stats_valid": scored_stats_valid,
        "warmup_observed_slots": warmup_stats["observed_slots"] if warmup_stats is not None else None,
        "warmup_active_slots": warmup_stats["active_slots"] if warmup_stats is not None else None,
        "drx_observed_slots": observed_slots,
        "drx_active_slots": active_slots,
        "drx_active_time_slot_ratio": active_ratio,
        "pdcch_monitoring_slot_ratio": active_ratio,
        "errors": evidence_errors,
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    if failures:
        print(f"[PARTIAL] {failures} traffic or metric evidence failures; see {args.command_plan}")
        print(f"[PARTIAL] campaign summary: {summary_path}")
        return 2
    print(f"[PASS] executed {len(rows)} scheduled iPerf2 invocations; raw evidence: {args.command_plan}")
    print(f"[PASS] campaign summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
