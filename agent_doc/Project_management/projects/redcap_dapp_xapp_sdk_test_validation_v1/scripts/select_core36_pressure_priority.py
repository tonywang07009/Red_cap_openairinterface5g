#!/usr/bin/env python3
"""Select Gate E-Core36 dApp priority UE(s) from baseline smoke evidence."""

from __future__ import annotations

import argparse
import csv
import glob
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
SDK_DIR = ROOT / "openair2/E3AP/sdk"
DEFAULT_LOG_DIR = ROOT / "test_log/compiler_logs"
SMOKE_TIMESTAMP_RE = re.compile(r"mmtc_smoke_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_")
UE_LOG_RE = re.compile(r"_ue(\d+)_docker\.log$")

sys.path.insert(0, str(SDK_DIR))
from redcap_dapp_sdk import (  # noqa: E402
    REDCAP_DAPP_PROXY_BWP_PRBS_30KHZ,
    RedCapDappAccessPressureRequest,
    redcap_dapp_select_ra_pressure_priority,
)


@dataclass(frozen=True)
class UeEvidence:
    ue: int
    log_path: Path
    ra_retry_count: int
    msg3_failure_count: int
    pucch_resource_reject_count: int
    crc_discard_count: int
    priority_weight: int
    latency_status: str
    launch_to_tun_ms: int | None
    synthetic_rnti: int

    def request(self) -> RedCapDappAccessPressureRequest:
        return RedCapDappAccessPressureRequest(
            rnti=self.synthetic_rnti,
            bwp_prbs=REDCAP_DAPP_PROXY_BWP_PRBS_30KHZ,
            priority_weight=self.priority_weight,
            has_iq_samples=True,
            previous_pressure_permille=0,
            ra_retry_count=self.ra_retry_count,
            msg3_failure_count=self.msg3_failure_count,
            pucch_resource_reject_count=self.pucch_resource_reject_count,
            crc_discard_count=self.crc_discard_count,
        )


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def extract_ue_index(path: Path) -> int | None:
    match = UE_LOG_RE.search(path.name)
    return int(match.group(1)) if match else None


