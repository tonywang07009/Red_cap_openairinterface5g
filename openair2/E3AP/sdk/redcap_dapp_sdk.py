#!/usr/bin/env python3
"""Minimal Python guard helpers matching the RedCap dApp C SDK."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class RedCapDappGuardDecision(IntEnum):
    ACK = 0
    NACK = 1


@dataclass(frozen=True)
class RedCapDappUlPrbRequest:
    rnti: int
    requested_ul_prb_cap: int
    min_ul_prb_cap: int
    max_ul_prb_cap: int


@dataclass(frozen=True)
class RedCapDappGuardResult:
    decision: RedCapDappGuardDecision
    applied_ul_prb_cap: int
    reason: str


REDCAP_DAPP_TEST_BWP_MHZ = 5
REDCAP_DAPP_TEST_BWP_PRBS_30KHZ = 12
REDCAP_DAPP_TEST_BWP_PRBS_30KHZ_COMPAT = 11


@dataclass(frozen=True)
class RedCapDappPrbAllocationRequest:
    rnti: int
    bwp_prbs: int
    pucch_ratio_permille: int
    pusch_ratio_permille: int
    priority_weight: int
    has_iq_samples: bool


@dataclass(frozen=True)
class RedCapDappPrbAllocationResult:
    decision: RedCapDappGuardDecision
    pucch_prbs: int
    pusch_prbs: int
    priority_weight: int
    reason: str
    marker: str


def redcap_dapp_guard_ul_prb_cap(request: RedCapDappUlPrbRequest | None) -> RedCapDappGuardResult:
    if request is None:
        return RedCapDappGuardResult(RedCapDappGuardDecision.NACK, 0, "missing_request")
    if request.rnti == 0:
        return RedCapDappGuardResult(RedCapDappGuardDecision.NACK, 0, "invalid_rnti")
    if request.min_ul_prb_cap > request.max_ul_prb_cap:
        return RedCapDappGuardResult(RedCapDappGuardDecision.NACK, 0, "invalid_contract_range")
    if request.requested_ul_prb_cap < request.min_ul_prb_cap or request.requested_ul_prb_cap > request.max_ul_prb_cap:
        return RedCapDappGuardResult(RedCapDappGuardDecision.NACK, 0, "outside_contract_range")
    return RedCapDappGuardResult(RedCapDappGuardDecision.ACK, request.requested_ul_prb_cap, "ack")


def redcap_dapp_guard_allows_apply(result: RedCapDappGuardResult | None) -> bool:
    return result is not None and result.decision == RedCapDappGuardDecision.ACK


def _ratio_to_prbs(bwp_prbs: int, ratio_permille: int) -> int:
    return (bwp_prbs * ratio_permille + 999) // 1000


def _is_5mhz_bwp_profile(bwp_prbs: int) -> bool:
    return bwp_prbs in {REDCAP_DAPP_TEST_BWP_PRBS_30KHZ, REDCAP_DAPP_TEST_BWP_PRBS_30KHZ_COMPAT}


def redcap_dapp_guard_prb_allocation(
    request: RedCapDappPrbAllocationRequest | None,
) -> RedCapDappPrbAllocationResult:
    if request is None:
        return RedCapDappPrbAllocationResult(RedCapDappGuardDecision.NACK, 0, 0, 0, "missing_request", "")
    if request.rnti == 0:
        return RedCapDappPrbAllocationResult(RedCapDappGuardDecision.NACK, 0, 0, 0, "invalid_rnti", "")
    if not request.has_iq_samples:
        return RedCapDappPrbAllocationResult(
            RedCapDappGuardDecision.NACK, 0, 0, request.priority_weight, "missing_iq_samples", ""
        )
    if not _is_5mhz_bwp_profile(request.bwp_prbs):
        return RedCapDappPrbAllocationResult(
            RedCapDappGuardDecision.NACK, 0, 0, request.priority_weight, "unsupported_5mhz_bwp_profile", ""
        )
    if (
        request.pucch_ratio_permille > 1000
        or request.pusch_ratio_permille > 1000
        or request.pucch_ratio_permille + request.pusch_ratio_permille > 1000
    ):
        return RedCapDappPrbAllocationResult(
            RedCapDappGuardDecision.NACK, 0, 0, request.priority_weight, "invalid_prb_ratio", ""
        )
    return RedCapDappPrbAllocationResult(
        RedCapDappGuardDecision.ACK,
        _ratio_to_prbs(request.bwp_prbs, request.pucch_ratio_permille),
        _ratio_to_prbs(request.bwp_prbs, request.pusch_ratio_permille),
        request.priority_weight,
        "ack",
        "RedCap dApp PRB decision",
    )


def redcap_dapp_prb_allocation_allows_apply(result: RedCapDappPrbAllocationResult | None) -> bool:
    return result is not None and result.decision == RedCapDappGuardDecision.ACK


def _self_check() -> None:
    ok = redcap_dapp_guard_ul_prb_cap(RedCapDappUlPrbRequest(0xE349, 32, 0, 275))
    bad = redcap_dapp_guard_ul_prb_cap(RedCapDappUlPrbRequest(0xE349, 300, 0, 275))
    assert redcap_dapp_guard_allows_apply(ok)
    assert ok.applied_ul_prb_cap == 32
    assert not redcap_dapp_guard_allows_apply(bad)
    assert bad.reason == "outside_contract_range"
    allocation = redcap_dapp_guard_prb_allocation(
        RedCapDappPrbAllocationRequest(0xE349, REDCAP_DAPP_TEST_BWP_PRBS_30KHZ, 200, 600, 15, True)
    )
    missing_iq = redcap_dapp_guard_prb_allocation(
        RedCapDappPrbAllocationRequest(0xE349, REDCAP_DAPP_TEST_BWP_PRBS_30KHZ, 200, 600, 15, False)
    )
    assert redcap_dapp_prb_allocation_allows_apply(allocation)
    assert allocation.pucch_prbs == 3
    assert allocation.pusch_prbs == 8
    assert allocation.marker == "RedCap dApp PRB decision"
    assert not redcap_dapp_prb_allocation_allows_apply(missing_iq)
    assert missing_iq.reason == "missing_iq_samples"


if __name__ == "__main__":
    _self_check()
    print("[PASS] redcap_dapp_sdk.py")
