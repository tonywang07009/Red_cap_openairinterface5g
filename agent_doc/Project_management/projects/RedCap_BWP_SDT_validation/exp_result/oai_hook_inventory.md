# OAI Hook Inventory For BWP / SDT Reproduction

- [Generated At]: 2026-06-30T02:26:02.772191+00:00
- [Source]: local OAI source tree scan
- [Interpretation]: [gap_present] is an explicit implementation gap, not a missing file.
- [Interpretation]: [wrapper_label] is recorded by the project runner/manifest but is not proven to alter OAI runtime behavior.
- [Interpretation]: [crash_repro_path] is a runtime-crash path confirmed by RFsim evidence, not a passing hook.

| area | hook | status | file:line | reproduction_impact |
|---|---|---|---|---|
| [BWP] | gNB BWP configuration | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c:2680` | Configures current DL/UL BWP structures used by gNB scheduling. |
| [BWP] | gNB BWP reconfiguration trigger | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c:3946` | Source hook for BWP switch trigger instrumentation and local delay extraction. |
| [BWP] | gNB BWP reconfiguration instrumentation | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c:3953` | Logs requested BWP switch target so the extractor can count local switch attempts. |
| [BWP] | gNB transmission interruption timer | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c:3517` | Existing timing hook used with instrumentation to approximate local switch interruption. |
| [BWP] | gNB transmission interruption instrumentation | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c:3527` | Logs interruption slots for local switch-delay evidence. |
| [BWP] | gNB BWP apply instrumentation | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c:614` | Logs the post-ACK DL/UL BWP IDs after the pending CellGroup is applied. |
| [BWP] | UE random-access BWP operation | [present] | `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c:908` | UE RA path switches current BWP according to TS 38.321 clause 5.15. |
| [BWP] | UE random-access BWP instrumentation | [present] | `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c:926` | Logs old/new active BWP IDs and keeps the inactivity-timer implementation gap explicit. |
| [BWP] | UE bwp-InactivityTimer implementation | [gap_present] | `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c:938` | Current instrumentation exposes the gap; paper timer curves still require full implementation or validated timer-equivalent runtime evidence. |
| [BWP] | BWP matrix traffic/timer scenario labels | [wrapper_label] | `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_bwp_validation.sh:32` | Records traffic/timer labels in manifests; targeted scan found no OAI C or compose hook that changes offered load, bwp-InactivityTimer, or switch-delay behavior. |
| [BWP] | BWP matrix force-recreate isolation | [present] | `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/redcap_runtime_common.sh:49` | Prevents cumulative docker logs across matrix rows when enabled by the BWP matrix runner. |
| [BWP] | BWP telnet trigger crash path | [crash_repro_path] | `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c:4110` | 2026-06-28 RFsim backtrace shows BWP 0 telnet trigger crashes inside this reconfiguration path; Gate 5 remains blocked until fixed. |
| [SDT] | gNB SDT log file hook | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c:43` | Provides a stable log target for SDT FSM transitions. |
| [SDT] | gNB CG-SDT classifier | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c:124` | Detects configured-grant SDT RX candidates in gNB UL processing. |
| [SDT] | gNB SDT UL grant transition | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c:198` | Starts SDT FSM transition logging when scheduler grants UL bytes. |
| [SDT] | gNB SDT UL burst completion | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c:223` | Completes SDT FSM state when UL pending bytes drain. |
| [SDT] | SDT FSM step | [present] | `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c:110` | Encodes the local SDT state/path transitions used by log extraction. |
| [SDT] | UE CG-SDT config detection | [present] | `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c:1239` | UE-side CG-SDT configuration gate for future runtime verification. |
| [SDT] | SDT 2-step RA scenario label | [wrapper_label] | `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_validation.sh:40` | Records the 2-step/4-step dimension in manifests; targeted scan found no OAI C or compose hook that changes RA procedure steps. |
| [SDT] | SDT slot10 scenario label | [wrapper_label] | `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_matrix.sh:17` | Records the slot10 paper dimension as a scenario name only; targeted scan found no runtime hook that changes slot timing. |
| [SDT] | SDT lambda_dp_5 scenario label | [wrapper_label] | `agent_doc/Project_management/projects/RedCap_BWP_SDT_validation/scripts/run_sdt_matrix.sh:17` | Records the lambda_Dp paper dimension as a scenario name only; targeted scan found no runtime hook that changes device intensity. |
