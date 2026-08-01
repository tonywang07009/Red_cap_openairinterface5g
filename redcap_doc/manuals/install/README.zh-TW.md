# RedCap 安裝文件

[English](./README.en.md) | [繁體中文](./README.zh-TW.md)

## 用途

這個資料夾放 RedCap/OAI workspace 的公開安裝與重建流程。

## 文件列表

| 檔案 | 用途 |
|---|---|
| [redcap_begin_from_zero.zh-TW.md](./redcap_begin_from_zero.zh-TW.md) | 從新的本機 checkout 開始，跑到 29 UE RFsim 驗證。 |
| [redcap_rebuild_after_changes.zh-TW.md](./redcap_rebuild_after_changes.zh-TW.md) | 修改 C、xApp、rApp、dApp、script、config 或 library 後重建。 |
| [redcap_newcomer_runtime_gate.zh-TW.md](./redcap_newcomer_runtime_gate.zh-TW.md) | 執行新手 gate，回報文件哪裡不清楚。 |

## 閱讀順序

1. 新機器或新 checkout 先執行 `./mmtc.menu.bash install`；安裝器細節或手動 fallback 請看 [從零開始安裝](./redcap_begin_from_zero.zh-TW.md)。
2. 修改 code 或 config 後看 [修改後重建流程](./redcap_rebuild_after_changes.zh-TW.md)。
3. 要驗證文件是否能被新手複現時，看 [新手複現 Gate](./redcap_newcomer_runtime_gate.zh-TW.md)。

安裝器驗收只執行 1 UE smoke；29 UE newcomer gate 是另一項獨立驗證。
