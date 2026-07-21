# RedCap 到 A-IoT／AIOTF 與 xApp/dApp 三週導讀課程

## 1. 課程定位

本課程供接手本 repository 的維護工程師使用。角色設定是售後服務工程師：先確認現象與證據層級，再沿 marker 找 owner，最後才判斷要修改哪一層。

| 項目 | 契約 |
|---|---|
| 時間 | 三週、15 個工作日；每天 60-90 分鐘 |
| 起點 | 已能讀 C、Markdown 與基本 NR 名詞，不要求先熟悉全部 OAI |
| 終點 | 能從 RedCap config 追到 Tag、UE Reader、RFsim、AIOTF、NRF/Naiotf，指出 AMF/RAN/NEF 的真實停止點，並能重用或最小擴充 xApp/dApp SDK 函式 |
| 預設操作 | 前兩週唯讀；`rg`、`sed`、函式與文件查詢 |
| 第三週操作 | 優先重用既有 SDK；需要新行為時只修改既有 SDK 與最近的 self-test，不新增平行模組 |
| 選修操作 | 使用既有 registry/menu/display；不刪 CN5G volume |
| GPT 5.6 Luna | 作為導讀者與理解檢查者；模型回答不算 source、build 或 runtime evidence |

先讀：

1. `AGENTS.md`
2. `redcap_doc/manuals/aiot_tag_aiotf_architecture.zh-TW.md`
3. `redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md`
4. `redcap_doc/specs/function_reference/aiot_tag_aiotf_function_trace.md`
5. `redcap_library/library_reports_summary/aiotf_cn5g_experimental_n6_validation_report.md`
6. `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/sdk_development_guide.zh-TW.md`

## 2. Luna 固定工作契約

每一天先把下列內容交給 GPT 5.6 Luna，再附上當日 prompt：

```text
你是本專案的售後服務導讀工程師。只根據我提供的 repository 檔案與可重現證據回答。

規則：
1. 先列出 source path、symbol、caller、callee、marker、status。
2. status 只能是 Public、Integrated、Runtime-evidenced、Experimental、Blocked 或 [Needs Verification]。
3. 找不到 owner 時明確說找不到，不補造函式、route、ASN.1 或 3GPP clause。
4. 不以 container healthy、NRF PASS、N6 UDP 或模型推論證明 AMF/NGAP/RRC/NEF 已完成。
5. 一次只教今天指定的路徑，最後出三題理解檢查；等我回答後再訂正。
6. 每一個行為結論都附 repository 相對路徑；規範結論不確定時標記 [Needs Verification]。
```

每次對話結束前，要求 Luna 產生：

```text
今日交接卡
- 我能解釋的資料流：
- 我找到的第一個 owner：
- 我找到的成功／失敗 marker：
- 我仍不能證明的部分：
- 明天應從哪個 caller 或 callee 繼續：
```

## 3. 實作檔地圖

### 3.1 RedCap 基線

