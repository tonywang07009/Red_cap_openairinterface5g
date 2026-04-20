# Work Daily Log
## Session Metadata
- Date: 2026-04-19 19:32
- Agent Session ID: N/A
- Task Slug: redcap-m5-cgcfg-postapply-segv-rca

## Milestone & Sub-task Reference
- Milestone: RedCap mMTC runtime stabilization (M5)
- Sub-task: CellGroupConfig first-apply path RCA and nofree/defer/BWP-guard validation
- Status: [COMPLETED]

## What Was Done
- Added and validated [MMTC_CGCFG_NOFREE] and [MMTC_CGCFG_DEFER_FREE_SLOTS] gates in `openair2/RRC/NR_UE/L2_interface_ue.c`.
- Added [BWP null guards] and guarded-path logs in `openair2/LAYER2/NR_MAC_UE/config_ue.c` for:
  - `configure_maccellgroup()`
  - `handle_mac_uecap_info()`
  - `nr_rrc_mac_config_req_cg()`
- Added extra diagnostics:
  - `process_msg_rcc_to_mac()` return marker after `nr_rrc_mac_config_req_cg()`.
  - `configure_BWPs()` start/end state marker.
  - `release_dl_BWP()` / `release_ul_BWP()` marker and current pointer safety-null on exact-pointer release.
- Wired runtime env passthrough in `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/scripts/generate_mmtc_overlay.sh` for:
  - `MMTC_CGCFG_NOFREE`
  - `MMTC_CGCFG_DEFER_FREE_SLOTS`
- Rebuilt `nr-uesoftmodem` and rebuilt local runtime images:
  - `oai-gnb:latest`
  - `oai-nr-ue:latest`

## 3GPP Spec Clauses Referenced
- ⚠ Needs Verification: TS 38.331 Section 5.3.5 (RRC Reconfiguration / application context for CellGroupConfig)
- ⚠ Needs Verification: TS 38.321 (MAC entity behavior after RRC reconfiguration; TAG/timeAlignment and BWP-related operation context)

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| UE29-64 baseline (`NOFREE=0, DEFER=0`) | Fail | Runtime smoke | 36/36 failures; only UE29/30/31 got TUN |
| UE29-64 nofree (`NOFREE=1, DEFER=0`) | Fail | Runtime smoke | 36/36 failures; TUN group drifted to UE29/30/31/32/63 |
| UE29-64 deferred (`NOFREE=0, DEFER=128`) | Fail | Runtime smoke | 36/36 failures; TUN group drifted to UE29/30/31/33/34 |
| UE33-36 focused (`NOFREE=1, DEFER=0`) | Fail | Runtime smoke + marker verification | UE33/34/35 got TUN, UE36 SIGSEGV after first apply |
| Marker validation (`mmtc_smoke_2026-04-19_19-29-37`) | Pass | New diagnostics | For failing UE36, `configure_BWPs end` + `returned from nr_rrc_mac_config_req_cg` + `pre-free gate` all printed before SIGSEGV |

## Known Issues / Blockers
- [CellGroupConfig free timing] is not root cause: SIGSEGV still occurs with [nofree] and [deferred free].
- Crash occurs after `nr_rrc_mac_config_req_cg()` returns, indicating likely [post-apply concurrent access] issue outside the immediate free point.
- In the observed focused run, no `release_*_BWP` markers were triggered (first apply was add-only path), so BWP release UAF did not explain that specific crash.

## Next Step
- Add minimal [post-apply concurrency instrumentation] around MAC/PHY readers of `current_UL_BWP/current_DL_BWP` to pinpoint first invalid dereference after `process_msg_rcc_to_mac()` return.
