"""Small talanet-compatible controller for atomic CFA RFsim channel epochs."""

from __future__ import annotations

import re
import socket
from typing import Callable


_EPOCH_RE = re.compile(
    r"AIOT_T2_CHANNEL_EPOCH\s+epoch=(?P<epoch>\d+)\s+"
    r"attenuation_db=(?P<attenuation>-?\d+(?:\.\d+)?)\s+"
    r"noise_power=(?P<noise>\d+(?:\.\d+)?)\s+seed=(?P<seed>\d+)\s+"
    r"readback=(?P<readback>\w+)(?:\s+queued=(?P<queued>\d+))?"
)


def parse_epoch_readback(response: str) -> dict:
    match = _EPOCH_RE.search(response)
    if match is None:
        raise ValueError("talanet response has no AIOT_T2_CHANNEL_EPOCH readback")
    values = match.groupdict()
    if values["readback"] not in {"ok", "config"}:
        raise ValueError("channel epoch readback is not acknowledged")
    return {
        "epoch": int(values["epoch"]),
        "attenuation_db": float(values["attenuation"]),
        "noise_power": float(values["noise"]),
        "seed": int(values["seed"]),
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

    def set_epoch(self, *, attenuation_db: float, noise_power: float, seed: int, drained: bool) -> dict:
        if not drained:
            raise ValueError("R2D packets must be drained before changing channel state")
        if seed <= 0 or noise_power < 0:
            raise ValueError("seed must be positive and noise_power must be non-negative")
        response = self._request(f"{self._command_prefix} set {attenuation_db} {noise_power} {seed}")
        state = parse_epoch_readback(response)
        if state["readback"] != "ok" or state["epoch"] <= self._last_epoch:
            raise RuntimeError("channel epoch was not monotonically acknowledged")
        if state["queued"] != 0:
            raise RuntimeError("RFsim channel update was not applied after packet drain")
        if abs(state["attenuation_db"] - attenuation_db) > 1e-6 or abs(state["noise_power"] - noise_power) > 1e-6:
            raise RuntimeError("RFsim readback differs from requested channel state")
        if state["seed"] != seed:
            raise RuntimeError("RFsim readback differs from requested seed")
        self._last_epoch = state["epoch"]
        return state

    def show(self) -> dict:
        state = parse_epoch_readback(self._request(f"{self._command_prefix} show"))
        if state["epoch"] < self._last_epoch:
            raise RuntimeError("RFsim channel epoch moved backwards")
        self._last_epoch = state["epoch"]
        return state
