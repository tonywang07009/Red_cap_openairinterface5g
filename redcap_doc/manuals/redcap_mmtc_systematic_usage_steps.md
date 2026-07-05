# RedCap mMTC 系統化使用步驟

## 1. 文件目的
- 固定短期驗收基線為：[50 UE 穩定可 ping]。
- 提供可重複執行的驗證流程，避免只靠單次結果判斷。

## 2. 適用範圍
- Repo：`Red_cap_openairinterface5g`
- 主要腳本：
  - `redcap_interface/redcap_mmtc_stage_scan.sh`
  - `redcap_interface/redcap_mmtc_smoke_validation.sh`

## 3. 前置條件
- Docker / docker compose 可正常操作。
- 可存取以下目錄：
  - `test_log/compiler_logs/`
  - `test_log/runtime_configs/`
- 建議先確認：
  - `bash -n redcap_interface/redcap_mmtc_stage_scan.sh`
  - `bash -n redcap_interface/redcap_mmtc_smoke_validation.sh`

## 4. 基線定義（短期驗收）
- 基線名稱：[MMTC_BASELINE_50]
- 驗收條件（需同時滿足）：
  - `sample=50`
  - `running=50`
  - `attach=50`
  - `pdu=50`
  - `tun=50`
  - `forward_ping_ok=50`
  - `gnb_restart=0`
  - `failures=0`

## 5. 標準執行流程

### 步驟 1：執行第 1 輪基線驗證
```bash
env MMTC_STAGE_LIST=50 \
    MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 \
    MMTC_UE_START_GAP=0 \
    MMTC_GNB_WARMUP=10 \
    MMTC_SLEEP_AFTER_UP=25 \
    bash redcap_interface/redcap_mmtc_stage_scan.sh
```

### 步驟 2：讀取第 1 輪摘要
```bash
ls -1t test_log/compiler_logs/mmtc_stage_scan_*_summary.log | head -n 1
cat <上一步輸出的summary.log>
```

### 步驟 3：執行第 2 輪基線驗證（重現性）
```bash
env MMTC_STAGE_LIST=50 \
    MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 \
    MMTC_UE_START_GAP=0 \
    MMTC_GNB_WARMUP=10 \
    MMTC_SLEEP_AFTER_UP=25 \
    bash redcap_interface/redcap_mmtc_stage_scan.sh
```

### 步驟 4：讀取第 2 輪摘要
```bash
ls -1t test_log/compiler_logs/mmtc_stage_scan_*_summary.log | head -n 2
cat <第2輪summary.log>
```

### 步驟 5：判定是否通過基線
- 兩輪都達到第 4 節所有驗收條件：判定 [PASS]。
- 任一輪未達：判定 [FAIL]，進入第 7 節排查。

## 6. 進階階段測試（基線通過後）
- 建議順序：`52 -> 56 -> 60`
- 範例：
```bash
env MMTC_STAGE_LIST=52,56,60 \
    MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 \
    MMTC_UE_START_GAP=0 \
    MMTC_GNB_WARMUP=10 \
    MMTC_SLEEP_AFTER_UP=25 \
    bash redcap_interface/redcap_mmtc_stage_scan.sh
```

## 7. 常見失敗與排查
- [Docker 權限錯誤]
  - 現象：`permission denied while trying to connect to docker API`
  - 處置：確認使用者權限與 docker daemon 狀態。

- [gNB 重啟]
  - 現象：`gnb_restart > 0` 或 log 出現 `Main child exited with signal 'Killed'`
  - 先看：
    - `test_log/compiler_logs/mmtc_smoke_*_gnb.log`
    - `test_log/compiler_logs/mmtc_smoke_*_gnb_state.log`

- [UE TUN / ping 未達標]
  - 現象：`tun < sample` 或 `forward_ping_ok < sample`
  - 先看：
    - `test_log/compiler_logs/mmtc_smoke_*_ue*_state.log`
    - `test_log/compiler_logs/mmtc_smoke_*_ue*_markers.log`

## 8. 已驗證參考（2026-04-21）
- 以下兩輪已達 [MMTC_BASELINE_50]：
  - `test_log/compiler_logs/mmtc_stage_scan_2026-04-21_23-36-58_summary.log`
  - `test_log/compiler_logs/mmtc_stage_scan_2026-04-21_23-40-02_summary.log`
