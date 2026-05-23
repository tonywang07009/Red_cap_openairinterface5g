# Work Daily - Runtime Menu 256QAM Switch

## Task
- Add a menu-level switch for RedCap 256QAM capability control.

## Code Change
- Updated `ci-scripts/redcap_runtime_menu.sh`.
- Added `normalize_bool()` for `0/1`, `yes/no`, `on/off`, and `enable/disable` inputs.
- Added runtime state:
  - `PUSCH_256QAM`
  - `PDSCH_256QAM`
- Passed the state into smoke validation:
  - `MMTC_PUSCH_256QAM`
  - `MMTC_PDSCH_256QAM`

## Menu Changes
- Added `7) Configure 256QAM capability`.
- Added `8) Enable PAPER-07 256QAM profile`.
- The PAPER-07 profile sets:
  - `PUSCH256QAM=1`
  - `PDSCH256QAM=1`
  - `iperf rate=35M`
  - `duration=60s`

## Documentation
- Updated `analysis/tutorial/paper07_tdd_reproduction_step_by_step.md` with the runtime menu shortcut.

## Validation
- `bash -n ci-scripts/redcap_runtime_menu.sh`: PASS.
- `printf '8\n\nq\n' | ci-scripts/redcap_runtime_menu.sh`: PASS.
  - Header changed to `PUSCH 256QAM: 1`, `PDSCH 256QAM: 1`, `iperf rate: 35M`, `iperf duration: 60s`.
- `env MMTC_PUSCH_256QAM=yes MMTC_PDSCH_256QAM=on MMTC_IPERF_RATE=35 bash -c "printf 'q\n' | ci-scripts/redcap_runtime_menu.sh"`: PASS.
  - Env values normalized to `PUSCH 256QAM: 1`, `PDSCH 256QAM: 1`, `iperf rate: 35M`.
- `printf '7\nyes\non\nq\n' | ci-scripts/redcap_runtime_menu.sh`: PASS.
  - Manual 256QAM configuration changed both capability flags to `1`.
