# CN5G Runtime Migration Report

## Result

| Scope | Status | Evidence |
|---|---|---|
| Repository copy and Compose parity | PASS | `test_log/compiler_logs/cn5g_compose_parity_2026-07-15_19-45-52.log` |
| Shell/help/active-set/static validation | PASS | `test_log/compiler_logs/cn5g_static_interface_2026-07-15_19-45-52.log` |
| Clean MySQL UE1..UE56 seed | PASS | `test_log/compiler_logs/cn5g_clean_seed_2026-07-15_19-45-52.log` |
| UE1-only boundary | PASS | `test_log/compiler_logs/cn5g_rfsim_ue1_2026-07-15_19-45-52.log` |
| UE56-only boundary | PASS | `test_log/compiler_logs/cn5g_rfsim_ue56_2026-07-15_19-45-52.log` |
| 56-active-UE regression | PASS | `test_log/compiler_logs/cn5g_rfsim_56ue_2026-07-15_19-45-52.log` |
| Strict governance and stale-reference validation | PASS | `test_log/compiler_logs/cn5g_final_governance_2026-07-15_19-45-52.log` |
| Unrelated dApp repository validator | PARTIAL | CN5G checks passed, but the validator still reports pre-existing missing `dev_refer/dapp_dev_need/*` paths in `cn5g_static_dapp_validator_2026-07-15_19-45-52.log` |

The active runtime is `oai-cn5g/docker-compose.yaml`. Capacity is fixed at 56 and current entry points use `MMTC_ACTIVE_UES`. The accepted regression result is:

```text
[SUMMARY] sample=56 active=56 running=56 attach=56 pdu=56 tun=56 forward_ping_ok=56 reverse_ping_ok=0 iperf_ul_ok=0 iperf_ul_run=0 gnb_restart=0 failures=0 mode=parallel
```

The retained 64 UE result is historical threshold evidence that ended in a gNB restart. It is not a supported capacity or PASS claim.

## Boundary finding

UE56-only validation used UICC IMSI `001010000000056`, queried the matching authentication and session rows, reached Registration Accept and PDU Session Establishment Accept, created TUN, and passed forward ping. It received `10.0.0.2` because it was the first active SMF session. The ordered 56 UE run assigned UE1..UE56 as `10.0.0.2..10.0.0.57`.

The seed contains the accepted deterministic static-address metadata, but SMF enforcement of that metadata is `[Needs Verification]`. Runtime identity conclusions use UICC IMSI, MySQL rows, and AMF SUPI rather than service name or assigned IP alone.

## Cleanup Rule inventory and execution

The user explicitly approved removal of the complete `redcap_library/library_cn5g/` directory on 2026-07-15. The deletion below does not include the external rollback runtime `/home/tonywang/OAI/oai-cn5g/`.

| path | reason | references checked | expected impact | recommendation |
|---|---|---|---|---|
| `/home/tonywang/OAI/oai-cn5g/` | External runtime is duplicated by the validated repository root `oai-cn5g/` | Active scripts, current manuals, root/project routers, Compose parity, retained historical reports | No current runtime dependency after migration; deletion removes the immediate rollback copy and breaks literal paths in historical commands | RETAIN until the user explicitly approves removal after reviewing this report |
| `redcap_library/library_cn5g/` (8 tracked files, 152 KiB) | Superseded 50/64 UE seeds, Compose overrides, static backup, and library routers | Active scripts/defaults, generator callers, library indexes, M5 reports, current root config, Compose parity | No active runtime impact; removes local legacy inputs and their direct report links | REMOVED with explicit user approval; recover exact files from Git history if required |

### Preserved static-backup findings

The removed static backup had SHA-256 `4f4ba012dd2ee0e7b693420628d9a86885d8119c6f7f3c8f97d985b94ea4d5b1`. Relative to the active `oai-cn5g/conf/config.yaml`, it recorded: `register_nf.general=yes` instead of `no`; `amf.support_features_options.enable_smf_selection=yes` instead of `no`; and no UPF `port: 8805` entry. This report and Git history retain the comparison; no replacement archive was created.

## Operational state

The successful 56 UE CN5G/RFsim environment remains running after validation. No existing MySQL volume was deleted or reset outside the run-owned container recreation performed by the registered smoke workflow. No 56 UE runtime regression was rerun for this documentation-only cleanup.
