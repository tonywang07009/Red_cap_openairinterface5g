# Apps Development References

`Apps_dev/` stores developer references for dApp, xApp, and rApp work. Treat these repositories and extracted documents as implementation inputs; production RedCap behavior remains owned by the corresponding `openair1/`, `openair2/`, or `openair3/` module.

`Apps_dev/` 用於存放 dApp、xApp 與 rApp 的開發參考資料。這些 repository 與擷取文件是實作輸入；正式 RedCap 行為仍由對應的 `openair1/`、`openair2/` 或 `openair3/` 模組負責。

## Quick routes / 快速導覽

| Need / 需求 | Path | Use / 用途 |
|---|---|---|
| dApp E3 transport | `dapp_dev_need/libe3/` | E3 roles, transport, encoding, and SWIG references / E3 角色、傳輸、編碼與 SWIG 參考 |
| dApp controller and I/Q | `dapp_dev_need/E3Controller/` | I/Q pipelines, PRB controls, and timing-log shapes / I/Q pipeline、PRB 控制與 timing log 格式 |
| dApp SDK examples | `dapp_dev_need/dApp-library/` | I/Q saver, control, and visualization examples / I/Q saver、控制與視覺化範例 |
| dApp OAI comparison | `dapp_dev_need/dApp-openairinterface5g/` | Targeted implementation comparison only / 僅供特定實作比對 |
| dApp FlexRIC comparison | `dapp_dev_need/dApp-flexric/` | FlexRIC-side dApp references / FlexRIC dApp 參考 |
| xApp SDK and examples | `xapp_dev_need/` | Service models and example xApps / service model 與 xApp 範例 |
| rApp references | `rapp_dev_need/` | rApp and generated API references / rApp 與產生的 API 參考 |
| Extracted development docs | `develop_refer_doc/` | Curated dApp, xApp, and rApp source notes / 整理後的 dApp、xApp 與 rApp 來源筆記 |
| Experiment skills | `exp_skill/README.md` | Reusable experiment workflows / 可重用的實驗流程 |

## Rules / 使用規則

- Use `Apps_dev/` in active plans, guides, and validation scripts. 現行計畫、指南與驗證腳本一律使用 `Apps_dev/`。
- Read only the files needed for the active task; do not copy a reference repository into OAI source modules. 僅讀取當前工作需要的檔案，不要將整個參考 repository 複製進 OAI source module。
- Preserve local nested-repository and submodule state. 保留巢狀 repository 與 submodule 的本地狀態。
- Historical reports may retain `dev_refer/` when it records the path used at that time. 歷史報告若記錄當時路徑，可以保留 `dev_refer/`。
