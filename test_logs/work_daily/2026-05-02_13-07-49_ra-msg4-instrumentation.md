# Work Daily Log
## Session Metadata
- Date: 2026-05-02 13:07
- Agent Session ID: N/A
- Task Slug: ra-msg4-instrumentation
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: M5 mMTC Runtime Scaling
- Milestone File: milestones/M5_mmtc_runtime_scaling.md
- Validation File: validation/test_matrix.md
- Task ID: M5-T3
- Batch: B
- Sub-task: gNB RA/Msg4 scheduler instrumentation after RT-M5-CASEB-030
- Status: [COMPLETED]

## What Was Done
- Modified `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c`.
- Added `count_vrb_occupied_prbs()` for diagnostic-only PRB pressure counting.
- Added `[RedCap RA][gNB Msg2 window fail]` logs with:
  - `frame.slot`, `RA-RNTI`, `TC-RNTI`, preamble index, RedCap marker, RA state, preamble `frame.slot`, response-window diff, DL/UL BWP.
- Added `[RedCap RA][gNB Msg2 vrb_map fail]` logs with:
  - BWP start/size, RB candidate, RB size, occupied PRBs, symbol mask, TDA, Msg3 allocation context.
- Added `[RedCap RA][gNB Msg4 vrb_map fail]` logs with:
  - BWP start/size, RB candidate, RB size, occupied PRBs, TDA, MCS, TBS, PDU length, HARQ context.
- Rebuilt `nr-softmodem`.
- Rebuilt local Docker images from the workspace.
- Reran `RT-M5-CASEB-030` with Case B config and external CN DB.
- Updated:
  - `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md`
  - `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/milestones/M5_mmtc_runtime_scaling.md`

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — Random Access procedure.
- TS 38.321 Section 5.1.4 — RAR reception. Exact subsection: [Needs Verification].
- TS 38.321 Section 5.1.5 — Contention Resolution. Exact subsection: [Needs Verification].
- TS 38.214 Section 5.1.2.2 — PDSCH frequency-domain resource allocation.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| source build | PASS | gNB-side source | `nr-softmodem` rebuilt successfully |
| unit test | N/A | Diagnostic log-only patch | No closest CTest target applies |
| container image rebuilt | PASS | local RFsim images | `oai-gnb:latest` and `oai-nr-ue:latest` rebuilt |
| RT-M5-CASEB-030 RFsim runtime | FAIL | 30 staged UEs | `27/30` attach/PDU/tunnel/ping |
| gNB instrumentation markers | PASS | gNB log | New Msg2 window, Msg2 `vrb_map`, Msg4 `vrb_map` markers present |
| UE Msg2 LDPC decode | PASS | UE logs | `0` LDPC decode failure matches |
| CN existing database | PASS | `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml` | Failed UE IMSIs exist in `oai_db.sql` |

## Known Issues / Blockers
- Failed UEs in the instrumented run: `UE25`, `UE29`, `UE30`.
- gNB restart count remained `0`.
- Msg2 failures show `occupied_prbs=48` in BWP51 while trying to allocate `rb_size=8`.
- Msg2 window failures are mostly `diff=21` with `window=20`.
- Msg4 failures show `rb_size=48` and `occupied_prbs=48`, so Msg4 PDSCH allocation is too wide for the loaded RedCap RA slot.
- UE logs still show RedCap DCI config at `coreset_id=1` / `BWP51`, with no LDPC decode failure.

## Next Step
- Implement a scheduler fix in a new atomic task:
  - review Msg4 PDSCH RB/MCS selection under RedCap mMTC load,
  - review Msg2 slot/RB selection before RA response-window expiry,
  - rebuild and rerun `RT-M5-CASEB-030`.
