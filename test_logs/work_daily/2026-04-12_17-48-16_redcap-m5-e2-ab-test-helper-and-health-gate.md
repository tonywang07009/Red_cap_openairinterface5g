# Work Daily Log
## Session Metadata
- Date: 2026-04-12 17:48
- Agent Session ID: N/A
- Task Slug: redcap-m5-e2-ab-test-helper-and-health-gate

## Milestone & Sub-task Reference
- Milestone: Milestone 5: Integration & UL Throughput Targets
- Sub-task: Add host-side A/B test helpers for isolating FlexRIC plugin loading from RedCap runtime boot
- Status: COMPLETED

## What Was Done
- Extended `ci-scripts/redcap_prepare_runtime_config.py` so it can keep the existing Case A / Case B rewrite and also switch `e2_agent` behavior between `enabled`, `disabled`, and `empty-sm-dir`.
- Updated `ci-scripts/redcap_runtime_host_validation.sh` to accept `REDCAP_E2_AGENT_MODE`, auto-generate a temporary RedCap gNB YAML under `test_log/runtime_configs/`, and feed that YAML into the existing compose path.
- Added `ci-scripts/redcap_runtime_e2_ab_test.sh` as a host wrapper that runs the baseline and `e2_agent`-disabled cases back-to-back; it can optionally include `empty-sm-dir`.
- Updated `ci-scripts/yaml_files/5g_rfsimulator_flexric_redcap/docker-compose.yml` so `oai-gnb` waits for `nearRT-RIC` health and always gets an empty tmpfs mount at `/opt/oai-gnb/flexric-empty` for the `empty-sm-dir` A/B case.
- Verified locally that the generated `disabled` YAML removes the `e2_agent` block entirely and the generated `empty-sm-dir` YAML rewrites `sm_dir` to `/opt/oai-gnb/flexric-empty/`.
- Attempted the requested host Docker inspections (`docker run --rm oai-gnb:latest ...`), but sandbox access to `/var/run/docker.sock` is denied here.

## 3GPP Spec Clauses Referenced
- TS 38.331 Section 5.2.2.4.2 — SIB1-based RedCap access behavior remains the downstream runtime checkpoint after the gNB boots.
- TS 38.331 `RedCap-ConfigCommonSIB-r17` — The runtime helper continues to preserve RedCap initial DL/UL BWP and half-duplex related SIB1 content while isolating only the `e2_agent` block.
- TS 38.306 Section 4.2.21.1 — Runtime validation still targets a RedCap UE path with reduced capability constraints once gNB startup succeeds.

## Test Results
| Test Item | Pass / Fail | Coverage | Notes |
|-----------|-------------|----------|-------|
| `python3 -m py_compile` for modified Python helpers | Pass | N/A | `redcap_prepare_runtime_config.py` still parses cleanly |
| `bash -n` for modified shell scripts | Pass | N/A | `redcap_runtime_host_validation.sh` and `redcap_runtime_e2_ab_test.sh` syntax is valid |
| Generate `--e2-agent-mode disabled` YAML | Pass | N/A | Output no longer contains `e2_agent` or `sm_dir` |
| Generate `--mode case-b --e2-agent-mode empty-sm-dir` YAML | Pass | N/A | Output keeps Case B and rewrites `sm_dir` to `/opt/oai-gnb/flexric-empty/` |
| Host `docker run --rm oai-gnb:latest ...` inspection | Fail | N/A | Blocked by sandbox denial on the Docker socket |

## Known Issues / Blockers
- Real runtime confirmation still requires host Docker access; this environment cannot execute the actual `docker run` or `run_locally.sh` container workflow.
- The `empty-sm-dir` mode depends on the updated compose file so `/opt/oai-gnb/flexric-empty` exists as an empty directory inside the container.
- The FlexRIC plugin ABI mismatch remains a hypothesis until the host-side A/B test confirms `[enabled fails]` and `[disabled boots]`.

## Next Step
- On the host, rebuild in this order: `ran-build` → `oai-gnb:latest` → `oai-nr-ue:latest`.
- Run `bash ci-scripts/redcap_runtime_e2_ab_test.sh` with `REDCAP_USE_LOCAL_OAI_IMAGES=1`.
- If `[disabled]` boots while `[enabled]` still crashes, lock the root cause to FlexRIC plugin loading and inspect `/usr/local/lib/flexric` inside `oai-gnb:latest`.
- After the gNB boots cleanly, resume testcase `302002` / `302005` / `302006` validation.
