# RedCap mMTC Milestone Attack Schedule and Validation Checklist

## Future Attack Schedule
| Order | Milestone | Focus | Entry Gate | Exit Gate |
|---:|---|---|---|---|
| 0 | M1/M2/M3/M4B unit baseline | Keep unit regression clean before runtime work | `ctest` unit set passes | 8/8 unit targets pass after every major patch group |
| 1 | M3 | Close CORESET#0 Case A/B runtime evidence and RA-RNTI BWP-domain behavior | Unit baseline pass | Case A and Case B RFsim evidence preserved; no RAR LDPC/BWP-domain mismatch |
| 2 | M4-B | Close DRX/eDRX/PSM validation boundary | Unit baseline pass and M3 stable | DRX flow-level evidence complete; eDRX/PSM compile/log-level or runtime boundary stated |
| 3 | M5 | Recover and extend mMTC runtime scaling | M3 stable and M4B boundary documented | 30/32 UE no-restart pass remains stable; 48/56/60/64 threshold classified |
| 4 | M6 | Package evidence, tutorial, and traceability | M3/M4B/M5 evidence ready | Project docs and learning reports match validation logs |
| 5 | M7 | Repository hygiene | User confirms cleanup scope | Unused files inventoried; removals only after explicit approval |

## Standing Regression Gate
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| M1 PHY RedCap PRB / antenna unit regression | TS 38.101-1 Section 5.3; TS 38.306 Section 4 [Needs Verification] |
| M2 RedCap SIB1 encode/decode and barring unit regression | TS 38.331 Section 6.3.1 / 6.3.2 [Needs Verification] |
| M3 RedCap BWP / CORESET / RA-RNTI BWP-domain unit regression | TS 38.331 Section 6.3.2; TS 38.213 Section 13; TS 38.321 Section 5.1 [Needs Verification] |
| M4B DRX/eDRX/PSM unit regression | TS 38.321 Section 5.7; TS 38.331 eDRX exact clause [Needs Verification]; TS 24.501 PSM exact clause [Needs Verification] |

## M1 PHY Constraints Checklist
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| RedCap FR1 UE BWP / frame-parameter PRB cap rejects over-20-MHz configuration | TS 38.101-1 Section 5.3; TS 38.306 Section 4 [Needs Verification] |
| RedCap UE accepts valid FR1 20-MHz-class PRB configuration | TS 38.101-1 Section 5.3 [Needs Verification] |
| RedCap UE rejects unsupported RX branch count | TS 38.306 Section 4 [Needs Verification] |
| RedCap UE rejects UL MIMO / multiple TX branches | TS 38.306 Section 4 [Needs Verification] |
| HD-FDD Tx/Rx switching guard remains deterministic | TS 38.306 Section 4; TS 38.101-1 HD-FDD exact clause [Needs Verification] |

## M2 RRC SIB1 RedCap Checklist
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| gNB SIB1 carries RedCap support fields without ASN.1 encode failure | TS 38.331 Section 6.3.1 / 6.3.2 [Needs Verification] |
| UE decodes RedCap SIB1 extension fields without ASN.1 decode failure | TS 38.331 Section 6.3.1 / 6.3.2 [Needs Verification] |
| UE applies 1Rx/2Rx RedCap barring decision from SIB1 | TS 38.331 Section 6.3.2; TS 38.306 Section 4 [Needs Verification] |
| UE cell-selection flow rejects barred RedCap profile | TS 38.331 Section 5.2.2.4.2 [Needs Verification] |

## M3 BWP / CORESET / Random Access Checklist
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| RedCap initial DL BWP and UL BWP config are parsed and bounded | TS 38.331 Section 6.3.2 [Needs Verification] |
| Case A uses Type0 CSS / CORESET#0 behavior for Msg2 | TS 38.213 Section 13 [Needs Verification] |
| Case B uses common CORESET inside RedCap BWP for Msg2 | TS 38.213 Section 13; TS 38.331 Section 6.3.2 [Needs Verification] |
| UE RA-RNTI monitoring BWP matches gNB Msg2 DCI/PDSCH BWP domain | TS 38.213 Section 13; TS 38.321 Section 5.1.4 [Needs Verification] |
| Msg1 preamble source correctly identifies RedCap RACH partition | TS 38.321 Section 5.1 [Needs Verification] |
| UE receives RAR and proceeds past Msg2 without LDPC/BWP mismatch | TS 38.321 Section 5.1.4 [Needs Verification] |
| Contention-based RA completes through Msg4 | TS 38.321 Section 5.1.5 [Needs Verification] |

