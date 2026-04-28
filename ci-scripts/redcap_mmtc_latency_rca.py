#!/usr/bin/env python3

"""Summarize RedCap mMTC RFsim latency and TCP bottleneck evidence."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from statistics import mean


RTT_RE = re.compile(r"rtt min/avg/max/mdev = ([0-9.]+)/([0-9.]+)/([0-9.]+)/([0-9.]+) ms")
IPERF_LINE_RE = re.compile(
    r"\[\s*\d+\]\s+([0-9.]+)-([0-9.]+)\s+sec\s+.+?\s+([0-9.]+)\s+Mbits/sec(?:\s+\d+)?\s+(sender|receiver)$",
    re.MULTILINE,
)
IPERF_ERROR_RE = re.compile(r"iperf3: error - (?P<error>.+)")
SUMMARY_RE = re.compile(r"\[SUMMARY\].+")
UE_STATS_RE = re.compile(r"^(?P<wall>[0-9.]+)\s+\[NR_MAC\]\s+I UE .* stats sfn: (?P<frame>\d+)\.(?P<slot>\d+),")


@dataclass
class IperfResult:
    path: Path
    sender_mbps: float | None = None
    receiver_mbps: float | None = None
    error: str | None = None


@dataclass
class DriftResult:
    path: Path
    samples: int
    wall_seconds: float
    sim_seconds: float

    @property
    def wall_to_sim_ratio(self) -> float:
        if self.sim_seconds <= 0:
            return 0.0
        return self.wall_seconds / self.sim_seconds


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log-dir",
        default="test_log/compiler_logs",
        help="Directory containing mMTC stage and smoke logs.",
    )
    parser.add_argument(
        "--timestamp",
        required=True,
        help="Timestamp prefix such as 2026-04-28_12-05-26.",
    )
    parser.add_argument(
        "--output",
        help="Optional Markdown output file. Prints to stdout when omitted.",
    )
    return parser.parse_args()


def collect_summary(log_dir: Path, timestamp: str) -> list[str]:
    """Collect stage summary lines for one timestamp."""
    summaries: list[str] = []
    for path in sorted(log_dir.glob(f"mmtc_stage_scan_{timestamp}_*.log")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if SUMMARY_RE.search(line):
                summaries.append(f"{path.name}: {line}")
    return summaries


def collect_rtts(log_dir: Path, timestamp: str) -> list[float]:
    """Collect ping average RTT values in milliseconds."""
    values: list[float] = []
    for path in sorted(log_dir.glob(f"mmtc_smoke_{timestamp}_ue*_ping.log")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in RTT_RE.finditer(text):
            values.append(float(match.group(2)))
    return values


def collect_iperf(log_dir: Path, timestamp: str) -> list[IperfResult]:
    """Collect iperf sender/receiver summaries and errors."""
    results: list[IperfResult] = []
    for path in sorted(log_dir.glob(f"mmtc_smoke_{timestamp}_ue*_iperf3_ul.log")):
        result = IperfResult(path=path)
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in IPERF_ERROR_RE.finditer(text):
            result.error = match.group("error")
        for match in IPERF_LINE_RE.finditer(text):
            bitrate = float(match.group(3))
            role = match.group(4)
            if role == "sender":
                result.sender_mbps = bitrate
            elif role == "receiver":
                result.receiver_mbps = bitrate
        results.append(result)
    return results


def sfn_diff_frames(prev_frame: int, next_frame: int) -> int:
    """Return frame delta with 1024-frame SFN wrap handling."""
    if next_frame >= prev_frame:
        return next_frame - prev_frame
    return 1024 - prev_frame + next_frame


def collect_drift(log_dir: Path, timestamp: str) -> list[DriftResult]:
    """Estimate wall-clock to simulated-time drift from UE MAC stats lines."""
    results: list[DriftResult] = []
    for path in sorted(log_dir.glob(f"mmtc_smoke_{timestamp}_ue*_docker.log")):
        points: list[tuple[float, int]] = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = UE_STATS_RE.search(line)
            if not match:
                continue
            points.append((float(match.group("wall")), int(match.group("frame"))))

        if len(points) < 2:
            continue

        wall_seconds = points[-1][0] - points[0][0]
        frame_delta = 0
        for (_, prev_frame), (_, next_frame) in zip(points, points[1:]):
            frame_delta += sfn_diff_frames(prev_frame, next_frame)
        sim_seconds = frame_delta * 0.01
        results.append(
            DriftResult(
                path=path,
                samples=len(points),
                wall_seconds=wall_seconds,
                sim_seconds=sim_seconds,
            )
        )
    return results


def fmt_float(value: float) -> str:
    """Format a float with stable precision."""
    return f"{value:.3f}"


def percentile(values: list[float], pct: float) -> float:
    """Return a simple nearest-rank percentile."""
    if not values:
        return 0.0
    ordered = sorted(values)
    index = round((len(ordered) - 1) * pct)
    return ordered[index]


def build_report(log_dir: Path, timestamp: str) -> str:
    """Build a Markdown RCA report."""
    summaries = collect_summary(log_dir, timestamp)
    rtts = collect_rtts(log_dir, timestamp)
    iperfs = collect_iperf(log_dir, timestamp)
    drifts = collect_drift(log_dir, timestamp)

    lines = [
        "# RedCap mMTC Latency RCA",
        f"- Timestamp: {timestamp}",
        f"- Log Dir: {log_dir}",
        "",
        "## Stage Summary",
    ]
    if summaries:
        lines.extend(f"- {line}" for line in summaries)
    else:
        lines.append("- No summary line found.")

    lines.extend(["", "## Ping RTT"])
    if rtts:
        lines.append(f"- Samples: {len(rtts)}")
        lines.append(f"- Avg RTT ms: {fmt_float(mean(rtts))}")
        lines.append(f"- Min RTT ms: {fmt_float(min(rtts))}")
        lines.append(f"- P50 RTT ms: {fmt_float(percentile(rtts, 0.50))}")
        lines.append(f"- P95 RTT ms: {fmt_float(percentile(rtts, 0.95))}")
        lines.append(f"- Max RTT ms: {fmt_float(max(rtts))}")
    else:
        lines.append("- No ping RTT samples found.")

    lines.extend(["", "## TCP iperf3"])
    if iperfs:
        lines.append("| Log | Sender Mbps | Receiver Mbps | Error |")
        lines.append("|-----|-------------|---------------|-------|")
        for result in iperfs:
            sender = "" if result.sender_mbps is None else fmt_float(result.sender_mbps)
            receiver = "" if result.receiver_mbps is None else fmt_float(result.receiver_mbps)
            error = result.error or ""
            lines.append(f"| {result.path.name} | {sender} | {receiver} | {error} |")
    else:
        lines.append("- No iperf3 logs found.")

    lines.extend(["", "## UE Sim-Time Drift"])
    if drifts:
        lines.append("| Log | Samples | Wall Seconds | Sim Seconds | Wall/Sim Ratio |")
        lines.append("|-----|---------|--------------|-------------|----------------|")
        for result in sorted(drifts, key=lambda item: item.wall_to_sim_ratio, reverse=True)[:10]:
            lines.append(
                f"| {result.path.name} | {result.samples} | {fmt_float(result.wall_seconds)} | "
                f"{fmt_float(result.sim_seconds)} | {fmt_float(result.wall_to_sim_ratio)} |"
            )
    else:
        lines.append("- No UE MAC stats drift samples found.")

    lines.extend(
        [
            "",
            "## RCA Hint",
            "- High RTT with low TCP receiver Mbps and low retransmission count points to scheduling latency or RFsim process-time drift.",
            "- A high Wall/Sim Ratio indicates the UE softmodem is advancing radio frames slower than real time.",
            "- If stop-quiesce restores TCP throughput, idle RFsim UE processes are still consuming enough host/RFsim time to affect the active UE.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    """Run the RCA summarizer."""
    args = parse_args()
    report = build_report(Path(args.log_dir), args.timestamp)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
