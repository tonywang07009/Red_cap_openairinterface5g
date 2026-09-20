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
    CBRA_OBSERVATION_STRUCT,
    OBSERVATION_STRUCT,
    D2RMeasurementService,
    D2RReservationScheduler,
    CAMPAIGN_DURATION_MULTIPLIERS,
    CbraSquareLawReceiver,
    aggregate_cbra_campaign_rows,
    aggregate_campaign_rows,
    PairedRicianChannelBank,
    decode_observation_datagram,
    decode_cbra_observation_datagram,
    estimate_rician_energy_ber,
    generate_visibility_map,
    sample_ticks_to_ns,
    validate_visibility_map,
    cbra_frame_components,
    cbra_expand_compact_chips,
    cbra_power_calibration_report,
    cbra_prdch_mean_power,
    cbra_prdch_physical_indices,
    cbra_snr_calibration,
    cbra_observation_to_campaign_row,
)
from storage import JsonExperimentStorage
from cbra_epoch import CbraAttemptEpochBinder, TalanetEpochController, deterministic_channel_provenance


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


class CbraCampaignTests(unittest.TestCase):
    @staticmethod
    def _rows(count=10_000):
        for attempt_index in range(count):
            failed = attempt_index >= count - 10
            yield {
                "message_kind": 0,
                "m": 6,
                "snr_db_x10": 0,
                "target_snr_db_x10": 0,
                "signal_power_q16": 65_536,
                "noise_power_q16": 65_536,
                "calibrated_snr_db_x10": 0,
                "attempt_index": attempt_index,
                "channel_epoch": 1,
                "epoch_ack": True,
                "channel_readback": True,
                "mac_bits": 224,
                "phy_bits": 240,
                "compared_bits": 224,
                "erroneous_bits": 1 if failed else 0,
                "crc_ok": not failed,
                "payload_match": not failed,
                "d2r_attempted": False,
                "context_eligible": True,
                "setup": False,
                "r2d_on_air_duration_ns": 1_000,
            }

    def test_cbra_aggregation_is_fixed_budget_and_keeps_failed_airtime(self):
        record = aggregate_cbra_campaign_rows(list(self._rows()))

        self.assertEqual(record["campaign"]["packet_budget"], 10_000)
        point = record["points"][0]
        self.assertEqual(point["attempted_packets"], 10_000)
        self.assertEqual(point["crc_failures"], 10)
        self.assertEqual(point["compared_bits"], 2_240_000)
        self.assertEqual(point["erroneous_bits"], 10)
        self.assertEqual(point["payload_bler"], 10 / 10_000)
        self.assertEqual(point["goodput_bps"], 224 * 9_990 / 0.01)
        self.assertAlmostEqual(point["payload_bler_ci95"]["upper"], 0.00184, places=4)

    def test_cbra_point_keeps_measured_snr_and_validates_pilot_center_tolerance(self):
        rows = list(self._rows())
        for row in rows:
            row["snr_db_x10"] = 174
            row["calibrated_snr_db_x10"] = 175
        point = aggregate_cbra_campaign_rows(rows)["points"][0]
        self.assertEqual(point["snr_db_x10"], 174)
        self.assertEqual(point["calibrated_snr_db_x10_mean"], 175)
        self.assertTrue(point["valid"])

        for row in rows:
            row["calibrated_snr_db_x10"] = 200
        point = aggregate_cbra_campaign_rows(rows)["points"][0]
        self.assertFalse(point["valid"])
        self.assertIn("calibration_outside_point_tolerance", point["invalid_reasons"])

    def test_cbra_aggregation_keeps_paging_and_trigger_denominators_separate(self):
        trigger_rows = [
            {
                **row,
                "message_kind": 1,
                "mac_bits": 3,
                "phy_bits": 9,
                "compared_bits": 3,
                "setup": False,
            }
            for row in self._rows()
        ]
        trigger_rows.append({**trigger_rows[0], "attempt_index": 10_000, "setup": True})
        record = aggregate_cbra_campaign_rows(list(self._rows()) + trigger_rows)
        self.assertEqual({point["message_kind"] for point in record["points"]}, {0, 1})
        self.assertEqual({point["attempted_packets"] for point in record["points"]}, {10_000})

    def test_cbra_aggregation_rejects_missing_attempt_and_invalid_epoch_evidence(self):
        rows = list(self._rows())
        rows.pop()
        with self.assertRaises(ValueError):
            aggregate_cbra_campaign_rows(rows)

        rows = list(self._rows())
        rows[0]["epoch_ack"] = False
        record = aggregate_cbra_campaign_rows(rows)
        point = record["points"][0]
        self.assertFalse(point["valid"])
        self.assertIsNone(point["payload_ber"])
        self.assertIsNone(point["goodput_bps"])
        self.assertIn("missing_channel_readback", point["invalid_reasons"])

        rows = list(self._rows())
        rows[0]["d2r_attempted"] = True
        rows[0]["crc_ok"] = False
        gate_record = aggregate_cbra_campaign_rows(rows)
        self.assertIn("unexpected_d2r_attempt", gate_record["points"][0]["invalid_reasons"])

        different_grid = list(self._rows())
        different_grid.extend({**row, "m": 2, "snr_db_x10": 10} for row in self._rows())
        with self.assertRaisesRegex(ValueError, "common SNR grid"):
            aggregate_cbra_campaign_rows(different_grid)

    def test_cbra_frame_components_cover_the_four_supported_m_values(self):
        expected_symbols = {2: 246, 6: 84, 12: 43, 24: 25}
        expected_padding = {2: 0, 6: 4, 12: 4, 24: 18}
        expected_reserved = {2: 0, 6: 0, 12: 0, 24: 46}
        expected_samples = {2: 269904, 6: 92160, 12: 47184, 24: 27432}
        expected_airtime_ns = {2: 17571875, 6: 6000000, 12: 3071875, 24: 1785938}
        for m, symbols in expected_symbols.items():
            frame = cbra_frame_components(m=m, prb_count=3)
            self.assertEqual(frame["frame_symbols"], symbols)
            self.assertEqual(frame["prdch_chips"], 480)
            self.assertEqual(frame["mac_bits"], 224)
            self.assertEqual(frame["phy_bits"], 240)
            self.assertEqual(frame["padding_chips"], expected_padding[m])
            self.assertEqual(frame["mapping_reserved_chips"], expected_reserved[m])
            self.assertEqual(frame["ofdm_sample_count"], expected_samples[m])
            self.assertEqual(frame["full_r2d_airtime_ns"], expected_airtime_ns[m])

        with self.assertRaises(ValueError):
            cbra_frame_components(m=3, prb_count=3)

    def test_cbra_square_law_receiver_decodes_all_m_values_without_tx_truth(self):
        expected_bits = tuple(index & 1 for index in range(240))
        for m in (2, 6, 12, 24):
            frame = cbra_frame_components(m=m)
            line_code = [chip for bit in expected_bits for chip in ((1, 0) if bit == 0 else (0, 1))]
            sequence = [1, 0, 1, 0] + line_code + [1, 1, 1, 1]
            chips = [0j] * frame["emitted_chip_count"]
            chips[:8] = [complex(bit) for bit in (1, 1, 0, 0, 1, 0, 0, 0)]
            physical_index = 8
            sequence_index = 0
            for _ in range(frame["symbols_after_sip"]):
                for position in range(m):
                    if m == 24 and position >= m - 2:
                        chips[physical_index] = 1 + 0j
                    else:
                        chips[physical_index] = complex(
                            sequence[sequence_index]
                            if sequence_index < len(sequence)
                            else (1 if m == 24 and sequence_index - len(sequence) >= frame["padding_chips"] - 2 else 0)
                        )
                        sequence_index += 1
                    physical_index += 1

            receiver = CbraSquareLawReceiver()
            energies = receiver.integrate_chip_energies(
                cbra_expand_compact_chips(chips, m=m),
                m=m,
                chip_count=len(chips),
            )
            decoded_bits = receiver.decide_manchester_bits(
                tuple(energies[index] for index in cbra_prdch_physical_indices(m=m))
            )
            self.assertEqual(decoded_bits, expected_bits)

    def test_cbra_square_law_reversal_changes_the_decision(self):
        m = 24
        frame = cbra_frame_components(m=m)
        chips = [0j] * frame["emitted_chip_count"]
        chips[:8] = [complex(bit) for bit in (1, 1, 0, 0, 1, 0, 0, 0)]
        sequence = [1, 0, 1, 0] + [1, 0] * 240 + [1, 1, 1, 1]
        physical_index = 8
        sequence_index = 0
        for _ in range(frame["symbols_after_sip"]):
            for position in range(m):
                if m == 24 and position >= m - 2:
                    chips[physical_index] = 1 + 0j
                else:
                    chips[physical_index] = complex(
                        sequence[sequence_index]
                        if sequence_index < len(sequence)
                        else (1 if sequence_index - len(sequence) >= frame["padding_chips"] - 2 else 0)
                    )
                    sequence_index += 1
                physical_index += 1
        first, second = cbra_prdch_physical_indices(m=m)[:2]
        chips[first], chips[second] = chips[second], chips[first]
        receiver = CbraSquareLawReceiver()
        energies = receiver.integrate_chip_energies(
            cbra_expand_compact_chips(chips, m=m),
            m=m,
            chip_count=len(chips),
        )
        decoded_bits = receiver.decide_manchester_bits(
            tuple(energies[index] for index in cbra_prdch_physical_indices(m=m))
        )
        self.assertEqual(decoded_bits[0], 1)

    def test_cbra_power_gate_measures_prdch_only_and_rejects_out_of_tolerance(self):
        waveforms = {}
        for m in (2, 6, 12, 24):
            frame = cbra_frame_components(m=m)
            samples = [0j] * frame["emitted_chip_count"]
            for offset, index in enumerate(cbra_prdch_physical_indices(m=m)):
                samples[index] = 1 + 0j if offset % 2 == 0 else 0j
            waveforms[m] = samples
        self.assertEqual(cbra_prdch_mean_power(waveforms[2], m=2), 0.5)
        passed = cbra_power_calibration_report(waveforms, target_power=0.5, tolerance=0.01)
        self.assertTrue(passed["passed"])

        waveforms[24] = [1 + 0j] * len(waveforms[24])
        failed = cbra_power_calibration_report(waveforms, target_power=0.5, tolerance=0.01)
        self.assertFalse(failed["passed"])
        self.assertFalse(failed["points"]["24"]["within_tolerance"])

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

        separate_seed_controller = TalanetEpochController(
            request=lambda command: (
                requests.append(command),
                "AIOT_T2_CHANNEL_EPOCH epoch=3 attenuation_db=10.000 noise_power=0.100000 seed=9 "
                "data_seed=9 noise_seed=11 readback=ok queued=0",
            )[1]
        )
        state = separate_seed_controller.set_epoch(
            attenuation_db=10, noise_power=0.1, data_seed=9, noise_seed=11, drained=True
        )
        self.assertEqual(state["data_seed"], 9)
        self.assertEqual(state["noise_seed"], 11)
        self.assertEqual(requests[-1], "rfsimu aiot_epoch set 10 0.1 9 11")

        queued_controller = TalanetEpochController(
            request=lambda _command: "AIOT_T2_CHANNEL_EPOCH epoch=3 attenuation_db=10.000 noise_power=0.100000 seed=9 readback=ok queued=1"
        )
        with self.assertRaises(RuntimeError):
            queued_controller.set_epoch(attenuation_db=10, noise_power=0.1, seed=9, drained=True)

    def test_cbra_attempt_epoch_binding_is_unique_and_fail_closed(self):
        binder = CbraAttemptEpochBinder()
        state = {
            "epoch": 4,
            "attenuation_db": 10.0,
            "noise_power": 0.1,
            "seed": 9,
            "data_seed": 9,
            "noise_seed": 11,
            "readback": "ok",
            "queued": 0,
        }
        self.assertEqual(binder.bind(attempt_index=0, epoch_state=state)["channel_epoch"], 4)
        with self.assertRaises(ValueError):
            binder.bind(attempt_index=0, epoch_state=state)
        with self.assertRaises(RuntimeError):
            binder.bind(attempt_index=1, epoch_state={**state, "queued": 1})

    def test_cbra_channel_provenance_is_replayable_and_epoch_sensitive(self):
        arguments = {
            "seed": 9,
            "tag_id": 100,
            "reader_handle": 1,
            "epoch": 4,
            "timestamp": 1234,
            "tbit": 1,
        }
        first = deterministic_channel_provenance(**arguments)
        self.assertEqual(first, deterministic_channel_provenance(**arguments))
        self.assertEqual(first, 0x148F1FEA3751507E)
        self.assertNotEqual(first, deterministic_channel_provenance(**{**arguments, "epoch": 5}))

    def test_cbra_snr_calibration_uses_separate_powers_without_adaptation(self):
        calibration = cbra_snr_calibration(signal_power=1.0, noise_power=0.1)
        self.assertEqual(calibration["snr_db_x10"], 100)
        self.assertFalse(calibration["per_packet_adaptation"])
        self.assertIsNone(cbra_snr_calibration(signal_power=1.0, noise_power=0.0)["snr_db_x10"])
        self.assertIsNone(cbra_snr_calibration(signal_power=0.0, noise_power=0.0)["snr_db_x10"])

    def test_cbra_observation_v4_preserves_kind_lengths_epoch_and_gate_fields(self):
        datagram = CBRA_OBSERVATION_STRUCT.pack(
            AIOT_T2_OBSERVATION_MAGIC,
            4,
            1,
            4,
            1,
            100,
            7,
            0xABC,
            0,
            6,
            3,
            2,
            2,
            1,
            224,
            240,
            50,
            0,
            10,
            20,
            4,
            0x1234,
            9,
            11,
            1,
            0,
            1,
            1,
            0,
            b"\0",
            224,
            2,
            269_904,
            17_571_875,
            bytes(range(30)),
            bytes(reversed(range(30))),
            65_536,
            6_554,
            bytes(12),
        )
        report = decode_cbra_observation_datagram(datagram)
        self.assertEqual(report["version"], 4)
        self.assertEqual(report["message_kind"], 0)
        self.assertEqual(report["mac_bits"], 224)
        self.assertEqual(report["phy_bits"], 240)
        self.assertEqual(report["channel_epoch"], 4)
        self.assertEqual(report["channel_provenance"], 0x1234)
        self.assertEqual(report["m"], 6)
        self.assertEqual(report["gate_status"], 2)
        self.assertTrue(report["setup"])
        self.assertEqual(report["calibrated_snr_db_x10"], 100)
        self.assertEqual(report["tx_pdu"], bytes(range(28)))

        with self.assertRaises(ValueError):
            decode_cbra_observation_datagram(datagram[:-1])

    def test_cbra_access_trigger_report_uses_three_mac_bits(self):
        datagram = CBRA_OBSERVATION_STRUCT.pack(
            AIOT_T2_OBSERVATION_MAGIC,
            4,
            1,
            0,
            1,
            100,
            7,
            0xABC,
            1,
            24,
            3,
            2,
            1,
            0,
            3,
            9,
            50,
            0,
            10,
            20,
            4,
            0x1234,
            9,
            11,
            1,
            0,
            1,
            1,
            0,
            b"\0",
            3,
            0,
            56,
            285_938,
            bytes([0x40, 0]) + bytes(28),
            bytes([0x40, 0]) + bytes(28),
            65_536,
            6_554,
            bytes(12),
        )
        report = decode_cbra_observation_datagram(datagram)
        self.assertEqual(report["message_kind"], 1)
        self.assertEqual(report["mac_bits"], 3)
        self.assertEqual(report["phy_bits"], 9)
        self.assertEqual(report["tx_pdu"], bytes([0x40, 0]))
        row = cbra_observation_to_campaign_row(report, snr_db_x10=50)
        self.assertEqual(row["message_kind"], 1)
        self.assertEqual(row["mac_bits"], 3)
        self.assertEqual(row["r2d_on_air_duration_ns"], 285_938)

        with self.assertRaises(ValueError):
            cbra_observation_to_campaign_row({"version": 3}, snr_db_x10=50)


if __name__ == "__main__":
    unittest.main()
