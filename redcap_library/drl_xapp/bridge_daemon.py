#!/usr/bin/env python3

"""Fail-closed UDS bridge; live KPM/control handlers are added behind explicit gates."""

import argparse
import json
import math
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
KPM_CADENCE_MIN_CALLBACKS = 3
KPM_SAMPLE_BUFFER_LIMIT = 64
APPLY_PROOF_WINDOW_MS = 1_000


def monotonic_ms() -> int:
    return time.monotonic_ns() // 1_000_000


def marker_proof(proof_path: Path, action: dict, sent_at_ms: int) -> dict:
    """Return only a gNB marker that matches this action inside its proof window."""
    try:
        rnti = action["rnti"]
        requested = action["max_ul_prb"]
        if any(isinstance(value, bool) for value in (rnti, requested, sent_at_ms)):
            raise ValueError
        rnti = int(rnti)
        requested = int(requested)
        sent_at_ms = int(sent_at_ms)
        if not 0 < rnti <= 0xFFFF or not 0 <= requested <= 275:
            raise ValueError
        records = proof_path.read_text(encoding="utf-8").splitlines()
    except (KeyError, OSError, TypeError, ValueError):
        return {"gnb_apply_marker": False}

    deadline_ms = sent_at_ms + APPLY_PROOF_WINDOW_MS
    for line in records:
        try:
            record = json.loads(line)
            observed_ms = record["observed_monotonic_ms"]
            if any(isinstance(value, bool) for value in (record["rnti"], record["requested"], record["effective"], observed_ms)):
                continue
            if (
                int(record["rnti"]) == rnti
                and int(record["requested"]) == requested
                and sent_at_ms <= int(observed_ms) <= deadline_ms
            ):
                return {"gnb_apply_marker": True, "marker": record}
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            continue
    return {"gnb_apply_marker": False}


def wait_marker_proof(proof_path: Path, action: dict, sent_at_ms: int) -> dict:
    deadline_ms = sent_at_ms + APPLY_PROOF_WINDOW_MS
    while monotonic_ms() <= deadline_ms:
        result = marker_proof(proof_path, action, sent_at_ms)
        if result["gnb_apply_marker"]:
            return result
        time.sleep(0.01)
    return {"gnb_apply_marker": False}


def canonical_kpm_styles(styles: object) -> list[dict]:
    if not isinstance(styles, list):
        return []
    return sorted(
        (style for style in styles if isinstance(style, dict)),
        key=lambda style: json.dumps(style, sort_keys=True),
    )


def pair_kpm_samples(samples: dict) -> list[tuple[dict, dict, int]]:
    """Pair cell and UE observations by E2 indication event time, never callback order."""
    cell = sorted(samples["cell"], key=lambda sample: sample["timestamp_ms"])
    ue = sorted(samples["ue"], key=lambda sample: sample["timestamp_ms"])
    return [(cell_sample, ue_sample, abs(cell_sample["timestamp_ms"] - ue_sample["timestamp_ms"]))
            for cell_sample, ue_sample in zip(cell, ue)]


def calibration_summary(pairs: list[tuple[dict, dict, int]]) -> dict:
    valid = [
        (cell, ue, skew_ms)
        for cell, ue, skew_ms in pairs
        if (
            cell.get("source_seq_origin") == "e2_indication"
            and ue.get("source_seq_origin") == "e2_indication"
            and cell.get("timestamp_ms", 0) > 0
            and ue.get("timestamp_ms", 0) > 0
        )
    ]
    if not valid:
        return {"event_time_origin": None, "valid_paired_samples": 0}
    evaluated_at_ms = monotonic_ms()
    return {
        "event_time_origin": "e2_indication_collectStartTime_ms",
        "valid_paired_samples": len(valid),
        "max_cell_ue_skew_ms": max(skew_ms for _cell, _ue, skew_ms in valid),
        "max_freshness_age_ms": max(
            evaluated_at_ms - min(cell["bridge_monotonic_receipt_ms"], ue["bridge_monotonic_receipt_ms"])
            for cell, ue, _skew_ms in valid
        ),
    }


