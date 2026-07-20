# A-IoT Tag 與 AIOTF 架構

[English](./aiot_tag_aiotf_architecture.en.md)

## 狀態

| 項目 | 目前結果 |
|---|---|
| 已實做 profile | `experimental_n6`，預設不啟用 |
| 標準路徑 profile | `trusted_af_sbi`、`third_party_af_nef` 尚不可用 `[Needs Verification]` |
| 規範基準 | 本地 TS 23.369 V20.0.0 draft；文件標示為尚未核准的 future-development material |
| 宣稱邊界 | 具 deterministic protocol、RFsim、process、diagnostic UDP、HTTP/2 NRF dependency 與 bounded Naiotf Inventory 證據；不宣稱 AMF/RAN round trip、完整 SBI、3GPP conformance 或實體 RF 成果 |

## 拓撲 2

```text
gNB/CW node -- CW2D 波束 --> Tag
UE Reader   -- R2D --------> Tag
UE Reader   <-- D2R -------- Tag
UE -- 自己的 PDU session / NR Uu --> gNB --> UPF -- N6 --> AIOTF diagnostic listener
```

- gNB 或獨立 CW node 提供連續載波能量；具睡眠機制的 RedCap UE 不負責持續 CW。
- UE 在 inventory window 喚醒。一個 reader 發 R2D；一個或兩個 eligible UE 可接收 D2R。
- Tag 僅保存自己的識別與 payload，不保存 UE allow-list 或 reader 指派。
- AIOTF 負責 binding、排程、correlation、failover、first-valid arbitration 與 evidence retention。
- N6 packet 使用 UE 的 PDU session；AIOTF 本身沒有 PDU session。

## Owner

| 責任 | 檔案或 runtime owner | 狀態 |
|---|---|---|
| Tag/CW 與實驗 Manchester/SFS codec | `radio/rfsimulator/stored_node.c` | 已實做，僅 RFsim |
| R2D/D2R control relay | `radio/rfsimulator/simulator.cpp` | 已實做，未選 `aiot_t2` 時停用 |
| UE R2D encode、D2R decode/CRC | `openair1/PHY/NR_UE_TRANSPORT/nr_ue_rf_helpers.c` | 已實做實驗 profile |
| UE wake gate 與 40-byte report producer | `executables/nr-ue.c` | 已實做實驗 profile |
| Binding、排程、failover、arbitration | `openair3/AIOTF/aiotf_inventory.c` | 已實做 60 Tags、兩個 reader handles |
| Process、health、pending context、UDP/Naiotf listener | `openair3/AIOTF/aiotf_service.c` | 已實做 `experimental_n6` 與 bounded Inventory surface |
| Container 與 network | `oai-cn5g/docker-compose.yaml` | `aiot` profile，預設停用 |
| NRF AIOTF profile schema 與 discovery | 外部 `oai-cn5g-nrf` owner | 已實做並以 Compose runtime 驗證 |
| AIOTF NRF client | `openair3/AIOTF/aiotf_service.c` | 已實做 HTTP/2 registration/update/read-back/discovery/delete |
| `Naiotf_AIoT_Inventory` listener/callback | `openair3/AIOTF/aiotf_service.c` | 已實做 h2c request/response 與 HTTP/2 callback；完整 profile 尚未 ready |
| AMF/NGAP/RRC 與 NEF adapter | 外部 CN owners 與本 repo RAN | 尚未實做 `[Needs Verification]` |

## Binding 與 arbitration

| Tag ID | Eligible readers | Normal primary | Diversity observer |
|---|---|---|---|
| 1-20 | UE1 | UE1 | 無 |
| 21-30 | UE1、UE2 | UE1 | UE2 |
| 31-40 | UE1、UE2 | UE2 | UE1 |
| 41-60 | UE2 | UE2 | 無 |

Normal mode 只啟動 primary reader。Diversity mode 僅允許 Tags 21-40；primary 發 R2D，observer 只收 D2R。AIOTF 只接受第一個同時符合 correlation、session、Tag、binding epoch、frame/slot、eligible reader、deadline 與 CRC 狀態的 report。後續相同 payload 保存為 duplicate evidence；不同但有效的 payload 保存為 conflict evidence。不做 MRC、soft combining 或 IQ combining。

## Diagnostic report contract

UE report 使用 network byte order，固定 40 bytes：

| 欄位 | 大小 | 邊界 |
|---|---:|---|
| Magic | 4 | `0x41494f54` |
| Version | 1 | `1` |
| Payload length | 1 | 1-16 |
| Flags | 2 | 必須含 CRC-valid flag |
| Reader handle | 4 | 1 或 2 |
| Tag ID | 4 | 1-60 |
| Frame | 4 | 0-1023 |
| Slot | 4 | 0-159 |
| Payload | 16 | 使用前 `payload length` bytes |

Wire record 不包含 correlation ID、session ID、binding epoch。因此 listener 在呼叫 arbitration 前，必須找到 Tag、frame、slot 相同且唯一的 pending context。零筆或多筆 match 都在 arbitration 前拒絕。

## CN5G profiles

| Profile | Networks | Readiness | 結果 |
|---|---|---|---|
| `experimental_n6` | `public_net`、`traffic_net` | State 初始化且 UDP listener 綁定 | 已實做 diagnostic path |
| `trusted_af_sbi` | `public_net` | Naiotf listener、AIOTF NRF client、AMF/NGAP/RRC endpoints | 停用；Naiotf 與 NRF dependency 已通過，但 RAN/AMF endpoints 缺少 |
| `third_party_af_nef` | `public_net` | Trusted-AF path 加 `Nnef_AIoT_*`、auth、callback | 停用；已選 OAI NEF `358f2131`，但缺少所需 API owner |

