# Work Daily Log
## Session Metadata
- Date: 2026-05-05 19:00
- Agent Session ID: N/A
- Task Slug: m5t3-msg4-compact-blocked
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: M5 mMTC Runtime Scaling
- Sub-task: M5-T3 Batch-B 30 UE RFsim RA/Msg4 scheduler convergence
- Status: BLOCKED

## What Was Done
- Modified openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c.
- Added ra_pdsch_allocation_t and find_compact_ra_pdsch_allocation() for RedCap RA PDSCH allocation search.
- Applied compact allocation only on RedCap Msg4/MsgB path after reverting the earlier Msg2 compact attempt.
- Set RedCap Msg4 compact preferred MCS cap to 4 and raised compact allocation log to LOG_I for RFsim observability.
- Rebuilt nr-softmodem successfully after the C change.
- Rebuilt local runtime images: ran-build:latest, oai-gnb:latest, and oai-nr-ue:latest.
- Ran M5-T3 30 UE Case-B RFsim validation; result blocked by CN UPF/NRF registration failure and residual Msg4 scheduling failures.

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — Random Access procedure, relevant for Msg2/Msg4 RA flow and contention resolution.
- TS 38.321 Section 5.1.4 — Random Access Response reception behavior, relevant for Msg2 response window timing. Needs Verification for exact subclause mapping in local notes.
- TS 38.321 Section 5.1.5 — Contention resolution behavior, relevant for Msg4 ACK/NACK and RA failure. Needs Verification for exact subclause mapping in local notes.
- TS 38.214 Section 5.1.2.2 — PDSCH frequency-domain resource allocation, relevant for Msg4 RB sizing and VRB map fitting. Needs Verification for exact RedCap-specific interpretation.
- TS 38.306 Section 4.2.1 — UE radio access capability framework, relevant for RedCap capability constraints. Needs Verification for exact RedCap bandwidth capability mapping.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| git diff --check | PASS | Formatting / whitespace | Passed for openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c |
| nr-softmodem build | PASS | gNB source build | Sandbox build failed due ccache /run/user write restriction; escalated rebuild passed and linked nr-softmodem |
| test_nr_redcap_bwp | PASS | Closest RedCap BWP unit test | Ran under build_test with LSAN_OPTIONS=detect_leaks=0; 1/1 passed |
| local image rebuild | PASS | Runtime container images | ran-build, oai-gnb, oai-nr-ue rebuilt from workspace |
| RT-M5-CASEB-030 30 UE RFsim | FAIL / BLOCKED | Runtime integration | Summary: sample=30 running=30 attach=27 pdu=0 tun=0 forward_ping_ok=0 gnb_restart=0 failures=30 |
| CN PDU session diagnosis | FAIL | AMF/SMF/UPF logs | UE markers show PDU Session Establishment reject; SMF shows UPF selection failed; UPF repeatedly could not get response from NRF |
| gNB RA diagnosis | FAIL | gNB RA log markers | RRCSetupComplete=29, Msg4 compact alloc=7904, Msg4 vrb_map fail=105, Msg2 window fail=466, Msg4 RA failed=442 |

## Known Issues / Blockers
- CN blocker: UPF failed NRF registration during the RFsim run, causing SMF UPF selection failed and 5GSM reject cause 0x21 for all PDU session attempts.
- Scheduler blocker: RedCap Msg4 compact allocation still produces residual VRB map failures and Msg4 NACK/retry storms under 30 UE load.
- The current Msg4 compact helper can still fall back to high MCS allocations in some TDA conditions; next patch should avoid high-MCS fallback for RedCap Msg4 and fall back to the baseline robust allocation when low-MCS compact fit is unavailable.
- Runtime result cannot be used as a clean M5-T3 pass/fail for user-plane throughput until the UPF-NRF registration issue is resolved.

## Next Step
- Fix or stabilize CN UPF-to-NRF registration in the RFsim validation path, then rerun RT-M5-CASEB-030.
- Patch Msg4 compact allocation fallback policy: prefer low-MCS compact fit; if unavailable, use baseline robust allocation instead of high-MCS compact allocation.
