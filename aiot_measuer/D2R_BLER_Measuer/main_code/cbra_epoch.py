"""Small talanet-compatible controller for atomic CBRA RFsim channel epochs."""

from __future__ import annotations

import re
import socket
from typing import Callable


_EPOCH_RE = re.compile(
    r"AIOT_T2_CHANNEL_EPOCH\s+epoch=(?P<epoch>\d+)\s+"
    r"attenuation_db=(?P<attenuation>-?\d+(?:\.\d+)?)\s+"
    r"noise_power=(?P<noise>\d+(?:\.\d+)?)\s+seed=(?P<seed>\d+)\s+"
    r"(?:data_seed=(?P<data_seed>\d+)\s+)?"
    r"(?:noise_seed=(?P<noise_seed>\d+)\s+)?"
    r"readback=(?P<readback>\w+)(?:\s+queued=(?P<queued>\d+))?"
)


def parse_epoch_readback(response: str) -> dict:
    match = _EPOCH_RE.search(response)
    if match is None:
        raise ValueError("talanet response has no AIOT_T2_CHANNEL_EPOCH readback")
    values = match.groupdict()
    if values["readback"] not in {"ok", "config"}:
        raise ValueError("channel epoch readback is not acknowledged")
    data_seed = int(values["data_seed"] or values["seed"])
    noise_seed = int(values["noise_seed"] or values["seed"])
    return {
        "epoch": int(values["epoch"]),
        "attenuation_db": float(values["attenuation"]),
        "noise_power": float(values["noise"]),
        "seed": data_seed,
        "data_seed": data_seed,
        "noise_seed": noise_seed,
        "readback": values["readback"],
        "queued": None if values["queued"] is None else int(values["queued"]),
    }


class TalanetEpochController:
    """Issue `rfsimu aiot_epoch` commands and fail closed on weak evidence."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 9090,
        *,
        request: Callable[[str], str] | None = None,
        command_prefix: str = "rfsimu aiot_epoch",
        timeout: float = 2.0,
    ) -> None:
        if not host or port <= 0 or timeout <= 0:
            raise ValueError("host, port, and timeout must be valid")
        self._host = host
        self._port = port
        self._request = request or self._tcp_request
        self._command_prefix = command_prefix
        self._timeout = timeout
        self._last_epoch = 0

    def _tcp_request(self, command: str) -> str:
        chunks: list[bytes] = []
        with socket.create_connection((self._host, self._port), timeout=self._timeout) as connection:
            connection.settimeout(self._timeout)
            connection.sendall((command + "\n").encode("ascii"))
            while sum(map(len, chunks)) < 4096:
                try:
                    chunk = connection.recv(1024)
                except socket.timeout:
                    break
                if not chunk:
                    break
                chunks.append(chunk)
                if b"readback=" in chunk:
                    break
        return b"".join(chunks).decode("utf-8", errors="replace")

    def set_epoch(
        self,
        *,
        attenuation_db: float,
        noise_power: float,
        drained: bool,
        seed: int | None = None,
        data_seed: int | None = None,
        noise_seed: int | None = None,
    ) -> dict:
        if not drained:
            raise ValueError("R2D packets must be drained before changing channel state")
        if data_seed is None:
            data_seed = seed
        if data_seed is None:
            raise ValueError("data_seed or seed must be provided")
        if noise_seed is None:
            noise_seed = data_seed
        if data_seed <= 0 or noise_seed <= 0 or noise_power < 0:
            raise ValueError("seeds must be positive and noise_power must be non-negative")
        command = f"{self._command_prefix} set {attenuation_db} {noise_power} {data_seed}"
        if noise_seed != data_seed or seed is None:
            command += f" {noise_seed}"
        response = self._request(command)
        state = parse_epoch_readback(response)
        if state["readback"] != "ok" or state["epoch"] <= self._last_epoch:
            raise RuntimeError("channel epoch was not monotonically acknowledged")
        if state["queued"] != 0:
            raise RuntimeError("RFsim channel update was not applied after packet drain")
        if abs(state["attenuation_db"] - attenuation_db) > 1e-6 or abs(state["noise_power"] - noise_power) > 1e-6:
            raise RuntimeError("RFsim readback differs from requested channel state")
        if state["data_seed"] != data_seed or state["noise_seed"] != noise_seed:
            raise RuntimeError("RFsim readback differs from requested seed group")
        self._last_epoch = state["epoch"]
        return state

    def show(self) -> dict:
        state = parse_epoch_readback(self._request(f"{self._command_prefix} show"))
        if state["epoch"] < self._last_epoch:
            raise RuntimeError("RFsim channel epoch moved backwards")
        self._last_epoch = state["epoch"]
        return state


class CbraAttemptEpochBinder:
    """Assign one acknowledged RFsim epoch to each attempted R2D packet."""

    def __init__(self) -> None:
        self._attempts: dict[int, dict] = {}

    def bind(self, *, attempt_index: int, epoch_state: dict) -> dict:
        if isinstance(attempt_index, bool) or attempt_index < 0:
            raise ValueError("attempt_index must be non-negative")
        if attempt_index in self._attempts:
            raise ValueError("attempt already has a channel epoch")
        if (
            epoch_state.get("readback") != "ok"
            or epoch_state.get("queued") != 0
            or not isinstance(epoch_state.get("epoch"), int)
            or epoch_state["epoch"] <= 0
        ):
            raise RuntimeError("attempt requires an acknowledged drained epoch")
        binding = {
            "attempt_index": attempt_index,
            "channel_epoch": epoch_state["epoch"],
            "epoch_ack": True,
            "channel_readback": True,
            "attenuation_db": epoch_state["attenuation_db"],
            "noise_power": epoch_state["noise_power"],
            "data_seed": epoch_state.get("data_seed", epoch_state["seed"]),
            "noise_seed": epoch_state.get("noise_seed", epoch_state["seed"]),
        }
        self._attempts[attempt_index] = binding
        return dict(binding)

    def get(self, attempt_index: int) -> dict:
        try:
            return dict(self._attempts[attempt_index])
        except KeyError as error:
            raise KeyError("attempt has no channel epoch binding") from error


def deterministic_channel_provenance(
    *, seed: int, tag_id: int, reader_handle: int, epoch: int, timestamp: int, tbit: int
) -> int:
    """Mirror RFsim's splitmix64 provenance derivation for replay checks."""
    mask = (1 << 64) - 1
    value = (seed ^ (tag_id << 32) ^ (reader_handle << 16) ^ ((epoch & 0xFFFF) << 8) ^ tbit ^ timestamp) & mask
    value ^= value >> 30
    value = (value * 0xBF58476D1CE4E5B9) & mask
    value ^= value >> 27
    value = (value * 0x94D049BB133111EB) & mask
    return (value ^ (value >> 31)) & mask