| 層級 | 主要檔案 | 導讀重點 |
|---|---|---|
| L1 RF/grid | `openair1/PHY/INIT/nr_parms.c` | FR1 PRB 上限與 gNB/UE frame parameter 驗證 |
| gNB config | `openair2/GNB_APP/gnb_config.c` | RedCap common config、initial BWP、half-duplex 設定入口 |
| gNB BWP helpers | `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h`, `nr_mac_redcap_bwp.c` | BWP RIV、CORESET#0、RACH feature partition |
| gNB SIB1/runtime SCC | `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` | RedCap DL/UL BWP clone、SIB1-v1700、runtime SCC |
| gNB RA | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c` | RedCap Msg1 判斷與 Msg2 BWP/CORESET 視圖 |
| UE BWP/RA | `openair2/LAYER2/NR_MAC_UE/config_ue.c`, `nr_ue_redcap_bwp.c`, `nr_ra_procedures.c` | UE 選取 RedCap initial BWP、feature preamble 與 Msg3 LCID |
| UE DRX gate | `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c` | 產生 `ue_connected` 與 `connected_drx_active` 狀態 |
| UE RRC | `openair2/RRC/NR_UE/rrc_ue_redcap.c` | 建立 UE capability、解析 SIB1、判斷 cell access |
| gNB RRC | `openair2/RRC/NR/rrc_gNB.c`, `rrc_gNB_radio_bearers.c`, `rrc_gNB_NGAP.c` | 保存 RedCap capability 與受限 PDCP/bearer 設定 |
| UE YAML | `openair3/UICC/nr_redcap_config.c` | 從 `nrue_recap` 載入 RedCap capability |

### 3.2 A-IoT Topology 2 與 UE Reader

| 層級 | 主要檔案 | 導讀重點 |
|---|---|---|
| RF control contract | `radio/COMMON/common_lib.h` | RFsim A-IoT option bits、packet/report wire types |
| RFsim relay | `radio/rfsimulator/simulator.cpp`, `radio/rfsimulator/CMakeLists.txt` | peer role registration與 CW/R2D/D2R relay，不改正常 IQ path |
| Tag/CW executable | `radio/rfsimulator/stored_node.c` | Tag state、Manchester/SFS、CRC、fault/self-test、RFsim client modes |
| UE codec API | `openair1/PHY/NR_UE_TRANSPORT/nr_transport_proto_ue.h`, `nr_ue_rf_helpers.c` | R2D encode、D2R decode、CRC 驗證 |
| UE shared state | `openair1/PHY/defs_nr_UE.h`, `openair2/NR_UE_PHY_INTERFACE/NR_IF_Module.h` | report socket與 MAC→PHY connected/DRX state |
| UE arguments | `executables/nr-uesoftmodem.c`, `nr-uesoftmodem.h` | reader/observer、Tag、window、handle、report endpoint 參數 |
| UE Reader loop | `executables/nr-ue.c` | awake gate、R2D/D2R、40-byte report、slot loop apply point |

### 3.3 AIOTF、CN5G 與操作面

| 層級 | 主要檔案 | 導讀重點 |
|---|---|---|
| AIOTF state | `openair3/AIOTF/aiotf_inventory.h`, `aiotf_inventory.c` | 60-Tag binding、reader selection、serialization、failover、arbitration |
| AIOTF tests | `openair3/AIOTF/tests/test_aiotf_inventory.c` | 邊界、first-valid、duplicate/conflict、timeout、ambiguous context |
| AIOTF process | `openair3/AIOTF/aiotf_service.c` | config、liveness/readiness、N6 adapter、NRF client、Naiotf Inventory |
| Build owner | `openair3/AIOTF/CMakeLists.txt`, `openair3/CMakeLists.txt`, `docker/Dockerfile.build.ubuntu`, `docker/Dockerfile.gNB.ubuntu` | `oai-aiotf` build/runtime target |
| CN5G owner | `oai-cn5g/docker-compose.yaml` | disabled-by-default `aiot` profile與 `public_net`／`traffic_net` |
| Registry | `redcap_library/bash_tool/registry.json`, `redcap_library/bash_tool/scripts/aiot_registered_check.sh` | 唯一可重複驗證與 cleanup owner |
| Skill | `redcap_library/skills/tag_aiotf_workflow/SKILL.md` | 只組合 registry entries，不直接執行 shell |
| Menu/display | `mmtc.menu.bash`, `redcap_interface/mmtc.display.bash` | `aiot validate|start|status|down` 與 `aiot-t2` 展示 |

### 3.4 xApp/dApp SDK

| 層級 | 主要檔案 | 導讀重點 |
|---|---|---|
| xApp C SDK | `openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.h`, `redcap_xapp_sdk.c` | metric、priority hint、RC request builder |
| xApp Python parity helper | `openair2/E2AP/REDCAP_SDK/xapp/redcap_xapp_sdk.py` | 快速驗證 algorithm intent；不等同 SWIG runtime binding |
| dApp C SDK | `openair2/E3AP/sdk/redcap_dapp_sdk.h`, `redcap_dapp_sdk.c` | guard、PRB allocation、access-pressure policy、RA selector |
| dApp Python parity helper | `openair2/E3AP/sdk/redcap_dapp_sdk.py` | policy/selector parity 與邊界練習 |
| E2 apply path | `ci-scripts/redcap_ul_prb_ctrl_xapp.c`, `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c` | xApp request、ACK、gNB apply/reject boundary |
| Scheduler observation hooks | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_uci.c`, `gNB_scheduler_ulsch.c` | dApp decision marker；不預設已修改 allocation |
| Contract check | `agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/dapp_xapp_sdk_contract_selftest.py` | C/Python contract 與邊界的最小回歸檢查 |

