# Script Interface Checklist

## Required Layout
- [x] `redcap_interface/mmtc.menu.bash` exists.
- [x] `redcap_interface/mmtc.display.bash` exists.
- [x] `redcap_interface/bash_library/` exists.
- [x] Functional scripts use the `fc_` prefix.
- [x] Legacy root scripts are shims.

## Required Menu Coverage
- [x] Daily RFsim menu can show mounted config files.
- [x] Daily RFsim menu exposes 256QAM flags.
- [x] Daily RFsim menu exposes RedCap RX and half-duplex knobs.
- [x] Daily RFsim menu exposes DRX/eDRX/PSM environment knobs.
- [x] Daily RFsim menu exposes Gate 3 with `MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1`.
- [x] Display menu routes paper/demo panels outside the daily menu.

## Validation Commands
```bash
bash -n redcap_interface/mmtc.menu.bash
bash -n redcap_interface/mmtc.display.bash
python3 -c 'import ast,pathlib,sys; [ast.parse(pathlib.Path(p).read_text(), filename=p) for p in sys.argv[1:]]' redcap_interface/iperf_live_panel.py redcap_interface/bash_library/fc_iperf_live_panel.py
bash redcap_interface/validate_redcap_interface.sh
```
