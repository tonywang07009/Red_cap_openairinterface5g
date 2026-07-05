# RedCap 參數代碼審查框架

**目的**：系統化地審查 RedCap 所有參數實現，確保合規性、一致性與正確性

**審查日期**：2026-04-09  
**審查階段**：Milestone 5（集成與吞吐驗證）

---

## 第一部分：審查策略與層次劃分

### A. 審查的四個層次（由上而下）

| 層次 | 範圍 | 關鍵視角 | 對應 3GPP 條款 |
|------|------|--------|------------|
| **L1：配置層** | YAML/config、gNB/UE 啟動參數 | 參數定義完整性、默認值正確性 | TS 38.306, 38.101-1 |
| **L2：RRC/MAC 層** | SIB1、Dedicated Config、BWP、DL/UL 配置 | 信號化路徑、ASN.1 結構正確性 | TS 38.331, 38.321 |
| **L3：物理層 (PHY)** | 帶寬、PRB 限制、MIMO、天線端口、參考靈敏度 | 參數邊界、計算公式、RF 約束 | TS 38.101-1, 38.306 |
| **L4：集成驗證** | 端-端吞吐、容量測試、兼容性 | 參數間協調、性能符合預期 | 測試場景、運行時日誌 |

### B. 審查順序（建議）

**第 1 天：L1 + L2**（配置與信號化──基礎）  
**第 2 天：L3**（物理層──技術約束）  
**第 3 天：L4**（端-端集成驗證）  

---

## 第二部分：L1 配置層審查清單

### 1.1 gNB 側配置審查

**檔案位置**：[openair2/RRC/NR/rrc_gNB.c](openair2/RRC/NR/rrc_gNB.c)、[openair2/RRC/NR/rrc_gNB_config.c](openair2/RRC/NR/rrc_gNB_config.c)

**審查項**：

```markdown
□ 检查 gNB YAML 配置中是否定義：
  □ `redCapInitialBWP_r17.dl_bwp_start` / `.dl_bwp_size`
  □ `redCapInitialBWP_r17.ul_bwp_start` / `.ul_bwp_size`
  □ `redCapInitialBWP_r17.scs` (應為 15 kHz 或 30 kHz)
  □ `redCapInitialBWP_r17.pucch_ResourceCommonRedCap_r17` 的 PUCCH Format 與位置
  □ `cellBarredRedCap1Rx_r17` / `cellBarredRedCap2Rx_r17` 默認值 (是否默認 notBarred)

□ 檢查結構體初始化：
  ✓ 搜索 `struct nr_redcap_config_t`，確認所有欄位已初始化或有防禦性檢查
  ✓ 檢查是否存在未初始化的指針陷阱 (use-after-free)

□ 檢查日誌完整性：
  ✓ gNB 初始化時應打印 "RedCap: [enabled/disabled]"
  ✓ SIB1 編碼前應打印 "SIB1 contains RedCap initial DL/UL BWP"
```

**審查程序**：
1. grep-search 查找所有 `nr_redcap_config_t` 聲明與初始化
2. 驗證與 YAML 配置的映射路徑
3. 檢查默認值是否符合 TS 38.306 / 38.331

---

### 1.2 UE 側配置審查

**檔案位置**：[openair2/RRC/NR/rrc_UE.c](openair2/RRC/NR/rrc_UE.c)、[openair2/RRC/NR/nr_rrc_ue_api.c](openair2/RRC/NR/nr_rrc_ue_api.c)

**審查項**：

```markdown
□ 檢查 UE YAML 配置中是否定義：
  □ `nrue_recap.supportOfRedCap_r17` (boolean)
  □ `nrue_recap.supportOfERedCap_r18` (boolean，可選)
  □ `nrue_recap.halfDuplexFDD_TypeA_RedCap_r17` (boolean)
  □ `nrue_recap.number_of_rx_redcap_r17` (1 或 2)
  □ `nrue_recap.minBW_redcap_r17` (20 MHz for FR1; 默認應為 "20MHz")

□ 檢查 UE 啟動路徑：
  ✓ 確認 `load_nr_redcap_config()` 在 RRC Init 時被調用
  ✓ 檢查 fallback capability 生成邏輯 (若 UE capability file 缺失)
  ✓ 確認 `nrue_recap` 結構體在整個 UE 緩存生命週期內保持一致

□ 檢查日誌：
  ✓ UE 應在 RRC Setup 後打印 "UE RedCap capability: [enabled] number_of_rx=[1/2]"
```

