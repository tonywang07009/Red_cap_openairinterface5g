"""D2R BER measurement primitives.

The module name follows the user-requested project layout.  It is a simulator
measurement interface and does not claim a real Reader BER estimator.
"""

from dataclasses import asdict, dataclass, field
from fractions import Fraction
import hashlib
import math
from random import Random
import struct


AIOT_T2_OBSERVATION_MAGIC = 0x41494F42
AIOT_T2_OBSERVATION_VERSION = 1
AIOT_T2_MAX_PAYLOAD_BYTES = 16
AIOT_T2_MAX_TAGS = 100
BASE_BIT_DURATION_US = 2_000_000 / 15_000
CAMPAIGN_DURATION_MULTIPLIERS = (1 / 96, 1 / 32, 1 / 16, 1 / 8, 1 / 4, 1 / 2, 1.0, 2.0)
CAMPAIGN_REPEAT_COUNT = 5
CAMPAIGN_CYCLES_PER_REPEAT = 100
CBRA_SUPPORTED_M = (2, 6, 12, 24)
CBRA_PRB_COUNT = 3
CBRA_PAGING_KIND = 0
CBRA_ACCESS_TRIGGER_KIND = 1
CBRA_PAGING_PDU_BITS = 224
CBRA_PAGING_PHY_BITS = 240
CBRA_TRIGGER_PDU_BITS = 3
CBRA_TRIGGER_PHY_BITS = 9
CBRA_FORMAL_PACKET_BUDGET = 10_000
# A frozen point is the pilot-derived SNR center; each row retains its exact
# pre-square-law calibration and the point mean must remain within this window.
CBRA_SNR_POINT_TOLERANCE_DB_X10 = 10
CBRA_SAMPLE_RATE_HZ = 15_360_000
CBRA_USEFUL_SAMPLES_PER_SYMBOL = 1_024
CBRA_LONG_CP_SAMPLES = 80
CBRA_SHORT_CP_SAMPLES = 72
CBRA_OBS_FLAG_SETUP = 0x0004
OBSERVATION_STRUCT = struct.Struct("!IBBHIIQQB3sHH16s16sQ")
CBRA_OBSERVATION_STRUCT = struct.Struct("!IBBHIIIQBBBBBBHHhHQQQQQQBBBBB1sHHIQ30s30sQQHBBII")
OBSERVATION_STATUS = {
    1: "complete",
    2: "crc_failure",
    3: "undetected",
    4: "unaligned",
    5: "invalid",
}


