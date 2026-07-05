#!/usr/bin/env python3
"""PAPER-08 Fig. 9 UDP downlink SNR-proxy sweep for OAI RFsim.

This reproduces the shape of PAPER-08 Fig. 9 using available RFsim channel
models. RFsim exposes noise/path-loss knobs, not a calibrated channel-emulator
SNR measurement. For that reason, the x-axis is named target_snr_proxy_db.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_DIR = SCRIPT_PATH.parents[2]
DATA_DIR = PROJECT_DIR / "analysis" / "data"
PLOT_DIR = PROJECT_DIR / "analysis" / "plots"
REPORT_PATH = PROJECT_DIR / "analysis" / "paper08_fig9_udp_snr_sweep_report.md"
PAPER_ANCHOR = "PAPER-08 Fig. 9 UDP DL data rate vs SNR"


DEFAULT_CHANNEL_MODELS = [
    "AWGN",
    "Rayleigh1",
    "Rayleigh8",
    "Rayleigh1_corr",
    "Rayleigh1_anticorr",
    "Rice1",
    "Rice8",
    "TDL_A",
]
DEFAULT_SNR_TO_NOISE = {
    30.0: -30.0,
    20.0: -20.0,
    10.0: -10.0,
    5.0: -5.0,
    0.0: 0.0,
}


@dataclass(frozen=True)
class SweepResult:
    run_id: str
    paper_anchor: str
    ue: int
    channel_model: str
    target_snr_proxy_db: float
    noise_power_db: float
    ploss_db: float
    direction: str
    protocol: str
    offered_rate: str
    duration_s: int
    server_ip: str
    ue_ip: str
    return_code: int
    sender_mbps: float | None
    receiver_mbps: float | None
    jitter_ms: float | None
    lost_packets: int | None
    packets: int | None
    lost_percent: float | None
    telnet_log_path: str
    iperf_log_path: str
    limitation_note: str


@dataclass(frozen=True)
class BlockedModel:
    channel_model: str
    stage: str
    status: str
    evidence_path: str
    limitation_note: str


def run_cmd(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(args)}\n{proc.stderr.strip()}")
    return proc


def docker_exec(container: str, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run_cmd(["docker", "exec", container, *args], check=check)


def parse_ipv4(output: str) -> str:
    for token in output.replace("/", " /").split():
        parts = token.split(".")
        if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
            return token
    raise RuntimeError(f"unable to parse IPv4 from: {output.strip()}")


def container_ip(container: str, interface: str) -> str:
    proc = docker_exec(container, ["ip", "-4", "-o", "addr", "show", "dev", interface])
    return parse_ipv4(proc.stdout)


def telnet_command(container: str, port: int, commands: list[str], log_path: Path) -> str:
    payload = "".join(f"{command}\n" for command in commands)
    shell = (
        f"exec 3<>/dev/tcp/127.0.0.1/{port}; "
        f"printf {json.dumps(payload)} >&3; "
        "timeout 3 cat <&3 || true"
    )
    proc = docker_exec(container, ["bash", "-lc", shell], check=False)
    text = "\n".join(
        [
            f"# collected_at={time.strftime('%Y-%m-%dT%H:%M:%S%z')}",
            f"# container={container}",
            f"# port={port}",
            f"# commands={json.dumps(commands)}",
            f"# return_code={proc.returncode}",
            proc.stdout,
            proc.stderr,
        ]
    )
    log_path.write_text(text, encoding="utf-8")
    return text


def set_downlink_channel(
    *,
    ue_container: str,
    telnet_port: int,
    channel_model: str,
    noise_power_db: float,
    ploss_db: float,
    log_path: Path,
    set_model: bool,
) -> str:
    logs: list[str] = []
    if set_model:
        logs.append(telnet_command(ue_container, telnet_port, [f"rfsimu setmodel rfsimu_channel_enB0 {channel_model}"], log_path))
        time.sleep(1.0)
    logs.append(telnet_command(ue_container, telnet_port, ["channelmod show current"], log_path))
    channel_index = find_channel_index(logs[-1], "rfsimu_channel_enB0")
    logs.append(telnet_command(ue_container, telnet_port, [f"channelmod modify {channel_index} ploss {ploss_db}"], log_path))
    time.sleep(0.5)
    logs.append(telnet_command(ue_container, telnet_port, [f"channelmod modify {channel_index} noise_power_dB {noise_power_db}"], log_path))
    time.sleep(0.5)
    logs.append(
        telnet_command(
            ue_container,
            telnet_port,
            ["channelmod show current"],
            log_path,
        )
    )
    combined = "\n".join(logs)
    log_path.write_text(combined, encoding="utf-8")
    return combined


def find_channel_index(show_current_text: str, model_name: str) -> int:
    pattern = re.compile(rf"model\s+(\d+)\s+{re.escape(model_name)}\s+type")
    match = pattern.search(show_current_text)
    if not match:
        raise RuntimeError(f"unable to find channel model index for {model_name}")
    return int(match.group(1))


def start_iperf_server(container: str, port: int) -> None:
    docker_exec(
        container,
        ["sh", "-c", f'pids=$(pidof iperf3 2>/dev/null || true); [ -z "$pids" ] || kill $pids; iperf3 -s -D -p {port}'],
    )


def stop_iperf_server(container: str) -> None:
    docker_exec(container, ["sh", "-c", 'pids=$(pidof iperf3 2>/dev/null || true); [ -z "$pids" ] || kill $pids'], check=False)


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
    return parsed if isinstance(parsed, dict) else None


def mbps(value: Any) -> float | None:
    return None if value is None else float(value) / 1_000_000.0


def sum_block(payload: dict[str, Any] | None, key: str) -> dict[str, Any]:
    if payload is None:
        return {}
    end = payload.get("end")
    if not isinstance(end, dict):
        return {}
    block = end.get(key)
    return block if isinstance(block, dict) else {}


def parse_iperf(raw: str) -> tuple[float | None, float | None, float | None, int | None, int | None, float | None]:
    payload = extract_json_object(raw)
    sent = sum_block(payload, "sum_sent")
    received = sum_block(payload, "sum_received")
    fallback = sum_block(payload, "sum")
    sender_mbps = mbps(sent.get("bits_per_second") or fallback.get("bits_per_second"))
    receiver_mbps = mbps(received.get("bits_per_second") or fallback.get("bits_per_second"))
    jitter_ms = received.get("jitter_ms") if received else fallback.get("jitter_ms")
    lost_packets = received.get("lost_packets") if received else fallback.get("lost_packets")
    packets = received.get("packets") if received else fallback.get("packets")
    lost_percent = received.get("lost_percent") if received else fallback.get("lost_percent")
    return (
        sender_mbps,
        receiver_mbps,
        float(jitter_ms) if jitter_ms is not None else None,
        int(lost_packets) if lost_packets is not None else None,
        int(packets) if packets is not None else None,
        float(lost_percent) if lost_percent is not None else None,
    )


def run_dl_iperf(
    *,
    ue_container: str,
    server_ip: str,
    ue_ip: str,
    port: int,
    duration_s: int,
    offered_rate: str,
    log_path: Path,
) -> tuple[int, float | None, float | None, float | None, int | None, int | None, float | None]:
    args = [
        "iperf3",
        "-c",
        server_ip,
        "-B",
        ue_ip,
        "-t",
        str(duration_s),
        "-p",
        str(port),
        "--json",
        "-u",
        "-b",
        offered_rate,
        "-R",
    ]
    try:
        proc = subprocess.run(
            ["docker", "exec", ue_container, *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=duration_s + 20,
        )
        return_code = proc.returncode
        output = proc.stdout
    except subprocess.TimeoutExpired as exc:
        return_code = 124
        output = (exc.stdout or "") + "\n# timeout expired\n"
    log_path.write_text(
        "# "
        + json.dumps(
            {
                "collected_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "command": ["docker", "exec", ue_container, *args],
                "return_code": return_code,
            },
            sort_keys=True,
        )
        + "\n"
        + output,
        encoding="utf-8",
    )
    sender_mbps, receiver_mbps, jitter_ms, lost_packets, packets, lost_percent = parse_iperf(output)
    return return_code, sender_mbps, receiver_mbps, jitter_ms, lost_packets, packets, lost_percent


def parse_snr_noise_pairs(value: str) -> dict[float, float]:
    pairs: dict[float, float] = {}
    for item in value.split(","):
        if not item.strip():
            continue
        snr_text, noise_text = item.split(":", 1)
        pairs[float(snr_text)] = float(noise_text)
    if not pairs:
        raise argparse.ArgumentTypeError("at least one SNR:noise pair is required")
    return pairs


def write_csv(path: Path, rows: list[SweepResult]) -> None:
    fieldnames = list(SweepResult.__dataclass_fields__.keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def read_csv_results(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_blocked_models(path: Path | None) -> list[BlockedModel]:
    if path is None or not path.exists():
        return []
    rows: list[BlockedModel] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                BlockedModel(
                    channel_model=row.get("channel_model", ""),
                    stage=row.get("stage", ""),
                    status=row.get("status", ""),
                    evidence_path=row.get("evidence_path", ""),
                    limitation_note=row.get("limitation_note", ""),
                )
            )
    return rows


def combine_csvs(paths: list[Path], output_path: Path) -> None:
    rows: list[dict[str, str]] = []
    fieldnames = list(SweepResult.__dataclass_fields__.keys())
    for path in paths:
        rows.extend(read_csv_results(path))
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def plot(csv_path: Path, png_path: Path, pdf_path: Path) -> None:
    matplotlib_cache = Path(os.environ.get("MPLCONFIGDIR", "/tmp/matplotlib-redcap"))
    matplotlib_cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(matplotlib_cache))

    import matplotlib.pyplot as plt

    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    models = []
    for row in rows:
        if row["channel_model"] not in models:
            models.append(row["channel_model"])

    fig, axes = plt.subplots(2, 1, figsize=(10.2, 7.4), sharex=True)
    for model in models:
        model_rows = [row for row in rows if row["channel_model"] == model and row["receiver_mbps"]]
        model_rows.sort(key=lambda row: float(row["target_snr_proxy_db"]))
        x = [float(row["target_snr_proxy_db"]) for row in model_rows]
        y = [float(row["receiver_mbps"]) for row in model_rows]
        loss = [float(row["lost_percent"] or 0.0) for row in model_rows]
        axes[0].plot(x, y, marker="o", linewidth=1.8, label=model)
        axes[1].plot(x, loss, marker="o", linewidth=1.3, label=model)

    axes[0].set_title("PAPER-08 Fig.9 RFsim Proxy: UDP DL Throughput vs SNR")
    axes[0].set_ylabel("Receiver throughput (Mbps)")
    axes[0].grid(alpha=0.25)
    axes[0].legend(loc="best", ncols=2, fontsize=8)
    axes[1].set_xlabel("Target SNR proxy (dB), mapped to RFsim noise_power_dB")
    axes[1].set_ylabel("UDP loss (%)")
    axes[1].grid(alpha=0.25)
    axes[1].invert_xaxis()
    axes[0].invert_xaxis()
    fig.tight_layout()
    fig.savefig(png_path, dpi=180)
    fig.savefig(pdf_path)
    plt.close(fig)


def write_report(
    path: Path,
    csv_path: Path,
    png_path: Path,
    pdf_path: Path,
    rows: list[SweepResult],
    blocked_models: list[BlockedModel] | None = None,
) -> None:
    complete = [row for row in rows if row.receiver_mbps is not None and row.return_code == 0]
    blocked = len(rows) - len(complete)
    blocked_models = blocked_models or []
    lines = [
        "# PAPER-08 Fig.9 UDP SNR Sweep Report",
        "",
        "## Scope",
        f"- [Paper Anchor]: {PAPER_ANCHOR}.",
        "- [Method]: RFsim channelmod proxy for PAPER-08 Fig.9 UDP downlink data-rate measurement.",
        "- [Plotting]: Paper07-style CSV to matplotlib PNG/PDF workflow.",
        "- [Guardrail]: `target_snr_proxy_db` is mapped to RFsim `noise_power_dB`; it is not calibrated instrument SNR.",
        f"- [CSV]: `{csv_path.relative_to(PROJECT_DIR)}`.",
        f"- [PNG]: `{png_path.relative_to(PROJECT_DIR)}`.",
        f"- [PDF]: `{pdf_path.relative_to(PROJECT_DIR)}`.",
        "",
        "## Result Summary",
        f"- [Completed Rows]: {len(complete)}.",
        f"- [Blocked/Failed Rows]: {blocked}.",
        f"- [Blocked Channel Models]: {len(blocked_models)}.",
        "",
        "| Channel Model | Best Receiver Mbps | Worst Receiver Mbps | Mean Loss % |",
        "|---|---:|---:|---:|",
    ]

    by_model: dict[str, list[SweepResult]] = {}
    for row in complete:
        by_model.setdefault(row.channel_model, []).append(row)
    for model, model_rows in by_model.items():
        throughputs = [float(row.receiver_mbps or 0.0) for row in model_rows]
        losses = [float(row.lost_percent or 0.0) for row in model_rows]
        lines.append(f"| {model} | {max(throughputs):.3f} | {min(throughputs):.3f} | {sum(losses) / len(losses):.3f} |")

    failed_rows = [row for row in rows if row.receiver_mbps is None or row.return_code != 0]
    if failed_rows:
        lines.extend(
            [
                "",
                "## Failed Measurement Rows",
                "| Channel Model | SNR Proxy dB | noise_power_dB | Return Code | Note |",
                "|---|---:|---:|---:|---|",
            ]
        )
        for row in failed_rows:
            lines.append(
                f"| {row.channel_model} | {row.target_snr_proxy_db:g} | {row.noise_power_db:g} | "
                f"{row.return_code} | {row.limitation_note} |"
            )

    if blocked_models:
        lines.extend(
            [
                "",
                "## Blocked Channel Models",
                "| Channel Model | Stage | Status | Evidence | Note |",
                "|---|---|---|---|---|",
            ]
        )
        for item in blocked_models:
            lines.append(
                f"| {item.channel_model} | {item.stage} | {item.status} | "
                f"`{item.evidence_path}` | {item.limitation_note} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "- [Comparable]: this run exercises continuous UDP downlink traffic while sweeping RFsim noise/channel models.",
            "- [Not Directly Comparable]: PAPER-08 used a hardware channel emulator and measured calibrated SNR at the UE.",
            "- [Needs Verification]: exact MCS pinning is not yet equivalent to the radio communication tester setup in PAPER-08.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def self_test() -> None:
    sample = {
        "end": {
            "sum_sent": {"bits_per_second": 10_000_000.0},
            "sum_received": {"bits_per_second": 9_000_000.0, "jitter_ms": 0.1, "lost_packets": 1, "packets": 100, "lost_percent": 1.0},
        }
    }
    raw = json.dumps(sample)
    sender, receiver, jitter, lost, packets, loss = parse_iperf(raw)
    assert sender == 10.0
    assert receiver == 9.0
    assert jitter == 0.1
    assert lost == 1
    assert packets == 100
    assert loss == 1.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PAPER-08 Fig.9 UDP DL SNR-proxy sweep")
    parser.add_argument("--ue", type=int, default=1)
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--offered-rate", default="90M")
    parser.add_argument("--port", type=int, default=5201)
    parser.add_argument("--ploss-db", type=float, default=20.0)
    parser.add_argument("--channel-models", default=",".join(DEFAULT_CHANNEL_MODELS))
    parser.add_argument("--skip-setmodel", action="store_true", help="do not dynamically switch RFsim model type; use startup config")
    parser.add_argument(
        "--snr-noise-pairs",
        type=parse_snr_noise_pairs,
        default=DEFAULT_SNR_TO_NOISE,
        help="comma-separated target_snr_proxy_db:noise_power_db pairs, e.g. 30:-30,20:-20,10:-10",
    )
    parser.add_argument("--run-id", default=time.strftime("paper08_fig9_udp_snr_%Y-%m-%d_%H-%M-%S"))
    parser.add_argument("--combine-csvs", nargs="+", type=Path, help="combine existing per-model CSVs and regenerate plot/report")
    parser.add_argument("--blocked-models-file", type=Path, help="optional CSV listing channel models blocked before measurement")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        print("self-test passed")
        return 0

    if args.combine_csvs:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        PLOT_DIR.mkdir(parents=True, exist_ok=True)
        csv_path = DATA_DIR / f"{args.run_id}.csv"
        png_path = PLOT_DIR / f"{args.run_id}.png"
        pdf_path = PLOT_DIR / f"{args.run_id}.pdf"
        combine_csvs(args.combine_csvs, csv_path)
        plot(csv_path, png_path, pdf_path)
        complete_rows: list[SweepResult] = []
        for row in read_csv_results(csv_path):
            complete_rows.append(
                SweepResult(
                    run_id=row["run_id"],
                    paper_anchor=row["paper_anchor"],
                    ue=int(row["ue"]),
                    channel_model=row["channel_model"],
                    target_snr_proxy_db=float(row["target_snr_proxy_db"]),
                    noise_power_db=float(row["noise_power_db"]),
                    ploss_db=float(row["ploss_db"]),
                    direction=row["direction"],
                    protocol=row["protocol"],
                    offered_rate=row["offered_rate"],
                    duration_s=int(row["duration_s"]),
                    server_ip=row["server_ip"],
                    ue_ip=row["ue_ip"],
                    return_code=int(row["return_code"]),
                    sender_mbps=float(row["sender_mbps"]) if row["sender_mbps"] else None,
                    receiver_mbps=float(row["receiver_mbps"]) if row["receiver_mbps"] else None,
                    jitter_ms=float(row["jitter_ms"]) if row["jitter_ms"] else None,
                    lost_packets=int(row["lost_packets"]) if row["lost_packets"] else None,
                    packets=int(row["packets"]) if row["packets"] else None,
                    lost_percent=float(row["lost_percent"]) if row["lost_percent"] else None,
                    telnet_log_path=row["telnet_log_path"],
                    iperf_log_path=row["iperf_log_path"],
                    limitation_note=row["limitation_note"],
                )
            )
        write_report(REPORT_PATH, csv_path, png_path, pdf_path, complete_rows, read_blocked_models(args.blocked_models_file))
        print(f"csv={csv_path}")
        print(f"png={png_path}")
        print(f"pdf={pdf_path}")
        print(f"report={REPORT_PATH}")
        return 0

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    run_dir = DATA_DIR / "paper08_fig9_udp_snr_raw" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    ue_container = f"rfsim5g-oai-nr-ue{args.ue}_redcap"
    telnet_port = 8090 + args.ue
    server_container = "oai-ext-dn"
    server_ip = container_ip(server_container, "eth0")
    ue_ip = container_ip(ue_container, "oaitun_ue1")
    channel_models = [item.strip() for item in args.channel_models.split(",") if item.strip()]

    rows: list[SweepResult] = []
    try:
        for channel_model in channel_models:
            for target_snr_proxy_db, noise_power_db in sorted(args.snr_noise_pairs.items(), reverse=True):
                row_id = f"{channel_model}_snr{target_snr_proxy_db:g}".replace(".", "p")
                telnet_log = run_dir / f"{args.run_id}_{row_id}_telnet.log"
                iperf_log = run_dir / f"{args.run_id}_{row_id}_iperf3_dl.json"
                set_downlink_channel(
                    ue_container=ue_container,
                    telnet_port=telnet_port,
                    channel_model=channel_model,
                    noise_power_db=noise_power_db,
                    ploss_db=args.ploss_db,
                    log_path=telnet_log,
                    set_model=not args.skip_setmodel,
                )
                time.sleep(1.0)
                start_iperf_server(server_container, args.port)
                rc, sender, receiver, jitter, lost, packets, loss = run_dl_iperf(
                    ue_container=ue_container,
                    server_ip=server_ip,
                    ue_ip=ue_ip,
                    port=args.port,
                    duration_s=args.duration,
                    offered_rate=args.offered_rate,
                    log_path=iperf_log,
                )
                rows.append(
                    SweepResult(
                        run_id=args.run_id,
                        paper_anchor=PAPER_ANCHOR,
                        ue=args.ue,
                        channel_model=channel_model,
                        target_snr_proxy_db=target_snr_proxy_db,
                        noise_power_db=noise_power_db,
                        ploss_db=args.ploss_db,
                        direction="DL",
                        protocol="udp",
                        offered_rate=args.offered_rate,
                        duration_s=args.duration,
                        server_ip=server_ip,
                        ue_ip=ue_ip,
                        return_code=rc,
                        sender_mbps=sender,
                        receiver_mbps=receiver,
                        jitter_ms=jitter,
                        lost_packets=lost,
                        packets=packets,
                        lost_percent=loss,
                        telnet_log_path=str(telnet_log),
                        iperf_log_path=str(iperf_log),
                        limitation_note="RFsim noise/channel proxy, not calibrated PAPER-08 channel-emulator SNR",
                    )
                )
                print(
                    f"{channel_model},snr_proxy={target_snr_proxy_db:g},"
                    f"receiver_mbps={receiver if receiver is not None else 'NA'},loss={loss if loss is not None else 'NA'},rc={rc}",
                    flush=True,
                )
    finally:
        stop_iperf_server(server_container)

    csv_path = DATA_DIR / f"{args.run_id}.csv"
    png_path = PLOT_DIR / f"{args.run_id}.png"
    pdf_path = PLOT_DIR / f"{args.run_id}.pdf"
    write_csv(csv_path, rows)
    plot(csv_path, png_path, pdf_path)
    write_report(REPORT_PATH, csv_path, png_path, pdf_path, rows)
    print(f"csv={csv_path}")
    print(f"png={png_path}")
    print(f"pdf={pdf_path}")
    print(f"report={REPORT_PATH}")
    failed = [row for row in rows if row.return_code != 0 or row.receiver_mbps is None]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
