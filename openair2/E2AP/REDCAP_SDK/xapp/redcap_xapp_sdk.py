#!/usr/bin/env python3
"""RedCap xApp data helpers; this module is not a live FlexRIC SWIG transport."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from typing import Any, Mapping, Sequence


NR_REDCAP_RC_CTRL_ACT_ID_UL_PRB_CAP = 100
NR_REDCAP_RC_RAN_PARAM_ID_UE_RNTI = 101
NR_REDCAP_RC_RAN_PARAM_ID_MAX_UL_PRB = 102
NR_REDCAP_RC_CTRL_STYLE_ID_RADIO_RESOURCE_ALLOCATION = 2
NR_REDCAP_RC_CTRL_ACT_ID_DRX_CONFIGURATION = 1
NR_REDCAP_RC_RAN_PARAM_ID_LONG_DRX_CYCLE = 1
APPROVED_LONG_DRX_CYCLES_MS = frozenset({320, 640, 1280, 2560, 5120, 10240})
SM_RC_ID = 3


@dataclass(frozen=True)
class RedCapUlPrbCtrlRequest:
    ue_id: int
    rnti: int
    max_ul_prb: int
    action_id: int = NR_REDCAP_RC_CTRL_ACT_ID_UL_PRB_CAP

    def as_e2sm_rc_dict(self) -> dict[str, Any]:
        return {
            "hdr": {
                "format": "FORMAT_1_E2SM_RC_CTRL_HDR",
                "ue_id": self.ue_id,
                "ric_style_type": 1,
                "ctrl_act_id": self.action_id,
            },
            "msg": {
                "format": "FORMAT_1_E2SM_RC_CTRL_MSG",
                "ran_param": [
                    {"ran_param_id": NR_REDCAP_RC_RAN_PARAM_ID_UE_RNTI, "int_ran": self.rnti},
                    {"ran_param_id": NR_REDCAP_RC_RAN_PARAM_ID_MAX_UL_PRB, "int_ran": self.max_ul_prb},
                ],
            },
        }


@dataclass(frozen=True)
class RedCapDrxCtrlRequest:
    ue_id: int
    long_cycle_ms: int
    ric_request_id: int
    policy_version: int

    def as_e2sm_rc_dict(self) -> dict[str, Any]:
        """Return only fields encoded by the standard RC request."""
        return {
            "hdr": {
                "format": "FORMAT_1_E2SM_RC_CTRL_HDR",
                "ue_id": self.ue_id,
                "ric_style_type": NR_REDCAP_RC_CTRL_STYLE_ID_RADIO_RESOURCE_ALLOCATION,
                "ctrl_act_id": NR_REDCAP_RC_CTRL_ACT_ID_DRX_CONFIGURATION,
            },
            "msg": {
                "format": "FORMAT_1_E2SM_RC_CTRL_MSG",
                "ran_param": [
                    {
                        "ran_param_id": NR_REDCAP_RC_RAN_PARAM_ID_LONG_DRX_CYCLE,
                        "int_ran": self.long_cycle_ms,
                    }
                ],
            },
        }

    def local_correlation(self) -> dict[str, int]:
        return {"ric_request_id": self.ric_request_id, "policy_version": self.policy_version}


@dataclass(frozen=True)
class RedCapUeMetric:
    rnti: int
    ul_buffer_bytes: int
    qos_weight: int
    redcap_weight: int


@dataclass(frozen=True)
class RedCapPriorityHint:
    rnti: int
    priority_weight: int
    validity_ms: int
    marker: str = "RedCap xApp priority hint"


def parse_u64(raw: str | None, min_value: int, max_value: int) -> int:
    if raw is None or raw == "":
        raise ValueError("missing integer value")
    value = int(raw, 0)
    if value < min_value or value > max_value:
        raise ValueError(f"value {value} outside [{min_value}, {max_value}]")
    return value


def read_required_env_u64(name: str, min_value: int, max_value: int) -> int:
    return parse_u64(os.environ.get(name), min_value, max_value)


def env_enabled(name: str) -> bool:
    return os.environ.get(name) in {"1", "true", "TRUE", "yes"}


def make_ul_prb_ctrl_request(ue_id: int, rnti: int, max_ul_prb: int) -> RedCapUlPrbCtrlRequest:
    if ue_id < 0:
        raise ValueError("ue_id must be non-negative")
    if rnti < 1 or rnti > 0xFFFF:
        raise ValueError("rnti must be in [1, 65535]")
    if max_ul_prb < 0 or max_ul_prb > 0xFFFF:
        raise ValueError("max_ul_prb must be in [0, 65535]")
    return RedCapUlPrbCtrlRequest(ue_id=ue_id, rnti=rnti, max_ul_prb=max_ul_prb)


def make_drx_ctrl_request(
    ue_id: int,
    long_cycle_ms: int,
    ric_request_id: int,
    policy_version: int,
) -> RedCapDrxCtrlRequest:
    if ue_id <= 0:
        raise ValueError("ue_id must be positive")
    if long_cycle_ms not in APPROVED_LONG_DRX_CYCLES_MS:
        raise ValueError("unsupported_long_cycle")
    if ric_request_id < 0 or policy_version <= 0:
        raise ValueError("ric_request_id must be non-negative and policy_version must be positive")
    return RedCapDrxCtrlRequest(ue_id, long_cycle_ms, ric_request_id, policy_version)


def find_rc_ran_func_idx(ran_functions: Sequence[Mapping[str, Any]]) -> int:
    for idx, ran_func in enumerate(ran_functions):
        if ran_func.get("id") == SM_RC_ID or ran_func.get("defn_type") == "RC_RAN_FUNC_DEF_E":
            return idx
    return -1


def make_priority_hint(metric: RedCapUeMetric, validity_ms: int) -> RedCapPriorityHint:
    if metric.rnti < 1 or metric.rnti > 0xFFFF:
        raise ValueError("rnti must be in [1, 65535]")
    if metric.ul_buffer_bytes < 0:
        raise ValueError("ul_buffer_bytes must be non-negative")
    if metric.qos_weight < 0 or metric.redcap_weight < 0:
        raise ValueError("weights must be non-negative")
    if validity_ms <= 0 or validity_ms > 0xFFFF:
        raise ValueError("validity_ms must be in [1, 65535]")
    priority = min(0xFFFF, metric.ul_buffer_bytes // 1024 + metric.qos_weight + metric.redcap_weight)
    return RedCapPriorityHint(rnti=metric.rnti, priority_weight=priority, validity_ms=validity_ms)


def select_top_priority_hint(metrics: Sequence[RedCapUeMetric], validity_ms: int) -> RedCapPriorityHint:
    hints = [make_priority_hint(metric, validity_ms) for metric in metrics]
    if not hints:
        raise ValueError("at least one metric is required")
    return max(hints, key=lambda hint: (hint.priority_weight, -hint.rnti))


def _self_check() -> None:
    req = make_ul_prb_ctrl_request(ue_id=0xE349, rnti=0xE349, max_ul_prb=32)
    encoded = req.as_e2sm_rc_dict()
    assert asdict(req)["action_id"] == NR_REDCAP_RC_CTRL_ACT_ID_UL_PRB_CAP
    assert encoded["hdr"]["ctrl_act_id"] == NR_REDCAP_RC_CTRL_ACT_ID_UL_PRB_CAP
    assert encoded["msg"]["ran_param"][0]["int_ran"] == 0xE349
    assert find_rc_ran_func_idx([{"id": 1}, {"id": SM_RC_ID}]) == 1
    assert find_rc_ran_func_idx([{"defn_type": "RC_RAN_FUNC_DEF_E"}]) == 0
    drx_req = make_drx_ctrl_request(ue_id=0xE349, long_cycle_ms=1280, ric_request_id=7, policy_version=3)
    drx_encoded = drx_req.as_e2sm_rc_dict()
    assert drx_encoded["hdr"]["ric_style_type"] == NR_REDCAP_RC_CTRL_STYLE_ID_RADIO_RESOURCE_ALLOCATION
    assert drx_encoded["msg"]["ran_param"] == [
        {"ran_param_id": NR_REDCAP_RC_RAN_PARAM_ID_LONG_DRX_CYCLE, "int_ran": 1280}
    ]
    assert "on_duration_ms" not in str(drx_encoded)
    assert drx_req.local_correlation() == {"ric_request_id": 7, "policy_version": 3}
    top = select_top_priority_hint(
        [
            RedCapUeMetric(rnti=0x1002, ul_buffer_bytes=1024, qos_weight=1, redcap_weight=1),
            RedCapUeMetric(rnti=0x1001, ul_buffer_bytes=4096, qos_weight=2, redcap_weight=1),
        ],
        validity_ms=10,
    )
    assert top.rnti == 0x1001
    assert top.priority_weight == 7
    assert top.marker == "RedCap xApp priority hint"


if __name__ == "__main__":
    _self_check()
    print("[PASS] redcap_xapp_sdk.py")
