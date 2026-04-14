# Work Daily Log
## Session Metadata
- Date: 2026-04-13 20:16
- Agent Session ID: N/A
- Task Slug: redcap-m5-analyze-ue2-userplane-blocker

## Milestone & Sub-task Reference
- Milestone: Milestone 5 runtime validation
- Sub-task: Analyze latest rerun after UE create-path fix and localize remaining `[020005]` blocker
- Status: [COMPLETED]

## What Was Done
- Reviewed `test_log/compiler_logs/redcap_runtime_host_disabled_2026-04-13_20-04-29.log` and confirmed the scenario now passes `[000004]`, `[333331]`, `[302001]`, `[000005]`, `[333332]`, `[302002]`, `[302003]`, and `[302004]`.
- Confirmed the remaining scenario failure is still `[020005]` with `[UE2]` pinging `ext-dn` at `100%` packet loss while `[UE1]` remains healthy at `0%`.
- Compared `cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/27-100009-oai-nr-ue1.logs` and `...ue2.logs`; both UEs received `PDU Session Establishment Accept` and configured `oaitun_ue1` with IPv4 addresses `10.0.0.2` and `10.0.0.3`.
- Cross-checked `cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/27-100009-oai-gnb.logs`; the gNB marks the second UE as RedCap and shows healthy DL/UL BLER statistics for both UEs.
- Cross-checked `cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/28-100001-oai-upf.logs`; PFCP/PDR state exists for both UE IPs, but during the ping window the UPF only logs `PDR/PDI IP is 200000a` (`10.0.0.2`), not `300000a` (`10.0.0.3`).
- Concluded that the confirmed blocker is `[UE2 standalone user-plane uplink packets do not reach UPF/ext-dn]`; the failure is no longer in attach sequencing or RedCap capability validation.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — runtime validation of RedCap capability has already been satisfied by the successful RedCap UE attach evidence.
- TS 38.331 Section 5.2.2.4.2 — SIB1 RedCap initial BWP runtime evidence is present and no longer the blocking item in this scenario.
- TS 38.331 Section 5.6.1.3 — PDU session related UE context setup is accepted, but end-to-end user-plane reachability remains the unresolved runtime criterion.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `[000004]` / `[000005]` create-but-not-start rerun | Pass | Scenario-level | XML path fix worked; no more early skip cascade |
| `[302002]` RedCap UE detection | Pass | Scenario-level | gNB log contains `UE with RNTI .... is RedCap` |
| `[302003]` / `[302004]` SIB1 RedCap BWP evidence | Pass | Scenario-level | gNB log contains RedCap initial DL/UL BWP markers |
| `[020005]` UE2 ping to `ext-dn` | Fail | Scenario-level | `17-020005-ping_rfsim5g_redcap_ue2.log` shows `100% packet loss` |
| `[020005]` UE1 ping to `ext-dn` | Pass | Scenario-level | `17-020005-ping_rfsim5g_redcap_ue1.log` shows `0% packet loss` |
| UPF traffic observation during ping window | Fail | User-plane path | Only UE1 IP `10.0.0.2` appears in UPF packet detection during ping interval |

## Known Issues / Blockers
- The remaining blocker is narrowed to `[UE2 user-plane connectivity]`, specifically between `[UE2 oaitun_ue1]` and `[UPF/ext-dn]`.
- ⚠ Needs Verification: because `[UE2]` is pinged only about `5` seconds after its attach completes, a residual `[post-attach user-plane stabilization lag]` is still plausible.
- ⚠ Needs Verification: if a longer post-attach wait still fails, the next suspect is `[per-UE DRB/GTP-U forwarding for UE2]` rather than timing.

## Next Step
- Instrument or re-run the scenario with a longer `[UE2 post-attach stabilization]` window or a dedicated delayed second ping on `[UE2]`.
- If `[UE2]` still fails after a longer delay, inspect `[gNB/NG-U/UPF]` per-UE tunnel forwarding for `10.0.0.3` and compare it against the healthy `10.0.0.2` path.
