#!/usr/bin/env python3
"""P3 RFsim DOE runner and smoke-log parser.

This tool keeps P3 data collection reproducible:
- read the P2 DOE matrix,
- print or execute the matching smoke-validation command,
- parse RFsim smoke logs into the P3 metric CSV schema.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from statistics import mean


CSV_COLUMNS = [
    "run_id",
    "status",
    "hard_pass",
    "pass_with_gap",
    "blocked",
    "invalid",
    "total_ues",
    "sample_ues",
    "iperf_rate",
    "receiver_mbps",
    "sender_mbps",
    "jitter_ms",
    "udp_loss_percent",
    "ping_loss_percent",
    "rtt_min_ms",
    "rtt_avg_ms",
    "rtt_max_ms",
    "attach_success_ratio",
    "pdu_success_ratio",
    "tunnel_success_ratio",
    "forward_ping_success_ratio",
    "gnb_restart_count",
    "failure_count",
    "raw_log_dir",
    "iperf_log_paths",
    "ping_log_paths",
    "trend_note",
    "failure_category",
    "improvement_direction",
]

SUMMARY_RE = re.compile(r"^\[SUMMARY\]\s+(?P<body>.*)$")
KEY_VALUE_RE = re.compile(r"(?P<key>[A-Za-z0-9_]+)=(?P<value>[^ ]+)")
PREFIX_RE = re.compile(r"mmtc_smoke_(?P<prefix>\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_")
IPERF_RE = re.compile(
    r"^\[.*?\]\s+"
    r"(?P<interval>\d+(?:\.\d+)?-\d+(?:\.\d+)?)\s+sec\s+"
    r"(?P<transfer>[0-9.]+)\s+\S+Bytes\s+"
    r"(?P<rate>[0-9.]+)\s+(?P<unit>[KMG]bits/sec)"
    r"(?:\s+(?P<jitter>[0-9.]+)\s+ms\s+"
    r"(?P<lost>\d+)/(?P<total>\d+)\s+\((?P<loss>[0-9.]+)%\))?\s+"
    r"(?P<side>sender|receiver)\s*$"
)
PING_LOSS_RE = re.compile(
    r"(?P<tx>\d+)\s+packets transmitted,\s+(?P<rx>\d+)\s+received,\s+(?P<loss>[0-9.]+)% packet loss"
)
PING_RTT_RE = re.compile(
    r"rtt min/avg/max/(?:mdev|stddev)\s+=\s+"
    r"(?P<min>[0-9.]+)/(?P<avg>[0-9.]+)/(?P<max>[0-9.]+)/(?P<mdev>[0-9.]+)\s+ms"
)


def find_repo_root(start: Path) -> Path:
    for path in [start, *start.parents]:
        if (path / "ci-scripts" / "redcap_mmtc_smoke_validation.sh").is_file():
            return path
    raise SystemExit("Could not locate repo root from script path")


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_DIR = SCRIPT_PATH.parents[2]
REPO_ROOT = find_repo_root(SCRIPT_PATH)
DEFAULT_MATRIX = PROJECT_DIR / "analysis" / "data" / "p2_taguchi_l9_run_matrix.csv"
DEFAULT_OUTPUT = PROJECT_DIR / "analysis" / "data" / "p3_runtime_metrics.csv"
DEFAULT_FAILURE_LOG = PROJECT_DIR / "analysis" / "data" / "p3_failure_to_improvement_log.csv"
DEFAULT_RAW_ROOT = PROJECT_DIR / "analysis" / "data" / "p3_raw"
SMOKE_SCRIPT = REPO_ROOT / "ci-scripts" / "redcap_mmtc_smoke_validation.sh"
COMPILER_LOG_DIR = REPO_ROOT / "test_log" / "compiler_logs"


def read_matrix(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def find_run(rows: list[dict[str, str]], run_id: str) -> dict[str, str]:
    for row in rows:
        if row["run_id"] == run_id:
            return row
    raise SystemExit(f"Unknown run_id: {run_id}")


def row_env(row: dict[str, str]) -> dict[str, str]:
    return {
        "MMTC_TOTAL_UES": row["total_ues"],
        "MMTC_SAMPLE_UES": row["sample_ues"],
        "MMTC_IPERF_SAMPLE_UES": row["iperf_sample_ues"],
        "MMTC_IPERF_ENABLE": "1",
        "MMTC_IPERF_UDP": row["iperf_udp"],
        "MMTC_IPERF_RATE": row["iperf_rate"],
        "MMTC_IPERF_DURATION": row["iperf_duration_s"],
        "MMTC_FORWARD_PING_MODE": row["forward_ping_mode"],
        "MMTC_RUN_REVERSE_PING": row["run_reverse_ping"],
        "MMTC_PUCCH_COMMON_FALLBACK_BWP0": "1",
    }


def shell_command(row: dict[str, str]) -> str:
    env = row_env(row)
    parts = [f"{key}={shlex.quote(value)}" for key, value in env.items()]
    parts.extend(["bash", shlex.quote(str(SMOKE_SCRIPT.relative_to(REPO_ROOT)))])
    return " ".join(parts)


def list_runs(rows: list[dict[str, str]]) -> None:
    for row in rows:
        print(
            f"{row['run_id']:12s} total_ues={row['total_ues']:>2s} "
            f"sample_ues={row['sample_ues']!r} rate={row['iperf_rate']} duration={row['iperf_duration_s']}s"
        )


def run_smoke(row: dict[str, str], raw_root: Path) -> tuple[int, Path, str | None]:
    run_id = row["run_id"]
    timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    raw_dir = raw_root / run_id / timestamp
    raw_dir.mkdir(parents=True, exist_ok=True)
    stdout_log = raw_dir / "smoke_stdout.log"
    command_log = raw_dir / "command.env"
    manifest = raw_dir / "smoke_log_manifest.txt"

    env = os.environ.copy()
    env.update(row_env(row))
    before = set(COMPILER_LOG_DIR.glob("mmtc_smoke_*"))

    command_log.write_text(shell_command(row) + "\n", encoding="utf-8")
    with stdout_log.open("w", encoding="utf-8") as handle:
        result = subprocess.run(
            ["bash", str(SMOKE_SCRIPT)],
            cwd=REPO_ROOT,
            env=env,
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=False,
        )

    after = set(COMPILER_LOG_DIR.glob("mmtc_smoke_*"))
    new_logs = sorted(after - before)
    manifest.write_text("\n".join(str(path) for path in new_logs) + "\n", encoding="utf-8")
    prefix = infer_log_prefix(new_logs, stdout_log)
    return result.returncode, raw_dir, prefix


def infer_log_prefix(paths: list[Path], stdout_log: Path | None = None) -> str | None:
    candidates: dict[str, int] = {}
    for path in paths:
        match = PREFIX_RE.search(path.name)
        if match:
            prefix = match.group("prefix")
            candidates[prefix] = candidates.get(prefix, 0) + 1
    if stdout_log and stdout_log.is_file():
        text = stdout_log.read_text(errors="ignore", encoding="utf-8")
        for match in PREFIX_RE.finditer(text):
            prefix = match.group("prefix")
            candidates[prefix] = candidates.get(prefix, 0) + 1
    if not candidates:
        return None
    return max(candidates.items(), key=lambda item: item[1])[0]


def parse_summary(stdout_log: Path | None) -> dict[str, str]:
    if not stdout_log or not stdout_log.is_file():
        return {}
    for line in stdout_log.read_text(errors="ignore", encoding="utf-8").splitlines():
        match = SUMMARY_RE.match(line.strip())
        if not match:
            continue
        return {m.group("key"): m.group("value") for m in KEY_VALUE_RE.finditer(match.group("body"))}
    return {}


def rate_to_mbps(value: str, unit: str) -> float:
    rate = float(value)
    if unit.startswith("K"):
        return rate / 1000.0
    if unit.startswith("G"):
        return rate * 1000.0
    return rate


def parse_iperf_logs(logs: list[Path]) -> dict[str, object]:
    senders: list[float] = []
    receivers: list[float] = []
    jitters: list[float] = []
    losses: list[float] = []
    parsed_logs: list[str] = []

    for path in logs:
        parsed_any = False
        for line in path.read_text(errors="ignore", encoding="utf-8").splitlines():
            match = IPERF_RE.match(line.strip())
            if not match:
                continue
            mbps = rate_to_mbps(match.group("rate"), match.group("unit"))
            side = match.group("side")
            if side == "sender":
                senders.append(mbps)
                parsed_any = True
            elif side == "receiver":
                receivers.append(mbps)
                parsed_any = True
                if match.group("jitter") is not None:
                    jitters.append(float(match.group("jitter")))
                if match.group("loss") is not None:
                    losses.append(float(match.group("loss")))
        if parsed_any:
            parsed_logs.append(str(path))

    return {
        "sender_mbps": mean(senders) if senders else None,
        "receiver_mbps": mean(receivers) if receivers else None,
        "jitter_ms": mean(jitters) if jitters else None,
        "udp_loss_percent": mean(losses) if losses else None,
        "parsed_log_paths": parsed_logs,
        "sender_count": len(senders),
        "receiver_count": len(receivers),
    }


def parse_ping_logs(logs: list[Path]) -> dict[str, object]:
    losses: list[float] = []
    rtt_mins: list[float] = []
    rtt_avgs: list[float] = []
    rtt_maxs: list[float] = []
    ok_count = 0
    parsed_logs: list[str] = []

    for path in logs:
        text = path.read_text(errors="ignore", encoding="utf-8")
        loss_match = PING_LOSS_RE.search(text)
        rtt_match = PING_RTT_RE.search(text)
        parsed_any = False
        if loss_match:
            loss = float(loss_match.group("loss"))
            losses.append(loss)
            if loss == 0.0:
                ok_count += 1
            parsed_any = True
        if rtt_match:
            rtt_mins.append(float(rtt_match.group("min")))
            rtt_avgs.append(float(rtt_match.group("avg")))
            rtt_maxs.append(float(rtt_match.group("max")))
            parsed_any = True
        if parsed_any:
            parsed_logs.append(str(path))

    return {
        "ping_loss_percent": mean(losses) if losses else None,
        "rtt_min_ms": min(rtt_mins) if rtt_mins else None,
        "rtt_avg_ms": mean(rtt_avgs) if rtt_avgs else None,
        "rtt_max_ms": max(rtt_maxs) if rtt_maxs else None,
        "forward_ping_ok_count": ok_count,
        "parsed_log_paths": parsed_logs,
    }


def parse_marker_logs(logs: list[Path]) -> dict[str, int]:
    attach = 0
    pdu = 0
    tunnel = 0
    for path in logs:
        text = path.read_text(errors="ignore", encoding="utf-8")
        if "Registration Accept" in text:
            attach += 1
        if "PDU Session Establishment Accept" in text:
            pdu += 1
        if "oaitun_ue1 successfully configured" in text:
            tunnel += 1
    return {"attach": attach, "pdu": pdu, "tun": tunnel}


def safe_float(value: object) -> str:
    if value is None or value == "":
        return ""
    return f"{float(value):.6f}"


def ratio(ok: int | None, total: int | None) -> float | None:
    if ok is None or total is None or total <= 0:
        return None
    return (ok / total) * 100.0


def classify(row: dict[str, str], parsed: dict[str, object]) -> tuple[str, str, str]:
    if parsed["invalid"]:
        return "[INVALID]", "[INSTRUMENTATION_GAP]", "Fix run metadata before using this row."
    if parsed["blocked"]:
        return "[BLOCKED]", "[ENVIRONMENT]", "Check runtime preflight, Docker compose, images, and config paths."

    checks = {
        "attach": parsed["attach_success_ratio"] == 100.0,
        "pdu": parsed["pdu_success_ratio"] == 100.0,
        "tunnel": parsed["tunnel_success_ratio"] == 100.0,
        "forward_ping": parsed["forward_ping_success_ratio"] == 100.0,
        "gnb_restart": parsed["gnb_restart_count"] == 0,
        "failures": parsed["failure_count"] == 0,
        "iperf_sender": parsed["sender_mbps"] is not None,
    }
    measurement_gap = parsed["receiver_mbps"] is None or not parsed["summary_available"]

    if all(checks.values()) and not measurement_gap:
        return "[PASS]", "", ""
    if all(checks.values()) and measurement_gap:
        return "[PASS_WITH_GAP]", "[MEASUREMENT_GAP]", (
            "Runtime passed, but receiver-side throughput or smoke summary is missing; "
            "improve parser/server-log collection before paper-level claims."
        )
    if not checks["attach"]:
        return "[FAIL]", "[ATTACH]", "Inspect UE/gNB/RRC/NAS readiness and UE launch timing."
    if not checks["pdu"]:
        return "[FAIL]", "[PDU_SESSION]", "Inspect CN/SMF/UPF session configuration and subscriber state."
    if not checks["tunnel"]:
        return "[FAIL]", "[TUNNEL]", "Inspect UE tunnel creation and container network state capture."
    if not checks["forward_ping"]:
        return "[FAIL]", "[USER_PLANE]", "Inspect routing, UPF path, ext-dn reachability, and packet forwarding."
    if not checks["gnb_restart"]:
        return "[FAIL]", "[GNB_STABILITY]", "Inspect gNB restart cause, memory pressure, and UE launch burst behavior."
    if not checks["iperf_sender"]:
        return "[FAIL]", "[THROUGHPUT]", "Inspect iperf client/server lifecycle and uplink user-plane scheduling."
    return "[FAIL]", "[JITTER_LOSS]", "Inspect failure markers and classify the dominant runtime issue."


def parse_logs(row: dict[str, str], prefix: str, stdout_log: Path | None) -> dict[str, str]:
    if not prefix:
        parsed = {
            "invalid": False,
            "blocked": True,
            "summary_available": False,
        }
        status, category, improvement = classify(row, parsed)
        return base_output_row(row) | {
            "status": status,
            "blocked": "true",
            "raw_log_dir": str(COMPILER_LOG_DIR),
            "failure_category": category,
            "improvement_direction": improvement,
        }

    logs = sorted(COMPILER_LOG_DIR.glob(f"mmtc_smoke_{prefix}_*"))
    if not logs:
        parsed = {
            "invalid": False,
            "blocked": True,
            "summary_available": False,
        }
        status, category, improvement = classify(row, parsed)
        return base_output_row(row) | {
            "status": status,
            "blocked": "true",
            "raw_log_dir": f"{COMPILER_LOG_DIR}/mmtc_smoke_{prefix}_*",
            "failure_category": category,
            "improvement_direction": improvement,
        }

    sample_count = len(row["sample_ues"].split())
    summary = parse_summary(stdout_log)
    summary_available = bool(summary)
    total_sample = int(summary.get("sample", sample_count))
    iperf_logs = sorted(COMPILER_LOG_DIR.glob(f"mmtc_smoke_{prefix}_ue*_iperf3_ul.log"))
    ping_logs = sorted(COMPILER_LOG_DIR.glob(f"mmtc_smoke_{prefix}_ue*_ping.log"))
    marker_logs = sorted(COMPILER_LOG_DIR.glob(f"mmtc_smoke_{prefix}_ue*_markers.log"))

    iperf = parse_iperf_logs(iperf_logs)
    ping = parse_ping_logs(ping_logs)
    markers = parse_marker_logs(marker_logs)

    attach_ok = int(summary.get("attach", markers["attach"]))
    pdu_ok = int(summary.get("pdu", markers["pdu"]))
    tun_ok = int(summary.get("tun", markers["tun"]))
    ping_ok = int(summary.get("forward_ping_ok", ping["forward_ping_ok_count"]))
    gnb_restart = int(summary.get("gnb_restart", 0))
    failures = int(summary.get("failures", 0))

    parsed = {
        "invalid": False,
        "blocked": False,
        "summary_available": summary_available,
        "attach_success_ratio": ratio(attach_ok, total_sample),
        "pdu_success_ratio": ratio(pdu_ok, total_sample),
        "tunnel_success_ratio": ratio(tun_ok, total_sample),
        "forward_ping_success_ratio": ratio(ping_ok, total_sample),
        "gnb_restart_count": gnb_restart,
        "failure_count": failures,
        "sender_mbps": iperf["sender_mbps"],
        "receiver_mbps": iperf["receiver_mbps"],
    }
    status, category, improvement = classify(row, parsed)

    note_parts = [
        "P3 parser output",
        f"log_prefix={prefix}",
        "receiver/sender/jitter/loss are means across parsed UE iperf logs",
    ]
    if not summary_available:
        note_parts.append("smoke summary missing; status may be PASS_WITH_GAP")

    output = base_output_row(row)
    output.update(
        {
            "status": status,
            "hard_pass": "true" if status == "[PASS]" else "false",
            "pass_with_gap": "true" if status == "[PASS_WITH_GAP]" else "false",
            "blocked": "false",
            "invalid": "false",
            "receiver_mbps": safe_float(iperf["receiver_mbps"]),
            "sender_mbps": safe_float(iperf["sender_mbps"]),
            "jitter_ms": safe_float(iperf["jitter_ms"]),
            "udp_loss_percent": safe_float(iperf["udp_loss_percent"]),
            "ping_loss_percent": safe_float(ping["ping_loss_percent"]),
            "rtt_min_ms": safe_float(ping["rtt_min_ms"]),
            "rtt_avg_ms": safe_float(ping["rtt_avg_ms"]),
            "rtt_max_ms": safe_float(ping["rtt_max_ms"]),
            "attach_success_ratio": safe_float(parsed["attach_success_ratio"]),
            "pdu_success_ratio": safe_float(parsed["pdu_success_ratio"]),
            "tunnel_success_ratio": safe_float(parsed["tunnel_success_ratio"]),
            "forward_ping_success_ratio": safe_float(parsed["forward_ping_success_ratio"]),
            "gnb_restart_count": str(gnb_restart),
            "failure_count": str(failures),
            "raw_log_dir": f"{COMPILER_LOG_DIR}/mmtc_smoke_{prefix}_*",
            "iperf_log_paths": ";".join(iperf["parsed_log_paths"]),
            "ping_log_paths": ";".join(ping["parsed_log_paths"]),
            "trend_note": "; ".join(note_parts),
            "failure_category": category,
            "improvement_direction": improvement,
        }
    )
    return output


def base_output_row(row: dict[str, str]) -> dict[str, str]:
    return {
        "run_id": row["run_id"],
        "status": "",
        "hard_pass": "false",
        "pass_with_gap": "false",
        "blocked": "false",
        "invalid": "false",
        "total_ues": row["total_ues"],
        "sample_ues": row["sample_ues"],
        "iperf_rate": row["iperf_rate"],
        "receiver_mbps": "",
        "sender_mbps": "",
        "jitter_ms": "",
        "udp_loss_percent": "",
        "ping_loss_percent": "",
        "rtt_min_ms": "",
        "rtt_avg_ms": "",
        "rtt_max_ms": "",
        "attach_success_ratio": "",
        "pdu_success_ratio": "",
        "tunnel_success_ratio": "",
        "forward_ping_success_ratio": "",
        "gnb_restart_count": "",
        "failure_count": "",
        "raw_log_dir": "",
        "iperf_log_paths": "",
        "ping_log_paths": "",
        "trend_note": "",
        "failure_category": "",
        "improvement_direction": "",
    }


def upsert_csv(path: Path, row: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    if path.is_file():
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    rows = [existing for existing in rows if existing.get("run_id") != row["run_id"]]
    rows.append(row)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def append_failure_log(path: Path, row: dict[str, str]) -> None:
    if row["status"] == "[PASS]":
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "timestamp",
        "run_id",
        "status",
        "failed_criteria",
        "evidence_paths",
        "suspected_layer",
        "paper_impact",
        "improvement_direction",
        "rerun_requirement",
    ]
    exists = path.is_file()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        if not exists:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp": dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                "run_id": row["run_id"],
                "status": row["status"],
                "failed_criteria": row["failure_category"] or "measurement gap",
                "evidence_paths": ";".join(
                    item
                    for item in [row["raw_log_dir"], row["iperf_log_paths"], row["ping_log_paths"]]
                    if item
                ),
                "suspected_layer": row["failure_category"],
                "paper_impact": "Paper-comparable trend claim must include this limitation.",
                "improvement_direction": row["improvement_direction"],
                "rerun_requirement": "yes" if row["status"] in {"[FAIL]", "[BLOCKED]", "[INVALID]"} else "no",
            }
        )


def print_row(row: dict[str, str]) -> None:
    writer = csv.DictWriter(sys.stdout, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    writer.writerow(row)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--failure-log", type=Path, default=DEFAULT_FAILURE_LOG)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-runs", help="List DOE rows.")

    command_parser = sub.add_parser("command", help="Print shell command for one run.")
    command_parser.add_argument("--run-id", required=True)

    run_parser = sub.add_parser("run", help="Execute one DOE row and parse generated logs.")
    run_parser.add_argument("--run-id", required=True)
    run_parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)

    parse_parser = sub.add_parser("parse-existing", help="Parse an existing smoke log prefix.")
    parse_parser.add_argument("--run-id", required=True)
    parse_parser.add_argument("--log-prefix", required=True, help="Example: 2026-05-20_18-02-35")
    parse_parser.add_argument("--stdout-log", type=Path, default=None)
    parse_parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    rows = read_matrix(args.matrix)

    if args.command == "list-runs":
        list_runs(rows)
        return 0

    row = find_run(rows, args.run_id)

    if args.command == "command":
        print(shell_command(row))
        return 0

    if args.command == "run":
        rc, raw_dir, prefix = run_smoke(row, args.raw_root)
        parsed = parse_logs(row, prefix or "", raw_dir / "smoke_stdout.log")
        upsert_csv(args.output, parsed)
        append_failure_log(args.failure_log, parsed)
        print_row(parsed)
        return rc

    if args.command == "parse-existing":
        parsed = parse_logs(row, args.log_prefix, args.stdout_log)
        if not args.no_write:
            upsert_csv(args.output, parsed)
            append_failure_log(args.failure_log, parsed)
        print_row(parsed)
        return 0

    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
