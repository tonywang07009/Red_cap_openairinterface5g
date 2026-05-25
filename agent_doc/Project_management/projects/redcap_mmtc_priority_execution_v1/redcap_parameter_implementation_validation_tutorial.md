# RedCap 參數實作邏輯與規範總檢核導讀

## 文件定位
- [文件目的]：把 `project_plan.md`、各 milestone、實作函數、runtime 參數、3GPP clause、驗證證據串成一份可逐行閱讀的導讀。
- [主要讀者]：Caramel Bird，用來理解「每個參數為什麼存在」、「程式碼如何使用它」、「如何重跑模擬」、「如何判讀 pass/fail」。
- [專案路徑]：`agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md`。
- [目前結論]：
  - [M1/M2/M3/M4/M4-B/M5/M6/M7] 均已在目前 v1 scope 關閉。
  - [M5] 接受的穩定模擬容量是 [56 RedCap UE]。
  - [64 UE] 已做為 upper-bound 實驗，分類為 [gNB runtime restart / SIGKILL threshold]，不是目前必要 pass gate。
- [限制聲明]：
  - 目前 [O-RAN] 僅保留既有 [FlexRIC runtime check] 範圍。
  - 本文件不聲稱已完成新的 [xApp/rApp/dApp SDK]。
  - 任何 exact clause 未由本地 spec 完整確認者，維持 `[Needs Verification]`。

## 如何使用本文件
- [第一輪閱讀]：先看 [RedCap 參數總表]，確認每個參數的用途。
- [第二輪閱讀]：看 [實作邏輯導讀]，把參數對到函數與 log marker。
- [第三輪操作]：照 [56 UE Case B 模擬導讀] 重跑 accepted runtime。
- [第四輪複盤]：用 [總檢核表] 對照 clause、證據、狀態。
- [第五輪練習]：完成每個教學單元的 [Basic]、[Applied]、[Advanced] 題目。

## Milestone 總覽
| Milestone | 目的 | 目前狀態 | 主要證據 |
|---|---|---|---|
| [M1] PHY constraints | RedCap FR1 PRB、天線、HD-FDD guard | [x] | `UT-M1-001`, `UT-M1-002` |
| [M2] RRC/SIB1 RedCap | SIB1 RedCap support、barring gate | [x] | `UT-M2-001`, `UT-M2-002`, `FV-M2-001` |
| [M3] BWP/CORESET/RA | RedCap initial BWP、CORESET#0 Case A/B、RA BWP 對齊 | [x] | `RT-M3-CASEA`, `RT-M3-CASEB`, `FV-M3-CASEB` |
| [M4] SDT/RRC_INACTIVE | RedCap SDT FSM 與 transition log | [x] | `UT-M4-001`, `UT-M4-002` |
| [M4-B] DRX/eDRX/PSM | Connected DRX、eDRX、NAS PSM boundary | [x] | `UT-M4B-001/002/003`, `FV-M4B-BOUNDARY` |
| [M5] mMTC scaling | 30/32/48/56 UE Case B runtime scaling | [x] | `RT-M5-032`, `RT-M5-048`, `RT-M5-056` |
| [M6] Docs/evidence | 報告、traceability、learning reports | [x] | `redcap_library/library_reports_summary/m6_evidence_package_summary.md` |
| [M7] Repo hygiene | approved cleanup，`test_log` 高價值證據已轉入 `redcap_library` | [x] | `redcap_library/library_reports_summary/redcap_test_log_curated_summary.md` |

## RedCap 參數總表
### gNB RedCap YAML 參數
| 參數 | 目前典型值 | 作用 | 程式入口 | 規範對應 |
|---|---:|---|---|---|
| `cellBarredRedCap1Rx_r17` | `0/1` | 控制 [1Rx RedCap UE] 是否被 SIB1 barred | `openair2/GNB_APP/gnb_config.c`, `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` | TS 38.331 Section 6.3.1 / 6.3.2 [Needs Verification] |
| `cellBarredRedCap2Rx_r17` | `0/1` | 控制 [2Rx RedCap UE] 是否被 SIB1 barred | `fill_redcap_sib1()` | TS 38.331 Section 6.3.1 / 6.3.2 [Needs Verification] |
| `halfDuplexRedCapAllowed_r17` | `1` | 宣告 cell 允許 HD-FDD RedCap，並觸發 scheduler gap floor | `redcap_half_duplex_allowed_requested()`, `nr_redcap_effective_min_rxtxtime()` | TS 38.306 Section 4 [Needs Verification] |
| `redcap_inactive_allowed` | `1` | 啟用 local [RedCap SDT/RRC_INACTIVE] FSM hook | `nr_redcap_sdt_fsm_init()` | TS 38.331 RRC_INACTIVE / SDT clause [Needs Verification] |
| `intraFreqReselectionRedCap_r17` | `0` | SIB1 RedCap intra-frequency reselection flag | `fill_redcap_sib1()` | TS 38.331 Section 6.3.2 [Needs Verification] |
| `initialDLBWPStart_r17` | `0` | RedCap initial DL BWP 起始 PRB | `get_redcap_initial_bwp_config()` | TS 38.331 Section 6.3.2 [Needs Verification] |
| `initialDLBWPSize_r17` | `51` | 30 kHz SCS 下 RedCap 20 MHz BWP size | `nr_redcap_configure_initial_bwp()` | TS 38.101-1 Section 5.3; TS 38.306 Section 4 [Needs Verification] |
| `initialDLBWPSubcarrierSpacing_r17` | `1` | RedCap initial DL BWP SCS，`1` 對應 30 kHz | `nr_redcap_fr1_max_prbs_from_scs()` | TS 38.101-1 Section 5.3 [Needs Verification] |
| `coreset0_redcap_mode_r17` | `0/1` | `0` = [Case A]，`1` = [Case B] | `nr_redcap_is_valid_coreset0_mode()` | TS 38.213 Section 13 [Needs Verification] |
| `initialDLBWPControlResourceSetZero_r17` | `10` | RedCap DL BWP 內的 CORESET0 value | `nr_redcap_configure_initial_bwp()` | TS 38.213 Section 13 [Needs Verification] |
| `initialDLBWPSearchSpaceZero_r17` | `0` | RedCap DL BWP 內的 SearchSpace0 value | `nr_redcap_configure_initial_bwp()` | TS 38.213 Section 13 [Needs Verification] |
| `initialULBWPStart_r17` | `0` | RedCap initial UL BWP 起始 PRB | `nr_redcap_configure_initial_bwp()` | TS 38.331 Section 6.3.2 [Needs Verification] |
| `initialULBWPSize_r17` | `51` | RedCap initial UL BWP size | `nr_redcap_configure_initial_bwp()` | TS 38.101-1 Section 5.3 [Needs Verification] |
| `initialULBWPSubcarrierSpacing_r17` | `1` | RedCap initial UL BWP SCS | `nr_redcap_configure_initial_bwp()` | TS 38.101-1 Section 5.3 [Needs Verification] |
| `initialULPUCCH_ResourceCommonRedCap_r17` | `0` | RedCap UL BWP PUCCH common resource index | `clone_redcap_uplink_bwp()`, UE `nr_ue_configure_pucch()` | TS 38.331 Section 6.3.2; TS 38.213 PUCCH clause [Needs Verification] |

