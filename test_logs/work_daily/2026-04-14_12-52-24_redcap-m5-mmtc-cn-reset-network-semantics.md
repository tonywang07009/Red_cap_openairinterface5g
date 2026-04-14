# Work Daily Log
## Session Metadata
- Date: 2026-04-14 12:52
- Agent Session ID: N/A
- Task Slug: redcap-m5-mmtc-cn-reset-network-semantics

## Milestone & Sub-task Reference
- Milestone: Milestone 5 Compose Architecture, Integration & UL Throughput Targets
- Sub-task: Correct CN reset semantics for the shared `oai-cn5g-public-net` network
- Status: [COMPLETED]

## What Was Done
- Refined `ci-scripts/redcap_mmtc_smoke_validation.sh`.
- Previous logic used:
  - `docker compose ... down -v`
  during CN reset.
- This was incorrect for the current architecture because:
  - `oai-cn5g-public-net` is shared by both the CN compose and the RedCap compose
  - `down` attempts to remove the shared network
  - removal fails whenever active endpoints still exist
- Updated the reset flow so the CN side now uses:
  - `docker compose ... rm -sfv`
  instead of `down -v`
- The helper still tears down the RedCap compose first, but now avoids trying to delete the shared network from the CN stack.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.6.1.3 — the failure was infra/runtime orchestration related and occurred before stable attach evidence could be collected.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Static shell syntax | Script remains valid after reset semantic change |
| `git diff --check -- ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Patch hygiene | No whitespace / formatting issues |

## Known Issues / Blockers
- A fresh host rerun is still required after this reset semantic fix.
- Live attach / TUN creation for generated UEs after this patch is not yet verified.

## Next Step
- Clean the current half-reset environment once, then rerun the mMTC smoke helper with `MMTC_RESET_CN=1`.
