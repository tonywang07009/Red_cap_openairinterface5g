#!/usr/bin/env python3
"""Focused standard-library checks for adaptive DRX runtime evidence metrics."""

from __future__ import annotations

import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from adaptive_drx import FALLBACK_PROFILE, write_campaign_manifest
from check_campaign import check, main as check_campaign


class CampaignEvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.manifest_path = write_campaign_manifest(self.root, 41, 1_800_000_000_000_000)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.campaign = next(entry for entry in manifest["campaigns"] if entry["id"] == "arm-a-dl")
        with (self.root / self.campaign["trace"]["path"]).open(newline="") as stream:
            self.trace = list(csv.DictReader(stream))

        self.metrics_path = self.root / "metrics.csv"
        with self.metrics_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(
                stream,
                fieldnames=(
                    "campaign_id",
                    "arrival_id",
                    "scheduled_source_tx_time_us",
                    "delivery_success",
                    "policy_version",
                    "profile_id",
                    "burst_goodput_mbps",
                    "udp_jitter_ms",
                    "udp_lost_packets",
                    "udp_total_packets",
                    "udp_loss_percent",
                ),
            )
            writer.writeheader()
            for row in self.trace[30:]:
                writer.writerow(
                    {
                        "campaign_id": "arm-a-dl",
                        "arrival_id": row["arrival_id"],
                        "scheduled_source_tx_time_us": row["scheduled_source_tx_time_us"],
                        "delivery_success": "1",
                        "policy_version": "1",
                        "profile_id": FALLBACK_PROFILE.profile_id,
                        "burst_goodput_mbps": "9.5",
                        "udp_jitter_ms": "0.5",
                        "udp_lost_packets": "0",
                        "udp_total_packets": "28",
                        "udp_loss_percent": "0.0",
                    }
                )

        self.receive_path = self.root / "receive.csv"
        self._write_receive()
        self.summary_path = self.root / "summary.json"
        self.summary_path.write_text(
            json.dumps(
                {
                    "campaign_id": "arm-a-dl",
                    "completed_arrivals": 330,
                    "scored_arrivals_completed": 300,
                    "scored_stats_valid": True,
                    "drx_observed_slots": 1000,
                    "drx_active_slots": 100,
                    "drx_active_time_slot_ratio": 0.1,
                    "pdcch_monitoring_slot_ratio": 0.1,
                }
            ),
            encoding="utf-8",
        )
        self.log_path = self.root / "runtime.log"
        self.log_path.write_text(
            "\n".join(
                (
                    "999.900000 UE 1234: dlsch_rounds 100/2/1/0, dlsch_errors 0",
                    "999.900100 UE 1234: ulsch_rounds 200/1/0/0, ulsch_errors 0",
                    "1000.000000 [NR_MAC] [RedCap DRX][gNB staged] RNTI 1234 policy_version 1 cycle_ms 320",
                    "1000.025000 [NR_MAC] [RedCap DRX][gNB applied] RNTI 1234 policy_version=1 cycle_ms=320 on_duration_ms=10",
                    "1000.050000 [NR_MAC] [RedCap DRX][RRC complete] RNTI 1234 policy_version 1 outcome success",
                    "1001.000000 UE 1234: dlsch_rounds 400/8/3/1, dlsch_errors 0",
                    "1001.000100 UE 1234: ulsch_rounds 500/4/2/0, ulsch_errors 0",
                    "1001.100000 [RedCap DRX][dApp REJECT] RNTI 1234 policy_version 2",
                    "1001.200000 [RedCap DRX][rollback] RNTI 1234 policy_version 2",
                    "1001.300000 [RedCap DRX][control timeout] policy_version=2",
                    "Configured Connected DRX",
                    "Received RRCReconfigurationComplete",
                )
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_receive(self, late_arrival: int | None = None) -> None:
        with self.receive_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=("campaign_id", "arrival_id", "source_receive_time_us"))
            writer.writeheader()
            for row in self.trace[30:]:
                arrival_id = int(row["arrival_id"])
                receive_us = int(row["scheduled_source_tx_time_us"]) + 1000
                if arrival_id == late_arrival:
                    receive_us = int(self.trace[arrival_id]["scheduled_source_tx_time_us"])
                writer.writerow(
                    {
                        "campaign_id": "arm-a-dl",
                        "arrival_id": arrival_id,
                        "source_receive_time_us": receive_us,
                    }
                )

    def test_complete_external_evidence_is_summarized(self) -> None:
        issues, summary = check(
            self.manifest_path,
            "arm-a-dl",
            self.metrics_path,
            [self.log_path],
            receive_path=self.receive_path,
            summary_path=self.summary_path,
            rnti=0x1234,
            require_frozen_metrics=True,
        )
        self.assertEqual(issues, [])
        self.assertEqual(summary["scheduled_to_first_receive_median_ms"], 1.0)
        self.assertEqual(summary["scheduled_to_first_receive_p95_ms"], 1.0)
        self.assertEqual(summary["scheduled_to_first_receive_max_ms"], 1.0)
        self.assertEqual(summary["policy_apply_latency_median_ms"], 50.0)
        self.assertEqual(summary["rrc_reconfiguration_count"], 1)
        self.assertEqual(summary["dl_harq_retransmission_count"], 9)
        self.assertEqual(summary["ul_harq_retransmission_count"], 5)
        self.assertEqual(summary["policy_reject_count"], 1)
        self.assertEqual(summary["rollback_count"], 1)
        self.assertEqual(summary["rrc_reconfiguration_timeout_count"], 1)
        self.assertEqual(summary["burst_goodput_mean_mbps"], 9.5)
        self.assertEqual(summary["drx_active_time_slot_ratio"], 0.1)

    def test_receive_timestamp_must_precede_next_arrival(self) -> None:
        self._write_receive(late_arrival=31)
        issues, summary = check(
            self.manifest_path,
            "arm-a-dl",
            self.metrics_path,
            [self.log_path],
            receive_path=self.receive_path,
            rnti=0x1234,
        )
        self.assertTrue(any("not before the next arrival" in issue for issue in issues))
        self.assertNotIn("scheduled_to_first_receive_median_ms", summary)

    def test_cli_reports_missing_optional_evidence_as_partial(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = check_campaign(
                [
                    "--manifest",
                    str(self.manifest_path),
                    "--campaign-id",
                    "arm-a-dl",
                    "--metrics-csv",
                    str(self.metrics_path),
                    "--log",
                    str(self.log_path),
                ]
            )
        self.assertEqual(result, 2)
        self.assertIn("[PARTIAL] missing optional evidence: --receive-csv", output.getvalue())
        self.assertIn("[PARTIAL] missing optional evidence: --summary-json", output.getvalue())
        self.assertIn("[PARTIAL] missing optional evidence: --rnti", output.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