### UE RedCap YAML 參數
| 參數 | 預設/用途 | 程式入口 | 驗證重點 |
|---|---|---|---|
| `enable` | 啟用 UE-side RedCap capability injection | `openair3/UICC/nr_redcap_config.c` | log `nrue_recap RedCap config` |
| `band` | RedCap capability band，例如 `78` | `load_nr_redcap_config()` | UE capability 與 scenario band 一致 |
| `support_of_redcap_r17` | 對 gNB 宣告支援 RedCap | `load_nr_redcap_config()` | gNB RRC 收到 RedCap capability |
| `support_of_16drb_redcap_r17` | RedCap 16 DRB capability | `load_nr_redcap_config()` | 目前不是 M5 runtime blocker |
| `pdcp_drb_long_sn_redcap_r17` | PDCP long SN capability | `rrc_gNB.c`, `rrc_gNB_radio_bearers.c` | M5 曾修正/確認 PDCP SN 邊界 |
| `rlc_am_drb_long_sn_redcap_r17` | RLC AM long SN capability | `load_nr_redcap_config()` | capability trace |
| `number_of_rx_redcap_r17` | UE-side 1Rx/2Rx barring 判斷 | `nr_rrc_redcap_sib1_access_allowed()` | 1Rx barred 時 UE 不應 attach |
| `half_duplex_fdd_type_a_redcap_r17` | UE-side HD-FDD Type A access gate | `nr_rrc_redcap_sib1_access_allowed()` | 若 SIB1 無 `halfDuplexRedCapAllowed-r17`，HD-FDD UE 會 barred |

### mMTC Runtime 環境變數
| 變數 | Accepted 56 UE 建議值 | 作用 | 驗證重點 |
|---|---|---|---|
| `GNB_REDCAP_CONFIG` | `redcap_library/library_gnb_config/gnb_redcap_mmtc_case_b_final.yaml` | 指定 Case B gNB runtime config | 確認 `coreset0_redcap_mode_r17: 1` |
| `MMTC_TOTAL_UES` | `64` | overlay 產生 UE1..UE64 | 可 sample 56，不必只產生 56 |
| `MMTC_SAMPLE_UES` | `1..56` | 指定要驗證的 UE 清單 | accepted run 是 56 個 sample 全 pass |
| `MMTC_CN_COMPOSE` | `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml` | 指定外部 CN compose | CN/UPF 必須已修正 interface 與 static discovery |
| `MMTC_USE_EXISTING_CN_DB` | `1` | 使用既有 CN DB，不產生 mMTC subscriber overlay | 避免覆蓋目前可用 DB |
| `MMTC_UE_START_GAP` | `8` | UE 啟動間距 | 降低同時 RA/CN 壓力 |
| `MMTC_FORWARD_PING_MODE` | `parallel` | forward ping 同步驗證 | 最終 `forward_ping_ok=56` |
| `MMTC_RUN_REVERSE_PING` | `0` | 關閉 reverse ping | 避免非必要壓力干擾 |
| `MMTC_IPERF_ENABLE` | `0` | 關閉 iperf | accepted capacity 以 attach/PDU/tun/ping 為主 |
| `MMTC_PUCCH_COMMON_FALLBACK_BWP0` | `1` | UE initial PUCCH 若 current BWP common resource 缺失，可 fallback BWP0 common | `pucch_ResourceCommon is NULL=0` |

