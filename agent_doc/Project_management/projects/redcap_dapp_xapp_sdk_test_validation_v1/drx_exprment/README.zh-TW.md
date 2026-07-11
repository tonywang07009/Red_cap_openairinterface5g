<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Adaptive C-DRX 實驗文件

本文件說明實驗設計、目前可用的證據，以及不使用 AI 工具時可由人工執行的重建步驟。本文件不取代下列 canonical 文件：

- [詳細人工重建指南](../Doc/adaptive_drx_ab_manual_reproduction.zh-TW.md)
- [API 與控制合約](../Doc/adaptive_drx_api_contract.zh-TW.md)
- [Trace Code Guide](../Doc/adaptive_drx_trace_code_guide.zh-TW.md)
- [目前 Gate 報告](../report/adaptive_drx_ab_gate_2026-07-11.zh-TW.md)

## 1. 實驗設計

### 1.1 範圍與控制權

本實驗只處理單一 RedCap UE 在 `RRC_CONNECTED` 狀態下的 C-DRX。不包含 RRC_INACTIVE eDRX、RRC_IDLE paging、PSM 或 UE 實體耗電量測。

控制權分工如下：

| 元件 | 責任 |
|---|---|
| xApp | 預測下一個 30-arrival window，並提出 Long DRX cycle |
| C dApp guard | 依 UE、版本、cooldown、profile 與 rollback 狀態接受或拒絕提案 |
| gNB | 透過 RRC 設定 UE，並避免在 UE 不屬於 DRX Active Time 時排程一般新資料 |
| UE MAC | 執行已設定的 DRX timers，並決定何時必須監聽 PDCCH |

TS 38.321 version 18.2.0 clause 5.7 定義 C-DRX 與 Active Time。Active Time 包含 On Duration、inactivity、適用的 HARQ retransmission timers、pending Scheduling Request，以及規格列出的其他條件。因此 DRX 控制的是 UE 的 PDCCH 監聽行為，不是讓 gNB 進入睡眠。

TS 38.331 version 18.5.1 的 `DRX-Config` 定義 RRC fields 與單位：

| Field | 規格單位 | v1 實驗值 |
|---|---|---|
| `drx-onDurationTimer` | 1/32 ms 或列舉的毫秒值 | 由 profile 選擇 10、20 或 40 ms |
| `drx-InactivityTimer` | 列舉的毫秒值 | 固定 20 ms |
| `drx-LongCycleStartOffset` | cycle 與 start offset，單位為 ms | profile cycle；offset 固定 0 |
| `drx-HARQ-RTT-TimerDL/UL` | symbols | 由 OAI RRC producer 固定 |
| `drx-RetransmissionTimerDL/UL` | slots | 由 OAI RRC producer 固定 |
| `drx-SlotOffset` | 1/32 ms | 固定 0 |

本地規格來源位於 `redcap_doc/specs/redcap_3gpp/DRX/`。

### 1.2 v1 合法 Profiles

實驗只接受下列 profile pairs：

| Profile | Long cycle | On Duration | On Duration / cycle |
|---|---:|---:|---:|
| `drx-320-10` | 320 ms | 10 ms | 3.125% |
| `drx-640-10` | 640 ms | 10 ms | 1.5625% |
| `drx-1280-20` | 1280 ms | 20 ms | 1.5625% |
| `drx-2560-20` | 2560 ms | 20 ms | 0.78125% |
| `drx-5120-40` | 5120 ms | 40 ms | 0.78125% |
| `drx-10240-40` | 10240 ms | 40 ms | 0.390625% |

這些是綁定的完整 profiles，不是 Long cycle 與 On Duration 的獨立 factorial experiment。A/B 結果可以比較完整 profile，但不能把效果單獨歸因於 On Duration。

主 v1 實驗停用 short DRX 與 optional DRX Command MAC CE。DRX Command 不是 RRC reconfiguration，也不是 rollback 方法。

### 1.3 Parameter Conformance 與 Adaptive A/B

Focused tests 用來建立 parameter conformance，範圍包含合法 profile pairs、timer boundaries、scheduler gating、stale version、cooldown、HARQ/SR Active-Time conditions、DRX Command guards 與 rollback state。

Runtime A/B 用來量測 end-to-end control path 與 traffic trade-off，包含四個彼此獨立的 campaigns：

