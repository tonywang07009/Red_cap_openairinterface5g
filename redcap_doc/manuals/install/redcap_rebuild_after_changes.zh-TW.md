# RedCap 修改後重建流程

[English](./redcap_rebuild_after_changes.en.md) | [繁體中文](./redcap_rebuild_after_changes.zh-TW.md)

## 目標

修改 OAI C code、RedCap scripts、xApp/rApp/dApp integration files、configs 或 local libraries 後，使用這份流程重建與驗證。

## 1. 判斷修改類型

| 修改類型 | 最小重建或檢查 |
|---|---|
| 只有文件 | Static documentation gate 與 `git diff --check`。 |
| Shell 或 Python interface script | `bash redcap_interface/validate_redcap_interface.sh`。 |
| gNB C code | 編譯 `nr-softmodem`，重建本地 RFsim images，再跑 29 UE marker gate。 |
| NR UE C code | 編譯 `nr-uesoftmodem`，重建本地 RFsim images，再跑 29 UE marker gate。 |
| gNB/UE 共用 C code | 兩個 modem targets 都編譯，然後重建 images。 |
| xApp control source | 使用 `REDCAP_CTRL_BUILD_ONLY=1 bash redcap_interface/redcap_send_ul_prb_control.sh` build。 |
| RFsim YAML 或 CN5G overlay | 先驗證 interface，再透過 menu 或 stage scan 重新產生 overlay，最後跑 gate。 |

## 2. Preflight

從 repository root 執行：

```bash
pwd
bash redcap_interface/validate_redcap_interface.sh
```

如果 interface validator 失敗，先修正這個問題，再重建 image 或執行 RFsim。

## 3. 重建 C targets

如果修改 gNB：

```bash
cmake --build --preset default --target nr-softmodem
```

如果修改 NR UE：

```bash
cmake --build --preset default --target nr-uesoftmodem
```

如果修改共用 code：

```bash
cmake --build --preset default --target nr-softmodem
cmake --build --preset default --target nr-uesoftmodem
```

如果出現 ccache 暫存路徑錯誤：

```bash
CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp cmake --build --preset default --target nr-softmodem
CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp cmake --build --preset default --target nr-uesoftmodem
```

## 4. 重建本地 RFsim images

任何需要進 container 的 C build 完成後，執行：

```bash
bash redcap_interface/redcap_rebuild_local_oai_images.sh
bash redcap_interface/redcap_inspect_gnb_image.sh
```

預期更新 images：

- `oai-gnb:latest`
- `oai-nr-ue:latest`

## 5. 重建 RedCap xApp control binary

如果修改 `ci-scripts/redcap_ul_prb_ctrl_xapp.c` 或 FlexRIC control integration，執行：

```bash
REDCAP_CTRL_BUILD_ONLY=1 bash redcap_interface/redcap_send_ul_prb_control.sh
```

預期輸出：

- Build log 在 `test_log/build_logs/`。
- Runtime binary 在 `test_log/runtime_bins/redcap_ul_prb_ctrl_xapp`。

若要做 live control test，需要 RFsim 與 FlexRIC 已經啟動。再執行公開 control scripts：

```bash
bash redcap_interface/redcap_send_ul_prb_control.sh
bash redcap_interface/redcap_verify_ul_prb_control.sh
```

## 6. 執行 29 UE marker gate

使用與新手流程相同的 stage scan：

```bash
env MMTC_TOTAL_UES_TARGET=29 \
    MMTC_STAGE_LIST=29 \
    MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 \
    MMTC_FORWARD_PING_MODE=parallel \
    MMTC_RUN_REVERSE_PING=0 \
    MMTC_IPERF_ENABLE=0 \
    MMTC_UE_START_GAP=3 \
    MMTC_GNB_WARMUP=10 \
    MMTC_SLEEP_AFTER_UP=25 \
    bash redcap_interface/redcap_mmtc_stage_scan.sh
```

通過 markers：

```text
sample=29
running=29
attach=29
pdu=29
tun=29
forward_ping_ok=29
gnb_restart=0
failures=0
```

## 7. 記錄 evidence

完成重建後，記錄：

- 修改範圍。
- Build command。
- Image rebuild command。
- Stage scan summary path。
- Pass/fail markers。
- 任何 `[Needs Verification]` spec mapping。
