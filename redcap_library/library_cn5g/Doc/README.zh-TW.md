# CN5G Library 文件

## 用途
- 這裡放 CN5G overlay、DB seed、可重用 compose fragment。

## Bash 連結
- 產生 helper 透過 `redcap_interface/mmtc.menu.bash` 或相容 shim 呼叫。
- 實作檔在 `redcap_interface/bash_library/fc_generate_mmtc_cn_db_overlay.sh`。

## 規則
- 文件流程不要直接改 `/home/tonywang/OAI/oai-cn5g`。
- runtime overlay 應由腳本產生 temporary file。
