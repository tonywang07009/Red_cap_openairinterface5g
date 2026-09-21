"""Bash-launchable terminal UI for saved D2R BER measurement records."""

import argparse
import json
import os
from pathlib import Path
import socket
import sys

from fourmula import (
    D2RMeasurementService,
    aggregate_cbra_campaign_rows,
    aggregate_campaign_rows,
    cbra_observation_to_campaign_row,
    decode_cbra_observation_datagram,
    estimate_rician_energy_ber,
    generate_visibility_map,
    reader_visible_tags,
    decode_observation_datagram,
    sample_ticks_to_ns,
    summarize_cbra_observation_outcomes,
)
from storage import JsonExperimentStorage


def _bar(value: float | None, width: int = 20) -> str:
    if value is None:
        return "-" * width
    filled = min(width, round(value * width))
    return "#" * filled + "." * (width - filled)


def render_status(record: dict) -> str:
    """Render a compact, htop-inspired status view without extra dependencies."""
    observations = record.get("observations", [])
    rows = [
        "D2R BER MEASUREMENT                                             [q: exit]",
        f"schema={record.get('schema_version', '?')}  observations={len(observations)}",
        "Reader  Window       BER        Bits   Errors  TX  Undet Unal  Loss     Valid  BER bar",
    ]
    for item in observations:
        ber = item.get("ber")
        loss = item.get("packet_loss_rate")
        rows.append(
            f"{item.get('reader_id', '?'):>6}  {item.get('window_index', '?'):>6}  "
            f"{('null' if ber is None else f'{ber:.6f}'):>9}  "
            f"{item.get('compared_bits', 0):>10}  {item.get('erroneous_bits', 0):>6}  "
            f"{item.get('actual_tx_packets', 0):>3}  {item.get('undetected_packets', 0):>5} "
            f"{item.get('unaligned_packets', 0):>4}  "
            f"{('null' if loss is None else f'{loss:.6f}'):>8}  "
            f"{str(item.get('valid', False)):>5}  {_bar(ber)}"
        )
    return "\n".join(rows)


def _init_record(args: argparse.Namespace) -> dict:
    reader_ids = (1, 2, 3)
    visibility_map = generate_visibility_map(tag_count=args.tag_count, reader_ids=reader_ids, seed=args.seed)
    return {
        "schema_version": 2,
        "config": {
            "reader_ids": list(reader_ids),
            "tag_count": args.tag_count,
            "visibility_seed": args.seed,
            "visibility_map": {str(tag): reader for tag, reader in visibility_map.items()},
            "reader_visible_tags": {str(reader): tags for reader, tags in reader_visible_tags(visibility_map, reader_ids).items()},
            "sample_rate_hz": args.sample_rate_hz,
            "observation_window_ns": 500_000,
            "ideal_cross_reader_isolation": True,
            "ideal_acquisition_alignment": True,
            "rician_k_db_per_leg": 3.0,
            "receiver_noise_power": 0.1,
            "channel_provenance": "RFsim report channel_provenance; numerical reference is separate",
            "packet_loss_formula": "(undetected_packets + unaligned_packets) / actual_tx_packets",
        },
        "observations": [],
        "duration_results": [],
        "wire_records": [],
        "reference_results": [],
        "pending_decisions": [],
    }


