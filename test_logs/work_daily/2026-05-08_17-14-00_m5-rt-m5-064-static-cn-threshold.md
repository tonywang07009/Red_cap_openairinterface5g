# Work Daily Log

## Session Metadata
- Date: 2026-05-08 17:14
- Agent Session ID: N/A
- Task Slug: m5-rt-m5-064-static-cn-threshold
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md
- Milestone File: milestones/M5_mmtc_runtime_scaling.md
- Validation File: validation/test_matrix.md
- Task ID: M5-T2
- Batch: B

## Milestone & Sub-task Reference
- Milestone: M5 mMTC Runtime Scaling
- Sub-task: RT-M5-064 static CN upper-bound classification
- Status: COMPLETED

## What Was Done
- Ran [RT-M5-064] with 64 sampled RedCap UEs under Case B gNB config and static CN discovery mitigation.
- Preserved artifacts under `test_log/runtime_artifacts/m5_rt_m5_064_caseb_static_cn_2026-05-08_16-55-20/`.
- Classified the 64 UE run as [gNB runtime restart / SIGKILL threshold].
- Updated M5 project files, validation matrix, checklist, and report:
  - `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md`.
  - `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/milestones/M5_mmtc_runtime_scaling.md`.
  - `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/validation/test_matrix.md`.
  - `checklist/redcap_milestone_validation_checklist.md`.
  - `test_log/report/m5_rt_m5_064_caseb_static_cn_threshold_report_2026-05-08_17-14-00.md`.

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — Random Access procedure baseline.
- TS 38.321 Section 5.1.4 — RAR reception / RA response-window pressure [Needs Verification].
- TS 38.321 Section 5.1.5 — Contention Resolution [Needs Verification].
- TS 38.331 Section 6.3.2 — RedCap BWP / common configuration mapping [Needs Verification].
- TS 24.501 registration / PDU session exact clauses — NAS pass/fail markers [Needs Verification].
- TS 29.510 NRF / NF discovery exact clause — CN discovery behavior [Needs Verification].

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| RT-M5-064 static CN run | FAIL | 64 sampled UEs | `running=4 attach=59 pdu=59 tun=0 forward_ping_ok=0 gnb_restart=1 failures=65` |
| gNB runtime stability | FAIL | gNB Docker state + gNB log | gNB child exited with signal `Killed`; container restarted once |
| CN blocker scan | PASS | AMF / SMF / UPF logs | Auth-vector failure, Registration Reject, empty SMF candidate, NRF error markers all `0` |
| Msg2 DCI / CCE | PASS | gNB log | `64 x cce=0 agg=4` |
| RA retry pressure | PASS with observation | gNB + UE logs | Msg2 window fail `53`; UE RAR reception failed `53` |
| Msg2 / Msg4 VRB | PASS | gNB log | Msg2 and Msg4 `vrb_map fail=0` |
| Msg4 contention | FAIL due runtime boundary | gNB log | Msg4 ACK / CBRA success `63/64`; contention timer expired `0` |
| UE PUCCH common fallback blocker | PASS | UE logs | `pucch_ResourceCommon is NULL=0`, `fallback=0/1=0/0` |
| Host OOM confirmation | Needs Verification | dmesg / Docker inspect | Docker `OOMKilled=false`; `dmesg` unavailable due `Operation not permitted` |

## Known Issues / Blockers
- [RT-M5-064] is not a stable pass. It is classified as a gNB runtime restart / SIGKILL threshold.
- Static CN discovery mitigation still holds at 64 UE; the previous CN auth/SMF blocker did not recur.
- Host/kernel cause of SIGKILL remains [Needs Verification] because `dmesg` access is restricted.
- `UE1..UE60` exited after the gNB restart; `UE61..UE64` remained running but had no `oaitun_ue1`.

## Next Step
- Run [RT-M5-060] as a bracketing point between 56 UE PASS and 64 UE gNB restart threshold, or rerun 64 UE with host resource telemetry / gNB recovery enabled before making scheduler code changes.
