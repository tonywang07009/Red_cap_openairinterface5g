#!/usr/bin/env python3

from contextlib import redirect_stderr
import io
import os
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
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

    def test_generic_episode_request_refuses_before_runtime_or_control(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            lock = {"name": "test-workspace", "release": "test-release", "images": {}, "profile": "ul-prb-cap-v1"}
            cli_module.load_workspace = lambda _workspace: (workspace, lock, {})
            external_calls = []
            cli_module.verify = lambda _args: external_calls.append("verify") or 0
            cli_module.bridge_gate = lambda _args: external_calls.append("qualify") or 0
            cli_module.overlay_command = lambda *_args: external_calls.append("runtime") or SimpleNamespace(returncode=0)
            args = SimpleNamespace(
                workspace=workspace,
                controller="model",
                entrypoint=None,
                enable_control=True,
                teardown=False,
                episodes=2,
            )
            diagnostic = io.StringIO()
            with redirect_stderr(diagnostic):
                self.assertEqual(cli_module.run_model(args), 2)

            self.assertEqual(external_calls, [])
            self.assertIn("PROFILE_SPECIFICATION_REQUIRED", diagnostic.getvalue())

    def test_validation_candidate_uses_approved_fixed_and_greedy_boundaries(self) -> None:
        cli_module = load_cli_module()

        self.assertEqual(
            cli_module.validation_candidate("fixed", []),
            {"ok": True, "max_ul_prb": 16, "source": "fixed"},
        )
        self.assertEqual(
            cli_module.validation_candidate("greedy", [{"measurements": {"RRU.PrbTotUl": 54}}]),
            {"ok": True, "max_ul_prb": 16, "source": "RRU.PrbTotUl", "ul_prb_utilization_pct": 54.0},
        )
        self.assertEqual(
            cli_module.validation_candidate("greedy", [{"measurements": {"RRU.PrbTotUl": 55}}]),
            {"ok": True, "max_ul_prb": 32, "source": "RRU.PrbTotUl", "ul_prb_utilization_pct": 55.0},
        )
        self.assertEqual(
            cli_module.validation_candidate("greedy", [{"measurements": {"RRU.PrbTotUl": 80}}]),
            {"ok": True, "max_ul_prb": 32, "source": "RRU.PrbTotUl", "ul_prb_utilization_pct": 80.0},
        )
        self.assertEqual(
            cli_module.validation_candidate("greedy", [{"measurements": {"RRU.PrbTotUl": 81}}]),
            {"ok": True, "max_ul_prb": 64, "source": "RRU.PrbTotUl", "ul_prb_utilization_pct": 81.0},
        )

    def test_greedy_candidate_refuses_missing_or_invalid_utilization(self) -> None:
        cli_module = load_cli_module()

        self.assertEqual(
            cli_module.validation_candidate("greedy", [{"measurements": {}}]),
            {"ok": False, "error": "UL_PRB_UTILIZATION_REQUIRED"},
        )
        self.assertEqual(
            cli_module.validation_candidate("greedy", [{"measurements": {"RRU.PrbTotUl": 101}}]),
            {"ok": False, "error": "UL_PRB_UTILIZATION_REQUIRED"},
        )

    def test_gnb_marker_record_projects_only_the_existing_apply_marker(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            proof_path = Path(temp_dir) / "gnb_apply_proof.jsonl"
            excerpt_path = Path(temp_dir) / "gnb_apply_excerpt.log"
            cli_module.monotonic_ms = lambda: 321

            result = cli_module.record_gnb_apply_marker(
                "[MAC] RedCap UL PRB control RNTI 1234 requested 32 effective 32\n",
                proof_path,
                excerpt_path,
            )

            self.assertEqual(
                result,
                {"rnti": 4660, "requested": 32, "effective": 32, "observed_monotonic_ms": 321},
            )
            self.assertEqual(json.loads(proof_path.read_text(encoding="utf-8")), result)
            self.assertIn("requested 32", excerpt_path.read_text(encoding="utf-8"))

    def test_greedy_run_closes_after_apply_proof_failure(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            lock = {"name": "test-workspace", "release": "test-release", "images": {}, "profile": "ul-prb-cap-v1"}
            cli_module.load_workspace = lambda _workspace: (workspace, lock, {})
            cli_module.verify = lambda _args: 0
            cli_module.bridge_gate = lambda _args: (0, {"cell": [{"measurements": {"RRU.PrbTotUl": 55}}]})
            requests = []

            def fake_uds_call(_socket, request, timeout_seconds=5):
                requests.append((request, timeout_seconds))
                if request["operation"] == "open":
                    return {"ok": True, "session_id": "session-1"}
                if request["operation"] == "act":
                    return {"ok": False, "error": "APPLY_PROOF_PROVIDER_REQUIRED"}
                return {"ok": True}

            cli_module.uds_call = fake_uds_call
            collector = object()
            cli_module.start_gnb_marker_collector = lambda *_args: collector
            cli_module.stop_gnb_marker_collector = lambda actual: self.assertIs(actual, collector)
            args = SimpleNamespace(workspace=workspace, controller="greedy", entrypoint=None, enable_control=True, teardown=False)

            self.assertEqual(cli_module.run_model(args), 4)
            self.assertEqual([request["operation"] for request, _timeout in requests], ["open", "act", "close"])
            self.assertEqual(requests[1][0]["action"]["max_ul_prb"], 32)
            self.assertEqual([timeout for _request, timeout in requests], [5, 5, 5])
            run_dir = next((workspace / "artifacts/runs").iterdir())
            events = [json.loads(line) for line in (run_dir / "events.ndjson").read_text(encoding="utf-8").splitlines()]
            self.assertEqual([event["operation"] for event in events], ["open", "act", "close"])

    def test_control_once_refuses_before_uds_when_marker_collector_is_unavailable(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            lock = {"name": "test-workspace", "release": "test-release", "images": {}, "profile": "ul-prb-cap-v1"}
            requests = []
            cli_module.uds_call = lambda _socket, request, timeout_seconds=5: requests.append(request) or {"ok": True}

            self.assertEqual(cli_module.control_once(workspace, lock, {"max_ul_prb": 16}), 4)
            self.assertEqual(requests, [])

    def test_fixed_run_selects_approved_candidate(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            lock = {"name": "test-workspace", "release": "test-release", "images": {}, "profile": "ul-prb-cap-v1"}
            cli_module.load_workspace = lambda _workspace: (workspace, lock, {})
            cli_module.verify = lambda _args: 0
            cli_module.bridge_gate = lambda _args: (0, {"cell": []})
            requests = []

            def fake_uds_call(_socket, request, timeout_seconds=5):
                requests.append((request, timeout_seconds))
                if request["operation"] == "open":
                    return {"ok": True, "session_id": "session-1"}
                return {"ok": True}

            cli_module.uds_call = fake_uds_call
            collector = object()
            cli_module.start_gnb_marker_collector = lambda *_args: collector
            cli_module.stop_gnb_marker_collector = lambda actual: self.assertIs(actual, collector)
            args = SimpleNamespace(workspace=workspace, controller="fixed", entrypoint=None, enable_control=True, teardown=False)

            self.assertEqual(cli_module.run_model(args), 0)
            self.assertEqual([request["operation"] for request, _timeout in requests], ["open", "act", "close"])
            self.assertEqual(requests[1][0]["action"]["max_ul_prb"], 16)

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

    def test_model_without_control_refuses_before_runtime_start(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            lock = {"name": "test-workspace", "release": "test-release", "images": {}, "profile": "ul-prb-cap-v1"}
            cli_module.load_workspace = lambda _workspace: (workspace, lock, {})
            runtime_calls = []
            cli_module.overlay_command = lambda *_args, **_kwargs: runtime_calls.append("runtime") or SimpleNamespace(returncode=0)
            args = SimpleNamespace(
                workspace=workspace,
                controller="model",
                entrypoint="policy:choose",
                enable_control=False,
                teardown=False,
            )

            with redirect_stderr(io.StringIO()) as diagnostic:
                self.assertEqual(cli_module.run_model(args), 2)
            self.assertIn("MODEL_OBSERVATION_REQUIRED", diagnostic.getvalue())
            self.assertEqual(runtime_calls, [])

    def test_model_entrypoint_receives_observation_and_emits_one_json_line(self) -> None:
        runner = REPO_ROOT / "redcap_library/drl_xapp/run_entrypoint.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "policy.py").write_text(
                "def choose(observation):\n"
                "    print('model diagnostic')\n"
                "    assert observation['sample_count'] == 30\n"
                "    return {'max_ul_prb': 32}\n",
                encoding="utf-8",
            )
            observation = root / "observation.json"
            observation.write_text('{"sample_count": 30}\n', encoding="utf-8")
            environment = dict(os.environ, PYTHONPATH=str(root))

            result = subprocess.run(
                [sys.executable, str(runner), "policy:choose", str(observation)],
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, '{"max_ul_prb": 32}\n')
            self.assertIn("model diagnostic", result.stderr)

    def test_model_control_summarizes_30_samples_and_sends_one_candidate(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            lock = {"name": "test-workspace", "release": "test-release", "images": {}, "profile": "ul-prb-cap-v1"}
            cli_module.load_workspace = lambda _workspace: (workspace, lock, {})
            cli_module.verify = lambda _args: 0
            cell = [
                {
                    "timestamp_ms": index + 1,
                    "source_seq_origin": "e2_indication",
                    "measurements": {"RRU.PrbTotUl": index},
                }
                for index in range(30)
            ]
            ue = [
                {"timestamp_ms": index + 1, "source_seq_origin": "e2_indication"}
                for index in range(30)
            ]
            cli_module.bridge_gate = lambda _args: (0, {"cell": cell, "ue": ue})
            runtime_calls = []

            def fake_overlay_command(_workspace, *command, **_kwargs):
                runtime_calls.append(command)
                observation = workspace / "run" / Path(command[-1]).name
                self.assertEqual(json.loads(observation.read_text(encoding="utf-8")), {
                    "profile_id": "ul-prb-cap-v1",
                    "rru_prb_tot_ul_pct": {"latest": 29.0, "max": 29.0, "mean": 14.5, "min": 0.0},
                    "sample_count": 30,
                    "schema_version": 1,
                })
                self.assertEqual(observation.stat().st_mode & 0o777, 0o444)
                return SimpleNamespace(returncode=0, stdout='{"max_ul_prb": 51}\n', stderr="")

            cli_module.overlay_command = fake_overlay_command
            requests = []
            cli_module.uds_call = lambda _socket, request, timeout_seconds=5: (
                requests.append(request)
                or ({"ok": True, "session_id": "session-1"} if request["operation"] == "open" else {"ok": True})
            )
            collector = object()
            cli_module.start_gnb_marker_collector = lambda *_args: collector
            cli_module.stop_gnb_marker_collector = lambda actual: self.assertIs(actual, collector)
            args = SimpleNamespace(
                workspace=workspace,
                controller="model",
                entrypoint="policy:choose",
                enable_control=True,
                teardown=False,
            )

            self.assertEqual(cli_module.run_model(args), 0)
            self.assertEqual(len(runtime_calls), 1)
            self.assertEqual([request["operation"] for request in requests], ["open", "act", "close"])
            self.assertEqual(requests[1]["action"], {"max_ul_prb": 51})

    def test_model_control_refuses_insufficient_samples_or_invalid_candidate_before_uds(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            lock = {"name": "test-workspace", "release": "test-release", "images": {}, "profile": "ul-prb-cap-v1"}
            cli_module.load_workspace = lambda _workspace: (workspace, lock, {})
            cli_module.verify = lambda _args: 0
            cell = [{"timestamp_ms": index + 1, "source_seq_origin": "e2_indication", "measurements": {"RRU.PrbTotUl": 20}}
                    for index in range(29)]
            ue = [{"timestamp_ms": index + 1, "source_seq_origin": "e2_indication"} for index in range(29)]
            cli_module.bridge_gate = lambda _args: (0, {"cell": cell, "ue": ue})
            runtime_calls = []
            uds_calls = []
            cli_module.overlay_command = lambda *_args, **_kwargs: runtime_calls.append("runtime") or SimpleNamespace(
                returncode=0, stdout='{"max_ul_prb": 0}\n', stderr=""
            )
            cli_module.uds_call = lambda *_args, **_kwargs: uds_calls.append("uds") or {"ok": True}
            args = SimpleNamespace(
                workspace=workspace,
                controller="model",
                entrypoint="policy:choose",
                enable_control=True,
                teardown=False,
            )

            with redirect_stderr(io.StringIO()) as diagnostic:
                self.assertEqual(cli_module.run_model(args), 2)
            self.assertIn("MODEL_OBSERVATION_REQUIRED", diagnostic.getvalue())
            self.assertEqual(runtime_calls, [])
            self.assertEqual(uds_calls, [])

            cell.append({"timestamp_ms": 30, "source_seq_origin": "e2_indication", "measurements": {"RRU.PrbTotUl": 20}})
            ue.append({"timestamp_ms": 30, "source_seq_origin": "e2_indication"})
            with redirect_stderr(io.StringIO()) as diagnostic:
                self.assertEqual(cli_module.run_model(args), 2)
            self.assertIn("MODEL_CANDIDATE_REQUIRED", diagnostic.getvalue())
            self.assertEqual(runtime_calls, ["runtime"])
            self.assertEqual(uds_calls, [])

    def test_model_control_rejects_every_non_profile_candidate_before_uds(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            lock = {"name": "test-workspace", "release": "test-release", "images": {}, "profile": "ul-prb-cap-v1"}
            cli_module.load_workspace = lambda _workspace: (workspace, lock, {})
            cli_module.verify = lambda _args: 0
            cell = [{"timestamp_ms": index + 1, "source_seq_origin": "e2_indication", "measurements": {"RRU.PrbTotUl": 20}}
                    for index in range(30)]
            ue = [{"timestamp_ms": index + 1, "source_seq_origin": "e2_indication"} for index in range(30)]
            cli_module.bridge_gate = lambda _args: (0, {"cell": cell, "ue": ue})
            cli_module.uds_call = lambda *_args, **_kwargs: self.fail("invalid model output opened UDS")
            args = SimpleNamespace(
                workspace=workspace,
                controller="model",
                entrypoint="policy:choose",
                enable_control=True,
                teardown=False,
            )

            for output in (
                '{"max_ul_prb": 0}\n',
                '{"max_ul_prb": 52}\n',
                '{"max_ul_prb": true}\n',
                '{"max_ul_prb": 1.0}\n',
                '{"max_ul_prb": "1"}\n',
                '{}\n',
                '{"max_ul_prb": 1, "unexpected": 2}\n',
                '{"max_ul_prb": 1}\nextra\n',
            ):
                cli_module.overlay_command = lambda *_args, output=output, **_kwargs: SimpleNamespace(
                    returncode=0, stdout=output, stderr=""
                )
                with redirect_stderr(io.StringIO()) as diagnostic:
                    self.assertEqual(cli_module.run_model(args), 2)
                self.assertIn("MODEL_CANDIDATE_REQUIRED", diagnostic.getvalue())

    def test_model_control_accepts_lower_profile_boundary(self) -> None:
        cli_module = load_cli_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            lock = {"name": "test-workspace", "release": "test-release", "images": {}, "profile": "ul-prb-cap-v1"}
            cli_module.load_workspace = lambda _workspace: (workspace, lock, {})
            cli_module.verify = lambda _args: 0
            cell = [{"timestamp_ms": index + 1, "source_seq_origin": "e2_indication", "measurements": {"RRU.PrbTotUl": 20}}
                    for index in range(30)]
            ue = [{"timestamp_ms": index + 1, "source_seq_origin": "e2_indication"} for index in range(30)]
            cli_module.bridge_gate = lambda _args: (0, {"cell": cell, "ue": ue})
            cli_module.overlay_command = lambda *_args, **_kwargs: SimpleNamespace(
                returncode=0, stdout='{"max_ul_prb": 1}\n', stderr=""
            )
            requests = []
            cli_module.uds_call = lambda _socket, request, timeout_seconds=5: (
                requests.append(request)
                or ({"ok": True, "session_id": "session-1"} if request["operation"] == "open" else {"ok": True})
            )
            collector = object()
            cli_module.start_gnb_marker_collector = lambda *_args: collector
            cli_module.stop_gnb_marker_collector = lambda actual: self.assertIs(actual, collector)
            args = SimpleNamespace(
                workspace=workspace,
                controller="model",
                entrypoint="policy:choose",
                enable_control=True,
                teardown=False,
            )

            self.assertEqual(cli_module.run_model(args), 0)
            self.assertEqual(requests[1]["action"], {"max_ul_prb": 1})


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

    def test_control_refuses_missing_apply_proof_provider_before_baseline(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bridge = bridge_module.Bridge(
                profile="ul-prb-cap-v1",
                qualified_binding={
                    "node_id": "2:1:1:123",
                    "kpm_ue_key": "ue-key-1",
                    "rc_ue_id": 17,
                    "rnti": 4660,
                    "source_seq": 9,
                },
                lease_dir=root / "leases",
                journal_path=root / "control_journal.json",
            )
            opened = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "open-without-provider",
                    "operation": "open",
                    "profile_id": "ul-prb-cap-v1",
                    "mode": "control-once",
                }
            )
            result = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "act-without-provider",
                    "operation": "act",
                    "profile_id": "ul-prb-cap-v1",
                    "session_id": opened["session_id"],
                    "action": {"max_ul_prb": 32},
                }
            )

            self.assertEqual(result["error"], "APPLY_PROOF_PROVIDER_REQUIRED")
            self.assertEqual(
                json.loads((root / "control_journal.json").read_text(encoding="utf-8"))["state"],
                "LEASE_ACQUIRED",
            )

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

    def test_native_control_ul_prb_preserves_swig_ack_request_id(self) -> None:
        bridge_module = load_bridge_module()
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        node = SimpleNamespace(ran_type=2, mcc=1, mnc=1, node_id=3584, id="native-node")
        calls = []

        class SwigSdk:
            @staticmethod
            def conn_e2_nodes():
                return [node]

            @staticmethod
            def control_redcap_ul_prb_sm(node_id, rc_ue_id, rnti, max_ul_prb):
                calls.append((node_id, rc_ue_id, rnti, max_ul_prb))
                return 37

        native.sdk = SwigSdk()
        result = native.control_ul_prb(
            {"node_id": "2:1:1:3584", "rc_ue_id": 17, "rnti": 4660, "max_ul_prb": 32}
        )

        self.assertEqual(calls, [("native-node", 17, 4660, 32)])
        self.assertEqual(result, {"acknowledged": True, "ric_request_id": 37})

    def test_native_control_ul_prb_refuses_boolean_prb_without_swig_call(self) -> None:
        bridge_module = load_bridge_module()
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        node = SimpleNamespace(ran_type=2, mcc=1, mnc=1, node_id=3584, id="native-node")
        calls = []

        class SwigSdk:
            @staticmethod
            def conn_e2_nodes():
                return [node]

            @staticmethod
            def control_redcap_ul_prb_sm(*args):
                calls.append(args)
                return 37

        native.sdk = SwigSdk()
        result = native.control_ul_prb(
            {"node_id": "2:1:1:3584", "rc_ue_id": 17, "rnti": 4660, "max_ul_prb": True}
        )

        self.assertEqual(result, {"acknowledged": False, "error": "INVALID_CONTROL_ACTION"})
        self.assertEqual(calls, [])

    def test_native_control_ul_prb_refuses_unavailable_node_provider_without_swig_call(self) -> None:
        bridge_module = load_bridge_module()
        native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
        calls = []

        class SwigSdk:
            @staticmethod
            def conn_e2_nodes():
                raise RuntimeError("E2 nodes unavailable")

            @staticmethod
            def control_redcap_ul_prb_sm(*args):
                calls.append(args)
                return 37

        native.sdk = SwigSdk()
        result = native.control_ul_prb(
            {"node_id": "2:1:1:3584", "rc_ue_id": 17, "rnti": 4660, "max_ul_prb": 32}
        )

        self.assertEqual(result, {"acknowledged": False, "error": "NATIVE_CONTROL_UNAVAILABLE"})
        self.assertEqual(calls, [])

    def test_native_proof_combines_ack_marker_and_fresh_kpm_inside_one_second(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            proof_path = Path(temp_dir) / "apply_proof.jsonl"
            proof_path.write_text(
                json.dumps({"rnti": 4660, "requested": 32, "effective": 32, "observed_monotonic_ms": 101}) + "\n",
                encoding="utf-8",
            )
            native = bridge_module.NativeFlexric(Path("/unused/flexric.conf"))
            native.control_ul_prb = lambda _action: {"acknowledged": True, "ric_request_id": 37}
            native.qualify = lambda _profile, observation_timeout_seconds=None: {
                "ok": True,
                "verified_target_binding": {"node_id": "2:1:1:3584", "rc_ue_id": 17, "rnti": 4660},
            }
            timestamps = iter((100, 102, 103, 104))
            bridge_module.monotonic_ms = lambda: next(timestamps)

            result = native.prove_ul_prb(
                {"node_id": "2:1:1:3584", "rc_ue_id": 17, "rnti": 4660, "max_ul_prb": 32},
                "ul-prb-cap-v1",
                proof_path,
            )

            self.assertEqual(result["ric_request_id"], 37)
            self.assertTrue(result["acknowledged"])
            self.assertTrue(result["gnb_apply_marker"])
            self.assertTrue(result["later_kpm"])

    def test_marker_proof_requires_matching_action_within_one_second(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            proof_path = Path(temp_dir) / "apply_proof.jsonl"
            sent_at_ms = bridge_module.monotonic_ms()
            matching = {
                "rnti": 4660,
                "requested": 32,
                "effective": 32,
                "observed_monotonic_ms": sent_at_ms + 10,
                "marker_line": "RedCap UL PRB control RNTI 1234 requested 32 effective 32",
            }
            proof_path.write_text(json.dumps(matching) + "\n", encoding="utf-8")

            result = bridge_module.marker_proof(
                proof_path,
                {"rnti": 4660, "max_ul_prb": 32},
                sent_at_ms,
            )

            self.assertEqual(result, {"gnb_apply_marker": True, "marker": matching})

    def test_marker_proof_refuses_stale_or_mismatched_record(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            proof_path = Path(temp_dir) / "apply_proof.jsonl"
            sent_at_ms = bridge_module.monotonic_ms()
            proof_path.write_text(
                "\n".join(
                    json.dumps(record)
                    for record in (
                        {"rnti": 4660, "requested": 32, "effective": 32, "observed_monotonic_ms": sent_at_ms - 1},
                        {"rnti": 4660, "requested": 16, "effective": 16, "observed_monotonic_ms": sent_at_ms + 10},
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            result = bridge_module.marker_proof(
                proof_path,
                {"rnti": 4660, "max_ul_prb": 32},
                sent_at_ms,
            )

            self.assertEqual(result, {"gnb_apply_marker": False})

    def test_every_control_phase_requires_ack_marker_and_later_kpm(self) -> None:
        bridge_module = load_bridge_module()

        self.assertFalse(
            bridge_module.Bridge._proof_succeeded(
                {"acknowledged": True, "gnb_apply_marker": True, "later_kpm": False}
            )
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

    def test_native_kpm_provenance_uses_e2_indication_sn(self) -> None:
        agent = (REPO_ROOT / "openair2/E2AP/flexric/src/agent/e2_agent.c").read_text(encoding="utf-8")
        event = (REPO_ROOT / "openair2/E2AP/flexric/src/lib/ind_event.h").read_text(encoding="utf-8")
        handoff = (REPO_ROOT / "openair2/E2AP/flexric/src/xApp/msg_handler_xapp.c").read_text(encoding="utf-8")
        copied = (REPO_ROOT / "openair2/E2AP/flexric/src/sm/agent_if/read/sm_ag_if_rd.c").read_text(encoding="utf-8")
        producer = (REPO_ROOT / "openair2/E2AP/flexric/src/xApp/swig/swig_wrapper.cpp").read_text(encoding="utf-8")
        callback = producer[producer.index("static void sm_cb_kpm"):producer.index("int subscribe_kpm")]

        self.assertIn("uint16_t indication_sn;", event)
        self.assertIn("ind.sn = malloc(sizeof(*ind.sn));", agent)
        self.assertIn("*ind.sn = i_ev->indication_sn;", agent)
        self.assertIn("i_ev->indication_sn =", agent)
        self.assertIn("msg_disp.rd.ind.kpm.has_e2_indication_sn = src->sn != NULL;", handoff)
        self.assertIn("msg_disp.rd.ind.kpm.e2_indication_sn = *src->sn;", handoff)
        self.assertIn("ans.kpm.has_e2_indication_sn = d->kpm.has_e2_indication_sn;", copied)
        self.assertIn("ans.kpm.e2_indication_sn = d->kpm.e2_indication_sn;", copied)
        self.assertIn('source_seq_origin = rd->ind.kpm.has_e2_indication_sn ? "e2_indication"', callback)
        self.assertNotIn("kpm_source_seq", callback)

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

    def test_control_once_refuses_failed_fresh_qualification_before_baseline(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            native_calls = []
            binding = {"node_id": "node-a", "kpm_ue_key": "ue-1", "rc_ue_id": 17, "rnti": 4660, "source_seq": 9}

            class QualificationSource:
                def __init__(self):
                    self.calls = 0

                def qualify(self, profile):
                    self.calls += 1
                    if self.calls == 1:
                        return {"ok": True, "verified_target_binding": binding}
                    return {"ok": False, "error": "KPM_FRESHNESS_REQUIRED"}

            bridge = bridge_module.Bridge(
                profile="ul-prb-cap-v1",
                native=QualificationSource(),
                native_control=lambda action: native_calls.append(action),
                lease_dir=root / "leases",
                workspace_id="workspace-a",
                journal_path=root / "control_journal.json",
            )
            opened = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "open-freshness",
                    "operation": "open",
                    "profile_id": "ul-prb-cap-v1",
                    "mode": "control-once",
                }
            )
            result = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "act-freshness",
                    "operation": "act",
                    "profile_id": "ul-prb-cap-v1",
                    "session_id": opened["session_id"],
                    "action": {"max_ul_prb": 32},
                }
            )

            self.assertEqual(result["error"], "KPM_FRESHNESS_REQUIRED")
            self.assertEqual(native_calls, [])

    def test_control_once_refuses_failed_fresh_qualification_before_candidate(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            native_calls = []
            binding = {"node_id": "node-a", "kpm_ue_key": "ue-1", "rc_ue_id": 17, "rnti": 4660, "source_seq": 9}

            class QualificationSource:
                def __init__(self):
                    self.calls = 0

                def qualify(self, profile):
                    self.calls += 1
                    if self.calls < 3:
                        return {"ok": True, "verified_target_binding": binding}
                    return {"ok": False, "error": "KPM_FRESHNESS_REQUIRED"}

            bridge = bridge_module.Bridge(
                profile="ul-prb-cap-v1",
                native=QualificationSource(),
                native_control=lambda action: native_calls.append(action) or {
                    "acknowledged": True,
                    "gnb_apply_marker": True,
                    "later_kpm": True,
                },
                lease_dir=root / "leases",
                workspace_id="workspace-a",
                journal_path=root / "control_journal.json",
            )
            opened = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "open-candidate-freshness",
                    "operation": "open",
                    "profile_id": "ul-prb-cap-v1",
                    "mode": "control-once",
                }
            )
            result = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "act-candidate-freshness",
                    "operation": "act",
                    "profile_id": "ul-prb-cap-v1",
                    "session_id": opened["session_id"],
                    "action": {"max_ul_prb": 32},
                }
            )

            self.assertEqual(result["error"], "KPM_FRESHNESS_REQUIRED")
            self.assertEqual([call["phase"] for call in native_calls], ["baseline"])
            self.assertEqual(json.loads((root / "control_journal.json").read_text(encoding="utf-8"))["state"], "RECOVERED")

    def test_control_once_locks_failed_fresh_qualification_before_restore(self) -> None:
        bridge_module = load_bridge_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            native_calls = []
            binding = {"node_id": "node-a", "kpm_ue_key": "ue-1", "rc_ue_id": 17, "rnti": 4660, "source_seq": 9}

            class QualificationSource:
                def __init__(self):
                    self.calls = 0

                def qualify(self, profile):
                    self.calls += 1
                    if self.calls < 4:
                        return {"ok": True, "verified_target_binding": binding}
                    return {"ok": False, "error": "KPM_FRESHNESS_REQUIRED"}

            bridge = bridge_module.Bridge(
                profile="ul-prb-cap-v1",
                native=QualificationSource(),
                native_control=lambda action: native_calls.append(action) or {
                    "acknowledged": True,
                    "gnb_apply_marker": True,
                    "later_kpm": True,
                },
                lease_dir=root / "leases",
                workspace_id="workspace-a",
                journal_path=root / "control_journal.json",
            )
            opened = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "open-restore-freshness",
                    "operation": "open",
                    "profile_id": "ul-prb-cap-v1",
                    "mode": "control-once",
                }
            )
            result = bridge.handle(
                {
                    "protocol_version": 1,
                    "request_id": "act-restore-freshness",
                    "operation": "act",
                    "profile_id": "ul-prb-cap-v1",
                    "session_id": opened["session_id"],
                    "action": {"max_ul_prb": 32},
                }
            )

            self.assertEqual(result["error"], "KPM_FRESHNESS_REQUIRED")
            self.assertEqual([call["phase"] for call in native_calls], ["baseline", "candidate"])
            self.assertEqual(json.loads((root / "control_journal.json").read_text(encoding="utf-8"))["state"], "ROLLBACK_UNCONFIRMED")
            self.assertTrue((root / "leases/node-a.lock").exists())

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
                    return {"acknowledged": True, "gnb_apply_marker": True, "later_kpm": True}
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
