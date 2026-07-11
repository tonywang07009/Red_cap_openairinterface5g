# Adaptive C-DRX API 與控制合約

## 1. 範圍與宣告邊界

本文件說明 v1 adaptive C-DRX 對單一 RRC_CONNECTED RedCap UE 的實作合約，
涵蓋可重現流量輸入、Python predictor、FlexRIC E2SM-RC request、process 內的
C dApp guard、gNB RRC/MAC 狀態、UE MAC 執行，以及 campaign 證據。

實際執行路徑為：

`Python campaign/xApp -> FlexRIC SWIG -> E2SM-RC -> gNB E2 agent -> process 內 C dApp guard -> gNB RRC/MAC -> UE MAC`

此路徑沒有 E3 transport。RFsim 只能支援 DRX 活動與延遲 proxy，不能證明 UE
實體硬體耗電。

## 2. 擁有者與資料方向

| 邊界 | 擁有者 | 方向 | 權限 |
|---|---|---|---|
| Trace 與 manifest | Campaign generator | 檔案 -> runner | 定義可重播的到達母體與 Arm A schedule |
| Window 統計與 intent | Python predictor | Runner 本地 | 提議 profile，不能套用無線電設定 |
| E2 request ID | FlexRIC | xApp -> E2 node | Runtime correlation key 與實際 `policy_version` |
| RC decode | gNB E2 agent | E2 -> 本地 C | 驗證 wire format 與 long-cycle 合法值 |
| DRX 安全決策 | Process 內 C dApp guard | 本地 C -> gNB MAC | 最終本地 accept/reject 邊界 |
| DRX 設定 | gNB | gNB -> UE，透過 RRC | 擁有 RRC `DRX-Config` 設定權 |
| DRX 執行 | UE MAC | UE 本地狀態 | 依 timer 與 event 決定 PDCCH monitoring |
| 證據判定 | Campaign checker | CSV/log -> 結果 | 回報 PASS、PARTIAL、BLOCKED 或無效證據 |

## 3. 可重現輸入合約

來源：[`adaptive_drx.py`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L18)，symbols `write_trace()` 與 `write_campaign_manifest()`。

### 3.1 凍結常數

| 欄位 | 值 | 驗證規則 |
|---|---:|---|
| `schema_version` | `1` | 本地 policy record 必須使用此版本 |
| `arrivals_per_campaign` | `330` | `read_trace()` 拒絕其他筆數 |
| `warmup_arrivals` | `30` | 不計分，用於訓練第一個 policy |
| `scored_arrivals` | `300` | Checker 要求 300 筆不重複 scored rows |
| `arrivals_per_window` | `30` | Predictor 拒絕不足或超過 30 筆的 window |
| `minimum_interval_us` | `300000` | Generator 會 clamp，predictor 會驗證 |
| `maximum_interval_us` | `10240000` | Generator 會 clamp，predictor 會驗證 |
| `control_service_style_id` | `2` | RC decoder 要求 Style 2 |
| `control_action_id` | `1` | RC decoder 要求 Action 1 |
| `long_cycle_parameter_id` | `1` | RC decoder 要求唯一 Parameter 1 |

### 3.2 Trace CSV 欄位

方向：generator -> campaign runner 與 checker。

| 欄位 | 擁有者與意義 | 驗證 / rollback | Marker |
|---|---|---|---|
| `arrival_id` | Generator；一基底 ID `1..330` | Checker 要求 scored rows ID 不重複 | 無 |
| `window_id` | Generator；零基底 30-arrival source window | 僅供資訊；scored policy window 在其他位置為一基底 | 無 |
| `phase` | Generator；`warmup` 或 `scored` | 第 1-30 筆為 warm-up | 無 |
| `scored_arrival_id` | Generator；warm-up 為空，其後為 `1..300` | 僅供資訊 | 無 |
| `direction` | Generator；`downlink` 或 `uplink` | Runner 拒絕與 campaign 不符的 trace | 無 |
| `traffic_source` | Generator；DL 為 `iperf_server`，UL 為 `redcap_ue` | 說明 timestamp 擁有者 | 無 |
| `interval_us` | Generator；inter-arrival 時間 | 必須位於 300 ms..10.24 s | 無 |
| `scheduled_source_tx_time_us` | Generator；累積 source schedule | Checker 要求與 metrics CSV 完全相等 | 無 |

