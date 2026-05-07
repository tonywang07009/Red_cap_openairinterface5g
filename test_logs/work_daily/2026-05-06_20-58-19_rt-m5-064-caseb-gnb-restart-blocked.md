# Work Daily Log
## Session Metadata
- Date: 2026-05-06 20:58
- Agent Session ID: N/A
- Task Slug: rt-m5-064-caseb-gnb-restart-blocked
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: M5 RedCap mMTC RFsim validation
- Sub-task: RT-M5-064 Case B 64-UE smoke validation after PUCCH fallback fix
- Status: [BLOCKED]

## What Was Done
- Ran RT-M5-064 using Case B gNB runtime config and 64 sampled UE containers.
- Generated 64-UE CN DB and compose override with MMTC_USE_EXISTING_CN_DB=0.
- Confirmed direct smoke path exported MMTC_PUCCH_COMMON_FALLBACK_BWP0=1.
- Collected gNB restart evidence and RA/Msg4 counters from the generated runtime logs.
- Checked representative UE logs for PUCCH fallback and tunnel/PDU state after the gNB restart.

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1.4 — Random Access Response reception and response-window behavior. [Needs Verification]
- TS 38.321 Section 5.1.5 — Contention resolution behavior for contention-based random access. [Needs Verification]
- TS 38.331 Section 6.3.2 — RRCSetup and ServingCellConfigCommon / PUCCH common configuration context. [Needs Verification]

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Source build | N/A | Runtime-only validation | No new C/C++ source patch was made during RT-M5-064. |
| Unit test | N/A | Runtime-only validation | No closest unit test target was applicable. |
| Container image rebuild | N/A | Existing local images | Used previously rebuilt oai-gnb/oai-nr-ue images. |
| RT-M5-064 RFsim runtime | FAIL | 64 sampled UEs | sample=64 running=4 attach=56 pdu=56 tun=0 forward_ping_ok=0 gnb_restart=1 failures=65. |
| gNB restart guard | FAIL | gNB container and log | gNB child exited with signal Killed; restart_count=1 before validation phase. |
| RA/Msg4 counters | WARN | gNB log scan | Msg2 window fail=35, RA CCE fail=1, Msg4 vrb=0, contention timer=1, Msg4 procedure fail=0, compact alloc=115. |
| UE PUCCH fallback spot-check | PASS | UE32/56/62/63/64 logs | No checked PUCCH_NULL regression; fallback use observed on representative UEs. |
| Host kill evidence | BLOCKED | dmesg access | Non-sudo dmesg was denied; sudo dmesg escalation was not available in this run. |

## Known Issues / Blockers
- gNB main child was killed around the 59-60 UE attach phase, then the container restarted.
- The smoke script skipped UE auto-recovery because gNB restart was detected before validation.
- UE1-60 containers exited after the gNB restart; UE61-64 remained running but had no tunnel.
- Current evidence does not identify whether the kill came from host OOM, cgroup pressure, watchdog timeout, or another external process signal.

## Next Step
- Classify the gNB child-kill root cause with host/cgroup evidence, or rerun RT-M5-064 with MMTC_RECOVER_ON_PRECHECK_GNB_RESTART=2 only as a recovery-path experiment.
- For true no-restart capacity validation, run staged 48/56/60/64 UE tests to locate the gNB restart threshold before changing RA scheduling behavior.
