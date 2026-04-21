# Work Daily Log
## Session Metadata
- Date: 2026-04-21 11:14
- Agent Session ID: N/A
- Task Slug: redcap-m5-pucch-oversubscribe-fix

## Milestone & Sub-task Reference
- Milestone: M5 RCA (mMTC staged load)
- Sub-task: Remove gNB hard reject at PUCCH UE budget gate and validate stage52/stage56
- Status: [COMPLETED]

## What Was Done
- Modified `openair2/LAYER2/NR_MAC_gNB/nr_radio_config.c` in `verify_radio_configuration()`.
- Replaced hard reject condition `uid >= max_supported_ues` with oversubscription fallback mapping `pucch_uid = uid % max_supported_ues`.
- Updated PUCCH resource index use sites (`pucchres0_startingPRB`, `idx`) to use `pucch_uid` instead of raw `uid`.
- Added warning marker: `reusing reservation index` for observability.
- Rebuilt local images with `ci-scripts/redcap_rebuild_local_oai_images.sh` and reran stage scan.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.3.3.1 — RRC connection establishment flow; avoid unnecessary RRCReject caused by implementation resource gate.
- TS 38.321 Section 5.1.4 — Random Access response and contention resolution context used for attach-phase diagnostics.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Stage scan UE=52 | Pass | Runtime stage smoke | `[SUMMARY] sample=52 running=52 attach=52 pdu=52 tun=52 forward_ping_ok=52 failures=0` |
| Stage scan UE=56 | Pass | Runtime stage smoke | `[SUMMARY] sample=56 running=56 attach=56 pdu=56 tun=56 forward_ping_ok=56 failures=0` |
| gNB restart monitor | Pass | Runtime stability | `gnb_restart=0` in both stages |

## Known Issues / Blockers
- No blocker for UE52/56 after this patch.
- Stage60/64 still pending to confirm behavior under higher load.

## Next Step
- Run `MMTC_STAGE_LIST=60,64` stage scan with the same image baseline and compare summaries + key gNB markers.