**審查程序**：
1. 搜索 `load_nr_redcap_config()` 定義與調用點
2. 驗證 parameterization 與運行時 capability 的對應
3. 檢查 UE capability signaling pathway

---

## 第三部分：L2 RRC/MAC 信號化層審查清單

### 2.1 SIB1 RedCap 欄位審查

**檔案位置**：[openair2/RRC/NR/rrc_gNB_sib1.c](openair2/RRC/NR/rrc_gNB_sib1.c)

**3GPP 規範參考**：TS 38.331 Clause 5.2.2.3 (SIB1 ASN.1 定義)；[TS 38.331 Clause 5.2.2.4.2](TS 38.331 Clause 5.2.2.4.2) (RedCap access barring logic)

**審查項**：

```markdown
□ RedCap-ConfigCommonSIB-r17 編碼檢查：
  □ SIB1 中是否包含 `redCap_ConfigCommon_r17` 指針
  □ 檢查是否正確設置 `halfDuplexRedCapAllowed_r17`
    ├─ 若為 present，應為 TS 38.331 定義的 enumeration (e.g., "true")
    └─ 若為 absent，RedCap 設備應視此 cell barred (審查邏輯正確性)
  
  □ 檢查 `cellBarredRedCap1Rx_r17` / `cellBarredRedCap2Rx_r17` 的編碼：
    ├─ 應為 BIT STRING 或 ENUMERATION
    └─ 默認應為 "notBarred"

□ initialDownlinkBWP-RedCap-r17 編碼檢查：
  □ 確認 `clone_redcap_downlink_bwp()` 將 common DL BWP 複製進 RedCap initial DL BWP
  □ 檢查 CORESET#0 與 searchSpace#0 的複製邏輯（若已實現）
  □ 驗證 `controlResourceSetZero` 與 `searchSpaceZero` 的正確參數透傳
  
  □ 檢查 PDCCH 監視空間是否正確複製：
    ├─ 對於 15 kHz SCS：搜索 `common-SearchSpace`、`pagingSearchSpace` 複製檢查
    └─ 對於 30 kHz SCS：驗證不同計算邏輯

□ initialUplinkBWP-RedCap-r17 編碼檢查：
  □ 確認 `clone_redcap_uplink_bwp()` 將 common UL BWP 複製進 RedCap initial UL BWP
  □ 檢查 PUCCH 資源池：
    ├─ `pucch_ResourceCommonRedCap_r17.pucchResource[]` 數量是否足夠 (建議 ≥ 4)
    ├─ 檢查 PUCCH formats (Red Cap 應支持 Format 0/1/2，視場景而定)
    └─ 檢查 PUSCH TBS 與 ResourceAllocation 默認值
  
  □ 檢查 RACH 資源：
    ├─ `.rach_ConfigCommon_r17` 中 RACH duration、timing advance 是否合理
    └─ RedCap RACH sequence 數量是否足夠 (不應超過 common RACH)

□ ASN.1 編碼檢查：
  □ 使用 `asn1c` 或本地 ASN.1 parser 驗證編碼的有效性
  □ 對比 cmake_targets/log 中 SIB1 dump 與預期結構
```

**審查程序**：
1. 找到 `clone_redcap_downlink_bwp()` 與 `clone_redcap_uplink_bwp()` 函數
2. 逐行檢查每個 RedCap-specific 欄位的複製邏輯
3. 運行單測：`./test_nr_sib1_redcap` (若存在) 或手動驗證 SIB1 dump
4. 對比 gNB log 中的 SIB1 結構與預期 ASN.1 結構

---

### 2.2 UE 側 SIB1 解析與 Barring 決策審查

**檔案位置**：[openair2/RRC/NR/rrc_UE.c](openair2/RRC/NR/rrc_UE.c), 函數 `rrc_UE_process_sib1()`