詳細 signatures、callers、callees 與 markers 不在本課程重複維護；以兩份 canonical lookup 為準：

- RedCap：`redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md`
- A-IoT／AIOTF：`redcap_doc/specs/function_reference/aiot_tag_aiotf_function_trace.md`

## 4. 第一週：先理解 RedCap，再說明為什麼需要 Topology 2

### Day 1：建立證據層級與專案路由

| 欄位 | 內容 |
|---|---|
| 目標 | 分清 production RedCap、experimental RFsim、runtime-evidenced AIOTF dependency 與 blocked standard path |
| 檔案 | `AGENTS.md`, `redcap_doc/README.md`, `redcap_library/README.md`, A-IoT architecture/report |
| 函式 | 今天不進函式；先建立 owner 與 evidence 分類 |
| 預期結果 | 能說明為何「UDP 收到資料」不等於「AMF/Namf_AIoT 已完成」 |
| 停止條件 | 如果回答把 NRF、N6、container health 合併成端到端 PASS，回到 capability matrix 重讀 |
| 交付 | 一張四層 evidence 表與一條目前可跑、不可跑的 path |

唯讀練習：

```bash
sed -n '1,180p' redcap_doc/manuals/aiot_tag_aiotf_architecture.zh-TW.md
sed -n '1,120p' redcap_library/library_reports_summary/aiotf_cn5g_experimental_n6_validation_report.md
```

Luna prompt：

```text
依 Day 1 檔案，把所有 A-IoT gate 分成 Implemented、Runtime-evidenced、Experimental、Blocked。
特別反證：「AIOTF 與 AMF 已正常通訊」這句話目前為何不成立？
```

### Day 2：RedCap 設定如何進入 gNB 與 UE

| 欄位 | 內容 |
|---|---|
| 目標 | 追蹤 config/YAML 到 RedCap runtime capability 的第一段 |
| 檔案 | `openair3/UICC/nr_redcap_config.c`, `openair2/GNB_APP/gnb_config.c`, `openair1/PHY/INIT/nr_parms.c` |
| 函式 | `load_nr_redcap_config`, `get_redcap_config`, `get_redcap_initial_bwp_config`, `nr_validate_redcap_*_frame_parms` |
| 預期結果 | 能指出 gNB config、UE capability 與 L1 grid validation 是不同 owner |
| 停止條件 | 找不到 input field 時不猜名稱；回到 config parser 與 lookup |
| 交付 | `input -> parser -> runtime struct -> validator` 四欄圖 |

```bash
rg -n "load_nr_redcap_config|get_redcap_config|get_redcap_initial_bwp_config|nr_validate_redcap" \
  openair1/PHY/INIT/nr_parms.c openair2/GNB_APP/gnb_config.c openair3/UICC/nr_redcap_config.c
```

Luna prompt：

```text
只追 Day 2 的 config flow。對每個函式列 input、寫入的 state、直接 caller/callee 與拒絕條件。
不要提前解釋 BWP 排程或 A-IoT。
```

### Day 3：gNB RedCap BWP、CORESET#0 與 SIB1

| 欄位 | 內容 |
|---|---|
| 目標 | 理解 RedCap initial BWP 如何從 helper 進入 runtime SCC 與 SIB1 |
| 檔案 | `nr_mac_redcap.h`, `nr_mac_redcap_bwp.c`, `nr_radio_config.c` |
| 函式 | `nr_redcap_configure_initial_bwp`, `nr_redcap_validate_coreset0_dl_bwp`, `clone_redcap_*_bwp`, `fill_redcap_sib1`, `nr_redcap_configure_runtime_scc` |
| 預期結果 | 能區分計算/驗證 helper、ASN.1 clone/fill 與 apply point |
| 停止條件 | exact TS 38.331/38.213 clause 未在本地證據確認時標記 `[Needs Verification]` |
| 交付 | 一張 `config -> BWP helper -> SCC/SIB1` 流程圖 |

```bash
rg -n "nr_redcap_configure_initial_bwp|nr_redcap_validate_coreset0_dl_bwp|clone_redcap_.*bwp|fill_redcap_sib1|nr_redcap_configure_runtime_scc" \
  openair2/LAYER2/NR_MAC_gNB
```

Luna prompt：

