# RedCap 入門建置與 29 UE 重現

[English](./redcap_begin_from_zero.en.md) | [繁體中文](./redcap_begin_from_zero.zh-TW.md)

## 目標

- 對象：尚未操作 dApp/xApp 控制路徑的新手。
- 從 repository root 開始操作。
- 驗證公開 RedCap 操作介面。
- 編譯本機 gNB 與 NR UE binaries。
- 重建本機 RFsim Docker images。
- 執行 29 UE RedCap/mMTC RFsim 驗證。
- 用 summary markers 判斷結果，不用 raw log 長度判斷。
- 第一個 layer 失敗就停止；本教學不宣稱 scheduler 或 dApp/xApp 效果。

## 前置需求

| 需求 | 檢查 | 停止條件 |
|---|---|---|
| OAI build 支援的 Ubuntu host | `lsb_release -ds` | Host 不支援或沒有 package-manager 權限 |
| Docker 與 Compose | `docker ps`、`docker compose version` | 任一指令失敗 |
| Repository 管理的 CN5G | `test -f oai-cn5g/docker-compose.yaml` | Compose 檔案不存在 |
| 足夠的 log 空間 | `df -h test_log` | Filesystem 無法保存 build 與 runtime log |

## 1. 進入專案

```bash
cd /home/tonywang/OAI/Red_cap_openairinterface5g
pwd
```

預期路徑：

```text
/home/tonywang/OAI/Red_cap_openairinterface5g
```

確認公開入口檔案：

```bash
ls README.md README.zh-TW.md redcap_interface/README.md redcap_doc/manuals/install/README.zh-TW.md
```

## 2. 檢查主機服務

RFsim 需要 Docker 與 Docker Compose：

```bash
docker ps
docker compose version
```

確認 RedCap RFsim 腳本會使用、由 repository 管理的 CN5G compose：

```bash
ls oai-cn5g/docker-compose.yaml
```

如果 CN5G 檔案不存在，先停止。請先恢復 repository 管理的 CN5G runtime，再執行 29 UE 驗證。

## 3. 驗證 RedCap 介面

這個檢查不應啟動 RFsim。

```bash
bash redcap_interface/validate_redcap_interface.sh
```

預期結果：

- Public shell entrypoints 存在。
- Python helpers 可以 parse。
- 必要 RedCap interface paths 存在。
- FlexRIC 與 RFsim scenario files 存在。

## 4. 安裝或更新 OAI 依賴

如果這台機器還沒編譯過 OAI，先使用 upstream OAI wrapper：

```bash
cd cmake_targets
./build_oai -I --install-optional-packages -w USRP
cd ..
```

注意：

- 這一步可能需要 package-manager 權限。
- 每台機器通常只需要跑一次；系統依賴缺失時再跑。
- 上游細節請看 `doc/BUILD.md`。

## 5. 設定並編譯 gNB + NR UE

設定 default build tree：

```bash
cmake --preset default
```

編譯兩個 RFsim modem target：

```bash
cmake --build --preset default --target nr-softmodem
cmake --build --preset default --target nr-uesoftmodem
```

預期結果：

- `nr-softmodem` 編譯成功。
- `nr-uesoftmodem` 編譯成功。
- Build artifacts 會在 `cmake_targets/ran_build/build/` 底下。

如果出現 ccache 暫存路徑錯誤，用下列指令重試：

```bash
CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp cmake --build --preset default --target nr-softmodem
CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp cmake --build --preset default --target nr-uesoftmodem
```

## 6. 重建本地 RFsim images

RFsim containers 使用本地 images，因此 fresh build 後要重建：

```bash
bash redcap_interface/redcap_rebuild_local_oai_images.sh
```

這一步應更新：

- `oai-gnb:latest`
- `oai-nr-ue:latest`

檢查 gNB image：

```bash
bash redcap_interface/redcap_inspect_gnb_image.sh
```

## 7. 執行 29 UE RFsim 驗證

這個 stage scan 不啟用 iperf，會檢查 attach、PDU session、tunnel 與 forward ping：

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

## 8. 讀取 summary

找最新 summary log：

```bash
ls -1t test_log/compiler_logs/mmtc_stage_scan_*_summary.log | head -n 1
```

印出 summary：

```bash
cat test_log/compiler_logs/<summary-log-name>
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

保留 `test_log/compiler_logs/` 內的 summary 與相同 timestamp stage log。Attach、PDU、TUN 與 ping 是不同驗收邊界；任一數量不足都不是 PASS。

## 9. 依第一個失敗點查詢

| 第一個失敗邊界 | 下一個檢查位置 | 不可宣稱 |
|---|---|---|
| CN services | CN Compose output 與 AMF/SMF/UPF logs | RF 或 RRC failure |
| RF synchronization 或 RA | 相同 timestamp 的 gNB 與 UE logs | attach success |
| RRC attach | gNB/UE RRC markers | PDU 或 tunnel success |
| PDU session | SMF/UPF 與 UE NAS logs | TUN readiness |
| TUN 或 forward ping | 每個 UE 的 tunnel 與 ping evidence | 完成 29 UE 重現 |

輸入會在 runtime 前檢查：UE 清單不可為空、index 不可重複、有效 service index 為 `1..56`。本教學執行前 29 個 service；UE `0`、負數、重複 index 與 UE `57` 都是無效輸入。

## 10. 下一步

29 UE path 可用後，開啟日常操作選單：

```bash
./mmtc.menu.bash
```

接著執行 [56 UE 實驗設定檔與 dApp/xApp 教學](../../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/gate_e_core56_manual_reproduction.zh-TW.md)。修改後重建請看 [redcap_rebuild_after_changes.zh-TW.md](./redcap_rebuild_after_changes.zh-TW.md)。
