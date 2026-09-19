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
    CFA_OBSERVATION_STRUCT,
    OBSERVATION_STRUCT,
    D2RMeasurementService,
    D2RReservationScheduler,
    CAMPAIGN_DURATION_MULTIPLIERS,
    aggregate_cfa_campaign_rows,
    aggregate_campaign_rows,
    PairedRicianChannelBank,
    decode_observation_datagram,
    decode_cfa_observation_datagram,
    estimate_rician_energy_ber,
    generate_visibility_map,
    sample_ticks_to_ns,
    validate_visibility_map,
    cfa_frame_components,
)
from storage import JsonExperimentStorage
from cfa_epoch import TalanetEpochController


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


class CfaCampaignTests(unittest.TestCase):
    @staticmethod
    def _rows(count=10_000):
        for attempt_index in range(count):
            failed = attempt_index >= count - 10
            yield {
                "m": 6,
                "snr_db_x10": 0,
                "attempt_index": attempt_index,
                "channel_epoch": 1,
                "epoch_ack": True,
                "channel_readback": True,
                "compared_bits": 216,
                "erroneous_bits": 1 if failed else 0,
                "crc_ok": not failed,
                "payload_match": not failed,
                "d2r_attempted": not failed,
                "r2d_on_air_duration_ns": 1_000,
            }

    def test_cfa_aggregation_is_fixed_budget_and_keeps_failed_airtime(self):
        record = aggregate_cfa_campaign_rows(list(self._rows()))

        self.assertEqual(record["campaign"]["packet_budget"], 10_000)
        point = record["points"][0]
        self.assertEqual(point["attempted_packets"], 10_000)
        self.assertEqual(point["crc_failures"], 10)
        self.assertEqual(point["compared_bits"], 2_160_000)
        self.assertEqual(point["erroneous_bits"], 10)
        self.assertEqual(point["payload_bler"], 10 / 10_000)
        self.assertEqual(point["goodput_bps"], 216 * 9_990 / 0.01)
        self.assertAlmostEqual(point["payload_bler_ci95"]["upper"], 0.00184, places=4)

    def test_cfa_aggregation_rejects_missing_attempt_and_invalid_epoch_evidence(self):
        rows = list(self._rows())
        rows.pop()
        with self.assertRaises(ValueError):
            aggregate_cfa_campaign_rows(rows)

        rows = list(self._rows())
        rows[0]["epoch_ack"] = False
        record = aggregate_cfa_campaign_rows(rows)
        point = record["points"][0]
        self.assertFalse(point["valid"])
        self.assertIsNone(point["payload_ber"])
        self.assertIsNone(point["goodput_bps"])
        self.assertIn("missing_channel_readback", point["invalid_reasons"])

        rows = list(self._rows())
        rows[0]["d2r_attempted"] = True
        rows[0]["crc_ok"] = False
        gate_record = aggregate_cfa_campaign_rows(rows)
        self.assertIn("d2r_gate_violation", gate_record["points"][0]["invalid_reasons"])

        different_grid = list(self._rows())
        different_grid.extend({**row, "m": 2, "snr_db_x10": 10} for row in self._rows())
        with self.assertRaisesRegex(ValueError, "common SNR grid"):
            aggregate_cfa_campaign_rows(different_grid)

    def test_cfa_frame_components_cover_the_four_supported_m_values(self):
        expected_symbols = {2: 238, 6: 81, 12: 42, 24: 24}
        for m, symbols in expected_symbols.items():
            frame = cfa_frame_components(m=m, prb_count=3)
            self.assertEqual(frame["frame_symbols"], symbols)
            self.assertEqual(frame["prdch_chips"], 464)
            self.assertEqual(frame["phy_bits"], 232)

        with self.assertRaises(ValueError):
            cfa_frame_components(m=3, prb_count=3)

    def test_talanet_epoch_controller_requires_drain_and_monotonic_readback(self):
        requests = []
        responses = iter(
            [
                "AIOT_T2_CHANNEL_EPOCH epoch=2 attenuation_db=10.000 noise_power=0.100000 seed=9 readback=ok queued=0",
                "AIOT_T2_CHANNEL_EPOCH epoch=1 attenuation_db=10.000 noise_power=0.100000 seed=9 readback=ok queued=0",
            ]
        )
        controller = TalanetEpochController(request=lambda command: (requests.append(command), next(responses))[1])
        with self.assertRaises(ValueError):
            controller.set_epoch(attenuation_db=10, noise_power=0.1, seed=9, drained=False)
        self.assertEqual(controller.set_epoch(attenuation_db=10, noise_power=0.1, seed=9, drained=True)["epoch"], 2)
        with self.assertRaises(RuntimeError):
            controller.set_epoch(attenuation_db=10, noise_power=0.1, seed=9, drained=True)
        self.assertEqual(requests, ["rfsimu aiot_epoch set 10 0.1 9", "rfsimu aiot_epoch set 10 0.1 9"])

        queued_controller = TalanetEpochController(
            request=lambda _command: "AIOT_T2_CHANNEL_EPOCH epoch=3 attenuation_db=10.000 noise_power=0.100000 seed=9 readback=ok queued=1"
        )
        with self.assertRaises(RuntimeError):
            queued_controller.set_epoch(attenuation_db=10, noise_power=0.1, seed=9, drained=True)

    def test_cfa_observation_v2_preserves_pdu_epoch_and_gate_fields(self):
        datagram = CFA_OBSERVATION_STRUCT.pack(
            AIOT_T2_OBSERVATION_MAGIC,
            2,
            1,
            1,
            1,
            100,
            10,
            20,
            3,
            0x1234,
            50,
            6,
            3,
            1,
            2,
            216,
            2,
            480,
            1,
            bytes(range(27)),
            bytes(reversed(range(27))),
            bytes(11),
        )
        report = decode_cfa_observation_datagram(datagram)
        self.assertEqual(report["channel_epoch"], 3)
        self.assertEqual(report["channel_provenance"], 0x1234)
        self.assertEqual(report["m"], 6)
        self.assertEqual(report["gate_status"], 2)
        self.assertEqual(report["tx_pdu"], bytes(range(27)))

        with self.assertRaises(ValueError):
            decode_cfa_observation_datagram(datagram[:-1])


if __name__ == "__main__":
    unittest.main()
