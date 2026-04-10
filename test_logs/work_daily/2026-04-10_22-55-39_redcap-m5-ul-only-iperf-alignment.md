# Work Daily Log
## Session Metadata
- Date: 2026-04-10 22:55
- Agent Session ID: N/A
- Task Slug: redcap-m5-ul-only-iperf-alignment

## Milestone & Sub-task Reference
- Milestone: Milestone 5
- Sub-task: Align the RedCap RF-sim runtime scenario with the UL-only throughput policy in `Simluation_v2.md`
- Status: COMPLETED

## What Was Done
- Updated [`ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml) test case `030001` so the RedCap throughput scenario no longer uses a DL reverse iperf run.
- Changed test case `030001` from:
  - description: `DL/60Mbps/UDP`
  - arguments: `-u -b 60M -t 30 -R`
- Changed test case `030001` to:
  - description: `UL/50Mbps/UDP`
  - arguments: `-u -b 50M -t 30`
- Kept the existing `030002` UL `20M` case intact, so the scenario now contains two UL-only iperf checks instead of one DL plus one UL check.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — the runtime throughput scenario remains constrained to the FR1 RedCap operating point.
- TS 38.331 Section 5.6.1.3 — runtime attach and capability evidence still frame the UE validation path before throughput testing.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| SymDex search against `Simluation_v2.md` for `Do NOT use -R` and `UL throughput` | Pass | Policy/source-of-truth confirmation | Confirmed the project plan explicitly requires UL-only iperf validation |
| XML readback of test case `030001` | Pass | Scenario content | Confirmed description is now `UL/50Mbps/UDP` and args are `-u -b 50M -t 30` |
| `rg '<iperf_args>.*-R|DL/60Mbps' ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml` | Pass | Regression check | Result: `XML_UL_ONLY_CHECK=PASS` |

## Known Issues / Blockers
- The sandbox still cannot execute the full Docker runtime scenario, so this task validates XML policy alignment only, not measured UL throughput.
- Existing host rerun is still required to verify whether the updated `50M` UL case reaches the expected sustained throughput target.

## Next Step
- Continue Milestone 5 by preparing the next host-side rerun with the now-aligned gNB override path, UE override path, and UL-only iperf profile.
