#!/usr/bin/env python3

"""Fail-closed UDS bridge; live KPM/control handlers are added behind explicit gates."""

import argparse
import json
import os
from pathlib import Path
import re
import secrets
import socket


PROTOCOL_VERSION = 1
KPM_RAN_FUNCTION_ID = 2
RC_RAN_FUNCTION_ID = 3


class NativeFlexric:
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.sdk = None
        self.initialized = False

    def load(self):
        if self.sdk is None:
            import xapp_sdk  # type: ignore

            self.sdk = xapp_sdk
        return self.sdk

    def discover(self) -> dict:
        if not self.config_file.is_file():
            raise RuntimeError("FLEXRIC_CONFIG_MISSING")
        sdk = self.load()
        if not hasattr(sdk, "init_with_config"):
            raise RuntimeError("NATIVE_INIT_API_UNAVAILABLE")
        if not self.initialized:
            if not sdk.init_with_config(str(self.config_file)):
                raise RuntimeError("NATIVE_INIT_FAILED")
            self.initialized = True
        nodes = []
        for node in sdk.conn_e2_nodes():
            if all(hasattr(node, field) for field in ("ran_type", "mcc", "mnc", "node_id")):
                key = f"{int(node.ran_type)}:{int(node.mcc)}:{int(node.mnc)}:{int(node.node_id)}"
            else:
                node_id = node.id
                key = (
                    f"{int(node_id.type)}:{int(node_id.plmn.mcc)}:{int(node_id.plmn.mnc)}:"
                    f"{int(node_id.nb_id.nb_id)}"
                )
            ran_functions = (
                sorted(int(function_id) for function_id in node.ran_function_ids)
                if hasattr(node, "ran_function_ids")
                else sorted(int(function.id) for function in node.ran_func)
            )
            kpm_styles = (
                [
                    {
                        "style_type": int(style.style_type),
                        "action_definition_format": int(style.action_definition_format),
                        "indication_header_format": int(style.indication_header_format),
                        "indication_message_format": int(style.indication_message_format),
                    }
                    for style in node.kpm_report_styles
                ]
                if hasattr(node, "kpm_report_styles")
                else "UNVERIFIED"
            )
            rc_styles = (
                [
                    {
                        "style_type": int(style.style_type),
                        "header_format": int(style.header_format),
                        "message_format": int(style.message_format),
                        "outcome_format": int(style.outcome_format),
                        "action_ids": [int(action_id) for action_id in style.action_ids],
                    }
                    for style in node.rc_control_styles
                ]
                if hasattr(node, "rc_control_styles")
                else "UNVERIFIED"
            )
            nodes.append(
                {
                    "node_id": key,
                    "ran_function_ids": ran_functions,
                    "kpm_advertised": KPM_RAN_FUNCTION_ID in ran_functions,
                    "rc_advertised": RC_RAN_FUNCTION_ID in ran_functions,
                    "kpm_styles": kpm_styles,
                    "rc_styles": rc_styles,
                }
            )
        return {"nodes": nodes, "eligible_node_count": sum(node["kpm_advertised"] and node["rc_advertised"] for node in nodes)}


