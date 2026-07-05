# RedCap RRC Inactive SDT O-RAN Control 文件

## 用途
- 這個 project 追蹤 RRC_INACTIVE、SDT、O-RAN control validation。

## 閱讀順序
1. `project_plan.md`
2. `agent_rules.md`
3. 目前 milestone
4. 目前 validation file
5. 最新相關 `test_log/work_daily/*.md`

## 目前邊界
- Gate 3 runtime 使用 `MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1`。
- 預期 marker 包含 configuredGrant parsing 與 cg-SDT PUSCH scheduling。
- runtime success 仍需 Docker/RFsim evidence。