**3GPP 規範參考**：TS 38.331 Clause 5.2.2.4.2

**審查項**：

```markdown
□ RedCap Barring 邏輯檢查（UE 端）：
  □ UE 在解析 SIB1 後，應執行以下決策樹：
    
    IF SIB1.cellAccessRelatedInfo.cellBarred == "barred":
      UE treats cell as barred → skip attach
    ELSE IF UE.redCapCapability.halfDuplexFDD_TypeA == true AND
            SIB1.redCap_ConfigCommon_r17.halfDuplexRedCapAllowed_r17 == absent:
      UE treats cell as barred (TS 38.331 clause 5.2.2.4.2 note) → skip attach
    ELSE IF UE.redCapCapability.number_of_rx == 1 AND
            SIB1.redCap_ConfigCommon_r17.cellBarredRedCap1Rx_r17 == "barred":
      UE treats cell as barred → skip attach
    ELSE IF UE.redCapCapability.number_of_rx == 2 AND
            SIB1.redCap_ConfigCommon_r17.cellBarredRedCap2Rx_r17 == "barred":
      UE treats cell as barred → skip attach
    ELSE:
      Proceed to UE attach (use RedCap initial BWP)

  □ 檢查是否每個分支都有對應代碼
  □ 檢查跳過 attach 後的狀態轉移 (應返回 RRC_IDLE)

□ RedCap initial BWP 套用檢查：
  □ 若 UE 通過 barring 檢查，應在 `nr_rrc_mac_config_req_sib1()` 中：
    ├─ 若存在 `initialDownlinkBWP-RedCap-r17`，使用之
    ├─ 否則使用 common initial DL BWP
    └─ 同樣邏輯適用於 UL BWP

  □ 檢查 MAC PWS (Physical Workspace State) 是否正確切換到 RedCap initial BWP

□ 日誌檢查：
  ✓ UE 應打印："[RRC] SIB1 parsed, RedCap initial DL BWP: PRB [X:Y], SCS [Z kHz]"
  ✓ UE 應打印："[RRC] UE RedCap barring decision: [PASS/FAIL] reason=[...]"
```

**審查程序**：
1. 搜索 `rrc_UE_process_sib1()` 定義
2. 追蹤 RedCap barring 決策流程，確保所有分支都覆蓋
3. 檢查狀態轉移是否正確
4. 從 `*-oai-nr-ue*.logs` 驗證執行時日誌

---

### 2.3 UE Capability 信號化與 Dedicated Config 審查

**檔案位置**：[openair2/RRC/NR/rrc_gNB_ue_context.c](openair2/RRC/NR/rrc_gNB_ue_context.c), [openair2/RRC/NR/rrc_UE.c](openair2/RRC/NR/rrc_UE.c)

**3GPP 規範參考**：TS 38.331 Clause 5.6.1.3

**審查項**：

```markdown
□ gNB 側 UE Capability 檢查邏輯：
  □ gNB 在接收 `UECapabilityInformation` 後，應驗證：
    ├─ `ueNrCapability.redCapFeatureSupport_r17.isPresent()` 是否存在
    ├─ 若存在，解析 `supportOfRedCap_r17`、`halfDuplexFDD_TypeA_RedCap_r17` 標誌
    ├─ 根據標誌決定是否為此 UE 分配 RedCap initial BWP
    └─ 記錄日誌："[gNB] UE RNTI 0x[...] is RedCap; capability: [...]"

  □ 檢查 gNB 後續配置邏輯：
    ├─ 若 UE RedCap，Dedicated Config 應包含 initialDownlinkBWP-RedCap-r17
    └─ 否則使用 common initial DL BWP（或不發送 initialBWP）

□ UE 側 Capability 生成邏輯（fallback path）：
  ✓ 若 UE capability file 不存在，應調用 `build_redcap_ue_capability_r17()`
  ✓ 檢查 fallback capability 是否包含：
    ├─ `supportOfRedCap_r17 = true`
    ├─ `halfDuplexFDD_TypeA_RedCap_r17 = [UE configuration]`
    ├─ `number_of_rx_redcap_r17 = [1 or 2]`
    └─ 其他必要欄位

□ ASN.1 編碼檢查：
  ✓ `UECapabilityInformation` 的 RedCap-capability 部分應正確編碼
  ✓ 驗證 Rel-17 RRC 消息版本 (應為 "c17" 或更高)
```