```text
解釋 Day 3 五組函式的責任分界。用 boundary-1、boundary、boundary+1 說明 BWP/CORESET 檢查應如何閱讀；
沒有現成 test 證據的案例標記 [Needs Verification]。
```

### Day 4：Random Access 與 UE 端 BWP 選擇

| 欄位 | 內容 |
|---|---|
| 目標 | 從 RedCap Msg1 feature preamble 追到 gNB Msg2 view，再追 UE initial BWP/Msg3 |
| 檔案 | `gNB_scheduler_RA.c`, `nr_ue_redcap_bwp.c`, `nr_ra_procedures.c`, `config_ue.c` |
| 函式 | `get_redcap_msg1_rach_config`, `configure_redcap_msg2_bwp`, `nr_ue_get_sib1_initial_*_bwp`, `get_redcap_feature_preamble_partition`, `use_redcap_msg3_ccch_lcid` |
| 預期結果 | 能分清 gNB RA state 與 UE RA/BWP state，不把 log marker 當作完整 attach proof |
| 停止條件 | 若只找到 Msg1 marker，不能宣稱 Msg2/Msg3 或 PDU session 完成 |
| 交付 | Msg1、Msg2、Msg3 各自的 owner、input、marker 表 |

```bash
rg -n "get_redcap_msg1_rach_config|configure_redcap_msg2_bwp|nr_ue_get_sib1_initial_|get_redcap_feature_preamble_partition|use_redcap_msg3_ccch_lcid" \
  openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c \
  openair2/LAYER2/NR_MAC_UE
```

Luna prompt：

```text
由 gNB 與 UE 兩側分別追 Day 4 RA path。輸出 sequence table，不要把尚未看到的 next message 標成 PASS。
最後問我三題，確認我知道 Msg2 BWP view 與 UE BWP selection 的差異。
```

### Day 5：UE capability、DRX awake gate 與 CW owner 決策

| 欄位 | 內容 |
|---|---|
| 目標 | 連接 RedCap capability/低功耗狀態與 Topology 2 的角色分工 |
| 檔案 | `rrc_ue_redcap.c`, `rrc_gNB.c`, `nr_ue_scheduler.c`, `executables/nr-ue.c` |
| 函式 | `nr_rrc_build_redcap_ue_capability`, `nr_rrc_parse_redcap_sib1`, `handle_ueCapabilityInformation`, `nr_ue_drx_is_active`, `aiot_t2_role_process_slot` |
| 預期結果 | 能說明 UE 只在 connected、DRX active、window active 時執行 reader role；持續 CW 留給 gNB/獨立 CW node |
| 停止條件 | 目前 window 是實驗 evidence gate，不可推導真實省電量或 battery-life 結論 |
| 交付 | `UE capability -> MAC DRX state -> PHY role_awake -> R2D/D2R` 圖 |

```bash
rg -n -C 3 "connected_drx_active|nr_ue_drx_is_active|aiot_t2_role_process_slot" \
  openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c executables/nr-ue.c
```

Luna prompt：

```text
說明 Day 5 中 RRC capability、MAC DRX active 與 A-IoT window 三個 gate 的資料來源與 apply point。
反證「RedCap UE 應持續供 CW」並列出目前無法證明的功耗項目。
```

## 5. 第二週：Topology 2、UE Reader、AIOTF 與 CN5G

### Day 6：RFsim Topology 2 封包與 relay

| 欄位 | 內容 |
|---|---|
| 目標 | 了解 RFsim 如何在正常 IQ path 外路由 Tag/CW/R2D/D2R control packet |
| 檔案 | `radio/COMMON/common_lib.h`, `radio/rfsimulator/simulator.cpp`, `stored_node.c` |
| 函式 | `aiot_t2_handle_packet`, `aiot_t2_relay_packet`, `aiot_t2_should_relay`, RFsim packet read/write helpers |
| 預期結果 | 能畫出 peer registration 與每種 packet 的合法 destination |
| 停止條件 | RFsim relay 只證明 logical routing，不證明實體雙波束、功率或干擾隔離 |
| 交付 | CW、R2D、D2R 三列 source/destination/marker 表 |

```bash
rg -n "aiot_t2_handle_packet|aiot_t2_relay_packet|AIOT_T2_.*RELAY|AIOT_T2_.*REGISTER" \
  radio/COMMON/common_lib.h radio/rfsimulator/simulator.cpp radio/rfsimulator/stored_node.c
```

