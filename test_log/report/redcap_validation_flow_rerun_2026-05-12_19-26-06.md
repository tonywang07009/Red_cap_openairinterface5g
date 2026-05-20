# RedCap Project Validation Flow Rerun

## 1. Technical Background
- [Purpose]：重跑目前 RedCap mMTC v1 的本地 validation flow，確認文件索引、evidence path、traceability marker、以及 focused CTest unit 沒有退化。
- [Scope]：本次是 [local validation rerun]，不啟動 Docker RFsim，不重建 container image。
- [Accepted runtime baseline]：M5 仍以 2026-05-08 的 [56 UE Case B static CN] `56/56` attach / PDU / tunnel / forward ping 作為已保存 evidence。

## 2. Validation Inputs
- [Project plan]：`agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md`
- [Test matrix]：`agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/validation/test_matrix.md`
- [Runtime checklist]：`agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/validation/runtime_checklist.md`
- [Tutorial]：`agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/redcap_parameter_implementation_validation_tutorial.md`
- [CTest log]：`test_log/compiler_logs/ctest_redcap_validation_flow_2026-05-12_19-26-06_lsanoff.log`

## 3. Test Results Summary
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Project plan existence | PASS | M6 / project index | `project_plan.md` exists |
| Tutorial existence | PASS | M6 documentation | `redcap_parameter_implementation_validation_tutorial.md` exists |
| Traceability marker search | PASS | M1-M7 docs/checklist | `RT-M5-056`, `56/56`, tutorial link, `[Needs Verification]` markers found |
| Evidence package path | PASS | M6 evidence | `test_log/report/m6_evidence_package_summary_2026-05-08_17-32-49.md` exists |
| Accepted 56 UE report path | PASS | M5 runtime evidence | `test_log/report/m5_rt_m5_056_caseb_static_cn_pass_report_2026-05-08_12-18-10.md` exists |
| Accepted 56 UE artifact path | PASS | M5 runtime artifacts | `test_log/runtime_artifacts/m5_rt_m5_056_caseb_static_cn_2026-05-08_12-03-22/` exists |
| Focused CTest unit regression | PASS | M1/M2/M3/M4/M4-B unit layer | 8/8 tests passed |
| Whitespace check | PASS | Git diff hygiene | `git diff --check` returned no issues |
| Source build | N/A | No C/C++ source changes | Build not required for this documentation/local validation rerun |
| Container image rebuild | N/A | No C/C++ source changes and no RFsim rerun | Image not rebuilt |
| RFsim UE/gNB/CN runtime | N/A | Runtime evidence only referenced | 56 UE runtime was not rerun in this local pass |

## 4. Focused CTest Details
| Test | Status |
|------|--------|
| `test_nr_ue_redcap_bwp` | PASS |
| `test_nr_ue_drx` | PASS |
| `test_nr_redcap_coreset0` | PASS |
| `test_nr_redcap_bwp` | PASS |
| `test_nr_redcap_sdt_fsm` | PASS |
| `test_nr_rrc_redcap` | PASS |
| `test_nr_rrc_lowpower` | PASS |
| `test_nr_nas_lowpower` | PASS |

## 5. 3GPP Specification Mapping
| Flow | Clause | Status |
|------|--------|--------|
| RedCap FR1 PRB / capability limits | TS 38.101-1 Section 5.3; TS 38.306 Section 4 | [Needs Verification] |
| RedCap SIB1 / access barring | TS 38.331 Section 6.3.1 / 6.3.2 | [Needs Verification] |
| CORESET#0 Case A/B and Type0 CSS | TS 38.213 Section 13 | [Needs Verification] |
| Random Access Msg1-Msg4 | TS 38.321 Section 5.1 | [Partially Verified] |
| RAR reception / Msg2 window | TS 38.321 Section 5.1.4 | [Needs Verification] |
| Contention resolution | TS 38.321 Section 5.1.5 | [Needs Verification] |
| Connected DRX | TS 38.321 Section 5.7; TS 38.331 Section 6.3.2 | [Partially Verified] |
| eDRX / PSM | TS 38.331 Section 6.3.2; TS 24.501 Section 8.2.7.1.1 / 5.5.1 | [Needs Verification] |

## 6. Modification Logs
- No C/C++ source files were modified.
- No runtime YAML was modified.
- No Docker image was rebuilt.
- New validation rerun report generated:
  - `test_log/report/redcap_validation_flow_rerun_2026-05-12_19-26-06.md`

## 7. Practice Exercises
- [Basic]：為什麼本次 validation 可以標記 [RFsim runtime N/A]，而不是 [FAIL]？
- [Applied]：如果 focused CTest 全過，但 56 UE runtime 失敗，下一步應優先分類 [RAN]、[CN]、還是 [runtime infra]？
- [Advanced]：請設計一個把本地 CTest rerun 與 56 UE Docker runtime rerun 合併成兩階段 validation pipeline 的流程。

