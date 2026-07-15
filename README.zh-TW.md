# OpenAirInterface5G RedCap Research Fork

[English](./README.en.md) | [繁體中文](./README.zh-TW.md)

## 專案概述

這個 repository 是以 OpenAirInterface5G 為基礎的 RedCap 研究工作區，主要用於 RedCap、mMTC、RRC_INACTIVE、SDT、O-RAN/FlexRIC 實驗。上游 OAI RAN codebase 盡量保持原狀，本地新增 RedCap 操作腳本、文件路由、可重用 runtime evidence 與專案管理紀錄。

## 從這裡開始

| 目標 | 第一個檔案 |
|---|---|
| 建置並重現 29 UE 入門流程 | [入門建置與 29 UE 重現](./redcap_doc/manuals/install/redcap_begin_from_zero.zh-TW.md) |
| 設定 56 UE profile 與 dApp/xApp 實驗 | [56 UE 實驗教學](./agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/gate_e_core56_manual_reproduction.zh-TW.md) |
| 開發或追蹤 dApp/xApp SDK | [SDK 開發指南](./agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/sdk_development_guide.zh-TW.md) |
| 查詢作用中 RedCap L1-L3 控制路徑 | [L1-L3 函式索引](./redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md) |
| 修改 C、xApp、rApp、dApp 或函式庫後重建 | [修改後重建流程](./redcap_doc/manuals/install/redcap_rebuild_after_changes.zh-TW.md) |
| 查看所有安裝文件 | [安裝文件入口](./redcap_doc/manuals/install/README.zh-TW.md) |
| 執行日常 RedCap/mMTC 操作 | [RedCap 介面文件](./redcap_interface/Doc/README.zh-TW.md) |
| 閱讀穩定 RedCap 文件 | [RedCap 穩定文件](./redcap_doc/Doc/README.zh-TW.md) |
| 查找可重用 evidence 與設定 | [RedCap library 文件](./redcap_library/Doc/README.zh-TW.md) |

## 快速指令

除非步驟中特別切換目錄，否則請從 repository root 執行。

```bash
# 驗證 RedCap 公開操作介面，不啟動 RFsim。
bash redcap_interface/validate_redcap_interface.sh

# 開啟統一 RedCap 操作入口：專案介紹、效能證據、實驗設定與進階 RFsim。
./mmtc.menu.bash

# 只顯示已驗證 paper/效能證據，不啟動 Docker。
./mmtc.menu.bash performance
```

## 已驗證實驗設定檔

| 欄位 | 目前契約 | 來源 |
|---|---|---|
| Service 上限 | `MMTC_TOTAL_UES=56` | `redcap_interface/bash_library/fc_mmtc_smoke_validation.sh` |
| Active UE 選擇 | `MMTC_ACTIVE_UES`，不可重複且範圍為 `1..56` | `redcap_interface/bash_library/fc_mmtc_smoke_validation.sh` |
| 拓樸 | 單一 gNB RFsim | `redcap_interface/Doc/README.zh-TW.md` |
| 多 gNB 或 CU/DU split | 實驗設定檔 v1 尚未支援 | `redcap_interface/Doc/README.zh-TW.md` |

先前提議的 `MMTC_ACTIVATE_UE` 不是目前腳本契約。

## 文件路由

| 路由 | 用途 | 第一個檔案 |
|---|---|---|
| 安裝文件 | 從零安裝、修改後重建、新手複現 gate | [redcap_doc/manuals/install/README.zh-TW.md](./redcap_doc/manuals/install/README.zh-TW.md) |
| 操作腳本 | RFsim、Docker、Gate、DRX/eDRX/PSM、paper demo 選單 | [redcap_interface/Doc/README.zh-TW.md](./redcap_interface/Doc/README.zh-TW.md) |
| 穩定 RedCap 文件 | specs、papers、manuals、checklists、function references | [redcap_doc/Doc/README.zh-TW.md](./redcap_doc/Doc/README.zh-TW.md) |
| 可重用 evidence | final configs、CN5G overlays、runtime probes、accepted reports | [redcap_library/Doc/README.zh-TW.md](./redcap_library/Doc/README.zh-TW.md) |
| 專案管理 | milestones、validation plans、analysis records | [agent_doc/Project_management/](./agent_doc/Project_management/) |
| dApp/xApp SDK | SDK 場景、API 行為、開發指南、56 UE Gate E-Core 手動復現 | [agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/README.zh-TW.md](./agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/README.zh-TW.md) |

