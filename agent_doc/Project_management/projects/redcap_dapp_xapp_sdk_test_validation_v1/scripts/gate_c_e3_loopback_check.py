#!/usr/bin/env python3
"""Gate C dependency and runtime checker for the local libe3 E3 loopback."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
LIBE3 = ROOT / "dev_refer/dapp_dev_need/libe3"

ROLE_PAIR_SOURCE = LIBE3 / "tests/integration/test_role_pair_posix.cpp"
BENCH_SOURCE = LIBE3 / "tests/integration/bench_full_loop_latency.cpp"
TESTS_CMAKE = LIBE3 / "cmake/libe3Tests.cmake"
DEPENDENCIES_CMAKE = LIBE3 / "cmake/libe3Dependencies.cmake"
MESSAGES_CMAKE = LIBE3 / "messages/CMakeLists.txt"

PREFERRED_BINARY_NAMES = (
    "test_role_pair_posix",
    "test_bench_full_loop_latency",
    "bench_full_loop_latency",
)

DEFAULT_BUILD_DIR = LIBE3 / "build/redcap-gate-c"
DEFAULT_LOG_DIR = ROOT / "test_log/compiler_logs"
ASN1C_CANDIDATES = (Path("/opt/asn1c/bin/asn1c"),)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def find_command(name: str, extra_paths: tuple[Path, ...] = ()) -> Path | None:
    resolved = shutil.which(name)
    if resolved:
        return Path(resolved)
    for path in extra_paths:
        if path.is_file() and path.stat().st_mode & 0o111:
            return path
    return None


def has_command(name: str) -> bool:
    return find_command(name) is not None


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_source_evidence(errors: list[str]) -> None:
    required = [
        ROLE_PAIR_SOURCE,
        BENCH_SOURCE,
        TESTS_CMAKE,
        DEPENDENCIES_CMAKE,
        MESSAGES_CMAKE,
    ]
    for path in required:
        if not path.exists():
            errors.append(f"missing source evidence: {rel(path)}")

    if errors:
        return

    role_pair = text(ROLE_PAIR_SOURCE)
    for needle in ["E3Role::RAN", "E3Role::DAPP", "wait_for_setup", "subscribe", "indications"]:
        if needle not in role_pair:
            errors.append(f"{rel(ROLE_PAIR_SOURCE)} missing marker: {needle}")

    bench = text(BENCH_SOURCE)
    for needle in ["send_control", "Full-loop latency benchmark", "Deliver control (dApp -> RAN)"]:
        if needle not in bench:
            errors.append(f"{rel(BENCH_SOURCE)} missing marker: {needle}")

    tests_cmake = text(TESTS_CMAKE)
    for needle in ["LIBE3_BUILD_INTEGRATION_TESTS", "LIBE3_ENABLE_ASN1", "asn1_e3ap"]:
        if needle not in tests_cmake:
            errors.append(f"{rel(TESTS_CMAKE)} missing integration requirement: {needle}")

    dependencies = text(DEPENDENCIES_CMAKE)
    if "tl_expected" not in dependencies or "FetchContent" not in dependencies:
        errors.append(f"{rel(DEPENDENCIES_CMAKE)} missing tl_expected FetchContent evidence")

    messages = text(MESSAGES_CMAKE)
    if "asn1c not found" not in messages:
        errors.append(f"{rel(MESSAGES_CMAKE)} missing asn1c requirement evidence")


def discover_binaries() -> list[Path]:
    found: list[Path] = []
    for name in PREFERRED_BINARY_NAMES:
        for path in LIBE3.rglob(name):
            if path.is_file() and path.stat().st_mode & 0o111:
                found.append(path)
    return sorted(set(found), key=lambda p: (PREFERRED_BINARY_NAMES.index(p.name), str(p)))


def discover_fetchcontent_cache() -> list[Path]:
    candidates: list[Path] = []
    for path in LIBE3.rglob("tl_expected-src"):
        if path.is_dir():
            candidates.append(path)
    return sorted(candidates)


def dependency_status() -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []

    for cmd in ["cmake", "c++"]:
        if not has_command(cmd):
            blockers.append(f"missing command: {cmd}")

    if find_command("asn1c", ASN1C_CANDIDATES) is None:
        blockers.append("missing command: asn1c")

    if not has_command("ninja"):
        warnings.append("missing command: ninja; CMake can still use another generator")

    if not discover_fetchcontent_cache():
        warnings.append("tl_expected FetchContent cache not found under libe3 build trees")

    if not has_command("pkg-config"):
        warnings.append("missing command: pkg-config; ZMQ auto-detection may fall back to library search")
    else:
        zmq = subprocess.run(
            ["pkg-config", "--exists", "libzmq"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if zmq.returncode != 0:
            warnings.append("libzmq pkg-config entry not found; use POSIX loopback or install libzmq dev files")

    return blockers, warnings


def run_binary(binary: Path, timeout_s: int) -> int:
    cmd = [str(binary)]
    if binary.name in {"test_bench_full_loop_latency", "bench_full_loop_latency"}:
        cmd.extend(["--link", "posix", "--transport", "ipc", "--encoding", "asn1"])

    print(f"[INFO] running Gate C binary: {rel(binary)}")
    completed = subprocess.run(
        cmd,
        cwd=LIBE3,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout_s,
        check=False,
    )
    if completed.stdout:
        print(completed.stdout.rstrip())
    if completed.returncode == 0:
        print("[PASS] Gate C E3 loopback runtime evidence captured")
        return 0
    print(f"[FAIL] Gate C binary exited with code {completed.returncode}")
    return 1


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def run_logged(command: list[str], label: str, log_dir: Path, cwd: Path) -> tuple[int, Path]:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{label}_{timestamp()}.log"
    print(f"[INFO] running: {' '.join(command)}")
    print(f"[INFO] log: {rel(log_path)}")
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_path.write_text(completed.stdout, encoding="utf-8")
    if completed.stdout:
        print(completed.stdout.rstrip())
    return completed.returncode, log_path


def try_configure(build_dir: Path, log_dir: Path, allow_fetch: bool) -> int:
    if not has_command("cmake"):
        print("[BLOCKED] missing command: cmake")
        return 2
    if not has_command("c++"):
        print("[BLOCKED] missing command: c++")
        return 2

    command = [
        "cmake",
        "-S",
        str(LIBE3),
        "-B",
        str(build_dir),
        "-DLIBE3_BUILD_INTEGRATION_TESTS=ON",
        "-DLIBE3_ENABLE_ZMQ=OFF",
    ]
    label = "gate_c_libe3_configure_fetch" if allow_fetch else "gate_c_libe3_configure"
    if allow_fetch:
        print("[WARN] network FetchContent is enabled for this configure attempt")
    else:
        command.append("-DFETCHCONTENT_FULLY_DISCONNECTED=ON")

    rc, log_path = run_logged(command, label, log_dir, ROOT)
    if rc == 0:
        print(f"[PASS] Gate C libe3 configure completed: {rel(log_path)}")
        return 0
    print(f"[BLOCKED] Gate C libe3 configure failed: {rel(log_path)}")
    return 2


def print_build_hint() -> None:
    build_dir = "dev_refer/dapp_dev_need/libe3/build/redcap-gate-c"
    print("[INFO] suggested Gate C build/run commands:")
    print(
        "  python3 -B "
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/"
        "gate_c_e3_loopback_check.py --try-configure"
    )
    print(
        "  python3 -B "
        "agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/"
        "gate_c_e3_loopback_check.py --try-configure --allow-fetch"
    )
    print(
        "  cmake -S dev_refer/dapp_dev_need/libe3 "
        f"-B {build_dir} "
        "-DLIBE3_BUILD_INTEGRATION_TESTS=ON "
        "-DLIBE3_ENABLE_ZMQ=OFF "
        "-DFETCHCONTENT_FULLY_DISCONNECTED=ON"
    )
    print(f"  cmake --build {build_dir} --target test_role_pair_posix test_bench_full_loop_latency")
    print(f"  ctest --test-dir {build_dir} -R test_role_pair_posix --output-on-failure")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, help="existing Gate C binary to run")
    parser.add_argument("--try-configure", action="store_true", help="run CMake configure and save a compiler log")
    parser.add_argument("--allow-fetch", action="store_true", help="allow CMake FetchContent network access during configure")
    parser.add_argument("--build-dir", type=Path, default=DEFAULT_BUILD_DIR, help="libe3 build directory for --try-configure")
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR, help="log directory for --try-configure")
    parser.add_argument("--timeout-s", type=int, default=90, help="runtime timeout for an existing binary")
    args = parser.parse_args(argv)

    errors: list[str] = []
    require_source_evidence(errors)
    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1

    print("[PASS] Gate C source evidence is present under dev_refer/dapp_dev_need/libe3")

    blockers, warnings = dependency_status()
    for warning in warnings:
        print(f"[WARN] {warning}")

    if args.try_configure:
        configure_rc = try_configure(args.build_dir, args.log_dir, args.allow_fetch)
        if configure_rc != 0:
            return configure_rc

    binaries = [args.binary.resolve()] if args.binary else discover_binaries()
    existing_binaries = [path for path in binaries if path.exists() and path.is_file()]
    if existing_binaries:
        return run_binary(existing_binaries[0], args.timeout_s)

    if blockers:
        for blocker in blockers:
            print(f"[BLOCKED] {blocker}")
        print("[BLOCKED] Gate C runtime was not run because no existing libe3 loopback binary was found")
        print_build_hint()
        return 2

    print("[BLOCKED] no existing libe3 loopback binary was found")
    print_build_hint()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