### CN Static Discovery 邊界參數
| 參數 | Accepted 56 UE 狀態 | 作用 | 注意 |
|---|---|---|---|
| `register_nf.general` | `no` | 關閉 NRF dynamic registration 壓力 | 屬於 CN 壓力 mitigation，不是 RAN scheduler fix |
| `amf.support_features_options.enable_smf_selection` | `no` | 避免 AMF runtime SMF selection 空候選 | 對應 56 UE pre-fix 的 `SMF Selection, no SMF candidate` |
| SMF UPF `host` | `oai-upf` | static UPF endpoint | UPF interface 需 `sbi/n3/n4 -> eth1`, `n6 -> eth0` |
| SMF UPF `port` | `8805` | N4 PFCP endpoint | 56 UE static CN 後 `PDU=56/56` |

## 實作邏輯導讀
### [M1] PHY / PRB / HD-FDD
| 步驟 | 你要理解的事 | 主要檔案/函數 | 觀察點 |
|---:|---|---|---|
| 1 | YAML 先宣告 RedCap BWP size，例如 `initialDLBWPSize_r17: 51` | `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml` | 30 kHz SCS 下 51 PRB 對應 20 MHz 級 RedCap BWP |
| 2 | gNB config parser 讀取 `redCapInitialBWP_r17` 子區塊 | `openair2/GNB_APP/gnb_config.c` `get_redcap_initial_bwp_config()` | 若只填部分 start/size/scs 會被 `AssertFatal` 擋下 |
| 3 | RedCap BWP helper 檢查 PRB 上限 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c` `nr_redcap_configure_initial_bwp()` | 15 kHz 對應 106 PRB，30 kHz 對應 51 PRB |
| 4 | HD-FDD 開啟時提高 scheduler minRXTXTIME floor | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h` `nr_redcap_effective_min_rxtxtime()` | floor 是 local project assumption：`NR_REDCAP_HD_FDD_MIN_RXTXTIME=6` |
| 5 | gNB ULSCH scheduler 使用 effective gap | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c` | 避免 HD-FDD RedCap 被安排過近的 DL/UL switch |

[Modification Point] → [M1 RedCap PRB cap helper]  
[Reason] → [RedCap UE] 的 initial BWP 不能沿用 full cell 106 PRB 行為，否則後續 PDCCH/PDSCH/PUCCH 資源會超出 RedCap 20 MHz 假設。  
[Before vs. After Comparison] → [Before] YAML 參數可能進入 full-cell 路徑；[After] `nr_redcap_configure_initial_bwp()` 會用 SCS 對應上限檢查 RedCap BWP。  
[Discussion Point] → exact PRB/BW mapping 請以 TS 38.101-1 Section 5.3 與本地 spec 再確認，本文保留 `[Needs Verification]`。

### [M2] RRC / SIB1 RedCap Access Gate
| 步驟 | 你要理解的事 | 主要檔案/函數 | 觀察點 |
|---:|---|---|---|
| 1 | gNB 讀 `cellBarredRedCap1Rx_r17`、`cellBarredRedCap2Rx_r17`、`halfDuplexRedCapAllowed_r17` | `openair2/GNB_APP/gnb_config.c` | log 會列出 RedCap access flags |
| 2 | gNB 把 RedCap access fields 填進 SIB1 v1700 extension | `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` `fill_redcap_sib1()` | 建立 `redCap_ConfigCommon_r17` |
| 3 | UE 讀自己的 RedCap capability | `openair3/UICC/nr_redcap_config.c` `load_nr_redcap_config()` | `support_of_redcap_r17`、Rx 數、HD-FDD Type A |
| 4 | UE 用 SIB1 RedCap fields 決定 cell 是否允許 access | `openair2/RRC/NR_UE/rrc_ue_redcap.c` `nr_rrc_redcap_sib1_access_allowed()` | 1Rx barred 或 HD-FDD 不允許時，UE 應停止 attach |
| 5 | 通過 access gate 後，UE 進入 RedCap initial BWP / RA path | `openair2/LAYER2/NR_MAC_UE/nr_ue_redcap_bwp.c` | RedCap UE 優先拿 `initialDownlinkBWP_RedCap_r17` |

[Modification Point] → [M2 RedCap SIB1 encode/decode + barring gate]  
[Reason] → RedCap UE 不應只靠一般 UE path attach；它必須先看 SIB1 是否允許 [1Rx/2Rx/HD-FDD] RedCap access。  
[Before vs. After Comparison] → [Before] RedCap barring field 可能只是 config，不一定形成 UE access gate；[After] gNB SIB1 與 UE access decision 有對應函數。  
[Discussion Point] → `fill_redcap_sib1()` 內的 field mapping comment 已明確標註 TS 38.331 clause `[Needs Verification]`，不能升級成 verified。

### [M3] BWP / CORESET#0 Case A/B / RA BWP Domain
| 步驟 | 你要理解的事 | 主要檔案/函數 | 觀察點 |
|---:|---|---|---|
| 1 | `coreset0_redcap_mode_r17=0` 是 [Case A] | `nr_redcap_coreset0_mode_to_string()` | log string：`case-a-full-cell` |
| 2 | `coreset0_redcap_mode_r17=1` 是 [Case B] | `ci-scripts/redcap_prepare_runtime_config.py` | runtime config 會 rewrite mode line |
| 3 | gNB 在 RedCap Msg2 path 切換到 Case B BWP | `gNB_scheduler_RA.c` `configure_redcap_msg2_bwp()` | log `[RedCap RA][gNB Msg2 gate] using RedCap Case B RA path` |
| 4 | gNB 判斷 Msg1 是否來自 RedCap preamble partition | `get_redcap_msg1_rach_config()`, `nr_redcap_is_msg1_preamble()` | log `[RedCap RA][gNB Msg1] detected RedCap preamble` |
| 5 | gNB Msg2 DCI/PDSCH 使用同一個 RedCap BWP domain | `fill_dci_pdu_rel15()`, Msg2 DCI log | 觀察 `coreset_id`, `bwp_start`, `bwp_size`, `pdsch_rb_size` |
| 6 | UE RA-RNTI monitor 也要切到相同 BWP domain | `nr_ue_dci_configuration.c`, `nr_ue_procedures.c` | 不能再出現 Case B gNB/UE BWP mismatch |

[Modification Point] → [M3 CORESET#0 Case A/B switch]  
[Reason] → RedCap Case B 需要讓 common CORESET 位在 RedCap BWP 內；若 gNB 用 BWP51 發 Msg2，但 UE 還在 full-cell Type0 CSS domain monitor，就會 RAR/LDPC/Msg2 path 失敗。  
[Before vs. After Comparison] → [Before] Case B 容易出現 gNB/UE common search space domain 不一致；[After] gNB log 與 UE monitor log 可共同證明 BWP51 path。  
[Discussion Point] → TS 38.213 Section 13 是 CORESET#0/Type0 CSS 對應主軸，但 exact RedCap Case A/B subsection 仍 `[Needs Verification]`。

### [M4] SDT / RRC_INACTIVE FSM
| 步驟 | 你要理解的事 | 主要檔案/函數 | 觀察點 |
|---:|---|---|---|
| 1 | gNB YAML 用 `redcap_inactive_allowed` 控制 local SDT FSM 是否啟用 | `gnb_config.c` | `rc->inactive_allowed` |
| 2 | UE context 建立時初始化 SDT FSM | `gNB_scheduler_primitives.c` `get_new_nr_ue_inst()` | 初始 inactive_allowed 是 false |
| 3 | UE 變成 connected 後，用 cell RedCap config 重新初始化 FSM | `add_connected_nr_ue()` | `inactive_allowed = nr_mac->radio_config.redcap->inactive_allowed` |
| 4 | UL data 觸發 FSM 選 MsgA 或 Msg3 path | `nr_mac_sdt_fsm.c` `nr_redcap_sdt_run_ul_data_arrival()` | sequence：`IDLE -> TRIGGER -> MSGA/MSG3 -> ACTIVE` |
| 5 | UL burst complete 後可回到 INACTIVE | `nr_redcap_sdt_complete_ul_burst()` | transition log 可寫入 `nrMAC_redcap_sdt.log` |

[Modification Point] → [M4 RedCap SDT transition logging]  
[Reason] → SDT/RRC_INACTIVE 是狀態流程，若沒有 transition log，學生很難確認目前是在 MsgA path、Msg3 fallback，還是仍在 connected path。  
[Before vs. After Comparison] → [Before] 只能從一般 scheduler log 旁推；[After] 有 `nr_redcap_sdt_fsm_t` 與 transition record 可對照單元測試。  
[Discussion Point] → TS 38.321 SDT 與 TS 38.331 RRC_INACTIVE exact clause 尚未在本地 traceability 中確認，維持 `[Needs Verification]`。

### [M4-B] DRX / eDRX / PSM Low-Power Boundary
| 步驟 | 你要理解的事 | 主要檔案/函數 | 觀察點 |
|---:|---|---|---|
| 1 | Connected DRX 先判斷 UE 是否在 active slot | `openair2/LAYER2/NR_MAC_UE/nr_ue_drx.c` `nr_ue_drx_is_active()` | 未配置 DRX 時回傳 active |
| 2 | pending SR 或 inactivity timer 仍會讓 UE active | `nr_ue_drx_is_active_slot()` | 避免有待送 SR 卻 sleep |
| 3 | UE scheduler 只有 active 時才進行一般 DCI monitoring | `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c` | `ue_dci_configuration()` 被 active gate 包住 |
| 4 | eDRX 從 SIB1 v1700 讀 idle/inactive allowed flag | `openair2/RRC/NR_UE/rrc_ue_lowpower.c` | log `SIB1 eDRX allowed: idle=... inactive=...` |
| 5 | NAS PSM 從 Registration Accept 讀 T3324/T3512 | `openair3/NAS/NR_UE/nr_nas_msg.c`, `nr_nas_lowpower.c` | log `NAS PSM timers: T3324=... T3512=...` |

[Modification Point] → [M4-B low-power boundary]  
[Reason] → DRX/eDRX/PSM 不是同一層：DRX 在 UE MAC active-time，eDRX 在 RRC/SIB1 paging permission，PSM 在 NAS timer。  
[Before vs. After Comparison] → [Before] 容易把三者混成一個「省電開關」；[After] 每個機制都有自己的函數入口、測試層級與 runtime claim 邊界。  
[Discussion Point] → 目前 [Connected DRX] 是 unit/flow-level pass；[eDRX/PSM] 是 runtime log-level pass，不宣稱 CN-driven sleep 已完成。

### [M5] mMTC RA / Msg4 / PUCCH / CN Boundary
| 步驟 | 你要理解的事 | 主要檔案/函數 | 觀察點 |
|---:|---|---|---|
| 1 | Case B runtime 用 51 PRB RedCap BWP，UE 分批啟動 | `ci-scripts/redcap_mmtc_smoke_validation.sh` | `MMTC_UE_START_GAP=8` |
| 2 | gNB Msg2 必須在 RAR response window 內排出 | `gNB_scheduler_RA.c` `msg2_in_response_window()` | log `[RedCap RA][gNB Msg2 window fail]` |
| 3 | Msg2 DCI 成功不代表 RAR 無 retry | `gNB_scheduler_RA.c` Msg2 DCI log | compare `Msg2 DCI` vs `RAR reception failed` |
| 4 | Msg2/Msg4 PDSCH 要在 RedCap BWP PRB 內找到空間 | `find_free_ra_pdsch_rb_start()` | log `Msg2 vrb_map fail`, `Msg4 vrb_map fail` |
| 5 | Msg4 優先用 compact allocation，必要時用 pair-pack allocation | `find_compact_ra_pdsch_allocation()`, `find_bounded_ra_pdsch_allocation()` | log `compact alloc`, `pair-pack alloc` |
| 6 | UE Msg4 ACK 需要 initial PUCCH resource | `nr_ue_configure_pucch()` | 若缺 resource，看 `MMTC_PUCCH_COMMON_FALLBACK_BWP0` |
| 7 | 56 UE pre-fix failure 曾落在 CN/NAS/PDU late stage | AMF/SMF/UPF logs | `Registration Reject`, `SMF Selection, no SMF candidate` |
| 8 | static CN discovery mitigation 後，56 UE 成為 accepted pass | `redcap_library/library_reports_summary/m5_caseb_56ue_static_cn_pass_report.md` | `56/56` attach/PDU/tun/ping |

[Modification Point] → [M5 Msg4 compact / pair-pack allocation]  
[Reason] → 30+ UE 同時進入 RA 時，Msg4 若仍吃滿 48 PRB，會把 RedCap BWP 資源塞滿，造成 `vrb_map` 與 contention failure。  
[Before vs. After Comparison] → [Before] Msg4 failure 看到 `rb_size=48 occupied_prbs=48`；[After] compact allocation 可出現 `rb=25 mcs=4 bwp=48`，pair-pack 作為 fallback。  
[Discussion Point] → 這是 scheduler load mitigation，仍需用 Msg2 window、Msg4 ACK、contention timer、ping 結果一起判斷，不可只看單一 marker。

[Modification Point] → [M5 UE PUCCH BWP0 common fallback]  
[Reason] → 某些 UE 在 RRCSetup 後 current BWP 的 `pucch_ResourceCommon` 可能為 NULL，Msg4 ACK 會失去 initial PUCCH resource。  
[Before vs. After Comparison] → [Before] UE log 出現 `pucch_ResourceCommon is NULL ... fallback=0`；[After] `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1` 時可改用 BWP0 common resource。  
[Discussion Point] → accepted 56 UE run 中 `pucch_ResourceCommon is NULL=0`，代表此 blocker 已從 pass run 中消失。

[Modification Point] → [M5 CN static discovery mitigation]  
[Reason] → 56 UE 首次 threshold run 的 terminal failure 是 CN auth/SMF selection pressure，不是 Msg2 CCE、LDPC、Msg4 contention 或 PUCCH fallback。  
[Before vs. After Comparison] → [Before] `UE54/UE55` Registration Reject、`UE56` no SMF candidate；[After] static CN 後 `Request Authentication Vectors failure=0`, `Registration Reject=0`, `SMF Selection no candidate=0`。  
[Discussion Point] → 這是 [CN boundary fix]，不能拿來宣稱 RAN scheduler 變強；它只是移除 CN blocker，讓 RAN RA/Msg4 counter 可以被乾淨觀察。

## 56 UE Case B 模擬導讀
### 逐行前置檢查
| 行 | 指令/動作 | 目的 | 預期 |
|---:|---|---|---|
| 1 | `cd /home/tonywang/OAI/Red_cap_openairinterface5g` | 進入 OAI RedCap repo | 後續路徑相對正確 |
| 2 | 確認 Docker 權限 | RFsim/CN 都用 Docker | `docker ps` 可讀 |
| 3 | 確認 local image marker | 確認 gNB binary 有最新 Msg4 allocation marker | `strings /opt/oai-gnb/bin/nr-softmodem` 可看到 `pair-pack alloc` |
| 4 | 確認 CN config | 移除 NRF/SMF dynamic discovery 壓力 | `register_nf.general=no`, `enable_smf_selection=no`, UPF `port=8805` |
| 5 | 確認 Case B gNB config | 啟用 RedCap Case B | `coreset0_redcap_mode_r17: 1` |
| 6 | 設定 56 UE sample | 驗證 accepted capacity | `MMTC_SAMPLE_UES=1..56` |
| 7 | 關閉 reverse ping/iperf | 避免非必要壓力 | `MMTC_RUN_REVERSE_PING=0`, `MMTC_IPERF_ENABLE=0` |
| 8 | 跑 smoke validation | 產出 compiler log、gNB log、UE logs | summary 顯示 `56/56` |

### 建議重跑指令
```bash
cd /home/tonywang/OAI/Red_cap_openairinterface5g

