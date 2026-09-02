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
import time
import threading
from datetime import datetime, timezone
import uuid


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from redcap_library.drl_xapp.bridge_daemon import pair_kpm_samples, qualified_model_observation

CONTRACT = REPO_ROOT / "redcap_interface/control/redcap_control_contract.yaml"
WORKSPACE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
ENTRYPOINT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*:[A-Za-z_][A-Za-z0-9_]*$")
GNB_APPLY_MARKER = re.compile(r"RedCap UL PRB control RNTI ([0-9a-fA-F]{4}) requested (\d+) effective (\d+)")
DISCOVERY_UDS_TIMEOUT_SECONDS = 30
# Three native phases each may spend the observation timeout on requalification.
CONTROL_UDS_TIMEOUT_SECONDS = 20
FINAL_CONTROL_JOURNAL_STATES = frozenset({"COMPLETED", "RECOVERED", "ROLLBACK_UNCONFIRMED"})


def monotonic_ms() -> int:
    return time.monotonic_ns() // 1_000_000


def record_gnb_apply_marker(line: str, proof_path: Path, excerpt_path: Path) -> dict | None:
    match = GNB_APPLY_MARKER.search(line)
    if match is None:
        return None
    record = {
        "rnti": int(match.group(1), 16),
        "requested": int(match.group(2)),
        "effective": int(match.group(3)),
        "observed_monotonic_ms": monotonic_ms(),
    }
    with proof_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
    with excerpt_path.open("a", encoding="utf-8") as stream:
        stream.write(line)
    return record


