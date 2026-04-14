# Work Daily Log
## Session Metadata
- Date: 2026-04-13 20:33
- Agent Session ID: N/A
- Task Slug: redcap-m5-compare-vendor-dual-ue-design

## Milestone & Sub-task Reference
- Milestone: Milestone 5 runtime validation
- Sub-task: Compare vendor multi-UE RFsim design against current RedCap FlexRIC path
- Status: [COMPLETED]

## What Was Done
- Compared `ci-scripts/yaml_files/5g_rfsimulator_multiue/docker-compose.yaml` with `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml`.
- Compared the working dual-container vendor path `ci-scripts/yaml_files/5g_rfsimulator_flexric/docker-compose.yml` against the current RedCap FlexRIC compose.
- Confirmed the vendor repository already supports many independent UE containers in the non-RedCap FlexRIC path, so the remaining blocker is not explained by the mere presence of two separate UE containers.
- Identified the main RedCap-specific deltas on the failing `UE2` path:
  - `--uecap_file /tmp/redcap_force_yaml_fallback/uecap-redcap.xml`
  - mount of `../../conf_files/nrue_recap/nrue2.uicc.yaml`
  - RedCap capability fields including `half_duplex_fdd_type_a_redcap_r17: 1`
  - RedCap RF settings `-C 3630360000 --ssb 144`
  - removal of vendor `--telnetsrv` options used in the working non-RedCap FlexRIC path
- Cross-checked runtime logs and confirmed `UE2` reaches RedCap attach, receives PDU session setup, adds DRB 1, and configures `oaitun_ue1`, yet `UPF` still only reports packet detection for `10.0.0.2` during the ping window.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — RedCap capability advertisement is active on `UE2`, but capability success alone does not guarantee end-to-end user-plane forwarding.
- TS 38.331 Section 5.2.2.4.2 — RedCap SIB1/BWP application is present at runtime and is not the remaining blocker.
- TS 38.331 Section 5.6.1.3 — successful DRB/PDU-session establishment evidence exists, while the unresolved issue remains the forwarding path after setup.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Vendor `5g_rfsimulator_multiue` design review | Pass | Compose-level | Vendor multi-UE baseline uses a different single-process `--num-ues` model |
| Vendor `5g_rfsimulator_flexric` dual-container review | Pass | Compose-level | Confirms the repo already supports many separate UE containers with the same external CN network model |
| Runtime log comparison for `UE2` RedCap attach and DRB setup | Pass | Scenario-level | `UE2` log shows capability fallback, DRB 1 setup, and PDU session accept |
| UPF traffic observation for `10.0.0.3` in latest rerun | Fail | User-plane path | During ping, UPF still only reports packet detection for `10.0.0.2` |

## Known Issues / Blockers
- The blocker remains `[UE2 RedCap-specific user-plane forwarding]`, not generic `[dual UE container design]`.
- ⚠ Needs Verification: the most suspicious remaining deltas are the `UE2` RedCap config/capability path rather than Docker networking itself.

## Next Step
- Run a targeted A/B experiment by making `oai-nr-ue2` in the RedCap scenario mirror the vendor working non-RedCap UE2 service more closely, then add back RedCap-specific deltas one by one.