## M3 Runtime Closure Evidence - 2026-05-07
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| [RT-M3-CASEA] RFsim Case A attach / RedCap BWP / user-plane PASS；evidence: `test_log/report/redcap_runtime_host_summary_case-a_disabled_2026-05-07_13-15-07.md`, `test_log/runtime_artifacts/m3_casea_2026-05-07_13-15-07/` | TS 38.213 Section 13; TS 38.321 Section 5.1.4 / 5.1.5; TS 38.331 Section 6.3.2 [Needs Verification] |
| [RT-M3-CASEB] RFsim Case B attach / `coreset_id=1` / BWP51-style edge allocation / user-plane PASS；evidence: `test_log/report/redcap_runtime_host_summary_case-b_disabled_2026-05-07_13-10-12.md`, `test_log/runtime_artifacts/m3_caseb_2026-05-07_13-10-12/` | TS 38.213 Section 13; TS 38.321 Section 5.1.4 / 5.1.5; TS 38.331 Section 6.3.2 [Needs Verification] |
| UE2 applies SIB1 RedCap initial DL/UL BWP in both Case A and Case B logs | TS 38.331 Section 6.3.2 [Needs Verification] |
| RAR/Msg4 path reaches ping and UL iperf without LDPC/BWP mismatch | TS 38.321 Section 5.1.4 / 5.1.5 [Needs Verification] |

## M4 SDT / RRC_INACTIVE Checklist
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| SDT FSM enters expected MsgA path | TS 38.331 SDT exact clause [Needs Verification] |
| SDT FSM falls back through Msg3 path when needed | TS 38.331 SDT exact clause; TS 38.321 Section 5.1 [Needs Verification] |
| Scheduler logs preserve SDT state transitions | TS 38.331 SDT exact clause [Needs Verification] |

## M4-B DRX / eDRX / PSM Checklist
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| Connected DRX config is accepted without `DRX not implemented` path | TS 38.321 Section 5.7 |
| UE active-time decision follows on-duration / inactivity / pending-SR conditions | TS 38.321 Section 5.7 |
| eDRX SIB1 low-power flags are decoded and applied to UE state | TS 38.331 eDRX exact clause [Needs Verification] |
| eDRX idle/inactive gating boundary is documented as compile-level, flow-level, or runtime-level | TS 38.331 eDRX exact clause [Needs Verification] |
| NAS PSM T3324 / T3512 timers are decoded and tracked | TS 24.501 PSM timer exact clause [Needs Verification] |
| PSM low-power-ready state is logged without claiming unsupported CN behavior | TS 24.501 PSM timer exact clause [Needs Verification] |

## M4-B Boundary Closure Evidence - 2026-05-07
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| [Connected DRX] config parser no longer uses `DRX not implemented`; focused CTest PASS in `test_log/compiler_logs/ctest_m4b_lowpower_boundary_2026-05-07_13-24-38_lsanoff.log` | TS 38.321 Section 5.7; TS 38.331 Section 6.3.2 [Needs Verification] |
| [Connected DRX] active-time gating is closed at [unit/flow-level]; current RFsim compose has no DRX-enabled runtime config, so [RT-M4B-001] is [NA] | TS 38.321 Section 5.7 |
| [eDRX] UE logs `SIB1 eDRX allowed: idle=0 inactive=0` in Case A/B runtime artifacts | TS 38.331 Section 6.3.2; TS 38.304 exact paging clause [Needs Verification] |
| [PSM] UE logs `NAS PSM timers: T3324=-1 sec T3512=1320 sec configured=1 low_power_ready=0` in Case A/B runtime artifacts | TS 24.501 Section 8.2.7.1.1; TS 24.501 Section 5.5.1 [Needs Verification] |
| [Boundary Claim] No CN-driven PSM sleep/quiesce or full eDRX paging behavior is claimed in this milestone closure | TS 24.501 Section 5.5.1; TS 38.304 eDRX paging exact clause [Needs Verification] |

## M5 mMTC Runtime Scaling Checklist
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| 30/32 UE staged attach reaches RRCSetup / Registration / PDU / tunnel / forward ping | TS 38.321 Section 5.1; TS 38.331 Section 6.3.2; TS 24.501 PDU session exact clause [Needs Verification] |
| Msg2 scheduling stays within RA response window | TS 38.321 Section 5.1.4 [Needs Verification] |
| Msg4 contention resolution completes without timer expiry storm | TS 38.321 Section 5.1.5 [Needs Verification] |
| PUCCH common fallback path applies when UE BWP1 lacks common PUCCH resource | TS 38.331 Section 6.3.2; TS 38.213 PUCCH exact clause [Needs Verification] |
| gNB remains no-restart during validation window | Implementation stability gate; no direct 3GPP clause |
| 48/56/60/64 staged capacity threshold is classified separately from recovery-path experiments | TS 38.321 Section 5.1.4 / 5.1.5 for RA counters [Needs Verification] |