def _ingest_udp(args: argparse.Namespace) -> dict:
    if args.profile == "cbra":
        return _ingest_cbra_udp(args)
    record = JsonExperimentStorage(args.input).load()
    sample_rate_hz = record.get("config", {}).get("sample_rate_hz", args.sample_rate_hz)
    if sample_rate_hz is None or sample_rate_hz <= 0:
        raise ValueError("sample-rate-hz is required for UDP ingest")
    service = D2RMeasurementService(window_ns=500_000)
    received = 0
    window_indices: set[int] = set()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as listener:
        listener.bind((args.bind, args.port))
        listener.settimeout(args.timeout)
        while args.packets == 0 or received < args.packets:
            try:
                data, _peer = listener.recvfrom(4096)
            except socket.timeout:
                break
            report = decode_observation_datagram(data)
            service.record_wire_observation(report, sample_rate_hz=sample_rate_hz)
            # Completed packets close in their decode window; known acquisition
            # losses are accounted in their TX-attempt window. Keep both so a
            # loss-only capture is visible in the persisted JSON.
            window_indices.add(sample_ticks_to_ns(report["completion_timestamp"], sample_rate_hz) // 500_000)
            window_indices.add(sample_ticks_to_ns(report["tx_timestamp"], sample_rate_hz) // 500_000)
            record.setdefault("wire_records", []).append(
                {key: (value.hex() if isinstance(value, bytes) else value) for key, value in report.items()}
            )
            received += 1
    reader_ids = tuple(record.get("config", {}).get("reader_ids", [1, 2, 3]))
    windows = window_indices or {0}
    for reader_id in reader_ids:
        for window_index in sorted(windows):
            record.setdefault("observations", []).append(service.closed_observation(reader_id=reader_id, window_index=window_index).to_dict())
    JsonExperimentStorage(args.output).save(record)
    return record


def _ingest_cbra_udp(args: argparse.Namespace) -> dict:
    """Capture v4 CBRA reports and aggregate only complete fixed-budget points."""
    rows: list[dict] = []
    measured = 0
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as listener:
        listener.bind((args.bind, args.port))
        listener.settimeout(args.timeout)
        while args.packets == 0 or measured < args.packets:
            try:
                data, _peer = listener.recvfrom(4096)
            except socket.timeout:
                break
            report = decode_cbra_observation_datagram(data)
            rows.append(cbra_observation_to_campaign_row(report, snr_db_x10=report["snr_db_x10"]))
            measured += not report["setup"]
    aggregate = aggregate_cbra_campaign_rows(rows)
    aggregate["raw_attempts"] = rows
    aggregate["outcome_summary"] = summarize_cbra_observation_outcomes(rows)
    JsonExperimentStorage(args.output).save(aggregate)
    return aggregate


def _write_reference(args: argparse.Namespace) -> None:
    points = [
        estimate_rician_energy_ber(
            duration_multiplier=multiplier,
            bits=args.bits,
            # Keep each duration's numerical sample independent; the measured
            # campaign also uses independent RFsim runs per duration/repeat.
            seed=args.seed + index,
            k_db=3.0,
            noise_power=0.1,
        )
        for index, multiplier in enumerate(args.multipliers)
    ]
    JsonExperimentStorage(args.output).save({"schema_version": 2, "reference_results": points})


def _campaign(args: argparse.Namespace) -> None:
    if args.input.suffix == ".jsonl":
        rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        value = json.loads(args.input.read_text(encoding="utf-8"))
        rows = value.get("rows", value) if isinstance(value, dict) else value
    if not isinstance(rows, list):
        raise ValueError("campaign input must be a JSON array, {rows: [...]}, or JSONL")
    aggregate = aggregate_cbra_campaign_rows(rows) if args.profile == "cbra" else aggregate_campaign_rows(rows)
    JsonExperimentStorage(args.output).save(aggregate)


def _plot(record: dict, output: Path, profile: str = "legacy") -> None:
    try:
        os.environ.setdefault("MPLCONFIGDIR", "/tmp/d2r-ber-matplotlib")
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise RuntimeError("matplotlib is required for plot") from error

    figure, axis = plt.subplots()
    if profile == "cbra":
        points = record.get("points", [])
        if not points or any(point.get("payload_ber") is None for point in points):
            raise ValueError("CBRA points must contain non-null control-bit BER values")
        for message_kind, m in sorted({(point["message_kind"], point["m"]) for point in points}):
            selected = sorted(
                (point for point in points if point["message_kind"] == message_kind and point["m"] == m),
                key=lambda point: point["snr_db_x10"],
            )
            axis.plot(
                [point["snr_db_x10"] / 10 for point in selected],
                [point["payload_ber"] for point in selected],
                marker="o",
                label=f"kind={message_kind}, M={m}",
            )
        axis.set_xlabel("SNR (dB), Tag ideal-acquisition reference plane")
        axis.set_ylabel("CBRA MAC/control-bit BER")
        axis.set_title("CBRA R2D; PRDCH-only power normalization; full-airtime goodput separate")
        axis.legend()
    else:
        points = record.get("duration_results", [])
        if not points or any(point.get("ber") is None for point in points):
            raise ValueError("duration_results must contain non-null duration_ns and ber values")
        durations = [point["duration_ns"] for point in points]
        bers = [point["ber"] for point in points]
        axis.plot(durations, bers, marker="o")
        axis.set_xlabel("D2R bit duration (ns)")
        axis.set_ylabel("BER")
    axis.grid(True)
    figure.tight_layout()
    figure.savefig(output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="write an editable empty measurement record")
    init.add_argument("--output", type=Path, required=True)
    init.add_argument("--tag-count", type=int, default=100)
    init.add_argument("--seed", type=int, default=1)
    init.add_argument("--sample-rate-hz", type=float, required=True)
    show = commands.add_parser("show", help="render a saved record")
    show.add_argument("--input", type=Path, required=True)
    plot = commands.add_parser("plot", help="plot saved duration BER values")
    plot.add_argument("--input", type=Path, required=True)
    plot.add_argument("--output", type=Path, required=True)
    plot.add_argument("--profile", choices=("legacy", "cbra"), default="legacy")
    ingest = commands.add_parser("ingest-udp", help="ingest fixed RFsim observation datagrams")
    ingest.add_argument("--input", type=Path, required=True)
    ingest.add_argument("--output", type=Path, required=True)
    ingest.add_argument("--bind", default="127.0.0.1")
    ingest.add_argument("--port", type=int, required=True)
    ingest.add_argument("--packets", type=int, default=0, help="0 waits until timeout")
    ingest.add_argument("--timeout", type=float, default=1.0)
    ingest.add_argument("--sample-rate-hz", type=float)
    ingest.add_argument("--profile", choices=("legacy", "cbra"), default="legacy")
    reference = commands.add_parser("reference", help="write the numerical model-matched BER reference")
    reference.add_argument("--output", type=Path, required=True)
    reference.add_argument("--bits", type=int, default=20_000)
    reference.add_argument("--seed", type=int, default=1)
    reference.add_argument("--multipliers", type=float, nargs="+", default=[1 / 96, 1 / 32, 1 / 16, 1 / 8, 1 / 4, 1 / 2, 1, 2])
    campaign = commands.add_parser("campaign", help="aggregate a fixed-budget RFsim campaign manifest")
    campaign.add_argument("--input", type=Path, required=True, help="JSON array/object or JSONL manifest")
    campaign.add_argument("--output", type=Path, required=True)
    campaign.add_argument("--profile", choices=("legacy", "cbra"), default="legacy")
    args = parser.parse_args(argv)

    if args.command == "init":
        if args.tag_count < 0 or args.sample_rate_hz <= 0:
            parser.error("tag-count must be non-negative and sample-rate-hz must be positive")
        JsonExperimentStorage(args.output).save(_init_record(args))
        print(f"saved editable record: {args.output}")
        return 0

    if args.command == "reference":
        if args.bits <= 0 or any(multiplier <= 0 for multiplier in args.multipliers):
            parser.error("bits and duration multipliers must be positive")
        _write_reference(args)
        print(f"saved numerical reference: {args.output}")
        return 0

    if args.command == "campaign":
        try:
            _campaign(args)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"campaign rejected: {error}", file=sys.stderr)
            return 2
        print(f"saved campaign aggregate: {args.output}")
        return 0

    if args.command == "ingest-udp":
        if args.packets < 0 or args.timeout <= 0:
            parser.error("packets must be non-negative and timeout must be positive")
        try:
            _ingest_udp(args)
        except (OSError, ValueError) as error:
            print(f"UDP ingest rejected: {error}", file=sys.stderr)
            return 2
        print(f"saved ingested record: {args.output}")
        return 0

    record = JsonExperimentStorage(args.input).load()
    if args.command == "show":
        print(render_status(record))
        return 0
    try:
        _plot(record, args.output, args.profile)
    except (RuntimeError, ValueError) as error:
        print(f"plot rejected: {error}", file=sys.stderr)
        return 2
    print(f"plot saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
