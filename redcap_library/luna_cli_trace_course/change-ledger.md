---
title: Source-backed RedCap to AIOTF change ledger
status: pilot-review-required
evidence_tier: mixed
last_reviewed: 2026-08-01
---

# Source-backed change ledger

本表是歷史修改重播入口，不是 Git author ledger。只有同時找到 planning
record、affected source、validation/evidence owner 的 change family 才能進入
教材。`git diff` 或目前 working tree 不能單獨證明某項修改由 Codex 完成。

## 納入規則

| Gate | 必要證據 | 不足時的處理 |
| --- | --- | --- |
| Planning | Project plan 或 OpenSpec change | 不列為已規劃修改 |
| Source | 具體 `openair1/2/3`、runtime 或 operator owner | 標記 source owner `[Needs Verification]` |
| Validation | Test、report 或 retained evidence owner | 不宣稱已驗證 |
| Attribution | 可追溯的 author/commit/project record | 不標記個人或 Codex authorship |

## 摘要

| ID | Change family | 最強證據 | Current state | 對應章節 |
| --- | --- | --- | --- | --- |
| CL-01 | RedCap PHY init constraints | Focused unit/build report | Implemented-called | 00、02 |
| CL-02 | Config、capability 與 SIB1 access | Source + unit tests | Implemented-called | 02 |
| CL-03 | Initial BWP、CORESET#0 與 RA | Source + retained RFsim evidence | Implemented-called | 03 |
| CL-04 | RRC_INACTIVE、SDT、DRX/eDRX/PSM | Unit/flow/log by feature | Partial by feature | 04 |
| CL-05 | mMTC scaling 與 CN boundary | Retained 56/56 and 64-UE boundary | Bounded runtime | 05 |
| CL-06 | Simulator performance/paper replay | Runtime measurement reports | Scenario-specific | 05、10 |
| CL-07 | A-IoT Topology 2 Tag/Reader | Experimental protocol/RFsim evidence | 25/26 tasks | 06 |
| CL-08 | AIOTF、NRF、Naiotf 與 N6 diagnostic | Layered runtime report | 20/22 tasks; standard path stopped | 07 |
| CL-09 | xApp/dApp SDK、E2、guard 與 apply | Static/ACK/apply/bounded A/B | Mixed; 21/22 test-validation tasks | 08、09 |

## CL-01：RedCap PHY init constraints

| 欄位 | Evidence |
| --- | --- |
| Planning/history owner | [RedCap mMTC project](../../agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md) |
| Earliest retained source-backed record found | [RedCap Unit 1 report](../library_reports_summary/redcap_unit1_init_validation_report.md) records 2026-04-09 build/unit evidence |
| Source owners | [`nr_parms.c`](../../openair1/PHY/INIT/nr_parms.c), [`nr_phy_init.h`](../../openair1/PHY/INIT/nr_phy_init.h) |
| Test owner | [`test_nr_frame_params.cpp`](../../openair1/PHY/INIT/tests/test_nr_frame_params.cpp) |
| Historical claim | RedCap FR1 grid/RX/TX constraints were moved into callable init-time validation helpers with unit coverage |
| Current applicability | Helpers are still called from gNB and UE frame-parameter initialization |
| Attribution boundary | This is the earliest currently identified retained modification record; individual/Codex authorship is `[Needs Verification]` |

## CL-02：Config、capability 與 SIB1 access

| 欄位 | Evidence |
| --- | --- |
| Planning/history owner | [RedCap parameter implementation tutorial](../../agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/redcap_parameter_implementation_validation_tutorial.md), M2 |
| Source owners | [`gnb_paramdef.h`](../../openair2/GNB_APP/gnb_paramdef.h), [`gnb_config.c`](../../openair2/GNB_APP/gnb_config.c), [`nr_radio_config.c`](../../openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c), [`nr_redcap_config.c`](../../openair3/UICC/nr_redcap_config.c), [`rrc_ue_redcap.c`](../../openair2/RRC/NR_UE/rrc_ue_redcap.c) |
| Validation owner | [`test_nr_rrc_redcap.cpp`](../../openair2/RRC/NR/tests/test_nr_rrc_redcap.cpp) and its [CTest registration](../../openair2/RRC/NR/tests/CMakeLists.txt) |
| Historical claim | gNB RedCap fields enter SIB1-v1700; UE-local capability fields build RedCap capability and participate in access barring |
| Current applicability | `implemented-called`; parser presence alone still does not prove attach or runtime outcome |
| Pilot | [Chapter 02](chapters/02-redcap-config-and-capability.md) |

