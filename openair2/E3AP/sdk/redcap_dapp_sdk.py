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


def _self_check() -> None:
    ok = redcap_dapp_guard_ul_prb_cap(RedCapDappUlPrbRequest(0xE349, 32, 0, 275))
    bad = redcap_dapp_guard_ul_prb_cap(RedCapDappUlPrbRequest(0xE349, 300, 0, 275))
    assert redcap_dapp_guard_allows_apply(ok)
    assert ok.applied_ul_prb_cap == 32
    assert not redcap_dapp_guard_allows_apply(bad)
    assert bad.reason == "outside_contract_range"


if __name__ == "__main__":
    _self_check()
    print("[PASS] redcap_dapp_sdk.py")