def count_matches(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def stage_run_log_from_summary(summary_log: Path, stage_ue_count: int) -> Path | None:
    text = read(summary_log)
    stage_log_pattern = re.compile(r"^\[STAGE\] log=(.+mmtc_stage_scan_.+_ue%d\.log)\s*$" % stage_ue_count, re.MULTILINE)
    matches = stage_log_pattern.findall(text)
    if not matches:
        return None
    return resolve(Path(matches[-1]))


def latency_log_from_run_log(run_log: Path) -> Path | None:
    text = read(run_log)
    match = re.search(r"Access latency CSV:\s*(.+mmtc_smoke_.+_access_latency\.csv)", text)
    if not match:
        return None
    return resolve(Path(match.group(1).strip()))


def timestamp_from_latency_log(latency_log: Path) -> str | None:
    match = SMOKE_TIMESTAMP_RE.search(latency_log.name)
    return match.group(1) if match else None


def load_latency_rows(latency_log: Path | None) -> dict[int, tuple[str, int | None]]:
    if latency_log is None or not latency_log.exists():
        return {}

    rows: dict[int, tuple[str, int | None]] = {}
    with latency_log.open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            ue_raw = row.get("ue", "")
            if not ue_raw.isdigit():
                continue
            latency_raw = row.get("launch_to_tun_ms", "")
            latency_ms = int(latency_raw) if latency_raw.isdigit() else None
            rows[int(ue_raw)] = (row.get("status", "missing"), latency_ms)
    return rows


def priority_weight_from_latency(latency_status: str, launch_to_tun_ms: int | None, text: str) -> int:
    weight = 0
    if latency_status != "tun":
        weight += 1000
    elif launch_to_tun_ms is not None:
        weight += min(900, launch_to_tun_ms // 1000)

    if "RRCSetupComplete" not in text:
        weight += 400
    if "PDU Session Establishment Accept" not in text and "PDU Session Setup" not in text:
        weight += 300
    return weight


def build_evidence(log_path: Path, latency_rows: dict[int, tuple[str, int | None]]) -> UeEvidence | None:
    ue = extract_ue_index(log_path)
    if ue is None:
        return None

    text = read(log_path)
    rar_success_count = count_matches(text, r"RAR-Msg2 decoded|Got RAPID RAR subPDU")
    explicit_ra_failures = count_matches(
        text,
        r"RA Procedure failed|Random Access.*fail|RAPROC.*fail|RAR.*(?:fail|timeout|miss)|RA response window",
    )
    msg3_failures = count_matches(text, r"Msg3.*(?:fail|retrans|timeout)|RA-Msg3.*(?:fail|retrans|timeout)")
    pucch_rejects = count_matches(text, r"PUCCH.*(?:reject|fail|resource)|SR.*(?:reject|fail)")
    crc_discards = count_matches(text, r"CRC.*(?:discard|fail)|discard.*CRC|invalid CCCH|bad DCI")
    ra_retry_count = explicit_ra_failures + max(0, rar_success_count - 1)
    latency_status, launch_to_tun_ms = latency_rows.get(ue, ("missing", None))
    priority_weight = priority_weight_from_latency(latency_status, launch_to_tun_ms, text)

    return UeEvidence(
        ue=ue,
        log_path=log_path,
        ra_retry_count=ra_retry_count,
        msg3_failure_count=msg3_failures,
        pucch_resource_reject_count=pucch_rejects,
        crc_discard_count=crc_discards,
        priority_weight=priority_weight,
        latency_status=latency_status,
        launch_to_tun_ms=launch_to_tun_ms,
        synthetic_rnti=0x2000 + ue,
    )


def select_top(candidates: list[UeEvidence], top_n: int) -> list[UeEvidence]:
    selected: list[UeEvidence] = []
    remaining = list(candidates)
    while remaining and len(selected) < top_n:
        selection = redcap_dapp_select_ra_pressure_priority([candidate.request() for candidate in remaining])
        if not selection.found:
            break
        selected.append(remaining.pop(selection.selected_index))
    return selected


def print_table(candidates: list[UeEvidence], selected: list[UeEvidence]) -> None:
    selected_ues = {candidate.ue for candidate in selected}
    print("# RedCap dApp RA pressure priority")
    print("# selection_rule=ra_retry_count,current_pressure,priority_weight,lower_rnti")
    print("ue,selected,synthetic_rnti,ra_retry_count,msg3_failure_count,pucch_resource_reject_count,"
          "crc_discard_count,priority_weight,latency_status,launch_to_tun_ms,log_path")
    for candidate in sorted(candidates, key=lambda item: item.ue):
        print(
            f"{candidate.ue},{int(candidate.ue in selected_ues)},0x{candidate.synthetic_rnti:04x},"
            f"{candidate.ra_retry_count},{candidate.msg3_failure_count},"
            f"{candidate.pucch_resource_reject_count},{candidate.crc_discard_count},"
            f"{candidate.priority_weight},{candidate.latency_status},"
            f"{candidate.launch_to_tun_ms if candidate.launch_to_tun_ms is not None else ''},"
            f"{candidate.log_path}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary-log", type=Path, help="mmtc_stage_scan summary log; auto-finds the ue36 run log")
    parser.add_argument("--run-log", type=Path, help="mmtc_stage_scan ue36 run log containing the smoke latency CSV path")
    parser.add_argument("--latency-log", type=Path, help="mmtc_smoke Launch-to-TUN latency CSV")
    parser.add_argument("--timestamp", help="mmtc_smoke timestamp, for example 2026-07-09_10-27-10")
    parser.add_argument("--ue-log-glob", help="override UE docker log glob")
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--stage-ue-count", type=int, default=36)
    parser.add_argument("--top-n", type=int, default=1)
    parser.add_argument("--emit-env-only", action="store_true", help="print only a comma-separated UE list")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_log = resolve(args.run_log) if args.run_log is not None else None
    if run_log is None and args.summary_log is not None:
        run_log = stage_run_log_from_summary(resolve(args.summary_log), args.stage_ue_count)
    latency_log = resolve(args.latency_log) if args.latency_log is not None else None
    if latency_log is None and run_log is not None:
        latency_log = latency_log_from_run_log(run_log)
    timestamp = args.timestamp or (timestamp_from_latency_log(latency_log) if latency_log is not None else None)

    if args.ue_log_glob:
        ue_log_pattern = str(resolve(Path(args.ue_log_glob)))
    elif timestamp:
        ue_log_pattern = str(resolve(args.log_dir) / f"mmtc_smoke_{timestamp}_ue*_docker.log")
    else:
        print("[FAIL] Provide --summary-log, --run-log, --latency-log, --timestamp, or --ue-log-glob", file=sys.stderr)
        return 1

    latency_rows = load_latency_rows(latency_log)
    log_paths = sorted(Path(path) for path in glob.glob(ue_log_pattern))
    candidates = [
        evidence
        for path in log_paths
        if (evidence := build_evidence(path, latency_rows)) is not None and evidence.ue <= args.stage_ue_count
    ]
    if not candidates:
        print(f"[FAIL] No UE docker logs matched core36 selector input: {ue_log_pattern}", file=sys.stderr)
        return 1

    selected = select_top(candidates, max(1, args.top_n))
    selected_list = ",".join(str(candidate.ue) for candidate in selected)
    if args.emit_env_only:
        print(selected_list)
        return 0

    print_table(candidates, selected)
    print(f"MMTC_DAPP_PRIORITY_UES={selected_list}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
