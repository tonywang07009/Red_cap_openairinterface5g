#!/usr/bin/env python3
"""Plan or run one frozen 330-arrival adaptive C-DRX iPerf2 campaign."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Iterable

from adaptive_drx import ARRIVALS_PER_CAMPAIGN, file_sha256, find_campaign, read_trace


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


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--server", required=True, help="iPerf2 server address reachable from the UE-side client")
    parser.add_argument("--iperf", default="iperf", help="iPerf2 client executable")
    parser.add_argument("--command-plan", type=Path, required=True, help="JSONL command/evidence output")
    parser.add_argument("--execute", action="store_true", help="execute instead of only writing the 330-command plan")
    args = parser.parse_args(argv)

    campaign, rows = load_campaign(args.manifest, args.campaign_id)
    if len(rows) != ARRIVALS_PER_CAMPAIGN:
        raise ValueError(f"campaign requires exactly {ARRIVALS_PER_CAMPAIGN} arrivals")
    if args.execute and shutil.which(args.iperf) is None:
        print(f"[BLOCKED] iPerf2 executable not found: {args.iperf}")
        return 2
    if args.execute and int(rows[0]["scheduled_source_tx_time_us"]) <= time.time_ns() // 1000:
        print("[BLOCKED] first --txstart-time is not in the future; regenerate the trace with a future start epoch")
        return 2

    args.command_plan.parent.mkdir(parents=True, exist_ok=True)
    failures = 0
    with args.command_plan.open("w", encoding="utf-8") as stream:
        for row in rows:
            command = iperf_command(args.server, row, args.iperf)
            record: dict[str, object] = {
                "campaign_id": campaign["id"],
                "arm": campaign["arm"],
                "arrival_id": int(row["arrival_id"]),
                "direction": row["direction"],
                "traffic_source": row["traffic_source"],
                "scheduled_source_tx_time_us": int(row["scheduled_source_tx_time_us"]),
                "command": command,
                "executed": args.execute,
            }
            if args.execute:
                record["client_launch_time_us"] = time.time_ns() // 1000
                result = subprocess.run(command, capture_output=True, text=True, check=False)
                record.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
                failures += result.returncode != 0
            stream.write(json.dumps(record, separators=(",", ":")) + "\n")

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