class Bridge:
    def __init__(
        self,
        profile: str,
        native_control=None,
        native=None,
        qualified_binding=None,
        lease_dir: Path = Path("/run/redcap-drl/leases"),
        workspace_id: str = "workspace",
        journal_path: Path = Path("/run/redcap-drl/control_journal.json"),
    ):
        self.profile = profile
        self.native_control = native_control
        self.native = native
        self.verified_target_binding = qualified_binding
        self.lease_dir = lease_dir
        self.workspace_id = workspace_id
        self.journal_path = journal_path
        self.sessions = {}

    def recovery_required(self) -> bool:
        if not self.journal_path.exists():
            return False
        try:
            state = json.loads(self.journal_path.read_text(encoding="utf-8")).get("state")
        except (OSError, json.JSONDecodeError):
            return True
        return state not in {"IDLE", "COMPLETED", "RECOVERED"}

    def lease_path(self) -> Path:
        node_id = str(self.verified_target_binding["node_id"])
        if not re.fullmatch(r"[A-Za-z0-9_.:-]+", node_id):
            raise ValueError("invalid node_id")
        return self.lease_dir / f"{node_id}.lock"

    def open(self, request: dict) -> dict:
        mode = request.get("mode")
        if mode not in {"observation-only", "control-once"}:
            return {"ok": False, "error": "INVALID_MODE", "request_id": request["request_id"]}
        if mode == "control-once":
            if self.profile == "none":
                return {"ok": False, "error": "PROFILE_FORBIDS_CONTROL", "request_id": request["request_id"]}
            if self.verified_target_binding is None:
                return {"ok": False, "error": "TARGET_BINDING_REQUIRED", "request_id": request["request_id"]}
            if self.recovery_required():
                return {"ok": False, "error": "RECOVERY_REQUIRED", "request_id": request["request_id"]}
            self.lease_dir.mkdir(parents=True, exist_ok=True)
            try:
                descriptor = os.open(self.lease_path(), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                return {"ok": False, "error": "TARGET_BUSY", "request_id": request["request_id"]}
            with os.fdopen(descriptor, "w", encoding="utf-8") as lease:
                lease.write(self.workspace_id + "\n")
        session_id = secrets.token_hex(16)
        self.sessions[session_id] = {"mode": mode, "acted": False}
        return {"ok": True, "request_id": request["request_id"], "session_id": session_id, "profile_id": self.profile}

    def handle(self, request: dict) -> dict:
        result = self._handle(request)
        result.setdefault("protocol_version", PROTOCOL_VERSION)
        result.setdefault("profile_id", self.profile)
        return result

    def _handle(self, request: dict) -> dict:
        required = {"protocol_version", "request_id", "operation"}
        missing = sorted(required - request.keys())
        if missing:
            return {"ok": False, "error": "INVALID_REQUEST", "missing": missing}
        if request["protocol_version"] != PROTOCOL_VERSION:
            return {"ok": False, "error": "UNSUPPORTED_PROTOCOL_VERSION", "request_id": request["request_id"]}
        if request.get("profile_id", self.profile) != self.profile:
            return {"ok": False, "error": "PROFILE_MISMATCH", "request_id": request["request_id"]}
        if request["operation"] == "health":
            try:
                sdk = self.native.load() if self.native is not None else __import__("xapp_sdk")
            except ImportError as error:
                return {"ok": False, "error": "NATIVE_EXTENSION_UNAVAILABLE", "detail": str(error), "request_id": request["request_id"]}
            return {"ok": True, "native_extension": sdk.__name__, "request_id": request["request_id"]}
        if request["operation"] == "discover":
            if self.native is None:
                return {"ok": False, "error": "NATIVE_DISCOVERY_UNAVAILABLE", "request_id": request["request_id"]}
            try:
                capabilities = self.native.discover()
            except (ImportError, RuntimeError) as error:
                return {"ok": False, "error": str(error), "request_id": request["request_id"]}
            return {"ok": True, "request_id": request["request_id"], "capabilities": capabilities, "control_attempted": False}
        if request["operation"] == "qualify":
            return {
                "ok": False,
                "error": "KPM_STREAM_BINDING_UNIMPLEMENTED",
                "needs_verification": "Live E2SM-KPM cell/UE styles and UE-to-RC identity mapping",
                "request_id": request["request_id"],
            }
        if request["operation"] == "observe":
            return {"ok": False, "error": "KPM_NOT_QUALIFIED", "request_id": request["request_id"]}
        if request["operation"] == "open":
            return self.open(request)
        if request["operation"] == "close":
            session_id = request.get("session_id")
            session = self.sessions.pop(session_id, None)
            if session is None:
                return {"ok": False, "error": "INVALID_SESSION", "request_id": request["request_id"]}
            if session["mode"] == "control-once" and self.verified_target_binding is not None:
                lease_path = self.lease_path()
                try:
                    if lease_path.read_text(encoding="utf-8") == self.workspace_id + "\n":
                        lease_path.unlink()
                except FileNotFoundError:
                    pass
            return {"ok": True, "request_id": request["request_id"], "session_id": session_id}
        if request["operation"] == "act" and self.profile == "none":
            return {"ok": False, "error": "PROFILE_FORBIDS_CONTROL", "request_id": request["request_id"]}
        if request["operation"] == "act" and self.verified_target_binding is None:
            return {"ok": False, "error": "TARGET_BINDING_REQUIRED", "request_id": request["request_id"]}
        if request["operation"] == "act":
            session = self.sessions.get(request.get("session_id"))
            if session is None or session["mode"] != "control-once":
                return {"ok": False, "error": "INVALID_SESSION", "request_id": request["request_id"]}
            if session["acted"]:
                return {"ok": False, "error": "CONTROL_ONCE_EXHAUSTED", "request_id": request["request_id"]}
            return {"ok": False, "error": "APPLY_PROOF_PROVIDER_REQUIRED", "request_id": request["request_id"]}
        return {"ok": False, "error": "OPERATION_NOT_READY", "request_id": request["request_id"]}


def serve(socket_path: Path, profile: str, flexric_config: Path, workspace_id: str) -> None:
    bridge = Bridge(profile, native=NativeFlexric(flexric_config), workspace_id=workspace_id)
    socket_path.parent.mkdir(parents=True, exist_ok=True)
    socket_path.unlink(missing_ok=True)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        server.bind(str(socket_path))
        socket_path.chmod(0o660)
        server.listen()
        while True:
            connection, _ = server.accept()
            with connection:
                raw = connection.recv(1024 * 1024)
                try:
                    request = json.loads(raw)
                    result = bridge.handle(request)
                except (json.JSONDecodeError, UnicodeDecodeError) as error:
                    result = {"ok": False, "error": "INVALID_JSON", "detail": str(error)}
                connection.sendall(json.dumps(result).encode("utf-8") + b"\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket", type=Path, required=True)
    parser.add_argument("--profile", choices=("none", "ul-prb-cap-v1"), required=True)
    parser.add_argument("--flexric-config", type=Path, required=True)
    parser.add_argument("--workspace-id", required=True)
    args = parser.parse_args()
    serve(args.socket, args.profile, args.flexric_config, args.workspace_id)


if __name__ == "__main__":
    main()
