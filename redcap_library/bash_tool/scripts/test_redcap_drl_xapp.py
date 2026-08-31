#!/usr/bin/env python3

import os
from pathlib import Path
import importlib.util
import json
import subprocess
import tempfile
import threading
from types import SimpleNamespace
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
CLI = REPO_ROOT / "redcap_library/bash_tool/scripts/redcap_drl_xapp.sh"
BRIDGE = REPO_ROOT / "redcap_library/drl_xapp/bridge_daemon.py"
CLI_MODULE = REPO_ROOT / "redcap_library/bash_tool/scripts/redcap_drl_xapp.py"


def load_bridge_module():
    spec = importlib.util.spec_from_file_location("redcap_drl_bridge", BRIDGE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_cli_module():
    spec = importlib.util.spec_from_file_location("redcap_drl_xapp_cli", CLI_MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RedcapDrlXappCliTest(unittest.TestCase):
    def test_qualify_runs_discovery_and_writes_one_manifest(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            lock = {
                "name": "test-workspace",
                "release": "test-release",
                "images": {},
                "profile": "ul-prb-cap-v1",
            }
            cli_module.load_workspace = lambda _workspace: (workspace, lock, {})
            calls = []

            def fake_uds_call(_socket, request):
                calls.append(request["operation"])
                if request["operation"] == "discover":
                    return {"ok": True, "capabilities": {"nodes": ["node-a"]}}
                return {"ok": True, "cell": [{"seq": 1}], "ue": [{"seq": 1}]}

            cli_module.uds_call = fake_uds_call
            self.assertEqual(cli_module.bridge_gate(SimpleNamespace(command="qualify-kpm", workspace=workspace)), 0)
            self.assertEqual(calls, ["discover", "qualify"])
            run_dir = next((workspace / "artifacts/runs").iterdir())
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertIn("discover-kpm", manifest["gates"])
            self.assertIn("qualify-kpm", manifest["gates"])
            self.assertNotIn("control", manifest["gates"])

    def test_qualify_stops_after_failed_discovery(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            lock = {"name": "test-workspace", "release": "test-release", "images": {}, "profile": "ul-prb-cap-v1"}
            cli_module.load_workspace = lambda _workspace: (workspace, lock, {})
            calls = []

            def fake_uds_call(_socket, request):
                calls.append(request["operation"])
                return {"ok": False, "error": "DISCOVERY_FAILED"}

            cli_module.uds_call = fake_uds_call
            self.assertEqual(cli_module.bridge_gate(SimpleNamespace(command="qualify-kpm", workspace=workspace)), 4)
            self.assertEqual(calls, ["discover"])
            run_dir = next((workspace / "artifacts/runs").iterdir())
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertIn("discover-kpm", manifest["gates"])
            self.assertNotIn("qualify-kpm", manifest["gates"])

    def test_qualify_evidence_projects_resolved_node_without_control(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            lock = {"name": "test-workspace", "release": "test-release", "images": {}, "profile": "ul-prb-cap-v1"}
            cli_module.load_workspace = lambda _workspace: (workspace, lock, {})

            def fake_uds_call(_socket, request):
                if request["operation"] == "discover":
                    return {"ok": True, "node_id": "node-a", "capabilities": {"nodes": ["node-a"]}}
                return {"ok": True, "node_id": "node-a", "cell": [{"seq": 1}], "ue": [{"seq": 1}]}

            cli_module.uds_call = fake_uds_call
            self.assertEqual(cli_module.bridge_gate(SimpleNamespace(command="qualify-kpm", workspace=workspace)), 0)
            run_dir = next((workspace / "artifacts/runs").iterdir())
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            journal = json.loads((run_dir / "control_journal.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["resolved_node"], "node-a")
            self.assertEqual(journal, {"state": "NOT_STARTED", "control_attempted": False})

    def test_run_control_stops_before_qualification_when_smoke_fails(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            lock = {"name": "test-workspace", "release": "test-release", "images": {}, "profile": "ul-prb-cap-v1"}
            cli_module.load_workspace = lambda _workspace: (workspace, lock, {})
            cli_module.verify = lambda _args: 3
            qualification_calls = []
            cli_module.bridge_gate = lambda _args: qualification_calls.append("qualify") or 0
            args = SimpleNamespace(workspace=workspace, controller="fixed", entrypoint=None, enable_control=True, teardown=False)

            self.assertEqual(cli_module.run_model(args), 2)
            self.assertEqual(qualification_calls, [])

    def test_model_rejects_invalid_entrypoint_before_runtime_start(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            lock = {"name": "test-workspace", "release": "test-release", "images": {}, "profile": "ul-prb-cap-v1"}
            cli_module.load_workspace = lambda _workspace: (workspace, lock, {})
            runtime_calls = []
            cli_module.overlay_command = lambda *_args, **_kwargs: runtime_calls.append(_args) or SimpleNamespace(returncode=0)
            args = SimpleNamespace(
                workspace=workspace,
                controller="model",
                entrypoint="not-an-entrypoint",
                enable_control=False,
                teardown=False,
            )

            self.assertEqual(cli_module.run_model(args), 2)
            self.assertEqual(runtime_calls, [])


    def test_unsupported_bridge_protocol_is_rejected(self) -> None:
        bridge_module = load_bridge_module()
        native_calls = []
        bridge = bridge_module.Bridge(profile="ul-prb-cap-v1", native_control=lambda action: native_calls.append(action))
        result = bridge.handle({"protocol_version": 99, "request_id": "old-client", "operation": "health"})
        self.assertEqual(result["error"], "UNSUPPORTED_PROTOCOL_VERSION")
        self.assertEqual(native_calls, [])

    def test_profile_none_refuses_action_before_native_control(self) -> None:
        bridge_module = load_bridge_module()
        native_calls = []
        bridge = bridge_module.Bridge(profile="none", native_control=lambda action: native_calls.append(action))
        result = bridge.handle(
            {
                "protocol_version": 1,
                "request_id": "request-1",
                "operation": "act",
                "session_id": "session-1",
                "profile_id": "none",
                "action": {"max_ul_prb": 32},
            }
        )
        self.assertEqual(result["error"], "PROFILE_FORBIDS_CONTROL")
        self.assertEqual(native_calls, [])

    def test_control_profile_refuses_action_without_verified_target_binding(self) -> None:
        bridge_module = load_bridge_module()
        native_calls = []
        bridge = bridge_module.Bridge(profile="ul-prb-cap-v1", native_control=lambda action: native_calls.append(action))
        result = bridge.handle(
            {
                "protocol_version": 1,
                "request_id": "request-2",
                "operation": "act",
                "session_id": "session-2",
                "profile_id": "ul-prb-cap-v1",
                "action": {"max_ul_prb": 32},
            }
        )
        self.assertEqual(result["error"], "TARGET_BINDING_REQUIRED")
        self.assertEqual(native_calls, [])

    def test_control_open_returns_target_busy_for_existing_node_lease(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            lease_dir = Path(temp_dir)
            node_id = "2:1:1:123"
            (lease_dir / f"{node_id}.lock").write_text("workspace-a\n", encoding="utf-8")
            bridge = bridge_module.Bridge(
                profile="ul-prb-cap-v1",
                native_control=lambda action: None,
                qualified_binding={
                    "node_id": node_id,
                    "kpm_ue_key": "ue-key-1",
                    "rc_ue_id": 17,
                    "rnti": 4660,
                    "source_seq": 9,
                },
                lease_dir=lease_dir,
                workspace_id="workspace-b",
            )
            result = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "request-3",
                    "operation": "open",
                    "profile_id": "ul-prb-cap-v1",
                    "mode": "control-once",
                }
            )
            self.assertEqual(result["error"], "TARGET_BUSY")
            self.assertEqual((lease_dir / f"{node_id}.lock").read_text(encoding="utf-8"), "workspace-a\n")

    def test_native_discovery_accepts_swig_truthy_boolean(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Path(temp_dir) / "flexric.conf"
            config.write_text("[NEAR-RIC]\n", encoding="utf-8")
            native = bridge_module.NativeFlexric(config)

            class SwigSdk:
                __name__ = "xapp_sdk"
                init_calls = 0

                @classmethod
                def init_with_config(cls, _config_path):
                    cls.init_calls += 1
                    return 1

                @staticmethod
                def conn_e2_nodes():
                    return []

            native.sdk = SwigSdk()
            self.assertEqual(native.discover()["nodes"], [])
            self.assertEqual(native.discover()["nodes"], [])
            self.assertEqual(native.sdk.init_calls, 1)

    def test_native_discovery_projects_kpm_and_rc_styles_without_asn_objects(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Path(temp_dir) / "flexric.conf"
            config.write_text("[NEAR-RIC]\n", encoding="utf-8")
            native = bridge_module.NativeFlexric(config)
            node = SimpleNamespace(
                id=SimpleNamespace(
                    type=2,
                    plmn=SimpleNamespace(mcc=1, mnc=1),
                    nb_id=SimpleNamespace(nb_id=123),
                ),
                ran_func=[SimpleNamespace(id=2), SimpleNamespace(id=3)],
                kpm_report_styles=[
                    SimpleNamespace(
                        style_type=1,
                        action_definition_format=1,
                        indication_header_format=1,
                        indication_message_format=1,
                    ),
                    SimpleNamespace(
                        style_type=4,
                        action_definition_format=4,
                        indication_header_format=1,
                        indication_message_format=3,
                    ),
                ],
                rc_control_styles=[
                    SimpleNamespace(
                        style_type=1,
                        header_format=1,
                        message_format=1,
                        outcome_format=1,
                        action_ids=[1, 100],
                    )
                ],
            )

            class SwigSdk:
                __name__ = "xapp_sdk"

                @staticmethod
                def init_with_config(_config_path):
                    return 1

                @staticmethod
                def conn_e2_nodes():
                    return [node]

            native.sdk = SwigSdk()
            discovered = native.discover()["nodes"][0]
            self.assertEqual(
                discovered["kpm_styles"],
                [
                    {"style_type": 1, "action_definition_format": 1, "indication_header_format": 1, "indication_message_format": 1},
                    {"style_type": 4, "action_definition_format": 4, "indication_header_format": 1, "indication_message_format": 3},
                ],
            )
            self.assertEqual(
                discovered["rc_styles"],
                [{"style_type": 1, "header_format": 1, "message_format": 1, "outcome_format": 1, "action_ids": [1, 100]}],
            )

    def test_qualification_refuses_missing_cell_stream_without_control(self) -> None:
        bridge_module = load_bridge_module()
        native_calls = []

        class Native:
            @staticmethod
            def qualify(_profile):
                return {
                    "ok": False,
                    "error": "CELL_KPM_STREAM_REQUIRED",
                    "cell": [],
                    "ue": [{"source_seq": 1, "kpm_ue_key": "ue-1"}],
                    "control_attempted": False,
                }

        bridge = bridge_module.Bridge(
            profile="ul-prb-cap-v1",
            native=Native(),
            native_control=lambda action: native_calls.append(action),
        )
        result = bridge.handle(
            {
                "protocol_version": 1,
                "request_id": "qualify-missing-cell",
                "operation": "qualify",
                "profile_id": "ul-prb-cap-v1",
            }
        )
        self.assertEqual(result["error"], "CELL_KPM_STREAM_REQUIRED")
        self.assertFalse(result["control_attempted"])
        self.assertEqual(native_calls, [])

    def test_native_qualification_refuses_node_without_cell_kpm_style(self) -> None:
        bridge_module = load_bridge_module()
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        native.discover = lambda: {
            "eligible_node_count": 1,
            "nodes": [
                {
                    "node_id": "2:1:1:3584",
                    "kpm_advertised": True,
                    "rc_advertised": True,
                    "kpm_styles": [
                        {
                            "style_type": 3,
                            "action_definition_format": 3,
                            "indication_header_format": 0,
                            "indication_message_format": 2,
                        }
                    ],
                }
            ],
        }
        result = native.qualify("ul-prb-cap-v1")
        self.assertEqual(result["error"], "CELL_KPM_STREAM_REQUIRED")
        self.assertEqual(result["failed_stage"], "capability")
        self.assertFalse(result["control_attempted"])

    def test_native_qualification_projects_primitive_streams_before_binding_refusal(self) -> None:
        bridge_module = load_bridge_module()
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        native.discover = lambda: {
            "eligible_node_count": 1,
            "nodes": [
                {
                    "node_id": "2:1:1:3584",
                    "kpm_advertised": True,
                    "rc_advertised": True,
                    "kpm_styles": [
                        {"style_type": 1, "action_definition_format": 0, "indication_header_format": 0, "indication_message_format": 0},
                        {"style_type": 4, "action_definition_format": 3, "indication_header_format": 0, "indication_message_format": 2},
                    ],
                }
            ],
        }
        calls = []

        class SwigSdk:
            @staticmethod
            def subscribe_kpm(node_id, stream, callback):
                calls.append((node_id, stream))
                callback(
                    {
                        "source_seq": 11,
                        "timestamp_ms": 1000,
                        "measurements": {"RRU.PrbTotDl": 30},
                    }
                    if stream == "cell"
                    else {"source_seq": 12, "timestamp_ms": 1000, "measurements": {}, "kpm_ue_key": "ue-1"}
                )
                return len(calls)

        native.sdk = SwigSdk()
        result = native.qualify("ul-prb-cap-v1")
        self.assertEqual(calls, [("2:1:1:3584", "cell"), ("2:1:1:3584", "ue")])
        self.assertEqual(result["error"], "TARGET_BINDING_REQUIRED")
        self.assertEqual(result["cell"][0]["source_seq"], 11)
        self.assertEqual(result["cell"][0]["measurements"], {"RRU.PrbTotDl": 30})
        self.assertEqual(result["ue"][0]["source_seq"], 12)
        self.assertEqual(result["ue"][0]["kpm_ue_key"], "ue-1")
        self.assertGreater(result["cell"][0]["bridge_monotonic_receipt_ms"], 0)
        self.assertGreater(result["ue"][0]["bridge_monotonic_receipt_ms"], 0)
        self.assertFalse(result["control_attempted"])

    def test_native_qualification_waits_for_both_async_streams(self) -> None:
        bridge_module = load_bridge_module()
        bridge_module.KPM_OBSERVATION_TIMEOUT_SECONDS = 0.2
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        native.discover = lambda: {
            "eligible_node_count": 1,
            "nodes": [{
                "node_id": "2:1:1:3584",
                "kpm_advertised": True,
                "rc_advertised": True,
                "kpm_styles": [
                    {"style_type": 1, "action_definition_format": 0, "indication_header_format": 0, "indication_message_format": 0},
                    {"style_type": 4, "action_definition_format": 3, "indication_header_format": 0, "indication_message_format": 2},
                ],
            }],
        }

        class SwigSdk:
            @staticmethod
            def subscribe_kpm(_node_id, stream, callback):
                sample = (
                    {"source_seq": 41, "source_seq_origin": "e2_indication", "timestamp_ms": 1000,
                     "measurements": {"RRU.PrbTotDl": 30}}
                    if stream == "cell"
                    else {
                        "source_seq": 42,
                        "timestamp_ms": 1000,
                        "measurements": {"OAI.RNTI": 4660},
                        "kpm_ue_key": "gnb-ran:17",
                        "rc_ue_id": 17,
                        "rnti": 4660,
                        "source_seq_origin": "e2_indication",
                    }
                )
                threading.Timer(0.01, callback, args=(sample,)).start()
                return stream

        native.sdk = SwigSdk()
        result = native.qualify("ul-prb-cap-v1")
        self.assertEqual(result["error"], "MEASUREMENT_POST_UNFROZEN")
        self.assertEqual(result["ue"][0]["rc_ue_id"], 17)
        self.assertEqual(result["ue"][0]["rnti"], 4660)
        self.assertEqual(result["ue"][0]["source_seq_origin"], "e2_indication")

    def test_native_qualification_refuses_malformed_callback_before_control(self) -> None:
        bridge_module = load_bridge_module()
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        native.discover = lambda: {
            "eligible_node_count": 1,
            "nodes": [
                {
                    "node_id": "2:1:1:3584",
                    "kpm_advertised": True,
                    "rc_advertised": True,
                    "kpm_styles": [
                        {"style_type": 1, "action_definition_format": 0, "indication_header_format": 0, "indication_message_format": 0},
                        {"style_type": 4, "action_definition_format": 3, "indication_header_format": 0, "indication_message_format": 2},
                    ],
                }
            ],
        }

        class SwigSdk:
            @staticmethod
            def subscribe_kpm(_node_id, _stream, callback):
                callback({"source_seq": 11})
                return 1

        native.sdk = SwigSdk()
        result = native.qualify("ul-prb-cap-v1")
        self.assertEqual(result["error"], "KPM_CALLBACK_MALFORMED")
        self.assertEqual(result["failed_stage"], "callback")
        self.assertEqual(result["cell"], [])
        self.assertEqual(result["ue"], [])
        self.assertFalse(result["control_attempted"])

    def test_native_qualification_refuses_unverified_source_sequence_without_control(self) -> None:
        bridge_module = load_bridge_module()
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        native.discover = lambda: {
            "eligible_node_count": 1,
            "nodes": [
                {
                    "node_id": "2:1:1:3584",
                    "kpm_advertised": True,
                    "rc_advertised": True,
                    "kpm_styles": [
                        {"style_type": 1, "action_definition_format": 0, "indication_header_format": 0, "indication_message_format": 0},
                        {"style_type": 4, "action_definition_format": 3, "indication_header_format": 0, "indication_message_format": 2},
                    ],
                }
            ],
        }

        class SwigSdk:
            @staticmethod
            def subscribe_kpm(_node_id, stream, callback):
                callback(
                    {"source_seq": 41, "timestamp_ms": 1000, "measurements": {"RRU.PrbTotDl": 30}}
                    if stream == "cell"
                    else {
                        "source_seq": 42,
                        "timestamp_ms": 1000,
                        "measurements": {},
                        "kpm_ue_key": "ue-1",
                        "rc_ue_id": 17,
                        "rnti": 4660,
                    }
                )
                return stream

        native.sdk = SwigSdk()
        result = native.qualify("ul-prb-cap-v1")
        self.assertEqual(result["error"], "SOURCE_SEQUENCE_UNVERIFIED")
        self.assertEqual(result["failed_stage"], "binding")
        self.assertFalse(result["control_attempted"])

    def test_native_qualification_refuses_unfrozen_measurement_post_without_control(self) -> None:
        bridge_module = load_bridge_module()
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        native.discover = lambda: {
            "eligible_node_count": 1,
            "nodes": [
                {
                    "node_id": "2:1:1:3584",
                    "kpm_advertised": True,
                    "rc_advertised": True,
                    "kpm_styles": [
                        {"style_type": 1, "action_definition_format": 0, "indication_header_format": 0, "indication_message_format": 0},
                        {"style_type": 4, "action_definition_format": 3, "indication_header_format": 0, "indication_message_format": 2},
                    ],
                }
            ],
        }
        subscriptions = []

        class SwigSdk:
            @staticmethod
            def subscribe_kpm(node_id, stream, callback):
                subscriptions.append((node_id, stream))
                callback(
                    {"source_seq": 41, "source_seq_origin": "e2_indication", "timestamp_ms": 1000,
                     "measurements": {"RRU.PrbTotDl": 30}}
                    if stream == "cell"
                    else {
                        "source_seq": 42,
                        "timestamp_ms": 1000,
                        "measurements": {},
                        "kpm_ue_key": "ue-1",
                        "rc_ue_id": 17,
                        "rnti": 4660,
                        "source_seq_origin": "e2_indication",
                    }
                )
                return stream

        native.sdk = SwigSdk()

        result = native.qualify("ul-prb-cap-v1")

        self.assertEqual(subscriptions, [("2:1:1:3584", "cell"), ("2:1:1:3584", "ue")])
        self.assertEqual(result["failed_stage"], "qualification")
        self.assertFalse(result["control_attempted"])
        self.assertEqual(result["error"], "MEASUREMENT_POST_UNFROZEN")
        self.assertEqual(result["measurement_post"]["event_time_origin"], "e2_indication_collectStartTime_ms")
        self.assertEqual(result["measurement_post"]["valid_paired_samples"], 1)

    def test_native_qualification_pairs_frozen_samples_by_event_time_not_callback_order(self) -> None:
        bridge_module = load_bridge_module()
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        styles = [
            {"style_type": 1, "action_definition_format": 0, "indication_header_format": 0, "indication_message_format": 0},
            {"style_type": 4, "action_definition_format": 3, "indication_header_format": 0, "indication_message_format": 2},
        ]
        native.measurement_post = {
            "status": "FROZEN", "freshness_window_ms": 10, "cell_ue_max_skew_ms": 0, "min_valid_paired_samples": 2,
            "fingerprint": {"node_id": "2:1:1:3584", "kpm_styles": styles, "cell_metrics": ["RRU.PrbTotDl"],
                            "ue_metrics": ["OAI.RNTI"], "event_time_origin": "e2_indication_collectStartTime_ms"},
        }
        native.discover = lambda: {"eligible_node_count": 1, "nodes": [{"node_id": "2:1:1:3584", "kpm_advertised": True,
            "rc_advertised": True, "kpm_styles": styles}]}

        class SwigSdk:
            @staticmethod
            def subscribe_kpm(_node_id, stream, callback):
                for timestamp_ms in ([2000, 1000] if stream == "cell" else [1000, 2000]):
                    callback({"source_seq": timestamp_ms, "source_seq_origin": "e2_indication", "timestamp_ms": timestamp_ms,
                              "measurements": {"RRU.PrbTotDl": 30} if stream == "cell" else {"OAI.RNTI": 4660},
                              **({} if stream == "cell" else {"kpm_ue_key": "gnb-ran:17", "rc_ue_id": 17, "rnti": 4660})})
                return stream

        native.sdk = SwigSdk()
        self.assertTrue(native.qualify("ul-prb-cap-v1")["ok"])

    def test_native_qualification_accepts_matching_frozen_measurement_post(self) -> None:
        bridge_module = load_bridge_module()
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        styles = [
            {"style_type": 1, "action_definition_format": 0, "indication_header_format": 0, "indication_message_format": 0},
            {"style_type": 4, "action_definition_format": 3, "indication_header_format": 0, "indication_message_format": 2},
        ]
        native.measurement_post = {
            "status": "FROZEN",
            "freshness_window_ms": 10,
            "cell_ue_max_skew_ms": 1,
            "min_valid_paired_samples": 1,
            "fingerprint": {
                "node_id": "2:1:1:3584",
                "kpm_styles": styles,
                "cell_metrics": ["RRU.PrbTotDl"],
                "ue_metrics": ["OAI.RNTI"],
                "event_time_origin": "e2_indication_collectStartTime_ms",
            },
        }
        native.discover = lambda: {
            "eligible_node_count": 1,
            "nodes": [{
                "node_id": "2:1:1:3584",
                "kpm_advertised": True,
                "rc_advertised": True,
                "kpm_styles": styles,
            }],
        }

        class SwigSdk:
            @staticmethod
            def subscribe_kpm(_node_id, stream, callback):
                callback(
                    {
                        "source_seq": 41,
                        "source_seq_origin": "e2_indication",
                        "timestamp_ms": 1000,
                        "measurements": {"RRU.PrbTotDl": 30},
                    }
                    if stream == "cell"
                    else {
                        "source_seq": 42,
                        "source_seq_origin": "e2_indication",
                        "timestamp_ms": 1001,
                        "measurements": {"OAI.RNTI": 4660},
                        "kpm_ue_key": "gnb-ran:17",
                        "rc_ue_id": 17,
                        "rnti": 4660,
                    }
                )
                return stream

        native.sdk = SwigSdk()
        result = native.qualify("ul-prb-cap-v1")

        self.assertTrue(result["ok"])
        self.assertEqual(result["verified_target_binding"], {
            "node_id": "2:1:1:3584",
            "kpm_ue_key": "gnb-ran:17",
            "rc_ue_id": 17,
            "rnti": 4660,
            "source_seq": 42,
            "source_seq_origin": "e2_indication",
        })
        self.assertEqual(result["measurement_post"]["valid_paired_samples"], 1)
        self.assertFalse(result["control_attempted"])

    def test_native_qualification_refuses_frozen_policy_skew_at_threshold_plus_one(self) -> None:
        bridge_module = load_bridge_module()
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        styles = [
            {"style_type": 1, "action_definition_format": 0, "indication_header_format": 0, "indication_message_format": 0},
            {"style_type": 4, "action_definition_format": 3, "indication_header_format": 0, "indication_message_format": 2},
        ]
        native.measurement_post = {
            "status": "FROZEN", "freshness_window_ms": 10, "cell_ue_max_skew_ms": 1, "min_valid_paired_samples": 1,
            "fingerprint": {
                "node_id": "2:1:1:3584", "kpm_styles": styles, "cell_metrics": ["RRU.PrbTotDl"],
                "ue_metrics": ["OAI.RNTI"], "event_time_origin": "e2_indication_collectStartTime_ms",
            },
        }
        native.discover = lambda: {"eligible_node_count": 1, "nodes": [{
            "node_id": "2:1:1:3584", "kpm_advertised": True, "rc_advertised": True, "kpm_styles": styles,
        }]}

        class SwigSdk:
            @staticmethod
            def subscribe_kpm(_node_id, stream, callback):
                callback(
                    {"source_seq": 1, "source_seq_origin": "e2_indication", "timestamp_ms": 1000, "measurements": {"RRU.PrbTotDl": 30}}
                    if stream == "cell" else {
                        "source_seq": 2, "source_seq_origin": "e2_indication", "timestamp_ms": 1002,
                        "measurements": {"OAI.RNTI": 4660}, "kpm_ue_key": "gnb-ran:17", "rc_ue_id": 17, "rnti": 4660,
                    }
                )
                return stream

        native.sdk = SwigSdk()
        result = native.qualify("ul-prb-cap-v1")
        self.assertEqual(result["error"], "CELL_UE_SKEW_EXCEEDED")
        self.assertEqual(result["failed_stage"], "alignment")
        self.assertFalse(result["control_attempted"])

    def test_native_qualification_refuses_frozen_policy_freshness_at_threshold_plus_one(self) -> None:
        bridge_module = load_bridge_module()
        timestamps = iter((100, 100, 102))
        bridge_module.monotonic_ms = lambda: next(timestamps)
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        styles = [
            {"style_type": 1, "action_definition_format": 0, "indication_header_format": 0, "indication_message_format": 0},
            {"style_type": 4, "action_definition_format": 3, "indication_header_format": 0, "indication_message_format": 2},
        ]
        native.measurement_post = {
            "status": "FROZEN", "freshness_window_ms": 1, "cell_ue_max_skew_ms": 1, "min_valid_paired_samples": 1,
            "fingerprint": {"node_id": "2:1:1:3584", "kpm_styles": styles, "cell_metrics": ["RRU.PrbTotDl"],
                            "ue_metrics": ["OAI.RNTI"], "event_time_origin": "e2_indication_collectStartTime_ms"},
        }
        native.discover = lambda: {"eligible_node_count": 1, "nodes": [{
            "node_id": "2:1:1:3584", "kpm_advertised": True, "rc_advertised": True, "kpm_styles": styles,
        }]}

        class SwigSdk:
            @staticmethod
            def subscribe_kpm(_node_id, stream, callback):
                callback(
                    {"source_seq": 1, "source_seq_origin": "e2_indication", "timestamp_ms": 1000, "measurements": {"RRU.PrbTotDl": 30}}
                    if stream == "cell" else {"source_seq": 2, "source_seq_origin": "e2_indication", "timestamp_ms": 1000,
                                                "measurements": {"OAI.RNTI": 4660}, "kpm_ue_key": "gnb-ran:17", "rc_ue_id": 17, "rnti": 4660}
                )
                return stream

        native.sdk = SwigSdk()
        result = native.qualify("ul-prb-cap-v1")
        self.assertEqual(result["error"], "KPM_FRESHNESS_EXPIRED")
        self.assertEqual(result["failed_stage"], "freshness")
        self.assertFalse(result["control_attempted"])

    def test_native_qualification_refuses_frozen_policy_with_n_minus_one_pairs(self) -> None:
        bridge_module = load_bridge_module()
        bridge_module.KPM_OBSERVATION_TIMEOUT_SECONDS = 0.01
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        styles = [
            {"style_type": 1, "action_definition_format": 0, "indication_header_format": 0, "indication_message_format": 0},
            {"style_type": 4, "action_definition_format": 3, "indication_header_format": 0, "indication_message_format": 2},
        ]
        native.measurement_post = {
            "status": "FROZEN", "freshness_window_ms": 10, "cell_ue_max_skew_ms": 1, "min_valid_paired_samples": 2,
            "fingerprint": {"node_id": "2:1:1:3584", "kpm_styles": styles, "cell_metrics": ["RRU.PrbTotDl"],
                            "ue_metrics": ["OAI.RNTI"], "event_time_origin": "e2_indication_collectStartTime_ms"},
        }
        native.discover = lambda: {"eligible_node_count": 1, "nodes": [{
            "node_id": "2:1:1:3584", "kpm_advertised": True, "rc_advertised": True, "kpm_styles": styles,
        }]}

        class SwigSdk:
            @staticmethod
            def subscribe_kpm(_node_id, stream, callback):
                callback(
                    {"source_seq": 1, "source_seq_origin": "e2_indication", "timestamp_ms": 1000, "measurements": {"RRU.PrbTotDl": 30}}
                    if stream == "cell" else {"source_seq": 2, "source_seq_origin": "e2_indication", "timestamp_ms": 1000,
                                                "measurements": {"OAI.RNTI": 4660}, "kpm_ue_key": "gnb-ran:17", "rc_ue_id": 17, "rnti": 4660}
                )
                return stream

        native.sdk = SwigSdk()
        result = native.qualify("ul-prb-cap-v1")
        self.assertEqual(result["error"], "VALID_PAIRED_SAMPLES_REQUIRED")
        self.assertEqual(result["failed_stage"], "pairing")
        self.assertFalse(result["control_attempted"])

    def test_native_qualification_refuses_frozen_policy_with_unproven_cell_time_origin(self) -> None:
        bridge_module = load_bridge_module()
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        styles = [
            {"style_type": 1, "action_definition_format": 0, "indication_header_format": 0, "indication_message_format": 0},
            {"style_type": 4, "action_definition_format": 3, "indication_header_format": 0, "indication_message_format": 2},
        ]
        native.measurement_post = {
            "status": "FROZEN", "freshness_window_ms": 10, "cell_ue_max_skew_ms": 1, "min_valid_paired_samples": 1,
            "fingerprint": {"node_id": "2:1:1:3584", "kpm_styles": styles, "cell_metrics": ["RRU.PrbTotDl"],
                            "ue_metrics": ["OAI.RNTI"], "event_time_origin": "e2_indication_collectStartTime_ms"},
        }
        native.discover = lambda: {"eligible_node_count": 1, "nodes": [{
            "node_id": "2:1:1:3584", "kpm_advertised": True, "rc_advertised": True, "kpm_styles": styles,
        }]}

        class SwigSdk:
            @staticmethod
            def subscribe_kpm(_node_id, stream, callback):
                callback(
                    {"source_seq": 1, "timestamp_ms": 1000, "measurements": {"RRU.PrbTotDl": 30}}
                    if stream == "cell" else {"source_seq": 2, "source_seq_origin": "e2_indication", "timestamp_ms": 1000,
                                                "measurements": {"OAI.RNTI": 4660}, "kpm_ue_key": "gnb-ran:17", "rc_ue_id": 17, "rnti": 4660}
                )
                return stream

        native.sdk = SwigSdk()
        result = native.qualify("ul-prb-cap-v1")
        self.assertEqual(result["error"], "KPM_TIME_ORIGIN_UNPROVEN")
        self.assertEqual(result["failed_stage"], "time-origin")
        self.assertFalse(result["control_attempted"])

    def test_native_qualification_refuses_changed_frozen_calibration_fingerprint(self) -> None:
        bridge_module = load_bridge_module()
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        styles = [
            {"style_type": 1, "action_definition_format": 0, "indication_header_format": 0, "indication_message_format": 0},
            {"style_type": 4, "action_definition_format": 3, "indication_header_format": 0, "indication_message_format": 2},
        ]
        native.measurement_post = {
            "status": "FROZEN", "freshness_window_ms": 10, "cell_ue_max_skew_ms": 1, "min_valid_paired_samples": 1,
            "fingerprint": {"node_id": "2:1:1:3584", "kpm_styles": styles, "cell_metrics": ["RRU.PrbTotDl"],
                            "ue_metrics": ["OAI.RNTI", "DRB.UEThpUl"], "event_time_origin": "e2_indication_collectStartTime_ms"},
        }
        native.discover = lambda: {"eligible_node_count": 1, "nodes": [{
            "node_id": "2:1:1:3584", "kpm_advertised": True, "rc_advertised": True, "kpm_styles": styles,
        }]}

        class SwigSdk:
            @staticmethod
            def subscribe_kpm(_node_id, stream, callback):
                callback(
                    {"source_seq": 1, "source_seq_origin": "e2_indication", "timestamp_ms": 1000, "measurements": {"RRU.PrbTotDl": 30}}
                    if stream == "cell" else {"source_seq": 2, "source_seq_origin": "e2_indication", "timestamp_ms": 1000,
                                                "measurements": {"OAI.RNTI": 4660}, "kpm_ue_key": "gnb-ran:17", "rc_ue_id": 17, "rnti": 4660}
                )
                return stream

        native.sdk = SwigSdk()
        result = native.qualify("ul-prb-cap-v1")
        self.assertEqual(result["error"], "CALIBRATION_FINGERPRINT_CHANGED")
        self.assertEqual(result["failed_stage"], "fingerprint")
        self.assertFalse(result["control_attempted"])

    def test_unsafe_journal_blocks_new_control_until_recovery(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            journal = root / "control_journal.json"
            journal.write_text('{"state":"ROLLBACK_UNCONFIRMED"}\n', encoding="utf-8")
            native_calls = []
            bridge = bridge_module.Bridge(
                profile="ul-prb-cap-v1",
                native_control=lambda action: native_calls.append(action),
                qualified_binding={"node_id": "node-a", "kpm_ue_key": "ue-1", "rc_ue_id": 17, "rnti": 4660, "source_seq": 9},
                lease_dir=root / "leases",
                workspace_id="workspace-b",
                journal_path=journal,
            )
            result = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "request-4",
                    "operation": "open",
                    "profile_id": "ul-prb-cap-v1",
                    "mode": "control-once",
                }
            )
            self.assertEqual(result["error"], "RECOVERY_REQUIRED")
            self.assertEqual(native_calls, [])
            self.assertFalse((root / "leases/node-a.lock").exists())

    def test_control_open_persists_lease_acquired_state(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            journal = root / "control_journal.json"
            bridge = bridge_module.Bridge(
                profile="ul-prb-cap-v1",
                qualified_binding={"node_id": "node-a", "kpm_ue_key": "ue-1", "rc_ue_id": 17, "rnti": 4660, "source_seq": 9},
                lease_dir=root / "leases",
                workspace_id="workspace-a",
                journal_path=journal,
            )
            result = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "lease-journal",
                    "operation": "open",
                    "profile_id": "ul-prb-cap-v1",
                    "mode": "control-once",
                }
            )
            self.assertTrue(result["ok"])
            self.assertEqual(json.loads(journal.read_text(encoding="utf-8"))["state"], "LEASE_ACQUIRED")

    def test_control_once_accepts_upper_contract_bound_with_required_proofs(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            calls = []

            def native_control(action):
                calls.append(action)
                return {"acknowledged": True, "gnb_apply_marker": True, "later_kpm": True}

            bridge = bridge_module.Bridge(
                profile="ul-prb-cap-v1",
                native_control=native_control,
                qualified_binding={"node_id": "node-a", "kpm_ue_key": "ue-1", "rc_ue_id": 17, "rnti": 4660, "source_seq": 9},
                lease_dir=root / "leases",
                workspace_id="workspace-a",
                journal_path=root / "control_journal.json",
            )
            opened = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "open-control",
                    "operation": "open",
                    "profile_id": "ul-prb-cap-v1",
                    "mode": "control-once",
                }
            )
            result = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "act-control",
                    "operation": "act",
                    "profile_id": "ul-prb-cap-v1",
                    "session_id": opened["session_id"],
                    "action": {"max_ul_prb": 275},
                }
            )
            self.assertTrue(result["ok"])
            self.assertEqual([call["phase"] for call in calls], ["baseline", "candidate", "restore"])
            self.assertEqual([call["max_ul_prb"] for call in calls], [0, 275, 0])
            self.assertEqual(json.loads((root / "control_journal.json").read_text(encoding="utf-8"))["state"], "COMPLETED")

    def test_control_once_refuses_out_of_contract_candidate_before_native_control(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            native_calls = []
            bridge = bridge_module.Bridge(
                profile="ul-prb-cap-v1",
                native_control=lambda action: native_calls.append(action),
                qualified_binding={"node_id": "node-a", "kpm_ue_key": "ue-1", "rc_ue_id": 17, "rnti": 4660, "source_seq": 9},
                lease_dir=root / "leases",
                workspace_id="workspace-a",
                journal_path=root / "control_journal.json",
            )
            opened = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "open-out-of-range",
                    "operation": "open",
                    "profile_id": "ul-prb-cap-v1",
                    "mode": "control-once",
                }
            )
            result = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "act-out-of-range",
                    "operation": "act",
                    "profile_id": "ul-prb-cap-v1",
                    "session_id": opened["session_id"],
                    "action": {"max_ul_prb": 276},
                }
            )
            self.assertEqual(result["error"], "CONTRACT_VALIDATION_FAILED")
            self.assertEqual(native_calls, [])

    def test_control_once_locks_target_after_unconfirmed_restore(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            calls = []

            def native_control(action):
                calls.append(action)
                if action["phase"] in {"candidate", "restore"}:
                    return {"acknowledged": True, "gnb_apply_marker": False, "later_kpm": False}
                return {"acknowledged": True, "gnb_apply_marker": True, "later_kpm": True}

            binding = {"node_id": "node-a", "kpm_ue_key": "ue-1", "rc_ue_id": 17, "rnti": 4660, "source_seq": 9}
            journal = root / "control_journal.json"
            bridge = bridge_module.Bridge(
                profile="ul-prb-cap-v1",
                native_control=native_control,
                qualified_binding=binding,
                lease_dir=root / "leases",
                workspace_id="workspace-a",
                journal_path=journal,
            )
            opened = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "open-rollback",
                    "operation": "open",
                    "profile_id": "ul-prb-cap-v1",
                    "mode": "control-once",
                }
            )
            result = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "act-rollback",
                    "operation": "act",
                    "profile_id": "ul-prb-cap-v1",
                    "session_id": opened["session_id"],
                    "action": {"max_ul_prb": 32},
                }
            )
            self.assertEqual(result["error"], "ROLLBACK_UNCONFIRMED")
            self.assertEqual([call["phase"] for call in calls], ["baseline", "candidate", "restore"])
            self.assertEqual(json.loads(journal.read_text(encoding="utf-8"))["state"], "ROLLBACK_UNCONFIRMED")

            blocked = bridge_module.Bridge(
                profile="ul-prb-cap-v1",
                qualified_binding=binding,
                lease_dir=root / "leases",
                workspace_id="workspace-b",
                journal_path=journal,
            ).handle(
                {
                    "protocol_version": 1,
                    "request_id": "open-blocked",
                    "operation": "open",
                    "profile_id": "ul-prb-cap-v1",
                    "mode": "control-once",
                }
            )
            self.assertEqual(blocked["error"], "RECOVERY_REQUIRED")

    def test_recover_proved_baseline_clears_unconfirmed_target_lock(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            calls = []

            def native_control(action):
                calls.append(action)
                if action["phase"] == "recovery":
                    return {"acknowledged": True, "gnb_apply_marker": True, "later_kpm": False}
                if action["phase"] in {"candidate", "restore"}:
                    return {"acknowledged": True, "gnb_apply_marker": False, "later_kpm": False}
                return {"acknowledged": True, "gnb_apply_marker": True, "later_kpm": True}

            binding = {"node_id": "node-a", "kpm_ue_key": "ue-1", "rc_ue_id": 17, "rnti": 4660, "source_seq": 9}
            journal = root / "control_journal.json"
            bridge = bridge_module.Bridge(
                profile="ul-prb-cap-v1",
                native_control=native_control,
                qualified_binding=binding,
                lease_dir=root / "leases",
                workspace_id="workspace-a",
                journal_path=journal,
            )
            opened = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "open-recovery",
                    "operation": "open",
                    "profile_id": "ul-prb-cap-v1",
                    "mode": "control-once",
                }
            )
            bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "act-recovery",
                    "operation": "act",
                    "profile_id": "ul-prb-cap-v1",
                    "session_id": opened["session_id"],
                    "action": {"max_ul_prb": 32},
                }
            )
            result = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "recover-target",
                    "operation": "recover",
                    "profile_id": "ul-prb-cap-v1",
                }
            )
            self.assertTrue(result["ok"])
            self.assertEqual(json.loads(journal.read_text(encoding="utf-8"))["state"], "RECOVERED")
            self.assertFalse((root / "leases/node-a.lock").exists())
            self.assertEqual([call["phase"] for call in calls], ["baseline", "candidate", "restore", "recovery"])

    def test_help_is_chinese_and_does_not_contact_docker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            docker_marker = root / "docker-called"
            fake_docker = fake_bin / "docker"
            fake_docker.write_text(f"#!/usr/bin/env bash\ntouch {docker_marker}\n", encoding="utf-8")
            fake_docker.chmod(0o755)
            result = subprocess.run(
                [str(CLI), "init", "--help"],
                text=True,
                capture_output=True,
                env={**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}"},
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("必要參數", result.stdout)
            self.assertIn("--workspace-root", result.stdout)
            self.assertIn("副作用", result.stdout)
            self.assertIn("下一步", result.stdout)
            self.assertFalse(docker_marker.exists())

    def test_build_release_refuses_existing_immutable_tag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            build_marker = root / "build-called"
            fake_docker = fake_bin / "docker"
            fake_docker.write_text(
                "#!/usr/bin/env python3\n"
                "import pathlib, sys\n"
                f"marker = pathlib.Path({str(build_marker)!r})\n"
                "if sys.argv[1:3] == ['image', 'inspect']:\n"
                "    print('sha256:already-exists'); raise SystemExit(0)\n"
                "if sys.argv[1] == 'build': marker.touch()\n"
                "raise SystemExit(99)\n",
                encoding="utf-8",
            )
            fake_docker.chmod(0o755)
            result = subprocess.run(
                [str(CLI), "build-release", "--release", "1.0.0"],
                text=True,
                capture_output=True,
                env={**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}"},
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("immutable tag 已存在", result.stderr)
            self.assertFalse(build_marker.exists())

    def test_build_release_refuses_unsafe_release_before_docker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            docker_marker = root / "docker-called"
            fake_docker = fake_bin / "docker"
            fake_docker.write_text(f"#!/usr/bin/env bash\ntouch {docker_marker}\n", encoding="utf-8")
            fake_docker.chmod(0o755)
            result = subprocess.run(
                [str(CLI), "build-release", "--release", "../../escape"],
                text=True,
                capture_output=True,
                env={**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}"},
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("release 名稱", result.stderr)
            self.assertFalse(docker_marker.exists())

    def test_init_refuses_existing_workspace_before_docker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            workspace = root / "tag_scheduler_dqn"
            workspace.mkdir()
            sentinel = workspace / "keep.txt"
            sentinel.write_text("keep\n", encoding="utf-8")

            fake_bin = root / "bin"
            fake_bin.mkdir()
            docker_marker = root / "docker-called"
            fake_docker = fake_bin / "docker"
            fake_docker.write_text(
                f"#!/usr/bin/env bash\ntouch {docker_marker}\nexit 99\n",
                encoding="utf-8",
            )
            fake_docker.chmod(0o755)

            result = subprocess.run(
                [
                    str(CLI),
                    "init",
                    "--name",
                    "tag_scheduler_dqn",
                    "--workspace-root",
                    str(root),
                    "--compose",
                    str(root / "missing-compose.yaml"),
                    "--runtime",
                    "cpu",
                    "--profile",
                    "none",
                    "--release",
                    "1.0.0",
                ],
                text=True,
                capture_output=True,
                env={**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}"},
                check=False,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("workspace 已存在", result.stderr)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")
            self.assertFalse(docker_marker.exists())

    def test_init_refuses_missing_compose_without_creating_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            docker_marker = root / "docker-called"
            fake_docker = fake_bin / "docker"
            fake_docker.write_text(
                f"#!/usr/bin/env bash\ntouch {docker_marker}\nexit 99\n",
                encoding="utf-8",
            )
            fake_docker.chmod(0o755)

            result = subprocess.run(
                [
                    str(CLI),
                    "init",
                    "--name",
                    "tag_scheduler_dqn",
                    "--workspace-root",
                    str(root),
                    "--compose",
                    str(root / "missing-compose.yaml"),
                    "--runtime",
                    "cpu",
                    "--profile",
                    "none",
                    "--release",
                    "1.0.0",
                ],
                text=True,
                capture_output=True,
                env={**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}"},
                check=False,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("compose 檔案不存在", result.stderr)
            self.assertFalse((root / "tag_scheduler_dqn").exists())
            self.assertFalse(docker_marker.exists())

    def test_init_refuses_ambiguous_ric_services_without_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            compose = root / "simulator.yaml"
            compose.write_text("services: {}\n", encoding="utf-8")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake_docker = fake_bin / "docker"
            model = {
                "name": "fixture",
                "networks": {"fabric": {"name": "external-net", "external": True}},
                "services": {
                    "ric-a": {"healthcheck": {"test": ["CMD-SHELL", "pgrep nearRT-RIC"]}, "networks": {"fabric": {}}},
                    "ric-b": {"healthcheck": {"test": ["CMD-SHELL", "pgrep nearRT-RIC"]}, "networks": {"fabric": {}}},
                    "ran": {"healthcheck": {"test": ["CMD-SHELL", "pgrep nr-softmodem"]}, "networks": {"fabric": {}}},
                },
            }
            fake_docker.write_text(
                "#!/usr/bin/env python3\nimport json\n"
                f"print(json.dumps({model!r}))\n",
                encoding="utf-8",
            )
            fake_docker.chmod(0o755)
            result = subprocess.run(
                [str(CLI), "init", "--name", "ambiguous", "--workspace-root", str(root), "--compose", str(compose), "--runtime", "cpu", "--profile", "none", "--release", "1.0.0"],
                text=True,
                capture_output=True,
                env={**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}"},
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("無法唯一解析 RIC/gNB service", result.stderr)
            self.assertFalse((root / "ambiguous").exists())

    def test_init_resolves_services_and_writes_isolated_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            compose = root / "simulator.yaml"
            compose.write_text("services: {}\n", encoding="utf-8")
            flexric_config = root / "flexric.conf"
            flexric_config.write_text("[NEAR-RIC]\n", encoding="utf-8")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake_docker = fake_bin / "docker"
            compose_model = {
                "name": "fixture",
                "networks": {"fabric": {"name": "resolved-external-net", "external": True}},
                "services": {
                    "ric-alpha": {
                        "healthcheck": {"test": ["CMD-SHELL", "pgrep nearRT-RIC"]},
                        "networks": {"fabric": {}},
                        "volumes": [{"type": "bind", "source": str(flexric_config), "target": "/usr/local/etc/flexric/flexric.conf"}],
                    },
                    "ran-alpha": {
                        "healthcheck": {"test": ["CMD-SHELL", "pgrep nr-softmodem"]},
                        "networks": {"fabric": {}},
                    },
                },
            }
            fake_docker.write_text(
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                f"model = {compose_model!r}\n"
                "if sys.argv[1] == 'compose':\n"
                "    print(json.dumps(model)); raise SystemExit(0)\n"
                "if sys.argv[1:3] == ['image', 'inspect']:\n"
                "    tag = sys.argv[3]\n"
                "    print('sha256:bridge' if 'bridge' in tag else 'sha256:runtime'); raise SystemExit(0)\n"
                "raise SystemExit(98)\n",
                encoding="utf-8",
            )
            fake_docker.chmod(0o755)

            result = subprocess.run(
                [
                    str(CLI),
                    "init",
                    "--name",
                    "tag_scheduler_dqn",
                    "--workspace-root",
                    str(root),
                    "--compose",
                    str(compose),
                    "--runtime",
                    "cpu",
                    "--profile",
                    "ul-prb-cap-v1",
                    "--release",
                    "1.0.0",
                ],
                text=True,
                capture_output=True,
                env={**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}"},
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            workspace = root / "tag_scheduler_dqn"
            lock = json.loads((workspace / "workspace.lock.json").read_text(encoding="utf-8"))
            overlay = json.loads((workspace / "compose.overlay.json").read_text(encoding="utf-8"))
            self.assertEqual(lock["resolved"]["ric_service"], "ric-alpha")
            self.assertEqual(lock["resolved"]["gnb_service"], "ran-alpha")
            self.assertEqual(lock["resolved"]["network_name"], "resolved-external-net")
            self.assertEqual(lock["images"]["runtime"]["id"], "sha256:runtime")
            self.assertEqual(lock["images"]["bridge"]["id"], "sha256:bridge")
            self.assertEqual(overlay["services"]["drl-runtime"]["network_mode"], "none")
            runtime_state_mount = next(
                mount
                for mount in overlay["services"]["drl-runtime"]["volumes"]
                if mount["target"] == "/run/redcap-drl"
            )
            self.assertTrue(runtime_state_mount["read_only"])
            self.assertEqual(overlay["services"]["flexric-bridge"]["user"], f"{os.getuid()}:{os.getgid()}")
            self.assertNotIn("privileged", json.dumps(overlay))
            self.assertNotIn("docker.sock", json.dumps(overlay))
            self.assertEqual(overlay["networks"]["simulator"]["name"], "resolved-external-net")
            flexric_mount = next(
                mount
                for mount in overlay["services"]["flexric-bridge"]["volumes"]
                if mount["target"] == "/usr/local/etc/flexric/flexric.conf"
            )
            self.assertTrue(flexric_mount["read_only"])

    def test_init_writes_unfrozen_measurement_post_for_bridge_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            compose = root / "simulator.yaml"
            compose.write_text("services: {}\n", encoding="utf-8")
            flexric_config = root / "flexric.conf"
            flexric_config.write_text("[NEAR-RIC]\n", encoding="utf-8")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake_docker = fake_bin / "docker"
            compose_model = {
                "name": "fixture",
                "networks": {"fabric": {"name": "resolved-external-net", "external": True}},
                "services": {
                    "ric-alpha": {
                        "healthcheck": {"test": ["CMD-SHELL", "pgrep nearRT-RIC"]},
                        "networks": {"fabric": {}},
                        "volumes": [{"type": "bind", "source": str(flexric_config), "target": "/usr/local/etc/flexric/flexric.conf"}],
                    },
                    "ran-alpha": {
                        "healthcheck": {"test": ["CMD-SHELL", "pgrep nr-softmodem"]},
                        "networks": {"fabric": {}},
                    },
                },
            }
            fake_docker.write_text(
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                f"model = {compose_model!r}\n"
                "if sys.argv[1] == 'compose':\n"
                "    print(json.dumps(model)); raise SystemExit(0)\n"
                "if sys.argv[1:3] == ['image', 'inspect']:\n"
                "    tag = sys.argv[3]\n"
                "    print('sha256:bridge' if 'bridge' in tag else 'sha256:runtime'); raise SystemExit(0)\n"
                "raise SystemExit(98)\n",
                encoding="utf-8",
            )
            fake_docker.chmod(0o755)

            result = subprocess.run(
                [
                    str(CLI), "init", "--name", "tag_scheduler_dqn", "--workspace-root", str(root),
                    "--compose", str(compose), "--runtime", "cpu", "--profile", "ul-prb-cap-v1",
                    "--release", "1.0.0",
                ],
                text=True,
                capture_output=True,
                env={**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}"},
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            workspace = root / "tag_scheduler_dqn"
            lock_path = workspace / "workspace.lock.json"
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            overlay = json.loads((workspace / "compose.overlay.json").read_text(encoding="utf-8"))
            bridge = overlay["services"]["flexric-bridge"]
            runtime = overlay["services"]["drl-runtime"]
            failures = []
            if lock.get("measurement_post", {}).get("status") != "UNFROZEN":
                failures.append("workspace.lock.json measurement_post.status is not UNFROZEN")
            command_text = json.dumps(bridge.get("command", []))
            if "--workspace-lock" not in command_text:
                failures.append("flexric-bridge command lacks a workspace-lock path argument")
            lock_mounts = [mount for mount in bridge.get("volumes", []) if mount.get("source") == str(lock_path)]
            if len(lock_mounts) != 1 or not lock_mounts[0].get("read_only"):
                failures.append("flexric-bridge lacks one read-only workspace.lock.json bind mount")
            else:
                lock_target = lock_mounts[0]["target"]
                if lock_target not in command_text:
                    failures.append("flexric-bridge command lacks its workspace.lock.json mount target")
                if any(
                    mount.get("source") == str(lock_path) or mount.get("target") == lock_target
                    for mount in runtime.get("volumes", [])
                ):
                    failures.append("drl-runtime receives the workspace.lock.json source or bridge lock target")
            self.assertEqual(failures, [])

    def test_freeze_measurement_post_requires_explicit_calibration_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "frozen-profile"
            run_id = "calibration-run"
            run_dir = workspace / "artifacts/runs" / run_id
            run_dir.mkdir(parents=True)
            lock = {
                "schema_version": 1,
                "name": workspace.name,
                "release": "1.0.12",
                "images": {"runtime": {"id": "sha256:runtime"}, "bridge": {"id": "sha256:bridge"}},
                "profile": "ul-prb-cap-v1",
                "measurement_post": {"status": "UNFROZEN"},
            }
            (workspace / "workspace.lock.json").write_text(json.dumps(lock), encoding="utf-8")
            (workspace / "compose.overlay.json").write_text(json.dumps({}), encoding="utf-8")
            manifest = {
                "run_id": run_id,
                "gates": {
                    "discover-kpm": {"ok": True, "capabilities": {"nodes": [{
                        "node_id": "2:1:1:3584",
                        "kpm_styles": [{"style_type": 1, "action_definition_format": 0, "indication_header_format": 0,
                                        "indication_message_format": 0}],
                    }]}},
                    "qualify-kpm": {
                        "node_id": "2:1:1:3584",
                        "cell": [{"source_seq_origin": "e2_indication", "timestamp_ms": 1000,
                                  "measurements": {"RRU.PrbTotDl": 30}}],
                        "ue": [{"source_seq_origin": "e2_indication", "timestamp_ms": 1001,
                                "measurements": {"OAI.RNTI": 4660}, "kpm_ue_key": "gnb-ran:17",
                                "rc_ue_id": 17, "rnti": 4660}],
                        "measurement_post": {"event_time_origin": "e2_indication_collectStartTime_ms",
                                             "valid_paired_samples": 1, "max_cell_ue_skew_ms": 1,
                                             "max_freshness_age_ms": 1},
                    },
                },
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            result = subprocess.run(
                [
                    str(CLI), "freeze-measurement-post", "--workspace", str(workspace), "--calibration-run", run_id,
                    "--approve-calibration", run_id, "--freshness-window-ms", "5", "--cell-ue-max-skew-ms", "1",
                    "--min-valid-paired-samples", "1",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            frozen = json.loads((workspace / "workspace.lock.json").read_text(encoding="utf-8"))["measurement_post"]
            self.assertEqual(frozen["status"], "FROZEN")
            self.assertEqual(frozen["approved_calibration_run"], run_id)
            self.assertEqual(frozen["fingerprint"]["release"], "1.0.12")
            self.assertEqual(frozen["fingerprint"]["images"], lock["images"])

    def test_init_refuses_compose_without_flexric_config_mount(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            compose = root / "simulator.yaml"
            compose.write_text("services: {}\n", encoding="utf-8")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake_docker = fake_bin / "docker"
            model = {
                "name": "fixture",
                "networks": {"fabric": {"name": "external-net", "external": True}},
                "services": {
                    "ric": {"healthcheck": {"test": ["CMD-SHELL", "pgrep nearRT-RIC"]}, "networks": {"fabric": {}}},
                    "ran": {"healthcheck": {"test": ["CMD-SHELL", "pgrep nr-softmodem"]}, "networks": {"fabric": {}}},
                },
            }
            fake_docker.write_text("#!/usr/bin/env python3\nimport json\n" f"print(json.dumps({model!r}))\n", encoding="utf-8")
            fake_docker.chmod(0o755)
            result = subprocess.run(
                [str(CLI), "init", "--name", "missing-config", "--workspace-root", str(root), "--compose", str(compose), "--runtime", "cpu", "--profile", "none", "--release", "1.0.0"],
                text=True,
                capture_output=True,
                env={**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}"},
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("FlexRIC config", result.stderr)
            self.assertFalse((root / "missing-config").exists())


if __name__ == "__main__":
    unittest.main()
