# RedCap Interface

[English](./Doc/README.en.md) | [繁體中文](./Doc/README.zh-TW.md)

## Purpose
- Keep RedCap/mMTC operator-facing shell entry points out of `ci-scripts/`.
- Leave Python/C/YAML/XML implementation assets in `ci-scripts/`.
- Run commands from the repository root unless a script states otherwise.
- Keep one public operator entry at repository root: `../mmtc.menu.bash`. The local `mmtc.menu.bash` is a compatibility shim.
- Keep functional helpers under `bash_library/fc_*`.

## Entry Points
| Script | Role |
|---|---|
| `../mmtc.menu.bash` | Public entry: project introduction, accepted evidence, versioned experiment profiles, and advanced RFsim operations |
| `mmtc.menu.bash` | Compatibility shim for existing callers |
| `mmtc.display.bash` | Internal/direct compatibility dispatcher for live panels and Paper 07/08/11 reproduction |
| `mmtc.ment.bash` | Legacy spelling alias that forwards to `mmtc.menu.bash` |
| `validate_redcap_interface.sh` | non-invasive dependency and syntax validator |

## Functional Library
| Path | Rule |
|---|---|
| `bash_library/fc_*.sh` / `bash_library/fc_*.bash` | Shell implementations called by the main entry, internal display dispatcher, or compatibility shims |
| `bash_library/fc_*.py` | Python implementations called by menus or shims |
| legacy root scripts | Compatibility shims retained because reports and manuals still reference the old paths |

## Common Commands
```bash
./mmtc.menu.bash
./mmtc.menu.bash intro
./mmtc.menu.bash performance
MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1 ./mmtc.menu.bash gate3
```

## Validation
```bash
bash redcap_interface/validate_redcap_interface.sh
```
