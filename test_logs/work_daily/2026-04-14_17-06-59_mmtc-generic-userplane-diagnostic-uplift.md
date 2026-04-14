# Work Daily Log
## Session Metadata
- Date: 2026-04-14 17:06
- Agent Session ID: N/A
- Task Slug: mmtc-generic-userplane-diagnostic-uplift

## Milestone & Sub-task Reference
- Milestone: Compose Rebase & mMTC Scaling
- Sub-task: Strengthen generated-UE smoke diagnostics for [generic user-plane connectivity] and remove stale [ext-dn ping target] assumptions
- Status: [COMPLETED]

## What Was Done
- [Reviewed] `agent_doc/Project_management/Simluation_v2.md` [Milestone 5: Compose Rebase & mMTC Scaling] and aligned the debugging scope with [generated UE packet-path evidence], not [RedCap capability toggles].
- [Compared] the [fixed-UE base compose] and the [generated mMTC overlay] in:
  - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml`
  - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml`
  - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/ue_mmtc_entrypoint.sh`
- [Confirmed] from the latest smoke artifacts that [UE32] receives `PDU Session Establishment Accept` with `IPv4 10.0.0.2` and configures `oaitun_ue1` as `10.0.0.2/24`.
- [Confirmed] the old smoke helper still defaulted to `MMTC_EXT_DN_IP=12.1.1.1`, which is inconsistent with the current CN overlay path generated from `doc/tutorial_resources/oai-cn5g/conf/config.yaml` and `ci-scripts/generate_mmtc_cn_db_overlay.sh`.
- [Updated] `ci-scripts/redcap_mmtc_smoke_validation.sh` to:
  - auto-derive the ping target from the UE TUN subnet when `MMTC_EXT_DN_IP` is not explicitly set
  - keep `12.1.1.1` only as a [legacy fallback]
  - dump [UE route/rule/route-get/interface counters] before and after ping
  - dump [gNB / UPF / ext-dn] pre/post snapshots with [ip addr / route / rule / UDP socket / `/proc/net/dev`]
  - add [ext-dn reverse ping] toward the UE TUN IP
  - record target-selection metadata per sampled UE

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.6.1.3 — used to separate [successful NAS/PDU session establishment] from [verified end-to-end user-plane packet traversal].
- TS 38.306 Section 4.2.21.1 — reused as the prior A/B isolation basis showing the current blocker is [generic generated-UE user-plane], not a [RedCap capability bit] difference.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Syntax | Updated helper parses successfully |
| Static review of latest smoke logs (`UE32` / `gNB` / `UPF`) | Pass | Diagnostic evidence | Verified `oaitun_ue1=10.0.0.2/24` while old helper still pinged `12.1.1.1` |
| Host Docker rerun with new instrumentation | Fail | Runtime | [Not executed in sandbox] Docker runtime evidence still needs host execution |

## Known Issues / Blockers
- [Unverified on host] Whether the correct reachable peer for the current CN overlay is [10.0.0.1] or another N6-side endpoint still requires a Docker-enabled rerun.
- [Unverified on host] Whether [gNB eth0] / [UPF N3/N6 path] counters move during the new ping window still requires fresh runtime artifacts.
- [Separate issue] [UE29 exit 139] remains independent of this helper uplift.

## Next Step
- Run the updated helper on a Docker-enabled host with a direct [fixed vs generated] comparison, for example:
  - `MMTC_SAMPLE_UES="1 32" bash ci-scripts/redcap_mmtc_smoke_validation.sh`
- Inspect the new per-UE artifacts:
  - `*_ue1_target.log` vs `*_ue32_target.log`
  - `*_ue32_route_get.log`
  - `*_ue32_upf_pre.log` / `*_ue32_upf_post.log`
  - `*_ue32_extdn_reverse_ping.log`
