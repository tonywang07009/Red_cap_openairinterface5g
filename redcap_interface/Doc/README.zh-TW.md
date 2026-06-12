# RedCap Interface 文件

## 用途
- 這裡放 RedCap / mMTC 操作者會直接使用的 shell 入口。
- RFsim、paper demo、介面驗證都從這裡開始。

## Bash 主入口
| 腳本 | 用途 |
|---|---|
| `mmtc.menu.bash` | 日常 RFsim：config mount、Docker 啟動、Gate 3、256QAM、RX mode、DRX/eDRX/PSM 參數 |
| `mmtc.display.bash` | Paper demo、live panel、展示型重現流程 |
| `validate_redcap_interface.sh` | 非破壞性語法與依賴檢查 |

## Step-by-Step Recap
```bash
bash redcap_interface/mmtc.menu.bash
bash redcap_interface/mmtc.display.bash
bash redcap_interface/validate_redcap_interface.sh
```