**審查程序**：
1. 搜索 UE capability processing 函數
2. 檢查 gNB 在接收 `UECapabilityInformation` 後的決策路徑
3. 檢查 UE fallback capability generation
4. 驗證 ASN.1 結構與日誌對應

---

## 第四部分：L3 物理層參數審查清單

### 3.1 帶寬與 PRB 限制審查

**檔案位置**：[openair1/PHY/NR_TRANSPORT/nr_transport.c](openair1/PHY/NR_TRANSPORT/nr_transport.c)、[openair2/RRC/NR/rrc_gNB_config.c](openair2/RRC/NR/rrc_gNB_config.c)

**3GPP 規範參考**：TS 38.306 Clause 4.2.21.1（RedCap FR1 最大帶寬 20 MHz）；TS 38.101-1 Annex C（PRB 與帶寬對應表）

**審查項**：

```markdown
□ RedCap FR1 帶寬硬性限制：
  □ 檢查 gNB 初始化時，若 `redCapFeatureEnabled == true`，應強制：
    ├─ `dl_carrier.dl_bandwidth <= 20 MHz` (檢查警告或 assert)
    ├─ `ul_carrier.ul_bandwidth <= 20 MHz`
    └─ 若配置超過 20 MHz，應 log FATAL 或返回初始化失敗

□ PRB 計算檢查：
  ✓ 對於 15 kHz SCS + 20 MHz BW：應為 106 PRBs (TS 38.101-1 Table C.1)
  ✓ 對於 30 kHz SCS + 20 MHz BW：應為 51 PRBs
  ✓ 檢查函數 `nr_get_prb_for_bw()` 或同類的邊界情況

□ eRedCap 專屬 PRB 限制（若已實現）：
  □ 若 `eRedCapNotReducedBB-BW-r18 == false`，unicast PDSCH/PUSCH 應限制在：
    ├─ 15 kHz SCS：25 PRBs (對應 5 MHz PHY bandwidth)
    ├─ 30 kHz SCS：12 PRBs (對應 5 MHz PHY bandwidth)
    └─ 檢查 scheduler 是否強制此限制

  □ 檢查日誌：
    ├─ "eRedCap: [enabled/disabled]; reduced_bb_bw_fallback: [yes/no]"
    └─ scheduler allocation 時若超過 PRB 限制應打印 WARNING
```

**審查程序**：
1. 搜索 `nr_get_prb_for_bw()` 與帶寬驗證邏輯
2. 檢查 gNB 初始化、scheduler、PHY frame generation 中的帶寬檢查
3. 驗證計算公式是否與 TS 38.101-1 對齐
4. 運行 unit tests：`./test_nr_frame_params` 並檢查 20 MHz RedCap 情況

---

### 3.2 MIMO / 天線端口審查

**檔案位置**：[openair1/PHY/NR_TRANSPORT/nr_precoding.c](openair1/PHY/NR_TRANSPORT/nr_precoding.c)、[openair2/RRC/NR/rrc_gNB_config.c](openair2/RRC/NR/rrc_gNB_config.c)

**3GPP 規範參考**：TS 38.306 Clause 4.2.21.1（RedCap 支持 1Rx mandatory 或 2Rx optional；無 UL MIMO）；TS 38.201 Annex B (precoding 表)

**審查項**：

