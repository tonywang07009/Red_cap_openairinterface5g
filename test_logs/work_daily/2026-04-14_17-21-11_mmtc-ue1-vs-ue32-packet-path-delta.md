# Work Daily Log
## Session Metadata
- Date: 2026-04-14 17:21
- Agent Session ID: N/A
- Task Slug: mmtc-ue1-vs-ue32-packet-path-delta

## Milestone & Sub-task Reference
- Milestone: Compose Rebase & mMTC Scaling
- Sub-task: Compare [fixed working UE1 path] versus [generated UE32 path] using the updated packet-path instrumentation
- Status: [COMPLETED]

## What Was Done
- [Reviewed] the latest host rerun artifacts under `test_log/compiler_logs/mmtc_smoke_2026-04-14_17-14-19_*`.
- [Confirmed] [UE1] now succeeds end-to-end with the corrected target:
  - `oaitun_ue1 = 10.0.0.2/24`
  - `ping 10.0.0.1` = [0% packet loss]
  - `ext-dn -> 10.0.0.2` reverse ping = [0% packet loss]
- [Confirmed] [UE32] still fails end-to-end:
  - `oaitun_ue1 = 10.0.0.3/24`
  - `ping 10.0.0.1` = [100% packet loss]
  - `ext-dn -> 10.0.0.3` reverse ping = [100% packet loss]
- [Compared] [UE1] and [UE32] route policy snapshots:
  - both resolve `10.0.0.1` through `oaitun_ue1`
  - both have the expected `ip rule` entries for their own UE IPv4
  - therefore the delta is [not] in [UE route / ip rule / target selection]
- [Compared] [UE / UPF / ext-dn] counters:
  - [UE32] `oaitun_ue1` TX increases during ping, proving the local kernel emits outbound packets into the UE data path
  - [UPF] `tun0` RX does [not] increase during the [UE32] ping window, so those uplink packets do not arrive at the UPF data-plane interface
  - [ext-dn] reverse ping toward `10.0.0.3` causes [UPF] `tun0` TX to increase, but [UE32] shows only `oaitun_ue1 RX dropped`, not successful RX bytes
- [Corrected] the earlier hypothesis from `2026-04-14_16-50-45_mmtc-ab-confirm-generic-userplane.md`:
  - that conclusion was based on the stale target `12.1.1.1`
  - after the [2026-04-14 17:14] rerun, only [UE1 normal] vs [generated UE32 RedCap] has been cleanly validated
  - [generic generated-UE failure] versus [RedCap-specific failure] is therefore [not yet re-proven] with the corrected target

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.6.1.3 — control-plane success (`PDU Session Establishment Accept`) is not sufficient to claim end-to-end user-plane success.
- TS 38.306 Section 4.2.21.1 — retained only as the prior RedCap isolation reference; the prior runtime conclusion now needs re-validation with the corrected target.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| [UE1] `10.0.0.2 -> 10.0.0.1` ping | Pass | Runtime packet path | [0% loss], reverse ping also passes |
| [UE32] `10.0.0.3 -> 10.0.0.1` ping | Fail | Runtime packet path | [100% loss] |
| [UE32] reverse ping `10.0.0.1/ext-dn -> 10.0.0.3` | Fail | Runtime packet path | [100% loss] |
| [UE1 vs UE32 route/rule comparison] | Pass | Config parity | Route/rule delta ruled out |
| [UE32 uplink arrival at UPF tun0] | Fail | Counter-based evidence | UE32 TUN TX increases, but UPF `tun0 RX` does not |
| [UE32 downlink delivery into kernel] | Fail | Counter-based evidence | `oaitun_ue1 RX dropped` increases without RX bytes |

## Known Issues / Blockers
- [Current confirmed blocker] is narrower than before: [generated UE32 user-plane path] fails even though [UE1] works in the same run and the same CN/gNB base.
- [Not yet proven] whether the failure is [generated-path generic] or [RedCap-specific], because the old [normal-template A/B] conclusion used the stale target `12.1.1.1`.
- [Likely fault region] is between [UE32 data-path handling] and [gNB↔UPF user-plane forwarding], not in [subscriber DB], [target IP selection], or [basic route/rule plumbing].

## Next Step
- Run one corrected three-way comparison in the same environment:
  - `MMTC_SAMPLE_UES="1 2 32" bash ci-scripts/redcap_mmtc_smoke_validation.sh`
- Interpret it as:
  - [UE1 pass, UE2 pass, UE32 fail] => [generated overlay path] is the primary suspect
  - [UE1 pass, UE2 fail, UE32 fail] => [RedCap user-plane path] is the primary suspect
- If [UE32] still fails after that, the next instrumentation should capture [GTP-U traffic per TEID] on [gNB] and [UPF] during the ping window.
