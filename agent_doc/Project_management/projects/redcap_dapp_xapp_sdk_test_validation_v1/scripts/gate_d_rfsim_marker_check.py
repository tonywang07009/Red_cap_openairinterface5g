#!/usr/bin/env python3
"""Gate D source and RFsim marker checker for the RedCap dApp/xApp SDK."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
GNB_ULSCH = ROOT / "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c"
GNB_UCI = ROOT / "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_uci.c"
GNB_RA = ROOT / "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c"
UE_DCI = ROOT / "openair2/LAYER2/NR_MAC_UE/nr_ue_dci_configuration.c"
CMAKE = ROOT / "CMakeLists.txt"
PROJECT = ROOT / "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1"
GNB_5MHZ_BWP_PROFILE = ROOT / "ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml"
FIVE_MHZ_BWP_MHZ = 5
FIVE_MHZ_BWP_PRB_MARKERS = (11, 12)
FIVE_MHZ_BWP_RUNTIME_MARKERS = (
    "bwp_prbs 11",
    "bwp_prbs 12",
    "dl_bwp_size 12",
    "ul_bwp_size 12",
    "bwp_size 12",
)


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
        GNB_RA,
        UE_DCI,
        CMAKE,
        ROOT / "openair2/E3AP/sdk/redcap_dapp_sdk.c",
        ROOT / "openair2/E3AP/sdk/redcap_dapp_sdk.h",
        ROOT / "Apps_dev/dapp_dev_need/E3Controller/README.md",
        ROOT / "Apps_dev/dapp_dev_need/E3Controller/src/e3sm/iq_pipeline.h",
        ROOT / "Apps_dev/dapp_dev_need/E3Controller/src/e3sm/slot_iq_pipeline.h",
        ROOT / "Apps_dev/dapp_dev_need/libe3/README.md",
        ROOT / "Apps_dev/dapp_dev_need/dApp-library/README.md",
        GNB_5MHZ_BWP_PROFILE,
        ROOT / "redcap_interface/bash_library/generate_mmtc_overlay.sh",
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

    gnb_ra = read(GNB_RA)
    ue_dci = read(UE_DCI)
    for needle in [
        "msg2_common_dci_bwp_size",
        "redcap_ra_common_nonzero_coreset ? dl_bwp->BWPSize : nr_mac->cset0_bwp_size",
    ]:
        require(needle in gnb_ra, f"gNB RA Msg2 DCI BWP-size alignment missing text: {needle}", errors)
    for needle in [
        "common_dci_bwp_size",
        "redcap_ra_common_nonzero_coreset ? current_DL_BWP->BWPSize : mac->type0_PDCCH_CSS_config.num_rbs",
    ]:
        require(needle in ue_dci, f"UE RA DCI BWP-size alignment missing text: {needle}", errors)

    generator = read(ROOT / "redcap_interface/bash_library/generate_mmtc_overlay.sh")
    require("OAI_REDCAP_DAPP_GATE_D_MARKER" in generator,
            "generate_mmtc_overlay.sh must expose OAI_REDCAP_DAPP_GATE_D_MARKER to the gNB container", errors)

    profile = read(GNB_5MHZ_BWP_PROFILE)
    for needle in [
        "dl_carrierBandwidth: 106",
        "ul_carrierBandwidth: 106",
        "first_active_bwp: 1",
        "bwpSize: 12",
        "redCapInitialBWP_r17:",
        "initialDLBWPSize_r17: 12",
        "initialULBWPSize_r17: 12",
        "initialDLBWPSubcarrierSpacing_r17: 1",
        "initialULBWPSubcarrierSpacing_r17: 1",
        "coreset0_redcap_mode_r17: 1",
    ]:
        require(needle in profile, f"5 MHz BWP profile missing text: {needle}", errors)


def first_dci_bits(log: str, marker: str) -> int | None:
    for line in log.splitlines():
        if marker not in line:
            continue
        match = re.search(r"\bdci_bits (\d+)\b", line)
        if match:
            return int(match.group(1))
    return None


def check_runtime_log(
    log_path: Path,
    ue_log_path: Path | None,
    require_bwp_prbs: int,
    require_bwp_mhz: int,
    errors: list[str],
) -> None:
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

    if require_bwp_mhz == FIVE_MHZ_BWP_MHZ:
        expected = ", ".join(FIVE_MHZ_BWP_RUNTIME_MARKERS)
        require(any(marker in log for marker in FIVE_MHZ_BWP_RUNTIME_MARKERS),
                f"runtime log missing required 5 MHz BWP marker: expected one of {expected}", errors)
    elif require_bwp_mhz > 0:
        errors.append(f"unsupported Gate D BWP MHz requirement: {require_bwp_mhz}")

    require("dApp PRB decision rejected" not in log or "gNB-side apply marker" in log,
            "runtime log contains only rejected Gate D dApp PRB decisions", errors)

    if ue_log_path is not None:
        if not ue_log_path.exists():
            errors.append(f"missing Gate D UE runtime log: {rel(ue_log_path)}")
            return
        ue_log = read(ue_log_path)
        gnb_dci_bits = first_dci_bits(log, "[RedCap RA][gNB Msg2 DCI]")
        ue_dci_bits = first_dci_bits(ue_log, "[RedCap RA][UE DCI cfg]")
        require(gnb_dci_bits is not None, "gNB runtime log missing RedCap Msg2 DCI bit-length marker", errors)
        require(ue_dci_bits is not None, "UE runtime log missing RedCap RA DCI bit-length marker", errors)
        if gnb_dci_bits is not None and ue_dci_bits is not None:
            require(gnb_dci_bits == ue_dci_bits,
                    f"gNB/UE RedCap RA DCI bit-length mismatch: gNB {gnb_dci_bits}, UE {ue_dci_bits}", errors)


def print_next_runtime_command(require_bwp_prbs: int, require_bwp_mhz: int) -> None:
    bwp_arg = f" --require-bwp-prbs {require_bwp_prbs}" if require_bwp_prbs > 0 else ""
    bwp_arg += f" --require-bwp-mhz {require_bwp_mhz}" if require_bwp_mhz > 0 else ""
    print("[INFO] next Gate D RFsim marker command shape:")
    print("  GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml \\")
    print("  MMTC_N_RB_DL=106 OAI_REDCAP_DAPP_GATE_D_MARKER=1 <start gNB/UE RFsim command>")
    print("  python3 -B "
          "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/"
          f"gate_d_rfsim_marker_check.py --gnb-log <gNB-log-path> --ue-log <UE-log-path> --require-runtime{bwp_arg}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gnb-log", type=Path, help="RFsim gNB log to scan for Gate D markers")
    parser.add_argument("--ue-log", type=Path, help="RFsim UE log to scan for RedCap RA DCI bit-length alignment")
    parser.add_argument("--require-runtime", action="store_true", help="return blocked when no runtime log is provided")
    parser.add_argument("--require-bwp-prbs", type=int, default=0, help="require a specific bwp_prbs marker in the runtime log")
    parser.add_argument("--require-bwp-mhz", type=int, default=0, help="require a BWP MHz profile marker in the runtime log")
    args = parser.parse_args()

    errors: list[str] = []
    check_source_hook(errors)

    if args.gnb_log is not None:
        check_runtime_log(args.gnb_log, args.ue_log, args.require_bwp_prbs, args.require_bwp_mhz, errors)
    elif args.require_runtime:
        print("[BLOCKED] Gate D RFsim runtime log was not provided")
        print_next_runtime_command(args.require_bwp_prbs, args.require_bwp_mhz)
        return 2

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        print_next_runtime_command(args.require_bwp_prbs, args.require_bwp_mhz)
        return 1

    if args.gnb_log is None:
        print("[PASS] Gate D source hook readiness is present")
        print("[INFO] RFsim dApp marker PASS evidence is still pending")
        print_next_runtime_command(args.require_bwp_prbs, args.require_bwp_mhz)
    else:
        print(f"[PASS] Gate D RFsim marker evidence found in {rel(args.gnb_log)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
