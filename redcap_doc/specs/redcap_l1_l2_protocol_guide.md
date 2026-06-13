# RedCap L1/L2 Protocol Guide

## Purpose
- Explain the RedCap L1/L2 implementation path in this OAI checkout.
- Use this guide before editing PHY, MAC, BWP, RACH, configured grant, or SDT behavior.
- Use `function_reference/redcap_l1_l3_function_lookup.md` when you need exact function names.

## Reading Model
- [L1 PHY] defines radio and frame constraints that bound what the scheduler can request.
- [L2 MAC] maps RedCap capability and BWP limits into RACH, Msg2/Msg3, scheduling, and configured grant behavior.
- [RLC/PDCP] carries SDUs after MAC scheduling; RedCap-specific SN-length and continuity claims must stay `[Needs Verification]` until checked against local spec notes.
- [RRC] configures the RedCap context through UE capability, SIB1, `RRCRelease`, `RRCResume`, and `configuredGrantConfig`.

## L1 PHY: RedCap Constraints
| Topic | Local Code Area | Runtime Meaning | Spec Direction |
|---|---|---|---|
| FR1 PRB limit | `openair1/PHY/INIT/nr_parms.c` | Reject or cap invalid RedCap bandwidth/grid assumptions before runtime. | TS 38.306 / TS 38.104 `[Needs Verification]` |
| UE/gNB RedCap configured check | `openair1/PHY/INIT/nr_parms.c` | Decide whether RedCap frame-parameter validation applies. | TS 38.306 `[Needs Verification]` |
| 1Rx/2Rx and 256QAM behavior | Runtime config plus MAC evidence | Use gNB/UE logs and `nrMAC_stats.log`; do not accept Mbps alone as proof. | TS 38.306 / TS 38.214 `[Needs Verification]` |

Key implementation rule:
- L1 validation should fail early for impossible RedCap bandwidth or frame settings.
- L1 evidence should be paired with L2 scheduler evidence such as `MCS`, `Qm`, `NPRB`, BWP size, or PRACH markers.

## L2 MAC: BWP and RACH
| Topic | Local Code Area | Runtime Marker |
|---|---|---|
| RedCap initial DL/UL BWP | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c`, `openair2/LAYER2/NR_MAC_UE/nr_ue_redcap_bwp.c` | `bwp_start`, `bwp_size`, `locationAndBandwidth` |
| SIB1 RedCap BWP broadcast | `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` | `initialDownlinkBWP-RedCap-r17`, `initialUplinkBWP-RedCap-r17` |
| RedCap Msg1 preamble partition | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c`, `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c` | `[RedCap RA][UE Msg1]`, `[RedCap RA][gNB Msg2 gate]` |
| Msg2/Msg3 RedCap handling | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c`, `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c` | `RAR`, `RA-Msg3 transmitted`, `4-Step RA procedure succeeded` |

Protocol rule:
- RACH is the first L2 proof that RedCap capability changes the access path.
- A RedCap-vs-normal comparison must include gNB-side BWP/RACH markers, not only UE attach or ping.

## L2 Scheduler: CG-SDT and Fallback
| Gate | Behavior | Main Code Area | Required Markers |
|---|---|---|---|
| Gate 3 | UE parses/stores `configuredGrantConfig` and sends small data on CG PUSCH. | `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c`, `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c` | `configuredGrantConfig parsed`, `cg-SDT PUSCH tx`, `cg-SDT PUSCH rx candidate` |
| Gate 4 | UE skips CG-SDT and falls back to 4-step RA when threshold validation requires it. | `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c` | `RSRP threshold exceeded`, `4-step RA triggered`, `4-Step RA procedure succeeded` |

Current validation boundary:
- `MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1` enables the Gate 3 configured-grant validation path.
- `MMTC_RRC_INACTIVE_GATE4_FORCE_FALLBACK=1` is a deterministic RFsim validation hook for fallback.
- Formal measured `cg-SDT-RSRP-ChangeThreshold` and TA expiry behavior remain `[Needs Verification]`.

## RLC / PDCP Boundary
| Topic | Local Code Area | Why It Matters |
|---|---|---|
| PDCP SN length | `openair2/RRC/NR/rrc_gNB_radio_bearers.c` | RedCap may force 12-bit behavior when long SN is unsupported. |
| E1 DRB setup propagation | `openair2/RRC/NR/rrc_gNB_NGAP.c` | CU/DU split paths must carry the same RedCap bearer assumptions. |
| RRC_INACTIVE resume continuity | `openair2/RRC/NR_UE/`, `openair2/RRC/NR/` | Resume validation must not silently reset context or counters. |

Validation rule:
- Do not claim PDCP/RLC continuity from ping alone.
- Pair user-plane success with RRC/RLC/PDCP markers when the test objective is context preservation.

## Runtime Commands
```bash
# Gate 3: configured grant SDT path.
MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1 bash redcap_interface/mmtc.menu.bash gate3

# Gate 4: forced fallback to 4-step RA.
MMTC_RRC_INACTIVE_GATE4_FORCE_FALLBACK=1 bash redcap_interface/mmtc.menu.bash gate4

# Operator menu for RX mode, 256QAM, DRX/eDRX/PSM, and Docker bring-up.
bash redcap_interface/mmtc.menu.bash
```

## Log Marker Checklist
| Behavior | Marker |
|---|---|
| RedCap SIB1 / BWP setup | `initialDownlinkBWP-RedCap-r17`, `bwp_size`, `locationAndBandwidth` |
| RedCap RA preamble | `[RedCap RA][UE Msg1]` |
| gNB RedCap RA classification | `[RedCap RA][gNB Msg2 gate]` |
| RRC_INACTIVE entry | `RRC_INACTIVE entered` |
| CG-SDT config parse | `configuredGrantConfig parsed` |
| CG-SDT UE transmit | `cg-SDT PUSCH tx` |
| CG-SDT gNB receive candidate | `cg-SDT PUSCH rx candidate` |
| Gate 4 fallback | `RSRP threshold exceeded`, `4-step RA triggered` |
| 4-step RA success | `4-Step RA procedure succeeded` |

## Common Pitfalls
- Do not treat generated `build_test` headers as proof of runtime/default-build support.
- Do not accept throughput-only evidence for 256QAM or RedCap BWP behavior.
- Do not remove compatibility shims until manuals and historical references are migrated.
- Keep exact 3GPP clause numbers as `[Needs Verification]` unless the local spec source has been checked.
