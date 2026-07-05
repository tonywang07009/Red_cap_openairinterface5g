# RedCap Interface

[English](./Doc/README.en.md) | [繁體中文](./Doc/README.zh-TW.md)

## Purpose
- Keep RedCap/mMTC operator-facing shell entry points out of `ci-scripts/`.
- Leave Python/C/YAML/XML implementation assets in `ci-scripts/`.
- Run commands from the repository root unless a script states otherwise.
- Keep the public operator surface small: daily RFsim work uses `mmtc.menu.bash`, and paper/demo work uses `mmtc.display.bash`.
- Keep functional helpers under `bash_library/fc_*`.

## Entry Points
| Script | Role |
|---|---|
| `mmtc.menu.bash` | Daily RFsim operator menu: gNB config, RedCap RX mode, 256QAM flags, DRX/eDRX/PSM knobs, Docker bring-up, Gate 3 run |
| `mmtc.display.bash` | Paper/demo display menu: live iperf panel, Paper 08/11 runners, legacy Paper 07 display menu |
| `mmtc.ment.bash` | Legacy spelling alias that forwards to `mmtc.menu.bash` |
| `validate_redcap_interface.sh` | non-invasive dependency and syntax validator |

## Functional Library
| Path | Rule |
|---|---|
| `bash_library/fc_*.sh` / `bash_library/fc_*.bash` | Shell implementations called by the two public menus or by compatibility shims |
| `bash_library/fc_*.py` | Python implementations called by menus or shims |
| legacy root scripts | Compatibility shims retained because reports and manuals still reference the old paths |

## Common Commands
```bash
bash redcap_interface/mmtc.menu.bash
bash redcap_interface/mmtc.display.bash
MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1 bash redcap_interface/mmtc.menu.bash gate3
```

## Validation
```bash
bash redcap_interface/validate_redcap_interface.sh
```
