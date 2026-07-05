#!/usr/bin/env python3
"""Minimal Python helpers matching the RedCap xApp C SDK."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from typing import Any, Mapping, Sequence


NR_REDCAP_RC_CTRL_ACT_ID_UL_PRB_CAP = 100
NR_REDCAP_RC_RAN_PARAM_ID_UE_RNTI = 101
NR_REDCAP_RC_RAN_PARAM_ID_MAX_UL_PRB = 102
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


def find_rc_ran_func_idx(ran_functions: Sequence[Mapping[str, Any]]) -> int:
    for idx, ran_func in enumerate(ran_functions):
        if ran_func.get("id") == SM_RC_ID or ran_func.get("defn_type") == "RC_RAN_FUNC_DEF_E":
            return idx
    return -1


def _self_check() -> None:
    req = make_ul_prb_ctrl_request(ue_id=0xE349, rnti=0xE349, max_ul_prb=32)
    encoded = req.as_e2sm_rc_dict()
    assert asdict(req)["action_id"] == NR_REDCAP_RC_CTRL_ACT_ID_UL_PRB_CAP
    assert encoded["hdr"]["ctrl_act_id"] == NR_REDCAP_RC_CTRL_ACT_ID_UL_PRB_CAP
    assert encoded["msg"]["ran_param"][0]["int_ran"] == 0xE349
    assert find_rc_ran_func_idx([{"id": 1}, {"id": SM_RC_ID}]) == 1
    assert find_rc_ran_func_idx([{"defn_type": "RC_RAN_FUNC_DEF_E"}]) == 0


if __name__ == "__main__":
    _self_check()
    print("[PASS] redcap_xapp_sdk.py")
