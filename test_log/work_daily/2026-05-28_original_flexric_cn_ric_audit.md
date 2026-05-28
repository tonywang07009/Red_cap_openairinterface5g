# 2026-05-28 Original FlexRIC CN/RIC Audit

## Work Completed
- [Audit Target]: `ci-scripts/yaml_files/5g_rfsimulator_flexric/`.
- [Runtime Evidence]: current AMF sees gNB connected but no UE registration.
- [RIC Evidence]: current `nearRT-RIC` process is `sleep infinity`; no actual RIC process is running.
- [Compile Evidence]: `nearRT-RIC`, xApps, and FlexRIC service-model `.so` files exist; `ldd` showed no missing libraries.
- [Fix]: updated original FlexRIC compose to start real nearRT-RIC, use real healthchecks, wait for healthy RIC/gNB, mount the FlexRIC gNB config, and force gNB RFsim server role with `--serveraddr server`.
- [Follow-Up]: `--rfsimulator.serveraddr server` was rejected by the running gNB parser as an unknown option, so the compose now uses no-prefix `--serveraddr server`.

## Validation
- [Compose Config]: `docker compose -f ci-scripts/yaml_files/5g_rfsimulator_flexric/docker-compose.yml config --services` passed.
- [Diff Check]: `git diff --check -- ci-scripts/yaml_files/5g_rfsimulator_flexric/docker-compose.yml` passed.

## Report
- `agent_doc/Project_management/projects/redcap_simulator_performance_eval_v1/analysis/original_5g_rfsimulator_flexric_cn_ric_audit_2026-05-28.md`