sudo env \
  GNB_REDCAP_CONFIG=/home/tonywang/OAI/Red_cap_openairinterface5g/redcap_library/library_gnb_config/gnb_redcap_mmtc_case_b_final.yaml \
  MMTC_TOTAL_UES=64 \
  MMTC_SAMPLE_UES="$(seq -s ' ' 1 56)" \
  MMTC_CN_COMPOSE=/home/tonywang/OAI/oai-cn5g/docker-compose.yaml \
  MMTC_USE_EXISTING_CN_DB=1 \
  MMTC_UE_START_GAP=8 \
  MMTC_FORWARD_PING_MODE=parallel \
  MMTC_RUN_REVERSE_PING=0 \
  MMTC_IPERF_ENABLE=0 \
  MMTC_PUCCH_COMMON_FALLBACK_BWP0=1 \
  bash ci-scripts/redcap_mmtc_smoke_validation.sh 2>&1 | tee test_log/compiler_logs/mmtc_smoke_56ue_caseb_static_cn_$(date +%F_%H-%M-%S)_manual.log
```

### 如果 shell 不想用 `seq`
```bash
MMTC_SAMPLE_UES="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56"
```

### Accepted 56 UE 應看到的結果
| Counter | Accepted 值 | 解讀 |
|---|---:|---|
| running | `56/56` | UE containers 存活 |
| attach | `56/56` | UE 都完成 Registration Accept |
| PDU | `56/56` | UE 都完成 PDU Session Establishment Accept |
| tunnel | `56/56` | 每個 UE 有 `oaitun_ue1` |
| forward ping | `56/56` | UE user-plane 可達 |
| gNB restart | `0` | 沒有中途重啟 |
| Msg2 DCI | `56` | 每個 UE 至少一次成功排出 Msg2 DCI |
| Msg2 window fail | 可大於 `0` | 代表 transient RAR retry pressure，不等於 terminal failure |
| Msg2 `vrb_map` fail | `0` | Msg2 PRB allocation 沒有塞爆 |
| Msg4 `vrb_map` fail | `0` | Msg4 PRB allocation 沒有塞爆 |
| contention timer expired | `0` | contention resolution 沒有 terminal timeout |
| Msg4 ACK / CBRA success | `56` | 所有 sample UE 完成 contention resolution |
| `pucch_ResourceCommon is NULL` | `0` | PUCCH fallback blocker 不存在 |
| LDPC decode failed | `0` | Case B DCI/PDSCH BWP 對齊沒有 decode blocker |

### 常見誤判
- [誤判 1]：看到 `RAR reception failed` 就認為 RA 失敗。
  - [正確判讀]：如果最後 attach/PDU/tun/ping 全 pass，這是 transient retry pressure。
- [誤判 2]：看到 64 UE `tun=0` 就認為所有 UE PDU 都失敗。
  - [正確判讀]：64 UE run 是 gNB restart 後的 final validation 結果；pre-restart 已有 `59/64` Registration/PDU accept。
- [誤判 3]：static CN pass 代表 RAN 變強。
  - [正確判讀]：static CN 只是移除 CN discovery/auth/SMF blocker；RAN 要看 Msg2/Msg4/PUCCH/contention counters。
- [誤判 4]：Case B 只要 `coreset0_redcap_mode_r17=1` 就一定正確。
  - [正確判讀]：還要看 gNB Msg2 DCI BWP 與 UE RA-RNTI monitor BWP 是否一致。

## 總檢核表：流程 -> 規範 Clause -> 證據
| 流程 | 要驗證的對應規範 clause | 程式/參數證據 | Runtime/測試證據 | 狀態 |
|---|---|---|---|---|
| RedCap FR1 BWP PRB cap | TS 38.101-1 Section 5.3; TS 38.306 Section 4 [Needs Verification] | `nr_redcap_fr1_max_prbs_from_scs()`, `nr_redcap_configure_initial_bwp()` | `UT-M1-001` | [x] |
| RedCap HD-FDD gap floor | TS 38.306 Section 4 [Needs Verification] | `NR_REDCAP_HD_FDD_MIN_RXTXTIME=6`, `nr_redcap_effective_min_rxtxtime()` | `UT-M1-002` | [x] |
| SIB1 RedCap access fields | TS 38.331 Section 6.3.1 / 6.3.2 [Needs Verification] | `fill_redcap_sib1()` | `UT-M2-001`, `FV-M2-001` | [x] |
| UE 1Rx/2Rx barring decision | TS 38.331 Section 6.3.2 [Needs Verification] | `nr_rrc_redcap_sib1_access_allowed()` | `UT-M2-002` | [x] |
| RedCap initial DL/UL BWP | TS 38.331 Section 6.3.2 [Needs Verification] | `initialDownlinkBWP_RedCap_r17`, `initialUplinkBWP_RedCap_r17` | `UT-M3-001` | [x] |
| CORESET#0 Case A/B | TS 38.213 Section 13 [Needs Verification] | `coreset0_redcap_mode_r17`, `nr_redcap_is_valid_coreset0_mode()` | `UT-M3-002`, `RT-M3-CASEA`, `RT-M3-CASEB` | [x] |
| UE RA-RNTI BWP-domain alignment | TS 38.213 Section 13; TS 38.321 Section 5.1 [Needs Verification] | `configure_redcap_msg2_bwp()`, UE RA DCI config | `UT-M3-003`, `FV-M3-CASEB` | [x] |
| Msg1 RedCap preamble partition | TS 38.321 Section 5.1 [Partially Verified] | `nr_redcap_configure_rach_feature_combination_preambles()`, `nr_redcap_is_msg1_preamble()` | gNB marker `[RedCap RA][gNB Msg1]` | [x] |
| RAR / Msg2 response window | TS 38.321 Section 5.1.4 [Needs Verification] | `msg2_in_response_window()` | `Msg2 window fail` classified through 56 UE | [x] |
| Msg2 PDSCH PRB allocation | TS 38.321 Section 5.1; TS 38.214 allocation exact clause [Needs Verification] | `find_free_ra_pdsch_rb_start()` | `Msg2 vrb_map fail=0` in accepted 56 UE | [x] |
| Msg4 contention resolution | TS 38.321 Section 5.1.5 [Needs Verification] | Msg4 compact/pair-pack allocation path | `Msg4 ACK / CBRA success=56`, timer expired `0` | [x] |
| UE Msg4 ACK PUCCH resource | TS 38.331 Section 6.3.2; TS 38.213 PUCCH exact clause [Needs Verification] | `nr_ue_configure_pucch()`, `MMTC_PUCCH_COMMON_FALLBACK_BWP0` | `pucch_ResourceCommon is NULL=0` | [x] |
| Connected DRX active-time gate | TS 38.321 Section 5.7; TS 38.331 Section 6.3.2 [Partially Verified] | `nr_ue_drx_is_active()`, `nr_ue_scheduler.c` active gate | `UT-M4B-001` | [x] |
| eDRX SIB1 flag parse | TS 38.331 Section 6.3.2; TS 38.304 paging exact clause [Needs Verification] | `nr_rrc_apply_sib1_edrx()` | runtime log `SIB1 eDRX allowed` | [x] |
| NAS PSM timer hooks | TS 24.501 Section 8.2.7.1.1; Section 5.5.1 [Partially Verified] | `nr_nas_psm_update_timers()`, `nr_nas_psm_low_power_ready()` | runtime log `NAS PSM timers` | [x] |
| 56 UE user-plane accepted capacity | TS 38.321 Section 5.1 runtime flow; NAS exact clauses [Needs Verification] | `redcap_mmtc_smoke_validation.sh` | `56/56` attach/PDU/tun/ping | [x] |
| 64 UE upper-bound classification | Not a 3GPP conformance claim | gNB restart telemetry | `RT-M5-064` classified `[!]` | [!] classified |
| O-RAN/FlexRIC runtime check | O-RAN non-3GPP | existing FlexRIC image/runtime checks | no new SDK claim | [Out of 3GPP Scope] |

## 教學單元 1：讀懂 RedCap 參數
### 學習目標
- [Goal]：能從 YAML 參數推到 gNB parser 與 UE access decision。
- [要讀的檔案]：
  - `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml`
  - `openair2/GNB_APP/gnb_paramdef.h`
  - `openair2/GNB_APP/gnb_config.c`
  - `openair3/UICC/nr_redcap_config.c`
  - `openair2/RRC/NR_UE/rrc_ue_redcap.c`
### 導讀任務
- [Step 1]：找到 `GNB_CONFIG_STRING_REDCAP`，確認 gNB RedCap section 的 key 名稱。
- [Step 2]：找到 `GNB_REDCAP_PARAMS_DESC` 與 `GNB_REDCAP_INITIAL_BWP_PARAMS_DESC`，確認 parser 有哪些欄位。
- [Step 3]：找到 `load_nr_redcap_config()`，確認 UE-side RedCap capability 預設值。
- [Step 4]：找到 `nr_rrc_redcap_sib1_access_allowed()`，確認 1Rx barred 與 HD-FDD barred 的判斷式。
### 練習題
- [Basic]：`number_of_rx_redcap_r17=1` 且 SIB1 `cellBarredRedCap1Rx_r17=barred` 時，UE 應該繼續 attach 嗎？
- [Applied]：如果 UE 設 `half_duplex_fdd_type_a_redcap_r17=1`，但 SIB1 沒有 `halfDuplexRedCapAllowed-r17`，哪個函數會把 cell 視為 barred？
- [Advanced]：請設計一個 A/B 測試，證明 1Rx barring gate 是 UE access blocker，而不是後續 RA/Msg2 blocker。

## 教學單元 2：讀懂 RedCap BWP 與 CORESET#0 Case B
### 學習目標
- [Goal]：能解釋 Case B 為什麼要同時修 gNB Msg2 與 UE RA-RNTI monitor BWP。
- [要讀的檔案]：
  - `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c`
  - `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c`
  - `openair2/LAYER2/NR_MAC_UE/nr_ue_redcap_bwp.c`
  - `openair2/LAYER2/NR_MAC_UE/nr_ue_dci_configuration.c`
### 導讀任務
- [Step 1]：在 `nr_mac_redcap_bwp.c` 找 `nr_redcap_fr1_max_prbs_from_scs()`，確認 30 kHz SCS 對應 51 PRB。
- [Step 2]：在 `gNB_scheduler_RA.c` 找 `configure_redcap_msg2_bwp()`，看 Case B 如何設定 `search_space`、`coreset`、DL/UL BWP。
- [Step 3]：找 log marker `[RedCap RA][gNB Msg2 DCI]`，確認可輸出 `coreset_id`、`bwp_start`、`bwp_size`。
- [Step 4]：對照 UE RA-RNTI monitor log，確認 UE 監看的 BWP 和 gNB 發 Msg2 的 BWP 一致。
### 練習題
- [Basic]：`coreset0_redcap_mode_r17=1` 代表 Case A 還是 Case B？
- [Applied]：若 gNB log 是 `coreset_id=1 bwp_size=51`，但 UE RAR LDPC decode failed，下一步應優先比對哪兩個 BWP domain？
- [Advanced]：設計一個 log parser，輸入 gNB/UE log，輸出 Case B 是否存在 gNB/UE BWP mismatch。

## 教學單元 3：讀懂 RA / Msg2 / Msg4 under mMTC Load
### 學習目標
- [Goal]：能區分 transient RA retry 與 terminal RA failure。
- [要讀的檔案]：
  - `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c`
  - `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c`
  - `openair2/LAYER2/NR_MAC_UE/nr_ue_procedures.c`
  - `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/milestones/M5_mmtc_runtime_scaling.md`
### 導讀任務
- [Step 1]：找到 `msg2_in_response_window()` 的 fail log，理解 `diff` 與 `window`。
- [Step 2]：找到 `find_compact_ra_pdsch_allocation()`，理解 compact allocation 如何縮小 Msg4 PRB 需求。
- [Step 3]：找到 `pair-pack alloc` marker，理解 compact 不足時如何限制 `rb_cap=bwp/2`。
- [Step 4]：在 M5 evidence 中比較 32/48/56 UE 的 `Msg2 window fail` 成長。
### 練習題
- [Basic]：`Msg2 DCI=56` 且 `RAR reception failed=55`，但最後 `attach=56/56`，這是 pass 還是 fail？
- [Applied]：如果 `Msg4 vrb_map fail > 0` 且 `contention timer expired > 0`，你會先看 Msg4 `rb_size` 還是 CN auth log？
- [Advanced]：請定義一個 [RA pressure score]，把 `Msg2 window fail`、`vrb_map fail`、`contention timer`、`CBRA success` 合成一個趨勢指標。

## 教學單元 4：讀懂 UE PUCCH Fallback
### 學習目標
- [Goal]：能理解 Msg4 ACK 為什麼會被 `pucch_ResourceCommon` 影響。
- [要讀的檔案]：
  - `openair2/LAYER2/NR_MAC_UE/nr_ue_procedures.c`
  - `ci-scripts/redcap_mmtc_smoke_validation.sh`
  - `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml`
### 導讀任務
- [Step 1]：找到 `mmtc_pucch_common_fallback_bwp0_enabled()`，確認它讀 `MMTC_PUCCH_COMMON_FALLBACK_BWP0`。
- [Step 2]：找到 `find_ul_bwp_by_id(mac, 0)`，理解 fallback 只找 BWP0 common resource。
- [Step 3]：找到 error log `pucch_ResourceCommon is NULL`，確認 fallback 狀態會一起印出。
- [Step 4]：在 accepted 56 UE report 中確認該 marker 為 `0`。
### 練習題
- [Basic]：`MMTC_PUCCH_COMMON_FALLBACK_BWP0=0` 時，fallback 會啟用嗎？
- [Applied]：如果 UE log 出現 `fallback=1` 但仍 `pucch_ResourceCommon is NULL`，代表 BWP0 common resource 存在還是不存在？
- [Advanced]：請設計一個 control run，比較 fallback on/off 對 Msg4 ACK / CBRA success 的影響。

## 教學單元 5：讀懂 Low-Power Boundary
### 學習目標
- [Goal]：能把 DRX、eDRX、PSM 分層，不把三者混成單一省電功能。
- [要讀的檔案]：
  - `openair2/LAYER2/NR_MAC_UE/nr_ue_drx.c`
  - `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c`
  - `openair2/RRC/NR_UE/rrc_ue_lowpower.c`
  - `openair3/NAS/NR_UE/nr_nas_lowpower.c`
  - `openair3/NAS/NR_UE/nr_nas_msg.c`
### 導讀任務
- [Step 1]：看 `nr_ue_drx_is_active_slot()`，列出讓 UE 保持 active 的條件。
- [Step 2]：看 `nr_ue_scheduler.c`，確認 DCI monitoring 被 `connected_drx_active` gate 控制。
- [Step 3]：看 `nr_rrc_apply_sib1_edrx()`，確認 eDRX 只是讀 SIB1 allowed flag。
- [Step 4]：看 `nr_nas_psm_low_power_ready()`，確認 PSM ready 需要 registered + idle + active time expired。
### 練習題
- [Basic]：未配置 DRX 時，`nr_ue_drx_is_active_slot()` 回傳 active 還是 inactive？
- [Applied]：pending SR 時，UE 應該保持 active 還是進入 sleep？
- [Advanced]：請說明為什麼目前不能宣稱 [CN-driven PSM sleep] 已完整完成。

## 教學單元 6：重跑 56 UE 並寫檢核報告
### 學習目標
- [Goal]：能獨立重跑 accepted 56 UE Case B，並寫出 pass/fail 判讀。
- [要讀的檔案]：
  - `ci-scripts/redcap_mmtc_smoke_validation.sh`
  - `agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/validation/runtime_checklist.md`
  - `redcap_doc/checklists/redcap_milestone_validation_checklist.md`
### 導讀任務
- [Step 1]：先確認 `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1` 有進入 script info log。
- [Step 2]：跑 56 UE command，保存 `tee` log。
- [Step 3]：讀 summary，填 running/attach/PDU/tun/ping。
- [Step 4]：讀 gNB log，填 Msg2/Msg4 counters。
- [Step 5]：讀 CN log，確認 auth-vector、Registration Reject、SMF candidate marker 都是 `0`。
- [Step 6]：寫 work daily log，記錄 test item、coverage、known issues。
### 練習題
- [Basic]：accepted 56 UE pass 的最重要 5 個結果 counter 是哪些？
- [Applied]：如果 `attach=56/56` 但 `tun=54/56`，你會先查 AMF、SMF、UPF 還是 gNB Msg2？
- [Advanced]：請設計一份 64 UE future telemetry plan，說明要收 Docker stats、host memory、gNB restart cause 與 dmesg 的哪些資訊。

## 後續可選工作
- [Optional 1]：若未來要挑戰 64 UE，先做 [host resource telemetry]，不要直接改 scheduler。
- [Optional 2]：若要做 M7 cleanup，必須先列出 deletion candidate、引用掃描、影響評估，再取得明確同意。
- [Optional 3]：若要啟動 O-RAN xApp/rApp/dApp 實作，應另開 task plan；目前 RedCap mMTC v1 不把 SDK 實作列為完成項。
