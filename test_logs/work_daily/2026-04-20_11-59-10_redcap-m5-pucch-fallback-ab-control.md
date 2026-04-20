# Work Daily Log
## Session Metadata
- Date: 2026-04-20 11:59
- Agent Session ID: N/A
- Task Slug: redcap-m5-pucch-fallback-ab-control

## Milestone & Sub-task Reference
- Milestone: RedCap mMTC [M5] CellGroupConfig / UE attach stability
- Sub-task: [PUCCH fallback gate] controlled A/B runtime verification
- Status: [COMPLETED]

## What Was Done
- Executed [A] run with `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1`, sample `UE33..40`.
- Executed [B] control run with `MMTC_PUCCH_COMMON_FALLBACK_BWP0=0`, sample `UE36..40`.
- Compared UE docker logs for:
  - `[CGDBG][PUCCH-FALLBACK] use BWP0 common resource`
  - `[CGDBG][PUCCH] pucch_ResourceCommon is NULL for initial PUCCH`
  - `[CGDBG][PUCCH] configure failed`.

## 3GPP Spec Clauses Referenced
- TS 38.213 Section 9.2.1 — initial PUCCH depends on common resource configuration.
- TS 38.331 Section 5.3.5 — ServingCell/BWP reconfiguration can alter active BWP context.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| A-run (`11-51-37`, fallback=1, UE33..40) | Fail | UE33..40 | TUN `8/8`, ping `0/8`; UE36..40 each had 1 fallback hit |
| A-run UE36..40 null/config-failed counters | Pass | UE36..40 | NULL `0`, configure-failed `0` |
| B-run (`11-56-41`, fallback=0, UE36..40) | Fail | UE36..40 | TUN `3/5` (UE39/40 no TUN), ping `0/3` |
| B-run UE39/40 null/config-failed counters | Pass | UE39/40 | NULL `57/37`, configure-failed `57/37`, marker `fallback=0` |

## Known Issues / Blockers
- [PUCCH common NULL] problem has clear mitigation via fallback gate, but [ping 0/x] remains unresolved.
- Data-plane issue likely in [gNB-UPF/ext-dn] path, independent from this PUCCH attach fix.

## Next Step
- Keep `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1` as temporary mitigation baseline.
- Move RCA to UPF/N3/N4 and ext-dn routing for multi-UE ping recovery.