## CL-03：Initial BWP、CORESET#0 與 RA

| 欄位 | Evidence |
| --- | --- |
| Planning records | [redcap-bwp-sdt-validation](../../openspec/changes/redcap-bwp-sdt-validation/proposal.md), [fix-bwp-trigger0-reconfiguration-crash](../../openspec/changes/fix-bwp-trigger0-reconfiguration-crash/proposal.md) |
| Project owner | [RedCap BWP/SDT validation](../../agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/project_BWP_SDT.md) |
| Source owners | [`gnb_config.c`](../../openair2/GNB_APP/gnb_config.c), [`nr_mac_redcap_bwp.c`](../../openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap_bwp.c), [`nr_radio_config.c`](../../openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c), [`gNB_scheduler_RA.c`](../../openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_RA.c), [`nr_ue_redcap_bwp.c`](../../openair2/LAYER2/NR_MAC_UE/nr_ue_redcap_bwp.c) |
| Evidence owner | [BWP/SDT result summary](../../agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/exp_result/exp_result_summary.md), [Case B mismatch report](../library_reports_summary/m3t2_caseb_ra_dci_mismatch_report.md) |
| Current applicability | Change records are complete; exact 3GPP mappings and some runtime generalizations remain `[Needs Verification]` |

## CL-04：RRC_INACTIVE、SDT、DRX/eDRX/PSM

| 欄位 | Evidence |
| --- | --- |
| Planning records | [RRC_INACTIVE/SDT project](../../agent_doc/Project_management/projects/redcap_rrc_inactive_sdt_oran_control_v1/project_plan.md), [adaptive-drx-ab-validation](../../openspec/changes/adaptive-drx-ab-validation/proposal.md) |
| Source owners | `openair2/LAYER2/NR_MAC_gNB/`, `openair2/LAYER2/NR_MAC_UE/`, `openair2/RRC/NR_UE/`, `openair3/NAS/NR_UE/` |
| Evidence owners | [Low-power unit-test report](../library_reports_summary/m4b_lowpower_unit_test_report.md), [low-power boundary report](../library_reports_summary/m4b_lowpower_boundary_report.md), [adaptive DRX A/B report](../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/report/adaptive_drx_ab_gate_2026-07-11.zh-TW.md) |
| Current applicability | DRX, eDRX, PSM, RRC_INACTIVE and SDT have different owners and evidence tiers; do not combine them into one power-saving PASS |

## CL-05：mMTC scaling 與 CN boundary

| 欄位 | Evidence |
| --- | --- |
| Project owner | [RedCap mMTC project](../../agent_doc/Project_management/projects/redcap_mmtc_priority_execution_v1/project_plan.md) |
| Source/runtime owners | RAN scheduler/RA owners, repository-owned [`oai-cn5g`](../../oai-cn5g/), and registered validation tooling |
| Accepted evidence | [56 UE static-CN report](../library_reports_summary/m5_caseb_56ue_static_cn_pass_report.md) |
| Upper-bound evidence | [64 UE threshold report](../library_reports_summary/m5_caseb_64ue_static_cn_threshold_report.md) |
| Current applicability | 56/56 is a retained Case B RFsim boundary; 64 UE is a classified upper-bound failure, not general capacity or real-network proof |

## CL-06：Simulator performance 與 paper replay

| 欄位 | Evidence |
| --- | --- |
| Project owner | [Simulator performance evaluation](../../agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/project_plan.md) |
| Source/runtime owners | RFsim/OAI configuration, `iperf`/ping collection, project analysis scripts and reports |
| Evidence examples | [Paper 07 UL reproduction](../../agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/paper07_ul_peak_reproduction_report.md), [platform validity](../../agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/p5_platform_validity_report.md) |
| Current applicability | Results are scenario- and configuration-specific; they do not prove physical power, general capacity, or paper parity outside recorded conditions |

