# Work Daily Log
## Session Metadata
- Date: 2026-04-10 17:10
- Agent Session ID: N/A
- Task Slug: redcap-runtime-attach-debug-capture

## Milestone & Sub-task Reference
- Milestone: Milestone 3 / Milestone 5 runtime validation
- Sub-task: RedCap runtime attach failure log capture
- Status: COMPLETED

## What Was Done
- Updated [`ci-scripts/redcap_runtime_host_validation.sh`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/redcap_runtime_host_validation.sh) to capture `docker ps -a` when the RedCap host validation exits with failure.
- Added automatic `docker logs` collection for [`rfsim5g-oai-gnb_redcap`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml), [`rfsim5g-oai-nr-ue1_redcap`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml), [`rfsim5g-oai-nr-ue2_redcap`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml), and [`nearRT-RIC_redcap`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml).
- Confirmed the existing RedCap runtime wiring still uses the corrected UE IDs in [`ci-scripts/ci_infra.yaml`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/ci_infra.yaml) and [`ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml).
- Compared [`nrue1.uicc.yaml`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/nrue_recap/nrue1.uicc.yaml) and [`nrue3.uicc.yaml`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/nrue_recap/nrue3.uicc.yaml); only IMSI/comment differences were found, so switching to `nrue3` would not address the current attach blocker.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.2.2.4.2 — SIB1 reception drives RedCap access conditions before successful cell access.
- TS 38.331 Section 5.6.1.3 — UECapabilityInformation handling remains part of the UE attach/runtime validation path.
- TS 38.306 Section 4.2.21.1 — RedCap UE runtime validation still targets FR1 RedCap capability constraints.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_runtime_host_validation.sh` | Pass | N/A | Shell syntax validated after adding debug log capture |
| `diff nrue1.uicc.yaml vs nrue3.uicc.yaml` | Pass | N/A | No behavioral delta except IMSI/comment formatting |

## Known Issues / Blockers
- Latest host log on 2026-04-10 16:59:33 to 17:00:19 still shows `oaitun_ue1` not created for `rfsim5g-oai-nr-ue1_redcap`.
- Earlier archived run on 2026-04-10 13:33:49 reported `NR-UE could NOT synch!` and `UE ended with a Segmentation Fault!`. Root cause still needs verification against the new debug logs.
- The 2026-04-10 16:58:44 rerun appears incomplete/interrupted before full scenario teardown and summary generation.

## Next Step
- Re-run `ci-scripts/redcap_runtime_case_matrix.sh` on the Docker host and inspect the generated `redcap_runtime_debug_*` logs to determine whether the next blocker is `[RF sync failure]`, `[UE crash]`, or `[gNB runtime mismatch]`.