def start_gnb_marker_collector(workspace: Path, lock: dict, excerpt_path: Path):
    try:
        compose = lock["compose"]
        gnb_service = lock["resolved"]["gnb_service"]
    except (KeyError, TypeError):
        return None
    proof_path = workspace / "run/gnb_apply_proof.jsonl"
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text("", encoding="utf-8")
    try:
        process = subprocess.Popen(
            ["docker", "compose", "-f", str(compose), "logs", "--follow", "--timestamps", "--since", "0s", gnb_service],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except OSError:
        return None

    def collect() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            record_gnb_apply_marker(line, proof_path, excerpt_path)

    reader = threading.Thread(target=collect, daemon=True)
    reader.start()
    return process, reader


def stop_gnb_marker_collector(collector) -> None:
    process, reader = collector
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()
    reader.join(timeout=1)


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
    freeze = commands.add_parser(
        "freeze-measurement-post",
        help="以人工批准的 calibration evidence 凍結 profile KPM policy。",
        description="必要參數：停止的 ul-prb-cap-v1 workspace、calibration run、明示批准與三個實測門檻。",
        epilog=(
            "副作用：只原子更新 workspace.lock.json；不啟動 Docker、不送 E2 control。\n"
            "限制：calibration run、approval token、node/style/metric/release fingerprint 必須一致。\n"
            "下一步：up → qualify-kpm；release upgrade 會使 policy 回到 UNFROZEN。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    freeze.add_argument("--workspace", type=Path, required=True, help="必要；已停止的 ul-prb-cap-v1 workspace。")
    freeze.add_argument("--calibration-run", action="append", required=True, help="必要；保留 calibration run ID，可重複指定。")
    freeze.add_argument("--approve-calibration", action="append", required=True, help="必要；人工確認的 calibration run ID，須與 --calibration-run 完全相同。")
    freeze.add_argument("--freshness-window-ms", type=int, required=True, help="必要；實測後批准的 freshness 上限（毫秒）。")
    freeze.add_argument("--cell-ue-max-skew-ms", type=int, required=True, help="必要；實測後批准的 cell/UE 最大 skew（毫秒）。")
    freeze.add_argument("--min-valid-paired-samples", type=int, required=True, help="必要；實測後批准的最少有效 paired samples。")
    for name, summary in (
        ("discover-kpm", "讀取 live E2 node/KPM/RC capability；不訂閱、不控制。"),
        ("probe-kpm", "以 cell/UE KPM callback cadence 做唯讀診斷；不控制。"),
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


def validation_candidate(controller: str, cell_samples: object) -> dict:
    if controller == "fixed":
        return {"ok": True, "max_ul_prb": 16, "source": "fixed"}
    if controller != "greedy" or not isinstance(cell_samples, list) or not cell_samples:
        return {"ok": False, "error": "UL_PRB_UTILIZATION_REQUIRED"}
    try:
        utilization = cell_samples[-1]["measurements"]["RRU.PrbTotUl"]
        if isinstance(utilization, bool):
            raise ValueError
        utilization = float(utilization)
    except (KeyError, TypeError, ValueError, OverflowError):
        return {"ok": False, "error": "UL_PRB_UTILIZATION_REQUIRED"}
    if not 0 <= utilization <= 100:
        return {"ok": False, "error": "UL_PRB_UTILIZATION_REQUIRED"}
    candidate = 16 if utilization < 55 else 32 if utilization <= 80 else 64
    return {
        "ok": True,
        "max_ul_prb": candidate,
        "source": "RRU.PrbTotUl",
        "ul_prb_utilization_pct": utilization,
    }


def model_candidate(workspace: Path, entrypoint: str, qualification: object, run_dir: Path) -> dict:
    summary = qualified_model_observation(qualification)
    if not summary["ok"]:
        return summary
    observation_path = workspace / "runtime-input" / f"model-observation-{uuid.uuid4().hex}.json"
    evidence_observation = run_dir / "model_observation.json"
    evidence_decision = run_dir / "model_decision.json"
    try:
        observation_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(observation_path, summary["observation"])
        observation_path.chmod(0o444)
        write_json(evidence_observation, summary["observation"])
        evidence_observation.chmod(0o444)
    except OSError:
        return {"ok": False, "error": "EVIDENCE_WRITE_REQUIRED"}
    runtime_path = Path("/run/redcap-drl") / observation_path.name
    result = overlay_command(
        workspace,
        "exec",
        "-T",
        "drl-runtime",
        "redcap-drl-run-entrypoint",
        entrypoint,
        str(runtime_path),
        capture=True,
    )
    if result.returncode != 0:
        return {"ok": False, "error": "MODEL_INFERENCE_FAILED"}
    try:
        lines = result.stdout.splitlines()
        decision = json.loads(lines[0]) if len(lines) == 1 else None
        max_ul_prb = decision["max_ul_prb"]
        if set(decision) != {"max_ul_prb"} or isinstance(max_ul_prb, bool) or type(max_ul_prb) is not int:
            raise ValueError
        if not 1 <= max_ul_prb <= 51:
            raise ValueError
    except (AttributeError, IndexError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return {"ok": False, "error": "MODEL_CANDIDATE_REQUIRED"}
    try:
        write_json(evidence_decision, {"max_ul_prb": max_ul_prb})
        evidence_decision.chmod(0o444)
    except OSError:
        return {"ok": False, "error": "EVIDENCE_WRITE_REQUIRED"}
    return {"ok": True, "max_ul_prb": max_ul_prb, "source": "model", "observation_path": str(evidence_observation)}


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


def canonical_kpm_styles(styles: object) -> list[dict]:
    if not isinstance(styles, list):
        return []
    return sorted(
        (style for style in styles if isinstance(style, dict)),
        key=lambda style: json.dumps(style, sort_keys=True),
    )


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
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


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
        (temporary / "runtime-input").mkdir()
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
                        {"type": "bind", "source": str(workspace / "runtime-input"), "target": "/run/redcap-drl", "read_only": True},
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


def freeze_measurement_post(args: argparse.Namespace) -> int:
    try:
        workspace, lock, _ = load_workspace(args.workspace)
    except ValueError as error:
        return fail(str(error))
    if lock.get("profile") != "ul-prb-cap-v1":
        return fail("只有 ul-prb-cap-v1 可以凍結 measurement_post policy")
    if (workspace / "run/bridge.sock").exists():
        return fail("workspace 必須先停止 bridge；未修改 lock")
    run_ids = args.calibration_run
    if (
        not isinstance(run_ids, list)
        or not run_ids
        or any(not isinstance(run_id, str) or not WORKSPACE_NAME.fullmatch(run_id) for run_id in run_ids)
        or len(set(run_ids)) != len(run_ids)
        or sorted(args.approve_calibration) != sorted(run_ids)
    ):
        return fail("calibration run 與人工 approval 必須為相同且唯一的 run ID 集合")
    if args.freshness_window_ms < 0 or args.cell_ue_max_skew_ms < 0 or args.min_valid_paired_samples < 1:
        return fail("measurement_post 門檻必須是非負毫秒值，且最少樣本數至少為 1")

    fingerprint = None
    paired_samples = 0
    for run_id in run_ids:
        try:
            manifest = json.loads((workspace / "artifacts/runs" / run_id / "manifest.json").read_text(encoding="utf-8"))
            discovery = manifest["gates"]["discover-kpm"]
            qualification = manifest["gates"]["qualify-kpm"]
            node_id = qualification["node_id"]
            node = next(node for node in discovery["capabilities"]["nodes"] if node["node_id"] == node_id)
            cell = qualification["cell"]
            ue = qualification["ue"]
            calibration = qualification["measurement_post"]
        except (OSError, StopIteration, KeyError, TypeError, json.JSONDecodeError):
            return fail(f"calibration evidence 無效：{run_id}")
        if not isinstance(cell, list) or not isinstance(ue, list) or not cell or not ue:
            return fail(f"calibration evidence 缺少 cell/UE observations：{run_id}")
        try:
            freshness_age_ms = calibration.get("latest_freshness_age_ms", calibration["max_freshness_age_ms"])
            if (
                calibration["event_time_origin"] != "e2_indication_collectStartTime_ms"
                or int(calibration["valid_paired_samples"]) < 1
                or int(freshness_age_ms) > args.freshness_window_ms
            ):
                return fail(f"calibration 不符合批准的 freshness 門檻：{run_id}")
        except (KeyError, TypeError, ValueError):
            return fail(f"calibration freshness evidence 無效：{run_id}")
        current_fingerprint = {
            "node_id": node_id,
            "kpm_styles": canonical_kpm_styles(node.get("kpm_styles")),
            "cell_metrics": sorted({name for sample in cell for name in sample.get("measurements", {})}),
            "ue_metrics": sorted({name for sample in ue for name in sample.get("measurements", {})}),
            "event_time_origin": "e2_indication_collectStartTime_ms",
            "release": lock["release"],
            "images": lock["images"],
        }
        if fingerprint is None:
            fingerprint = current_fingerprint
        elif fingerprint != current_fingerprint:
            return fail("calibration fingerprint 不一致；未修改 lock")
        try:
            pairs = pair_kpm_samples({"cell": cell, "ue": ue})
        except (KeyError, TypeError):
            return fail(f"calibration time evidence 無效：{run_id}")
        for cell_sample, ue_sample, skew_ms in pairs:
            try:
                time_origins_proven = (
                    cell_sample["source_seq_origin"] == "e2_indication"
                    and ue_sample["source_seq_origin"] == "e2_indication"
                    and int(cell_sample["timestamp_ms"]) > 0
                    and int(ue_sample["timestamp_ms"]) > 0
                )
                skew_ms = int(skew_ms)
            except (KeyError, TypeError, ValueError):
                return fail(f"calibration time evidence 無效：{run_id}")
            if not time_origins_proven or skew_ms > args.cell_ue_max_skew_ms:
                return fail(f"calibration 不符合批准的 time/skew 門檻：{run_id}")
            paired_samples += 1
    if paired_samples < args.min_valid_paired_samples:
        return fail("calibration valid paired samples 少於批准門檻；未修改 lock")

    updated_lock = dict(lock)
    updated_lock["measurement_post"] = {
        "status": "FROZEN",
        "approved_calibration_run": run_ids[0],
        "approved_calibration_runs": run_ids,
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "freshness_window_ms": args.freshness_window_ms,
        "cell_ue_max_skew_ms": args.cell_ue_max_skew_ms,
        "min_valid_paired_samples": args.min_valid_paired_samples,
        "fingerprint": fingerprint,
    }
    temporary = workspace / ".workspace.lock.json.tmp"
    write_json(temporary, updated_lock)
    temporary.replace(workspace / "workspace.lock.json")
    print(json.dumps({
        "workspace": str(workspace),
        "gate_status": "MEASUREMENT_POST_FROZEN_NO_CONTROL",
        "calibration_runs": run_ids,
        "safe_next_command": f"redcap_drl_xapp.sh up --workspace {workspace}",
    }))
    return 0


def overlay_command(workspace: Path, *args: str, capture: bool = False) -> subprocess.CompletedProcess:
    command = [
        "docker", "compose", "-p", f"redcap-drl-{workspace.name.lower().replace('.', '-')}",
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
    if args.command != "up":
        try:
            (workspace / "run/bridge.sock").unlink(missing_ok=True)
        except OSError:
            return fail("workspace bridge socket cleanup 失敗")
    status = {"up": "WORKSPACE_UP", "down": "WORKSPACE_DOWN", "remove": "WORKSPACE_RESOURCES_REMOVED"}[args.command]
    print(json.dumps({"workspace": str(workspace), "gate_status": status, "safe_next_command": f"redcap_drl_xapp.sh status --workspace {workspace}"}))
    return 0


def uds_call(socket_path: Path, request: dict, timeout_seconds: int = DISCOVERY_UDS_TIMEOUT_SECONDS) -> dict:
    import socket

    alias_dir = None
    connect_path = str(socket_path)
    if len(os.fsencode(connect_path)) >= 108:
        alias_dir = Path(tempfile.mkdtemp(prefix="redcap-drl-uds-"))
        connect_path = str(alias_dir / "bridge.sock")
        (alias_dir / "bridge.sock").symlink_to(socket_path)
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(timeout_seconds)
            client.connect(connect_path)
            client.sendall(json.dumps(request).encode("utf-8"))
            return json.loads(client.recv(1024 * 1024))
    finally:
        if alias_dir is not None:
            shutil.rmtree(alias_dir, ignore_errors=True)


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
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("finalized_at"):
        raise OSError("EVIDENCE_FINALIZED")
    with (run_dir / "events.ndjson").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, sort_keys=True) + "\n")


def _record_final_event(run_dir: Path, event: dict) -> None:
    if event.get("event") != "CONTROL_RUN_FINISHED":
        raise OSError("FINAL_EVENT_REQUIRED")
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("finalized_at"):
        raise OSError("EVIDENCE_FINALIZATION_REQUIRED")
    with (run_dir / "events.ndjson").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, sort_keys=True) + "\n")


def emit_json(record: dict) -> None:
    print(json.dumps(record))


def evidence_writable(run_dir: Path) -> bool:
    try:
        for name in ("manifest.json", "events.ndjson", "control_journal.json"):
            with (run_dir / name).open("a", encoding="utf-8"):
                pass
    except OSError:
        return False
    return True


def bridge_operations(workspace: Path, lock: dict, operations: list[str], run_dir: Path, manifest: dict) -> dict:
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
        gate_name = {"discover": "discover-kpm", "observe": "probe-kpm", "qualify": "qualify-kpm", "recover": "recover"}[operation]
        record_event(run_dir, {"event": gate_name, "operation": operation, "result": result})
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
                "cadence": result.get("cadence"),
                "measurement_post": result.get("measurement_post"),
                "qualification": "QUALIFIED" if result.get("ok") and "qualify" in operations else "UNPROVED",
            },
        )
    return result


