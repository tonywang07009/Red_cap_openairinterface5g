# Work Daily Log
## Session Metadata
- Date: 2026-04-14 12:03
- Agent Session ID: N/A
- Task Slug: redcap-m5-mmtc-cn-db-overlay-fix

## Milestone & Sub-task Reference
- Milestone: Milestone 5 Compose Architecture, Integration & UL Throughput Targets
- Sub-task: Fix mMTC generated UE attach failure by extending CN subscriber provisioning beyond UE28
- Status: [COMPLETED]

## What Was Done
- Diagnosed the first live [mMTC smoke validation] failure:
  - `nr-uesoftmodem` processes were alive
  - `oaitun_ue1` was missing on `UE29`
  - the issue was traced to [CN subscriber DB coverage], not container boot failure
- Confirmed the current SQL assets only provision subscribers up to `IMSI 001010000000028`.
- Added `ci-scripts/generate_mmtc_cn_db_overlay.sh`.
- Updated `ci-scripts/redcap_mmtc_smoke_validation.sh` so it now:
  - generates the [UE29..N] CN SQL overlay
  - generates a CN compose override that mounts the extra SQL into MySQL init
  - can reset CN with `MMTC_RESET_CN=1` before rerun so MySQL reinitializes with the extended subscriber set
- Verified the generated CN compose override and SQL overlay for the [64 UE] target.

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — [RedCap UE capability] remained valid; the blocker was outside UE capability signaling.
- TS 38.331 Section 5.6.1.3 — [Attach / capability path] diagnosis showed the missing TUN happened before full PDU session establishment.
- TS 38.331 Section 5.2.2.4.2 — [SIB1 RedCap] was not the current blocker for the generated UEs.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Root-cause check against subscriber SQL assets | Pass | UE29 / UE32 / UE64 | Confirmed current DB stopped at UE28 |
| `bash -n` on CN DB generator + smoke helper | Pass | Static shell syntax | No shell syntax issues |
| `MMTC_SMOKE_PREPARE_ONLY=1 bash ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Helper preflight path | CN DB overlay generation confirmed |
| `docker compose -f doc/.../docker-compose.yaml -f .../oai-cn5g_mmtc_64.override.yml config -q` | Pass | CN base + CN DB override | Compose override parses cleanly |
| `git diff --check` on updated helper assets | Pass | Patch hygiene | No whitespace / patch issues |

## Known Issues / Blockers
- A fresh host rerun is still required to prove that the [CN DB overlay] resolves the missing `oaitun_ue1` problem for generated UEs.
- The fixed-UE RedCap blocker in `[020005]` remains a separate issue.

## Next Step
- Re-run the mMTC smoke helper on host with CN reset enabled and check whether sampled generated UEs now receive `oaitun_ue1` and can ping `12.1.1.1`.
