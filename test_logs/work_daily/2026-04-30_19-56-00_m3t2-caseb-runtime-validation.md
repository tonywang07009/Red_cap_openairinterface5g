# Work Daily Log
## Session Metadata
- Date: 2026-04-30 19:56
- Agent Session ID: N/A
- Task Slug: m3t2-caseb-runtime-validation
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: M3-T2 RedCap RA / CORESET#0 Case B runtime validation
- Sub-task: RFsim Case B runtime validation for Msg2 scheduler RedCap gate
- Status: BLOCKED

## What Was Done
- Rebuilt local runtime images from workspace:
  - oai-gnb:latest
  - oai-nr-ue:latest
- Generated Case B gNB runtime config:
  - test_log/runtime_configs/gnb.redcap_case-b_disabled_2026-04-30_19-43-24.yaml
- Ran RFsim Case B validation with:
  - REDCAP_EXPECTED_MODE=case-b
  - REDCAP_USE_LOCAL_OAI_IMAGES=1
  - REDCAP_E2_AGENT_MODE=disabled
- Collected and inspected runtime artifacts:
  - test_log/compiler_logs/redcap_runtime_host_case-b_disabled_2026-04-30_19-43-24.log
  - test_log/report/redcap_runtime_host_summary_case-b_disabled_2026-04-30_19-43-24.md
  - cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/27-100009-oai-gnb.logs
  - cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/27-100009-oai-nr-ue2.logs
- Runtime result:
  - UE1 attach passed.
  - UE2 RedCap attach failed because UE2 did not obtain an IP address.
  - Later scenario checks were skipped after test 333332 failed.
- Marker diagnosis:
  - gNB `[RedCap RA][gNB Msg1]`: not found.
  - gNB `[RedCap RA][gNB Msg2 gate]`: not found.
  - gNB `[RedCap RA][gNB Msg2 DCI]`: found, but DCI used `coreset_id 0` and `bwp_size 48`.
  - UE2 `[RedCap RA][UE DCI cfg]`: found with `coreset_id 1` and `bwp_size 51`.
  - UE2 RAR success marker: not found.
  - UE2 `RAR reception failed`: found repeatedly.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.2.2.4.2 — SIB1 / serving cell common configuration relevance for RedCap initial BWP.
- TS 38.321 Section 5.1 — Random Access procedure overview.
- TS 38.321 Section 5.1.4 — Random Access Response reception. [⚠ Needs Verification]

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Local runtime image rebuild | PASS | gNB/nrUE container images | `oai-gnb:latest` and `oai-nr-ue:latest` rebuilt from workspace |
| RFsim Case B runtime | FAIL | UE1/UE2 attach path | Test `333332` failed because UE2 did not get IP |
| gNB Msg1 RedCap marker | FAIL | gNB RA Msg1 marking | `[RedCap RA][gNB Msg1]` not found |
| gNB Msg2 RedCap gate marker | FAIL | gNB Msg2 scheduling path | `[RedCap RA][gNB Msg2 gate]` not found |
| gNB Msg2 DCI marker | PARTIAL | gNB Msg2 DCI generation | Marker found, but `coreset_id=0`, `bwp_size=48` instead of Case B RedCap path |
| UE2 RA-RNTI monitoring | PASS | UE2 RedCap RA monitor config | UE2 uses `coreset_id=1`, `bwp_size=51` |
| UE2 RAR reception | FAIL | UE2 RA response | `RAR reception failed` repeated; no RAR success marker found |

## Known Issues / Blockers
- gNB did not mark RedCap Msg1 at runtime, so `ra->is_redcap_msg1` stayed false or did not reach the Msg2 gate.
- Because the gNB did not enter the RedCap Msg2 gate, Msg2 DCI stayed on baseline CORESET/BWP.
- UE2 correctly monitored the RedCap RA path on CORESET 1 / BWP 51, causing a DCI/RAR mismatch against the gNB output.

## Next Step
- Debug why `nr_redcap_is_msg1_preamble()` / `nr_initiate_ra_proc()` does not emit `[RedCap RA][gNB Msg1]` for UE2 preambles 60-63 in Case B runtime.