## M5 Case B 30 UE Evidence - 2026-05-07
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| [RT-M5-CASEB-030] reaches `30/30` running / attach / PDU / tunnel / forward ping；evidence: `test_log/compiler_logs/mmtc_smoke_30ue_caseb_rerun_2026-05-07_13-29-43_escalated.log` | TS 38.321 Section 5.1; TS 38.331 Section 6.3.2; TS 24.501 PDU session exact clause [Needs Verification] |
| Msg2 Case B path remains active: `[gNB Msg2 gate]=153`, `[gNB Msg2 DCI]=30`, RedCap RA DCI CCE allocation `30 x cce=0 agg=4` | TS 38.321 Section 5.1.4; TS 38.213 Section 13 [Needs Verification] |
| Msg2 failure counters reduced to non-fatal retries: window fail `6`, vrb_map fail `0`, UE RAR reception failed `6`, LDPC decode fail `0` | TS 38.321 Section 5.1.4 [Needs Verification] |
| Msg4 contention path succeeds: Msg4 vrb_map fail `0`, contention timer expired `0`, Msg4 ACK / CBRA success `30` | TS 38.321 Section 5.1.5 [Needs Verification] |
| UE PUCCH common fallback blocker is absent in this run: `pucch_ResourceCommon is NULL=0`, env `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1` | TS 38.331 Section 6.3.2; TS 38.213 PUCCH exact clause [Needs Verification] |

## M5 Case B 32 UE Evidence - 2026-05-08
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| [RT-M5-032] reaches `32/32` running / attach / PDU / tunnel / forward ping；evidence: `test_log/compiler_logs/mmtc_smoke_32ue_caseb_2026-05-08_10-05-58_escalated.log`, `test_log/runtime_artifacts/m5_rt_m5_032_caseb_2026-05-08_10-05-58/` | TS 38.321 Section 5.1; TS 38.331 Section 6.3.2; TS 24.501 PDU session exact clause [Needs Verification] |
| Msg2 Case B path remains active: `[gNB Msg2 gate]=104`, `[gNB Msg2 DCI]=32`, RedCap RA DCI CCE allocation `32 x cce=0 agg=4` | TS 38.321 Section 5.1.4; TS 38.213 Section 13 [Needs Verification] |
| Msg2 failure counters remain non-fatal and lower than 30 UE baseline: window fail `1`, vrb_map fail `0`, UE RAR reception failed `1`, LDPC decode fail `0` | TS 38.321 Section 5.1.4 [Needs Verification] |
| Msg4 contention path succeeds: Msg4 vrb_map fail `0`, contention timer expired `0`, Msg4 ACK / CBRA success `32` | TS 38.321 Section 5.1.5 [Needs Verification] |
| UE PUCCH common fallback blocker is absent in this run: `pucch_ResourceCommon is NULL=0`, env `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1` | TS 38.331 Section 6.3.2; TS 38.213 PUCCH exact clause [Needs Verification] |

## M5 Case B 48 UE Evidence - 2026-05-08
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| [RT-M5-048] reaches `48/48` running / attach / PDU / tunnel / forward ping；evidence: `test_log/compiler_logs/mmtc_smoke_48ue_caseb_2026-05-08_10-22-06_escalated.log`, `test_log/runtime_artifacts/m5_rt_m5_048_caseb_2026-05-08_10-22-06/` | TS 38.321 Section 5.1; TS 38.331 Section 6.3.2; TS 24.501 PDU session exact clause [Needs Verification] |
| Msg2 Case B path remains active: `[gNB Msg2 gate]=393`, `[gNB Msg2 DCI]=48`, RedCap RA DCI CCE allocation `48 x cce=0 agg=4` | TS 38.321 Section 5.1.4; TS 38.213 Section 13 [Needs Verification] |
| Msg2 failure counters increase but remain non-fatal: window fail `23`, vrb_map fail `0`, UE RAR reception failed `23`, LDPC decode fail `0` | TS 38.321 Section 5.1.4 [Needs Verification] |
| Msg4 contention path succeeds: Msg4 vrb_map fail `0`, contention timer expired `0`, Msg4 ACK / CBRA success `48` | TS 38.321 Section 5.1.5 [Needs Verification] |
| UE PUCCH common fallback blocker is absent in this run: `pucch_ResourceCommon is NULL=0`, env `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1` | TS 38.331 Section 6.3.2; TS 38.213 PUCCH exact clause [Needs Verification] |