```markdown
□ DL MIMO 限制檢查：
  □ gNB 若知悉 UE 為 RedCap (1Rx or 2Rx)，應限制 DL layers：
    ├─ 若 UE.number_of_rx_redcap == 1：DL layers ≤ 1 (SISO only)
    ├─ 若 UE.number_of_rx_redcap == 2：DL layers ≤ 2
    └─ 檢查 PMI / precoding matrix 的應用邏輯

  □ 檢查日誌：
    ├─ PDSCH allocation 時："[MAC/SCHED] PDSCH RNTI 0x[...] DL layers: 1 (RedCap 1Rx)"
    └─ 若嘗試分配超過限制的 layers，應打印 WARNING

□ UL MIMO 限制檢查（應為 NONE）：
  □ gNB 對 RedCap UE 的 PUSCH 應強制：
    ├─ `rank = 1` (無 spatial multiplexing)
    ├─ `number_of_tx_ports = 1`
    └─ Codebook restriction (若適用)

  □ 檢查日誌：
    ├─ PUSCH allocation 時："[MAC/SCHED] PUSCH RNTI 0x[...] rank: 1 (RedCap)"

□ 天線端口配置檢查：
  ✓ 檢查 `antenna_ports_tx` / `antenna_ports_rx` 的初始化
  ✓ 若為 RedCap，應限制 `antenna_ports_rx = [1 or 2]`, `antenna_ports_tx = 1`
```

**審查程序**：
1. 搜索 scheduler PDSCH/PUSCH allocation 函數
2. 檢查 layer/rank 決策邏輯中的 RedCap 檢查
3. 檢查 precoding matrix 選擇邏輯
4. 驗證相關日誌的完整性

---

### 3.3 參考靈敏度與功率調整審查

**檔案位置**：[openair1/PHY/NR_UE_TRANSPORT/nr_dlsch_decoding.c](openair1/PHY/NR_UE_TRANSPORT/nr_dlsch_decoding.c)、[openair1/PHY/NR_UE_TRANSPORT/nr_srs_modulation.c](openair1/PHY/NR_UE_TRANSPORT/nr_srs_modulation.c)

**3GPP 規範參考**：TS 38.101-1 Clause 6.3.3.1（Reference Sensitivity；ΔR_1R for 1Rx）；TS 38.306 FDD / TDD tables

**審查項**：

```markdown
□ DL Reference Sensitivity 調整（UE 端）：
  □ 若 UE 為 RedCap 1Rx，應應用 ΔR_1R 修正：
    ├─ FDD 1Rx：通常為 +3 dB (相對 2Rx)
    ├─ 檢查是否在 DLSCH decode pipeline 中應用此修正因子
    ├─ 檢查受影響頻段：10/15/20 MHz
    └─ 驗證公式：REFSENS_1Rx = REFSENS_nominal + ΔR_1R

  □ 檢查是否有相關日誌："[UE PHY] DLSCH REFSENS adjustment: +3 dB (1Rx RedCap)"

□ UL Power Control 檢查：
  □ RedCap UE 功率等級通常為 Power Class 3 (+23 dBm)
  □ 檢查 PUSCH/PUCCH 功率計算中是否正確應用：
    ├─ 基礎功率設定 (P_CMAX = 23 dBm for RedCap)
    ├─ Power headroom report (PHR) 是否正確
    └─ Frequency-selective power adjustment 邏輯

  □ 檢查 `nr_ue_power_procedures()` 或類似函數中的 RedCap 分支

□ 日誌驗證：
  ✓ gNB log 應打印："[PHY] RSRPmeas RNTI 0x[...]: [value] dBm (1Rx RedCap ref: +3 dB)"
  ✓ UE log 應打印："[UE MAC] PHR: [value] dB; P_CMAX: 23 dBm (RedCap)"
```

**審查程序**：
1. 搜索 `REFSENS` / sensitivity 修正邏輯
2. 找到功率控制函數，確認 RedCap 分支
3. 檢查日誌語句的完整性與準確性

---

## 第五部分：L4 端-端集成驗證審查清單

### 4.1 運行時日誌驗證

**預期日誌檢查點**（參考 [redcap_runtime_validation_checklist.md](../../../agent_doc/Project_management/redcap_runtime_validation_checklist.md)）

