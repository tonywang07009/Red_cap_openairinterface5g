#!/usr/bin/env python3
"""Minimal Python rApp policy package helper."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from typing import Any


REQUIRED_FIELDS = (
    "policy_version",
    "rapp_role",
    "control_contract",
    "allowed_runtime_parameters",
    "decision_policy",
)


@dataclass(frozen=True)
class RedCapRappPolicyPackage:
    policy_version: str
    control_contract: str
    allowed_runtime_parameters: tuple[str, ...]
    decision_policy: Mapping[str, Any] = field(default_factory=dict)
    rapp_role: str = "long_term_policy"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_runtime_parameters"] = list(self.allowed_runtime_parameters)
        return data


def validate_policy_package(policy: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for field_name in REQUIRED_FIELDS:
        if field_name not in policy:
            errors.append(f"missing {field_name}")
    if policy.get("rapp_role") != "long_term_policy":
        errors.append("rapp_role must be long_term_policy")
    allowed = policy.get("allowed_runtime_parameters")
    if not isinstance(allowed, Sequence) or isinstance(allowed, (str, bytes)) or len(allowed) == 0:
        errors.append("allowed_runtime_parameters must be a non-empty sequence")
    decision_policy = policy.get("decision_policy")
    if not isinstance(decision_policy, Mapping):
        errors.append("decision_policy must be a mapping")
    return errors


def build_case_b_policy() -> RedCapRappPolicyPackage:
    return RedCapRappPolicyPackage(
        policy_version="case_b_oran_control_v1",
        control_contract="ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/control/redcap_control_contract.yaml",
        allowed_runtime_parameters=(
            "redcap_ul_prb_cap",
            "drx_profile",
            "edrx_cycle_s",
            "edrx_ptw_s",
            "psm_t3324_active_time_s",
            "psm_t3512_tau_s",
        ),
        decision_policy={
            "default_policy": "power_saving_priority",
            "control_path": {
                "observation": "E2SM-KPM",
                "control": "E2SM-RC",
                "guard": "dapp_gnb_guard",
            },
        },
    )


def _self_check() -> None:
    package = build_case_b_policy().to_dict()
    assert validate_policy_package(package) == []
    assert "redcap_ul_prb_cap" in package["allowed_runtime_parameters"]
    assert validate_policy_package({"rapp_role": "runtime_writer"}) != []


if __name__ == "__main__":
    _self_check()
    print("[PASS] redcap_rapp_policy.py")