Luna prompt：

```text
追 Day 6 RFsim control path。分別列出 CW、R2D、D2R 的 source role、destination role、option guard 與 marker。
將 physical RF 結論全部標為 [Needs Verification]。
```

### Day 7：Tag、Manchester/SFS 與 CRC

| 欄位 | 內容 |
|---|---|
| 目標 | 從 Tag state 追 R2D decode、D2R encode、fault injection 與 self-test |
| 檔案 | `radio/rfsimulator/stored_node.c` |
| 函式 | `aiot_tag_exchange`, `aiot_crc`, `aiot_encode_pair`, `aiot_decode_pair`, `aiot_apply_fault`, `aiot_tag_self_test`, `aiot_tag_rfsim_cli` |
| 預期結果 | 能解釋 0/1、Manchester pair、payload 1/16/17 與 CRC reject 邊界 |
| 停止條件 | Manchester/SFS 是本實驗 profile，不可宣稱等同目前 TS 38.291 D2R |
| 交付 | 一個 1-byte payload 的 bit→pair→CRC→D2R 範例與三種 reject 原因 |

```bash
rg -n "aiot_tag_exchange|aiot_crc\(|aiot_encode_pair|aiot_decode_pair|aiot_apply_fault|aiot_tag_self_test|aiot_tag_rfsim_cli" \
  radio/rfsimulator/stored_node.c
```

選修 self-test：

```bash
redcap_library/bash_tool/scripts/aiot_registered_check.sh tag-selftest
```

Luna prompt：

```text
只根據 stored_node.c 解釋 Day 7 codec。列出 empty、1、16、17 bytes 與 invalid pair/CRC 的結果。
不要引用模型記憶補足 3GPP encoding。
```

### Day 8：UE Reader／observer 與 40-byte report

| 欄位 | 內容 |
|---|---|
| 目標 | 追參數解析、R2D/D2R codec、awake gate、reader/observer 分工與 N6 diagnostic report |
| 檔案 | `nr-uesoftmodem.c/h`, `nr_ue_rf_helpers.c`, `nr-ue.c`, `common_lib.h` |
| 函式 | `nr_ue_aiot_t2_prepare_r2d`, `nr_ue_aiot_t2_decode_d2r`, `aiot_t2_role_window_active`, `aiot_t2_role_process_slot`, `aiot_t2_send_report` |
| 預期結果 | 能說明只有 primary 發 R2D，observer 只收 D2R；report 缺 correlation/session/epoch |
| 停止條件 | 40-byte UDP 是 `experimental_n6`；不可當作 RRC、NGAP 或 `Namf_AIoT` |
| 交付 | Reader與observer行為表、40-byte欄位表、缺失 correlation 欄位清單 |

```bash
rg -n "nr_ue_aiot_t2_prepare_r2d|nr_ue_aiot_t2_decode_d2r|aiot_t2_role_window_active|aiot_t2_role_process_slot|aiot_t2_send_report" \
  openair1/PHY/NR_UE_TRANSPORT/nr_ue_rf_helpers.c executables/nr-ue.c
```

Luna prompt：

```text
由參數、window、DRX、R2D、D2R、report 六個步驟追 Day 8 UE Reader。
說明 ambiguous pending context 為何必須在 AIOTF arbitration 前拒絕。
```

### Day 9：AIOTF binding、排程、failover 與 first-valid

| 欄位 | 內容 |
|---|---|
| 目標 | 理解 AIOTF 為何是 reader binding 與 arbitration 的唯一 owner |
| 檔案 | `aiotf_inventory.h`, `aiotf_inventory.c`, `tests/test_aiotf_inventory.c` |
| 函式 | `aiotf_binding_table_init`, `aiotf_select_readers`, `aiotf_failover_primary`, `aiotf_schedule_transactions`, `aiotf_arbitrate_report`, `aiotf_diagnostic_associate_report` |
| 預期結果 | 能解釋 1-20/21-30/31-40/41-60 binding、pre-R2D failover、first-valid/duplicate/conflict/stale |
| 停止條件 | 目前 serialized 60 Tags 不等於 60 個 RF Tag 同時競爭；不做 MRC/soft combining |
| 交付 | Tag range mapping、state transition、arbitration decision table |

