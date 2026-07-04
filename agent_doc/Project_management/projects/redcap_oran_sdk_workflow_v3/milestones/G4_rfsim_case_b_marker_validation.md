# G4 RFsim Case B Marker Validation

## Scope

- Validate the first Workflow 3.0 SDK runtime slice in live RFsim Case B.
- Target parameter: `redcap_ul_prb_cap`.
- Required markers: contract validation, xApp control request/ACK, and gNB-side `RedCap UL PRB control`.

## Attempted Command Shape

- Started existing compose services with Case B policy and `oai-nr-ue1`.
- Captured gNB, UE, nearRT-RIC, and UE inspect evidence under `test_log/compiler_logs/`.

## Result

- [Status]: BLOCKED.
- [Reason]: rebuilt OAI images are available, but Docker image inspection and RFsim restart are blocked by sandbox escalation rejection.
- [UE1 finding]: `rfsim5g-oai-nr-ue1_redcap` exits with code 139 before an active UE/RNTI is available.
- [UE2 finding]: `rfsim5g-oai-nr-ue2_redcap` reaches healthy state and produces RNTI `e349`.
- [Live control finding]: a live xApp attempt against the pre-rebuild gNB image timed out because the old image asserted on non-QoS RC action ID.
- [Safety decision]: do not claim PASS until a rebuilt gNB image emits the gNB-side `RedCap UL PRB control` marker.

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
| post-rebuild rerun block | command rejection | `workspace is out of credits` |

## Next Action

- Inspect the rebuilt `oai-gnb:latest` image once Docker escalation is available.
- Force recreate gNB and `oai-nr-ue2` from the rebuilt images.
- Re-run live `redcap_ul_prb_cap` control and require the gNB-side `RedCap UL PRB control` marker before closing task 4.5.
