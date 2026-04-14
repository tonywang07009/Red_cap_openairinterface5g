# Work Daily Log
## Session Metadata
- Date: 2026-04-14 12:42
- Agent Session ID: N/A
- Task Slug: redcap-m5-mmtc-stale-network-reset-fix

## Milestone & Sub-task Reference
- Milestone: Milestone 5 Compose Architecture, Integration & UL Throughput Targets
- Sub-task: Fix stale network attachment during mMTC smoke rerun with CN reset
- Status: [COMPLETED]

## What Was Done
- Diagnosed the rerun failure:
  - `failed to set up container networking: network ... not found`
- Root cause:
  - the smoke helper reset CN and recreated `oai-cn5g-public-net`
  - but it did not first remove the old RedCap compose containers
  - sampled generated UEs therefore tried to start with stale network references
- Updated `ci-scripts/redcap_mmtc_smoke_validation.sh` so that when `MMTC_RESET_CN=1`:
  - the RedCap base + overlay compose is brought down first
  - then the CN compose is brought down with `-v`
  - then both layers are recreated cleanly

## 3GPP Spec Clauses Referenced
- TS 38.306 Section 4.2.21.1 — [RedCap capability] was not the blocker in this failure.
- TS 38.331 Section 5.6.1.3 — the failure occurred before a stable attach / PDU session path could be established for sampled generated UEs.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Static shell syntax | Helper remains valid after reset-order change |
| `git diff --check -- ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Patch hygiene | No whitespace / format issues |

## Known Issues / Blockers
- A fresh host rerun is still required to verify that the new reset order removes the stale network error.
- The live attach result after this fix is not yet known.

## Next Step
- Re-run the mMTC smoke helper with `MMTC_RESET_CN=1` and re-check whether sampled generated UEs reach `oaitun_ue1` and ext-dn ping.
