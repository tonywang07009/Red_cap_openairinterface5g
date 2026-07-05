# RedCap vs Non-RedCap UE Live Probe Design

## 1. Goal

- Build a small control experiment that separates [RedCap UE flow] from [normal NR UE flow].
- Keep the same gNB, CN, RF simulator, PRB profile, RF frequency, numerology, and SSB start.
- Change only the UE capability path:
  - UE1: `MMTC_REDCAP_ENABLE=0`
  - UE2: `MMTC_REDCAP_ENABLE=1`
- Display live status so the operator can see whether each UE is following the expected logic.

## 2. Experiment Logic

| UE | Role | Controlled variable | Expected behavior |
|---|---|---|---|
| UE1 | Normal UE | `MMTC_REDCAP_ENABLE=0` | Runtime YAML sets `support_of_redcap_r17: 0`; UE capability log does not contain `supportOfRedCap-r17` |
| UE2 | RedCap UE | `MMTC_REDCAP_ENABLE=1` | Runtime YAML sets `support_of_redcap_r17: 1`; UE capability log contains `supportOfRedCap-r17` |

The experiment uses a temporary compose override generated under `test_log/compiler_logs/`.
This avoids permanently rewriting the base UE YAML files and keeps the repo clean.

## 3. Fixed Factors

- gNB config: current menu-selected `GNB_CONFIG`.
- UE PRB: current menu-selected `MMTC_N_RB_DL`.
- UE RF frequency: current menu-selected `MMTC_RF_FREQ`.
- UE SSB start: current menu-selected `MMTC_SSB_START`.
- CN compose: current menu-selected `MMTC_CN_COMPOSE`.
- Traffic: disabled. This probe validates flow selection, attach, PDU, and TUN creation, not throughput.

## 4. Runtime Observability

The menu prints one live row per UE at each interval.

| Column | Meaning |
|---|---|
| `container` | Docker container state from `docker inspect` |
| `tun_ip` | IPv4 address on the UE `oaitun*` interface |
| `expect` | Expected RedCap flag for the UE |
| `capability` | Whether the UE log contains `supportOfRedCap-r17` |
| `reg` | Registration state inferred from registration markers or an active UE TUN IP |
| `pdu` | PDU/session state inferred from PDU markers or an active UE TUN IP |
| `ok` | `PASS` when role/TUN/capability expectations match; `FLOW` when runtime role and TUN are present but the capability marker is missing |
| `config_marker` | First `nrue_recap RedCap config` or `support_of_redcap_r17` line found in UE logs |

## 5. Pass Criteria

- UE1 passes when:
  - Container is running.
  - `oaitun*` has an IPv4 address.
  - UE log shows `RedCap=0` or `support_of_redcap_r17: 0`.
  - UE log does not contain `supportOfRedCap-r17`.
- UE2 passes when:
  - Container is running.
  - `oaitun*` has an IPv4 address.
  - UE log shows `RedCap=1` or `support_of_redcap_r17: 1`.
  - UE log contains `supportOfRedCap-r17`.
- UE2 shows `FLOW` when:
  - Container is running.
  - `oaitun*` has an IPv4 address.
  - Runtime YAML shows `support_of_redcap_r17: 1`.
  - The currently running image does not emit a RedCap capability marker.

## 6. Failure Interpretation

- UE1 shows `supportOfRedCap-r17`: the non-RedCap branch is leaking RedCap capability fields.
- UE2 shows `RedCap=0`: the compose override or entrypoint variable propagation failed.
- TUN IP is missing for both UEs: likely gNB/CN/RF profile failure, not a RedCap-vs-normal distinction.
- TUN IP is missing for only one UE: inspect that UE's runtime YAML and NAS/RRC logs first.

## 7. Live Marker Stability

- `reg` and `pdu` are live-state indicators, not one-shot log-line indicators.
- If `tun_ip` is present, the menu reports both `reg=yes` and `pdu=yes`.
- This avoids stale `no` values after the original registration/PDU log lines have already scrolled past or are missed by a polling interval.

## 8. How To Run

From the repo root:

```bash
redcap_interface/mmtc.menu.bash
```

