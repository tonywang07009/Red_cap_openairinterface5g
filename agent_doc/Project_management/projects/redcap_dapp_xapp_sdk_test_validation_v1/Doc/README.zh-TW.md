# RedCap dApp/xApp SDK 測試驗證

## Scope

- 本頁說明 RedCap dApp/xApp SDK slice 的測試方式。
- 主要參考來源是 `dev_refer/`。
- 靜態檢查不代表 56 UE / 5 MHz BWP runtime PASS。

## API / config behavior

| API | 語言 | 功能 | 目前證據 |
|---|---|---|---|
| `redcap_xapp_make_priority_hint` | C | 依 UL buffer 與權重建立單一 UE priority hint | 語法檢查目標 |
| `redcap_xapp_select_top_priority_hint` | C | 選出最高優先 UE；同分時使用較小 RNTI | 語法檢查目標 |
| `make_priority_hint` | Python | C priority hint builder 的 Python 對應版本 | self-test |
| `select_top_priority_hint` | Python | top UE 選擇的 Python 對應版本 | self-test |
| `redcap_dapp_guard_prb_allocation` | C | 驗證 5 MHz BWP profile、I/Q presence、PUCCH/PUSCH ratio intent | 語法檢查目標 |
| `redcap_dapp_guard_prb_allocation` | Python | dApp allocation guard 的 Python 對應版本 | self-test |

重要欄位：

- [RNTI]：UE 識別碼，不能為 0。
- [priority_weight]：xApp 輸出，dApp 會放進 decision metadata。
- [bwp_prbs]：runtime 推導出的 BWP PRB marker；在 5 MHz / 30 kHz SCS profile 下，本地 notes 預期約 `12` PRBs `[Needs Verification]`。
- [pucch_ratio_permille] / [pusch_ratio_permille]：permille 比例，總和不得超過 `1000`。
- [has_iq_samples]：dApp 必須有 I/Q observation 證據才允許 apply。

## Command usage

執行靜態驗證：

```bash
python3 agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/check_dapp_xapp_sdk_test_validation.py
```

執行 SDK contract 驗證：

```bash
python3 agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/dapp_xapp_sdk_contract_selftest.py
```

執行 OpenSpec 驗證：

```bash
openspec validate redcap-dapp-xapp-sdk-test-validation --strict
```

執行 Gate C E3 loopback dependency/runtime 檢查：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py
```

當 `dev_refer/dapp_dev_need/libe3` 沒有既有 loopback binary，或本機缺少必要 build 依賴時，Gate C 會回報 `blocked`；這不等於失敗，也不等於 PASS。

保存 Gate C configure 證據：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure
```

目前 configure 證據位於 `test_log/compiler_logs/gate_c_libe3_configure_2026-07-05_18-43-41.log`；目前 blocker 是離線 `tl::expected` target/cache 不可用，不是 `asn1c`。

若允許 network FetchContent，請使用乾淨 build directory：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure --allow-fetch --build-dir dev_refer/dapp_dev_need/libe3/build/redcap-gate-c-fetch
```

目前 fetch 證據位於 `test_log/compiler_logs/gate_c_libe3_configure_fetch_2026-07-05_18-46-35.log`；sandbox DNS 無法解析 `github.com`，且 escalation 因 workspace credits 不足被拒絕。

使用 project-local expected shim 執行 Gate C：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_c_e3_loopback_check.py --try-configure --use-local-expected-stub --try-build --build-dir dev_refer/dapp_dev_need/libe3/build/redcap-gate-c-local-expected
```

目前 Gate C runtime 證據：

- POSIX IPC/TCP loopback PASS：`test_log/compiler_logs/gate_c_libe3_runtime_test_role_pair_posix_2026-07-06_11-58-08.log`
- Full-loop latency PASS：`test_log/compiler_logs/gate_c_libe3_runtime_test_bench_full_loop_latency_2026-07-06_11-58-23.log`
- Total round-trip latency：p99 `183 us`，max `260 us`

執行 Gate D source readiness 檢查：

```bash
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py
```

啟用 marker 環境變數後，執行 Gate D RFsim marker 掃描：

```bash
cd ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap
GNB_REDCAP_CONFIG=../../conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml \
MMTC_N_RB_DL=106 \
OAI_REDCAP_DAPP_GATE_D_MARKER=1 <start gNB/UE RFsim command>
python3 -B agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/scripts/gate_d_rfsim_marker_check.py --gnb-log <gNB-log-path> --ue-log <UE-log-path> --require-runtime --require-bwp-mhz 5
```

Gate D source readiness 與 `nr-softmodem` build 證據位於 `test_log/build_logs/build_nr-softmodem_2026-07-06_gate-d-pucch-marker.log`。這代表 gNB ULSCH/PUSCH/PDCCH 路徑已在 `config_uldci()` 之後呼叫 dApp PRB guard，PUCCH FAPI 路徑也已在 `nr_configure_pucch()` 之後呼叫同一個 guard，且目前仍可 build；這不等於 RFsim runtime PASS。

