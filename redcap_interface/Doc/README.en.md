# RedCap Interface Docs

[English](./README.en.md) | [繁體中文](./README.zh-TW.md)

## Purpose
- Operator-facing RedCap and mMTC shell entrypoints live here.
- Use this folder for running RFsim, paper demos, and quick interface validation.

## Main Bash Entries
| Script | Use |
|---|---|
| `../../mmtc.menu.bash` | Single public entry: project introduction, accepted evidence, experiment profiles, and advanced RFsim |
| `../mmtc.menu.bash` | Compatibility shim for existing callers |
| `mmtc.display.bash` | Paper demo/live-panel dispatcher explicitly delegated by the main entry; direct calls remain compatible |
| `validate_redcap_interface.sh` | Non-invasive syntax and dependency validation |

## Step-by-Step Recap
```bash
./mmtc.menu.bash
./mmtc.menu.bash intro
./mmtc.menu.bash performance
bash redcap_interface/validate_redcap_interface.sh
```

## Experiment Profile v1

```bash
# Create interactively; only writes below test_log/runtime_configs/ and does not start Docker.
./mmtc.menu.bash experiment

# Validate and show normalized content without generating an overlay.
./mmtc.menu.bash preview-profile test_log/runtime_configs/<run-id>.profile.env

# Explicitly execute the existing smoke path.
./mmtc.menu.bash run-profile test_log/runtime_configs/<run-id>.profile.env smoke
```

Profile v1 fixes `REDCAP_TOPOLOGY=single_gnb_rfsim`, `REDCAP_GNB_COUNT=1`, `REDCAP_CU_DU_SPLIT=0`, and `MMTC_TOTAL_UES=56`. It configures active UEs, 51/106 PRB, gNB/CN/policy/contract paths, `case_a/case_b`, and existing xApp/dApp flags. Multiple gNBs and CU/DU split are unsupported.

## Profile Trace

| Step | File / symbol | Input | Output / owner | Marker | Next | Status |
|---|---|---|---|---|---|---|
| 1 | `mmtc.menu.bash:create_experiment_profile` | Interactive values | version-1 profile / operator | `[OK] Experiment profile created` | preview | implemented |
| 2 | `mmtc.menu.bash:load_profile` | profile | allowlisted normalized fields / main menu | normalized `KEY=value` output | adapter | implemented |
| 3 | `mmtc.menu.bash:apply_loaded_profile` | validated fields | existing environment-variable state / runtime wrapper | main menu header and smoke info | `run_smoke` | implemented |
| 4 | `fc_mmtc_smoke_validation.sh` | active UE, RF, xApp/dApp flags | Compose services and overlay / smoke runner | `[INFO] Active UE selection` | gNB/xApp/dApp runtime | implemented |
| 5 | `redcap_control_contract.yaml` + policy | existing control selection | xApp hint and dApp/gNB accept/reject/apply boundary | feature-specific ACK/apply markers | checker/report | implemented; no new control semantics |

## Related Public Manuals
- Install from zero: `redcap_doc/manuals/install/redcap_begin_from_zero.en.md`.
- Rebuild after changes: `redcap_doc/manuals/install/redcap_rebuild_after_changes.en.md`.
- Paper recovery tutorials: `redcap_doc/evluation_recover/README.en.md`.
