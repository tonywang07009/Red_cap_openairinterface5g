#!/usr/bin/env python3
"""Live iperf3 UL/DL panel for the RedCap RFsim containers."""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "test_log/compiler_logs"
BITRATE_RE = re.compile(r"(?P<value>[0-9.]+)\s+(?P<unit>[KMG])bits/sec")
LOSS_RE = re.compile(r"(?P<lost>[0-9]+)/(?P<total>[0-9]+)\s+\((?P<pct>[0-9.]+)%\)")
JITTER_RE = re.compile(r"(?P<jitter>[0-9.]+)\s+ms")


@dataclass
class DirectionState:
  name: str
  rate: str
  port: int
  log_path: Path
  current_mbps: float | None = None
  receiver_mbps: float | None = None
  jitter_ms: float | None = None
  lost_packets: int | None = None
  total_packets: int | None = None
  lost_percent: float | None = None
  last_line: str = "waiting"
  return_code: int | None = None


def run_cmd(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
  proc = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
  if check and proc.returncode != 0:
    raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(args)}\n{proc.stderr.strip()}")
  return proc


def docker_exec(container: str, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
  return run_cmd(["docker", "exec", container, *args], check=check)


def parse_ipv4(output: str) -> str:
  match = re.search(r"\binet\s+([0-9]+(?:\.[0-9]+){3})/", output)
  if not match:
    raise RuntimeError(f"cannot parse IPv4 from: {output.strip()}")
  return match.group(1)


def container_ipv4(container: str, interface: str) -> str:
  proc = docker_exec(container, ["ip", "-4", "-o", "addr", "show", "dev", interface])
  return parse_ipv4(proc.stdout)


def start_iperf_servers(server_container: str, ports: list[int], log_path: Path) -> None:
  port_text = " ".join(str(port) for port in ports)
  script = (
    "pids=$(pidof iperf3 2>/dev/null || true); "
    '[ -z "$pids" ] || kill $pids; '
    f"for p in {port_text}; do iperf3 -s -D -p \"$p\"; done"
  )
  proc = docker_exec(server_container, ["sh", "-c", script], check=False)
  log_path.write_text(
    "\n".join(
      [
        f"# collected_at={time.strftime('%Y-%m-%dT%H:%M:%S%z')}",
        f"# ports={port_text}",
        f"# return_code={proc.returncode}",
        proc.stdout,
        proc.stderr,
      ]
    ),
    encoding="utf-8",
  )
  if proc.returncode != 0:
    raise RuntimeError(f"failed to start iperf3 server(s); see {log_path}")


def to_mbps(value: float, unit: str) -> float:
  if unit == "K":
    return value / 1000.0
  if unit == "G":
    return value * 1000.0
  return value


def update_state_from_line(state: DirectionState, line: str) -> None:
  state.last_line = line.strip()
  bitrate = BITRATE_RE.search(line)
  if bitrate:
    mbps = to_mbps(float(bitrate.group("value")), bitrate.group("unit"))
    state.current_mbps = mbps
    if "receiver" in line:
      state.receiver_mbps = mbps

  jitter = JITTER_RE.search(line)
  if jitter and "bits/sec" in line:
    state.jitter_ms = float(jitter.group("jitter"))

  loss = LOSS_RE.search(line)
  if loss:
    state.lost_packets = int(loss.group("lost"))
    state.total_packets = int(loss.group("total"))
    state.lost_percent = float(loss.group("pct"))


def build_iperf_command(
  *,
  ue_container: str,
  server_ip: str,
  ue_ip: str,
  state: DirectionState,
  protocol: str,
  duration: int,
) -> list[str]:
  cmd = [
    "docker",
    "exec",
    ue_container,
    "iperf3",
    "-c",
    server_ip,
    "-B",
    ue_ip,
    "-p",
    str(state.port),
    "-t",
    str(duration),
    "-i",
    "1",
    "--forceflush",
  ]
  if protocol == "udp":
    cmd.extend(["-u", "-b", state.rate])
  elif state.rate:
    cmd.extend(["-b", state.rate])
  if state.name == "DL":
    cmd.append("-R")
  return cmd


def reader_thread(proc: subprocess.Popen[str], state: DirectionState, lock: threading.Lock) -> None:
  with state.log_path.open("a", encoding="utf-8") as log_file:
    log_file.write(f"# collected_at={time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n")
    log_file.write(f"# direction={state.name}\n")
    log_file.write(f"# offered_rate={state.rate}\n")
    for raw_line in proc.stdout or []:
      log_file.write(raw_line)
      log_file.flush()
      with lock:
        update_state_from_line(state, raw_line)
  proc.wait()
  with lock:
    state.return_code = proc.returncode


def fmt(value: object, suffix: str = "") -> str:
  if value is None:
    return "-"
  if isinstance(value, float):
    return f"{value:.3f}{suffix}"
  return f"{value}{suffix}"


def render_panel(states: list[DirectionState], *, run_id: str, no_clear: bool) -> None:
  if sys.stdout.isatty() and not no_clear:
    print("\033[2J\033[H", end="")
  print(f"[PAPER iperf live panel] run_id={run_id} time={time.strftime('%H:%M:%S')}")
  print("direction offered current_mbps final_rx_mbps jitter_ms loss lost/total rc")
  for state in states:
    lost_total = "-"
    if state.lost_packets is not None and state.total_packets is not None:
      lost_total = f"{state.lost_packets}/{state.total_packets}"
    print(
      f"{state.name:<9} {state.rate:<7} {fmt(state.current_mbps):<12} "
      f"{fmt(state.receiver_mbps):<13} {fmt(state.jitter_ms):<9} "
      f"{fmt(state.lost_percent, '%'):<6} {lost_total:<10} {fmt(state.return_code)}"
    )
  print()
  for state in states:
    print(f"[{state.name}] {state.last_line[:160]}")
  print("", flush=True)


def write_summary_csv(path: Path, run_id: str, states: list[DirectionState], server_ip: str, ue_ip: str) -> None:
  with path.open("w", encoding="utf-8", newline="") as csv_file:
    writer = csv.DictWriter(
      csv_file,
      fieldnames=[
        "run_id",
        "direction",
        "offered_rate",
        "server_ip",
        "ue_ip",
        "current_mbps",
        "receiver_mbps",
        "jitter_ms",
        "lost_packets",
        "total_packets",
        "lost_percent",
        "return_code",
        "log_path",
      ],
    )
    writer.writeheader()
    for state in states:
      writer.writerow(
        {
          "run_id": run_id,
          "direction": state.name,
          "offered_rate": state.rate,
          "server_ip": server_ip,
          "ue_ip": ue_ip,
          "current_mbps": state.current_mbps,
          "receiver_mbps": state.receiver_mbps,
          "jitter_ms": state.jitter_ms,
          "lost_packets": state.lost_packets,
          "total_packets": state.total_packets,
          "lost_percent": state.lost_percent,
          "return_code": state.return_code,
          "log_path": state.log_path,
        }
      )


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="Live iperf3 UL/DL panel for RedCap RFsim.")
  parser.add_argument("--direction", choices=["ul", "dl", "both"], default="both")
  parser.add_argument("--ue", type=int, default=1)
  parser.add_argument("--ue-container")
  parser.add_argument("--server-container", default="oai-ext-dn")
  parser.add_argument("--server-ip")
  parser.add_argument("--ue-ip")
  parser.add_argument("--protocol", choices=["udp", "tcp"], default="udp")
  parser.add_argument("--ul-rate", default="17M")
  parser.add_argument("--dl-rate", default="68M")
  parser.add_argument("--duration", type=int, default=20)
  parser.add_argument("--base-port", type=int, default=5221)
  parser.add_argument("--run-id", default=f"iperf_live_panel_{time.strftime('%Y-%m-%d_%H-%M-%S')}")
  parser.add_argument("--output-dir", type=Path)
  parser.add_argument("--no-clear", action="store_true")
  return parser.parse_args()


