#!/usr/bin/env python3

"""Fail-closed UDS bridge; live KPM/control handlers are added behind explicit gates."""

import argparse
import json
import os
from pathlib import Path
import re
import secrets
import socket
import tempfile
import threading
import time


PROTOCOL_VERSION = 1
KPM_RAN_FUNCTION_ID = 2
RC_RAN_FUNCTION_ID = 3
KPM_OBSERVATION_TIMEOUT_SECONDS = 2.0


def validate_workspace_lock(path: Path, profile: str, workspace_id: str) -> None:
    try:
        lock = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("WORKSPACE_LOCK_INVALID") from error
    if (
        not isinstance(lock, dict)
        or lock.get("schema_version") != 1
        or lock.get("name") != workspace_id
        or lock.get("profile") != profile
    ):
        raise ValueError("WORKSPACE_LOCK_MISMATCH")
    if profile == "ul-prb-cap-v1":
        measurement_post = lock.get("measurement_post")
        if not isinstance(measurement_post, dict) or measurement_post.get("status") != "UNFROZEN":
            raise ValueError("MEASUREMENT_POST_POLICY_UNSUPPORTED")


class NativeFlexric:
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.sdk = None
        self.initialized = False
        self.kpm_subscriptions = {}
        self.kpm_callbacks = {}

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

    def qualify(self, profile: str) -> dict:
        if profile != "ul-prb-cap-v1":
            return {"ok": False, "error": "PROFILE_FORBIDS_LIVE_KPM", "control_attempted": False}
        capabilities = self.discover()
        eligible = [node for node in capabilities["nodes"] if node["kpm_advertised"] and node["rc_advertised"]]
        if len(eligible) != 1:
            return {
                "ok": False,
                "error": "EXACTLY_ONE_ELIGIBLE_NODE_REQUIRED",
                "eligible_node_count": len(eligible),
                "control_attempted": False,
            }
        node = eligible[0]
        styles = node["kpm_styles"]
        if not isinstance(styles, list):
            return {"ok": False, "error": "KPM_STYLE_UNVERIFIED", "node_id": node["node_id"], "control_attempted": False}
        has_cell = any(style["action_definition_format"] == 0 and style["indication_message_format"] == 0 for style in styles)
        has_ue = any(style["action_definition_format"] == 3 and style["indication_message_format"] == 2 for style in styles)
        if not has_cell:
            return {
                "ok": False,
                "error": "CELL_KPM_STREAM_REQUIRED",
                "failed_stage": "capability",
                "node_id": node["node_id"],
                "available_kpm_styles": styles,
                "cell": [],
                "ue": [],
                "control_attempted": False,
            }
        if not has_ue:
            return {
                "ok": False,
                "error": "UE_KPM_STREAM_REQUIRED",
                "failed_stage": "capability",
                "node_id": node["node_id"],
                "available_kpm_styles": styles,
                "cell": [],
                "ue": [],
                "control_attempted": False,
            }
        sdk = self.load()
        if not hasattr(sdk, "subscribe_kpm"):
            return {
                "ok": False,
                "error": "KPM_SUBSCRIPTION_PROVIDER_REQUIRED",
                "failed_stage": "subscription",
                "node_id": node["node_id"],
                "cell": [],
                "ue": [],
                "control_attempted": False,
            }

        for handle in self.kpm_subscriptions.values():
            if hasattr(sdk, "unsubscribe_kpm"):
                try:
                    sdk.unsubscribe_kpm(handle)
                except (RuntimeError, TypeError):
                    pass
        self.kpm_subscriptions = {}
        self.kpm_callbacks = {}
        samples = {"cell": [], "ue": []}
        callback_error = []
        observation_ready = threading.Event()

        def collect(stream, sample):
            try:
                if isinstance(sample, dict):
                    projected = dict(sample)
                    projected["source_seq"] = int(projected["source_seq"])
                    projected["timestamp_ms"] = int(projected["timestamp_ms"])
                    projected["measurements"] = dict(projected["measurements"])
                    if stream == "ue":
                        projected["kpm_ue_key"] = str(projected["kpm_ue_key"])
                else:
                    projected = {
                        "source_seq": int(sample.source_seq),
                        "timestamp_ms": int(sample.timestamp_ms),
                        "measurements": {
                            str(item.name): (float(item.value) if item.has_value else None)
                            for item in sample.measurements
                        },
                    }
                    if stream == "ue":
                        projected["kpm_ue_key"] = str(sample.kpm_ue_key)
                    for field in ("rc_ue_id", "rnti"):
                        if hasattr(sample, field):
                            projected[field] = int(getattr(sample, field))
                    if hasattr(sample, "source_seq_origin"):
                        projected["source_seq_origin"] = str(sample.source_seq_origin)
                projected["bridge_monotonic_receipt_ms"] = time.monotonic_ns() // 1_000_000
                samples[stream].append(projected)
                if samples["cell"] and samples["ue"]:
                    observation_ready.set()
            except (AttributeError, KeyError, TypeError, ValueError):
                callback_error.append(stream)
                observation_ready.set()

        try:
            for stream in ("cell", "ue"):
                if hasattr(sdk, "kpm_cb"):
                    class Callback(sdk.kpm_cb):
                        def handle(callback_self, sample, stream_name=stream):
                            collect(stream_name, sample)

                    callback = Callback()
                else:
                    callback = lambda sample, stream=stream: collect(stream, sample)
                handle = sdk.subscribe_kpm(
                    node["node_id"], stream, callback
                )
                if not handle:
                    raise RuntimeError("KPM_SUBSCRIPTION_PROVIDER_REQUIRED")
                self.kpm_subscriptions[stream] = handle
                self.kpm_callbacks[stream] = callback
        except (AttributeError, RuntimeError, TypeError):
            for handle in self.kpm_subscriptions.values():
                if hasattr(sdk, "unsubscribe_kpm"):
                    try:
                        sdk.unsubscribe_kpm(handle)
                    except (RuntimeError, TypeError):
                        pass
            self.kpm_subscriptions = {}
            self.kpm_callbacks = {}
            return {
                "ok": False,
                "error": "KPM_SUBSCRIPTION_PROVIDER_REQUIRED",
                "failed_stage": "subscription",
                "node_id": node["node_id"],
                "cell": [],
                "ue": [],
                "control_attempted": False,
            }

        observation_ready.wait(KPM_OBSERVATION_TIMEOUT_SECONDS)

        if callback_error:
            return {
                "ok": False,
                "error": "KPM_CALLBACK_MALFORMED",
                "failed_stage": "callback",
                "node_id": node["node_id"],
                "cell": [],
                "ue": [],
                "control_attempted": False,
            }
        if not samples["cell"] or not samples["ue"]:
            return {
                "ok": False,
                "error": "KPM_STREAM_EMPTY",
                "failed_stage": "observation",
                "node_id": node["node_id"],
                "cell": samples["cell"],
                "ue": samples["ue"],
                "control_attempted": False,
            }
        if not all(
            sample.get("kpm_ue_key") and sample.get("rc_ue_id") and sample.get("rnti")
            for sample in samples["ue"]
        ):
            return {
                "ok": False,
                "error": "TARGET_BINDING_REQUIRED",
                "failed_stage": "binding",
                "node_id": node["node_id"],
                "cell": samples["cell"],
                "ue": samples["ue"],
                "control_attempted": False,
            }
        if not all(
            sample["source_seq"] > 0 and sample.get("source_seq_origin") == "e2_indication"
            for sample in samples["ue"]
        ):
            return {
                "ok": False,
                "error": "SOURCE_SEQUENCE_UNVERIFIED",
                "failed_stage": "binding",
                "node_id": node["node_id"],
                "cell": samples["cell"],
                "ue": samples["ue"],
                "control_attempted": False,
            }
        return {
            "ok": False,
            "error": "MEASUREMENT_POST_UNFROZEN",
            "failed_stage": "qualification",
            "node_id": node["node_id"],
            "cell": samples["cell"],
            "ue": samples["ue"],
            "control_attempted": False,
        }


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

    def _journal_state(self) -> str | None:
        if not self.journal_path.exists():
            return None
        try:
            return json.loads(self.journal_path.read_text(encoding="utf-8")).get("state")
        except (OSError, json.JSONDecodeError, AttributeError):
            return None

    def _write_journal(self, state: str) -> None:
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.journal_path.parent,
                prefix=f".{self.journal_path.name}.",
                delete=False,
            ) as stream:
                temp_name = stream.name
                json.dump(
                    {
                        "state": state,
                        "workspace_id": self.workspace_id,
                        "node_id": self.verified_target_binding["node_id"] if self.verified_target_binding else None,
                    },
                    stream,
                    sort_keys=True,
                )
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, self.journal_path)
        finally:
            if temp_name is not None:
                try:
                    Path(temp_name).unlink()
                except FileNotFoundError:
                    pass

    def _release_lease(self) -> None:
        if self.verified_target_binding is None:
            return
        lease_path = self.lease_path()
        try:
            if lease_path.read_text(encoding="utf-8") == self.workspace_id + "\n":
                lease_path.unlink()
        except FileNotFoundError:
            pass

    def _binding_action_fields(self) -> dict | None:
        binding = self.verified_target_binding
        if not isinstance(binding, dict):
            return None
        try:
            node_id = binding["node_id"]
            rc_ue_id = int(binding["rc_ue_id"])
            rnti = int(binding["rnti"])
        except (KeyError, TypeError, ValueError):
            return None
        if (
            not isinstance(node_id, str)
            or not re.fullmatch(r"[A-Za-z0-9_.:-]+", node_id)
            or rc_ue_id <= 0
            or rnti <= 0
            or rnti > 0xFFFF
        ):
            return None
        return {"node_id": node_id, "rc_ue_id": rc_ue_id, "rnti": rnti}

    @staticmethod
    def _proof_succeeded(outcome: object, candidate: bool = False) -> bool:
        if not isinstance(outcome, dict):
            return False
        return (
            outcome.get("acknowledged") is True
            and outcome.get("gnb_apply_marker") is True
            and (not candidate or outcome.get("later_kpm") is True)
        )

    def _control_once(self, request: dict, session: dict) -> dict:
        response = {"request_id": request["request_id"]}
        binding = self._binding_action_fields()
        if binding is None:
            response.update({"ok": False, "error": "TARGET_BINDING_REQUIRED"})
            return response
        if not callable(self.native_control):
            response.update({"ok": False, "error": "APPLY_PROOF_PROVIDER_REQUIRED"})
            return response

        action = request.get("action")
        candidate = action.get("max_ul_prb") if isinstance(action, dict) else None
        if isinstance(candidate, bool) or not isinstance(candidate, int) or candidate < 0 or candidate > 275:
            response.update({"ok": False, "error": "CONTRACT_VALIDATION_FAILED"})
            return response

        calls = []

        def apply(phase: str, value: int, journal_state: str) -> object | None:
            self._write_journal(journal_state)
            payload = {**binding, "phase": phase, "max_ul_prb": value}
            calls.append(payload)
            try:
                return self.native_control(payload)
            except (OSError, RuntimeError, TypeError, ValueError):
                return None

        baseline = apply("baseline", 0, "BASELINE_PENDING")
        if not self._proof_succeeded(baseline):
            self._write_journal("ROLLBACK_UNCONFIRMED")
            session["acted"] = True
            response.update({"ok": False, "error": "ROLLBACK_UNCONFIRMED"})
            return response

        candidate_result = apply("candidate", candidate, "CANDIDATE_PENDING")
        if not self._proof_succeeded(candidate_result, candidate=True):
            restored = apply("restore", 0, "ROLLBACK_PENDING")
            session["acted"] = True
            if self._proof_succeeded(restored):
                self._write_journal("RECOVERED")
                response.update({"ok": False, "error": "CANDIDATE_PROOF_REQUIRED"})
                return response
            self._write_journal("ROLLBACK_UNCONFIRMED")
            response.update({"ok": False, "error": "ROLLBACK_UNCONFIRMED"})
            return response

        restored = apply("restore", 0, "RESTORE_PENDING")
        session["acted"] = True
        if not self._proof_succeeded(restored):
            self._write_journal("ROLLBACK_UNCONFIRMED")
            response.update({"ok": False, "error": "ROLLBACK_UNCONFIRMED"})
            return response

        self._write_journal("COMPLETED")
        response.update({"ok": True, "transaction": "baseline-candidate-restore", "phases": [call["phase"] for call in calls]})
        return response

    def recover(self, request: dict) -> dict:
        response = {"request_id": request["request_id"]}
        state = self._journal_state()
        if state is None:
            response.update({"ok": False, "error": "RECOVERY_REQUIRED"})
            return response
        if state in {"IDLE", "COMPLETED", "RECOVERED"}:
            response.update({"ok": False, "error": "RECOVERY_NOT_REQUIRED"})
            return response
        binding = self._binding_action_fields()
        if binding is None:
            response.update({"ok": False, "error": "TARGET_BINDING_REQUIRED"})
            return response
        if not callable(self.native_control):
            response.update({"ok": False, "error": "APPLY_PROOF_PROVIDER_REQUIRED"})
            return response
        self._write_journal("RECOVERY_PENDING")
        payload = {**binding, "phase": "recovery", "max_ul_prb": 0}
        try:
            outcome = self.native_control(payload)
        except (OSError, RuntimeError, TypeError, ValueError):
            outcome = None
        if self._proof_succeeded(outcome):
            self._write_journal("RECOVERED")
            self._release_lease()
            response.update({"ok": True, "phase": "recovery"})
            return response
        self._write_journal("ROLLBACK_UNCONFIRMED")
        response.update({"ok": False, "error": "ROLLBACK_UNCONFIRMED"})
        return response

    def open(self, request: dict) -> dict:
        mode = request.get("mode")
        if mode not in {"observation-only", "control-once"}:
            return {"ok": False, "error": "INVALID_MODE", "request_id": request["request_id"]}
        if mode == "control-once":
            if self.profile == "none":
                return {"ok": False, "error": "PROFILE_FORBIDS_CONTROL", "request_id": request["request_id"]}
            if self._binding_action_fields() is None:
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
            try:
                self._write_journal("LEASE_ACQUIRED")
            except OSError:
                self._release_lease()
                return {"ok": False, "error": "JOURNAL_WRITE_FAILED", "request_id": request["request_id"]}
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
            if self.native is None or not hasattr(self.native, "qualify"):
                return {"ok": False, "error": "NATIVE_QUALIFICATION_UNAVAILABLE", "request_id": request["request_id"]}
            try:
                result = dict(self.native.qualify(self.profile))
            except (ImportError, RuntimeError) as error:
                return {"ok": False, "error": str(error), "request_id": request["request_id"]}
            result.setdefault("request_id", request["request_id"])
            result.setdefault("control_attempted", False)
            return result
        if request["operation"] == "recover":
            try:
                return self.recover(request)
            except OSError:
                return {"ok": False, "error": "JOURNAL_WRITE_FAILED", "request_id": request["request_id"]}
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
                if self._journal_state() != "ROLLBACK_UNCONFIRMED":
                    self._release_lease()
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
            try:
                return self._control_once(request, session)
            except OSError:
                return {"ok": False, "error": "JOURNAL_WRITE_FAILED", "request_id": request["request_id"]}
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
    parser.add_argument("--workspace-lock", type=Path, required=True)
    args = parser.parse_args()
    try:
        validate_workspace_lock(args.workspace_lock, args.profile, args.workspace_id)
    except ValueError as error:
        parser.error(str(error))
    serve(args.socket, args.profile, args.flexric_config, args.workspace_id)


if __name__ == "__main__":
    main()