## M5 Case B 56 UE Evidence - 2026-05-08
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| [RT-M5-056] classifies the first threshold boundary: `56/56` running, `54/56` attach, `53/56` PDU / tunnel / forward ping；evidence: `test_log/compiler_logs/mmtc_smoke_56ue_caseb_2026-05-08_11-20-59_escalated.log`, `test_log/runtime_artifacts/m5_rt_m5_056_caseb_2026-05-08_11-20-59/` | TS 38.321 Section 5.1; TS 38.331 Section 6.3.2; TS 24.501 PDU session exact clause [Needs Verification] |
| Msg2 Case B path remains active: `[gNB Msg2 gate]=440`, `[gNB Msg2 DCI]=56`, RedCap RA DCI CCE allocation `56 x cce=0 agg=4` | TS 38.321 Section 5.1.4; TS 38.213 Section 13 [Needs Verification] |
| Msg2 retry pressure is visible but not the terminal failure: window fail `25`, vrb_map fail `0`, UE RAR reception failed `25`, LDPC decode fail `0` | TS 38.321 Section 5.1.4 [Needs Verification] |
| Msg4 contention path succeeds for all RA completions: Msg4 vrb_map fail `0`, contention timer expired `0`, Msg4 ACK / CBRA success `56` | TS 38.321 Section 5.1.5 [Needs Verification] |
| UE PUCCH common fallback blocker is absent in this run: `pucch_ResourceCommon is NULL=0`, env `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1` | TS 38.331 Section 6.3.2; TS 38.213 PUCCH exact clause [Needs Verification] |
| CN/NAS/PDU blocker is isolated: `UE54` / `UE55` receive Registration Reject after AMF `Request Authentication Vectors failure`; `UE56` registers but AMF reports `SMF Selection, no SMF candidate is available` | TS 24.501 registration and PDU session exact clauses [Needs Verification] |

## M5 Case B 56 UE Static CN Evidence - 2026-05-08
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| [RT-M5-056] rerun reaches `56/56` running / attach / PDU / tunnel / forward ping after static CN discovery mitigation；evidence: `test_log/compiler_logs/mmtc_smoke_56ue_caseb_static_cn_2026-05-08_12-03-21_escalated.log`, `test_log/runtime_artifacts/m5_rt_m5_056_caseb_static_cn_2026-05-08_12-03-22/` | TS 38.321 Section 5.1; TS 38.331 Section 6.3.2; TS 24.501 registration / PDU session exact clauses [Needs Verification] |
| CN pressure boundary is reduced by static discovery: `register_nf.general=no`, `enable_smf_selection=no`, static SMF UPF `host=oai-upf port=8805`; CN blocker markers all `0` | TS 29.510 NRF/NF discovery exact clause [Needs Verification]; TS 24.501 registration / PDU session exact clauses [Needs Verification] |
| Previously failed `UE54` / `UE55` / `UE56` now obtain `oaitun_ue1`: `10.0.0.55/24`, `10.0.0.56/24`, `10.0.0.57/24` | TS 24.501 PDU session exact clause [Needs Verification] |
| Msg2 Case B path remains active: `[gNB Msg2 gate]=770`, `[gNB Msg2 DCI]=56`, RedCap RA DCI CCE allocation `56 x cce=0 agg=4` | TS 38.321 Section 5.1.4; TS 38.213 Section 13 [Needs Verification] |
| Msg2 retry pressure is non-terminal but elevated: window fail `55`, UE RAR reception failed `55`, Msg2 `vrb_map fail=0`, LDPC decode fail `0` | TS 38.321 Section 5.1.4 [Needs Verification] |
| Msg4 contention path succeeds: Msg4 `vrb_map fail=0`, contention timer expired `0`, Msg4 ACK / CBRA success `56`, compact allocation `106 x rb=25 mcs=4 bwp=48` | TS 38.321 Section 5.1.5 [Needs Verification] |
| UE PUCCH common fallback blocker is absent in this run: `pucch_ResourceCommon is NULL=0`, `fallback=0/1=0/0`, env `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1` | TS 38.331 Section 6.3.2; TS 38.213 PUCCH exact clause [Needs Verification] |

## M6 Documentation / Evidence Packaging Checklist
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| Learning reports cite only clauses present in local spec notes or traceability matrix | All referenced 3GPP rows in validation/spec_traceability_matrix.md |
| Uncertain clause references remain marked `[Needs Verification]` | Accuracy protocol; no direct 3GPP clause |
| Runtime evidence links point to preserved logs under `test_log/` or `test_logs/` | Project validation rule; no direct 3GPP clause |

## M7 Repository Hygiene Checklist
| 流程 | 要驗證的對應規範的 clause |
|---|---|
| Inventory unused scripts/docs before deletion | Repository hygiene gate; no direct 3GPP clause |
| Verify active references with `rg` before removing files | Repository hygiene gate; no direct 3GPP clause |
| Remove files only after explicit user approval | Repository hygiene gate; no direct 3GPP clause |
| Run `git diff --check` after cleanup | Repository hygiene gate; no direct 3GPP clause |