```bash
rg -n "aiotf_binding_table_init|aiotf_select_readers|aiotf_failover_primary|aiotf_schedule_transactions|aiotf_arbitrate_report|aiotf_diagnostic_associate_report" \
  openair3/AIOTF/aiotf_inventory.c openair3/AIOTF/tests/test_aiotf_inventory.c
```

選修 self-test：

```bash
redcap_library/bash_tool/scripts/aiot_registered_check.sh aiotf-selftest
```

Luna prompt：

```text
以 Tag 25 diversity 為例，追 Day 9 從 binding 到 first-valid、duplicate、conflict、stale 的所有 guard。
再用 Tag 20/21/30/31/40/41 做 boundary table。
```

### Day 10：AIOTF process、NRF/Naiotf 與 AMF/RAN/NEF 停止點

| 欄位 | 內容 |
|---|---|
| 目標 | 追 long-running AIOTF、profile readiness、NRF lifecycle、Naiotf Inventory，並正確停止在缺少 owner 的 standard path |
| 檔案 | `aiotf_service.c`, `oai-cn5g/docker-compose.yaml`, registry wrapper, architecture/operator/function trace |
| 函式 | `parse_config`, `evaluate_health`, `run_service`, `register_and_verify_nrf`, `deregister_nrf`, `handle_sbi_connection`, `parse_naiotf_request`, `start_inventory_operation`, `notify_inventory_result` |
| 預期結果 | 能分開 `experimental_n6`、NRF dependency、bounded Naiotf 與完整 `trusted_af_sbi` |
| 停止條件 | OAI AMF `POST /namf-aiot/v1/transfer` 目前 404；缺 NGAP/RRC topology-2 Stage-3 owner；NEF 缺 `Nnef_AIoT_*` `[Needs Verification]` |
| 交付 | 一張完整 success path、一張 blocked standard path、下一位 owner 的 escalation ticket |

```bash
rg -n "parse_config|evaluate_health|run_service|register_and_verify_nrf|deregister_nrf|handle_sbi_connection|parse_naiotf_request|start_inventory_operation|notify_inventory_result" \
  openair3/AIOTF/aiotf_service.c
rg -n "namf-aiot|Namf_AIoT|Nnef_AIoT|amf_dependency_unavailable" \
  redcap_doc openspec/changes/integrate-aiotf-cn5g-tag-workflow
```

選修且會啟動 container 的展示：

```bash
./mmtc.menu.bash aiot validate
redcap_interface/mmtc.display.bash aiot-t2
./mmtc.menu.bash aiot down
```

Luna prompt：

```text
追 Day 10：Trusted AF -> Naiotf -> AIOTF state -> NRF dependency，以及預期但尚不存在的 AIOTF -> AMF -> NGAP -> RRC -> UE Reader 反向回報。
輸出兩張表：已證實 path 與 blocked path。對 blocked path 必須列 HTTP 404、missing owner 或未凍結 Stage-3 證據，不得補 stub。
```

## 6. 第三週：xApp/dApp 函式重用與最小擴充

第三週以既有 [SDK 開發指南](../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/sdk_development_guide.zh-TW.md) 為 canonical API 說明。本節只安排學習順序，不重複維護 signatures。

### Day 11：先分清 xApp、dApp 與 apply owner

| 欄位 | 內容 |
|---|---|
| 目標 | 判斷需求應放在 xApp decision、dApp guard，或 gNB apply point |
| 檔案 | xApp/dApp SDK headers、`redcap_ul_prb_ctrl_xapp.c`、`ran_func_rc.c` |
| 函式 | `redcap_xapp_find_rc_ran_func_idx`, `redcap_xapp_make_ul_prb_ctrl_req`, `redcap_dapp_guard_ul_prb_cap` |
| 預期結果 | 能畫出 `metric -> xApp request -> E2 RC -> dApp guard -> gNB apply/ACK`，並指出每段 owner |
| 停止條件 | 找不到 production caller 或 apply marker 時標記 `Dormant/blocked`，不把 Public API 寫成已整合功能 |
| 交付 | 一張 responsibility table：input、decision owner、guard owner、apply owner、marker |

```bash
rg -n "redcap_xapp_find_rc_ran_func_idx|redcap_xapp_make_ul_prb_ctrl_req|redcap_dapp_guard_ul_prb_cap|apply_redcap_ul_prb_control" \
  openair2/E2AP/REDCAP_SDK openair2/E3AP/sdk ci-scripts/redcap_ul_prb_ctrl_xapp.c \
  openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c
```