Manifest 會保存 trace `path`、`sha256`、`trace_seed` 與 `start_epoch_us`。
`load_campaign()` 會拒絕 checksum 或 direction 不一致的輸入。

### 3.3 Manifest 欄位

| 欄位群組 | 欄位 | 擁有者 / 規則 |
|---|---|---|
| Top level | `schema_version`、`experiment`、`trace_seed`、`arm_a_profile_seed`、`claim_boundary` | Generator；保存重現條件與 RFsim-only 宣告邊界 |
| Population | `arrivals_per_campaign`、`warmup_arrivals`、`scored_arrivals`、`arrivals_per_window`、`minimum_interval_us`、`maximum_interval_us` | 凍結的 v1 實驗形狀 |
| Traffic | `tool`、`transport`、`bytes_per_burst`、`payload_bytes`、`target_bitrate_bps`、`schedule_option`、`latency_option` | 固定 iPerf2 UDP burst 合約 |
| Campaign | `id`、`arm`、`direction`、`trace`、`control_mode`、`required_markers` | 選擇 Arm A/B 與 DL/UL |
| Arm A | `profile_schedule[]`：`scored_window_id`、`profile_id`、`long_cycle_ms`、`on_duration_ms` | 固定 seed 的本地 RRC schedule |
| Arm B | `initial_profile`：`profile_id`、`long_cycle_ms`、`on_duration_ms` | 只初始化 runner 本地 label；請見 baseline 缺口 |
| Profiles | `approved_profiles[]`：`profile_id`、`long_cycle_ms`、`on_duration_ms` | 六組 v1 合法 profile pair |

## 4. Python Predictor 與本地 Policy Record

