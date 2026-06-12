# Bash Library Docs

## Purpose
- This folder contains implementation scripts called by the two public menus.
- Files use the `fc_` prefix to mark function-level helpers.

## Naming Rule
- `fc_*.sh`: shell function script.
- `fc_*.bash`: Bash-specific function script.
- `fc_*.py`: Python function script.

## Usage Rule
- Prefer calling `redcap_interface/mmtc.menu.bash` or `redcap_interface/mmtc.display.bash`.
- Call `fc_*` directly only when debugging a specific implementation.
