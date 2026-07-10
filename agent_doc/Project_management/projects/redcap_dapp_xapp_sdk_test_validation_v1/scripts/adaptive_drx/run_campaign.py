#!/usr/bin/env python3
"""Plan or run one frozen 330-arrival adaptive C-DRX iPerf2 campaign."""

from __future__ import annotations

import argparse
import contextlib
import csv
import importlib
import json
import re
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


def iperf_command(server: str, row: dict[str, str], iperf: str = "iperf") -> list[str]:
    scheduled_seconds = int(row["scheduled_source_tx_time_us"]) / 1_000_000
    command = [
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
        "--txstart-time",
        f"{scheduled_seconds:.6f}",
        "--trip-times",
    ]
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
    parser.add_argument("--iperf", default="iperf", help="iPerf2 client executable")
    parser.add_argument("--command-plan", type=Path, required=True, help="JSONL command/evidence output")
    parser.add_argument("--metrics-csv", type=Path, help="scored correlation CSV; defaults beside --command-plan")
    parser.add_argument("--execute", action="store_true", help="execute instead of only writing the 330-command plan")
    parser.add_argument("--rnti", type=lambda value: int(value, 0), help="gNB C-RNTI used by the local Arm A control")
    parser.add_argument("--rrc-ue-id", type=lambda value: int(value, 0), help="E2SM-RC UE ID used by Arm B")
    parser.add_argument("--node-index", type=int, default=0, help="FlexRIC E2 node index for Arm B")
    parser.add_argument("--gnb-control-host", default="127.0.0.1")
    parser.add_argument("--gnb-control-port", type=int, default=9091)
    parser.add_argument("--runtime-log", type=Path, help="combined gNB/UE runtime log used for policy commit")
    parser.add_argument("--control-timeout-s", type=float, default=5.0)
    args = parser.parse_args(argv)

    campaign, rows = load_campaign(args.manifest, args.campaign_id)
    if len(rows) != ARRIVALS_PER_CAMPAIGN:
        raise ValueError(f"campaign requires exactly {ARRIVALS_PER_CAMPAIGN} arrivals")
    if args.execute and shutil.which(args.iperf) is None:
        print(f"[BLOCKED] iPerf2 executable not found: {args.iperf}")
        return 2
    if args.execute and args.runtime_log is None:
        print("[BLOCKED] --runtime-log is required to commit a policy window")
        return 2
    if args.execute and campaign["arm"] == "A" and args.rnti is None:
        print("[BLOCKED] --rnti is required for Arm A local RRC control")
        return 2
    if args.execute and campaign["arm"] == "B" and args.rrc_ue_id is None:
        print("[BLOCKED] --rrc-ue-id is required for Arm B E2SM-RC control")
        return 2
    if args.control_timeout_s <= 0:
        print("[BLOCKED] --control-timeout-s must be positive")
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
    if args.execute:
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
    failures = 0
    predictor = AdaptiveDrxPredictor() if campaign["arm"] == "B" else None
    profiles = {profile.profile_id: profile for profile in APPROVED_PROFILES}
    current_profile = profiles.get(str(campaign.get("initial_profile", {}).get("profile_id")), APPROVED_PROFILES[0])
    current_policy_version = 0
    schedule = {int(item["scored_window_id"]): item for item in campaign.get("profile_schedule", [])}
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
                ),
            )
            metrics_writer.writeheader()
        for row in rows:
            arrival_id = int(row["arrival_id"])
            control: dict[str, object] | None = None
            if arrival_id > WARMUP_ARRIVALS and (arrival_id - WARMUP_ARRIVALS - 1) % 30 == 0:
                window_id = (arrival_id - WARMUP_ARRIVALS - 1) // 30 + 1
                if campaign["arm"] == "A":
                    selected = schedule[window_id]
                    profile = DrxProfile(selected["profile_id"], selected["long_cycle_ms"], selected["on_duration_ms"])
                    planned_version = window_id
                    intent = None
                else:
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

                policy_version = planned_version
                accepted = True
                if args.execute:
                    try:
                        if campaign["arm"] == "A":
                            _send_local_drx_policy(
                                args.gnb_control_host,
                                args.gnb_control_port,
                                args.rnti,
                                policy_version,
                                profile,
                            )
                        else:
                            assert ric is not None and node_id is not None
                            policy_version = int(ric.control_drx_sm(node_id, args.rrc_ue_id, profile.long_cycle_ms))
                            accepted = policy_version > 0
                    except (OSError, RuntimeError) as error:
                        accepted = False
                        control = {"error": str(error)}
                    if accepted:
                        accepted = _wait_for_commit(
                            args.runtime_log,
                            log_start,
                            policy_version,
                            str(campaign["arm"]),
                            args.control_timeout_s,
                        )
                if predictor is not None:
                    predictor.resolve(accepted)
                intent_record = intent.to_dict() if intent is not None else {}
                if intent is not None:
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
                if not accepted:
                    stream.write(json.dumps({"campaign_id": campaign["id"], "control": control}, separators=(",", ":")) + "\n")
                    print(f"[PARTIAL] [RedCap DRX][control timeout] policy_version={policy_version}")
                    return 2
                current_policy_version = policy_version
                current_profile = profile

            command = iperf_command(args.server, row, args.iperf)
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
            if control is not None:
                record["control"] = control
            if args.execute:
                record["client_launch_time_us"] = time.time_ns() // 1000
                result = subprocess.run(command, capture_output=True, text=True, check=False)
                record.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
                failures += result.returncode != 0
                assert metrics_writer is not None
                metrics_writer.writerow(
                    {
                        "campaign_id": campaign["id"],
                        "arrival_id": arrival_id,
                        "scheduled_source_tx_time_us": row["scheduled_source_tx_time_us"],
                        "delivery_success": int(result.returncode == 0),
                        "policy_version": current_policy_version,
                        "profile_id": current_profile.profile_id,
                        "client_launch_time_us": record["client_launch_time_us"],
                        "iperf_returncode": result.returncode,
                    }
                )
            stream.write(json.dumps(record, separators=(",", ":")) + "\n")
            if failures:
                break
            if predictor is not None:
                predictor.observe(int(row["interval_us"]))

    if not args.execute:
        print(f"[PLAN] wrote {len(rows)} iPerf2 commands to {args.command_plan}")
        print("[BLOCKED] RFsim/iPerf2 execution and source receive timestamps are external evidence")
        return 2
    if failures:
        print(f"[PARTIAL] {failures}/{len(rows)} iPerf2 invocations failed; see {args.command_plan}")
        return 2
    print(f"[PASS] executed {len(rows)} scheduled iPerf2 invocations; raw evidence: {args.command_plan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
