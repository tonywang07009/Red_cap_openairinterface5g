#!/usr/bin/env python3
"""Gate D source and RFsim marker checker for the RedCap dApp/xApp SDK."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
GNB_ULSCH = ROOT / "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c"
GNB_UCI = ROOT / "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_uci.c"
CMAKE = ROOT / "CMakeLists.txt"
PROJECT = ROOT / "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1"


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_source_hook(errors: list[str]) -> None:
    for path in [
        GNB_ULSCH,
        GNB_UCI,
        CMAKE,
        ROOT / "openair2/E3AP/sdk/redcap_dapp_sdk.c",
        ROOT / "openair2/E3AP/sdk/redcap_dapp_sdk.h",
        ROOT / "dev_refer/dapp_dev_need/E3Controller/README.md",
        ROOT / "dev_refer/dapp_dev_need/E3Controller/src/e3sm/iq_pipeline.h",
        ROOT / "dev_refer/dapp_dev_need/E3Controller/src/e3sm/slot_iq_pipeline.h",
        ROOT / "dev_refer/dapp_dev_need/libe3/README.md",
        ROOT / "dev_refer/dapp_dev_need/dApp-library/README.md",
        ROOT / "ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml",
        ROOT / "ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh",
    ]:
        require(path.exists(), f"missing source/reference path: {rel(path)}", errors)

    if not GNB_ULSCH.exists() or not GNB_UCI.exists() or not CMAKE.exists():
        return

    gnb = read(GNB_ULSCH)
    uci = read(GNB_UCI)
    cmake = read(CMAKE)
    config_idx = gnb.find("config_uldci(")
    call_idx = gnb.find("nr_redcap_dapp_note_gate_d_ul_prb_decision(UE, frame, slot")
    for needle in [
        "OAI_REDCAP_DAPP_GATE_D_MARKER",
        "redcap_dapp_guard_prb_allocation",
        "gNB-side apply marker",
        "RedCap dApp Gate D",
        "frequency_domain_assignment",
    ]:
        require(needle in gnb, f"gNB ULSCH hook missing text: {needle}", errors)
    require(config_idx >= 0 and call_idx > config_idx,
            "Gate D marker call must appear after config_uldci() in post_process_ulsch()", errors)

    configure_pucch_idx = uci.find("nr_configure_pucch(")
    pucch_call_idx = uci.find("nr_redcap_dapp_note_gate_d_pucch_decision(frame, slot, pucch, pucch_pdu, UE)")
    for needle in [
        "OAI_REDCAP_DAPP_GATE_D_MARKER",
        "redcap_dapp_guard_prb_allocation",
        "gNB-side PUCCH marker",
        "RedCap dApp Gate D",
        "prb_start",
        "prb_size",
    ]:
        require(needle in uci, f"gNB UCI PUCCH hook missing text: {needle}", errors)
    require(configure_pucch_idx >= 0 and pucch_call_idx > configure_pucch_idx,
            "Gate D PUCCH marker call must appear after nr_configure_pucch()", errors)
    require("redcap_dapp_sdk.c" in cmake, "CMakeLists.txt must compile redcap_dapp_sdk.c into MAC_NR_SRC", errors)

    compose = read(ROOT / "ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml")
    generator = read(ROOT / "ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh")
    for path_name, text in [
        ("docker-compose.mmtc.yml", compose),
        ("generate_mmtc_overlay.sh", generator),
    ]:
        require("OAI_REDCAP_DAPP_GATE_D_MARKER" in text,
                f"{path_name} must expose OAI_REDCAP_DAPP_GATE_D_MARKER to the gNB container", errors)


def check_runtime_log(log_path: Path, require_bwp_prbs: int, errors: list[str]) -> None:
    if not log_path.exists():
        errors.append(f"missing Gate D runtime log: {rel(log_path)}")
        return

    log = read(log_path)
    for needle in [
        "[RedCap dApp Gate D][gNB MAC UL]",
        "[RedCap dApp Gate D][gNB MAC PUCCH]",
        "gNB-side apply marker",
        "gNB-side PUCCH marker",
        "RedCap dApp PRB decision",
    ]:
        require(needle in log, f"runtime log missing marker: {needle}", errors)

    if require_bwp_prbs > 0:
        require(f"bwp_prbs {require_bwp_prbs}" in log,
                f"runtime log missing required BWP marker: bwp_prbs {require_bwp_prbs}", errors)

    require("dApp PRB decision rejected" not in log or "gNB-side apply marker" in log,
            "runtime log contains only rejected Gate D dApp PRB decisions", errors)


def print_next_runtime_command(require_bwp_prbs: int) -> None:
    bwp_arg = f" --require-bwp-prbs {require_bwp_prbs}" if require_bwp_prbs > 0 else ""
    print("[INFO] next Gate D RFsim marker command shape:")
    print("  OAI_REDCAP_DAPP_GATE_D_MARKER=1 <start gNB/UE RFsim command>")
    print("  python3 -B "
          "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/"
          f"gate_d_rfsim_marker_check.py --gnb-log <gNB-log-path> --require-runtime{bwp_arg}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gnb-log", type=Path, help="RFsim gNB log to scan for Gate D markers")
    parser.add_argument("--require-runtime", action="store_true", help="return blocked when no runtime log is provided")
    parser.add_argument("--require-bwp-prbs", type=int, default=0, help="require a specific bwp_prbs marker in the runtime log")
    args = parser.parse_args()

    errors: list[str] = []
    check_source_hook(errors)

    if args.gnb_log is not None:
        check_runtime_log(args.gnb_log, args.require_bwp_prbs, errors)
    elif args.require_runtime:
        print("[BLOCKED] Gate D RFsim runtime log was not provided")
        print_next_runtime_command(args.require_bwp_prbs)
        return 2

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        print_next_runtime_command(args.require_bwp_prbs)
        return 1

    if args.gnb_log is None:
        print("[PASS] Gate D source hook readiness is present")
        print("[INFO] RFsim runtime evidence is still pending")
        print_next_runtime_command(args.require_bwp_prbs)
    else:
        print(f"[PASS] Gate D RFsim marker evidence found in {rel(args.gnb_log)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
