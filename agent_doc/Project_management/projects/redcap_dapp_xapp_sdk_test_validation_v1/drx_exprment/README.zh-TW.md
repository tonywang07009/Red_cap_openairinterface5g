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

### 1.4 已實作的 Baseline Protocol

目前 A/B protocol 使用 `drx-320-10` 作為固定 Arm A baseline；Traffic 前只 pre-apply 一次，300 筆 scored arrivals 全程不變。Runner 已實作此行為。Fresh Arm B state 會先用保留的 bootstrap version 0 commit 同一 profile；每個 scored window 分別記錄正值的 xApp-local `e42_request_id`，並將 Near-RT RIC 的 network request ID correlation 為 `policy_version`。重用已配置的 DRX state 會被拒絕。

### 1.5 必要量測與宣稱邊界

| 量測 | 用途 | 目前支援狀態 |
|---|---|---|
| Applied profile 與 marker chain | 證明 control 已生效 | Logs/checker 已實作 |
| Delivery success | 確認每個 arrival 有 scored record | 需要 parsed receiver report 且實際收到 packet |
| First receive latency | 量測 wake-to-delivery 行為 | Filtered tcpdump -> `receive-csv` -> checker |
| iPerf goodput/loss/jitter | 發現 traffic degradation | 已解析到 metrics CSV |
| UE DRX Active-Time slot ratio | 與能源相關的行為 proxy | `ciUE drx_stats` atomic UE counter |
| DL/UL HARQ retransmissions | 解釋 delivery 下降或 Active Time 延長 | RNTI-specific first/last log delta |
| Policy apply latency | 量化 RRC control overhead | Timestamped staged-to-RRC-complete correlation |

RFsim 無法量測電流、瓦特、焦耳、電池壽命或 receiver-chain power states。Active-Time 與 PDCCH-monitoring ratio 只能稱為 behavior proxies。

## 2. 目前實驗結果說明

### 2.1 Evidence 狀態

| Surface | 目前結果 |
|---|---|
| gNB 與 UE softmodem builds | PASS |
| Telnet CI DRX control module | PASS |
| Focused UE DRX、RC 與 gNB DRX CTest targets | PASS，3/3 |
| Trace、predictor、window、receiver 與 checker tests | PASS，16/16 加 evidence 3/3 |
| C dApp 與 C xApp self-checks | PASS |
| 產生的 Python FlexRIC module | Repository SWIG 4.1.1 + Python 3.12 PASS |
| 隔離的 E2 build path | `E2_AGENT=ON`，gNB/UE、`telnetsrv_ci`、`ciUE` PASS |
| 單 UE RFsim C-DRX smoke | PASS：attach/PDU/TUN/ping、E2 Setup、Arm A apply/RRC complete、UE counters、UL/DL bursts |
| 四個 RFsim campaigns | PASS，1200/1200 scored arrivals |

Live Python xApp discovery 回傳 `nodes 1`。每個 Arm B campaign 都完成十次
E2 CONTROL request 與 RRC reconfiguration，沒有 reject、rollback 或 timeout。

### 2.2 Scored Population

| Campaign | Planned scored | Evidenced scored | 結果 |
|---|---:|---:|---|
| `arm-a-dl` | 300 | 300 | PASS |
| `arm-b-dl` | 300 | 300 | PASS |
| `arm-a-ul` | 300 | 300 | PASS |
| `arm-b-ul` | 300 | 300 | PASS |
| **Total** | **1200** | **1200** | **PASS** |

最終可證明的 scored population 是 `1200/1200`，trace seed 為 `41`。

| Metric | Arm A DL | Arm B DL | Arm A UL | Arm B UL |
|---|---:|---:|---:|---:|
| First-receive median / p95 ms | 59.0125 / 67.991 | 58.891 / 71.028 | 5.2345 / 5.768 | 5.217 / 5.853 |
| Active-Time ratio | 0.075978 | 0.029380 | 0.078937 | 0.034690 |
| Mean goodput Mbps | 10.229333 | 10.232600 | 9.749533 | 9.740133 |
| Mean loss percent | 3.4 | 3.4 | 0.0 | 0.0 |
| DL / UL HARQ retransmissions | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 3 |