def bridge_gate(args: argparse.Namespace) -> int:
    try:
        workspace, lock, _ = load_workspace(args.workspace)
    except ValueError as error:
        return fail(str(error))
    run_dir, manifest = create_evidence(workspace, lock, args.command)
    operations = (
        ["discover", "qualify"] if args.command == "qualify-kpm"
        else ["discover", "observe"] if args.command == "probe-kpm"
        else [{"discover-kpm": "discover", "recover": "recover"}[args.command]]
    )
    result = bridge_operations(workspace, lock, operations, run_dir, manifest)
    manifest["gate_status"] = "PASS" if result.get("ok") else "FAIL"
    manifest["safe_next_command"] = (
        f"redcap_drl_xapp.sh qualify-kpm --workspace {workspace}"
        if result.get("ok") and args.command in {"discover-kpm", "probe-kpm"}
        else f"redcap_drl_xapp.sh status --workspace {workspace}"
    )
    manifest["finalized_at"] = datetime.now(timezone.utc).isoformat()
    try:
        write_json(run_dir / "manifest.json", manifest)
    except OSError:
        return fail("EVIDENCE_FINALIZATION_FAILED")
    print(json.dumps({"workspace": str(workspace), "run_id": manifest["run_id"], "gate_status": manifest["gate_status"], "evidence_manifest_path": str(run_dir / "manifest.json"), "safe_next_command": manifest["safe_next_command"]}))
    status = 0 if result.get("ok") else 4
    return (status, result) if getattr(args, "capture_result", False) else status


