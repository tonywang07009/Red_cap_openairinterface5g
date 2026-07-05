# D2 Script Interface Reorganization

## Goal
- Reduce the operator-facing RedCap script surface to two menus.

## Public Menus
| Script | Role |
|---|---|
| `redcap_interface/mmtc.menu.bash` | Daily RFsim work, Docker bring-up, Gate 3, mounted file checks, 256QAM, RX mode, DRX/eDRX/PSM knobs |
| `redcap_interface/mmtc.display.bash` | Paper reproduction, demo panels, live iperf display, legacy Paper 07 display path |

## Functional Library
| Pattern | Rule |
|---|---|
| `redcap_interface/bash_library/fc_*.sh` | Shell implementation |
| `redcap_interface/bash_library/fc_*.bash` | Bash-specific implementation |
| `redcap_interface/bash_library/fc_*.py` | Python implementation |

## Acceptance Criteria
- [x] Functional scripts are under `bash_library/` with `fc_` prefixes.
- [x] Public menus call library scripts instead of duplicating logic.
- [x] Root-level old script names are compatibility shims.
- [x] Validator checks the new layout.

## Discussion Point
- Shims are retained because active reports and manuals still reference old paths.
