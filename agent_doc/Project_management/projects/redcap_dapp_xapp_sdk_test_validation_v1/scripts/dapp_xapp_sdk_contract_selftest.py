#!/usr/bin/env python3
"""Self-test for the RedCap dApp/xApp SDK test-facing contract."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    xapp = load_module("redcap_xapp_sdk", ROOT / "openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.py")
    dapp = load_module("redcap_dapp_sdk", ROOT / "openair2/E3AP/sdk/redcap_dapp_sdk.py")

    top = xapp.select_top_priority_hint(
        [
            xapp.RedCapUeMetric(rnti=0x1002, ul_buffer_bytes=1024, qos_weight=1, redcap_weight=1),
            xapp.RedCapUeMetric(rnti=0x1001, ul_buffer_bytes=4096, qos_weight=2, redcap_weight=1),
            xapp.RedCapUeMetric(rnti=0x1003, ul_buffer_bytes=4096, qos_weight=2, redcap_weight=1),
        ],
        validity_ms=10,
    )
    assert top.rnti == 0x1001
    assert top.priority_weight == 7
    assert top.marker == "RedCap xApp priority hint"

    allocation = dapp.redcap_dapp_guard_prb_allocation(
        dapp.RedCapDappPrbAllocationRequest(
            rnti=top.rnti,
            bwp_prbs=dapp.REDCAP_DAPP_TEST_BWP_PRBS_30KHZ,
            pucch_ratio_permille=200,
            pusch_ratio_permille=600,
            priority_weight=top.priority_weight,
            has_iq_samples=True,
        )
    )
    assert dapp.redcap_dapp_prb_allocation_allows_apply(allocation)
    assert allocation.pucch_prbs == 3
    assert allocation.pusch_prbs == 8
    assert allocation.priority_weight == top.priority_weight
    assert allocation.marker == "RedCap dApp PRB decision"

    missing_iq = dapp.redcap_dapp_guard_prb_allocation(
        dapp.RedCapDappPrbAllocationRequest(top.rnti, dapp.REDCAP_DAPP_TEST_BWP_PRBS_30KHZ, 200, 600, 7, False)
    )
    assert not dapp.redcap_dapp_prb_allocation_allows_apply(missing_iq)
    assert missing_iq.reason == "missing_iq_samples"

    bad_bwp = dapp.redcap_dapp_guard_prb_allocation(
        dapp.RedCapDappPrbAllocationRequest(top.rnti, 51, 200, 600, 7, True)
    )
    assert not dapp.redcap_dapp_prb_allocation_allows_apply(bad_bwp)
    assert bad_bwp.reason == "unsupported_5mhz_bwp_profile"

    bad_ratio = dapp.redcap_dapp_guard_prb_allocation(
        dapp.RedCapDappPrbAllocationRequest(top.rnti, dapp.REDCAP_DAPP_TEST_BWP_PRBS_30KHZ, 800, 400, 7, True)
    )
    assert not dapp.redcap_dapp_prb_allocation_allows_apply(bad_ratio)
    assert bad_ratio.reason == "invalid_prb_ratio"

    print("[PASS] dApp/xApp SDK contract self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
