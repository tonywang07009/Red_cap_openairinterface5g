# Work Daily - Runtime Menu DL iperf

## Task
- Add downlink iperf support to `ci-scripts/redcap_runtime_menu.sh`.
- Ensure DL testing supports both 64QAM-level and 256QAM profiles.

## Code Change
- Added DL-specific runtime settings:
  - `DL_IPERF_SERVER_IP`
  - `DL_IPERF_RATE`
  - `DL_IPERF_DURATION`
- Added DL iperf runner:
  - starts `iperf3 -s -D` in `oai-ext-dn`
  - resolves UE1 `oaitun_ue1` IPv4
  - runs UE-side reverse iperf with `-R`
  - stores logs under `test_log/compiler_logs/redcap_menu_*_ue1_iperf3_dl.log`
- Updated latest-log lookup to include both UL and DL logs.

## Menu Changes
- Added `9) Enable PAPER-07 DL 64QAM profile`.
  - `PDSCH256QAM=0`
  - `DL rate=106M`
  - `duration=60s`
- Added `10) Enable PAPER-07 DL 256QAM profile`.
  - `PDSCH256QAM=1`
  - `DL rate=141M`
  - `duration=60s`
- Added `11) Run UDP downlink iperf with current DL rate`.
- Added `12) Run UDP downlink iperf with custom DL rate`.

## Usage Note
- Changing `PDSCH256QAM` only changes the next smoke/runtime startup.
- After selecting profile `9` or `10`, run option `2` or `3` to restart/apply UE capability.
- Then run option `11` for DL reverse iperf.

## Documentation
- Updated `analysis/tutorial/paper07_tdd_reproduction_step_by_step.md`.

## Validation
- `bash -n ci-scripts/redcap_runtime_menu.sh`: PASS.
- `printf '9\n\nq\n' | ci-scripts/redcap_runtime_menu.sh`: PASS.
  - Header changed to `DL iperf rate: 106M`, `PDSCH 256QAM: 0`.
- `printf '10\n\nq\n' | ci-scripts/redcap_runtime_menu.sh`: PASS.
  - Header changed to `DL iperf rate: 141M`, `PDSCH 256QAM: 1`.
- DL custom smoke with option `12`: PASS.
  - command path: `env MMTC_DL_IPERF_RATE=1M MMTC_DL_IPERF_DURATION=1 bash -c "printf '12\n1M\n1\n\nq\n' | ci-scripts/redcap_runtime_menu.sh"`
  - receiver: `1.04 Mbits/sec`.
  - jitter: `0.142 ms`.
  - loss: `0/90 (0%)`.
  - log: `test_log/compiler_logs/redcap_menu_2026-05-23_13-40-17_ue1_iperf3_dl.log`.

