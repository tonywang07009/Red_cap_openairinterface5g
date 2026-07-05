# OpenAirInterface5G RedCap Research Fork

[English](./README.en.md) | [繁體中文](./README.zh-TW.md)

## 專案概述

這個 repository 是以 OpenAirInterface5G 為基礎的 RedCap 研究工作區，主要用於 RedCap、mMTC、RRC_INACTIVE、SDT、O-RAN/FlexRIC 實驗。上游 OAI RAN codebase 盡量保持原狀，本地新增 RedCap 操作腳本、文件路由、可重用 runtime evidence 與專案管理紀錄。

## 從這裡開始

| 目標 | 第一個檔案 |
|---|---|
| 從 0 安裝、編譯、執行 | [從零開始安裝](./redcap_doc/manuals/install/redcap_begin_from_zero.zh-TW.md) |
| 修改 C、xApp、rApp、dApp 或函式庫後重建 | [修改後重建流程](./redcap_doc/manuals/install/redcap_rebuild_after_changes.zh-TW.md) |
| 執行新手複現驗證 | [新手複現 Gate](./redcap_doc/manuals/install/redcap_newcomer_runtime_gate.zh-TW.md) |
| 查看所有安裝文件 | [安裝文件入口](./redcap_doc/manuals/install/README.zh-TW.md) |
| 執行日常 RedCap/mMTC 操作 | [RedCap 介面文件](./redcap_interface/Doc/README.zh-TW.md) |
| 閱讀穩定 RedCap 文件 | [RedCap 穩定文件](./redcap_doc/Doc/README.zh-TW.md) |
| 查找可重用 evidence 與設定 | [RedCap library 文件](./redcap_library/Doc/README.zh-TW.md) |

## 快速指令

除非步驟中特別切換目錄，否則請從 repository root 執行。

```bash
# 驗證 RedCap 公開操作介面，不啟動 RFsim。
bash redcap_interface/validate_redcap_interface.sh

# 開啟日常 RedCap/mMTC 操作選單。
bash redcap_interface/mmtc.menu.bash

# 開啟 paper/demo 顯示工具。
bash redcap_interface/mmtc.display.bash
```

## 文件路由

| 路由 | 用途 | 第一個檔案 |
|---|---|---|
| 安裝文件 | 從零安裝、修改後重建、新手複現 gate | [redcap_doc/manuals/install/README.zh-TW.md](./redcap_doc/manuals/install/README.zh-TW.md) |
| 操作腳本 | RFsim、Docker、Gate、DRX/eDRX/PSM、paper demo 選單 | [redcap_interface/Doc/README.zh-TW.md](./redcap_interface/Doc/README.zh-TW.md) |
| 穩定 RedCap 文件 | specs、papers、manuals、checklists、function references | [redcap_doc/Doc/README.zh-TW.md](./redcap_doc/Doc/README.zh-TW.md) |
| 可重用 evidence | final configs、CN5G overlays、runtime probes、accepted reports | [redcap_library/Doc/README.zh-TW.md](./redcap_library/Doc/README.zh-TW.md) |
| 專案管理 | milestones、validation plans、analysis records | [agent_doc/Project_management/](./agent_doc/Project_management/) |

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
| 日常 RFsim 與 mMTC 操作 | `bash redcap_interface/mmtc.menu.bash` |
| Paper reproduction 與 display panels | `bash redcap_interface/mmtc.display.bash` |
| 功能腳本實作 | `redcap_interface/bash_library/` |
| 介面驗證 | `bash redcap_interface/validate_redcap_interface.sh` |
| 目前 RFsim YAML source of truth | `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/` |

## 協定學習路徑

| 主題 | 第一個檔案 |
|---|---|
| RedCap 穩定文件 | [redcap_doc/Doc/README.zh-TW.md](./redcap_doc/Doc/README.zh-TW.md) |
| Spec notes | [redcap_doc/specs/Doc/README.zh-TW.md](./redcap_doc/specs/Doc/README.zh-TW.md) |
| Function reference 路由 | [redcap_doc/function_reference/Doc/README.zh-TW.md](./redcap_doc/function_reference/Doc/README.zh-TW.md) |

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
