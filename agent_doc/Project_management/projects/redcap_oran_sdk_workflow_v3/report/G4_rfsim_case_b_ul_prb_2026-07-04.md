# RedCap Workflow 3.0 Gate Report

## [Gate Scope]

- [Gate]: G4 RFsim Case B marker validation.
- [Goal]: validate live `redcap_ul_prb_cap` control through Case B policy, xApp sender, and gNB RC apply marker.
- [Non-goal]: debug the UE segmentation fault root cause in this Gate report.

## [3GPP / O-RAN Mapping]

| Behavior | Spec / Clause | Status | Local evidence |
|---|---|---|---|
| E2SM-RC control path | O-RAN WG3 E2SM-RC `[Needs Verification]` | [Needs Verification] | nearRT-RIC accepts RAN function ID 3 |
| RedCap scheduler cap | Local OAI scheduler rule | [Verified local code path] | `redcap_ul_prb_cap` contract and xApp dry-run evidence |

## [Modification Points]

| Modification Point | Reason | Before | After | Discussion Point |
|---|---|---|---|---|
| `fc_send_ul_prb_control.sh` | Validate contract before xApp control | xApp helper accepted env cap directly | wrapper validates Case B policy and `redcap_ul_prb_cap` bounds | Keep full YAML parser out; use standard-library targeted check |
| `redcap_control_contract.yaml` | Make seed parameter contract-backed | UL PRB cap helper existed outside contract | `redcap_ul_prb_cap` has owner/unit/default/range/rollback/marker | RFsim marker is now observed for this parameter |
| `ran_func_rc.c` | Make the gNB marker visible in Docker logs | marker used `printf` without immediate flush | `fflush(stdout)` after the RedCap marker | Minimal visibility fix; no control semantics changed |
| `fc_verify_ul_prb_control.sh` | Prevent ACK-only overclaiming | xApp ACK fallback returned PASS | verifier now requires live gNB marker | xApp ACK remains evidence, not G4 PASS |

## [Validation Evidence]

| Test Item | Pass-Fail Status | Evidence Path | Key Log Marker | Coverage / Limitation |
|---|---|---|---|---|
| OpenSpec strict validation | PASS | command output | `Change 'redcap-oran-sdk-workflow-v3' is valid` | planning artifacts only |
| Workflow static checker | PASS | command output | `[PASS] RedCap Workflow 3.0 static checks` | static contract/report checks only |
| xApp build/dry-run | PASS | `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-04_21-57-46.log` | `[Contract][PASS]`, `mode=dry-run` | no live E2 control |
| nearRT-RIC/gNB E2 setup | PARTIAL | `test_log/compiler_logs/workflow3_g4_2026-07-04_nearric.log`, `test_log/compiler_logs/workflow3_g4_2026-07-04_gnb.log` | `E2 SETUP RESPONSE rx` | proves E2 setup, not control apply |
| UE readiness for live control | FAIL | `test_log/compiler_logs/workflow3_g4_2026-07-04_ue1.log`, `test_log/compiler_logs/workflow3_g4_2026-07-04_ue1_inspect.json` | `Segmentation fault`, `ExitCode: 139` | no active UE/RNTI; live control not sent |
| UE2 fallback readiness | PASS | command output | `rfsim5g-oai-nr-ue2_redcap Up ... healthy`, `UE RNTI e349 CU-UE-ID 1 in-sync` | UE2 avoids the UE1 `cells:` crash path |
| live xApp attempt against old gNB image | FAIL | `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-04_22-07-24.log` | `mode=live`, `raw_rnti=0xe349`, `cond_wait_sync_ui` timeout | gNB image asserted before returning RC outcome |
| old gNB image RC action gate | FAIL | operator log scan output | `ctrl_act_id == 2`, `Currently only QoS flow mapping configuration supported` | source has RedCap branch, running image was stale |
| local image rebuild | PASS | `test_log/build_logs/rebuild_local_oai_images_2026-07-04_22-08-54_workflow3-g4.log` | `[Done] Local RedCap runtime images rebuilt from workspace` | rebuilt image not yet restarted |
| flushed marker image rebuild | PASS | `test_log/build_logs/rebuild_local_oai_images_2026-07-05_12-38-32_workflow3-g4-flush-marker.log` | `[Done] Local RedCap runtime images rebuilt from workspace` | rebuild includes marker flush fix |
| fresh gNB/UE2 containers | PASS | command output | `oai-gnb:latest sha256:ea14936... running healthy`, `oai-nr-ue:latest sha256:4c9665... running healthy` | exact image IDs captured from `docker inspect` |
| UE2 fresh readiness | PASS | command output | `UE RNTI 7d05 CU-UE-ID 1 in-sync` | UE2 used because UE1 still exits 139 |
| live xApp control after rebuild | PASS | `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-05_12-44-32.log` | `[Contract][PASS]`, `CONTROL ACK rx`, `rnti=0x7d05`, `max_ul_prb=32` | proves contract and E2 control ACK |
| gNB-side apply marker | PASS | command output | `2725:RedCap UL PRB control RNTI 7d05 requested 32 effective 32` | required G4 runtime marker |
| final marker verifier | PASS | command output | `Verified RedCap UL PRB control marker in live gNB logs` | verifier no longer accepts ACK-only fallback |
| short Docker evidence log persistence | BLOCKED | command rejection | `workspace is out of credits` | validation already passed; only follow-up tee capture was blocked |

## [Overclaim Guard]

- attach/session/tunnel/ping alone cannot claim RedCap/O-RAN protocol PASS.
- This Gate claims PASS only for the first narrow Case B `redcap_ul_prb_cap` slice.
- The PASS requires all three local markers: `[Contract][PASS]`, xApp `CONTROL ACK rx`, and gNB-side `RedCap UL PRB control RNTI 7d05 requested 32 effective 32`.
- UE1 exit 139 remains unresolved and is outside this Gate report.

## [Next Action]

- [Decision]: PASS.
- [Next pull item]: select the next SDK runtime parameter or dApp apply boundary; do not generalize this PASS beyond `redcap_ul_prb_cap`.
