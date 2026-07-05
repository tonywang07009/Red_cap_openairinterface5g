# G4 RFsim Case B Marker Validation

## Scope

- Validate the first Workflow 3.0 SDK runtime slice in live RFsim Case B.
- Target parameter: `redcap_ul_prb_cap`.
- Required markers: contract validation, xApp control request/ACK, and gNB-side `RedCap UL PRB control`.

## Attempted Command Shape

- Started existing compose services with Case B policy and `oai-nr-ue1`.
- Captured gNB, UE, nearRT-RIC, and UE inspect evidence under `test_log/compiler_logs/`.
- Rebuilt local `oai-gnb:latest` and `oai-nr-ue:latest`.
- Force recreated `oai-gnb` and `oai-nr-ue2` with Case B policy.
- Sent live `redcap_ul_prb_cap=32` control to UE2 RNTI `7d05`.

## Result

- [Status]: PASS.
- [Scope]: first narrow Case B marker validation for `redcap_ul_prb_cap` only.
- [UE1 finding]: `rfsim5g-oai-nr-ue1_redcap` exits with code 139 before an active UE/RNTI is available.
- [UE2 finding]: `rfsim5g-oai-nr-ue2_redcap` reaches healthy state and produces RNTI `e349`.
- [Live control finding]: a live xApp attempt against the pre-rebuild gNB image timed out because the old image asserted on non-QoS RC action ID.
- [Post-rebuild finding]: fresh `oai-gnb:latest` and `oai-nr-ue:latest` containers reached healthy state, UE2 produced RNTI `7d05`, xApp received `CONTROL ACK`, and gNB emitted the `RedCap UL PRB control` marker.
- [Evidence persistence note]: final Docker marker output was observed in command output, but the follow-up attempt to tee short Docker evidence logs was rejected by the workspace credit gate.

## Evidence

| Item | Evidence Path | Marker |
|---|---|---|
| UE crash | `test_log/compiler_logs/workflow3_g4_2026-07-04_ue1.log` | `Main child exited with signal 'Segmentation fault'` |
| UE inspect | `test_log/compiler_logs/workflow3_g4_2026-07-04_ue1_inspect.json` | `"Status": "exited"`, `"ExitCode": 139`, `"OOMKilled": false` |
| gNB E2 setup | `test_log/compiler_logs/workflow3_g4_2026-07-04_gnb.log` | `E2 SETUP RESPONSE rx` |
| nearRT-RIC E2 setup | `test_log/compiler_logs/workflow3_g4_2026-07-04_nearric.log` | `Accepting RAN function ID 3 with def = ORAN-E2SM-RC` |
| UE2 healthy fallback | command output | `rfsim5g-oai-nr-ue2_redcap Up ... healthy`, `UE RNTI e349 CU-UE-ID 1 in-sync` |
| live xApp timeout on old image | `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-04_22-07-24.log` | `mode=live`, `raw_rnti=0xe349`, `cond_wait_sync_ui` timeout |
| image rebuild | `test_log/build_logs/rebuild_local_oai_images_2026-07-04_22-08-54_workflow3-g4.log` | `[Done] Local RedCap runtime images rebuilt from workspace` |
| flushed marker rebuild | `test_log/build_logs/rebuild_local_oai_images_2026-07-05_12-38-32_workflow3-g4-flush-marker.log` | `[Done] Local RedCap runtime images rebuilt from workspace` |
| fresh image/container state | command output | `oai-gnb:latest sha256:ea14936... running healthy`, `oai-nr-ue:latest sha256:4c9665... running healthy` |
| UE2 fresh RNTI | command output | `UE RNTI 7d05 CU-UE-ID 1 in-sync` |
| live xApp control | `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-07-05_12-44-32.log` | `[Contract][PASS]`, `CONTROL ACK rx`, `rnti=0x7d05`, `max_ul_prb=32` |
| gNB apply marker | command output | `2725:RedCap UL PRB control RNTI 7d05 requested 32 effective 32` |
| final verifier | command output | `Verified RedCap UL PRB control marker in live gNB logs` |

## Next Action

- Keep UE1 exit 139 as a separate runtime issue; G4 used UE2 as the validated live-control target.
- Start the next SDK runtime slice only after defining the target parameter, contract bounds, xApp request shape, and gNB/dApp marker.