Canonical evidence 位於
`test_log/runtime_logs/adaptive_drx_2026-07-13_full_ab/` 的
`arm-a-dl-run2`、`arm-b-dl-run7`、`arm-a-ul-run1` 與 `arm-b-ul-run1`。
先前 Arm B/DL attempts 因 UE counters 無效、timeout 或不完整而排除。耗電不列入
本次驗收；本報告只確認 DRX uplink 與 downlink 行為完成。

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
PYTHONPATH=/tmp/flexric-adaptive-drx/examples/xApp/python3 \
  python3 -c 'import xapp_sdk; print(xapp_sdk.__file__)'
grep '^E2_AGENT:' /tmp/oai-e2-agent-build/CMakeCache.txt
```

若 module 無法 import，或 campaign 使用的 build 沒有啟用 `E2_AGENT`，請停止並記錄 `[BLOCKED]`。

### Step 2：編譯受影響 Targets

```bash
cmake -S . -B /tmp/oai-e2-agent-build -GNinja -DE2_AGENT=ON -DENABLE_TELNETSRV=ON
cmake --build /tmp/oai-e2-agent-build \
  --target nr-softmodem nr-uesoftmodem telnetsrv_ci telnetsrv_ciUE -j2
```

### Step 3：執行 Focused Tests

```bash
cmake --preset tests
cmake --build --preset tests --target test_nr_ue_drx test_nr_redcap_rc_ctrl test_nr_gnb_drx -j2
ctest --test-dir cmake_targets/ran_build/build_test \
  --output-on-failure \
  -R '^(test_nr_ue_drx|test_nr_redcap_rc_ctrl|test_nr_gnb_drx)$'

python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/test_adaptive_drx.py -v
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/test_campaign_evidence.py -v
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
  --start-epoch-us "$START_EPOCH_US"

wc -l "$RUN_DIR"/adaptive_drx_*_trace.csv
sha256sum "$RUN_DIR"/adaptive_drx_*_trace.csv
```

每個 trace 應有 331 行。每個 sequential campaign 使用詳細指南的 `rebase`，保留完全相同 intervals 並配置 future timestamps。

### Step 5：啟動 Runtime Services 與 Log Collection

使用本專案 RFsim topology 啟動 CN5G、nearRT-RIC、gNB 與一個 RedCap UE。gNB 必須包含：

```text
--telnetsrv --telnetsrv.shrmod ci --telnetsrv.listenaddr 192.168.70.140 --telnetsrv.listenport 9091
```

重新建立 RFsim gNB 與 UE 時載入共用 UE CI telnet module，並在 330-arrival
run 開始前要求 DRX counter marker：

```bash
COMPOSE_DIR=ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap
export MMTC_UE_EXTRA_OPTIONS="--telnetsrv.shrmod ciUE"
docker compose -f "$COMPOSE_DIR/docker-compose.yml" \
  -f "$COMPOSE_DIR/docker-compose.mmtc.yml" \
  up -d --force-recreate --no-deps oai-gnb oai-nr-ue1
printf 'ciUE drx_stats\n' | nc -w 3 192.168.71.150 8091 \
  | grep -E '\[RedCap DRX\]\[UE stats\].*observed_slots=[0-9]+.*active_slots=[0-9]+'
```

必要的原始回應 marker 是 `[RedCap DRX][UE stats]`。

確認 UE 已建立 PDU session，而且 campaign process 同時可連線 UE data path
與 FlexRIC Python module。每個 campaign 啟動全新的 iPerf2 2.1.9 server，
使 server 與 UE client 使用相同版本：

```bash
docker run --rm --name adaptive-drx-iperf-server \
  --network oai-cn5g-traffic-net --ip 192.168.72.136 \
  --entrypoint /usr/bin/iperf oai-nr-ue:latest -s -u -i 1
