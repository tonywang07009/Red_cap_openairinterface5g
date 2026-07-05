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
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.c", "redcap_dapp_guard_prb_allocation", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.py", "RedCapDappPrbAllocationRequest", errors)
    require_text("openair2/E3AP/sdk/redcap_dapp_sdk.py", "RedCap dApp PRB decision", errors)


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
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/README.en.md",
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/README.zh-TW.md",
        "agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md",
    ]:
        require_path(path, errors)

    for doc in ["Doc/README.en.md", "Doc/README.zh-TW.md"]:
        text = (PROJECT / doc).read_text(encoding="utf-8")
        for needle in ["API / config behavior", "Command usage", "Step-by-step recap", "Expected markers", "Limitations"]:
            require(needle in text, f"{doc} missing section: {needle}", errors)
        require("runtime PASS" in text and ("do not claim" in text or "不代表" in text),
                f"{doc} must explicitly avoid runtime PASS overclaim", errors)

    gates = (PROJECT / "validation/gates.md").read_text(encoding="utf-8")
    for gate in ["Gate A", "Gate B", "Gate C", "Gate D", "Gate E"]:
        require(gate in gates, f"validation/gates.md missing {gate}", errors)
    require("gate_c_e3_loopback_check.py" in gates,
            "validation/gates.md missing Gate C runner command", errors)
    require("tl_expected" in gates and "Configure Evidence" in gates and "workspace credits" in gates,
            "validation/gates.md missing Gate C configure blocker evidence", errors)

    workflow_v3_plan = read("agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md")
    require("redcap_dapp_xapp_sdk_test_validation_v1/followups/workflow_v3_followups.md" in workflow_v3_plan,
            "Workflow v3 project plan missing dApp/xApp follow-up ledger", errors)

    for doc in ["Doc/README.en.md", "Doc/README.zh-TW.md"]:
        text = (PROJECT / doc).read_text(encoding="utf-8")
        require("--try-configure" in text and "--allow-fetch" in text and "tl::expected" in text,
                f"{doc} missing Gate C configure evidence command/blocker", errors)


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
