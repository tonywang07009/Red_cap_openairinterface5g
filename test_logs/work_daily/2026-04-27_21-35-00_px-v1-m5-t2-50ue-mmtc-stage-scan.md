# Work Daily Log
## Session Metadata
- Date: 2026-04-27 21:35
- Agent Session ID: N/A
- Task Slug: px-v1-m5-t2-50ue-mmtc-stage-scan
- Task ID: M5-T2
- Batch: B
- Project Path: agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md

## Milestone & Sub-task Reference
- Milestone: [M5: Compose + mMTC]
- Sub-task: [M5-T2] scalable mMTC staged validation for 50 UE
- Status: [COMPLETED]

## What Was Done
- Updated `ci-scripts/redcap_mmtc_stage_scan.sh` defaults for the 50 UE mMTC path.
- Added UL-only `iperf3` validation pass-through from stage scan to smoke validation.
- Updated `ci-scripts/redcap_mmtc_smoke_validation.sh` to run sampled UL `iperf3` checks against `oai-ext-dn`.
- Fixed `iperf3` server lifecycle by restarting the ext-dn server before each sampled UE test.
- Updated the RedCap compose path so UE1 defaults to `nrue_recap` and removed the XML `--uecap_file` path from UE2.
- Updated `generate_mmtc_overlay.sh` so base UE1..UE28 also receive RedCap mMTC runtime variables and entrypoint mounting.
- Regenerated `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml` for UE1..UE50.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — RedCap UE FR1 reduced capability context, including reduced bandwidth and low-complexity UE behavior.
- TS 38.306 Section 4.2.21.6 — RedCap UE physical layer capability context.
- TS 38.331 Section 5.2.2.4.2 — SIB1-based RedCap access barring behavior context.
- TS 38.321 Section 5.1 — Random Access procedure context for UE attach and initial access validation.
- O-RAN E2/FlexRIC validation path is non-3GPP and remains an integration-side dependency.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_mmtc_stage_scan.sh` | Pass | Shell syntax | No syntax error |
| `bash -n ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Shell syntax | No syntax error |
| `MMTC_STAGE_LIST=50 MMTC_TOTAL_UES_TARGET=50 MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 MMTC_UE_START_GAP=0 MMTC_GNB_WARMUP=10 MMTC_SLEEP_AFTER_UP=25 MMTC_IPERF_ENABLE=1 MMTC_IPERF_SAMPLE_UES=1,25,50 bash ci-scripts/redcap_mmtc_stage_scan.sh` | Pass | 50 UE attach, PDU, TUN, parallel ping, sampled UL iperf3 | Summary: `sample=50 running=50 attach=50 pdu=50 tun=50 forward_ping_ok=50 iperf_ul_ok=3 iperf_ul_run=3 gnb_restart=0 failures=0` |
| UE1 UL `iperf3` sampled flow | Pass | mMTC low-rate UL traffic | 1.00 Mbit/s sender, 976 Kbit/s receiver, 0/1727 lost |
| UE25 UL `iperf3` sampled flow | Pass | mMTC low-rate UL traffic | 1.00 Mbit/s sender, 971 Kbit/s receiver, 0/1727 lost |
| UE50 UL `iperf3` sampled flow | Pass | mMTC low-rate UL traffic | 1.00 Mbit/s sender, 959 Kbit/s receiver, 0/1726 lost |

## Known Issues / Blockers
- 30 Mbps UDP per sampled UE is not stable in the 50 UE loaded mMTC run; it is kept as an override for single-UE or peak-throughput experiments via `MMTC_IPERF_RATE=30M`.
- Current validated mMTC default is 1 Mbps UL UDP for sampled UE1/25/50.
- `cmake_targets/swig` and `openair2/E2AP/flexric` were already dirty submodules and were not modified by this task.

## Next Step
- If peak RedCap throughput is required separately, run a single-UE or low-load `MMTC_IPERF_RATE=30M` profile outside the 50 UE mMTC stability gate.