def qualified_model_observation(qualification: object) -> dict:
    """Build the profile's model input from event-time-qualified KPM pairs."""
    if not isinstance(qualification, dict):
        return {"ok": False, "error": "MODEL_OBSERVATION_REQUIRED"}
    cell = qualification.get("cell")
    ue = qualification.get("ue")
    if not isinstance(cell, list) or not isinstance(ue, list):
        return {"ok": False, "error": "MODEL_OBSERVATION_REQUIRED"}
    values = []
    try:
        for cell_sample, ue_sample, _skew_ms in pair_kpm_samples({"cell": cell, "ue": ue}):
            if (
                cell_sample.get("source_seq_origin") != "e2_indication"
                or ue_sample.get("source_seq_origin") != "e2_indication"
                or int(cell_sample["timestamp_ms"]) <= 0
                or int(ue_sample["timestamp_ms"]) <= 0
            ):
                continue
            value = cell_sample["measurements"]["RRU.PrbTotUl"]
            if isinstance(value, bool):
                continue
            value = float(value)
            if 0 <= value <= 100 and math.isfinite(value):
                values.append(value)
    except (KeyError, TypeError, ValueError, OverflowError):
        return {"ok": False, "error": "MODEL_OBSERVATION_REQUIRED"}
    if len(values) < 30:
        return {"ok": False, "error": "MODEL_OBSERVATION_REQUIRED"}
    values = values[-30:]
    return {
        "ok": True,
        "observation": {
            "schema_version": 1,
            "profile_id": "ul-prb-cap-v1",
            "sample_count": 30,
            "rru_prb_tot_ul_pct": {
                "latest": values[-1],
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
            },
        },
    }


def validate_workspace_lock(path: Path, profile: str, workspace_id: str) -> dict:
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
        if not isinstance(measurement_post, dict) or measurement_post.get("status") not in {"UNFROZEN", "FROZEN"}:
            raise ValueError("MEASUREMENT_POST_POLICY_UNSUPPORTED")
        if measurement_post["status"] == "FROZEN":
            fingerprint = measurement_post.get("fingerprint")
            if (
                not isinstance(fingerprint, dict)
                or fingerprint.get("release") != lock.get("release")
                or fingerprint.get("images") != lock.get("images")
            ):
                raise ValueError("CALIBRATION_FINGERPRINT_CHANGED")
    return lock


