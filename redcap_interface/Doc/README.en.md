# RedCap Interface Docs

## Purpose
- Operator-facing RedCap and mMTC shell entrypoints live here.
- Use this folder for running RFsim, paper demos, and quick interface validation.

## Main Bash Entries
| Script | Use |
|---|---|
| `mmtc.menu.bash` | Daily RFsim work: config mounts, Docker bring-up, Gate 3, 256QAM, RX mode, DRX/eDRX/PSM knobs |
| `mmtc.display.bash` | Paper demos, live panels, and display-oriented reproduction flows |
| `validate_redcap_interface.sh` | Non-invasive syntax and dependency validation |

## Step-by-Step Recap
```bash
bash redcap_interface/mmtc.menu.bash
bash redcap_interface/mmtc.display.bash
bash redcap_interface/validate_redcap_interface.sh
```