Luna prompt：

```text
只追 Day 11 的 UL PRB control path。逐段列 input、output、caller、callee、拒絕條件與 marker。
對沒有 production caller 或 runtime marker 的函式標記 Dormant/blocked。
```

### Day 12：重用既有 xApp 函式

| 欄位 | 內容 |
|---|---|
| 目標 | 不新增 algorithm，使用既有 helper 選 UE 並建立 bounded control intent |
| 檔案 | `redcap_xapp_sdk.h/.c/.py`, `dapp_xapp_sdk_contract_selftest.py` |
| 函式 | `redcap_xapp_make_priority_hint`, `redcap_xapp_select_top_priority_hint`, `redcap_xapp_make_ul_prb_ctrl_req` |
| 邊界 | null/empty、RNTI 0、validity 0、同分較小 RNTI、`uint16` 飽和、PRB cap min/max |
| 預期結果 | 能先搜尋既有 API，再以現有 self-test 證明選擇與 request contract；不另建 helper |
| 停止條件 | C/Python 對無效元素的行為不一致時，不假設 parity；先記錄差異 `[Needs Verification]` |
| 交付 | 一份「可直接重用／需 adapter／缺少功能」三欄表 |

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/dapp_xapp_sdk_contract_selftest.py
```

Luna prompt：

```text
以三個 UE metric 示範既有 xApp API：一個無效 RNTI、兩個同權重有效 UE。
列出 C 與 Python 預期結果，並說明何時才可建立 UL PRB control request。不要新增函式。
```

### Day 13：重用既有 dApp guard 與 policy

| 欄位 | 內容 |
|---|---|
| 目標 | 用現有 guard 驗證 xApp intent，再選擇 access-pressure policy 或 RA-pressure selector |
| 檔案 | `redcap_dapp_sdk.h/.c/.py`, `gNB_scheduler_uci.c`, `gNB_scheduler_ulsch.c` |
| 函式 | `redcap_dapp_guard_prb_allocation`, `redcap_dapp_access_pressure_policy`, `redcap_dapp_select_ra_pressure_priority` |
| 邊界 | null/empty、RNTI 0、BWP 11/12/51 與非法值、ratio 合計 999/1000/1001、無 I/Q、counter clamp 1000 |
| 預期結果 | 能說明 policy result 必須再通過 allocation guard，且 decision marker 不等於 allocation mutation |
| 停止條件 | 不用 Gate E-Core 56 UE A/B 宣稱 access-pressure mitigation 或 latency improvement |
| 交付 | 一張 accept/reject boundary table，加一條目前已證實與尚未證實的 runtime claim |

```bash
rg -n "redcap_dapp_guard_prb_allocation|redcap_dapp_access_pressure_policy|redcap_dapp_select_ra_pressure_priority|RedCap dApp PRB decision" \
  openair2/E3AP/sdk openair2/LAYER2/NR_MAC_gNB
```

Luna prompt：

```text
以 BWP 12、ratio 合計 999/1000/1001、has_iq_samples true/false 建立 Day 13 boundary table。
分開 Public、Integrated、Runtime-evidenced 與 enforcement [Needs Verification]。
```

### Day 14：只有既有函式無法滿足時，才新增函式

| 步驟 | 操作 | 完成條件 |
|---:|---|---|
| 1 | 先用 `rg` 搜尋 SDK header/source、caller 與相似 guard | 證明現有 API 無法用組合或小 adapter 解決 |
| 2 | 寫一行 contract：input、output、owner、reject、shared state | 不含「未來可能需要」欄位 |
| 3 | 在既有 `.h/.c` 加最小 C API；需要 parity 才同步既有 `.py` | 不新增平行 SDK 檔案或依賴 |
| 4 | 在既有 contract self-test 加一個成功案例與邊界案例 | 至少覆蓋 empty/null、0、min/max、boundary-1/+1 中適用者 |
| 5 | 接到單一既有 caller；先保留 reject/diagnostic marker | 無未宣告 shared-state side effect |
| 6 | 跑 static checks；runtime 未跑就只報 static PASS | claim 不超過證據層級 |

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/dapp_xapp_sdk_contract_selftest.py
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/check_dapp_xapp_sdk_test_validation.py
git diff --check -- openair2/E2AP/REDCAP_SDK openair2/E3AP/sdk \
  agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts
```

