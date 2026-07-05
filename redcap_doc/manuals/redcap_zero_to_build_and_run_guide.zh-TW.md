# RedCap 從零編譯到 29 UE 執行指南

## 目標
- 從 repository root 開始操作。
- 編譯本機 gNB 與 NR UE binary。
- 重建 RFsim 會使用的本地 Docker images。
- 執行 29 UE RedCap/mMTC RFsim 驗證。
- 用 summary markers 判斷結果，不先讀 raw logs。

## 適用範圍
- 這份文件給第一次使用本 RedCap/OAI workspace 的使用者。
- 文件中的指令是一般 shell 指令，不使用 Codex 內部 wrapper。
- 除非步驟中特別 `cd`，否則所有指令都預設從 repository root 執行。

## 1. 進入專案

```bash
cd /home/tonywang/OAI/Red_cap_openairinterface5g
```

先確認主要入口存在：

```bash
ls AGENTS.md README.md redcap_interface/README.md redcap_doc/manuals/README.md
```

## 2. 檢查必要服務

RFsim 需要 Docker 與 Docker Compose：

```bash
docker ps
docker compose version
```

確認 RedCap RFsim 腳本會使用的本機 CN5G compose：

```bash
ls /home/tonywang/OAI/oai-cn5g/docker-compose.yaml
```

如果這個檔案不存在，先停止。需要先恢復本機 CN5G workspace，才能跑 29 UE 測試。

## 3. 驗證 RedCap 介面

這是非侵入式檢查，不會啟動 RFsim。

```bash
bash redcap_interface/validate_redcap_interface.sh
```

預期結果：

- Shell entrypoints 存在。
- Python helpers 可以正確 parse。
- 必要 RedCap interface paths 存在。

## 4. 安裝或更新 OAI 編譯依賴

如果這台機器還沒編譯過 OAI，先使用 upstream OAI wrapper：

```bash
cd cmake_targets
./build_oai -I --install-optional-packages -w USRP
cd ..
```

注意：

- 這一步可能需要 package-manager 權限。
- 每台機器通常只需要跑一次；系統依賴缺失時再跑。
- 更完整的 upstream build 細節請看 `doc/BUILD.md`。

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
- build artifacts 會在 `cmake_targets/ran_build/build/` 底下。

## 6. 重建本地 Docker images

RFsim containers 使用本地 images，所以 C code 改完後要重建：

```bash
bash redcap_interface/redcap_rebuild_local_oai_images.sh
```

這一步應該會更新：

- `oai-gnb:latest`
- `oai-nr-ue:latest`

重建後檢查 gNB image：

```bash
bash redcap_interface/redcap_inspect_gnb_image.sh
```

## 7. 執行 29 UE RedCap RFsim 驗證

這個指令會跑 29 UE stage scan，不啟用 iperf。它會檢查 attach、PDU session、tunnel 與 forward ping。

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

找出最新 summary log：

```bash
ls -1t test_log/compiler_logs/mmtc_stage_scan_*_summary.log | head -n 1
```

印出內容：

```bash
cat test_log/compiler_logs/<summary-log-name>
```

通過時應包含：

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

## 9. 開啟日常操作選單

build path 確認可用後，日常 RedCap/mMTC 操作使用：

```bash
bash redcap_interface/mmtc.menu.bash
```

常見用途：

| 需求 | 路由 |
|---|---|
| 檢查目前 mount 的 gNB config | `mmtc.menu.bash` daily menu |
| 設定 RedCap RX mode | `mmtc.menu.bash` daily menu |
| 開關 256QAM flags | `mmtc.menu.bash` daily menu |
| 設定 DRX/eDRX/PSM knobs | `mmtc.menu.bash` daily menu |
| Paper/demo display 工作 | `bash redcap_interface/mmtc.display.bash` |

## 10. Troubleshooting

| 現象 | 第一個檢查點 | 修正方向 |
|---|---|---|
| `docker ps` permission denied | Docker group 或 daemon | 先修好 Docker 權限再跑 RFsim |
| CN5G compose 不存在 | `/home/tonywang/OAI/oai-cn5g/docker-compose.yaml` | 恢復本機 CN5G workspace |
| CMake configure 失敗 | `doc/BUILD.md` 與 dependency install 步驟 | 重跑 `build_oai -I` 依賴安裝 |
| build 出現 ccache temp path 錯誤 | ccache 暫存路徑 | 使用 `CCACHE_DIR=/tmp/ccache CCACHE_TEMPDIR=/tmp/ccache-tmp` 重試 |
| 29 UE summary 沒有 PASS | 最新 `mmtc_stage_scan_*_summary.log` | 依序看 gNB restart、UE attach、tunnel、ping markers |

## 下一步閱讀

- RedCap operator routes：`redcap_interface/README.md`
- Manual index：`redcap_doc/manuals/README.md`
- L1/L2 protocol guide：`redcap_doc/specs/redcap_l1_l2_protocol_guide.md`
- Function lookup：`redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md`