來源：[`adaptive_drx.py`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py#L34)。

### 4.1 `DrxProfile`

| 欄位 | 意義 | 驗證規則 |
|---|---|---|
| `profile_id` | 穩定的本地 profile 名稱 | 必須是六組 approved profile 之一 |
| `long_cycle_ms` | 候選 long DRX cycle | `320`、`640`、`1280`、`2560`、`5120` 或 `10240` |
| `on_duration_ms` | 本地配對的 On Duration | `10`、`20` 或 `40`，由 profile table 固定 |

### 4.2 `WindowStatistics`

所有欄位都是 Python 本地 JSON 證據，不會透過 E2 編碼。

| 欄位 | 意義 | 驗證規則 |
|---|---|---|
| `sample_count` | 已 commit 的 interval 數量 | 必須為 `30` |
| `mean_interval_us` | 算術平均數 | `statistics.fmean()` |
| `stddev_interval_us` | 樣本標準差 | `statistics.stdev()` |
| `lower_3sigma_us` | 平均數減三倍標準差 | 用於選擇 profile |
| `upper_3sigma_us` | 平均數加三倍標準差 | 有記錄，但 live path 未強制檢查 |
| `median_interval_us` | 中位數 | 描述性證據 |
| `p95_interval_us` | Nearest-rank p95 | 排序後第 `ceil(0.95*N)-1` 個項目 |
| `minimum_interval_us` | 最小 sample | 描述性證據 |
| `maximum_interval_us` | 最大 sample | 描述性證據 |

### 4.3 `PolicyIntent`

方向：predictor -> command JSONL / 本地 correlation。只有 UE identity 與所選
long cycle 會進入實際 SWIG call。

| 欄位 | 擁有者與意義 | 驗證 / rollback |
|---|---|---|
| `schema_version` | Predictor；本地 schema `1` | Rich dApp guard 可驗證，但該 guard 不是 live path |
| `campaign_id` | Runner 選擇的 campaign | 必須符合 manifest |
| `direction` | `downlink` 或 `uplink` | Predictor 拒絕其他值 |
| `window_id` | 一基底 scored policy window | Runner 產生十個 window |
| `policy_version` | 本地規劃的 window version | Execute 時由 FlexRIC RIC request ID 取代 |
| `ric_request_id` | 本地規劃的 correlation value | Execute 時由 FlexRIC RIC request ID 取代 |
| `rnti` | 名稱不正確的本地 identity 欄位 | Arm B 放入 `--rrc-ue-id`，不是權威 C-RNTI `[Needs Verification]` |
| `sample_count` | 已 commit history 大小 | 固定 `30` |
| `prediction_status` | `predicted`、`fallback` 或 `zero_variance` | 記錄選擇結果 |
| `selected_profile_id` | 提議的 profile | 必須 approved |
| `previous_profile_id` | Runner 最後 commit 的 profile label | 必須 approved；不是 gNB state readback |
| `valid_for_arrivals` | 預測 horizon | 固定 `30` |
| `short_drx_enabled` | 本地 v1 常數 | `false` |
| `drx_inactivity_timer_ms` | 本地 v1 常數 | `20` |
| `drx_slot_offset_1_over_32_ms` | 本地 v1 常數 | `0` |
| Statistics 欄位 | 攤平的 `WindowStatistics` | Live path 僅存在 JSON |
| `e2sm_rc_request` | 供人閱讀的 request metadata | 不是傳給 FlexRIC 的 object |

`AdaptiveDrxPredictor.resolve(true)` 會清除 30 筆 samples。Reject 或 timeout
呼叫 `resolve(false)` 時，只移除 pending decision 並保留 sample window；runner
接著回傳 PARTIAL，不會繼續下一個 window。

## 5. E2SM-RC 與 SWIG 合約

來源：[`redcap_xapp_sdk.c`](../../../../../openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.c#L48)、[`swig_wrapper.cpp`](../../../../../openair2/E2AP/flexric/src/xApp/swig/swig_wrapper.cpp#L459) 與 [`ran_func_rc_redcap.c`](../../../../../openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc_redcap.c#L51)。

### 5.1 Live SWIG API

```c
uint32_t control_drx_sm(global_e2_node_id_t *id,
                        uint64_t rrc_ue_id,
                        uint16_t long_cycle_ms);
```

| 欄位 | 方向 | 驗證規則 | 回傳 / marker |
|---|---|---|---|
| `id` | Python -> SWIG | E2 node 不可為 null | 本地 request 建立失敗時回傳 `0` |
| `rrc_ue_id` | Python -> RC header | 正值；編碼為 GNB UE `ran_ue_id` | 在 gNB 解析為 C-RNTI |
| `long_cycle_ms` | Python -> RC Parameter 1 | 六種 approved cycle 之一 | E2 ACK 包含 decode 後的值 |
| 回傳值 | FlexRIC -> Python | Transport 成功時為產生的 RIC request ID | 否則為 `0` |

### 5.2 實際透過 E2 編碼的欄位

| RC 位置 | 欄位 | 必要值 |
|---|---|---|
| Header | `format` | `FORMAT_1_E2SM_RC_CTRL_HDR` |
| Header | `ue_id.type` | `GNB_UE_ID_E2SM`，或 decoder 支援的 `GNB_DU_UE_ID_E2SM` |
| Header | `ue_id.*.ran_ue_id` | 非 null、非零 RRC UE identity |
| Header | `ric_style_type` | `2` |
| Header | `ctrl_act_id` | `1` |
| Message | `format` | `FORMAT_1_E2SM_RC_CTRL_MSG` |
| Message | `sz_ran_param` | 必須剛好為 `1` |
| Parameter | `ran_param_id` | `1` |
| Parameter | value kind | Element-key true、integer RAN parameter |
| Parameter | integer value | Approved `long_cycle_ms` |

`policy_version`、prediction statistics、profile ID、On Duration、inactivity、
start offset 與 rollback data 都不是 E2 RAN parameter。FlexRIC 從一開始產生
RIC request ID，將其複製到 agent；live gNB path 使用該 ID 作為
`policy_version`。

`[RedCap DRX][xApp request]` 與 `[RedCap DRX][E2 ACK]` 都由 gNB RC handler
輸出。後者只證明 decode 被接受，不代表 dApp 或 RRC 已套用。

## 6. C dApp Guard 合約

來源：[`redcap_dapp_sdk.h`](../../../../../openair2/E3AP/sdk/redcap_dapp_sdk.h#L87) 與 [`redcap_dapp_sdk.c`](../../../../../openair2/E3AP/sdk/redcap_dapp_sdk.c#L202)。

### 6.1 Live Narrow E2 Request：`redcap_dapp_e2_drx_cycle_request_t`

Live RC path 會使用此 request 與目前已套用的設定呼叫 `redcap_dapp_guard_e2_drx_cycle()`。

| 欄位 | 擁有者 / 方向 | 驗證規則 |
|---|---|---|
| `rnti` | gNB lookup -> dApp | 非零且已解析的 C-RNTI |
| `policy_version` | FlexRIC RIC request ID -> dApp | 非零且比 current 更新 |
| `requested_long_cycle_ms` | E2 decode -> dApp | 必須映射到 approved profile |
| `ue_connected` | gNB state snapshot -> dApp | 必須為 true |
| `rrc_reconfiguration_cooldown_elapsed` | gNB state snapshot -> dApp | 不可有 pending CellGroup 或 RRC completion |

Guard 還要求 current profile 有效、`rollback_available=true`、C-RNTI 相符、
offset/profile pair 合法且 inactivity 為 20 ms。Accept 時會在本地選擇 On
Duration、使用 start offset 0、停用 short DRX 與 DRX Command，並回傳 dApp
ACCEPT。

### 6.2 Rich Local Request：`redcap_dapp_drx_policy_request_t`

`redcap_dapp_guard_drx_policy()` 有 C unit test，但沒有 live caller。

| 欄位 | 驗證規則 |
|---|---|
| `schema_version` | 必須等於 `REDCAP_DAPP_DRX_SCHEMA_VERSION` (`1`) |
| `rnti` | 非零且符合 rollback profile |
| `policy_version` | 必須比 current 更新 |
| `sample_count` | 必須剛好為 `30` |
| `lower_3sigma_us` | 至少 `300000`；選擇最大 eligible profile |
| `upper_3sigma_us` | 最多 `10240000`，且不可小於 lower bound |
| `next_arrival_drx_epoch_ms` | 對 long cycle 取餘數以產生 start offset |
| `requested_long_cycle_ms` | 必須等於 lower 3-sigma 規則所選 profile |
| `ue_connected` | 必須為 true |
| `rrc_reconfiguration_cooldown_elapsed` | 必須為 true |

### 6.3 Accepted Configuration 與 Guard Result

| Structure / 欄位 | 意義 | Rollback 行為 |
|---|---|---|
| `redcap_dapp_drx_config_t.rnti` | Target C-RNTI | 必須與已保存 current state 相符 |
| `.policy_version` | Accepted version | gNB 拒絕 stale staging |
| `.long_cycle_ms` | Approved cycle | 儲存在 gNB applied/previous state |
| `.on_duration_ms` | Approved local pair | 儲存在 gNB applied/previous state |
| `.start_offset_ms` | Cycle offset | Live E2 path 使用 `0` |
| `.inactivity_ms` | Inactivity timer | 固定 `20` |
| `.rollback_available` | Guard proof | Apply 前必要條件 |
| `.drx_command_enabled` | Optional CE feature flag | 兩種 dApp guard 都停用 |
| `.profile_id` | 本地 profile label | 不會複製到 gNB profile |
| `guard_result.decision` | ACK 或 NACK | 只有 ACK 可 apply |
| `guard_result.accepted` | Candidate configuration | 轉換成 `nr_gnb_drx_profile_t` |
| `guard_result.previous` | Guard 回傳的 snapshot | Caller 本身沒有持久化此欄位 |
| `guard_result.reason` | `ack` 或 reject reason | 輸出於 dApp marker |
| `guard_result.marker` | ACCEPT 或 REJECT marker | Runtime 證據 |

Decode、guard 與 apply 路徑實作的 reject reasons 包括
`e2_decode_error`、`unsupported_long_cycle`、`unknown_rnti`、
`ue_not_connected`、`stale_policy_version`、`cooldown_active`、
`rollback_unavailable`、`prediction_out_of_bounds`、`sample_count_not_30`、
`invalid_schema_version`、`unsupported_node_role` 與 `gnb_apply_failed`。

## 7. gNB RRC/MAC 與 UE MAC 合約

### 7.1 `nr_gnb_drx_profile_t`

來源：[`nr_mac_drx.h`](../../../../../openair2/LAYER2/NR_MAC_gNB/nr_mac_drx.h#L21)。

| 欄位 | 驗證規則 | RRC mapping |
|---|---|---|
| `policy_version` | 已 configured 時必須單調增加 | 只用於本地 correlation |
| `long_cycle_ms` | Approved pair | `drx-LongCycleStartOffset` choice |
| `on_duration_ms` | Approved pair | Integer-ms `drx-onDurationTimer` |
| `inactivity_ms` | 必須為 `20` | `drx-InactivityTimer=ms20` |
| `start_offset_ms` | 必須小於 long cycle | Long-cycle choice value |
| `drx_command_enabled` | 本地 feature flag | 不是 RRC field |

Producer 另固定 HARQ RTT DL/UL 為四個 symbols、retransmission DL/UL 為八個
slots、`shortDRX=NULL`、`drx-SlotOffset=0`；請見
[`update_cellGroupConfig_for_drx()`](../../../../../openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c#L4267)。

### 7.2 Apply 與 Rollback

1. `nr_mac_apply_drx_policy()` 驗證 profile 與 target UE。
2. `trigger_drx_reconfiguration()` clone 並 encode `CellGroupConfig`、stage
   profile、標記 RRC completion pending，並送出 DU-to-CU request。
3. RRC transport commit 成功時，將 `pending` 移至 `applied`，並把舊
   `applied` 保存為 `previous`。
4. RRC completion 清除 cooldown，並輸出 versioned success evidence。
5. Completion 失敗時，取消未 commit candidate 或還原已保存的 previous
   profile 與 CellGroup，再輸出 rollback 與 failure evidence。

自動 rollback 實作於
[`mac_rrc_dl_handler.c`](../../../../../openair2/LAYER2/NR_MAC_gNB/mac_rrc_dl_handler.c#L767)。
Explicit `nr_mac_rollback_drx_policy()` API 已存在，但目前沒有 caller。

### 7.3 UE 執行狀態

UE 將 RRC fields decode 成 `nr_drx_config_t`：On Duration、inactivity、HARQ
RTT 與 retransmission timers、long/short cycle、offsets、monotonic clock 與
每個 HARQ state。`nr_ue_drx_is_active_slot()` 在 pending SR、inactivity、
HARQ retransmission window 或 On Duration 時回傳 active。UE scheduler 只有在
active 時設定 DCI monitoring。DRX 與 Long DRX MAC CE 會停止目前 active
deadline，並選擇下一個 short/long-cycle transition。

## 8. Runtime 證據合約

來源：[`run_campaign.py`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/run_campaign.py#L176) 與 [`check_campaign.py`](../../../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/check_campaign.py#L17)。

### 8.1 Metrics CSV 欄位

| 欄位 | 意義 | Checker 規則 |
|---|---|---|
| `campaign_id` | 選擇的 campaign | 必須完全相符 |
| `arrival_id` | Trace row | 必須有 300 個不重複 scored IDs |
| `scheduled_source_tx_time_us` | Source schedule | 必須與 trace 完全相符 |
| `delivery_success` | iPerf process 成功回傳 | 依 truthy/falsey 計數 |
| `policy_version` | 已 commit 的 FlexRIC/local version | 十個 versions，每個 30 rows |
| `profile_id` | Runner 已 commit 的 profile label | 必須 approved，且每 window 唯一 |
| `client_launch_time_us` | Client process launch time | 有記錄，但 checker 未檢查 |
| `iperf_returncode` | Process return code | 有記錄，但未獨立檢查 |

Command JSONL 另記錄 `arm`、`direction`、`traffic_source`、完整 command、
`executed`、optional flattened control intent、`returncode`、`stdout` 與
`stderr`。

### 8.2 Runtime Markers

| Marker | Producer | 意義 / correlation |
|---|---|---|
| `[RedCap DRX][xApp request]` | gNB RC handler | Style/action 已辨識；有 version |
| `[RedCap DRX][E2 ACK]` | gNB RC handler | RC fields decode 成功；有 version |
| `[RedCap DRX][dApp ACCEPT]` | Process 內 guard caller | 本地 safety guard 通過；有 version |
| `[RedCap DRX][dApp REJECT]` | Decode/guard/apply path | 含 reason；部分早期格式沒有 version |
| `[RedCap DRX][gNB staged]` | gNB MAC | RRC candidate 已 encode 並 stage；有 version |
| `[RedCap DRX][gNB applied]` | gNB MAC | 已套用 cycle 與 On Duration；可依 version/profile 檢查 |
| `Configured Connected DRX` | UE MAC | UE 已 decode DRX config；沒有 version |
| `Received RRCReconfigurationComplete` | gNB RRC | CU 已收到 UE completion；沒有 version |
| `[RedCap DRX][RRC complete]` | gNB DU MAC | 有 version 的 success/failure commit marker |
| `[RedCap DRX][rollback]` | gNB MAC | 已還原 previous config，或 explicit rollback 已 stage |
| `[RedCap DRX][DRX Command requested]` | gNB local API | 已要求一次性 command |
| `[RedCap DRX][DRX Command]` | gNB scheduler | 已送出 zero-length MAC CE |
| `[RedCap DRX][control timeout]` | Runner/checker | 必要的 versioned marker chain 不完整 |

## 9. 必須保留的 `[Needs Verification]` 邊界

1. E2SM-RC Long DRX Cycle Length 所使用的 integer value，仍需核對 TS
   38.473 的精確 encoding。
2. Arm B manifest 的 `initial_profile` 只初始化 Python label。Runner 沒有
   在 gNB 安裝 baseline，但 live dApp guard 要求既有 rollback profile。
3. Arm B 的 `PolicyIntent.rnti` 實際包含 `rrc_ue_id`。權威 C-RNTI 只在 gNB
   內解析。
4. Statistics、prediction quality、profile IDs 與 planned version 只存在
   JSON。Live E2 path 呼叫 narrow cycle guard，而非 statistics-aware rich guard。
5. `select_profile()` 只使用 `lower_3sigma_us`；過大的 `upper_3sigma_us` 不會
   在 live E2 request 前強制 fallback。
6. Live E2 path 將 start offset 固定為零。Predicted-arrival/SFN alignment 尚未
   實作。
7. FlexRIC control ACK 不會回報 dApp outcome。Runtime commit 必須由完整
   marker chain 判斷。
8. Checker 會依 version correlate custom RRC marker，但 UE config 與一般 RRC
   completion string 只做全域存在檢查。
9. 目前 metrics 尚未量測 first-receive latency、goodput、UDP loss/jitter、
   HARQ retransmission，或 DRX monitoring/Active-Time ratio。
10. 已有自動 failure rollback，但沒有 dApp rollback-decision marker，也沒有
    `nr_mac_rollback_drx_policy()` 的 live caller。