class NativeFlexric:
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.sdk = None
        self.initialized = False
        self.kpm_subscriptions = {}
        self.kpm_callbacks = {}
        self.kpm_node_id = None
        self.kpm_samples = {"cell": [], "ue": []}
        self.kpm_callback_error = []
        self.kpm_cadence = {}
        self.kpm_condition = threading.Condition()
        self.measurement_post = {"status": "UNFROZEN"}

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

    def control_ul_prb(self, action: dict) -> dict:
        try:
            if any(isinstance(action[field], bool) for field in ("rc_ue_id", "rnti", "max_ul_prb")):
                raise ValueError
            node_id = str(action["node_id"])
            rc_ue_id = int(action["rc_ue_id"])
            rnti = int(action["rnti"])
            max_ul_prb = int(action["max_ul_prb"])
        except (KeyError, TypeError, ValueError):
            return {"acknowledged": False, "error": "INVALID_CONTROL_ACTION"}
        if rc_ue_id <= 0 or rnti <= 0 or rnti > 0xFFFF or max_ul_prb < 0 or max_ul_prb > 275:
            return {"acknowledged": False, "error": "INVALID_CONTROL_ACTION"}
        sdk = self.load()
        if not hasattr(sdk, "control_redcap_ul_prb_sm"):
            return {"acknowledged": False, "error": "NATIVE_CONTROL_UNAVAILABLE"}
        try:
            nodes = list(sdk.conn_e2_nodes())
        except (AttributeError, RuntimeError, TypeError, ValueError):
            return {"acknowledged": False, "error": "NATIVE_CONTROL_UNAVAILABLE"}
        for node in nodes:
            if all(hasattr(node, field) for field in ("ran_type", "mcc", "mnc", "node_id")):
                key = f"{int(node.ran_type)}:{int(node.mcc)}:{int(node.mnc)}:{int(node.node_id)}"
            else:
                native_id = node.id
                key = f"{int(native_id.type)}:{int(native_id.plmn.mcc)}:{int(native_id.plmn.mnc)}:{int(native_id.nb_id.nb_id)}"
            if key != node_id or not hasattr(node, "id"):
                continue
            try:
                request_id = int(sdk.control_redcap_ul_prb_sm(node.id, rc_ue_id, rnti, max_ul_prb))
            except (RuntimeError, TypeError, ValueError):
                return {"acknowledged": False, "error": "NATIVE_CONTROL_FAILED"}
            return {"acknowledged": request_id != 0, "ric_request_id": request_id}
        return {"acknowledged": False, "error": "TARGET_NODE_UNAVAILABLE"}

    def prove_ul_prb(self, action: dict, profile: str, proof_path: Path) -> dict:
        sent_at_ms = monotonic_ms()
        outcome = self.control_ul_prb(action)
        if not isinstance(outcome, dict):
            return {"acknowledged": False, "gnb_apply_marker": False, "later_kpm": False}
        if outcome.get("acknowledged") is not True:
            return {**outcome, "gnb_apply_marker": False, "later_kpm": False}

        marker = wait_marker_proof(proof_path, action, sent_at_ms)
        deadline_ms = sent_at_ms + APPLY_PROOF_WINDOW_MS
        remaining_seconds = (deadline_ms - monotonic_ms()) / 1_000
        if not marker["gnb_apply_marker"] or remaining_seconds <= 0:
            return {**outcome, **marker, "later_kpm": False}
        qualification = self.qualify(
            profile,
            observation_timeout_seconds=remaining_seconds,
            received_after_ms=sent_at_ms,
        )
        binding = qualification.get("verified_target_binding") if isinstance(qualification, dict) else None
        later_kpm = isinstance(qualification, dict) and bool(
            qualification.get("ok")
            and isinstance(binding, dict)
            and all(binding.get(field) == action.get(field) for field in ("node_id", "rc_ue_id", "rnti"))
            and monotonic_ms() <= deadline_ms
        )
        return {**outcome, **marker, "later_kpm": later_kpm}

    def _eligible_kpm_node(self, profile: str) -> tuple[dict | None, dict | None]:
        if profile != "ul-prb-cap-v1":
            return None, {"ok": False, "error": "PROFILE_FORBIDS_LIVE_KPM", "control_attempted": False}
        capabilities = self.discover()
        eligible = [node for node in capabilities["nodes"] if node["kpm_advertised"] and node["rc_advertised"]]
        if len(eligible) != 1:
            return None, {"ok": False, "error": "EXACTLY_ONE_ELIGIBLE_NODE_REQUIRED",
                          "eligible_node_count": len(eligible), "control_attempted": False}
        node = eligible[0]
        styles = node["kpm_styles"]
        if not isinstance(styles, list):
            return None, {"ok": False, "error": "KPM_STYLE_UNVERIFIED", "node_id": node["node_id"],
                          "control_attempted": False}
        has_cell = any(style["action_definition_format"] == 0 and style["indication_message_format"] == 0 for style in styles)
        has_ue = any(style["action_definition_format"] == 3 and style["indication_message_format"] == 2 for style in styles)
        if not has_cell or not has_ue:
            return None, {
                "ok": False,
                "error": "CELL_KPM_STREAM_REQUIRED" if not has_cell else "UE_KPM_STREAM_REQUIRED",
                "failed_stage": "capability",
                "node_id": node["node_id"],
                "available_kpm_styles": styles,
                "cell": [],
                "ue": [],
                "control_attempted": False,
            }
        return node, None

    def _clear_kpm_subscriptions(self, sdk) -> None:
        for handle in self.kpm_subscriptions.values():
            if hasattr(sdk, "unsubscribe_kpm"):
                try:
                    sdk.unsubscribe_kpm(handle)
                except (RuntimeError, TypeError):
                    pass
        self.kpm_subscriptions = {}
        self.kpm_callbacks = {}
        self.kpm_node_id = None

    def _record_kpm_sample(self, stream: str, sample: object) -> None:
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
            projected["bridge_monotonic_receipt_ms"] = monotonic_ms()
        except (AttributeError, KeyError, TypeError, ValueError):
            with self.kpm_condition:
                self.kpm_callback_error.append(stream)
                self.kpm_condition.notify_all()
            return
        with self.kpm_condition:
            cadence = self.kpm_cadence[stream]
            received_at_ms = projected["bridge_monotonic_receipt_ms"]
            if cadence["first_callback_monotonic_ms"] is None:
                cadence["first_callback_monotonic_ms"] = received_at_ms
            cadence["callback_count"] += 1
            cadence["latest_ric_indication_sn"] = (
                projected["source_seq"] if projected.get("source_seq_origin") == "e2_indication" else None
            )
            cadence["latest_event_time_ms"] = projected["timestamp_ms"]
            self.kpm_samples[stream].append(projected)
            del self.kpm_samples[stream][:-KPM_SAMPLE_BUFFER_LIMIT]
            self.kpm_condition.notify_all()

    def _ensure_kpm_subscriptions(self, node: dict) -> tuple[bool, dict | None]:
        sdk = self.load()
        if not hasattr(sdk, "subscribe_kpm"):
            return False, {"ok": False, "error": "KPM_SUBSCRIPTION_PROVIDER_REQUIRED", "failed_stage": "subscription",
                           "node_id": node["node_id"], "cell": [], "ue": [], "control_attempted": False}
        if self.kpm_node_id == node["node_id"] and set(self.kpm_subscriptions) == {"cell", "ue"}:
            return False, None
        self._clear_kpm_subscriptions(sdk)
        with self.kpm_condition:
            self.kpm_node_id = node["node_id"]
            self.kpm_samples = {"cell": [], "ue": []}
            self.kpm_callback_error = []
            self.kpm_cadence = {
                stream: {
                    "subscription_accepted_monotonic_ms": None,
                    "first_callback_monotonic_ms": None,
                    "callback_count": 0,
                    "latest_ric_indication_sn": None,
                    "latest_event_time_ms": None,
                }
                for stream in ("cell", "ue")
            }
        try:
            for stream in ("cell", "ue"):
                if hasattr(sdk, "kpm_cb"):
                    native = self

                    class Callback(sdk.kpm_cb):
                        def handle(callback_self, sample, stream_name=stream):
                            native._record_kpm_sample(stream_name, sample)

                    callback = Callback()
                else:
                    callback = lambda sample, stream_name=stream: self._record_kpm_sample(stream_name, sample)
                handle = sdk.subscribe_kpm(node["node_id"], stream, callback)
                if not handle:
                    raise RuntimeError("KPM_SUBSCRIPTION_PROVIDER_REQUIRED")
                with self.kpm_condition:
                    self.kpm_subscriptions[stream] = handle
                    self.kpm_callbacks[stream] = callback
                    self.kpm_cadence[stream]["subscription_accepted_monotonic_ms"] = time.monotonic_ns() // 1_000_000
        except (AttributeError, RuntimeError, TypeError):
            self._clear_kpm_subscriptions(sdk)
            return False, {"ok": False, "error": "KPM_SUBSCRIPTION_PROVIDER_REQUIRED", "failed_stage": "subscription",
                           "node_id": node["node_id"], "cell": [], "ue": [], "control_attempted": False}
        return True, None

    def _wait_for_kpm_samples(self, minimum_samples: int, received_after_ms: int | None, timeout_seconds: float) -> tuple[dict, list[str]]:
        deadline = time.monotonic() + max(0.0, min(float(timeout_seconds), KPM_OBSERVATION_TIMEOUT_SECONDS))
        with self.kpm_condition:
            while True:
                samples = {
                    stream: [
                        sample for sample in self.kpm_samples[stream]
                        if received_after_ms is None or sample["bridge_monotonic_receipt_ms"] > received_after_ms
                    ]
                    for stream in ("cell", "ue")
                }
                if self.kpm_callback_error or all(len(samples[stream]) >= minimum_samples for stream in samples):
                    return samples, list(self.kpm_callback_error)
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return samples, list(self.kpm_callback_error)
                self.kpm_condition.wait(remaining)

    def _cadence_snapshot(self) -> dict:
        with self.kpm_condition:
            snapshot = {}
            for stream, cadence in self.kpm_cadence.items():
                accepted = cadence["subscription_accepted_monotonic_ms"]
                first = cadence["first_callback_monotonic_ms"]
                snapshot[stream] = {
                    "subscription_accepted_monotonic_ms": accepted,
                    "first_callback_latency_ms": None if accepted is None or first is None else max(0, first - accepted),
                    "callback_count": cadence["callback_count"],
                    "latest_ric_indication_sn": cadence["latest_ric_indication_sn"],
                    "latest_event_time_ms": cadence["latest_event_time_ms"],
                }
            return snapshot

    def observe(self, profile: str) -> dict:
        node, failure = self._eligible_kpm_node(profile)
        if failure is not None:
            return failure
        created, failure = self._ensure_kpm_subscriptions(node)
        if failure is not None:
            return failure
        received_after_ms = None if created else monotonic_ms()
        samples, callback_error = self._wait_for_kpm_samples(
            KPM_CADENCE_MIN_CALLBACKS,
            received_after_ms,
            KPM_OBSERVATION_TIMEOUT_SECONDS,
        )
        cadence = self._cadence_snapshot()
        if callback_error:
            return {"ok": False, "error": "KPM_CALLBACK_MALFORMED", "failed_stage": "callback", "node_id": node["node_id"],
                    "cell": samples["cell"], "ue": samples["ue"], "cadence": cadence, "control_attempted": False}
        if not all(len(samples[stream]) >= KPM_CADENCE_MIN_CALLBACKS for stream in samples):
            return {"ok": False, "error": "KPM_STREAM_EMPTY", "failed_stage": "observation", "node_id": node["node_id"],
                    "cell": samples["cell"], "ue": samples["ue"], "cadence": cadence, "control_attempted": False}
        return {"ok": True, "node_id": node["node_id"], "cell": samples["cell"], "ue": samples["ue"],
                "cadence": cadence, "control_attempted": False}

    def qualify(
        self,
        profile: str,
        observation_timeout_seconds: float | None = None,
        received_after_ms: int | None = None,
    ) -> dict:
        node, failure = self._eligible_kpm_node(profile)
        if failure is not None:
            return failure
        created, failure = self._ensure_kpm_subscriptions(node)
        if failure is not None:
            return failure
        policy = self.measurement_post
        minimum_samples = policy.get("min_valid_paired_samples", 1) if isinstance(policy, dict) else 1
        if isinstance(minimum_samples, bool) or not isinstance(minimum_samples, int) or minimum_samples < 1:
            minimum_samples = 1
        if received_after_ms is None and not created:
            received_after_ms = monotonic_ms()
        timeout_seconds = KPM_OBSERVATION_TIMEOUT_SECONDS if observation_timeout_seconds is None else observation_timeout_seconds
        samples, callback_error = self._wait_for_kpm_samples(minimum_samples, received_after_ms, timeout_seconds)
        if callback_error:
            return {"ok": False, "error": "KPM_CALLBACK_MALFORMED", "failed_stage": "callback", "node_id": node["node_id"],
                    "cell": [], "ue": [], "control_attempted": False}
        if not samples["cell"] or not samples["ue"]:
            return {"ok": False, "error": "KPM_STREAM_EMPTY", "failed_stage": "observation", "node_id": node["node_id"],
                    "cell": samples["cell"], "ue": samples["ue"], "control_attempted": False}
        if not all(sample.get("kpm_ue_key") and sample.get("rc_ue_id") and sample.get("rnti") for sample in samples["ue"]):
            return {"ok": False, "error": "TARGET_BINDING_REQUIRED", "failed_stage": "binding", "node_id": node["node_id"],
                    "cell": samples["cell"], "ue": samples["ue"], "control_attempted": False}
        if not all(sample["source_seq"] > 0 and sample.get("source_seq_origin") == "e2_indication" for sample in samples["ue"]):
            return {"ok": False, "error": "SOURCE_SEQUENCE_UNVERIFIED", "failed_stage": "binding", "node_id": node["node_id"],
                    "cell": samples["cell"], "ue": samples["ue"], "control_attempted": False}
        pairs = pair_kpm_samples(samples)
        calibration = calibration_summary(pairs)
        if not isinstance(policy, dict) or policy.get("status") != "FROZEN":
            return {"ok": False, "error": "MEASUREMENT_POST_UNFROZEN", "failed_stage": "qualification", "node_id": node["node_id"],
                    "cell": samples["cell"], "ue": samples["ue"], "measurement_post": calibration, "control_attempted": False}
        try:
            freshness_window_ms = int(policy["freshness_window_ms"])
            max_skew_ms = int(policy["cell_ue_max_skew_ms"])
            minimum_samples = int(policy["min_valid_paired_samples"])
            expected_fingerprint = policy["fingerprint"]
        except (KeyError, TypeError, ValueError):
            return {"ok": False, "error": "MEASUREMENT_POST_POLICY_INVALID", "failed_stage": "qualification", "node_id": node["node_id"],
                    "cell": samples["cell"], "ue": samples["ue"], "control_attempted": False}
        if freshness_window_ms < 0 or max_skew_ms < 0 or minimum_samples < 1 or not isinstance(expected_fingerprint, dict):
            return {"ok": False, "error": "MEASUREMENT_POST_POLICY_INVALID", "failed_stage": "qualification", "node_id": node["node_id"],
                    "cell": samples["cell"], "ue": samples["ue"], "control_attempted": False}
        if not all(sample.get("source_seq_origin") == "e2_indication" and sample.get("timestamp_ms", 0) > 0
                   for stream in ("cell", "ue") for sample in samples[stream]):
            return {"ok": False, "error": "KPM_TIME_ORIGIN_UNPROVEN", "failed_stage": "time-origin", "node_id": node["node_id"],
                    "cell": samples["cell"], "ue": samples["ue"], "control_attempted": False}
        actual_fingerprint = {
            "node_id": node["node_id"], "kpm_styles": canonical_kpm_styles(node["kpm_styles"]),
            "cell_metrics": sorted({name for sample in samples["cell"] for name in sample["measurements"]}),
            "ue_metrics": sorted({name for sample in samples["ue"] for name in sample["measurements"]}),
            "event_time_origin": "e2_indication_collectStartTime_ms",
        }
        expected = {
            "node_id": expected_fingerprint.get("node_id"),
            "kpm_styles": canonical_kpm_styles(expected_fingerprint.get("kpm_styles")),
            "cell_metrics": expected_fingerprint.get("cell_metrics"),
            "ue_metrics": expected_fingerprint.get("ue_metrics"),
            "event_time_origin": expected_fingerprint.get("event_time_origin"),
        }
        if actual_fingerprint != expected:
            return {"ok": False, "error": "CALIBRATION_FINGERPRINT_CHANGED", "failed_stage": "fingerprint", "node_id": node["node_id"],
                    "cell": samples["cell"], "ue": samples["ue"], "control_attempted": False}
        if any(skew_ms > max_skew_ms for _cell, _ue, skew_ms in pairs):
            return {"ok": False, "error": "CELL_UE_SKEW_EXCEEDED", "failed_stage": "alignment", "node_id": node["node_id"],
                    "cell": samples["cell"], "ue": samples["ue"], "control_attempted": False}
        if len(pairs) < minimum_samples:
            return {"ok": False, "error": "VALID_PAIRED_SAMPLES_REQUIRED", "failed_stage": "pairing", "node_id": node["node_id"],
                    "cell": samples["cell"], "ue": samples["ue"], "control_attempted": False}
        freshness_age_ms = calibration["max_freshness_age_ms"]
        if freshness_age_ms > freshness_window_ms:
            return {"ok": False, "error": "KPM_FRESHNESS_EXPIRED", "failed_stage": "freshness", "node_id": node["node_id"],
                    "cell": samples["cell"], "ue": samples["ue"], "control_attempted": False}
        selected_ue = pairs[0][1]
        return {
            "ok": True,
            "node_id": node["node_id"],
            "cell": samples["cell"],
            "ue": samples["ue"],
            "verified_target_binding": {
                "node_id": node["node_id"], "kpm_ue_key": selected_ue["kpm_ue_key"],
                "rc_ue_id": selected_ue["rc_ue_id"], "rnti": selected_ue["rnti"],
                "source_seq": selected_ue["source_seq"], "source_seq_origin": selected_ue["source_seq_origin"],
            },
            "measurement_post": {"freshness_age_ms": freshness_age_ms,
                                 "max_cell_ue_skew_ms": max(skew_ms for _cell, _ue, skew_ms in pairs),
                                 "valid_paired_samples": len(pairs)},
            "control_attempted": False,
        }


