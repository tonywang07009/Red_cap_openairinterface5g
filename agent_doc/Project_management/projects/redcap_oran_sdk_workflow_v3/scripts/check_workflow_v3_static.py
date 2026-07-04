#!/usr/bin/env python3
"""Static checks for RedCap O-RAN SDK Workflow 3.0."""

from pathlib import Path
import re
import sys


def find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AGENTS.md").is_file():
            return parent
    raise RuntimeError("Unable to find repo root from script path")


ROOT = find_repo_root()
PROJECT = ROOT / "agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3"
CHANGE = ROOT / "openspec/changes/redcap-oran-sdk-workflow-v3"
CONTROL = ROOT / "ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_required_files(errors: list[str]) -> None:
    required = [
        ROOT / "AGENTS.md",
        CHANGE / "proposal.md",
        CHANGE / "design.md",
        CHANGE / "tasks.md",
        CHANGE / "specs/redcap-oran-sdk-workflow/spec.md",
        CHANGE / "specs/redcap-workflow-reporting-ci/spec.md",
        PROJECT / "project_plan.md",
        PROJECT / "agent_rules.md",
        PROJECT / "milestones/G0_workflow_scaffold.md",
        PROJECT / "milestones/G1_sdk_contract.md",
        PROJECT / "milestones/G2_sdk_runtime_v1.md",
        PROJECT / "milestones/G3_reporting_static_ci.md",
        PROJECT / "milestones/G4_rfsim_case_b_marker_validation.md",
        PROJECT / "spec_refs/README.md",
        PROJECT / "validation/sdk_seed_inventory.md",
        PROJECT / "validation/daily_report_template.md",
        PROJECT / "validation/gate_report_template.md",
        PROJECT / "validation/static_ci_checklist.md",
        PROJECT / "report/README.md",
        PROJECT / "report/G4_rfsim_case_b_ul_prb_2026-07-04.md",
        CONTROL / "redcap_control_contract.yaml",
        CONTROL / "redcap_policy_case_a.yaml",
        CONTROL / "redcap_policy_case_b.yaml",
    ]
    for path in required:
        require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}", errors)


def check_openspec_specs(errors: list[str]) -> None:
    for path in (CHANGE / "specs").glob("*/spec.md"):
        text = read(path)
        rel = path.relative_to(ROOT)
        require("## ADDED Requirements" in text, f"{rel}: missing ADDED Requirements", errors)
        require("#### Scenario:" in text, f"{rel}: missing Scenario blocks", errors)


def check_report_templates(errors: list[str]) -> None:
    daily = read(PROJECT / "validation/daily_report_template.md")
    gate = read(PROJECT / "validation/gate_report_template.md")
    for field in ["[Today Done]", "[Evidence Path]", "[Blocked]", "[Next Pull Item]", "[Status]"]:
        require(field in daily, f"daily report template missing {field}", errors)
    for field in ["[Gate Scope]", "[3GPP / O-RAN Mapping]", "[Modification Points]", "[Validation Evidence]", "[Overclaim Guard]", "[Next Action]"]:
        require(field in gate, f"gate report template missing {field}", errors)
    require("attach/session/tunnel/ping alone cannot claim RedCap/O-RAN protocol PASS" in gate,
            "gate report template missing overclaim guard text", errors)


def parameter_blocks(contract_text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"(?m)^  - name:\s*([A-Za-z0-9_\"'-]+)\s*$", contract_text))
    blocks: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(contract_text)
        name = match.group(1).strip("\"'")
        blocks.append((name, contract_text[start:end]))
    return blocks


def check_control_contract(errors: list[str]) -> None:
    text = read(CONTROL / "redcap_control_contract.yaml")
    blocks = parameter_blocks(text)
    require(blocks, "control contract has no parameter blocks", errors)
    seen: set[str] = set()
    required_fields = ["owner:", "unit:", "default:", "runtime_mutable:", "rollback:", "validation_log_marker:"]
    for name, block in blocks:
        require(name not in seen, f"duplicate control parameter: {name}", errors)
        seen.add(name)
        for field in required_fields:
            require(field in block, f"parameter {name} missing {field}", errors)
        has_range = "allowed_values:" in block or ("min:" in block and "max:" in block)
        require(has_range, f"parameter {name} missing allowed_values or min/max", errors)
    for name in ["redcap_ul_prb_cap", "kpm_control_enable", "e2sm_rc_control_enable", "dapp_local_api_enable"]:
        require(name in seen, f"control contract missing SDK control parameter {name}", errors)


def check_case_policy_boundaries(errors: list[str]) -> None:
    case_a = read(CONTROL / "redcap_policy_case_a.yaml")
    case_b = read(CONTROL / "redcap_policy_case_b.yaml")
    require("enabled: false" in case_a, "Case A policy should keep dynamic control disabled", errors)
    require("kpm_observation: false" in case_a, "Case A policy should keep KPM observation disabled", errors)
    require("enabled: true" in case_b, "Case B policy should enable dynamic control", errors)
    require("kpm_observation: true" in case_b, "Case B policy should enable KPM observation", errors)
    require("KPM provides observation only" in case_b, "Case B policy should state KPM is observation only", errors)


def check_slm_scope(errors: list[str]) -> None:
    text = read(PROJECT / "project_plan.md") + "\n" + read(CHANGE / "proposal.md")
    require("SLM" in text and "out of scope" in text.lower(), "SLM exclusion is not explicit", errors)


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    if not errors:
        check_openspec_specs(errors)
        check_report_templates(errors)
        check_control_contract(errors)
        check_case_policy_boundaries(errors)
        check_slm_scope(errors)

    if errors:
        print("[FAIL] RedCap Workflow 3.0 static checks")
        for error in errors:
            print(f"- {error}")
        return 1

    print("[PASS] RedCap Workflow 3.0 static checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
