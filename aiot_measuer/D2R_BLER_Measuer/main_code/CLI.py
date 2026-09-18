"""Bash-launchable terminal UI for saved D2R BER measurement records."""

import argparse
import json
import os
from pathlib import Path
import sys

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
        "Reader  Window       BER        Bits   Errors  Valid  BER bar",
    ]
    for item in observations:
        ber = item.get("ber")
        rows.append(
            f"{item.get('reader_id', '?'):>6}  {item.get('window_index', '?'):>6}  "
            f"{('null' if ber is None else f'{ber:.6f}'):>9}  "
            f"{item.get('compared_bits', 0):>10}  {item.get('erroneous_bits', 0):>6}  "
            f"{str(item.get('valid', False)):>5}  {_bar(ber)}"
        )
    return "\n".join(rows)


def _init_record(args: argparse.Namespace) -> dict:
    return {
        "schema_version": 1,
        "config": {
            "reader_ids": [1, 2, 3],
            "tag_count": args.tag_count,
            "visibility_seed": args.seed,
            "sample_rate_hz": args.sample_rate_hz,
            "observation_window_ns": 500_000,
            "ideal_cross_reader_isolation": True,
            "ideal_acquisition_alignment": True,
        },
        "observations": [],
        "duration_results": [],
        "pending_decisions": [
            "RFsim sample-tick to nanosecond conversion",
            "D2R payload/framing and phase convention",
            "independent numerical BER reference and acceptance tolerance",
        ],
    }


def _plot(record: dict, output: Path) -> None:
    try:
        os.environ.setdefault("MPLCONFIGDIR", "/tmp/d2r-ber-matplotlib")
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise RuntimeError("matplotlib is required for plot") from error

    points = record.get("duration_results", [])
    if not points or any(point.get("ber") is None for point in points):
        raise ValueError("duration_results must contain non-null duration_ns and ber values")
    durations = [point["duration_ns"] for point in points]
    bers = [point["ber"] for point in points]
    figure, axis = plt.subplots()
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
    args = parser.parse_args(argv)

    if args.command == "init":
        if args.tag_count < 0 or args.sample_rate_hz <= 0:
            parser.error("tag-count must be non-negative and sample-rate-hz must be positive")
        JsonExperimentStorage(args.output).save(_init_record(args))
        print(f"saved editable record: {args.output}")
        return 0

    record = JsonExperimentStorage(args.input).load()
    if args.command == "show":
        print(render_status(record))
        return 0
    try:
        _plot(record, args.output)
    except (RuntimeError, ValueError) as error:
        print(f"plot rejected: {error}", file=sys.stderr)
        return 2
    print(f"plot saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
