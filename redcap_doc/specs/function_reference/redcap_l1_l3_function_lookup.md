# RedCap L1-L3 函式查詢手冊

## 使用方式
- 先依層級找函式，再用檔案路徑追 code。
- 規範欄位為對應方向；精確 clause 仍需用 local spec/PDF 核對。
- 標示 `[Needs Verification]` 代表需再核對 3GPP clause。

## L1 PHY
| 函式名稱 | 使用語言 | 對應規範 | 50 字內用途 | 檔案 |
|---|---|---|---|---|
| `nr_redcap_fr1_max_prbs` | C | TS 38.306 RedCap FR1 bandwidth [Needs Verification] | 回傳 RedCap FR1 不同 SCS 的 PRB 上限。 | `openair1/PHY/INIT/nr_parms.c` |
| `nr_redcap_gnb_configured` | C | TS 38.331 RedCap SIB1 [Needs Verification] | 判斷 gNB config 是否啟用 RedCap。 | `openair1/PHY/INIT/nr_parms.c` |
| `nr_redcap_ue_configured` | C | TS 38.306 UE capability [Needs Verification] | 判斷 UE YAML 是否宣告 RedCap capability。 | `openair1/PHY/INIT/nr_parms.c` |
| `nr_assert_redcap_fr1_grid_size` | C | TS 38.104 / TS 38.306 [Needs Verification] | 檢查 RedCap FR1 grid 是否超出限制。 | `openair1/PHY/INIT/nr_parms.c` |
| `nr_validate_redcap_gnb_frame_parms` | C | TS 38.104 / TS 38.306 [Needs Verification] | 驗證 gNB frame parms 是否符合 RedCap。 | `openair1/PHY/INIT/nr_parms.c` |
| `nr_validate_redcap_ue_frame_parms` | C | TS 38.306 UE RF capability [Needs Verification] | 驗證 UE frame parms 是否符合 RedCap。 | `openair1/PHY/INIT/nr_parms.c` |

