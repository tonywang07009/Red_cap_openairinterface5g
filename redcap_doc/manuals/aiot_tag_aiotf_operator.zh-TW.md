# A-IoT Tag 與 AIOTF 操作指南

[English](./aiot_tag_aiotf_operator.en.md)

## 範圍

一般操作與展示命令只用於預設停用的 `experimental_n6` diagnostic profile。另有獨立的 AIOTF NRF client 與 Naiotf Inventory gates；它們不驗證 AMF/NGAP/RRC transport、NEF exposure、實體 RF 或 3GPP conformance。

## 建置

修改 AIOTF、UE、RFsim 或 Docker source 後，使用已註冊的 rebuild owner：

```bash
redcap_interface/bash_library/fc_rebuild_local_oai_images.sh
```

此流程產生 `ran-build:latest`、`oai-aiotf:latest`、`oai-gnb:latest`、`oai-nr-ue:latest`。長時間命令必須記錄於 `task_log/tasks.json`，而且要讀完 retained build log 才能標為 passed。

## 設定

| Input | 預設值 | 規則 |
|---|---|---|
| `AIOTF_TRANSPORT_PROFILE` | `experimental_n6` | 其他值 fail closed，不做 fallback |
| `AIOTF_TAGS` | `1,2,...,60` | 唯一 Tag IDs 1-60 |
| `AIOTF_PENDING_CONTEXT` | `25:diversity:9:1:1:10:5` | `TAG:normal|diversity:CORRELATION:SESSION:EPOCH:FRAME:SLOT` |
| `AIOTF_TIMEOUT_MS` | `60000` | 正數的 local diagnostic timeout；不是 3GPP timer |

Pending Tag 必須出現在 `AIOTF_TAGS`。重複 Tag/frame/slot context、stale binding epoch、重複 session ID、空 Tag 集合與超出範圍的值，都會在 UDP listener 啟動前失敗。

## 操作

```bash
./mmtc.menu.bash aiot validate
./mmtc.menu.bash aiot start
./mmtc.menu.bash aiot status
./mmtc.menu.bash aiot down
```

| 命令 | Mutation | 必要結果 |
|---|---|---|
| `validate` | 無 | Baseline 不含 AIOTF；`aiot` profile 包含 AIOTF；Compose 可 render |
| `start` | 只啟動 `oai-aiotf` | `AIOT_OPERATOR_START PASS` |
| `status` | 無 | 回報 `running` 或 `stopped` |
| `down` | 只停止並移除 `oai-aiotf` | `AIOT_OPERATOR_DOWN PASS ... volumes=preserved` |

`down` 可重複執行，不傳 `-v`，也不停止 NRF、AMF、SMF、UPF、UDM、UDR、AUSF、MySQL、IMS、ext-DN、gNB 或 UE。

## 展示

```bash
redcap_interface/mmtc.display.bash aiot-t2
```

固定展示建立 Tag 25 diversity pending context，送出三筆 loopback diagnostic record，最後移除 AIOTF：

| Record | 預期 marker |
|---|---|
| Reader 2、frame 10、slot 5 | `AIOTF_DIAGNOSTIC_ASSOCIATED ... arbitration=0` |
| Reader 1、frame 10、slot 5 | `AIOTF_DIAGNOSTIC_ASSOCIATED ... arbitration=1` |
| Reader 1、frame 10、slot 6 | `AIOTF_DIAGNOSTIC_REJECT ... reason=no_pending_context` |

最後 marker 為 `AIOT_T2_DEMO PASS profile=experimental_n6 first_valid=1 duplicate=1 rejected=1`。無論成功或失敗，trap 都會呼叫已註冊的 AIOTF `down`。

## Registry 與 skill

| Owner | Entry |
|---|---|
| Bash Tool Registry | `redcap_library/bash_tool/registry.json` |
| Registered wrapper | `redcap_library/bash_tool/scripts/aiot_registered_check.sh` |
| Workflow skill | `redcap_library/skills/tag_aiotf_workflow/SKILL.md` |

Skill 驗證 Tags、payload length、reader mode、wake window、reader handles、evidence path 與 exact profile，而且只呼叫 registry dependencies。要求不可用的 `trusted_af_sbi` 或 `third_party_af_nef` 時，回傳 `missing_capability`，不會降級成 N6。

## Self-tests 與 retained evidence