目前 Gate D 5 MHz RFsim 證據：

- gNB log：`test_log/runtime_logs/gate_d_5mhz_gnb_2026-07-06_17-16-57.log`
- UE2 log：`test_log/runtime_logs/gate_d_5mhz_ue2_2026-07-06_17-16-57.log`
- gNB 已觀察到 `[RedCap RA][gNB Msg2 BWP selected]`，其中 `dl_bwp_size 12`、`ul_bwp_size 12`。
- UE2 已觀察到 `SIB1 RedCap initial BWP decision`，並套用 DL/UL BWP size `12`。
- 舊 log 也顯示 RedCap RA DCI bit-length 不一致：gNB `dci_bits 35`，UE `dci_bits 39`。
- source fix 已讓兩端在 RedCap Case B RA common DCI sizing 使用目前的 12 PRB DL BWP。
- Gate D 仍未 PASS，因為這次 runtime 在 RA/RAR/Msg3 階段停止，尚未出現 `[RedCap dApp Gate D][gNB MAC UL]` 與 `[RedCap dApp Gate D][gNB MAC PUCCH]` marker。

## Step-by-step recap

1. 確認本地 `dev_refer/` 參考資料存在。
2. 確認 xApp priority hint API 同時存在於 C 與 Python。
3. 確認 dApp PRB allocation API 同時存在於 C 與 Python。
4. 確認 `libe3` 與 I/Q saver 的 SWIG definition 檔存在。
5. 執行 SDK contract self-test。
6. 執行 Gate C E3 loopback checker。
7. 執行 Gate D source readiness checker。
8. Gate D-E 在 RFsim runtime 證據出現前都維持 pending。

## Example logic

- xApp 讀取 UE metrics。
- xApp 計算 priority hints。
- dApp 收到被選出的 hint。
- dApp 檢查 I/Q observation 是否存在。
- dApp 驗證 5 MHz BWP profile 與 PUCCH/PUSCH ratios。
- dApp 輸出 apply/reject result。

## Visualization

- 參考 `dev_refer/dapp_dev_need/dApp-library/examples/spectrum_dapp.py` 的可視化模式。
- 相關選項包含：
  - `--demo-gui`
  - `--iq-plotter-gui`
  - `--energy-gui`
  - `--num-prbs <derived 5 MHz PRB count>`
- 可視化不是 PASS gate；必須等 dApp runtime path 接上後才能作為驗收證據。

## Expected markers

- `RedCap xApp priority hint`
- `RedCap dApp PRB decision`
- `[RedCap dApp Gate D][gNB MAC UL] gNB-side apply marker`
- `[RedCap dApp Gate D][gNB MAC PUCCH] gNB-side PUCCH marker`
- Gate C source path：`dev_refer/dapp_dev_need/libe3/tests/integration/test_role_pair_posix.cpp`
- Gate D source path：`openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c`
- Gate D PUCCH source path：`openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_uci.c`
- Gate D 5 MHz BWP profile：`ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.5mhz-bwp.yaml`
- Gate D runtime env passthrough：`ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.mmtc.yml` 的 `OAI_REDCAP_DAPP_GATE_D_MARKER`
- Gate D I/Q reference：`dev_refer/dapp_dev_need/E3Controller/src/e3sm/iq_pipeline.h` 與 `slot_iq_pipeline.h`
- PDCCH command path：ULSCH path 中 `config_uldci()` 後接 `fill_dci_pdu_rel15()` `[Needs Verification: TS 38.212 Section 7.3.1.1 / TS 38.214 Section 6.1]`

## Limitations

- Gate B 目前只驗證 SWIG definition，尚未驗證 generated SWIG module runtime。
- Gate C E3 loopback 已使用 project-local `tl_expected` test shim 通過。
- Official `tl_expected` FetchContent 仍不可用；不要把 local shim 當成 production dependency 證據。
- Gate D source hook readiness 與 `nr-softmodem` build PASS 已存在；small RFsim marker validation 已執行，但尚未 PASS。
- DCI bit-length source fix 已通過 `nr-softmodem` 與 `nr-uesoftmodem` build。
- Gate D runtime env passthrough 已加入 compose overlay，且最新 runtime 已將 5 MHz BWP profile mount 進 gNB container。
- 5 MHz profile 保留 106 PRB RF carrier，但 BWP1 與 RedCap DL/UL initial BWP 設為 30 kHz SCS 的 12 PRBs `[Needs Verification]`；runtime log 已確認 RA/SIB1 使用 size `12`，但 dApp marker 被阻擋在 connected scheduling 之前。
- 目前 Gate D runtime blocker：post-fix Docker image rebuild/RFsim recreate 因 workspace credits 不足被拒絕。
- Gate D 目前涵蓋 ULSCH/PUSCH/PDCCH 與 PUCCH marker path；尚未實作 dApp policy rewrite 去改寫 PUCCH/PUSCH allocation。
- Gate E 56 UE / 5 MHz BWP stress validation 尚未執行。
- 精確 O-RAN 與 3GPP clause mapping 仍是 `[Needs Verification]`。