目前 AIOTF container 在 `public_net` 使用 `192.168.70.141`，在 `traffic_net` 使用 `192.168.72.141`。UDP 36900 只 publish 到 host loopback。未選 `aiot` profile 時，baseline Compose 不包含 AIOTF。

## Naiotf Inventory contract

| 項目 | 實做邊界 |
|---|---|
| Route | h2c `POST /naiotf-aiot/v1/request-inv` |
| Request | `afId`、explicit `targetDevices.devices`、`notifUri`；`numDevices` 與 `timeInterval` 為 bounded optional fields |
| Response | HTTP 200 與唯一 `transId` |
| Device mapping | 1-60 的 Tag ID 以 4-byte network-order unsigned integer後再做 base64；Tag 1=`AAAAAQ==`、Tag 60=`AAAAPA==` |
| Authorization | 啟動參數 `--trusted-af-id` 的單一 local allow-list；錯誤 AF 回 403 |
| Notification | HTTP/2 POST `AIoTNotif`；成功需 callback 回 204，失敗每 5 秒重試 |
| Bounded state | 一次只接受一個 active Inventory operation，最多 60 個不重複 Tag；沿用 `aiotf_inventory` correlation、epoch、first-valid、duplicate/conflict 與 timeout state |

目前不接受 `targetArea`、filtering selection、HTTPS callback 或 OAuth token，也不提供 Command、ADM 或 AIoT security service。上述 permanent-ID mapping 與 local authorization 是本實驗 contract，並非 3GPP conformance 證據 `[Needs Verification]`。

## NRF schema 與版本

| 項目 | 固定值 |
|---|---|
| NRF source | `087f11cab1bd01a6d30fd97f225b5258e77d8e3a` |
| common-src source | `d30e5b06a05d00e68e85ef3060d484a3e6d26ed7` 加最小 generated-style AIOTF diff |
| OpenAPI baseline | 3GPP Forge `REL-20` commit `28e28457200336cf6d291ed1dd419f194fc50fe5`，TS 29.510 V19.6.0 |
| Runtime image | `oai-nrf@sha256:59bbe00f83453e4543eb8c37a77db024711f3cd74708a3819ac6b407b60e901f` |
| Previous image | `oaisoftwarealliance/oai-nrf@sha256:af0fd1d202af0b6ceb65373977abe780b69aad1912390bf5835350955a034a92` |

NRF 現在可原生保存 `nfType=AIOTF` 與 `aiotfInfoList`，並支援 `target-nf-type=AIOTF` 與 `aiot-area-ids` filter。Server conformance 證據位於 `test_log/compiler_logs/nrf_aiotf_conformance_2026-07-20_14-38-05.log`。AIOTF client 的 create 201、restart/update 200、read-back、area discovery、rejection、timeout、NRF unavailable 與 deregistration 204 證據位於 `test_log/compiler_logs/aiotf_nrf_client_runtime_final_2026-07-20_15-30-03.log`。

Client profile 刻意不送 `nfServices`：frozen TS 29.510 `ServiceName` schema 沒有 `Naiotf` 值，不能虛構 service name。`Naiotf` service-list mapping 與 NRF HTTP/1 generated API parity 保持 `[Needs Verification]`；目前實證僅涵蓋 HTTP/2。

外部 owner 沒有提交可重現的 TS 29.510 model-generation command，因此目前是針對 frozen baseline 的最小 generated-style diff，不宣稱完整升級所有 Release 19 models。`[Needs Verification]`

## Rollback

執行已註冊的 AIOTF `down`。它只停止並移除 `oai-aiotf`，不執行 `docker compose down`、不刪 volume、不修改 `register_nf.general`，也不重建其他 CN5G service。可重複執行 `down`。

NRF rollback 僅把 `oai-cn5g/docker-compose.yaml` 的 image 改回上表 previous digest，然後執行：

```bash
docker compose -f oai-cn5g/docker-compose.yaml up -d --no-deps --force-recreate oai-nrf
```

不得使用 `down -v`。實際 rollback 與 forward restoration 均約 11 秒，完整結果位於 `test_log/compiler_logs/nrf_aiotf_rollback_drill_2026-07-20_14-47-35.log`。

## 受阻的標準路徑

NRF server、AIOTF registration/update/read-back/discovery client 與 bounded `Naiotf_AIoT_Inventory` gate 已通過。完整標準路徑仍受阻於 AMF `Namf_AIoT` route、RAN NGAP/RRC AIoT endpoint，以及已選 OAI NEF `358f2131` 中缺少的 `Nnef_AIoT_*` owner。不得用 N6 UDP 取代這些介面，也不得把 AIOTF 假裝註冊成其他 NF type。

公開的 TS 38.413 V19.1.0 已有 A-IoT NGAP/ASN.1，但 8.20.1-8.20.5 明確限定 NG-RAN node 是 gNB reader；公開的 TS 38.331 V19.1.0 找不到對應的 AIoT/UE Reader RRC endpoint。直接匯入 Release 19 NGAP 會變成拓撲 1，不是本專案選定的拓撲 2，因此 2.8 需等待一致的 UE Reader NGAP/RRC Stage-3 baseline `[Needs Verification]`。

## 參考

- 3GPP TS 29.510: <https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3345>
- 3GPP 5G APIs Forge: <https://forge.3gpp.org/rep/all/5G_APIs>
- OAI NRF owner: <https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-nrf>
- ETSI/3GPP TS 38.413 V19.1.0: <https://www.etsi.org/deliver/etsi_ts/138400_138499/138413/19.01.00_60/ts_138413v190100p.pdf>
- ETSI/3GPP TS 38.331 V19.1.0: <https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/19.01.00_60/ts_138331v190100p.pdf>