| Campaign | Arm | 方向 | Arrivals | Warm-up | Scored |
|---|---|---|---:|---:|---:|
| `arm-a-dl` | gNB 本地控制 | Downlink | 330 | 30 | 300 |
| `arm-b-dl` | Adaptive E2SM-RC 控制 | Downlink | 330 | 30 | 300 |
| `arm-a-ul` | gNB 本地控制 | Uplink | 330 | 30 | 300 |
| `arm-b-ul` | Adaptive E2SM-RC 控制 | Uplink | 330 | 30 | 300 |

Arm B 每 30 筆 scored arrivals 套用一個 policy。只有 versioned request、E2 acknowledgement、dApp acceptance、gNB application 與 RRC completion markers 全部可以關聯時，policy 才算 committed。

### 1.4 下一版 Baseline Protocol

下一版 A/B protocol 使用 `drx-320-10` 作為固定 Arm A baseline。Traffic 開始前只 pre-apply 一次，300 筆 scored arrivals 期間都保持不變。Arm B 從相同的合法 baseline 開始，之後每累積並 commit 一個 30-arrival history window 才能更新 profile。

這是已核准的下一次實驗設計，不是目前 runner 的行為。現有 manifest 與 `run_campaign.py` 仍會在每個 scored window 套用固定 seed 的 Arm A profile。Runner 與 manifest 尚未完成修改前，不可把目前 v1 run 標示為 fixed-baseline experiment。

Arm B baseline 還有 version correlation 限制：第一個 FlexRIC RIC request ID 必須嚴格大於本地已套用的 baseline version。若無法證明此順序，應停止並回報 `stale_policy_version` 或 `rollback_unavailable`，不可強制執行。

### 1.5 必要量測與宣稱邊界

| 量測 | 用途 | 目前支援狀態 |
|---|---|---|
| Applied profile 與 marker chain | 證明 control 已生效 | Logs/checker 已實作 |
| Delivery success | 確認每個 arrival 有 scored record | 目前只有 process result；UDP delivery 仍需 receiver evidence |
| First receive latency | 量測 wake-to-delivery 行為 | 缺 receiver timestamp collector |
| iPerf goodput/loss/jitter | 發現 traffic degradation | 已保存 raw output；缺 parser |
| UE DRX Active-Time slot ratio | 與能源相關的行為 proxy | 缺 counter/export |
| DL/UL HARQ retransmissions | 解釋 delivery 下降或 Active Time 延長 | 缺 campaign counter/export |
| Policy apply latency | 量化 RRC control overhead | 缺 timestamp correlation |

RFsim 無法量測電流、瓦特、焦耳、電池壽命或 receiver-chain power states。Active-Time 與 PDCCH-monitoring ratio 只能稱為 behavior proxies。

## 2. 目前實驗結果說明

### 2.1 Evidence 狀態

| Surface | 目前結果 |
|---|---|
| gNB 與 UE softmodem builds | PASS |
| Telnet CI DRX control module | PASS |
| Focused UE DRX、RC 與 gNB DRX CTest targets | PASS，3/3 |
| Trace、predictor、window 與 checker tests | PASS，4/4 |
| C dApp 與 C xApp self-checks | PASS |
| 產生的 Python FlexRIC module | 此主機為 definition-only |
| Main build E2 path | 記錄的 build caches 為 `E2_AGENT=OFF` |
| 四個 RFsim campaigns | BLOCKED / 尚未執行 |

通過的 builds 與 unit tests 只證明 source readiness，不代表 live E2 control request、RFsim adaptive policy 已套用，或 traffic 有改善。

### 2.2 Scored Population

| Campaign | Planned scored | Evidenced scored | 結果 |
|---|---:|---:|---|
| `arm-a-dl` | 300 | 0 | BLOCKED |
| `arm-b-dl` | 300 | 0 | BLOCKED |
| `arm-a-ul` | 300 | 0 | BLOCKED |
| `arm-b-ul` | 300 | 0 | BLOCKED |
| **Total** | **1200** | **0** | **BLOCKED** |

目前整體可證明的 scored population 是 `0/1200`。

目前所有 latency、goodput、loss、jitter、HARQ、monitoring、Active-Time、reject 與 rollback metrics 都是 `N/A`。`N/A` 代表尚未量測，不是零，也不是成功結果。

