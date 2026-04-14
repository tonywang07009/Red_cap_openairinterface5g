# Work Daily Log
## Session Metadata
- Date: 2026-04-14 16:50
- Agent Session ID: N/A
- Task Slug: mmtc-ab-confirm-generic-userplane

## Milestone & Sub-task Reference
- Milestone: Compose Rebase & mMTC Scaling
- Sub-task: Validate whether generated UE smoke failure is [RedCap-specific] or [generic generated-UE user-plane]
- Status: [COMPLETED]

## What Was Done
- [Reviewed] host rerun results for:
  - [case A] generated [UE32] with default [RedCap-enabled] template path
  - [case B] generated [UE32] with `MMTC_REDCAP_ENABLE=0`
- [Confirmed] both cases still:
  - establish [Registration Accept]
  - establish [PDU Session Establishment Accept]
  - configure `oaitun_ue1`
  - fail `ping -I oaitun_ue1 12.1.1.1` with [100% packet loss]
- [Confirmed] the corrected [case B] now prints a [normal-template] generated config without a `nrue_recap:` section, even though OAI still logs the generic message `trying nrue_recap YAML fallback` when no XML capability file is present.
- [Reviewed] [gNB] and [UPF] logs for both cases:
  - [gNB] creates [DRB 1] and [GTP-U tunnel]
  - [UPF] receives [N4 session establish/modify] and installs [PDR/FAR] for `10.0.0.2`
- [Interpreted] the sustained [HARQ] / [MAC TX/RX] updates as [RAN/MAC continuity evidence], not [user-plane success evidence].

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — used to isolate whether [RedCap capability mode] is the differentiator in generated UE runtime behavior.
- TS 38.331 Section 5.6.1.3 — used to distinguish [successful RRC/NAS/PDU session setup] from [actual end-to-end data-plane connectivity].

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| [case A] UE32 RedCap smoke | Fail | Runtime smoke | `oaitun_ue1` present, ping still [100% loss] |
| [case B] UE32 normal-template smoke | Fail | Runtime smoke | `oaitun_ue1` present, ping still [100% loss] |
| [A/B differential hypothesis: RedCap-specific] | Fail | Analysis | Both cases fail, so hypothesis rejected |
| [RAN attach / DRB / tunnel creation] | Pass | Runtime evidence | [UE], [gNB], [UPF] control-path evidence all present |

## Known Issues / Blockers
- [Confirmed] Current blocker is [generic generated-UE user-plane connectivity], not [RedCap feature toggles].
- [Confirmed] Continuous [HARQ] counters only prove [RAN link + scheduling] is alive; they do not prove [ICMP/user-plane] traffic reaches [UPF/ext-dn].
- [Unresolved] Root cause is still between [generated UE data path emission] and [actual N3/UPF packet traversal].
- [Separate issue] [UE29] segmentation fault remains an independent blocker and should not be conflated with [UE32 ping failure].

## Next Step
- Compare [fixed working UE1 runtime path] versus [generated UE32 runtime path] at the packet path level:
  - [UE-side routes / rules / tuntap behavior]
  - [gNB N3/GTP-U runtime evidence]
  - [UPF counters/logs during live ping window]
- If needed, add targeted runtime instrumentation to [smoke helper] for [ext-dn reverse ping], [UPF live tail], and [generated UE route/rule dumps].
