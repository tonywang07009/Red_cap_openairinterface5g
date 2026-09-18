"""Public behavior tests for the D2R BER measurement service."""

from pathlib import Path
import sys
import tempfile
import unittest


MAIN_CODE = Path(__file__).resolve().parents[1] / "main_code"
sys.path.insert(0, str(MAIN_CODE))

from fourmula import D2RMeasurementService, D2RReservationScheduler, generate_visibility_map
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
            completion_ns=500_000,
            reason="missing_iq",
        )

        observation = service.closed_observation(reader_id=2, window_index=1)

        self.assertFalse(observation.valid)
        self.assertEqual(observation.invalid_evidence_count, 1)
        self.assertEqual(observation.invalid_reasons, ("missing_iq",))
        self.assertIsNone(observation.ber)

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
                {"reader_id": 1, "ber": None, "valid": False, "invalid_reasons": ["missing_iq"]}
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            storage = JsonExperimentStorage(Path(directory) / "result.json")
            storage.save(record)

            self.assertEqual(storage.load(), record)


if __name__ == "__main__":
    unittest.main()
