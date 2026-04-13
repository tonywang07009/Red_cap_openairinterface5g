# Work Daily Log
## Session Metadata
- Date: 2026-04-12 12:56
- Agent Session ID: N/A
- Task Slug: redcap-m5-runtime-rc-control-host-path

## Milestone & Sub-task Reference
- Milestone: Milestone 5: Integration & UL Throughput Targets
- Sub-task: Host-side FlexRIC RC control injection path for RedCap UL PRB runtime evidence
- Status: COMPLETED

## What Was Done
- Added `ci-scripts/redcap_ul_prb_ctrl_xapp.c` as a standalone FlexRIC xApp helper that builds an RC control message for:
  - action id `100`
  - `UE RNTI` RAN parameter `101`
  - `Max UL PRB cap` RAN parameter `102`
- Added `ci-scripts/redcap_send_ul_prb_control.sh` to:
  - flatten FlexRIC SM `.so` files into a local runtime plugin directory
  - compile the helper against the local FlexRIC build
  - auto-resolve the RedCap UE RNTI from `rfsim5g-oai-gnb_redcap` logs
  - support `build-only` and `dry-run` validation paths
- Updated `ci-scripts/xml_files/container_5g_flexric_rfsim_redcap.xml` to insert:
  - `[302005]` apply E2/xApp RedCap UL PRB cap
  - `[302006]` verify gNB applied the cap
  between the baseline `[030001]` UL iperf case and the follow-up `[030002]` UL iperf case.
- Updated `ci-scripts/redcap_runtime_summary.py` so Milestone 5 summaries now track:
  - `[302005]`
  - `[302006]`
  - `RedCap UL PRB control RNTI .... requested ... effective ...`
- Updated `agent_doc/Project_management/Simluation_v2.md` to:
  - record the new host-side RC control helper path
  - add `[302005] / [302006]` to Milestone 5 acceptance/evidence notes
  - align stale `nearRT-RIC` management IP references from `192.168.70.155` to `192.168.70.180`
  - align the M6-C compose note with the current `nearRT-RIC_redcap` / `oai-flexric:custom-dev` asset state

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — RedCap reduced-bandwidth operation bounds the UL runtime cap the xApp is allowed to tighten.
- TS 38.331 Section 5.2.2.4.2 — RedCap common configuration in SIB1 remains the broadcast context while the xApp applies a stricter runtime UL PRB limit.
- TS 38.331 Section 5.6.1.3 — UE capability / attach semantics remain part of the runtime evidence chain for distinguishing baseline UE1 from RedCap UE2.
- O-RAN E2SM-RC control-action clause number for the local RedCap action id `100`: ⚠ Needs Verification.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_send_ul_prb_control.sh` | Pass | shell wrapper syntax | Confirms the host-side RC control wrapper parses cleanly |
| `python3 -m py_compile ci-scripts/redcap_runtime_summary.py` | Pass | runtime summary syntax | Confirms the new `[302005] / [302006]` parsing logic is valid |
| `REDCAP_CTRL_BUILD_ONLY=1 ci-scripts/redcap_send_ul_prb_control.sh` | Pass | helper compile path | Build log: `test_log/build_logs/redcap_ul_prb_ctrl_xapp_build_2026-04-12_12-56-21.log` |
| `REDCAP_CTRL_DRY_RUN=1 REDCAP_CTRL_RNTI=0x1234 REDCAP_CTRL_UE_ID=0x1234 REDCAP_UL_PRB_CAP=32 ci-scripts/redcap_send_ul_prb_control.sh` | Pass | helper request assembly | RC control log: `test_log/compiler_logs/redcap_rc_ctrl_xapp_2026-04-12_12-56-21.log` |
| `rg -n '302005|302006|RedCap UL PRB control RNTI|redcap_send_ul_prb_control' ...` | Pass | XML + summary + project-plan wiring | Confirms the new runtime evidence path is connected end-to-end in repo assets |
| `rg -n '192\\.168\\.70\\.155' agent_doc/Project_management/Simluation_v2.md` | Pass | project-plan cleanup | No stale `192.168.70.155` references remain in the primary plan file |

## Known Issues / Blockers
- Live Docker/FlexRIC execution is still blocked in the current sandbox, so `[302005] / [302006]` were wired and locally dry-run validated but not executed against a running nearRT-RIC here.
- The helper currently uses a minimal gNB UE ID in the RC control header and relies on the explicit `UE RNTI` inside the control message body for UE selection, matching the current OAI agent-side implementation.
- The follow-up capped throughput case still depends on real host runtime conditions; the repo now provides the injection path, but the actual UL bitrate under the chosen cap must be measured on a Docker-enabled host.

## Next Step
- On a Docker-enabled host, run `ci-scripts/redcap_runtime_host_validation.sh` or `run_locally.sh` for `container_5g_flexric_rfsim_redcap.xml`, confirm `[302005] / [302006]` pass, then archive the resulting `[030001]` baseline and `[030002]` capped UL throughput evidence.
