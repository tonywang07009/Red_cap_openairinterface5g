# Work Daily Log
## Session Metadata
- Date: 2026-05-06 10:10
- Agent Session ID: N/A
- Task Slug: m5t3-ra-priority-pairpack
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md
- Milestone File: milestones/M5_mmtc_runtime_scaling.md
- Validation File: validation/test_matrix.md, validation/runtime_checklist.md, validation/spec_traceability_matrix.md
- Task ID: M5-T3
- Batch: B

## Milestone & Sub-task Reference
- Milestone: M5 mMTC Runtime Scaling
- Sub-task: M5-T3 RA/Msg4 scheduler pressure reduction for 30 UE Case B RFsim
- Status: IN-PROGRESS

## What Was Done
- Updated `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c`.
- Added `find_bounded_ra_pdsch_allocation()` for RedCap RA Msg4 bounded PRB allocation.
- Added a RedCap Msg4 pair-pack allocation path that tries to keep Msg4 PDSCH within half of the DL BWP when possible.
- Preserved the existing low-MCS compact Msg4 allocation and baseline OAI fallback path.
- Changed `nr_schedule_RA()` to schedule all Msg2 attempts before Msg3 retransmission and Msg4/MsgB in each slot.
- Kept RA contention resolution timer handling as a once-per-slot pre-pass before the prioritized RA scheduling passes.

## 3GPP Spec Clauses Referenced
- TS 38.321 Section 5.1 — Random Access procedure, relevant to Msg1/Msg2/Msg3/Msg4 sequencing.
- TS 38.321 Section 5.1.4 — Random Access Response reception window; exact wording Needs Verification against local spec artifact.
- TS 38.321 Section 5.1.5 — Contention resolution; relevant to Msg4 ACK/NACK and contention timer behavior.
- TS 38.214 Section 5.1.2.2 — PDSCH resource allocation relevance for PRB/MCS/TBS selection; exact clause mapping Needs Verification.
- TS 38.306 Section 4 — RedCap UE capability and bandwidth constraints; exact subsection Needs Verification.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| source build: `nr-softmodem` | PASS | gNB MAC RA scheduler | `test_log/build_logs/build_nr-softmodem_2026-05-06_10-09-02_m5t3-ra-priority-pairpack.log` |
| unit test: `ctest -R test_nr_redcap_bwp` | PASS | RedCap BWP/RA helper regression path | `test_log/compiler_logs/ctest_test_nr_redcap_bwp_2026-05-06_10-09-11_m5t3-ra-priority-pairpack-lsanoff.log` |
| unit test first run without LSAN override | FAIL | Environment-only failure after 15/15 tests passed | `ctest_test_nr_redcap_bwp_2026-05-06_10-06-27_m5t3-msg4-pairpack.log`; LeakSanitizer under ptrace |
| container image rebuild | FAIL | Docker host access | `test_log/build_logs/rebuild_local_oai_images_2026-05-06_10-06-56_m5t3-msg4-pairpack.log`; Docker socket permission denied |
| RFsim UE/gNB/CN runtime | NOT RUN | RT-M5-CASEB-030 | Blocked because local OAI image could not be rebuilt in this sandbox |

## Known Issues / Blockers
- Runtime validation remains blocked by host Docker permission: `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock`.
- The code change is build- and unit-test-validated, but not yet RFsim-validated.
- The expected runtime effect is reduced Msg2 window misses and fewer Msg4 `rb_size=25` packing failures, but this still Needs Verification with RT-M5-CASEB-030.

## Next Step
- Rebuild local OAI runtime images from a Docker-enabled shell, then rerun `RT-M5-CASEB-030` with the existing Case B 30 UE scenario and compare Msg2 window, Msg2 CCE, Msg4 vrb_map, and contention timer counters.