目前 blockers 如下：

- Evidence host 的 SWIG 是 4.0.2，但 FlexRIC 需要 4.1 以上。
- 尚未證明可 import 的 `xapp_sdk` module 與 live E2 control path。
- Traffic runner 必須同時具備 UE data path 與 FlexRIC Python environment。
- 缺 receiver timestamp、iPerf result parser、Active-Time 與 HARQ exporters。
- 固定 Arm A baseline protocol 已核准，但 current runner 尚未實作。

## 3. 無 AI 工具的人工重建步驟

所有 repository commands 都從 repository root 執行。所有 generated runtime materials 都放在 `test_log/`，不可放入本文件目錄。

### Step 1：檢查 Host

```bash
python3 --version
cmake --version
ninja --version
swig -version
iperf --version
iperf --help | grep -E -- '--txstart-time|--trip-times|--reverse'
docker compose version
```

Arm B 需要 SWIG 4.1 以上與可 import 的 FlexRIC module：

```bash
python3 -c 'import xapp_sdk; print(xapp_sdk.__file__)'
grep '^E2_AGENT:' cmake_targets/ran_build/build/CMakeCache.txt
```

若 module 無法 import，或 campaign 使用的 build 沒有啟用 `E2_AGENT`，請停止並記錄 `[BLOCKED]`。

### Step 2：編譯受影響 Targets

```bash
cmake --preset default -DENABLE_TELNETSRV=ON
cmake --build --preset default --target nr-softmodem nr-uesoftmodem telnetsrv_ci -j2
```

### Step 3：執行 Focused Tests

```bash
cmake --preset tests
cmake --build --preset tests --target test_nr_ue_drx test_nr_redcap_rc_ctrl test_nr_gnb_drx -j2
ctest --test-dir cmake_targets/ran_build/build_test \
  --output-on-failure \
  -R '^(test_nr_ue_drx|test_nr_redcap_rc_ctrl|test_nr_gnb_drx)$'

python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/test_adaptive_drx.py -v
```

任何 focused test 失敗時都不可繼續執行 runtime campaign。

### Step 4：產生 Deterministic Traces

```bash
RUN_ID=$(date +%F_%H-%M-%S)
RUN_DIR="test_log/runtime_logs/adaptive_drx_${RUN_ID}"
START_EPOCH_US=$(date -d '+10 minutes' +%s%6N)
mkdir -p "$RUN_DIR"

python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/adaptive_drx.py generate \
  --output-dir "$RUN_DIR" \
  --trace-seed 41 \
  --profile-seed 73 \
  --start-epoch-us "$START_EPOCH_US"

wc -l "$RUN_DIR"/adaptive_drx_*_trace.csv
sha256sum "$RUN_DIR"/adaptive_drx_*_trace.csv
```

每個 trace 應有 331 行：一行 header 與 330 筆 arrivals。每個 sequential campaign 都要重新產生 manifest，確保 absolute `--txstart-time` 仍在未來；使用相同 seeds 可維持相同 interval sequence。

### Step 5：啟動 Runtime Services 與 Log Collection

使用本專案 RFsim topology 啟動 CN5G、nearRT-RIC、gNB 與一個 RedCap UE。gNB 必須包含：

```text
--telnetsrv --telnetsrv.shrmod ci --telnetsrv.listenaddr 192.168.70.140 --telnetsrv.listenport 9091
```

確認 UE 已建立 PDU session，而且 campaign process 同時可連線 UE data path 與 FlexRIC Python module。在接收端 data-network namespace 啟動 persistent iPerf2 server：

```bash
iperf -s -u -i 1
```

在另一個 terminal 持續保存 combined gNB/UE log 到 `$RUN_DIR/runtime.log`。Docker Compose log 的完整命令請使用[詳細人工重建指南](../Doc/adaptive_drx_ab_manual_reproduction.zh-TW.md)。

### Step 6：Pre-apply Baseline

從目前 gNB evidence 找出 connected UE C-RNTI。透過 telnet CI command 套用 `drx-320-10`、offset 0，並停用 DRX Command：

```text
ci trigger_drx_policy 1 320 10 0 0 0x1234
```

