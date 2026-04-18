# Work Daily Log
## Session Metadata
- Date: 2026-04-18 22:39
- Agent Session ID: N/A
- Task Slug: compose-overlay-align-redcap-pdu-localize

## Milestone & Sub-task Reference
- Milestone: Compose Rebase & mMTC Scaling
- Sub-task: Align overlay generator with per-UE direct-mounted YAML and localize the RedCap-common PDU/user-plane blockage
- Status: COMPLETED

## What Was Done
- Confirmed the active project milestone against `agent_doc/Project_management/Simluation_v2.md` and kept this work under the compose rebase / scaling track.
- Verified that `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml` already uses per-UE direct mounts to `/opt/oai-nr-ue/etc/nr-ue.yaml` for the fixed UE path.
- Found a drift in `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh`: it still emitted the old dual-template mount model (`nr-ue-redcap.yaml` + `nr-ue-normal.yaml`) and would overwrite the user's manual `docker-compose.mmtc.yml` path alignment on the next smoke run.
- Patched `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh` so generated overlay services now use:
  - `MMTC_TEMPLATE_CONFIG: /opt/oai-nr-ue/etc/nr-ue.yaml`
  - `../../conf_files/nrue_recap/nrue${idx}.uicc.yaml:/opt/oai-nr-ue/etc/nr-ue.yaml:ro`
- Regenerated `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml` and verified UE29..UE64 now follow the same direct-mount pattern.
- Reconstructed the PDU/user-plane evidence chain from the latest runtime logs:
  - UE1 baseline path works end-to-end.
  - UE2 and UE32 both complete RedCap attach, receive PDU Session Establishment Accept, configure `oaitun_ue1`, and obtain valid GTP/TEID setup in gNB/UPF.
  - UE2 and UE32 still fail both forward and reverse ping, with `oaitun_ue1` showing TX growth but RX remaining zero.
  - UPF `tun0` counters increase for UE1 traffic but do not receive corresponding UE2/UE32 uplink payloads.
- Narrowed the blockage from "compose path / subscriber DB / route issue" down to a RedCap-common data path after tunnel establishment and before payload reaches UPF.
- Identified the strongest code-level suspect for next verification:
  - `openair2/RRC/NR/rrc_gNB_radio_bearers.c` forces RedCap DRB PDCP SN to 12 bits when `pdcp_drb_long_sn_redcap_r17 = 0`.
  - This matches TS 38.306 optional long-SN signaling, but may expose an implementation gap in the current RedCap bearer path.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — Definition of RedCap UE; FR1 max bandwidth 20 MHz, max mandatory DRB count 8, PDCP/RLC AM 12-bit SN mandatory and 18-bit SN optional.
- TS 38.306 Section 4.2.21.3 — `longSN-RedCap-r17`; optional 18-bit PDCP sequence number support for (e)RedCap UE.
- TS 38.306 Section 4.2.21.4 — `am-WithLongSN-RedCap-r17`; optional 18-bit AM RLC sequence number support for (e)RedCap UE.
- TS 38.331 Section 6.3.1 — SIB1 / `RedCap-ConfigCommonSIB-r17`; includes `halfDuplexRedCapAllowed-r17` and RedCap barring-related cell access information.
- TS 38.331 Section 6.3.1 — `initialDownlinkBWP-RedCap-r17` and related SIB1-carried RedCap initial DL/UL BWP behavior. ⚠ Needs Verification: finer IE-level subclause naming inside the 6.3 field-definition chapter should be cited more precisely in the next pass.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Overlay generator syntax check | Pass | N/A | `bash -n ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh` |
| Overlay regeneration after patch | Pass | N/A | Regenerated `docker-compose.mmtc.yml`; UE29..UE64 now use per-UE `nrueXX.uicc.yaml -> /opt/oai-nr-ue/etc/nr-ue.yaml` |
| UE1 / UE2 / UE32 evidence correlation | Pass | N/A | Confirmed `[UE1 pass] / [UE2 fail] / [UE32 fail]`; failure is RedCap-common rather than generated-overlay-only |
| Post-ping UPF / UE counter review | Pass | N/A | UE2/UE32 `oaitun_ue1` TX grows with RX=0; UPF `tun0` does not receive matching UE2/UE32 uplink payloads |
| Root-cause behavior fix validation | Not Run | N/A | No docker rerun after this patch set; only path alignment and diagnostic localization were completed in this sub-task |

## Known Issues / Blockers
- Exact RedCap user-plane root cause is not yet fully proven.
- Current strongest suspect is the RedCap-specific bearer configuration path around PDCP/RLC SN handling when long-SN capability is not advertised.
- A secondary but lower-confidence branch remains the RedCap-specific initial BWP / data bearer interaction.
- Because the user-plane fix point is not yet confirmed, no behavior-changing code patch was applied to PHY/MAC/RRC in this sub-task.

## Next Step
- Re-run the aligned compose path with the corrected overlay generator and perform a focused UE1 / UE2 / UE32 comparison.
- Capture gNB and UPF user-plane evidence again after the path fix, then A/B verify whether the no-long-SN RedCap bearer path is the actual blocker.
- If the suspicion holds, prepare a minimal diagnostic or corrective patch around the RedCap bearer configuration path and validate it with the same three-way comparison.