class Bridge:
    def __init__(
        self,
        profile: str,
        native_control=None,
        native=None,
        measurement_post=None,
        qualified_binding=None,
        lease_dir: Path = Path("/run/redcap-drl/leases"),
        workspace_id: str = "workspace",
        journal_path: Path = Path("/run/redcap-drl/control_journal.json"),
    ):
        self.profile = profile
        self.native_control = native_control
        self.native = native
        self.measurement_post = measurement_post or {"status": "UNFROZEN"}
        if self.native is not None and hasattr(self.native, "measurement_post"):
            self.native.measurement_post = self.measurement_post
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

    def _requalify_before_action(self) -> str | None:
        if self.native is None or not hasattr(self.native, "qualify"):
            return None
        try:
            qualification = self.native.qualify(self.profile)
        except (ImportError, RuntimeError):
            return "KPM_QUALIFICATION_REQUIRED"
        if not qualification.get("ok"):
            return qualification.get("error", "KPM_QUALIFICATION_REQUIRED")
        binding = qualification.get("verified_target_binding")
        if not isinstance(binding, dict):
            return "TARGET_BINDING_REQUIRED"
        current = self.verified_target_binding
        if not isinstance(current, dict) or any(
            binding.get(field) != current.get(field)
            for field in ("node_id", "kpm_ue_key", "rc_ue_id", "rnti")
        ):
            return "TARGET_BINDING_CHANGED"
        return None

    @staticmethod
    def _proof_succeeded(outcome: object) -> bool:
        if not isinstance(outcome, dict):
            return False
        return (
            outcome.get("acknowledged") is True
            and outcome.get("gnb_apply_marker") is True
            and outcome.get("later_kpm") is True
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

        qualification_error = self._requalify_before_action()
        if qualification_error is not None:
            response.update({"ok": False, "error": qualification_error})
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

        qualification_error = self._requalify_before_action()
        if qualification_error is not None:
            self._write_journal("RECOVERED")
            session["acted"] = True
            response.update({"ok": False, "error": qualification_error})
            return response

        candidate_result = apply("candidate", candidate, "CANDIDATE_PENDING")
        if not self._proof_succeeded(candidate_result):
            restored = apply("restore", 0, "ROLLBACK_PENDING")
            session["acted"] = True
            if self._proof_succeeded(restored):
                self._write_journal("RECOVERED")
                response.update({"ok": False, "error": "CANDIDATE_PROOF_REQUIRED"})
                return response
            self._write_journal("ROLLBACK_UNCONFIRMED")
            response.update({"ok": False, "error": "ROLLBACK_UNCONFIRMED"})
            return response

        qualification_error = self._requalify_before_action()
        if qualification_error is not None:
            session["acted"] = True
            self._write_journal("ROLLBACK_UNCONFIRMED")
            response.update({"ok": False, "error": qualification_error})
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
            if self.native is not None and hasattr(self.native, "qualify"):
                try:
                    qualification = self.native.qualify(self.profile)
                except (ImportError, RuntimeError):
                    qualification = {"ok": False, "error": "KPM_QUALIFICATION_REQUIRED"}
                if not qualification.get("ok"):
                    return {
                        "ok": False,
                        "error": qualification.get("error", "KPM_QUALIFICATION_REQUIRED"),
                        "request_id": request["request_id"],
                    }
                self.verified_target_binding = qualification["verified_target_binding"]
            elif self._binding_action_fields() is None:
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
            if self.native is None or not hasattr(self.native, "observe"):
                return {"ok": False, "error": "NATIVE_OBSERVATION_UNAVAILABLE", "request_id": request["request_id"]}
            try:
                result = dict(self.native.observe(self.profile))
            except (ImportError, RuntimeError) as error:
                return {"ok": False, "error": str(error), "request_id": request["request_id"]}
            result.setdefault("request_id", request["request_id"])
            result.setdefault("control_attempted", False)
            return result
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


def serve(socket_path: Path, profile: str, flexric_config: Path, workspace_id: str, measurement_post: dict) -> None:
    native = NativeFlexric(flexric_config)
    bridge = Bridge(
        profile,
        native=native,
        native_control=lambda action: native.prove_ul_prb(
            action,
            profile,
            socket_path.parent / "gnb_apply_proof.jsonl",
        ),
        measurement_post=measurement_post,
        workspace_id=workspace_id,
    )
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
        lock = validate_workspace_lock(args.workspace_lock, args.profile, args.workspace_id)
    except ValueError as error:
        parser.error(str(error))
    serve(args.socket, args.profile, args.flexric_config, args.workspace_id, lock.get("measurement_post", {"status": "UNFROZEN"}))


if __name__ == "__main__":
    main()