def sample_ticks_to_ns(ticks: int, sample_rate_hz: float) -> int:
    """Convert RFsim ticks with exact decimal-rate arithmetic and half-up rounding."""
    if ticks < 0 or sample_rate_hz <= 0:
        raise ValueError("ticks must be non-negative and sample_rate_hz must be positive")
    rate = Fraction(str(sample_rate_hz))
    numerator = ticks * 1_000_000_000 * rate.denominator
    return (numerator + rate.numerator // 2) // rate.numerator


def payload_bits(payload: bytes) -> tuple[int, ...]:
    return tuple((byte >> bit) & 1 for byte in payload for bit in range(7, -1, -1))


def decode_observation_datagram(data: bytes) -> dict:
    """Decode the fixed 80-byte RFsim observation report without guessing fields."""
    if len(data) != OBSERVATION_STRUCT.size:
        raise ValueError(f"observation datagram must be {OBSERVATION_STRUCT.size} bytes")
    (
        magic,
        version,
        status,
        flags,
        reader_id,
        tag_id,
        tx_timestamp,
        completion_timestamp,
        payload_len,
        _reserved,
        compared_bits,
        erroneous_bits,
        tx_payload,
        decoded_payload,
        channel_provenance,
    ) = OBSERVATION_STRUCT.unpack(data)
    if magic != AIOT_T2_OBSERVATION_MAGIC or version != AIOT_T2_OBSERVATION_VERSION:
        raise ValueError("unsupported observation report")
    if status not in OBSERVATION_STATUS:
        raise ValueError("unknown observation status")
    if payload_len > AIOT_T2_MAX_PAYLOAD_BYTES:
        raise ValueError("observation payload length exceeds 16 bytes")
    return {
        "status": OBSERVATION_STATUS[status],
        "status_code": status,
        "flags": flags,
        "reader_id": reader_id,
        "tag_id": tag_id,
        "tx_timestamp": tx_timestamp,
        "completion_timestamp": completion_timestamp,
        "payload_len": payload_len,
        "compared_bits": compared_bits,
        "erroneous_bits": erroneous_bits,
        "tx_payload": bytes(tx_payload[:payload_len]),
        "decoded_payload": bytes(decoded_payload[:payload_len]),
        "channel_provenance": channel_provenance,
    }


def decode_cbra_observation_datagram(data: bytes) -> dict:
    if len(data) != CBRA_OBSERVATION_STRUCT.size:
        raise ValueError(f"CBRA observation datagram must be {CBRA_OBSERVATION_STRUCT.size} bytes")
    (
        magic,
        version,
        status,
        flags,
        reader_handle,
        tag_id,
        attempt_index,
        packet_id,
        message_kind,
        m,
        prb_count,
        pdu_profile_version,
        gate_status,
        context_eligible,
        mac_bits,
        phy_bits,
        snr_db_x10,
        _reserved_header,
        tx_timestamp,
        completion_timestamp,
        channel_epoch,
        channel_provenance,
        data_seed,
        noise_seed,
        epoch_readback,
        d2r_attempted,
        crc_ok,
        payload_match,
        decode_result,
        _reserved_status,
        compared_bits,
        erroneous_bits,
        full_airtime_samples,
        full_airtime_ns,
        tx_pdu,
        decoded_pdu,
        signal_power_q16,
        noise_power_q16,
        random_id,
        access_occasion,
        msg2_status,
        config_version,
        config_round,
    ) = CBRA_OBSERVATION_STRUCT.unpack(data)
    if magic != AIOT_T2_OBSERVATION_MAGIC or version != 4:
        raise ValueError("unsupported CBRA observation report")
    if status not in OBSERVATION_STATUS:
        raise ValueError("unknown CBRA observation status")
    if message_kind not in {CBRA_PAGING_KIND, CBRA_ACCESS_TRIGGER_KIND}:
        raise ValueError("unsupported CBRA message kind")
    expected_mac_bits = CBRA_PAGING_PDU_BITS if message_kind == CBRA_PAGING_KIND else CBRA_TRIGGER_PDU_BITS
    expected_phy_bits = CBRA_PAGING_PHY_BITS if message_kind == CBRA_PAGING_KIND else CBRA_TRIGGER_PHY_BITS
    if (m not in CBRA_SUPPORTED_M or prb_count != CBRA_PRB_COUNT or pdu_profile_version != 2
            or mac_bits != expected_mac_bits or phy_bits != expected_phy_bits):
        raise ValueError("unsupported CBRA profile fields")
    gate_values = (context_eligible, epoch_readback, d2r_attempted, crc_ok, payload_match)
    if gate_status not in {0, 1, 2} or any(value not in {0, 1} for value in gate_values):
        raise ValueError("invalid CBRA gate fields")
    if compared_bits > mac_bits or erroneous_bits > compared_bits:
        raise ValueError("invalid CBRA bit counters")
    pdu_bytes = CBRA_PAGING_PDU_BITS // 8 if message_kind == CBRA_PAGING_KIND else 2
    signal_power = signal_power_q16 / (1 << 16)
    noise_power = noise_power_q16 / (1 << 16)
    calibrated_snr_db_x10 = cbra_snr_calibration(
        signal_power=signal_power,
        noise_power=noise_power,
    )["snr_db_x10"]
    return {
        "version": version,
        "status": OBSERVATION_STATUS[status],
        "status_code": status,
        "flags": flags,
        "reader_id": reader_handle,
        "tag_id": tag_id,
        "attempt_index": attempt_index,
        "packet_id": packet_id,
        "message_kind": message_kind,
        "mac_bits": mac_bits,
        "phy_bits": phy_bits,
        "tx_timestamp": tx_timestamp,
        "completion_timestamp": completion_timestamp,
        "channel_epoch": channel_epoch,
        "channel_provenance": channel_provenance,
        "data_seed": data_seed,
        "noise_seed": noise_seed,
        "snr_db_x10": snr_db_x10,
        "m": m,
        "prb_count": prb_count,
        "pdu_profile_version": pdu_profile_version,
        "gate_status": gate_status,
        "context_eligible": bool(context_eligible),
        "setup": bool(flags & CBRA_OBS_FLAG_SETUP),
        "epoch_readback": bool(epoch_readback),
        "d2r_attempted": bool(d2r_attempted),
        "crc_ok": bool(crc_ok),
        "payload_match": bool(payload_match),
        "decode_result": decode_result,
        "compared_bits": compared_bits,
        "erroneous_bits": erroneous_bits,
        "full_airtime_samples": full_airtime_samples,
        "full_airtime_ns": full_airtime_ns,
        "signal_power_q16": signal_power_q16,
        "noise_power_q16": noise_power_q16,
        "signal_power": signal_power,
        "noise_power": noise_power,
        "calibrated_snr_db_x10": calibrated_snr_db_x10,
        "random_id": random_id,
        "access_occasion": access_occasion,
        "msg2_status": msg2_status,
        "config_version": config_version,
        "config_round": config_round,
        "tx_pdu": bytes(tx_pdu[:pdu_bytes]),
        "decoded_pdu": bytes(decoded_pdu[:pdu_bytes]),
    }


@dataclass(frozen=True)
class ReaderBerObservation:
    """One closed 0.5 ms-equivalent Reader observation window."""

    reader_id: int
    window_index: int
    window_start_ns: int
    window_end_ns: int
    available_at_ns: int
    completed_packets: int
    actual_tx_packets: int
    undetected_packets: int
    unaligned_packets: int
    compared_bits: int
    erroneous_bits: int
    ber: float | None
    packet_loss_rate: float | None
    valid: bool
    invalid_evidence_count: int
    invalid_reasons: tuple[str, ...]
    channel_provenance: int | None = None

    def to_dict(self) -> dict:
        """Return the JSON-ready observation record, including loss counters."""
        record = asdict(self)
        record["invalid_reasons"] = list(self.invalid_reasons)
        return record


@dataclass(frozen=True)
class D2RReservation:
    admitted: bool
    reason: str | None


class D2RMeasurementService:
    """Accumulate completed-packet BER by Reader and completion window."""

    def __init__(self, window_ns: int = 500_000):
        if window_ns <= 0:
            raise ValueError("window_ns must be positive")
        self._window_ns = window_ns
        # compared bits, errors, completed packets, actual TX, undetected, unaligned
        self._counts: dict[tuple[int, int], list[int]] = {}
        self._invalid_evidence: dict[tuple[int, int], list[str]] = {}
        self._provenance: dict[tuple[int, int], set[int]] = {}

    def record_completed_packet(
        self,
        *,
        reader_id: int,
        completion_ns: int,
        transmitted_bits: tuple[int, ...],
        decoded_bits: tuple[int, ...],
        channel_provenance: int | None = None,
    ) -> None:
        if reader_id <= 0:
            raise ValueError("reader_id must be positive")
        if completion_ns < 0:
            raise ValueError("completion_ns must be non-negative")
        if len(transmitted_bits) != len(decoded_bits):
            raise ValueError("transmitted_bits and decoded_bits must have equal length")
        if not transmitted_bits:
            raise ValueError("bit sequences must not be empty")
        if any(bit not in (0, 1) for bit in transmitted_bits + decoded_bits):
            raise ValueError("bit sequences must contain only 0 or 1")

        window_index = completion_ns // self._window_ns
        counts = self._counts.setdefault((reader_id, window_index), [0, 0, 0, 0, 0, 0])
        counts[0] += len(transmitted_bits)
        counts[1] += sum(tx != rx for tx, rx in zip(transmitted_bits, decoded_bits))
        counts[2] += 1
        counts[3] += 1
        self._remember_provenance(reader_id, window_index, channel_provenance)

    def record_acquisition_loss(
        self,
        *,
        reader_id: int,
        tx_ns: int,
        loss_kind: str,
        channel_provenance: int | None = None,
    ) -> None:
        """Record an observed undetected or unaligned transmitted packet."""
        if reader_id <= 0:
            raise ValueError("reader_id must be positive")
        if tx_ns < 0:
            raise ValueError("tx_ns must be non-negative")
        if loss_kind not in {"undetected", "unaligned"}:
            raise ValueError("loss_kind must be undetected or unaligned")

        window_index = tx_ns // self._window_ns
        counts = self._counts.setdefault((reader_id, window_index), [0, 0, 0, 0, 0, 0])
        counts[3] += 1
        counts[4 if loss_kind == "undetected" else 5] += 1
        self._remember_provenance(reader_id, window_index, channel_provenance)

    def record_missing_evidence(
        self, *, reader_id: int, tx_ns: int, reason: str, channel_provenance: int | None = None
    ) -> None:
        """Preserve an unclassified transmitted packet as invalid evidence."""
        if reader_id <= 0:
            raise ValueError("reader_id must be positive")
        if tx_ns < 0:
            raise ValueError("tx_ns must be non-negative")
        if not reason:
            raise ValueError("reason must not be empty")

        window_index = tx_ns // self._window_ns
        counts = self._counts.setdefault((reader_id, window_index), [0, 0, 0, 0, 0, 0])
        counts[3] += 1
        self._invalid_evidence.setdefault((reader_id, window_index), []).append(reason)
        self._remember_provenance(reader_id, window_index, channel_provenance)

    def _remember_provenance(self, reader_id: int, window_index: int, provenance: int | None) -> None:
        if provenance is not None:
            self._provenance.setdefault((reader_id, window_index), set()).add(int(provenance))

    def record_wire_observation(self, report: dict, *, sample_rate_hz: float) -> None:
        """Apply one decoded RFsim report; truth and decoder payloads stay explicit."""
        completion_ns = sample_ticks_to_ns(report["completion_timestamp"], sample_rate_hz)
        tx_ns = sample_ticks_to_ns(report["tx_timestamp"], sample_rate_hz)
        provenance = report.get("channel_provenance")
        status = report["status"]
        if status in {"complete", "crc_failure"}:
            tx = payload_bits(report["tx_payload"])
            decoded = payload_bits(report["decoded_payload"])
            if not tx or len(tx) != len(decoded):
                self.record_missing_evidence(
                    reader_id=report["reader_id"],
                    tx_ns=tx_ns,
                    reason="payload_length_mismatch",
                    channel_provenance=provenance,
                )
                return
            self.record_completed_packet(
                reader_id=report["reader_id"],
                completion_ns=completion_ns,
                transmitted_bits=tx,
                decoded_bits=decoded,
                channel_provenance=provenance,
            )
            return
        if status in {"undetected", "unaligned"}:
            self.record_acquisition_loss(
                reader_id=report["reader_id"],
                tx_ns=tx_ns,
                loss_kind=status,
                channel_provenance=provenance,
            )
            return
        self.record_missing_evidence(
            reader_id=report["reader_id"],
            tx_ns=tx_ns,
            reason=f"invalid_observation:{status}",
            channel_provenance=provenance,
        )

    def closed_observation(self, *, reader_id: int, window_index: int) -> ReaderBerObservation:
        if reader_id <= 0:
            raise ValueError("reader_id must be positive")
        if window_index < 0:
            raise ValueError("window_index must be non-negative")

        (
            compared_bits,
            erroneous_bits,
            completed_packets,
            actual_tx_packets,
            undetected_packets,
            unaligned_packets,
        ) = self._counts.get((reader_id, window_index), [0, 0, 0, 0, 0, 0])
        invalid_reasons = tuple(self._invalid_evidence.get((reader_id, window_index), []))
        provenances = tuple(sorted(self._provenance.get((reader_id, window_index), set())))
        window_start_ns = window_index * self._window_ns
        window_end_ns = window_start_ns + self._window_ns
        return ReaderBerObservation(
            reader_id=reader_id,
            window_index=window_index,
            window_start_ns=window_start_ns,
            window_end_ns=window_end_ns,
            available_at_ns=window_end_ns,
            completed_packets=completed_packets,
            actual_tx_packets=actual_tx_packets,
            undetected_packets=undetected_packets,
            unaligned_packets=unaligned_packets,
            compared_bits=compared_bits,
            erroneous_bits=erroneous_bits,
            ber=None if compared_bits == 0 or invalid_reasons else erroneous_bits / compared_bits,
            packet_loss_rate=(
                None
                if actual_tx_packets == 0 or invalid_reasons
                else (undetected_packets + unaligned_packets) / actual_tx_packets
            ),
            valid=not invalid_reasons,
            invalid_evidence_count=len(invalid_reasons),
            invalid_reasons=invalid_reasons,
            channel_provenance=provenances[0] if len(provenances) == 1 else None,
        )


def _nonnegative_int(row: dict, name: str) -> int:
    value = row.get(name, 0)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def aggregate_campaign_rows(
    rows: list[dict],
    *,
    duration_multipliers: tuple[float, ...] = CAMPAIGN_DURATION_MULTIPLIERS,
    repeat_count: int = CAMPAIGN_REPEAT_COUNT,
    cycles_per_repeat: int = CAMPAIGN_CYCLES_PER_REPEAT,
) -> dict:
    """Aggregate a fixed-budget manifest without inventing missing RF evidence."""
    expected = {
        (duration_index, repeat, cycle)
        for duration_index in range(len(duration_multipliers))
        for repeat in range(repeat_count)
        for cycle in range(cycles_per_repeat)
    }
    seen: set[tuple[int, int, int]] = set()
    source: str | None = None
    totals = [
        {"actual_tx_packets": 0, "undetected_packets": 0, "unaligned_packets": 0,
         "compared_bits": 0, "erroneous_bits": 0, "deferrals": 0, "invalid_runs": 0}
        for _ in duration_multipliers
    ]

    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("campaign rows must be JSON objects")
        duration_index = row.get("duration_index")
        repeat = row.get("repeat")
        cycle = row.get("cycle")
        key = (duration_index, repeat, cycle)
        if any(isinstance(value, bool) or not isinstance(value, int) for value in key):
            raise ValueError("duration_index, repeat, and cycle must be integers")
        if key not in expected:
            raise ValueError(f"campaign variant is outside the fixed budget: {key}")
        if key in seen:
            raise ValueError(f"duplicate campaign variant: {key}")
        seen.add(key)
        multiplier = row.get("duration_multiplier")
        if multiplier != duration_multipliers[duration_index]:
            raise ValueError(f"duration multiplier does not match duration_index {duration_index}")
        row_source = row.get("source")
        if row_source not in {"rfsim", "numerical_model"}:
            raise ValueError("source must be rfsim or numerical_model")
        if source is None:
            source = row_source
        elif source != row_source:
            raise ValueError("campaign cannot mix evidence sources")
        total = totals[duration_index]
        for name in total:
            total[name] += _nonnegative_int(row, name)
        invalid = row.get("invalid", False)
        if not isinstance(invalid, bool):
            raise ValueError("invalid must be boolean")
        total["invalid_runs"] += int(invalid)
    missing = sorted(expected - seen)
    if missing:
        raise ValueError(f"campaign manifest is missing {len(missing)} fixed-budget variants")

    duration_results = []
    for duration_index, multiplier in enumerate(duration_multipliers):
        total = totals[duration_index]
        invalid = total["invalid_runs"] > 0
        compared = total["compared_bits"]
        tx_packets = total["actual_tx_packets"]
        losses = total["undetected_packets"] + total["unaligned_packets"]
        duration_results.append(
            {
                "duration_index": duration_index,
                "duration_multiplier": multiplier,
                "duration_ns": multiplier * BASE_BIT_DURATION_US * 1_000.0,
                **total,
                "ber": None if compared == 0 or invalid else total["erroneous_bits"] / compared,
                "packet_loss_rate": None if tx_packets == 0 or invalid else losses / tx_packets,
                "valid": not invalid,
                "source": source,
            }
        )
    return {
        "schema_version": 2,
        "campaign": {
            "duration_multipliers": list(duration_multipliers),
            "repeat_count": repeat_count,
            "cycles_per_repeat": cycles_per_repeat,
            "variant_count": len(seen),
            "fixed_stop": True,
            "source": source,
            "sampling": "independent channel/noise draws per duration, repeat, physical link, Tag, and cycle",
        },
        "duration_results": duration_results,
    }


def _wilson_interval(failures: int, trials: int) -> dict[str, float] | None:
    if trials < 0 or failures < 0 or failures > trials:
        raise ValueError("Wilson interval counts are invalid")
    if trials == 0:
        return None
    z = 1.96
    proportion = failures / trials
    denominator = 1.0 + z * z / trials
    centre = (proportion + z * z / (2.0 * trials)) / denominator
    radius = z * math.sqrt(proportion * (1.0 - proportion) / trials + z * z / (4.0 * trials * trials)) / denominator
    return {"lower": max(0.0, centre - radius), "upper": min(1.0, centre + radius)}


@dataclass
class _IirSection:
    b0: float
    b1: float
    b2: float
    a1: float
    a2: float
    x1: complex | float = 0.0
    x2: complex | float = 0.0
    y1: complex | float = 0.0
    y2: complex | float = 0.0

    def process(self, value: complex | float) -> complex | float:
        output = self.b0 * value + self.b1 * self.x1 + self.b2 * self.x2 - self.a1 * self.y1 - self.a2 * self.y2
        self.x2, self.x1 = self.x1, value
        self.y2, self.y1 = self.y1, output
        return output


def _butterworth_sections(cutoff_hz: float, sample_rate_hz: int) -> tuple[_IirSection, _IirSection]:
    """Build the bilinear-transform 3rd-order Butterworth sections."""
    if not 0 < cutoff_hz < sample_rate_hz / 2:
        raise ValueError("Butterworth cutoff must be below Nyquist")
    k = math.tan(math.pi * cutoff_hz / sample_rate_hz)
    first_denominator = 1.0 + k
    first = _IirSection(
        b0=k / first_denominator,
        b1=k / first_denominator,
        b2=0.0,
        a1=(1.0 - k) / first_denominator,
        a2=0.0,
    )
    second_denominator = 1.0 + k + k * k
    second = _IirSection(
        b0=k * k / second_denominator,
        b1=2.0 * k * k / second_denominator,
        b2=k * k / second_denominator,
        a1=(-2.0 + 2.0 * k * k) / second_denominator,
        a2=(1.0 - k + k * k) / second_denominator,
    )
    return first, second


def _filter_value(sections: tuple[_IirSection, _IirSection], value: complex | float) -> complex | float:
    for section in sections:
        value = section.process(value)
    return value


def _fractional_integral(values: list[float], start: Fraction, end: Fraction) -> float:
    if end <= start:
        return 0.0
    total = 0.0
    first = max(0, start.numerator // start.denominator)
    last = min(len(values), (end.numerator + end.denominator - 1) // end.denominator)
    for index in range(first, last):
        overlap = min(end, Fraction(index + 1)) - max(start, Fraction(index))
        if overlap > 0:
            total += values[index] * float(overlap)
    return total


def _cbra_symbol_start_samples(symbol: int) -> int:
    long_cp_count = (symbol + 6) // 7
    short_cp_count = symbol - long_cp_count
    return symbol * CBRA_USEFUL_SAMPLES_PER_SYMBOL + long_cp_count * CBRA_LONG_CP_SAMPLES + short_cp_count * CBRA_SHORT_CP_SAMPLES


@dataclass
class CbraSquareLawReceiver:
    """Stateful ideal-acquisition receiver for the compact CBRA waveform model."""

    sample_rate_hz: int = CBRA_SAMPLE_RATE_HZ
    decimation: int = 4
    preselection_cutoff_hz: float = 270_000.0
    smoothing_cutoff_hz: float = 540_000.0
    calibrated_delay_samples: Fraction = Fraction(0)
    _preselection: tuple[_IirSection, _IirSection] = field(init=False)
    _smoothing: tuple[_IirSection, _IirSection] = field(init=False)
    _input_samples: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        if self.sample_rate_hz <= 0 or self.decimation <= 0:
            raise ValueError("receiver sample rate and decimation must be positive")
        if self.sample_rate_hz % self.decimation:
            raise ValueError("receiver sample rate must divide evenly by decimation")
        self.calibrated_delay_samples = Fraction(self.calibrated_delay_samples)
        if self.calibrated_delay_samples < 0:
            raise ValueError("receiver calibrated delay must be non-negative")
        self._preselection = _butterworth_sections(self.preselection_cutoff_hz, self.sample_rate_hz)
        self._smoothing = _butterworth_sections(self.smoothing_cutoff_hz, self.sample_rate_hz)

    @property
    def output_sample_rate_hz(self) -> int:
        return self.sample_rate_hz // self.decimation

    def process(self, samples: list[complex]) -> list[float]:
        """Filter, square-law detect, smooth, and decimate one contiguous sample chunk."""
        output: list[float] = []
        for sample in samples:
            filtered = _filter_value(self._preselection, complex(sample))
            power = filtered.real * filtered.real + filtered.imag * filtered.imag
            smoothed = _filter_value(self._smoothing, power)
            if self._input_samples % self.decimation == self.decimation - 1:
                output.append(float(smoothed))
            self._input_samples += 1
        return output

    def integrate_chip_energies(self, samples: list[complex], *, m: int, chip_count: int) -> tuple[float, ...]:
        if m not in CBRA_SUPPORTED_M or chip_count <= 0:
            raise ValueError("invalid CBRA receiver geometry")
        if len(samples) % self.decimation:
            raise ValueError("receiver input must end on a decimation boundary")
        decimated = self.process(samples)
        delay = self.calibrated_delay_samples
        energies = []
        for index in range(chip_count):
            if index < 8:
                symbol = index // 4
                position = index % 4
                chip_span = Fraction(64)
            else:
                symbol = 2 + (index - 8) // m
                position = (index - 8) % m
                chip_span = Fraction(256, m)
            useful_start = Fraction(_cbra_symbol_start_samples(symbol), self.decimation)
            useful_start += Fraction(80 if symbol % 7 == 0 else 72, self.decimation)
            start = useful_start + position * chip_span + delay
            energies.append(_fractional_integral(decimated, start, start + chip_span))
        return tuple(energies)

    @staticmethod
    def decide_manchester_bits(chip_energies: tuple[float, ...]) -> tuple[int, ...]:
        if len(chip_energies) == 0 or len(chip_energies) % 2:
            raise ValueError("Manchester energy input must contain complete pairs")
        bits = []
        for first, second in zip(chip_energies[::2], chip_energies[1::2]):
            if first == second:
                raise ValueError("Manchester pair has equal energy")
            bits.append(int(second > first))
        return tuple(bits)


def cbra_expand_compact_chips(chips: list[complex], *, m: int) -> list[complex]:
    """Lift one RFsim logical chip to 15.36 Msps rectangular samples."""
    if m not in CBRA_SUPPORTED_M or not chips:
        raise ValueError("compact CBRA chip input is invalid")
    if len(chips) < 8 or (len(chips) - 8) % m:
        raise ValueError("compact CBRA chip input does not align to M symbols")
    symbols_after_sip = (len(chips) - 8) // m
    frame_symbols = 2 + symbols_after_sip
    sample_count = _cbra_symbol_start_samples(frame_symbols)
    samples: list[complex] = []
    symbol = 0
    symbol_start = 0
    symbol_end = 80 + CBRA_USEFUL_SAMPLES_PER_SYMBOL
    for index in range(sample_count):
        while symbol + 1 < frame_symbols and index >= symbol_end:
            symbol += 1
            symbol_start = _cbra_symbol_start_samples(symbol)
            symbol_end = symbol_start + (80 if symbol % 7 == 0 else 72) + CBRA_USEFUL_SAMPLES_PER_SYMBOL
        cp = 80 if symbol % 7 == 0 else 72
        if index < symbol_start + cp:
            samples.append(0j)
            continue
        useful_index = index - symbol_start - cp
        position = useful_index // 256 if symbol < 2 else useful_index * m // CBRA_USEFUL_SAMPLES_PER_SYMBOL
        chip_index = symbol * 4 + position if symbol < 2 else 8 + (symbol - 2) * m + position
        samples.append(complex(chips[min(len(chips) - 1, chip_index)]))
    return samples


def cbra_prdch_physical_indices(*, m: int, message_kind: int = CBRA_PAGING_KIND) -> tuple[int, ...]:
    frame = cbra_frame_components(m=m, message_kind=message_kind)
    indices: list[int] = []
    sequence_index = 0
    physical_index = frame["r_tas_sip_chips"]
    for _ in range(frame["symbols_after_sip"]):
        for position in range(m):
            if m == 24 and position >= m - 2:
                physical_index += 1
                continue
            if frame["r_tas_cap_chips"] <= sequence_index < frame["r_tas_cap_chips"] + frame["prdch_chips"]:
                indices.append(physical_index)
            sequence_index += 1
            physical_index += 1
    if len(indices) != frame["prdch_chips"]:
        raise ValueError("CBRA PRDCH mapping did not produce the configured chip count")
    return tuple(indices)


def cbra_prdch_mean_power(samples: list[complex], *, m: int, message_kind: int = CBRA_PAGING_KIND) -> float:
    frame = cbra_frame_components(m=m, message_kind=message_kind)
    if len(samples) != frame["emitted_chip_count"]:
        raise ValueError("CBRA waveform length does not match M")
    indices = cbra_prdch_physical_indices(m=m, message_kind=message_kind)
    return sum(abs(samples[index]) ** 2 for index in indices) / len(indices)


def cbra_power_calibration_report(
    waveforms: dict[int, list[complex]],
    *,
    target_power: float,
    tolerance: float = 0.01,
    message_kind: int = CBRA_PAGING_KIND,
) -> dict:
    """Measure PRDCH-only power and fail the pre-formal gate outside tolerance."""
    if target_power <= 0 or tolerance < 0:
        raise ValueError("target power must be positive and tolerance must be non-negative")
    if set(waveforms) != set(CBRA_SUPPORTED_M):
        raise ValueError("power calibration requires all four CBRA M values")
    points = {}
    for m in CBRA_SUPPORTED_M:
        measured = cbra_prdch_mean_power(waveforms[m], m=m, message_kind=message_kind)
        relative_error = (measured - target_power) / target_power
        points[str(m)] = {
            "measured_mean_power": measured,
            "target_mean_power": target_power,
            "relative_error": relative_error,
            "within_tolerance": abs(relative_error) <= tolerance,
        }
    return {
        "basis": "PRDCH data chips only",
        "target_mean_power": target_power,
        "relative_tolerance": tolerance,
        "points": points,
        "passed": all(point["within_tolerance"] for point in points.values()),
    }


def cbra_snr_calibration(*, signal_power: float, noise_power: float) -> dict:
    """Calibrate SNR from separate post-filter signal/noise power measurements."""
    if signal_power < 0 or noise_power < 0:
        raise ValueError("signal and noise power must be non-negative")
    snr_db_x10 = None if noise_power == 0 or signal_power == 0 else math.floor(
        100.0 * math.log10(signal_power / noise_power) + 0.5
    )
    return {
        "receiver_reference_plane": "after pre-selection filter, before square-law",
        "signal_power": signal_power,
        "noise_power": noise_power,
        "snr_db_x10": snr_db_x10,
        "per_packet_adaptation": False,
    }


def cbra_observation_to_campaign_row(report: dict, *, snr_db_x10: int | None = None) -> dict:
    """Convert one v4 RFsim report into the fixed-budget aggregation shape."""
    if report.get("version") != 4:
        raise ValueError("formal CBRA campaign rows require the v4 observation report")
    required = (
        "attempt_index",
        "channel_epoch",
        "epoch_readback",
        "message_kind",
        "m",
        "mac_bits",
        "phy_bits",
        "compared_bits",
        "erroneous_bits",
        "full_airtime_ns",
        "crc_ok",
        "payload_match",
        "d2r_attempted",
        "context_eligible",
        "setup",
    )
    if any(name not in report for name in required):
        raise ValueError("v4 observation report is missing formal campaign fields")
    calibrated_snr_db_x10 = report.get("calibrated_snr_db_x10")
    if calibrated_snr_db_x10 is None and report.get("setup") and snr_db_x10 is not None:
        calibrated_snr_db_x10 = snr_db_x10
    if isinstance(calibrated_snr_db_x10, bool) or not isinstance(calibrated_snr_db_x10, int):
        raise ValueError("v4 observation report is missing calibrated SNR")
    point_snr_db_x10 = calibrated_snr_db_x10 if snr_db_x10 is None else snr_db_x10
    if isinstance(point_snr_db_x10, bool) or not isinstance(point_snr_db_x10, int):
        raise ValueError("CBRA SNR point must be an integer")
    return {
        "message_kind": report["message_kind"],
        "m": report["m"],
        "snr_db_x10": point_snr_db_x10,
        "target_snr_db_x10": report.get("snr_db_x10", snr_db_x10),
        "attempt_index": report["attempt_index"],
        "channel_epoch": report["channel_epoch"],
        "epoch_ack": report["epoch_readback"],
        "channel_readback": report["epoch_readback"],
        "mac_bits": report["mac_bits"],
        "phy_bits": report["phy_bits"],
        "compared_bits": report["compared_bits"],
        "erroneous_bits": report["erroneous_bits"],
        "crc_ok": report["crc_ok"],
        "payload_match": report["payload_match"],
        "d2r_attempted": report["d2r_attempted"],
        "context_eligible": report["context_eligible"],
        "setup": report["setup"],
        "r2d_on_air_duration_ns": report["full_airtime_ns"],
        "signal_power_q16": report.get("signal_power_q16", 0),
        "noise_power_q16": report.get("noise_power_q16", 0),
        "calibrated_snr_db_x10": calibrated_snr_db_x10,
    }


def _cbra_message_bits(message_kind: int) -> tuple[int, int, str]:
    if message_kind == CBRA_PAGING_KIND:
        return CBRA_PAGING_PDU_BITS, CBRA_PAGING_PHY_BITS, "paging"
    if message_kind == CBRA_ACCESS_TRIGGER_KIND:
        return CBRA_TRIGGER_PDU_BITS, CBRA_TRIGGER_PHY_BITS, "access_trigger"
    raise ValueError("message_kind must be Paging (0) or Access Trigger (1)")


def cbra_frame_components(
    *, m: int, prb_count: int = CBRA_PRB_COUNT, message_kind: int = CBRA_PAGING_KIND
) -> dict:
    """Return TS 38.291 CBRA chip, symbol, CP, and sample accounting."""
    if isinstance(m, bool) or m not in CBRA_SUPPORTED_M:
        raise ValueError("m must be one of 2, 6, 12, or 24")
    if isinstance(prb_count, bool) or prb_count != CBRA_PRB_COUNT:
        raise ValueError("cbra profile requires exactly three R2D PRBs")
    mac_bits, phy_bits, message_name = _cbra_message_bits(message_kind)
    usable_chips_per_symbol = 22 if m == 24 else m
    data_and_overhead_chips = 4 + phy_bits * 2 + 4
    symbols_after_sip = (data_and_overhead_chips + usable_chips_per_symbol - 1) // usable_chips_per_symbol
    frame_symbols = 2 + symbols_after_sip
    mapping_positions = symbols_after_sip * m
    mapping_reserved_chips = symbols_after_sip * 2 if m == 24 else 0
    padding_chips = mapping_positions - mapping_reserved_chips - data_and_overhead_chips
    emitted_chip_count = 8 + mapping_positions
    long_cp_count = (frame_symbols + 6) // 7
    short_cp_count = frame_symbols - long_cp_count
    ofdm_sample_count = (
        frame_symbols * CBRA_USEFUL_SAMPLES_PER_SYMBOL
        + long_cp_count * CBRA_LONG_CP_SAMPLES
        + short_cp_count * CBRA_SHORT_CP_SAMPLES
    )
    return {
        "profile": "cbra_r2d_m_snr",
        "m": m,
        "prb_count": prb_count,
        "message_kind": message_kind,
        "message_name": message_name,
        "scs_khz": 15,
        "mac_bits": mac_bits,
        "phy_bits": phy_bits,
        "manchester_pairs": phy_bits,
        "prdch_chips": phy_bits * 2,
        "data_and_overhead_chips": data_and_overhead_chips,
        "usable_chips_per_symbol": usable_chips_per_symbol,
        "symbols_after_sip": symbols_after_sip,
        "r_tas_sip_chips": 8,
        "r_tas_cap_chips": 4,
        "postamble_chips": 4,
        "padding_chips": padding_chips,
        "mapping_reserved_chips": mapping_reserved_chips,
        "frame_symbols": frame_symbols,
        "occupied_chip_positions": emitted_chip_count,
        "emitted_chip_count": emitted_chip_count,
        "useful_samples_per_symbol": CBRA_USEFUL_SAMPLES_PER_SYMBOL,
        "long_cp_samples": CBRA_LONG_CP_SAMPLES,
        "short_cp_samples": CBRA_SHORT_CP_SAMPLES,
        "long_cp_count": long_cp_count,
        "short_cp_count": short_cp_count,
        "ofdm_sample_count": ofdm_sample_count,
        "sample_rate_hz": CBRA_SAMPLE_RATE_HZ,
        "full_r2d_airtime_ns": sample_ticks_to_ns(ofdm_sample_count, CBRA_SAMPLE_RATE_HZ),
        "m24_mapping_exception": m == 24,
    }


def aggregate_cbra_campaign_rows(rows: list[dict], *, packet_budget: int = CBRA_FORMAL_PACKET_BUDGET) -> dict:
    """Aggregate fixed-budget CBRA M/SNR evidence without fabricating missing RF state."""
    if packet_budget != CBRA_FORMAL_PACKET_BUDGET:
        raise ValueError("formal CBRA packet budget must be exactly 10000")
    if not isinstance(rows, list) or not rows:
        raise ValueError("CBRA campaign rows must be a non-empty list")

    groups: dict[tuple[int, int, int], dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("CBRA campaign rows must be JSON objects")
        message_kind = row.get("message_kind")
        if isinstance(message_kind, bool) or message_kind not in {CBRA_PAGING_KIND, CBRA_ACCESS_TRIGGER_KIND}:
            raise ValueError("row message_kind is not a supported CBRA value")
        if row.get("setup") is True:
            continue
        m = row.get("m")
        snr_db_x10 = row.get("snr_db_x10")
        if isinstance(m, bool) or not isinstance(m, int) or m not in CBRA_SUPPORTED_M:
            raise ValueError("row m is not a supported CBRA value")
        if isinstance(snr_db_x10, bool) or not isinstance(snr_db_x10, int):
            raise ValueError("snr_db_x10 must be an integer")
        key = (message_kind, m, snr_db_x10)
        group = groups.setdefault(key, {"rows": [], "invalid_reasons": set()})
        group["rows"].append(row)

        for name in ("signal_power_q16", "noise_power_q16"):
            value = row.get(name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                group["invalid_reasons"].add("missing_power_calibration")
        if row.get("calibrated_snr_db_x10") is None:
            group["invalid_reasons"].add("missing_power_calibration")

        attempt_index = row.get("attempt_index")
        if isinstance(attempt_index, bool) or not isinstance(attempt_index, int) or not 0 <= attempt_index < packet_budget:
            raise ValueError("attempt_index is outside the fixed budget")
        channel_epoch = row.get("channel_epoch")
        if isinstance(channel_epoch, bool) or not isinstance(channel_epoch, int) or channel_epoch <= 0:
            group["invalid_reasons"].add("missing_channel_epoch")
        if row.get("epoch_ack") is not True or row.get("channel_readback") is not True:
            group["invalid_reasons"].add("missing_channel_readback")
        mac_bits, phy_bits, _message_name = _cbra_message_bits(message_kind)
        if row.get("mac_bits") != mac_bits or row.get("phy_bits") != phy_bits:
            group["invalid_reasons"].add("message_bit_length_mismatch")
        for name in ("compared_bits", "erroneous_bits", "r2d_on_air_duration_ns"):
            value = row.get(name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if row["compared_bits"] > mac_bits or row["erroneous_bits"] > row["compared_bits"]:
            raise ValueError("CBRA bit counters exceed the message MAC bit length")
        if row["r2d_on_air_duration_ns"] <= 0:
            raise ValueError("r2d_on_air_duration_ns must be positive")
        for name in ("crc_ok", "payload_match", "d2r_attempted", "context_eligible", "setup"):
            if not isinstance(row.get(name), bool):
                raise ValueError(f"{name} must be boolean")
        if row["d2r_attempted"]:
            group["invalid_reasons"].add("unexpected_d2r_attempt")

    if not groups:
        raise ValueError("CBRA campaign has no measured attempts after setup exclusion")

    snr_grid_by_kind: dict[int, dict[int, set[int]]] = {}
    for message_kind, m, snr_db_x10 in groups:
        snr_grid_by_kind.setdefault(message_kind, {}).setdefault(m, set()).add(snr_db_x10)
    for grids_by_m in snr_grid_by_kind.values():
        grids = list(grids_by_m.values())
        if grids and any(grid != grids[0] for grid in grids[1:]):
            raise ValueError("CBRA M values must share one common SNR grid per message kind")

    points = []
    for (message_kind, m, snr_db_x10), group in sorted(groups.items()):
        point_rows = sorted(group["rows"], key=lambda row: row["attempt_index"])
        indices = [row["attempt_index"] for row in point_rows]
        if len(point_rows) != packet_budget or indices != list(range(packet_budget)):
            raise ValueError(
                f"CBRA point {(message_kind, m, snr_db_x10)} must contain exactly 10000 unique attempts"
            )
        epochs = [row.get("channel_epoch") for row in point_rows if isinstance(row.get("channel_epoch"), int)]
        if epochs and any(current < previous for previous, current in zip(epochs, epochs[1:])):
            group["invalid_reasons"].add("non_monotonic_channel_epoch")

        attempted = len(point_rows)
        calibrated_snr_values = [
            row["calibrated_snr_db_x10"]
            for row in point_rows
            if isinstance(row.get("calibrated_snr_db_x10"), int)
        ]
        calibrated_snr_db_x10_mean = (
            sum(calibrated_snr_values) // attempted if len(calibrated_snr_values) == attempted else None
        )
        if calibrated_snr_db_x10_mean is None:
            group["invalid_reasons"].add("missing_power_calibration")
        elif abs(calibrated_snr_db_x10_mean - snr_db_x10) > CBRA_SNR_POINT_TOLERANCE_DB_X10:
            group["invalid_reasons"].add("calibration_outside_point_tolerance")
        compared_bits = sum(row["compared_bits"] for row in point_rows)
        erroneous_bits = sum(row["erroneous_bits"] for row in point_rows)
        crc_failures = sum(not row["crc_ok"] for row in point_rows)
        correctly_delivered = sum(row["crc_ok"] and row["payload_match"] for row in point_rows)
        payload_block_errors = attempted - correctly_delivered
        d2r_attempts = sum(row["d2r_attempted"] for row in point_rows)
        full_airtime_ns = sum(row["r2d_on_air_duration_ns"] for row in point_rows)
        signal_power_q16 = sum(row.get("signal_power_q16", 0) for row in point_rows) // attempted
        noise_power_q16 = sum(row.get("noise_power_q16", 0) for row in point_rows) // attempted
        invalid_reasons = sorted(group["invalid_reasons"])
        valid = not invalid_reasons
        points.append(
            {
                "message_kind": message_kind,
                "m": m,
                "prb_count": CBRA_PRB_COUNT,
                "snr_db_x10": snr_db_x10,
                "frame": cbra_frame_components(m=m, message_kind=message_kind),
                "attempted_packets": attempted,
                "compared_bits": compared_bits,
                "erroneous_bits": erroneous_bits,
                "crc_failures": crc_failures,
                "payload_block_errors": payload_block_errors,
                "d2r_attempts": d2r_attempts,
                "d2r_gate_refusals": attempted - d2r_attempts,
                "full_r2d_airtime_ns": full_airtime_ns,
                "signal_power_q16_mean": signal_power_q16,
                "noise_power_q16_mean": noise_power_q16,
                "calibrated_snr_db_x10_mean": calibrated_snr_db_x10_mean,
                "payload_ber": None if compared_bits == 0 or not valid else erroneous_bits / compared_bits,
                "payload_bler": None if compared_bits == 0 or not valid else payload_block_errors / attempted,
                "payload_bler_ci95": None if compared_bits == 0 or not valid else _wilson_interval(payload_block_errors, attempted),
                "goodput_bps": (
                    None
                    if full_airtime_ns == 0 or not valid
                    else cbra_frame_components(m=m, message_kind=message_kind)["mac_bits"]
                    * correctly_delivered
                    / (full_airtime_ns / 1_000_000_000)
                ),
                "valid": valid,
                "invalid_reasons": invalid_reasons,
            }
        )
    return {
        "schema_version": 3,
        "campaign": {
            "profile": "cbra_r2d_m_snr",
            "packet_budget": CBRA_FORMAL_PACKET_BUDGET,
            "message_kinds": [CBRA_PAGING_KIND, CBRA_ACCESS_TRIGGER_KIND],
            "scs_khz": 15,
            "prb_count": CBRA_PRB_COUNT,
            "receiver_reference_plane": "Tag preselection output before square-law; Manchester low/high pair separation",
            "snr_grid_definition": "pilot-derived point center in 0.1 dB units; point mean calibrated SNR must be within +/-1 dB",
            "goodput_definition": "message_mac_bits * correctly_delivered_blocks / full_R2D_airtime_seconds",
            "fixed_stop": True,
        },
        "points": points,
    }


def generate_visibility_map(*, tag_count: int, reader_ids: tuple[int, int, int], seed: int) -> dict[int, int | None]:
    """Draw the accepted equal-probability Reader-or-unseen scenario mapping."""
    if tag_count < 0 or tag_count > AIOT_T2_MAX_TAGS:
        raise ValueError(f"tag_count must be between 0 and {AIOT_T2_MAX_TAGS}")
    if len(set(reader_ids)) != 3 or any(reader_id <= 0 for reader_id in reader_ids):
        raise ValueError("reader_ids must contain three distinct positive values")

    generator = Random(seed)
    choices: tuple[int | None, ...] = (None,) + reader_ids
    return {tag_id: generator.choice(choices) for tag_id in range(1, tag_count + 1)}


def validate_visibility_map(
    mapping: dict[int, int | None], *, tag_count: int, reader_ids: tuple[int, int, int]
) -> None:
    """Validate the persisted one-Reader-or-unseen topology boundary."""
    if tag_count < 0 or tag_count > AIOT_T2_MAX_TAGS:
        raise ValueError(f"tag_count must be between 0 and {AIOT_T2_MAX_TAGS}")
    if set(mapping) != set(range(1, tag_count + 1)):
        raise ValueError("visibility map must contain every Tag exactly once")
    if len(set(reader_ids)) != 3 or any(reader_id <= 0 for reader_id in reader_ids):
        raise ValueError("reader_ids must contain three distinct positive values")
    allowed = {None, *reader_ids}
    if any(reader not in allowed for reader in mapping.values()):
        raise ValueError("visibility map contains an unknown Reader")
    visible = [tag for tag, reader in mapping.items() if reader is not None]
    if len(visible) > AIOT_T2_MAX_TAGS or len(visible) != len(set(visible)):
        raise ValueError("visible Tag identities must be pairwise disjoint")


def reader_visible_tags(mapping: dict[int, int | None], reader_ids: tuple[int, int, int]) -> dict[int, list[int]]:
    validate_visibility_map(mapping, tag_count=len(mapping), reader_ids=reader_ids)
    return {reader: [tag for tag, owner in mapping.items() if owner == reader] for reader in reader_ids}


def _rician(rng: Random, k_db: float) -> complex:
    k = 10.0 ** (k_db / 10.0)
    los = math.sqrt(k / (k + 1.0))
    diffuse = math.sqrt(1.0 / (2.0 * (k + 1.0)))
    return complex(los + diffuse * rng.gauss(0.0, 1.0), diffuse * rng.gauss(0.0, 1.0))


class PairedRicianChannelBank:
    """Deterministic pair of independent unit-power Rician legs per physical key."""

    def __init__(self, seed: int, k_db: float = 3.0):
        self.seed = seed
        self.k_db = k_db
        self._cache: dict[tuple[int, str, int, int], complex] = {}

    def coefficient(self, *, repeat: int, link: str, tag_id: int, cycle: int) -> complex:
        key = (repeat, link, tag_id, cycle)
        if key not in self._cache:
            material = f"{self.seed}:{repeat}:{link}:{tag_id}:{cycle}".encode()
            derived = int.from_bytes(hashlib.blake2b(material, digest_size=8).digest(), "big")
            rng = Random(derived)
            self._cache[key] = _rician(rng, self.k_db)
        return self._cache[key]

    def cascaded(self, *, repeat: int, tag_id: int, cycle: int) -> complex:
        return self.coefficient(repeat=repeat, link="gnb-tag", tag_id=tag_id, cycle=cycle) * self.coefficient(
            repeat=repeat, link="tag-reader", tag_id=tag_id, cycle=cycle
        )

    def provenance(self, *, repeat: int, reader_id: int, tag_id: int, cycle: int) -> int:
        material = f"{self.seed}:{repeat}:{reader_id}:{tag_id}:{cycle}:{self.k_db}".encode()
        return int.from_bytes(hashlib.blake2b(material, digest_size=8).digest(), "big")


def estimate_rician_energy_ber(
    *,
    duration_multiplier: float,
    bits: int = 20000,
    seed: int = 1,
    k_db: float = 3.0,
    noise_power: float = 0.1,
) -> dict:
    """Numerical ON/OFF energy reference; it is not a runtime RFsim result."""
    if duration_multiplier <= 0 or bits <= 0 or noise_power < 0:
        raise ValueError("duration_multiplier and bits must be positive; noise_power must be non-negative")
    samples_per_chip = max(1, round(duration_multiplier * 8))
    bank = PairedRicianChannelBank(seed, k_db)
    rng = Random(seed + 0xA10)
    errors = 0
    compared = 0
    ties = 0
    noise_sd = math.sqrt(noise_power / 2.0)
    for bit_index in range(bits):
        bit = rng.randrange(2)
        channel = bank.cascaded(repeat=0, tag_id=1, cycle=bit_index)
        energies = []
        for on in (bit == 0, bit == 1):
            energy = 0.0
            for _ in range(samples_per_chip):
                sample = (channel if on else 0j) + complex(rng.gauss(0.0, noise_sd), rng.gauss(0.0, noise_sd))
                energy += (sample.real * sample.real + sample.imag * sample.imag)
            energies.append(energy)
        if energies[0] == energies[1]:
            ties += 1
            continue
        decoded = 0 if energies[0] > energies[1] else 1
        compared += 1
        errors += decoded != bit
    return {
        "reference_kind": "numerical_cascaded_rician_energy_detector",
        "seed": seed,
        "duration_multiplier": duration_multiplier,
        "duration_ns": duration_multiplier * BASE_BIT_DURATION_US * 1_000.0,
        "samples_per_chip": samples_per_chip,
        "k_db_per_leg": k_db,
        "noise_power": noise_power,
        "compared_bits": compared,
        "erroneous_bits": errors,
        "tie_count": ties,
        "ber": None if compared == 0 else errors / compared,
    }


class D2RReservationScheduler:
    """Reserve half-open D2R intervals independently for each Reader."""

    def __init__(self):
        self._intervals: dict[int, list[tuple[int, int]]] = {}

    def reserve(self, *, reader_id: int, start_ns: int, end_ns: int) -> D2RReservation:
        if reader_id <= 0:
            raise ValueError("reader_id must be positive")
        if start_ns < 0 or end_ns <= start_ns:
            raise ValueError("interval must have non-negative start and positive duration")

        intervals = self._intervals.setdefault(reader_id, [])
        if any(start_ns < reserved_end and reserved_start < end_ns for reserved_start, reserved_end in intervals):
            return D2RReservation(admitted=False, reason="same_reader_overlap")

        intervals.append((start_ns, end_ns))
        return D2RReservation(admitted=True, reason=None)