def qualify_control_run(workspace: Path, lock: dict, run_dir: Path, manifest: dict) -> dict:
    return bridge_operations(workspace, lock, ["discover", "qualify"], run_dir, manifest)


def control_once_in_run(workspace: Path, lock: dict, candidate: dict, run_dir: Path, manifest: dict) -> int:
    manifest["candidate"] = candidate
    marker_collector = start_gnb_marker_collector(workspace, lock, run_dir / "gnb_apply_excerpt.log")
    if marker_collector is None:
        manifest["gates"]["control"] = {"collector": {"ok": False, "error": "GNB_MARKER_COLLECTOR_REQUIRED"}}
        manifest["gate_status"] = "FAIL"
        return 4
    if not evidence_writable(run_dir):
        stop_gnb_marker_collector(marker_collector)
        manifest["gates"]["control"] = {"evidence": {"ok": False, "error": "EVIDENCE_WRITE_REQUIRED"}}
        manifest["gate_status"] = "FAIL"
        return 4
    try:
        write_json(run_dir / "control_journal.json", {"state": "OPEN_PENDING", "control_attempted": True})
    except OSError:
        stop_gnb_marker_collector(marker_collector)
        manifest["gates"]["control"] = {"evidence": {"ok": False, "error": "EVIDENCE_WRITE_REQUIRED"}}
        manifest["gate_status"] = "FAIL"
        return 4
    socket_path = workspace / "run/bridge.sock"

    def call(request: dict) -> dict:
        try:
            result = uds_call(socket_path, request, timeout_seconds=CONTROL_UDS_TIMEOUT_SECONDS)
        except (OSError, json.JSONDecodeError) as error:
            result = {"ok": False, "error": "BRIDGE_UNREACHABLE", "detail": str(error)}
        record_event(run_dir, {"operation": request["operation"], "result": result})
        return result

    try:
        opened = call(
            {
                "protocol_version": 1,
                "request_id": uuid.uuid4().hex,
                "operation": "open",
                "profile_id": lock["profile"],
                "mode": "control-once",
            }
        )
        session_id = opened.get("session_id") if opened.get("ok") else None
        if isinstance(session_id, str):
            acted = call(
                {
                    "protocol_version": 1,
                    "request_id": uuid.uuid4().hex,
                    "operation": "act",
                    "profile_id": lock["profile"],
                    "session_id": session_id,
                    "action": {"max_ul_prb": candidate["max_ul_prb"]},
                }
            )
            closed = call(
                {
                    "protocol_version": 1,
                    "request_id": uuid.uuid4().hex,
                    "operation": "close",
                    "profile_id": lock["profile"],
                    "session_id": session_id,
                }
            )
        else:
            acted = {"ok": False, "error": "CONTROL_OPEN_REQUIRED"}
            closed = {"ok": False, "error": "CONTROL_OPEN_REQUIRED"}
    finally:
        stop_gnb_marker_collector(marker_collector)
    manifest["gates"]["control"] = {"open": opened, "act": acted, "close": closed}
    manifest["gate_status"] = "PASS" if all(result.get("ok") for result in (opened, acted, closed)) else "FAIL"
    manifest["safe_next_command"] = f"redcap_drl_xapp.sh status --workspace {workspace}"
    return 0 if manifest["gate_status"] == "PASS" else 4


