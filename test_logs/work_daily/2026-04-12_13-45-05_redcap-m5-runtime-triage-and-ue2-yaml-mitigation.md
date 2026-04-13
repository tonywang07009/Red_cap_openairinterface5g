# Work Daily Log
## Session Metadata
- Date: 2026-04-12 13:45
- Agent Session ID: N/A
- Task Slug: redcap-m5-runtime-triage-and-ue2-yaml-mitigation

## Milestone & Sub-task Reference
- Milestone: Milestone 5: Integration & UL Throughput Targets
- Sub-task: Runtime failure triage for RedCap UE2 attach blocker and host-side mitigation input cleanup
- Status: COMPLETED

## What Was Done
- Confirmed the host-side failure still happens before `[302005] / [302006]`; the true blocker is `[333332] Attach UE2 RedCap`.
- Confirmed [`ci-scripts/redcap_runtime_summary.py`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/redcap_runtime_summary.py) had a gNB artifact lookup bug: `find_service_log()` was matching `*-oai-gnb.logs.logs`.
- Patched [`ci-scripts/redcap_runtime_summary.py`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/redcap_runtime_summary.py) so service lookup normalizes optional `.logs` suffixes and correctly resolves `25-100009-oai-gnb.logs`.
- Re-ran the summary script on the existing host artifacts and confirmed the gNB cross-check now reads the archived gNB log instead of reporting it as missing.
- Compared the active RedCap UE YAML against the non-RedCap baseline and isolated the additional runtime-affecting input to the `[nrue_recap]` block plus the `[cells]` override block.
- Removed the `[cells]` override block from the active scenario asset [`ci-scripts/conf_files/nrue_recap/nrue2.uicc.yaml`](/home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts/conf_files/nrue_recap/nrue2.uicc.yaml), while preserving the `[nrue_recap]` capability declaration.
- Correlated host logs and archived UE logs:
  - [`test_log/compiler_logs/redcap_runtime_host_2026-04-12_13-14-02.log`](/home/tonywang/OAI/Red_cap_openairinterface5g/test_log/compiler_logs/redcap_runtime_host_2026-04-12_13-14-02.log)
  - [`cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/25-100009-oai-nr-ue2.logs`](/home/tonywang/OAI/Red_cap_openairinterface5g/cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/25-100009-oai-nr-ue2.logs)
  - [`cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/25-100009-oai-nr-ue1.logs`](/home/tonywang/OAI/Red_cap_openairinterface5g/cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/25-100009-oai-nr-ue1.logs)
- Established the current evidence chain:
  - `[UE1]` decodes `[PBCH]`, `[SIB1]`, and attaches normally.
  - `[UE2]` segfaults before `[PBCH decode]` / `[SIB1 decoded]`.
  - Therefore `Could not retrieve UE IP address(es)` is only a downstream symptom.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — The runtime target remains an FR1 RedCap UE profile subject to reduced-capability constraints.
- TS 38.331 Section 5.2.2.4.2 — SIB1 RedCap common information remains the expected admission/runtime evidence point once UE2 reaches SIB1 decoding.
- TS 38.331 Section 5.6.1.3 — UE capability signaling remains part of the RedCap attach path and must stay intact while triaging early attach failures.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `python3 -m py_compile ci-scripts/redcap_runtime_summary.py` | Pass | Updated summary tooling | Confirmed the Python patch is syntactically valid |
| `python3 ci-scripts/redcap_runtime_summary.py --html ci-scripts/test_results.html --artifacts cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d --run-log test_log/compiler_logs/redcap_runtime_host_2026-04-12_13-14-02.log` | Pass | Existing host artifacts | Confirmed gNB log is now discovered correctly |
| `rg -n "^cells:" ci-scripts/conf_files/nrue_recap/nrue2.uicc.yaml` | Pass | Active UE2 runtime YAML | No remaining `cells` override block in the active RedCap UE2 asset |

## Known Issues / Blockers
- `[⚠ Needs Verification]` The UE2 attach fix is not yet runtime-verified; a fresh host-side Docker/FlexRIC rerun is still required.
- The currently archived failed run still does not contain `[UE with RNTI .... is RedCap]`, `[SIB1 RedCap initial DL BWP]`, or `[RedCap UL PRB control RNTI .... requested ... effective ...]` because UE2 never reached those phases.
- If the next host rerun still segfaults after removing the active `[cells]` override, the next suspect should be narrowed to the `[nrue_recap]` capability construction path rather than the CI attach/IP checks.

## Next Step
- Re-run the host validation with the updated active UE2 YAML:
  `cd /home/tonywang/OAI/Red_cap_openairinterface5g/ci-scripts && REDCAP_UL_PRB_CAP=32 ./redcap_runtime_host_validation.sh container_5g_flexric_rfsim_redcap.xml`
