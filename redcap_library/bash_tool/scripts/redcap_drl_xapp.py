#!/usr/bin/env python3

import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
import uuid


REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACT = REPO_ROOT / "redcap_interface/control/redcap_control_contract.yaml"
WORKSPACE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
ENTRYPOINT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*:[A-Za-z_][A-Za-z0-9_]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="redcap_drl_xapp.sh",
        description="建立與操作具安全 Gate 的 RedCap DRL xApp workspace。help 為唯讀，不會連線 Docker。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser(
        "init",
        help="建立名稱化 workspace。",
        description="必要參數：名稱、workspace 根目錄、既有 compose、runtime、profile、release。",
        epilog=(
            "副作用：全部 preflight 通過後，原子式建立一個新 workspace；不啟動容器、不發送 E2 control。\n"
            "證據：workspace.lock.json、resolved-compose.json、compose.overlay.json。\n"
            "下一步：redcap_drl_xapp.sh up --workspace <workspace>"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    init.add_argument("--name", required=True, help="必要；workspace 名稱，不可與既有目錄重複。")
    init.add_argument("--workspace-root", type=Path, required=True, help="必要；workspace 的父目錄。")
    init.add_argument("--compose", type=Path, required=True, help="必要；既有 FlexRIC RedCap compose 路徑，唯讀。")
    init.add_argument("--runtime", choices=("cpu", "gpu"), required=True, help="必要；CPU 或 GPU runtime。")
    init.add_argument("--profile", choices=("none", "ul-prb-cap-v1"), required=True, help="必要；初始化後鎖定。")
    init.add_argument("--release", required=True, help="必要；已建置 immutable release，例如 1.0.0。")
    build = commands.add_parser(
        "build-release",
        help="建置一次共用 CPU/GPU/bridge images。",
        description="必要參數：新的 release 版本。",
        epilog=(
            "副作用：依序建置 CPU、GPU、bridge temporary images，smoke 通過後才建立 immutable tags。\n"
            "升級順序：build-release → 確認 smoke/evidence → upgrade workspace。\n"
            "下一步：redcap_drl_xapp.sh init ... 或 upgrade --workspace <path> --to-release <release>"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    build.add_argument("--release", required=True, help="必要；新版本，例如 1.0.0；既有 tag 不可覆寫。")
    build.add_argument("--flexric-base", default="oai-flexric:custom-dev", help="可選；本機 FlexRIC base tag，預設 oai-flexric:custom-dev；其 image ID 會鎖定。")
    for name, summary, side_effect in (
        ("up", "啟動 workspace runtime 與 bridge。", "只啟動 generated overlay services；不重啟 simulator。"),
        ("verify", "執行 runtime、native extension、bridge 與 RIC reachability smoke。", "唯讀檢查；不發送 E2 control。"),
        ("status", "顯示 workspace 與最近 gate 狀態。", "唯讀；不呼叫控制介面。"),
        ("down", "停止 workspace runtime 與 bridge。", "只停止 generated overlay services；保留 evidence。"),
        ("remove", "移除 workspace containers/networks。", "只移除 generated overlay resources；保留 workspace 與 evidence。"),
    ):
        command = commands.add_parser(
            name,
            help=summary,
            description=f"必要參數：--workspace。{summary}",
            epilog=f"副作用：{side_effect}\n證據：命令輸出的 gate_status。\n下一步：執行 status 或命令輸出的 safe_next_command。",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        command.add_argument("--workspace", type=Path, required=True, help="必要；init 建立的 workspace 路徑。")
    upgrade = commands.add_parser(
        "upgrade",
        help="切換 workspace 的 immutable runtime/bridge release。",
        description="必要參數：--workspace、--to-release。workspace 必須停止。",
        epilog=(
            "副作用：新 images 全部存在後才原子更新 lock/overlay；不發送 E2 control。\n"
            "升級順序：build-release → 驗證 release smoke → down workspace → upgrade → up → verify。\n"
            "失敗時：保留舊 lock 與 overlay。\n下一步：redcap_drl_xapp.sh up --workspace <workspace>"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    upgrade.add_argument("--workspace", type=Path, required=True, help="必要；已停止的 workspace。")
    upgrade.add_argument("--to-release", required=True, help="必要；已建置的新 immutable release。")
    for name, summary in (
        ("discover-kpm", "讀取 live E2 node/KPM/RC capability；不訂閱、不控制。"),
        ("qualify-kpm", "先讀取 capability，再驗證 profile 所需 cell/UE KPM freshness、alignment 與 target binding。"),
        ("recover", "依 durable journal 嘗試恢復安全 baseline；不得重啟 simulator。"),
    ):
        command = commands.add_parser(
            name,
            help=summary,
            description=f"必要參數：--workspace。{summary}",
            epilog="副作用：寫入新的 run evidence；只有 recover 可能在完整 binding 存在時送 baseline。\n下一步：依 safe_next_command。",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        command.add_argument("--workspace", type=Path, required=True, help="必要；已啟動的 workspace。")
    run = commands.add_parser(
        "run",
        help="執行模型 entrypoint；啟用控制時最多一個 candidate action。",
        description="必要參數：--workspace。model controller 另需 --entrypoint module:callable。",
        epilog=(
            "副作用：啟動模型；只有 --enable-control 且所有 gates 通過時才送 baseline→candidate→baseline。\n"
            "預設保留 containers；--teardown 才停止 workspace。\n下一步：redcap_drl_xapp.sh status --workspace <workspace>"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    run.add_argument("--workspace", type=Path, required=True, help="必要；workspace 路徑。")
    run.add_argument("--controller", choices=("fixed", "greedy", "model"), default="model", help="預設 model；fixed/greedy 僅供 bounded validation。")
    run.add_argument("--entrypoint", help="model controller 必要；例如 src.policy:main。")
    run.add_argument("--enable-control", action="store_true", help="顯式開啟 control-once；預設 observation/offline only。")
    run.add_argument("--teardown", action="store_true", help="完成後停止 workspace；預設保留。")
    return parser.parse_args()


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


def valid_entrypoint(entrypoint: object) -> bool:
    return isinstance(entrypoint, str) and ENTRYPOINT.fullmatch(entrypoint) is not None


def docker_json(args: list[str]) -> dict:
    result = subprocess.run(["docker", *args], text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "Docker command failed")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValueError("Docker Compose 未回傳有效 JSON") from error


def service_signature(service: dict) -> str:
    selected = {
        "command": service.get("command"),
        "entrypoint": service.get("entrypoint"),
        "healthcheck": service.get("healthcheck"),
        "image": service.get("image"),
    }
    return json.dumps(selected, sort_keys=True).lower()


def resolve_compose(compose: Path) -> dict:
    model = docker_json(["compose", "-f", str(compose), "config", "--format", "json"])
    services = model.get("services")
    networks = model.get("networks")
    if not isinstance(services, dict) or not isinstance(networks, dict):
        raise ValueError("compose 缺少 services 或 networks")

    ric = [name for name, service in services.items() if "nearrt-ric" in service_signature(service)]
    gnb = [name for name, service in services.items() if "nr-softmodem" in service_signature(service)]
    if len(ric) != 1 or len(gnb) != 1:
        raise ValueError(f"無法唯一解析 RIC/gNB service：RIC={ric}, gNB={gnb}")

    ric_networks = set((services[ric[0]].get("networks") or {}).keys())
    gnb_networks = set((services[gnb[0]].get("networks") or {}).keys())
    shared = sorted(ric_networks & gnb_networks)
    if len(shared) != 1:
        raise ValueError(f"無法唯一解析 RIC/gNB 共用 network：{shared}")
    network = networks.get(shared[0])
    if not isinstance(network, dict) or not network.get("name"):
        raise ValueError("compose network 缺少解析後名稱")

    config_mounts = []
    for role, service_name in (("ric", ric[0]), ("gnb", gnb[0])):
        for volume in services[service_name].get("volumes") or []:
            if not isinstance(volume, dict) or volume.get("type") != "bind":
                continue
            target = str(volume.get("target", ""))
            if Path(target).suffix.lower() not in {".conf", ".yaml", ".yml"}:
                continue
            config_mounts.append({"role": role, "source": volume.get("source"), "target": target})

    flexric_configs = [
        mount
        for mount in config_mounts
        if mount["role"] == "ric" and Path(mount["target"]).name == "flexric.conf" and mount["source"]
    ]
    if len(flexric_configs) != 1 or not Path(flexric_configs[0]["source"]).is_file():
        raise ValueError("無法唯一解析可讀的 FlexRIC config bind mount")

    return {
        "compose_project": model.get("name"),
        "ric_service": ric[0],
        "gnb_service": gnb[0],
        "network_key": shared[0],
        "network_name": network["name"],
        "config_mounts": config_mounts,
    }


def image_id(tag: str) -> str:
    result = subprocess.run(
        ["docker", "image", "inspect", tag, "--format", "{{.Id}}"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip().startswith("sha256:"):
        raise ValueError(f"找不到本機 immutable image：{tag}")
    return result.stdout.strip()


def tag_exists(tag: str) -> bool:
    return subprocess.run(
        ["docker", "image", "inspect", tag],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def build_release(args: argparse.Namespace) -> int:
    if not WORKSPACE_NAME.fullmatch(args.release):
        return fail("release 名稱只能包含英數、點、底線與連字號")
    # ponytail: one host-wide build lane; split by release only if build throughput becomes a bottleneck.
    with Path(__file__).open("rb") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        return build_release_locked(args)


def build_release_locked(args: argparse.Namespace) -> int:
    tags = [
        f"redcap-drl-runtime:{args.release}-cpu",
        f"redcap-drl-runtime:{args.release}-gpu",
        f"redcap-flexric-bridge:{args.release}",
    ]
    existing = [tag for tag in tags if tag_exists(tag)]
    if existing:
        return fail(f"immutable tag 已存在：{', '.join(existing)}")
    try:
        flexric_base_id = image_id(args.flexric_base)
    except ValueError as error:
        return fail(str(error))

    suffix = f"tmp-{os.getpid()}"
    temporary = {
        "cpu": f"redcap-drl-runtime:{suffix}-cpu",
        "gpu": f"redcap-drl-runtime:{suffix}-gpu",
        "bridge": f"redcap-flexric-bridge:{suffix}",
    }
    builds = [
        [
            "docker", "build", "-f", str(REPO_ROOT / "redcap_library/drl_xapp/Dockerfile.runtime"),
            "--build-arg", "TORCH_SPEC=torch==2.13.0+cpu",
            "--build-arg", "TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu",
            "-t", temporary["cpu"], str(REPO_ROOT),
        ],
        [
            "docker", "build", "-f", str(REPO_ROOT / "redcap_library/drl_xapp/Dockerfile.runtime"),
            "--build-arg", "TORCH_SPEC=torch==2.13.0",
            "--build-arg", "TORCH_INDEX_URL=https://download.pytorch.org/whl/cu132",
            "-t", temporary["gpu"], str(REPO_ROOT),
        ],
        [
            "docker", "build", "-f", str(REPO_ROOT / "redcap_library/drl_xapp/Dockerfile.bridge"),
            "--build-arg", f"FLEXRIC_BASE={args.flexric_base}",
            "-t", temporary["bridge"], str(REPO_ROOT),
        ],
    ]
    try:
        for command in builds:
            if subprocess.run(command, check=False).returncode != 0:
                return fail(f"release build 失敗：{command[-2]}")
        smoke_commands = [
            ["docker", "run", "--rm", temporary["cpu"], "redcap-drl-runtime-smoke"],
            [
                "docker", "run", "--rm", "--gpus", "all", "--entrypoint", "python3", temporary["gpu"],
                "-c", "import torch; assert torch.version.cuda == '13.2'; assert torch.cuda.is_available(); "
                "assert torch.ones(1, device='cuda').item() == 1; print(torch.cuda.get_device_name(0))",
            ],
            [
                "docker", "run", "--rm", "--entrypoint", "python3", temporary["bridge"], "-c",
                "import xapp_sdk as x; n=x.E2Node(); n.ran_function_ids.append(2); "
                "assert list(n.ran_function_ids) == [2]; k=x.KpmReportStyle(); k.style_type=4; "
                "n.kpm_report_styles.append(k); r=x.RcControlStyle(); r.style_type=1; r.action_ids.append(100); "
                "n.rc_control_styles.append(r); assert n.kpm_report_styles[0].style_type == 4; "
                "assert list(n.rc_control_styles[0].action_ids) == [100]; print('BRIDGE_SMOKE PASS')",
            ],
        ]
        for command in smoke_commands:
            if subprocess.run(command, check=False).returncode != 0:
                return fail("release smoke 失敗；不建立 final tags")
        tagged = []
        try:
            for source, target in zip(temporary.values(), tags, strict=True):
                subprocess.run(["docker", "tag", source, target], check=True)
                tagged.append(target)
        except subprocess.CalledProcessError:
            for tag in tagged:
                subprocess.run(["docker", "image", "rm", tag], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            return fail("建立 final immutable tags 失敗；已移除本次建立的 partial tags")
    finally:
        for tag in temporary.values():
            subprocess.run(["docker", "image", "rm", tag], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

    evidence_dir = REPO_ROOT / "test_log/runtime_configs/drl_releases"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "release": args.release,
        "flexric_base": {"tag": args.flexric_base, "id": flexric_base_id},
        "images": {tag: image_id(tag) for tag in tags},
        "smoke": "PASS",
    }
    write_json(evidence_dir / f"{args.release}.json", manifest)
    print(json.dumps({"gate_status": "RELEASE_READY", "evidence_manifest_path": str(evidence_dir / f"{args.release}.json"), "safe_next_command": "redcap_drl_xapp.sh init --help"}))
    return 0


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def initialize(args: argparse.Namespace) -> int:
    if not WORKSPACE_NAME.fullmatch(args.name):
        return fail("workspace 名稱只能包含英數、點、底線與連字號")
    if not WORKSPACE_NAME.fullmatch(args.release):
        return fail("release 名稱只能包含英數、點、底線與連字號")
    workspace = args.workspace_root.resolve() / args.name
    if workspace.exists():
        return fail(f"workspace 已存在：{workspace}")
    if not args.compose.is_file():
        return fail(f"compose 檔案不存在：{args.compose}")

    try:
        resolved = resolve_compose(args.compose.resolve())
        runtime_tag = f"redcap-drl-runtime:{args.release}-{args.runtime}"
        bridge_tag = f"redcap-flexric-bridge:{args.release}"
        runtime_id = image_id(runtime_tag)
        bridge_id = image_id(bridge_tag)
    except ValueError as error:
        return fail(str(error))

    args.workspace_root.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{args.name}.", dir=args.workspace_root))
    try:
        (temporary / "src").mkdir()
        (temporary / "artifacts/runs").mkdir(parents=True)
        (temporary / "runtime_configs").mkdir()
        (temporary / "run").mkdir()
        lock = {
            "schema_version": 1,
            "name": args.name,
            "runtime": args.runtime,
            "profile": args.profile,
            "release": args.release,
            "compose": str(args.compose.resolve()),
            "images": {
                "runtime": {"tag": runtime_tag, "id": runtime_id},
                "bridge": {"tag": bridge_tag, "id": bridge_id},
            },
            "resolved": resolved,
        }
        if args.profile == "ul-prb-cap-v1":
            lock["measurement_post"] = {"status": "UNFROZEN"}
        bridge_mounts = [
            {"type": "bind", "source": str(workspace / "run"), "target": "/run/redcap-drl"},
            {"type": "bind", "source": str(CONTRACT), "target": "/opt/redcap/control/redcap_control_contract.yaml", "read_only": True},
            {
                "type": "bind",
                "source": str(workspace / "workspace.lock.json"),
                "target": "/opt/redcap/workspace.lock.json",
                "read_only": True,
            },
        ]
        for index, mount in enumerate(resolved["config_mounts"]):
            if mount["source"]:
                external_target = (
                    "/usr/local/etc/flexric/flexric.conf"
                    if mount["role"] == "ric" and Path(mount["target"]).name == "flexric.conf"
                    else f"/opt/redcap/external/{mount['role']}/{index}-{Path(mount['target']).name}"
                )
                bridge_mounts.append(
                    {
                        "type": "bind",
                        "source": mount["source"],
                        "target": external_target,
                        "read_only": True,
                    }
                )
        overlay = {
            "name": f"redcap-drl-{args.name}",
            "services": {
                "drl-runtime": {
                    "image": runtime_tag,
                    "command": ["sleep", "infinity"],
                    "network_mode": "none",
                    "read_only": True,
                    "user": f"{os.getuid()}:{os.getgid()}",
                    "working_dir": "/workspace",
                    "volumes": [
                        {"type": "bind", "source": str(workspace / "src"), "target": "/workspace/src"},
                        {"type": "bind", "source": str(workspace / "run"), "target": "/run/redcap-drl", "read_only": True},
                    ],
                    "tmpfs": ["/tmp"],
                    "cap_drop": ["ALL"],
                    "security_opt": ["no-new-privileges:true"],
                },
                "flexric-bridge": {
                    "image": bridge_tag,
                    "command": [
                        "--socket",
                        "/run/redcap-drl/bridge.sock",
                        "--profile",
                        args.profile,
                        "--flexric-config",
                        "/usr/local/etc/flexric/flexric.conf",
                        "--workspace-id",
                        args.name,
                        "--workspace-lock",
                        "/opt/redcap/workspace.lock.json",
                    ],
                    "read_only": True,
                    "user": f"{os.getuid()}:{os.getgid()}",
                    "volumes": bridge_mounts,
                    "tmpfs": ["/tmp"],
                    "cap_drop": ["ALL"],
                    "security_opt": ["no-new-privileges:true"],
                    "networks": ["simulator"],
                },
            },
            "networks": {"simulator": {"external": True, "name": resolved["network_name"]}},
        }
        if args.runtime == "gpu":
            overlay["services"]["drl-runtime"]["gpus"] = "all"
        write_json(temporary / "workspace.lock.json", lock)
        write_json(temporary / "resolved-compose.json", resolved)
        write_json(temporary / "compose.overlay.json", overlay)
        temporary.rename(workspace)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise

    print(json.dumps({"workspace": str(workspace), "gate_status": "INITIALIZED", "safe_next_command": f"redcap_drl_xapp.sh up --workspace {workspace}"}))
    return 0


def load_workspace(workspace: Path) -> tuple[Path, dict, dict]:
    workspace = workspace.resolve()
    lock_path = workspace / "workspace.lock.json"
    overlay_path = workspace / "compose.overlay.json"
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"無效 workspace：{workspace}: {error}") from error
    if lock.get("schema_version") != 1 or lock.get("name") != workspace.name:
        raise ValueError("workspace lock schema/name 不一致")
    return workspace, lock, overlay


def overlay_command(workspace: Path, *args: str, capture: bool = False) -> subprocess.CompletedProcess:
    command = [
        "docker", "compose", "-p", f"redcap-drl-{workspace.name}",
        "-f", str(workspace / "compose.overlay.json"), *args,
    ]
    return subprocess.run(command, text=True, capture_output=capture, check=False)


def lifecycle(args: argparse.Namespace) -> int:
    try:
        workspace, lock, _ = load_workspace(args.workspace)
    except ValueError as error:
        return fail(str(error))
    if args.command == "up" and lock["runtime"] == "gpu":
        result = subprocess.run(["docker", "info", "--format", "{{json .Runtimes}}"], text=True, capture_output=True, check=False)
        if result.returncode != 0 or "nvidia" not in result.stdout.lower():
            return fail("GPU runtime 不可用；未啟動 workspace")
    compose_args = {
        "up": ("up", "-d"),
        "down": ("down",),
        "remove": ("down", "--remove-orphans"),
    }[args.command]
    result = overlay_command(workspace, *compose_args)
    if result.returncode != 0:
        return fail(f"workspace {args.command} 失敗")
    status = {"up": "WORKSPACE_UP", "down": "WORKSPACE_DOWN", "remove": "WORKSPACE_RESOURCES_REMOVED"}[args.command]
    print(json.dumps({"workspace": str(workspace), "gate_status": status, "safe_next_command": f"redcap_drl_xapp.sh status --workspace {workspace}"}))
    return 0


def uds_call(socket_path: Path, request: dict) -> dict:
    import socket

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(5)
        client.connect(str(socket_path))
        client.sendall(json.dumps(request).encode("utf-8"))
        return json.loads(client.recv(1024 * 1024))


def verify(args: argparse.Namespace) -> int:
    try:
        workspace, lock, _ = load_workspace(args.workspace)
    except ValueError as error:
        return fail(str(error))
    runtime = overlay_command(workspace, "exec", "-T", "drl-runtime", "redcap-drl-runtime-smoke", capture=True)
    try:
        bridge = uds_call(
            workspace / "run/bridge.sock",
            {"protocol_version": 1, "request_id": "verify-health", "operation": "health"},
        ) if (workspace / "run/bridge.sock").exists() else {"ok": False, "error": "BRIDGE_SOCKET_MISSING"}
    except (OSError, json.JSONDecodeError) as error:
        bridge = {"ok": False, "error": "BRIDGE_UNREACHABLE", "detail": str(error)}
    reachability = overlay_command(
        workspace,
        "exec", "-T", "flexric-bridge", "getent", "hosts", lock["resolved"]["ric_service"],
        capture=True,
    )
    gates = {
        "runtime_smoke": runtime.returncode == 0,
        "bridge_health": bridge.get("ok") is True,
        "ric_name_resolution": reachability.returncode == 0,
        "e2_setup": "UNPROVED",
        "kpm": "UNPROVED",
        "control": "NOT_ATTEMPTED",
    }
    passed = all(gates[key] is True for key in ("runtime_smoke", "bridge_health", "ric_name_resolution"))
    print(json.dumps({"workspace": str(workspace), "gate_status": "SMOKE_PASS" if passed else "SMOKE_FAIL", "gates": gates, "safe_next_command": f"redcap_drl_xapp.sh discover-kpm --workspace {workspace}"}))
    return 0 if passed else 3


def status(args: argparse.Namespace) -> int:
    try:
        workspace, lock, _ = load_workspace(args.workspace)
    except ValueError as error:
        return fail(str(error))
    result = overlay_command(workspace, "ps", "--format", "json", capture=True)
    print(json.dumps({"workspace": str(workspace), "release": lock["release"], "profile": lock["profile"], "gate_status": "STATUS_READ", "compose_ps": result.stdout.strip(), "safe_next_command": f"redcap_drl_xapp.sh verify --workspace {workspace}"}))
    return 0 if result.returncode == 0 else 3


def create_evidence(workspace: Path, lock: dict, command: str) -> tuple[Path, dict]:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    run_dir = workspace / "artifacts/runs" / run_id
    run_dir.mkdir(parents=True)
    manifest = {
        "schema_version": 1,
        "workspace": lock["name"],
        "run_id": run_id,
        "command": command,
        "release": lock["release"],
        "images": lock["images"],
        "profile": lock["profile"],
        "resolved_node": None,
        "gate_status": "STARTED",
        "gates": {},
        "safe_next_command": f"redcap_drl_xapp.sh status --workspace {workspace}",
        "evidence": {
            "events": str(run_dir / "events.ndjson"),
            "kpm": str(run_dir / "kpm_evidence.json"),
            "journal": str(run_dir / "control_journal.json"),
            "gnb_apply_excerpt": str(run_dir / "gnb_apply_excerpt.log"),
            "resolved_compose": str(workspace / "resolved-compose.json"),
            "generated_overlay": str(workspace / "compose.overlay.json"),
        },
    }
    (run_dir / "events.ndjson").write_text("", encoding="utf-8")
    write_json(run_dir / "kpm_evidence.json", {"cell": [], "ue": [], "qualification": "UNPROVED"})
    write_json(run_dir / "control_journal.json", {"state": "NOT_STARTED", "control_attempted": False})
    (run_dir / "gnb_apply_excerpt.log").write_text("", encoding="utf-8")
    write_json(run_dir / "manifest.json", manifest)
    return run_dir, manifest


def record_event(run_dir: Path, event: dict) -> None:
    with (run_dir / "events.ndjson").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, sort_keys=True) + "\n")


def bridge_gate(args: argparse.Namespace) -> int:
    try:
        workspace, lock, _ = load_workspace(args.workspace)
    except ValueError as error:
        return fail(str(error))
    run_dir, manifest = create_evidence(workspace, lock, args.command)
    operations = ["discover", "qualify"] if args.command == "qualify-kpm" else [{"discover-kpm": "discover", "recover": "recover"}[args.command]]
    discovery = None
    result = {"ok": False}
    for operation in operations:
        request = {
            "protocol_version": 1,
            "request_id": uuid.uuid4().hex,
            "operation": operation,
            "profile_id": lock["profile"],
        }
        try:
            result = uds_call(workspace / "run/bridge.sock", request)
        except (OSError, json.JSONDecodeError) as error:
            result = {"ok": False, "error": "BRIDGE_UNREACHABLE", "detail": str(error)}
        gate_name = {"discover": "discover-kpm", "qualify": "qualify-kpm", "recover": "recover"}[operation]
        record_event(run_dir, {"event": gate_name, "result": result})
        manifest["gates"][gate_name] = result
        if operation == "discover":
            discovery = result
        if isinstance(result.get("node_id"), str):
            manifest["resolved_node"] = result["node_id"]
        if not result.get("ok"):
            break
    if discovery is not None:
        write_json(
            run_dir / "kpm_evidence.json",
            {
                "capabilities": discovery.get("capabilities", {}),
                "cell": result.get("cell", []),
                "ue": result.get("ue", []),
                "qualification": "QUALIFIED" if result.get("ok") and args.command == "qualify-kpm" else "UNPROVED",
            },
        )
    manifest["gate_status"] = "PASS" if result.get("ok") else "FAIL"
    manifest["safe_next_command"] = (
        f"redcap_drl_xapp.sh qualify-kpm --workspace {workspace}"
        if result.get("ok") and args.command == "discover-kpm"
        else f"redcap_drl_xapp.sh status --workspace {workspace}"
    )
    write_json(run_dir / "manifest.json", manifest)
    print(json.dumps({"workspace": str(workspace), "run_id": manifest["run_id"], "gate_status": manifest["gate_status"], "evidence_manifest_path": str(run_dir / "manifest.json"), "safe_next_command": manifest["safe_next_command"]}))
    return 0 if result.get("ok") else 4


def run_model(args: argparse.Namespace) -> int:
    try:
        workspace, lock, _ = load_workspace(args.workspace)
    except ValueError as error:
        return fail(str(error))
    if args.controller == "model":
        if not args.entrypoint:
            return fail("model controller 必須提供 --entrypoint module:callable")
        if not valid_entrypoint(args.entrypoint):
            return fail("entrypoint 必須是 module:callable")
    if args.enable_control:
        if lock["profile"] == "none":
            return fail("profile=none 禁止 E2 control")
        if verify(argparse.Namespace(workspace=workspace)) != 0:
            return fail("runtime smoke 或 RIC reachability 未通過；qualification 與 control 均未啟動")
        qualifier = argparse.Namespace(command="qualify-kpm", workspace=workspace)
        if bridge_gate(qualifier) != 0:
            return fail("KPM qualification 未通過；模型與 control 均未啟動")
        return fail("control-once runner 尚未取得可驗證 live binding；未發送 control")
    if args.controller != "model":
        return fail("fixed/greedy controller 僅能搭配 --enable-control 與完整 live gates")
    result = overlay_command(workspace, "exec", "-T", "drl-runtime", "redcap-drl-run-entrypoint", args.entrypoint)
    if args.teardown:
        overlay_command(workspace, "down")
    print(json.dumps({"workspace": str(workspace), "gate_status": "MODEL_EXITED" if result.returncode == 0 else "MODEL_FAILED", "control": "NOT_ATTEMPTED", "safe_next_command": f"redcap_drl_xapp.sh status --workspace {workspace}"}))
    return result.returncode


def upgrade(args: argparse.Namespace) -> int:
    if not WORKSPACE_NAME.fullmatch(args.to_release):
        return fail("release 名稱只能包含英數、點、底線與連字號")
    try:
        workspace, lock, overlay = load_workspace(args.workspace)
        runtime_tag = f"redcap-drl-runtime:{args.to_release}-{lock['runtime']}"
        bridge_tag = f"redcap-flexric-bridge:{args.to_release}"
        runtime_id = image_id(runtime_tag)
        bridge_id = image_id(bridge_tag)
    except ValueError as error:
        return fail(str(error))
    ps = overlay_command(workspace, "ps", "-q", capture=True)
    if ps.returncode != 0 or ps.stdout.strip():
        return fail("workspace 必須先停止；未修改 lock")
    updated_lock = dict(lock)
    updated_lock["release"] = args.to_release
    updated_lock["images"] = {
        "runtime": {"tag": runtime_tag, "id": runtime_id},
        "bridge": {"tag": bridge_tag, "id": bridge_id},
    }
    updated_overlay = dict(overlay)
    updated_overlay["services"]["drl-runtime"]["image"] = runtime_tag
    updated_overlay["services"]["flexric-bridge"]["image"] = bridge_tag
    lock_tmp = workspace / ".workspace.lock.json.tmp"
    overlay_tmp = workspace / ".compose.overlay.json.tmp"
    write_json(lock_tmp, updated_lock)
    write_json(overlay_tmp, updated_overlay)
    old_lock = (workspace / "workspace.lock.json").read_bytes()
    old_overlay = (workspace / "compose.overlay.json").read_bytes()
    try:
        lock_tmp.replace(workspace / "workspace.lock.json")
        overlay_tmp.replace(workspace / "compose.overlay.json")
    except OSError as error:
        (workspace / "workspace.lock.json").write_bytes(old_lock)
        (workspace / "compose.overlay.json").write_bytes(old_overlay)
        lock_tmp.unlink(missing_ok=True)
        overlay_tmp.unlink(missing_ok=True)
        return fail(f"upgrade 寫入失敗；已恢復舊 lock/overlay：{error}")
    print(json.dumps({"workspace": str(workspace), "gate_status": "UPGRADED_NO_CONTROL", "safe_next_command": f"redcap_drl_xapp.sh up --workspace {workspace}"}))
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "init":
        return initialize(args)
    if args.command == "build-release":
        return build_release(args)
    if args.command in {"up", "down", "remove"}:
        return lifecycle(args)
    if args.command == "verify":
        return verify(args)
    if args.command == "status":
        return status(args)
    if args.command == "upgrade":
        return upgrade(args)
    if args.command in {"discover-kpm", "qualify-kpm", "recover"}:
        return bridge_gate(args)
    if args.command == "run":
        return run_model(args)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
