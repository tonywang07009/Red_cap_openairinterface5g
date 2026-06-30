# RedCap 從零開始安裝

[English](./redcap_begin_from_zero.en.md) | [繁體中文](./redcap_begin_from_zero.zh-TW.md)

## 目標

- 從 repository root 開始操作。
- 驗證公開 RedCap 操作介面。
- 編譯本機 gNB 與 NR UE binaries。
- 重建本機 RFsim Docker images。
- 執行 29 UE RedCap/mMTC RFsim 驗證。
- 用 summary markers 判斷結果，不用 raw log 長度判斷。

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

確認 RedCap RFsim 腳本會使用的本機 CN5G compose：

```bash
ls /home/tonywang/OAI/oai-cn5g/docker-compose.yaml
```

如果 CN5G 檔案不存在，先停止。請先恢復本機 CN5G workspace，再執行 29 UE 驗證。

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

## 9. 下一步

29 UE path 可用後，開啟日常操作選單：

```bash
bash redcap_interface/mmtc.menu.bash
```

修改後重建請看 [redcap_rebuild_after_changes.zh-TW.md](./redcap_rebuild_after_changes.zh-TW.md)。