將 `0x1234` 替換成 live C-RNTI。Log 出現 matching gNB applied marker 與 versioned RRC completion success 前，不可開始傳送 traffic。

下一版 fixed-baseline protocol 在整個 Arm A 都保留此 profile。Current runner 尚無法做到這件事，仍會在每個 window 更換固定 seed 的 Arm A profiles。Runner 更新前，應在此停止新的 protocol，或只執行並明確標示為 legacy v1 seeded-baseline procedure。

執行 Arm B 前，必須證明下一個 FlexRIC-generated request ID 大於 baseline policy version，且 gNB 具有 rollback state；否則記錄 `[BLOCKED]`。

### Step 7：執行四個 Campaigns

依序一次執行一個 campaign：

1. `arm-a-dl`
2. `arm-a-ul`
3. `arm-b-dl`
4. `arm-b-ul`

每個 campaign 都使用新的 future trace 與乾淨的 gNB policy state。Arm A 與 Arm B 的 exact command templates 維護在[詳細人工重建指南](../Doc/adaptive_drx_ab_manual_reproduction.zh-TW.md)第 5.4 與 5.5 節。

每個 command 都必須提供：

- generated manifest；
- campaign ID；
- persistent iPerf2 server address；
- `$RUN_DIR` 內的 command-plan JSONL 與 metrics CSV path；
- `--execute` 與正確的 C-RNTI 或 RRC UE ID；
- combined runtime log 與大於零的 control timeout。

除非同一個 runner environment 可以 import `xapp_sdk` 並透過 UE data path 傳送 traffic，否則不可執行 Arm B。

### Step 8：收集 Evidence

每個 campaign 都保留下列 artifacts：

- manifest、trace CSV、trace hashes、command-plan JSONL 與 metrics CSV；
- combined gNB/UE logs 與 xApp/nearRT-RIC logs；
- 與每個 scheduled arrival 對應的 receiver-side first UDP packet timestamps；
- parsed iPerf goodput、loss 與 jitter；
- UE Active-Time slot counts 與 total observed slots；
- DL/UL HARQ retransmission counters；
- request、ACK、dApp decision、gNB apply、UE configuration 與 RRC completion markers。

目前 source 尚未輸出 receiver timestamp、Active-Time 或 campaign HARQ measurements，也沒有解析所有 iPerf metrics。真正的 collectors 完成前，這些 fields 保持 `N/A`，runtime Gate 維持 `BLOCKED`。

### Step 9：驗證每個 Campaign

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/check_campaign.py \
  --manifest "$RUN_DIR/adaptive_drx_campaign_manifest_v1.json" \
  --campaign-id arm-b-dl \
  --metrics-csv "$RUN_DIR/arm-b-dl.metrics.csv" \
  --log "$RUN_DIR/runtime.log"
```

對四個 campaigns 使用對應的 ID 與 metrics file 重複執行。

- `PASS`：300 筆 scored rows、profile/version correlation 與所有 required markers 都存在。
- `PARTIAL`：已有 artifacts，但 row、version、profile 或 marker 不完整。
- `BLOCKED`：缺少 prerequisite 或 external runtime artifact。
- `FAIL`：提供的 evidence 無效或互相矛盾。

四個 campaign checks 全部通過前，不可計算 Arm A/B comparison。

### Step 10：處理 Reject 與 Rollback

發生 reject 或 timeout 時，保留目前 30-sample window 與全部 artifacts，不可清除 predictor evidence。

RRC failure 的 automatic handling 可以恢復前一個 applied profile，並輸出 `[RedCap DRX][rollback]`。目前沒有 public campaign 或 telnet command 可呼叫 explicit rollback API，不可自行發明命令。需要 operator recovery 時，停止 campaign 並從乾淨 topology 重新開始。

## 4. 發布檢查表

- 記錄兩個 seeds、start epoch、profile table、software revision、build options 與 topology。
- DL 與 UL 結果分開保存與說明。
- 清楚區分 current implementation behavior 與下一版 fixed-baseline protocol。
- Missing metrics 使用 `N/A`，不完整 evidence 使用 PARTIAL 或 BLOCKED。
- RFsim Active-Time 與 PDCCH values 只能稱為 behavior proxies，不可稱為實體耗電量測。
- 從 Gate report 連結 final evidence package，不可將 generated logs 複製進本目錄。