def control_once(workspace: Path, lock: dict, candidate: dict) -> int:
    run_dir, manifest = create_evidence(workspace, lock, "run")
    status = control_once_in_run(workspace, lock, candidate, run_dir, manifest)
    try:
        write_json(run_dir / "manifest.json", manifest)
    except OSError:
        return fail("EVIDENCE_FINALIZATION_FAILED")
    emit_json(
        {
            "workspace": str(workspace),
            "run_id": manifest["run_id"],
            "gate_status": manifest["gate_status"],
            "evidence_manifest_path": str(run_dir / "manifest.json"),
            "safe_next_command": manifest["safe_next_command"],
        }
    )
    return status


def finalize_control_run(workspace: Path, run_dir: Path, manifest: dict, status: int) -> int:
    manifest["gate_status"] = "PASS" if status == 0 else "FAIL"
    manifest["finalized_at"] = datetime.now(timezone.utc).isoformat()
    try:
        package_journal = run_dir / "control_journal.json"
        journal = json.loads(package_journal.read_text(encoding="utf-8"))
        if journal.get("control_attempted") is True:
            workspace_journal = workspace / "run/control_journal.json"
            if not workspace_journal.is_file():
                raise OSError("workspace control journal required")
            final_journal = json.loads(workspace_journal.read_text(encoding="utf-8"))
            if not isinstance(final_journal, dict):
                raise OSError("invalid workspace control journal")
            final_state = final_journal.get("state")
            if final_state not in FINAL_CONTROL_JOURNAL_STATES or (status == 0 and final_state != "COMPLETED"):
                raise OSError("workspace control journal not terminal")
            journal.update(final_journal)
            journal["control_attempted"] = True
            write_json(package_journal, journal)
        write_json(run_dir / "manifest.json", manifest)
        _record_final_event(
            run_dir,
            {"event": "CONTROL_RUN_FINISHED", "gate_status": manifest["gate_status"]},
        )
    except (OSError, AttributeError, json.JSONDecodeError):
        return fail("EVIDENCE_FINALIZATION_FAILED")
    emit_json(
        {
            "event": "CONTROL_RUN_FINISHED",
            "run_id": manifest["run_id"],
            "gate_status": manifest["gate_status"],
            "finalized_at": manifest["finalized_at"],
            "evidence_manifest_path": str(run_dir / "manifest.json"),
        }
    )
    return status


