# RedCap 文件與介面重整

## 用途
- 這個 project 用來說明目前文件架構與 Bash 介面架構。
- 修改 `redcap_interface/`、`redcap_doc/`、`redcap_library/` 前，先讀這裡。
- 修改 root `README.md` 或 RedCap 文件路由時，也先讀這裡。

## 閱讀順序
1. `project_plan.md`
2. `agent_rules.md`
3. 目標 milestone
4. 目標 validation

## 產出
- 兩個主選單：`mmtc.menu.bash`、`mmtc.display.bash`。
- 功能腳本庫：`redcap_interface/bash_library/fc_*`。
- RedCap 主要資料夾的雙語 `Doc/` 頁面。
- 可重用文件 Skill：`redcap_library/redcap_doc_writer_skill/SKILL.md`。
- Root `README.md` 的 RedCap 路由入口。
- RedCap L1/L2 protocol guide：`redcap_doc/specs/redcap_l1_l2_protocol_guide.md`。

## README 模板規則
- 可參考 `doc_example/Best_README_template/README.md` 的章節順序。
- 不複製範例專案的 MIT license、徽章、作者欄位或簡體中文品牌內容。
- root README 必須保留 OAI license、NOTICE、upstream docs、support 入口。
