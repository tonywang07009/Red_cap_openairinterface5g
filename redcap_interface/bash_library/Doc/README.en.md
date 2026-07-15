# Bash Library Docs

## Purpose
- This folder contains implementations called by the unified main entry, the internal display dispatcher, and compatibility shims.
- Files use the `fc_` prefix to mark function-level helpers.

## Naming Rule
- `fc_*.sh`: shell function script.
- `fc_*.bash`: Bash-specific function script.
- `fc_*.py`: Python function script.

## Usage Rule
- Prefer root `mmtc.menu.bash`; `redcap_interface/mmtc.menu.bash` and direct `mmtc.display.bash` calls remain compatible.
- Call `fc_*` directly only when debugging a specific implementation.
