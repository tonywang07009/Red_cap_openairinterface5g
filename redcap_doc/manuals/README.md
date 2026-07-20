# RedCap Manuals

## Purpose
- Store stable RedCap operation and reproduction manuals.
- Keep these files separate from temporary process logs under `test_log/`.
- Prefer concise step-by-step procedures that can be rerun by another engineer.

## Current Manuals
| File | Purpose |
|---|---|
| `install/README.zh-TW.md` | 繁體中文安裝、重建、新手 gate 文件入口 |
| `install/README.en.md` | English install, rebuild, and newcomer gate index |
| `install/redcap_begin_from_zero.zh-TW.md` | 繁體中文新手流程：從 0 安裝、編譯、重建 images、跑 29 UE RFsim validation |
| `install/redcap_begin_from_zero.en.md` | English beginner path: install, build, rebuild images, and run 29 UE RFsim validation |
| `install/redcap_rebuild_after_changes.zh-TW.md` | 繁體中文修改 C/xApp/rApp/dApp/config/library 後重建流程 |
| `install/redcap_rebuild_after_changes.en.md` | English rebuild path after C/xApp/rApp/dApp/config/library changes |
| `install/redcap_newcomer_runtime_gate.zh-TW.md` | 繁體中文新手複現 gate 與回饋格式 |
| `install/redcap_newcomer_runtime_gate.en.md` | English newcomer runtime gate and feedback format |
| `redcap_zero_to_build_and_run_guide.zh-TW.md` | 繁體中文新手指南：從 repo root 編譯、重建 images、跑 29 UE RFsim validation |
| `redcap_zero_to_build_and_run_guide.en.md` | English beginner guide: build, image rebuild, and 29 UE RFsim validation |
| `redcap_mmtc_systematic_usage_steps.md` | Baseline 50 UE mMTC validation procedure and troubleshooting notes |
| `redcap_project_onboarding_step_by_step.md` | Step-by-step handoff guide for dependencies, build, UI use, and function modification |
| `aiot_tag_aiotf_architecture.zh-TW.md`, `.en.md` | A-IoT Topology 2, Tag/UE/AIOTF ownership, CN5G profiles, N6 isolation, and blocked standard path |
| `aiot_tag_aiotf_operator.zh-TW.md`, `.en.md` | Registered build, skill, menu, display, evidence, failure, and cleanup procedure |

## Compatibility Note
- The `redcap_zero_to_build_and_run_guide.*.md` files remain as older compatible beginner guides.
- New public install and rebuild work should route through `install/`.

## Related Recovery Manuals
| Folder | Purpose |
|---|---|
| `redcap_doc/evluation_recover/` | Stable step-by-step reproduction procedures for evaluation papers |