```markdown
□ [Task 333331] - Attach OAI UE 1 (normal user)
  Expected logs:
  ├─ "[RRC] UE attach success, RNTI: 0x[...]"
  └─ "[MAC] UE normal DL/UL BWP assigned"

□ [Task 302001] - Verify UE 1 is normal (no RedCap)
  Expected logs:
  ├─ "[gNB] UE RNTI 0x[...] capability: NOT RedCap"
  └─ "[MAC] UE1 assigned common initial BWP (non-RedCap)"

□ [Task 333332] - Attach OAI UE 2 (RedCap)
  Expected logs:
  ├─ "[RRC] UE2 attach success, RNTI: 0x[...] (RedCap)"
  └─ "[MAC] UE2 RedCap initial DL/UL BWP assigned"

□ [Task 302002] - Verify UE 2 is RedCap
  Expected logs:
  ├─ "[gNB] UE with RNTI 0x[...] is RedCap"
  ├─ "[gNB] RedCap capability: 1Rx/2Rx, half-duplex: [yes/no]"
  └─ "[gNB] UE2 will use RedCap initial BWP"

□ [Task 302003] - Verify gNB builds RedCap initial BWP into SIB1
  Expected logs:
  ├─ "[SIB1 encode] RedCap initial DL BWP: start=[X] size=[Y] scs=[Z]"
  ├─ "[SIB1 encode] RedCap initial UL BWP: start=[X] size=[Y] scs=[Z]"
  └─ "[SIB1 encode] cellBarredRedCap1Rx: notBarred, cellBarredRedCap2Rx: notBarred"

□ [Task 020005] - Ping ext-dn from both UEs
  Expected logs:
  ├─ "UE1 ping: [XX] packets transmitted, [YY]% loss"
  └─ "UE2 ping: [XX] packets transmitted, [YY]% loss (RedCap)"

□ [Task 030001] - Iperf RedCap UE2 DL 60 Mbps UDP
  Expected logs:
  ├─ "[TRAFFIC] DL throughput UE2: [X] Mbps (target 60 Mbps)"
  └─ "[TRAFFIC] Packet loss UE2: [Y]% (threshold [Z]%)"

□ [Task 030002] - Iperf RedCap UE2 UL 20 Mbps UDP
  Expected logs:
  ├─ "[TRAFFIC] UL throughput UE2: [X] Mbps (target 20 Mbps)"
  └─ "[TRAFFIC] Packet loss UE2: [Y]% (threshold [Z]%)"
```

**審查程序**：
1. 執行完整運行時驗證：`cd ci-scripts && ./redcap_runtime_host_validation.sh`
2. 從 `test_results.html` 確認所有測試 ID 的 PASS/FAIL 狀態
3. 從 `cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/` 提取 gNB/UE logs
4. grep 查找上述預期日誌，確認所有關鍵點都有輸出

---

### 4.2 吞吐量與性能驗證

**檔案位置**：[ci-scripts/redcap_runtime_summary.py](ci-scripts/redcap_runtime_summary.py)

```markdown
□ 吞吐量目標檢查：
  □ RedCap UE2 DL throughput：
    ├─ 目標值：≥ 60 Mbps
    ├─ 容差：±15% (允許 51～69 Mbps)
    └─ 驗證來源：`iperf_client_rfsim5g_ue2.log` 中的 "Receiver Bitrate"
  
  □ RedCap UE2 UL throughput：
    ├─ 目標值：≥ 20 Mbps
    ├─ 容差：±25% (允許 15～25 Mbps)
    └─ 驗證來源：`iperf_server_redcap_ue2.log` 或 client 端 ACK bitrate

□ 可靠性檢查：
  □ 丟包率：
    ├─ DL iperf 丟包率 < 5%
    ├─ UL iperf 丟包率 < 10%
    └─ ping 丟包率 < 2%

□ 延遲檢查（若有 ping output）：
  ├─ 平均 RTT < 50 ms
  └─ 最大 RTT < 200 ms
```

**審查程序**：
1. 執行 `python3 redcap_runtime_summary.py --scenario container_5g_flexric_rfsim_redcap.xml`
2. 檢查輸出的 Markdown 報告中的吞吐量表
3. 對比與預期值，記錄任何偏差 > 20% 的情況

---

## 第六部分：集成審查檢查清單（跨層驗證）

