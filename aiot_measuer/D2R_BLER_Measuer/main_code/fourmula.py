"""D2R BER measurement primitives.

The module name follows the user-requested project layout.  It is a simulator
measurement interface and does not claim a real Reader BER estimator.
"""

from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class ReaderBerObservation:
    """One closed 0.5 ms-equivalent Reader observation window."""

    reader_id: int
    window_index: int
    window_start_ns: int
    window_end_ns: int
    available_at_ns: int
    completed_packets: int
    compared_bits: int
    erroneous_bits: int
    ber: float | None
    valid: bool
    invalid_evidence_count: int
    invalid_reasons: tuple[str, ...]


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
        self._counts: dict[tuple[int, int], list[int]] = {}
        self._invalid_evidence: dict[tuple[int, int], list[str]] = {}

    def record_completed_packet(
        self,
        *,
        reader_id: int,
        completion_ns: int,
        transmitted_bits: tuple[int, ...],
        decoded_bits: tuple[int, ...],
    ) -> None:
        if reader_id <= 0:
            raise ValueError("reader_id must be positive")
        if completion_ns < 0:
            raise ValueError("completion_ns must be non-negative")
        if len(transmitted_bits) != len(decoded_bits):
            raise ValueError("transmitted_bits and decoded_bits must have equal length")
        if any(bit not in (0, 1) for bit in transmitted_bits + decoded_bits):
            raise ValueError("bit sequences must contain only 0 or 1")

        window_index = completion_ns // self._window_ns
        counts = self._counts.setdefault((reader_id, window_index), [0, 0, 0])
        counts[0] += len(transmitted_bits)
        counts[1] += sum(tx != rx for tx, rx in zip(transmitted_bits, decoded_bits))
        counts[2] += 1

    def record_missing_evidence(self, *, reader_id: int, completion_ns: int, reason: str) -> None:
        """Preserve missing runtime evidence instead of treating it as success."""
        if reader_id <= 0:
            raise ValueError("reader_id must be positive")
        if completion_ns < 0:
            raise ValueError("completion_ns must be non-negative")
        if not reason:
            raise ValueError("reason must not be empty")

        window_index = completion_ns // self._window_ns
        self._invalid_evidence.setdefault((reader_id, window_index), []).append(reason)

    def closed_observation(self, *, reader_id: int, window_index: int) -> ReaderBerObservation:
        if reader_id <= 0:
            raise ValueError("reader_id must be positive")
        if window_index < 0:
            raise ValueError("window_index must be non-negative")

        compared_bits, erroneous_bits, completed_packets = self._counts.get((reader_id, window_index), [0, 0, 0])
        invalid_reasons = tuple(self._invalid_evidence.get((reader_id, window_index), []))
        window_start_ns = window_index * self._window_ns
        window_end_ns = window_start_ns + self._window_ns
        return ReaderBerObservation(
            reader_id=reader_id,
            window_index=window_index,
            window_start_ns=window_start_ns,
            window_end_ns=window_end_ns,
            available_at_ns=window_end_ns,
            completed_packets=completed_packets,
            compared_bits=compared_bits,
            erroneous_bits=erroneous_bits,
            ber=None if compared_bits == 0 or invalid_reasons else erroneous_bits / compared_bits,
            valid=not invalid_reasons,
            invalid_evidence_count=len(invalid_reasons),
            invalid_reasons=invalid_reasons,
        )


def generate_visibility_map(*, tag_count: int, reader_ids: tuple[int, int, int], seed: int) -> dict[int, int | None]:
    """Draw the accepted equal-probability Reader-or-unseen scenario mapping."""
    if tag_count < 0:
        raise ValueError("tag_count must be non-negative")
    if len(set(reader_ids)) != 3 or any(reader_id <= 0 for reader_id in reader_ids):
        raise ValueError("reader_ids must contain three distinct positive values")

    generator = Random(seed)
    choices: tuple[int | None, ...] = (None,) + reader_ids
    return {tag_id: generator.choice(choices) for tag_id in range(1, tag_count + 1)}


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
