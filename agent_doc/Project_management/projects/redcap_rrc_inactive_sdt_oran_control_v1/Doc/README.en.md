# RedCap RRC Inactive SDT O-RAN Control Docs

## Purpose
- This project tracks RRC_INACTIVE, SDT, and O-RAN control validation.

## Read Order
1. `project_plan.md`
2. `agent_rules.md`
3. Current milestone
4. Current validation file
5. Latest relevant `test_log/work_daily/*.md`

## Current Boundary
- Gate 3 runtime should use `MMTC_RRC_INACTIVE_GATE3_CG_CONFIG=1`.
- Expected markers include configuredGrant parsing and cg-SDT PUSCH scheduling.
- Runtime success still requires Docker/RFsim evidence.
