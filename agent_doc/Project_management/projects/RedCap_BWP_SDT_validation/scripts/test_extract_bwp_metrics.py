#!/usr/bin/env python3
"""Smoke-test BWP metric extraction without requiring a Docker RFsim run."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from extract_bwp_metrics import extract_metrics


def by_metric(rows: list[dict[str, str]]) -> dict[str, str]:
    return {row["metric"]: row["local_value"] for row in rows}


def main() -> int:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        gnb_log = root / "gnb.log"
        ric_log = root / "ric.log"
        xapp_log = root / "xapp.log"
        ue_log = root / "ue.log"

        gnb_log.write_text(
            "\n".join(
                [
                    "UE RNTI 1234 CU-UE-ID 1 in-sync",
                    "UE 1234: dlsch_rounds 10/1/0/0, dlsch_errors 0",
                    "UE 1234: ulsch_rounds 8/0/0/0, ulsch_errors 0",
                    "UE 1234: MAC: TX 100 RX 200 bytes",
                    "E2 SETUP RESPONSE rx",
                    "1.000000 [GNB_APP] I RedCap initial DL BWP configured: start=0 size=51 scs=1 coreset0=10 searchSpace0=0 mode=case-a-full-cell",
                    "1.000100 [GNB_APP] I BWP 1, start PRB 0 size 106 locationandbandwidth 28875, scs 1",
                    "2.000000 [NR_MAC] I Switching to DL-BWP 1",
                    "5.000000 [NR_MAC] I [RedCap BWP][gNB reconfiguration] RNTI 1234 old_bwp_id 1 new_bwp_id 0 local_bwp_id 1",
                    "5.001000 [NR_MAC] I [RedCap BWP][gNB interrupt] RNTI 1234 slots 6 slots_per_frame 20 inactive_frames 0 frame 10",
                    "5.002000 [NR_MAC] I Switching to DL-BWP 0",
                    "5.004000 [NR_MAC] I [RRC_INACTIVE Gate 2][gNB MAC UL] received SRB1 SDU RNTI 1234 frame.slot 10.1 bytes 8",
                    "6.000000 [NR_MAC] I final timestamp",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        ric_log.write_text("E2 SETUP\n", encoding="utf-8")
        xapp_log.write_text("E42 SETUP-RESPONSE rx\n", encoding="utf-8")
        ue_log.write_text(
            "[RedCap BWP][UE RA] active BWP operation old_dl_bwp_id 0 old_ul_bwp_id 0 "
            "new_dl_bwp_id 1 new_ul_bwp_id 1 rach_configured 0 "
            "bwp_inactivity_timer=not_implemented\n",
            encoding="utf-8",
        )

        metrics = by_metric(extract_metrics(gnb_log, ric_log, xapp_log, ue_log, "synthetic_bwp"))

    expected = {
        "active_ue_count": "1",
        "ric_e2_setup_seen": "1",
        "xapp_e42_setup_seen": "1",
        "bwp_gnb_reconfiguration_count": "1",
        "bwp_gnb_reconfiguration_last_new_bwp_id": "0",
        "bwp_gnb_interrupt_count": "1",
        "bwp_gnb_interrupt_last_slots": "6",
        "bwp_ue_ra_operation_count": "1",
        "bwp_ue_ra_bwp_change_count": "1",
        "bwp_inactivity_timer_gap_seen": "1",
        "default_bwp_size_prb": "51",
        "dedicated_bwp_size_prb": "106",
        "default_bwp_residency_ms": "998.000000",
        "dedicated_bwp_residency_ms": "3002.000000",
        "bwp_switch_apply_delay_ms": "2.000000",
        "pdu_scheduling_delay_ms": "4.000000",
    }
    for metric, value in expected.items():
        assert metrics.get(metric) == value, f"{metric}: expected {value}, got {metrics.get(metric)}"

    print("BWP extractor smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
