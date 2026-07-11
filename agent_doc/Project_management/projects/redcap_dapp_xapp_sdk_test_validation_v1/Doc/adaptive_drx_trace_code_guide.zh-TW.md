# Adaptive C-DRX Trace Code 指南

## 1. 使用方式

請以同一個 `policy_version`，從 generated trace 一路追到 checker。每個步驟
都先確認表格中的 input、output 與 marker，再前往下一個 source location。
Runtime `policy_version` 是 FlexRIC RIC request ID，不一定等於 predictor 原先
規劃的 window number。

## 2. End-to-End Source Route

| 步驟 | Source 與 symbol | Input | Output | 預期 marker | 下一個 trace point |
|---:|---|---|---|---|---|
| 1 | [`adaptive_drx.py:92`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L92)，`_stable_direction_seed()` | Trace seed、DL/UL direction | 穩定且依方向區分的 seed | 無 | `generate_intervals()` |
| 2 | [`adaptive_drx.py:105`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L105)，`generate_intervals()` | Stable seed、十一個 window means | 330 筆有界 inter-arrival values | 無 | `write_trace()` |
| 3 | [`adaptive_drx.py:119`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L119)，`write_trace()` | Intervals 與 start epoch | 由方向擁有 timestamp 的 trace CSV | 無 | `write_campaign_manifest()` |
| 4 | [`adaptive_drx.py:162`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L162)，`write_campaign_manifest()` | Trace/profile seeds | 四組 campaign records、checksums 與 profiles | 無 | `load_campaign()` |
| 5 | [`run_campaign.py:53`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L53)，`load_campaign()` | Manifest 與 campaign ID | 已驗證 campaign 與 330 rows | 證據無效時 BLOCKED/exception | Main campaign loop |
| 6 | [`run_campaign.py:31`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L31)，`iperf_command()` | Trace row 與 server address | Fixed-byte UDP command；DL 加上 `-R` | 無 | `subprocess.run()` |
| 7 | [`adaptive_drx.py:306`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L306)，`AdaptiveDrxPredictor.observe()` | Burst 後的一筆 `interval_us` | 保留的 30-sample history | 無 | 下一 boundary 的 `propose()` |
| 8 | [`adaptive_drx.py:245`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L245)，`summarize_window()` | 剛好 30 筆 bounded intervals | Mean、sample sigma、+/-3 sigma、median、p95、min/max | 無 | `select_profile()` |
| 9 | [`adaptive_drx.py:266`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L266)，`select_profile()` | `lower_3sigma_us` | 不大於 lower bound 的最大 approved cycle，否則 fallback | 無 | `AdaptiveDrxPredictor.propose()` |
| 10 | [`adaptive_drx.py:313`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L313)，`propose()` | Campaign/window IDs、UE identity、previous profile | 本地 `PolicyIntent` 與 JSON request description | 僅為 JSON `[xApp request]` label | Runner control branch |
| 11 | [`run_campaign.py:193`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L193)，window-control branch | Policy intent 或 seeded Arm A profile | 下一個 30 scored arrivals 使用的 profile | 無 | Local telnet 或 SWIG |
| 12A | [`run_campaign.py:91`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L91)，`_send_local_drx_policy()` | Arm A version、C-RNTI、完整 profile | Local telnet 的 `ci trigger_drx_policy ...` | gNB staged/applied | 步驟 20 |
| 12B | [`run_campaign.py:226`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L226)，`ric.control_drx_sm()` | Arm B node、RRC UE ID、long cycle | FlexRIC 產生的 RIC request ID | Caller 無 marker | SWIG wrapper |
| 13 | [`swig_wrapper.cpp:459`](../../../../../openair2/E2AP/flexric/src/xApp/swig/swig_wrapper.cpp#L459)，`control_drx_sm()` | E2 node、`rrc_ue_id`、cycle | 同步 RC control 與回傳 request ID | Generic FlexRIC response | C xApp request builder |
| 14 | [`redcap_xapp_sdk.c:86`](../../../../../openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.c#L86)，`redcap_xapp_make_drx_ctrl_req()` | RRC UE ID 與 approved cycle | RC Format 1 header/message、Style 2、Action 1、Parameter 1 | 無 | `control_sm_xapp_api()` |
| 15 | [`msg_handler_agent.c:272`](../../../../../openair2/E2AP/flexric/src/agent/msg_handler_agent.c#L272)，`e2ap_handle_control_request_agent()` | E2 control request | Request ID 與 encoded RC buffers 傳入 service model | Generic E2 control acknowledge | `on_control_rc_sm_ag()` |
| 16 | [`rc_sm_agent.c:133`](../../../../../openair2/E2AP/flexric/src/sm/rc_sm/rc_sm_agent.c#L133)，`on_control_rc_sm_ag()` | Request ID 與 RC buffers | Decoded `rc_ctrl_req_data_t` | 無 | `write_ctrl_rc_sm()` |
| 17 | [`ran_func_rc.c:1070`](../../../../../openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c#L1070)，`write_ctrl_rc_sm()` | Decoded RC request | Style/action dispatch 與 cycle decode | `[xApp request]`，接著 `[E2 ACK]` | `apply_redcap_drx_control()` |
| 18 | [`ran_func_rc_redcap.c:51`](../../../../../openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc_redcap.c#L51)，`nr_redcap_parse_drx_ctrl_message()` | RC Format 1 header/message | `rrc_ue_id` 與 approved `long_cycle_ms` | Decode 失敗為 dApp REJECT | gNB UE lookup |
| 19 | [`ran_func_rc.c:89`](../../../../../openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c#L89)，`find_redcap_ue_by_rrc_id()` | RRC UE ID | `NR_UE_info_t` 與權威 C-RNTI | 無法解析時 dApp REJECT | Guard snapshot |
| 20 | [`ran_func_rc.c:99`](../../../../../openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c#L99)，`apply_redcap_drx_control()` | Cycle、RIC request ID、UE state | Narrow dApp request 與 accepted gNB profile | `[dApp ACCEPT]` 或 `[dApp REJECT]` | `nr_mac_apply_drx_policy()` |
| 21 | [`redcap_dapp_sdk.c:311`](../../../../../openair2/E3AP/sdk/redcap_dapp_sdk.c#L311)，`redcap_dapp_guard_e2_drx_cycle()` | C-RNTI、version、cycle、connected/cooldown/current state | Approved cycle/On Duration pair、offset 0、inactivity 20 | Marker 回傳步驟 20 | gNB profile conversion |
| 22 | [`gNB_scheduler_primitives.c:4150`](../../../../../openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c#L4150)，`nr_mac_apply_drx_policy()` | C-RNTI 與 `nr_gnb_drx_profile_t` | Locked target UE 與 reconfiguration attempt | Unknown UE 時 gNB reject | `trigger_drx_reconfiguration()` |
| 23 | [`gNB_scheduler_primitives.c:4092`](../../../../../openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c#L4092)，`trigger_drx_reconfiguration()` | Current CellGroup 與 accepted profile | Encoded candidate、staged state、DU-to-CU RRC information | `[gNB staged]` 或 `[gNB reject]` | RRC delivery |
| 24 | [`nr_radio_config.c:4267`](../../../../../openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c#L4267)，`update_cellGroupConfig_for_drx()` | Current CellGroup 與 profile | 固定 inactivity/HARQ/short-DRX 值的 RRC DRX setup | 無 | UE RRC decoder |
| 25 | [`rrc_UE.c:1022`](../../../../../openair2/RRC/NR_UE/rrc_UE.c#L1022)，`nr_rrc_ue_process_masterCellGroup()` | Encoded master CellGroup | Decoded CellGroup 排入 UE MAC | CellGroup debug markers | `nr_rrc_mac_config_req_cg()` |
| 26 | [`config_ue.c:3288`](../../../../../openair2/LAYER2/NR_MAC_UE/config_ue.c#L3288)，`nr_rrc_mac_config_req_cg()` | Decoded CellGroup | MAC CellGroup applied | Applying CellGroupConfig | `configure_drx()` |
| 27 | [`config_ue.c:2647`](../../../../../openair2/LAYER2/NR_MAC_UE/config_ue.c#L2647)，`configure_drx()` | RRC `DRX-Config` 與 SCS | Slot-based `nr_drx_config_t` | `Configured Connected DRX` | UE Active Time |
| 28 | [`nr_ue_drx.c:111`](../../../../../openair2/LAYER2/NR_MAC_UE/nr_ue_drx.c#L111)，`nr_ue_drx_is_active_slot()` | Slot、SR、inactivity 與 HARQ timers | Active/sleep decision | 無 | UE PDCCH gate |
| 29 | [`nr_ue_scheduler.c:1169`](../../../../../openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c#L1169)，`nr_ue_dl_scheduler()` | UE state 與 current slot | 只在 Active Time 設定 DCI monitoring | 無 | Assignment event hooks |
| 30 | [`nr_ue_drx.c:173`](../../../../../openair2/LAYER2/NR_MAC_UE/nr_ue_drx.c#L173)，assignment/HARQ hooks | New DL/UL grants 與 HARQ outcomes | Inactivity 與 retransmission deadlines | 無 | 下一次 Active-Time evaluation |
| 31 | [`nr_mac_drx.c:62`](../../../../../openair2/LAYER2/NR_MAC_gNB/nr_mac_drx.c#L62)，stage/commit/complete state | Profile 與 RRC outcomes | `pending -> applied`、保存 `previous`、清除 cooldown | `[gNB applied]` | RRC completion |
| 32 | [`rrc_gNB.c:1973`](../../../../../openair2/RRC/NR/rrc_gNB.c#L1973)，`handle_rrcReconfigurationComplete()` | UE RRC complete | F1 success indication 傳回 DU | `Received RRCReconfigurationComplete` | DU completion handler |
| 33 | [`mac_rrc_dl_handler.c:767`](../../../../../openair2/LAYER2/NR_MAC_gNB/mac_rrc_dl_handler.c#L767)，completion branch | F1 success/failure | Commit completion 或自動還原 | `[RRC complete]`，可能有 `[rollback]` | Runner commit wait |
| 34 | [`run_campaign.py:73`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L73)，`_wait_for_commit()` | Runtime log 與 request ID | 只有完整 versioned marker chain 才成功 | Expire 時 `[control timeout]` | `predictor.resolve()` |
| 35 | [`run_campaign.py:241`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L241)，resolve/record branch | Commit result | 成功清 sample；失敗保留；寫 JSONL/CSV | PASS/PARTIAL | Checker |
| 36 | [`check_campaign.py:43`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/check_campaign.py#L43)，`check()` | Manifest、metrics CSV、runtime logs | Population、version、profile 與 marker issues | PASS 或 PARTIAL | Gate report |

## 3. 成功 Marker 順序

Arm B 必須以相同 `policy_version`，依序在 combined runtime log 找到：

1. `[RedCap DRX][xApp request]`
2. `[RedCap DRX][E2 ACK]`
3. `[RedCap DRX][dApp ACCEPT]`
4. `[RedCap DRX][gNB staged]`（diagnostic，checker 不要求）
5. `[RedCap DRX][gNB applied]`，並符合預期 `cycle_ms` 與 `on_duration_ms`
6. `Configured Connected DRX`（UE marker，沒有 version）
7. `Received RRCReconfigurationComplete`（一般 gNB RRC marker，沒有 version）
8. `[RedCap DRX][RRC complete] ... outcome success`

只有 E2 ACK 不代表 commit。Runner 必須確認步驟 1-3、5 與 8 都依 runtime
request ID correlate，才會清除 predictor window。

## 4. Failure 與 Rollback Route

| 條件 | Source | State action | 證據 |
|---|---|---|---|
| Decode/guard reject | `ran_func_rc.c` / `redcap_dapp_sdk.c` | 不進行 gNB staging | 含 reason 的 dApp REJECT；稍後 control timeout |
| Candidate encode/stage failure | `gNB_scheduler_primitives.c` | 釋放 candidate；applied profile 不變 | gNB reject 或 dApp REJECT `gnb_apply_failed` |
| Commit 前 RRC failure | `nr_mac_drx_fail_reconfiguration()` | 取消 pending candidate | Rollback 與 RRC failure markers |
| Commit 後 RRC failure | `mac_rrc_dl_handler.c` | 還原 `previous` profile 與 CellGroup | `[rollback]` 加 versioned failure |
| 缺少 completion marker | `run_campaign._wait_for_commit()` | Predictor 保留 30 筆 samples | `[control timeout]`、PARTIAL |

[`gNB_scheduler_primitives.c:4164`](../../../../../openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c#L4164)
的 `nr_mac_rollback_drx_policy()` 可以用新 version stage 已保存 profile，但目前
沒有 live dApp/E2 caller。

## 5. Optional DRX Command Route

此路徑與 DRX reconfiguration 分離，且兩種 live dApp guard 都會停用它。

1. [`nr_mac_request_drx_command()`](../../../../../openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c#L4187) 建立一次性 request，輸出 `[DRX Command requested]`。
2. [`nr_gnb_drx_note_dl_ack()`](../../../../../openair2/LAYER2/NR_MAC_gNB/nr_mac_drx.c#L190) 只在 DL HARQ ACK 成功且仍處於 Active Time 時 arm request。
3. [`nr_gnb_drx_command_ready()`](../../../../../openair2/LAYER2/NR_MAC_gNB/nr_mac_drx.c#L262) 要求沒有 pending SR、沒有 retransmission work、queue 為空、RRC config 已完成，且仍在 Active Time。
4. [`post_process_dlsch()`](../../../../../openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c#L1088) 寫入 zero-length DL MAC CE，輸出 `[DRX Command]`。
5. [`nr_ue_process_mac_pdu()`](../../../../../openair2/LAYER2/NR_MAC_UE/nr_ue_procedures.c#L4110) 辨識 DRX/Long DRX LCID，並呼叫 `nr_ue_drx_on_command()`。
6. [`nr_ue_drx_on_command()`](../../../../../openair2/LAYER2/NR_MAC_UE/nr_ue_drx.c#L245) 結束目前 active deadline，選擇下一個 short/long-cycle transition。

此 command 不會變更 long cycle、On Duration 或 RRC configuration。

## 6. 停止點與 `[Needs Verification]`

- 如果 fallback baseline 尚未安裝到 gNB，請停止宣告 live Arm B pass；manifest
  `initial_profile` 只存在 Python 本地。
- 將 `PolicyIntent.rnti` 視為名稱不正確的 RRC UE correlation value。請繼續
  追到 `find_redcap_ue_by_rrc_id()`，才取得權威 C-RNTI。
- 不要在 E2 packet 內尋找 prediction statistics；它們只存在 JSON。
- 不要宣告已強制執行 upper-bound fallback；live selection 只使用
  `lower_3sigma_us`。
- 不要宣告已完成 predicted start-offset alignment；live E2 guard 使用零。
- 不可從目前 CSV 推論 latency、goodput、loss、HARQ 或 monitoring-time
  metrics；程式尚未產生這些欄位。
- TS 38.473 integer mapping 必須維持 `[Needs Verification]`。

