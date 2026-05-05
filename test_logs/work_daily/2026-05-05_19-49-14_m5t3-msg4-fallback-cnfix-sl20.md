# Work Daily Log
## Session Metadata
- Date: 2026-05-05 19:49
- Agent Session ID: N/A
- Task Slug: m5t3-msg4-fallback-cnfix-sl20
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: M5 mMTC Runtime Scaling
- Sub-task: M5-T3 Case B 30 UE RedCap RFsim runtime, Msg4 compact allocation fallback, CN UPF-NRF interface fix
- Status: IN-PROGRESS

## What Was Done
- Updated `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c`.
- Added `ra_pdsch_allocation_t` and `find_compact_ra_pdsch_allocation()` for RedCap RA Msg4 low-MCS compact allocation search.
- Changed RedCap Msg4 scheduling to try compact allocation up to MCS 4 first, then fall back to baseline OAI allocation if compact low-MCS allocation cannot fit the PDU.
- Rebuilt `nr-softmodem` successfully after the C change.
- Rebuilt local OAI runtime images with `ci-scripts/redcap_rebuild_local_oai_images.sh`.
- Fixed CN UPF runtime config outside this repo at `/home/tonywang/OAI/oai-cn5g/conf/config.yaml` so UPF SBI/N3/N4 use `eth0` and N6 uses `eth1`; UPF now registers with NRF successfully.
- Tested `ra_ResponseWindow: 6` / sl40 and confirmed it is invalid for this OAI gNB scheduler path because `nr_check_Msg2_MsgB_window()` requires the RA response window to stay within 10 ms.
- Updated `test_log/runtime_configs/gnb.redcap_mmtc_case-b_2026-05-02_12-35-01.yaml` to keep `ra_ResponseWindow: 5` / sl20.

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — Random Access procedure relevance for Msg1/Msg2/Msg3/Msg4 flow.
- TS 38.321 Section 5.1.4 — Random Access Response reception window; exact wording Needs Verification against local spec artifact.
- TS 38.321 Section 5.1.5 — Contention resolution behavior for Msg4.
- TS 38.214 Section 5.1.2.2 — PDSCH resource allocation relevance for Msg4 PRB/MCS/TBS sizing.
- TS 38.306 Section 4.2.1 — RedCap UE capability constraints; exact RedCap clause mapping Needs Verification.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| source build: `nr-softmodem` | PASS | gNB MAC RA scheduler | `test_log/build_logs/build_nr-softmodem_2026-05-05_19-03-49_m5t3-msg4-fallback_escalated.log` |
| unit test: `ctest -R test_nr_redcap_bwp` | PASS | RedCap BWP unit coverage | `test_log/compiler_logs/ctest_test_nr_redcap_bwp_*_m5t3-msg4-fallback.log` |
| container image rebuild | PASS | local `oai-gnb:latest` and runtime image refresh | `test_log/build_logs/rebuild_local_oai_images_2026-05-05_19-14-27_m5t3-msg4-fallback-cnfix_escalated.log` |
| RFsim 30 UE Case B after CN fix, sl20 baseline | PARTIAL | 30 sampled UE attach/PDU/tunnel/ping | `attach=21 pdu=21 tun=21 forward_ping_ok=21 failures=9`; CN UPF-NRF errors cleared |
| RFsim 30 UE Case B with sl40 | FAIL | RA response window experiment | `attach=3 pdu=3 tun=3 failures=27`; gNB logs show `RA-ResponseWindow need to be configured to a value lower than or equal to 10 ms` |
| RFsim 30 UE Case B with sl20 restored | PARTIAL | 30 sampled UE attach/PDU/tunnel/ping | `attach=26 pdu=26 tun=26 forward_ping_ok=26 failures=4`; no UPF selection failure; remaining failures are RA scheduler pressure |

## Known Issues / Blockers
- M5-T3 still does not reach 30/30 sampled UE pass.
- Latest sl20 run summary: `sample=30 running=30 attach=26 pdu=26 tun=26 forward_ping_ok=26 reverse_ping_ok=0 iperf_ul_ok=0 iperf_ul_run=0 gnb_restart=0 failures=4 mode=parallel`.
- Latest gNB marker counts include `Msg2 window fail=408`, `cannot find free CCE for Msg2=116`, `Received Nack in Msg4=1545`, `RA Procedure failed at Msg4=515`, and `RA Contention Resolution timer expired=515`.
- Latest CN markers show `Got successful response from NRF=30`, `UPF selection failed=0`, `Could not get response from NRF=0`; CN is no longer the active blocker.
- The active blocker is now gNB RA scheduling pressure under high RedCap RA load, mainly Msg2 CCE/window pressure and Msg4 HARQ NACK/contention resolution churn.

## Next Step
- Continue M5-T3 by reducing RA scheduler pressure without increasing `ra_ResponseWindow` beyond OAI's 10 ms guard: inspect Msg2 CCE allocation and Msg4 retransmission/resource scheduling around `nr_generate_Msg2_MsgB()` and `nr_generate_Msg4_MsgB()`.