def execute_control_run(args: argparse.Namespace, workspace: Path, lock: dict) -> int:
    def preflight_failure(message: str) -> int:
        status = finalize_control_run(workspace, run_dir, manifest, 4)
        return fail(message) if status == 4 else status

    run_dir, manifest = create_evidence(workspace, lock, "run")
    try:
        record_event(run_dir, {"event": "CONTROL_RUN_STARTED", "run_id": manifest["run_id"]})
    except OSError:
        return fail("EVIDENCE_WRITE_REQUIRED")
    emit_json({"event": "CONTROL_RUN_STARTED", "run_id": manifest["run_id"], "evidence_manifest_path": str(run_dir / "manifest.json")})
    if lock["profile"] == "none":
        manifest["gates"]["profile"] = {"ok": False, "error": "PROFILE_FORBIDS_CONTROL"}
        return preflight_failure("profile=none 禁止 E2 control")
    smoke_status = verify(argparse.Namespace(workspace=workspace))
    manifest["gates"]["verify"] = {"ok": smoke_status == 0}
    try:
        record_event(run_dir, {"event": "verify", "result": manifest["gates"]["verify"]})
    except OSError:
        return fail("EVIDENCE_WRITE_REQUIRED")
    if smoke_status != 0:
        return preflight_failure("runtime smoke 或 RIC reachability 未通過；qualification 與 control 均未啟動")
    try:
        qualification = qualify_control_run(workspace, lock, run_dir, manifest)
    except OSError:
        return fail("EVIDENCE_WRITE_REQUIRED")
    if not qualification.get("ok"):
        return preflight_failure("KPM qualification 未通過；模型與 control 均未啟動")
    candidate = (
        model_candidate(workspace, args.entrypoint, qualification, run_dir)
        if args.controller == "model"
        else validation_candidate(args.controller, qualification.get("cell", []))
    )
    if args.controller == "model":
        model_observation = run_dir / "model_observation.json"
        model_decision = run_dir / "model_decision.json"
        if model_observation.is_file():
            manifest["evidence"]["model_observation"] = str(model_observation)
        if candidate.get("ok") and model_decision.is_file():
            manifest["evidence"]["model_decision"] = str(model_decision)
    try:
        record_event(run_dir, {"event": "candidate", "result": candidate})
    except OSError:
        return fail("EVIDENCE_WRITE_REQUIRED")
    if not candidate.get("ok"):
        return preflight_failure(candidate["error"] + "；未發送 act")
    return finalize_control_run(workspace, run_dir, manifest, control_once_in_run(workspace, lock, candidate, run_dir, manifest))


def run_model(args: argparse.Namespace) -> int:
    if args.controller == "model":
        if not args.entrypoint:
            return fail("model controller 必須提供 --entrypoint module:callable")
        if not valid_entrypoint(args.entrypoint):
            return fail("entrypoint 必須是 module:callable")
    try:
        workspace, lock, _ = load_workspace(args.workspace)
    except ValueError as error:
        return fail(str(error))
    if args.enable_control:
        status = execute_control_run(args, workspace, lock)
        if args.teardown:
            teardown_status = lifecycle(argparse.Namespace(command="down", workspace=workspace))
            if status == 0 and teardown_status != 0:
                return teardown_status
        return status
    if args.controller != "model":
        return fail("fixed/greedy controller 僅能搭配 --enable-control 與完整 live gates")
    return fail("MODEL_OBSERVATION_REQUIRED：model controller 必須搭配 --enable-control 與 30 筆 qualified samples")


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
    if updated_lock.get("profile") == "ul-prb-cap-v1" and updated_lock.get("measurement_post", {}).get("status") == "FROZEN":
        updated_lock["measurement_post"] = {"status": "UNFROZEN", "invalidated_by": "release-upgrade"}
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
    if args.command == "freeze-measurement-post":
        return freeze_measurement_post(args)
    if args.command in {"discover-kpm", "probe-kpm", "qualify-kpm", "recover"}:
        return bridge_gate(args)
    if args.command == "run":
        return run_model(args)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
