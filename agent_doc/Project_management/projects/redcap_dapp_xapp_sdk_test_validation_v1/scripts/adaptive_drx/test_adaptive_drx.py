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
    LONG_CYCLE_PARAMETER_ID,
    STYLE_ID,
    AdaptiveDrxPredictor,
    generate_arm_a_profiles,
    generate_intervals,
    write_campaign_manifest,
)
from check_campaign import CONTROL_MARKERS, TIMEOUT_MARKER, check
from run_campaign import iperf_command, main as run_campaign


class AdaptiveDrxTest(unittest.TestCase):
    def test_trace_is_deterministic_and_paired_between_arms(self) -> None:
        self.assertEqual(generate_intervals(41, "downlink"), generate_intervals(41, "downlink"))
        self.assertNotEqual(generate_intervals(41, "downlink"), generate_intervals(42, "downlink"))
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = write_campaign_manifest(Path(temp_dir), 41, 73, 1_800_000_000_000_000)
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
            self.assertEqual(
                campaigns["arm-a-dl"]["profile_schedule"],
                [
                    {"scored_window_id": index, **profile.__dict__}
                    for index, profile in enumerate(generate_arm_a_profiles(73, "downlink"), start=1)
                ],
            )

    def test_scored_csv_and_policy_markers_correlate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = write_campaign_manifest(root, 41, 73, 1_800_000_000_000_000)
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

    def test_arm_b_runner_plans_ten_committed_windows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = write_campaign_manifest(root, 41, 73, 1_800_000_000_000_000)
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
            self.assertEqual(len(controls), 10)
            self.assertEqual([control["policy_version"] for control in controls], list(range(1, 11)))
            for version in range(1, 11):
                scored = [record for record in records if record["policy_version"] == version]
                self.assertEqual(len(scored), 30)


if __name__ == "__main__":
    unittest.main(verbosity=2)
