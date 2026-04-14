# Work Daily Log
## Session Metadata
- Date: 2026-04-14 13:58
- Agent Session ID: N/A
- Task Slug: redcap-m5-mmtc-runtime-split-diagnosis

## Milestone & Sub-task Reference
- Milestone: Compose Rebase & mMTC Scaling
- Sub-task: Split generated-UE runtime failures into `[UE crash]` and `[user-plane]` branches
- Status: COMPLETED

## What Was Done
- [Modification Point] `[runtime diagnosis]` → [Reason] the previous blocker `[mysql / AUSF auth]` had already been fixed, so the next step was to identify the new runtime frontier → [Before vs. After Comparison] `[all sampled UEs failed]` → `[UE29 exit 139]` + `[UE32/UE64 registered and got TUN, but ping still 100% loss]` → [Discussion Point] this removes `[CN provisioning]` from the critical path.
- [Modification Point] `[latest smoke logs]` → [Reason] determine whether `[UE32/UE64]` were still failing in `[auth]` or had moved into `[data plane]` → [Before vs. After Comparison] unclear → confirmed `[Registration Accept]`, `[PDU Session Establishment Accept]`, `oaitun_ue1` for UE32/UE64 → [Discussion Point] `[AMF/UDM/AUSF]` path is now good for generated UEs.
- [Modification Point] `[live runtime probes]` → [Reason] differentiate `[readiness lag]` from `[persistent user-plane bug]` → [Before vs. After Comparison] initial smoke ping failed after setup → later live re-ping from UE32 and UE64 still failed with `[100% packet loss]` → [Discussion Point] this is no longer a simple `[wait longer]` issue.
- [Modification Point] `[helper diagnostics]` → [Reason] future reruns need `[UE state / route / UPF]` evidence without manual commands → [Before vs. After Comparison] helper only kept `[mysql/amf/udm/ausf/smf/gnb]` → [After] helper now also stores `[ue*_state.log]`, `[ue*_route.log]`, and `[upf.log]` → [Discussion Point] next rerun can directly show whether a failure is `[container crash]`, `[routing]`, or `[N3/UPF]`.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.6.1.3 — `[Registration Accept]`, `[Registration Complete]`, and `[PDU Session Establishment Accept]` are prerequisites before evaluating user-plane reachability.
- TS 38.306 Section 4.2.21.1 — RedCap capability signaling is present in runtime, but the remaining blocker has shifted to post-attach data-plane behavior.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `mmtc_smoke_2026-04-14_13-33-23_mysql_subscribers.log` | Pass | Generated CN DB overlay | IMSI 29/32/64 exist in `AuthenticationSubscription` and `SessionManagementSubscriptionData` |
| `mmtc_smoke_2026-04-14_13-33-23_amf.log` | Pass | Registration state | UE32/UE64 reached `5GMM-REGISTERED` and triggered PDU Session Establishment |
| `mmtc_smoke_2026-04-14_13-33-23_ue32_markers.log` / `ue64_markers.log` | Pass | UE-side NAS/session setup | Both UEs received `Registration Accept`, `PDU Session Establishment Accept`, and configured `oaitun_ue1` |
| `docker inspect rfsim5g-oai-nr-ue29_redcap --format '{{json .State}}'` | Fail | UE29 runtime | Exit code `139`, not OOM-killed; separate crash branch |
| live re-ping from UE32/UE64 to `12.1.1.1` | Fail | Post-attach user-plane | Still `100% packet loss` after extra settle time |
| live reverse ping from `oai-ext-dn` to `10.0.0.2` / `10.0.0.3` | Fail | Downlink reply path | Also `100% packet loss`; supports persistent data-path issue |
| `bash -n ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Helper syntax | Diagnostic helper patch is syntactically valid |
| `git diff --check -- ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Formatting / whitespace | No diff-check issues |

## Known Issues / Blockers
- `[UE29]` crashes immediately after `[Applying CellGroupConfig from gNodeB]` with exit code `139`; this is independent from the current `[UE32/UE64 user-plane]` failure.
- `[UE32/UE64]` complete `[Registration Accept]` and `[PDU Session Establishment Accept]`, and gNB creates `[DRB 1 / GTP-U tunnel]`, but ext-dn ping still fails both directions.
- `[UE32/UE64 route table]` currently shows `default via 192.168.70.1 dev eth0`; adding a temporary `12.1.1.0/24 dev oaitun_ue1` route did not recover ping, so the remaining issue is not just a simple route missing case.

## Next Step
- Run targeted A/B checks:
- `[A]` single generated RedCap UE only: `MMTC_TOTAL_UES=64 MMTC_SAMPLE_UES="32" MMTC_RESET_CN=1 bash ci-scripts/redcap_mmtc_smoke_validation.sh`
- `[B]` single generated non-RedCap UE only: `MMTC_REDCAP_ENABLE=0 MMTC_TOTAL_UES=64 MMTC_SAMPLE_UES="32" MMTC_RESET_CN=1 bash ci-scripts/redcap_mmtc_smoke_validation.sh`
- Compare whether `[user-plane failure]` is `[generated-UE generic]` or `[RedCap-specific]`.
