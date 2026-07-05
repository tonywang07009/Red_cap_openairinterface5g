# Original 5g_rfsimulator_flexric CN/RIC Audit

## Scope
- [Target]: `ci-scripts/yaml_files/5g_rfsimulator_flexric/`.
- [Question]: why gNB/UE side can appear alive, but CN5G/AMF or nearRT-RIC behavior is not correct.
- [Date]: 2026-05-28.
- [Runtime Note]: the currently running `rfsim5g-oai-gnb` container was launched from `/home/tonywang/OAI/openairinterface5g`, while this fix was applied in `/home/tonywang/OAI/Red_cap_openairinterface5g`.

## Findings
- [AMF Static Route Hypothesis]: partial match only.
  - Current AMF log shows `NG_SETUP_RESPONSE Ok`.
  - Current AMF log shows `gNB with gNB_id 0xe00 ... has been attached to AMF`.
  - Current AMF UE table stays empty, so the current failure is not AMF static route first; UE has not reached NAS registration.
- [Original Repo gNB CN Address Mismatch]:
  - `5g_rfsimulator_flexric/docker-compose.yml` assigned gNB to `192.168.70.140`.
  - Mounted YAML `gnb.sa.band78.106prb.rfsim.yaml` pointed AMF to `192.168.71.132` and gNB N2/N3 to `192.168.71.140`.
  - CN compose AMF is `192.168.70.132`.
  - This can prevent NGAP/SCTP when launching from this repo.
- [nearRT-RIC Not Running]:
  - Container process was `sleep infinity`.
  - Healthcheck returned a dummy success string instead of checking `nearRT-RIC`.
  - gNB log showed repeated `[E2 AGENT]: E2 SETUP REQUEST timeout`.
- [Compilation Completeness]:
  - `/usr/local/bin/nearRT-RIC` exists.
  - xApp binaries exist under `/usr/local/flexric/xApp/c/...`.
  - service-model libraries exist under `/usr/local/lib/flexric/`.
  - `ldd` for `nearRT-RIC` and `xapp_rc_moni` did not show missing libraries.
  - `timeout 5 nearRT-RIC ...` stayed alive until timeout, so the binary did not immediately crash.
- [RFsim Socket Issue]:
  - UE log repeatedly showed `connect() to 192.168.70.140:4043 failed`.
  - gNB container had no TCP listener on `4043`.
  - gNB log also repeatedly tried `127.0.0.1:4043`.
- [RFsim CLI Compatibility]:
  - A follow-up run showed E2 SETUP succeeded, then gNB exited on `[CONFIG] unknown option: --rfsimulator.serveraddr`.
  - This confirms `--rfsimulator.serveraddr server` is not accepted by this gNB command-line parsing path.
  - Local source shows RFsim options are marked with `PARAMFLAG_CMDLINE_NOPREFIXENABLED`, so the compose now uses `--serveraddr server`.

## Applied Fixes
- [Modification Point] `nearRT-RIC.command` -> [Reason] actual RIC process was never started -> [Before vs. After Comparison] `sleep infinity` to `/usr/local/bin/nearRT-RIC ...` -> [Discussion Point] this should allow E2 SETUP instead of permanent timeout.
- [Modification Point] `nearRT-RIC.healthcheck` -> [Reason] dummy health allowed dependent services too early -> [Before vs. After Comparison] `echo 'I am ready for compilation'` to `pgrep nearRT-RIC` -> [Discussion Point] xApps/gNB should wait for a real RIC process.
- [Modification Point] `xApp depends_on` -> [Reason] xApps should not start before RIC/gNB are healthy -> [Before vs. After Comparison] plain service dependency to `condition: service_healthy` -> [Discussion Point] avoids false-positive startup.
- [Modification Point] `oai-gnb.volume` -> [Reason] original YAML has CN IP mismatch and lacks the FlexRIC E2 config used by the working profile -> [Before vs. After Comparison] `gnb.sa.band78.106prb.rfsim.yaml:/opt/oai-gnb/etc/gnb.yaml` to `gnb.sa.band78.106prb.rfsim.flexric.conf:/opt/oai-gnb/etc/gnb.conf` -> [Discussion Point] aligns AMF `192.168.70.132`, gNB `192.168.70.140`, and `near_ric_ip_addr`.
- [Modification Point] `oai-gnb.USE_ADDITIONAL_OPTIONS` -> [Reason] runtime gNB did not listen on RFsim port `4043` and prefixed CLI option was rejected -> [Before vs. After Comparison] implicit config-driven serveraddr to explicit no-prefix `--serveraddr server` -> [Discussion Point] avoids ambiguity in RFsim server/client role without triggering unknown-option exit.

## Validation
- [Compose Syntax]: `docker compose -f ci-scripts/yaml_files/5g_rfsimulator_flexric/docker-compose.yml config --services` passed.
- [Compose Route Check]: rendered config points gNB mount to `gnb.sa.band78.106prb.rfsim.flexric.conf` and command includes `--serveraddr server`.
- [Whitespace]: `git diff --check -- ci-scripts/yaml_files/5g_rfsimulator_flexric/docker-compose.yml` passed.

## Recommended Next Runtime Test
```bash
cd ci-scripts/yaml_files/5g_rfsimulator_flexric
docker compose up -d nearRT-RIC
docker compose up -d oai-gnb oai-nr-ue1
docker logs nearRT-RIC --tail 100
docker logs rfsim5g-oai-gnb --tail 300
docker logs oai-amf --tail 300
```

Expected:
- [RIC]: `nearRT-RIC` process is present and healthcheck is healthy.
- [E2]: gNB E2 SETUP no longer repeats timeout.
- [RFsim]: gNB listens on or accepts UE RFsim connection on `4043`.
- [CN]: AMF shows gNB connected and then UE registration entries.
