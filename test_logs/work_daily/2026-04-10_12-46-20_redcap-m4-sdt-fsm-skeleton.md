# Work Daily Log
## Session Metadata
- Date: 2026-04-10 12:46
- Agent Session ID: N/A
- Task Slug: redcap-m4-sdt-fsm-skeleton

## Milestone & Sub-task Reference
- Milestone: Milestone 4: SDT / RRC_INACTIVE
- Sub-task: Minimal SDT scheduler FSM, gNB inactive flag, and UE RedCap RRC state plumbing
- Status: [COMPLETED]

## What Was Done
- Added `openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.[ch]` implementing:
  - `IDLE -> SDT_TRIGGER -> MsgA / Msg3 -> SDT_ACTIVE -> INACTIVE`
  - payload-threshold based path selection
  - `inactive_allowed` guard handling
- Added `nr_redcap_rrc_state_t` in `openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h`.
- Added `redcap_rrc_state` field and `nr_ue_mac_set_state()` helper in `openair2/LAYER2/NR_MAC_UE/mac_defs.h`.
- Replaced direct UE MAC state assignments in `config_ue.c`, `nr_ra_procedures.c`, and `nr_ue_scheduler.c` with `nr_ue_mac_set_state()` so RedCap RRC state stays synchronized.
- Added gNB config flag `redcap_inactive_allowed` in:
  - `openair2/GNB_APP/gnb_paramdef.h`
  - `openair2/GNB_APP/gnb_config.c`
  - `ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml`
- Added `test_nr_redcap_sdt_fsm.cpp` and registered it in `openair2/LAYER2/NR_MAC_gNB/tests/CMakeLists.txt`.
- Updated `agent_doc/Project_management/Simluation_v2.md` so M4 is no longer shown as `[Pending]`.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 6.3.2 — SIB1 ASN.1 contains `sdt-ConfigCommon-r17` and related RedCap common information.
- TS 38.331 Section 5.3.1 — ⚠ Needs Verification for precise RRC suspend / inactive / resume procedure mapping.
- TS 38.321 SDT procedure clause — ⚠ Needs Verification for the exact MsgA vs Msg3 selection clause number.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `cmake --build --preset tests --target nr-softmodem test_nr_redcap_coreset0 test_nr_redcap_sdt_fsm` | Pass | Build coverage for new FSM source + existing RedCap code paths | Log: `test_log/build_logs/redcap_m4_sdt_build_2026-04-10_12-44-29.log` |
| `ctest -R 'test_nr_redcap_coreset0|test_nr_redcap_sdt_fsm|test_nr_frame_params' --output-on-failure` | Pass | Unit coverage for MsgA, Msg3, inactive-disabled, CORESET, PHY constraints | Log: `test_log/compiler_logs/redcap_m4_sdt_ctest_2026-04-10_12-44-43.log` |

## Known Issues / Blockers
- FSM is currently a minimal, testable module; it is not yet wired into the live gNB scheduler call chain.
- UE-side `redcap_rrc_state` plumbing is synchronized with current MAC state transitions, but no runtime path drives it into `[INACTIVE]` yet.
- Full MsgA simulation and runtime state-trace verification still require future scheduler integration and host runtime access.

## Next Step
- Wire the SDT FSM into the appropriate gNB scheduling path and prepare a runtime trace for `[MsgA]` / `[Msg3]` verification before attempting Milestone 5 host throughput evidence collection.
