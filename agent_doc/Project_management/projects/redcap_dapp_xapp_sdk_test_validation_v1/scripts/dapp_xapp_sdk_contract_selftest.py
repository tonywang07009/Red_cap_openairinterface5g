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

    proxy_allocation = dapp.redcap_dapp_guard_prb_allocation(
        dapp.RedCapDappPrbAllocationRequest(
            rnti=top.rnti,
            bwp_prbs=dapp.REDCAP_DAPP_PROXY_BWP_PRBS_30KHZ,
            pucch_ratio_permille=200,
            pusch_ratio_permille=600,
            priority_weight=top.priority_weight,
            has_iq_samples=True,
        )
    )
    assert dapp.redcap_dapp_prb_allocation_allows_apply(proxy_allocation)
    assert proxy_allocation.pucch_prbs == 11
    assert proxy_allocation.pusch_prbs == 31
    assert proxy_allocation.marker == "RedCap dApp PRB decision"

    missing_iq = dapp.redcap_dapp_guard_prb_allocation(
        dapp.RedCapDappPrbAllocationRequest(top.rnti, dapp.REDCAP_DAPP_TEST_BWP_PRBS_30KHZ, 200, 600, 7, False)
    )
    assert not dapp.redcap_dapp_prb_allocation_allows_apply(missing_iq)
    assert missing_iq.reason == "missing_iq_samples"

    bad_bwp = dapp.redcap_dapp_guard_prb_allocation(
        dapp.RedCapDappPrbAllocationRequest(top.rnti, 106, 200, 600, 7, True)
    )
    assert not dapp.redcap_dapp_prb_allocation_allows_apply(bad_bwp)
    assert bad_bwp.reason == "unsupported_bwp_profile"

    bad_ratio = dapp.redcap_dapp_guard_prb_allocation(
        dapp.RedCapDappPrbAllocationRequest(top.rnti, dapp.REDCAP_DAPP_TEST_BWP_PRBS_30KHZ, 800, 400, 7, True)
    )
    assert not dapp.redcap_dapp_prb_allocation_allows_apply(bad_ratio)
    assert bad_ratio.reason == "invalid_prb_ratio"

    low_pressure = dapp.redcap_dapp_access_pressure_policy(
        dapp.RedCapDappAccessPressureRequest(
            rnti=top.rnti,
            bwp_prbs=dapp.REDCAP_DAPP_TEST_BWP_PRBS_30KHZ,
            priority_weight=top.priority_weight,
            has_iq_samples=True,
            previous_pressure_permille=0,
            ra_retry_count=0,
            msg3_failure_count=0,
            pucch_resource_reject_count=0,
            crc_discard_count=0,
        )
    )
    assert dapp.redcap_dapp_access_pressure_allows_apply(low_pressure)
    assert low_pressure.pressure_level == "low"
    assert low_pressure.pucch_ratio_permille == 200
    assert low_pressure.pusch_ratio_permille == 600
    assert low_pressure.allocation.pucch_prbs == 3
    assert low_pressure.allocation.pusch_prbs == 8

    medium_pressure = dapp.redcap_dapp_access_pressure_policy(
        dapp.RedCapDappAccessPressureRequest(
            rnti=top.rnti,
            bwp_prbs=dapp.REDCAP_DAPP_TEST_BWP_PRBS_30KHZ,
            priority_weight=top.priority_weight,
            has_iq_samples=True,
            previous_pressure_permille=300,
            ra_retry_count=2,
            msg3_failure_count=1,
            pucch_resource_reject_count=1,
            crc_discard_count=0,
        )
    )
    assert dapp.redcap_dapp_access_pressure_allows_apply(medium_pressure)
    assert medium_pressure.pressure_level == "medium"
    assert medium_pressure.pucch_ratio_permille == 300
    assert medium_pressure.pusch_ratio_permille == 500

    high_pressure = dapp.redcap_dapp_access_pressure_policy(
        dapp.RedCapDappAccessPressureRequest(
            rnti=top.rnti,
            bwp_prbs=dapp.REDCAP_DAPP_TEST_BWP_PRBS_30KHZ,
            priority_weight=top.priority_weight,
            has_iq_samples=True,
            previous_pressure_permille=900,
            ra_retry_count=0,
            msg3_failure_count=2,
            pucch_resource_reject_count=4,
            crc_discard_count=0,
        )
    )
    assert dapp.redcap_dapp_access_pressure_allows_apply(high_pressure)
    assert high_pressure.pressure_level == "high"
    assert high_pressure.pucch_ratio_permille == 400
    assert high_pressure.pusch_ratio_permille == 400

    missing_iq_pressure = dapp.redcap_dapp_access_pressure_policy(
        dapp.RedCapDappAccessPressureRequest(
            rnti=top.rnti,
            bwp_prbs=dapp.REDCAP_DAPP_TEST_BWP_PRBS_30KHZ,
            priority_weight=top.priority_weight,
            has_iq_samples=False,
            previous_pressure_permille=900,
            ra_retry_count=0,
            msg3_failure_count=2,
            pucch_resource_reject_count=4,
            crc_discard_count=0,
        )
    )
    assert not dapp.redcap_dapp_access_pressure_allows_apply(missing_iq_pressure)
    assert missing_iq_pressure.allocation.reason == "missing_iq_samples"

    selected_pressure_ue = dapp.redcap_dapp_select_ra_pressure_priority(
        [
            dapp.RedCapDappAccessPressureRequest(
                rnti=0x2001,
                bwp_prbs=dapp.REDCAP_DAPP_PROXY_BWP_PRBS_30KHZ,
                priority_weight=40,
                has_iq_samples=True,
                previous_pressure_permille=0,
                ra_retry_count=1,
                msg3_failure_count=3,
                pucch_resource_reject_count=4,
                crc_discard_count=0,
            ),
            dapp.RedCapDappAccessPressureRequest(
                rnti=0x2002,
                bwp_prbs=dapp.REDCAP_DAPP_PROXY_BWP_PRBS_30KHZ,
                priority_weight=10,
                has_iq_samples=True,
                previous_pressure_permille=0,
                ra_retry_count=4,
                msg3_failure_count=0,
                pucch_resource_reject_count=0,
                crc_discard_count=0,
            ),
            dapp.RedCapDappAccessPressureRequest(
                rnti=0x2003,
                bwp_prbs=dapp.REDCAP_DAPP_PROXY_BWP_PRBS_30KHZ,
                priority_weight=50,
                has_iq_samples=True,
                previous_pressure_permille=0,
                ra_retry_count=4,
                msg3_failure_count=0,
                pucch_resource_reject_count=0,
                crc_discard_count=0,
            ),
        ]
    )
    assert selected_pressure_ue.found
    assert selected_pressure_ue.selected_index == 2
    assert selected_pressure_ue.selected_rnti == 0x2003
    assert selected_pressure_ue.selected_ra_retry_count == 4
    assert selected_pressure_ue.marker == "RedCap dApp RA pressure priority"
    assert dapp.redcap_dapp_access_pressure_allows_apply(selected_pressure_ue.pressure)

    print("[PASS] dApp/xApp SDK contract self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
