# Work Daily Log
## Session Metadata
- Date: 2026-04-14 13:08
- Agent Session ID: N/A
- Task Slug: redcap-m5-fix-mmtc-cn-overlay-schema

## Milestone & Sub-task Reference
- Milestone: Compose Rebase & mMTC Scaling
- Sub-task: Align generated CN subscriber overlay with `oai-cn5g` base schema for UE29..UE64
- Status: COMPLETED

## What Was Done
- [Modification Point] `[ci-scripts/generate_mmtc_cn_db_overlay.sh]` → [Reason] current overlay targeted the legacy `users` table from `ci-scripts/yaml_files/5g_rfsimulator/oai_db.sql`, but `doc/tutorial_resources/oai-cn5g/database/oai_db.sql` does not define that table → [Before vs. After Comparison] removed the invalid `INSERT INTO users` block and kept only `AuthenticationSubscription` plus `SessionManagementSubscriptionData` → [Discussion Point] this removes the most likely MySQL init failure that caused `mysql` to exit and `AUSF` to return `CONTEXT_NOT_FOUND`.
- [Modification Point] `[ci-scripts/generate_mmtc_cn_db_overlay.sh]` → [Reason] generated UE PDU-session IPs were incorrectly placed in the `12.1.1.x` ext-dn subnet → [Before vs. After Comparison] changed generated `staticIpAddress` values to `10.0.0.(UE index + 1)` and restored vendor-like `ims` DNN plus `5qi=6` for `oai` → [Discussion Point] this matches the stock `oai-cn5g` topology and avoids future data-plane addressing conflicts.
- [Modification Point] `[ci-scripts/redcap_mmtc_smoke_validation.sh]` → [Reason] previous diagnostics did not make MySQL/AUSF failures explicit → [Before vs. After Comparison] now captures `[mysql / ausf / udm]` logs, records live `mysql` container state, and removes the invalid `users` query from subscriber checks → [Discussion Point] if the next run still fails, the root cause should be visible directly in the generated diagnostics.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.6.1.3 — runtime registration and session establishment must complete before UE user-plane validation is meaningful.
- TS 38.306 Section 4.2.21.1 — RedCap UE capability is already being signaled correctly; this sub-task focused on CN provisioning needed to let that UE finish registration.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `bash -n ci-scripts/generate_mmtc_cn_db_overlay.sh ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Script syntax | No shell syntax errors after generator/helper changes |
| `MMTC_SMOKE_PREPARE_ONLY=1 MMTC_TOTAL_UES=64 bash ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Overlay generation path | Re-generated compose and CN DB overlays successfully |
| `docker compose -f doc/tutorial_resources/oai-cn5g/docker-compose.yaml -f test_log/runtime_configs/oai-cn5g_mmtc_64.override.yml config -q` | Pass | Compose config validation | Generated CN overlay is structurally valid |
| `git diff --check -- ci-scripts/generate_mmtc_cn_db_overlay.sh ci-scripts/redcap_mmtc_smoke_validation.sh` | Pass | Formatting / whitespace | No diff-check issues |

## Known Issues / Blockers
- [⚠ Needs Verification] the updated CN DB overlay still needs a fresh host rerun to confirm `mysql` stays up and `AUSF` can resolve UE29/32/64.
- [⚠ Needs Verification] if registration still fails after MySQL init is fixed, the next likely investigation point is whether additional `oai-cn5g` subscription data beyond `AuthenticationSubscription` and `SessionManagementSubscriptionData` is required for large generated UE sets.

## Next Step
- Re-run `MMTC_TOTAL_UES=64 MMTC_SAMPLE_UES="29 32 64" MMTC_RESET_CN=1 bash ci-scripts/redcap_mmtc_smoke_validation.sh` and check whether `[mysql container status]` remains `running` and whether UE29/32/64 receive `[Registration Accept]` plus `oaitun_ue1`.
