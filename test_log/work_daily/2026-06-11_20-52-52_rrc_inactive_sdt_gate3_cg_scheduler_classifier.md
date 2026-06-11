# RRC_INACTIVE SDT Gate 3 CG Scheduler / RX Classifier Slice

## Conclusion
- Result: UE autonomous CG PUSCH scheduler slice and gNB CG-SDT RX classifier candidate implemented.
- Status: PARTIAL
- Scope: Gate 3 source-build validation plus RFsim pre-fix evidence. Latest inactive CG flag source build passes, but Docker image rebuild/RFsim rerun is blocked by workspace escalation credits.

## Required Project Fields
- Project Path: `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md`
- [Case]: A
- [Gate]: 3
- [source build PASS/FAIL/NA]: PASS
- [unit test PASS/FAIL/NA]: NA, no focused unit test exists for CG-SDT scheduler/classifier.
- [RFsim runtime PASS/FAIL/NA]: FAIL for full Gate 3 marker sequence; RFsim ping baseline passes but UE CG TX markers are absent.
- [exit 139]: absent in the RFsim smoke logs listed below.

## Improvement Target
- Original issue: Gate 3 stopped after `configuredGrantConfig parsed`; `cg-SDT PUSCH tx` and `cg-SDT PUSCH rx` were still absent.
- Improvement direction: Add a validation-oriented UE CG PUSCH scheduler and a gNB-side CG-SDT RX classifier marker without claiming full Gate 3 PASS.