def main() -> int:
  args = parse_args()
  ue_container = args.ue_container or f"rfsim5g-oai-nr-ue{args.ue}_redcap"
  output_dir = args.output_dir or (DEFAULT_OUTPUT_ROOT / args.run_id)
  output_dir.mkdir(parents=True, exist_ok=True)

  server_ip = args.server_ip or container_ipv4(args.server_container, "eth0")
  ue_ip = args.ue_ip or container_ipv4(ue_container, "oaitun_ue1")

  states: list[DirectionState] = []
  if args.direction in ("ul", "both"):
    states.append(DirectionState("UL", args.ul_rate, args.base_port, output_dir / f"{args.run_id}_UL.log"))
  if args.direction in ("dl", "both"):
    states.append(DirectionState("DL", args.dl_rate, args.base_port + 1, output_dir / f"{args.run_id}_DL.log"))

  start_iperf_servers(args.server_container, [state.port for state in states], output_dir / f"{args.run_id}_server.log")

  lock = threading.Lock()
  processes: list[subprocess.Popen[str]] = []
  threads: list[threading.Thread] = []
  for state in states:
    cmd = build_iperf_command(
      ue_container=ue_container,
      server_ip=server_ip,
      ue_ip=ue_ip,
      state=state,
      protocol=args.protocol,
      duration=args.duration,
    )
    state.log_path.write_text("# command: " + " ".join(cmd) + "\n", encoding="utf-8")
    proc = subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
    processes.append(proc)
    thread = threading.Thread(target=reader_thread, args=(proc, state, lock), daemon=True)
    thread.start()
    threads.append(thread)

  while any(proc.poll() is None for proc in processes):
    with lock:
      render_panel(states, run_id=args.run_id, no_clear=args.no_clear)
    time.sleep(1)

  for thread in threads:
    thread.join(timeout=2)

  with lock:
    render_panel(states, run_id=args.run_id, no_clear=args.no_clear)
    summary_path = output_dir / f"{args.run_id}_summary.csv"
    write_summary_csv(summary_path, args.run_id, states, server_ip, ue_ip)

  print(f"[INFO] raw output: {output_dir}")
  print(f"[INFO] summary: {summary_path}")
  return 0 if all(state.return_code == 0 for state in states) else 1


if __name__ == "__main__":
  raise SystemExit(main())
