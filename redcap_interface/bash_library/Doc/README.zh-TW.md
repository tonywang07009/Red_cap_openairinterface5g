# Bash Library 文件

## 用途
- 這裡放兩個主選單會呼叫的功能實作腳本。
- 檔名前綴 `fc_` 代表 function-level helper。

## 命名規則
- `fc_*.sh`：shell 功能腳本。
- `fc_*.bash`：Bash 專用功能腳本。
- `fc_*.py`：Python 功能腳本。

## 使用規則
- 一般操作優先呼叫 `redcap_interface/mmtc.menu.bash` 或 `redcap_interface/mmtc.display.bash`。
- 只有 debug 單一功能時才直接呼叫 `fc_*`。