```

讓它在整個 campaign 期間持續執行、保留 log，並在 traffic 前比對兩端
`iperf --version`。下一個 campaign 不可重用同一個 process。

在另一個 terminal 持續保存 combined gNB/UE log 到 `$RUN_DIR/runtime.log`。Docker Compose log 的完整命令請使用[詳細人工重建指南](../Doc/adaptive_drx_ab_manual_reproduction.zh-TW.md)。

### Step 6：讓 Runner Pre-apply Baseline

從目前 gNB evidence 找出 connected UE C-RNTI，並用 `--rnti` 傳給 runner。Runner 使用下列 local control surface：

```text
ci trigger_drx_policy 1 320 10 0 0 0x1234
```

將 `0x1234` 替換成 live C-RNTI。Log 出現 matching gNB applied marker 與 versioned RRC completion success 前，不可開始傳送 traffic。

Arm A 只 commit version 1 一次。Fresh-stack Arm B 使用 `ci bootstrap_drx 320 10 <rnti>` 建立保留 version 0。每個 adaptive request 必須回傳正值的本地 `e42_request_id`；runner 再要求較新的 network RIC request ID 與完整 gNB marker chain。

### Step 7：執行四個 Campaigns

依序一次執行一個 campaign：

1. `arm-a-dl`
2. `arm-b-dl`
3. `arm-a-ul`
4. `arm-b-ul`

每個 campaign 都使用新的 future trace 與乾淨的 gNB policy state。Arm A 與 Arm B 的 exact command templates 維護在[詳細人工重建指南](../Doc/adaptive_drx_ab_manual_reproduction.zh-TW.md)第 5.4 與 5.5 節。

每個 command 都必須提供：

- generated manifest；
- campaign ID；
- persistent iPerf2 server address；
- 以 `--bind-address` 傳入的 UE PDU-session address，例如 `10.0.0.2`；
- `$RUN_DIR` 內的 command-plan JSONL 與 metrics CSV path；
- `--execute` 與正確的 C-RNTI 或 RRC UE ID；
- combined runtime log 與大於零的 control/traffic timeouts。

Python 在 host 執行，使用詳細指南的 `--traffic-prefix` 讓 iPerf2 進入 UE container，並綁定 UE PDU-session address，避免 traffic 經 container `eth0` 繞過 `oaitun_ue1`。

### Step 8：收集 Evidence

每個 campaign 都保留下列 artifacts：

- manifest、trace CSV、trace hashes、command-plan JSONL 與 metrics CSV；
- combined gNB/UE logs 與 xApp/nearRT-RIC logs；
- 與每個 scheduled arrival 對應的 receiver-side first UDP packet timestamps；
- parsed iPerf goodput、loss 與 jitter；
- UE Active-Time slot counts 與 total observed slots；
- DL/UL HARQ retransmission counters；
- request、ACK、dApp decision、gNB apply、UE configuration 與 RRC completion markers。

Collectors 已 source-ready；真實 campaign 產生 metrics/receive CSVs、UE summary 與 RNTI-specific runtime logs 前，這些 fields 仍為 `N/A`。

### Step 9：驗證每個 Campaign

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/adaptive_drx/check_campaign.py \
  --manifest "$RUN_DIR/adaptive_drx_campaign_manifest_v1.json" \
  --campaign-id arm-b-dl \
  --metrics-csv "$RUN_DIR/arm-b-dl.metrics.csv" \
  --receive-csv "$RUN_DIR/arm-b-dl.receive.csv" \
  --summary-json "$RUN_DIR/arm-b-dl.summary.json" \
  --rnti 0x1234 \
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

- 記錄 trace seed、start epoch、profile table、software revision、build options 與 topology。
- DL 與 UL 結果分開保存與說明。
- 記錄固定 Arm A version 1 與 fresh-state Arm B bootstrap version 0。
- Missing metrics 使用 `N/A`，不完整 evidence 使用 PARTIAL 或 BLOCKED。
- RFsim Active-Time 與 PDCCH values 只能稱為 behavior proxies，不可稱為實體耗電量測。
- 從 Gate report 連結 final evidence package，不可將 generated logs 複製進本目錄。
