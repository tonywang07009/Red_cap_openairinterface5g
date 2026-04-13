# Work Daily Log
## Session Metadata
- Date: 2026-04-12 17:31
- Agent Session ID: N/A
- Task Slug: redcap-m5-flexric-plugin-crash-rca

## Milestone & Sub-task Reference
- Milestone: Milestone 5: Integration & UL Throughput Targets
- Sub-task: Root-cause analysis for local RedCap runtime gNB exit during FlexRIC-integrated RF-sim deployment
- Status: COMPLETED

## What Was Done
- Read the latest runtime failure log `cmake_targets/log/container_5g_flexric_rfsim_redcap.xml.d/25-100009-oai-gnb.logs`.
- Verified that the gNB successfully loaded the mounted RedCap YAML at `/opt/oai-gnb/etc/gnb.yaml`, parsed RedCap fields, completed NGAP setup, and reached RU initialization.
- Identified the first fatal failure as an AddressSanitizer `SEGV` during `load_all_pugin_ag()` / `init_plugin_ag()` in the E2/FlexRIC agent path, not during YAML parsing or RF sample processing.
- Cross-checked `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml` and confirmed the RedCap compose mounts the gNB YAML but does not mount host FlexRIC service-model libraries into the gNB container.
- Cross-checked `docker/Dockerfile.build.ubuntu` and `docker/Dockerfile.gNB.ubuntu` and confirmed the gNB image copies `/usr/local/lib/flexric` from the `ran-build` stage, meaning stale or mismatched `ran-build` artifacts can desynchronize `nr-softmodem` from FlexRIC plugin `.so` files.
- Verified `openair2/E2AP/README.md` notes that OAI RAN and FlexRIC must be compiled with the same E2AP and E2SM-KPM versions.
- Verified the current RedCap YAML contains `e2_agent.sm_dir: /usr/local/lib/flexric/`, `halfDuplexRedCapAllowed_r17`, RedCap initial DL/UL BWP fields, and RedCap cell barring fields.
- Verified the current RedCap compose file does not gate `oai-gnb` startup on `nearRT-RIC` health; it only declares `depends_on: - nearRT-RIC`.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.2.2.4.2 — UE actions upon reception of SIB1, including RedCap cell barring behavior and half-duplex gating.
- TS 38.331 `RedCap-ConfigCommonSIB-r17` IE — RedCap SIB1 structure carrying `halfDuplexRedCapAllowed-r17`, `cellBarredRedCap1Rx/2Rx`, and RedCap initial BWP fields.
- TS 38.321 Section 5.7 — Connected-mode DRX timer semantics (`drx-onDurationTimer`, `drx-InactivityTimer`, `drx-LongCycleStartOffset`, `drx-ShortCycle`).
- TS 38.306 Section 4.2.21.1 — Definition of RedCap UE reduced capability, including 20 MHz FR1 limit and RedCap-specific initial BWPs.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| Latest gNB runtime log triage | Pass | N/A | Fatal point is ASAN `SEGV` during FlexRIC plugin loading, after config parse and NGAP setup |
| RedCap YAML mount / parse validation | Pass | N/A | gNB log shows YAML loaded and RedCap fields parsed successfully |
| Compose image/env validation | Pass | N/A | Run log confirms `REGISTRY=\"\"`, `TAG=\"latest\"`, `GNB_IMG=\"oai-gnb\"`, `NRUE_IMG=\"oai-nr-ue\"` |
| FlexRIC version-alignment rule check | Pass | N/A | Repo README explicitly requires same E2AP / E2SM-KPM versions |
| Docker in-situ container inspection | Fail | N/A | Not executable in sandbox; requires host Docker access |

## Known Issues / Blockers
- The immediate blocker is not SIB1 / RedCap YAML wiring; it is the FlexRIC plugin loader crashing inside the gNB container.
- The most likely causes are stale or ABI-mismatched `/usr/local/lib/flexric/*.so` artifacts relative to the `nr-softmodem` binary copied into `oai-gnb:latest`.
- `nearRT-RIC` health is not currently enforced as a startup condition for `oai-gnb`; this is a robustness gap but not the first observed fatal error in this trace.
- eDRX / PSM compliance checks are still secondary until the gNB boots through E2 initialization.

## Next Step
- Rebuild `ran-build` first, then rebuild `oai-gnb:latest`, ensuring both `nr-softmodem` and `/usr/local/lib/flexric` come from the same fresh build chain.
- On the host, inspect `/usr/local/lib/flexric` inside `oai-gnb:latest` and compare plugin inventory / timestamps against the rebuilt `ran-build` artifacts.
- Run an A/B validation by temporarily disabling the `e2_agent` block or pointing `sm_dir` to an empty directory; if gNB then boots, the blocker is confirmed to be FlexRIC plugin loading rather than RedCap RAN configuration.
- After the gNB boots cleanly, re-run testcase `302002` and resume RedCap attach / UL PRB control validation.
