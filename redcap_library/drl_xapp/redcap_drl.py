"""Stable Python client for the workspace-private RedCap DRL bridge."""

from __future__ import annotations

import json
from pathlib import Path
import socket
import uuid


class BridgeError(RuntimeError):
    pass


class Client:
    def __init__(self, socket_path: str | Path = "/run/redcap-drl/bridge.sock"):
        self.socket_path = Path(socket_path)

    def request(self, operation: str, **payload):
        request_id = uuid.uuid4().hex
        request = {"protocol_version": 1, "request_id": request_id, "operation": operation, **payload}
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(str(self.socket_path))
            client.sendall(json.dumps(request).encode("utf-8"))
            response = json.loads(client.recv(1024 * 1024))
        if response.get("request_id") not in {None, request_id}:
            raise BridgeError("bridge request_id mismatch")
        if response.get("ok") is not True:
            raise BridgeError(response.get("error", "bridge request failed"))
        return response

    def health(self):
        return self.request("health")

    def open(self, profile_id: str, mode: str):
        return self.request("open", profile_id=profile_id, mode=mode)

    def observe(self, session_id: str, after_seq: int, timeout: float):
        return self.request("observe", session_id=session_id, after_seq=after_seq, timeout=timeout)

    def act(self, session_id: str, profile_id: str, action: dict):
        return self.request("act", session_id=session_id, profile_id=profile_id, action=action)

    def close(self, session_id: str):
        return self.request("close", session_id=session_id)