## 文件與證據分層

| 層級 | 用途 | 路徑 |
|---|---|---|
| 參考 | 簽章、呼叫端、防護、套用點與 runtime marker | [L1-L3 函式索引](./redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md) |
| 指南 | 如何擴充與驗證 dApp/xApp SDK | [SDK 開發指南](./agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/sdk_development_guide.zh-TW.md) |
| 範例 | 可重現的入門與 56 UE 實驗 | [29 UE](./redcap_doc/manuals/install/redcap_begin_from_zero.zh-TW.md) / [56 UE](./agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/Doc/gate_e_core56_manual_reproduction.zh-TW.md) |

證據標籤彼此獨立：`Public` 代表已有公開宣告；`Integrated` 必須有正式呼叫端與套用路徑；`Runtime-evidenced` 必須有對應且保留的 marker；`Dormant/blocked` 代表公開或已實作路徑仍缺正式接線或證據。缺少證據或規格對應時標記 `[Needs Verification]`。

## 編譯與測試

第一次使用 RedCap 請先看：

- [從零開始安裝](./redcap_doc/manuals/install/redcap_begin_from_zero.zh-TW.md)

一般本機 OAI build：

```bash
cmake --preset default
cmake --build --preset default --target nr-softmodem
cmake --build --preset default --target nr-uesoftmodem
```

若需要安裝依賴或使用上游 wrapper：

```bash
cd cmake_targets
./build_oai -I --install-optional-packages -w USRP
./build_oai --ninja --gNB --nrUE
cd ..
```

若要刷新本地 RedCap RFsim images：

```bash
bash redcap_interface/redcap_rebuild_local_oai_images.sh
bash redcap_interface/redcap_inspect_gnb_image.sh
```

## RedCap 操作路由

| 任務 | 指令或檔案 |
|---|---|
| 日常 RFsim 與 mMTC 操作 | `./mmtc.menu.bash` |
| Paper/效能證據與明確重現入口 | `./mmtc.menu.bash performance` |
| 功能腳本實作 | `redcap_interface/bash_library/` |
| 介面驗證 | `bash redcap_interface/validate_redcap_interface.sh` |
| 目前 RFsim YAML source of truth | `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/` |

## 協定學習路徑

| 主題 | 第一個檔案 |
|---|---|
| RedCap 穩定文件 | [redcap_doc/Doc/README.zh-TW.md](./redcap_doc/Doc/README.zh-TW.md) |
| Spec notes | [redcap_doc/specs/Doc/README.zh-TW.md](./redcap_doc/specs/Doc/README.zh-TW.md) |
| RedCap L1-L3 函式索引 | [redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md](./redcap_doc/specs/function_reference/redcap_l1_l3_function_lookup.md) |

## Repository Map

```text
openairinterface5g
├── openair1/         L1 PHY 與 frame-parameter code
├── openair2/         L2 MAC/RLC/PDCP/RRC、F1/E1/X2、E2AP
├── openair3/         NGAP、GTP、NAS、UICC 與 control-plane code
├── executables/      gNB、eNB、UE、softmodem 入口
├── radio/            RF back ends，包含 RFsim
├── ci-scripts/       CI helpers、runtime YAML、RFsim scenarios、xApp assets
├── doc/              上游 OAI 文件
├── redcap_interface/ RedCap 操作選單與功能腳本
├── redcap_doc/       穩定 RedCap docs、specs、manuals、checklists
├── redcap_library/   可重用 RedCap evidence 與 configs
└── agent_doc/        專案管理、milestones、validation、rules
```

## 授權與支援

本 repository 保留上游 [OAI Public License V1.1](./LICENSE)。第三方 notices 請看 [NOTICE.md](./NOTICE.md)。

若是上游 OAI 問題，請使用 OAI community channels。若是本地 RedCap 研究問題，請附上 active project path、執行指令、預期 marker 與 log path。