```markdown
□ 一致性檢查：
  ✓ gNB 配置中的 RedCap initial BWP 參數 == SIB1 編碼的 initialDownlinkBWP-RedCap-r17
  ✓ UE 解析 SIB1 的 initialDownlinkBWP-RedCap-r17 == UE 實際使用的 DL BWP
  ✓ gNB 檢測到 UE RedCap == UE 聲明的 capability 一致

□ 邊界條件檢查：
  ✓ 1Rx RedCap UE 在 2層 DL transmission 時是否被拒絕
  ✓ eRedCap UE (reduced BB BW) 超過 25 PRB 分配時是否被糾正
  ✓ half-duplex RedCap UE 在 half-duplex 不支持的 cell 上是否被 barred

□ 降級與兼容性檢查：
  ✓ 若配置或運行時參數缺失，系統是否優雅降級（使用 common initial BWP）
  ✓ 非 RedCap UE 在同一 cell 上是否不受影響
  ✓ 混合 RedCap + 普通 UE 的 scheduler 資源分配是否無衝突

□ 性能與反向兼容性：
  ✓ 啟用 RedCap 時，non-RedCap UE 吞吐量是否 < 5% 衰減
  ✓ Latency 是否在 ±10% 之內
```

---

## 第七部分：代碼審查執行順序與時間估計

### 審查分階段執行

**第 1 天（4 小時）：L1 + L2 基礎迴圈**

| 時段 | 任務 | 預估時間 |
|------|------|--------|
| 09:00-10:30 | L1.1 gNB 配置審查 + L1.2 UE 配置審查 | 90 min |
| 10:30-10:45 | 休息 | 15 min |
| 10:45-12:15 | L2.1 SIB1 RedCap 欄位審查 | 90 min |
| 12:15-13:00 | 午餐 | 45 min |
| 13:00-14:30 | L2.2 UE barring 決策審查 | 90 min |
| 14:30-15:00 | L2.3 UE capability 信號化審查 | 30 min |
| 15:00-15:15 | 總結 Day 1 發現 | 15 min |

**第 2 天（3 小時）：L3 物理層**

| 時段 | 任務 | 預估時間 |
|------|------|--------|
| 09:00-10:30 | L3.1 帶寬與 PRB 限制審查 | 90 min |
| 10:30-10:45 | 休息 | 15 min |
| 10:45-12:15 | L3.2 MIMO / 天線審查 + L3.3 功率調整審查 | 90 min |
| 12:15-13:00 | 午餐 | 45 min |
| 13:00-14:00 | 單元測試與邊界驗證 | 60 min |
| 14:00-14:15 | 總結 Day 2 發現 | 15 min |

**第 3 天（2.5 小時）：L4 集成驗證**

| 時段 | 任務 | 預估時間 |
|------|------|--------|
| 09:00-10:30 | L4.1 執行運行時驗證 + 日誌檢查 | 90 min |
| 10:30-10:45 | 休息 | 15 min |
| 10:45-12:15 | L4.2 吞吐量驗證 + 跨層一致性檢查 | 90 min |
| 12:15-13:00 | 午餐 | 45 min |
| 13:00-13:30 | 最終報告與改進建議匯總 | 30 min |

---

## 第八部分：常見審查發現模板與改進建議

### 如果發現...

| 發現 | 原因分析 | 改進建議 |
|------|--------|--------|
| SIB1 中缺少 `initialDownlinkBWP-RedCap-r17` | `clone_redcap_downlink_bwp()` 未被調用或條件檢查失敗 | 1) 確認 gNB YAML 中 `redCapInitialBWP_r17` 已配置 <br> 2) 添加 DEBUG log 在 clone 函數進入點 <br> 3) 檢查 SIB1 encoding 函數中的 RedCap 欄位指針是否初始化 |
| UE 接收 SIB1 但未有效套用 RedCap initial BWP | `rrc_UE_process_sib1()` 中解析邏輯缺陷 或 `nr_rrc_mac_config_req_sib1()` 未被後續調用 | 1) 單步追蹤 SIB1 parsing 路徑 <br> 2) 確認 UE capability check 正確 <br> 3) 驗證 MAC 層 PWS 更新邏輯 |
| RedCap UE 被不必要地分配 2 層 DL transmission | Scheduler 未檢查 UE RedCap capability | 1) 在 `sched_nr_ue_dci()` 中添加層數限制檢查 <br> 2) 若 `ue->redcap_capability.number_of_rx == 1`，強制 `max_dlayers = 1` <br> 3) 添加 WARNING log 若超過限制 |
| 吞吐量低於預期 (< 40 Mbps DL) | 1) PRB 分配不足 <br> 2) MCS 過低 <br> 3) 編碼錯誤 | 1) 檢查 scheduler allocation log 中的 PRB count <br> 2) 驗證 SINR / CQI 計算邏輯 <br> 3) 檢查 HARQ 重傳率 |
| UE 被不正確地 barred | `nr_rrc_redcap_sib1_access_allowed()` 邏輯錯誤 | 1) 重新檢查 barring 決策樹（見 2.2 節） <br> 2) 驗證 `halfDuplexRedCapAllowed_r17` 解析邏輯 <br> 3) 添加詳細 DEBUG log 每個 barring 條件檢查 |

