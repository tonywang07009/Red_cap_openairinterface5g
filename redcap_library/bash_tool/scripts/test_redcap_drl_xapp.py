#!/usr/bin/env python3

import os
from pathlib import Path
import importlib.util
import json
import subprocess
import tempfile
from types import SimpleNamespace
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
CLI = REPO_ROOT / "redcap_library/bash_tool/scripts/redcap_drl_xapp.sh"
BRIDGE = REPO_ROOT / "redcap_library/drl_xapp/bridge_daemon.py"


def load_bridge_module():
    spec = importlib.util.spec_from_file_location("redcap_drl_bridge", BRIDGE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RedcapDrlXappCliTest(unittest.TestCase):
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