## L2 MAC / Scheduler
| 函式名稱 | 使用語言 | 對應規範 | 50 字內用途 | 檔案 |
|---|---|---|---|---|
| `redcap_half_duplex_allowed_requested` | C | TS 38.331 `halfDuplexRedCapAllowed-r17` [Needs Verification] | 讀取 gNB 是否允許 RedCap half-duplex。 | `openair2/GNB_APP/gnb_config.c` |
| `get_redcap_initial_bwp_config` | C | TS 38.331 RedCap initial BWP [Needs Verification] | 從 config/SCC 組出 RedCap initial BWP。 | `openair2/GNB_APP/gnb_config.c` |
| `get_redcap_config` | C | TS 38.331 RedCap common config [Needs Verification] | 建立 gNB RedCap runtime config 結構。 | `openair2/GNB_APP/gnb_config.c` |
| `nr_redcap_is_valid_coreset0_mode` | C | TS 38.213 CORESET#0 [Needs Verification] | 檢查 RedCap CORESET#0 模式是否合法。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h` |
| `nr_redcap_coreset0_mode_to_string` | C | TS 38.213 CORESET#0 [Needs Verification] | 將 RedCap CORESET#0 模式轉成 log 字串。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h` |
| `nr_redcap_rrc_state_to_string` | C | TS 38.331 RRC state [Needs Verification] | 將 RedCap RRC state 轉成 log 字串。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h` |
| `nr_redcap_effective_min_rxtxtime` | C | TS 38.214 HD-FDD timing [Needs Verification] | 套用 RedCap HD-FDD 最小收發切換間隔。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h` |
| `nr_redcap_sanitize_ul_prb_cap` | C | O-RAN RC / scheduler local rule | 正規化 xApp 下發的 UL PRB cap。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h` |
| `nr_redcap_effective_ul_prb_cap` | C | O-RAN RC / scheduler local rule | 將 UL grant RB 數限制在 RedCap cap 內。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h` |
| `nr_redcap_is_edge_aligned_bwp` | C | TS 38.213 Case B CORESET#0 [Needs Verification] | 判斷 RedCap BWP 是否貼齊 carrier 邊界。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h` |
| `nr_redcap_location_and_bw` | C | TS 38.331 `locationAndBandwidth` [Needs Verification] | 編碼 RedCap BWP 的 RIV locationAndBandwidth。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c` |
| `nr_redcap_rebind_common_searchspaces_to_coreset` | C | TS 38.213 SearchSpace/CORESET [Needs Verification] | 將 common search space 重新綁到 Case B CORESET。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c` |
| `nr_redcap_fr1_max_prbs_from_scs` | C | TS 38.306 RedCap FR1 bandwidth [Needs Verification] | 依 SCS 回傳 RedCap FR1 PRB 上限。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c` |
| `nr_redcap_initial_bwp_requested` | C | TS 38.331 RedCap initial BWP [Needs Verification] | 判斷設定是否要求 RedCap initial BWP。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c` |
| `nr_redcap_configure_initial_bwp` | C | TS 38.331 RedCap initial BWP [Needs Verification] | 填入 RedCap BWP start/size/SCS/RIV。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c` |
| `nr_redcap_validate_coreset0_dl_bwp` | C | TS 38.213 CORESET#0 [Needs Verification] | 驗證 RedCap DL BWP 與 CORESET#0 相容性。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c` |
| `nr_redcap_apply_case_b_common_coreset` | C | TS 38.213 Case B CORESET#0 [Needs Verification] | 將 common CORESET 套入 RedCap Case B。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c` |
| `nr_redcap_rach_feature_partition_exists` | C | TS 38.321 RA / TS 38.331 RACH [Needs Verification] | 檢查 RACH 是否有 RedCap feature preambles。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c` |
| `nr_redcap_is_msg1_preamble` | C | TS 38.321 random access [Needs Verification] | 判斷 Msg1 preamble 是否屬 RedCap 分區。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c` |
| `nr_redcap_configure_rach_feature_combination_preambles` | C | TS 38.321 RA [Needs Verification] | 配置 RedCap RACH feature-combination preambles。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c` |
| `apply_redcap_case_b_common_coreset` | C | TS 38.213 Case B CORESET#0 [Needs Verification] | 依 SCC 與 config 套用 Case B common CORESET。 | `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` |
| `clone_redcap_downlink_bwp` | C | TS 38.331 `initialDownlinkBWP-RedCap-r17` [Needs Verification] | 複製並建立 SIB1 RedCap DL BWP。 | `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` |
| `clone_redcap_uplink_bwp` | C | TS 38.331 `initialUplinkBWP-RedCap-r17` [Needs Verification] | 複製並建立 SIB1 RedCap UL BWP。 | `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` |
| `fill_redcap_sib1` | C | TS 38.331 SIB1-v1700 RedCap IE [Needs Verification] | 填入 SIB1 RedCap barring/HD-FDD/reselection IE。 | `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` |
| `nr_redcap_configure_runtime_scc` | C | TS 38.331 ServingCellConfigCommon [Needs Verification] | 將 RedCap config 套進 runtime SCC。 | `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` |
| `configure_redcap_msg2_bwp` | C | TS 38.321 Msg2 / TS 38.213 PDCCH [Needs Verification] | RedCap RA Msg2 前切換 BWP/CORESET 視圖。 | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c` |
| `get_redcap_msg1_rach_config` | C | TS 38.321 random access [Needs Verification] | 取得 RedCap Msg1 判斷用 RACH config。 | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c` |
| `nr_redcap_sdt_get_log_stream` | C | TS 38.321 SDT [Needs Verification] | 取得 RedCap SDT transition log stream。 | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c` |
| `nr_redcap_sdt_enabled` | C | TS 38.321 SDT [Needs Verification] | 判斷 UE 是否啟用 RedCap SDT hooks。 | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c` |
| `nr_redcap_sdt_log_transition` | C | TS 38.321 SDT [Needs Verification] | 寫入 RedCap SDT FSM transition log。 | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c` |
| `nr_redcap_sdt_note_ul_grant` | C | TS 38.321 SDT [Needs Verification] | UL grant 發生時推進 SDT FSM。 | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c` |
| `nr_redcap_sdt_maybe_complete_ul_burst` | C | TS 38.321 SDT [Needs Verification] | UL burst 結束時完成 SDT FSM 狀態。 | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c` |
| `nr_redcap_sdt_fsm_init` | C | TS 38.321 SDT [Needs Verification] | 初始化 RedCap SDT FSM。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c` |
| `nr_redcap_sdt_fsm_step` | C | TS 38.321 SDT [Needs Verification] | 執行 RedCap SDT FSM 單步轉移。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c` |
| `nr_redcap_sdt_start_ul_burst` | C | TS 38.321 SDT [Needs Verification] | 啟動 RedCap SDT UL burst 流程。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c` |
| `nr_redcap_sdt_complete_ul_burst` | C | TS 38.321 SDT [Needs Verification] | 完成 RedCap SDT UL burst。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c` |
| `nr_redcap_sdt_state_to_string` | C | TS 38.321 SDT [Needs Verification] | 將 SDT state 轉成字串。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c` |
| `nr_redcap_sdt_path_to_string` | C | TS 38.321 SDT [Needs Verification] | 將 SDT path 轉成字串。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c` |
| `nr_redcap_sdt_event_to_string` | C | TS 38.321 SDT [Needs Verification] | 將 SDT event 轉成字串。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c` |
| `nr_redcap_sdt_transition_fprintf` | C | TS 38.321 SDT [Needs Verification] | 將 SDT transition 輸出成 log 行。 | `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c` |
| `use_sib1_redcap_initial_bwp` | C | TS 38.331 SIB1 RedCap BWP [Needs Verification] | UE 端判斷是否使用 SIB1 RedCap BWP。 | `openair2/LAYER2/NR_MAC_UE/config_ue.c` |
| `nr_ue_get_sib1_initial_dl_bwp` | C | TS 38.331 `initialDownlinkBWP-RedCap-r17` [Needs Verification] | UE 端選取 RedCap DL initial BWP。 | `openair2/LAYER2/NR_MAC_UE/nr_ue_redcap_bwp.c` |
| `nr_ue_get_sib1_initial_ul_bwp` | C | TS 38.331 `initialUplinkBWP-RedCap-r17` [Needs Verification] | UE 端選取 RedCap UL initial BWP。 | `openair2/LAYER2/NR_MAC_UE/nr_ue_redcap_bwp.c` |
| `is_redcap_ue_configured` | C | TS 38.306 UE capability [Needs Verification] | UE RA 流程判斷本機是否為 RedCap。 | `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c` |
| `use_redcap_msg3_ccch_lcid` | C | TS 38.321 CCCH LCID [Needs Verification] | 判斷 Msg3 是否使用 RedCap CCCH LCID。 | `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c` |
| `get_redcap_feature_preamble_partition` | C | TS 38.321 RA feature preamble [Needs Verification] | UE 端取得 RedCap preamble partition。 | `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c` |
| `nr_redcap_rrc_state_from_mac_state` | C | TS 38.331 RRC state [Needs Verification] | 將 MAC UE state 映射為 RedCap RRC state。 | `openair2/LAYER2/NR_MAC_UE/mac_defs.h` |

## L3 RRC / UICC / Bearer
| 函式名稱 | 使用語言 | 對應規範 | 50 字內用途 | 檔案 |
|---|---|---|---|---|
| `load_nr_redcap_config` | C | TS 38.306 UE capability [Needs Verification] | 從 `nrue_recap` YAML 載入 RedCap UE 能力。 | `openair3/UICC/nr_redcap_config.c` |
| `set_optional_enum_supported` | C | TS 38.331 UE capability IE [Needs Verification] | 建立 RedCap capability optional enum 欄位。 | `openair2/RRC/NR_UE/rrc_ue_redcap.c` |
| `nr_rrc_build_redcap_ue_capability` | C | TS 38.306 / TS 38.331 UE capability [Needs Verification] | 建立最小 RedCap UE capability container。 | `openair2/RRC/NR_UE/rrc_ue_redcap.c` |
| `nr_rrc_parse_redcap_sib1` | C | TS 38.331 SIB1-v1700 [Needs Verification] | 從 SIB1-v1700 取出 RedCap common config。 | `openair2/RRC/NR_UE/rrc_ue_redcap.c` |
| `nr_rrc_redcap_sib1_access_allowed` | C | TS 38.331 cell barring [Needs Verification] | 依 1Rx/2Rx/HD-FDD 判斷 RedCap 是否可駐留。 | `openair2/RRC/NR_UE/rrc_ue_redcap.c` |
| `get_redcapparam_r17` | C | TS 38.306 RedCapParameters-r17 [Needs Verification] | 從 UE capability 找出 RedCapParameters-r17。 | `openair2/RRC/NR/rrc_gNB.c` |
| `set_bearer_context_pdcp_config` | C | TS 38.331 PDCP config [Needs Verification] | RedCap 未支援 long SN 時強制 PDCP 12-bit。 | `openair2/RRC/NR/rrc_gNB_radio_bearers.c` |
| `fill_e1_drb_to_setup` | C | TS 38.463 / TS 38.331 [Needs Verification] | 將 RedCap PDCP 設定帶入 E1 DRB setup。 | `openair2/RRC/NR/rrc_gNB_NGAP.c` |
| `handle_ueCapabilityInformation` | C | TS 38.331 UECapabilityInformation [Needs Verification] | gNB 接收 UE capability 後保存 RedCap flags。 | `openair2/RRC/NR/rrc_gNB.c` |
| `rrc_delete_ue_data` | C | TS 38.331 UE context lifecycle [Needs Verification] | 釋放 UE context 時清除 RedCap capability。 | `openair2/RRC/NR/rrc_gNB.c` |

## O-RAN / xApp Control Interface
| 函式名稱 | 使用語言 | 對應規範 | 50 字內用途 | 檔案 |
|---|---|---|---|---|
| `nr_redcap_extract_int_ran_param` | C | O-RAN E2SM-RC [Needs Verification] | 從 RC RAN parameter 取出整數值。 | `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc_redcap.c` |
| `nr_redcap_parse_ul_prb_ctrl_message` | C | O-RAN E2SM-RC [Needs Verification] | 解析 RedCap UL PRB cap control message。 | `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc_redcap.c` |
| `apply_redcap_ul_prb_control` | C | O-RAN E2SM-RC / MAC scheduler local rule | 將 xApp UL PRB cap 寫入 gNB UE context。 | `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c` |
| `make_redcap_ul_prb_ctrl_req` | C | O-RAN E2SM-RC [Needs Verification] | xApp 端組出 RedCap UL PRB cap request。 | `ci-scripts/redcap_ul_prb_ctrl_xapp.c` |

## 查詢建議
- 要看呼叫來源：`symdex get_callers <function>`。
- 要看會呼叫誰：`symdex get_callees <function>`。
- 要改 runtime 行為：先看 L2 MAC / Scheduler。
- 要改 UE 能力宣告：先看 L3 RRC / UICC。
- 要改 RF/BWP 上限：先看 L1 PHY 與 L2 BWP helper。
