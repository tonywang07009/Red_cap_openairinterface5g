# OAI Hook Inventory For BWP / SDT Reproduction

- [Generated At]: 2026-06-26T05:21:14.823500+00:00
- [Source]: local OAI source tree scan
- [Interpretation]: [gap_present] is an explicit implementation gap, not a missing file.

| area | hook | status | file:line | reproduction_impact |
|---|---|---|---|---|
| [BWP] | gNB BWP configuration | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c:2680` | Configures current DL/UL BWP structures used by gNB scheduling. |
| [BWP] | gNB BWP reconfiguration trigger | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c:3939` | Candidate hook for future BWP switch-delay instrumentation. |
| [BWP] | gNB transmission interruption timer | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c:3517` | Existing timing hook that can approximate switch interruption in local validation. |
| [BWP] | UE random-access BWP operation | [present] | `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c:904` | UE RA path switches current BWP according to TS 38.321 clause 5.15. |
| [BWP] | UE bwp-InactivityTimer implementation | [gap_present] | `openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c:924` | Paper timer curves cannot be claimed reproduced until this gap is instrumented or implemented. |
| [SDT] | gNB SDT log file hook | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c:43` | Provides a stable log target for SDT FSM transitions. |
| [SDT] | gNB CG-SDT classifier | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c:124` | Detects configured-grant SDT RX candidates in gNB UL processing. |
| [SDT] | gNB SDT UL grant transition | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c:198` | Starts SDT FSM transition logging when scheduler grants UL bytes. |
| [SDT] | gNB SDT UL burst completion | [present] | `openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c:223` | Completes SDT FSM state when UL pending bytes drain. |
| [SDT] | SDT FSM step | [present] | `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c:110` | Encodes the local SDT state/path transitions used by log extraction. |
| [SDT] | UE CG-SDT config detection | [present] | `openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c:1239` | UE-side CG-SDT configuration gate for future runtime verification. |
