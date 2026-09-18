"""D2R BER measurement primitives.

The module name follows the user-requested project layout.  It is a simulator
measurement interface and does not claim a real Reader BER estimator.
"""

from dataclasses import asdict, dataclass
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
OBSERVATION_STRUCT = struct.Struct("!IBBHIIQQB3sHH16s16sQ")
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
    channel_keys: dict[tuple[int, int], dict[int, object]] = {}
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
        if "channel_key" in row:
            pair_key = (repeat, cycle)
            duration_keys = channel_keys.setdefault(pair_key, {})
            duration_keys[duration_index] = row["channel_key"]

    missing = sorted(expected - seen)
    if missing:
        raise ValueError(f"campaign manifest is missing {len(missing)} fixed-budget variants")
    for pair_key, duration_keys in channel_keys.items():
        if len(duration_keys) == len(duration_multipliers) and len(set(duration_keys.values())) != 1:
            raise ValueError(f"channel_key is not paired across durations for {pair_key}")

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
            "pairing_key": "repeat,cycle,physical_link,tag_id",
        },
        "duration_results": duration_results,
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
