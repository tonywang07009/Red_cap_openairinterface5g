#!/usr/bin/env python3
"""Static checks for RedCap dApp/xApp SDK test validation."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
PROJECT = ROOT / "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def require_path(path: str, errors: list[str]) -> None:
    require((ROOT / path).exists(), f"missing path: {path}", errors)


def require_text(path: str, needle: str, errors: list[str]) -> None:
    require(needle in read(path), f"{path} missing text: {needle}", errors)


def reject_text(path: str, needle: str, errors: list[str]) -> None:
    require(needle not in read(path), f"{path} has stale text: {needle}", errors)


def check_reference_paths(errors: list[str]) -> None:
    for path in [
        "dev_refer/dapp_dev_need/libe3",
        "dev_refer/dapp_dev_need/dApp-library",
        "dev_refer/dapp_dev_need/dApp-openairinterface5g",
        "dev_refer/xapp_dev_need",
        "openair2/E2AP/flexric",
    ]:
        require_path(path, errors)


def check_sdk_symbols(errors: list[str]) -> None:
    for path in [
        "openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.h",
        "openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.c",
        "openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.py",
        "openair2/E3AP/sdk/redcap_dapp_sdk.h",
        "openair2/E3AP/sdk/redcap_dapp_sdk.c",
        "openair2/E3AP/sdk/redcap_dapp_sdk.py",
    ]:
        require_path(path, errors)

    require_text("openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.h", "redcap_xapp_priority_hint_t", errors)
    require_text("openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.c", "redcap_xapp_select_top_priority_hint", errors)
    require_text("openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.py", "RedCapPriorityHint", errors)
    require_text("openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.py", "select_top_priority_hint", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.h", "redcap_dapp_prb_allocation_request_t", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.h", "redcap_dapp_access_pressure_request_t", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.h", "redcap_dapp_access_pressure_policy", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.h", "REDCAP_DAPP_TEST_BWP_MHZ = 5", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.h", "REDCAP_DAPP_TEST_BWP_PRBS_30KHZ = 12", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.c", "redcap_dapp_guard_prb_allocation", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.c", "redcap_dapp_access_pressure_policy", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.c", "RedCap dApp access pressure policy", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.c", "unsupported_5mhz_bwp_profile", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.py", "RedCapDappPrbAllocationRequest", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.py", "RedCapDappAccessPressureRequest", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.py", "redcap_dapp_access_pressure_policy", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.py", "RedCap dApp access pressure policy", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.py", "RedCap dApp PRB decision", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.py", "REDCAP_DAPP_TEST_BWP_MHZ = 5", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.py", "REDCAP_DAPP_TEST_BWP_PRBS_30KHZ = 12", errors)


def check_swig_evidence(errors: list[str]) -> list[str]:
    for path in [
        "dev_refer/dapp_dev_need/libe3/swig/libe3.i",
        "dev_refer/dapp_dev_need/libe3/cmake/libe3SWIG.cmake",
        "dev_refer/dapp_dev_need/dApp-library/libiqsaver/swig/iqsaver.i",
        "dev_refer/dapp_dev_need/dApp-library/libiqsaver/CMakeLists.txt",
    ]:
        require_path(path, errors)

    require_text("dev_refer/dapp_dev_need/libe3/cmake/libe3SWIG.cmake", "LIBE3_ENABLE_SWIG", errors)
    require_text("dev_refer/dapp_dev_need/dApp-library/libiqsaver/CMakeLists.txt", "LIBIQSAVER_ENABLE_SWIG", errors)

    generated = [
        "dev_refer/dapp_dev_need/libe3/build/swig/libe3py.py",
        "dev_refer/dapp_dev_need/libe3/build/swig/_libe3py.so",
        "dev_refer/dapp_dev_need/dApp-library/build/libiqsaver/swig/iqsaver_native.py",
    ]
    return [path for path in generated if (ROOT / path).exists()]


def check_docs(errors: list[str]) -> None:
    for path in [
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/project_plan.md",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/agent_rules.md",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/validation/gates.md",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/followups/workflow_v3_followups.md",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/report/gate_e_first32_2026-07-07.md",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/third_party/tl_expected_gate_c_stub/CMakeLists.txt",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/third_party/tl_expected_gate_c_stub/include/tl/expected.hpp",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/README.en.md",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/README.zh-TW.md",
        "agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md",
        "ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml",
        "ci-scripts/conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml",
        "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c",
        "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_uci.c",
        "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c",
        "openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c",
        "ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml",
        "ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh",
        "redcap_interface/generate_mmtc_cn_db_overlay.sh",
        "redcap_interface/bash_library/fc_generate_mmtc_cn_db_overlay.sh",
        "dev_refer/dapp_dev_need/E3Controller/README.md",
        "dev_refer/dapp_dev_need/E3Controller/src/e3sm/iq_pipeline.h",
        "dev_refer/dapp_dev_need/E3Controller/src/e3sm/slot_iq_pipeline.h",
    ]:
        require_path(path, errors)

    for doc in ["Doc/README.en.md", "Doc/README.zh-TW.md"]:
        text = (PROJECT / doc).read_text(encoding="utf-8")
        for needle in ["API / config behavior", "Command usage", "Step-by-step recap", "Expected markers", "Limitations"]:
            require(needle in text, f"{doc} missing section: {needle}", errors)
        require("runtime PASS" in text and ("do not claim" in text or "不代表" in text),
                f"{doc} must explicitly avoid runtime PASS overclaim", errors)
        require("Access-pressure policy" in text or "access-pressure policy" in text,
                f"{doc} missing access-pressure policy section", errors)
        require("redcap_dapp_access_pressure_policy" in text,
                f"{doc} missing access-pressure policy API name", errors)
        require("64 UE" in text and "32 UE" in text and "20 MHz" in text,
                f"{doc} missing 64 UE staged test wording", errors)
        require("5 MHz BWP" in text and "--require-bwp-mhz 5" in text,
                f"{doc} missing 5 MHz BWP Gate D command wording", errors)
        require("gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml" in text,
                f"{doc} missing 5 MHz BWP profile path", errors)

    gates = (PROJECT / "validation/gates.md").read_text(encoding="utf-8")
    for gate in ["Gate A", "Gate B", "Gate C", "Gate D", "Gate E"]:
        require(gate in gates, f"validation/gates.md missing {gate}", errors)
    require("gate_c_e3_loopback_check.py" in gates,
            "validation/gates.md missing Gate C runner command", errors)
    require("tl_expected" in gates and "Runtime Evidence" in gates and "183 us" in gates,
            "validation/gates.md missing Gate C runtime/latency evidence", errors)

    workflow_v3_plan = read("agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md")
    require("redcap_dapp_xapp_sdk_test_validation_v1/followups/workflow_v3_followups.md" in workflow_v3_plan,
            "Workflow v3 project plan missing dApp/xApp follow-up ledger", errors)

    gate_e_report = read("agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/report/gate_e_first32_2026-07-07.md")
    require("## English" in gate_e_report and "## Traditional Chinese" in gate_e_report,
            "Gate E first32 report must include English and Traditional Chinese sections", errors)
    require("attach=32" in gate_e_report and "pdu=32" in gate_e_report and "tun=32" in gate_e_report,
            "Gate E first32 report missing attach/PDU/TUN summary", errors)
    require("ORAN-E2SM-RC" in gate_e_report and "RIC Control request/ACK" in gate_e_report,
            "Gate E first32 report missing xApp/RIC boundary evidence", errors)

    for doc in ["Doc/README.en.md", "Doc/README.zh-TW.md"]:
        text = (PROJECT / doc).read_text(encoding="utf-8")
        require("--try-configure" in text and "--use-local-expected-stub" in text and "183 us" in text,
                f"{doc} missing Gate C configure evidence command/blocker", errors)
        require("gate_d_rfsim_marker_check.py" in text and "OAI_REDCAP_DAPP_GATE_D_MARKER" in text,
                f"{doc} missing Gate D marker checker/env usage", errors)
        require("gate_e_64ue_stage_check.py" in text and "generate_mmtc_overlay.sh 64" in text,
                f"{doc} missing Gate E 64 UE preflight command", errors)
        require("--summary-log" in text and "mmtc_stage_scan" in text,
                f"{doc} missing Gate E runtime summary-log command/evidence", errors)
        require("generate_mmtc_cn_db_overlay.sh 64" in text and "oai_db_mmtc_64.sql" in text,
                f"{doc} missing Gate E CN DB overlay command/evidence", errors)
        require("/home/tonywang/OAI/oai-cn5g/docker-compose.yaml" in text and "oai-amf" in text,
                f"{doc} missing Gate E oai-cn5g AMF source evidence", errors)
        require("runtime PASS is still pending" in text or "runtime PASS 仍然 pending" in text,
                f"{doc} must keep Gate E runtime pending", errors)
        require("[RedCap RA][gNB DL TDA]" in text and "RRCSetupComplete" in text,
                f"{doc} missing Gate E DL TDA / RRCSetupComplete blocker evidence", errors)
        require("[RedCap RA][gNB DCI BWP]" in text and "Docker image rebuild" in text,
                f"{doc} missing Gate E DCI BWP source-build/runtime boundary evidence", errors)

    five_mhz_profile = read("ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml")
    for needle in [
        "dl_carrierBandwidth: 106",
        "ul_carrierBandwidth: 106",
        "first_active_bwp: 1",
        "bwpSize: 12",
        "initialDLBWPSize_r17: 12",
        "initialULBWPSize_r17: 12",
        "coreset0_redcap_mode_r17: 1",
    ]:
        require(needle in five_mhz_profile, f"5 MHz BWP profile missing text: {needle}", errors)

    twenty_mhz_profile = read("ci-scripts/conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml")
    for needle in [
        "dl_carrierBandwidth: 51",
        "ul_carrierBandwidth: 51",
        "initialDLBWPSize_r17: 51",
        "initialULBWPSize_r17: 51",
    ]:
        require(needle in twenty_mhz_profile, f"20 MHz proxy profile missing text: {needle}", errors)

    for path in [
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/project_plan.md",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/agent_rules.md",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/validation/gates.md",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/followups/workflow_v3_followups.md",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/README.en.md",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/README.zh-TW.md",
        "agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md",
        "openspec/changes/redcap-dapp-xapp-sdk-test-validation/proposal.md",
        "openspec/changes/redcap-dapp-xapp-sdk-test-validation/design.md",
        "openspec/changes/redcap-dapp-xapp-sdk-test-validation/specs/redcap-dapp-xapp-sdk-test-validation/spec.md",
        "openspec/changes/redcap-dapp-xapp-sdk-test-validation/tasks.md",
    ]:
        reject_text(path, "5 PRB BWP", errors)
        reject_text(path, "bwp_prbs 5", errors)
        reject_text(path, "--require-bwp-prbs 5", errors)
        reject_text(path, "56 UE", errors)

    gnb_ulsch = read("openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c")
    require("redcap_dapp_guard_prb_allocation" in gnb_ulsch and "gNB-side apply marker" in gnb_ulsch,
            "gNB ULSCH missing Gate D dApp PRB guard marker", errors)
    require("nr_redcap_dapp_note_gate_d_ul_prb_decision(UE, frame, slot" in gnb_ulsch,
            "gNB ULSCH missing Gate D marker call", errors)
    gnb_uci = read("openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_uci.c")
    require("redcap_dapp_guard_prb_allocation" in gnb_uci and "gNB-side PUCCH marker" in gnb_uci,
            "gNB UCI missing Gate D dApp PUCCH guard marker", errors)
    require("nr_redcap_dapp_note_gate_d_pucch_decision(frame, slot, pucch, pucch_pdu, UE)" in gnb_uci,
            "gNB UCI missing Gate D PUCCH marker call", errors)
    nr_radio_config = read("openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c")
    require("get_pucch_reservation_uid" in nr_radio_config and "[RedCap dApp Gate E][PUCCH pressure]" in nr_radio_config,
            "nr_radio_config.c missing Gate E PUCCH pressure guard marker", errors)
    require('get_pucch_reservation_uid(scc, curr_bwp, uid, "active")' in nr_radio_config,
            "nr_radio_config.c missing active BWP PUCCH pressure guard", errors)
    require("rebuild_redcap_dl_tda_list" in nr_radio_config and "[RedCap RA][gNB DL TDA]" in nr_radio_config,
            "nr_radio_config.c missing Gate E RedCap DL TDA rebuild marker", errors)
    gnb_primitives = read("openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c")
    require("apply_redcap_initial_bwp_if_needed" in gnb_primitives and "[RedCap RA][gNB DCI BWP]" in gnb_primitives,
            "gNB scheduler primitives missing Gate E RedCap connected DCI BWP preservation marker", errors)
    gate_e_checker = read("agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_e_64ue_stage_check.py")
    require("--summary-log" in gate_e_checker and "check_stage_summary" in gate_e_checker,
            "gate_e_64ue_stage_check.py missing stage summary metric validation", errors)
    require('errors.append("Gate E runtime validation requires --summary-log with attach/PDU/TUN metrics")' in gate_e_checker,
            "gate_e_64ue_stage_check.py must reject runtime validation without a summary log", errors)
    require("redcap_dapp_sdk.c" in read("CMakeLists.txt"),
            "CMakeLists.txt missing redcap_dapp_sdk.c in build source list", errors)
    require("OAI_REDCAP_DAPP_GATE_D_MARKER" in read("ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml"),
            "docker-compose.mmtc.yml missing Gate D marker env passthrough", errors)
    mmtc_overlay = read("ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml")
    require("oai-nr-ue64:" in mmtc_overlay and 'MMTC_UE_INDEX: "64"' in mmtc_overlay,
            "docker-compose.mmtc.yml missing generated UE64 service/index", errors)
    require("nrue64.uicc.yaml:/opt/oai-nr-ue/etc/nr-ue.yaml:ro" in mmtc_overlay,
            "docker-compose.mmtc.yml missing UE64 RedCap config mount", errors)
    require("OAI_REDCAP_DAPP_GATE_D_MARKER" in read("ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh"),
            "generate_mmtc_overlay.sh missing Gate D marker env passthrough", errors)
    overlay_generator = read("ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh")
    require("TOTAL_UES" in overlay_generator and "nrue${idx}.uicc.yaml" in overlay_generator,
            "generate_mmtc_overlay.sh missing scalable UE generation logic", errors)
    cn_db_generator = read("redcap_interface/bash_library/fc_generate_mmtc_cn_db_overlay.sh")
    require("AuthenticationSubscription" in cn_db_generator and "SessionManagementSubscriptionData" in cn_db_generator,
            "mMTC CN DB generator missing subscription rows", errors)
    smoke_runner = read("redcap_interface/bash_library/fc_mmtc_smoke_validation.sh")
    require("CN_COMPOSE=${MMTC_CN_COMPOSE:-/home/tonywang/OAI/oai-cn5g/docker-compose.yaml}" in smoke_runner,
            "mMTC smoke runner missing oai-cn5g CN compose default", errors)
    require("5g_rfsimulator_flexric_redcap/docker-compose.yml" in smoke_runner
            and "5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml" in smoke_runner,
            "mMTC smoke runner missing RFsim FlexRIC RedCap compose paths", errors)
    cn_compose = Path("/home/tonywang/OAI/oai-cn5g/docker-compose.yaml")
    require(cn_compose.exists(), "missing CN compose: /home/tonywang/OAI/oai-cn5g/docker-compose.yaml", errors)
    if cn_compose.exists():
        cn_compose_text = cn_compose.read_text(encoding="utf-8")
        require("oai-amf:" in cn_compose_text and 'container_name: "oai-amf"' in cn_compose_text,
                "oai-cn5g compose missing oai-amf service", errors)
        require("mysql:" in cn_compose_text and "oai-upf:" in cn_compose_text,
                "oai-cn5g compose missing mysql/oai-upf services", errors)
    require("--num-prbs" in read("dev_refer/dapp_dev_need/E3Controller/README.md"),
            "E3Controller README missing --num-prbs reference for dApp PRB gate", errors)
    require("DecompressedSample" in read("dev_refer/dapp_dev_need/E3Controller/src/e3sm/iq_pipeline.h"),
            "E3Controller iq_pipeline.h missing I/Q sample reference", errors)
    require("SlotSample" in read("dev_refer/dapp_dev_need/E3Controller/src/e3sm/slot_iq_pipeline.h"),
            "E3Controller slot_iq_pipeline.h missing slot I/Q sample reference", errors)


def main() -> int:
    errors: list[str] = []
    check_reference_paths(errors)
    check_sdk_symbols(errors)
    generated_swig = check_swig_evidence(errors)
    check_docs(errors)

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1

    swig_status = "generated" if generated_swig else "definition-only"
    print(f"[INFO] SWIG generated module status: {swig_status}")
    if generated_swig:
        for path in generated_swig:
            print(f"[INFO] SWIG generated module: {path}")
    print("[PASS] dApp/xApp SDK test validation static checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