## Changes
| Type | File / Function | Note |
|---|---|---|
| Code | `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c` / `nr_ue_try_schedule_cg_sdt_pusch()` | Schedules a Type1 configured-grant PUSCH on supported CG occasions when pending LC data exists. |
| Code | `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c` / `nr_ue_ul_scheduler()` | Logs `cg-SDT PUSCH tx` only after MAC SDU mux succeeds on a matching CG PUSCH. |
| Code | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c` / `nr_redcap_sdt_classify_cg_rx()` | Logs `cg-SDT PUSCH rx candidate` when an UL PDU matches the CG-SDT classifier conditions. |
| Code | `openair2/COMMON/rrc_messages_types.h` / `NR_MAC_RRC_ENTER_INACTIVE` | Adds a UE RRC-to-MAC indication for RRC inactive entry. |
| Code | `openair2/RRC/NR_UE/rrc_UE.c` / `nr_rrc_ue_notify_mac_inactive()` | Sends the inactive indication after `RRC_INACTIVE entered`. |
| Code | `openair2/RRC/NR_UE/L2_interface_ue.c` / `process_msg_rcc_to_mac()` | Sets `mac->redcap_rrc_state = NR_REDCAP_RRC_INACTIVE` for Gate 3 scheduling. |
| Code | `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c` / `nr_ue_cg_sdt_inactive_active()` | Allows inactive+cg-SDT config to refresh RLC buffer status and try autonomous CG PUSCH scheduling. |
| Doc | `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md` | Gate 3 updated to [in progress], not PASS. |
| Doc | `agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/milestones/T2_rrc_inactive_sdt_protocol.md` | Gate 3 current status and remaining RFsim boundary updated. |

## Validation
1. `rtk git diff --check -- openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`
2. `rtk bash -lc 'CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp cmake --build --preset default --target nr-uesoftmodem'`
3. `rtk bash -lc 'CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp cmake --build --preset default --target nr-softmodem'`
4. `rtk bash -lc 'bash redcap_interface/redcap_mmtc_smoke_validation.sh ... MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1'`

## Key Evidence
| Metric / Gate | Result | Evidence |
|---|---:|---|
| `nr-uesoftmodem` build | PASS | `test_log/build_logs/build_nr-uesoftmodem_2026-06-11_20-55-04_gate3-cg-scheduler-format.log` |
| `nr-softmodem` build | PASS | `test_log/build_logs/build_nr-softmodem_2026-06-11_20-52-29_gate3-cg-rx-classifier.log` |
| Local image rebuild before inactive flag | PASS | `test_log/build_logs/rebuild_local_oai_images_2026-06-11_20-58-59_gate3-cg-scheduler-classifier.log` |
| Image marker check before inactive flag | PASS | `test_log/build_logs/image_marker_check_2026-06-11_21-02-36_gate3-cg-scheduler-classifier.log` |
| Gate 2 ON RFsim smoke before inactive flag | PARTIAL | `test_log/compiler_logs/mmtc_gate3_cg_scheduler_classifier_smoke_2026-06-11_21-03-40.log` |
| Gate 2 OFF RFsim smoke before inactive flag | PARTIAL | `test_log/compiler_logs/mmtc_gate3_cg_scheduler_classifier_gate2off_smoke_2026-06-11_21-06-48.log` |
| `nr-uesoftmodem` build after inactive flag | PASS | `test_log/build_logs/build_nr-uesoftmodem_2026-06-11_21-15-30_gate3-inactive-cg-flag.log` |
| `nr-softmodem` build after inactive flag | PASS | `test_log/build_logs/build_nr-softmodem_2026-06-11_21-15-59_gate3-inactive-cg-flag.log` |
| Local `nr-uesoftmodem` marker check after inactive flag | PASS | binary contains `entered inactive for cg-SDT scheduling`, `CG occasion has no pending LCID data`, `cg-SDT autonomous CG PUSCH scheduled` |
| Local `nr-softmodem` marker check after inactive flag | PASS | binary contains `cg-SDT PUSCH rx candidate` |
| UE marker added | PASS | `cg-SDT autonomous CG PUSCH scheduled`, `cg-SDT PUSCH tx` |
| gNB marker added | PASS | `cg-SDT PUSCH rx candidate` |

## RFsim Pre-fix Evidence
| Run | Baseline | UE Parse | UE CG Schedule | UE CG TX | gNB RX Candidate | `classifier=cg-no-dynamic-grant` |
|---|---|---:|---:|---:|---:|---:|
| Gate 2 ON, `2026-06-11_21-03-40` | attach/pdu/tun/ping PASS | 3 | 0 | 0 | 178 | 2 |
| Gate 2 OFF, `2026-06-11_21-06-48` | attach/pdu/tun/ping PASS | 2 | 0 | 0 | 175 | 2 |

## Latest Inactive-Flag Slice
- [Modification Point] -> `NR_MAC_RRC_ENTER_INACTIVE` RRC-to-MAC message.
- [Reason] -> Gate 2 OFF smoke showed UE enters RRC_INACTIVE but no UE CG scheduler/TX marker appears; MAC needs explicit inactive visibility for Gate 3 autonomous CG checks.
- [Before vs. After Comparison] -> Before: Gate 3 scheduler path depended on normal connected scheduling visibility; After: UE MAC records `redcap_rrc_state=inactive`, refreshes RLC buffer status on inactive cg-SDT occasions, and permits matching CG PUSCH mux outside connected-only gating.
- [Discussion Point] -> This is source-build PASS only until Docker image rebuild and RFsim rerun prove `cg-SDT autonomous CG PUSCH scheduled` and `cg-SDT PUSCH tx`.

## Current Blocker
- Docker image rebuild for the inactive-flag binary could not run because escalation was rejected with `workspace is out of credits`.
- No workaround was attempted.
- Next validation must rebuild `oai-gnb:latest` and `oai-nr-ue:latest`, then rerun Gate 2 OFF smoke with `MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1`.

## Follow-up
- Rebuild local OAI images once Docker escalation is available.
- Run Gate 3 Gate2-OFF RFsim with `MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1`.
- Check markers: `RRC_INACTIVE Gate 3][UE MAC] entered inactive`, `CG occasion has no pending LCID data`, `cg-SDT autonomous CG PUSCH scheduled`, `cg-SDT PUSCH tx`, `cg-SDT PUSCH rx candidate`, and absence of `exit 139`.
- If `CG occasion has no pending LCID data` appears but UE ping reply still succeeds, next blocker is RLC/SDAP buffer visibility into inactive MAC scheduling.
