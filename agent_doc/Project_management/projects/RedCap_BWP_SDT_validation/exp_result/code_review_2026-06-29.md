# RedCap BWP / SDT Project Code Review - 2026-06-29

## Scope

- Reviewed current implementation changes under `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/`.
- Reviewed the BWP crash fix call chain in `openair2/LAYER2/NR_MAC_gNB/`.
- Focused on Gate 5 / Gate 6 / Gate 7 risks: runtime wrappers, extractors, aggregators, CSV merge behavior, hook inventory, and report wording.

## Findings

| severity | area | finding | status |
|---|---|---|---|
| High | BWP runtime wrapper | `run_bwp_validation.sh` swallowed telnet/docker trigger failures with `|| true`, so a BWP crash row could still be reported as a successful runner row. | Fixed: trigger failures and gNB crash markers are counted after artifact collection, then the wrapper exits non-zero. |
| Medium | Hook audit | `audit_oai_hooks.py` still searched for `void nr_mac_trigger_reconfiguration` after the BWP trigger API changed to `bool`. | Fixed: hook audit now searches for `bool nr_mac_trigger_reconfiguration`. |
| Medium | BWP trigger API | `nr_trigger_bwp_switch()` previously returned success even if candidate CellGroup creation or ASN.1 encoding failed. | Fixed: `nr_mac_trigger_reconfiguration()` now returns `bool`; success is reported only after encode and request submission. |
| High | BWP initial UL BWP rebuild | `configure_initial_ul_bwp()` reused the raw UE `uid` for PUCCH resources after `verify_radio_configuration()` remapped oversubscribed PUCCH reservations. | Fixed: BWP0 initial UL rebuild now uses the same bounded PUCCH reservation index for PUCCH resource sets. |
| High | BWP PUCCH capability guard | `config_pucch_resset0()` and `config_pucch_resset1()` checked `uecap != NULL` but dereferenced optional `phy_ParametersFRX_Diff` unconditionally. Trigger-time UE capability data can omit that subtree, causing SIGSEGV before a diagnostic assertion. | Fixed and runtime-validated on 2026-06-30: trigger0, bidirectional `0 1 0`, and 8-row matrix completed without gNB crash markers. |
| Medium | BWP apply evidence | The project spec required post-ACK BWP apply evidence, but the previous gNB logs only exposed reconfiguration attempts and generic RRC completion. | Fixed: `ack_reconfig()` emits `[RedCap BWP][gNB apply]`, and the extractor exports apply count plus final DL/UL BWP IDs. |

## Review Result

- [Status]: [PASS WITH PAPER-EQUIVALENCE LIMITATION]
- [Reason]: static review issues were fixed, Docker images were rebuilt, and post-fix RFsim evidence now covers single trigger0, bidirectional `0 1 0`, and the eight-row BWP matrix.
- [Runtime evidence]: `20260630_100054_bwp_trigger0_apply_marker`, `20260630_100329_bwp_bidirectional_apply_marker`, and `20260630_100615_bwp_matrix_apply_marker` completed without gNB crash markers.
- [Gate 5 limitation]: `bwp-InactivityTimer`, traffic profile, and switch-delay scenario controls are still wrapper labels unless a later runtime hook proves otherwise.
- [Gate 6 limitation]: SDT probabilities remain marker-classified local RFsim values; `MMTC_RA_ACCESS_STEPS`, `slot10`, and `lambda_dp_5` behavior remains `[Needs Verification]`.
- [Gate 7 limitation]: final CSV, plots, and conclusion text must be refreshed only after new runtime evidence is available.

## Validation Commands

| command | result |
|---|---|
| `rtk git -c core.optionalLocks=false diff --check -- ...` | PASS |
| `rtk bash -n scripts/run_bwp_validation.sh` | PASS |
| `rtk bash -n scripts/run_sdt_validation.sh` | PASS |
| `rtk bash -n scripts/run_bwp_matrix.sh` | PASS |
| `rtk bash -n scripts/run_sdt_matrix.sh` | PASS |
| `rtk python -m py_compile scripts/*.py` | PASS for reviewed project scripts |
| `rtk python scripts/test_extract_bwp_metrics.py` | PASS |
| `rtk python scripts/test_extract_sdt_metrics.py` | PASS |
| `rtk python scripts/test_merge_runtime_metrics.py` | PASS |
| `rtk python scripts/audit_oai_hooks.py` | PASS |
| `rtk bash -lc 'CCACHE_DIR=/tmp/oai-ccache CCACHE_TEMPDIR=/tmp/oai-ccache-tmp cmake --build --preset default --target nr-softmodem ...'` | PASS |
| `rtk bash redcap_interface/redcap_rebuild_local_oai_images.sh` | PASS after optional capability guard and BWP apply marker |
| `BWP_TRIGGER_SEQUENCE=0 ... run_bwp_validation.sh --run` | PASS; `20260630_100054_bwp_trigger0_apply_marker` final apply to BWP0, no crash markers |
| `BWP_TRIGGER_SEQUENCE="0 1 0" ... run_bwp_validation.sh --run` | PASS; `20260630_100329_bwp_bidirectional_apply_marker` final apply to BWP0, no crash markers |
| `rtk bash scripts/run_bwp_matrix.sh --run` | PASS; `20260630_100615_bwp_matrix_apply_marker`, `runs=8`, `runner_failures=0` |
| `rtk python exp_pictture/plot_paper_vs_local.py` | PASS; BWP and SDT plots refreshed after CSV update |

## Next Required Evidence

- Implement or validate real BWP traffic, inactivity timer, and switch-delay hooks before claiming publication-grade paper equivalence.
- Keep SDT 2-step RA, slot10, and `lambda_dp_5` semantics marked `[Needs Verification]` / `[wrapper_label]` until runtime hook impact is proven.
