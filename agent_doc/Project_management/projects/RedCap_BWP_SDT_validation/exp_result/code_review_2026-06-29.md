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
| High | BWP PUCCH capability guard | `config_pucch_resset0()` and `config_pucch_resset1()` checked `uecap != NULL` but dereferenced optional `phy_ParametersFRX_Diff` unconditionally. Trigger-time UE capability data can omit that subtree, causing SIGSEGV before a diagnostic assertion. | Fixed in host build: optional `phy_ParametersFRX_Diff` is now guarded before reading `pucch_F0_2WithoutFH`; Docker/runtime verification is still blocked by workspace credits. |

## Review Result

- [Status]: [PASS WITH RUNTIME BLOCKER]
- [Reason]: static review issues found in this pass were fixed and revalidated at host-build level, but Gate 5 cannot pass until new RFsim trigger0, bidirectional trigger, and eight-row matrix evidence are generated after the latest Docker image rebuild.
- [Runtime blocker]: the `fix_bwp_trigger0_pucch_id` RFsim run still hit a gNB crash in the BWP0 rebuild path; the follow-up optional capability guard builds on host but could not be pushed into Docker images because the workspace credits gate rejected Docker rebuild.
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
| `rtk bash redcap_interface/redcap_inspect_gnb_image.sh` | PASS before the optional capability guard; image rebuild is required again after the latest host build. |
| `BWP_TRIGGER_SEQUENCE=0 ... run_bwp_validation.sh --run` | FAIL before optional capability guard: `trigger_failures=0`, `runtime_failures=1`, crash marker in `test_log/redcap_bwp_sdt_validation/20260629_234523_bwp_trigger0_pucch_id_bwp/container_logs/full/gnb.log`. |
| `rtk bash redcap_interface/redcap_rebuild_local_oai_images.sh` after optional capability guard | BLOCKED: workspace credits rejected the Docker rebuild escalation, so no post-guard RFsim runtime claim is made. |

## Next Required Evidence

- Rebuild local Docker runtime images after the optional capability guard once workspace credits are available.
- Run a single `BWP_TRIGGER_SEQUENCE=0` RFsim case with `MMTC_SEGV_BACKTRACE=1`.
- Run a bidirectional `BWP_TRIGGER_SEQUENCE="0 1 0"` RFsim sanity case.
- Rerun the eight-row BWP matrix and update CSVs/plots/summary only from the new evidence.
