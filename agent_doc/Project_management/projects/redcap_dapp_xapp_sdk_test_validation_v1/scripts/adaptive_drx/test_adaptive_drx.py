#!/usr/bin/env python3
"""Focused standard-library checks for adaptive DRX trace and predictor logic."""

from __future__ import annotations

import csv
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from adaptive_drx import (
    ACTION_ID,
    ARRIVALS_PER_CAMPAIGN,
    FALLBACK_PROFILE,
    LONG_CYCLE_PARAMETER_ID,
    MAX_INTERVAL_US,
    MIN_INTERVAL_US,
    STYLE_ID,
    AdaptiveDrxPredictor,
    file_sha256,
    generate_intervals,
    rebase_campaign_manifest,
    write_campaign_manifest,
)
from check_campaign import CONTROL_MARKERS, TIMEOUT_MARKER, check
from run_campaign import (
    iperf_command,
    iperf_delivery_success,
    main as run_campaign,
    parse_iperf2_udp_report,
    parse_ue_drx_stats,
)


class AdaptiveDrxTest(unittest.TestCase):
    def test_iperf2_udp_receiver_report_is_parsed(self) -> None:
        output = """
[ ID] Interval       Transfer     Bandwidth        Jitter   Lost/Total Datagrams
[  3] 0.0000-0.0280 sec  32.0 KBytes  9.14 Mbits/sec  0.123 ms 1/28 (3.6%)
"""
        report = parse_iperf2_udp_report(output)
        self.assertEqual(
            report,
            {
                "burst_goodput_mbps": 9.14,
                "udp_jitter_ms": 0.123,
                "udp_lost_packets": 1,
                "udp_total_packets": 28,
                "udp_loss_percent": 3.6,
            },
        )
        self.assertTrue(iperf_delivery_success(0, report))
        self.assertFalse(iperf_delivery_success(1, report))

    def test_iperf2_udp_malformed_or_empty_receiver_report_fails_delivery(self) -> None:
        self.assertIsNone(parse_iperf2_udp_report("iperf: connection refused"))
        self.assertFalse(iperf_delivery_success(0, None))
        no_delivery = parse_iperf2_udp_report(
            "[  3] 0.0000-0.0280 sec 32.0 KBytes 9.14 Mbits/sec 0.123 ms 28/28 (100%)"
        )
        self.assertIsNotNone(no_delivery)
        self.assertFalse(iperf_delivery_success(0, no_delivery))

    def test_ue_drx_stats_marker_is_parsed_and_validated(self) -> None:
        self.assertEqual(
            parse_ue_drx_stats(
                "telnet prompt\n[RedCap DRX][UE stats] observed_slots=100 active_slots=25 active_ratio=0.25 reset=0"
            ),
            {"observed_slots": 100, "active_slots": 25},
        )
        self.assertIsNone(
            parse_ue_drx_stats("[RedCap DRX][UE stats] observed_slots=10 active_slots=11 active_ratio=1.1 reset=0")
        )

    def test_trace_is_deterministic_and_paired_between_arms(self) -> None:
        self.assertEqual(generate_intervals(41, "downlink"), generate_intervals(41, "downlink"))
        self.assertNotEqual(generate_intervals(41, "downlink"), generate_intervals(42, "downlink"))
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = write_campaign_manifest(root, 41, 1_800_000_000_000_000)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            campaigns = {entry["id"]: entry for entry in manifest["campaigns"]}
            self.assertEqual(campaigns["arm-a-dl"]["trace"], campaigns["arm-b-dl"]["trace"])
            self.assertEqual(campaigns["arm-a-ul"]["trace"], campaigns["arm-b-ul"]["trace"])
            with (manifest_path.parent / campaigns["arm-a-dl"]["trace"]["path"]).open(newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), ARRIVALS_PER_CAMPAIGN)
            self.assertEqual(rows[0]["traffic_source"], "iperf_server")
            self.assertEqual(rows[30]["phase"], "scored")
            self.assertIn("-R", iperf_command("10.0.0.2", rows[0]))
            prefixed = iperf_command("10.0.0.2", rows[0], traffic_prefix=("docker", "exec", "ue1"))
            self.assertEqual(prefixed[:4], ["docker", "exec", "ue1", "iperf"])
            self.assertEqual(campaigns["arm-a-dl"]["control_mode"], "fixed_local_rrc")
            self.assertEqual(campaigns["arm-a-dl"]["initial_profile"], FALLBACK_PROFILE.__dict__)
            self.assertNotIn("profile_schedule", campaigns["arm-a-dl"])

            source_hash = campaigns["arm-a-dl"]["trace"]["sha256"]
            rebased_path = rebase_campaign_manifest(manifest_path, root / "rebased", 1_900_000_000_000_000)
            rebased = json.loads(rebased_path.read_text(encoding="utf-8"))
            rebased_campaign = next(entry for entry in rebased["campaigns"] if entry["id"] == "arm-a-dl")
            with (rebased_path.parent / rebased_campaign["trace"]["path"]).open(newline="") as stream:
                rebased_rows = list(csv.DictReader(stream))
            self.assertEqual([row["interval_us"] for row in rows], [row["interval_us"] for row in rebased_rows])
            self.assertEqual(
                int(rebased_rows[0]["scheduled_source_tx_time_us"]) - int(rows[0]["scheduled_source_tx_time_us"]),
                100_000_000_000_000,
            )
            self.assertNotEqual(rebased_campaign["trace"]["sha256"], source_hash)
            self.assertEqual(
                rebased_campaign["trace"]["sha256"], file_sha256(rebased_path.parent / rebased_campaign["trace"]["path"])
            )
            self.assertEqual(source_hash, file_sha256(root / campaigns["arm-a-dl"]["trace"]["path"]))

    def test_scored_csv_and_policy_markers_correlate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = write_campaign_manifest(root, 41, 1_800_000_000_000_000)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            campaign = next(entry for entry in manifest["campaigns"] if entry["id"] == "arm-b-ul")
            trace_path = root / campaign["trace"]["path"]
            with trace_path.open(newline="") as stream:
                trace = list(csv.DictReader(stream))

            metrics_path = root / "metrics.csv"
            with metrics_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=(
                        "campaign_id",
                        "arrival_id",
                        "scheduled_source_tx_time_us",
                        "delivery_success",
                        "policy_version",
                        "profile_id",
                    ),
                )
                writer.writeheader()
                for row in trace[30:]:
                    writer.writerow(
                        {
                            "campaign_id": "arm-b-ul",
                            "arrival_id": row["arrival_id"],
                            "scheduled_source_tx_time_us": row["scheduled_source_tx_time_us"],
                            "delivery_success": "1",
                            "policy_version": (int(row["arrival_id"]) - 31) // 30 + 1,
                            "profile_id": "drx-320-10",
                        }
                    )

            log_path = root / "runtime.log"
            log_lines = []
            for version in range(1, 11):
                log_lines.extend(
                    f"{marker} policy_version={version}"
                    + (" cycle_ms=320 on_duration_ms=10" if marker == "[RedCap DRX][gNB applied]" else "")
                    + (" outcome success" if marker == "[RedCap DRX][RRC complete]" else "")
                    for marker in CONTROL_MARKERS
                )
            log_lines.extend(("Configured Connected DRX", "Received RRCReconfigurationComplete"))
            log_path.write_text("\n".join(log_lines), encoding="utf-8")

            issues, summary = check(manifest_path, "arm-b-ul", metrics_path, [log_path])
            self.assertEqual(issues, [])
            self.assertEqual(summary["scored_records"], 300)
            self.assertEqual(summary["delivery_success_count"], 300)
            self.assertEqual(summary["policy_versions"], 10)

            log_path.write_text(
                "\n".join(
                    line
                    for line in log_lines
                    if line != "[RedCap DRX][RRC complete] policy_version=10 outcome success"
                ),
                encoding="utf-8",
            )
            issues, _ = check(manifest_path, "arm-b-ul", metrics_path, [log_path])
            self.assertTrue(any(issue.startswith(TIMEOUT_MARKER) for issue in issues))

    def test_arm_a_checker_accepts_one_fixed_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = write_campaign_manifest(root, 41, 1_800_000_000_000_000)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            campaign = next(entry for entry in manifest["campaigns"] if entry["id"] == "arm-a-dl")
            with (root / campaign["trace"]["path"]).open(newline="") as stream:
                trace = list(csv.DictReader(stream))

            metrics_path = root / "arm-a-metrics.csv"
            with metrics_path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=(
                        "campaign_id",
                        "arrival_id",
                        "scheduled_source_tx_time_us",
                        "delivery_success",
                        "policy_version",
                        "profile_id",
                    ),
                )
                writer.writeheader()
                for row in trace[30:]:
                    writer.writerow(
                        {
                            "campaign_id": "arm-a-dl",
                            "arrival_id": row["arrival_id"],
                            "scheduled_source_tx_time_us": row["scheduled_source_tx_time_us"],
                            "delivery_success": "1",
                            "policy_version": "1",
                            "profile_id": FALLBACK_PROFILE.profile_id,
                        }
                    )

            log_path = root / "arm-a-runtime.log"
            log_path.write_text(
                "\n".join(
                    (
                        "[RedCap DRX][gNB applied] policy_version=1 cycle_ms=320 on_duration_ms=10",
                        "[RedCap DRX][RRC complete] policy_version=1 outcome success",
                        "Configured Connected DRX",
                        "Received RRCReconfigurationComplete",
                    )
                ),
                encoding="utf-8",
            )
            issues, summary = check(manifest_path, "arm-a-dl", metrics_path, [log_path])
            self.assertEqual(issues, [])
            self.assertEqual(summary["scored_records"], 300)
            self.assertEqual(summary["policy_versions"], 1)

    def test_zero_variance_standard_request_and_accept_only_reset(self) -> None:
        predictor = AdaptiveDrxPredictor()
        for _ in range(30):
            predictor.observe(640_000)
        intent = predictor.propose(
            campaign_id="arm-b-dl",
            direction="downlink",
            window_id=0,
            policy_version=1,
            ric_request_id=9001,
            rnti=0x1234,
            previous_profile_id="drx-320-10",
        )
        self.assertEqual(intent.prediction_status, "zero_variance")
        self.assertEqual(intent.statistics.stddev_interval_us, 0)
        self.assertEqual(intent.statistics.lower_3sigma_us, 640_000)
        self.assertEqual(intent.selected_profile_id, "drx-640-10")
        request = intent.e2sm_rc_request
        self.assertEqual(request["control_service_style_id"], STYLE_ID)
        self.assertEqual(request["control_action_id"], ACTION_ID)
        self.assertEqual(request["ran_parameters"][0]["id"], LONG_CYCLE_PARAMETER_ID)
        self.assertNotIn("on_duration_ms", request["ran_parameters"][0])

        predictor.resolve(False)
        self.assertEqual(len(predictor.samples), 30)
        predictor.propose(
            campaign_id="arm-b-dl",
            direction="downlink",
            window_id=0,
            policy_version=2,
            ric_request_id=9002,
            rnti=0x1234,
            previous_profile_id="drx-320-10",
        )
        predictor.resolve(True)
        self.assertEqual(predictor.samples, ())

    def test_out_of_range_prediction_falls_back_before_e2_submission(self) -> None:
        predictor = AdaptiveDrxPredictor()
        for interval_us in [7_000_000] * 15 + [9_000_000] * 15:
            predictor.observe(interval_us)
        intent = predictor.propose(
            campaign_id="arm-b-dl",
            direction="downlink",
            window_id=1,
            policy_version=1,
            ric_request_id=1,
            rnti=0x1234,
            previous_profile_id="drx-320-10",
        )
        self.assertGreaterEqual(intent.statistics.lower_3sigma_us, MIN_INTERVAL_US)
        self.assertGreater(intent.statistics.upper_3sigma_us, MAX_INTERVAL_US)
        self.assertEqual(intent.prediction_status, "fallback")
        self.assertEqual(intent.selected_profile_id, FALLBACK_PROFILE.profile_id)
        self.assertEqual(intent.e2sm_rc_request["ran_parameters"][0]["value_ms"], FALLBACK_PROFILE.long_cycle_ms)

    def test_arm_a_runner_plans_one_pre_campaign_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = write_campaign_manifest(root, 41, 1_800_000_000_000_000)
            plan_path = root / "arm-a-commands.jsonl"
            with contextlib.redirect_stdout(io.StringIO()):
                result = run_campaign(
                    [
                        "--manifest",
                        str(manifest_path),
                        "--campaign-id",
                        "arm-a-dl",
                        "--server",
                        "10.0.0.2",
                        "--command-plan",
                        str(plan_path),
                    ]
                )
            self.assertEqual(result, 2)
            records = [json.loads(line) for line in plan_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(records), ARRIVALS_PER_CAMPAIGN)
            controls = [record["control"] for record in records if "control" in record]
            self.assertEqual(
                controls,
                [
                    {
                        "phase": "pre_campaign",
                        "policy_version": 1,
                        **FALLBACK_PROFILE.__dict__,
                        "accepted": True,
                    }
                ],
            )
            self.assertTrue(all(record["policy_version"] == 1 for record in records))
            self.assertTrue(all(record["profile_id"] == FALLBACK_PROFILE.profile_id for record in records))

    def test_arm_b_runner_plans_ten_committed_windows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = write_campaign_manifest(root, 41, 1_800_000_000_000_000)
            plan_path = root / "commands.jsonl"
            with contextlib.redirect_stdout(io.StringIO()):
                result = run_campaign(
                    [
                        "--manifest",
                        str(manifest_path),
                        "--campaign-id",
                        "arm-b-dl",
                        "--server",
                        "10.0.0.2",
                        "--command-plan",
                        str(plan_path),
                        "--rrc-ue-id",
                        "17",
                    ]
                )
            self.assertEqual(result, 2)
            records = [json.loads(line) for line in plan_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(records), ARRIVALS_PER_CAMPAIGN)
            controls = [record["control"] for record in records if "control" in record]
            self.assertEqual(len(controls), 11)
            self.assertEqual(controls[0]["phase"], "pre_campaign_rollback_baseline")
            self.assertEqual(controls[0]["policy_version"], 0)
            self.assertEqual(controls[0]["profile_id"], FALLBACK_PROFILE.profile_id)
            self.assertEqual([control["policy_version"] for control in controls[1:]], list(range(1, 11)))
            self.assertTrue(all(record["policy_version"] == 0 for record in records[:30]))
            for version in range(1, 11):
                scored = [record for record in records if record["policy_version"] == version]
                self.assertEqual(len(scored), 30)


if __name__ == "__main__":
    unittest.main(verbosity=2)
