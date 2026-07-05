#!/usr/bin/env python3
"""PAPER-10 multi-UE iperf3 runner for the RFsim platform.

The script assumes the RFsim/OAI containers are already up and that the target
UEs have an oaitun_ue1 address. It starts one iperf3 server port per UE on
oai-ext-dn, launches the UE clients concurrently, and writes raw logs plus a
parsed CSV.

This is a software-throughput reproduction helper. It does not reproduce the
paper's OTA channel, COTS UEs, SDR, or Open5GS environment by itself.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[6]
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT
    / "agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/data/paper10_multiue_raw"
)
PAPER_ANCHOR = "PAPER-10 Performance Analysis and Comparison of Full-Fledged 5G Standalone Experimental TDD Testbeds"


@dataclass(frozen=True)
class UeEndpoint:
    ue: int
    container: str
    ip: str
    port: int


@dataclass(frozen=True)
class IperfResult:
    run_id: str
    paper_anchor: str
    test_id: str
    direction: str
    ue: int
    container: str
    server_ip: str
    ue_ip: str
    port: int
    protocol: str
    offered_rate: str
    duration_s: int
    return_code: int
    sender_mbps: float | None
    receiver_mbps: float | None
    jitter_ms: float | None
    lost_packets: int | None
    packets: int | None
    lost_percent: float | None
    log_path: str
    limitation_note: str


def run_cmd(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if check and proc.returncode != 0:
        joined = " ".join(args)
        raise RuntimeError(f"command failed ({proc.returncode}): {joined}\n{proc.stderr.strip()}")
    return proc


def docker_exec(container: str, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run_cmd(["docker", "exec", container, *args], check=check)


def parse_ipv4_from_ip_output(output: str) -> str:
    match = re.search(r"\binet\s+([0-9]+(?:\.[0-9]+){3})/", output)
    if not match:
        raise RuntimeError(f"unable to parse IPv4 from: {output.strip()}")
    return match.group(1)


def get_container_ipv4(container: str, interface: str) -> str:
    proc = docker_exec(container, ["ip", "-4", "-o", "addr", "show", "dev", interface])
    return parse_ipv4_from_ip_output(proc.stdout)


def make_endpoints(ues: list[int], base_port: int) -> list[UeEndpoint]:
    endpoints: list[UeEndpoint] = []
    for offset, ue in enumerate(ues):
        container = f"rfsim5g-oai-nr-ue{ue}_redcap"
        ip_addr = get_container_ipv4(container, "oaitun_ue1")
        endpoints.append(UeEndpoint(ue=ue, container=container, ip=ip_addr, port=base_port + offset))
    return endpoints


def start_iperf_servers(ports: list[int], server_container: str, log_path: Path) -> None:
    port_text = " ".join(str(port) for port in ports)
    script = (
        "pids=$(pidof iperf3 2>/dev/null || true); "
        '[ -z "$pids" ] || kill $pids; '
        f"for p in {port_text}; do iperf3 -s -D -p \"$p\"; done"
    )
    proc = docker_exec(server_container, ["sh", "-c", script], check=False)
    log_path.write_text(
        "\n".join(
            [
                f"# collected_at={time.strftime('%Y-%m-%dT%H:%M:%S%z')}",
                f"# ports={port_text}",
                f"# return_code={proc.returncode}",
                proc.stdout,
                proc.stderr,
            ]
        ),
        encoding="utf-8",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"failed to start iperf3 servers on ports {port_text}; see {log_path}")


def stop_iperf_servers(server_container: str) -> None:
    docker_exec(server_container, ["sh", "-c", 'pids=$(pidof iperf3 2>/dev/null || true); [ -z "$pids" ] || kill $pids'], check=False)


def extract_json_object(raw: str) -> dict[str, Any] | None:
    body = "\n".join(line for line in raw.splitlines() if not line.startswith("#"))
    start = body.find("{")
    end = body.rfind("}")
    if start < 0 or end < start:
        return None
    try:
        parsed = json.loads(body[start : end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def mbps_from_bits_per_second(value: Any) -> float | None:
    if value is None:
        return None
    return float(value) / 1_000_000.0


def get_sum_block(payload: dict[str, Any], name: str) -> dict[str, Any]:
    end = payload.get("end")
    if not isinstance(end, dict):
        return {}
    block = end.get(name)
    return block if isinstance(block, dict) else {}


def parse_iperf_payload(payload: dict[str, Any] | None) -> tuple[float | None, float | None, float | None, int | None, int | None, float | None]:
    if payload is None:
        return (None, None, None, None, None, None)

    sender = get_sum_block(payload, "sum_sent")
    receiver = get_sum_block(payload, "sum_received")
    fallback = get_sum_block(payload, "sum")
    sender_mbps = mbps_from_bits_per_second(sender.get("bits_per_second") or fallback.get("bits_per_second"))
    receiver_mbps = mbps_from_bits_per_second(receiver.get("bits_per_second") or fallback.get("bits_per_second"))

    jitter_ms = receiver.get("jitter_ms")
    lost_packets = receiver.get("lost_packets")
    packets = receiver.get("packets")
    lost_percent = receiver.get("lost_percent")

    return (
        sender_mbps,
        receiver_mbps,
        float(jitter_ms) if jitter_ms is not None else None,
        int(lost_packets) if lost_packets is not None else None,
        int(packets) if packets is not None else None,
        float(lost_percent) if lost_percent is not None else None,
    )


def build_iperf_args(
    endpoint: UeEndpoint,
    *,
    server_ip: str,
    direction: str,
    protocol: str,
    offered_rate: str,
    duration_s: int,
) -> list[str]:
    args = [
        "iperf3",
        "-c",
        server_ip,
        "-B",
        endpoint.ip,
        "-t",
        str(duration_s),
        "-p",
        str(endpoint.port),
        "--json",
    ]
    if protocol == "udp":
        args.extend(["-u", "-b", offered_rate])
    elif offered_rate:
        args.extend(["-b", offered_rate])
    if direction == "DL":
        args.append("-R")
    return args


def run_direction(
    *,
    run_id: str,
    test_id: str,
    direction: str,
    protocol: str,
    offered_rate: str,
    duration_s: int,
    server_ip: str,
    server_container: str,
    endpoints: list[UeEndpoint],
    output_dir: Path,
    limitation_note: str,
) -> list[IperfResult]:
    start_iperf_servers([endpoint.port for endpoint in endpoints], server_container, output_dir / f"{run_id}_{direction}_servers.log")

    processes: list[tuple[UeEndpoint, subprocess.Popen[str], Path]] = []
    for endpoint in endpoints:
        iperf_args = build_iperf_args(
            endpoint,
            server_ip=server_ip,
            direction=direction,
            protocol=protocol,
            offered_rate=offered_rate,
            duration_s=duration_s,
        )
        log_path = output_dir / f"{run_id}_{direction}_ue{endpoint.ue}_iperf3.json"
        log_file = log_path.open("w", encoding="utf-8")
        header = {
            "collected_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "direction": direction,
            "ue": endpoint.ue,
            "container": endpoint.container,
            "server_ip": server_ip,
            "ue_ip": endpoint.ip,
            "port": endpoint.port,
            "protocol": protocol,
            "offered_rate": offered_rate,
            "duration_s": duration_s,
            "command": ["docker", "exec", endpoint.container, *iperf_args],
        }
        log_file.write("# " + json.dumps(header, sort_keys=True) + "\n")
        log_file.flush()
        proc = subprocess.Popen(
            ["docker", "exec", endpoint.container, *iperf_args],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
        )
        log_file.close()
        processes.append((endpoint, proc, log_path))

    results: list[IperfResult] = []
    for endpoint, proc, log_path in processes:
        return_code = proc.wait()
        raw = log_path.read_text(encoding="utf-8", errors="replace")
        payload = extract_json_object(raw)
        sender_mbps, receiver_mbps, jitter_ms, lost_packets, packets, lost_percent = parse_iperf_payload(payload)
        results.append(
            IperfResult(
                run_id=run_id,
                paper_anchor=PAPER_ANCHOR,
                test_id=test_id,
                direction=direction,
                ue=endpoint.ue,
                container=endpoint.container,
                server_ip=server_ip,
                ue_ip=endpoint.ip,
                port=endpoint.port,
                protocol=protocol,
                offered_rate=offered_rate,
                duration_s=duration_s,
                return_code=return_code,
                sender_mbps=sender_mbps,
                receiver_mbps=receiver_mbps,
                jitter_ms=jitter_ms,
                lost_packets=lost_packets,
                packets=packets,
                lost_percent=lost_percent,
                log_path=str(log_path),
                limitation_note=limitation_note,
            )
        )

    stop_iperf_servers(server_container)
    return results


def write_csv(path: Path, results: list[IperfResult]) -> None:
    fieldnames = list(IperfResult.__dataclass_fields__.keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))


def parse_existing_run(run_dir: Path) -> list[IperfResult]:
    metadata_path = run_dir / "metadata.json"
    if not metadata_path.exists():
        raise RuntimeError(f"missing metadata.json under {run_dir}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    run_id = str(metadata["run_id"])
    protocol = str(metadata["protocol"])
    duration_s = int(metadata["duration_s"])
    server_ip = str(metadata["server_ip"])
    limitation_note = str(metadata.get("limitation_note", ""))
    endpoints = [
        UeEndpoint(
            ue=int(item["ue"]),
            container=str(item["container"]),
            ip=str(item["ip"]),
            port=int(item["port"]),
        )
        for item in metadata["endpoints"]
    ]

    results: list[IperfResult] = []
    for direction, offered_rate in (("UL", str(metadata.get("ul_rate", ""))), ("DL", str(metadata.get("dl_rate", "")))):
        for endpoint in endpoints:
            log_path = run_dir / f"{run_id}_{direction}_ue{endpoint.ue}_iperf3.json"
            if not log_path.exists():
                continue
            raw = log_path.read_text(encoding="utf-8", errors="replace")
            payload = extract_json_object(raw)
            sender_mbps, receiver_mbps, jitter_ms, lost_packets, packets, lost_percent = parse_iperf_payload(payload)
            results.append(
                IperfResult(
                    run_id=run_id,
                    paper_anchor=PAPER_ANCHOR,
                    test_id="PERF-P10-THR-002",
                    direction=direction,
                    ue=endpoint.ue,
                    container=endpoint.container,
                    server_ip=server_ip,
                    ue_ip=endpoint.ip,
                    port=endpoint.port,
                    protocol=protocol,
                    offered_rate=offered_rate,
                    duration_s=duration_s,
                    return_code=0 if payload is not None else 1,
                    sender_mbps=sender_mbps,
                    receiver_mbps=receiver_mbps,
                    jitter_ms=jitter_ms,
                    lost_packets=lost_packets,
                    packets=packets,
                    lost_percent=lost_percent,
                    log_path=str(log_path),
                    limitation_note=limitation_note,
                )
            )
    return results


def jain_fairness(values: list[float]) -> float | None:
    if not values:
        return None
    denom = len(values) * sum(value * value for value in values)
    if denom == 0:
        return None
    return (sum(values) ** 2) / denom


def print_summary(results: list[IperfResult]) -> None:
    print("direction,ue,receiver_mbps,sender_mbps,lost_percent,return_code")
    for result in results:
        print(
            f"{result.direction},UE{result.ue},"
            f"{result.receiver_mbps if result.receiver_mbps is not None else 'NA'},"
            f"{result.sender_mbps if result.sender_mbps is not None else 'NA'},"
            f"{result.lost_percent if result.lost_percent is not None else 'NA'},"
            f"{result.return_code}"
        )

    for direction in sorted({result.direction for result in results}):
        values = [result.receiver_mbps for result in results if result.direction == direction and result.receiver_mbps is not None]
        fairness = jain_fairness([float(value) for value in values])
        aggregate = sum(float(value) for value in values)
        print(
            f"aggregate,{direction},receiver_mbps={aggregate:.6f},"
            f"jain_fairness={fairness:.6f}" if fairness is not None else f"aggregate,{direction},receiver_mbps={aggregate:.6f},jain_fairness=NA"
        )


def self_test() -> None:
    payload = {
        "end": {
            "sum_sent": {"bits_per_second": 35_000_000.0},
            "sum_received": {
                "bits_per_second": 34_500_000.0,
                "jitter_ms": 0.42,
                "lost_packets": 1,
                "packets": 1000,
                "lost_percent": 0.1,
            },
        }
    }
    sender_mbps, receiver_mbps, jitter_ms, lost_packets, packets, lost_percent = parse_iperf_payload(payload)
    assert sender_mbps == 35.0
    assert receiver_mbps == 34.5
    assert jitter_ms == 0.42
    assert lost_packets == 1
    assert packets == 1000
    assert lost_percent == 0.1
    fairness = jain_fairness([10.0, 10.0, 10.0])
    assert fairness is not None and abs(fairness - 1.0) < 1e-12


def parse_ues(value: str) -> list[int]:
    ues = [int(item.strip()) for item in value.split(",") if item.strip()]
    if not ues:
        raise argparse.ArgumentTypeError("at least one UE index is required")
    return ues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run concurrent PAPER-10 multi-UE iperf3 measurements")
    parser.add_argument("--ues", type=parse_ues, default=parse_ues("1,2,3"), help="comma-separated UE indices")
    parser.add_argument("--direction", choices=["UL", "DL", "both"], default="both")
    parser.add_argument("--duration", type=int, default=180)
    parser.add_argument("--protocol", choices=["udp", "tcp"], default="udp")
    parser.add_argument("--ul-rate", default="35M")
    parser.add_argument("--dl-rate", default="141M")
    parser.add_argument("--base-port", type=int, default=5201)
    parser.add_argument("--server-container", default="oai-ext-dn")
    parser.add_argument("--server-interface", default="eth0")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--run-id", default=time.strftime("paper10_multiue_%Y-%m-%d_%H-%M-%S"))
    parser.add_argument("--test-id", default="PERF-P10-THR-002")
    parser.add_argument("--limitation-note", default="RFsim/OAI-CN/OAI-nrUE proxy; not OTA Open5GS+COTS UE reproduction")
    parser.add_argument("--parse-run-dir", type=Path, help="parse an existing run directory without launching iperf3")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        print("self-test passed")
        return 0

    if args.parse_run_dir:
        results = parse_existing_run(args.parse_run_dir)
        metadata = json.loads((args.parse_run_dir / "metadata.json").read_text(encoding="utf-8"))
        csv_path = args.parse_run_dir / f"{metadata['run_id']}_results.csv"
        write_csv(csv_path, results)
        print(f"results_csv={csv_path}")
        print_summary(results)
        failed = [result for result in results if result.return_code != 0 or result.receiver_mbps is None]
        return 1 if failed else 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_dir = args.output_dir / args.run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    server_ip = get_container_ipv4(args.server_container, args.server_interface)
    endpoints = make_endpoints(args.ues, args.base_port)
    metadata = {
        "run_id": args.run_id,
        "paper_anchor": PAPER_ANCHOR,
        "ues": args.ues,
        "server_ip": server_ip,
        "duration_s": args.duration,
        "protocol": args.protocol,
        "ul_rate": args.ul_rate,
        "dl_rate": args.dl_rate,
        "limitation_note": args.limitation_note,
        "endpoints": [asdict(endpoint) for endpoint in endpoints],
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    results: list[IperfResult] = []
    try:
        if args.direction in ("UL", "both"):
            results.extend(
                run_direction(
                    run_id=args.run_id,
                    test_id=args.test_id,
                    direction="UL",
                    protocol=args.protocol,
                    offered_rate=args.ul_rate,
                    duration_s=args.duration,
                    server_ip=server_ip,
                    server_container=args.server_container,
                    endpoints=endpoints,
                    output_dir=run_dir,
                    limitation_note=args.limitation_note,
                )
            )
        if args.direction in ("DL", "both"):
            results.extend(
                run_direction(
                    run_id=args.run_id,
                    test_id=args.test_id,
                    direction="DL",
                    protocol=args.protocol,
                    offered_rate=args.dl_rate,
                    duration_s=args.duration,
                    server_ip=server_ip,
                    server_container=args.server_container,
                    endpoints=endpoints,
                    output_dir=run_dir,
                    limitation_note=args.limitation_note,
                )
            )
    finally:
        stop_iperf_servers(args.server_container)

    csv_path = run_dir / f"{args.run_id}_results.csv"
    write_csv(csv_path, results)
    print(f"results_csv={csv_path}")
    print_summary(results)

    failed = [result for result in results if result.return_code != 0 or result.receiver_mbps is None]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