Then choose:

```text
15) Run RedCap vs non-RedCap live probe
```

For a short debug run without the interactive menu:

```bash
REDCAP_VS_NORMAL_WATCH_ROUNDS=3 REDCAP_VS_NORMAL_WATCH_INTERVAL=3 redcap_interface/mmtc.menu.bash redcap-vs-normal
```

## 9. Design Notes

- The probe is intentionally not an iperf test.
- The purpose is to validate [UE capability path selection] before throughput experiments.
- The probe forces `MMTC_PUCCH_COMMON_FALLBACK_BWP0=1` because this is the stable setting used by the existing RedCap smoke flow.
- UE role assignment follows the existing RedCap RFsim CI topology:
  - UE1 is the normal UE.
  - UE2 is the RedCap UE.
- The test is compatible with both menu PRB profiles:
  - 106PRB carrier profile.
  - 51PRB full-carrier profile.
- The temporary override is written to the log folder so each run keeps its own evidence.

## 10. 2026-05-23 Short Validation Result

- Command:

```bash
GNB_REDCAP_CONFIG=ci-scripts/conf_files/gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml \
REDCAP_VS_NORMAL_WATCH_ROUNDS=5 \
REDCAP_VS_NORMAL_WATCH_INTERVAL=4 \
REDCAP_VS_NORMAL_GNB_WARMUP=12 \
REDCAP_VS_NORMAL_UE_GAP=8 \
redcap_interface/mmtc.menu.bash redcap-vs-normal
```

- Log:
  - `redcap_library/library_runtime_probe/redcap_vs_nonredcap_live_probe_final.log`
- Observed before the 2026-05-23 fix:
  - UE2 normal path reached `PASS`, `support_of_redcap_r17: 0`, and `10.0.0.2`.
  - UE1 RedCap path generated `support_of_redcap_r17: 1`, then exited with `Segmentation fault` before the `supportOfRedCap-r17` capability marker appeared.
- Root cause:
  - The first probe version forced UE1 into the RedCap path.
  - `nrue_recap/nrue1.uicc.yaml` contains a `cells:` block, so UE1 took the YAML cell-parameter override path and crashed before capability generation.
  - Existing RedCap RFsim CI uses UE1 as normal and UE2 as RedCap; UE2's RedCap template does not carry the same `cells:` override.
- Fix:
  - The menu probe now uses UE1 as normal and UE2 as RedCap.
  - UE1's temporary override also mounts `ci-scripts/conf_files/nrue/nrue1.uicc.yaml`, avoiding the `nrue_recap/nrue1.uicc.yaml` `cells:` override.

## 11. 2026-05-23 Bug-Fix Validation Result

- Command:

```bash
GNB_REDCAP_CONFIG=ci-scripts/conf_files/gnb.sa.band78.fr1.51PRB.usrpb210.redcap.yaml \
MMTC_N_RB_DL=51 \
MMTC_RF_FREQ=3617640000 \
MMTC_SSB_START=238 \
REDCAP_VS_NORMAL_WATCH_ROUNDS=8 \
REDCAP_VS_NORMAL_WATCH_INTERVAL=4 \
REDCAP_VS_NORMAL_GNB_WARMUP=12 \
REDCAP_VS_NORMAL_UE_GAP=8 \
redcap_interface/mmtc.menu.bash redcap-vs-normal
```

- Log:
  - `redcap_library/library_runtime_probe/redcap_vs_nonredcap_live_probe_final.log`
- Observed:
  - UE1 normal stayed running and reached `PASS`, `no-nrue-recap`, `10.0.0.2`.
  - UE2 RedCap stayed running and reached `FLOW`, `support_of_redcap_r17: 1`, `10.0.0.3`.
  - No early `Segmentation fault` occurred after moving the normal UE back to the normal template.
- Interpretation:
  - The probe crash bug is fixed.
  - Current live image did not emit `supportOfRedCap-r17` / gNB `UE ... is RedCap` markers during this short run, so the RedCap side is marked `FLOW` rather than `PASS`.
  - A full capability-marker validation should be rerun after confirming the local RedCap image contains the latest UE capability injection code.
