#!/usr/bin/env python3
"""Deterministic traffic traces and the 30-sample adaptive DRX predictor."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


SCHEMA_VERSION = 1
ARRIVALS_PER_CAMPAIGN = 330
WARMUP_ARRIVALS = 30
SCORED_ARRIVALS = 300
ARRIVALS_PER_WINDOW = 30
MIN_INTERVAL_US = 300_000
MAX_INTERVAL_US = 10_240_000
WINDOW_MEANS_MS = (640, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400)
STDDEV_FRACTION = 0.10

STYLE_ID = 2
ACTION_ID = 1
LONG_CYCLE_PARAMETER_ID = 1
REQUEST_MARKER = "[RedCap DRX][xApp request]"


@dataclass(frozen=True)
class DrxProfile:
    profile_id: str
    long_cycle_ms: int
    on_duration_ms: int


APPROVED_PROFILES = (
    DrxProfile("drx-320-10", 320, 10),
    DrxProfile("drx-640-10", 640, 10),
    DrxProfile("drx-1280-20", 1280, 20),
    DrxProfile("drx-2560-20", 2560, 20),
    DrxProfile("drx-5120-40", 5120, 40),
    DrxProfile("drx-10240-40", 10240, 40),
)
FALLBACK_PROFILE = APPROVED_PROFILES[0]


@dataclass(frozen=True)
class WindowStatistics:
    sample_count: int
    mean_interval_us: float
    stddev_interval_us: float
    lower_3sigma_us: float
    upper_3sigma_us: float
    median_interval_us: float
    p95_interval_us: int
    minimum_interval_us: int
    maximum_interval_us: int


@dataclass(frozen=True)
class PolicyIntent:
    schema_version: int
    campaign_id: str
    direction: str
    window_id: int
    policy_version: int
    ric_request_id: int
    rnti: int
    sample_count: int
    prediction_status: str
    selected_profile_id: str
    previous_profile_id: str
    valid_for_arrivals: int
    short_drx_enabled: bool
    drx_inactivity_timer_ms: int
    drx_slot_offset_1_over_32_ms: int
    statistics: WindowStatistics
    e2sm_rc_request: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        record = asdict(self)
        stats = record.pop("statistics")
        record.update(stats)
        return record


def _stable_direction_seed(trace_seed: int, direction: str) -> int:
    digest = hashlib.sha256(f"adaptive-c-drx-v1:{trace_seed}:{direction}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


def generate_intervals(trace_seed: int, direction: str) -> list[int]:
    """Generate the frozen eleven-window truncated-normal interval population."""
    if direction not in {"downlink", "uplink"}:
        raise ValueError(f"unsupported direction: {direction}")
    rng = random.Random(_stable_direction_seed(trace_seed, direction))
    intervals: list[int] = []
    for mean_ms in WINDOW_MEANS_MS:
        for _ in range(ARRIVALS_PER_WINDOW):
            interval_us = round(rng.normalvariate(mean_ms, mean_ms * STDDEV_FRACTION) * 1000)
            intervals.append(min(MAX_INTERVAL_US, max(MIN_INTERVAL_US, interval_us)))
    assert len(intervals) == ARRIVALS_PER_CAMPAIGN
    return intervals


def write_trace(path: Path, trace_seed: int, direction: str, start_epoch_us: int) -> None:
    if start_epoch_us < 0:
        raise ValueError("start_epoch_us must be non-negative")
    path.parent.mkdir(parents=True, exist_ok=True)
    source_role = "iperf_server" if direction == "downlink" else "redcap_ue"
    scheduled_us = start_epoch_us
    fieldnames = (
        "arrival_id",
        "window_id",
        "phase",
        "scored_arrival_id",
        "direction",
        "traffic_source",
        "interval_us",
        "scheduled_source_tx_time_us",
    )
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for index, interval_us in enumerate(generate_intervals(trace_seed, direction), start=1):
            scheduled_us += interval_us
            writer.writerow(
                {
                    "arrival_id": index,
                    "window_id": (index - 1) // ARRIVALS_PER_WINDOW,
                    "phase": "warmup" if index <= WARMUP_ARRIVALS else "scored",
                    "scored_arrival_id": "" if index <= WARMUP_ARRIVALS else index - WARMUP_ARRIVALS,
                    "direction": direction,
                    "traffic_source": source_role,
                    "interval_us": interval_us,
                    "scheduled_source_tx_time_us": scheduled_us,
                }
            )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def write_campaign_manifest(
    output_dir: Path,
    trace_seed: int,
    start_epoch_us: int,
) -> Path:
    """Write paired A/B campaign entries that reference one trace per direction."""
    output_dir.mkdir(parents=True, exist_ok=True)
    traces: dict[str, dict[str, object]] = {}
    for direction in ("downlink", "uplink"):
        trace_path = output_dir / f"adaptive_drx_{direction}_trace.csv"
        write_trace(trace_path, trace_seed, direction, start_epoch_us)
        traces[direction] = {
            "path": trace_path.name,
            "sha256": file_sha256(trace_path),
            "trace_seed": trace_seed,
            "start_epoch_us": start_epoch_us,
        }

    campaigns = []
    for direction, suffix in (("downlink", "dl"), ("uplink", "ul")):
        for arm in ("A", "B"):
            campaign = {
                "id": f"arm-{arm.lower()}-{suffix}",
                "arm": arm,
                "direction": direction,
                "trace": traces[direction],
            }
            if arm == "A":
                campaign["control_mode"] = "fixed_local_rrc"
                campaign["initial_profile"] = asdict(FALLBACK_PROFILE)
                campaign["baseline_policy_version"] = 1
                campaign["required_markers"] = [
                    "[RedCap DRX][gNB applied]",
                    "Configured Connected DRX",
                    "Received RRCReconfigurationComplete",
                ]
            else:
                campaign["control_mode"] = "adaptive_e2sm_rc"
                campaign["initial_profile"] = asdict(FALLBACK_PROFILE)
                campaign["required_markers"] = [
                    REQUEST_MARKER,
                    "[RedCap DRX][E2 ACK]",
                    "[RedCap DRX][dApp ACCEPT]",
                    "[RedCap DRX][gNB applied]",
                    "Configured Connected DRX",
                    "Received RRCReconfigurationComplete",
                ]
            campaigns.append(campaign)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "experiment": "adaptive_c_drx_ab_v1",
        "trace_seed": trace_seed,
        "population": {
            "arrivals_per_campaign": ARRIVALS_PER_CAMPAIGN,
            "warmup_arrivals": WARMUP_ARRIVALS,
            "scored_arrivals": SCORED_ARRIVALS,
            "arrivals_per_window": ARRIVALS_PER_WINDOW,
            "minimum_interval_us": MIN_INTERVAL_US,
            "maximum_interval_us": MAX_INTERVAL_US,
        },
        "traffic": {
            "tool": "iperf2",
            "transport": "udp",
            "bytes_per_burst": 32768,
            "payload_bytes": 1200,
            "target_bitrate_bps": 10_000_000,
            "schedule_option": "--txstart-time",
            "latency_option": "--trip-times",
        },
        "campaigns": campaigns,
        "approved_profiles": [asdict(profile) for profile in APPROVED_PROFILES],
        "claim_boundary": "rf_simulation_energy_proxies_only",
    }
    manifest_path = output_dir / "adaptive_drx_campaign_manifest_v1.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def rebase_campaign_manifest(manifest_path: Path, output_dir: Path, start_epoch_us: int) -> Path:
    """Clone the frozen interval population with a new absolute start time."""
    if start_epoch_us < 0:
        raise ValueError("start_epoch_us must be non-negative")
    if output_dir.resolve() == manifest_path.parent.resolve():
        raise ValueError("rebase output directory must preserve the source manifest")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != SCHEMA_VERSION or manifest.get("experiment") != "adaptive_c_drx_ab_v1":
        raise ValueError("unsupported adaptive DRX manifest")

    source_intervals: dict[str, list[int]] = {}
    for campaign in manifest.get("campaigns", []):
        if not isinstance(campaign, dict) or campaign.get("direction") not in {"downlink", "uplink"}:
            raise ValueError("manifest campaign is invalid")
        trace_record = campaign.get("trace")
        if not isinstance(trace_record, dict):
            raise ValueError("campaign trace record is missing")
        trace_path = manifest_path.parent / str(trace_record["path"])
        if file_sha256(trace_path) != trace_record.get("sha256"):
            raise ValueError(f"trace checksum mismatch: {trace_path}")
        rows = read_trace(trace_path)
        direction = str(campaign["direction"])
        intervals = [int(row["interval_us"]) for row in rows]
        if direction in source_intervals and source_intervals[direction] != intervals:
            raise ValueError(f"paired {direction} campaigns do not share one interval population")
        source_intervals[direction] = intervals

    if set(source_intervals) != {"downlink", "uplink"}:
        raise ValueError("manifest must contain paired downlink and uplink traces")

    rebased_path = write_campaign_manifest(output_dir, int(manifest["trace_seed"]), start_epoch_us)
    rebased = json.loads(rebased_path.read_text(encoding="utf-8"))
    for direction, suffix in (("downlink", "dl"), ("uplink", "ul")):
        campaign = find_campaign(rebased, f"arm-a-{suffix}")
        trace_path = rebased_path.parent / str(campaign["trace"]["path"])
        if [int(row["interval_us"]) for row in read_trace(trace_path)] != source_intervals[direction]:
            raise RuntimeError(f"rebased {direction} interval population changed")
    rebased["rebase"] = {
        "source_manifest_sha256": file_sha256(manifest_path),
        "start_epoch_us": start_epoch_us,
    }
    rebased_path.write_text(json.dumps(rebased, indent=2) + "\n", encoding="utf-8")
    return rebased_path


def summarize_window(samples: Sequence[int]) -> WindowStatistics:
    if len(samples) != ARRIVALS_PER_WINDOW:
        raise ValueError(f"expected {ARRIVALS_PER_WINDOW} samples, got {len(samples)}")
    if any(sample < MIN_INTERVAL_US or sample > MAX_INTERVAL_US for sample in samples):
        raise ValueError("interval outside the frozen 300 ms..10.24 s boundary")
    ordered = sorted(samples)
    mean_us = statistics.fmean(samples)
    stddev_us = statistics.stdev(samples)
    return WindowStatistics(
        sample_count=len(samples),
        mean_interval_us=mean_us,
        stddev_interval_us=stddev_us,
        lower_3sigma_us=mean_us - 3 * stddev_us,
        upper_3sigma_us=mean_us + 3 * stddev_us,
        median_interval_us=statistics.median(samples),
        p95_interval_us=ordered[math.ceil(0.95 * len(ordered)) - 1],
        minimum_interval_us=ordered[0],
        maximum_interval_us=ordered[-1],
    )


def select_profile(lower_3sigma_us: float) -> tuple[DrxProfile, bool]:
    eligible = [profile for profile in APPROVED_PROFILES if profile.long_cycle_ms * 1000 <= lower_3sigma_us]
    return (eligible[-1], False) if eligible else (FALLBACK_PROFILE, True)


def make_rc_request(ric_request_id: int, rnti: int, policy_version: int, profile: DrxProfile) -> dict[str, object]:
    """Represent the standard RC fields without inventing an OnDuration parameter."""
    return {
        "ric_request_id": ric_request_id,
        "rnti": rnti,
        "policy_version": policy_version,
        "control_service_style_id": STYLE_ID,
        "control_action_id": ACTION_ID,
        "ran_parameters": [
            {
                "id": LONG_CYCLE_PARAMETER_ID,
                "name": "Long DRX Cycle Length",
                "value_ms": profile.long_cycle_ms,
                "encoding_status": "needs_verification_against_ts_38_473",
            }
        ],
        "marker": REQUEST_MARKER,
    }


class AdaptiveDrxPredictor:
    """Keep one 30-arrival window until its policy is explicitly accepted."""

    def __init__(self) -> None:
        self._samples: list[int] = []
        self._pending: PolicyIntent | None = None

    @property
    def samples(self) -> tuple[int, ...]:
        return tuple(self._samples)

    @property
    def ready(self) -> bool:
        return len(self._samples) == ARRIVALS_PER_WINDOW

    def observe(self, interval_us: int) -> None:
        if interval_us < MIN_INTERVAL_US or interval_us > MAX_INTERVAL_US:
            raise ValueError("interval outside the frozen 300 ms..10.24 s boundary")
        if self.ready:
            raise RuntimeError("the current 30-sample window must be resolved before another sample")
        self._samples.append(interval_us)

    def propose(
        self,
        *,
        campaign_id: str,
        direction: str,
        window_id: int,
        policy_version: int,
        ric_request_id: int,
        rnti: int,
        previous_profile_id: str,
    ) -> PolicyIntent:
        if not self.ready:
            raise RuntimeError(f"predictor needs {ARRIVALS_PER_WINDOW} samples")
        if self._pending is not None:
            raise RuntimeError("a policy decision is already pending")
        if direction not in {"downlink", "uplink"}:
            raise ValueError(f"unsupported direction: {direction}")
        if policy_version <= 0 or ric_request_id < 0 or rnti <= 0:
            raise ValueError("policy_version and rnti must be positive; ric_request_id must be non-negative")
        if previous_profile_id not in {profile.profile_id for profile in APPROVED_PROFILES}:
            raise ValueError(f"unsupported previous profile: {previous_profile_id}")

        stats = summarize_window(self._samples)
        prediction_out_of_range = stats.lower_3sigma_us < MIN_INTERVAL_US or stats.upper_3sigma_us > MAX_INTERVAL_US
        profile, used_fallback = (
            (FALLBACK_PROFILE, True) if prediction_out_of_range else select_profile(stats.lower_3sigma_us)
        )
        if prediction_out_of_range:
            status = "fallback"
        elif stats.stddev_interval_us == 0:
            status = "zero_variance"
        elif used_fallback:
            status = "fallback"
        else:
            status = "predicted"
        self._pending = PolicyIntent(
            schema_version=SCHEMA_VERSION,
            campaign_id=campaign_id,
            direction=direction,
            window_id=window_id,
            policy_version=policy_version,
            ric_request_id=ric_request_id,
            rnti=rnti,
            sample_count=ARRIVALS_PER_WINDOW,
            prediction_status=status,
            selected_profile_id=profile.profile_id,
            previous_profile_id=previous_profile_id,
            valid_for_arrivals=ARRIVALS_PER_WINDOW,
            short_drx_enabled=False,
            drx_inactivity_timer_ms=20,
            drx_slot_offset_1_over_32_ms=0,
            statistics=stats,
            e2sm_rc_request=make_rc_request(ric_request_id, rnti, policy_version, profile),
        )
        return self._pending

    def resolve(self, accepted: bool) -> None:
        if self._pending is None:
            raise RuntimeError("no pending policy decision")
        self._pending = None
        if accepted:
            self._samples.clear()


def read_trace(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != ARRIVALS_PER_CAMPAIGN:
        raise ValueError(f"trace must contain {ARRIVALS_PER_CAMPAIGN} arrivals, got {len(rows)}")
    return rows


def find_campaign(manifest: dict[str, object], campaign_id: str) -> dict[str, object]:
    campaigns = manifest.get("campaigns")
    if not isinstance(campaigns, list):
        raise ValueError("manifest campaigns must be a list")
    for campaign in campaigns:
        if isinstance(campaign, dict) and campaign.get("id") == campaign_id:
            return campaign
    raise ValueError(f"unknown campaign: {campaign_id}")


def write_receive_csv(manifest_path: Path, campaign_id: str, capture_path: Path, output_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    campaign = find_campaign(manifest, campaign_id)
    trace_record = campaign.get("trace")
    if not isinstance(trace_record, dict):
        raise ValueError("campaign trace record is missing")
    trace_path = manifest_path.parent / str(trace_record["path"])
    if file_sha256(trace_path) != trace_record.get("sha256"):
        raise ValueError(f"trace checksum mismatch: {trace_path}")
    trace = read_trace(trace_path)

    packet_pattern = re.compile(r"^\s*(\d+)(?:\.(\d+))?\s+IP\s+\S+\.(\d+)\s+>\s+\S+\.(\d+):")
    packet_flows: list[list[int]] = []
    previous_flow: tuple[int, int] | None = None
    for line in capture_path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = packet_pattern.match(line)
        if match is None:
            continue
        source_port = int(match.group(3))
        destination_port = int(match.group(4))
        if 5001 not in {source_port, destination_port}:
            continue
        flow = (source_port, destination_port)
        fraction = (match.group(2) or "")[:6].ljust(6, "0")
        timestamp_us = int(match.group(1)) * 1_000_000 + int(fraction)
        if flow != previous_flow:
            packet_flows.append([])
            previous_flow = flow
        packet_flows[-1].append(timestamp_us)

    if len(packet_flows) != ARRIVALS_PER_CAMPAIGN:
        raise ValueError(
            f"capture must contain {ARRIVALS_PER_CAMPAIGN} sequential iPerf2 flows, got {len(packet_flows)}"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("campaign_id", "arrival_id", "source_receive_time_us"))
        writer.writeheader()
        for row, packet_times_us in zip(trace[WARMUP_ARRIVALS:], packet_flows[WARMUP_ARRIVALS:]):
            scheduled_us = int(row["scheduled_source_tx_time_us"])
            receive_time_us = next((timestamp for timestamp in packet_times_us if timestamp >= scheduled_us), None)
            if receive_time_us is None:
                raise ValueError(f"capture flow for arrival {row['arrival_id']} has no packet at or after its scheduled epoch")
            writer.writerow(
                {
                    "campaign_id": campaign_id,
                    "arrival_id": row["arrival_id"],
                    "source_receive_time_us": receive_time_us,
                }
            )


def _generate_command(args: argparse.Namespace) -> int:
    manifest_path = write_campaign_manifest(args.output_dir, args.trace_seed, args.start_epoch_us)
    print(manifest_path)
    return 0


def _rebase_command(args: argparse.Namespace) -> int:
    manifest_path = rebase_campaign_manifest(args.manifest, args.output_dir, args.start_epoch_us)
    print(manifest_path)
    return 0


def _receive_csv_command(args: argparse.Namespace) -> int:
    write_receive_csv(args.manifest, args.campaign_id, args.capture_log, args.output)
    print(args.output)
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(required=True)
    generate = subparsers.add_parser("generate", help="write paired DL/UL traces and a JSON run manifest")
    generate.add_argument("--output-dir", type=Path, required=True)
    generate.add_argument("--trace-seed", type=int, required=True)
    generate.add_argument("--start-epoch-us", type=int, required=True)
    generate.set_defaults(handler=_generate_command)
    rebase = subparsers.add_parser("rebase", help="clone a manifest with fresh absolute traffic timestamps")
    rebase.add_argument("--manifest", type=Path, required=True)
    rebase.add_argument("--output-dir", type=Path, required=True)
    rebase.add_argument("--start-epoch-us", type=int, required=True)
    rebase.set_defaults(handler=_rebase_command)
    receive_csv = subparsers.add_parser("receive-csv", help="correlate filtered tcpdump timestamps to scored arrivals")
    receive_csv.add_argument("--manifest", type=Path, required=True)
    receive_csv.add_argument("--campaign-id", required=True)
    receive_csv.add_argument("--capture-log", type=Path, required=True)
    receive_csv.add_argument("--output", type=Path, required=True)
    receive_csv.set_defaults(handler=_receive_csv_command)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
