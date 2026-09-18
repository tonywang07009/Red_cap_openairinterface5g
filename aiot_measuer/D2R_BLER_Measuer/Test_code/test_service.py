"""Public behavior tests for the D2R BER measurement service."""

from pathlib import Path
import sys
import tempfile
import unittest


MAIN_CODE = Path(__file__).resolve().parents[1] / "main_code"
sys.path.insert(0, str(MAIN_CODE))

from fourmula import (
    AIOT_T2_OBSERVATION_MAGIC,
    AIOT_T2_OBSERVATION_VERSION,
    OBSERVATION_STRUCT,
    D2RMeasurementService,
    D2RReservationScheduler,
    CAMPAIGN_DURATION_MULTIPLIERS,
    aggregate_campaign_rows,
    PairedRicianChannelBank,
    decode_observation_datagram,
    estimate_rician_energy_ber,
    generate_visibility_map,
    sample_ticks_to_ns,
    validate_visibility_map,
)
from storage import JsonExperimentStorage


class CompletedPacketObservationTests(unittest.TestCase):
    def test_packet_is_counted_in_its_decode_completion_window(self):
        service = D2RMeasurementService(window_ns=500_000)

        service.record_completed_packet(
            reader_id=1,
            completion_ns=800_000,
            transmitted_bits=(0, 1, 0, 1),
            decoded_bits=(0, 1, 1, 1),
        )

        empty = service.closed_observation(reader_id=1, window_index=0)
        completed = service.closed_observation(reader_id=1, window_index=1)

        self.assertEqual(empty.compared_bits, 0)
        self.assertIsNone(empty.ber)
        self.assertEqual(completed.window_start_ns, 500_000)
        self.assertEqual(completed.window_end_ns, 1_000_000)
        self.assertEqual(completed.available_at_ns, 1_000_000)
        self.assertEqual(completed.compared_bits, 4)
        self.assertEqual(completed.erroneous_bits, 1)
        self.assertEqual(completed.ber, 0.25)

    def test_missing_comparison_evidence_invalidates_its_completion_window(self):
        service = D2RMeasurementService(window_ns=500_000)

        service.record_missing_evidence(
            reader_id=2,
            tx_ns=500_000,
            reason="missing_iq",
        )

        observation = service.closed_observation(reader_id=2, window_index=1)

        self.assertFalse(observation.valid)
        self.assertEqual(observation.invalid_evidence_count, 1)
        self.assertEqual(observation.invalid_reasons, ("missing_iq",))
        self.assertIsNone(observation.ber)
        self.assertEqual(observation.actual_tx_packets, 1)
        self.assertEqual(observation.undetected_packets, 0)
        self.assertEqual(observation.unaligned_packets, 0)
        self.assertIsNone(observation.packet_loss_rate)

    def test_packet_loss_rate_uses_undetected_and_unaligned_transmissions(self):
        service = D2RMeasurementService(window_ns=500_000)

        service.record_completed_packet(
            reader_id=1,
            completion_ns=100,
            transmitted_bits=(0, 1),
            decoded_bits=(0, 1),
        )
        service.record_acquisition_loss(
            reader_id=1,
            tx_ns=200,
            loss_kind="undetected",
        )
        service.record_acquisition_loss(
            reader_id=1,
            tx_ns=300,
            loss_kind="unaligned",
        )

        observation = service.closed_observation(reader_id=1, window_index=0)

        self.assertEqual(observation.actual_tx_packets, 3)
        self.assertEqual(observation.undetected_packets, 1)
        self.assertEqual(observation.unaligned_packets, 1)
        self.assertEqual(observation.packet_loss_rate, 2 / 3)
        self.assertTrue(observation.valid)

    def test_packet_loss_kind_is_explicit(self):
        service = D2RMeasurementService(window_ns=500_000)

        with self.assertRaises(ValueError):
            service.record_acquisition_loss(reader_id=1, tx_ns=100, loss_kind="missing")

    def test_completed_packet_rejects_empty_payload(self):
        service = D2RMeasurementService(window_ns=500_000)

        with self.assertRaises(ValueError):
            service.record_completed_packet(
                reader_id=1,
                completion_ns=100,
                transmitted_bits=(),
                decoded_bits=(),
            )

    def test_observation_to_dict_preserves_loss_fields_for_json(self):
        service = D2RMeasurementService(window_ns=500_000)
        service.record_acquisition_loss(reader_id=1, tx_ns=100, loss_kind="unaligned")

        record = service.closed_observation(reader_id=1, window_index=0).to_dict()

        self.assertEqual(record["actual_tx_packets"], 1)
        self.assertEqual(record["undetected_packets"], 0)
        self.assertEqual(record["unaligned_packets"], 1)
        self.assertEqual(record["packet_loss_rate"], 1.0)
        self.assertIsInstance(record["invalid_reasons"], list)

    def test_completion_boundaries_and_bit_weighted_aggregation(self):
        service = D2RMeasurementService(window_ns=500_000)

        service.record_completed_packet(
            reader_id=1,
            completion_ns=499_999,
            transmitted_bits=(0,) * 100,
            decoded_bits=(1, 1) + (0,) * 98,
        )
        service.record_completed_packet(
            reader_id=1,
            completion_ns=500_000,
            transmitted_bits=(0,) * 900,
            decoded_bits=(0,) * 900,
        )
        service.record_completed_packet(
            reader_id=1,
            completion_ns=500_001,
            transmitted_bits=(0,) * 100,
            decoded_bits=(0,) * 100,
        )

        first = service.closed_observation(reader_id=1, window_index=0)
        second = service.closed_observation(reader_id=1, window_index=1)

        self.assertEqual(first.completed_packets, 1)
        self.assertEqual(first.ber, 0.02)
        self.assertEqual(second.completed_packets, 2)
        self.assertEqual(second.compared_bits, 1_000)
        self.assertEqual(second.erroneous_bits, 0)
        self.assertEqual(second.ber, 0.0)

    def test_seeded_visibility_is_replayable_and_assigns_each_tag_at_most_once(self):
        first = generate_visibility_map(tag_count=100, reader_ids=(1, 2, 3), seed=73)
        replay = generate_visibility_map(tag_count=100, reader_ids=(1, 2, 3), seed=73)

        self.assertEqual(first, replay)
        self.assertEqual(set(first), set(range(1, 101)))
        self.assertTrue(all(reader_id in (None, 1, 2, 3) for reader_id in first.values()))

    def test_same_reader_overlap_is_deferred_but_other_readers_can_receive_concurrently(self):
        scheduler = D2RReservationScheduler()

        first = scheduler.reserve(reader_id=1, start_ns=100, end_ns=200)
        same_reader = scheduler.reserve(reader_id=1, start_ns=150, end_ns=250)
        other_reader = scheduler.reserve(reader_id=2, start_ns=150, end_ns=250)

        self.assertTrue(first.admitted)
        self.assertFalse(same_reader.admitted)
        self.assertEqual(same_reader.reason, "same_reader_overlap")
        self.assertTrue(other_reader.admitted)

    def test_json_storage_round_trips_null_ber_and_invalid_evidence(self):
        record = {
            "schema_version": 1,
            "observations": [
                {
                    "reader_id": 1,
                    "ber": None,
                    "actual_tx_packets": 1,
                    "undetected_packets": 0,
                    "unaligned_packets": 0,
                    "packet_loss_rate": None,
                    "valid": False,
                    "invalid_reasons": ["missing_iq"],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            storage = JsonExperimentStorage(Path(directory) / "result.json")
            storage.save(record)

            self.assertEqual(storage.load(), record)

    def test_json_storage_rejects_nan_without_leaving_a_partial_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            storage = JsonExperimentStorage(path)

            with self.assertRaises(ValueError):
                storage.save({"ber": float("nan")})

            self.assertFalse(path.exists())
            self.assertEqual(list(Path(directory).glob(".result.json.*")), [])

    def test_visibility_rejects_more_than_100_tags_and_unknown_reader(self):
        with self.assertRaises(ValueError):
            generate_visibility_map(tag_count=101, reader_ids=(1, 2, 3), seed=1)
        with self.assertRaises(ValueError):
            validate_visibility_map({1: 4}, tag_count=1, reader_ids=(1, 2, 3))

    def test_sample_tick_conversion_is_explicit_at_window_edges(self):
        self.assertEqual(sample_ticks_to_ns(499_999, 1_000_000), 499_999_000)
        self.assertEqual(sample_ticks_to_ns(500_000, 1_000_000), 500_000_000)
        self.assertEqual(sample_ticks_to_ns(500_001, 1_000_000), 500_001_000)

    def test_wire_crc_failure_is_compared_and_provenance_is_preserved(self):
        transmitted = bytes([0xA5])
        decoded = bytes([0x25])
        datagram = OBSERVATION_STRUCT.pack(
            AIOT_T2_OBSERVATION_MAGIC,
            AIOT_T2_OBSERVATION_VERSION,
            2,
            0,
            2,
            7,
            100,
            800_000,
            1,
            b"\0\0\0",
            8,
            1,
            transmitted + b"\0" * 15,
            decoded + b"\0" * 15,
            0x1234,
        )
        report = decode_observation_datagram(datagram)
        service = D2RMeasurementService(window_ns=500_000)
        service.record_wire_observation(report, sample_rate_hz=1_000_000_000)
        observation = service.closed_observation(reader_id=2, window_index=1)
        self.assertEqual(observation.compared_bits, 8)
        self.assertEqual(observation.erroneous_bits, 1)
        self.assertEqual(observation.channel_provenance, 0x1234)

    def test_paired_channel_replays_same_key_and_separates_other_keys(self):
        bank = PairedRicianChannelBank(seed=9)
        first = bank.cascaded(repeat=0, tag_id=1, cycle=4)
        self.assertEqual(first, bank.cascaded(repeat=0, tag_id=1, cycle=4))
        self.assertNotEqual(first, bank.cascaded(repeat=0, tag_id=1, cycle=5))
        result = estimate_rician_energy_ber(duration_multiplier=1 / 8, bits=100, seed=9)
        self.assertGreaterEqual(result["compared_bits"], 0)
        self.assertIn("ber", result)

    def test_campaign_requires_the_fixed_4000_variant_budget_and_sums_bits(self):
        rows = []
        for duration_index, multiplier in enumerate(CAMPAIGN_DURATION_MULTIPLIERS):
            for repeat in range(5):
                for cycle in range(100):
                    rows.append(
                        {
                            "duration_index": duration_index,
                            "duration_multiplier": multiplier,
                            "repeat": repeat,
                            "cycle": cycle,
                            "actual_tx_packets": 1,
                            "compared_bits": 100,
                            "erroneous_bits": 2,
                            "deferrals": 3,
                            "invalid": False,
                            "source": "rfsim",
                        }
                    )

        record = aggregate_campaign_rows(rows)

        self.assertEqual(record["campaign"]["variant_count"], 4_000)
        self.assertEqual(len(record["duration_results"]), 8)
        self.assertEqual(record["duration_results"][0]["compared_bits"], 50_000)
        self.assertEqual(record["duration_results"][0]["erroneous_bits"], 1_000)
        self.assertEqual(record["duration_results"][0]["ber"], 0.02)
        self.assertEqual(record["duration_results"][0]["deferrals"], 1_500)
        self.assertEqual(record["campaign"]["source"], "rfsim")

    def test_campaign_rejects_duplicate_or_missing_variant(self):
        row = {
            "duration_index": 0,
            "duration_multiplier": CAMPAIGN_DURATION_MULTIPLIERS[0],
            "repeat": 0,
            "cycle": 0,
            "actual_tx_packets": 0,
            "compared_bits": 0,
            "erroneous_bits": 0,
            "deferrals": 0,
            "invalid": False,
            "source": "rfsim",
        }
        with self.assertRaises(ValueError):
            aggregate_campaign_rows([row, dict(row)])
        with self.assertRaises(ValueError):
            aggregate_campaign_rows([row])


if __name__ == "__main__":
    unittest.main()