---

## 第九部分：代碼審查文件清單

準備以下文件進行審查：

### 配置文件
- [ ] [../../../common/ran_context.h](../../../common/ran_context.h) — 全局上下文定義
- [ ] [../../RRC/NR/rrc_gNB.c](../../RRC/NR/rrc_gNB.c) — gNB RRC 主體
- [ ] [../../RRC/NR/rrc_UE.c](../../RRC/NR/rrc_UE.c) — UE RRC 主體

### 信號化與配置
- [ ] [../../RRC/NR/rrc_gNB_config.c](../../RRC/NR/rrc_gNB_config.c) — gNB 配置生成
- [ ] [../../RRC/NR/rrc_gNB_sib1.c](../../RRC/NR/rrc_gNB_sib1.c) — SIB1 編碼
- [ ] [../../RRC/NR/rrc_UE_api.c](../../RRC/NR/rrc_UE_api.c) — UE RRC API

### 物理層
- [ ] [../../../openair1/PHY/NR_TRANSPORT/nr_transport.c](../../../openair1/PHY/NR_TRANSPORT/nr_transport.c) — 傳輸層
- [ ] [../../../openair1/PHY/NR_TRANSPORT/nr_precoding.c](../../../openair1/PHY/NR_TRANSPORT/nr_precoding.c) — Precoding
- [ ] [../../MAC/NR/nr_scheduler.c](../../MAC/NR/nr_scheduler.c) — 調度器

### 測試與驗證
- [ ] [../../../cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/](../../../cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/) — 運行時日誌
- [ ] [../../../test_results.html](../../../test_results.html) — 運行時測試結果

---

## 常用工具命令

```bash
# 基本搜索
grep -r "redcap\|RedCap\|REDCAP" openair1/ openair2/ openair3/ --include="*.c" --include="*.h" | head -100

# 按檔案分類統計
find openair{1,2,3} -name "*.c" -o -name "*.h" | xargs grep -l "redcap\|RedCap" | sort

# 查找特定函數
grep -n "clone_redcap_downlink_bwp\|clone_redcap_uplink_bwp\|nr_rrc_redcap_sib1_access_allowed" openair2/RRC/NR/*.c

# 提取 SIB1 dump 進行 ASN.1 驗證
grep -A 50 "SIB1 encoded" cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/*-oai-gnb.logs | head -100

# 統計 RedCap 相關的日誌行數
grep -c "RedCap" cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/*-oai-gnb.logs
```

---

## 審查反饋與改進建議模板

請使用以下格式記錄每項發現：

```
### [優先級] 發現编号：[簡述標題]

**涉及檔案**：filePath (Line X-Y)

**3GPP 規範引用**：TS XX.XXX Clause X.X.X

**發現詳情**：
[詳細描述問題]

**原因分析**：
[分析根本原因]

**改進建議**：
1. [建議 1]
2. [建議 2]
3. [建議 3]

**嚴重性評級**：
- CRITICAL (影响功能正确性或规范一致性)
- MAJOR (性能偏差或设计缺陷)
- MINOR (代码风格、文档不清晰)
- INFO (说明或建议性反馈)
```

---

**審查框架完成。建議依序進行第 1-3 天的審查。** 🎯