```bash
redcap_library/bash_tool/scripts/aiot_registered_check.sh tag-selftest
redcap_library/bash_tool/scripts/aiot_registered_check.sh aiotf-selftest
redcap_library/bash_tool/scripts/aiot_registered_check.sh evidence aiotf \
  test_log/compiler_logs/aiotf_evidence_ladder_selftests_2026-07-20_13-39-00.log
```

Evidence path 必須 resolve 到 `test_log/` 下。未知 evidence class、缺 marker、指向 `test_log/` 外的 path，以及 executable 缺失，都會回傳 non-zero status。

## NRF schema 維護驗證

以下命令屬於 NRF maintainer gate，不會啟用 `trusted_af_sbi`：

```bash
NRF_SOURCE_DIR=/home/tonywang/OAI/oai-cn5g-nrf \
  redcap_library/bash_tool/scripts/aiot_registered_check.sh build-nrf-candidate

NRF_CONFORMANCE_TARGET=deployed \
  NRF_CANDIDATE_IMAGE=oai-nrf@sha256:59bbe00f83453e4543eb8c37a77db024711f3cd74708a3819ac6b407b60e901f \
  redcap_library/bash_tool/scripts/aiot_registered_check.sh nrf-aiotf-conformance
```

Build 與 conformance 分別對應 registry entries `build_aiotf_nrf_candidate`、`validate_aiotf_nrf_candidate`。Conformance 使用唯一 profiles，涵蓋 create/read/update/delete、invalid/unknown、repeated/concurrent PUT、target/area discovery、AMF regression，並以 cleanup trap 移除測試狀態。長時間 build 必須先更新 `task_log/tasks.json`。

## AIOTF NRF client 驗證

```bash
redcap_library/bash_tool/scripts/aiot_registered_check.sh aiotf-nrf-client
```

此命令對應 registry entry `validate_aiotf_nrf_client`。它以固定測試 instance 驗證 create、read-back、area discovery、HTTP rejection、timeout、duplicate/restart update、deregistration 與 NRF unavailable，並由 trap 移除測試 containers/profile。PASS marker 為：

```text
AIOTF_NRF_CLIENT PASS accepted=1 rejection=1 timeout=1 duplicate=1 restart=1 deregistration=1 unavailable=1 cleanup=empty
```

此 PASS 只滿足 `nrf_aiotf_profile_registered_and_read_back`。在 Naiotf listener 已綁定後，`AIOTF_SERVICE_READY ready=0 reason=amf_dependency_unavailable` 是預期的 fail-closed 結果，不得解讀成完整 `trusted_af_sbi` ready。

## Naiotf Inventory 驗證

```bash
redcap_library/bash_tool/scripts/aiot_registered_check.sh aiotf-naiotf-inventory
```

此命令對應 registry entry `validate_aiotf_naiotf_inventory`。它在 `public_net` 建立 bounded AIOTF service、h2c callback proxy 與 callback backend，驗證 0/1/60/61 Tags、重複 Tag、錯誤 AF、timeout notification、callback 204、restart `transId` 唯一性與 cleanup。PASS marker 為：

```text
AIOTF_NAIOTF_RUNTIME PASS protocol=h2c tags=0,1,60,61 auth=rejected callback=204 restart=unique cleanup=empty
```

Retained evidence 位於 `test_log/compiler_logs/aiotf_naiotf_inventory_runtime_2026-07-20_16-35-47.log`。此 gate 只完成 bounded `Naiotf_AIoT_Inventory` surface；AMF/NGAP/RRC round trip 仍缺少，因此完整 `trusted_af_sbi` 維持 fail closed。

## 失敗處理

| Marker 或錯誤 | 處理方式 |
|---|---|
| `AIOT_OPERATOR_REJECT reason=unsupported_profile` | 選 `experimental_n6`；不可把要求的標準 profile 靜默降級 |
| `AIOTF_CONFIG_REJECT` | 修正 Tags、pending context、timeout、address 或 port 後再啟動 |
| `Address already in use` | 同時檢查 Docker static address 與 host UDP 36900；不可停止無關 service |
| `AIOTF_DIAGNOSTIC_REJECT reason=no_pending_context` | 讓 Tag、frame、slot 對應到唯一 active pending context |
| `AIOTF_NRF_GATE REJECT` | 依 `reason=http_rejected|timeout|unavailable` 修正 NRF URI、schema 或連線；不可 alias 成其他 NF type |
| AMF/RAN 或 NEF gate 不可用 | 停止 evidence ladder；NRF/Naiotf PASS 不可替代缺少的 endpoint |

最後執行 `./mmtc.menu.bash aiot down`。不得刪除 CN5G volume。