Luna prompt：

```text
審查我準備新增的 xApp/dApp 函式。先找可重用 API；若確實缺少，輸出最小 contract、正確 owner、唯一 caller、
適用的 boundary cases 與一個最小 self-test。不要產生新模組、factory 或預留欄位。
```

### Day 15：整合、驗證與證據分級

| 欄位 | 內容 |
|---|---|
| 目標 | 從 SDK self-test 追到 E2/E3 transport、guard、apply/reject marker 與 retained report |
| 靜態驗證 | contract self-test、project static checker、`git diff --check` |
| Runtime 驗證 | 依需求選最近 gate；56 UE 流程使用既有 Gate E-Core 手動復現，不自行拼 command |
| 預期結果 | 能分開 static PASS、transport PASS、control ACK、gNB apply marker 與效果比較 |
| 停止條件 | 沒有 post-hook runtime evidence 時，不宣稱新函式改善 latency、接入率或資源配置 |
| 交付 | 一張 evidence ladder 與一張失敗時的 next-owner ticket |

```bash
sed -n '1,240p' \
  agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/gate_e_core56_manual_reproduction.zh-TW.md
```

Luna prompt：

```text
依 Day 15 將證據分成 source、self-test、transport、ACK、apply marker、outcome comparison。
若缺任一層，停止在最後已證實層並產生 next-owner ticket，不把較低層 PASS 外推成 runtime 效果。
```

## 7. 售後服務診斷流程

收到 A-IoT 問題時固定使用下列順序：

| 次序 | 問題 | 證據 |
|---:|---|---|
| 1 | 使用哪個 profile？ | `profile=experimental_n6|trusted_af_sbi|third_party_af_nef` |
| 2 | 最後一個成功 producer marker？ | Tag、relay、UE、AIOTF、NRF 或 Naiotf marker |
| 3 | 下一個 consumer owner 是否存在？ | source symbol、route、decoder與 state owner |
| 4 | 是 reject、timeout、unavailable 還是 ambiguous？ | exact reason 與 boundary input |
| 5 | cleanup 是否只影響 A-IoT？ | `AIOT_OPERATOR_DOWN ... volumes=preserved` |
| 6 | claim 是否超過 evidence layer？ | 不用 N6/NRF/container health 替代 AMF/RAN/NEF |

Escalation ticket 使用：

```text
Profile:
Input boundary:
Last producer marker:
Expected consumer owner:
Observed reject/status:
Source path and symbol:
Retained evidence path:
Claim allowed:
Claim not allowed:
Next owner/action:
```

## 8. 結業驗收

完成課程後，應能在不查答案的情況下完成：

- 畫出 `RedCap config -> BWP/RACH -> RRC capability -> DRX awake gate`。
- 畫出 `CW node -> Tag <- UE Reader` 與 RFsim control relay。
- 說明 Manchester/SFS/CRC 為實驗 profile `[Needs Verification]`。
- 由 `aiot_t2_role_process_slot` 追到 40-byte N6 report。
- 由 `aiotf_binding_table_init` 追到 arbitration 與 evidence retention。
- 分開 AIOTF liveness、profile readiness、NRF registration 與 Naiotf request/callback。
- 明確回答：目前 AIOTF 與 AMF 尚未完成 `Namf_AIoT` 正常通訊。
- 指出 2.8 必須等待一致的 topology-2 NGAP/RRC Stage-3 owner，2.9 才能接續 NEF。
- 判斷一個控制需求應由 xApp decision、dApp guard 或 gNB apply owner 負責。
- 先重用既有 xApp/dApp API；只有 contract 缺口被證明後才在既有 SDK 檔案新增最小函式。
- 為新函式列出適用的 empty/null、0、min/max、boundary-1/+1 與 shared-state 邊界，並更新既有 contract self-test。
- 分開 static PASS、E2/E3 transport、control ACK、gNB apply marker 與 runtime outcome。
- 使用 `./mmtc.menu.bash aiot down` cleanup，且不刪除 CN5G volume。

若任何一項只能用「應該」、「看起來」或模型記憶回答，該項尚未完成；回到對應 source、marker 或 retained evidence。
