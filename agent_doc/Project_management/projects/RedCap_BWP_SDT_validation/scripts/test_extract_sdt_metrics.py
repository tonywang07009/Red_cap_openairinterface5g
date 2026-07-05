#!/usr/bin/env python3
"""Smoke-test SDT metric extraction without requiring a Docker RFsim run."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from extract_sdt_metrics import extract_metrics


def by_metric(rows: list[dict[str, str]]) -> dict[str, str]:
    return {row["metric"]: row["local_value"] for row in rows}


def main() -> int:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        gnb_log = root / "gnb.log"
        ue_log = root / "ue.log"

        gnb_log.write_text(
            "\n".join(
                [
                    "UE RNTI 1234 CU-UE-ID 1 in-sync",
                    "[RRC_INACTIVE Gate 3][gNB RRC] configuredGrantConfig validation setup cg_sdt=1",
                    "[RRC_INACTIVE Gate 3][gNB MAC UL] cg-SDT PUSCH rx candidate RNTI 1234 frame.slot 10.1 bytes 17",
                    "UE 1234: dlsch_rounds 10/0/0/0, dlsch_errors 0",
                    "UE 1234: ulsch_rounds 8/0/0/0, ulsch_errors 0",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        ue_log.write_text("cg-SDT autonomous CG PUSCH scheduled\n", encoding="utf-8")
        metrics = by_metric(extract_metrics(gnb_log, ue_log, "4_step_sdt"))

    expected = {
        "active_ue_count": "1",
        "ue_in_sync_seen": "1",
        "rrc_inactive_marker_seen": "1",
        "configured_grant_marker_seen": "1",
        "cg_sdt_marker_seen": "1",
        "cg_sdt_rx_candidate_count": "1",
        "cg_sdt_tx_marker_count": "1",
        "packet_attempt_count": "1",
        "packet_success_count": "1",
        "threshold_fallback_count": "0",
        "timeout_failure_count": "0",
        "sdt_failure_count": "0",
        "packet_transmission_success_probability": "1.000000",
    }
    for metric, value in expected.items():
        assert metrics.get(metric) == value, f"{metric}: expected {value}, got {metrics.get(metric)}"

    print("SDT extractor smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
