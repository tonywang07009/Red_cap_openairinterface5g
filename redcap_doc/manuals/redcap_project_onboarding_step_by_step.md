# RedCap 專案接手教學

## 0. 使用原則
- 一次只做一層：先能跑，再看 log，再改函式。
- 不先讀舊 raw log；先讀 `AGENTS.md`、本文件、`redcap_library/README.md`。
- 有疑問先定位到「路徑、腳本、函式、驗證」其中一類。

## 1. 進入專案
```bash
cd /home/tonywang/OAI/Red_cap_openairinterface5g
```

先確認三個入口：
```bash
ls AGENTS.md redcap_interface/README.md redcap_doc/manuals/README.md
bash redcap_interface/validate_redcap_interface.sh
```

## 2. 認識資料夾分工
| 路徑 | 用途 |
|---|---|
| `redcap_interface/` | RedCap 操作介面與 shell 入口 |
| `ci-scripts/` | OAI CI、compose、Python/C helper、yaml/xml 資產 |
| `redcap_doc/` | paper、spec、checklist、manual、函式查詢 |
| `redcap_library/` | 已整理可重用的 config、report、runtime evidence |
| `test_log/` | 暫存 build/runtime/process log |

## 3. 依賴項檢查
先跑非侵入檢查：
```bash
bash redcap_interface/validate_redcap_interface.sh
```

確認 Docker 可用：
```bash
docker ps
docker compose version
```

確認本機 CN compose：
```bash
ls /home/tonywang/OAI/oai-cn5g/docker-compose.yaml
```

## 4. 編譯與映像
若只改 C 函式，先編譯對應 target：
```bash
cmake --preset default
cmake --build --preset default --target nr-softmodem
cmake --build --preset default --target nr-uesoftmodem
```

若 runtime 容器要吃到 C 改動，再重建本地映像：
```bash
bash redcap_interface/redcap_rebuild_local_oai_images.sh
```

重建後檢查 gNB 映像 marker：
```bash
bash redcap_interface/redcap_inspect_gnb_image.sh
```

## 5. 操作用戶介面
開啟互動式 runtime menu：
```bash
bash redcap_interface/mmtc.menu.bash
```

常用選項：
| 選項 | 用途 |
|---|---|
| `1` | 檢查 gNB config mount |
| `2` | 單 UE baseline，不跑 iperf |
| `3` | UL UDP iperf |
| `5` | 顯示最新 iperf log |
| `13` | 切到 106PRB |
| `14` | 切到 51PRB |
| `15` | RedCap vs non-RedCap live probe |

## 6. Paper 07 類測試
使用 51PRB profile：
```bash
bash redcap_interface/mmtc.menu.bash
# choose 14, then choose 2 or 3
```

非互動式 smoke 範例：
```bash
env MMTC_TOTAL_UES=29 \
    MMTC_SAMPLE_UES=1 \
    MMTC_IPERF_SAMPLE_UES=1 \
    MMTC_IPERF_ENABLE=1 \
    MMTC_IPERF_UDP=1 \
    MMTC_IPERF_RATE=35M \
    MMTC_IPERF_DURATION=60 \
    MMTC_FORWARD_PING_MODE=parallel \
    MMTC_RUN_REVERSE_PING=0 \
    MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 \
    bash redcap_interface/redcap_mmtc_smoke_validation.sh
```

## 7. 修改函式前的定位流程
1. 先查 `redcap_doc/function_reference/redcap_l1_l3_function_lookup.md`。
2. 找到函式所在檔案。
3. 用 `symdex` 查 callers/callees。
4. 修改最小範圍。
5. 跑最近的 unit test 或 runtime smoke。

## 8. 常見修改入口
| 想改的能力 | 先看檔案 |
|---|---|
| FR1 20MHz / 51PRB 限制 | `openair1/PHY/INIT/nr_parms.c` |
| gNB RedCap config parsing | `openair2/GNB_APP/gnb_config.c` |
| SIB1 RedCap BWP / RACH | `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` |
| Msg1/Msg2 RedCap RA | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c` |
| UE 讀 RedCap initial BWP | `openair2/LAYER2/NR_MAC_UE/nr_ue_redcap_bwp.c` |
| UE capability injection | `openair2/RRC/NR_UE/rrc_ue_redcap.c` |
| UE YAML RedCap config | `openair3/UICC/nr_redcap_config.c` |
| xApp UL PRB cap | `openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc_redcap.c` |

## 9. 驗證順序
```bash
bash redcap_interface/validate_redcap_interface.sh
bash -n redcap_interface/*.sh redcap_interface/*.bash
git diff --check -- redcap_interface redcap_doc AGENTS.md
```

若改 C code：
```bash
cmake --build --preset default --target nr-softmodem
cmake --build --preset default --target nr-uesoftmodem
```

若改 runtime 行為：
```bash
bash redcap_interface/mmtc.menu.bash
```

## 10. 紀錄規則
- 成功且可重用的流程，寫入 `redcap_doc/manuals/` 或 active project analysis。
- raw log 暫存於 `test_log/`。
- 可重用 evidence 推到 `redcap_library/`。
- 失敗但指出 simulator 修改方向，寫入 validation/debug item。
