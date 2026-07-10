#!/usr/bin/env python3
"""Gate E preflight and runtime checker for RedCap dApp/xApp two-tier tests."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
PROJECT = ROOT / "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1"
COMPOSE_DIR = ROOT / "ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap"
COMPOSE_OVERLAY = COMPOSE_DIR / "docker-compose.mmtc.yml"
OVERLAY_GENERATOR = COMPOSE_DIR / "scripts/generate_mmtc_overlay.sh"
NRUE_RECAP_DIR = ROOT / "ci-scripts/conf_files/nrue_recap"
GNB_5MHZ_PROFILE = ROOT / "ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml"
GNB_20MHZ_PROXY_PROFILE = ROOT / "ci-scripts/conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml"
GATE_D_GNB_LOG = ROOT / "test_log/runtime_logs/gate_d_access_pressure_gnb_2026-07-07_00-47_local_no_csirs_srs.log"
GATE_D_UE_LOG = ROOT / "test_log/runtime_logs/gate_d_access_pressure_ue2_2026-07-07_00-47_local_no_csirs_srs.log"
GATE_E_FIRST32_GNB_LOG = ROOT / "test_log/compiler_logs/mmtc_smoke_2026-07-07_23-18-49_gnb.log"
GATE_E_FIRST32_SUMMARY_LOG = ROOT / "test_log/compiler_logs/mmtc_stage_scan_2026-07-07_23-18-49_summary.log"
CN_DB_GENERATOR = ROOT / "redcap_interface/generate_mmtc_cn_db_overlay.sh"
CN_DB_IMPL = ROOT / "redcap_interface/bash_library/fc_generate_mmtc_cn_db_overlay.sh"
SMOKE_WRAPPER = ROOT / "redcap_interface/bash_library/fc_mmtc_smoke_validation.sh"
EXPECTED_UE_COUNT = 64
CORE_UE_COUNT = 56
CORE36_UE_COUNT = 36
FIRST_STAGE_UE_COUNT = 32
STAGE_EXPECTED_UE_COUNT = {
    "core36-pressure": CORE36_UE_COUNT,
    "core56-ab": CORE_UE_COUNT,
    "first32": FIRST_STAGE_UE_COUNT,
    "full64": EXPECTED_UE_COUNT,
}


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def cn_db_sql_path(ue_count: int) -> Path:
    return ROOT / f"test_log/runtime_configs/oai_db_mmtc_{ue_count}.sql"


def cn_db_compose_path(ue_count: int) -> Path:
    return ROOT / f"test_log/runtime_configs/oai-cn5g_mmtc_{ue_count}.override.yml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def ue_indices_from_compose(text: str) -> set[int]:
    return {int(match.group(1)) for match in re.finditer(r"^  oai-nr-ue(\d+):", text, re.MULTILINE)}


def imsi_from_config(path: Path) -> str | None:
    match = re.search(r"^\s*imsi:\s*([0-9]+)\s*$", read(path), re.MULTILINE)
    return match.group(1) if match else None


def redcap_rntis(log_text: str) -> set[str]:
    patterns = [
        r"UE with RNTI ([0-9A-Fa-f]{4}) is RedCap",
        r"Create UE context:.*RNTI ([0-9A-Fa-f]{4})",
        r"\bRNTI ([0-9A-Fa-f]{4})\b",
    ]
    rntis: set[str] = set()
    for pattern in patterns:
        for match in re.finditer(pattern, log_text):
            rntis.add(match.group(1).lower())
    return rntis


def parse_summary_metrics(text: str) -> dict[str, int]:
    matches = re.findall(r"\b(sample|running|attach|pdu|tun|gnb_restart|failures)=([0-9]+)\b", text)
    return {key: int(value) for key, value in matches}


def has_xapp_control_success(text: str) -> bool:
    gnb_apply_marker = re.search(
        r"RedCap UL PRB control RNTI [0-9A-Fa-f]{4} requested [0-9]+ effective [0-9]+",
        text,
    )
    xapp_ack_marker = re.search(r"\bCONTROL ACK(?:NOWLEDGE)? rx\b", text)
    return bool(gnb_apply_marker or xapp_ack_marker or "CONTROL ACKNOWLEDGE rx" in text)


def check_stage_summary(summary_log_path: Path, required_ue_count: int, errors: list[str]) -> None:
    if not summary_log_path.exists():
        errors.append(f"missing Gate E stage summary log: {rel(summary_log_path)}")
        return

    metrics = parse_summary_metrics(read(summary_log_path))
    for key in ["sample", "running", "attach", "pdu", "tun", "gnb_restart", "failures"]:
        require(key in metrics, f"Gate E stage summary missing metric: {key}", errors)
    if not metrics:
        return

    require(metrics.get("sample", 0) >= required_ue_count,
            f"Gate E stage summary sample={metrics.get('sample', 0)}, expected at least {required_ue_count}", errors)
    require(metrics.get("running", 0) >= required_ue_count,
            f"Gate E stage summary running={metrics.get('running', 0)}, expected at least {required_ue_count}", errors)
    require(metrics.get("attach", 0) >= required_ue_count,
            f"Gate E stage summary attach={metrics.get('attach', 0)}, expected at least {required_ue_count}", errors)
    require(metrics.get("pdu", 0) >= required_ue_count,
            f"Gate E stage summary pdu={metrics.get('pdu', 0)}, expected at least {required_ue_count}", errors)
    require(metrics.get("tun", 0) >= required_ue_count,
            f"Gate E stage summary tun={metrics.get('tun', 0)}, expected at least {required_ue_count}", errors)
    require(metrics.get("gnb_restart", 1) == 0,
            f"Gate E stage summary gnb_restart={metrics.get('gnb_restart', 'missing')}, expected 0", errors)
    require(metrics.get("failures", 1) == 0,
            f"Gate E stage summary failures={metrics.get('failures', 'missing')}, expected 0", errors)


def latency_success_count(latency_log_path: Path, required_ue_count: int, errors: list[str], label: str) -> int:
    rows, success_rows = latency_status_counts(latency_log_path, required_ue_count, errors, label)
    require(success_rows >= required_ue_count,
            f"Gate E {label} latency success rows={success_rows}, expected at least {required_ue_count}", errors)
    return success_rows


def latency_status_counts(
    latency_log_path: Path,
    required_ue_count: int,
    errors: list[str],
    label: str,
) -> tuple[int, int]:
    if not latency_log_path.exists():
        errors.append(f"missing Gate E {label} latency log: {rel(latency_log_path)}")
        return 0, 0

    with latency_log_path.open(newline="", encoding="utf-8", errors="replace") as handle:
        rows = list(csv.DictReader(handle))
    success_rows = [
        row for row in rows
        if row.get("status") == "tun" and row.get("launch_to_tun_ms", "").isdigit()
    ]
    require(len(rows) >= required_ue_count,
            f"Gate E {label} latency rows={len(rows)}, expected at least {required_ue_count}", errors)
    return len(rows), len(success_rows)


def check_core36_summary_shape(text: str, label: str, errors: list[str]) -> dict[str, int]:
    require("stage_profile=core36_pressure" in text,
            f"Gate E core36-pressure {label} summary missing stage_profile=core36_pressure", errors)
    require("total_ues_target=56" in text,
            f"Gate E core36-pressure {label} summary missing total_ues_target=56", errors)
    require("stages=36" in text,
            f"Gate E core36-pressure {label} summary missing stages=36", errors)
    require("ue_start_gap=0" in text,
            f"Gate E core36-pressure {label} summary missing ue_start_gap=0", errors)
    require("adaptive_burst_on_zero_gap=0" in text,
            f"Gate E core36-pressure {label} summary missing adaptive_burst_on_zero_gap=0", errors)

    metrics = parse_summary_metrics(text)
    for key in ["sample", "running", "attach", "pdu", "tun", "gnb_restart", "failures"]:
        require(key in metrics, f"Gate E core36-pressure {label} summary missing metric: {key}", errors)
    require(metrics.get("sample", 0) >= CORE36_UE_COUNT,
            f"Gate E core36-pressure {label} sample={metrics.get('sample', 0)}, expected at least {CORE36_UE_COUNT}",
            errors)
    require(metrics.get("running", 0) >= CORE36_UE_COUNT,
            f"Gate E core36-pressure {label} running={metrics.get('running', 0)}, expected at least {CORE36_UE_COUNT}",
            errors)
    require(metrics.get("gnb_restart", 1) == 0,
            f"Gate E core36-pressure {label} gnb_restart={metrics.get('gnb_restart', 'missing')}, expected 0",
            errors)
    return metrics


def check_core56_ab(args: argparse.Namespace, errors: list[str]) -> None:
    required_paths = [
        ("baseline summary", args.baseline_summary_log),
        ("dApp summary", args.dapp_summary_log),
        ("baseline latency", args.baseline_latency_log),
        ("dApp latency", args.dapp_latency_log),
        ("dApp gNB log", args.dapp_gnb_log),
    ]
    for label, path in required_paths:
        if path is None:
            errors.append(f"Gate E core56-ab requires --{label.replace(' ', '-').lower()}")
            return
        if not path.exists():
            errors.append(f"missing Gate E core56-ab {label}: {rel(path)}")
            return

    check_stage_summary(args.baseline_summary_log, CORE_UE_COUNT, errors)
    check_stage_summary(args.dapp_summary_log, CORE_UE_COUNT, errors)
    baseline_success = latency_success_count(args.baseline_latency_log, CORE_UE_COUNT, errors, "baseline")
    dapp_success = latency_success_count(args.dapp_latency_log, CORE_UE_COUNT, errors, "dApp")
    require(baseline_success == dapp_success,
            f"Gate E core56-ab latency success counts differ: baseline={baseline_success}, dApp={dapp_success}", errors)

    dapp_log = read(args.dapp_gnb_log)
    require(any(marker in dapp_log for marker in [
                "RedCap dApp access pressure policy",
                "access-pressure policy",
                "[RedCap dApp Gate E][PUCCH pressure]",
                "RedCap dApp PRB decision",
            ]),
            "Gate E core56-ab dApp gNB log missing dApp decision/pressure marker", errors)
    require("Aborted" not in dapp_log and "Assertion" not in dapp_log,
            "Gate E core56-ab dApp gNB log contains abort/assert evidence", errors)


def check_core36_pressure(args: argparse.Namespace, errors: list[str]) -> None:
    required_paths = [
        ("baseline summary", args.baseline_summary_log),
        ("dApp summary", args.dapp_summary_log),
        ("baseline latency", args.baseline_latency_log),
        ("dApp latency", args.dapp_latency_log),
        ("dApp gNB log", args.dapp_gnb_log),
    ]
    for label, path in required_paths:
        if path is None:
            errors.append(f"Gate E core36-pressure requires --{label.replace(' ', '-').lower()}")
            return
        if not path.exists():
            errors.append(f"missing Gate E core36-pressure {label}: {rel(path)}")
            return

    baseline_summary = read(args.baseline_summary_log)
    dapp_summary = read(args.dapp_summary_log)
    baseline_metrics = check_core36_summary_shape(baseline_summary, "baseline", errors)
    dapp_metrics = check_core36_summary_shape(dapp_summary, "dApp", errors)
    dapp_priority_match = re.search(r"\bdapp_priority_ues=([^ \n]+)", dapp_summary)
    require("dapp_stop_non_priority=1" in dapp_summary,
            "Gate E core36-pressure dApp summary missing dapp_stop_non_priority=1", errors)
    require("dapp_ra_retry_priority=1" in dapp_summary,
            "Gate E core36-pressure dApp summary missing dapp_ra_retry_priority=1", errors)
    require(dapp_priority_match is not None and dapp_priority_match.group(1) != "none",
            "Gate E core36-pressure dApp summary did not record selected priority UE(s)", errors)

    for key in ["attach", "pdu", "tun", "running"]:
        require(dapp_metrics.get(key, 0) >= baseline_metrics.get(key, 0),
                f"Gate E core36-pressure dApp {key}={dapp_metrics.get(key, 0)} below baseline {baseline_metrics.get(key, 0)}",
                errors)
    require(dapp_metrics.get("failures", 9999) <= baseline_metrics.get("failures", 9999),
            f"Gate E core36-pressure dApp failures={dapp_metrics.get('failures', 'missing')} above baseline {baseline_metrics.get('failures', 'missing')}",
            errors)

    _, baseline_success = latency_status_counts(args.baseline_latency_log, CORE36_UE_COUNT, errors, "baseline")
    _, dapp_success = latency_status_counts(args.dapp_latency_log, CORE36_UE_COUNT, errors, "dApp")
    require(dapp_success >= baseline_success,
            f"Gate E core36-pressure dApp latency success rows={dapp_success} below baseline={baseline_success}", errors)

    dapp_log = read(args.dapp_gnb_log)
    require(any(marker in dapp_log for marker in [
                "RedCap dApp RA retry priority",
                "RedCap dApp RA pressure priority",
                "RedCap dApp PRB decision",
            ]),
            "Gate E core36-pressure dApp gNB log missing RA retry/pressure priority or PRB decision marker", errors)
    require("Aborted" not in dapp_log and "Assertion" not in dapp_log,
            "Gate E core36-pressure dApp gNB log contains abort/assert evidence", errors)


def check_static_preflight(errors: list[str], expected_ue_count: int) -> None:
    cn_db_sql = cn_db_sql_path(expected_ue_count)
    cn_db_compose = cn_db_compose_path(expected_ue_count)
    for path in [
        COMPOSE_OVERLAY,
        OVERLAY_GENERATOR,
        NRUE_RECAP_DIR,
        GNB_5MHZ_PROFILE,
        GNB_20MHZ_PROXY_PROFILE,
        PROJECT / "scripts/gate_d_rfsim_marker_check.py",
        CN_DB_GENERATOR,
        CN_DB_IMPL,
        SMOKE_WRAPPER,
        cn_db_sql,
        cn_db_compose,
        GATE_D_GNB_LOG,
        GATE_D_UE_LOG,
    ]:
        require(path.exists(), f"missing Gate E preflight path: {rel(path)}", errors)

    if COMPOSE_OVERLAY.exists():
        overlay = read(COMPOSE_OVERLAY)
        indices = ue_indices_from_compose(overlay)
        expected = set(range(1, expected_ue_count + 1))
        missing = sorted(expected - indices)
        extra = sorted(index for index in indices if index > EXPECTED_UE_COUNT)
        require(len(indices) >= expected_ue_count,
                f"mMTC overlay exposes {len(indices)} UE services, expected at least {expected_ue_count}", errors)
        require(not missing, f"mMTC overlay missing UE services: {missing}", errors)
        require(not extra, f"mMTC overlay has unexpected UE services above 64: {extra}", errors)
        require(f"oai-nr-ue{expected_ue_count}:" in overlay,
                f"mMTC overlay missing oai-nr-ue{expected_ue_count} service", errors)
        require(f'MMTC_UE_INDEX: "{expected_ue_count}"' in overlay,
                f"mMTC overlay missing UE{expected_ue_count} MMTC_UE_INDEX", errors)
        require(f"nrue{expected_ue_count}.uicc.yaml:/opt/oai-nr-ue/etc/nr-ue.yaml:ro" in overlay,
                f"mMTC overlay missing UE{expected_ue_count} RedCap config mount", errors)
        require("OAI_REDCAP_DAPP_GATE_D_MARKER" in overlay,
                "mMTC overlay missing dApp marker env passthrough", errors)
        require("OAI_REDCAP_DAPP_RA_RETRY_PRIORITY" in overlay,
                "mMTC overlay missing dApp RA retry-priority env passthrough", errors)

    if OVERLAY_GENERATOR.exists():
        generator = read(OVERLAY_GENERATOR)
        for needle in [
            "TOTAL_UES",
            "BASE_FIXED_UE_COUNT",
            "OAI_REDCAP_DAPP_GATE_D_MARKER",
            "OAI_REDCAP_DAPP_RA_RETRY_PRIORITY",
            "MMTC_GNB_EXTRA_OPTIONS",
            "nrue${idx}.uicc.yaml",
        ]:
            require(needle in generator, f"overlay generator missing text: {needle}", errors)

    missing_configs: list[int] = []
    imsis: list[str] = []
    for idx in range(1, expected_ue_count + 1):
        config = NRUE_RECAP_DIR / f"nrue{idx}.uicc.yaml"
        if not config.exists():
            missing_configs.append(idx)
            continue
        imsi = imsi_from_config(config)
        require(imsi is not None, f"UE{idx} config missing IMSI: {rel(config)}", errors)
        if imsi is not None:
            imsis.append(imsi)
    require(not missing_configs, f"missing RedCap UE configs: {missing_configs}", errors)
    require(len(set(imsis)) == expected_ue_count,
            f"expected {expected_ue_count} unique IMSIs, found {len(set(imsis))}", errors)

    if GNB_5MHZ_PROFILE.exists():
        five_mhz = read(GNB_5MHZ_PROFILE)
        for needle in [
            "dl_carrierBandwidth: 106",
            "ul_carrierBandwidth: 106",
            "bwpSize: 12",
            "initialDLBWPSize_r17: 12",
            "initialULBWPSize_r17: 12",
        ]:
            require(needle in five_mhz, f"5 MHz Gate E profile missing text: {needle}", errors)

    if GNB_20MHZ_PROXY_PROFILE.exists():
        twenty_mhz = read(GNB_20MHZ_PROXY_PROFILE)
        for needle in [
            "dl_carrierBandwidth: 51",
            "ul_carrierBandwidth: 51",
            "initialDLBWPSize_r17: 51",
            "initialULBWPSize_r17: 51",
        ]:
            require(needle in twenty_mhz, f"20 MHz proxy profile missing text: {needle}", errors)

    if CN_DB_IMPL.exists():
        cn_generator = read(CN_DB_IMPL)
        for needle in [
            "AuthenticationSubscription",
            "SessionManagementSubscriptionData",
            "TOTAL_UES",
            "001010%09d",
        ]:
            require(needle in cn_generator, f"CN DB generator missing text: {needle}", errors)

    if cn_db_sql.exists():
        cn_sql = read(cn_db_sql)
        cn_imsis = set(re.findall(r"001010[0-9]{9}", cn_sql))
        require(len(cn_imsis) == expected_ue_count,
                f"CN DB SQL has {len(cn_imsis)} unique UE IMSIs, expected {expected_ue_count}", errors)
        last_imsi = f"001010{expected_ue_count:09d}"
        require(last_imsi in cn_imsis, f"CN DB SQL missing UE{expected_ue_count} IMSI", errors)

    if cn_db_compose.exists():
        cn_compose = read(cn_db_compose)
        require("zz_oai_db_mmtc.sql" in cn_compose, "CN compose overlay missing DB init mount", errors)
        require(f"oai_db_mmtc_{expected_ue_count}.sql" in cn_compose,
                f"CN compose overlay missing {expected_ue_count} UE SQL path", errors)

    if SMOKE_WRAPPER.exists():
        smoke_wrapper = read(SMOKE_WRAPPER)
        for needle in [
            "apply_radio_profile_defaults",
            "51PRB",
            "3617640000",
            "238",
            "MMTC_RF_FREQ",
            "MMTC_SSB_START",
        ]:
            require(needle in smoke_wrapper, f"mMTC smoke wrapper missing 51PRB RF/SSB default text: {needle}", errors)

    if GATE_D_GNB_LOG.exists():
        gate_d_log = read(GATE_D_GNB_LOG)
        require("[RedCap dApp Gate D][gNB MAC UL]" in gate_d_log,
                "Gate E preflight requires prior Gate D UL marker evidence", errors)
        require("[RedCap dApp Gate D][gNB MAC PUCCH]" in gate_d_log,
                "Gate E preflight requires prior Gate D PUCCH marker evidence", errors)
        require("bwp_prbs 12" in gate_d_log, "Gate E preflight requires prior 12 PRB Gate D evidence", errors)


def check_runtime_log(
    gnb_log_path: Path,
    stage: str,
    required_ue_count: int,
    errors: list[str],
    control_log_paths: list[Path] | None = None,
) -> None:
    if not gnb_log_path.exists():
        errors.append(f"missing Gate E gNB runtime log: {rel(gnb_log_path)}")
        return

    log = read(gnb_log_path)
    rntis = redcap_rntis(log)
    require(len(rntis) >= required_ue_count,
            f"Gate E runtime has {len(rntis)} unique RedCap RNTIs, expected at least {required_ue_count}", errors)
    if stage != "full64":
        require(any(marker in log for marker in ["bwp_prbs 12", "dl_bwp_size 12", "ul_bwp_size 12"]),
                "Gate E runtime missing first-stage 5 MHz / 12 PRB evidence", errors)
    if stage == "full64":
        require(any(marker in log for marker in ["BWP 1, start PRB 0 size 51", "bwp_size 51", "20 MHz"]),
                "Gate E runtime missing later-stage 20 MHz / 51 PRB expansion evidence", errors)
        control_text = log
        for path in control_log_paths or []:
            if path.exists():
                control_text += "\n" + read(path)
        require(has_xapp_control_success(control_text),
                "Gate E runtime missing xApp control or ACK marker", errors)
    require(any(marker in log for marker in [
                "RedCap dApp access pressure policy",
                "access-pressure policy",
                "[RedCap dApp Gate E][PUCCH pressure]",
                "RedCap dApp PRB decision",
            ]),
            "Gate E runtime missing dApp access-pressure policy marker", errors)
    require("Aborted" not in log and "Assertion" not in log,
            "Gate E runtime log contains abort/assert evidence", errors)


def print_next_commands() -> None:
    services_first = " ".join(f"oai-nr-ue{i}" for i in range(1, FIRST_STAGE_UE_COUNT + 1))
    services_all = " ".join(f"oai-nr-ue{i}" for i in range(1, EXPECTED_UE_COUNT + 1))
    print("[INFO] Gate E preflight command:")
    print("  python3 -B "
          "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/"
          "gate_e_64ue_stage_check.py")
    print("[INFO] Gate E runtime evidence check command shape:")
    print("  python3 -B "
          "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/"
          "gate_e_64ue_stage_check.py --stage full64 \\")
    print("    --gnb-log test_log/compiler_logs/mmtc_smoke_<timestamp>_gnb.log \\")
    print("    --summary-log test_log/compiler_logs/mmtc_stage_scan_<timestamp>_summary.log \\")
    print("    --xapp-log test_log/compiler_logs/mmtc_smoke_<timestamp>_xapp-rc-moni.log \\")
    print("    --ric-log test_log/compiler_logs/mmtc_smoke_<timestamp>_nearRT-RIC.log")
    print("[INFO] Gate E-Core 56 UE A/B latency evidence check command shape:")
    print("  python3 -B "
          "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/"
          "gate_e_64ue_stage_check.py --stage core56-ab \\")
    print("    --baseline-summary-log test_log/compiler_logs/mmtc_stage_scan_<baseline>_summary.log \\")
    print("    --dapp-summary-log test_log/compiler_logs/mmtc_stage_scan_<dapp>_summary.log \\")
    print("    --baseline-latency-log test_log/compiler_logs/mmtc_smoke_<baseline>_access_latency.csv \\")
    print("    --dapp-latency-log test_log/compiler_logs/mmtc_smoke_<dapp>_access_latency.csv \\")
    print("    --dapp-gnb-log test_log/compiler_logs/mmtc_smoke_<dapp>_gnb.log")
    print("[INFO] Gate E-Core 36 UE zero-gap pressure command shape:")
    print("  MMTC_STAGE_PROFILE=core36_pressure MMTC_START_XAPP=0 MMTC_USE_EXISTING_CN_DB=0 \\")
    print("  MMTC_N_RB_DL=51 GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml \\")
    print('  MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \\')
    print("  bash redcap_interface/redcap_mmtc_stage_scan.sh")
    print("  python3 -B "
          "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/"
          "select_core36_pressure_priority.py \\")
    print("    --summary-log test_log/compiler_logs/mmtc_stage_scan_<baseline>_summary.log")
    print("  MMTC_STAGE_PROFILE=core36_pressure MMTC_START_XAPP=1 MMTC_USE_EXISTING_CN_DB=0 \\")
    print("  OAI_REDCAP_DAPP_GATE_D_MARKER=1 OAI_REDCAP_DAPP_RA_RETRY_PRIORITY=1 \\")
    print("  MMTC_DAPP_STOP_NON_PRIORITY=1 MMTC_DAPP_PRIORITY_UES=<top-ue-list> \\")
    print("  MMTC_N_RB_DL=51 GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml \\")
    print('  MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \\')
    print("  bash redcap_interface/redcap_mmtc_stage_scan.sh")
    print("[INFO] regenerate 64 UE overlay:")
    print("  bash ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh 64")
    print("[INFO] regenerate 64 UE CN DB overlay:")
    print("  bash redcap_interface/generate_mmtc_cn_db_overlay.sh 64")
    print("[INFO] one-UE 51PRB RF/SSB alignment smoke command shape:")
    print("  MMTC_TOTAL_UES=64 MMTC_SAMPLE_UES=1 MMTC_START_XAPP=1 MMTC_USE_EXISTING_CN_DB=0 \\")
    print("  MMTC_N_RB_DL=51 GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml \\")
    print("  OAI_REDCAP_DAPP_GATE_D_MARKER=1 \\")
    print('  MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \\')
    print("  bash redcap_interface/redcap_mmtc_smoke_validation.sh")
    print("[INFO] first-stage 32 UE RFsim command shape:")
    print("  cd ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap")
    print("  REGISTRY= TAG=latest GNB_IMG=oai-gnb NRUE_IMG=oai-nr-ue \\")
    print("  GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml \\")
    print("  MMTC_N_RB_DL=106 OAI_REDCAP_DAPP_GATE_D_MARKER=1 \\")
    print('  MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \\')
    print(f"  docker compose -f docker-compose.yml -f docker-compose.mmtc.yml up -d --force-recreate oai-gnb {services_first}")
    print("[INFO] later-stage 64 UE / 20 MHz proxy command shape:")
    print("  REGISTRY= TAG=latest GNB_IMG=oai-gnb NRUE_IMG=oai-nr-ue \\")
    print("  GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml \\")
    print("  MMTC_N_RB_DL=51 OAI_REDCAP_DAPP_GATE_D_MARKER=1 \\")
    print('  MMTC_GNB_EXTRA_OPTIONS="--gNBs.[0].do_CSIRS 0 --gNBs.[0].do_SRS 0" \\')
    print(f"  docker compose -f docker-compose.yml -f docker-compose.mmtc.yml up -d --force-recreate oai-gnb {services_all}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=sorted(STAGE_EXPECTED_UE_COUNT), default="full64")
    parser.add_argument("--gnb-log", type=Path, help="Gate E gNB runtime log to scan")
    parser.add_argument("--summary-log", type=Path, help="Gate E stage summary log to scan")
    parser.add_argument("--first-stage-gnb-log", type=Path, default=GATE_E_FIRST32_GNB_LOG)
    parser.add_argument("--first-stage-summary-log", type=Path, default=GATE_E_FIRST32_SUMMARY_LOG)
    parser.add_argument("--xapp-log", type=Path, help="optional xApp log to scan for control/ACK evidence")
    parser.add_argument("--ric-log", type=Path, help="optional nearRT-RIC log to scan for control/ACK evidence")
    parser.add_argument("--baseline-summary-log", type=Path, help="Gate E-Core baseline stage summary log")
    parser.add_argument("--dapp-summary-log", type=Path, help="Gate E-Core dApp-enabled stage summary log")
    parser.add_argument("--baseline-latency-log", type=Path, help="Gate E-Core baseline Launch-to-TUN latency CSV")
    parser.add_argument("--dapp-latency-log", type=Path, help="Gate E-Core dApp-enabled Launch-to-TUN latency CSV")
    parser.add_argument("--dapp-gnb-log", type=Path, help="Gate E-Core dApp-enabled gNB log")
    parser.add_argument("--require-runtime", action="store_true", help="fail when --gnb-log is not provided")
    parser.add_argument("--required-ue-count", type=int)
    args = parser.parse_args()

    errors: list[str] = []
    required_ue_count = args.required_ue_count or STAGE_EXPECTED_UE_COUNT[args.stage]
    has_runtime_evidence = args.gnb_log is not None or args.baseline_summary_log is not None
    static_ue_count = EXPECTED_UE_COUNT if has_runtime_evidence and args.stage == "full64" else CORE_UE_COUNT
    check_static_preflight(errors, static_ue_count)

    if args.stage == "core36-pressure":
        check_core36_pressure(args, errors)
    elif args.stage == "core56-ab":
        check_core56_ab(args, errors)
    elif args.gnb_log is not None:
        if args.summary_log is None:
            errors.append("Gate E runtime validation requires --summary-log with attach/PDU/TUN metrics")
        else:
            check_stage_summary(args.summary_log, required_ue_count, errors)
        if args.stage == "full64":
            check_stage_summary(args.first_stage_summary_log, FIRST_STAGE_UE_COUNT, errors)
            check_runtime_log(args.first_stage_gnb_log, "first32", FIRST_STAGE_UE_COUNT, errors)
        control_logs = [path for path in [args.xapp_log, args.ric_log] if path is not None]
        check_runtime_log(args.gnb_log, args.stage, required_ue_count, errors, control_logs)
    elif args.require_runtime:
        print("[BLOCKED] Gate E runtime log was not provided")
        print_next_commands()
        return 2

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        print_next_commands()
        return 1

    if args.stage == "core36-pressure" and args.baseline_summary_log is not None:
        print("[PASS] Gate E-Core36 zero-gap pressure A/B evidence found")
    elif args.stage == "core56-ab" and args.baseline_summary_log is not None:
        print("[PASS] Gate E-Core 56 UE A/B latency evidence found")
    elif args.gnb_log is None:
        print("[PASS] Gate E static preflight is ready for two-tier RFsim validation")
        print("[INFO] Runtime evidence checks require --stage plus log/CSV arguments")
        print_next_commands()
    else:
        print(f"[PASS] Gate E {args.stage} runtime evidence found in {rel(args.gnb_log)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