## CL-07：A-IoT Topology 2 Tag/Reader

| 欄位 | Evidence |
| --- | --- |
| Planning record | [add-aiot-topology2-reader-experiment](../../openspec/changes/add-aiot-topology2-reader-experiment/proposal.md) |
| Source owners | [`stored_node.c`](../../radio/rfsimulator/stored_node.c), [`simulator.cpp`](../../radio/rfsimulator/simulator.cpp), [`nr-ue.c`](../../executables/nr-ue.c), UE PHY codec owners |
| Evidence owner | [AIOTF/N6 validation report](../library_reports_summary/aiotf_cn5g_experimental_n6_validation_report.md), prerequisite protocol/RFsim rows |
| Current state | OpenSpec is 25/26; remaining focused build/check task keeps the change in progress |
| Claim boundary | Manchester/SFS and RFsim routing are experimental; no physical dual-beam RF or 3GPP conformance claim |

## CL-08：AIOTF、NRF、Naiotf 與 N6 diagnostic

| 欄位 | Evidence |
| --- | --- |
| Planning records | [integrate-aiotf-cn5g-tag-workflow](../../openspec/changes/integrate-aiotf-cn5g-tag-workflow/proposal.md), [upgrade-oai-nrf-aiotf-schema](../../openspec/changes/upgrade-oai-nrf-aiotf-schema/proposal.md) |
| Source owners | [`openair3/AIOTF`](../../openair3/AIOTF/), [`oai-cn5g/docker-compose.yaml`](../../oai-cn5g/docker-compose.yaml) |
| Evidence owner | [AIOTF CN5G experimental N6 report](../library_reports_summary/aiotf_cn5g_experimental_n6_validation_report.md) |
| Current state | NRF and bounded Naiotf Inventory have evidence; the integration change is 20/22 because AMF/NGAP/RRC and NEF owners remain stopped |
| Claim boundary | `experimental_n6` is diagnostic delivery through the UE PDU session; it is not `Namf_AIoT`, `Nnef_AIoT_*`, or a standard-path round trip |

## CL-09：xApp/dApp SDK、E2、guard 與 apply

| 欄位 | Evidence |
| --- | --- |
| Planning records | [Workflow v3](../../openspec/changes/redcap-oran-sdk-workflow-v3/proposal.md), [dApp/xApp validation](../../openspec/changes/redcap-dapp-xapp-sdk-test-validation/proposal.md) |
| Project owners | [Workflow v3 project](../../agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/project_plan.md), [SDK validation project](../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/project_plan.md) |
| Source owners | [`REDCAP_SDK/xapp`](../../openair2/E2AP/REDCAP_SDK/xapp/), [`E3AP/sdk`](../../openair2/E3AP/sdk/), [`ran_func_rc.c`](../../openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c) |
| Evidence owners | [G4 report](../../agent_doc/Project_management/projects/redcap_oran_sdk_workflow_v3/report/G4_rfsim_case_b_ul_prb_2026-07-04.md), [Gate E Core56 report](../../agent_doc/Project_management/projects/redcap_dapp_xapp_sdk_test_validation_v1/report/gate_e_core56_ab_latency_2026-07-09.md) |
| Current state | One bounded `redcap_ul_prb_cap` path has contract, ACK and gNB apply evidence; broader helpers are mixed and the SDK validation change is 21/22 |
| Claim boundary | ACK does not imply apply; Core56 comparability does not establish latency improvement or generic dApp effectiveness |

## 排除項目

下列 change 可作文件治理背景，但不列入 source/runtime 修改主線：public-doc
restructure、English-first wiki migration、system-map creation，以及本教材本身。
它們沒有改變 OAI runtime behavior。

## 下一次更新規則

1. 先更新本 ledger 的 planning/source/evidence 三欄。
2. 再更新受影響章節的 current applicability 與 CLI locator。
3. 保留歷史結論；若 current source 已不同，另加 current-state 說明。
4. 新 runtime claim 必須有 owning marker 與 outcome evidence；否則停止在既有 tier。
